# Tenant Registry DB Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hardcoded `TenantRegistry.java` with database-backed `TenantRegistryService` using 2 new tables, with in-memory cache (startup + TTL 30min).

**Architecture:** Liquibase migration creates `tenant_source` and `tenant_company` tables with seed data. JPA entities + Spring `@Component` service replaces static utility. Caffeine cache with 30-min TTL ensures performance. All 5 caller files switch from `TenantRegistry.*` static calls to injected `TenantRegistryService`.

**Tech Stack:** Java 17+, Spring Boot, JPA/Hibernate, Caffeine cache, Liquibase, PostgreSQL

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260504-tenant-registry-db-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `module/core/src/main/java/of1/fms/core/common/tenant/TenantSource.java` | JPA entity for `tenant_source` table |
| Create | `module/core/src/main/java/of1/fms/core/common/tenant/TenantCompany.java` | JPA entity for `tenant_company` table |
| Create | `module/core/src/main/java/of1/fms/core/common/tenant/TenantSourceRepository.java` | Spring Data repository |
| Create | `module/core/src/main/java/of1/fms/core/common/tenant/TenantCompanyRepository.java` | Spring Data repository |
| Create | `module/core/src/main/java/of1/fms/core/common/tenant/TenantRegistryService.java` | Cached service replacing static TenantRegistry |
| Modify | `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql` | Append changeset fms:62 (DDL + seed) |
| Modify | `module/core/src/main/java/of1/fms/core/db/FMSDaoService.java` | Replace `TenantRegistry.getDbUrl()` with service call + DB credentials |
| Modify | `module/core/src/main/java/of1/fms/core/cdc/service/InternalCallGateway.java` | Replace `TenantRegistry.getDatabaseSource()` |
| Modify | `module/transaction/src/main/java/of1/fms/module/transaction/cdc/CDCLookupSupport.java` | Replace `TenantRegistry.getDatabaseSource()` |
| Modify | `module/settings/src/main/java/of1/fms/settings/user/UserInfoLogic.java` | Replace `TenantRegistry.getDatabaseSource()` x2 |
| Modify | `module/integration/src/main/java/of1/fms/module/integration/batch/user/UserSyncLogic.java` | Replace `TenantRegistry.toInternalCompanyCode()` + `getDatabaseSource()` |
| Delete | `module/core/src/main/java/of1/fms/core/common/TenantRegistry.java` | Remove old hardcoded class |

---

## Task 1: Liquibase Migration — DDL + Seed Data

**Files:**
- Modify: `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql` (append after line 998)

- [ ] **Step 1: Append changeset fms:62 — CREATE tables + INSERT seed data**

Append the following SQL at the end of `002-schema-updates.sql`:

