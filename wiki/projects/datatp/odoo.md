---
title: "Odoo — ERP & Kế toán"
tags:
  - datatp
  - odoo
  - accounting
---

## Odoo ERP — Development

> [!note]+ ### Develop
> - **Activate ENV:** `source odoo14-venv/bin/activate`

> [!note]+ ### Cập nhật dữ liệu lên web server
> `**ssh:
> ssh -p 30221 **`[`**datatp@beescs-1.dev.datatp.net**`](mailto:datatp@beescs-1.dev.datatp.net)`** , pass = Datatp!@#
> ssh -p 30222 **`[`**datatp@beescs-2.dev.datatp.net**`](mailto:datatp@beescs-2.dev.datatp.net)`** , pass = Datatp!@#**`
> 
> [`**tuan08@gmail.com**`](mailto:tuan08@gmail.com)`**/DataTP@123**`** ⇒ acc beescs.com**
> 
> - Command depends: 
> - Connect qua ssh lên server → chạy run:clean  → init data từ giao diện

> [!note]+ ### Ask
> ![[Screenshot_2022-12-07_at_17.17.08.png]]
> 
> - Hạch toán lương, hạch toán chi phí bảo hiểm trừ lương
> 

- Khái niệm là có 1 cái máy chủ ở bên ngoài, và có nhiều cái máy ảo ở bên trong. Thực sự máy ảo của docker không phải là máy ảo thật. Chiến lược là nhiều phần mềm (program) nhóm chung lại với nhau, và coi như nhóm chung đó là một cái máy ảo

```bash
cd namespaces/generic-server/production
vi k8s-config/

ssh -p 30231 datatp@datatp.cloud
```

Máy ảo giống virtual box hay parallel thì nó simulate một cái máy ảo thật, như vậy có thể cái window trên linux, và linux trên window được 

Còn container là máy ảo và máy chủ là phải cùng nhân kernel là linux,

![[Screenshot_2023-01-27_at_13.48.43.png]]

In **projects/k8s: **

In **namespace/generic-server/productions: **

Địa chỉ mount trên máy thật : **/mnt/data/cloud/pv/generic-server/production/servers**

In **namespace/it/prod: (location của nginx container)**

Trong trường hợp cần vào root của máy ảo để cài. 

setup Odoo: 
---

## Báo cáo kế toán


Modify Depreciation Asset

- Lỗi dữ liệu tài sản: CC00028, sai luôn bút toán liên kết. 
- Lỗi dữ liệu tài sản: CC00117, sai luôn bút toán liên kết. 


CC00100

CC00101

Chỉ modify nếu value_residual !- 0 

TS00010

---

tài sản cố định: 

Phí làm giá kệ kho BTL

---


Tài sản cố định

1.552.468,9

**Chi phí phát triển phần mềm**


CCDC: 
---

## HPS — Odoo Integration


> [!note]+ ### BFS DB
> - PersonalProfile: thông tin bank của hps

> [!note]+ Hướng dẫn công cụ dụng cụ. tài sản.
> Trong phần kế toán của Odoo có 1 phần gọi là khấu hao tài sản: 

Account datatp chị Loan, **hps.loanpt/hps.loanpt@123**

Đối chiếu lại các số tài khoản, khoản mục, sổ nhật ký.


HAIHAN2302004: job chị Mỹ sai invoice chi hộ


> [!note]+ ### Đẩy các invoice từ phần mềm nghiệp vụ qua Odoo
> Bfsone: 
> 
> Không biết job nào xong, job nào chưa xong. 
> 
> Phần mềm mới là đẩy qua kế toán. Xong xuất hoá đơn trên phầm mềm kế toán. 
> 
> Hoá đơn bán đẩy trước vì phải xuất hoá đơn cho khách
> 
> Còn công nợ với agent và nhà cung cấp thì phải đợi confirm rồi mới đẩy sau. Có thể là cuối tháng. Hoặc lâu lâu chị ấy lại đẩy một lần nhiều hoá đơn qua. 
> 
> Giờ chị ấy cần lọc ra những hoá đơn nào đã đẩy rồi và những hoá đơn nào chưa đẩy ạ
> 
> 
> ⇒ Đối với hoá đơn bán: Lúc nào cần xuất thì đẩy, đẩy invoice xong thì mặc định sẽ là posted với invoice đó luôn và không cho chỉnh sữa. Hoặc người có quyền cao hơn sẽ được chỉnh sữa. Nhưng vẫn phải đối chiếu lại với kế toán. 
> 
> ⇒ Đối với công nợ của nhà cung cấp hoặc agent: đẩy tuỳ thời điểm, có thể là 
> 
> HAIHAN2302041
> 
> HLGHAN2301011
> 
> 
> 
> - Đánh dấu những hoá đơn đã xuất. 
> - Sẽ có các hoá đơn cus yêu cầu xuất, thì chị sẽ xuất ra trước. 
> - Các hoá đơn còn lại 
> - 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
>  
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 
> 

