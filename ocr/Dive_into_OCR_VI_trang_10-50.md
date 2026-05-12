# Dive into OCR — Bản dịch tiếng Việt (Trang 10–50)

*Tiếp nối từ file dịch trang 1–10.*

---

## (Trang 11) Cộng tác viên PaddleOCR

Hình ảnh: Bức tranh tổng hợp avatar của các nhà phát triển đã đóng góp cho cuốn sách (PaddleOCR Contributor).

---

# CHƯƠNG 2 — KIẾN THỨC TIÊN QUYẾT (COURSE PREREQUISITES)

Mô hình OCR được đề cập trong khóa học này dựa trên học sâu (deep learning). Vì vậy, phần này sẽ giới thiệu các kiến thức cơ bản liên quan, cấu hình môi trường, kỹ thuật dự án và các tài liệu liên quan. Người đọc mới làm quen với học sâu có thể tận dụng phần này.

## 2.1 Kiến thức nền tảng

Khái niệm "học" (learning) của học sâu được kế thừa từ các nội dung như nơ-ron, perceptron và mạng nơ-ron đa lớp trong học máy. Do đó, hiểu được các thuật toán học máy cơ bản sẽ giúp ích rất nhiều trong việc nắm bắt và ứng dụng học sâu. "Chiều sâu" của học sâu được thể hiện qua các phép toán toán học dựa trên vector như tích chập (convolution) và pooling, dùng để xử lý lượng lớn thông tin. Nếu bạn chưa quen với nền tảng lý thuyết của hai chủ đề này, bạn có thể học từ các khóa *Đại số tuyến tính (Linear Algebra)* và *Học máy (Machine Learning)* của thầy Lý Hồng Nghị (Li Hongyi).

Để hiểu chính bản chất của học sâu, bạn có thể tham khảo khóa học cơ bản của Bi Ran — một kiến trúc sư xuất sắc của Baidu: *Baidu Architect Guides You through Deep Learning Practice*, bao gồm lịch sử phát triển của học sâu và giới thiệu tất cả các thành phần của nó với một ví dụ kinh điển. Đây là một khóa học định hướng thực hành.

Để học phần thực hành của kiến thức lý thuyết, điều thiết yếu là tham gia khóa học *Kiến thức cơ bản về Python (Basic Knowledge of Python)*. Đồng thời, để nhanh chóng tái hiện mô hình học sâu, framework được sử dụng trong khóa học này là: **PaddlePaddle**. Nếu bạn đã từng dùng framework khác, bạn có thể nhanh chóng học cách sử dụng PaddlePaddle thông qua *Tài liệu Bắt đầu nhanh (Quick Start Document)*.

## 2.2 Chuẩn bị môi trường cơ bản

Nếu bạn muốn chạy mã của khóa học này trong môi trường cục bộ và chưa từng xây dựng môi trường Python trước đó, bạn có thể làm theo *Beginner's Guide to Prepare the Operational Environment*, cài đặt Anaconda hoặc môi trường docker theo hệ điều hành của mình.

Nếu bạn không có tài nguyên cục bộ, bạn có thể chạy mã trên nền tảng huấn luyện *AI Studio*. Mỗi mục trên nền tảng này được trình bày trong một notebook, thuận tiện cho việc học. Nếu bạn không biết cách dùng Notebook, hãy tham khảo *AI Studio Project Description*.

## 2.3 Lấy mã nguồn và chạy thử

Khóa học này dựa trên kho mã nguồn của PaddleOCR. Trước tiên, clone toàn bộ dự án PaddleOCR:

```bash
# [khuyến nghị]
git clone https://github.com/PaddlePaddle/PaddleOCR

# Nếu không thể pull do vấn đề mạng, có thể chọn lưu trữ trên Gitee:
git clone https://gitee.com/paddlepaddle/PaddleOCR
```

> Lưu ý: Dịch vụ lưu trữ mã Gitee có thể không đồng bộ cập nhật theo thời gian thực với dự án GitHub này, và thường có độ trễ 3–5 ngày. Vui lòng ưu tiên phương pháp được khuyến nghị.
>
> Nếu bạn không quen với các thao tác git, bạn có thể tải gói nén trong mục **Code** trên trang chủ PaddleOCR.

Sau đó cài đặt các thư viện bên thứ ba:

```bash
cd PaddleOCR
pip3 install -r requirements.txt
```

## 2.4 Truy cập thông tin

Tài liệu *PaddleOCR Usage Document* trình bày chi tiết cách sử dụng PaddleOCR để triển khai ứng dụng, huấn luyện và triển khai mô hình. Tài liệu rất giàu thông tin. Hầu hết các câu hỏi của người dùng đều được giải đáp trong tài liệu hoặc trong mục FAQ — đặc biệt là **FAQ**, nơi tổng hợp các vấn đề thường gặp theo quy trình ứng dụng học sâu. Khuyến nghị bạn đọc kỹ.

## 2.5 Hỏi đáp hỗ trợ

Nếu gặp lỗi, vấn đề về tính khả dụng hoặc tài liệu khi dùng PaddleOCR, bạn có thể liên hệ qua *Github issue*. Hãy theo template để cung cấp càng nhiều thông tin càng tốt, giúp đội ngũ chính thức nhanh chóng định vị vấn đề. Ngoài ra, nhóm WeChat là kênh trao đổi hàng ngày cho người dùng PaddleOCR, đặc biệt dùng để tư vấn. Bên cạnh đội PaddleOCR, còn có một số nhà phát triển nhiệt tình sẵn sàng trả lời câu hỏi của bạn.

---

# CHƯƠNG 3 — GIỚI THIỆU CÔNG NGHỆ OCR

*Hình ảnh minh họa: nhận dạng thẻ tín dụng qua điện thoại, biểu mẫu, đồng hồ nước, sổ tay, container PIL, bút quét từ điển, v.v. (nguồn từ Internet)*

## 3.1 Bối cảnh kỹ thuật của OCR

### 3.1.1 Các kịch bản ứng dụng

**OCR là gì?**

OCR (Optical Character Recognition — Nhận dạng ký tự quang học) là một lĩnh vực then chốt trong thị giác máy tính. OCR truyền thống thường được dùng để quét tài liệu. Ngày nay, nó thường ám chỉ *Nhận dạng văn bản trong cảnh thực (Scene Text Recognition — STR)*, chủ yếu cho các cảnh tự nhiên như biển hiệu trong hình bên dưới và các văn bản khác trong nhiều bối cảnh tự nhiên khác nhau.

*Hình 1: So sánh nhận dạng văn bản tài liệu (Document) vs. nhận dạng văn bản cảnh thực (Scene)*

**Các kịch bản ứng dụng của OCR là gì?**

Công nghệ OCR có nhiều kịch bản ứng dụng phong phú. Một kịch bản điển hình là nhận dạng văn bản có cấu trúc trong các lĩnh vực cụ thể, được sử dụng rộng rãi trong đời sống hàng ngày như nhận dạng biển số xe, thông tin thẻ ngân hàng, chứng minh thư, vé tàu, v.v. Đặc điểm chung của các lĩnh vực dọc (vertical) này là chúng có định dạng cố định. Rất phù hợp khi dùng OCR để tự động hóa, tiết kiệm nhân công và tăng hiệu suất.

Đây hiện là kịch bản được dùng rộng rãi nhất và tương đối hoàn thiện về công nghệ trong OCR.

*Hình 2: Các kịch bản ứng dụng của công nghệ OCR — cảnh chung, cảnh giao thông, thẻ căn cước, công nghiệp, hóa đơn, y tế, giáo dục, và các kịch bản khác*

Ngoài việc nhận dạng văn bản có cấu trúc trong các lĩnh vực cụ thể, công nghệ OCR phổ thông cũng có nhiều kịch bản ứng dụng đa dạng, thường được dùng để hoàn thành các tác vụ đa phương thức (multi-modal) cùng các công nghệ khác. Ví dụ, trong cảnh video, OCR thường được dùng cho dịch phụ đề tự động, giám sát an toàn nội dung, v.v., hoặc kết hợp với đặc trưng hình ảnh để hoàn thành các tác vụ như hiểu video (video understanding) và tìm kiếm video.

*Hình 3: OCR phổ thông trong cảnh đa phương thức (phụ đề video, truy xuất video, giám sát nội dung, dịch phụ đề, ...)*

### 3.1.2 Các thách thức kỹ thuật

Có hai loại thách thức kỹ thuật: thách thức về thuật toán và thách thức về ứng dụng.

**Thách thức về thuật toán**

OCR có nhiều kịch bản ứng dụng phong phú, dẫn đến nhiều khó khăn công nghệ. Có tám vấn đề phổ biến:

