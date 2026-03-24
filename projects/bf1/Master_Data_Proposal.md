# Đề xuất Bộ Master Data — BF1 Cloud System

> Tài liệu đề xuất cấu trúc schema và các trường dữ liệu cho bộ master data của hệ thống BF1 Cloud.
> Nguồn tham khảo: `Cloud_DB_Schema.md` (datatpdb) và `OF1_DB_Schema.md` (BEE_DB).

---

## Nhóm A — Quốc gia & Khu vực

### A1. `settings_country` — Quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar(2) | | Mã ISO 3166-1 alpha-2 (e.g. `VN`, `US`) — UNIQUE |
| `code3` | varchar(3) | | Mã ISO 3166-1 alpha-3 (e.g. `VNM`) |
| `label` | varchar | | Tên quốc gia (tiếng Anh, uppercase) |
| `label_local` | varchar | | Tên bản địa |
| `phone_code` | varchar(10) | | Mã điện thoại quốc tế (e.g. `+84`) |
| `currency_code` | varchar(3) | | Mã tiền tệ mặc định (FK → `settings_currency.code`) |
| `address_format` | varchar | | Template định dạng địa chỉ theo quốc gia |
| `is_active` | boolean | | Đang sử dụng |

### A2. `settings_country_group` — Nhóm quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã nhóm (e.g. `ASEAN`, `EU`) — UNIQUE |
| `label` | varchar | | Tên nhóm |
| `parent_id` | bigint | | FK → `settings_country_group.id` (hỗ trợ phân cấp) |
| `is_active` | boolean | | Đang sử dụng |

### A3. `settings_country_group_rel` — Mapping quốc gia ↔ nhóm

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `country_id` | bigint | | FK → `settings_country.id` |
| `group_id` | bigint | | FK → `settings_country_group.id` |

### A4. `settings_zone` — Khu vực vận chuyển

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã khu vực — UNIQUE |
| `label` | varchar | | Tên khu vực |
| `zone_type` | varchar | | Phân loại: `global`, `local`, `custom` |
| `is_active` | boolean | | Đang sử dụng |

---

## Nhóm B — Địa lý Hành chính

### B1. `settings_location_state` — Tỉnh / Bang

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã định danh — UNIQUE |
| `label` | varchar | | Tên tỉnh/bang |
| `country_id` | bigint | | FK → `settings_country.id` |
| `country_code` | varchar(2) | | Denormalized |
| `gov_code` | varchar | | Mã hành chính nhà nước |
| `administrative_unit` | varchar | | Loại đơn vị (Tỉnh, Thành phố trực thuộc TW) |

### B2. `settings_location_district` — Huyện / Quận

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã định danh — UNIQUE |
| `label` | varchar | | Tên huyện/quận |
| `state_id` | bigint | | FK → `settings_location_state.id` |
| `state_label` | varchar | | Denormalized |
| `gov_code` | varchar | | Mã hành chính nhà nước |
| `administrative_unit` | varchar | | Loại đơn vị (Huyện, Quận, Thị xã) |

### B3. `settings_location_subdistrict` — Phường / Xã

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã định danh — UNIQUE |
| `label` | varchar | | Tên phường/xã |
| `district_id` | bigint | | FK → `settings_location_district.id` |
| `district_label` | varchar | | Denormalized |
| `state_id` | bigint | | FK → `settings_location_state.id` |
| `state_label` | varchar | | Denormalized |
| `gov_code` | varchar | | Mã hành chính nhà nước |
| `administrative_unit` | varchar | | Loại đơn vị (Phường, Xã, Thị trấn) |
| `postal_code` | varchar | | Mã bưu chính |

---

## Nhóm C — Địa điểm Logistics

### C1. `settings_location` — Địa điểm (Sân bay, Cảng, KCN, ...)

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã nội bộ — UNIQUE |
| `iata_code` | varchar(3) | | Mã IATA sân bay |
| `un_locode` | varchar | | Mã UN/LOCODE cảng biển |
| `label` | varchar | | Tên đầy đủ |
| `short_label` | varchar | | Tên viết tắt |
| `location_type` | varchar | | `Airport` / `Port` / `KCN` / `State` / `District` / `Address` |
| `country_id` | bigint | | FK → `settings_country.id` |
| `country_label` | varchar | | Denormalized |
| `state_id` | bigint | | FK → `settings_location_state.id` |
| `district_id` | bigint | | FK → `settings_location_district.id` |
| `subdistrict_id` | bigint | | FK → `settings_location_subdistrict.id` |
| `latitude` | double | | Vĩ độ |
| `longitude` | double | | Kinh độ |
| `postal_code` | varchar | | Mã bưu chính |
| `contact` | varchar | | Thông tin liên hệ |
| `is_active` | boolean | | Đang hoạt động |

