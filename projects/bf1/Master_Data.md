# Master Data — BF1 Cloud System

---

## Nhóm A — Địa lý & Tiền tệ

### A1. `settings_country` — Quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar(2) | | Mã ISO 3166-1 alpha-2 (e.g. `VN`, `US`) — UNIQUE | `code` |
| `code3` | varchar(3) | | Mã ISO 3166-1 alpha-3 (e.g. `VNM`) | — |
| `label` | varchar | | Tên quốc gia (tiếng Anh, uppercase) | `label` |
| `localized_label` | varchar | | Tên bản địa | `label2` |
| `phone_code` | varchar(10) | | Mã điện thoại quốc tế (e.g. `+84`) | `phone_code` |
| `currency_code` | varchar(3) | | Mã tiền tệ mặc định (FK → `settings_currency.code`) | `currency` |
| `address_format` | varchar | | Template định dạng địa chỉ theo quốc gia | `address_format` |

**Sample data:**

| id | code | code3 | label | localized_label | phone_code | currency_code |
|---|---|---|---|---|---|---|
| 1 | `VN` | `VNM` | VIETNAM | Việt Nam | `+84` | `VND` |
| 2 | `US` | `USA` | UNITED STATES | Hoa Kỳ | `+1` | `USD` |
| 3 | `CN` | `CHN` | CHINA | Trung Quốc | `+86` | `CNY` |
| 4 | `SG` | `SGP` | SINGAPORE | Singapore | `+65` | `SGD` |
| 5 | `JP` | `JPN` | JAPAN | Nhật Bản | `+81` | `JPY` |
| 6 | `KR` | `KOR` | KOREA, REPUBLIC OF | Hàn Quốc | `+82` | `KRW` |

### A2. `settings_country_group` — Nhóm quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nhóm (e.g. `ASEAN`, `EU`) — UNIQUE | `name` |
| `label` | varchar | | Tên nhóm | `label` |
| `parent_id` | bigint | | FK → `settings_country_group.id` (hỗ trợ phân cấp) | — |

**Sample data:**

| id | code | label | parent_id |
|---|---|---|---|
| 1 | `ASEAN` | ASEAN Countries | null |
| 2 | `EU` | European Union | null |
| 3 | `APAC` | Asia Pacific | null |
| 4 | `SEA` | Southeast Asia | 3 |

### A3. `settings_country_group_rel` — Mapping quốc gia ↔ nhóm

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `country_id` | bigint | | FK → `settings_country.id` | `country` |
| `group_id` | bigint | | FK → `settings_country_group.id` | `country_group` |

**Sample data:**

| country_id | group_id | (mô tả) |
|---|---|---|
| 1 (VN) | 1 (ASEAN) | Vietnam → ASEAN |
| 1 (VN) | 4 (SEA) | Vietnam → SEA |
| 4 (SG) | 1 (ASEAN) | Singapore → ASEAN |
| 4 (SG) | 4 (SEA) | Singapore → SEA |

### A4. `settings_zone` — Khu vực vận chuyển

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã khu vực — UNIQUE | `name` |
| `label` | varchar | | Tên khu vực | `label` |
| `zone_type` | varchar | | Phân loại: `global`, `local`, `custom` | — |

**Sample data:**

| id | code | label | zone_type |
|---|---|---|---|
| 1 | `GLOBAL` | Global | `global` |
| 2 | `VN_NORTH` | Vietnam - North | `local` |
| 3 | `VN_SOUTH` | Vietnam - South | `local` |
| 4 | `VN_CENTRAL` | Vietnam - Central | `local` |
| 5 | `ASEAN_ZONE` | ASEAN Region | `custom` |

### A5. `settings_location_state` — Tỉnh / Bang

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã định danh — UNIQUE | `code` |
| `label` | varchar | | Tên tỉnh/bang | `label` |
| `country_id` | bigint | | FK → `settings_country.id` | `country_id` |
| `country_code` | varchar(2) | | Denormalized | `country_label` |
| `gov_code` | varchar | | Mã hành chính nhà nước | `gov_administration_code` |
| `administrative_unit` | varchar | | Loại đơn vị (Tỉnh, Thành phố trực thuộc TW) | `administrative_unit` |

**Sample data:**

| id | code | label | country_id | country_code | gov_code | administrative_unit |
|---|---|---|---|---|---|---|
| 1 | `VN-SG` | Hồ Chí Minh | 1 | `VN` | `79` | Thành phố trực thuộc TW |
| 2 | `VN-HN` | Hà Nội | 1 | `VN` | `01` | Thành phố trực thuộc TW |
| 3 | `VN-DN` | Đà Nẵng | 1 | `VN` | `48` | Thành phố trực thuộc TW |
| 4 | `VN-BD` | Bình Dương | 1 | `VN` | `74` | Tỉnh |
| 5 | `VN-DN2` | Đồng Nai | 1 | `VN` | `75` | Tỉnh |