- Biến đổi phối cảnh (Perspective transformation)
- Thay đổi tỉ lệ lớn (Large scale change)
- Văn bản cong (Curve text)
- Nhiễu nền (Background noise)
- Phông chữ khác nhau (Different fonts)
- Đa ngôn ngữ (Multi-languages)
- Mờ (Blur)
- Ánh sáng (Illumination)

*Hình 4: Các thách thức kỹ thuật của thuật toán OCR*

Những vấn đề trên đặt ra thách thức rất lớn cho phát hiện và nhận dạng văn bản. Có thể thấy phần lớn thách thức xuất hiện trong cảnh tự nhiên. Hiện nay, hầu hết nghiên cứu học thuật tập trung vào cảnh tự nhiên, và các tập dữ liệu học thuật của OCR cũng vậy. Có nhiều nghiên cứu tập trung vào những vấn đề này. Tuy nhiên, **nhận dạng khó hơn phát hiện**.

**Thách thức về ứng dụng**

Trong ứng dụng, đặc biệt là các kịch bản phổ thông đa dạng, công nghệ OCR còn phải đối mặt với hai khó khăn lớn ngoài các vấn đề thuật toán đã nêu (biến đổi affine, vấn đề tỉ lệ, ánh sáng kém, ảnh mờ):

1. **Dữ liệu khổng lồ đòi hỏi OCR xử lý theo thời gian thực.** OCR thường được dùng cho dữ liệu lớn, do đó yêu cầu xử lý theo thời gian thực. Nhưng việc tăng tốc độ mô hình đạt chuẩn này khá thách thức.

2. **Ứng dụng trên thiết bị đầu cuối yêu cầu mô hình OCR đủ nhẹ và tốc độ nhận dạng đủ nhanh.** OCR thường được triển khai trên thiết bị di động hoặc phần cứng nhúng. Có hai chế độ: gửi lên server vs. nhận dạng trực tiếp trên thiết bị. Vì phương pháp đầu yêu cầu mạng cao, không tốt theo thời gian thực, server chịu tải lớn và có thể gặp rủi ro bảo mật khi truyền dữ liệu — nên chúng tôi hy vọng dùng phương pháp sau. Nhưng dung lượng lưu trữ và năng lực tính toán của thiết bị đầu cuối có hạn, nên yêu cầu cao về kích thước và tốc độ suy luận của mô hình OCR.

*Hình 5: Các thách thức kỹ thuật của ứng dụng OCR — cân bằng giữa Độ chính xác (Accuracy) với Kích thước mô hình (Model size) và Tốc độ suy luận (Inference speed)*

## 3.2 Các thuật toán OCR tiên tiến

Mặc dù OCR khá đặc thù, nó liên quan đến nhiều khía cạnh công nghệ: phát hiện văn bản, nhận dạng văn bản, nhận dạng văn bản đầu-cuối, phân tích tài liệu, v.v. Nghiên cứu học thuật về các công nghệ liên quan đang phát triển mạnh. Phần sau giới thiệu ngắn gọn các công nghệ then chốt trong tác vụ OCR.

### 3.2.1 Phát hiện văn bản (Text Detection)

Nhiệm vụ phát hiện văn bản là định vị vùng văn bản trong ảnh đầu vào. Trong những năm gần đây, có nhiều nghiên cứu học thuật về phát hiện văn bản. Một lớp phương pháp xem phát hiện văn bản là một kịch bản đặc biệt của phát hiện đối tượng (object detection), và sửa đổi các thuật toán phát hiện đối tượng phổ thông cho phù hợp với phát hiện văn bản. Ví dụ, **TextBoxes**[1] dựa trên detector một giai đoạn SSD, điều chỉnh khung mục tiêu cho phù hợp với các dòng văn bản có tỷ lệ khung hình cực đoan; còn **CTPN**[3] được phát triển từ thuật toán phát hiện hai giai đoạn Faster R-CNN[4]. Tuy nhiên, vẫn có những khác biệt giữa phát hiện văn bản và phát hiện đối tượng. Ví dụ, văn bản thường rất dài như "vạch sọc", khoảng cách giữa các dòng nhỏ, văn bản bị uốn cong, v.v. Do đó, nhiều thuật toán chuyên biệt cho phát hiện văn bản đã ra đời như **EAST**[5], **PSENet**[6], **DBNet**[7], v.v.

*Hình 6: Ví dụ tác vụ phát hiện văn bản*

Các thuật toán phát hiện văn bản phổ biến hiện nay có thể được phân thành hai loại:

- **Thuật toán dựa trên hồi quy (Regression-based Algorithms)**: bao gồm CTPN, SegLink, Textboxes/Textboxes++, EAST, LOMO, CRAFT, ... — Ưu điểm: thường tốt cho văn bản có hình dạng thông thường. Nhược điểm: không phát hiện chính xác văn bản hình dạng bất thường.
- **Thuật toán dựa trên phân đoạn (Segmentation-based Algorithms)**: Pixel embedding (Tian et al. 2019), SPCNet, PSENet, PAN, DB, ... — Ưu điểm: tốt cho văn bản đa dạng hình dạng. Nhược điểm: hậu xử lý phức tạp, tốn thời gian, kém hiệu quả với văn bản chồng nhau.

Có cả các thuật toán kết hợp hai cách tiếp cận. Các phương pháp dựa trên hồi quy mượn thuật toán phát hiện đối tượng tổng quát: hồi quy hộp phát hiện bằng cách thiết lập anchor hoặc trực tiếp thực hiện hồi quy pixel. Loại này tốt cho văn bản hình dạng thông thường, kém với văn bản hình dạng bất thường. Ví dụ, CTPN tốt cho văn bản ngang, nhưng kém với văn bản bị xoắn/cong. **SegLink**[8] phù hợp với văn bản dài, nhưng không tốt cho văn bản phân bố thưa. Thuật toán dựa trên phân đoạn (như **Mask-RCNN**[9]) có thể hoạt động tốt hơn trong nhiều cảnh và nhiều hình dạng văn bản, nhưng hậu xử lý phức tạp, có thể chậm và không thể phát hiện văn bản chồng lấp.

*Hình 7: Tổng quan các thuật toán phát hiện văn bản*
*Hình 8: (trái) Tối ưu hóa anchor của CTPN dựa trên hồi quy; (giữa) Tối ưu hóa hậu xử lý của DB dựa trên phân đoạn*

Các công nghệ liên quan đến phát hiện văn bản sẽ được giải thích và thực hành ở Chương 4.

### 3.2.2 Nhận dạng văn bản (Text Recognition)

Nhận dạng văn bản là nhận dạng nội dung văn bản trong ảnh. Đầu vào thường đến từ vùng văn bản đã được cắt ra bởi hộp phát hiện trong tác vụ phát hiện văn bản. Nhận dạng văn bản thường chia thành hai loại theo đường viền văn bản:

- **Nhận dạng văn bản thông thường (Regular Text Recognition)**: chủ yếu là phông in, văn bản quét — gần như nằm ngang.
- **Nhận dạng văn bản không thông thường (Irregular Text Recognition)**: thường không nằm ngang, thường bị cong, che khuất và mờ. Đây là hướng nghiên cứu chính trong nhận dạng văn bản.

*Hình 9: (Trái) Văn bản thông thường VS. (Phải) Văn bản không thông thường*

Các thuật toán nhận dạng văn bản thông thường có thể chia thành hai loại theo phương pháp giải mã: **dựa trên CTC** và **dựa trên Sequence2Sequence**. Chúng khác nhau ở cách chuyển đổi đặc trưng chuỗi do mạng học được thành kết quả nhận dạng cuối cùng. Một thuật toán đại diện dựa trên CTC là **CRNN**[11] kinh điển.

- *Dựa trên CTC*: CRNN, STAR-Net, Rosetta, ... — Ưu: hiệu suất cao, tốt cho văn bản thông thường và dài. Nhược: không dùng thông tin ngữ cảnh, kém với văn bản bất thường.
- *Dựa trên Attention*: R2AM, SAR, RARE, ... — Ưu: độ chính xác cao hơn. Nhược: kém với văn bản quá dài hoặc quá ngắn.

*Hình 10: Thuật toán dựa trên CTC VS. dựa trên Attention*

Thuật toán cho văn bản bất thường phong phú hơn. **STAR-Net**[12] hiệu chỉnh đường viền của văn bản bất thường thành hình chữ nhật chuẩn bằng cách thêm module hiệu chỉnh như TPS trước khi nhận dạng. Các phương pháp dựa trên attention như **RARE**[13] chú ý nhiều hơn đến mối tương quan giữa các bộ phận trong chuỗi. Các phương pháp dựa trên phân đoạn xem mỗi ký tự như một đơn vị riêng biệt, dễ nhận dạng ký tự đã phân đoạn hơn so với toàn bộ dòng văn bản sau khi hiệu chỉnh. Ngoài ra, với sự phát triển nhanh chóng của **Transformer**[14] và tính hiệu quả của nó được chứng minh trong nhiều tác vụ những năm gần đây, một số thuật toán nhận dạng văn bản dựa trên transformer đã ra đời. Các giải pháp này dùng cấu trúc transformer để giải quyết bài toán phụ thuộc dài hạn trong mô hình CNN và đạt kết quả tốt.

