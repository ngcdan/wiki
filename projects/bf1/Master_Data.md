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

### A3. `settings_country_group_rel` — Mapping quốc gia ↔ nhóm

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `country_id` | bigint | | FK → `settings_country.id` | `country` |
| `group_id` | bigint | | FK → `settings_country_group.id` | `country_group` |

**Sample data:**

| country_id | group_id | (mô tả) |
|---|---|---|
| 1 (VN) | 1 (ASEAN) | Vietnam → ASEAN |
| 2 (US) | 2 (EU) | — |

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
| 2 | `VN-HN-HK` | Hoàn Kiếm | 2 | Hà Nội | `002` | Quận |

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
| 2 | `VNSGN` | — | `VNSGN` | Ho Chi Minh Port (Cat Lai) | Cat Lai | `Port` | 1 | VIETNAM | 1 | 10.7741 | 106.7590 |

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
| 2 | 2 (VNSGN) | `VNSGN` | `UNLOCODE` |

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
| 2 | 1 (VND) | 2 (USD) | `24850.000000` | `2025-01-01` | `2025-12-31` | `SBV` |

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
| 2 | `MTQ` | cbm | 2 (volume) | `MTQ` | 1.0 | Cubic Meter | Mét khối |

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

### D2. `settings_charge_type` — Danh mục loại phí

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã phí — UNIQUE | `name` |
| `label` | varchar | | Tên phí (e.g. THC, B/L Fee, Origin CFS) | `label` |
| `localized_label` | varchar | | Tên bản địa | `local_label` |
| `charge_group` | varchar | | Nhóm phí (Origin, Freight, Destination, Other) | `charge_group` |
| `type` | varchar | | Phân loại: `SELLING` / `BUYING` | `type` |

**Sample data:**

| id | code | label | localized_label | charge_group | type |
|---|---|---|---|---|---|
| 1 | `OBL` | Original B/L Fee | Phí vận đơn gốc | `Origin` | `SELLING` |
| 2 | `OCF` | Ocean Freight | Cước biển | `Freight` | `BUYING` |

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
| 2 | `LOG` | Logistics / Freight Forwarding |

### E2. `settings_partner_source` — Nguồn đối tác (mạng lưới forwarder)


| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `label` | varchar | | Tên mạng lưới / kênh nguồn | `name` |

**Sample data:**

| id | label |
|---|---|
| 1 | WCA |
| 2 | WPA |

---

## Nhóm F — Partner / Forwarder

### F1. `of1_fms_custom_list` — Danh sách chi cục hải quan


| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigserial | | PK | `id` |
| `code` | varchar(255) | ✓ | Mã chi cục hải quan — UNIQUE | `code` |
| `label` | varchar(255) | | Tên chi cục hải quan | `label` |
| `name` | varchar(255) | | Mã nội bộ / tên định danh | `name` |
| `note` | varchar(4096) | | Ghi chú | `note` |
| `province` | varchar(255) | | Tỉnh/thành phố | `province` |
| `team_code` | varchar(255) | | Mã cục hải quan cấp trên | `team_code` |
| `team_name` | varchar(255) | | Tên đội thủ tục | `team_name` |
| `storage_state` | varchar(255) | | Trạng thái: `CREATED` / `ACTIVE` / `INACTIVE` / `JUNK` / `DEPRECATED` / `ARCHIVED` | `storage_state` |

**Sample data:**

| id | code | label | name | province | team_code | team_name | storage_state |
|---|---|---|---|---|---|---|---|
| 788 | `01D1` | Chi cục HQ Bưu Điện TP Hà Nội | MYDINHBDHN | Hà Nội | `00` | Đội Thủ tục HH XNK liên tỉnh | `ACTIVE` |
| 789 | `01D2` | Chi cục HQ Bưu Điện TP Hà Nội | FEDEXBDHN | Hà Nội | `00` | Đội Thủ tục HH XNK CPN – FeDex | `ACTIVE` |

### F2. `of1_fms_partner` — Đối tác / Khách hàng


