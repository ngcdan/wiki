# FMS Transaction Type Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo 2 bảng `of1_fms_transaction_type` (global metadata, 15 seed rows) + `of1_fms_transaction_type_sequence` (per-company doc number + lock config) cho FMS, mở rộng enum `TypeOfService` thêm 4 values, và service sinh document number có row-lock.

**Architecture:** Hybrid — enum Java là source-of-truth cho code, bảng DB lưu metadata + cấu hình per-company. Startup validator đảm bảo đồng bộ. MSSQL import tách riêng khỏi Liquibase. Không đụng `Transaction.typeOfService` column hiện tại.

**Tech Stack:** Java 17+, Spring Boot, JPA/Hibernate, PostgreSQL, Liquibase (formatted SQL), JUnit 5, Mockito, Testcontainers.

**Spec reference:** `/Users/nqcdan/dev/wiki/wiki/daily/260408-fms-transaction-type.md`

---

## File Structure

### Files to create

| Path | Responsibility |
|---|---|
| `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java` | Global metadata entity (standalone — không extend PersistableEntity vì PK là String không auto-generate) |
| `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java` | Per-company config entity, extends `CompanyEntity` |
| `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java` | JpaRepository<TransactionType, String> |
| `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java` | JpaRepository với pessimistic lock query |
| `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java` | Service: get metadata, generate next number, startup sync validator |
| `module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java` | Pure util — format `{SIGN}{YY}{MM}{###}` template → string |
| `module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java` | Unit test formatter |
| `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java` | Unit test service logic (mock repositories) |
| `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java` | Integration test: concurrent `generateNextNumber` không sinh trùng |

### Files to modify

| Path | Change |
|---|---|
| `module/core/src/main/java/of1/fms/core/common/TypeOfService.java` | Thêm 4 enum values + 4 switch cases trong `resolve()` |
| `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql` | Append 3 changesets (`fms:22`, `fms:23`, `fms:24`) |

---

## Task 1: Mở rộng enum `TypeOfService`

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/common/TypeOfService.java`

- [ ] **Step 1.1: Thêm 4 enum values**

Sửa block enum (sau `WAREHOUSE`, trước dấu `;`):

```java
public enum TypeOfService {
  AIR_EXPORT,
  AIR_IMPORT,
  SEA_EXPORT_FCL,
  SEA_EXPORT_LCL,
  SEA_EXPORT_CSL,
  SEA_IMPORT_FCL,
  SEA_IMPORT_LCL,
  SEA_IMPORT_CSL,
  CUSTOMS_LOGISTICS,
  INLAND_TRUCKING,
  CROSS_BORDER,
  ROUND_USE_TRUCKING,
  WAREHOUSE,
  EXPRESS,
  PROJECT_LOGISTICS;
  ...
}
```

- [ ] **Step 1.2: Thêm 4 switch cases vào `resolve()`**

```java
case "SeaExpTransactions_CSL"  -> SEA_EXPORT_CSL;
case "SeaImpTransactions_CSL"  -> SEA_IMPORT_CSL;
case "ExpressTransactions"     -> EXPRESS;
case "ProjectLogistics"        -> PROJECT_LOGISTICS;
```

Đặt chúng theo thứ tự logic cùng nhóm (CSL cạnh FCL/LCL, EXPRESS / PROJECT_LOGISTICS cuối).

- [ ] **Step 1.3: Build module core**

Run: `./gradlew :module:core:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 1.4: Commit**

```bash
git add module/core/src/main/java/of1/fms/core/common/TypeOfService.java
git commit -m "feat(core): extend TypeOfService with EXPRESS, PROJECT_LOGISTICS, SEA_*_CSL"
```

---

## Task 2: Liquibase changeset — tạo 2 bảng + seed

**Files:**
- Modify: `module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql`

- [ ] **Step 2.1: Append changeset fms:22 (create transaction_type)**

Append vào cuối file:

