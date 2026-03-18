# DEVLOG - CDC Pipeline (Change Data Capture)

## Tổng quan

Hệ thống CDC dùng **Debezium 2.4** để bắt thay đổi dữ liệu từ **SQL Server** (ECUS5VNACCS, BEE_NEW, BEEOLD, lkt) và stream real-time vào **Apache Kafka 7.5.0**. Mục đích: đồng bộ dữ liệu hải quan từ hệ thống ECUS sang platform OF1 mà không cần polling database.

### Kiến trúc tổng thể

```
SQL Server (ECUS)  ──CDC──►  Debezium Connect  ──►  Kafka  ──►  Consumer (downstream apps)
   (4 databases)              (connector/task)      (topics)
```

**Các thành phần:**
| Component | Image / Version | Port |
|---|---|---|
| Zookeeper | confluentinc/cp-zookeeper:7.5.0 | 2181 |
| Kafka | confluentinc/cp-kafka:7.5.0 | 9092 (external), 29092 (internal) |
| Debezium Connect | debezium/connect:2.4 | 8083 |
| Kafka UI | provectuslabs/kafka-ui | 8085 |
| Debezium UI | debezium/debezium-ui:2.4 | 8081 |

---

## Cách CDC hoạt động

### 1. SQL Server CDC mechanism

SQL Server có tính năng CDC built-in. Khi bật CDC cho một bảng, SQL Server tự động tạo các bảng `cdc.*` để lưu lại mọi thay đổi (INSERT/UPDATE/DELETE). SQL Server Agent job sẽ đọc transaction log và ghi vào bảng CDC.

### 2. Debezium đọc thay đổi

Debezium connector (`SqlServerConnector`) kết nối vào SQL Server, đọc bảng CDC, chuyển thành Kafka message. Mỗi thay đổi tạo 1 message chứa:

```json
{
  "before": { ... },       // Trạng thái cũ (null nếu INSERT)
  "after": { ... },        // Trạng thái mới (null nếu DELETE)
  "op": "c|u|d|r",         // c=create, u=update, d=delete, r=read(snapshot)
  "ts_ms": 1234567890,     // Timestamp
  "source": { ... }        // Thông tin kết nối, transaction
}
```

### 3. Topic naming

Pattern: `<topic_prefix>.<table_name>`

Có transform RegexRouter bỏ phần schema (dbo): `([^.]+)\.([^.]+)\.([^.]+)` → `$1.$3`

Ví dụ: `cdc-dev-ecus.DTOKHAIMD`, `cdc-prod-ecus.DHANGMDDK`

Topic đặc biệt:
- `dbhistory.<prefix>-<database>` — lịch sử schema
- `schema-changes.<prefix>-<database>` — thay đổi schema

---

## Các database được CDC

| Database | Dev Connector | Prod Connector | Topic Prefix (dev) | Topic Prefix (prod) |
|---|---|---|---|---|
| ECUS5VNACCS | mssql-dev-ecus-ECUS5VNACCS-connector | mssql-prod-ecus-ECUS5VNACCS-connector | cdc-dev-ecus | cdc-prod-ecus |
| BEE_NEW | mssql-dev-ecus-BEE_NEW-connector | mssql-prod-ecus-BEE-connector | cdc-dev-ecus | cdc-prod-ecus |
| BEEOLD | mssql-dev-ecus-BEEOLD-connector | mssql-prod-ecus-BEEOLD-connector | cdc-dev-ecus | cdc-prod-ecus |
| lkt | mssql-dev-ecus-lkt-connector | mssql-prod-ecus-lkt-connector | cdc-dev-ecus | cdc-prod-ecus |

**SQL Server hosts:**
- Dev: `win-server-vm.of1-dev-egov.svc.cluster.local:1433`
- Prod: `win-server-16-ecus-hp.beehp-prod-logs.svc.cluster.local:1433`

---

## Setup từ đầu (step-by-step)

### Bước 1: Chuẩn bị SQL Server