*Hình 11: Thuật toán nhận dạng dựa trên phân đoạn ký tự*

Các công nghệ liên quan đến nhận dạng văn bản sẽ được giải thích chi tiết ở Chương 5.

### 3.2.3 Nhận dạng cấu trúc tài liệu

Theo truyền thống, công nghệ OCR có thể đáp ứng nhu cầu phát hiện và nhận dạng văn bản. Tuy nhiên, trong các kịch bản thực tế, thứ chúng ta thường cần là **thông tin có cấu trúc**, như trích xuất từ thẻ căn cước và hóa đơn, nhận dạng có cấu trúc các bảng, v.v. Các kịch bản ứng dụng phần lớn là: trích xuất tài liệu chuyển phát nhanh, so sánh nội dung hợp đồng, so sánh thông tin tài liệu tài chính, nhận dạng tài liệu logistics. Lược đồ "kết quả OCR + hậu xử lý" được dùng phổ biến để cấu trúc hóa, nhưng nó phức tạp, hậu xử lý cần thiết kế cẩn thận và kém về khả năng tổng quát. Khi nhu cầu trích xuất thông tin có cấu trúc tăng, các công nghệ liên quan đến phân tích tài liệu thông minh — như **phân tích bố cục (layout analysis)**, **nhận dạng bảng (table recognition)** và **trích xuất thông tin then chốt (key information extraction)** — ngày càng được chú ý.

**Phân tích bố cục (Layout Analysis)**

Phân tích bố cục được thực hiện để phân loại nội dung ảnh tài liệu thành các loại: văn bản thuần, tiêu đề, bảng, hình ảnh, v.v. Các phương pháp hiện tại thường phát hiện hoặc phân đoạn chúng riêng biệt. Ví dụ, **Soto Carlos**[16] dùng thông tin ngữ cảnh và vị trí vốn có của nội dung tài liệu để cải thiện hiệu năng phát hiện vùng dựa trên thuật toán Faster R-CNN. **Sarkar Mausoom et al.**[17] đề xuất cơ chế phân đoạn dựa trên tiên nghiệm để huấn luyện mô hình phân đoạn tài liệu với ảnh độ phân giải cao, giải quyết vấn đề các cấu trúc khác nhau trong vùng dày đặc không thể phân biệt và bị gộp do giảm kích thước quá mức của ảnh gốc.

*Hình 12: Phân tích bố cục — phân loại vùng văn bản, hình, bảng, tiêu đề, v.v.*

**Nhận dạng bảng (Table Recognition)**

Nhận dạng bảng là nhận diện và chuyển đổi thông tin bảng trong tài liệu thành file excel. Có nhiều loại và phong cách bảng trong ảnh văn bản, như nhiều rowspan và colspan, các loại văn bản khác nhau. Ngoài ra, phong cách tài liệu và điều kiện ánh sáng khi chụp gây thách thức lớn cho nhận dạng bảng, khiến nhận dạng bảng trở thành một khó khăn nghiên cứu trong hiểu tài liệu.

*Hình 13: Bảng so sánh hiệu năng nhận dạng bảng (TextSnake, CSE, LOMO, ATRR, SegLink++, TextField, MSR, PSENet-1s, DB, CRAFT, TextDragon, PAN, ContourNet, DRRG, TextPerception, ...)*

Có nhiều phương pháp nhận dạng bảng. Thời kỳ đầu có các thuật toán truyền thống dựa trên quy tắc heuristic, như **T-Rect** của **Kieninger**[18] et al. — thường dùng quy tắc thủ công và phát hiện miền liên thông. Gần đây, khi học sâu phát triển, một số thuật toán nhận dạng cấu trúc bảng dựa trên CNN đã xuất hiện như **DeepTabStR** của **Siddiqui Shoaib Ahmed**[19] et al. và **TabStruct-Net** của **Raja Sachin**[20] et al. Ngoài ra, cùng với sự phát triển của *Graph Neural Network*, một số nhà nghiên cứu đã áp dụng GNN cho nhận dạng cấu trúc bảng và xem đó là bài toán tái dựng đồ thị — ví dụ **TGRNet** của **Xue Wenyuan**[21] et al. Hơn nữa, có các giải pháp đầu-cuối xuất cấu trúc bảng dưới dạng HTML. Hầu hết dùng Seq2Seq để dự đoán cấu trúc bảng, dựa trên attention hoặc transformer, bao gồm **TableMaster**[22].

*Hình 14: Các phương pháp nhận dạng bảng (Heuristic rules, CNN-based, GCN-based, End-to-end)*

**Trích xuất thông tin then chốt (Key Information Extraction — KIE)**

KIE là tác vụ quan trọng trong DocVQA. Nó đề cập đến việc trích xuất thông tin cần thiết từ ảnh — ví dụ tên và số căn cước từ thẻ căn cước. Thông tin được cố định trong một tác vụ, nhưng khác nhau giữa các tác vụ.

*Hình 15: Các tác vụ DocVQA — ví dụ Q&A về địa chỉ và diện tích nhà*

KIE thường được chia thành hai tác vụ con để nghiên cứu:

- **SER** (Semantic Entity Recognition — Nhận dạng thực thể ngữ nghĩa): phân loại từng văn bản đã phát hiện. Ví dụ chia văn bản thành "tên" và "số thẻ căn cước".
- **RE** (Relation Extraction — Trích xuất quan hệ): phân loại từng văn bản đã phát hiện. Ví dụ phân loại văn bản thành câu hỏi và câu trả lời, sau đó tìm câu trả lời tương ứng cho mỗi câu hỏi. Hộp đỏ và đen biểu diễn câu hỏi và trả lời, mũi tên vàng cho thấy mối tương ứng.

*Hình 16: Các tác vụ SER và RE*

Phương pháp KIE phổ thông được phát triển dựa trên Nhận dạng thực thể có tên (NER)[4], nhưng chỉ dùng thông tin văn bản trong ảnh mà không dùng thông tin hình ảnh và cấu trúc. Do đó không quá chính xác. Vì thế, gần đây nhiều giải pháp đã bắt đầu hợp nhất thông tin hình ảnh và cấu trúc với thông tin văn bản. Do nguyên lý hợp nhất thông tin đa phương thức khác nhau, các phương pháp này có thể chia thành bốn loại:

- Phương pháp dựa trên Grid
- Phương pháp dựa trên Token
- Phương pháp dựa trên GCN
- Phương pháp End-to-end

Công nghệ liên quan đến Phân tích tài liệu sẽ được trình bày và thực hành ở Chương 8.

### 3.2.4 Các công nghệ khác

Ba công nghệ then chốt của OCR đã được giới thiệu: phát hiện văn bản, nhận dạng văn bản, nhận dạng cấu trúc tài liệu. Các công nghệ tiên tiến khác liên quan đến OCR như nhận dạng văn bản đầu-cuối, công nghệ tiền xử lý ảnh, và tổng hợp dữ liệu OCR — chi tiết tham khảo Chương 9, 10 và 11.

## 3.3 Thực hành công nghiệp của công nghệ OCR

*Hình truyện minh họa: Sếp yêu cầu Wong phát triển ứng dụng nhận dạng hóa đơn trong một tuần; nếu không xong sẽ bị trừ thưởng.*

Nếu bạn là Wong, bạn sẽ làm gì?
1. Tôi không biết gì về việc này. Tôi bỏ.
2. Khuyên sếp thuê công ty bên ngoài hoặc đề xuất dự án thương mại. Đằng nào cũng là tiền của sếp.
3. Tìm dự án tương tự trên mạng và lập trình theo hướng Github.

Công nghệ OCR hướng đến việc được áp dụng trong thực tế công nghiệp. Mặc dù có nhiều nghiên cứu học thuật về OCR và ứng dụng thương mại đã trưởng thành hơn các công nghệ AI khác, vẫn có một số khó khăn trong ứng dụng công nghiệp. Phần tiếp theo sẽ phân tích những khó khăn về công nghệ và thực tiễn công nghiệp.

### 3.3.1 Những khó khăn trong thực tiễn công nghiệp

Trong thực tiễn công nghiệp, các nhà phát triển thường cần dựa vào tài nguyên cộng đồng mã nguồn mở để khởi động hoặc thúc đẩy dự án. Nhưng họ thường gặp ba vấn đề khi sử dụng mô hình mã nguồn mở:

*Hình 17: Ba vấn đề chính trong thực tiễn công nghiệp của công nghệ OCR — Khó tìm/khó chọn, Không phù hợp với kịch bản công nghiệp, Khó tối ưu hóa*

