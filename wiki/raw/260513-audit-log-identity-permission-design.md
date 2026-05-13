# Audit Log for Identity & Permission — Design Spec

**Date:** 2026-05-13
**Module:** `of1-core / module/platform-federation`
**Status:** Approved

---

## 1. Goal

Implement audit logging for all write operations on Identity, Role, and Permission entities in the `platform-federation` module. The audit log records **who** performed **what action** on **which entity** and **when**, stored in a dedicated DB table for direct SQL querying.

## 2. Scope

### In Scope

- Identity lifecycle: create, update, enable/disable, password reset, remove required actions
- Role operations: assign, remove
- Role type operations: create, delete
- App operations: create/update, delete
- Permission operations: save, delete, update capability, update data scope, update storage state
- DB-only storage (single `platform_audit_log` table)
- Action metadata only (no before/after snapshots)
- Explicit logging in Logic layer (no AOP)

### Out of Scope

- Kafka event publishing for audit (future enhancement)
- RPC API for querying audit logs (future enhancement)
- Before/after data snapshots
- Read operation auditing
- Federation/integration audit (Nextcloud, Moodle, Mailcow, etc.)

## 3. Data Model

### 3.1 Entity: `AuditLog`

Extends `CompanyEntity` (inherits `companyId`, `createdTime`, `createdBy`, `modifiedTime`, `modifiedBy`, `storageState`, `version`).

Note: `createdBy` from `PersistableEntity` stores `remoteUser` (which is `loginId` — see `PersistableEntity.set(ClientContext)` → `getRemoteUser()` → returns `loginId`). This serves as a fallback identifier when `performerFullName` is null.

**Table:** `platform_audit_log`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT (PK, auto) | Primary key (from Persistable) |
| `company_id` | BIGINT (NOT NULL) | From CompanyEntity |
| `action` | VARCHAR(50) (ENUM) | AuditAction enum value |
| `entity_type` | VARCHAR(50) | Plain string: "IDENTITY", "IDENTITY_ROLE", etc. |
| `entity_id` | BIGINT | ID of the affected entity |
| `entity_label` | VARCHAR(255) | Human-readable label (loginId, role name, app name) |
| `performer_account_id` | BIGINT | Account ID of the performer (from ClientContext). Note: `ClientContext.accountId` is primitive `long` — will be `0` (not null) for SYSTEM/DEFAULT/ANON contexts. |
| `performer_full_name` | VARCHAR(255) | Full name of the performer (from ClientContext). May be null — use `createdBy` (loginId) as fallback. |
| `action_date` | TIMESTAMP | When the action occurred (separate tracking date) |
| `description` | TEXT | Short description of the action |
| `created_time` | TIMESTAMP | Entity creation time (from PersistableEntity) |
| `created_by` | VARCHAR | Entity creator = loginId (from PersistableEntity) |
| `modified_time` | TIMESTAMP | Last modification time (from PersistableEntity) |
| `modified_by` | VARCHAR | Last modifier (from PersistableEntity) |
| `storage_state` | VARCHAR | From PersistableEntity |
| `version` | BIGINT | Optimistic lock (from PersistableEntity) |

**Indexes:**

| Name | Columns | Purpose |
|------|---------|---------|
| `idx_audit_entity` | `entity_type, entity_id` | Query by entity |
| `idx_audit_performer` | `performer_account_id` | Query by who performed |
| `idx_audit_action_date` | `action_date` | Query by time range |
| `idx_audit_company_date` | `company_id, action_date` | Query by company + time range (multi-tenant) |

### 3.2 Enum: `AuditAction`

```java
public enum AuditAction {
  // Identity
  CREATE_IDENTITY,
  UPDATE_IDENTITY,
  ENABLE_IDENTITY,
  DISABLE_IDENTITY,
  PASSWORD_RESET,
  REMOVE_REQUIRED_ACTIONS,

  // Role
  ROLE_ASSIGN,
  ROLE_REMOVE,

  // Role Type
  ROLE_TYPE_CREATE,
  ROLE_TYPE_DELETE,

  // App
  APP_SAVE,
  APP_DELETE,

  // Permission (UserAppFeature)
  PERMISSION_SAVE,
  PERMISSION_DELETE,
  PERMISSION_UPDATE_CAPABILITY,
  PERMISSION_UPDATE_DATASCOPE,
  PERMISSION_UPDATE_STATE
}
```

