# CDC Handler Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor CDC handlers to enforce 1 handler per MSSQL table, with PG lookup enrichment and consistent naming.

**Architecture:** Merge FmsTransactionCDCHandler into TransactionsCDCHandler, extend HAWBCDCHandler to enrich HouseBill, rename 4 handlers to match MSSQL table names, add PG lookups for creator name / location code / partner name.

**Tech Stack:** Java 21, Spring Boot, Spring Data JPA, Kafka (Debezium CDC)

**Spec:** `/Users/nqcdan/dev/wiki/wiki/daily/260406-cdc-handler-refactor.md`

---

### Task 1: Add findByLabel to SettingLocationRepository

**Files:**
- Modify: `module/settings/src/main/java/of1/fms/settings/location/repository/SettingLocationRepository.java`

- [ ] **Step 1: Add findByLabel query method**

```java
@Query("SELECT sl FROM SettingLocation sl WHERE sl.label = :label")
SettingLocation findByLabel(@Param("label") String label);
```

Add this method to `SettingLocationRepository` interface, below the existing `getByCode` method.

- [ ] **Step 2: Commit**

```bash
git add module/settings/src/main/java/of1/fms/settings/location/repository/SettingLocationRepository.java
git commit -m "feat(cdc): add findByLabel to SettingLocationRepository for CDC lookup"
```

---

### Task 2: Merge FmsTransactionCDCHandler into TransactionsCDCHandler

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java`
- Delete: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/FmsTransactionCDCHandler.java`

- [ ] **Step 1: Add new imports and dependencies to TransactionsCDCHandler**

Add these imports:
```java
import of1.fms.core.cdc.context.CDCTenantContext;
import of1.fms.core.common.ShipmentType;
import of1.fms.core.common.TypeOfService;
import of1.fms.module.transaction.entity.Transaction;
import of1.fms.module.transaction.repository.TransactionRepository;
import of1.fms.settings.location.entity.SettingLocation;
import of1.fms.settings.location.repository.SettingLocationRepository;
import of1.fms.settings.user.entity.SettingsUserRole;
import of1.fms.settings.user.repository.SettingsUserRoleRepository;
```

Add these `@Autowired` fields:
```java
@Autowired
private TransactionRepository fmsTransactionRepo;

@Autowired
private SettingsUserRoleRepository userRoleRepo;

@Autowired
private SettingLocationRepository locationRepo;
```

- [ ] **Step 2: Update comment at top of class**

```java
// CDC: dbo.Transactions (MSSQL) -> integrated_transaction, of1_fms_transactions (PostgreSQL)
```

- [ ] **Step 3: Add FMS Transaction logic into handleCreate**

After the existing `transactionRepo.save(tx)` line and before the log line, add:
```java
      // Save to of1_fms_transactions
      saveFmsTransaction(data, transId);
```

Do the same for `handleUpdate`.

- [ ] **Step 4: Update handleDelete to archive both entities**

After the existing archive block for IntegratedTransaction, add:
```java
      Transaction fmsTx = fmsTransactionRepo.findByCode(transId);
      if (fmsTx != null) {
        fmsTx.setStorageState(StorageState.ARCHIVED);
        fmsTransactionRepo.save(fmsTx);
      }
```

- [ ] **Step 5: Add saveFmsTransaction method**

