---
title: "FMS Mapping Index"
tags: [bf1, fms, mapping]
---

# CDC Field Mappings

Source MSSQL → FMS PostgreSQL field mappings, organized by **target entity**.

See also: [[bf1-fms-04-integration]] for pipeline architecture, [[bf1-fms-03-data-model]] for entity schemas.

---

## Index by Target Entity

| Target Entity | File | Source Tables | CDC Handler(s) | Notes |
|---|---|---|---|---|
| `of1_fms_transactions` | [[bf1-fms-mapping-transaction]] | `dbo.Transactions` | `TransactionsCDCHandler` | Master bill + parses `ContainerSize` + rebuilds transport plan |
| `of1_fms_house_bill` + details | [[bf1-fms-mapping-house-bill]] | `dbo.TransactionDetails`, `dbo.HAWB`, `dbo.HAWBDETAILS`, `dbo.SellingRate`, `dbo.BuyingRateWithHBL`, `dbo.OtherChargeDetail` | `TransactionDetailsCDCHandler`, `HAWBCDCHandler`, `HAWBDETAILSCDCHandler`, `SellingRateCDCHandler`, `BuyingRateWithHBLCDCHandler`, `OtherChargeDetailCDCHandler` | Skeleton + details + rates |
| `of1_fms_cargo` | [[bf1-fms-mapping-cargo]] | `dbo.HAWB` | `HAWBCDCHandler` (auto-upsert) | GW/CBM/Pieces → Cargo |
| `of1_fms_container` | [[bf1-fms-mapping-container]] | `dbo.Transactions.ContainerSize`, `dbo.ContainerListOnHBL` | `TransactionsCDCHandler` (parse text), `ContainerListOnHBLCDCHandler` (line items) | Dual-source |
| `of1_fms_transport_plan` / `of1_fms_transport_route` | [[bf1-fms-mapping-transport-plan]] | `dbo.Transactions` | `TransactionsCDCHandler` (rebuild) | Delete + recreate per event |
| `of1_fms_purchase_order` / `of1_fms_booking_process` | [[bf1-fms-mapping-purchase-order]] | — | FMS-only | No CDC (created via UI/API) |

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
