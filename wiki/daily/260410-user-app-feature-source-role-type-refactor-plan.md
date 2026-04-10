# UserAppFeature `sourceRoleTypeId` Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire `UserAppFeature.sourceRoleTypeId` end-to-end so that CUSTOM vs ROLE permission rows are distinguished, synced deterministically (max-capability wins), and surfaced on the Identity detail screen, with the "Sync Permission" button materializing rows atomically in the same transaction.

**Architecture:** Backend fixes: single-line guard in `AppLogic.saveAppPermission` (covers all admin save paths), rewrite of `UserAppFeatureTemplateLogic.syncUserPermissions` with CUSTOM-collision filter and max-capability winner selection, direct in-transaction sync call added to both `IdentityEventLogic.syncRoles` and `syncIdentities`, TODO stubs at template save/delete, and SQL exposure of `source_role_type_id` / `source_role_type_label`. Frontend cleanup: drop the `templateAppMap` workaround and read the new fields directly.

**Tech Stack:** Java 17 + Spring Boot + JPA + Lombok (backend), Groovy SQL templates, JUnit 5 + Mockito + Spring Boot test slices, React + TypeScript + custom `@of1-webui/lib` (frontend).

**Spec:** `/Users/nqcdan/dev/wiki/wiki/daily/260410-user-app-feature-source-role-type-refactor.md`

---

## File Structure

### Backend — files to create

- `of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java` — unit tests for `syncUserPermissions` (tests 1–8 from the spec).
- `of1-core/module/platform-federation/src/test/java/datatp/platform/identity/queue/IdentityEventLogicSyncTest.java` — integration tests for `syncRoles` and `syncIdentities` in-transaction materialization (tests 9–11).

### Backend — files to modify

- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/groovy/AppSql.groovy` — add `source_role_type_label` to `SearchUserAppPermissions`.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java` — single-line edit in `saveAppPermission`.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java` — rewrite `syncUserPermissions`, add rank helpers, replace `syncUserAppFeatures` body with TODO stub, add TODO markers in save/delete paths.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java` — constructor-inject `UserAppFeatureTemplateLogic`, call `syncUserPermissions` inside `syncRoles` and `syncIdentities`.

### Frontend — files to modify

- `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentityAppFeatureList.tsx` — drop `templateAppMap`, `loadTemplates`, `componentDidMount` override; replace column `customRender` to read `sourceRoleTypeLabel`; update `orderBy`.
- `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentity.tsx` — remove `loadTemplates()` call from `onRolesChanged`.

---

## Task 1: BE-5 — Force `sourceRoleTypeId = null` in `AppLogic.saveAppPermission`

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java` (method `saveAppPermission`)

**Rationale:** Smallest atomic change. All admin save paths (Add, Edit, bulk capability update, bulk data-scope update) delegate to this one method, so a single edit covers every admin-initiated write. Ship first to unblock downstream work.

- [ ] **Step 1: Read the file and locate `saveAppPermission`**

Open `AppLogic.java` and verify the method signature matches:
```java
public UserAppFeature saveAppPermission(ClientContext client, UserAppFeature permission) {
  permission.set(client);
  return permissionRepo.save(permission);
}
```

- [ ] **Step 2: Apply the edit**

Add one line at the top of the method body:
```java
public UserAppFeature saveAppPermission(ClientContext client, UserAppFeature permission) {
  permission.setSourceRoleTypeId(null);   // BE-5: admin Add/Edit/Update is always CUSTOM
  permission.set(client);
  return permissionRepo.save(permission);
}
```

- [ ] **Step 3: Build to verify no compile error**

Run from `of1-core/module/platform-federation`:
```
mvn -pl module/platform-federation -am compile -DskipTests -o
```
(Adjust module path / build command to match repo conventions; if Gradle, use `./gradlew :platform-federation:compileJava`.)

Expected: `BUILD SUCCESS` with no errors.

- [ ] **Step 4: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java
git commit -m "fix(security): force sourceRoleTypeId=null on saveAppPermission

Admin-initiated Add/Edit/Update paths all delegate to saveAppPermission.
Setting sourceRoleTypeId=null explicitly ensures ROLE rows become CUSTOM
on edit, preventing silent reset on the next syncUserPermissions call."
```

---

## Task 2: BE-3 setup — Add rank helpers to `UserAppFeatureTemplateLogic`

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java` (add private helpers)
- Create: `of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java` (test scaffolding)

**Rationale:** Pure functions are the cheapest to TDD. Get the ranking helpers correct and covered first, then build the sync logic on top.

- [ ] **Step 1: Create the test file with scaffolding**

Create `UserAppFeatureTemplateLogicTest.java`:
```java
package datatp.platform.resource;

import static org.junit.jupiter.api.Assertions.*;

import datatp.platform.resource.logic.UserAppFeatureTemplateLogic;
import net.datatp.security.client.Capability;
import net.datatp.security.client.DataScope;
import org.junit.jupiter.api.Test;

class UserAppFeatureTemplateLogicTest {
  // Rank helper tests
  @Test
  void capabilityRank_ordersAdminHighestNoneLowest() {
    fail("Not yet implemented");
  }

  @Test
  void dataScopeRank_ordersAllHighestOwnerLowest() {
    fail("Not yet implemented");
  }
}
```

- [ ] **Step 2: Run the tests to verify they fail**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest
```

Expected: 2 tests fail with `Not yet implemented`.

- [ ] **Step 3: Write the first real test — capability ordering**

Replace `capabilityRank_ordersAdminHighestNoneLowest` body:
```java
@Test
void capabilityRank_ordersAdminHighestNoneLowest() {
  assertTrue(UserAppFeatureTemplateLogic.capabilityRank(Capability.Admin)
      > UserAppFeatureTemplateLogic.capabilityRank(Capability.Moderator));
  assertTrue(UserAppFeatureTemplateLogic.capabilityRank(Capability.Moderator)
      > UserAppFeatureTemplateLogic.capabilityRank(Capability.Write));
  assertTrue(UserAppFeatureTemplateLogic.capabilityRank(Capability.Write)
      > UserAppFeatureTemplateLogic.capabilityRank(Capability.Read));
  assertTrue(UserAppFeatureTemplateLogic.capabilityRank(Capability.Read)
      > UserAppFeatureTemplateLogic.capabilityRank(Capability.None));
  assertEquals(0, UserAppFeatureTemplateLogic.capabilityRank(null));
}
```

