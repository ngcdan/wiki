# CDC ClientContext + MapObject Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace CDCTenantContext (ThreadLocal) with explicit ClientContext param and change CDCEvent\<Map\<String, Object\>\> to CDCEvent\<MapObject\> across the CDC handler framework.

**Architecture:** CDCListener creates a ClientContext with company info, converts CDCEvent to MapObject-based, and passes both to handlers explicitly. CDCTenantContext is deleted entirely.

**Tech Stack:** Java 21, Spring Boot, Kafka, Jackson, net.datatp.security.client.ClientContext, net.datatp.util.ds.MapObject

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260415-cdc-clientcontext-refactor.md`

---

## File Structure

| Action | File | Responsibility |
|--------|------|---------------|
| Modify | `of1-core/.../ClientContext.java` | Add @Setter to companyLabel |
| Modify | `module/core/.../handler/CDCEventHandler.java` | New interface signatures + stamp() utility |
| Modify | `module/core/.../listener/CDCListener.java` | Create ClientContext, convert event, remove CDCTenantContext |
| Delete | `module/core/.../context/CDCTenantContext.java` | Remove entirely |
| Modify | `module/transaction/.../cdc/CDCLookupSupport.java` | Add ClientContext param |
| Modify | `module/transaction/.../cdc/CDCLookupSupportUnitTest.java` | Update test to pass ClientContext |
| Modify | 12 handler files in `module/transaction/.../cdc/` | Signature + CDCTenantContext replacement |
| Modify | `module/settings/.../cdc/ExchangeRateCDCHandler.java` | Signature only |
| Modify | `module/partner/.../cdc/PartnersCDCHandler.java` | Signature only |

---

## Task 1: Update ClientContext in of1-core

**Files:**
- Modify: `/Users/nqcdan/OF1/forgejo/of1-platform/of1-core/module/common/src/main/java/net/datatp/security/client/ClientContext.java:42-43`

- [ ] **Step 1: Add @Setter to companyLabel**

Change line 42-43 from:
```java
  @Getter
  public  String     companyLabel ;
```
to:
```java
  @Getter @Setter
  public  String     companyLabel ;
```

- [ ] **Step 2: Build of1-core to verify**

Run: `cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-core && gradle compileJava`
Expected: BUILD SUCCESSFUL

---

## Task 2: Update CDCEventHandler Interface

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/cdc/handler/CDCEventHandler.java`

- [ ] **Step 1: Update interface with ClientContext param + MapObject + stamp utility**

Replace entire file content with:

```java
package of1.fms.core.cdc.handler;

import java.util.Date;
import net.datatp.module.data.db.entity.CompanyEntity;
import net.datatp.module.data.db.entity.PersistableEntity;
import net.datatp.security.client.ClientContext;
import net.datatp.util.ds.MapObject;
import of1.fms.core.cdc.model.CDCEvent;

public interface CDCEventHandler {

  String getTableName();

  void handleCreate(ClientContext ctx, CDCEvent<MapObject> event);

  void handleUpdate(ClientContext ctx, CDCEvent<MapObject> event);

  void handleDelete(ClientContext ctx, CDCEvent<MapObject> event);

  void handleSnapshot(ClientContext ctx, CDCEvent<MapObject> event);

  static <T extends PersistableEntity<?>> T stamp(ClientContext ctx, T entity) {
    entity.set(ctx.getLoginId(), new Date());
    if (entity instanceof CompanyEntity ce && ce.getCompanyId() == null) {
      ce.setCompanyId(ctx.getCompanyId());
    }
    return entity;
  }
}
```