```sql
--changeset fms:62-tenant-registry-tables labels:schema-update context:dev,beta,prod
--comment: Create tenant_source and tenant_company tables to replace hardcoded TenantRegistry

CREATE TABLE IF NOT EXISTS tenant_source (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(32) NOT NULL,
    label VARCHAR(128),
    db_url VARCHAR(512) NOT NULL,
    db_username VARCHAR(128),
    db_password VARCHAR(256)
);
CREATE UNIQUE INDEX IF NOT EXISTS uk_tenant_source_code ON tenant_source(code);

CREATE TABLE IF NOT EXISTS tenant_company (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(32) NOT NULL,
    label VARCHAR(128),
    work_branch_codes VARCHAR(512),
    source_id BIGINT REFERENCES tenant_source(id),
    tenant_group VARCHAR(32)
);
CREATE UNIQUE INDEX IF NOT EXISTS uk_tenant_company_code ON tenant_company(code);
CREATE INDEX IF NOT EXISTS tenant_company_source_id_idx ON tenant_company(source_id);
CREATE INDEX IF NOT EXISTS tenant_company_tenant_group_idx ON tenant_company(tenant_group);

--changeset fms:62-tenant-registry-seed labels:schema-update context:dev,beta,prod
--comment: Seed tenant_source and tenant_company with data from hardcoded TenantRegistry

-- tenant_source seed (20 sources)
INSERT INTO tenant_source (code, label, db_url, db_username, db_password) VALUES
  ('BEE_VN',      'Bee Vietnam',       'jdbc:sqlserver://of1.beelogistics.com:34541;databaseName=BEE_DB;encrypt=true;trustServerCertificate=true;',         'devhph', 'Hph@dev!@#123'),
  ('BEE_INDIA',   'Bee India',         'jdbc:sqlserver://ind.openfreightone.com:34541;databaseName=BEEINDIA;encrypt=true;trustServerCertificate=true;',     'devhph', 'Hph@dev!@#123'),
  ('BEESCS',      'Bee SCS',           'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=BEESCS_DB;encrypt=true;trustServerCertificate=true;',   'devhph', 'Hph@dev!@#123'),
  ('TDLVN',       'Thu Do Logistics',  'jdbc:sqlserver://hpsvn.openfreightone.com:34541;databaseName=TD_DB;encrypt=true;trustServerCertificate=true;',      'devhph', 'Hph@dev!@#123'),
  ('BEE_PAC',     'Bee Pacific',       'jdbc:sqlserver://of1.beelogistics.com:34541;databaseName=PAC_DB;encrypt=true;trustServerCertificate=true;',         'devhph', 'Hph@dev!@#123'),
  ('BEE_VN_DIS',  'Bee VN DIS',        'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=BEEDIS_DB;encrypt=true;trustServerCertificate=true;',   'devhph', 'Hph@dev!@#123'),
  ('BEE_TRAN',    'Bee Tran',          'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=TRN_DB;encrypt=true;trustServerCertificate=true;',      'devhph', 'Hph@dev!@#123'),
  ('BEE_VN_PROJ', 'Bee VN Proj',       'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=BEEPROJ_DB;encrypt=true;trustServerCertificate=true;',  'devhph', 'Hph@dev!@#123'),
  ('BONDS',       'Bonds',             'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=BOND_DB;encrypt=true;trustServerCertificate=true;',     'devhph', 'Hph@dev!@#123'),
  ('MARINE',      'Marine',            'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=HANGHAI_DB;encrypt=true;trustServerCertificate=true;',   'devhph', 'Hph@dev!@#123'),
  ('HPS',         'HPS',               'jdbc:sqlserver://;serverName=10.43.39.49;databaseName=HPS_TEST_DB;encrypt=true;trustServerCertificate=true;',       'sa',     '12345678'),
  ('PROS_JSC',    'Pros JSC',          'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=PROS_DB;encrypt=true;trustServerCertificate=true;',     'devhph', 'Hph@dev!@#123'),
  ('TIENDAT',     'Tien Dat',          'jdbc:sqlserver://hpsvn.openfreightone.com:34541;databaseName=TIENDAT_DB;encrypt=true;trustServerCertificate=true;',  'devhph', 'Hph@dev!@#123'),
  ('BEE_ID',      'Bee Indonesia',     'jdbc:sqlserver://hpsvn.openfreightone.com:34541;databaseName=INDO_DB;encrypt=true;trustServerCertificate=true;',    'devhph', 'Hph@dev!@#123'),
  ('BEE_KH',      'Bee Cambodia',      'jdbc:sqlserver://pnh.beelogistics.com:34541;databaseName=BEECAM_DB;encrypt=true;trustServerCertificate=true;',      'devhph', 'Hph@dev!@#123'),
  ('BEE_MM',      'Bee Myanmar',       'jdbc:sqlserver://pnh.beelogistics.com:34541;databaseName=BEERGN_DB;encrypt=true;trustServerCertificate=true;',      'devhph', 'Hph@dev!@#123'),
  ('BEE_CN_CNC',  'Bee China CNC',     'jdbc:sqlserver://las.openfreightone.com:34541;databaseName=BEECN_DB;encrypt=true;trustServerCertificate=true;',     'devhph', 'Hph@dev!@#123'),
  ('BEE_MY',      'Bee Malaysia',      'jdbc:sqlserver://of1.beelogistics.com:34541;databaseName=MY_DB;encrypt=true;trustServerCertificate=true;',          'devhph', 'Hph@dev!@#123'),
  ('BEE_LA',      'Bee Laos',          'jdbc:sqlserver://pros.openfreightone.com:34541;databaseName=LAOS_DB;encrypt=true;trustServerCertificate=true;',     'devhph', 'Hph@dev!@#123'),
  ('BEE_US_OCL',  'Bee US OCL',        'jdbc:sqlserver://las.openfreightone.com:34541;databaseName=OCL_US_DB;encrypt=true;trustServerCertificate=true;',    'devhph', 'Hph@dev!@#123');

-- tenant_company seed (22 companies)
-- BEE_VN group (5 companies sharing BEE_VN source)
INSERT INTO tenant_company (code, label, work_branch_codes, source_id, tenant_group) VALUES
  ('bee',         'Bee Logistics',           NULL,                                                     (SELECT id FROM tenant_source WHERE code='BEE_VN'),      'BEE_VN'),
  ('beehan',      'Bee Ha Noi',              'BEEHN,BEELS',                                            (SELECT id FROM tenant_source WHERE code='BEE_VN'),      'BEE_VN'),
  ('beehph',      'Bee Hai Phong',           'BEEHP',                                                  (SELECT id FROM tenant_source WHERE code='BEE_VN'),      'BEE_VN'),
  ('beedad',      'Bee Da Nang',             'BEEDN,BEECRX',                                           (SELECT id FROM tenant_source WHERE code='BEE_VN'),      'BEE_VN'),
  ('beehcm',      'Bee Ho Chi Minh',         'BEEHCM',                                                 (SELECT id FROM tenant_source WHERE code='BEE_VN'),      'BEE_VN');

-- BEE_INDIA group
INSERT INTO tenant_company (code, label, work_branch_codes, source_id, tenant_group) VALUES
  ('bee-in',      'Bee India',               'BEEAMD,BEEBLR,BEEBOM,BEECCU,BEECHN,BEEHYD,BEEIND,BEEPUN', (SELECT id FROM tenant_source WHERE code='BEE_INDIA'), 'BEE_INDIA');

-- Individual tenants
INSERT INTO tenant_company (code, label, work_branch_codes, source_id, tenant_group) VALUES
  ('beescs',      'Bee SCS',                 'SCSHN',                                                  (SELECT id FROM tenant_source WHERE code='BEESCS'),      NULL),
  ('thudo',       'Thu Do Logistics',        NULL,                                                     (SELECT id FROM tenant_source WHERE code='TDLVN'),       NULL),
  ('bee-pac',     'Bee Pacific',             'PACVN',                                                  (SELECT id FROM tenant_source WHERE code='BEE_PAC'),     NULL),
  ('bee-vn-dis',  'Bee VN DIS',              'BEEDIS',                                                 (SELECT id FROM tenant_source WHERE code='BEE_VN_DIS'),  NULL),
  ('beetran',     'Bee Tran',                'TRNHCM',                                                 (SELECT id FROM tenant_source WHERE code='BEE_TRAN'),    NULL),
  ('bee-vn-proj', 'Bee VN Proj',             'BEEPROJ',                                                (SELECT id FROM tenant_source WHERE code='BEE_VN_PROJ'), NULL),
  ('bonds',       'Bonds',                   'BONDVN',                                                 (SELECT id FROM tenant_source WHERE code='BONDS'),       NULL),
  ('marine',      'Marine',                  'PTHH',                                                   (SELECT id FROM tenant_source WHERE code='MARINE'),      NULL),
  ('hps',         'HPS',                     'HPSVN',                                                  (SELECT id FROM tenant_source WHERE code='HPS'),         NULL),
  ('pros-jsc',    'Pros JSC',                'PROHCM',                                                 (SELECT id FROM tenant_source WHERE code='PROS_JSC'),    NULL),
  ('tiendat',     'Tien Dat',                'TIENDAT',                                                (SELECT id FROM tenant_source WHERE code='TIENDAT'),     NULL),
  ('bee-id',      'Bee Indonesia',           'INDO',                                                   (SELECT id FROM tenant_source WHERE code='BEE_ID'),      NULL),
  ('bee-kh',      'Bee Cambodia',            'BEEPNH',                                                 (SELECT id FROM tenant_source WHERE code='BEE_KH'),      NULL),
  ('bee-mm',      'Bee Myanmar',             'BEERGN',                                                 (SELECT id FROM tenant_source WHERE code='BEE_MM'),      NULL),
  ('bee-cn-cnc',  'Bee China CNC',           'BEECN',                                                  (SELECT id FROM tenant_source WHERE code='BEE_CN_CNC'),  NULL),
  ('bee-my',      'Bee Malaysia',            'MYPKL',                                                  (SELECT id FROM tenant_source WHERE code='BEE_MY'),      NULL),
  ('bee-la',      'Bee Laos',                'LAOS',                                                   (SELECT id FROM tenant_source WHERE code='BEE_LA'),      NULL),
  ('bee-us-ocl',  'Bee US OCL',              'OCLUS',                                                  (SELECT id FROM tenant_source WHERE code='BEE_US_OCL'),  NULL);
```

