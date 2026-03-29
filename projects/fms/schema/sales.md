# Schema — Sales (Kinh doanh & Báo giá)

Tài liệu mô tả schema các bảng thuộc module Sales Executive: lịch tàu, database giá, báo giá, booking, và yêu cầu dịch vụ.

**Quy trình chính:**
```
Service Inquiry → Pricing DB → Quotation → Booking → Xác nhận → Mở file (Documentation)
```

---

## GROUP A — Lịch tàu

### `of1_fms_vessel_schedule` — Lịch tàu / Chuyến bay

Lưu trữ lịch chạy tàu và chuyến bay. Sales dùng để tra cứu và tư vấn khách hàng về ETD/ETA.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `service_type` | varchar | ✓ | Loại dịch vụ: `AIR` / `SEA_FCL` / `SEA_LCL` | |
| `vessel_name` | varchar | ✓ | Tên tàu / chuyến bay (e.g. `EVER GIVEN`, `VN601`) | |
| `voyage_no` | varchar | | Số chuyến / số hiệu chuyến bay | |
| `carrier_id` | bigint | ✓ | FK hãng tàu / hãng bay | `of1_fms_partner.id` |
| `carrier_label` | varchar | | Tên hãng vận chuyển (denormalized) | |
| `pol_code` | varchar | ✓ | Cảng xếp hàng (Port of Loading) | `settings_location.code` |
| `pol_label` | varchar | | Tên cảng xếp hàng (denormalized) | |
| `pod_code` | varchar | ✓ | Cảng dỡ hàng (Port of Discharge) | `settings_location.code` |
| `pod_label` | varchar | | Tên cảng dỡ hàng (denormalized) | |
| `etd` | timestamp | ✓ | Estimated Time of Departure | |
| `eta` | timestamp | | Estimated Time of Arrival | |
| `cutoff_date` | timestamp | | Thời hạn chốt hàng (cutoff) | |
| `transit_time` | int | | Thời gian vận chuyển (ngày) | |
| `status` | varchar | | Trạng thái: `ACTIVE` / `CANCELLED` / `DELAYED` | |
| `note` | varchar | | Ghi chú thêm | |

**Enum values — `status`:**

| Code | Mô tả |
|---|---|
| `ACTIVE` | Lịch đang hiệu lực |
| `CANCELLED` | Chuyến đã hủy |
| `DELAYED` | Chuyến bị hoãn |

**Sample data:**

| id | service_type | vessel_name | voyage_no | carrier_label | pol_code | pod_code | etd | eta | cutoff_date | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `SEA_FCL` | EVER ALOT | `0123E` | EVERGREEN | `VNSGN` | `CNSHA` | 2025-04-05 | 2025-04-20 | 2025-04-03 | `ACTIVE` |
| 2 | `AIR` | VN601 | `VN601` | VIETNAM AIRLINES CARGO | `SGN` | `NRT` | 2025-04-07 | 2025-04-08 | 2025-04-07 | `ACTIVE` |

---

## GROUP B — Database Giá

### `of1_fms_pricing` — Database giá vận chuyển

Lưu trữ giá mua từ hãng vận chuyển / nhà thầu phụ. Được dùng làm cơ sở tạo báo giá cho khách hàng. Hỗ trợ 3 loại: AirFreight, SeaFreight, Express.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `type` | varchar | ✓ | Loại giá: `AIR` / `SEA_FCL` / `SEA_LCL` / `EXPRESS` | |
| `carrier_id` | bigint | ✓ | FK hãng tàu / hãng bay / nhà thầu phụ | `of1_fms_partner.id` |
| `carrier_label` | varchar | | Tên hãng (denormalized) | |
| `pol_code` | varchar | ✓ | Cảng xếp hàng | `settings_location.code` |
| `pol_label` | varchar | | Tên cảng xếp hàng (denormalized) | |
| `pod_code` | varchar | ✓ | Cảng dỡ hàng | `settings_location.code` |
| `pod_label` | varchar | | Tên cảng dỡ hàng (denormalized) | |
| `valid_from` | date | ✓ | Ngày bắt đầu hiệu lực | |
| `valid_to` | date | ✓ | Ngày hết hiệu lực | |
| `currency` | varchar | ✓ | Tiền tệ (e.g. `USD`) | `settings_currency.code` |
| `rates` | jsonb | | Bảng giá theo loại container/trọng lượng (JSON) | |
| `surcharges` | jsonb | | Phụ phí bổ sung (BAF, CAF, THC, ...) (JSON) | |
| `status` | varchar | | Trạng thái: `ACTIVE` / `EXPIRED` / `DRAFT` | |
| `note` | varchar | | Ghi chú | |

