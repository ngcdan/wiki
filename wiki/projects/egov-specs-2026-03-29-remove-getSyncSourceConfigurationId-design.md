---
title: "Spec — Remove getSyncSourceConfigurationId Design"
tags: [egov, specs, design, refactor]
created: 2026-03-29
---

# Design: Remove getSyncSourceConfigurationId from AbstractEcusMapper

**Date:** 2026-03-29
**Scope:** module/ecus-thaison

---

## Problem

`AbstractEcusMapper.getSyncSourceConfigurationId(companyId)` performs a DB lookup
(find-or-create `SyncSourceConfiguration`) on every batch/page during sync. This
lookup is redundant because `SyncController` already has the `SyncSourceConfiguration`
record in hand when it sets up the tenant context.

The root cause is that most `SyncController` multi-ECUS endpoints only pass 2 args to
`EcusTenantContext.set()`, leaving `syncSourceConfigurationId` out of context. Mappers
then re-derive it via a service call.

---

## Solution

Pass `mapping.getId()` as the 3rd arg in all remaining `SyncController` endpoints,
making `syncSourceConfigurationId` available in context for both CDC and batch flows.
Remove the redundant derivation from `AbstractEcusMapper` and from all mappers that
carry their own private copy.

---

## Changes

### 1. SyncController — 9 remaining 2-arg call sites

`/{ecusDbName}/company-entities` (line 241) is already migrated to 3-arg. The
following 9 endpoints still use the 2-arg form and need updating:

| Line | Endpoint |
|---|---|
| 185 | `/{ecusDbName}/test` |
| 217 | `/{ecusDbName}/core-entities` |
| 264 | `/{ecusDbName}/partner-entities` |
| 287 | `/{ecusDbName}/partner-entities/declaration` |
| 309 | `/{ecusDbName}/partner-entities/vnaccs` |
| 331 | `/{ecusDbName}/partner-entities/goods` |
| 353 | `/{ecusDbName}/partner-entities/customs/dms` |
| 375 | `/{ecusDbName}/partner-entities/customs/loginfo` |
| 399 | `/{ecusDbName}/partner-entities/ola` |

Change:
```java
// Before
EcusTenantContext.set(ecusDbName, mapping.getCompanyId());

// After
EcusTenantContext.set(ecusDbName, mapping.getCompanyId(), mapping.getId());
```

`mapping` is fetched via `orElseThrow` in 8 of 9 endpoints, so `mapping.getId()` is
always non-null at the call site. The `/{ecusDbName}/test` endpoint uses `orElse(null)`
followed by an explicit null check and early return (line 175-179), so `mapping` is
also guaranteed non-null by line 185.

Note: `POST /company-entities/cache` (no `{ecusDbName}` path variable) does not set
`EcusTenantContext` and is intentionally excluded from this change.

### 2. EcusTenantContext — keep 2-arg overload with TODO

The 2-arg `set(String ecusDbName, Long companyId)` is kept as-is but annotated:

```java
// TODO: remove once all callers migrated to 3-arg set()
public static void set(String ecusDbName, Long companyId) { ... }
```

### 3. AbstractEcusMapper — remove service dependency and method

Remove:
- `@Autowired SyncSourceConfigurationService syncSourceConfigurationService` field
- `getSyncSourceConfigurationId(Long companyId)` method
- All associated imports (`SyncSourceConfiguration`, `SyncSourceConfigurationService`,
  `Optional`, `@Slf4j` annotation, `lombok.extern.slf4j.Slf4j`)

Result: `AbstractEcusMapper` becomes an empty abstract class.

### 4. Mappers with private copies

Three mappers do NOT extend `AbstractEcusMapper` and carry their own private
`getSyncSourceConfigurationId(Long companyId)` method:

| File | Line of private method | Call site |
|---|---|---|
| `logic/mapper/core/EcusSDonViMapper.java` | 243 | line 102 (inside lambda) |
| `logic/mapper/partner/EcusDTOKHAIMDVNACCSMapper.java` | 203 | line 237 (inside `processBatch`) |
| `logic/mapper/partner/EcusDTOKHAIMDVNACCS2Mapper.java` | 199 | line 231 (inside `processBatch`) |

