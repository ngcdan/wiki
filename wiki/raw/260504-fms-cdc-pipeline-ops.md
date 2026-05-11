# FMS CDC Pipeline - Operations Guide

Toan bo pipeline, thao tac, va huong dan van hanh CDC (Change Data Capture) cho FMS.

---

## 1. Tong quan Architecture

```
BF1 MSSQL (HPS_TEST_DB)
     |
     +-- Debezium CDC --> Kafka (of1.{env}.fms.cdc.hps.*) --> CDCListener --> CDCEventHandler --> PostgreSQL (of1_fms_db)
     |
     +-- BatchSyncService (CronJob 30m) --> Kafka (of1.{env}.fms.sync.*) --> Consumer --> PostgreSQL (of1_fms_db)
```

**Infra:**

| Component | Dev | Prod |
|-----------|-----|------|
| MSSQL Host | `10.43.240.129:1433` (cap nhat 2026-05-04) | `10.43.75.99:1433` |
| MSSQL DB | `HPS_TEST_DB` | `HPS_TEST_DB` |
| MSSQL User | `debezium` / `Dbz_Sandbox@2026` | `debezium` / `Dbz_Sandbox@2026` |
| PostgreSQL | `fms-server.of1-beta-platform.svc.cluster.local:5432` / `of1_fms_db` | `crm-server.of1-prod-platform.svc.cluster.local` / `datatp_crm_db` |
| Kafka Connect (Debezium) | `debezium-connect.of1-dev-kafka.svc.cluster.local:8083` | `debezium-connect.of1-prod-kafka.svc.cluster.local:8083` |
| Kafka Brokers | `server-01..03.of1-dev-kafka.svc:9092` | `server-01..03.of1-prod-kafka.svc:9092` |

---

## 2. Debezium Connector Management

### 2.1 Config files

| File | Connector Name | Muc dich |
|------|----------------|----------|
| `scripts/debezium-hps-connector.json` | `mssql-dev-hps-connector` | CDC dev: MSSQL -> Kafka dev |
| `scripts/debezium-hps-connector-dev2prod.json` | `mssql-dev2prod-hps-connector` | CDC dev MSSQL -> Kafka **prod** (cross-cluster producer) |
| `scripts/debezium-hps-connector-prod.json` | `mssql-prod-hps-connector` | CDC prod: MSSQL prod -> Kafka prod |

### 2.2 Cac table CDC dang enable

```
dbo.Partners, dbo.Transactions, dbo.HAWB, dbo.TransactionDetails,
dbo.HAWBDETAILS, dbo.ContainerListOnHBL, dbo.SellingRate,
dbo.BuyingRateWithHBL, dbo.OtherChargeDetail, dbo.ExchangeRate,
dbo.ProfitShares, dbo.CustomsDeclaration, dbo.Trucking_Track,
dbo.TransactionInfo
```

### 2.3 Cheat sheet - Debezium REST API

```bash
# ---- Bien moi truong ----
CONNECT=http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083
NAME=mssql-dev-hps-connector

# ---- List tat ca connector ----
curl -sS "$CONNECT/connectors"

# ---- Xem status (connector + tasks) ----
curl -sS "$CONNECT/connectors/$NAME/status" | python3 -m json.tool

# ---- Xem config hien tai ----
curl -sS "$CONNECT/connectors/$NAME/config"

# ---- Register connector moi ----
curl -sS -X POST "$CONNECT/connectors" \
  -H 'Content-Type: application/json' \
  -d @scripts/debezium-hps-connector.json

# ---- Xoa connector (phai xoa truoc khi register lai) ----
curl -sS -X DELETE "$CONNECT/connectors/$NAME"

# ---- Restart connector + tasks ----
curl -sS -X POST "$CONNECT/connectors/$NAME/restart?includeTasks=true&onlyFailed=false"

# ---- Restart rieng task bi fail ----
curl -sS -X POST "$CONNECT/connectors/$NAME/tasks/0/restart"

# ---- Pause / Resume ----
curl -sS -X PUT "$CONNECT/connectors/$NAME/pause"
curl -sS -X PUT "$CONNECT/connectors/$NAME/resume"

# ---- Update config (PUT, body la config object khong co wrapper) ----
curl -sS -X PUT "$CONNECT/connectors/$NAME/config" \
  -H 'Content-Type: application/json' \
  -d @scripts/debezium-hps-connector.json
# Luu y: PUT /config can body la config object, khong phai {name, config}
```

