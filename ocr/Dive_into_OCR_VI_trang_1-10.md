# Dive into OCR (Tìm hiểu sâu về OCR)

**动手学 OCR — Dive into OCR**

*Baidu | PaddlePaddle (飞桨)*

---

## Thông tin tác giả

Chenxia Li, Weiwei Liu, Ruoyu Guo, Xiaoting Yin
Kaitao Jiang, Yongkun Du, Yuning Du
Lingfeng Zhu, Runjie Jin, Keying Liu, Yehua Yang
Ran Bi, Xiaoguang Hu, Dianhai Yu, Yanjun Ma

*Ngày 12 tháng 8 năm 2022*

---

## MỤC LỤC

### 1. Lời nói đầu (Preface) — trang 1
- 1.1 Về cuốn sách — 1
  - 1.1.1 Nội dung và cấu trúc — 2
  - 1.1.2 Đối tượng độc giả — 3
- 1.2 Cộng đồng — 3
- 1.3 Lời cảm ơn — 3

### 2. Kiến thức tiên quyết của khóa học (Course Prerequisites) — trang 5
- 2.1 Kiến thức nền tảng — 5
- 2.2 Chuẩn bị môi trường cơ bản — 5
- 2.3 Lấy mã nguồn và chạy thử — 6
- 2.4 Truy cập thông tin — 6
- 2.5 Hỏi đáp hỗ trợ — 6

### 3. Giới thiệu công nghệ OCR (Introduction to OCR Technology) — trang 7
- 3.1 Bối cảnh kỹ thuật của OCR — 7
  - 3.1.1 Các kịch bản ứng dụng — 7
  - 3.1.2 Các thách thức kỹ thuật — 9
- 3.2 Các thuật toán OCR tiên tiến — 10
  - 3.2.1 Phát hiện văn bản (Text Detection) — 10
  - 3.2.2 Nhận dạng văn bản (Text Recognition) — 12
  - 3.2.3 Nhận dạng cấu trúc tài liệu — 14
  - 3.2.4 Các công nghệ khác — 18
- 3.3 Thực hành công nghiệp của công nghệ OCR — 19
  - 3.3.1 Những khó khăn trong thực tiễn công nghiệp — 19
  - 3.3.2 Bộ phát triển OCR cấp công nghiệp — PaddleOCR — 20
- 3.4 Tổng kết — 28
- 3.5 Tài liệu tham khảo — 28

### 4. Phát hiện văn bản (Text Detection) — trang 31
- 4.1 Giới thiệu các phương pháp phát hiện văn bản — 32
  - 4.1.1 Phát hiện văn bản dựa trên hồi quy — 33
  - 4.1.2 Phát hiện văn bản dựa trên phân đoạn — 37
- 4.2 Thực hành thuật toán phát hiện văn bản DBNet — 41
  - 4.2.1 Bắt đầu nhanh — 42
  - 4.2.2 Triển khai chi tiết thuật toán DB — 45
  - 4.2.3 Huấn luyện mô hình DB — 51
  - 4.2.4 Hỏi đáp về phát hiện văn bản — 71
  - 4.2.5 Bài tập — 76
- 4.3 Tổng kết — 76
- 4.4 Tài liệu tham khảo — 77

### 5. Nhận dạng văn bản (Text Recognition) — trang 79
- 5.1 Giới thiệu các phương pháp nhận dạng văn bản — 81
  - 5.1.1 Nhận dạng văn bản thông thường — 81
  - 5.1.2 Nhận dạng văn bản không thông thường — 84
- 5.2 Thực hành thuật toán nhận dạng văn bản CRNN — 87
  - 5.2.1 Bắt đầu nhanh — 88
  - 5.2.2 Triển khai chi tiết thuật toán CRNN — 88
  - 5.2.3 Huấn luyện mô hình CRNN — 102
  - 5.2.4 Hỏi đáp về nhận dạng văn bản — 111
  - 5.2.5 Bài tập — 116
