# Đề xuất Bộ Master Data — BF1 Cloud System

## Bối cảnh

Tài liệu này so sánh master data giữa hai hệ thống hiện tại và đề xuất bộ master data chuẩn cho BF1 Cloud:

| Hệ thống | DB | Engine | Ghi chú |
|---|---|---|---|
| **Cloud (datatpdb)** | `datatpdb` | PostgreSQL | Schema mới, đang phát triển |
| **OF1 (BEE_DB)** | `BEE_DB` | MSSQL | Hệ thống legacy, đang hoạt động |

---

## 1. So sánh Master Data Hiện Tại

### 1.1 Quốc gia (Country)

| Hạng mục | Cloud (datatpdb) | OF1 (BEE_DB) |
|---|---|---|
| Bảng chính | `settings_country` (250 rows) | `Countries` / `lst_Countries` / `lst_Country` (~250 rows) |
| Nhóm quốc gia | `settings_country_group` (27 rows) | `lst_Continents` (6), `lst_Regions` (23) |
| Mapping | `settings_country_group_rel` | — |
| Key field | `code` (ISO 2 ký tự) | — |
| Thông tin bổ sung | `phone_code`, `currency`, `address_format` | — |

**Nhận xét:** Cloud schema phong phú hơn — có nhóm quốc gia linh hoạt (hỗ trợ cây phân cấp), phone code, address format. OF1 chỉ có flat list + continent/region riêng.

---

### 1.2 Tiền tệ & Tỷ giá (Currency)

| Hạng mục | Cloud (datatpdb) | OF1 (BEE_DB) |
|---|---|---|
| Danh sách tiền tệ | `settings_currency` (19 rows) | `ExchangeRate` (19 rows) |
| Tỷ giá theo thời kỳ | `settings_currency_exchange_rate` (0 rows — chưa có data) | `CurrencyExchangeRate` (5,174 rows) |
| Chi tiết | `symbol`, `ext_usd`, `ext_vnd_sales`, `decimal_places`, `rounding` | — |

**Nhận xét:** OF1 đang dùng `CurrencyExchangeRate` với dữ liệu thực (5K+ rows). Cloud chưa populate `settings_currency_exchange_rate`. Cần migrate tỷ giá từ OF1 sang Cloud.

---

### 1.3 Địa điểm (Location)

| Hạng mục | Cloud (datatpdb) | OF1 (BEE_DB) |
|---|---|---|
| Tỉnh/bang | `settings_location_state` (5,070 rows) | `lst_States` (17 rows) |
| Thành phố | `settings_location_city` (1,389 rows) | `lst_Cities` (1,115 rows) |
| Huyện/quận | `settings_location_district` (706 rows) | — |
| Phường/xã | `settings_location_subdistrict` (13,923 rows) | — |
| Sân bay | `settings_location` (location_type=Airport) | `Airports` (15K) / `Airport_AIR` (1K) |
| Cảng biển | `settings_location` (location_type=Port) | — |
| Khu vực | — | `lst_Zone` (15) / `lst_Zone_Local` (27) |
| Tổng hợp | `settings_location` (40,647 rows) — đa năng | — |

**Nhận xét:** Cloud có cấu trúc địa lý hành chính chi tiết hơn nhiều. `settings_location` là bảng đa năng gộp nhiều loại địa điểm. OF1 có `Airports` lớn hơn (15K). Cần xem xét merge airport data.

---

### 1.4 Đơn vị đo lường (Unit of Measure)

| Hạng mục | Cloud (datatpdb) | OF1 (BEE_DB) |
|---|---|---|
| Đơn vị | `company_settings_unit` (172 rows) | `UnitContents` (145 rows) |
| Nhóm đơn vị | `company_settings_unit_group` (26 rows) | — |
| Alias | `company_settings_unit_alias` | — |
| Scope | Per `company_id` | Global |

**Nhận xét:** Cloud có nhóm đơn vị và alias — linh hoạt hơn. OF1 dùng global list đơn giản.

