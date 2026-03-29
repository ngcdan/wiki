# BEE_DB — Khảo sát Schema & Cấu trúc Bảng

## Tổng quan

- **461 bảng** tổng cộng (~200 bảng có data thực tế)
- Bảng lớn nhất: `EInvoice_History` (11.7 GB), `DebitNoteDetails` (7.5 GB), `ProfitShares` (5.6 GB)

---

## Phân nhóm bảng

### Nhóm 1 — Partner / Khách hàng (Master)

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Partners` | 52,414 | 82 | Master đối tác/khách hàng (PK: `PartnerID` nvarchar) |
| `PartnerContact` | 25,009 | 22 | Người liên hệ của partner |
| `Partner_BankInfo` | 14,449 | 2.6 | Thông tin ngân hàng cá nhân |
| `Partner_BankInfo_Comp` | 8 | 0.07 | Thông tin ngân hàng theo công ty |
| `Partner_Bank_Default` | 12 | 0.07 | Ngân hàng mặc định |
| `Partner_Bank_Request` | 1,749 | 0.95 | Yêu cầu đổi ngân hàng |
| `Partner_History` | 16,485,161 | 3,561 | Lịch sử thay đổi partner |
| `Partner_Payment_Bank` | 866,196 | 722 | Thanh toán qua ngân hàng |
| `Partner_Payment_Plan` | 24,023 | 22 | Kế hoạch thanh toán |
| `Partner_Warning` | 61,832 | 120 | Cảnh báo đối tác |
| `Partner_Warining_Details` | 6,872,900 | 1,870 | Chi tiết cảnh báo |
| `Partner_Notes` | 956 | 14 | Ghi chú đối tác |
| `Partner_More_Revenue` | 1,295 | 0.2 | Doanh thu bổ sung |
| `Partner_Source` | 31 | 0.07 | Nguồn đối tác |
| `Partner_Transaction_Allow` | 15,060 | 3.6 | Phân quyền giao dịch |
| `Partner_Tariff` | 46 | 0.14 | Tariff riêng theo partner |
| `Partner_Tariff_SellingRate` | 46 | 0.14 | Giá bán theo tariff |
| `Partner_Tariff_BuyingRate` | 46 | 0.02 | Giá mua theo tariff |
| `Partner_Tariff_ProfitShares` | 45 | 0.14 | Chia lợi nhuận theo tariff |
| `PartnerIDMaker` | 7 | 0.14 | Tạo mã đối tác |
| `PartnerTransactions` | 10 | 0.07 | Giao dịch đối tác |

**FK từ Partners ra ngoài:** `Partners.PartnerID` được tham chiếu bởi:
`DebitNotes`, `DebitNoteDetails_Other`, `TransactionDetails` (ShipperID), `InvoiceReference` (ShipperID), `BookingRateRequest`, `HandleInstructions`, `HandleServiceRate`, `PODetail` (VendorCode), `ProfitShares`, `Partner_BankInfo`, `Partner_BankInfo_Comp`

---

### Nhóm 2 — Transactions / Lô hàng

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Transactions` | 681,038 | 1,476 | Master lô hàng (PK: `TransID` dạng `BIHCM008238/25`) |
| `TransactionDetails` | 831,608 | 1,982 | Chi tiết lô hàng (FK: `TransID`, `HWBNO`, `ShipperID`) |
| `TransactionInfo` | 508,008 | 292 | Thông tin bổ sung per shipment |
| `TransactionInfoDetail` | 0 | — | Chưa dùng |
| `TransactionsChange` | 1,411,298 | 353 | Lịch sử thay đổi lô hàng |
| `TransactionsChangeHis` | 63 | 0.07 | Lưu trữ lịch sử thay đổi |
| `Transaction_Notes` | 45,824 | 10 | Ghi chú lô hàng |
| `Transaction_Ops` | 22,810 | 4.9 | Thao tác vận hành |
| `Transaction_Task` | 399,773 | 140 | Task gắn với lô hàng |
| `Transaction_Task_Group` | 41 | 0.07 | Nhóm task |
| `Transaction_Service_Task` | 178 | 0.15 | Task dịch vụ |
| `TransactionType` | 17 | 0.21 | Loại giao dịch |
| `TransactionTypeDetail` | 92 | 0.21 | Chi tiết loại |
| `TransactionReminder` | 8 | 0.07 | Nhắc nhở |
| `TransactionLead` | 86 | 0.13 | Lead giao dịch |