- 5.3 Tổng kết — 116
- 5.4 Tài liệu tham khảo — 117

### 6. Hệ thống và chiến lược PP-OCR — trang 119
- 6.1 Giới thiệu về PP-OCR — 119
  - 6.1.1 Giới thiệu hệ thống PP-OCR và chiến lược tối ưu — 119
  - 6.1.2 Giới thiệu hệ thống PP-OCRv2 và chiến lược tối ưu — 120
- 6.2 Chiến lược tối ưu hóa PP-OCR — 121
  - 6.2.1 Phát hiện văn bản — 122
  - 6.2.2 Bộ phân loại hướng — 133
  - 6.2.3 Nhận dạng văn bản — 139
- 6.3 Giải thích chiến lược tối ưu hóa PP-OCRv2 — 148
  - 6.3.1 Giải thích chi tiết tối ưu hóa mô hình phát hiện văn bản — 149
  - 6.3.2 Giải thích chi tiết tối ưu hóa mô hình nhận dạng văn bản — 161
- 6.4 Tổng kết — 171
- 6.5 Bài tập — 171

### 7. Suy luận và triển khai PP-OCRv2 — trang 173
- 7.1 Tổng quan về suy luận và triển khai — 173
  - 7.1.1 Giới thiệu — 173
  - 7.1.2 Chuẩn bị môi trường — 174
- 7.2 Suy luận Python dựa trên Paddle Inference — 175
  - 7.2.1 Giới thiệu — 175
  - 7.2.2 Suy luận mô hình phát hiện văn bản PP-OCRv2 — 176
  - 7.2.3 Suy luận mô hình phân loại hướng PP-OCRv2 — 187
  - 7.2.4 Suy luận mô hình nhận dạng văn bản PP-OCRv2 — 190
  - 7.2.5 Suy luận đầu-cuối của hệ thống PP-OCRv2 — 193
  - 7.2.6 Suy luận với gói WHL trong PP-OCRv2 — 199
- 7.3 Suy luận C++ dựa trên Paddle Inference — 202
  - 7.3.1 Chuẩn bị mô hình — 202
  - 7.3.2 Biên dịch thư viện OpenCV — 202
  - 7.3.3 Tải thư viện suy luận của **Paddle Inference** — 203
  - 7.3.4 Biên dịch mã suy luận của PaddleOCR — 204
  - 7.3.5 Chạy hệ thống PP-OCRv2 — 204
- 7.4 Triển khai dịch vụ với **Paddle Serving** — 205
  - 7.4.1 Giới thiệu Paddle Serving — 206
  - 7.4.2 Chuẩn bị dữ liệu suy luận và môi trường triển khai — 206
  - 7.4.3 Chuẩn bị triển khai mô hình — 207
  - 7.4.4 Triển khai pipeline Paddle Serving — 208
  - 7.4.5 Hỏi đáp — 210
- 7.5 Suy luận đầu-cuối dựa trên Paddle Lite — 210
  - 7.5.1 Chuẩn bị môi trường — 211
  - 7.5.2 Chuẩn bị mô hình — 211
  - 7.5.3 Biên dịch — 211
  - 7.5.4 Tải lên các thiết bị di động như điện thoại — 211
  - 7.5.5 Chạy — 212
  - 7.5.6 Hỏi đáp — 212
- 7.6 Bài tập về nhà — 213

### 8. Công nghệ phân tích tài liệu — trang 215
- 8.1 Giới thiệu công nghệ phân tích tài liệu — 215
  - 8.1.1 Phân tích bố cục (Layout Analysis) — 215
  - 8.1.2 Nhận dạng bảng (Table Recognition) — 220
  - 8.1.3 Hỏi đáp tài liệu (Document VQA) — 228
- 8.2 Thực hành nhận dạng bảng OCR — 236
  - 8.2.1 Bắt đầu nhanh — 236
  - 8.2.2 Giải thích nguyên lý dự đoán — 238
  - 8.2.3 Huấn luyện — 249
  - 8.2.4 Tổng kết — 254
  - 8.2.5 Bài tập — 254
