---
title: "FMS Designs & Plans"
tags: [bf1, fms, design, raw]
---


## FMS Transaction Type — Design Spec


**Date**: 2026-04-08
**Author**: brainstormed with Claude
**Status**: Draft — pending review
**Scope**: Tạo 2 bảng `of1_fms_transaction_type` và `of1_fms_transaction_type_sequence` cho FMS, thay thế/bổ sung enum `TypeOfService` hardcode, port từ bảng `TransactionType` bên MSSQL (HPS_TEST_DB).

---

## 1. Motivation

Enum `of1.fms.core.common.TypeOfService` hiện có 11 values được hardcode trong code. Bên MSSQL (`HPS_TEST_DB.dbo.TransactionType`, 18 cột, 13 rows) lưu metadata + cấu hình sinh document number + lock days per-tenant. FMS hiện:

- Không có nơi lưu metadata nghiệp vụ (description, nhóm hiển thị).
- Không có cơ chế sinh document number theo format tenant riêng.
- Không có cấu hình lock days động theo tenant.

Cần port sang FMS để:
- Có thể admin cấu hình qua DB (không cần redeploy).
- Giữ type-safety của Java enum cho code path đang dùng.
- Map 1-1 với MSSQL cho flow sync/migration.

## 2. Source reference (MSSQL)

Schema bảng `dbo.TransactionType` (HPS_TEST_DB):

| # | Column | Type | Null | Default |
|---|---|---|---|---|
| 1 | `IDTransType` | nvarchar(50) | NO | — |
| 2 | `Description` | nvarchar(150) | YES | — |
| 3 | `Request` | bit | NO | 0 |
| 4 | `Export` | bit | NO | 0 |
| 5 | `RateRequired` | bit | NO | 0 |
| 6 | `Sign` | nvarchar(50) | YES | — |
| 7 | `sMonth` | nvarchar(50) | YES | — |
| 8 | `No` | nvarchar(50) | YES | — |
| 9 | `Ys` | nvarchar(50) | YES | — |
| 10 | `sYear` | nvarchar(50) | YES | — |
| 11 | `Increment` | nvarchar(50) | YES | — |
| 12 | `IDResetOn` | int | YES | 0 |
| 13 | `NoDaysLock` | int | YES | 0 |
| 14 | `DayofLogisticsLock` | int | YES | 0 |
| 15 | `LockAgainAfterUnlock` | int | YES | 0 |
| 16 | `ApproveManager` | nvarchar(50) | YES | — |
| 17 | `MngAPP` | bit | YES | 0 |
| 18 | `TypeList` | nvarchar(1000) | YES | — |

13 rows trong HPS_TEST_DB: `AirExpTransactions`, `AirImpTransactions`, `CustomsLogistics`, `ExpressTransactions`, `InlandTrucking`, `ProjectLogistics`, `SeaExpTransactions_CSL/FCL/LCL`, `SeaImpTransactions_CSL/FCL/LCL`, `WarehouseService`.

## 3. Design decisions

| # | Decision | Chosen | Rationale |
|---|---|---|---|
| 1 | Schema shape | **Split 2 tables**: global metadata + per-company sequence config | Tách sạch concerns "loại giao dịch là gì" vs "tenant này cấu hình ra sao" |
| 2 | Enum vs DB source of truth | **Hybrid**: enum ở code, DB bắt buộc đồng bộ (startup validator) | Giữ type-safety Java + cho phép admin configure metadata qua DB |
| 3 | Tenant scope | Global metadata + per-company override | Định nghĩa nghiệp vụ không đổi theo tenant; config sinh số/lock là riêng |
| 4 | Columns bỏ bớt | `is_export`, `rate_required`, `sort_order`, `active`, `approve_manager`, `mng_app_enabled` | Không dùng trong flow FMS hiện tại |
| 5 | Column gộp | `sMonth + No + Ys + sYear + Increment` → `number_format` (template) | Dễ đọc hơn, 1 cột thay vì 5 |
| 6 | DB engine | PostgreSQL (đã xác nhận FMS dùng Postgres) | — |
| 7 | Enum extension | **Thêm 4 enum values** để cover toàn bộ MSSQL | Tránh silent-skip trong import flow |
| 8 | MSSQL import | Tách riêng khỏi Liquibase, làm service/CLI | Giữ migration deterministic, import data là bước runtime |
| 9 | Transaction entity | Không đổi — giữ `@Enumerated(EnumType.STRING)` | Non-invasive, không đụng TransactionSql |

### 3.1. Enum expansion

Thêm 4 values vào `TypeOfService`:

| New enum | MSSQL code | Description | TypeList |
|---|---|---|---|
| `EXPRESS` | `ExpressTransactions` | Express | — |
| `PROJECT_LOGISTICS` | `ProjectLogistics` | Projects | — |
| `SEA_EXPORT_CSL` | `SeaExpTransactions_CSL` | Export (Consol) | Sea Export |
| `SEA_IMPORT_CSL` | `SeaImpTransactions_CSL` | Import (Consol) | Sea Import |

Cập nhật `TypeOfService.resolve()` switch để map 4 MSSQL codes mới.

Tổng sau khi mở rộng: **15 values** (11 cũ + 4 mới).

## 4. Schema

### 4.1. `of1_fms_transaction_type` (global metadata)

```sql
CREATE TABLE IF NOT EXISTS of1_fms_transaction_type (
    id_trans_type       VARCHAR(50)  PRIMARY KEY,
    description         VARCHAR(255) NOT NULL,
    type_list           VARCHAR(255) NOT NULL,
    legacy_mssql_code   VARCHAR(255),
    storage_state       VARCHAR(255),
    version             BIGINT,
    created_by          VARCHAR(255),
    created_time        TIMESTAMP(6),
    modified_by         VARCHAR(255),
    modified_time       TIMESTAMP(6)
);

CREATE INDEX IF NOT EXISTS of1_fms_transaction_type_legacy_idx
    ON of1_fms_transaction_type (legacy_mssql_code);
```

### 4.2. `of1_fms_transaction_type_sequence` (per-company)

```sql
CREATE TABLE IF NOT EXISTS of1_fms_transaction_type_sequence (
    id                       BIGSERIAL    PRIMARY KEY,
    company_id               BIGINT       NOT NULL,
    id_trans_type            VARCHAR(50)  NOT NULL,
    sign_prefix              VARCHAR(255),
    number_format            VARCHAR(255),
    reset_period_days        INTEGER      NOT NULL DEFAULT 365,
    current_sequence         INTEGER      NOT NULL DEFAULT 0,
    last_reset_date          DATE,
    no_days_lock             INTEGER      NOT NULL DEFAULT 0,
    day_of_logistics_lock    INTEGER      NOT NULL DEFAULT 0,
    lock_again_after_unlock  INTEGER      NOT NULL DEFAULT 0,
    storage_state            VARCHAR(255),
    version                  BIGINT,
    created_by               VARCHAR(255),
    created_time             TIMESTAMP(6),
    modified_by              VARCHAR(255),
    modified_time            TIMESTAMP(6),
    CONSTRAINT of1_fms_trans_type_seq_company_type_uk
        UNIQUE (company_id, id_trans_type),
    CONSTRAINT of1_fms_trans_type_seq_type_fk
        FOREIGN KEY (id_trans_type) REFERENCES of1_fms_transaction_type (id_trans_type)
);

CREATE INDEX IF NOT EXISTS of1_fms_trans_type_seq_company_idx
    ON of1_fms_transaction_type_sequence (company_id);
```

### 4.3. Seed data (15 rows, tương ứng 15 enum values sau khi mở rộng)

```sql
INSERT INTO of1_fms_transaction_type (id_trans_type, description, type_list, legacy_mssql_code) VALUES
    ('AIR_EXPORT',         'Export (Air)',       'Air Export', 'AirExpTransactions'),
    ('AIR_IMPORT',         'Import (Air)',       'Air Import', 'AirImpTransactions'),
    ('SEA_EXPORT_FCL',     'Export (Sea FCL)',   'Sea Export', 'SeaExpTransactions_FCL'),
    ('SEA_EXPORT_LCL',     'Export (Sea LCL)',   'Sea Export', 'SeaExpTransactions_LCL'),
    ('SEA_EXPORT_CSL',     'Export (Consol)',    'Sea Export', 'SeaExpTransactions_CSL'),
    ('SEA_IMPORT_FCL',     'Import (Sea FCL)',   'Sea Import', 'SeaImpTransactions_FCL'),
    ('SEA_IMPORT_LCL',     'Import (Sea LCL)',   'Sea Import', 'SeaImpTransactions_LCL'),
    ('SEA_IMPORT_CSL',     'Import (Consol)',    'Sea Import', 'SeaImpTransactions_CSL'),
    ('CUSTOMS_LOGISTICS',  'Logistics',          'Logistics',  'CustomsLogistics'),
    ('INLAND_TRUCKING',    'Inland Trucking',    'Logistics',  'InlandTrucking'),
    ('CROSS_BORDER',       'Cross Border',       'Logistics',  'LogisticsCrossBorder'),
    ('ROUND_USE_TRUCKING', 'Round Use Trucking', 'Logistics',  'RoundUseTrucking'),
    ('WAREHOUSE',          'Warehouse Service',  'Logistics',  'WarehouseService'),
    ('EXPRESS',            'Express',            'Logistics',  'ExpressTransactions'),
    ('PROJECT_LOGISTICS',  'Projects',           'Logistics',  'ProjectLogistics')
ON CONFLICT (id_trans_type) DO NOTHING;
```

## 5. Java code changes

### 5.1. Enum extension — `of1.fms.core.common.TypeOfService`

Thêm 4 values + cập nhật switch trong `resolve()`:

```java
EXPRESS,
PROJECT_LOGISTICS,
SEA_EXPORT_CSL,
SEA_IMPORT_CSL,
// resolve() switch:
case "ExpressTransactions"      -> EXPRESS;
case "ProjectLogistics"         -> PROJECT_LOGISTICS;
case "SeaExpTransactions_CSL"   -> SEA_EXPORT_CSL;
case "SeaImpTransactions_CSL"   -> SEA_IMPORT_CSL;
```

### 5.2. Entity classes

**Path**: `module/transaction/src/main/java/of1/fms/module/transaction/entity/`

- `TransactionType extends PersistableEntity<String>` — PK string = enum name. Kiểm tra `Persistable<PK>` xem `id` column có thể override tên thành `id_trans_type` qua `@AttributeOverride`, nếu không khả thi thì không extend base class mà tự khai báo audit fields.
- `TransactionTypeSequence extends CompanyEntity` — dùng sẵn `company_id` + audit fields từ base.

### 5.3. Repository

**Path**: `module/transaction/src/main/java/of1/fms/module/transaction/repository/`

- `TransactionTypeRepository extends JpaRepository<TransactionType, String>`
  - `findByLegacyMssqlCode(String)`
- `TransactionTypeSequenceRepository extends JpaRepository<TransactionTypeSequence, Long>`
  - `findByCompanyIdAndIdTransType(Long, String)` với `@Lock(PESSIMISTIC_WRITE)` cho path sinh số
  - `findByCompanyId(Long)`

### 5.4. Service — `TransactionTypeService`

**Path**: `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java`

Responsibilities:

- `get(TypeOfService)` — lookup metadata (cache ConcurrentHashMap, load lúc startup)
- `getAll()` — list cho UI dropdown
- `getOrCreateSequence(ctx, companyId, type)` — lazy create row với default format nếu chưa tồn tại
- `@Transactional generateNextNumber(ctx, companyId, type)` — logic sinh số (xem 5.5)
- `@PostConstruct validateEnumSync()` — fail-fast nếu enum ↔ DB lệch

### 5.5. Document number generator

**Template format**: `{SIGN}{YY}{MM}{###}` (ví dụ `HAEHAN2604001`)

Placeholders supported:

| Token | Value |
|---|---|
| `{SIGN}` | `sign_prefix` (vd `HAEHAN`) |
| `{YY}` | 2 digit năm |
| `{YYYY}` | 4 digit năm |
| `{MM}` | 2 digit tháng |
| `{###}`, `{####}`, … | Sequence zero-padded, độ dài = số `#` |

**Flow**:

```
@Transactional
generateNextNumber(ctx, companyId, type):
  seq = repo.findByCompanyIdAndIdTransType(companyId, type.name())  // PESSIMISTIC_WRITE
  if seq == null:
    seq = createDefaultSequence(companyId, type)

  today = LocalDate.now()
  if shouldReset(seq, today):   // (today - last_reset_date) >= reset_period_days
    seq.currentSequence = 0
    seq.lastResetDate = today

  seq.currentSequence++
  repo.save(seq)

  return formatNumber(seq.numberFormat, seq.signPrefix, today, seq.currentSequence)
```

**Race condition**: `PESSIMISTIC_WRITE` row-level lock ngăn 2 transaction cùng tăng counter.

**Default fallback** khi row chưa tồn tại: format `{SIGN}{YY}{MM}{###}`, `sign_prefix` = hardcoded map theo enum (copy từ MSSQL HPS data: `AIR_EXPORT` → `HAEHAN`, `SEA_EXPORT_*` → `HSEHAN`, …). Các tenant khác HPS sẽ import config riêng (5.7).

### 5.6. Startup validator

```java
@PostConstruct
public void validateEnumSync() {
  Set<String> dbIds = typeRepo.findAll().stream()
      .map(TransactionType::getIdTransType).collect(toSet());
  Set<String> enumIds = Arrays.stream(TypeOfService.values())
      .map(Enum::name).collect(toSet());
  if (!dbIds.equals(enumIds)) {
    throw new IllegalStateException(
      "TransactionType table out of sync with TypeOfService enum. " +
      "Missing in DB: " + Sets.difference(enumIds, dbIds) +
      ", extra in DB: " + Sets.difference(dbIds, enumIds));
  }
}
```

### 5.7. MSSQL import (tách riêng, không trong Liquibase)

**Path**: `module/integration/src/main/java/of1/fms/module/integration/batch/transactiontype/`

- `TransactionTypeImportLogic` — dùng `FMSDaoService.getBFSOneDataSource(ctx, sourceDb)` query MSSQL `TransactionType`
- `TransactionTypeImportEvent` — Kafka event trigger (theo pattern `TransactionSyncEvent` hiện có)

**Import flow**:

```
for each tenant in TenantRegistry:
  companyId = resolveCompanyId(tenantCode)
  sourceDb  = TenantRegistry.getDatabaseSource(tenantCode)
  mssqlRows = mssqlQuery("SELECT * FROM TransactionType")
  for row in mssqlRows:
    enumVal = TypeOfService.resolve(row.IDTransType)
    if enumVal == null: log.warn("skip unknown type {}", row.IDTransType); continue
    numberFormat = buildFormat(row.Sign, row.sYear, row.sMonth, row.No, row.Increment)
    upsert(companyId, enumVal.name(), {
      signPrefix: row.Sign,
      numberFormat: numberFormat,
      resetPeriodDays: row.IDResetOn,
      noDaysLock: row.NoDaysLock,
      dayOfLogisticsLock: row.DayofLogisticsLock,
      lockAgainAfterUnlock: row.LockAgainAfterUnlock,
    })
```

**Trigger**: Kafka event admin-initiated, không auto.

## 6. Liquibase changesets

**File**: `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql` (append vào cuối)

Changesets tiếp theo (cuối hiện tại là `fms:21`):

- `fms:22-create-transaction-type` — CREATE TABLE `of1_fms_transaction_type` + index
- `fms:23-seed-transaction-type` — INSERT 15 rows
- `fms:24-create-transaction-type-sequence` — CREATE TABLE `of1_fms_transaction_type_sequence` + unique + FK + index

Tất cả dùng `CREATE TABLE IF NOT EXISTS` / `ON CONFLICT DO NOTHING` để idempotent.

## 7. Non-goals

- **Không** migrate `Transaction.typeOfService` column sang FK (giữ `@Enumerated(EnumType.STRING)`).
- **Không** sửa `TransactionSql.groovy` hoặc `UITransactionList.tsx` — đây là scope riêng.
- **Không** tự động chạy MSSQL import khi deploy — phải admin trigger.
- **Không** build UI quản lý `transaction_type`/`sequence` trong scope này — có thể làm ở spec sau.
- **Không** thay đổi logic lock transaction hiện tại dựa trên `no_days_lock` — field được thêm vào DB nhưng logic dùng field này là scope tương lai.

## 8. Open items / risks

1. **Override PK column name cho `TransactionType`**: base class `Persistable<PK>` có thể đã khai báo `id` column. Cần verify khả năng dùng `@AttributeOverride(name = "id", column = @Column(name = "id_trans_type"))` ở subclass. Nếu không làm được, fallback: không extend base, tự khai báo audit fields tay.
2. **`company_id` resolution**: Import flow cần map `tenantCode` → `companyId`. Cần check repo xem có sẵn resolver chưa (có thể query `company` table theo code).
3. **Default `sign_prefix` hardcoded** trong service: chỉ đúng cho tenant HPS. Các tenant khác cần import config riêng trước khi sinh số thật, nếu không sẽ tạo số trùng prefix.
4. **Not tested against concurrent load**: phải có test integration cho `generateNextNumber` với concurrent calls để verify row-lock.

## 9. Test plan (high level)

- **Unit**: `formatNumber()` với các format variants (`{YY}`, `{YYYY}`, `{###}`, `{####}`)
- **Unit**: `shouldReset()` logic với các giá trị `reset_period_days` và `last_reset_date`
- **Unit**: `validateEnumSync()` happy path + mismatch cases
- **Integration**: `generateNextNumber()` concurrent — 100 threads cùng sinh, assert không trùng + counter đúng
- **Integration**: Liquibase migration apply sạch trên empty DB + re-run idempotent
- **Integration**: MSSQL import từ HPS_TEST_DB seed → verify 13 rows transform đúng

## 10. Rollout

