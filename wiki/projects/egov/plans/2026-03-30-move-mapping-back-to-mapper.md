# Move `to*()` Mapping Back to Mapper Classes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the `to*(template)` instance methods from 19 ECUS entity classes back into their corresponding mapper classes as `private EgovXxx mapToEgovXxx(ECUS ecus, EgovXxx template)` private methods.

**Architecture:** Pure code movement — no logic changes. Each entity loses its `to*()` public method (and any private helpers), imports for egov types are removed from entities. Each mapper gains a `private mapToXxx(ecus, template)` method with identical logic (field accesses rewritten as `ecus.getField()`), and `processSync()` calls are updated from `entity.to*(existing)` to `mapToXxx(entity, existing)`.

**Tech Stack:** Java 21, Spring Boot 3.3.3, Lombok, Gradle (`:datatp-egov-module-ecus-thaison`)

---

## File Map

Each task modifies exactly one entity file and one mapper file:

| Entity (modify) | Mapper (modify) |
|---|---|
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/DCHUNGTUKEM.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusDCHUNGTUKEMMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/REPORTSEXCEL.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusREPORTSEXCELMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SBIEU_THUE_TEN.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSBIEU_THUE_TENMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SCUAKHAU.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SCUAKHAUNN.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUNNMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SDKGH.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDKGHMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SDVT.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDVTMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SHAIQUAN.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSHAIQUANMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLHINHMD.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLHINHMDMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLOAI_GP.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_GPMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLOAI_KIEN.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_KIENMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SMA_AP_MIENTHUE.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_AP_MIENTHUEMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SMA_MIENTHUE.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_MIENTHUEMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNGAN_HANG.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGAN_HANGMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNGTE.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGTEMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNUOC.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNUOCMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SPTTT.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTTTMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SPTVT.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTVTMapper.java` |
| `module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SVB_PQ.java` | `module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSVB_PQMapper.java` |

---

## Task 1: DCHUNGTUKEM + REPORTSEXCEL

**Files:**
- Modify: `entity/DCHUNGTUKEM.java`
- Modify: `mapper/company/EcusDCHUNGTUKEMMapper.java`
- Modify: `entity/REPORTSEXCEL.java`
- Modify: `mapper/company/EcusREPORTSEXCELMapper.java`

- [ ] **Step 1: Update `DCHUNGTUKEM.java`** — remove `toAttachedDocument()` method and `import com.egov.ecutoms.entity.AttachedDocument`

After removal, the only remaining import in DCHUNGTUKEM.java should be:
```java
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.math.BigDecimal;
import java.util.Date;
```

- [ ] **Step 2: Update `EcusDCHUNGTUKEMMapper.java`** — add `mapToAttachedDocument()` private method and update `processSync()` call

Add this method to `EcusDCHUNGTUKEMMapper` (after `processSync`):
```java
private AttachedDocument mapToAttachedDocument(DCHUNGTUKEM ecus, AttachedDocument template) {
    AttachedDocument ad = template != null ? template : new AttachedDocument();
    ad.setDocumentNumber(ecus.getSotn());
    ad.setDateCreated(ecus.getNgaytn());
    ad.setDocumentCode(ecus.getSoCt());
    ad.setDocumentDate(ecus.getNgayCt());
    ad.setDocumentTypeCode(ecus.getMaLoaiCt());
    ad.setDescription(ecus.getDienGiai());
    ad.setTotalSize(ecus.getTotalSize());
    ad.setCategoryType(ecus.getLoaiKB());
    ad.setStatus(ecus.getTrangThai());
    ad.setTempId(ecus.getTempt());
    ad.setMessageId(ecus.getMessageID());
    ad.setKdtReferences(ecus.getKdtReferences());
    ad.setKdtWaiting(ecus.getKdtWaiting());
    ad.setKdtLastInfo(ecus.getKdtLastInfo());
    ad.setIsSigned(ecus.getIsSign());
    ad.setSignData(ecus.getSignData());
    ad.setIsSubmitted(ecus.getIsTrinhKy());
    ad.setClassificationCategory(ecus.getPhanLoaiKB());
    ad.setProcedureName(ecus.getTenThuTucKB());
    ad.setCustomsOfficeCode(ecus.getMaHQ());
    ad.setProcessingGroup(ecus.getNhomXuLy());
    ad.setProcedureClassification(ecus.getPhanLoaiThuTuc());
    ad.setSubmitterPhone(ecus.getNguoiKBDienThoai());
    ad.setSubmitterName(ecus.getNguoiKBTen());
    ad.setSubmitterAddress(ecus.getNguoiKBDiaChi());
    ad.setManagementNumber(ecus.getSoQuanLyNB());
    ad.setAttachmentFileCount(ecus.getSoLayFileDinhKem());
    ad.setSubmissionDate(ecus.getNgayKB());
    ad.setDeclarationId(ecus.getDToKhaiMDID());
    ad.setTrackingNumber(ecus.getSotk());
    ad.setGuid(ecus.getGuid());
    ad.setIsTest(ecus.getIsTest());
    ad.setTestSubmissionNumber(ecus.getTestSoKB());
    ad.setTestScenario(ecus.getTestKichBan());
    ad.setTestNotes(ecus.getTestGhiChu());
    ad.setIsVersion2(ecus.getIsVersion2());
    ad.setSubmissionStatus(ecus.getTrangThaiKB());
    ad.setLegalBasis(ecus.getCanCuPhapLenh());
    ad.setNotificationDate(ecus.getNgayTB());
    ad.setDepartmentHeadName(ecus.getTenTruongDvHQ());
    ad.setCustomsNotes(ecus.getGhiChuHQ());
    ad.setDepartmentCode(ecus.getMaDV());
    ad.setOriginalId(ecus.getDChungTuKemID() != null ? String.valueOf(ecus.getDChungTuKemID()) : null);
    return ad;
}
```

In `processSync()`, replace:
```java
AttachedDocument saved = attachedDocumentService.save(dchungtukem.toAttachedDocument(existing));
```
with:
```java
AttachedDocument saved = attachedDocumentService.save(mapToAttachedDocument(dchungtukem, existing));
```

No import changes needed in mapper (all imports already present).

- [ ] **Step 3: Update `REPORTSEXCEL.java`** — remove `toCustomsMessageType()`, `determineChannelType()`, and `import com.egov.ecutoms.entity.CustomsMessageType` and `import java.util.Optional`

- [ ] **Step 4: Update `EcusREPORTSEXCELMapper.java`** — add `mapToCustomsMessageType()` and `determineChannelType()` private methods, update `processSync()` call

Add these methods (after `processSync`):
```java
private CustomsMessageType mapToCustomsMessageType(REPORTSEXCEL ecus, CustomsMessageType template) {
    CustomsMessageType cmt = template != null ? template : new CustomsMessageType();
    String trimCode = Optional.ofNullable(ecus.getMsgOutCode()).map(String::trim).orElse(null);
    cmt.setMessageCode(trimCode);
    cmt.setMessageName(ecus.getMsgOutName());
    cmt.setDeclarationType(ecus.getLoaiChungTu());
    cmt.setDescription(ecus.getFileName());
    cmt.setChannelType(determineChannelType(ecus.getMsgOutCode()));
    cmt.setOriginalId(trimCode);
    return cmt;
}