- 8.3 Thực hành DOC-VQA SER — 254
  - 8.3.1 Bắt đầu nhanh — 254
  - 8.3.2 Giải thích nguyên lý — 257
  - 8.3.3 Huấn luyện — 264
  - 8.3.4 Bài tập — 270

### 9. Thuật toán đầu-cuối (End-to-end) — trang 271
- 9.1 Bối cảnh — 271
- 9.2 Các thuật toán — 272
  - 9.2.1 Thuật toán nhận dạng văn bản thông thường đầu-cuối — 272
  - 9.2.2 Thuật toán nhận dạng văn bản có hình dạng tùy ý đầu-cuối — 274
- 9.3 Tổng kết — 284
- 9.4 Tài liệu tham khảo — 285

### 10. Thuật toán tiền xử lý — trang 287
- 10.1 Bối cảnh — 287
- 10.2 Tăng cường dữ liệu (Data Augmentation) — 288
  - 10.2.1 Tăng cường dữ liệu tiêu chuẩn — 289
  - 10.2.2 Kỹ thuật biến đổi hình ảnh — 296
  - 10.2.3 Kỹ thuật cắt xén hình ảnh — 297
  - 10.2.4 Kỹ thuật trộn hình ảnh — 300
- 10.3 Nhị phân hóa hình ảnh — 301
  - 10.3.1 Ngưỡng toàn cục — 301
  - 10.3.2 Ngưỡng cục bộ — 301
  - 10.3.3 Kỹ thuật dựa trên Học sâu — 302
- 10.4 Khử nhiễu — 303
  - 10.4.1 Lọc miền không gian — 303
- 10.5 Lọc miền biến đổi — 306
  - 10.5.1 BM3D — 306
  - 10.5.2 Phương pháp dựa trên Học sâu — 307
- 10.6 Tổng kết — 307
- 10.7 Tài liệu tham khảo — 307

### 11. Thuật toán tổng hợp dữ liệu — trang 309
- 11.1 Bối cảnh — 309
- 11.2 Thuật toán tổng hợp dữ liệu — 309
- 11.3 Tổng kết — 315
- 11.4 Tài liệu tham khảo — 315

---

# CHƯƠNG 1 — LỜI NÓI ĐẦU (PREFACE)

Trong những năm gần đây, cùng với sự phát triển của công nghệ, Nhận dạng ký tự quang học (Optical Character Recognition — OCR) đã được ứng dụng rộng rãi trong nhiều kịch bản khác nhau. Các thuật toán phát hiện và nhận dạng văn bản dựa trên framework học sâu đã được sử dụng phổ biến trong đời sống hằng ngày, ví dụ như: nhận dạng biển số xe, nhận dạng thông tin thẻ ngân hàng, nhận dạng thông tin chứng minh thư, nhận dạng thông tin vé tàu, v.v. Ngoài ra, công nghệ OCR phổ thông còn được sử dụng rộng rãi cho các tác vụ như giám sát an toàn nội dung, hoặc kết hợp với các đặc trưng hình ảnh để hoàn thành những tác vụ như hiểu video và tìm kiếm video.

