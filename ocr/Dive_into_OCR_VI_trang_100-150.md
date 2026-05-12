# Dive into OCR — Tóm tắt tiếng Việt (Trang 100–150)

*Tiếp nối từ file dịch trang 50–100. Phần này tóm tắt phần còn lại Chương 5 (CRNN code, huấn luyện, FAQ) và Chương 6 (PP-OCR System & Strategy).*

> Phần này là **bản tóm tắt giáo dục** bằng tiếng Việt, không phải bản dịch nguyên văn. Mã nguồn đầy đủ tham khảo:
> - Repo PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
> - File config: https://github.com/PaddlePaddle/PaddleOCR/tree/release/2.4/configs

---

## Phần 5.2.2 (tiếp) — Triển khai chi tiết CRNN

### Ví dụ mã CRNN

CRNN có cấu trúc đơn giản, mã triển khai theo 4 phần: **nhập dữ liệu, backbone, neck, head**.

**1. Nhập dữ liệu (Data Input)**

Dữ liệu cần được scale về kích thước thống nhất `(3, 32, 320)` và chuẩn hóa trước khi đưa vào mạng. Hàm `resize_norm_img(img)` thực hiện:
- Tính tỉ lệ khung hình của ảnh
- Scale theo chiều cao 32 và giữ tỉ lệ chiều rộng, giới hạn tối đa 320
- Chuẩn hóa: trừ 0.5, chia 0.5
- Padding 0 cho phần không đủ chiều rộng

**2. Backbone (MobileNetV3)**

PaddleOCR dùng **MobileNetV3** làm backbone. Mã định nghĩa các module công cộng:

- `ConvBNLayer`: tầng tích chập + BatchNorm + activation (relu hoặc hardswish)
- `SEModule` (Squeeze-and-Excitation): avg pooling toàn cục, hai tầng 1×1 conv với reduction, hardsigmoid activation, nhân với đầu vào để tái cân bằng kênh
- `ResidualUnit`: khối residual gồm expand_conv → bottleneck_conv (depthwise) → optional SE → linear_conv
- `make_divisible(v, divisor=8)`: đảm bảo channel chia hết cho 8

`MobileNetV3` class có hai chế độ (`small`/`large`), tham số `scale` điều chỉnh số kênh, `disable_se` cho phép tắt SE module. Với ảnh đầu vào `(1, 3, 32, 320)`, đầu ra backbone là một feature map dùng cho recognition.

**3. Neck — Im2Seq + EncoderWithRNN**

- `Im2Seq`: chuyển feature map 2D thành chuỗi 1D bằng cách squeeze chiều cao (H phải = 1) và transpose thành `(batch, width, channels)` = (N, W, C).
- `EncoderWithRNN`: BiLSTM 2 tầng (`direction='bidirectional', num_layers=2`).
- `SequenceEncoder`: kết hợp `Im2Seq` và `EncoderWithRNN`. Đầu vào `hidden_size=48`, đầu ra `hidden_size*2 = 96` (do bidirectional).

**4. Head — CTCHead**

`CTCHead`: tầng fully-connected ánh xạ đặc trưng chuỗi sang phân phối xác suất nhãn. Ví dụ có `out_channels=37` (26 chữ cái thường + 10 số + 1 ký tự blank).

Khi suy luận, áp dụng softmax theo axis=2 để có xác suất; khi huấn luyện trả về logits trực tiếp.

**5. Hậu xử lý — Decoding**

Hàm `decode(text_index, text_prob, is_remove_duplicate=False)`:
- Bỏ qua token blank (id=0)
- Khi `is_remove_duplicate=True` (chỉ dùng khi predict), gộp các ký tự lặp liền kề
- Trả về danh sách `(text, confidence_mean)`

Bộ ký tự ví dụ: `"-0123456789abcdefghijklmnopqrstuvwxyz"` (37 ký tự).

Mạng chưa huấn luyện sẽ cho kết quả ngẫu nhiên. Cần định nghĩa loss và optimizer rồi huấn luyện thực sự.

---

## 5.2.3 Huấn luyện mô hình CRNN

### Chuẩn bị dữ liệu

PaddleOCR hỗ trợ 2 định dạng:
- `lmdb` — dữ liệu lưu định dạng LMDB (`LMDBDataSet`)
- `General Data` — dữ liệu lưu file văn bản (`SimpleDataSet`)

