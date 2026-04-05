---
title: "Mail — Email Solutions"
tags:
  - datatp
  - mail
  - outlook
---

## Exchange Online Setup


# 1. Cài đặt PowerShell trên macOS

brew install --cask powershell

# 2. Mở PowerShell

pwsh

# 3. Trong PowerShell, cài module

Install-Module -Name ExchangeOnlineManagement -Force

# 4. Kết nối

Connect-ExchangeOnline -UserPrincipalName [admin@beelogistics.com](mailto:admin@beelogistics.com)

# 5. Tạo policy

New-ApplicationAccessPolicy `    -AppId "YOUR-CLIENT-ID"`
-PolicyScopeGroupId "[GraphAPI-TeamsAccess@beelogistics.com](mailto:GraphAPI-TeamsAccess@beelogistics.com)" `    -AccessRight RestrictAccess`
-Description "Teams meeting access for CRM"

# 6. Test

Test-ApplicationAccessPolicy `    -Identity "dcenter@beelogistics.com"`
-AppId "YOUR-CLIENT-ID"



Connect-ExchangeOnline
New-ApplicationAccessPolicy -AppId "`4fd9400d-b576-4884-880b-670a3b0c7f0a`" -PolicyScopeGroupId "[d](mailto:group@domain.com)center@beelogistics.com" -AccessRight RestrictAccess -Description "Teams access"





---

## Mail Ticket — Nghiên cứu giải pháp

## Mail ticket: Nghiên cứu, tìm giải pháp, case study.

### Quản lý Email trong Công ty

### 1. Mục tiêu

- Tối ưu hóa quy trình tự động và quản lý dữ liệu:
- Đảm bảo dữ liệu từ email được tích hợp vào phần mềm nội bộ để tự động hóa quy trình.
- Giảm thiểu sự phụ thuộc vào Microsoft Outlook, từ đó tối ưu hóa chi phí.

### 2. Thách thức

- **Email server tự quản lý:**
Dễ bị chặn bởi các bộ lọc spam, không phù hợp cho các email quan trọng.
- **Tự động hóa và thu thập dữ liệu:**
Dữ liệu email cần được tích hợp vào hệ thống phần mềm nội bộ để xử lý và phân tích.
- **Chi phí:**
Sử dụng Outlook cho toàn bộ nhân viên gây tốn kém.
- **Tính liên tục và chuyên nghiệp:**
Email cá nhân (ví dụ: [jesse.vnhph@beelogistics.com](mailto:jesse.vnhph@beelogistics.com)) gây khó khăn trong việc duy trì giao tiếp liên tục với khách hàng khi nhân viên nghỉ việc hoặc thay đổi.
Một hệ thống email chung giúp tăng tính chuyên nghiệp, đảm bảo giao tiếp chỉ thông qua thương hiệu công ty.
- **Đa kênh:**
Tích hợp email với các nền tảng khác (như Zalo) để quản lý dữ liệu tập trung.

### 3. Giải pháp

### 3.1. Rà soát quy trình sử dụng email xác định:

- Bộ phận/nhân sự cần sử dụng Outlook: Ví dụ, đội ngũ sales, quản lý cấp cao.
- Bộ phận/nhân sự có thể sử dụng email nội bộ hoặc tài khoản miễn phí: Sử dụng Gmail/Outlook cá nhân được route qua domain công ty.

### 3.2. Giải pháp kỹ thuật

- Triển khai hệ thống email chung:
    - Sử dụng email chung (ví dụ: [pricing@beelogistics.com](mailto:pricing@beelogistics.com)) tích hợp với phần mềm nội bộ.
    - Gán ticket ID và định tuyến email tự động.
