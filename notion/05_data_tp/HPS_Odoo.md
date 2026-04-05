# 🌵 HPS - Odoo

> Notion ID: `774e7cc474af43439eb1f1791be218c6`
> Parent: Data TP → Status: Interview / Meeting/Discuss
> Synced: 2026-04-05

## BFS DB

- PersonalProfile: thông tin bank của hps

### Hướng dẫn công cụ dụng cụ. tài sản.

Trong phần kế toán của Odoo có 1 phần gọi là khấu hao tài sản:

Theo luật ấy, thì bh em mua 1 cái máy tính khấu hao trong 3 năm (36 tháng), mỗi tháng mình khấu hao được bn % đó. Phần mềm kế toán sẽ cho chị tạo ra 1 cái bút toán, tự động hàng tháng nó sinh ra.

Mỗi 1 loại tài sản thì sẽ cách, phương thức tính toán, config chung. Vào `accounting config ⇒ Asset Type`: Cái này sẽ nói là loại tài sản đó khấu hao ntn? Lấy từ tài khoản nào ra và khấu hao vào tài khoản nào.

Ví dụ em mua cái máy tính 20.000 thì đầu tiên nó hạnh toán vào 1 số kế toán (1 account) là em phải chi ra 20tr. Và sau đó mỗi năm em được khấu hao bao nhiêu, thì tiền khấu hao kia được hiểu là nó đã bị khấu hao, đã bị hao hụt đi rồi.

Máy tính mua trả 1 lần là 20tr. khấu hao trong vòng 2 năm, 1 năm em mất khoảng 10tr. Như vậy năm đầu tiên tài sản của em có là 20tr, nhưng sang năm tài sản đó nó bị hao hụt, cũ đi thanh lý cũng chỉ được 10tr thôi. Như vậy số kế toán của em là em sẽ chuyển đi 10tr ở chỗ `Tài khoản cố định` của em sang cái `tài khoản hao hụt`. Coi như là đã mất đi rồi.

*(screenshot)*

**Computation:**
- Linear: 1 tháng em mất gần 1tr ⇒ Linear
- Trong thực tế có nhiều mô hình khấu hao khác, ví dụ mỗi năm mất đi 10%, mua 500tr năm đầu tiên mất 10% là mất 50tr, năm thứ 2 mất 10% là 10% của 450 tr
- Thường mọi người dùng Linear cho đơn giản, trong buôn bán, hoặc hàng tồn kho thì mới dùng cái Degressive thôi

**Auto-Confirm Asset:**
- Nếu ko tích thì nó sẽ tạo những bút toán là Draft và kế toán phải vào review và tự post.
- Còn nếu để confirm thì nó sẽ tự Post luôn

Thường thì các Asset Type thì sẽ có một bộ chuẩn, đầu tiên chị phải config các loại tài sản này cho chuẩn. Chị biết các nhóm tài sản này phân bổ về đâu? Thì đây là chuyện chị config loại tài sản, giờ đến chuyện mỗi khi chị có tài sản mới thì chị sẽ vào tạo tài sản. Thì chị chọn nhóm tài sản, khi chị chọn nhóm tài sản thì tự động các config nó đã đi theo nhóm này rồi.

**Ngày mua, ngày bắt đầu tính. Giá trị ban đầu, Salvage (giá trị bị khấu hao). Giá trị hạnh toán: giá trị bắt đầu hạnh toán. Giá trị còn lại.**

Mỗi Asset này sẽ tạo ra một bút toán.

Nếu hàng tháng, cuối tháng nếu chị kế toán chị muốn chốt ⇒ Generate Assets Entries thì nó sẽ quét qua các tài sản và tạo cho chị.

Mở lại các Asset, mở lại thấy nó gen, màu vàng là chưa post
*(screenshot)*

Lên kết quả kinh doanh hiện tại chị đang làm như thế nào?

Tất cả dữ liệu này đều được export ra và làm bằng excel được.

## Account

Account datatp chị Loan: **hps.loanpt/hps.loanpt@123**

