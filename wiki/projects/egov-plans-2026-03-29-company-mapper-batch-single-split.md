---
title: "Plan — Company Mapper Batch/Single Split"
tags: [egov, plans, mapper, refactor]
created: 2026-03-29
---

# Company Mapper Batch/Single Split — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate ~3600 lines of duplicated batch boilerplate from 22 company mapper classes by extracting a shared `BatchSyncOrchestrator` + `BatchSyncAdapterService`, leaving each mapper with only its unique single-record logic.

**Architecture:** Mappers implement `EcusBatchSyncProvider<E>` (returns a `BatchSyncDescriptor`) instead of `IEcusCompanyEntityMapper`. `BatchSyncOrchestrator` owns all paging/async/threading/context/aggregation logic. `BatchSyncAdapterService` auto-discovers providers and routes calls. `EcusMappingService` switches its company-entity method to use `BatchSyncAdapterService`.

**Tech Stack:** Java 21, Spring Boot 3.3.3, Lombok (`@Getter @Builder`), JUnit 5, Mockito, `@Tag("unit")`

**Spec:** `docs/superpowers/specs/2026-03-29-company-mapper-batch-single-split-design.md`

---

## File Map

### New files
| File | Responsibility |
|---|---|
| `sync/RecordProcessor.java` | Functional interface: `process(companyId, record, syncSourceConfigId)` |
| `sync/BatchSyncDescriptor.java` | Data object: config + optional hooks per sync job |
| `logic/EcusBatchSyncProvider.java` | Interface: `descriptor()` — replaces `IEcusCompanyEntityMapper` for company mappers |
| `sync/BatchSyncOrchestrator.java` | All batch logic: paging, async, context propagation, result aggregation |
| `sync/BatchSyncAdapterService.java` | Auto-discovers providers, routes `syncAll()` / `syncByName()` / `sync()` |
| `test/.../sync/BatchSyncOrchestratorUnitTest.java` | Unit tests for `processBatch()` |
| `test/.../sync/BatchSyncAdapterServiceUnitTest.java` | Unit tests for routing methods |

### Modified files
| File | Change |
|---|---|
| `service/EcusMappingService.java` | Switch `syncCompanyEntities()` + `syncIndividualCompanyEntity()` to use `BatchSyncAdapterService` |
| `logic/mapper/company/Ecus*Mapper.java` (22 files) | Remove `syncEntity()`, `processBatch()`, `@Value` fields, `SyncExecutor` injection; add `descriptor()` method; make `processSync()` private |
| `test/.../CompanyEntitiesIntegrationTest.java` | Update `processSync()` calls → `descriptor().getRecordProcessor().process(...)` |

### Unchanged files
| File | Reason |
|---|---|
| `logic/IEcusCompanyEntityMapper.java` | Left for core/partner mappers (out of scope) |
| `controller/SyncController.java` | Concrete mapper beans still injectable; satisfy `EcusBatchSyncProvider<?>` |
| `sync/SyncExecutor.java` | Called by `BatchSyncOrchestrator.processBatch()` unchanged |

---

## Base paths (use as prefix for all file paths below)

```
src/main  → module/ecus-thaison/src/main/java/com/egov/ecusthaison
src/test  → module/ecus-thaison/src/test/java/com/egov/ecusthaison
```

---

## Task 1: Foundation types

**Files:**
- Create: `src/main/sync/RecordProcessor.java`
- Create: `src/main/sync/BatchSyncDescriptor.java`
- Create: `src/main/logic/EcusBatchSyncProvider.java`

No tests needed — these are plain data objects and a functional interface.

- [ ] **Step 1: Create `RecordProcessor.java`**

```java
package com.egov.ecusthaison.sync;

@FunctionalInterface
public interface RecordProcessor<E> {
    void process(Long companyId, E record, Long syncSourceConfigId);
}
```

- [ ] **Step 2: Create `BatchSyncDescriptor.java`**

```java
package com.egov.ecusthaison.sync;

import lombok.Builder;
import lombok.Getter;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.function.BiConsumer;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.UnaryOperator;

@Getter
@Builder
public class BatchSyncDescriptor<E> {

    // Required
    private final String syncName;
    private final JpaRepository<E, ?> repository;
    private final Function<E, String> idExtractor;
    private final Function<E, String> descExtractor;
    private final RecordProcessor<E> recordProcessor;

    // Optional batch config overrides — null means use app-level @Value default
    private final Integer importLimit;
    private final Integer batchSize;
    private final Integer threadPoolSize;

    // Optional hooks — null means skip; exceptions inside hooks are logged and swallowed
    private final BiConsumer<Integer, SyncResult> onBatchComplete;  // (pageNumber, batchResult)
    private final Consumer<SyncResult> onSyncComplete;              // called after all pages
    private final UnaryOperator<SyncResult> resultEnricher;         // enriches final SyncResult
}
```

