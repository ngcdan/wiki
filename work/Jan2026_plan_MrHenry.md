Henry,

Kế hoạch tổng thể thì như tôi nói, bên tôi bám theo các kế hoạch đã trình lên bộ Khoa học công nghệ bao gồm:

- Xây dựng hạ tầng cloud, môi trường cloud lại được chia tiếp thành các hệ thống production, beta, develop…
- Thiết kế phần mềm theo kiến trúc MSA (Micro Service Architecture) , chia hệ thống thành nhiều module nhỏ và có thể đấu nối với nhau và chia ra cho các team làm việc gần như độc lập như CRM, TMS , Khai Quan. Nếu một module hỏng , có thể thuê, đi mua hay giao cho đội khác làm. Hoặc trong tương lai có thể nâng cấp, làm lại từng phần một cách linh hoạt và dễ dàng.
- Hiện trạng thì bên tôi đã dựng được hệ thống cloud production và đưa vào sử dụng.  Tổ chức lại code theo kiến trúc MSA cũng được khoảng 70%.
- Ngoài ra kiến trúc MSA + SSO còn cho phép đí lấy các đồ có sẵn hoặc đi mua để tích hợp triển khai cho nhanh. Cụ thể bên mình sử dụng lại sản phẩm Keycloak cho việc SSO, Moodle cho hệ thống LMS,  Wikijs cho document,  Nextcloud  cho hệ thống office hay Talk sẽ được tích hợp với Mobile thay cho Zalo…
- Hiện bên tôi đang có CRM, TMS, OKR/KPI đã triển khai tốt và tiếp túc phát triển.
- Ngoài ra còn có hệ thống Mobile sẽ được release thử nghiệm vào tuần tới và có hệ thống khai quan cần đấu nối với BFS One nữa thì sẽ sử lý được một số công việc tự động cho bộ phận Log.

Kế hoạch bên tôi thì như vậy 1 năm nữa ông có hỏi tôi kế hoạch thế nào thì chắc vẫn như vậy. Chủ chương của tôi là Bottom Up làm chắc từng việc 1 bên dưới  rồi mới làm tiếp lên. Như giờ TMS , CRM làm đủ tốt bước đầu triển khai có người dùng thì sẽ tăng tốc , thuê người làm cho nhanh hơn. Còn phần khai quan thì đang thử nghiệm hy vọng triển khai được thành công có người dùng bước đầu thì cũng sẽ mới tính chuyện thêm người, thêm tiền để làm


Việc họp 2 tuần 1 lần tôi mong muốn chỉ tập chung các việc gạch đầu dòng , các chuyện bên dưới ko đồng thuận. Các việc tôi muốn giải quyết trong cuộc họp này:
-  Ra chính sách quản tý  tài nguyên IT, bao gồm code , db , máy móc… Tôi chủ trương quản lý hệ thống theo phương thức mở, và ai miễn có khả năng đều có quyền tiếp cận tìm hiểu hoặc làm thêm các cái mình cần.
- Các dự án đều phân ra cho các nhóm quản lý làm dộc lập tuy nhiên nhóm đó phải duy trì dự án theo phương án mở , tức là các nhóm khác có quyền vào xem lấy code về chạy chỉnh sửa hoặc làm thêm các cái mình cần , miễn là không ảnh hưởng hay vi phạm các quy định của công ty. Nhóm quản lý dự án phải duy trị hệ thống code, document , hệ thống alpha, beta sao thuận tiện nhất cho các nhóm khác vào xem và chạy thử nghiệm.
- Tôi muốn trong cuộc họp tới bên Quí phải đưa code và hướng dẫn Đàn chạy hệ thống BFS One để Đàn thay thế hệ thống lưu trữ dùng S3 và làm các việc đấu nối BFS One với phần khai quan.
- Phần Nam viét liên quan đến các định hướng, chính sách của công ty mà tôi muốn xây dựng.

---

**ĐỊNH HƯỚNG MÔ HÌNH PHÁT TRIỂN PHẦN MỀM CHO OF1**

**I. Thực trạng và vấn đề hiện tại**

- **_Tổng quan_**

Phần mềm ứng dụng cho BeeLogistics không phải là bài toán quá khó về mặt công nghệ, mà là một hệ thống lớn, nhiều phân hệ, liên quan trực tiếp đến vận hành cốt lõi của công ty (BFS, AV, HRM, Logistics, Khai quan…).

- **_Các trở ngại hiện tại của OF1:_**
  - Chiến lược

- Hiện OF1 chưa có chiến lược tổng thể cũng như các kế hoạch cho phát triển của công ty. Mọi việc vẫn dừng ở định hướng.
- Vấn đề nhân sự chủ chốt cũng đang tồn tại rất nhiều các vấn đề tiềm ẩn mâu thuẫn cho phát triển lâu dài.

2.2. Bài toán nhân lực và chi phí

- Phần mềm có nhiều phân hệ nên cần nhiều nhân lực tham gia đồng thời.
- Cân đối nhân lực và chi phí phù hợp với chiến lược phát triển chung (điều này rất quan trọng trong kế hoạch phát triển bền vững của công ty).
- Sản phẩm hiện tại chủ yếu phục vụ nội bộ Bee, cần khảo sát kỹ nếu muốn đưa sản phẩm ra thị trường.

2.3. Mô hình phát triển hiện tại khi quá ít người tham gia phát triển nên sẽ gặp một số vấn đề:

- Thiếu góc nhìn tổng quan
- Thiếu việc đánh giá lại khách quan sản phẩm
- Thiếu backup nhân sự
- Tốc độ chậm, rủi ro cao

2.4. Các vấn đề khi tổ chức thực hiện:

