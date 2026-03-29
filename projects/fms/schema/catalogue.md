# Schema — Catalogue (Master Data)

Tài liệu mô tả schema các bảng master data dùng chung trong toàn hệ thống FMS: địa lý, tiền tệ, cảng/địa điểm, đối tác, và người dùng.

---

## GROUP A — Địa lý & Tiền tệ

### `settings_country` — Quốc gia (ISO 3166-1)

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `code` | varchar(2) | ✓ | Mã ISO 3166-1 alpha-2 (e.g. `VN`, `US`) — UNIQUE | |
| `code3` | varchar(3) | | Mã ISO 3166-1 alpha-3 (e.g. `VNM`) | |
| `label` | varchar | | Tên quốc gia tiếng Anh (uppercase) | |
| `localized_label` | varchar | | Tên bản địa | |
| `phone_code` | varchar(10) | | Mã điện thoại quốc tế (e.g. `+84`) | |
| `currency_code` | varchar(3) | | Mã tiền tệ mặc định | `settings_currency.code` |
| `address_format` | varchar | | Template định dạng địa chỉ theo quốc gia | |

**Sample data:**

| id | code | code3 | label | localized_label | phone_code | currency_code |
|---|---|---|---|---|---|---|
| 1 | `VN` | `VNM` | VIETNAM | Việt Nam | `+84` | `VND` |
| 2 | `US` | `USA` | UNITED STATES | Hoa Kỳ | `+1` | `USD` |

---

### `settings_currency` — Tiền tệ

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `code` | varchar(3) | ✓ | Mã ISO 4217 (e.g. `VND`, `USD`) — UNIQUE | |
| `label` | varchar | | Tên tiền tệ đầy đủ | |
| `symbol` | varchar(10) | | Ký hiệu (e.g. `đ`, `$`, `€`) | |
| `decimal_places` | int | | Số chữ số thập phân (VND=0, USD=2) | |
| `rounding` | double | | Đơn vị làm tròn | |

**Sample data:**

| id | code | label | symbol | decimal_places | rounding |
|---|---|---|---|---|---|
| 1 | `VND` | Vietnamese Dong | `đ` | 0 | 1.0 |
| 2 | `USD` | US Dollar | `$` | 2 | 0.01 |

---

### `settings_country_group` — Nhóm quốc gia

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `code` | varchar | ✓ | Mã nhóm (e.g. `ASEAN`, `EU`) — UNIQUE | |
| `label` | varchar | | Tên nhóm | |
| `parent_id` | bigint | | Hỗ trợ phân cấp nhóm | `settings_country_group.id` |

**Sample data:**

| id | code | label | parent_id |
|---|---|---|---|
| 1 | `ASEAN` | ASEAN Countries | null |
| 2 | `EU` | European Union | null |

---

## GROUP B — Cảng & Địa điểm

### `settings_location` — Địa điểm (Sân bay, Cảng, KCN, ...)

Bảng tổng hợp mọi loại địa điểm vật lý: sân bay, cảng biển, khu công nghiệp, tỉnh/thành, quận huyện, địa chỉ cụ thể.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `code` | varchar | ✓ | Mã nội bộ — UNIQUE | |
| `iata_code` | varchar(3) | | Mã IATA sân bay | |
| `un_locode` | varchar | | Mã UN/LOCODE cảng biển | |
| `label` | varchar | | Tên đầy đủ | |
| `short_label` | varchar | | Tên viết tắt | |
| `location_type` | varchar | | Phân loại địa điểm (xem enum bên dưới) | |
| `country_id` | bigint | | FK quốc gia | `settings_country.id` |
| `country_label` | varchar | | Tên quốc gia (denormalized) | |
| `state_id` | bigint | | FK tỉnh/bang | `settings_location_state.id` |
| `district_id` | bigint | | FK huyện/quận | `settings_location_district.id` |
| `subdistrict_id` | bigint | | FK phường/xã | `settings_location_subdistrict.id` |
| `latitude` | double | | Vĩ độ | |
| `longitude` | double | | Kinh độ | |
| `postal_code` | varchar | | Mã bưu chính | |
| `contact` | varchar | | Thông tin liên hệ | |

