# Developer Log

## 2026-03-31: CDC Handlers E2E — Partners, Transactions, HAWB, HAWBRATE

### Tong quan

Implement 4 CDC handlers dong bo du lieu tu HPS MSSQL ve FMS PostgreSQL qua Debezium + Kafka.
Test va verify E2E cho tat ca INSERT/UPDATE/DELETE operations.

### 1. CDC Handler Implementation

#### PartnersCDCHandler
- **File:** `module/partner/src/main/java/of1/fms/module/partner/cdc/PartnersCDCHandler.java`
- **Source table:** `Partners` (HPS MSSQL, 107 columns)
- **Target entity:** `IntegratedPartner` (FMS PostgreSQL, table `integrated_partner`)
- **Mapping:** 30+ fields — PartnerID->partnerCode, PartnerName->label, Group->PartnerGroup enum, Category->PartnerCategory enum, Location->PartnerScope enum
- **Delete behavior:** Soft delete — set `storageState = ARCHIVED`
- **Enum mapping:** Normalize strings truoc khi parse enum (e.g. `AGENT - OVERSEAS` -> `AGENT_OVERSEAS`, `Domestic` -> `DOMESTIC`)

#### TransactionsCDCHandler
- **File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java`
- **Source table:** `Transactions` (HPS MSSQL, 127 columns)
- **Target entity:** `IntegratedTransaction` (table `integrated_transaction`)
- **Mapping:** TransID->transactionId, TpyeofService->typeOfService, PortofLading/Unlading->fromLocationCode/toLocationCode, LoadingDate->etd, ArrivalDate->eta, ContainerSize, WhoisMaking->creatorUsername
- **Derived fields** (tu dong tinh):
  - `companyBranchCode`: extract tu transactionId (e.g. `VNHCM12345` -> `HCM`)
  - `reportDate`: Export dung etd, Import dung eta, fallback transactionDate
  - `cont20Count/cont40Count/cont45Count`: parse tu containerSize (e.g. `2x40HC & 1x20` -> 20:1, 40:2)
- **Them repo method:** `IntegratedTransactionRepository.getByTransactionId()`

#### HAWBCDCHandler
- **File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java`
- **Source table:** `HAWB` (HPS MSSQL)
- **Target entity:** `IntegratedHousebill` (table `integrated_housebill`)
- **Mapping:** HWBNO->hawbNo, TRANSID->transactionId, ConsigneeID->customerCode, Consignee->customerName, HBAgentID->agentCode, GrossWeight->hawbGw, ChargeableWeight->hawbCw, Dimension->hawbCbm, Pieces->totalPackages
- **Luu y:** `HAWB.ShipmentType` la `decimal` (khong phai varchar) — can truyen so khi INSERT/UPDATE tren MSSQL

#### HAWBRATECDCHandler
- **File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBRATECDCHandler.java`
- **Source table:** `HAWBRATE` (HPS MSSQL)
- **Target entity:** `IntegratedHawbProfit` (table `integrated_hawb_profit`)
- **Logic:** Lookup `IntegratedHousebill` by hawbNo de lay transactionId, customerCode, agentCode. Map RateCharges voi Shmt/Collect flags vao selling/buying VND.
- **Luu y:** HAWBRATE la charge line items — mapping financial fields can review them vi schema HPS khong 1:1 voi FMS profit model

### 2. CDCEventHandlerRegistry Fix

**Van de:** `@Autowired(required=false) List<CDCEventHandler>` chi inject beans trong cung module. Handlers o `module/partner` va `module/transaction` khong duoc inject vao registry o `module/core`.

**Fix:** Doi sang `ApplicationContext.getBeansOfType(CDCEventHandler.class)` trong `@EventListener(ApplicationReadyEvent.class)`:
```java
// Truoc (chi thay beans trong core module):
@Autowired(required=false)
private List<CDCEventHandler> eventHandlers;

// Sau (thay tat ca beans cross-module):
@EventListener(ApplicationReadyEvent.class)
public void init() {
    Map<String, CDCEventHandler> beans = applicationContext.getBeansOfType(CDCEventHandler.class);
    // register all handlers
}
```

### 3. Enable CDC tren MSSQL

```sql
-- Enable CDC cho tung table (chay tren HPS_TEST_DB)
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name = N'Partners',    -- hoac 'Transactions', 'HAWB', 'HAWBRATE'
  @role_name = NULL,
  @supports_net_changes = 1;