private String determineChannelType(String msgOutCode) {
    if (msgOutCode == null || msgOutCode.trim().isEmpty()) {
        return null;
    }
    String upperCode = msgOutCode.toUpperCase();
    if (upperCode.contains("1")) {
        return "VÀNG";
    } else if (upperCode.contains("2")) {
        return "XANH";
    } else if (upperCode.contains("3")) {
        return "ĐỎ";
    }
    return null;
}
```

In `processSync()`, replace:
```java
CustomsMessageType saved = customsMessageTypeService.save(reportsExcel.toCustomsMessageType(existing));
```
with:
```java
CustomsMessageType saved = customsMessageTypeService.save(mapToCustomsMessageType(reportsExcel, existing));
```

No import changes needed (`Optional` already present in mapper).

- [ ] **Step 5: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 6: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/DCHUNGTUKEM.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusDCHUNGTUKEMMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/REPORTSEXCEL.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusREPORTSEXCELMapper.java
git commit -m "refactor(ecus-thaison): move toAttachedDocument, toCustomsMessageType back to mapper"
```

---

## Task 2: SBIEU_THUE_TEN + SCUAKHAU + SCUAKHAUNN

**Files:**
- Modify: `entity/SBIEU_THUE_TEN.java`, `mapper/company/EcusSBIEU_THUE_TENMapper.java`
- Modify: `entity/SCUAKHAU.java`, `mapper/company/EcusSCUAKHAUMapper.java`
- Modify: `entity/SCUAKHAUNN.java`, `mapper/company/EcusSCUAKHAUNNMapper.java`

- [ ] **Step 1: Update `SBIEU_THUE_TEN.java`** — remove `toTariffSchedule()` and remove `import com.egov.ecutoms.entity.TariffSchedule` and `import java.util.Optional`

- [ ] **Step 2: Update `EcusSBIEU_THUE_TENMapper.java`** — add `mapToTariffSchedule()`, update `processSync()` call

Add method (after `processSync`):
```java
private TariffSchedule mapToTariffSchedule(SBIEU_THUE_TEN ecus, TariffSchedule template) {
    TariffSchedule ts = template != null ? template : new TariffSchedule();
    String trimmedCode = Optional.ofNullable(ecus.getMaBT()).map(String::trim).orElse(null);
    ts.setCode(trimmedCode);
    ts.setOriginalId(trimmedCode);
    ts.setDescription(ecus.getTenBT());
    ts.setDescriptionAlt(ecus.getTenBT1());
    ts.setCategory(ecus.getLoaiThue());
    ts.setNotes(ecus.getGhiChu());
    ts.setIsActive(true);
    return ts;
}
```

