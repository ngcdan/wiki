# Audit Log for Identity & Permission — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add audit logging for all write operations on Identity, Role, and Permission entities in `platform-federation`, stored in a `platform_audit_log` DB table.

**Architecture:** New `AuditLog` entity (extends `CompanyEntity`) + `AuditLogWriter` helper component injected into `IdentityLogic` and `AppLogic`. Each write method calls `auditLogWriter.log(...)` within the same transaction. No AOP, no Kafka — explicit DB-only logging.

**Tech Stack:** Java 21, Spring Boot 3.2, JPA/Hibernate, JUnit 5

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260513-audit-log-identity-permission-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `module/platform-federation/src/main/java/datatp/platform/identity/audit/AuditAction.java` | Enum: all audit action types |
| Create | `module/platform-federation/src/main/java/datatp/platform/identity/audit/AuditLogWriter.java` | Stateless helper to insert audit records |
| Create | `module/platform-federation/src/main/java/datatp/platform/identity/entity/AuditLog.java` | JPA entity extending CompanyEntity |
| Create | `module/platform-federation/src/main/java/datatp/platform/identity/repository/AuditLogRepository.java` | Spring Data JPA repository |
| Modify | `module/platform-federation/src/main/java/datatp/platform/identity/IdentityLogic.java` | Add `@Autowired AuditLogWriter` + audit calls in 10 methods |
| Modify | `module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java` | Add `@Autowired AuditLogWriter` + audit calls in 9 methods |
| Create | `module/platform-federation/src/test/java/datatp/identity/AuditLogUnitTest.java` | Unit tests for audit logging |

---

## Task 1: Create AuditAction enum + AuditLog entity + AuditLogRepository

**Files:**
- Create: `module/platform-federation/src/main/java/datatp/platform/identity/audit/AuditAction.java`
- Create: `module/platform-federation/src/main/java/datatp/platform/identity/entity/AuditLog.java`
- Create: `module/platform-federation/src/main/java/datatp/platform/identity/repository/AuditLogRepository.java`

- [ ] **Step 1: Create `AuditAction.java`**

```java
package datatp.platform.identity.audit;

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

- [ ] **Step 2: Create `AuditLog.java`**

```java
package datatp.platform.identity.entity;

import java.io.Serial;
import java.util.Date;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonInclude;

import datatp.platform.identity.audit.AuditAction;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.CompanyEntity;
import net.datatp.util.text.DateUtil;

