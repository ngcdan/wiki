# Phân tích Dự án OF1 - Freight Management System

## 1. Tổng quan hệ thống

OF1 (OpenFreightOne) là một hệ thống quản lý vận tải hàng hoá (Freight Management System) được thiết kế cho các công ty giao nhận vận tải quốc tế (Freight Forwarder) tại Việt Nam. Hệ thống bao phủ toàn bộ quy trình nghiệp vụ từ tiếp nhận khách hàng, báo giá, đặt chỗ, quản lý chứng từ, xuất hoá đơn, đến đối soát công nợ và báo cáo tài chính.

Hệ thống được chia thành **4 module chính**:

- **Catalogue** - Quản lý danh mục dữ liệu gốc (master data)
- **Sales Executive** - Quản lý kinh doanh, báo giá và đặt chỗ
- **Documentations** - Quản lý chứng từ và vận hành lô hàng
- **Accounting** - Kế toán, hoá đơn và báo cáo tài chính

### Kiến trúc tổng thể hệ thống

```mermaid
graph TB
    subgraph OF1["HỆ THỐNG PHẦN MỀM OF1 - Freight Management System"]
        direction TB

        subgraph MOD_CAT["II. CATALOGUE - Danh mục dữ liệu"]
            CAT_DEPT["Departments<br/>Phân quyền quản trị"]
            CAT_LEADS["Leads<br/>Khách hàng tiềm năng"]
            CAT_CUST["Customer<br/>Khách hàng"]
            CAT_SHIP["Shipper List<br/>Nhà vận chuyển"]
            CAT_CONS["Consignee List<br/>Người nhận hàng"]
            CAT_CARR["Carrier List<br/>Co-loader"]
            CAT_AGENT["Agents<br/>Đại lý"]
            CAT_OTHER["Other Contacts<br/>Liên hệ khác"]
            CAT_PORT["Port Index<br/>Danh mục cảng"]
            CAT_CONT["Container List<br/>Danh sách container"]
            CAT_TRUCK["Port Index Trucking"]
            CAT_WARN["Shipment Type Warning<br/>Hàng cảnh báo"]
            CAT_TASK["Transaction Task List"]
        end

        subgraph MOD_SALE["III. SALES EXECUTIVE - Kinh doanh"]
            SALE_VESSEL["Vessel Schedules<br/>Lịch tàu"]
            SALE_DB_AIR["DB AirFreight Pricing"]
            SALE_DB_EXP["DB Express Pricing"]
            SALE_DB_SEA["DB SeaFreight Pricing"]
            SALE_QUO_AIR["AirFreight Quotation<br/>Báo giá hàng không"]
            SALE_QUO_EXP["Express Quotation<br/>Báo giá chuyển phát"]
            SALE_QUO_SEA["SeaFreight Quotation<br/>Báo giá hàng biển"]
            SALE_BOOK_REQ["AirFreight Booking Request"]
            SALE_BOOK_CFM["AirFreight Booking Confirm"]
            SALE_LOG_REQ["Logistics Service Request"]
            SALE_TRUCK_REQ["Inland Trucking Request"]
            SALE_FREIGHT["Freight Shipment Mgmt"]
            SALE_SEA_ACK["Sea Booking Acknowledgement"]
            SALE_INT_BOOK["Internal Booking Request"]
            SALE_INQUIRY["Service Inquiry"]
            SALE_PL["P/L Sheet<br/>Lợi nhuận / Lỗ"]
        end

        subgraph MOD_DOCS["V. DOCUMENTATIONS - Chứng từ"]
            DOCS_EXPRESS["Express<br/>Chuyển phát nhanh"]
            DOCS_AIR_OUT["Outbound Air<br/>Xuất hàng không"]
            DOCS_AIR_IN["Inbound Air<br/>Nhập hàng không"]
            DOCS_LCL_OUT["LCL Outbound Sea<br/>LCL xuất biển"]
            DOCS_LCL_IN["LCL Inbound Sea<br/>LCL nhập biển"]
            DOCS_FCL_OUT["FCL Outbound Sea<br/>FCL xuất biển"]
            DOCS_FCL_IN["FCL Inbound Sea<br/>FCL nhập biển"]
            DOCS_CONSOL_OUT["Outbound Sea Consol<br/>Consol xuất"]
            DOCS_CONSOL_IN["Inbound Sea Consol<br/>Consol nhập"]
            DOCS_TRUCK["Inland Trucking<br/>Giao nhận nội địa"]
            DOCS_LOG["Logistics"]
            DOCS_WH["Warehouse Mgmt<br/>Quản lý kho"]
            DOCS_CFS["CFS Inbound"]
            DOCS_OPS["OPS Management"]
            DOCS_CUSTOMS["Customs Clearance"]
            DOCS_TRACE["Tracing ETD-ETA"]
            DOCS_EDI["EDI Local"]
        end

        subgraph MOD_ACC["IV. ACCOUNTING - Kế toán"]
            ACC_VAT_NEW["New VAT Invoice<br/>Tạo hoá đơn điện tử"]
            ACC_VAT_MGT["VAT Invoice Management"]
            ACC_MGMT["Accounting Management<br/>Phiếu thu/chi"]
            ACC_TRANS["Transaction Register<br/>Công nợ"]
            ACC_ADV["Advance Request<br/>Tạm ứng"]
            ACC_PAY["History of Payment<br/>Giải trình"]
            ACC_PAY_CTRL["Payment Request Control"]
            ACC_SHIP_PAY["Shipment Payment Control"]
            ACC_CREDIT["Credit Invoice Report"]
            ACC_DEBIT["Sheet of Debit Record"]
            ACC_REPORT["VAT Invoice Report"]
            ACC_AR["Account Receivable<br/>Công nợ phải thu"]
            ACC_OD["Overdue Debts<br/>Nợ quá hạn"]
            ACC_FP["Financial Planning<br/>Kế hoạch tài chính"]
        end
    end

    %% Quan hệ liên module
    CAT_LEADS -->|"Chuyển đổi"| CAT_CUST
    CAT_CUST -->|"Tạo báo giá"| SALE_QUO_SEA
    CAT_CUST -->|"Tạo báo giá"| SALE_QUO_AIR
    CAT_AGENT -->|"Chọn đại lý"| DOCS_AIR_OUT
    CAT_PORT -->|"POL/POD"| SALE_QUO_SEA
    CAT_PORT -->|"POL/POD"| DOCS_FCL_OUT

    SALE_QUO_SEA -->|"Booking"| SALE_INT_BOOK
    SALE_QUO_AIR -->|"Booking"| SALE_BOOK_REQ
    SALE_BOOK_REQ -->|"Confirm"| SALE_BOOK_CFM
    SALE_INT_BOOK -->|"Mở file"| DOCS_FCL_OUT
    SALE_INT_BOOK -->|"Mở file"| DOCS_AIR_OUT

    DOCS_AIR_OUT -->|"Xuất hoá đơn"| ACC_VAT_NEW
    DOCS_FCL_OUT -->|"Xuất hoá đơn"| ACC_VAT_NEW
    ACC_VAT_NEW -->|"Quản lý"| ACC_VAT_MGT
    ACC_TRANS -->|"SOA"| ACC_AR
    ACC_ADV -->|"Giải trình"| ACC_PAY

    classDef catStyle fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    classDef saleStyle fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef docsStyle fill:#FFF3E0,stroke:#E65100,color:#BF360C
    classDef accStyle fill:#FCE4EC,stroke:#C62828,color:#B71C1C

    class CAT_DEPT,CAT_LEADS,CAT_CUST,CAT_SHIP,CAT_CONS,CAT_CARR,CAT_AGENT,CAT_OTHER,CAT_PORT,CAT_CONT,CAT_TRUCK,CAT_WARN,CAT_TASK catStyle
    class SALE_VESSEL,SALE_DB_AIR,SALE_DB_EXP,SALE_DB_SEA,SALE_QUO_AIR,SALE_QUO_EXP,SALE_QUO_SEA,SALE_BOOK_REQ,SALE_BOOK_CFM,SALE_LOG_REQ,SALE_TRUCK_REQ,SALE_FREIGHT,SALE_SEA_ACK,SALE_INT_BOOK,SALE_INQUIRY,SALE_PL saleStyle
    class DOCS_EXPRESS,DOCS_AIR_OUT,DOCS_AIR_IN,DOCS_LCL_OUT,DOCS_LCL_IN,DOCS_FCL_OUT,DOCS_FCL_IN,DOCS_CONSOL_OUT,DOCS_CONSOL_IN,DOCS_TRUCK,DOCS_LOG,DOCS_WH,DOCS_CFS,DOCS_OPS,DOCS_CUSTOMS,DOCS_TRACE,DOCS_EDI docsStyle
    class ACC_VAT_NEW,ACC_VAT_MGT,ACC_MGMT,ACC_TRANS,ACC_ADV,ACC_PAY,ACC_PAY_CTRL,ACC_SHIP_PAY,ACC_CREDIT,ACC_DEBIT,ACC_REPORT,ACC_AR,ACC_OD,ACC_FP accStyle
```