**1a. Tạo user debezium:**
```sql
-- File: debezium/scripts/create-debezium-db-user.sql
CREATE LOGIN debezium WITH PASSWORD = 'Sa12345678@';
-- Tạo user trên mỗi database
USE ECUS5VNACCS;
CREATE USER debezium FOR LOGIN debezium;
ALTER ROLE db_owner ADD MEMBER debezium;
```

**1b. Cấp quyền CDC:**
```sql
-- File: debezium/scripts/grant-cdc-permissions-all.sql
-- Chạy cho mỗi database (ECUS5VNACCS, BEE_NEW, BEEOLD, lkt):
GRANT SELECT ON SCHEMA::cdc TO debezium;
GRANT EXECUTE ON SCHEMA::cdc TO debezium;
GRANT VIEW DATABASE STATE TO debezium;
ALTER ROLE db_datareader ADD MEMBER debezium;
```

**1c. Bật CDC cho database và tables:**
```sql
-- Bật CDC ở mức database
USE ECUS5VNACCS;
EXEC sys.sp_cdc_enable_db;

-- Bật CDC cho từng bảng (file: enable-cdc-tables-sync.sql)
-- 27 bảng chính cần sync:
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'DTOKHAIMD', @role_name = NULL;
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'DHANGMDDK', @role_name = NULL;
-- ... (SDONVI, SCUAKHAU, SVB_PQ, SLOAI_GP, SNGAN_HANG, Reports_Excel, SDVT, ...)
```

**1d. Kiểm tra CDC đã bật:**
```sql
-- File: debezium/scripts/check-cdc-tables.sql
SELECT name, is_cdc_enabled FROM sys.databases;
SELECT s.name AS schema_name, t.name AS table_name, t.is_tracked_by_cdc
FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id;
```

### Bước 2: Khởi động Debezium stack

```bash
cd debezium
./scripts/start.sh     # docker-compose up -d, chờ ~30s cho các service sẵn sàng
```

Kiểm tra:
```bash
./scripts/status.sh    # Xem trạng thái tất cả service + connector
```

### Bước 3: Đăng ký connector

**Cách 1 — Đăng ký tất cả (dev):**
```bash
cd debezium/scripts
./register-all-connectors.sh    # Đăng ký 4 connector cho localhost
# hoặc
./register-all-servers.sh       # Đăng ký 4 connector cho remote K8s
```

**Cách 2 — Đăng ký từng database:**
```bash
cd debezium-ECUS5VNACCS
./register.sh            # localhost
./register-server.sh     # dev server
./register-prod.sh       # production
```

**Cách 3 — Dùng manage.py (debezium-final/, khuyến nghị):**
```bash
cd debezium-final
ENV_NAME=dev python3 manage.py register    # Đăng ký connector cho env dev
ENV_NAME=prod python3 manage.py register   # Đăng ký connector cho env prod
```

### Bước 4: Xác nhận hoạt động

```bash
# Liệt kê connectors
curl -s http://localhost:8083/connectors | jq

# Xem status connector
curl -s http://localhost:8083/connectors/mssql-dev-ecus-ECUS5VNACCS-connector/status | jq

# Xem topics trên Kafka
./scripts/view-topics.sh

# Xem messages
./scripts/view-all-messages.sh
```

Hoặc mở trình duyệt:
- Kafka UI: http://localhost:8085
- Debezium UI: http://localhost:8081

---

## Quản lý connector (debezium-final/manage.py)

Hệ thống quản lý generic, dùng environment file + template:

```bash
ENV_NAME=<env> python3 manage.py <command>
```

| Command | Mô tả |
|---|---|
| `register` | Xóa connector cũ + đăng ký mới |
| `delete` | Xóa connector |
| `status` | Xem trạng thái connector + tasks |
| `list` | Liệt kê tất cả connector |
| `config` | In ra JSON config (dry-run) |
| `restart` | Restart connector + tasks |
| `pause` | Tạm dừng connector |
| `resume` | Tiếp tục connector đã pause |
| `info` | Hiển thị thông tin environment |

**Environment files:** `env-local.sh`, `env-dev.sh`, `env-prod.sh` — chứa biến MSSQL host, Kafka bootstrap, Debezium URL, topic prefix.