```sql
--changeset fms:22-create-transaction-type labels:schema-update context:dev,beta,prod
--comment: Tạo bảng of1_fms_transaction_type (global metadata) thay thế enum TypeOfService hardcode
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

- [ ] **Step 2.2: Append changeset fms:23 (seed 15 rows)**

```sql
--changeset fms:23-seed-transaction-type labels:schema-update context:dev,beta,prod
--comment: Seed 15 loại giao dịch khớp enum TypeOfService (11 cũ + 4 mới)
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

- [ ] **Step 2.3: Append changeset fms:24 (create transaction_type_sequence)**

```sql
--changeset fms:24-create-transaction-type-sequence labels:schema-update context:dev,beta,prod
--comment: Tạo bảng of1_fms_transaction_type_sequence per-company lưu config sinh document number và lock days
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

- [ ] **Step 2.4: Verify Liquibase formatted SQL syntax**

Run manual check: mở file, đảm bảo mỗi changeset có `--changeset fms:N-slug labels:schema-update context:dev,beta,prod` header.

- [ ] **Step 2.5: Apply migration lên DB dev**

Run: `./gradlew :module:core:bootRun -Pprofile=dev` (hoặc script Liquibase update tương đương trong repo)
Expected: Log "ChangeSet fms:22-create-transaction-type ran successfully" (và 23, 24). Không có ERROR.

- [ ] **Step 2.6: Verify bảng + rows trên Postgres**

```sql
SELECT COUNT(*) FROM of1_fms_transaction_type;  -- expect 15
SELECT id_trans_type FROM of1_fms_transaction_type ORDER BY id_trans_type;
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'of1_fms_transaction_type%';
```

- [ ] **Step 2.7: Commit**

```bash
git add module/core/src/main/resources/db/changelog/changes/002-schema-updates.sql
git commit -m "feat(db): add of1_fms_transaction_type + sequence tables with seed"
```

---

## Task 3: Entity `TransactionType`

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java`

> **Note**: Không extend `PersistableEntity<String>` vì base class có `@Id @GeneratedValue(IDENTITY)` — không phù hợp với String PK không auto-generate. Thay vào đó tự khai báo các audit field để match schema DB.

- [ ] **Step 3.1: Create TransactionType.java**

```java
package of1.fms.module.transaction.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import of1.fms.core.common.TypeOfService;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

@Entity
@Table(
  name = TransactionType.TABLE_NAME,
  indexes = {
    @Index(name = TransactionType.TABLE_NAME + "_legacy_idx", columnList = "legacy_mssql_code")
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter
@Setter
public class TransactionType implements Serializable {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "of1_fms_transaction_type";

  @Id
  @Column(name = "id_trans_type", length = 50, nullable = false)
  private String idTransType;

  @Column(name = "description", length = 255, nullable = false)
  private String description;

  @Column(name = "type_list", length = 255, nullable = false)
  private String typeList;

  @Column(name = "legacy_mssql_code", length = 255)
  private String legacyMssqlCode;

  @Column(name = "storage_state", length = 255)
  private String storageState;

  @Column(name = "version")
  private Long version;

  @Column(name = "created_by", length = 255)
  private String createdBy;

  @Column(name = "created_time")
  private Date createdTime;

  @Column(name = "modified_by", length = 255)
  private String modifiedBy;

  @Column(name = "modified_time")
  private Date modifiedTime;

  /** Convenience: resolve to enum value. Returns null if no match. */
  public TypeOfService toEnum() {
    return TypeOfService.parse(idTransType);
  }
}
```

- [ ] **Step 3.2: Build module transaction**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 3.3: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionType.java
git commit -m "feat(transaction): add TransactionType entity"
```

---

## Task 4: Entity `TransactionTypeSequence`

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java`

- [ ] **Step 4.1: Create TransactionTypeSequence.java**