In `processSync()`, replace:
```java
tariffScheduleService.save(sbieuThueTen.toTariffSchedule(existing));
```
with:
```java
tariffScheduleService.save(mapToTariffSchedule(sbieuThueTen, existing));
```

- [ ] **Step 3: Update `SCUAKHAU.java`** — remove `toBorderGate()` and `import com.egov.ecutoms.entity.BorderGate`

- [ ] **Step 4: Update `EcusSCUAKHAUMapper.java`** — add `mapToBorderGate()`, update `processSync()` call

Add method (after `processSync`):
```java
private BorderGate mapToBorderGate(SCUAKHAU ecus, BorderGate template) {
    BorderGate bg = template != null ? template : new BorderGate();
    bg.setCode(ecus.getMaCK());
    bg.setName(ecus.getTenCK());
    bg.setNameAlt(ecus.getTenCK1());
    bg.setType("LOADING");
    bg.setDepartmentCode(ecus.getMaCuc());
    bg.setTableName(ecus.getTenBang());
    bg.setCountryCode(ecus.getMaNuoc());
    bg.setOldCode(ecus.getMaCu());
    bg.setOldName(ecus.getTenCu());
    bg.setNameVn(ecus.getTenCKVN());
    bg.setNameAltVn(ecus.getTenCK1VN());
    if (ecus.getIsVNACCS() != null) {
        bg.setIsVnaccs(ecus.getIsVNACCS() == 1);
    }
    bg.setIsActive(true);
    bg.setOriginalId(ecus.getMaCK());
    return bg;
}
```

In `processSync()`, replace:
```java
BorderGate savedBorderGate = borderGateService.save(scuakhau.toBorderGate(existing));
```
with:
```java
BorderGate savedBorderGate = borderGateService.save(mapToBorderGate(scuakhau, existing));
```

- [ ] **Step 5: Update `SCUAKHAUNN.java`** — remove `toBorderGate()` and `import com.egov.ecutoms.entity.BorderGate`

- [ ] **Step 6: Update `EcusSCUAKHAUNNMapper.java`** — add `mapToBorderGate()`, update `processSync()` call

Add method (after `processSync`):
```java
private BorderGate mapToBorderGate(SCUAKHAUNN ecus, BorderGate template) {
    BorderGate bg = template != null ? template : new BorderGate();
    bg.setCode(ecus.getMaCK());
    bg.setName(ecus.getTenCK());
    bg.setNameAlt(ecus.getTenCK1());
    bg.setType("UNLOADING");
    bg.setDepartmentCode(ecus.getMaCuc());
    bg.setTableName(ecus.getTenBang());
    bg.setCountryCode(ecus.getMaNuoc());
    bg.setOldCode(ecus.getMaCu());
    bg.setOldName(ecus.getTenCu());
    bg.setNameVn(ecus.getTenCKVN());
    bg.setNameAltVn(ecus.getTenCK1VN());
    if (ecus.getIsVNACCS() != null) {
        bg.setIsVnaccs(ecus.getIsVNACCS() == 1);
    }
    if (ecus.getItemType() != null && !ecus.getItemType().trim().isEmpty()) {
        bg.setDescription("ItemType: " + ecus.getItemType());
    }
    bg.setIsActive(true);
    bg.setOriginalId(ecus.getMaCK());
    return bg;
}
```

In `processSync()`, replace:
```java
BorderGate saved = borderGateService.save(scuakhaunn.toBorderGate(existing));
```
with:
```java
BorderGate saved = borderGateService.save(mapToBorderGate(scuakhaunn, existing));
```

