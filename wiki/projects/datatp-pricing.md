---
title: "Pricing — Features & Enhancement"
tags:
  - datatp
  - pricing
  - api
---

## Pricing Tools Enhancement

1. Siết chặt các chức năng upload, xoá giá.
Không chỉnh sửa giá, chỉ cho phép copy sửa xong và archive dòng cũ đi. save xong e mở thêm màn hình message confirm cho user chọn archive hoặc ko.

```json

```

2. Group `partnerIndices` theo `partnerSource`
3. Với source `CRM_LEAD`: fetch từ **CustomerLeads**
4. Với các source khác (BEE partners): fetch từ **CRMPartner**
5. Collect thành `SqlMapRecord` theo cấu trúc comment, để `"N/A"` cho các field chưa có

---

## Search giá Trucking HCM


### **Mô tả công việc:**

- Excel Template:  https://adminbeelogistics-my.sharepoint.com/:f:/g/personal/jesse_vnhph_beelogistics_com/IgDv9g-0KT5QQqPV3hLy98LXATPUA8HmslxyzjKqJV9xqlQ?e=TmQHXs 
- Enhance lại search giá trucking để tìm được theo tiêu chí pickup/ develiry address (nhớ normalize text trước khi search)

---

## Tracking Pricing Performance


1. Viết bảng sheet tổng hợp Inquiry theo chiều pricing để vào báo cáo:
    - Tương tự màn hình Pricing Queue, thêm cột để tính thời gian báo giá so với thời điểm gửi request.
    - Phân quyền theo access control crm.
    - Để thêm các chức năng cho phép chỉnh sửa request như thông tin pricing, thông tin sales, volume, tuyến, đổi status … gửi mail thông báo cho pic liên quan.

---

## Vendor Pricing API

### **Mô tả công việc:**

Phát triển API để các vendor bên ngoài có thể đẩy dữ liệu giá vào hệ thống. API cần hỗ trợ cấu hình margin/markup và xử lý các trường thông tin cơ bản dựa trên logic upload Excel hiện tại.

**Phạm vi công việc:**

- Xây dựng API nhận giá từ vendor (bulk input), sử dụng format tương tự chức năng upload Excel đang dùng.
- Rà soát và chuẩn hóa lại các trạng thái của bảng giá:
    - Giá upload từ UI: **validated/active**
    - Giá upload qua API: **draft**
- Cân nhắc tách Entity riêng để quản lý dữ liệu giá dạng draft.
- Xây dựng màn hình admin để xem và kiểm tra giá draft trước khi duyệt.

### Implementation

### Docs/ Guide

---

## Update Route Field


cập nhật cho cả container/ trucking.

![[Screenshot_2025-12-08_at_08.52.16.png]]

Query route trong db, Fix search UI ở cột Dest (rename to Route) để search được theo route, show thông tin tuyến. 

![[Screenshot_2025-12-08_at_08.54.43.png]]
---

Xem thêm: [[datatp-datatp-overview]]