- [ ] **Step 3: Create `EcusBatchSyncProvider.java`**

```java
package com.egov.ecusthaison.logic;

import com.egov.ecusthaison.sync.BatchSyncDescriptor;

public interface EcusBatchSyncProvider<E> {
    BatchSyncDescriptor<E> descriptor();
}
```

- [ ] **Step 4: Compile to verify**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/RecordProcessor.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/BatchSyncDescriptor.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/EcusBatchSyncProvider.java
git commit -m "feat(ecus-thaison): add RecordProcessor, BatchSyncDescriptor, EcusBatchSyncProvider foundation types"
```

---

## Task 2: `BatchSyncOrchestrator`

**Files:**
- Create: `src/main/sync/BatchSyncOrchestrator.java`
- Create: `src/test/sync/BatchSyncOrchestratorUnitTest.java`

- [ ] **Step 1: Write the failing unit test**

```java
package com.egov.ecusthaison.sync;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class BatchSyncOrchestratorUnitTest {

    @Mock private SyncExecutor syncExecutor;
    @InjectMocks private BatchSyncOrchestrator orchestrator;

    @BeforeEach
    void setUp() {
        // Inject @Value defaults directly (no Spring context in unit tests)
        ReflectionTestUtils.setField(orchestrator, "defaultImportLimit", 1000);
        ReflectionTestUtils.setField(orchestrator, "defaultBatchSize", 100);
        ReflectionTestUtils.setField(orchestrator, "defaultThreadPoolSize", 2);
    }

    @Test
    void processBatchShouldReturnEmptyResultWhenPageIsEmpty() {
        JpaRepository<String, Long> repo = mock(JpaRepository.class);
        when(repo.findAll(any(Pageable.class))).thenReturn(new PageImpl<>(List.of()));

        BatchSyncDescriptor<String> descriptor = BatchSyncDescriptor.<String>builder()
            .syncName("TEST")
            .repository(repo)
            .idExtractor(s -> s)
            .descExtractor(s -> s)
            .recordProcessor((companyId, r, configId) -> {})
            .build();

        SyncResult result = orchestrator.processBatch(descriptor, 1L, 0, 42L);

        assertThat(result.getTotalRecords()).isEqualTo(0);
        verifyNoInteractions(syncExecutor);
    }

    @Test
    void processBatchShouldCallSyncExecutorWhenRecordsPresent() {
        JpaRepository<String, Long> repo = mock(JpaRepository.class);
        when(repo.findAll(any(Pageable.class))).thenReturn(new PageImpl<>(List.of("A", "B")));

        SyncResult fakeResult = SyncResult.builder()
            .syncName("TEST_Page_0").totalRecords(2).successCount(2).failedCount(0).skippedCount(0)
            .build();
        when(syncExecutor.executeWithTracking(any(), any(), any(), any(), any())).thenReturn(fakeResult);

        BatchSyncDescriptor<String> descriptor = BatchSyncDescriptor.<String>builder()
            .syncName("TEST")
            .repository(repo)
            .idExtractor(s -> s)
            .descExtractor(s -> "desc-" + s)
            .recordProcessor((companyId, r, configId) -> {})
            .build();

        SyncResult result = orchestrator.processBatch(descriptor, 1L, 0, 42L);

        verify(syncExecutor).executeWithTracking(eq("TEST_Page_0"), eq(List.of("A", "B")), any(), any(), any());
        assertThat(result.getSuccessCount()).isEqualTo(2);
    }

    @Test
    void processBatchShouldInvokeOnBatchCompleteHookWhenPresent() {
        JpaRepository<String, Long> repo = mock(JpaRepository.class);
        when(repo.findAll(any(Pageable.class))).thenReturn(new PageImpl<>(List.of("X")));

        SyncResult fakeResult = SyncResult.builder()
            .syncName("TEST_Page_0").totalRecords(1).successCount(1).failedCount(0).skippedCount(0)
            .build();
        when(syncExecutor.executeWithTracking(any(), any(), any(), any(), any())).thenReturn(fakeResult);

        int[] hookCallCount = {0};
        BatchSyncDescriptor<String> descriptor = BatchSyncDescriptor.<String>builder()
            .syncName("TEST")
            .repository(repo)
            .idExtractor(s -> s)
            .descExtractor(s -> s)
            .recordProcessor((companyId, r, configId) -> {})
            .onBatchComplete((page, result) -> hookCallCount[0]++)
            .build();

        orchestrator.processBatch(descriptor, 1L, 0, 42L);

        assertThat(hookCallCount[0]).isEqualTo(1);
    }

    @Test
    void processBatchShouldContinueWhenHookThrows() {
        JpaRepository<String, Long> repo = mock(JpaRepository.class);
        when(repo.findAll(any(Pageable.class))).thenReturn(new PageImpl<>(List.of("X")));

        SyncResult fakeResult = SyncResult.builder()
            .syncName("TEST_Page_0").totalRecords(1).successCount(1).failedCount(0).skippedCount(0)
            .build();
        when(syncExecutor.executeWithTracking(any(), any(), any(), any(), any())).thenReturn(fakeResult);

        BatchSyncDescriptor<String> descriptor = BatchSyncDescriptor.<String>builder()
            .syncName("TEST")
            .repository(repo)
            .idExtractor(s -> s)
            .descExtractor(s -> s)
            .recordProcessor((companyId, r, configId) -> {})
            .onBatchComplete((page, result) -> { throw new RuntimeException("hook error"); })
            .build();

        // Should not throw — hook exception is swallowed
        SyncResult result = orchestrator.processBatch(descriptor, 1L, 0, 42L);
        assertThat(result.getSuccessCount()).isEqualTo(1);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.sync.BatchSyncOrchestratorUnitTest"
```

Expected: FAIL — `BatchSyncOrchestrator` does not exist yet

- [ ] **Step 3: Create `BatchSyncOrchestrator.java`**

```java
package com.egov.ecusthaison.sync;

import com.egov.ecusthaison.context.EcusTenantContext;
import com.egov.ecusthaison.util.ApplicationContextProvider;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Service
@Slf4j
public class BatchSyncOrchestrator {

    @Value("${ecus.import.company.limit:1000}")
    private int defaultImportLimit;

    @Value("${ecus.import.company.batch-size:1000}")
    private int defaultBatchSize;

    @Value("${ecus.import.company.thread-pool-size:5}")
    private int defaultThreadPoolSize;

    @Autowired
    private SyncExecutor syncExecutor;

    public <E> SyncResult run(BatchSyncDescriptor<E> descriptor) {
        int effectiveImportLimit = descriptor.getImportLimit() != null ? descriptor.getImportLimit() : defaultImportLimit;
        int effectiveBatchSize = descriptor.getBatchSize() != null ? descriptor.getBatchSize() : defaultBatchSize;
        int effectiveThreadPoolSize = descriptor.getThreadPoolSize() != null ? descriptor.getThreadPoolSize() : defaultThreadPoolSize;
        String syncName = descriptor.getSyncName();

        log.info("Starting {} sync — batchSize: {}, threadPoolSize: {}", syncName, effectiveBatchSize, effectiveThreadPoolSize);

        Long companyId = EcusTenantContext.getCompanyId();
        if (companyId == null) {
            throw new RuntimeException(
                "CompanyId not set in EcusTenantContext. Call via /{ecusDbName}/company-entities endpoint.");
        }

        long totalCount = descriptor.getRepository().count();
        log.debug("{}: total records = {}", syncName, totalCount);

        if (totalCount == 0) {
            return SyncResult.emptyBuilder(syncName).build();
        }

        int totalPages = (int) Math.ceil((double) Math.min(totalCount, effectiveImportLimit) / effectiveBatchSize);
        log.debug("{}: processing {} pages", syncName, totalPages);

        final String ecusDbName = EcusTenantContext.getEcusDbName();
        final Long capturedCompanyId = companyId;
        final Long capturedSyncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
        final int batchSizeForThreads = effectiveBatchSize;

        ExecutorService executorService = Executors.newFixedThreadPool(effectiveThreadPoolSize);
        List<CompletableFuture<SyncResult>> futures = new ArrayList<>();
        LocalDateTime startTime = LocalDateTime.now();

        try {
            for (int page = 0; page < totalPages; page++) {
                final int currentPage = page;
                CompletableFuture<SyncResult> future = CompletableFuture.supplyAsync(() -> {
                    EcusTenantContext.set(ecusDbName, capturedCompanyId, capturedSyncSourceConfigId);
                    try {
                        BatchSyncOrchestrator self = ApplicationContextProvider.getBean(BatchSyncOrchestrator.class);
                        return self.processBatch(descriptor, capturedCompanyId, currentPage, capturedSyncSourceConfigId);
                    } finally {
                        EcusTenantContext.clear();
                    }
                }, executorService);
                futures.add(future);
            }

            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

            int totalSuccess = 0, totalFailed = 0, totalSkipped = 0, totalProcessed = 0;
            SyncResult.SyncResultBuilder finalBuilder = SyncResult.builder()
                .syncName(syncName)
                .startTime(startTime)
                .endTime(LocalDateTime.now());

            for (CompletableFuture<SyncResult> f : futures) {
                SyncResult r = f.get();
                totalProcessed += r.getTotalRecords();
                totalSuccess += r.getSuccessCount();
                totalFailed += r.getFailedCount();
                totalSkipped += r.getSkippedCount();
                if (r.getErrors() != null) {
                    for (SyncResult.SyncError err : r.getErrors()) {
                        finalBuilder.addError(err.getRecordId(), err.getRecordDescription(), err.getException());
                    }
                }
            }

            log.info("{} sync done — total: {}, success: {}, failed: {}, skipped: {}",
                syncName, totalProcessed, totalSuccess, totalFailed, totalSkipped);

            SyncResult finalResult = finalBuilder
                .totalRecords(totalProcessed)
                .successCount(totalSuccess)
                .failedCount(totalFailed)
                .skippedCount(totalSkipped)
                .build();

            if (descriptor.getResultEnricher() != null) {
                try {
                    finalResult = descriptor.getResultEnricher().apply(finalResult);
                } catch (Exception e) {
                    log.error("{}: resultEnricher hook threw — ignoring: {}", syncName, e.getMessage());
                }
            }

            if (descriptor.getOnSyncComplete() != null) {
                try {
                    descriptor.getOnSyncComplete().accept(finalResult);
                } catch (Exception e) {
                    log.error("{}: onSyncComplete hook threw — ignoring: {}", syncName, e.getMessage());
                }
            }

            return finalResult;

        } catch (Exception e) {
            log.error("{}: critical error — {}", syncName, e.getMessage(), e);
            return SyncResult.emptyBuilder(syncName)
                .startTime(startTime)
                .addError("GLOBAL", syncName + " Sync", e)
                .build();
        } finally {
            executorService.shutdown();
        }
    }

    @Transactional(propagation = Propagation.REQUIRED)
    public <E> SyncResult processBatch(BatchSyncDescriptor<E> descriptor, Long companyId, int pageNumber, Long syncSourceConfigId) {
        String syncName = descriptor.getSyncName();
        int batchSize = descriptor.getBatchSize() != null ? descriptor.getBatchSize() : defaultBatchSize;

        try {
            Pageable pageable = PageRequest.of(pageNumber, batchSize);
            Page<E> page = (Page<E>) descriptor.getRepository().findAll(pageable);
            List<E> records = page.getContent();

            if (records.isEmpty()) {
                return SyncResult.emptyBuilder(syncName + "_Page_" + pageNumber).build();
            }

            SyncResult result = syncExecutor.executeWithTracking(
                syncName + "_Page_" + pageNumber,
                records,
                descriptor.getIdExtractor(),
                descriptor.getDescExtractor(),
                (record, context) -> descriptor.getRecordProcessor().process(companyId, record, syncSourceConfigId));

            log.info("{} page {} done — success: {}, failed: {}",
                syncName, pageNumber + 1, result.getSuccessCount(), result.getFailedCount());

            if (descriptor.getOnBatchComplete() != null) {
                try {
                    descriptor.getOnBatchComplete().accept(pageNumber, result);
                } catch (Exception e) {
                    log.error("{}: onBatchComplete hook threw on page {} — ignoring: {}", syncName, pageNumber, e.getMessage());
                }
            }

            return result;

        } catch (Exception e) {
            log.error("{}: error on page {} — {}", syncName, pageNumber, e.getMessage(), e);
            return SyncResult.emptyBuilder(syncName + "_Page_" + pageNumber)
                .addError("Page_" + pageNumber, "Batch processing", e)
                .build();
        }
    }
}
```

- [ ] **Step 4: Run tests**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.sync.BatchSyncOrchestratorUnitTest"
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/BatchSyncOrchestrator.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/BatchSyncOrchestratorUnitTest.java
git commit -m "feat(ecus-thaison): add BatchSyncOrchestrator with unit tests"
```

---

## Task 3: `BatchSyncAdapterService`

**Files:**
- Create: `src/main/sync/BatchSyncAdapterService.java`
- Create: `src/test/sync/BatchSyncAdapterServiceUnitTest.java`

- [ ] **Step 1: Write the failing unit test**

```java
package com.egov.ecusthaison.sync;

import com.egov.ecusthaison.logic.EcusBatchSyncProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class BatchSyncAdapterServiceUnitTest {

    @Mock private BatchSyncOrchestrator orchestrator;
    @InjectMocks private BatchSyncAdapterService service;

    private EcusBatchSyncProvider<String> providerAlpha;
    private EcusBatchSyncProvider<String> providerBeta;
    private BatchSyncDescriptor<String> descriptorAlpha;
    private BatchSyncDescriptor<String> descriptorBeta;

    @BeforeEach
    @SuppressWarnings("unchecked")
    void setUp() {
        descriptorAlpha = BatchSyncDescriptor.<String>builder()
            .syncName("ALPHA").repository(mock(org.springframework.data.jpa.repository.JpaRepository.class))
            .idExtractor(s -> s).descExtractor(s -> s).recordProcessor((a, b, c) -> {}).build();
        descriptorBeta = BatchSyncDescriptor.<String>builder()
            .syncName("BETA").repository(mock(org.springframework.data.jpa.repository.JpaRepository.class))
            .idExtractor(s -> s).descExtractor(s -> s).recordProcessor((a, b, c) -> {}).build();

        providerAlpha = () -> descriptorAlpha;
        providerBeta = () -> descriptorBeta;

        ReflectionTestUtils.setField(service, "providers", List.of(providerAlpha, providerBeta));
    }

    @Test
    void syncAllShouldRunAllProviders() {
        SyncResult r1 = SyncResult.emptyBuilder("ALPHA").build();
        SyncResult r2 = SyncResult.emptyBuilder("BETA").build();
        when(orchestrator.run(descriptorAlpha)).thenReturn(r1);
        when(orchestrator.run(descriptorBeta)).thenReturn(r2);

        List<SyncResult> results = service.syncAll();

        assertThat(results).hasSize(2);
        verify(orchestrator).run(descriptorAlpha);
        verify(orchestrator).run(descriptorBeta);
    }

    @Test
    void syncByNameShouldRunMatchingProvider() {
        SyncResult r = SyncResult.emptyBuilder("ALPHA").build();
        when(orchestrator.run(descriptorAlpha)).thenReturn(r);

        SyncResult result = service.syncByName("ALPHA");

        assertThat(result).isSameAs(r);
        verify(orchestrator).run(descriptorAlpha);
        verify(orchestrator, never()).run(descriptorBeta);
    }

    @Test
    void syncByNameShouldThrowWhenNameNotFound() {
        assertThatThrownBy(() -> service.syncByName("UNKNOWN"))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("UNKNOWN");
    }

    @Test
    void syncShouldRunSingleProvider() {
        SyncResult r = SyncResult.emptyBuilder("BETA").build();
        when(orchestrator.run(descriptorBeta)).thenReturn(r);

        SyncResult result = service.sync(providerBeta);

        assertThat(result).isSameAs(r);
        verify(orchestrator).run(descriptorBeta);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.sync.BatchSyncAdapterServiceUnitTest"
```

Expected: FAIL — `BatchSyncAdapterService` does not exist yet

- [ ] **Step 3: Create `BatchSyncAdapterService.java`**

```java
package com.egov.ecusthaison.sync;

import com.egov.ecusthaison.logic.EcusBatchSyncProvider;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@Slf4j
public class BatchSyncAdapterService {

    @Autowired
    private List<EcusBatchSyncProvider<?>> providers;

    @Autowired
    private BatchSyncOrchestrator orchestrator;

    @PostConstruct
    void logDiscoveredProviders() {
        log.info("BatchSyncAdapterService: discovered {} company sync providers:", providers.size());
        providers.forEach(p -> log.info("  - {}", p.descriptor().getSyncName()));
    }

    public List<SyncResult> syncAll() {
        return providers.stream()
            .map(p -> orchestrator.run(p.descriptor()))
            .toList();
    }

    public SyncResult syncByName(String syncName) {
        return providers.stream()
            .filter(p -> syncName.equals(p.descriptor().getSyncName()))
            .findFirst()
            .map(p -> orchestrator.run(p.descriptor()))
            .orElseThrow(() -> new IllegalArgumentException(
                "No EcusBatchSyncProvider found with syncName: " + syncName));
    }

    public SyncResult sync(EcusBatchSyncProvider<?> provider) {
        return orchestrator.run(provider.descriptor());
    }
}
```

- [ ] **Step 4: Run tests**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.sync.BatchSyncAdapterServiceUnitTest"
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/BatchSyncAdapterService.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/BatchSyncAdapterServiceUnitTest.java
git commit -m "feat(ecus-thaison): add BatchSyncAdapterService with unit tests"
```

---

## Task 4: Update `EcusMappingService` — signature preparation

Update `syncIndividualCompanyEntity()` signature NOW, before any mapper is refactored. This lets `SyncController` keep compiling as mappers are refactored one by one in subsequent tasks.

**Files:**
- Modify: `src/main/service/EcusMappingService.java`

- [ ] **Step 1: Update `EcusMappingService`**

In `EcusMappingService.java`:

1. Add import: `import com.egov.ecusthaison.logic.EcusBatchSyncProvider;`
2. Add import: `import com.egov.ecusthaison.sync.BatchSyncAdapterService;`
3. Add field: `@Autowired private BatchSyncAdapterService batchSyncAdapterService;`
4. Change `syncCompanyEntities()`:
   ```java
   public List<SyncResult> syncCompanyEntities() {
       return batchSyncAdapterService.syncAll();
   }
   ```
5. Change `syncIndividualCompanyEntity()` signature and body:
   ```java
   public SyncResult syncIndividualCompanyEntity(EcusBatchSyncProvider<?> provider) {
       return batchSyncAdapterService.sync(provider);
   }
   ```
6. Remove: `@Autowired private List<IEcusCompanyEntityMapper> companyEntityMappers;`

- [ ] **Step 2: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

Note: `SyncController` still compiles because it injects concrete mapper types. After all 22 mappers implement `EcusBatchSyncProvider<E>`, the concrete types will satisfy the new parameter type. During the transition (Tasks 5–9), if any un-refactored mapper is passed to `syncIndividualCompanyEntity()` in `SyncController`, it will be a compile error — but the `/company-entities/cache` endpoint only uses mappers that will be refactored in Task 5 (batch 1).

- [ ] **Step 3: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/service/EcusMappingService.java
git commit -m "refactor(ecus-thaison): wire EcusMappingService to BatchSyncAdapterService"
```

---

## Task 5: Refactor mappers — batch 1 (5 mappers)

**Mappers:** `EcusDCHUNGTUKEMMapper`, `EcusREPORTSEXCELMapper`, `EcusSBIEU_THUE_TENMapper`, `EcusSCUAKHAUMapper`, `EcusSCUAKHAUNNMapper`

**Pattern to apply to each mapper:**

1. Replace `implements IEcusCompanyEntityMapper` → `implements EcusBatchSyncProvider<ENTITY_TYPE>`
2. Remove all `@Value` fields (`importLimit`, `batchSize`, `threadPoolSize`)
3. Remove `@Autowired private SyncExecutor syncExecutor;`
4. Remove `syncEntity()` method entirely
5. Remove `processBatch()` method entirely
6. Add `descriptor()` method (see pattern below)
7. Make `processSync()` `private`
8. Remove unused imports: `EcusTenantContext`, `ApplicationContextProvider`, `IEcusCompanyEntityMapper`, `SyncExecutor`, `Page`, `PageRequest`, `Pageable`, `LocalDateTime`, `ArrayList`, `CompletableFuture`, `ExecutorService`, `Executors`, `@Value`
9. Add imports: `EcusBatchSyncProvider`, `BatchSyncDescriptor`

**`descriptor()` pattern:**

```java
@Override
public BatchSyncDescriptor<ENTITY_TYPE> descriptor() {
    return BatchSyncDescriptor.<ENTITY_TYPE>builder()
        .syncName("ENTITY_TABLE_NAME")
        .repository(theRepository)
        .idExtractor(r -> r.getId())         // use actual ID getter
        .descExtractor(r -> r.getId() + " - " + r.getName())  // use actual fields
        .recordProcessor(this::processSync)
        .build();
}
```

**Per-mapper `descriptor()` implementations:**

`EcusDCHUNGTUKEMMapper` — NOTE: this mapper has extra public methods (`getByLoaiKB`, `getByTrangThai`) — keep them:
```java
@Override
public BatchSyncDescriptor<DCHUNGTUKEM> descriptor() {
    return BatchSyncDescriptor.<DCHUNGTUKEM>builder()
        .syncName("DCHUNGTUKEM")
        .repository(dchungtukemRepository)
        .idExtractor(r -> String.valueOf(r.getDChungTuKemID()))
        .descExtractor(r -> r.getSoCt() + " - " + r.getDienGiai())
        .recordProcessor(this::processSync)
        .build();
}
```

`EcusREPORTSEXCELMapper`:
```java
@Override
public BatchSyncDescriptor<REPORTSEXCEL> descriptor() {
    return BatchSyncDescriptor.<REPORTSEXCEL>builder()
        .syncName("REPORTSEXCEL")
        .repository(reportsExcelRepository)
        .idExtractor(r -> r.getMsgOutCode())
        .descExtractor(r -> r.getMsgOutCode() + " - " + r.getMsgOutName())
        .recordProcessor(this::processSync)
        .build();
}
```

`EcusSBIEU_THUE_TENMapper` — read the file first to get the correct extractors, then apply pattern.

`EcusSCUAKHAUMapper`:
```java
@Override
public BatchSyncDescriptor<SCUAKHAU> descriptor() {
    return BatchSyncDescriptor.<SCUAKHAU>builder()
        .syncName("SCUAKHAU")
        .repository(scuakhauRepository)
        .idExtractor(r -> r.getMaCK())
        .descExtractor(r -> r.getMaCK() + " - " + r.getTenCK())
        .recordProcessor(this::processSync)
        .build();
}
```

`EcusSCUAKHAUNNMapper`:
```java
@Override
public BatchSyncDescriptor<SCUAKHAUNN> descriptor() {
    return BatchSyncDescriptor.<SCUAKHAUNN>builder()
        .syncName("SCUAKHAUNN")
        .repository(scuakhaunnRepository)
        .idExtractor(r -> r.getMaCK())
        .descExtractor(r -> r.getMaCK() + " - " + r.getTenCK())
        .recordProcessor(this::processSync)
        .build();
}
```

- [ ] **Step 1: Refactor `EcusDCHUNGTUKEMMapper`** (apply pattern above)
- [ ] **Step 2: Refactor `EcusREPORTSEXCELMapper`** (apply pattern above)
- [ ] **Step 3: Refactor `EcusSBIEU_THUE_TENMapper`** (read file → identify extractors → apply pattern)
- [ ] **Step 4: Refactor `EcusSCUAKHAUMapper`** (apply pattern above)
- [ ] **Step 5: Refactor `EcusSCUAKHAUNNMapper`** (apply pattern above)

- [ ] **Step 6: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusDCHUNGTUKEMMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusREPORTSEXCELMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSBIEU_THUE_TENMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUNNMapper.java
git commit -m "refactor(ecus-thaison): convert mapper batch 1 to EcusBatchSyncProvider (DCHUNGTUKEM, REPORTSEXCEL, SBIEU_THUE_TEN, SCUAKHAU, SCUAKHAUNN)"
```

---

## Task 6: Refactor mappers — batch 2 (5 mappers)

**Mappers:** `EcusSDIA_DIEM_THUPHIMapper`, `EcusSDIA_DIEMMapper`, `EcusSDKGHMapper`, `EcusSDVTMapper`, `EcusSHAIQUANMapper`

Apply the same pattern from Task 5. For each mapper: read the existing `processBatch()` to identify `idExtractor` and `descExtractor` lambdas, then build `descriptor()`.

`EcusSHAIQUANMapper` (reference — already known):
```java
@Override
public BatchSyncDescriptor<SHAIQUAN> descriptor() {
    return BatchSyncDescriptor.<SHAIQUAN>builder()
        .syncName("SHAIQUAN")
        .repository(shaiquanRepository)
        .idExtractor(SHAIQUAN::getMaHQ)
        .descExtractor(r -> r.getMaHQ() + " - " + r.getTenHQ())
        .recordProcessor(this::processSync)
        .build();
}
```

- [ ] **Step 1: Refactor `EcusSDIA_DIEM_THUPHIMapper`**
- [ ] **Step 2: Refactor `EcusSDIA_DIEMMapper`**
- [ ] **Step 3: Refactor `EcusSDKGHMapper`**
- [ ] **Step 4: Refactor `EcusSDVTMapper`**
- [ ] **Step 5: Refactor `EcusSHAIQUANMapper`**

- [ ] **Step 6: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDIA_DIEM_THUPHIMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDIA_DIEMMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDKGHMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDVTMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSHAIQUANMapper.java
git commit -m "refactor(ecus-thaison): convert mapper batch 2 to EcusBatchSyncProvider (SDIA_DIEM_THUPHI, SDIA_DIEM, SDKGH, SDVT, SHAIQUAN)"
```

---

## Task 7: Refactor mappers — batch 3 (5 mappers)

**Mappers:** `EcusSLHINHMDMapper`, `EcusSLOAI_GPMapper`, `EcusSLOAI_KIENMapper`, `EcusSMA_AP_MIENTHUEMapper`, `EcusSMA_MIENTHUEMapper`

Apply the same pattern from Tasks 5–6.

- [ ] **Step 1: Refactor `EcusSLHINHMDMapper`**
- [ ] **Step 2: Refactor `EcusSLOAI_GPMapper`**
- [ ] **Step 3: Refactor `EcusSLOAI_KIENMapper`**
- [ ] **Step 4: Refactor `EcusSMA_AP_MIENTHUEMapper`**
- [ ] **Step 5: Refactor `EcusSMA_MIENTHUEMapper`**

- [ ] **Step 6: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLHINHMDMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_GPMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_KIENMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_AP_MIENTHUEMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_MIENTHUEMapper.java
git commit -m "refactor(ecus-thaison): convert mapper batch 3 to EcusBatchSyncProvider (SLHINHMD, SLOAI_GP, SLOAI_KIEN, SMA_AP_MIENTHUE, SMA_MIENTHUE)"
```

---

## Task 8: Refactor mappers — batch 4 (5 mappers)

**Mappers:** `EcusSMACACLOAIMapper`, `EcusSNGAN_HANGMapper`, `EcusSNGTEMapper`, `EcusSNUOCMapper`, `EcusSPTTTMapper`

**Important — `EcusSMACACLOAIMapper`:** this mapper has extra public helper methods (`getByLoaiMa()`, `getTransportPurposeCodes()`, `getTransportModes()`, `getLoadingUnloadingPositions()`, `getGuarantees()`, `getByMultipleLoaiMa()`). Keep all of them. Only remove the batch boilerplate.

`EcusSNUOCMapper` (reference — already known):
```java
@Override
public BatchSyncDescriptor<SNUOC> descriptor() {
    return BatchSyncDescriptor.<SNUOC>builder()
        .syncName("SNUOC")
        .repository(snuocRepository)
        .idExtractor(SNUOC::getMaNuoc)
        .descExtractor(r -> r.getMaNuoc() + " - " + r.getTenNuoc())
        .recordProcessor(this::processSync)
        .build();
}
```

- [ ] **Step 1: Refactor `EcusSMACACLOAIMapper`** (keep all helper methods)
- [ ] **Step 2: Refactor `EcusSNGAN_HANGMapper`**
- [ ] **Step 3: Refactor `EcusSNGTEMapper`**
- [ ] **Step 4: Refactor `EcusSNUOCMapper`**
- [ ] **Step 5: Refactor `EcusSPTTTMapper`**

- [ ] **Step 6: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMACACLOAIMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGAN_HANGMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGTEMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNUOCMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTTTMapper.java
git commit -m "refactor(ecus-thaison): convert mapper batch 4 to EcusBatchSyncProvider (SMACACLOAI, SNGAN_HANG, SNGTE, SNUOC, SPTTT)"
```

---

## Task 9: Refactor mappers — batch 5 (final 2 mappers)

**Mappers:** `EcusSPTVTMapper`, `EcusSVB_PQMapper`

Apply the same pattern from Tasks 5–8.

- [ ] **Step 1: Refactor `EcusSPTVTMapper`**
- [ ] **Step 2: Refactor `EcusSVB_PQMapper`**

- [ ] **Step 3: Compile**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTVTMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSVB_PQMapper.java
git commit -m "refactor(ecus-thaison): convert mapper batch 5 to EcusBatchSyncProvider (SPTVT, SVB_PQ) — all 22 mappers done"
```

---

## Task 10: Update `CompanyEntitiesIntegrationTest`

`processSync()` is now `private` in all mappers. The integration test must switch from calling `processSync()` directly to calling through the descriptor.

**File:** `src/test/java/com/egov/ecusthaison/CompanyEntitiesIntegrationTest.java`

**Pattern to apply to every test method:**

```java
// Before
scuakhauMapper.processSync(COMPANY_ID, scuakhau, syncSource.getId());

// After
scuakhauMapper.descriptor().getRecordProcessor().process(COMPANY_ID, scuakhau, syncSource.getId());
```

Apply this change to every occurrence of `mapper.processSync(...)` in the file. The rest of each test (assertions, repository lookups) stays the same.

- [ ] **Step 1: Update all `processSync()` calls in `CompanyEntitiesIntegrationTest`**

Find all occurrences:
```bash
grep -n "\.processSync(" module/ecus-thaison/src/test/java/com/egov/ecusthaison/CompanyEntitiesIntegrationTest.java
```

Replace each `xyzMapper.processSync(COMPANY_ID, entity, syncSource.getId())` with `xyzMapper.descriptor().getRecordProcessor().process(COMPANY_ID, entity, syncSource.getId())`.

- [ ] **Step 2: Compile tests**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileTestJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 3: Commit**

```bash
git add module/ecus-thaison/src/test/java/com/egov/ecusthaison/CompanyEntitiesIntegrationTest.java
git commit -m "test(ecus-thaison): update CompanyEntitiesIntegrationTest to use descriptor().getRecordProcessor()"
```

---

## Task 11: Full test suite

Run all tests to verify nothing is broken.

- [ ] **Step 1: Run unit tests**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*UnitTest"
```

Expected: All PASS. Should include at minimum: `BatchSyncOrchestratorUnitTest` (4 tests), `BatchSyncAdapterServiceUnitTest` (4 tests), plus any existing unit tests.

- [ ] **Step 2: Run integration tests** (requires Docker — starts Postgres, MSSQL, Kafka containers)

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*IntegrationTest"
```

Expected: All PASS. Key test: `CompanyEntitiesIntegrationTest`.

- [ ] **Step 3: Run full module build**

```bash
./gradlew :datatp-egov-module-ecus-thaison:build
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Verify `BatchSyncAdapterService` discovers all 22 providers at startup**

Check test logs for the `@PostConstruct` output. Should list exactly 22 entries:

```
BatchSyncAdapterService: discovered 22 company sync providers:
  - DCHUNGTUKEM
  - REPORTSEXCEL
  ...
```

If count is wrong: check that all 22 mapper classes have `implements EcusBatchSyncProvider<E>` and are annotated `@Service`.
