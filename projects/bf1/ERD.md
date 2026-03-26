# ERD — BF1 Logistics Management

Sơ đồ Entity Relationship cho các thực thể nghiệp vụ cốt lõi của hệ thống BF1.

> **Nguồn mapping:**
> - Cloud DB (`datatpdb`): `lgc_mgmt_*` tables
> - BEE DB (MSSQL): `Transactions`, `HAWB`, `SellingRate`, `ProfitShares`, v.v.

---

## Sơ đồ Domain Driven Design

```mermaid
graph TD
    subgraph ORDER["Order Domain"]
        PO["Purchase Order"] -->|"1 → N"| BK["Booking"]
    end

    subgraph SHIPMENT["Shipment Domain"]
        MB["Transactions - Master Bill"] -->|"1 → N"| HB["House Bill"]
        HB -->|"1 → 1"| HD["Hawb Detail"]
    end

    subgraph CARGO["Cargo Domain"]
        CC["Container / Cargo / Commodity"]
    end

    subgraph PRICING["Pricing Domain"]
        RP["Rates / Profit"]
    end

    subgraph TRANSPORT["Transport Domain"]
        TP["Transport Plan"] -->|"1 → N"| TR["Transport Route"]
    end

    BK -->|"N → 1"| MB
    BK -.->|"optional"| HB
    HB -->|"1 → N"| CC
    HB -->|"1 → N"| RP
    HB -->|"1 → 1"| TP
```

---

## Sơ đồ ERD (Mermaid)

```mermaid
erDiagram
    PURCHASE_ORDER {
        varchar code PK "Mã đơn hàng (UNIQUE)"
        varchar label "Tên đơn hàng"
        bigint client_partner_id FK "Khách hàng"
        bigint assignee_employee_id FK "Nhân viên phụ trách"
    }

    BOOKING {
        varchar code PK "Mã booking (UNIQUE)"
        varchar mode "Phương thức (Air/Sea/Rail/Truck/CC)"
        varchar type "Loại (FCL/LCL/Air/...)"
        bigint purchase_order_id FK "FK → PURCHASE_ORDER"
        varchar state "Trạng thái (draft/confirmed/...)"
        timestamp close_date "Ngày đóng booking"
    }

    TRANSACTIONS_MASTER_BILL {
        varchar code PK "Mã nội bộ (UNIQUE)"
        varchar master_bill_no "Số vận đơn chủ (MAWB#/MBL#)"
        varchar transportation_mode "Phương thức (AIR/SEA/RAIL)"
        varchar shipment_type "Loại lô hàng (FCL/LCL)"
        varchar carrier_label "Hãng tàu/hàng không"
        date issued_date "Ngày phát hành"
        varchar state "Trạng thái"
    }

    HOUSE_BILL {
        varchar code PK "Mã nội bộ (UNIQUE)"
        bigint booking_process_id FK "FK → BOOKING"
        bigint master_bill_id FK "FK → TRANSACTIONS_MASTER_BILL"
        varchar shipment_type "Loại lô hàng"
        varchar shipper_label "Người gửi"
        varchar consignee_label "Người nhận"
        varchar payment_term "Điều khoản thanh toán"
        varchar status "Trạng thái"
        date issued_date "Ngày phát hành"
    }

    CONTAINER_CARGO_COMMODITY {
        bigint id PK
        bigint booking_process_id FK "FK → BOOKING"
        bigint container_id FK "FK → Container"
        varchar container_no "Số container"
        varchar container_type "Loại container (20GP/40HQ/...)"
        varchar packaging_type "Loại bao bì"
        double quantity "Số lượng"
        double gross_weight_in_kg "Trọng lượng (kg)"
        double volume_in_cbm "Thể tích (CBM)"
        varchar commodity_desc "Mô tả hàng hóa"
        varchar seal_no "Số chì seal"
    }

    RATES_PROFIT {
        bigint id PK
        varchar hawb_no FK "FK → HOUSE_BILL"
        varchar charge_code "Mã loại phí"
        varchar charge_name "Tên phí"
        varchar rate_type "Loại (Selling/Buying/Profit)"
        double quantity "Số lượng"
        double unit_price "Đơn giá"
        double amount "Thành tiền"
        varchar currency "Ngoại tệ"
        double amount_vnd "Thành tiền VND"
        varchar vendor_id "Nhà cung cấp (Buying)"
    }

    HAWB_DETAIL {
        varchar hwb_no FK "FK → HOUSE_BILL (PK cũng là FK)"
        nvarchar description "Mô tả hàng hóa"
        decimal quantity "Số lượng"
        decimal weight "Trọng lượng"
        decimal volume "Thể tích"
        varchar unit "Đơn vị"
        varchar rate_code "Mã loại phí"
        decimal rate_amount "Giá trị"
        varchar currency "Ngoại tệ"
    }

    TRANSPORT_PLAN {
        bigint id PK
        bigint booking_process_id FK "FK → BOOKING"
        bigint order_process_id FK "FK → Order Process"
        varchar state "Trạng thái"
        timestamp created_time "Ngày tạo"
    }

    TRANSPORT_ROUTE {
        bigint id PK
        bigint transport_plan_id FK "FK → TRANSPORT_PLAN"
        varchar from_location_code "Điểm đi"
        varchar from_location_label "Tên điểm đi"
        varchar to_location_code "Điểm đến"
        varchar to_location_label "Tên điểm đến"
        timestamp depart_time "Giờ khởi hành"
        timestamp arrival_time "Giờ đến"
        varchar transport_no "Số chuyến/tàu/chuyến bay"
        varchar transport_method_label "Phương tiện"
        varchar carrier_label "Hãng vận chuyển"
        int sort_order "Thứ tự chặng"
    }

    %% ─── Quan hệ ───
    PURCHASE_ORDER ||--o{ BOOKING : "1 PO → N Bookings"
    BOOKING }o--|| TRANSACTIONS_MASTER_BILL : "N Bookings → 1 Master Bill"
    TRANSACTIONS_MASTER_BILL ||--o{ HOUSE_BILL : "1 Master Bill → N House Bills"
    HOUSE_BILL ||--o{ CONTAINER_CARGO_COMMODITY : "1 HBL → N Cargo/Container"
    HOUSE_BILL ||--o{ RATES_PROFIT : "1 HBL → N Rates/Profit"
    HOUSE_BILL ||--o| HAWB_DETAIL : "1 HBL → 1 Hawb Detail"
    BOOKING ||--o| HOUSE_BILL : "1 Booking → 1 HBL (optional)"
    HOUSE_BILL ||--|| TRANSPORT_PLAN : "1 HBL → 1 Transport Plan"
    TRANSPORT_PLAN ||--o{ TRANSPORT_ROUTE : "1 Plan → N Routes"
```

