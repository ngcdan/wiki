# FE Input Validators cho Declaration Form — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply `MaxLengthValidator` và `EmptyValidator` chuẩn của `@of1-webui/lib` cho declaration form, thay thế validation thủ công trong `onPreCommit`.

**Architecture:** Thêm prop `validators` và `inputObserver` vào các `BB*Field` hiện có. Refactor `onPreCommit` từ if-else → `assertNoError()`. Không tạo file mới — chỉ sửa file hiện tại.

**Tech Stack:** React 18, `@of1-webui/lib` (util.validator), TypeScript/TSX

**Issue:** of1-egov/of1-egov#340

---

## Import Pattern

```tsx
// util đã được import sẵn trong hầu hết file
import { bs, entity, input, util } from '@of1-webui/lib';

// Sử dụng validator qua namespace
validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]}
validators={[new util.validator.EmptyValidator(T('Bắt buộc nhập'))]}
```

## File Map

| File | Action |
|------|--------|
| `detail-screens/ImportExportNEntity.tsx` | Add `inputObserver={observer}` + `validators` to 4 fields |
| `detail-screens/ImportExportXEntity.tsx` | Add `inputObserver={observer}` + `validators` to 5 fields |
| `detail-screens/OtherInformation.tsx` | Add `validators` to `internalReferenceNo` (already has inputObserver) |
| `goods/UIProductEditor.tsx` | Add `validators` to 3 BBStringField goods fields |
| `UIImportEditor.tsx` | Refactor `onPreCommit` |
| `UIExportEditor.tsx` | Refactor `onPreCommit` |
| `UIOLAEditor.tsx` | Refactor `onPreCommit` |

---

## Task 1: Add validators to ImportExportNEntity.tsx (Import screen)

**File:** `webui/egov/src/module/egov/declaration/detail-screens/ImportExportNEntity.tsx`

**Context:** File đã import `util` từ `@of1-webui/lib`. Observer có sẵn qua `this.props.observer`. Các field dùng `onInputChange={this.onModify}` — cần thêm `inputObserver={observer}` để validator hoạt động.

- [ ] **Step 1:** Thêm `inputObserver={observer}` và `validators` vào field `customerTaxCode` (line 132)

Before:
```tsx
<input.BBStringField label={T("Mã bưu chính")} bean={declaration} field={"customerTaxCode"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Mã bưu chính")} bean={declaration} field={"customerTaxCode"}
  inputObserver={observer} onInputChange={this.onModify}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 2:** Thêm validators cho `delegatorCode` (line 84) — field này `disable` nên chỉ thêm maxLength phòng trường hợp data từ lookup vượt limit

Before:
```tsx
<input.BBStringField label={T("Mã người uỷ thác nhập khẩu")} bean={declaration}
  field={"delegatorCode"} onInputChange={this.onModify} disable />
```

After:
```tsx
<input.BBStringField label={T("Mã người uỷ thác nhập khẩu")} bean={declaration}
  field={"delegatorCode"} onInputChange={this.onModify} disable
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 3:** Thêm validators cho `exportPrincipalName` (line 150)

Before:
```tsx
<input.BBStringField label={T("Người uỷ thác xuất khẩu")} bean={declaration}
  field={"exportPrincipalName"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Người uỷ thác xuất khẩu")} bean={declaration}
  field={"exportPrincipalName"} onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(70, T('Tối đa 70 ký tự'))]} />
```

- [ ] **Step 4:** Thêm validators cho `customsDeclarantCode` (line 154)

