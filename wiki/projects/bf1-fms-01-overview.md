---
title: "FMS 01 - Overview"
tags: [bf1, fms]
---

# OF1 FMS — Project Overview

## 1. Project Goals

### Mục tiêu của hệ thống

1. **Phát triển BF1 trên nền tảng mới theo định hướng sản phẩm hóa**
   Xây dựng BF1 trên nền tảng mới theo khung kiến trúc/framework của anh Tuấn, hướng tới sản phẩm chuẩn hóa, dễ đóng gói và sẵn sàng triển khai cho khách hàng bên ngoài.

2. **Thiết kế hệ thống theo mô hình module/app độc lập, tập trung vào nghiệp vụ Freight Forwarder Management**
   Tổ chức hệ thống thành các module/app độc lập theo từng nhóm chức năng, tập trung vào các nghiệp vụ cốt lõi của Freight Forwarder Management, thuận tiện cho phát triển, triển khai và mở rộng.

3. **Chuẩn hóa nền tảng để hỗ trợ tích hợp và vận hành lâu dài**
   Chuẩn hóa kiến trúc, dữ liệu và cơ chế kết nối để hỗ trợ tích hợp, vận hành ổn định và mở rộng lâu dài.

### System Overview

OF1 (OpenFreightOne) là hệ thống quản lý vận tải hàng hoá (Freight Management System) cho các công ty giao nhận vận tải quốc tế (Freight Forwarder) tại Việt Nam. Hệ thống bao phủ toàn bộ quy trình nghiệp vụ từ tiếp nhận khách hàng, báo giá, đặt chỗ, quản lý chứng từ, xuất hoá đơn, đến đối soát công nợ và báo cáo tài chính.

---

## 2. Core Business Modules

### I. Master Data
- Quản lý dữ liệu nền dùng chung như location, country, currency, unit và các danh mục chuẩn khác
- Chuẩn hóa dữ liệu nền, giảm trùng lặp, tăng tính nhất quán
- Làm cơ sở cho tích hợp, mở rộng module và triển khai cho nhiều khách hàng

**Danh mục hệ thống (5 loại):** Port Index, Container List, Port Index Trucking, Shipment Type Warning, Transaction Task List.

### II. Partner & Customer
- Quản lý partner, customer, agent, carrier và các bên liên quan
- Tích hợp và đồng bộ dữ liệu đối tác, khách hàng với CRM

**Quản lý đối tác (8 nhóm):**

| Đối tượng | Vai trò | Đặc điểm |
|-----------|---------|----------|
| Departments | Phân quyền nội bộ | Admin only, phân quyền theo chi nhánh |
| Leads | Khách hàng tiềm năng | Có thể chuyển đổi thành Customer |
| Customer | Khách hàng thực tế | Trung tâm của toàn bộ giao dịch |
| Shipper | Người gửi hàng | Xuất hiện trên vận đơn |
| Consignee | Người nhận hàng | Xuất hiện trên vận đơn |
| Carrier | Hãng tàu/hãng bay | Vận chuyển thực tế |
| Agents | Đại lý | Đại diện tại nước ngoài |
| Other Contacts | Liên hệ khác | Hải quan, kho bãi, ... |

### III. Job File (Master Bill)
Theo dõi job file (master bill) và liên kết với house bill. Quản lý cấu trúc shipment, thông tin vận chuyển và dữ liệu đối tác liên quan. File là thực thể trung tâm nhất, liên kết với hầu hết các thực thể khác.

### IV. House Bill
Theo dõi vòng đời house bill theo từng lô hàng. Tra cứu, cập nhật trạng thái, theo dõi chứng từ nghiệp vụ. Bill có 2 loại: House (HAWB/HBL) và Master (MAWB/MBL).

### V. Sales & Quotation Management
Quản lý báo giá và booking theo 3 phương thức vận chuyển chính: Hàng không, Hàng biển, Chuyển phát. Hỗ trợ Database giá từ các hãng vận chuyển.

Quy trình: **Database Giá → Báo giá → Đặt chỗ (Booking) → Xác nhận → Mở file**

**Database Giá (3 loại):** AirFreight Pricing, SeaFreight Pricing, Express Pricing.

