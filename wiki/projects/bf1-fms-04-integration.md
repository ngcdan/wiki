---
title: "FMS 04 - Integration Pipeline"
tags: [bf1, fms]
---

# Integration Pipeline (CDC + Batch Sync)

Sync data from BF1 (MSSQL) to FMS (PostgreSQL) via Kafka. Two pipelines run concurrently — CDC for realtime changes, Batch Sync for periodic reference data.

See also: [[bf1-fms-03-data-model]] · [[bf1-fms-mapping-readme]]

---

## 1. Architecture

```
BF1 MSSQL (BEE_DB)
     │
     ├── Debezium CDC ──► Kafka (cdc-{env}-hps.*) ──► CDCListener ──► CDCEventHandler ──► Postgres (FMS)
     │
     └── SyncLogic (CronJob) ──► Kafka (setting-* / transaction-*) ──► Consumer ──► Postgres (FMS)
```

**Infrastructure:**
- **BF1 Source:** `of1.beelogistics.com:34541` / `BEE_DB` (credentials in TenantRegistry)
- **FMS Target:** `postgres.of1-dev-crm.svc.cluster.local:5432` / `of1_fms_db`
- **Kafka config:** `addon-fms-config.yaml` → `datatp.msa.fms.queue.topic.*`
- **Sync API:** `POST {host}/platform/plugin/fms/rest/v1.0.0/rpc/internal/call`

**Pipeline Entry Point:**
```json
{
  "component": "BFSOneSyncService",
  "endpoint": "<endpoint>",
  "userParams": { "sourceDb": "BEE_VN" }
}
```

---

## 2. CDC vs Batch Sync — Decision Matrix

| Criterion | CDC (Realtime) | Batch Sync (Periodic) |
|-----------|----------------|-----------------------|
| Latency | Seconds | 30 min |
| Source | Debezium connector required | Any MSSQL table/view |
| Mapping complexity | 1:1 table mapping | Multi-table JOIN/aggregate |
| Error handling | Retry 3× + DLQ | Log + skip |
| Concurrency | Configurable (default 5) | 1 thread |
| Use case | Transactions, HouseBill, Containers, Rates | Reference/master data |

---

## 3. CDC Pipeline (Realtime)

### 3.1 Flow

```
Debezium (MSSQL log)
   │
   ▼
Kafka topic: cdc-{env}-hps.{schema}.{table}
   │
   ▼
CDCListener (@KafkaListener pattern: cdc-{env}-hps.*)
   │
   ▼
CDCEventHandlerRegistry (routes by getTableName())
   │
   ▼
CDCEventHandler.handle{Create|Update|Delete|Snapshot}()
   │
   ▼
Repository.save() → PostgreSQL (of1_fms_*)
```

### 3.2 Key Components

| Component | Role |
|-----------|------|
| **CDCEvent** | Debezium JSON model: `before`, `after`, `source`, `op` (c/u/d/r), `ts_ms` |
| **CDCEventHandler** | Interface: `getTableName()`, `handleCreate/Update/Delete/Snapshot()` |
| **CDCListener** | `@KafkaListener` on `cdc-{env}-hps.*`, manual ACK |
| **CDCEventHandlerRegistry** | Scans all handler beans, routes by table name (1:N handlers supported) |
| **EntityLockManager** | `ConcurrentHashMap` lock keys (e.g. `"transaction:BIHCM008238/25"`) for thread safety |
| **CDCSyncMonitorService** | Tracks `processedCount`, `errorCount`, `lastOffset`, `lastSyncTime`, MD5 checksum in `of1_fms_cdc_sync_status` |
| **CDCMapperUtils** | `parseLong/Integer/Double/BigDecimal/Boolean`, `trimString`, `toTimestamp` |
| **CDCKafkaConfig** | Consumer factory, retry policy (`DefaultErrorHandler + FixedBackOff`), DLQ (`DeadLetterPublishingRecoverer`) |

### 3.3 Error Handling

Retry 3x with 1000ms backoff → publish to `{topic}.DLQ`.

### 3.4 Registered Handlers

