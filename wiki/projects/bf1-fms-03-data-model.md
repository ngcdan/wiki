---
title: "FMS 03 - Data Model"
tags: [bf1, fms]
---

# Data Model & Schema

Comprehensive data model covering entity relationships, master data structures, and database schema for OF1 FMS.

See also: [[bf1-fms-02-features]] · [[bf1-fms-mapping-readme]] for source→target field mappings.

---

## 1. Entity Diagrams

### 1.1 Domain Driven Design Overview
![DDD](img/ddd.png)

### 1.2 FMS ERD
![ERD FMS](img/fms-erd.png)

### 1.3 UI Transaction Form
![UI Transaction Form](img/UITransactionForm.png)

---

## 2. Core Transaction & Bill

### 2.1 `of1_fms_transactions` — Master Bill

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `code` | varchar | ✓ | Mã lô hàng — UNIQUE (e.g. `BIHCM008238/25`) |
| `transaction_date` | timestamp |  | Ngày tạo lô hàng (nghiệp vụ) |
| `issued_date` | timestamp |  | Ngày phát hành |
| `etd` | timestamp |  | Estimated Time of Departure |
| `eta` | timestamp |  | Estimated Time of Arrival |
| `created_by_account_id` | bigint |  | FK → `of1_fms_user_role.id` |
| `created_by_account_name` | varchar |  | Tên người tạo lô (denormalized) |
| `master_bill_no` | varchar |  | Số vận đơn chủ (MAWB# / MBL#) |
| `type_of_service` | enum TypeOfService |  | Loại dịch vụ (xem §6) |
| `shipment_type` | enum ShipmentType |  | `FREEHAND` / `NOMINATED` |
| `incoterms` | enum Incoterms |  | Điều kiện giao hàng (xem §6) |
| `carrier_partner_id` | bigint |  | FK → `of1_fms_partner.id` |
| `carrier_label` | varchar |  | Tên hãng vận chuyển (denormalized) |
| `handling_agent_partner_id` | bigint |  | FK → `of1_fms_partner.id` |
| `handling_agent_label` | varchar |  | (denormalized) |
| `transport_name` | varchar |  | Vessel / flight / xe |
| `transport_no` | varchar |  | Voyage no / flight no / biển số |
| `from_location_code` | varchar |  | POL (FK → `of1_fms_settings_location.code`) |
| `from_location_label` | varchar |  | (denormalized) |
| `to_location_code` | varchar |  | POD |
| `to_location_label` | varchar |  | (denormalized) |
| `cargo_gross_weight_in_kgs` | double |  | GW trên MAWB |
| `cargo_volume_in_cbm` | double |  | CBM trên MAWB |
| `cargo_chargeable_weight_in_kgs` | double |  | CW trên MAWB |
| `package_quantity` | int |  | Số kiện hàng |
| `packaging_type` | varchar |  | Loại bao bì |
| `container_vol` | varchar |  | `ContainerSize` text — parse sinh ra Container (xem [[bf1-fms-mapping-container]]) |

### 2.2 `of1_fms_house_bill`

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `hawb_no` | varchar | ✓ | Mã house bill — UNIQUE |
| `type_of_service` | enum TypeOfService |  | |
| `booking_process_id` | bigint |  | FK → `of1_fms_booking_process.id` |
| `transaction_id` | bigint |  | FK → `of1_fms_transactions.id` |
| `shipment_type` | enum ShipmentType |  | |
| `client_partner_id` | bigint |  | FK → `of1_fms_partner.id` (customer) |
| `client_label` | varchar |  | (denormalized) |
| `shipper_partner_id` | bigint |  | FK → `of1_fms_partner.id` |
| `shipper_label` | varchar |  | (denormalized) |
| `consignee_partner_id` | bigint |  | FK → `of1_fms_partner.id` |
| `consignee_label` | varchar |  | (denormalized) |
| `handling_agent_partner_id` | bigint |  | FK → `of1_fms_partner.id` |
| `handling_agent_label` | varchar |  | (denormalized) |
| `saleman_account_id` | bigint |  | FK → `of1_fms_user_role.id` |
| `saleman_label` | varchar |  | (denormalized) |
| `assignee_account_id` | bigint |  | FK → `of1_fms_user_role.id` |
| `assignee_label` | varchar |  | (denormalized) |
| `status` | varchar |  | Trạng thái |
| `issued_date` | date |  | |
| `consigned_date` | timestamp |  | Ngày handover cho carrier |
| `cargo_gross_weight_in_kgs` | double |  | GW |
| `cargo_volume_in_cbm` | double |  | CBM |
| `cargo_chargeable_weight_in_kgs` | double |  | CW |
| `container_vol` | varchar |  | `ContainerSize` text |
| `desc_of_goods` | varchar |  | Mô tả hàng hoá |
| `package_quantity` | int |  | |
| `packaging_type` | varchar |  | |

**Relationships:**

| From | → | To | Meaning |
|------|---|-----|---------|
| Transaction | 1 : N | House Bill | MAWB chứa nhiều HAWB |
| House Bill | 1 : N | `house_bill_detail_base` | Base detail lines |
| House Bill | 1 : N | `air / sea / truck / logistics_house_bill_detail` | Service-specific details |
| House Bill | 1 : N | `cargo` | Cargo items (commodity, HS, container link) |
| House Bill | 1 : N | `hawb_rates` | Buying/selling/OBH charges |
| House Bill | 1 : N | `house_bill_invoice` | Debit/Credit notes |

### 2.3 `of1_fms_house_bill_detail_base`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `house_bill_id` | bigint | FK → `of1_fms_house_bill.id` |
| `payment_term` | varchar | |
| `description_of_goods` | varchar | |
| `quantity` | decimal | |
| `weight` | decimal | |
| `volume` | decimal | |
| `rate_code` | varchar | |

### 2.4 Service-Specific Details

**`of1_fms_air_house_bill_detail`:** `shipper_*`, `consignee_*`, `notify_party_*`, `no_of_original_hbl`.

**`of1_fms_sea_house_bill_detail`:** fields of Air + `manifest_no`, `require_hc_surrender`, `require_hc_seaway`, `require_hc_original`, `free_demurrage_note`, `free_detention_note`, `free_storage_note`.

**`of1_fms_truck_house_bill_detail`:** minimal placeholder (FMS-only).

**`of1_fms_logistics_house_bill_detail`:** `cds_no`, `cds_date`, `customs_agency_*`, `selectivity_of_customs`, `ops_account_id`, `ops_label`.

---

## 3. Cargo, Container & Transport

### 3.1 `of1_fms_container`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `transaction_id` | bigint | FK → `of1_fms_transactions.id` |
| `container_no` | varchar | Số container |
| `container_type` | varchar | `20GP` / `40HQ` / `40HC` / ... |
| `seal_no` | varchar | Số chì |
| `quantity` | double | Số lượng |
| `gross_weight_in_kg` | double | |
| `volume_in_cbm` | double | |

Two CDC sources: (1) `TransactionsCDCHandler` parses `ContainerSize` text (`"2x40HC & 1x20"`) to create type+quantity records; (2) `ContainerListOnHBLCDCHandler` creates line-item records from `dbo.ContainerListOnHBL` with container_no + seal_no. Xem [[bf1-fms-mapping-container]].

### 3.2 `of1_fms_cargo`

Kết hợp Commodity + Cargo. Mỗi record là một kiện/lô hàng trong house bill, có thể gắn với container cụ thể.

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `house_bill_id` | bigint | ✓ | FK → `of1_fms_house_bill.id` |
| `container_id` | bigint |  | FK → `of1_fms_container.id` (nullable) |
| `commodity_code` | varchar |  | FK → `of1_fms_settings_commodity.code` |
| `commodity_type` | varchar |  | |
| `commodity_desc` | varchar(1024) |  | |
| `desc_of_goods` | varchar(2048) |  | |
| `hs_code` | varchar |  | |
| `weight` | double |  | GW |
| `volume` | double |  | CBM |
| `packaging_type` | varchar |  | |
| `package_quantity` | int |  | |
| `dimension_length / _width / _height` | double |  | cm |
| `stackable` | enum |  | `STACKABLE` / `NON_STACKABLE` |

Auto-upsert từ `HAWBCDCHandler` sử dụng GW/CBM/Pieces từ `dbo.HAWB`. Xem [[bf1-fms-mapping-cargo]].

### 3.3 `of1_fms_transport_plan` & `of1_fms_transport_route`

**Transport Plan** (header): `house_bill_id`, `from_location_*`, `to_location_*`, `depart_time`, `arrival_time`, `transport_name`, `flight_date_confirm`.

**Transport Route** (legs): `transport_plan_id`, `from_location_*`, `to_location_*`, `depart_time`, `arrival_time`, `transport_no`, `carrier_label`, `sort_order`.

Rebuilt mỗi lần Transaction CDC event đến (delete + recreate). Xem [[bf1-fms-mapping-transport-plan]].

---

## 4. Invoicing & Financial

### 4.1 `of1_fms_house_bill_invoice`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `house_bill_id` | bigint | FK |
| `invoice_type` | enum | `DEBIT` / `CREDIT` |
| `payer_partner_id` / `payer_label` | bigint / varchar | |
| `payee_partner_id` / `payee_label` | bigint / varchar | |
| `state` | varchar | Trạng thái |
| `currency` | varchar | |
| `total_amount` / `total_tax` / `total_final_charge` | double | Trước/thuế/sau thuế |
| `exchange_rate` | decimal(20,6) | |
| `domestic_currency` / `domestic_total_*` | varchar / double | VND equivalents |

### 4.2 `of1_fms_house_bill_invoice_item`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `invoice_id` | bigint | FK |
| `charge_code` / `charge_name` | varchar | |
| `quantity` / `unit` / `unit_price` | double / varchar / double | |
| `total` / `total_tax` / `final_charge` | double | |
| `currency` / `exchange_rate` | varchar / decimal | |
| `domestic_currency` / `domestic_total` / `domestic_total_tax` / `domestic_final_charge` | varchar / double | |
| `payer_partner_id` / `payer_label` | bigint / varchar | |
| `payee_partner_id` / `payee_label` | bigint / varchar | |
| `reference_code` | varchar | |

### 4.3 `of1_fms_hawb_rates`

Tất cả phí/cước mua bán trên từng house bill. Cùng structure với `house_bill_invoice_item` + `rate_type` (`Debit` / `Credit` / `On_Behalf`).

Xem [[bf1-fms-mapping-house-bill]] cho field mapping chi tiết từ `dbo.SellingRate` / `BuyingRateWithHBL` / `OtherChargeDetail`.

### 4.4 `of1_fms_document_history`

Lưu snapshot dữ liệu tại thời điểm phát hành chứng từ (Authorize Letter, Delivery Order, ...). Mỗi lần in/phát hành tạo một record với PDF lưu trên S3/MinIO (`storage_bucket`, `storage_key`).

Fields chính (snapshot): `document_type` (`AUTHORIZE_LETTER` / `DELIVERY_ORDER`), `document_no`, `issued_time`, `issued_at`, `issued_by_*`, company info (name/address/website/email/tel/fax) bilingual, consignee/shipper/notify party, transport info, master/house bill nos, invoice items JSON, bank info, payment notice.

---

## 5. Order & Booking Domain

### 5.1 Purchase Order Model

Sau khi thảo luận với stakeholders, mô hình PO được áp dụng:

1. Tất cả yêu cầu của khách hàng là một Purchase Order (PO)
2. 1 PO có 1 hoặc nhiều booking (giải quyết khi KH cần giao trước một số lô)
3. Mỗi nghiệp vụ xử lý yêu cầu là 1 Purchase Order Process (POP), hoạt động độc lập, có mã riêng, lưu hoá đơn/chứng từ riêng

**Ví dụ:** KH có 5 kiện hàng, door-to-door, 2 kiện đầu tháng + 2 kiện giữa tháng. Cần 3 nghiệp vụ: gom hàng/trucking, ship biển, khai quan. Mô hình: **1 PO với 2 bookings**; **4 POP per vận chuyển** × 2 lần = **8 POP**. Mô hình master/house bill cũ chỉ tương ứng 1 POP của 1 PO.

### 5.2 `of1_fms_purchase_order`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar | UNIQUE |
| `order_date` | timestamp | |
| `label` | varchar | |
| `client_partner_id` / `client_label` | bigint / varchar | |
| `assignee_account_id` / `assignee_label` | bigint / varchar | |

### 5.3 `of1_fms_booking_process`

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar | UNIQUE |
| `type_of_service` | enum TypeOfService | |
| `purchase_order_id` | bigint | FK |
| `state` | varchar | `draft` / `confirmed` / ... |
| `close_date` | timestamp | |

---

## 6. Enums

### TypeOfService

| Code | Label |
|---|---|
| `AIR_EXPORT` | Air Export |
| `AIR_IMPORT` | Air Import |
| `SEA_EXPORT_FCL` | Sea Export FCL |
| `SEA_EXPORT_LCL` | Sea Export LCL |
| `SEA_IMPORT_FCL` | Sea Import FCL |
| `SEA_IMPORT_LCL` | Sea Import LCL |
| `CUSTOMS_LOGISTICS` | Customs & Logistics |
| `INLAND_TRUCKING` | Inland Trucking |
| `CROSS_BORDER` | Cross Border Logistics |
| `ROUND_USE_TRUCKING` | Round Use Trucking |
| `WAREHOUSE` | Warehouse Service |

### ShipmentType
`FREEHAND`, `NOMINATED`

### Incoterms

| Code | Label | Service Scope |
|---|---|---|
| `EXW` | Ex Works | `DOOR_TO_DOOR` |
| `FCA` | Free Carrier | `DOOR_TO_DOOR` |
| `FAS` | Free Alongside Ship | `PORT_TO_PORT` |
| `FOB` | Free On Board | `PORT_TO_PORT` |
| `CFR` | Cost and Freight | `PORT_TO_PORT` |
| `CIF` | Cost, Insurance and Freight | `PORT_TO_PORT` |
| `CPT` | Carriage Paid To | `DOOR_TO_PORT` |
| `CIP` | Carriage and Insurance Paid To | `DOOR_TO_PORT` |
| `DAP` | Delivered At Place | `DOOR_TO_DOOR` |
| `DDU` | Delivered at Place Unloaded | `DOOR_TO_DOOR` |
| `DDP` | Delivered Duty Paid | `DOOR_TO_DOOR` |

### InvoiceType
`DEBIT`, `CREDIT`

### DocumentType
`AUTHORIZE_LETTER`, `DELIVERY_ORDER`

### StorageState (common)
`CREATED`, `ACTIVE`, `INACTIVE`, `JUNK`, `DEPRECATED`, `ARCHIVED`

---

## 7. Master Data

### 7.1 Geographic & Currency

- **`of1_fms_settings_country`** — ISO alpha-2/3, label, localized_label, phone_code, currency_code, address_format
- **`of1_fms_settings_currency`** — ISO 4217 code, label, symbol, decimal_places, rounding
- **`of1_fms_settings_currency_exchange_rate`** — currency_id, base_currency_id, rate (decimal 20,6), valid_from/to, source
- **`of1_fms_settings_location_state`** — tỉnh/bang, gov_code, country_id
- **`of1_fms_settings_location_district`** — huyện/quận, state_id
- **`of1_fms_settings_location_subdistrict`** — phường/xã, district_id, postal_code
- **`of1_fms_settings_location`** — Airport / Port / KCN / State / District / Address; iata_code, un_locode, lat/lon

### 7.2 Units & Commodities

- **`of1_fms_settings_unit_group`** — weight, volume, quantity, ...
- **`of1_fms_settings_unit`** — ISO code, label, group_id, scale
- **`of1_fms_settings_commodity`** — code, label, hs_code, is_dangerous

### 7.3 Financial Masters

- **`of1_fms_settings_bank`** — code, swift_code, label, country_id
- **`of1_fms_settings_charge_type`** — code, label, charge_group (`Origin`/`Freight`/`Destination`/`Other`), type (`SELLING`/`BUYING`)

### 7.4 CRM & Partner Masters

- **`of1_fms_settings_industry`** — code, label
- **`of1_fms_custom_list`** — chi cục hải quan: code, label, province, team_code, team_name
- **`of1_fms_partner`** — customer/vendor/agent/carrier/notify party; identity (partner_code, category, group, scope), bilingual label/address, contact (email, cell, work_phone), finance (tax_code, swift, bank), industry/KCN, approval workflow
- **`of1_fms_user_role`** — account_id, bfsone_code, bfsone_username, full_name, email, phone, position, department, company_branch

---

## 8. Audit Fields (common)

All entities support:

| Field | Type | Description |
|---|---|---|
| `company_id` | bigint | Multi-tenant owner |
| `created_by` / `created_time` | varchar / timestamp | Creation audit |
| `modified_by` / `modified_time` | varchar / timestamp | Modification audit |
| `version` | int | Optimistic locking |
| `storage_state` | varchar | See StorageState enum §6 |

---

## 9. Legacy BF1 Schema — Core Tables

Core tables in legacy MSSQL `BEE_DB` that power CDC/Batch Sync pipelines.

### 9.1 Core Transaction
- **`Transactions`** — Master lô hàng. PK `TransID`. 681K rows / 1,476 MB.
- **`TransactionDetails`** — Chi tiết lô. PK `IDKeyShipment`, FK `TransID`, `HWBNO`, `ShipperID`, `CustomsID`. 831K rows / 1,982 MB.

### 9.2 House Bill & Cargo
- **`HAWB`** — Vận đơn nhà. PK `HWBNO`, FK `TRANSID`. 866K rows / 2,773 MB.
- **`HAWBDETAILS`** — Chi tiết hàng hóa. FK `HWBNO`. 369K rows / 451 MB.
- **`ContainerListOnHBL`** — Container gắn HBL. FK `HBLNo`. 141K rows / 67 MB.

### 9.3 Rates & Financial
- **`SellingRate`** — Giá bán. FK `HAWBNO`. 1.94M rows / 3,537 MB.
- **`BuyingRateWithHBL`** — Giá mua. FK `HAWBNO`, `VendorID`. 433K rows / 921 MB.
- **`OtherChargeDetail`** — Phí khác. FK `HBL`. 246K rows / 151 MB.
- **`RateHistory`** — Audit log. FK `HWBNO`. 6.45M rows / 4,863 MB.

### 9.4 Debit Notes & Payment
- **`DebitNotes`** — Phiếu công nợ. PK `dbtID`. 309K rows / 316 MB.
- **`DebitNoteDetails`** — Chi tiết. PK `IDKeyIndex`, FK `dbtID`, `HWBNO`. 4.14M rows / 7,487 MB.
- **`DebitNoteDetails_Payment`** — Thanh toán. FK `dbtDID`. 3.82M rows / 1,303 MB.

### 9.5 Profit & Revenue
- **`ProfitShares`** — Chia lợi nhuận. FK `HAWBNO`. 3.17M rows / 5,565 MB.
- **`RevenueDetails_Sheet`** — Chi tiết doanh thu. 4.60M rows / 2,105 MB.

### 9.6 Operations & Tracking
- **`Booking`** — Booking nội địa. 41K rows / 97 MB.
- **`SeaBookingNote`** — Booking sea. 38K rows / 282 MB.
- **`HAWBTracking`** — Tracking trạng thái. 96K rows / 66 MB.
- **`Trucking_Track`** — Tracking xe tải. 115K rows / 51 MB.

### 9.7 Customs
- **`CustomsDeclaration`** — Tờ khai hải quan. PK `MasoTK`. 790K rows / 559 MB.
- **`Customs_Bonded_Warehouse`** — Kho ngoại quan. 15K rows / 2 MB.

### 9.8 Master Data Equivalents

| BF1 Table | OF1 Equivalent |
|-----------|----------------|
| `Partners` | `of1_fms_partner` |
| `Countries` | `of1_fms_settings_country` |
| `Airports` | `of1_fms_settings_location` (type=Airport) |
| `CurrencyExchangeRate` | `of1_fms_settings_currency_exchange_rate` |
| `Commodity` | `of1_fms_settings_commodity` |
| `UnitContents` | `of1_fms_settings_unit` |
| `lst_Bank` | `of1_fms_settings_bank` |
| `lst_Industries` | `of1_fms_settings_industry` |
| `lst_Source` | `of1_fms_settings_partner_source` |
| `NameFeeDescription` | `of1_fms_settings_name_fee_desc` |
| `CustomsList` | `of1_fms_custom_list` |
| `UserInfos` | `of1_fms_user_role` |

Detailed mappings: see [[bf1-fms-mapping-readme]].

---

## 10. Data Integration Notes

### Legacy Bridges
- `Transactions.TransID` → `of1_fms_transactions.code`
- `HAWB.HWBNO` → `of1_fms_house_bill.hawb_no`
- `DebitNotes.dbtID` → `of1_fms_house_bill_invoice` (via CDC)
- `CustomsDeclaration.MasoTK` → `of1_fms_logistics_house_bill_detail.cds_no`

### Multi-Tenancy
- All entities include `company_id` for tenant isolation
- `CDCTenantContext` propagates tenant identity through Kafka topic → handler
- Partner sourcing via `partner_source` (e.g. `BEE_VN`)

### Localization
- All master data supports bilingual labels (label + localized_label)
- Address formatting per country
- Documents (Authorize Letter, DO) generated in VI + EN
