---
title: "Change Data Capture (CDC) với Debezium"
tags:
  - datatp
  - cdc
  - debezium
  - kafka
---

###  1. Bật Change Data Capture (CDC) trên SQL Server (MSSQL)

- Kích hoạt CDC cho database (ví dụ: `MyDatabase`)

```javascript
USE MyDatabase;
GO

-- Bật CDC cho database
EXEC sys.sp_cdc_enable_db;
GO

-- Kiem tra
SELECT name, is_cdc_enabled
FROM sys.databases
WHERE name = 'MyDatabase';
```

`is_cdc_enabled = 1` nghĩa là đã bật CDC.

![[Screenshot_2025-10-27_at_14.15.45.png]]

![[Screenshot_2025-10-27_at_14.16.17.png]]

- Kích hoạt CDC cho từng bảng

```javascript
USE MyDatabase;
GO

EXEC sys.sp_cdc_enable_table
    @source_schema           = N'dbo',
    @source_name             = N'Employees',
    @role_name               = NULL,           -- Nếu muốn giới hạn quyền xem change, có thể đặt role
    @filegroup_name          = N'cdc',          -- Tên filegroup lưu trữ bảng log CDC (tùy chọn)
    @supports_net_changes    = 1;               -- 1 để theo dõi net changes, 0 để false
GO
```

Tham số chính:

- `@source_schema`: schema của bảng (thường là `dbo`).
- `@source_name`: tên bảng.
- `@role_name`: nếu chỉ định, chỉ người trong role này mới xem được data change. Để NULL nếu cho phép mọi user có quyền SELECT trên cdc schema.
- `@filegroup_name`: nếu bạn có filegroup chuyên dụng cho CDC, đặt tên filegroup này, nếu không có thì để NULL hoặc bỏ qua.
- `@supports_net_changes`: bật tính năng net changes (giúp chỉ lấy delta) – thiết lập 0 hoặc 1.

![[Screenshot_2025-10-27_at_14.29.03.png]]

Bạn có thể kiểm tra bảng nào đã bật CDC:

```javascript
SELECT s.name AS schema_name,
       t.name AS table_name,
       is_tracked_by_cdc
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE is_tracked_by_cdc = 1;
```

Kiểm tra và sử dụng CDC.

SQL SERVER tạo scheme cdc, để truy vấn dữ liệu thay đổi: 

```javascript
-- Lấy full changes trong khoảng LSN
DECLARE @from_lsn binary(10), @to_lsn binary(10);

-- Lấy LSN hiện tại
SET @from_lsn = sys.fn_cdc_get_min_lsn('dbo_Employees');
SET @to_lsn   = sys.fn_cdc_get_max_lsn();

-- Lấy changes
SELECT *
FROM cdc.fn_cdc_get_all_changes_dbo_Employees(@from_lsn, @to_lsn, 'all');
```

Tắt CDC: 

```javascript
-- tat cho bang
EXEC sys.sp_cdc_disable_table
    @source_schema = N'dbo',
    @source_name   = N'Employees',
    @capture_instance = N'dbo_Employees';  -- tên instance thường là schema_tênbảng
GO

-- tat cho database
USE MyDatabase;
GO
EXEC sys.sp_cdc_disable_db;
GO
```


Khi bật CDC cho một bảng, sql server tạo ra một bảng thay đổi (change table) trong schema cdc (ví dụ cdc.dbo_Partners_CT)

CDC đọc transaction log để lấy thay đổi (job capture).


**Best practices / khuyến nghị:**
• Đặt filegroup CDC trên disk riêng (tách khỏi file dữ liệu chính và transaction log) để giảm cạnh tranh I/O và dễ quản lý dung lượng.




 PGPASSWORD="postgres" psql -h "postgres.of1-dev-crm.svc.cluster.local" -p "5432" -U "postgres" -d "datatp_crm_db”

```javascript
 PGPASSWORD="postgres" psql -h "postgres.of1-dev-crm.svc.cluster.local" -p "5432" -U "postgres" -d "datatp_crm_db"
 brew services stop  postgresql@16
 
 SELECT count(*) FROM pg_replication_slots WHERE slot_name = 'debezium_slot';
 SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');
 
```

![[Screenshot_2026-01-10_at_09.33.34.png]]

kns-ctl of1-dev-crm get services,pods