**FK từ Transactions:** `Transactions.TransID` → `AdvanceSettlementPayment`, `BookingLocal`, `BuyingRate`, `BuyingRateFixCost`, `BuyingRateOthers`, `ConsolidationRate`, `ContainerLoaded`, `InvoiceReference`, `OPSManagement`, `ProfitShareCalc`, `ShippingInstruction`, `TransactionDetails`

---

### Nhóm 3 — HAWB / House Bill of Lading

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `HAWB` | 866,657 | 2,773 | House Bill (PK: `HWBNO`; ref: `TRANSID`, `AWBNO`) |
| `HAWBDETAILS` | 369,773 | 451 | Chi tiết hàng hóa trên HBL |
| `HAWBRATE` | 87,694 | 18 | Giá theo vận đơn |
| `HAWBTracking` | 96,599 | 66 | Tracking trạng thái vận chuyển |
| `HAWBSEPDetails` | 0 | — | Tách lô |
| `HAWBTranshipment` | 0 | — | Transshipment |
| `HAWB_Air_Tracking` | 41 | 0.07 | Tracking hàng không |
| `HAWB_DELETE` | 755,954 | 30 | Vận đơn đã xóa (audit) |
| `HAWB_FMC` | 6 | 0.07 | FMC info |
| `HAWB_Partner_Address` | 5,191 | 4.8 | Địa chỉ đối tác trên HBL |
| `ContainerListOnHBL` | 141,216 | 67 | Container gắn với HBL |
| `ContainerLoadedHBL` | 75,514 | 31 | Container đã load lên HBL |

**FK từ HAWB.HWBNO →** (20+ bảng): `SellingRate`, `BuyingRateWithHBL`, `ProfitShares`, `ProfitSharesCost`, `RevenueDetails_Sheet`, `TransactionDetails`, `TransactionInfo`, `OtherChargeDetail`, `ContainerListOnHBL`, `ContainerLoadedHBL`, `HAWBTracking`, `HAWBDETAILS`, `HAWBRATE`, `BookingLocal`, `AdvanceSettlementPayment`, `CargoOperationRequest`, `AMSDeclaration`, `AcsInstallPayment`, ...

---

### Nhóm 4 — Rates / Bảng giá

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `SellingRate` | 1,942,592 | 3,537 | Giá bán (theo HAWBNO) |
| `SellingRate_Temp` | 822 | 0.38 | Tạm thời |
| `SellingRate_Partner_Disable` | 235 | 0.2 | Bị tắt theo partner |
| `SellingRate_Saleman_Disable` | 1 | 0.07 | Bị tắt theo saleman |
| `BuyingRateWithHBL` | 433,281 | 921 | Giá mua (theo HAWBNO) |
| `BuyingRate` | 5,177 | 8.2 | Giá mua (theo TransID) |
| `BuyingRateOthers` | 4,133 | 7.2 | Phí mua khác |
| `BuyingRateInland` | 2 | 0.37 | Giá nội địa |
| `BuyingRateFixCost` | 0 | — | Chi phí cố định |
| `RateHistory` | 6,448,501 | 4,863 | Lịch sử tất cả rates |
| `ArrivalFreightCharges` | 1,158,503 | 288 | Phí arrival |
| `ArrivalFreightChargesDefault` | 47 | 0.08 | Mặc định phí arrival |
| `SeaFreightPricing` | 55,590 | 102 | Bảng giá sea FCL export |
| `SeaFreightPricing_Exp` | 8,076 | 3.4 | Bảng giá sea FCL express |
| `SeaFreightPricingLCL` | 800 | 0.45 | Bảng giá sea LCL |
| `SeaFreightPricingLCL_Exp` | 1,892 | 1.5 | Bảng giá sea LCL express |
| `Seafclpricingimpstd` | 13,508 | 5.6 | FCL import std |
| `Sealclpricingimpstd` | 602 | 0.55 | LCL import std |
| `Sealclpricingexpstd` | 1,020 | 0.72 | LCL export std |
| `AirfreightPrcing` | 3,191 | 2.5 | Bảng giá air |
| `AirFreightPricing_Exp` | 1,454 | 0.86 | Bảng giá air express |
| `AirfreightPrcingDetail` | 0 | — | Chi tiết giá air |
| `Airpricingstd` | 350 | 0.27 | Air pricing std |
| `AirPortPerKGSChargeable` | 2 | 0.07 | Air per KG |
| `TruckingFCLPricing` | 742 | 0.34 | Giá trucking FCL |
| `TruckingLCLPricing` | 1,688 | 0.70 | Giá trucking LCL |
| `ATruckingFee` | 2,306 | 1.0 | Phí trucking |
| `HandleServiceRate` | 45 | 0.65 | Giá dịch vụ xử lý |
| `ConsolidationRate` | 0 | — | Giá consolidation |
| `OtherChargeList` | 26,123 | 30 | Danh mục phí khác |
| `OtherChargeDetail` | 246,546 | 151 | Chi tiết phí khác |
| `NameFeeDescription` | 1,130 | 0.94 | Mô tả tên phí |

