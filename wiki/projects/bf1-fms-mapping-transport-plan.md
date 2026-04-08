---
title: "FMS Mapping - Transport Plan"
tags: [bf1, fms, mapping]
---

# Mapping — Transport Plan & Route

**Targets:** `of1_fms_transport_plan`, `of1_fms_transport_route`
**Source:** `dbo.Transactions` (via `TransactionsCDCHandler.saveTransportPlan`)
**CDC Handler:** `TransactionsCDCHandler` — rebuilt on every Transaction CDC event

See also: [[bf1-fms-mapping-transaction]]

---

## 1. Rebuild Strategy

On every Transaction CDC event (`handleCreate` / `handleUpdate` / `handleSnapshot`):

1. Look up HouseBill by `HWBNO` from the Transaction record
2. Delete ALL existing `TransportPlan` (and cascading `TransportRoute`) for that HouseBill
3. Build fresh `TransportPlan` from `PortofLading` / `PortofUnlading` / `LoadingDate` / `ArrivalDate` / `TransitPort*`
4. Build one or two `TransportRoute` legs depending on presence of transit port
5. Save

**Rationale:** BF1 route data is simple and changes atomically. Rebuilding is safer than merging and avoids stale leg state.

---

## 2. TransportPlan Fields

| FMS Column | Source | Notes |
|---|---|---|
| `id` | — | PK |
| `house_bill_id` | `HouseBill` (via `HWBNO` lookup) | FK |
| `company_id` | `CDCTenantContext` | Tenant |
| `from_location_code` | `PortofLading` → location code lookup | POL |
| `from_location_label` | `PortofLading` | POL label |
| `to_location_code` | `PortofUnlading` → lookup | POD |
| `to_location_label` | `PortofUnlading` | POD label |
| `depart_time` | `LoadingDate` | |
| `arrival_time` | `ArrivalDate` | |
| `transport_name` | `RefNoSea` | Vessel/flight name |
| `flight_date_confirm` | `FlightDateConfirm` | |

## 3. TransportRoute Legs

### 3.1 Direct (no transit)

If neither `TransitPortFrom` nor `TransitPortDes` is set, one route is created:

| Route Field | Source |
|---|---|
| `from_location_label/code` | `PortofLading` |
| `to_location_label/code` | `PortofUnlading` |
| `depart_time` | `LoadingDate` |
| `arrival_time` | `ArrivalDate` |
| `transport_no` | `FlghtNo` |
| `carrier_label` | `ColoaderID` → partner lookup |
| `sort_order` | `0` |

### 3.2 With Transit

If transit is present, two routes:

**Leg 1 — POL → Transit:**

| Route Field | Source |
|---|---|
| `from_location_label/code` | `PortofLading` |
| `to_location_label/code` | `TransitPortFrom` (fallback to `TransitPortDes` if only one is set) |
| `depart_time` | `LoadingDate` |
| `arrival_time` | `ETATransit` or fallback `ETDTransit` |
| `sort_order` | `0` |

**Leg 2 — Transit → POD:**

| Route Field | Source |
|---|---|
| `from_location_label/code` | `TransitPortDes` (fallback to `TransitPortFrom`) |
| `to_location_label/code` | `PortofUnlading` |
| `depart_time` | `ETDTransit` or fallback `ETATransit` |
| `arrival_time` | `ArrivalDate` |
| `sort_order` | `1` |

Both legs share: `transport_no` = `FlghtNo`, `carrier_label` = `ColoaderID` lookup.

---

## 4. Status

**CDC-verified** — production coverage for basic POL/POD + 1-transit routing.

**Not yet supported from CDC:**
- Multi-hop routing (>2 legs)
- Per-leg carrier assignment (all legs share same carrier)
- Manual route overrides (will be wiped on next Transaction CDC event — do not edit rebuilt routes manually)

---

## 5. Implementation Reference

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java`

Methods: `saveTransportPlan()`, `buildTransportPlan()`, `newRoute()`.