- [ ] **Step 7: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 8: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SBIEU_THUE_TEN.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSBIEU_THUE_TENMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SCUAKHAU.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SCUAKHAUNN.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSCUAKHAUNNMapper.java
git commit -m "refactor(ecus-thaison): move toTariffSchedule, toBorderGate (x2) back to mapper"
```

---

## Task 3: SDKGH + SDVT + SHAIQUAN

**Files:**
- Modify: `entity/SDKGH.java`, `mapper/company/EcusSDKGHMapper.java`
- Modify: `entity/SDVT.java`, `mapper/company/EcusSDVTMapper.java`
- Modify: `entity/SHAIQUAN.java`, `mapper/company/EcusSHAIQUANMapper.java`

- [ ] **Step 1: Update `SDKGH.java`** — remove `toInvoiceDeliveryTerms()`, remove `import com.egov.ecutoms.entity.InvoiceDeliveryTerms` and `import java.util.Optional`

- [ ] **Step 2: Update `EcusSDKGHMapper.java`** — add `mapToInvoiceDeliveryTerms()`, update `processSync()` call

Add method:
```java
private InvoiceDeliveryTerms mapToInvoiceDeliveryTerms(SDKGH ecus, InvoiceDeliveryTerms template) {
    InvoiceDeliveryTerms idt = template != null ? template : new InvoiceDeliveryTerms();
    String trimmedCode = Optional.ofNullable(ecus.getMaGH()).map(String::trim).orElse(null);
    idt.setCode(trimmedCode);
    idt.setOriginalId(trimmedCode);
    idt.setName(ecus.getTenGH());
    idt.setNote(ecus.getGhiChu());
    idt.setTableName(ecus.getTenBang());
    idt.setNameTcvn(ecus.getTenGHTCVN());
    idt.setIsActive(true);
    return idt;
}
```

In `processSync()`, replace:
```java
invoiceDeliveryTermsService.save(sdkgh.toInvoiceDeliveryTerms(existing));
```
with:
```java
invoiceDeliveryTermsService.save(mapToInvoiceDeliveryTerms(sdkgh, existing));
```

- [ ] **Step 3: Update `SDVT.java`** — remove `toEgovUnit()`, remove `import com.egov.ecutoms.entity.EgovUnit` and `import org.springframework.util.StringUtils`

- [ ] **Step 4: Update `EcusSDVTMapper.java`** — add `mapToEgovUnit()`, update `processSync()` call

`StringUtils` is already imported in this mapper. Add method:
```java
private EgovUnit mapToEgovUnit(SDVT ecus, EgovUnit template) {
    EgovUnit unit = template != null ? template : new EgovUnit();
    String trimmedCode = ecus.getMaDVT() != null ? StringUtils.trimAllWhitespace(ecus.getMaDVT()) : null;
    unit.setCode(trimmedCode);
    unit.setName(ecus.getTenDVT());
    unit.setNameAlt(ecus.getTenDVT1());
    unit.setNameVn(ecus.getTenDVTVN());
    unit.setNameAltVn(ecus.getTenDVT1VN());
    unit.setTableName(ecus.getTenBang());
    unit.setIsVnaccs(ecus.getIsVNACCS());
    unit.setOldCode(ecus.getMaCu());
    unit.setOldName(ecus.getTenCu());
    unit.setDisplayOrder(ecus.getHienThi());
    unit.setIsActive(true);
    unit.setSourceId("ECUS_" + ecus.getMaDVT());
    unit.setOriginalId(trimmedCode);
    return unit;
}
```

In `processSync()`, replace:
```java
egovUnitService.save(sdvt.toEgovUnit(existing));
```
with:
```java
egovUnitService.save(mapToEgovUnit(sdvt, existing));
```

- [ ] **Step 5: Update `SHAIQUAN.java`** — remove `toCustomsOffice()`, remove `import com.egov.ecutoms.entity.CustomsOffice` and `import java.util.Optional`

- [ ] **Step 6: Update `EcusSHAIQUANMapper.java`** — add `import java.util.Optional`, add `mapToCustomsOffice()`, update `processSync()` call

Add import at top (not already present):
```java
import java.util.Optional;
```

Add method:
```java
private CustomsOffice mapToCustomsOffice(SHAIQUAN ecus, CustomsOffice template) {
    CustomsOffice co = template != null ? template : new CustomsOffice();
    String trimCode = Optional.ofNullable(ecus.getMaHQ()).map(String::trim).orElse(null);
    co.setCode(trimCode);
    co.setName(ecus.getTenHQ() != null ? ecus.getTenHQ().trim() : null);
    co.setAlternateName(ecus.getTenHQ1());
    co.setLevel(ecus.getCapHQ());
    co.setIsDisplayed(ecus.getHienThi());
    co.setIsVNACCS(ecus.getIsVNACCS());
    co.setTableName(ecus.getTenBang());
    co.setOldCode(ecus.getMaCu());
    co.setOldName(ecus.getTenCu());
    co.setVietnameseName(ecus.getTenHQVN());
    co.setVietnameseAlternateName(ecus.getTenHQ1VN());
    co.setShortName(ecus.getTenHQVT());
    co.setOriginalId(trimCode);
    return co;
}
```

In `processSync()`, replace:
```java
CustomsOffice savedOffice = customsOfficeService.save(shaiquan.toCustomsOffice(existing));
```
with:
```java
CustomsOffice savedOffice = customsOfficeService.save(mapToCustomsOffice(shaiquan, existing));
```

- [ ] **Step 7: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 8: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SDKGH.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDKGHMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SDVT.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSDVTMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SHAIQUAN.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSHAIQUANMapper.java
git commit -m "refactor(ecus-thaison): move toInvoiceDeliveryTerms, toEgovUnit, toCustomsOffice back to mapper"
```

---

## Task 4: SLHINHMD + SLOAI_GP + SLOAI_KIEN

**Files:**
- Modify: `entity/SLHINHMD.java`, `mapper/company/EcusSLHINHMDMapper.java`
- Modify: `entity/SLOAI_GP.java`, `mapper/company/EcusSLOAI_GPMapper.java`
- Modify: `entity/SLOAI_KIEN.java`, `mapper/company/EcusSLOAI_KIENMapper.java`