---

### Nhóm 5 — Debit Notes / Công nợ

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `DebitNotes` | 309,724 | 316 | Phiếu công nợ (PK: `dbtID`) |
| `DebitNoteDetails` | 4,141,341 | 7,487 | Chi tiết công nợ (FK: `dbtID`) |
| `DebitNoteDetails_Payment` | 3,820,487 | 1,303 | Thanh toán chi tiết (FK: `dbtDID`) |
| `DebitNotes_Payment` | 318,685 | 54 | Thanh toán tổng (FK: `dbtID`) |
| `DebitNotes_Other` | 27 | 0.64 | Công nợ khác |
| `DebitNoteDetails_Other` | 4 | 0.29 | Chi tiết công nợ khác |
| `DebitNote_Payment_Bank` | 0 | — | Thanh toán qua ngân hàng |
| `DebitMemory` | 0 | — | Bộ nhớ debit |

**FK chain:** `DebitNotes.dbtID` → `DebitNoteDetails.dbtID` → `DebitNoteDetails_Payment.dbtDID`

---

### Nhóm 6 — VAT Invoice / Hóa đơn

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `VATInvoice` | 465,478 | 1,409 | Hóa đơn VAT (PK: `ID`+`InvoiceNo`) |
| `VATInvoiceDetail` | 2,289,816 | 1,112 | Chi tiết hóa đơn (FK: `ID`, `InvoiceNo`) |
| `VATINvoice_2019` | 167,012 | 488 | Archive 2019 |
| `VATInvoiceDetail_2019` | 791,413 | 235 | Chi tiết archive 2019 |
| `VATInvoice_Costing_Ref` | 1,947,737 | 830 | Tham chiếu costing |
| `VATInvoice_Costing_Import_Info` | 1,006,608 | 420 | Thông tin import costing |
| `VATInvoice_Editing_Info` | 423 | 0.62 | Lịch sử chỉnh sửa |
| `VATInvoice_Transactions` | 51 | 0.26 | HĐ liên kết giao dịch |
| `VATInvoice_Temp` | 0 | — | Tạm thời |
| `VATInvSOA` | 1 | 0.07 | SOA |
| `VATInvoiceLog` | 0 | — | Log |
| `EInvoice_History` | 941,165 | 11,756 | Lịch sử hóa đơn điện tử |
| `EInvoice_Register` | 49 | 1.05 | Đăng ký phát hành hóa đơn điện tử |
| `EInvoice_Register_Detail` | 122 | 0.07 | Chi tiết đăng ký |
| `InvoiceForm` | 64 | 0.30 | Mẫu hóa đơn |
| `InvoiceFormReserve` | 722 | 0.44 | Dự trữ số hóa đơn |
| `InvoiceDocument` | 2,435 | 923 | File đính kèm hóa đơn (lớn) |