Dữ liệu mặc định lưu ở `./train_data`. Định dạng nhãn:
```
train/word_1.png    Genaxis Theatre
train/word_2.png    [06]
```
> Lưu ý: phân cách `\t` (tab), không dùng ký tự khác.

**Cấu trúc thư mục:**
```
train_data/ic15_data/
├── rec_gt_train.txt
├── train/word_001.png, word_002.jpg, ...
├── rec_gt_test.txt
└── test/word_001.png, word_002.jpg, ...
```

**File cấu hình** `rec_icdar15_train.yml` định nghĩa:
- `Train`/`Eval`: dataset, transforms (`DecodeImage`, `CTCLabelEncode`, `RecResizeImg`, `KeepKeys`)
- `loader`: shuffle, batch_size_per_card (256), num_workers (8)

### Tiền xử lý dữ liệu

- **Scaling và Normalization**: dùng `resize_norm_img` (giống phần 5.2.2)
- **Data Augmentation**: PaddleOCR có nhiều cách — đảo màu, phân đoạn ngẫu nhiên, biến đổi affine, nhiễu ngẫu nhiên... Ví dụ `get_crop(image)` cắt ngẫu nhiên phần trên ảnh để mô phỏng ảnh thực bị xuống cấp.

### Chương trình huấn luyện chính

Mã entry là `train.py`, gồm các module: `build_dataloader`, `build_post_process`, `build_model`, `build_loss`, `build_optim`, `build_metric`.

- **Build dataloader**: dùng `SimpleDataSet`, `__getitem__` trả về dict `{'img_path', 'label', 'image'}`.
- **Build model**: xây mạng theo phần 5.2.2.
- **Build loss — CTCLoss**:
  ```python
  class CTCLoss(nn.Layer):
      def __init__(self, use_focal_loss=False):
          self.loss_func = nn.CTCLoss(blank=0, reduction='none')
      def forward(self, predicts, batch):
          predicts = predicts.transpose((1, 0, 2))  # (T, N, C)
          # tính độ dài và áp CTC loss
          return {'loss': loss.mean()}
  ```
- **Build optim**: `paddle.optimizer.Adam`.
- **Build metric**: tính accuracy theo dòng — dự đoán đúng toàn bộ câu mới tính là đúng.
  ```python
  def metric(preds, labels):
      correct = sum(1 for p, t in zip(preds, labels) if p.replace(' ','') == t.replace(' ',''))
      return {'acc': correct / len(preds)}
  ```

Hàm `main(config, device, logger, vdl_writer)` ghép tất cả lại và gọi `program.train(...)`.

### Bắt đầu huấn luyện

```bash
git clone https://gitee.com/paddlepaddle/PaddleOCR  # hoặc github
cd PaddleOCR && pip install -r requirements.txt

# Tải mô hình tiền huấn luyện MobileNetV3 cho recognition
wget -P ./pretrain_models/ \
  https://paddleocr.bj.bcebos.com/dygraph_v2.0/en/rec_mv3_none_bilstm_ctc_v2.0_train.tar
tar -xf pretrain_models/rec_mv3_none_bilstm_ctc_v2.0_train.tar

# Chạy huấn luyện
python3 tools/train.py -c configs/rec/rec_icdar15_train.yml \
  -o Global.pretrained_model=rec_mv3_none_bilstm_ctc_v2.0_train/best_accuracy \
     Global.character_dict_path=ppocr/utils/ic15_dict.txt \
     Global.eval_batch_step=[0,200] \
     Global.epoch_num=40
```

Mô hình được lưu trong `output/rec/ic15/`:
- `best_accuracy.*` — mô hình tốt nhất trên tập eval
- `iter_epoch_x.*` — lưu định kỳ
- `latest.*` — mô hình mới nhất

### Đánh giá và dự đoán

```bash
# Đánh giá
python tools/eval.py -c configs/rec/rec_icdar15_train.yml \
  -o Global.checkpoints=output/rec/ic15/best_accuracy \
     Global.character_dict_path=ppocr/utils/ic15_dict.txt

# Dự đoán
python tools/infer_rec.py -c configs/rec/rec_icdar15_train.yml \
  -o Global.checkpoints=output/rec/ic15/best_accuracy \
     Global.character_dict_path=ppocr/utils/ic15_dict.txt
```

Kết quả: `result: slow  0.8795223`

---

## 5.2.4 FAQ về Nhận dạng văn bản