Note: `DELETE_IDENTITY` removed — no delete identity method exists in current codebase. Will be added when the operation is implemented.

## 4. Components

### 4.1 File Structure

Following existing convention — entities in `entity/`, repositories in `repository/`:

```
datatp/platform/identity/audit/
├── AuditAction.java           // Enum
└── AuditLogWriter.java        // @Component helper for writing audit records

datatp/platform/identity/entity/
└── AuditLog.java              // @Entity extends CompanyEntity (alongside existing entities)

datatp/platform/identity/repository/
└── AuditLogRepository.java    // Spring Data JPA repository (alongside existing repos)
```

`AuditLog` entity goes in `entity/` and `AuditLogRepository` goes in `repository/` to match the existing `Identity`, `IdentityRole`, etc. pattern. Only `AuditAction` enum and `AuditLogWriter` helper live in the new `audit/` package.

### 4.2 AuditLogWriter

Stateless helper component injected into `IdentityLogic` and `AppLogic`.

```java
@Component
public class AuditLogWriter {

  @Autowired
  private AuditLogRepository auditLogRepo;

  public void log(ClientContext ctx, AuditAction action,
                  String entityType, Long entityId, String entityLabel,
                  String description) {
    AuditLog audit = new AuditLog();
    audit.setAction(action);
    audit.setEntityType(entityType);
    audit.setEntityId(entityId);
    audit.setEntityLabel(entityLabel);
    audit.setPerformerAccountId(ctx.getAccountId());
    audit.setPerformerFullName(ctx.getFullName());
    audit.setActionDate(new Date());
    audit.setDescription(description);
    audit.set(ctx, ctx.getCompanyId());
    auditLogRepo.save(audit);
  }
}
```

- Runs within the **same transaction** as the calling Logic method
- If the business operation rolls back, the audit record rolls back too
- No try/catch — audit failure should surface, not be silently swallowed

### 4.3 AuditLogRepository

```java
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
}
```

Minimal — no custom queries needed yet (future API will add search methods).

### 4.4 Config Update

Existing `IdentityConfig.java` already scans `datatp.platform.identity.entity` and `datatp.platform.identity.repository` — no config change needed for `AuditLog` entity and repository since they go into those existing packages.

Only the `audit/` sub-package (containing `AuditAction` and `AuditLogWriter`) needs to be component-scanned, which happens automatically via Spring Boot's component scan.

## 5. Integration Points

### 5.1 IdentityLogic — 12 audit points

| # | Method | AuditAction | entityType | entityLabel |
|---|--------|-------------|------------|-------------|
| 1 | `saveIdentity()` | CREATE_IDENTITY or UPDATE_IDENTITY | IDENTITY | identity.loginId |
| 2 | `createEmployeeIdentity()` — new identity branch only | CREATE_IDENTITY | IDENTITY | employeeCreator.username |
| 3 | `disabledIdentities()` — per identity | ENABLE_IDENTITY or DISABLE_IDENTITY | IDENTITY | identity.loginId |
| 4 | `resetAccountPassword()` | PASSWORD_RESET | IDENTITY | pwReset.getUsername() (from `PasswordReset` DTO) |
| 5 | `removeRequiredActions()` | REMOVE_REQUIRED_ACTIONS | IDENTITY | username |
| 6 | `saveRole()` | ROLE_ASSIGN | IDENTITY_ROLE | identity.loginId + roleType info |
| 7 | `saveRoles()` — per role | ROLE_ASSIGN | IDENTITY_ROLE | identity.loginId + roleType info |
| 8 | `deleteIdentityRoles()` — per role | ROLE_REMOVE | IDENTITY_ROLE | identity.loginId |
| 9 | `saveRoleType()` | ROLE_TYPE_CREATE | IDENTITY_ROLE_TYPE | roleType.role |
| 10 | `deleteRoleTypes()` — per roleType | ROLE_TYPE_DELETE | IDENTITY_ROLE_TYPE | roleType.role |

Note: `updateIdentity()` calls `saveIdentity()` internally — audit is logged only in `saveIdentity()` to avoid duplication. See Section 7 for details.

### 5.2 AppLogic — 9 audit points