---

### 1.5 Master Data chỉ có trong OF1 (chưa có trong Cloud)

| Bảng OF1 | Mô tả | Ưu tiên đưa vào Cloud |
|---|---|---|
| `lst_Bank` (203) | Ngân hàng | **Cao** — dùng trong thanh toán |
| `VesselCode` (26,376) | Mã tàu biển | **Cao** — cần cho sea shipment |
| `Commodity` (96) | Loại hàng hóa | **Trung bình** |
| `lst_Service` (13) | Dịch vụ logistics | **Cao** |
| `lst_Mode` (8) | Phương thức vận chuyển | **Cao** — air/sea/truck/... |
| `lst_SaleType` (10) | Loại kinh doanh | **Trung bình** |
| `lst_Industries` (23) | Ngành nghề | **Thấp** |
| `lst_Source` (30) | Nguồn khách hàng | **Thấp** |
| `lst_Zone` / `lst_Zone_Local` | Khu vực địa lý | **Trung bình** |
| `TransactionType` (17) | Loại giao dịch | **Cao** |

---

## 2. Đề xuất Bộ Master Data Chuẩn

### Nhóm A — Địa lý & Quốc gia

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| A1 | `settings_country` | Cloud (giữ nguyên) | Đủ 250 quốc gia, có phone_code & address_format |
| A2 | `settings_country_group` | Cloud (giữ nguyên) | Cấu trúc linh hoạt hơn OF1 |
| A3 | `settings_country_group_rel` | Cloud (giữ nguyên) | Mapping country ↔ group |
| A4 | `settings_location` | Cloud (mở rộng) | Bảng đa năng — cần import airport từ OF1 |
| A5 | `settings_location_state` | Cloud (giữ nguyên) | 5K+ state records |
| A6 | `settings_location_city` | Cloud (giữ nguyên) | 1.3K cities |
| A7 | `settings_location_district` | Cloud (giữ nguyên) | 706 huyện |
| A8 | `settings_location_subdistrict` | Cloud (giữ nguyên) | 13.9K phường/xã |
| A9 | `settings_location_reference_code` | Cloud (giữ nguyên) | IATA/UNLOCODE reference |
| A10 | `settings_zone` *(mới)* | OF1: `lst_Zone` + `lst_Zone_Local` | Khu vực vận chuyển (cho pricing) |

### Nhóm B — Tiền tệ

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| B1 | `settings_currency` | Cloud (giữ nguyên) | Schema đầy đủ |
| B2 | `settings_currency_exchange_rate` | Migrate từ OF1: `CurrencyExchangeRate` | Cloud hiện trống — cần populate từ OF1 |

### Nhóm C — Đơn vị đo lường

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| C1 | `settings_unit` *(rename)* | Cloud: `company_settings_unit` → global | Bỏ `company_id` scope, chuyển thành global |
| C2 | `settings_unit_group` *(rename)* | Cloud: `company_settings_unit_group` | Giữ nhóm đơn vị |
| C3 | `settings_unit_alias` *(rename)* | Cloud: `company_settings_unit_alias` | Alias cho các hệ thống khác (AFR, AMS/ACI) |

### Nhóm D — Vận tải & Dịch vụ

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| D1 | `settings_transport_mode` *(mới)* | OF1: `lst_Mode` | Air / Sea FCL / Sea LCL / Truck / Rail |
| D2 | `settings_service_type` *(mới)* | OF1: `lst_Service` | Import / Export / Customs / ... |
| D3 | `settings_vessel` *(mới)* | OF1: `VesselCode` (26K) | Tàu biển — cần import |
| D4 | `settings_commodity` *(mới)* | OF1: `Commodity` | Loại hàng hóa |
| D5 | `settings_transaction_type` *(mới)* | OF1: `TransactionType` | Loại giao dịch vận chuyển |

### Nhóm E — Tài chính

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| E1 | `settings_bank` *(mới)* | OF1: `lst_Bank` (203) | Danh sách ngân hàng |
| E2 | `settings_charge_type` *(mới)* | OF1: `NameFeeDescription` (1,130) | Danh mục phí — quan trọng cho pricing |

