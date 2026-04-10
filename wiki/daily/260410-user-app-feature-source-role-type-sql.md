# Migration — Add `source_role_type_id` to `security_user_app_feature`

> **Date**: 2026-04-10
> **Ticket**: Audit source of user app feature permissions (custom vs role-sourced)
> **Related entity**: `datatp.platform.resource.entity.UserAppFeature`
> **Related logic**: `UserAppFeatureTemplateLogic.syncUserPermissions`, `IdentityLogic.deleteRoleTypes`
> **Design doc**: [`260410-identity-erd.md`](./260410-identity-erd.md)

## Goal

Add a nullable column `source_role_type_id` to `security_user_app_feature` so every permission row can be audited as either:

- `NULL` → **CUSTOM** (granted manually by admin, protected from sync)
- `NOT NULL` → **Role-sourced** (materialized from `UserAppFeatureTemplate` of the referenced `IdentityRoleType`)

## Target schema

```
security_user_app_feature
├── id                    BIGINT  PK
├── company_id            BIGINT  NOT NULL  ─┐
├── account_id            BIGINT  NOT NULL   ├─ UK (company_id, account_id, app_id)
├── app_id                BIGINT  NOT NULL  ─┘
├── source_role_type_id   BIGINT  NULL      ─── NEW (indexed, nullable)
├── access_type           VARCHAR NOT NULL
├── capability            VARCHAR NOT NULL
├── data_scope            VARCHAR
└── ...                   (audit columns from PersistableEntity)
```

---

## Migration SQL

### PostgreSQL

```sql
-- =====================================================================
-- 2026-04-10: UserAppFeature.source_role_type_id (audit source column)
-- =====================================================================

BEGIN;

-- 1. Add nullable column
ALTER TABLE security_user_app_feature
  ADD COLUMN source_role_type_id BIGINT NULL;

-- 2. Index for cascade/audit queries (delete-by-source-role-type,
--    "find all permissions from role X", filter custom vs role-sourced)
CREATE INDEX idx_security_user_app_feature_source_role_type_id
  ON security_user_app_feature(source_role_type_id);

-- 3. (Optional) Add FK constraint referencing identity_role_type.
--    Kept commented out by default: keeping the FK soft lets us drop a
--    role type without touching permission rows at the DB layer — the
--    cascade is handled by IdentityLogic.deleteRoleTypes which calls
--    deleteBySourceRoleTypeId explicitly. Enable only if you prefer
--    a DB-level guarantee over application-level cascade.
--
-- ALTER TABLE security_user_app_feature
--   ADD CONSTRAINT fk_security_user_app_feature_source_role_type
--   FOREIGN KEY (source_role_type_id)
--   REFERENCES identity_role_type(id)
--   ON DELETE SET NULL;

COMMIT;
```

### Microsoft SQL Server

```sql
BEGIN TRANSACTION;

ALTER TABLE security_user_app_feature
  ADD source_role_type_id BIGINT NULL;

CREATE INDEX idx_security_user_app_feature_source_role_type_id
  ON security_user_app_feature(source_role_type_id);

-- Optional FK (see note above)
-- ALTER TABLE security_user_app_feature
--   ADD CONSTRAINT fk_security_user_app_feature_source_role_type
--   FOREIGN KEY (source_role_type_id)
--   REFERENCES identity_role_type(id)
--   ON DELETE SET NULL;

COMMIT TRANSACTION;
```

---

## Backfill (optional, 1-time)

Existing rows sẽ có `source_role_type_id = NULL` sau khi migration chạy → mặc định bị treat là **CUSTOM**. Nếu muốn tự động nhận dạng những row đã được template sync trước đây, chạy backfill script này.

**Chiến lược match**: row được coi là "từ role type X" nếu tồn tại template match **chính xác** với `(companyId, appId, capability, dataScope, accessType)`. Nếu nhiều templates match (user có nhiều role) — lấy role type ID **nhỏ nhất** (deterministic, tuỳ ý).

### PostgreSQL