> **Cấu trúc `rates` (jsonb):**
> - SEA_FCL: `{"20GP": 150, "40HQ": 280, "40HC": 280, "45HC": 310}` (USD/container)
> - SEA_LCL: `{"rate_per_cbm": 18, "min_charge": 50}` (USD/CBM)
> - AIR: `{"rate_per_kg": 2.5, "min_weight": 45}` (USD/kg)
> - EXPRESS: `{"rate_per_kg": 4.5, "min_charge": 30}` (USD/kg)

**Enum values — `type`:**

| Code | Mô tả |
|---|---|
| `AIR` | Hàng không (AirFreight) |
| `SEA_FCL` | Hàng biển nguyên container (FCL) |
| `SEA_LCL` | Hàng biển lẻ (LCL) |
| `EXPRESS` | Chuyển phát nhanh |

**Enum values — `status`:**

| Code | Mô tả |
|---|---|
| `DRAFT` | Chờ duyệt |
| `ACTIVE` | Đang hiệu lực |
| `EXPIRED` | Hết hiệu lực |

**Sample data:**

| id | type | carrier_label | pol_code | pod_code | valid_from | valid_to | currency | status |
|---|---|---|---|---|---|---|---|---|
| 101 | `SEA_FCL` | EVERGREEN | `VNSGN` | `CNSHA` | 2025-04-01 | 2025-06-30 | `USD` | `ACTIVE` |
| 102 | `AIR` | VIETNAM AIRLINES CARGO | `SGN` | `NRT` | 2025-04-01 | 2025-04-30 | `USD` | `ACTIVE` |

---

## GROUP C — Báo giá

### `of1_fms_quotation` — Báo giá khách hàng

Ghi nhận báo giá gửi cho khách hàng. Mỗi báo giá liên kết với 1 khách hàng, 1 tuyến POL→POD và có thời gian hiệu lực xác định.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `quotation_no` | varchar | ✓ | Mã báo giá — UNIQUE (e.g. `QUO-2025-00123`) | |
| `type` | varchar | ✓ | Loại báo giá: `AIR` / `SEA_FCL` / `SEA_LCL` / `EXPRESS` | |
| `customer_id` | bigint | ✓ | FK khách hàng | `of1_fms_partner.id` |
| `customer_label` | varchar | | Tên khách hàng (denormalized) | |
| `pol_code` | varchar | ✓ | Cảng xếp hàng | `settings_location.code` |
| `pol_label` | varchar | | Tên cảng xếp hàng (denormalized) | |
| `pod_code` | varchar | ✓ | Cảng dỡ hàng | `settings_location.code` |
| `pod_label` | varchar | | Tên cảng dỡ hàng (denormalized) | |
| `valid_from` | date | ✓ | Ngày bắt đầu hiệu lực | |
| `valid_to` | date | ✓ | Ngày hết hiệu lực | |
| `currency` | varchar | ✓ | Tiền tệ báo giá | `settings_currency.code` |
| `rates` | jsonb | | Bảng giá đề xuất cho khách (cùng cấu trúc với pricing.rates) | |
| `surcharges` | jsonb | | Phụ phí kèm theo | |
| `status` | varchar | | Trạng thái (xem enum bên dưới) | |
| `pricing_id` | bigint | | FK database giá tham chiếu (nullable) | `of1_fms_pricing.id` |
| `saleman_id` | bigint | | FK nhân viên kinh doanh phụ trách | `of1_fms_user_role.id` |
| `saleman_label` | varchar | | Tên nhân viên kinh doanh (denormalized) | |
| `note` | varchar | | Ghi chú nội bộ | |
| `created_by` | varchar | | Người tạo | |
| `created_time` | timestamp | | Thời điểm tạo | |

**Enum values — `status`:**

| Code | Mô tả |
|---|---|
| `DRAFT` | Nháp — chưa gửi khách |
| `SENT` | Đã gửi cho khách |
| `ACCEPTED` | Khách hàng chấp nhận |
| `REJECTED` | Khách hàng từ chối |
| `EXPIRED` | Hết hiệu lực |

