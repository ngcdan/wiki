---
title: "Spec — Company Mapper Batch/Single Split Design"
tags: [egov, specs, design, mapper]
created: 2026-03-29
---

# Design: Split Batch / Single Logic in Company Mapper Layer

**Date:** 2026-03-29
**Scope:** `module/ecus-thaison` — `logic/mapper/company/` (22 mapper classes)
**Goal:** Remove ~3600 lines of duplicated batch boilerplate; each mapper retains only its unique single-record logic.

---

## Problem

All 22 mappers in `logic/mapper/company/` share an identical ~165-line structure per file:

| Method | Lines | Uniqueness |
|---|---|---|
| `syncEntity()` | ~100 | 0% — only the entity name string differs |
| `processBatch()` | ~35 | ~5% — only repository type and extractors differ |
| `processSync()` | ~15 | 100% — the only real per-mapper logic |

All 22 files duplicate the same threading, paging, context propagation, result aggregation, and logging. Total waste: ~3600 lines.

---

## Chosen Approach: Provider + Orchestrator (Option B)

Mappers are decoupled from batch concerns entirely. A descriptor object carries per-mapper config; a shared orchestrator drives execution.

### Why not abstract base class (Option A)

Inheritance couples mapper lifecycle to batch config. Harder to test batch logic in isolation. Adding new hooks (e.g., per-batch callbacks) requires touching the base class and all subclasses.

### Why not interface extension only (Option C)

Does not eliminate the boilerplate — only formalises it. Each mapper still contains ~150 lines of duplicated code.

---

## Components

### 1. `RecordProcessor<E>` (functional interface)

```java
@FunctionalInterface
public interface RecordProcessor<E> {
    void process(Long companyId, E record, Long syncSourceConfigId);
}
```

Single-responsibility: process one record. Matches the signature of all existing `processSync()` methods.

### 2. `BatchSyncDescriptor<E>` (data object, no Spring dependency)

Holds all configuration and optional hooks for one sync job.

```java
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

    // Optional hooks — null means skip
    private final BiConsumer<Integer, SyncResult> onBatchComplete;  // (pageNumber, batchResult)
    private final Consumer<SyncResult> onSyncComplete;              // called after all pages
    private final UnaryOperator<SyncResult> resultEnricher;         // enrich final SyncResult
}
```

**Extension pattern:** to customise behaviour for a specific mapper, set the relevant hook in `descriptor()`. No subclassing required.

### 3. `EcusBatchSyncProvider<E>` (interface)

```java
public interface EcusBatchSyncProvider<E> {
    BatchSyncDescriptor<E> descriptor();
}
```

All 22 company mappers implement this instead of `IEcusCompanyEntityMapper`.

### 4. `BatchSyncOrchestrator` (`@Service`)

Owns all batch logic currently duplicated across `syncEntity()` and `processBatch()`.

**`run(descriptor)` flow:**

```
1. Validate companyId present in EcusTenantContext
2. Count total records via descriptor.repository
3. Return empty SyncResult if count == 0
4. Resolve effective batchSize / importLimit / threadPoolSize
   (descriptor override → app @Value default)
5. Calculate totalPages = ceil(min(count, importLimit) / batchSize)
6. Capture EcusTenantContext fields for async threads
7. Create ExecutorService (fixed thread pool)
8. For each page: submit CompletableFuture
   a. Restore EcusTenantContext in thread
   b. Call self.processBatch(descriptor, companyId, page, syncSourceConfigId)
      via Spring proxy (ApplicationContextProvider) to preserve @Transactional
   c. Clear EcusTenantContext in finally
   d. If onBatchComplete hook present: invoke after processBatch
9. join() all futures
10. Aggregate SyncResult across all pages
11. If resultEnricher present: apply to final SyncResult
12. If onSyncComplete present: invoke
13. Shutdown ExecutorService
14. Return final SyncResult
```

**`processBatch()` is `public` and annotated `@Transactional(propagation = Propagation.REQUIRED)`** — required for Spring proxy to wrap per-record `save()` calls within a transaction. Called via `ApplicationContextProvider.getBean(BatchSyncOrchestrator.class)` from async threads (same pattern as current mapper code).

**`EcusTenantContext` lifecycle in async threads:** each `CompletableFuture` restores context before calling `processBatch()` and always clears it in a `finally` block — even if `processBatch()` throws.

**`MigrationJob` lifecycle:** one `MigrationJob` is created per page (per `processBatch()` call) via `SyncExecutor.executeWithTracking()`. This matches current behaviour. The outer orchestrator aggregates page-level `SyncResult` objects into the final result; it does not create a top-level `MigrationJob` itself.

**Hook exception handling:** if any hook (`onBatchComplete`, `onSyncComplete`, `resultEnricher`) throws, the orchestrator logs the error and continues. Hooks must not affect batch correctness.

**Error handling:**
- CompanyId null → throw `RuntimeException` immediately, return error SyncResult
- Per-batch exception → return error SyncResult for that page, continue others
- Unexpected exception in outer try → log, return global error SyncResult

### 5. `BatchSyncAdapterService` (`@Service`)

Auto-discovers all `EcusBatchSyncProvider` beans; provides routing.