- Tổ chức nhóm chưa đủ mở và độc lập
- Sản phẩm đã định hình nhưng:
- Hoặc sử dụng công nghệ đã cũ, đóng, logic và quy trình cứng nhắc (BFSOne/AV)
- Thiết kế DB, luồng dữ liệu, logic xử lý (vẫn bị ràng buộc bởi AV)
- Chưa có tính mở
- Độ đáp ứng của hệ thống còn chậm
- Không đáp ứng tốc độ phát triển chung
- Hoặc việc phát triển chạy theo yêu cầu sử dụng mà chưa có quy hoạch tổng thể (các phần mềm khác đang phát triển)

2.5. Cần có một số yêu cầu chung, ngay cho giai đoạn này

- Hệ thống phải có tính mở
- Cần hệ thống tài liệu rõ ràng, đầy đủ
- Dễ tiếp cận, dễ chạy thử
- Công nghệ, kiến trúc phải lấy hiệu quả để đanh giá chính

**II. Định hướng phát triển bền vững**

Để phát triển phần mềm thành công, cần hội đủ 3 yếu tố cốt lõi:

- Sản phẩm hướng đến người sử dụng và có lượng người sử dụng thường xuyên: Hiện tại nhu cầu sử dụng các ứng dụng trong nội bộ BeeLogistics rất cao, bản thân các ứng dụng hiện tại đều góp phần tăng hiệu quả trong vận hành, sản xuất
- Thu hút và duy trì nguồn lực để phát triển sản phẩm. Đây là vấn đề rất cần thiết và song hành với chiến lược phát triển sản phẩm. Hiện tại OF1 không thiếu nguồn hỗ trợ tài chính cũng như đầu tư (đầu tư vào team Tuấn, Lepus,…), tuy nhiên tầm nhìn, kỹ năng quản trị, công nghệ, kể cả tính cách nhân sự chưa đáp ứng hoặc phù hợp để có những bước tiến đột phá như kỹ vọng.
- Nền tảng công nghệ. Công nghệ hiện nay phát triển rất nhanh, chu kỳ vòng đời công nghệ cũng rất ngắn nên việc định hướng công nghệ để có thể phát triển ổn định là điều cần đặt lên hàng đầu. Định hướng trong thời gian tiếp theo:
- Áp dụng kiến trúc mở, cloud, MSA:
- Quản trị tài nguyên linh hoạt
- Phân quyền an toàn, linh hoạt theo nhiều hình thức quản trị: mô hình tổ chức, nhóm, ứng dụng, nghiệp vụ, chức năng…

**III. Đề xuất mô hình tổ chức mới**

**_1\. Tổ chức công ty theo hướng quản trị hiện đại và mở_**

- Tài nguyên, mã nguồn và các database phải được quản trị tập trung và phân cấp, phân quyền
- Việc phân quyền được phê duyệt phải từ BoD, không phải từ các đơn vị trong công ty
- Các nhân viên đều có thể truy cập khi được cấp quyền
- Tách biệt Prod và dev để mọi nhân viên đều có thể truy cập tài nguyên, nghiên cứu, chạy thử và cập nhật khi đc cấp quyền.

**_2\. Tổ chức bộ phận phát triển phần mềm_** thành nhiều nhóm nhỏ, độc lập, theo domain, dự án có vòng đời rõ ràng ví dụ các nhóm: BFS One, TMS, CRM, Logistics, Khai quan…

Các nhóm có thể chủ động đề xuất, phát triển sản phẩm độc lập tuy nhiên vẫn phải theo chiến lược chung. Do hoạt động theo cơ chế nhóm, dự án nên hoàn toàn có thể phân bổ nhân sự linh hoạt nhằm phân tải công việc cũng như có backup khi cần.

**IV. Kế hoạch triển khai đề xuất (phần kỹ thuật)**

**_Giai đoạn 1:_** Chuẩn hoá, tập trung hạ tầng và dữ liệu

- Tài nguyên hệ thống: Máy chủ, lưu trữ, hệ thống mạng, quyền truy cập (k8s, VM, S3, keycloak…)
- Tài nguyên phần mềm: Source-code, Database, chuẩn hoá API, chuẩn hoá các Document

**_Giai đoạn 2:_** Tách dần BFS One theo MSA

Tách các phần: Lưu trữ dữ liệu, báo cáo, tích hợp khai quan, các module mới cần tách biệt về hoạt động với phần mềm kế toán AV

**_Giai đoạn 3:_** Phối hợp giữa các nhóm

**V. Dựa vào các phân tích, định hướng trên, Tuấn yêu cầu những việc trước mắt với nhóm Quý:**

- **_Tập trung code của nhóm Quý đang phát triển lên nền tảng quản lý code chung của công ty_**
- **_Phối hợp, hướng dẫn Đàn:_**
- **_Xây dựng phần lưu trữ dữ liệu trên hệ thống Bee Private Cloud S3_**
- **_Đấu nối BFS One với hệ thống khai quan team Tuấn đang phát triển_**
- **_Cùng thử nghiệm và đánh giá khi hoạt động với: Mô hình mở, Mô hình nhiều nhóm cùng tham gia, Kiểm chứng khả năng mở rộng thực tế_**

**VI. Tổng kết**

Vấn đề của Bee đơn thuần không nằm ở kỹ thuật mà ở:

- Cách tổ chức con người
- Tính mở và liên kết giữa các hệ thống
- Quản trị nguồn nhân lực

Để xây dựng hệ thống với quy mô lớn, đáp ứng nhu cầu của Bee và của khách hàng sau này:

**_Cần tăng cường đội ngũ --> Cần có chính sách và môi trường tốt để thu hut nhân lực_**