**Sample data:**

| id | quotation_no | type | customer_label | pol_code | pod_code | valid_from | valid_to | currency | status |
|---|---|---|---|---|---|---|---|---|---|
| 501 | `QUO-2025-00501` | `SEA_FCL` | LAVERGNE VIETNAM CO LTD | `VNSGN` | `CNSHA` | 2025-04-01 | 2025-04-30 | `USD` | `SENT` |
| 502 | `QUO-2025-00502` | `AIR` | HANESBRANDS VIETNAM CO., LTD | `SGN` | `NRT` | 2025-04-05 | 2025-04-20 | `USD` | `ACCEPTED` |

---

## GROUP D — Booking

### `of1_fms_booking` — Booking request

Ghi nhận yêu cầu đặt chỗ từ khách hàng sau khi báo giá được chấp nhận. Sau khi xác nhận booking, hệ thống tạo `of1_fms_booking_process` để xử lý vận hành.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `booking_no` | varchar | ✓ | Mã booking — UNIQUE (e.g. `BK-2025-00789`) | |
| `type` | varchar | ✓ | Loại: `AIR` / `SEA_FCL` / `SEA_LCL` / `EXPRESS` / `INTERNAL` | |
| `quotation_id` | bigint | | FK báo giá tham chiếu (nullable) | `of1_fms_quotation.id` |
| `customer_id` | bigint | ✓ | FK khách hàng | `of1_fms_partner.id` |
| `customer_label` | varchar | | Tên khách hàng (denormalized) | |
| `carrier_id` | bigint | | FK hãng vận chuyển | `of1_fms_partner.id` |
| `carrier_label` | varchar | | Tên hãng vận chuyển (denormalized) | |
| `pol_code` | varchar | ✓ | Cảng xếp hàng | `settings_location.code` |
| `pol_label` | varchar | | Tên cảng xếp hàng (denormalized) | |
| `pod_code` | varchar | ✓ | Cảng dỡ hàng | `settings_location.code` |
| `pod_label` | varchar | | Tên cảng dỡ hàng (denormalized) | |
| `requested_etd` | timestamp | | ETD khách hàng yêu cầu | |
| `confirmed_etd` | timestamp | | ETD hãng vận chuyển xác nhận | |
| `cargo_description` | varchar | | Mô tả hàng hóa | |
| `cargo_weight` | double | | Trọng lượng ước tính (kg) | |
| `cargo_volume` | double | | Thể tích ước tính (CBM) | |
| `status` | varchar | | Trạng thái (xem enum bên dưới) | |
| `saleman_id` | bigint | | FK nhân viên kinh doanh | `of1_fms_user_role.id` |
| `saleman_label` | varchar | | Tên nhân viên kinh doanh (denormalized) | |
| `note` | varchar | | Ghi chú | |
| `created_by` | varchar | | Người tạo | |
| `created_time` | timestamp | | Thời điểm tạo | |

**Enum values — `status`:**

| Code | Mô tả |
|---|---|
| `PENDING` | Chờ xác nhận từ hãng |
| `CONFIRMED` | Đã xác nhận — có thể mở file |
| `CANCELLED` | Đã hủy |
| `CLOSED` | Đã đóng / đã mở file |

> **Lưu ý quy trình:**
> - AIR: Booking Request (PENDING) → Booking Confirm (CONFIRMED) — 2 bước
> - Sea / Internal: Internal Booking Request (1 bước, CONFIRMED ngay sau khi tạo)
> - Sau khi `CONFIRMED`, hệ thống tạo `of1_fms_booking_process` liên kết với `of1_fms_purchase_order`

**Sample data:**

| id | booking_no | type | customer_label | pol_code | pod_code | requested_etd | confirmed_etd | status |
|---|---|---|---|---|---|---|---|---|
| 701 | `BK-2025-00701` | `SEA_FCL` | LAVERGNE VIETNAM CO LTD | `VNSGN` | `CNSHA` | 2025-04-05 | 2025-04-05 | `CONFIRMED` |
| 702 | `BK-2025-00702` | `AIR` | HANESBRANDS VIETNAM CO., LTD | `SGN` | `NRT` | 2025-04-07 | 2025-04-08 | `PENDING` |

---

## GROUP E — Yêu cầu dịch vụ

### `of1_fms_service_inquiry` — Yêu cầu dịch vụ