- [ ] **Step 2: Verify SQL syntax**

Run: `gradle compileJava` (Liquibase validates on startup, but compile check catches packaging issues)

- [ ] **Step 3: Commit**

```bash
git add module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql
git commit -m "feat(tenant): add liquibase migration for tenant_source and tenant_company tables"
```

---

## Task 2: JPA Entities

**Files:**
- Create: `module/core/src/main/java/of1/fms/core/common/tenant/TenantSource.java`
- Create: `module/core/src/main/java/of1/fms/core/common/tenant/TenantCompany.java`

- [ ] **Step 1: Create TenantSource entity**

```java
package of1.fms.core.common.tenant;

import jakarta.persistence.*;
import java.io.Serial;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.PersistableEntity;

@Entity
@Table(name = TenantSource.TABLE_NAME)
@NoArgsConstructor
@Getter
@Setter
public class TenantSource extends PersistableEntity<Long> {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "tenant_source";

  @Column(name = "code", nullable = false, length = 32)
  private String code;

  @Column(name = "label", length = 128)
  private String label;

  @Column(name = "db_url", nullable = false, length = 512)
  private String dbUrl;

  @Column(name = "db_username", length = 128)
  private String dbUsername;

  @Column(name = "db_password", length = 256)
  private String dbPassword;
}
```

