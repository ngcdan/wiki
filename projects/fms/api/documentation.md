# API Spec — Documentation (Transaction, House Bill, Cargo & Container)

> Cross-reference: xem `schema/documentation.md` cho định nghĩa đầy đủ của các entity.

Base URL: `/api/v1`

> Lỗi response: xem định nghĩa chuẩn trong `api/catalogue.md`.

---

## Phase 1 vs Phase 2

| Endpoint group | Phase 1 | Phase 2 |
|---|---|---|
| GET /transactions (all & one) | ✓ read-only (synced từ CDC) | ✓ |
| POST/PUT /transactions | ✗ | ✓ writable |
| GET /house-bills (all & one) | ✓ read-only (synced từ CDC) | ✓ |
| POST/PUT /house-bills | ✗ | ✓ writable |
| GET containers & commodities | ✓ read-only | ✓ |
| POST containers & commodities | ✗ | ✓ writable |

---

## Transactions (Master Bill)

### GET /api/v1/transactions

Lấy danh sách transaction (Master Bill of Lading).

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type_of_service | string | Loại dịch vụ: `FCL`, `LCL`, `AIR`, `TRUCKING` |
| state | string | Trạng thái: `OPEN`, `IN_TRANSIT`, `ARRIVED`, `COMPLETED`, `CANCELLED` |
| from_date | string | Ngày tạo từ (ISO 8601: `YYYY-MM-DD`) |
| to_date | string | Ngày tạo đến (ISO 8601: `YYYY-MM-DD`) |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "tx-001",
      "ref_no": "TX2026-0001",
      "mbl_no": "EVGL123456789",
      "type_of_service": "FCL",
      "state": "IN_PROGRESS",
      "shipper_id": "p-001",
      "consignee_id": "p-020",
      "pol_code": "VNSGN",
      "pod_code": "CNSHA",
      "etd": "2026-04-10",
      "eta": "2026-04-20",
      "created_at": "2026-03-20T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 112
  }
}
```

---

### GET /api/v1/transactions/{id}

Lấy chi tiết một transaction.

**Response 200:**

```json
{
  "id": "tx-001",
  "ref_no": "TX2026-0001",
  "mbl_no": "EVGL123456789",
  "type_of_service": "FCL",
  "state": "IN_PROGRESS",
  "shipper_id": "p-001",
  "shipper_name": "Công ty TNHH ABC",
  "consignee_id": "p-020",
  "consignee_name": "Shanghai Trading Co.",
  "notify_party": "Same as consignee",
  "carrier_id": "p-010",
  "carrier_name": "Evergreen",
  "vessel_name": "EVER GIVEN",
  "voyage_no": "EG0412E",
  "pol_code": "VNSGN",
  "pol_name": "Cảng Sài Gòn",
  "pod_code": "CNSHA",
  "pod_name": "Shanghai Port",
  "etd": "2026-04-10",
  "eta": "2026-04-20",
  "booking_id": "bk-001",
  "house_bill_count": 3,
  "note": null,
  "created_by": "u-002",
  "created_at": "2026-03-20T08:00:00Z",
  "updated_at": "2026-03-25T14:00:00Z"
}
```

---

### POST /api/v1/transactions

Tạo mới transaction (Master Bill).

**Request body:**

```json
{
  "type_of_service": "FCL",
  "mbl_no": "EVGL999000111",
  "shipper_id": "p-001",
  "consignee_id": "p-020",
  "notify_party": "Same as consignee",
  "carrier_id": "p-010",
  "vessel_name": "EVER GIVEN",
  "voyage_no": "EG0412E",
  "pol_code": "VNSGN",
  "pod_code": "CNSHA",
  "etd": "2026-04-10",
  "eta": "2026-04-20",
  "booking_id": "bk-001",
  "note": null
}
```

**Response 201:**

```json
{
  "id": "tx-002",
  "ref_no": "TX2026-0002",
  "state": "OPEN",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/transactions/{id}

Cập nhật thông tin transaction.

**Request body:** (chỉ gửi các field cần thay đổi)

```json
{
  "vessel_name": "EVER ACE",
  "voyage_no": "EA0415E",
  "etd": "2026-04-15",
  "eta": "2026-04-25"
}
```

**Response 200:** Trả về transaction sau khi cập nhật (cùng cấu trúc với GET one).

---

### PUT /api/v1/transactions/{id}/state

Thay đổi trạng thái của transaction.

**Request body:**

```json
{
  "state": "COMPLETED"
}
```

Giá trị hợp lệ cho `state`: `OPEN`, `IN_TRANSIT`, `ARRIVED`, `COMPLETED`, `CANCELLED`.

**Response 200:**

```json
{
  "id": "tx-001",
  "ref_no": "TX2026-0001",
  "state": "COMPLETED",
  "updated_at": "2026-03-29T10:00:00Z"
}
```

**Response 400** — khi chuyển trạng thái không hợp lệ:

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "message": "Cannot transition from COMPLETED to OPEN",
  "status": 400
}
```

---

## House Bill

### GET /api/v1/house-bills

Lấy danh sách House Bill of Lading.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| transaction_id | string | Lọc theo transaction (Master Bill) |
| status | string | Trạng thái: `DRAFT`, `CONFIRMED`, `ISSUED`, `COMPLETED`, `SURRENDERED`, `TELEX_RELEASED` |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "hb-001",
      "ref_no": "HB2026-0001",
      "hbl_no": "FMS-HB-001",
      "status": "ISSUED",
      "transaction_id": "tx-001",
      "shipper_id": "p-001",
      "consignee_id": "p-020",
      "pol_code": "VNSGN",
      "pod_code": "CNSHA",
      "created_at": "2026-03-21T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 58
  }
}
```