- [ ] **Step 1: Update `SLHINHMD.java`** — remove `toDeclarationType()`, remove `import com.egov.ecutoms.entity.DeclarationType` and `import java.util.Optional`

- [ ] **Step 2: Update `EcusSLHINHMDMapper.java`** — add `mapToDeclarationType()`, update `processSync()` call

Add method:
```java
private DeclarationType mapToDeclarationType(SLHINHMD ecus, DeclarationType template) {
    DeclarationType result = template != null ? template : new DeclarationType();
    String trimCode = Optional.ofNullable(ecus.getMaLH()).map(String::trim).orElse(null);
    result.setCode(trimCode);
    result.setOriginalId(trimCode);
    result.setGroupCode(ecus.getNhomLH());
    result.setName(ecus.getTenLH());
    result.setName1(ecus.getTenLH1());
    result.setAlias(ecus.getTenVT());
    result.setSequence(ecus.getSoTT());
    result.setDisplayOrder(ecus.getHienThi() != null ? (ecus.getHienThi() ? 1 : 0) : 0);
    result.setTableName(ecus.getTenBang());
    result.setOldCode(ecus.getMaCu());
    result.setOldName(ecus.getTenCu());
    result.setNameVn(ecus.getTenLHVN());
    result.setNameVn1(ecus.getTenLH1VN());
    result.setIsActive(true);
    return result;
}
```

In `processSync()`, replace:
```java
declarationTypeService.save(slhinhmd.toDeclarationType(existing));
```
with:
```java
declarationTypeService.save(mapToDeclarationType(slhinhmd, existing));
```

- [ ] **Step 3: Update `SLOAI_GP.java`** — remove `toTradingLicenseType()`, remove `import com.egov.ecutoms.entity.TradingLicenseType` and `import java.util.Optional`

- [ ] **Step 4: Update `EcusSLOAI_GPMapper.java`** — add `mapToTradingLicenseType()`, update `processSync()` call

Add method:
```java
private TradingLicenseType mapToTradingLicenseType(SLOAI_GP ecus, TradingLicenseType template) {
    TradingLicenseType lt = template != null ? template : new TradingLicenseType();
    String trimmedCode = Optional.ofNullable(ecus.getMaLoaiGP()).map(String::trim).orElse(null);
    lt.setCode(trimmedCode);
    lt.setOriginalId(trimmedCode);
    lt.setName(ecus.getTenLoaiGP());
    lt.setNameAlt(ecus.getTenLoaiGP1());
    lt.setTableName(ecus.getTenBang());
    lt.setCategory(TradingLicenseType.Category.BOTH);
    lt.setIsActive(true);
    return lt;
}
```

In `processSync()`, replace:
```java
tradingLicenseTypeService.save(sloaiGP.toTradingLicenseType(existing));
```
with:
```java
tradingLicenseTypeService.save(mapToTradingLicenseType(sloaiGP, existing));
```

- [ ] **Step 5: Update `SLOAI_KIEN.java`** — remove `toEgovUnit()`, remove `import com.egov.ecutoms.entity.EgovUnit` and `import org.springframework.util.StringUtils`

- [ ] **Step 6: Update `EcusSLOAI_KIENMapper.java`** — add `mapToEgovUnit()`, update `processSync()` call

`StringUtils` is already imported in this mapper. Add method:
```java
private EgovUnit mapToEgovUnit(SLOAI_KIEN ecus, EgovUnit template) {
    EgovUnit unit = template != null ? template : new EgovUnit();
    String trimmedCode = ecus.getMaLK() != null ? StringUtils.trimAllWhitespace(ecus.getMaLK()) : null;
    unit.setCode(trimmedCode);
    unit.setName(ecus.getTenLK());
    unit.setNameAlt(ecus.getTenLK1());
    unit.setNameVn(ecus.getTenLKVN());
    unit.setNameAltVn(ecus.getTenLK1VN());
    unit.setTableName(ecus.getTenBang());
    unit.setIsVnaccs(ecus.getIsVNACCS());
    unit.setOldCode(ecus.getMaCu());
    unit.setOldName(ecus.getTenCu());
    unit.setDisplayOrder(ecus.getHienThi());
    unit.setIsActive(true);
    unit.setSourceId("ECUS_" + ecus.getMaLK());
    unit.setOriginalId(trimmedCode);
    return unit;
}
```

In `processSync()`, replace:
```java
egovUnitService.save(sloaiKien.toEgovUnit(existing));
```
with:
```java
egovUnitService.save(mapToEgovUnit(sloaiKien, existing));
```

