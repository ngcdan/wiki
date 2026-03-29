# ERP — BF1 Logistics Management

Sơ đồ Entity Relationship cho các thực thể nghiệp vụ cốt lõi của hệ thống BF1.

![Domain Model](img/domain-model.png)

---

## Nhóm A — Shipment Domain

### `of1_fms_transactions` — Transactions - Vận đơn chủ (Master Bill)

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `code` | varchar | ✓ | Mã lô hàng — UNIQUE (e.g. `BIHCM008238/25`) |
| `trans_date` | timestamp |  | Ngày tạo lô hàng (nghiệp vụ) |
| `created_by_account_id` | bigint |  | FK → `of1_fms_user_role.id` — người tạo lô (nghiệp vụ) |
| `created_by_account_name` | varchar |  | Tên người tạo lô (denormalized) |
| `master_bill_no` | varchar |  | Số vận đơn chủ (MAWB# / MBL#) |
| `type_of_service` | varchar |  | Loại dịch vụ (xem enum bên dưới) |
| `shipment_type` | varchar |  | Loại lô hàng: `FREEHAND` / `NOMINATED` |
| `carrier_partner_id` | bigint |  | FK → `of1_fms_partner.id` (hãng vận chuyển) |
| `carrier_label` | varchar |  | Tên hãng vận chuyển (denormalized) |
| `issued_date` | date |  | Ngày phát hành |
| `loading_date` | timestamp |  | Ngày xếp hàng thực tế |
| `arrival_date` | timestamp |  | Ngày hàng đến thực tế |
| `etd` | timestamp |  | Estimated Time of Departure |
| `eta` | timestamp |  | Estimated Time of Arrival |
| `from_location_code` | varchar |  | Cảng xếp hàng (FK → `of1_fms_settings_location.code`) |
| `from_location_label` | varchar |  | Tên cảng xếp hàng (denormalized) |
| `to_location_code` | varchar |  | Cảng dỡ hàng (FK → `of1_fms_settings_location.code`) |
| `to_location_label` | varchar |  | Tên cảng dỡ hàng (denormalized) |
| `state` | varchar |  | Trạng thái |

> **`type_of_service` enum:**
>
> | Code | Label | Giá trị cũ |
> |---|---|---|
> | `AIR_EXPORT` | Air Export | `AirExpTransactions` |
> | `AIR_IMPORT` | Air Import | `AirImpTransactions` |
> | `SEA_EXPORT_FCL` | Sea Export FCL | `SeaExpTransactions_FCL` |
> | `SEA_EXPORT_LCL` | Sea Export LCL | `SeaExpTransactions_LCL` |
> | `SEA_IMPORT_FCL` | Sea Import FCL | `SeaImpTransactions_FCL` |
> | `SEA_IMPORT_LCL` | Sea Import LCL | `SeaImpTransactions_LCL` |
> | `CUSTOMS_LOGISTICS` | Customs & Logistics | `CustomsLogistics` |
> | `INLAND_TRUCKING` | Inland Trucking | `InlandTrucking` |
> | `CROSS_BORDER` | Cross Border Logistics | `LogisticsCrossBorder` |
> | `ROUND_USE_TRUCKING` | Round Use Trucking | `RoundUseTrucking` |
> | `WAREHOUSE` | Warehouse Service | `WarehouseService` |

### `of1_fms_house_bill` — Vận đơn nhà (House Bill)

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `hawb_no` | varchar | ✓ | Mã nội bộ tự gen hoặc số house bill trên chứng từ — UNIQUE |
| `type_of_service` | varchar |  | Loại dịch vụ (xem enum bên dưới) |
| `booking_process_id` | bigint |  | FK → `of1_fms_booking.id` |
| `transaction_id` | bigint |  | FK → `of1_fms_transactions.id` |
| `shipment_type` | varchar |  | Loại lô hàng |
| `client_partner_id` | bigint |  | FK → `of1_fms_partner.id` (khách hàng) |
| `client_label` | varchar |  | Tên khách hàng (denormalized) |
| `handling_agent_partner_id` | bigint |  | FK → `of1_fms_partner.id` (đại lý xử lý) |
| `handling_agent_label` | varchar |  | Tên đại lý xử lý (denormalized) |
| `saleman_account_id` | bigint |  | FK → `of1_fms_user_role.id` (nhân viên kinh doanh) |
| `saleman_label` | varchar |  | Tên nhân viên kinh doanh (denormalized) |
| `assignee_account_id` | bigint |  | FK → `of1_fms_user_role.id` (nhân viên phụ trách) |
| `assignee_label` | varchar |  | Tên nhân viên phụ trách (denormalized) |
| `status` | varchar |  | Trạng thái |
| `issued_date` | date |  | Ngày phát hành |
| `cargo_gross_weight` | double |  | Trọng lượng tổng (kg) |
| `cargo_volume` | double |  | Thể tích (CBM) |
| `cargo_chargeable_weight` | double |  | Trọng lượng tính cước |
| `container_vol` | varchar |  | Thông tin container (text) |
| `desc_of_goods` | varchar |  | Mô tả hàng hóa |
| `package_quantity` | int |  | Số kiện hàng |
| `packaging_type` | varchar |  | Loại bao bì |

### `of1_fms_hawb_detail` — Chi tiết vận đơn nhà

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `hawb_no` | varchar | ✓ | FK → `of1_fms_house_bill.hawb_no` (PK & FK) |
| `type_of_service` | varchar |  | Loại dịch vụ (xem enum bên dưới) |
| `shipper_partner_id` | bigint |  | FK → `of1_fms_partner.id` (người gửi) |
| `shipper_label` | varchar |  | Tên người gửi — hiển thị trên bill |
| `consignee_partner_id` | bigint |  | FK → `of1_fms_partner.id` (người nhận) |
| `consignee_label` | varchar |  | Tên người nhận — hiển thị trên bill |
| `notify_party_partner_id` | bigint |  | FK → `of1_fms_partner.id` (bên thông báo) |
| `notify_party_label` | varchar |  | Tên bên thông báo — hiển thị trên bill |
| `payment_term` | varchar |  | Điều khoản thanh toán |
| `no_of_original_hbl` | int |  | Số bản gốc vận đơn |
| `description` | varchar |  | Mô tả hàng hóa |
| `quantity` | decimal |  | Số lượng |
| `weight` | decimal |  | Trọng lượng |
| `volume` | decimal |  | Thể tích |
| `unit` | varchar |  | Đơn vị |
| `rate_code` | varchar |  | Mã loại phí |
| `rate_amount` | decimal |  | Giá trị |
| `currency` | varchar |  | Ngoại tệ |
| `warehouse_location_config_id` | bigint |  | FK → cấu hình kho |
| `manifest_no` | varchar |  | Số manifest (Sea) |
| `require_hc_surrender` | boolean |  | Yêu cầu surrender bill (Sea) |
| `require_hc_seaway` | boolean |  | Yêu cầu seaway bill (Sea) |
| `require_hc_original` | boolean |  | Yêu cầu original bill (Sea) |
| `free_demurrage_note` | varchar |  | Ghi chú free time demurrage (Sea) |
| `free_detention_note` | varchar |  | Ghi chú free time detention (Sea) |
| `free_storage_note` | varchar |  | Ghi chú free time storage (Sea) |
| `cds_no` | varchar |  | Số tờ khai hải quan (Logistics) |
| `cds_date` | date |  | Ngày tờ khai hải quan (Logistics) |
| `customs_agency_partner_id` | bigint |  | FK → `of1_fms_partner.id` (đại lý hải quan) (Logistics) |
| `customs_agency_partner_name` | varchar |  | Tên đại lý hải quan (denormalized) (Logistics) |
| `selectivity_of_customs` | varchar |  | Luồng kiểm tra hải quan (Logistics) |
| `ops_account_id` | bigint |  | FK → `of1_fms_user_role.id` (nhân viên ops) (Logistics) |
| `ops_label` | varchar |  | Tên nhân viên ops (denormalized) (Logistics) |

> Các trường đánh dấu **(Sea)** chỉ áp dụng cho dịch vụ Sea (SeaExp/SeaImp).
> Các trường đánh dấu **(Logistics)** chỉ áp dụng cho CustomsLogistics / InlandTrucking.

> [!NOTE]
> `of1_fms_hawb_detail` có thể chia thành từng bảng riêng cho từng loại dịch vụ:
> `of1_fms_sea_hawb_detail` / `of1_fms_air_hawb_detail` / `of1_fms_trucking_hawb_detail` / `of1_fms_logistics_hawb_detail` / ...

---

## Nhóm B — Tracking & Tracing

### `of1_fms_cargo_container` — Container

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `house_bill_id` | bigint |  | FK → `of1_fms_house_bill.id` |
| `container_no` | varchar |  | Số container |
| `container_type` | varchar |  | Loại container: `20GP` / `40HQ` / ... |
| `seal_no` | varchar |  | Số chì seal |
| `quantity` | double |  | Số lượng |
| `gross_weight_in_kg` | double |  | Trọng lượng (kg) |
| `volume_in_cbm` | double |  | Thể tích (CBM) |
| `packaging_type` | varchar |  | Loại bao bì |

### `of1_fms_commodity` — Hàng hóa

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `house_bill_id` | bigint |  | FK → `of1_fms_house_bill.id` |
| `container_id` | bigint |  | FK → `of1_fms_cargo_container.id` (nullable) |
| `commodity_code` | varchar |  | Mã hàng hóa (FK → `of1_fms_settings_commodity.code`) |
| `commodity_desc` | varchar |  | Mô tả hàng hóa |
| `desc_of_goods` | varchar |  | Mô tả chi tiết hàng hóa |
| `hs_code` | varchar |  | Mã HS code |
| `quantity` | double |  | Số lượng |
| `gross_weight_in_kg` | double |  | Trọng lượng (kg) |
| `volume_in_cbm` | double |  | Thể tích (CBM) |
| `packaging_type` | varchar |  | Loại bao bì |
| `package_quantity` | int |  | Số kiện |

### `of1_fms_transport_plan` — Kế hoạch vận chuyển

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `house_bill_id` | bigint |  | FK → `of1_fms_house_bill.id` |
| `booking_process_id` | bigint |  | FK → `of1_fms_booking.id` |
| `from_location_code` | varchar |  | Điểm đi chặng đầu (FK → `of1_fms_settings_location.code`) |
| `from_location_label` | varchar |  | Tên điểm đi chặng đầu (denormalized) |
| `to_location_code` | varchar |  | Điểm đến chặng cuối (FK → `of1_fms_settings_location.code`) |
| `to_location_label` | varchar |  | Tên điểm đến chặng cuối (denormalized) |
| `depart_time` | timestamp |  | Giờ khởi hành (chặng đầu) |
| `arrival_time` | timestamp |  | Giờ đến (chặng cuối) |
| `state` | varchar |  | Trạng thái |

### `of1_fms_transport_route` — Chặng vận chuyển

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `transport_plan_id` | bigint |  | FK → `of1_fms_transport_plan.id` |
| `from_location_code` | varchar |  | Mã điểm đi (FK → `of1_fms_settings_location.code`) |
| `from_location_label` | varchar |  | Tên điểm đi (denormalized) |
| `to_location_code` | varchar |  | Mã điểm đến (FK → `of1_fms_settings_location.code`) |
| `to_location_label` | varchar |  | Tên điểm đến (denormalized) |
| `depart_time` | timestamp |  | Giờ khởi hành |
| `arrival_time` | timestamp |  | Giờ đến |
| `transport_no` | varchar |  | Số chuyến / tàu / chuyến bay |
| `transport_method_label` | varchar |  | Phương tiện |
| `carrier_partner_id` | bigint |  | FK → `of1_fms_partner.id` (hãng vận chuyển, type `COLOADER`) |
| `carrier_label` | varchar |  | Tên hãng vận chuyển (denormalized) |
| `sort_order` | int |  | Thứ tự chặng |

### `of1_fms_hawb_rates`

> Toàn bộ phí, cước mua bán trên từng house bill (selling, buying).

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `house_bill_id` | bigint |  | FK → `of1_fms_house_bill.id` |
| `charge_code` | varchar |  | Mã loại phí (FK → `of1_fms_settings_charge_type.code`) |
| `charge_name` | varchar |  | Tên phí |
| `rate_type` | varchar |  | Loại: `Debit` / `Credit` / `On_Behalf` |
| `quantity` | double |  | Số lượng |
| `unit` | varchar |  | Đơn vị tính phí (FK → `of1_fms_settings_unit.code`) |
| `unit_price` | double |  | Đơn giá |
| `total` | double |  | Thành tiền (trước thuế) |
| `total_tax` | double |  | Thuế |
| `final_charge` | double |  | Thành tiền (sau thuế) |
| `currency` | varchar |  | Ngoại tệ |
| `exchange_rate` | decimal(20,6) |  | Tỷ giá quy đổi |
| `domestic_currency` | varchar |  | Loại nội tệ (e.g. `VND`) |
| `domestic_total` | double |  | Thành tiền nội tệ (trước thuế) |
| `domestic_total_tax` | double |  | Thuế nội tệ |
| `domestic_final_charge` | double |  | Thành tiền nội tệ (sau thuế) |
| `payer_partner_id` | bigint |  | FK → `of1_fms_partner.id` (bên thanh toán) |
| `payer_label` | varchar |  | Tên bên thanh toán (denormalized) |
| `payee_partner_id` | bigint |  | FK → `of1_fms_partner.id` (bên thụ hưởng) |
| `payee_label` | varchar |  | Tên bên thụ hưởng (denormalized) |
| `reference_code` | varchar |  | Mã tham chiếu (dùng cho reference sau này) |

---

## Nhóm C — Order Domain

### Đặt vấn đề

#### Mô Hình Purchase Order (PO)

Sau khi nói chuyện kỹ với Xuân thì mình và Xuân có thống nhất một số vấn đề:

1. Mô hình hiện tại chỉ chú trọng giải quyết các bài toán về gom hàng ship hàng qua đường biển và đường hàng không.
2. Không giải quyết được bài toán như khách hàng có 5 lô hàng, cần giao trước hai lô, và giao tiếp 3 lô tháng sau nhưng vẫn cần theo dõi như một đơn hàng.
3. Mô hình hiện tại và các chức năng là chắp vá dựa trên mô hình master bill và house bill là mô hình cho vận tải đường biển. Rất khó để phát triển các nghiệp vụ khác trên nền tảng master bill/house bill. Ví dụ nghiệp vụ kê khai hải quan, hay nghiệp vụ vận tải đường đường bộ, gom và vận chuyển bằng xe tải.

**Mô hình Purchase Order:**

1. Coi tất cả các yêu cầu của khách hàng là một Purchase Order (PO)
2. 1 PO có thể có 1 hoặc nhiều booking (sẽ giải bài toán khách hàng cần giao trước một số lô hàng)
3. Mỗi một nghiệp vụ xử lý yêu cầu của khách hàng sẽ là 1 Purchase Order Process (POP), 1 POP sẽ hoạt động độc lập, có một mã số riêng để theo dõi, có lưu trữ các hoá đơn, chứng từ, document riêng cho từng POP.

> **Ví dụ:** Yêu cầu của khách hàng là có 5 kiện hàng, cần vận chuyển door to door, 2 kiện đi trước vào đầu tháng và 2 kiện đi sau vào giữa tháng. Như vậy ở đây chúng ta cần 3 nghiệp vụ để giải quyết yêu cầu khách hàng:
>
> 1. Nghiệp vụ gom hàng và vận chuyển hàng bằng xe tải từ kho tới cảng và từ cảng về kho.
> 2. Nghiệp vụ vận chuyển bằng đường biển.
> 3. Nghiệp vụ kê khai thông quan.
>
> Nếu tổ chức theo mô hình Purchase Order và Purchase Order Process chúng ta sẽ có:
>
> 1. 1 Purchase Order từ khách hàng với 2 booking cho 2 lần vận chuyển khác nhau.
> 2. 1 POP vận chuyển bằng xe tải từ kho ra cảng, 1 POP ship hàng, 1 POP khai quan và 1 POP vận chuyển hàng từ cảng về kho của khách hàng. Như vậy có 4 POP cho 1 lần vận chuyển và 2 lần vận chuyển là 8 POP.
> 3. Mô hình master bill/house bill cũ chỉ tương ứng với một POP (purchase order process) của 1 PO (Purchase Order).

---

### `of1_fms_purchase_order` — Đơn hàng

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `code` | varchar | ✓ | Mã đơn hàng — UNIQUE |
| `order_date` | timestamp |  | Ngày tạo đơn hàng (nghiệp vụ) |
| `label` | varchar |  | Tên đơn hàng |
| `client_partner_id` | bigint |  | FK → `of1_fms_partner.id` (khách hàng) |
| `client_label` | varchar |  | Tên khách hàng (denormalized) |
| `assignee_account_id` | bigint |  | FK → `of1_fms_user_role.id` (nhân viên phụ trách) |
| `assignee_label` | varchar |  | Tên nhân viên phụ trách (denormalized) |

### `of1_fms_booking_process` — Booking Process

> Clone từ booking của khách hàng. Tracking trạng thái xử lý được ghi nhận trên record này.

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigserial |  | PK |
| `code` | varchar | ✓ | Mã booking — UNIQUE |
| `type_of_service` | varchar |  | Loại dịch vụ (xem enum bên dưới) |
| `purchase_order_id` | bigint |  | FK → `of1_fms_purchase_order.id` |
| `state` | varchar |  | Trạng thái: `draft` / `confirmed` / ... |
| `close_date` | timestamp |  | Ngày đóng booking |

> **`type_of_service` enum:** `AIR_EXPORT`, `AIR_IMPORT`, `SEA_EXPORT_FCL`, `SEA_EXPORT_LCL`, `SEA_IMPORT_FCL`, `SEA_IMPORT_LCL`, `CUSTOMS_LOGISTICS`, `INLAND_TRUCKING`, `CROSS_BORDER`, `ROUND_USE_TRUCKING`, `WAREHOUSE`

---

## Audit Fields (áp dụng cho tất cả bảng)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `company_id` | bigint | FK → công ty sở hữu bản ghi |
| `created_by` | varchar | Người tạo |
| `created_time` | timestamp | Thời điểm tạo |
| `modified_by` | varchar | Người sửa cuối |
| `modified_time` | timestamp | Thời điểm sửa cuối |
| `version` | int | Optimistic locking |
| `storage_state` | varchar | Vòng đời bản ghi: `CREATED` / `ACTIVE` / `INACTIVE` / `JUNK` / `DEPRECATED` / `ARCHIVED` |

---