# BFSOne Sync Pipeline — Design Spec
Date: 2026-03-28

## Overview

Port and complete the BFSOne (BFS One legacy MSSQL) sync pipeline from the `bee_legacy` Python project into `of1-fms` Java/Spring. The pipeline reads data from MSSQL (BFS One), publishes to Kafka, and consumers save to PostgreSQL.

Pipeline flow:
```
MSSQL (BFS One) → [*SyncLogic — JDBC, chunk 5000, batch 50] → Kafka → [*SyncEventConsumer] → PostgreSQL
```

## Scope

### Part A — Review & fix existing code
Verify and fix existing Java implementation of `IntegratedTransaction`, `IntegratedHousebill`, `IntegratedHawbProfit`.

**Known bug to fix — ETD/ETA column alias inversion in SQL:**
Both `TRANSACTION_QUERY` and `HOUSEBILL_QUERY` in `BfsOneSyncLogic` swap aliases for Import:
```sql
-- WRONG (current):
CASE WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate ELSE t.LoadingDate END AS etd,
CASE WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate ELSE t.ArrivalDate END AS eta,

-- CORRECT (fix):
t.LoadingDate AS etd,
t.ArrivalDate AS eta,
```
`LoadingDate` is always ETD, `ArrivalDate` is always ETA. The CASE swap causes Import `report_date` to use LoadingDate instead of ArrivalDate.

**`HawbProfitSyncEventConsumer` is missing — must be created:**
`TransactionQueueConfig` registers `HawbProfitSyncEventProducer` but no consumer. Create `HawbProfitSyncEventConsumer` in `event/transaction/` and register it.

**Other logic to verify (against Python bee_legacy):**
- Chunked pagination (5000 rows, OFFSET/FETCH)
- Kafka batch publish (50 records/batch)
- `report_date` computation (after fixing aliases above)
- `company_branch_code` extraction: `"HCVND0012025"` → skip 2 chars → `"VND0012025"` → take until first digit → `"VND"`
- Container size string parsing (`"2x40'HC & 1x20'"`)
- Upsert strategy (delete by ID + insert, not merge)
- **Pre-existing bug: `IntegratedHawbProfitRepository.deleteByTransactionIds`** uses wrong field (`ihp.id` instead of `ihp.transactionId`) and wrong param type (`List<Long>` instead of `List<String>`). Fix this before implementing `HawbProfitSyncEventConsumer`.

### Part B — Port new sync domains
- `ExchangeRate` sync: MSSQL `CurrencyExchangeRate` → Kafka → `ExchangeRate` entity (`module/settings`)
- `SettingUnit` sync: MSSQL `UnitContents` → Kafka → `SettingUnit` entity (`module/settings`)

### Part C — Rename BfsOne → BFSOne
Rename all existing classes from `BfsOne*` to `BFSOne*`. Also update the `@Service` annotation string:
`@Service("BfsOneSyncService")` → `@Service("BFSOneSyncService")`

## Module & Package Structure

All new code lives in `module/transaction`, under package `of1.fms.module.partner`.

**Cross-module dependency — add to `module/transaction/build.gradle`:**
```groovy
api project(":of1-fms-module-settings")
```
Required for `ExchangeRateSyncEventConsumer` and `SettingUnitSyncEventConsumer` to access repositories from `module/settings`.

```
bfsone/                              (flat — no sub-packages)
├── BFSOneDataConfig.java            rename from BfsOneDataConfig
├── BFSOneSyncService.java           rename from BfsOneSyncService, delegate to Logic classes
├── TransactionSyncLogic.java        refactor from BfsOneSyncLogic
├── ExchangeRateSyncLogic.java       new
└── SettingUnitSyncLogic.java        new

event/
├── transaction/                     move ALL existing transaction event classes here
│   ├── TransactionSyncEvent.java
│   ├── TransactionSyncEventProducer.java
│   ├── TransactionSyncEventConsumer.java
│   ├── HousebillSyncEvent.java
│   ├── HousebillSyncEventProducer.java
│   ├── HousebillSyncEventConsumer.java
│   ├── HawbProfitSyncEvent.java
│   ├── HawbProfitSyncEventProducer.java
│   └── HawbProfitSyncEventConsumer.java   new — missing, must be created
├── exchangerate/
│   ├── ExchangeRateSyncEvent.java
│   ├── ExchangeRateSyncEventProducer.java
│   └── ExchangeRateSyncEventConsumer.java
├── settingunit/
│   ├── SettingUnitSyncEvent.java
│   ├── SettingUnitSyncEventProducer.java
│   └── SettingUnitSyncEventConsumer.java
└── TransactionQueueConfig.java      update imports + register new beans
```

