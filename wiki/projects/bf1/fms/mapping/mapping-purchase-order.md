# Mapping: Purchase Order & Booking Process

> FMS-only — không có tương đương BF1
> CDC Handler: Chưa có

---

## of1_fms_purchase_order

> Mô hình PO mới, không có trong BF1

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `code` | varchar | Y | Mã đơn hàng — UNIQUE | | | |
| `order_date` | timestamp | | Ngày tạo đơn hàng (nghiệp vụ) | | | |
| `label` | varchar | | Tên đơn hàng | | | |
| `client_partner_id` | bigint | | FK — khách hàng | | | |
| `client_label` | varchar | | Tên khách hàng (denormalized) | | | |
| `assignee_account_id` | bigint | | FK — nhân viên phụ trách | | | |
| `assignee_label` | varchar | | Tên nhân viên phụ trách (denormalized) | | | |

---

## of1_fms_booking_process

> Không mapping với BF1. Bảng `BookingLocal` trong BF1 không tương đương trực tiếp.

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `code` | varchar | Y | Mã booking — UNIQUE | | | |
| `type_of_service` | varchar | | Loại dịch vụ | | | |
| `purchase_order_id` | bigint | | FK → of1_fms_purchase_order.id | | | |
| `state` | varchar | | Trạng thái | | | |
| `close_date` | timestamp | | Ngày đóng booking | | | |