---

## Quan hệ chi tiết

| Từ | Đến | Cardinality | Ghi chú |
|---|---|---|---|
| Purchase Order | Booking | 1 → N | 1 PO có nhiều booking theo mode/loại hàng |
| Booking | Transactions (Master Bill) | N → 1 | Nhiều booking gộp vào 1 master bill (consolidation) |
| Transactions (Master Bill) | House Bill | 1 → N | 1 master bill có nhiều house bill |
| Booking | House Bill | 1 → 0..1 | Booking có thể có 1 HBL trực tiếp (tùy luồng) |
| House Bill | Container/Cargo/Commodity | 1 → N | 1 HBL có nhiều cargo/container/commodity |
| House Bill | Rates/Profit | 1 → N | 1 HBL có nhiều dòng phí (selling, buying, profit) |
| House Bill | Hawb Detail | 1 → 1 | Chi tiết in ấn, thông số hàng hóa của HBL |
| House Bill | Transport Plan | 1 → 1 | Mỗi HBL gắn với 1 kế hoạch vận chuyển |
| Transport Plan | Transport Route | 1 → N | 1 kế hoạch có nhiều chặng vận chuyển |

---

## Mapping bảng thực tế

### Cloud DB (`datatpdb` — PostgreSQL)

| Entity (ERD) | Bảng thực tế | Ghi chú |
|---|---|---|
| Purchase Order | `of1_fms_purchase_order` | PK: `id`, UNIQUE: `code` |
| Booking | `of1_fms_booking_process` | FK: `purchase_order_id` |
| Transactions / Master Bill | `of1_fms_air_master_bill` | Mode: Air (MAWB) |
| | `of1_fms_sea_master_bill` | Mode: Sea (MBL) |
| | `of1_fms_rail_master_bill` | Mode: Rail |
| House Bill | `of1_fms_air_house_bill` | Mode: Air (HAWB) |
| | `of1_fms_sea_house_bill` | Mode: Sea FCL/LCL (HBL) |
| | `of1_fms_truck_house_bill` | Mode: Truck |
| | `of1_fms_rail_house_bill` | Mode: Rail |
| | `of1_fms_cc_house_bill` | Mode: Cross-Country |
| Container/Cargo/Commodity | `of1_fms_trackable_cargo` | FK: `booking_process_id`, `container_id` |
| | `of1_fms_trackable_container` | Thông tin container |
| | `of1_fms_booking_process_commodity` | Hàng hóa khai báo trong booking |
| Transport Plan | `of1_fms_transport_plan` | FK: `booking_process_id` |
| | `of1_fms_order_transport_plan` | Kế hoạch theo order |
| | `of1_fms_master_bill_transport_plan` | Kế hoạch theo master bill |
| Transport Route | `of1_fms_transport_route` | FK: `order_transport_plan_id` |

### BEE DB (BFS One — MSSQL)

| Entity (ERD) | Bảng thực tế | Ghi chú |
|---|---|---|
| Booking | `BookingLocal` | PK: `BkgID`; FK: `ConformJobNo` → Transactions |
| Transactions (Master Bill) | `Transactions` | PK: `TransID` |
| House Bill | `HAWB` | PK: `HWBNO`; FK: `TRANSID` |
| Hawb Detail | `HAWBDETAILS` | FK: `HWBNO` — chi tiết hàng hóa |
| | `HAWBRATE` | FK: `HWBNO` — giá theo vận đơn |
| Container/Cargo | `ContainerListOnHBL` | FK: `HBLNo` → HAWB |
| | `ContainerLoadedHBL` | Container đã đóng hàng |
| Rates/Profit | `SellingRate` | FK: `HAWBNO` — giá bán |
| | `BuyingRateWithHBL` | FK: `HAWBNO` — giá mua |
| | `ProfitShares` | FK: `HAWBNO` — chia lợi nhuận |
| | `OtherChargeDetail` | FK: `HBL` — phí khác |