---

## 2. Phân tích từng Module

### 2.1 Catalogue - Nền tảng dữ liệu gốc

Module này là nền tảng cho toàn bộ hệ thống, quản lý toàn bộ đối tượng tham gia vào quy trình giao nhận.

**Quản lý đối tác (8 nhóm):**

| Đối tượng | Vai trò | Đặc điểm |
|-----------|---------|----------|
| Departments | Phân quyền nội bộ | Admin only, phân quyền theo chi nhánh |
| Leads | Khách hàng tiềm năng | Có thể chuyển đổi thành Customer |
| Customer | Khách hàng thực tế | Trung tâm của toàn bộ giao dịch |
| Shipper | Người gửi hàng | Xuất hiện trên vận đơn |
| Consignee | Người nhận hàng | Xuất hiện trên vận đơn |
| Carrier | Hãng tàu/hãng bay | Vận chuyển thực tế |
| Agents | Đại lý | Đại diện tại nước ngoài |
| Other Contacts | Liên hệ khác | Hải quan, kho bãi, ... |

**Danh mục hệ thống (5 loại):**

- Port Index: Danh mục cảng biển, cảng hàng không theo chuẩn UNECE
- Container List: Danh sách container với ISO code, trọng lượng, kích thước
- Port Index Trucking: Cảng chuyên dùng cho trucking nội địa
- Shipment Type Warning: Hàng hoá đặc biệt (hàng nguy hiểm, ...)
- Transaction Task List: Danh sách giao dịch/công việc

