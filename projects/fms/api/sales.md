# API Spec — Sales (Quotation, Booking, Inquiry, Vessel Schedule)

> Cross-reference: xem `schema/sales.md` cho định nghĩa đầy đủ của các entity.

Base URL: `/api/v1`

> Lỗi response: xem định nghĩa chuẩn trong `api/catalogue.md`.

---

## Phase 1 vs Phase 2

| Endpoint group | Phase 1 | Phase 2 |
|---|---|---|
| GET /quotations (all & one) | ✓ read-only | ✓ |
| POST/PUT /quotations | ✗ | ✓ writable |
| GET /bookings (all & one) | ✓ read-only | ✓ |
| POST/PUT /bookings | ✗ | ✓ writable |
| GET /inquiries | ✓ read-only | ✓ |
| POST /inquiries, PUT /inquiries/{id}/convert | ✗ | ✓ writable |
| GET /vessel-schedules | ✓ read-only | ✓ |

---

## Quotation

### GET /api/v1/quotations

Lấy danh sách báo giá.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type | string | Loại dịch vụ: `FCL`, `LCL`, `AIR`, `TRUCKING` |
| status | string | Trạng thái: `DRAFT`, `SENT`, `ACCEPTED`, `REJECTED`, `EXPIRED` |
| customer_id | string | Lọc theo khách hàng |
| from_date | string | Ngày tạo từ (ISO 8601: `YYYY-MM-DD`) |
| to_date | string | Ngày tạo đến (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "q-001",
      "ref_no": "QT2026-0001",
      "type": "FCL",
      "status": "SENT",
      "customer_id": "p-001",
      "customer_name": "Công ty TNHH ABC",
      "pol_code": "VNSGN",
      "pod_code": "CNSHA",
      "valid_from": "2026-03-01",
      "valid_to": "2026-03-31",
      "created_at": "2026-03-01T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 45
  }
}
```

---

### GET /api/v1/quotations/{id}

Lấy chi tiết một báo giá.

**Response 200:**

```json
{
  "id": "q-001",
  "ref_no": "QT2026-0001",
  "type": "FCL",
  "status": "SENT",
  "customer_id": "p-001",
  "customer_name": "Công ty TNHH ABC",
  "pol_code": "VNSGN",
  "pol_name": "Cảng Sài Gòn",
  "pod_code": "CNSHA",
  "pod_name": "Shanghai Port",
  "carrier_id": "p-010",
  "valid_from": "2026-03-01",
  "valid_to": "2026-03-31",
  "currency": "USD",
  "charge_lines": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển",
      "unit": "20DC",
      "unit_price": 350.00,
      "quantity": 2,
      "amount": 700.00
    }
  ],
  "total_amount": 700.00,
  "note": "Báo giá tháng 3/2026",
  "created_by": "u-001",
  "created_at": "2026-03-01T08:00:00Z",
  "updated_at": "2026-03-02T09:00:00Z"
}
```

---

### POST /api/v1/quotations

Tạo mới báo giá.

**Request body:**

```json
{
  "type": "FCL",
  "customer_id": "p-001",
  "pol_code": "VNSGN",
  "pod_code": "CNSHA",
  "carrier_id": "p-010",
  "valid_from": "2026-04-01",
  "valid_to": "2026-04-30",
  "currency": "USD",
  "charge_lines": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "description": "Cước biển",
      "unit": "20DC",
      "unit_price": 350.00,
      "quantity": 2
    }
  ],
  "note": "Báo giá tháng 4/2026"
}
```

**Response 201:**

```json
{
  "id": "q-002",
  "ref_no": "QT2026-0002",
  "type": "FCL",
  "status": "DRAFT",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/quotations/{id}

Cập nhật báo giá (chỉ áp dụng khi `status = DRAFT`).

**Request body:** (chỉ gửi các field cần thay đổi)

```json
{
  "valid_to": "2026-05-31",
  "charge_lines": [
    {
      "charge_code": "OCEAN_FREIGHT",
      "unit_price": 400.00,
      "quantity": 2
    }
  ]
}
```

**Response 200:** Trả về quotation sau khi cập nhật (cùng cấu trúc với GET one).

---

### PUT /api/v1/quotations/{id}/send

Gửi báo giá cho khách hàng. Chuyển trạng thái `DRAFT` → `SENT`.

**Request body:** (không bắt buộc)

```json
{
  "note": "Kính gửi quý khách, đây là báo giá tháng 4."
}
```

**Response 200:**

```json
{
  "id": "q-002",
  "ref_no": "QT2026-0002",
  "status": "SENT",
  "sent_at": "2026-03-29T10:00:00Z"
}
```

**Response 400** — khi `status` không phải `DRAFT`:

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "message": "Quotation must be in DRAFT status to send",
  "status": 400
}
```

---

## Booking

### GET /api/v1/bookings

Lấy danh sách booking.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type | string | Loại dịch vụ: `FCL`, `LCL`, `AIR`, `TRUCKING` |
| status | string | Trạng thái: `PENDING`, `CONFIRMED`, `CANCELLED`, `CLOSED` |
| customer_id | string | Lọc theo khách hàng |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "bk-001",
      "ref_no": "BK2026-0001",
      "type": "FCL",
      "status": "CONFIRMED",
      "customer_id": "p-001",
      "customer_name": "Công ty TNHH ABC",
      "quotation_id": "q-001",
      "pol_code": "VNSGN",
      "pod_code": "CNSHA",
      "etd": "2026-04-10",
      "created_at": "2026-03-05T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 30
  }
}
```

