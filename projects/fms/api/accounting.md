# API Spec — Accounting (Invoice, Payment, P/L Sheet, Advance Request, AR Report)

> Cross-reference: xem `schema/accounting.md` cho định nghĩa đầy đủ của các entity.

Base URL: `/api/v1`

> Lỗi response: xem định nghĩa chuẩn trong `api/catalogue.md`.

---

## Phase 1 vs Phase 2

| Endpoint group | Phase 1 | Phase 2 |
|---|---|---|
| GET /invoices (all & one) | ✓ read-only (synced từ CDC) | ✓ |
| POST /invoices, PUT /invoices/{id}/* | ✗ | ✓ writable |
| GET /payments | ✓ read-only (synced từ CDC) | ✓ |
| POST /payments | ✗ | ✓ writable |
| GET /pl-sheets | ✓ read-only (synced từ CDC) | ✓ |
| GET /advance-requests | ✓ read-only | ✓ |
| POST /advance-requests, PUT approve/reject | ✗ | ✓ writable |
| GET /reports/ar | ✓ read-only | ✓ |

---

## Invoice

### GET /api/v1/invoices

Lấy danh sách hóa đơn.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| partner_id | string | Lọc theo đối tác (khách hàng hoặc nhà cung cấp) |
| status | string | Trạng thái: `DRAFT`, `ISSUED`, `PARTIAL_PAID`, `PAID`, `CANCELLED` |
| from_date | string | Ngày hóa đơn từ (ISO 8601: `YYYY-MM-DD`) |
| to_date | string | Ngày hóa đơn đến (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "inv-001",
      "invoice_no": "INV2026-0001",
      "type": "RECEIVABLE",
      "status": "ISSUED",
      "partner_id": "p-001",
      "partner_name": "Công ty TNHH ABC",
      "invoice_date": "2026-03-20",
      "due_date": "2026-04-19",
      "currency": "VND",
      "total_amount": 18500000,
      "paid_amount": 0,
      "transaction_id": "tx-001",
      "created_at": "2026-03-20T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 88
  }
}
```

---

### GET /api/v1/invoices/{id}

Lấy chi tiết một hóa đơn.

**Response 200:**

```json
{
  "id": "inv-001",
  "invoice_no": "INV2026-0001",
  "type": "RECEIVABLE",
  "status": "ISSUED",
  "partner_id": "p-001",
  "partner_name": "Công ty TNHH ABC",
  "invoice_date": "2026-03-20",
  "due_date": "2026-04-19",
  "currency": "VND",
  "exchange_rate": 1.0,
  "transaction_id": "tx-001",
  "house_bill_id": "hb-001",
  "line_items": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển",
      "unit": "20DC",
      "unit_price": 8000000,
      "quantity": 2,
      "amount": 16000000
    },
    {
      "charge_code": "HANDLING",
      "description": "Phí handling",
      "unit": "BL",
      "unit_price": 2500000,
      "quantity": 1,
      "amount": 2500000
    }
  ],
  "subtotal": 18500000,
  "tax_amount": 0,
  "total_amount": 18500000,
  "paid_amount": 0,
  "outstanding_amount": 18500000,
  "note": null,
  "issued_by": "u-003",
  "issued_at": "2026-03-20T09:30:00Z",
  "created_at": "2026-03-20T09:00:00Z",
  "updated_at": "2026-03-20T09:30:00Z"
}
```

---

### POST /api/v1/invoices

Tạo mới hóa đơn.

**Request body:**

```json
{
  "type": "RECEIVABLE",
  "partner_id": "p-001",
  "invoice_date": "2026-04-01",
  "due_date": "2026-04-30",
  "currency": "VND",
  "exchange_rate": 1.0,
  "transaction_id": "tx-001",
  "house_bill_id": "hb-001",
  "line_items": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển",
      "unit": "20DC",
      "unit_price": 8000000,
      "quantity": 2
    }
  ],
  "note": null
}
```

**Response 201:**

```json
{
  "id": "inv-002",
  "invoice_no": "INV2026-0002",
  "status": "DRAFT",
  "total_amount": 16000000,
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/invoices/{id}/issue

Phát hành hóa đơn. Chuyển trạng thái `DRAFT` → `ISSUED`.

**Request body:** (không bắt buộc)

```json
{
  "note": "Phát hành sau khi xác nhận với kế toán"
}
```

**Response 200:**

```json
{
  "id": "inv-002",
  "invoice_no": "INV2026-0002",
  "status": "ISSUED",
  "issued_at": "2026-03-29T10:00:00Z"
}
```

**Response 400** — khi không ở trạng thái `DRAFT`:

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "message": "Invoice must be in DRAFT status to issue",
  "status": 400
}
```

---

### PUT /api/v1/invoices/{id}/cancel

Hủy hóa đơn.

**Request body:**

```json
{
  "reason": "Sai thông tin khách hàng, tạo lại hóa đơn mới"
}
```

**Response 200:**

```json
{
  "id": "inv-002",
  "invoice_no": "INV2026-0002",
  "status": "CANCELLED",
  "cancelled_at": "2026-03-29T11:00:00Z"
}
```

---

## Payment

### GET /api/v1/payments

Lấy danh sách thanh toán.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| invoice_id | string | Lọc theo hóa đơn |
| partner_id | string | Lọc theo đối tác |
| from_date | string | Ngày thanh toán từ (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "pay-001",
      "invoice_id": "inv-001",
      "invoice_no": "INV2026-0001",
      "partner_id": "p-001",
      "partner_name": "Công ty TNHH ABC",
      "payment_date": "2026-04-15",
      "amount": 18500000,
      "currency": "VND",
      "payment_method": "BANK_TRANSFER",
      "reference_no": "TT-20260415-001",
      "created_at": "2026-04-15T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 72
  }
}
```

---

### POST /api/v1/payments

Ghi nhận một khoản thanh toán.

**Request body:**

```json
{
  "invoice_id": "inv-001",
  "payment_date": "2026-04-15",
  "amount": 18500000,
  "currency": "VND",
  "payment_method": "BANK_TRANSFER",
  "reference_no": "TT-20260415-001",
  "note": "Khách chuyển khoản đầy đủ"
}
```

**Response 201:**

```json
{
  "id": "pay-002",
  "invoice_id": "inv-001",
  "amount": 18500000,
  "invoice_status": "PAID",
  "created_at": "2026-04-15T14:00:00Z"
}
```

> Ghi chú: Sau khi tạo payment, hệ thống tự tính toán lại `paid_amount` và cập nhật `status` của invoice (`PARTIAL_PAID` hoặc `PAID`).

---

### GET /api/v1/invoices/{id}/payments

Lấy tất cả các khoản thanh toán thuộc một hóa đơn.

**Response 200:**

```json
{
  "invoice_id": "inv-001",
  "invoice_no": "INV2026-0001",
  "total_amount": 18500000,
  "paid_amount": 18500000,
  "outstanding_amount": 0,
  "payments": [
    {
      "id": "pay-001",
      "payment_date": "2026-04-15",
      "amount": 18500000,
      "payment_method": "BANK_TRANSFER",
      "reference_no": "TT-20260415-001"
    }
  ]
}
```

---

## P/L Sheet

### GET /api/v1/pl-sheets

Lấy danh sách P/L sheet.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| transaction_id | string | Lọc theo transaction |
| from_date | string | Ngày tạo từ (ISO 8601: `YYYY-MM-DD`) |
| to_date | string | Ngày tạo đến (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "transaction_id": "tx-001",
      "ref_no": "TX2026-0001",
      "total_revenue": 22000000,
      "total_cost": 14500000,
      "profit": 7500000,
      "profit_margin_pct": 34.09,
      "currency": "VND",
      "updated_at": "2026-04-20T16:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 95
  }
}
```

---

### GET /api/v1/pl-sheets/{transaction_id}

Lấy P/L chi tiết của một transaction.

**Response 200:**

```json
{
  "transaction_id": "tx-001",
  "ref_no": "TX2026-0001",
  "mbl_no": "EVGL123456789",
  "currency": "VND",
  "revenue_lines": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển (thu)",
      "amount": 16000000
    },
    {
      "charge_code": "HANDLING",
      "description": "Phí handling (thu)",
      "amount": 2500000
    },
    {
      "charge_code": "DOC_FEE",
      "description": "Phí chứng từ (thu)",
      "amount": 3500000
    }
  ],
  "cost_lines": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển (trả hãng tàu)",
      "amount": 12000000
    },
    {
      "charge_code": "PORT_HANDLING",
      "description": "Phí cảng (trả)",
      "amount": 2500000
    }
  ],
  "total_revenue": 22000000,
  "total_cost": 14500000,
  "profit": 7500000,
  "profit_margin_pct": 34.09,
  "updated_at": "2026-04-20T16:00:00Z"
}
```

---

## Cost & Revenue Entries

> **Note:** `of1_fms_cost_revenue` entries được tạo **tự động** khi:
> - Invoice ISSUED → tạo Revenue entry
> - Payment recorded → tạo actual received entry
> - Advance Request APPROVED → tạo Cost entry
>
> Không có endpoint riêng để tạo cost/revenue entries. Xem `schema/accounting.md` cho cấu trúc bảng.
>
> Để đọc P/L detail: `GET /api/v1/pl-sheets/{transaction_id}` trả về tổng hợp từ bảng này.

---

## Advance Request

### GET /api/v1/advance-requests

Lấy danh sách đề nghị tạm ứng.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| status | string | Trạng thái: `PENDING`, `APPROVED`, `REJECTED`, `SETTLED` |
| requested_by | string | Lọc theo user |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "adv-001",
      "ref_no": "ADV2026-0001",
      "status": "APPROVED",
      "transaction_id": "tx-001",
      "requested_by": "u-002",
      "requested_by_name": "Trần Thị B",
      "amount": 5000000,
      "currency": "VND",
      "purpose": "Thanh toán phí cảng trước",
      "requested_at": "2026-03-22T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 18
  }
}
```

---

### POST /api/v1/advance-requests

Tạo mới đề nghị tạm ứng.

**Request body:**

```json
{
  "transaction_id": "tx-001",
  "amount": 5000000,
  "currency": "VND",
  "purpose": "Thanh toán phí cảng trước chuyến hàng tháng 4",
  "required_by_date": "2026-04-05",
  "note": null
}
```

**Response 201:**

```json
{
  "id": "adv-002",
  "ref_no": "ADV2026-0002",
  "status": "PENDING",
  "amount": 5000000,
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/advance-requests/{id}/approve

Phê duyệt đề nghị tạm ứng. Chuyển trạng thái `PENDING` → `APPROVED`.

**Request body:**

```json
{
  "approved_amount": 5000000,
  "note": "Đồng ý tạm ứng, chuyển khoản trước ngày 5/4"
}
```

**Response 200:**

```json
{
  "id": "adv-002",
  "ref_no": "ADV2026-0002",
  "status": "APPROVED",
  "approved_amount": 5000000,
  "approved_by": "u-004",
  "approved_at": "2026-03-29T11:00:00Z"
}
```

---

### PUT /api/v1/advance-requests/{id}/reject

Từ chối đề nghị tạm ứng. Chuyển trạng thái `PENDING` → `REJECTED`.

**Request body:**

```json
{
  "reason": "Số tiền vượt hạn mức tạm ứng theo quy định"
}
```

**Response 200:**

```json
{
  "id": "adv-002",
  "ref_no": "ADV2026-0002",
  "status": "REJECTED",
  "rejected_by": "u-004",
  "rejected_at": "2026-03-29T11:30:00Z"
}
```

---

## Account Receivable (Report)

### GET /api/v1/reports/ar

Báo cáo công nợ phải thu.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| partner_id | string | Lọc theo đối tác |
| overdue_only | boolean | Chỉ hiển thị hóa đơn quá hạn (`true`/`false`, mặc định: `false`) |
| from_date | string | Ngày hóa đơn từ (ISO 8601: `YYYY-MM-DD`) |
| to_date | string | Ngày hóa đơn đến (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "summary": {
    "total_outstanding": 145000000,
    "total_overdue": 32000000,
    "partner_count": 12
  },
  "data": [
    {
      "partner_id": "p-001",
      "partner_name": "Công ty TNHH ABC",
      "invoice_id": "inv-001",
      "invoice_no": "INV2026-0001",
      "invoice_date": "2026-03-20",
      "due_date": "2026-04-19",
      "total_amount": 18500000,
      "paid_amount": 0,
      "outstanding_amount": 18500000,
      "days_overdue": 0,
      "is_overdue": false
    },
    {
      "partner_id": "p-005",
      "partner_name": "Công ty CP DEF",
      "invoice_id": "inv-008",
      "invoice_no": "INV2026-0008",
      "invoice_date": "2026-02-10",
      "due_date": "2026-03-11",
      "total_amount": 32000000,
      "paid_amount": 0,
      "outstanding_amount": 32000000,
      "days_overdue": 18,
      "is_overdue": true
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 24
  }
}
```
