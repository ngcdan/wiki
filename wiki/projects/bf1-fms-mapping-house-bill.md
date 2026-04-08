---
title: "FMS Mapping - House Bill"
tags: [bf1, fms, mapping]
---

# Mapping — House Bill

**Targets:** `of1_fms_house_bill`, `of1_fms_house_bill_detail_base`, `of1_fms_air_house_bill_detail`, `of1_fms_sea_house_bill_detail`, `of1_fms_hawb_rates`

**Sources:** `dbo.TransactionDetails`, `dbo.HAWB`, `dbo.HAWBDETAILS`, `dbo.SellingRate`, `dbo.BuyingRateWithHBL`, `dbo.OtherChargeDetail`

**CDC Handlers:**
- `TransactionDetailsCDCHandler` — skeleton + client/saleman + description/packaging
- `HAWBCDCHandler` — cargo weights, container, consigned date, handling agent + auto-upsert Cargo
- `HAWBDETAILSCDCHandler` — air/sea detail line items
- `SellingRateCDCHandler` — Debit rate items
- `BuyingRateWithHBLCDCHandler` — Credit rate items
- `OtherChargeDetailCDCHandler` — On_Behalf items

See also: [[bf1-fms-mapping-transaction]] · [[bf1-fms-mapping-cargo]] · [[bf1-fms-mapping-container]]

---

## 1. `of1_fms_house_bill` — Field Ownership

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
| `client_label` | varchar | `TransactionDetails` | `ContactID` → lookup | TransactionDetails | `resolveClient.label` |
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

## 2. `of1_fms_house_bill_detail_base`

**CDC Handler:** `HAWBDETAILSCDCHandler.mapBaseFields()`

| FMS Column | Source Column |
|---|---|
| `id` | PK |
| `house_bill_id` | FK → `of1_fms_house_bill.id` |
| `description_of_goods` | `HAWBDETAILS.Description` |
| `weight` | `HAWBDETAILS.GrossWeight` |
| `volume` | `HAWBDETAILS.CBM` |
| `quantity` | `HAWBDETAILS.NoPieces` (parsed: strips non-numeric) |
| `unit` | `HAWBDETAILS.Unit` |
| `rate_amount` | `HAWBDETAILS.RateCharge` |

---

## 3. Service-specific details

### 3.1 `of1_fms_air_house_bill_detail`

**CDC Handler:** `HAWBDETAILSCDCHandler.upsertAirDetail()` — when `typeOfService` does NOT contain sea.

Inherits base fields. Additional: `shipper_*`, `consignee_*`, `notify_party_*`, `no_of_original_hbl` (default 3).

`shipper_*` / `consignee_*` copied from HouseBill (populated by TransactionDetails + HAWB handlers).

### 3.2 `of1_fms_sea_house_bill_detail`

**CDC Handler:** `HAWBDETAILSCDCHandler.upsertSeaDetail()` — when `typeOfService` is one of `SEA_EXPORT_FCL/LCL`, `SEA_IMPORT_FCL/LCL`.

Air fields + `manifest_no` (from `Transaction.manifestNo` / `Transactions.Ref`), `require_hc_*`, `free_*_note`.

---

## 4. `of1_fms_hawb_rates`

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