**1. Khó tìm & khó chọn**

Cộng đồng mã nguồn mở có nguồn tài nguyên phong phú, nhưng sự bất đối xứng thông tin sẽ ngăn cản các nhà phát triển giải quyết vấn đề hiệu quả. Một mặt, tài nguyên mã nguồn mở quá phong phú đến mức các nhà phát triển khó nhanh chóng tìm dự án phù hợp với yêu cầu kinh doanh trong kho mã khổng lồ — đó là vấn đề "khó tìm". Mặt khác, trong việc chọn thuật toán, các nhà phát triển phải xác minh từng cái một — và các chỉ số trên tập dữ liệu tiếng Anh công khai không thể cung cấp tham chiếu trực tiếp cho kịch bản tiếng Trung mà họ gặp phải. Việc này tốn thời gian và công sức, thậm chí không đảm bảo lựa chọn phù hợp nhất — đó là vấn đề "khó chọn".

**2. Không phù hợp với kịch bản công nghiệp**

Công việc cộng đồng mã nguồn mở tập trung nhiều vào tối ưu hóa hiệu quả — như mã nguồn mở hoặc tái hiện mã trong bài báo học thuật — và hiệu ứng thuật toán, thay vì kích thước và tốc độ mô hình. Nhưng hai chỉ số này quan trọng không kém hiệu ứng mô hình và không thể bỏ qua trong thực tiễn công nghiệp. Dù trên thiết bị di động hay server, số lượng ảnh cần nhận dạng rất lớn nên mô hình cần nhỏ hơn, chính xác hơn và nhanh hơn trong suy luận. Nhưng GPU quá đắt nên kinh tế hơn khi dùng CPU. Với điều kiện đáp ứng nhu cầu kinh doanh, mô hình càng nhẹ, càng tốn ít tài nguyên.

**3. Khó tối ưu hóa & khó huấn luyện và triển khai**

Chỉ dùng thuật toán hoặc mô hình mã nguồn mở thuần túy không đáp ứng trực tiếp nhu cầu kinh doanh. Trong các kịch bản kinh doanh thực tế, OCR cần được dùng để xử lý nhiều vấn đề. Cá nhân hóa kịch bản kinh doanh thường đòi hỏi huấn luyện lại trên tập dữ liệu tùy chỉnh. Việc thử nghiệm các giải pháp tối ưu hóa trong dự án mã nguồn mở hiện tại tốn kém. Ngoài ra, OCR đã được áp dụng cho rất nhiều kịch bản với nhiều nhu cầu khác nhau trên server và thiết bị di động. Do đó, môi trường phần cứng đa dạng nên hỗ trợ nhiều phương pháp triển khai. Nhưng dự án cộng đồng mã nguồn mở tập trung vào thuật toán và mô hình, thiếu hỗ trợ suy luận và triển khai. Để áp dụng công nghệ OCR từ các thuật toán trong bài báo, yêu cầu cao về khả năng thuật toán và kỹ thuật của nhà phát triển.

### 3.3.2 Bộ phát triển OCR cấp công nghiệp — PaddleOCR

Thực tiễn công nghiệp OCR đòi hỏi một tập giải pháp toàn diện để tăng tốc quá trình nghiên cứu và phát triển và tiết kiệm thời gian. Nói cách khác, mô hình siêu nhẹ và giải pháp toàn diện là yêu cầu cấp thiết, đặc biệt đối với thiết bị di động và nhúng có khả năng tính toán và lưu trữ hạn chế.

Vì vậy, bộ phát triển OCR cấp công nghiệp **PaddleOCR** đã ra đời.

PaddleOCR được xây dựng từ chân dung và nhu cầu người dùng, chọn lọc và tái hiện các thuật toán tiên tiến đa dạng với framework lõi PaddlePaddle. Phát triển các mô hình PP phù hợp hơn cho công nghiệp hóa dựa trên các thuật toán đã tái hiện, và tích hợp huấn luyện và suy luận để cung cấp nhiều phương pháp suy luận và triển khai, đáp ứng các kịch bản nhu cầu khác nhau trong ứng dụng.

*Hình 18: Toàn cảnh bộ phát triển PaddleOCR — gồm các tầng: kịch bản ứng dụng (thẻ, hóa đơn tài chính, biển số, tài liệu văn phòng, hóa đơn y tế, cảnh giáo dục), triển khai (Paddle Inference, Paddle Serving, Paddle Lite, công cụ dữ liệu), mô hình tiền huấn luyện (General/Ultra-lightweight/Multilingual/Document analysis), thuật toán (PP-OCR, PP-Structure: Detection EAST/DB/SAST/PSENet; Recognition CRNN/Rosetta/RARE/STAR-Net/SAR/SRN/NRTR/SEED; End-to-End PGNet/ABCNet; Layout analysis; Table recognition; Key info extraction; Semantic entity recognition), và Core platform PaddlePaddle*

Có thể thấy PaddleOCR cung cấp giải pháp phong phú về thuật toán mô hình, thư viện mô hình tiền huấn luyện và triển khai cấp công nghiệp với sự hỗ trợ của framework lõi PaddlePaddle, đồng thời cung cấp công cụ tổng hợp dữ liệu và gán nhãn dữ liệu bán tự động để thúc đẩy sản xuất dữ liệu của nhà phát triển.

**Về thuật toán mô hình**, PaddleOCR cung cấp giải pháp cho phát hiện và nhận dạng văn bản và phân tích cấu trúc tài liệu. PaddleOCR đã tái hiện hoặc mã nguồn mở 4 thuật toán phát hiện văn bản, 8 thuật toán nhận dạng văn bản, và 1 thuật toán nhận dạng văn bản đầu-cuối. Dựa trên đó, một giải pháp phát hiện và nhận dạng phổ thông cho loạt PP-OCR đã được phát triển. Về phân tích cấu trúc tài liệu, PaddleOCR cung cấp các thuật toán như phân tích bố cục, nhận dạng bảng, trích xuất thông tin then chốt và nhận dạng thực thể có tên — và đề xuất tài liệu PP-Structure. Việc thống nhất framework mã cũng tạo điều kiện so sánh hiệu năng và tối ưu hóa giữa các thuật toán.

**Về thư viện mô hình tiền huấn luyện**, với giải pháp PP-OCR và PP-Structure, PaddleOCR đã phát triển và mã nguồn mở các mô hình loạt PP phù hợp với thực tiễn công nghiệp: bao gồm các mô hình phát hiện và nhận dạng văn bản phổ thông/siêu nhẹ/đa ngôn ngữ, và mô hình phân tích tài liệu phức tạp. Các mô hình loạt PP được tối ưu hóa kỹ lưỡng dựa trên thuật toán gốc để hiệu ứng và hiệu năng đạt chuẩn công nghiệp. Nhà phát triển có thể dễ dàng phát triển "mô hình thực tiễn" cho nhu cầu kinh doanh của mình bằng cách áp dụng trực tiếp hoặc fine-tuning bằng dữ liệu doanh nghiệp.

**Về triển khai cấp công nghiệp**, PaddleOCR cung cấp giải pháp suy luận phía server dựa trên Paddle Inference, giải pháp triển khai dịch vụ dựa trên Paddle Serving, và giải pháp triển khai phía đầu cuối dựa trên Paddle Lite — đáp ứng nhu cầu triển khai trên nhiều môi trường phần cứng. Cũng cung cấp lược đồ nén mô hình dựa trên PaddleSlim. Các phương pháp triển khai này đã chạy thông toàn bộ quy trình huấn luyện và suy luận, đảm bảo nhà phát triển có thể triển khai hiệu quả, ổn định và tin cậy.

**Về công cụ dữ liệu**, PaddleOCR cung cấp công cụ gán nhãn dữ liệu bán tự động — **PPOCRLabel** — và công cụ tổng hợp dữ liệu **Style-Text** giúp nhà phát triển sản xuất tập dữ liệu và thông tin nhãn cần thiết để huấn luyện mô hình thuận tiện hơn. PPOCRLabel là công cụ gán nhãn dữ liệu OCR bán tự động mã nguồn mở đầu tiên trong ngành, nhằm giải quyết vấn đề quy trình gán nhãn mệt mỏi và máy móc, nhu cầu lớn về gán nhãn thủ công, và chi phí cao về thời gian và tiền bạc. Nó giới thiệu chế độ "tiền gán nhãn + xác minh thủ công" tích hợp trong mô hình PP-OCR, giúp tăng hiệu suất và tiết kiệm chi phí. Công cụ tổng hợp dữ liệu Style-Text tập trung vào giải pháp cho tình trạng thiếu dữ liệu thật trong cảnh thực và sự thất bại của các thuật toán tổng hợp truyền thống trong tổng hợp phong cách văn bản (font, màu, khoảng cách, nền). Chỉ với một vài ảnh cảnh mục tiêu, có thể tổng hợp một lượng lớn ảnh văn bản tương tự về phong cách với cảnh mục tiêu.