**Nhận xét:**
- Cấu trúc đối tác (mục 3-8) sử dụng chung các trường: source, name_aka, name_full, name_vn, location, category, email, ac_ref, status
- Trường "ac_ref" dùng để liên kết công ty mẹ cho báo cáo SOA - thiết kế này giúp gom công nợ theo nhóm công ty
- Trường "status" có 3 trạng thái: Public / Lock / Warning - cho phép kiểm soát đối tác có vấn đề
- Agent có thêm trường "priority" (1-8) và "association_group" - cho thấy hệ thống hỗ trợ lựa chọn đại lý theo độ ưu tiên

### 2.2 Sales Executive - Kinh doanh & Báo giá

Module này quản lý toàn bộ quy trình từ báo giá đến đặt chỗ, bao gồm 16 chức năng chính.

**Quy trình chính:**

```
Database Giá -> Báo giá -> Đặt chỗ (Booking) -> Xác nhận -> Mở file
```

**Database Giá (3 loại):**
- AirFreight Pricing: Giá từ hãng hàng không
- SeaFreight Pricing: Giá từ hãng tàu
- Express Pricing: Giá từ nhà thầu phụ

**Báo giá (Quotation):** Hệ thống hỗ trợ 3 loại báo giá tương ứng với 3 phương thức vận chuyển. Mỗi báo giá chứa: customer, POL/POD, currency, giá theo loại container (20/40/40HQ/45), thời gian hiệu lực.

**Booking:** Chia thành 2 nhánh:
- AirFreight: Booking Request -> Booking Confirm (2 bước riêng biệt)
- Sea/Internal: Internal Booking Request (1 bước, đơn giản hơn)

**P/L Sheet:** Báo cáo lợi nhuận/lỗ của từng lô hàng - kết nối trực tiếp từ Selling Rate và Buying Rate trên file.

**Nhận xét:**
- Vessel Schedules là feature quan trọng giúp Sales có dữ liệu lịch tàu để tư vấn khách hàng
- Quy trình Air phức tạp hơn Sea (2 bước booking vs 1 bước) - phản ánh thực tế ngành freight forwarding
- Service Inquiry cho phép yêu cầu chỉnh sửa giá mua - có quy trình duyệt riêng
- P/L Sheet là điểm kết nối giữa module Sales và Accounting

### 2.3 Documentations - Vận hành & Chứng từ

Đây là module lớn nhất với 20 chức năng, quản lý toàn bộ chứng từ cho các loại lô hàng.

**Phân loại lô hàng (11 loại):**

| Loại | Hướng | Phương thức |
|------|-------|-------------|
| Express | Xuất | Chuyển phát nhanh |
| Outbound Air | Xuất | Hàng không |
| Inbound Air | Nhập | Hàng không |
| LCL Outbound Sea | Xuất | Đường biển lẻ |
| LCL Inbound Sea | Nhập | Đường biển lẻ |
| FCL Outbound Sea | Xuất | Đường biển nguyên cont |
| FCL Inbound Sea | Nhập | Đường biển nguyên cont |
| Outbound Sea Consol | Xuất | Gom hàng đường biển |
| Inbound Sea Consol | Nhập | Gom hàng đường biển |
| Inland Trucking | Nội địa | Xe tải |
| Logistics | Phức hợp | Dịch vụ logistics |

**Các thành phần chung của mỗi file:**

Mỗi file lô hàng đều có các thành phần:
- Thông tin cơ bản: Job ID, Customer, Agent, Shipper, Consignee, POL/POD, ETD/ETA
- Vận đơn: HAWB/HBL (House Bill) và MAWB/MBL (Master Bill)
- Giá mua/bán: Buying Rate, Selling Rate
- Debit/Credit Note: Xuất cho Customer, Agent, Carrier
- Logistics Charges: Chi phí vận hành
- Container chi tiết (đối với hàng biển FCL)

**Chức năng bổ trợ:**
- Warehouse Management: Quản lý kho hàng
- CFS Inbound: Quản lý hàng nhập kho CFS
- OPS Management: Điều phối vận hành
- Customs Clearance: Thủ tục hải quan
- Tracing ETD-ETA: Theo dõi lô hàng theo thời gian thực
- EDI Local: Trao đổi dữ liệu điện tử với các bên
- Task Notes: Ghi chú/nhắc nhở theo file

**Nhận xét:**
- Cấu trúc "File" là trung tâm của toàn bộ hệ thống - mọi giao dịch đều xoay quanh File
- Hệ thống hỗ trợ cả Inbound (nhập) và Outbound (xuất) cho mọi phương thức
- Sea Consol (gom hàng) là loại phức tạp nhất - liên kết nhiều HBL vào 1 MBL
- Chức năng "Change Salesman/Partner in file" cho thấy có nhu cầu chuyển đổi nhân sự phụ trách
- EDI là điểm kết nối với hệ thống bên ngoài (customs, hãng tàu, ...)

### 2.4 Accounting - Kế toán & Tài chính

Module này gồm 22 chức năng, chia thành các nhóm:

