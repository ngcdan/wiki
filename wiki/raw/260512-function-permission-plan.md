# Function Permission System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hardcoded `UserAccessProfile` with flexible function-level permission system using master data + per-user-per-function rows.

**Architecture:** Two main entities: `FunctionDefinition` (master data defining CRM screens/functions) and `UserFunctionPermission` (per-user capability booleans + data scope per function). Child tables `PermissionAccessibleCompanyBranch` and `PermissionAccessibleAccount` support CUSTOM scope. `UserFunctionPermissionLogic` replaces `UserAccessProfileLogic`.

**Tech Stack:** Java 21, Spring Boot, JPA/Hibernate, Lombok, PostgreSQL

**Spec:** `.claude/specs/260512-function-permission-design.md`

---

## File Structure

### New Files (all under `module/core/src/main/java/cloud/datatp/core/template/`)

| File | Responsibility |
|------|---------------|
| `entity/FunctionType.java` | Enum: SCREEN, FUNCTION |
| `entity/CapabilityType.java` | Enum: READ, WRITE, DELETE, APPROVE, PRINT, EXPORT |
| `entity/FunctionDefinition.java` | Master data entity defining CRM functions |
| `entity/UserFunctionPermission.java` | Per-user-per-function permission entity |
| `entity/PermissionAccessibleCompanyBranch.java` | Child entity for CUSTOM scope company branches |
| `entity/PermissionAccessibleAccount.java` | Child entity for CUSTOM scope accounts |
| `repository/FunctionDefinitionRepository.java` | JPA repository for FunctionDefinition |
| `repository/UserFunctionPermissionRepository.java` | JPA repository for UserFunctionPermission |
| `UserFunctionPermissionLogic.java` | Business logic replacing UserAccessProfileLogic |

### Existing Files to Reference (read-only during Phase 1)

| File | Why |
|------|-----|
| `entity/UserAccessProfile.java` | Pattern reference for entity structure, OneToMany, cascade |
| `entity/AccessibleCompanyBranch.java` | Pattern reference for child entity (extends Persistable) |
| `entity/AccessibleAccount.java` | Pattern reference for child entity |
| `entity/PermissionScope.java` | Reused enum, no changes |
| `repository/UserAccessProfileRepository.java` | Pattern reference for repository queries |
| `UserAccessProfileLogic.java` | Pattern reference for Logic class structure |

---

## Task 1: Create Enums (FunctionType, CapabilityType)

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/FunctionType.java`
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/CapabilityType.java`

- [ ] **Step 1: Create FunctionType enum**

```java
package cloud.datatp.core.template.entity;

public enum FunctionType {
  SCREEN,
  FUNCTION
}
```

- [ ] **Step 2: Create CapabilityType enum**

```java
package cloud.datatp.core.template.entity;

public enum CapabilityType {
  READ, WRITE, DELETE, APPROVE, PRINT, EXPORT
}
```

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 2: Create FunctionDefinition Entity

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/FunctionDefinition.java`
- Reference: `module/core/src/main/java/cloud/datatp/core/template/entity/UserInfo.java` (pattern for @Table, @Index, TABLE_NAME constant)

- [ ] **Step 1: Create FunctionDefinition entity**

```java
package cloud.datatp.core.template.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.io.Serial;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.PersistableEntity;