**Template:** `config/mssql-connector.template.json` — dùng placeholder `${CONNECTOR_NAME}`, `${MSSQL_HOST}`, `${TOPIC_PREFIX}`, ...

---

## Cấu hình quan trọng

### Connector config

| Parameter | Value | Giải thích |
|---|---|---|
| `snapshot.mode` | `schema_only` | Chỉ capture thay đổi mới, không snapshot toàn bộ data cũ |
| `decimal.handling.mode` | `string` | Tránh lỗi precision với kiểu decimal |
| `time.precision.mode` | `adaptive` | Tự động chọn precision phù hợp cho datetime |
| `query.fetch.size` | `10000` | Số records mỗi lần fetch |
| `max.batch.size` | `1024` | Batch gửi Kafka |
| `max.queue.size` | `2048` | Queue nội bộ connector |
| `poll.interval.ms` | `1000` | Khoảng cách polling CDC tables |
| `retriable.restart.connector.wait.ms` | `10000` | Chờ 10s trước khi retry khi lỗi |

### Large message support

Cấu hình để xử lý message lớn (một số bảng ECUS có record lớn):

| Parameter | Value |
|---|---|
| `kafka.message.max.bytes` | 50MB |
| `producer.max.request.size` | 50MB |
| `producer.buffer.memory` | 100MB |
| `producer.compression.type` | snappy |
| `producer.batch.size` | 320KB |
| `producer.linger.ms` | 10ms |
| `consumer.max.partition.fetch.bytes` | 50MB |

---

## Cấu trúc thư mục CDC

```
debezium/                          # Setup chính (docker-compose + scripts)
├── docker-compose.yml             # Zookeeper + Kafka + Debezium + UI
├── config/                        # Connector JSON configs
├── scripts/                       # Shell scripts + SQL scripts
│   ├── start.sh / stop.sh         # Lifecycle
│   ├── register-*.sh              # Đăng ký connector
│   ├── view-*.sh / export-*.sh    # Debug & inspect messages
│   ├── enable-cdc-*.sql           # Bật CDC trên SQL Server
│   ├── grant-*.sql                # Cấp quyền
│   └── check-*.sql                # Kiểm tra trạng thái
├── readme.md

debezium-ECUS5VNACCS/              # Config riêng cho database ECUS5VNACCS
debezium-BEE_NEW/                  # Config riêng cho database BEE_NEW
debezium-BEEOLD/                   # Config riêng cho database BEEOLD
debezium-lkt/                      # Config riêng cho database lkt
│   ├── mssql-connector-large-messages.json       # Dev config
│   ├── mssql-connector-large-messages-prod.json  # Prod config
│   ├── register.sh / register-server.sh / register-prod.sh

debezium-final/                    # Generic management system (khuyến nghị dùng)
├── manage.py                      # Python CLI quản lý connector
├── env-local.sh / env-dev.sh / env-prod.sh
├── config/mssql-connector.template.json
├── README.md
```

---

## Troubleshooting

### Connector ở trạng thái FAILED
```bash
# Xem lỗi chi tiết
curl -s http://localhost:8083/connectors/<connector-name>/status | jq

# Restart
ENV_NAME=dev python3 manage.py restart
# hoặc
curl -X POST http://localhost:8083/connectors/<connector-name>/restart
```

### Không thấy message trên Kafka
1. Kiểm tra CDC đã bật trên SQL Server chưa (`check-cdc-tables.sql`)
2. Kiểm tra SQL Server Agent đang chạy (CDC cần Agent để capture changes)
3. Kiểm tra connector status (phải RUNNING)
4. Thử INSERT/UPDATE 1 record rồi xem topic

### Kết nối SQL Server bị lỗi
```bash
./scripts/test-mssql-connection.sh   # Test network + SQL connection
```

### Reset toàn bộ
```bash
./scripts/reset-all.sh   # Xóa hết container + volume, khởi tạo lại từ đầu
```

---

## Chi tiết: debezium-BEEOLD