Port `mapFields` logic from `FmsTransactionCDCHandler` into a new private method:
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
    log.debug("CDC saved fms_transaction: {}", transId);
}
```

- [ ] **Step 6: Add mapFmsTransactionFields method**

Copy field mapping from `FmsTransactionCDCHandler.mapFields()`:
```java
private void mapFmsTransactionFields(Map<String, Object> data, Transaction tx) {
    // Dates
    Long transDate = CDCMapperUtils.parseLong(data.get("TransDate"));
    if (transDate != null) tx.setTransactionDate(CDCMapperUtils.toTimestamp(transDate));

    Long loadingDate = CDCMapperUtils.parseLong(data.get("LoadingDate"));
    if (loadingDate != null) tx.setEtd(CDCMapperUtils.toTimestamp(loadingDate));

    Long arrivalDate = CDCMapperUtils.parseLong(data.get("ArrivalDate"));
    if (arrivalDate != null) tx.setEta(CDCMapperUtils.toTimestamp(arrivalDate));

    Long issuedDate = CDCMapperUtils.parseLong(data.get("IssuedDate"));
    if (issuedDate != null) tx.setIssuedDate(CDCMapperUtils.toTimestamp(issuedDate));

    // Service & shipment
    String typeOfServiceStr = CDCMapperUtils.trimString(data.get("TpyeofService"));
    if (typeOfServiceStr != null) {
      try { tx.setTypeOfService(TypeOfService.valueOf(typeOfServiceStr)); } catch (IllegalArgumentException ignored) {}
    }
    String shipmentTypeStr = CDCMapperUtils.trimString(data.get("ModeSea"));
    if (shipmentTypeStr != null) {
      try { tx.setShipmentType(ShipmentType.valueOf(shipmentTypeStr)); } catch (IllegalArgumentException ignored) {}
    }

    // Master bill
    tx.setMasterBillNo(CDCMapperUtils.trimString(data.get("MAWB")));

    // Locations (with PG lookup for code, fallback to label)
    String fromLabel = CDCMapperUtils.trimString(data.get("PortofLading"));
    String toLabel = CDCMapperUtils.trimString(data.get("PortofUnlading"));
    tx.setFromLocationLabel(fromLabel);
    tx.setToLocationLabel(toLabel);
    tx.setFromLocationCode(lookupLocationCode(fromLabel));
    tx.setToLocationCode(lookupLocationCode(toLabel));

    // Transport
    tx.setTransportName(CDCMapperUtils.trimString(data.get("AirLine")));
    tx.setTransportNo(CDCMapperUtils.trimString(data.get("FlghtNo")));

    // Carrier / Agent
    tx.setCarrierLabel(CDCMapperUtils.trimString(data.get("ColoaderID")));
    tx.setHandlingAgentLabel(CDCMapperUtils.trimString(data.get("AgentID")));

    // Creator (with PG lookup for full name)
    String username = CDCMapperUtils.trimString(data.get("WhoisMaking"));
    tx.setCreatedByAccountName(username);

    // Cargo
    tx.setCargoGrossWeightInKgs(CDCMapperUtils.parseDouble(data.get("GrossWeight")));
    tx.setCargoChargeableWeightInKgs(CDCMapperUtils.parseDouble(data.get("ChargeableWeight")));
    tx.setCargoVolumeInCbm(CDCMapperUtils.parseDouble(data.get("Dimension")));

    Double pieces = CDCMapperUtils.parseDouble(data.get("Noofpieces"));
    if (pieces != null) tx.setPackageQuantity(pieces.intValue());

    // Container
    tx.setContainerVol(CDCMapperUtils.trimString(data.get("ContainerSize")));
}
```

- [ ] **Step 7: Add PG lookup enrichment to mapFields (IntegratedTransaction)**

Update the existing `mapFields` method to enrich location codes and creator name:

After location mapping lines, replace:
```java
tx.setFromLocationCode(CDCMapperUtils.trimString(data.get("PortofLading")));
tx.setFromLocationLabel(CDCMapperUtils.trimString(data.get("PortofLading")));
tx.setToLocationCode(CDCMapperUtils.trimString(data.get("PortofUnlading")));
tx.setToLocationLabel(CDCMapperUtils.trimString(data.get("PortofUnlading")));
```
With:
```java
String fromLabel = CDCMapperUtils.trimString(data.get("PortofLading"));
String toLabel = CDCMapperUtils.trimString(data.get("PortofUnlading"));
tx.setFromLocationLabel(fromLabel);
tx.setToLocationLabel(toLabel);
tx.setFromLocationCode(lookupLocationCode(fromLabel));
tx.setToLocationCode(lookupLocationCode(toLabel));
```

After creator username mapping, add:
```java
String username = CDCMapperUtils.trimString(data.get("WhoisMaking"));
tx.setCreatorUsername(username);
tx.setCreatorName(lookupCreatorName(username));
```
And remove the old `tx.setCreatorUsername(...)` line.

- [ ] **Step 8: Add lookup helper methods**

```java
private String lookupLocationCode(String label) {
    if (label == null) return null;
    try {
      SettingLocation loc = locationRepo.findByLabel(label);
      if (loc != null) return loc.getCode();
    } catch (Exception e) {
      log.debug("Location lookup failed for label: {}", label);
    }
    return label; // fallback: code = label
}

