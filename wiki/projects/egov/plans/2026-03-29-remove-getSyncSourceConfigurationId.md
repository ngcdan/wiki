# Remove getSyncSourceConfigurationId from AbstractEcusMapper — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the redundant `getSyncSourceConfigurationId(companyId)` DB lookup from
`AbstractEcusMapper` (and 3 private copies) by sourcing the value from `EcusTenantContext`
instead, after updating `SyncController` to pass it in on every endpoint.

**Architecture:** `SyncController` already fetches `SyncSourceConfiguration mapping` before
setting context — it just wasn't passing `mapping.getId()` to `EcusTenantContext.set()`.
Once that 3rd arg is in the context, all mapper lookup code becomes dead weight and is deleted.
Tasks 1–3 form one atomic commit (SyncController + shared infrastructure). Tasks 4–6 each
clean up one group of mappers.

**Tech Stack:** Java 21, Spring Boot 3.3.3, Lombok, `EcusTenantContext` (ThreadLocal),
`AbstractEcusMapper`, Gradle (`./gradlew :datatp-egov-module-ecus-thaison:build`)

---

## Spec

`docs/superpowers/specs/2026-03-29-remove-getSyncSourceConfigurationId-design.md`

---

## File Map

| File | Action |
|---|---|
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncController.java` | Modify: 9 call sites 2-arg → 3-arg |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/context/EcusTenantContext.java` | Modify: add TODO to 2-arg overload |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/AbstractEcusMapper.java` | Modify: gut class (remove field + method + imports) |
| `…/logic/mapper/core/EcusSDonViMapper.java` | Modify: remove private copy, update lambda |
| `…/logic/mapper/partner/EcusDTOKHAIMDVNACCSMapper.java` | Modify: remove private copy, update lambda + processBatch |
| `…/logic/mapper/partner/EcusDTOKHAIMDVNACCS2Mapper.java` | Modify: remove private copy, update lambda + processBatch |
| 2 direct mappers: `EcusSPTVTMapper`, `EcusSPTTTMapper` | Modify: replace direct call (Case B) |
| 27 async AbstractEcusMapper subclasses | Modify: capture + 3-arg set + read from context (Case A) |

---

## Task 1: SyncController + EcusTenantContext + AbstractEcusMapper (foundation commit)

**Important:** All three files in this task MUST be committed together. The mapper changes
in Tasks 2–6 depend on `syncSourceConfigurationId` being in context, which requires
`SyncController` to pass it. Committing incrementally here would break a running system.

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncController.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/context/EcusTenantContext.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/AbstractEcusMapper.java`

- [ ] **Step 1.1: Update SyncController — 9 endpoints**

  In `SyncController.java`, find all 9 occurrences of `EcusTenantContext.set(ecusDbName, mapping.getCompanyId())`.
  They are at these approximate line numbers: **185, 217, 264, 287, 309, 331, 353, 375, 399**.
  (Line 241 is already 3-arg — leave it alone. Also leave the old commented-out line 240 in place.)

  Change each from:
  ```java
  EcusTenantContext.set(ecusDbName, mapping.getCompanyId());
  ```
  To:
  ```java
  EcusTenantContext.set(ecusDbName, mapping.getCompanyId(), mapping.getId());
  ```

- [ ] **Step 1.2: Add TODO comment to EcusTenantContext 2-arg overload**

  In `EcusTenantContext.java`, find the 2-arg overload (approx line 28):
  ```java
  public static void set(String ecusDbName, Long companyId) {
  ```
  Add a `// TODO` comment on the line immediately before it:
  ```java
  // TODO: remove once all callers migrated to 3-arg set()
  public static void set(String ecusDbName, Long companyId) {
      TENANT_INFO.set(new TenantInfo(ecusDbName, companyId, null));
  }
  ```

- [ ] **Step 1.3: Gut AbstractEcusMapper**

  Replace the entire content of `AbstractEcusMapper.java` with:
  ```java
  package com.egov.ecusthaison.logic.mapper;

  /**
   * Abstract base class for ECUS mappers.
   */
  public abstract class AbstractEcusMapper {
  }
  ```

