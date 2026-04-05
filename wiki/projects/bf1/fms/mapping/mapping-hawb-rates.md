# Mapping: of1_fms_hawb_rates

> BF1 -> FMS field mapping cho bảng `of1_fms_hawb_rates`
> CDC Handler: `SellingRateCDCHandler` (Debit), `BuyingRateCDCHandler` (Credit), `OtherChargeCDCHandler` (On_Behalf)
> Coverage: CDC-verified
> Note: CDC handlers ghi vào `HouseBillInvoice` + `HouseBillInvoiceItem` Java entities

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table (Debit) | BF1 Column (Debit) | BF1 Table (Credit) | BF1 Column (Credit) | BF1 Table (On_Behalf) | BF1 Column (On_Behalf) | BF1 UI Label |
|---|---|---|---|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | | | | | |
| `house_bill_id` | bigint | | FK → of1_fms_house_bill.id | | | | | | | |
| `charge_code` | varchar | | Mã loại phí | `SellingRate` | `FieldName` | `BuyingRateWithHBL` | `FieldName` | | | |
| `charge_name` | varchar | | Tên phí | `SellingRate` | `Description` | `BuyingRateWithHBL` | `Description` | `OtherChargeDetail` | `Description` | |
| `rate_type` | varchar | | Loại: Debit / Credit / On_Behalf | (hardcoded `Debit`) | | (hardcoded `Credit`) | | (hardcoded `On_Behalf`) | | |
| `quantity` | double | | Số lượng | `SellingRate` | `Quantity` | `BuyingRateWithHBL` | `Quantity` | `OtherChargeDetail` | `Quantity` | |
| `unit` | varchar | | Đơn vị tính phí | `SellingRate` | `QUnit` | `BuyingRateWithHBL` | `Unit` | `OtherChargeDetail` | `UnitQty` | |
| `unit_price` | double | | Đơn giá | `SellingRate` | `UnitPrice` | `BuyingRateWithHBL` | `UnitPrice` | | | |
| `total` | double | | Thành tiền (trước thuế) | `SellingRate` | `TotalValue` | `BuyingRateWithHBL` | `TotalValue` | `OtherChargeDetail` | `BFVATAmount` | |
| `total_tax` | double | | Thuế | `SellingRate` | `VAT` | `BuyingRateWithHBL` | `VAT` | `OtherChargeDetail` | `VAT` | |
| `final_charge` | double | | Thành tiền (sau thuế) | `SellingRate` | `Amount` | `BuyingRateWithHBL` | `Amount` | `OtherChargeDetail` | `Amount` | |
| `currency` | varchar | | Ngoại tệ | `SellingRate` | `Unit` | `BuyingRateWithHBL` | `Unit` | `OtherChargeDetail` | `Currency` | |
| `exchange_rate` | decimal(20,6) | | Tỷ giá quy đổi | `SellingRate` | `ExtRateVND` | `BuyingRateWithHBL` | `ExtRateVND` | | | |
| `domestic_currency` | varchar | | Loại nội tệ | (hardcoded `VND`) | | (hardcoded `VND`) | | | | |
| `domestic_total` | double | | Thành tiền nội tệ (trước thuế) | `SellingRate` | `ExtVND` | `BuyingRateWithHBL` | `ExtVND` | | | |
| `domestic_total_tax` | double | | Thuế nội tệ | | | | | | | |
| `domestic_final_charge` | double | | Thành tiền nội tệ (sau thuế) | | | | | | | |
| `payer_partner_id` | bigint | | FK — bên thanh toán | | | | | | | |
| `payer_label` | varchar | | Tên bên thanh toán (denormalized) | | | | | `OtherChargeDetail` | `PartnerID` | |
| `payee_partner_id` | bigint | | FK — bên thụ hưởng | | | | | | | |
| `payee_label` | varchar | | Tên bên thụ hưởng (denormalized) | `SellingRate` | `OBHPartnerID` | `BuyingRateWithHBL` | `OBHPartnerID` | | | |
| `reference_code` | varchar | | Mã tham chiếu | (derived `SR-{IDKeyIndex}`) | | (derived `BR-{IDKeyIndex}`) | | (derived `OC-{IDKeyIndex}`) | | |
