# Function Permission System — Phase 2-3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seed FunctionDefinition master data and migrate all callers from UserAccessProfileLogic to UserFunctionPermissionLogic.

**Architecture:** Seed FunctionDefinition rows mapping old ResourceType + TaskVisibility to function codes. Update each caller to use UserFunctionPermissionLogic instead of UserAccessProfileLogic. Keep old entities intact until Phase 5.

**Tech Stack:** Java 21, Spring Boot, JPA/Hibernate, Lombok, PostgreSQL

**Spec:** `.claude/specs/260512-function-permission-design.md`
**Phase 1 commit:** `f86cfb731` (entities, repos, logic created)

---

## Caller Migration Map

| File | Old Usage | New Usage |
|------|-----------|-----------|
| `CRMIdentityEventConsumer` | `new UserAccessProfile()` + `initAllSelfOnlyPermissions()` | `permissionLogic.grantAllFunctions(NONE, false...)` |
| `CRMPartnerLogic.getPartnerIfAuthorized` | `permission.getAgentViewScope()` | `permissionLogic.hasPermission(PARTNER_AGENT, READ)` |
| `CRMPartnerLogic.searchCRMPartners` | `permission.getAgentViewScope().toString()` | `permissionLogic.getDataScope(PARTNER_AGENT)` |
| `CRMPartnerLogic.getPartnerRequestApprover` | `findUsersWithAgentApproveScope()` | `permissionLogic` query by approve + function |
| `CustomerLeadsLogic.getLeadIfAuthorized` | `permission.getAgentPotentialViewScope()` | `permissionLogic.hasPermission(PARTNER_AGENTS_APPROACHED, READ)` |
| `CustomerLeadsLogic.searchCustomerLeads` | `permission.getAgentPotentialViewScope()` | `permissionLogic.getDataScope(PARTNER_AGENTS_APPROACHED)` |
| `PartnerReportLogic.searchIntegratedPartners` | `permission.getTaskVisibilityScope()` | `permissionLogic.getDataScope(REPORT_PARTNER)` |
| `PartnerReportLogic.reportAgentTransactions` | `canEditResource(AGENT, GROUP_ALL)` | `permissionLogic.hasPermission(PARTNER_AGENT, WRITE)` + scope check |
| `PartnerRequestLogic.searchPartnerRequests` | `accessProfileLogic.getByAccountId()` | `permissionLogic.findByAccountId()` |
| `TaskCalendarLogic.searchTasksCalendar` | `computeTaskPermissionReport()` | `permissionLogic.computePermissionReport(TASK_CALENDAR)` |
| `InquiryRequestLogic` (6 methods) | `computeTaskPermissionReport()` | `permissionLogic.computePermissionReport(INQUIRY_REQUEST)` |
| `BusinessReportLogic` (4 methods) | `computeTaskPermissionReport()` | `permissionLogic.computePermissionReport(REPORT_QUOTATION)` |
| `PerformanceReportLogic` (2+ methods) | `permission.getTaskVisibilityScope()` | `permissionLogic.getDataScope(REPORT_PERFORMANCE)` |

---

## FunctionDefinition Master Data

| code | group_name | function_name | type |
|------|-----------|---------------|------|
| PARTNER_AGENT | Partner Management | Agent | SCREEN |
| PARTNER_COLOADER | Partner Management | Coloader | SCREEN |
| PARTNER_CUSTOMER | Partner Management | Customer | SCREEN |
| PARTNER_CUSTOMER_LEAD | Partner Management | Customer Lead | SCREEN |
| PARTNER_AGENTS_APPROACHED | Partner Management | Agents Approached | SCREEN |
| PARTNER_REQUEST | Partner Management | Partner Request | FUNCTION |
| TASK_CALENDAR | Sales | Task Calendar | SCREEN |
| INQUIRY_REQUEST | Price | Inquiry Request | SCREEN |
| REPORT_QUOTATION | Reports | Quotation Report | SCREEN |
| REPORT_PARTNER | Reports | Partner Report | SCREEN |
| REPORT_PERFORMANCE | Reports | Performance Report | SCREEN |

