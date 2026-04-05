# Mapping: Transaction & House Bill

> BF1 -> FMS field mapping cho nhóm Transaction & House Bill
> Coverage: CDC-verified

---

## of1_fms_transactions

> CDC Handler: `FmsTransactionCDCHandler`

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `code` | varchar | Y | Mã lô hàng — UNIQUE | `Transactions` | `TransID` | |
| `trans_date` | timestamp | | Ngày tạo lô hàng (nghiệp vụ) | `Transactions` | `TransDate` | |
| `issued_date` | date | | Ngày phát hành | `Transactions` | `IssuedDate` | |
| `etd` | timestamp | | Estimated Time of Departure | `Transactions` | `LoadingDate` | |
| `eta` | timestamp | | Estimated Time of Arrival | `Transactions` | `ArrivalDate` | |
| `created_by_account_id` | bigint | | FK — người tạo lô (nghiệp vụ) | | | |
| `created_by_account_name` | varchar | | Tên người tạo lô (denormalized) | `Transactions` | `WhoisMaking` | |
| `op_account_id` | bigint | | FK — nhân viên OP | | | |
| `op_account_name` | varchar | | Tên nhân viên OP (denormalized) | | | |
| `master_bill_no` | varchar | | Số vận đơn chủ (MAWB# / MBL#) | `Transactions` | `MAWB` | |
| `type_of_service` | varchar | | Loại dịch vụ | `Transactions` | `TpyeofService` | |
| `shipment_type` | varchar | | Loại lô hàng: FREEHAND / NOMINATED | `Transactions` | `ModeSea` | |
| `incoterms` | varchar | | Điều kiện giao hàng | | | |
| `carrier_partner_id` | bigint | | FK — hãng vận chuyển | | | |
| `carrier_label` | varchar | | Tên hãng vận chuyển (denormalized) | `Transactions` | `ColoaderID` | |
| `handling_agent_partner_id` | bigint | | FK — đại lý xử lý | | | |
| `handling_agent_label` | varchar | | Tên đại lý xử lý (denormalized) | `Transactions` | `AgentID` | |
| `transport_name` | varchar | | Tên phương tiện | `Transactions` | `AirLine` | |
| `transport_no` | varchar | | Số hiệu phương tiện | `Transactions` | `FlghtNo` | |
| `from_location_code` | varchar | | Cảng xếp hàng | `Transactions` | `PortofLading` | |
| `from_location_label` | varchar | | Tên cảng xếp hàng (denormalized) | `Transactions` | `PortofLading` | |
| `to_location_code` | varchar | | Cảng dỡ hàng | `Transactions` | `PortofUnlading` | |
| `to_location_label` | varchar | | Tên cảng dỡ hàng (denormalized) | `Transactions` | `PortofUnlading` | |
| `state` | varchar | | Trạng thái | `Transactions` | `Starus` | |
| `cargo_gross_weight_in_kgs` | double | | Trọng lượng tổng (kg) | `Transactions` | `GrossWeight` | |
| `cargo_volume_in_cbm` | double | | Thể tích (CBM) | `Transactions` | `Dimension` | |
| `cargo_chargeable_weight_in_kgs` | double | | Trọng lượng tính cước | `Transactions` | `ChargeableWeight` | |
| `package_quantity` | int | | Số kiện hàng | `Transactions` | `Noofpieces` | |
| `packaging_type` | varchar | | Loại bao bì | | | |
| `container_vol` | varchar | | Thông tin container (text) | `Transactions` | `ContainerSize` | |

---

## of1_fms_house_bill

> CDC Handler: `TransactionDetailsCDCHandler`

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `hawb_no` | varchar | Y | Mã nội bộ hoặc số house bill — UNIQUE | `TransactionDetails` | `HWBNO` | |
| `type_of_service` | varchar | | Loại dịch vụ | | | |
| `booking_process_id` | bigint | | FK → of1_fms_booking.id | | | |
| `transaction_id` | bigint | | FK → of1_fms_transactions.id | | | |
| `shipment_type` | varchar | | Loại lô hàng | `TransactionDetails` | `ShipmentType` | |
| `client_partner_id` | bigint | | FK — khách hàng | | | |
| `client_label` | varchar | | Tên khách hàng (denormalized) | `TransactionDetails` | `ContactID` | |
| `handling_agent_partner_id` | bigint | | FK — đại lý xử lý | | | |
| `handling_agent_label` | varchar | | Tên đại lý xử lý (denormalized) | | | |
| `saleman_account_id` | bigint | | FK — nhân viên kinh doanh | | | |
| `saleman_label` | varchar | | Tên nhân viên kinh doanh (denormalized) | `TransactionDetails` | `SalesManID` | |
| `assignee_account_id` | bigint | | FK — nhân viên phụ trách | | | |
| `assignee_label` | varchar | | Tên nhân viên phụ trách (denormalized) | | | |
| `status` | varchar | | Trạng thái | | | |
| `issued_date` | date | | Ngày phát hành | | | |
| `cargo_gross_weight_in_kgs` | double | | Trọng lượng tổng (kg) | `TransactionDetails` | `GrosWeight` | |
| `cargo_volume_in_cbm` | double | | Thể tích (CBM) | `TransactionDetails` | `CBMSea` | |
| `cargo_chargeable_weight_in_kgs` | double | | Trọng lượng tính cước | `TransactionDetails` | `WeightChargeable` | |
| `container_vol` | varchar | | Thông tin container (text) | `TransactionDetails` | `ContainerSize` | |
| `desc_of_goods` | varchar | | Mô tả hàng hóa | `TransactionDetails` | `Description` | |
| `package_quantity` | int | | Số kiện hàng | `TransactionDetails` | `Quantity` | |
| `packaging_type` | varchar | | Loại bao bì | `TransactionDetails` | `UnitDetail` | |

---

## of1_fms_house_bill_detail_base

> CDC Handler: `HAWBDetailsCDCHandler` (mapBaseFields)

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | Y | FK → of1_fms_house_bill.id | | | |
| `payment_term` | varchar | | Điều khoản thanh toán | | | |
| `description_of_goods` | varchar | | Mô tả hàng hóa | `HAWBDETAILS` | `Description` | |
| `quantity` | decimal | | Số lượng | `HAWBDETAILS` | `NoPieces` | |
| `weight` | decimal | | Trọng lượng | `HAWBDETAILS` | `GrossWeight` | |
| `volume` | decimal | | Thể tích | `HAWBDETAILS` | `CBM` | |
| `unit` | varchar | | Đơn vị | `HAWBDETAILS` | `Unit` | |
| `rate_code` | varchar | | Mã loại phí | | | |
| `rate_amount` | decimal | | Giá trị | `HAWBDETAILS` | `RateCharge` | |
| `warehouse_location_config_id` | bigint | | FK → cấu hình kho | | | |

---

## of1_fms_air_house_bill_detail

> CDC Handler: `HAWBDetailsCDCHandler` (upsertAirDetail — khi typeOfService KHÔNG chứa "sea")
> Base fields kế thừa từ `of1_fms_house_bill_detail_base` (xem bảng trên)

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | Y | FK → of1_fms_house_bill.id | | | |
| `shipper_partner_id` | bigint | | FK — người gửi | | | |
| `shipper_label` | varchar | | Tên người gửi | | | |
| `consignee_partner_id` | bigint | | FK — người nhận | | | |
| `consignee_label` | varchar | | Tên người nhận | | | |
| `notify_party_partner_id` | bigint | | FK — bên thông báo | | | |
| `notify_party_label` | varchar | | Tên bên thông báo | | | |
| `no_of_original_hbl` | int | | Số bản gốc vận đơn | | | |

---

## of1_fms_sea_house_bill_detail

> CDC Handler: `HAWBDetailsCDCHandler` (upsertSeaDetail — khi typeOfService chứa "sea")
> Base fields kế thừa từ `of1_fms_house_bill_detail_base` (xem bảng trên)

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | Y | FK → of1_fms_house_bill.id | | | |
| `shipper_partner_id` | bigint | | FK — người gửi | | | |
| `shipper_label` | varchar | | Tên người gửi | | | |
| `consignee_partner_id` | bigint | | FK — người nhận | | | |
| `consignee_label` | varchar | | Tên người nhận | | | |
| `notify_party_partner_id` | bigint | | FK — bên thông báo | | | |
| `notify_party_label` | varchar | | Tên bên thông báo | | | |
| `no_of_original_hbl` | int | | Số bản gốc vận đơn | | | |
| `manifest_no` | varchar | | Số manifest | | | |
| `require_hc_surrender` | boolean | | Yêu cầu surrender bill | | | |
| `require_hc_seaway` | boolean | | Yêu cầu seaway bill | | | |
| `require_hc_original` | boolean | | Yêu cầu original bill | | | |
| `free_demurrage_note` | varchar | | Ghi chú free time demurrage | | | |
| `free_detention_note` | varchar | | Ghi chú free time detention | | | |
| `free_storage_note` | varchar | | Ghi chú free time storage | | | |

---

## of1_fms_truck_house_bill_detail

> FMS-only — không có tương đương BF1
> CDC Handler: Chưa có

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | Y | FK → of1_fms_house_bill.id | | | |

---

## of1_fms_logistics_house_bill_detail

> CDC Handler: Chưa có
> Coverage: Schema match — chưa CDC-verified
> Note: BF1 `CustomsDeclaration` liên kết gián tiếp qua `TransactionDetails.CustomsID`

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | Y | FK → of1_fms_house_bill.id | | | |
| `cds_no` | varchar | | Số tờ khai hải quan | `CustomsDeclaration` | `MasoTK` | |
| `cds_date` | date | | Ngày tờ khai hải quan | `CustomsDeclaration` | `DeclarationDate` | |
| `customs_agency_partner_id` | bigint | | FK — đại lý hải quan | | | |
| `customs_agency_partner_name` | varchar | | Tên đại lý hải quan (denormalized) | | | |
| `selectivity_of_customs` | varchar | | Luồng kiểm tra hải quan | `CustomsDeclaration` | `Status` | |
| `ops_account_id` | bigint | | FK — nhân viên ops | | | |
| `ops_label` | varchar | | Tên nhân viên ops (denormalized) | | | |