| Handler | Source Table | Target |
|---------|--------------|--------|
| `TransactionsCDCHandler` | `dbo.Transactions` | `integrated_transaction` + `of1_fms_transactions` + parses `ContainerSize` → `of1_fms_container` + rebuilds `of1_fms_transport_plan` |
| `TransactionDetailsCDCHandler` | `dbo.TransactionDetails` | `of1_fms_house_bill` (skeleton + client/saleman + desc/packaging) |
| `HAWBCDCHandler` | `dbo.HAWB` | `integrated_housebill` + `of1_fms_house_bill` (cargo weights, container, agent) + auto-upsert `of1_fms_cargo` |
| `HAWBDETAILSCDCHandler` | `dbo.HAWBDETAILS` | `of1_fms_air_house_bill_detail` / `of1_fms_sea_house_bill_detail` |
| `ContainerListOnHBLCDCHandler` | `dbo.ContainerListOnHBL` | `of1_fms_container` (container_no + seal_no line items) |
| `SellingRateCDCHandler` | `dbo.SellingRate` | `of1_fms_house_bill_invoice` + `_item` (Debit) |
| `BuyingRateWithHBLCDCHandler` | `dbo.BuyingRateWithHBL` | `of1_fms_house_bill_invoice` + `_item` (Credit) |
| `OtherChargeDetailCDCHandler` | `dbo.OtherChargeDetail` | `of1_fms_house_bill_invoice` + `_item` (On_Behalf) |

Field-level mapping: see [[bf1-fms-mapping-readme]].

---

## 4. Batch Sync Pipeline (Periodic)

### 4.1 Flow

```
CronJob (every 30 min — prod only)
   │
   ▼
FMSDaoService (Groovy SQL query on MSSQL)
   │
   ▼
BatchSyncService (chunks 5000, batches 50)
   │
   ▼
Producer → Kafka topic → Consumer
   │
   ▼
Logic/Repository.save() → PostgreSQL
```

### 4.2 Key Components

| Component | Role |
|-----------|------|
| **CronJob** | Extends `net.datatp.module.bot.cron.CronJob`, frequency `EVERY_30_MINUTE` (prod) or `NONE` (dev) |
| **FMSDaoService** | Base class: `searchBF1DbRecords(ctx, sourceDb, scriptPath, queryName, sqlParams)` |
| **BatchSyncService** | `@Service("BFSOneSyncService")` orchestrator. CHUNK_SIZE=5000, BATCH_SIZE=50 |
| **SyncEvent DTO** | `@Data` Lombok class carrying transformed data |
| **Producer** | `KafkaTemplate<String,String>`, wraps in `KafkaMessage(ctx, event)`, JSON serialization |
| **Consumer** | `@KafkaListener` (manual topic/groupId/autoStartup), saves to DB |

### 4.3 Sync Endpoints

| Endpoint | BF1 Table | Records | FMS Table | Entity | Cron |
|----------|-----------|---------|-----------|--------|------|
| `syncBanks` | `lst_Bank` | ~203 | `settings_bank` | `SettingBank` | 30m |
| `syncIndustries` | `lst_Industries` | ~23 | `settings_industry` | `SettingIndustry` | 30m |
| `syncPartnerSources` | `lst_Source` | ~30 | `settings_partner_source` | `SettingPartnerSource` | 30m |
| `syncCommodities` | `Commodity` | ~96 | `settings_commodity` | `SettingCommodity` | 30m |
| `syncNameFeeDescriptions` | `NameFeeDescription` | ~1138 | `settings_name_fee_desc` | `NameFeeDescription` | 30m |
| `syncCustomLists` | `CustomsList` | varies | `settings_custom_list` | `SettingCustomList` | 30m |
| `syncSettingUnits` | `UnitContents` | varies | `settings_unit` | `SettingUnit` | 30m |
| `syncExchangeRates` | `CurrencyExchangeRate` | varies | `settings_exchange_rate` | `ExchangeRate` | 30m |
| `syncUserRoles` | `UserInfos` | ~1095 | `settings_user_roles` | `SettingsUserRole` | 30m |
| `syncTransactions` | `Transactions` | varies | `of1_fms_integrated_transaction` | `IntegratedTransaction` | 30m |
| `syncHousebills` | `TransactionDetails` + joins | varies | `of1_fms_integrated_housebill` | `IntegratedHousebill` | per txn |
| `syncHawbProfits` | `BuyingRateWithHBL`, `SellingRate`, `ProfitShares` | varies | `of1_fms_integrated_hawb_profit` | `IntegratedHawbProfit` | per txn |

### 4.4 Code Structure

```
module/integration/src/main/java/of1/fms/module/integration/batch/
  groovy/BFSOneSyncSql.groovy      # All BF1 SQL queries
  config/SyncQueueConfig.java      # Kafka bean registration
  BatchSyncService.java            # RPC endpoints orchestrator
  bank/                            # one subfolder per pipeline
  industry/
  partnersource/
  commodity/
  namefeedesc/
  customlist/
  settingunit/
  exchangerate/
  userrole/
  transaction/                     # Transaction + Housebill + HAWB Profit
```