**Hoá đơn điện tử (VAT Invoice):**
- Tạo hoá đơn từ Debit/Credit Note của file
- Vòng đời: Draft (trắng) -> Issued (hồng) -> Paid (xanh)
- Hỗ trợ: Issue, Sign (ký điện tử), Send by mail (PDF + XML)
- Xử lý đặc biệt: Replace (huỷ cũ xuất mới), Editing Invoice (điều chỉnh)

**Quản lý công nợ:**
- Transaction Register: Trung tâm đối soát công nợ
- Statement of Account (SOA): Báo cáo công nợ theo khách hàng
- Account Receivable: Công nợ phải thu
- Overdue Debts: Cảnh báo nợ quá hạn

**Tạm ứng & Giải trình (Settlement):**
- Quy trình duyệt 3 cấp: Trưởng phòng -> Kế toán trưởng -> Giám đốc
- Mỗi cấp có quyền Approve hoặc Decline
- Kế toán trưởng có thể uỷ quyền duyệt thay Giám đốc (trong hạn mức)
- Sau khi duyệt xong, chi phí tự động nhập vào Logistics Charges của file

**Báo cáo (Reports):**
- VAT Invoice Report
- Credit Invoice Report
- Sheet of Debit Record
- Account Receivable
- Revenue & Profit Report

**Financial Planning:**
- Payment-Receivable Planning: Kế hoạch thu chi
- Bank Transaction History: Theo dõi biến động tài khoản ngân hàng

**Nhận xét:**
- Hoá đơn điện tử tích hợp ký số và gửi mail - phù hợp quy định pháp luật VN
- Quy trình duyệt tạm ứng/giải trình rất chặt chẽ với 3 cấp, có cảnh báo phí trùng lặp
- Financial Planning với Bank Transaction History cho thấy hệ thống hướng đến quản lý dòng tiền toàn diện

---

## 3. Quy trình nghiệp vụ chính (Business Processes)

### 3.1 Vòng đời lô hàng (Shipment Lifecycle)

```mermaid
flowchart TD
    START((Bắt đầu)) --> LEAD["1. Tiếp nhận khách hàng<br/><i>Catalogue > Leads</i>"]
    LEAD -->|"Chuyển đổi thành KH"| CUST["2. Tạo Customer<br/><i>Catalogue > Customer</i>"]

    CUST --> QUO{"3. Tạo báo giá<br/><i>Sales Executive</i>"}
    QUO -->|"Hàng không"| QUO_AIR["AirFreight Quotation"]
    QUO -->|"Hàng biển"| QUO_SEA["SeaFreight Quotation"]
    QUO -->|"Chuyển phát"| QUO_EXP["Express Quotation"]

    QUO_AIR --> BOOK_AIR["4a. AirFreight<br/>Booking Request"]
    QUO_SEA --> BOOK_SEA["4b. Internal Booking<br/>Request"]
    QUO_EXP --> BOOK_EXP["4c. Express Booking"]

    BOOK_AIR --> CONFIRM["5. Booking Confirm<br/><i>Xác nhận đặt chỗ</i>"]
    BOOK_SEA --> CONFIRM
    BOOK_EXP --> CONFIRM

    CONFIRM --> DOCS{"6. Mở File chứng từ<br/><i>Documentations</i>"}

    DOCS -->|"Air xuất"| D_AIR_OUT["Outbound Air"]
    DOCS -->|"Air nhập"| D_AIR_IN["Inbound Air"]
    DOCS -->|"Sea LCL xuất"| D_LCL_OUT["LCL Outbound Sea"]
    DOCS -->|"Sea LCL nhập"| D_LCL_IN["LCL Inbound Sea"]
    DOCS -->|"Sea FCL xuất"| D_FCL_OUT["FCL Outbound Sea"]
    DOCS -->|"Sea FCL nhập"| D_FCL_IN["FCL Inbound Sea"]
    DOCS -->|"Consol xuất"| D_CON_OUT["Outbound Sea Consol"]
    DOCS -->|"Consol nhập"| D_CON_IN["Inbound Sea Consol"]
    DOCS -->|"Trucking"| D_TRUCK["Inland Trucking"]
    DOCS -->|"Logistics"| D_LOG["Logistics"]
    DOCS -->|"Chuyển phát"| D_EXP["Express"]

    D_AIR_OUT --> BILL["7. Tạo vận đơn<br/><i>HAWB / HBL</i>"]
    D_AIR_IN --> BILL
    D_LCL_OUT --> BILL
    D_LCL_IN --> BILL
    D_FCL_OUT --> BILL
    D_FCL_IN --> BILL
    D_CON_OUT --> BILL
    D_CON_IN --> BILL
    D_TRUCK --> BILL
    D_LOG --> BILL
    D_EXP --> BILL

    BILL --> COST["8. Nhập giá mua/bán<br/><i>Buying Rate / Selling Rate</i>"]
    COST --> DEBIT["9. Xuất Debit/Credit Note<br/><i>Cho KH và đại lý</i>"]

    DEBIT --> INV["10. Xuất hoá đơn<br/><i>Accounting > New VAT Invoice</i>"]
    INV --> SOA["11. Đối soát công nợ<br/><i>Transaction Register > SOA</i>"]

    SOA --> PAY["12. Thanh toán<br/><i>History of Payment</i>"]
    PAY --> PROFIT["13. Báo cáo lợi nhuận<br/><i>P/L Sheet</i>"]
    PROFIT --> DONE((Hoàn thành))

    %% Quy trình phụ
    COST -.->|"Tạm ứng"| ADV["Advance Request<br/><i>Tạm ứng cho OP</i>"]
    ADV -.->|"Giải trình"| SETTLE["Settlement<br/><i>Giải trình chi phí</i>"]
    SETTLE -.-> PAY

    BILL -.->|"Thông quan"| CUSTOMS["Customs Clearance<br/><i>Thủ tục hải quan</i>"]
    BILL -.->|"Theo dõi"| TRACE["Tracing ETD-ETA<br/><i>Theo dõi lô hàng</i>"]
    BILL -.->|"EDI"| EDI["Send/Receive EDI"]

    classDef startEnd fill:#4CAF50,stroke:#2E7D32,color:white
    classDef catalogue fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    classDef sales fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef docs fill:#FFF3E0,stroke:#E65100,color:#BF360C
    classDef accounting fill:#FCE4EC,stroke:#C62828,color:#B71C1C
    classDef side fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C

    class START,DONE startEnd
    class LEAD,CUST catalogue
    class QUO,QUO_AIR,QUO_SEA,QUO_EXP,BOOK_AIR,BOOK_SEA,BOOK_EXP,CONFIRM sales
    class DOCS,D_AIR_OUT,D_AIR_IN,D_LCL_OUT,D_LCL_IN,D_FCL_OUT,D_FCL_IN,D_CON_OUT,D_CON_IN,D_TRUCK,D_LOG,D_EXP,BILL,COST,DEBIT docs
    class INV,SOA,PAY,PROFIT accounting
    class ADV,SETTLE,CUSTOMS,TRACE,EDI side
```