- [ ] **Step 4: Run it — expect compile error (helper doesn't exist)**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest#capabilityRank_ordersAdminHighestNoneLowest
```

Expected: compile failure "cannot find symbol: method capabilityRank".

- [ ] **Step 5: Add the helper in `UserAppFeatureTemplateLogic.java`**

Add inside the class, near the bottom (package-private so tests can reach it without reflection):
```java
static int capabilityRank(Capability c) {
  if (c == null) return 0;
  switch (c) {
    case Admin:     return 4;
    case Moderator: return 3;
    case Write:     return 2;
    case Read:      return 1;
    case None:      return 0;
    default:        return 0;
  }
}
```

Before writing, verify the exact enum constant names by reading `net.datatp.security.client.Capability`. Adjust casing/spelling if the enum uses different labels (e.g. `ADMIN` vs `Admin`).

- [ ] **Step 6: Run the test — expect pass**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest#capabilityRank_ordersAdminHighestNoneLowest
```

Expected: 1 test passed.

- [ ] **Step 7: Write the dataScope test**

Replace `dataScopeRank_ordersAllHighestOwnerLowest` body:
```java
@Test
void dataScopeRank_ordersAllHighestOwnerLowest() {
  assertTrue(UserAppFeatureTemplateLogic.dataScopeRank(DataScope.All)
      > UserAppFeatureTemplateLogic.dataScopeRank(DataScope.Company));
  assertTrue(UserAppFeatureTemplateLogic.dataScopeRank(DataScope.Company)
      > UserAppFeatureTemplateLogic.dataScopeRank(DataScope.Group));
  assertTrue(UserAppFeatureTemplateLogic.dataScopeRank(DataScope.Group)
      > UserAppFeatureTemplateLogic.dataScopeRank(DataScope.Owner));
  assertEquals(0, UserAppFeatureTemplateLogic.dataScopeRank(null));
}
```

- [ ] **Step 8: Run — expect compile failure, then add helper**

Add to `UserAppFeatureTemplateLogic.java` below `capabilityRank`:
```java
static int dataScopeRank(DataScope s) {
  if (s == null) return 0;
  switch (s) {
    case All:     return 4;
    case Company: return 3;
    case Group:   return 2;
    case Owner:   return 1;
    default:      return 0;
  }
}
```

Again verify enum constant names against `net.datatp.security.client.DataScope`.

- [ ] **Step 9: Run both rank tests — expect pass**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest
```

Expected: 2/2 passed.

- [ ] **Step 10: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java \
        of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java
git commit -m "test(security): add capabilityRank/dataScopeRank helpers with unit tests"
```

---

## Task 3: BE-3 — Rewrite `syncUserPermissions` with CUSTOM guard and max-capability winner

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java` (method `syncUserPermissions`)
- Modify: `of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java` (add tests 1–8)

**Rationale:** This is the heart of the refactor. Build up TDD style, one invariant at a time. Mock `UserAppFeatureTemplateRepository` and `AppPermissionRepository` to keep tests fast and hermetic.

- [ ] **Step 1: Extend the test class with mock infrastructure**

Add at the top of `UserAppFeatureTemplateLogicTest.java`:
```java
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;

import datatp.platform.resource.entity.UserAppFeature;
import datatp.platform.resource.entity.UserAppFeatureTemplate;
import datatp.platform.resource.repository.AppPermissionRepository;
import datatp.platform.resource.repository.UserAppFeatureTemplateRepository;
import java.util.*;
import net.datatp.security.client.AccessType;
import net.datatp.security.client.ClientContext;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.ArgumentCaptor;
```

Add fields and setup:
```java
private UserAppFeatureTemplateLogic logic;
private UserAppFeatureTemplateRepository templateRepo;
private AppPermissionRepository permissionRepo;
private ClientContext ctx;

private static final Long COMPANY_ID = 100L;
private static final Long ACCOUNT_ID = 200L;

@BeforeEach
void setUp() throws Exception {
  logic = new UserAppFeatureTemplateLogic();
  templateRepo = mock(UserAppFeatureTemplateRepository.class);
  permissionRepo = mock(AppPermissionRepository.class);
  ctx = mock(ClientContext.class);

  // Use reflection to set @Autowired private fields.
  setField(logic, "templateRepo", templateRepo);
  setField(logic, "userAppFeatureRepo", permissionRepo);
}

private static void setField(Object target, String name, Object value) throws Exception {
  java.lang.reflect.Field f = target.getClass().getDeclaredField(name);
  f.setAccessible(true);
  f.set(target, value);
}

private static UserAppFeature custom(Long appId, Capability cap) {
  UserAppFeature u = new UserAppFeature();
  u.setAppId(appId);
  u.setAccountId(ACCOUNT_ID);
  u.setCompanyId(COMPANY_ID);
  u.setSourceRoleTypeId(null);
  u.setAccessType(AccessType.Employee);
  u.setCapability(cap);
  u.setDataScope(DataScope.Owner);
  return u;
}

private static UserAppFeature roleSourced(Long appId, Long roleTypeId, Capability cap, DataScope scope) {
  UserAppFeature u = new UserAppFeature();
  u.setAppId(appId);
  u.setAccountId(ACCOUNT_ID);
  u.setCompanyId(COMPANY_ID);
  u.setSourceRoleTypeId(roleTypeId);
  u.setAccessType(AccessType.Employee);
  u.setCapability(cap);
  u.setDataScope(scope);
  return u;
}

private static UserAppFeatureTemplate template(Long roleTypeId, Long appId, Capability cap, DataScope scope) {
  UserAppFeatureTemplate t = new UserAppFeatureTemplate();
  t.setRoleTypeId(roleTypeId);
  t.setAppFeatureId(appId);
  t.setCompanyId(COMPANY_ID);
  t.setAccessType(AccessType.Employee);
  t.setCapability(cap);
  t.setDataScope(scope);
  return t;
}
```

Verify the setter names (`setRoleTypeId`, `setAppFeatureId`, etc.) match the actual `UserAppFeatureTemplate` entity — read its source to be sure. Adjust if different.

- [ ] **Step 2: Write test #1 — empty roleTypeIds deletes only ROLE rows**

```java
@Test
void syncWithEmptyRoleTypeIds_deletesAllRoleSourcedRowsOnly() {
  UserAppFeature custom1 = custom(1L, Capability.Read);
  UserAppFeature custom2 = custom(2L, Capability.Write);
  UserAppFeature role1 = roleSourced(3L, 10L, Capability.Read, DataScope.Owner);
  UserAppFeature role2 = roleSourced(4L, 10L, Capability.Write, DataScope.Owner);
  UserAppFeature role3 = roleSourced(5L, 11L, Capability.Admin, DataScope.All);

  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of(custom1, custom2, role1, role2, role3));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of());

  ArgumentCaptor<List<UserAppFeature>> deleteCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).deleteAll(deleteCaptor.capture());
  List<UserAppFeature> deleted = deleteCaptor.getValue();
  assertEquals(3, deleted.size());
  assertTrue(deleted.contains(role1));
  assertTrue(deleted.contains(role2));
  assertTrue(deleted.contains(role3));
  assertFalse(deleted.contains(custom1));
  assertFalse(deleted.contains(custom2));

  verify(permissionRepo, never()).saveAll(any());
  verifyNoInteractions(templateRepo);
}
```

- [ ] **Step 3: Run — expect fail (existing method may partially work; check)**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest#syncWithEmptyRoleTypeIds_deletesAllRoleSourcedRowsOnly
```