Ghi nhận yêu cầu từ khách hàng trước khi tạo báo giá chính thức, hoặc yêu cầu điều chỉnh giá mua. Có quy trình duyệt riêng.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigserial | | PK | |
| `inquiry_no` | varchar | ✓ | Mã yêu cầu — UNIQUE (e.g. `INQ-2025-00045`) | |
| `customer_id` | bigint | ✓ | FK khách hàng | `of1_fms_partner.id` |
| `customer_label` | varchar | | Tên khách hàng (denormalized) | |
| `service_type` | varchar | ✓ | Loại dịch vụ: `AIR` / `SEA_FCL` / `SEA_LCL` / `EXPRESS` / `CUSTOMS_LOGISTICS` / `INLAND_TRUCKING` | |
| `origin` | varchar | | Điểm xuất phát | `settings_location.code` |
| `origin_label` | varchar | | Tên điểm xuất phát (denormalized) | |
| `destination` | varchar | | Điểm đến | `settings_location.code` |
| `destination_label` | varchar | | Tên điểm đến (denormalized) | |
| `cargo_type` | varchar | | Loại hàng hóa (General Cargo, Dangerous Goods, ...) | |
| `cargo_weight` | double | | Trọng lượng ước tính (kg) | |
| `cargo_volume` | double | | Thể tích ước tính (CBM) | |
| `requested_date` | date | | Ngày khách hàng muốn vận chuyển | |
| `status` | varchar | | Trạng thái (xem enum bên dưới) | |
| `quotation_id` | bigint | | FK báo giá được tạo từ inquiry này (nullable) | `of1_fms_quotation.id` |
| `notes` | varchar | | Ghi chú / yêu cầu đặc biệt | |
| `saleman_id` | bigint | | FK nhân viên kinh doanh phụ trách | `of1_fms_user_role.id` |
| `saleman_label` | varchar | | Tên nhân viên kinh doanh (denormalized) | |
| `created_by` | varchar | | Người tạo | |
| `created_time` | timestamp | | Thời điểm tạo | |

**Enum values — `status`:**

| Code | Mô tả |
|---|---|
| `OPEN` | Mới tiếp nhận, chưa xử lý |
| `IN_PROGRESS` | Đang xử lý / đang báo giá |
| `CONVERTED` | Đã tạo báo giá thành công |
| `CLOSED` | Đã đóng (không chuyển đổi được) |

**Sample data:**

| id | inquiry_no | customer_label | service_type | origin | destination | cargo_weight | requested_date | status |
|---|---|---|---|---|---|---|---|---|
| 201 | `INQ-2025-00201` | LAVERGNE VIETNAM CO LTD | `SEA_FCL` | `VNSGN` | `CNSHA` | 18000 | 2025-04-05 | `CONVERTED` |
| 202 | `INQ-2025-00202` | ABC ELECTRONICS VIETNAM | `AIR` | `SGN` | `ICN` | 500 | 2025-04-10 | `IN_PROGRESS` |

---

## Audit Fields

Tất cả các bảng trên kế thừa Audit Fields tiêu chuẩn (xem catalogue.md):

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

- `of1_fms_service_inquiry` (N) → `of1_fms_partner` (customer)
- `of1_fms_service_inquiry` (N) → `of1_fms_quotation` (khi chuyển đổi thành báo giá)
- `of1_fms_pricing` (N) → `of1_fms_partner` (carrier)
- `of1_fms_pricing` (N) → `settings_location` (POL/POD)
- `of1_fms_quotation` (N) → `of1_fms_partner` (customer)
- `of1_fms_quotation` (N) → `settings_location` (POL/POD)
- `of1_fms_quotation` (N) → `of1_fms_pricing` (tham chiếu giá gốc)
- `of1_fms_booking` (N) → `of1_fms_quotation`
- `of1_fms_booking` (N) → `of1_fms_partner` (customer)
- `of1_fms_booking` (N) → `of1_fms_partner` (carrier)
- `of1_fms_booking` (N) → `settings_location` (POL/POD)
- `of1_fms_vessel_schedule` (N) → `of1_fms_partner` (carrier)
- `of1_fms_vessel_schedule` (N) → `settings_location` (POL/POD)

> Cross-reference: xem schema/catalogue.md cho định nghĩa đầy đủ của partner và location.
> `of1_fms_booking.id` được dùng làm FK trong schema/documentation.md (transactions — qua `of1_fms_booking_process`).