- [ ] **Step 2: Create TenantCompany entity**

```java
package of1.fms.core.common.tenant;

import jakarta.persistence.*;
import java.io.Serial;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.PersistableEntity;

@Entity
@Table(name = TenantCompany.TABLE_NAME)
@NoArgsConstructor
@Getter
@Setter
public class TenantCompany extends PersistableEntity<Long> {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "tenant_company";

  @Column(name = "code", nullable = false, length = 32)
  private String code;

  @Column(name = "label", length = 128)
  private String label;

  @Column(name = "work_branch_codes", length = 512)
  private String workBranchCodes;

  @ManyToOne(fetch = FetchType.EAGER)
  @JoinColumn(name = "source_id")
  private TenantSource source;

  @Column(name = "tenant_group", length = 32)
  private String tenantGroup;
}
```

- [ ] **Step 3: Compile check**

Run: `gradle compileJava`

- [ ] **Step 4: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/common/tenant/
git commit -m "feat(tenant): add TenantSource and TenantCompany JPA entities"
```

---

## Task 3: Repositories

**Files:**
- Create: `module/core/src/main/java/of1/fms/core/common/tenant/TenantSourceRepository.java`
- Create: `module/core/src/main/java/of1/fms/core/common/tenant/TenantCompanyRepository.java`

- [ ] **Step 1: Create TenantSourceRepository**

```java
package of1.fms.core.common.tenant;

import java.io.Serializable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TenantSourceRepository extends JpaRepository<TenantSource, Serializable> {
}
```

- [ ] **Step 2: Create TenantCompanyRepository**

```java
package of1.fms.core.common.tenant;

import java.io.Serializable;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TenantCompanyRepository extends JpaRepository<TenantCompany, Serializable> {
  List<TenantCompany> findByTenantGroup(String tenantGroup);
}
```

- [ ] **Step 3: Compile check**

Run: `gradle compileJava`

- [ ] **Step 4: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/common/tenant/TenantSourceRepository.java
git add module/core/src/main/java/of1/fms/core/common/tenant/TenantCompanyRepository.java
git commit -m "feat(tenant): add TenantSource and TenantCompany repositories"
```

---

## Task 4: TenantRegistryService — Cached Service

**Files:**
- Create: `module/core/src/main/java/of1/fms/core/common/tenant/TenantRegistryService.java`

- [ ] **Step 1: Create TenantRegistryService**