### Nhóm F — CRM / Phân loại

| # | Bảng đề xuất | Nguồn | Ghi chú |
|---|---|---|---|
| F1 | `settings_sale_type` *(mới)* | OF1: `lst_SaleType` | Loại kinh doanh |
| F2 | `settings_industry` *(mới)* | OF1: `lst_Industries` | Ngành nghề đối tác |
| F3 | `settings_partner_source` *(mới)* | OF1: `lst_Source` | Nguồn đối tác |

---

## 3. Kế hoạch Migration / Khởi tạo Data

### Ưu tiên Cao (cần có trước khi go-live)

| STT | Việc cần làm | Nguồn → Đích |
|---|---|---|
| 1 | Import airport data vào `settings_location` | `Airports` (OF1) → Cloud |
| 2 | Populate `settings_currency_exchange_rate` | `CurrencyExchangeRate` (OF1) → Cloud |
| 3 | Tạo & import `settings_transport_mode` | `lst_Mode` (OF1) → Cloud |
| 4 | Tạo & import `settings_service_type` | `lst_Service` (OF1) → Cloud |
| 5 | Tạo & import `settings_transaction_type` | `TransactionType` (OF1) → Cloud |
| 6 | Tạo & import `settings_bank` | `lst_Bank` (OF1) → Cloud |
| 7 | Tạo & import `settings_charge_type` | `NameFeeDescription` (OF1) → Cloud |

### Ưu tiên Trung bình

| STT | Việc cần làm | Nguồn → Đích |
|---|---|---|
| 8 | Tạo & import `settings_vessel` | `VesselCode` (OF1) → Cloud |
| 9 | Tạo & import `settings_commodity` | `Commodity` (OF1) → Cloud |
| 10 | Tạo & import `settings_zone` | `lst_Zone` + `lst_Zone_Local` (OF1) → Cloud |
| 11 | Rename `company_settings_unit` → global `settings_unit` | Cloud internal refactor |

### Ưu tiên Thấp

| STT | Việc cần làm | Ghi chú |
|---|---|---|
| 12 | Tạo `settings_sale_type`, `settings_industry`, `settings_partner_source` | CRM lookup tables |

---

## 4. Điểm cần làm rõ

| # | Câu hỏi | Lý do cần biết |
|---|---|---|
| Q1 | `company_settings_unit` scoped theo `company_id` — có giữ scope hay chuyển global? | Ảnh hưởng đến thiết kế multi-tenant |
| Q2 | `settings_location` đã có airport VN chưa, hay cần import từ `Airports` (15K)? | Tránh duplicate |
| Q3 | Tỷ giá sẽ do Cloud quản lý hay vẫn đồng bộ từ OF1? | Quyết định architecture `settings_currency_exchange_rate` |
| Q4 | `VesselCode` (26K rows) — có cần real-time sync với database tàu quốc tế không? | Ảnh hưởng đến strategy update |
| Q5 | `NameFeeDescription` trong OF1 là charge catalog chung hay per-company? | Cần biết để thiết kế bảng Cloud tương đương |

---

## 5. Tóm tắt

| Nhóm | Trạng thái hiện tại | Hành động |
|---|---|---|
| Quốc gia | ✅ Cloud đủ | Giữ nguyên |
| Tiền tệ | ⚠️ Cloud thiếu tỷ giá | Import từ OF1 |
| Địa điểm | ⚠️ Cloud thiếu airport đầy đủ | Merge từ OF1 |
| Đơn vị đo | ✅ Cloud đủ | Cân nhắc bỏ company_id scope |
| Vận tải/Dịch vụ | ❌ Cloud chưa có | Tạo mới + import OF1 |
| Tài chính | ❌ Cloud chưa có | Tạo mới + import OF1 |
| CRM | ❌ Cloud chưa có | Tạo mới (ưu tiên thấp) |
