# UserAppFeature `sourceRoleTypeId` Refactor — Design Spec

**Date:** 2026-04-10
**Status:** Draft
**Owner:** nqcdan
**Scope:** `of1-core/module/platform-federation` (backend) + `of1-platform/webui/platform` (frontend)

## Problem

The `UserAppFeature` entity (table `security_user_app_feature`) now has a `sourceRoleTypeId` column that distinguishes two row types:

- `sourceRoleTypeId = NULL` → **CUSTOM** override, granted manually by an admin. Must be preserved across syncs.
- `sourceRoleTypeId NOT NULL` → **ROLE**-sourced, materialized from a `UserAppFeatureTemplate` owned by an `IdentityRoleType`. Refreshed/deleted on sync.

The field exists and `UserAppFeatureTemplateLogic.syncUserPermissions` has a first-pass implementation, but several logic paths are not yet wired correctly, and the frontend does not use the field at all.

### Concrete gaps

1. **`IdentityEventLogic.syncRoles`** — the entry point behind the UI "Sync Permission" button. Currently it only updates `IdentityRole.changeRequest` and publishes an async event. It does **not** directly materialize permissions. If no async consumer exists, `security_user_app_feature` is never populated.
2. **`UserAppFeatureTemplateLogic.syncUserAppFeatures(roleTypeId)`** — body is commented out. Template save/delete never re-materializes permissions for affected users.
3. **`AppSql.SearchUserAppPermissions`** — the SQL used to drive the frontend App Features list does not return `uaf.source_role_type_id` or join to `identity_role_type` for its label. Frontend cannot see CUSTOM vs ROLE.
4. **Frontend `UIIdentityAppFeatureList`** — today it guesses "in role template" by separately fetching templates and matching by `appFeatureName`. Redundant, fragile, and wrong once `sourceRoleTypeId` is available.
5. **`AppLogic.saveAppPermission(s)`** — the admin-add path does not explicitly set `sourceRoleTypeId = null`. It works by field default, but is implicit and allows a malicious/broken client to set a non-null value that violates the CUSTOM/ROLE invariant. The admin-edit path also risks overwriting a ROLE row's source and then having it silently reset on the next sync.
6. **`syncUserPermissions` latent bugs**:
   - **CUSTOM collision**: if an account has a CUSTOM row for app X and a new template also targets app X, the current code would insert a "fresh" role-sourced row and violate the unique constraint `(company_id, account_id, app_id)`.
   - **Multi-role conflict resolution**: the current `for (UserAppFeatureTemplate template : templates)` loop behaves differently for update vs insert paths. For update-in-place on an existing ROLE row, the last template iterated wins non-deterministically (depends on DB return order). For the insert path, multiple templates targeting the same `appFeatureId` produce duplicate fresh rows and trigger a unique constraint violation on `(company_id, account_id, app_id)` — a latent crash, not just indeterminism.

## Goals

- Backend becomes single source of truth for CUSTOM vs ROLE classification.
- The "Sync Permission" button deterministically materializes rows in the same transaction as the role ack update.
- Frontend reads `sourceRoleTypeId` / `sourceRoleTypeLabel` directly, without extra round-trips.
- Multi-role conflict resolution is deterministic and follows standard RBAC "max capability wins".
- CUSTOM rows are truly bullet-proof against sync.
- Admin edits on a ROLE row become an explicit conversion to CUSTOM so edits are not silently reset.

## Non-Goals

- Bulk sync across identities from the UI.
- Implementing the async event consumer for template-change → re-sync. Stubbed with a TODO.
- Adding a `priority` field to `IdentityRoleType`.
- Backfilling `source_role_type_id` on existing rows. They remain `NULL` (CUSTOM) until an admin clicks Sync.
- Onboarding banner / migration UX notification.
- Removing or replacing the async event published by `IdentityEventLogic.syncRoles` — it is still needed for other consumers (Keycloak, audit).

## Architecture & Data Model

### Row classification