### Câu hỏi chung

**Q1.1** PaddleOCR cung cấp các thuật toán nhận dạng nào?
→ Có 5 thuật toán chính: **CRNN, StarNet, RARE, Rosetta** (dựa CTC); **SRN** (Baidu phát triển, kết hợp ngữ nghĩa, độ chính xác cao hơn).

**Q1.2** Công nghệ then chốt trong CRNN?
→ (1) Trích đặc trưng CNN, (2) BiLSTM trích đặc trưng chuỗi, (3) CTC giải vấn đề căn chỉnh ký tự.

**Q1.3** CTC hay Attention tốt hơn cho tiếng Trung?
→ CTC tốt hơn về hiệu quả vì từ điển tiếng Trung lớn (>3000 ký tự). Attention không ưu thế khi thiếu mẫu huấn luyện và phù hợp văn bản ngắn hơn. CTC cũng nhanh hơn (Attention dùng decoder tuần tự).

**Q1.4** Cách nhận dạng văn bản cong, ứng dụng TPS?
→ (1) Nếu cong nhẹ: phát hiện 4 đỉnh, biến đổi affine. (2) TPS (Thin Plate Spline) dùng nội suy với các điểm điều khiển, áp dụng cho văn bản cong. Đã tích hợp trong STAR-Net và RARE.
> **Cảnh báo**: TPS lý thuyết tốt nhưng ứng dụng kém ổn định, làm nhận dạng tốn thời gian hơn — cân nhắc kỹ.

### Ứng dụng nhận dạng văn bản trong các kịch bản chiều dọc

**Q2.1** Nhận dạng văn bản bị mờ bởi nền (như chữ ký với dấu)?
→ Đảm bảo hộp phát hiện đúng; thêm dữ liệu với lọc màu và nhãn liên quan. Có thể thử backbone lớn hơn như ResNet.

**Q2.2** Cải thiện ảnh đối với văn bản mờ?
→ Thêm tăng cường dữ liệu mờ (mean/median/gaussian filter); thử adversarial training và super resolution (SR).

**Q2.3** Giải pháp SR cho văn bản phân giải thấp?
→ **SRCNN** kinh điển; xem CVPR 2020 "Unpaired Image Super-Resolution using Pseudo-Supervision".

**Q2.4** Cách nhận dạng văn bản dài?
→ Trong huấn luyện tiếng Trung, scale ảnh theo chiều cao 32, không trực tiếp ép `(3,32,320)`. Nếu chiều rộng < 320, padding 0. Nếu tỉ lệ width/height > 10, loại bỏ. Khi suy luận theo batch, dùng max width.

**Q2.5** Nhận dạng tiếng Anh có khoảng trắng?
→ (1) Tối ưu thuật toán phát hiện để tách dòng theo khoảng trắng. (2) Thêm ký tự space vào từ điển nhận dạng.

**Q2.6** TPS của OpenCV có thể hiệu chỉnh văn bản cong không?
→ TPS OpenCV cần nhãn điểm biên trên/dưới — khó. Module TPS của StarNet trong PaddleOCR học các điểm này tự động.

**Q2.7** Nhận dạng chữ nghệ thuật trên biển hiệu?
→ Khó vì phong cách khác chữ in. Nếu danh sách chữ trong từ điển cố định: biến mỗi mục từ điển thành template ảnh, dùng hệ thống nhận dạng ảnh tổng quát (PaddleClas).

**Q2.8** Nhận dạng văn bản con dấu (seal)?
→ (1) Dùng mạng có TPS hoặc ABCNet. (2) Phẳng ảnh qua biến đổi tọa độ cực, sau đó dùng CRNN.

**Q2.9** Hiệu suất kém với ký tự đặc biệt khi dùng mô hình tiền huấn luyện?
→ Vì mô hình huấn luyện trên dữ liệu phổ thông. Xây tập dữ liệu cụ thể với mỗi ký tự xuất hiện ≥300 lần và cân bằng — fine-tune.

**Q2.10** Ký tự lặp khi suy luận?
→ Kiểm tra dimension huấn luyện và suy luận có khớp không (ví dụ [3,32,320] vs [3,64,640]).

**Q2.11** Chữ Hán cổ trên thanh tre?
→ Nếu là chữ Hán phổ thông: gán nhãn đủ và fine-tune (có thể dùng StyleText). Nếu là ký tự đặc biệt (giáp cốt, chữ tượng hình): tạo từ điển chuyên biệt và huấn luyện.