## Domain Details

### Transaction / Housebill / HawbProfit

**`TransactionSyncLogic`** (refactor from `BFSOneSyncLogic`): same methods, same SQL — only class rename + fix ETD/ETA aliases above.

**Kafka topics:**
- `bee-legacy.transaction.sync`
- `bee-legacy.housebill.sync`
- `bee-legacy.hawb-profit.sync`

**`report_date` logic (after ETD/ETA fix):**
```
Import (typeOfService contains "Imp"): eta ?? etd ?? transactionDate
Export:                                etd ?? eta ?? transactionDate
```

**Profit sync trigger flow (service-orchestrated, NOT consumer-triggered):**
```
BFSOneSyncService.syncHousebills(ctx, transactionId)
  → TransactionSyncLogic.queryHousebills(transactionId) — MSSQL query
  → HousebillSyncEventProducer.send() per housebill
  → returns List<HousebillSyncEvent>

Caller then calls:
BFSOneSyncService.syncHawbProfits(ctx, transactionId, housebills)
  → extract hawbNos from housebills
  → TransactionSyncLogic.queryProfitData(hawbNos) — MSSQL query
  → look up ExchangeRate: ExchangeRateRepository.findLatestByReportDate(reportDate)
      (new repo method: SELECT er FROM ExchangeRate er
       WHERE er.effectiveDate <= :reportDate ORDER BY er.effectiveDate DESC — limit 1)
  → merge housebill context + profit data + exchangeRateUSD
  → HawbProfitSyncEventProducer.send() per record
```

`HousebillSyncEventConsumer` — saves housebill to PostgreSQL only. Does NOT trigger profit sync.

`HawbProfitSyncEventConsumer` (new):
- Deserialize `HawbProfitSyncEvent`
- Delete existing `IntegratedHawbProfit` by `transactionId`
- Insert new records
- Register bean in `TransactionQueueConfig`

**`BFSOneSyncService` public signatures:**
```java
syncTransactions(ClientContext ctx)
syncHousebills(ClientContext ctx, String transactionId)                           // returns List<HousebillSyncEvent>
syncHawbProfits(ClientContext ctx, String transactionId, List<HousebillSyncEvent> housebills)
syncExchangeRates(ClientContext ctx)    // new
syncSettingUnits(ClientContext ctx)     // new
```

---

### ExchangeRate Sync (new)

**Source table:** `CurrencyExchangeRate` (MSSQL)

**Query:**
```sql
SELECT ID, ExtVNDSales
FROM CurrencyExchangeRate
WHERE Unit = 'USD' AND ID LIKE 'HCMGIANGNTH_%'
ORDER BY ID
```

**Transform:**
- `code` = ID field (e.g. `HCMGIANGNTH_JAN012025`)
- `effectiveDate` = parsed from code suffix (`JAN012025` → 2025-01-01) as `java.util.Date`
- `effectiveTo` = effectiveDate of the next record in sorted sequence as `java.util.Date`; null for last record
- `exchangeRateUSD` = ExtVNDSales as `Double`

**Kafka topic:** `bee-legacy.exchange-rate.sync`

**`ExchangeRateSyncEvent` fields** (match entity field names exactly):
```java
String  code
Double  exchangeRateUSD        // uppercase USD — matches ExchangeRate.exchangeRateUSD
Date    effectiveDate
Date    effectiveTo
```

**Consumer upsert strategy** (`ExchangeRateSyncEventConsumer`):
```
ExchangeRate existing = exchangeRateRepo.getByCode(event.getCode())
if existing != null: exchangeRateRepo.deleteByIds(List.of(existing.getId()))
insert new ExchangeRate with event fields + syncedToKafka = new Date()  // syncedToKafka is set by consumer, NOT from event
```
No `deleteByCode` method exists — use the two-step find-then-delete pattern above.