Before:
```tsx
<input.BBStringField label={T("Mã người khai Hải quan")} bean={declaration}
  field={"customsDeclarantCode"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Mã người khai Hải quan")} bean={declaration}
  field={"customsDeclarantCode"} onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 5:** Commit

```bash
git add webui/egov/src/module/egov/declaration/detail-screens/ImportExportNEntity.tsx
git commit -m "feat(egov): add MaxLengthValidator to ImportExportNEntity fields"
```

---

## Task 2: Add validators to ImportExportXEntity.tsx (Export screen)

**File:** `webui/egov/src/module/egov/declaration/detail-screens/ImportExportXEntity.tsx`

**Context:** Tương tự N nhưng có thêm `delegatorName`. File đã import `util`.

- [ ] **Step 1:** Thêm validators cho `delegatorCode` (line 82)

Before:
```tsx
<input.BBStringField label={T("Mã người ủy thác xuất khẩu")} bean={declaration}
  field={"delegatorCode"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Mã người ủy thác xuất khẩu")} bean={declaration}
  field={"delegatorCode"} onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 2:** Thêm validators cho `delegatorName` (line 86)

Before:
```tsx
<input.BBStringField label={T("Tên người ủy thác xuất khẩu")} bean={declaration}
  field={"delegatorName"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Tên người ủy thác xuất khẩu")} bean={declaration}
  field={"delegatorName"} onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(300, T('Tối đa 300 ký tự'))]} />
```

- [ ] **Step 3:** Thêm validators cho `customerTaxCode` (line 115)

Before:
```tsx
<input.BBStringField label={T("Mã bưu chính")} bean={declaration} field={"customerTaxCode"}
  onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Mã bưu chính")} bean={declaration} field={"customerTaxCode"}
  onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 4:** Thêm validators cho `customsDeclarantCode` (line 135)

Before:
```tsx
<input.BBStringField label={T("Mã người khai Hải quan")} bean={declaration}
  field={"customsDeclarantCode"} onInputChange={this.onModify} />
```

After:
```tsx
<input.BBStringField label={T("Mã người khai Hải quan")} bean={declaration}
  field={"customsDeclarantCode"} onInputChange={this.onModify}
  inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]} />
```

- [ ] **Step 5:** Commit

```bash
git add webui/egov/src/module/egov/declaration/detail-screens/ImportExportXEntity.tsx
git commit -m "feat(egov): add MaxLengthValidator to ImportExportXEntity fields"
```

---

## Task 3: Add validators to OtherInformation.tsx

**File:** `webui/egov/src/module/egov/declaration/detail-screens/OtherInformation.tsx`

**Context:** File đã có `inputObserver={observer}` trên field. Cần thêm `util` vào import và thêm validators prop.

- [ ] **Step 1:** Thêm `util` vào import (line 2)

Before:
```tsx
import {bs, entity, input} from '@of1-webui/lib';
```

After:
```tsx
import {bs, entity, input, util} from '@of1-webui/lib';
```

- [ ] **Step 2:** Thêm validators cho `internalReferenceNo` (line 21-27)

Before:
```tsx
<input.BBStringField
  label={T("Số tham chiếu nội bộ doanh nghiệp")}
  bean={declaration}
  field="internalReferenceNo"
  inputObserver={observer}
  placeholder={T("Nhập số tham chiếu nội bộ")}
/>
```

After:
```tsx
<input.BBStringField
  label={T("Số tham chiếu nội bộ doanh nghiệp")}
  bean={declaration}
  field="internalReferenceNo"
  inputObserver={observer}
  placeholder={T("Nhập số tham chiếu nội bộ")}
  validators={[new util.validator.MaxLengthValidator(50, T('Tối đa 50 ký tự'))]}
