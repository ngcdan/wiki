# Schema — Accounting (Kế toán & Tài chính)

Tài liệu mô tả schema các bảng kế toán trong FMS: hoá đơn điện tử, lịch sử thanh toán, tạm ứng, P/L sheet, và chi tiết thu/chi.

---

## GROUP A — Hoá đơn & Thanh toán

### `of1_fms_invoice` — Hoá đơn điện tử (VAT Invoice / Debit Note / Credit Note)

Lưu trữ thông tin hoá đơn xuất cho Customer, Agent, Carrier từ Debit/Credit Note của file vận đơn. Vòng đời: Draft → Issued → Paid.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `invoice_no` | varchar(50) | ✓ | Số hoá đơn — UNIQUE | |
| `transaction_id` | bigint | ✓ | Liên kết lô hàng/file | `of1_fms_transactions.id` |
| `house_bill_id` | bigint | | Liên kết vận đơn nhà (HAWB/HBL) | |
| `partner_id` | bigint | ✓ | Khách hàng / Agent / Carrier nhận hoá đơn | `of1_fms_partner.id` |
| `invoice_type` | varchar(20) | ✓ | Loại hoá đơn: `VAT` / `DEBIT_NOTE` / `CREDIT_NOTE` | |
| `amount` | numeric(18,2) | ✓ | Tiền trước thuế | |
| `currency` | varchar(3) | ✓ | Mã tiền tệ (VD: `VND`, `USD`) | |
| `tax_rate` | numeric(5,2) | | Thuế suất VAT (%) — VD: `10.00` | |
| `tax_amount` | numeric(18,2) | | Tiền thuế VAT | |
| `total_amount` | numeric(18,2) | ✓ | Tổng tiền (amount + tax_amount) | |
| `status` | varchar(20) | ✓ | Trạng thái hoá đơn (xem enum bên dưới) | |
| `issued_date` | date | | Ngày phát hành hoá đơn | |
| `due_date` | date | | Ngày đến hạn thanh toán | |
| `created_by` | bigint | | Người tạo | |
| `created_at` | timestamptz | ✓ | Thời điểm tạo | |

**Enum — `invoice_type`:**

| Code | Mô tả |
|---|---|
| `VAT` | Hoá đơn giá trị gia tăng thông thường |
| `DEBIT_NOTE` | Debit Note — phát sinh thêm chi phí |
| `CREDIT_NOTE` | Credit Note — giảm trừ / hoàn tiền |

**Enum — `status`:**

| Code | Mô tả |
|---|---|
| `DRAFT` | Nháp (màu trắng) — chưa phát hành |
| `ISSUED` | Đã phát hành (màu hồng) — chờ thanh toán |
| `PAID` | Đã thanh toán đủ (màu xanh) |
| `PARTIAL_PAID` | Thanh toán một phần |
| `CANCELLED` | Đã huỷ (bị Replace bằng hoá đơn mới) |
| `OVERDUE` | Quá hạn thanh toán |

**Sample data:**

| id | invoice_no | transaction_id | partner_id | invoice_type | amount | currency | tax_rate | tax_amount | total_amount | status | issued_date | due_date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `INV-2025-00001` | 101 | 5 | `VAT` | 10000000 | `VND` | 10.00 | 1000000 | 11000000 | `ISSUED` | 2025-03-01 | 2025-03-31 |
| 2 | `INV-2025-00002` | 102 | 8 | `DEBIT_NOTE` | 500.00 | `USD` | 0.00 | 0.00 | 500.00 | `PAID` | 2025-03-05 | 2025-04-04 |
| 3 | `INV-2025-00003` | 103 | 5 | `CREDIT_NOTE` | 200.00 | `USD` | 0.00 | 0.00 | 200.00 | `DRAFT` | null | null |

---

### `of1_fms_payment` — Lịch sử thanh toán (History of Payment)

Ghi nhận từng lần thanh toán của đối tác cho một hoá đơn. Một hoá đơn có thể có nhiều lần thanh toán (partial payment).

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `payment_no` | varchar(50) | ✓ | Số phiếu thu — UNIQUE | |
| `invoice_id` | bigint | ✓ | Hoá đơn được thanh toán | `of1_fms_invoice.id` |
| `partner_id` | bigint | ✓ | Đối tác thanh toán | `of1_fms_partner.id` |
| `amount` | numeric(18,2) | ✓ | Số tiền đã thanh toán | |
| `currency` | varchar(3) | ✓ | Mã tiền tệ | |
| `payment_date` | date | ✓ | Ngày thanh toán | |
| `payment_method` | varchar(20) | ✓ | Phương thức thanh toán (xem enum) | |
| `reference_no` | varchar(100) | | Số tham chiếu (số giao dịch ngân hàng, số séc, ...) | |
| `notes` | text | | Ghi chú thêm | |
| `created_by` | bigint | | Người nhập | |
| `created_at` | timestamptz | ✓ | Thời điểm tạo | |