For all three:
- Remove the private `getSyncSourceConfigurationId` method and its unused imports.

**EcusSDonViMapper** — call site is inside the async lambda:
- Capture `capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId()` before the lambda.
- Change `EcusTenantContext.set(ecusDbName, capturedCompanyId)` inside lambda to 3-arg.
- Replace `getSyncSourceConfigurationId(capturedCompanyId)` inside lambda with `EcusTenantContext.getSyncSourceConfigurationId()`.
- Remove dead commented-out line 212 in `processSync` (`// Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);`).

**EcusDTOKHAIMDVNACCSMapper / EcusDTOKHAIMDVNACCS2Mapper** — call site is inside `processBatch`:
- Capture `capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId()` before the lambda in `syncEntity()`.
- Change `EcusTenantContext.set(ecusDbName, companyId)` inside lambda to 3-arg (pass `capturedSyncSourceConfigId`).
- Replace `getSyncSourceConfigurationId(companyId)` inside `processBatch` with `EcusTenantContext.getSyncSourceConfigurationId()`.
- No change to `processBatch` method signature.
- **Dependency:** the capture in `syncEntity()` reads from `EcusTenantContext`, so Step 1
  (SyncController 3-arg) must be applied in the same commit. Applying this step alone
  would silently set `syncSourceConfigurationId = null` on all entities.

### 5. 29 AbstractEcusMapper subclasses — replace call sites

**Case A — async mappers (27 files):**

Capture `syncSourceConfigId` from context BEFORE spawning threads, pass it into the
lambda via the 3-arg `set()`, then read from context inside the lambda.

```java
// Before
final Long capturedCompanyId = companyId;
CompletableFuture.supplyAsync(() -> {
    EcusTenantContext.set(ecusDbName, capturedCompanyId);
    ...
    Long syncSourceConfigId = getSyncSourceConfigurationId(capturedCompanyId);
    return self.processBatch(capturedCompanyId, currentPage, syncSourceConfigId);
});

// After
final Long capturedCompanyId = companyId;
final Long capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
CompletableFuture.supplyAsync(() -> {
    EcusTenantContext.set(ecusDbName, capturedCompanyId, capturedSyncSourceConfigId);
    ...
    Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
    return self.processBatch(capturedCompanyId, currentPage, syncSourceConfigId);
});
```

**Case B — direct (non-async) mappers (2 files: `EcusSPTVTMapper`, `EcusSPTTTMapper`):**

```java
// Before
Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);

// After
Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
```

---

## Files Affected

| File | Change |
|---|---|
| `controller/SyncController.java` | 9 call sites: 2-arg → 3-arg `set()` |
| `context/EcusTenantContext.java` | Add TODO comment on 2-arg overload |
| `logic/mapper/AbstractEcusMapper.java` | Remove field + method + imports |
| `logic/mapper/core/EcusSDonViMapper.java` | Remove private method, update lambda |
| `logic/mapper/partner/EcusDTOKHAIMDVNACCSMapper.java` | Remove private method, update lambda + `processBatch` |
| `logic/mapper/partner/EcusDTOKHAIMDVNACCS2Mapper.java` | Remove private method, update lambda + `processBatch` |
| 27 async AbstractEcusMapper subclasses (company/, partner/) | Case A: capture + 3-arg set + read from context |
| 2 direct AbstractEcusMapper subclasses (`EcusSPTVTMapper`, `EcusSPTTTMapper`) | Case B: direct replacement |

---

## Non-Goals

- No changes to CDC consumers (they already use 3-arg `set()`).
- No changes to `SyncSourceConfigurationService` itself.
- The 2-arg `EcusTenantContext.set()` overload is NOT removed (kept with TODO).
- No `processBatch` signature changes in VNACCS mappers.
- No behavior change — same `syncSourceConfigurationId` values flow through, just
  sourced from context instead of a DB lookup.
