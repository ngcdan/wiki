---
title: "DB Schema Core"
tags:
  - bf1
  - fms
  - schema
  - postgresql
---

# BF1_DB_Schema_Core — Schema Nghiệp vụ Lõi

> Tập trung vào nghiệp vụ vận chuyển: Lô hàng, Vận đơn, Giá, Công nợ, Doanh thu, Booking, Kho, Hải quan, Trucking, Master data.
> Bỏ qua: kế toán (PhieuThuChi), hóa đơn VAT (VATInvoice), người dùng (UserInfos), quotation.

---

## Tổng quan quan hệ

```
[Nhóm 10: Master data]
  Partners, Countries, Airports, VesselCode, CurrencyExchangeRate ...
        │
        ▼
[Nhóm 1: Transactions]          [Nhóm 6: Booking]
  Transactions (TransID)  ◄──── BookingLocal (BkgID)
        │                        SeaBookingNote
        ▼
  TransactionDetails (TransID, HWBNO, ShipperID)
        │                │              │
        │                │              ▼
        │                │     [Nhóm 10: Partners]
        │                ▼
[Nhóm 2: HAWB]      [Nhóm 8: Customs]
  HAWB (HWBNO)       CustomsDeclaration (MasoTK)
     │  │
     │  └──► [Nhóm 3: Rates]
     │           SellingRate (HAWBNO)
     │           BuyingRateWithHBL (HAWBNO)
     │           OtherChargeDetail (HBL)
     │
     ├──► [Nhóm 4: Debit Notes]
     │        DebitNoteDetails (HWBNO)
     │              └──► DebitNoteDetails_Payment
     │
     ├──► [Nhóm 5: Profit & Revenue]
     │        ProfitShares (HAWBNO)
     │        RevenueDetails_Sheet (HWBNO)
     │
     └──► HAWBTracking, HAWBDETAILS, HAWBRATE
              │
              └──► [Nhóm 7: Warehouse] (xử lý kho sau khi hàng về)
                       Warehouse, WarehouseDetail

[Nhóm 9: Trucking]
  Trucking_Track (gắn với lô hàng/HWBNO)
```

---

## Nhóm 1 — Transactions / Lô hàng

### `Transactions` — Master lô hàng

| Column | Type | Mô tả |
|--------|------|-------|
| `TransID` | nvarchar (PK) | Mã lô hàng. Format: `BIHCM008238/25` (prefix văn phòng + số + năm) |
| `TransDate` | datetime | Ngày tạo lô |
| `TpyeofService` | nvarchar | Loại dịch vụ (AIR, SEA FCL, SEA LCL, ...) |
| `WhoisMaking` | nvarchar | Username người tạo |
| `LoadingDate` | datetime | Ngày xếp hàng |
| `ArrivalDate` | datetime | Ngày hàng đến |
| `PortofLading` | nvarchar | Cảng xếp hàng (airport/port code) |
| `PortofUnlading` | nvarchar | Cảng dỡ hàng |
| `Status` | int/bit | Trạng thái lô |

- **Rows:** 681,038 | **Size:** 1,476 MB
- **FK ra ngoài:** `Transactions.TransID` → `TransactionDetails`, `BuyingRate`, `InvoiceReference`, `ShippingInstruction`, `BookingLocal`, `ProfitShareCalc`

---

### `TransactionDetails` — Chi tiết lô hàng

| Column | Type | Mô tả |
|--------|------|-------|
| `IDKeyShipment` | int (PK) | Khóa chính nội bộ |
| `TransID` | nvarchar (FK) | FK → `Transactions.TransID` |
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ShipperID` | nvarchar (FK) | FK → `Partners.PartnerID` |
| `CustomsID` | nvarchar (FK) | FK → `CustomsDeclaration.MasoTK` |
| `ETD` | datetime | Estimated Time of Departure |
| `ETA` | datetime | Estimated Time of Arrival |
| `ShipmentType` | nvarchar | Loại hàng (FCL, LCL, ...) |

- **Rows:** 831,608 | **Size:** 1,982 MB

---

### `TransactionInfo` — Thông tin bổ sung per shipment

| Column | Type | Mô tả |
|--------|------|-------|
| `HAWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `TransID` | nvarchar | Mã lô hàng |
| *(thông tin mở rộng)* | | Các field bổ sung cho lô hàng |

