---
title: "Plan — ECUS Entity Mapping Refactor"
tags: [egov, plans, ecus, mapping, refactor]
created: 2026-03-29
---

# ECUS Entity Mapping Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move pure field mapping logic out of 19 company mapper `mapTo*()` private methods and into ECUS source entities as public `to*(template)` instance methods.

**Architecture:** Each ECUS entity gains a `to[EgovEntity](template)` method. Caller (mapper `processSync()`) prepares the template: find existing OR new entity, set `companyId`/`syncSourceConfigurationId` only when creating new, then call `ecusEntity.to*(template)` and save. The private `mapTo*()` method is deleted entirely. No Spring calls or context access inside `to*()`.

**Tech Stack:** Java 21, Spring Boot 3, JPA, Lombok, JUnit 5, AssertJ. Module dependency `ecus-thaison` → `ecutoms` already exists — no build file changes needed.

---

## File Map

**Entities to modify** — all in `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/`:

| Entity file | New method | eGov import |
|---|---|---|
| `SCUAKHAU.java` | `toBorderGate(BorderGate)` | `com.egov.ecutoms.entity.BorderGate` |
| `SCUAKHAUNN.java` | `toBorderGate(BorderGate)` | same |
| `SHAIQUAN.java` | `toCustomsOffice(CustomsOffice)` | `com.egov.ecutoms.entity.CustomsOffice` |
| `SNUOC.java` | `toEgovCountry(EgovCountry)` | `com.egov.ecutoms.entity.EgovCountry` |
| `SNGTE.java` | `toEgovCurrency(EgovCurrency)` | `com.egov.ecutoms.entity.EgovCurrency` |
| `SDVT.java` | `toEgovUnit(EgovUnit)` | `com.egov.ecutoms.entity.EgovUnit` |
| `SLOAI_KIEN.java` | `toEgovUnit(EgovUnit)` | same |
| `SNGAN_HANG.java` | `toBank(Bank)` | `com.egov.ecutoms.entity.Bank` |
| `SPTTT.java` | `toInvoicePaymentMethod(InvoicePaymentMethod)` | `com.egov.ecutoms.entity.InvoicePaymentMethod` |
| `SPTVT.java` | `toTransportMode(TransportMode)` | `com.egov.ecutoms.entity.TransportMode` |
| `SDKGH.java` | `toInvoiceDeliveryTerms(InvoiceDeliveryTerms)` | `com.egov.ecutoms.entity.InvoiceDeliveryTerms` |
| `SVB_PQ.java` | `toCustomsLegalCode(CustomsLegalCode)` | `com.egov.ecutoms.entity.CustomsLegalCode` |
| `SLOAI_GP.java` | `toTradingLicenseType(TradingLicenseType)` | `com.egov.ecutoms.entity.TradingLicenseType` |
| `SLHINHMD.java` | `toDeclarationType(DeclarationType)` | `com.egov.ecutoms.entity.DeclarationType` |
| `SMA_AP_MIENTHUE.java` | `toTaxExemption(TaxExemption)` | `com.egov.ecutoms.entity.TaxExemption` |
| `SMA_MIENTHUE.java` | `toTaxExemptionCategory(TaxExemptionCategory)` | `com.egov.ecutoms.entity.TaxExemptionCategory` |
| `REPORTSEXCEL.java` | `toCustomsMessageType(CustomsMessageType)` | `com.egov.ecutoms.entity.CustomsMessageType` |
| `SBIEU_THUE_TEN.java` | `toTariffSchedule(TariffSchedule)` | `com.egov.ecutoms.entity.TariffSchedule` |
| `DCHUNGTUKEM.java` | `toAttachedDocument(AttachedDocument)` | `com.egov.ecutoms.entity.AttachedDocument` |

**Mappers to modify** — all in `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/`:
`EcusSCUAKHAUMapper`, `EcusSCUAKHAUNNMapper`, `EcusSHAIQUANMapper`, `EcusSNUOCMapper`, `EcusSNGTEMapper`, `EcusSDVTMapper`, `EcusSLOAI_KIENMapper`, `EcusSNGAN_HANGMapper`, `EcusSPTTTMapper`, `EcusSPTVTMapper`, `EcusSDKGHMapper`, `EcusSVB_PQMapper`, `EcusSLOAI_GPMapper`, `EcusSLHINHMDMapper`, `EcusSMA_AP_MIENTHUEMapper`, `EcusSMA_MIENTHUEMapper`, `EcusREPORTSEXCELMapper`, `EcusSBIEU_THUE_TENMapper`, `EcusDCHUNGTUKEMMapper`

**Tests to create** — all in `module/ecus-thaison/src/test/java/com/egov/ecusthaison/entity/`:
One `*UnitTest.java` per entity class above.

---

## Core Patterns

### processSync() upsert pattern (applies to all tasks)

Replace every occurrence of:
```java
EntityType existing = service.findBy...(companyId, [trimmedCode,] syncSourceConfigId);
EntityType entity = Optional.ofNullable(existing).orElseGet(EntityType::new);
mapToEntityType(companyId, entity, ecusEntity[, trimmedCode], syncSourceConfigId);
EntityType saved = service.save(entity);
```

with:
```java
EntityType existing = service.findBy...(companyId, [trimmedCode,] syncSourceConfigId);
boolean isNew = existing == null;
if (isNew) {
  existing = new EntityType();
  existing.setCompanyId(companyId);
  existing.setSyncSourceConfigurationId(syncSourceConfigId);
}
EntityType saved = service.save(ecusEntity.toEntityType(existing));
```

Update any `existingXxx != null ? "Updated" : "Created"` log references to `isNew ? "Created" : "Updated"`.

### Trim rules recap
- Fields that mappers currently trim: use same trim method in `to*()` for **both** `setCode()` and `setOriginalId()`.
- Mappers using `Optional.ofNullable(x).map(String::trim).orElse(null)`: SHAIQUAN, SNUOC, SNGTE, SNGAN_HANG, SPTTT, SPTVT, SDKGH, SVB_PQ, SLOAI_GP, SLHINHMD, SMA_AP_MIENTHUE, SMA_MIENTHUE, REPORTSEXCEL, SBIEU_THUE_TEN.
- Mappers using `StringUtils.trimAllWhitespace(x)`: SDVT, SLOAI_KIEN.
- No trim: SCUAKHAU, SCUAKHAUNN, DCHUNGTUKEM.

---

### Task 1: Pilot — SCUAKHAU → toBorderGate

**Files:**
- Modify: `entity/SCUAKHAU.java`
- Modify: `mapper/company/EcusSCUAKHAUMapper.java`
- Create: `test/.../entity/SCUAKHAUUnitTest.java`

- [ ] **Step 1: Write failing test**