Đối chiếu lại các số tài khoản, khoản mục, sổ nhật ký.

HAIHAN2302004: job chị Mỹ sai invoice chi hộ

### Đẩy các invoice từ phần mềm nghiệp vụ qua Odoo

**BFSOne:**
- Xuất hoá đơn trên phần mềm bfsone
- Sau đó, kế toán sẽ đẩy một lúc nhiều hoá đơn sang phần mềm Odoo bằng cách chọn ngày.

Không biết job nào xong, job nào chưa xong. Xuất hoá đơn trên PM bfsone, rồi đẩy qua kế toán. Phần mềm mới là đẩy qua kế toán. Xong xuất hoá đơn trên phầm mềm kế toán.

Hoá đơn bán đẩy trước vì phải xuất hoá đơn cho khách. Còn công nợ với agent và nhà cung cấp thì phải đợi confirm rồi mới đẩy sau. Có thể là cuối tháng. Hoặc lâu lâu chị ấy lại đẩy một lần nhiều hoá đơn qua.

Giờ chị ấy cần lọc ra những hoá đơn nào đã đẩy rồi và những hoá đơn nào chưa đẩy ạ.

**⇒ Đối với hoá đơn bán:** Lúc nào cần xuất thì đẩy, đẩy invoice xong thì mặc định sẽ là posted với invoice đó luôn và không cho chỉnh sữa. Hoặc người có quyền cao hơn sẽ được chỉnh sữa. Nhưng vẫn phải đối chiếu lại với kế toán.

**⇒ Đối với công nợ của nhà cung cấp hoặc agent:** đẩy tuỳ thời điểm, có thể là...

HAIHAN2302041, HLGHAN2301011

**Danh dấu những hoá đơn đã xuất:**
- Sẽ có các hoá đơn cus yêu cầu xuất, thì chị sẽ xuất ra trước.
- Các hoá đơn còn lại...

### Accountant

- Em nhờ người nhập các báo nợ, báo có giúp chị rồi.
- Có các báo nợ liên quan đến các hoá đơn mua, bán của của nghiệp vụ logistics mà có số tiền phát sinh bằng với các hoá đơn trên từng job ⇒ Thì em cũng gạch luôn hoá đơn đó.
- Còn các báo nợ, báo có khác (hầu như là của đại lý, Bee) em không gạch được. Vì số tiền trên từng báo nợ, báo có file excel chị gửi số tiền không giống với các hoá đơn trên từng job của tháng 1. ⇒ Chị tự đối soát để gạch những hoá đơn theo từng job tương ứng. ⇒ Chị hỗ trợ em thanh toán nốt các hoá đơn trong tháng 1.
- Hỗ trợ giúp em các phần như số tài khoản, sổ nhật ký, các khoản mục. Cấu hình kết chuyển xem cần sữa, bổ sung gì nữa không báo em bổ sung?
- Tiếp đó là phần số dư đầu kỳ, tạo kết chuyển kqkd tháng 1. Chạy các báo cáo tháng 1 để đối chiếu dữ liệu.
- Đẩy dữ liệu tháng 2, xem giúp em các dữ liệu đẩy qua đã đúng, đủ chưa (thông tin đối tác, tiền, sổ nhật ký, tài khoản, khoản mục)
- Tạo thanh toán cho các hoá đơn tháng 2, nhập các bút toán admin ⇒ Tạo kết chuyển ⇒ Xem các báo cáo.
- Em chỉ có thể ưu tiên hỗ trợ chị các mục này trước. Mục đích là đối chiếu dữ liệu đảm bảo đúng đủ trước. Sau đó 2 chị em bắt đầu mổ xẻ các bất cập, các phần kém hiệu quả, cần tối ưu trên phần mềm để hoàn thiện quy trình, nghiệp vụ của kế toán tiếp. Em cần phải có kết quả để báo cáo cho anh Tuấn rồi mới làm tiếp các yêu cầu khác được. Chị thấy thế nào ạ?

**Job cần sữa lại:** HAEHAN2301001