Database BEEOLD chứa dữ liệu cũ từ hệ thống BEE. Thư mục `debezium-BEEOLD/` đã được setup sẵn cho cả dev và prod.

### Cấu trúc thư mục

```
debezium-BEEOLD/
├── mssql-connector-large-messages.json       # Config cho DEV
├── mssql-connector-large-messages-prod.json  # Config cho PROD
├── register.sh                               # Đăng ký → localhost:8083
├── register-server.sh                        # Đăng ký → dev K8s cluster
└── register-prod.sh                          # Đăng ký → prod K8s cluster
```

### So sánh Dev vs Prod

| | Dev | Prod |
|---|---|---|
| **Connector name** | `mssql-dev-ecus-BEEOLD-connector` | `mssql-prod-ecus-BEEOLD-connector` |
| **SQL Server host** | `win-server-16-ecus-hp.of1-dev-egov.svc.cluster.local` | `win-server-16-ecus-hp.beehp-prod-logs.svc.cluster.local` |
| **Kafka bootstrap** | `server-01~03.of1-dev-kafka.svc:9092` | `server-01~03.of1-prod-kafka.svc:9092` |
| **Debezium Connect** | `debezium-connect.of1-dev-kafka.svc.cluster.local:8083` | `debezium-connect.of1-prod-kafka.svc.cluster.local:8083` |
| **Topic prefix** | `cdc-dev-ecus` | `cdc-prod-ecus` |
| **DB history topic** | `dbhistory.cdc-dev-ecus-BEEOLD` | `dbhistory.cdc-prod-ecus-BEEOLD` |
| **Schema history topic** | `schema-changes.cdc-dev-ecus-BEEOLD` | `schema-changes.cdc-prod-ecus-BEEOLD` |
| **Config file** | `mssql-connector-large-messages.json` | `mssql-connector-large-messages-prod.json` |

### Cấu hình connector (giống nhau dev/prod)

- **database.names:** `BEEOLD`
- **table.include.list:** `dbo.*` (tất cả bảng trong schema dbo)
- **snapshot.mode:** `schema_only` — chỉ bắt thay đổi mới
- **database.user:** `debezium`
- **database.applicationName:** `Debezium-BEEOLD`
- **Có RegexRouter transform** — bỏ phần `dbo` trong topic name: `cdc-dev-ecus.dbo.TABLE` → `cdc-dev-ecus.TABLE`
- **Large message support:** producer max request 50MB, buffer 100MB, compression snappy

### Cách đăng ký connector

**3 scripts, 3 mục đích khác nhau:**

**1. `register.sh` — Đăng ký vào Debezium Connect chạy trên localhost**
```bash
cd debezium-BEEOLD
./register.sh
# Target: http://localhost:8083
# Config: mssql-connector-large-messages.json (dev)
# Connector: mssql-dev-ecus-BEEOLD-connector
```
Dùng khi chạy Debezium stack local bằng docker-compose.

**2. `register-server.sh` — Đăng ký vào Debezium Connect trên K8s dev**
```bash
cd debezium-BEEOLD
./register-server.sh
# Target: http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083
# Config: mssql-connector-large-messages.json (dev)
# Connector: mssql-dev-ecus-BEEOLD-connector
```
Dùng khi đăng ký trực tiếp lên cluster dev. Cần có network access vào K8s cluster (kubectl port-forward hoặc chạy từ trong cluster).

**3. `register-prod.sh` — Đăng ký vào Debezium Connect trên K8s prod**
```bash
cd debezium-BEEOLD
./register-prod.sh
# Target: http://debezium-connect.of1-prod-kafka.svc.cluster.local:8083
# Config: mssql-connector-large-messages-prod.json (prod)
# Connector: mssql-prod-ecus-BEEOLD-connector
```
Dùng cho production. Trỏ vào SQL Server prod và Kafka cluster prod.

### Flow hoạt động của register script

Cả 3 script đều chạy cùng logic:

