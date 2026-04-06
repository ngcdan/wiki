# ecus-thaison Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 3 operational gaps in the ecus-thaison module: monitoring endpoints, DLQ consumer for silent CDC failures, and batch error retry.

**Architecture:**
- Gap 1 (Monitoring): Read-only REST layer over existing `MigrationJob`/`MigrationRecord` DB tables + Actuator counters in `CommonCDCListener`. No new entities needed.
- Gap 2 (DLQ Consumer): New `CDCEventProcessor` component extracted from `CommonCDCListener`, used by both the existing CDC listener and a new `DLQConsumer`. Dead events stored in a new `DeadLetterEvent` entity. Replay via REST.
- Gap 3 (Batch Retry): Add `supportedEntityClass()` to `IEcusSingleMapper`, build `EcusSingleMapperRegistry`, implement `RetryService` that deserializes `MigrationRecord.sourceData` and re-routes to the correct mapper.

**Tech Stack:** Spring Boot 3.3.3, Java 21, Spring Kafka, Spring Data JPA (PostgreSQL), Spring Actuator + Micrometer, Jackson ObjectMapper, Lombok, JUnit 5 + Mockito, Testcontainers.

**Spec:** `docs/superpowers/specs/2026-03-29-ecus-thaison-architecture-design.md`

**Test commands:**
- Unit tests: `./gradlew :datatp-egov-module-ecus-thaison:test -Dgroups=unit`
- Integration tests: `./gradlew :datatp-egov-module-ecus-thaison:test -Dgroups=integration`
- All: `./gradlew :datatp-egov-module-ecus-thaison:test`

---

## Phase 1 — Monitoring

### File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `module/ecutoms/src/main/java/com/egov/ecutoms/service/MigrationJobQueryService.java` | Read-only queries over MigrationJob + MigrationRecord |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java` | GET /api/sync/jobs, GET /api/sync/jobs/{id} |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobSummaryDto.java` | Flat response for job list |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobDetailDto.java` | Job + failures response |
| Modify | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java` | Inject MeterRegistry, increment counters |
| Create | `module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java` | Unit tests for controller |
| Create | `module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/MigrationJobQueryServiceUnitTest.java` | Unit tests for query service |

---

### Task 1: MigrationJobQueryService

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/service/MigrationJobQueryService.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/MigrationJobQueryServiceUnitTest.java`

- [ ] **Step 1: Write the failing unit test**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/MigrationJobQueryServiceUnitTest.java
package com.egov.ecusthaison.sync;