*Hình 19: Sơ đồ sử dụng PPOCRLabel*
*Hình 20: Ví dụ kết quả tổng hợp Style-Text*

**PP-OCR và PP-Structure**

Các mô hình loạt PP được tối ưu hóa kỹ lưỡng để đáp ứng nhu cầu thực tiễn công nghiệp thông qua bộ công cụ phát triển trực quan của PaddlePaddle, nhằm cân bằng giữa tốc độ và độ chính xác. Mô hình loạt PP trong PaddleOCR bao gồm mô hình loạt PP-OCR cho phát hiện và nhận dạng văn bản và mô hình loạt PP-Structure cho phân tích tài liệu.

**(1) Mô hình Chinese and English của PP-OCR**

*Hình 21: Ví dụ kết quả nhận dạng của mô hình tiếng Trung và tiếng Anh của PP-OCR*

Thuật toán OCR hai giai đoạn điển hình được mô hình Chinese and English của PP-OCR áp dụng theo mô hình: mô hình phát hiện + mô hình nhận dạng. Framework cụ thể như sau:

*Hình 22: Sơ đồ pipeline hệ thống PP-OCR — Image → Text Detection (DB) → Detection Boxes Rectify → Text Recognition (CRNN) → Output*

Có thể thấy ngoài đầu vào và đầu ra, framework lõi PP-OCR gồm ba module: phát hiện văn bản, hiệu chỉnh khung phát hiện, và nhận dạng văn bản.

- **Module phát hiện văn bản**: lõi là mô hình phát hiện văn bản được huấn luyện theo thuật toán phát hiện **DB**, dùng để phát hiện vùng văn bản trong ảnh.
- **Module hiệu chỉnh khung phát hiện**: đưa hộp văn bản phát hiện được vào module này. Ở giai đoạn này, hộp văn bản bất thường được hiệu chỉnh thành khung chữ nhật, chuẩn bị cho nhận dạng. Hướng văn bản cũng được đánh giá và hiệu chỉnh — ví dụ nếu dòng văn bản bị lộn ngược, nó sẽ được sửa. Chức năng này dựa trên huấn luyện bộ phân loại hướng văn bản.
- **Module nhận dạng văn bản**: cuối cùng, module thực hiện nhận dạng văn bản trên hộp đã hiệu chỉnh để biết nội dung. Thuật toán nhận dạng văn bản kinh điển dùng trong PP-OCR là **CRNN**.

PaddleOCR đã giới thiệu các mô hình **PP-OCR**[23] và **PP-OCRv2**[24].

Mô hình PP-OCR có phiên bản mobile (lightweight) và server (universal). Phiên bản mobile chủ yếu tối ưu dựa trên backbone nhẹ MobileNetV3. Mô hình đã tối ưu (detection + text direction classification + recognition) chỉ 8.1M, mất 350ms để dự đoán một ảnh trên CPU và khoảng 110ms trên T4 GPU. Sau khi cắt tỉa và lượng tử hóa, kích thước có thể giảm xuống còn 3.5M với cùng độ chính xác, thuận tiện triển khai phía đầu cuối. Kiểm thử suy luận mô hình trước đó chỉ mất 260ms trên bộ vi xử lý Snapdragon 855. Để xem thêm dữ liệu đánh giá PP-OCR, vui lòng tham khảo **benchmark**.

PP-OCRv2 giữ framework chung của PP-OCR và thực hiện tối ưu hóa chính sách, chủ yếu ở 3 khía cạnh:
- Hiệu ứng mô hình tăng hơn 7% so với phiên bản PP-OCR mobile;
- Tốc độ tăng 220% so với phiên bản PP-OCR server;
- Kích thước mô hình 11.6M giúp dễ triển khai trên cả server và thiết bị di động.

Các chính sách tối ưu của PP-OCR và PP-OCRv2 sẽ được trình bày chi tiết ở Chương 6.

Ngoài các mô hình tiếng Trung và tiếng Anh, PaddleOCR cũng đã huấn luyện và mã nguồn mở **mô hình tiếng Anh số** và **mô hình nhận dạng đa ngôn ngữ** với các tập dữ liệu khác nhau. Tất cả đều siêu nhẹ và phù hợp với các kịch bản ngôn ngữ khác nhau.

*Hình 23: Sơ đồ kết quả nhận dạng của mô hình tiếng Anh số và mô hình đa ngôn ngữ của PP-OCR*

**(2) Mô hình phân tích tài liệu PP-Structure**

PP-Structure hỗ trợ ba tác vụ con: phân tích bố cục, nhận dạng bảng, và DocVQA.

Có sáu chức năng cốt lõi của PP-Structure:
- Thực hiện phân tích bố cục của tài liệu dạng ảnh, có thể chia thành 5 loại vùng: văn bản, tiêu đề, bảng, hình và danh sách (dùng cùng Layout-Parser)
- Trích xuất văn bản, tiêu đề, hình và danh sách dưới dạng trường văn bản (dùng cùng PP-OCR)
- Phân tích có cấu trúc cho bảng, kết quả cuối được xuất ra file Excel
- Hỗ trợ gói Python whl và command line, đơn giản và dễ dùng
- Hỗ trợ huấn luyện tùy chỉnh cho hai loại tác vụ: phân tích bố cục và cấu trúc bảng
- Hỗ trợ tác vụ VQA — SER và RE

*Hình 24: Sơ đồ hệ thống PP-Structure (chỉ chứa phân tích bố cục + nhận dạng bảng)*

Kế hoạch cụ thể của PP-Structure sẽ được giải thích chi tiết ở Chương 8.

**Kế hoạch triển khai cấp công nghiệp**

Có thể tiến hành suy luận toàn quy trình và toàn cảnh trên PaddlePaddle với ba nguồn mô hình chính. Đầu tiên là huấn luyện bằng cấu trúc mạng được xây dựng với API PaddlePaddle. Thứ hai là loạt bộ công cụ PaddlePaddle — cung cấp nhiều thư viện mô hình và API ngắn gọn, dễ dùng, có thể dùng ngay (out-of-the-box) — gồm thư viện mô hình thị giác PaddleCV, thư viện giọng nói thông minh PaddleSpeech và thư viện xử lý ngôn ngữ tự nhiên PaddleNLP, v.v. Loại thứ ba là mô hình được sinh từ các framework bên thứ ba (PyTorch, ONNX, TensorFlow, ...) bằng công cụ X2Paddle.

Mô hình PaddlePaddle có thể được nén, lượng tử hóa và chưng cất bằng PaddleSlim. Hỗ trợ năm lược đồ triển khai: Paddle Serving (service-based), Paddle Inference (server-side/cloud-side), Paddle Lite (mobile/edge), Paddle.js (front-end of web). Một số phần cứng không khả dụng như MCU, Horizon, Kunyun và các chip nội địa khác có thể chuyển sang framework bên thứ ba hỗ trợ ONNX với sự giúp đỡ của Paddle2ONNX.

*Hình 25: Các phương pháp triển khai có sẵn trên PaddlePaddle*

- **Paddle Inference** hỗ trợ triển khai server-side và cloud, hiệu năng cao và đa năng. Đã được điều chỉnh và tối ưu hóa kỹ lưỡng cho các nền tảng và kịch bản ứng dụng khác nhau. Paddle Inference là thư viện suy luận gốc của PaddlePaddle để đảm bảo mô hình có thể được dùng ngay khi huấn luyện xong phía server và triển khai nhanh. Phù hợp với phần cứng hiệu năng cao dùng môi trường đa ngôn ngữ với các thuật toán phức tạp. Phần cứng gồm CPU x86, GPU Nvidia, và bộ tăng tốc AI như Baidu Kunlun XPU và Huawei Shengteng.

- **Paddle Lite** là engine suy luận phía đầu cuối, nhẹ và hiệu năng cao. Đã được cấu hình và tối ưu sâu cho thiết bị đầu cuối và các kịch bản ứng dụng. Hiện hỗ trợ nhiều nền tảng như Android, iOS, thiết bị Linux nhúng, macOS, v.v. Phần cứng bao gồm CPU ARM và GPU, CPU x86 và phần cứng mới như Baidu Kunlun, Huawei Ascend và Kirin, Rockchip, v.v.

- **Paddle Serving** là framework dịch vụ hiệu năng cao thiết kế để giúp người dùng nhanh chóng triển khai mô hình trong dịch vụ đám mây với vài bước. Hiện hỗ trợ tiền xử lý tùy chỉnh, kết hợp mô hình, cập nhật mô hình hot reload, đa máy đa thẻ đa mô hình, suy luận phân tán, triển khai K8S, gateway bảo mật và triển khai mã hóa mô hình, và truy cập đa ngôn ngữ đa client. Trang chính thức cũng cung cấp ví dụ triển khai hơn 40 mô hình bao gồm PaddleOCR.