**Enum — `payment_method`:**

| Code | Mô tả |
|---|---|
| `BANK_TRANSFER` | Chuyển khoản ngân hàng |
| `CASH` | Tiền mặt |
| `CHECK` | Séc ngân hàng |

**Sample data:**

| id | payment_no | invoice_id | partner_id | amount | currency | payment_date | payment_method | reference_no |
|---|---|---|---|---|---|---|---|---|
| 1 | `PAY-2025-00001` | 1 | 5 | 5000000 | `VND` | 2025-03-15 | `BANK_TRANSFER` | `VCB20250315001` |
| 2 | `PAY-2025-00002` | 1 | 5 | 6000000 | `VND` | 2025-03-28 | `BANK_TRANSFER` | `VCB20250328002` |
| 3 | `PAY-2025-00003` | 2 | 8 | 500.00 | `USD` | 2025-03-20 | `BANK_TRANSFER` | `ACB20250320001` |

---

## GROUP B — Tạm ứng & Giải trình

### `of1_fms_advance_request` — Tạm ứng (Advance Request)

Quản lý yêu cầu tạm ứng tiền mặt của nhân viên vận hành (OP) để thanh toán chi phí phát sinh trong quá trình xử lý lô hàng. Sau khi giải trình, chi phí tự động nhập vào Logistics Charges của file.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `request_no` | varchar(50) | ✓ | Số phiếu tạm ứng — UNIQUE | |
| `transaction_id` | bigint | ✓ | Lô hàng liên quan | `of1_fms_transactions.id` |
| `requested_by` | bigint | ✓ | Nhân viên yêu cầu tạm ứng | |
| `amount` | numeric(18,2) | ✓ | Số tiền tạm ứng | |
| `currency` | varchar(3) | ✓ | Mã tiền tệ | |
| `purpose` | text | ✓ | Mục đích tạm ứng (chi phí gì, cho hàng nào) | |
| `status` | varchar(20) | ✓ | Trạng thái (xem enum) | |
| `approved_by` | bigint | | Người duyệt | |
| `approved_at` | timestamptz | | Thời điểm duyệt | |
| `settled_at` | timestamptz | | Thời điểm giải trình xong | |
| `created_at` | timestamptz | ✓ | Thời điểm tạo | |

**Enum — `status`:**

| Code | Mô tả |
|---|---|
| `PENDING` | Chờ duyệt |
| `APPROVED` | Đã duyệt — chờ giải trình |
| `REJECTED` | Từ chối |
| `SETTLED` | Đã giải trình xong, chi phí đã vào file |

**Sample data:**

| id | request_no | transaction_id | requested_by | amount | currency | purpose | status | approved_by | approved_at |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `ADV-2025-00001` | 101 | 12 | 2000000 | `VND` | Phí cước địa phương hãng tàu lô HCM-SGN | `APPROVED` | 3 | 2025-03-02 08:30:00+07 |
| 2 | `ADV-2025-00002` | 102 | 15 | 150.00 | `USD` | Airport handling fee tại NBIA | `SETTLED` | 3 | 2025-03-06 09:00:00+07 |
| 3 | `ADV-2025-00003` | 104 | 12 | 500000 | `VND` | Chi phí xếp dỡ cảng Cát Lái | `PENDING` | null | null |

---

## GROUP C — P/L & Chi tiết thu/chi

### `of1_fms_pl_sheet` — P/L Sheet (Báo cáo Lợi nhuận / Lỗ)

Tổng hợp lợi nhuận/lỗ của từng lô hàng sau khi đối chiếu toàn bộ doanh thu (Selling Rate) và chi phí (Buying Rate). Được tính tự động khi file hoàn tất.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `transaction_id` | bigint | ✓ | Lô hàng — UNIQUE (1 lô 1 P/L) | `of1_fms_transactions.id` |
| `house_bill_id` | bigint | | House Bill liên quan (nếu tính riêng theo HBL) | |
| `revenue_amount` | numeric(18,2) | ✓ | Tổng doanh thu (Selling Rate) | |
| `cost_amount` | numeric(18,2) | ✓ | Tổng chi phí (Buying Rate) | |
| `profit_amount` | numeric(18,2) | ✓ | Lợi nhuận = revenue_amount - cost_amount | |
| `currency` | varchar(3) | ✓ | Tiền tệ quy đổi (thường là `VND`) | |
| `exchange_rate` | numeric(18,6) | | Tỷ giá quy đổi tại thời điểm tính | |
| `calculated_at` | timestamptz | ✓ | Thời điểm tính P/L | |