**Enum values — `location_type`:**

| Code | Mô tả |
|---|---|
| `Airport` | Sân bay |
| `Port` | Cảng biển |
| `KCN` | Khu công nghiệp |
| `State` | Tỉnh / Bang |
| `District` | Quận / Huyện |
| `Address` | Địa chỉ cụ thể |

**Sample data:**

| id | code | iata_code | un_locode | label | short_label | location_type | country_id | country_label |
|---|---|---|---|---|---|---|---|---|
| 1 | `SGN` | `SGN` | — | Tan Son Nhat International Airport | SGN | `Airport` | 1 | VIETNAM |
| 2 | `VNSGN` | — | `VNSGN` | Ho Chi Minh Port (Cat Lai) | Cat Lai | `Port` | 1 | VIETNAM |

---

## GROUP C — Đối tác

### `of1_fms_partner` — Đối tác / Khách hàng

Bảng trung tâm lưu trữ tất cả loại đối tác: khách hàng, hãng tàu/hãng bay (Carrier), đại lý (Agent), người gửi hàng (Shipper), người nhận hàng (Consignee), và các mối liên hệ khác.

**Định danh & phân loại:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `partner_code` | varchar | ✓ | Mã đối tác — UNIQUE (e.g. `CS016288`, `CN000138`) | |
| `category` | varchar | | Loại đối tác (xem enum bên dưới) | |
| `partner_group` | varchar | | Nhóm phân loại: `CUSTOMERS`, `AGENTS`, ... | |
| `scope` | varchar | | Phạm vi: `Domestic` / `International` | |
| `shareable` | varchar | | Khả năng chia sẻ: `PRIVATE` / `PUBLIC` | |
| `source` | varchar | | Hệ thống nguồn (e.g. `BEE`) | |
| `partner_source` | varchar | | Mạng lưới / kênh (e.g. `BEE_VN`) | `settings_partner_source.label` |
| `status` | varchar | | Trạng thái bổ sung (xem enum bên dưới) | |
| `storage_state` | varchar | | Vòng đời bản ghi (xem Audit Fields) | |

**Tên & địa chỉ:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `label` | varchar | | Tên tiếng Anh (uppercase) | |
| `localized_label` | varchar | | Tên tiếng Việt | |
| `name` | varchar | | Tên ngắn / tên in | |
| `address` | varchar | | Địa chỉ tiếng Anh | |
| `localized_address` | varchar | | Địa chỉ tiếng Việt | |
| `work_address` | varchar | | Địa chỉ làm việc | |
| `country_id` | bigint | | FK quốc gia | `settings_country.id` |
| `country_label` | varchar | | Tên quốc gia (denormalized) | |
| `province_id` | bigint | | FK tỉnh/bang | `settings_location_state.id` |
| `province_label` | varchar | | Tên tỉnh/bang (denormalized) | |
| `continent` | varchar | | Châu lục | |

**Liên hệ:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `email` | varchar | | Email | |
| `cell` | varchar | | Điện thoại di động | |
| `home_phone` | varchar | | Điện thoại nhà | |
| `work_phone` | varchar | | Điện thoại văn phòng | |
| `fax` | varchar | | Fax | |
| `personal_contact` | varchar | | Người liên hệ | |
| `vip_contact` | varchar | | Liên hệ VIP | |
| `vip_cellphone` | varchar | | SĐT VIP | |
| `vip_email` | varchar | | Email VIP | |
| `vip_position` | varchar | | Chức vụ VIP | |