- [ ] **Step 2: Verify compiles (will fail — handlers not yet updated, that's expected)**

Run: `gradle :module-core:compileJava` — expected: compile success (interface only, handlers are in other modules)

---

## Task 3: Update CDCListener

**Files:**
- Modify: `module/core/src/main/java/of1/fms/core/cdc/listener/CDCListener.java`

- [ ] **Step 1: Update imports**

Remove:
```java
import of1.fms.core.cdc.context.CDCTenantContext;
```

Add:
```java
import net.datatp.security.client.ClientContext;
import net.datatp.util.ds.MapObject;
```

- [ ] **Step 2: Replace CDCTenantContext.set() with ClientContext creation in listen() method**

Replace lines 100-102:
```java
    String tableName = null;
    String operation = null;
    CDCTenantContext.set(companyCode, companyInfo.id(), companyInfo.label());
```

With:
```java
    String tableName = null;
    String operation = null;
    ClientContext ctx = new ClientContext("default", "cdc-sync", "localhost");
    ctx.setCompanyId(companyInfo.id());
    ctx.setCompanyCode(companyCode);
    ctx.setCompanyLabel(companyInfo.label());
```

- [ ] **Step 3: Update event deserialization + handler invocation**

Replace lines 104-124 (inside try block) with:

```java
    try {
      CDCEvent<Map<String, Object>> rawEvent = objectMapper.readValue(
        message,
        objectMapper.getTypeFactory().constructParametricType(CDCEvent.class, Map.class));

      tableName = rawEvent.getSource().getTable();
      operation = rawEvent.getOperation();

      log.info("[CDC_RECEIVED] table={} op={} offset={} company={}", tableName, operation, offset, companyCode);

      List<CDCEventHandler> handlers = handlerRegistry.getHandlers(tableName);
      if (handlers == null || handlers.isEmpty()) {
        acknowledgment.acknowledge();
        return;
      }

      CDCEvent<MapObject> cdcEvent = toMapObjectEvent(rawEvent);

      long startTime = System.currentTimeMillis();

      for (CDCEventHandler handler : handlers) {
        invokeHandlerWithRetry(handler, ctx, cdcEvent, operation, tableName, offset, companyCode);
      }
```

- [ ] **Step 4: Update invokeHandlerWithRetry signature and switch block**

Replace the method (lines 149-174):

```java
  private void invokeHandlerWithRetry(CDCEventHandler handler, ClientContext ctx, CDCEvent<MapObject> cdcEvent,
      String operation, String tableName, long offset, String companyCode) {
    for (int attempt = 1; attempt <= maxRetryAttempts; attempt++) {
      try {
        switch (operation) {
          case "c" -> handler.handleCreate(ctx, cdcEvent);
          case "u" -> handler.handleUpdate(ctx, cdcEvent);
          case "d" -> handler.handleDelete(ctx, cdcEvent);
          case "r" -> handler.handleSnapshot(ctx, cdcEvent);
          default  -> log.warn("Unknown CDC operation: {} for table: {}", operation, tableName);
        }
        return;
      } catch (Exception e) {
        boolean isStaleState = isOptimisticLockException(e);
        if (isStaleState && attempt < maxRetryAttempts) {
          log.warn("[CDC_RETRY] table={} op={} handler={} offset={} attempt={}/{} (optimistic lock conflict)",
              tableName, operation, handler.getClass().getSimpleName(), offset, attempt, maxRetryAttempts);
          try { Thread.sleep(retryBackoffMs * attempt); } catch (InterruptedException ie) { Thread.currentThread().interrupt(); return; }
        } else {
          log.error("[CDC_HANDLER_ERROR] table={} op={} handler={} offset={} company={} attempt={} error={}",
              tableName, operation, handler.getClass().getSimpleName(), offset, companyCode, attempt, e.getMessage(), e);
          return;
        }
      }
    }
  }
```

- [ ] **Step 5: Remove CDCTenantContext.clear() from finally block**

Replace lines 143-146:
```java
    } finally {
      CDCTenantContext.clear();
    }
```

With:
```java
    }
```

- [ ] **Step 6: Add toMapObjectEvent() helper method**

Add before `parseCompanyCode()` method:

```java
  private CDCEvent<MapObject> toMapObjectEvent(CDCEvent<Map<String, Object>> raw) {
    CDCEvent<MapObject> event = new CDCEvent<>();
    event.setBefore(raw.getBefore() != null ? new MapObject(raw.getBefore()) : null);
    event.setAfter(raw.getAfter() != null ? new MapObject(raw.getAfter()) : null);
    event.setSource(raw.getSource());
    event.setOperation(raw.getOperation());
    event.setTimestamp(raw.getTimestamp());
    event.setTransaction(raw.getTransaction());
    return event;
  }
```

- [ ] **Step 7: Remove unused Map import if no longer needed**

Check if `java.util.Map` is still used elsewhere in file. If only used for deserialization (still needed for `objectMapper.readValue`), keep it.

---

## Task 4: Update CDCLookupSupport

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/CDCLookupSupport.java`
- Modify: `module/transaction/src/test/java/of1/fms/module/transaction/cdc/CDCLookupSupportUnitTest.java`

- [ ] **Step 1: Update CDCLookupSupport — add ClientContext param to methods that use CDCTenantContext**

In `CDCLookupSupport.java`:

1. Remove import: `import of1.fms.core.cdc.context.CDCTenantContext;`
2. Add import: `import net.datatp.security.client.ClientContext;`
3. Change `resolveClient()` method signature — add `ClientContext ctx` as first param. Replace line 41 `String companyCode = CDCTenantContext.getCompanyCode();` with `String companyCode = ctx.getCompanyCode();`
4. Change `resolveHandlingAgent()` method signature — add `ClientContext ctx` as first param. Replace line 65 `String companyCode = CDCTenantContext.getCompanyCode();` with `String companyCode = ctx.getCompanyCode();`

- [ ] **Step 2: Update CDCLookupSupportUnitTest**

In `CDCLookupSupportUnitTest.java`:

1. Remove import: `import of1.fms.core.cdc.context.CDCTenantContext;`
2. Add import: `import net.datatp.security.client.ClientContext;`
3. Remove all `MockedStatic<CDCTenantContext>` usage
4. Create a test `ClientContext` fixture:
   ```java
   private ClientContext ctx;

   @BeforeEach
   void setUp() {
     ctx = new ClientContext("default", "cdc-sync", "localhost");
     ctx.setCompanyCode("BEE_VN");
     ctx.setCompanyId(1L);
   }
   ```
5. Update all test method calls to pass `ctx` as first argument to `resolveClient(ctx, ...)` and `resolveHandlingAgent(ctx, ...)`

---

## Task 5: Update Handlers — Group A (CDCTenantContext.stamp + getCompanyXxx)

These handlers use both `CDCTenantContext.stamp()` AND `CDCTenantContext.getCompanyCode()/getCompanyId()/getCompanyLabel()`.

For EACH handler in this group, apply ALL of these changes:

1. Remove import: `import of1.fms.core.cdc.context.CDCTenantContext;`
2. Add imports: `import net.datatp.security.client.ClientContext;` and `import net.datatp.util.ds.MapObject;`
3. Update all 4 method signatures: `CDCEvent<Map<String, Object>> event` → `ClientContext ctx, CDCEvent<MapObject> event`
4. Replace `CDCTenantContext.stamp(entity)` → `CDCEventHandler.stamp(ctx, entity)`
5. Replace `CDCTenantContext.getCompanyCode()` → `ctx.getCompanyCode()`
6. Replace `CDCTenantContext.getCompanyId()` → `ctx.getCompanyId()`
7. Replace `CDCTenantContext.getCompanyLabel()` → `ctx.getCompanyLabel()`
8. Update calls to `CDCLookupSupport` methods that now require `ctx` param
9. Replace `Map<String, Object> after = event.getAfter()` → `MapObject after = event.getAfter()` (and same for `before`)
10. Remove unused `import java.util.Map;` if applicable

### 5A: TransactionsCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java`

- [ ] **Step 1: Apply all changes listed above**

Specific replacements:
- 4 method signatures (handleCreate/Update/Delete/Snapshot)
- `CDCTenantContext.stamp(fmsTx)` → `CDCEventHandler.stamp(ctx, fmsTx)` (line ~147)
- `CDCTenantContext.stamp(tx)` → `CDCEventHandler.stamp(ctx, tx)` (line ~167)
- `CDCTenantContext.stamp(hb)` → `CDCEventHandler.stamp(ctx, hb)` (line ~199)
- `CDCTenantContext.stamp(container)` → `CDCEventHandler.stamp(ctx, container)` (line ~239)
- `CDCTenantContext.stamp(plan)` → `CDCEventHandler.stamp(ctx, plan)` (line ~288)
- `CDCTenantContext.getCompanyCode()` → `ctx.getCompanyCode()` (line ~508)
- Update `lookupSupport.resolveClient(...)` → `lookupSupport.resolveClient(ctx, ...)`
- Update `lookupSupport.resolveHandlingAgent(...)` → `lookupSupport.resolveHandlingAgent(ctx, ...)`
- `Map<String, Object>` → `MapObject` for local variables

### 5B: TransactionDetailsCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionDetailsCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(hb)` x2 (lines ~63, ~130)
- `CDCTenantContext.getCompanyCode()` (line ~106)
- Update lookupSupport calls with `ctx` param

### 5C: HAWBCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(hb)` (line ~157)
- `CDCTenantContext.stamp(cargo)` (line ~202)
- `CDCTenantContext.getCompanyCode()` (line ~147)

### 5D: ProfitSharesCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/ProfitSharesCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(invoice)` (line ~151)
- `CDCTenantContext.getCompanyLabel()` x2 (lines ~173, ~175)

### 5E: BuyingRateWithHBLCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/BuyingRateWithHBLCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(invoice)` (line ~117)
- `CDCTenantContext.getCompanyLabel()` (line ~165)

### 5F: SellingRateCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/SellingRateCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(invoice)` (line ~112)
- `CDCTenantContext.getCompanyLabel()` (line ~126)

### 5G: CustomsDeclarationCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/CustomsDeclarationCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(detail)` (line ~107)
- `CDCTenantContext.getCompanyId()` (line ~95)

### 5H: TruckingTrackCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TruckingTrackCDCHandler.java`

- [ ] **Step 1: Apply all changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(detail)` (line ~110)
- `CDCTenantContext.getCompanyId()` (line ~93)

---

## Task 6: Update Handlers — Group B (CDCTenantContext.stamp only)

These handlers use `CDCTenantContext.stamp()` but NOT `getCompanyCode()/getCompanyId()/getCompanyLabel()`.

Apply: import changes + method signatures + stamp replacement + Map→MapObject.

### 6A: HAWBDETAILSCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBDETAILSCDCHandler.java`

- [ ] **Step 1: Apply changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(hb)` (lines ~88, ~247)
- `CDCTenantContext.stamp(detail)` (lines ~128, ~147)

### 6B: OtherChargeDetailCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/OtherChargeDetailCDCHandler.java`

- [ ] **Step 1: Apply changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(invoice)` (line ~133)

### 6C: ContainerListOnHBLCDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/ContainerListOnHBLCDCHandler.java`

- [ ] **Step 1: Apply changes**

Specific replacements:
- 4 method signatures
- `CDCTenantContext.stamp(c)` (line ~74)
- `CDCTenantContext.stamp(container)` (line ~132)

---

## Task 7: Update Handlers — Group C (no CDCTenantContext, signature only)

These handlers don't use CDCTenantContext at all. Only method signature + Map→MapObject change needed.

### 7A: HAWBRATECDCHandler

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBRATECDCHandler.java`

- [ ] **Step 1: Update 4 method signatures + imports**

### 7B: ExchangeRateCDCHandler

**File:** `module/settings/src/main/java/of1/fms/settings/currency/cdc/ExchangeRateCDCHandler.java`

- [ ] **Step 1: Update 4 method signatures + imports**

### 7C: PartnersCDCHandler

**File:** `module/partner/src/main/java/of1/fms/module/partner/cdc/PartnersCDCHandler.java`

- [ ] **Step 1: Update 4 method signatures + imports**

---

## Task 8: Delete CDCTenantContext

**File:**
- Delete: `module/core/src/main/java/of1/fms/core/cdc/context/CDCTenantContext.java`

- [ ] **Step 1: Delete the file**

- [ ] **Step 2: Verify no remaining references**

Run: `grep -r "CDCTenantContext" --include="*.java" .`
Expected: No results (0 matches)

---

## Task 9: Build Verification

- [ ] **Step 1: Full compile**

Run: `gradle compileJava`
Expected: BUILD SUCCESSFUL

- [ ] **Step 2: Run existing tests**

Run: `gradle :module-transaction:test --tests "*CDCLookupSupportUnitTest*"`
Expected: All tests PASS

- [ ] **Step 3: Full test suite**

Run: `gradle test`
Expected: BUILD SUCCESSFUL