### A6. `settings_location_district` — Huyện / Quận

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã định danh — UNIQUE | `code` |
| `label` | varchar | | Tên huyện/quận | `label` |
| `state_id` | bigint | | FK → `settings_location_state.id` | `state_id` |
| `state_label` | varchar | | Denormalized | `state_label` |
| `gov_code` | varchar | | Mã hành chính nhà nước | `gov_administration_code` |
| `administrative_unit` | varchar | | Loại đơn vị (Huyện, Quận, Thị xã) | `administrative_unit` |

**Sample data:**

| id | code | label | state_id | state_label | gov_code | administrative_unit |
|---|---|---|---|---|---|---|
| 1 | `VN-SG-Q1` | Quận 1 | 1 | Hồ Chí Minh | `760` | Quận |
| 2 | `VN-SG-Q7` | Quận 7 | 1 | Hồ Chí Minh | `770` | Quận |
| 3 | `VN-SG-BT` | Bình Thạnh | 1 | Hồ Chí Minh | `765` | Quận |
| 4 | `VN-HN-HK` | Hoàn Kiếm | 2 | Hà Nội | `002` | Quận |

### A7. `settings_location_subdistrict` — Phường / Xã

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã định danh — UNIQUE | `code` |
| `label` | varchar | | Tên phường/xã | `label` |
| `district_id` | bigint | | FK → `settings_location_district.id` | `district_id` |
| `district_label` | varchar | | Denormalized | `district_label` |
| `state_id` | bigint | | FK → `settings_location_state.id` | `state_id` |
| `state_label` | varchar | | Denormalized | `state_label` |
| `gov_code` | varchar | | Mã hành chính nhà nước | `gov_administration_code` |
| `administrative_unit` | varchar | | Loại đơn vị (Phường, Xã, Thị trấn) | `administrative_unit` |
| `postal_code` | varchar | | Mã bưu chính | — |

**Sample data:**

| id | code | label | district_id | district_label | state_id | state_label | gov_code | administrative_unit | postal_code |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `VN-SG-Q1-BN` | Bến Nghé | 1 | Quận 1 | 1 | Hồ Chí Minh | `26734` | Phường | `700000` |
| 2 | `VN-SG-Q1-BT` | Bến Thành | 1 | Quận 1 | 1 | Hồ Chí Minh | `26737` | Phường | `700000` |
| 3 | `VN-SG-Q7-TPH` | Tân Phong | 2 | Quận 7 | 1 | Hồ Chí Minh | `26863` | Phường | `700000` |

### A8. `settings_location` — Địa điểm (Sân bay, Cảng, KCN, ...)

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nội bộ — UNIQUE | `code` |
| `iata_code` | varchar(3) | | Mã IATA sân bay | `iata_code` |
| `un_locode` | varchar | | Mã UN/LOCODE cảng biển | `un_locode` |
| `label` | varchar | | Tên đầy đủ | `label` |
| `short_label` | varchar | | Tên viết tắt | `short_label` |
| `location_type` | varchar | | `Airport` / `Port` / `KCN` / `State` / `District` / `Address` | `location_type` |
| `country_id` | bigint | | FK → `settings_country.id` | `country_id` |
| `country_label` | varchar | | Denormalized | `country_label` |
| `state_id` | bigint | | FK → `settings_location_state.id` | `state_id` |
| `district_id` | bigint | | FK → `settings_location_district.id` | `district_id` |
| `subdistrict_id` | bigint | | FK → `settings_location_subdistrict.id` | `subdistrict_id` |
| `latitude` | double | | Vĩ độ | `latitude` |
| `longitude` | double | | Kinh độ | `longitude` |
| `postal_code` | varchar | | Mã bưu chính | `postal_code` |
| `contact` | varchar | | Thông tin liên hệ | `contact` |

**Sample data:**

