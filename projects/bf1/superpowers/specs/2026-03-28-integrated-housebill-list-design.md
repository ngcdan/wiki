# Integrated Housebill List — Design Spec

**Date:** 2026-03-28
**Scope:** UI list for `IntegratedHousebill` entity with backend search support, new navigation screen

---

## 1. Goal

Display a searchable, filterable list of `IntegratedHousebill` records loaded from the server via `IntegratedHousebillService`. The list is read-only (no action on row click). Registered as a new sub-screen `fms-housebill` inside the `screens[]` array of the existing `fms` root entry in `init.tsx` (alongside `fms-transaction`, `fms-partner`, etc.).

---

## 2. Columns (18 total)

| Field | Label | Width |
|---|---|---|
| `transactionId` | Transaction ID | 150 |
| `hawbNo` | HAWB No | 160 |
| `reportDate` | Report Date | 130 |
| `typeOfService` | Type of Service | 130 |
| `shipmentType` | Shipment Type | 120 |
| `customerCode` | Customer Code | 130 |
| `customerName` | Customer Name | 180 |
| `agentCode` | Agent Code | 120 |
| `agentName` | Agent Name | 180 |
| `containerSize` | Container Size | 180 |
| `totalPackages` | Total Packages | 120 |
| `hawbGw` | GW | 90 |
| `hawbCw` | CW | 90 |
| `hawbCbm` | CBM | 90 |
| `customsNoSummary` | Customs Nos | 200 |
| `cont20Count` | 20ft | 70 |
| `cont40Count` | 40ft | 70 |
| `cont45Count` | 45ft | 70 |

---

## 3. Search & Filter Bar (5 controls)

1. **Text input** — free-text search. Matches `hawb_no`, `customer_name`, `agent_name`, `transaction_id`. Param key: `search`. Debounced 300ms.
2. **Report Date range** — two date inputs. Param keys: `reportDateFrom` / `reportDateTo`. Applied as `report_date >= from` and `report_date <= to` when present.
3. **Type of Service dropdown** — options: All / Imp / Exp. Param key: `typeOfService`. Null when "All". Stored values are free-form strings from BFS One (e.g. "Air Import") — backend uses `LIKE '%Imp%'` / `LIKE '%Exp%'` matching.
4. **Customer Code input** — text input. Param key: `customerCode`. Null when empty. Exact match via `AND_FILTER_BY_PARAM`. Debounced 300ms.
5. **Shipment Type dropdown** — options: All / FREEHAND / NOMINATED. Param key: `shipmentType`. Null when "All". Exact match via `AND_FILTER_BY_PARAM`. The `<option>` value attributes must be the uppercase enum name strings exactly: `value="FREEHAND"` and `value="NOMINATED"` (from `ShipmentType` enum in `of1.fms.module.common`, stored as `shipmentType.name()` in the DB).

Each control calls `plugin.loadData(this)` on change (with debounce for text inputs).

---

## 4. Backend

### 4.1 Groovy SQL Script

**Path:** `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy`

Class: `IntegratedHousebillSql extends Executor`
Inner class: `SearchIntegratedHousebills extends ExecutableSqlBuilder`

`IntegratedHousebill` has no `storage_state` column. `WHERE` anchored with `1 = 1`.

- `shipmentType` and `customerCode` use `AND_FILTER_BY_PARAM` (exact match — known controlled values).
- `typeOfService` uses Groovy conditional LIKE (free-form BFS One strings, same pattern as `IntegratedTransactionSql`).
- Date range uses Groovy conditional string interpolation.
- Text search covers `hawb_no`, `customer_name`, `agent_name`, `transaction_id`.

```groovy
package of1.fms.module.transaction.groovy

import net.datatp.lib.executable.ExecutableContext
import net.datatp.lib.executable.Executor
import net.datatp.module.data.db.ExecutableSqlBuilder
import net.datatp.util.ds.MapObject
import org.springframework.context.ApplicationContext

public class IntegratedHousebillSql extends Executor {
  public class SearchIntegratedHousebills extends ExecutableSqlBuilder {
    public Object execute(ApplicationContext appCtx, ExecutableContext ctx) {
      MapObject sqlParams = ctx.getParam("sqlParams");
      String query = """
        SELECT
          h.id,
          h.transaction_id,
          h.hawb_no,
          h.report_date,
          h.type_of_service,
          h.shipment_type,
          h.customer_code,
          h.customer_name,
          h.agent_code,
          h.agent_name,
          h.container_size,
          h.total_packages,
          h.hawb_gw,
          h.hawb_cw,
          h.hawb_cbm,
          h.customs_no_summary,
          h.cont_20_count,
          h.cont_40_count,
          h.cont_45_count
        FROM integrated_housebill h
        WHERE
          1 = 1
          ${AND_FILTER_BY_PARAM('h.shipment_type', 'shipmentType', sqlParams)}
          ${AND_FILTER_BY_PARAM('h.customer_code', 'customerCode', sqlParams)}
          ${sqlParams.get('typeOfService') ? "AND h.type_of_service LIKE '%${sqlParams.get('typeOfService')}%'" : ''}
          ${AND_SEARCH_BY_PARAMS(['h.hawb_no', 'h.customer_name', 'h.agent_name', 'h.transaction_id'], 'search', sqlParams)}
          ${sqlParams.get('reportDateFrom') ? "AND h.report_date >= '${sqlParams.get('reportDateFrom')}'" : ''}
          ${sqlParams.get('reportDateTo')   ? "AND h.report_date <= '${sqlParams.get('reportDateTo')}'"   : ''}
        ORDER BY h.report_date DESC, h.hawb_no
        ${MAX_RETURN(sqlParams)}
      """;
      return query;
    }
  }

  public IntegratedHousebillSql() {
    register(new SearchIntegratedHousebills())
  }
}
```