1. **Chờ Debezium Connect sẵn sàng** — poll `GET /connectors` cho đến khi trả HTTP 200
2. **Xóa connector cũ** (nếu có) — `DELETE /connectors/{name}`
3. **Đăng ký connector mới** — `POST /connectors/` với JSON config
4. **Kiểm tra status** — `GET /connectors/{name}/status`

Kết quả mong đợi: connector status = `RUNNING`, task status = `RUNNING`.

### Kiểm tra sau khi đăng ký

```bash
# Xem status
curl -s http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/status | jq

# Response mong đợi:
# {
#   "name": "mssql-dev-ecus-BEEOLD-connector",
#   "connector": { "state": "RUNNING", "worker_id": "..." },
#   "tasks": [{ "id": 0, "state": "RUNNING", "worker_id": "..." }]
# }

# Xem topics được tạo (chứa "BEEOLD")
curl -s http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/topics | jq
```

### Lưu ý riêng cho BEEOLD

- **Host dev** là `win-server-16-ecus-hp.of1-dev-egov.svc` (khác với ECUS5VNACCS dùng `win-server-vm.of1-dev-egov.svc`) — cả dev và prod BEEOLD đều trỏ vào máy `win-server-16-ecus-hp`, chỉ khác namespace K8s
- **table.include.list = `dbo.*`** — capture TẤT CẢ bảng, không giới hạn như ECUS5VNACCS (chỉ 27 bảng). Cần cẩn thận vì sẽ tạo nhiều topic
- **Cùng topic prefix** với các database khác (`cdc-dev-ecus` / `cdc-prod-ecus`) — phân biệt nhau qua tên bảng. Nếu BEEOLD và ECUS5VNACCS có bảng trùng tên, message sẽ vào cùng topic

---

## Lưu ý quan trọng

1. **SQL Server Agent phải chạy** — CDC phụ thuộc vào Agent jobs để đọc transaction log
2. **snapshot.mode = schema_only** — Connector chỉ bắt thay đổi mới, không sync data cũ. Nếu cần full sync lần đầu, đổi thành `initial`
3. **Chưa có consumer code trong repo** — Pipeline hiện chỉ stream vào Kafka, consumer phải implement ở downstream app
4. **Message format là JSON** (không dùng Avro/Schema Registry)
5. **Cấu hình large message (50MB)** vì một số bảng ECUS có record/blob lớn
6. **4 databases dùng chung Kafka cluster** nhưng topic prefix khác nhau để phân biệt

---

## Hướng dẫn thao tác từng bước

### Kịch bản A: Setup CDC pipeline từ zero (local development)

**Yêu cầu trước khi bắt đầu:**
- Docker Desktop đang chạy
- SQL Server đã cài và có database cần CDC (ECUS5VNACCS, BEE_NEW, BEEOLD, lkt)
- Quyền `sysadmin` trên SQL Server

---

#### Bước 1: Chuẩn bị SQL Server

**1.1 Tạo user `debezium` và cấp quyền (chạy trên SSMS với quyền sysadmin):**

Mở SSMS, kết nối SQL Server, mở New Query và chạy:

```sql
-- File sẵn có: debezium/scripts/grant-cdc-permissions-all.sql
-- Script này tự động:
--   1. Tạo login debezium (password: Sa12345678@)
--   2. Tạo user debezium trên 4 database
--   3. Cấp quyền SELECT/EXECUTE trên schema cdc
--   4. Cấp VIEW DATABASE STATE + db_datareader
```

Chạy lệnh:
```bash
# Nếu có sqlcmd:
sqlcmd -S localhost,1433 -U sa -P 'your_sa_password' -i debezium/scripts/grant-cdc-permissions-all.sql

# Hoặc copy nội dung file vào SSMS rồi Execute (F5)
```

**1.2 Cấp thêm db_owner (cần cho một số trường hợp):**
```bash
sqlcmd -S localhost,1433 -U sa -P 'your_sa_password' -i debezium/scripts/grant-db-owner.sql
```

**1.3 Bật CDC trên database và tables:**

Có nhiều file SQL tùy nhu cầu:

