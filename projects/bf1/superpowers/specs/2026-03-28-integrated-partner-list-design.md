# Integrated Partner List — Design Spec

**Date:** 2026-03-28
**Scope:** Replace broken `UIPartnerList` component with a working implementation backed by a new Groovy SQL search method on `IntegratedPartnerService`.

---

## 1. Goal

Replace the existing broken `UIPartnerList.tsx` (wrong service name, wrong field names, old plugin pattern) with a correct implementation that loads `IntegratedPartner` records from the server via `IntegratedPartnerService.searchIntegratedPartners`. The list is read-only (no action on row click). The `fms-partner` screen registration in `init.tsx` already exists and does not need to change.

---

## 2. Columns (12 total)

| Field | Label | Width |
|---|---|---|
| `partnerCode` | Partner Code | 130 |
| `name` | Name | 200 |
| `taxCode` | Tax Code | 130 |
| `category` | Category | 120 |
| `partnerGroup` | Group | 120 |
| `scope` | Scope | 110 |
| `countryLabel` | Country | 130 |
| `provinceLabel` | Province | 130 |
| `saleOwnerCode` | Sale Owner | 120 |
| `partnerSource` | Source | 120 |
| `email` | Email | 180 |
| `cell` | Cell | 120 |

---

## 3. Search Bar (1 control)

1. **Text input** — free-text search. Matches `p.name`, `p.partner_code`, `p.tax_code`. Param key: `search`. Debounced 300ms.

Control calls `plugin.loadData(this)` on change (with 300ms debounce).

---

## 4. Backend

Partner module path: `module/partner/src/main/java/of1/fms/module/partner/`

### 4.1 Groovy SQL Script

**Path:** `module/partner/src/main/java/of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy`

Class: `IntegratedPartnerSql extends Executor`
Inner class: `SearchIntegratedPartners extends ExecutableSqlBuilder`

`IntegratedPartner` has no `storage_state` column. `WHERE` anchored with `1 = 1`.

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

### 4.2 IntegratedPartnerLogic

Add method after existing CRUD methods:

```java
public List<SqlMapRecord> searchIntegratedPartners(ClientContext ctx, SqlQueryParams params) {
  String scriptFile = "of1/fms/module/partner/groovy/IntegratedPartnerSql.groovy";
  return searchDbRecords(ctx, scriptFile, "SearchIntegratedPartners", params);
}
```

The existing Logic file has a disordered import block. Replace the entire import block with the correct ordering (`net.datatp.*` before `of1.*`), adding the two new imports:

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

### 4.3 IntegratedPartnerService

Add method (method-level `@Transactional(readOnly = true)`):

```java
@Transactional(readOnly = true)
public List<SqlMapRecord> searchIntegratedPartners(ClientContext ctx, SqlQueryParams params) {
  return integratedPartnerLogic.searchIntegratedPartners(ctx, params);
}
```

Service bean name: `"IntegratedPartnerService"` (from `@Service("IntegratedPartnerService")`).

---

## 5. Frontend

### Replace: `UIPartnerList.tsx`

**Path:** `webui/fms/src/app/fms/partner/UIPartnerList.tsx`

#### Plugin (`UIPartnerListPlugin`)

```typescript
backend: { backend: 'fms', context: 'system', service: 'IntegratedPartnerService', searchMethod: 'searchIntegratedPartners' }
```

Fields: `search: string = ''`.

Overrides `loadData` — builds flat params object with `maxReturn: 500`, calls `createBackendSearch(uiList, { params }).call()`.

#### Component (`UIPartnerList`)

- Private `searchDebounce` field for debouncing text input (300ms).
- `protected createVGridConfig()` — 12 columns as specified in Section 2. No toolbar actions (read-only).
- `renderSearchBar()` — `flex-hbox p-1 gap-2` with 1 text input (`flex-grow-1`, debounced 300ms).
- `render()` — `flex-vbox h-100` with `renderSearchBar()` + `renderUIGrid()`.

### No changes needed

- `webui/fms/src/app/fms/partner/index.tsx` — already exports `UIPartnerList, UIPartnerListPlugin`
- `webui/fms/src/app/fms/init.tsx` — `fms-partner` screen already registered correctly

---

## 6. Files Changed

| File | Action |
|---|---|
| `module/partner/.../groovy/IntegratedPartnerSql.groovy` | Create |
| `module/partner/.../IntegratedPartnerLogic.java` | Add `searchIntegratedPartners` |
| `module/partner/.../IntegratedPartnerService.java` | Add `searchIntegratedPartners` |
| `webui/fms/src/app/fms/partner/UIPartnerList.tsx` | Replace |

---

## 7. Out of Scope

- Create / edit / delete partners from UI
- Detail popup on row click
- Pagination (maxReturn = 500)
- Additional filters (category, scope, partnerSource)