*Hình 26: Chế độ triển khai được hỗ trợ của PaddlePaddle*

| Triển khai | Đặc trưng | Cảnh | Phần cứng |
|---|---|---|---|
| Paddle Inference | Hiệu năng cao | Thuật toán phức tạp, phần cứng cao | x86 CPU, NVIDIA GPU, Loongson/Feitong, Kunlun/Ascend/Haiguang DCU |
| Paddle Lite | Nhẹ | Mô hình nhẹ, phần cứng hạn chế, công suất thấp | ARM CPU, ARM/Qualcomm/Apple GPU, Kunlun/Ascend/Kirin/Rockchip... |
| Paddle Serving | Đồng thời cao | Lưu lượng lớn, độ trễ thấp, throughput lớn | x86/ARM CPU, NVIDIA GPU, Kunlun/Shengteng |
| Paddle.js | Suy luận trên trình duyệt | Chrome, Safari, Firefox, ... | — |
| Paddle2ONNX | Mở và tương thích | Triển khai trên nhiều chip AI hơn | Horizon X3, Corerain X3, Allwinner R329, các chip AI khác |

Các kế hoạch triển khai trên sẽ được trình bày và thực hành chi tiết dựa trên mô hình PP-OCRv2 ở Chương 7.

## 3.4 Tổng kết

Phần này trước hết giới thiệu các kịch bản ứng dụng và thuật toán tiên tiến của công nghệ OCR, sau đó phân tích các khó khăn và ba thách thức lớn của OCR trong thực tiễn công nghiệp.

Nội dung các chương tiếp theo:
- **Chương 4 và 5**: phát hiện và nhận dạng văn bản và thực hành
- **Chương 6**: chính sách tối ưu hóa PP-OCR
- **Chương 7**: thực hành suy luận và triển khai
- **Chương 8**: cấu trúc tài liệu
- **Chương 9–11**: các thuật toán liên quan OCR khác (đầu-cuối, tiền xử lý, tổng hợp dữ liệu)

## 3.5 Tài liệu tham khảo

[1] Liao, Minghui, et al. "Textboxes: A fast text detector with a single deep neural network." Thirty-first AAAI conference on artificial intelligence. 2017.

[2] Liu W, Anguelov D, Erhan D, et al. SSD: Single shot multibox detector. ECCV, Springer, Cham, 2016: 21-37.

[3] Tian, Zhi, et al. "Detecting text in natural image with connectionist text proposal network." ECCV. Springer, Cham, 2016.

[4] Ren S, He K, Girshick R, et al. Faster R-CNN: Towards real-time object detection with region proposal networks. NeurIPS, 2015, 28: 91-99.

[5] Zhou, Xinyu, et al. "EAST: an efficient and accurate scene text detector." CVPR, 2017.

[6] Wang, Wenhai, et al. "Shape robust text detection with progressive scale expansion network." CVPR, 2019.

[7] Liao, Minghui, et al. "Real-time scene text detection with differentiable binarization." AAAI, Vol. 34. No. 07. 2020.

[8] Deng, Dan, et al. "Pixellink: Detecting scene text via instance segmentation." AAAI, Vol. 32. No. 1. 2018.

[9] He K, Gkioxari G, Dollár P, et al. Mask R-CNN. ICCV, 2017: 2961-2969.

[10] Wang P, Zhang C, Qi F, et al. A single-shot arbitrarily-shaped text detector based on context attended multi-task learning. ACM Multimedia, 2019: 1277-1285.

[11] Shi, B., Bai, X., & Yao, C. (2016). An end-to-end trainable neural network for image-based sequence recognition and its application to scene text recognition. IEEE TPAMI, 39(11), 2298-2304.

[12] STAR-Net Max Jaderberg, Karen Simonyan, Andrew Zisserman, et al. Spatial transformer networks. NeurIPS, pp. 2017–2025, 2015.

[13] Shi, B., Wang, X., Lyu, P., Yao, C., & Bai, X. (2016). Robust scene text recognition with automatic rectification. CVPR, pp. 4168-4176.

[14] Sheng, F., Chen, Z., & Xu, B. (2019, September). NRTR: A no-recurrence sequence-to-sequence model for scene text recognition. ICDAR (pp. 781-786). IEEE.

[15] Lyu P, Liao M, Yao C, et al. Mask textspotter: An end-to-end trainable neural network for spotting text with arbitrary shapes. ECCV, 2018: 67-83.

[16] Soto C, Yoo S. Visual detection with context for document layout analysis. EMNLP-IJCNLP, 2019: 3464-3470.

[17] Sarkar M, Aggarwal M, Jain A, et al. Document Structure Extraction using Prior based High Resolution Hierarchical Semantic Segmentation. ECCV, Springer, Cham, 2020: 649-666.

[18] Kieninger T, Dengel A. A paper-to-HTML table converting system. DAS, 1998, 98: 356-365.

[19] Siddiqui S A, Fateh I A, Rizvi S T R, et al. DeepTabStR: Deep learning based table structure recognition. ICDAR. IEEE, 2019: 1403-1409.

[20] Raja S, Mondal A, Jawahar C V. Table structure recognition using top-down and bottom-up cues. ECCV, Springer, Cham, 2020: 70-86.

[21] Xue W, Yu B, Wang W, et al. TGRNet: A Table Graph Reconstruction Network for Table Structure Recognition. arXiv:2106.10598, 2021.

[22] Ye J, Qi X, He Y, et al. PingAn-VCGroup's Solution for ICDAR 2021 Competition on Scientific Literature Parsing Task B: Table Recognition to HTML. arXiv:2105.01848, 2021.

[23] Du Y, Li C, Guo R, et al. PP-OCR: A practical ultra lightweight OCR system. arXiv:2009.09941, 2020.

[24] Du Y, Li C, Guo R, et al. PP-OCRv2: Bag of Tricks for Ultra Lightweight OCR System. arXiv:2109.03144, 2021.

---

# CHƯƠNG 4 — PHÁT HIỆN VĂN BẢN (TEXT DETECTION)

Phát hiện văn bản là tìm ra vị trí của văn bản trong ảnh hoặc video. Khác với *phát hiện đối tượng (object detection)* — chuyên giải quyết cả bài toán định vị và phân loại — phát hiện văn bản chỉ cần định vị.

Biểu diễn văn bản trong ảnh có thể được coi như một loại "đối tượng", nên các phương pháp phát hiện đối tượng cũng phù hợp với phát hiện văn bản. So sánh điểm giống và khác về nhiệm vụ:

- **Phát hiện đối tượng**: tìm hộp của đối tượng trong ảnh/video, và phân loại.
- **Phát hiện văn bản**: tìm vùng văn bản trong ảnh/video — có thể là một ký tự đơn hoặc cả dòng văn bản.

*Hình 1: Sơ đồ phát hiện đối tượng — person, horse, dog với bounding box*
*Hình 2: Sơ đồ phát hiện văn bản — bảng kiểm số liệu, biển hiệu, biển hiệu cong*

Phát hiện đối tượng và phát hiện văn bản đều liên quan đến "vị trí". Nhưng loại sau không cần phân loại đối tượng, và hình dạng văn bản phức tạp đa dạng.

Hiện tại, phát hiện văn bản thường ám chỉ phát hiện văn bản cảnh thực, gặp các khó khăn:

1. **Đa dạng văn bản trong cảnh tự nhiên**: phát hiện văn bản có thể bị ảnh hưởng bởi màu sắc, kích thước, font, hình dạng, hướng, ngôn ngữ và độ dài.
2. **Phức tạp về nền và nhiễu**: có thể bị ảnh hưởng bởi biến dạng ảnh, mờ, độ phân giải thấp, bóng, độ sáng, v.v.
3. **Văn bản dày đặc hoặc chồng lấp.**
4. **Tính đồng nhất một phần của văn bản**: một phần nhỏ của dòng văn bản cũng có thể được coi là một văn bản riêng.

*Hình 3: Các cảnh phát hiện văn bản*

Nhiều thuật toán phát hiện văn bản dựa trên học sâu đã ra đời để giải quyết các vấn đề này. Các phương pháp có thể chia thành phát hiện dựa trên hồi quy và dựa trên phân đoạn.

Phần tiếp theo giới thiệu ngắn gọn các thuật toán phát hiện văn bản kinh điển dựa trên học sâu.

## 4.1 Giới thiệu các phương pháp phát hiện văn bản

Trong những năm gần đây, các thuật toán phát hiện văn bản dựa trên học sâu đang tăng nhanh. Có thể chia thành hai loại:

1. Phương pháp dựa trên hồi quy
2. Phương pháp dựa trên phân đoạn