Create `module/ecus-thaison/src/test/java/com/egov/ecusthaison/entity/SCUAKHAUUnitTest.java`:
```java
package com.egov.ecusthaison.entity;

import com.egov.ecutoms.entity.BorderGate;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@Tag("unit")
class SCUAKHAUUnitTest {

  @Test
  void toBorderGate_nullTemplate_createsNewEntity() {
    SCUAKHAU s = new SCUAKHAU();
    s.setMaCK("CK01");
    s.setTenCK("Cua khau 01");
    s.setTenCKVN("Cua khau VN");
    s.setMaNuoc("VN");
    s.setIsVNACCS(1);

    BorderGate result = s.toBorderGate(null);

    assertThat(result).isNotNull();
    assertThat(result.getCode()).isEqualTo("CK01");
    assertThat(result.getName()).isEqualTo("Cua khau 01");
    assertThat(result.getNameVn()).isEqualTo("Cua khau VN");
    assertThat(result.getType()).isEqualTo("LOADING");
    assertThat(result.getOriginalId()).isEqualTo("CK01");
    assertThat(result.getCountryCode()).isEqualTo("VN");
    assertThat(result.getIsVnaccs()).isTrue();
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
    assertThat(result.getSyncSourceConfigurationId()).isNull();
  }

  @Test
  void toBorderGate_existingTemplate_updatesFieldsPreservesContext() {
    SCUAKHAU s = new SCUAKHAU();
    s.setMaCK("CK02");
    s.setTenCK("Updated");

    BorderGate existing = new BorderGate();
    existing.setCompanyId(100L);
    existing.setSyncSourceConfigurationId(200L);

    BorderGate result = s.toBorderGate(existing);

    assertThat(result).isSameAs(existing);
    assertThat(result.getCode()).isEqualTo("CK02");
    assertThat(result.getCompanyId()).isEqualTo(100L);
    assertThat(result.getSyncSourceConfigurationId()).isEqualTo(200L);
  }

  @Test
  void toBorderGate_nullIsVnaccs_doesNotOverwrite() {
    SCUAKHAU s = new SCUAKHAU();
    s.setMaCK("CK03");
    s.setIsVNACCS(null);

    BorderGate existing = new BorderGate();
    existing.setIsVnaccs(true);
    s.toBorderGate(existing);

    assertThat(existing.getIsVnaccs()).isTrue();
  }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.entity.SCUAKHAUUnitTest" 2>&1 | tail -15
```
Expected: compilation error — `toBorderGate` does not exist.

- [ ] **Step 3: Add `toBorderGate()` to SCUAKHAU.java**

Add to `SCUAKHAU.java` — add import and method after existing fields:
```java
import com.egov.ecutoms.entity.BorderGate;
```

```java
public BorderGate toBorderGate(BorderGate template) {
  BorderGate bg = template != null ? template : new BorderGate();
  bg.setCode(this.maCK);
  bg.setName(this.tenCK);
  bg.setNameAlt(this.tenCK1);
  bg.setType("LOADING");
  bg.setDepartmentCode(this.maCuc);
  bg.setTableName(this.tenBang);
  bg.setCountryCode(this.maNuoc);
  bg.setOldCode(this.maCu);
  bg.setOldName(this.tenCu);
  bg.setNameVn(this.tenCKVN);
  bg.setNameAltVn(this.tenCK1VN);
  if (this.isVNACCS != null) {
    bg.setIsVnaccs(this.isVNACCS == 1);
  }
  bg.setIsActive(true);
  bg.setOriginalId(this.maCK);
  return bg;
}
```

- [ ] **Step 4: Run test → expect PASS**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test --tests "com.egov.ecusthaison.entity.SCUAKHAUUnitTest" 2>&1 | tail -10
```

- [ ] **Step 5: Update EcusSCUAKHAUMapper.processSync()**

In `processSync()`, replace:
```java
BorderGate borderGate = Optional.ofNullable(existingBorderGate).orElseGet(BorderGate::new);
mapToBorderGate(companyId, borderGate, scuakhau, syncSourceConfigId);
BorderGate savedBorderGate = borderGateService.save(borderGate);
log.debug("{} BorderGate ...", existingBorderGate != null ? "Updated" : "Created", ...);
```
with:
```java
boolean isNew = existingBorderGate == null;
if (isNew) {
  existingBorderGate = new BorderGate();
  existingBorderGate.setCompanyId(companyId);
  existingBorderGate.setSyncSourceConfigurationId(syncSourceConfigId);
}
BorderGate savedBorderGate = borderGateService.save(scuakhau.toBorderGate(existingBorderGate));
log.debug("{} BorderGate ...", isNew ? "Created" : "Updated", ...);
```

Delete the `mapToBorderGate()` private method. Remove unused `Optional` import if no longer needed elsewhere.

- [ ] **Step 6: Compile check**

```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava 2>&1 | tail -10
```
Expected: BUILD SUCCESSFUL.

- [ ] **Step 7: Commit**

```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SCUAKHAU.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUMapper.java \
        module/ecus-thaison/src/test/java/com/egov/ecusthaison/entity/SCUAKHAUUnitTest.java
git commit -m "refactor: move SCUAKHAU->BorderGate field mapping into entity"
```

---

### Task 2: SCUAKHAUNN → toBorderGate

Type = `"UNLOADING"`. Extra field: `itemType` → `setDescription("ItemType: " + itemType)` when non-blank.

**Files:** `entity/SCUAKHAUNN.java`, `mapper/company/EcusSCUAKHAUNNMapper.java`, `test/.../entity/SCUAKHAUNNUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
package com.egov.ecusthaison.entity;

import com.egov.ecutoms.entity.BorderGate;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

@Tag("unit")
class SCUAKHAUNNUnitTest {

