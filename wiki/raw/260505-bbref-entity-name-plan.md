# BBRefEntity Popup Title Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `searchTitle` and `infoTitle` props to BBRefEntity base class, then pass Vietnamese search titles at all caller sites in eGov to match ECUS UX.

**Architecture:** Add 2 optional props to base class (backward-compatible), then add `searchTitle="Chọn ..."` at each BBRef usage.

**Tech Stack:** React/TypeScript, `@of1-webui/lib`

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260505-bbref-entity-name.md`
**Issue:** of1-egov/of1-egov#265

---

## Mapping Reference

| Component | searchTitle |
|-----------|-------------|
| BBRefDeclarationType | "Chọn loại hình tờ khai" |
| BBRefCustomsOffice | "Chọn cơ quan hải quan" |
| BBRefClassification | "Chọn phân loại cá nhân/tổ chức" |
| BBRefTransportMode | "Chọn phương thức vận chuyển" |
| BBRefInvoiceType | "Chọn phân loại hình thức hoá đơn" |
| BBRefInvoicePaymentMethod | "Chọn phương thức thanh toán" |
| BBRefInvoicePriceClassification | "Chọn phân loại giá hoá đơn" |
| BBRefInvoiceDeliveryTerms | "Chọn điều kiện giao hàng" |
| BBRefEgovCurrency | "Chọn loại tiền tệ" |
| BBRefTradingOrganization | "Chọn doanh nghiệp đối tác" |
| BBRefEgovCountry | "Chọn quốc gia" |
| BBRefEgovUnit | "Chọn đơn vị tính" |
| BBRefTariffSchedule | "Chọn mã biểu thuế" |
| BBRefEgovTaxExemption | "Chọn miễn giảm thuế" |
| BBRefEgovTaxExemptionCategory | "Chọn loại miễn giảm thuế" |
| BBRefCustomsLegalCode | "Chọn văn bản pháp quy" |
| BBRefTradingLicenseType | "Chọn loại giấy phép" |
| BBRefTransitLocation | "Chọn địa điểm lưu kho" |
| BBRefBorderGate | "Chọn cửa khẩu/cảng" |
| BBRefTransportPurpose | "Chọn mục đích vận chuyển" |
| BBRefBank | "Chọn ngân hàng" |
| BBRefTaxpayerType | "Chọn loại người nộp thuế" |
| BBRefMeasureReason | "Chọn lý do biện pháp" |
| BBRefPaymentDeadline | "Chọn thời hạn nộp thuế" |
| BBRefValuationDeclarationType | "Chọn phân loại khai trị giá" |
| BBRefValuationFreightChargeType | "Chọn phân loại phí vận tải" |
| BBRefValuationInsuranceChargeType | "Chọn phân loại phí bảo hiểm" |
| BBRefValuationAdjustmentItemType | "Chọn loại điều chỉnh" |
| BBRefValuationAdjustmentCategory | "Chọn nhóm điều chỉnh" |
| BBRefSyncSource | "Chọn nguồn đồng bộ" |
| BBRefPartnerCompany | "Chọn công ty đối tác" |
| BBRefAccountPartnerCompany | "Chọn công ty đối tác" |

---

## Tasks

### Task 1: Base Class — Add props to BBRefEntity (of1-core)

**File:** `/Users/nqcdan/OF1/forgejo/of1-platform/of1-core/webui/lib/src/entity/BBRefEntity.tsx`

- [ ] **Step 1: Add searchTitle and infoTitle to BBRefEntityProps (after line 350)**

```typescript
  refEntityName?: string;
  searchTitle?: string;
  infoTitle?: string;
```

- [ ] **Step 2: Update info popup title (line 588)**

Change:
```typescript
let title = refEntityName || 'Ref Entity';
```
To:
```typescript
let { appContext, pageContext, bean: bean, refEntityName, infoTitle } = this.props;
let title = infoTitle || refEntityName || 'Ref Entity';
```

- [ ] **Step 3: Update search popup title (line 641)**

Change:
```typescript
let { pageContext, refEntityName } = this.props;
let searchTitle = refEntityName ? `Search ${refEntityName}` : 'Search Ref Entities';
```
To:
```typescript
let { pageContext, refEntityName, searchTitle: searchTitleProp } = this.props;
let searchTitle = searchTitleProp || (refEntityName ? `Search ${refEntityName}` : 'Search Ref Entities');
```

- [ ] **Step 4: Update multi-entity info title (line 917)**

Change:
```typescript
let title = refEntityName || 'Ref Entity';
```
To:
```typescript
let { appContext, pageContext, hideMoreInfo, refEntityName, infoTitle } = this.props;
let title = infoTitle || refEntityName || 'Ref Entity';
```

- [ ] **Step 5: Build of1-core lib**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-core/webui/lib && pnpm build
```

---

### Task 2: UIBasicInformationEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/UIBasicInformationEntity.tsx`