> [!note]+ ### Accountant 
> - Em nhờ người nhập các báo nợ, báo có giúp chị rồi. 
> - Có các báo nợ liên quan đến các hoá đơn mua, bán của của nghiệp vụ logistics mà có số tiền phát sinh bằng với các hoá đơn trên từng job ⇒ Thì em cũng gạch luôn hoá đơn đó. 
> - Còn các báo nợ, báo có khác (hầu như là của đại lý, Bee) em không gạch được. Vì số tiền trên từng báo nợ, báo có file excel chị gửi số tiền không giống với các hoá đơn trên từng job của tháng 1.   ⇒ Chị tự đối soát để gạch những hoá đơn theo từng job tương ứng. ⇒ Chị hỗ trợ em thanh toán nốt các hoá đơn trong tháng 1. 
> - Hỗ trợ giúp em các phần như số tài khoản, sổ nhật ký, các khoản mục. Cấu hình kết chuyển xem cần sữa, bổ sung gì nữa không báo em bổ sung?
> - Tiếp đó là phần số dư đầu kỳ, tạo kết chuyển kqkd tháng 1. Chạy các báo cáo tháng 1 để đối chiếu dữ liệu.
> - Đẩy dữ liệu tháng 2, xem giúp em các dữ liệu đẩy qua đã đúng, đủ chưa (thông tin đối tác, tiền, sổ nhật ký, tài khoản, khoản mục)
> - Tạo thanh toán cho các hoá đơn tháng 2, nhập các bút toán admin ⇒ Tạo kết chuyển ⇒ Xem các báo cáo. 
> - Em chỉ có thể ưu tiên hỗ trợ chị các mục này trước. Mục đích là đối chiếu dữ liệu đảm bảo đúng đủ trước. 
> Sau đó 2 chị em bắt đầu mổ xẻ các bất cập, các phần kém hiệu quả, cần tối ưu trên phần mềm để hoàn thiện quy trình, nghiệp vụ của kế toán tiếp.
> Em cần phải có kết quả để báo cáo cho anh Tuấn rồi mới làm tiếp các yêu cầu khác được. 
> Chị thấy thế nào ạ? 
> 
> 
> 
> job cần sữa lại: 
> 
> Màn hình Booking Process: 

> [!note]+ ### Đối soát tháng 1
> Doanh thu trên báo cáo kết quả kinh doanh bị lệch: 
> 
> Chị Loan ơi, anh Tuấn vừa mới báo lại em việc gạch hoá đơn ấy ạ. 
> 
> Hiện tại phần mềm vẫn hoạt động được theo các cách em đã hướng dẫn cho chị. Chị giúp em gạch các hoá đơn trong tháng 1, tháng 2 để chạy báo cáo với ạ. 


Chị cần báo cáo gì ở tập toàn chị list ra giúp em được không? 

Loại báo cáo? Xuất ở đâu?



Quy trình bên bfsone: 
---

## Kế toán — Bugs & Nghiệp vụ

> [!note]+ ### [Bugs] - Số liệu trước và sau kết chuyển không giống nhau
> - Nguyên tắc: 
> Tài khoản đầu 5, 6, 7, 8 không có dư ⇒ hàng tháng (hoặc theo chu kỳ của kế toán) phải thực hiện kết chuyển để tính ra lãi lỗ
> Tính ra lãi lỗ sẽ ghi vào tài khoản `421 - Lợi nhuận chưa phân phối năm nay`
> Không kết chuyển trực tiếp mà sẽ kết chuyển qua tài khoản `911 - Tài khoản kết chuyển.`  ( có thể kết chuyển nhiều level)

### Thanh toán hoá đơn

Chênh lệch tỷ giá: 

1. Nếu tỷ giá hoá đơn > tỷ giá BN/ BC:
    - Tạo bút toán chênh lệch ghi nhận doanh thu, link với HĐ
    - Các tài khoản phân tích lấy theo hoá đơn.
2. Nếu tỷ giá hoá đơn < tỷ giá BN/ BC:
- Tạo bút toán chênh lệch ghi nhận chi phí, link với BN/ BC.
- Các tài khoản phân tích lấy theo báo nợ, báo có.
![[Screenshot_2024-09-13_at_14.50.07.png]]
---

Xem thêm: [[datatp-overview]]