If the existing implementation already handles this, it passes — fine, move on. If it fails, implement the minimum to pass (likely already does).

- [ ] **Step 4: Write test #5 — CUSTOM collision wins**

```java
@Test
void syncWithCustomCollision_customWinsAndTemplateSkipped() {
  UserAppFeature customA = custom(1L, Capability.Read);
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of(customA));
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L))))
      .thenReturn(List.of(template(10L, 1L, Capability.Write, DataScope.Company)));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L));

  // saveAll must never be called with a row for appId=1
  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo, atMost(1)).saveAll(saveCaptor.capture());
  if (!saveCaptor.getAllValues().isEmpty()) {
    List<UserAppFeature> saved = saveCaptor.getValue();
    assertTrue(saved.stream().noneMatch(u -> Long.valueOf(1L).equals(u.getAppId())),
        "No save should touch appId=1 because custom override exists");
  }
  // CUSTOM row must not be deleted
  verify(permissionRepo, never()).deleteAll(argThat(list -> list.contains(customA)));
}
```

- [ ] **Step 5: Run — expect fail because current code will try to insert a fresh row for appId=1**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest#syncWithCustomCollision_customWinsAndTemplateSkipped
```

Expected: FAIL — either assertion violation on save, or `saveAll` called with a row for appId=1.

- [ ] **Step 6: Rewrite `syncUserPermissions` to add CUSTOM filter**

Replace the entire method body with the new implementation (from spec BE-3). Full replacement, no patching:

```java
public void syncUserPermissions(ClientContext ctx, Long companyId, Long accountId, List<Long> roleTypeIds) {
  List<UserAppFeature> existingPermissions =
      userAppFeatureRepo.findAppPermissionByAccountId(companyId, accountId);

  List<UserAppFeature> roleSourced = existingPermissions.stream()
      .filter(p -> p.getSourceRoleTypeId() != null)
      .collect(Collectors.toList());

  if (roleTypeIds == null || roleTypeIds.isEmpty()) {
    if (!roleSourced.isEmpty()) userAppFeatureRepo.deleteAll(roleSourced);
    return;
  }

  Set<Long> customAppIds = existingPermissions.stream()
      .filter(p -> p.getSourceRoleTypeId() == null)
      .map(UserAppFeature::getAppId)
      .collect(Collectors.toSet());

  List<UserAppFeatureTemplate> rawTemplates =
      templateRepo.findByRoleTypeIdIn(companyId, roleTypeIds);

  List<UserAppFeatureTemplate> templates = rawTemplates.stream()
      .filter(t -> !customAppIds.contains(t.getAppFeatureId()))
      .collect(Collectors.toList());

  Comparator<UserAppFeatureTemplate> bestFirst =
      Comparator
          .comparingInt((UserAppFeatureTemplate t) -> capabilityRank(t.getCapability())).reversed()
          .thenComparing(Comparator.comparingInt(
              (UserAppFeatureTemplate t) -> dataScopeRank(t.getDataScope())).reversed())
          .thenComparingLong(UserAppFeatureTemplate::getRoleTypeId);

  Map<Long, UserAppFeatureTemplate> winnerByAppId = new HashMap<>();
  for (UserAppFeatureTemplate t : templates) {
    winnerByAppId.merge(t.getAppFeatureId(), t,
        (a, b) -> bestFirst.compare(a, b) <= 0 ? a : b);
  }

  Map<Long, UserAppFeature> sourcedByAppId = roleSourced.stream()
      .collect(Collectors.toMap(UserAppFeature::getAppId, p -> p, (p1, p2) -> p1));

  List<UserAppFeature> toSave = new ArrayList<>();
  for (Map.Entry<Long, UserAppFeatureTemplate> e : winnerByAppId.entrySet()) {
    Long appId = e.getKey();
    UserAppFeatureTemplate winner = e.getValue();
    UserAppFeature current = sourcedByAppId.get(appId);

    if (current == null) {
      UserAppFeature fresh = new UserAppFeature();
      fresh.setAppId(appId);
      fresh.setAccountId(accountId);
      fresh.setCompanyId(companyId);
      fresh.setSourceRoleTypeId(winner.getRoleTypeId());
      fresh.setAccessType(winner.getAccessType());
      fresh.setCapability(winner.getCapability());
      fresh.setDataScope(winner.getDataScope());
      fresh.set(ctx);
      toSave.add(fresh);
    } else {
      current.setSourceRoleTypeId(winner.getRoleTypeId());
      current.setAccessType(winner.getAccessType());
      current.setCapability(winner.getCapability());
      current.setDataScope(winner.getDataScope());
      toSave.add(current);
    }
  }

  if (!toSave.isEmpty()) {
    userAppFeatureRepo.saveAll(toSave);
  }

  Set<Long> validAppFeatureIds = winnerByAppId.keySet();
  List<UserAppFeature> toDelete = roleSourced.stream()
      .filter(p -> !validAppFeatureIds.contains(p.getAppId()))
      .collect(Collectors.toList());

  if (!toDelete.isEmpty()) {
    userAppFeatureRepo.deleteAll(toDelete);
  }
}
```

Add imports at the top of the file if missing: `java.util.Comparator`, `java.util.HashMap`, `java.util.Map`.

- [ ] **Step 7: Run tests 1 and 5 — expect pass**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest#syncWithEmptyRoleTypeIds_deletesAllRoleSourcedRowsOnly+syncWithCustomCollision_customWinsAndTemplateSkipped
```

