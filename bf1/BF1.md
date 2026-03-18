# BF1 Upgrade

## Bối cảnh

BF1 hiện tại vẫn gắn chặt với các chức năng kế toán trên hệ thống cũ, nên việc thay thế hoàn toàn trong ngắn hạn là chưa khả thi. Trong giai đoạn chuyển tiếp, hệ thống mới vẫn cần bảo đảm khả năng ghi ngược dữ liệu về hệ thống cũ theo đúng cấu trúc và mapping cần thiết để các chức năng kế toán hiện tại tiếp tục vận hành ổn định.

## Hướng tiếp cận

Thay vì làm lại toàn bộ BF1 từ đầu, hướng đề xuất là phát triển theo **2 giai đoạn** để giảm thời gian chờ, giảm rủi ro và tận dụng hệ thống cũ trong quá trình chuyển đổi.

### Giai đoạn 1: Read-First Migration

**Mục tiêu:** Nhanh chóng hình thành nền tảng mới có dữ liệu đầy đủ để phục vụ tra cứu, kiểm tra và đối soát, trong khi hệ thống cũ vẫn tiếp tục xử lý nghiệp vụ chính.

- Tạo database mới trên nền PostgreSQL cho BF1 mới.
- **Replicate/đồng bộ dữ liệu realtime từ DB cũ (MSSQL) sang DB mới (PostgreSQL)** — chi tiết xem [mục bên dưới](#chi-tiết-cdc-pipeline-mssql--kafka--postgresql).
- Ưu tiên implement các chức năng read trước: báo cáo, tra cứu, view data, dashboard và các màn hình theo dõi nghiệp vụ.
- Xây dựng form và màn hình hiển thị đúng, đủ thông tin theo nhu cầu vận hành thực tế.
- Tổ chức kiểm tra dữ liệu, đối chiếu màn hình và xác nhận tính đúng đắn với người dùng.
- Dùng giai đoạn này để chuẩn hóa data model, mapping dữ liệu và luồng hiển thị trước khi xử lý bài toán ghi dữ liệu.
- Có thể giải quyết sớm các bài toán sync dữ liệu, đọc dữ liệu realtime, tích hợp với các hệ thống liên quan như CRM, TMS.

### Giai đoạn 2: Write-Back Integration

**Mục tiêu:** Sau khi nền tảng mới đã đọc dữ liệu ổn định và được kiểm chứng, từng bước chuyển nghiệp vụ ghi dữ liệu sang hệ thống mới.

- Implement các chức năng write trên hệ thống mới, lưu dữ liệu vào database mới.
- Thiết kế cơ chế đồng bộ ngược từ hệ thống mới về hệ thống cũ để bảo đảm hai hệ thống vẫn chạy song song trong giai đoạn chuyển tiếp.
- Xây dựng pipeline sử dụng Kafka để publish message từ hệ thống mới và cập nhật ngược vào database cũ, hoặc đấu nối qua API tùy theo từng luồng nghiệp vụ và khả năng tích hợp của hệ thống cũ.
- Bảo đảm dữ liệu ghi ngược về hệ thống cũ đúng cấu trúc, đúng mapping và đủ thông tin để các chức năng kế toán trên hệ thống cũ tiếp tục sử dụng được.
- Áp dụng rollout theo từng nhóm chức năng và từng nhóm người dùng, bắt đầu từ các nghiệp vụ ít rủi ro hơn.
- Tăng dần phạm vi write trên hệ thống mới khi kết quả test, pilot run và đối soát đã ổn định.

## Lợi ích

- Rút ngắn thời gian triển khai bằng cách ưu tiên hoàn thiện từng phần trước khi thay thế toàn bộ ứng dụng.
- Giảm rủi ro khi chưa cần thay thế toàn bộ app và chức năng ngay từ đầu.
- Tạo điều kiện kiểm tra sớm dữ liệu và giao diện trên nền tảng mới, hỗ trợ vận hành song song với hệ thống cũ và rollout theo từng nhóm chức năng, nhóm người dùng.
- Tạo nền tảng dùng chung cho các nhu cầu đồng bộ dữ liệu realtime và tích hợp với CRM, TMS và các hệ thống liên quan.
- Giữ được khả năng vận hành các chức năng kế toán trên hệ thống cũ trong khi từng bước chuyển nghiệp vụ sang nền tảng mới.

---

## Chi tiết: CDC Pipeline (MSSQL → Kafka → PostgreSQL)

### Kiến trúc tổng thể

```
MSSQL (BF1 DB cũ)  ──CDC──►  Debezium Connect  ──►  Kafka  ──►  Kafka Consumer  ──►  PostgreSQL (BF1 DB mới)
```

| Component | Version | Vai trò | Trạng thái |
|---|---|---|---|
| SQL Server CDC | Built-in | Bắt thay đổi từ transaction log, ghi vào bảng `cdc.*` | Đã setup cho ECUS, cần bật thêm cho BF1 DB |
| Debezium Connect | 2.4 | Đọc bảng CDC, chuyển thành Kafka message (JSON) | Đã setup, có manage.py quản lý |
| Kafka | 7.5.0 (Confluent) | Message broker, lưu trữ CDC events theo topic | Đã setup (dev + prod cluster) |
| Kafka Consumer | — | Đọc message từ Kafka, transform và ghi vào PostgreSQL | **Chưa có — cần implement** |
| PostgreSQL | — | Database mới cho BF1 | **Cần tạo mới** |

### Thông tin kết nối MSSQL Prod

> Credentials lưu tại `env.sh` (đã gitignore, không commit).

```bash
source env.sh
```

| Thông tin | Giá trị |
|---|---|
| Host | `of1.beelogistics.com` |
| Port | `34541` |
| Database | `BEE_DB` |
| Username | `devhph` |
| JDBC URL | `jdbc:sqlserver://of1.beelogistics.com:34541;databaseName=BEE_DB;encrypt=true;trustServerCertificate=true;` |

**Target table hiện tại:** `PARTNERS`

---

### Bước 0: Setup BF1 software và DB trên VM/Windows

#### 0a. Chuẩn bị Windows Server VM

```powershell
# Kiểm tra Windows version
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Kiểm tra .NET Framework (BF1 cần .NET)
reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Version

# Mở port cần thiết trên Windows Firewall
netsh advfirewall firewall add rule name="MSSQL" dir=in action=allow protocol=tcp localport=1433
netsh advfirewall firewall add rule name="BF1 Web" dir=in action=allow protocol=tcp localport=80
netsh advfirewall firewall add rule name="BF1 Web HTTPS" dir=in action=allow protocol=tcp localport=443
```

#### 0b. Cài đặt SQL Server

1. Download SQL Server (Developer hoặc Standard) từ Microsoft.
2. Chạy installer, chọn:
   - Database Engine Services
   - SQL Server Agent (bắt buộc — CDC cần Agent)
   - Full-Text Search (nếu cần)
3. Authentication mode: **Mixed Mode** (SQL Server + Windows Authentication).
4. Đặt sa password.

```powershell
# Kiểm tra SQL Server service đang chạy
Get-Service -Name "MSSQLSERVER"
Get-Service -Name "SQLSERVERAGENT"

# Đảm bảo SQL Server Agent tự khởi động cùng Windows
Set-Service -Name "SQLSERVERAGENT" -StartupType Automatic
Start-Service -Name "SQLSERVERAGENT"
```

#### 0c. Cài đặt SQL Server Management Studio (SSMS)

Download SSMS từ Microsoft, cài đặt, kết nối vào SQL Server bằng sa account.

#### 0d. Restore BF1 database từ file backup (.bak)

```sql
-- Xem danh sách logical file names trong file backup
RESTORE FILELISTONLY FROM DISK = N'C:\Backup\BEE_DB.bak';

-- Restore database
RESTORE DATABASE [BEE_DB]
FROM DISK = N'C:\Backup\BEE_DB.bak'
WITH
  MOVE N'BEE_DB_Data' TO N'C:\SQLData\BEE_DB.mdf',
  MOVE N'BEE_DB_Log'  TO N'C:\SQLData\BEE_DB_log.ldf',
  REPLACE,
  STATS = 10;

-- Kiểm tra
SELECT name, state_desc FROM sys.databases WHERE name = 'BEE_DB';
```

#### 0e. Deploy BF1 application

BF1 là ứng dụng .NET, chạy trên IIS/Windows Server. Phần deploy do **anh Quý** phụ trách — liên hệ anh Quý để cài đặt và cấu hình.

---

### Bước 1: Dump / Backup BF1 database

#### Backup full database (.bak)

```sql
-- Backup full (chạy trên SSMS hoặc sqlcmd)
BACKUP DATABASE [BEE_DB]
TO DISK = N'C:\Backup\BEE_DB_full_20260317.bak'
WITH
  FORMAT,
  INIT,
  NAME = N'BF1 Full Backup',
  COMPRESSION,
  STATS = 10;

-- Kiểm tra backup
RESTORE HEADERONLY FROM DISK = N'C:\Backup\BEE_DB_full_20260317.bak';
```

#### Backup bằng sqlcmd (command line)

```bash
# Từ Windows CMD hoặc PowerShell
sqlcmd -S localhost -U sa -P "PASSWORD" -Q "BACKUP DATABASE [BEE_DB] TO DISK = N'C:\Backup\BEE_DB_full.bak' WITH FORMAT, COMPRESSION, STATS = 10"

# Từ Linux/Mac qua Docker
docker run --rm -it mcr.microsoft.com/mssql-tools \
  /opt/mssql-tools/bin/sqlcmd -S HOST,1433 -U sa -P "PASSWORD" \
  -Q "BACKUP DATABASE [BEE_DB] TO DISK = N'C:\Backup\BEE_DB_full.bak' WITH FORMAT, COMPRESSION"
```

#### Export schema only (không data)

```bash
# Dùng mssql-scripter (Python tool)
pip install mssql-scripter
mssql-scripter -S localhost -d BF1 -U sa -P "PASSWORD" \
  --schema-only -f BF1_schema.sql

# Hoặc dùng SSMS: Database → Tasks → Generate Scripts → Schema Only
```

#### Export data ra CSV (từng bảng)

```bash
# Dùng bcp (SQL Server bulk copy)
bcp "SELECT * FROM BEE_DB.dbo.Partners" queryout "C:\Export\Partners.csv" \
  -S localhost -U sa -P "PASSWORD" -c -t "," -r "\n"

# Export tất cả bảng (PowerShell script)
$tables = sqlcmd -S localhost -U sa -P "PASSWORD" -d BF1 -h -1 -Q "SELECT name FROM sys.tables"
foreach ($t in $tables) {
  $t = $t.Trim()
  if ($t) {
    bcp "BEE_DB.dbo.$t" out "C:\Export\$t.csv" -S localhost -U sa -P "PASSWORD" -c -t "," -r "\n"
  }
}
```

---

### Bước 2: Restore BF1 database (trên môi trường dev/test)

#### Restore từ .bak file

```sql
-- Xem logical file names
RESTORE FILELISTONLY FROM DISK = N'C:\Backup\BEE_DB_full_20260317.bak';

-- Restore thành database mới (không ghi đè DB gốc)
RESTORE DATABASE [BEE_DB_DEV]
FROM DISK = N'C:\Backup\BEE_DB_full_20260317.bak'
WITH
  MOVE N'BEE_DB_Data' TO N'C:\SQLData\BEE_DB_DEV.mdf',
  MOVE N'BEE_DB_Log'  TO N'C:\SQLData\BEE_DB_DEV_log.ldf',
  REPLACE,
  STATS = 10;
```

#### Copy database giữa 2 server

```bash
# Cách 1: Backup trên server A, copy file .bak sang server B, restore
# (đơn giản, phù hợp cho DB vừa và nhỏ)

# Cách 2: Dùng SSMS → Tasks → Copy Database Wizard

# Cách 3: Backup to network share
sqlcmd -S SERVER_A -U sa -P "PASSWORD" -Q "BACKUP DATABASE [BEE_DB] TO DISK = N'\\share\BEE_DB.bak' WITH COMPRESSION"
sqlcmd -S SERVER_B -U sa -P "PASSWORD" -Q "RESTORE DATABASE [BEE_DB] FROM DISK = N'\\share\BEE_DB.bak' WITH MOVE N'BEE_DB_Data' TO N'D:\Data\BEE_DB.mdf', MOVE N'BEE_DB_Log' TO N'D:\Data\BEE_DB_log.ldf', REPLACE"
```

---

### Bước 3: Xác định scope bảng cần sync

- Khảo sát database BF1 hiện tại trên MSSQL:

```sql
-- Liệt kê tất cả bảng + số rows + dung lượng
SELECT
  t.name AS table_name,
  p.rows AS row_count,
  CAST(ROUND(SUM(a.total_pages) * 8.0 / 1024, 2) AS DECIMAL(18,2)) AS size_mb
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.is_ms_shipped = 0
GROUP BY t.name, p.rows
ORDER BY p.rows DESC;

-- Xem quan hệ foreign key
SELECT
  fk.name AS fk_name,
  OBJECT_NAME(fk.parent_object_id) AS child_table,
  OBJECT_NAME(fk.referenced_object_id) AS parent_table
FROM sys.foreign_keys fk
ORDER BY parent_table, child_table;
```

- Phân loại bảng theo mức ưu tiên:
  - **P0 — Bảng master/danh mục:** ít thay đổi, cần có đầu tiên để hiển thị được giao diện.
  - **P1 — Bảng nghiệp vụ chính:** thay đổi thường xuyên, cần sync realtime.
  - **P2 — Bảng phụ/lịch sử:** sync sau hoặc batch import.
- Xác nhận danh sách bảng cần bật CDC với anh Quý (dựa trên nghiệp vụ thực tế).

#### Bảng target hiện tại: `Partners` (BEE_DB)

- **Rows:** 52,367 — **Size:** 82.38 MB
- **Primary Key:** `PartnerID` (nvarchar(100))

**Các cột chính:**

| Cột | Type | Mô tả |
|---|---|---|
| `PartnerID` | nvarchar(100) NOT NULL | PK — mã đối tác |
| `DateCreate` | datetime | Ngày tạo |
| `DateModify` | datetime | Ngày cập nhật |
| `PartnerName` | nvarchar(300) | Tên viết tắt |
| `PartnerName2` | nvarchar(300) | Tên tiếng Anh |
| `PartnerName3` | nvarchar(510) | Tên đầy đủ tiếng Việt |
| `PersonalContact` | nvarchar(300) | Người liên hệ |
| `Email` | nvarchar(510) | Email |
| `Address` | nvarchar(510) | Địa chỉ |
| `Taxcode` | nvarchar(100) | Mã số thuế |
| `Country` | nvarchar(100) | Quốc gia |
| `Group` | nvarchar(100) | Nhóm (CUSTOMERS, ...) |
| `GroupType` | nvarchar(300) | Loại nhóm |
| `ContactID` | nvarchar(100) | Mã contact liên kết |
| `Category` | nvarchar(300) | Phân loại (CUSTOMER, AIRLINE, ...) |
| `AccRef` | nvarchar(100) | Mã kế toán tham chiếu |
| `Denied` | bit | Bị chặn |
| `Status` | bit | Trạng thái |
| `BankAccsNo` | nvarchar(100) | Số tài khoản ngân hàng |
| `BankName` | nvarchar(MAX) | Tên ngân hàng |
| `PaymentTerm` | int | Kỳ thanh toán |
| `Industry` | nvarchar(100) | Ngành nghề |

**Bảng liên quan (Foreign Keys tham chiếu đến Partners):**

| Bảng con | Cột FK | Relationship |
|---|---|---|
| `DebitNotes` | PartnerID | Công nợ |
| `DebitNoteDetails_Other` | PartnerID | Chi tiết công nợ |
| `TransactionDetails` | ShipperID | Giao dịch vận chuyển |
| `InvoiceReference` | ShipperID | Hóa đơn |
| `BookingRateRequest` | PartnerID | Yêu cầu báo giá |
| `HandleInstructions` | PartnerID | Hướng dẫn xử lý |
| `HandleServiceRate` | PartnerID | Bảng giá dịch vụ |
| `PODetail` | VendorCode | Chi tiết PO |
| `ProfitShares` | PartnerID | Chia lợi nhuận |
| `Partner_BankInfo` | PartnerID | Thông tin ngân hàng |
| `Partner_BankInfo_Comp` | PartnerID | Thông tin ngân hàng (company) |

---

### Bước 4: Bật CDC trên SQL Server cho BF1 database

> Yêu cầu: quyền sysadmin, SQL Server Agent phải đang chạy.

```sql
-- 4a. Kiểm tra SQL Server Agent
EXEC xp_servicecontrol 'QueryState', 'SQLServerAgent';
-- Kết quả phải là "Running."
-- Nếu chưa chạy, start từ Services hoặc:
-- EXEC xp_servicecontrol 'Start', 'SQLServerAgent';

-- 4b. Bật CDC ở mức database
USE [BEE_DB];
EXEC sys.sp_cdc_enable_db;
GO

-- 4c. Kiểm tra database đã bật CDC
SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'BEE_DB';
-- is_cdc_enabled = 1 là OK

-- 4d. Bật CDC cho từng bảng (lặp cho mỗi bảng trong scope)
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'Partners',
  @role_name     = NULL,
  @supports_net_changes = 0;
GO
-- Lặp lại cho mỗi bảng P0 + P1

-- 4e. Bật CDC hàng loạt (tất cả bảng trong schema dbo)
DECLARE @name NVARCHAR(128);
DECLARE cur CURSOR FOR
  SELECT t.name FROM sys.tables t
  JOIN sys.schemas s ON t.schema_id = s.schema_id
  WHERE s.name = 'dbo' AND t.is_tracked_by_cdc = 0;
OPEN cur;
FETCH NEXT FROM cur INTO @name;
WHILE @@FETCH_STATUS = 0
BEGIN
  EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = @name,
    @role_name = NULL,
    @supports_net_changes = 0;
  PRINT 'Enabled CDC for: ' + @name;
  FETCH NEXT FROM cur INTO @name;
END
CLOSE cur; DEALLOCATE cur;
GO

-- 4f. Kiểm tra kết quả
SELECT
  s.name AS schema_name,
  t.name AS table_name,
  t.is_tracked_by_cdc
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'dbo'
ORDER BY t.is_tracked_by_cdc DESC, t.name;

-- 4g. Kiểm tra CDC jobs đang chạy
EXEC sys.sp_cdc_help_jobs;
```

---

### Bước 5: Tạo user Debezium và cấp quyền

```sql
-- 5a. Tạo login (chạy trên master)
USE [master];
CREATE LOGIN debezium WITH PASSWORD = 'THAY_PASSWORD_MANH';
GO

-- 5b. Tạo user + cấp quyền trên BF1 database
USE [BEE_DB];
CREATE USER debezium FOR LOGIN debezium;

-- Quyền đọc CDC tables
GRANT SELECT ON SCHEMA::cdc TO debezium;
GRANT EXECUTE ON SCHEMA::cdc TO debezium;

-- Quyền đọc data và xem trạng thái DB
GRANT VIEW DATABASE STATE TO debezium;
ALTER ROLE db_datareader ADD MEMBER debezium;
GO

-- 5c. (Tùy chọn) Cấp db_owner nếu connector cần snapshot initial
ALTER ROLE db_owner ADD MEMBER debezium;
GO

-- 5d. Kiểm tra quyền
SELECT dp.name, dp.type_desc, p.permission_name, p.state_desc
FROM sys.database_permissions p
JOIN sys.database_principals dp ON p.grantee_principal_id = dp.principal_id
WHERE dp.name = 'debezium';
```

---

### Bước 6: Kết nối Kafka & Debezium trên K8s

Kafka và Debezium Connect đã được deploy sẵn trên K8s cluster. Không dùng Docker local.

#### Thông tin K8s services

| Component | Dev (namespace: `of1-dev-kafka`) | Prod (namespace: `of1-prod-kafka`) |
|---|---|---|
| Kafka bootstrap | `server-01.of1-dev-kafka.svc:9092`, `server-02...`, `server-03...` | `server-01.of1-prod-kafka.svc:9092`, `server-02...`, `server-03...` |
| Debezium Connect | `debezium-connect.of1-dev-kafka.svc.cluster.local:8083` | `debezium-connect.of1-prod-kafka.svc.cluster.local:8083` |
| Kafka UI | http://webui.of1-dev-kafka.svc.cluster.local/ | http://webui.of1-prod-kafka.svc.cluster.local/ |
| Debezium UI | http://debezium-ui.of1-dev-kafka.svc.cluster.local/ | http://debezium-ui.of1-prod-kafka.svc.cluster.local/ |

#### Port-forward để thao tác từ máy local

```bash
# Port-forward Debezium Connect (dev) — cần cho curl commands
kubectl port-forward -n of1-dev-kafka svc/debezium-connect 8083:8083 &

# Port-forward Kafka broker (dev) — để dùng kafka CLI tools
kubectl port-forward -n of1-dev-kafka svc/server-01 9092:9092 &

# Kiểm tra Debezium Connect đã sẵn sàng
curl -s http://localhost:8083/ | jq
```

```bash
# Port-forward cho Prod
kubectl port-forward -n of1-prod-kafka svc/debezium-connect 8083:8083 &
```

**Web UI (truy cập trực tiếp, không cần port-forward):**
- Kafka UI dev: http://webui.of1-dev-kafka.svc.cluster.local/
- Kafka UI prod: http://webui.of1-prod-kafka.svc.cluster.local/
- Debezium UI dev: http://debezium-ui.of1-dev-kafka.svc.cluster.local/
- Debezium UI prod: http://debezium-ui.of1-prod-kafka.svc.cluster.local/

#### Kiểm tra trạng thái services trên K8s

```bash
# Xem pods
kubectl get pods -n of1-dev-kafka
kubectl get pods -n of1-prod-kafka

# Xem logs Debezium Connect
kubectl logs -n of1-dev-kafka deploy/debezium-connect --tail=100 -f

# Xem logs Kafka broker
kubectl logs -n of1-dev-kafka pod/server-01 --tail=100
```

---

### Bước 7: Đăng ký Debezium connector cho BF1

#### 7a. Tạo file config connector

Tạo file `bf1-connector.json`:

```json
{
  "name": "mssql-bf1-connector",
  "config": {
    "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector",
    "tasks.max": "1",

    "database.hostname": "${BF1_MSSQL_HOST}",
    "database.port": "${BF1_MSSQL_PORT}",
    "database.user": "${BF1_MSSQL_USER}",
    "database.password": "${BF1_MSSQL_PASS}",
    "database.names": "BEE_DB",
    "database.applicationName": "Debezium-BF1",

    "topic.prefix": "cdc-bf1",
    "table.include.list": "dbo.Partners",

    "schema.history.internal.kafka.bootstrap.servers": "server-01.of1-dev-kafka.svc:9092,server-02.of1-dev-kafka.svc:9092,server-03.of1-dev-kafka.svc:9092",
    "schema.history.internal.kafka.topic": "dbhistory.cdc-bf1",

    "snapshot.mode": "initial",
    "decimal.handling.mode": "string",
    "time.precision.mode": "adaptive",

    "query.fetch.size": "10000",
    "max.batch.size": "1024",
    "max.queue.size": "2048",
    "poll.interval.ms": "1000",

    "producer.override.max.request.size": "52428800",
    "producer.override.buffer.memory": "104857600",
    "producer.override.compression.type": "snappy",

    "transforms": "unwrap_schema",
    "transforms.unwrap_schema.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.unwrap_schema.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.unwrap_schema.replacement": "$1.$3"
  }
}
```

> **Lưu ý:**
> - `database.hostname`: đổi thành IP/hostname của SQL Server VM
> - `table.include.list`: thay bằng danh sách bảng thực tế, hoặc dùng `dbo.*` để capture tất cả
> - `snapshot.mode`: dùng `initial` lần đầu (full snapshot), sau đó đổi thành `schema_only`

#### 7b. Đăng ký connector

```bash
# Xóa connector cũ (nếu có)
curl -X DELETE http://localhost:8083/connectors/mssql-bf1-connector 2>/dev/null

# Đăng ký connector mới
curl -X POST http://localhost:8083/connectors/ \
  -H "Content-Type: application/json" \
  -d @bf1-connector.json | jq

# Kiểm tra status
curl -s http://localhost:8083/connectors/mssql-bf1-connector/status | jq
```

Kết quả mong đợi:
```json
{
  "name": "mssql-bf1-connector",
  "connector": { "state": "RUNNING" },
  "tasks": [{ "id": 0, "state": "RUNNING" }]
}
```

#### 7c. Xác nhận dữ liệu đang chảy

```bash
# Xem danh sách topics (qua port-forward 8083)
curl -s http://localhost:8083/connectors/mssql-bf1-connector/topics | jq

# Xem messages trên 1 topic (kubectl exec vào Kafka pod)
kubectl exec -it -n of1-dev-kafka pod/server-01 -- \
  kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic cdc-bf1.Partners \
  --from-beginning \
  --max-messages 5

# Hoặc dùng Kafka UI → chọn topic → tab Messages
# Dev:  http://webui.of1-dev-kafka.svc.cluster.local/
# Prod: http://webui.of1-prod-kafka.svc.cluster.local/

# Test end-to-end: thay đổi data trên MSSQL
sqlcmd -S HOST -U sa -P "PASSWORD" -d BF1 \
  -Q "UPDATE dbo.Partners SET COLUMN = COLUMN WHERE ID = 1"
# Rồi xem message mới xuất hiện trên Kafka UI hoặc console consumer
```

---

### Bước 8: Thiết kế schema PostgreSQL cho BF1 mới

#### 8a. Data type mapping MSSQL → PostgreSQL

| MSSQL | PostgreSQL | Lưu ý |
|---|---|---|
| `INT` | `INTEGER` | |
| `BIGINT` | `BIGINT` | |
| `SMALLINT` | `SMALLINT` | |
| `BIT` | `BOOLEAN` | |
| `NVARCHAR(n)` | `VARCHAR(n)` hoặc `TEXT` | Dùng `TEXT` nếu không cần giới hạn |
| `VARCHAR(n)` | `VARCHAR(n)` | |
| `NTEXT` / `TEXT` | `TEXT` | |
| `DATETIME` | `TIMESTAMP` | Hoặc `TIMESTAMPTZ` nếu cần timezone |
| `DATETIME2` | `TIMESTAMP` | |
| `DATE` | `DATE` | |
| `DECIMAL(p,s)` | `NUMERIC(p,s)` | |
| `MONEY` | `NUMERIC(19,4)` | |
| `FLOAT` | `DOUBLE PRECISION` | |
| `REAL` | `REAL` | |
| `UNIQUEIDENTIFIER` | `UUID` | |
| `VARBINARY(MAX)` | `BYTEA` | |
| `IMAGE` | `BYTEA` | |

#### 8b. Tạo schema trên PostgreSQL

```sql
-- Tạo database
CREATE DATABASE bf1_new WITH ENCODING 'UTF8';

-- Tạo schema (tùy chọn, có thể dùng public)
\c bf1_new
CREATE SCHEMA IF NOT EXISTS bf1;

-- Ví dụ tạo bảng Partners (chuẩn hóa naming sang snake_case)
CREATE TABLE bf1.partners (
  partner_id VARCHAR(100) PRIMARY KEY,
  date_create TIMESTAMP,
  date_modify TIMESTAMP,
  partner_name VARCHAR(300),
  partner_name2 VARCHAR(300),
  partner_name3 VARCHAR(510),
  personal_contact VARCHAR(300),
  public BOOLEAN NOT NULL DEFAULT FALSE,
  email TEXT,
  address TEXT,
  address2 TEXT,
  homephone VARCHAR(100),
  workphone VARCHAR(100),
  fax VARCHAR(100),
  cell VARCHAR(100),
  taxcode VARCHAR(100),
  notes_less TEXT,
  notes TEXT,
  country VARCHAR(100),
  website VARCHAR(300),
  "group" VARCHAR(100),
  group_type VARCHAR(300),
  contact_id VARCHAR(100),
  category VARCHAR(300),
  acc_ref VARCHAR(100),
  denied BOOLEAN DEFAULT FALSE,
  warning BOOLEAN DEFAULT FALSE,
  warning_msg TEXT,
  payment_term INTEGER,
  payment_amount DOUBLE PRECISION,
  location VARCHAR(300),
  status BOOLEAN DEFAULT FALSE,
  industry VARCHAR(100),
  bank_accs_no VARCHAR(100),
  bank_name TEXT,
  bank_address TEXT,
  swift_code VARCHAR(100),
  -- ... thêm các cột khác tùy nhu cầu
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_partners_partner_name ON bf1.partners(partner_name);
CREATE INDEX idx_partners_taxcode ON bf1.partners(taxcode);
CREATE INDEX idx_partners_contact_id ON bf1.partners(contact_id);
CREATE INDEX idx_partners_acc_ref ON bf1.partners(acc_ref);
CREATE INDEX idx_partners_group ON bf1.partners("group");

-- Tạo bảng mapping để consumer biết ghi vào đâu
CREATE TABLE bf1._table_mapping (
  mssql_table VARCHAR(128) PRIMARY KEY,
  pg_table VARCHAR(128) NOT NULL,
  notes TEXT
);
INSERT INTO bf1._table_mapping VALUES
  ('Partners', 'bf1.partners', 'Danh mục đối tác/khách hàng');
```

---

### Bước 9: Implement Kafka Consumer → PostgreSQL

> Đây là phần **chưa có** — cần implement mới.

**Nhiệm vụ của consumer:**
1. Subscribe vào các Kafka topic của BF1 (prefix `cdc-bf1`).
2. Parse CDC message format Debezium JSON:
   ```json
   {
     "before": { ... },
     "after": { ... },
     "op": "c|u|d|r",
     "ts_ms": 1234567890,
     "source": { "table": "Partners", ... }
   }
   ```
3. Transform data: mapping tên cột MSSQL → PostgreSQL, chuyển đổi data type.
4. Ghi vào PostgreSQL:
   - `op = "r"` hoặc `"c"` (snapshot/insert) → `INSERT ... ON CONFLICT DO UPDATE`
   - `op = "u"` (update) → `UPDATE`
   - `op = "d"` (delete) → `DELETE` hoặc soft-delete tùy nghiệp vụ
5. Xử lý lỗi: retry, dead-letter queue cho message không xử lý được.
6. Tracking offset: đảm bảo at-least-once semantics + idempotent writes (upsert).

**Lựa chọn công nghệ consumer:**
- **Option A:** Viết consumer bằng Python/Go trong service backend BF1 mới.
- **Option B:** Dùng Kafka Connect JDBC Sink Connector (ít code hơn, nhưng hạn chế transform).
- **Option C:** Dùng Debezium Server + JDBC Sink (kết hợp).

---

### Bước 10: Đối soát dữ liệu

```sql
-- So sánh row count MSSQL vs PostgreSQL
-- Trên MSSQL:
SELECT 'Partners' AS tbl, COUNT(*) AS cnt FROM BEE_DB.dbo.Partners;

-- Trên PostgreSQL:
SELECT 'partners' AS tbl, COUNT(*) AS cnt FROM bf1.partners;
```

- Spot-check dữ liệu: chọn random records, so sánh giá trị từng cột.
- Test realtime: INSERT/UPDATE trên MSSQL, xác nhận xuất hiện trên PostgreSQL trong vài giây.
- Thiết lập monitoring cho Kafka consumer lag:
  ```bash
  # Xem consumer group lag (kubectl exec vào Kafka pod)
  kubectl exec -it -n of1-dev-kafka pod/server-01 -- \
    kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group bf1-consumer-group \
    --describe
  ```

---

### Quản lý connector (thao tác hàng ngày)

> Tất cả lệnh `curl` bên dưới giả sử đã port-forward Debezium Connect về `localhost:8083`.
> Nếu chạy từ trong K8s cluster, thay `localhost:8083` bằng `debezium-connect.of1-dev-kafka.svc.cluster.local:8083` (dev) hoặc `...of1-prod-kafka...` (prod).

```bash
# Port-forward (nếu chưa)
kubectl port-forward -n of1-dev-kafka svc/debezium-connect 8083:8083 &

# Liệt kê connectors
curl -s http://localhost:8083/connectors | jq

# Xem status
curl -s http://localhost:8083/connectors/mssql-bf1-connector/status | jq

# Restart (khi bị lỗi hoặc stuck)
curl -X POST http://localhost:8083/connectors/mssql-bf1-connector/restart?includeTasks=true

# Pause (bảo trì)
curl -X PUT http://localhost:8083/connectors/mssql-bf1-connector/pause

# Resume
curl -X PUT http://localhost:8083/connectors/mssql-bf1-connector/resume

# Xóa connector
curl -X DELETE http://localhost:8083/connectors/mssql-bf1-connector

# Xem config hiện tại
curl -s http://localhost:8083/connectors/mssql-bf1-connector/config | jq

# Update config (không cần xóa + tạo lại)
curl -X PUT http://localhost:8083/connectors/mssql-bf1-connector/config \
  -H "Content-Type: application/json" \
  -d @bf1-connector-updated.json
```

**Dùng manage.py (khuyến nghị cho daily ops):**

```bash
cd debezium-final

# Dev
ENV_NAME=dev python3 manage.py status
ENV_NAME=dev python3 manage.py list
ENV_NAME=dev python3 manage.py restart
ENV_NAME=dev python3 manage.py register    # Xóa cũ + đăng ký mới

# Prod
ENV_NAME=prod python3 manage.py status
ENV_NAME=prod python3 manage.py register
```

### Troubleshooting

| Triệu chứng | Kiểm tra | Xử lý |
|---|---|---|
| Connector FAILED | `curl .../status \| jq '.tasks[0].trace'` | Đọc error trace, sửa config, restart |
| Không kết nối SQL Server | Ping host, telnet port 1433 | Kiểm tra firewall, hostname, credentials |
| CDC không capture thay đổi | Kiểm tra SQL Server Agent | Start Agent: `EXEC xp_servicecontrol 'Start', 'SQLServerAgent'` |
| Không thấy message trên Kafka | `check-cdc-tables.sql` | Bật CDC cho bảng, INSERT test record |
| Consumer lag tăng liên tục | Xem consumer group lag | Scale consumer, tăng batch size |
| Message quá lớn bị reject | Kafka broker log | Tăng `message.max.bytes` trên broker + producer |

### Rủi ro và giải pháp

| Rủi ro | Giải pháp |
|---|---|
| SQL Server Agent dừng → CDC ngừng capture | Monitoring Agent status, alert khi Agent down |
| Consumer lag cao → dữ liệu PostgreSQL bị trễ | Monitor consumer group lag, scale consumer nếu cần |
| Schema change trên MSSQL phá vỡ consumer | Debezium gửi schema change event → consumer cần handle gracefully |
| Snapshot lần đầu quá lâu với bảng lớn | Batch import riêng bằng bcp/bulk insert, chỉ dùng CDC cho incremental |
| Message quá lớn (blob/binary columns) | Cấu hình large message support (50MB) trên Kafka + Debezium |
| Duplicate message (at-least-once) | Consumer dùng upsert (`ON CONFLICT DO UPDATE`) thay vì INSERT thuần |

---

## Thành viên

| Member | Vai trò | Scope of Work |
|--------|---------|---------------|
| Anh Quý | Tư vấn nghiệp vụ và dữ liệu | Hỗ trợ thiết kế schema database, tư vấn quy trình nghiệp vụ, luồng dữ liệu |
| Anh Tuấn | Tư vấn giải pháp hạ tầng | Tư vấn giải pháp kỹ thuật liên quan đến hạ tầng và định hướng nền tảng triển khai |
| Đàn | Triển khai hệ thống | Phát triển và hoàn thiện |
| An | Triển khai hệ thống | Phát triển và hoàn thiện |
| Đức | Triển khai hệ thống | Phát triển và hoàn thiện |
| Tiến | Triển khai hệ thống | Phát triển và hoàn thiện |