```java
package of1.fms.module.transaction.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.CompanyEntity;

import java.io.Serial;
import java.time.LocalDate;

@Entity
@Table(
  name = TransactionTypeSequence.TABLE_NAME,
  uniqueConstraints = {
    @UniqueConstraint(
      name = TransactionTypeSequence.TABLE_NAME + "_company_type_uk",
      columnNames = {"company_id", "id_trans_type"}
    )
  },
  indexes = {
    @Index(
      name = TransactionTypeSequence.TABLE_NAME + "_company_idx",
      columnList = "company_id"
    )
  }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter
@Setter
public class TransactionTypeSequence extends CompanyEntity {
  @Serial
  private static final long serialVersionUID = 1L;

  public static final String TABLE_NAME = "of1_fms_transaction_type_sequence";

  @Column(name = "id_trans_type", length = 50, nullable = false)
  private String idTransType;

  @Column(name = "sign_prefix", length = 255)
  private String signPrefix;

  @Column(name = "number_format", length = 255)
  private String numberFormat;

  @Column(name = "reset_period_days", nullable = false)
  private Integer resetPeriodDays = 365;

  @Column(name = "current_sequence", nullable = false)
  private Integer currentSequence = 0;

  @Column(name = "last_reset_date")
  private LocalDate lastResetDate;

  @Column(name = "no_days_lock", nullable = false)
  private Integer noDaysLock = 0;

  @Column(name = "day_of_logistics_lock", nullable = false)
  private Integer dayOfLogisticsLock = 0;

  @Column(name = "lock_again_after_unlock", nullable = false)
  private Integer lockAgainAfterUnlock = 0;
}
```

- [ ] **Step 4.2: Build**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 4.3: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/entity/TransactionTypeSequence.java
git commit -m "feat(transaction): add TransactionTypeSequence entity"
```

---

## Task 5: Repositories

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java`
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java`

- [ ] **Step 5.1: Create TransactionTypeRepository**

Kiểm tra package repository hiện có: `ls module/transaction/src/main/java/of1/fms/module/transaction/repository/ 2>/dev/null` — nếu chưa có thì tạo.

```java
package of1.fms.module.transaction.repository;

import of1.fms.module.transaction.entity.TransactionType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TransactionTypeRepository extends JpaRepository<TransactionType, String> {
  Optional<TransactionType> findByLegacyMssqlCode(String mssqlCode);
}
```

- [ ] **Step 5.2: Create TransactionTypeSequenceRepository**

```java
package of1.fms.module.transaction.repository;

import jakarta.persistence.LockModeType;
import of1.fms.module.transaction.entity.TransactionTypeSequence;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TransactionTypeSequenceRepository
    extends JpaRepository<TransactionTypeSequence, Long> {

  Optional<TransactionTypeSequence> findByCompanyIdAndIdTransType(Long companyId, String idTransType);

  @Lock(LockModeType.PESSIMISTIC_WRITE)
  @Query("SELECT s FROM TransactionTypeSequence s " +
         "WHERE s.companyId = :companyId AND s.idTransType = :idTransType")
  Optional<TransactionTypeSequence> lockForUpdate(
      @Param("companyId") Long companyId,
      @Param("idTransType") String idTransType);

  List<TransactionTypeSequence> findByCompanyId(Long companyId);
}
```

- [ ] **Step 5.3: Build**

Run: `./gradlew :module:transaction:compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 5.4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeRepository.java \
        module/transaction/src/main/java/of1/fms/module/transaction/repository/TransactionTypeSequenceRepository.java