| File | Dùng khi |
|---|---|
| `enable-cdc-tables-sync.sql` | Bật CDC cho 27 bảng chính (ECUS5VNACCS). **Dùng file này cho lần setup đầu** |
| `enable-cdc-tables-batch.sql` | Bật CDC cho 10 bảng (KHO_SSP, SNPL, SSP, ...) với kiểm tra trùng |
| `enable-cdc-all-tables.sql` | Bật CDC cho TẤT CẢ bảng (dùng cursor, chạy lâu) |
| `enable-cdc-specific-table.sql` | Template bật 1 bảng cụ thể |

```bash
# Bật 27 bảng chính cho ECUS5VNACCS:
sqlcmd -S localhost,1433 -U sa -P 'your_sa_password' -i debezium/scripts/enable-cdc-tables-sync.sql
```

**1.4 Kiểm tra CDC đã bật đúng chưa:**
```bash
sqlcmd -S localhost,1433 -U sa -P 'your_sa_password' -i debezium/scripts/check-cdc-tables.sql
```

Output sẽ hiện:
- Tổng số bảng trong database
- Số bảng đã bật CDC
- Danh sách bảng có CDC
- Danh sách bảng chưa có CDC (50 bảng đầu)
- Trạng thái CDC jobs

**Quan trọng:** Đảm bảo SQL Server Agent đang chạy. Kiểm tra trong SQL Server Configuration Manager → SQL Server Services → SQL Server Agent.

---

#### Bước 2: Khởi động Debezium stack (Docker)

```bash
cd debezium
./scripts/start.sh
```

Script này chạy `docker compose up -d` và chờ 30 giây. Sau khi chạy xong:

| Service | URL | Cách kiểm tra |
|---|---|---|
| Debezium Connect REST | http://localhost:8083 | `curl http://localhost:8083/` |
| Kafka UI | http://localhost:8085 | Mở trình duyệt |
| Debezium UI | http://localhost:8081 | Mở trình duyệt |

Kiểm tra tất cả services đang chạy:
```bash
./scripts/status.sh
# Hoặc:
docker compose ps
```

Tất cả container phải ở trạng thái `Up`. Nếu có container bị restart loop, xem log:
```bash
docker compose logs debezium-connect    # Xem log Debezium
docker compose logs kafka               # Xem log Kafka
docker compose logs zookeeper           # Xem log Zookeeper
```

---

#### Bước 3: Đăng ký connector

**Cách 1 — Từng database riêng lẻ (khuyến nghị cho lần đầu):**

```bash
# Ví dụ đăng ký BEEOLD:
cd debezium-BEEOLD
./register.sh

# Ví dụ đăng ký ECUS5VNACCS:
cd debezium-ECUS5VNACCS
./register.sh
```

Mỗi script sẽ:
1. Chờ Debezium Connect sẵn sàng (poll cho đến khi HTTP 200)
2. Xóa connector cũ nếu có
3. POST config JSON lên `http://localhost:8083/connectors/`
4. In ra status — phải thấy `RUNNING`

**Cách 2 — Dùng manage.py (linh hoạt hơn, khuyến nghị cho daily ops):**

```bash
cd debezium-final

# Xem config sẽ gửi đi (dry-run, không thay đổi gì):
ENV_NAME=local python3 manage.py config

# Xem thông tin environment:
ENV_NAME=local python3 manage.py info

# Đăng ký connector:
ENV_NAME=local python3 manage.py register
```

---

#### Bước 4: Xác nhận CDC đang hoạt động

**4.1 Kiểm tra connector status:**
```bash
# Liệt kê tất cả connector:
curl -s http://localhost:8083/connectors | jq

# Xem status chi tiết:
curl -s http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/status | jq
```

Kết quả mong đợi:
```json
{
  "connector": { "state": "RUNNING" },
  "tasks": [{ "id": 0, "state": "RUNNING" }]
}
```

**4.2 Xem danh sách Kafka topics:**
```bash
cd debezium
./scripts/view-topics.sh
# Liệt kê topics rồi hỏi bạn muốn xem topic nào
```

