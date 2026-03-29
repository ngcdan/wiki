# BFSOne Sync Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port and complete the BFSOne MSSQL→Kafka→PostgreSQL sync pipeline — fix existing bugs, create missing components, rename BfsOne→BFSOne, and add ExchangeRate + SettingUnit sync domains.

**Architecture:** MSSQL (BFS One legacy) queried by `*SyncLogic` classes via JDBC, events published to Kafka topics, `*SyncEventConsumer` listeners save to PostgreSQL. All new code lives in `module/transaction` under `of1.fms.module.partner`. `BFSOneSyncService` is the orchestrator, delegating to per-domain Logic classes.

**Tech Stack:** Java 21, Spring Boot 3.x, Spring Kafka, Spring Data JPA, Hibernate, Lombok, MSSQL JDBC 12.8.1, PostgreSQL

**Spec:** `docs/superpowers/specs/2026-03-28-bfsone-sync-pipeline-design.md`

**Python Reference:** `/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python/bee_legacy`

**Build command:** `./gradlew :of1-fms-module-transaction:compileJava` (run after each task to verify)

> **Note:** No test infrastructure exists in this module. Verification = successful compilation + code review against Python reference.

---

## File Map

### Files to rename (Part C)
| From | To |
|---|---|
| `bfsone/BfsOneDataConfig.java` | `bfsone/BFSOneDataConfig.java` |
| `bfsone/BfsOneSyncLogic.java` | `bfsone/TransactionSyncLogic.java` |
| `bfsone/BfsOneSyncService.java` | `bfsone/BFSOneSyncService.java` |

### Event files to move into sub-packages
| From | To |
|---|---|
| `event/TransactionSyncEvent.java` | `event/transaction/TransactionSyncEvent.java` |
| `event/TransactionSyncEventProducer.java` | `event/transaction/TransactionSyncEventProducer.java` |
| `event/TransactionSyncEventConsumer.java` | `event/transaction/TransactionSyncEventConsumer.java` |
| `event/HousebillSyncEvent.java` | `event/transaction/HousebillSyncEvent.java` |
| `event/HousebillSyncEventProducer.java` | `event/transaction/HousebillSyncEventProducer.java` |
| `event/HousebillSyncEventConsumer.java` | `event/transaction/HousebillSyncEventConsumer.java` |
| `event/HawbProfitSyncEvent.java` | `event/transaction/HawbProfitSyncEvent.java` |
| `event/HawbProfitSyncEventProducer.java` | `event/transaction/HawbProfitSyncEventProducer.java` |
| `event/TransactionQueueConfig.java` | stays at `event/TransactionQueueConfig.java` |

### Files to create (Part A + Part B)
- `event/transaction/HawbProfitSyncEventConsumer.java` (Part A — missing)
- `event/exchangerate/ExchangeRateSyncEvent.java`
- `event/exchangerate/ExchangeRateSyncEventProducer.java`
- `event/exchangerate/ExchangeRateSyncEventConsumer.java`
- `event/settingunit/SettingUnitSyncEvent.java`
- `event/settingunit/SettingUnitSyncEventProducer.java`
- `event/settingunit/SettingUnitSyncEventConsumer.java`
- `bfsone/ExchangeRateSyncLogic.java`
- `bfsone/SettingUnitSyncLogic.java`
- `PYTHON_DEVLOG.md` (root of `of1-fms`)
- `PYTHON_CLAUDE.md` (root of `of1-fms`)

### Files to modify
- `bfsone/TransactionSyncLogic.java` — fix ETD/ETA alias inversion
- `repository/IntegratedHawbProfitRepository.java` — fix `deleteByTransactionIds` bug
- `bfsone/BFSOneSyncService.java` — add `syncExchangeRates` + `syncSettingUnits` methods; update autowired fields
- `event/TransactionQueueConfig.java` — register 5 new beans; update imports
- `module/settings/.../repository/ExchangeRateRepository.java` — add `findLatestByEffectiveDateOnOrBefore`
- `module/transaction/build.gradle` — add `api project(":of1-fms-module-settings")`

**Base path shorthand used in this plan:**
- `$TX` = `module/transaction/src/main/java/of1/fms/module/partner`
- `$ST` = `module/settings/src/main/java/of1/fms/settings`

---

## Task 1: Rename BfsOne → BFSOne + Move event files to sub-packages

> Do this as one isolated commit before any bug fixes or new code.

**Files:**
- Delete+recreate: all files in rename table above
- Modify: all callers of renamed classes

- [ ] **Step 1.1: Rename `BfsOneDataConfig` → `BFSOneDataConfig`**

Delete `$TX/bfsone/BfsOneDataConfig.java`, create `$TX/bfsone/BFSOneDataConfig.java`.
**Keep existing logic exactly** — only rename the class. Use `DataSourceBuilder` pattern to match the existing codebase:
```java
package of1.fms.module.partner.bfsone;

import com.zaxxer.hikari.HikariDataSource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;

@Configuration
@Slf4j
public class BFSOneDataConfig {

  public static final String DS_BEAN = "bfsOneDataSource";
  public static final String JDBC_TEMPLATE = "bfsOneJdbcTemplate";

  @Bean(DS_BEAN)
  @ConfigurationProperties("spring.datasource.bfsone")
  DataSource bfsOneDataSource() {
    log.info("Creating BFS One MSSQL DataSource");
    return DataSourceBuilder.create().type(HikariDataSource.class).build();
  }

  @Bean(JDBC_TEMPLATE)
  JdbcTemplate bfsOneJdbcTemplate(@Qualifier(DS_BEAN) DataSource ds) {
    log.info("Creating BFS One JdbcTemplate");
    return new JdbcTemplate(ds);
  }
}
```

- [ ] **Step 1.2: Rename `BfsOneSyncLogic` → `TransactionSyncLogic`**