1. Apply Liquibase changesets (tạo bảng + seed 15 rows).
2. Deploy code với enum mở rộng + service + startup validator (fail-fast nếu seed thiếu).
3. Admin trigger MSSQL import cho từng tenant đã có MSSQL source.
4. Các tenant chưa có MSSQL sẽ dùng default format đến khi được cấu hình qua UI admin (scope sau).

---

## FMS Transaction Type Implementation Plan


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo 2 bảng `of1_fms_transaction_type` (global metadata, 15 seed rows) + `of1_fms_transaction_type_sequence` (per-company doc number + lock config) cho FMS, mở rộng enum `TypeOfService` thêm 4 values, và service sinh document number có row-lock.

**Architecture:** Hybrid — enum Java là source-of-truth cho code, bảng DB lưu metadata + cấu hình per-company. Startup validator đảm bảo đồng bộ. MSSQL import tách riêng khỏi Liquibase. Không đụng `Transaction.typeOfService` column hiện tại.

**Tech Stack:** Java 17+, Spring Boot, JPA/Hibernate, PostgreSQL, Liquibase (formatted SQL), JUnit 5, Mockito, Testcontainers.

**Spec reference:** `/Users/nqcdan/dev/wiki/wiki/daily/260408-fms-transaction-type.md`

---

## File Structure

### Files to create

| Path | Responsibility |
|---|---|
| `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java` | Global metadata entity (standalone — không extend PersistableEntity vì PK là String không auto-generate) |
| `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java` | Per-company config entity, extends `CompanyEntity` |
| `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java` | JpaRepository<TransactionType, String> |
| `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java` | JpaRepository với pessimistic lock query |
| `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java` | Service: get metadata, generate next number, startup sync validator |
| `module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java` | Pure util — format `{SIGN}{YY}{MM}{###}` template → string |
| `module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java` | Unit test formatter |
| `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java` | Unit test service logic (mock repositories) |
| `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java` | Integration test: concurrent `generateNextNumber` không sinh trùng |

### Files to modify

| Path | Change |
|---|---|
| `module/core/src/main/java/of1/fms/core/common/TypeOfService.java` | Thêm 4 enum values + 4 switch cases trong `resolve()` |
| `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql` | Append 3 changesets (`fms:22`, `fms:23`, `fms:24`) |

---

## Task 1: Mở rộng enum `TypeOfService`

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/common/TypeOfService.java`

- [ ] **Step 1.1: Thêm 4 enum values**

Sửa block enum (sau `WAREHOUSE`, trước dấu `;`):

```java
public enum TypeOfService {
  AIR_EXPORT,
  AIR_IMPORT,
  SEA_EXPORT_FCL,
  SEA_EXPORT_LCL,
  SEA_EXPORT_CSL,
  SEA_IMPORT_FCL,
  SEA_IMPORT_LCL,
  SEA_IMPORT_CSL,
  CUSTOMS_LOGISTICS,
  INLAND_TRUCKING,
  CROSS_BORDER,
  ROUND_USE_TRUCKING,
  WAREHOUSE,
  EXPRESS,
  PROJECT_LOGISTICS;
  ...
}
```

- [ ] **Step 1.2: Thêm 4 switch cases vào `resolve()`**

```java
case "SeaExpTransactions_CSL"  -> SEA_EXPORT_CSL;
case "SeaImpTransactions_CSL"  -> SEA_IMPORT_CSL;
case "ExpressTransactions"     -> EXPRESS;
case "ProjectLogistics"        -> PROJECT_LOGISTICS;
```

Đặt chúng theo thứ tự logic cùng nhóm (CSL cạnh FCL/LCL, EXPRESS / PROJECT_LOGISTICS cuối).

- [ ] **Step 1.3: Build module core**

Run: `./gradlew :module:core:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 1.4: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/common/TypeOfService.java
git commit -m "feat(core): extend TypeOfService with EXPRESS, PROJECT_LOGISTICS, SEA_*_CSL"
```

---

## Task 2: Liquibase changeset — tạo 2 bảng + seed

**Files:**
- Modify: `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql`

- [ ] **Step 2.1: Append changeset fms:22 (create transaction_type)**

Append vào cuối file:

```sql
--changeset fms:22-create-transaction-type labels:schema-update context:dev,beta,prod
--comment: Tạo bảng of1_fms_transaction_type (global metadata) thay thế enum TypeOfService hardcode
CREATE TABLE IF NOT EXISTS of1_fms_transaction_type (
    id_trans_type       VARCHAR(50)  PRIMARY KEY,
    description         VARCHAR(255) NOT NULL,
    type_list           VARCHAR(255) NOT NULL,
    legacy_mssql_code   VARCHAR(255),
    storage_state       VARCHAR(255),
    version             BIGINT,
    created_by          VARCHAR(255),
    created_time        TIMESTAMP(6),
    modified_by         VARCHAR(255),
    modified_time       TIMESTAMP(6)
);

CREATE INDEX IF NOT EXISTS of1_fms_transaction_type_legacy_idx
    ON of1_fms_transaction_type (legacy_mssql_code);
```

- [ ] **Step 2.2: Append changeset fms:23 (seed 15 rows)**

```sql
--changeset fms:23-seed-transaction-type labels:schema-update context:dev,beta,prod
--comment: Seed 15 loại giao dịch khớp enum TypeOfService (11 cũ + 4 mới)
INSERT INTO of1_fms_transaction_type (id_trans_type, description, type_list, legacy_mssql_code) VALUES
    ('AIR_EXPORT',         'Export (Air)',       'Air Export', 'AirExpTransactions'),
    ('AIR_IMPORT',         'Import (Air)',       'Air Import', 'AirImpTransactions'),
    ('SEA_EXPORT_FCL',     'Export (Sea FCL)',   'Sea Export', 'SeaExpTransactions_FCL'),
    ('SEA_EXPORT_LCL',     'Export (Sea LCL)',   'Sea Export', 'SeaExpTransactions_LCL'),
    ('SEA_EXPORT_CSL',     'Export (Consol)',    'Sea Export', 'SeaExpTransactions_CSL'),
    ('SEA_IMPORT_FCL',     'Import (Sea FCL)',   'Sea Import', 'SeaImpTransactions_FCL'),
    ('SEA_IMPORT_LCL',     'Import (Sea LCL)',   'Sea Import', 'SeaImpTransactions_LCL'),
    ('SEA_IMPORT_CSL',     'Import (Consol)',    'Sea Import', 'SeaImpTransactions_CSL'),
    ('CUSTOMS_LOGISTICS',  'Logistics',          'Logistics',  'CustomsLogistics'),
    ('INLAND_TRUCKING',    'Inland Trucking',    'Logistics',  'InlandTrucking'),
    ('CROSS_BORDER',       'Cross Border',       'Logistics',  'LogisticsCrossBorder'),
    ('ROUND_USE_TRUCKING', 'Round Use Trucking', 'Logistics',  'RoundUseTrucking'),
    ('WAREHOUSE',          'Warehouse Service',  'Logistics',  'WarehouseService'),
    ('EXPRESS',            'Express',            'Logistics',  'ExpressTransactions'),
    ('PROJECT_LOGISTICS',  'Projects',           'Logistics',  'ProjectLogistics')
ON CONFLICT (id_trans_type) DO NOTHING;
```

- [ ] **Step 2.3: Append changeset fms:24 (create transaction_type_sequence)**

```sql
--changeset fms:24-create-transaction-type-sequence labels:schema-update context:dev,beta,prod
--comment: Tạo bảng of1_fms_transaction_type_sequence per-company lưu config sinh document number và lock days
CREATE TABLE IF NOT EXISTS of1_fms_transaction_type_sequence (
    id                       BIGSERIAL    PRIMARY KEY,
    company_id               BIGINT       NOT NULL,
    id_trans_type            VARCHAR(50)  NOT NULL,
    sign_prefix              VARCHAR(255),
    number_format            VARCHAR(255),
    reset_period_days        INTEGER      NOT NULL DEFAULT 365,
    current_sequence         INTEGER      NOT NULL DEFAULT 0,
    last_reset_date          DATE,
    no_days_lock             INTEGER      NOT NULL DEFAULT 0,
    day_of_logistics_lock    INTEGER      NOT NULL DEFAULT 0,
    lock_again_after_unlock  INTEGER      NOT NULL DEFAULT 0,
    storage_state            VARCHAR(255),
    version                  BIGINT,
    created_by               VARCHAR(255),
    created_time             TIMESTAMP(6),
    modified_by              VARCHAR(255),
    modified_time            TIMESTAMP(6),
    CONSTRAINT of1_fms_trans_type_seq_company_type_uk
        UNIQUE (company_id, id_trans_type),
    CONSTRAINT of1_fms_trans_type_seq_type_fk
        FOREIGN KEY (id_trans_type) REFERENCES of1_fms_transaction_type (id_trans_type)
);

CREATE INDEX IF NOT EXISTS of1_fms_trans_type_seq_company_idx
    ON of1_fms_transaction_type_sequence (company_id);
```

- [ ] **Step 2.4: Verify Liquibase formatted SQL syntax**

Run manual check: mở file, đảm bảo mỗi changeset có `--changeset fms:N-slug labels:schema-update context:dev,beta,prod` header.

- [ ] **Step 2.5: Apply migration lên DB dev**

Run: `./gradlew :module:core:bootRun -Pprofile=dev` (hoặc script Liquibase update tương đương trong repo)
Expected: Log "ChangeSet fms:22-create-transaction-type ran successfully" (và 23, 24). Không có ERROR.

- [ ] **Step 2.6: Verify bảng + rows trên Postgres**

```sql
SELECT COUNT(*) FROM of1_fms_transaction_type;  -- expect 15
SELECT id_trans_type FROM of1_fms_transaction_type ORDER BY id_trans_type;
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'of1_fms_transaction_type%';
```

- [ ] **Step 2.7: Commit**

```bash
git add module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql
git commit -m "feat(db): add of1_fms_transaction_type + sequence tables with seed"
```

---

## Task 3: Entity `TransactionType`

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java`

> **Note**: Không extend `PersistableEntity<String>` vì base class có `@Id @GeneratedValue(IDENTITY)` — không phù hợp với String PK không auto-generate. Thay vào đó tự khai báo các audit field để match schema DB.

- [ ] **Step 3.1: Create TransactionType.java**

```java
package of1.fms.module.transaction.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import of1.fms.core.common.TypeOfService;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

@Entity
@Table(
  name = TransactionType.TABLE_NAME,
  indexes = {
    @Index(name = TransactionType.TABLE_NAME + "_legacy_idx", columnList = "legacy_mssql_code")
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter
@Setter
public class TransactionType implements Serializable {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "of1_fms_transaction_type";

  @Id
  @Column(name = "id_trans_type", length = 50, nullable = false)
  private String idTransType;

  @Column(name = "description", length = 255, nullable = false)
  private String description;

  @Column(name = "type_list", length = 255, nullable = false)
  private String typeList;

  @Column(name = "legacy_mssql_code", length = 255)
  private String legacyMssqlCode;

  @Column(name = "storage_state", length = 255)
  private String storageState;

  @Column(name = "version")
  private Long version;

  @Column(name = "created_by", length = 255)
  private String createdBy;

  @Column(name = "created_time")
  private Date createdTime;

  @Column(name = "modified_by", length = 255)
  private String modifiedBy;

  @Column(name = "modified_time")
  private Date modifiedTime;

  /** Convenience: resolve to enum value. Returns null if no match. */
  public TypeOfService toEnum() {
    return TypeOfService.parse(idTransType);
  }
}
```

- [ ] **Step 3.2: Build module transaction**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 3.3: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java
git commit -m "feat(transaction): add TransactionType entity"
```

---

## Task 4: Entity `TransactionTypeSequence`

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java`

- [ ] **Step 4.1: Create TransactionTypeSequence.java**

```java
package of1.fms.module.transaction.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.CompanyEntity;

import java.io.Serial;
import java.time.LocalDate;

@Entity
@Table(
  name = TransactionTypeSequence.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = TransactionTypeSequence.TABLE_NAME + "_company_type_uk",
      columnNames = {"company_id", "id_trans_type"}
    )
  },
  indexes = {
    @Index(
      name = TransactionTypeSequence.TABLE_NAME + "_company_idx",
      columnList = "company_id"
    )
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter
@Setter
public class TransactionTypeSequence extends CompanyEntity {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "of1_fms_transaction_type_sequence";

  @Column(name = "id_trans_type", length = 50, nullable = false)
  private String idTransType;

  @Column(name = "sign_prefix", length = 255)
  private String signPrefix;

  @Column(name = "number_format", length = 255)
  private String numberFormat;

  @Column(name = "reset_period_days", nullable = false)
  private Integer resetPeriodDays = 365;

  @Column(name = "current_sequence", nullable = false)
  private Integer currentSequence = 0;

  @Column(name = "last_reset_date")
  private LocalDate lastResetDate;

  @Column(name = "no_days_lock", nullable = false)
  private Integer noDaysLock = 0;

  @Column(name = "day_of_logistics_lock", nullable = false)
  private Integer dayOfLogisticsLock = 0;

  @Column(name = "lock_again_after_unlock", nullable = false)
  private Integer lockAgainAfterUnlock = 0;
}
```

- [ ] **Step 4.2: Build**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 4.3: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java
git commit -m "feat(transaction): add TransactionTypeSequence entity"
```

---

## Task 5: Repositories

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java`
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java`

- [ ] **Step 5.1: Create TransactionTypeRepository**

Kiểm tra package repository hiện có: `ls module/transaction/src/main/java/of1/fms/module/transaction/repository/ 2>/dev/null` — nếu chưa có thì tạo.

```java
package of1.fms.module.transaction.repository;

import of1.fms.module.transaction.entity.TransactionType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TransactionTypeRepository extends JpaRepository<TransactionType, String> {
  Optional<TransactionType> findByLegacyMssqlCode(String mssqlCode);
}
```

- [ ] **Step 5.2: Create TransactionTypeSequenceRepository**

```java
package of1.fms.module.transaction.repository;

import jakarta.persistence.LockModeType;
import of1.fms.module.transaction.entity.TransactionTypeSequence;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TransactionTypeSequenceRepository
    extends JpaRepository<TransactionTypeSequence, Long> {

  Optional<TransactionTypeSequence> findByCompanyIdAndIdTransType(Long companyId, String idTransType);

  @Lock(LockModeType.PESSIMISTIC_WRITE)
  @Query("SELECT s FROM TransactionTypeSequence s " +
         "WHERE s.companyId = :companyId AND s.idTransType = :idTransType")
  Optional<TransactionTypeSequence> lockForUpdate(
      @Param("companyId") Long companyId,
      @Param("idTransType") String idTransType);

  List<TransactionTypeSequence> findByCompanyId(Long companyId);
}
```

- [ ] **Step 5.3: Build**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 5.4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java \
        module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java
git commit -m "feat(transaction): add TransactionType + Sequence repositories"
```

---

## Task 6: `DocumentNumberFormatter` util (TDD)

Pure function: template `{SIGN}{YY}{MM}{###}` + date + counter → string. Không đụng JPA, không đụng Spring — hoàn toàn test được bằng unit test.

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java`
- Test: `module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java`

- [ ] **Step 6.1: Write failing test — basic format**

```java
package of1.fms.module.transaction;

import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class DocumentNumberFormatterTest {

  @Test
  void format_basicTemplate_sign_yy_mm_seq3digit() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "HAEHAN", LocalDate.of(2026, 4, 8), 1);
    assertThat(result).isEqualTo("HAEHAN2604001");
  }

  @Test
  void format_fourDigitYear() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YYYY}{MM}{####}", "HSE", LocalDate.of(2026, 12, 31), 42);
    assertThat(result).isEqualTo("HSE2026120042");
  }

  @Test
  void format_nullTemplate_usesDefault() {
    String result = DocumentNumberFormatter.format(
        null, "HAEHAN", LocalDate.of(2026, 4, 8), 7);
    assertThat(result).isEqualTo("HAEHAN2604007");
  }

  @Test
  void format_nullSign_replacedWithEmpty() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", null, LocalDate.of(2026, 4, 8), 1);
    assertThat(result).isEqualTo("2604001");
  }

  @Test
  void format_largeSequence_exceedsPadding_noTruncation() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "X", LocalDate.of(2026, 1, 1), 12345);
    assertThat(result).isEqualTo("X260112345");
  }

  @Test
  void format_negativeSequence_throws() {
    assertThatThrownBy(() -> DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "X", LocalDate.of(2026, 1, 1), -1))
      .isInstanceOf(IllegalArgumentException.class);
  }
}
```

- [ ] **Step 6.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests DocumentNumberFormatterTest`
Expected: FAIL — `DocumentNumberFormatter` not found.

- [ ] **Step 6.3: Implement DocumentNumberFormatter**

```java
package of1.fms.module.transaction;

import java.time.LocalDate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class DocumentNumberFormatter {

  private static final String DEFAULT_TEMPLATE = "{SIGN}{YY}{MM}{###}";
  private static final Pattern HASH_TOKEN = Pattern.compile("\\{(#+)\\}");

  private DocumentNumberFormatter() {}

  public static String format(String template, String signPrefix, LocalDate date, int sequence) {
    if (sequence < 0) {
      throw new IllegalArgumentException("sequence must be >= 0, got " + sequence);
    }
    String tpl = (template == null || template.isBlank()) ? DEFAULT_TEMPLATE : template;
    String sign = signPrefix == null ? "" : signPrefix;

    String yy = String.format("%02d", date.getYear() % 100);
    String yyyy = String.format("%04d", date.getYear());
    String mm = String.format("%02d", date.getMonthValue());
    String dd = String.format("%02d", date.getDayOfMonth());

    String out = tpl
        .replace("{SIGN}", sign)
        .replace("{YYYY}", yyyy)
        .replace("{YY}", yy)
        .replace("{MM}", mm)
        .replace("{DD}", dd);

    // Replace {###..#} with zero-padded sequence
    Matcher m = HASH_TOKEN.matcher(out);
    StringBuilder sb = new StringBuilder();
    while (m.find()) {
      int width = m.group(1).length();
      String padded = String.format("%0" + width + "d", sequence);
      m.appendReplacement(sb, Matcher.quoteReplacement(padded));
    }
    m.appendTail(sb);
    return sb.toString();
  }
}
```