**Tài chính & thuế:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `tax_code` | varchar | | Mã số thuế | |
| `swift_code` | varchar | | Mã SWIFT | |
| `bank_name` | varchar | | Tên ngân hàng | |
| `bank_accs_no` | varchar | | Số tài khoản | |
| `bank_address` | varchar | | Địa chỉ ngân hàng | |
| `bank_currency` | varchar | | Tiền tệ tài khoản | |
| `is_refund` | boolean | | Có hoàn tiền không | |

**Phân loại ngành & KCN:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `industry_code` | varchar | | Mã ngành nghề | `settings_industry.code` |
| `industry_label` | varchar | | Tên ngành (denormalized) | |
| `kcn_code` | varchar | | Mã khu công nghiệp | |
| `kcn_label` | varchar | | Tên khu công nghiệp | |
| `investment_origin` | varchar | | Nguồn vốn đầu tư | |

**Quản lý & phê duyệt:**

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `account_id` | bigint | | Account người phụ trách | |
| `sale_owner_account_id` | bigint | | Account sale phụ trách | |
| `sale_owner_full_name` | varchar | | Tên sale phụ trách | |
| `approved_by_account_id` | bigint | | Account duyệt | |
| `approved_by_full_name` | varchar | | Tên người duyệt | |
| `request_by_account_id` | bigint | | Account yêu cầu tạo | |
| `request_by_full_name` | varchar | | Tên người yêu cầu | |
| `group_name` | varchar | | Nhóm quản lý | |
| `bfsone_group_id` | bigint | | ID nhóm BFSOne | |
| `lead_code` | varchar | | Mã lead | |
| `date_created` | timestamp | | Ngày tạo nghiệp vụ | |
| `date_modified` | timestamp | | Ngày sửa nghiệp vụ | |
| `note` | varchar | | Ghi chú | |
| `warning_message` | varchar | | Cảnh báo hiển thị | |

**Enum values — `category` (loại đối tác):**

| Code | Mô tả |
|---|---|
| `CUSTOMER` | Khách hàng thực tế — trung tâm của giao dịch |
| `CARRIER` | Hãng tàu / hãng bay — thực hiện vận chuyển |
| `AGENT` | Đại lý — đại diện tại nước ngoài |
| `SHIPPER` | Người gửi hàng — xuất hiện trên vận đơn |
| `CONSIGNEE` | Người nhận hàng — xuất hiện trên vận đơn |
| `VENDOR` | Nhà cung cấp dịch vụ |
| `OTHER` | Liên hệ khác (hải quan, kho bãi, ...) |

**Enum values — `status` (trạng thái):**

| Code | Mô tả |
|---|---|
| `PUBLIC` | Hoạt động bình thường |
| `WARNING` | Đối tác có vấn đề — hiển thị cảnh báo khi chọn |
| `LOCK` | Bị khóa — không thể tạo giao dịch mới |

**Enum values — `storage_state`:**

| Code | Mô tả |
|---|---|
| `CREATED` | Mới tạo, chưa active |
| `ACTIVE` | Đang hoạt động |
| `INACTIVE` | Tạm ngừng hoạt động |
| `JUNK` | Rác, cần xử lý |
| `DEPRECATED` | Lỗi thời, không dùng nữa |
| `ARCHIVED` | Đã lưu trữ |

**Sample data:**

| id | partner_code | label | localized_label | category | tax_code | province_label | partner_source | status | storage_state |
|---|---|---|---|---|---|---|---|---|---|
| 34682 | `CS016288` | LAVERGNE VIETNAM CO LTD | Công ty TNHH Lavergne Việt Nam | `CUSTOMER` | `4000765976` | Quảng Nam | `BEE_VN` | `PUBLIC` | `ACTIVE` |
| 34700 | `CS016198` | HANESBRANDS VIETNAM CO., LTD-HUE BRANCH | CÔNG TY TNHH HANESBRANDS VIỆT NAM HUẾ | `CUSTOMER` | `3301559929` | Thừa Thiên Huế | `BEE_VN` | `PUBLIC` | `ACTIVE` |

