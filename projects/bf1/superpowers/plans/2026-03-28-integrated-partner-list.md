# Integrated Partner List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken `UIPartnerList` component and its missing backend with a working search-backed list of `IntegratedPartner` records.

**Architecture:** Backend exposes a Groovy SQL-based search method on `IntegratedPartnerService`. Frontend plugin calls this method with a flat params object; the component renders a debounced text search bar above a read-only 12-column VGrid.

**Tech Stack:** Java 17 / Spring Boot (backend), Groovy (SQL script), React 18 class components + OF1 `@of1-webui/lib` (frontend), TypeScript.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `module/partner/src/main/java/of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy` | Create | SQL query with text search |
| `module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerLogic.java` | Modify | Delegate to searchDbRecords |
| `module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerService.java` | Modify | Expose search via @Transactional |
| `webui/fms/src/app/fms/partner/UIPartnerList.tsx` | Replace | Plugin + 12-column grid with search bar |

---

## Task 1: Create Groovy SQL Script

**Files:**
- Create: `module/partner/src/main/java/of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy`

Reference pattern: `module/transaction/src/main/java/of1/fms/module/transaction/groovy/IntegratedTransactionSql.groovy`

- [ ] **Step 1: Create the groovy directory and file**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms && mkdir -p module/partner/src/main/java/of1/fms/module/partner/groovy
```

Create `module/partner/src/main/java/of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy`:

```groovy
package of1.fms.module.partner.groovy

import net.datatp.lib.executable.ExecutableContext
import net.datatp.lib.executable.Executor
import net.datatp.module.data.db.ExecutableSqlBuilder
import net.datatp.util.ds.MapObject
import org.springframework.context.ApplicationContext

public class IntegratedPartnerSql extends Executor {
  public class SearchIntegratedPartners extends ExecutableSqlBuilder {
    public Object execute(ApplicationContext appCtx, ExecutableContext ctx) {
      MapObject sqlParams = ctx.getParam("sqlParams");
      String query = """
        SELECT
          p.id,
          p.partner_code,
          p.name,
          p.tax_code,
          p.category,
          p.partner_group AS partnerGroup,
          p.scope,
          p.country_label,
          p.province_label,
          p.sale_owner_code,
          p.partner_source,
          p.email,
          p.cell
        FROM integrated_partner p
        WHERE
          1 = 1
          ${AND_SEARCH_BY_PARAMS(['p.name', 'p.partner_code', 'p.tax_code'], 'search', sqlParams)}
        ORDER BY p.name
        ${MAX_RETURN(sqlParams)}
      """;
      return query;
    }
  }