| id | code | iata_code | un_locode | label | short_label | location_type | country_id | country_label | state_id | latitude | longitude |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `SGN` | `SGN` | — | Tan Son Nhat International Airport | SGN | `Airport` | 1 | VIETNAM | 1 | 10.8188 | 106.6520 |
| 2 | `HAN` | `HAN` | — | Noi Bai International Airport | HAN | `Airport` | 1 | VIETNAM | 2 | 21.2213 | 105.8074 |
| 3 | `DAD` | `DAD` | — | Da Nang International Airport | DAD | `Airport` | 1 | VIETNAM | 3 | 16.0439 | 108.1993 |
| 4 | `VNSGN` | — | `VNSGN` | Ho Chi Minh Port (Cat Lai) | Cat Lai | `Port` | 1 | VIETNAM | 1 | 10.7741 | 106.7590 |
| 5 | `VNDAD` | — | `VNDAD` | Da Nang Port | Da Nang | `Port` | 1 | VIETNAM | 3 | 16.0746 | 108.2237 |
| 6 | `SIN` | `SIN` | — | Singapore Changi Airport | SIN | `Airport` | 4 | SINGAPORE | null | 1.3644 | 103.9915 |

### A9. `settings_location_reference_code` — Mã tham chiếu bổ sung

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `location_id` | bigint | | FK → `settings_location.id` | `location_id` |
| `code` | varchar | | Giá trị mã | `code` |
| `code_type` | varchar | | Loại mã: `IATA`, `UNLOCODE`, `CAN_CODE`, `AUS_CODE`, `US_CODE`, ... | `type` |

**Sample data:**

| id | location_id | code | code_type |
|---|---|---|---|
| 1 | 1 (SGN) | `SGN` | `IATA` |
| 2 | 4 (VNSGN) | `VNSGN` | `UNLOCODE` |
| 3 | 4 (VNSGN) | `C0001` | `CAN_CODE` |
| 4 | 5 (VNDAD) | `VNDAD` | `UNLOCODE` |

### A10. `settings_currency` — Tiền tệ

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar(3) | | Mã ISO 4217 (e.g. `VND`, `USD`) — UNIQUE | `name` |
| `label` | varchar | | Tên tiền tệ | — |
| `symbol` | varchar(10) | | Ký hiệu (e.g. `đ`, `$`, `€`) | `symbol` |
| `decimal_places` | int | | Số chữ số thập phân (VND=0, USD=2) | `decimal_places` |
| `rounding` | double | | Đơn vị làm tròn | `rounding` |

**Sample data:**

| id | code | label | symbol | decimal_places | rounding |
|---|---|---|---|---|---|
| 1 | `VND` | Vietnamese Dong | `đ` | 0 | 1.0 |
| 2 | `USD` | US Dollar | `$` | 2 | 0.01 |
| 3 | `EUR` | Euro | `€` | 2 | 0.01 |
| 4 | `CNY` | Chinese Yuan | `¥` | 2 | 0.01 |
| 5 | `SGD` | Singapore Dollar | `S$` | 2 | 0.01 |
| 6 | `JPY` | Japanese Yen | `¥` | 0 | 1.0 |
| 7 | `KRW` | Korean Won | `₩` | 0 | 1.0 |

### A11. `settings_currency_exchange_rate` — Tỷ giá theo thời kỳ

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `currency_id` | bigint | | FK → `settings_currency.id` | `currency` |
| `base_currency_id` | bigint | | Tiền tệ cơ sở (thường là USD hoặc VND) | — |
| `rate` | decimal(20,6) | | Tỷ giá | `exchange_rate` |
| `valid_from` | timestamp | | Ngày bắt đầu hiệu lực | `valid_from` |
| `valid_to` | timestamp | | Ngày kết thúc hiệu lực (null = còn hiệu lực) | `valid_to` |
| `source` | varchar | | Nguồn tỷ giá (e.g. `SBV`, `manual`) | — |

**Sample data:** *(base = USD, tỷ giá tham khảo Q1/2026)*

| id | currency_id | base_currency_id | rate | valid_from | valid_to | source |
|---|---|---|---|---|---|---|
| 1 | 1 (VND) | 2 (USD) | `25450.000000` | `2026-01-01` | null | `SBV` |
| 2 | 3 (EUR) | 2 (USD) | `1.085000` | `2026-01-01` | null | `manual` |
| 3 | 4 (CNY) | 2 (USD) | `7.240000` | `2026-01-01` | null | `manual` |
| 4 | 5 (SGD) | 2 (USD) | `1.340000` | `2026-01-01` | null | `manual` |
| 5 | 1 (VND) | 2 (USD) | `24850.000000` | `2025-01-01` | `2025-12-31` | `SBV` |

---

## Nhóm B — Đơn vị đo lường

### B1. `settings_unit_group` — Nhóm đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nhóm (e.g. `weight`, `volume`, `quantity`) — UNIQUE | `name` |
| `label` | varchar | | Tên nhóm | `label` |

**Sample data:**