git commit -m "feat(transaction): add TransactionType + Sequence repositories"
```

---

## Task 6: `DocumentNumberFormatter` util (TDD)

Pure function: template `{SIGN}{YY}{MM}{###}` + date + counter → string. Không đụng JPA, không đụng Spring — hoàn toàn test được bằng unit test.

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java`
- Test: `module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java`

- [ ] **Step 6.1: Write failing test — basic format**

```java
package of1.fms.module.transaction;

import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class DocumentNumberFormatterTest {

  @Test
  void format_basicTemplate_sign_yy_mm_seq3digit() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "HAEHAN", LocalDate.of(2026, 4, 8), 1);
    assertThat(result).isEqualTo("HAEHAN2604001");
  }

  @Test
  void format_fourDigitYear() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YYYY}{MM}{####}", "HSE", LocalDate.of(2026, 12, 31), 42);
    assertThat(result).isEqualTo("HSE2026120042");
  }

  @Test
  void format_nullTemplate_usesDefault() {
    String result = DocumentNumberFormatter.format(
        null, "HAEHAN", LocalDate.of(2026, 4, 8), 7);
    assertThat(result).isEqualTo("HAEHAN2604007");
  }

  @Test
  void format_nullSign_replacedWithEmpty() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", null, LocalDate.of(2026, 4, 8), 1);
    assertThat(result).isEqualTo("2604001");
  }

  @Test
  void format_largeSequence_exceedsPadding_noTruncation() {
    String result = DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "X", LocalDate.of(2026, 1, 1), 12345);
    assertThat(result).isEqualTo("X260112345");
  }

  @Test
  void format_negativeSequence_throws() {
    assertThatThrownBy(() -> DocumentNumberFormatter.format(
        "{SIGN}{YY}{MM}{###}", "X", LocalDate.of(2026, 1, 1), -1))
      .isInstanceOf(IllegalArgumentException.class);
  }
}
```

- [ ] **Step 6.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests DocumentNumberFormatterTest`
Expected: FAIL — `DocumentNumberFormatter` not found.

- [ ] **Step 6.3: Implement DocumentNumberFormatter**

```java
package of1.fms.module.transaction;

import java.time.LocalDate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class DocumentNumberFormatter {

  private static final String DEFAULT_TEMPLATE = "{SIGN}{YY}{MM}{###}";
  private static final Pattern HASH_TOKEN = Pattern.compile("\\{(#+)\\}");

  private DocumentNumberFormatter() {}

  public static String format(String template, String signPrefix, LocalDate date, int sequence) {
    if (sequence < 0) {
      throw new IllegalArgumentException("sequence must be >= 0, got " + sequence);
    }
    String tpl = (template == null || template.isBlank()) ? DEFAULT_TEMPLATE : template;
    String sign = signPrefix == null ? "" : signPrefix;

    String yy = String.format("%02d", date.getYear() % 100);
    String yyyy = String.format("%04d", date.getYear());
    String mm = String.format("%02d", date.getMonthValue());
    String dd = String.format("%02d", date.getDayOfMonth());

    String out = tpl
        .replace("{SIGN}", sign)
        .replace("{YYYY}", yyyy)
        .replace("{YY}", yy)
        .replace("{MM}", mm)
        .replace("{DD}", dd);

    // Replace {###..#} with zero-padded sequence
    Matcher m = HASH_TOKEN.matcher(out);
    StringBuilder sb = new StringBuilder();
    while (m.find()) {
      int width = m.group(1).length();
      String padded = String.format("%0" + width + "d", sequence);
      m.appendReplacement(sb, Matcher.quoteReplacement(padded));
    }
    m.appendTail(sb);
    return sb.toString();
  }
}
```

- [ ] **Step 6.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests DocumentNumberFormatterTest`
Expected: 6 tests pass.

- [ ] **Step 6.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/DocumentNumberFormatter.java \
        module/transaction/src/test/java/of1/fms/module/transaction/DocumentNumberFormatterTest.java
git commit -m "feat(transaction): add DocumentNumberFormatter with tests"
```

---

## Task 7: `TransactionTypeService` — read path + sync validator (TDD)

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java`
- Test: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java`

- [ ] **Step 7.1: Write failing test for getAll + get(enum) + validateEnumSync**