Delete `$TX/bfsone/BfsOneSyncLogic.java`, create `$TX/bfsone/TransactionSyncLogic.java` with:
- Package: `of1.fms.module.partner.bfsone`
- Class name: `TransactionSyncLogic`
- All content identical to `BfsOneSyncLogic` — only change class name and the `@Qualifier(BfsOneDataConfig.JDBC_TEMPLATE)` reference to `@Qualifier(BFSOneDataConfig.JDBC_TEMPLATE)`
- Import: `of1.fms.module.partner.event.transaction.*` (after events are moved)

- [ ] **Step 1.3: Rename `BfsOneSyncService` → `BFSOneSyncService`**

Delete `$TX/bfsone/BfsOneSyncService.java`, create `$TX/bfsone/BFSOneSyncService.java`:
- Package: `of1.fms.module.partner.bfsone`
- Class name: `BFSOneSyncService`
- Annotation: `@Service("BFSOneSyncService")`
- Field `private BfsOneSyncLogic syncLogic` → `private TransactionSyncLogic syncLogic`
- Import: `of1.fms.module.partner.event.transaction.*`
- All method bodies identical to existing `BfsOneSyncService`

- [ ] **Step 1.4: Move transaction event files to `event/transaction/` sub-package**

For each file in the list below, delete from `event/` and recreate in `event/transaction/` with updated package declaration `package of1.fms.module.partner.event.transaction;`:
- `TransactionSyncEvent.java`
- `TransactionSyncEventProducer.java`
- `TransactionSyncEventConsumer.java`
- `HousebillSyncEvent.java`
- `HousebillSyncEventProducer.java`
- `HousebillSyncEventConsumer.java`
- `HawbProfitSyncEvent.java`
- `HawbProfitSyncEventProducer.java`

- [ ] **Step 1.5: Update `TransactionQueueConfig.java` imports**

`$TX/event/TransactionQueueConfig.java` — update imports to use new sub-package:
```java
package of1.fms.module.partner.event;

import datatp.data.kafka.KafkaConfig;
import of1.fms.module.partner.event.transaction.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

@Configuration
@Import(value = {KafkaConfig.class})
public class TransactionQueueConfig {

  @Bean("TransactionSyncEventProducer")
  TransactionSyncEventProducer createTransactionSyncEventProducer() {
    return new TransactionSyncEventProducer();
  }

  @Bean("HousebillSyncEventProducer")
  HousebillSyncEventProducer createHousebillSyncEventProducer() {
    return new HousebillSyncEventProducer();
  }

  @Bean("HawbProfitSyncEventProducer")
  HawbProfitSyncEventProducer createHawbProfitSyncEventProducer() {
    return new HawbProfitSyncEventProducer();
  }

  @Bean("TransactionSyncEventConsumer")
  TransactionSyncEventConsumer createTransactionSyncEventConsumer() {
    return new TransactionSyncEventConsumer();
  }

  @Bean("HousebillSyncEventConsumer")
  HousebillSyncEventConsumer createHousebillSyncEventConsumer() {
    return new HousebillSyncEventConsumer();
  }
}
```

- [ ] **Step 1.6: Verify build compiles**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```
Expected: `BUILD SUCCESSFUL`

- [ ] **Step 1.7: Commit**
```bash
git add module/transaction/
git commit -m "refactor(transaction): rename BfsOne to BFSOne, move event classes to sub-packages"
```

---

## Task 2: Fix ETD/ETA alias inversion bug in `TransactionSyncLogic`

**Files:**
- Modify: `$TX/bfsone/TransactionSyncLogic.java`

- [ ] **Step 2.1: Fix `TRANSACTION_QUERY` — replace CASE swap with direct aliases**

In `TransactionSyncLogic.java`, find `TRANSACTION_QUERY`. Replace the CASE block:
```sql
-- REMOVE this (lines ~36-43):
CASE
  WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate
  ELSE t.LoadingDate
END                 AS etd,
CASE
  WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate
  ELSE t.ArrivalDate
END                 AS eta,

-- REPLACE with:
t.LoadingDate       AS etd,
t.ArrivalDate       AS eta,
```

- [ ] **Step 2.2: Fix `HOUSEBILL_QUERY` — same fix**

In `TransactionSyncLogic.java`, find `HOUSEBILL_QUERY`. Replace the same CASE block (lines ~101-108) with:
```sql
t.LoadingDate       AS etd,
t.ArrivalDate       AS eta,
```

- [ ] **Step 2.3: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 2.4: Verify logic correctness against Python reference**

Open `/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python/bee_legacy/service/hawb/integrated_transaction_service.py`.
Check the SQL query — `LoadingDate` should map to `etd`, `ArrivalDate` to `eta` without any CASE swap.
Confirm `computeReportDate` for Import uses `eta` (ArrivalDate) first.

- [ ] **Step 2.5: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/bfsone/TransactionSyncLogic.java
git commit -m "fix(transaction): correct ETD/ETA column alias inversion in BFSOne SQL queries"
```

---

## Task 3: Fix `IntegratedHawbProfitRepository.deleteByTransactionIds` bug

**Files:**
- Modify: `$TX/repository/IntegratedHawbProfitRepository.java`

- [ ] **Step 3.1: Fix the repository method**

`$TX/repository/IntegratedHawbProfitRepository.java` — replace wrong method:
```java
// REMOVE:
@Modifying
@Query("DELETE IntegratedHawbProfit ihp WHERE ihp.id IN :ids")
void deleteByTransactionIds(@Param("ids") List<Long> ids);

// ADD:
@Modifying
@Query("DELETE FROM IntegratedHawbProfit ihp WHERE ihp.transactionId IN :transactionIds")
void deleteByTransactionIds(@Param("transactionIds") List<String> transactionIds);
```