| `sourceRoleTypeId` | Type | Owner | Sync behavior |
|---|---|---|---|
| `NULL` | CUSTOM | Admin (manual) | Never read, never written by sync |
| `NOT NULL` | ROLE | Template sync logic | Refreshed from template; deleted if no backing template remains |

Invariant (enforced by unique constraint `(company_id, account_id, app_id)`): exactly one row per account per app. Sync must never try to create a second row for an app that already has a CUSTOM row.

### Data flow

```
[Admin UI "Add App Feature"]
    → AppService.saveAppPermissions
    → AppLogic.saveAppPermissions (forces sourceRoleTypeId = null) — BE-5
    → security_user_app_feature (CUSTOM row)

[Admin UI "Edit App Feature" capability/dataScope]
    → AppService.saveAppPermission
    → AppLogic.saveAppPermission (forces sourceRoleTypeId = null) — BE-5 path (ii)
    → ROLE row is auto-converted to CUSTOM on edit

[Admin UI "Sync Permission"]
    → IdentityEventService.syncRoles(identityId, roleIds)
    → IdentityEventLogic.syncRoles — BE-2
        1. Update IdentityRole.changeRequest to PROCESSED
        2. Call UserAppFeatureTemplateLogic.syncUserPermissions(accountId, roleTypeIds)
        3. Publish async IdentityEvent (kept for other consumers)
    (whole method runs in one @Transactional boundary)

[Template save/delete — BE-4 stub]
    → saveUserAppFeatureTemplate / deleteUserAppFeatureTemplatesByIds
    → // TODO: publish TemplateChanged(roleTypeId) async event for re-sync
    → until then, admins must click Sync Permission manually
```

### Sync rules (inside `syncUserPermissions`)

1. **CUSTOM untouchable**: Build `Set<Long> customAppIds` from existing rows where `sourceRoleTypeId == null`. Templates whose `appFeatureId ∈ customAppIds` are skipped entirely — no insert, no update, no delete, no attempt.
2. **Multi-role conflict resolution — max capability wins**:
   - Capability rank: `Admin(4) > Moderator(3) > Write(2) > Read(1) > None(0)`.
   - DataScope rank: `All(4) > Company(3) > Group(2) > Owner(1)`.
   - Group templates by `appFeatureId`. For each group, pick winner via:
     ```
     Comparator.comparingInt(capabilityRank).reversed()
       .thenComparingInt(dataScopeRank).reversed()
       .thenComparingLong(template.roleTypeId)
     ```
   - The winner's `capability`, `dataScope`, `accessType`, and `roleTypeId` populate the resulting row. `sourceRoleTypeId = winner.roleTypeId`.
3. **Materialization**:
   - Existing ROLE rows for an app → update in place (preserves `id`, keeps FK references).
   - No existing ROLE row and no CUSTOM block → insert fresh.
4. **Cleanup**: ROLE rows whose `appId` is not in the winning set are deleted. CUSTOM rows are untouched.

## Backend Changes

### BE-1. SQL `SearchUserAppPermissions` returns source role type label

**File**: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/groovy/AppSql.groovy`

Modify the `SearchUserAppPermissions` query:

```sql
SELECT
  uaf.*,
  af.module                 AS module,
  af.name                   AS name,
  aa.login_id               AS login_id,
  aa.full_name              AS user_full_name,
  srt.label                 AS source_role_type_label
FROM security_user_app_feature uaf
  INNER JOIN security_app_feature af ON af.id = uaf.app_id
  INNER JOIN account_account    aa  ON aa.id  = uaf.account_id
  LEFT  JOIN identity_role_type srt ON srt.id = uaf.source_role_type_id
WHERE
  ${FILTER_BY_STORAGE_STATE('uaf', sqlParams)}
  ${AND_FILTER_BY_PARAM('uaf.app_id', 'appId', sqlParams)}
  ${AND_FILTER_BY_PARAM('uaf.account_id', 'accountId', sqlParams)}
  ${AND_FILTER_BY_PARAM('uaf.access_type', 'accessType', sqlParams)}
  ${AND_FILTER_BY_PARAM('uaf.company_id', 'companyId', sqlParams)}
  ${AND_FILTER_BY_RANGE('uaf.created_time', 'createdTime', sqlParams)}
  ${AND_FILTER_BY_RANGE('uaf.modified_time', 'modifiedTime', sqlParams)}
  ${AND_FILTER_BY_OPTION('uaf.capability', "capability", sqlParams)}
  ${ORDER_BY(sqlParams)}
