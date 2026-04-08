---
title: "FMS Mapping - Cargo"
tags: [bf1, fms, mapping]
---

# Mapping — Cargo

**Target:** `of1_fms_cargo`
**Source:** `dbo.HAWB` (auto-upsert)
**CDC Handler:** `HAWBCDCHandler.upsertCargo()` — called after `enrichHouseBill()`

See also: [[bf1-fms-mapping-house-bill]] · [[bf1-fms-mapping-container]]

---

## 1. Overview

Cargo records are **not** directly mapped from a dedicated source table. Instead, `HAWBCDCHandler` auto-upserts a single Cargo record per HouseBill using aggregate cargo metrics from `dbo.HAWB` plus enrichment fields already populated on HouseBill by the `TransactionDetailsCDCHandler`.

**Why auto-upsert?** Before this change, the Cargo table was only populated via manual UI/API input. The aggregate cargo data (weight, volume, pieces) was visible on Transaction/HouseBill but not on Cargo, creating a data gap for downstream consumers querying cargo directly.

---

## 2. Upsert Logic

```
HAWBCDCHandler.handleCreate/Update(event)
  ├─ save(IntegratedHousebill)
  └─ enrichHouseBill(data, hawbNo)
       ├─ save(HouseBill)  ← cargo fields populated here
       └─ upsertCargo(hb, data)  ← NEW
            ├─ find existing: cargoRepo.findByHouseBillId(hb.id)
            ├─ if exists → update first record
            ├─ else → create new with hb.id + companyId
            └─ save
```

Upsert key: **first Cargo record with matching `house_bill_id`** (one Cargo per HouseBill from CDC; additional Cargo line items can be created manually via UI).

---

## 3. Field Mapping

| FMS Column | Source | Notes |
|---|---|---|
| `id` | — | PK |
| `house_bill_id` | `hb.id` | FK → `of1_fms_house_bill.id` |
| `company_id` | `CDCTenantContext.getCompanyId()` | Tenant |
| `weight` | `HAWB.GrossWeight` (double) | Only written if non-null |
| `volume` | `HAWB.Dimension` (double) | CBM — only written if non-null |
| `package_quantity` | `HAWB.Pieces` (int via `parseDouble().intValue()`) | Only written if non-null |
| `desc_of_goods` | `hb.descOfGoods` | From HouseBill (populated by `TransactionDetailsCDCHandler` from `TransactionDetails.Description`) |
| `packaging_type` | `hb.packagingType` | From HouseBill (from `TransactionDetails.UnitDetail`) |

---

## 4. Fields NOT populated by CDC

These remain null from CDC and are expected to be filled manually via UI/API:

- `container_id` — link to specific container (manual)
- `commodity_code` / `commodity_type` / `commodity_desc` — commodity classification
- `hs_code` — customs HS code
- `dimension_length` / `dimension_width` / `dimension_height` — per-cm dimensions
- `stackable` — stackable flag

---

## 5. Implementation Reference

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java`

Method: `upsertCargo(HouseBill hb, Map<String, Object> data)` — called at end of `enrichHouseBill()` inside the `housebill:` lock.

Guard: skips if `hb.getId() == null` (HouseBill skeleton must exist — created by `TransactionDetailsCDCHandler` first).