- **Rows:** 508,008 | **Size:** 292 MB

---

### Các bảng phụ (Nhóm 1)

| Bảng | Rows | Mô tả |
|------|------|-------|
| `TransactionsChange` | 1,411,298 | Lịch sử thay đổi lô hàng (audit log) |
| `Transaction_Notes` | 45,824 | Ghi chú đính kèm lô hàng |
| `Transaction_Ops` | 22,810 | Thao tác vận hành |
| `Transaction_Task` | 399,773 | Task gắn với lô hàng |
| `TransactionType` | 17 | Danh mục loại giao dịch |

---

## Nhóm 2 — HAWB / House Bill of Lading

### `HAWB` — Vận đơn nhà (House Bill)

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (PK) | Mã vận đơn nhà. Format đa dạng theo loại hàng và văn phòng |
| `AWBNO` | nvarchar | Master AWB/BL số (Air Waybill / Bill of Lading của carrier) |
| `TRANSID` | nvarchar (FK) | FK → `Transactions.TransID` (qua `TransactionDetails`) |
| `ISSUED` | datetime | Ngày phát hành vận đơn |
| `Status` | int/bit | Trạng thái vận đơn |

- **Rows:** 866,657 | **Size:** 2,773 MB
- **FK ra ngoài (20+ bảng):** `HAWB.HWBNO` → `SellingRate`, `BuyingRateWithHBL`, `ProfitShares`, `ProfitSharesCost`, `RevenueDetails_Sheet`, `TransactionDetails`, `TransactionInfo`, `OtherChargeDetail`, `ContainerListOnHBL`, `ContainerLoadedHBL`, `HAWBTracking`, `HAWBDETAILS`, `HAWBRATE`, `BookingLocal`, `AdvanceSettlementPayment`, `DebitNoteDetails`

---

### `HAWBDETAILS` — Chi tiết hàng hóa trên HBL

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `Description` | nvarchar | Mô tả hàng hóa |
| `Quantity` | decimal | Số lượng |
| `Weight` | decimal | Trọng lượng |
| `Volume` | decimal | Thể tích |
| `Unit` | nvarchar | Đơn vị |

- **Rows:** 369,773 | **Size:** 451 MB

---

### `HAWBRATE` — Giá theo vận đơn (tổng hợp trên HBL)

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `RateCode` | nvarchar | Mã loại phí |
| `Amount` | decimal | Giá trị |
| `Currency` | nvarchar | Ngoại tệ |

- **Rows:** 87,694 | **Size:** 18 MB

---

### `HAWBTracking` — Tracking trạng thái vận chuyển

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `Status` | nvarchar | Trạng thái (DEPARTED, ARRIVED, ...) |
| `Location` | nvarchar | Địa điểm |
| `EventDate` | datetime | Thời điểm sự kiện |

- **Rows:** 96,599 | **Size:** 66 MB

---

### `ContainerListOnHBL` — Container gắn với HBL

| Column | Type | Mô tả |
|--------|------|-------|
| `HBLNo` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ContainerNo` | nvarchar | Số container |
| `SealNo` | nvarchar | Số chì |
| `ContainerType` | nvarchar | Loại container (20DC, 40HC, ...) |

- **Rows:** 141,216 | **Size:** 67 MB

---

### `HAWB_Partner_Address` — Địa chỉ đối tác trên HBL

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `PartnerID` | nvarchar (FK) | FK → `Partners.PartnerID` |
| `AddressType` | nvarchar | Loại địa chỉ (Shipper, Consignee, ...) |
| `Address` | nvarchar | Địa chỉ đầy đủ |

- **Rows:** 5,191 | **Size:** 4.8 MB

---

## Nhóm 3 — Rates / Bảng giá

> Chỉ lấy các bảng có FK trực tiếp tới `HAWB.HWBNO` hoặc `Transactions.TransID`.

### `SellingRate` — Giá bán (theo HAWBNO)

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `HAWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `ChargeName` | nvarchar | Tên phí |
| `Quantity` | decimal | Số lượng |
| `UnitPrice` | decimal | Đơn giá |
| `Amount` | decimal | Thành tiền |
| `Currency` | nvarchar | Ngoại tệ |
| `ExRate` | decimal | Tỷ giá |
| `AmountVND` | decimal | Thành tiền VND |

- **Rows:** 1,942,592 | **Size:** 3,537 MB

