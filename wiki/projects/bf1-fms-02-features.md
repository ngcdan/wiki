---
title: "FMS 02 - Features"
tags: [bf1, fms]
---

# Feature Specification

Tài liệu phân tích nghiệp vụ và đặc tả tính năng của hệ thống OF1 FMS.

See also: [[bf1-fms-01-overview]] · [[bf1-fms-03-data-model]]

---

## 1. Applications

| App | Purpose |
|-----|---------|
| **Catalogue** | Master Data — đối tác, cảng, container, danh mục |
| **CRM** | Sales Executive — báo giá, đặt chỗ, internal booking |
| **FMS** | Documentations — chứng từ, vận đơn, giá mua/bán, invoice |
| **Accounting** | Accounting — hoá đơn điện tử, công nợ, tạm ứng, báo cáo |

---

## 2. Business Process — Vòng đời lô hàng (13 bước)

```mermaid
flowchart TD
    S1["1. Tiếp nhận khách hàng<br/>Catalogue > Leads"]
    S2["2. Tạo Customer<br/>Catalogue > Customer"]
    S3{"3. Tạo báo giá<br/>CRM > Quotation"}
    S3A["Air"]
    S3B["Sea"]
    S3C["Rail"]
    S3D["Trucking"]
    S3E["Custom Clearance"]
    S4["4. Booking Request<br/>CRM > Internal Booking"]
    S5["5. Xác nhận Booking<br/>FMS > Booking Confirm"]
    S6{"6. Mở File chứng từ<br/>FMS > Documentations"}
    S7["7. Tạo vận đơn<br/>HAWB / HBL + MAWB / MBL"]
    S8["8. Nhập giá mua/bán<br/>Buying Rate / Selling Rate"]
    S9["9. Xuất Debit/Credit Note<br/>cho Customer / Agent / Carrier"]
    S10["10. Xuất hoá đơn điện tử<br/>Accounting > VAT Invoice"]
    S11["11. Đối soát công nợ<br/>Transaction Register > SOA"]
    S12["12. Thanh toán<br/>History of Payment"]
    S13["13. Báo cáo lợi nhuận<br/>CRM > P/L Sheet"]

    ADV["Advance Request / Tạm ứng"]
    SETTLE["Settlement / Giải trình"]
    CUSTOMS["Customs Clearance"]
    TRACE["Tracing ETD-ETA"]
    EDI["Send/Receive EDI"]

    S1 --> S2 --> S3
    S3 --> S3A & S3B & S3C & S3D & S3E
    S3A & S3B & S3C & S3D & S3E --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> S10 --> S11 --> S12 --> S13

    S8 -.-> ADV
    S9 -.-> SETTLE
    S6 -.-> CUSTOMS
    S5 -.-> TRACE
    S6 -.-> EDI
```

Xem thêm: [[bf1-fms-01-overview|01-overview.md §3]] cho chi tiết Invoice Flow và Settlement Flow.

---

## 3. Core Features

### 3.1 Transaction Management (Quản lý lô hàng)

- Create shipment from booking request
- Track shipment status (draft, confirmed, in-transit, delivered, closed)
- Multiple service types: Air Export/Import, Sea FCL/LCL, Customs & Logistics, Inland Trucking, Cross Border
- Manage ETD/ETA and tracking events
- Support multiple house bills per shipment

**Entities:** `of1_fms_transactions`, `of1_fms_booking_process`

### 3.2 House Bill & Documentation

**House Bill:**
- Generate house bills (HAWB/HBL) per house customer
- Service-specific details (Air, Sea, Trucking, Logistics)
- Container tracking
- Cargo description, commodity classification, HS code
- Bill status workflow

**Documentation:**
- Authorize Letter, Delivery Order generation
- Document versioning and history (PDF snapshot with audit trail)
- Multi-language support (Vietnamese & English)
- Company info, shipper/consignee/notify party capture