- [ ] **Step 1.4: Build (expected to FAIL — proceed anyway)**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: COMPILE ERROR — ~27 mapper subclasses still reference `getSyncSourceConfigurationId`
  which no longer exists on `AbstractEcusMapper`. This is expected. Do NOT stop here.
  The call sites are removed in Tasks 4 and 5. Proceed with Step 1.5.

- [ ] **Step 1.5: Commit**

  ```bash
  git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncController.java \
          module/ecus-thaison/src/main/java/com/egov/ecusthaison/context/EcusTenantContext.java \
          module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/AbstractEcusMapper.java
  git commit -m "refactor: pass syncSourceConfigId from SyncController into EcusTenantContext, gut AbstractEcusMapper"
  ```

---

## Task 2: EcusSDonViMapper (private copy — lambda pattern)

`EcusSDonViMapper` does NOT extend `AbstractEcusMapper` — it has its own private copy of
the method. The call site is inside the async lambda body.

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/core/EcusSDonViMapper.java`

- [ ] **Step 2.1: Capture syncSourceConfigId before the lambda**

  In `syncEntity()`, find the block that captures context variables for async threads
  (approx lines 89-91):
  ```java
  // Capture context for async threads
  final String ecusDbName = EcusTenantContext.getEcusDbName();
  final Long capturedCompanyId = companyId;
  ```
  Add one line after:
  ```java
  final Long capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
  ```

- [ ] **Step 2.2: Update the lambda — 3-arg set + replace call**

  Inside the `CompletableFuture.supplyAsync` lambda (approx lines 97-103), change:
  ```java
  // Restore context in async thread
  EcusTenantContext.set(ecusDbName, capturedCompanyId);
  try {
      // Need to use Spring proxy to ensure transaction works
      EcusSDonViMapper self = ApplicationContextProvider.getBean(EcusSDonViMapper.class);
      Long syncSourceConfigId = getSyncSourceConfigurationId(capturedCompanyId);
      return self.processBatch(capturedCompanyId, currentPage, syncSourceConfigId);
  ```
  To:
  ```java
  // Restore context in async thread
  EcusTenantContext.set(ecusDbName, capturedCompanyId, capturedSyncSourceConfigId);
  try {
      // Need to use Spring proxy to ensure transaction works
      EcusSDonViMapper self = ApplicationContextProvider.getBean(EcusSDonViMapper.class);
      Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
      return self.processBatch(capturedCompanyId, currentPage, syncSourceConfigId);
  ```

- [ ] **Step 2.3: Remove dead comment in processSync**

  In the `processSync` method, find and delete the commented-out line (approx line 212):
  ```java
  // Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);
  ```

- [ ] **Step 2.4: Remove the private getSyncSourceConfigurationId method**

  Delete the entire private method starting at approx line 243:
  ```java
  private Long getSyncSourceConfigurationId(Long companyId) {
      // ... entire method body ...
  }
  ```
  Also remove the imports that are now unused:
  - `import com.egov.ecutoms.entity.SyncSourceConfiguration;`
  - `import com.egov.ecutoms.service.SyncSourceConfigurationService;`
  - `import org.springframework.beans.factory.annotation.Autowired;` (if no other `@Autowired` fields remain)
  - Any `@Autowired private SyncSourceConfigurationService syncSourceConfigurationService;` field declaration
  - `import java.util.Optional;` (if unused elsewhere in the file)
  - `@Slf4j` annotation and `import lombok.extern.slf4j.Slf4j;` (if no other log calls remain)

- [ ] **Step 2.5: Build**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: BUILD SUCCESSFUL.

- [ ] **Step 2.6: Commit**

  ```bash
  git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/core/EcusSDonViMapper.java
  git commit -m "refactor: remove private getSyncSourceConfigurationId from EcusSDonViMapper"
  ```

---

## Task 3: EcusDTOKHAIMDVNACCSMapper + EcusDTOKHAIMDVNACCS2Mapper (private copy — processBatch pattern)

These two mappers are identical in structure. The call site is inside `processBatch`, which
is invoked from inside the async lambda. The fix: capture the ID before lambdas, propagate
via context, read from context inside `processBatch`.

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/EcusDTOKHAIMDVNACCSMapper.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/EcusDTOKHAIMDVNACCS2Mapper.java`

Apply the same steps to both files:

- [ ] **Step 3.1: Capture syncSourceConfigId before the lambda (in syncEntity)**

  Find the context-capture block in `syncEntity()` (approx lines 122-125 in VNACCS,
  similar in VNACCS2) — the comment reads "Capture context (only ecusDbName and companyId
  - syncSourceConfigurationId will be fetched in processBatch)":
  ```java
  final String ecusDbName = EcusTenantContext.getEcusDbName();
  final Long companyId = EcusTenantContext.getCompanyId();
  ```
  Update the comment and add the capture:
  ```java
  final String ecusDbName = EcusTenantContext.getEcusDbName();
  final Long companyId = EcusTenantContext.getCompanyId();
  final Long capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
  ```

- [ ] **Step 3.2: Update lambda to 3-arg set**

  Inside the `CompletableFuture.supplyAsync` lambda (approx line 133 in VNACCS), change:
  ```java
  EcusTenantContext.set(ecusDbName, companyId);
  ```
  To:
  ```java
  EcusTenantContext.set(ecusDbName, companyId, capturedSyncSourceConfigId);
  ```

- [ ] **Step 3.3: Update processBatch to read from context instead of lookup**

  In `processBatch` (approx line 237 in VNACCS, 231 in VNACCS2), change:
  ```java
  final Long syncSourceConfigurationId = getSyncSourceConfigurationId(companyId);
  ```
  To:
  ```java
  final Long syncSourceConfigurationId = EcusTenantContext.getSyncSourceConfigurationId();
  ```

- [ ] **Step 3.4: Remove the private getSyncSourceConfigurationId method**

  Delete the entire private method (approx line 203 in VNACCS, 199 in VNACCS2) and its
  associated field declaration `@Autowired private SyncSourceConfigurationService ...`.
  Remove unused imports:
  - `import com.egov.ecutoms.entity.SyncSourceConfiguration;`
  - `import com.egov.ecutoms.service.SyncSourceConfigurationService;`
  - `import java.util.Optional;` (if unused elsewhere)

- [ ] **Step 3.5: Build**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: BUILD SUCCESSFUL.

- [ ] **Step 3.6: Commit**

  ```bash
  git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/EcusDTOKHAIMDVNACCSMapper.java \
          module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/EcusDTOKHAIMDVNACCS2Mapper.java
  git commit -m "refactor: remove private getSyncSourceConfigurationId from VNACCS mappers"
  ```

---

## Task 4: Case B — Direct (non-async) AbstractEcusMapper subclasses

`EcusSPTVTMapper` and `EcusSPTTTMapper` call `getSyncSourceConfigurationId(companyId)`
directly in `syncEntity()`, with no async thread involved — the simplest case.

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTVTMapper.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTTTMapper.java`

Apply to both files:

- [ ] **Step 4.1: Replace direct call**

  Find (approx line 48 in EcusSPTVTMapper):
  ```java
  Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);
  ```
  Replace with:
  ```java
  Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
  ```
  (The `EcusTenantContext` import is already present in both files.)

- [ ] **Step 4.2: Build**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: BUILD SUCCESSFUL (no call sites remain for the now-removed parent method).

- [ ] **Step 4.3: Commit**

  ```bash
  git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTVTMapper.java \
          module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTTTMapper.java
  git commit -m "refactor: replace getSyncSourceConfigurationId call in direct mappers (Case B)"
  ```

---

## Task 5: Case A — 27 async AbstractEcusMapper subclasses

These are the bulk of the work. Each file follows an identical pattern. The 27 files are:

**company/ (20 files — EcusSPTVTMapper and EcusSPTTTMapper already done in Task 4):**
`EcusSLOAI_KIENMapper`, `EcusSDVTMapper`, `EcusSNUOCMapper`, `EcusSNGTEMapper`,
`EcusSNGAN_HANGMapper`, `EcusSVB_PQMapper`, `EcusSHAIQUANMapper`, `EcusSCUAKHAUMapper`,
`EcusSCUAKHAUNNMapper`, `EcusSDIA_DIEMMapper`, `EcusSDIA_DIEM_THUPHIMapper`,
`EcusSMACACLOAIMapper`, `EcusSMA_MIENTHUEMapper`, `EcusSMA_AP_MIENTHUEMapper`,
`EcusSLOAI_GPMapper`, `EcusSLHINHMDMapper`, `EcusDCHUNGTUKEMMapper`,
`EcusREPORTSEXCELMapper`, `EcusSBIEU_THUE_TENMapper`, `EcusSDKGHMapper`

**partner/ (7 files):**
`EcusDTOKHAIMapper`, `EcusDHANGMDDKMapper`, `EcusDLOGINFOMapper`,
`EcusDMSGOUTREPMapper`, `EcusD_OLAMapper`, `EcusD_OLA_ContainerMapper`,
`EcusD_OLA_HangMapper`

> Note: verify the exact list at runtime with:
> ```bash
> grep -rl "getSyncSourceConfigurationId" \
>   module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/ \
>   module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/
> ```
> Files already handled (Tasks 3/4) will no longer appear in this list.

**Pattern to apply to every file:**

```java
// BEFORE (inside syncEntity, before the for-loop):
final String ecusDbName = EcusTenantContext.getEcusDbName();
final Long capturedCompanyId = companyId;