---

### `BuyingRateWithHBL` — Giá mua (theo HAWBNO)

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `HAWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `ChargeName` | nvarchar | Tên phí |
| `Quantity` | decimal | Số lượng |
| `UnitPrice` | decimal | Đơn giá |
| `Amount` | decimal | Thành tiền |
| `Currency` | nvarchar | Ngoại tệ |
| `ExRate` | decimal | Tỷ giá |
| `AmountVND` | decimal | Thành tiền VND |
| `VendorID` | nvarchar | Nhà cung cấp |

- **Rows:** 433,281 | **Size:** 921 MB

---

### `BuyingRate` — Giá mua (theo TransID)

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `TransID` | nvarchar (FK) | FK → `Transactions.TransID` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `Amount` | decimal | Thành tiền |
| `Currency` | nvarchar | Ngoại tệ |

- **Rows:** 5,177 | **Size:** 8.2 MB

---

### `BuyingRateOthers` — Phí mua khác (theo TransID)

| Column | Type | Mô tả |
|--------|------|-------|
| `TransID` | nvarchar (FK) | FK → `Transactions.TransID` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `Amount` | decimal | Thành tiền |

- **Rows:** 4,133 | **Size:** 7.2 MB

---

### `OtherChargeList` — Danh mục phí khác

| Column | Type | Mô tả |
|--------|------|-------|
| `ChargeCode` | nvarchar (PK) | Mã phí |
| `ChargeName` | nvarchar | Tên phí |
| `Description` | nvarchar | Mô tả |
| `ChargeSide` | nvarchar | Selling/Buying |

- **Rows:** 26,123 | **Size:** 30 MB

---

### `OtherChargeDetail` — Chi tiết phí khác (theo HBL)

| Column | Type | Mô tả |
|--------|------|-------|
| `HBL` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `Amount` | decimal | Thành tiền |
| `Currency` | nvarchar | Ngoại tệ |

- **Rows:** 246,546 | **Size:** 151 MB

---

### `RateHistory` — Lịch sử tất cả rates

| Column | Type | Mô tả |
|--------|------|-------|
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `RateType` | nvarchar | Loại rate (Selling/Buying) |
| `ChangedAt` | datetime | Thời điểm thay đổi |
| `OldAmount` | decimal | Giá trị cũ |
| `NewAmount` | decimal | Giá trị mới |

- **Rows:** 6,448,501 | **Size:** 4,863 MB (audit log — không sync realtime)

---

## Nhóm 4 — Debit Notes / Công nợ

### `DebitNotes` — Phiếu công nợ

| Column | Type | Mô tả |
|--------|------|-------|
| `dbtID` | nvarchar (PK) | Mã phiếu. Format: `BKHCM2603/03194` |
| `PartnerID` | nvarchar (FK) | FK → `Partners.PartnerID` |
| `DebitDate` | datetime | Ngày lập phiếu |
| `Fromdate` | datetime | Từ ngày (kỳ công nợ) |
| `ToDate` | datetime | Đến ngày |
| `TotalAmount` | decimal | Tổng tiền |
| `Currency` | nvarchar | Ngoại tệ |
| `isApproved` | bit | Đã duyệt |
| `Paid` | bit | Đã thanh toán |
| `Note` | nvarchar | Ghi chú |

- **Rows:** 309,724 | **Size:** 316 MB

---

### `DebitNoteDetails` — Chi tiết công nợ

| Column | Type | Mô tả |
|--------|------|-------|
| `IDKeyIndex` | int (PK) | Khóa chính (dùng làm FK cho payment) |
| `dbtID` | nvarchar (FK) | FK → `DebitNotes.dbtID` |
| `TransID` | nvarchar | Mã lô hàng |
| `HWBNO` | nvarchar | Mã vận đơn nhà |
| `ChargeCode` | nvarchar | Mã loại phí |
| `ChargeName` | nvarchar | Tên phí |
| `Quantity` | decimal | Số lượng |
| `UnitPrice` | decimal | Đơn giá |
| `PaidAmount` | decimal | Số tiền đã thanh toán |
| `Currency` | nvarchar | Ngoại tệ |
| `ExRate` | decimal | Tỷ giá |

- **Rows:** 4,141,341 | **Size:** 7,487 MB

---

### `DebitNoteDetails_Payment` — Thanh toán chi tiết

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `dbtDID` | int (FK) | FK → `DebitNoteDetails.IDKeyIndex` |
| `PaymentNo` | nvarchar | Số phiếu thanh toán |
| `PaidAmount` | decimal | Số tiền thanh toán lần này |
| `PaidDate` | datetime | Ngày thanh toán |
| `Currency` | nvarchar | Ngoại tệ |

- **Rows:** 3,820,487 | **Size:** 1,303 MB

---

### `DebitNotes_Payment` — Thanh toán tổng phiếu

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `dbtID` | nvarchar (FK) | FK → `DebitNotes.dbtID` |
| `PaymentNo` | nvarchar | Số phiếu thanh toán |
| `PaidAmount` | decimal | Tổng tiền thanh toán |
| `PaidDate` | datetime | Ngày thanh toán |

- **Rows:** 318,685 | **Size:** 54 MB

---

## Nhóm 5 — Profit & Revenue

### `ProfitShares` — Chia lợi nhuận

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `HAWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `PartnerID` | nvarchar (FK) | FK → `Partners.PartnerID` |
| `GroupName` | nvarchar | Nhóm phí (Selling, Buying, ...) |
| `FieldName` | nvarchar | Tên trường phí |
| `Quantity` | decimal | Số lượng |
| `UnitPrice` | decimal | Đơn giá |
| `Amount` | decimal | Thành tiền |
| `TotalValue` | decimal | Tổng giá trị |
| `Currency` | nvarchar | Ngoại tệ |
| `ExRate` | decimal | Tỷ giá |

