---
title: "FMS CDC Field Mappings"
tags: [bf1, fms, mapping, cdc]
---

> Sub-index cua [[bf1-index|BF1 — Index]]

# CDC Field Mappings

Source MSSQL -> FMS PostgreSQL field mappings, organized by **target entity**.

See also: [[bf1-fms-04-integration]] for pipeline architecture, [[bf1-fms-03-data-model]] for entity schemas.

---

## Index by Target Entity

| Target Entity | Section | Source Tables | CDC Handler(s) | Notes |
|---|---|---|---|---|
| `of1_fms_transactions` | [Transaction](#mapping--transaction) | `dbo.Transactions` | `TransactionsCDCHandler` | Master bill + parses `ContainerSize` + rebuilds transport plan |
| `of1_fms_house_bill` + details | [House Bill](#mapping--house-bill) | `dbo.TransactionDetails`, `dbo.HAWB`, `dbo.HAWBDETAILS`, `dbo.SellingRate`, `dbo.BuyingRateWithHBL`, `dbo.OtherChargeDetail` | `TransactionDetailsCDCHandler`, `HAWBCDCHandler`, `HAWBDETAILSCDCHandler`, `SellingRateCDCHandler`, `BuyingRateWithHBLCDCHandler`, `OtherChargeDetailCDCHandler` | Skeleton + details + rates |
| `of1_fms_cargo` | [Cargo](#mapping--cargo) | `dbo.HAWB` | `HAWBCDCHandler` (auto-upsert) | GW/CBM/Pieces -> Cargo |
| `of1_fms_container` | [Container](#mapping--container) | `dbo.Transactions.ContainerSize`, `dbo.ContainerListOnHBL` | `TransactionsCDCHandler` (parse text), `ContainerListOnHBLCDCHandler` (line items) | Dual-source |
| `of1_fms_transport_plan` / `of1_fms_transport_route` | [Transport Plan](#mapping--transport-plan--route) | `dbo.Transactions` | `TransactionsCDCHandler` (rebuild) | Delete + recreate per event |
| `of1_fms_purchase_order` / `of1_fms_booking_process` | [Purchase Order](#mapping--purchase-order--booking-process) | — | FMS-only | No CDC (created via UI/API) |

---

## Mapping Coverage Legend

- **CDC-verified** — Handler exists, running in production, mapping confirmed
- **CDC-auto** — Derived from another CDC handler (e.g. Cargo from HAWB)
- **FMS-only** — No BF1 equivalent, created via UI/API

---

## Notes

- Integrated entities (`IntegratedTransaction`, `IntegratedHousebill`, `IntegratedHawbProfit`) are NOT in scope of these mapping docs. They are denormalized mirrors used for reporting. See [[bf1-fms-04-integration|04-integration.md §4.3]] Batch Sync section for Integrated* pipeline mapping.
- All CDC handlers write to both the normalized FMS entity tables AND (where applicable) the Integrated* mirror tables.
- Tenant isolation is enforced via `CDCTenantContext.getCompanyId()` propagated from the Kafka topic name.

---

## Images

- [img/air-import-transaction.png](img/air-import-transaction.png) — sample Air Import transaction data
- [img/air-export-transaction.png](img/air-export-transaction.png) — sample Air Export transaction data

---

## Mapping — Transaction

**Target:** `of1_fms_transactions`
**Source:** `dbo.Transactions` (MSSQL)
**CDC Handler:** `TransactionsCDCHandler` (also writes `integrated_transaction`, parses `ContainerSize` -> Container, rebuilds TransportPlan)

See also: [Container](#mapping--container) · [Transport Plan](#mapping--transport-plan--route) · [House Bill](#mapping--house-bill)

---

### 1. Field Mapping — Common

| FMS Column | Type | Source Column | Notes |
|---|---|---|---|
| `id` | bigserial | — | PK |
| `code` | varchar (UNIQUE) | `TransID` | Ma lo hang |
| `company_id` | bigint | `CDCTenantContext` | From Kafka topic |
| `transaction_date` | timestamp | `TransDate` | Ngay tao lo |
| `issued_date` | date | `IssuedDate` | |
| `loading_date` | timestamp | `LoadingDate` | ETD equivalent |
| `arrival_date` | timestamp | `ArrivalDate` | ETA equivalent |
| `type_of_service` | enum TypeOfService | `TpyeofService` | `TypeOfService.resolve()` |
| `shipment_type` | enum ShipmentType | `ModeSea` | `ShipmentType.parse()` |
| `status` | enum TransactionStatus | `Starus` + `Delivered` | Computed — see §3 |
| `master_bill_no` | varchar | `MAWB` | |
| `from_location_code` | varchar | `PortofLading` -> lookup | `SettingLocationRepository.findByLabel` |
| `from_location_label` | varchar | `PortofLading` | Raw label |
| `to_location_code` | varchar | `PortofUnlading` -> lookup | |
| `to_location_label` | varchar | `PortofUnlading` | |
| `transport_name` | varchar | `AirLine` (lookup partner) / `RefNoSea` | Air: partner name; Sea: vessel name |
| `transport_no` | varchar | `FlghtNo` | Flight/voyage/license plate |
| `manifest_no` | varchar | `Ref` | |
| `coloader_partner_label` | varchar | `ColoaderID` -> lookup | Inbound coloader |
| `coloader_outbound_partner_label` | varchar | `ColoaderID_O` -> lookup | Outbound coloader |
| `handling_agent_partner_id` | bigint | `AgentID` -> lookup | Via `HouseBillLookupSupport.resolveHandlingAgent` |
| `handling_agent_label` | varchar | `AgentID` -> lookup | |
| `created_by_account_name` | varchar | `Attn` -> fallback `WhoisMaking` -> lookup fullname | Priority: `Attn` > FMS user fullname > raw username |
| `cargo_gross_weight_in_kgs` | double | `GrossWeight` | |
| `cargo_chargeable_weight_in_kgs` | double | `ChargeableWeight` | |
| `cargo_volume_in_cbm` | double | `Dimension` (overridden by `SeaCBM` if present) | Sea uses `SeaCBM` |
| `package_quantity` | int | `Noofpieces` | |
| `packaging_type` | varchar | `UnitPieaces` | |
| `container_vol` | varchar | `ContainerSize` | Text — parsed into Container records |
| `desc_of_goods` | varchar | `Description` | |
| `note` | varchar | `ExpressNotes` | On-bill notes |
| `remark` | varchar | `Remark` | Internal staff notes |
| `booking_request_note` | varchar | `BookingRequestNotes` | Customer booking notes |
| `mbl_type` | varchar | `OtherInfo` | M-B/L Type |
| `original_master_bill_no` | varchar | `OMB` | |
| `final_destination` | varchar | `Destination` | |
| `report_info` | varchar | `ReportInfor` | |
| `pre_alert_date` | timestamp | `DateofPrealert` | |

### 2. Service-specific Additional Fields

#### 2.1 Outbound Air

| FMS Column | BF1 Column | BF1 UI Label |
|---|---|---|
| `commodity` | `Description` | `Commodity` |
| `ref` | `Ref` | `B/K No` |
| `package_unit` | `UnitPieaces` | `Unit` |
| `term` | `PaymentTerm` | `Term / D.Date` |
| `note` | `ExpressNotes` | `Notes` |

#### 2.2 Inbound Air

| FMS Column | BF1 Column | BF1 UI Label |
|---|---|---|
| `etd_transit` | `ETDTransit` | `Etd / T.S` |
| `eta_transit` | `ETATransit` | `Eta / T.S` |
| `commodity` | `Description` | `Commodity` |
| `package_unit` | `UnitPieaces` | `Unit` |
| `transit_port_des` | `TransitPortDes` | `Delivery` |
| `note` | `ExpressNotes` | `Notes` |

---

### 3. Status Computation

HPS has no standard status column. Two related columns:

- **`Starus`** (typo of "Status") — free-text lifecycle (`CREATE`, `OPEN`, `TERM`, `CLOSED`, `CANCEL`, ...). Updated on both Inbound and Outbound Save.
- **`Delivered`** — bit/varchar flag. True when shipment handed over to consignee. Updated on both Inbound and Outbound Save.

**Resolution order** in `TransactionsCDCHandler.computeStatus()`:

1. If `Starus` maps to `CLOSED` or `CANCELED` -> keep as-is (terminal state, `Delivered` cannot override)
2. Else if `Delivered = true` -> `DELIVERED`
3. Else -> map `Starus` via `TransactionStatus.resolve()` (may be null)
4. If null -> don't overwrite existing FMS status

`parseBoolFlag()` accepts: Boolean, Number (0/1), String (`"1"` / `"0"` / `"true"` / `"false"` / `"Y"` / `"N"`).

---

### 4. Side Effects (during upsert)

In addition to saving `of1_fms_transactions`, `TransactionsCDCHandler.saveFmsTransaction()` triggers:

1. **Container upsert** — parses `ContainerSize` text (e.g. `"2x40HC & 1x20"`) and upserts Container records by type. See [Container](#mapping--container).
2. **Transport Plan rebuild** — deletes existing `TransportPlan` + `TransportRoute` for the HouseBill and recreates based on `PortofLading`/`PortofUnlading`/`TransitPortFrom`/`TransitPortDes`/dates. See [Transport Plan](#mapping--transport-plan--route).
3. **IntegratedTransaction mirror** — parallel write to `integrated_transaction` for denormalized reporting.

---

## Mapping — House Bill

**Targets:** `of1_fms_house_bill`, `of1_fms_house_bill_detail_base`, `of1_fms_air_house_bill_detail`, `of1_fms_sea_house_bill_detail`, `of1_fms_hawb_rates`

**Sources:** `dbo.TransactionDetails`, `dbo.HAWB`, `dbo.HAWBDETAILS`, `dbo.SellingRate`, `dbo.BuyingRateWithHBL`, `dbo.OtherChargeDetail`

**CDC Handlers:**
- `TransactionDetailsCDCHandler` — skeleton + client/saleman + description/packaging
- `HAWBCDCHandler` — cargo weights, container, consigned date, handling agent + auto-upsert Cargo
- `HAWBDETAILSCDCHandler` — air/sea detail line items
- `SellingRateCDCHandler` — Debit rate items
- `BuyingRateWithHBLCDCHandler` — Credit rate items
- `OtherChargeDetailCDCHandler` — On_Behalf items

See also: [Transaction](#mapping--transaction) · [Cargo](#mapping--cargo) · [Container](#mapping--container)

---

### 1. `of1_fms_house_bill` — Field Ownership

Different CDC handlers own different fields. Skeleton is created by `TransactionDetailsCDCHandler`; `HAWBCDCHandler` enriches with cargo-related data.

| FMS Column | Type | Source Table | Source Column | Owner Handler | Lookup |
|---|---|---|---|---|---|
| `id` | bigserial | — | — | — | PK |
| `hawb_no` | varchar (UNIQUE) | `TransactionDetails` | `HWBNO` | TransactionDetails | |
| `company_id` | bigint | — | `CDCTenantContext` | TransactionDetails | |
| `transaction_id` | bigint | `TransactionDetails` | `TRANSID` | TransactionDetails | `HouseBillLookupSupport.resolveTransaction` |
| `type_of_service` | enum | `Transactions` (via lookup) | — | TransactionDetails | `resolveTransaction.typeOfService` |
| `shipment_type` | varchar | `TransactionDetails` | `ShipmentType` | TransactionDetails | |
| `client_partner_id` | bigint | `TransactionDetails` | `ContactID` | TransactionDetails | `resolveClient.id` |
| `client_label` | varchar | `TransactionDetails` | `ContactID` -> lookup | TransactionDetails | `resolveClient.label` |
| `shipper_partner_id` / `shipper_label` | bigint / varchar | `TransactionDetails` | `ShipperID` | TransactionDetails | Partner lookup |
| `consignee_partner_id` / `consignee_label` | bigint / varchar | `HAWB` | `ConsigneeID` | **HAWB** | `resolveClient` |
| `saleman_account_id` / `saleman_label` | bigint / varchar | `TransactionDetails` | `SalesManID` | TransactionDetails | `resolveSaleman` |
| `desc_of_goods` | varchar | `TransactionDetails` | `Description` | TransactionDetails | |
| `packaging_type` | varchar | `TransactionDetails` | `UnitDetail` | TransactionDetails | |
| `issued_date` | date | `Transactions` (via lookup) | — | TransactionDetails | `resolveTransaction.issuedDate` |
| `handling_agent_partner_id` | bigint | `HAWB` / `Transactions` | `HBAgentID` / `AgentID` | **HAWB** | `resolveHandlingAgent` (HAWB primary, Transaction fallback) |
| `handling_agent_label` | varchar | same | same | **HAWB** | same |
| `assignee_account_id` / `assignee_label` | bigint / varchar | `Transactions` (via lookup) | — | **HAWB** | `resolveTransaction.createdByAccountId/Name` |
| `cargo_gross_weight_in_kgs` | double | `HAWB` | `GrossWeight` | **HAWB** | |
| `cargo_chargeable_weight_in_kgs` | double | `HAWB` | `ChargeableWeight` | **HAWB** | |
| `cargo_volume_in_cbm` | double | `HAWB` | `Dimension` | **HAWB** | |
| `container_vol` | varchar | `HAWB` | `ContainerSize` | **HAWB** | |
| `package_quantity` | int | `HAWB` | `Pieces` | **HAWB** | |
| `consigned_date` | timestamp | `HAWB` | `CussignedDate` (typo) | **HAWB** | Handover to carrier |
| `booking_process_id` | bigint | — | — | FMS-only | Null from CDC |

---

### 2. `of1_fms_house_bill_detail_base`

**CDC Handler:** `HAWBDETAILSCDCHandler.mapBaseFields()`

| FMS Column | Source Column |
|---|---|
| `id` | PK |
| `house_bill_id` | FK -> `of1_fms_house_bill.id` |
| `description_of_goods` | `HAWBDETAILS.Description` |
| `weight` | `HAWBDETAILS.GrossWeight` |
| `volume` | `HAWBDETAILS.CBM` |
| `quantity` | `HAWBDETAILS.NoPieces` (parsed: strips non-numeric) |
| `unit` | `HAWBDETAILS.Unit` |
| `rate_amount` | `HAWBDETAILS.RateCharge` |

---

### 3. Service-specific details

#### 3.1 `of1_fms_air_house_bill_detail`

**CDC Handler:** `HAWBDETAILSCDCHandler.upsertAirDetail()` — when `typeOfService` does NOT contain sea.

Inherits base fields. Additional: `shipper_*`, `consignee_*`, `notify_party_*`, `no_of_original_hbl` (default 3).

`shipper_*` / `consignee_*` copied from HouseBill (populated by TransactionDetails + HAWB handlers).

#### 3.2 `of1_fms_sea_house_bill_detail`

**CDC Handler:** `HAWBDETAILSCDCHandler.upsertSeaDetail()` — when `typeOfService` is one of `SEA_EXPORT_FCL/LCL`, `SEA_IMPORT_FCL/LCL`.

Air fields + `manifest_no` (from `Transaction.manifestNo` / `Transactions.Ref`), `require_hc_*`, `free_*_note`.

---

### 4. `of1_fms_hawb_rates`

**CDC Handlers:** `SellingRateCDCHandler` (Debit), `BuyingRateWithHBLCDCHandler` (Credit), `OtherChargeDetailCDCHandler` (On_Behalf).

All three write to `HouseBillInvoice` + `HouseBillInvoiceItem` entities.

| FMS Column | SellingRate (Debit) | BuyingRateWithHBL (Credit) | OtherChargeDetail (On_Behalf) |
|---|---|---|---|
| `rate_type` | `'Debit'` (hardcoded) | `'Credit'` (hardcoded) | `'On_Behalf'` (hardcoded) |
| `charge_code` | `FieldName` | `FieldName` | — |
| `charge_name` | `Description` | `Description` | `Description` |
| `quantity` | `Quantity` | `Quantity` | `Quantity` |
| `unit` | `QUnit` | `Unit` | `UnitQty` |
| `unit_price` | `UnitPrice` | `UnitPrice` | — |
| `total` | `TotalValue` | `TotalValue` | `BFVATAmount` |
| `total_tax` | `VAT` | `VAT` | `VAT` |
| `final_charge` | `Amount` | `Amount` | `Amount` |
| `currency` | `Unit` | `Unit` | `Currency` |
| `exchange_rate` | `ExtRateVND` | `ExtRateVND` | — |
| `domestic_currency` | `'VND'` (hardcoded) | `'VND'` (hardcoded) | — |
| `domestic_total` | `ExtVND` | `ExtVND` | — |
| `payer_label` | — | — | `PartnerID` |
| `payee_label` | `OBHPartnerID` | `OBHPartnerID` | — |
| `reference_code` | derived `SR-{IDKeyIndex}` | derived `BR-{IDKeyIndex}` | derived `OC-{IDKeyIndex}` |

---

## Mapping — Cargo

**Target:** `of1_fms_cargo`
**Source:** `dbo.HAWB` + `dbo.TransactionDetails` (auto-upsert)
**CDC Handler:** `HAWBCDCHandler.upsertCargo()` — called after `enrichHouseBill()`

See also: [House Bill](#mapping--house-bill) · [Container](#mapping--container)

---

### 1. Overview

Cargo records are **not** directly mapped from a dedicated source table. Instead, `HAWBCDCHandler` auto-upserts a single Cargo record per HouseBill using aggregate cargo metrics from `dbo.HAWB` plus enrichment fields already populated on HouseBill by the `TransactionDetailsCDCHandler`.

**Why auto-upsert?** Before this change, the Cargo table was only populated via manual UI/API input. The aggregate cargo data (weight, volume, pieces) was visible on Transaction/HouseBill but not on Cargo, creating a data gap for downstream consumers querying cargo directly.

---

### 2. MSSQL Source Tables

Cargo is built from **2 MSSQL tables** via 2 CDC handlers:

```
dbo.HAWB (CDC)
  ├─ GrossWeight ──> HAWBCDCHandler.upsertCargo() ──> Cargo.weight
  ├─ Dimension ────> HAWBCDCHandler.upsertCargo() ──> Cargo.volume
  └─ Pieces ───────> HAWBCDCHandler.upsertCargo() ──> Cargo.packageQuantity

dbo.TransactionDetails (CDC)
  ├─ Description ──> TransactionDetailsCDCHandler ──> HouseBill.descOfGoods ──> Cargo.descOfGoods
  └─ UnitDetail ───> TransactionDetailsCDCHandler ──> HouseBill.packagingType ──> Cargo.packagingType
```

**Execution order matters:** `TransactionDetailsCDCHandler` must run before `HAWBCDCHandler` for `descOfGoods` and `packagingType` to flow through. If HAWB CDC arrives first, these fields will be null until the next HAWB CDC event.

---

### 3. Upsert Logic

```
HAWBCDCHandler.handleCreate/Update(event)
  ├─ save(IntegratedHousebill)
  └─ enrichHouseBill(data, hawbNo)
       ├─ save(HouseBill)  <- cargo fields populated here
       └─ upsertCargo(hb, data)
            ├─ find existing: cargoRepo.findByHouseBillId(hb.id)
            ├─ if exists -> update first record
            ├─ else -> create new with hb.id + companyId
            └─ save
```

Upsert key: **first Cargo record with matching `house_bill_id`** (one Cargo per HouseBill from CDC; additional Cargo line items can be created manually via UI).

---

### 4. Field Mapping

| FMS Column | MSSQL Table | MSSQL Column | Transform | Notes |
|---|---|---|---|---|
| `id` | — | — | — | PK auto-generated |
| `house_bill_id` | — | — | `hb.getId()` | FK to `of1_fms_house_bill` |
| `company_id` | — | — | `CDCTenantContext.getCompanyId()` | Tenant |
| `weight` | `dbo.HAWB` | `GrossWeight` | `parseDouble()` | Only written if non-null |
| `volume` | `dbo.HAWB` | `Dimension` | `parseDouble()` | CBM — only written if non-null |
| `package_quantity` | `dbo.HAWB` | `Pieces` | `parseDouble().intValue()` | Only written if non-null |
| `desc_of_goods` | `dbo.TransactionDetails` | `Description` | Via HouseBill | Populated by `TransactionDetailsCDCHandler`, read from `hb.descOfGoods` |
| `packaging_type` | `dbo.TransactionDetails` | `UnitDetail` | Via HouseBill | Populated by `TransactionDetailsCDCHandler`, read from `hb.packagingType` |

---

### 5. Fields NOT populated by CDC

These remain null from CDC and are expected to be filled manually via UI/API:

| Field | Purpose |
|---|---|
| `container_id` | Link to specific container (manual assignment) |
| `commodity_code` | Commodity classification code |
| `commodity_type` | Commodity type classification |
| `commodity_desc` | Commodity description |
| `hs_code` | Customs HS code |
| `dimension_l` / `dimension_w` / `dimension_h` | Per-item dimensions in cm |
| `stackable` | Stackability flag (STACKABLE / NON_STACKABLE) |

---

### 6. Implementation Reference

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java`

Method: `upsertCargo(HouseBill hb, Map<String, Object> data)` — called at end of `enrichHouseBill()` inside the `housebill:` lock.

Guard: skips if `hb.getId() == null` (HouseBill skeleton must exist — created by `TransactionDetailsCDCHandler` first).

---

## Mapping — Container

**Target:** `of1_fms_container`

**Sources (two):**
1. `dbo.Transactions.ContainerSize` — text field parsed into type+quantity records
2. `dbo.ContainerListOnHBL` — individual container records with container_no + seal_no

**CDC Handlers:**
- `TransactionsCDCHandler.upsertContainersFromSize()` — parses `ContainerSize` text
- `ContainerListOnHBLCDCHandler.upsert()` — line-item container records

See also: [Transaction](#mapping--transaction) · [Cargo](#mapping--cargo)

---

### 1. Dual Source Strategy

Containers are populated from two independent CDC streams that coexist on the same `of1_fms_container` table:

| Source | Scope | Key Fields | Upsert Key |
|--------|-------|-----------|------------|
| `Transactions.ContainerSize` | Aggregate — counts per container type | `container_type`, `quantity` | `(transaction_id, container_type)` |
| `ContainerListOnHBL` | Per-container — real container numbers + seals | `container_no`, `seal_no`, `gross_weight_in_kg`, `volume_in_cbm` | `(transaction_id, container_no)` |

**Rationale:** Legacy BF1 stores container info in two places. Some shipments have only `ContainerSize` text (e.g. `"2x40HC & 1x20"`) without per-container details; others have full `ContainerListOnHBL` line items. FMS merges both into one table so downstream consumers see a unified view.

---

### 2. Source 1 — `Transactions.ContainerSize`

**CDC Handler:** `TransactionsCDCHandler.upsertContainersFromSize()` — called from `saveFmsTransaction()` after the Transaction itself is saved.

#### 2.1 Parser

Regex: `(\d+)\s*[xX]\s*(.+)` on each `&`-split segment.

Examples:

| Input | Parsed |
|---|---|
| `"2x40HC & 1x20"` | `[{qty=2, type="40HC"}, {qty=1, type="20"}]` |
| `"1 x 40"` | `[{qty=1, type="40"}]` |
| `"3X20GP"` | `[{qty=3, type="20GP"}]` |
| `""` or null | `[]` (skip) |
| `"invalid"` | `[]` (no `x` separator) |

#### 2.2 Upsert Logic

For each parsed `(quantity, type)`:

1. Lookup existing Containers for `transaction_id` where `containerType` (uppercase) matches
2. If found -> update `quantity`
3. Else -> create new Container with `transaction_id`, `company_id` (from `CDCTenantContext`), `container_type`, `quantity`

**Note:** This source does NOT populate `container_no`, `seal_no`, `gross_weight_in_kg`, `volume_in_cbm`. Those fields come from Source 2.

#### 2.3 Field Mapping (Source 1)

| FMS Column | Source | Notes |
|---|---|---|
| `id` | — | PK |
| `transaction_id` | `fmsTx.getId()` | FK |
| `company_id` | `CDCTenantContext.getCompanyId()` | Tenant |
| `container_type` | Parsed from `ContainerSize` text | Upper-cased lookup key |
| `quantity` | Parsed integer -> double | E.g. `2.0` for `"2x40HC"` |

---

### 3. Source 2 — `ContainerListOnHBL`

**CDC Handler:** `ContainerListOnHBLCDCHandler`

#### 3.1 Upsert Key

`(transaction_id, container_no)` — resolved via HouseBill lookup:

```
HBLNo → findByHawbNo(HouseBill) → getTransactionId()
```

If HouseBill not found or `transactionId == null`, the container event is skipped with a warning.

#### 3.2 Field Mapping (Source 2)

| FMS Column | Source Column | Notes |
|---|---|---|
| `id` | — | PK |
| `transaction_id` | `HouseBill.transactionId` (via `HBLNo` lookup) | FK |
| `company_id` | `CDCTenantContext.getCompanyId()` | Tenant |
| `container_no` | `ContainerNo` | Upsert key |
| `container_type` | `ContainerType` | |
| `seal_no` | `SealNo` | |
| `quantity` | `Qty` (int -> double) | |
| `gross_weight_in_kg` | `GW` (parseDouble) | |
| `volume_in_cbm` | `CBM` (parseDouble) | |

#### 3.3 Delete

`handleDelete()` soft-deletes: sets `storage_state = ARCHIVED` (does not hard-delete).

#### 3.4 Locking

Lock key: `"container:" + hblNo + ":" + containerNo` — allows concurrent updates on different containers of the same HBL.

---

### 4. Coexistence Notes

- A single Transaction can have Container records from both sources simultaneously
- Source 1 records typically have `container_no == null` (aggregate only)
- Source 2 records have `container_no` populated (line items)
- Consumers filtering by `container_no IS NOT NULL` get only real line items
- Consumers summing `quantity` across all records for a transaction should de-duplicate carefully (Source 1 aggregates may conflict with Source 2 counts)

---

### 5. Implementation Reference

**Source 1:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java` — `upsertContainersFromSize()`, `parseContainerSize()`, `ContainerParsed` record.

**Source 2:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/ContainerListOnHBLCDCHandler.java`

---

## Mapping — Transport Plan & Route

**Targets:** `of1_fms_transport_plan`, `of1_fms_transport_route`
**Source:** `dbo.Transactions`
**CDC Handler:** `TransactionsCDCHandler.saveTransportPlan()` — rebuilt on every Transaction CDC event

See also: [Transaction](#mapping--transaction)

---

### 1. MSSQL Source Table: `dbo.Transactions`

#### 1.1 Full Schema (HPS_TEST_DB)

| Column | Type | Used by TransportPlan | Used by Transaction |
|---|---|---|---|
| `TransID` | nvarchar(50) | — | PK / code |
| `ManifestNo` | nvarchar(50) | — | manifestNo |
| `TransDate` | datetime | — | transactionDate |
| `ModifyDate` | datetime | — | — |
| `LoadingDate` | datetime | **departTime** | loadingDate |
| `FlightScheduleRequest` | datetime | — | — |
| `ArrivalDate` | datetime | **arrivalTime** | arrivalDate |
| `ColoaderID` | nvarchar(50) | **carrierLabel** (lookup) | coloaderPartnerLabel |
| `ContactID` | nvarchar(50) | — | — |
| `RouteDelivery` | nvarchar(50) | — | routeDelivery |
| `Destination` | nvarchar(150) | — | finalDestination |
| `Attn` | nvarchar(150) | — | createdByAccountName |
| `AirPortID` | nvarchar(150) | — | — |
| `Description` | nvarchar(255) | — | descOfGoods |
| `Noofpieces` | float | — | packageQuantity |
| `UnitPieaces` | nvarchar(50) | — | packagingType |
| `GrossWeight` | float | — | cargoGrossWeightInKgs |
| `ChargeableWeight` | float | — | cargoChargeableWeightInKgs |
| `AirDimension` | nvarchar(150) | — | — |
| `Length` | float | — | — |
| `Width` | float | — | — |
| `Height` | float | — | — |
| `Dimension` | float | — | cargoVolumeInCbm |
| `RateRequest` | nvarchar(50) | — | — |
| `PaymentTerm` | nvarchar(50) | — | paymentTerm |
| `TransactionNotes` | varchar(8000) | — | — |
| `TpyeofService` | nvarchar(50) | — | typeOfService |
| `MAWB` | nvarchar(50) | — | masterBillNo |
| `FlghtNo` | nvarchar(50) | **transportNo** | transportNo |
| `FlightDateConfirm` | datetime | **flightDateConfirm** | — |
| `AgentID` | nvarchar(50) | — | handlingAgent |
| `PayableAgentID` | nvarchar(50) | — | — |
| `ExpressNotes` | nvarchar(255) | — | note |
| `TotalBuyingRate` | float | — | — |
| `TotalSellingRate` | float | — | — |
| `TotalProfitshared` | float | — | — |
| `Profit` | int | — | — |
| `BookingRequestNotes` | nvarchar(150) | — | bookingRequestNote |
| `WhoisMaking` | nvarchar(50) | — | createdByAccountName (fallback) |
| `Consign` | nvarchar(50) | — | — |
| `TransactionDone` | bit | — | — |
| `DeliverDateText` | nvarchar(50) | — | — |
| `DestinationDate` | datetime | — | destinationDate |
| `Delivered` | bit | — | status (DELIVERED flag) |
| `Reported` | bit | — | — |
| `ReportInfor` | varchar(8000) | — | reportInfo |
| `OMB` | nvarchar(50) | — | originalMasterBillNo |
| `AirLine` | nvarchar(255) | — | transportName (air) |
| `MarksRegistration` | nvarchar(150) | — | — |
| `PortofLading` | nvarchar(150) | **fromLocationLabel/Code** | fromLocation |
| `PortofUnlading` | nvarchar(150) | **toLocationLabel/Code** | toLocation |
| `ModeSea` | nvarchar(50) | — | shipmentType |
| `Consolidatater` | nvarchar(150) | — | — |
| `DeConsolidatater` | nvarchar(150) | — | — |
| `Forwarder` | nvarchar(255) | — | — |
| `Notes` | nvarchar(255) | — | — |
| `NatureofGoods` | ntext | — | — |
| `ColoaderRouting` | ntext | — | — |
| `PSAC` | bit | — | — |
| `CargoOnly` | bit | — | — |
| `NonRadioactive` | bit | — | — |
| `Radioactive` | bit | — | — |
| `HandlingInformation` | nvarchar(255) | — | — |
| `ShipperRef` | nvarchar(50) | — | — |
| `IssuedPlace` | nvarchar(50) | — | — |
| `IssuedDate` | datetime | — | issuedDate |
| `LCL` | bit | — | — |
| `FCL` | bit | — | — |
| `SeaCBM` | float | — | cargoVolumeInCbm (override) |
| `SeaUnit` | nvarchar(50) | — | — |
| `Revision` | datetime | — | — |
| `EstimatedVessel` | nvarchar(150) | — | — |
| `ContSealNo` | nvarchar(150) | — | contSealNo |
| `Starus` | nvarchar(100) | — | status |
| `Remark` | nvarchar(4000) | — | remark |
| `Ref` | nvarchar(255) | — | manifestNo |
| `Amount` | nvarchar(50) | — | — |
| `ETA` | datetime | — | — |
| `RoleShipper` | nvarchar(255) | — | — |
| `RoleATTN` | nvarchar(255) | — | — |
| `RoleFrom` | nvarchar(255) | — | — |
| `DateofPrealert` | datetime | — | preAlertDate |
| `NoofPages` | numeric | — | — |
| `ATTNofPrealert` | nvarchar(150) | — | — |
| `NoofMAWB` | int | — | — |
| `NoofHAWB` | int | — | — |
| `NoInvoice` | int | — | — |
| `NoofDebitNote` | int | — | — |
| `OtherInfo` | nvarchar(255) | — | mblType |
| `transLock` | bit | — | — |
| `TransUnlock` | bit | — | — |
| `TransLockLog` | bit | — | — |
| `TransUnlockLog` | bit | — | — |
| `SeaRevised` | nvarchar(150) | — | — |
| `RefNoSea` | nvarchar(150) | **transportName** | transportName (sea) |
| `ContainerSize` | nvarchar(150) | — | containerVol |
| `assigned` | decimal | — | — |
| `customs` | bit | — | — |
| `Accs` | bit | — | — |
| `AccsUnlock` | bit | — | — |
| `ConsoleNoteCarrier` | nvarchar(255) | — | — |
| `ConsoleNoteAgent` | nvarchar(255) | — | — |
| `ConsoleNoteShipper` | nvarchar(255) | — | — |
| `ConsoleNoteOthers` | nvarchar(255) | — | — |
| `Approved` | bit | — | — |
| `Approvedby` | nvarchar(50) | — | — |
| `ApproveDate` | datetime | — | — |
| `Cancelled` | bit | — | — |
| `RefSellingRate` | nvarchar(255) | — | — |
| `ExpressCW` | float | — | — |
| `ExpressRate` | float | — | — |
| `ExpressUnit` | nvarchar(50) | — | — |
| `LogSV` | nvarchar(50) | — | — |
| `ETATransit` | datetime | **leg1 arrival / leg2 depart** | etaTransit |
| `TransitPortDes` | nvarchar(150) | **transit destination** | transitPortDes |
| `ETDTransit` | datetime | **leg2 depart / leg1 arrival** | etdTransit |
| `OceanVesselName` | nvarchar(50) | — | — |
| `OceanVoy` | nvarchar(50) | — | — |
| `ShowMark` | bit | — | — |
| `AlertDate` | datetime | — | — |
| `AlertPreview` | bit | — | — |
| `ETATransitAlertDate` | datetime | — | — |
| `ETATransitAlertPreview` | bit | — | — |
| `ErrorAttr` | bit | — | — |
| `ColoaderID_O` | nvarchar(50) | — | coloaderOutboundPartnerLabel |
| `TransitPortFrom` | nvarchar(200) | **transit origin** | transitPortFrom |
| `AlertETDDate` | datetime | — | — |
| `AlertETDTransitDate` | datetime | — | — |
| `AlertETDPreview` | bit | — | — |
| `AlertETDTransitPreview` | bit | — | — |
| `CareToOfficeID` | nvarchar(50) | — | — |
| `DocsFolder` | nvarchar(255) | — | — |
| `ColoaderRouting_html` | ntext | — | — |
| `CustomsPortID` | nvarchar(50) | — | — |

**Bold** = columns used by TransportPlan/Route mapping.

#### 1.2 Columns Used by TransportPlan

| MSSQL Column | Type | FMS Target | Transform |
|---|---|---|---|
| `PortofLading` | nvarchar(150) | `from_location_label` + `from_location_code` | Direct + location lookup |
| `PortofUnlading` | nvarchar(150) | `to_location_label` + `to_location_code` | Direct + location lookup |
| `LoadingDate` | datetime | `depart_time` | `toTimestamp()` |
| `ArrivalDate` | datetime | `arrival_time` | `toTimestamp()` |
| `FlightDateConfirm` | datetime | `flight_date_confirm` | `toTimestamp()` |
| `FlghtNo` | nvarchar(50) | Route `transport_no` | Direct |
| `RefNoSea` | nvarchar(150) | `transport_name` | Direct (vessel name) |
| `TransitPortFrom` | nvarchar(200) | Route leg location | Direct + location lookup |
| `TransitPortDes` | nvarchar(150) | Route leg location | Direct + location lookup |
| `ETDTransit` | datetime | Route leg times | `toTimestamp()` |
| `ETATransit` | datetime | Route leg times | `toTimestamp()` |
| `ColoaderID` | nvarchar(50) | Route `carrier_label` | Partner name lookup via CRM |

#### 1.3 Lookup Tables

| Lookup | Source | Method |
|---|---|---|
| Location code | `of1_fms_settings_location` (PG) | `SettingLocationRepository.findByLabel(label)` -> `code`. Fallback: label as code. |
| Partner name | CRM RPC service | `CRMGateway.getPartnerLabel(companyCode, partnerCode)`. Cached via `CDC_PARTNER_CACHE`. |

---

### 2. Rebuild Strategy

On every Transaction CDC event (`handleCreate` / `handleUpdate` / `handleSnapshot`):

1. Save/update `of1_fms_transactions` record
2. `linkOrphanHouseBills()` — link any unlinked HouseBills to this Transaction via MSSQL lookup
3. Query ALL HouseBills linked to this Transaction (`houseBillRepo.findByTransactionId(tx.id)`)
4. For each HouseBill:
   a. Delete ALL existing `TransportPlan` (and cascading `TransportRoute`)
   b. Build fresh `TransportPlan` + `TransportRoute` legs
   c. Save

**Rationale:** BF1 route data is simple and changes atomically. Rebuilding is safer than merging and avoids stale leg state.

**HouseBill resolution:** Uses `transactionId` FK (not HWBNO from CDC data, since `dbo.Transactions` does not have HWBNO column — that field is in `TransactionDetails`). Depends on `linkOrphanHouseBills()` running first.

---

### 3. TransportPlan Fields

| FMS Column | MSSQL Column | Transform | Notes |
|---|---|---|---|
| `id` | — | — | PK |
| `house_bill_id` | — | `HouseBill.id` via transactionId lookup | FK |
| `company_id` | — | `CDCTenantContext.getCompanyId()` | Tenant |
| `from_location_label` | `PortofLading` | Direct | POL label |
| `from_location_code` | `PortofLading` | `lookupLocationCode()` | POL code |
| `to_location_label` | `PortofUnlading` | Direct | POD label |
| `to_location_code` | `PortofUnlading` | `lookupLocationCode()` | POD code |
| `depart_time` | `LoadingDate` | `toTimestamp()` | ETD |
| `arrival_time` | `ArrivalDate` | `toTimestamp()` | ETA |
| `transport_name` | `RefNoSea` | Direct | Vessel name |
| `flight_date_confirm` | `FlightDateConfirm` | `toTimestamp()` | |
| `booking_process_id` | — | — | Not populated by CDC |

---

### 4. TransportRoute Legs

#### 4.1 Direct Route (no transit)

Condition: `TransitPortFrom == null AND TransitPortDes == null`

One route: POL -> POD

| Route Field | MSSQL Column | Notes |
|---|---|---|
| `from_location_label/code` | `PortofLading` | |
| `to_location_label/code` | `PortofUnlading` | |
| `depart_time` | `LoadingDate` | |
| `arrival_time` | `ArrivalDate` | |
| `transport_no` | `FlghtNo` | |
| `carrier_label` | `ColoaderID` | Via `lookupPartnerName()` |
| `sort_order` | — | `0` |

#### 4.2 Transit Route (2 legs)

Condition: `TransitPortFrom != null OR TransitPortDes != null`

Normalization: if only one transit port is supplied, it's used for both ends.

**Leg 1 — POL -> Transit:**

| Route Field | MSSQL Column | Notes |
|---|---|---|
| `from_location_label/code` | `PortofLading` | |
| `to_location_label/code` | `TransitPortFrom` | Fallback: `TransitPortDes` |
| `depart_time` | `LoadingDate` | |
| `arrival_time` | `ETATransit` | Fallback: `ETDTransit` |
| `transport_no` | `FlghtNo` | |
| `carrier_label` | `ColoaderID` | Via `lookupPartnerName()` |
| `sort_order` | — | `0` |

**Leg 2 — Transit -> POD:**

| Route Field | MSSQL Column | Notes |
|---|---|---|
| `from_location_label/code` | `TransitPortDes` | Fallback: `TransitPortFrom` |
| `to_location_label/code` | `PortofUnlading` | |
| `depart_time` | `ETDTransit` | Fallback: `ETATransit` |
| `arrival_time` | `ArrivalDate` | |
| `transport_no` | `FlghtNo` | |
| `carrier_label` | `ColoaderID` | Via `lookupPartnerName()` |
| `sort_order` | — | `1` |

Both legs share the same `transport_no` and `carrier_label`.

#### 4.3 Fields NOT populated by CDC

| Route Field | Notes |
|---|---|
| `transport_method_label` | Transport method (Air/Sea/Road) — not set |
| `carrier_partner_id` | Partner FK — only label is set, not ID |

---

### 5. Status

**CDC-verified** — production coverage for basic POL/POD + 1-transit routing.

**Not yet supported from CDC:**
- Multi-hop routing (>2 legs)
- Per-leg carrier assignment (all legs share same carrier)
- Per-leg transport number (all legs share same FlghtNo)
- Manual route overrides (will be wiped on next Transaction CDC event)

---

### 6. Implementation Reference

**File:** `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java`

Methods: `saveTransportPlan()`, `buildTransportPlan()`, `newRoute()`.

---

## Mapping — Purchase Order & Booking Process

**Targets:** `of1_fms_purchase_order`, `of1_fms_booking_process`
**Status:** **FMS-only** — no CDC handler, no BF1 equivalent

See also: [[bf1-fms-03-data-model|03-data-model.md §5]]

---

### 1. Why FMS-only?

BF1 doesn't have a Purchase Order concept. The legacy `BookingLocal` table is not a direct equivalent — it lacks the one-PO-to-many-bookings structure and per-POP (Purchase Order Process) lifecycle tracking.

FMS introduces the PO model to handle cases like: one customer request ("5 cartons, door-to-door, 2 early + 3 mid-month") that maps to multiple bookings, each further decomposing into multiple POPs (trucking, ocean freight, customs clearance, etc.).

See [[bf1-fms-03-data-model|03-data-model.md §5.1 Purchase Order Model]] for the full rationale and example walkthrough.

---

### 2. Record Lifecycle

Both tables are created and updated via FMS UI / REST API, not CDC.

- `of1_fms_purchase_order` — created from a customer request (e.g. sales app creates PO on booking confirmation)
- `of1_fms_booking_process` — cloned from a PO; state transitions (`draft` -> `confirmed` -> `closed`) tracked here
- `of1_fms_house_bill.booking_process_id` — FK link from HouseBill to its owning BookingProcess

---

### 3. Field Reference

#### 3.1 `of1_fms_purchase_order`

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar (UNIQUE) | PO code |
| `order_date` | timestamp | Business date |
| `label` | varchar | Display label |
| `client_partner_id` / `client_label` | bigint / varchar | Customer |
| `assignee_account_id` / `assignee_label` | bigint / varchar | Owner |

#### 3.2 `of1_fms_booking_process`

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar (UNIQUE) | Booking code |
| `type_of_service` | enum TypeOfService | Service type |
| `purchase_order_id` | bigint | FK -> `of1_fms_purchase_order.id` |
| `state` | varchar | `draft` / `confirmed` / `closed` / ... |
| `close_date` | timestamp | Set when transitioning to closed |

---

### 4. Future Integration

When write-back pipelines (Phase 1) go live, BookingProcess state changes may need to sync back to BF1 `BookingLocal` for operational parity. This is not yet implemented.