- [ ] **Step 3.2: Fix the Logic class signature to match**

`$TX/IntegratedHawbProfitLogic.java` — the existing `deleteByTransactionIds` takes `List<Long>` which is now wrong. Replace:
```java
// REMOVE:
public void deleteByTransactionIds(ClientContext ctx, List<Long> ids) {
  integratedHawbProfitRepo.deleteByTransactionIds(ids);
}

// ADD:
public void deleteByTransactionId(ClientContext ctx, String transactionId) {
  if (transactionId == null) return;
  integratedHawbProfitRepo.deleteByTransactionIds(List.of(transactionId));
}
```

- [ ] **Step 3.3: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 3.4: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/repository/IntegratedHawbProfitRepository.java \
        module/transaction/src/main/java/of1/fms/module/partner/IntegratedHawbProfitLogic.java
git commit -m "fix(transaction): correct deleteByTransactionIds query field and param type"
```

---

## Task 4: Create `HawbProfitSyncEventConsumer` (missing component)

**Files:**
- Create: `$TX/event/transaction/HawbProfitSyncEventConsumer.java`
- Modify: `$TX/event/TransactionQueueConfig.java`

- [ ] **Step 4.1: Create `HawbProfitSyncEventConsumer.java`**

```java
package of1.fms.module.partner.event.transaction;

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.security.client.ClientContext;
import net.datatp.util.dataformat.DataSerializer;
import of1.fms.module.partner.IntegratedHawbProfitLogic;
import of1.fms.module.partner.entity.IntegratedHawbProfit;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;

import java.util.List;

@Slf4j
public class HawbProfitSyncEventConsumer {

  @Value("${datatp.msa.fms.queue.topic.hawb-profit-sync:bee-legacy.hawb-profit.sync}")
  private String topicEvents;

  @Autowired
  private IntegratedHawbProfitLogic hawbProfitLogic;

  @PostConstruct
  public void onInit() {
    log.info("HawbProfitSyncEventConsumer initialized for topic: {}", topicEvents);
  }

  @KafkaListener(
    id = "msa.HawbProfitSyncEventConsumer",
    topics = "${datatp.msa.fms.queue.topic.hawb-profit-sync:bee-legacy.hawb-profit.sync}",
    groupId = "fms-hawb-profit-consumer-group",
    autoStartup = "${datatp.msa.fms.queue.event-consumer-enable:false}",
    concurrency = "1"
  )
  public void onEvent(ConsumerRecord<String, String> consumerRecord) {
    try {
      String json = consumerRecord.value();
      KafkaMessage message = DataSerializer.JSON.fromString(json, KafkaMessage.class);
      HawbProfitSyncEvent event = message.getDataAs(HawbProfitSyncEvent.class);
      ClientContext ctx = message.getClientContext();

      // Delete existing records for this transaction before inserting new ones
      hawbProfitLogic.deleteByTransactionId(ctx, event.getTransactionId());

      IntegratedHawbProfit profit = new IntegratedHawbProfit();
      profit.setTransactionId(event.getTransactionId());
      profit.setHawbNo(event.getHawbNo());
      profit.setReportDate(event.getReportDate());
      profit.setCustomerCode(event.getCustomerCode());
      profit.setAgentCode(event.getAgentCode());
      profit.setSalemanContactId(event.getSalemanContactId());
      profit.setCompanyBranchCode(event.getCompanyBranchCode());
      profit.setSubtotalSellingVND(event.getSubtotalSellingVND());
      profit.setTotalSellingVND(event.getTotalSellingVND());
      profit.setSubtotalBuyingVND(event.getSubtotalBuyingVND());
      profit.setTotalBuyingVND(event.getTotalBuyingVND());
      profit.setSubtotalOtherDebitVND(event.getSubtotalOtherDebitVND());
      profit.setTotalOtherDebitVND(event.getTotalOtherDebitVND());
      profit.setSubtotalOtherCreditVND(event.getSubtotalOtherCreditVND());
      profit.setTotalOtherCreditVND(event.getTotalOtherCreditVND());
      profit.setExchangeRateUSD(event.getExchangeRateUSD());

      hawbProfitLogic.saveIntegratedHawbProfit(ctx, profit);
      log.info("Saved hawb profit: {} for transaction: {}", event.getHawbNo(), event.getTransactionId());
    } catch (Exception e) {
      log.error("Error processing hawb profit sync event: topic={}, partition={}, offset={}, error={}",
        consumerRecord.topic(), consumerRecord.partition(), consumerRecord.offset(), e.getMessage(), e);
    }
  }
}
```

- [ ] **Step 4.2: Verify `deleteByTransactionId` method exists in `IntegratedHawbProfitLogic`**

This method was added in Task 3 Step 3.2. Confirm it is present in `$TX/IntegratedHawbProfitLogic.java`:
```java
public void deleteByTransactionId(ClientContext ctx, String transactionId) {
  if (transactionId == null) return;
  integratedHawbProfitRepo.deleteByTransactionIds(List.of(transactionId));
}
```
If missing, add it now (should have been done in Task 3).

- [ ] **Step 4.3: Register bean in `TransactionQueueConfig`**

Add to `$TX/event/TransactionQueueConfig.java`:
```java
@Bean("HawbProfitSyncEventConsumer")
HawbProfitSyncEventConsumer createHawbProfitSyncEventConsumer() {
  return new HawbProfitSyncEventConsumer();
}
```
Note: `HawbProfitSyncEventConsumer` is already covered by the wildcard import `of1.fms.module.partner.event.transaction.*` added in Step 1.5 — no additional import needed.

- [ ] **Step 4.4: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 4.5: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/
git commit -m "feat(transaction): add missing HawbProfitSyncEventConsumer"
```

