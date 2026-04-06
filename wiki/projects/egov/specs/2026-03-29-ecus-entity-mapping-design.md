# Design: Move Field Mapping into ECUS Entity Classes

**Date:** 2026-03-29
**Module:** `ecus-thaison`

---

## Problem

Each mapper in `logic/mapper/company/` has a private `mapTo[EgovEntity]()` method responsible for pure field assignment (ECUS → eGov). This logic lives in the mapper class even though it has no dependency on Spring beans — it only reads from the ECUS entity and writes to the eGov entity.

Field mapping knowledge is scattered across 20+ mapper files instead of sitting alongside the data it describes.

---

## Goal

Move pure field mapping logic out of mapper classes and into the ECUS source entity as an instance method `to[EgovEntity](template)`.

---

## Design

### Method signature on ECUS entity

```java
// In SCUAKHAU.java (ecus-thaison module)
public BorderGate toBorderGate(BorderGate template) {
  BorderGate bg = template != null ? template : new BorderGate();
  bg.setCode(this.maCK);
  bg.setName(this.tenCK);
  bg.setNameVn(this.tenCKVN);
  bg.setType("LOADING");
  bg.setOriginalId(this.maCK);
  // companyId + syncSourceConfigurationId: NOT set here — caller responsibility
  return bg;
}
```

### Caller pattern in mapper (`processSync`)

```java
BorderGate existing = borderGateService.findByCompanyIdAndCodeAndTypeAndSyncSourceConfigurationId(
    companyId, scuakhau.getMaCK(), "LOADING", syncSourceConfigId);

if (existing == null) {
  existing = new BorderGate();
  existing.setCompanyId(companyId);             // set only when new
  existing.setSyncSourceConfigurationId(syncSourceConfigId);
}

BorderGate result = scuakhau.toBorderGate(existing);
borderGateService.save(result);
```

### Rules

1. `to[EgovEntity]()` is a public **instance method** on the ECUS entity — never calls Spring services, never accesses `EcusTenantContext`.

2. `companyId` and `syncSourceConfigurationId` are **NOT set** inside `to*()`. They are set by the caller only when creating a new entity. Existing records already have them from DB. This is a deliberate change from the current pattern where some mappers set `companyId` unconditionally — the new behavior is correct and intentional.

3. **Trimmed code:** many ECUS entity fields contain trailing whitespace. The `to*()` method is responsible for trimming internally — not the caller. Use `Optional.ofNullable(this.field).map(String::trim).orElse(null)` for all code/key fields. Apply trim to every use of a field inside `to*()` — the field assignment, `originalId`, and any other assignment — regardless of whether the current mapper trims before or after calling `mapTo*()`. Several mappers trim a field only for the lookup key but pass the un-trimmed value into `mapTo*()`, where it is then assigned to both `code` and `originalId`. Known cases: `EcusSBIEU_THUE_TENMapper` (`maBT`), `EcusSDKGHMapper` (`maGH`), `EcusSPTVTMapper` (`maPTVT` trimmed for `setCode` but not `setOriginalId`). The new `to*()` methods for these entities must trim the field consistently everywhere. Review all 19 mappers systematically — do not rely solely on the named examples.

4. `to[EgovEntity]()` accepts `null` template defensively and creates a bare entity. In practice callers always pass a non-null template.

5. After refactor, the mapper's private `mapTo*()` method is **deleted entirely**.

---

## Architectural note — cross-module type coupling

ECUS entity classes currently import nothing from `ecutoms`. After this refactor, each ECUS entity will import one eGov entity type (e.g., `SCUAKHAU` imports `BorderGate`). This is a new **type-level coupling** from `ecus-thaison` entity classes into `ecutoms` entity classes.

The module-level dependency (`ecus-thaison` depends on `ecutoms`) already exists and will not change — this compiles without any build file changes. The tradeoff is accepted: ECUS entity classes gain a direct reference to their eGov counterpart, which is the whole point of the refactor (co-locating mapping knowledge with the source data).

---

## Scope

### In scope — company mappers (19 files)