**Màn hình Booking Process:**
- Chỉ xem profit của một lô hàng: có thể bị lệch so với phần mềm kế toán theo các nguyên nhân:
  - Kế toán tách thuế cho debit thu nước ngoài, nhưng cus ko tách lúc nhập các chi phí đso.
  - Có các job hạch toán cả 2 tháng. ⇒ Khác so với báo cáo doanh thu tháng của kế toán.

### Đối soát tháng 1

Doanh thu trên báo cáo kết quả kinh doanh bị lệch.

Chị Loan ơi, anh Tuấn vừa mới báo lại em việc gạch hoá đơn ấy ạ. Hiện tại phần mềm vẫn hoạt động được theo các cách em đã hướng dẫn cho chị. Chị giúp em gạch các hoá đơn trong tháng 1, tháng 2 để chạy báo cáo với ạ.

Vì việc này cũng không phải trách nhiệm của chị, thì chị cứ ghi các giờ làm thêm anh Tuấn báo bên tập toàn trả cho chị ạ. Còn chị ko làm thì bên em phải mướn kế toán về nhập hoặc IT gạch thay ạ. Anh Tuấn cần chốt, chạy các báo cáo đảm bảo đúng, khớp dữ liệu ạ.

Tập đoàn xem báo cáo gì? xem ở đâu?

Chị cần báo cáo gì ở tập toàn chị list ra giúp em được không? Loại báo cáo? Xuất ở đâu?

### Quy trình bên bfsone

Thao tách gạch hoá đơn bên phần mềm bfsone, tạo báo nợ/ có bên phần mềm kế toán. Vậy các hoá đơn có đẩy sang phần mềm AV không? hay chỉ có các báo nợ/có thôi. Báo cáo kết quả kinh doanh thì xuất ở phần mềm nào? Báo cáo mã vụ việc thì chị đang làm tay hay xuất trên phần mềm nào?

SOA là tổng hợp từ các hoá đơn bao gồm bán và mua đúng ko chị? Ví dụ em lấy số liệu từ báo cáo sổ chi tiết công nợ 131, 331 và thêm các thông tin như mã master bill, house bill, … thì có đúng không?

Gạch hoá đơn chị ấy đang bận thì chị ấy hẹn cuối tuần này chị ấy làm. Về báo cáo thì bên trên tập đoàn mọi người chủ động vào xem. Hàng quý, chị ấy sẽ báo cáo Sale Profit như này. Tất cả những thông tin quan trọng có trên lô hàng thì đều được show ở đây. Chi phí sẽ được phân loại, tổng hợp lại. (Ví dụ doanh thu, chi phí, thu hộ). Ngoài ra bên bfsone có báo cáo tuổi nợ. Xem xem đối tác kia có khoản nợ bao lâu rồi. (tính từ thời điểm làm hàng)

Về việc hạch toán 1 hoá đơn, quy trình chị ấy đang làm là khi 1 lô hàng phát sinh chi phí từ bfsone. Chị ấy tạo thanh toán từ bfsone. Sau khi tạo thanh toán từ bfsone thì sẽ tạo thành báo nợ báo có trên AV. Sau đó chị ấy đẩy hoá đơn sang AV để hạch toán hoá đơn đó. (Đối ứng với thanh toán đã tạo, có dữ liệu để xuất các báo cáo). Từ phần mềm AV, chị ấy ko xem được hoá đơn nào đã được thanh toán và hoá đơn nào chưa. Chị ấy chỉ xem được hoá đơn đã được thanh toán trên phần mềm bfsone. các hoá đơn đó sau khi thanh toán cũng sẽ được trường là thông tin mã BN/BC bên phần mềm AV để keep track giữa 2 phần mềm.

### BFSOne sync

- **Tháng 5:** thiếu ngày 26,27/05/2023

- **Ms Hiền:**
  - Kiểm tra, đối soát lại dữ liệu tháng 1, 2
  - Nhập các bút toán tháng 3. Đối soát các hoá đơn tháng 3.
  - Thông tin account, phần mềm:
    - account: **flora.us@oclogis.com/flora@123**
    - web phần mềm kế toán: https://odoo-1.dev.datatp.net/web
    - web phần mềm forwarder: https://erp.datatp.cloud/