```java
@Service
public class BatchSyncAdapterService {

    @Autowired private List<EcusBatchSyncProvider<?>> providers;
    @Autowired private BatchSyncOrchestrator orchestrator;

    public List<SyncResult> syncAll();                            // run all providers
    public SyncResult syncByName(String syncName);                // find by name, run
    public SyncResult sync(EcusBatchSyncProvider<?> provider);   // run one provider
}
```

`syncByName` throws `IllegalArgumentException` if no provider matches the name.

**`syncName` uniqueness:** each `descriptor().getSyncName()` must be unique across all providers. `BatchSyncAdapterService` logs all discovered providers and their names at startup (`@PostConstruct`) to surface duplicates early.

---

## Changes to Existing Code

### `EcusMappingService`

Two changes only:

```java
// Remove
@Autowired private List<IEcusCompanyEntityMapper> companyEntityMappers;

// Add
@Autowired private BatchSyncAdapterService batchSyncAdapterService;

// syncCompanyEntities()
return batchSyncAdapterService.syncAll();

// syncIndividualCompanyEntity — signature change
public SyncResult syncIndividualCompanyEntity(EcusBatchSyncProvider<?> provider) {
    return batchSyncAdapterService.sync(provider);
}
```

### `IEcusCompanyEntityMapper`

**Kept as-is.** Not used by company mappers after this change, but left for potential use by other mapper categories (core, partner) which are out of scope.

### `SyncController`

**No changes required.** `SyncController` injects concrete mapper beans via `@RequiredArgsConstructor` (e.g. `EcusSLOAI_GPMapper`). After refactor, those beans still exist as `@Service` — they just implement `EcusBatchSyncProvider<E>` instead of `IEcusCompanyEntityMapper`. At call sites like:

```java
ecusMappingService.syncIndividualCompanyEntity(ecusSLOAI_GPMapper);
```

the concrete mapper instance satisfies the new `EcusBatchSyncProvider<?>` parameter type, so no change is needed in `SyncController`.

### Concrete mappers (22 files)

Each mapper:
- Removes: `@Value` fields, `syncEntity()`, `processBatch()`, `@Autowired SyncExecutor`
- Removes: `implements IEcusCompanyEntityMapper`
- Adds: `implements EcusBatchSyncProvider<E>`
- Adds: `descriptor()` method (~10 lines)
- Keeps: `processSync()` (renamed to `private`, was `public`)

**Example — `EcusSHAIQUANMapper` after refactor (~35 lines):**

```java
@Service
@Slf4j
public class EcusSHAIQUANMapper implements EcusBatchSyncProvider<SHAIQUAN> {

    @Autowired private SHAIQUANRepository repo;
    @Autowired private CustomsOfficeService customsOfficeService;

    @Override
    public BatchSyncDescriptor<SHAIQUAN> descriptor() {
        return BatchSyncDescriptor.<SHAIQUAN>builder()
            .syncName("SHAIQUAN")
            .repository(repo)
            .idExtractor(SHAIQUAN::getMaHQ)
            .descExtractor(r -> r.getMaHQ() + " - " + r.getTenHQ())
            .recordProcessor(this::processSync)
            .build();
    }

    private void processSync(Long companyId, SHAIQUAN shaiquan, Long syncSourceConfigId) {
        String trimCode = shaiquan.getMaHQ() != null ? shaiquan.getMaHQ().trim() : null;
        CustomsOffice existing = customsOfficeService
            .findByCompanyIdAndCodeAndSyncSourceConfigurationId(companyId, trimCode, syncSourceConfigId);
        if (existing == null) {
            existing = new CustomsOffice();
            existing.setCompanyId(companyId);
            existing.setSyncSourceConfigurationId(syncSourceConfigId);
        }
        customsOfficeService.save(shaiquan.toCustomsOffice(existing));
    }
}
```

---

## File Layout (new files)

```
module/ecus-thaison/src/main/java/com/egov/ecusthaison/
  sync/
    BatchSyncDescriptor.java       (new)
    RecordProcessor.java           (new)
    BatchSyncOrchestrator.java     (new)
    BatchSyncAdapterService.java   (new)
  logic/
    EcusBatchSyncProvider.java     (new)
    mapper/company/
      Ecus*Mapper.java             (22 files — refactored)
  service/
    EcusMappingService.java        (modified — 2 changes)
```

---

## Scope Boundary

- **In scope:** `logic/mapper/company/` (22 files) + 5 new files + 2 modified files (`EcusMappingService`)
- **Out of scope:** `logic/mapper/partner/`, `logic/mapper/core/`, CDC event handlers — same boilerplate exists there but will be addressed separately if needed; `BatchSyncOrchestrator` and `EcusBatchSyncProvider` are designed to be reusable for those layers
- **No schema changes, no Liquibase migrations**

---

## Impact Summary

| Metric | Before | After |
|---|---|---|
| Lines per mapper | ~200 | ~35 |
| Total lines in company mappers | ~4400 | ~770 |
| Batch boilerplate locations | 22 | 1 (`BatchSyncOrchestrator`) |
| New files | — | 4 |
| Files modified | — | 23 (22 mappers + `EcusMappingService`) |
