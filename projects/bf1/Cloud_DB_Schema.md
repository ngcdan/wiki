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

### Nhóm A — Core Process (Quy trình đặt hàng & booking)

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

### Nhóm B — Transport Plan (Kế hoạch vận chuyển)

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

### Nhóm C — Master Bills (Vận đơn chủ)

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

### Nhóm D — House Bills (Vận đơn nhà)

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

### Nhóm E — Cargo & Container

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
