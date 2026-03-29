# Integrated Housebill List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a search method to the backend and create a new frontend list component + navigation screen to display `IntegratedHousebill` records with text, date range, typeOfService, customerCode, and shipmentType filters.

**Architecture:** Backend exposes a Groovy SQL-based search method on `IntegratedHousebillService`. Frontend plugin calls this method with a flat params object; the component renders a 5-control search bar above an 18-column read-only VGrid. A new `fms-housebill` screen is registered in the FMS navigation.

**Tech Stack:** Java 17 / Spring Boot (backend), Groovy (SQL script), React 18 class components + OF1 `@of1-webui/lib` (frontend), TypeScript.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy` | Create | SQL query with all 5 filters |
| `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillLogic.java` | Modify | Delegate to searchDbRecords |
| `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillService.java` | Modify | Expose search via @Transactional |
| `webui/fms/src/app/fms/transaction/UIHousebillList.tsx` | Create | Plugin + component with search bar |
| `webui/fms/src/app/fms/transaction/index.tsx` | Modify | Add UIHousebillList exports |
| `webui/fms/src/app/fms/init.tsx` | Modify | Register fms-housebill screen |

---

## Task 1: Create Groovy SQL Script

**Files:**
- Create: `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy`

Reference pattern: `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy`

- [ ] **Step 1: Create the file**

The `groovy/` directory already exists (created during IntegratedTransaction feature). Create the file:

`module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy`:

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

- [ ] **Step 2: Commit**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
git add module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy
git commit -m "feat: add IntegratedHousebillSql groovy search script"
```

---

## Task 2: Add search method to IntegratedHousebillLogic

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillLogic.java`

The class already extends `FMSDaoService` which provides `searchDbRecords`. Import ordering convention: `net.datatp.*` before `of1.*`.

- [ ] **Step 1: Replace the entire import block**

In `IntegratedHousebillLogic.java`, replace the full import block (lines 3–13) as a unit with the following (this reorders existing imports and adds two new ones — do not insert lines, replace the whole block):

```java
import lombok.extern.slf4j.Slf4j;
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
import net.datatp.security.client.ClientContext;
import of1.fms.core.db.FMSDaoService;
import of1.fms.module.transaction.entity.IntegratedHousebill;
import of1.fms.module.transaction.repository.IntegratedHousebillRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
```

- [ ] **Step 2: Add searchIntegratedHousebills method**

Append after the `deleteByTransactionIds` method (before the closing `}`):

```java
public List<SqlMapRecord> searchIntegratedHousebills(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/transaction/groovy/IntegratedHousebillSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedHousebills", params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
gradle :of1-fms-module-transaction:compileJava
```

Expected: `BUILD SUCCESSFUL`

NOTE: Use `gradle` (global, from sdkman), NOT `./gradlew`. Project name is `:of1-fms-module-transaction`.

- [ ] **Step 4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillLogic.java
git commit -m "feat: add searchIntegratedHousebills to IntegratedHousebillLogic"
```

---

## Task 3: Expose search method on IntegratedHousebillService

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillService.java`

No class-level `@Transactional` — method-level only, consistent with existing methods.

- [ ] **Step 1: Replace the entire import block**

Replace the full import block with the following (preserves the blank line before `java.util.List` that exists in the current file):

```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
import net.datatp.module.service.BaseComponent;
import net.datatp.security.client.ClientContext;
import of1.fms.module.transaction.entity.IntegratedHousebill;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
```

- [ ] **Step 2: Add searchIntegratedHousebills method**

Append after the `deleteByTransactionIds` method (before closing `}`):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedHousebills(ClientContext ctx, SqlQueryParams params) {
  return integratedHousebillLogic.searchIntegratedHousebills(ctx, params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
gradle :of1-fms-module-transaction:compileJava
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/IntegratedHousebillService.java
git commit -m "feat: expose searchIntegratedHousebills on IntegratedHousebillService"
```

---

