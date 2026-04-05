# Mapping: Transport Plan & Route

> FMS-only — không có tương đương BF1
> CDC Handler: Chưa có

---

## of1_fms_transport_plan

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | | FK → of1_fms_house_bill.id | | | |
| `booking_process_id` | bigint | | FK → of1_fms_booking.id | | | |
| `from_location_code` | varchar | | Điểm đi chặng đầu | | | |
| `from_location_label` | varchar | | Tên điểm đi (denormalized) | | | |
| `to_location_code` | varchar | | Điểm đến chặng cuối | | | |
| `to_location_label` | varchar | | Tên điểm đến (denormalized) | | | |
| `depart_time` | timestamp | | Giờ khởi hành (chặng đầu) | | | |
| `arrival_time` | timestamp | | Giờ đến (chặng cuối) | | | |
| `state` | varchar | | Trạng thái | | | |

---

## of1_fms_transport_route

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `transport_plan_id` | bigint | | FK → of1_fms_transport_plan.id | | | |
| `from_location_code` | varchar | | Mã điểm đi | | | |
| `from_location_label` | varchar | | Tên điểm đi (denormalized) | | | |
| `to_location_code` | varchar | | Mã điểm đến | | | |
| `to_location_label` | varchar | | Tên điểm đến (denormalized) | | | |
| `depart_time` | timestamp | | Giờ khởi hành | | | |
| `arrival_time` | timestamp | | Giờ đến | | | |
| `transport_no` | varchar | | Số chuyến / tàu / chuyến bay | | | |
| `transport_method_label` | varchar | | Phương tiện | | | |
| `carrier_partner_id` | bigint | | FK — hãng vận chuyển | | | |
| `carrier_label` | varchar | | Tên hãng vận chuyển (denormalized) | | | |
| `sort_order` | int | | Thứ tự chặng | | | |
