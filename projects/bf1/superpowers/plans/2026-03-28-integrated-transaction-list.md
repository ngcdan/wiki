# Integrated Transaction List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a search method to the backend and update the frontend list component to display `IntegratedTransaction` records with text, date range, and service type filters.

**Architecture:** Backend exposes a Groovy SQL-based search method on `IntegratedTransactionService`. Frontend plugin calls this method with a flat params object; the component renders a search bar with three controls above a read-only VGrid.

**Tech Stack:** Java 17 / Spring Boot (backend), Groovy (SQL script), React 18 class components + OF1 `@of1-webui/lib` (frontend), TypeScript.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy` | Create | SQL query with all filters |
| `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionLogic.java` | Modify | Delegate to searchDbRecords |
| `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionService.java` | Modify | Expose search via @Transactional |
| `webui/fms/src/app/fms/transaction/UITransactionList.tsx` | Modify | Plugin + component with search bar |

---

## Task 1: Create Groovy SQL Script

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy`

Reference pattern: `module/settings/src/main/java/of1/fms/settings/bank/groovy/BankSql.groovy`

- [ ] **Step 1: Create the groovy directory and file**

```bash
mkdir -p module/transaction/src/main/java/of1/fms/module/transaction/groovy
```

Create `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy`:

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

- [ ] **Step 2: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/groovy/
git commit -m "feat: add IntegratedTransactionSql groovy search script"
```

---

## Task 2: Add search method to IntegratedTransactionLogic

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionLogic.java`

The class already extends `FMSDaoService` which provides `searchDbRecords`. Add the import and method.

- [ ] **Step 1: Add import for SqlMapRecord and SqlQueryParams**

At the top of `IntegratedTransactionLogic.java`, the existing imports block already has several `net.datatp.*` imports. Add these two if not present:

```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
```

- [ ] **Step 2: Add searchIntegratedTransactions method**

Append after the `deleteByTransactionIds` method (before the closing `}`):

```java
public List<SqlMapRecord> searchIntegratedTransactions(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedTransactions", params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
./gradlew :module:transaction:compileJava
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionLogic.java
git commit -m "feat: add searchIntegratedTransactions to IntegratedTransactionLogic"
```

---

## Task 3: Expose search method on IntegratedTransactionService

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionService.java`

- [ ] **Step 1: Add import for SqlMapRecord and SqlQueryParams**

Add to the imports block at top if not present:

```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
```

- [ ] **Step 2: Add searchIntegratedTransactions method**

Append after the `deleteByTransactionIds` method (before the closing `}`):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedTransactions(ClientContext ctx, SqlQueryParams params) {
  return integratedTransactionLogic.searchIntegratedTransactions(ctx, params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
./gradlew :module:transaction:compileJava
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/IntegratedTransactionService.java
git commit -m "feat: expose searchIntegratedTransactions on IntegratedTransactionService"
```

---

## Task 4: Update UITransactionList.tsx

**Files:**
- Modify: `webui/fms/src/app/fms/transaction/UITransactionList.tsx`

The entire plugin and component are replaced. The existing file uses a broken `TransactionService.search` call. Reference pattern: `webui/fms/src/app/fms/settings/finance/UISettingBankList.tsx` for plugin/loadData style.

- [ ] **Step 1: Replace UITransactionList.tsx with the new implementation**

```typescript
import React from 'react';
import { entity, grid } from '@of1-webui/lib';

const T = (str: string) => str;

export class UITransactionListPlugin extends entity.DbEntityListPlugin {
  search: string = '';
  reportDateFrom: string | null = null;
  reportDateTo: string | null = null;
  typeOfService: string | null = null;

  constructor() {
    super([]);
    this.backend = {
      backend: 'fms',
      context: 'system',
      service: 'IntegratedTransactionService',
      searchMethod: 'searchIntegratedTransactions',
    };
  }

  loadData(uiList: entity.DbEntityList<any>) {
    const params = {
      search: this.search,
      reportDateFrom: this.reportDateFrom,
      reportDateTo: this.reportDateTo,
      typeOfService: this.typeOfService,
      maxReturn: 500,
    };
    this.createBackendSearch(uiList, { params }).call();
  }
}

export class UITransactionList extends entity.DbEntityList {
  protected createVGridConfig(): grid.VGridConfig {
    return {
      toolbar: {},
      record: {
        fields: [
          { name: 'transactionId',    label: T('Transaction ID'),  width: 160 },
          { name: 'reportDate',       label: T('Report Date'),     width: 130 },
          { name: 'typeOfService',    label: T('Type of Service'), width: 130 },
          { name: 'fromLocationCode', label: T('From (Code)'),     width: 130 },
          { name: 'fromLocationLabel',label: T('From (Label)'),    width: 180 },
          { name: 'toLocationCode',   label: T('To (Code)'),       width: 130 },
          { name: 'toLocationLabel',  label: T('To (Label)'),      width: 180 },
          { name: 'containerSize',    label: T('Container Size'),  width: 200 },
        ]
      },
      view: {
        currentViewName: 'table',
        availables: { table: { viewMode: 'table' } }
      }
    };
  }

  renderSearchBar() {
    const plugin = this.props.plugin as UITransactionListPlugin;
    return (
      <div className="flex-hbox p-1 gap-2">
        <input
          type="text"
          className="form-control flex-grow-1"
          placeholder={T('Search...')}
          onChange={(e) => { plugin.search = e.target.value; plugin.loadData(this); }}
        />
        <input
          type="date"
          className="form-control"
          placeholder={T('From date')}
          onChange={(e) => { plugin.reportDateFrom = e.target.value || null; plugin.loadData(this); }}
        />
        <input
          type="date"
          className="form-control"
          placeholder={T('To date')}
          onChange={(e) => { plugin.reportDateTo = e.target.value || null; plugin.loadData(this); }}
        />
        <select
          className="form-select"
          style={{ width: 120, flexShrink: 0 }}
          onChange={(e) => {
            plugin.typeOfService = e.target.value || null;
            plugin.loadData(this);
          }}
        >
          <option value="">{T('All')}</option>
          <option value="Imp">{T('Imp')}</option>
          <option value="Exp">{T('Exp')}</option>
        </select>
      </div>
    );
  }

  render() {
    return (
      <div className="flex-vbox h-100">
        {this.renderSearchBar()}
        {this.renderUIGrid()}
      </div>
    );
  }
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms/webui/fms
pnpm dev-build
```

Expected: no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
git add webui/fms/src/app/fms/transaction/UITransactionList.tsx
git commit -m "feat: implement IntegratedTransaction list with search, date range and service type filters"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `./gradlew :module:transaction:compileJava` passes
- [ ] `pnpm dev-build` passes with no type errors
- [ ] In the running app: transaction list screen loads without error
- [ ] Text search filters rows by transaction ID or location label
- [ ] Date range filters rows by report date
- [ ] Dropdown "Imp" shows only import transactions, "Exp" shows only export
- [ ] "All" dropdown resets filter and shows all records
