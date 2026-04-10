# CDC Kafka Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scale CDC consumer to process each topic on a dedicated thread and fix EntityLockManager race condition.

**Architecture:** Increase `ConcurrentKafkaListenerContainerFactory` concurrency from 1 to 30 so Kafka assigns each topic partition to its own consumer thread. Replace `ConcurrentHashMap` + `clear()` in `EntityLockManager` with Caffeine cache for safe per-entry eviction.

**Tech Stack:** Java 21, Spring Kafka 3.3.10, Caffeine (already in project)

**Spec:** `~/dev/wiki/wiki/daily/260409-cdc-kafka-scaling-design.md`

---

## Task 1: Fix EntityLockManager — Replace ConcurrentHashMap with Caffeine

**Files:**
- Modify: `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/lock/EntityLockManager.java`
- Create: `module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/lock/EntityLockManagerUnitTest.java`

- [ ] **Step 1: Write failing test for EntityLockManager**

```java
package com.egov.ecusthaison.cdc.lock;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@Tag("unit")
class EntityLockManagerUnitTest {

    private final EntityLockManager lockManager = new EntityLockManager();

    @Test
    void getLock_sameKey_returnsSameObject() {
        Object lock1 = lockManager.getLock("Declaration:1:100");
        Object lock2 = lockManager.getLock("Declaration:1:100");
        assertThat(lock1).isSameAs(lock2);
    }

    @Test
    void getLock_differentKeys_returnsDifferentObjects() {
        Object lock1 = lockManager.getLock("Declaration:1:100");
        Object lock2 = lockManager.getLock("Declaration:1:200");
        assertThat(lock1).isNotSameAs(lock2);
    }

    @Test
    void getLock_neverThrowsUnderLoad() {
        // Verify no NPE or exception when many keys are created
        for (int i = 0; i < 10_000; i++) {
            Object lock = lockManager.getLock("Key:" + i);
            assertThat(lock).isNotNull();
        }
    }
}
```

- [ ] **Step 2: Run test to verify it passes with current impl (baseline)**

Run: `./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.cdc.lock.EntityLockManagerUnitTest" -i`

Expected: PASS (current impl satisfies these basic contracts)

- [ ] **Step 3: Rewrite EntityLockManager with Caffeine**

Replace full content of `EntityLockManager.java`:

```java
package com.egov.ecusthaison.cdc.lock;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * Per-entity lock manager for CDC processing.
 * Ensures that concurrent CDC events targeting the same EGOV entity
 * (e.g., DTOKHAIMD and DTOKHAIMD_VNACCS both updating Declaration#123)
 * are processed sequentially, while different entities run in parallel.
 *
 * Uses Caffeine cache with TTL eviction instead of manual clear()
 * to avoid deleting locks that are actively held by other threads.
 */
@Slf4j
@Component
public class EntityLockManager {

    private final Cache<String, Object> locks = Caffeine.newBuilder()
        .maximumSize(50_000)
        .expireAfterAccess(5, TimeUnit.MINUTES)
        .build();

    public Object getLock(String lockKey) {
        return locks.get(lockKey, k -> new Object());
    }
}
```

- [ ] **Step 4: Run tests to verify they still pass**

Run: `./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.cdc.lock.EntityLockManagerUnitTest" -i`

Expected: PASS

- [ ] **Step 5: Run existing CDC tests to verify no regression**

Run: `./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.cdc.handler.CDCLoopPreventionUnitTest" -i`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/lock/EntityLockManager.java
git add module/ecus-thaison/src/test/java/com/egov/ecusthaison/cdc/lock/EntityLockManagerUnitTest.java
git commit -m "fix(cdc): replace EntityLockManager ConcurrentHashMap with Caffeine cache

clear() on ConcurrentHashMap deleted actively-held locks causing race
conditions between DTOKHAIMD and DTOKHAIMD_VNACCS handlers.
Caffeine evicts per-entry with TTL, never bulk-deletes active locks."
```

---

## Task 2: Increase CDC concurrency

**Files:**
- Modify: `server/src/main/resources/application.yaml:167`

- [ ] **Step 1: Change concurrency from 1 to 30**

In `application.yaml`, line 167:

```yaml
# Before
kafka:
  cdc:
    topics: cdc-${env.kafka.topic.env}-ecus.*
    concurrency: 1

# After
kafka:
  cdc:
    topics: cdc-${env.kafka.topic.env}-ecus.*
    concurrency: 30
```

- [ ] **Step 2: Verify build compiles**

Run: `./gradlew :datatp-egov-cc-server:compileJava`

Expected: BUILD SUCCESSFUL

- [ ] **Step 3: Commit**

```bash
git add server/src/main/resources/application.yaml
git commit -m "perf(cdc): increase consumer concurrency from 1 to 30

Each CDC topic (1 partition) gets its own consumer thread.
High-volume tables (DTOKHAIMD) no longer block reference tables (SNUOC)."
```

---

## Task 3: Verify full build

- [ ] **Step 1: Run full test suite**

Run: `./gradlew :datatp-egov-module-ecus-thaison:test`

Expected: All tests PASS

- [ ] **Step 2: Run full build**

Run: `./gradlew build`

Expected: BUILD SUCCESSFUL