Một mặt, chúng ta thấy không gian ứng dụng rộng lớn của OCR, nhưng mặt khác cũng nhận ra rằng trên thế giới có rất ít cuốn sách giới thiệu một cách toàn diện về OCR từ lý thuyết đến thực hành. Điều này khiến nhiều kỹ sư thuật toán phải đi qua nhiều vòng vèo mới có thể làm quen và hiểu được lĩnh vực này. Đồng thời, trong các ứng dụng thực tế, đặc biệt là trong các kịch bản tổng quát, các bài toán OCR vẫn phải đối mặt với một số thách thức như: biến dạng affine, vấn đề tỉ lệ kích thước, ánh sáng không đủ, ảnh chụp bị mờ và những khó khăn kỹ thuật khác. Bên cạnh đó, các ứng dụng OCR thường phải xử lý lượng dữ liệu khổng lồ nhưng đòi hỏi xử lý theo thời gian thực. Hơn nữa, ứng dụng OCR thường được triển khai trên phần cứng di động hoặc nhúng, vốn có hạn chế về dung lượng lưu trữ và năng lực tính toán — do đó có yêu cầu cao về kích thước và tốc độ dự đoán của mô hình OCR. Việc chia sẻ những nội dung rất quan trọng đối với người thực hành này chắc chắn sẽ thúc đẩy quá trình nâng cấp ngành công nghiệp liên quan đến OCR và việc triển khai công nghệ học sâu OCR trong công nghiệp.

Dựa trên động lực đó, xoay quanh các nội dung cốt lõi của ứng dụng OCR trong công nghiệp, và để tri ân cuốn sách nổi tiếng toàn cầu "Dive into Deep Learning", cuốn sách mang tên "Dive into OCR" này được đồng kiến tạo bởi các trường đại học, doanh nghiệp và các nhà phát triển cộng đồng, mã nguồn mở toàn bộ nội dung và mã trên GitHub, đồng thời cung cấp khóa học video đi kèm để các nhà phát triển có thể học và sử dụng.

Vì cuốn sách được hoàn thành bởi nhiều nhà phát triển, các biên tập viên sau này đã cố gắng thống nhất phong cách nhiều nhất có thể, nhưng khó tránh khỏi sai sót. Nếu có nội dung thiếu sót hoặc lỗi, hoan nghênh bạn đọc đóng góp ý kiến và sửa chữa qua mục thảo luận trên GitHub, và cũng hoan nghênh bạn gửi trực tiếp Pull Request để cùng tham gia xây dựng.

## 1.1 Về cuốn sách

Quy trình làm việc của cuốn sách này cũng được thực hiện dưới hình thức gửi và bảo trì mã trên GitHub kết hợp với tích hợp jupyter notebook, công thức và hình ảnh, bao gồm những phương pháp và ứng dụng mới nhất của OCR, và được cập nhật liên tục. Về mặt nội dung, sách chủ yếu giới thiệu công nghệ học sâu dựa trên tính khả thi của ứng dụng thực tế. Về mặt nội dung, chúng tôi không dám tuyên bố rằng đây là một sách giáo khoa nghiêm ngặt, nhưng chắc chắn đây là một hướng dẫn sống động với mã có thể thực thi giúp các nhà phát triển nhanh chóng triển khai các dự án OCR.

Chúng tôi tin tưởng mạnh mẽ vào tầm quan trọng của việc học thực hành đối với học sâu, và chúng tôi cũng cố gắng trình bày càng nhiều càng tốt cách triển khai một phương pháp nhất định bằng mã, cũng như giải thích ý tưởng và chi tiết triển khai của thiết kế thuật toán. Cuốn sách này không chỉ dành cho người mới bắt đầu OCR muốn nhanh chóng hiểu được các khái niệm cơ bản và một số thuật toán then chốt trong lĩnh vực OCR, mà còn dành cho các kỹ sư thuật toán muốn nhanh chóng khởi động dự án của mình dựa trên mã ví dụ và các chương trình suy luận, triển khai.

Đối với dự án này, chúng tôi hy vọng đạt được các mục tiêu sau:

1. Truy cập miễn phí trực tuyến vào các tệp mã nguồn cho tất cả mọi người.

2. Sử dụng cuốn sách như một cầu nối để thu hút các nhà nghiên cứu OCR cùng xây dựng và chia sẻ, công bố các kết quả nghiên cứu mới nhất của họ, mở rộng phạm vi kỹ thuật nhiều nhất có thể, và trở thành một sách giáo khoa tổng quan nghiên cứu khoa học cho các sách công nghệ OCR.