---

## GROUP D — Người dùng

### `of1_fms_user_role` — Người dùng & phân quyền

Bảng lưu trữ tài khoản người dùng nội bộ và phân quyền theo vai trò trong hệ thống. Được dùng làm FK trong tất cả các bảng nghiệp vụ (người tạo lô, salesman, nhân viên ops, ...).

> Tương ứng với module **Departments** trong Catalogue UI — quản lý nhóm người dùng có thẩm quyền (Giám đốc, Kế toán trưởng, Trưởng phòng, ...).

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `username` | varchar | ✓ | Tên đăng nhập — UNIQUE | |
| `full_name` | varchar | | Họ và tên đầy đủ | |
| `email` | varchar | | Email công ty | |
| `role` | varchar | | Vai trò / chức danh (xem enum bên dưới) | |
| `branch_id` | bigint | | Chi nhánh phụ trách | |
| `branch_label` | varchar | | Tên chi nhánh (denormalized) | |
| `department` | varchar | | Phòng ban | |
| `is_active` | boolean | | Tài khoản đang hoạt động | |
| `storage_state` | varchar | | Vòng đời bản ghi | |

**Enum values — `role`:**

| Code | Mô tả |
|---|---|
| `DIRECTOR` | Giám đốc / Chủ tịch HĐQT |
| `CHIEF_ACCOUNTANT` | Kế toán trưởng |
| `MANAGER` | Trưởng phòng / Quản lý |
| `SALES` | Nhân viên kinh doanh (salesman) |
| `OPS` | Nhân viên vận hành (operations) |
| `ACCOUNTANT` | Nhân viên kế toán |
| `ADMIN` | Quản trị hệ thống |

**Sample data:**

| id | username | full_name | email | role | branch_label | is_active |
|---|---|---|---|---|---|---|
| 1001 | `admin.hcm` | Nguyễn Văn A | admin.hcm@company.vn | `ADMIN` | HCM Branch | true |
| 2605 | `linhtth.nd` | TRẦN THỊ HỒNG LINH | linhtth.nd@company.vn | `SALES` | Nam Định Branch | true |

---

## Audit Fields (áp dụng cho tất cả bảng)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `created_by` | varchar | Người tạo |
| `created_time` | timestamp | Thời điểm tạo |
| `modified_by` | varchar | Người sửa cuối |
| `modified_time` | timestamp | Thời điểm sửa cuối |
| `version` | int | Optimistic locking |
| `storage_state` | varchar | Vòng đời: `CREATED` / `ACTIVE` / `INACTIVE` / `JUNK` / `DEPRECATED` / `ARCHIVED` |

---

## Entity Relations

- `settings_currency` (1) ──── (N) `settings_country` (qua `currency_code`)
- `settings_country` (1) ──── (N) `settings_location` (qua `country_id`)
- `settings_country_group` (1) ──── (N) `settings_country_group` (self-ref qua `parent_id`)
- `settings_country` (M) ──── (N) `settings_country_group` (qua bảng `settings_country_group_rel`)
- `settings_location` referenced by `of1_fms_transactions.from_location_code` / `to_location_code` (POL/POD)
- `of1_fms_partner` (1) ──── (N) `of1_fms_house_bill` (as `client_partner_id`)
- `of1_fms_partner` referenced as `carrier_partner_id`, `shipper_partner_id`, `consignee_partner_id`, `handling_agent_partner_id` trong các bảng shipment
- `of1_fms_user_role` (1) ──── (N) `of1_fms_transactions` (as `created_by_account_id`)
- `of1_fms_user_role` referenced as `saleman_account_id`, `assignee_account_id`, `ops_account_id` trong `of1_fms_house_bill`

> Cross-reference: `of1_fms_partner` và `of1_fms_user_role` được dùng làm FK trong schema/sales.md, schema/documentation.md, schema/accounting.md.