-- Verify
SELECT name, is_tracked_by_cdc FROM sys.tables
WHERE name IN ('Partners', 'Transactions', 'HAWB', 'HAWBRATE');
```

### 4. Debezium Connector

**Endpoint:** `http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083`

**Config file:** `scripts/debezium-hps-connector.json`
```json
{
  "table.include.list": "dbo.Partners,dbo.Transactions,dbo.HAWB,dbo.HAWBRATE",
  "topic.prefix": "cdc-dev-hps",
  "producer.compression.type": "none",
  "snapshot.mode": "schema_only"
}
```

**Cac lenh quan ly:**
```bash
# Tao connector
curl -X POST -H "Content-Type: application/json" \
  --data @scripts/debezium-hps-connector.json \
  http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors

# Update config (them table moi)
curl -X PUT -H "Content-Type: application/json" \
  --data '{ ...config... }' \
  http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/config

# Restart (bat buoc sau khi update)
curl -X POST http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/restart?includeTasks=true

# Check status
curl http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/status
```

**Kafka topics duoc tao:**
- `cdc-dev-hps.HPS_TEST_DB.dbo.Partners`
- `cdc-dev-hps.HPS_TEST_DB.dbo.Transactions`
- `cdc-dev-hps.HPS_TEST_DB.dbo.HAWB`
- `cdc-dev-hps.HPS_TEST_DB.dbo.HAWBRATE`

### 5. Build va Deploy

```bash
# Build code (PHAI dung -clean -code)
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
./tools.sh build -clean -code

# QUAN TRONG: Sau khi build, copy snappy-java JAR (build overwrite lib/)
cp /Users/nqcdan/OF1/forgejo/of1-platform/working/release-egov/server/addons/egov/lib/snappy-java-1.1.10.5.jar \
   /Users/nqcdan/OF1/forgejo/of1-platform/working/release-fms/server/addons/fms/lib/

# Neu them handler moi, force rebuild module JAR truoc tools.sh build
gradle :of1-fms-module-transaction:clean :of1-fms-module-transaction:jar

# Start server
cd /Users/nqcdan/OF1/forgejo/of1-platform/working/release-fms/server-env
bash instances.sh run
```

**Verify sau khi start:**
```bash
# Check handlers registered
grep "Registered CDC\|Total CDC" server.log
# Expected: Total CDC handlers registered: 4

# Check partitions assigned
grep "partitions assigned" server.log | grep HAWB
# Expected: HAWB + HAWBRATE partitions assigned
```

### 6. Troubleshooting Gaps da Gap

**Snappy ClassNotFoundException:**
- Debezium mac dinh dung snappy compression
- FMS server thieu `snappy-java` JAR → CDC consumer crash ngay khi nhan message
- Fix: Copy `snappy-java-1.1.10.5.jar` vao FMS lib, hoac doi connector `producer.compression.type: none`
- **Phai copy lai sau moi lan `tools.sh build`** vi build overwrite lib/

**Handler khong duoc register (Total = 1 thay vi 4):**
- Nguyen nhan: `@Autowired List<CDCEventHandler>` chi inject beans visible trong module hien tai
- Fix: Doi sang `ApplicationContext.getBeansOfType()` voi `@EventListener(ApplicationReadyEvent.class)`

**HAWB/HAWBRATE topics khong duoc consume:**
- Nguyen nhan: Topic duoc tao SAU khi consumer da join group → consumer khong biet topic moi
- Fix: Restart server de consumer re-subscribe va discover topics moi

**HAWB INSERT cho fields null:**
- Nguyen nhan: INSERT minimal (chi HWBNO, TRANSID), sau do UPDATE rieng tung field
- CDC bat ca 2 event: event INSERT co tat ca field = null, event UPDATE chi co field da thay doi
- Giai phap: Handler dung pattern upsert — luon ghi de field tu `event.after`, null field khong bi overwrite

**HAWB.ShipmentType la decimal (khong phai varchar):**
- Khi INSERT/UPDATE tren MSSQL phai dung so (vd: `ShipmentType = 1`), khong dung string
- CDC event tra ve number, handler map thanh String

**HAWBRATE.IDKeyIX la IDENTITY:**
- Khong can truyen gia tri khi INSERT, SQL Server tu tang
- `FreightCharges` la NOT NULL (nvarchar) — phai co gia tri

### 7. E2E Test Results

| Handler | Operation | MSSQL | Kafka CDC | PostgreSQL |
|---------|-----------|-------|-----------|------------|
| Partners | INSERT | CS999901 | op=c | partner_code=CS999901, label, email, scope=DOMESTIC |
| Partners | UPDATE | CS999901 | op=u | label updated, email updated |
| Partners | DELETE | CS999901 | op=d | storage_state=ARCHIVED |
| Transactions | INSERT | VNHCM-CDC-001 | op=c | type=AirExp, from=VNSGN, to=USLAX, reportDate=etd |
| Transactions | INSERT | VNHPH-CDC-002 | op=c | cont20=1, cont40=2, branchCode=HPH |
| Transactions | UPDATE | VNHCM-CDC-001 | op=u | to=CNSHA, eta updated |
| Transactions | DELETE | VNHPH-CDC-002 | op=d | storage_state=ARCHIVED |
| HAWB | INSERT+UPDATE | HAWB-CDC-001 | op=c,u | customerCode=CS999901, gw=150.5, cbm=1.2 |
| HAWBRATE | INSERT+UPDATE | HAWB-CDC-001 | op=c,u | hawbProfit synced, lastUpdateBy=HPS_CDC |

**Verify commands:**
```bash
# Partners
psql "postgresql://of1-fms:of1-fms@postgres.of1-dev-crm.svc.cluster.local:5432/of1_fms_db" \
  -c "SELECT partner_code, label, scope, category, source FROM integrated_partner;"