```java
package of1.fms.module.transaction;

import of1.fms.core.common.TypeOfService;
import of1.fms.module.transaction.entity.TransactionType;
import of1.fms.module.transaction.repository.TransactionTypeRepository;
import of1.fms.module.transaction.repository.TransactionTypeSequenceRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TransactionTypeServiceTest {

  @Mock TransactionTypeRepository typeRepo;
  @Mock TransactionTypeSequenceRepository seqRepo;

  private TransactionTypeService service;

  @BeforeEach
  void setUp() {
    service = new TransactionTypeService(typeRepo, seqRepo);
  }

  private TransactionType row(String id) {
    TransactionType t = new TransactionType();
    t.setIdTransType(id);
    t.setDescription(id);
    t.setTypeList("Test");
    return t;
  }

  @Test
  void get_returnsMetadataByEnum() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.reloadCache();
    TransactionType t = service.get(TypeOfService.AIR_EXPORT);
    assertThat(t).isNotNull();
    assertThat(t.getIdTransType()).isEqualTo("AIR_EXPORT");
  }

  @Test
  void getAll_returnsAllFromCache() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.reloadCache();
    assertThat(service.getAll()).hasSize(TypeOfService.values().length);
  }

  @Test
  void validateEnumSync_ok_whenDbMatchesEnum() {
    when(typeRepo.findAll()).thenReturn(allEnumRows());
    service.validateEnumSync();  // no exception
  }

  @Test
  void validateEnumSync_fails_whenDbMissingEnumValue() {
    List<TransactionType> rows = allEnumRows().stream()
        .filter(t -> !t.getIdTransType().equals("AIR_EXPORT"))
        .collect(Collectors.toList());
    when(typeRepo.findAll()).thenReturn(rows);
    assertThatThrownBy(() -> service.validateEnumSync())
      .isInstanceOf(IllegalStateException.class)
      .hasMessageContaining("AIR_EXPORT");
  }

  @Test
  void validateEnumSync_fails_whenDbHasExtraValue() {
    List<TransactionType> rows = new java.util.ArrayList<>(allEnumRows());
    rows.add(row("UNKNOWN_TYPE"));
    when(typeRepo.findAll()).thenReturn(rows);
    assertThatThrownBy(() -> service.validateEnumSync())
      .isInstanceOf(IllegalStateException.class)
      .hasMessageContaining("UNKNOWN_TYPE");
  }

  private List<TransactionType> allEnumRows() {
    return Arrays.stream(TypeOfService.values())
        .map(v -> row(v.name()))
        .collect(Collectors.toList());
  }
}
```

- [ ] **Step 7.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: FAIL — `TransactionTypeService` not found.

- [ ] **Step 7.3: Implement TransactionTypeService (read path + validator only)**

> Note: Write path `generateNextNumber` sẽ thêm ở Task 8 để giữ test nhỏ.

```java
package of1.fms.module.transaction;

import jakarta.annotation.PostConstruct;
import of1.fms.core.common.TypeOfService;
import of1.fms.module.transaction.entity.TransactionType;
import of1.fms.module.transaction.repository.TransactionTypeRepository;
import of1.fms.module.transaction.repository.TransactionTypeSequenceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class TransactionTypeService {

  private final TransactionTypeRepository typeRepo;
  private final TransactionTypeSequenceRepository seqRepo;
  private volatile Map<String, TransactionType> cache = Collections.emptyMap();

  @Autowired
  public TransactionTypeService(
      TransactionTypeRepository typeRepo,
      TransactionTypeSequenceRepository seqRepo) {
    this.typeRepo = typeRepo;
    this.seqRepo = seqRepo;
  }

  @PostConstruct
  public void init() {
    reloadCache();
    validateEnumSync();
  }

  public void reloadCache() {
    Map<String, TransactionType> map = new ConcurrentHashMap<>();
    for (TransactionType t : typeRepo.findAll()) {
      map.put(t.getIdTransType(), t);
    }
    this.cache = map;
  }

  public TransactionType get(TypeOfService type) {
    if (type == null) return null;
    return cache.get(type.name());
  }

  public List<TransactionType> getAll() {
    return List.copyOf(cache.values());
  }

  public void validateEnumSync() {
    Set<String> enumIds = Arrays.stream(TypeOfService.values())
        .map(Enum::name).collect(Collectors.toSet());
    Set<String> dbIds = typeRepo.findAll().stream()
        .map(TransactionType::getIdTransType).collect(Collectors.toSet());
    Set<String> missingInDb = new java.util.HashSet<>(enumIds);
    missingInDb.removeAll(dbIds);
    Set<String> extraInDb = new java.util.HashSet<>(dbIds);
    extraInDb.removeAll(enumIds);
    if (!missingInDb.isEmpty() || !extraInDb.isEmpty()) {
      throw new IllegalStateException(
        "TransactionType table out of sync with TypeOfService enum. " +
        "Missing in DB: " + missingInDb + ", extra in DB: " + extraInDb);
    }
  }
}
```