This service loads all tenant data into in-memory maps at startup, rebuilds every 30 minutes via `@Scheduled`, and exposes the same method signatures as the old `TenantRegistry`.

```java
package of1.fms.core.common.tenant;

import jakarta.annotation.PostConstruct;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import lombok.extern.slf4j.Slf4j;
import net.datatp.util.text.StringUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class TenantRegistryService {

  @Autowired
  private TenantSourceRepository sourceRepo;

  @Autowired
  private TenantCompanyRepository companyRepo;

  // work-branch code (uppercase) -> tenant company code
  private volatile Map<String, String> workBranchToTenantCode = Map.of();

  // tenant code (lowercase) -> source code
  private volatile Map<String, String> tenantCodeToSource = Map.of();

  // source code (uppercase) -> TenantSource (contains URL + credentials)
  private volatile Map<String, TenantSource> sourceByCode = Map.of();

  // tenant group name -> set of tenant codes
  private volatile Map<String, Set<String>> tenantGroupMembers = Map.of();

  @PostConstruct
  public void init() {
    refresh();
  }

  @Scheduled(fixedRate = 30 * 60 * 1000) // 30 minutes
  public void refresh() {
    try {
      List<TenantSource> sources = sourceRepo.findAll();
      List<TenantCompany> companies = companyRepo.findAll();

      Map<String, TenantSource> newSourceByCode = new ConcurrentHashMap<>();
      for (TenantSource src : sources) {
        newSourceByCode.put(src.getCode().toUpperCase(), src);
      }

      Map<String, String> newWorkBranchMap = new ConcurrentHashMap<>();
      Map<String, String> newTenantToSource = new ConcurrentHashMap<>();
      Map<String, Set<String>> newGroupMembers = new ConcurrentHashMap<>();

      for (TenantCompany company : companies) {
        String tenantCode = company.getCode().toLowerCase();

        // Map tenant -> source
        if (company.getSource() != null) {
          newTenantToSource.put(tenantCode, company.getSource().getCode().toUpperCase());
        }

        // Map work-branch codes -> tenant
        if (company.getWorkBranchCodes() != null && !company.getWorkBranchCodes().isBlank()) {
          for (String branch : company.getWorkBranchCodes().split(",")) {
            String trimmed = branch.trim().toUpperCase();
            if (!trimmed.isEmpty()) {
              newWorkBranchMap.put(trimmed, tenantCode);
            }
          }
        }

        // Map tenant group
        if (company.getTenantGroup() != null && !company.getTenantGroup().isBlank()) {
          newGroupMembers
            .computeIfAbsent(company.getTenantGroup().toUpperCase(), k -> ConcurrentHashMap.newKeySet())
            .add(tenantCode);
        }
      }

      this.sourceByCode = newSourceByCode;
      this.workBranchToTenantCode = newWorkBranchMap;
      this.tenantCodeToSource = newTenantToSource;
      this.tenantGroupMembers = newGroupMembers;

      log.info("[TenantRegistry] Refreshed: {} sources, {} companies, {} work-branch mappings",
        sources.size(), companies.size(), newWorkBranchMap.size());
    } catch (Exception e) {
      log.error("[TenantRegistry] Failed to refresh tenant cache", e);
    }
  }

  /** Resolve work-branch code to internal tenant code. e.g. BEEHN -> beehan */
  public String toInternalCompanyCode(String workBranchCode) {
    if (StringUtil.isEmpty(workBranchCode)) return null;
    return workBranchToTenantCode.get(workBranchCode.trim().toUpperCase());
  }

  /** Resolve tenant code to logical data source key. e.g. beehcm -> BEE_VN */
  public String getDatabaseSource(String companyCode) {
    if (StringUtil.isEmpty(companyCode)) return "";
    return tenantCodeToSource.getOrDefault(companyCode.trim().toLowerCase(), "");
  }

  /** Resolve source code to JDBC URL. e.g. BEE_VN -> jdbc:sqlserver://... */
  public String getDbUrl(String sourceDb) {
    return getDbUrl(sourceDb, false);
  }

  /** Resolve source code to JDBC URL; fail fast when required. */
  public String getDbUrl(String sourceDb, boolean required) {
    if (StringUtil.isEmpty(sourceDb)) {
      if (required) throw new IllegalArgumentException("Invalid sourceDb: null/empty");
      return null;
    }
    TenantSource src = sourceByCode.get(sourceDb.trim().toUpperCase());
    if (src == null) {
      if (required) throw new IllegalArgumentException("Invalid sourceDb '" + sourceDb + "'");
      return null;
    }
    return src.getDbUrl();
  }

  /** Get full TenantSource (URL + credentials) by source code. Used by FMSDaoService. */
  public TenantSource getSource(String sourceDb) {
    if (StringUtil.isEmpty(sourceDb)) return null;
    return sourceByCode.get(sourceDb.trim().toUpperCase());
  }
}
```