---

## Task 5: Add build dependency + ExchangeRateRepository method

**Files:**
- Modify: `module/transaction/build.gradle`
- Modify: `$ST/currency/repository/ExchangeRateRepository.java`

- [ ] **Step 5.1: Add settings module dependency**

In `module/transaction/build.gradle`, add after `api project(":of1-fms-module-common")`:
```groovy
api project(":of1-fms-module-settings")
```

- [ ] **Step 5.2: Add `findLatestByEffectiveDateOnOrBefore` to `ExchangeRateRepository`**

Open `$ST/currency/repository/ExchangeRateRepository.java`. Add:
```java
import org.springframework.data.domain.Pageable;
// ...

// Name uses "OnOrBefore" to signal inclusive <= semantics
// (Spring Data "Before" would generate strict < )
@Query("SELECT er FROM ExchangeRate er WHERE er.effectiveDate <= :date ORDER BY er.effectiveDate DESC")
List<ExchangeRate> findLatestByEffectiveDateOnOrBefore(@Param("date") Date date, Pageable pageable);
```
Add import: `import java.util.Date;` if not present.

- [ ] **Step 5.3: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava :of1-fms-module-settings:compileJava
```

- [ ] **Step 5.4: Commit**
```bash
git add module/transaction/build.gradle module/settings/src/main/java/of1/fms/settings/currency/repository/ExchangeRateRepository.java
git commit -m "feat(transaction): add settings module dependency and ExchangeRate date lookup method"
```

---

## Task 6: ExchangeRate sync — Logic + Event + Producer + Consumer

**Files:**
- Create: `$TX/bfsone/ExchangeRateSyncLogic.java`
- Create: `$TX/event/exchangerate/ExchangeRateSyncEvent.java`
- Create: `$TX/event/exchangerate/ExchangeRateSyncEventProducer.java`
- Create: `$TX/event/exchangerate/ExchangeRateSyncEventConsumer.java`

- [ ] **Step 6.1: Create `ExchangeRateSyncEvent.java`**

```java
package of1.fms.module.partner.event.exchangerate;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExchangeRateSyncEvent {
  private String code;
  private Double exchangeRateUSD;
  private Date effectiveDate;
  private Date effectiveTo;
}
```

- [ ] **Step 6.2: Create `ExchangeRateSyncLogic.java`**

```java
package of1.fms.module.partner.bfsone;

import lombok.extern.slf4j.Slf4j;
import net.datatp.module.service.BaseComponent;
import of1.fms.module.partner.event.exchangerate.ExchangeRateSyncEvent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.sql.ResultSet;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

@Component
@Slf4j
public class ExchangeRateSyncLogic extends BaseComponent {

  @Autowired
  @Qualifier(BFSOneDataConfig.JDBC_TEMPLATE)
  private JdbcTemplate bfsOneJdbc;

  private static final String EXCHANGE_RATE_QUERY = """
    SELECT ID, ExtVNDSales
    FROM CurrencyExchangeRate
    WHERE Unit = 'USD' AND ID LIKE 'HCMGIANGNTH_%'
    ORDER BY ID
    """;

  public List<ExchangeRateSyncEvent> queryExchangeRates() {
    List<ExchangeRateSyncEvent> rows = bfsOneJdbc.query(
      EXCHANGE_RATE_QUERY, (rs, rowNum) -> mapRow(rs)
    );

    // Compute effectiveTo: each record's effectiveTo = next record's effectiveDate
    for (int i = 0; i < rows.size() - 1; i++) {
      rows.get(i).setEffectiveTo(rows.get(i + 1).getEffectiveDate());
    }
    // Last record has no effectiveTo
    if (!rows.isEmpty()) {
      rows.get(rows.size() - 1).setEffectiveTo(null);
    }

    return rows;
  }

  private ExchangeRateSyncEvent mapRow(ResultSet rs) throws java.sql.SQLException {
    ExchangeRateSyncEvent event = new ExchangeRateSyncEvent();
    String code = rs.getString("ID");
    event.setCode(code);
    event.setExchangeRateUSD(rs.getDouble("ExtVNDSales"));
    event.setEffectiveDate(parseEffectiveDateFromCode(code));
    return event;
  }

  /**
   * Parse date from code suffix.
   * Example: "HCMGIANGNTH_JAN012025" -> 2025-01-01
   */
  private Date parseEffectiveDateFromCode(String code) {
    if (code == null) return null;
    int underscoreIdx = code.lastIndexOf('_');
    if (underscoreIdx < 0 || underscoreIdx >= code.length() - 1) return null;
    String datePart = code.substring(underscoreIdx + 1); // e.g. "JAN012025"
    try {
      SimpleDateFormat sdf = new SimpleDateFormat("MMMddyyyy", Locale.ENGLISH);
      return sdf.parse(datePart);
    } catch (ParseException e) {
      log.warn("Cannot parse date from exchange rate code '{}': {}", code, e.getMessage());
      return null;
    }
  }
}
```

- [ ] **Step 6.3: Create `ExchangeRateSyncEventProducer.java`**

```java
package of1.fms.module.partner.event.exchangerate;

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.security.client.ClientContext;
import net.datatp.util.dataformat.DataSerializer;
import net.datatp.util.error.ErrorType;
import net.datatp.util.error.RuntimeError;
import net.datatp.util.text.StringUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;

@Slf4j
public class ExchangeRateSyncEventProducer {

  @Autowired
  private KafkaTemplate<String, String> kafkaTemplate;

  @Value("${datatp.msa.fms.queue.event-producer-enable:false}")
  private boolean enable;

  @Value("${datatp.msa.fms.queue.topic.exchange-rate-sync:bee-legacy.exchange-rate.sync}")
  private String topicEvents;