### 2.4 Quy trinh doi IP / update connector

```bash
# 1. Sua file config (vi du doi database.hostname)
vim scripts/debezium-hps-connector.json

# 2. Xoa connector cu
curl -sS -X DELETE "$CONNECT/connectors/$NAME"
# HTTP 204 = thanh cong

# 3. Register lai
curl -sS -X POST "$CONNECT/connectors" \
  -H 'Content-Type: application/json' \
  -d @scripts/debezium-hps-connector.json
# HTTP 201 = thanh cong

# 4. Verify status (doi 3-5s cho task spawn)
curl -sS "$CONNECT/connectors/$NAME/status" | python3 -m json.tool
# Expected: connector RUNNING, tasks[0] RUNNING
```

### 2.5 Them table moi vao CDC

```bash
# 1. Enable CDC tren MSSQL
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name = N'YourTable',
  @role_name = NULL;

# 2. Verify
SELECT name, is_tracked_by_cdc FROM sys.tables WHERE name = 'YourTable';

# 3. Sua file config: them vao table.include.list
# 4. Xoa + register lai connector (muc 2.4)
# 5. Tao CDCEventHandler class (muc 4)
# 6. Build + restart FMS server
```

---

## 3. Kafka Topic Naming

### 3.1 Scheme

```
of1.<env>.fms.<action>.<domain>[.DLQ]
```

- `<env>` = `dev` | `prod`
- `<action>` = `sync` | `writeback` | `cdc`
- `<domain>` = kebab-case

### 3.2 CDC Topics (tu dong tao boi Debezium)

```
of1.<env>.fms.cdc.hps.HPS_TEST_DB.dbo.<TableName>
```

Vi du:
- `of1.dev.fms.cdc.hps.HPS_TEST_DB.dbo.Transactions`
- `of1.dev.fms.cdc.hps.HPS_TEST_DB.dbo.HAWB`

### 3.3 Batch Sync Topics

| Topic | Data |
|-------|------|
| `of1.<env>.fms.sync.transaction` | Transaction |
| `of1.<env>.fms.sync.housebill` | Housebill |
| `of1.<env>.fms.sync.hawb-profit` | HAWB Profit |
| `of1.<env>.fms.sync.exchange-rate` | Exchange Rate |
| `of1.<env>.fms.sync.setting-unit` | Setting Unit |
| `of1.<env>.fms.sync.bank` | Bank |
| `of1.<env>.fms.sync.industry` | Industry |
| `of1.<env>.fms.sync.partner-source` | Partner Source |
| `of1.<env>.fms.sync.commodity` | Commodity |
| `of1.<env>.fms.sync.user-role` | User Role |
| `of1.<env>.fms.sync.name-fee-desc` | Name Fee Description |
| `of1.<env>.fms.sync.custom-list` | Custom List |

DLQ: `<topic>.DLQ` (vi du `of1.dev.fms.cdc.hps.HPS_TEST_DB.dbo.Transactions.DLQ`)

---

## 4. CDC Handlers

### 4.1 Danh sach handler