**Q2.12** Nhận dạng văn bản trong video?
→ PaddleOCR hiện chỉ xử lý ảnh. Trích frame từ video rồi dùng PaddleOCR.

**Q2.13** Fine-tune mô hình tiếng Trung-Anh để thêm số La Mã?
→ (1) Chuẩn bị data tiếng Trung, Anh và số La Mã. (2) Thêm ký tự La Mã vào cuối file từ điển. (3) Tải mô hình tiền huấn luyện, cấu hình và huấn luyện.

**Q2.14** Một số ký tự đặc biệt (như dấu câu) nhận dạng kém?
→ Kiểm tra ký tự có trong từ điển không. Nếu có nhưng vẫn kém: thêm dữ liệu liên quan để fine-tune.

**Q2.15** Ảnh chứa nhiều loại văn bản (in + viết tay)?
→ Phương án "1 detection model + 1 N-class model + N recognition models". N-class classifier phân loại loại văn bản trong hộp; mỗi loại có recognition model riêng.

**Q2.16** Từ điển chứa nhiều loại văn bản, có gì đặc biệt?
→ FC layer lớp cuối lớn lên, kích thước mô hình tăng. Tốt nhất tách từ điển theo loại.

**Q2.17** Ngôn ngữ nhỏ như Thái — một từ có thể chiếm 2-3 ký tự?
→ Coi toàn bộ từ là một đơn vị. Đảm bảo mỗi dòng chỉ một từ.

### Quy trình huấn luyện và tối ưu mô hình

**Q3.1** Tăng `batch_size` không tăng tốc độ huấn luyện?
→ Tăng giá trị bộ nhớ ban đầu: `export FLAGS_initial_cpu_memory_in_mb=2000` (~2GB).

**Q3.2** Cảnh báo ảnh/video quá lớn và rò rỉ bộ nhớ?
→ Theo PR #2230 của PaddleOCR.

**Q3.3** Train ACC=90 nhưng val ACC=70?
→ Có thể overfitting. (1) Thêm augmentation hoặc tăng xác suất (mặc định 0.4). (2) Tăng L2 decay.

---

## 5.2.5 Bài tập

**Task 1**: Trực quan kết quả Data Augmentation trong PaddleOCR (noise, jitter) và giải thích.

**Task 2**: Thay backbone trong `configs/rec/rec_icdar15_train.yml` bằng **ResNet34_vd**. Với đầu vào (3, 32, 100), kích thước feature output của head là bao nhiêu?

**Task 3**: Tải tập tiếng Trung 10W `rec_data_lesson_demo`, chỉnh config và huấn luyện. Pretrain model: https://paddleocr.bj.bcebos.com/dygraph_v2.0/en/rec_mv3_none_bilstm_ctc_v2.0_train.tar

## 5.3 Tổng kết

Chương này giới thiệu lý thuyết và thực hành nhận dạng văn bản, bao gồm các phương pháp dựa **CTC**, **Sequence2Sequence**, **Segmentation**, **Transformer**. Phần thực hành CRNN minh họa toàn bộ quy trình từ mạng đến tối ưu.

## 5.4 Tài liệu tham khảo

Gồm 17 bài báo chính:
1. Shi, B., Bai, X., & Yao, C. (2016) — CRNN
2. Borisyuk, F. et al. (2018) — Rosetta
3. Gao, Y. et al. (2017) — Attention convolutional sequence modeling
4. Shi, B. et al. (2016) — RARE
5. Jaderberg, M. et al. (2015) — Spatial transformer networks (STAR-Net)
6. Shi, B. et al. (2018) — ASTER
7. Lee, C.Y., Osindero, S. (2016) — R²AM
8. Li, H. et al. (2019) — SAR
9. Lyu, P. et al. (2018) — Mask TextSpotter
10. Liao, M. et al. (2019) — 2D perspective text recognition
11. Yu, D. et al. (2020) — SRN
12. Sheng, F. et al. (2019) — NRTR
13. Yang, L. et al. (2020) — Holistic attention
14. Wang, T. et al. (2020) — Decoupled attention (DAN)
15. Wang, Y. et al. (2021) — PREN
16. Fang, S. et al. (2021) — ABINet
17. Yan, R. et al. (2021) — Primitive Representation Learning

