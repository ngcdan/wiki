# FMS Transaction Type — Design Spec

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