| Handler | Source Table | Target Table(s) | Logic |
|---------|-------------|------------------|-------|
| `TransactionsCDCHandler` | `Transactions` | `integrated_transaction` + `of1_fms_transactions` + `of1_fms_container` + `of1_fms_transport_plan` | Parse ContainerSize, tinh reportDate, companyBranchCode |
| `TransactionDetailsCDCHandler` | `TransactionDetails` | `of1_fms_house_bill` | Skeleton HBL + client/saleman + desc/packaging |
| `HAWBCDCHandler` | `HAWB` | `integrated_housebill` + `of1_fms_house_bill` + `of1_fms_cargo` | Cargo weights, container, agent, auto-upsert cargo |
| `HAWBDETAILSCDCHandler` | `HAWBDETAILS` | `of1_fms_air_house_bill_detail` / `of1_fms_sea_house_bill_detail` | Air/Sea detail |
| `ContainerListOnHBLCDCHandler` | `ContainerListOnHBL` | `of1_fms_container` | Container no + seal no line items |
| `SellingRateCDCHandler` | `SellingRate` | `of1_fms_house_bill_invoice` + `_item` | Debit invoice |
| `BuyingRateWithHBLCDCHandler` | `BuyingRateWithHBL` | `of1_fms_house_bill_invoice` + `_item` | Credit invoice |
| `OtherChargeDetailCDCHandler` | `OtherChargeDetail` | `of1_fms_house_bill_invoice` + `_item` | On_Behalf invoice |
| `PartnersCDCHandler` | `Partners` | `integrated_partner` | 30+ fields, enum mapping, soft delete |

### 4.2 CDC Handler Pattern

```java
@Component
public class YourTableCDCHandler implements CDCEventHandler {

  @Autowired
  private YourEntityRepository repo;

  @Autowired
  private EntityLockManager lockManager;

  @Override
  public String getTableName() { return "YourMSSQLTableName"; }

  @Override
  @Transactional(transactionManager = "fmsTransactionManager")
  public void handleCreate(CDCEvent<Map<String, Object>> event) {
    Map<String, Object> after = event.getAfter();
    String key = CDCMapperUtils.trimString(after.get("PrimaryKeyColumn"));
    synchronized (lockManager.getLock("yourEntity:" + key)) {
      YourEntity entity = repo.getByKey(key);
      if (entity == null) { entity = new YourEntity(); entity.setKey(key); }
      // map fields from after -> entity
      repo.save(entity);
    }
  }

  @Override
  public void handleUpdate(CDCEvent<Map<String, Object>> event) {
    handleCreate(event); // upsert pattern
  }

  @Override
  public void handleDelete(CDCEvent<Map<String, Object>> event) {
    Map<String, Object> before = event.getBefore();
    String key = CDCMapperUtils.trimString(before.get("PrimaryKeyColumn"));
    synchronized (lockManager.getLock("yourEntity:" + key)) {
      YourEntity entity = repo.getByKey(key);
      if (entity != null) {
        entity.setStorageState(StorageState.ARCHIVED);
        repo.save(entity);
      }
    }
  }

  @Override
  public void handleSnapshot(CDCEvent<Map<String, Object>> event) {
    handleCreate(event);
  }
}
```

### 4.3 CDC Infrastructure Components

| Component | Package | Mo ta |
|-----------|---------|-------|
| `CDCEvent<T>` | `of1.fms.core.cdc.model` | Debezium event model: `before`, `after`, `source`, `op` (c/u/d/r) |
| `CDCEventHandler` | `of1.fms.core.cdc.handler` | Interface: `getTableName()`, `handle{Create,Update,Delete,Snapshot}()` |
| `CDCEventHandlerRegistry` | `of1.fms.core.cdc.handler` | Auto-scan beans via `ApplicationContext.getBeansOfType()` |
| `CDCListener` | `of1.fms.core.cdc.listener` | `@KafkaListener` pattern match, manual ACK, dispatch to registry |
| `CDCKafkaConfig` | `of1.fms.core.cdc.config` | Rieng consumer factory, retry 3x + DLQ |
| `EntityLockManager` | `of1.fms.core.cdc.lock` | Per-entity ConcurrentHashMap lock, max 100k |
| `CDCMapperUtils` | `of1.fms.core.cdc.util` | `parseLong/Integer/Double/BigDecimal/Boolean`, `trimString`, `toTimestamp` |
| `CDCSyncMonitorService` | `of1.fms.core.cdc` | Track processed/error count, offset, MD5 checksum |