/>
```

- [ ] **Step 3:** Commit

```bash
git add webui/egov/src/module/egov/declaration/detail-screens/OtherInformation.tsx
git commit -m "feat(egov): add MaxLengthValidator to OtherInformation.internalReferenceNo"
```

---

## Task 4: Add validators to UIProductEditor.tsx (Goods fields)

**File:** `webui/egov/src/module/egov/declaration/goods/UIProductEditor.tsx`

**Context:** File đã import `util` (có `bs, entity, input`) và tất cả field đ�� có `inputObserver={observer}`. Chỉ thêm `validators` prop. Chỉ áp dụng cho 3 field là `BBStringField` — các field còn lại là `BBRef*` (country, unit, currency) nên maxLength được kiểm soát bởi data từ ref lookup.

- [ ] **Step 1:** Thêm `util` vào import nếu chưa có, kiểm tra import line

- [ ] **Step 2:** Thêm validators cho `itemCode` (line ~163)

Before:
```tsx
<input.BBStringField field="itemCode" label={T("Mã hàng hoá")} disable={!writeCap} inputObserver={observer} />
```

After:
```tsx
<input.BBStringField field="itemCode" label={T("Mã hàng hoá")} disable={!writeCap} inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(100, T('Tối đa 100 ký tự'))]} />
```

- [ ] **Step 3:** Thêm validators cho `itemDescription` (line ~174)

Before:
```tsx
<input.BBStringField field="itemDescription" label={T("Mô tả hàng hoá")} disable={!writeCap} inputObserver={observer} />
```

After:
```tsx
<input.BBStringField field="itemDescription" label={T("Mô tả hàng hoá")} disable={!writeCap} inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(600, T('Tối đa 600 ký tự'))]} />
```

- [ ] **Step 4:** Thêm validators cho `hsCode` (line ~182)

Before:
```tsx
<input.BBStringField field="hsCode" label={T("Mã HS")} disable={!writeCap} inputObserver={observer} />
```

After:
```tsx
<input.BBStringField field="hsCode" label={T("Mã HS")} disable={!writeCap} inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(12, T('Tối đa 12 ký tự'))]} />
```

- [ ] **Step 5:** Thêm validators cho `importDutyExemptionCode` (line ~419)

Before:
```tsx
<input.BBStringField field="importDutyExemptionCode" label={T("Mã miễn/giảm/không chịu thuế nhập khẩu")} disable={!writeCap} inputObserver={observer} />
```

After:
```tsx
<input.BBStringField field="importDutyExemptionCode" label={T("Mã miễn/giảm/không chịu thuế nhập khẩu")} disable={!writeCap} inputObserver={observer}
  validators={[new util.validator.MaxLengthValidator(5, T('Tối đa 5 ký tự'))]} />
```

- [ ] **Step 6:** Commit

```bash
git add webui/egov/src/module/egov/declaration/goods/UIProductEditor.tsx
git commit -m "feat(egov): add MaxLengthValidator to goods item fields"
```

**Note:** Các field `originCountry` (max 2), `quantityUnitCode` (max 4), `secondQuantityUnitCode` (max 4), `invoiceUnitPriceCurrencyCode` (max 3), `invoiceUnitPriceUnitCode` (max 4) là **BBRef* components** — giá trị được chọn từ dropdown/lookup nên luôn đúng format. Không cần thêm MaxLengthValidator cho BBRef*.

---

## Task 5: Refactor onPreCommit — UIImportEditor.tsx

**File:** `webui/egov/src/module/egov/declaration/UIImportEditor.tsx`

**Context:** Hiện tại `onPreCommit` (line 220-254) dùng if-else check `missingFields` + `bs.dialogShow`. Thay bằng `assertNoError()`. Required validation đã được handle bởi `required` prop trên các BBRef* field tương ứng + `EmptyValidator` trên free-text field.

- [ ] **Step 1:** Thêm `EmptyValidator` vào field `customerName` trong `ImportExportNEntity.tsx` — field này dùng `BBRefTradingOrganization` với `required` prop đã có (line 114) → **Không cần thêm gì**, `required` trên BBRef đã handle.

- [ ] **Step 2:** Thêm `EmptyValidator` vào `customerAddress` trong `ImportExportNEntity.tsx` (line 135-136) — field đã có `required` prop → lib tự handle khi có `inputObserver`. Thêm `inputObserver={observer}`:

Before:
```tsx
<input.BBTextField bean={declaration}
  style={{ height: '3rem' }} field={"customerAddress"} required onInputChange={this.onModify} />
```

After:
```tsx
<input.BBTextField bean={declaration}
  style={{ height: '3rem' }} field={"customerAddress"} required onInputChange={this.onModify}
  inputObserver={observer} />