Các phương pháp thường dùng từ 2017–2021 được phân loại như sau:

| Loại | Văn bản ngang | Văn bản ở bất kỳ góc độ | Văn bản cảnh hình dạng tùy ý |
|---|---|---|---|
| **Dựa trên hồi quy** | Textbox, CTPN, ... | Textbox++, EAST, MOST, ... | CTD, ContourNet, LOMO, PCR, ... |
| **Dựa trên phân đoạn** | — | Pixellink, PAN, PSENet, Seglink++, ... | MSR, DB |

*Hình 4: Các thuật toán phát hiện văn bản*

### 4.1.1 Phát hiện văn bản dựa trên hồi quy

Thuật toán dựa trên hồi quy tương tự thuật toán phát hiện đối tượng. Có chỉ hai phần trong phương pháp phát hiện văn bản: văn bản của ảnh là mục tiêu cần phát hiện, phần còn lại là nền.

**Thuật toán phát hiện văn bản ngang**

Thời kỳ đầu, các phương pháp dựa trên học sâu là các thuật toán phát hiện đối tượng được sửa đổi, hỗ trợ phát hiện văn bản ngang. Ví dụ, thuật toán *TextBoxes* được cải tiến từ thuật toán SSD, và CTPN từ thuật toán phát hiện đối tượng hai giai đoạn Fast-RCNN.

Thuật toán **TextBoxes**[1] được điều chỉnh từ detector mục tiêu một giai đoạn SSD. Hộp văn bản mặc định được đổi thành tứ giác phù hợp với hướng và tỷ lệ khung hình của văn bản. Thuật toán cũng cung cấp phương pháp huấn luyện end-to-end mà không cần hậu xử lý phức tạp:
- Hộp tiền chọn lớn hơn theo tỷ lệ khung hình.
- Kernel tích chập đổi từ 3×3 sang 1×51, phù hợp hơn cho văn bản dài.
- Áp dụng đầu vào đa tỉ lệ.

Dựa trên thuật toán Fast-RCNN, **CTPN**[3] mở rộng module RPN và thiết kế module dựa trên CRNN để mạng có thể phát hiện chuỗi văn bản từ đặc trưng tích chập. Phương pháp hai giai đoạn có thể định vị đặc trưng chính xác hơn qua ROI Pooling. Nhưng TextBoxes và CTPN chỉ phát hiện được văn bản ngang.

*Hình 6: Sơ đồ frame của CTPN*

**Phát hiện văn bản ở góc bất kỳ**

**TextBoxes++**[2] được sửa từ TextBoxes, có thể phát hiện văn bản ở góc bất kỳ. Về cấu trúc, khác với TextBoxes, TextBoxes++ thiết kế để phát hiện văn bản đa góc. Đầu tiên, sửa tỷ lệ khung hình của hộp tiền chọn và điều chỉnh thành 1, 2, 3, 5, 1/2, 1/3, 1/5. Thứ hai, đổi kernel tích chập 1×5 thành 3×5 để học tốt hơn đặc trưng của văn bản nghiêng. Cuối cùng, xuất thông tin biểu diễn hộp xoay.

*Hình 7: Sơ đồ frame của TextBoxes++*

**EAST**[4] áp dụng phương pháp phát hiện văn bản hai giai đoạn cho vị trí của văn bản nghiêng — gồm trích xuất đặc trưng FCN và NMS. EAST đề xuất cấu trúc pipeline phát hiện văn bản mới, có thể huấn luyện end-to-end và phát hiện văn bản ở bất kỳ hướng nào. Cũng đơn giản về cấu trúc và xuất sắc về hiệu năng. FCN hỗ trợ xuất hình chữ nhật ngang hoặc nghiêng có định dạng do người dùng quyết định:
- Nếu hình dạng xuất là RBox, xuất góc xoay của hộp và hình dạng văn bản AABB (dịch chuyển trên/dưới/trái/phải). RBox có thể xoay văn bản hình chữ nhật.
- Nếu hộp xuất là four-point, kích thước cuối cùng có 8 số (dịch chuyển từ 4 đỉnh tứ giác). Phương pháp này có thể dự đoán văn bản dạng tứ giác bất thường.

Hộp văn bản xuất bởi FCN là dư thừa. Ví dụ, hộp sinh bởi pixel kề của vùng văn bản chồng lấp cao. Nhưng những hộp từ cùng một văn bản thì không vậy. Do đó, EAST đề xuất hợp các hộp dự đoán theo hàng, rồi lọc các tứ giác còn lại bằng NMS gốc.

*Hình 8: Sơ đồ frame của EAST*

**MOST**[15] đề xuất module TFAM để điều chỉnh động trường thụ cảm theo kết quả phát hiện thô, đồng thời đề xuất PA-NMS để kết hợp phát hiện đáng tin cậy và kết quả dự đoán dựa trên vị trí. Hơn nữa, hàm mất mát Instance-wise IoU được đưa ra khi huấn luyện, dùng để cân bằng huấn luyện và xử lý văn bản tỉ lệ khác nhau. Phương pháp này có thể kết hợp với EAST để có hiệu ứng và hiệu năng tốt trong phát hiện văn bản tỷ lệ và tỷ lệ khung hình cực đoan.

*Hình 9: Sơ đồ frame MOST*

**Phát hiện văn bản hình dạng tùy ý**

Trong các ý tưởng dùng hồi quy để phát hiện văn bản cong, một cách đơn giản là mô tả đa giác có biên là văn bản cong với tọa độ nhiều điểm, rồi dự đoán tọa độ đỉnh của đa giác.

**CTD**[6] đề xuất dự đoán đa giác văn bản cong với 14 đỉnh. Mạng dùng tầng Bi-LSTM[13] để tinh chỉnh tọa độ đỉnh đã dự đoán và phát hiện văn bản cong dựa trên hồi quy.

*Hình 10: Sơ đồ frame của CTD*

Đối với phát hiện văn bản dài và cong, **LOMO**[19] đề xuất phương pháp lặp để tối ưu hóa đặc trưng định vị văn bản, nhằm thu được vị trí văn bản chính xác hơn. LOMO gồm bộ hồi quy trực tiếp (DR), module tinh chỉnh lặp (IRM), và module biểu diễn hình dạng (SEM). Vùng văn bản được sinh bởi DR, sau đó IRM tinh chỉnh đặc trưng định vị văn bản lặp, và cuối cùng SEM được giới thiệu để dự đoán vùng văn bản, đường tâm và độ lệch biên. Tối ưu hóa lặp của đặc trưng văn bản có thể giải quyết tốt hơn định vị văn bản dài và định vị vùng văn bản chính xác hơn.

*Hình 11: Sơ đồ frame của LOMO*

**ContourNet**[18] đề xuất mô hình hóa điểm đường viền văn bản để có hộp phát hiện của văn bản cong. Đầu tiên, Adaptive-RPN được đề xuất để sinh đề xuất vùng văn bản. Sau đó, Local Orthogonal Texture-aware Module (LOTM) học đặc trưng kết cấu ngang và dọc, biểu diễn chúng bằng điểm đường viền. Cuối cùng, xem xét phản hồi đặc trưng ở hai hướng trực giao, thuật toán Point Re-Scoring được dùng để lọc dự đoán có kích hoạt một chiều mạnh hoặc trực giao yếu, đảm bảo đường viền văn bản có thể được biểu diễn bằng tập hợp các điểm đường viền chất lượng cao.

*Hình 12: Sơ đồ frame của Contournet*

**PCR**[14] khuyến nghị phát hiện văn bản cong bằng hồi quy tọa độ tiệm tiến. Giải pháp có ba giai đoạn. Đầu tiên, phát hiện vùng văn bản thô và lấy một hộp văn bản. Thứ hai, Contour Localization Mechanism được thiết kế để dự đoán góc của hộp bao nhỏ nhất của văn bản. Cuối cùng, xếp chồng module CLM và RCLM để dự đoán văn bản cong. Phương pháp hồi quy đường viền tiệm tiến có thể giúp có biểu diễn văn bản tinh chỉnh hơn, không chỉ bảo vệ hồi quy tọa độ khỏi bị ảnh hưởng bởi nhiễu dư thừa mà còn định vị vùng văn bản chính xác hơn.

*Hình 13: Sơ đồ frame của PCR*

### 4.1.2 Phát hiện văn bản dựa trên phân đoạn

Mặc dù phương pháp dựa trên hồi quy hoạt động tốt trong phát hiện văn bản, chúng thường khó vạch ra một văn bản cong có đường cong mượt mà, và mô hình của chúng phức tạp hơn nhưng không vượt trội về hiệu năng. Do đó, các nhà nghiên cứu đã đề xuất phương pháp phân đoạn văn bản dựa trên phân đoạn ảnh. Đầu tiên, phân loại các pixel, xác định mỗi pixel có khớp với một mục tiêu văn bản. Sau đó nhận đồ thị xác suất của vùng văn bản, và lấy đường cong vạch văn bản đã phân đoạn qua hậu xử lý.