- [ ] **Step 7.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: 5 tests pass.

- [ ] **Step 7.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java \
        module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java
git commit -m "feat(transaction): add TransactionTypeService read path + sync validator"
```

---

## Task 8: `generateNextNumber` — write path với row-lock (TDD)

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java`
- Modify: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java`

- [ ] **Step 8.1: Add failing tests cho generateNextNumber**

Thêm vào `TransactionTypeServiceTest`:

```java
@Test
void generateNextNumber_existingSequence_incrementsAndFormats() {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(100L);
  seq.setIdTransType("AIR_EXPORT");
  seq.setSignPrefix("HAEHAN");
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(5);
  seq.setLastResetDate(LocalDate.now());

  when(seqRepo.lockForUpdate(100L, "AIR_EXPORT")).thenReturn(Optional.of(seq));
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.AIR_EXPORT, LocalDate.of(2026, 4, 8));

  assertThat(seq.getCurrentSequence()).isEqualTo(6);
  assertThat(result).isEqualTo("HAEHAN2604006");
}

@Test
void generateNextNumber_noExistingSequence_createsWithDefaults() {
  when(seqRepo.lockForUpdate(100L, "SEA_EXPORT_FCL")).thenReturn(Optional.empty());
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.SEA_EXPORT_FCL, LocalDate.of(2026, 4, 8));

  assertThat(result).endsWith("001");
  assertThat(result).contains("2604");
}