- [ ] **Step 6.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests DocumentNumberFormatterTest`
Expected: 6 tests pass.

- [ ] **Step 6.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java \
        module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java
git commit -m "feat(transaction): add DocumentNumberFormatter with tests"
```

---

## Task 7: `TransactionTypeService` — read path + sync validator (TDD)

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java`
- Test: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java`

- [ ] **Step 7.1: Write failing test for getAll + get(enum) + validateEnumSync**

```java
package of1.fms.module.transaction;

import of1.fms.core.common.TypeOfService;
import of1.fms.module.transaction.entity.TransactionType;
import of1.fms.module.transaction.repository.TransactionTypeRepository;
import of1.fms.module.transaction.repository.TransactionTypeSequenceRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TransactionTypeServiceTest {

  @Mock TransactionTypeRepository typeRepo;
  @Mock TransactionTypeSequenceRepository seqRepo;

  private TransactionTypeService service;

  @BeforeEach
  void setUp() {
    service = new TransactionTypeService(typeRepo, seqRepo);
  }

  private TransactionType row(String id) {
    TransactionType t = new TransactionType();
    t.setIdTransType(id);
    t.setDescription(id);
    t.setTypeList("Test");
    return t;
  }

  @Test
  void get_returnsMetadataByEnum() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.reloadCache();
    TransactionType t = service.get(TypeOfService.AIR_EXPORT);
    assertThat(t).isNotNull();
    assertThat(t.getIdTransType()).isEqualTo("AIR_EXPORT");
  }

  @Test
  void getAll_returnsAllFromCache() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.reloadCache();
    assertThat(service.getAll()).hasSize(TypeOfService.values().length);
  }

  @Test
  void validateEnumSync_ok_whenDbMatchesEnum() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.validateEnumSync();  // no exception
  }

  @Test
  void validateEnumSync_fails_whenDbMissingEnumValue() {
    List<TransactionType> rows = allEnumRows().stream()
        .filter(t -> !t.getIdTransType().equals("AIR_EXPORT"))
        .collect(Collectors.toList());
    when(typeRepo.findAll()).thenReturn(rows);
    assertThatThrownBy(() -> service.validateEnumSync())
      .isInstanceOf(IllegalStateException.class)
      .hasMessageContaining("AIR_EXPORT");
  }

  @Test
  void validateEnumSync_fails_whenDbHasExtraValue() {
    List<TransactionType> rows = new java.util.ArrayList<>(allEnumRows());
    rows.add(row("UNKNOWN_TYPE"));
    when(typeRepo.findAll()).thenReturn(rows);
    assertThatThrownBy(() -> service.validateEnumSync())
      .isInstanceOf(IllegalStateException.class)
      .hasMessageContaining("UNKNOWN_TYPE");
  }

  private List<TransactionType> allEnumRows() {
    return Arrays.stream(TypeOfService.values())
        .map(v -> row(v.name()))
        .collect(Collectors.toList());
  }
}
```

- [ ] **Step 7.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: FAIL — `TransactionTypeService` not found.

- [ ] **Step 7.3: Implement TransactionTypeService (read path + validator only)**

> Note: Write path `generateNextNumber` sẽ thêm ở Task 8 để giữ test nhỏ.

```java
package of1.fms.module.transaction;

import jakarta.annotation.PostConstruct;
import of1.fms.core.common.TypeOfService;
import of1.fms.module.transaction.entity.TransactionType;
import of1.fms.module.transaction.repository.TransactionTypeRepository;
import of1.fms.module.transaction.repository.TransactionTypeSequenceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class TransactionTypeService {

  private final TransactionTypeRepository typeRepo;
  private final TransactionTypeSequenceRepository seqRepo;
  private volatile Map<String, TransactionType> cache = Collections.emptyMap();

  @Autowired
  public TransactionTypeService(
      TransactionTypeRepository typeRepo,
      TransactionTypeSequenceRepository seqRepo) {
    this.typeRepo = typeRepo;
    this.seqRepo = seqRepo;
  }

  @PostConstruct
  public void init() {
    reloadCache();
    validateEnumSync();
  }

  public void reloadCache() {
    Map<String, TransactionType> map = new ConcurrentHashMap<>();
    for (TransactionType t : typeRepo.findAll()) {
      map.put(t.getIdTransType(), t);
    }
    this.cache = map;
  }

  public TransactionType get(TypeOfService type) {
    if (type == null) return null;
    return cache.get(type.name());
  }

  public List<TransactionType> getAll() {
    return List.copyOf(cache.values());
  }

  public void validateEnumSync() {
    Set<String> enumIds = Arrays.stream(TypeOfService.values())
        .map(Enum::name).collect(Collectors.toSet());
    Set<String> dbIds = typeRepo.findAll().stream()
        .map(TransactionType::getIdTransType).collect(Collectors.toSet());
    Set<String> missingInDb = new java.util.HashSet<>(enumIds);
    missingInDb.removeAll(dbIds);
    Set<String> extraInDb = new java.util.HashSet<>(dbIds);
    extraInDb.removeAll(enumIds);
    if (!missingInDb.isEmpty() || !extraInDb.isEmpty()) {
      throw new IllegalStateException(
        "TransactionType table out of sync with TypeOfService enum. " +
        "Missing in DB: " + missingInDb + ", extra in DB: " + extraInDb);
    }
  }
}
```

- [ ] **Step 7.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: 5 tests pass.

- [ ] **Step 7.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java \
        module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java
git commit -m "feat(transaction): add TransactionTypeService read path + sync validator"
```

---

## Task 8: `generateNextNumber` — write path với row-lock (TDD)

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java`
- Modify: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java`

- [ ] **Step 8.1: Add failing tests cho generateNextNumber**

Thêm vào `TransactionTypeServiceTest`:

```java
@Test
void generateNextNumber_existingSequence_incrementsAndFormats() {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(100L);
  seq.setIdTransType("AIR_EXPORT");
  seq.setSignPrefix("HAEHAN");
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(5);
  seq.setLastResetDate(LocalDate.now());

  when(seqRepo.lockForUpdate(100L, "AIR_EXPORT")).thenReturn(Optional.of(seq));
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.AIR_EXPORT, LocalDate.of(2026, 4, 8));

  assertThat(seq.getCurrentSequence()).isEqualTo(6);
  assertThat(result).isEqualTo("HAEHAN2604006");
}

@Test
void generateNextNumber_noExistingSequence_createsWithDefaults() {
  when(seqRepo.lockForUpdate(100L, "SEA_EXPORT_FCL")).thenReturn(Optional.empty());
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.SEA_EXPORT_FCL, LocalDate.of(2026, 4, 8));

  assertThat(result).endsWith("001");
  assertThat(result).contains("2604");
}

@Test
void generateNextNumber_resetPeriodElapsed_resetsCounter() {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(100L);
  seq.setIdTransType("AIR_EXPORT");
  seq.setSignPrefix("HAE");
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(999);
  seq.setLastResetDate(LocalDate.of(2025, 1, 1));  // > 365 days ago

  when(seqRepo.lockForUpdate(100L, "AIR_EXPORT")).thenReturn(Optional.of(seq));
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.AIR_EXPORT, LocalDate.of(2026, 4, 8));

  assertThat(seq.getCurrentSequence()).isEqualTo(1);
  assertThat(seq.getLastResetDate()).isEqualTo(LocalDate.of(2026, 4, 8));
  assertThat(result).isEqualTo("HAE2604001");
}
```

Thêm imports: `java.time.LocalDate`, `java.util.Optional`, `static org.mockito.ArgumentMatchers.any`, `of1.fms.module.transaction.entity.TransactionTypeSequence`.

- [ ] **Step 8.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: FAIL — `generateNextNumber` not defined.

- [ ] **Step 8.3: Implement generateNextNumber**

Thêm method vào `TransactionTypeService`:

```java
@Transactional
public String generateNextNumber(Long companyId, TypeOfService type, LocalDate today) {
  if (companyId == null || type == null) {
    throw new IllegalArgumentException("companyId and type are required");
  }
  String idTransType = type.name();
  TransactionTypeSequence seq = seqRepo.lockForUpdate(companyId, idTransType)
      .orElseGet(() -> createDefaultSequence(companyId, idTransType));

  if (shouldReset(seq, today)) {
    seq.setCurrentSequence(0);
    seq.setLastResetDate(today);
  }

  seq.setCurrentSequence(seq.getCurrentSequence() + 1);
  seqRepo.save(seq);

  return DocumentNumberFormatter.format(
      seq.getNumberFormat(),
      seq.getSignPrefix(),
      today,
      seq.getCurrentSequence());
}

public String generateNextNumber(Long companyId, TypeOfService type) {
  return generateNextNumber(companyId, type, LocalDate.now());
}

private boolean shouldReset(TransactionTypeSequence seq, LocalDate today) {
  if (seq.getLastResetDate() == null) return false;
  int period = seq.getResetPeriodDays() == null ? 0 : seq.getResetPeriodDays();
  if (period <= 0) return false;
  return java.time.temporal.ChronoUnit.DAYS.between(seq.getLastResetDate(), today) >= period;
}

private TransactionTypeSequence createDefaultSequence(Long companyId, String idTransType) {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(companyId);
  seq.setIdTransType(idTransType);
  seq.setSignPrefix(defaultSignPrefix(idTransType));
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(0);
  seq.setLastResetDate(LocalDate.now());
  seq.setNoDaysLock(0);
  seq.setDayOfLogisticsLock(0);
  seq.setLockAgainAfterUnlock(0);
  return seq;
}

/** Fallback prefix khi company chưa config — derived từ MSSQL HPS seed (xem spec section 5.5). */
private String defaultSignPrefix(String idTransType) {
  return switch (idTransType) {
    case "AIR_EXPORT" -> "HAE";
    case "AIR_IMPORT" -> "HAI";
    case "SEA_EXPORT_FCL", "SEA_EXPORT_LCL", "SEA_EXPORT_CSL" -> "HSE";
    case "SEA_IMPORT_FCL", "SEA_IMPORT_LCL", "SEA_IMPORT_CSL" -> "HSI";
    case "CUSTOMS_LOGISTICS" -> "HLG";
    case "INLAND_TRUCKING"   -> "HTR";
    case "EXPRESS"           -> "HEX";
    case "PROJECT_LOGISTICS" -> "HPR";
    case "WAREHOUSE"         -> "HST";
    default -> "DOC";
  };
}
```

Thêm imports: `org.springframework.transaction.annotation.Transactional`, `java.time.LocalDate`, `of1.fms.module.transaction.entity.TransactionTypeSequence`.

- [ ] **Step 8.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: 8 tests pass.

- [ ] **Step 8.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java \
        module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java
git commit -m "feat(transaction): generateNextNumber with row-lock, reset, default fallback"
```

---

## Task 9: Concurrency integration test

**Files:**
- Create: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java`

> Chỉ triển khai nếu repo đã có setup Testcontainers Postgres. Nếu chưa, mark task này là **skipped** và ghi chú trong commit message; concurrency được verify manually trên dev DB bằng script thay thế.

- [ ] **Step 9.1: Check Testcontainers availability**

Run: `grep -rn "Testcontainers\|@Container\|PostgreSQLContainer" module/transaction/src/test/ module/core/src/test/ 2>/dev/null | head`

Nếu không có kết quả → **skip** task này, ghi note `docs/superpowers/plans/...` và chuyển sang Task 10.

- [ ] **Step 9.2 (if available): Write concurrency IT**

```java
package of1.fms.module.transaction;

import of1.fms.core.common.TypeOfService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.*;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class TransactionTypeGenerateConcurrencyIT {

  @Autowired TransactionTypeService service;

  @Test
  void concurrentGenerate_noDuplicates() throws Exception {
    int threads = 20;
    int callsPerThread = 10;
    long companyId = 999_001L;
    TypeOfService type = TypeOfService.AIR_EXPORT;

    ExecutorService pool = Executors.newFixedThreadPool(threads);
    List<Future<String>> futures = new ArrayList<>();
    for (int i = 0; i < threads * callsPerThread; i++) {
      futures.add(pool.submit(() -> service.generateNextNumber(companyId, type)));
    }
    pool.shutdown();
    pool.awaitTermination(60, TimeUnit.SECONDS);

    List<String> all = new ArrayList<>();
    for (Future<String> f : futures) all.add(f.get());
    Set<String> unique = all.stream().collect(Collectors.toSet());

    assertThat(all).hasSize(threads * callsPerThread);
    assertThat(unique).hasSize(threads * callsPerThread);  // no duplicates
  }
}
```

- [ ] **Step 9.3: Run IT**

Run: `./gradlew :module:transaction:integrationTest --tests TransactionTypeGenerateConcurrencyIT` (hoặc tên task tương đương trong repo)
Expected: PASS — không có số trùng.

- [ ] **Step 9.4: Commit**

```bash
git add module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java
git commit -m "test(transaction): concurrent generateNextNumber no duplicates"
```

---

## Task 10: Full build + final verification

- [ ] **Step 10.1: Clean build toàn repo**

Run: `./gradlew clean build -x test` (nếu test chạy chậm) hoặc `./gradlew clean build`
Expected: BUILD SUCCESSFUL.

- [ ] **Step 10.2: Run toàn bộ test module transaction**

Run: `./gradlew :module:transaction:test`
Expected: all green.

- [ ] **Step 10.3: Apply migration lên DB dev rồi khởi động ứng dụng**

Run: Start FMS backend như workflow thường.
Expected: Application start OK. Log có `TransactionTypeService.init()` không throw, `validateEnumSync` passes.

- [ ] **Step 10.4: Smoke query DB**

```sql
SELECT id_trans_type, description, type_list, legacy_mssql_code
FROM of1_fms_transaction_type
ORDER BY id_trans_type;
```
Expected: 15 rows.

```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'of1_fms_transaction_type_sequence' ORDER BY ordinal_position;
```
Expected: 17 columns khớp schema ở Task 2.

- [ ] **Step 10.5: Final commit (chỉ nếu có changes từ fix nhỏ)**

```bash
git status
# nếu sạch, không commit. Nếu có fix, commit với message mô tả.
```

---

## Out of scope (không làm trong plan này — sẽ có plan riêng)

- MSSQL import flow (spec section 5.7) — chờ quyết định trigger (Kafka event vs admin endpoint vs CLI) và mapping `tenantCode → companyId`.
- UI admin quản lý `transaction_type` / `transaction_type_sequence`.
- Refactor `Transaction.typeOfService` column sang FK.
- Áp dụng `no_days_lock` / `day_of_logistics_lock` vào logic lock transaction hiện tại.

## Rollback

Nếu cần revert:
- Xoá changesets `fms:22`, `fms:23`, `fms:24` khỏi file SQL (hoặc dùng `liquibase rollbackCount 3`).
- Xoá entity / repository / service files.
- Revert enum change trong `TypeOfService.java`.
- Application sẽ fail startup validator nếu còn bảng nhưng thiếu enum value tương ứng — phải rollback đồng thời cả hai.

---

## FMS CDC HouseBill

title: "FMS CDC HouseBill"
tags: [daily, fms, cdc, house-bill, hps, mssql, transport-plan, mapping, spec, plan]
created: 2026-04-08
---

# FMS CDC HouseBill

Tổng hợp nghiên cứu, phân tích field MSSQL, implementation, design spec, và plan cho CDC mapping HPS → FMS liên quan đến HouseBill.

## Mục lục

- [Tổng quan](#tổng-quan)
- [A. HPS MSSQL Field Analysis](#a-hps-mssql-field-analysis) — nghiên cứu field chưa/đã map
- [B. CDC Implementation](#b-cdc-implementation) — code đã implement trong ngày
- [C. HouseBill CDC Completeness — Design](#c-housebill-cdc-completeness--design) — spec cho Sub-project 1
- [D. HouseBill CDC Completeness — Plan](#d-housebill-cdc-completeness--plan) — plan 12 tasks TDD
- [Appendix](#appendix) — typo reference, field dễ nhầm lẫn
- [E. Schema Mismatch Analysis & Solutions](#e-schema-mismatch-analysis--solutions) — phân tích field lệch schema MSSQL→PostgreSQL và giải pháp

---

## Tổng quan

| Chủ đề | Status | Section |
|--------|--------|---------|
| ColoaderID / AirLine analysis | Research done | A.1 |
| Status / Notes / Contact fields | Research done | A.2 |
| Lock / Audit / Commercial fields | Research done | A.3 |
| HAWB.CussignedDate | Implemented | A.4 |
| CDC Transaction → TransportPlan | Implemented (sẽ refactor) | B.1 |
| HouseBill CDC Completeness | Design + Plan | C + D |
| Schema Mismatch MSSQL→PostgreSQL | Analysis + 3 Solutions | E |

**Source chung**: `dbo.Transactions`, `dbo.TransactionDetails`, `dbo.HAWB` (HPS BFS One)
**CDC handler**: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/`
**Ref docs**: `docs/references/mapping/ref/sql_query_analysis.md`, `docs/references/bfs/documentation.md`, `docs/references/mapping/mapping-transactions.md`

---

# A. HPS MSSQL Field Analysis

## A.1 ColoaderID / ColoaderID_O / AirLine

Source: `dbo.Transactions`

### Giống nhau

- Cả 3 đều là mã đối tác (partner code) — join ra bảng partner để lookup label
- Cả 3 phản ánh "bên vận chuyển" — thuộc nhóm carrier/coloader

### Khác nhau