```

- [ ] **Step 3:** Refactor `onPreCommit` trong `UIImportEditor.tsx` (line 220-254)

Before:
```tsx
onPreCommit = (observer: entity.IBeanObserver) => {
  let declaration = observer.getMutableBean();
  let missingFields: string[] = [];

  if (!declaration.groupDeclarationType || declaration.groupDeclarationType.trim() === '') {
    missingFields.push(T('Nhóm loại hình'));
  }
  if (!declaration.declarationTypeId) {
    missingFields.push(T('Mã loại hình'));
  }
  if (!declaration.customsOfficeId) {
    missingFields.push(T('Cơ quan hải quan'));
  }
  if (!declaration.customerName || declaration.customerName.trim() === '') {
    missingFields.push(T('Tên người xuất khẩu'));
  }
  if (!declaration.customerAddress || declaration.customerAddress.trim() === '') {
    missingFields.push(T('Địa chỉ người xuất khẩu'));
  }

  if (missingFields.length > 0) {
    bs.dialogShow(T('Thông tin thiếu'),
      <div className="text-danger fw-bold text-center py-3 border-bottom">
        <FeatherIcon.AlertCircle className="mx-2" />
        {T('Vui lòng nhập')}: {missingFields.join(', ')}
      </div>,
      { backdrop: 'static', size: 'sm' }
    );
    throw new Error(`${T('Vui lòng nhập')}: ${missingFields.join(', ')}`);
  }
}
```

After:
```tsx
onPreCommit = (observer: entity.IBeanObserver) => {
  let declaration = observer.getMutableBean();

  // Manual checks for fields without inputObserver (BBRef/Radio fields)
  let missingFields: string[] = [];
  if (!declaration.groupDeclarationType || declaration.groupDeclarationType.trim() === '') {
    missingFields.push(T('Nhóm loại hình'));
  }
  if (!declaration.declarationTypeId) {
    missingFields.push(T('Mã loại hình'));
  }
  if (!declaration.customsOfficeId) {
    missingFields.push(T('Cơ quan hải quan'));
  }

  if (missingFields.length > 0) {
    let errorCollector = observer.getErrorCollector();
    missingFields.forEach(f => errorCollector.collect(f, new Error(T('Bắt buộc nhập'))));
  }

  observer.getErrorCollector().assertNoError(T('Lỗi nhập liệu'));
}
```

**Giải thích:** `groupDeclarationType` là radio button, `declarationTypeId` và `customsOfficeId` là BBRef field — 3 field này không dùng `inputObserver` flow nên cần check thủ công và collect error vào ErrorCollector. `customerName` và `customerAddress` giờ được validate real-time qua `required` + `inputObserver` trên các field tương ứng.

- [ ] **Step 4:** Xóa import `FeatherIcon` nếu không còn dùng ở chỗ khác trong file (kiểm tra trước khi xóa)

- [ ] **Step 5:** Commit

```bash
git add webui/egov/src/module/egov/declaration/UIImportEditor.tsx
git add webui/egov/src/module/egov/declaration/detail-screens/ImportExportNEntity.tsx
git commit -m "refactor(egov): migrate UIImportEditor onPreCommit to ErrorCollector pattern"
```

---

## Task 6: Refactor onPreCommit — UIExportEditor.tsx

**File:** `webui/egov/src/module/egov/declaration/UIExportEditor.tsx`

- [ ] **Step 1:** Thêm `inputObserver={observer}` vào `customerAddress` field trong `ImportExportXEntity.tsx` (line 71-73) — field đã có `required`:

Before:
```tsx
<input.BBTextField required
  style={{ height: '3rem' }} bean={declarationTradingOrganization} field={"address"}
  onInputChange={this.onModifyOrg} />
```

After:
```tsx
<input.BBTextField required
  style={{ height: '3rem' }} bean={declarationTradingOrganization} field={"address"}
  onInputChange={this.onModifyOrg} inputObserver={observer} />