Expected: 2/2 passed.

- [ ] **Step 8: Write tests #2, #3, #4 (baseline sync behavior)**

```java
@Test
void syncWithNewRoleType_insertsFreshRoleSourcedRows() {
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of());
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L))))
      .thenReturn(List.of(
          template(10L, 1L, Capability.Read, DataScope.Owner),
          template(10L, 2L, Capability.Write, DataScope.Owner)
      ));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L));

  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).saveAll(saveCaptor.capture());
  List<UserAppFeature> saved = saveCaptor.getValue();
  assertEquals(2, saved.size());
  assertTrue(saved.stream().allMatch(u -> Long.valueOf(10L).equals(u.getSourceRoleTypeId())));
  assertTrue(saved.stream().anyMatch(u -> Long.valueOf(1L).equals(u.getAppId())));
  assertTrue(saved.stream().anyMatch(u -> Long.valueOf(2L).equals(u.getAppId())));
}

@Test
void syncWithExistingRoleRows_refreshesCapabilityFromTemplate() {
  UserAppFeature existing = roleSourced(1L, 10L, Capability.Read, DataScope.Owner);
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of(existing));
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L))))
      .thenReturn(List.of(template(10L, 1L, Capability.Write, DataScope.Company)));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L));

  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).saveAll(saveCaptor.capture());
  List<UserAppFeature> saved = saveCaptor.getValue();
  assertEquals(1, saved.size());
  UserAppFeature row = saved.get(0);
  assertSame(existing, row); // in-place update preserves identity
  assertEquals(Capability.Write, row.getCapability());
  assertEquals(DataScope.Company, row.getDataScope());
  assertEquals(Long.valueOf(10L), row.getSourceRoleTypeId());
}

@Test
void syncRemovesRoleRowsNotBackedByAnyTemplate() {
  UserAppFeature orphanRow = roleSourced(1L, 10L, Capability.Read, DataScope.Owner);
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of(orphanRow));
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L))))
      .thenReturn(List.of()); // role type no longer has any template for appId=1

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L));

  ArgumentCaptor<List<UserAppFeature>> deleteCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).deleteAll(deleteCaptor.capture());
  assertEquals(1, deleteCaptor.getValue().size());
  assertSame(orphanRow, deleteCaptor.getValue().get(0));
}
```

- [ ] **Step 9: Run — expect all 3 pass**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest
```

Expected: 5/5 passed (tests 1–4 + CUSTOM collision).

- [ ] **Step 10: Write tests #6, #7, #8 — multi-role tie-breakers**

```java
@Test
void syncWithMultiRoleOverlap_picksMaxCapability() {
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of());
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L, 20L))))
      .thenReturn(List.of(
          template(10L, 1L, Capability.Read, DataScope.Owner),
          template(20L, 1L, Capability.Write, DataScope.Company)
      ));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L, 20L));

  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).saveAll(saveCaptor.capture());
  List<UserAppFeature> saved = saveCaptor.getValue();
  assertEquals(1, saved.size());
  UserAppFeature row = saved.get(0);
  assertEquals(Capability.Write, row.getCapability());
  assertEquals(DataScope.Company, row.getDataScope());
  assertEquals(Long.valueOf(20L), row.getSourceRoleTypeId());
}

@Test
void syncWithMultiRoleSameCapability_tieBreaksByDataScope() {
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of());
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L, 20L))))
      .thenReturn(List.of(
          template(10L, 1L, Capability.Write, DataScope.Owner),
          template(20L, 1L, Capability.Write, DataScope.Company)
      ));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L, 20L));

  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).saveAll(saveCaptor.capture());
  UserAppFeature row = saveCaptor.getValue().get(0);
  assertEquals(DataScope.Company, row.getDataScope());
  assertEquals(Long.valueOf(20L), row.getSourceRoleTypeId());
}

@Test
void syncWithMultiRoleSameCapAndScope_tieBreaksBySmallerRoleTypeId() {
  when(permissionRepo.findAppPermissionByAccountId(COMPANY_ID, ACCOUNT_ID))
      .thenReturn(List.of());
  // Intentionally shuffle order to prove determinism
  when(templateRepo.findByRoleTypeIdIn(eq(COMPANY_ID), eq(List.of(10L, 20L))))
      .thenReturn(List.of(
          template(20L, 1L, Capability.Write, DataScope.Owner),
          template(10L, 1L, Capability.Write, DataScope.Owner)
      ));

  logic.syncUserPermissions(ctx, COMPANY_ID, ACCOUNT_ID, List.of(10L, 20L));

  ArgumentCaptor<List<UserAppFeature>> saveCaptor = ArgumentCaptor.forClass(List.class);
  verify(permissionRepo).saveAll(saveCaptor.capture());
  UserAppFeature row = saveCaptor.getValue().get(0);
  assertEquals(Long.valueOf(10L), row.getSourceRoleTypeId());
}
```

- [ ] **Step 11: Run — expect all 8 pass**

```
mvn -pl module/platform-federation test -Dtest=UserAppFeatureTemplateLogicTest
```

Expected: 8/8 passed (rank helpers + all 8 sync scenarios).

- [ ] **Step 12: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java \
        of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java
git commit -m "fix(security): rewrite syncUserPermissions with CUSTOM guard + max-capability

- Filter out templates targeting appIds that have CUSTOM (sourceRoleTypeId=null) rows
  to preserve admin overrides and prevent unique-constraint violations.
- Group templates by appFeatureId and pick winner via deterministic comparator:
  capability desc > dataScope desc > roleTypeId asc.
- Covered by 8 unit tests in UserAppFeatureTemplateLogicTest."
```