| Field | Giai đoạn Save | Ý nghĩa nghiệp vụ | Phạm vi |
|---|---|---|---|
| `ColoaderID` | Inbound + Outbound | Coloader/carrier chính — canonical "carrier hiện tại" | Mọi TypeOfService |
| `ColoaderID_O` | Chỉ Outbound (suffix `_O`) | Coloader thực tế khi xuất — có thể khác ColoaderID (đổi hãng tại khâu handover) | Chỉ outbound |
| `AirLine` | Chỉ Inbound | Hãng hàng không actual — chỉ áp dụng Air | TypeOfService nhóm Air |

### Quan hệ

- **ColoaderID vs ColoaderID_O**: `ColoaderID_O` = snapshot riêng outbound. Nếu khác → đã đổi coloader tại khâu xuất. Ưu tiên `ColoaderID_O` nếu non-null.
- **ColoaderID vs AirLine**: ColoaderID = forwarder/coloader (CASS member). AirLine = carrier thực tế (hãng bay phát MAWB). Trong Air 2 bên **khác nhau** — forwarder bán cước, airline chở hàng.

### Trạng thái mapping FMS

| Field MSSQL | Transaction (FMS) | TransportPlan/Route |
|---|---|---|
| `ColoaderID` | `coloaderPartnerLabel` | `TransportRoute.carrierLabel` |
| `ColoaderID_O` | Chưa map | Chưa map |
| `AirLine` | `transportName` (fallback RefNoSea) | Chưa map |

### Đề xuất

1. Thêm `coloader_partner_label_outbound` hoặc ưu tiên `ColoaderID_O` → fallback `ColoaderID`
2. Tách `carrier_airline_label` riêng cho actual airline
3. `IntegratedTransaction` cần map thêm `ColoaderID` và `AirLine` cho analytics

**Gap**: `ColoaderID_O` chưa map ở bất kỳ entity nào. "Forwarder vs actual airline" là khác biệt quan trọng — đừng merge vào 1 field.

---

## A.2 Status / Notes / Contact Fields

Source: `dbo.Transactions`

### 6 cột phân tích

| Cột | Kiểu | Ý nghĩa | Update stage |
|---|---|---|---|
| `Starus` | varchar | Status (typo gốc HPS) — trạng thái term: CREATE, OPEN, CLOSED, PRE-ALERT, TERMED... | Inbound + Outbound |
| `Delivered` | bit/varchar | Cờ đã giao hàng | Inbound + Outbound |
| `BookingRequestNotes` | nvarchar | Ghi chú Sales/CS khi tạo booking request | Chỉ Inbound |
| `Remark` | nvarchar | Nhận xét chung về shipment | Chỉ Inbound |
| `Attn` | nvarchar | Attention to — tên người chịu trách nhiệm file | Chỉ Inbound |
| `OtherInfo` | nvarchar | M-B/L Type hoặc metadata chứng từ | Inbound + Outbound |

### Nhóm semantics

**Operation state**: `Starus` + `Delivered` → xây state machine: `Booked → In Transit → Delivered → Closed`

**Notes family (3 field RIÊNG — đừng gộp)**:

| Field MSSQL | FMS target | Ý nghĩa |
|---|---|---|
| `BookingRequestNotes` | Chưa map | Yêu cầu từ khách lúc book |
| `Remark` | Chưa map | Ghi chú vận hành của staff |
| `ExpressNotes` | `Transaction.note` | Ghi chú chứng từ in trên bill |

3 field có audience và lifecycle khác nhau, **không nên gộp** thành 1 field `notes`.

**Contact / Metadata**: `Attn` = Sales/CS owner. `OtherInfo` = M-B/L Type.

### Mapping gaps

| Field | Gap |
|---|---|
| `Starus` | Doc nói map → `state`, nhưng CDC handler chưa set |
| `Delivered` | Chưa map — cần thêm field + column + CDC |
| `BookingRequestNotes` | Chưa map — cần field riêng |
| `Remark` | Chưa map — cần field riêng |
| `Attn` | Chưa map — cần `fileOwnerName` |
| `OtherInfo` | Chưa map (có placeholder comment) — map tới `mblType` |

### Đề xuất schema mở rộng Transaction (FMS)

```java
@Column(name = "state")                       private String state;                // ← Starus
@Column(name = "delivered")                    private Boolean delivered;           // ← Delivered
@Column(name = "booking_request_notes")        private String bookingRequestNotes;  // ← BookingRequestNotes
@Column(name = "remark")                       private String remark;               // ← Remark
@Column(name = "file_owner_name")              private String fileOwnerName;        // ← Attn
@Column(name = "mbl_type")                     private String mblType;              // ← OtherInfo
```

### Query sample

```sql
SELECT TOP 10 TransID, TransDate, TpyeofService, Starus, Delivered,
       Attn, OtherInfo, BookingRequestNotes, Remark
FROM dbo.Transactions ORDER BY TransDate DESC;
```

Database: `HPS_DB` @ `hpsvn.openfreightone.com:34541`

### Notes

- `Starus` là typo gốc HPS — khi viết code comment nên nhắc rõ để dev sau không sửa nhầm
- Nếu enum hoá state, cần survey giá trị distinct trên HPS trước khi define `TransactionState` enum
- `Delivered` dùng `Boolean` trong Java (parse từ bit/0/1 string)

---

## A.3 Lock / Audit / Commercial Fields

Source: `dbo.Transactions`
Ref: `docs/references/mapping/ref/sql_query_analysis.md`, `docs/references/mapping/ref/legacy_entity_mapping_review.md`

### Nhóm 1: Lock / Audit nội bộ (KHÔNG sync sang FMS)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `transLock` | bit | Cờ khoá file inbound — HPS auto-set sau save, kiểm tra qua `NoDaysLock` + `DateofPrealert` | **Skip** — cơ chế lock nội bộ HPS |
| `TransLockLog` | bit | Cờ khoá file logistics — tương tự `transLock` cho tab Logistics | **Skip** — cùng lý do |
| `Revision` | int | Số lần sửa đổi file (counter) | **Skip** — dùng JPA `version` + `modified_time` của FMS |
| `ModifyDate` | datetime | Ngày sửa cuối cùng trên HPS | **Skip** — FMS đã có `modified_time` (JPA auditing) |

### Nhóm 2: Notes / Log (append-only text)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `TransactionNotes` | ntext | Log thay đổi — HPS append text mỗi lần save (format: `[date] [user] [action]`) | **Skip** (optional phase sau) — FMS có `modified_by` + `modified_time` |
| `ReportInfor` | ntext | Thông tin báo cáo — arrival/delivery status updates, milestone notes | **Map** → `reportInfo` (text) |

### Nhóm 3: Tham chiếu thương mại (NÊN sync)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `OtherInfo` | nvarchar | M-B/L Type (Original / Surrendered / Seaway / Express Release) | **Map** → `mblType` |
| `OMB` | nvarchar | Original Master Bill — số MBL gốc (có thể khác MAWB khi amendment) | **Map** → `originalMasterBillNo` |
| `Destination` | nvarchar | Điểm đến cuối — khác POD (cảng dỡ hàng vs địa chỉ giao cuối) | **Map** → `finalDestination` |
| `Ref` | nvarchar | Số tham chiếu booking / manifest number | **Đã map** → `Transaction.manifestNo` |

### DateofPrealert

| Cột | Ý nghĩa | Quyết định |
|---|---|---|
| `DateofPrealert` | Ngày gửi pre-alert cho đại lý đích. HPS dùng làm điều kiện lock, nhưng bản thân có giá trị nghiệp vụ | **Map** → `preAlertDate` |

Timeline vị trí:
```
Booking → ConsignedDate → LoadingDate (ETD)
       → DateofPrealert (gửi thông báo cho agent đích)
       → ArrivalDate (ETA) → DestinationDate (giao cuối)
```

### Tổng hợp quyết định

| Cột | Quyết định | FMS field |
|---|---|---|
| `transLock` | **Skip** | — |
| `TransLockLog` | **Skip** | — |
| `Revision` | **Skip** | — |
| `ModifyDate` | **Skip** | — |
| `TransactionNotes` | **Skip** (optional) | `changeLog` |
| `DateofPrealert` | **Map** | `preAlertDate` |
| `ReportInfor` | **Map** | `reportInfo` |
| `OtherInfo` | **Map** | `mblType` |
| `OMB` | **Map** | `originalMasterBillNo` |
| `Destination` | **Map** | `finalDestination` |
| `Ref` | **Đã xong** | `manifestNo` |

---

## A.4 HAWB.CussignedDate

Status: **Implemented**
Source: `dbo.HAWB`
Ref: `docs/references/mapping/ref/sql_query_analysis.md:129`, `docs/references/mapping/ref/legacy_entity_mapping_review.md:27`

### Ý nghĩa

`CussignedDate` = typo của `ConsignedDate`. **Consigned Date** = ngày consign/handover lô hàng cho carrier — bắt đầu trách nhiệm vận chuyển. Trên HAWB gọi là "Date of Issue" hoặc "Date of Consignment".

Chỉ update ở **Inbound Save** — mốc khởi đầu shipment.

### Timeline điển hình

```
Booking → CussignedDate (handover) → IssuedDate (phát HAWB) → LoadingDate (ETD) → ArrivalDate (ETA) → DestinationDate (giao cuối)
```

### Implementation

**Entity HouseBill**: `consignedDate` (column `consigned_date`) — sửa typo trong FMS, handler vẫn đọc raw key `"CussignedDate"`.

**CDC mapping** (`HAWBCDCHandler.enrichHouseBill`):
```java
Long consignedDate = CDCMapperUtils.parseLong(data.get("CussignedDate"));
if (consignedDate != null) hb.setConsignedDate(CDCMapperUtils.toTimestamp(consignedDate));
```

**Liquibase**:
```sql
ALTER TABLE of1_fms_house_bill ADD COLUMN IF NOT EXISTS consigned_date TIMESTAMP(6);
```

**Lưu ý**: Đừng gộp với `issuedDate` — 2 khái niệm khác nhau. Nếu FMS cần state machine chi tiết, `consignedDate` xác định `BOOKED → CONSIGNED` trước `IN_TRANSIT`.

---

# B. CDC Implementation

## B.1 CDC Transactions → HouseBill + TransportPlan/Route

Status: **Implemented** — `saveDraftHouseBill` sẽ bị **xoá** trong section C (Completeness spec), ownership chuyển sang `TransactionDetailsCDCHandler`.
File: `TransactionsCDCHandler.java`

### Goal

Khi CDC `dbo.Transactions` flow vào FMS, ngoài upsert `IntegratedTransaction` + `of1_fms_transactions`:
1. Tạo/đảm bảo có **HouseBill draft** gắn với transaction.
2. Build **TransportPlan** + **TransportRoute** theo thông tin transit trên MSSQL.

### MSSQL Columns (4 cột transit)

| Cột | Ý nghĩa |
|---|---|
| `TransitPortFrom` | Cảng transit đầu vào |
| `TransitPortDes` | Cảng transit đầu ra (thường trùng `TransitPortFrom`) |
| `ETDTransit` | Ngày/giờ rời transit port |
| `ETATransit` | Ngày/giờ đến transit port |

### Target Entities

- `of1_fms_house_bill` — neo vào `transaction_id`, unique theo `hawb_no`
- `of1_fms_transport_plan` — neo vào `house_bill_id`, chứa POL/POD + depart/arrival tổng
- `of1_fms_transport_route` — các chặng con, có `sort_order`

### Flow

```
saveFmsTransaction
  → save Transaction (FMS)
  → saveDraftHouseBill(data, fmsTx)        // trả về HouseBill
  → saveTransportPlan(data, hb, fmsTx)     // rebuild plan + routes
```

### saveDraftHouseBill

- Lookup theo `HWBNO` (unique) → fallback `findByTransactionId`
- Nếu không có → tạo draft: `companyId` từ `CDCTenantContext`, `transactionId`, `hawbNo`, `typeOfService`, `shipmentType`, `issuedDate` copy từ `fmsTx`

### buildTransportPlan

**Plan header**: `fromLocation=PortofLading`, `toLocation=PortofUnlading`, `departTime=LoadingDate`, `arrivalTime=ArrivalDate`

**Normalize transit**: nếu chỉ 1 trong 2 cột `TransitPortFrom`/`TransitPortDes` có giá trị → dùng chung cho cả 2.

**Route logic**:

| Case | Routes |
|---|---|
| Không transit | 1 route: `POL → POD` |
| Có transit | Leg1: `POL → Transit` (depart=LoadingDate, arrival=ETATransit), Leg2: `Transit → POD` (depart=ETDTransit, arrival=ArrivalDate) |

**Route fields**: `transportNo=FlghtNo`, `carrierLabel=lookupPartnerName(ColoaderID)`, location codes qua `lookupLocationCode(label)`

### User Decisions (confirmed)

1. Lookup transaction by code → lookup house bill theo transaction id → tạo draft nếu chưa có
2. Transit chỉ 1 port: `fromLocation → transitPort → toLocation`
3. Rebuild routes: mỗi lần CDC update → xoá plan cũ rồi build lại, không merge

### Code Structure

```java
saveFmsTransaction(...)                  // upsert fms_transaction
  └── saveDraftHouseBill(data, fmsTx)    // returns HouseBill (draft nếu cần)
  └── saveTransportPlan(data, hb, fmsTx) // delete old + build + save
        └── buildTransportPlan(...)      // plan header + routes
              └── newRoute(...)          // helper cho từng TransportRoute
```

**Dependencies mới inject**: `HouseBillRepository`, `TransportPlanRepository` (đã có sẵn: `SettingLocationRepository`, `IntegratedPartnerRepository`).

### Notes / TODO

- `saveDraftHouseBill` sẽ bị xoá — xem section C, Task 6. `TransportPlan` logic giữ lại nhưng refactor signature.
- HouseBill chưa có field `status`/`draft` rõ ràng — thêm enum status sau (deferred)
- Chưa xử lý multi-transit (schema MSSQL chỉ expose 1 cặp transit)
- Pipeline (booking_process_id / status update) xử lý ở bước sau

---

# C. HouseBill CDC Completeness — Design

Scope: Sub-project 1 of "HouseBill + HouseBillDetail mapping" decomposition
Status: Draft — pending user review

## Context

Three CDC handlers currently write to `of1_fms_house_bill`:

1. `TransactionsCDCHandler.saveDraftHouseBill()` — creates draft when `Transactions` CDC fires.
2. `TransactionDetailsCDCHandler.upsert()` — writes from `TransactionDetails`.
3. `HAWBCDCHandler.enrichHouseBill()` — writes from `HAWB`.