Quy trình 13 bước từ tiếp nhận khách hàng đến báo cáo lợi nhuận, xuyên suốt 4 module. Đây là quy trình cốt lõi của hệ thống.

**Các nhánh phụ:**
- Tạm ứng / Giải trình: Song song với quy trình chính, phục vụ vận hành
- Customs Clearance: Thủ tục hải quan tại các node vận đơn
- Tracing: Theo dõi lô hàng theo thời gian thực
- EDI: Trao đổi dữ liệu điện tử

### 3.2 Quy trình xuất hoá đơn (Invoice Flow)

```mermaid
flowchart TD
    START((File đã nhập giá)) --> DEBIT["Xuất Debit/Credit Note<br/><i>Docs > More > Subject to</i>"]

    DEBIT --> DEBIT_CUST["Debit cho Customer"]
    DEBIT --> DEBIT_AGENT["Debit cho Agent"]
    DEBIT --> DEBIT_CARRIER["Debit cho Carrier"]

    DEBIT_CUST --> CREATE_INV["Tạo hoá đơn điện tử<br/><i>Accounting > New VAT Invoice</i>"]
    DEBIT_AGENT --> CREATE_INV
    DEBIT_CARRIER --> CREATE_INV

    CREATE_INV --> STEP1["Bước 1: Chọn Accounting > New VAT Invoice"]
    STEP1 --> STEP2["Bước 2: Add from list<br/>Chọn KH/File > Filter > Tick chi phí > OK"]
    STEP2 --> SAVE["Bước 3: Kiểm tra > Save"]

    SAVE --> DRAFT["Hoá đơn NHÁP (Draft)<br/>Màu trắng"]

    DRAFT --> ISSUE{"Issue E-Invoice?"}
    ISSUE -->|"Yes"| ISSUED["Hoá đơn đã ISSUE<br/>Màu hồng"]
    ISSUE -->|"Chưa"| DRAFT

    ISSUED --> SIGN["Make E-Invoice Signature<br/><i>Ký điện tử</i>"]
    SIGN --> SEND["Send E-Invoice by mail<br/><i>PDF + XML cho KH</i>"]

    ISSUED --> PAID{"Khách hàng<br/>thanh toán?"}
    PAID -->|"Đã thanh toán"| DONE_INV["Hoá đơn XONG<br/>Màu xanh"]
    PAID -->|"Chưa"| OVERDUE["Công nợ quá hạn<br/><i>Overdue Debts</i>"]

    DONE_INV --> SOA["Đối soát công nợ<br/><i>Statement Of Account</i>"]
    OVERDUE --> SOA

    %% Luồng phụ
    ISSUED -.->|"Sai thông tin"| REPLACE["Replace New E-Invoice<br/><i>Huỷ cũ, xuất mới</i>"]
    REPLACE -.-> DRAFT

    ISSUED -.->|"Điều chỉnh"| EDIT["Make Editing Invoice<br/><i>Hoá đơn điều chỉnh</i>"]

    ISSUED -.->|"Import"| ACC_SYS["Import to Accounting System<br/><i>Đẩy vào PM kế toán</i>"]

    SOA --> REPORT["Báo cáo"]
    REPORT --> R1["VAT Invoice Report"]
    REPORT --> R2["Credit Invoice Report"]
    REPORT --> R3["Sheet of Debit Record"]
    REPORT --> R4["Account Receivable"]
    REPORT --> R5["Revenue & Profit Report"]

    classDef draft fill:#FFFFFF,stroke:#9E9E9E
    classDef issued fill:#FCE4EC,stroke:#C62828
    classDef paid fill:#E8F5E9,stroke:#2E7D32
    classDef warning fill:#FFF3E0,stroke:#E65100
    classDef report fill:#E3F2FD,stroke:#1565C0

    class DRAFT draft
    class ISSUED,SIGN,SEND issued
    class DONE_INV,SOA paid
    class OVERDUE warning
    class R1,R2,R3,R4,R5 report
```