  @PostConstruct
  public void onInit() {
    log.info("ExchangeRateSyncEventProducer config: enable={}, topic={}", enable, topicEvents);
    if (enable && StringUtil.isEmpty(topicEvents)) {
      throw RuntimeError.IllegalArgument("Topic exchange-rate-sync is empty.");
    }
  }

  public void send(ClientContext ctx, ExchangeRateSyncEvent event) {
    if (!enable) return;
    try {
      KafkaMessage message = new KafkaMessage(ctx, event);
      String json = DataSerializer.JSON.toString(message);
      kafkaTemplate.send(topicEvents, json).whenComplete((result, ex) -> {
        if (ex != null) {
          log.error("Failed to send exchange rate sync event to {}: {}", topicEvents, ex.getMessage(), ex);
        }
      });
    } catch (Exception e) {
      log.error("Error sending exchange rate sync event: {}", e.getMessage(), e);
      throw new RuntimeError(ErrorType.IllegalState, "Failed to send exchange rate sync event", e);
    }
  }
}
```

- [ ] **Step 6.4: Create `ExchangeRateSyncEventConsumer.java`**

```java
package of1.fms.module.partner.event.exchangerate;

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.util.dataformat.DataSerializer;
import of1.fms.settings.currency.entity.ExchangeRate;
import of1.fms.settings.currency.repository.ExchangeRateRepository;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;

import java.util.Date;
import java.util.List;

@Slf4j
public class ExchangeRateSyncEventConsumer {

  @Value("${datatp.msa.fms.queue.topic.exchange-rate-sync:bee-legacy.exchange-rate.sync}")
  private String topicEvents;

  @Autowired
  private ExchangeRateRepository exchangeRateRepo;

  @PostConstruct
  public void onInit() {
    log.info("ExchangeRateSyncEventConsumer initialized for topic: {}", topicEvents);
  }

  @KafkaListener(
    id = "msa.ExchangeRateSyncEventConsumer",
    topics = "${datatp.msa.fms.queue.topic.exchange-rate-sync:bee-legacy.exchange-rate.sync}",
    groupId = "fms-exchange-rate-consumer-group",
    autoStartup = "${datatp.msa.fms.queue.event-consumer-enable:false}",
    concurrency = "1"
  )
  public void onEvent(ConsumerRecord<String, String> consumerRecord) {
    try {
      String json = consumerRecord.value();
      KafkaMessage message = DataSerializer.JSON.fromString(json, KafkaMessage.class);
      ExchangeRateSyncEvent event = message.getDataAs(ExchangeRateSyncEvent.class);

      // Two-step upsert: find existing by code, delete by id, insert new
      ExchangeRate existing = exchangeRateRepo.getByCode(event.getCode());
      if (existing != null) {
        exchangeRateRepo.deleteByIds(List.of(existing.getId()));
      }

      ExchangeRate rate = new ExchangeRate();
      rate.setCode(event.getCode());
      rate.setExchangeRateUSD(event.getExchangeRateUSD());
      rate.setEffectiveDate(event.getEffectiveDate());
      rate.setEffectiveTo(event.getEffectiveTo());
      rate.setSyncedToKafka(new Date());  // set by consumer, not from event

      exchangeRateRepo.save(rate);
      log.info("Saved exchange rate: {}", event.getCode());
    } catch (Exception e) {
      log.error("Error processing exchange rate sync event: topic={}, partition={}, offset={}, error={}",
        consumerRecord.topic(), consumerRecord.partition(), consumerRecord.offset(), e.getMessage(), e);
    }
  }
}
```

- [ ] **Step 6.5: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 6.6: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/bfsone/ExchangeRateSyncLogic.java \
        module/transaction/src/main/java/of1/fms/module/partner/event/exchangerate/
git commit -m "feat(transaction): add ExchangeRate BFSOne sync logic, event, producer, consumer"
```

---

## Task 7: SettingUnit sync — Logic + Event + Producer + Consumer

**Files:**
- Create: `$TX/bfsone/SettingUnitSyncLogic.java`
- Create: `$TX/event/settingunit/SettingUnitSyncEvent.java`
- Create: `$TX/event/settingunit/SettingUnitSyncEventProducer.java`
- Create: `$TX/event/settingunit/SettingUnitSyncEventConsumer.java`

- [ ] **Step 7.1: Create `SettingUnitSyncEvent.java`**

```java
package of1.fms.module.partner.event.settingunit;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SettingUnitSyncEvent {
  private String unitCode;
  private String unitName;           // maps to SettingUnit.label
  private String unitLocalizedName;  // maps to SettingUnit.localizedDescription
  private String isoCode;            // maps to SettingUnit.isoCode
  private String description;
  private String groupName;          // resolved to SettingUnit.groupId via SettingUnitGroup
}
```

- [ ] **Step 7.2: Create `SettingUnitSyncLogic.java`**

```java
package of1.fms.module.partner.bfsone;

import lombok.extern.slf4j.Slf4j;
import net.datatp.module.service.BaseComponent;
import of1.fms.module.partner.event.settingunit.SettingUnitSyncEvent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.sql.ResultSet;
import java.util.List;

@Component
@Slf4j
public class SettingUnitSyncLogic extends BaseComponent {

  @Autowired
  @Qualifier(BFSOneDataConfig.JDBC_TEMPLATE)
  private JdbcTemplate bfsOneJdbc;

  // IsActive is skipped — no corresponding field in SettingUnit entity
  private static final String SETTING_UNIT_QUERY = """
    SELECT UnitCode, UnitName, LocalizedName, ISOCode, Description, GroupName
    FROM UnitContents
    """;

  public List<SettingUnitSyncEvent> querySettingUnits() {
    return bfsOneJdbc.query(SETTING_UNIT_QUERY, (rs, rowNum) -> mapRow(rs));
  }

  private SettingUnitSyncEvent mapRow(ResultSet rs) throws java.sql.SQLException {
    SettingUnitSyncEvent event = new SettingUnitSyncEvent();
    event.setUnitCode(rs.getString("UnitCode"));
    event.setUnitName(rs.getString("UnitName"));
    event.setUnitLocalizedName(rs.getString("LocalizedName"));
    event.setIsoCode(rs.getString("ISOCode"));
    event.setDescription(rs.getString("Description"));
    event.setGroupName(rs.getString("GroupName"));
    return event;
  }
}
```