- [ ] **Step 1: Add searchTitle to all 4 BBRef usages**

Line 70 — BBRefDeclarationType:
```tsx
<BBRefDeclarationType minWidth={500} offset={[0, 0]} placement='bottom-start'
  searchTitle="Chọn loại hình tờ khai"
  appContext={appContext} pageContext={pageContext}
```

Line 88 — BBRefCustomsOffice:
```tsx
<BBRefCustomsOffice required minWidth={500} offset={[0, 0]} placement='bottom-start'
  searchTitle="Chọn cơ quan hải quan"
  appContext={appContext} pageContext={pageContext}
```

Line 95 — BBRefClassification:
```tsx
<BBRefClassification required minWidth={500} offset={[0, 0]} placement='bottom-start'
  searchTitle="Chọn phân loại cá nhân/tổ chức"
  appContext={appContext} pageContext={pageContext}
```

Line 124 — BBRefTransportMode:
```tsx
<BBRefTransportMode required minWidth={500} offset={[0, 0]} placement='bottom-start'
  searchTitle="Chọn phương thức vận chuyển"
  appContext={appContext} pageContext={pageContext}
```

---

### Task 3: TradingInvoiceEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/TradingInvoiceEntity.tsx`

- [ ] **Step 1: Add searchTitle to all 5 BBRef usages**

Line 38 — BBRefInvoiceType: `searchTitle="Chọn phân loại hình thức hoá đơn"`
Line 67 — BBRefInvoicePaymentMethod: `searchTitle="Chọn phương thức thanh toán"`
Line 80 — BBRefInvoicePriceClassification: `searchTitle="Chọn phân loại giá hoá đơn"`
Line 91 — BBRefInvoiceDeliveryTerms: `searchTitle="Chọn điều kiện giao hàng"`
Line 108 — BBRefEgovCurrency: `searchTitle="Chọn loại tiền tệ"`

---

### Task 4: ImportExportXEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/ImportExportXEntity.tsx`

- [ ] **Step 1: Add searchTitle to all BBRef usages**

Lines 47, 103 — BBRefTradingOrganization: `searchTitle="Chọn doanh nghiệp đối tác"`
Line 134 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`

---

### Task 5: ImportExportNEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/ImportExportNEntity.tsx`

- [ ] **Step 1: Add searchTitle to all BBRef usages**

Lines 51, 90, 117 — BBRefTradingOrganization: `searchTitle="Chọn doanh nghiệp đối tác"`
Line 145 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`

---

### Task 6: TaxAndGuaranteeEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/TaxAndGuaranteeEntity.tsx`

- [ ] **Step 1: Add searchTitle to all BBRef usages**

Line 41 — BBRefMeasureReason: `searchTitle="Chọn lý do biện pháp"`
Line 63 — BBRefTaxpayerType: `searchTitle="Chọn loại người nộp thuế"`
Line 101 — BBRefPaymentDeadline: `searchTitle="Chọn thời hạn nộp thuế"`
Lines 148, 167 — BBRefBank: `searchTitle="Chọn ngân hàng"`

---

### Task 7: DeclarationLicenseEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/DeclarationLicenseEntity.tsx`

- [ ] **Step 1: Add searchTitle to all BBRef usages**

Line 57 — BBRefCustomsLegalCode: `searchTitle="Chọn văn bản pháp quy"`
Line 85 — BBRefTradingLicenseType: `searchTitle="Chọn loại giấy phép"`

---

### Task 8: TransportDocumentEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/TransportDocumentEntity.tsx`

- [ ] **Step 1: Add searchTitle to all BBRef usages**

Lines 381, 393 — BBRefEgovUnit: `searchTitle="Chọn đơn vị tính"`
Line 408 — BBRefTransitLocation: `searchTitle="Chọn địa điểm lưu kho"`
Lines 453, 463 — BBRefBorderGate: `searchTitle="Chọn cửa khẩu/cảng"`

---

### Task 9: TransportInformationEntity.tsx + ExportContainerEntity.tsx

**Files:**
- `declaration/detail-screens/TransportInformationEntity.tsx`
- `declaration/detail-screens/ExportContainerEntity.tsx`

- [ ] **Step 1: Add searchTitle**

TransportInformationEntity — lines 91, 148 — BBRefTransitLocation: `searchTitle="Chọn địa điểm lưu kho"`
ExportContainerEntity — line 48 — BBRefTransitLocation: `searchTitle="Chọn địa điểm lưu kho"`

---

### Task 10: ValuationDeclarationEntity.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/ValuationDeclarationEntity.tsx`

- [ ] **Step 1: Add searchTitle to all 10 BBRef usages**