Bắt đầu từ việc nhập giá trên file, xuất Debit/Credit Note cho 3 đối tượng (Customer, Agent, Carrier), sau đó tạo hoá đơn điện tử. Hoá đơn trải qua 3 trạng thái màu sắc: trắng (Draft) -> hồng (Issued) -> xanh (Paid).

### 3.3 Quy trình duyệt tạm ứng / giải trình (Settlement Flow)

```mermaid
stateDiagram-v2
    [*] --> TạoGiảiTrình: OP tạo giải trình

    TạoGiảiTrình --> GửiYêuCầu: Click Send Request
    GửiYêuCầu --> TrưởngPhòngDuyệt: Gửi tới Trưởng phòng

    TrưởngPhòngDuyệt --> KếToánDuyệt: Approve
    TrưởngPhòngDuyệt --> TạoGiảiTrình: Decline\n(Thông báo OP làm lại)

    state TrưởngPhòngDuyệt {
        [*] --> KiểmTraPhí: Kiểm tra phí và hoá đơn theo HBL
        KiểmTraPhí --> CảnhBáoTrùng: Nếu phí trùng lặp -> hiện màu đỏ
        CảnhBáoTrùng --> QuyếtĐịnh: Chọn Yes/No
        KiểmTraPhí --> QuyếtĐịnh: Không trùng
    }

    KếToánDuyệt --> GiámĐốcDuyệt: Approve
    KếToánDuyệt --> TạoGiảiTrình: Decline\n(Thông báo OP)

    state KếToánDuyệt {
        [*] --> SoSánh: So sánh với phiếu tạm ứng
        SoSánh --> CóThểXoá: Có thể xoá chi phí không hợp lý
        CóThểXoá --> UỷQuyền: Uỷ quyền duyệt dùm Giám đốc\n(trong hạn mức)
    }

    GiámĐốcDuyệt --> HoànThành: Approve
    GiámĐốcDuyệt --> TạoGiảiTrình: Decline\n(Mở khoá để chỉnh sửa)

    state GiámĐốcDuyệt {
        [*] --> KiểmTraHạnMức: Kiểm tra hạn mức
        KiểmTraHạnMức --> UỷQuyềnKTT: Có thể uỷ quyền KTT duyệt
    }

    HoànThành --> TựĐộngNhập: Chi phí tự động nhập vào\nLogistics Charges của file

    state HoànThành {
        [*] --> Cleared: Giải trình đã clear
        Cleared --> ImpAcc: Import vào phần mềm kế toán
    }

    TựĐộngNhập --> [*]

    note right of TạoGiảiTrình
        Trường hợp 1: Chưa approve -> OP tự xoá
        Trường hợp 2: Đã approve & clear -> KT mở khoá
        Trường hợp 3: Đã import Acc -> Bỏ dấu ImpAcc trước
    end note
```

Quy trình 3 cấp với các lưu ý:
- Trưởng phòng kiểm tra phí và cảnh báo trùng lặp
- Kế toán so sánh với phiếu tạm ứng, có thể xoá chi phí không hợp lý
- Giám đốc có thể uỷ quyền cho Kế toán trưởng duyệt trong hạn mức

---

## 4. Mô hình dữ liệu (Data Model)

### 4.1 Sơ đồ quan hệ thực thể (Entity Relationship)