**4.3 Xem messages trên Kafka:**
```bash
./scripts/view-all-messages.sh
# Menu interactive:
#   1. View last N messages
#   2. View all messages from beginning
#   3. View real-time messages (new messages only)
#   4. Count total messages in topic
```

**4.4 Test CDC end-to-end:**

Mở SSMS, INSERT hoặc UPDATE 1 record trong bảng đã bật CDC:
```sql
USE ECUS5VNACCS;
UPDATE dbo.SDONVI SET TEN_DONVI = TEN_DONVI WHERE MA_DONVI = 'TEST';
-- (Update không đổi giá trị, chỉ để trigger CDC)
```

Sau đó xem message xuất hiện trên Kafka:
```bash
# Xem real-time messages (option 3):
./scripts/view-all-messages.sh
# Nhập topic: cdc-dev-ecus.SDONVI
# Chọn option 3 (real-time)
# Sẽ thấy message CDC xuất hiện
```

Hoặc mở Kafka UI tại http://localhost:8085, chọn topic tương ứng, xem tab Messages.

**4.5 Export messages ra file để phân tích:**
```bash
./scripts/export-messages.sh
# Export topic ecus.dbo.DTOKHAIMD ra /tmp/kafka-export/messages_<timestamp>.json
# (Sửa biến TOPIC trong script nếu muốn export topic khác)
```

---

### Kịch bản B: Đăng ký connector lên K8s cluster (dev/prod)

Khác với local, khi đăng ký lên K8s cần network access tới cluster.

**Dev environment:**
```bash
# Đăng ký BEEOLD lên dev:
cd debezium-BEEOLD
./register-server.sh
# Target: http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083

# Hoặc dùng manage.py:
cd debezium-final
ENV_NAME=dev python3 manage.py register
```

**Prod environment:**
```bash
# Đăng ký BEEOLD lên prod:
cd debezium-BEEOLD
./register-prod.sh
# Target: http://debezium-connect.of1-prod-kafka.svc.cluster.local:8083

# Hoặc dùng manage.py:
cd debezium-final
ENV_NAME=prod python3 manage.py register
```

**Lưu ý:** Các script `register-server.sh` / `register-prod.sh` dùng hostname K8s internal (`*.svc.cluster.local`). Phải chạy từ trong cluster hoặc từ máy có kết nối tới K8s network (kubectl port-forward, VPN, ...).

---

### Kịch bản C: Thao tác hàng ngày (daily operations)

#### Xem trạng thái connector
```bash
# Local:
cd debezium && ./scripts/status.sh

# Hoặc dùng manage.py (dev/prod):
cd debezium-final
ENV_NAME=dev python3 manage.py status
ENV_NAME=dev python3 manage.py list      # Liệt kê tất cả connector
```

#### Restart connector (khi bị lỗi hoặc stuck)
```bash
# Dùng manage.py:
ENV_NAME=dev python3 manage.py restart

# Hoặc REST API trực tiếp:
curl -X POST http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/restart?includeTasks=true
```

#### Pause / Resume connector (bảo trì)
```bash
# Tạm dừng:
ENV_NAME=dev python3 manage.py pause

# Tiếp tục:
ENV_NAME=dev python3 manage.py resume
```

#### Xóa connector
```bash
ENV_NAME=dev python3 manage.py delete

# Hoặc REST API:
curl -X DELETE http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector
```

#### Đăng ký lại connector (re-register)
```bash
# manage.py register tự động xóa cũ rồi đăng ký mới:
ENV_NAME=dev python3 manage.py register
```

---

### Kịch bản D: Thêm bảng mới vào CDC

Khi cần track thêm bảng chưa bật CDC:

**Bước 1:** Bật CDC trên SQL Server cho bảng mới
```sql
USE ECUS5VNACCS;
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'TEN_BANG_MOI',
  @role_name     = NULL,
  @supports_net_changes = 0;
GO
```

**Bước 2:** Kiểm tra CDC đã bật
```sql
SELECT t.name, t.is_tracked_by_cdc
FROM sys.tables t WHERE t.name = 'TEN_BANG_MOI';
```