**Định danh & phân loại:**

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigserial | | PK | `id` |
| `partner_code` | varchar | | Mã đối tác — UNIQUE (e.g. `CS016288`, `CN000138`) | `partner_code` |
| `category` | varchar | | Loại: `CUSTOMER`, `VENDOR`, ... | `category` |
| `partner_group` | varchar | | Nhóm: `CUSTOMERS`, `AGENTS`, ... | `partner_group` |
| `scope` | varchar | | Phạm vi: `Domestic` / `International` | `scope` |
| `shareable` | varchar | | Chia sẻ: `PRIVATE` / `PUBLIC` | `shareable` |
| `source` | varchar | | Hệ thống nguồn (e.g. `BEE`) | `source` |
| `partner_source` | varchar | | Mạng lưới / kênh (FK → `settings_partner_source.label`, e.g. `BEE_VN`) | `partner_source` |
| `status` | varchar | | Trạng thái bổ sung | `status` |
| `storage_state` | varchar | | `CREATED` / `ACTIVE` / `INACTIVE` / `JUNK` / `DEPRECATED` / `ARCHIVED` | `storage_state` |

**Tên & địa chỉ:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `label` | varchar | Tên tiếng Anh (uppercase) | `label` |
| `localized_label` | varchar | Tên tiếng Việt | `localized_label` |
| `name` | varchar | Tên ngắn / tên in | `name` |
| `address` | varchar | Địa chỉ tiếng Anh | `address` |
| `localized_address` | varchar | Địa chỉ tiếng Việt | `localized_address` |
| `work_address` | varchar | Địa chỉ làm việc | `work_address` |
| `country_id` | bigint | FK → `settings_country.id` | `country_id` |
| `country_label` | varchar | Denormalized | `country_label` |
| `province_id` | bigint | FK → `settings_location_state.id` | `province_id` |
| `province_label` | varchar | Denormalized | `province_label` |
| `continent` | varchar | Châu lục | `continent` |

**Liên hệ:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `email` | varchar | Email | `email` |
| `cell` | varchar | Điện thoại di động | `cell` |
| `home_phone` | varchar | Điện thoại nhà | `home_phone` |
| `work_phone` | varchar | Điện thoại văn phòng | `work_phone` |
| `fax` | varchar | Fax | `fax` |
| `personal_contact` | varchar | Người liên hệ | `personal_contact` |
| `vip_contact` | varchar | Liên hệ VIP | `vip_contact` |
| `vip_cellphone` | varchar | SĐT VIP | `vip_cellphone` |
| `vip_email` | varchar | Email VIP | `vip_email` |
| `vip_position` | varchar | Chức vụ VIP | `vip_position` |

**Tài chính & thuế:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `tax_code` | varchar | Mã số thuế | `tax_code` |
| `swift_code` | varchar | Mã SWIFT | `swift_code` |
| `bank_name` | varchar | Tên ngân hàng | `bank_name` |
| `bank_accs_no` | varchar | Số tài khoản | `bank_accs_no` |
| `bank_address` | varchar | Địa chỉ ngân hàng | `bank_address` |
| `bank_account` | varchar | Tài khoản ngân hàng bổ sung | `bank_account` |
| `bank_currency` | varchar | Tiền tệ tài khoản | `bank_currency` |
| `is_refund` | boolean | Có hoàn tiền không | `is_refund` |

**Phân loại ngành & KCN:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `industry_code` | varchar | FK → `settings_industry.code` | `industry_code` |
| `industry_label` | varchar | Denormalized | `industry_label` |
| `kcn_code` | varchar | Mã khu công nghiệp | `kcn_code` |
| `kcn_label` | varchar | Tên khu công nghiệp | `kcn_label` |
| `investment_origin` | varchar | Nguồn vốn đầu tư | `investment_origin` |

