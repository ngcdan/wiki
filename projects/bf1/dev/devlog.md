# DEVLOG - BF1 CDC Pipeline

## Sandbox: MSSQL + Debezium local → Kafka K8s (2026-03-18)

### Kiến trúc

```
Docker Compose (local)               K8s cluster (of1-dev-kafka)
┌────────────────────────────┐       ┌─────────────────────────────┐
│  MSSQL 2022 (:1433)        │       │                             │
│  └─ BEE_DB → Partners (CDC)│       │  Kafka 7.5.0                │
│         │                  │       │  ├─ server-01 (10.43.101.85)│
│         ▼                  │       │  ├─ server-02 (10.43.180.91)│
│  Debezium Connect 2.4      │──────►│  └─ server-03 (10.43.183.203)
│  (:8083)                   │       │         │                   │
│                            │       │         ▼                   │
│  extra_hosts:              │       │  Kafka UI (:80)             │
│   server-01~03 → K8s IPs  │       │  webui.of1-dev-kafka.svc    │
└────────────────────────────┘       └─────────────────────────────┘
```

Topic: `cdc-bf1-sandbox.BEE_DB.dbo.Partners`

### Quick start

```bash
cd bf1/sandbox
docker compose up -d          # start 2 containers (mssql + debezium)
sleep 25                      # chờ MSSQL ready
./init-db.sh                  # tạo BEE_DB, Partners, CDC, seed 3 rows
./register-connector.sh       # đăng ký connector → RUNNING
./test-crud.sh                # INSERT/UPDATE/DELETE → xem messages
./status.sh                   # xem trạng thái
./sql.sh                      # interactive SQL
```

### Containers

| Container | Image | Port | Vai trò |
|---|---|---|---|
| bf1-mssql | mcr.microsoft.com/mssql/server:2022-latest | 1433 | Source DB (CDC enabled) |
| bf1-debezium | debezium/connect:2.4 | 8083 | CDC connector → Kafka K8s |

Kafka + Kafka UI dùng K8s cluster `of1-dev-kafka`:
- Kafka: `server-01~03.of1-dev-kafka.svc:9092`
- Kafka UI: http://webui.of1-dev-kafka.svc.cluster.local/

**DNS trick:** Debezium container dùng `extra_hosts` để map K8s service names → IPs, vì Docker container không resolve được K8s DNS.

### Kết quả test (2026-03-18)

**Init database:**
- BEE_DB created, CDC enabled (database + table)
- Partners table: 100+ cột, schema giống prod
- SQL Server Agent: running (`MSSQL_AGENT_ENABLED=true`)
- User debezium: created + db_owner + CDC permissions
- Seed data: 3 rows (TEST001, TEST002, TEST003)
- CDC jobs: capture + cleanup running

**Connector:**
- Name: `mssql-bf1-sandbox`
- Status: **RUNNING** (connector + task)
- Snapshot mode: `initial` → đọc 3 seed rows, sau đó chỉ bắt thay đổi
- Topics tạo ra:
  - `cdc-bf1-sandbox` (heartbeat)
  - `cdc-bf1-sandbox.BEE_DB.dbo.Partners` (CDC events)
  - `dbhistory.cdc-bf1-sandbox` (schema history)

**CRUD test:**

| # | Thao tác | Record | Kafka op | Kết quả |
|---|---|---|---|---|
| 1 | INSERT | `CDC_TEST_071251` | `c` (create) | OK |
| 2 | UPDATE | `TEST001` — đổi email + tên | `u` (update) | OK |
| 3 | BATCH UPDATE | `TEST002`, `TEST003` — đổi country → SINGAPORE | `u` × 2 | OK |
| 4 | DELETE | `CDC_TEST_071251` | `d` (delete) | OK |

Tổng messages trên Kafka: 3 (snapshot, op=`r`) + 4 (CRUD) = **7 messages**.

Xem messages: http://webui.of1-dev-kafka.svc.cluster.local/ → topic `cdc-bf1-sandbox.BEE_DB.dbo.Partners`

### Các kiến trúc đã thử

| # | Kiến trúc | Kết quả | Lý do |
|---|---|---|---|
| 1 | Toàn bộ local (MSSQL + Kafka + Debezium + Kafka UI) | **OK** nhưng nặng | 5 containers, Kafka + Zookeeper chiếm nhiều RAM |
| 2 | MSSQL local + Debezium K8s + Kafka K8s | **FAILED** | K8s pods không route được đến máy local (VPN 1 chiều) |
| 3 | **MSSQL + Debezium local + Kafka K8s + Kafka UI K8s** | **OK** ✓ | 2 containers local, Kafka dùng cluster có sẵn |

---

## Các vấn đề gặp và cách fix

### 1. NVARCHAR(8000) không hợp lệ

**Lỗi:** `The size (8000) given to the parameter 'AccessCode' exceeds the maximum allowed (4000).`

**Nguyên nhân:** SQL Server giới hạn NVARCHAR tối đa 4000 characters. Prod dùng NVARCHAR(8000) nhưng thực tế không hợp lệ (có thể do legacy schema).

**Fix:** Đổi thành `NVARCHAR(MAX)` trong `init-db.sql`.

### 2. Password không đủ complexity

**Lỗi:** `Password validation failed. The password does not meet SQL Server password policy requirements.`

**Nguyên nhân:** Password `Debezium@2026` thiếu chữ thường.

**Fix:** Đổi thành `Dbz_Sandbox@2026` (có uppercase + lowercase + digit + symbol).

### 3. K8s pods không kết nối được máy local

**Lỗi:** `connect timed out` khi Debezium trên K8s cố kết nối MSSQL Docker trên máy local.