Line 83 — BBRefValuationDeclarationType: `searchTitle="Chọn phân loại khai trị giá"`
Lines 106, 149, 189, 256 — BBRefEgovCurrency: `searchTitle="Chọn loại tiền tệ"`
Line 136 — BBRefValuationFreightChargeType: `searchTitle="Chọn phân loại phí vận tải"`
Line 175 — BBRefValuationInsuranceChargeType: `searchTitle="Chọn phân loại phí bảo hiểm"`
Line 232 — BBRefValuationAdjustmentItemType: `searchTitle="Chọn loại điều chỉnh"`
Line 244 — BBRefValuationAdjustmentCategory: `searchTitle="Chọn nhóm điều chỉnh"`
Line 311 — BBRefTaxpayerType: `searchTitle="Chọn loại người nộp thuế"`

---

### Task 11: OLA Screens

**Files:**
- `declaration/detail-screens/ola-screen/UIOLAInformationSection.tsx`
- `declaration/detail-screens/ola-screen/UIOLAGoodsInformationSection.tsx`
- `declaration/detail-screens/ola-screen/UILoadingLocationSection.tsx`

- [ ] **Step 1: UIOLAInformationSection**

Line 45 — BBRefCustomsOffice: `searchTitle="Chọn cơ quan hải quan"`
Line 97 — BBRefTransportMode: `searchTitle="Chọn phương thức vận chuyển"`
Line 109 — BBRefTransportPurpose: `searchTitle="Chọn mục đích vận chuyển"`

- [ ] **Step 2: UIOLAGoodsInformationSection**

Line 78 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`
Lines 90, 102 — BBRefBorderGate: `searchTitle="Chọn cửa khẩu/cảng"`
Line 121 — BBRefTransportMode: `searchTitle="Chọn phương thức vận chuyển"`
Lines 243, 266, 289 — BBRefEgovUnit: `searchTitle="Chọn đơn vị tính"`
Line 312 — BBRefEgovCurrency: `searchTitle="Chọn loại tiền tệ"`

- [ ] **Step 3: UILoadingLocationSection**

Lines 32, 58 — BBRefBorderGate: `searchTitle="Chọn cửa khẩu/cảng"`

---

### Task 12: Goods Editors

**Files:**
- `declaration/goods/UIProductEditor.tsx`
- `declaration/goods/UIProductList.tsx`

- [ ] **Step 1: UIProductEditor (9 usages)**

Line 197 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`
Line 211 — BBRefTariffSchedule: `searchTitle="Chọn mã biểu thuế"`
Lines 263, 281, 335 — BBRefEgovUnit: `searchTitle="Chọn đơn vị tính"`
Lines 322, 357 — BBRefEgovCurrency: `searchTitle="Chọn loại tiền tệ"`
Line 514 — BBRefEgovTaxExemption: `searchTitle="Chọn miễn giảm thuế"`
Line 528 — BBRefEgovTaxExemptionCategory: `searchTitle="Chọn loại miễn giảm thuế"`

- [ ] **Step 2: UIProductList (4 usages)**

Line 172 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`
Lines 195, 218 — BBRefEgovUnit: `searchTitle="Chọn đơn vị tính"`
Line 241 — BBRefTariffSchedule: `searchTitle="Chọn mã biểu thuế"`

---

### Task 13: Reports

**Files:**
- `report/UIGoodsItemsReport.tsx`
- `report/user-activity/UIUserActivityReport.tsx`

- [ ] **Step 1: UIGoodsItemsReport (6 usages)**

Line 277 — BBRefPartnerCompany: `searchTitle="Chọn công ty đối tác"`
Line 286 — BBRefCustomsOffice: `searchTitle="Chọn cơ quan hải quan"`
Line 295 — BBRefBorderGate: `searchTitle="Chọn cửa khẩu/cảng"`
Line 304 — BBRefDeclarationType: `searchTitle="Chọn loại hình tờ khai"`
Lines 315, 324 — BBRefEgovCountry: `searchTitle="Chọn quốc gia"`

- [ ] **Step 2: UIUserActivityReport (1 usage)**

Line 221 — BBRefSyncSource: `searchTitle="Chọn nguồn đồng bộ"`

---

### Task 14: Account

**Files:**
- `account/UIAccountConfiguration.tsx`
- `account/UIPartnerCompanySelector.tsx`

- [ ] **Step 1: Add searchTitle**

UIAccountConfiguration line 361 — BBRefSyncSource: `searchTitle="Chọn nguồn đồng bộ"`
UIPartnerCompanySelector lines 202, 349 — BBRefAccountPartnerCompany: `searchTitle="Chọn công ty đối tác"`

---

### Task 15: Final Verification

- [ ] **Step 1: Build of1-core lib**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-core/webui/lib && pnpm build
```

- [ ] **Step 2: Build egov**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-egov/webui/egov && pnpm dev-build
```

- [ ] **Step 3: Grep verify — no BBRef caller without searchTitle**

```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-egov/webui/egov
grep -rn '<BBRef' src/module/egov/ | grep -v 'company/input/' | grep -v 'account/input/' | grep -v 'searchTitle'
```

Expected: No results.