---

### GET /api/v1/house-bills/{id}

Lấy chi tiết một House Bill.

**Response 200:**

```json
{
  "id": "hb-001",
  "ref_no": "HB2026-0001",
  "hbl_no": "FMS-HB-001",
  "status": "ISSUED",
  "transaction_id": "tx-001",
  "shipper_id": "p-001",
  "shipper_name": "Công ty TNHH ABC",
  "consignee_id": "p-020",
  "consignee_name": "Shanghai Trading Co.",
  "notify_party": "Same as consignee",
  "pol_code": "VNSGN",
  "pol_name": "Cảng Sài Gòn",
  "pod_code": "CNSHA",
  "pod_name": "Shanghai Port",
  "description_of_goods": "Electronic components",
  "gross_weight": 12500.0,
  "gross_weight_unit": "KGS",
  "measurement": 45.5,
  "measurement_unit": "CBM",
  "container_count": 2,
  "created_by": "u-002",
  "issued_at": "2026-03-22T10:00:00Z",
  "created_at": "2026-03-21T08:00:00Z",
  "updated_at": "2026-03-22T10:00:00Z"
}
```

---

### POST /api/v1/house-bills

Tạo mới House Bill.

**Request body:**

```json
{
  "transaction_id": "tx-001",
  "hbl_no": "FMS-HB-002",
  "shipper_id": "p-001",
  "consignee_id": "p-020",
  "notify_party": "Same as consignee",
  "pol_code": "VNSGN",
  "pod_code": "CNSHA",
  "description_of_goods": "Electronic components",
  "gross_weight": 12500.0,
  "gross_weight_unit": "KGS",
  "measurement": 45.5,
  "measurement_unit": "CBM"
}
```

**Response 201:**