3. Tất cả các thuật toán đều chứa mã có thể thực thi, cho thấy cho các kỹ sư thuật toán OCR cách giải quyết vấn đề trong thực tế, và trở thành một tài liệu hướng dẫn cho triển khai công nghiệp OCR.

4. Nội dung sách được đồng xây dựng và chia sẻ bởi toàn cộng đồng, với các bản cập nhật liên tục, theo kịp lĩnh vực học sâu vẫn đang phát triển rất nhanh.

5. Các câu hỏi và trả lời về chi tiết kỹ thuật có thể được thảo luận trong các issues và discussions trên GitHub của PaddleOCR, cho phép mọi người trả lời câu hỏi của nhau và trao đổi kinh nghiệm.

### 1.1.1 Nội dung và cấu trúc

Cấu trúc các chương:

- **Phần 1**: Lời nói đầu và Kiến thức tiên quyết
- **Phần 2 (Chương 3–7)**: Giới thiệu OCR → Phát hiện văn bản → Nhận dạng văn bản → Hệ thống PP-OCR → Suy luận & Triển khai PP-OCRv2
- **Phần 3 (Chương 8–11)**: Phân tích tài liệu, Thuật toán đầu-cuối, Tiền xử lý, Tổng hợp dữ liệu

Sơ đồ cấu trúc:

```
        [1. Preface]
        [2. Course Prerequisites]
               │
   ┌───────────┼───────────┐
   ▼           ▼           ▼
[10. Pre-     [3. Intro   [9. End-to-end
 processing    to OCR      Algorithm]
 Algorithm]    Technology]
[11. Data      │
 Synthesis     ▼          [8. Document
 Algorithm]   [4. Text     Analysis
              Detection]    Technology]
               │           (Layout, Table,
               ▼            Document VQA)
              [5. Text
              Recognition]
               │
               ▼
              [6. PP-OCR
              System and Strategy]
               │
               ▼
              [7. Inference and
               Deployment of PP-OCRv2]
```

- Phần đầu là lời nói đầu và kiến thức sơ bộ của cuốn sách, bao gồm chỉ mục kiến thức và các liên kết tài nguyên cần thiết trong quá trình sử dụng sách.

- Phần thứ hai của cuốn sách, các chương 3–7, giới thiệu các khái niệm, ứng dụng và thực tiễn công nghiệp liên quan đến năng lực phát hiện và nhận dạng cốt lõi của OCR. Trong "Giới thiệu công nghệ OCR", chúng tôi giải thích tổng quát các kịch bản ứng dụng và thách thức của OCR, các khái niệm cơ bản của công nghệ, và các điểm nhức nhối trong ứng dụng công nghiệp. Sau đó, hai tác vụ cơ bản của OCR được giới thiệu trong các chương "Phát hiện văn bản" và "Nhận dạng văn bản", và mỗi chương đi kèm với phần giải thích thuật toán đến chi tiết mã và bài tập thực hành. Chương 6 và 7 trình bày chi tiết các mô hình loạt PP-OCR. PP-OCR là một hệ thống OCR cho các ứng dụng công nghiệp, dựa trên các mô hình phát hiện và nhận dạng thông qua một loạt chiến lược tối ưu để đạt được mô hình SOTA công nghiệp tổng quát, đồng thời hỗ trợ nhiều giải pháp suy luận và triển khai khác nhau để giúp các doanh nghiệp nhanh chóng triển khai ứng dụng OCR.

- Phần thứ ba của cuốn sách, các chương 8–11, giới thiệu các ứng dụng vượt ra ngoài engine OCR hai giai đoạn, bao gồm tổng hợp dữ liệu, các thuật toán tiền xử lý, và các mô hình đầu-cuối, tập trung vào năng lực OCR trong các kịch bản tài liệu, bao gồm phân tích bố cục, nhận dạng bảng, và hỏi đáp tài liệu trực quan — một lần nữa thông qua sự kết hợp giữa thuật toán và mã giúp người đọc hiểu sâu và áp dụng được.