${MAX_RETURN(sqlParams)}
```

`uaf.*` includes `source_role_type_id`, so the frontend receives `sourceRoleTypeId` automatically. The LEFT JOIN adds `sourceRoleTypeLabel` in the same round-trip, avoiding N+1.

### BE-2. `IdentityEventLogic.syncRoles` materializes permissions in-transaction

**File**: `of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java`

- Inject `UserAppFeatureTemplateLogic`. Prefer constructor injection (see Testing section note on mockability).
- Inside `syncRoles(ctx, identityId, roleIds)`, after persisting role change-request acks and before publishing the async event, insert:
  ```java
  Long accountId = identity.getAccountId();
  if (accountId != null) {
    List<Long> roleTypeIds = roles.stream()
      .map(IdentityRole::getRoleTypeId)
      .distinct()
      .collect(Collectors.toList());
    templateLogic.syncUserPermissions(ctx, ctx.getCompanyId(), accountId, roleTypeIds);
  }
  ```
- **Transaction boundary is already in place**: `IdentityEventService.syncRoles` is annotated `@Transactional` at the service layer (`IdentityEventService.java:30`). No new annotation needed — the injected `syncUserPermissions` call runs inside the same Spring-managed transaction, so any failure rolls back the ack update automatically. Caveat: during implementation, verify that nothing in the injected call chain overrides propagation to `REQUIRES_NEW`.
- The async event is still published afterwards; other consumers (Keycloak sync, audit, etc.) remain untouched.

### BE-2b. `IdentityEventLogic.syncIdentities` also materializes permissions

**File**: same `IdentityEventLogic.java`

`IdentityEventLogic.syncIdentities(ctx, identityIds)` (lines 60-94) is a second entry point that acks change-requests for a list of identities and emits `Sync` events. If left untouched, any caller of `IdentityEventService.syncIdentities` will ack role change-requests without materializing `security_user_app_feature`, leaving permissions stale.

Patch the per-identity loop: after loading `roles` for the identity and persisting `changeRequest` acks, add the same sync call:

```java
Long accountId = identity.getAccountId();
if (accountId != null) {
  List<Long> roleTypeIds = roles == null
      ? java.util.Collections.emptyList()
      : roles.stream().map(IdentityRole::getRoleTypeId).distinct().collect(Collectors.toList());
  templateLogic.syncUserPermissions(ctx, ctx.getCompanyId(), accountId, roleTypeIds);
}
```

`IdentityEventService.syncIdentities` is already `@Transactional` (line 20), so the sync runs inside the enclosing transaction — one identity failing rolls back its own updates. If partial success per identity is desired instead of all-or-nothing, that is an intentional design choice to make at implementation time; default to all-or-nothing because it matches the current behavior of `syncRoles`.

### BE-3. `UserAppFeatureTemplateLogic.syncUserPermissions` — bug fixes + max-capability rule

**File**: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java`

Rewrite the method body:

1. Load `existingPermissions = userAppFeatureRepo.findAppPermissionByAccountId(companyId, accountId)`.
2. Partition:
   - `customAppIds = existingPermissions.stream().filter(p -> p.getSourceRoleTypeId() == null).map(UserAppFeature::getAppId).collect(Collectors.toSet())`.
   - `roleSourced = existingPermissions.stream().filter(p -> p.getSourceRoleTypeId() != null).collect(Collectors.toList())`.