```sql
-- =====================================================================
-- Backfill: detect role-sourced rows by exact template match
-- =====================================================================

BEGIN;

-- Update rows that match exactly one template per (company_id, app_id, account_id)
UPDATE security_user_app_feature uaf
SET source_role_type_id = sub.role_type_id
FROM (
  SELECT
    uaf.id AS uaf_id,
    MIN(t.role_type_id) AS role_type_id
  FROM security_user_app_feature uaf
  JOIN security_user_app_feature_template t
    ON t.company_id    = uaf.company_id
   AND t.app_feature_id = uaf.app_id
   AND t.access_type    = uaf.access_type
   AND t.capability     = uaf.capability
   AND COALESCE(t.data_scope, '') = COALESCE(uaf.data_scope, '')
  -- Only consider templates whose role type is currently assigned to the account
  JOIN identity_role ir
    ON ir.company_id   = uaf.company_id
   AND ir.role_type_id = t.role_type_id
  JOIN identity_identity i
    ON i.id         = ir.identity_id
   AND i.account_id = uaf.account_id
  WHERE uaf.source_role_type_id IS NULL
  GROUP BY uaf.id
) sub
WHERE uaf.id = sub.uaf_id;

-- Report how many rows are still CUSTOM after backfill
SELECT
  COUNT(*) FILTER (WHERE source_role_type_id IS NULL)      AS custom_rows,
  COUNT(*) FILTER (WHERE source_role_type_id IS NOT NULL)  AS role_sourced_rows,
  COUNT(*)                                                  AS total_rows
FROM security_user_app_feature;

COMMIT;
```

### Microsoft SQL Server

```sql
BEGIN TRANSACTION;

WITH matched AS (
  SELECT
    uaf.id AS uaf_id,
    MIN(t.role_type_id) AS role_type_id
  FROM security_user_app_feature uaf
  INNER JOIN security_user_app_feature_template t
    ON t.company_id    = uaf.company_id
   AND t.app_feature_id = uaf.app_id
   AND t.access_type    = uaf.access_type
   AND t.capability     = uaf.capability
   AND ISNULL(t.data_scope, '') = ISNULL(uaf.data_scope, '')
  INNER JOIN identity_role ir
    ON ir.company_id   = uaf.company_id
   AND ir.role_type_id = t.role_type_id
  INNER JOIN identity_identity i
    ON i.id         = ir.identity_id
   AND i.account_id = uaf.account_id
  WHERE uaf.source_role_type_id IS NULL
  GROUP BY uaf.id
)
UPDATE uaf
SET uaf.source_role_type_id = m.role_type_id
FROM security_user_app_feature uaf
INNER JOIN matched m ON m.uaf_id = uaf.id;

SELECT
  SUM(CASE WHEN source_role_type_id IS NULL     THEN 1 ELSE 0 END) AS custom_rows,
  SUM(CASE WHEN source_role_type_id IS NOT NULL THEN 1 ELSE 0 END) AS role_sourced_rows,
  COUNT(*)                                                          AS total_rows
FROM security_user_app_feature;

COMMIT TRANSACTION;
```

---

## Rollback

Migration này an toàn rollback vì cột mới chỉ là nullable, không ảnh hưởng existing queries.

```sql
BEGIN;

DROP INDEX IF EXISTS idx_security_user_app_feature_source_role_type_id;

-- If FK was enabled:
-- ALTER TABLE security_user_app_feature
--   DROP CONSTRAINT IF EXISTS fk_security_user_app_feature_source_role_type;

ALTER TABLE security_user_app_feature
  DROP COLUMN source_role_type_id;

COMMIT;
```

⚠️ **Trước khi rollback**, đảm bảo đã deploy lại code cũ (không còn reference tới `sourceRoleTypeId`), nếu không JPA sẽ fail khi bootstrap.

---

## Verification queries

### 1. Smoke test — column exists và index đã tạo

**PostgreSQL:**
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'security_user_app_feature'
  AND column_name = 'source_role_type_id';