# Transactions
psql ... -c "SELECT transaction_id, type_of_service, from_location_code, to_location_code, report_date, company_branch_code FROM integrated_transaction;"

# HouseBill
psql ... -c "SELECT hawb_no, transaction_id, customer_code, agent_code, hawb_gw, hawb_cbm FROM integrated_housebill;"

# HawbProfit
psql ... -c "SELECT hawb_no, transaction_id, subtotal_selling_vnd, last_update_by FROM integrated_hawb_profit;"
```

### 8. Pattern de them CDC handler moi

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
  // handleUpdate: same as create (upsert pattern)
  // handleDelete: soft delete (storageState = ARCHIVED)
  // handleSnapshot: delegate to handleCreate
}
```

**Buoc them table moi vao CDC pipeline:**
1. Enable CDC tren MSSQL: `EXEC sys.sp_cdc_enable_table @source_name = N'TableName'`
2. Update Debezium connector: them vao `table.include.list`
3. Restart connector: `curl -X POST .../restart?includeTasks=true`
4. Tao handler class implement `CDCEventHandler`
5. Build: `gradle :module:clean :module:jar && ./tools.sh build -clean -code`
6. Copy snappy JAR
7. Restart server (de discover topic moi)

---

## 2026-03-31: HPS CDC Pipeline + Master Data Group A Backend

### Tong quan

Implement CDC (Change Data Capture) pipeline tu HPS MSSQL database ve FMS PostgreSQL qua Debezium + Kafka.
Dong thoi them toan bo 11 entity Master Data nhom A (Location + Currency) vao FMS settings module.

Pipeline: `MSSQL (HPS) -> Debezium CDC -> Kafka topic -> CDCListener -> CDCEventHandler -> PostgreSQL`

### 1. Master Data Group A — 11 Entities

Tao Entity/Repository/Logic/Service/Groovy SQL cho toan bo nhom A theo master-data-diagram.md.
Copy pattern tu of1-platform entities, rename theo convention FMS (`Setting*`).

**2 package moi:**

| Package | Entities | Mo ta |
|---------|----------|-------|
| `of1.fms.settings.location` | A1-A9 (9 entity) | Country, CountryGroup, CountryGroupRel, Zone, LocationState, LocationDistrict, LocationSubdistrict, Location, LocationReferenceCode |
| `of1.fms.settings.currency` | A10-A11 (2 entity) | SettingCurrency, SettingCurrencyExchangeRate |

**Luu y:**
- A4 `SettingZone` va A9 `SettingLocationReferenceCode` la entity moi hoan toan (khong co source tu platform)
- A3 `SettingCountryGroupRel` chi co Entity + Repository, query qua `SettingCountryGroupLogic`
- Package `currency` da co `ExchangeRate` entity cu — them `SettingCurrency*` song song, khong modify file cu
- Index name phai <= 63 ky tu (PostgreSQL limit), vi du `fms_loc_subdistrict_code_idx`
- Update `FmsSettingsModuleConfig.java` them scan packages `of1.fms.settings.location.entity` va `of1.fms.settings.location.repository`