- **Rows:** 3,167,966 | **Size:** 5,565 MB

---

### `Revenue_Sheet` — Tổng hợp doanh thu

| Column | Type | Mô tả |
|--------|------|-------|
| `DocID` | nvarchar (PK) | Mã tờ doanh thu |
| `DocDate` | datetime | Ngày |
| `TotalRevenue` | decimal | Tổng doanh thu |
| `Currency` | nvarchar | Ngoại tệ |
| `Status` | int | Trạng thái |

- **Rows:** 5,781 | **Size:** 6.3 MB
- **FK:** `Revenue_Sheet.DocID` → `RevenueDetails_Sheet.DocRefID`

---

### `RevenueDetails_Sheet` — Chi tiết doanh thu

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `DocRefID` | nvarchar (FK) | FK → `Revenue_Sheet.DocID` |
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ChargeCode` | nvarchar | Mã loại phí |
| `Amount` | decimal | Thành tiền |
| `Currency` | nvarchar | Ngoại tệ |

- **Rows:** 4,596,253 | **Size:** 2,105 MB

---

## Nhóm 6 — Booking

### `BookingLocal` — Booking nội địa

| Column | Type | Mô tả |
|--------|------|-------|
| `BkgID` | nvarchar (PK) | Mã booking |
| `ConfirmHBL` | nvarchar (FK) | FK → `HAWB.HWBNO` |
| `ConformJobNo` | nvarchar (FK) | FK → `Transactions.TransID` |
| `BookingDate` | datetime | Ngày booking |
| `Status` | nvarchar | Trạng thái |
| `PartnerID` | nvarchar (FK) | FK → `Partners.PartnerID` |

- **Rows:** 41,481 | **Size:** 97 MB

---

### `BookingContainer` — Container trong booking

| Column | Type | Mô tả |
|--------|------|-------|
| `BkgID` | nvarchar (FK) | FK → `BookingLocal.BkgID` |
| `ContainerNo` | nvarchar | Số container |
| `ContainerType` | nvarchar | Loại container |
| `SealNo` | nvarchar | Số chì |

- **Rows:** 36,291 | **Size:** 10 MB

---

### `SeaBookingNote` — Booking sea

| Column | Type | Mô tả |
|--------|------|-------|
| `BookingID` | nvarchar (PK) | Mã booking sea |
| `TransactionID` | nvarchar (FK) | FK → `TransactionDetails.IDKeyShipment` |
| `VesselCode` | nvarchar | Mã tàu |
| `Voyage` | nvarchar | Số chuyến |
| `ETD` | datetime | Ngày khởi hành dự kiến |
| `ETA` | datetime | Ngày đến dự kiến |

- **Rows:** 38,286 | **Size:** 282 MB

---

### `ShippingInstruction` — Hướng dẫn vận chuyển

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `TransID` | nvarchar (FK) | FK → `Transactions.TransID` |
| `Instructions` | nvarchar | Nội dung hướng dẫn |
| `CreatedAt` | datetime | Ngày tạo |
| `Status` | nvarchar | Trạng thái |

- **Rows:** 235,879 | **Size:** 118 MB

---

## Nhóm 7 — Warehouse / Kho

### `Warehouse` — Kho hàng

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` (hoặc TransID) |
| `WarehouseCode` | nvarchar | Mã kho |
| `ReceivedDate` | datetime | Ngày nhận hàng |
| `Status` | nvarchar | Trạng thái |