**Sample data:**

| id | transaction_id | revenue_amount | cost_amount | profit_amount | currency | exchange_rate | calculated_at |
|---|---|---|---|---|---|---|---|
| 1 | 101 | 25000000 | 18000000 | 7000000 | `VND` | 1.0 | 2025-03-31 10:00:00+07 |
| 2 | 102 | 1200.00 | 950.00 | 250.00 | `USD` | 25450.0 | 2025-03-31 10:05:00+07 |
| 3 | 103 | 32000000 | 35000000 | -3000000 | `VND` | 1.0 | 2025-03-31 10:10:00+07 |

---

### `of1_fms_cost_revenue` — Chi tiết Thu/Chi (Cost & Revenue Entries)

Ghi nhận từng dòng thu/chi của lô hàng (Selling Rate / Buying Rate / Logistics Charges). Là nguồn dữ liệu để tổng hợp P/L Sheet và xuất Debit/Credit Note.

| Trường | Kiểu | Bắt buộc | Mô tả | FK |
|---|---|---|---|---|
| `id` | bigint | | PK | |
| `transaction_id` | bigint | ✓ | Lô hàng liên quan | `of1_fms_transactions.id` |
| `house_bill_id` | bigint | | House Bill liên quan (nếu tách theo HBL) | |
| `entry_type` | varchar(10) | ✓ | Loại: `REVENUE` (thu) hoặc `COST` (chi) | |
| `category` | varchar(100) | ✓ | Nhóm phí (VD: `OCEAN_FREIGHT`, `HANDLING`, `CUSTOMS`, `LOCAL_CHARGES`) | |
| `description` | varchar(255) | | Diễn giải chi tiết | |
| `amount` | numeric(18,2) | ✓ | Số tiền | |
| `currency` | varchar(3) | ✓ | Mã tiền tệ | |
| `partner_id` | bigint | | Đối tác liên quan (hãng tàu, đại lý, nhà cung cấp) | `of1_fms_partner.id` |
| `invoice_id` | bigint | | Hoá đơn đã xuất cho dòng này (nếu có) | `of1_fms_invoice.id` |
| `created_by` | bigint | | Người nhập | |
| `created_at` | timestamptz | ✓ | Thời điểm tạo | |

**Enum — `entry_type`:**

| Code | Mô tả |
|---|---|
| `REVENUE` | Khoản thu (Selling Rate — thu từ khách hàng) |
| `COST` | Khoản chi (Buying Rate — chi cho hãng tàu, đại lý, nhà cung cấp) |

**Sample data:**

| id | transaction_id | entry_type | category | description | amount | currency | partner_id | invoice_id |
|---|---|---|---|---|---|---|---|---|
| 1 | 101 | `REVENUE` | `OCEAN_FREIGHT` | Ocean Freight - KH ABC Corp | 15000000 | `VND` | 5 | 1 |
| 2 | 101 | `REVENUE` | `LOCAL_CHARGES` | THC + Documentation fee | 5000000 | `VND` | 5 | 1 |
| 3 | 101 | `COST` | `OCEAN_FREIGHT` | Cước hãng tàu Evergreen | 12000000 | `VND` | 22 | null |
| 4 | 101 | `COST` | `HANDLING` | Phí xếp dỡ cảng Cát Lái | 2500000 | `VND` | 30 | null |
| 5 | 102 | `REVENUE` | `AIR_FREIGHT` | Air Freight SGN-ICN | 800.00 | `USD` | 8 | 2 |
| 6 | 102 | `COST` | `AIR_FREIGHT` | Cước hãng bay Vietnam Airlines | 650.00 | `USD` | 25 | null |

---

## Entity Relations

- `of1_fms_transactions` (1) → (N) `of1_fms_invoice`
- `of1_fms_invoice` (1) → (N) `of1_fms_payment`
- `of1_fms_transactions` (1) → (N) `of1_fms_cost_revenue`
- `of1_fms_transactions` (1) → (1) `of1_fms_pl_sheet`
- `of1_fms_transactions` (1) → (N) `of1_fms_advance_request`
- `of1_fms_invoice` (N) → (1) `of1_fms_partner` (customer / agent / carrier)
- `of1_fms_payment` (N) → (1) `of1_fms_partner`
- `of1_fms_cost_revenue` (N) → (1) `of1_fms_partner`
- `of1_fms_cost_revenue` (N) → (1) `of1_fms_invoice` (khi dòng thu/chi đã xuất hoá đơn)

> Cross-reference: `of1_fms_transactions` được định nghĩa trong `schema/documentation.md`
> `of1_fms_partner` được định nghĩa trong `schema/catalogue.md`