**Moi entity gom 5 file:**
- Entity: extend `PersistableEntity<Long>`, `@JsonInclude(NON_NULL)`, table name `of1_fms_settings_*`
- Repository: extend `JpaRepository<Entity, Serializable>`, JPQL queries
- Logic: extend `FMSDaoService`, inject repository, `searchDbRecords()` qua Groovy SQL
- Service: `@Service("SettingXxxService")`, `@Transactional(transactionManager = "fmsTransactionManager")`
- Groovy SQL: `ExecutableSqlBuilder` voi `FILTER_BY_STORAGE_STATE`, `AND_SEARCH_BY_PARAMS`, `MAX_RETURN`

### 2. HPS MSSQL Datasource

Them HPS datasource vao FMSDaoService, mirror pattern BFSOne.

**Config** (`addon-fms-config.yaml`):
```yaml
env:
  hps:
    host: win-server-vm.of1-dev-crm.svc.cluster.local
    port: 1433
    db: HPS_TEST_DB
    username: sa
    password: "Sa12345*"
```

**Runtime env** (`working/release-fms/server-env/env.sh`):
```bash
# Truyen env vars qua JVM system properties khi chay server
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.host=win-server-vm.of1-dev-crm.svc.cluster.local"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.port=1433"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.db=HPS_TEST_DB"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.username=sa"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.hps.password=Sa12345*"
```

**FMSDaoService.java** — 3 methods moi:
```java
// Tao MSSQL datasource tu env properties, dung ExternalDataSourceManager de pool connection
public DataSource getHPSDataSource(ClientContext ctx) { ... }

// Chay Groovy SQL query tren HPS, tra ve SqlSelectView (raw result)
public SqlSelectView searchHPSDbView(ClientContext ctx, String scriptFile, String scriptName, SqlQueryParams sqlParams) { ... }

// Chay Groovy SQL query tren HPS, tra ve List<SqlMapRecord> (da rename column sang camelCase)
public List<SqlMapRecord> searchHPSDbRecords(ClientContext ctx, String scriptFile, String scriptName, SqlQueryParams sqlParams) { ... }
```

### 3. CDC Infrastructure

Tham khao of1-egov (`/of1-egov/module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/`), don gian hoa bo multi-tenant.

**Package:** `of1.fms.core.cdc`

| File | Mo ta |
|------|-------|
| `model/CDCEvent.java` | Debezium CDC event model. Generic `CDCEvent<T>` voi `before` (du lieu truoc), `after` (du lieu sau), `source` (db/schema/table), `op` (c=create, u=update, d=delete, r=snapshot) |
| `handler/CDCEventHandler.java` | Interface. Moi handler khai bao `getTableName()` va 4 method: `handleCreate`, `handleUpdate`, `handleDelete`, `handleSnapshot` |
| `handler/CDCEventHandlerRegistry.java` | Spring `@Service`. Tu dong tim tat ca bean `CDCEventHandler` qua `@Autowired(required=false)`, dang ky vao map theo table name. Khi co CDC event, lookup handler bang `getHandler(tableName)` |
| `listener/CDCListener.java` | Kafka consumer `@KafkaListener`. Subscribe topic pattern `cdc-{env}-hps.*`. Parse CDC event tu JSON, lay table name tu `event.source.table`, dispatch toi handler qua registry. Manual ACK sau khi xu ly thanh cong |
| `config/CDCKafkaConfig.java` | Tao rieng `cdcKafkaListenerContainerFactory` (tach biet voi Kafka cua SyncQueueConfig). Cau hinh: manual ACK, retry voi `FixedBackOff`, DLQ (Dead Letter Queue) khi het retry |
| `lock/EntityLockManager.java` | Per-entity lock dung `ConcurrentHashMap`. Dam bao 2 CDC event cung entity khong xu ly dong thoi. Max 100k lock, auto clear khi vuot nguong |
| `util/CDCMapperUtils.java` | Helper chuyen doi kieu du lieu tu CDC Map sang Java types: `parseLong`, `parseInteger`, `parseDouble`, `parseBoolean`, `trimString`, `toTimestamp` |