- [ ] **Step 7: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 8: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLHINHMD.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLHINHMDMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLOAI_GP.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_GPMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SLOAI_KIEN.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSLOAI_KIENMapper.java
git commit -m "refactor(ecus-thaison): move toDeclarationType, toTradingLicenseType, toEgovUnit back to mapper"
```

---

## Task 5: SMA_AP_MIENTHUE + SMA_MIENTHUE + SNGAN_HANG + SNGTE

**Files:**
- Modify: `entity/SMA_AP_MIENTHUE.java`, `mapper/company/EcusSMA_AP_MIENTHUEMapper.java`
- Modify: `entity/SMA_MIENTHUE.java`, `mapper/company/EcusSMA_MIENTHUEMapper.java`
- Modify: `entity/SNGAN_HANG.java`, `mapper/company/EcusSNGAN_HANGMapper.java`
- Modify: `entity/SNGTE.java`, `mapper/company/EcusSNGTEMapper.java`

- [ ] **Step 1: Update `SMA_AP_MIENTHUE.java`** — remove `toTaxExemption()`, remove `import com.egov.ecutoms.entity.TaxExemption` and `import java.util.Optional`

- [ ] **Step 2: Update `EcusSMA_AP_MIENTHUEMapper.java`** — add `mapToTaxExemption()`, update `processSync()` call

Add method:
```java
private TaxExemption mapToTaxExemption(SMA_AP_MIENTHUE ecus, TaxExemption template) {
    TaxExemption result = template != null ? template : new TaxExemption();
    String trimCode = Optional.ofNullable(ecus.getCode()).map(String::trim).orElse(null);
    result.setCode(trimCode);
    result.setOriginalId(trimCode);
    result.setIssueDate(ecus.getNgayPhatHanh());
    result.setEffectiveDate(ecus.getNgayHieuLuc());
    result.setExpiryDate(ecus.getNgayHH());
    result.setExemptionRate(ecus.getTyLe());
    result.setUnitCode(ecus.getMaDVT());
    result.setCurrencyCode(ecus.getMaNT());
    result.setTableId(ecus.getTableID());
    result.setKeyField(ecus.getKeyField());
    result.setDisplayOrder(ecus.getHienThi());
    result.setName(ecus.getTen());
    result.setType(ecus.getType());
    result.setIsActive(true);
    return result;
}
```

In `processSync()`, replace:
```java
taxExemptionService.save(smaApMienThue.toTaxExemption(existing));
```
with:
```java
taxExemptionService.save(mapToTaxExemption(smaApMienThue, existing));
```

- [ ] **Step 3: Update `SMA_MIENTHUE.java`** — remove `toTaxExemptionCategory()`, remove `import com.egov.ecutoms.entity.TaxExemptionCategory` and `import java.util.Optional`

- [ ] **Step 4: Update `EcusSMA_MIENTHUEMapper.java`** — add `mapToTaxExemptionCategory()`, update `processSync()` call

Add method:
```java
private TaxExemptionCategory mapToTaxExemptionCategory(SMA_MIENTHUE ecus, TaxExemptionCategory template) {
    TaxExemptionCategory result = template != null ? template : new TaxExemptionCategory();
    String trimCode = Optional.ofNullable(ecus.getMa()).map(String::trim).orElse(null);
    result.setCode(trimCode);
    result.setOriginalId(trimCode);
    result.setIssueDate(ecus.getNgayBanHanh());
    result.setEffectiveDate(ecus.getNgayHieuLuc());
    result.setExpiryDate(ecus.getNgayHH());
    result.setName(ecus.getTen());
    result.setTableId(ecus.getTableID());
    result.setKeyField(ecus.getKeyField());
    result.setNameVn(ecus.getTenVN());
    result.setNameVnTcvn(ecus.getTenVNTCVN());
    result.setType(ecus.getType());
    result.setDisplayOrder(ecus.getHienThi());
    result.setIsActive(true);
    return result;
}
```

In `processSync()`, replace:
```java
taxExemptionCategoryService.save(smaMienThue.toTaxExemptionCategory(existing));
```
with:
```java
taxExemptionCategoryService.save(mapToTaxExemptionCategory(smaMienThue, existing));
```

- [ ] **Step 5: Update `SNGAN_HANG.java`** — remove `toBank()`, remove `import com.egov.ecutoms.entity.Bank` and `import java.util.Optional`

- [ ] **Step 6: Update `EcusSNGAN_HANGMapper.java`** — add `mapToBank()`, update `processSync()` call

Add method:
```java
private Bank mapToBank(SNGAN_HANG ecus, Bank template) {
    Bank bank = template != null ? template : new Bank();
    String trimmedCode = Optional.ofNullable(ecus.getMaNH()).map(String::trim).orElse(null);
    bank.setCode(trimmedCode);
    bank.setOriginalId(trimmedCode);
    bank.setName(ecus.getTenNH());
    bank.setNameAlt(ecus.getTenNH1());
    bank.setNote(ecus.getGhiChu());
    bank.setTableName(ecus.getTenBang());
    bank.setIsActive(true);
    return bank;
}
```

In `processSync()`, replace:
```java
bankService.save(snganHang.toBank(existing));
```
with:
```java
bankService.save(mapToBank(snganHang, existing));
```

- [ ] **Step 7: Update `SNGTE.java`** — remove `toEgovCurrency()`, remove `import com.egov.ecutoms.entity.EgovCurrency`, `import java.util.Optional`, and `import java.math.BigDecimal`

- [ ] **Step 8: Update `EcusSNGTEMapper.java`** — add `import java.math.BigDecimal`, add `mapToEgovCurrency()`, update `processSync()` call

Add import (not currently present in mapper):
```java
import java.math.BigDecimal;
```

Add method:
```java
private EgovCurrency mapToEgovCurrency(SNGTE ecus, EgovCurrency template) {
    EgovCurrency c = template != null ? template : new EgovCurrency();
    String trimCode = Optional.ofNullable(ecus.getMaNT()).map(String::trim).orElse(null);
    c.setCode(trimCode);
    c.setName(ecus.getTenNT());
    c.setNameAlt(ecus.getTenNT1());
    c.setTableName(ecus.getTenBang());
    if (ecus.getTygiaVND() != null) {
        c.setExchangeRateVnd(BigDecimal.valueOf(ecus.getTygiaVND().doubleValue()));
    }
    c.setIsActive(true);
    c.setSourceId("ECUS_" + ecus.getMaNT());
    c.setOriginalId(trimCode);
    return c;
}
```

In `processSync()`, replace:
```java
egovCurrencyService.save(sngte.toEgovCurrency(existing));
```
with:
```java
egovCurrencyService.save(mapToEgovCurrency(sngte, existing));
```

- [ ] **Step 9: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 10: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SMA_AP_MIENTHUE.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_AP_MIENTHUEMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SMA_MIENTHUE.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSMA_MIENTHUEMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNGAN_HANG.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGAN_HANGMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNGTE.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNGTEMapper.java
git commit -m "refactor(ecus-thaison): move toTaxExemption, toTaxExemptionCategory, toBank, toEgovCurrency back to mapper"
```