Problems:
- Overlapping writes cause race conditions; last writer wins non-deterministically (cargo weights written by both #2 and #3).
- Many fields on `HouseBill` entity are unmapped despite MSSQL sources being available.
- Partner code lookups only populate labels, not foreign keys — breaking FK-based queries.
- No single source of truth for shared fields.

This spec fixes data completeness, introduces shared lookup utility, enforces ownership matrix, and removes the draft-creation path.

## Goals

1. Every field on `HouseBill` entity is mapped from an explicit HPS source (or documented as FMS-internal).
2. Each field has exactly one owning CDC handler; no race between handlers.
3. Partner/account codes are resolved to FK ids, not just labels.
4. Shared lookup logic lives in one testable helper.

## Non-goals

- `HouseBillStatus` enum/workflow (deferred).
- `of1_fms_air/sea/truck/logistics_house_bill_detail` mapping (Sub-project 2 & 3).
- UI changes for House Bill editor.
- CDC ordering guarantees / snapshot replay for out-of-order events.
- `bookingProcessId` linking (FMS-internal; set by booking flow).

## Ownership matrix

| Field | Owner | HPS source |
|---|---|---|
| `hawbNo` (PK) | TransactionDetails | `TransactionDetails.HWBNO` |
| `companyId` | TransactionDetails (at create) | `CDCTenantContext` |
| `transactionId` | TransactionDetails | Lookup `of1_fms_transactions.id` by `TRANSID` |
| `typeOfService` | TransactionDetails | Copied from `of1_fms_transactions.type_of_service` via transaction lookup |
| `shipmentType` | TransactionDetails | `TransactionDetails.ShipmentType` |
| `clientPartnerId` / `clientLabel` | TransactionDetails | `TransactionDetails.ContactID` → `IntegratedPartner` lookup |
| `salemanAccountId` / `salemanLabel` | TransactionDetails | `TransactionDetails.SalesManID` → `SettingsUserRole` lookup |
| `handlingAgentPartnerId` / `handlingAgentLabel` | HAWB (primary), fallback Transaction | `HAWB.HBAgentID` → `IntegratedPartner`; fallback `Transaction.handlingAgent*` |
| `assigneeAccountId` / `assigneeLabel` | HAWB | Copy `of1_fms_transactions.createdByAccountId/Name` via `transactionId` |
| `descOfGoods` | TransactionDetails | `TransactionDetails.Description` |
| `packagingType` | TransactionDetails | `TransactionDetails.UnitDetail` |
| `cargoGrossWeightInKgs` | **HAWB** | `HAWB.GrossWeight` |
| `cargoChargeableWeightInKgs` | **HAWB** | `HAWB.ChargeableWeight` |
| `cargoVolumeInCbm` | **HAWB** | `HAWB.Dimension` |
| `containerVol` | **HAWB** | `HAWB.ContainerSize` |
| `packageQuantity` | **HAWB** | `HAWB.Pieces` |
| `consignedDate` | HAWB | `HAWB.CussignedDate` |
| `issuedDate` | TransactionDetails | Copy `of1_fms_transactions.issued_date` via transaction lookup |
| `bookingProcessId` | FMS-only | Null from CDC |

**Key rule**: cargo weights / container / packages are owned exclusively by HAWB.

## Architecture

### Removed code

- `TransactionsCDCHandler.saveDraftHouseBill()` — deleted.
- Call site in `saveFmsTransaction` — removed.

### New component — `HouseBillLookupSupport`

Location: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HouseBillLookupSupport.java`
Type: Spring `@Component`

```java
public record PartnerRef(Long id, String label) {}
public record AccountRef(Long id, String label) {}
public record TransactionRef(
    Long id, TypeOfService typeOfService, Date issuedDate,
    Long handlingAgentPartnerId, String handlingAgentLabel,
    Long createdByAccountId, String createdByAccountName
) {}

public class HouseBillLookupSupport {
  PartnerRef resolveClient(String contactId);
  AccountRef resolveSaleman(String salesmanUsername);
  PartnerRef resolveHandlingAgent(String hawbAgentId, TransactionRef transactionRef);
  TransactionRef resolveTransaction(String transId);
}
```

Behavior: null-safe, lookup miss returns ref with `id=null, label=rawCode`, logs at `debug`.

### Refactor — `TransactionDetailsCDCHandler`

Inject `HouseBillLookupSupport`. In `upsert(data)`:

```java
String hwbNo = CDCMapperUtils.trimString(data.get("HWBNO"));
if (hwbNo == null) return;

synchronized (lockManager.getLock("housebill:" + hwbNo)) {
  HouseBill hb = houseBillRepo.findByHawbNo(hwbNo);
  if (hb == null) {
    hb = new HouseBill();
    hb.setHawbNo(hwbNo);
    hb.setCompanyId(CDCTenantContext.getCompanyId());
  }

  // Transaction lookup → transactionId, typeOfService, issuedDate
  TransactionRef txRef = lookupSupport.resolveTransaction(transId);
  if (txRef != null) { hb.setTransactionId(txRef.id()); ... }

  // Client (ContactID → IntegratedPartner), Saleman (SalesManID → SettingsUserRole)
  // TransactionDetails-owned plain fields: descOfGoods, packagingType
  // NOTE: cargo weights OWNED BY HAWB — do NOT set here.

  houseBillRepo.save(hb);
}
```

### Refactor — `HAWBCDCHandler.enrichHouseBill`

```java
synchronized (lockManager.getLock("housebill:" + hawbNo)) {
  HouseBill hb = houseBillRepo.findByHawbNo(hawbNo);
  if (hb == null) return; // Wait for TransactionDetails CDC

  // HAWB-owned: cargo weights, container, consigned date
  // Handling agent (HAWB primary, Transaction fallback)
  // Assignee = Transaction.createdBy*

  houseBillRepo.save(hb);
}
```

### Side change — `TransactionsCDCHandler`

Populate `Transaction.handlingAgentPartnerId` (not just label) via `lookupSupport.resolveHandlingAgent`.

## Data flow

```
1. Transactions CDC        → of1_fms_transactions (+ handlingAgent* now with id)
2. TransactionDetails CDC  → of1_fms_house_bill (CREATE skeleton + TD-owned fields)
3. HAWB CDC                → of1_fms_house_bill (UPDATE HAWB-owned fields)
                              Skips if HB not yet created
```

**CDC ordering limitations** (accepted):
- HAWB before TransactionDetails: enrich skips; next HAWB update re-fires.
- TransactionDetails before Transactions: `resolveTransaction` returns null; fields stay null until next update.

**Lock key**: both handlers use `housebill:{hwbNo}`.

## Error handling

| Condition | Handling |
|---|---|
| Lookup miss | Return ref with `id=null, label=rawCode`. Log `debug`. |
| HAWB before TransactionDetails | `enrichHouseBill` returns early. |
| TransactionDetails before Transactions | Dependent fields stay null. Next CDC fills them. |
| DB exception | Bubble → rollback → CDC framework retry. |

## Testing

**Unit — `HouseBillLookupSupportTest`**: Mock repos with Mockito. Test resolveClient/resolveSaleman/resolveHandlingAgent/resolveTransaction (happy / null / not-found).

**Integration — `HouseBillCDCIntegrationIT`**: Testcontainers Postgres. 4 scenarios:
1. Full happy path: all fields populated correctly.
2. HAWB before TransactionDetails: enrich skipped → re-fire succeeds.
3. TransactionDetails before Transactions: transactionId null → re-fire fills.
4. Ownership enforcement: HAWB doesn't overwrite TD-owned fields.

Coverage target: 80%+.

## Migration

**No Liquibase changes**. All columns already exist. Code backward compat: existing draft HB rows updated normally by next CDC event. Weight staleness window until next HAWB CDC fires.

## Limitations / accepted risks

1. CDC ordering: HAWB-before-TransactionDetails loses data until next HAWB update.
2. Partner uniqueness assumption (`partner_code` unique).
3. Missing assignee for non-HAWB shipments.
4. Weight staleness window after deployment.

## Checklist

- [ ] Create `HouseBillLookupSupport` with 4 methods + 3 record types
- [ ] Unit tests for `HouseBillLookupSupport`
- [ ] Refactor `TransactionDetailsCDCHandler.upsert` — add lookups, remove weight writes
- [ ] Refactor `HAWBCDCHandler.enrichHouseBill` — add lock + lookups + assignee + handling agent
- [ ] Remove `TransactionsCDCHandler.saveDraftHouseBill` + call site
- [ ] Update `TransactionsCDCHandler` to populate `handlingAgentPartnerId`
- [ ] Integration tests for 4 scenarios
- [ ] Verify no Liquibase changes needed
- [ ] Update `docs/references/mapping/mapping-transactions.md` with ownership matrix

---

# D. HouseBill CDC Completeness — Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every field on `HouseBill` entity populated correctly from HPS CDC with no race between handlers.

**Architecture:** Introduce `HouseBillLookupSupport` (Spring `@Component`) that centralises partner/user/transaction lookups. Enforce ownership matrix. Remove `saveDraftHouseBill` entirely.

**Tech Stack:** Java 21, Spring Boot, JPA, JUnit 5, Mockito, AssertJ, Testcontainers.

## File structure

**New files:**
- `module/transaction/.../cdc/HouseBillLookupSupport.java`
- `module/transaction/.../cdc/HouseBillLookupSupportTest.java`

**Modified files:**
- `TransactionsCDCHandler.java` — remove `saveDraftHouseBill`; add `handlingAgentPartnerId` lookup
- `TransactionDetailsCDCHandler.java` — inject lookup support, add lookups, remove cargo weight writes
- `HAWBCDCHandler.java` — add lock; inject lookup support; set handling agent + assignee
- `docs/references/mapping/mapping-transactions.md` — update ownership matrix

---

## Task 1: Create HouseBillLookupSupport skeleton + record types

- [ ] **Step 1: Write failing skeleton test**

```java
@ExtendWith(MockitoExtension.class)
class HouseBillLookupSupportTest {
  @Mock IntegratedPartnerRepository partnerRepo;
  @Mock SettingsUserRoleRepository userRoleRepo;
  @Mock TransactionRepository transactionRepo;
  HouseBillLookupSupport support;

  @BeforeEach
  void setUp() {
    support = new HouseBillLookupSupport(partnerRepo, userRoleRepo, transactionRepo);
  }

  @Test void resolveClient_nullInput_returnsNull() {
    assertThat(support.resolveClient(null)).isNull();
  }
}
```

- [ ] **Step 2: Run test → verify FAIL** (`cannot find symbol HouseBillLookupSupport`)
- [ ] **Step 3: Create skeleton class** — `@Component`, 3 records, 4 stub methods returning null
- [ ] **Step 4: Run test → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): add HouseBillLookupSupport skeleton`

---

## Task 2: Implement resolveClient

- [ ] **Step 1: Write failing tests** — `resolveClient_found_returnsPartnerRef`, `resolveClient_notFound_returnsRefWithRawCode`
- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement**

```java
public PartnerRef resolveClient(String contactId) {
  if (contactId == null) return null;
  try {
    IntegratedPartner p = partnerRepo.getByPartnerCode(contactId);
    if (p != null) return new PartnerRef(p.getId(), p.getLabel());
  } catch (Exception e) { log.debug("Client partner lookup failed: {}", contactId); }
  return new PartnerRef(null, contactId);
}
```

- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveClient`

---

## Task 3: Implement resolveSaleman

- [ ] **Step 1: Write failing tests** — found / not-found / null
- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — `userRoleRepo.getByBfsoneUsername(username)` → `AccountRef(accountId, fullName)`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveSaleman`

---

## Task 4: Implement resolveTransaction

- [ ] **Step 1: Write failing tests** — found (full ref) / not-found / null

```java
@Test void resolveTransaction_found_returnsFullRef() {
  Transaction tx = new Transaction();
  tx.setId(10L); tx.setTypeOfService(TypeOfService.AIR_IMPORT);
  tx.setIssuedDate(new Date(1_700_000_000L));
  tx.setHandlingAgentPartnerId(55L); tx.setHandlingAgentLabel("Agent X");
  tx.setCreatedByAccountId(77L); tx.setCreatedByAccountName("Owner");
  when(transactionRepo.findByCode("TR001")).thenReturn(tx);

  TransactionRef ref = support.resolveTransaction("TR001");
  assertThat(ref.id()).isEqualTo(10L);
  assertThat(ref.typeOfService()).isEqualTo(TypeOfService.AIR_IMPORT);
  // ... assert all fields
}
```

- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — `transactionRepo.findByCode(transId)` → build `TransactionRef`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveTransaction`

---

## Task 5: Implement resolveHandlingAgent

- [ ] **Step 1: Write failing tests** — hawb present / hawb null + tx fallback / both null

```java
@Test void resolveHandlingAgent_hawbIdPresent_usesHawb() { ... }
@Test void resolveHandlingAgent_hawbNull_fallbackToTransaction() { ... }
@Test void resolveHandlingAgent_bothNull_returnsNull() { ... }
```

- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — if hawbAgentId → `resolvePartnerById(hawbAgentId)`, else fallback `transactionRef.handlingAgent*`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveHandlingAgent`

---

## Task 6: Remove TransactionsCDCHandler.saveDraftHouseBill

- [ ] **Step 1: Remove method + call site** — update `saveTransportPlan` signature to resolve HouseBill inline
- [ ] **Step 2: Run existing tests → verify nothing broken**
- [ ] **Step 3: Commit** `refactor(cdc): remove saveDraftHouseBill from TransactionsCDCHandler`

---

## Task 7: TransactionsCDCHandler — populate handlingAgentPartnerId

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Replace label-only mapping** with `lookupSupport.resolveHandlingAgent` → set both `id` and `label`
- [ ] **Step 3: Build + run tests**
- [ ] **Step 4: Commit** `feat(cdc): populate Transaction.handlingAgentPartnerId via lookup`

---

## Task 8: Refactor TransactionDetailsCDCHandler.upsert

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Rewrite `upsert(data)` body** — add lock, transaction/client/saleman lookup, remove cargo weight writes
- [ ] **Step 3: Build + run tests**
- [ ] **Step 4: Commit** `refactor(cdc): TransactionDetails uses HouseBillLookupSupport + ownership matrix`

---

## Task 9: Refactor HAWBCDCHandler.enrichHouseBill

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Rewrite `enrichHouseBill`** — add lock, cargo weights, consigned date, handling agent + assignee lookup
- [ ] **Step 3: Build**
- [ ] **Step 4: Commit** `refactor(cdc): HAWB handler enriches HouseBill with lookups + lock`

---

## Task 10: Integration tests (4 scenarios)

Create: `HouseBillCDCIntegrationIT.java` (Testcontainers Postgres)

- [ ] **Step 1: Write 4 test methods**
  1. `fullHappyPath_allFieldsPopulated`
  2. `hawbBeforeTransactionDetails_enrichSkipped`
  3. `transactionDetailsBeforeTransactions_transactionIdNull`
  4. `ownershipEnforced_hawbDoesNotOverwriteTDFields`
- [ ] **Step 2: Run IT**
- [ ] **Step 3: Fix failures iteratively**
- [ ] **Step 4: Commit** `test(cdc): integration tests for HouseBill CDC ownership + ordering`

---

## Task 11: Update mapping doc

- [ ] **Step 1: Update `of1_fms_house_bill` section** in `docs/references/mapping/mapping-transactions.md` with ownership matrix
- [ ] **Step 2: Commit** `docs(mapping): update house_bill ownership matrix`

---

## Task 12: Final verification

- [ ] **Step 1: Full module build + test** — `./gradlew :module-transaction:build`
- [ ] **Step 2: Manual smoke check** (optional)
- [ ] **Step 3: Push branch**
- [ ] **Step 4: Open PR** — `feat(cdc): HouseBill CDC completeness with ownership matrix`

---

## Plan notes

- Task 1–5: build `HouseBillLookupSupport` via strict TDD (one method per task).
- Task 6: remove legacy draft path **before** new handlers use lookup.
- Task 7: fix prerequisite (`handlingAgentPartnerId` must be populated for HAWB fallback).
- Task 8–9: wire lookup into surviving handlers.
- Task 10: single IT file with 4 scenarios (limit test container startup overhead).
- All changes are code-only; no Liquibase migration required.

---

# Appendix

## HPS Typo Reference

| HPS Column | Nghĩa gốc |
|---|---|
| `Starus` | Status |
| `TpyeofService` | TypeOfService |
| `CussignedDate` | ConsignedDate |
| `Noofpieces` | NoOfPieces |
| `FlghtNo` | FlightNo |
| `Pieaces` | Pieces |

## Field dễ nhầm lẫn

### `masterBillNo` vs `originalMasterBillNo` (OMB)
- `masterBillNo` (← MAWB): số MBL/MAWB hiện tại (có thể đã amended).
- `originalMasterBillNo` (← OMB): số MBL gốc ban đầu trước khi amend.
- Thường giống nhau. Khác khi carrier issue correction/amendment.

### `toLocationLabel` (POD) vs `finalDestination` (Destination)
- `toLocationLabel` (← PortofUnlading): cảng dỡ hàng (port/airport level).
- `finalDestination` (← Destination): địa chỉ giao cuối cùng (warehouse, door, ICD).
- Ví dụ: POD = "Cat Lai Port", finalDestination = "KCN Binh Duong, Lot A1-5".

### `mblType` (OtherInfo) — giá trị phổ biến
- "Original" — vận đơn gốc (cần surrender để nhận hàng).
- "Surrendered" — đã surrender (nhận hàng bằng bản copy).
- "Seaway Bill" — vận đơn điện tử (không cần surrender).
- "Express Release" — giải phóng nhanh (telex release).

---

---

# E. Schema Mismatch — CDC MSSQL → PostgreSQL

## E.1 Bối cảnh: Tại sao schema không khớp?

### Hệ thống cũ (HPS BFS One — MSSQL)

Thiết kế **flat**: bảng `Transactions` chứa mọi thứ — cả thông tin master bill lẫn thông tin per-HAWB.

```
dbo.Transactions (MSSQL)
├── TransID, TransDate, MAWB, PortofLading...     ← master-level (đúng)
├── BookingNo, BookingRequestNotes, PaymentTerm    ← per-HAWB (lẫn vào)
├── ExpressNotes, Remark                           ← per-HAWB (lẫn vào)
├── Ref (manifest)                                 ← sea-specific (lẫn vào)
└── GrossWeight, Noofpieces, Description           ← aggregate summary
```

Lý do: HPS không phân biệt master vs house bill. Mỗi transaction thường chỉ có 1 HAWB, nên mọi thứ gom vào 1 bảng cho tiện.

### Hệ thống mới (FMS — PostgreSQL)

Thiết kế **normalized**: tách rõ 3 tầng.

```
of1_fms_transactions          ← Master Bill (1 lô hàng)
    └── of1_fms_house_bill    ← House Bill (1:N HAWB per master)
        └── of1_fms_*_house_bill_detail  ← Chi tiết theo loại dịch vụ (air/sea/truck/logistics)
```

### Vấn đề phát sinh

Khi CDC đồng bộ data từ MSSQL → PostgreSQL:
- Một số field trên `Transactions` **không thuộc về** `of1_fms_transactions` trong schema mới
- Nhưng entity đích (`HouseBill`, `SeaHouseBillDetail`) **chưa tồn tại** tại thời điểm CDC event đến
- Kết quả: field bị ghi vào entity sai, hoặc bị mất

---

## E.2 Ba vấn đề cụ thể

### Vấn đề 1: Field per-HAWB mắc kẹt trên Transaction

**Hiện trạng**: 5 field sau đây nằm trên `Transaction.java` nhưng **không tồn tại trên `HouseBill.java`**:

| Field | MSSQL source | Tại sao thuộc HouseBill? |
|---|---|---|
| `bookingNo` | `Transactions.BookingNo` | Mỗi HAWB có booking riêng với carrier |
| `bookingRequestNote` | `Transactions.BookingRequestNotes` | Ghi chú đặt chỗ là per-customer, per-HAWB |
| `paymentTerm` | `Transactions.PaymentTerm` | HAWB A có thể Prepaid, HAWB B có thể Collect |
| `note` | `Transactions.ExpressNotes` | Ghi chú trên bill — mỗi HAWB khác nhau |
| `remark` | `Transactions.Remark` | Ghi chú nội bộ — mỗi HAWB khác nhau |

**Ví dụ thực tế**:
```
Transaction BIHCM008238/25 (Sea Export)
├── HAWB-001: client ABC, paymentTerm = Prepaid, bookingNo = BK-001
├── HAWB-002: client XYZ, paymentTerm = Collect, bookingNo = BK-002
└── Transaction.paymentTerm = "Prepaid" ← GIÁ TRỊ CỦA AI? Ambiguous!
```

Khi chỉ có 1 HAWB → không thấy vấn đề. Khi có 2+ HAWB → data mâu thuẫn.

**Bằng chứng trong code**: `Transaction.java` line 215, 228 có comment:
```java
// REMIND: Dan - review with a Quy move to House Bill entity
```

**Hậu quả**:
- UI hiển thị paymentTerm/bookingNo ở detail view → đọc từ Transaction → sai khi có nhiều HAWB
- Không thể filter/search theo paymentTerm per-HAWB
- Data integrity: HouseBill entity thiếu thông tin quan trọng

### Vấn đề 2: Field sea-specific mắc kẹt trên Transaction

**Hiện trạng**: `manifestNo` (`Transactions.Ref`) nằm trên `Transaction.java`.

| Field | MSSQL source | Nên thuộc về |
|---|---|---|
| `manifestNo` | `Transactions.Ref` | `SeaHouseBillDetail.manifestNo` |

**Tại sao sai?**
- Manifest number chỉ có ý nghĩa với **sea shipment** (không phải air/truck/logistics)
- Trong schema mới, nó thuộc `SeaHouseBillDetail` — entity con chuyên biệt cho sea
- `HAWBDETAILSCDCHandler` đã set đúng `manifestNo` trên `SeaHouseBillDetail` (từ `HAWBDETAILS`)
- Nhưng `Transaction` cũng giữ 1 bản copy riêng → 2 nguồn, dễ inconsistent

**Hậu quả**: Nhẹ hơn vấn đề 1 vì `SeaHouseBillDetail` đã có field này. Nhưng `Transaction.manifestNo` là bản copy thừa, gây confusion cho developer.

### Vấn đề 3: Field duplicate OK nhưng cần hiểu rõ vai trò

**Hiện trạng**: 6 field tồn tại trên CẢ `Transaction` VÀ `HouseBill`, mỗi bên set bởi handler khác nhau.

| Field | Transaction (aggregate) | HouseBill (per-HAWB) |
|---|---|---|
| `descOfGoods` | `Transactions.Description` | `TransactionDetails.Description` |
| `cargoGrossWeightInKgs` | `Transactions.GrossWeight` | `HAWB.GrossWeight` |
| `cargoVolumeInCbm` | `Transactions.Dimension` | `HAWB.Dimension` |
| `cargoChargeableWeightInKgs` | `Transactions.ChargeableWeight` | `HAWB.ChargeableWeight` |
| `packageQuantity` | `Transactions.Noofpieces` | `HAWB.Pieces` |
| `packagingType` | `Transactions.UnitPieaces` | `TransactionDetails.UnitDetail` |

**Kết luận: KHÔNG phải vấn đề.**
- Transaction giữ tổng số (aggregate of all HAWBs)
- HouseBill giữ chi tiết per-HAWB
- 2 handler set độc lập, mỗi bên có data source riêng
- Mô hình master-detail chuẩn

---

## E.3 Gốc rễ: Timing mismatch trong CDC pipeline

Tại sao Vấn đề 1 & 2 xảy ra? Vì thứ tự CDC events:

```
T0  Transactions INSERT (MSSQL)
    → TransactionsCDCHandler chạy
    → Transaction entity CREATED ✅
    → HouseBill CHƯA TỒN TẠI ❌
    → bookingNo, note, remark... GHI LÊN TRANSACTION (đành vậy)

T1  TransactionDetails INSERT (MSSQL, vài ms sau)
    → TransactionDetailsCDCHandler chạy
    → HouseBill skeleton CREATED ✅
    → NHƯNG KHÔNG KÉO bookingNo/note/remark TỪ TRANSACTION XUỐNG ❌

T2  HAWB INSERT (MSSQL)
    → HAWBCDCHandler chạy
    → HouseBill enriched (weights, consignee, agent...) ✅
    → VẪN KHÔNG KÉO bookingNo/note/remark XUỐNG ❌

T3  HAWBDETAILS INSERT (MSSQL)
    → HAWBDETAILSCDCHandler chạy
    → SeaHouseBillDetail CREATED, manifestNo SET ✅ (từ HAWBDETAILS riêng)
```

**Gap rõ ràng**: Không có bước nào propagate 5 field Loại 1 từ Transaction → HouseBill.

**Tại sao gap này tồn tại?**
- Ban đầu code xử lý đúng thứ tự: Transaction ghi trước, HouseBill ghi sau
- Nhưng 5 field per-HAWB bị "mắc kẹt" trên Transaction vì HouseBill entity ban đầu không có các field này
- Không ai thêm bước propagation vì HouseBill.java chưa có columns để nhận

---

## E.4 Năm giải pháp

### Giải pháp A — Propagation đơn giản (Quick fix)

**Tư tưởng**: Giữ nguyên mọi thứ. Chỉ thêm field vào HouseBill + thêm logic copy data.

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity
        bookingNo, bookingRequestNote, paymentTerm, note, remark

Bước 2: TransactionDetailsCDCHandler (T1) — khi tạo HouseBill:
        → Đọc parent Transaction
        → Copy 5 fields xuống HouseBill (nếu HouseBill chưa có giá trị)

Bước 3: TransactionsCDCHandler (T0) — khi Transaction UPDATE:
        → Tìm HouseBills đã tồn tại
        → Push 5 fields xuống (nếu HouseBill chưa có giá trị)
```

**Transaction entity**: GIỮ NGUYÊN 5 field (backward compatible).

**Ưu điểm**: Effort thấp nhất, risk thấp nhất, backward compatible.
**Nhược điểm**: Data duplicate — 5 fields tồn tại trên CẢ Transaction VÀ HouseBill. Phải đồng bộ khi update. Developer dễ nhầm "đọc từ đâu mới đúng?"

---

### Giải pháp B — Propagation + Ownership documentation

**Tư tưởng**: Giống A, nhưng thêm convention rõ ràng cho developer biết field nào là "bản gốc" vs "bản copy".

**Cách làm**: Giống A, cộng thêm:

```java
// Transaction.java — đánh dấu field là copy
/** @denorm Source of truth: HouseBill.bookingNo. Copy for list/search perf. */
private String bookingNo;

/** @denorm Source of truth: HouseBill.paymentTerm. Copy for list/search perf. */
private FreightTerm paymentTerm;
```

**Quy tắc đọc**:
- **Detail view** (xem chi tiết 1 transaction): đọc từ HouseBill (source of truth)
- **List view** (danh sách): đọc từ Transaction (denormalized, nhanh)

**Ưu điểm**: Developer biết rõ "cái nào là gốc, cái nào là copy". Giảm confusion.
**Nhược điểm**: Convention-based — phụ thuộc vào kỷ luật team. Nếu developer mới không đọc comment → vẫn nhầm.

---

### Giải pháp C — Xóa field sai khỏi Transaction + staging buffer

**Tư tưởng**: "Dọn sạch" Transaction entity. Transaction chỉ chứa đúng master-level data. HAWB-level fields chỉ tồn tại trên HouseBill.

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity

Bước 2: XÓA 5 columns khỏi Transaction entity

Bước 3: Khi Transactions CDC đến (T0) mà HouseBill chưa có:
        → Lưu 5 fields vào bảng staging: of1_fms_cdc_pending_fields
          (transaction_code, field_name, field_value, created_at)

Bước 4: Khi TransactionDetails CDC đến (T1) và tạo HouseBill:
        → Check pending_fields cho transaction này
        → Apply lên HouseBill
        → Xóa pending records

Bước 5: DB migration: chuyển data cũ từ Transaction → HouseBill, drop columns
```

**Ưu điểm**: Schema sạch nhất. Không duplicate. Không ambiguous.
**Nhược điểm**: Effort cao. Cần migration + bảng staging mới. UI/API phải đổi query source. Risk medium.

---

### Giải pháp D — CQRS: Dùng IntegratedTransaction làm Read Model (Recommended long-term)

**Insight quan trọng**: Project ĐÃ CÓ `IntegratedTransaction` — entity denormalized song song, chứa MỌI field (cả master lẫn HAWB-level). Đây chính là **Read Model** trong pattern CQRS, chỉ chưa được commit vào vai trò đó.

**Hiện tại `Transaction` đang đóng 2 vai:**
1. Write Model (domain entity, normalized) — vai trò đúng
2. Read Model (denormalized, cho UI list/search) — vai trò sai, nên là IntegratedTransaction

**Tư tưởng**: Tách rõ 2 vai. Transaction chỉ làm Write Model. IntegratedTransaction làm Read Model.

```
┌─────────────────────────────────────────────────────────────┐
│                    WRITE MODEL (Normalized)                  │
│                                                             │
│  Transaction                    HouseBill                   │
│  ├── code                       ├── hawbNo                  │
│  ├── masterBillNo               ├── bookingNo         NEW   │
│  ├── fromLocationCode           ├── bookingRequestNote NEW  │
│  ├── toLocationCode             ├── paymentTerm        NEW  │
│  ├── loadingDate                ├── note               NEW  │
│  ├── arrivalDate                ├── remark             NEW  │
│  ├── typeOfService              ├── clientPartnerId         │
│  ├── status                     ├── cargoGrossWeight...     │
│  ├── carrierPartnerId           └── ...                     │
│  ├── cargoGrossWeight (agg)                                 │
│  └── ...                        SeaHouseBillDetail          │
│  ❌ KHÔNG CÒN: bookingNo,      ├── manifestNo (SOT)        │
│     paymentTerm, note, remark   └── ...                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    READ MODEL (Denormalized)                 │
│                                                             │
│  IntegratedTransaction (ĐÃ CÓ SẴN)                        │
│  ├── transactionId, transactionDate, etd, eta               │
│  ├── typeOfService, status, manifestNo                      │
│  ├── bookingRequestNote, paymentTerm, remark    ← ĐÃ CÓ    │
│  ├── fromLocationCode, toLocationCode                       │
│  ├── coloaderLabel, handlingAgentLabel                      │
│  └── ... (tất cả field gộp lại cho list/search/report)     │
│                                                             │
│  IntegratedHousebill (ĐÃ CÓ SẴN)                          │
│  ├── hawbNo, transactionId, customerName                    │
│  ├── hawbGw, hawbCw, hawbCbm                                │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity

Bước 2: XÓA 5 columns + manifestNo khỏi Transaction entity

Bước 3: IntegratedTransaction GIỮ NGUYÊN (nó đã có sẵn tất cả field)

Bước 4: CDC handlers:
        TransactionsCDCHandler:
          → Set master fields lên Transaction (không còn HAWB fields)
          → Set TẤT CẢ fields lên IntegratedTransaction (như cũ)
          → Nếu HouseBill đã tồn tại → propagate HAWB fields xuống

        TransactionDetailsCDCHandler:
          → Tạo HouseBill skeleton
          → Pull HAWB fields từ IntegratedTransaction (buffer tự nhiên!)
            IntegratedTransaction đã nhận data từ T0 → không cần staging table

Bước 5: UI/API queries:
        - List/search → IntegratedTransaction (denormalized, nhanh)
        - Detail view → Transaction JOIN HouseBill (normalized, chính xác)
```

**Xử lý timing — IntegratedTransaction là buffer tự nhiên:**

```
T0  Transactions CDC
    → Transaction: chỉ set master fields ✅
    → IntegratedTransaction: set TẤT CẢ fields (kể cả bookingNo, remark...) ✅
    → HouseBill chưa có? OK, không sao — data đã an toàn trong IntegratedTransaction

T1  TransactionDetails CDC
    → HouseBill skeleton CREATED ✅
    → Pull bookingNo, remark... từ IntegratedTransaction → set lên HouseBill ✅
    → Data không bị mất!
```

**Ưu điểm**:
- Schema domain sạch nhất — Transaction chỉ chứa master-level
- Không cần bảng staging mới — IntegratedTransaction đã đóng vai trò buffer
- Tận dụng 100% infra có sẵn
- UI list/search không đổi gì — đã đọc IntegratedTransaction
- Rõ ràng về mặt kiến trúc: Write Model vs Read Model

**Nhược điểm**:
- Cần migration xóa columns trên Transaction
- Detail API phải đổi source (Transaction → Transaction + HouseBill join)
- IntegratedTransaction fail → HouseBill thiếu data (nhưng IntegratedTransaction đã ổn định)

---

### Giải pháp E — CDC Deferred Event Queue (generic infra)

**Tư tưởng**: Giải quyết timing ở tầng infrastructure. Bất kỳ CDC event nào mà target entity chưa sẵn sàng → lưu vào queue → tự động replay khi target có.

**Khi nào cần**: Khi CDC mở rộng thêm nhiều bảng source và timing issues trở nên pattern phổ biến (không chỉ 5 fields hiện tại).

```sql
CREATE TABLE of1_fms_cdc_deferred_event (
    id          BIGSERIAL PRIMARY KEY,
    event_key   VARCHAR(100) NOT NULL,   -- "housebill:BIHCM008238/25"
    handler     VARCHAR(100) NOT NULL,   -- "TransactionsCDCHandler"
    field_group VARCHAR(50)  NOT NULL,   -- "hawb_level_fields"
    payload     JSONB        NOT NULL,   -- subset CDC data
    created_at  TIMESTAMP    DEFAULT NOW(),
    processed   BOOLEAN      DEFAULT FALSE,
    processed_at TIMESTAMP
);
```

**Flow:**

```
T0: Transactions CDC → TransactionsCDCHandler
    ├─ Set master fields lên Transaction ✅
    ├─ HouseBill exists?
    │   ├─ YES → set HAWB fields trực tiếp ✅
    │   └─ NO  → INSERT deferred_event (payload = {bookingNo, remark...}) ⏳
    └─ Set IntegratedTransaction ✅

T1: TransactionDetails CDC → TransactionDetailsCDCHandler
    ├─ Create HouseBill ✅
    ├─ Query deferred_event WHERE event_key matches
    │   └─ Found → apply payload lên HouseBill, mark processed ✅
    └─ Done
```

**Ưu điểm**:
- Generic — giải quyết MỌI timing mismatch, không chỉ 5 fields
- Domain model sạch
- Audit trail: biết event nào bị deferred, bao lâu
- Retry-safe: data không mất

**Nhược điểm**:
- Thêm bảng + logic mới
- HouseBill thiếu data tạm thời (vài giây)
- Cần monitor expired events
- Over-engineering nếu chỉ cần cho 5 fields

---

## E.5 So sánh tổng thể

| Tiêu chí | A | B | C | D | E |
|---|---|---|---|---|---|
| **Tên** | Propagation | + Ownership docs | Xóa + Buffer | CQRS | Deferred Queue |
| **Effort** | Thấp | Thấp-TB | Cao | Trung bình | Trung bình |
| **Risk** | Thấp | Thấp | Cao | TB | Thấp |
| **Schema sạch?** | Không (duplicate) | Không (documented duplicate) | Sạch | **Sạch nhất** | Sạch |
| **Backward compatible?** | 100% | 100% | Không | Phần lớn | 100% |
| **Dùng infra sẵn?** | Dùng | Dùng | Không | **Tốt nhất** | Không |
| **Giải timing generic?** | Chỉ 5 fields | Chỉ 5 fields | Chỉ 5 fields | Phần lớn | **Tất cả** |

**Khi nào dùng?**

| Giải pháp | Giai đoạn phù hợp | Điều kiện |
|---|---|---|
| A | Ngay bây giờ | Cần unblock CDC migration nhanh |
| B | Sau A | Team cần convention rõ ràng |
| C | Refactor lớn | Quyết định xóa technical debt triệt để |
| D | Khi ổn định | Muốn kiến trúc sạch, tận dụng IntegratedTransaction |
| E | Khi scale CDC | Timing issues xuất hiện ở nhiều bảng khác |

## E.6 Lộ trình khuyến nghị

```
Phase 1 (Now)   ─── A: Thêm 5 fields vào HouseBill + propagation logic
                     → Unblock CDC. Effort: 1-2 ngày. Risk: thấp.

Phase 2 (Soon)  ─── D: CQRS cleanup
                     → Xóa 5 fields + manifestNo khỏi Transaction
                     → IntegratedTransaction làm Read Model chính thức
                     → Kết hợp B (ownership docs) cho bất kỳ field nào còn duplicate
                     → Effort: 3-5 ngày. Risk: trung bình.

Phase 3 (If needed) ─ E: Deferred Queue
                     → Chỉ khi CDC thêm 5+ bảng source mới
                     → Timing issues trở thành pattern phổ biến
                     → Effort: 2-3 ngày.
```

**Tại sao D là đích đến tốt nhất?**
1. IntegratedTransaction **ĐÃ TỒN TẠI** — đó chính là Read Model, chỉ cần chính thức hóa vai trò
2. Transaction entity trở về đúng vai domain model — sạch, dễ test, không ambiguous
3. Không cần bảng mới (khác C, E)
4. IntegratedTransaction đã nhận TẤT CẢ data từ T0 → đóng vai buffer tự nhiên cho timing issue
5. UI list/search đã đọc từ IntegratedTransaction → không đổi gì

**Nguyên tắc kiến trúc (áp dụng cho toàn bộ CDC pipeline):**

| Entity | Vai trò | Quy tắc |
|---|---|---|
| `Transaction` | Write Model, aggregate root | Chỉ master-level: code, MBL, ports, dates, carrier, status |
| `HouseBill` | Write Model, source of truth per-HAWB | Tất cả per-HAWB: client, booking, payment, notes, cargo |
| `*HouseBillDetail` | Write Model, service-specific | manifestNo (sea), truckNo (truck), cdsNo (logistics) |
| `IntegratedTransaction` | Read Model, denormalized | Gộp tất cả cho list/search/report. Chấp nhận eventual consistency |
| `IntegratedHousebill` | Read Model, denormalized | Gộp HAWB-level cho report |

---

## Liên quan

- [[260406-cdc-handler-refactor]] — Refactor CDC handler trước đó
- [[260406-cdc-handler-refactor-plan]] — Plan refactor CDC
- [[260407-customs-receipt-bot-v5-design]] — Customs receipt bot

---

## FMS Transaction Search Bar — Design Spec


## Overview

Add a search bar panel to `UIMainWindow` that allows users to search transactions by multiple criteria with server-side search. The search bar supports two view modes (Full and Compact) with a toggle button to switch between them.

## Requirements

### Search Criteria

| Field | Type | Options |
|-------|------|---------|
| Search By | Radio (Full) / Dropdown (Compact) | Job ID (default), POL, POD, H-B/L No, M-B/L No, Booking No, Vessel/Flight, Container/Seal, Other |
| Document Type | Dropdown | Cargo Manifest (default) — UI placeholder for future backend support |
| Branch/Office | Dropdown | Maps to `companyId` filter. Options loaded from user context. |
| Search Value | Text input | Free text |
| Date Range | Date inputs + presets | From/To with WDateRangeFilter presets (Today, YTD, This Week, etc.) |

**Removed from Phase 1** (no backing entity fields): CDs Number, CDs Invoice, Issued Invoice. These can be added in Phase 2 when backend schema supports them.

### Checkbox Options

| Checkbox | Default | Behavior |
|----------|---------|----------|
| Hide Result After Click View Detail | unchecked | UI-only: closes list panel after opening detail tab |
| Shipment Finish | unchecked | Backend filter: filters by `status = 'DELIVERED' or 'CLOSED'` |
| Shipment Changed | unchecked | Backend filter: filters by `modifiedTime > transactionDate` |
| Disable Notification | unchecked | UI-only: suppresses toast notifications during search |
| Auto Login | unchecked | UI-only: persists search session across page reloads |

### View Modes

- **Full (Option A)**: 3-row compact horizontal layout. Row 1: Search By radio buttons. Row 2: Doc Type, Branch, Search Value, Date Range, Apply button. Row 3: Checkboxes. Recommended for wide screens.
- **Compact (Option C)**: Single-row minimal layout. Search By as dropdown, Search Value, Date Range, Search button, Advanced popover for other options. Recommended for HD/narrow screens.
- Toggle button in top-right corner to switch between modes.

## Architecture

### New Component: `WTransactionSearchBar`

**File**: `webui/fms/src/app/fms/transaction/WTransactionSearchBar.tsx`

**Props**:
```typescript
interface WTransactionSearchBarProps extends app.AppComponentProps {
  plugin: UITransactionListPlugin;
  onApplySearch: () => void;
}
```

**State**:
```typescript
interface WTransactionSearchBarState {
  searchBy: string;        // 'JOB_ID' | 'POL' | 'POD' | 'HAWB' | 'MAWB' | 'BOOKING' | 'VESSEL_FLIGHT' | 'CONTAINER_SEAL' | 'OTHER'
  docType: string;         // 'CARGO_MANIFEST' (Phase 1: UI-only, no backend filter)
  branch: string;          // companyId value from user context
  searchValue: string;
  dateFilter: DateRangeBean;
  hideResultAfterView: boolean;
  shipmentFinish: boolean;
  shipmentChanged: boolean;
  disableNotification: boolean;
  autoLogin: boolean;
  viewMode: 'full' | 'compact';
}
```

**Behavior**:
- `onApplySearch()`: Builds search params from state, updates plugin filters, calls `onApplySearch` prop which triggers `reloadData()` on the list.
- Toggle button switches `viewMode` between 'full' and 'compact'.
- Date range reuses existing `WDateRangeFilter` component.

### Plugin Extension: `UITransactionListPlugin`

Add methods to accept new search criteria:

```typescript
withSearchBy(searchBy: string, searchValue: string): UITransactionListPlugin
withOptions(options: { shipmentFinish?: boolean; shipmentChanged?: boolean }): UITransactionListPlugin
```

The `withSearchBy` method updates `this.searchParams.filters` to replace the generic `AND_SEARCH_BY_PARAMS` with a field-specific filter based on the `searchBy` value. For searches that require JOINs (H-B/L, Container/Seal), this adds a `customFilter` entry that the backend Groovy SQL template consumes.

### Modified: `UIMainView.tsx`

Plugin and ref must be class-level fields (not recreated in `render()`):

```typescript
export class UIMainWindow extends app.AppComponent<UIMainWindowProps, UIMainWindowState> {
  private transactionPlugin = new UITransactionListPlugin();
  private listRef = React.createRef<UITransactionList>();

  render(): React.ReactNode {
    const { appContext, pageContext } = this.props;

    return (
      <div className='flex-vbox'>
        <WTransactionSearchBar
          appContext={appContext} pageContext={pageContext}
          plugin={this.transactionPlugin}
          onApplySearch={() => this.listRef.current?.reloadData()}
        />
        <div className='flex-vbox' style={{ flex: 1 }}>
          <UITransactionList ref={this.listRef}
            appContext={appContext} pageContext={pageContext}
            plugin={this.transactionPlugin} />
        </div>
      </div>
    );
  }
}
```

### Modified: `UITransactionList`

- The existing `renderHeaderBar()` with `WStringInput` and `WDateRangeFilter` will be **hidden** when used inside `UIMainView` (since `WTransactionSearchBar` replaces it). Add a `hideHeaderBar` prop to control this.
- When used standalone (without UIMainView), the existing header bar remains.

## Data Flow

1. User fills search criteria in `WTransactionSearchBar`
2. User clicks "Apply Search"
3. `WTransactionSearchBar.onApplySearch()` calls plugin methods to update `searchParams`
4. Calls `onApplySearch` prop -> `UITransactionList.reloadData()`
5. Plugin's `loadData()` sends updated `searchParams` to `TransactionService.searchTransactions`
6. Backend Groovy SQL processes field-specific filter via `AND_SEARCH_BY_PARAMS` or custom filter
7. Backend returns filtered results, grid re-renders

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `webui/fms/src/app/fms/transaction/WTransactionSearchBar.tsx` | CREATE | New search bar component with dual view modes |
| `webui/fms/src/app/fms/transaction/UIMainView.tsx` | MODIFY | Integrate WTransactionSearchBar above UITransactionList |
| `webui/fms/src/app/fms/transaction/UITransactionList.tsx` | MODIFY | Extend UITransactionListPlugin with new filter methods; add hideHeaderBar prop |
| `webui/fms/src/app/fms/transaction/index.tsx` | MODIFY | Export WTransactionSearchBar |
| `module/transaction/.../groovy/TransactionSql.groovy` | MODIFY | Add field-specific search support (searchBy discriminator in WHERE clause) |

## Search By Field Mapping

| Search By | Backend Entity | Field | Requires JOIN | Notes |
|-----------|---------------|-------|---------------|-------|
| Job ID | Transaction | `code` | No | Direct match on `t.code` |
| POL | Transaction | `fromLocationLabel` | No | Direct match on `t.from_location_label` |
| POD | Transaction | `toLocationLabel` | No | Direct match on `t.to_location_label` |
| H-B/L No | HouseBill | `hawbNo` | Yes | JOIN `of1_fms_house_bills hb ON hb.transaction_id = t.id` |
| M-B/L No | Transaction | `masterBillNo` | No | Direct match on `t.master_bill_no` |
| Booking No | Transaction | `bookingNo` | No | Direct match on `t.booking_no` |
| Vessel/Flight | Transaction | `transportName` + `transportNo` | No | LIKE on `t.transport_name` OR `t.transport_no` |
| Container/Seal | Container | `containerNo` + `sealNo` | Yes | JOIN `of1_fms_containers c ON c.transaction_id = t.id` |
| Other | Transaction | (multiple) | No | Existing `AND_SEARCH_BY_PARAMS` across code, masterBillNo, typeOfService, carrierLabel, fromLocationLabel, toLocationLabel |

### Backend Groovy Changes (TransactionSql.groovy)

The `SearchTransactions` query needs a new optional parameter `searchByField` that, when present, replaces `AND_SEARCH_BY_PARAMS` with a field-specific WHERE clause:

```groovy
// When searchByField is set, use targeted search instead of generic AND_SEARCH_BY_PARAMS
if (params.searchByField == 'HAWB') {
  // Add LEFT JOIN to house_bills and filter by hawb_no
} else if (params.searchByField == 'CONTAINER_SEAL') {
  // Add LEFT JOIN to containers and filter by container_no or seal_no
} else if (params.searchByField) {
  // Direct field match on transaction table
} else {
  // Default: existing AND_SEARCH_BY_PARAMS behavior
}
```

## UI Specifications

- Font sizes: labels 10px, inputs 12px, radio/checkbox text 11-12px
- Input height: 30px consistent
- Colors: Primary blue #0d6efd for Apply button and selected radio, Gray #6c757d for labels
- Row 3 background: #f8f9fa (subtle gray)
- Spacing: 8px gap between inputs, 16px gap between checkboxes

## Phase 2 (Future)

- Add CDs Number, CDs Invoice, Issued Invoice search-by options (requires new entity fields)
- Document Type backend filter support
- Save/load search presets

---

## FMS Transaction Search Bar — Implementation Plan


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a search bar panel to UIMainWindow with 9 search-by options, date range, checkboxes, and two switchable view modes (Full 3-row / Compact 1-row).

**Architecture:** New `WTransactionSearchBar` component manages search state and delegates to the existing `UITransactionListPlugin` which sends server-side search params to `TransactionService.searchTransactions`. Backend Groovy SQL is extended with field-specific WHERE clauses and optional JOINs for cross-entity searches (HouseBill, Container). Parameters are passed as top-level properties on `searchParams`, accessed via `sqlParams.get()` in Groovy (same pattern as `IntegratedHousebillSql.groovy`).

**Tech Stack:** React 18 (class components), TypeScript, @of1-webui/lib (bs, input, entity, app, sql, util), Groovy SQL templates

**Spec:** `~/dev/wiki/wiki/daily/260413-fms-search-bar-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `module/transaction/.../groovy/TransactionSql.groovy` | MODIFY | Add `searchByField` + `searchByValue` params, shipmentFinish/Changed filters |
| `webui/fms/src/app/fms/transaction/UITransactionList.tsx` | MODIFY | Extend plugin with `withSearchBy()`, `withOptions()`; add `hideHeaderBar` prop |
| `webui/fms/src/app/fms/transaction/WTransactionSearchBar.tsx` | CREATE | Search bar component with Full/Compact view modes |
| `webui/fms/src/app/fms/transaction/UIMainView.tsx` | MODIFY | Integrate `WTransactionSearchBar` above `UITransactionList` |
| `webui/fms/src/app/fms/transaction/index.tsx` | MODIFY | Export `WTransactionSearchBar` |

---

### Task 1: Extend Backend Groovy SQL — Field-Specific Search

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/groovy/TransactionSql.groovy`

- [ ] **Step 1: Replace `SearchTransactions` class**

The current query uses `AND_SEARCH_BY_PARAMS` across 6 fixed columns. We add an alternative path when `searchByField` is provided via `sqlParams.get()` (same pattern as `IntegratedHousebillSql.groovy` line 57).

Replace the entire `SearchTransactions` inner class:

```groovy
public class SearchTransactions extends ExecutableSqlBuilder {
  public Object execute(ApplicationContext appCtx, ExecutableContext ctx) {
    MapObject sqlParams = ctx.getParam("sqlParams");

    String searchByField = sqlParams.get("searchByField") ?: null
    String searchByValue = sqlParams.get("searchByValue") ?: null

    String joinClause = ""
    String searchClause = ""
    String selectKeyword = "SELECT"

    if (searchByField && searchByField != "OTHER" && searchByValue && searchByValue.trim()) {
      String safeValue = searchByValue.replace("'", "''")

      switch (searchByField) {
        case "JOB_ID":
          searchClause = "AND LOWER(t.code) LIKE LOWER('%" + safeValue + "%')"; break
        case "POL":
          searchClause = "AND LOWER(t.from_location_label) LIKE LOWER('%" + safeValue + "%')"; break
        case "POD":
          searchClause = "AND LOWER(t.to_location_label) LIKE LOWER('%" + safeValue + "%')"; break
        case "MAWB":
          searchClause = "AND LOWER(t.master_bill_no) LIKE LOWER('%" + safeValue + "%')"; break
        case "BOOKING":
          searchClause = "AND LOWER(t.booking_no) LIKE LOWER('%" + safeValue + "%')"; break
        case "VESSEL_FLIGHT":
          searchClause = "AND (LOWER(t.transport_name) LIKE LOWER('%" + safeValue + "%') OR LOWER(t.transport_no) LIKE LOWER('%" + safeValue + "%'))"; break
        case "HAWB":
          joinClause = "LEFT JOIN of1_fms_house_bills hb ON hb.transaction_id = t.id"
          searchClause = "AND LOWER(hb.hawb_no) LIKE LOWER('%" + safeValue + "%')"
          selectKeyword = "SELECT DISTINCT"
          break
        case "CONTAINER_SEAL":
          joinClause = "LEFT JOIN of1_fms_containers c ON c.transaction_id = t.id"
          searchClause = "AND (LOWER(c.container_no) LIKE LOWER('%" + safeValue + "%') OR LOWER(c.seal_no) LIKE LOWER('%" + safeValue + "%'))"
          selectKeyword = "SELECT DISTINCT"
          break
      }
    }

    // Fall back to generic multi-column search when no field-specific search is active
    String genericSearch = (searchClause == "")
      ? AND_SEARCH_BY_PARAMS(['t.code', 't.master_bill_no', 't.type_of_service', 't.carrier_label', 't.from_location_label', 't.to_location_label'], 'search', sqlParams)
      : ""

    // Checkbox filters
    String shipmentFinishFilter = sqlParams.get("shipmentFinish") == "true"
      ? "AND t.status IN ('DELIVERED', 'CLOSED')"
      : ""
    String shipmentChangedFilter = sqlParams.get("shipmentChanged") == "true"
      ? "AND t.modified_time > t.transaction_date"
      : ""

    String query = """
      ${selectKeyword}
        t.id, t.created_by, t.created_time, t.modified_by, t.modified_time,
        t.storage_state, t.version, t.company_id,
        t.code, t.status, t.transaction_date, t.issued_date, t.loading_date, t.arrival_date,
        t.created_by_account_id, t.created_by_account_name,
        t.master_bill_no, t.type_of_service, t.shipment_type, t.incoterms,
        t.carrier_partner_id, t.carrier_label,
        t.handling_agent_partner_id, t.handling_agent_label,
        t.transport_name, t.transport_no,
        t.from_location_code, t.from_location_label,
        t.to_location_code, t.to_location_label,
        t.cargo_gross_weight_in_kgs, t.cargo_volume_in_cbm,
        t.cargo_chargeable_weight_in_kgs,
        t.package_quantity, t.packaging_type, t.container_vol,
        t.mbl_type, t.original_master_bill_no, t.final_destination,
        t.pre_alert_date, t.report_info
      FROM of1_fms_transactions t
      ${joinClause}
      WHERE
        ${FILTER_BY_STORAGE_STATE(sqlParams)}
        ${AND_FILTER_BY_RANGE('t.transaction_date', 'transactionDate', sqlParams)}
        ${AND_FILTER_BY_RANGE('t.modified_time', 'modifiedTime', sqlParams)}
        ${searchClause}
        ${genericSearch}
        ${shipmentFinishFilter}
        ${shipmentChangedFilter}
      ORDER BY t.transaction_date DESC, t.code
      ${MAX_RETURN(sqlParams)}
    """;
    return query;
  }
}
```

Key changes:
- `searchByField`/`searchByValue` read via `sqlParams.get()` (matches `IntegratedHousebillSql` pattern)
- `DISTINCT` only applied when JOINs are used (HAWB, CONTAINER_SEAL)
- Edge case: if `searchByField` is set but `searchByValue` is empty, falls back to generic search
- Shipment Finish filter: `status IN ('DELIVERED', 'CLOSED')`
- Shipment Changed filter: `modified_time > transaction_date`
- String concatenation for SQL values (matches existing codebase pattern in `IntegratedHousebillSql.groovy` line 57)

- [ ] **Step 2: Verify Java compile**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms && gradle compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 3: Commit**

```
git add module/transaction/src/main/java/of1/fms/module/transaction/groovy/TransactionSql.groovy
git commit -m "feat: add field-specific search and shipment filters to TransactionSql"
```

---

### Task 2: Extend UITransactionListPlugin + Add hideHeaderBar

**Files:**
- Modify: `webui/fms/src/app/fms/transaction/UITransactionList.tsx`

- [ ] **Step 1: Add `withSearchBy` and `withOptions` methods to `UITransactionListPlugin`**

Add after the existing `withTransactionDate` method (after line 68). These set **top-level properties** on `searchParams` (NOT inside `filters` array), so they map to `sqlParams.get()` in the Groovy SQL:

```typescript
withSearchBy(searchBy: string, searchValue: string) {
  if (!this.searchParams) return this;
  (this.searchParams as any).searchByField = searchBy;
  (this.searchParams as any).searchByValue = searchValue || '';
  return this;
}

withOptions(options: { shipmentFinish?: boolean; shipmentChanged?: boolean }) {
  if (!this.searchParams) return this;
  (this.searchParams as any).shipmentFinish = options.shipmentFinish ? 'true' : '';
  (this.searchParams as any).shipmentChanged = options.shipmentChanged ? 'true' : '';
  return this;
}
```

- [ ] **Step 2: Add `hideHeaderBar` prop to `UITransactionList`**

Replace the `render()` method (lines 238-245):

```typescript
render() {
  const { hideHeaderBar } = this.props as any;
  return (
    <div className='flex-vbox h-100'>
      {!hideHeaderBar && this.renderHeaderBar()}
      {this.renderUIGrid()}
    </div>
  );
}
```

- [ ] **Step 3: Verify frontend build**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms/webui/fms && pnpm run dev-server`
Expected: Compiles without errors. Press Ctrl+C after confirming.

- [ ] **Step 4: Commit**

```
git add webui/fms/src/app/fms/transaction/UITransactionList.tsx
git commit -m "feat: extend UITransactionListPlugin with searchBy and options filters"
```

---

### Task 3: Create WTransactionSearchBar Component

**Files:**
- Create: `webui/fms/src/app/fms/transaction/WTransactionSearchBar.tsx`

- [ ] **Step 1: Create the search bar component**

```typescript
import React from 'react';
import { app, input, bs, util } from '@of1-webui/lib';
import { WDateRangeFilter, DateRangeBean } from '../settings';
import { UITransactionListPlugin } from './UITransactionList';

const SEARCH_BY_OPTIONS = [
  { value: 'JOB_ID', label: 'Job ID' },
  { value: 'POL', label: 'POL' },
  { value: 'POD', label: 'POD' },
  { value: 'HAWB', label: 'H-B/L No' },
  { value: 'MAWB', label: 'M-B/L No' },
  { value: 'BOOKING', label: 'Booking No' },
  { value: 'VESSEL_FLIGHT', label: 'Vessel/Flight' },
  { value: 'CONTAINER_SEAL', label: 'Container/Seal' },
  { value: 'OTHER', label: 'Other' },
];

const DOC_TYPE_OPTIONS = ['Cargo Manifest', 'Bill of Lading', 'Invoice'];
const BRANCH_OPTIONS = ['HPSVN', 'HPSHCM', 'HPSHN'];

export interface WTransactionSearchBarProps extends app.AppComponentProps {
  plugin: UITransactionListPlugin;
  onApplySearch: () => void;
}

interface WTransactionSearchBarState {
  searchBy: string;
  docType: string;
  branch: string;
  searchValue: string;
  dateFilter: DateRangeBean;
  hideResultAfterView: boolean;
  shipmentFinish: boolean;
  shipmentChanged: boolean;
  disableNotification: boolean;
  autoLogin: boolean;
  viewMode: 'full' | 'compact';
}

export class WTransactionSearchBar extends app.AppComponent<WTransactionSearchBarProps, WTransactionSearchBarState> {

  constructor(props: WTransactionSearchBarProps) {
    super(props);

    const today = new Date();
    const firstDayOfYear = new Date(today.getFullYear(), 0, 1);
    const timeRange = new util.TimeRange();
    timeRange.fromSetDate(firstDayOfYear);
    timeRange.toSetDate(today);

    this.state = {
      searchBy: 'JOB_ID',
      docType: 'Cargo Manifest',
      branch: 'HPSVN',
      searchValue: '',
      dateFilter: {
        fromValue: timeRange.fromFormat(),
        toValue: timeRange.toFormat(),
        label: 'Year to Date'
      },
      hideResultAfterView: false,
      shipmentFinish: false,
      shipmentChanged: false,
      disableNotification: false,
      autoLogin: false,
      viewMode: 'full',
    };
  }

  onApplySearch = () => {
    const { plugin, onApplySearch } = this.props;
    const { searchBy, searchValue, dateFilter, shipmentFinish, shipmentChanged } = this.state;

    plugin
      .withSearchBy(searchBy, searchValue)
      .withTransactionDate(dateFilter.fromValue, dateFilter.toValue)
      .withOptions({ shipmentFinish, shipmentChanged });

    onApplySearch();
  }

  onSearchByChange = (value: string) => {
    this.setState({ searchBy: value });
  }

  onSearchValueChange = (_oldVal: any, newVal: any) => {
    this.setState({ searchValue: newVal || '' });
  }

  onDateFilterChange = (bean: DateRangeBean) => {
    this.setState({ dateFilter: bean });
  }

  onToggleViewMode = () => {
    this.setState(prev => ({
      viewMode: prev.viewMode === 'full' ? 'compact' : 'full'
    }));
  }

  onCheckboxChange = (field: keyof WTransactionSearchBarState) => {
    this.setState((prev: any) => ({ [field]: !prev[field] } as any));
  }

  renderFullView(): React.ReactNode {
    const { appContext, pageContext } = this.props;
    const { searchBy, docType, branch, searchValue, dateFilter,
      hideResultAfterView, shipmentFinish, shipmentChanged, disableNotification, autoLogin } = this.state;

    return (
      <div className='flex-vbox' style={{ borderBottom: '1px solid #dee2e6' }}>
        {/* Toggle button */}
        <div className='flex-hbox justify-content-end' style={{ padding: '4px 12px', borderBottom: '1px solid #f0f0f0' }}>
          <button className='btn btn-sm btn-outline-primary' style={{ fontSize: 10, padding: '2px 8px' }}
            onClick={this.onToggleViewMode}>
            Switch to Compact View
          </button>
        </div>

        {/* Row 1: Search By radio buttons */}
        <div className='flex-hbox align-items-center flex-wrap' style={{ gap: 8, padding: '8px 12px', borderBottom: '1px solid #e9ecef' }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: '#6c757d', whiteSpace: 'nowrap' }}>Search by:</span>
          {SEARCH_BY_OPTIONS.map(opt => (
            <label key={opt.value} className='flex-hbox align-items-center' style={{ gap: 3, fontSize: 12, cursor: 'pointer' }}>
              <input type='radio' name='searchBy' checked={searchBy === opt.value}
                onChange={() => this.onSearchByChange(opt.value)}
                style={{ accentColor: '#0d6efd' }} />
              <span style={searchBy === opt.value ? { fontWeight: 600, color: '#0d6efd' } : undefined}>
                {opt.label}
              </span>
            </label>
          ))}
        </div>

        {/* Row 2: Inputs + Apply */}
        <div className='flex-hbox align-items-end' style={{ gap: 8, padding: '8px 12px', borderBottom: '1px solid #e9ecef' }}>
          {/* Doc Type (Phase 1: UI placeholder) */}
          <div style={{ minWidth: 140 }}>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Doc Type</span>
            <select className='form-select form-select-sm' style={{ fontSize: 12, height: 30 }}
              value={docType} onChange={(e) => this.setState({ docType: e.target.value })}>
              {DOC_TYPE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Branch (Phase 1: UI placeholder) */}
          <div style={{ minWidth: 120 }}>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Branch</span>
            <select className='form-select form-select-sm' style={{ fontSize: 12, height: 30 }}
              value={branch} onChange={(e) => this.setState({ branch: e.target.value })}>
              {BRANCH_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Search Value */}
          <div style={{ flex: 1, minWidth: 200 }}>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Search Value</span>
            <input.WStringInput name='searchValue' value={searchValue}
              placeholder='Enter search value...'
              onChange={this.onSearchValueChange}
              style={{ fontSize: 12, height: 30 }} />
          </div>

          {/* Date Range */}
          <div className='flex-shrink-0'>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Period</span>
            <WDateRangeFilter appContext={appContext} pageContext={pageContext}
              initBean={dateFilter} onModify={this.onDateFilterChange} />
          </div>

          {/* Apply Button */}
          <button className='btn btn-primary btn-sm' style={{ fontSize: 12, fontWeight: 600, height: 30, whiteSpace: 'nowrap', padding: '4px 16px' }}
            onClick={this.onApplySearch}>
            Apply Search
          </button>
        </div>

        {/* Row 3: Checkboxes */}
        <div className='flex-hbox align-items-center' style={{ gap: 16, padding: '6px 12px', background: '#f8f9fa' }}>
          <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, color: '#495057', cursor: 'pointer' }}>
            <input type='checkbox' checked={hideResultAfterView}
              onChange={() => this.onCheckboxChange('hideResultAfterView')} />
            Hide Result After Click View Detail
          </label>
          <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, color: '#495057', cursor: 'pointer' }}>
            <input type='checkbox' checked={shipmentFinish}
              onChange={() => this.onCheckboxChange('shipmentFinish')} />
            Shipment Finish
          </label>
          <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, color: '#495057', cursor: 'pointer' }}>
            <input type='checkbox' checked={shipmentChanged}
              onChange={() => this.onCheckboxChange('shipmentChanged')} />
            Shipment Changed
          </label>
          <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, color: '#495057', cursor: 'pointer' }}>
            <input type='checkbox' checked={disableNotification}
              onChange={() => this.onCheckboxChange('disableNotification')} />
            Disable Notification
          </label>
          <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, color: '#495057', cursor: 'pointer' }}>
            <input type='checkbox' checked={autoLogin}
              onChange={() => this.onCheckboxChange('autoLogin')} />
            Auto Login
          </label>
        </div>
      </div>
    );
  }

  renderCompactView(): React.ReactNode {
    const { appContext, pageContext } = this.props;
    const { searchBy, searchValue, dateFilter, docType, branch,
      hideResultAfterView, shipmentFinish, shipmentChanged, disableNotification, autoLogin } = this.state;

    return (
      <div style={{ borderBottom: '1px solid #dee2e6' }}>
        {/* Toggle button */}
        <div className='flex-hbox justify-content-end' style={{ padding: '4px 12px', borderBottom: '1px solid #f0f0f0' }}>
          <button className='btn btn-sm btn-outline-primary' style={{ fontSize: 10, padding: '2px 8px' }}
            onClick={this.onToggleViewMode}>
            Switch to Full View
          </button>
        </div>

        {/* Single row */}
        <div className='flex-hbox align-items-end' style={{ gap: 8, padding: '8px 12px' }}>
          {/* Search By dropdown */}
          <div style={{ minWidth: 130 }}>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Search By</span>
            <select className='form-select form-select-sm' style={{ fontSize: 12, height: 30 }}
              value={searchBy} onChange={(e) => this.onSearchByChange(e.target.value)}>
              {SEARCH_BY_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Search Value */}
          <div style={{ flex: 1, minWidth: 250 }}>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Search Value</span>
            <input.WStringInput name='searchValue' value={searchValue}
              placeholder='Enter search value...'
              onChange={this.onSearchValueChange}
              style={{ fontSize: 12, height: 30 }} />
          </div>

          {/* Date Range */}
          <div className='flex-shrink-0'>
            <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Period</span>
            <WDateRangeFilter appContext={appContext} pageContext={pageContext}
              initBean={dateFilter} onModify={this.onDateFilterChange} />
          </div>

          {/* Search + Advanced */}
          <button className='btn btn-primary btn-sm' style={{ fontSize: 12, fontWeight: 600, height: 30, padding: '4px 16px' }}
            onClick={this.onApplySearch}>
            Search
          </button>

          <bs.Popover popoverId={`adv-search-${util.IDTracker.next()}`}
            className='flex-shrink-0' placement='bottom-end' offset={[0, 4]} closeOnTrigger='.btn'>
            <bs.PopoverToggle laf='secondary' outline className='p-1' style={{ height: 30, fontSize: 11, color: '#6c757d' }}>
              Advanced
            </bs.PopoverToggle>
            <bs.PopoverContent>
              <div className='flex-vbox p-2 gap-2' style={{ minWidth: 320 }}>
                {/* Doc Type */}
                <div>
                  <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Doc Type</span>
                  <select className='form-select form-select-sm' style={{ fontSize: 12 }}
                    value={docType} onChange={(e) => this.setState({ docType: e.target.value })}>
                    {DOC_TYPE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>
                {/* Branch */}
                <div>
                  <span style={{ fontSize: 10, color: '#6c757d', fontWeight: 600 }}>Branch</span>
                  <select className='form-select form-select-sm' style={{ fontSize: 12 }}
                    value={branch} onChange={(e) => this.setState({ branch: e.target.value })}>
                    {BRANCH_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>
                {/* Checkboxes */}
                <div className='flex-vbox gap-1 pt-1 border-top'>
                  <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, cursor: 'pointer' }}>
                    <input type='checkbox' checked={hideResultAfterView}
                      onChange={() => this.onCheckboxChange('hideResultAfterView')} />
                    Hide Result After Click View Detail
                  </label>
                  <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, cursor: 'pointer' }}>
                    <input type='checkbox' checked={shipmentFinish}
                      onChange={() => this.onCheckboxChange('shipmentFinish')} />
                    Shipment Finish
                  </label>
                  <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, cursor: 'pointer' }}>
                    <input type='checkbox' checked={shipmentChanged}
                      onChange={() => this.onCheckboxChange('shipmentChanged')} />
                    Shipment Changed
                  </label>
                  <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, cursor: 'pointer' }}>
                    <input type='checkbox' checked={disableNotification}
                      onChange={() => this.onCheckboxChange('disableNotification')} />
                    Disable Notification
                  </label>
                  <label className='flex-hbox align-items-center' style={{ gap: 4, fontSize: 11, cursor: 'pointer' }}>
                    <input type='checkbox' checked={autoLogin}
                      onChange={() => this.onCheckboxChange('autoLogin')} />
                    Auto Login
                  </label>
                </div>
              </div>
            </bs.PopoverContent>
          </bs.Popover>
        </div>
      </div>
    );
  }

  render(): React.ReactNode {
    const { viewMode } = this.state;
    return viewMode === 'full' ? this.renderFullView() : this.renderCompactView();
  }
}
```

- [ ] **Step 2: Verify frontend build**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms/webui/fms && pnpm run dev-server`
Expected: Compiles without errors. Press Ctrl+C after confirming.