- Quy trình chi tiết:
    - Khi có mail gửi đến. ([pricing@beelogistics.com](mailto:pricing@beelogistics.com), [sales.hph@beelogistics.com](mailto:sales.hph@beelogistics.com), [sales.vnsgn@beelogistics.com](mailto:sales.vnsgn@beelogistics.com), ...)
    - Phần mềm scan mail liên tục đến phát hiện nhận được email, phân tích thông tin, dữ liệu và tiến hành định tuyến.
        - Ví dụ:
            - Phân loại email, mail to, mail from, trích xuất thông tin cảng, địa chỉ, công ty, code, tên người, ...
            - TH mail được gửi đi từ các hệ thống có sẵn của công ty như CRM, dữ liệu sẽ được thu thập trước lúc gửi.
            - Nhân sự điều phối mail kiểm tra thông tin mail và điều phối về từng VP, từng nhân sự.
    - Sau khi định tuyến: Hệ thống forwarding mail về email cá nhân của nhân sự phụ trách (Gmail/ Outlook).
    - Lưu lại thông tin vào cơ sở dữ liệu phục vụ phân tích, báo cáo.
    - [Optional]: Reply, follow up theo luồng mail.
        - Nhân sự dùng mail cá nhân reply lại email vừa nhận (sau khi hệ thống forwarding).
        - Hệ thống dùng email chung forward thông tin với thông tin chữ ký custom theo thông tin nhân sự để reply lại chính luồng mail đó.
        - Tương tự: nếu nhân sự thao tác với dữ liệu trên hệ thống, phần mềm cũng sẽ reply lại mail tương ứng tuỳ thuộc vào quy trình lúc đó.
```plain text
  Ví dụ với mail pricing@beelogistics.com, mục đích mail này để nhận hỏi giá, request giá từ sales gửi cho pricing và gửi qua hệ thống CRM.
  => Trước đó, CRM đã thu thập thông tin sales nhập như tuyến, loại hình (FCL Imp, FCL Exp, LCL, ..)
  => TH không gửi qua CRM, hệ thống sử dụng công nghệ như OCR để scan thông tin có trong mail hoặc pricing admin nhận thông tin và gắn tag (ticket ID).
  => Hệ thống dự theo dữ liệu thu thập hoặc ticket ID để định tuyến về đúng nhân sự pricing xử lý request đó.
  => Gửi email về Gmail/ Outlook cá nhân của nhân sự.
  => Nếu pricing muốn reply lại trực tiếp trên luồng email của sales:
    - Vào CRM chọn đúng request sales gửi để reply => CRM tự động gửi mail, hệ thống sẽ dùng email pricing@beelogistics.com để reply lại trên chính luồng mail sales gửi.
    - Pricing dùng mail cá nhân reply lại email vừa nhận, hệ thống forwarding qua cho sales, dùng mail pricing@beelogistics.com gửi chữ ký custom theo thông tin pricing xử lý.


```

### Flowchart.

```plain text
+--------------------+       +------------------------+        +------------------------+
|                    |       |                        |        |                        |
| Sales/ Khách hàng/ +------->  Email chung           +-------->  Email Routing System  |
| Others             |       |  pricing@bee...        |        |  (ERS)                 |
|                    |       |  sales.vnhph@bee...    |        |                        |
|                    |       |  sales.vnsgn@bee...    |        |                        |
+--------------------+       +------------------------+        +------------+-----------+
                                                                           |
                                                                           |
                                                                           v
                            +-----------------------------+                |
                            |                             |                |
                            |  Phân tích dữ liệu:         <----------------+
                            |  - OCR trích xuất           |
                            |  - Phân loại mail           |
                            |  - Ticket ID                |
                            |                             |
                            +-------------+---------------+
                                          |
                                          |
                                          v
+--------------------+        +-----------------------------+
|                    |        |                             |
| Cơ sở dữ liệu      <--------+  Định tuyến mail:           |
| lưu trữ            |        |  - Dựa theo thông tin       |
|                    |        |    phân tích                |
+--------------------+        |  - TICKET ID                |
                              |  - Nhân sự tự điều phối     |
                              |                             |
                              +-------------+---------------+
                                            |
                                            |
                                            v
                              +-----------------------------+
                              |                             |
                              |  Forward mail đến           |
                              |  nhân sự phụ trách          |
                              |  (Gmail/Outlook cá nhân)    |
                              |                             |
                              +-------------+---------------+
                                            |
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
            +---------------------------+       +---------------------------+
            |                           |       |                           |
            | Nhân sự xử lý trên        |       | Nhân sự xử lý qua         |
            | phần mềm:                 |       | mail cá nhân:             |
            | - Cập nhật thông tin      |       | - Soạn mail phản hồi      |
            | - Thực hiện quy trình     |       | - Reply trực tiếp vào     |
            | - Phê duyệt/từ chối       |       |   mail đã nhận            |
            |                           |       |                           |
            +--------------+------------+       +--------------+------------+
                           |                                   |
                           |                                   |
                           v                                   v
            +---------------------------+       +---------------------------+
            |                           |       |                           |
            | Hệ thống gen email        |       | Hệ thống forward mail     |
            | từ phần mềm:              |       | cá nhân:                  |
            | - Tự động tạo nội dung    |       | - Chuyển tiếp mail        |
            | - Đính kèm thông tin      |       | - Custom chữ ký theo      |
            | - Duy trì TICKET ID       |       |   thông tin nhân sự       |
            |                           |       |                           |
            +--------------+------------+       +--------------+------------+
                           |                                   |
                           |                                   |
                           +-------------------+---------------+
                                               |
                                               v
                                   +---------------------------+
                                   |                           |
                                   | Email phản hồi gửi lại cho|
                                   | Sales/ Khách hàng/ Others:|
                                   | - Duy trì luồng email gốc |
                                   | - Thống nhất thông tin    |
                                   | - Lưu trữ lịch sử trao đổi|
                                   |                           |
                                   +---------------------------+

```

