# API Spec — Catalogue (Partner, Users, Master Data)

> Cross-reference: xem `schema/catalogue.md` cho định nghĩa đầy đủ của các entity.

Base URL: `/api/v1`

---

## Standard Error Response

Tất cả các endpoint trả về lỗi theo định dạng sau:

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Partner not found",
  "status": 404
}
```

| HTTP Status | Ý nghĩa |
|---|---|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request (validation) |
| 404 | Not Found |
| 409 | Conflict (trùng dữ liệu) |
| 500 | Internal Server Error |

---

## Phase 1 vs Phase 2

| Endpoint group | Phase 1 | Phase 2 |
|---|---|---|
| GET /partners, GET /users (all & one) | ✓ read-only | ✓ |
| POST/PUT /partners, POST/PUT /users | ✗ | ✓ writable |
| DELETE /partners/{id} | ✗ | ✓ writable |
| GET /settings/* (master data) | ✓ read-only | ✓ |

---

## Partner

### GET /api/v1/partners

Lấy danh sách partner.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type | string | Loại partner: `CUSTOMER`, `CARRIER`, `AGENT`, `VENDOR` |
| status | string | Trạng thái: `ACTIVE`, `LOCK` |
| page | integer | Số trang (bắt đầu từ 1, mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "p-001",
      "code": "KH001",
      "name": "Công ty TNHH ABC",
      "type": "CUSTOMER",
      "status": "ACTIVE",
      "tax_code": "0123456789",
      "country_code": "VN",
      "created_at": "2025-01-15T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 150
  }
}
```

---

### GET /api/v1/partners/{id}

Lấy thông tin chi tiết một partner.

**Response 200:**

```json
{
  "id": "p-001",
  "code": "KH001",
  "name": "Công ty TNHH ABC",
  "type": "CUSTOMER",
  "status": "ACTIVE",
  "tax_code": "0123456789",
  "country_code": "VN",
  "address": "123 Nguyễn Huệ, Q.1, TP.HCM",
  "email": "contact@abc.com",
  "phone": "+84901234567",
  "credit_limit": 500000000,
  "credit_days": 30,
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-03-01T10:30:00Z"
}
```

**Response 404:**

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Partner not found",
  "status": 404
}
```

---

### POST /api/v1/partners

Tạo mới partner.

**Request body:**

```json
{
  "code": "KH002",
  "name": "Công ty CP XYZ",
  "type": "CUSTOMER",
  "tax_code": "0987654321",
  "country_code": "VN",
  "address": "456 Lê Lợi, Q.1, TP.HCM",
  "email": "info@xyz.com",
  "phone": "+84907654321",
  "credit_limit": 200000000,
  "credit_days": 45
}
```

**Response 201:**

```json
{
  "id": "p-002",
  "code": "KH002",
  "name": "Công ty CP XYZ",
  "type": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2026-03-29T09:00:00Z"
}
```

**Response 409** — khi `code` hoặc `tax_code` đã tồn tại:

```json
{
  "code": "DUPLICATE_PARTNER_CODE",
  "message": "Partner code KH002 already exists",
  "status": 409
}
```

---

### PUT /api/v1/partners/{id}

Cập nhật thông tin partner.

**Request body:** (chỉ gửi các field cần thay đổi)

```json
{
  "name": "Công ty CP XYZ (Đã đổi tên)",
  "email": "new@xyz.com",
  "credit_limit": 300000000
}
```

**Response 200:** Trả về partner sau khi cập nhật (cùng cấu trúc với GET one).

---

### DELETE /api/v1/partners/{id}

Soft-delete partner: chuyển `status` thành `LOCK`.

**Response 200:**

```json
{
  "id": "p-002",
  "status": "LOCK",
  "updated_at": "2026-03-29T10:00:00Z"
}
```

---

## Users

### GET /api/v1/users

Lấy danh sách người dùng.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| status | string | Trạng thái: `ACTIVE`, `INACTIVE` |
| page | integer | Số trang (mặc định: 1) |
| size | integer | Số bản ghi mỗi trang (mặc định: 20) |

**Response 200:**

```json
{
  "data": [
    {
      "id": "u-001",
      "username": "nguyen.van.a",
      "full_name": "Nguyễn Văn A",
      "email": "a@company.com",
      "role": "SALES",
      "status": "ACTIVE",
      "created_at": "2025-06-01T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 25
  }
}
```

---

### GET /api/v1/users/{id}

Lấy thông tin chi tiết một user.

**Response 200:**

```json
{
  "id": "u-001",
  "username": "nguyen.van.a",
  "full_name": "Nguyễn Văn A",
  "email": "a@company.com",
  "role": "SALES",
  "status": "ACTIVE",
  "partner_id": null,
  "created_at": "2025-06-01T08:00:00Z",
  "updated_at": "2026-01-10T09:00:00Z"
}
```

---

### POST /api/v1/users

Tạo mới user.

**Request body:**

```json
{
  "username": "tran.thi.b",
  "full_name": "Trần Thị B",
  "email": "b@company.com",
  "role": "DOCUMENTATION",
  "password": "initial_password_hash"
}
```

**Response 201:**

```json
{
  "id": "u-002",
  "username": "tran.thi.b",
  "full_name": "Trần Thị B",
  "email": "b@company.com",
  "role": "DOCUMENTATION",
  "status": "ACTIVE",
  "created_at": "2026-03-29T09:00:00Z"
}
```

---

### PUT /api/v1/users/{id}

Cập nhật thông tin user.

**Request body:** (chỉ gửi các field cần thay đổi)

```json
{
  "full_name": "Trần Thị B (cập nhật)",
  "role": "ACCOUNTING",
  "status": "INACTIVE"
}
```

**Response 200:** Trả về user sau khi cập nhật (cùng cấu trúc với GET one).

---

## Master Data (read-only)

### GET /api/v1/settings/countries

Lấy danh sách quốc gia.

**Response 200:**

```json
{
  "data": [
    { "code": "VN", "name": "Việt Nam", "phone_code": "+84" },
    { "code": "CN", "name": "China", "phone_code": "+86" },
    { "code": "US", "name": "United States", "phone_code": "+1" }
  ]
}
```

---

### GET /api/v1/settings/currencies

Lấy danh sách tiền tệ.

**Response 200:**

```json
{
  "data": [
    { "code": "VND", "name": "Vietnamese Dong", "symbol": "₫" },
    { "code": "USD", "name": "US Dollar", "symbol": "$" },
    { "code": "EUR", "name": "Euro", "symbol": "€" }
  ]
}
```

---

### GET /api/v1/settings/locations

Lấy danh sách địa điểm (cảng, sân bay, kho).

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type | string | Loại: `PORT`, `AIRPORT`, `WAREHOUSE` |

**Response 200:**

```json
{
  "data": [
    {
      "code": "VNSGN",
      "name": "Cảng Sài Gòn",
      "type": "PORT",
      "country_code": "VN",
      "city": "Ho Chi Minh City"
    },
    {
      "code": "VNHAN",
      "name": "Cảng Hải Phòng",
      "type": "PORT",
      "country_code": "VN",
      "city": "Hai Phong"
    }
  ]
}
```

---

### GET /api/v1/settings/ports

Shorthand cho `/api/v1/settings/locations?type=PORT` hoặc `type=AIRPORT`. Trả về danh sách cảng biển và sân bay.

**Query params:**

| Tham số | Kiểu | Mô tả |
|---|---|---|
| type | string | `PORT` (mặc định) hoặc `AIRPORT` |

**Response 200:** Cùng cấu trúc với `/settings/locations`.