### VI. Purchase Order & Process
- Quản lý yêu cầu dịch vụ của khách hàng theo Purchase Order (PO)
- Hỗ trợ một PO có một hoặc nhiều booking
- Theo dõi từng Purchase Order Process (POP) độc lập, có mã, trạng thái và bộ chứng từ riêng

### VII. Tracking & Tracing
- Theo dõi trạng thái hàng hóa, shipment, container và các mốc nghiệp vụ
- Tracing theo house bill, master bill, container hoặc mã tham chiếu
- Theo dõi tiến độ theo PO, booking và từng POP

### VIII. Documentations — Vận hành & Chứng từ

Module này quản lý toàn bộ chứng từ cho các loại lô hàng (11 loại):

| Loại | Hướng | Phương thức |
|------|-------|-------------|
| Express | Xuất | Chuyển phát nhanh |
| Outbound Air | Xuất | Hàng không |
| Inbound Air | Nhập | Hàng không |
| LCL Outbound Sea | Xuất | Đường biển lẻ |
| LCL Inbound Sea | Nhập | Đường biển lẻ |
| FCL Outbound Sea | Xuất | Đường biển nguyên cont |
| FCL Inbound Sea | Nhập | Đường biển nguyên cont |
| Outbound Sea Consol | Xuất | Gom hàng đường biển |
| Inbound Sea Consol | Nhập | Gom hàng đường biển |
| Inland Trucking | Nội địa | Xe tải |
| Logistics | Phức hợp | Dịch vụ logistics |

**Thành phần chung của mỗi file:** Job ID, Customer, Agent, Shipper, Consignee, POL/POD, ETD/ETA; HAWB/HBL + MAWB/MBL; Buying/Selling Rate; Debit/Credit Note; Logistics Charges; Container chi tiết (FCL).

**Chức năng bổ trợ:** Warehouse Management, CFS Inbound, OPS Management, Customs Clearance, Tracing ETD-ETA, EDI Local, Task Notes.

### IX. Accounting — Kế toán & Tài chính

Module này gồm 22 chức năng:

**Hoá đơn điện tử (VAT Invoice):** Tạo từ Debit/Credit Note. Vòng đời: Draft (trắng) → Issued (hồng) → Paid (xanh). Hỗ trợ Issue, Sign, Send by mail. Xử lý đặc biệt: Replace, Editing Invoice.

**Quản lý công nợ:** Transaction Register (trung tâm đối soát), Statement of Account (SOA), Account Receivable, Overdue Debts.

**Tạm ứng & Giải trình (Settlement):** Quy trình duyệt 3 cấp (Trưởng phòng → Kế toán trưởng → Giám đốc). Sau duyệt, chi phí tự động nhập vào Logistics Charges.

**Báo cáo:** VAT Invoice, Credit Invoice, Sheet of Debit Record, Account Receivable, Revenue & Profit.

**Financial Planning:** Payment-Receivable Planning, Bank Transaction History.

---

## 3. Business Processes

### 3.1 Vòng đời lô hàng (Shipment Lifecycle — 13 bước)

1. **Tiếp nhận khách hàng** — Catalogue > Leads
2. **Tạo Customer** — Chuyển đổi Lead thành Khách hàng
3. **Tạo báo giá** — Sales Executive (AirFreight/SeaFreight/Express)
4. **Đặt chỗ (Booking)** — Booking Request/Confirm
5. **Booking Confirm** — Xác nhận đặt chỗ
6. **Mở File chứng từ** — Documentations (theo loại vận chuyển)
7. **Tạo vận đơn** — HAWB/HBL hoặc MAWB/MBL
8. **Nhập giá mua/bán** — Buying Rate / Selling Rate
9. **Xuất Debit/Credit Note** — Cho Customer, Agent, Carrier
10. **Xuất hoá đơn** — Accounting > New VAT Invoice
11. **Đối soát công nợ** — Transaction Register > SOA
12. **Thanh toán** — History of Payment
13. **Báo cáo lợi nhuận** — P/L Sheet

**Các nhánh phụ:** Tạm ứng / Giải trình, Customs Clearance, Tracing, EDI.