**CDC Kafka Config** (`addon-fms-config.yaml`):
```yaml
datatp:
  msa:
    fms:
      queue:
        cdc:
          topics: "cdc-${env.kafka.env}-hps.*"        # Topic pattern match tat ca table tu HPS
          consumer-group: "fms-cdc-consumer-${env.kafka.env}"
          concurrency: 5                                # 5 consumer thread song song
          auto-startup: true                            # Tu dong bat khi server start
          retry:
            max-attempts: 3                             # Thu lai 3 lan khi loi
            backoff-interval: 1000                      # Doi 1s giua cac lan thu
          dlq:
            topic-suffix: .DLQ                          # Dead Letter Queue topic = original + .DLQ
            enabled: true                               # Bat DLQ
```

### 4. PartnersCDCHandler — CDC Handler dau tien

**File:** `module/partner/src/main/java/of1/fms/module/partner/cdc/PartnersCDCHandler.java`

Map 30+ fields tu HPS `Partners` table sang FMS `IntegratedPartner` entity:
- `PartnerID` -> `partnerCode`
- `PartnerName/PartnerName2/PartnerName3` -> `label/localizedLabel/name`
- `Group` -> `PartnerGroup` enum (CUSTOMERS, AGENTS, COLOADERS, ...)
- `Category` -> `PartnerCategory` enum (normalize: `AGENT - OVERSEAS` -> `AGENT_OVERSEAS`)
- `Location` -> `PartnerScope` enum (Domestic -> DOMESTIC, Overseas -> OVERSEAS)
- DELETE = soft delete (set `storageState = ARCHIVED`), khong xoa record

**Pattern de tao CDC handler moi:**
```java
@Component
public class YourTableCDCHandler implements CDCEventHandler {
  @Override public String getTableName() { return "YourTable"; }  // Ten bang tren MSSQL
  @Override public void handleCreate(CDCEvent<Map<String, Object>> event) {
    Map<String, Object> after = event.getAfter();   // Du lieu sau khi insert
    // Map fields va save vao PostgreSQL
  }
  @Override public void handleUpdate(CDCEvent<Map<String, Object>> event) { ... }
  @Override public void handleDelete(CDCEvent<Map<String, Object>> event) {
    Map<String, Object> before = event.getBefore();  // Du lieu truoc khi delete
  }
  @Override public void handleSnapshot(CDCEvent<Map<String, Object>> event) { handleCreate(event); }
}
```

### 5. Debezium Connector Setup

**Kafka Connect endpoint:** `http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083`

**Tao connector:**
```bash
# Tao moi Debezium connector cho HPS_TEST_DB
curl -X POST -H "Content-Type: application/json" \
  --data @scripts/debezium-hps-connector.json \
  http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors

# Check trang thai
curl http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/status

# List tat ca connectors
curl http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors

# Restart connector (sau khi update config)
curl -X POST http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/restart?includeTasks=true

# Update config connector (vi du doi compression)
curl -X PUT -H "Content-Type: application/json" \
  --data '{ ... config ... }' \
  http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector/config

# Xoa connector
curl -X DELETE http://debezium-connect.of1-dev-kafka.svc.cluster.local:8083/connectors/mssql-dev-hps-connector
```

**Connector config** (`scripts/debezium-hps-connector.json`):
- `topic.prefix: cdc-dev-hps` — prefix cho Kafka topic, topic se la `cdc-dev-hps.{DB}.dbo.{TABLE}`
- `table.include.list: dbo.Partners` — chi CDC bang Partners (them bang khac bang dau phay)
- `snapshot.mode: schema_only` — chi lay schema, khong snapshot data cu
- `producer.compression.type: none` — tat compression (tranh loi snappy)

**Luu y quan trong:** Neu dung `producer.compression.type: snappy`, FMS server can co `snappy-java` JAR trong classpath. Copy tu egov:
```bash
cp working/release-egov/server/addons/egov/lib/snappy-java-1.1.10.5.jar \
   working/release-fms/server/addons/fms/lib/
```

### 6. Build va Run Server

**Build:**
```bash
# cd vao thu muc of1-fms
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms

# Build toan bo project (of1-core + of1-platform + of1-fms + webui)
# -clean: xoa build cu, -build: build code
bash tools.sh build -clean -build
```

**Run server:**
```bash
# cd vao thu muc release
cd /Users/nqcdan/OF1/forgejo/of1-platform/working/release-fms/server-env

# Chay server (foreground, thay log truc tiep)
bash instances.sh run

# Chay server (background daemon)
bash instances.sh start

# Dung server
bash instances.sh stop

# Xem log
bash instances.sh log:watch
```

