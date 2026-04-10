---
title: "Odoo — ERP & Kế toán"
tags:
  - datatp
  - odoo
  - accounting
---

## Odoo ERP — Development

### Develop

- **Activate ENV:** `source odoo14-venv/bin/activate`

### Cập nhật dữ liệu lên web server

```
ssh -p 30221 datatp@beescs-1.dev.datatp.net   # pass = Datatp!@#
ssh -p 30222 datatp@beescs-2.dev.datatp.net   # pass = Datatp!@#
```

Account beescs.com: `tuan08@gmail.com / DataTP@123`

- Connect qua ssh lên server → chạy run:clean → init data từ giao diện

### Ask

![[Screenshot_2022-12-07_at_17.17.08.png]]

- Hạch toán lương, hạch toán chi phí bảo hiểm trừ lương

---

## Docker & K8s Notes

Khái niệm: có 1 máy chủ ở bên ngoài, và nhiều máy ảo bên trong. Docker container không phải máy ảo thật — nhiều phần mềm nhóm chung lại, coi như một máy ảo.

```bash
cd namespaces/generic-server/production
vi k8s-config/

ssh -p 30231 datatp@datatp.cloud
```

Máy ảo (VirtualBox/Parallels) simulate máy ảo thật — có thể Windows trên Linux. Container thì máy ảo và máy chủ phải cùng kernel Linux.

![[Screenshot_2023-01-27_at_13.48.43.png]]

Địa chỉ mount trên máy thật: `/mnt/data/cloud/pv/generic-server/production/servers`

---

## Báo cáo kế toán

### Modify Depreciation Asset

- Lỗi dữ liệu tài sản: CC00028, sai bút toán liên kết.
- Lỗi dữ liệu tài sản: CC00117, sai bút toán liên kết.
- Chỉ modify nếu value_residual != 0

---

## HPS — Odoo Integration

### BFS DB

- PersonalProfile: thông tin bank của HPS

### Hướng dẫn công cụ dụng cụ, tài sản

Trong phần kế toán của Odoo có phần khấu hao tài sản.

Account datatp chị Loan: `hps.loanpt / hps.loanpt@123`

Đối chiếu lại các số tài khoản, khoản mục, sổ nhật ký.

HAIHAN2302004: job chị Mỹ sai invoice chi hộ

### Đẩy invoice từ phần mềm nghiệp vụ qua Odoo

- Không biết job nào xong, job nào chưa xong.
- Phần mềm mới là đẩy qua kế toán → xuất hoá đơn trên phần mềm kế toán.
- Hoá đơn bán đẩy trước vì phải xuất hoá đơn cho khách.
- Công nợ với agent và nhà cung cấp phải đợi confirm rồi mới đẩy sau (cuối tháng hoặc đẩy nhiều hoá đơn một lần).
- Cần lọc ra hoá đơn đã đẩy và chưa đẩy.

**Hoá đơn bán:** Lúc cần xuất thì đẩy → mặc định posted, không cho chỉnh sửa (người có quyền cao hơn mới chỉnh được). Vẫn phải đối chiếu lại với kế toán.

**Công nợ nhà cung cấp/agent:** Đẩy tuỳ thời điểm.

- Đánh dấu hoá đơn đã xuất.
- Hoá đơn customer yêu cầu xuất → chị xuất trước.

### Accountant — Quy trình đối soát

- Nhờ người nhập các báo nợ, báo có.
- Báo nợ liên quan đến hoá đơn mua/bán logistics có số tiền phát sinh bằng hoá đơn trên từng job → gạch luôn.
- Báo nợ/báo có khác (đại lý, Bee) — số tiền không khớp → chị tự đối soát.
- Hỗ trợ: số tài khoản, sổ nhật ký, khoản mục. Cấu hình kết chuyển.
- Tiếp: số dư đầu kỳ, kết chuyển KQKD tháng 1, chạy báo cáo đối chiếu.
- Đẩy dữ liệu tháng 2, đối chiếu (đối tác, tiền, sổ nhật ký, tài khoản, khoản mục).
- Tạo thanh toán tháng 2 → nhập bút toán admin → kết chuyển → xem báo cáo.

### Đối soát tháng 1

Doanh thu trên báo cáo KQKD bị lệch.

Chị Loan: gạch hoá đơn tháng 1, tháng 2 để chạy báo cáo.

---

## Kế toán — Bugs & Nghiệp vụ

### [Bug] Số liệu trước và sau kết chuyển không giống nhau

Nguyên tắc:
- Tài khoản đầu 5, 6, 7, 8 không có dư → hàng tháng phải kết chuyển để tính lãi lỗ.
- Lãi lỗ ghi vào tài khoản `421 - Lợi nhuận chưa phân phối năm nay`.
- Không kết chuyển trực tiếp mà qua tài khoản `911 - Tài khoản kết chuyển` (có thể nhiều level).

### Thanh toán hoá đơn — Chênh lệch tỷ giá

1. Tỷ giá hoá đơn > tỷ giá BN/BC:
   - Tạo bút toán chênh lệch ghi nhận doanh thu, link với HĐ.
   - Tài khoản phân tích lấy theo hoá đơn.
2. Tỷ giá hoá đơn < tỷ giá BN/BC:
   - Tạo bút toán chênh lệch ghi nhận chi phí, link với BN/BC.
   - Tài khoản phân tích lấy theo báo nợ, báo có.

![[Screenshot_2024-09-13_at_14.50.07.png]]

---

## Xem thêm

- [[datatp-datatp-overview]]