- [ ] **Step 3: Commit**

```
git add webui/fms/src/app/fms/transaction/WTransactionSearchBar.tsx
git commit -m "feat: create WTransactionSearchBar with Full and Compact view modes"
```

---

### Task 4: Integrate Search Bar into UIMainView + Export

**Files:**
- Modify: `webui/fms/src/app/fms/transaction/UIMainView.tsx`
- Modify: `webui/fms/src/app/fms/transaction/index.tsx`

- [ ] **Step 1: Update UIMainView.tsx**

Replace the entire file:

```typescript
import React from 'react';
import { app } from '@of1-webui/lib';
import { WTransactionSearchBar } from './WTransactionSearchBar';
import { UITransactionList, UITransactionListPlugin } from './UITransactionList';

export interface UIMainWindowProps extends app.AppComponentProps { }

export interface UIMainWindowState { }

export class UIMainWindow extends app.AppComponent<UIMainWindowProps, UIMainWindowState> {
  private transactionPlugin = new UITransactionListPlugin();
  private listRef = React.createRef<UITransactionList>();

  onApplySearch = () => {
    if (this.listRef.current) {
      this.listRef.current.reloadData();
    }
  }

  render(): React.ReactNode {
    const { appContext, pageContext } = this.props;

    return (
      <div className='flex-vbox h-100'>
        <div className='flex-vbox flex-grow-0'>
          <WTransactionSearchBar
            appContext={appContext} pageContext={pageContext}
            plugin={this.transactionPlugin}
            onApplySearch={this.onApplySearch}
          />
        </div>
        <div className='flex-vbox' style={{ flex: 1 }}>
          <UITransactionList ref={this.listRef}
            appContext={appContext} pageContext={pageContext}
            plugin={this.transactionPlugin}
            hideHeaderBar={true} />
        </div>
      </div>
    );
  }
}
```