**Cau hinh server** (`working/release-fms/server-env/env.sh`):
- `env.name` — moi truong (dev/beta/prod)
- `env.db.host/port` — PostgreSQL FMS
- `env.kafka.env` — Kafka environment (dev/prod)
- `env.hps.*` — HPS MSSQL connection
- `env.bfsone.*` — BFSOne MSSQL connection

### 7. E2E Test Results

| Step | Lenh | Ket qua |
|------|------|---------|
| MSSQL CDC enabled | `SELECT is_cdc_enabled FROM sys.databases` | `True` cho HPS_TEST_DB va table Partners |
| Debezium connector | `curl .../connectors/mssql-dev-hps-connector/status` | RUNNING |
| Kafka topic | `cdc-dev-hps.HPS_TEST_DB.dbo.Partners` | Created, messages flowing |
| INSERT Partner | SQL: `INSERT INTO Partners (PartnerID='CS999901', ...)` | CDC `op=c` -> `CDC CREATE partner: CS999901` -> PostgreSQL synced |
| UPDATE Partner | SQL: `UPDATE Partners SET PartnerName='...' WHERE PartnerID='CS999901'` | CDC `op=u` -> `CDC UPDATE partner: CS999901` -> fields updated |
| DELETE Partner | SQL: `DELETE FROM Partners WHERE PartnerID='CS999901'` | CDC `op=d` -> `CDC DELETE (archive) partner: CS999901` -> `storage_state=ARCHIVED` |
| Enum mapping | `Location=Overseas, Group=AGENTS, Category=AGENT - OVERSEAS` | `scope=OVERSEAS, partner_group=AGENTS, category=AGENT_OVERSEAS` |

**Verify du lieu PostgreSQL:**
```bash
psql "postgresql://of1-fms:of1-fms@postgres.of1-dev-crm.svc.cluster.local:5432/of1_fms_db" \
  -c "SELECT partner_code, label, scope, partner_group, category, source, storage_state FROM integrated_partner;"
```

### 8. Troubleshooting

**Loi `SnappyOutputStream` ClassNotFoundException:**
- Nguyen nhan: Debezium dung snappy compression nhung FMS thieu snappy-java JAR
- Fix: Copy `snappy-java-1.1.10.5.jar` vao `working/release-fms/server/addons/fms/lib/`
- Hoac: Update Debezium connector `producer.compression.type: none`

**CDC consumer khong nhan event:**
- Check `auto-startup: true` trong addon-fms-config.yaml
- Check `event-consumer-enable: true`
- Check log: `grep "Registered CDC handler" server.log` — phai thay handler duoc dang ky
- Check log: `grep "cdc-consumer" server.log` — phai thay consumer subscribed

**Debezium connector FAILED:**
- Check: `curl .../connectors/mssql-dev-hps-connector/status`
- Restart: `curl -X POST .../connectors/mssql-dev-hps-connector/restart?includeTasks=true`
- Xem config: `curl .../connectors/mssql-dev-hps-connector/config`

**Consumer group bi stuck (offset cu):**
```bash
# Xoa consumer group de reset offset (server phai stop truoc)
# Dung kafka-consumer-groups CLI hoac KafkaAdminClient
```

---

## 2026-03-28: Port BFSOne Sync Pipeline (MSSQL -> Kafka -> PostgreSQL)

### Tong quan

Port va hoan thien pipeline dong bo du lieu tu BFS One (MSSQL legacy) vao PostgreSQL qua Kafka.
Pipeline: `MSSQL (BFS One) -> *SyncLogic (JDBC, chunk 5000, batch 50) -> Kafka -> *SyncEventConsumer -> PostgreSQL`
Toan bo code nam trong `module/transaction` package `of1.fms.module.partner`.

### Part C: Rename BfsOne -> BFSOne (refactor)

- `BfsOneDataConfig` -> `BFSOneDataConfig`
- `BfsOneSyncLogic` -> `TransactionSyncLogic`
- `BfsOneSyncService` -> `BFSOneSyncService`, annotation `@Service("BFSOneSyncService")`
- 8 event file chuyen tu `event/` sang sub-package `event/transaction/` (package `of1.fms.module.partner.event.transaction`)
- `TransactionQueueConfig` cap nhat wildcard import `event.transaction.*`

### Part A: Fix bug ton tai

**Bug 1 — ETD/ETA alias inversion trong SQL**