### 3.2 Quy trình xuất hoá đơn (Invoice Flow)

1. Xuất Debit/Credit Note — Docs > More > Subject to
2. Tạo hoá đơn điện tử — Accounting > New VAT Invoice
3. Chọn KH/File > Filter > Tick chi phí > OK
4. Kiểm tra > Save → Hoá đơn NHÁP (Draft)
5. Issue E-Invoice → Hoá đơn đã ISSUE (Màu hồng)
6. Make E-Invoice Signature (Ký điện tử)
7. Send E-Invoice by mail (PDF + XML cho KH)
8. Khách hàng thanh toán → Hoá đơn XONG (Màu xanh)
9. Đối soát công nợ — Statement Of Account

**Xử lý đặc biệt:** Replace New E-Invoice (huỷ cũ xuất mới), Make Editing Invoice, Import to Accounting System.

### 3.3 Quy trình duyệt tạm ứng / giải trình (Settlement Flow)

```
OP tạo yêu cầu → Trưởng phòng duyệt → Kế toán trưởng duyệt → Giám đốc duyệt → Hoàn thành
```

**Lưu ý:**
- Trưởng phòng: kiểm tra phí, hoá đơn theo HBL. Nếu phí trùng lặp → hiện màu đỏ.
- Kế toán trưởng: so sánh với phiếu tạm ứng. Có quyền xoá chi phí không hợp lý. Có thể uỷ quyền duyệt thay Giám đốc (trong hạn mức).
- Giám đốc: kiểm tra hạn mức.
- Bất kỳ cấp nào Decline đều trả về OP làm lại.
- Sau khi hoàn thành: chi phí tự động nhập vào Logistics Charges, Import vào PM kế toán.

---

## 4. User Roles & Permissions

| Vai trò | Quyền hạn chính |
|---------|----------------|
| Admin | Toàn quyền hệ thống, quản trị phân quyền |
| Giám đốc | Duyệt tạm ứng/giải trình cấp cao nhất |
| Kế toán trưởng | Duyệt tài chính, uỷ quyền duyệt thay Giám đốc |
| Trưởng phòng | Duyệt nghiệp vụ, ký Settlement |
| Salesman | Quản lý KH, báo giá, booking, xem P/L Sheet |
| Nhân viên chứng từ | Mở file, tạo vận đơn, nhập giá, xuất Debit/Credit |
| Kế toán | Xuất hoá đơn VAT, quản lý công nợ, báo cáo |
| Nhân viên OP | Tạm ứng, giải trình, trucking request |

---

## 5. Implementation Phases

Lộ trình triển khai được chia thành 3 giai đoạn chính:

- **Phase 0: Read-First Migration** — Nhanh chóng hình thành nền tảng mới phục vụ tra cứu và đối soát
- **Phase 1: Write-Back Integration** — Từng bước chuyển luồng ghi dữ liệu sang hệ thống mới
- **Phase 2: Full Data Migration & Production Rollout** — Hoàn tất migrate dữ liệu và triển khai thực tế

### Principles

- BF1 mới được phát triển và vận hành **song song** với hệ thống cũ trong suốt quá trình chuyển đổi
- Triển khai theo từng nhóm chức năng và từng nhóm người dùng, **không cut-over** toàn bộ trong một lần
- Ưu tiên làm `read` trước `write`, ưu tiên hiển thị đúng dữ liệu trước khi thay đổi luồng vận hành
- Mỗi nhóm chức năng cần có giai đoạn test, pilot run, đối soát và nghiệm thu trước khi mở rộng phạm vi

### Milestone Timeline