3. If `roleTypeIds` is null/empty, delete all `roleSourced` and return. CUSTOM rows are untouched.
4. Load `templates = templateRepo.findByRoleTypeIdIn(companyId, roleTypeIds)`.
5. **Filter out CUSTOM collisions**: `templates = templates.stream().filter(t -> !customAppIds.contains(t.getAppFeatureId())).toList()`. Log at DEBUG for each skipped entry.
6. **Group by appFeatureId and pick winners**:
   ```java
   Comparator<UserAppFeatureTemplate> bestFirst =
       Comparator.comparingInt((UserAppFeatureTemplate t) -> capabilityRank(t.getCapability())).reversed()
           .thenComparing(Comparator.comparingInt((UserAppFeatureTemplate t) -> dataScopeRank(t.getDataScope())).reversed())
           .thenComparingLong(UserAppFeatureTemplate::getRoleTypeId);

   Map<Long, UserAppFeatureTemplate> winnerByAppId = templates.stream()
       .collect(Collectors.toMap(
           UserAppFeatureTemplate::getAppFeatureId,
           Function.identity(),
           (a, b) -> bestFirst.compare(a, b) <= 0 ? a : b));
   ```
7. Index role-sourced existing rows by `appId`: `sourcedByAppId = roleSourced.stream().collect(Collectors.toMap(UserAppFeature::getAppId, ...))`.
8. For each `(appId, winner)`:
   - If `sourcedByAppId` has an entry, update in place: `current.setSourceRoleTypeId(winner.getRoleTypeId()); current.setAccessType(winner.getAccessType()); current.setCapability(winner.getCapability()); current.setDataScope(winner.getDataScope());`
   - Else, create a fresh row and add to `toSave`. CUSTOM collision is already filtered out in step 5, so no unique-constraint violation is possible.
9. Persist `toSave` via `userAppFeatureRepo.saveAll(toSave)`.
10. Delete `roleSourced` entries whose `appId` is not in `winnerByAppId`.

Add private helpers:

```java
private static int capabilityRank(Capability c) {
  if (c == null) return 0;
  switch (c) {
    case Admin:     return 4;
    case Moderator: return 3;
    case Write:     return 2;
    case Read:      return 1;
    case None:      return 0;
    default:        return 0;
  }
}

private static int dataScopeRank(DataScope s) {
  if (s == null) return 0;
  switch (s) {
    case All:     return 4;
    case Company: return 3;
    case Group:   return 2;
    case Owner:   return 1;
    default:      return 0;
  }
}
```

(Adjust enum constant names to match `net.datatp.security.client.Capability` / `DataScope`.)

### BE-4. `syncUserAppFeatures(roleTypeId)` — TODO stub

**File**: same `UserAppFeatureTemplateLogic.java`

Delete the commented-out body and replace with:

```java
/**
 * Trigger re-materialization of UserAppFeature rows for every account that
 * currently holds {@code roleTypeId}, after a template change on that role type.
 *
 * TODO: Publish TemplateChanged(roleTypeId) async event via IdentityEventProducer.
 * A consumer will iterate IdentityRole by roleTypeId → for each account, call
 * syncUserPermissions with the account's full current roleTypeIds set.
 *
 * Until the consumer is implemented, this is a no-op. Admins must click
 * "Sync Permission" on affected identities manually.
 */
public void syncUserAppFeatures(ClientContext ctx, Long roleTypeId) {
  // No-op. See TODO above.
}
```

Also add TODO markers in the two call-sites:

```java
public UserAppFeatureTemplate saveUserAppFeatureTemplate(ClientContext ctx, UserAppFeatureTemplate template) {
  template.set(ctx);
  template.setCompanyId(ctx.getCompanyId());
  UserAppFeatureTemplate saved = templateRepo.save(template);
  // TODO: trigger syncUserAppFeatures(ctx, saved.getRoleTypeId()) when async
  // re-sync consumer is in place. See syncUserAppFeatures() javadoc.
  return saved;
}

public void deleteUserAppFeatureTemplatesByIds(ClientContext ctx, List<Long> ids) {
  if (ids == null || ids.isEmpty()) return;
  // ... existing delete loop
  // TODO: for each distinct affected roleTypeId, call syncUserAppFeatures(ctx, roleTypeId)
  // when the async re-sync consumer is in place.
}
```

### BE-5. `AppLogic.saveAppPermission` — explicit CUSTOM assignment (single edit)