---

# CHƯƠNG 6 — HỆ THỐNG VÀ CHIẾN LƯỢC PP-OCR

Hai chương trước nói về **DBNet** (phát hiện) và **CRNN** (nhận dạng). Nhưng trong cảnh thực, không thể vừa lấy vị trí vừa nội dung văn bản chỉ từ một mô hình. Vì vậy, ta nối hai mô hình thành hệ thống PP-OCR. Hơn nữa, hướng văn bản phát hiện được có thể không như mong muốn — gây sai trong nhận dạng. Do đó PP-OCR thêm **bộ phân loại hướng (direction classifier)**.

Chương này giới thiệu:
- Kỹ năng tinh chỉnh chiến lược trong PaddleOCR
- Kỹ thuật tối ưu hóa cho phát hiện, nhận dạng và bộ phân loại hướng

PP-OCR đã trải qua 2 giai đoạn tối ưu hóa.

## 6.1 Giới thiệu PP-OCR

### 6.1.1 Hệ thống PP-OCR và chiến lược tối ưu

Quy trình PP-OCR:
1. **Phát hiện văn bản** (DBNet trong PP-OCR) → lấy đa giác văn bản (hộp 4 điểm)
2. **Cắt và hiệu chỉnh phối cảnh** → chuyển vùng văn bản thành hình chữ nhật, dùng direction classifier sửa hướng
3. **Nhận dạng văn bản** (CRNN) → lấy kết quả văn bản

*Hình 1: Sơ đồ hệ thống PP-OCR — `Image → Text Detection (db_mv3_slim, 1.4M) → Detection Boxes Rectify (dir_cls_mv3_slim, 0.5M) → Text Recognition (crnn_mv3_slim, 1.6M) → Output`*

**19 chiến lược tối ưu** trong các phần backbone, learning rate, data augmentation, model tailoring và quantization để có hệ thống server và mobile.

### 6.1.2 PP-OCRv2 — cải tiến

So với PP-OCR, PP-OCRv2 cải tiến **backbone, data augmentation, loss function** để giảm:
- Hiệu suất dự đoán end-to-end kém
- Nền phức tạp
- Nhận nhầm ký tự tương tự

PP-OCRv2 cũng giới thiệu **knowledge distillation** để tăng độ chính xác.

**Cải tiến cụ thể:**
- *Phát hiện*: (1) **CML** (Collaborative Mutual Learning) — chiến lược chưng cất; (2) **CopyPaste** — augmentation
- *Nhận dạng*: (1) **PP-LCNet**; (2) **U-DML** — chưng cất; (3) **Enhanced CTC loss**

**Kết quả:**
- Hiệu quả mô hình tăng >7% so với PP-OCR mobile
- Tốc độ tăng >220% so với PP-OCR server
- Kích thước 11.6M — dễ triển khai trên cả server và mobile

*Hình 3: Sơ đồ PP-OCRv2 với các chiến lược trong khung xanh (giữ từ PP-OCR), khung cam (mới trong v2), khung xám (sẽ dùng trong v2-tiny tương lai)*

## 6.2 Chiến lược tối ưu PP-OCR

Gồm 3 hướng: text detector, direction classifier, text recognizer.

### 6.2.1 Phát hiện văn bản

Detection trong PP-OCR dùng **DBNet** (dựa phân đoạn, hậu xử lý đơn giản).

DBNet trích đặc trưng qua backbone, dùng neck **DBFPN** để hợp đặc trưng, head sinh probability map và threshold map. Khi tính loss, tính cả 3 feature map; binary supervision được áp dụng để mô hình học biên chính xác hơn.

**6 chiến lược tối ưu trong DBNet:**

#### Lightweight Backbone Network

Kích thước backbone ảnh hưởng lớn đến kích thước detector. **MobileNetV1, V2, V3, ShuffleNetV2** thường dùng làm backbone nhẹ. **PaddleClas** cung cấp >20 backbone nhẹ với benchmark accuracy-speed sẵn trên ARM.

PP-OCR chọn **MobileNetV3_large 0.5x** để cân bằng độ chính xác và hiệu suất.

Feature map của mỗi stage MobileNetV3 trong DBNet (đầu vào (1, 3, 640, 640)):
```
stage 0: [1, 16, 160, 160]
stage 1: [1, 24, 80, 80]
stage 2: [1, 56, 40, 40]
stage 3: [1, 480, 20, 20]
```