## Task 4: Create UIHousebillList.tsx

**Files:**
- Create: `webui/fms/src/app/fms/transaction/UIHousebillList.tsx`

Reference pattern: `webui/fms/src/app/fms/transaction/UITransactionList.tsx`

- [ ] **Step 1: Create UIHousebillList.tsx**

```typescript
import React from 'react';
import { entity, grid } from '@of1-webui/lib';

const T = (str: string) => str;

export class UIHousebillListPlugin extends entity.DbEntityListPlugin {
  search: string = '';
  reportDateFrom: string | null = null;
  reportDateTo: string | null = null;
  typeOfService: string | null = null;
  customerCode: string | null = null;
  shipmentType: string | null = null;

  constructor() {
    super([]);
    this.backend = {
      backend: 'fms',
      context: 'system',
      service: 'IntegratedHousebillService',
      searchMethod: 'searchIntegratedHousebills',
    };
  }

  loadData(uiList: entity.DbEntityList<any>) {
    const params = {
      search: this.search,
      reportDateFrom: this.reportDateFrom,
      reportDateTo: this.reportDateTo,
      typeOfService: this.typeOfService,
      customerCode: this.customerCode,
      shipmentType: this.shipmentType,
      maxReturn: 500,
    };
    this.createBackendSearch(uiList, { params }).call();
  }
}

export class UIHousebillList extends entity.DbEntityList {
  private searchDebounce: ReturnType<typeof setTimeout> | null = null;
  private customerCodeDebounce: ReturnType<typeof setTimeout> | null = null;

  protected createVGridConfig(): grid.VGridConfig {
    return {
      toolbar: {},
      record: {
        fields: [
          { name: 'transactionId',    label: T('Transaction ID'),  width: 150 },
          { name: 'hawbNo',           label: T('HAWB No'),         width: 160 },
          { name: 'reportDate',       label: T('Report Date'),     width: 130 },
          { name: 'typeOfService',    label: T('Type of Service'), width: 130 },
          { name: 'shipmentType',     label: T('Shipment Type'),   width: 120 },
          { name: 'customerCode',     label: T('Customer Code'),   width: 130 },
          { name: 'customerName',     label: T('Customer Name'),   width: 180 },
          { name: 'agentCode',        label: T('Agent Code'),      width: 120 },
          { name: 'agentName',        label: T('Agent Name'),      width: 180 },
          { name: 'containerSize',    label: T('Container Size'),  width: 180 },
          { name: 'totalPackages',    label: T('Total Packages'),  width: 120 },
          { name: 'hawbGw',           label: T('GW'),              width: 90  },
          { name: 'hawbCw',           label: T('CW'),              width: 90  },
          { name: 'hawbCbm',          label: T('CBM'),             width: 90  },
          { name: 'customsNoSummary', label: T('Customs Nos'),     width: 200 },
          { name: 'cont20Count',      label: T('20ft'),            width: 70  },
          { name: 'cont40Count',      label: T('40ft'),            width: 70  },
          { name: 'cont45Count',      label: T('45ft'),            width: 70  },
        ]
      },
      view: {
        currentViewName: 'table',
        availables: { table: { viewMode: 'table' } }
      }
    };
  }

  renderSearchBar() {
    const plugin = this.props.plugin as UIHousebillListPlugin;
    return (
      <div className="flex-hbox p-1 gap-2">
        <input
          type="text"
          className="form-control flex-grow-1"
          placeholder={T('Search...')}
          onChange={(e) => {
            plugin.search = e.target.value;
            if (this.searchDebounce) clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => plugin.loadData(this), 300);
          }}
        />
        <input
          type="date"
          className="form-control"
          onChange={(e) => { plugin.reportDateFrom = e.target.value || null; plugin.loadData(this); }}
        />
        <input
          type="date"
          className="form-control"
          onChange={(e) => { plugin.reportDateTo = e.target.value || null; plugin.loadData(this); }}
        />
        <select
          className="form-select w-auto"
          onChange={(e) => {
            plugin.typeOfService = e.target.value || null;
            plugin.loadData(this);
          }}
        >
          <option value="">{T('All')}</option>
          <option value="Imp">{T('Imp')}</option>
          <option value="Exp">{T('Exp')}</option>
        </select>
        <input
          type="text"
          className="form-control"
          style={{ width: 140 }}
          placeholder={T('Customer code')}
          onChange={(e) => {
            plugin.customerCode = e.target.value || null;
            if (this.customerCodeDebounce) clearTimeout(this.customerCodeDebounce);
            this.customerCodeDebounce = setTimeout(() => plugin.loadData(this), 300);
          }}
        />
        <select
          className="form-select w-auto"
          onChange={(e) => {
            plugin.shipmentType = e.target.value || null;
            plugin.loadData(this);
          }}
        >
          <option value="">{T('All')}</option>
          <option value="FREEHAND">{T('Freehand')}</option>
          <option value="NOMINATED">{T('Nominated')}</option>
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

Expected: webpack compiled successfully, no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
git add webui/fms/src/app/fms/transaction/UIHousebillList.tsx
git commit -m "feat: create UIHousebillList component with 18 columns and 5-control search bar"
```

