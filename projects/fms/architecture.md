# FMS — Kiến trúc Hệ thống

## 1. Kiến trúc tổng thể

```
MSSQL (BF1 cũ — BEE_DB)
    │ CDC (SQL Server Agent + transaction log)
    ▼
Debezium Connect (v2.4)
    │ JSON events
    ▼
Apache Kafka (Confluent 7.5.0)
    │ topics: fms.<table_name>
    ▼
Kafka Consumer (Spring Boot)
    │ transform + upsert
    ▼
PostgreSQL (FMS DB mới)
    │ REST API
    ▼
React Frontend (TypeScript)
```

### Bảng thành phần

| Component | Version | Vai trò |
|---|---|---|
| SQL Server CDC | Built-in (SQL Server Agent) | Bắt thay đổi từ transaction log, ghi vào bảng `cdc.*` |
| Debezium Connect | 2.4 | Đọc bảng CDC, chuyển thành Kafka message JSON |
| Apache Kafka | Confluent 7.5.0 | Message broker, lưu trữ CDC events theo topic |
| Kafka Consumer | Spring Boot 3.x | Đọc message từ Kafka, transform và upsert vào PostgreSQL |
| PostgreSQL | latest | Database mới cho FMS |
| Spring Boot | 3.x | REST API backend, xử lý nghiệp vụ |
| React + TypeScript | 18+ | Frontend — tra cứu, báo cáo, quản lý nghiệp vụ |

### Phạm vi dữ liệu

FMS giai đoạn hiện tại sync từ **MSSQL database `BEE_DB`** (hệ thống BF1 cũ). Các database ECUS khác (`ECUS5VNACCS`, `BEE_NEW`, `BEEOLD`) được quản lý bởi Debezium connector riêng (xem `projects/bf1/fms/cdc-architecture.md`).

**Về Kafka Consumer:** Giai đoạn 1 khuyến nghị triển khai consumer như một **Spring Boot microservice độc lập** để tách biệt CDC sync logic. Giai đoạn 2 có thể tích hợp vào FMS API chính tuỳ theo cấu trúc deployment.

---

## 2. CDC Event Format

Mỗi thay đổi trong MSSQL tạo một Kafka message có cấu trúc:

```json
{
  "before": { "TransID": "BIHCM008238/25", "Status": "OLD" },
  "after":  { "TransID": "BIHCM008238/25", "Status": "NEW" },
  "op": "u",
  "ts_ms": 1234567890000,
  "source": {
    "db": "BEE_DB",
    "table": "Transactions",
    "lsn": "00000025:00000d20:0003"
  }
}
```

- `before`: trạng thái cũ — `null` nếu là INSERT
- `after`: trạng thái mới — `null` nếu là DELETE
- `op`: loại thao tác
- `ts_ms`: timestamp UTC tính bằng milliseconds
- `source.lsn`: Log Sequence Number trong SQL Server transaction log

### Bảng giá trị `op`

| Giá trị | Ý nghĩa | Hành động trong Consumer |
|---|---|---|
| `c` | create (INSERT) | INSERT vào PostgreSQL |
| `u` | update (UPDATE) | UPDATE vào PostgreSQL |
| `d` | delete (DELETE) | Soft-delete hoặc DELETE tùy bảng |
| `r` | read / snapshot | UPSERT (dùng khi initial snapshot) |

---

## 3. Kafka Topic Naming

### Pattern

```
fms.<table_name>
```

### Ví dụ thực tế

Các bảng chính trong BEE_DB được CDC và stream qua Kafka:

| Bảng MSSQL (BEE_DB) | Kafka Topic | Mô tả |
|---|---|---|
| `Transactions` | `fms.Transactions` | Master lô hàng |
| `TransactionDetails` | `fms.TransactionDetails` | Chi tiết lô hàng |
| `HAWB` | `fms.HAWB` | House Air/Bill of Lading |
| `Partners` | `fms.Partners` | Đối tác (shipper, consignee, agent) |
| `BookingLocal` | `fms.BookingLocal` | Booking nội địa |
| `SellingRate` | `fms.SellingRate` | Bảng giá bán |
| `BuyingRateWithHBL` | `fms.BuyingRateWithHBL` | Bảng giá mua |
| `DebitNoteDetails` | `fms.DebitNoteDetails` | Chi tiết debit note |
| `Countries` | `fms.Countries` | Danh mục quốc gia |
| `CurrencyExchangeRate` | `fms.CurrencyExchangeRate` | Tỷ giá ngoại tệ |

### Consumer Group

```
fms-consumer-group
```

### Partition Strategy

Message key = Primary Key của record (ví dụ: `TransID`, `HWBNO`, `PartnerID`).

Mục đích: đảm bảo ordering per-record — tất cả thay đổi của cùng một record đi vào cùng một partition, consumer xử lý đúng thứ tự.

