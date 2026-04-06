# CDC Handler Refactor - 1 Handler per MSSQL Table

**Date:** 2026-04-06
**Status:** Approved

## Principle

- 1 CDC handler = 1 MSSQL source table
- Each handler can write to multiple PostgreSQL target tables if data is related
- Handler name = MSSQL table name + suffix `CDCHandler`
- Enrich data via PostgreSQL lookups when CDC event lacks JOINed data

## Naming Convention

| MSSQL Table | Handler Name |
|---|---|
| Transactions | TransactionsCDCHandler |
| TransactionDetails | TransactionDetailsCDCHandler |
| HAWB | HAWBCDCHandler |
| HAWBDETAILS | HAWBDETAILSCDCHandler |
| HAWBRATE | HAWBRATECDCHandler |
| Partners | PartnersCDCHandler |
| ContainerListOnHBL | ContainerListOnHBLCDCHandler |
| SellingRate | SellingRateCDCHandler |
| BuyingRateWithHBL | BuyingRateWithHBLCDCHandler |
| OtherChargeDetail | OtherChargeDetailCDCHandler |
| ExchangeRate | ExchangeRateCDCHandler |

**Renames:** HAWBDetailsCDCHandler -> HAWBDETAILSCDCHandler, ContainerListCDCHandler -> ContainerListOnHBLCDCHandler, BuyingRateCDCHandler -> BuyingRateWithHBLCDCHandler, OtherChargeCDCHandler -> OtherChargeDetailCDCHandler

## Current State (12 handlers)

| Handler | MSSQL Source | PostgreSQL Target |
|---|---|---|
| TransactionsCDCHandler | dbo.Transactions | integrated_transaction |
| FmsTransactionCDCHandler | dbo.Transactions | of1_fms_transactions |
| TransactionDetailsCDCHandler | dbo.TransactionDetails | of1_fms_house_bill |
| HAWBCDCHandler | dbo.HAWB | integrated_housebill |
| HAWBDetailsCDCHandler | dbo.HAWBDETAILS | of1_fms_air/sea_house_bill_detail |
| HAWBRATECDCHandler | dbo.HAWBRATE | integrated_hawb_profit |
| PartnersCDCHandler | dbo.Partners | integrated_partner |
| ContainerListCDCHandler | dbo.ContainerListOnHBL | of1_fms_container |
| SellingRateCDCHandler | dbo.SellingRate | of1_fms_house_bill_invoice, _item |
| BuyingRateCDCHandler | dbo.BuyingRateWithHBL | of1_fms_house_bill_invoice, _item |
| OtherChargeCDCHandler | dbo.OtherChargeDetail | of1_fms_house_bill_invoice, _item |
| ExchangeRateCDCHandler | dbo.ExchangeRate | exchange_rate |

## Target State (11 handlers)

| # | Handler | MSSQL Source | PostgreSQL Targets |
|---|---|---|---|
| 1 | TransactionsCDCHandler | dbo.Transactions | integrated_transaction, of1_fms_transactions |
| 2 | TransactionDetailsCDCHandler | dbo.TransactionDetails | of1_fms_house_bill |
| 3 | HAWBCDCHandler | dbo.HAWB | integrated_housebill, of1_fms_house_bill (enrich) |
| 4 | HAWBDETAILSCDCHandler | dbo.HAWBDETAILS | of1_fms_air_house_bill_detail, of1_fms_sea_house_bill_detail |
| 5 | HAWBRATECDCHandler | dbo.HAWBRATE | integrated_hawb_profit |
| 6 | PartnersCDCHandler | dbo.Partners | integrated_partner |
| 7 | ContainerListOnHBLCDCHandler | dbo.ContainerListOnHBL | of1_fms_container |
| 8 | SellingRateCDCHandler | dbo.SellingRate | of1_fms_house_bill_invoice, of1_fms_house_bill_invoice_item |
| 9 | BuyingRateWithHBLCDCHandler | dbo.BuyingRateWithHBL | of1_fms_house_bill_invoice, of1_fms_house_bill_invoice_item |
| 10 | OtherChargeDetailCDCHandler | dbo.OtherChargeDetail | of1_fms_house_bill_invoice, of1_fms_house_bill_invoice_item |
| 11 | ExchangeRateCDCHandler | dbo.ExchangeRate | exchange_rate |

## Changes

### 1. Merge FmsTransactionCDCHandler into TransactionsCDCHandler