```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : "phân quyền"
    USER ||--o{ LEAD : "tạo/quản lý"
    USER ||--o{ CUSTOMER : "quản lý"
    USER ||--o{ QUOTATION : "tạo"
    USER ||--o{ FILE : "mở file"

    LEAD ||--o| CUSTOMER : "chuyển đổi"
    LEAD {
        string lead_no PK "Mã tự động"
        string first_name
        string middle_name
        string last_name
        string nick_name
        string mobile
        string country
        string industry
        string email
        string status "Active/Inactive"
        string city
        string company
        string assigned_to
    }

    CUSTOMER ||--o{ QUOTATION : "nhận báo giá"
    CUSTOMER ||--o{ FILE : "chủ hàng"
    CUSTOMER ||--o{ INVOICE : "nhận hoá đơn"
    CUSTOMER {
        string customer_id PK "Mã tự động"
        string source "Nhóm phân loại"
        string name_abbr "Tên viết tắt"
        string name_en "Tên tiếng Anh"
        string name_vn "Tên tiếng Việt"
        string personal_contact
        string address_en
        string address_vn
        string country
        string sale_manager
        string location "Oversea/Domestic"
        string tax_code
        string category "Customer/Co-loader/Shipper/Consignee"
        string ac_ref "Công ty mẹ cho SOA"
        string status "Public/Lock/Warning"
        int term_day "Số ngày nợ"
        string swift_code
        string bank
    }

    SHIPPER {
        string id PK
        string source
        string name_aka
        string name_full
        string name_vn
        string location
        string category
        string email
        string ac_ref
        string status "Public/Lock/Warning"
    }

    CONSIGNEE {
        string id PK
        string source
        string name_aka
        string name_full
        string name_vn
        string location
        string category
        string email
        string ac_ref
        string status "Public/Lock/Warning"
    }

    AGENT {
        string id PK
        string source
        string name_aka
        string name_full
        string name_vn
        string location
        string category
        string email
        string ac_ref
        string status "Public/Lock/Warning"
        int priority "1-8 độ ưu tiên"
        string service_type
        string association_group
    }

    CARRIER {
        string id PK
        string source
        string name_aka
        string name_full
        string name_vn
        string location
        string category
        string email
        string ac_ref
        string status "Public/Lock/Warning"
    }

    PORT {
        string port_code PK "Chuẩn UNECE"
        string port_name
        string country
        string zone "Châu lục"
        string mode "Sea/Air/Inland/Depot"
    }

    CONTAINER {
        string container_no PK
        string iso
        string type
        string description
        float weight
        string vendor
        string origin
        string owner
    }

    VESSEL_SCHEDULE {
        string id PK
        string line "Chuyến tàu"
        string pol FK "Cảng đi"
        string pod FK "Cảng đến"
        date etd
        date eta
        string vessel
        string vessel_no
    }

    QUOTATION ||--o{ BOOKING : "đặt chỗ"
    QUOTATION {
        string id PK
        string type "Sea/Air/Express"
        string customer_id FK
        string pol FK
        string pod FK
        string currency
        float price_20
        float price_40
        float price_40hq
        float price_45
        string carrier_service
        date valid_from
        date valid_to
    }

    BOOKING ||--|| FILE : "mở file"
    BOOKING {
        string id PK
        string quotation_id FK
        string type "Air/Sea/Internal"
        string status "Request/Confirmed"
    }

    FILE ||--o{ BILL : "chứa"
    FILE ||--o{ BUYING_RATE : "giá mua"
    FILE ||--o{ SELLING_RATE : "giá bán"
    FILE ||--o{ DEBIT_NOTE : "phát hành"
    FILE ||--o{ CREDIT_NOTE : "phát hành"
    FILE {
        string job_id PK "Mã lô hàng"
        date create_date
        date etd
        date eta
        string commodity "Loại hàng"
        string mode "Air/Sea/Express/Truck"
        string direction "Inbound/Outbound"
        string type "FCL/LCL/Consol"
        string customer_id FK
        string agent_id FK
        string shipper_id FK
        string consignee_id FK
        string pol FK
        string pod FK
        string salesman
    }

    BILL {
        string bill_no PK "HAWB/HBL/MAWB/MBL"
        string job_id FK
        string type "House/Master"
        string mode "Original/Copy/Surrendered"
    }

    INVOICE ||--o{ SOA : "thuộc"
    INVOICE {
        string invoice_no PK
        string job_id FK
        string bill_no FK
        string customer_id FK
        date issue_date
        float amount
        string currency
        float vat
        string status "Draft/Issued/Paid/Cancelled"
        string type "VAT/Debit/Credit"
    }

    SOA {
        string soa_no PK
        string customer_id FK
        date from_date
        date to_date
        float total_amount
        string status "Open/Paid/Partial"
    }

    SETTLEMENT {
        string id PK
        string advance_id FK
        string job_id FK
        float amount
        string status "Pending/Approved/Declined"
        string approved_by_manager
        string approved_by_accountant
        string approved_by_director
    }

    ADVANCE_REQUEST ||--|{ SETTLEMENT : "giải trình"
    ADVANCE_REQUEST {
        string id PK
        string creator FK
        float amount
        date request_date
        string status "Pending/Approved/Cleared"
    }

    PORT ||--o{ VESSEL_SCHEDULE : "POL"
    PORT ||--o{ VESSEL_SCHEDULE : "POD"
    PORT ||--o{ QUOTATION : "POL"
    PORT ||--o{ QUOTATION : "POD"
    PORT ||--o{ FILE : "POL"
    PORT ||--o{ FILE : "POD"
    AGENT ||--o{ FILE : "đại lý"
    SHIPPER ||--o{ FILE : "người gửi"
    CONSIGNEE ||--o{ FILE : "người nhận"
    CARRIER ||--o{ FILE : "vận chuyển"
    FILE ||--o{ INVOICE : "xuất hoá đơn"
    FILE ||--o{ ADVANCE_REQUEST : "tạm ứng"
```

### 4.2 Các thực thể chính

Hệ thống có khoảng **15 thực thể chính** với quan hệ phức tạp:

**Nhóm đối tác:** Lead, Customer, Shipper, Consignee, Agent, Carrier
- Lead có thể chuyển đổi thành Customer (quan hệ 1-1)
- Customer là trung tâm kết nối với Quotation, File, Invoice

**Nhóm vận hành:** Port, Container, Vessel Schedule, Quotation, Booking, File, Bill
- File là thực thể trung tâm nhất, liên kết với hầu hết các thực thể khác
- Bill (vận đơn) có 2 loại: House (HAWB/HBL) và Master (MAWB/MBL)