### 4.2 IntegratedHousebillLogic

Add method after existing CRUD methods:

```java
public List<SqlMapRecord> searchIntegratedHousebills(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedHousebills", params);
}
```

Imports to add if not present:
```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
```

### 4.3 IntegratedHousebillService

Add method (method-level `@Transactional(readOnly = true)`, no class-level — consistent with existing service pattern):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedHousebills(ClientContext ctx, SqlQueryParams params) {
  return integratedHousebillLogic.searchIntegratedHousebills(ctx, params);
}
```

Service bean name: `"IntegratedHousebillService"` (from `@Service("IntegratedHousebillService")`).

---

## 5. Frontend

### New file: `UIHousebillList.tsx`

**Path:** `webui/fms/src/app/fms/transaction/UIHousebillList.tsx`

#### Plugin (`UIHousebillListPlugin`)

```typescript
backend: { backend: 'fms', context: 'system', service: 'IntegratedHousebillService', searchMethod: 'searchIntegratedHousebills' }
```

Fields: `search`, `reportDateFrom`, `reportDateTo`, `typeOfService`, `customerCode`, `shipmentType` (all null/empty by default).

Overrides `loadData` — builds flat params object with `maxReturn: 500`, calls `createBackendSearch(uiList, { params }).call()`.

#### Component (`UIHousebillList`)

- Private `searchDebounce` and `customerCodeDebounce` fields for debouncing text inputs (300ms).
- `protected createVGridConfig()` — 18 columns as specified in Section 2. No toolbar actions (read-only).
- `renderSearchBar()` — `flex-hbox p-1 gap-2` with 5 controls in order: text search (flex-grow-1), date From, date To, typeOfService select (w-auto), customerCode input, shipmentType select (w-auto).
- `render()` — `flex-vbox h-100` with `renderSearchBar()` + `renderUIGrid()`.

### Update: `transaction/index.tsx`

Add exports:
```typescript
export { UIHousebillList, UIHousebillListPlugin } from './UIHousebillList';
```

### Update: `init.tsx`

Add import and plugin instance:
```typescript
import { UIHousebillList, UIHousebillListPlugin } from "./transaction";
const housebillPlugin = new UIHousebillListPlugin();
```

Add entry inside the `screens: [...]` array of the existing `fms` root entry (alongside `fms-transaction`, `fms-partner`, etc.). Use `icon.Inbox` (distinct from the parent `fms` screen which uses `icon.Package`):

```typescript
// Inside the fms root entry's screens: [...] array
{
  id: 'fms-housebill', label: 'Housebills', backend: MODULE_NAME, icon: icon.Inbox,
  checkPermission: { feature: { module: MODULE_NAME, name: FEATURE_BASIC }, requiredCapability: app.READ },
  renderUI: (appCtx: app.AppContext, pageCtx: app.PageContext) => {
    return <UIHousebillList appContext={appCtx} pageContext={pageCtx} plugin={housebillPlugin} />;
  },
},
```

---

## 6. Files Changed

| File | Action |
|---|---|
| `module/transaction/.../groovy/IntegratedHousebillSql.groovy` | Create |
| `module/transaction/.../IntegratedHousebillLogic.java` | Add `searchIntegratedHousebills` |
| `module/transaction/.../IntegratedHousebillService.java` | Add `searchIntegratedHousebills` |
| `webui/fms/src/app/fms/transaction/UIHousebillList.tsx` | Create |
| `webui/fms/src/app/fms/transaction/index.tsx` | Add export |
| `webui/fms/src/app/fms/init.tsx` | Add screen |

---

## 7. Out of Scope

- Create / edit / delete housebills from UI
- Detail popup on row click
- Pagination (maxReturn = 500)
