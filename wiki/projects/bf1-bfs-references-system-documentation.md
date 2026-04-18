---
title: "BFS - Documentations"
tags:
  - bf1
  - bfs
  - documentation
---

# Documentations - Bộ phận chứng từ

Hướng dẫn chi tiết về các loại chứng từ và quy trình quản lý lô hàng trong hệ thống OF1.

## Mục lục

1. [Express - Chuyên phát nhanh](#1-express---chuyên-phát-nhanh)
2. [Outbound Air - Hàng xuất đường không](#2-outbound-air---hàng-xuất-đường-không)
3. [Inbound Air - Hàng nhập đường không](#3-inbound-air---hàng-nhập-đường-không)
4. [LCL Outbound Sea - Hàng LCL xuất đường biển](#4-lcl-outbound-sea---hàng-lcl-xuất-đường-biển)
5. [LCL Inbound Sea - Hàng LCL nhập đường biển](#5-lcl-inbound-sea---hàng-lcl-nhập-đường-biển)
6. [FCL Outbound Sea - Hàng FCL xuất đường biển](#6-fcl-outbound-sea---hàng-fcl-xuất-đường-biển)
7. [FCL Inbound Sea - Hàng FCL nhập đường biển](#7-fcl-inbound-sea---hàng-fcl-nhập-đường-biển)
8. [Outbound Sea Consol - Hàng consol xuất đường biển](#8-outbound-sea-consol---hàng-consol-xuất-đường-biển)
9. [Inbound Sea Consol - Hàng consol nhập đường biển](#9-inbound-sea-consol---hàng-consol-nhập-đường-biển)
10. [Inland Trucking - Giao nhận nội địa](#10-inland-trucking---giao-nhận-nội-địa)
11. [Logistics - Hàng logistics](#11-logistics---hàng-logistics)
12. [Warehouse Management - Quản lý kho](#12-warehouse-management---quản-lý-kho)
13. [CFS Inbound](#13-cfs-inbound)
14. [OPS Management](#14-ops-management)
15. [Customs Clearance List](#15-customs-clearance-list)
16. [Tracing ETD-ETA-Transit time](#16-tracing-etd-eta-transit-time)
17. [How to change Salesman in file](#17-how-to-change-salesman-in-file)
18. [How to change Partner in file](#18-how-to-change-partner-in-file)
19. [Hướng dẫn Send/Received EDI Local](#19-hướng-dẫn-sendreceived-edi-local)
20. [Hướng dẫn chức năng Task Notes theo File](#20-hướng-dẫn-chức-năng-task-notes-theo-file)
- [Phụ lục A - Các thành phần dùng chung (Section 2-11)](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11)

---

## 1. Express - Chuyên phát nhanh

Mở files quản lý 1 lô hàng chuyên phát nhanh (giá mua, giá bán, ...).

**Cách thực hiện:**
- Chọn `Documentations` > `Express`
- Cách thứ 2: Chọn button `Express` trên thanh công cụ

![Documentation page 3](../attachments/bf1-bfs/documentation/docs_003.png)

---

## 2. Outbound Air - Hàng xuất đường không

### a. Giới thiệu

Nơi chứa các đơn hàng xuất đường không trong vòng 1 tháng.

**Cách thực hiện:**
- Chọn `Documentations` > `Outbound Air`
- Cách thứ 2: Chọn nút `Air Exp` trên thanh công cụ

![Documentation page 4](../attachments/bf1-bfs/documentation/docs_004.png)

**Mã màu trạng thái đơn hàng:**

| Màu | Trạng thái |
|-----|-----------|
| Hồng nhạt | Đã xuất debit, hóa đơn chưa thanh toán |
| Trắng | Chưa nhập giá |
| Đỏ | Thu chi xong hết |
| Xanh nước biển | Gợi ý giá của lô hàng đã đi qua cảng do (để nhập lại lô hàng, không cần nhập giá) |
| Xanh | Xuất hóa đơn, xuất debit hoặc credit (1 trong những tab) |

![Documentation page 5](../attachments/bf1-bfs/documentation/docs_005.png)

### b. Cách tạo và xem chi tiết đơn hàng

Cách tạo 1 đơn hàng xuất hàng không bao gồm các thông tin cần thiết:

| Trường                       | Mô tả                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- |
| Job ID                       | Mã số lô hàng                                                                                           |
| Create                       | Ngày tạo files                                                                                          |
| ETD/ETA                      | Ngày dự kiến đi / Ngày dự kiến đến                                                                      |
| Commodity                    | Loại hàng gì                                                                                            |
| MAWB No.                     | Mã số master airway bill                                                                                |
| Mode                         | Copy (bản sao chép) / Original (bản gốc) / Surrendered (bản để làm surrendered bill)                    |
| Flight No.                   | Mã số chuyến bay, ngày bay                                                                              |
| Shipment                     | 2 loại: Nominated (hàng chỉ định) và Free-hand                                                          |
| B/K No.                      | Mã số booking                                                                                           |
| A.O.L (Airport Of Loading)   | Cảng đi                                                                                                 |
| P.Transit                    | Cảng chuyển tải (nếu có)                                                                                |
| Q'ty/Unit                    | Số lượng / kiện hàng (có 2 loại đơn vị)                                                                 |
| Term                         | Điều kiện của lô hàng                                                                                   |
| Agent                        | Đại lý                                                                                                  |
| Airlines                     | Hãng hàng không phải chỉ trả chi phí                                                                    |
| A.O.D (Airport Of Discharge) | Cảng đến                                                                                                |
| O.P IC                       | Nhân viên OP chịu trách nhiệm lô hàng                                                                   |
| G.W (Gross Weight)           | Khối lượng thực tế                                                                                      |
| C.W (Charge Weight)          | Khối lượng tính phí                                                                                     |
| CBM (Cubic Meter)            | Thể tích lô hàng                                                                                        |
| L*W*H*Q                      | Nhập (Dài * Rộng * Cao * Số lượng), click vào link bên cạnh để hệ thống tự động tính toán G.W, C.W, CBM |
| P.O                          | Số đơn đặt hàng                                                                                         |
| O.Airlines                   | Chi nhánh của hãng hàng không, gửi MBL                                                                  |

![Documentation page 6](../attachments/bf1-bfs/documentation/docs_006.png)

Click vào job cần xem để hiển thị thông tin chi tiết của lô hàng đó.

**Chi tiết HAWB (House Air Way Bill):**

| Trường                   | Mô tả                                                  |
| ------------------------ | ------------------------------------------------------ |
| No.                      | Số thứ tự                                              |
| Customer (Payer/Shipper) | Khách hàng (Người trả chi phí / Người vận chuyển hàng) |
| HAWB                     | Vận đơn của công ty                                    |

Ta có thể kiểm tra vận đơn bằng cách click chọn vào HAWB.

![Documentation page 7](../attachments/bf1-bfs/documentation/docs_007.png)

**Các thao tác trên HAWB:**
- **Save**: Lưu thông tin bill
- **Save As**: Lưu thông tin bill thành số bill mới có nội dung như bill cũ
- **Preview**: Xem trước bill

**HAWB Print Preview:** In các thông số trong vận đơn lên đơn biểu mẫu để xuất ra cho khách hàng.

**(Frame) Print Preview:** In hóa đơn có cả khung biểu mẫu sẵn trên hệ thống.

![Documentation page 8](../attachments/bf1-bfs/documentation/docs_008.png)

![Documentation page 9](../attachments/bf1-bfs/documentation/docs_009.png)

### c. Các công cụ

Các công cụ được truy cập từ nút **More** trên thanh công cụ.

> Các công cụ dùng chung cho tất cả các loại đơn hàng (Section 2-11) được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Outbound Air:**

- **Booking Note**: Nếu không có, hệ thống sẽ hỏi bạn có muốn tạo booking note hay không. Nếu có, click OK hệ thống sẽ mở 1 form để làm booking note. Sau khi điền đầy đủ thông tin, click chọn Save để lưu vào lô hàng.

![Documentation page 11](../attachments/bf1-bfs/documentation/docs_011.png)

- **Invoice Packing List (Agent)**: Xem hóa đơn và danh sách kiện hàng cho đại lý
- **Invoice Packing List (Shipper)**: Xem hóa đơn và kiện hàng gửi cho người vận chuyển
- **ETA reminder date**: Ngày ETA nhắc nhở. Nếu đơn hàng không có ngày ETA thì báo lỗi, nếu có sẽ hiện form cài đặt ngày thông báo đơn hàng chưa đầy đủ thông tin hoặc có trục trặc.

![Documentation page 12](../attachments/bf1-bfs/documentation/docs_012.png)

![Documentation page 13](../attachments/bf1-bfs/documentation/docs_013.png)

- **Shipping Instruction (SI)**: Hướng dẫn vận chuyển đơn hàng (xem chi tiết tại [Phụ lục A - Shipping Instruction](#shipping-instruction-si))

---

## 3. Inbound Air - Hàng nhập đường không

### a. Giới thiệu

Nơi chứa các đơn hàng nhập đường không trong vòng 1 tháng. Tương tự như hàng xuất đường không, hàng nhập cũng có những trường như Outbound Air.

**Cách thực hiện:**
- Chọn `Documentations` > `Inbound Air`
- Cách thứ 2: Chọn nút `Air Imp` trên thanh công cụ

![Documentation page 25](../attachments/bf1-bfs/documentation/docs_025.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Hình bên dưới là tổng hợp các lô hàng trong vòng 1 tháng. Click chọn vào 1 lô hàng để hệ thống hiển thị chi tiết lô hàng đó lên phía trên.

![Documentation page 26](../attachments/bf1-bfs/documentation/docs_026.png)

**Thông tin chính của đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của lô hàng đó hệ thống tự động cấp |
| ETD | Ngày khởi hành dự kiến của lô hàng |
| Carrier/Customer | Người vận chuyển / Khách hàng |
| Agent/Creator | Đại lý / Người tạo files |
| Routing | Lộ trình |
| Qty | Số lượng lô hàng |
| G.W (Gross Weight) | Khối lượng thực tế của lô hàng |
| C.W (Charge Weight) | Khối lượng tính phí |

**Chi tiết HAWB:**

| Trường | Mô tả |
|--------|-------|
| Customer (Payer/Consignee) | Khách hàng (Người trả chi phí / Người nhận hàng) |
| HAWB (House Airways Bill) | Vận đơn hàng không do BEE cung cấp |
| Qty (Quantity) | Số lượng |
| Unit | Đơn vị |
| G.W / C.W / CBM | Khối lượng thực tế / Khối lượng tính phí / Thể tích khối hàng |
| Dest (Destination) | Điểm đến |
| ETD / ETA | Ngày khởi hành dự kiến / Ngày đến dự kiến |
| Salesman | Nhân viên kinh doanh của lô hàng |
| Source | Hàng FREE-HAND hoặc NOMINATED (hàng chỉ định) |

![Documentation page 27](../attachments/bf1-bfs/documentation/docs_027.png)

**Chi tiết HAWB khi click xem:**

![Documentation page 28](../attachments/bf1-bfs/documentation/docs_028.png)

- **Save**: Lưu thông tin
- **Search to Copy**: Sao chép nội dung bill ra 1 bill mới

**Preview Arrival Notice:**
- **Arrival Notice (Original Currency)**: Bản thông báo hàng đến cảng (với tỷ giá gốc)
- **Arrival Notice (Local)**: Bản thông báo hàng đến (tỷ giá trong nước)
- **Arrival Notice (TEL)**: Bản thông báo hàng đến (TEL) - gửi cho bên forwarder chịu trách nhiệm lô hàng

![Documentation page 29](../attachments/bf1-bfs/documentation/docs_029.png)

![Documentation page 30](../attachments/bf1-bfs/documentation/docs_030.png)

![Documentation page 31](../attachments/bf1-bfs/documentation/docs_031.png)

**Preview Authorized Letter:**
- **Authorized Letter (Form 1)**: Thư ủy quyền (bản 1)
- **Authorized Letter (Form 2)**: Thư ủy quyền (bản 2)
- **Authorized Letter (TEL)**: Thư ủy quyền (TEL) - gửi cho co-loader

![Documentation page 32](../attachments/bf1-bfs/documentation/docs_032.png)

![Documentation page 33](../attachments/bf1-bfs/documentation/docs_033.png)

![Documentation page 34](../attachments/bf1-bfs/documentation/docs_034.png)

**Preview Delivery Order:**
- **Delivery Order**: Bản thông báo hàng đến được xuất ra cho khách hàng
- **Document Release Form**: Biên bản giao nhận chứng từ cho khách hàng hoặc người nhận
- **Delivery Order (TEL)**: Biên bản gửi cho bên forwarder chịu trách nhiệm lô hàng

![Documentation page 35](../attachments/bf1-bfs/documentation/docs_035.png)

![Documentation page 36](../attachments/bf1-bfs/documentation/docs_036.png)

![Documentation page 37](../attachments/bf1-bfs/documentation/docs_037.png)

**More Options:**
- **Send Mail**: Gửi thư cho khách hàng, đại lý hoặc co-loader
- **Reset Freight in AN**: Khởi tạo lại nội dung lô hàng trong biên bản thông báo hàng đến
- **Partner Email - Contact**: Địa chỉ email của đối tác liên hệ

![Documentation page 38](../attachments/bf1-bfs/documentation/docs_038.png)

### c. Các công cụ

Tương tự như bên hàng xuất hàng không, hàng nhập đường không cũng có các lựa chọn từ nút **More**.

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Inbound Air:**

- **DO reminder date**: Ngày nhắc nhở in DO để gửi cho khách hàng, đại lý hoặc co-loader

![Documentation page 45](../attachments/bf1-bfs/documentation/docs_045.png)

---

## 4. LCL Outbound Sea - Hàng LCL xuất đường biển

### a. Giới thiệu

Nơi chứa các đơn hàng LCL xuất đường biển.

**Cách thực hiện:**
- Chọn `Documentations` > `LCL Outbound Sea`
- Cách thứ 2: Click chọn nút trên thanh công cụ phía bên trên

![Documentation page 54](../attachments/bf1-bfs/documentation/docs_054.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Ta có thể tạo mới hoặc xem chi tiết của 1 đơn hàng. Nếu ta tạo mới click chọn **New**, hoặc xóa click chọn vào đơn hàng và ấn nút **Delete**, hoặc có thay đổi thông tin đơn hàng thì ấn **Save**, đóng tab click chọn **Close**.

![Documentation page 55](../attachments/bf1-bfs/documentation/docs_055.png)

**Thông tin chính của đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của đơn hàng đó hệ thống tự động cấp |
| ETD | Ngày dự kiến khởi hành |
| Co-loader/Customer | Co-loader / Khách hàng |
| Agent/Creator | Đại lý / Người tạo file |
| POL/POD | Cảng đi / Cảng đến |
| Qty (Quantity) | Số lượng |
| G.W / C.W | Khối lượng thực tế / Khối lượng tính phí |

![Documentation page 56](../attachments/bf1-bfs/documentation/docs_056.png)

**Chi tiết đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| No. | Số booking bên internal booking chuyển qua |
| Booking No. | Số booking note |
| Payer/Shipper | Người chi trả / Người vận chuyển |
| H-B/L | Số house bill |

Ta có thể thay đổi hoặc xem chi tiết số Booking note bằng cách click vào nút.

![Documentation page 57](../attachments/bf1-bfs/documentation/docs_057.png)

**Chi tiết HBL khi click xem:**

![Documentation page 58](../attachments/bf1-bfs/documentation/docs_058.png)

- **Save**: Lưu thông tin HBL đã chính sửa thay đổi

**HBL Preview** (các carrier frame có sẵn cho hàng đường biển):

| Preview | Mô tả |
|---------|-------|
| BEE H-B/L Preview | Bản vận đơn của BEE |
| BEE (Frame) H-B/L Preview | Bản vận đơn của BEE có khung |
| BSL (Frame) H-B/L Preview | Vận đơn của BSL có khung |
| CRW (Frame) H-B/L Preview | Vận đơn của CRW có khung |
| EVR (Frame) H-B/L Preview | Vận đơn của EVR có khung |
| PLI (Frame) H-B/L Preview | Vận đơn của PLI có khung |
| RMI (Frame) H-B/L Preview | Vận đơn của RMI có khung |
| Nankai H-B/L Preview | Vận đơn của Nankai |
| Nankai (Frame) H-B/L Preview | Vận đơn của Nankai có khung |
| AGL H-B/L Preview | Vận đơn của AGL |
| AGL (Frame) H-B/L Preview | Vận đơn của AGL có khung |
| Nankai Express H-B/L Preview | Vận đơn hàng xuất của Nankai |
| Nankai Express (Frame) H-B/L Preview | Vận đơn hàng xuất của Nankai có khung |
| BEE-DN H-B/L Preview Drafts | Vận đơn bản nhập cho BEE Đà Nẵng |
| BEE H-B/L Preview (DN) | Vận đơn cho BEE Đà Nẵng |

![Documentation page 59](../attachments/bf1-bfs/documentation/docs_059.png)

![Documentation page 60](../attachments/bf1-bfs/documentation/docs_060.png)

**Các thao tác khác trên HBL:**
- **HBL Form Setup**: Cài đặt bản vận đơn
- **Search to Copy**: Sao chép 1 bill
- **Loading confirm**: Xác nhận đã làm vận đơn với khách hàng hoặc đại lý
- **Telex Release**: Điền giao hàng để thuận tiện giao nhận hàng

![Documentation page 61](../attachments/bf1-bfs/documentation/docs_061.png)

![Documentation page 62](../attachments/bf1-bfs/documentation/docs_062.png)

**More Options:**
- **Insurance**: Bảo hiểm đơn hàng
- **Extract E-Manifest**: Xuất dữ liệu ra bản kê khai điện tử
- **Send Mail**: Gửi thư cho khách hàng hay đại lý
- **Show/Hide Signature Box**: Mở/Đóng cho chữ ký số
- **Show/Hide Detail**: Mở/Đóng chi tiết hàng
- **Show Separate HBL**: Hiển thị tách rời số house bill
- **Show Separate HBL Combine**: Hiển thị tách rời số house bill đã gộp
- **Show Attach List**: Hiển thị danh sách các file đính kèm
- **Preview Attach List**: In ra bản các file đính kèm
- **Partner Email - Contact**: Liên hệ email của đối tác
- **Update CTNR Info to Master File**: Cập nhật thông tin container lên tập tin chính

![Documentation page 63](../attachments/bf1-bfs/documentation/docs_063.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho LCL Outbound Sea:**

- **Export Data**: Xuất dữ liệu ra file .xml. Có 2 dạng:
  - Export file EDI in Local: Xuất dữ liệu file EDI trong nội bộ văn phòng
  - Export file EDI in Public: Xuất dữ liệu file EDI tất cả các văn phòng có thể sử dụng được

- **Cargo Manifest** (có thêm các thao tác):
  - Save: Lưu thông tin bảng kê hàng hóa
  - Print: In thông tin bảng kê hàng hóa
  - E Manifest: Xuất thông tin bảng kê hàng hóa thành bảng kê điện tử
  - More Options > Send Mail: Gửi thư cho khách hàng hoặc đại lý

![Documentation page 67](../attachments/bf1-bfs/documentation/docs_067.png)

- **Invoice and Packing List (Agent)**: Hóa đơn và danh sách đơn hàng (gửi cho đại lý)
- **Invoice and Packing List (Shipper)**: Hóa đơn và danh sách đơn hàng (gửi cho shipper)
- **ETA reminder date**: Ngày nhắc nhở ETA
- **Shipping Instruction (SI)**: Hướng dẫn vận chuyển đơn hàng (xem chi tiết tại [Phụ lục A - Shipping Instruction](#shipping-instruction-si))

![Documentation page 68](../attachments/bf1-bfs/documentation/docs_068.png)

**Điểm khác biệt:**
- **Other Credit** có thêm trường **S.S.P (Share Sales Profit)**: Chỉ dùng cho Other Credit (Hàng LCL và hàng Consol). Khi ta chọn agent thuộc group mà ta handle hàng, ta phải trả handling cho agent thuộc group của mình, nhưng handling đó sẽ được tích chọn S.S.P. Khi ta tích chọn thì cost đó sẽ không bị tính cho salesman đó và profit của salesman đó sẽ nhiều hơn.

---

## 5. LCL Inbound Sea - Hàng LCL nhập đường biển

### a. Giới thiệu

Nơi chứa tất cả các đơn hàng nhập đường biển trong vòng 1 tháng.

**Cách thực hiện:**
- Chọn `Documentations` > `LCL Inbound Sea`
- Cách thứ 2: Click chọn nút `LCL Imp` trên thanh công cụ

![Documentation page 78](../attachments/bf1-bfs/documentation/docs_078.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Ta có thể thêm sửa xóa 1 đơn hàng bằng cách click chọn nút **New** để tạo mới, **Delete** để xóa và **Save** để lưu thông tin đơn hàng, **Close** để đóng lại.

![Documentation page 79](../attachments/bf1-bfs/documentation/docs_079.png)

**Thông tin chính của đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của file đó hệ thống tự động cấp |
| ETA | Ngày dự kiến hàng đến nơi |
| Shipping Lines/Customer | Dây chuyền vận chuyển / Khách hàng |
| Agent/Creator | Đại lý / Người tạo file |
| POL/POD | Cảng đi / Cảng đến |
| Container(s) | Số container |
| Qty / G.W / CBM | Số lượng / Khối lượng thực tế / Thể tích khối |

**Chi tiết đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| No. | Số lô hàng |
| Customer (Consignee/Payer) | Khách hàng |
| H-B/L | Số house bill của lô hàng |

Ta có thể xem chi tiết số house bill bằng cách click chọn vào nút kế bên house bill.

![Documentation page 80](../attachments/bf1-bfs/documentation/docs_080.png)

**Chi tiết HBL khi click xem:**
- **Save**: Lưu thông tin số house bill
- **Search to Copy**: Sao chép 1 bill
- **Local Charges**: Default (mặc định), Reset Freight Charges in AN (tạo mới lại phụ phí hàng trong thông báo hàng đến)
- **E-Manifest**: House bill of lading / Goods Declaration / Dangerous Goods

![Documentation page 81](../attachments/bf1-bfs/documentation/docs_081.png)

**Print Preview** (các loại preview cho hàng nhập):
- **Arrival Notice (Original Currency)**: Thông báo hàng đến (tỷ giá gốc)
- **Arrival Notice (LC Currency)**: Thông báo hàng đến (tỷ giá của khu vực)
- **Arrival Notice TEL**: Thông báo hàng đến bằng điện tử
- **A/N Print Setup**: Cài đặt in thông báo hàng đến

![Documentation page 82](../attachments/bf1-bfs/documentation/docs_082.png)

![Documentation page 83](../attachments/bf1-bfs/documentation/docs_083.png)

![Documentation page 84](../attachments/bf1-bfs/documentation/docs_084.png)

**Delivery Order:**
- **Authorized Letter Print Preview**: Xem thư thư ủy quyền
- **D/O Print Preview**: Xem thư biên bản giao nhận hàng
- **D/O (Without-letter-head) Print Preview**: Xem thư biên bản giao nhận hàng (không có tiêu đề)
- **RMI-D/O Print Preview**: Xem thư biên bản giao nhận hàng của RMI
- **Authorized Letter TEL**: Thư ủy quyền dạng bản điện tử
- **D/O Print Setup**: Cài đặt cách in bản giao nhận hàng
- **Print Preview Attached Sheet**: Xem thư bản kê có file đi kèm
- **Print Preview Proof of Delivery**: Xem thư bản in có bằng chứng đã giao hàng

![Documentation page 85](../attachments/bf1-bfs/documentation/docs_085.png)

![Documentation page 86](../attachments/bf1-bfs/documentation/docs_086.png)

![Documentation page 87](../attachments/bf1-bfs/documentation/docs_087.png)

![Documentation page 88](../attachments/bf1-bfs/documentation/docs_088.png)

![Documentation page 89](../attachments/bf1-bfs/documentation/docs_089.png)

![Documentation page 90](../attachments/bf1-bfs/documentation/docs_090.png)

![Documentation page 91](../attachments/bf1-bfs/documentation/docs_091.png)

**More Options:**
- **Send Mail**: Gửi thư
- **Partner Email - Contact**: Email liên hệ đối tác
- **Update CTNR Info to Master File**: Cập nhật thông tin container vào tập tin chủ

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho LCL Inbound Sea:**

- **Import file from EDI**:
  - CMS EDI file: Số file EDI của CMS
  - BEE EDI file: Số file EDI của BEE

![Documentation page 98](../attachments/bf1-bfs/documentation/docs_098.png)

**Điểm khác biệt:**
- **Other Credit** có thêm trường **S.S.P (Share Sales Profit)**: Tương tự như [LCL Outbound Sea](#4-lcl-outbound-sea---hàng-lcl-xuất-đường-biển).

---

## 6. FCL Outbound Sea - Hàng FCL xuất đường biển

### a. Giới thiệu

Nơi chứa các đơn hàng FCL xuất đường biển.

**Cách thực hiện:**
- Chọn `Documentations` > `FCL Outbound Sea`
- Cách thứ 2: Click chọn nút trên thanh công cụ phía bên trên

![Documentation page 103](../attachments/bf1-bfs/documentation/docs_103.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Tương tự như [LCL Outbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-2). Bao gồm các trường: Job ID, ETD, Co-loader/Customer, Agent/Creator, POL/POD, Qty, G.W, C.W.

Chi tiết đơn hàng có: No., Booking No., Payer/Shipper, H-B/L.

HBL Preview có tất cả các carrier frame như [LCL Outbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-2) (BEE, BSL, CRW, EVR, PLI, RMI, Nankai, AGL).

![Documentation page 104](../attachments/bf1-bfs/documentation/docs_104.png)

![Documentation page 105](../attachments/bf1-bfs/documentation/docs_105.png)

![Documentation page 106](../attachments/bf1-bfs/documentation/docs_106.png)

![Documentation page 107](../attachments/bf1-bfs/documentation/docs_107.png)

![Documentation page 108](../attachments/bf1-bfs/documentation/docs_108.png)

![Documentation page 109](../attachments/bf1-bfs/documentation/docs_109.png)

![Documentation page 110](../attachments/bf1-bfs/documentation/docs_110.png)

![Documentation page 111](../attachments/bf1-bfs/documentation/docs_111.png)

![Documentation page 112](../attachments/bf1-bfs/documentation/docs_112.png)

![Documentation page 113](../attachments/bf1-bfs/documentation/docs_113.png)

![Documentation page 114](../attachments/bf1-bfs/documentation/docs_114.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho FCL Outbound Sea:**

- **Shipping Instruction (SI)**: Hướng dẫn vận chuyển đơn hàng (xem chi tiết tại [Phụ lục A - Shipping Instruction](#shipping-instruction-si))
- **Invoice and Packing List (Agent)**: Hóa đơn và danh sách đơn hàng (gửi cho đại lý)
- **Invoice and Packing List (Shipper)**: Hóa đơn và danh sách đơn hàng (gửi cho shipper)
- **ETA reminder date**: Ngày nhắc nhở ETA

![Documentation page 118](../attachments/bf1-bfs/documentation/docs_118.png)

![Documentation page 119](../attachments/bf1-bfs/documentation/docs_119.png)

---

## 7. FCL Inbound Sea - Hàng FCL nhập đường biển

### a. Giới thiệu

Nơi chứa tất cả các đơn hàng FCL nhập đường biển trong vòng 1 tháng.

**Cách thực hiện:**
- Chọn `Documentations` > `FCL Inbound Sea`
- Cách thứ 2: Click chọn nút `FCL Imp` trên thanh công cụ

![Documentation page 128](../attachments/bf1-bfs/documentation/docs_128.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Tương tự như [LCL Inbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-3). Bao gồm các trường: Job ID, ETA, Shipping Lines/Customer, Agent/Creator, POL/POD, Container(s), Qty, G.W, CBM.

Chi tiết đơn hàng có: No., Customer (Consignee/Payer), H-B/L.

HBL có đầy đủ Arrival Notice, Authorized Letter, Delivery Order như [LCL Inbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-3).

![Documentation page 129](../attachments/bf1-bfs/documentation/docs_129.png)

![Documentation page 130](../attachments/bf1-bfs/documentation/docs_130.png)

![Documentation page 131](../attachments/bf1-bfs/documentation/docs_131.png)

![Documentation page 132](../attachments/bf1-bfs/documentation/docs_132.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho FCL Inbound Sea:**

- **Cargo Manifest**: Bảng kê hàng hóa. Hệ thống sẽ hiển thị ra form để in bảng kê theo hình thức nào:
  - Attached Sheet / Cargo Manifest: Gắn các file đi kèm với bảng kê
  - Extract to E-Manifest: Xuất ra bảng kê điện tử
  - Preview: In ra bản mẫu xem thử
  - Cancel: Hủy

- **Import file from EDI**:
  - CMS EDI file: Số file EDI của CMS
  - BEE EDI file: Số file EDI của BEE

![Documentation page 138](../attachments/bf1-bfs/documentation/docs_138.png)

![Documentation page 139](../attachments/bf1-bfs/documentation/docs_139.png)

---

## 8. Outbound Sea Consol - Hàng consol xuất đường biển

### a. Giới thiệu

Nơi chứa tất cả hàng xuất consol đường biển.

**Cách thực hiện:**
- Chọn `Documentations` > `Outbound Sea Consol`
- Cách thứ 2: Click chọn nút trên thanh công cụ phía bên trên

![Documentation page 143](../attachments/bf1-bfs/documentation/docs_143.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Tương tự như [LCL Outbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-2). Bao gồm các trường: Job ID, ETD, Co-loader/Customer, Agent/Creator, POL/POD, Qty, G.W, C.W.

Chi tiết đơn hàng có: No., Booking No., Payer/Shipper, H-B/L.

**Booking Note có thêm các thao tác:**
- **New Booking**: Tạo 1 booking note mới
- **Save**: Lưu những thay đổi trên booking note
- **Preview**: Để in bản mẫu booking note
- **Search**: Tìm kiếm booking note
- **Remove Booking**: Gỡ bỏ booking note ra khỏi đơn hàng
- **Move to...**: Chuyển tới đơn hàng nào
- **Reset**: Làm mới
- **Send Request**: Gửi yêu cầu
- **Close**: Đóng lại

![Documentation page 145](../attachments/bf1-bfs/documentation/docs_145.png)

![Documentation page 146](../attachments/bf1-bfs/documentation/docs_146.png)

HBL Preview có tất cả các carrier frame như [LCL Outbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-2).

![Documentation page 147](../attachments/bf1-bfs/documentation/docs_147.png)

![Documentation page 148](../attachments/bf1-bfs/documentation/docs_148.png)

![Documentation page 149](../attachments/bf1-bfs/documentation/docs_149.png)

![Documentation page 150](../attachments/bf1-bfs/documentation/docs_150.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Outbound Sea Consol:**

- **Shipping Instruction (SI)**: Hướng dẫn vận chuyển đơn hàng (xem chi tiết tại [Phụ lục A - Shipping Instruction](#shipping-instruction-si))
- **Export Data**: Có 2 dạng: Export file EDI in Local / Export file EDI in Public
- **Invoice and Packing List (Agent/Shipper)**: Hóa đơn và danh sách đơn hàng
- **ETA reminder date**: Ngày nhắc nhở ETA

![Documentation page 155](../attachments/bf1-bfs/documentation/docs_155.png)

![Documentation page 156](../attachments/bf1-bfs/documentation/docs_156.png)

**Điểm khác biệt:**
- **Other Credit** có thêm trường **S.S.P (Share Sales Profit)**: Tương tự như [LCL Outbound Sea](#4-lcl-outbound-sea---hàng-lcl-xuất-đường-biển).

---

## 9. Inbound Sea Consol - Hàng consol nhập đường biển

### a. Giới thiệu

Nơi chứa các đơn hàng hàng nhập đường biển consol.

**Cách thực hiện:**
- Chọn `Documentations` > `Inbound Sea Consol`
- Cách thứ 2: Click chọn nút `CSL Imp` trên thanh công cụ

![Documentation page 166](../attachments/bf1-bfs/documentation/docs_166.png)

**Mã màu trạng thái:** Tương tự như [Outbound Air](#a-giới-thiệu).

### b. Cách tạo và xem chi tiết đơn hàng

Tương tự như [LCL Inbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-3).

**Thông tin chính của đơn hàng (phần trên):**

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của đơn hàng đó hệ thống tự động cấp |
| Created/ETA | Ngày tạo file / Ngày dự kiến đến nơi |
| M-B/L No. | Số master bill |
| P.O.L (Port of Loading) | Cảng đi |
| P.O.D (Port of Discharge) | Cảng đến |
| ETD | Ngày dự kiến khởi hành |
| F/N | FREE-HAND hoặc NOMINATED |
| O.P IC | Nhân viên hiện trường chịu trách nhiệm đơn hàng |
| S.CName (Source Name) | Nơi gửi hàng |
| Vessel | Hãng tàu |
| Packages | Kiện hàng |
| Unit | Đơn vị |
| Commodity | Loại mặt hàng |
| Service | Loại dịch vụ |
| ETA/T.S | Ngày dự kiến đến nơi / Cảng chuyển tải |
| ETD/T.S | Ngày dự kiến khởi hành / Cảng chuyển tải |
| S.Lines (Shipping Lines) | Dây chuyền vận chuyển |
| Agent | Đại lý |
| Voyage | Lộ trình |
| Delivery | Nơi giao hàng |
| G.W / CBM | Khối lượng thực tế / Thể tích khối |
| Notes | Ghi chú đơn hàng |

![Documentation page 167](../attachments/bf1-bfs/documentation/docs_167.png)

**Bảng dưới là tổng hợp các đơn hàng nhập đường biển consol trong 1 tháng:** Job ID, ETA, Shipping Lines/Customer, Agent/Creator, POL/POD, Container(s), Qty, G.W, CBM.

![Documentation page 168](../attachments/bf1-bfs/documentation/docs_168.png)

Chi tiết đơn hàng có: No., Customer (Consignee/Payer), H-B/L.

HBL có đầy đủ Arrival Notice, Authorized Letter, Delivery Order như [LCL Inbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-3).

![Documentation page 169](../attachments/bf1-bfs/documentation/docs_169.png)

![Documentation page 170](../attachments/bf1-bfs/documentation/docs_170.png)

![Documentation page 171](../attachments/bf1-bfs/documentation/docs_171.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Inbound Sea Consol:**

- **Export file**: Xuất dữ liệu ra file .xml.
  - Excel File Template of CFS Storage: Xuất file để làm bảng kê danh mục hàng hóa nhập khẩu số vào CFS
  - Letter of CFS Storage: Bản thư gửi cho kho CFS
  - Export to excel for import to BEE storage: Xuất dữ liệu ra file excel để nhập vào hệ thống kho của BEE
  - Export Bee EDI in Public: Xuất file ra .xml để lưu trữ dữ liệu

![Documentation page 175](../attachments/bf1-bfs/documentation/docs_175.png)

![Documentation page 176](../attachments/bf1-bfs/documentation/docs_176.png)

- **Import file from EDI**: CMS EDI file / BEE EDI file

![Documentation page 178](../attachments/bf1-bfs/documentation/docs_178.png)

**Điểm khác biệt:**
- **Other Credit** có thêm trường **S.S.P (Share Sales Profit)**: Tương tự như [LCL Outbound Sea](#4-lcl-outbound-sea---hàng-lcl-xuất-đường-biển).

---

## 10. Inland Trucking - Giao nhận nội địa

### a. Giới thiệu

Nơi chứa các đơn hàng cần dịch vụ giao nhận nội địa.

**Cách thực hiện:**
- Chọn `Documentations` > `Inland Trucking`

![Documentation page 183](../attachments/bf1-bfs/documentation/docs_183.png)

### b. Cách tạo và xem chi tiết đơn hàng

Ta có thể thêm sửa xóa 1 đơn hàng bằng cách click chọn nút **New** để tạo mới, **Delete** để xóa và **Save** để lưu thông tin đơn hàng, **Close** để đóng lại.

**Thông tin chính (đặc thù cho Inland Trucking):**

| Trường | Mô tả |
|--------|-------|
| Job No. | Số job đó hệ thống tự động cấp |
| T/K Date | Ngày trucking |
| Vendor | Người cho thuê xe vận chuyển |
| Invoice No. | Số hóa đơn |
| Service | Loại dịch vụ |
| P/K At | Lấy hàng tại |
| Destination | Điểm đến |
| Truck No. | Số xe |
| Delivery | Ngày giao hàng |
| Notes | Ghi chú |

![Documentation page 184](../attachments/bf1-bfs/documentation/docs_184.png)

**Chi tiết đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| No. | Số đơn hàng |
| Customer (Payer) | Khách hàng (Người chi trả) |
| HBL No | Số house bill |

Ta có thể xem chi tiết số house bill hoặc chính sửa bằng cách click vào nút bên cạnh.

![Documentation page 185](../attachments/bf1-bfs/documentation/docs_185.png)

HBL Preview có tất cả các carrier frame như [LCL Outbound Sea](#b-cách-tạo-và-xem-chi-tiết-đơn-hàng-2) (BEE, BSL, CRW, EVR, PLI, RMI, Nankai, AGL). Có thêm Loading confirm và Telex Release.

![Documentation page 186](../attachments/bf1-bfs/documentation/docs_186.png)

![Documentation page 187](../attachments/bf1-bfs/documentation/docs_187.png)

**More Options:** Insurance, Extract E-Manifest, Send Mail, Show/Hide Signature Box, Show/Hide Detail, Show Separate HBL, Show Separate HBL Combine, Show Attach List, Preview Attach List, Partner Email - Contact, Update CTNR Info to Master File.

![Documentation page 188](../attachments/bf1-bfs/documentation/docs_188.png)

![Documentation page 189](../attachments/bf1-bfs/documentation/docs_189.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Inland Trucking:**

- **ETA reminder config**: Ngày nhắc nhở ETA

![Documentation page 193](../attachments/bf1-bfs/documentation/docs_193.png)

---

## 11. Logistics - Hàng logistics

### a. Giới thiệu

Nơi chứa tất cả các hàng logistics.

**Cách thực hiện:**
- Chọn `Documentations` > `Logistics`
- Cách thứ 2: Click chọn nút `Logistics` trên thanh công cụ

![Documentation page 197](../attachments/bf1-bfs/documentation/docs_197.png)

### b. Cách tạo và xem chi tiết đơn hàng

Ta có thể thêm sửa xóa 1 đơn hàng bằng cách click chọn nút **New** để tạo mới, **Delete** để xóa và **Save** để lưu thông tin đơn hàng, **Close** để đóng lại.

![Documentation page 198](../attachments/bf1-bfs/documentation/docs_198.png)

**Thông tin chính của đơn hàng:**

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của file đó hệ thống tự động cấp |
| ETD | Ngày dự kiến khởi hành |
| Fleat/Customer | Nhà cung cấp / Khách hàng |
| MBL | Số master bill |
| Q'ty (Quantity) | Số lượng |
| CTNS | Đơn vị hàng |
| G.W / CBM | Khối lượng thực tế / Thể tích khối |
| Custom No. | Mã số khách hàng |
| Port Name | Tên cảng |
| Invoice No. | Số hóa đơn |
| Service | Dịch vụ |

![Documentation page 199](../attachments/bf1-bfs/documentation/docs_199.png)

**Chi tiết đơn hàng (đặc thù cho Logistics):**

| Trường | Mô tả |
|--------|-------|
| No. | Số lô hàng |
| CDS/INS/ROUTE/W.H | Mã khách hàng |
| Customer (Payer) | Khách hàng (Người chi trả) |
| HBL (HAWB) | Vận đơn house bill |
| Extra CDS (Credit Default Swap) | Hoán vị rủi ro tín dụng |
| Delivery Place | Nơi giao hàng (có thể chính sửa bằng cách click vào nút bên cạnh) |
| Transfer | Ngày chuyển khoản |
| Signed | Ngày ký xác nhận |
| Regist | Ngày đăng ký |
| Inspection | Ngày kiểm duyệt |
| Delivery | Ngày giao |
| Salesman | Nhân viên kinh doanh chịu trách nhiệm đơn hàng |
| CDS Edit | Chính sửa hoán vị rủi tín dụng |
| S.Service (Shipping Service) | Dịch vụ vận chuyển |
| Quotation No. | Số báo cáo |
| Notes | Ghi chú |
| Link HBL | Đường link của vận đơn house bill |

![Documentation page 200](../attachments/bf1-bfs/documentation/docs_200.png)

**HBL chi tiết:** Tương tự như các loại inbound (có Arrival Notice, Authorized Letter, Delivery Order, các loại preview).

![Documentation page 201](../attachments/bf1-bfs/documentation/docs_201.png)

![Documentation page 202](../attachments/bf1-bfs/documentation/docs_202.png)

![Documentation page 203](../attachments/bf1-bfs/documentation/docs_203.png)

![Documentation page 204](../attachments/bf1-bfs/documentation/docs_204.png)

### c. Các công cụ

> Các công cụ dùng chung được mô tả chi tiết tại [Phụ lục A](#phụ-lục-a---các-thành-phần-dùng-chung-section-2-11).

**Các công cụ đặc thù cho Logistics:**

- **Handle Instruction**: Hướng dẫn làm hàng
  - Save: Lưu thông tin
  - Send Information to OP: Gửi thông tin đến nhân viên hiện trường
  - Delete: Xóa thông tin
  - Close: Đóng lại
- **Send request handle shipment info**: Gửi thông tin hướng dẫn làm hàng đến 1 user nào đó

![Documentation page 208](../attachments/bf1-bfs/documentation/docs_208.png)

---

## 12. Warehouse Management - Quản lý kho

Nơi quản lý các đơn hàng xuất nhập kho.

**Cách thực hiện:**
- Chọn `Documentations` > `Warehouse Management`

![Documentation page 212](../attachments/bf1-bfs/documentation/docs_212.png)

Ta có thể xem dữ liệu các lô hàng xuất nhập kho bằng cách chọn ngày tháng năm cần xem.

**Mã màu trạng thái:**

| Màu | Trạng thái |
|-----|-----------|
| Xanh | Đã thanh toán và xuất hàng ra khỏi kho |
| Cam | Đã xuất debit hoặc credit và vẫn chưa thanh toán hết với kho |
| Trắng | Mới nhập vào kho |

Sau khi nhập xong hoặc chọn ngày xong ta click chọn nút **Apply** để hệ thống lọc dữ liệu và xuất ra bảng bên dưới.

**Các thao tác:**
- **Add new**: Thêm phiếu kho
- **Delete**: Xóa 1 phiếu
- **Close**: Đóng tab lại

Ta có thể xem chi tiết 1 phiếu bằng cách double click vào phiếu đó.

![Documentation page 213](../attachments/bf1-bfs/documentation/docs_213.png)

**Chi tiết phiếu kho:**
- **New**: Tạo mới 1 phiếu kho
- **Save**: Lưu thông tin phiếu kho
- **Create File**: Tạo file từ phiếu kho
- **Delete**: Xóa phiếu đang mở
- **Make Payment**: Làm phiếu chi trả hàng
- **Close**: Đóng lại

---

## 13. CFS Inbound

Nơi quản lý hóa đơn lưu kho. Sau đó đẩy hóa đơn qua cho kế toán.

**Cách thực hiện:**
- Chọn `Documentations` > `CFS Inbound`

Sau khi đã xuất lô hàng ra cho khách hàng, các phiếu hóa đơn kho sẽ được lưu trữ ở đây và được đẩy qua cho kế toán để làm công nợ đối với khách hàng đó.

![Documentation page 214](../attachments/bf1-bfs/documentation/docs_214.png)

---

## 14. OPS Management

Nơi ủy quyền cho user thực hiện chính sửa file hoặc chứng từ.

**Cách thực hiện:**
- Chọn `Documentations` > `OPS Management`

![Documentation page 215](../attachments/bf1-bfs/documentation/docs_215.png)

**Các trường tìm kiếm:**
- **Job No.**: Số job của file được hệ thống tự động cấp
- **Requester**: Người yêu cầu
- **Approved by**: Được chấp thuận bởi
- **Approved**: Chấp thuận
- **From/To**: Từ ngày / Đến ngày
- **Mode**: Theo loại

Sau đó click chọn nút **Apply** hệ thống sẽ hiển thị dữ liệu ra bảng bên dưới và chi tiết của từng file sẽ hiển thị ở Details.

Ta có thể tạo mới bằng cách click chọn nút **New**, sau đó điền các thông tin tương ứng như yêu cầu chính sửa giải trình, tạm ứng, file, ... Sau khi điền đầy đủ thông tin theo các trường tương ứng ở bảng Details, click chọn nút **Save** để lưu thông tin và hệ thống tự động gửi request đó tới người được nhận ở phần Receiver.

---

## 15. Customs Clearance List

Nơi lưu trữ số tờ khai quan với hải quan.

**Cách thực hiện:**
- Chọn `Documentations` > `Customs Clearance List`

![Documentation page 216](../attachments/bf1-bfs/documentation/docs_216.png)

Ta có thể lọc dữ liệu bằng cách chọn ngày tháng năm hoặc có số file, tên khách hàng để ta tìm kiếm. Sau đó click chọn **Apply**, hệ thống sẽ hiển thị dữ liệu ở bảng bên dưới.

**Các trường dữ liệu:**

| Trường | Mô tả |
|--------|-------|
| ID | Số ID do hệ thống tự động cấp |
| Regist | Ngày đăng ký |
| CDS No. | Số chứng từ hải quan |
| Type | Loại |
| Measure | Độ lượng |
| CDS Officer | Văn phòng làm hợp đồng |
| Shipper | Người vận chuyển |
| Consignee | Người nhận hàng |
| Creator | Người tạo files |
| Job No. | Số Job do hệ thống tự động cấp cho từng đơn hàng riêng |
| Service Type | Loại dịch vụ |

---

## 16. Tracing ETD-ETA-Transit time

Nơi chứa các cảnh báo theo ngày cài đặt của đơn hàng do. Các cảnh báo phải để trước 2 ngày so với ngày ETD/ETA để làm tracing báo với hãng tàu.

Giúp kiểm tra lô hàng còn sót, liệt kê các files trước 2 ngày để coi hàng hóa sẽ đến để báo cáo, theo dõi lô hàng. Có thể thêm nội dung tracing, sau khi cập nhật sẽ gửi mail để kiểm tra lô hàng.

![Documentation page 217](../attachments/bf1-bfs/documentation/docs_217.png)

---

## 17. How to change Salesman in file

![Documentation page 218](../attachments/bf1-bfs/documentation/docs_218.png)

**Trường hợp 1: Đối với file chưa nhập giá, chưa có salesman**

Click vào nút bên cạnh ở Salesman. Hệ thống sẽ hiển thị ra bảng Contact List, tìm kiếm salesman chính thức của lô hàng và click chọn.

**Trường hợp 2: Đã nhập giá, có salesman và muốn đổi qua salesman khác**

- Bước 1: Tương tự như trường hợp 1
- Bước 2: Hệ thống sẽ tự động request tới salesman hiện tại của lô hàng đã nhập giá. Lúc ta request xong thì trên phần mềm của salesman đó sẽ hiển thị thông báo, nếu họ cho đổi salesman khác thì họ click vào approve. Sau đó ta mới có thể đổi thành salesman khác được.

Nếu salesman của lô hàng đó là Văn phòng thì request đó sẽ được gửi tới admin của văn phòng đó. Admin xem xét nếu đồng ý thì approve, ngược lại denied request đó.

---

## 18. How to change Partner in file

![Documentation page 219](../attachments/bf1-bfs/documentation/docs_219.png)

**Trường hợp 1: Đối với file chưa làm SM (Settlement) và đã làm SM nhưng chưa được duyệt**

Click chọn vào nút như hình bên dưới. Hệ thống sẽ hiển thị 1 form bao gồm tất cả khách hàng của văn phòng đó, chọn khách hàng đúng, save file và báo lại cho nhân viên OP, Salesman về sự thay đổi khách hàng.

**Trường hợp 2: File đã làm SM và đã được duyệt**

- Bước 1: Thực hiện tương tự như trường hợp bên trên, hệ thống sẽ hiển thị 1 form request thay đổi khách hàng đến kế toán trưởng của từng văn phòng sẽ approve.
- Bước 2: Click chọn nút "Send" để gửi thông báo đến kế toán trưởng của từng văn phòng. Nhân viên thực hiện có nhiệm vụ phải thông báo đến các kế toán trưởng văn để nay để được giải quyết sớm nhất. Các kế toán trưởng có thể duyệt trực tiếp từ phần mềm ở phần thông báo phía trên. Sau khi approve xong hệ thống sẽ tự động cập nhật khách hàng mới vào file đó và cả SM (Settlement).

---

## 19. Hướng dẫn Send/Received EDI Local

### Gửi EDI

![Documentation page 220](../attachments/bf1-bfs/documentation/docs_220.png)

1. Chọn file cần gửi EDI > More > Export Data > Send EDI in Local Office
2. Sẽ xuất hiện màn hình các văn phòng chi nhánh. Chọn văn phòng chi nhánh cần gửi EDI đến. Double click vào để chọn văn phòng cần gửi.
3. Sẽ xuất hiện màn hình nhập địa chỉ email của người nhận (mặc định sẽ lấy địa chỉ email đã cài đặt sẵn). Mục đích là thông báo cho người nhận biết được có EDI shipment được gửi đến.
4. Nhập địa chỉ email khác vào nếu cần. Có thể gửi đến nhiều email, mỗi email cách nhau bằng dấu chấm phẩy.
5. Bấm OK để thực hiện.

![Documentation page 221](../attachments/bf1-bfs/documentation/docs_221.png)

Sau khi gửi thành công sẽ xuất hiện thông báo. Lúc này hệ thống sẽ gửi thông tin EDI của shipment tới nguồn dữ liệu của văn phòng chi nhánh được chọn.

### Nhận EDI

Người nhận sẽ nhận được email thông báo. Sau khi nhận được email, người dùng sẽ nhận EDI bằng cách:

1. Vào chức năng `Tools` > `Create Shipment From Local EDI`
2. Sẽ xuất hiện danh sách EDI
3. Double click vào dòng EDI cần tạo file, sẽ xuất hiện màn hình thông tin shipment EDI
4. Thực hiện điền thông tin phù hợp cho shipment rồi bấm **Save** để tạo file

---

## 20. Hướng dẫn chức năng Task Notes theo File

![Documentation page 222](../attachments/bf1-bfs/documentation/docs_222.png)

### Xem danh sách công việc

Để xem danh sách công việc cần thực hiện của 1 quy trình file:

1. Chọn file và HBL cần xem
2. Bấm vào nút "Show Task" trên thanh công cụ
3. Sẽ xuất hiện màn hình công việc. Danh sách công việc này đã được cài đặt sẵn theo chức năng nghiệp vụ của từng bộ phận.

### Phân loại công việc

- **Màu chữ đen**: Những công việc không cần gửi mail thông báo đến khách hàng. Sau khi thực hiện xong công việc thì user tick vào cột "Done" của dòng công việc tương ứng. Hệ thống sẽ ghi nhận thông tin người dùng tick "Done" lại. Nếu có ghi chú gì thì cần nhập ghi chú trước khi tick "Done".

- **Màu chữ cam**: Những công việc sau khi hoàn thành sẽ có gửi mail thông báo đến khách hàng. Để thực hiện gửi mail thì double vào tên công việc cần gửi mail, sau đó sẽ xuất hiện màn hình gửi mail đã được điền sẵn thông tin theo form mẫu tương ứng với từng loại thông báo. Có thể chính sửa lại thông tin và email, sau đó bấm **Send**.

![Documentation page 223](../attachments/bf1-bfs/documentation/docs_223.png)

![Documentation page 224](../attachments/bf1-bfs/documentation/docs_224.png)

Sau khi gửi xong thì hệ thống sẽ tick "Done" công việc này. Để xem lại nội dung email đã gửi thì double vào công việc đó.

### Tự động tick Done

Một số công việc sẽ tự động tick "Done" sau khi người dùng thực hiện các chức năng trên file như:
- Tick "Finish" file
- Export manifest
- Send Pre-alert
- Request collect documents

---

## Phụ lục A - Các thành phần dùng chung (Section 2-11)

Các công cụ và trường thông tin dưới đây được sử dụng chung cho tất cả các loại đơn hàng từ Section 2 đến Section 11. Mỗi section chỉ có thêm một số đặc thù riêng được ghi chú tại phần tương ứng.

### Print Preview

![Documentation page 9](../attachments/bf1-bfs/documentation/docs_009.png)

In biểu mẫu đơn hàng. Các trường lọc:

| Trường | Mô tả |
|--------|-------|
| Job ID | Số ID của lô hàng do hệ thống cung cấp |
| H-B/L (HAWB) | Số chứng từ house bill |
| Contained H-B/L No. | Số chứng từ house bill có chứa |
| Combine H-B/L | Số chứng từ đã được gộp |
| Reset | Trở lại điều chỉnh ban đầu |
| Add | Thêm chứng từ |

**Subject to** (mỗi lần ta chọn nút hệ thống sẽ hiển thị dữ liệu ở bảng bên dưới):

| Tùy chọn | Mô tả |
|----------|-------|
| Customer | Gửi debit/credit đến khách hàng của lô hàng |
| Agent | Gửi debit/credit đến đại lý của lô hàng |
| Carrier/Co-loader | Gửi debit/credit đến co-loader hoặc carrier của lô hàng |
| Other Credit | Những đối tượng phải trả trong lô hàng |
| Other Debit | Những đối tượng phải thu trong lô hàng |
| Logistics | Liên quan đến hàng logistics |

**Print Options:**

| Tùy chọn | Mô tả |
|----------|-------|
| Show Group | Hiển thị các nhóm phí |
| Remark | Nhận xét |
| Set template | Đặt biểu mẫu |
| Include Paid Records | Bao gồm hồ sơ thanh toán |
| As Invoice | Xuất ra như 1 hóa đơn |
| Show Cont/Seal No. | Hiển thị số cont/seal |
| View Drap Invoice | Xem bản hóa đơn nhập |

![Documentation page 10](../attachments/bf1-bfs/documentation/docs_010.png)

**Invoice Reference** (các chức năng của hóa đơn):

| Trường | Mô tả |
|--------|-------|
| Issue Invoice | Xuất hóa đơn (nếu tích chọn thì Invoice Reference mới mở) |
| Invoice No. | Số hóa đơn (nếu có thì tích chọn ở và tìm kiếm hóa đơn đó) |
| Partner's Ref No. | Mã số người công tác viên liên quan |
| Date | Ngày |
| Payment | Chi trả (ngày tháng năm) |
| Issue VAT Invoice | Xuất hóa đơn thuế giá trị gia tăng |
| Assign to | Giao cho ai |
| Other Reference | Những bên liên quan khác |

Click chọn **Preview** để in ra, **Custom** để điều chỉnh cần in chi phí nào ra. Nếu ta muốn xuất các phí hoặc loại phí nào đó, click chọn, sau đó click nút **Issue Invoice** hệ thống sẽ đẩy chi phí đó xuống bên bảng dưới.

- **Remove Ref**: Loại bỏ các bên liên quan hoặc các chứng từ hóa đơn liên quan
- **Close**: Đóng tab hiện tại

### Refresh Data

Làm mới dữ liệu.

### Export Data

Xuất dữ liệu ra file .xml để lưu trữ hoặc chuyển qua các văn phòng khác tùy theo trường hợp.

### Cargo Manifest

Bảng kê hàng hóa.

![Documentation page 11](../attachments/bf1-bfs/documentation/docs_011.png)

### Save As

Lưu thông tin đơn hàng thành một đơn hàng mới có dữ liệu như đơn hàng cũ nhưng có mã mới.

![Documentation page 13](../attachments/bf1-bfs/documentation/docs_013.png)

**Các tùy chọn:**

| Tùy chọn | Mô tả |
|----------|-------|
| Select Shipper | Chọn người vận chuyển |
| Select the existing Job ID | Chọn số job file hiện tại |
| Select the existing HBL | Chọn số house bill hiện tại |
| Copy to new Shipment | Sao chép sang 1 bản đơn hàng mới |
| Change the Shipment Service | Đổi loại dịch vụ đơn hàng |
| Attach HBL to shtm | Đính kèm house bill vào file |
| Move to shipment | Chuyển đến đơn hàng |

Sau khi điền đủ thông tin ta click chọn **Next** để hệ thống chuyển đến form tiếp theo.

![Documentation page 14](../attachments/bf1-bfs/documentation/docs_014.png)

**Form tiếp theo:**

Ta có thể nhập số Job của file nếu ta muốn, không thì hệ thống sẽ tự động cấp cho file đó 1 job ID.

| Tùy chọn | Mô tả |
|----------|-------|
| Số master bill | Số master bill |
| Include Shipment Detail | Bao gồm chi tiết đơn hàng |
| Include Shipment Rates | Bao gồm tỷ giá của đơn hàng |
| Invoice & Packing List | Hóa đơn và danh sách hàng hóa |
| House Bill of Lading (HBL, HAWB) | House bill |
| Include OBH charges | Bao gồm phí chi hộ |

Sau khi chọn đủ thông tin click chọn **Next** để qua form tiếp theo. Ta click chọn **Finish** để hoàn tất quy trình và trở về màn hình ban đầu của lô hàng.

### Custom (Customs Clearance)

![Documentation page 15](../attachments/bf1-bfs/documentation/docs_015.png)

- **Non-Trading Customs Clearance Sheet**: Hiển thị biểu mẫu tờ khai hàng hóa xuất khẩu - mẫu dịch. Điền đầy đủ thông tin theo biểu mẫu sau đó click chọn Save để lưu thông tin vào đơn hàng và click chọn Print để in tờ khai ra.
- **Trading Custom Clearance Sheet**: Tương tự như bảng trên chỉ khác nhau cách nhập dữ liệu.

### Shipping Instruction (SI)

Hướng dẫn vận chuyển đơn hàng. Chỉ có ở các loại **Outbound Sea** (Section 4, 6, 8).

![Documentation page 71](../attachments/bf1-bfs/documentation/docs_071.png)

- **Bill Instruction**:
  - Save: Lưu thông tin
  - Reset: Khôi phục lại trạng thái ban đầu
  - Print Preview: SI Form Preview
  - Close: Đóng lại
- **Bill Detail**: Chi tiết bill
- **Attach List**: Danh sách file đính kèm

![Documentation page 72](../attachments/bf1-bfs/documentation/docs_072.png)

### Send Shipment Pre-alert

Gửi thông báo lô hàng đến đại lý.

![Documentation page 16](../attachments/bf1-bfs/documentation/docs_016.png)

### Send Shipment Info

Gửi thông tin hàng hóa cho khách hàng.

### Add refund charges

- **Add refund charge to Client**: Thêm chi phí trả cho khách hàng
- **Add refund charge to Agent (Other Credit)**: Thêm chi phí trả cho đại lý
- **Add refund charge to Agent (Other Debit)**: Thêm chi phí thu cho đại lý

![Documentation page 17](../attachments/bf1-bfs/documentation/docs_017.png)

### Convert Selling rate to local rate

Chuyển đổi tiền tệ về giá tiền hiện tại của văn phòng.

### Documents

Upload các file từ hệ thống BFSOne lên BEEcloud.

![Documentation page 17](../attachments/bf1-bfs/documentation/docs_017.png)

Ta click chuột phải để Attach New File, hệ thống sẽ hiển thị loại file bên dưới để ta chọn. Sau khi chọn được loại file ta click chọn **Choose** để xuất file lên BEEcloud.

![Documentation page 18](../attachments/bf1-bfs/documentation/docs_018.png)

**Có tất cả 8 loại file:**

| Loại file | Mô tả |
|-----------|-------|
| Arrival Notice | Thông báo hàng đến |
| HBL Information File | File thông tin house bill |
| Manifest File | File bảng kê |
| Shipment Instruction | File hướng dẫn làm hàng |
| Debit/Credit Note | Bảng kê thu/chi |
| P/L Sheet | Bảng P/L |
| EDI File | File EDI |
| Other File | Các loại file khác |

### Request collect documents

Yêu cầu kế toán đóng tiền để lấy chứng từ.

![Documentation page 19](../attachments/bf1-bfs/documentation/docs_019.png)

**Các trường thông tin:**

| Trường | Mô tả |
|--------|-------|
| Job No | Số job của file |
| MBL No | Số master bill |
| HBL No | Số house bill |
| Date | Ngày yêu cầu |
| Partner | Tên khách hàng |
| Address | Địa chỉ khách hàng |
| District | Quận |
| Content | Nội dung |
| Amount | Tổng cộng |
| OP Name | Tên nhân viên OP |
| Notes | Ghi chú |
| Request to | Yêu cầu tới |
| File attach | File đính kèm |
| Status | Trạng thái |
| Finish Date | Ngày hoàn thành |
| Result Notes | Ghi chú kết quả |

Sau khi điền đầy đủ thông tin ta click chọn **Send** để gửi trực tiếp yêu cầu đến nhân viên kế toán cụ thể để thanh toán và lấy chứng từ về.

### Request to guaranteeing

![Documentation page 19](../attachments/bf1-bfs/documentation/docs_019.png)

Hạn mức bảo lãnh của salesman được cho phép trên hệ thống được quản lý và duyệt bảo lãnh bởi (Ms.Hạnh). Bên trên là số job của file và tên khách hàng được bảo lãnh. Ta sẽ điền số tiền bảo lãnh vào phần Amount, ghi chú thêm (nếu có) ghi vào phần Notes.

![Documentation page 20](../attachments/bf1-bfs/documentation/docs_020.png)

| Trường | Mô tả |
|--------|-------|
| Guaranteeing amount | Hạn mức bảo lãnh của salesman hiện tại tối đa có thể được |
| Guaranteeing current amount | Hạn mức bảo lãnh hiện tại ở phía trên là bao nhiêu |
| Guaranteeing remain amount | Hạn mức bảo lãnh của salesman hiện tại còn đang bảo lãnh cho khách hàng khác mà vẫn chưa thanh toán với công ty |

Bảng bên trên là các khách hàng và số file mà salesman đã bảo lãnh bao gồm đã thanh toán và chưa thanh toán.

### Buying Rate

![Documentation page 21](../attachments/bf1-bfs/documentation/docs_021.png)

Giá mua của lô hàng.

| Trường | Mô tả |
|--------|-------|
| Description | Mô tả chi tiết |
| GW (Gross Weight) | Khối lượng thực tế |
| Quantity | Số lượng |
| Unit | Đơn vị |
| Unit Price | Giá của 1 đơn vị hàng |
| Curr | Tỷ giá |
| TAX | Thuế |
| Total Value | Tổng giá trị |
| Notes | Nếu có chuyển đổi tỷ giá thì sẽ thêm vào ghi chú |
| Account Ref | Mã số của loại phí |
| Docs | Chứng từ |
| No Inv (No Invoice) | Tick chọn sẽ không có hóa đơn |

### Selling Rate

![Documentation page 22](../attachments/bf1-bfs/documentation/docs_022.png)

Giá bán của lô hàng. Các trường tương tự như Buying Rate: Description, GW, Quantity, Unit, Unit Price, Curr, TAX, Total Value, Notes, Account Ref, Docs, No Inv.

### Other Credit

![Documentation page 22](../attachments/bf1-bfs/documentation/docs_022.png)

Các khoản phải chi khác.

| Trường | Mô tả |
|--------|-------|
| Payee | Người nhận tiền |
| GW (Gross Weight) | Khối lượng thực tế |
| Quantity | Số lượng |
| Unit | Đơn vị |
| Unit Price | Giá của 1 đơn vị hàng |
| Curr | Tỷ giá |
| TAX | Thuế |
| No Inv | Không hóa đơn |
| Total Value | Tổng giá trị |
| KB (Kick Back) | Tiền hoa hồng |
| Description | Mô tả chi tiết |
| OBH (On Behalf of) | Chi hộ |
| Account | Mã của loại phí |
| Docs | Chứng từ |
| Notes | Ghi chú |

> Lưu ý: Các loại LCL và Consol (Section 4, 5, 8, 9) có thêm trường **S.S.P (Share Sales Profit)** trong Other Credit.

### Other Debit

![Documentation page 23](../attachments/bf1-bfs/documentation/docs_023.png)

Các khoản phải thu khác. Các trường tương tự như Other Credit, chỉ thay Payee bằng **Payer** (Người trả tiền).

### Logistics Charges

![Documentation page 23](../attachments/bf1-bfs/documentation/docs_023.png)

Phụ phí logistics.

| Trường | Mô tả |
|--------|-------|
| Description | Mô tả chi tiết |
| Qty (Quantity) | Số lượng |
| Unit | Đơn vị |
| Unit Price | Giá của 1 đơn vị hàng |
| Curr | Tỷ giá |
| TAX | Thuế |
| Amount | Tổng cộng |

### Sales Profit

![Documentation page 24](../attachments/bf1-bfs/documentation/docs_024.png)

Lợi nhuận của sales.

| Trường | Mô tả |
|--------|-------|
| Currency | Tỷ giá |
| Destination | Điểm đến |
| Quantity | Số lượng |
| Buying Rate | Giá mua |
| Selling Rate | Giá bán |
| Other Credit | Các khoản chi khác |
| Other Debit | Các khoản thu khác |
| Logistics Charges | Phụ phí logistics |
| Fixed Costs | Chi phí sửa đổi |
| Total Profit | Tổng lợi nhuận |

### Others Info

Các thông tin khác của lô hàng.

| Trường | Mô tả |
|--------|-------|
| Type | Loại |
| Date Modified | Ngày chính sửa |
| Start Date | Ngày bắt đầu |
| Finish Date | Ngày kết thúc |
| Description | Mô tả chi tiết |
| Done | Trạng thái |
| Evaluation | Đánh giá |
| Attached | Đính kèm |
| Issued by | Được xuất hóa đơn bởi |