**Nhóm tài chính:** Invoice, SOA, Settlement, Advance Request
- Invoice có 3 loại: VAT, Debit, Credit
- SOA gom nhiều Invoice theo khách hàng và thời gian

### 4.3 Quan hệ đáng chú ý

- **File -> Bill**: 1 file có thể có nhiều vận đơn (1:N)
- **File -> Invoice**: 1 file có thể xuất nhiều hoá đơn (1:N)
- **File -> Buying/Selling Rate**: Giá mua/bán riêng cho từng file
- **Customer -> SOA**: Đối soát công nợ theo khách hàng
- **Advance Request -> Settlement**: Mỗi tạm ứng phải có giải trình (1:N)

---

## 5. Hệ thống phân quyền (User Roles)

### 5.1 Sơ đồ vai trò và quyền hạn

```mermaid
flowchart LR
    subgraph ROLES["VAI TRÒ NGƯỜI DÙNG"]
        ADMIN["ADMIN<br/>Quản trị hệ thống"]
        DIRECTOR["GIÁM ĐỐC<br/>Phê duyệt cấp cao"]
        ACCT_CHIEF["KẾ TOÁN TRƯỞNG<br/>Duyệt tài chính"]
        DEPT_HEAD["TRƯỞNG PHÒNG<br/>Duyệt nghiệp vụ"]
        SALESMAN["SALESMAN<br/>Kinh doanh"]
        DOCS_STAFF["NHÂN VIÊN CHỨNG TỪ<br/>Xử lý file"]
        ACCOUNTANT["KẾ TOÁN<br/>Xử lý hoá đơn"]
        OP["NHÂN VIÊN OP<br/>Vận hành"]
    end

    subgraph PERMS["QUYỀN HẠN"]
        P_FULL["Toàn quyền hệ thống"]
        P_APPROVE_HIGH["Duyệt tạm ứng/giải trình<br/>hạn mức cao"]
        P_APPROVE_MID["Duyệt tài chính<br/>Uỷ quyền Giám đốc"]
        P_APPROVE_LOW["Duyệt nghiệp vụ<br/>Ký Settlement"]
        P_SALES["Quản lý KH, Báo giá,<br/>Booking, P/L Sheet"]
        P_DOCS["Mở file, Tạo vận đơn,<br/>Nhập giá, Xuất Debit/Credit"]
        P_ACCT["Xuất hoá đơn VAT,<br/>Quản lý công nợ, Báo cáo"]
        P_OP["Tạm ứng, Giải trình,<br/>Trucking Request"]
    end

    ADMIN --> P_FULL
    DIRECTOR --> P_APPROVE_HIGH
    ACCT_CHIEF --> P_APPROVE_MID
    DEPT_HEAD --> P_APPROVE_LOW
    SALESMAN --> P_SALES
    DOCS_STAFF --> P_DOCS
    ACCOUNTANT --> P_ACCT
    OP --> P_OP

    subgraph APPROVAL["QUY TRÌNH DUYỆT TẠM ỨNG / GIẢI TRÌNH"]
        direction TB
        A1["OP tạo yêu cầu"] --> A2["Trưởng phòng duyệt"]
        A2 -->|"Approve"| A3["Kế toán trưởng duyệt"]
        A2 -->|"Decline"| A1
        A3 -->|"Approve"| A4["Giám đốc duyệt"]
        A3 -->|"Decline"| A1
        A4 -->|"Approve"| A5["Hoàn thành"]
        A4 -->|"Decline"| A1
    end

    classDef admin fill:#D32F2F,color:white
    classDef director fill:#1565C0,color:white
    classDef chief fill:#2E7D32,color:white
    classDef head fill:#F57F17,color:white
    classDef staff fill:#7B1FA2,color:white

    class ADMIN admin
    class DIRECTOR director
    class ACCT_CHIEF chief
    class DEPT_HEAD head
    class SALESMAN,DOCS_STAFF,ACCOUNTANT,OP staff
```

### 5.2 Các vai trò

| Vai trò | Quyền hạn chính |
|---------|----------------|
| Admin | Toàn quyền hệ thống, quản trị phân quyền |
| Giám đốc | Duyệt tạm ứng/giải trình cấp cao nhất |
| Kế toán trưởng | Duyệt tài chính, uỷ quyền duyệt thay Giám đốc |
| Trưởng phòng | Duyệt nghiệp vụ, ký Settlement |
| Salesman | Quản lý KH, báo giá, booking, xem P/L Sheet |
| Nhân viên chứng từ | Mở file, tạo vận đơn, nhập giá, xuất Debit/Credit |
| Kế toán | Xuất hoá đơn VAT, quản lý công nợ, báo cáo |
| Nhân viên OP | Tạm ứng, giải trình, trucking request |

### 5.3 Quy trình duyệt phân cấp

```
OP tạo yêu cầu -> Trưởng phòng duyệt -> Kế toán trưởng duyệt -> Giám đốc duyệt -> Hoàn thành
```

Bất kỳ cấp nào Decline đều trả về OP làm lại. Đây là quy trình kiểm soát nội bộ nghiêm ngặt, phù hợp với doanh nghiệp logistics VN.