---

## Task 6: SNUOC + SPTTT + SPTVT + SVB_PQ

**Files:**
- Modify: `entity/SNUOC.java`, `mapper/company/EcusSNUOCMapper.java`
- Modify: `entity/SPTTT.java`, `mapper/company/EcusSPTTTMapper.java`
- Modify: `entity/SPTVT.java`, `mapper/company/EcusSPTVTMapper.java`
- Modify: `entity/SVB_PQ.java`, `mapper/company/EcusSVB_PQMapper.java`

- [ ] **Step 1: Update `SNUOC.java`** — remove `toEgovCountry()`, remove `import com.egov.ecutoms.entity.EgovCountry` and `import java.util.Optional`

- [ ] **Step 2: Update `EcusSNUOCMapper.java`** — add `mapToEgovCountry()`, update `processSync()` call

Add method:
```java
private EgovCountry mapToEgovCountry(SNUOC ecus, EgovCountry template) {
    EgovCountry c = template != null ? template : new EgovCountry();
    String trimCode = Optional.ofNullable(ecus.getMaNuoc()).map(String::trim).orElse(null);
    c.setCode(trimCode);
    c.setName(ecus.getTenNuoc());
    c.setNameAlt(ecus.getTenNuoc1());
    c.setNameVn(ecus.getTenNuocVN());
    c.setNameAltVn(ecus.getTenNuoc1VN());
    c.setCurrencyCode(ecus.getMaNT());
    c.setDisplayOrder(ecus.getHienThi());
    c.setIsActive(true);
    c.setSourceId("ECUS_" + ecus.getMaNuoc());
    c.setOriginalId(trimCode);
    return c;
}
```

In `processSync()`, replace:
```java
egovCountryService.save(snuoc.toEgovCountry(existing));
```
with:
```java
egovCountryService.save(mapToEgovCountry(snuoc, existing));
```

- [ ] **Step 3: Update `SPTTT.java`** — remove `toInvoicePaymentMethod()`, remove `import com.egov.ecutoms.entity.InvoicePaymentMethod` and `import java.util.Optional`

- [ ] **Step 4: Update `EcusSPTTTMapper.java`** — add `mapToInvoicePaymentMethod()`, update `processSync()` call

Add method:
```java
private InvoicePaymentMethod mapToInvoicePaymentMethod(SPTTT ecus, InvoicePaymentMethod template) {
    InvoicePaymentMethod paymentMethod = template != null ? template : new InvoicePaymentMethod();
    String trimmedCode = Optional.ofNullable(ecus.getMaPTTT()).map(String::trim).orElse(null);
    paymentMethod.setCode(trimmedCode);
    paymentMethod.setOriginalId(trimmedCode);
    paymentMethod.setName(ecus.getTenPTTT());
    paymentMethod.setNameTcvn(ecus.getTenPTTTTCVN());
    paymentMethod.setNote(ecus.getGhiChu());
    paymentMethod.setIsActive(true);
    return paymentMethod;
}
```