- **Đàn:** Chuẩn bị dữ liệu tháng 3, chuẩn bị các báo cáo tháng 1, 2 cho c Hiền.

**Review công việc:**
- Tháng 1, 2 đã đối soát với chị Loan rồi, giờ sẽ không đối soát lại. Chỉ cần kiểm tra lại số dư các đầu tài khoản đó.
- Bắt đầu đẩy dữ liệu tháng 3, nhập bút toán admin và tiến hành đối soát tiếp.

#### TODO

- Thêm mã liên kết giữa hoá đơn phần mềm forwarder và phần mềm kế toán.
- Kế toán yêu cầu:
  - đối với hoá đơn đầu vào: phải nhập mã hoá đơn (mã này theo thông tin chứng từ mà vender gửi) trước khi đẩy sang phần mềm kế toán.
  - đối với hoá đơn đầu ra (công ty tự xuất hoá đơn): Sau khi xuất hoá đơn, link lại số hoá đơn qua invoice của phần mềm forwarder. ⇒ Hỗ trợ theo dõi
- Làm báo cáo giống báo cáo mã vụ việc cho phần mềm kế toán. (có thể view xem chi tiết từng bút toán). ⇒ Hỗ trợ theo dõi, đối soát giữa phần mềm kế toán và phần mềm forwarder.
- Clean màn hình invoice item trong tab `invoice view`. Sử dụng màn hình invoice item model.
- Xin chị Loan báo cáo sổ nhật ký chung tháng 1, 2 cho c Hiền đối soát.

**Partner Issued:**
- Một partner có được hạch toán 2 loại tiền không? Ví dụ partner là guangdong, thì có thể có các bút toán liên quan đến tài khoản 331 (phải trả cho người bán trong nước) hoặc 331 (trả cho đại lý)
- Một số hoá đơn mua hàng bên fwd của Guangdong đang nhập cả tiền đô lẫn tiền việt. Cái này hoá đơn hạch toán về tài khoản nào?

**Bút toán lương:**
- Không thấy các bút toán liên quan đến việc chi lương cho nhân viên, chỉ thấy các bút toán liên quan đến thuế, bảo hiểm.
- Có thể tạo phiếu kế toán lương

**Cách hạnh toán lương:**
- Tính tiền lương và các khoản phụ cấp phải trả cho nhân viên
  - Nợ TK 241, 622, 623, 627, 641, 642: Tổng lương và phụ cấp
  - Có TK 334: Tổng lương và phụ cấp

1 Bút toán ghi nhận tổng tiền lương (642 - chi phí nhân viên quản lý) đối ứng với các chi phí bảo hiểm, công đoàn (338, 334). Bút toán này, 642 thì để tên công ty mình, còn các tài khoản bảo hiểm để tên công ty bảo hiểm, công đoàn.

```bash
./runtime/hpsvn.sh rename-module --from=account_invoice_template --to=account_move_ext
```

#### Nghiệp vụ lương

- **Tính lương:** ⇒ Tạo phiếu kế toán (bút toán)
  - Nợ TK 6422, 6421…
  - Có TK 334
- **Chi lương:** ⇒ Tạo phiếu chi
  - Nợ 334
  - Có 111
- **Các khoản trích theo lương (doanh nghiệp chịu):** Tạo phiếu kế toán (bút toán) gồm BHXH, Bảo hiểm y tế, thất nghiệp
  - Nợ TK 6422, 6421…
  - Có 3383 (BHXH), 3384 (BHYT), 3385 (BHTN)
- **Các khoản trừ vào lương:** Tạo phiếu kế toán
  - Nợ 334
  - Có 3383…

#### Xem hoá đơn thanh toán

- Ở nghiệp vụ 16, Account Receivable.
  - Xem được mã bảng kê.
- Copy mã bảng kê vào nghiệp vụ 17: Debit Note