---

## Task 1: Add seed data method to UserFunctionPermissionLogic

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/UserFunctionPermissionLogic.java`

- [ ] **Step 1: Add seedFunctionDefinitions method**

Add method to `UserFunctionPermissionLogic.java` that creates all FunctionDefinition rows if they don't exist:

```java
public void seedFunctionDefinitions(ClientContext client) {
  seedFunction(client, "Partner Management", "Agent", "PARTNER_AGENT", FunctionType.SCREEN);
  seedFunction(client, "Partner Management", "Coloader", "PARTNER_COLOADER", FunctionType.SCREEN);
  seedFunction(client, "Partner Management", "Customer", "PARTNER_CUSTOMER", FunctionType.SCREEN);
  seedFunction(client, "Partner Management", "Customer Lead", "PARTNER_CUSTOMER_LEAD", FunctionType.SCREEN);
  seedFunction(client, "Partner Management", "Agents Approached", "PARTNER_AGENTS_APPROACHED", FunctionType.SCREEN);
  seedFunction(client, "Partner Management", "Partner Request", "PARTNER_REQUEST", FunctionType.FUNCTION);
  seedFunction(client, "Sales", "Task Calendar", "TASK_CALENDAR", FunctionType.SCREEN);
  seedFunction(client, "Price", "Inquiry Request", "INQUIRY_REQUEST", FunctionType.SCREEN);
  seedFunction(client, "Reports", "Quotation Report", "REPORT_QUOTATION", FunctionType.SCREEN);
  seedFunction(client, "Reports", "Partner Report", "REPORT_PARTNER", FunctionType.SCREEN);
  seedFunction(client, "Reports", "Performance Report", "REPORT_PERFORMANCE", FunctionType.SCREEN);
}