---

## Task 4: BE-4 — TODO stubs for template save/delete

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java` (`syncUserAppFeatures`, `saveUserAppFeatureTemplate`, `deleteUserAppFeatureTemplatesByIds`)

**Rationale:** No behavior change, just documentation that async re-sync is a deferred concern. Keeps the call-sites honest for whoever implements the consumer.

- [ ] **Step 1: Delete commented-out body of `syncUserAppFeatures` and replace with stub**

Replace the entire method with:
```java
/**
 * Trigger re-materialization of UserAppFeature rows for every account that
 * currently holds {@code roleTypeId}, after a template change on that role type.
 *
 * TODO: Publish TemplateChanged(roleTypeId) async event via IdentityEventProducer.
 * A consumer will iterate IdentityRole by roleTypeId, then for each account call
 * syncUserPermissions with the account's current roleTypeIds set.
 *
 * Until the consumer is implemented, this is a no-op. Admins must click
 * "Sync Permission" on each affected identity manually.
 */
public void syncUserAppFeatures(ClientContext ctx, Long roleTypeId) {
  // No-op. See TODO above.
}
```

- [ ] **Step 2: Add TODO marker in `saveUserAppFeatureTemplate`**

```java
public UserAppFeatureTemplate saveUserAppFeatureTemplate(ClientContext ctx, UserAppFeatureTemplate template) {
  template.set(ctx);
  template.setCompanyId(ctx.getCompanyId());
  UserAppFeatureTemplate saved = templateRepo.save(template);
  // TODO: trigger syncUserAppFeatures(ctx, saved.getRoleTypeId()) when async
  // re-sync consumer is in place. See syncUserAppFeatures() javadoc.
  return saved;
}
```

- [ ] **Step 3: Add TODO marker in `deleteUserAppFeatureTemplatesByIds`**

At the end of the existing method, before the closing brace:
```java
// TODO: for each distinct affected roleTypeId, call syncUserAppFeatures(ctx, roleTypeId)
// when the async re-sync consumer is in place. Role type IDs are available on the
// loaded `templates` list above.
```

- [ ] **Step 4: Build to verify**

```
mvn -pl module/platform-federation compile -DskipTests -o
```

Expected: `BUILD SUCCESS`.

- [ ] **Step 5: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java
git commit -m "chore(security): stub syncUserAppFeatures with TODO for async consumer"
```

---

## Task 5: BE-2 — `IdentityEventLogic.syncRoles` materializes permissions in-transaction

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java` (constructor injection + call `syncUserPermissions` inside `syncRoles`)
- Create: `of1-core/module/platform-federation/src/test/java/datatp/platform/identity/queue/IdentityEventLogicSyncTest.java` (integration tests 9, 10)

**Rationale:** This is the customer-facing fix — the "Sync Permission" button actually materializes rows. Convert to constructor injection first so the logic is mockable in a plain unit test.

- [ ] **Step 1: Convert `IdentityEventLogic` to constructor injection for the new dependency**

Open `IdentityEventLogic.java`. Keep existing `@Autowired` fields as-is (don't churn unrelated code), but add a new constructor-injected field:

```java
private final UserAppFeatureTemplateLogic templateLogic;