---

## 5. Batch Sync Pipeline

### 5.1 Flow

```
CronJob (30m, prod only)
   |
   v
FMSDaoService (Groovy SQL -> MSSQL)
   |
   v
BatchSyncService (chunk 5000, batch 50)
   |
   v
Producer -> Kafka -> Consumer -> PostgreSQL
```

### 5.2 RPC Endpoints (BFSOneSyncService)

Goi qua: `POST {host}/platform/plugin/fms/rest/v1.0.0/rpc/internal/call`

```json
{
  "component": "BFSOneSyncService",
  "endpoint": "<method>",
  "userParams": { "sourceDb": "HPS" }
}
```

| Method | Mo ta |
|--------|-------|
| `syncTransactions` | Dong bo toan bo transaction |
| `syncByTransactionIds` | Dong bo housebill + profit cho danh sach transactionId |
| `syncHousebills` | Dong bo housebill cua 1 transaction |
| `syncHawbProfits` | Dong bo HAWB profit |
| `syncExchangeRates` | Dong bo ti gia USD |
| `syncSettingUnits` | Dong bo don vi |
| `syncTransactionTrackings` | Dong bo tracing |

---

## 6. CDC Trigger Script (Dev/Test)

Reset va trigger lai CDC data cho dev/test.

```bash
python3 scripts/cdc-trigger.py
```

### 6.1 Script lam gi (theo thu tu)

1. **Clean PostgreSQL** - Xoa toan bo data FMS (child tables truoc):
   `invoice_item -> invoice -> cargo -> transport_plan -> *_detail -> document_history -> house_bill -> container -> transactions`

2. **Lookup HWBNO** - Query MSSQL `TransactionDetails` + `HAWB` cho tat ca target TRANSIDs

3. **Trigger CDC** - Update 12 MSSQL tables theo thu tu (delay 5s giua moi table):
   `Transactions -> TransactionDetails -> HAWB -> HAWBDETAILS -> SellingRate -> BuyingRateWithHBL -> OtherChargeDetail -> ProfitShares -> ContainerListOnHBL -> CustomsDeclaration -> Trucking_Track -> TransactionInfo`

4. Debezium capture changes -> Kafka -> FMS consumers tai tao data trong PostgreSQL

### 6.2 Luu y

- Script dung MSSQL host `10.43.240.129` (can update neu IP thay doi)
- `DELAY_BETWEEN_TABLES = 5` giay — cho consumer du thoi gian tao HouseBill truoc khi HAWB event den
- Idempotent: chay nhieu lan an toan
- Chi dung cho dev/test, **KHONG** chay tren prod

---

## 7. Configuration

### 7.1 Kafka Config (addon-fms-config.yaml)

```yaml
datatp:
  msa:
    fms:
      queue:
        event-producer-enable: true
        event-consumer-enable: true
        cdc:
          topics: "of1.${env.kafka.env}.fms.cdc.hps.*"
          consumer-group: "fms-cdc-consumer-${env.kafka.env}"
          concurrency: 5
          auto-startup: true
          retry:
            max-attempts: 3
            backoff-interval: 1000
          dlq:
            topic-suffix: .DLQ
            enabled: true
```

### 7.2 MSSQL Datasource (env.sh)

```bash
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.host=10.43.240.129"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.port=1433"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.db=HPS_TEST_DB"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.username=sa"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.password=Sa12345*"
```

---

## 8. Build & Deploy