### 1.1.2 Đối tượng độc giả

Cuốn sách này dành cho sinh viên, nhà nghiên cứu và kỹ sư muốn tìm hiểu và áp dụng kiến thức OCR một cách chuyên sâu. Đây là một cuốn sách thực hành trong lĩnh vực OCR, đòi hỏi kiến thức cơ bản về học sâu, học máy và thị giác máy tính.

## 1.2 Cộng đồng

Có hai cách chính để thảo luận về cuốn sách này trong PaddleOCR:

1. **[i18n]** Mục *discussions* trên GitHub của PaddleOCR chủ yếu dành cho các nhà phát triển quốc tế để thảo luận và trao đổi kỹ thuật, bao gồm nhưng không giới hạn ở các thuật toán lý thuyết, công nghệ và ứng dụng.

2. **[Tiếng Trung]** *Community regular season* của PaddleOCR là hoạt động cộng đồng tiếng Trung với OCR làm trọng tâm, cung cấp các nhiệm vụ mở đa cấp độ và đa chiều cho các loại nhà phát triển khác nhau, đồng thời trao tặng nhiều phần thưởng vật chất và tinh thần cho các dự án cộng đồng xuất sắc.

## 1.3 Lời cảm ơn

Chúng tôi vô cùng biết ơn các đồng tác giả đã đóng góp cho các phiên bản tiếng Trung và tiếng Anh của cuốn sách này, bao gồm nhưng không giới hạn ở việc thêm nội dung, sửa lỗi, cải thiện cấu trúc, và cung cấp phản hồi quý giá. Chúng tôi đặc biệt muốn cảm ơn từng nhà phát triển đã đóng góp cho dự án. Tên người dùng GitHub hoặc tên của các đồng tác giả này (không theo thứ tự cụ thể nào) là: LDOUBLEV, WenmuZhou, dyning, tink2123, MissPenguin, littletomatodonkey, Evezerest, andyjpaddle, D-DanielYang, Topdu, weisy11, BeyondYourself, JetHong, Intsigstephon, xmy0916, cuicheng01, bjjwwang, ZhangXinNan, hysunflower, d2623587501, Wei-JL, xxxpsyduck, Yipeng-Sun, TingquanGao, tangmq, MrCuiHao, authorfu, HexToString, GreatV, neonhuang, xiangyubo, Huntersdeng, iamyoyo, buptlihang, Lovely-Pig, OliverLPH, YukSing12, bingooo, fengxiaoshuai, lilinxiong, SibiAkkash, linkecoding, kjf4096, Sunny-wong, bupt906, XiaoguangHu01, Nikhil-Sawant-141, xxlyu-2046, znsoftm, xiaoyangyang2, sdcb, lyl120117, daassh, PeterH0323, before31, zhiqiu, zhangyingying520, DannyIsFunny, ufoym, ITerydh, fushall, baiyfbupt, OneYearIsEnough, tirkarthi, Zhouzd21, karl-horky, lgcy, raoyutian, ronny1996, light1003, JimEverest, Justus-Jonas, Jane-Ding, sushant1212, mengfu188, Channingss, edencfc, mymagicpower.

Ngoài ra, chúng tôi đặc biệt cảm ơn các nhà phát triển trong cộng đồng OCR: RangeKing, HustBestCat, v3fc, 1084667371, livingbody, haigang1975, fansong1983, Kongsea, fanruinet, thunderstudying, WZMIAOMIAO. Họ đã có những đóng góp xuất sắc cho các tài liệu tiếng Trung và tiếng Anh của cuốn sách điện tử.

Bên cạnh sách điện tử, đáng nhắc đến là 'Dive into OCR' cũng có một khóa học video tiếng Trung đi kèm, được các nhà phát triển OCR yêu thích sâu sắc. Khóa học đã thu hút hơn 8000 người đăng ký học. **Các khóa học tiếng Anh sẽ được ra mắt sau.**

---

*— Hết phần dịch 10 trang đầu —*