---

## Task 5: Update transaction/index.tsx and init.tsx

**Files:**
- Modify: `webui/fms/src/app/fms/transaction/index.tsx`
- Modify: `webui/fms/src/app/fms/init.tsx`

Current `transaction/index.tsx`:
```typescript
export { UITransactionList, UITransactionListPlugin } from './UITransactionList';
```

Current `init.tsx` imports (lines 1-9) and screens (lines 39-81).

- [ ] **Step 1: Add export to transaction/index.tsx**

Append to `webui/fms/src/app/fms/transaction/index.tsx`:

```typescript
export { UIHousebillList, UIHousebillListPlugin } from './UIHousebillList';
```

- [ ] **Step 2: Update init.tsx**

In `webui/fms/src/app/fms/init.tsx`:

**2a. Update import from `./transaction`** (line 6):
```typescript
import { UITransactionList, UITransactionListPlugin, UIHousebillList, UIHousebillListPlugin } from "./transaction";
```

**2b. Add plugin instance** after line 21 (`const reportPlugin = new UIReportListPlugin();`):
```typescript
const housebillPlugin = new UIHousebillListPlugin();
```

**2c. Add screen** inside the `screens: [...]` array of the `fms` root entry, after the `fms-transaction` entry (after line 49):
```typescript
{
  id: 'fms-housebill', label: 'Housebills', backend: MODULE_NAME, icon: icon.Inbox,
  checkPermission: {
    feature: { module: MODULE_NAME, name: FEATURE_BASIC },
    requiredCapability: app.READ,
  },
  renderUI: (appCtx: app.AppContext, pageCtx: app.PageContext) => {
    return <UIHousebillList appContext={appCtx} pageContext={pageCtx} plugin={housebillPlugin} />;
  },
},
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms/webui/fms
pnpm dev-build
```

Expected: webpack compiled successfully, no TypeScript errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
git add webui/fms/src/app/fms/transaction/index.tsx webui/fms/src/app/fms/init.tsx
git commit -m "feat: register fms-housebill screen in FMS navigation"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `gradle :of1-fms-module-transaction:compileJava` passes
- [ ] `pnpm dev-build` passes with no type errors
- [ ] In the running app: "Housebills" screen appears in FMS navigation
- [ ] Housebill list loads data without error
- [ ] Text search filters rows by HAWB No, customer name, agent name, or transaction ID
- [ ] Date range filters rows by report date
- [ ] Dropdown "Imp" shows only import housebills, "Exp" shows only export
- [ ] Customer code input filters by exact customer code
- [ ] Dropdown "Freehand" / "Nominated" filters by shipment type
- [ ] All 18 columns display correctly