public IdentityEventLogic(UserAppFeatureTemplateLogic templateLogic) {
  this.templateLogic = templateLogic;
}
```

Note: if the class already has a constructor, add the new parameter to it. If Spring complains about ambiguous constructors, annotate the new one with `@Autowired`.

- [ ] **Step 2: Write integration test #9 — sync materializes rows**

Create `IdentityEventLogicSyncTest.java`:
```java
package datatp.platform.identity.queue;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import datatp.platform.identity.entity.Identity;
import datatp.platform.identity.entity.IdentityRole;
import datatp.platform.identity.repository.IdentityRepository;
import datatp.platform.identity.repository.IdentityRoleRepository;
import datatp.platform.resource.logic.UserAppFeatureTemplateLogic;
import java.util.List;
import net.datatp.security.client.ClientContext;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class IdentityEventLogicSyncTest {
  private IdentityEventLogic eventLogic;
  private UserAppFeatureTemplateLogic templateLogic;
  private IdentityRepository identityRepo;
  private IdentityRoleRepository identityRoleRepo;
  private IdentityEventProducer eventProducer;
  private ClientContext ctx;

  private static final Long COMPANY_ID = 100L;
  private static final Long IDENTITY_ID = 500L;
  private static final Long ACCOUNT_ID = 600L;

  @BeforeEach
  void setUp() throws Exception {
    templateLogic = mock(UserAppFeatureTemplateLogic.class);
    identityRepo = mock(IdentityRepository.class);
    identityRoleRepo = mock(IdentityRoleRepository.class);
    eventProducer = mock(IdentityEventProducer.class);
    ctx = mock(ClientContext.class);
    when(ctx.getCompanyId()).thenReturn(COMPANY_ID);

    eventLogic = new IdentityEventLogic(templateLogic);
    setField(eventLogic, "identityRepo", identityRepo);
    setField(eventLogic, "identityRoleRepo", identityRoleRepo);
    setField(eventLogic, "eventProducer", eventProducer);
  }

  private static void setField(Object target, String name, Object value) throws Exception {
    java.lang.reflect.Field f = target.getClass().getDeclaredField(name);
    f.setAccessible(true);
    f.set(target, value);
  }

  private static Identity identity(Long accountId) {
    Identity i = new Identity();
    // Use the entity's available setters (verify against Identity.java)
    try {
      java.lang.reflect.Field idField = Identity.class.getSuperclass().getDeclaredField("id");
      idField.setAccessible(true);
      idField.set(i, IDENTITY_ID);
    } catch (Exception ignored) {}
    i.setAccountId(accountId);
    return i;
  }

  private static IdentityRole role(Long roleTypeId) {
    IdentityRole r = new IdentityRole();
    r.setRoleTypeId(roleTypeId);
    // Ensure change request is non-null — sync sets PROCESSED on it.
    // Use whatever the entity API requires; if a no-arg ChangeRequest needs to be attached, attach one.
    return r;
  }

  @Test
  void syncRoles_materializesPermissionsInSameTransaction() {
    Identity id = identity(ACCOUNT_ID);
    IdentityRole r1 = role(10L);
    IdentityRole r2 = role(20L);

    when(identityRepo.getById(IDENTITY_ID)).thenReturn(id);
    when(identityRoleRepo.findByIds(eq(COMPANY_ID), eq(List.of(30L, 40L))))
        .thenReturn(List.of(r1, r2));

    eventLogic.syncRoles(ctx, IDENTITY_ID, List.of(30L, 40L));

    // Assert: permissions sync was called with distinct roleTypeIds
    ArgumentCaptor<List<Long>> captor = ArgumentCaptor.forClass(List.class);
    verify(templateLogic).syncUserPermissions(eq(ctx), eq(COMPANY_ID), eq(ACCOUNT_ID), captor.capture());
    assertEquals(List.of(10L, 20L), captor.getValue());

    // Assert: event was still published
    verify(eventProducer).send(eq(ctx), any(IdentityEvent.class));
  }

  @Test
  void syncRoles_skipsSyncWhenAccountIdIsNull() {
    Identity id = identity(null);
    when(identityRepo.getById(IDENTITY_ID)).thenReturn(id);
    when(identityRoleRepo.findByIds(anyLong(), anyList())).thenReturn(List.of());

    eventLogic.syncRoles(ctx, IDENTITY_ID, List.of());

    verifyNoInteractions(templateLogic);
  }

  @Test
  void syncRoles_propagatesExceptionFromSyncUserPermissions() {
    Identity id = identity(ACCOUNT_ID);
    IdentityRole r1 = role(10L);
    when(identityRepo.getById(IDENTITY_ID)).thenReturn(id);
    when(identityRoleRepo.findByIds(eq(COMPANY_ID), eq(List.of(30L))))
        .thenReturn(List.of(r1));
    doThrow(new RuntimeException("boom"))
        .when(templateLogic).syncUserPermissions(any(), any(), any(), any());

    assertThrows(RuntimeException.class,
        () -> eventLogic.syncRoles(ctx, IDENTITY_ID, List.of(30L)));

    // Event must NOT be published on failure — transaction would rollback
    verify(eventProducer, never()).send(any(), any());
  }
}
```

Note on test #3 (`propagatesExceptionFromSyncUserPermissions`): this is the "rollback on failure" check (test #10 from the spec). We assert the exception propagates; the actual DB rollback happens at the `@Transactional` service boundary and is tested implicitly.

- [ ] **Step 3: Run tests — expect fail (method not yet calling syncUserPermissions)**

```
mvn -pl module/platform-federation test -Dtest=IdentityEventLogicSyncTest
```

Expected: `syncRoles_materializesPermissionsInSameTransaction` fails because `templateLogic.syncUserPermissions` is never called.

- [ ] **Step 4: Patch `syncRoles` to call `syncUserPermissions`**

Edit `IdentityEventLogic.syncRoles`. After the existing `identityRoleRepo.saveAll(roles)` and before the `IdentityEvent` construction, insert:

```java
Long accountId = identity.getAccountId();
if (accountId != null) {
  List<Long> roleTypeIds = roles.stream()
      .map(IdentityRole::getRoleTypeId)
      .distinct()
      .collect(Collectors.toList());
  templateLogic.syncUserPermissions(ctx, ctx.getCompanyId(), accountId, roleTypeIds);
}
```

Add `import java.util.stream.Collectors;` if not already imported.

- [ ] **Step 5: Run tests — expect pass**

```
mvn -pl module/platform-federation test -Dtest=IdentityEventLogicSyncTest
```

Expected: 3/3 passed.

- [ ] **Step 6: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java \
        of1-core/module/platform-federation/src/test/java/datatp/platform/identity/queue/IdentityEventLogicSyncTest.java
git commit -m "feat(security): syncRoles materializes UserAppFeature rows in-transaction

IdentityEventLogic.syncRoles now calls UserAppFeatureTemplateLogic.syncUserPermissions
directly, inside the existing @Transactional boundary on IdentityEventService.syncRoles.
Failures roll back both the IdentityRole changeRequest ack and the permission sync.

Covered by IdentityEventLogicSyncTest (3 tests)."
```

---

