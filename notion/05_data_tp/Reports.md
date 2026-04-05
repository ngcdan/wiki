# 📟 Reports

> Notion ID: `28ef924d5d7b809f9c21e5ddda6d5573`
> Parent: Data TP → Status: Business Domain (Glossary - Process - Use case)
> Synced: 2026-04-05

## Dựng OF1 Cloud Production (Tuấn + Nam phụ trách)

### Giai Đoạn 1 tháng 7-9
- Xây dựng và test hệ thống - **FINISHED**

### Giai Đoạn 2 tháng 9-12
- Chuyển các phần mềm của OF1 HP&HN về hạ tầng OF Cloud - **FINISHED**
- Tạo môi trường máy ảo cho nhóm CRM, TMS, Egov. Mỗi nhóm được cấp 1 máy db, 1 máy server, 1 máy window và các máy ảo khác theo yêu cầu - **FINISHED**
- Chuyển Ecus server HP lên hệ thống OF1 Cloud - **IN PROGRESS**
- Phối hợp với team HCM chuyển 1 số máy lên OF1 Cloud - **PENDING**

## Triển khai hệ thống SSO dựa trên Keycloak (Tuấn + Đạt Lương phụ trách)

### Giai Đoạn 1 tháng 9-10
- Tìm hiểu test thử nghiệm - **FINISHED**
- Viết code để tích hợp với beelogistics.cloud - **FINISHED**
- Migrate dữ liệu user, user profile qua keycloak db - **FINISHED**
- Triển khai test thử nghiệm trên 1 nhóm nhỏ - **IN PROGRESS**
- Hướng dẫn, triển khai cho toàn bộ beelogistics.cloud users - **WAITING**

### Giai Đoạn 2 tháng 10-12
- BFS One tích hợp, sử dụng keycloak
- Tích hợp với một số phần mềm khác như Moodle LMS

## Team OF1 - CRM

### Giai Đoạn 3 tháng 7-9 (Đàn, Nhật, An)

#### 1. Task Request: Công cụ request lỗi cho kế toán (HRM)

**Requirements:**
Việc các bộ phận sales/docs/cus khi nhập liệu vào hệ thống có sai sót và nhờ bộ phận kế toán mở lại file, sửa lại thông tin. Kế toán cần công cụ để theo dõi đầu mục này để tính toán hiệu quả, KPI sau này.

**Status:** Đưa vào dùng từ tháng 7 đến hiện tại, dùng đều đặn.

#### 2. Chức năng book lịch phòng họp + xe (triển khai cho HPH/HAN)

#### 3. Setup và triển khai Pricing cho BEE VP nước ngoài

### Keycloak Integration

**Requirements:**
- Xây dựng API cho phép các ứng dụng nội bộ thao tác với Keycloak qua REST (tạo user, cập nhật, phân quyền…)
- Tích hợp đồng bộ dữ liệu người dùng với các hệ thống: **BFSOne**, **HRM**, **Bee Cloud**
- Cung cấp template tạo mới nhân sự, submit thông tin và phân quyền tập trung trên Bee Cloud (khi HRM tạo nhân sự mới → auto tạo user + gán quyền)

**Implements:**

1. Thiết kế, phát triển API Gateway tích hợp Keycloak
   - Thu thập danh sách API cần dùng từ từng hệ thống (BFSOne, HRM, Bee Cloud)
   - Thiết kế flow đồng bộ: HR Submit → Bee Cloud nhận data → gọi API Keycloak → produce message vào Kafka → BFSOne, HRM, Bee Cloud consume message để đồng bộ thông tin
   - API tạo user, cập nhật user, vô hiệu hóa user, gán role, group theo template

2. Tích hợp hệ thống
   - **Bee Cloud:** Form submit tạo nhân sự mới, produce message vào Kafka, đồng bộ thông tin cơ bản (tên, email, vị trí, phòng ban)
   - **HRM, BFSOne:** Nhận event khi HRM tạo nhân viên mới, đồng bộ thông tin cơ bản (tên, email, vị trí, phòng ban)

3. Logging + audit trail cho toàn bộ thao tác

**Reviews:**
- Quy trình tạo user + phân quyền đúng luồng đã thiết kế
- Đồng bộ hoạt động ổn định
- Có mô tả API rõ ràng, hướng dẫn tích hợp
- Có checklist khi tạo mới nhân sự

### Hoàn thành (Done)
- Tổ chức lại các app, web documentation cho of1 platform
- Review account trong hệ thống, liên kết với các entity khác bằng account_id thay vì login_id
- Chức năng book lịch phòng họp + xe (triển khai cho HPH/HAN)
- Quản lý công việc hàng ngày của team BD Support liên quan tới lịch Event, chi phí tham gia hiệp hội, theo dõi hợp đồng Agent
- Đưa quy trình request/approve và quản lý thông tin khách hàng qua CRM mới
- Setup và triển khai Pricing cho BEE VP nước ngoài
- API với hệ thống HRM để tự động hóa việc tạo account

### In Progress
- **Report cho BD về Volume, Profit, Revenue, Agent Transactions, Sale Teams**
  Vướng nhiều ở data nguồn, hiện tại đang dùng bee legacy report, không đảm bảo chính xác do sync data set lớn

- **Tuning công việc cho team BD qua Daily Tasks**
  Theo dõi công việc hằng ngày, cuộc họp, tham dự conference

### Giai Đoạn 2 tháng 10-12 (Đàn, Nhật, An, Đức)
- Kết với team vận hành HPH/HCM triển khai pricing HCM
- Hoàn thiện quy trình công việc/báo cáo cho team BD
- Sync data real-time từ bfsone qua bee legacy report. Dùng công nghệ **debezium + kafka** (demo với a Quý)
- Tách db cho TMS
- Triển khai báo cáo tuần thay thế báo cáo tuần trên CRM cũ cho toàn VP
- Hoàn thiện các chức năng CRM cho sales, cắt CRM cũ
- Phiếu đánh giá KPI cho năm (request chị Huyền)