| id | code | label |
|---|---|---|
| 1 | `weight` | Weight |
| 2 | `volume` | Volume |
| 3 | `quantity` | Quantity |
| 4 | `length` | Length |
| 5 | `area` | Area |

### B2. `settings_unit` — Đơn vị đo

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã đơn vị (e.g. `KGM`, `MTQ`) — UNIQUE | `name` |
| `label` | varchar | | Tên hiển thị (e.g. `kg(s)`, `cbm`) | `label` |
| `group_id` | bigint | | FK → `settings_unit_group.id` | `group_name` |
| `iso_code` | varchar | | Mã ISO | `iso_code` |
| `scale` | double | | Tỷ lệ quy đổi về đơn vị chuẩn của nhóm | `scale` |
| `description` | varchar | | Mô tả tiếng Anh | `en_description` |
| `localized_description` | varchar | | Mô tả tiếng Việt | `description` |

**Sample data:**

| id | code | label | group_id | iso_code | scale | description | localized_description |
|---|---|---|---|---|---|---|---|
| 1 | `KGM` | kg(s) | 1 (weight) | `KGM` | 1.0 | Kilogram | Kilogram |
| 2 | `TNE` | ton(s) | 1 (weight) | `TNE` | 1000.0 | Metric Ton | Tấn |
| 3 | `LBR` | lbs | 1 (weight) | `LBR` | 0.453592 | Pound | Pound |
| 4 | `MTQ` | cbm | 2 (volume) | `MTQ` | 1.0 | Cubic Meter | Mét khối |
| 5 | `LTR` | liter(s) | 2 (volume) | `LTR` | 0.001 | Liter | Lít |
| 6 | `PKG` | pkg(s) | 3 (quantity) | `PKG` | 1.0 | Package | Kiện |
| 7 | `PCE` | pcs | 3 (quantity) | `PCE` | 1.0 | Piece | Cái |
| 8 | `CTN` | ctn(s) | 3 (quantity) | `CTN` | 1.0 | Carton | Thùng |

### B3. `settings_unit_alias` — Bí danh đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `unit_id` | bigint | | FK → `settings_unit.id` | `unit_id` |
| `alias` | varchar | | Tên alias | `alias_id` |
| `system` | varchar | | Hệ thống dùng alias (e.g. `AFR`, `AMS_ACI`) | `system` |

**Sample data:**

| id | unit_id | alias | system |
|---|---|---|---|
| 1 | 1 (KGM) | `KG` | `AFR` |
| 2 | 1 (KGM) | `KGS` | `AMS_ACI` |
| 3 | 4 (MTQ) | `CBM` | `AFR` |
| 4 | 4 (MTQ) | `M3` | `AMS_ACI` |
| 5 | 6 (PKG) | `PKGS` | `AFR` |

---

## Nhóm C — Hàng hóa

### C1. `settings_commodity` — Loại hàng hóa

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã hàng hóa — UNIQUE | `name` |
| `label` | varchar | | Tên hàng hóa | `label` |
| `hs_code` | varchar | | Mã HS code | — |
| `is_dangerous` | boolean | | Hàng nguy hiểm | — |

**Sample data:**

| id | code | label | hs_code | is_dangerous |
|---|---|---|---|---|
| 1 | `GEN` | General Cargo | — | false |
| 2 | `DGR` | Dangerous Goods | — | true |
| 3 | `PER` | Perishables | — | false |
| 4 | `CLD` | Cold Chain / Reefer | — | false |
| 5 | `ELC` | Electronics | `8471` | false |
| 6 | `TEX` | Garment / Textile | `6109` | false |
| 7 | `MAC` | Machinery & Equipment | `8479` | false |
| 8 | `CHE` | Chemicals | `2800` | true |

---

## Nhóm D — Tài chính

### D1. `settings_bank` — Ngân hàng

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã ngân hàng — UNIQUE | `name` |
| `swift_code` | varchar | | Mã SWIFT/BIC | `swift_code` |
| `label` | varchar | | Tên đầy đủ | `label` |
| `short_label` | varchar | | Tên viết tắt | `short_label` |
| `country_id` | bigint | | FK → `settings_country.id` | `country_id` |

**Sample data:**