private void seedFunction(ClientContext client, String groupName, String functionName, String code, FunctionType type) {
  FunctionDefinition existing = functionRepo.getByCode(code);
  if (existing != null) return;
  FunctionDefinition funcDef = new FunctionDefinition();
  funcDef.setGroupName(groupName);
  funcDef.setFunctionName(functionName);
  funcDef.setCode(code);
  funcDef.setType(type);
  createFunction(client, funcDef);
  log.info("Seeded FunctionDefinition: {}", code);
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-core:compileJava`

---

## Task 2: Add migration method to UserFunctionPermissionLogic

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/UserFunctionPermissionLogic.java`

- [ ] **Step 1: Add migrateFromUserAccessProfile method**

This method reads existing `UserAccessProfile` data and creates corresponding `UserFunctionPermission` rows.

```java
@Autowired
private UserAccessProfileLogic accessProfileLogic;

public int migrateFromUserAccessProfile(ClientContext client) {
  seedFunctionDefinitions(client);
  List<UserAccessProfile> allProfiles = accessProfileLogic.findAll(client);
  int count = 0;
  for (UserAccessProfile profile : allProfiles) {
    Long accountId = profile.getAccountId();
    List<UserFunctionPermission> existing = permissionRepo.findByAccountId(accountId);
    if (!existing.isEmpty()) continue;
    try {
      migrateProfile(client, profile);
      count++;
      log.info("Migrated permissions for account: {}", accountId);
    } catch (Exception e) {
      log.error("Error migrating permissions for account: {}", accountId, e);
    }
  }
  return count;
}

private void migrateProfile(ClientContext client, UserAccessProfile profile) {
  Long accountId = profile.getAccountId();
  Set<Long> companyBranchIds = new LinkedHashSet<>(profile.getAccessibleCompanyBranchIds());
  Set<Long> accessibleAccountIds = new LinkedHashSet<>(profile.getAccessibleAccountIds());

  migrateResourcePermission(client, accountId, "PARTNER_AGENT",
    profile.getAgentViewScope(), profile.getAgentEditScope(), profile.getAgentApproveScope(),
    companyBranchIds, accessibleAccountIds);
  migrateResourcePermission(client, accountId, "PARTNER_COLOADER",
    profile.getColoaderViewScope(), profile.getColoaderEditScope(), profile.getColoaderApproveScope(),
    companyBranchIds, accessibleAccountIds);
  migrateResourcePermission(client, accountId, "PARTNER_CUSTOMER",
    profile.getCustomerViewScope(), profile.getCustomerEditScope(), profile.getCustomerApproveScope(),
    companyBranchIds, accessibleAccountIds);
  migrateResourcePermission(client, accountId, "PARTNER_CUSTOMER_LEAD",
    profile.getCustomerLeadViewScope(), profile.getCustomerLeadEditScope(), profile.getCustomerLeadApproveScope(),
    companyBranchIds, accessibleAccountIds);
  migrateResourcePermission(client, accountId, "PARTNER_AGENTS_APPROACHED",
    profile.getAgentPotentialViewScope(), profile.getAgentPotentialEditScope(), profile.getAgentPotentialApproveScope(),
    companyBranchIds, accessibleAccountIds);

  PermissionScope taskScope = profile.getTaskVisibilityScope();
  migrateTaskPermission(client, accountId, "PARTNER_REQUEST", taskScope, companyBranchIds, accessibleAccountIds);
  migrateTaskPermission(client, accountId, "TASK_CALENDAR", taskScope, companyBranchIds, accessibleAccountIds);
  migrateTaskPermission(client, accountId, "INQUIRY_REQUEST", taskScope, companyBranchIds, accessibleAccountIds);
  migrateTaskPermission(client, accountId, "REPORT_QUOTATION", taskScope, companyBranchIds, accessibleAccountIds);
  migrateTaskPermission(client, accountId, "REPORT_PARTNER", taskScope, companyBranchIds, accessibleAccountIds);
  migrateTaskPermission(client, accountId, "REPORT_PERFORMANCE", taskScope, companyBranchIds, accessibleAccountIds);
}

private void migrateResourcePermission(ClientContext client, Long accountId, String functionCode,
  PermissionScope viewScope, PermissionScope editScope, PermissionScope approveScope,
  Set<Long> companyBranchIds, Set<Long> accessibleAccountIds) {
  boolean canRead = viewScope != PermissionScope.NONE;
  boolean canWrite = editScope != PermissionScope.NONE;
  boolean canApprove = approveScope != PermissionScope.NONE;
  PermissionScope widestScope = widest(viewScope, editScope, approveScope);

  UserFunctionPermission perm = grantPermissions(client, accountId, functionCode,
    widestScope, canRead, canWrite, false, canApprove, false, false);

  if (widestScope == PermissionScope.CUSTOM || widestScope == PermissionScope.COMPANY_ONLY) {
    if (!companyBranchIds.isEmpty()) perm.setAccessibleCompanyBranchIds(companyBranchIds);
    if (!accessibleAccountIds.isEmpty()) perm.setAccessibleAccountIds(accessibleAccountIds);
    save(client, perm);
  }
}

private void migrateTaskPermission(ClientContext client, Long accountId, String functionCode,
  PermissionScope taskScope, Set<Long> companyBranchIds, Set<Long> accessibleAccountIds) {
  boolean canRead = taskScope != PermissionScope.NONE;

  UserFunctionPermission perm = grantPermissions(client, accountId, functionCode,
    taskScope, canRead, false, false, false, false, false);

  if (taskScope == PermissionScope.CUSTOM || taskScope == PermissionScope.COMPANY_ONLY) {
    if (!companyBranchIds.isEmpty()) perm.setAccessibleCompanyBranchIds(companyBranchIds);
    if (!accessibleAccountIds.isEmpty()) perm.setAccessibleAccountIds(accessibleAccountIds);
    save(client, perm);
  }
}

private PermissionScope widest(PermissionScope... scopes) {
  PermissionScope widest = PermissionScope.NONE;
  for (PermissionScope s : scopes) {
    if (s.ordinal() > widest.ordinal()) widest = s;
  }
  return widest;
}
```

- [ ] **Step 2: Add required import**

Add `import java.util.LinkedHashSet;` and `import cloud.datatp.core.template.entity.UserAccessProfile;` to imports.

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-core:compileJava`

---

## Task 3: Add query methods to UserFunctionPermissionRepository

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/repository/UserFunctionPermissionRepository.java`

- [ ] **Step 1: Add finder methods for approval discovery**

These methods replace `findUsersWithAgentApproveScope()` etc. from `UserAccessProfileRepository`.

```java
@Query("SELECT p FROM UserFunctionPermission p JOIN p.functionDefinition fd WHERE fd.code = :functionCode AND p.canApprove = true AND p.dataScope = :scope")
List<UserFunctionPermission> findByFunctionCodeAndCanApproveAndDataScope(
  @Param("functionCode") String functionCode, @Param("scope") PermissionScope scope);

@Query("SELECT p FROM UserFunctionPermission p JOIN p.functionDefinition fd WHERE fd.code = :functionCode AND p.canRead = true AND p.dataScope = :scope")
List<UserFunctionPermission> findByFunctionCodeAndCanReadAndDataScope(
  @Param("functionCode") String functionCode, @Param("scope") PermissionScope scope);
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-core:compileJava`

---

## Task 4: Add approval discovery methods to UserFunctionPermissionLogic

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/UserFunctionPermissionLogic.java`

- [ ] **Step 1: Add findUsersWithApprovePermission method**

Replace `findUsersWithAgentApproveScope`, `findUsersWithCustomerApproveScope`, `findUsersWithColoaderApproveScope` with generic method:

```java
public List<UserFunctionPermission> findUsersWithApprovePermission(ClientContext client, String functionCode, PermissionScope scope) {
  return permissionRepo.findByFunctionCodeAndCanApproveAndDataScope(functionCode, scope);
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-core:compileJava`

---

## Task 5: Migrate CRMIdentityEventConsumer

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/CRMIdentityEventConsumer.java`

- [ ] **Step 1: Read current file**

Read `module/core/src/main/java/cloud/datatp/core/template/CRMIdentityEventConsumer.java` to understand full context.

- [ ] **Step 2: Replace UserAccessProfileLogic usage**

Replace the `UserAccessProfile` creation block (around lines 124-130):
```java
// OLD:
UserAccessProfile profile = accessProfileLogic.getByAccountId(ctx, accountId);
if (profile == null) {
  profile = new UserAccessProfile(newUserInfo);
  profile.initAllSelfOnlyPermissions();
  accessProfileLogic.save(ctx, profile);
}

// NEW:
List<UserFunctionPermission> permissions = permissionLogic.findByAccountId(ctx, accountId);
if (permissions.isEmpty()) {
  permissionLogic.seedFunctionDefinitions(ctx);
  permissionLogic.grantAllFunctions(ctx, accountId, PermissionScope.NONE, false, false, false, false, false, false);
}
```

Update imports: replace `UserAccessProfileLogic` with `UserFunctionPermissionLogic`, remove `UserAccessProfile` import. Replace `@Autowired private UserAccessProfileLogic accessProfileLogic;` with `@Autowired private UserFunctionPermissionLogic permissionLogic;`.

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-core:compileJava`

---

## Task 6: Migrate CRMPartnerLogic

**Files:**
- Modify: `module/partner/src/main/java/cloud/datatp/partner/CRMPartnerLogic.java`

- [ ] **Step 1: Read current file fully**

Read `module/partner/src/main/java/cloud/datatp/partner/CRMPartnerLogic.java`.

- [ ] **Step 2: Replace @Autowired field**

```java
// OLD:
@Autowired
private UserAccessProfileLogic accessProfileLogic;

// NEW:
@Autowired
private UserFunctionPermissionLogic permissionLogic;
```

- [ ] **Step 3: Migrate getPartnerIfAuthorized (lines 116-137)**

```java
// OLD:
UserAccessProfile permission = accessProfileLogic.getByAccountId(client, client.getAccountId());
if (permission == null) return null;
// ... permission.getAgentViewScope() == PermissionScope.GROUP_ALL

// NEW:
for (PartnerGroup pg : partnerGroups) {
  String functionCode = switch (pg) {
    case AGENTS -> "PARTNER_AGENT";
    case CUSTOMERS -> "PARTNER_CUSTOMER";
    case COLOADERS -> "PARTNER_COLOADER";
    default -> null;
  };
  if (functionCode != null && permissionLogic.hasPermission(client, client.getAccountId(), functionCode, CapabilityType.READ)
    && permissionLogic.getDataScope(client, client.getAccountId(), functionCode) == PermissionScope.GROUP_ALL) {
    return partner;
  }
}
```

- [ ] **Step 4: Migrate searchCRMPartners (lines 352-376)**

```java
// OLD: permission.getAgentViewScope().toString()
// NEW:
PermissionScope agentScope = permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_AGENT");
PermissionScope coloaderScope = permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_COLOADER");
PermissionScope customerScope = permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_CUSTOMER");
sqlParams.addParam("agentPermission", agentScope.toString());
sqlParams.addParam("coloaderPermission", coloaderScope.toString());
sqlParams.addParam("customerPermission", customerScope.toString());
sqlParams.addParam("accessAccountId", client.getAccountId());

UserFunctionPermission agentPerm = permissionLogic.getByAccountIdAndFunctionCode(client, client.getAccountId(), "PARTNER_AGENT");
if (agentPerm != null) {
  sqlParams.addParam("companyId", agentPerm.getCompanyId()); // NOTE: needs UserInfo lookup instead
  List<Long> accessibleAccountIds = agentPerm.getAccessibleAccountIds();
  if (!accessibleAccountIds.isEmpty()) sqlParams.addParam("accessibleAccountIds", accessibleAccountIds);
  List<Long> accessibleCompanyIds = agentPerm.getAccessibleCompanyBranchIds();
  if (!accessibleCompanyIds.isEmpty()) sqlParams.addParam("accessibleCompanyIds", accessibleCompanyIds);
}
```

Note: `companyId` was from `UserAccessProfile.companyId`. Since we removed that, use `client.getCompanyId()` instead.

- [ ] **Step 5: Migrate getPartnerRequestApprover (lines 304-349)**

```java
// OLD:
Function<PermissionScope, List<UserAccessProfile>> finder = switch (group) {
  case AGENTS -> scope -> accessProfileLogic.findUsersWithAgentApproveScope(client, scope);
  ...
};

// NEW:
String functionCode = switch (group) {
  case AGENTS -> "PARTNER_AGENT";
  case CUSTOMERS -> "PARTNER_CUSTOMER";
  case COLOADERS -> "PARTNER_COLOADER";
  default -> null;
};
if (functionCode == null) return new ArrayList<>();

Set<UserFunctionPermission> approverPermissions = new LinkedHashSet<>();
for (PermissionScope scope : scopes) {
  List<UserFunctionPermission> found = permissionLogic.findUsersWithApprovePermission(client, functionCode, scope);
  collectApprovers(scope, targetCompanyId, found, approverPermissions);
}
if (approverPermissions.isEmpty()) return new ArrayList<>();
List<Long> ids = approverPermissions.stream().map(UserFunctionPermission::getAccountId).collect(Collectors.toList());
return userInfoLogic.findByAccountIds(client, ids);
```

Update `collectApprovers` method signature to accept `List<UserFunctionPermission>` and `Set<UserFunctionPermission>`.

- [ ] **Step 6: Update imports**

Replace `UserAccessProfileLogic` with `UserFunctionPermissionLogic`, `UserAccessProfile` with `UserFunctionPermission`. Add `CapabilityType` import.

- [ ] **Step 7: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-partner:compileJava`

---

## Task 7: Migrate CustomerLeadsLogic

**Files:**
- Modify: `module/partner/src/main/java/cloud/datatp/partner/CustomerLeadsLogic.java`

- [ ] **Step 1: Read current file**
- [ ] **Step 2: Replace @Autowired and imports**
- [ ] **Step 3: Migrate getLeadIfAuthorized**

```java
// OLD: permission.getAgentPotentialViewScope() == PermissionScope.GROUP_ALL
// NEW:
if (type == CustomerLeadType.AGENTS_APPROACHED
  && permissionLogic.hasPermission(client, client.getAccountId(), "PARTNER_AGENTS_APPROACHED", CapabilityType.READ)
  && permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_AGENTS_APPROACHED") == PermissionScope.GROUP_ALL)
  return lead;
if (type == CustomerLeadType.CUSTOMER_LEAD
  && permissionLogic.hasPermission(client, client.getAccountId(), "PARTNER_CUSTOMER_LEAD", CapabilityType.READ)
  && permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_CUSTOMER_LEAD") == PermissionScope.GROUP_ALL)
  return lead;
```

- [ ] **Step 4: Migrate searchCustomerLeads**

```java
// OLD: permission.getAgentPotentialViewScope().toString()
// NEW:
sqlParams.addParam("agentPermission", permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_AGENTS_APPROACHED").toString());
sqlParams.addParam("customerPermission", permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_CUSTOMER_LEAD").toString());
sqlParams.addParam("accessAccountId", client.getAccountId());
sqlParams.addParam("companyId", client.getCompanyId());

List<Long> accessibleAccountIds = permissionLogic.getAccessibleAccountIds(client, client.getAccountId(), "PARTNER_AGENTS_APPROACHED");
if (!accessibleAccountIds.isEmpty()) sqlParams.addParam("accessibleAccountIds", accessibleAccountIds);

List<Long> accessibleCompanyIds = permissionLogic.getAccessibleCompanyBranchIds(client, client.getAccountId(), "PARTNER_AGENTS_APPROACHED");
if (!accessibleCompanyIds.isEmpty()) sqlParams.addParam("accessibleCompanyIds", accessibleCompanyIds);
```

- [ ] **Step 5: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-partner:compileJava`

---

## Task 8: Migrate PartnerReportLogic + PartnerRequestLogic

**Files:**
- Modify: `module/partner/src/main/java/cloud/datatp/partner/PartnerReportLogic.java`
- Modify: `module/partner/src/main/java/cloud/datatp/partner/PartnerRequestLogic.java`

- [ ] **Step 1: Read both files**
- [ ] **Step 2: Migrate PartnerReportLogic.searchIntegratedPartners**

Replace `profile.getTaskVisibilityScope()` with `permissionLogic.getDataScope(client, client.getAccountId(), "REPORT_PARTNER")`.
Replace `profile.getAccessibleAccountIds()` with `permissionLogic.getAccessibleAccountIds(client, client.getAccountId(), "REPORT_PARTNER")`.

- [ ] **Step 3: Migrate PartnerReportLogic.reportAgentTransactionsGroupByAgent**

```java
// OLD: accessProfileLogic.canEditResource(client, client.getAccountId(), ResourceType.AGENT, PermissionScope.GROUP_ALL)
// NEW:
boolean canEdit = permissionLogic.hasPermission(client, client.getAccountId(), "PARTNER_AGENT", CapabilityType.WRITE)
  && permissionLogic.getDataScope(client, client.getAccountId(), "PARTNER_AGENT") == PermissionScope.GROUP_ALL;
```

- [ ] **Step 4: Migrate PartnerRequestLogic.searchPartnerRequests**

Replace `accessProfileLogic.getByAccountId()` with relevant `permissionLogic` calls. The method only checks if permission exists (non-null check), so replace with `!permissionLogic.findByAccountId(client, client.getAccountId()).isEmpty()`.

- [ ] **Step 5: Update imports for both files**
- [ ] **Step 6: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-partner:compileJava`

---

## Task 9: Migrate TaskCalendarLogic

**Files:**
- Modify: `module/sales/src/main/java/cloud/datatp/sales/project/TaskCalendarLogic.java`

- [ ] **Step 1: Read current file**
- [ ] **Step 2: Replace @Autowired and imports**
- [ ] **Step 3: Migrate searchTasksCalendar**

```java
// OLD: if (!accessProfileLogic.computeTaskPermissionReport(client, sqlParams)) return Collections.emptyList();
// NEW: if (!permissionLogic.computePermissionReport(client, "TASK_CALENDAR", sqlParams)) return Collections.emptyList();
```

- [ ] **Step 4: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-sales:compileJava`

---

## Task 10: Migrate InquiryRequestLogic

**Files:**
- Modify: `module/price/src/main/java/cloud/datatp/price/request/InquiryRequestLogic.java`

- [ ] **Step 1: Read current file**
- [ ] **Step 2: Replace @Autowired and imports**
- [ ] **Step 3: Migrate all computeTaskPermissionReport calls (6 methods)**

Replace all occurrences:
```java
// OLD: if (!accessProfileLogic.computeTaskPermissionReport(client, sqlParams))
// NEW: if (!permissionLogic.computePermissionReport(client, "INQUIRY_REQUEST", sqlParams))
```

- [ ] **Step 4: Migrate pricingInquiryRequestReport (line 466-468)**

```java
// OLD:
UserAccessProfile profile = accessProfileLogic.getByAccountId(client, client.getAccountId());
PermissionScope scope = profile.getTaskVisibilityScope();

// NEW:
PermissionScope scope = permissionLogic.getDataScope(client, client.getAccountId(), "INQUIRY_REQUEST");
```

- [ ] **Step 5: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-price:compileJava`

---

## Task 11: Migrate BusinessReportLogic

**Files:**
- Modify: `module/reports/src/main/java/cloud/datatp/reports/bd/BusinessReportLogic.java`

- [ ] **Step 1: Read current file**
- [ ] **Step 2: Replace @Autowired and imports**
- [ ] **Step 3: Migrate all computeTaskPermissionReport calls (4 methods)**

Replace all occurrences:
```java
// OLD: if (!accessProfileLogic.computeTaskPermissionReport(client, sqlParams))
// NEW: if (!permissionLogic.computePermissionReport(client, "REPORT_QUOTATION", sqlParams))
```

- [ ] **Step 4: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-reports:compileJava`

---

## Task 12: Migrate PerformanceReportLogic

**Files:**
- Modify: `module/sales/src/main/java/cloud/datatp/sales/report/PerformanceReportLogic.java`

- [ ] **Step 1: Read current file fully**
- [ ] **Step 2: Replace @Autowired and imports**
- [ ] **Step 3: Migrate searchVolumePerformanceBySalemanReport + searchVolumeSalemanKeyAccountReport**

Both methods have identical scope-resolution pattern. Replace:
```java
// OLD:
UserAccessProfile permission = accessProfileLogic.getByAccountId(client, client.getAccountId());
PermissionScope scope = permission.getTaskVisibilityScope();
// ... scope-based logic with SELF_ONLY/COMPANY_ONLY/GROUP_ALL

// NEW - use computePermissionReport which handles all scope logic:
if (!permissionLogic.computePermissionReport(client, "REPORT_PERFORMANCE", sqlParams)) return new ArrayList<>();
```

Note: The existing manual scope logic is complex (fetches users by company, etc.). Replace with `computePermissionReport` which handles the same pattern. If the Groovy SQL scripts need `accessibleAccountIds` and `accessibleCompanyIds` params (not just `accessibleAccountIds` and `companyId`), add `accessibleCompanyIds` param support to `computePermissionReport`.

- [ ] **Step 4: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew :datatp-crm-module-sales:compileJava`

---

## Task 13: Migrate UserInfoModel (DTO)

**Files:**
- Modify: `module/core/src/main/java/cloud/datatp/core/template/dto/UserInfoModel.java`

- [ ] **Step 1: Read and check UserAccessProfile references**
- [ ] **Step 2: Replace references if any**
- [ ] **Step 3: Verify compilation**

---

## Task 14: Full Build Verification + Commit

- [ ] **Step 1: Run full build**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./gradlew build -x test`
Expected: BUILD SUCCESSFUL

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: migrate callers from UserAccessProfileLogic to UserFunctionPermissionLogic

Seed FunctionDefinition master data with 11 function codes.
Add migration method to convert UserAccessProfile data.
Update all callers across partner, price, sales, reports modules."
```