---

### GET /api/v1/bookings/{id}

Lấy chi tiết một booking.

**Response 200:**

```json
{
  "id": "bk-001",
  "ref_no": "BK2026-0001",
  "type": "FCL",
  "status": "CONFIRMED",
  "customer_id": "p-001",
  "customer_name": "Công ty TNHH ABC",
  "quotation_id": "q-001",
  "pol_code": "VNSGN",
  "pol_name": "Cảng Sài Gòn",
  "pod_code": "CNSHA",
  "pod_name": "Shanghai Port",
  "carrier_id": "p-010",
  "vessel_schedule_id": "vs-005",
  "etd": "2026-04-10",
  "eta": "2026-04-20",
  "containers": [
    { "container_type": "20DC", "quantity": 2 }
  ],
  "note": null,
  "created_by": "u-001",
  "confirmed_at": "2026-03-06T10:00:00Z",
  "created_at": "2026-03-05T08:00:00Z",
  "updated_at": "2026-03-06T10:00:00Z"
}
```

---

### POST /api/v1/bookings

Tạo booking từ một báo giá đã được chấp thuận.

**Request body:**

```json
{
  "quotation_id": "q-001",
  "vessel_schedule_id": "vs-005",
  "etd": "2026-04-10",
  "containers": [
    { "container_type": "20DC", "quantity": 2 }
  ],
  "note": "Hàng xuất tháng 4"
}
```

**Response 201:**

```json
{
  "id": "bk-002",
  "ref_no": "BK2026-0002",
  "status": "PENDING",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/bookings/{id}/confirm

Xác nhận booking. Chuyển trạng thái `PENDING` → `CONFIRMED`.

**Request body:** (không bắt buộc)

```json
{
  "note": "Đã xác nhận với hãng tàu"
}
```

**Response 200:**

```json
{
  "id": "bk-002",
  "ref_no": "BK2026-0002",
  "status": "CONFIRMED",
  "confirmed_at": "2026-03-29T11:00:00Z"
}
```

---

### PUT /api/v1/bookings/{id}/cancel

Hủy booking. Chuyển trạng thái về `CANCELLED`.

**Request body:**

```json
{
  "reason": "Khách hàng thay đổi kế hoạch xuất hàng"
}
```

**Response 200:**

```json
{
  "id": "bk-002",
  "ref_no": "BK2026-0002",
  "status": "CANCELLED",
  "cancelled_at": "2026-03-29T14:00:00Z"
}
```

---

## Service Inquiry

### GET /api/v1/inquiries

Lấy danh sách yêu cầu dịch vụ.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| status | string | `OPEN`, `CONVERTED`, `CLOSED` |
| customer_id | string | Lọc theo khách hàng |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "inq-001",
      "ref_no": "INQ2026-0001",
      "status": "OPEN",
      "customer_id": "p-001",
      "customer_name": "Công ty TNHH ABC",
      "service_type": "FCL",
      "pol_code": "VNSGN",
      "pod_code": "CNSHA",
      "created_at": "2026-03-28T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 10
  }
}
```

---

### POST /api/v1/inquiries

Tạo mới yêu cầu dịch vụ.

**Request body:**

```json
{
  "customer_id": "p-001",
  "service_type": "FCL",
  "pol_code": "VNSGN",
  "pod_code": "CNSHA",
  "cargo_description": "Hàng điện tử",
  "container_types": ["20DC", "40HC"],
  "expected_date": "2026-04-15",
  "note": "Cần báo giá gấp"
}
```

**Response 201:**

```json
{
  "id": "inq-002",
  "ref_no": "INQ2026-0002",
  "status": "OPEN",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/inquiries/{id}/convert

Chuyển đổi inquiry thành quotation. Trả về `quotation_id` vừa tạo.

**Request body:** (không bắt buộc)

```json
{
  "note": "Chuyển từ inquiry INQ2026-0001"
}
```

**Response 200:**

```json
{
  "inquiry_id": "inq-001",
  "quotation_id": "q-003",
  "quotation_ref_no": "QT2026-0003",
  "status": "CONVERTED"
}
```

---

## Vessel Schedule

### GET /api/v1/vessel-schedules

Lấy danh sách lịch tàu.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| pol_code | string | Cảng xuất (bắt buộc nếu không có pod_code) |
| pod_code | string | Cảng đến |
| from_date | string | Ngày khởi hành từ (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "vs-005",
      "vessel_name": "EVER GIVEN",
      "voyage_no": "EG0412E",
      "carrier_id": "p-010",
      "carrier_name": "Evergreen",
      "pol_code": "VNSGN",
      "pol_name": "Cảng Sài Gòn",
      "pod_code": "CNSHA",
      "pod_name": "Shanghai Port",
      "etd": "2026-04-10",
      "eta": "2026-04-20",
      "transit_days": 10,
      "cut_off_date": "2026-04-08"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 8
  }
}
```