```bash
# Build BE + FE
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
./tools.sh build -clean -code -ui

# QUAN TRONG: Copy snappy-java sau moi lan build (Debezium can)
cp /Users/nqcdan/OF1/forgejo/of1-platform/working/release-egov/server/addons/egov/lib/snappy-java-1.1.10.5.jar \
   /Users/nqcdan/OF1/forgejo/of1-platform/working/release-fms/server/addons/fms/lib/

# Run server
cd /Users/nqcdan/OF1/forgejo/of1-platform/working/release-fms/server-env
bash instances.sh run

# Verify CDC handlers registered
grep "Registered CDC\|Total CDC" server.log
```

---

## 9. Troubleshooting

### 9.1 Connector khong RUNNING

```bash
# Check status
curl -sS "$CONNECT/connectors/$NAME/status" | python3 -m json.tool

# Neu FAILED -> check log worker Debezium
# Thuong gap: loi auth MSSQL, khong connect duoc broker, sai IP

# Restart
curl -sS -X POST "$CONNECT/connectors/$NAME/restart?includeTasks=true"
```

### 9.2 Handler khong duoc register

- Check log: `grep "Registered CDC handler" server.log`
- Nguyen nhan pho bien: `@Autowired List<CDCEventHandler>` chi inject beans trong cung module
- Fix: Dung `ApplicationContext.getBeansOfType(CDCEventHandler.class)` voi `@EventListener(ApplicationReadyEvent.class)`

### 9.3 SnappyOutputStream ClassNotFoundException

- Debezium mac dinh dung snappy compression
- Fix: Copy `snappy-java-1.1.10.5.jar` vao FMS lib (xem muc 8)
- Hoac: Set `producer.compression.type: none` trong connector config

### 9.4 Consumer khong nhan event

- Check `auto-startup: true` trong addon-fms-config.yaml
- Check `event-consumer-enable: true`
- Neu them table moi: restart server de consumer re-subscribe

### 9.5 Duplicate data / Race condition

- CDC dung `EntityLockManager` de dam bao thread safety
- `CDCSyncMonitorService` track MD5 checksum
- HAWB INSERT co the cho fields null (INSERT minimal, sau do UPDATE rieng tung field) -> handler dung upsert pattern

### 9.6 Monitoring queries

```sql
-- PostgreSQL: CDC sync status
SELECT table_name, processed_count, error_count, last_error, last_sync_time
FROM of1_fms_cdc_sync_status ORDER BY table_name;

-- Tables co loi
SELECT table_name, error_count, last_error
FROM of1_fms_cdc_sync_status WHERE error_count > 0;
```

```bash
# Kafka: consumer group lag
kafka-consumer-groups.sh --bootstrap-server <broker> \
  --describe --group fms-cdc-consumer-<env>

# List CDC topics
kafka-topics.sh --bootstrap-server <broker> --list | grep "of1.*cdc"

# Doc DLQ
kafka-console-consumer.sh --bootstrap-server <broker> \
  --topic of1.<env>.fms.cdc.hps.HPS_TEST_DB.dbo.<Table>.DLQ --from-beginning
```

---

## 10. Lich su thay doi

| Ngay | Thay doi |
|------|---------|
| 2026-05-04 | Update MSSQL host dev: `10.43.39.49` -> `10.43.240.129`, re-register connector |
| 2026-04-07 | Chuan hoa Kafka topic naming (`of1.<env>.fms.<action>.<domain>`), fix DAOTemplate log spam |
| 2026-04-07 | Tao Debezium prod + dev2prod connector |
| 2026-04-02 | Update connector password + mo rong table list (4 -> 11 tables) |
| 2026-03-31 | Implement 4 CDC handlers dau tien (Partners, Transactions, HAWB, HAWBRATE) |
| 2026-03-31 | CDC infrastructure (CDCEvent, CDCListener, CDCKafkaConfig, EntityLockManager) |
| 2026-03-28 | Port BFSOne Batch Sync pipeline |