@Entity
@Table(
  name = "platform_audit_log",
  indexes = {
    @Index(name = "idx_audit_entity", columnList = "entity_type, entity_id"),
    @Index(name = "idx_audit_performer", columnList = "performer_account_id"),
    @Index(name = "idx_audit_action_date", columnList = "action_date"),
    @Index(name = "idx_audit_company_date", columnList = "company_id, action_date")
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter @Setter
public class AuditLog extends CompanyEntity {

  @Serial
  private static final long serialVersionUID = 1L;

  @Enumerated(EnumType.STRING)
  @Column(name = "action", length = 50)
  private AuditAction action;

  @Column(name = "entity_type", length = 50)
  private String entityType;

  @Column(name = "entity_id")
  private Long entityId;

  @Column(name = "entity_label", length = 255)
  private String entityLabel;

  @Column(name = "performer_account_id")
  private long performerAccountId;

  @Column(name = "performer_full_name", length = 255)
  private String performerFullName;

  @JsonFormat(pattern = DateUtil.COMPACT_DATETIME_FORMAT)
  @Column(name = "action_date")
  private Date actionDate;

  @Column(name = "description", columnDefinition = "TEXT")
  private String description;
}
```

- [ ] **Step 3: Create `AuditLogRepository.java`**

```java
package datatp.platform.identity.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import datatp.platform.identity.entity.AuditLog;

public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
}
```

- [ ] **Step 4: Verify compilation**

Run: `gradle :datatp-core-module-platform-federation:compileJava`
Expected: BUILD SUCCESSFUL

---

## Task 2: Create AuditLogWriter helper

**Files:**
- Create: `module/platform-federation/src/main/java/datatp/platform/identity/audit/AuditLogWriter.java`

- [ ] **Step 1: Create `AuditLogWriter.java`**

```java
package datatp.platform.identity.audit;

import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import datatp.platform.identity.entity.AuditLog;
import datatp.platform.identity.repository.AuditLogRepository;
import net.datatp.security.client.ClientContext;

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

- [ ] **Step 2: Verify compilation**

Run: `gradle :datatp-core-module-platform-federation:compileJava`
Expected: BUILD SUCCESSFUL

---

## Task 3: Write unit test for AuditLogWriter

**Files:**
- Create: `module/platform-federation/src/test/java/datatp/identity/AuditLogUnitTest.java`

- [ ] **Step 1: Write test**

```java
package datatp.identity;

import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.annotation.DirtiesContext.ClassMode;

import datatp.platform.identity.IdentityConfig;
import datatp.platform.identity.IdentityService;
import datatp.platform.identity.audit.AuditAction;
import datatp.platform.identity.entity.AuditLog;
import datatp.platform.identity.entity.Identity;
import datatp.platform.identity.entity.IdentityRole;
import datatp.platform.identity.entity.IdentityRoleType;
import datatp.platform.identity.repository.AuditLogRepository;
import datatp.platform.resource.AppResourceConfig;
import datatp.platform.resource.entity.AppFeature;
import datatp.platform.resource.entity.UserAppFeature;
import datatp.platform.resource.logic.AppLogic;
import net.datatp.module.data.db.PlatformJpaConfiguration;
import net.datatp.security.client.ClientContext;

@SpringBootTest(
  webEnvironment = WebEnvironment.NONE,
  classes = {PlatformJpaConfiguration.class, IdentityConfig.class, AppResourceConfig.class},
  properties = {
    "spring.config.location=classpath:application-test.yaml",
    "spring.datasource.hibernate.show_sql=false",
    "logging.level.org.springframework=INFO",
    "spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration"
  })
@DirtiesContext(classMode = ClassMode.AFTER_EACH_TEST_METHOD)
class AuditLogUnitTest {

  @Autowired IdentityService identityService;
  @Autowired AuditLogRepository auditLogRepo;
  @Autowired AppLogic appLogic;

  static final ClientContext ctx;
  static {
    ctx = new ClientContext("default", "testuser", "localhost");
    ctx.setCompanyId(1L);
    ctx.setFullName("Test User");
  }

  @Test
  @Tag("unit")
  void testCreateIdentityGeneratesAuditLog() {
    Identity identity = new Identity();
    identity.setLoginId("audit-test-user");
    identity.setEmail("audit@test.com");
    identity.setMobile("0999888777");
    identity.setFullName("Audit Test");
    identity.setIdentityType("USER");

    Identity saved = identityService.saveIdentity(ctx, identity);

    List<AuditLog> logs = auditLogRepo.findAll();
    assertTrue(logs.size() >= 1, "Should have at least 1 audit log");

    AuditLog log = logs.stream()
        .filter(l -> l.getAction() == AuditAction.CREATE_IDENTITY)
        .findFirst().orElse(null);
    assertNotNull(log, "Should have CREATE_IDENTITY audit log");
    assertEquals("IDENTITY", log.getEntityType());
    assertEquals(saved.getId(), log.getEntityId());
    assertEquals("audit-test-user", log.getEntityLabel());
    assertNotNull(log.getActionDate());
  }

  @Test
  @Tag("unit")
  void testUpdateIdentityGeneratesAuditLog() {
    Identity identity = new Identity();
    identity.setLoginId("update-audit-user");
    identity.setEmail("update-audit@test.com");
    identity.setMobile("0999111222");
    identity.setFullName("Update Audit");
    identity.setIdentityType("USER");
    Identity saved = identityService.saveIdentity(ctx, identity);

    saved.setFullName("Updated Name");
    identityService.saveIdentity(ctx, saved);

    List<AuditLog> logs = auditLogRepo.findAll();
    long updateCount = logs.stream()
        .filter(l -> l.getAction() == AuditAction.UPDATE_IDENTITY)
        .count();
    assertTrue(updateCount >= 1, "Should have UPDATE_IDENTITY audit log");
  }

  @Test
  @Tag("unit")
  void testRoleAssignGeneratesAuditLog() {
    Identity identity = new Identity();
    identity.setLoginId("role-audit-user");
    identity.setEmail("role-audit@test.com");
    identity.setMobile("0999333444");
    identity.setFullName("Role Audit");
    identity.setIdentityType("USER");
    Identity saved = identityService.saveIdentity(ctx, identity);

    IdentityRoleType roleType = new IdentityRoleType();
    roleType.setRole("AUDIT_ROLE");
    roleType.setLabel("Audit Role");
    roleType = identityService.saveRoleType(ctx, roleType);

    IdentityRole role = new IdentityRole();
    role.setIdentityId(saved.getId());
    role.setRoleTypeId(roleType.getId());
    identityService.saveRole(ctx, role);

    List<AuditLog> logs = auditLogRepo.findAll();
    boolean hasRoleAssign = logs.stream()
        .anyMatch(l -> l.getAction() == AuditAction.ROLE_ASSIGN);
    assertTrue(hasRoleAssign, "Should have ROLE_ASSIGN audit log");
  }

  @Test
  @Tag("unit")
  void testRoleRemoveGeneratesAuditLog() {
    Identity identity = new Identity();
    identity.setLoginId("role-remove-user");
    identity.setEmail("role-remove@test.com");
    identity.setMobile("0999555666");
    identity.setFullName("Role Remove");
    identity.setIdentityType("USER");
    Identity saved = identityService.saveIdentity(ctx, identity);

    IdentityRoleType roleType = new IdentityRoleType();
    roleType.setRole("REMOVE_ROLE");
    roleType.setLabel("Remove Role");
    roleType = identityService.saveRoleType(ctx, roleType);

    IdentityRole role = new IdentityRole();
    role.setIdentityId(saved.getId());
    role.setRoleTypeId(roleType.getId());
    IdentityRole savedRole = identityService.saveRole(ctx, role);

    auditLogRepo.deleteAll(); // clear previous logs

    identityService.deleteRoles(ctx, null, List.of(savedRole.getId()));

    List<AuditLog> logs = auditLogRepo.findAll();
    boolean hasRoleRemove = logs.stream()
        .anyMatch(l -> l.getAction() == AuditAction.ROLE_REMOVE);
    assertTrue(hasRoleRemove, "Should have ROLE_REMOVE audit log");
  }

  @Test
  @Tag("unit")
  void testRoleTypeDeleteGeneratesAuditLog() {
    IdentityRoleType roleType = new IdentityRoleType();
    roleType.setRole("DELETE_RT");
    roleType.setLabel("Delete RT");
    roleType = identityService.saveRoleType(ctx, roleType);

    auditLogRepo.deleteAll();

    identityService.deleteRoleTypes(ctx, List.of(roleType.getId()));

    List<AuditLog> logs = auditLogRepo.findAll();
    boolean hasRoleTypeDelete = logs.stream()
        .anyMatch(l -> l.getAction() == AuditAction.ROLE_TYPE_DELETE);
    assertTrue(hasRoleTypeDelete, "Should have ROLE_TYPE_DELETE audit log");
  }

  @Test
  @Tag("unit")
  void testAppPermissionSaveGeneratesAuditLog() {
    AppFeature app = new AppFeature();
    app.setModule("test");
    app.setName("audit-app");
    app.setLabel("Audit App");
    app = appLogic.saveApp(ctx, app);

    auditLogRepo.deleteAll();

    UserAppFeature perm = new UserAppFeature();
    perm.setAppId(app.getId());
    perm.setAccountId(99L);
    perm.setCompanyId(ctx.getCompanyId());
    appLogic.saveAppPermission(ctx, perm);

    List<AuditLog> logs = auditLogRepo.findAll();
    boolean hasPermSave = logs.stream()
        .anyMatch(l -> l.getAction() == AuditAction.PERMISSION_SAVE);
    assertTrue(hasPermSave, "Should have PERMISSION_SAVE audit log");
  }
}
```

- [ ] **Step 2: Run test — should FAIL** (AuditLogWriter not wired into Logic classes yet)

Run: `gradle :datatp-core-module-platform-federation:test --tests "datatp.identity.AuditLogUnitTest"`
Expected: Tests FAIL because `IdentityLogic` and `AppLogic` don't call `auditLogWriter.log()` yet.

---

## Task 4: Wire audit into IdentityLogic

**Files:**
- Modify: `module/platform-federation/src/main/java/datatp/platform/identity/IdentityLogic.java`

- [ ] **Step 1: Add AuditLogWriter field**

Add after the existing `@Autowired` fields (around line 115):

```java
@Autowired
private AuditLogWriter auditLogWriter;
```

Add import:
```java
import datatp.platform.identity.audit.AuditAction;
import datatp.platform.identity.audit.AuditLogWriter;
```

- [ ] **Step 2: Add audit to `saveIdentity()` (line ~151)**

After `return identityRepo.save(identity);` (line 167), change to:

```java
Identity saved = identityRepo.save(identity);

AuditAction auditAction = isNew ? AuditAction.CREATE_IDENTITY : AuditAction.UPDATE_IDENTITY;
String desc = isNew ? "Created identity: " + saved.getLoginId() : "Updated identity: " + saved.getLoginId();
auditLogWriter.log(ctx, auditAction, "IDENTITY", saved.getId(), saved.getLoginId(), desc);

return saved;
```

Note: `isNew` is already computed at line 158.

- [ ] **Step 3: Add audit to `disabledIdentities()` (line ~537)**

Inside the for-loop, after the `internalClient.internalCall(...)` and `disabledList.add(identity)` (around line 556), add:

```java
AuditAction auditAction = isDisabled ? AuditAction.DISABLE_IDENTITY : AuditAction.ENABLE_IDENTITY;
String desc = (isDisabled ? "Disabled" : "Enabled") + " identity: " + identity.getLoginId();
auditLogWriter.log(client, auditAction, "IDENTITY", identity.getId(), identity.getLoginId(), desc);
```

- [ ] **Step 4: Add audit to `resetAccountPassword()` (line ~436)**

After the successful Keycloak password change (after `log.info("Successfully reset password...")`  around line 462), add:

```java
auditLogWriter.log(client, AuditAction.PASSWORD_RESET, "IDENTITY",
    identity.getId(), normalizedUsername,
    "Password reset for user: " + normalizedUsername);
```

- [ ] **Step 5: Add audit to `removeRequiredActions()` (line ~483)**

After `log.info("Successfully removed required actions...")` (around line 492), add:

```java
auditLogWriter.log(client, AuditAction.REMOVE_REQUIRED_ACTIONS, "IDENTITY",
    null, username,
    "Removed required actions for user: " + username);
```

- [ ] **Step 6: Add audit to `saveRole()` (line ~281)**

After `IdentityRole savedRole = identityRoleRepo.save(identityRole);` (line 297), add:

```java
String roleLabel = identity != null ? identity.getLoginId() : "identityId=" + savedRole.getIdentityId();
if (isNew) {
  auditLogWriter.log(ctx, AuditAction.ROLE_ASSIGN, "IDENTITY_ROLE",
      savedRole.getId(), roleLabel,
      "Assigned role (roleTypeId=" + savedRole.getRoleTypeId() + ") to " + roleLabel);
}
```

Note: `identity` is fetched later for event publishing — move the identity fetch before the audit call, or use `savedRole.getIdentityId()` for the label when identity is null.

Revised approach — add audit after the existing identity fetch block (around line 305):

```java
if (isNew) {
  String roleLabel = identity != null ? identity.getLoginId() : "identityId=" + savedRole.getIdentityId();
  auditLogWriter.log(ctx, AuditAction.ROLE_ASSIGN, "IDENTITY_ROLE",
      savedRole.getId(), roleLabel,
      "Assigned role (roleTypeId=" + savedRole.getRoleTypeId() + ") to " + roleLabel);
}
```

- [ ] **Step 7: Add audit to `saveRoles()` (line ~314)**

Inside the for-loop, after `if (isNew) newRoles.add(saved);` (line 336), add:

```java
if (isNew) {
  auditLogWriter.log(ctx, AuditAction.ROLE_ASSIGN, "IDENTITY_ROLE",
      saved.getId(), "identityId=" + saved.getIdentityId(),
      "Assigned role (roleTypeId=" + saved.getRoleTypeId() + ") to identityId=" + saved.getIdentityId());
}
```

- [ ] **Step 8: Add audit to `deleteIdentityRoles()` (line ~359)**

Inside the event publishing block, after building `affectedIdentities` map and before `identityRoleRepo.deleteByIds(ids)` (line 372), add per-role audit:

```java
for (IdentityRole role : roles) {
  Identity identity = affectedIdentities.get(role.getIdentityId());
  String label = identity != null ? identity.getLoginId() : "identityId=" + role.getIdentityId();
  auditLogWriter.log(ctx, AuditAction.ROLE_REMOVE, "IDENTITY_ROLE",
      role.getId(), label,
      "Removed role (roleTypeId=" + role.getRoleTypeId() + ") from " + label);
}
```

- [ ] **Step 9: Add audit to `saveRoleType()` (line ~400)**

Change the method body:

```java
public IdentityRoleType saveRoleType(ClientContext ctx, IdentityRoleType identityRoleType) {
  boolean isNew = identityRoleType.isNew();
  IdentityRoleType saved = identityRoleTypeRepo.save(identityRoleType);
  if (isNew) {
    auditLogWriter.log(ctx, AuditAction.ROLE_TYPE_CREATE, "IDENTITY_ROLE_TYPE",
        saved.getId(), saved.getRole(),
        "Created role type: " + saved.getRole());
  }
  return saved;
}
```

- [ ] **Step 10: Add audit to `deleteRoleTypes()` (line ~404)**

Inside the for-loop, after `deletedRoleTypeList.add(roleType)` (around line 414), add:

```java
if (roleType != null) {
  auditLogWriter.log(ctx, AuditAction.ROLE_TYPE_DELETE, "IDENTITY_ROLE_TYPE",
      roleType.getId(), roleType.getRole(),
      "Deleted role type: " + roleType.getRole());
}
```

- [ ] **Step 11: Verify compilation**

Run: `gradle :datatp-core-module-platform-federation:compileJava`
Expected: BUILD SUCCESSFUL

---

## Task 5: Wire audit into AppLogic

**Files:**
- Modify: `module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java`

- [ ] **Step 1: Add AuditLogWriter field**

Add after the existing `@Autowired` fields (around line 16):

```java
@Autowired
private AuditLogWriter auditLogWriter;
```

Add imports:
```java
import datatp.platform.identity.audit.AuditAction;
import datatp.platform.identity.audit.AuditLogWriter;
```

- [ ] **Step 2: Add audit to `saveApp()` (line ~53)**

Change:
```java
public AppFeature saveApp(ClientContext client, AppFeature app) {
  app.set(client);
  AppFeature saved = appRepo.save(app);
  auditLogWriter.log(client, AuditAction.APP_SAVE, "APP_FEATURE",
      saved.getId(), saved.getModule() + ":" + saved.getName(),
      "Saved app: " + saved.getModule() + ":" + saved.getName());
  return saved;
}
```

- [ ] **Step 3: Add audit to `deleteAppByIds()` (line ~70)**

Before `appRepo.deleteAppByIds(ids)`, add audit per app:

```java
public void deleteAppByIds(ClientContext client, List<Long> ids) {
  List<UserAppFeature> appPermissions = getAppPermissionsByAppIds(client, ids);
  deletePermissions(client, appPermissions);
  for (Long id : ids) {
    auditLogWriter.log(client, AuditAction.APP_DELETE, "APP_FEATURE",
        id, "appId=" + id,
        "Deleted app id=" + id);
  }
  appRepo.deleteAppByIds(ids);
}
```

- [ ] **Step 4: Add audit to `saveAppPermission()` (line ~92)**

Change:
```java
public UserAppFeature saveAppPermission(ClientContext client, UserAppFeature permission) {
  permission.setSourceRoleTypeId(null);
  permission.set(client);
  UserAppFeature saved = permissionRepo.save(permission);
  auditLogWriter.log(client, AuditAction.PERMISSION_SAVE, "USER_APP_FEATURE",
      saved.getId(), "appId=" + saved.getAppId() + ",accountId=" + saved.getAccountId(),
      "Saved permission for appId=" + saved.getAppId() + " accountId=" + saved.getAccountId());
  return saved;
}
```

Note: `saveAppPermissions()` calls `saveAppPermission()` internally — audit is logged by `saveAppPermission()`, no separate audit needed in `saveAppPermissions()`.

- [ ] **Step 5: Add audit to `deletePermissions()` (line ~138)**

Change:
```java
public boolean deletePermissions(ClientContext client, List<UserAppFeature> permissions) {
  for (UserAppFeature sel : permissions) {
    auditLogWriter.log(client, AuditAction.PERMISSION_DELETE, "USER_APP_FEATURE",
        sel.getId(), "appId=" + sel.getAppId() + ",accountId=" + sel.getAccountId(),
        "Deleted permission id=" + sel.getId());
    permissionRepo.delete(sel);
  }
  return true;
}
```

- [ ] **Step 6: Add audit to `deletePermissionsByIds()` (line ~145)**

Change:
```java
public boolean deletePermissionsByIds(ClientContext client, List<Long> ids) {
  for (Long id : ids) {
    UserAppFeature appPermission = permissionRepo.findById(id).get();
    auditLogWriter.log(client, AuditAction.PERMISSION_DELETE, "USER_APP_FEATURE",
        id, "appId=" + appPermission.getAppId() + ",accountId=" + appPermission.getAccountId(),
        "Deleted permission id=" + id);
    permissionRepo.delete(appPermission);
  }
  return true;
}
```

- [ ] **Step 7: Add audit to `updateAppPermissionCapabilities()` (line ~111)**

Inside the for-loop, after `target = saveAppPermission(client, target)`, note that `saveAppPermission()` already logs `PERMISSION_SAVE`. To log the specific capability update action instead, add audit before calling `saveAppPermission()`:

Actually, since `saveAppPermission()` already logs `PERMISSION_SAVE`, and `updateAppPermissionCapabilities()` is a more specific action, we should log `PERMISSION_UPDATE_CAPABILITY` here and skip the generic save log. But `saveAppPermission()` is shared — simplest approach: let `saveAppPermission()` log `PERMISSION_SAVE` as usual. The update-specific methods add additional context.

Revised: keep `saveAppPermission()` audit as-is. Add a separate audit in update methods:

```java
public List<UserAppFeature> updateAppPermissionCapabilities(ClientContext client, Capability capability, List<Long> targetIds) {
  List<UserAppFeature> holder = new ArrayList<>();
  for (Long targetId : targetIds) {
    UserAppFeature target = getAppPermission(client, targetId);
    target.setCapability(capability);
    target = saveAppPermission(client, target);
    holder.add(target);
  }
  return holder;
}
```

Since `saveAppPermission()` already logs audit — no extra audit needed here. Same for `updateAppPermissionDataScopes()`.

- [ ] **Step 8: Add audit to `updateAppPermissionStorageStates()` (line ~133)**

This method uses bulk SQL (`permissionRepo.updateStorageState()`) — `saveAppPermission()` is NOT called, so we need explicit audit:

```java
public int updateAppPermissionStorageStates(ClientContext client, StorageState storageState, List<Long> targetIds) {
  if (targetIds == null || targetIds.isEmpty()) return 0;
  int count = permissionRepo.updateStorageState(storageState, targetIds);
  if (count > 0) {
    String idsStr = targetIds.size() <= 10 ? targetIds.toString() : targetIds.size() + " permissions";
    auditLogWriter.log(client, AuditAction.PERMISSION_UPDATE_STATE, "USER_APP_FEATURE",
        null, idsStr,
        "Updated storage state to " + storageState + " for " + idsStr);
  }
  return count;
}
```

- [ ] **Step 9: Verify compilation**

Run: `gradle :datatp-core-module-platform-federation:compileJava`
Expected: BUILD SUCCESSFUL

---

## Task 6: Run tests and verify

- [ ] **Step 1: Run audit log tests**

Run: `gradle :datatp-core-module-platform-federation:test --tests "datatp.identity.AuditLogUnitTest"`
Expected: ALL PASS

- [ ] **Step 2: Run existing identity tests to check no regressions**

Run: `gradle :datatp-core-module-platform-federation:test --tests "datatp.identity.IdentityLogicUnitTest"`
Expected: ALL PASS

- [ ] **Step 3: Run full module tests**

Run: `gradle :datatp-core-module-platform-federation:test`
Expected: ALL PASS

- [ ] **Step 4: Full build**

Run: `gradle build publishToMavenLocal -x test`
Expected: BUILD SUCCESSFUL

---

## Task 7: Commit

- [ ] **Step 1: Review changes**

Run: `git diff --stat`

Expected files:
- 4 new files (AuditAction, AuditLog, AuditLogRepository, AuditLogWriter)
- 1 new test file (AuditLogUnitTest)
- 2 modified files (IdentityLogic, AppLogic)

- [ ] **Step 2: Commit**

```bash
git add module/platform-federation/src/main/java/datatp/platform/identity/audit/
git add module/platform-federation/src/main/java/datatp/platform/identity/entity/AuditLog.java
git add module/platform-federation/src/main/java/datatp/platform/identity/repository/AuditLogRepository.java
git add module/platform-federation/src/main/java/datatp/platform/identity/IdentityLogic.java
git add module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java
git add module/platform-federation/src/test/java/datatp/identity/AuditLogUnitTest.java
git commit -m "$(cat <<'EOF'
feat: add audit log for identity, role, and permission write operations

New platform_audit_log table tracks who performed what action on which
entity. AuditLogWriter helper is called explicitly from IdentityLogic
and AppLogic within the same transaction boundary.

Covers: identity CRUD, enable/disable, password reset, role assign/remove,
role type create/delete, app save/delete, permission CRUD.

Refs #666
EOF
)"
```
