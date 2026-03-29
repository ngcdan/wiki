# Schema: Documentation — Transactions, House Bill, Cargo

Tài liệu schema cho các bảng nghiệp vụ vận đơn và hàng hóa trong hệ thống FMS.

---

## Nhóm A — Shipment Domain

### `of1_fms_transactions` — Vận đơn chủ (Master Bill)

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `code` | varchar | ✓ | Mã lô hàng — UNIQUE (e.g. `BIHCM008238/25`) | |
| `trans_date` | timestamp | | Ngày tạo lô hàng (nghiệp vụ) | |
| `created_by_account_id` | bigint | | Người tạo lô (nghiệp vụ) | FK → `of1_fms_user_role.id` |
| `created_by_account_name` | varchar | | Tên người tạo lô (denormalized) | |
| `master_bill_no` | varchar | | Số vận đơn chủ (MAWB# / MBL#) | |
| `type_of_service` | varchar | | Loại dịch vụ (xem enum bên dưới) | |
| `shipment_type` | varchar | | Loại lô hàng: `FREEHAND` / `NOMINATED` | |
| `carrier_partner_id` | bigint | | Hãng vận chuyển | FK → `of1_fms_partner.id` |
| `carrier_label` | varchar | | Tên hãng vận chuyển (denormalized) | |
| `issued_date` | date | | Ngày phát hành | |
| `loading_date` | timestamp | | Ngày xếp hàng thực tế | |
| `arrival_date` | timestamp | | Ngày hàng đến thực tế | |
| `etd` | timestamp | | Estimated Time of Departure | |
| `eta` | timestamp | | Estimated Time of Arrival | |
| `from_location_code` | varchar | | Cảng xếp hàng | FK → `settings_location.code` |
| `from_location_label` | varchar | | Tên cảng xếp hàng (denormalized) | |
| `to_location_code` | varchar | | Cảng dỡ hàng | FK → `settings_location.code` |
| `to_location_label` | varchar | | Tên cảng dỡ hàng (denormalized) | |
| `state` | varchar | | Trạng thái | |

**Enum `type_of_service`:**

| Code | Mô tả |
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

---

### `of1_fms_house_bill` — Vận đơn nhà (House Bill)

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `hawb_no` | varchar | ✓ | Mã nội bộ tự gen hoặc số house bill trên chứng từ — UNIQUE | |
| `type_of_service` | varchar | | Loại dịch vụ (xem enum `of1_fms_transactions`) | |
| `booking_process_id` | bigint | | FK → `of1_fms_booking.id` (booking nguồn — alias là booking_process trong BF1 cũ) | `of1_fms_booking.id` |
| `transaction_id` | bigint | | Liên kết vận đơn chủ | FK → `of1_fms_transactions.id` |
| `shipment_type` | varchar | | Loại lô hàng | |
| `client_partner_id` | bigint | | Khách hàng | FK → `of1_fms_partner.id` |
| `client_label` | varchar | | Tên khách hàng (denormalized) | |
| `handling_agent_partner_id` | bigint | | Đại lý xử lý | FK → `of1_fms_partner.id` |
| `handling_agent_label` | varchar | | Tên đại lý xử lý (denormalized) | |
| `saleman_account_id` | bigint | | Nhân viên kinh doanh | FK → `of1_fms_user_role.id` |
| `saleman_label` | varchar | | Tên nhân viên kinh doanh (denormalized) | |
| `assignee_account_id` | bigint | | Nhân viên phụ trách | FK → `of1_fms_user_role.id` |
| `assignee_label` | varchar | | Tên nhân viên phụ trách (denormalized) | |
| `status` | varchar | | Trạng thái | |
| `issued_date` | date | | Ngày phát hành | |
| `cargo_gross_weight` | double | | Trọng lượng tổng (kg) | |
| `cargo_volume` | double | | Thể tích (CBM) | |
| `cargo_chargeable_weight` | double | | Trọng lượng tính cước | |
| `container_vol` | varchar | | Thông tin container (text) | |
| `desc_of_goods` | varchar | | Mô tả hàng hóa | |
| `package_quantity` | int | | Số kiện hàng | |
| `packaging_type` | varchar | | Loại bao bì | |

---

### `of1_fms_hawb_detail` — Chi tiết vận đơn nhà

> Bảng tổng hợp chi tiết cho tất cả loại dịch vụ. Các trường đánh dấu **(Sea)** chỉ áp dụng cho SeaExp/SeaImp. Các trường đánh dấu **(Logistics)** chỉ áp dụng cho CustomsLogistics / InlandTrucking.
>
> [!NOTE]
> `of1_fms_hawb_detail` có thể chia thành từng bảng riêng trong tương lai: `of1_fms_sea_hawb_detail` / `of1_fms_air_hawb_detail` / `of1_fms_trucking_hawb_detail` / `of1_fms_logistics_hawb_detail` / ...

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `hawb_no` | varchar | ✓ | PK & FK — liên kết house bill | FK → `of1_fms_house_bill.hawb_no` |
| `type_of_service` | varchar | | Loại dịch vụ | |
| `shipper_partner_id` | bigint | | Người gửi | FK → `of1_fms_partner.id` |
| `shipper_label` | varchar | | Tên người gửi — hiển thị trên bill | |
| `consignee_partner_id` | bigint | | Người nhận | FK → `of1_fms_partner.id` |
| `consignee_label` | varchar | | Tên người nhận — hiển thị trên bill | |
| `notify_party_partner_id` | bigint | | Bên thông báo | FK → `of1_fms_partner.id` |
| `notify_party_label` | varchar | | Tên bên thông báo — hiển thị trên bill | |
| `payment_term` | varchar | | Điều khoản thanh toán | |
| `no_of_original_hbl` | int | | Số bản gốc vận đơn | |
| `description` | varchar | | Mô tả hàng hóa | |
| `quantity` | decimal | | Số lượng | |
| `weight` | decimal | | Trọng lượng | |
| `volume` | decimal | | Thể tích | |
| `unit` | varchar | | Đơn vị | |
| `rate_code` | varchar | | Mã loại phí | |
| `rate_amount` | decimal | | Giá trị | |
| `currency` | varchar | | Ngoại tệ | |
| `warehouse_location_config_id` | bigint | | FK → cấu hình kho | |
| `manifest_no` | varchar | | Số manifest **(Sea)** | |
| `require_hc_surrender` | boolean | | Yêu cầu surrender bill **(Sea)** | |
| `require_hc_seaway` | boolean | | Yêu cầu seaway bill **(Sea)** | |
| `require_hc_original` | boolean | | Yêu cầu original bill **(Sea)** | |
| `free_demurrage_note` | varchar | | Ghi chú free time demurrage **(Sea)** | |
| `free_detention_note` | varchar | | Ghi chú free time detention **(Sea)** | |
| `free_storage_note` | varchar | | Ghi chú free time storage **(Sea)** | |
| `cds_no` | varchar | | Số tờ khai hải quan **(Logistics)** | |
| `cds_date` | date | | Ngày tờ khai hải quan **(Logistics)** | |
| `customs_agency_partner_id` | bigint | | Đại lý hải quan **(Logistics)** | FK → `of1_fms_partner.id` |
| `customs_agency_partner_name` | varchar | | Tên đại lý hải quan (denormalized) **(Logistics)** | |
| `selectivity_of_customs` | varchar | | Luồng kiểm tra hải quan **(Logistics)** | |
| `ops_account_id` | bigint | | Nhân viên ops **(Logistics)** | FK → `of1_fms_user_role.id` |
| `ops_label` | varchar | | Tên nhân viên ops (denormalized) **(Logistics)** | |

---

## Nhóm B — Tracking & Tracing

### `of1_fms_cargo_container` — Container

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `house_bill_id` | bigint | | Liên kết house bill | FK → `of1_fms_house_bill.id` |
| `container_no` | varchar | | Số container | |
| `container_type` | varchar | | Loại container: `20GP` / `40HQ` / ... | |
| `seal_no` | varchar | | Số chì seal | |
| `quantity` | double | | Số lượng | |
| `gross_weight_in_kg` | double | | Trọng lượng (kg) | |
| `volume_in_cbm` | double | | Thể tích (CBM) | |
| `packaging_type` | varchar | | Loại bao bì | |

---

### `of1_fms_commodity` — Hàng hóa

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `house_bill_id` | bigint | | Liên kết house bill | FK → `of1_fms_house_bill.id` |
| `container_id` | bigint | | Liên kết container (nullable) | FK → `of1_fms_cargo_container.id` |
| `commodity_code` | varchar | | Mã hàng hóa | FK → `of1_fms_settings_commodity.code` |
| `commodity_desc` | varchar | | Mô tả hàng hóa | |
| `desc_of_goods` | varchar | | Mô tả chi tiết hàng hóa | |
| `hs_code` | varchar | | Mã HS code | |
| `quantity` | double | | Số lượng | |
| `gross_weight_in_kg` | double | | Trọng lượng (kg) | |
| `volume_in_cbm` | double | | Thể tích (CBM) | |
| `packaging_type` | varchar | | Loại bao bì | |
| `package_quantity` | int | | Số kiện | |

---

## Entity Relations

- `of1_fms_booking` (1) → (N) `of1_fms_transactions` (master bill)
- `of1_fms_transactions` (1) → (N) `of1_fms_house_bill`
- `of1_fms_house_bill` (1) → (1) `of1_fms_hawb_detail`
- `of1_fms_house_bill` (1) → (N) `of1_fms_cargo_container`
- `of1_fms_cargo_container` (1) → (N) `of1_fms_commodity`
- `of1_fms_house_bill` (N) → (1) `of1_fms_partner` (client) — xem schema/catalogue.md
- `of1_fms_house_bill` (N) → (1) `of1_fms_user_role` (saleman) — xem schema/catalogue.md

> Cross-reference: transactions và house_bill FKs đến partner và user_role được định nghĩa trong schema/catalogue.md
> Booking FK: xem schema/sales.md cho of1_fms_booking