#### Cấu trúc DBFPN nhẹ

DBFPN hợp feature map nhiều scale để cải thiện phát hiện text các kích thước. Dùng conv 1×1 để giảm channel về cùng số. `inner_channels` ảnh hưởng lớn đến kích thước mô hình:
- inner_channels = 256: kích thước 7M
- inner_channels = 96: kích thước 4.1M, tốc độ tăng 48%, độ chính xác giảm nhẹ

#### Phân tích & loại bỏ SE Module

SE (Squeeze-and-Excitation) trong MobileNetV3 ước lượng quan trọng của mỗi kênh đặc trưng. Tuy nhiên với độ phân giải đầu vào lớn (640×640), SE tốn nhiều thời gian mà cải thiện hạn chế.

→ **Loại SE module khỏi backbone DBNet**, giảm kích thước từ 4.1M xuống 2.6M, độ chính xác gần như giữ nguyên.

```python
backbone_mv3 = MobileNetV3(scale=0.5, model_name='large', disable_se=True)
```

#### Tối ưu Learning Rate

**Cosine Learning Rate Reduction**: Learning rate (lr) là hyperparameter điều khiển tốc độ cập nhật weight. Đầu huấn luyện (weight ngẫu nhiên) → cần lr lớn để hội tụ nhanh. Cuối huấn luyện (weight gần optimal) → lr nhỏ để tránh dao động. **Cosine decay** giảm lr theo đường cosine từ giá trị ban đầu xuống 0.

So với **piecewise decay** (giảm theo bậc thang ở các epoch cụ thể), cosine decay hội tụ chậm hơn nhưng chính xác hơn.

**Learning Rate Warm-up**: ở đầu huấn luyện, weight ngẫu nhiên, nếu lr lớn ngay có thể không ổn định. Warm-up tăng lr từ giá trị nhỏ lên giá trị mục tiêu trong vài epoch đầu (mặc định 2 epoch). Kết hợp warm-up + cosine cho hiệu quả tốt nhất.

#### Model Tailoring — FPGM

**FPGM** (Filter Pruning via Geometric Median): mỗi filter trong conv layer là một điểm trong không gian Euclidean; điểm nào gần "geometric median" (điểm có tổng khoảng cách đến tất cả các điểm khác nhỏ nhất) thì thông tin của nó chồng lấp với các filter khác và có thể bỏ.

Áp dụng FPGM cho DBNet: độ chính xác giảm nhẹ, **kích thước mô hình giảm 46%, tốc độ tăng 19%**.

**Lưu ý khi tailoring:**
1. Sau pruning cần huấn luyện lại
2. Code tailoring tùy chỉnh cho DBNet — nếu prune mô hình khác cần phân tích cấu trúc và độ nhạy tham số
3. Tailoring rate của mỗi layer khác nhau quan trọng — không thể dùng cùng rate cho mọi layer
4. Cần nhiều thí nghiệm

### Mô tả file cấu hình DBNet

```yaml
Architecture:
  model_type: det
  algorithm: DB
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
    disable_se: True       # Loại SE
  Neck:
    name: DBFPN
    out_channels: 96       # Giảm inner_channels
  Head:
    name: DBHead
    k: 50

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine           # Cosine decay
    learning_rate: 0.001
    warmup_epoch: 2        # Warm-up 2 epoch
  regularizer:
    name: 'L2'
    factor: 0
```

### Tổng kết tối ưu phát hiện PP-OCR

Bảng ablation:

| inner_channel | Remove SE | Cosine | Warm-up | Precision | Recall | HMean | Size (M) | Time (CPU, ms) |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 256 |   |   |   | 0.6821 | 0.5560 | 0.6127 | 7   | 406 |
| 96  |   |   |   | 0.6677 | 0.5524 | 0.6046 | 4.1 | 213 |
| 96  | ✓ |   |   | 0.6952 | 0.5413 | 0.6087 | 2.6 | 173 |
| 96  | ✓ | ✓ |   | 0.7034 | 0.5404 | 0.6112 | 2.6 | 173 |
| 96  | ✓ | ✓ | ✓ | 0.7349 | 0.5420 | 0.6239 | 2.6 | 173 |

Qua các chiến lược, kích thước DBNet giảm từ **7M xuống 1.5M** (tính cả tailoring), độ chính xác **tăng >1%**.