![[Screenshot_2026-01-10_at_10.19.02.png]]


**Kafka Connect - CDC Pipeline (PostgreSQL → Kafka)**

### (1) Giải thích ngắn gọn

Đây là giải pháp giúp tự động truyền tải mọi thay đổi dữ liệu (thêm, sửa, xóa) từ PostgreSQL sang Kafka theo thời gian thực (real-time). Thay vì phải viết code để truy vấn database liên tục (polling), hệ thống này "lắng nghe" các thay đổi và đẩy chúng vào Kafka dưới dạng các sự kiện (events).

### (2) Bản chất / cơ chế

Hệ thống vận hành dựa trên sự kết hợp của 4 thành phần chính:

- **PostgreSQL WAL (Write-Ahead Log):** Mọi thay đổi dữ liệu đều được ghi vào file log này trước khi lưu chính thức vào bảng. Để CDC hoạt động, Postgres cần cấu hình `wal_level = logical` để ghi lại chi tiết các thay đổi,.
- **Debezium:** Một công cụ mã nguồn mở đóng vai trò là "người đọc log". Nó kết nối với Postgres như một máy con (replication client), đọc các dòng log WAL, sau đó phân tích (parse) chúng thành các thông điệp dữ liệu,.
- **Kafka Connect:** Framework trung gian quản lý Debezium, giúp chạy các tiến trình kết nối một cách ổn định, tự động xử lý lỗi và quản lý vị trí đọc dữ liệu (offset) mà không cần viết code (config bằng JSON qua REST API),.
- **Kafka Broker:** Nơi lưu trữ cuối cùng của các sự kiện. Mỗi bảng trong database thường sẽ tương ứng với một topic trong Kafka.

### (3) Minh họa

Giả sử bạn có một bảng `users` và thực hiện một lệnh cập nhật:

1. **Thao tác:** Bạn chạy lệnh `UPDATE users SET name = 'An' WHERE id = 1;`.
2. **Xử lý:**
    - Postgres ghi nhận thay đổi này vào WAL.
    - Debezium phát hiện thay đổi qua **Logical Replication Slot** (một dạng "đánh dấu" vị trí đọc trên log),.
    - Debezium gửi một message vào Kafka topic tên là `dbserver1.public.users`.
3. **Kết quả trong Kafka:** Bạn nhận được một JSON message chứa:
    - `before`: Dữ liệu cũ (ví dụ: `name: 'Bình'`).
    - `after`: Dữ liệu mới (`name: 'An'`).
    - `op`: `u` (viết tắt của Update),.

### (4) Ghi chú quan trọng

- **REPLICA IDENTITY FULL:** Đây là cài đặt bắt buộc trên các bảng Postgres nếu bạn muốn Kafka nhận được đầy đủ dữ liệu cũ ("before") khi có lệnh UPDATE hoặc DELETE,. Nếu để mặc định, bạn có thể chỉ nhận được ID của dòng bị xóa.
- **Replication Slot:** Cần được giám sát kỹ vì nó sẽ giữ lại các file log trên ổ cứng Postgres cho đến khi Debezium xác nhận đã đọc xong. Nếu Debezium ngừng chạy lâu, ổ cứng database có thể bị đầy.
- **Ưu điểm so với Polling:** CDC không gây tải cho database vì nó không thực hiện lệnh `SELECT` liên tục. Nó có độ trễ cực thấp (< 1 giây) và đảm bảo không bỏ sót bất kỳ thay đổi nào, kể cả khi dữ liệu thay đổi nhanh chóng,.
- **Snapshot:** Khi bắt đầu chạy lần đầu (initial), Debezium sẽ thực hiện quét toàn bộ dữ liệu hiện có trong bảng để đồng bộ hóa trạng thái ban đầu vào Kafka trước khi chuyển sang chế độ stream các thay đổi mới,.
- **Best Practice:** Trong môi trường Production, nên sử dụng **Avro Converter** thay vì JSON thuần túy để giảm kích thước dữ liệu (30-40%) và quản lý cấu trúc dữ liệu (Schema) tốt hơn.

---

## Liên quan

- [[cdc-architecture|CDC Architecture - BF1 Pipeline]]
- [[datatp-overview|DataTP - Tổng quan dự án]]
- [[devlog|Developer Log (BF1)]]