- **Rows:** 88,947 | **Size:** 68 MB

---

### `WarehouseDetail` — Chi tiết kho

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `WarehouseID` | int (FK) | FK → `Warehouse.ID` |
| `ItemCode` | nvarchar | Mã hàng |
| `Quantity` | decimal | Số lượng |
| `Weight` | decimal | Trọng lượng |
| `Location` | nvarchar | Vị trí trong kho |

- **Rows:** 183,114 | **Size:** 59 MB

---

### `Warehouse_Payment` — Thanh toán kho

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `WarehouseID` | int (FK) | FK → `Warehouse.ID` |
| `Amount` | decimal | Số tiền |
| `PaidDate` | datetime | Ngày thanh toán |

- **Rows:** 84,913 | **Size:** 74 MB

---

## Nhóm 8 — Hải quan / Customs

### `CustomsDeclaration` — Tờ khai hải quan

| Column | Type | Mô tả |
|--------|------|-------|
| `MasoTK` | nvarchar (PK) | Mã số tờ khai |
| `TransID` | nvarchar | Mã lô hàng (link qua `TransactionDetails.CustomsID`) |
| `HWBNO` | nvarchar | Mã vận đơn nhà |
| `DeclarationDate` | datetime | Ngày khai báo |
| `Status` | nvarchar | Trạng thái (chờ, thông quan, ...) |
| `CustomsOffice` | nvarchar | Chi cục hải quan |
| `ImportExport` | nvarchar | Xuất/Nhập khẩu |

- **Rows:** 790,556 | **Size:** 559 MB
- **FK:** `CustomsDeclaration.MasoTK` → `TransactionDetails.CustomsID`

---

### `CustomsAssignedList` — Phân công hải quan

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `MasoTK` | nvarchar (FK) | FK → `CustomsDeclaration.MasoTK` |
| `StaffID` | nvarchar | Nhân viên phụ trách |
| `AssignedDate` | datetime | Ngày phân công |

- **Rows:** 2,039 | **Size:** 1.05 MB

---

### `Customs_Bonded_Warehouse` — Kho ngoại quan

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `MasoTK` | nvarchar (FK) | FK → `CustomsDeclaration.MasoTK` |
| `WarehouseCode` | nvarchar | Mã kho ngoại quan |
| `EntryDate` | datetime | Ngày nhập kho |
| `ExitDate` | datetime | Ngày xuất kho |

- **Rows:** 15,927 | **Size:** 2.1 MB

---

## Nhóm 9 — Trucking

### `Trucking_Track` — Tracking xe tải

| Column | Type | Mô tả |
|--------|------|-------|
| `ID` | int (PK) | Khóa chính |
| `HWBNO` | nvarchar (FK) | FK → `HAWB.HWBNO` (hoặc TransID) |
| `TruckNo` | nvarchar | Số xe tải |
| `DriverName` | nvarchar | Tên tài xế |
| `Status` | nvarchar | Trạng thái (Đang chạy, Đã giao, ...) |
| `PickupDate` | datetime | Ngày lấy hàng |
| `DeliveryDate` | datetime | Ngày giao hàng |
| `PickupAddress` | nvarchar | Địa điểm lấy hàng |
| `DeliveryAddress` | nvarchar | Địa điểm giao hàng |

- **Rows:** 114,938 | **Size:** 51 MB

---

## Nhóm 10 — Master data / Danh mục