- [ ] **Step 2: Add export to index.tsx**

Add after existing exports:

```typescript
export { WTransactionSearchBar } from './WTransactionSearchBar';
```

- [ ] **Step 3: Verify frontend build**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms/webui/fms && pnpm run dev-server`
Expected: Compiles without errors. Press Ctrl+C after confirming.

- [ ] **Step 4: Manual verification in browser**

Run the full stack:
```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
./tools.sh build -clean -code -ui
cd working/release-fms/server-env
./instance.sh run
```

Open `http://localhost:8080`, navigate to Transaction screen. Verify:
- Search bar appears above the transaction list
- Full view: 3 rows (radios, inputs, checkboxes)
- Toggle switches to Compact view (single row + Advanced popover)
- Apply Search triggers server-side search and refreshes grid
- Date range presets work
- Search by Job ID, POL, HAWB, Container filter correctly
- Shipment Finish checkbox filters by DELIVERED/CLOSED status
- Old inline header bar in UITransactionList is hidden

- [ ] **Step 5: Commit**

```
git add webui/fms/src/app/fms/transaction/UIMainView.tsx webui/fms/src/app/fms/transaction/index.tsx
git commit -m "feat: integrate WTransactionSearchBar into UIMainWindow"
```

---

## Phase 1 Limitations (Documented)