In `processSync()`, replace:
```java
invoicePaymentMethodService.save(spttt.toInvoicePaymentMethod(existing));
```
with:
```java
invoicePaymentMethodService.save(mapToInvoicePaymentMethod(spttt, existing));
```

- [ ] **Step 5: Update `SPTVT.java`** — remove `toTransportMode()`, remove `import com.egov.ecutoms.entity.TransportMode` and `import java.util.Optional`

- [ ] **Step 6: Update `EcusSPTVTMapper.java`** — add `mapToTransportMode()`, update `processSync()` call

Add method:
```java
private TransportMode mapToTransportMode(SPTVT ecus, TransportMode template) {
    TransportMode tm = template != null ? template : new TransportMode();
    String trimmedCode = Optional.ofNullable(ecus.getMaPTVT()).map(String::trim).orElse(null);
    tm.setCode(trimmedCode);
    tm.setOriginalId(trimmedCode);
    tm.setName(ecus.getTenPTVT());
    tm.setNameAlt(ecus.getTenPTVT1());
    tm.setDeclarationNumber(ecus.getSpSoTK());
    tm.setDeclarationTypeCode(ecus.getSpMaLH());
    tm.setCustomsCode(ecus.getSpMaHQ());
    tm.setRegistrationYear(ecus.getSpNamDK());
    tm.setNameVn(ecus.getTenPTVTVN());
    tm.setNameAltVn(ecus.getTenPTVT1VN());
    tm.setDisplayOrder(ecus.getHienThi());
    tm.setIsVnaccs(ecus.getIsVNACCS() != null && ecus.getIsVNACCS() == 1);
    tm.setIsActive(true);
    return tm;
}
```

In `processSync()`, replace:
```java
transportModeService.save(sptvt.toTransportMode(existing));
```
with:
```java
transportModeService.save(mapToTransportMode(sptvt, existing));
```

- [ ] **Step 7: Update `SVB_PQ.java`** — remove `toCustomsLegalCode()`, remove `import com.egov.ecutoms.entity.CustomsLegalCode` and `import java.util.Optional`

- [ ] **Step 8: Update `EcusSVB_PQMapper.java`** — add `mapToCustomsLegalCode()`, update `processSync()` call

Add method:
```java
private CustomsLegalCode mapToCustomsLegalCode(SVB_PQ ecus, CustomsLegalCode template) {
    CustomsLegalCode lc = template != null ? template : new CustomsLegalCode();
    String trimmedCode = Optional.ofNullable(ecus.getMaVB()).map(String::trim).orElse(null);
    lc.setCode(trimmedCode);
    lc.setOriginalId(trimmedCode);
    lc.setLegalDocumentNo(ecus.getSoHieu());
    lc.setDocumentDate(ecus.getNgayVB());
    lc.setContent(ecus.getNoiDung());
    lc.setContentTcvn(ecus.getNoiDungTCVN());
    lc.setDisplayOrder(ecus.getHienThi());
    if (ecus.getExport() != null) {
        lc.setIsExport(ecus.getExport());
    }
    if (ecus.getImportField() != null) {
        lc.setIsImport(ecus.getImportField());
    }
    if (ecus.getSoHieu() != null && !ecus.getSoHieu().trim().isEmpty()) {
        lc.setName("Van ban " + ecus.getSoHieu());
    } else {
        lc.setName("Van ban " + trimmedCode);
    }
    lc.setIsActive(true);
    return lc;
}
```

In `processSync()`, replace:
```java
customsLegalCodeService.save(svbPQ.toCustomsLegalCode(existing));
```
with:
```java
customsLegalCodeService.save(mapToCustomsLegalCode(svbPQ, existing));
```

- [ ] **Step 9: Compile check**
```bash
./gradlew :datatp-egov-module-ecus-thaison:compileJava
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 10: Commit**
```bash
git add module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SNUOC.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSNUOCMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SPTTT.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTTTMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SPTVT.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSPTVTMapper.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/SVB_PQ.java \
        module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/EcusSVB_PQMapper.java
git commit -m "refactor(ecus-thaison): move toEgovCountry, toInvoicePaymentMethod, toTransportMode, toCustomsLegalCode back to mapper"
```

---

## Task 7: Full test run

- [ ] **Step 1: Run full module tests**
```bash
./gradlew :datatp-egov-module-ecus-thaison:test
```
Expected: BUILD SUCCESSFUL, all tests pass

- [ ] **Step 2: Verify no entity still has `to*()` methods**
```bash
grep -r "public.*to[A-Z].*template" module/ecus-thaison/src/main/java/com/egov/ecusthaison/entity/
```
Expected: no output

- [ ] **Step 3: Verify all mappers have `mapTo*()` methods**
```bash
grep -r "private.*mapTo[A-Z]" module/ecus-thaison/src/main/java/com/egov/ecusthaison/logic/mapper/company/
```
Expected: 20 lines (19 mappers, REPORTSEXCEL has 2 private methods)