| Bảng | Rows | Mô tả | Dùng trong |
|------|------|-------|-----------|
| `Partners` | 52,414 | Master đối tác/KH (PK: `PartnerID`) | TransactionDetails, DebitNotes, ProfitShares |
| `Countries` / `lst_Countries` | ~250 | Danh sách quốc gia | Partners, HAWB |
| `lst_Cities` | 1,115 | Thành phố | Địa chỉ đối tác |
| `lst_Bank` | 203 | Ngân hàng | Partner_BankInfo |
| `Airports` / `Airport_AIR` | 15K / 1K | Sân bay (PK: `AirPortName`) | Transactions (PortofLading/Unlading) |
| `VesselCode` | 26,376 | Mã tàu | SeaBookingNote |
| `CurrencyExchangeRate` | 5,174 | Tỷ giá ngoại tệ (PK: `ID` dạng `HCMGIANGNTH_2025`) | SellingRate, BuyingRate |
| `ExchangeRate` | 19 | Tỷ giá cơ bản | Tham chiếu nhanh |
| `Commodity` | 96 | Hàng hóa | HAWBDETAILS |
| `UnitContents` | 145 | Đơn vị (PK: `UnitID`) | HAWBDETAILS, SellingRate |
| `lst_Mode` | 8 | Phương thức vận chuyển | Transactions |
| `lst_Service` | 13 | Dịch vụ | Transactions |
| `TransactionType` | 17 | Loại giao dịch | Transactions |

---

## Sơ đồ quan hệ chi tiết (nghiệp vụ lõi)

```
Transactions (TransID = 'BIHCM008238/25')
  │
  ├──[1:N]──► TransactionDetails (TransID)
  │                │
  │                ├──[N:1]──► HAWB (HWBNO)                ← cùng lô có nhiều vận đơn nhà
  │                │              │
  │                │              ├──[1:N]──► HAWBDETAILS (HWBNO)
  │                │              ├──[1:N]──► HAWBRATE (HWBNO)
  │                │              ├──[1:N]──► HAWBTracking (HWBNO)
  │                │              ├──[1:N]──► ContainerListOnHBL (HBLNo)
  │                │              │
  │                │              ├──[1:N]──► SellingRate (HAWBNO)
  │                │              ├──[1:N]──► BuyingRateWithHBL (HAWBNO)
  │                │              ├──[1:N]──► OtherChargeDetail (HBL)
  │                │              │
  │                │              ├──[1:N]──► ProfitShares (HAWBNO)
  │                │              ├──[1:N]──► RevenueDetails_Sheet (HWBNO)
  │                │              │              └─[N:1]──► Revenue_Sheet (DocID)
  │                │              │
  │                │              └──[1:N]──► DebitNoteDetails (HWBNO)
  │                │                             └─[N:1]──► DebitNotes (dbtID)
  │                │                                            ├──[1:N]──► DebitNoteDetails_Payment (dbtDID)
  │                │                                            └──[1:N]──► DebitNotes_Payment (dbtID)
  │                │
  │                ├──[N:1]──► Partners (ShipperID = PartnerID)
  │                └──[N:1]──► CustomsDeclaration (CustomsID = MasoTK)
  │
  ├──[1:N]──► BuyingRate (TransID)
  ├──[1:N]──► BuyingRateOthers (TransID)
  ├──[1:N]──► ShippingInstruction (TransID)
  └──[1:1]──► BookingLocal (ConformJobNo = TransID)
                  └──[1:1]──► BookingLocal.ConfirmHBL = HAWB.HWBNO

Partners (PartnerID = 'CS000001')
  └──[1:N]──► DebitNotes (PartnerID)
  └──[1:N]──► ProfitShares (PartnerID)

CurrencyExchangeRate (ID = 'HCMGIANGNTH_2025')
  └── được tham chiếu bởi ExRate trong SellingRate, BuyingRateWithHBL, DebitNotes...

Airports (AirPortName)
  └──[N:1]──► Transactions (PortofLading, PortofUnlading)

CustomsDeclaration (MasoTK)
  ├──[1:N]──► CustomsAssignedList (MasoTK)
  └──[1:N]──► Customs_Bonded_Warehouse (MasoTK)
```

---

## Sample Data

### `Transactions`

| TransID | TransDate | TpyeofService | WhoisMaking | PortofLading | PortofUnlading |
|---------|-----------|---------------|-------------|--------------|----------------|
| `BIHCM008238/25` | 2025-03-01 | AIR EXPORT | nguyenvana | SGN | NRT |
| `BIHCM008239/25` | 2025-03-01 | SEA FCL EXP | tranb | VNCMT | CNSHA |
| `BIHCM008240/25` | 2025-03-02 | SEA LCL EXP | lethic | VNCMT | USLAX |