- [ ] **Step 2: Enable scheduling in the app**

Check if `@EnableScheduling` already exists in the project. If not, it needs to be added to a `@Configuration` class. Search for existing config:

Run: `grep -r "@EnableScheduling" module/`

If not found, add `@EnableScheduling` to an existing config class (e.g., `CDCCacheConfig.java` or create a minimal config).

- [ ] **Step 3: Compile check**

Run: `gradle compileJava`

- [ ] **Step 4: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/common/tenant/TenantRegistryService.java
git commit -m "feat(tenant): add TenantRegistryService with startup cache and 30min TTL refresh"
```

---

## Task 5: Update Callers — FMSDaoService

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/db/FMSDaoService.java`

This is the most impactful change: `getBFSOneDataSource()` currently hardcodes credentials. After migration, it pulls URL + credentials from `TenantSource`.

- [ ] **Step 1: Inject TenantRegistryService and replace getBFSOneDataSource**

Replace the `TenantRegistry` import and update `getBFSOneDataSource` method:

Old code (lines 17, 57-68):
```java
import of1.fms.core.common.TenantRegistry;
```
```java
  public DataSource getBFSOneDataSource(ClientContext ctx, String sourceDb) {
    String url = TenantRegistry.getDbUrl(sourceDb, true);
    ExternalDataSourceManager.DataSourceParams dsParams = new ExternalDataSourceManager.DataSourceParams();
    dsParams.setUrl(url);
    if (url != null && url.contains("10.43.39.49")) {
      dsParams.setUsername("sa");
      dsParams.setPassword("12345678");
    } else {
      dsParams.setUsername("devhph");
      dsParams.setPassword("Hph@dev!@#123");
    }
    dsParams.setType("mssql");
    return dataSourceManager.getDataSource(ctx, dsParams);
  }
```

New code:
```java
import of1.fms.core.common.tenant.TenantRegistryService;
import of1.fms.core.common.tenant.TenantSource;
```
```java
  @Autowired
  protected TenantRegistryService tenantRegistryService;

  public DataSource getBFSOneDataSource(ClientContext ctx, String sourceDb) {
    TenantSource src = tenantRegistryService.getSource(sourceDb);
    if (src == null) {
      throw new IllegalArgumentException("Invalid sourceDb '" + sourceDb + "'");
    }
    ExternalDataSourceManager.DataSourceParams dsParams = new ExternalDataSourceManager.DataSourceParams();
    dsParams.setUrl(src.getDbUrl());
    dsParams.setUsername(src.getDbUsername());
    dsParams.setPassword(src.getDbPassword());
    dsParams.setType("mssql");
    return dataSourceManager.getDataSource(ctx, dsParams);
  }
```

- [ ] **Step 2: Compile check**

Run: `gradle compileJava`

- [ ] **Step 3: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/db/FMSDaoService.java
git commit -m "refactor(tenant): FMSDaoService reads DB URL and credentials from TenantRegistryService"
```

---

## Task 6: Update Callers — Remaining 4 Files

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/cdc/service/InternalCallGateway.java`
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/CDCLookupSupport.java`
- Modify: `module/settings/src/main/java/of1/fms/settings/user/UserInfoLogic.java`
- Modify: `module/integration/src/main/java/of1/fms/module/integration/batch/user/UserSyncLogic.java`

All 4 files extend `FMSDaoService` or have it available. Since `TenantRegistryService` is now `@Autowired` in `FMSDaoService`, subclasses (`UserInfoLogic`, `CDCLookupSupport`) can access it via `tenantRegistryService` field inherited from the parent.

For files that don't extend `FMSDaoService` (`InternalCallGateway`, `UserSyncLogic`), inject directly.

- [ ] **Step 1: Update InternalCallGateway.java**

Replace:
```java
import of1.fms.core.common.TenantRegistry;
```
With:
```java
import of1.fms.core.common.tenant.TenantRegistryService;
```

Add field:
```java
  @Autowired
  private TenantRegistryService tenantRegistryService;