`TransactionSyncLogic`: ca `TRANSACTION_QUERY` lan `HOUSEBILL_QUERY` co CASE block swap ETD/ETA cho Import records. Sai logic — `LoadingDate` luon la ETD, `ArrivalDate` luon la ETA, khong co dieu kien.

```sql
-- Truoc (sai):
CASE WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate ELSE t.LoadingDate END AS etd,
CASE WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate ELSE t.ArrivalDate END AS eta,

-- Sau (dung):
t.LoadingDate AS etd,
t.ArrivalDate AS eta,
```

**Bug 2 — deleteByTransactionIds dung sai field**

`IntegratedHawbProfitRepository`: JPQL dung `ihp.id` thay vi `ihp.transactionId`, param type `List<Long>` thay vi `List<String>`.
`IntegratedHawbProfitLogic`: doi signature thanh `deleteByTransactionId(ctx, String)` (singular).

**Bug 3 — Thieu HawbProfitSyncEventConsumer**

`TransactionQueueConfig` da register `HawbProfitSyncEventProducer` nhung khong co consumer.
Tao `event/transaction/HawbProfitSyncEventConsumer.java`: upsert flow — delete by transactionId -> insert new.

### Part B: Port domain moi

**ExchangeRate sync**

- `ExchangeRateSyncLogic`: query `CurrencyExchangeRate WHERE Unit='USD' AND ID LIKE 'HCMGIANGNTH_%'`, parse `effectiveDate` tu code suffix (e.g. `JAN012025`), tinh `effectiveTo` bang record ke tiep.
- `ExchangeRateSyncEvent`: `code`, `exchangeRateUSD`, `effectiveDate`, `effectiveTo`
- `ExchangeRateSyncEventProducer` + `ExchangeRateSyncEventConsumer` (two-step upsert: getByCode -> deleteByIds -> insert)
- Kafka topic: `bee-legacy.exchange-rate.sync`

**SettingUnit sync**

- `SettingUnitSyncLogic`: query `UnitContents` (bo qua `IsActive` — khong co field tuong ung trong entity)
- `SettingUnitSyncEvent`: `unitCode`, `unitName`, `unitLocalizedName`, `isoCode`, `description`, `groupName`
- `SettingUnitSyncEventConsumer`: update-in-place (khong delete/re-insert, tranh cascade delete tren `aliases`); resolve `groupName -> SettingUnitGroup.id`, tu dong tao group neu chua co
- Kafka topic: `bee-legacy.setting-unit.sync`

### Cap nhat BFSOneSyncService

- Them `syncExchangeRates(ClientContext)` va `syncSettingUnits(ClientContext)`
- Them lookup exchange rate trong `syncHawbProfits`: tra cuu `exchangeRateUSD` theo `reportDate` truoc khi publish

### Cap nhat TransactionQueueConfig

Tang so bean tu 5 len 10: bo sung `ExchangeRateSyncEventProducer`, `ExchangeRateSyncEventConsumer`, `SettingUnitSyncEventProducer`, `SettingUnitSyncEventConsumer`.

### Build dependency

`module/transaction/build.gradle`: them `api project(":of1-fms-module-settings")` de truy cap `ExchangeRateRepository`, `SettingUnitRepository`, `SettingUnitGroupRepository`.

### ExchangeRateRepository — method moi

```java
@Query("SELECT er FROM ExchangeRate er WHERE er.effectiveDate <= :date ORDER BY er.effectiveDate DESC")
List<ExchangeRate> findLatestByEffectiveDateOnOrBefore(@Param("date") Date date, Pageable pageable);
// Dat ten "OnOrBefore" vi Spring Data "Before" sinh ra strict < thay vi <=
```

### Hotfix — IntegratedPartner.group reserved keyword

`group` la reserved keyword trong PostgreSQL. Hibernate sinh DDL loi khi them column.
Fix: `@Column(name = "group")` -> `@Column(name = "partner_group")` trong `IntegratedPartner.java`.

### RPC Methods (goi qua PlatformClient)

Service name: `"BFSOneSyncService"`