### `TransactionDetails`

| IDKeyShipment | TransID | HWBNO | ShipperID | ETD | ETA |
|---------------|---------|-------|-----------|-----|-----|
| 1001 | `BIHCM008238/25` | `HCM-AIR-001/25` | `CS000123` | 2025-03-05 | 2025-03-06 |
| 1002 | `BIHCM008239/25` | `HCM-SEA-002/25` | `CS000456` | 2025-03-10 | 2025-04-01 |

### `HAWB`

| HWBNO | AWBNO | TRANSID | ISSUED |
|-------|-------|---------|--------|
| `HCM-AIR-001/25` | `176-12345678` | `BIHCM008238/25` | 2025-03-04 |
| `HCM-SEA-002/25` | `COSU1234567890` | `BIHCM008239/25` | 2025-03-08 |

### `SellingRate`

| ID | HAWBNO | ChargeCode | ChargeName | Quantity | UnitPrice | Amount | Currency |
|----|--------|------------|------------|----------|-----------|--------|----------|
| 5001 | `HCM-AIR-001/25` | AF | Air Freight | 100 | 3.5 | 350 | USD |
| 5002 | `HCM-AIR-001/25` | FSC | Fuel Surcharge | 100 | 0.8 | 80 | USD |
| 5003 | `HCM-SEA-002/25` | OF | Ocean Freight | 1 | 1200 | 1200 | USD |

### `BuyingRateWithHBL`

| ID | HAWBNO | ChargeCode | ChargeName | Amount | Currency | VendorID |
|----|--------|------------|------------|--------|----------|---------|
| 3001 | `HCM-AIR-001/25` | AF | Air Freight | 280 | USD | `AG000088` |
| 3002 | `HCM-SEA-002/25` | OF | Ocean Freight | 950 | USD | `AG000012` |

### `DebitNotes`

| dbtID | PartnerID | DebitDate | TotalAmount | Currency | isApproved | Paid |
|-------|-----------|-----------|-------------|----------|-----------|------|
| `BKHCM2603/03194` | `CS000123` | 2025-03-20 | 430 | USD | 1 | 0 |
| `BKHCM2603/03195` | `CS000456` | 2025-03-20 | 1200 | USD | 1 | 1 |

### `DebitNoteDetails`

| IDKeyIndex | dbtID | TransID | HWBNO | ChargeName | PaidAmount | Currency |
|------------|-------|---------|-------|------------|------------|---------|
| 9001 | `BKHCM2603/03194` | `BIHCM008238/25` | `HCM-AIR-001/25` | Air Freight | 350 | USD |
| 9002 | `BKHCM2603/03194` | `BIHCM008238/25` | `HCM-AIR-001/25` | Fuel Surcharge | 80 | USD |

### `ProfitShares`

| HAWBNO | PartnerID | GroupName | FieldName | Amount | Currency |
|--------|-----------|-----------|-----------|--------|---------|
| `HCM-AIR-001/25` | `CS000123` | Selling | Air Freight | 350 | USD |
| `HCM-AIR-001/25` | `AG000088` | Buying | Air Freight | 280 | USD |

### `CustomsDeclaration`

| MasoTK | DeclarationDate | Status | CustomsOffice | ImportExport |
|--------|-----------------|--------|---------------|--------------|
| `10100000000001` | 2025-03-04 | Thông quan | HCM - Cảng SGN | Export |
| `10100000000002` | 2025-03-10 | Chờ thông quan | HCM - Cảng Cát Lái | Export |

### `Trucking_Track`

| ID | HWBNO | TruckNo | Status | PickupDate | DeliveryDate |
|----|-------|---------|--------|------------|--------------|
| 201 | `HCM-AIR-001/25` | 51B-12345 | Đã giao | 2025-03-03 08:00 | 2025-03-03 14:30 |
| 202 | `HCM-SEA-002/25` | 51C-67890 | Đang chạy | 2025-03-09 07:00 | NULL |

---

## Lưu ý về format ID