**FK:** `VATInvoice.ID` → `VATInvoiceDetail.ID` và `VATInvoice.InvoiceNo` → `VATInvoiceDetail.InvoiceNo`

---

### Nhóm 7 — Invoice Reference / SOA

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `InvoiceReference` | 137,154 | 151 | Tham chiếu HĐ ↔ lô hàng (FK: `TransID`, `ShipperID`) |
| `InvoiceReferenceDetail` | 137,286 | 41 | Chi tiết (FK: `InvoiceNo`) |
| `InvoiceRefGrouping` | 28 | 0.16 | Nhóm tham chiếu |
| `InvoiceSOA` | 11,625 | 10 | Statement of Account (PK: `SOANO`) |
| `InvoiceBankInfo` | 9 | 0.14 | Thông tin ngân hàng trên HĐ |

**FK:** `InvoiceSOA.SOANO` → `InvoiceReference.SOANO`

---

### Nhóm 8 — Profit & Revenue

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `ProfitShares` | 3,167,966 | 5,565 | Chia lợi nhuận (theo HAWBNO + PartnerID) |
| `ProfitShareCalc` | 2 | 0.07 | Tính toán lợi nhuận |
| `ProfitShareCalcDetail` | 95 | 0.2 | Chi tiết tính toán |
| `ProfitSharesCost` | 0 | — | Chi phí chia lợi nhuận |
| `ProfitSharesRef_In_Local_Office` | 22 | 0.2 | Tham chiếu văn phòng nội bộ |
| `Revenue_Sheet` | 5,781 | 6.3 | Tổng hợp doanh thu (PK: `DocID`) |
| `RevenueDetails_Sheet` | 4,596,253 | 2,105 | Chi tiết doanh thu (FK: `DocRefID`) |

**FK:** `Revenue_Sheet.DocID` → `RevenueDetails_Sheet.DocRefID`

---

### Nhóm 9 — Kế toán (PhieuThuChi & Advance)

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `PhieuThuChi` | 120,491 | 224 | Phiếu thu/chi (PK: `Maso`) |
| `PhieuThuChiDetails` | 592,650 | 395 | Chi tiết (FK: `SoCT`) |
| `PhieuThuChiDetail` | 25,701 | 7.7 | Chi tiết phụ |
| `PhieuThuChiTaxReport` | 9 | 0.07 | Báo cáo thuế |
| `PhieuThuChiPL` | 14 | 0.09 | P&L |
| `AdvanceSettlementPayment` | 1,040,101 | 439 | Thanh toán tạm ứng |
| `AdvanceSettlementPayment_Office_OBH` | 40,960 | 71 | Tạm ứng văn phòng OBH |
| `AdvanceSettlementPayment_Deleted` | 6,602 | 7.3 | Đã xóa |
| `AdvancePaymentRequest` | 10,035 | 41 | Yêu cầu tạm ứng |
| `AdvancePaymentRequestDetails` | 3,376 | 1.05 | Chi tiết yêu cầu |
| `AdvanceRequest` | 63 | 0.44 | Yêu cầu ứng tiền |
| `AcsSetlementPayment` | 83,589 | 230 | Quyết toán kế toán |

**FK:** `PhieuThuChi.Maso` → `PhieuThuChiDetails.SoCT`, `PhieuThuChiDetail.MasoPhieu`, `PhieuThuChiTaxReport.RefNo`

---