| Milestone | Phase | Key Deliverables | Acceptance Criteria |
|-----------|-------|------------------|---------------------|
| M0: Analysis & Rollout Design | 0.0 | Đánh giá hiện trạng BF1 (.NET, MSSQL), xác định phạm vi module ưu tiên, thiết kế kiến trúc Java/ReactJS/PostgreSQL/Kafka và kế hoạch rollout song song | Phạm vi triển khai, luồng dữ liệu, kiến trúc mục tiêu, thứ tự module và kế hoạch pilot được thống nhất |
| M1: PostgreSQL Foundation & Schema Design | 0.1 | Thiết lập PostgreSQL, chuẩn hóa schema, entity, mapping và validation cho các nhóm dữ liệu cốt lõi | Schema mục tiêu được chốt, database mới sẵn sàng và các quy tắc mapping dữ liệu được thống nhất |
| M2: Read APIs & Business Screens with Test Data | 0.2 | Xây dựng API read, màn hình tra cứu, báo cáo, dashboard và form hiển thị bằng dữ liệu test cho các module ưu tiên | Người dùng có thể kiểm tra luồng hiển thị, thông tin nghiệp vụ và xác nhận tính đúng đắn của screen/API trên dữ liệu test |
| M3: Realtime Sync Pipeline | 0.3 | Xây dựng pipeline realtime `MSSQL CDC → Kafka → PostgreSQL`, kèm retry, logging, offset tracking và checksum | Dữ liệu được đồng bộ ổn định sang DB mới và có khả năng đối soát theo luồng realtime |
| M4: Module Pilot - Read-First Rollout | 0.4 | Pilot theo từng nhóm chức năng và nhóm người dùng cho các module read-first | Mỗi nhóm pilot có checklist test, kết quả đối soát với hệ thống cũ và xác nhận sẵn sàng mở rộng |
| M5: Write Functions & Write-Back Pipeline | 1.0 | Implement chức năng write trên hệ thống mới, lưu vào PostgreSQL và xây pipeline publish message qua Kafka để cập nhật ngược về hệ thống cũ | Các luồng write hoạt động ổn định, dữ liệu ghi mới được đồng bộ ngược chính xác và không ảnh hưởng vận hành hiện tại |
| M6: Parallel Run by User Group | 1.1 | Mở rộng pilot write theo từng nhóm chức năng, từng nhóm người dùng và theo dõi song song hai hệ thống | Mỗi đợt rollout có kết quả test, đối soát, xử lý lỗi và xác nhận nghiệm thu trước khi mở rộng tiếp |
| M7: Operational Hardening & Expansion | 1.2 | Tối ưu hiệu năng, logging, monitoring, alerting, tracking chất lượng dữ liệu và lập kế hoạch mở rộng các module còn lại | BF1 mới sẵn sàng vận hành lâu dài, có khả năng scale, giám sát đầy đủ và mở rộng tiếp theo từng module |
| M8: Full Data Migration Readiness | 2.0 | Chuẩn bị kế hoạch migrate toàn bộ dữ liệu, chiến lược cut-over, backup/rollback, checklist đối soát và tiêu chí go-live | Kế hoạch migrate được chốt, dữ liệu được kiểm tra sẵn sàng và rủi ro go-live có phương án kiểm soát |
| M9: Full Data Migration & Production Go-Live | 2.1 | Thực hiện migrate toàn bộ dữ liệu cần thiết sang hệ thống mới, triển khai production và theo dõi go-live | Dữ liệu migrate đầy đủ, hệ thống mới vận hành thực tế ổn định và được nghiệm thu sau go-live |
| M10: Post Go-Live Stabilization | 2.2 | Theo dõi vận hành thực tế, xử lý lỗi phát sinh, đối soát dữ liệu sau migrate và tối ưu sau triển khai | Hệ thống ổn định sau production rollout, lỗi trọng yếu được xử lý và vận hành được bàn giao rõ ràng |

### Phase 0 — Read-First Migration

#### 0.0 Analysis & Rollout Design
- Đánh giá hiện trạng BF1 hiện tại trên .NET và MSSQL
- Xác định phạm vi module ưu tiên: Master Data, Partner & Customer, Job File, House Bill, Purchase Order & Process, Tracking & Tracing
- Thiết kế kiến trúc mục tiêu trên Java, ReactJS, PostgreSQL và Kafka
- Xây dựng backlog, milestone và chiến lược rollout song song
- Xác định tiêu chí test, pilot run, đối soát và nghiệm thu

#### 0.1 PostgreSQL Foundation & Schema Design
- Thiết lập PostgreSQL làm database mới
- Chuẩn hóa schema, entity, mapping và validation
- Thiết kế chiến lược migrate dữ liệu, khóa chính, khóa ngoại
- Rà soát khác biệt giữa MSSQL hiện tại và PostgreSQL mục tiêu

