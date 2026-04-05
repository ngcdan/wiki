---
title: DataTP - Tổng quan dự án
tags:
  - datatp
  - overview
  - release
  - infrastructure
---

# Hướng Dẫn

Trang này đóng vai trò như menu tổng quan, giúp bạn điều hướng nhanh đến các mục hướng dẫn chi tiết.

---

## Mục lục

### Nghiệp vụ
- [[odoo|Odoo — ERP & Kế toán]]
- [[script-bia-2025|Script BIA 2025]]

### Kỹ thuật
- [[cdc-debezium|CDC với Debezium]]
- [[mail|Mail — Email Solutions]]
- [[mobile|Mobile App]]
- [[setup-macos-env|Setup macOS]]

### Pricing
- [[pricing|Pricing — Features & Enhancement]]

### Tasks
- [[crm-tasks|CRM Tasks — Bug fixes & Enhancements]]

### Liên quan
- [[project-overview|BF1 Upgrade - Tổng quan]]
- [[cdc-architecture|CDC Architecture (BF1)]]
- [[datatp-ideas|DataTP Ideas]]


# Changelog

All notable changes to this project will be documented in this file.

### [Unreleased]
#### Hướng dẫn cập nhật
- Update schema - yêu cầu chạy instance.sh với run:update:
[Document-set] Thêm 2 cột :
***category(house-bills, tms-fcl-inv, tms-lcl-inv, receipt,...)***
Sử dụng tạo key lưu trữ trên s3 với cấu trúc {document-category}/{docSetId} - vd: tms-fcl-inv/doc-set-01.
***upload_app(tms, document,crm,...)***
Sử dụng phân loại document đc upload từ đâu

- Yêu câu máy chủ platform cập nhật config/application-env.yaml
```
s3:
  endpoint: http://rook-ceph-rgw-bee-vietnam-hn-prod-store.rook-ceph.svc.cluster.local
  access-key: U7IZNLULT4U5WECC29ZP
  secret-key: Gufj2fk7S2pnKuB5X3evzCsTM5kiALLzsmaPM9cM
  region: bee-vietnam
```
Thêm trong datatp
```
datatp:
  msa:
    identity:
      queue:
        event-producer-enable: false
        event-consumer-enable: false
        topic:
          events: "datatp.${env.name}.identity.events"
          retry-events: "datatp.${env.name}.identity.retry-events"
          event-acks: "datatp.${env.name}.identity.event-acks"
```
#### Thông tin cập nhập
- Cập nhật giao diện S3 Manager
- Viết document-set-plugin hỗ trợ xử lý các việc như move file với các loại doc-set khác nhau

- Lưu trữ vào document-upload theo cấu trúc mới
```
{companyCode}-doc-upload
    {document-category}/{docSetId}:  // vd: tms-fcl-inv/doc-set-01
        __info__
        hb-1-invoice-01.pdf
        hb-2-invoice-01.pdf
        hb-1-receipt-01.pdf
        hb-1-other-01.pdf
```

- Rename các file upload trong bộ doc-set theo bảng kê với cấu trúc {hbl-no}-{invoice-no}.ext
b1: Thực hiện đổi key và save lại trên document-db
b2: Lưu file với key mới trên S3
b3: Xóa các file với key cũ
- Move file to hbl
b1: Tạo các bộ doc-set loại doc-accounting với name là hblNo tương ứng
b2: Sao chép file từ bucket: {companyCode}-doc-upload sang {companyCode}-doc-accounting với cấu trúc
```
{companyCode}-doc-accounting
    house-bills
        {house-bill-code}
            __info__
            invoices
                invoice-01.pdf
                invoice-01.pdfie
            receipts
                receipt-01.pdf
                receipt-01.pdfie
            others
                other-01.pdf
```
b3: S3 các file origin xóa nội dung và lưu metadata link tới vị trí file ở bucket mới
datatp-storage-move-to: bucket:/key

### [R20250820]

    - Thêm chức năng in cho document dạng ảnh
    - Thêm chức năng cache lại dữ liệu taxcode

### [R20250818]

1. Tasks:

- [Dat]:
    - Thêm bổ sung xử lý các document dạng ảnh, thêm type "image" và plugin
- [Dat]:
  - Cập nhập bổ sung phần tạo bảng kê cho hóa đơn nâng hạ
- [Dat]:
  - Bổ sung phần download bộ chứng từ theo format chuẩn BFSOne

### [R20250721]


---

## Releases

@All

Hi mọi người,