### Nhóm 10 — Quotation / Báo giá

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `QUOTATIONS` | 17,803 | 46 | Báo giá air |
| `QUOTATIONDETAILS` | 24,533 | 20 | Chi tiết báo giá air |
| `QUOTATIONDETAILSOTS` | 335 | 0.2 | Chi tiết OTS |
| `QuotationFreightDetail` | 20,660 | 7.2 | Chi tiết freight |
| `SeaQuotations` | 47,878 | 169 | Báo giá sea |
| `SeaQuotationDetails` | 200,075 | 78 | Chi tiết báo giá sea |
| `SeaQuotationCtnrs` | 60,675 | 20 | Container trong báo giá |
| `SeaQuotationOthers` | 2,181 | 1.3 | Phí khác trong báo giá |
| `QuoSentHistory` | 92,924 | 20 | Lịch sử gửi báo giá |
| `BookingRateRequest` | 151,646 | 90 | Yêu cầu báo giá (FK: `BkgID`, `PartnerID`) |
| `Quotation_Combine` | 124 | 0.52 | Báo giá tổng hợp |
| `Quotation_Combine_Air` | 10 | 0.07 | Air |
| `Quotation_Combine_Sea` | 126 | 0.2 | Sea |
| `Quotation_Combine_Truck_FCL` | 9 | 0.07 | Truck FCL |
| `Quotation_Combine_Truck_LCL` | 4 | 0.07 | Truck LCL |
| `Quotation_Combine_Air_Charges` | 16 | 0.07 | Phí air trong combined |
| `Quotation_Combine_Sea_Charge` | 206 | 0.2 | Phí sea trong combined |
| `Quotation_Setting` | 18 | 0.14 | Cấu hình báo giá |

---

### Nhóm 11 — Booking

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `BookingLocal` | 41,481 | 97 | Booking nội địa (FK: `BkgID`, `ConfirmHBL`, `ConformJobNo`) |
| `BookingContainer` | 36,291 | 10 | Container trong booking |
| `BookingConfirmList` | 11,721 | 49 | Danh sách xác nhận |
| `SeaBookingNote` | 38,286 | 282 | Booking sea (FK: `BookingID` → `TransactionDetails`) |
| `SeaBookingContainer` | 33 | 0.14 | Container sea |
| `ShippingInstruction` | 235,879 | 118 | Hướng dẫn vận chuyển (FK: `TransID`) |

---

### Nhóm 12 — Warehouse / Kho

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Warehouse` | 88,947 | 68 | Kho hàng |
| `WarehouseDetail` | 183,114 | 59 | Chi tiết kho |
| `Warehouse_Payment` | 84,913 | 74 | Thanh toán kho |
| `Warehouse_Assign_Group` | 125 | 0.07 | Phân nhóm kho |

---

### Nhóm 13 — Hải quan / Customs

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `CustomsDeclaration` | 790,556 | 559 | Tờ khai hải quan (PK: `MasoTK`) |
| `CustomsDeclarationDetail` | 1 | 0.16 | Chi tiết tờ khai |
| `CustomsAssignedList` | 2,039 | 1.05 | Phân công hải quan |
| `CustomsArisingList` | 272 | 0.14 | Danh sách phát sinh |
| `CustomsArising_Assign_Group` | 274 | 0.07 | Phân nhóm phát sinh |
| `CustomsList` | 264 | 0.13 | Danh mục hải quan |
| `Customs_Bonded_Warehouse` | 15,927 | 2.1 | Kho ngoại quan |
| `Customs_Clearance_Tariff` | 2,281 | 1.06 | Biểu thuế thông quan |
| `EcusCuakhau` | 282 | 0.2 | Cửa khẩu ECUS |
| `ECusCucHQ` | 53 | 0.07 | Cục hải quan ECUS |

**FK:** `CustomsDeclaration.MasoTK` → `TransactionDetails.CustomsID`

---

### Nhóm 14 — Trucking

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `Trucking_Track` | 114,938 | 51 | Tracking xe tải |
| `Trucking_Pricing_Localnote` | 6 | 0.14 | Ghi chú giá trucking |

---

### Nhóm 15 — Người dùng / Phân quyền

| Bảng | Rows | Size (MB) | Mô tả |
|---|---|---|---|
| `UserInfos` | 1,091 | 1.2 | Thông tin user (login) |
| `ActiveUsers` | 4,693,571 | 2,678 | Lịch sử đăng nhập |
| `AccessRight` | 2 | 0.28 | Quyền truy cập |
| `AccessRightCTRL` | 462 | 0.2 | Kiểm soát quyền |
| `AccessRightLevel` | 10 | 0.02 | Cấp độ quyền |
| `GroupList` | 17 | 0.07 | Danh sách nhóm |
| `Departments` | 108 | 0.48 | Phòng ban |
| `Dept_Manage` | 675 | 0.07 | Quản lý phòng ban |
| `Department_Group_Setup` | 98 | 0.07 | Cấu hình nhóm phòng ban |
| `Department_Report_Setup` | 773 | 0.21 | Cấu hình báo cáo |
| `Department_ViewReports` | 9,852 | 2.98 | Phân quyền xem báo cáo |
| `PersonalProfile` | 21 | 0.50 | Hồ sơ cá nhân |

---

### Nhóm 16 — Master data / Danh mục

| Bảng | Rows | Mô tả |
|---|---|---|
| `Countries` / `lst_Countries` / `lst_Country` | ~250 | Danh sách quốc gia |
| `lst_Cities` | 1,115 | Thành phố |
| `lst_States` | 17 | Tỉnh/bang |
| `lst_Regions` | 23 | Vùng |
| `lst_Continents` | 6 | Châu lục |
| `lst_Bank` | 203 | Ngân hàng |
| `Airports` / `Airport_AIR` | 15K / 1K | Sân bay |
| `VesselCode` | 26,376 | Mã tàu |
| `VesselSchedules` | 0 | Lịch tàu |
| `CurrencyExchangeRate` | 5,174 | Tỷ giá ngoại tệ |
| `ExchangeRate` | 19 | Tỷ giá cơ bản |
| `Commodity` | 96 | Hàng hóa |
| `UnitContents` | 145 | Đơn vị |
| `lst_Zone` / `lst_Zone_Local` | 15 / 27 | Khu vực |
| `lst_Service` | 13 | Dịch vụ |
| `lst_Industries` | 23 | Ngành nghề |
| `lst_Mode` | 8 | Phương thức vận chuyển |
| `lst_SaleType` | 10 | Loại kinh doanh |
| `lst_Source` | 30 | Nguồn |
| `TransactionType` | 17 | Loại giao dịch |

---

## Sơ đồ quan hệ chính

```
Partners (PartnerID)
  ├──► DebitNotes (PartnerID)
  │       └──► DebitNoteDetails (dbtID)
  │               └──► DebitNoteDetails_Payment (dbtDID)
  │       └──► DebitNotes_Payment (dbtID)
  │
  ├──► InvoiceReference (ShipperID)
  │       └──► InvoiceReferenceDetail (InvoiceNo)
  │
  ├──► TransactionDetails (ShipperID)
  │
  ├──► ProfitShares (PartnerID)
  └──► HandleInstructions (PartnerID)

