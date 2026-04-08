---
title: "FMS Mapping - Container"
tags: [bf1, fms, mapping]
---

# Mapping — Container

**Target:** `of1_fms_container`

**Sources (two):**
1. `dbo.Transactions.ContainerSize` — text field parsed into type+quantity records
2. `dbo.ContainerListOnHBL` — individual container records with container_no + seal_no

**CDC Handlers:**
- `TransactionsCDCHandler.upsertContainersFromSize()` — parses `ContainerSize` text
- `ContainerListOnHBLCDCHandler.upsert()` — line-item container records

See also: [[bf1-fms-mapping-transaction]] · [[bf1-fms-mapping-cargo]]

---

## 1. Dual Source Strategy

Containers are populated from two independent CDC streams that coexist on the same `of1_fms_container` table:

| Source | Scope | Key Fields | Upsert Key |
|--------|-------|-----------|------------|
| `Transactions.ContainerSize` | Aggregate — counts per container type | `container_type`, `quantity` | `(transaction_id, container_type)` |
| `ContainerListOnHBL` | Per-container — real container numbers + seals | `container_no`, `seal_no`, `gross_weight_in_kg`, `volume_in_cbm` | `(transaction_id, container_no)` |

**Rationale:** Legacy BF1 stores container info in two places. Some shipments have only `ContainerSize` text (e.g. `"2x40HC & 1x20"`) without per-container details; others have full `ContainerListOnHBL` line items. FMS merges both into one table so downstream consumers see a unified view.

---

## 2. Source 1 — `Transactions.ContainerSize`

**CDC Handler:** `TransactionsCDCHandler.upsertContainersFromSize()` — called from `saveFmsTransaction()` after the Transaction itself is saved.

### 2.1 Parser

Regex: `(\d+)\s*[xX]\s*(.+)` on each `&`-split segment.

Examples:

| Input | Parsed |
|---|---|
| `"2x40HC & 1x20"` | `[{qty=2, type="40HC"}, {qty=1, type="20"}]` |
| `"1 x 40"` | `[{qty=1, type="40"}]` |
| `"3X20GP"` | `[{qty=3, type="20GP"}]` |
| `""` or null | `[]` (skip) |
| `"invalid"` | `[]` (no `x` separator) |

### 2.2 Upsert Logic

For each parsed `(quantity, type)`:

1. Lookup existing Containers for `transaction_id` where `containerType` (uppercase) matches
2. If found → update `quantity`
3. Else → create new Container with `transaction_id`, `company_id` (from `CDCTenantContext`), `container_type`, `quantity`

**Note:** This source does NOT populate `container_no`, `seal_no`, `gross_weight_in_kg`, `volume_in_cbm`. Those fields come from Source 2.

### 2.3 Field Mapping (Source 1)

| FMS Column | Source | Notes |
|---|---|---|
| `id` | — | PK |
| `transaction_id` | `fmsTx.getId()` | FK |
| `company_id` | `CDCTenantContext.getCompanyId()` | Tenant |
| `container_type` | Parsed from `ContainerSize` text | Upper-cased lookup key |
| `quantity` | Parsed integer → double | E.g. `2.0` for `"2x40HC"` |

---

## 3. Source 2 — `ContainerListOnHBL`

**CDC Handler:** `ContainerListOnHBLCDCHandler`

### 3.1 Upsert Key

`(transaction_id, container_no)` — resolved via HouseBill lookup:

```
HBLNo → findByHawbNo(HouseBill) → getTransactionId()
```

If HouseBill not found or `transactionId == null`, the container event is skipped with a warning.

### 3.2 Field Mapping (Source 2)

| FMS Column | Source Column | Notes |
|---|---|---|
| `id` | — | PK |
| `transaction_id` | `HouseBill.transactionId` (via `HBLNo` lookup) | FK |
| `company_id` | `CDCTenantContext.getCompanyId()` | Tenant |
| `container_no` | `ContainerNo` | Upsert key |
| `container_type` | `ContainerType` | |
| `seal_no` | `SealNo` | |
| `quantity` | `Qty` (int → double) | |
| `gross_weight_in_kg` | `GW` (parseDouble) | |
| `volume_in_cbm` | `CBM` (parseDouble) | |

### 3.3 Delete

`handleDelete()` soft-deletes: sets `storage_state = ARCHIVED` (does not hard-delete).

### 3.4 Locking

Lock key: `"container:" + hblNo + ":" + containerNo` — allows concurrent updates on different containers of the same HBL.

---

## 4. Coexistence Notes

- A single Transaction can have Container records from both sources simultaneously
- Source 1 records typically have `container_no == null` (aggregate only)
- Source 2 records have `container_no` populated (line items)
- Consumers filtering by `container_no IS NOT NULL` get only real line items
- Consumers summing `quantity` across all records for a transaction should de-duplicate carefully (Source 1 aggregates may conflict with Source 2 counts)

---

## 5. Implementation Reference

**Source 1:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java` — `upsertContainersFromSize()`, `parseContainerSize()`, `ContainerParsed` record.

**Source 2:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/ContainerListOnHBLCDCHandler.java`