@Entity
@Table(
  name = FunctionDefinition.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = FunctionDefinition.TABLE_NAME + "_code_uk",
      columnNames = {"code"}
    )
  },
  indexes = {
    @Index(
      name = FunctionDefinition.TABLE_NAME + "_group_name_idx",
      columnList = "group_name"
    ),
    @Index(
      name = FunctionDefinition.TABLE_NAME + "_type_idx",
      columnList = "type"
    )
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor @AllArgsConstructor
@Setter @Getter
public class FunctionDefinition extends PersistableEntity<Long> {

  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "function_definition";

  @Column(name = "group_name", nullable = false)
  private String groupName;

  @Column(name = "function_name", nullable = false)
  private String functionName;

  @Column(name = "code", nullable = false)
  private String code;

  @Enumerated(EnumType.STRING)
  @Column(name = "type", nullable = false)
  private FunctionType type;

  @Column(name = "description")
  private String description;
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 3: Create Child Entities (PermissionAccessibleCompanyBranch, PermissionAccessibleAccount)

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/PermissionAccessibleCompanyBranch.java`
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/PermissionAccessibleAccount.java`
- Reference: `module/core/src/main/java/cloud/datatp/core/template/entity/AccessibleCompanyBranch.java` (pattern: extends Persistable, simple FK + value column)

- [ ] **Step 1: Create PermissionAccessibleCompanyBranch entity**

Follow same pattern as `AccessibleCompanyBranch`: extends `Persistable<Long>`, simple entity with FK index and unique constraint.

```java
package cloud.datatp.core.template.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.io.Serial;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.Persistable;

@Entity
@Table(
  name = PermissionAccessibleCompanyBranch.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = PermissionAccessibleCompanyBranch.TABLE_NAME + "_perm_company_uk",
      columnNames = {"permission_id", "company_branch_id"}
    )
  },
  indexes = {
    @Index(name = PermissionAccessibleCompanyBranch.TABLE_NAME + "_perm_id_idx", columnList = "permission_id")
  }
)
@NoArgsConstructor
@Getter @Setter
public class PermissionAccessibleCompanyBranch extends Persistable<Long> {

  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "permission_accessible_company_branch";

  @Column(name = "company_branch_id", nullable = false)
  private Long companyBranchId;

  public PermissionAccessibleCompanyBranch(Long companyBranchId) {
    this.companyBranchId = companyBranchId;
  }
}
```

- [ ] **Step 2: Create PermissionAccessibleAccount entity**

```java
package cloud.datatp.core.template.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.io.Serial;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.Persistable;

@Entity
@Table(
  name = PermissionAccessibleAccount.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = PermissionAccessibleAccount.TABLE_NAME + "_perm_account_uk",
      columnNames = {"permission_id", "accessible_account_id"}
    )
  },
  indexes = {
    @Index(name = PermissionAccessibleAccount.TABLE_NAME + "_perm_id_idx", columnList = "permission_id")
  }
)
@NoArgsConstructor
@Getter @Setter
public class PermissionAccessibleAccount extends Persistable<Long> {

  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "permission_accessible_account";

  @Column(name = "accessible_account_id", nullable = false)
  private Long accessibleAccountId;

  public PermissionAccessibleAccount(Long accessibleAccountId) {
    this.accessibleAccountId = accessibleAccountId;
  }
}
```

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 4: Create UserFunctionPermission Entity

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/entity/UserFunctionPermission.java`
- Reference: `module/core/src/main/java/cloud/datatp/core/template/entity/UserAccessProfile.java` (pattern for OneToMany with CascadeType.ALL + orphanRemoval, @JoinColumn)

- [ ] **Step 1: Create UserFunctionPermission entity**

```java
package cloud.datatp.core.template.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.io.Serial;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.PersistableEntity;

@Entity
@Table(
  name = UserFunctionPermission.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = UserFunctionPermission.TABLE_NAME + "_account_func_uk",
      columnNames = {"account_id", "function_definition_id"}
    )
  },
  indexes = {
    @Index(
      name = UserFunctionPermission.TABLE_NAME + "_account_id_idx",
      columnList = "account_id"
    ),
    @Index(
      name = UserFunctionPermission.TABLE_NAME + "_func_def_id_idx",
      columnList = "function_definition_id"
    )
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor @AllArgsConstructor
@Setter @Getter
public class UserFunctionPermission extends PersistableEntity<Long> {

  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "user_function_permission";

  @Column(name = "account_id", nullable = false)
  private Long accountId;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "function_definition_id", nullable = false)
  private FunctionDefinition functionDefinition;

  @Enumerated(EnumType.STRING)
  @Column(name = "data_scope", nullable = false)
  private PermissionScope dataScope = PermissionScope.NONE;

  @Column(name = "can_read", nullable = false)
  private boolean canRead = false;

  @Column(name = "can_write", nullable = false)
  private boolean canWrite = false;

  @Column(name = "can_delete", nullable = false)
  private boolean canDelete = false;

  @Column(name = "can_approve", nullable = false)
  private boolean canApprove = false;

  @Column(name = "can_print", nullable = false)
  private boolean canPrint = false;

  @Column(name = "can_export", nullable = false)
  private boolean canExport = false;

  @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
  @JoinColumn(name = "permission_id")
  private List<PermissionAccessibleCompanyBranch> accessibleCompanyBranches = new ArrayList<>();

  @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
  @JoinColumn(name = "permission_id")
  private List<PermissionAccessibleAccount> accessibleAccounts = new ArrayList<>();

  // ============ ACCESSIBLE HELPERS ============

  public List<Long> getAccessibleCompanyBranchIds() {
    if (accessibleCompanyBranches == null) return new ArrayList<>();
    return accessibleCompanyBranches.stream()
      .map(PermissionAccessibleCompanyBranch::getCompanyBranchId)
      .collect(Collectors.toList());
  }

  public void setAccessibleCompanyBranchIds(Set<Long> branchIds) {
    if (this.accessibleCompanyBranches == null) this.accessibleCompanyBranches = new ArrayList<>();
    this.accessibleCompanyBranches.clear();
    if (branchIds != null) {
      for (Long branchId : branchIds) {
        this.accessibleCompanyBranches.add(new PermissionAccessibleCompanyBranch(branchId));
      }
    }
  }

  public List<Long> getAccessibleAccountIds() {
    if (accessibleAccounts == null) return new ArrayList<>();
    return accessibleAccounts.stream()
      .map(PermissionAccessibleAccount::getAccessibleAccountId)
      .collect(Collectors.toList());
  }

  public void setAccessibleAccountIds(Set<Long> accountIds) {
    if (this.accessibleAccounts == null) this.accessibleAccounts = new ArrayList<>();
    this.accessibleAccounts.clear();
    if (accountIds != null) {
      for (Long accountId : accountIds) {
        this.accessibleAccounts.add(new PermissionAccessibleAccount(accountId));
      }
    }
  }

  // ============ CAPABILITY CHECK ============

  public boolean hasCapability(CapabilityType type) {
    return switch (type) {
      case READ -> canRead;
      case WRITE -> canWrite;
      case DELETE -> canDelete;
      case APPROVE -> canApprove;
      case PRINT -> canPrint;
      case EXPORT -> canExport;
    };
  }
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 5: Create Repositories

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/repository/FunctionDefinitionRepository.java`
- Create: `module/core/src/main/java/cloud/datatp/core/template/repository/UserFunctionPermissionRepository.java`
- Reference: `module/core/src/main/java/cloud/datatp/core/template/repository/UserAccessProfileRepository.java` (pattern for @Repository, @Query, @Param)

- [ ] **Step 1: Create FunctionDefinitionRepository**

```java
package cloud.datatp.core.template.repository;

import cloud.datatp.core.template.entity.FunctionDefinition;
import cloud.datatp.core.template.entity.FunctionType;
import java.io.Serializable;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FunctionDefinitionRepository extends JpaRepository<FunctionDefinition, Serializable> {

  FunctionDefinition getByCode(String code);

  List<FunctionDefinition> findByGroupName(String groupName);

  List<FunctionDefinition> findByType(FunctionType type);
}
```

- [ ] **Step 2: Create UserFunctionPermissionRepository**

```java
package cloud.datatp.core.template.repository;

import cloud.datatp.core.template.entity.UserFunctionPermission;
import java.io.Serializable;
import java.util.List;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserFunctionPermissionRepository extends JpaRepository<UserFunctionPermission, Serializable> {

  List<UserFunctionPermission> findByAccountId(Long accountId);

  UserFunctionPermission getByAccountIdAndFunctionDefinitionId(Long accountId, Long functionDefinitionId);

  @Query("SELECT p FROM UserFunctionPermission p JOIN p.functionDefinition fd WHERE p.accountId = :accountId AND fd.code = :code")
  UserFunctionPermission getByAccountIdAndFunctionCode(@Param("accountId") Long accountId, @Param("code") String code);

  @Query("SELECT p FROM UserFunctionPermission p JOIN p.functionDefinition fd WHERE p.accountId = :accountId AND fd.groupName = :groupName")
  List<UserFunctionPermission> findByAccountIdAndGroup(@Param("accountId") Long accountId, @Param("groupName") String groupName);

  void deleteByAccountId(Long accountId);
}
```

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 6: Create UserFunctionPermissionLogic

**Files:**
- Create: `module/core/src/main/java/cloud/datatp/core/template/UserFunctionPermissionLogic.java`
- Reference: `module/core/src/main/java/cloud/datatp/core/template/UserAccessProfileLogic.java` (pattern for Logic class structure, CRMDaoService, @Component, ClientContext)

- [ ] **Step 1: Create UserFunctionPermissionLogic with CRUD + permission check methods**

```java
package cloud.datatp.core.template;

import cloud.datatp.core.db.CRMDaoService;
import cloud.datatp.core.template.entity.CapabilityType;
import cloud.datatp.core.template.entity.FunctionDefinition;
import cloud.datatp.core.template.entity.FunctionType;
import cloud.datatp.core.template.entity.PermissionScope;
import cloud.datatp.core.template.entity.UserFunctionPermission;
import cloud.datatp.core.template.entity.UserInfo;
import cloud.datatp.core.template.repository.FunctionDefinitionRepository;
import cloud.datatp.core.template.repository.UserFunctionPermissionRepository;
import cloud.datatp.core.template.repository.UserInfoRepository;
import java.util.ArrayList;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import net.datatp.module.company.entity.Company;
import net.datatp.module.data.db.query.SqlQueryParams;
import net.datatp.security.client.ClientContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class UserFunctionPermissionLogic extends CRMDaoService {

  @Autowired
  private UserFunctionPermissionRepository permissionRepo;

  @Autowired
  private FunctionDefinitionRepository functionRepo;

  @Autowired
  private UserInfoRepository userInfoRepo;

  // ============ FUNCTION DEFINITION CRUD ============

  public FunctionDefinition createFunction(ClientContext client, FunctionDefinition functionDef) {
    functionDef.set(client);
    return functionRepo.save(functionDef);
  }

  public List<FunctionDefinition> findAllFunctions(ClientContext client) {
    return functionRepo.findAll();
  }

  public List<FunctionDefinition> findFunctionsByGroup(ClientContext client, String groupName) {
    return functionRepo.findByGroupName(groupName);
  }

  public FunctionDefinition getFunctionByCode(ClientContext client, String code) {
    return functionRepo.getByCode(code);
  }

  // ============ PERMISSION CRUD ============

  public UserFunctionPermission getById(ClientContext client, Long id) {
    return permissionRepo.findById(id).orElse(null);
  }

  public List<UserFunctionPermission> findByAccountId(ClientContext client, Long accountId) {
    return permissionRepo.findByAccountId(accountId);
  }

  public UserFunctionPermission getByAccountIdAndFunctionCode(ClientContext client, Long accountId, String functionCode) {
    return permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
  }

  public List<UserFunctionPermission> findByAccountIdAndGroup(ClientContext client, Long accountId, String groupName) {
    return permissionRepo.findByAccountIdAndGroup(accountId, groupName);
  }

  public UserFunctionPermission save(ClientContext client, UserFunctionPermission permission) {
    permission.set(client);
    return permissionRepo.save(permission);
  }

  public boolean deleteById(ClientContext client, Long id) {
    permissionRepo.deleteById(id);
    return true;
  }

  // ============ PERMISSION CHECK ============

  public boolean hasPermission(ClientContext client, Long accountId, String functionCode, CapabilityType capabilityType) {
    UserFunctionPermission permission = permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
    if (permission == null) return false;
    return permission.hasCapability(capabilityType);
  }

  public PermissionScope getDataScope(ClientContext client, Long accountId, String functionCode) {
    UserFunctionPermission permission = permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
    if (permission == null) return PermissionScope.NONE;
    return permission.getDataScope();
  }

  public List<Long> getAccessibleCompanyBranchIds(ClientContext client, Long accountId, String functionCode) {
    UserFunctionPermission permission = permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
    if (permission == null) return new ArrayList<>();
    return permission.getAccessibleCompanyBranchIds();
  }

  public List<Long> getAccessibleAccountIds(ClientContext client, Long accountId, String functionCode) {
    UserFunctionPermission permission = permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
    if (permission == null) return new ArrayList<>();
    return permission.getAccessibleAccountIds();
  }

  // ============ DATA SCOPE QUERY SUPPORT ============

  public boolean computePermissionReport(ClientContext client, String functionCode, SqlQueryParams sqlParams) {
    UserFunctionPermission permission = getByAccountIdAndFunctionCode(client, client.getAccountId(), functionCode);
    if (permission == null) return false;

    PermissionScope scope = permission.getDataScope();
    String companyCode = sqlParams.getString("companyCode");
    Long currentCompanyId = null;
    if (companyCode != null) {
      Company company = platformCallGateway.getCompanyInfo(client, companyCode);
      if (company != null) currentCompanyId = company.getId();
    }

    if (PermissionScope.GROUP_ALL == scope) {
      sqlParams.addParam("companyId", currentCompanyId);
      return true;
    } else if (PermissionScope.COMPANY_ONLY == scope) {
      sqlParams.addParam("companyId", currentCompanyId);
      List<Long> accessibleAccountIds = permission.getAccessibleAccountIds();
      if (!accessibleAccountIds.isEmpty()) {
        sqlParams.addParam("accessibleAccountIds", accessibleAccountIds);
      }
      return true;
    } else if (PermissionScope.CUSTOM == scope) {
      List<Long> accessibleBranchIds = permission.getAccessibleCompanyBranchIds();
      if (currentCompanyId != null && !accessibleBranchIds.isEmpty() && !accessibleBranchIds.contains(currentCompanyId)) {
        return false;
      }
      sqlParams.addParam("companyId", currentCompanyId);
      List<Long> accessibleAccountIds = permission.getAccessibleAccountIds();
      if (!accessibleAccountIds.isEmpty()) {
        sqlParams.addParam("accessibleAccountIds", accessibleAccountIds);
      }
      return true;
    } else if (PermissionScope.SELF_ONLY == scope) {
      if (!sqlParams.hasParam("accessAccountId")) {
        List<Long> accessibleAccountIds = permission.getAccessibleAccountIds();
        accessibleAccountIds.add(client.getAccountId());
        sqlParams.addParam("accessibleAccountIds", accessibleAccountIds);
      }
      return true;
    }
    return false;
  }

  // ============ BATCH GRANT ============

  public UserFunctionPermission grantPermissions(ClientContext client, Long accountId, String functionCode,
    PermissionScope dataScope, boolean canRead, boolean canWrite, boolean canDelete,
    boolean canApprove, boolean canPrint, boolean canExport) {
    UserFunctionPermission permission = permissionRepo.getByAccountIdAndFunctionCode(accountId, functionCode);
    if (permission == null) {
      FunctionDefinition funcDef = functionRepo.getByCode(functionCode);
      if (funcDef == null) throw new RuntimeException("FunctionDefinition not found: " + functionCode);
      permission = new UserFunctionPermission();
      permission.setAccountId(accountId);
      permission.setFunctionDefinition(funcDef);
    }
    permission.setDataScope(dataScope);
    permission.setCanRead(canRead);
    permission.setCanWrite(canWrite);
    permission.setCanDelete(canDelete);
    permission.setCanApprove(canApprove);
    permission.setCanPrint(canPrint);
    permission.setCanExport(canExport);
    return save(client, permission);
  }

  public void grantAllFunctions(ClientContext client, Long accountId, PermissionScope dataScope,
    boolean canRead, boolean canWrite, boolean canDelete,
    boolean canApprove, boolean canPrint, boolean canExport) {
    List<FunctionDefinition> allFunctions = functionRepo.findAll();
    for (FunctionDefinition funcDef : allFunctions) {
      grantPermissions(client, accountId, funcDef.getCode(), dataScope,
        canRead, canWrite, canDelete, canApprove, canPrint, canExport);
    }
  }

  public void revokeAllPermissions(ClientContext client, Long accountId) {
    permissionRepo.deleteByAccountId(accountId);
  }

  // ============ SYNC ============

  public int syncWithUserRoles(ClientContext client) {
    List<UserInfo> allUsers = userInfoRepo.findAll();
    List<FunctionDefinition> allFunctions = functionRepo.findAll();
    int count = 0;
    for (UserInfo user : allUsers) {
      List<UserFunctionPermission> existing = permissionRepo.findByAccountId(user.getAccountId());
      if (existing.isEmpty()) {
        for (FunctionDefinition funcDef : allFunctions) {
          try {
            UserFunctionPermission permission = new UserFunctionPermission();
            permission.setAccountId(user.getAccountId());
            permission.setFunctionDefinition(funcDef);
            permission.setDataScope(PermissionScope.NONE);
            save(client, permission);
            count++;
          } catch (Exception e) {
            log.error("Error creating permission for user {} function {}", user.getAccountId(), funcDef.getCode(), e);
          }
        }
        log.info("Created {} permissions for user: {}", allFunctions.size(), user.getAccountId());
      }
    }
    return count;
  }
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build core`
Expected: BUILD SUCCESS

---

## Task 7: Verify Full Build

- [ ] **Step 1: Run full project build**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm && ./tools.sh build`
Expected: BUILD SUCCESS across all modules (core, partner, price, sales, reports)

The new entities exist alongside old ones. No callers are changed yet, so all existing code continues to work.

- [ ] **Step 2: Commit Phase 1**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-crm
git add module/core/src/main/java/cloud/datatp/core/template/entity/FunctionType.java \
  module/core/src/main/java/cloud/datatp/core/template/entity/CapabilityType.java \
  module/core/src/main/java/cloud/datatp/core/template/entity/FunctionDefinition.java \
  module/core/src/main/java/cloud/datatp/core/template/entity/UserFunctionPermission.java \
  module/core/src/main/java/cloud/datatp/core/template/entity/PermissionAccessibleCompanyBranch.java \
  module/core/src/main/java/cloud/datatp/core/template/entity/PermissionAccessibleAccount.java \
  module/core/src/main/java/cloud/datatp/core/template/repository/FunctionDefinitionRepository.java \
  module/core/src/main/java/cloud/datatp/core/template/repository/UserFunctionPermissionRepository.java \
  module/core/src/main/java/cloud/datatp/core/template/UserFunctionPermissionLogic.java
git commit -m "feat: add function permission system entities, repositories and logic"
```

---

## Notes for Future Phases (not in this plan)

The following phases from the spec are **out of scope** for this implementation plan. They should be planned separately after Phase 1 is deployed and verified:

- **Phase 2-3**: Seed `FunctionDefinition` master data + migration script from `UserAccessProfile` data
- **Phase 4**: Update callers in partner, sales, reports, task modules
- **Phase 5**: Remove deprecated entities (`UserAccessProfile`, `ResourceType`, etc.)