#### 0.2 Read APIs & Business Screens with Test Data
- Chuẩn bị data test cho các module ưu tiên
- Xây dựng API `read`, màn hình tra cứu, báo cáo, dashboard
- Review với người dùng nghiệp vụ và đội vận hành
- Chốt tiêu chí đúng dữ liệu và đúng nghiệp vụ trước khi kết nối dữ liệu thực

#### 0.3 Realtime Sync Pipeline
- Thiết lập cơ chế đọc log từ MSSQL qua CDC (Debezium)
- Đẩy dữ liệu realtime từ MSSQL vào Kafka và từ Kafka xuống PostgreSQL
- Bổ sung retry, logging, monitoring, offset tracking, checksum
- Thiết lập cơ chế theo dõi trạng thái sync và xử lý lỗi

#### 0.4 Module Pilot — Read-First Rollout
- Chọn nhóm chức năng và nhóm người dùng ưu tiên để pilot
- Chạy thử các luồng `read` song song với hệ thống cũ
- Đối soát dữ liệu giữa MSSQL và PostgreSQL
- Ghi nhận lỗi, chênh lệch nghiệp vụ và hoàn thiện

### Phase 1 — Write-Back Integration

#### 1.0 Write Functions & Write-Back Pipeline
- Implement `write` trên hệ thống mới, lưu vào PostgreSQL
- Thiết kế message model cho luồng ghi cần đồng bộ ngược
- Publish message qua Kafka để cập nhật ngược về hệ thống cũ
- Bảo đảm retry, idempotency, logging, đối soát

#### 1.1 Parallel Run by User Group
- Triển khai luồng `write` theo nhóm chức năng và nhóm người dùng
- Chạy song song BF1 mới với hệ thống cũ
- Đối soát kết quả ghi dữ liệu
- Nghiệm thu từng đợt trước khi mở rộng

#### 1.2 Operational Hardening & Expansion
- Tối ưu hiệu năng API, pipeline, Kafka consumer/producer, Web UI
- Hoàn thiện logging, monitoring, alerting, dashboard
- Giám sát chất lượng dữ liệu, độ trễ sync, trạng thái message
- Lập kế hoạch mở rộng các module tiếp theo

### Phase 2 — Full Data Migration & Production Rollout

#### 2.0 Full Data Migration Readiness
- Xác định phạm vi dữ liệu cần migrate
- Chuẩn bị kế hoạch migrate, backup, rollback, checklist cut-over
- Thiết lập tiêu chí đối soát trước, trong và sau khi migrate
- Rà soát tính sẵn sàng của hạ tầng, ứng dụng, dữ liệu, đội vận hành

#### 2.1 Full Data Migration & Production Go-Live
- Thực hiện migrate toàn bộ dữ liệu
- Triển khai BF1 mới lên production
- Cut-over và chuyển người dùng sang hệ thống mới
- Theo dõi sát trạng thái hệ thống, dữ liệu, luồng tích hợp

#### 2.2 Post Go-Live Stabilization
- Đối soát dữ liệu sau migrate và xử lý chênh lệch
- Theo dõi lỗi production, hiệu năng, độ ổn định
- Hoàn thiện tài liệu vận hành, quy trình hỗ trợ, bàn giao
- Đánh giá kết quả và lập kế hoạch tối ưu

---

## 6. Required Resources

- BF1 bản test — application và database riêng cho thử nghiệm
- Full database từ hệ thống thực tế (bao gồm dữ liệu kế toán) cho mapping, đối soát và test nghiệp vụ

---

## 7. External Links

- [BF1 Web Upgrade Plan](https://wiki.beelogistics.cloud/vi/OF1/IT_Plans/BF1_Web_Upgrade_Plan)
- [Dev Team Project Board](https://git.datatp.cloud/of1-fms/of1-fms/projects/2)
- [Google Drive — Project Documentation](https://drive.google.com/drive/folders/1-sBVcPbf-EAcsQ1YNrcHfndLrAojCaDF?usp=sharing)