import com.egov.ecutoms.entity.MigrationJob;
import com.egov.ecutoms.entity.MigrationRecord;
import com.egov.ecutoms.entity.MigrationRecordStatus;
import com.egov.ecutoms.entity.MigrationStatus;
import com.egov.ecutoms.repository.MigrationJobRepository;
import com.egov.ecutoms.repository.MigrationRecordRepository;
import com.egov.ecutoms.service.MigrationJobQueryService;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class MigrationJobQueryServiceUnitTest {

  @Mock
  private MigrationJobRepository jobRepository;

  @Mock
  private MigrationRecordRepository recordRepository;

  @InjectMocks
  private MigrationJobQueryService service;

  @Test
  void listJobs_returnsPagedResults() {
    MigrationJob job = new MigrationJob();
    job.setId(1L);
    job.setJobName("DTOKHAIMD_Page_0");
    job.setStatus(MigrationStatus.COMPLETED);
    Page<MigrationJob> page = new PageImpl<>(List.of(job));
    when(jobRepository.findAll(any(PageRequest.class))).thenReturn(page);

    Page<MigrationJob> result = service.listJobs(PageRequest.of(0, 20));

    assertThat(result.getContent()).hasSize(1);
    assertThat(result.getContent().get(0).getJobName()).isEqualTo("DTOKHAIMD_Page_0");
  }

  @Test
  void getJobById_returnsEmpty_whenNotFound() {
    when(jobRepository.findById(99L)).thenReturn(Optional.empty());

    Optional<MigrationJob> result = service.getJobById(99L);

    assertThat(result).isEmpty();
  }

  @Test
  void getFailedRecords_queriesWithFailedStatus() {
    MigrationRecord record = new MigrationRecord();
    record.setRecordIdentifier("42");
    Page<MigrationRecord> page = new PageImpl<>(List.of(record));
    when(recordRepository.findByMigrationJobIdAndStatus(eq(1L), eq(MigrationRecordStatus.FAILED), any()))
        .thenReturn(page);

    Page<MigrationRecord> result = service.getFailedRecords(1L, PageRequest.of(0, 20));

    assertThat(result.getContent()).hasSize(1);
  }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.MigrationJobQueryServiceUnitTest" -Dgroups=unit
```

Expected: FAIL — `MigrationJobQueryService` does not exist.

- [ ] **Step 3: Create MigrationJobQueryService**

```java
// module/ecutoms/src/main/java/com/egov/ecutoms/service/MigrationJobQueryService.java
package com.egov.ecutoms.service;

import com.egov.ecutoms.entity.MigrationJob;
import com.egov.ecutoms.entity.MigrationRecord;
import com.egov.ecutoms.entity.MigrationRecordStatus;
import com.egov.ecutoms.repository.MigrationJobRepository;
import com.egov.ecutoms.repository.MigrationRecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class MigrationJobQueryService {

  @Autowired
  private MigrationJobRepository jobRepository;

  @Autowired
  private MigrationRecordRepository recordRepository;

  public Page<MigrationJob> listJobs(Pageable pageable) {
    return jobRepository.findAll(pageable);
  }

  public Optional<MigrationJob> getJobById(Long jobId) {
    return jobRepository.findById(jobId);
  }

  public Page<MigrationRecord> getFailedRecords(Long jobId, Pageable pageable) {
    return recordRepository.findByMigrationJobIdAndStatus(jobId, MigrationRecordStatus.FAILED, pageable);
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.MigrationJobQueryServiceUnitTest" -Dgroups=unit
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/service/MigrationJobQueryService.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/MigrationJobQueryServiceUnitTest.java
git commit -m "feat: add MigrationJobQueryService for read-only job/record queries"
```

---

### Task 2: DTO classes

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobSummaryDto.java`
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobDetailDto.java`
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/FailedRecordDto.java`

These are simple value objects — no test needed for pure data classes.

- [ ] **Step 1: Create JobSummaryDto**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobSummaryDto.java
package com.egov.ecusthaison.controller.dto;

import com.egov.ecutoms.entity.MigrationJob;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class JobSummaryDto {
  private final Long id;
  private final String jobName;
  private final String status;
  private final Integer totalRecords;
  private final Integer successCount;
  private final Integer failureCount;
  private final Integer skipCount;
  private final LocalDateTime startTime;
  private final LocalDateTime endTime;

  public JobSummaryDto(MigrationJob job) {
    this.id = job.getId();
    this.jobName = job.getJobName();
    this.status = job.getStatus() != null ? job.getStatus().name() : null;
    this.totalRecords = job.getTotalRecords();
    this.successCount = job.getSuccessCount();
    this.failureCount = job.getFailureCount();
    this.skipCount = job.getSkipCount();
    this.startTime = job.getStartTime();
    this.endTime = job.getEndTime();
  }
}
```

- [ ] **Step 2: Create FailedRecordDto**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/FailedRecordDto.java
package com.egov.ecusthaison.controller.dto;

import com.egov.ecutoms.entity.MigrationRecord;
import lombok.Getter;

@Getter
public class FailedRecordDto {
  private final Long id;
  private final String recordIdentifier;
  private final String targetEntity;
  private final String status;
  private final String errorType;
  private final String errorMessage;

  public FailedRecordDto(MigrationRecord record) {
    this.id = record.getId();
    this.recordIdentifier = record.getRecordIdentifier();
    this.targetEntity = record.getTargetEntity();
    this.status = record.getStatus() != null ? record.getStatus().name() : null;
    this.errorType = record.getErrorType() != null ? record.getErrorType().name() : null;
    this.errorMessage = record.getErrorMessage();
  }
}
```

- [ ] **Step 3: Create JobDetailDto**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/JobDetailDto.java
package com.egov.ecusthaison.controller.dto;

import com.egov.ecutoms.entity.MigrationJob;
import com.egov.ecutoms.entity.MigrationRecord;
import lombok.Getter;
import org.springframework.data.domain.Page;

import java.util.List;
import java.util.stream.Collectors;

@Getter
public class JobDetailDto {
  private final JobSummaryDto job;
  private final List<FailedRecordDto> failures;
  private final long totalFailures;
  private final int failurePage;
  private final int failureTotalPages;

  public JobDetailDto(MigrationJob job, Page<MigrationRecord> failures) {
    this.job = new JobSummaryDto(job);
    this.failures = failures.getContent().stream()
        .map(FailedRecordDto::new)
        .collect(Collectors.toList());
    this.totalFailures = failures.getTotalElements();
    this.failurePage = failures.getNumber();
    this.failureTotalPages = failures.getTotalPages();
  }
}
```

- [ ] **Step 4: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/dto/
git commit -m "feat: add DTO classes for sync job monitoring responses"
```

---

### Task 3: SyncJobController + Actuator metrics

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java`

- [ ] **Step 1: Write failing controller test**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java
package com.egov.ecusthaison.controller;

import com.egov.ecutoms.entity.MigrationJob;
import com.egov.ecutoms.entity.MigrationStatus;
import com.egov.ecutoms.service.MigrationJobQueryService;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class SyncJobControllerUnitTest {

  @Mock
  private MigrationJobQueryService queryService;

  @InjectMocks
  private SyncJobController controller;

  @Test
  void listJobs_returns200WithPage() {
    MigrationJob job = new MigrationJob();
    job.setId(1L);
    job.setStatus(MigrationStatus.COMPLETED);
    when(queryService.listJobs(any())).thenReturn(new PageImpl<>(List.of(job)));

    ResponseEntity<?> response = controller.listJobs(0, 20);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
  }

  @Test
  void getJobDetail_returns404_whenJobNotFound() {
    when(queryService.getJobById(99L)).thenReturn(Optional.empty());

    ResponseEntity<?> response = controller.getJobDetail(99L, 0, 20);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
  }

  @Test
  void getJobDetail_returns200_whenFound() {
    MigrationJob job = new MigrationJob();
    job.setId(1L);
    job.setStatus(MigrationStatus.COMPLETED);
    when(queryService.getJobById(1L)).thenReturn(Optional.of(job));
    when(queryService.getFailedRecords(any(), any())).thenReturn(Page.empty());

    ResponseEntity<?> response = controller.getJobDetail(1L, 0, 20);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
  }
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.SyncJobControllerUnitTest" -Dgroups=unit
```

Expected: FAIL — `SyncJobController` does not exist.

- [ ] **Step 3: Create SyncJobController**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java
package com.egov.ecusthaison.controller;

import com.egov.ecutoms.entity.MigrationJob;
import com.egov.ecutoms.entity.MigrationRecord;
import com.egov.ecutoms.service.MigrationJobQueryService;
import com.egov.ecusthaison.controller.dto.JobDetailDto;
import com.egov.ecusthaison.controller.dto.JobSummaryDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequestMapping("/api/sync/jobs")
public class SyncJobController {

  @Autowired
  private MigrationJobQueryService queryService;

  @GetMapping
  public ResponseEntity<Page<JobSummaryDto>> listJobs(
      @RequestParam(defaultValue = "0") int page,
      @RequestParam(defaultValue = "20") int size) {
    Page<MigrationJob> jobs = queryService.listJobs(PageRequest.of(page, size));
    return ResponseEntity.ok(jobs.map(JobSummaryDto::new));
  }

  @GetMapping("/{jobId}")
  public ResponseEntity<JobDetailDto> getJobDetail(
      @PathVariable Long jobId,
      @RequestParam(defaultValue = "0") int failurePage,
      @RequestParam(defaultValue = "20") int failureSize) {
    Optional<MigrationJob> job = queryService.getJobById(jobId);
    if (job.isEmpty()) {
      return ResponseEntity.notFound().build();
    }
    Page<MigrationRecord> failures = queryService.getFailedRecords(jobId, PageRequest.of(failurePage, failureSize));
    return ResponseEntity.ok(new JobDetailDto(job.get(), failures));
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.SyncJobControllerUnitTest" -Dgroups=unit
```

Expected: PASS

- [ ] **Step 5: Add Actuator metrics to CommonCDCListener**

Open `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java`.

Add imports:
```java
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
```

Add field after existing `@Autowired` fields:
```java
@Autowired
private MeterRegistry meterRegistry;
```

After the successful acknowledgment line (`acknowledgment.acknowledge();`), add:
```java
meterRegistry.counter("ecus.cdc.events.processed", "table", tableName).increment();
```

In the `catch` block (if any exists for handler errors), or after the `if (handler == null)` skip, add in the default switch case or as appropriate:
```java
meterRegistry.counter("ecus.cdc.events.failed", "table", tableName != null ? tableName : "unknown").increment();
```

- [ ] **Step 6: Verify build passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java
git commit -m "feat: add sync job monitoring endpoints and Actuator CDC metrics"
```

---

## Phase 2 — DLQ Consumer

### File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeadLetterEvent.java` | Dead event storage entity |
| Create | `module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeadLetterEventRepository.java` | JPA repo for dead events |
| Create (refactor) | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/processor/CDCEventProcessor.java` | Shared CDC processing logic extracted from CommonCDCListener |
| Modify | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java` | Delegate to CDCEventProcessor |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQConsumer.java` | Kafka listener for *.DLQ topics |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQEventService.java` | Retry logic + dead event persistence |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/DLQController.java` | POST /api/dlq/replay/{id} |
| Create | `module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/dlq/DLQConsumerUnitTest.java` | Unit tests for DLQ flow |

---

### Task 4: DeadLetterEvent entity + repository

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeadLetterEvent.java`
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeadLetterEventRepository.java`

- [ ] **Step 1: Create DeadLetterEvent entity**

```java
// module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeadLetterEvent.java
package com.egov.ecutoms.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "dead_letter_event",
    indexes = {
        @Index(name = "idx_dle_topic", columnList = "topic"),
        @Index(name = "idx_dle_resolved_at", columnList = "resolved_at"),
        @Index(name = "idx_dle_created_at", columnList = "created_at")
    })
@Getter
@Setter
@NoArgsConstructor
public class DeadLetterEvent {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private String topic;

  @Column(name = "partition_num")
  private Integer partitionNum;

  @Column(name = "kafka_offset")
  private Long kafkaOffset;

  // Full original message payload
  @Column(columnDefinition = "text", nullable = false)
  private String payload;

  @Column(name = "error_message", columnDefinition = "text")
  private String errorMessage;

  @Column(name = "retry_count", nullable = false)
  private int retryCount = 0;

  @Column(name = "created_at", nullable = false)
  private LocalDateTime createdAt;

  @Column(name = "resolved_at")
  private LocalDateTime resolvedAt;
}
```

- [ ] **Step 2: Create DeadLetterEventRepository**

```java
// module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeadLetterEventRepository.java
package com.egov.ecutoms.repository;

import com.egov.ecutoms.entity.DeadLetterEvent;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DeadLetterEventRepository extends JpaRepository<DeadLetterEvent, Long> {

  Page<DeadLetterEvent> findByResolvedAtIsNull(Pageable pageable);

  Page<DeadLetterEvent> findByTopic(String topic, Pageable pageable);
}
```

- [ ] **Step 3: Verify build passes**

```bash
./gradlew :datatp-egov-module-ecutoms:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeadLetterEvent.java \
        module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeadLetterEventRepository.java
git commit -m "feat: add DeadLetterEvent entity and repository for DLQ dead events"
```

---

### Task 5: Extract CDCEventProcessor from CommonCDCListener

**Why:** DLQConsumer needs the same processing logic as CommonCDCListener. Extract it to avoid duplication.

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/processor/CDCEventProcessor.java`
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/processor/CDCEventProcessorUnitTest.java`

- [ ] **Step 1: Write failing test for CDCEventProcessor**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/processor/CDCEventProcessorUnitTest.java
package com.egov.ecusthaison.cdc.processor;

import com.egov.ecusthaison.cdc.handler.CDCEventHandler;
import com.egov.ecusthaison.cdc.handler.CDCEventHandlerRegistry;
import com.egov.ecusthaison.context.EcusTenantContext;
import com.egov.ecutoms.entity.SyncSourceConfiguration;
import com.egov.ecutoms.repository.SyncSourceConfigurationRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class CDCEventProcessorUnitTest {

  @Mock
  private CDCEventHandlerRegistry handlerRegistry;

  @Mock
  private SyncSourceConfigurationRepository syncSourceConfigRepository;

  @Mock
  private ObjectMapper objectMapper;

  @Mock
  private CDCEventHandler handler;

  @InjectMocks
  private CDCEventProcessor processor;

  @AfterEach
  void cleanup() {
    EcusTenantContext.clear();
  }

  @Test
  void process_skipsWhenSyncSourceNotFound() throws Exception {
    when(syncSourceConfigRepository.findByVendorIgnoreCaseAndSourceName(any(), any()))
        .thenReturn(Optional.empty());

    boolean result = processor.process(validPayload(), "cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC");

    assertThat(result).isFalse();
    verify(handlerRegistry, never()).getHandler(any());
  }

  @Test
  void process_skipsWhenHandlerNotFound() throws Exception {
    SyncSourceConfiguration config = new SyncSourceConfiguration();
    config.setCompanyId(1L);
    when(syncSourceConfigRepository.findByVendorIgnoreCaseAndSourceName(any(), any()))
        .thenReturn(Optional.of(config));
    when(handlerRegistry.getHandler("SNUOC")).thenReturn(null);

    boolean result = processor.process(validPayload(), "cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC");

    assertThat(result).isFalse();
  }

  private String validPayload() {
    return """
        {"op":"c","source":{"table":"SNUOC"},"after":{"MaNuoc":"VN","TenNuoc":"Vietnam"}}
        """;
  }
}
```

Note: This test uses `assertThat` from AssertJ — add `import static org.assertj.core.api.Assertions.assertThat;`.

- [ ] **Step 2: Run to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.CDCEventProcessorUnitTest" -Dgroups=unit
```

Expected: FAIL — `CDCEventProcessor` does not exist.

- [ ] **Step 3: Create CDCEventProcessor**

The processing logic to extract from CommonCDCListener: parse topic, lookup SyncSourceConfiguration, set EcusTenantContext, deserialize CDCEvent, get handler, route to correct handle* method.

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/processor/CDCEventProcessor.java
package com.egov.ecusthaison.cdc.processor;

import com.egov.ecusthaison.cdc.handler.CDCEventHandler;
import com.egov.ecusthaison.cdc.handler.CDCEventHandlerRegistry;
import com.egov.ecusthaison.cdc.model.CDCEvent;
import com.egov.ecusthaison.context.EcusTenantContext;
import com.egov.ecutoms.entity.SyncSourceConfiguration;
import com.egov.ecutoms.repository.SyncSourceConfigurationRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Optional;

/**
 * Stateless CDC event processor — shared between CommonCDCListener (real-time) and DLQConsumer (retry).
 * Returns true if the event was successfully routed to a handler, false if skipped.
 */
@Slf4j
@Component
public class CDCEventProcessor {

  @Autowired
  private CDCEventHandlerRegistry handlerRegistry;

  @Autowired
  private SyncSourceConfigurationRepository syncSourceConfigRepository;

  @Autowired
  private ObjectMapper objectMapper;

  /**
   * Process a single CDC message. Returns true on success, false on skip (no handler, no config).
   * Throws on processing error so caller can decide how to handle (ack vs DLQ).
   */
  public boolean process(String message, String topic) throws Exception {
    if (message == null || message.isBlank()) {
      log.warn("Skipping null/empty CDC message from topic: {}", topic);
      return false;
    }

    TopicInfo info = parseTopicName(topic);
    if (info == null) {
      log.error("Cannot parse topic: {}", topic);
      return false;
    }

    Optional<SyncSourceConfiguration> syncSource = syncSourceConfigRepository
        .findByVendorIgnoreCaseAndSourceName(info.vendor(), info.sourceName());
    if (syncSource.isEmpty()) {
      log.error("No SyncSourceConfiguration for vendor={}, sourceName={}", info.vendor(), info.sourceName());
      return false;
    }

    SyncSourceConfiguration config = syncSource.get();
    EcusTenantContext.set(info.sourceName(), config.getCompanyId(), config.getId());
    try {
      CDCEvent<Map<String, Object>> cdcEvent = objectMapper.readValue(
          message,
          objectMapper.getTypeFactory().constructParametricType(CDCEvent.class, Map.class));

      String tableName = cdcEvent.getSource().getTable();
      CDCEventHandler handler = handlerRegistry.getHandler(tableName);
      if (handler == null) {
        log.warn("No handler for table: {}", tableName);
        return false;
      }

      switch (cdcEvent.getOperation()) {
        case "c" -> handler.handleCreate(cdcEvent, config);
        case "u" -> handler.handleUpdate(cdcEvent, config);
        case "d" -> handler.handleDelete(cdcEvent, config);
        case "r" -> handler.handleSnapshot(cdcEvent, config);
        default -> log.warn("Unknown operation: {} for table: {}", cdcEvent.getOperation(), tableName);
      }
      return true;
    } finally {
      EcusTenantContext.clear();
    }
  }

  private TopicInfo parseTopicName(String topic) {
    String[] parts = topic.split("\\.");
    if (parts.length < 4) return null;
    String prefix = parts[0];
    String sourceName = parts[1];
    if (prefix.startsWith("cdc-")) {
      String[] p = prefix.split("-", 3);
      if (p.length >= 3) return new TopicInfo(p[2], sourceName);
    }
    return new TopicInfo(prefix.split("-")[0], sourceName);
  }

  private record TopicInfo(String vendor, String sourceName) {}
}
```

- [ ] **Step 4: Update CommonCDCListener to delegate to CDCEventProcessor**

Open `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java`.

Replace the inline processing logic with a call to `CDCEventProcessor.process(message, topic)`. The listener keeps: DLQ skip guard, null/empty message guard, manual acknowledgment, error handling. Remove the duplicated parsing/routing code.

The resulting `listen()` method becomes:
```java
@KafkaListener(topicPattern = "${kafka.cdc.topics}", groupId = "${spring.kafka.consumer.group-id}",
    containerFactory = "kafkaListenerContainerFactory")
public void listen(@Payload(required = false) String message,
    @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
    @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
    @Header(KafkaHeaders.OFFSET) long offset,
    Acknowledgment acknowledgment) throws JsonProcessingException {
  if (topic.endsWith(dlqTopicSuffix)) {
    acknowledgment.acknowledge();
    return;
  }
  try {
    boolean processed = cdcEventProcessor.process(message, topic);
    if (processed) {
      meterRegistry.counter("ecus.cdc.events.processed", "topic", topic).increment();
    }
    acknowledgment.acknowledge();
  } catch (Exception e) {
    log.error("CDC processing failed for topic: {}, offset: {}", topic, offset, e);
    meterRegistry.counter("ecus.cdc.events.failed", "topic", topic).increment();
    // Do NOT acknowledge — let Kafka retry / route to DLQ
    throw new RuntimeException(e);
  }
}
```

Add `@Autowired private CDCEventProcessor cdcEventProcessor;` field.

- [ ] **Step 5: Run tests to verify passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.CDCEventProcessorUnitTest" -Dgroups=unit
./gradlew :datatp-egov-module-ecus-thaison:test -Dgroups=unit
```

Expected: All unit tests PASS.

- [ ] **Step 6: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/processor/ \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/listener/CommonCDCListener.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/processor/
git commit -m "refactor: extract CDCEventProcessor from CommonCDCListener for reuse in DLQ consumer"
```

---

### Task 6: DLQEventService + DLQConsumer

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQEventService.java`
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQConsumer.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/dlq/DLQConsumerUnitTest.java`

- [ ] **Step 1: Write failing tests for DLQ flow**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/dlq/DLQConsumerUnitTest.java
package com.egov.ecusthaison.cdc.dlq;

import com.egov.ecusthaison.cdc.processor.CDCEventProcessor;
import com.egov.ecutoms.entity.DeadLetterEvent;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.support.Acknowledgment;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class DLQConsumerUnitTest {

  @Mock
  private CDCEventProcessor cdcEventProcessor;

  @Mock
  private DLQEventService dlqEventService;

  @Mock
  private Acknowledgment acknowledgment;

  @InjectMocks
  private DLQConsumer dlqConsumer;

  @Test
  void listen_acknowledgesAndSkips_whenMessageIsNull() {
    dlqConsumer.listen(null, "cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ", 0, 0L, acknowledgment);

    verify(acknowledgment).acknowledge();
    verify(dlqEventService, never()).persistDeadEvent(any(), any(), any());
  }

  @Test
  void listen_acknowledgesOnSuccess() throws Exception {
    when(cdcEventProcessor.process(any(), any())).thenReturn(true);

    dlqConsumer.listen("{}", "cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ", 0, 0L, acknowledgment);

    verify(acknowledgment).acknowledge();
    verify(dlqEventService, never()).persistDeadEvent(any(), any(), any());
  }

  @Test
  void listen_persistsDeadEvent_afterRetryExhaustion() throws Exception {
    when(cdcEventProcessor.process(any(), any())).thenThrow(new RuntimeException("mapping failed"));

    dlqConsumer.listen("{}", "cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ", 0, 0L, acknowledgment);

    verify(dlqEventService).persistDeadEvent(eq("cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ"), eq("{}"), any());
    verify(acknowledgment).acknowledge();
  }
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.DLQConsumerUnitTest" -Dgroups=unit
```

Expected: FAIL — `DLQConsumer` does not exist.

- [ ] **Step 3: Create DLQEventService**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQEventService.java
package com.egov.ecusthaison.cdc.dlq;

import com.egov.ecutoms.entity.DeadLetterEvent;
import com.egov.ecutoms.repository.DeadLetterEventRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Slf4j
public class DLQEventService {

  @Autowired
  private DeadLetterEventRepository repository;

  @Transactional(propagation = Propagation.REQUIRES_NEW)
  public DeadLetterEvent persistDeadEvent(String topic, String payload, String errorMessage) {
    DeadLetterEvent event = new DeadLetterEvent();
    event.setTopic(topic);
    event.setPayload(payload);
    event.setErrorMessage(errorMessage);
    event.setCreatedAt(LocalDateTime.now());
    DeadLetterEvent saved = repository.save(event);
    log.warn("Persisted dead letter event id={} from topic={}", saved.getId(), topic);
    return saved;
  }

  @Transactional
  public void markResolved(Long eventId) {
    repository.findById(eventId).ifPresent(event -> {
      event.setResolvedAt(LocalDateTime.now());
      repository.save(event);
    });
  }
}
```

- [ ] **Step 4: Create DLQConsumer**

Retry config: 3 attempts, 2s between retries. These can be externalized to properties later if needed.

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/DLQConsumer.java
package com.egov.ecusthaison.cdc.dlq;

import com.egov.ecusthaison.cdc.processor.CDCEventProcessor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;

/**
 * Consumes from *.DLQ topics. Retries up to maxAttempts times,
 * then persists unprocessable events to the dead_letter_event table.
 */
@Service
@Slf4j
public class DLQConsumer {

  private static final int MAX_ATTEMPTS = 3;
  private static final long RETRY_DELAY_MS = 2000;

  @Autowired
  private CDCEventProcessor cdcEventProcessor;

  @Autowired
  private DLQEventService dlqEventService;

  @KafkaListener(topicPattern = "${kafka.cdc.dlq.topic-pattern:.*\\.DLQ}",
      groupId = "${spring.kafka.consumer.group-id}-dlq",
      containerFactory = "kafkaListenerContainerFactory")
  public void listen(
      @Payload(required = false) String message,
      @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
      @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
      @Header(KafkaHeaders.OFFSET) long offset,
      Acknowledgment acknowledgment) {
    if (message == null || message.isBlank()) {
      acknowledgment.acknowledge();
      return;
    }

    // Strip .DLQ suffix to get original topic for processor
    String originalTopic = topic.endsWith(".DLQ")
        ? topic.substring(0, topic.length() - 4)
        : topic;

    Exception lastError = null;
    for (int attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      try {
        cdcEventProcessor.process(message, originalTopic);
        acknowledgment.acknowledge();
        log.info("DLQ retry succeeded on attempt {} for topic={}, offset={}", attempt, topic, offset);
        return;
      } catch (Exception e) {
        lastError = e;
        log.warn("DLQ retry attempt {}/{} failed for topic={}: {}", attempt, MAX_ATTEMPTS, topic, e.getMessage());
        if (attempt < MAX_ATTEMPTS) {
          try {
            Thread.sleep(RETRY_DELAY_MS);
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            break;
          }
        }
      }
    }

    // All retries exhausted — persist as dead event
    dlqEventService.persistDeadEvent(topic, message,
        lastError != null ? lastError.getMessage() : "Unknown error after " + MAX_ATTEMPTS + " attempts");
    acknowledgment.acknowledge();
  }
}
```

- [ ] **Step 5: Run tests to verify passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.DLQConsumerUnitTest" -Dgroups=unit
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/dlq/ \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/dlq/
git commit -m "feat: add DLQ consumer with retry and dead event persistence"
```

---

### Task 7: DLQController (replay endpoint)

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/DLQController.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/DLQControllerUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/DLQControllerUnitTest.java
package com.egov.ecusthaison.controller;

import com.egov.ecusthaison.cdc.dlq.DLQEventService;
import com.egov.ecusthaison.cdc.processor.CDCEventProcessor;
import com.egov.ecutoms.entity.DeadLetterEvent;
import com.egov.ecutoms.repository.DeadLetterEventRepository;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class DLQControllerUnitTest {

  @Mock
  private DeadLetterEventRepository repository;

  @Mock
  private CDCEventProcessor cdcEventProcessor;

  @Mock
  private DLQEventService dlqEventService;

  @InjectMocks
  private DLQController controller;

  @Test
  void replay_returns404_whenEventNotFound() {
    when(repository.findById(99L)).thenReturn(Optional.empty());

    ResponseEntity<?> response = controller.replay(99L);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
  }

  @Test
  void replay_returns200_andMarksResolved_onSuccess() throws Exception {
    DeadLetterEvent event = new DeadLetterEvent();
    event.setId(1L);
    event.setTopic("cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ");
    event.setPayload("{}");
    when(repository.findById(1L)).thenReturn(Optional.of(event));
    when(cdcEventProcessor.process(any(), any())).thenReturn(true);

    ResponseEntity<?> response = controller.replay(1L);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    verify(dlqEventService).markResolved(1L);
  }

  @Test
  void replay_returns500_onProcessingError() throws Exception {
    DeadLetterEvent event = new DeadLetterEvent();
    event.setId(2L);
    event.setTopic("cdc-dev-ecus.ECUS5VNACCS.dbo.SNUOC.DLQ");
    event.setPayload("{}");
    when(repository.findById(2L)).thenReturn(Optional.of(event));
    when(cdcEventProcessor.process(any(), any())).thenThrow(new RuntimeException("still failing"));

    ResponseEntity<?> response = controller.replay(2L);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.INTERNAL_SERVER_ERROR);
  }
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.DLQControllerUnitTest" -Dgroups=unit
```

Expected: FAIL — `DLQController` does not exist.

- [ ] **Step 3: Create DLQController**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/DLQController.java
package com.egov.ecusthaison.controller;

import com.egov.ecusthaison.cdc.dlq.DLQEventService;
import com.egov.ecusthaison.cdc.processor.CDCEventProcessor;
import com.egov.ecutoms.entity.DeadLetterEvent;
import com.egov.ecutoms.repository.DeadLetterEventRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequestMapping("/api/dlq")
@Slf4j
public class DLQController {

  @Autowired
  private DeadLetterEventRepository repository;

  @Autowired
  private CDCEventProcessor cdcEventProcessor;

  @Autowired
  private DLQEventService dlqEventService;

  @PostMapping("/replay/{id}")
  public ResponseEntity<?> replay(@PathVariable Long id) {
    Optional<DeadLetterEvent> eventOpt = repository.findById(id);
    if (eventOpt.isEmpty()) {
      return ResponseEntity.notFound().build();
    }
    DeadLetterEvent event = eventOpt.get();
    // Strip .DLQ suffix to get original topic
    String originalTopic = event.getTopic().endsWith(".DLQ")
        ? event.getTopic().substring(0, event.getTopic().length() - 4)
        : event.getTopic();
    try {
      cdcEventProcessor.process(event.getPayload(), originalTopic);
      dlqEventService.markResolved(id);
      return ResponseEntity.ok().build();
    } catch (Exception e) {
      log.error("Replay failed for dead letter event id={}: {}", id, e.getMessage(), e);
      return ResponseEntity.internalServerError().body(e.getMessage());
    }
  }
}
```

- [ ] **Step 4: Run tests to verify passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.DLQControllerUnitTest" -Dgroups=unit
./gradlew :datatp-egov-module-ecus-thaison:test -Dgroups=unit
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/DLQController.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/DLQControllerUnitTest.java
git commit -m "feat: add DLQ replay endpoint POST /api/dlq/replay/{id}"
```

---

## Phase 3 — Batch Error Retry

### File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/IEcusSingleMapper.java` | Add `supportedEntityClass()` |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistry.java` | Map entity class name → mapper bean |
| Create | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/RetryService.java` | Load failed records + re-route |
| Modify | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java` | Add POST /api/sync/jobs/{id}/retry-failures |
| Modify (×5) | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/partner/Ecus*Mapper.java` | Implement `supportedEntityClass()` |
| Create | `module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/RetryServiceUnitTest.java` | Unit tests for retry service |

**Which mappers implement IEcusSingleMapper and need `supportedEntityClass()`:**
- `EcusDTOKHAIMapper` → `DTOKHAIMD.class`
- `EcusDHANGMDDKMapper` → `DHANGMDDK.class`
- `EcusD_OLAMapper` → `D_OLA.class`
- `EcusD_OLA_HangMapper` → `D_OLA_Hang.class`
- `EcusD_OLA_ContainerMapper` → `D_OLA_Container.class`

Check if company/core mappers also implement `IEcusSingleMapper` — if so, add `supportedEntityClass()` there too (follow same pattern).

---

### Task 8: Extend IEcusSingleMapper + implement in all mappers

- [ ] **Step 1: Extend IEcusSingleMapper**

Open `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/IEcusSingleMapper.java`.

```java
package com.egov.ecusthaison.logic;

/**
 * Marker interface for mappers that process a single ECUS entity into eGov.
 * Called from the CDC flow (per-event, real-time) — each invocation runs in its own transaction.
 */
public interface IEcusSingleMapper<TSource> {
  void processSync(TSource ecusEntity);

  /**
   * Returns the ECUS entity class this mapper handles.
   * Used by EcusSingleMapperRegistry to route retry jobs to the correct mapper.
   */
  Class<TSource> supportedEntityClass();
}
```

- [ ] **Step 2: Run compile to see which mappers need updating**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava 2>&1 | grep "error:"
```

Expected: Compile errors listing all `IEcusSingleMapper` implementors missing `supportedEntityClass()`.

- [ ] **Step 3: Add `supportedEntityClass()` to each partner mapper**

For each mapper listed above, open the file and add one method. Example for `EcusDTOKHAIMapper.java`:

```java
// Add inside EcusDTOKHAIMapper class body, after the existing processSync() method:
@Override
public Class<DTOKHAIMD> supportedEntityClass() {
  return DTOKHAIMD.class;
}
```

Repeat for each mapper, substituting the correct entity class:
- `EcusDHANGMDDKMapper` → `DHANGMDDK.class`
- `EcusD_OLAMapper` → `D_OLA.class`
- `EcusD_OLA_HangMapper` (check actual entity class name in file) → correct class
- `EcusD_OLA_ContainerMapper` (check actual entity class name in file) → correct class
- Any company/core mappers that implement `IEcusSingleMapper`

- [ ] **Step 4: Verify build passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/IEcusSingleMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/
git commit -m "feat: add supportedEntityClass() to IEcusSingleMapper for retry routing"
```

---

### Task 9: EcusSingleMapperRegistry

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistry.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistryUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistryUnitTest.java
package com.egov.ecusthaison.sync.retry;

import com.egov.ecusthaison.entity.DTOKHAIMD;
import com.egov.ecusthaison.logic.IEcusSingleMapper;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@Tag("unit")
class EcusSingleMapperRegistryUnitTest {

  @Test
  void getMapper_returnsMapper_whenEntityClassMatches() {
    IEcusSingleMapper<DTOKHAIMD> mapper = mock(IEcusSingleMapper.class);
    when(mapper.supportedEntityClass()).thenAnswer(inv -> DTOKHAIMD.class);

    EcusSingleMapperRegistry registry = new EcusSingleMapperRegistry(List.of(mapper));

    Optional<IEcusSingleMapper<?>> result = registry.getMapper("DTOKHAIMD");

    assertThat(result).isPresent();
    assertThat(result.get()).isEqualTo(mapper);
  }

  @Test
  void getMapper_returnsEmpty_whenNoMatch() {
    EcusSingleMapperRegistry registry = new EcusSingleMapperRegistry(List.of());

    Optional<IEcusSingleMapper<?>> result = registry.getMapper("UNKNOWN_TABLE");

    assertThat(result).isEmpty();
  }
}
```

- [ ] **Step 2: Run to verify fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.EcusSingleMapperRegistryUnitTest" -Dgroups=unit
```

Expected: FAIL.

- [ ] **Step 3: Create EcusSingleMapperRegistry**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistry.java
package com.egov.ecusthaison.sync.retry;

import com.egov.ecusthaison.logic.IEcusSingleMapper;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Registry of all IEcusSingleMapper beans keyed by their supported entity class simple name.
 * Used by RetryService to route retry jobs to the correct mapper.
 */
@Component
public class EcusSingleMapperRegistry {

  private final Map<String, IEcusSingleMapper<?>> mappersByEntityName;

  public EcusSingleMapperRegistry(List<IEcusSingleMapper<?>> mappers) {
    this.mappersByEntityName = mappers.stream()
        .collect(Collectors.toMap(
            m -> m.supportedEntityClass().getSimpleName(),
            Function.identity(),
            (a, b) -> a));  // keep first on collision
  }

  public Optional<IEcusSingleMapper<?>> getMapper(String entityClassSimpleName) {
    return Optional.ofNullable(mappersByEntityName.get(entityClassSimpleName));
  }
}
```

- [ ] **Step 4: Run test to verify passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.EcusSingleMapperRegistryUnitTest" -Dgroups=unit
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistry.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/EcusSingleMapperRegistryUnitTest.java
git commit -m "feat: add EcusSingleMapperRegistry for retry entity-to-mapper routing"
```

---

### Task 10: RetryService

**Files:**
- Create: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/RetryService.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/RetryServiceUnitTest.java`

**How retry works:**
1. Load failed `MigrationRecord` rows by jobId (status = FAILED).
2. Each record has `targetEntity` (e.g., "DTOKHAIMD") and `sourceData` (JSON of original entity).
3. Look up the right `IEcusSingleMapper` from `EcusSingleMapperRegistry`.
4. Deserialize `sourceData` to the mapper's `supportedEntityClass()`.
5. Call `processSync(entity)` — it is already idempotent (lookup-or-create).
6. Track results in a new `MigrationJob` with type `RETRY_FAILED`.

- [ ] **Step 1: Write failing test**

```java
// module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/RetryServiceUnitTest.java
package com.egov.ecusthaison.sync.retry;

import com.egov.ecusthaison.entity.DTOKHAIMD;
import com.egov.ecusthaison.logic.IEcusSingleMapper;
import com.egov.ecusthaison.sync.SyncResult;
import com.egov.ecutoms.entity.MigrationRecord;
import com.egov.ecutoms.entity.MigrationRecordStatus;
import com.egov.ecutoms.repository.MigrationRecordRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class RetryServiceUnitTest {

  @Mock
  private MigrationRecordRepository recordRepository;

  @Mock
  private EcusSingleMapperRegistry mapperRegistry;

  @Mock
  private ObjectMapper objectMapper;

  @InjectMocks
  private RetryService retryService;

  @Test
  void retryFailedRecords_returnsZeroSuccess_whenNoFailedRecords() {
    when(recordRepository.findByMigrationJobIdAndStatus(eq(1L), eq(MigrationRecordStatus.FAILED), any()))
        .thenReturn(new PageImpl<>(List.of()));

    SyncResult result = retryService.retryFailedRecords(1L);

    assertThat(result.getTotalRecords()).isZero();
  }

  @Test
  void retryFailedRecords_skipsRecord_whenNoMapperFound() {
    MigrationRecord record = new MigrationRecord();
    record.setTargetEntity("UNKNOWN_ENTITY");
    record.setRecordIdentifier("42");
    record.setSourceData(Map.of("id", "42"));
    when(recordRepository.findByMigrationJobIdAndStatus(eq(1L), eq(MigrationRecordStatus.FAILED), any()))
        .thenReturn(new PageImpl<>(List.of(record)));
    when(mapperRegistry.getMapper("UNKNOWN_ENTITY")).thenReturn(Optional.empty());

    SyncResult result = retryService.retryFailedRecords(1L);

    assertThat(result.getFailedCount()).isEqualTo(1);
  }
}
```

- [ ] **Step 2: Run to verify fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.RetryServiceUnitTest" -Dgroups=unit
```

Expected: FAIL.

- [ ] **Step 3: Create RetryService**

```java
// module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/RetryService.java
package com.egov.ecusthaison.sync.retry;

import com.egov.ecusthaison.logic.IEcusSingleMapper;
import com.egov.ecusthaison.sync.SyncResult;
import com.egov.ecutoms.entity.MigrationRecord;
import com.egov.ecutoms.entity.MigrationRecordStatus;
import com.egov.ecutoms.repository.MigrationRecordRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Slf4j
public class RetryService {

  @Autowired
  private MigrationRecordRepository recordRepository;

  @Autowired
  private EcusSingleMapperRegistry mapperRegistry;

  @Autowired
  private ObjectMapper objectMapper;

  @SuppressWarnings("unchecked")
  public SyncResult retryFailedRecords(Long jobId) {
    Page<MigrationRecord> failedPage = recordRepository.findByMigrationJobIdAndStatus(
        jobId, MigrationRecordStatus.FAILED, Pageable.unpaged());
    List<MigrationRecord> failedRecords = failedPage.getContent();

    LocalDateTime start = LocalDateTime.now();
    int success = 0;
    int failed = 0;
    SyncResult.SyncResultBuilder resultBuilder = SyncResult.builder()
        .syncName("RETRY_JOB_" + jobId)
        .startTime(start);

    for (MigrationRecord record : failedRecords) {
      String entityName = record.getTargetEntity();
      Optional<IEcusSingleMapper<?>> mapperOpt = mapperRegistry.getMapper(entityName);

      if (mapperOpt.isEmpty()) {
        log.warn("No mapper found for entity={}, recordId={}. Skipping retry.", entityName, record.getRecordIdentifier());
        failed++;
        resultBuilder.addError(record.getRecordIdentifier(), entityName,
            new RuntimeException("No mapper registered for entity: " + entityName));
        continue;
      }

      IEcusSingleMapper mapper = mapperOpt.get();
      try {
        Object entity = objectMapper.convertValue(record.getSourceData(), mapper.supportedEntityClass());
        mapper.processSync(entity);
        success++;
      } catch (Exception e) {
        failed++;
        log.error("Retry failed for entity={}, recordId={}: {}", entityName, record.getRecordIdentifier(), e.getMessage());
        resultBuilder.addError(record.getRecordIdentifier(), entityName, e);
      }
    }

    return resultBuilder
        .endTime(LocalDateTime.now())
        .totalRecords(failedRecords.size())
        .successCount(success)
        .failedCount(failed)
        .skippedCount(0)
        .build();
  }
}
```

- [ ] **Step 4: Run test to verify passes**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.RetryServiceUnitTest" -Dgroups=unit
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/sync/retry/ \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/sync/retry/RetryServiceUnitTest.java
git commit -m "feat: add RetryService for re-processing failed MigrationRecord entries"
```

---

### Task 11: Retry endpoint in SyncJobController

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java`
- Modify: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java`

- [ ] **Step 1: Add retry test case to existing test class**

Open `SyncJobControllerUnitTest.java` and add:

```java
// Add to existing SyncJobControllerUnitTest — new field and test method

@Mock
private RetryService retryService;

@Test
void retryFailures_returns200_withSyncResult() {
  SyncResult result = SyncResult.builder()
      .syncName("RETRY_JOB_1")
      .totalRecords(3)
      .successCount(3)
      .failedCount(0)
      .skippedCount(0)
      .startTime(LocalDateTime.now())
      .endTime(LocalDateTime.now())
      .build();
  when(retryService.retryFailedRecords(1L)).thenReturn(result);

  ResponseEntity<?> response = controller.retryFailures(1L);

  assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
}
```

- [ ] **Step 2: Run to verify fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "*.SyncJobControllerUnitTest" -Dgroups=unit
```

Expected: FAIL (compile error or test failure — `retryFailures` method missing from controller).

- [ ] **Step 3: Add retry endpoint to SyncJobController**

Open `SyncJobController.java` and add:

```java
// New field (after existing @Autowired fields):
@Autowired
private RetryService retryService;

// New endpoint method:
@PostMapping("/{jobId}/retry-failures")
public ResponseEntity<SyncResult> retryFailures(@PathVariable Long jobId) {
  SyncResult result = retryService.retryFailedRecords(jobId);
  return ResponseEntity.ok(result);
}
```

- [ ] **Step 4: Run all unit tests**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test -Dgroups=unit
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/controller/SyncJobController.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/controller/SyncJobControllerUnitTest.java
git commit -m "feat: add POST /api/sync/jobs/{jobId}/retry-failures endpoint"
```

---

## Final Verification

- [ ] **Run full test suite**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test
./gradlew :datatp-egov-module-ecutoms:test
```

Expected: All tests PASS, no regressions.

- [ ] **Verify build**

```bash
./gradlew build
```

Expected: BUILD SUCCESSFUL.