private String lookupCreatorName(String username) {
    if (username == null) return null;
    try {
      SettingsUserRole user = userRoleRepo.getByBfsoneUsername(username);
      if (user != null) return user.getFullName();
    } catch (Exception e) {
      log.debug("User lookup failed for username: {}", username);
    }
    return null;
}
```

- [ ] **Step 9: Delete FmsTransactionCDCHandler.java**

```bash
git rm module/transaction/src/main/java/of1/fms/module/transaction/cdc/FmsTransactionCDCHandler.java
```

- [ ] **Step 10: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionsCDCHandler.java
git commit -m "feat(cdc): merge FmsTransactionCDCHandler into TransactionsCDCHandler with PG lookups"
```

---

### Task 3: Extend HAWBCDCHandler to enrich HouseBill + Partner lookups

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java`

- [ ] **Step 1: Add new imports and dependencies**

Add imports:
```java
import of1.fms.module.transaction.entity.HouseBill;
import of1.fms.module.transaction.repository.HouseBillRepository;
import of1.fms.module.partner.entity.IntegratedPartner;
import of1.fms.module.partner.repository.IntegratedPartnerRepository;
```

Add fields:
```java
@Autowired
private HouseBillRepository houseBillRepo;

@Autowired
private IntegratedPartnerRepository partnerRepo;
```

- [ ] **Step 2: Update class comment**

```java
// CDC: dbo.HAWB (MSSQL) -> integrated_housebill, of1_fms_house_bill (PostgreSQL)
```

- [ ] **Step 3: Add Partner lookup enrichment to mapFields**

After `hb.setAgentCode(...)` line, add:
```java
// Enrich agent name from IntegratedPartner
String agentCode = hb.getAgentCode();
if (agentCode != null) {
  try {
    IntegratedPartner agent = partnerRepo.getByPartnerCode(agentCode);
    if (agent != null) hb.setAgentName(agent.getLabel());
  } catch (Exception e) {
    log.debug("Partner lookup failed for agentCode: {}", agentCode);
  }
}
```

After `hb.setCustomerName(...)` line, add enrichment only if customerName is null (CDC already has Consignee field):
```java
// Enrich customer name if not available from CDC
if (hb.getCustomerName() == null && hb.getCustomerCode() != null) {
  try {
    IntegratedPartner customer = partnerRepo.getByPartnerCode(hb.getCustomerCode());
    if (customer != null) hb.setCustomerName(customer.getLabel());
  } catch (Exception e) {
    log.debug("Partner lookup failed for customerCode: {}", hb.getCustomerCode());
  }
}
```

- [ ] **Step 4: Add HouseBill enrichment after IntegratedHousebill save**

In `handleCreate` and `handleUpdate`, after `housebillRepo.save(hb)` and before the log line, add:
```java
      enrichHouseBill(data, hawbNo);
```

- [ ] **Step 5: Add enrichHouseBill method**

```java
private void enrichHouseBill(Map<String, Object> data, String hawbNo) {
    try {
      HouseBill hb = houseBillRepo.findByHawbNo(hawbNo);
      if (hb == null) return; // TransactionDetails CDC hasn't created it yet

      hb.setCargoGrossWeightInKgs(CDCMapperUtils.parseDouble(data.get("GrossWeight")));
      hb.setCargoChargeableWeightInKgs(CDCMapperUtils.parseDouble(data.get("ChargeableWeight")));
      hb.setCargoVolumeInCbm(CDCMapperUtils.parseDouble(data.get("Dimension")));

      Double pieces = CDCMapperUtils.parseDouble(data.get("Pieces"));
      if (pieces != null) hb.setPackageQuantity(pieces.intValue());

      hb.setContainerVol(CDCMapperUtils.trimString(data.get("ContainerSize")));

      houseBillRepo.save(hb);
      log.debug("CDC enriched house_bill: {}", hawbNo);
    } catch (Exception e) {
      log.debug("HouseBill enrich skipped for hawbNo: {}", hawbNo);
    }
}
```

- [ ] **Step 6: Commit**

```bash
git add module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBCDCHandler.java
git commit -m "feat(cdc): extend HAWBCDCHandler with HouseBill enrichment and Partner lookups"
```

---

### Task 4: Rename 4 CDC handlers to match MSSQL table names

**Files:**
- Rename: `HAWBDetailsCDCHandler.java` -> `HAWBDETAILSCDCHandler.java`
- Rename: `ContainerListCDCHandler.java` -> `ContainerListOnHBLCDCHandler.java`
- Rename: `BuyingRateCDCHandler.java` -> `BuyingRateWithHBLCDCHandler.java`
- Rename: `OtherChargeCDCHandler.java` -> `OtherChargeDetailCDCHandler.java`

All in: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/`