*Hình 14: Sơ đồ thuật toán phân đoạn văn bản — Input Image → Text Segmentation → output → PostProcess → Text Polygon → visualization*

Các phương pháp này thường dựa trên phân đoạn để đạt phát hiện văn bản, và phương pháp dựa trên phân đoạn có lợi thế tự nhiên cho phát hiện văn bản với hình dạng bất thường. Ý tưởng chính là lấy vùng văn bản trong ảnh qua phương pháp phân đoạn, sau đó dùng OpenCV, đa giác và hậu xử lý khác để có đường cong bao tối thiểu của vùng văn bản.

**PixelLink**[7] dùng phân đoạn để phát hiện văn bản. Đối tượng được phân đoạn là một vùng văn bản. Các pixel của cùng một dòng văn bản (từ) được liên kết với nhau để phân đoạn văn bản, và hộp văn bản được trích từ phân đoạn mà không cần hồi quy vị trí. Kết quả phát hiện văn bản tốt như những phương pháp dựa trên hồi quy. Tuy nhiên, có một vấn đề với phương pháp dựa trên phân đoạn. Với văn bản ở các vị trí tương tự, vùng phân đoạn dễ "dính" vào nhau. Wu, Yue et al.[8] đã đề xuất tách văn bản và học vị trí biên văn bản để phân biệt vùng văn bản tốt hơn. Ngoài ra, Tian et al.[9] đã đề xuất ánh xạ các pixel của cùng một văn bản vào không gian ánh xạ, nơi khoảng cách của các vector ánh xạ của cùng một văn bản gần nhau, và những vector của văn bản khác thì xa nhau.

*Hình 15: Sơ đồ frame của PixelLink*

Với vấn đề đa tỉ lệ của phát hiện văn bản, **MSR**[20] khuyến nghị trích đặc trưng đa tỉ lệ từ cùng một ảnh, sau đó hợp các đặc trưng và upsample chúng về kích thước ảnh gốc. Cuối cùng, mạng đa tỉ lệ dự đoán vùng tâm văn bản và offsetX, offsetY của mỗi điểm ở vùng tâm đến điểm biên gần nhất. Cuối cùng, có thể lấy tập tọa độ của đường viền vùng văn bản.

*Hình 16: Sơ đồ frame của MSR*

Xét đến việc thuật toán văn bản dựa trên phân đoạn có khó khăn trong phân biệt văn bản kề nhau, **PSENet**[10] áp dụng mạng mở rộng tỉ lệ tiệm tiến mới lạ để học vùng văn bản đã phân đoạn, dự đoán vùng văn bản với các tỉ lệ co rút khác nhau, và mở rộng các vùng văn bản đã phát hiện. Bản chất của phương pháp này là một biến thể của phương pháp học đường biên, phát hiện hiệu quả văn bản kề nhau ở bất kỳ hình dạng nào.

*Hình 17: Sơ đồ frame của PSENet*

Giả sử ba kernel ở các tỉ lệ khác nhau được dùng trong hậu xử lý PSENet, như trong hình trên (s1, s2, s3). Đầu tiên, kernel nhỏ nhất s1 tính miền liên thông của vùng văn bản đã phân đoạn, được (b), sau đó mở rộng miền liên thông xung quanh, và phân loại pixel của s2 thay vì s1 trong vùng đã mở rộng. Khi có xung đột, lặp lại mở rộng theo nguyên tắc "ai đến trước được trước", và cuối cùng tất cả các dòng văn bản có thể được phân đoạn thành vùng riêng lẻ.

Với văn bản cong và dày đặc, **Seglink++**[17] đề xuất đặc trưng hóa lực hút và đẩy giữa các đoạn văn bản, dùng thuật toán cây bao trùm tối thiểu để kết hợp các đoạn để có hộp phát hiện văn bản và hàm mất mát nhận thức instance để cho phép huấn luyện end-to-end.

*Hình 18: Sơ đồ frame của Seglink++*

Mặc dù phân đoạn thực hiện phát hiện văn bản cong, logic hậu xử lý phức tạp và tốc độ dự đoán cũng cần tối ưu. **PAN**[11] nhắm vào tăng tốc phát hiện và dự đoán văn bản bằng cách cải thiện thiết kế mạng và hậu xử lý để nâng cao hiệu năng. Đầu tiên, PAN dùng ResNet18 nhẹ làm backbone, và thiết kế module tăng cường đặc trưng nhẹ FPEM và module hợp nhất đặc trưng FFM để cải thiện đặc trưng trích bởi backbone. Về hậu xử lý, PAN dùng phân cụm pixel để gộp các pixel có khoảng cách từ kernel nhỏ hơn ngưỡng d quanh tâm văn bản dự đoán (kernel). Giải pháp này đảm bảo cả độ chính xác và tốc độ dự đoán nhanh.

*Hình 19: Sơ đồ frame của PAN*

**DBNet**[12] nhằm tối ưu hóa hậu xử lý tốn thời gian trong phương pháp dựa trên phân đoạn cần dùng ngưỡng để nhị phân hóa. Đề xuất ngưỡng có thể học và hàm nhị phân hóa tương tự hàm bậc thang để đảm bảo mạng phân đoạn học ngưỡng phân đoạn end-to-end trong huấn luyện. Việc điều chỉnh tự động ngưỡng không chỉ cải thiện độ chính xác mà còn đơn giản hóa hậu xử lý và cải thiện hiệu năng phát hiện văn bản.

*Hình 20: Sơ đồ frame của DB*

**FCENet**[16] biểu diễn đường cong vạch văn bản với tham số biến đổi Fourier. Vì hệ số Fourier có thể về mặt lý thuyết khớp với bất kỳ đường cong khép kín nào, FCENet thiết kế mô hình phù hợp để dự đoán biểu diễn của đường cong vạch ở hình dạng tùy ý dựa trên biến đổi Fourier. Theo cách này, độ chính xác phát hiện văn bản cong cao trong cảnh tự nhiên có thể được cải thiện.

*Hình 21: Sơ đồ frame của FCENet*

## 4.2 Thực hành thuật toán phát hiện văn bản DBNet

Phần này sẽ giới thiệu cách dùng PaddleOCR để hoàn thành huấn luyện và triển khai thuật toán DB cho phát hiện văn bản, bao gồm:

1. Gọi nhanh gói PaddleOCR để thử phát hiện văn bản
2. Hiểu nguyên lý thuật toán DB
3. Học quy trình xây dựng mô hình phát hiện văn bản
4. Học huấn luyện mô hình phát hiện văn bản

> Lưu ý: `paddleocr` ám chỉ gói `PaddleOCR whl`.

### 4.2.1 Bắt đầu nhanh

Phần này sẽ lấy `paddleocr` làm ví dụ để giới thiệu cách nhanh chóng triển khai phát hiện văn bản trong ba bước:

1. Cài gói PaddleOCR whl
2. Phát hành lệnh để chạy thuật toán DB lấy kết quả phát hiện
3. Trực quan hóa kết quả phát hiện văn bản

**Cài gói PaddleOCR whl**

```bash
!pip install --upgrade pip
!pip install paddleocr
```

**Phát hành lệnh để thực hiện phát hiện văn bản**

Lần thực hiện đầu, `paddleocr` sẽ tự động tải và vận hành **mô hình nhẹ PP-OCRv2** trong kho GitHub của PaddleOCR.

Nhập ảnh `./12.jpg` vào `paddleocr` đã cài sẽ được kết quả sau:

*Hình 1: Ảnh ./12.jpg — biển hiệu khách sạn và căn hộ tiếng Trung*

```
[[79.0, 555.0], [398.0, 542.0], [399.0, 571.0], [80.0, 584.0]]
[[21.0, 507.0], [512.0, 491.0], [513.0, 532.0], [22.0, 548.0]]
[[174.0, 458.0], [397.0, 449.0], [398.0, 480.0], [175.0, 489.0]]
[[42.0, 414.0], [482.0, 392.0], [484.0, 428.0], [44.0, 450.0]]
```

Kết quả suy luận có bốn hộp văn bản, mỗi hộp chứa bốn tọa độ, tức là tập tọa độ của mỗi hộp văn bản, được sắp xếp theo chiều kim đồng hồ từ trên trái.

Lệnh `paddleocr` gọi mô hình phát hiện văn bản để dự đoán ảnh `./12.jpg`, được hiển thị như sau:

---

*— Hết phần dịch trang 10–50 —*

*Phần tiếp theo sẽ tiếp tục từ trang 51 trở đi (huấn luyện mô hình DB, chi tiết thuật toán, ...).*
