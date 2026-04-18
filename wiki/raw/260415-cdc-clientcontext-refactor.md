# CDC Refactor: ClientContext + CDCEvent\<MapObject\>

**Date:** 2026-04-15
**Status:** Approved
**Scope:** module/core (CDC framework), module/transaction (handlers), of1-core (ClientContext)

---

## Problem

CDC handlers hiện dùng `CDCTenantContext` (ThreadLocal) để truyền company info và `CDCEvent<Map<String, Object>>` cho event data. Vấn đề:

1. **ThreadLocal implicit dependency** — handlers gọi `CDCTenantContext.getCompanyCode()` mà không khai báo dependency rõ ràng, khó test, dễ leak
2. **Duplicate context mechanism** — Platform đã có `ClientContext` với đầy đủ company info (`companyId`, `companyCode`, `companyLabel`), CDC tự tạo riêng `CDCTenantContext`
3. **Raw Map** — `Map<String, Object>` thiếu API fluent, mỗi handler phải cast thủ công. `MapObject` đã có sẵn `.getString()`, `.getLong()`, `.with()`

## Solution

### 1. CDCEventHandler Interface

**Before:**
```java
public interface CDCEventHandler {
  String getTableName();
  void handleCreate(CDCEvent<Map<String, Object>> event);
  void handleUpdate(CDCEvent<Map<String, Object>> event);
  void handleDelete(CDCEvent<Map<String, Object>> event);
  void handleSnapshot(CDCEvent<Map<String, Object>> event);
}
```

**After:**
```java
public interface CDCEventHandler {
  String getTableName();
  void handleCreate(ClientContext ctx, CDCEvent<MapObject> event);
  void handleUpdate(ClientContext ctx, CDCEvent<MapObject> event);
  void handleDelete(ClientContext ctx, CDCEvent<MapObject> event);
  void handleSnapshot(ClientContext ctx, CDCEvent<MapObject> event);
}
```

### 2. CDCListener Changes

CDCListener tạo `ClientContext` thay vì `CDCTenantContext`:

```java
ClientContext ctx = new ClientContext("default", "cdc-sync", "localhost");
ctx.setCompanyId(companyInfo.id());
ctx.setCompanyCode(companyCode);
ctx.setCompanyLabel(companyInfo.label());
```

**Event deserialization:** Vẫn deserialize `CDCEvent<Map<String, Object>>`, rồi convert sang `CDCEvent<MapObject>` bằng helper method (dùng `new MapObject(map)` constructor, tương tự pattern trong `CDCCompanyResolver`).

Xóa toàn bộ `CDCTenantContext.set()` / `CDCTenantContext.clear()`.

### 3. CDCTenantContext — Xóa

Xóa class `CDCTenantContext`.

`stamp()` method chuyển thành static utility (hoặc đặt trong `CDCEventHandler` default method):

```java
static <T extends PersistableEntity<?>> T stamp(ClientContext ctx, T entity) {
  entity.set(ctx.getLoginId(), new Date());
  if (entity instanceof CompanyEntity ce && ce.getCompanyId() == null) {
    ce.setCompanyId(ctx.getCompanyId());
  }
  return entity;
}
```

### 4. of1-core: ClientContext Update

Thêm `@Setter` cho field `companyLabel` trong `ClientContext.java`:
```java
@Getter @Setter
public String companyLabel;
```

### 5. CDCEvent\<MapObject\> Conversion

CDCListener convert sau khi deserialize:

```java
// Deserialize raw
CDCEvent<Map<String, Object>> raw = objectMapper.readValue(message, ...);

// Convert to MapObject
CDCEvent<MapObject> cdcEvent = convertToMapObject(raw);
```

Helper method trên CDCEvent hoặc CDCListener:
```java
private CDCEvent<MapObject> convertToMapObject(CDCEvent<Map<String, Object>> raw) {
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

## Impact

### Files Changed

**of1-core (1 file):**
- `net/datatp/security/client/ClientContext.java` — add `@Setter` to `companyLabel`

**module/core (4 files):**
- `CDCEventHandler.java` — update interface signatures
- `CDCListener.java` — create ClientContext, convert event, remove CDCTenantContext usage
- `CDCTenantContext.java` — DELETE
- `CDCSyncMonitorService.java` — no change (already uses ClientContext)

**module/transaction (CDC handlers + support, ~16 files):**

| Handler | CDCTenantContext Usage | Change |
|---------|----------------------|--------|
| TransactionsCDCHandler | `getCompanyCode()` | `ctx.getCompanyCode()` |
| TransactionDetailsCDCHandler | `getCompanyCode()` | `ctx.getCompanyCode()` |
| HAWBCDCHandler | `getCompanyCode()` | `ctx.getCompanyCode()` |
| CustomsDeclarationCDCHandler | `getCompanyId()` | `ctx.getCompanyId()` |
| TruckingTrackCDCHandler | `getCompanyId()` | `ctx.getCompanyId()` |
| ProfitSharesCDCHandler | `getCompanyLabel()` | `ctx.getCompanyLabel()` |
| CDCLookupSupport | `getCompanyCode()` x2 | `ctx.getCompanyCode()` |
| All 14 handlers | `Map<String, Object>` → `MapObject` | Signature change |
| All handlers using `stamp()` | `CDCTenantContext.stamp(e)` | `stamp(ctx, e)` |

## Non-Goals

- Không refactor handler business logic
- Không thay đổi Kafka/Debezium config
- Không thay đổi CDCSyncMonitorService behavior