**Bước 3:** Nếu connector dùng `table.include.list = "dbo.*"` (như BEEOLD) thì không cần làm gì thêm — Debezium tự detect bảng mới.

Nếu connector dùng danh sách bảng cụ thể, cần update config JSON rồi re-register:
```bash
# Sửa file config, thêm bảng vào table.include.list
# Rồi re-register:
ENV_NAME=dev python3 manage.py register
```

---

### Kịch bản E: Reset toàn bộ (khi mọi thứ hỏng)

```bash
cd debezium
./scripts/reset-all.sh
```

Script sẽ hỏi xác nhận, sau đó:
1. Stop tất cả container
2. Xóa volumes (mất hết data Kafka, offsets, ...)
3. Xóa orphaned container
4. Prune Docker system
5. Start lại từ đầu
6. Chờ 30s cho services ready

**Sau khi reset xong, phải đăng ký lại connector:**
```bash
cd debezium-BEEOLD && ./register.sh
cd debezium-ECUS5VNACCS && ./register.sh
# ... (các database khác)
```

---

### Kịch bản F: Debug khi connector không hoạt động

**F.1 Connector FAILED:**
```bash
# Xem chi tiết lỗi:
curl -s http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/status | jq '.tasks[0].trace'

# Nguyên nhân phổ biến:
# - Không kết nối được SQL Server → kiểm tra network
# - User debezium không có quyền → chạy lại grant-cdc-permissions-all.sql
# - CDC chưa bật trên database → chạy enable-cdc-tables-sync.sql
# - SQL Server Agent không chạy → khởi động Agent

# Thử restart:
curl -X POST http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/restart?includeTasks=true
```

**F.2 Test kết nối SQL Server:**
```bash
cd debezium
./scripts/test-mssql-connection.sh
# Test 4 bước:
#   1. Ping server
#   2. Telnet port 1433
#   3. sqlcmd từ Docker container (qua debezium network)
#   4. sqlcmd từ host network
```

**F.3 Connector RUNNING nhưng không thấy message:**
```bash
# 1. Kiểm tra SQL Server Agent đang chạy
# 2. Kiểm tra CDC đã bật cho bảng cần track:
sqlcmd -S localhost,1433 -U sa -P 'password' -i debezium/scripts/check-cdc-tables.sql

# 3. Thử thay đổi data trên SQL Server rồi xem Kafka:
./scripts/view-all-messages.sh
# Chọn topic, chọn option 3 (real-time)

# 4. Xem connector đang track những topic nào:
curl -s http://localhost:8083/connectors/mssql-dev-ecus-BEEOLD-connector/topics | jq
```

**F.4 Kafka UI không load được:**
```bash
# Kiểm tra container:
docker compose ps
docker compose logs kafka-ui

# Thường do Kafka chưa ready → chờ thêm hoặc restart:
docker compose restart kafka-ui
```

---

### Tham chiếu nhanh: Debezium REST API

Tất cả thao tác connector đều qua REST API trên port 8083:

| Thao tác | HTTP Method | Endpoint |
|---|---|---|
| Liệt kê connectors | GET | `/connectors` |
| Tạo connector | POST | `/connectors/` (body: JSON config) |
| Xem config | GET | `/connectors/{name}/config` |
| Update config | PUT | `/connectors/{name}/config` |
| Xóa connector | DELETE | `/connectors/{name}` |
| Xem status | GET | `/connectors/{name}/status` |
| Restart connector | POST | `/connectors/{name}/restart?includeTasks=true` |
| Pause | PUT | `/connectors/{name}/pause` |
| Resume | PUT | `/connectors/{name}/resume` |
| Xem topics | GET | `/connectors/{name}/topics` |

**Base URL:**
- Local: `http://localhost:8083`
- Dev: `http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083`
- Prod: `http://debezium-connect.of1-prod-kafka.svc.cluster.local:8083`

---

## BF1 CDC Pipeline

Chi tiết sandbox setup, kết quả test, Debezium UI API, trạng thái cluster → xem `bf1/DEVLOG.md`.