### C2. `settings_location_reference_code` — Mã tham chiếu bổ sung

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `location_id` | bigint | | FK → `settings_location.id` |
| `code` | varchar | | Giá trị mã |
| `code_type` | varchar | | Loại mã: `IATA`, `UNLOCODE`, `CAN_CODE`, `AUS_CODE`, `US_CODE`, ... |

---

## Nhóm D — Tiền tệ & Tỷ giá

### D1. `settings_currency` — Tiền tệ

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar(3) | | Mã ISO 4217 (e.g. `VND`, `USD`) — UNIQUE |
| `label` | varchar | | Tên tiền tệ |
| `symbol` | varchar(10) | | Ký hiệu (e.g. `đ`, `$`, `€`) |
| `decimal_places` | int | | Số chữ số thập phân (VND=0, USD=2) |
| `rounding` | double | | Đơn vị làm tròn |
| `is_active` | boolean | | Đang sử dụng |

### D2. `settings_currency_exchange_rate` — Tỷ giá theo thời kỳ

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `currency_id` | bigint | | FK → `settings_currency.id` |
| `base_currency_id` | bigint | | Tiền tệ cơ sở (thường là USD hoặc VND) |
| `rate` | decimal(20,6) | | Tỷ giá |
| `valid_from` | timestamp | | Ngày bắt đầu hiệu lực |
| `valid_to` | timestamp | | Ngày kết thúc hiệu lực (null = còn hiệu lực) |
| `source` | varchar | | Nguồn tỷ giá (e.g. `SBV`, `manual`) |

---

## Nhóm E — Đơn vị đo lường

### E1. `settings_unit_group` — Nhóm đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã nhóm (e.g. `weight`, `volume`, `quantity`) — UNIQUE |
| `label` | varchar | | Tên nhóm |

### E2. `settings_unit` — Đơn vị đo

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã đơn vị (e.g. `KGM`, `MTQ`) — UNIQUE |
| `label` | varchar | | Tên hiển thị (e.g. `kg(s)`, `cbm`) |
| `group_id` | bigint | | FK → `settings_unit_group.id` |
| `iso_code` | varchar | | Mã ISO |
| `scale` | double | | Tỷ lệ quy đổi về đơn vị chuẩn của nhóm |
| `description` | varchar | | Mô tả tiếng Việt |
| `description_en` | varchar | | Mô tả tiếng Anh |
| `is_active` | boolean | | Đang sử dụng |

### E3. `settings_unit_alias` — Bí danh đơn vị

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `unit_id` | bigint | | FK → `settings_unit.id` |
| `alias` | varchar | | Tên alias |
| `system` | varchar | | Hệ thống dùng alias (e.g. `AFR`, `AMS_ACI`) |

---

## Nhóm F — Hàng hóa

### F1. `settings_commodity` — Loại hàng hóa

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã hàng hóa — UNIQUE |
| `label` | varchar | | Tên hàng hóa |
| `hs_code` | varchar | | Mã HS code |
| `is_dangerous` | boolean | | Hàng nguy hiểm |
| `is_active` | boolean | | Đang sử dụng |

---

## Nhóm G — Tài chính

### G1. `settings_bank` — Ngân hàng

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã ngân hàng — UNIQUE |
| `swift_code` | varchar | | Mã SWIFT/BIC |
| `label` | varchar | | Tên đầy đủ |
| `short_label` | varchar | | Tên viết tắt |
| `country_id` | bigint | | FK → `settings_country.id` |
| `is_active` | boolean | | Đang hoạt động |

### G2. `settings_charge_type` — Danh mục loại phí

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã phí — UNIQUE |
| `label` | varchar | | Tên phí (e.g. THC, B/L Fee, Origin CFS) |
| `label_en` | varchar | | Tên tiếng Anh |
| `charge_group` | varchar | | Nhóm phí (Origin, Freight, Destination, Other) |
| `is_buying` | boolean | | Áp dụng cho giá mua |
| `is_selling` | boolean | | Áp dụng cho giá bán |
| `is_active` | boolean | | Đang sử dụng |

---

## Nhóm H — CRM / Phân loại đối tác

### H1. `settings_industry` — Ngành nghề

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã ngành — UNIQUE |
| `label` | varchar | | Tên ngành nghề |
| `is_active` | boolean | | Đang sử dụng |

### H2. `settings_sale_type` — Loại kinh doanh

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã loại — UNIQUE |
| `label` | varchar | | Tên (e.g. Direct, Agent, Co-loader) |
| `is_active` | boolean | | Đang sử dụng |

### H3. `settings_partner_source` — Nguồn đối tác

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | bigint | | PK |
| `code` | varchar | | Mã nguồn — UNIQUE |
| `label` | varchar | | Tên nguồn (e.g. Referral, Cold Call, Exhibition) |
| `is_active` | boolean | | Đang sử dụng |

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