SELECT indexname FROM pg_indexes
WHERE tablename = 'security_user_app_feature'
  AND indexname = 'idx_security_user_app_feature_source_role_type_id';
```

**MSSQL:**
```sql
SELECT name, system_type_id, is_nullable
FROM sys.columns
WHERE object_id = OBJECT_ID('security_user_app_feature')
  AND name = 'source_role_type_id';

SELECT name FROM sys.indexes
WHERE object_id = OBJECT_ID('security_user_app_feature')
  AND name = 'idx_security_user_app_feature_source_role_type_id';
```

### 2. Audit — xem permission của 1 user kèm source

```sql
SELECT
  uaf.id,
  af.module,
  af.name        AS app_name,
  uaf.capability,
  uaf.data_scope,
  CASE
    WHEN uaf.source_role_type_id IS NULL THEN 'CUSTOM'
    ELSE rt.role
  END            AS source,
  rt.label       AS source_role_label
FROM security_user_app_feature uaf
JOIN security_app_feature af     ON af.id = uaf.app_id
LEFT JOIN identity_role_type rt  ON rt.id = uaf.source_role_type_id
WHERE uaf.account_id = :accountId
  AND uaf.company_id = :companyId
ORDER BY af.module, af.name;
```

### 3. Phân bố custom vs role-sourced

```sql
SELECT
  CASE WHEN source_role_type_id IS NULL THEN 'CUSTOM' ELSE 'ROLE' END AS source_type,
  COUNT(*) AS row_count
FROM security_user_app_feature
GROUP BY source_type;
```

### 4. Tìm all permissions materialized từ 1 role type cụ thể

```sql
SELECT COUNT(*) AS cnt
FROM security_user_app_feature
WHERE source_role_type_id = :roleTypeId;
```

---

## Deployment order

1. ✅ Deploy code mới (entity + repository + sync logic + cascade) — code **forward-compatible**: không đọc cột mới nếu NULL
2. ▶️ Chạy migration SQL (add column + index)
3. ▶️ (Optional) Chạy backfill script
4. ▶️ Verify bằng audit queries

**Reverse order** nếu rollback:
1. Rollback code trước
2. Rollback migration (drop column + index)

---

## Impact on existing code paths

| Path | Behavior before | Behavior after |
|------|----------------|----------------|
| `AppLogic.getAppPermission` (hot path) | Đọc row bình thường | Không đổi — không join `source_role_type_id` |
| `UserAppFeatureTemplateLogic.syncUserPermissions` | Sync tất cả rows | **Chỉ sync rows có `source_role_type_id NOT NULL`**; CUSTOM rows được bảo vệ |
| `IdentityLogic.deleteRoleTypes` | Xoá `IdentityRole` + templates | Cascade thêm: `deleteBySourceRoleTypeId` cho mỗi role type id |
| Admin UI (save permission manually) | Bình thường | Nên set `source_role_type_id = NULL` để flag là CUSTOM |

⚠️ **Action required**: các nơi trong code trực tiếp save `UserAppFeature` (không qua sync) cần đảm bảo `sourceRoleTypeId` để `NULL`. Hiện tại các path này:

- `AppLogic.saveAppPermission(...)` — admin grant → leave NULL (correct, sẽ auto-NULL vì field default)
- `AppLogic.updateAppPermissionCapabilities(...)` — admin update capability → **giữ nguyên** `sourceRoleTypeId` (không đổi)
- `AppLogic.updateAppPermissionDataScopes(...)` — tương tự, giữ nguyên

Không cần code thay đổi — mặc định Java field = NULL, và update paths không touch field mới.

---

## References

- Entity: `module/platform-federation/src/main/java/datatp/platform/resource/entity/UserAppFeature.java`
- Repository: `module/platform-federation/src/main/java/datatp/platform/resource/repository/AppPermissionRepository.java`
- Sync logic: `module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java`
- Cascade: `module/platform-federation/src/main/java/datatp/platform/identity/IdentityLogic.java` (`deleteRoleTypes`)
- Design: [`260410-identity-erd.md`](./260410-identity-erd.md)
