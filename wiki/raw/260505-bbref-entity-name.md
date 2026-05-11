# Spec: BBRefEntity popup title theo ECUS (#265)

**Date:** 2026-05-05
**Project:** of1-egov + of1-core
**Issue:** of1-egov/of1-egov#265

---

## Problem

Tất cả BBRef component khi click `...` mở popup đều hiện title chung **"Search Ref Entities"**.
User không biết popup đang dùng để chọn cái gì. UX kém + không match ECUS.

## Solution

1. **Sửa base class** `BBRefEntity.tsx` (of1-core): thêm 2 prop mới `searchTitle` và `infoTitle`
2. **Tại caller site** (of1-egov): truyền `searchTitle` với title tiếng Việt match ECUS

## Base Class Changes (of1-core)

File: `/Users/nqcdan/OF1/forgejo/of1-platform/of1-core/webui/lib/src/entity/BBRefEntity.tsx`

### Props interface — thêm 2 optional props:

```typescript
refEntityName?: string;
searchTitle?: string;   // NEW: custom title cho search popup
infoTitle?: string;     // NEW: custom title cho info popup
```

### Logic thay đổi (backward-compatible):

```typescript
// Line 588 (info popup)
let title = this.props.infoTitle || refEntityName || 'Ref Entity';

// Line 641 (search popup)
let searchTitle = this.props.searchTitle || (refEntityName ? `Search ${refEntityName}` : 'Search Ref Entities');

// Line 917 (multi-entity info)
let title = this.props.infoTitle || refEntityName || 'Ref Entity';
```

## Caller Site Changes (of1-egov)

Tại mỗi `<BBRefXxx .../>` trong `webui/egov/src/`, thêm prop `searchTitle="Chọn ..."`.

### Mapping Table (title tiếng Việt theo ECUS)

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
| BBRefSyncSource | "Chọn ngu��n đồng bộ" |
| BBRefPartnerCompany | "Chọn công ty đối tác" |
| BBRefAccountPartnerCompany | "Chọn công ty đối tác" |

> **Note:** Title chính thức cần verify với ECUS khi implement. Bảng trên là best-guess dựa trên label field tương ứng.

## Affected Files

### of1-core (1 file)
- `webui/lib/src/entity/BBRefEntity.tsx` — thêm props + sửa logic title

### of1-egov (19 files)
- `declaration/detail-screens/UIBasicInformationEntity.tsx`
- `declaration/detail-screens/TradingInvoiceEntity.tsx`
- `declaration/detail-screens/ImportExportXEntity.tsx`
- `declaration/detail-screens/ImportExportNEntity.tsx`
- `declaration/detail-screens/TaxAndGuaranteeEntity.tsx`
- `declaration/detail-screens/DeclarationLicenseEntity.tsx`
- `declaration/detail-screens/TransportDocumentEntity.tsx`
- `declaration/detail-screens/TransportInformationEntity.tsx`
- `declaration/detail-screens/ExportContainerEntity.tsx`
- `declaration/detail-screens/ValuationDeclarationEntity.tsx`
- `declaration/detail-screens/ola-screen/UIOLAInformationSection.tsx`
- `declaration/detail-screens/ola-screen/UIOLAGoodsInformationSection.tsx`
- `declaration/detail-screens/ola-screen/UILoadingLocationSection.tsx`
- `declaration/goods/UIProductEditor.tsx`
- `declaration/goods/UIProductList.tsx`
- `report/UIGoodsItemsReport.tsx`
- `report/user-activity/UIUserActivityReport.tsx`
- `account/UIAccountConfiguration.tsx`
- `account/UIPartnerCompanySelector.tsx`

## Out of Scope

- Không thêm `infoTitle` tại caller sites (chỉ thêm prop definition ở base class, để dùng sau nếu cần)
- Không i18n — dùng string literal trực tiếp (không wrap `T()`)
- Không thay đổi search/info popup logic ngoài title