| ECUS Entity file | eGov Target | New method on ECUS entity |
|---|---|---|
| `SCUAKHAU.java` | `BorderGate` | `toBorderGate(BorderGate)` |
| `SCUAKHAUNN.java` | `BorderGate` | `toBorderGate(BorderGate)` |
| `SHAIQUAN.java` | `CustomsOffice` | `toCustomsOffice(CustomsOffice)` |
| `SNUOC.java` | `EgovCountry` | `toEgovCountry(EgovCountry)` |
| `SDVT.java` | `EgovUnit` | `toEgovUnit(EgovUnit)` |
| `SLOAI_KIEN.java` | `EgovUnit` | `toEgovUnit(EgovUnit)` |
| `SNGTE.java` | `EgovCurrency` | `toEgovCurrency(EgovCurrency)` |
| `SNGAN_HANG.java` | `Bank` | `toBank(Bank)` |
| `SPTTT.java` | `InvoicePaymentMethod` | `toInvoicePaymentMethod(InvoicePaymentMethod)` |
| `SPTVT.java` | `TransportMode` | `toTransportMode(TransportMode)` |
| `SDKGH.java` | `InvoiceDeliveryTerms` | `toInvoiceDeliveryTerms(InvoiceDeliveryTerms)` |
| `SVB_PQ.java` | `CustomsLegalCode` | `toCustomsLegalCode(CustomsLegalCode)` |
| `SLOAI_GP.java` | `TradingLicenseType` | `toTradingLicenseType(TradingLicenseType)` |
| `SLHINHMD.java` | `DeclarationType` | `toDeclarationType(DeclarationType)` |
| `SMA_AP_MIENTHUE.java` | `TaxExemption` | `toTaxExemption(TaxExemption)` |
| `SMA_MIENTHUE.java` | `TaxExemptionCategory` | `toTaxExemptionCategory(TaxExemptionCategory)` |
| `REPORTSEXCEL.java` | `CustomsMessageType` | `toCustomsMessageType(CustomsMessageType)` |
| `SBIEU_THUE_TEN.java` | `TariffSchedule` | `toTariffSchedule(TariffSchedule)` |
| `DCHUNGTUKEM.java` | `AttachedDocument` | `toAttachedDocument(AttachedDocument)` |

### Explicitly excluded

| File | Reason |
|---|---|
| `EcusSMACACLOAIMapper` | Single ECUS entity (`SMACACLOAI`) fans out to 17 different eGov types based on a runtime `loaiMa` discriminator, with 18 `mapTo*()` methods (17 per eGov type + 1 shared field helper) each calling a distinct Spring service. Adding that many `to*()` methods on one entity is unreasonable. Excluded — keep current pattern. |
| `EcusSDIA_DIEMMapper` / `EcusSDIA_DIEM_THUPHIMapper` | `processSync()` delegates entirely to `transitLocationService.findOrCreateAndUpdateWithSyncSource()` with an inline lambda — there is no private `mapTo*()` method to move. The field assignment lives inside the service's updater lambda and is not separable without changing service-layer code that is out of scope. |
| All other partner mappers (including `EcusD_OLA_ContainerMapper`) | `mapTo*()` calls Spring services internally — cannot move to entity. |

---

## What changes per file

**ECUS entity class** (`ecus-thaison/entity/[SourceEntity].java`):
- Add `to[EgovEntity](template)` public instance method
- Add import for the eGov entity type (`com.egov.ecutoms.entity.*`)
- Replicate trim logic from mapper into the `to*()` method for any code/key fields

**Mapper class** (`logic/mapper/company/[XxxMapper].java`):
- `processSync()`: replace `mapTo*()` call block with template-prep pattern + `ecusEntity.to*(template)`
- Delete the private `mapTo*()` method
- Fix any inline FQCNs in `processSync()` while touching the method (e.g., `EcusSDKGHMapper` has `catch (org.springframework.dao.DataIntegrityViolationException e)` — replace with a proper `import` and simple name)

---

## Out of scope

- No change to `syncEntity()`, `processBatch()`, `SyncExecutor`, `SyncController`
- No `IEcusToEgov<T>` interface — YAGNI
- No changes to partner mappers
- No changes to `EcusSMACACLOAIMapper`