**Nguyên nhân:** Network một chiều — máy local route được vào K8s (qua VPN utun7), nhưng K8s pods không route ngược về máy local. Đã test 3 IP (`192.168.109.61`, `10.188.0.4`, `100.78.159.118`), tất cả timeout.

**Fix:** Chuyển sang chạy toàn bộ local (MSSQL + Kafka + Debezium trong cùng docker compose). Debezium kết nối MSSQL qua Docker network hostname `mssql`.

### 4. Topic name có thêm database + schema prefix

**Thực tế:** Topic tạo ra là `cdc-bf1-sandbox.BEE_DB.dbo.Partners` thay vì `cdc-bf1-sandbox.Partners`.

**Nguyên nhân:** RegexRouter transform `([^.]+)\.([^.]+)\.([^.]+)` → `$1.$3` chỉ match 3 phần, nhưng topic gốc có 4 phần: `prefix.database.schema.table`.

**Nếu muốn fix:** Đổi regex thành `([^.]+)\.([^.]+)\.([^.]+)\.([^.]+)` → `$1.$4` để chỉ giữ prefix + table name.

### 5. Apple Silicon (arm64) chạy MSSQL (amd64)

**Warning:** `The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)`

**Thực tế:** MSSQL + Debezium đều chạy qua Rosetta emulation, hoạt động bình thường nhưng chậm hơn native.

### 6. Docker container không resolve K8s DNS

**Lỗi:** `DNS resolution failed for server-01.of1-dev-kafka.svc`

**Nguyên nhân:** Docker container dùng DNS riêng (127.0.0.11), không resolve được K8s service names. Thử dùng `dns: 10.43.0.10` (CoreDNS) nhưng CoreDNS không reachable từ Docker network.

**Fix:** Dùng `extra_hosts` trong docker-compose để map K8s hostnames → IPs:
```yaml
extra_hosts:
  - "server-01.of1-dev-kafka.svc:10.43.101.85"
  - "server-02.of1-dev-kafka.svc:10.43.180.91"
  - "server-03.of1-dev-kafka.svc:10.43.183.203"
```

**Lưu ý:** IPs có thể thay đổi khi K8s service restart. Cập nhật bằng:
```bash
python3 -c "import socket; print(socket.gethostbyname('server-01.of1-dev-kafka.svc.cluster.local'))"
```

### 7. K8s pods không kết nối ngược về máy local

**Lỗi:** Debezium trên K8s timeout khi kết nối MSSQL Docker trên máy local.

**Nguyên nhân:** Network một chiều — local → K8s OK (qua VPN utun7), nhưng K8s → local bị chặn. Test 3 IPs (`192.168.x`, `10.188.x`, `100.78.x`) đều timeout.

**Fix:** Chạy Debezium local (Docker) thay vì trên K8s. Debezium kết nối MSSQL qua Docker network, kết nối Kafka qua VPN (extra_hosts).

---

## Debezium UI API (không cần kubectl)

Khi không có kubectl access, dùng Debezium UI backend API để quản lý connectors.

### Endpoints

Base URL dev: `http://debezium-ui.of1-dev-kafka.svc.cluster.local`
Base URL prod: `http://debezium-ui.of1-prod-kafka.svc.cluster.local`

| Thao tác | Method | Path |
|---|---|---|
| List connect clusters | GET | `/api/connect-clusters` |
| List connector types | GET | `/api/connector-types` |
| List connectors | GET | `/api/connectors/{cluster}` |
| Get connector config | GET | `/api/connectors/{cluster}/{name}/config` |
| Create connector | POST | `/api/connector/{cluster}/{connector-type-id}` |
| Update connector | PUT | `/api/connectors/{cluster}/{name}` |
| Pause | PUT | `/api/connector/{cluster}/{name}/pause` |
| Resume | PUT | `/api/connector/{cluster}/{name}/resume` |
| Restart | POST | `/api/connector/{cluster}/{name}/restart` |
| Restart task | POST | `/api/connector/{cluster}/{name}/task/{num}/restart` |
| Validate connection | POST | `/api/connector-types/{id}/validation/connection` |
| OpenAPI spec | GET | `/q/openapi` |

`{cluster}` = `1` (index-based).

### Ví dụ

```bash
DBZ_UI="http://debezium-ui.of1-dev-kafka.svc.cluster.local"

# List connectors
curl -s "${DBZ_UI}/api/connectors/1" | jq .

# Xem config
curl -s "${DBZ_UI}/api/connectors/1/mssql-dev-ecus-BEEOLD-connector/config" | jq .

# Tạo connector
curl -s -X POST "${DBZ_UI}/api/connector/1/sqlserver" \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "config": {...}}' | jq .

# Validate connection (test từ trong K8s)
curl -s -X POST "${DBZ_UI}/api/connector-types/sqlserver/validation/connection" \
  -H "Content-Type: application/json" \
  -d '{"database.hostname":"...","database.port":"1433",...}'
```

---

## Trạng thái K8s clusters (2026-03-18)

| Cluster | Debezium Connect | Connectors |
|---|---|---|
| Dev (`of1-dev-kafka`) | OK (sau restart) | 5 connectors (BEEOLD task FAILED, còn lại RUNNING) |
| Prod (`of1-prod-kafka`) | OK | 4 connectors, tất cả RUNNING |

**Web UIs:**
- Kafka UI dev: http://webui.of1-dev-kafka.svc.cluster.local/
- Kafka UI prod: http://webui.of1-prod-kafka.svc.cluster.local/
- Debezium UI dev: http://debezium-ui.of1-dev-kafka.svc.cluster.local/
- Debezium UI prod: http://debezium-ui.of1-prod-kafka.svc.cluster.local/