  @Test
  void toBorderGate_setsTypeUnloading() {
    SCUAKHAUNN s = new SCUAKHAUNN();
    s.setMaCK("CK01");
    BorderGate result = s.toBorderGate(null);
    assertThat(result.getType()).isEqualTo("UNLOADING");
    assertThat(result.getCode()).isEqualTo("CK01");
    assertThat(result.getOriginalId()).isEqualTo("CK01");
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toBorderGate_nonBlankItemType_setsDescription() {
    SCUAKHAUNN s = new SCUAKHAUNN();
    s.setMaCK("CK02");
    s.setItemType("TypeA");
    assertThat(s.toBorderGate(null).getDescription()).isEqualTo("ItemType: TypeA");
  }

  @Test
  void toBorderGate_blankItemType_doesNotOverwriteDescription() {
    SCUAKHAUNN s = new SCUAKHAUNN();
    s.setMaCK("CK03");
    s.setItemType("  ");
    BorderGate existing = new BorderGate();
    existing.setDescription("keep");
    s.toBorderGate(existing);
    assertThat(existing.getDescription()).isEqualTo("keep");
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toBorderGate()` to SCUAKHAUNN.java**

Add import `import com.egov.ecutoms.entity.BorderGate;` and method:
```java
public BorderGate toBorderGate(BorderGate template) {
  BorderGate bg = template != null ? template : new BorderGate();
  bg.setCode(this.maCK);
  bg.setName(this.tenCK);
  bg.setNameAlt(this.tenCK1);
  bg.setType("UNLOADING");
  bg.setDepartmentCode(this.maCuc);
  bg.setTableName(this.tenBang);
  bg.setCountryCode(this.maNuoc);
  bg.setOldCode(this.maCu);
  bg.setOldName(this.tenCu);
  bg.setNameVn(this.tenCKVN);
  bg.setNameAltVn(this.tenCK1VN);
  if (this.isVNACCS != null) {
    bg.setIsVnaccs(this.isVNACCS == 1);
  }
  if (this.itemType != null && !this.itemType.trim().isEmpty()) {
    bg.setDescription("ItemType: " + this.itemType);
  }
  bg.setIsActive(true);
  bg.setOriginalId(this.maCK);
  return bg;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusSCUAKHAUNNMapper.processSync()** — same upsert pattern as Task 1. Delete `mapToBorderGate()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move SCUAKHAUNN->BorderGate field mapping into entity"
```

---

### Task 3: SHAIQUAN → toCustomsOffice

Trim: `maHQ` and `tenHQ` trimmed inside `mapToCustomsOffice()`. Fix `originalId` to also use `trimCode`.

**Files:** `entity/SHAIQUAN.java`, `mapper/company/EcusSHAIQUANMapper.java`, `test/.../entity/SHAIQUANUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
@Tag("unit")
class SHAIQUANUnitTest {

  @Test
  void toCustomsOffice_trimsMaHQAndTenHQ() {
    SHAIQUAN s = new SHAIQUAN();
    s.setMaHQ("  HQ01  ");
    s.setTenHQ("  Chi cuc HQ  ");

    CustomsOffice result = s.toCustomsOffice(null);

    assertThat(result.getCode()).isEqualTo("HQ01");
    assertThat(result.getName()).isEqualTo("Chi cuc HQ");
    assertThat(result.getOriginalId()).isEqualTo("HQ01");
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toCustomsOffice_preservesContextOnExistingTemplate() {
    SHAIQUAN s = new SHAIQUAN();
    s.setMaHQ("HQ02");
    CustomsOffice existing = new CustomsOffice();
    existing.setCompanyId(99L);
    existing.setSyncSourceConfigurationId(88L);
    s.toCustomsOffice(existing);
    assertThat(existing.getCompanyId()).isEqualTo(99L);
    assertThat(existing.getSyncSourceConfigurationId()).isEqualTo(88L);
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toCustomsOffice()` to SHAIQUAN.java**

Add imports: `import com.egov.ecutoms.entity.CustomsOffice;`, `import java.util.Optional;`

```java
public CustomsOffice toCustomsOffice(CustomsOffice template) {
  CustomsOffice co = template != null ? template : new CustomsOffice();
  String trimCode = Optional.ofNullable(this.maHQ).map(String::trim).orElse(null);
  co.setCode(trimCode);
  co.setName(this.tenHQ != null ? this.tenHQ.trim() : null);
  co.setAlternateName(this.tenHQ1);
  co.setLevel(this.capHQ);
  co.setIsDisplayed(this.hienThi);
  co.setIsVNACCS(this.isVNACCS);
  co.setTableName(this.tenBang);
  co.setOldCode(this.maCu);
  co.setOldName(this.tenCu);
  co.setVietnameseName(this.tenHQVN);
  co.setVietnameseAlternateName(this.tenHQ1VN);
  co.setShortName(this.tenHQVT);
  co.setOriginalId(trimCode);
  return co;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusSHAIQUANMapper.processSync()**

`trimCode` is already computed for the lookup — keep it. Apply upsert pattern. Delete `mapToCustomsOffice()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move SHAIQUAN->CustomsOffice field mapping into entity"
```

---

### Task 4: SNUOC → toEgovCountry + SNGTE → toEgovCurrency

Both use `Optional.ofNullable(x).map(String::trim)`. Both set `sourceId = "ECUS_" + rawField` (keep raw for sourceId). Fix `originalId` to use trimmed value in both.

**Files:** `entity/SNUOC.java`, `entity/SNGTE.java`, both mappers, both test files.

- [ ] **Step 1: Write failing tests**

`SNUOCUnitTest.java`:
```java
@Tag("unit")
class SNUOCUnitTest {

  @Test
  void toEgovCountry_trimsMaNuoc() {
    SNUOC s = new SNUOC();
    s.setMaNuoc("  VN  ");
    s.setTenNuoc("Viet Nam");
    s.setMaNT("VND");

    EgovCountry result = s.toEgovCountry(null);

    assertThat(result.getCode()).isEqualTo("VN");
    assertThat(result.getOriginalId()).isEqualTo("VN");
    assertThat(result.getName()).isEqualTo("Viet Nam");
    assertThat(result.getCurrencyCode()).isEqualTo("VND");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

`SNGTEUnitTest.java`:
```java
@Tag("unit")
class SNGTEUnitTest {

  @Test
  void toEgovCurrency_trimsMaNT() {
    SNGTE s = new SNGTE();
    s.setMaNT("  USD  ");
    s.setTenNT("US Dollar");

    EgovCurrency result = s.toEgovCurrency(null);

    assertThat(result.getCode()).isEqualTo("USD");
    assertThat(result.getOriginalId()).isEqualTo("USD");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toEgovCurrency_convertsExchangeRate() {
    SNGTE s = new SNGTE();
    s.setMaNT("EUR");
    s.setTygiaVND(25000.0);

    EgovCurrency result = s.toEgovCurrency(null);

    assertThat(result.getExchangeRateVnd()).isEqualByComparingTo("25000.0");
  }
}
```

- [ ] **Step 2: Run both tests → expect FAIL**

- [ ] **Step 3: Add `toEgovCountry()` to SNUOC.java**

Add imports: `import com.egov.ecutoms.entity.EgovCountry;`, `import java.util.Optional;`

```java
public EgovCountry toEgovCountry(EgovCountry template) {
  EgovCountry c = template != null ? template : new EgovCountry();
  String trimCode = Optional.ofNullable(this.maNuoc).map(String::trim).orElse(null);
  c.setCode(trimCode);
  c.setName(this.tenNuoc);
  c.setNameAlt(this.tenNuoc1);
  c.setNameVn(this.tenNuocVN);
  c.setNameAltVn(this.tenNuoc1VN);
  c.setCurrencyCode(this.maNT);
  c.setDisplayOrder(this.hienThi);
  c.setIsActive(true);
  c.setSourceId("ECUS_" + this.maNuoc);
  c.setOriginalId(trimCode);
  return c;
}
```

- [ ] **Step 4: Add `toEgovCurrency()` to SNGTE.java**

Add imports: `import com.egov.ecutoms.entity.EgovCurrency;`, `import java.math.BigDecimal;`, `import java.util.Optional;`

```java
public EgovCurrency toEgovCurrency(EgovCurrency template) {
  EgovCurrency c = template != null ? template : new EgovCurrency();
  String trimCode = Optional.ofNullable(this.maNT).map(String::trim).orElse(null);
  c.setCode(trimCode);
  c.setName(this.tenNT);
  c.setNameAlt(this.tenNT1);
  c.setTableName(this.tenBang);
  if (this.tygiaVND != null) {
    c.setExchangeRateVnd(BigDecimal.valueOf(this.tygiaVND));
  }
  c.setIsActive(true);
  c.setSourceId("ECUS_" + this.maNT);
  c.setOriginalId(trimCode);
  return c;
}
```

- [ ] **Step 5: Run both tests → expect PASS**

- [ ] **Step 6: Update both mapper processSync() methods**

`trimmedCode` is still needed for the service lookup — keep it. Apply upsert pattern for both. Delete both `mapTo*()` methods.

- [ ] **Step 7: Compile + Commit**

```bash
git commit -m "refactor: move SNUOC->EgovCountry and SNGTE->EgovCurrency field mapping into entities"
```

---

### Task 5: SDVT → toEgovUnit + SLOAI_KIEN → toEgovUnit

Both use `StringUtils.trimAllWhitespace()` (removes ALL whitespace, not just trim). Keep this exact method. Fix `originalId` to use `trimCode`.

**Files:** `entity/SDVT.java`, `entity/SLOAI_KIEN.java`, both mappers, both test files.

- [ ] **Step 1: Write failing tests**

`SDVTUnitTest.java`:
```java
@Tag("unit")
class SDVTUnitTest {

  @Test
  void toEgovUnit_trimsMaDVT() {
    SDVT s = new SDVT();
    s.setMaDVT("KG ");
    s.setTenDVT("Kilogram");

    EgovUnit result = s.toEgovUnit(null);

    assertThat(result.getCode()).isEqualTo("KG");
    assertThat(result.getOriginalId()).isEqualTo("KG");
    assertThat(result.getName()).isEqualTo("Kilogram");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

`SLOAI_KIENUnitTest.java`:
```java
@Tag("unit")
class SLOAI_KIENUnitTest {

  @Test
  void toEgovUnit_trimsMaLK() {
    SLOAI_KIEN s = new SLOAI_KIEN();
    s.setMaLK("  CT  ");
    s.setTenLK("Cai");

    EgovUnit result = s.toEgovUnit(null);

    assertThat(result.getCode()).isEqualTo("CT");
    assertThat(result.getOriginalId()).isEqualTo("CT");
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run both tests → expect FAIL**

- [ ] **Step 3: Add `toEgovUnit()` to SDVT.java**

Add imports: `import com.egov.ecutoms.entity.EgovUnit;`, `import org.springframework.util.StringUtils;`

```java
public EgovUnit toEgovUnit(EgovUnit template) {
  EgovUnit u = template != null ? template : new EgovUnit();
  String trimCode = StringUtils.trimAllWhitespace(this.maDVT);
  u.setCode(trimCode);
  u.setName(this.tenDVT);
  u.setNameAlt(this.tenDVT1);
  u.setNameVn(this.tenDVTVN);
  u.setNameAltVn(this.tenDVT1VN);
  u.setTableName(this.tenBang);
  u.setIsVnaccs(this.isVNACCS);
  u.setOldCode(this.maCu);
  u.setOldName(this.tenCu);
  u.setDisplayOrder(this.hienThi);
  u.setIsActive(true);
  u.setSourceId("ECUS_" + this.maDVT);
  u.setOriginalId(trimCode);
  return u;
}
```

- [ ] **Step 4: Add `toEgovUnit()` to SLOAI_KIEN.java**

Add same imports. Replace `maDVT`/`tenDVT*` with `maLK`/`tenLK*`:

```java
public EgovUnit toEgovUnit(EgovUnit template) {
  EgovUnit u = template != null ? template : new EgovUnit();
  String trimCode = StringUtils.trimAllWhitespace(this.maLK);
  u.setCode(trimCode);
  u.setName(this.tenLK);
  u.setNameAlt(this.tenLK1);
  u.setNameVn(this.tenLKVN);
  u.setNameAltVn(this.tenLK1VN);
  u.setTableName(this.tenBang);
  u.setIsVnaccs(this.isVNACCS);
  u.setOldCode(this.maCu);
  u.setOldName(this.tenCu);
  u.setDisplayOrder(this.hienThi);
  u.setIsActive(true);
  u.setSourceId("ECUS_" + this.maLK);
  u.setOriginalId(trimCode);
  return u;
}
```

- [ ] **Step 5: Run both tests → expect PASS**

- [ ] **Step 6: Update both mapper processSync() methods**

Apply upsert pattern. Delete both `mapToEgovUnit()` methods.

- [ ] **Step 7: Compile + Commit**

```bash
git commit -m "refactor: move SDVT/SLOAI_KIEN->EgovUnit field mapping into entities"
```

---

### Task 6: SNGAN_HANG → toBank + SPTTT → toInvoicePaymentMethod

**SNGAN_HANG:** `mapToBank()` uses raw `getMaNH()` for code and originalId despite mapper computing `trimmedCode` for lookup. Fix both.

**SPTTT:** `mapToInvoicePaymentMethod()` receives `trimmedCode` for code but uses raw `getMaPTTT()` for originalId. Fix originalId.

**Files:** `entity/SNGAN_HANG.java`, `entity/SPTTT.java`, both mappers, both test files.

- [ ] **Step 1: Write failing tests**

`SNGAN_HANGUnitTest.java`:
```java
@Tag("unit")
class SNGAN_HANGUnitTest {

  @Test
  void toBank_trimsMaNH() {
    SNGAN_HANG s = new SNGAN_HANG();
    s.setMaNH("  NH01  ");
    s.setTenNH("Ngan hang 01");
    s.setGhiChu("note");

    Bank result = s.toBank(null);

    assertThat(result.getCode()).isEqualTo("NH01");
    assertThat(result.getOriginalId()).isEqualTo("NH01");
    assertThat(result.getName()).isEqualTo("Ngan hang 01");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

`SPTTTUnitTest.java`:
```java
@Tag("unit")
class SPTTTUnitTest {

  @Test
  void toInvoicePaymentMethod_trimsMaPTTT() {
    SPTTT s = new SPTTT();
    s.setMaPTTT("  TM  ");
    s.setTenPTTT("Tien mat");

    InvoicePaymentMethod result = s.toInvoicePaymentMethod(null);

    assertThat(result.getCode()).isEqualTo("TM");
    assertThat(result.getOriginalId()).isEqualTo("TM");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run tests → expect FAIL**

- [ ] **Step 3: Add `toBank()` to SNGAN_HANG.java**

Add imports: `import com.egov.ecutoms.entity.Bank;`, `import java.util.Optional;`

```java
public Bank toBank(Bank template) {
  Bank b = template != null ? template : new Bank();
  String trimCode = Optional.ofNullable(this.maNH).map(String::trim).orElse(null);
  b.setCode(trimCode);
  b.setName(this.tenNH);
  b.setNameAlt(this.tenNH1);
  b.setNote(this.ghiChu);
  b.setTableName(this.tenBang);
  b.setIsActive(true);
  b.setOriginalId(trimCode);
  return b;
}
```

- [ ] **Step 4: Add `toInvoicePaymentMethod()` to SPTTT.java**

Add imports: `import com.egov.ecutoms.entity.InvoicePaymentMethod;`, `import java.util.Optional;`

```java
public InvoicePaymentMethod toInvoicePaymentMethod(InvoicePaymentMethod template) {
  InvoicePaymentMethod p = template != null ? template : new InvoicePaymentMethod();
  String trimCode = Optional.ofNullable(this.maPTTT).map(String::trim).orElse(null);
  p.setCode(trimCode);
  p.setName(this.tenPTTT);
  p.setNameTcvn(this.tenPTTTTCVN);
  p.setNote(this.ghiChu);
  p.setIsActive(true);
  p.setOriginalId(trimCode);
  return p;
}
```

- [ ] **Step 5: Run tests → expect PASS**

- [ ] **Step 6: Update both mapper processSync() methods**

Apply upsert pattern. Delete both `mapTo*()` methods.

- [ ] **Step 7: Compile + Commit**

```bash
git commit -m "refactor: move SNGAN_HANG->Bank and SPTTT->InvoicePaymentMethod field mapping into entities"
```

---

### Task 7: SPTVT → toTransportMode

`mapToTransportMode()` receives `trimmedCode` for code but uses raw `getMaPTVT()` for originalId. Fix originalId. Has `isVNACCS` boolean conversion.

**Files:** `entity/SPTVT.java`, `mapper/company/EcusSPTVTMapper.java`, `test/.../entity/SPTVTUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
@Tag("unit")
class SPTVTUnitTest {

  @Test
  void toTransportMode_trimsMaPTVT_andOriginalId() {
    SPTVT s = new SPTVT();
    s.setMaPTVT("  DL  ");
    s.setTenPTVT("Duong lo");
    s.setIsVNACCS(1);

    TransportMode result = s.toTransportMode(null);

    assertThat(result.getCode()).isEqualTo("DL");
    assertThat(result.getOriginalId()).isEqualTo("DL");
    assertThat(result.getName()).isEqualTo("Duong lo");
    assertThat(result.getIsVnaccs()).isTrue();
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toTransportMode_nullIsVnaccs_doesNotOverwrite() {
    SPTVT s = new SPTVT();
    s.setMaPTVT("DL");
    s.setIsVNACCS(null);
    TransportMode existing = new TransportMode();
    existing.setIsVnaccs(true);
    s.toTransportMode(existing);
    assertThat(existing.getIsVnaccs()).isTrue();
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toTransportMode()` to SPTVT.java**

Add imports: `import com.egov.ecutoms.entity.TransportMode;`, `import java.util.Optional;`

```java
public TransportMode toTransportMode(TransportMode template) {
  TransportMode t = template != null ? template : new TransportMode();
  String trimCode = Optional.ofNullable(this.maPTVT).map(String::trim).orElse(null);
  t.setCode(trimCode);
  t.setName(this.tenPTVT);
  t.setNameAlt(this.tenPTVT1);
  t.setDeclarationNumber(this.spSoTK);
  t.setDeclarationTypeCode(this.spMaLH);
  t.setCustomsCode(this.spMaHQ);
  t.setRegistrationYear(this.spNamDK);
  t.setNameVn(this.tenPTVTVN);
  t.setNameAltVn(this.tenPTVT1VN);
  t.setDisplayOrder(this.hienThi);
  if (this.isVNACCS != null) {
    t.setIsVnaccs(this.isVNACCS == 1);
  }
  t.setIsActive(true);
  t.setOriginalId(trimCode);
  return t;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusSPTVTMapper.processSync()** — apply upsert pattern. Delete `mapToTransportMode()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move SPTVT->TransportMode field mapping into entity"
```

---

### Task 8: SDKGH → toInvoiceDeliveryTerms

`mapToInvoiceDeliveryTerms()` uses raw `getMaGH()` for both code and originalId. Fix both. **Also:** `EcusSDKGHMapper.processSync()` has an inline FQCN in the catch block — fix while modifying the method.

**Files:** `entity/SDKGH.java`, `mapper/company/EcusSDKGHMapper.java`, `test/.../entity/SDKGHUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
@Tag("unit")
class SDKGHUnitTest {

  @Test
  void toInvoiceDeliveryTerms_trimsMaGH() {
    SDKGH s = new SDKGH();
    s.setMaGH("  FOB  ");
    s.setTenGH("Free on Board");
    s.setGhiChu("note");
    s.setTenGHTCVN("TCVN");

    InvoiceDeliveryTerms result = s.toInvoiceDeliveryTerms(null);

    assertThat(result.getCode()).isEqualTo("FOB");
    assertThat(result.getOriginalId()).isEqualTo("FOB");
    assertThat(result.getName()).isEqualTo("Free on Board");
    assertThat(result.getNote()).isEqualTo("note");
    assertThat(result.getNameTcvn()).isEqualTo("TCVN");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toInvoiceDeliveryTerms()` to SDKGH.java**

Add imports: `import com.egov.ecutoms.entity.InvoiceDeliveryTerms;`, `import java.util.Optional;`

```java
public InvoiceDeliveryTerms toInvoiceDeliveryTerms(InvoiceDeliveryTerms template) {
  InvoiceDeliveryTerms d = template != null ? template : new InvoiceDeliveryTerms();
  String trimCode = Optional.ofNullable(this.maGH).map(String::trim).orElse(null);
  d.setCode(trimCode);
  d.setName(this.tenGH);
  d.setNote(this.ghiChu);
  d.setTableName(this.tenBang);
  d.setNameTcvn(this.tenGHTCVN);
  d.setIsActive(true);
  d.setOriginalId(trimCode);
  return d;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusSDKGHMapper**

Add import at top of `EcusSDKGHMapper.java`:
```java
import org.springframework.dao.DataIntegrityViolationException;
```

In `processSync()`:
1. Apply upsert pattern.
2. Change `} catch (org.springframework.dao.DataIntegrityViolationException e) {` → `} catch (DataIntegrityViolationException e) {`

Delete `mapToInvoiceDeliveryTerms()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move SDKGH->InvoiceDeliveryTerms field mapping into entity, fix FQCN catch"
```

---

### Task 9: SVB_PQ → toCustomsLegalCode + SLOAI_GP → toTradingLicenseType

**SVB_PQ:** `mapToCustomsLegalCode()` receives `trimmedCode` for code but uses raw `getMaVB()` for originalId. Fix originalId. Has conditional name generation and boolean flag assignments.

**SLOAI_GP:** `mapToTradingLicenseType()` uses raw `getMaLoaiGP()` for both code and originalId. Fix both. Has `TradingLicenseType.Category.BOTH` enum.

**Files:** `entity/SVB_PQ.java`, `entity/SLOAI_GP.java`, both mappers, both test files.

- [ ] **Step 1: Write failing tests**

`SVB_PQUnitTest.java`:
```java
@Tag("unit")
class SVB_PQUnitTest {

  @Test
  void toCustomsLegalCode_trimsMaVB() {
    SVB_PQ s = new SVB_PQ();
    s.setMaVB("  VB01  ");
    s.setSoHieu("42/2023/ND-CP");

    CustomsLegalCode result = s.toCustomsLegalCode(null);

    assertThat(result.getCode()).isEqualTo("VB01");
    assertThat(result.getOriginalId()).isEqualTo("VB01");
    assertThat(result.getLegalDocumentNo()).isEqualTo("42/2023/ND-CP");
    assertThat(result.getName()).isEqualTo("Van ban 42/2023/ND-CP");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toCustomsLegalCode_blankSoHieu_usesCodeInName() {
    SVB_PQ s = new SVB_PQ();
    s.setMaVB("VB02");
    s.setSoHieu(null);
    assertThat(s.toCustomsLegalCode(null).getName()).isEqualTo("Van ban VB02");
  }
}
```

`SLOAI_GPUnitTest.java`:
```java
@Tag("unit")
class SLOAI_GPUnitTest {

  @Test
  void toTradingLicenseType_trimsMaLoaiGP() {
    SLOAI_GP s = new SLOAI_GP();
    s.setMaLoaiGP("  GP01  ");
    s.setTenLoaiGP("Giay phep loai 1");

    TradingLicenseType result = s.toTradingLicenseType(null);

    assertThat(result.getCode()).isEqualTo("GP01");
    assertThat(result.getOriginalId()).isEqualTo("GP01");
    assertThat(result.getName()).isEqualTo("Giay phep loai 1");
    assertThat(result.getCategory()).isEqualTo(TradingLicenseType.Category.BOTH);
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run both tests → expect FAIL**

- [ ] **Step 3: Add `toCustomsLegalCode()` to SVB_PQ.java**

Add imports: `import com.egov.ecutoms.entity.CustomsLegalCode;`, `import java.util.Optional;`

```java
public CustomsLegalCode toCustomsLegalCode(CustomsLegalCode template) {
  CustomsLegalCode c = template != null ? template : new CustomsLegalCode();
  String trimCode = Optional.ofNullable(this.maVB).map(String::trim).orElse(null);
  c.setCode(trimCode);
  c.setLegalDocumentNo(this.soHieu);
  c.setDocumentDate(this.ngayVB);
  c.setContent(this.noiDung);
  c.setContentTcvn(this.noiDungTCVN);
  c.setDisplayOrder(this.hienThi);
  if (this.export != null) {
    c.setIsExport(this.export);
  }
  if (this.importField != null) {
    c.setIsImport(this.importField);
  }
  if (this.soHieu != null && !this.soHieu.trim().isEmpty()) {
    c.setName("Van ban " + this.soHieu);
  } else {
    c.setName("Van ban " + trimCode);
  }
  c.setIsActive(true);
  c.setOriginalId(trimCode);
  return c;
}
```

- [ ] **Step 4: Add `toTradingLicenseType()` to SLOAI_GP.java**

Add imports: `import com.egov.ecutoms.entity.TradingLicenseType;`, `import java.util.Optional;`

```java
public TradingLicenseType toTradingLicenseType(TradingLicenseType template) {
  TradingLicenseType t = template != null ? template : new TradingLicenseType();
  String trimCode = Optional.ofNullable(this.maLoaiGP).map(String::trim).orElse(null);
  t.setCode(trimCode);
  t.setName(this.tenLoaiGP);
  t.setNameAlt(this.tenLoaiGP1);
  t.setTableName(this.tenBang);
  t.setCategory(TradingLicenseType.Category.BOTH);
  t.setIsActive(true);
  t.setOriginalId(trimCode);
  return t;
}
```

- [ ] **Step 5: Run both tests → expect PASS**

- [ ] **Step 6: Update both mapper processSync() methods** — apply upsert pattern, delete both `mapTo*()` methods.

- [ ] **Step 7: Compile + Commit**

```bash
git commit -m "refactor: move SVB_PQ->CustomsLegalCode and SLOAI_GP->TradingLicenseType field mapping into entities"
```

---

### Task 10: SLHINHMD + SMA_AP_MIENTHUE + SMA_MIENTHUE

**SLHINHMD:** `mapToDeclarationType()` receives `trimmedCode` for code but uses raw for originalId. Has `Boolean hienThi → int displayOrder` conversion.

**SMA_AP_MIENTHUE / SMA_MIENTHUE:** Both use raw field for code and originalId in `mapTo*()` despite mapper computing `trimmedCode` for lookup. Fix both.

**Files:** 3 entity files, 3 mapper files, 3 test files.

- [ ] **Step 1: Write failing tests**

`SLHINHMDUnitTest.java`:
```java
@Tag("unit")
class SLHINHMDUnitTest {

  @Test
  void toDeclarationType_trimsMaLH_andMapsDisplayOrder() {
    SLHINHMD s = new SLHINHMD();
    s.setMaLH("  E31  ");
    s.setTenLH("Xuat khau");
    s.setHienThi(true);

    DeclarationType result = s.toDeclarationType(null);

    assertThat(result.getCode()).isEqualTo("E31");
    assertThat(result.getOriginalId()).isEqualTo("E31");
    assertThat(result.getName()).isEqualTo("Xuat khau");
    assertThat(result.getDisplayOrder()).isEqualTo(1);
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

`SMA_AP_MIENTHUEUnitTest.java`:
```java
@Tag("unit")
class SMA_AP_MIENTHUEUnitTest {

  @Test
  void toTaxExemption_trimsCode() {
    SMA_AP_MIENTHUE s = new SMA_AP_MIENTHUE();
    s.setCode("  MT01  ");
    s.setTen("Mien thue loai 1");

    TaxExemption result = s.toTaxExemption(null);

    assertThat(result.getCode()).isEqualTo("MT01");
    assertThat(result.getOriginalId()).isEqualTo("MT01");
    assertThat(result.getName()).isEqualTo("Mien thue loai 1");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

`SMA_MIENTHUEUnitTest.java`:
```java
@Tag("unit")
class SMA_MIENTHUEUnitTest {

  @Test
  void toTaxExemptionCategory_trimsMa() {
    SMA_MIENTHUE s = new SMA_MIENTHUE();
    s.setMa("  DM01  ");
    s.setTen("Danh muc 01");

    TaxExemptionCategory result = s.toTaxExemptionCategory(null);

    assertThat(result.getCode()).isEqualTo("DM01");
    assertThat(result.getOriginalId()).isEqualTo("DM01");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run all three tests → expect FAIL**

- [ ] **Step 3: Add `toDeclarationType()` to SLHINHMD.java**

Add imports: `import com.egov.ecutoms.entity.DeclarationType;`, `import java.util.Optional;`

```java
public DeclarationType toDeclarationType(DeclarationType template) {
  DeclarationType d = template != null ? template : new DeclarationType();
  String trimCode = Optional.ofNullable(this.maLH).map(String::trim).orElse(null);
  d.setGroupCode(this.nhomLH);
  d.setCode(trimCode);
  d.setName(this.tenLH);
  d.setName1(this.tenLH1);
  d.setAlias(this.tenVT);
  d.setSequence(this.soTT);
  d.setDisplayOrder(this.hienThi != null ? (this.hienThi ? 1 : 0) : 0);
  d.setTableName(this.tenBang);
  d.setOldCode(this.maCu);
  d.setOldName(this.tenCu);
  d.setNameVn(this.tenLHVN);
  d.setNameVn1(this.tenLH1VN);
  d.setIsActive(true);
  d.setOriginalId(trimCode);
  return d;
}
```

- [ ] **Step 4: Add `toTaxExemption()` to SMA_AP_MIENTHUE.java**

Add imports: `import com.egov.ecutoms.entity.TaxExemption;`, `import java.util.Optional;`

```java
public TaxExemption toTaxExemption(TaxExemption template) {
  TaxExemption t = template != null ? template : new TaxExemption();
  String trimCode = Optional.ofNullable(this.code).map(String::trim).orElse(null);
  t.setCode(trimCode);
  t.setIssueDate(this.ngayPhatHanh);
  t.setEffectiveDate(this.ngayHieuLuc);
  t.setExpiryDate(this.ngayHH);
  t.setExemptionRate(this.tyLe);
  t.setUnitCode(this.maDVT);
  t.setCurrencyCode(this.maNT);
  t.setTableId(this.tableID);
  t.setKeyField(this.keyField);
  t.setDisplayOrder(this.hienThi);
  t.setName(this.ten);
  t.setType(this.type);
  t.setIsActive(true);
  t.setOriginalId(trimCode);
  return t;
}
```

- [ ] **Step 5: Add `toTaxExemptionCategory()` to SMA_MIENTHUE.java**

Add imports: `import com.egov.ecutoms.entity.TaxExemptionCategory;`, `import java.util.Optional;`

```java
public TaxExemptionCategory toTaxExemptionCategory(TaxExemptionCategory template) {
  TaxExemptionCategory c = template != null ? template : new TaxExemptionCategory();
  String trimCode = Optional.ofNullable(this.ma).map(String::trim).orElse(null);
  c.setCode(trimCode);
  c.setIssueDate(this.ngayBanHanh);
  c.setEffectiveDate(this.ngayHieuLuc);
  c.setExpiryDate(this.ngayHH);
  c.setName(this.ten);
  c.setTableId(this.tableID);
  c.setKeyField(this.keyField);
  c.setNameVn(this.tenVN);
  c.setNameVnTcvn(this.tenVNTCVN);
  c.setType(this.type);
  c.setDisplayOrder(this.hienThi);
  c.setIsActive(true);
  c.setOriginalId(trimCode);
  return c;
}
```

- [ ] **Step 6: Run all three tests → expect PASS**

- [ ] **Step 7: Update all three mapper processSync() methods** — apply upsert pattern, delete all three `mapTo*()` methods.

- [ ] **Step 8: Compile + Commit**

```bash
git commit -m "refactor: move SLHINHMD/SMA_AP_MIENTHUE/SMA_MIENTHUE field mapping into entities"
```

---

### Task 11: REPORTSEXCEL → toCustomsMessageType

`mapToCustomsMessageType()` calls a private helper `determineChannelType()`. This helper contains pure string logic — copy it into the entity as a private method.

**Files:** `entity/REPORTSEXCEL.java`, `mapper/company/EcusREPORTSEXCELMapper.java`, `test/.../entity/REPORTSEXCELUnitTest.java`

- [ ] **Step 1: Read `determineChannelType()` from the mapper**

```bash
grep -A 30 "private.*determineChannelType" module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusREPORTSEXCELMapper.java
```

Note the full method body before proceeding.

- [ ] **Step 2: Write failing test**

```java
@Tag("unit")
class REPORTSEXCELUnitTest {

  @Test
  void toCustomsMessageType_trimsMsgOutCode() {
    REPORTSEXCEL r = new REPORTSEXCEL();
    r.setMsgOutCode("  IDA  ");
    r.setMsgOutName("Khai bao nhap");
    r.setLoaiChungTu("NK");

    CustomsMessageType result = r.toCustomsMessageType(null);

    assertThat(result.getMessageCode()).isEqualTo("IDA");
    assertThat(result.getOriginalId()).isEqualTo("IDA");
    assertThat(result.getMessageName()).isEqualTo("Khai bao nhap");
    assertThat(result.getDeclarationType()).isEqualTo("NK");
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 3: Run test → expect FAIL**

- [ ] **Step 4: Add `toCustomsMessageType()` and private `determineChannelType()` to REPORTSEXCEL.java**

Add imports: `import com.egov.ecutoms.entity.CustomsMessageType;`, `import java.util.Optional;`

```java
public CustomsMessageType toCustomsMessageType(CustomsMessageType template) {
  CustomsMessageType c = template != null ? template : new CustomsMessageType();
  String trimCode = Optional.ofNullable(this.msgOutCode).map(String::trim).orElse(null);
  c.setMessageCode(trimCode);
  c.setMessageName(this.msgOutName);
  c.setDeclarationType(this.loaiChungTu);
  c.setDescription(this.fileName);
  c.setChannelType(determineChannelType(trimCode));
  c.setOriginalId(trimCode);
  return c;
}

// Copy exact body from EcusREPORTSEXCELMapper.determineChannelType()
private String determineChannelType(String msgOutCode) {
  // [paste body from Step 1 here]
}
```

- [ ] **Step 5: Run test → expect PASS**

- [ ] **Step 6: Update EcusREPORTSEXCELMapper.processSync()**

Apply upsert pattern. Delete `mapToCustomsMessageType()` and `determineChannelType()` from mapper.

- [ ] **Step 7: Compile + Commit**

```bash
git commit -m "refactor: move REPORTSEXCEL->CustomsMessageType field mapping into entity"
```

---

### Task 12: SBIEU_THUE_TEN → toTariffSchedule

`mapToTariffSchedule()` uses raw `getMaBT()` for both code and originalId despite mapper computing `trimmedHsCode` for lookup. Fix both.

**Files:** `entity/SBIEU_THUE_TEN.java`, `mapper/company/EcusSBIEU_THUE_TENMapper.java`, `test/.../entity/SBIEU_THUE_TENUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
@Tag("unit")
class SBIEU_THUE_TENUnitTest {

  @Test
  void toTariffSchedule_trimsMaBT() {
    SBIEU_THUE_TEN s = new SBIEU_THUE_TEN();
    s.setMaBT("  2501  ");
    s.setTenBT("Muoi");
    s.setLoaiThue("XK");

    TariffSchedule result = s.toTariffSchedule(null);

    assertThat(result.getCode()).isEqualTo("2501");
    assertThat(result.getOriginalId()).isEqualTo("2501");
    assertThat(result.getDescription()).isEqualTo("Muoi");
    assertThat(result.getCategory()).isEqualTo("XK");
    assertThat(result.getIsActive()).isTrue();
    assertThat(result.getCompanyId()).isNull();
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toTariffSchedule()` to SBIEU_THUE_TEN.java**

Add imports: `import com.egov.ecutoms.entity.TariffSchedule;`, `import java.util.Optional;`

```java
public TariffSchedule toTariffSchedule(TariffSchedule template) {
  TariffSchedule t = template != null ? template : new TariffSchedule();
  String trimCode = Optional.ofNullable(this.maBT).map(String::trim).orElse(null);
  t.setCode(trimCode);
  t.setDescription(this.tenBT);
  t.setDescriptionAlt(this.tenBT1);
  t.setCategory(this.loaiThue);
  t.setNotes(this.ghiChu);
  t.setIsActive(true);
  t.setOriginalId(trimCode);
  return t;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusSBIEU_THUE_TENMapper.processSync()**

`trimmedHsCode` kept for lookup only. Apply upsert pattern. Delete `mapToTariffSchedule()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move SBIEU_THUE_TEN->TariffSchedule field mapping into entity, fix trim inconsistency"
```

---

### Task 13: DCHUNGTUKEM → toAttachedDocument

No trim (lookup uses `messageID` + `sotn`, not a code field). `originalId = String.valueOf(dChungTuKemID)` — Long to String, no trim. Large field count — copy from `mapToAttachedDocument()` verbatim.

**Files:** `entity/DCHUNGTUKEM.java`, `mapper/company/EcusDCHUNGTUKEMMapper.java`, `test/.../entity/DCHUNGTUKEMUnitTest.java`

- [ ] **Step 1: Write failing test**

```java
@Tag("unit")
class DCHUNGTUKEMUnitTest {

  @Test
  void toAttachedDocument_mapsKeyFields() {
    DCHUNGTUKEM d = new DCHUNGTUKEM();
    d.setDChungTuKemID(42L);
    d.setSoCt("CT001");
    d.setDienGiai("Mo ta");
    d.setGuid("abc-123");

    AttachedDocument result = d.toAttachedDocument(null);

    assertThat(result.getOriginalId()).isEqualTo("42");
    assertThat(result.getDocumentCode()).isEqualTo("CT001");
    assertThat(result.getDescription()).isEqualTo("Mo ta");
    assertThat(result.getGuid()).isEqualTo("abc-123");
    assertThat(result.getCompanyId()).isNull();
  }

  @Test
  void toAttachedDocument_preservesContextOnExistingTemplate() {
    DCHUNGTUKEM d = new DCHUNGTUKEM();
    d.setDChungTuKemID(1L);
    AttachedDocument existing = new AttachedDocument();
    existing.setCompanyId(55L);
    existing.setSyncSourceConfigurationId(66L);
    d.toAttachedDocument(existing);
    assertThat(existing.getCompanyId()).isEqualTo(55L);
    assertThat(existing.getSyncSourceConfigurationId()).isEqualTo(66L);
  }
}
```

- [ ] **Step 2: Run test → expect FAIL**

- [ ] **Step 3: Add `toAttachedDocument()` to DCHUNGTUKEM.java**

Add import: `import com.egov.ecutoms.entity.AttachedDocument;`

Copy all field assignments from `mapToAttachedDocument()`, replacing `attachedDocument.setXxx(dchungtukem.getXxx())` with `doc.setXxx(this.xxx)`. Remove `companyId` and `syncSourceConfigurationId` setters.

```java
public AttachedDocument toAttachedDocument(AttachedDocument template) {
  AttachedDocument doc = template != null ? template : new AttachedDocument();
  doc.setDocumentNumber(this.sotn);
  doc.setDateCreated(this.ngaytn);
  doc.setDocumentCode(this.soCt);
  doc.setDocumentDate(this.ngayCt);
  doc.setDocumentTypeCode(this.maLoaiCt);
  doc.setDescription(this.dienGiai);
  doc.setTotalSize(this.totalSize);
  doc.setCategoryType(this.loaiKB);
  doc.setStatus(this.trangThai);
  doc.setTempId(this.tempt);
  doc.setMessageId(this.messageID);
  doc.setKdtReferences(this.kdtReferences);
  doc.setKdtWaiting(this.kdtWaiting);
  doc.setKdtLastInfo(this.kdtLastInfo);
  doc.setIsSigned(this.isSign);
  doc.setSignData(this.signData);
  doc.setIsSubmitted(this.isTrinhKy);
  doc.setClassificationCategory(this.phanLoaiKB);
  doc.setProcedureName(this.tenThuTucKB);
  doc.setCustomsOfficeCode(this.maHQ);
  doc.setProcessingGroup(this.nhomXuLy);
  doc.setProcedureClassification(this.phanLoaiThuTuc);
  doc.setSubmitterPhone(this.nguoiKBDienThoai);
  doc.setSubmitterName(this.nguoiKBTen);
  doc.setSubmitterAddress(this.nguoiKBDiaChi);
  doc.setManagementNumber(this.soQuanLyNB);
  doc.setAttachmentFileCount(this.soLayFileDinhKem);
  doc.setSubmissionDate(this.ngayKB);
  doc.setDeclarationId(this.dToKhaiMDID);
  doc.setTrackingNumber(this.sotk);
  doc.setGuid(this.guid);
  doc.setIsTest(this.isTest);
  doc.setTestSubmissionNumber(this.testSoKB);
  doc.setTestScenario(this.testKichBan);
  doc.setTestNotes(this.testGhiChu);
  doc.setIsVersion2(this.isVersion2);
  doc.setSubmissionStatus(this.trangThaiKB);
  doc.setLegalBasis(this.canCuPhapLenh);
  doc.setNotificationDate(this.ngayTB);
  doc.setDepartmentHeadName(this.tenTruongDvHQ);
  doc.setCustomsNotes(this.ghiChuHQ);
  doc.setDepartmentCode(this.maDV);
  doc.setOriginalId(String.valueOf(this.dChungTuKemID));
  return doc;
}
```

- [ ] **Step 4: Run test → expect PASS**

- [ ] **Step 5: Update EcusDCHUNGTUKEMMapper.processSync()** — apply upsert pattern. Delete `mapToAttachedDocument()`.

- [ ] **Step 6: Compile + Commit**

```bash
git commit -m "refactor: move DCHUNGTUKEM->AttachedDocument field mapping into entity"
```

---

### Task 14: Final verification

- [ ] **Step 1: Full test suite**

```bash
./gradlew :datatp-egov-module-ecus-thaison:test 2>&1 | tail -20
```
Expected: BUILD SUCCESSFUL, all tests pass.

- [ ] **Step 2: Verify no stray mapTo*() in company mappers**

```bash
grep -r "private void mapTo" module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/
```
Expected: Only `EcusSMACACLOAIMapper` results. No other files.

- [ ] **Step 3: Verify all 19 to*() methods exist on entities**

```bash
grep -r "public.*to[A-Z].*template" module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/
```
Expected: 19 lines.

- [ ] **Step 4: Full module build**

```bash
./gradlew :datatp-egov-module-ecus-thaison:build 2>&1 | tail -10
```
Expected: BUILD SUCCESSFUL.