  public IntegratedPartnerSql() {
    register(new SearchIntegratedPartners())
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add module/partner/src/main/java/of1/fms/module/partner/groovy/
git commit -m "feat: add IntegratedPartnerSql groovy search script"
```

---

## Task 2: Add search method to IntegratedPartnerLogic

**Files:**
- Modify: `module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerLogic.java`

The class already extends `FMSDaoService` which provides `searchDbRecords`. The existing import block is disordered (`of1.*` before `net.datatp.*`) — fix it while adding the new imports.

- [ ] **Step 1: Replace the entire import block**

The current import block (lines 3–13) is:
```java
import of1.fms.core.db.FMSDaoService;
import net.datatp.security.client.ClientContext;
import of1.fms.module.partner.entity.IntegratedPartner;
import of1.fms.module.partner.entity.PartnerCategory;
import of1.fms.module.partner.entity.PartnerGroup;
import of1.fms.module.partner.repository.IntegratedPartnerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.List;
```

Replace it entirely with the correctly ordered block (`net.datatp.*` before `of1.*`), adding the two new imports:

```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
import net.datatp.security.client.ClientContext;
import of1.fms.core.db.FMSDaoService;
import of1.fms.module.partner.entity.IntegratedPartner;
import of1.fms.module.partner.entity.PartnerCategory;
import of1.fms.module.partner.entity.PartnerGroup;
import of1.fms.module.partner.repository.IntegratedPartnerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.List;
```

- [ ] **Step 2: Add searchIntegratedPartners method**

Append after the `deleteIntegratedPartnerByIds` method (before the closing `}`):

```java
public List<SqlMapRecord> searchIntegratedPartners(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedPartners", params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
gradle :of1-fms-module-partner:compileJava
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Commit**

```bash
git add module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerLogic.java
git commit -m "feat: add searchIntegratedPartners to IntegratedPartnerLogic"
```

---

## Task 3: Expose search method on IntegratedPartnerService

**Files:**
- Modify: `module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerService.java`

- [ ] **Step 1: Add imports for SqlMapRecord and SqlQueryParams**

Insert these two lines after `import net.datatp.security.client.ClientContext;` (line 4) and before `import of1.fms.module.partner.entity.IntegratedPartner;` (line 5). Note: `java.util.List` is already present on line 12 — no additional import needed.

```java
import net.datatp.module.data.db.SqlMapRecord;
import net.datatp.module.data.db.query.SqlQueryParams;
```

- [ ] **Step 2: Add searchIntegratedPartners method**

Append after the `deleteIntegratedPartnerByIds` method (before the closing `}`):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedPartners(ClientContext ctx, SqlQueryParams params) {
  return integratedPartnerLogic.searchIntegratedPartners(ctx, params);
}
```

- [ ] **Step 3: Verify the file compiles**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-fms
gradle :of1-fms-module-partner:compileJava
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Commit**

```bash
git add module/partner/src/main/java/of1/fms/module/partner/IntegratedPartnerService.java
git commit -m "feat: expose searchIntegratedPartners on IntegratedPartnerService"
```

---

## Task 4: Replace UIPartnerList.tsx

**Files:**
- Replace: `webui/fms/src/app/fms/partner/UIPartnerList.tsx`

Reference pattern: `webui/fms/src/app/fms/transaction/UITransactionList.tsx`

The current file uses the old `DbEntityListBackendConfig` pattern, wrong service name (`PartnerService`), wrong field names (`code`, `type`, `country`), and has no debounce. Replace the entire file.

- [ ] **Step 1: Replace UIPartnerList.tsx with the new implementation**

```typescript
import React from 'react';
import { entity, grid } from '@of1-webui/lib';

const T = (str: string) => str;

export class UIPartnerListPlugin extends entity.DbEntityListPlugin {
  search: string = '';

  constructor() {
    super([]);
    this.backend = {
      backend: 'fms',
      context: 'system',
      service: 'IntegratedPartnerService',
      searchMethod: 'searchIntegratedPartners',
    };
  }

  loadData(uiList: entity.DbEntityList<any>) {
    const params = {
      search: this.search,
      maxReturn: 500,
    };
    this.createBackendSearch(uiList, { params }).call();
  }
}

export class UIPartnerList extends entity.DbEntityList {
  private searchDebounce: ReturnType<typeof setTimeout> | null = null;

  protected createVGridConfig(): grid.VGridConfig {
    return {
      toolbar: {},
      record: {
        fields: [
          { name: 'partnerCode',   label: T('Partner Code'), width: 130 },
          { name: 'name',          label: T('Name'),         width: 200 },
          { name: 'taxCode',       label: T('Tax Code'),     width: 130 },
          { name: 'category',      label: T('Category'),     width: 120 },
          { name: 'partnerGroup',  label: T('Group'),        width: 120 },
          { name: 'scope',         label: T('Scope'),        width: 110 },
          { name: 'countryLabel',  label: T('Country'),      width: 130 },
          { name: 'provinceLabel', label: T('Province'),     width: 130 },
          { name: 'saleOwnerCode', label: T('Sale Owner'),   width: 120 },
          { name: 'partnerSource', label: T('Source'),       width: 120 },
          { name: 'email',         label: T('Email'),        width: 180 },
          { name: 'cell',          label: T('Cell'),         width: 120 },
        ]
      },
      view: {
        currentViewName: 'table',
        availables: { table: { viewMode: 'table' } }
      }
    };
  }

  renderSearchBar() {
    const plugin = this.props.plugin as UIPartnerListPlugin;
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

Expected: `webpack X.X.X compiled successfully` — no TypeScript errors.

- [ ] **Step 2b: Verify `partner/index.tsx` already exports the correct names**

Read `webui/fms/src/app/fms/partner/index.tsx` and confirm it contains:
```typescript
export { UIPartnerList, UIPartnerListPlugin } from './UIPartnerList';
```
No change needed if this line is already present.

- [ ] **Step 3: Commit**

```bash
git add webui/fms/src/app/fms/partner/UIPartnerList.tsx
git commit -m "feat: replace UIPartnerList with correct 12-column grid and search"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `gradle :of1-fms-module-partner:compileJava` passes
- [ ] `pnpm dev-build` passes with no type errors
- [ ] In the running app: partner list screen loads without error
- [ ] Text search filters rows by name, partner code, or tax code
- [ ] Clearing search shows all records (up to 500)
- [ ] All 12 columns render with correct data