// AFTER — add one line:
final String ecusDbName = EcusTenantContext.getEcusDbName();
final Long capturedCompanyId = companyId;
final Long capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
```

```java
// BEFORE (inside lambda — context restore):
EcusTenantContext.set(ecusDbName, capturedCompanyId);

// AFTER:
EcusTenantContext.set(ecusDbName, capturedCompanyId, capturedSyncSourceConfigId);
```

```java
// BEFORE (inside lambda — lookup call):
Long syncSourceConfigId = getSyncSourceConfigurationId(capturedCompanyId);

// AFTER:
Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
```

**Variant for several partner/ mappers** — some files have NO lambda body call; the only
call site is inside a `@Transactional processSync` method invoked from the async thread via
Spring proxy. The context IS properly restored in the async thread before the proxy call,
so the same read-from-context replacement is safe:

```java
// BEFORE (inside processSync, called from async thread via Spring proxy):
Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);

// AFTER:
Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
```

- `EcusDHANGMDDKMapper`, `EcusDLOGINFOMapper`, `EcusDMSGOUTREPMapper`, `EcusDTOKHAIMapper`:
  the ONLY live call site is in `processSync` (no lambda body call).
- `EcusD_OLAMapper`, `EcusD_OLA_ContainerMapper`, `EcusD_OLA_HangMapper`:
  TWO call sites each — one already migrated in the capture block, one in `processSync`.

- [ ] **Step 5.1: Apply pattern to company/ mappers**

  Edit each file in `logic/mapper/company/` that still contains `getSyncSourceConfigurationId`
  (run the grep above to get the exact list after Tasks 4 completes). Apply the three
  substitutions described in the pattern above to each file.

- [ ] **Step 5.2: Build after company/ edits**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: BUILD SUCCESSFUL.

- [ ] **Step 5.3: Apply pattern to partner/ mappers**

  Edit each file in `logic/mapper/partner/` that still contains `getSyncSourceConfigurationId`
  (run the grep above to get the exact list). Apply the same three substitutions.

- [ ] **Step 5.4: Build after partner/ edits**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:build -x test
  ```
  Expected: BUILD SUCCESSFUL.

- [ ] **Step 5.5: Verify no call sites remain**

  ```bash
  grep -r "getSyncSourceConfigurationId" \
    module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/
  ```
  Expected: **no output**. If any matches appear, fix them before committing.

- [ ] **Step 5.6: Run tests**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:test
  ```
  Expected: all tests pass. Fix any failures before committing.

- [ ] **Step 5.7: Commit**

  ```bash
  git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/ \
          module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/
  git commit -m "refactor: replace getSyncSourceConfigurationId with context read in async mappers (Case A)"
  ```

---

## Final Verification

- [ ] **Grep: no remaining call sites**

  ```bash
  grep -r "getSyncSourceConfigurationId" module/ecus-thaison/src/main/java/
  ```
  Expected: no output.

- [ ] **Full module build + test**

  ```bash
  ./gradlew :datatp-egov-module-ecus-thaison:test
  ```
  Expected: all tests pass.