Transactions (TransID)
  ├──► TransactionDetails (TransID)
  │       ├── FK: HWBNO → HAWB
  │       ├── FK: ShipperID → Partners
  │       └── FK: CustomsID → CustomsDeclaration
  │
  ├──► InvoiceReference (TransID)
  ├──► BuyingRate (TransID)
  ├──► ContainerLoaded (TransID)
  └──► ShippingInstruction (TransID)

HAWB (HWBNO)                             ← FK từ TransactionDetails.HWBNO
  ├──► SellingRate (HAWBNO)
  ├──► BuyingRateWithHBL (HAWBNO)
  ├──► ProfitShares (HAWBNO)
  ├──► RevenueDetails_Sheet (HWBNO)
  ├──► HAWBTracking (HWBNO)
  ├──► HAWBDETAILS (HWBNO)
  ├──► HAWBRATE (HWBNO)
  ├──► OtherChargeDetail (HBL)
  ├──► ContainerListOnHBL (HBLNo)
  ├──► ContainerLoadedHBL (HBLNo)
  ├──► TransactionInfo (HAWBNO)
  ├──► AdvanceSettlementPayment (HBL)
  └──► BookingLocal (ConfirmHBL)

VATInvoice (ID, InvoiceNo)
  └──► VATInvoiceDetail (ID, InvoiceNo)

InvoiceSOA (SOANO)
  └──► InvoiceReference (SOANO)

Revenue_Sheet (DocID)
  └──► RevenueDetails_Sheet (DocRefID)

PhieuThuChi (Maso)
  ├──► PhieuThuChiDetails (SoCT)
  └──► PhieuThuChiDetail (MasoPhieu)

DebitNotes (dbtID)
  ├──► DebitNoteDetails (dbtID)
  │       └──► DebitNoteDetails_Payment (dbtDID)
  └──► DebitNotes_Payment (dbtID)