**File**: `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/AppLogic.java`

Only one method needs to change. `saveAppPermissions` (list variant), `updateAppPermissionCapabilities`, and `updateAppPermissionDataScopes` all delegate to `saveAppPermission(client, permission)` per row (verified in `AppLogic.java:91-128`), so a single edit propagates the rule to every Add / Edit / bulk-update path automatically.

```java
public UserAppFeature saveAppPermission(ClientContext client, UserAppFeature permission) {
  permission.setSourceRoleTypeId(null);   // BE-5: admin Add/Edit/Update is always CUSTOM
  permission.set(client);
  return permissionRepo.save(permission);
}
```

Decision (option ii from brainstorming): editing a ROLE row through any admin UI path (detail editor, capability popover, data-scope popover) **converts it to CUSTOM**. The next `syncUserPermissions` call then leaves it alone. This matches the mental model "admin edit = intentional override".

Consequence: `updateAppPermissionCapabilities` and `updateAppPermissionDataScopes` inherit CUSTOM conversion for free — no additional edits, no separate decision to make. This is the desired behavior.

## Frontend Changes

### FE-1. `UIIdentityAppFeatureList.tsx` — drop template fetch, read field directly

**File**: `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentityAppFeatureList.tsx`

Remove:
- Instance field `templateAppMap: Map<string, string[]>`.
- Method `loadTemplates()`.
- The entire `componentDidMount` override — **delete the whole method, do not leave an empty stub**. An empty override without `super.componentDidMount()` would silently break the base class lifecycle.

Replace the current `In Role Template` column with:

```tsx
{
  name: 'sourceRoleTypeLabel', label: T('Source'), width: 200, filterable: true,
  customRender: (_ctx, _field, dRec) => {
    const record: any = dRec.record;
    const label = record.sourceRoleTypeLabel;

    if (!label) {
      return (
        <span className='badge bg-warning-soft text-warning border border-warning'
          style={{ fontSize: 11, fontWeight: 500 }}>
          {T('Custom')}
        </span>
      );
    }
    return (
      <span className='badge bg-success-soft text-success border border-success'
        style={{ fontSize: 11, fontWeight: 500 }}>
        {label}
      </span>
    );
  }
}
```

- CUSTOM rows render a warning-colored "Custom" badge.
- ROLE rows render a success-colored badge with the role type label.
- `sourceRoleTypeLabel` comes from BE-1's SQL alias.

### FE-2. `UIIdentity.tsx` — drop stale `loadTemplates()` call

**File**: `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentity.tsx`

```tsx
onRolesChanged = () => {
  this.listRef.current?.reloadData();
  this.featureListRef.current?.reloadData();
  // removed: this.featureListRef.current?.loadTemplates();
}
```

After BE-2, a reload of the App Features list is sufficient — the freshly synced data already carries `sourceRoleTypeLabel`.

**FE-1 and FE-2 must ship together as one atomic change.** Shipping FE-1 without FE-2 leaves a `loadTemplates` call referencing a deleted method → TypeScript compile error. Shipping FE-2 without FE-1 leaves the stale `templateAppMap` code wired to a method that no longer runs.

### FE-3. Add App Feature payload — verify

**File**: same `UIIdentityAppFeatureList.tsx`, method `onAddAppFeature`

No code change. The payload sent to `AppService.saveAppPermissions` does not include `sourceRoleTypeId`. BE-5 guarantees the server sets it to `null` explicitly.

### FE-4. Sort options include the new column

**File**: same `UIIdentityAppFeatureList.tsx`, plugin `orderBy`:

```tsx
orderBy: {
  fields: ['module', 'name', 'sourceRoleTypeLabel', 'capability', 'modifiedTime'],
  fieldLabels: ['App', 'Feature Screen', 'Source', 'Capability', 'Modified Time'],
  selectFields: ['module', 'name'],
  sort: 'ASC'
}
```

Lets admins sort by source role type label, grouping CUSTOMs together.

## Testing

### Backend — unit tests (new file)