- [ ] **Step 7.3: Create `SettingUnitSyncEventProducer.java`**

```java
package of1.fms.module.partner.event.settingunit;

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.security.client.ClientContext;
import net.datatp.util.dataformat.DataSerializer;
import net.datatp.util.error.ErrorType;
import net.datatp.util.error.RuntimeError;
import net.datatp.util.text.StringUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;

@Slf4j
public class SettingUnitSyncEventProducer {

  @Autowired
  private KafkaTemplate<String, String> kafkaTemplate;

  @Value("${datatp.msa.fms.queue.event-producer-enable:false}")
  private boolean enable;

  @Value("${datatp.msa.fms.queue.topic.setting-unit-sync:bee-legacy.setting-unit.sync}")
  private String topicEvents;

  @PostConstruct
  public void onInit() {
    log.info("SettingUnitSyncEventProducer config: enable={}, topic={}", enable, topicEvents);
    if (enable && StringUtil.isEmpty(topicEvents)) {
      throw RuntimeError.IllegalArgument("Topic setting-unit-sync is empty.");
    }
  }

  public void send(ClientContext ctx, SettingUnitSyncEvent event) {
    if (!enable) return;
    try {
      KafkaMessage message = new KafkaMessage(ctx, event);
      String json = DataSerializer.JSON.toString(message);
      kafkaTemplate.send(topicEvents, json).whenComplete((result, ex) -> {
        if (ex != null) {
          log.error("Failed to send setting unit sync event to {}: {}", topicEvents, ex.getMessage(), ex);
        }
      });
    } catch (Exception e) {
      log.error("Error sending setting unit sync event: {}", e.getMessage(), e);
      throw new RuntimeError(ErrorType.IllegalState, "Failed to send setting unit sync event", e);
    }
  }
}
```

- [ ] **Step 7.4: Create `SettingUnitSyncEventConsumer.java`**

```java
package of1.fms.module.partner.event.settingunit;

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.util.dataformat.DataSerializer;
import of1.fms.settings.unit.entity.SettingUnit;
import of1.fms.settings.unit.entity.SettingUnitGroup;
import of1.fms.settings.unit.repository.SettingUnitGroupRepository;
import of1.fms.settings.unit.repository.SettingUnitRepository;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;

@Slf4j
public class SettingUnitSyncEventConsumer {

  @Value("${datatp.msa.fms.queue.topic.setting-unit-sync:bee-legacy.setting-unit.sync}")
  private String topicEvents;

  @Autowired
  private SettingUnitRepository settingUnitRepo;

  @Autowired
  private SettingUnitGroupRepository settingUnitGroupRepo;

  @PostConstruct
  public void onInit() {
    log.info("SettingUnitSyncEventConsumer initialized for topic: {}", topicEvents);
  }

  @KafkaListener(
    id = "msa.SettingUnitSyncEventConsumer",
    topics = "${datatp.msa.fms.queue.topic.setting-unit-sync:bee-legacy.setting-unit.sync}",
    groupId = "fms-setting-unit-consumer-group",
    autoStartup = "${datatp.msa.fms.queue.event-consumer-enable:false}",
    concurrency = "1"
  )
  public void onEvent(ConsumerRecord<String, String> consumerRecord) {
    try {
      String json = consumerRecord.value();
      KafkaMessage message = DataSerializer.JSON.fromString(json, KafkaMessage.class);
      SettingUnitSyncEvent event = message.getDataAs(SettingUnitSyncEvent.class);

      Long groupId = resolveGroupId(event.getGroupName());

      // Update in-place to avoid cascade delete on SettingUnit.aliases
      SettingUnit unit = settingUnitRepo.getByCode(event.getUnitCode());
      if (unit == null) {
        unit = new SettingUnit();
        unit.setCode(event.getUnitCode());
      }
      unit.setLabel(event.getUnitName());
      unit.setLocalizedDescription(event.getUnitLocalizedName());
      unit.setIsoCode(event.getIsoCode());
      unit.setDescription(event.getDescription());
      unit.setGroupId(groupId);

      settingUnitRepo.save(unit);
      log.info("Saved setting unit: {}", event.getUnitCode());
    } catch (Exception e) {
      log.error("Error processing setting unit sync event: topic={}, partition={}, offset={}, error={}",
        consumerRecord.topic(), consumerRecord.partition(), consumerRecord.offset(), e.getMessage(), e);
    }
  }

  /**
   * Find SettingUnitGroup by code (exact match). Create if not found.
   */
  private Long resolveGroupId(String groupName) {
    if (groupName == null || groupName.isBlank()) {
      groupName = "UNKNOWN";
    }
    SettingUnitGroup group = settingUnitGroupRepo.getByCode(groupName);
    if (group == null) {
      group = new SettingUnitGroup();
      group.setCode(groupName);
      group.setLabel(groupName);
      group = settingUnitGroupRepo.save(group);
      log.info("Created new SettingUnitGroup: {}", groupName);
    }
    return group.getId();
  }
}
```

- [ ] **Step 7.5: Verify `SettingUnitRepository.getByCode` exists**

Open `$ST/unit/repository/SettingUnitRepository.java`. Confirm `getByCode(String code)` is already present (verified during spec review — no action needed unless missing).