Each pipeline folder contains: `*SyncEvent.java`, `*SyncLogic.java`, `*SyncEventProducer.java`, `*SyncEventConsumer.java`, `BFSOneSync*CronJob.java`.

### 4.5 Error Handling

Log + skip on error (no retry / no DLQ).

---

## 5. Configuration Properties

| Property | Default | Description |
|----------|---------|-------------|
| `spring.kafka.bootstrap-servers` | — | Kafka broker address |
| `datatp.msa.fms.queue.event-producer-enable` | `false` | Enable Batch Sync producers |
| `datatp.msa.fms.queue.event-consumer-enable` | `false` | Enable Batch Sync consumers + CDC listener |
| `datatp.msa.fms.queue.cdc.topics` | `cdc-dev-hps.*` | CDC topic pattern |
| `datatp.msa.fms.queue.cdc.consumer-group` | `fms-cdc-consumer` | CDC consumer group |
| `datatp.msa.fms.queue.cdc.concurrency` | `5` | CDC listener threads |
| `datatp.msa.fms.queue.cdc.auto-startup` | `false` | Auto-start listener |
| `datatp.msa.fms.queue.cdc.retry.max-attempts` | `3` | Retry attempts before DLQ |
| `datatp.msa.fms.queue.cdc.retry.backoff-interval` | `1000` | Backoff (ms) |
| `datatp.msa.fms.queue.cdc.dlq.enabled` | `true` | Enable DLQ |
| `datatp.msa.fms.queue.cdc.dlq.topic-suffix` | `.DLQ` | DLQ topic suffix |

---

## 6. Monitoring & Troubleshooting

### 6.1 CDC Troubleshooting

**Handler not invoked:**
- Verify `getTableName()` returns correct MSSQL table name (case-sensitive)
- Check startup log: `"Registered CDC handler: {TableName} -> {HandlerClass}"`
- Confirm Debezium topic exists and matches `cdc-{env}-hps.*`
- Verify `auto-startup` and `event-consumer-enable` are `true`

**Duplicate data:**
- CDC uses MD5 checksum tracking in `of1_fms_cdc_sync_status`
- Single table can have multiple handlers (1:N) — check for duplicate registrations
- Verify `EntityLockManager` uses correct lock keys

**Messages in DLQ:**
- Check `{topic}.DLQ` for failed messages
- Review `lastError` in `of1_fms_cdc_sync_status`
- Replay: republish message from DLQ to original topic
- Tune `max-attempts` (default 3), `backoff-interval` (default 1000ms)

**Slow performance:**
- Increase `cdc.concurrency` (default 5)
- Check `max.partition.fetch.bytes` (default 1MB)
- Monitor `[CDC_PROCESSED] ... duration=Xms` logs

### 6.2 Batch Sync Troubleshooting

**CronJob not running:**
- Dev env uses `CronJobFrequency.NONE` (disabled by design)
- Verify `event-producer-enable` + `event-consumer-enable` flags
- Confirm CronJob class has `@Component`

**Consumer not receiving:**
- Verify consumer group, topic, `autoStartup` match
- Check `SyncQueueConfig` has `@Bean` for consumer
- Confirm topic name in `@KafkaListener` matches Producer

**MSSQL connection errors:**
- Verify `TenantRegistry` has entry for `sourceDb` (e.g. `BEE_VN`, `HPS`)
- Check network connectivity

**Data mismatch:**
- Compare SQL directly on MSSQL vs Postgres
- Verify `CHUNK_SIZE=5000`, `BATCH_SIZE=50`
- Review field aliases in SyncLogic

### 6.3 Useful Queries

**PostgreSQL:**
```sql
-- Full CDC sync status
SELECT table_name, processed_count, error_count, last_error, last_sync_time
FROM of1_fms_cdc_sync_status ORDER BY table_name;

-- Tables with errors
SELECT table_name, error_count, last_error
FROM of1_fms_cdc_sync_status WHERE error_count > 0;

-- Last sync time
SELECT table_name, last_sync_time, processed_count
FROM of1_fms_cdc_sync_status ORDER BY last_sync_time DESC;
```

**Kafka CLI:**
```bash
# CDC consumer group lag
kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group fms-cdc-consumer-<env>

# Batch Sync consumer lag
kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group fms-setting-unit-consumer-group

# List CDC topics
kafka-topics.sh --bootstrap-server <broker> --list | grep "cdc-"

# Read DLQ
kafka-console-consumer.sh --bootstrap-server <broker> --topic cdc-<env>-hps.YourTable.DLQ --from-beginning
```