`of1-core/module/platform-federation/src/test/java/datatp/platform/resource/UserAppFeatureTemplateLogicTest.java`

| # | Name | Scenario |
|---|---|---|
| 1 | `syncWithEmptyRoleTypeIds_deletesAllRoleSourcedRowsOnly` | Arrange: 2 CUSTOM + 3 ROLE rows. Act: sync `[]`. Assert: 2 CUSTOM rows remain, 3 ROLE rows deleted. |
| 2 | `syncWithNewRoleType_insertsFreshRoleSourcedRows` | No existing rows; `R1` template has apps A, B. After sync `[R1]`: 2 new rows with `sourceRoleTypeId = R1`. |
| 3 | `syncWithExistingRoleRows_refreshesCapabilityFromTemplate` | Existing ROLE row for `appA` (`Read`, sourced from `R1`). Template `R1/appA` now `Write`. After sync `[R1]`: same row, now `Write`, same `sourceRoleTypeId`. |
| 4 | `syncRemovesRoleRowsNotBackedByAnyTemplate` | Existing ROLE row for `appA`. Template `R1` no longer has `appA`. After sync `[R1]`: row deleted. |
| 5 | `syncWithCustomCollision_customWinsAndTemplateSkipped` | Existing CUSTOM row `appA` (`Read`, `sourceRoleTypeId=null`). Template `R1/appA` has `Write`. After sync `[R1]`: CUSTOM row untouched, no extra row for `appA`, no unique-constraint violation. |
| 6 | `syncWithMultiRoleOverlap_picksMaxCapability` | `R1/appA=Read/Owner`, `R2/appA=Write/Company`. After sync `[R1,R2]`: row is `Write/Company`, `sourceRoleTypeId=R2`. |
| 7 | `syncWithMultiRoleSameCapability_tieBreaksByDataScope` | `R1/appA=Write/Owner`, `R2/appA=Write/Company`. After sync `[R1,R2]`: `dataScope=Company`, `sourceRoleTypeId=R2`. |
| 8 | `syncWithMultiRoleSameCapAndScope_tieBreaksBySmallerRoleTypeId` | `R1/appA=Write/Owner`, `R2/appA=Write/Owner`, `R1.id < R2.id`. Sync input order shuffled. Result: `sourceRoleTypeId=R1`. |

### Backend — integration tests (extend existing)

Add to `IdentityIntegrationTest` (or create `IdentityEventLogicIntegrationTest`):

| # | Name | Scenario |
|---|---|---|
| 9 | `syncRoles_materializesPermissionsInSameTransaction` | Identity with `accountId`, 2 role types each with a template. Call `IdentityEventLogic.syncRoles`. Assert: `IdentityRole.changeRequest.ackStatus == PROCESSED`, `security_user_app_feature` populated per templates, event published. |
| 10 | `syncRoles_rollbackOnPermissionSyncFailure` | Mock `syncUserPermissions` to throw. Call `syncRoles`. Assert: `IdentityRole.changeRequest` not updated (full rollback). |
| 11 | `syncIdentities_materializesPermissionsPerIdentity` | Two identities with distinct role types and templates. Call `IdentityEventLogic.syncIdentities`. Assert: each identity's `security_user_app_feature` rows match their respective templates; each `changeRequest` acked; event published per identity. |

**Mocking technique**: `IdentityEventLogic` currently uses field injection (`@Autowired`). To make test #10 feasible, either:
- Use `@MockBean UserAppFeatureTemplateLogic` in a `@SpringBootTest` slice, or
- Convert `IdentityEventLogic` to constructor injection for the new `UserAppFeatureTemplateLogic` dependency and pass a Mockito mock in a plain `@ExtendWith(MockitoExtension.class)` unit test.

Prefer constructor injection — it's more testable, documents dependencies, and matches modern Spring guidance.

### Frontend — manual QA checklist