- **Doc Type** and **Branch** dropdowns are UI placeholders — no backend filter applied. Phase 2 will add `companyId` and document type filtering.
- **Hide Result After Click View Detail**, **Disable Notification**, **Auto Login** checkboxes are UI-only toggles — behavior to be implemented when the corresponding features are built.
- SQL values use string concatenation (matching existing codebase pattern in `IntegratedHousebillSql.groovy`). Phase 2 should migrate to parameterized queries.

---

## FMS Cron Master Data Sync — Design Spec


**Date:** 2026-04-13
**Status:** Approved

## Problem

He thong FMS co 2 nguon sync master data:
1. **BFS One** (MSSQL -> FMS) - da co cron cho hau het entity, **ngoai tru Zone**
2. **Platform** (of1-platform -> FMS) - chua co cron nao, chi trigger thu cong qua RPC

## Solution

### Cron 1: BFSOneSyncZoneCronJob

- **File:** `batch/zone/BFSOneSyncZoneCronJob.java`
- **Pattern:** Giong cac BFS One cron hien tai (Bank, Commodity...)
- **Frequency:** `EVERY_DAY_07_AM`
- **Action:** `BatchSyncService.syncZones(client, "BEE_VN")`

### Cron 2: MasterDataSyncCronJob

- **File:** `batch/masterdata/MasterDataSyncCronJob.java`
- **Pattern:** 1 cron job gop, goi MasterDataSyncService theo thu tu dependency
- **Frequency:** `EVERY_DAY_07_AM`
- **Thu tu sync:**
  1. CountryGroups
  2. Countries
  3. CountryGroupRels
  4. Locations
  5. States
  6. Districts
  7. Subdistricts
  8. Units
- **Error handling:** Neu 1 step fail -> log error + Telegram notify -> tiep tuc step tiep theo
- **Telegram notify:** Summary voi so record moi step

## Files Created

1. `module/integration/src/main/java/of1/fms/module/integration/batch/zone/BFSOneSyncZoneCronJob.java`
2. `module/integration/src/main/java/of1/fms/module/integration/batch/masterdata/MasterDataSyncCronJob.java`