| Field | Format | Ví dụ |
|-------|--------|-------|
| `TransID` | `{prefix văn phòng}{số}/{năm 2 chữ số}` | `BIHCM008238/25` |
| `HWBNO` | Đa dạng theo loại hàng và văn phòng | `HCM-AIR-001/25`, `176-12345678` |
| `PartnerID` | `{CS/AG/CL}{6 số}` | `CS000001` (customer), `AG000001` (agent) |
| `dbtID` | `{BK}{văn phòng}{MMYY}/{số}` | `BKHCM2603/03194` |
| `MasoTK` | Số tờ khai 14 ký tự | `10100000000001` |
| `CurrencyExchangeRate.ID` | `{văn phòng}_{năm}` | `HCMGIANGNTH_2025` |

---

## SQL Queries mẫu (nghiệp vụ lõi)

### 1. Lô hàng + vận đơn + shipper

```sql
SELECT
  t.TransID, t.TransDate, t.TpyeofService,
  td.HWBNO, td.ETD, td.ETA, td.ShipmentType,
  p.PartnerID, p.PartnerName
FROM Transactions t
JOIN TransactionDetails td ON t.TransID = td.TransID
LEFT JOIN Partners p ON td.ShipperID = p.PartnerID
WHERE t.TransDate >= DATEADD(day, -30, GETDATE())
ORDER BY t.TransDate DESC;
```

### 2. HAWB + Selling / Buying / Profit

```sql
SELECT
  h.HWBNO, h.AWBNO, h.TRANSID,
  ISNULL(sr.sell_total, 0)                                AS TotalSelling,
  ISNULL(br.buy_total, 0)                                 AS TotalBuying,
  ISNULL(sr.sell_total, 0) - ISNULL(br.buy_total, 0)     AS Profit
FROM HAWB h
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS sell_total FROM SellingRate GROUP BY HAWBNO
) sr ON h.HWBNO = sr.HAWBNO
LEFT JOIN (
  SELECT HAWBNO, SUM(Amount) AS buy_total FROM BuyingRateWithHBL GROUP BY HAWBNO
) br ON h.HWBNO = br.HAWBNO
WHERE h.TRANSID IS NOT NULL
ORDER BY h.ISSUED DESC;
```

### 3. Công nợ chưa thanh toán theo partner

```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.PartnerID, p.PartnerName,
  dn.TotalAmount, dn.Currency, dn.isApproved, dn.Paid,
  dn.Fromdate, dn.ToDate
FROM DebitNotes dn
JOIN Partners p ON dn.PartnerID = p.PartnerID
WHERE dn.Paid = 0 AND dn.isApproved = 1
ORDER BY dn.TotalAmount DESC;
```

### 4. Debit Note chi tiết + tracking thanh toán

```sql
SELECT
  dn.dbtID, dn.DebitDate, dn.TotalAmount,
  dnd.IDKeyIndex, dnd.HWBNO, dnd.ChargeName, dnd.PaidAmount,
  dnp.PaymentNo, dnp.PaidAmount AS PaymentAmt, dnp.PaidDate
FROM DebitNotes dn
JOIN DebitNoteDetails dnd ON dn.dbtID = dnd.dbtID
LEFT JOIN DebitNoteDetails_Payment dnp ON dnd.IDKeyIndex = dnp.dbtDID
WHERE dn.dbtID = 'BKHCM2603/03194';
```

### 5. ProfitShares theo HAWB

```sql
SELECT
  ps.HAWBNO, ps.PartnerID, p.PartnerName,
  ps.GroupName, ps.FieldName,
  ps.Quantity, ps.UnitPrice, ps.Amount
FROM ProfitShares ps
LEFT JOIN Partners p ON ps.PartnerID = p.PartnerID
WHERE ps.HAWBNO = 'HCM-AIR-001/25';
```

### 6. Hải quan theo lô hàng

```sql
SELECT
  td.TransID, td.HWBNO,
  cd.MasoTK, cd.DeclarationDate, cd.Status, cd.CustomsOffice
FROM TransactionDetails td
LEFT JOIN CustomsDeclaration cd ON td.CustomsID = cd.MasoTK
WHERE td.TransID = 'BIHCM008238/25';
```

### 7. Trucking theo HWBNO

```sql
SELECT
  tt.HWBNO, tt.TruckNo, tt.DriverName,
  tt.Status, tt.PickupDate, tt.DeliveryDate,
  tt.PickupAddress, tt.DeliveryAddress
FROM Trucking_Track tt
WHERE tt.HWBNO = 'HCM-AIR-001/25'
ORDER BY tt.PickupDate DESC;
```