- [ ] Identity detail opens; App Features list loads; `Source` column visible.
- [ ] Identity never synced → every row shows the yellow `Custom` badge.
- [ ] Click `Sync Permission` → list reloads; apps with templates now show a green badge with the role type label.
- [ ] `Add App Feature` popup → newly added row shows `Custom`.
- [ ] Admin edits `capability` on a ROLE row through `UIFeatureAccessEditor` → row becomes `Custom` on save (BE-5 path ii).
- [ ] Remove a role from the Role Type list + click `Sync` → apps that were only backed by that role disappear from App Features (CUSTOM overrides remain).
- [ ] Delete a role type in the Role Type admin page → all ROLE rows sourced from it disappear for affected users (existing `IdentityLogic.deleteRoleTypes` cascade path).

## Migration & Rollout

- **No DB migration script**. `source_role_type_id` column exists already; existing rows remain `NULL` → treated as CUSTOM.
- **Deploy order**:
  1. Backend (BE-1..BE-5). Backward compatible with old frontend; adding a field and logic does not break old clients.
  2. Frontend (FE-1..FE-4). Safe to deploy anytime after BE is live.
  3. Rollback: revert backend to previous version; old frontend still works because it does not read `sourceRoleTypeLabel`.
- **Admin communication** after deploy:
  > After this upgrade, all App Features on the identity detail screen will show as **Custom**. Click **Sync Permission** on each identity to materialize rows from the current role templates. CUSTOM rows are preserved; only role-sourced rows are created/refreshed.

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Legacy rows are in fact template-sourced but now read as CUSTOM → admins may be confused. | High | Q4 rule "CUSTOM wins" guarantees that clicking Sync will not erase legacy rows; it only creates additional rows from templates. Manual review may be required but no data is lost. Documented in admin communication. |
| R2 | `syncRoles` runs sync + ack in one transaction → long transactions on accounts with many roles or large templates. | Medium | Monitor transaction duration post-deploy. Fallback: split permission sync into a non-transactional helper if throughput becomes a problem (trades off atomicity). |
| R3 | BE-5 path (ii) auto-converts ROLE row to CUSTOM on edit → an accidental edit permanently detaches the row from template sync. | Medium | Documented behavior. Optional follow-up: add a confirm dialog in `UIFeatureAccessEditor` when editing a row whose `sourceRoleTypeId != null`. Out of scope here. |
| R4 | Switching from "last wins" to max-capability may grant some accounts higher capabilities than before. | Low | "Last wins" was non-deterministic and largely unused; max-capability matches RBAC intent. Document and spot-check after deploy. |
| R5 | Bug in the CUSTOM collision filter → unique constraint violation on sync. | Low | Tests #1 and #5 cover exactly this scenario. CI gate required before deploy. |
| R6 | BE-4 stub → template save does not auto-propagate to existing users. | Medium | Admin communication + manual Sync workflow. Will be resolved by follow-up work on the async consumer. |
| R7 | Orphaned ROLE rows: if an identity previously had an `accountId` that materialized ROLE rows and the account link was later removed (identity.accountId set to NULL), those rows persist and are never touched by sync (the null-guard in BE-2/BE-2b skips them entirely). | Low | Out of scope for this refactor. Cascade cleanup on account unlink is handled by `IdentityLogic` deletion paths today. Flag as a known limitation; consider a follow-up cleanup job if it becomes material. |

## Open Questions

_(None. Both prior open questions were resolved during the spec review: bulk update paths delegate through `saveAppPermission` and inherit the CUSTOM rule automatically; `@Transactional` already lives at `IdentityEventService` for both `syncRoles` and `syncIdentities`.)_

## References

- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/entity/UserAppFeature.java` — entity with `sourceRoleTypeId`.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/logic/UserAppFeatureTemplateLogic.java` — `syncUserPermissions` first pass.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/identity/queue/IdentityEventLogic.java` — entry point for the Sync Permission UI action.
- `of1-core/module/platform-federation/src/main/java/datatp/platform/resource/groovy/AppSql.groovy` — `SearchUserAppPermissions` SQL.
- `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentityAppFeatureList.tsx` — current frontend list with `templateAppMap` hack.
- `of1-platform/webui/platform/src/module/platform/security/identity/UIIdentity.tsx` — `UIIdentityDetail` and `syncRoles` client call.
