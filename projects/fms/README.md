# FMS — Freight Management System

> Hệ thống quản lý vận tải hàng hoá, thay thế BF1 cũ (MSSQL) trên nền tảng mới.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Java Spring Boot |
| Message Broker | Apache Kafka |
| Frontend | React + TypeScript |
| Database | PostgreSQL |
| CDC Source | MSSQL via Debezium |

## Tổng quan 2 giai đoạn

### Giai đoạn 1: Read-First Migration

**Mục tiêu:** Nhanh chóng hình thành nền tảng mới có dữ liệu đầy đủ để phục vụ tra cứu, kiểm tra và đối soát, trong khi hệ thống cũ vẫn tiếp tục xử lý nghiệp vụ chính.

**Các hoạt động chính:**
- Replicate/đồng bộ dữ liệu realtime từ DB cũ (MSSQL) sang DB mới (PostgreSQL) qua CDC pipeline
- Ưu tiên implement các chức năng read: báo cáo, tra cứu, view data, dashboard và các màn hình theo dõi nghiệp vụ
- Xây dựng form và màn hình hiển thị đúng, đủ thông tin theo nhu cầu vận hành thực tế
- Tổ chức kiểm tra dữ liệu, đối chiếu màn hình và xác nhận tính đúng đắn với người dùng
- Chuẩn hóa data model, mapping dữ liệu và luồng hiển thị trước khi xử lý bài toán ghi dữ liệu
- Giải quyết sớm các bài toán sync dữ liệu, đọc dữ liệu realtime, tích hợp với CRM, TMS

### Giai đoạn 2: Write-Back Integration

**Mục tiêu:** Sau khi nền tảng mới đã đọc dữ liệu ổn định và được kiểm chứng, từng bước chuyển nghiệp vụ ghi dữ liệu sang hệ thống mới.

**Các hoạt động chính:**
- Implement các chức năng write trên hệ thống mới, lưu dữ liệu vào database mới
- Thiết kế cơ chế đồng bộ ngược từ hệ thống mới về hệ thống cũ (ghi ngược MSSQL) để bảo đảm hai hệ thống vẫn chạy song song
- Xây dựng pipeline sử dụng Kafka để publish message từ hệ thống mới và cập nhật ngược vào database cũ
- Bảo đảm dữ liệu ghi ngược về hệ thống cũ đúng cấu trúc, đúng mapping và đủ thông tin cho các chức năng kế toán
- Áp dụng rollout theo từng nhóm chức năng và từng nhóm người dùng, bắt đầu từ các nghiệp vụ ít rủi ro hơn
- Tăng dần phạm vi write trên hệ thống mới khi kết quả test, pilot run và đối soát đã ổn định

## Navigation

| Section | Nội dung |
|---|---|
| [Architecture](architecture.md) | Kiến trúc tổng thể, CDC pipeline, Kafka, config |
| [Schema — Catalogue](schema/catalogue.md) | Partner, User/Role, Master Data |
| [Schema — Sales](schema/sales.md) | Quotation, Booking, Vessel Schedule |
| [Schema — Documentation](schema/documentation.md) | Transactions, House Bill, Cargo, Tracking |
| [Schema — Accounting](schema/accounting.md) | Invoice, Payment, P&L |
| [API — Catalogue](api/catalogue.md) | Partner, User APIs |
| [API — Sales](api/sales.md) | Quotation, Booking APIs |
| [API — Documentation](api/documentation.md) | Shipment, House Bill APIs |
| [API — Accounting](api/accounting.md) | Invoice, Payment APIs |
| [Module — Catalogue](modules/catalogue.md) | Flow quản lý đối tác, danh mục |
| [Module — Sales](modules/sales.md) | Flow Inquiry → Quotation → Booking |
| [Module — Documentation](modules/documentation.md) | Flow Booking → Shipment → Chứng từ |
| [Module — Accounting](modules/accounting.md) | Flow Invoice → Payment → Báo cáo |

## Trạng thái module

| Module | Schema | API | Nghiệp vụ | Owner | Status |
|---|---|---|---|---|---|
| Catalogue | [ ] | [ ] | [ ] | — | planned |
| Sales | [ ] | [ ] | [ ] | — | planned |
| Documentation | [ ] | [ ] | [ ] | — | planned |
| Accounting | [ ] | [ ] | [ ] | — | planned |
