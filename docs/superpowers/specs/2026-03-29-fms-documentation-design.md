# FMS Documentation Framework — Design Spec

- **Date:** 2026-03-29
- **Author:** nqcdan
- **Status:** Approved

## Mục tiêu

Xây dựng bộ tài liệu kỹ thuật đầy đủ cho dự án **FMS (Freight Management System)** — hệ thống mới thay thế BF1, để dev có thể bắt đầu code ngay. Tài liệu cover cả 2 giai đoạn: Phase 1 (Read-First Migration) và Phase 2 (Write-Back Integration).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Java Spring Boot |
| Message Broker | Apache Kafka |
| Frontend | React + TypeScript |
| Database | PostgreSQL |
| CDC Source | MSSQL (BF1 cũ) via Debezium |

---

## Cấu trúc tài liệu

```
projects/fms/
├── README.md
├── architecture.md
├── schema/
│   ├── catalogue.md
│   ├── sales.md
│   ├── documentation.md
│   └── accounting.md
├── api/
│   ├── catalogue.md
│   ├── sales.md
│   ├── documentation.md
│   └── accounting.md
└── modules/
    ├── catalogue.md
    ├── sales.md
    ├── documentation.md
    └── accounting.md
```

---

## Nội dung từng file

### `README.md`
- Mô tả ngắn dự án FMS (mục tiêu, thay thế BF1)
- Tech stack table
- Bảng navigation đến từng section (architecture, schema, api, modules)
- Phase 1 vs Phase 2 overview
- Trạng thái từng module: `planned` / `in-progress` / `done`

### `architecture.md`
- Sơ đồ kiến trúc tổng thể (text/mermaid):
  `MSSQL → Debezium → Kafka → Consumer → PostgreSQL`
- Tech stack chi tiết từng component
- CDC event format: `before` / `after` / `op` (c/u/d/r)
- Phase 1 data flow: sync-only, read-first
- Phase 2 data flow: write vào DB mới, đồng bộ ngược về MSSQL

### `schema/catalogue.md`
- Shared/master entities dùng chung toàn hệ thống
- Bảng: `settings_country`, `settings_currency`, `settings_location`, `of1_fms_partner`, `of1_fms_user_role`
- Mỗi bảng: columns (type, nullable, FK), enum values, sample data

### `schema/sales.md`
- Entities cho module Sales Executive
- Bảng: Vessel Schedules, Quotation (Air/Sea/Express), Booking Request/Confirm, Service Inquiry, P/L Sheet
- Relations đến catalogue entities

### `schema/documentation.md`
- Entities cho module Documentation
- Bảng: `of1_fms_transactions` (Master Bill), House Bill, Shipment ops, chứng từ
- State machine cho transaction lifecycle

### `schema/accounting.md`
- Entities cho module Accounting
- Bảng: Invoice, Payment, Cost/Revenue entries, Debit/Credit Note
- Relations đến transactions và partner

### `api/*.md` (mỗi module)
- Danh sách endpoints theo resource
- Format: `METHOD /path` — mô tả ngắn
- Request body (fields, types, required)
- Response format
- Error codes

### `modules/*.md` (mỗi module)
- Business flow dạng mermaid diagram
- State/status lifecycle của entity chính
- Business rules quan trọng (validation, constraints)
- Danh sách màn hình liên quan

---

## Module order

Tài liệu được build theo thứ tự luồng nghiệp vụ:

1. **Catalogue** — Master data, Partner, User/Role (foundation)
2. **Sales** — Inquiry → Quotation → Booking
3. **Documentation** — Booking → Shipment ops → B/L → Chứng từ
4. **Accounting** — Shipment → Invoice → Payment → Báo cáo

---

## Nguồn dữ liệu hiện có

Tái sử dụng từ wiki hiện tại:
- `projects/bf1/fms/erd.md` — ERD entities và columns
- `projects/bf1/fms/master-data.md` — Master data tables + sample data
- `projects/bf1/bfs/of1-project-analysis.md` — Module breakdown, business flow
- `projects/bf1/fms/cdc-architecture.md` — CDC pipeline details
- `projects/bf1/project-overview.md` — Phase 1/2 strategy

---

## Phạm vi không bao gồm

- Setup guide (local dev environment)
- Deployment / DevOps docs
- Security / monitoring docs
- Onboarding guide