```

Replace usage (line ~127):
```java
// Old: String databaseSource = TenantRegistry.getDatabaseSource(companyCode);
String databaseSource = tenantRegistryService.getDatabaseSource(companyCode);
```

- [ ] **Step 2: Update CDCLookupSupport.java**

This class extends `FMSDaoService`, so it inherits `tenantRegistryService`.

Replace import:
```java
// Remove: import of1.fms.core.common.TenantRegistry;
```

Replace usage (line ~142):
```java
// Old: String sourceDb = TenantRegistry.getDatabaseSource(ctx.getCompanyCode());
String sourceDb = tenantRegistryService.getDatabaseSource(ctx.getCompanyCode());
```

- [ ] **Step 3: Update UserInfoLogic.java**

This class extends `FMSDaoService`, so it inherits `tenantRegistryService`.

Replace import:
```java
// Remove: import of1.fms.core.common.TenantRegistry;
```

Replace both usages:
```java
// Old: String databaseSource = TenantRegistry.getDatabaseSource(client.getCompanyCode());
String databaseSource = tenantRegistryService.getDatabaseSource(client.getCompanyCode());
```

- [ ] **Step 4: Update UserSyncLogic.java**

Replace import:
```java
// Remove: import of1.fms.core.common.TenantRegistry;
import of1.fms.core.common.tenant.TenantRegistryService;
```

Add field:
```java
  @Autowired
  private TenantRegistryService tenantRegistryService;
```

Replace usages — line ~130:
```java
// Old: String tenantCode = TenantRegistry.toInternalCompanyCode(cmpId);
String tenantCode = tenantRegistryService.toInternalCompanyCode(cmpId);
```

Line ~168-170 — convert static method to instance method:
```java
// Old static method:
//   private static String resolveDataSource(String workBranchCode, String fallback) {
//     String tenantCode = TenantRegistry.toInternalCompanyCode(workBranchCode);
//     String source = TenantRegistry.getDatabaseSource(tenantCode);

// New instance method:
  private String resolveDataSource(String workBranchCode, String fallback) {
    if (workBranchCode == null || workBranchCode.isBlank()) return fallback;
    String tenantCode = tenantRegistryService.toInternalCompanyCode(workBranchCode);
    if (tenantCode == null) return fallback;
    String source = tenantRegistryService.getDatabaseSource(tenantCode);
    return (source == null || source.isBlank()) ? fallback : source;
  }
```

- [ ] **Step 5: Compile check**

Run: `gradle compileJava`

- [ ] **Step 6: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/cdc/service/InternalCallGateway.java
git add module/transaction/src/main/java/of1/fms/module/transaction/cdc/CDCLookupSupport.java
git add module/settings/src/main/java/of1/fms/settings/user/UserInfoLogic.java
git add module/integration/src/main/java/of1/fms/module/integration/batch/user/UserSyncLogic.java
git commit -m "refactor(tenant): replace static TenantRegistry calls with TenantRegistryService in all callers"
```

---

## Task 7: Delete TenantRegistry.java + Final Verification

**Files:**
- Delete: `module/core/src/main/java/of1/fms/core/common/TenantRegistry.java`

- [ ] **Step 1: Verify no remaining references**

Run: `grep -r "TenantRegistry" module/ --include="*.java" | grep -v "TenantRegistryService"`

Expected: no results (or only the file itself if not yet deleted)

- [ ] **Step 2: Delete the file**

```bash
rm module/core/src/main/java/of1/fms/core/common/TenantRegistry.java
```

- [ ] **Step 3: Full compile check**

Run: `gradle compileJava`

Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Commit**

```bash
git add -u module/core/src/main/java/of1/fms/core/common/TenantRegistry.java
git commit -m "refactor(tenant): remove hardcoded TenantRegistry, fully replaced by database-backed TenantRegistryService"
```