## Task 6: BE-2b — `IdentityEventLogic.syncIdentities` also materializes permissions

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java` (method `syncIdentities`)
- Modify: `of1-core/module/platform-federation/src/test/java/datatp/platform/identity/queue/IdentityEventLogicSyncTest.java` (add test #11)

**Rationale:** The second entry point must not diverge. Test first, patch, commit.

- [ ] **Step 1: Add test for bulk sync**

Append to `IdentityEventLogicSyncTest.java`:
```java
@Test
void syncIdentities_materializesPermissionsPerIdentity() {
  Long id1 = 501L, id2 = 502L, acc1 = 601L, acc2 = 602L;
  Identity i1 = new Identity();
  try { java.lang.reflect.Field f = Identity.class.getSuperclass().getDeclaredField("id");
    f.setAccessible(true); f.set(i1, id1); } catch (Exception ignored) {}
  i1.setAccountId(acc1);

  Identity i2 = new Identity();
  try { java.lang.reflect.Field f = Identity.class.getSuperclass().getDeclaredField("id");
    f.setAccessible(true); f.set(i2, id2); } catch (Exception ignored) {}
  i2.setAccountId(acc2);

  IdentityRole r1 = role(11L);
  IdentityRole r2 = role(12L);

  when(identityRepo.findByIds(eq(List.of(id1, id2)))).thenReturn(List.of(i1, i2));
  when(identityRepo.save(any(Identity.class))).thenAnswer(inv -> inv.getArgument(0));
  when(identityRoleRepo.getRoleByIdentityId(eq(COMPANY_ID), eq(id1))).thenReturn(List.of(r1));
  when(identityRoleRepo.getRoleByIdentityId(eq(COMPANY_ID), eq(id2))).thenReturn(List.of(r2));

  eventLogic.syncIdentities(ctx, List.of(id1, id2));

  verify(templateLogic).syncUserPermissions(ctx, COMPANY_ID, acc1, List.of(11L));
  verify(templateLogic).syncUserPermissions(ctx, COMPANY_ID, acc2, List.of(12L));
  verify(eventProducer, times(2)).send(eq(ctx), any(IdentityEvent.class));
}
```

- [ ] **Step 2: Run — expect fail**

```
mvn -pl module/platform-federation test -Dtest=IdentityEventLogicSyncTest#syncIdentities_materializesPermissionsPerIdentity
```

Expected: verification fails because `syncIdentities` does not yet call `templateLogic.syncUserPermissions`.

- [ ] **Step 3: Patch `syncIdentities`**

Inside the existing `for (Identity identity : identities)` loop, after the block that saves `roles` via `identityRoleRepo.saveAll(roles)` and before building the `IdentityEvent`, add:

```java
Long syncAccountId = identity.getAccountId();
if (syncAccountId != null) {
  List<Long> roleTypeIds = roles == null
      ? java.util.Collections.<Long>emptyList()
      : roles.stream().map(IdentityRole::getRoleTypeId).distinct().collect(Collectors.toList());
  templateLogic.syncUserPermissions(ctx, ctx.getCompanyId(), syncAccountId, roleTypeIds);
}
```

Watch variable naming — the existing loop may already declare a local `accountId` for something else; prefix with `sync` to avoid collision. Keep the enclosing `if (roles != null && !roles.isEmpty())` block intact for the save; the new sync block lives after it, outside that guard, because we still want sync to run (with an empty roleTypeIds list) for identities with no roles — that correctly deletes their orphaned role-sourced rows.

- [ ] **Step 4: Run — expect pass**

```
mvn -pl module/platform-federation test -Dtest=IdentityEventLogicSyncTest
```

Expected: 4/4 passed.

- [ ] **Step 5: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java \
        of1-core/module/platform-federation/src/test/java/datatp/platform/identity/queue/IdentityEventLogicSyncTest.java
git commit -m "feat(security): syncIdentities also materializes UserAppFeature rows"
```

---

## Task 7: BE-1 — SQL exposes `source_role_type_label`