- [ ] **Step 7.6: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 7.7: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/bfsone/SettingUnitSyncLogic.java \
        module/transaction/src/main/java/of1/fms/module/partner/event/settingunit/ \
        module/settings/src/main/java/of1/fms/settings/unit/repository/SettingUnitRepository.java
git commit -m "feat(transaction): add SettingUnit BFSOne sync logic, event, producer, consumer"
```

---

## Task 8: Update `BFSOneSyncService` with new sync methods

**Files:**
- Modify: `$TX/bfsone/BFSOneSyncService.java`

- [ ] **Step 8.1: Add autowired fields, new sync methods, and ExchangeRate lookup in `syncHawbProfits`**

**8.1a — Add autowired fields** to `BFSOneSyncService.java`:
```java
@Autowired
private ExchangeRateSyncLogic exchangeRateSyncLogic;

@Autowired
private SettingUnitSyncLogic settingUnitSyncLogic;

@Autowired
private ExchangeRateSyncEventProducer exchangeRateProducer;

@Autowired
private SettingUnitSyncEventProducer settingUnitProducer;

@Autowired
private ExchangeRateRepository exchangeRateRepo;  // for exchange rate lookup in syncHawbProfits
```

**8.1b — Fix `syncHawbProfits` to inject `exchangeRateUSD`** (spec requirement — currently missing).
In the existing `syncHawbProfits` loop, before calling `profitProducer.send`, add the exchange rate lookup:
```java
// Inside the for loop, after setting profit.setCompanyBranchCode(...):
if (hb.getReportDate() != null) {
  List<ExchangeRate> rates = exchangeRateRepo.findLatestByEffectiveDateOnOrBefore(
    hb.getReportDate(), PageRequest.of(0, 1));
  if (!rates.isEmpty()) {
    profit.setExchangeRateUSD(rates.get(0).getExchangeRateUSD());
  }
}
```

Add import: `import org.springframework.data.domain.PageRequest;`
Add import: `import of1.fms.settings.currency.entity.ExchangeRate;`
Add import: `import of1.fms.settings.currency.repository.ExchangeRateRepository;`

**8.1c — Add new sync methods:**
```java
/**
 * Sync all USD exchange rates from BFS One MSSQL to Kafka.
 */
public int syncExchangeRates(ClientContext ctx) {
  List<ExchangeRateSyncEvent> rates = exchangeRateSyncLogic.queryExchangeRates();
  for (ExchangeRateSyncEvent event : rates) {
    exchangeRateProducer.send(ctx, event);
  }
  log.info("Exchange rate sync completed: total={}", rates.size());
  return rates.size();
}

/**
 * Sync all unit contents from BFS One MSSQL to Kafka.
 */
public int syncSettingUnits(ClientContext ctx) {
  List<SettingUnitSyncEvent> units = settingUnitSyncLogic.querySettingUnits();
  for (SettingUnitSyncEvent event : units) {
    settingUnitProducer.send(ctx, event);
  }
  log.info("Setting unit sync completed: total={}", units.size());
  return units.size();
}
```

Add imports:
```java
import of1.fms.module.partner.event.exchangerate.ExchangeRateSyncEvent;
import of1.fms.module.partner.event.exchangerate.ExchangeRateSyncEventProducer;
import of1.fms.module.partner.event.settingunit.SettingUnitSyncEvent;
import of1.fms.module.partner.event.settingunit.SettingUnitSyncEventProducer;
```

- [ ] **Step 8.2: Verify build**
```bash
./gradlew :of1-fms-module-transaction:compileJava
```

- [ ] **Step 8.3: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/bfsone/BFSOneSyncService.java
git commit -m "feat(transaction): add syncExchangeRates and syncSettingUnits to BFSOneSyncService"
```

---

## Task 9: Register new beans in `TransactionQueueConfig`

**Files:**
- Modify: `$TX/event/TransactionQueueConfig.java`

- [ ] **Step 9.1: Add all new producer + consumer beans**

Full updated `TransactionQueueConfig.java`:
```java
package of1.fms.module.partner.event;

import datatp.data.kafka.KafkaConfig;
import of1.fms.module.partner.event.exchangerate.ExchangeRateSyncEventConsumer;
import of1.fms.module.partner.event.exchangerate.ExchangeRateSyncEventProducer;
import of1.fms.module.partner.event.settingunit.SettingUnitSyncEventConsumer;
import of1.fms.module.partner.event.settingunit.SettingUnitSyncEventProducer;
import of1.fms.module.partner.event.transaction.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

@Configuration
@Import(value = {KafkaConfig.class})
public class TransactionQueueConfig {

  @Bean("TransactionSyncEventProducer")
  TransactionSyncEventProducer createTransactionSyncEventProducer() {
    return new TransactionSyncEventProducer();
  }

  @Bean("HousebillSyncEventProducer")
  HousebillSyncEventProducer createHousebillSyncEventProducer() {
    return new HousebillSyncEventProducer();
  }

  @Bean("HawbProfitSyncEventProducer")
  HawbProfitSyncEventProducer createHawbProfitSyncEventProducer() {
    return new HawbProfitSyncEventProducer();
  }

  @Bean("TransactionSyncEventConsumer")
  TransactionSyncEventConsumer createTransactionSyncEventConsumer() {
    return new TransactionSyncEventConsumer();
  }

  @Bean("HousebillSyncEventConsumer")
  HousebillSyncEventConsumer createHousebillSyncEventConsumer() {
    return new HousebillSyncEventConsumer();
  }

  @Bean("HawbProfitSyncEventConsumer")
  HawbProfitSyncEventConsumer createHawbProfitSyncEventConsumer() {
    return new HawbProfitSyncEventConsumer();
  }

  @Bean("ExchangeRateSyncEventProducer")
  ExchangeRateSyncEventProducer createExchangeRateSyncEventProducer() {
    return new ExchangeRateSyncEventProducer();
  }

  @Bean("ExchangeRateSyncEventConsumer")
  ExchangeRateSyncEventConsumer createExchangeRateSyncEventConsumer() {
    return new ExchangeRateSyncEventConsumer();
  }

  @Bean("SettingUnitSyncEventProducer")
  SettingUnitSyncEventProducer createSettingUnitSyncEventProducer() {
    return new SettingUnitSyncEventProducer();
  }

  @Bean("SettingUnitSyncEventConsumer")
  SettingUnitSyncEventConsumer createSettingUnitSyncEventConsumer() {
    return new SettingUnitSyncEventConsumer();
  }
}
```