| # | Method | AuditAction | entityType | entityLabel |
|---|--------|-------------|------------|-------------|
| 1 | `saveApp()` | APP_SAVE | APP_FEATURE | app.module + ":" + app.name |
| 2 | `deleteAppByIds()` — per app | APP_DELETE | APP_FEATURE | app id |
| 3 | `saveAppPermission()` | PERMISSION_SAVE | USER_APP_FEATURE | app module + name |
| 4 | `saveAppPermissions()` — per permission | PERMISSION_SAVE | USER_APP_FEATURE | app module + name |
| 5 | `deletePermissions()` — per permission | PERMISSION_DELETE | USER_APP_FEATURE | permission id |
| 6 | `deletePermissionsByIds()` — per id | PERMISSION_DELETE | USER_APP_FEATURE | permission id |
| 7 | `updateAppPermissionCapabilities()` — per target | PERMISSION_UPDATE_CAPABILITY | USER_APP_FEATURE | permission id |
| 8 | `updateAppPermissionDataScopes()` — per target | PERMISSION_UPDATE_DATASCOPE | USER_APP_FEATURE | permission id |
| 9 | `updateAppPermissionStorageStates()` | PERMISSION_UPDATE_STATE | USER_APP_FEATURE | target ids summary |

## 6. Transaction Behavior

- Audit writes happen **inside** the existing `@Transactional` boundary of the calling method
- If the business operation fails and rolls back, audit is also rolled back (no orphan audit records)
- This is intentional: an audit record should only exist for successfully completed operations
- No transactional outbox pattern — not needed for DB-only audit

## 7. Edge Cases

| Case | Behavior |
|------|----------|
| `ClientContext` has null fullName | Store null in `performerFullName` — loginId is available via `createdBy` from PersistableEntity |
| `ClientContext` is SYSTEM/DEFAULT/ANON | `performerAccountId` will be `0` (primitive `long` default, not null). Record as-is — system operations are also audited |
| Batch operations (saveRoles, deleteIdentityRoles) | One audit record per entity affected, not one for the batch |
| `createEmployeeIdentity()` for existing identity (republish) | No audit — only the new identity creation branch is audited |
| `updateAppPermissionStorageStates()` uses bulk SQL update | Single audit record with summary of target IDs |

### Duplicate audit concern: `updateIdentity()` → `saveIdentity()`

`updateIdentity()` calls `saveIdentity()` internally. To avoid double-logging:
- **Option chosen:** Only log in `saveIdentity()` (which already distinguishes CREATE vs UPDATE based on `isNew()`). No audit in `updateIdentity()` since `saveIdentity()` covers it.
- `updateIdentity()` adds Kafka event publishing on top — that is not an audit concern.

### Duplicate audit concern: `createEmployeeIdentity()` → `saveIdentity()`

`createEmployeeIdentity()` calls `saveIdentity()` for new identities. To avoid double-logging:
- **Option chosen:** Only log in `saveIdentity()`. No separate audit in `createEmployeeIdentity()`.

## 8. Sample SQL Queries

```sql
-- All actions by a specific user in the last 7 days
SELECT * FROM platform_audit_log
WHERE performer_account_id = 123
  AND action_date > NOW() - INTERVAL '7 days'
ORDER BY action_date DESC;

-- All permission changes for a company
SELECT * FROM platform_audit_log
WHERE company_id = 4
  AND entity_type = 'USER_APP_FEATURE'
ORDER BY action_date DESC;

-- All role assignments/removals
SELECT * FROM platform_audit_log
WHERE action IN ('ROLE_ASSIGN', 'ROLE_REMOVE')
ORDER BY action_date DESC;

-- Password resets
SELECT * FROM platform_audit_log
WHERE action = 'PASSWORD_RESET'
ORDER BY action_date DESC;

-- All audit events for a company in a time range
SELECT * FROM platform_audit_log
WHERE company_id = 4
  AND action_date BETWEEN '2026-05-01' AND '2026-05-13'
ORDER BY action_date DESC;
```

## 9. Future Enhancements (Out of Scope)

1. **Kafka audit events** — publish to `audit-events` topic for downstream consumers
2. **RPC API** — expose `@RPCCall` search endpoint for audit log queries
3. **Before/after snapshots** — JSON diff of entity state changes
4. **Retention policy** — auto-archive or delete old audit records
5. **Federation audit** — extend to Nextcloud/Moodle/Mailcow operations
6. **DELETE_IDENTITY** — add audit action when identity deletion is implemented