**Files:**
- Modify: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/groovy/AppSql.groovy` (query `SearchUserAppPermissions`)

**Rationale:** Frontend depends on this field. Ship after all the backend logic so that the sync actually populates the data the SQL will expose.

- [ ] **Step 1: Read the current `SearchUserAppPermissions` query**

Open `AppSql.groovy` and locate the inner class. Verify it starts at around line 12 and the SELECT currently has these columns: `uaf.*, af.module AS module, af.name AS name, aa.login_id AS login_id, aa.full_name AS user_full_name`.

- [ ] **Step 2: Patch the SELECT and FROM clauses**

Apply this edit:
```groovy
String query = """
  SELECT
    uaf.*,
    af.module      AS module,
    af.name        AS name,
    aa.login_id    AS login_id,
    aa.full_name   AS user_full_name,
    srt.label      AS source_role_type_label
  FROM security_user_app_feature uaf
    INNER JOIN security_app_feature af  ON af.id = uaf.app_id
    INNER JOIN account_account      aa  ON aa.id = uaf.account_id
    LEFT  JOIN identity_role_type   srt ON srt.id = uaf.source_role_type_id
  WHERE
    ${FILTER_BY_STORAGE_STATE('uaf', sqlParams)}
    ${AND_FILTER_BY_PARAM('uaf.app_id', 'appId', sqlParams)}
    ${AND_FILTER_BY_PARAM('uaf.account_id', 'accountId', sqlParams)}
    ${AND_FILTER_BY_PARAM('uaf.access_type', 'accessType', sqlParams)}
    ${AND_FILTER_BY_PARAM('uaf.company_id', 'companyId', sqlParams)}
    ${AND_FILTER_BY_RANGE('uaf.created_time', 'createdTime', sqlParams)}
    ${AND_FILTER_BY_RANGE('uaf.modified_time', 'modifiedTime', sqlParams)}
    ${AND_FILTER_BY_OPTION('uaf.capability', "capability", sqlParams)}
    ${ORDER_BY(sqlParams)}
  ${MAX_RETURN(sqlParams)}
"""
```

Only change: add `srt.label AS source_role_type_label` to the SELECT list and add the `LEFT JOIN identity_role_type srt ON srt.id = uaf.source_role_type_id` line. Do not touch the WHERE filters.

- [ ] **Step 3: Build to verify Groovy compiles**

```
mvn -pl module/platform-federation compile -DskipTests -o
```

Expected: `BUILD SUCCESS`.

- [ ] **Step 4: Manual smoke test (optional, requires running instance)**

Start the backend locally, open the Identity detail screen on an identity that has both CUSTOM and synced permissions, and verify the response for `AppService.searchUserAppPermissions` contains `sourceRoleTypeId` and `sourceRoleTypeLabel` in each record. If running locally is not feasible, rely on the frontend task's QA checklist.

- [ ] **Step 5: Commit**

```bash
git add of1-core/module/platform-federation/src/main/java/datatp/platform/resource/groovy/AppSql.groovy
git commit -m "feat(security): expose source_role_type_label in SearchUserAppPermissions"
```

---

## Task 8: FE-1 + FE-2 — Frontend reads `sourceRoleTypeLabel` directly (atomic change)

**Files:**
- Modify: `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentityAppFeatureList.tsx`
- Modify: `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentity.tsx`

**Rationale:** These two edits must ship in the same commit — shipping FE-1 without FE-2 leaves a TypeScript compile error (call to deleted method).

- [ ] **Step 1: Open `UIIdentityAppFeatureList.tsx` and locate the sections to remove**

Identify and delete:
- The instance field `templateAppMap: Map<string, string[]> = new Map();`
- The entire `componentDidMount` override (including its `super.componentDidMount()` call).
- The entire `loadTemplates = () => { ... }` method.
- The `In Role Template` column's current `customRender` (replace below, don't leave stale code).

- [ ] **Step 2: Replace the column config**

Find the `roleTypeTemplate` column in the fields array and replace with:
```tsx
{
  name: 'sourceRoleTypeLabel', label: T('Source'), width: 200, filterable: true,
  customRender: (_ctx: grid.VGridContext, _field: grid.FieldConfig, dRec: grid.DisplayRecord) => {
    const record: any = dRec.record;
    const label = record.sourceRoleTypeLabel;

    if (!label) {
      return (
        <span className='badge bg-warning-soft text-warning border border-warning'
          style={{ fontSize: 11, fontWeight: 500 }}>
          {T('Custom')}
        </span>
      );
    }
    return (
      <span className='badge bg-success-soft text-success border border-success'
        style={{ fontSize: 11, fontWeight: 500 }}>
        {label}
      </span>
    );
  }
},
```

- [ ] **Step 3: Update `orderBy` to include the new field (FE-4)**

Locate the plugin's `orderBy` block:
```tsx
orderBy: {
  fields: ['module', 'name', 'capability', 'modifiedTime'],
  fieldLabels: ['App', 'Feature Screen', 'Capability', 'Modified Time'],
  selectFields: ['module', 'name'],
  sort: 'ASC'
},
```

Replace with:
```tsx
orderBy: {
  fields: ['module', 'name', 'sourceRoleTypeLabel', 'capability', 'modifiedTime'],
  fieldLabels: ['App', 'Feature Screen', 'Source', 'Capability', 'Modified Time'],
  selectFields: ['module', 'name'],
  sort: 'ASC'
},
```

- [ ] **Step 4: Open `UIIdentity.tsx` and remove the `loadTemplates()` call**

Find `onRolesChanged`:
```tsx
onRolesChanged = () => {
  this.listRef.current?.reloadData();
  this.featureListRef.current?.reloadData();
  this.featureListRef.current?.loadTemplates();
}
```

Delete the third line:
```tsx
onRolesChanged = () => {
  this.listRef.current?.reloadData();
  this.featureListRef.current?.reloadData();
}
```

- [ ] **Step 5: Type-check both files**

From `of1-platform/webui/platform`:
```
npx tsc --noEmit -p tsconfig.json 2>&1 | grep -E "UIIdentity|UIIdentityAppFeatureList"
```

Expected: no output (clean).

- [ ] **Step 6: Manual QA checklist (requires running UI against patched backend)**

- [ ] Identity detail opens; the `Source` column is visible.
- [ ] An identity that has never been synced → all rows show the yellow `Custom` badge.
- [ ] Click "Sync Permission" → list reloads; apps backed by a role template now show a green badge with the role type label.
- [ ] Add App Feature popup → newly added row renders the yellow `Custom` badge.
- [ ] Edit a row's capability or data-scope via the feature access editor → after save, the row flips to `Custom` (BE-5 path ii).
- [ ] Remove a role from the Role Type list + click Sync → apps only backed by that role disappear; CUSTOM rows remain.
- [ ] Sort by `Source` groups all CUSTOM rows together.

- [ ] **Step 7: Commit**

```bash
git add of1-platform/webui/platform/src/module/platform/security/identity/UIIdentityAppFeatureList.tsx \
        of1-platform/webui/platform/src/module/platform/security/identity/UIIdentity.tsx
git commit -m "feat(security): UIIdentityAppFeatureList reads sourceRoleTypeLabel directly

Drops the templateAppMap workaround and separate loadTemplates() fetch.
After BE-1, backend returns sourceRoleTypeLabel alongside the row, so the
Source column can render a yellow Custom badge or a green role-type badge
directly from the record. Sort options now include Source."
```

---

## Task 9: Full regression sweep

**Rationale:** Final sanity gate before the deploy checklist. All backend tests should pass; frontend TypeScript should be clean.

- [ ] **Step 1: Run the full backend test suite for the module**

```
mvn -pl module/platform-federation test
```

Expected: all tests pass, including the new `UserAppFeatureTemplateLogicTest` and `IdentityEventLogicSyncTest`.

- [ ] **Step 2: Run frontend type-check on the whole project**

```
cd of1-platform/webui/platform && npx tsc --noEmit -p tsconfig.json
```

Expected: zero errors.

- [ ] **Step 3: Review the full diff**

```
git log --oneline origin/develop..HEAD
git diff origin/develop...HEAD --stat
```

Expected: around 8 commits, covering BE-5 / BE-3 helpers / BE-3 sync / BE-4 stub / BE-2 / BE-2b / BE-1 / FE-1+FE-2.

- [ ] **Step 4: Dry-run the deploy order**

Confirm the backend commits are ordered before the frontend commits. Deploy order matters: backend must be live before frontend, so the FE reader has the `sourceRoleTypeLabel` field available.

- [ ] **Step 5: Post-deploy admin communication**

Draft a short message for the admin team:
> Sau upgrade, toàn bộ App Features trên màn hình Identity Detail sẽ hiển thị dưới dạng **Custom**. Hãy click **Sync Permission** trên từng identity để re-materialize từ role template hiện tại. Các CUSTOM row cấp tay trước đây vẫn được giữ nguyên, sync chỉ tạo thêm các row từ template.

Post this to the team channel right after deploy.

---

## Rollback Plan

If any backend issue is discovered post-deploy:
1. Revert all BE commits (`git revert <range>`) and redeploy backend.
2. Frontend continues to work because FE reads `record.sourceRoleTypeLabel`, which will simply be `undefined` → renders as `Custom`. No breakage.
3. If the frontend commit must also be rolled back, revert FE-1+FE-2 together — they are atomic.