> **Giai đoạn 2 — Write-Back Topics:** Khi FMS ghi dữ liệu ngược về MSSQL, dùng topic pattern `fms.writeback.<table_name>` để phân biệt với CDC sync topics.

---

## 4. Error Handling & Dead-Letter Queue

### Luồng xử lý lỗi

```
Kafka message
    │
    ▼
Consumer xử lý
    │ lỗi?
    ├── Retry lần 1 (wait 1s)
    ├── Retry lần 2 (wait 2s)
    ├── Retry lần 3 (wait 4s)
    │
    ▼ vẫn lỗi sau 3 lần
Dead-Letter Queue: fms.dlq.<table_name>
    │
    ▼
Monitor / Alert
    │
    ▼ sau khi fix
Manual replay
```

### Quy tắc

- Retry tối đa 3 lần với exponential backoff (1s, 2s, 4s)
- Sau 3 lần thất bại: publish message gốc vào topic `fms.dlq.<table_name>`
- DLQ message đính kèm thông tin lỗi để debug
- Monitor và alert khi có message vào DLQ
- Sau khi fix lỗi: replay thủ công từ DLQ topic

### Spring Kafka Config

```yaml
spring:
  kafka:
    consumer:
      group-id: fms-consumer-group
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    listener:
      ack-mode: MANUAL
    retry:
      topic:
        enabled: true
        attempts: 3
        delay: 1000
        multiplier: 2
```

---

## 5. Phase 1 vs Phase 2 Data Flow

### Giai đoạn 1 — Read-First Migration

**Mục tiêu:** Nền tảng mới có dữ liệu đầy đủ để tra cứu, báo cáo và đối soát. Hệ thống cũ vẫn là source of truth cho nghiệp vụ ghi.

```
MSSQL (BF1 cũ)
    │ CDC events
    ▼
Kafka (fms.<table_name>)
    │
    ▼
Kafka Consumer (Spring Boot)
    │ transform + upsert (read-only sync)
    ▼
PostgreSQL (FMS DB)
    │ REST API (GET only)
    ▼
React Frontend
  (tra cứu / báo cáo / dashboard)
```

- Consumer chỉ sync data chiều MSSQL → PostgreSQL
- Không có write API từ frontend
- Ưu tiên màn hình: tra cứu lô hàng, HAWB, đối tác, tỷ giá, báo cáo

### Giai đoạn 2 — Write-Back Integration

**Mục tiêu:** Từng bước chuyển nghiệp vụ ghi sang hệ thống mới, đảm bảo hệ thống cũ vẫn hoạt động song song.

```
React Frontend
    │ POST/PUT/DELETE
    ▼
Spring Boot API
    │ write
    ▼
PostgreSQL (FMS DB)
    │ Kafka Producer (write-back events)
    ▼
Kafka (fms.writeback.<table_name>)
    │
    ▼
Write-Back Consumer
    │ transform + ghi ngược
    ▼
MSSQL (BF1 cũ)
  (kế toán cũ tiếp tục hoạt động)
```

- Spring Boot expose write API
- Sau khi ghi vào PostgreSQL, publish event vào Kafka topic write-back
- Write-Back Consumer nhận event, transform đúng cấu trúc MSSQL và ghi ngược
- Đảm bảo kế toán cũ (BF1) vẫn nhận đủ dữ liệu để vận hành
- Rollout theo từng nhóm chức năng, bắt đầu từ nghiệp vụ ít rủi ro

---

## 6. Config Reference

Các biến môi trường cần thiết để chạy FMS backend:

```env
# Database — PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fms_db
DB_USERNAME=fms_user
DB_PASSWORD=...

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP_ID=fms-consumer-group

# Debezium / MSSQL source
MSSQL_HOST=...
MSSQL_PORT=34541
MSSQL_DATABASE=BEE_DB
MSSQL_USERNAME=...
MSSQL_PASSWORD=...

# Dead-Letter Queue
KAFKA_DLQ_TOPIC_PREFIX=fms.dlq

# Debezium Connect
DEBEZIUM_CONNECT_URL=http://localhost:8083
KAFKA_TOPIC_PREFIX=fms
```

> Credentials thực tế lưu trong file `.env` (không commit vào git).

### Các port mặc định (dev local)

| Service | Port |
|---|---|
| Kafka | 9092 |
| Zookeeper | 2181 |
| Debezium Connect | 8083 |
| Kafka UI | 8085 |
| PostgreSQL | 5432 |
| Spring Boot API | 8080 |
| React Dev Server | 3000 |

---

## Authentication & Authorization

> **Scope:** Auth/authorization mechanism is out of scope for this documentation phase.
>
> Developers should expect: JWT Bearer token via `Authorization` header for all `/api/v1/*` endpoints.
> Role-based access control (RBAC) design to be defined separately.