| id | code | swift_code | label | short_label | country_id |
|---|---|---|---|---|---|
| 1 | `VCB` | `BFTVVNVX` | Ngân hàng TMCP Ngoại Thương Việt Nam | Vietcombank | 1 (VN) |
| 2 | `BIDV` | `BIDVVNVX` | Ngân hàng TMCP Đầu Tư và Phát Triển VN | BIDV | 1 (VN) |
| 3 | `ACB` | `ASCBVNVX` | Ngân hàng TMCP Á Châu | ACB | 1 (VN) |
| 4 | `TCB` | `VTCBVNVX` | Ngân hàng TMCP Kỹ Thương Việt Nam | Techcombank | 1 (VN) |
| 5 | `HSBC_VN` | `HSBCVNVX` | HSBC Vietnam | HSBC | 1 (VN) |
| 6 | `CITI_SG` | `CITISGSX` | Citibank Singapore | Citibank SG | 4 (SG) |

### D2. `settings_charge_type` — Danh mục loại phí

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã phí — UNIQUE | `name` |
| `label` | varchar | | Tên phí (e.g. THC, B/L Fee, Origin CFS) | `label` |
| `localized_label` | varchar | | Tên bản địa | `local_label` |
| `charge_group` | varchar | | Nhóm phí (Origin, Freight, Destination, Other) | `charge_group` |

**Sample data:**

| id | code | label | localized_label | charge_group |
|---|---|---|---|---|
| 1 | `OBL` | Original B/L Fee | Phí vận đơn gốc | `Origin` |
| 2 | `OTHC` | Origin THC | Phí xếp hàng cảng xuất | `Origin` |
| 3 | `OCFS` | Origin CFS | Phí CFS xuất | `Origin` |
| 4 | `OCF` | Ocean Freight | Cước biển | `Freight` |
| 5 | `FSC` | Fuel Surcharge | Phụ phí xăng dầu | `Freight` |
| 6 | `DTHC` | Destination THC | Phí xếp hàng cảng nhập | `Destination` |
| 7 | `DCFS` | Destination CFS | Phí CFS nhập | `Destination` |
| 8 | `DO` | Delivery Order Fee | Phí lệnh giao hàng | `Destination` |
| 9 | `COD` | COD Fee | Phí thu hộ | `Other` |

---

## Nhóm E — CRM / Phân loại đối tác

### E1. `settings_industry` — Ngành nghề

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã ngành — UNIQUE | `name` |
| `label` | varchar | | Tên ngành nghề | `label` |

**Sample data:**

| id | code | label |
|---|---|---|
| 1 | `MAN` | Manufacturing |
| 2 | `TRD` | Trading / Import-Export |
| 3 | `LOG` | Logistics / Freight Forwarding |
| 4 | `RET` | Retail |
| 5 | `CON` | Construction |
| 6 | `AGR` | Agriculture / Food |
| 7 | `ELC` | Electronics / Technology |

### E2. `settings_sale_type` — Loại kinh doanh

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã loại — UNIQUE | `name` |
| `label` | varchar | | Tên (e.g. Direct, Agent, Co-loader) | `label` |

**Sample data:**

| id | code | label |
|---|---|---|
| 1 | `DIRECT` | Direct |
| 2 | `AGENT` | Agent |
| 3 | `CO_LOAD` | Co-loader |
| 4 | `BROKER` | Customs Broker |
| 5 | `CARRIER` | Carrier / Airline |

### E3. `settings_partner_source` — Nguồn đối tác

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nguồn — UNIQUE | `name` |
| `label` | varchar | | Tên nguồn (e.g. Referral, Cold Call, Exhibition) | `label` |

**Sample data:**

| id | code | label |
|---|---|---|
| 1 | `REF` | Referral |
| 2 | `COLD` | Cold Call |
| 3 | `EXPO` | Exhibition / Trade Fair |
| 4 | `ONLINE` | Online / Website |
| 5 | `WALK_IN` | Walk-in |
| 6 | `EXISTING` | Existing Customer |

---

## Audit Fields (áp dụng cho tất cả bảng)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `created_by` | varchar | Người tạo |
| `created_time` | timestamp | Thời điểm tạo |
| `modified_by` | varchar | Người sửa cuối |
| `modified_time` | timestamp | Thời điểm sửa cuối |
| `version` | int | Optimistic locking |

---

## Sơ đồ quan hệ

```
settings_country (id)
  ├──► settings_country_group_rel → settings_country_group (hỗ trợ cây phân cấp)
  ├──► settings_location (country_id)
  ├──► settings_location_state (country_id)
  └──► settings_bank (country_id)

settings_location_state (id)
  └──► settings_location_district (state_id)
         └──► settings_location_subdistrict (district_id)

settings_location (id)
  └──► settings_location_reference_code (location_id)

settings_currency (id)
  └──► settings_currency_exchange_rate (currency_id)

settings_unit_group (id)
  └──► settings_unit (group_id)
         └──► settings_unit_alias (unit_id)

```
