# Integrated Transaction List — Design Spec

**Date:** 2026-03-28
**Scope:** UI list for `IntegratedTransaction` entity with backend search support

---

## 1. Goal

Display a searchable, filterable list of `IntegratedTransaction` records loaded from the server via `IntegratedTransactionService`. The list is read-only (no detail popup on row click).

---

## 2. Columns

| Field | Label | Width |
|---|---|---|
| `transactionId` | Transaction ID | 160 |
| `reportDate` | Report Date | 130 |
| `typeOfService` | Type of Service | 130 |
| `fromLocationCode` | From (Code) | 130 |
| `fromLocationLabel` | From (Label) | 180 |
| `toLocationCode` | To (Code) | 130 |
| `toLocationLabel` | To (Label) | 180 |
| `containerSize` | Container Size | 200 |

---

## 3. Search & Filter Bar

Three controls rendered in a horizontal bar above the grid:

1. **Text input** — free-text search. Matches against `transaction_id`, `from_location_label`, `to_location_label` (SQL `OR` condition via `AND_SEARCH_BY_PARAMS`). Param key: `search`.
2. **Report Date range** — two date inputs. Param keys: `reportDateFrom` / `reportDateTo`. Applied as `report_date >= from` and `report_date <= to` when present.
3. **Type of Service dropdown** — options: All / Imp / Exp. Param key: `typeOfService`. Omitted (null) when "All" is selected. The stored values are free-form strings from BFS One (e.g. "Air Import", "Sea Export") — the backend uses `LIKE '%Imp%'` / `LIKE '%Exp%'` matching, consistent with how `IntegratedTransactionLogic.computeReportDate` uses `.contains("Imp")`.

Each control calls `plugin.loadData(this)` on change.

---

## 4. Backend

### 4.1 Groovy SQL Script

**Path:** `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy`

Class: `IntegratedTransactionSql extends Executor`
Inner class: `SearchIntegratedTransactions extends ExecutableSqlBuilder`

`IntegratedTransaction` has no `storage_state` column, so `FILTER_BY_STORAGE_STATE` is not used. The `WHERE` clause is anchored with `1 = 1` to ensure valid SQL when all optional filters are absent.

Date range filters use Groovy conditional string interpolation (there is no range macro in the framework). The `sqlParams` `MapObject` is checked at script evaluation time — if the param is null/absent, the fragment evaluates to an empty string.

`typeOfService` uses Groovy conditional string interpolation with `LIKE '%...%'` matching (not `AND_FILTER_BY_PARAM`). The stored values from BFS One are free-form strings like "Air Import", "Sea Export" — partial matching via `LIKE` is required, consistent with how `IntegratedTransactionLogic.computeReportDate` uses `.contains("Imp")`.

The `search` param key name is `"search"`, matching `AND_SEARCH_BY_PARAMS` convention and the frontend plugin field name.

Groovy SQL files are auto-discovered from the classpath. The file path string passed to `searchDbRecords` must match the package-style resource path: `"of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy"`.

```groovy
package of1.fms.module.transaction.groovy

import net.datatp.lib.executable.ExecutableContext
import net.datatp.lib.executable.Executor
import net.datatp.module.data.db.ExecutableSqlBuilder
import net.datatp.util.ds.MapObject
import org.springframework.context.ApplicationContext

public class IntegratedTransactionSql extends Executor {
  public class SearchIntegratedTransactions extends ExecutableSqlBuilder {
    public Object execute(ApplicationContext appCtx, ExecutableContext ctx) {
      MapObject sqlParams = ctx.getParam("sqlParams");
      String query = """
        SELECT
          t.id,
          t.transaction_id,
          t.report_date,
          t.type_of_service,
          t.from_location_code,
          t.from_location_label,
          t.to_location_code,
          t.to_location_label,
          t.container_size
        FROM integrated_transaction t
        WHERE
          1 = 1
          ${sqlParams.get('typeOfService') ? "AND t.type_of_service LIKE '%${sqlParams.get('typeOfService')}%'" : ''}
          ${AND_SEARCH_BY_PARAMS(['t.transaction_id', 't.from_location_label', 't.to_location_label'], 'search', sqlParams)}
          ${sqlParams.get('reportDateFrom') ? "AND t.report_date >= '${sqlParams.get('reportDateFrom')}'" : ''}
          ${sqlParams.get('reportDateTo')   ? "AND t.report_date <= '${sqlParams.get('reportDateTo')}'"   : ''}
        ORDER BY t.report_date DESC, t.transaction_id
        ${MAX_RETURN(sqlParams)}
      """;
      return query;
    }
  }

  public IntegratedTransactionSql() {
    register(new SearchIntegratedTransactions())
  }
}
```

### 4.2 IntegratedTransactionLogic

Add method (consistent with existing search methods in the codebase):

```java
public List<SqlMapRecord> searchIntegratedTransactions(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedTransactions", params);
}
```

### 4.3 IntegratedTransactionService

Add method at method level (consistent with existing method-level `@Transactional` annotations in this service — no class-level `@Transactional` is present, which is intentional and differs from settings services):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedTransactions(ClientContext ctx, SqlQueryParams params) {
  return integratedTransactionLogic.searchIntegratedTransactions(ctx, params);
}
```

Service bean name is `"IntegratedTransactionService"` (from `@Service("IntegratedTransactionService")`) — matches the frontend `service` config string.

---

## 5. Frontend

**File:** `webui/fms/src/app/fms/transaction/UITransactionList.tsx`

### Plugin (`UITransactionListPlugin`)

Backend config:
```
backend: 'fms'
context: 'system'
service: 'IntegratedTransactionService'
searchMethod: 'searchIntegratedTransactions'
```

The plugin overrides `loadData` (same pattern as `UISettingBankList`) and calls `createBackendSearch(uiList, { params: this.searchParams })`.

Search params shape — flat `MapObject` passed under `params` key (no `sql.createSearchFilter()` envelope, since filters are custom controls rather than the standard toolbar filter widget):
```typescript
{
  search: string,           // free text, empty string when blank
  reportDateFrom: string | null,  // ISO date or null
  reportDateTo: string | null,    // ISO date or null
  typeOfService: string | null,   // 'Imp' | 'Exp' | null
  maxReturn: 500
}
```

`maxReturn` is 500. The `integrated_transaction` table is populated via BFS One sync and expected to contain thousands of records; 500 covers typical daily/weekly operational views without pagination. This can be raised later if needed.

### Component (`UITransactionList`)

Render layout:
```
flex-vbox h-100
  ├── search bar (flex-hbox, gap-2, p-1)
  │     ├── text input        (flex-grow-1, placeholder "Search...")
  │     ├── date input        (placeholder "From date")
  │     ├── date input        (placeholder "To date")
  │     └── select dropdown   (options: All / Imp / Exp)
  └── renderUIGrid()
```

Grid config — no toolbar actions (read-only list, no delete/new). Fields use standard `VGridConfig` field objects.

---

## 6. Files Changed

| File | Action |
|---|---|
| `module/transaction/.../groovy/IntegratedTransactionSql.groovy` | Create |
| `module/transaction/.../IntegratedTransactionLogic.java` | Add `searchIntegratedTransactions` |
| `module/transaction/.../IntegratedTransactionService.java` | Add `searchIntegratedTransactions` |
| `webui/fms/src/app/fms/transaction/UITransactionList.tsx` | Update |

---

## 7. Out of Scope

- Create / edit / delete transactions from UI
- Detail popup on row click
- Pagination (maxReturn = 500 sufficient for initial release)
