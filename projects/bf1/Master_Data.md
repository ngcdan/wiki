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

### A2. `settings_country_group` — Nhóm quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nhóm (e.g. `ASEAN`, `EU`) — UNIQUE | `name` |
| `label` | varchar | | Tên nhóm | `label` |
| `parent_id` | bigint | | FK → `settings_country_group.id` (hỗ trợ phân cấp) | — |

### A3. `settings_country_group_rel` — Mapping quốc gia ↔ nhóm

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `country_id` | bigint | | FK → `settings_country.id` | `country` |
| `group_id` | bigint | | FK → `settings_country_group.id` | `country_group` |

### A4. `settings_zone` — Khu vực vận chuyển

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã khu vực — UNIQUE | `name` |
| `label` | varchar | | Tên khu vực | `label` |
| `zone_type` | varchar | | Phân loại: `global`, `local`, `custom` | — |

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

### A9. `settings_location_reference_code` — Mã tham chiếu bổ sung

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `location_id` | bigint | | FK → `settings_location.id` | `location_id` |
| `code` | varchar | | Giá trị mã | `code` |
| `code_type` | varchar | | Loại mã: `IATA`, `UNLOCODE`, `CAN_CODE`, `AUS_CODE`, `US_CODE`, ... | `type` |

### A10. `settings_currency` — Tiền tệ

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar(3) | | Mã ISO 4217 (e.g. `VND`, `USD`) — UNIQUE | `name` |
| `label` | varchar | | Tên tiền tệ | — |
| `symbol` | varchar(10) | | Ký hiệu (e.g. `đ`, `$`, `€`) | `symbol` |
| `decimal_places` | int | | Số chữ số thập phân (VND=0, USD=2) | `decimal_places` |
| `rounding` | double | | Đơn vị làm tròn | `rounding` |

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

---

## Nhóm B — Đơn vị đo lường

### B1. `settings_unit_group` — Nhóm đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nhóm (e.g. `weight`, `volume`, `quantity`) — UNIQUE | `name` |
| `label` | varchar | | Tên nhóm | `label` |

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

### B3. `settings_unit_alias` — Bí danh đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `unit_id` | bigint | | FK → `settings_unit.id` | `unit_id` |
| `alias` | varchar | | Tên alias | `alias_id` |
| `system` | varchar | | Hệ thống dùng alias (e.g. `AFR`, `AMS_ACI`) | `system` |

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

### D2. `settings_charge_type` — Danh mục loại phí

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã phí — UNIQUE | `name` |
| `label` | varchar | | Tên phí (e.g. THC, B/L Fee, Origin CFS) | `label` |
| `localized_label` | varchar | | Tên bản địa | `local_label` |
| `charge_group` | varchar | | Nhóm phí (Origin, Freight, Destination, Other) | `charge_group` |

---

## Nhóm E — CRM / Phân loại đối tác

### E1. `settings_industry` — Ngành nghề

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã ngành — UNIQUE | `name` |
| `label` | varchar | | Tên ngành nghề | `label` |

### E2. `settings_sale_type` — Loại kinh doanh

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã loại — UNIQUE | `name` |
| `label` | varchar | | Tên (e.g. Direct, Agent, Co-loader) | `label` |

### E3. `settings_partner_source` — Nguồn đối tác

| Trường | Kiểu | Bắt buộc | Mô tả | BF1 Column |
|---|---|---|---|---|
| `id` | bigint | | PK | `id` |
| `code` | varchar | | Mã nguồn — UNIQUE | `name` |
| `label` | varchar | | Tên nguồn (e.g. Referral, Cold Call, Exhibition) | `label` |

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