- Delete `FmsTransactionCDCHandler.java`
- TransactionsCDCHandler save vao ca `IntegratedTransaction` + `Transaction`
- Port field mapping logic tu FmsTransactionCDCHandler
- **Enrich via PG lookup:**
  - `SettingsUserRoleRepository.getByBfsoneUsername(WhoisMaking)` -> lay `fullName` cho `creatorName` (IntegratedTransaction) va `createdByAccountName` (Transaction)
  - `SettingLocationRepository.getByLabel(PortofLading)` -> lay `code` cho `fromLocationCode` (hien dang set = label)
  - `SettingLocationRepository.getByLabel(PortofUnlading)` -> lay `code` cho `toLocationCode`
- Can them method `findByLabel()` vao `SettingLocationRepository`
- Update CDC router config

### 2. Extend HAWBCDCHandler to enrich of1_fms_house_bill

- Sau khi save `IntegratedHousebill`, lookup `HouseBill` by hawbNo
- Neu found: update enrichment fields (grossWeight, chargeableWeight, cbm, totalPackages)
- Neu not found: skip (TransactionDetails CDC chua tao HouseBill)
- **Enrich via PG lookup:**
  - `IntegratedPartnerRepository.getByPartnerCode(HBAgentID)` -> lay `label` cho `agentName` (IntegratedHousebill)
  - `IntegratedPartnerRepository.getByPartnerCode(ConsigneeID)` -> lay `label` cho `customerName` (IntegratedHousebill)

### 3. Rename 4 handlers theo MSSQL table name

- `HAWBDetailsCDCHandler` -> `HAWBDETAILSCDCHandler`
- `ContainerListCDCHandler` -> `ContainerListOnHBLCDCHandler`
- `BuyingRateCDCHandler` -> `BuyingRateWithHBLCDCHandler`
- `OtherChargeCDCHandler` -> `OtherChargeDetailCDCHandler`
- Update tat ca references (CDC router config, bean registrations)

### 4. Remaining handlers - no logic changes

- Update comments cho tat ca handlers

## PostgreSQL Lookup Dependencies

| CDC Handler | Lookup Repository | Method | Purpose |
|---|---|---|---|
| TransactionsCDCHandler | SettingsUserRoleRepository | getByBfsoneUsername() | Creator name |
| TransactionsCDCHandler | SettingLocationRepository | findByLabel() (NEW) | Location code from name |
| HAWBCDCHandler | IntegratedPartnerRepository | getByPartnerCode() | Agent/Customer name |
| HAWBCDCHandler | HouseBillRepository | getByHawbNo() | Enrich HouseBill |
| HAWBRATECDCHandler | IntegratedHousebillRepository | getByHawbNo() | Get transactionId, etc. |
| ContainerListOnHBLCDCHandler | HouseBillRepository | getByHawbNo() | Get transactionId |

**Note:** Lookups are best-effort with fallback:
- `SettingLocationRepository.findByLabel()` -> if not found, fallback set `locationCode = locationLabel` (same as current behavior)
- `IntegratedPartnerRepository.getByPartnerCode()` -> if not found, set name to null
- `SettingsUserRoleRepository.getByBfsoneUsername()` -> if not found, set creatorName to null
- Data will be enriched when the lookup source CDC fires and triggers re-processing.

## Files Affected

### Delete
- `FmsTransactionCDCHandler.java`

### Modify (merge + enrich)
- `TransactionsCDCHandler.java` - merge FmsTransaction logic + add PG lookups
- `HAWBCDCHandler.java` - add HouseBill enrich + Partner lookups

### Rename
- `HAWBDetailsCDCHandler.java` -> `HAWBDETAILSCDCHandler.java`
- `ContainerListCDCHandler.java` -> `ContainerListOnHBLCDCHandler.java`
- `BuyingRateCDCHandler.java` -> `BuyingRateWithHBLCDCHandler.java`
- `OtherChargeCDCHandler.java` -> `OtherChargeDetailCDCHandler.java`

### New method
- `SettingLocationRepository` - add `findByLabel(String label)`

### Config
- CDC router/config - update handler registrations (remove FmsTransaction, rename 4 handlers)

## Risks

- **Order dependency:** PG lookups may return null if dependent CDC data hasn't arrived yet. This is acceptable - fields remain null until re-sync or next CDC event.
- **Transaction scope:** Both saves (integrated + fms) happen in same @Transactional. If one fails, both roll back.
- **Performance:** Extra PG lookups per CDC event. Mitigated by: lookups are simple primary-key/indexed queries, CDC events are low-frequency.