Quotation_Combine (QuoID)
  ├──► Quotation_Combine_Air (QuoNo)
  │       └──► Quotation_Combine_Air_Charges (QuoDetailID)
  ├──► Quotation_Combine_Sea (QuoNo)
  │       └──► Quotation_Combine_Sea_Charge (QuoDetailID)
  ├──► Quotation_Combine_Truck_FCL (QuoNo)
  └──► Quotation_Combine_Truck_LCL (QuoNo)
```

---

## SQL Queries mẫu

### 1. Partner + thông tin ngân hàng
```sql
SELECT
  p.PartnerID, p.PartnerName, p.PartnerName3,
  p.Category, p.[Group], p.Taxcode, p.Country, p.PaymentTerm, p.Industry,
  b.BankName, b.BankAccNo
FROM Partners p
LEFT JOIN Partner_BankInfo b ON p.PartnerID = b.PartnerID
WHERE p.[Group] = 'CUSTOMERS' AND p.Status = 0
ORDER BY p.PartnerName;
```

### 2. Lô hàng gần đây + chi tiết vận đơn
```sql
SELECT
  t.TransID, t.TransDate, t.TpyeofService,
  td.IDKeyShipment, td.HWBNO, td.ShipperID,
  p.PartnerName, td.ETD, td.ETA, td.ShipmentType
FROM Transactions t
JOIN TransactionDetails td ON t.TransID = td.TransID
LEFT JOIN Partners p ON td.ShipperID = p.PartnerID
WHERE t.TransDate >= DATEADD(day, -30, GETDATE())
ORDER BY t.TransDate DESC;
```

### 3. Công nợ chưa thanh toán theo partner
```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.PartnerID, p.PartnerName,
  dn.TotalAmount, dn.isApproved, dn.Paid,
  dn.Fromdate, dn.ToDate
FROM DebitNotes dn
JOIN Partners p ON dn.PartnerID = p.PartnerID
WHERE dn.Paid = 0 AND dn.isApproved = 1
ORDER BY dn.TotalAmount DESC;
```

### 4. Hóa đơn VAT tháng hiện tại
```sql
SELECT
  v.InvoiceNo, v.InvoiceDate, v.CustomerID, v.CompanyName,
  v.Currency, v.VATTotal, v.ExRate,
  vd.Description, vd.Quantity, vd.UnitPrice, vd.Amount
FROM VATInvoice v
JOIN VATInvoiceDetail vd ON v.ID = vd.ID AND v.InvoiceNo = vd.InvoiceNo
WHERE v.InvoiceDate >= DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)
ORDER BY v.InvoiceDate DESC;
```

### 5. HAWB + Tổng giá bán / giá mua / lợi nhuận
```sql
SELECT
  h.HWBNO, h.AWBNO, h.TRANSID,
  ISNULL(sr.sell_total, 0) AS TotalSelling,
  ISNULL(br.buy_total, 0) AS TotalBuying,
  ISNULL(sr.sell_total, 0) - ISNULL(br.buy_total, 0) AS Profit
FROM HAWB h
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS sell_total
  FROM SellingRate GROUP BY HAWBNO
) sr ON h.HWBNO = sr.HAWBNO
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS buy_total
  FROM BuyingRateWithHBL GROUP BY HAWBNO
) br ON h.HWBNO = br.HAWBNO
WHERE h.TRANSID IS NOT NULL
ORDER BY h.ISSUED DESC;
```

### 6. ProfitShares theo HAWB
```sql
SELECT
  ps.HAWBNO, ps.PartnerID, p.PartnerName,
  ps.GroupName, ps.FieldName,
  ps.Quantity, ps.UnitPrice, ps.Amount, ps.TotalValue
FROM ProfitShares ps
LEFT JOIN Partners p ON ps.PartnerID = p.PartnerID
WHERE ps.HAWBNO = 'YOUR_HAWBNO_HERE';
```

### 7. Debit Note chi tiết + thanh toán
```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.PartnerID, p.PartnerName, dn.TotalAmount,
  dnd.IDKeyIndex, dnd.TransID, dnd.HWBNO, dnd.PaidAmount,
  dnp.PaymentNo, dnp.PaidAmount AS PaymentAmt