```json
{
  "id": "hb-002",
  "ref_no": "HB2026-0002",
  "status": "DRAFT",
  "transaction_id": "tx-001",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/house-bills/{id}

Cập nhật thông tin House Bill (chỉ khi `status = DRAFT`).

**Request body:** (chỉ gửi các field cần thay đổi)

```json
{
  "description_of_goods": "Electronic components - revised",
  "gross_weight": 13000.0
}
```

**Response 200:** Trả về house bill sau khi cập nhật (cùng cấu trúc với GET one).

---

### GET /api/v1/transactions/{id}/house-bills

Lấy tất cả House Bill thuộc một transaction.

**Response 200:** Cùng cấu trúc với `GET /api/v1/house-bills` nhưng không cần truyền `transaction_id` trong query (đã được xác định qua path).

```json
{
  "data": [
    {
      "id": "hb-001",
      "ref_no": "HB2026-0001",
      "hbl_no": "FMS-HB-001",
      "status": "ISSUED",
      "transaction_id": "tx-001",
      "shipper_name": "Công ty TNHH ABC",
      "consignee_name": "Shanghai Trading Co.",
      "created_at": "2026-03-21T08:00:00Z"
    },
    {
      "id": "hb-002",
      "ref_no": "HB2026-0002",
      "hbl_no": "FMS-HB-002",
      "status": "DRAFT",
      "transaction_id": "tx-001",
      "shipper_name": "Công ty TNHH ABC",
      "consignee_name": "Shanghai Trading Co.",
      "created_at": "2026-03-29T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 2
  }
}
```

---

## Cargo & Container

### GET /api/v1/house-bills/{id}/containers

Lấy danh sách container thuộc một House Bill.

**Response 200:**

```json
{
  "data": [
    {
      "id": "c-001",
      "house_bill_id": "hb-001",
      "container_no": "EVGU1234567",
      "container_type": "20DC",
      "seal_no": "SL-98765",
      "gross_weight": 6200.0,
      "tare_weight": 2200.0,
      "net_weight": 4000.0,
      "measurement": 22.0
    },
    {
      "id": "c-002",
      "house_bill_id": "hb-001",
      "container_no": "EVGU7654321",
      "container_type": "40HC",
      "seal_no": "SL-11223",
      "gross_weight": 6300.0,
      "tare_weight": 3900.0,
      "net_weight": 2400.0,
      "measurement": 23.5
    }
  ]
}
```

---

### POST /api/v1/house-bills/{id}/containers

Thêm container vào House Bill.

**Request body:**

```json
{
  "container_no": "EVGU9999999",
  "container_type": "40DC",
  "seal_no": "SL-55555",
  "gross_weight": 7000.0,
  "tare_weight": 2200.0,
  "measurement": 25.0
}
```

**Response 201:**

```json
{
  "id": "c-003",
  "house_bill_id": "hb-001",
  "container_no": "EVGU9999999",
  "container_type": "40DC",
  "created_at": "2026-03-29T10:00:00Z"
}
```

---

### GET /api/v1/house-bills/{id}/commodities

Lấy danh sách hàng hóa (commodity) thuộc một House Bill.

**Response 200:**

```json
{
  "data": [
    {
      "id": "cm-001",
      "house_bill_id": "hb-001",
      "hs_code": "8542.31",
      "description": "Integrated circuits",
      "quantity": 500,
      "unit": "CTNS",
      "gross_weight": 12500.0,
      "net_weight": 11000.0,
      "measurement": 45.5
    }
  ]
}
```

---

### POST /api/v1/house-bills/{id}/commodities

Thêm hàng hóa vào House Bill.

**Request body:**

```json
{
  "hs_code": "8542.39",
  "description": "Semiconductor devices",
  "quantity": 200,
  "unit": "CTNS",
  "gross_weight": 5000.0,
  "net_weight": 4500.0,
  "measurement": 18.0
}
```

**Response 201:**

```json
{
  "id": "cm-002",
  "house_bill_id": "hb-001",
  "hs_code": "8542.39",
  "description": "Semiconductor devices",
  "created_at": "2026-03-29T10:00:00Z"
}
```