### 6.2.2 Bộ phân loại hướng (Direction Classifier)

Mục tiêu: phân loại hướng của instance văn bản, xoay về 0° rồi gửi sang text recognizer. PP-OCR chọn 2 hướng: **0°** và **180°**.

#### Lightweight Backbone

Dùng **MobileNetV3_small 0.35x** — task phân loại đơn giản hơn, backbone lớn hơn không cải thiện đáng kể.

So sánh backbone:
| Backbone | Size(M) | Accuracy | Time(CPU ms) |
|---|---|---|---|
| MobileNetV3_small_x0.5 | 1.34 | 0.9494 | 3.22 |
| MobileNetV3_small_x0.35 | 0.85 | 0.9403 | 3.21 |
| ShuffleNetV2_x0.5 | 1.72 | 0.9017 | 3.41 |

#### Data Augmentation

**BDA (Base Data Augmentation)**: rotation, perspective distortion, motion blur, gaussian noise — cải thiện đáng kể độ chính xác direction classifier.

Thử thêm augmentation cấp cao:
- *Image transformation*: AutoAugment, RandAugment
- *Image tailoring*: CutOut, RandErasing, HideAndSeek, GridMask
- *Image mixing*: Mixup, Cutmix

Thí nghiệm cho thấy chỉ **RandAugment** và **RandomErasing** phù hợp:

| Chiến lược | Accuracy |
|---|---|
| Không augmentation | 0.8879 |
| BDA | 0.9134 |
| BDA + RandAugment | **0.9212** |
| BDA + RandomErasing | 0.9193 |
| BDA + AutoAugment | 0.9133 |
| BDA + GridMask | 0.914 |
| BDA + Mixup | 0.9104 |
| BDA + CutMix | 0.9083 |
| BDA + Cutout | 0.9081 |
| BDA + HideAndSeek | 0.8598 |

→ Kết hợp **BDA + RandAugment**.

Demo RandAugment:
```python
from ppocr.data.imaug import DecodeImage, RandAugment, transform
ops_list = [DecodeImage(), RandAugment()]
data = transform(data, ops_list)
```

#### Input Resolution Optimization

Tăng độ phân giải đầu vào → độ chính xác tăng. Vì tham số backbone direction classifier rất nhỏ nên tăng độ phân giải không tăng đáng kể thời gian suy luận.

Thay đổi từ `3×32×100` → `3×48×192`: accuracy **tăng từ 92.1% lên 94.0%**, thời gian dự đoán chỉ tăng từ 3.19ms lên 3.21ms.

#### Model Quantization — PACT

**Quantization**: chuyển tính toán floating point sang fixed point — giảm latency, kích thước và tài nguyên.

- *Offline quantization*: dùng KL divergence để xác định tham số quantization, không cần huấn luyện lại
- *Online quantization*: xác định tham số trong huấn luyện — sai số nhỏ hơn

**PACT** (PArameterized Clipping acTivation): loại bỏ các giá trị cực trị từ activation layer trước. Công thức gốc:
$$y = PACT(x) = 0.5 (|x| - |x - \alpha| + \alpha)$$

Với MobileNetV3 (dùng cả ReLU và hardswish), công thức được điều chỉnh:
$$y = PACT(x) = \begin{cases} -\alpha & x \in (-\infty, -\alpha) \\ x & x \in [-\alpha, \alpha] \\ \alpha & x \in [\alpha, +\infty) \end{cases}$$

#### File cấu hình direction classifier

```yaml
Architecture:
  model_type: cls
  algorithm: CLS
  Backbone:
    name: MobileNetV3
    scale: 0.35
    model_name: small
  Head:
    name: ClsHead
    class_dim: 2

Train:
  dataset:
    name: SimpleDataSet
    transforms:
      - DecodeImage
      - ClsLabelEncode
      - RecAug
      - RandAugment
      - ClsResizeImg:
          image_shape: [3, 48, 192]   # Tăng độ phân giải
```

**Tổng kết direction classifier:**

| Input Res | PACT Quant | Accuracy | Size(M) | Time(SD855 ms) |
|---|:-:|---|---|---|
| 3×32×100  |   | 0.9212 | 0.85 | 3.19 |
| 3×48×192  |   | 0.9403 | 0.85 | 3.21 |
| 3×48×192  | ✓ | **0.9456** | **0.46** | **2.38** |