FROM DebitNotes dn
JOIN Partners p ON dn.PartnerID = p.PartnerID
JOIN DebitNoteDetails dnd ON dn.dbtID = dnd.dbtID
LEFT JOIN DebitNoteDetails_Payment dnp ON dnd.IDKeyIndex = dnp.dbtDID
WHERE dn.dbtID = 'YOUR_DBTID_HERE';
```

### 8. Phiếu thu/chi trong kỳ
```sql
SELECT
  ptc.Maso, ptc.Ngay, ptc.MaLoaiPhieu,
  ptc.Nguoinoptien, ptc.Donvi,
  ptc.Sotien, ptc.LoaiTien, ptc.Tygia,
  ptc.Lydo
FROM PhieuThuChi ptc
WHERE ptc.Ngay >= '2026-01-01' AND ptc.Ngay < '2026-04-01'
ORDER BY ptc.Ngay DESC;
```

### 9. List bảng + row count + size (khảo sát)
```sql
SELECT
  t.name AS table_name,
  p.rows AS row_count,
  CAST(ROUND(SUM(a.total_pages) * 8.0 / 1024, 2) AS DECIMAL(18,2)) AS size_mb
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.is_ms_shipped = 0
GROUP BY t.name, p.rows
ORDER BY p.rows DESC;
```

### 10. Foreign key relationships
```sql
SELECT
  tp.name AS parent_table,
  cp.name AS parent_column,
  tr.name AS child_table,
  cr.name AS child_column,
  fk.name AS fk_name
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
JOIN sys.tables tp ON fkc.referenced_object_id = tp.object_id
JOIN sys.columns cp ON fkc.referenced_object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
JOIN sys.tables tr ON fkc.parent_object_id = tr.object_id
JOIN sys.columns cr ON fkc.parent_object_id = cr.object_id AND fkc.parent_column_id = cr.column_id
ORDER BY parent_table, child_table;
```

---

## Gợi ý Priority cho CDC Sync

| Priority | Bảng | Lý do |
|---|---|---|
| **P0** | `Partners`, `PartnerContact` | Master — cần trước để hiển thị UI |
| **P0** | `Departments`, `UserInfos` | Danh mục người dùng |
| **P0** | `Countries`, `Airports`, `VesselCode` | Reference data |
| **P0** | `CurrencyExchangeRate` | Tỷ giá |
| **P1** | `Transactions`, `TransactionDetails` | Nghiệp vụ chính, realtime |
| **P1** | `HAWB`, `HAWBDETAILS` | Vận đơn, realtime |
| **P1** | `DebitNotes`, `DebitNoteDetails` | Công nợ |
| **P1** | `VATInvoice`, `VATInvoiceDetail` | Hóa đơn |
| **P1** | `SellingRate`, `BuyingRateWithHBL` | Doanh thu/chi phí |
| **P1** | `ProfitShares` | Lợi nhuận |
| **P1** | `InvoiceReference` | Đối soát hóa đơn |
| **P1** | `PhieuThuChi`, `PhieuThuChiDetails` | Kế toán thu/chi |
| **P2** | `Partner_History`, `RateHistory` | Archive — batch import |
| **P2** | `*_DELETE`, `*_2019` | Archive/deleted data |
| **P2** | `EInvoice_History` | Lớn (11GB) — sync sau |
| **P2** | `ActiveUsers`, `TransactionsChange` | Log — ít cần thiết |

---

## Lưu ý

- `PartnerID` là `nvarchar(100)`, format: `CS000001` (customer), `AG000001` (agent), `CL000001` (client)
- `TransID` format: `BIHCM008238/25` (prefix office + số + năm)
- `HWBNO` format đa dạng theo loại hàng và văn phòng
- `dbtID` format: `BKHCM2603/03194` (debit note ID)
- Nhiều bảng có cột `OBH` (On Behalf) — dùng cho trường hợp đại lý làm thay
- Bảng `*_DELETE` là audit trail — lưu dữ liệu đã xóa, không cần sync realtime