- [ ] **Step 1: Rename HAWBDetailsCDCHandler**

```bash
cd module/transaction/src/main/java/of1/fms/module/transaction/cdc
git mv HAWBDetailsCDCHandler.java HAWBDETAILSCDCHandler.java
```

In the file, update:
- Class name: `HAWBDetailsCDCHandler` -> `HAWBDETAILSCDCHandler`
- Comment: `// CDC: dbo.HAWBDETAILS (MSSQL) -> of1_fms_air_house_bill_detail, of1_fms_sea_house_bill_detail (PostgreSQL)`

- [ ] **Step 2: Rename ContainerListCDCHandler**

```bash
git mv ContainerListCDCHandler.java ContainerListOnHBLCDCHandler.java
```

In the file, update:
- Class name: `ContainerListCDCHandler` -> `ContainerListOnHBLCDCHandler`
- Comment: `// CDC: dbo.ContainerListOnHBL (MSSQL) -> of1_fms_container (PostgreSQL)`

- [ ] **Step 3: Rename BuyingRateCDCHandler**

```bash
git mv BuyingRateCDCHandler.java BuyingRateWithHBLCDCHandler.java
```

In the file, update:
- Class name: `BuyingRateCDCHandler` -> `BuyingRateWithHBLCDCHandler`
- Comment: `// CDC: dbo.BuyingRateWithHBL (MSSQL) -> of1_fms_house_bill_invoice, of1_fms_house_bill_invoice_item (PostgreSQL)`

- [ ] **Step 4: Rename OtherChargeCDCHandler**

```bash
git mv OtherChargeCDCHandler.java OtherChargeDetailCDCHandler.java
```

In the file, update:
- Class name: `OtherChargeCDCHandler` -> `OtherChargeDetailCDCHandler`
- Comment: `// CDC: dbo.OtherChargeDetail (MSSQL) -> of1_fms_house_bill_invoice, of1_fms_house_bill_invoice_item (PostgreSQL)`

- [ ] **Step 5: Verify no compile errors**

```bash
./gradlew compileJava
```

No other files reference these handler classes by name (auto-discovery via @Component).

- [ ] **Step 6: Commit**

```bash
git add -A module/transaction/src/main/java/of1/fms/module/transaction/cdc/
git commit -m "refactor(cdc): rename 4 handlers to match MSSQL table names"
```

---

### Task 5: Update comments on remaining handlers

**Files:**
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/TransactionDetailsCDCHandler.java`
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HAWBRATECDCHandler.java`
- Modify: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/SellingRateCDCHandler.java`
- Modify: `module/partner/src/main/java/of1/fms/module/partner/cdc/PartnersCDCHandler.java`
- Modify: `module/settings/src/main/java/of1/fms/settings/currency/cdc/ExchangeRateCDCHandler.java`

Comments already added in earlier commit. Verify they are correct:

- [ ] **Step 1: Verify all handler comments match spec**

Each handler should have comment format: `// CDC: dbo.TableName (MSSQL) -> pg_table_1, pg_table_2 (PostgreSQL)`

- [ ] **Step 2: Commit if any changes needed**

```bash
git add -A
git commit -m "chore(cdc): finalize handler comments"
```

---

### Task 6: Build verification

- [ ] **Step 1: Full build**

```bash
./gradlew clean build -x test
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 2: Final commit + push**

```bash
git push
```