```

- [ ] **Step 2:** Refactor `onPreCommit` trong `UIExportEditor.tsx` (line 233-270)

After:
```tsx
onPreCommit = (observer: entity.IBeanObserver) => {
  let declaration = observer.getMutableBean();
  this.normalizeGoodsDeclaration(declaration);

  // Manual checks for fields without inputObserver (BBRef/Radio fields)
  let missingFields: string[] = [];
  if (!declaration.groupDeclarationType || declaration.groupDeclarationType.trim() === '') {
    missingFields.push(T('Nhóm loại hình'));
  }
  if (!declaration.declarationTypeId) {
    missingFields.push(T('Mã loại hình'));
  }
  if (!declaration.customsOfficeId) {
    missingFields.push(T('Cơ quan hải quan'));
  }

  if (missingFields.length > 0) {
    let errorCollector = observer.getErrorCollector();
    missingFields.forEach(f => errorCollector.collect(f, new Error(T('Bắt buộc nhập'))));
  }

  observer.getErrorCollector().assertNoError(T('Lỗi nhập liệu'));
}
```

**Note:** Giữ `this.normalizeGoodsDeclaration(declaration)` — đây là business logic normalize, không phải validation. `exporterName` và `address` giờ được validate real-time qua `required` + `inputObserver` trên BBRef/TextField.

- [ ] **Step 3:** Commit

```bash
git add webui/egov/src/module/egov/declaration/UIExportEditor.tsx
git add webui/egov/src/module/egov/declaration/detail-screens/ImportExportXEntity.tsx
git commit -m "refactor(egov): migrate UIExportEditor onPreCommit to ErrorCollector pattern"
```

---

## Task 7: Refactor onPreCommit — UIOLAEditor.tsx

**File:** `webui/egov/src/module/egov/declaration/UIOLAEditor.tsx`

- [ ] **Step 1:** Refactor `onPreCommit` (line 18-38)

After:
```tsx
onPreCommit = (observer: entity.IBeanObserver) => {
  let declaration = observer.getMutableBean();

  let missingFields: string[] = [];
  if (!declaration.declarationType || !declaration.declarationType.id) {
    missingFields.push(T('Mã loại hình'));
  }
  if (!declaration.customsOffice || !declaration.customsOffice.id) {
    missingFields.push(T('Cơ quan hải quan'));
  }

  if (missingFields.length > 0) {
    let errorCollector = observer.getErrorCollector();
    missingFields.forEach(f => errorCollector.collect(f, new Error(T('Bắt buộc nhập'))));
  }

  observer.getErrorCollector().assertNoError(T('Lỗi nhập liệu'));
}
```

- [ ] **Step 2:** Xóa import `FeatherIcon` nếu không còn dùng ở chỗ khác

- [ ] **Step 3:** Commit

```bash
git add webui/egov/src/module/egov/declaration/UIOLAEditor.tsx
git commit -m "refactor(egov): migrate UIOLAEditor onPreCommit to ErrorCollector pattern"
```

---

## Task 8: Verify build

- [ ] **Step 1:** Run build

```bash
cd webui/egov && pnpm build
```

Expected: Build success, no TypeScript errors.

- [ ] **Step 2:** Fix any errors nếu có

- [ ] **Step 3:** Final commit nếu có fix

---

## Notes

### Không thêm validator cho các field sau (lý do):
- **BBRef* components** (BBRefDeclarationType, BBRefCustomsOffice, BBRefEgovCountry, BBRefEgovUnit, BBRefEgovCurrency) — giá trị chọn từ dropdown/lookup, luôn đúng format
- **Radio/Select fields** (groupDeclarationType) — options cố định
- **Disabled fields** mà data auto-fill từ BBRef lookup — vẫn thêm MaxLength phòng trường hợp data source vượt limit

### assertNoError behavior:
- Lib `assertNoError(title)` tự động show modal liệt kê TẤT CẢ lỗi (từ validator inline + lỗi collect thủ công)
- Throw error → chặn save
- User thấy 1 modal duy nhất thay vì dialog custom

### Backward compatibility:
- `required` prop trên BBRef* vẫn hoạt động như cũ
- `onInputChange={this.onModify}` vẫn hoạt động song song với `inputObserver`
- Thêm `inputObserver` không break behavior hiện tại, chỉ bật thêm error collection