### 3.3. Case study: Tối ưu hóa quy trình kiểm tra giá (Pricing Request)

**Vấn đề hiện tại:**

- Sales phải xác định và gửi email trực tiếp đến nhân viên pricing phụ trách theo tuyến (châu Á, châu Âu,...) hoặc loại hình dịch vụ (hàng xuất, hàng nhập,...).
- Việc nhớ thông tin nhân viên pricing phụ trách từng tuyến/dịch vụ gây tốn thời gian và dễ nhầm lẫn, làm giảm hiệu suất làm việc.
- Thông tin trao đổi bị phân mảnh khi gửi qua nhiều email cá nhân khác nhau.

**Giải pháp triển khai:**

- Thiết lập email chung [pricing@beelogistics.com](mailto:pricing@beelogistics.com) làm đầu mối tiếp nhận tất cả yêu cầu kiểm tra giá.
- Sales tạo request qua hệ thống CRM với đầy đủ thông tin (tuyến, loại hình dịch vụ, yêu cầu cụ thể). `DONE`
- CRM tự động gửi email với subject có ticket ID định danh (ví dụ: [TICKET-EX1234]) đến [pricing@beelogistics.com](mailto:pricing@beelogistics.com).
- Email Routing System (ERS) phân tích nội dung và ticket ID để định tuyến email đến đúng nhân viên pricing phụ trách.
- Hệ thống forward email đến địa chỉ cá nhân (Gmail/Outlook) của nhân viên pricing phụ trách.
- Nhân sự pricing xử lý thông tin trực tiếp trên phần mềm CRM (cập nhật báo giá, trạng thái).
- Hệ thống tự động tạo email phản hồi với nội dung cập nhật. (Duy trì luồng mail).

```plain text
+--------------------+       +--------------------+      +----------------------+
|                    |       |                    |      |                      |
| Sales              +------>+ CRM System         +----->+ Tạo subject với      |
| (tạo request với   |       | (thông tin tuyến,  |      | ticket ID            |
| đầy đủ thông tin)  |       |  loại hình dịch vụ)|      | [TICKET-EX1234]      |
+--------------------+       +--------------------+      +-----------+----------+
                                                                    |
                                                                    v
                                                  +---------------------------+
                                                  |                           |
                                                  | Email chung                |
                                                  | pricing@beelogistics.com   |
                                                  |                           |
                                                  +--------------+------------+
                                                                 |
                                                                 v
                                                  +---------------------------+
                                                  |                           |
                                                  | Email Routing System:     |
                                                  | - Phân tích ticket ID     |
                                                  | - Phân tích nội dung      |
                                                  | - Xác định nhân sự        |
                                                  |                           |
                                                  +--------------+------------+
                                                                 |
                                                                 v
                                                  +---------------------------+
                                                  |                           |
                                                  | Forward email đến         |
                                                  | nhân viên pricing         |
                                                  | phụ trách tuyến           |
                                                  |                           |
                                                  +--------------+------------+
                                                                 |
                                                                 v
                                                  +---------------------------+
                                                  |                           |
                                                  | Nhân sự pricing xử lý     |
                                                  | thông tin trực tiếp       |
                                                  | trên phần mềm CRM         |
                                                  | (cập nhật báo giá,        |
                                                  |  trạng thái)              |
                                                  |                           |
                                                  +--------------+------------+
                                                                 |
                                                                 v
                                                  +---------------------------+
                                                  |                           |
                                                  | Hệ thống gửi mail phản    |
                                                  | hồi lại sales từ email    |
                                                  | pricing@beelogistics.com  |
                                                  | (Duy trì luồng mail)      |
                                                  |                           |
                                                  +---------------------------+

```

---

Xem thêm: [[datatp-overview]]
