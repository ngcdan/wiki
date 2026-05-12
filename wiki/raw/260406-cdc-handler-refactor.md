---
title: "CDC Handler Refactor — 1 Handler per MSSQL Table"
tags: [daily, bf1, cdc, refactor, spec, plan]
created: 2026-04-06
---

# CDC Handler Refactor — 1 Handler per MSSQL Table

Status: Approved

## Mục lục

- [A. Design Spec](#a-design-spec)
- [B. Implementation Plan](#b-implementation-plan)

---

# A. Design Spec

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

## Current State (12 handlers) → Target State (11 handlers)

| # | Handler | MSSQL Source | PostgreSQL Targets |
|---|---|---|---|
| 1 | TransactionsCDCHandler | dbo.Transactions | integrated_transaction, of1_fms_transactions |
| 2 | TransactionDetailsCDCHandler | dbo.TransactionDetails | of1_fms_house_bill |
| 3 | HAWBCDCHandler | dbo.HAWB | integrated_housebill, of1_fms_house_bill (enrich) |
| 4 | HAWBDETAILSCDCHandler | dbo.HAWBDETAILS | of1_fms_air_house_bill_detail, of1_fms_sea_house_bill_detail |
| 5 | HAWBRATECDCHandler | dbo.HAWBRATE | integrated_hawb_profit |
| 6 | PartnersCDCHandler | dbo.Partners | integrated_partner |
| 7 | ContainerListOnHBLCDCHandler | dbo.ContainerListOnHBL | of1_fms_container |
| 8 | SellingRateCDCHandler | dbo.SellingRate | of1_fms_house_bill_invoice, _item |
| 9 | BuyingRateWithHBLCDCHandler | dbo.BuyingRateWithHBL | of1_fms_house_bill_invoice, _item |
| 10 | OtherChargeDetailCDCHandler | dbo.OtherChargeDetail | of1_fms_house_bill_invoice, _item |
| 11 | ExchangeRateCDCHandler | dbo.ExchangeRate | exchange_rate |

## Changes

### 1. Merge FmsTransactionCDCHandler into TransactionsCDCHandler

- Delete `FmsTransactionCDCHandler.java`
- TransactionsCDCHandler save vào cả `IntegratedTransaction` + `Transaction`
- Port field mapping logic từ FmsTransactionCDCHandler
- **Enrich via PG lookup:**
  - `SettingsUserRoleRepository.getByBfsoneUsername(WhoisMaking)` → `fullName` cho `creatorName`
  - `SettingLocationRepository.getByLabel(PortofLading)` → `code` cho `fromLocationCode`
  - `SettingLocationRepository.getByLabel(PortofUnlading)` → `code` cho `toLocationCode`
- Cần thêm method `findByLabel()` vào `SettingLocationRepository`

### 2. Extend HAWBCDCHandler to enrich of1_fms_house_bill

- Sau khi save `IntegratedHousebill`, lookup `HouseBill` by hawbNo
- Nếu found: update enrichment fields (grossWeight, chargeableWeight, cbm, totalPackages)
- Nếu not found: skip
- **Enrich via PG lookup:**
  - `IntegratedPartnerRepository.getByPartnerCode(HBAgentID)` → `agentName`
  - `IntegratedPartnerRepository.getByPartnerCode(ConsigneeID)` → `customerName`

### 3. Rename 4 handlers theo MSSQL table name

- `HAWBDetailsCDCHandler` → `HAWBDETAILSCDCHandler`
- `ContainerListCDCHandler` → `ContainerListOnHBLCDCHandler`
- `BuyingRateCDCHandler` → `BuyingRateWithHBLCDCHandler`
- `OtherChargeCDCHandler` → `OtherChargeDetailCDCHandler`

### 4. Remaining handlers — no logic changes, update comments only

## PostgreSQL Lookup Dependencies

| CDC Handler | Repository | Method | Purpose |
|---|---|---|---|
| TransactionsCDCHandler | SettingsUserRoleRepository | getByBfsoneUsername() | Creator name |
| TransactionsCDCHandler | SettingLocationRepository | findByLabel() (NEW) | Location code |
| HAWBCDCHandler | IntegratedPartnerRepository | getByPartnerCode() | Agent/Customer name |
| HAWBCDCHandler | HouseBillRepository | getByHawbNo() | Enrich HouseBill |
| HAWBRATECDCHandler | IntegratedHousebillRepository | getByHawbNo() | Get transactionId |
| ContainerListOnHBLCDCHandler | HouseBillRepository | getByHawbNo() | Get transactionId |

**Lookups are best-effort with fallback** — location code fallback = label, partner name fallback = null. Data enriched when lookup source CDC fires.

## Files Affected

- **Delete:** `FmsTransactionCDCHandler.java`
- **Modify (merge + enrich):** `TransactionsCDCHandler.java`, `HAWBCDCHandler.java`
- **Rename:** 4 handlers (see above)
- **New method:** `SettingLocationRepository.findByLabel(String label)`
- **Config:** CDC router — remove FmsTransaction, rename 4 handlers

## Risks

- **Order dependency:** PG lookups may return null if dependent CDC hasn't arrived. Acceptable — fields remain null until re-sync.
- **Transaction scope:** Both saves in same `@Transactional`. One fails → both roll back.
- **Performance:** Extra PG lookups per CDC event. Mitigated: simple indexed queries, low-frequency events.

---

# B. Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Tech Stack:** Java 21, Spring Boot, Spring Data JPA, Kafka (Debezium CDC)

---

## Task 1: Add findByLabel to SettingLocationRepository

- [ ] **Step 1:** Add query method:
```java
@Query("SELECT sl FROM SettingLocation sl WHERE sl.label = :label")
SettingLocation findByLabel(@Param("label") String label);
```

- [ ] **Step 2:** Commit `feat(cdc): add findByLabel to SettingLocationRepository for CDC lookup`

---

## Task 2: Merge FmsTransactionCDCHandler into TransactionsCDCHandler

File: `TransactionsCDCHandler.java`

- [ ] **Step 1:** Add imports + dependencies: `TransactionRepository`, `SettingsUserRoleRepository`, `SettingLocationRepository`
- [ ] **Step 2:** Update class comment: `// CDC: dbo.Transactions (MSSQL) -> integrated_transaction, of1_fms_transactions (PostgreSQL)`
- [ ] **Step 3:** Add `saveFmsTransaction(data, transId)` call in handleCreate + handleUpdate
- [ ] **Step 4:** Update handleDelete to archive both entities
- [ ] **Step 5:** Add `saveFmsTransaction` method — port from FmsTransactionCDCHandler

```java
private void saveFmsTransaction(Map<String, Object> data, String transId) {
    Transaction tx = fmsTransactionRepo.findByCode(transId);
    if (tx == null) {
      tx = new Transaction();
      tx.setCode(transId);
      tx.setCompanyId(CDCTenantContext.getCompanyId());
    }
    mapFmsTransactionFields(data, tx);
    fmsTransactionRepo.save(tx);
}
```

- [ ] **Step 6:** Add `mapFmsTransactionFields` — dates, service/shipment type, master bill, locations (with PG lookup), transport, carrier/agent, creator (with PG lookup), cargo, container
- [ ] **Step 7:** Add PG lookup enrichment to `mapFields` (IntegratedTransaction) — location codes + creator name
- [ ] **Step 8:** Add lookup helpers: `lookupLocationCode(label)`, `lookupCreatorName(username)`
- [ ] **Step 9:** Delete `FmsTransactionCDCHandler.java`: `git rm`
- [ ] **Step 10:** Commit `feat(cdc): merge FmsTransactionCDCHandler into TransactionsCDCHandler with PG lookups`

---

## Task 3: Extend HAWBCDCHandler — HouseBill enrich + Partner lookups

- [ ] **Step 1:** Add dependencies: `HouseBillRepository`, `IntegratedPartnerRepository`
- [ ] **Step 2:** Update class comment
- [ ] **Step 3:** Add Partner lookup enrichment to mapFields (agent + customer)
- [ ] **Step 4:** Add `enrichHouseBill(data, hawbNo)` call in handleCreate + handleUpdate
- [ ] **Step 5:** Add `enrichHouseBill` method — lookup HouseBill by hawbNo, update cargo fields

```java
private void enrichHouseBill(Map<String, Object> data, String hawbNo) {
    try {
      HouseBill hb = houseBillRepo.findByHawbNo(hawbNo);
      if (hb == null) return;
      hb.setCargoGrossWeightInKgs(CDCMapperUtils.parseDouble(data.get("GrossWeight")));
      hb.setCargoChargeableWeightInKgs(CDCMapperUtils.parseDouble(data.get("ChargeableWeight")));
      hb.setCargoVolumeInCbm(CDCMapperUtils.parseDouble(data.get("Dimension")));
      Double pieces = CDCMapperUtils.parseDouble(data.get("Pieces"));
      if (pieces != null) hb.setPackageQuantity(pieces.intValue());
      hb.setContainerVol(CDCMapperUtils.trimString(data.get("ContainerSize")));
      houseBillRepo.save(hb);
    } catch (Exception e) { log.debug("HouseBill enrich skipped: {}", hawbNo); }
}
```

- [ ] **Step 6:** Commit `feat(cdc): extend HAWBCDCHandler with HouseBill enrichment and Partner lookups`

---

## Task 4: Rename 4 CDC handlers

- [ ] **Step 1:** `git mv HAWBDetailsCDCHandler.java HAWBDETAILSCDCHandler.java` + update class name + comment
- [ ] **Step 2:** `git mv ContainerListCDCHandler.java ContainerListOnHBLCDCHandler.java` + update
- [ ] **Step 3:** `git mv BuyingRateCDCHandler.java BuyingRateWithHBLCDCHandler.java` + update
- [ ] **Step 4:** `git mv OtherChargeCDCHandler.java OtherChargeDetailCDCHandler.java` + update
- [ ] **Step 5:** `./gradlew compileJava` — verify no compile errors
- [ ] **Step 6:** Commit `refactor(cdc): rename 4 handlers to match MSSQL table names`

---

## Task 5: Update comments on remaining handlers

- [ ] **Step 1:** Verify all handlers have comment: `// CDC: dbo.TableName (MSSQL) -> pg_table_1, pg_table_2 (PostgreSQL)`
- [ ] **Step 2:** Commit if changes needed `chore(cdc): finalize handler comments`

---

## Task 6: Build verification

- [ ] **Step 1:** `./gradlew clean build -x test` — BUILD SUCCESSFUL
- [ ] **Step 2:** `git push`

---

## Liên quan

- [[260408-fms-cdc-housebill]] — Tiếp nối: HouseBill CDC completeness
- [[bf1-fms-cdc-architecture|CDC Architecture]]
- [[bf1-dev-devlog|BF1 Devlog]]
