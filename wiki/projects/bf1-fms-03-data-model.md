---
title: "FMS 03 - Data Model"
tags: [bf1, fms]
---

# Data Model & Schema

Comprehensive data model covering entity relationships, master data structures, and database schema for OF1 FMS.

See also: [[bf1-fms-02-features]] · [[bf1-fms-mapping]] for source→target field mappings.

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
| `container_vol` | varchar |  | `ContainerSize` text — parse sinh ra Container (xem [[bf1-fms-mapping#mapping--container]]) |

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

Two CDC sources: (1) `TransactionsCDCHandler` parses `ContainerSize` text (`"2x40HC & 1x20"`) to create type+quantity records; (2) `ContainerListOnHBLCDCHandler` creates line-item records from `dbo.ContainerListOnHBL` with container_no + seal_no. Xem [[bf1-fms-mapping#mapping--container]].

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

Auto-upsert từ `HAWBCDCHandler` sử dụng GW/CBM/Pieces từ `dbo.HAWB`. Xem [[bf1-fms-mapping#mapping--cargo]].

### 3.3 `of1_fms_transport_plan` & `of1_fms_transport_route`

**Transport Plan** (header): `house_bill_id`, `from_location_*`, `to_location_*`, `depart_time`, `arrival_time`, `transport_name`, `flight_date_confirm`.

**Transport Route** (legs): `transport_plan_id`, `from_location_*`, `to_location_*`, `depart_time`, `arrival_time`, `transport_no`, `carrier_label`, `sort_order`.

Rebuilt mỗi lần Transaction CDC event đến (delete + recreate). Xem [[bf1-fms-mapping#mapping--transport-plan--route]].

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

Xem [[bf1-fms-mapping#mapping--house-bill]] cho field mapping chi tiết từ `dbo.SellingRate` / `BuyingRateWithHBL` / `OtherChargeDetail`.

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

## 9. BEE_DB Schema Survey

# BEE_DB — Khảo sát Schema & Cấu trúc Bảng

## Tổng quan

- **461 bảng** tổng cộng (~200 bảng có data thực tế)
- Bảng lớn nhất: `EInvoice_History` (11.7 GB), `DebitNoteDetails` (7.5 GB), `ProfitShares` (5.6 GB)

---

## Phân nhóm bảng

### Nhóm 1 — Partner / Khách hàng (Master)

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Partners` | 52,414 | 82 | Master đối tác/khách hàng (PK: `PartnerID` nvarchar) |
| `PartnerContact` | 25,009 | 22 | Người liên hệ của partner |
| `Partner_BankInfo` | 14,449 | 2.6 | Thông tin ngân hàng cá nhân |
| `Partner_BankInfo_Comp` | 8 | 0.07 | Thông tin ngân hàng theo công ty |
| `Partner_Bank_Default` | 12 | 0.07 | Ngân hàng mặc định |
| `Partner_Bank_Request` | 1,749 | 0.95 | Yêu cầu đổi ngân hàng |
| `Partner_History` | 16,485,161 | 3,561 | Lịch sử thay đổi partner |
| `Partner_Payment_Bank` | 866,196 | 722 | Thanh toán qua ngân hàng |
| `Partner_Payment_Plan` | 24,023 | 22 | Kế hoạch thanh toán |
| `Partner_Warning` | 61,832 | 120 | Cảnh báo đối tác |
| `Partner_Warining_Details` | 6,872,900 | 1,870 | Chi tiết cảnh báo |
| `Partner_Notes` | 956 | 14 | Ghi chú đối tác |
| `Partner_More_Revenue` | 1,295 | 0.2 | Doanh thu bổ sung |
| `Partner_Source` | 31 | 0.07 | Nguồn đối tác |
| `Partner_Transaction_Allow` | 15,060 | 3.6 | Phân quyền giao dịch |
| `Partner_Tariff` | 46 | 0.14 | Tariff riêng theo partner |
| `Partner_Tariff_SellingRate` | 46 | 0.14 | Giá bán theo tariff |
| `Partner_Tariff_BuyingRate` | 46 | 0.02 | Giá mua theo tariff |
| `Partner_Tariff_ProfitShares` | 45 | 0.14 | Chia lợi nhuận theo tariff |
| `PartnerIDMaker` | 7 | 0.14 | Tạo mã đối tác |
| `PartnerTransactions` | 10 | 0.07 | Giao dịch đối tác |

**FK từ Partners ra ngoài:** `Partners.PartnerID` được tham chiếu bởi:
`DebitNotes`, `DebitNoteDetails_Other`, `TransactionDetails` (ShipperID), `InvoiceReference` (ShipperID), `BookingRateRequest`, `HandleInstructions`, `HandleServiceRate`, `PODetail` (VendorCode), `ProfitShares`, `Partner_BankInfo`, `Partner_BankInfo_Comp`

---

### Nhóm 2 — Transactions / Lô hàng

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Transactions` | 681,038 | 1,476 | Master lô hàng (PK: `TransID` dạng `BIHCM008238/25`) |
| `TransactionDetails` | 831,608 | 1,982 | Chi tiết lô hàng (FK: `TransID`, `HWBNO`, `ShipperID`) |
| `TransactionInfo` | 508,008 | 292 | Thông tin bổ sung per shipment |
| `TransactionInfoDetail` | 0 | — | Chưa dùng |
| `TransactionsChange` | 1,411,298 | 353 | Lịch sử thay đổi lô hàng |
| `TransactionsChangeHis` | 63 | 0.07 | Lưu trữ lịch sử thay đổi |
| `Transaction_Notes` | 45,824 | 10 | Ghi chú lô hàng |
| `Transaction_Ops` | 22,810 | 4.9 | Thao tác vận hành |
| `Transaction_Task` | 399,773 | 140 | Task gắn với lô hàng |
| `Transaction_Task_Group` | 41 | 0.07 | Nhóm task |
| `Transaction_Service_Task` | 178 | 0.15 | Task dịch vụ |
| `TransactionType` | 17 | 0.21 | Loại giao dịch |
| `TransactionTypeDetail` | 92 | 0.21 | Chi tiết loại |
| `TransactionReminder` | 8 | 0.07 | Nhắc nhở |
| `TransactionLead` | 86 | 0.13 | Lead giao dịch |

**FK từ Transactions:** `Transactions.TransID` → `AdvanceSettlementPayment`, `BookingLocal`, `BuyingRate`, `BuyingRateFixCost`, `BuyingRateOthers`, `ConsolidationRate`, `ContainerLoaded`, `InvoiceReference`, `OPSManagement`, `ProfitShareCalc`, `ShippingInstruction`, `TransactionDetails`

---

### Nhóm 3 — HAWB / House Bill of Lading

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `HAWB` | 866,657 | 2,773 | House Bill (PK: `HWBNO`; ref: `TRANSID`, `AWBNO`) |
| `HAWBDETAILS` | 369,773 | 451 | Chi tiết hàng hóa trên HBL |
| `HAWBRATE` | 87,694 | 18 | Giá theo vận đơn |
| `HAWBTracking` | 96,599 | 66 | Tracking trạng thái vận chuyển |
| `HAWBSEPDetails` | 0 | — | Tách lô |
| `HAWBTranshipment` | 0 | — | Transshipment |
| `HAWB_Air_Tracking` | 41 | 0.07 | Tracking hàng không |
| `HAWB_DELETE` | 755,954 | 30 | Vận đơn đã xóa (audit) |
| `HAWB_FMC` | 6 | 0.07 | FMC info |
| `HAWB_Partner_Address` | 5,191 | 4.8 | Địa chỉ đối tác trên HBL |
| `ContainerListOnHBL` | 141,216 | 67 | Container gắn với HBL |
| `ContainerLoadedHBL` | 75,514 | 31 | Container đã load lên HBL |

**FK từ HAWB.HWBNO →** (20+ bảng): `SellingRate`, `BuyingRateWithHBL`, `ProfitShares`, `ProfitSharesCost`, `RevenueDetails_Sheet`, `TransactionDetails`, `TransactionInfo`, `OtherChargeDetail`, `ContainerListOnHBL`, `ContainerLoadedHBL`, `HAWBTracking`, `HAWBDETAILS`, `HAWBRATE`, `BookingLocal`, `AdvanceSettlementPayment`, `CargoOperationRequest`, `AMSDeclaration`, `AcsInstallPayment`, ...

---

### Nhóm 4 — Rates / Bảng giá

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `SellingRate` | 1,942,592 | 3,537 | Giá bán (theo HAWBNO) |
| `SellingRate_Temp` | 822 | 0.38 | Tạm thời |
| `SellingRate_Partner_Disable` | 235 | 0.2 | Bị tắt theo partner |
| `SellingRate_Saleman_Disable` | 1 | 0.07 | Bị tắt theo saleman |
| `BuyingRateWithHBL` | 433,281 | 921 | Giá mua (theo HAWBNO) |
| `BuyingRate` | 5,177 | 8.2 | Giá mua (theo TransID) |
| `BuyingRateOthers` | 4,133 | 7.2 | Phí mua khác |
| `BuyingRateInland` | 2 | 0.37 | Giá nội địa |
| `BuyingRateFixCost` | 0 | — | Chi phí cố định |
| `RateHistory` | 6,448,501 | 4,863 | Lịch sử tất cả rates |
| `ArrivalFreightCharges` | 1,158,503 | 288 | Phí arrival |
| `ArrivalFreightChargesDefault` | 47 | 0.08 | Mặc định phí arrival |
| `SeaFreightPricing` | 55,590 | 102 | Bảng giá sea FCL export |
| `SeaFreightPricing_Exp` | 8,076 | 3.4 | Bảng giá sea FCL express |
| `SeaFreightPricingLCL` | 800 | 0.45 | Bảng giá sea LCL |
| `SeaFreightPricingLCL_Exp` | 1,892 | 1.5 | Bảng giá sea LCL express |
| `Seafclpricingimpstd` | 13,508 | 5.6 | FCL import std |
| `Sealclpricingimpstd` | 602 | 0.55 | LCL import std |
| `Sealclpricingexpstd` | 1,020 | 0.72 | LCL export std |
| `AirfreightPrcing` | 3,191 | 2.5 | Bảng giá air |
| `AirFreightPricing_Exp` | 1,454 | 0.86 | Bảng giá air express |
| `AirfreightPrcingDetail` | 0 | — | Chi tiết giá air |
| `Airpricingstd` | 350 | 0.27 | Air pricing std |
| `AirPortPerKGSChargeable` | 2 | 0.07 | Air per KG |
| `TruckingFCLPricing` | 742 | 0.34 | Giá trucking FCL |
| `TruckingLCLPricing` | 1,688 | 0.70 | Giá trucking LCL |
| `ATruckingFee` | 2,306 | 1.0 | Phí trucking |
| `HandleServiceRate` | 45 | 0.65 | Giá dịch vụ xử lý |
| `ConsolidationRate` | 0 | — | Giá consolidation |
| `OtherChargeList` | 26,123 | 30 | Danh mục phí khác |
| `OtherChargeDetail` | 246,546 | 151 | Chi tiết phí khác |
| `NameFeeDescription` | 1,130 | 0.94 | Mô tả tên phí |

---

### Nhóm 5 — Debit Notes / Công nợ

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `DebitNotes` | 309,724 | 316 | Phiếu công nợ (PK: `dbtID`) |
| `DebitNoteDetails` | 4,141,341 | 7,487 | Chi tiết công nợ (FK: `dbtID`) |
| `DebitNoteDetails_Payment` | 3,820,487 | 1,303 | Thanh toán chi tiết (FK: `dbtDID`) |
| `DebitNotes_Payment` | 318,685 | 54 | Thanh toán tổng (FK: `dbtID`) |
| `DebitNotes_Other` | 27 | 0.64 | Công nợ khác |
| `DebitNoteDetails_Other` | 4 | 0.29 | Chi tiết công nợ khác |
| `DebitNote_Payment_Bank` | 0 | — | Thanh toán qua ngân hàng |
| `DebitMemory` | 0 | — | Bộ nhớ debit |

**FK chain:** `DebitNotes.dbtID` → `DebitNoteDetails.dbtID` → `DebitNoteDetails_Payment.dbtDID`

---

### Nhóm 6 — VAT Invoice / Hóa đơn

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `VATInvoice` | 465,478 | 1,409 | Hóa đơn VAT (PK: `ID`+`InvoiceNo`) |
| `VATInvoiceDetail` | 2,289,816 | 1,112 | Chi tiết hóa đơn (FK: `ID`, `InvoiceNo`) |
| `VATINvoice_2019` | 167,012 | 488 | Archive 2019 |
| `VATInvoiceDetail_2019` | 791,413 | 235 | Chi tiết archive 2019 |
| `VATInvoice_Costing_Ref` | 1,947,737 | 830 | Tham chiếu costing |
| `VATInvoice_Costing_Import_Info` | 1,006,608 | 420 | Thông tin import costing |
| `VATInvoice_Editing_Info` | 423 | 0.62 | Lịch sử chỉnh sửa |
| `VATInvoice_Transactions` | 51 | 0.26 | HĐ liên kết giao dịch |
| `VATInvoice_Temp` | 0 | — | Tạm thời |
| `VATInvSOA` | 1 | 0.07 | SOA |
| `VATInvoiceLog` | 0 | — | Log |
| `EInvoice_History` | 941,165 | 11,756 | Lịch sử hóa đơn điện tử |
| `EInvoice_Register` | 49 | 1.05 | Đăng ký phát hành hóa đơn điện tử |
| `EInvoice_Register_Detail` | 122 | 0.07 | Chi tiết đăng ký |
| `InvoiceForm` | 64 | 0.30 | Mẫu hóa đơn |
| `InvoiceFormReserve` | 722 | 0.44 | Dự trữ số hóa đơn |
| `InvoiceDocument` | 2,435 | 923 | File đính kèm hóa đơn (lớn) |

**FK:** `VATInvoice.ID` → `VATInvoiceDetail.ID` và `VATInvoice.InvoiceNo` → `VATInvoiceDetail.InvoiceNo`

---

### Nhóm 7 — Invoice Reference / SOA

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `InvoiceReference` | 137,154 | 151 | Tham chiếu HĐ ↔ lô hàng (FK: `TransID`, `ShipperID`) |
| `InvoiceReferenceDetail` | 137,286 | 41 | Chi tiết (FK: `InvoiceNo`) |
| `InvoiceRefGrouping` | 28 | 0.16 | Nhóm tham chiếu |
| `InvoiceSOA` | 11,625 | 10 | Statement of Account (PK: `SOANO`) |
| `InvoiceBankInfo` | 9 | 0.14 | Thông tin ngân hàng trên HĐ |

**FK:** `InvoiceSOA.SOANO` → `InvoiceReference.SOANO`

---

### Nhóm 8 — Profit & Revenue

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `ProfitShares` | 3,167,966 | 5,565 | Chia lợi nhuận (theo HAWBNO + PartnerID) |
| `ProfitShareCalc` | 2 | 0.07 | Tính toán lợi nhuận |
| `ProfitShareCalcDetail` | 95 | 0.2 | Chi tiết tính toán |
| `ProfitSharesCost` | 0 | — | Chi phí chia lợi nhuận |
| `ProfitSharesRef_In_Local_Office` | 22 | 0.2 | Tham chiếu văn phòng nội bộ |
| `Revenue_Sheet` | 5,781 | 6.3 | Tổng hợp doanh thu (PK: `DocID`) |
| `RevenueDetails_Sheet` | 4,596,253 | 2,105 | Chi tiết doanh thu (FK: `DocRefID`) |

**FK:** `Revenue_Sheet.DocID` → `RevenueDetails_Sheet.DocRefID`

---

### Nhóm 9 — Kế toán (PhieuThuChi & Advance)

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `PhieuThuChi` | 120,491 | 224 | Phiếu thu/chi (PK: `Maso`) |
| `PhieuThuChiDetails` | 592,650 | 395 | Chi tiết (FK: `SoCT`) |
| `PhieuThuChiDetail` | 25,701 | 7.7 | Chi tiết phụ |
| `PhieuThuChiTaxReport` | 9 | 0.07 | Báo cáo thuế |
| `PhieuThuChiPL` | 14 | 0.09 | P&L |
| `AdvanceSettlementPayment` | 1,040,101 | 439 | Thanh toán tạm ứng |
| `AdvanceSettlementPayment_Office_OBH` | 40,960 | 71 | Tạm ứng văn phòng OBH |
| `AdvanceSettlementPayment_Deleted` | 6,602 | 7.3 | Đã xóa |
| `AdvancePaymentRequest` | 10,035 | 41 | Yêu cầu tạm ứng |
| `AdvancePaymentRequestDetails` | 3,376 | 1.05 | Chi tiết yêu cầu |
| `AdvanceRequest` | 63 | 0.44 | Yêu cầu ứng tiền |
| `AcsSetlementPayment` | 83,589 | 230 | Quyết toán kế toán |

**FK:** `PhieuThuChi.Maso` → `PhieuThuChiDetails.SoCT`, `PhieuThuChiDetail.MasoPhieu`, `PhieuThuChiTaxReport.RefNo`

---

### Nhóm 10 — Quotation / Báo giá

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `QUOTATIONS` | 17,803 | 46 | Báo giá air |
| `QUOTATIONDETAILS` | 24,533 | 20 | Chi tiết báo giá air |
| `QUOTATIONDETAILSOTS` | 335 | 0.2 | Chi tiết OTS |
| `QuotationFreightDetail` | 20,660 | 7.2 | Chi tiết freight |
| `SeaQuotations` | 47,878 | 169 | Báo giá sea |
| `SeaQuotationDetails` | 200,075 | 78 | Chi tiết báo giá sea |
| `SeaQuotationCtnrs` | 60,675 | 20 | Container trong báo giá |
| `SeaQuotationOthers` | 2,181 | 1.3 | Phí khác trong báo giá |
| `QuoSentHistory` | 92,924 | 20 | Lịch sử gửi báo giá |
| `BookingRateRequest` | 151,646 | 90 | Yêu cầu báo giá (FK: `BkgID`, `PartnerID`) |
| `Quotation_Combine` | 124 | 0.52 | Báo giá tổng hợp |
| `Quotation_Combine_Air` | 10 | 0.07 | Air |
| `Quotation_Combine_Sea` | 126 | 0.2 | Sea |
| `Quotation_Combine_Truck_FCL` | 9 | 0.07 | Truck FCL |
| `Quotation_Combine_Truck_LCL` | 4 | 0.07 | Truck LCL |
| `Quotation_Combine_Air_Charges` | 16 | 0.07 | Phí air trong combined |
| `Quotation_Combine_Sea_Charge` | 206 | 0.2 | Phí sea trong combined |
| `Quotation_Setting` | 18 | 0.14 | Cấu hình báo giá |

---

### Nhóm 11 — Booking

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `BookingLocal` | 41,481 | 97 | Booking nội địa (FK: `BkgID`, `ConfirmHBL`, `ConformJobNo`) |
| `BookingContainer` | 36,291 | 10 | Container trong booking |
| `BookingConfirmList` | 11,721 | 49 | Danh sách xác nhận |
| `SeaBookingNote` | 38,286 | 282 | Booking sea (FK: `BookingID` → `TransactionDetails`) |
| `SeaBookingContainer` | 33 | 0.14 | Container sea |
| `ShippingInstruction` | 235,879 | 118 | Hướng dẫn vận chuyển (FK: `TransID`) |

---

### Nhóm 12 — Warehouse / Kho

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Warehouse` | 88,947 | 68 | Kho hàng |
| `WarehouseDetail` | 183,114 | 59 | Chi tiết kho |
| `Warehouse_Payment` | 84,913 | 74 | Thanh toán kho |
| `Warehouse_Assign_Group` | 125 | 0.07 | Phân nhóm kho |

---

### Nhóm 13 — Hải quan / Customs

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `CustomsDeclaration` | 790,556 | 559 | Tờ khai hải quan (PK: `MasoTK`) |
| `CustomsDeclarationDetail` | 1 | 0.16 | Chi tiết tờ khai |
| `CustomsAssignedList` | 2,039 | 1.05 | Phân công hải quan |
| `CustomsArisingList` | 272 | 0.14 | Danh sách phát sinh |
| `CustomsArising_Assign_Group` | 274 | 0.07 | Phân nhóm phát sinh |
| `CustomsList` | 264 | 0.13 | Danh mục hải quan |
| `Customs_Bonded_Warehouse` | 15,927 | 2.1 | Kho ngoại quan |
| `Customs_Clearance_Tariff` | 2,281 | 1.06 | Biểu thuế thông quan |
| `EcusCuakhau` | 282 | 0.2 | Cửa khẩu ECUS |
| `ECusCucHQ` | 53 | 0.07 | Cục hải quan ECUS |

**FK:** `CustomsDeclaration.MasoTK` → `TransactionDetails.CustomsID`

---

### Nhóm 14 — Trucking

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Trucking_Track` | 114,938 | 51 | Tracking xe tải |
| `Trucking_Pricing_Localnote` | 6 | 0.14 | Ghi chú giá trucking |

---

### Nhóm 15 — Người dùng / Phân quyền

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `UserInfos` | 1,091 | 1.2 | Thông tin user (login) |
| `ActiveUsers` | 4,693,571 | 2,678 | Lịch sử đăng nhập |
| `AccessRight` | 2 | 0.28 | Quyền truy cập |
| `AccessRightCTRL` | 462 | 0.2 | Kiểm soát quyền |
| `AccessRightLevel` | 10 | 0.02 | Cấp độ quyền |
| `GroupList` | 17 | 0.07 | Danh sách nhóm |
| `Departments` | 108 | 0.48 | Phòng ban |
| `Dept_Manage` | 675 | 0.07 | Quản lý phòng ban |
| `Department_Group_Setup` | 98 | 0.07 | Cấu hình nhóm phòng ban |
| `Department_Report_Setup` | 773 | 0.21 | Cấu hình báo cáo |
| `Department_ViewReports` | 9,852 | 2.98 | Phân quyền xem báo cáo |
| `PersonalProfile` | 21 | 0.50 | Hồ sơ cá nhân |

---

### Nhóm 16 — Master data / Danh mục

| Bảng | Rows | Mô tả |
|---|---|---|
| `Countries` / `lst_Countries` / `lst_Country` | ~250 | Danh sách quốc gia |
| `lst_Cities` | 1,115 | Thành phố |
| `lst_States` | 17 | Tỉnh/bang |
| `lst_Regions` | 23 | Vùng |
| `lst_Continents` | 6 | Châu lục |
| `lst_Bank` | 203 | Ngân hàng |
| `Airports` / `Airport_AIR` | 15K / 1K | Sân bay |
| `VesselCode` | 26,376 | Mã tàu |
| `VesselSchedules` | 0 | Lịch tàu |
| `CurrencyExchangeRate` | 5,174 | Tỷ giá ngoại tệ |
| `ExchangeRate` | 19 | Tỷ giá cơ bản |
| `Commodity` | 96 | Hàng hóa |
| `UnitContents` | 145 | Đơn vị |
| `lst_Zone` / `lst_Zone_Local` | 15 / 27 | Khu vực |
| `lst_Service` | 13 | Dịch vụ |
| `lst_Industries` | 23 | Ngành nghề |
| `lst_Mode` | 8 | Phương thức vận chuyển |
| `lst_SaleType` | 10 | Loại kinh doanh |
| `lst_Source` | 30 | Nguồn |
| `TransactionType` | 17 | Loại giao dịch |

---

## Sơ đồ quan hệ chính

```
Partners (PartnerID)
  ├──► DebitNotes (PartnerID)
  │       └──► DebitNoteDetails (dbtID)
  │               └──► DebitNoteDetails_Payment (dbtDID)
  │       └──► DebitNotes_Payment (dbtID)
  │
  ├──► InvoiceReference (ShipperID)
  │       └──► InvoiceReferenceDetail (InvoiceNo)
  │
  ├──► TransactionDetails (ShipperID)
  │
  ├──► ProfitShares (PartnerID)
  └──► HandleInstructions (PartnerID)

Transactions (TransID)
  ├──► TransactionDetails (TransID)
  │       ├── FK: HWBNO → HAWB
  │       ├── FK: ShipperID → Partners
  │       └── FK: CustomsID → CustomsDeclaration
  │
  ├──► InvoiceReference (TransID)
  ├──► BuyingRate (TransID)
  ├──► ContainerLoaded (TransID)
  └──► ShippingInstruction (TransID)

HAWB (HWBNO)                             ← FK từ TransactionDetails.HWBNO
  ├──► SellingRate (HAWBNO)
  ├──► BuyingRateWithHBL (HAWBNO)
  ├──► ProfitShares (HAWBNO)
  ├──► RevenueDetails_Sheet (HWBNO)
  ├──► HAWBTracking (HWBNO)
  ├──► HAWBDETAILS (HWBNO)
  ├──► HAWBRATE (HWBNO)
  ├──► OtherChargeDetail (HBL)
  ├──► ContainerListOnHBL (HBLNo)
  ├──► ContainerLoadedHBL (HBLNo)
  ├──► TransactionInfo (HAWBNO)
  ├──► AdvanceSettlementPayment (HBL)
  └──► BookingLocal (ConfirmHBL)

VATInvoice (ID, InvoiceNo)
  └──► VATInvoiceDetail (ID, InvoiceNo)

InvoiceSOA (SOANO)
  └──► InvoiceReference (SOANO)

Revenue_Sheet (DocID)
  └──► RevenueDetails_Sheet (DocRefID)

PhieuThuChi (Maso)
  ├──► PhieuThuChiDetails (SoCT)
  └──► PhieuThuChiDetail (MasoPhieu)

DebitNotes (dbtID)
  ├──► DebitNoteDetails (dbtID)
  │       └──► DebitNoteDetails_Payment (dbtDID)
  └──► DebitNotes_Payment (dbtID)

Quotation_Combine (QuoID)
  ├──► Quotation_Combine_Air (QuoNo)
  │       └──► Quotation_Combine_Air_Charges (QuoDetailID)
  ├──► Quotation_Combine_Sea (QuoNo)
  │       └──► Quotation_Combine_Sea_Charge (QuoDetailID)
  ├──► Quotation_Combine_Truck_FCL (QuoNo)
  └──► Quotation_Combine_Truck_LCL (QuoNo)
```

---

## SQL Queries mẫu

### 1. Partner + thông tin ngân hàng
```sql
SELECT
  p.PartnerID, p.PartnerName, p.PartnerName3,
  p.Category, p.[Group], p.Taxcode, p.Country, p.PaymentTerm, p.Industry,
  b.BankName, b.BankAccNo
FROM Partners p
LEFT JOIN Partner_BankInfo b ON p.PartnerID = b.PartnerID
WHERE p.[Group] = 'CUSTOMERS' AND p.Status = 0
ORDER BY p.PartnerName;
```

### 2. Lô hàng gần đây + chi tiết vận đơn
```sql
SELECT
  t.TransID, t.TransDate, t.TpyeofService,
  td.IDKeyShipment, td.HWBNO, td.ShipperID,
  p.PartnerName, td.ETD, td.ETA, td.ShipmentType
FROM Transactions t
JOIN TransactionDetails td ON t.TransID = td.TransID
LEFT JOIN Partners p ON td.ShipperID = p.PartnerID
WHERE t.TransDate >= DATEADD(day, -30, GETDATE())
ORDER BY t.TransDate DESC;
```

### 3. Công nợ chưa thanh toán theo partner
```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.PartnerID, p.PartnerName,
  dn.TotalAmount, dn.isApproved, dn.Paid,
  dn.Fromdate, dn.ToDate
FROM DebitNotes dn
JOIN Partners p ON dn.PartnerID = p.PartnerID
WHERE dn.Paid = 0 AND dn.isApproved = 1
ORDER BY dn.TotalAmount DESC;
```

### 4. Hóa đơn VAT tháng hiện tại
```sql
SELECT
  v.InvoiceNo, v.InvoiceDate, v.CustomerID, v.CompanyName,
  v.Currency, v.VATTotal, v.ExRate,
  vd.Description, vd.Quantity, vd.UnitPrice, vd.Amount
FROM VATInvoice v
JOIN VATInvoiceDetail vd ON v.ID = vd.ID AND v.InvoiceNo = vd.InvoiceNo
WHERE v.InvoiceDate >= DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)
ORDER BY v.InvoiceDate DESC;
```

### 5. HAWB + Tổng giá bán / giá mua / lợi nhuận
```sql
SELECT
  h.HWBNO, h.AWBNO, h.TRANSID,
  ISNULL(sr.sell_total, 0) AS TotalSelling,
  ISNULL(br.buy_total, 0) AS TotalBuying,
  ISNULL(sr.sell_total, 0) - ISNULL(br.buy_total, 0) AS Profit
FROM HAWB h
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS sell_total
  FROM SellingRate GROUP BY HAWBNO
) sr ON h.HWBNO = sr.HAWBNO
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS buy_total
  FROM BuyingRateWithHBL GROUP BY HAWBNO
) br ON h.HWBNO = br.HAWBNO
WHERE h.TRANSID IS NOT NULL
ORDER BY h.ISSUED DESC;
```

### 6. ProfitShares theo HAWB
```sql
SELECT
  ps.HAWBNO, ps.PartnerID, p.PartnerName,
  ps.GroupName, ps.FieldName,
  ps.Quantity, ps.UnitPrice, ps.Amount, ps.TotalValue
FROM ProfitShares ps
LEFT JOIN Partners p ON ps.PartnerID = p.PartnerID
WHERE ps.HAWBNO = 'YOUR_HAWBNO_HERE';
```

### 7. Debit Note chi tiết + thanh toán
```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.PartnerID, p.PartnerName, dn.TotalAmount,
  dnd.IDKeyIndex, dnd.TransID, dnd.HWBNO, dnd.PaidAmount,
  dnp.PaymentNo, dnp.PaidAmount AS PaymentAmt
FROM DebitNotes dn
JOIN Partners p ON dn.PartnerID = p.PartnerID
JOIN DebitNoteDetails dnd ON dn.dbtID = dnd.dbtID
LEFT JOIN DebitNoteDetails_Payment dnp ON dnd.IDKeyIndex = dnp.dbtDID
WHERE dn.dbtID = 'YOUR_DBTID_HERE';
```

### 8. Phiếu thu/chi trong kỳ
```sql
SELECT
  ptc.Maso, ptc.Ngay, ptc.MaLoaiPhieu,
  ptc.Nguoinoptien, ptc.Donvi,
  ptc.Sotien, ptc.LoaiTien, ptc.Tygia,
  ptc.Lydo
FROM PhieuThuChi ptc
WHERE ptc.Ngay >= '2026-01-01' AND ptc.Ngay < '2026-04-01'
ORDER BY ptc.Ngay DESC;
```

### 9. List bảng + row count + size (khảo sát)
```sql
SELECT
  t.name AS table_name,
  p.rows AS row_count,
  CAST(ROUND(SUM(a.total_pages) * 8.0 / 1024, 2) AS DECIMAL(18,2)) AS size_mb
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.is_ms_shipped = 0
GROUP BY t.name, p.rows
ORDER BY p.rows DESC;
```

### 10. Foreign key relationships
```sql
SELECT
  tp.name AS parent_table,
  cp.name AS parent_column,
  tr.name AS child_table,
  cr.name AS child_column,
  fk.name AS fk_name
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
JOIN sys.tables tp ON fkc.referenced_object_id = tp.object_id
JOIN sys.columns cp ON fkc.referenced_object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
JOIN sys.tables tr ON fkc.parent_object_id = tr.object_id
JOIN sys.columns cr ON fkc.parent_object_id = cr.object_id AND fkc.parent_column_id = cr.column_id
ORDER BY parent_table, child_table;
```

---

## Gợi ý Priority cho CDC Sync

| Priority | Bảng | Lý do |
|---|---|---|
| **P0** | `Partners`, `PartnerContact` | Master — cần trước để hiển thị UI |
| **P0** | `Departments`, `UserInfos` | Danh mục người dùng |
| **P0** | `Countries`, `Airports`, `VesselCode` | Reference data |
| **P0** | `CurrencyExchangeRate` | Tỷ giá |
| **P1** | `Transactions`, `TransactionDetails` | Nghiệp vụ chính, realtime |
| **P1** | `HAWB`, `HAWBDETAILS` | Vận đơn, realtime |
| **P1** | `DebitNotes`, `DebitNoteDetails` | Công nợ |
| **P1** | `VATInvoice`, `VATInvoiceDetail` | Hóa đơn |
| **P1** | `SellingRate`, `BuyingRateWithHBL` | Doanh thu/chi phí |
| **P1** | `ProfitShares` | Lợi nhuận |
| **P1** | `InvoiceReference` | Đối soát hóa đơn |
| **P1** | `PhieuThuChi`, `PhieuThuChiDetails` | Kế toán thu/chi |
| **P2** | `Partner_History`, `RateHistory` | Archive — batch import |
| **P2** | `*_DELETE`, `*_2019` | Archive/deleted data |
| **P2** | `EInvoice_History` | Lớn (11GB) — sync sau |
| **P2** | `ActiveUsers`, `TransactionsChange` | Log — ít cần thiết |

---

## Lưu ý

- `PartnerID` là `nvarchar(100)`, format: `CS000001` (customer), `AG000001` (agent), `CL000001` (client)
- `TransID` format: `BIHCM008238/25` (prefix office + số + năm)
- `HWBNO` format đa dạng theo loại hàng và văn phòng
- `dbtID` format: `BKHCM2603/03194` (debit note ID)
- Nhiều bảng có cột `OBH` (On Behalf) — dùng cho trường hợp đại lý làm thay
- Bảng `*_DELETE` là audit trail — lưu dữ liệu đã xóa, không cần sync realtime

Detailed mappings: see [[bf1-fms-mapping]].

---

## 10. DB Schema Cloud

# datatpdb — Khảo sát Schema & Cấu trúc Bảng

| Thông tin | Giá trị |
|---|---|
| Host | `postgres.of1-dev-crm.svc.cluster.local` |
| Port | `5432` |
| Database | `datatpdb` |
| Username | `datatp` |
| Password | `datatp` |
| DB Driver | `postgresql` |

---

## Master Data Tables

Các bảng danh mục dùng chung toàn hệ thống (country, location, currency, unit).

### 1. Quốc gia & Nhóm quốc gia

| Bảng | Rows | Mô tả |
|---|---|---|
| `settings_country` | 250 | Danh sách quốc gia (PK: `id`, UNIQUE: `code`) |
| `settings_country_group` | 27 | Nhóm quốc gia (e.g. ASEAN, EU) — hỗ trợ cây phân cấp (`parent_id`) |
| `settings_country_group_rel` | — | Mapping: country ↔ country_group |

**Cột quan trọng của `settings_country`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `code` | varchar | Mã ISO 2 ký tự (e.g. `VN`, `US`) — UNIQUE |
| `label` | varchar | Tên quốc gia (uppercase) |
| `label2` | varchar | Tên ngôn ngữ thứ hai |
| `phone_code` | varchar | Mã điện thoại quốc tế |
| `currency` | varchar | Mã tiền tệ mặc định |
| `address_format` | varchar | Định dạng địa chỉ theo quốc gia |

**Sample data — `settings_country`:**

| code | label | label2 | phone_code | currency |
|---|---|---|---|---|
| VN | VIETNAM | | | |
| US | UNITED STATES | | | |
| CN | CHINA | | | |
| JP | JAPAN | | | |
| SG | SINGAPORE | | | |
| KR | KOREA, REPUBLIC OF | SOUTH KOREA | | |
| DE | GERMANY | | | |

**Sample data — `settings_country_group`:**

| name | label |
|---|---|
| AF | AFRICA |
| AM | AMERICA |
| AS | ASIA |
| CEU | CENTRAL EUROPE |
| CAM | CENTRAL AMERICA |

---

### 2. Tiền tệ & Tỷ giá

| Bảng | Rows | Mô tả |
|---|---|---|
| `settings_currency` | 19 | Danh sách tiền tệ (UNIQUE: `name`) |
| `settings_currency_exchange_rate` | 0 | Tỷ giá theo thời kỳ (`valid_from` / `valid_to`) |

**Cột quan trọng của `settings_currency`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `name` | varchar | Mã tiền tệ ISO (e.g. `VND`, `USD`) — UNIQUE |
| `symbol` | varchar | Ký hiệu (e.g. `đ`, `$`) |
| `ext_usd` | double | Tỷ giá so với USD |
| `ext_vnd_sales` | double | Tỷ giá bán VND |
| `commission_ext_usd` | double | Tỷ giá hoa hồng USD |
| `commission_ext_vnd_sales` | double | Tỷ giá hoa hồng VND |
| `decimal_places` | int | Số chữ số thập phân |
| `rounding` | double | Đơn vị làm tròn |

**Cột quan trọng của `settings_currency_exchange_rate`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `currency` | varchar | FK → `settings_currency.name` |
| `exchange_rate` | double | Tỷ giá tại thời điểm |
| `valid_from` | timestamp | Bắt đầu hiệu lực |
| `valid_to` | timestamp | Kết thúc hiệu lực |

**Sample data — `settings_currency`:**

| name | symbol | ext_usd | ext_vnd_sales | decimal_places | rounding |
|---|---|---|---|---|---|
| VND | đ | — | — | 0 | 1000 |
| USD | $ | — | — | 0 | 0.01 |
| EUR | € | — | — | 0 | 0.01 |
| CNY | ¥ | — | — | 0 | 0.01 |
| JPY | ¥ | — | — | 0 | 0.01 |
| SGD | SG$ | — | — | 0 | 0.01 |
| GBP | £ | — | — | 0 | 0.01 |
| HKD | HK$ | — | — | 0 | 0.01 |
| MYR | RM | — | — | 0 | 0.01 |
| IDR | Rp | — | — | 0 | 0.01 |

> `ext_usd` và `ext_vnd_sales` hiện để trống — tỷ giá thực tế lấy từ BFS One MSSQL (`CurrencyExchangeRate`).

---

### 3. Địa điểm (Location)

Hệ thống địa điểm gồm 2 nhánh: **địa lý hành chính** (state/city/district/subdistrict) và **bảng tổng hợp** `settings_location`.

#### 3a. Địa lý hành chính

| Bảng | Rows | Mô tả |
|---|---|---|
| `settings_location_state` | 5,070 | Tỉnh/bang theo quốc gia |
| `settings_location_city` | 1,389 | Thành phố/quận theo tỉnh |
| `settings_location_district` | 706 | Huyện/quận theo tỉnh |
| `settings_location_subdistrict` | 13,923 | Phường/xã — cấp thấp nhất |
| `settings_location_road` | 0 | Đường/phố (chưa có data) |

**Cột chung của các bảng hành chính:**

| Cột | Mô tả |
|---|---|
| `code` | Mã định danh — UNIQUE |
| `label` | Tên địa danh |
| `country_id` / `country_label` | Quốc gia (denormalized) |
| `state_id` / `state_label` | Tỉnh (denormalized) |
| `gov_administration_code` | Mã hành chính Nhà nước |
| `administrative_unit` | Loại đơn vị hành chính (Thành phố, Huyện, ...) |
| `compute_id` | ID tính toán nội bộ — UNIQUE |
| `variants` | Tên biến thể/viết tắt |

**Sample data — `settings_location_state` (VN):**

| code | label | country_code | gov_administration_code |
|---|---|---|---|
| vn-01 | Thành phố Hà Nội | VN | 01 |
| vn-02 | Tỉnh Hà Giang | VN | 02 |
| vn-26 | Tỉnh Vĩnh Phúc | VN | 26 |
| vn-79 | Thành phố Hồ Chí Minh | VN | 79 |

**Sample data — `settings_location_city` (VN):**

| code | label | country_code | administrative_unit |
|---|---|---|---|
| VNHAN | HANOI | VN | |
| VNDAD | DA NANG | VN | |
| VNHPH | HAIPHONG | VN | |
| VNVCA | CAN THO | VN | |

**Sample data — `settings_location_district` (VN):**

| code | label | administrative_unit | state_label | gov_administration_code |
|---|---|---|---|---|
| vn-016 | Huyện Sóc Sơn | District | Thành phố Hà Nội | 016 |
| vn-017 | Huyện Đông Anh | District | Thành phố Hà Nội | 017 |
| vn-269 | Thị xã Sơn Tây | District | Thành phố Hà Nội | 269 |

**Sample data — `settings_location_subdistrict` (VN):**

| code | label | administrative_unit | district_label | state_label |
|---|---|---|---|---|
| vn-10330 | Xã Chuyên Mỹ | Subdistrict | | Thành phố Hà Nội |
| vn-10342 | Xã Đại Xuyên | Subdistrict | | Thành phố Hà Nội |
| vn-10354 | Xã Vân Đình | Subdistrict | | Thành phố Hà Nội |

#### 3b. Bảng tổng hợp `settings_location`

| Rows | Size | Ghi chú |
|---|---|---|
| 40,647 | 21 MB | Bảng địa điểm đa năng (airport, port, country, district, ...) |

**Cột quan trọng:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `code` | varchar | Mã nội bộ |
| `iata_code` | varchar | Mã IATA (sân bay) — UNIQUE với `location_type` |
| `un_locode` | varchar | Mã UN/LOCODE (cảng biển) |
| `label` | varchar | Tên đầy đủ |
| `short_label` | varchar | Tên viết tắt |
| `location_type` | varchar | Loại: `Airport`, `Port`, `Country`, `State`, `District`, `Subdistrict`, `Address`, `KCN` |
| `country_id` / `country_label` | — | Quốc gia (denormalized) |
| `state_id` / `district_id` / `subdistrict_id` | — | FK đến các bảng hành chính |
| `latitude` / `longitude` | double | Tọa độ địa lý |
| `postal_code` | varchar | Mã bưu chính |
| `contact` | varchar | Thông tin liên hệ |

**Sample data — `settings_location` (Airport & Port):**

| code | label | iata_code | un_locode | location_type | country_label |
|---|---|---|---|---|---|
| SGN | TAN SON NHAT INTERNATIONAL AIRPORT | SGN | | Airport | VIETNAM |
| VNHAN | NOI BAI INTERNATIONAL AIRPORT | HAN | | Airport | VIETNAM |
| DAD | DA NANG INTERNATIONAL AIRPORT | DAD | | Airport | VIETNAM |
| SGSIN | SINGAPORE, SINGAPORE | | SGSIN | Port | SINGAPORE |
| LVRIX | RIGA, LATVIA | | LVRIX | Port | LATVIA |

#### 3c. Bảng phụ trợ location

| Bảng | Rows | Mô tả |
|---|---|---|
| `settings_location_reference_code` | 30,962 | Mã tham chiếu thêm cho location (IATA Code, UNLOCODE, Can Code, Aus Code, US Code, ...) |
| `settings_location_tag` | — | Tag phân loại location |
| `settings_location_tag_rel` | — | Mapping: location ↔ tag |

**Sample data — `settings_location_reference_code`:**

| code | type | label |
|---|---|---|
| SGN | IATA Code | SGN |
| HAN | IATA Code | HAN |
| VNSGN | UNLOCODE | VNSGN |
| VNHAN | UNLOCODE | VNHAN |

---

### 4. Đơn vị đo lường

| Bảng | Rows | Mô tả |
|---|---|---|
| `company_settings_unit` | 172 | Đơn vị đo (kg, CBM, pcs, ...) — scoped theo `company_id` |
| `company_settings_unit_group` | 26 | Nhóm đơn vị (Weight, Volume, Quantity, ...) |
| `company_settings_unit_alias` | — | Bí danh/alias cho đơn vị |

**Cột quan trọng của `company_settings_unit`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `name` | varchar | Mã đơn vị — UNIQUE |
| `label` | varchar | Tên hiển thị |
| `group_name` | varchar | Nhóm đơn vị |
| `iso_code` | varchar | Mã ISO |
| `scale` | double | Tỷ lệ quy đổi |
| `description` / `en_description` | varchar | Mô tả (VN/EN) |
| `afr_alias_id` | varchar | Alias cho AFR |
| `ams_aci_alias_id` | varchar | Alias cho AMS/ACI |
| `shareable` | varchar | Có chia sẻ giữa các company không |

**Sample data — `company_settings_unit`:**

| name | label | group_name | description |
|---|---|---|---|
| KGM | kg(s) | weight | Kilogram |
| TNE | Metric ton(s) | weight | Tấn |
| LBR | Pounds | weight | Cân Anh |
| MTQ | cbm | volume | Mét khối |
| CBM | Cubic Metter | volume | Cubic Meter |
| TEU | TEU | volume | TEU |
| FEU | FEU | volume | FEU |
| LTR | Litre | volume | Lít |
| MTR | Metre(s) | length | Mét |
| MTK | m2 | area | m2 |
| BAG | Bag(s) | packing | Túi |
| BAL | Bale | packing | Bao |
| BA | Barrel(s) | packing | Thùng |

---

## Quan hệ giữa các bảng master data

```
settings_country (code)
  ├──► settings_country_group_rel (country ↔ country_group)
  └──► settings_location (country_id)
         ├──► settings_location_reference_code (location_id)
         └──► settings_location_tag_rel (location_id)

settings_location_state (id)
  └──► settings_location_city (state_id)
         └──► settings_location_district (state_id)
                └──► settings_location_subdistrict (district_id)

settings_currency (name)
  └──► settings_currency_exchange_rate (currency)

company_settings_unit (id)
  └──► company_settings_unit_alias (unit_id)
```

---

## Ghi chú

- Tất cả bảng đều có audit fields: `created_by`, `created_time`, `modified_by`, `modified_time`, `version`, `storage_state`.
- Các bảng địa chính dùng pattern **denormalized labels** (lưu `country_label`, `state_label` trực tiếp trong row) để tránh JOIN khi query.
- `settings_location` là bảng đa năng — gộp airport, port, district, address vào một bảng và phân loại qua `location_type`.
- `settings_currency_exchange_rate` hiện chưa có data — tỷ giá có thể đang lấy từ BFS One MSSQL (`CurrencyExchangeRate`).

---

## lgc_mgmt — Logistics Management Module

**30 bảng** quản lý vận đơn và quy trình vận chuyển hàng hóa theo các phương thức (Air/Sea/Rail/Truck/CC).

---

### Nhóm A — Transactions - Master Bill (Vận đơn chủ)

| Bảng | Rows | Mô tả |
|---|---|---|
| `lgc_mgmt_air_master_bill` | 7,779 | Vận đơn chủ hàng không (MAWB) |
| `lgc_mgmt_air_master_bill_custom_field` | 7 | Custom print fields cho Air MAWB |
| `lgc_mgmt_air_master_bill_follower` | ~0 | Người theo dõi Air MAWB |
| `lgc_mgmt_sea_master_bill` | 12,062 | Vận đơn chủ đường biển (MBL/BOL) |
| `lgc_mgmt_sea_master_bill_custom_field` | 2 | Custom print fields cho Sea MBL |
| `lgc_mgmt_sea_master_bill_follower` | ~0 | Người theo dõi Sea MBL |
| `lgc_mgmt_rail_master_bill` | 1 | Vận đơn chủ đường sắt |
| `lgc_mgmt_rail_master_bill_follower` | ~0 | Người theo dõi Rail MB |
| `lgc_mgmt_master_bill_attachment` | 6 | File đính kèm vận đơn chủ |

**Cột chung của các Master Bill:**

| Cột | Mô tả |
|---|---|
| `code` | Mã nội bộ — UNIQUE |
| `master_bill_no` | Số vận đơn chủ (MAWB#/MBL#) |
| `master_shipper_partner_id` / `master_shipper_label` | Người gửi (denormalized) |
| `master_consignee_partner_id` / `master_consignee_label` | Người nhận (denormalized) |
| `master_consolidator_partner_id` / `master_consolidator_label` | Consolidator |
| `carrier_partner_id` / `carrier_label` | Hãng tàu/hàng không |
| `shipment_type` | Loại lô hàng (FCL/LCL/Air) |
| `transportation_mode` | Phương thức (AIR/SEA/RAIL) |
| `purpose` | Mục đích (Original/Sea Waybill/Surrender/...) |
| `issued_date` | Ngày phát hành |
| `close_date` | Ngày đóng |
| `state` | Trạng thái |
| `chargeable_weight_in_kgs` / `gross_weight_in_kgs` / `volume_in_cbm` | Thông số hàng hóa |
| `ignore_sync` | Bỏ qua sync CDC |

---

### Nhóm B — House Bills (Vận đơn nhà)

| Bảng | Rows | Mô tả |
|---|---|---|
| `lgc_mgmt_air_house_bill` | 9,166 | Vận đơn nhà hàng không (HAWB) |
| `lgc_mgmt_air_house_bill_custom_field` | 9,164 | Custom print fields cho Air HAWB |
| `lgc_mgmt_sea_house_bill` | 18,670 | Vận đơn nhà đường biển (HBL) |
| `lgc_mgmt_sea_house_bill_custom_field` | 18,667 | Custom print fields cho Sea HBL |
| `lgc_mgmt_rail_house_bill` | 1 | Vận đơn nhà đường sắt |
| `lgc_mgmt_truck_house_bill` | 56,728 | Vận đơn nhà đường bộ |
| `lgc_mgmt_truck_house_bill_custom_field` | 56,728 | Custom print fields cho Truck HBL |
| `lgc_mgmt_cc_house_bill` | 1 | Vận đơn nhà Cross-Country (customs) |
| `lgc_mgmt_house_bill_attachment` | 6 | File đính kèm vận đơn nhà |

**Cột chung của các House Bill:**

| Cột | Mô tả |
|---|---|
| `code` | Mã nội bộ — UNIQUE |
| `booking_process_id` | FK → `lgc_mgmt_booking_process.id` — NOT NULL |
| `order_process_id` | FK → `lgc_mgmt_order_process.id` — NOT NULL |
| `master_bill_id` | FK → master bill tương ứng (theo mode) |
| `shipper_partner_id` / `shipper_label` | Người gửi (denormalized) |
| `consignee_partner_id` / `consignee_label` | Người nhận (denormalized) |
| `notify_party_partner_id` / `notify_party_label` | Bên thông báo |
| `handling_agent_partner_id` / `handling_agent_label` | Đại lý xử lý |
| `client_partner_id` / `client_label` | Khách hàng |
| `sales_employee_id` / `sales_label` | Nhân viên kinh doanh |
| `assignee_employee_id` / `assignee_label` | Nhân viên phụ trách |
| `shipment_type` | Loại lô hàng |
| `payment_term` | Điều khoản thanh toán (Prepaid/Collect) |
| `purpose` | Mục đích vận đơn |
| `status` / `state` | Trạng thái |
| `issued_date` | Ngày phát hành |
| `cargo_gross_weight` / `cargo_volume` / `cargo_chargeable_weight` | Thông số hàng hóa |
| `package_quantity` / `packaging_type` | Số kiện và loại bao bì |
| `no_of_original_hbl` | Số bản gốc vận đơn |
| `warehouse_location_config_id` | FK → cấu hình kho |
| `desc_of_goods` | Mô tả hàng hóa |

**Cột đặc thù Sea HBL (`lgc_mgmt_sea_house_bill`):**

| Cột | Mô tả |
|---|---|
| `mode` | FCL/LCL — NOT NULL |
| `lcl_type` | Loại LCL |
| `manifest_no` | Số manifest |
| `require_hc_*` | Yêu cầu chứng từ (surrender/seaway/original/...) |
| `free_demurrage_note` / `free_detention_note` / `free_storage_note` | Ghi chú free time |

**Cột đặc thù CC HBL (`lgc_mgmt_cc_house_bill`):**

| Cột | Mô tả |
|---|---|
| `type` | Loại CC — NOT NULL |
| `cds_no` / `cds_date` | Số/ngày tờ khai hải quan |
| `customs_agency_partner_id` / `customs_agency_partner_name` | Đại lý hải quan |
| `selectivity_of_customs` | Luồng kiểm tra hải quan |
| `ops_employee_id` / `ops_employee_label` | Nhân viên ops |

---

### Nhóm C — Transport Plan (Kế hoạch vận chuyển)

| Bảng | Rows | Mô tả |
|---|---|---|
| `lgc_mgmt_transport_plan` | 81,225 | Kế hoạch vận chuyển tổng thể (FK: `booking_process_id`) |
| `lgc_mgmt_order_transport_plan` | 84,560 | Kế hoạch vận chuyển theo order (FK: `transport_plan_id`, `order_process_id`) |
| `lgc_mgmt_master_bill_transport_plan` | 19,835 | Kế hoạch vận chuyển theo master bill |
| `lgc_mgmt_transport_route` | 103,058 | Từng chặng vận chuyển (FK: `order_transport_plan_id`, `master_bill_transport_plan_id`) |

**Cột quan trọng `lgc_mgmt_transport_route`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `from_location_code` / `from_location_label` | varchar | Điểm đi |
| `to_location_code` / `to_location_label` | varchar | Điểm đến |
| `depart_time` / `arrival_time` | timestamp | Giờ khởi hành / đến |
| `transport_no` | varchar | Số chuyến/chuyến bay/tàu |
| `transport_method_label` | varchar | Tên phương tiện |
| `carrier_partner_id` | bigint | FK → partner (hãng vận chuyển) |
| `carrier_label` / `carrier_short_name` | varchar | Tên hãng (denormalized) |
| `sort_order` | int | Thứ tự chặng |

---

### Nhóm D — Cargo & Container

| Bảng | Rows | Mô tả |
|---|---|---|
| `lgc_mgmt_trackable_cargo` | 64,517 | Hàng hóa có thể tracking (FK: `booking_process_id`, `container_id`) |
| `lgc_mgmt_trackable_container` | 32,023 | Container tracking |

**Cột quan trọng `lgc_mgmt_trackable_cargo`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `quantity` | double | Số lượng — NOT NULL |
| `packaging_type` | varchar | Loại bao bì |
| `gross_weight_of_each_package` / `gross_weight_unit` | double/varchar | Trọng lượng |
| `gross_volume` / `gross_volume_unit` | double/varchar | Thể tích |
| `total_gross_weight_in_kg` / `total_volume_in_cbm` | double | Tổng quy chuẩn |
| `dimension_x/y/z` / `dimension_unit` | double/varchar | Kích thước |
| `container_id` | bigint | FK → `lgc_mgmt_trackable_container.id` |
| `container_no` | varchar | Số container (denormalized) |
| `booking_process_id` | bigint | FK → `lgc_mgmt_booking_process.id` |

**Cột quan trọng `lgc_mgmt_trackable_container`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `container_type` | varchar | Loại container (20GP/40HQ/...) |
| `seal_no` | varchar | Số chì seal |
| `master_bill_code` | varchar | Mã master bill (denormalized) |
| `max_gross_weight` / `verified_gross_mass` | double | Trọng lượng tối đa / VGM |
| `requested_temperature` | varchar | Nhiệt độ yêu cầu (Reefer) |
| `ventilation` | varchar | Thông khí |

---

### Nhóm E — Core Process (Quy trình đặt hàng & booking)

| Bảng | Rows | Mô tả |
|---|---|---|
| `lgc_mgmt_purchase_order` | 81,226 | Đơn hàng mua (PK: `id`, UNIQUE: `code`) |
| `lgc_mgmt_purchase_order_follower` | 60,631 | Người theo dõi đơn hàng |
| `lgc_mgmt_booking_process` | 81,225 | Booking lô hàng (PK: `id`, UNIQUE: `code`; FK: `purchase_order_id`) |
| `lgc_mgmt_booking_process_commodity` | 78,296 | Hàng hóa trong booking (FK: `booking_process_id`) |
| `lgc_mgmt_booking_process_commodity_type_rel` | 1 | Mapping: commodity ↔ commodity_type |
| `lgc_mgmt_order_process` | 84,561 | Quy trình order theo booking (FK: `booking_process_id`) |

**Cột quan trọng `lgc_mgmt_purchase_order`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `code` | varchar | Mã đơn hàng — UNIQUE, NOT NULL |
| `label` | varchar | Tên đơn hàng |
| `client_partner_id` | bigint | FK → partner (khách hàng) |
| `assignee_employee_id` | bigint | FK → nhân viên phụ trách |
| `client_label` | varchar | Tên khách hàng (denormalized) |
| `assignee_label` | varchar | Tên nhân viên (denormalized) |

**Cột quan trọng `lgc_mgmt_booking_process`:**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `code` | varchar | Mã booking — UNIQUE, NOT NULL |
| `mode` | varchar | Phương thức vận chuyển (Air/Sea/Rail/Truck/CC) |
| `type` | varchar | Loại booking (FCL/LCL/Air/...) |
| `purchase_order_id` | bigint | FK → `lgc_mgmt_purchase_order.id` |
| `booking_id` | bigint | FK → booking (bên ngoài lgc_mgmt) |
| `state` | varchar | Trạng thái (draft/confirmed/...) |
| `close_date` | timestamp | Ngày đóng booking |
| `ignore_sync` | boolean | Bỏ qua sync CDC |

---

### Sơ đồ quan hệ

```
lgc_mgmt_purchase_order (id)
  ├──► lgc_mgmt_purchase_order_follower (po_id)
  └──► lgc_mgmt_booking_process (purchase_order_id)
         ├──► lgc_mgmt_booking_process_commodity (booking_process_id)
         │      └──► lgc_mgmt_booking_process_commodity_type_rel (commodity_id)
         ├──► lgc_mgmt_order_process (booking_process_id)
         │      └──► lgc_mgmt_order_transport_plan (order_process_id)
         │             └──► lgc_mgmt_transport_route (order_transport_plan_id)
         ├──► lgc_mgmt_transport_plan (booking_process_id)
         │      └──► lgc_mgmt_order_transport_plan (transport_plan_id)
         ├──► lgc_mgmt_trackable_cargo (booking_process_id)
         │      └──► lgc_mgmt_trackable_container (id ← container_id)
         │
         ├── [Air] lgc_mgmt_air_house_bill (booking_process_id, order_process_id)
         │      ├──► lgc_mgmt_air_house_bill_custom_field (id ← air_house_bill_custom_field_id)
         │      └──► lgc_mgmt_air_master_bill (id ← master_bill_id)
         │             ├──► lgc_mgmt_air_master_bill_custom_field (id ← air_master_bill_custom_field_id)
         │             ├──► lgc_mgmt_air_master_bill_follower (air_master_bill_id)
         │             └──► lgc_mgmt_master_bill_transport_plan (id ← air_master_bill_plan_id)
         │                    └──► lgc_mgmt_transport_route (master_bill_transport_plan_id)
         │
         ├── [Sea] lgc_mgmt_sea_house_bill (booking_process_id, order_process_id)
         │      ├──► lgc_mgmt_sea_house_bill_custom_field (id ← sea_house_bill_custom_field_id)
         │      └──► lgc_mgmt_sea_master_bill (id ← master_bill_id)
         │             ├──► lgc_mgmt_sea_master_bill_custom_field (id ← sea_master_bill_custom_field_id)
         │             ├──► lgc_mgmt_sea_master_bill_follower (sea_master_bill_id)
         │             └──► lgc_mgmt_master_bill_transport_plan (id ← sea_master_bill_plan_id)
         │                    └──► lgc_mgmt_transport_route (master_bill_transport_plan_id)
         │
         ├── [Rail] lgc_mgmt_rail_house_bill (booking_process_id, order_process_id)
         │      └──► lgc_mgmt_rail_master_bill (id ← master_bill_id)
         │             ├──► lgc_mgmt_rail_master_bill_follower (rail_master_bill_id)
         │             └──► lgc_mgmt_master_bill_transport_plan (id ← rail_master_bill_plan_id)
         │
         ├── [Truck] lgc_mgmt_truck_house_bill (booking_process_id, order_process_id)
         │      └──► lgc_mgmt_truck_house_bill_custom_field (id ← truck_house_bill_custom_field_id)
         │
         └── [CC] lgc_mgmt_cc_house_bill (booking_process_id, order_process_id)

lgc_mgmt_house_bill_attachment — tham chiếu qua hb_code (varchar, không FK cứng)
lgc_mgmt_master_bill_attachment — tham chiếu qua mb_code (varchar, không FK cứng)
```

---

### Ghi chú lgc_mgmt

- Tất cả bảng đều có audit fields chuẩn (`created_by`, `created_time`, `modified_by`, `modified_time`, `version`, `storage_state`).
- Các bảng **_custom_field** chứa thông tin in ấn tùy chỉnh (custom print), được tách ra khỏi bảng chính để giữ bảng chính gọn.
- Các bảng **_follower** lưu người theo dõi tài liệu, hỗ trợ notification; có thêm `type` (smallint) để phân biệt loại follower.
- Pattern **denormalized labels**: toàn bộ các bảng đều lưu thêm `_label` (tên) song song với `_id` (FK) để tránh JOIN khi query.
- Quan hệ `booking_process` → `house_bill` → `master_bill` là luồng chính: **1 PO → 1 Booking → N House Bills (theo mode) → N Master Bills**.
- `lgc_mgmt_transport_plan` và `lgc_mgmt_order_transport_plan` quản lý lịch trình vận chuyển tổng thể; `lgc_mgmt_transport_route` là từng chặng cụ thể.
- Attachment dùng `hb_code`/`mb_code` (varchar, không FK cứng) thay vì FK ID — cho phép tham chiếu linh hoạt qua code của vận đơn.
- `ignore_sync` (boolean) trên các master bill: đánh dấu bỏ qua CDC sync — hữu ích khi cần exclude các record test/dummy.
- Rail và CC hiện gần như chưa có data thực tế (1 record/loại) — đây là các mode đang pilot.

---

## 11. Data Integration Notes

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