Tổng kết: kích thước giảm từ **0.85M xuống 0.46M**, độ chính xác tăng >2%.

### 6.2.3 Nhận dạng văn bản

Text recognizer của PP-OCR là **CRNN** với CTC loss.

**Mục tiêu tối ưu**: backbone, head structure, data enhancement, regularization, feature map downsampling, quantization.

Bảng ablation toàn diện:

| Id | Ablation Study | ACC | Size(M) |
|:-:|---|---|---|
| 1 | baseline | — | 23 |
| 2 | + Lightweight Backbone & Head | 0.5193 | 4.6 |
| 3 | + BDA | 0.5505 | 4.6 |
| 4 | + Cosine LR | 0.5652 | 4.6 |
| 5 | + Feature Map Downsampling Strategy | 0.6179 | 4.6 |
| 6 | + Regularization | 0.6519 | 4.6 |
| 7 | + Warmup | 0.6581 | 4.6 |
| 8 | + TIA | 0.6670 | 4.6 |
| 9 | + PACT | 0.6740 | 1.5 |
| 10 | + Pretrain | **0.6900** | **1.5** |

#### Lightweight Backbone & Head

**Backbone**: vẫn dùng MobileNetV3 (giống detection). PP-OCR chọn `MobileNetV3_small_x0.5` để cân bằng.

| Backbone | Accuracy | Size(M) | Time(CPU ms) |
|---|---|---|---|
| MobileNetV3_small_x0.35 | 0.6288 | 22   | 17 |
| MobileNetV3_small_x0.5  | 0.6556 | 23   | 17.27 |
| MobileNetV3_small_x1    | 0.6933 | 28   | 19.15 |

**Head**: fully-connected layer giải mã chuỗi. Dimension của feature chuỗi rất ảnh hưởng đến model size — đặc biệt khi nhận dạng >6000 ký tự Hán. Nếu chiều = 256, head ~6.7M.

PP-OCR chọn **dimension = 48** — cân bằng:

| Channels | Accuracy | Size(M) | Time(CPU ms) |
|---|---|---|---|
| 256 | 0.6556 | 23  | 17.27 |
| 96  | 0.6673 | 8   | 13.36 |
| 64  | 0.6642 | 5.6 | 12.64 |
| 48  | 0.6581 | 4.6 | 12.26 |

#### Data Augmentation — TIA

Ngoài BDA, **TIA** (Luo et al., 2020) là một phương pháp tăng cường hiệu quả cho text recognition. TIA đặt nhiều điểm tham chiếu trong ảnh và di chuyển ngẫu nhiên các điểm qua biến đổi hình học — tăng đa dạng dữ liệu.

Thí nghiệm: TIA tăng độ chính xác text recognition **0.9%** trên baseline cao.

3 loại TIA: `tia_distort`, `tia_stretch`, `tia_perspective`.

```python
from ppocr.data.imaug.rec_img_aug import tia_distort, tia_stretch, tia_perspective
img_out1 = tia_distort(img, 2.5)
img_out2 = tia_stretch(img, 3)
img_out3 = tia_perspective(img)
```

#### Learning Rate Strategy & Regularization

- LR: Cosine + Warmup (giống detection).
- Regularization: PP-OCR dùng **L2 regularization** — L2 norm của weight được cộng vào loss. Giúp weight nhỏ hơn, giảm overfitting, cải thiện tổng quát. L2 regularization có ảnh hưởng lớn đến độ chính xác nhận dạng văn bản.

#### Feature Map Downsampling Strategy

Trong vision tasks tổng quát (classification), input thường 224×224, giảm mẫu cả width và height đồng thời.

Trong text recognition, input 32×100 (tỉ lệ khung hình cực đoan). Giảm mẫu đồng thời width+height gây mất đặc trưng nghiêm trọng.

→ Sửa **stride downsampling từ (2,2) sang (2,1)** trong các stage sau (giữ stage đầu (2,2)) — giữ nhiều thông tin hơn cho chiều cao của text.

> **Lưu ý**: nếu thay backbone, phải xem xét và điều chỉnh downsampling phù hợp.

---

*— Hết phần tóm tắt trang 100–150 —*

*Phần tiếp theo sẽ tiếp tục từ trang 151 trở đi: tham khảo Quantization, Pretrain, Enhanced CTC loss, PP-OCRv2 (CML knowledge distillation, CopyPaste augmentation, PP-LCNet, U-DML, ...).*