**Quản lý & phê duyệt:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `account_id` | bigint | FK account người phụ trách | `account_id` |
| `sale_owner_account_id` | bigint | Account sale phụ trách | `sale_owner_account_id` |
| `sale_owner_full_name` | varchar | Tên sale phụ trách | `sale_owner_full_name` |
| `approved_by_account_id` | bigint | Account duyệt | `approved_by_account_id` |
| `approved_by_full_name` | varchar | Tên người duyệt | `approved_by_full_name` |
| `request_by_account_id` | bigint | Account yêu cầu tạo | `request_by_account_id` |
| `request_by_full_name` | varchar | Tên người yêu cầu | `request_by_full_name` |
| `group_name` | varchar | Nhóm quản lý | `group_name` |
| `bfsone_group_id` | bigint | ID nhóm BFSOne | `bfsone_group_id` |
| `lead_code` | varchar | Mã lead | `lead_code` |
| `date_created` | timestamp | Ngày tạo nghiệp vụ (khác `created_time`) | `date_created` |
| `date_modified` | timestamp | Ngày sửa nghiệp vụ | `date_modified` |

**Khác:**

| Trường | Kiểu | Mô tả | BF1 Column |
|---|---|---|---|
| `note` | varchar | Ghi chú | `note` |
| `warning_message` | varchar | Cảnh báo hiển thị | `warning_message` |
| `suggestion` | varchar | Gợi ý | `suggestion` |
| `position` | varchar | Chức vụ | `position` |
| `print_custom_confirm_bill_info` | varchar | Thông tin in trên confirm bill | `print_custom_confirm_bill_info` |

**Sample data:**

| id | partner_code | label | localized_label | category | tax_code | province_label | partner_source | storage_state |
|---|---|---|---|---|---|---|---|---|
| 34682 | `CS016288` | LAVERGNE VIETNAM CO LTD | Công ty TNHH Lavergne Việt Nam | `CUSTOMER` | `4000765976` | Quảng Nam | `BEE_VN` | `ACTIVE` |
| 34700 | `CS016198` | HANESBRANDS VIETNAM CO., LTD-HUE BRANCH | CÔNG TY TNHH HANESBRANDS VIỆT NAM HUẾ | `CUSTOMER` | `3301559929` | Thừa Thiên Huế | `BEE_VN` | `ACTIVE` |

### F3. `of1_fms_saleman_partner_obligation` — Cam kết salesman ↔ đối tác


| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigserial | | PK | `id` |
| `code` | varchar | | Mã cam kết — UNIQUE | `code` |
| `obligation_type` | varchar | | Loại cam kết | `obligation_type` |
| `partner_id` | bigint | | FK → `of1_fms_partner.id` | `partner_id` |
| `partner_name` | varchar | | Denormalized | `partner_name` |
| `saleman_company_id` | bigint | | FK → công ty salesman | `saleman_company_id` |
| `saleman_account_id` | bigint | | FK → account salesman | `saleman_account_id` |
| `saleman_label` | varchar | | Tên salesman (denormalized) | `saleman_label` |
| `effective_from` | varchar | | Ngày bắt đầu hiệu lực | `effective_from` |
| `effective_to` | varchar | | Ngày kết thúc hiệu lực | `effective_to` |
| `note` | varchar | | Ghi chú | `note` |
| `storage_state` | varchar | | `CREATED` / `ACTIVE` / `INACTIVE` / `JUNK` / `DEPRECATED` / `ARCHIVED` | `storage_state` |

**Sample data:**

| id | obligation_type | partner_id | partner_name | saleman_company_id | saleman_account_id | saleman_label | storage_state |
|---|---|---|---|---|---|---|---|
| 409473 | `OWNER` | 85303 | BALTIC HAI DUONG-BALTIC HAI DUONG | 8 | 62378 | BEE HPH | `ACTIVE` |
| 409474 | `OWNER` | 81187 | XAY DUNG DIEN GREEN TECH | 8 | 2605 | TRẦN THỊ HỒNG LINH - NDLINHTTH | `ACTIVE` |

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

of1_fms_custom_list — danh sách độc lập, không FK ra ngoài
  (tra cứu theo team_code, province)

of1_fms_partner
  ├──► settings_country (country_id)
  ├──► settings_location_state (province_id)
  └──► settings_industry (industry_code)

of1_fms_saleman_partner_obligation
  └──► of1_fms_partner (partner_id)

```