Nhóm theo bảng kê ⇒ Nhóm theo mã vụ việc ⇒ Nhóm theo Partner ⇒ Khớp tiền hoá đơn thì gạch.

Làm sao để biết việc gạch hoá đơn, thanh toán là đúng. Xem những sổ nào, báo cáo nào? Setup công cụ dụng cụ lên phần mềm.

Cột Paid Date ở trên bảng nghiệp vụ 16 là ngày gì?

**Lỗi:**
- Đơn vị trên hoá đơn phải để 3 số thập phân, sữa cả phần mềm forwarder và phần mềm Odoo (xem job HSIHAN2301001 trên 2 phần mềm để xem chi tiết)
- Số báo nợ liên kết với hoá đơn thanh toán trên debit note không match với BN kế toán xuất trên sổ nhật ký chung. (xem số bảng kê HSBK2301/0051 trên phần mềm BFSOne để xem chi tiết)
- Bảng cân đối: V. Tài sản ngắn hạn khác ⇒ Sai

**Request:**
- Tối ưu việc gạch nợ các hoá đơn
  - Tạo màn hình list hoá đơn, báo nợ, báo có, phiếu thu, phiếu chi
  - Gồm có các thông tin: mã vụ việc, mã chứng từ (mã hoá đơn, số hoá đơn, mã báo nợ, báo có, …), tên đối tác, tổng tiền, ngày, tên người tạo phiếu nếu cần.
  - Màn hình danh sách, mặc định nhóm theo đối tác ⇒ case reference. Sắp xếp theo cột tổng tiền.
  - Các chức năng:
    - Case 1: trường hợp đã có báo có, báo nợ sẵn (khách hàng đã trả tiền trước hoặc còn dư tiền và chờ hoá đơn về sau) ⇒ Chọn các hoá đơn và BN, BC tương ứng và click chọn để reconcide.
    - Case 2: trường hợp chưa có báo nợ, báo có: Quy trình hoá đơn về ⇒ tạo thanh toán ⇒ Hữu dụng trong trường hợp gom nhiều job để tạo thành 1 báo nợ, báo có. Chọn các hoá đơn muốn gom thanh toán 1 lần và tiến hành thanh toán.

- Theo dõi trạng thái hoá đơn, chi phí trên từng lô hàng.
  - Trên phần mềm fwd:
    - Xem được chi phí (từng chi phí) đã được thanh toán hay chưa?
    - Ngày thanh toán, người thanh toán,
    - Mã account.move, mã thanh toán,
    - Số hoá đơn:
      - đối với hoá đơn mua, số đơn kế toán sẽ tự nhập theo số trên hoá đơn NCC
      - Với hoá đơn bán, vì hoá đơn xuất ở phần mềm Odoo, nên phải sync lại số hoá đơn từ phần mềm Odoo qua chi phí bên phần mềm fwd.

- Trả: Hoá đơn C131, PC N131
- Thu: PT: N331, Hoá đơn C331

Chi hộ của EAGLE đang hạch toán sai. Tạo phiếu thu của EAGLE, thay vì tạo Phiếu chi.

*(screenshot)*

Tiền đô \* tỷ giá ra tổng tiền không đúng. Dòng 1, 3

*(screenshot)*

Xem lại bút toán này, ghi nhận lỗ

*(screenshot)*

- Tỷ giá nhân không khớp tiền

HLGHAN2301003: check lại lô này, dữ liệu từ fwd và kế toán không giống nhau

#### Khách hàng Đại lý, API trả về tiền VND, dữ liệu kế toán tiền USD

*(screenshot)*
*(screenshot)*
*(screenshot)*

**Tăng giảm tài sản:**
- Nguyên giá cuối kỳ = giá trị tài sản + tăng trong kỳ - giam trong kì
- khấu hao cuối kỳ = khấu hao đầu kỳ + khấu hao trong kì

- Kết chuyển tiền đô, Odoo đang kết chuyển theo tiền việt
  *(screenshot)*
  *(screenshot)*
  - Dư cuối kỳ ngoại tệ sai.