1. Em cập nhật phần mềm, chỉnh lại chức năng tìm kiếm giá, tạo request cho **Trucking**.
Chi tiết và hướng dẫn xem lại link.
[https://docs.beelogistics.cloud/docs/shared/user/system/#%C4%91%E1%BB%95i-m%E1%BA%ADt-kh%E1%BA%A9u](https://docs.beelogistics.cloud/docs/datatp-crm/user/crm/references/search_prices#trucking)
2. Tổ chức lại màn hình báo cáo, tập trung về 1 màn hình Reports như hình đính kèm.
[Reports | DataTP Cloud Documentation](https://docs.beelogistics.cloud/docs/datatp-crm/user/crm/reports).
3. Setup, chuyển đổi toàn bộ báo cáo tuần từ CRM cũ qua CRM mới.
Chi tiết hướng dẫn xem tại [Project/ Tasks | DataTP Cloud Documentation](https://docs.beelogistics.cloud/docs/datatp-hrm/user/project/).
4. Pricing Performance/  Pricing SLA. Theo dõi thời gian báo giá của Pricing.
Ở giao diện của Pricing theo dõi Inquiry. Phần mềm sẽ hightlight mức độ theo các màu tương ứng với thời gian trễ chưa báo giá cho sales.
Ngoài ra, với Trucking HPH vào đầu mỗi ngày sẽ có mail tổng hợp những inquiry chậm gửi tới TBP theo từng dịch vụ.
Chi tiết xem ở hình bên dưới.
5. Ngày 15/12 (đầu tuần sau), hệ thống CRM cũ sẽ chính thức không truy cập được nữa.
Toàn bộ các chức năng sẽ thực hiện trên CRM mới. [DATATP ERP](https://beelogistics.cloud/).
Bao gồm lịch họp/ book xe. Mọi người kiểm tra và đặt lại lịch họp trên CRM mới để đảm bảo công việc không bị gián đoạn.
[https://docs.beelogistics.cloud/docs/datatp-utilities/user/asset](https://docs.beelogistics.cloud/docs/datatp-utilities/user/asset)

Toàn bộ hướng dẫn trên hệ thống cloud, ACE có thể tìm kiếm ở trang [https://docs.beelogistics.cloud/](https://docs.beelogistics.cloud/)



@All
Hi mọi người,
Em cập nhật phần mềm, thêm trường thông tin Pricing Branch vào form request check giá.
Trường này trường bắt buộc, mặc định lấy theo Branch của user, mọi người lúc gửi request check giá chọn đúng VP check giá giúp em nhé.

---

## BF1 Web Upgrade

Tạo task mới.

Cài đặt, setup dự án, môi trường, ….

Sample data để mỗi bảng 2 records là đủ

![[Screenshot_2026-03-26_at_09.36.19.png]]

Em xác nhận lại thông tin:

- **Group Name:** `OF1-Dev`
- **Group ID:** `1001991820626`

Có phải anh muốn thêm em vào group **"OF1-Dev"** với ID `-1001991820626` không ạ?



Hi anh Hải,

Em đã xem lại các comment của anh và xin cập nhật lại trạng thái các hạng mục như sau:

**Về các mục đã làm (mục 52):**

**1. Agent Conference & Meeting trong Task Calendar (BIA) => Ưu tiên làm.**

- Trước mắt sẽ tập trung vào phần input nhập liệu, dự kiến hoàn thành trong tháng 5 (có thể sớm cuối tháng 4).
- Phần biểu đồ sẽ triển khai sau, khi user đã input đủ dữ liệu vào hệ thống.

**2. SPM – Sales Performance Management (Báo cáo hiệu suất sales)**

- **Report của MNG:** Đã hoàn thành và cập nhật, em cũng đã thông tin trước đó. Anh check lại giúp em và cho em thêm feedback nếu cần điều chỉnh.
- **Report của từng salesman:** => release trên phần mềm vào tuần sau.
- Các yêu cầu liên quan đến biểu đồ sẽ làm sau, cần đủ data từ phía user để vẽ.
- Ngoài ra, các báo cáo sẽ ưu tiên triển khai trên CRM; phần này bên IT sẽ tự làm việc và cập nhật thêm nếu phát triển trên BF1.

**3. Agent / Customer Hub**

- Sau khi BD duyệt như đã nêu và đảm bảo record đủ data.
- Nếu đủ các điều kiện, dự kiến IT sẽ thực hiện sau tháng 9.


150tr



50/ tháng ⇒


43

30tr →

![[Screenshot_2026-03-28_at_16.07.10.png]]



- Tạo account devhcm → phân quyền dùng chung cho toàn bộ các app
- An tạo api trong postman với
Base URL: [https://beelogistics.cloud/platform/plugin/crm/rest/v1.0.0/rpc/internal/call](https://beelogistics.cloud/platform/plugin/crm/rest/v1.0.0/rpc/internal/call)
Method: POST
Param:
```javascript
{
   "component": "BFSOneSyncService",
   "endpoint": "syncExchangeRates",
   "userParams": {}
}

```

> [!note]+ ### Meeting Note
> 1. Danh sách Transactions - Master Bill (show 1 tháng gần nhất)
> 2. [Express - Chuyên phát nhanh](https://github.com/ngcdan/wiki/blob/main/projects/bf1/bfs/references/system-documentation.md#1-express---chuy%C3%AAn-ph%C3%A1t-nhanh)
> Khác gì so với hàng Air, có thể gộp vào được không? hoặc cân nhắc bỏ.
> 3.

Thêm bảng để lưu thông tin, tracking debit riêng.

CDC: Debezium MSSQL -> Kafka -> CDCListener -> CDCEventHandler -> save PostgreSQL

Batch Sync: CronJob query MSSQL -> Producer -> Kafka -> Consumer -> save PostgreSQL

Write Fms Entity → save Postgresql →  Kafka → Consumer call BF1 Api → Mssql








Điện Đ: 666 - 585 ⇒ 81 số x 3.5k ⇒ 284k

Điện N: 4521 - 4410 ⇒ 111 x 3.5 ⇒ 389k

Tổng tiền Điện 812k → (284 + 389) = 139 (điện chung) + 230k (rác + nước) ⇒ 369 / 2 ⇒ 184,5k

**Nhật trả: 389 (điện riêng) + 184 (chung) + 4000 ⇒ 4.573**


Điện chung: 20908 - 20657 ⇒ 251 x 3.5k ⇒ 900k
Tổng điện tháng 4: 1573


<!-- Notion API token removed -->

### Lien quan

- [[project-overview|BF1 Upgrade - Tổng quan]]
- [[datatp-overview|DataTP - Tổng quan]]
- [[cdc-architecture|CDC Architecture]]

---

## Reports — OF1 Cloud Production

### Dựng OF1 Cloud Production (Tuấn + Nam phụ trách)

#### Giai Đoạn 1 tháng 7 - 9:

- Xây dựng và test hệ thống - FINISHED.

#### Giai Đoạn 2 tháng 9 - 12:

- Chuyển các phần mềm của OF1 HP&HN về hạ tầng OF Cloud - FINISHED
- Tạo môi trường máy ảo cho nhóm CRM, TMS, Egov. Mỗi nhóm được cấp 1 máy db , 1 máy server, 1 máy window và các máy ảo khác theo yêu cầu - FINISHED.
- Chuyển Ecus server HP lên hệ thống OF1 Cloud - IN PROGRESS.
- Phối hợp với team HCM chuyển 1 số máy lên OF1 Cloud - PENDING

### Triển khai hệ thống SSO dựa trên Keycloak (Tuấn + Đạt Lương phụ trách).

#### Giai Đoạn 1 tháng 9 - 10:

- Tìm hiểu test thử nghiệm - FINISHED
- Viết code để tích hợp với beelogistics.cloud - FINISHED
- Migrate dữ liệu user, user profile qua keycloak db - FINISHED.
- Triển khai test thử nghiệm trên 1 nhóm nhỏ - IN PROGESS.
- Hướng dẫn , triển khai cho toàn bộ beelogistics.cloud users - WAITING.

#### Giai Đoạn 2 tháng 10 - 12:

- BFS One tích hợp , sử dụng keycloak
- Tích hợp với một số phần mềm khác như Moodle LMS.

### Team OF1 - CRM

#### Giai Đoạn 3 tháng 7 - 9: (Đàn, Nhật, An)

1. Task Request: Công cụ request lỗi cho kế toán. (HRM)
Requirements:
Implements:
Reviews:
2. Chức năng book lịch phòng họp + xe (triển khai cho HPH/ HAN)
Requirements:
Implements:
Reviews:
3. Setup và triển khai Pricing cho BEE VP nước ngoài.
Requirements:
Implements:
Reviews:


Keycloak Integration:


- DONE - Tổ chức lại các app, web documentation cho of1 platform.
- DONE - Review account trong hệ thống, liên kết với các entity khác bằng account_id thay vì login_id.
- DONE - Chức năng book lịch phòng họp + xe (triển khai cho HPH/ HAN)
- DONE - Quản lý công việc hàng ngày của team BD Support liên quan tới lịch Event, chi phí tham gia hiệp hội, theo dõi hợp đồng Agent.
- DONE - Đưa quy trình request/ approve và quản lý thông tin khách hàng qua CRM mới.
- DONE - Setup và triển khai Pricing cho BEE VP nước ngoài.
- DONE - Api với hệ thống HRM để tự động hoá việc tạo account.

- INPROGRESS - Report cho BD về Volume, Profit, Revenue, Agent Transactions, Sale Teams.
Vướng nhiều ở data nguồn, hiện tại đang dùng bee legacy report, không đảm bảo chính xác do sync data set lớn.
- INPROGRESS - Tunning công việc cho team BD qua Daily Tasks. Theo dõi công việc hằng ngày, cuộc họp, tham dự conference.

#### Giai Đoạn 2 tháng 10 - 12: (Đàn, Nhật, An, Đức)

- Kết với với team vận hành HPH/ HCM triển khai pricing HCM.
- Hoàn thiện quy trình công việc/ báo cáo cho team BD.
- Sync data real-time từ bfsone qua bee legacy report. Dùng công nghệ [**debezium + kafka**](https://github.com/ngcdan/debezium-kafka-demo)** demo với a Quý.**
- Tách db cho TMS.
- Triển khai báo cáo tuần thay thế báo cáo tuần trên CRM cũ cho toàn VP.
- Hoàn thiện các chức năng CRM cho sales, cắt CRM cũ.
- Phiếu đánh giá KPI cho năm (request chị Huyền)

**Keycloak Integration:**

---

Xem thêm: [[datatp-overview]]