**New repository method needed** (`ExchangeRateRepository`):
```java
// Name uses "OnOrBefore" to match the inclusive <= semantics (avoid Spring Data "Before" which generates <)
@Query("SELECT er FROM ExchangeRate er WHERE er.effectiveDate <= :date ORDER BY er.effectiveDate DESC")
List<ExchangeRate> findLatestByEffectiveDateOnOrBefore(@Param("date") Date date, Pageable pageable);
// usage: findLatestByEffectiveDateOnOrBefore(reportDate, PageRequest.of(0, 1)) → take first result
```

---

### SettingUnit Sync (new)

**Source table:** `UnitContents` (MSSQL)

**Query:**
```sql
SELECT UnitCode, UnitName, LocalizedName, ISOCode, Description, GroupName
FROM UnitContents
```

Note: `IsActive` column exists in Python but has no corresponding field in `SettingUnit` entity — skip it.

**Kafka topic:** `bee-legacy.setting-unit.sync`

**`SettingUnitSyncEvent` fields:**
```java
String  unitCode
String  unitName               // maps to SettingUnit.label
String  unitLocalizedName      // maps to SettingUnit.localizedDescription
String  isoCode                // maps to SettingUnit.isoCode
String  description
String  groupName              // resolve to SettingUnit.groupId via SettingUnitGroup
```

**Group resolution in `SettingUnitSyncEventConsumer`:**
`SettingUnit.groupId` is a non-nullable FK to `SettingUnitGroup`. Consumer must:
1. Find `SettingUnitGroup` where `code = groupName` (exact match, case-sensitive — use `getByCode()`)
2. If not found: create and save a new `SettingUnitGroup` with `code = groupName`, `label = groupName`
3. Use the resulting `groupId` when saving `SettingUnit`

**Upsert strategy** (update in-place to avoid cascade delete on `SettingUnit.aliases`):
```
SettingUnit existing = settingUnitRepo.getByCode(event.getUnitCode())
if existing != null:
  update existing.label, localizedDescription, isoCode, description, groupId
  save existing
else:
  insert new SettingUnit
```

---

## Configuration

**Add to `module/transaction/build.gradle`:**
```groovy
api project(":of1-fms-module-settings")
```

**New application properties:**
```properties
datatp.msa.fms.queue.topic.exchange-rate-sync=bee-legacy.exchange-rate.sync
datatp.msa.fms.queue.topic.setting-unit-sync=bee-legacy.setting-unit.sync
```

**`TransactionQueueConfig` new beans (add to existing):**
```java
@Bean("HawbProfitSyncEventConsumer")
HawbProfitSyncEventConsumer createHawbProfitSyncEventConsumer()

@Bean("ExchangeRateSyncEventProducer")
ExchangeRateSyncEventProducer createExchangeRateSyncEventProducer()

@Bean("ExchangeRateSyncEventConsumer")
ExchangeRateSyncEventConsumer createExchangeRateSyncEventConsumer()

@Bean("SettingUnitSyncEventProducer")
SettingUnitSyncEventProducer createSettingUnitSyncEventProducer()

@Bean("SettingUnitSyncEventConsumer")
SettingUnitSyncEventConsumer createSettingUnitSyncEventConsumer()
```

---

## Reference Files

- **`PYTHON_DEVLOG.md`** (root of of1-fms) — Work log tracking port progress per entity, notes on Java vs Python differences.
- **`PYTHON_CLAUDE.md`** (root of of1-fms) — AI instructions: Python→Java class mapping, special logic notes, reference path to `bee_legacy`.

## Python Reference

Source: `/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python/bee_legacy`

| Python file | Java equivalent |
|---|---|
| `service/hawb/integrated_transaction_service.py` | `TransactionSyncLogic` + `BFSOneSyncService` |
| `service/hawb/integrated_hawb_profit_service.py` | `TransactionSyncLogic.queryProfitData()` |
| `service/exchange_rate_service.py` | `ExchangeRateSyncLogic` |
| `service/settings_unit_service.py` | `SettingUnitSyncLogic` |
| `db/bfsone_config.py` | `BFSOneDataConfig` |