@Test
void generateNextNumber_resetPeriodElapsed_resetsCounter() {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(100L);
  seq.setIdTransType("AIR_EXPORT");
  seq.setSignPrefix("HAE");
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(999);
  seq.setLastResetDate(LocalDate.of(2025, 1, 1));  // > 365 days ago

  when(seqRepo.lockForUpdate(100L, "AIR_EXPORT")).thenReturn(Optional.of(seq));
  when(seqRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

  String result = service.generateNextNumber(100L, TypeOfService.AIR_EXPORT, LocalDate.of(2026, 4, 8));

  assertThat(seq.getCurrentSequence()).isEqualTo(1);
  assertThat(seq.getLastResetDate()).isEqualTo(LocalDate.of(2026, 4, 8));
  assertThat(result).isEqualTo("HAE2604001");
}
```

Thêm imports: `java.time.LocalDate`, `java.util.Optional`, `static org.mockito.ArgumentMatchers.any`, `of1.fms.module.transaction.entity.TransactionTypeSequence`.

- [ ] **Step 8.2: Run test — expect FAIL**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: FAIL — `generateNextNumber` not defined.

- [ ] **Step 8.3: Implement generateNextNumber**

Thêm method vào `TransactionTypeService`:

```java
@Transactional
public String generateNextNumber(Long companyId, TypeOfService type, LocalDate today) {
  if (companyId == null || type == null) {
    throw new IllegalArgumentException("companyId and type are required");
  }
  String idTransType = type.name();
  TransactionTypeSequence seq = seqRepo.lockForUpdate(companyId, idTransType)
      .orElseGet(() -> createDefaultSequence(companyId, idTransType));

  if (shouldReset(seq, today)) {
    seq.setCurrentSequence(0);
    seq.setLastResetDate(today);
  }

  seq.setCurrentSequence(seq.getCurrentSequence() + 1);
  seqRepo.save(seq);

  return DocumentNumberFormatter.format(
      seq.getNumberFormat(),
      seq.getSignPrefix(),
      today,
      seq.getCurrentSequence());
}

public String generateNextNumber(Long companyId, TypeOfService type) {
  return generateNextNumber(companyId, type, LocalDate.now());
}

private boolean shouldReset(TransactionTypeSequence seq, LocalDate today) {
  if (seq.getLastResetDate() == null) return false;
  int period = seq.getResetPeriodDays() == null ? 0 : seq.getResetPeriodDays();
  if (period <= 0) return false;
  return java.time.temporal.ChronoUnit.DAYS.between(seq.getLastResetDate(), today) >= period;
}

private TransactionTypeSequence createDefaultSequence(Long companyId, String idTransType) {
  TransactionTypeSequence seq = new TransactionTypeSequence();
  seq.setCompanyId(companyId);
  seq.setIdTransType(idTransType);
  seq.setSignPrefix(defaultSignPrefix(idTransType));
  seq.setNumberFormat("{SIGN}{YY}{MM}{###}");
  seq.setResetPeriodDays(365);
  seq.setCurrentSequence(0);
  seq.setLastResetDate(LocalDate.now());
  seq.setNoDaysLock(0);
  seq.setDayOfLogisticsLock(0);
  seq.setLockAgainAfterUnlock(0);
  return seq;
}

/** Fallback prefix khi company chưa config — derived từ MSSQL HPS seed (xem spec section 5.5). */
private String defaultSignPrefix(String idTransType) {
  return switch (idTransType) {
    case "AIR_EXPORT" -> "HAE";
    case "AIR_IMPORT" -> "HAI";
    case "SEA_EXPORT_FCL", "SEA_EXPORT_LCL", "SEA_EXPORT_CSL" -> "HSE";
    case "SEA_IMPORT_FCL", "SEA_IMPORT_LCL", "SEA_IMPORT_CSL" -> "HSI";
    case "CUSTOMS_LOGISTICS" -> "HLG";
    case "INLAND_TRUCKING"   -> "HTR";
    case "EXPRESS"           -> "HEX";
    case "PROJECT_LOGISTICS" -> "HPR";
    case "WAREHOUSE"         -> "HST";
    default -> "DOC";
  };
}
```

Thêm imports: `org.springframework.transaction.annotation.Transactional`, `java.time.LocalDate`, `of1.fms.module.transaction.entity.TransactionTypeSequence`.

- [ ] **Step 8.4: Run test — expect PASS**

Run: `./gradlew :module:transaction:test --tests TransactionTypeServiceTest`
Expected: 8 tests pass.

- [ ] **Step 8.5: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/TransactionTypeService.java \
        module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeServiceTest.java
git commit -m "feat(transaction): generateNextNumber with row-lock, reset, default fallback"
```

---

## Task 9: Concurrency integration test

**Files:**
- Create: `module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java`

> Chỉ triển khai nếu repo đã có setup Testcontainers Postgres. Nếu chưa, mark task này là **skipped** và ghi chú trong commit message; concurrency được verify manually trên dev DB bằng script thay thế.

- [ ] **Step 9.1: Check Testcontainers availability**

Run: `grep -rn "Testcontainers\|@Container\|PostgreSQLContainer" module/transaction/src/test/ module/core/src/test/ 2>/dev/null | head`

Nếu không có kết quả → **skip** task này, ghi note `docs/superpowers/plans/...` và chuyển sang Task 10.

- [ ] **Step 9.2 (if available): Write concurrency IT**

```java
package of1.fms.module.transaction;

import of1.fms.core.common.TypeOfService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.*;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class TransactionTypeGenerateConcurrencyIT {

  @Autowired TransactionTypeService service;

  @Test
  void concurrentGenerate_noDuplicates() throws Exception {
    int threads = 20;
    int callsPerThread = 10;
    long companyId = 999_001L;
    TypeOfService type = TypeOfService.AIR_EXPORT;

    ExecutorService pool = Executors.newFixedThreadPool(threads);
    List<Future<String>> futures = new ArrayList<>();
    for (int i = 0; i < threads * callsPerThread; i++) {
      futures.add(pool.submit(() -> service.generateNextNumber(companyId, type)));
    }
    pool.shutdown();
    pool.awaitTermination(60, TimeUnit.SECONDS);

    List<String> all = new ArrayList<>();
    for (Future<String> f : futures) all.add(f.get());
    Set<String> unique = all.stream().collect(Collectors.toSet());

    assertThat(all).hasSize(threads * callsPerThread);
    assertThat(unique).hasSize(threads * callsPerThread);  // no duplicates
  }
}
```

- [ ] **Step 9.3: Run IT**

Run: `./gradlew :module:transaction:integrationTest --tests TransactionTypeGenerateConcurrencyIT` (hoặc tên task tương đương trong repo)
Expected: PASS — không có số trùng.

- [ ] **Step 9.4: Commit**

```bash
git add module/transaction/src/test/java/of1/fms/module/transaction/TransactionTypeGenerateConcurrencyIT.java
git commit -m "test(transaction): concurrent generateNextNumber no duplicates"
```

---

## Task 10: Full build + final verification

- [ ] **Step 10.1: Clean build toàn repo**

Run: `./gradlew clean build -x test` (nếu test chạy chậm) hoặc `./gradlew clean build`
Expected: BUILD SUCCESSFUL.

- [ ] **Step 10.2: Run toàn bộ test module transaction**

Run: `./gradlew :module:transaction:test`
Expected: all green.

- [ ] **Step 10.3: Apply migration lên DB dev rồi khởi động ứng dụng**

Run: Start FMS backend như workflow thường.
Expected: Application start OK. Log có `TransactionTypeService.init()` không throw, `validateEnumSync` passes.

- [ ] **Step 10.4: Smoke query DB**

```sql
SELECT id_trans_type, description, type_list, legacy_mssql_code
FROM of1_fms_transaction_type
ORDER BY id_trans_type;
```
Expected: 15 rows.

```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'of1_fms_transaction_type_sequence' ORDER BY ordinal_position;
```
Expected: 17 columns khớp schema ở Task 2.

- [ ] **Step 10.5: Final commit (chỉ nếu có changes từ fix nhỏ)**

```bash
git status
# nếu sạch, không commit. Nếu có fix, commit với message mô tả.
```

---

## Out of scope (không làm trong plan này — sẽ có plan riêng)

- MSSQL import flow (spec section 5.7) — chờ quyết định trigger (Kafka event vs admin endpoint vs CLI) và mapping `tenantCode → companyId`.
- UI admin quản lý `transaction_type` / `transaction_type_sequence`.
- Refactor `Transaction.typeOfService` column sang FK.
- Áp dụng `no_days_lock` / `day_of_logistics_lock` vào logic lock transaction hiện tại.

## Rollback

Nếu cần revert:
- Xoá changesets `fms:22`, `fms:23`, `fms:24` khỏi file SQL (hoặc dùng `liquibase rollbackCount 3`).
- Xoá entity / repository / service files.
- Revert enum change trong `TypeOfService.java`.
- Application sẽ fail startup validator nếu còn bảng nhưng thiếu enum value tương ứng — phải rollback đồng thời cả hai.
