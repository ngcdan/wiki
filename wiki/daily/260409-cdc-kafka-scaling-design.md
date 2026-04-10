# CDC Kafka Scaling Design

**Date:** 2026-04-09
**Status:** Approved
**Scope:** CDC consumer only (eCUS -> eGov direction)

---

## Problem

The CDC pipeline uses a single `CommonCDCListener` with `concurrency=1`, processing all ~28 table topics sequentially on one thread. When data volume increases, high-volume tables (DTOKHAIMD) block low-volume reference tables (SNUOC), causing consumer lag to grow unboundedly.

Additionally, `EntityLockManager` uses `ConcurrentHashMap.clear()` when exceeding 100k entries, which deletes all active locks and creates race conditions between handlers sharing the same entity (e.g., DTOKHAIMD and DTOKHAIMD_VNACCS both updating the same Declaration).

## Current Architecture

```
eCUS SQL Server (Debezium CDC)
  -> Kafka topics: cdc-{ENV}-ecus.{SOURCE}.dbo.{TABLE}  (~28 topics, 1 partition each)
  -> CommonCDCListener (topicPattern: cdc-{ENV}-ecus.*, concurrency=1)
    -> CDCEventHandlerRegistry.getHandler(table)
      -> DTOKHAIMDCDCHandler / SNUOCCDCHandler / ... (28 handlers)
        -> processSync() -> PostgreSQL
```

**Key components:**

| Component | File | Role |
|-----------|------|------|
| CommonCDCListener | `module/ecus-thaison/.../cdc/listener/CommonCDCListener.java` | Single @KafkaListener with topic pattern, routes to handlers |
| CDCEventHandlerRegistry | `module/ecus-thaison/.../cdc/handler/CDCEventHandlerRegistry.java` | Auto-discovers handler beans, maps table name to handler |
| CDCEventHandler (interface) | `module/ecus-thaison/.../cdc/handler/CDCEventHandler.java` | Handler contract: handleCreate/Update/Delete/Snapshot |
| EntityLockManager | `module/ecus-thaison/.../cdc/lock/EntityLockManager.java` | Per-entity locking via ConcurrentHashMap |
| KafkaConfig | `module/ecus-thaison/.../config/KafkaConfig.java` | Consumer/producer factory, error handler, container factory |
| KafkaDLQConfig | `module/ecus-thaison/.../config/KafkaDLQConfig.java` | Auto-creates DLQ topics (skips wildcards) |

**Table volume tiers:**

| Tier | Tables | Characteristics |
|------|--------|-----------------|
| High-volume | DTOKHAIMD, DTOKHAIMD_VNACCS, DTOKHAIMD_VNACCS2, DHANGMDDK | Declarations + goods, continuous changes, ordering matters |
| Medium | DLOGINFO, DMSGOUTREP, REPORTSEXCEL | Logs/reports |
| Low (reference) | SNUOC, SHAIQUAN, SDONVI, SDVT, SCUAKHAU, SNGTE... (~20 tables) | Master data, rarely changes |

## Identified Issues

### 1. Single-thread bottleneck (CRITICAL)

- `kafka.cdc.concurrency: 1` — all CDC events processed sequentially
- Debezium creates 1 topic per table, each with 1 partition (default)
- ~28 topics but only 1 thread — high-volume DTOKHAIMD blocks reference table SNUOC

### 2. EntityLockManager race condition (HIGH)

- `locks.clear()` when > 100k entries deletes ALL active locks
- Thread A may be inside `synchronized(lock)` when Thread B clears the map
- Thread C then gets a NEW lock object for the same key — two threads now hold different locks for the same entity
- Lock is JVM-local — does not work across multiple application instances

### 3. EntityLockManager memory leak (MEDIUM)

- ConcurrentHashMap only grows, never evicts unused entries
- Entries accumulate until hitting 100k threshold, then bulk clear

### 4. DLQ wildcard skip (LOW)

- KafkaDLQConfig skips wildcard topic patterns
- DLQ topics rely on `admin.auto-create: true` with broker defaults
- Not a blocking issue — auto-create works, just uses default retention/partition config

## Solution: Approach A — Increase Concurrency + Fix EntityLockManager

Chosen over dedicated-listener-per-table (Approach B) and dynamic-consumer-per-topic (Approach C) because it delivers ~80% of the benefit with ~20% of the effort. Can evolve to Approach B later if a specific table needs dedicated tuning.

### Change 1: Increase concurrency to 30

**File:** `server/src/main/resources/application.yaml`

**Change:** `kafka.cdc.concurrency: 1` -> `kafka.cdc.concurrency: 30`

**How it works:**
- `ConcurrentKafkaListenerContainerFactory.setConcurrency(30)` creates 30 KafkaConsumer threads in the same consumer group
- Kafka assigns each partition (= each topic, since 1 partition per topic) to one thread
- Result: each table is processed by its own dedicated thread — effectively "1 topic = 1 consumer"
- Surplus threads (30 - 28 = 2) remain idle with negligible resource cost
- Ordering within the same partition is preserved (1 thread per partition)

**No code changes required** — CommonCDCListener works identically, just runs on more threads.

### Change 2: Fix EntityLockManager with Caffeine cache

**File:** `module/ecus-thaison/src/main/java/com/egov/ecusthaison/cdc/lock/EntityLockManager.java`

**Change:** Replace `ConcurrentHashMap` + `clear()` with Caffeine cache.

**Before (current):**
```java
private final ConcurrentHashMap<String, Object> locks = new ConcurrentHashMap<>();

public Object getLock(String lockKey) {
    if (locks.size() > MAX_LOCK_SIZE) {
        locks.clear();  // BUG: deletes active locks
    }
    return locks.computeIfAbsent(lockKey, k -> new Object());
}
```

**After (proposed):**
```java
private final Cache<String, Object> locks = Caffeine.newBuilder()
    .maximumSize(50_000)
    .expireAfterAccess(5, TimeUnit.MINUTES)
    .build();

public Object getLock(String lockKey) {
    return locks.get(lockKey, k -> new Object());
}
```

**Why this fixes the issues:**
- No `clear()` — Caffeine evicts individual entries when they expire or exceed max size
- `expireAfterAccess(5, MINUTES)` — entries actively being used (inside synchronized block) count as "accessed" and won't be evicted
- `maximumSize(50_000)` — bounded memory, LRU eviction for least-used entries
- Caffeine dependency already exists in the project (`module/ecutoms` uses it for CacheConfig)

### No changes needed

| Component | Reason |
|-----------|--------|
| CommonCDCListener | Works as-is with higher concurrency |
| CDCEventHandler interface | No change |
| All 28 handler implementations | No change |
| KafkaConfig (factory, error handler) | `cdcConcurrency` field already reads from config |
| KafkaDLQConfig | `admin.auto-create: true` handles DLQ topic creation |
| Consumer group ID | Same group, more threads |

## Pre-deployment Checklist

- [ ] Verify each CDC topic has >= 1 partition via Kafka admin
- [ ] Confirm Debezium message key is set to primary key (ensures same entity always goes to same partition)
- [ ] Monitor consumer lag after deployment — should decrease significantly
- [ ] Watch for any ordering issues in high-volume tables during first 24h

## Future Evolution

If a specific table (e.g., DTOKHAIMD) needs more throughput than 1 thread:
1. Increase that topic's partition count in Kafka
2. Split into dedicated listener with its own consumer group and higher concurrency (Approach B, tier-based)
3. EntityLockManager still ensures cross-handler entity safety within the same JVM