- [ ] **Step 9.2: Final build verification**
```bash
./gradlew :of1-fms-module-transaction:compileJava :of1-fms-module-settings:compileJava
```
Expected: `BUILD SUCCESSFUL` with no warnings about unresolved symbols.

- [ ] **Step 9.3: Commit**
```bash
git add module/transaction/src/main/java/of1/fms/module/partner/event/TransactionQueueConfig.java
git commit -m "feat(transaction): register all new Kafka producer/consumer beans in TransactionQueueConfig"
```

---

## Task 10: Create `PYTHON_DEVLOG.md` and `PYTHON_CLAUDE.md`

**Files:**
- Create: `PYTHON_DEVLOG.md` (root of `of1-fms`)
- Create: `PYTHON_CLAUDE.md` (root of `of1-fms`)

- [ ] **Step 10.1: Create `PYTHON_DEVLOG.md`**

```markdown
# Python Port — Development Log

Tracks progress of porting bee_legacy Python sync pipeline to Java.
Python reference: `/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python/bee_legacy`

## Status

| Domain | Logic | Event | Producer | Consumer | Bug Fixes | Status |
|---|---|---|---|---|---|---|
| Transaction | TransactionSyncLogic | TransactionSyncEvent | ✓ | ✓ | ETD/ETA fix | Done |
| Housebill | TransactionSyncLogic | HousebillSyncEvent | ✓ | ✓ | - | Done |
| HawbProfit | TransactionSyncLogic | HawbProfitSyncEvent | ✓ | ✓ (new) | deleteByTransactionIds fix | Done |
| ExchangeRate | ExchangeRateSyncLogic | ExchangeRateSyncEvent | ✓ (new) | ✓ (new) | - | Done |
| SettingUnit | SettingUnitSyncLogic | SettingUnitSyncEvent | ✓ (new) | ✓ (new) | - | Done |

## Java vs Python Differences

- **ETD/ETA alias:** Python maps `LoadingDate→etd`, `ArrivalDate→eta` directly. Java had incorrect CASE swap for Import — fixed.
- **deleteByTransactionIds:** Java had wrong JPQL query (used `id` instead of `transactionId`) — fixed.
- **ExchangeRate effectiveTo:** Python computes in-memory by iterating sorted results — Java does the same.
- **SettingUnit groupId:** Python stores `group_name` as String. Java resolves `group_name → SettingUnitGroup.id` via repo lookup/create.
- **syncedToKafka:** Python tracks this on producer side to skip re-syncing. Java sets on consumer side at insert time only.
- **HawbProfit trigger:** Python triggers from Kafka consumer. Java is service-orchestrated: `syncHousebills` caller must then call `syncHawbProfits`.
```

- [ ] **Step 10.2: Create `PYTHON_CLAUDE.md`**

```markdown
# Python Port — AI Instructions

## Python Reference Path
`/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python/bee_legacy`

## Python → Java Class Mapping

| Python file | Java class | Location |
|---|---|---|
| `service/hawb/integrated_transaction_service.py` | `TransactionSyncLogic` | `module/transaction/.../bfsone/` |
| `service/hawb/integrated_hawb_profit_service.py` | `TransactionSyncLogic.queryProfitData()` | same |
| `service/exchange_rate_service.py` | `ExchangeRateSyncLogic` | same |
| `service/settings_unit_service.py` | `SettingUnitSyncLogic` | same |
| `db/bfsone_config.py` | `BFSOneDataConfig` | same |
| `db/engine.py` | `FmsDataModuleConfig` | `module/core/` |

## Special Logic Notes

1. **chunking:** Python uses 5000-row chunks with OFFSET/FETCH. Java uses same approach in `BFSOneSyncService.syncTransactions()`.
2. **batch publish:** Python sends 50 records per Kafka batch. Java does same in `syncTransactions()`.
3. **report_date:** `LoadingDate` = ETD, `ArrivalDate` = ETA. Import uses ETA first, Export uses ETD first.
4. **company_branch_code:** Skip first 2 chars of transactionId, take letters until first digit. `"HCVND0012025"` → `"VND"`.
5. **SettingUnit groupId:** Must resolve `groupName` string → `SettingUnitGroup.id`. Create group if not exists.
6. **ExchangeRate date parsing:** Code suffix `"JAN012025"` → parse with `SimpleDateFormat("MMMddyyyy", Locale.ENGLISH)`.

## Architecture Rules
- All BFS One sync code lives in `module/transaction` under `of1.fms.module.partner`
- `BFSOneSyncService` is the only entry point for triggering syncs
- Kafka consumers in `event/transaction/`, `event/exchangerate/`, `event/settingunit/`
- Entity classes for ExchangeRate + SettingUnit live in `module/settings` — consumers access them via cross-module dependency
```

- [ ] **Step 10.3: Commit**
```bash
git add PYTHON_DEVLOG.md PYTHON_CLAUDE.md
git commit -m "docs: add PYTHON_DEVLOG and PYTHON_CLAUDE for BFSOne port reference"
```