| Method | Params | Return | Mo ta |
|---|---|---|---|
| `syncTransactions` | `ctx` | `int` | Dong bo toan bo transaction (chunk 5000, batch 50) |
| `syncByTransactionIds` | `ctx, transactionIds: List<String>` | `int` | Dong bo housebill + profit cho danh sach transaction ID cu the |
| `syncHousebills` | `ctx, transactionId: String` | `List<HousebillSyncEvent>` | Dong bo housebill cua 1 transaction |
| `syncHawbProfits` | `ctx, transactionId: String, housebills: List<HousebillSyncEvent>` | `int` | Dong bo HAWB profit (phai goi sau syncHousebills) |
| `syncExchangeRates` | `ctx` | `int` | Dong bo ti gia USD tu BFS One |
| `syncSettingUnits` | `ctx` | `int` | Dong bo don vi tu BFS One |

Goi mau:
```java
// Dong bo toan bo transaction
platformClient.internalCall(ctx, "BFSOneSyncService", "syncTransactions", new MapObject());

// Dong bo 1 transactionId cu the (housebill + profit)
platformClient.internalCall(ctx, "BFSOneSyncService", "syncByTransactionIds",
  new MapObject().with("transactionIds", List.of("HCVND0012025XXX")));

// Dong bo ti gia + don vi (thich hop chay dinh ky)
platformClient.internalCall(ctx, "BFSOneSyncService", "syncExchangeRates", new MapObject());
platformClient.internalCall(ctx, "BFSOneSyncService", "syncSettingUnits", new MapObject());
```

---

## 2026-03-24: Cau hinh uu tien Maven Nexus trong Gradle

### Hien trang

Repository resolution order trong `build.gradle` (ap dung cho tat ca subproject):

```groovy
repositories {
  mavenLocal()     // 1st: ~/.m2/repository — local dev cache
  maven {
    url "${nexusUrl}/repository/maven-public/"  // 2nd: Nexus group repo
    allowInsecureProtocol = true
  }
  mavenCentral()   // 3rd: fallback neu Nexus khong co artifact
}
```

`nexusUrl` duoc dinh nghia trong `~/.gradle/gradle.properties` (global, khong commit):

```properties
nexusUrl=http://nexus.of1-dev-egov.svc.cluster.local
nexusUsername=admin
nexusPassword=admin
```

### Nguyen tac hoat dong

Gradle kiem tra repo theo **thu tu khai bao** — repo dau tien tim thay artifact se duoc dung.
Thu tu hien tai: `mavenLocal` > `Nexus` > `mavenCentral`.

### Cac phuong an cau hinh

**PA1 (hien tai): mavenLocal → Nexus → mavenCentral fallback**
- Uu: linh hoat, Nexus khong co van resolve duoc tu Central
- Nhuoc: phu thuoc internet neu Nexus thieu artifact

**PA2: Nexus lam proxy duy nhat (khuyen nghi cho moi truong corporate/offline)**

Xoa `mavenCentral()`, cau hinh Nexus `maven-public` group de proxy mavenCentral.
Loi ich: tat ca artifact di qua Nexus (cache, kiem soat, offline).

**PA3: Nexus truoc ca mavenLocal (it gap)**

Chi dung khi Nexus giu phien ban moi hon local cache.

**PA4: Centralize bang `dependencyResolutionManagement` (Gradle 7+)**

`PREFER_SETTINGS`: settings.gradle repo uu tien hon subproject repo.
`FAIL_ON_PROJECT_REPOS`: ep buoc chi dung repo khai bao o settings (strict nhat).

### Plugin Resolution

Plugin resolve rieng, phai khai bao trong `pluginManagement {}` o `settings.gradle`.

---

## 2026-03-02: Khởi tạo Cấu trúc Module Of1-Tools

### Cấu hình Build System
- Cập nhật `settings.gradle` để đăng ký `module/partner` và dọn dẹp cấu hình không hợp lệ (`module:core:core`).
- Sửa lỗi build do file `build.gradle` của `common` và `core` chứa cú pháp `plugins {}` conflict với thiết lập subprojects ở dự án gốc.

### Scaffolding Khung Module
- Thiết lập sẵn cấu trúc thư mục mã nguồn chuẩn (`src/main/java`) cho các module: `common`, `core`, `transaction`, `partner`.
- Bổ sung `.gitkeep` để đảm bảo các package trống được nhận diện bởi hệ thống theo dõi mã nguồn và được ghi nhận với project root.

### Cập nhật Package
- Đổi cấu trúc thư mục từ `org.example` sang `of1.tools` cho toàn bộ các module.
- Chỉnh sửa `Main.java` sử dụng package `of1.tools` tương ứng.
- Hoàn tất loại bỏ thư mục `org/example`.

Dự án hiện đã build thành công 100% qua lệnh `gradle clean build`.