**Entities:** `of1_fms_house_bill`, `of1_fms_house_bill_detail_base`, `of1_fms_air_house_bill_detail`, `of1_fms_sea_house_bill_detail`, `of1_fms_document_history`

### 3.3 Rate Management

**Selling Rates:** Charge tracking per house bill, multi-currency, VND equivalents, tax calculation.
**Buying Rates:** Vendor-based cost tracking, margin analysis, on-behalf-of handling.
**Other Charges:** Demurrage, detention, storage.

**Entities:** `of1_fms_hawb_rates`, `of1_fms_house_bill_invoice`, `of1_fms_house_bill_invoice_item`

### 3.4 Invoicing & Debit Notes

- Generate debit/credit notes
- Multi-party invoicing (customer, agent, carrier)
- Tax calculation and VAT handling
- Currency management with exchange rates
- Invoice status tracking and approval workflow
- Line-item breakdown by charge type
- Partial payment tracking, settlement reconciliation

**Entities:** `of1_fms_house_bill_invoice`, `of1_fms_house_bill_invoice_item`

### 3.5 Transportation & Tracking

**Transport Planning:** Multi-leg journey, route sequencing, carrier per leg, ETD/ETA per leg.
**Container Management:** Type, count, seal, weight/volume per container.
**Cargo Tracking:** Per-piece tracking, commodity, packaging, HS code, container linkage.

**Entities:** `of1_fms_transport_plan`, `of1_fms_transport_route`, `of1_fms_container`, `of1_fms_cargo`

### 3.6 Order & Booking Management

**Purchase Order:** Master order from customer, multiple bookings per order (phased shipments).
**Booking Process:** Service-type specific booking, link to PO, state tracking, close date.

**Entities:** `of1_fms_purchase_order`, `of1_fms_booking_process`

### 3.7 Payment Tracking

- Multiple payments per invoice item or full invoice
- Payment date and amount tracking
- Currency-specific payment records
- Payment history and reconciliation
- Settlement status tracking

---

## 4. System Entity Relationships

```mermaid
graph TD
    PO["Purchase Order<br/>(Customer Request)"]
    BP["Booking Process<br/>(Service Type)"]
    HB["House Bill<br/>(House Customer)"]
    TX["Transaction<br/>(Master Bill)"]

    RATES["Rates<br/>(Selling/Buying)"]
    INV["Invoice<br/>(Debit/Credit)"]
    DOCS["Documents<br/>(Authorize Letter, DO)"]

    TRANS["Transport<br/>(Routes & Legs)"]
    CARGO["Cargo<br/>(Packages & HS)"]
    CONT["Container<br/>(Sea/Air)"]

    PO -->|"1:N"| BP
    BP -->|"1:N"| HB
    TX -->|"1:N"| HB

    HB -->|"1:N"| RATES
    HB -->|"1:N"| INV
    HB -->|"1:N"| DOCS

    HB -->|"1:N"| TRANS
    HB -->|"1:N"| CARGO
    TX -->|"1:N"| CONT

    CARGO -->|"N:1"| CONT
    TRANS -->|"1:N"| CARGO

    INV -->|"1:N"| RATES
```

---

## 5. Audit & Compliance

All entities support common audit fields:

- `created_by` / `created_time` — creation audit
- `modified_by` / `modified_time` — modification audit
- `version` — optimistic locking
- `storage_state` — record lifecycle (`CREATED`, `ACTIVE`, `INACTIVE`, `JUNK`, `DEPRECATED`, `ARCHIVED`)
- `company_id` — multi-tenant isolation

---

## 6. Cross-Cutting Capabilities

- **Vietnamese Localization:** bilingual labels, regional compliance (VND, local tax codes)
- **Multi-Currency:** exchange rate management, domestic (VND) equivalents
- **Service Type Support:** Air, Sea FCL/LCL, customs, trucking, cross-border, warehouse
