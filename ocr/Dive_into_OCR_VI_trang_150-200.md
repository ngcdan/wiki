# Dive into OCR — Tóm tắt tiếng Việt (Trang 150–200)

*Tiếp nối từ file dịch trang 100–150. Phần này là **bản tóm tắt giáo dục ngắn gọn** bằng tiếng Việt, không phải bản dịch nguyên văn. Mã nguồn và chi tiết kỹ thuật đầy đủ vui lòng tham khảo repo PaddleOCR.*

> Tài liệu gốc: https://github.com/PaddlePaddle/PaddleOCR (release/2.4)
> File config liên quan: `configs/det/ch_PP-OCRv2/`, `configs/rec/ch_PP-OCRv2/`

---

## Phần còn lại Chương 6 — Tối ưu PP-OCR & PP-OCRv2

### 6.2.3 Tối ưu nhận dạng (tiếp)

**Tối ưu downsampling stride trong MobileNetV3:**

Trong text recognition, ảnh đầu vào có tỉ lệ khung hình cực đoan (32×100 hoặc 32×320). Stride downsampling tiêu chuẩn (2,2) cho cả width và height gây mất thông tin nghiêm trọng theo chiều cao. PP-OCR điều chỉnh:
- Stride đầu giữ nguyên (2,2)
- Các stride sau sửa từ (2,1) thành **(1,1)** để giữ nhiều thông tin hơn

Kết quả: feature map có cùng hình dạng đầu ra `[1, 288, 1, 80]` nhưng thông tin được bảo toàn tốt hơn trong encoding. CPU inference tăng nhẹ từ 11.84ms → 12.96ms.

**PACT Online Quantization** cho text recognizer:
- Giống direction classifier, dùng PACT để lượng tử hóa
- LSTM **không** được lượng tử hóa do phức tạp
- Kết quả: kích thước giảm 67.4%, tốc độ tăng 8%, accuracy tăng 1.6%

| PACT Quantization | Accuracy | Size (M) | Inference (SD855 ms) |
|:-:|:-:|:-:|:-:|
|   | 0.6581 | 4.6 | 12 |
| ✓ | 0.674  | 1.5 | 11 |

**Pre-training Model**: Trong PP-OCR, dữ liệu tổng hợp 10⁷ ảnh được dùng để pretrain, sau đó fine-tune trên dữ liệu thật. Accuracy tăng từ 65.81% → 69%.

**Tổng kết tối ưu nhận dạng:**
Qua tất cả chiến lược (lightweight backbone+head, BDA, Cosine LR, downsampling, regularization, warmup, TIA, PACT, pretrain), kích thước CRNN giảm từ **4.5M xuống 1.6M**, accuracy tăng **15.4%** trên tập validation.

---

## 6.3 Giải thích chiến lược tối ưu PP-OCRv2

PP-OCRv2 cải tiến 3 mặt so với PP-OCR: **backbone, data augmentation, loss function** — cùng với knowledge distillation.

### 6.3.1 Tối ưu mô hình phát hiện văn bản

Hai chiến lược chính: **CML knowledge distillation** và **CopyPaste**. Kích thước mô hình không đổi (3.0M) nhưng Hmean tăng từ 0.759 → **0.795**.

| Strategy | Precision | Recall | Hmean | Size (M) | Time (CPU ms) |
|---|---|---|---|---|---|
| PP-OCR det | 0.718 | 0.805 | 0.759 | 3.0 | 129 |
| PP-OCR det + DML | 0.743 | 0.815 | 0.777 | 3.0 | 129 |
| PP-OCR det + CML | 0.746 | 0.835 | 0.789 | 3.0 | 129 |
| PP-OCR det + CML + CopyPaste | 0.754 | 0.840 | **0.795** | 3.0 | 129 |

#### CML — Collaborative Mutual Learning

Knowledge distillation thường dùng để cải thiện model nhỏ bằng cách "học từ" model lớn. Có 3 kiểu:

- **Standard Distillation**: 1 Teacher (lớn) → 1 Student (nhỏ).
- **DML** (Deep Mutual Learning): hai Student cùng cấu trúc học từ nhau, không cần Teacher lớn.
- **CML** (Collaborative Mutual Learning) — PP-OCRv2 dùng: kết hợp cả Teacher (ResNet18_vd) và **2 Student** (MobileNetV3) cùng cấu trúc, học lẫn nhau và đồng thời chịu giám sát từ Teacher.

**Loss CML** gồm 3 thành phần:
1. **GT Loss**: 2 Student cần được giám sát bởi ground truth. Pipeline DBNet xuất 3 feature map (probability map, threshold map, binary map) với loss khác nhau:
   - Probability map → Binary cross-entropy loss (weight 1.0)
   - Binary map → Dice loss (weight α)
   - Threshold map → L1 loss (weight β)
   
   $$Loss_{gt}(T_{out}, gt) = l_p(S_{out}, gt) + \alpha l_b(S_{out}, gt) + \beta l_t(S_{out}, gt)$$

2. **DML Loss**: hai Student có output giống nhau, dùng KL divergence đối xứng:
   $$Loss_{dml} = \frac{KL(S1_{pout} \| S2_{pout}) + KL(S2_{pout} \| S1_{pout})}{2}$$

3. **Distill Loss**: Teacher giám sát Student, chỉ áp dụng cho probability map:
   $$Loss_{distill} = \gamma l_p(S_{out}, f_{dila}(T_{out})) + l_b(S_{out}, f_{dila}(T_{out}))$$

Cấu hình huấn luyện: `ch_PP-OCRv2_det_cml.yml` — định nghĩa `DistillationModel` với 3 subnet `Teacher`, `Student`, `Student2`. Teacher có `freeze_params: true` và dùng pretrained ResNet18.

#### CopyPaste — Data Augmentation

Thuật toán augmentation mới được kiểm chứng trong target detection và segmentation. CopyPaste tổng hợp các instance text để cân bằng tỷ lệ mẫu dương/âm trong ảnh huấn luyện — điều mà rotation/flip/crop thông thường không làm được.

**Các bước CopyPaste:**
1. Chọn ngẫu nhiên 2 ảnh huấn luyện
2. Random scale jittering
3. Lật ngang ngẫu nhiên
4. Chọn ngẫu nhiên một subset của ảnh thứ nhất
5. Dán vào vị trí ngẫu nhiên trong ảnh thứ hai

Kết quả: các sample đa dạng hơn, mô hình robust hơn — đặc biệt với nền văn bản đa dạng.

**Sử dụng**: thêm `CopyPaste` vào `Train.transforms` trong file config.

### 6.3.2 Tối ưu mô hình nhận dạng văn bản

3 chiến lược: **PP-LCNet backbone, U-DML knowledge distillation, Enhanced CTC loss**. Accuracy tăng từ 66.7% → **74.8%**.

| Strategy | Acc | Size (M) | Time (CPU ms) |
|---|---|---|---|
| PP-OCR rec (MV3) | 0.667 | 5.0 | 7.7 |
| PP-OCR rec (LCNet) | 0.693 | 8.0 | 6.2 |
| PP-OCR rec (LCNet) + U-DML | 0.739 | 8.6 | 6.2 |
| PP-OCR rec (LCNet) + U-DML + Enhanced CTC | **0.748** | 8.6 | 6.2 |

#### PP-LCNet — Lightweight CPU Network

Baidu đề xuất mạng CPU nhẹ dựa trên tăng tốc MKLDNN. Cải tiến từ MobileNetV1:
- Hầu hết ReLU đổi sang **h-swish** (trừ trong SE module) — accuracy +1-2%
- DepthSepConv stage 5 dùng kernel **5×5** thay vì 3×3 — +0.5-1%
- Thêm SE module ở 2 block cuối — +0.5-1%
- Thêm FC layer 1280-d sau GAP — +2-3%

Trên ImageNet1k, PP-LCNet-1.0x đạt **Top1=71.32%** với inference **3.16ms**, vượt MobileNetV3 và GhostNet ở cả độ chính xác và tốc độ.

PP-LCNet được tối ưu riêng cho kịch bản **CPU+MKLDNN**.

#### U-DML — Unified Deep Mutual Learning

DML chuẩn chỉ giám sát ở output layer. Nhưng với 2 model cùng cấu trúc, đặc trưng trung gian cũng nên giống nhau. **U-DML** thêm giám sát feature map trung gian:

3 loss thành phần:
1. **GT loss (CTC)**: $Loss_{ctc} = CTC(S_{hout}, gt) + CTC(T_{hout}, gt)$
2. **DML loss**: KL divergence đối xứng giữa output Student và Teacher
3. **Feature loss** (mới): L2 loss giữa feature map của Student và Teacher
   $$Loss_{feat} = L2(S_{bout}, T_{bout})$$

Tổng: $Loss_{total} = Loss_{ctc} + Loss_{dml} + Loss_{feat}$

Cấu hình huấn luyện: `ch_PP-OCRv2_rec_distillation.yml` — định nghĩa Teacher, Student, Student2 với cùng cấu trúc MobileNetV1Enhance + SequenceEncoder + CTCHead.

#### Enhanced CTC Loss

Trong nhận dạng tiếng Trung, nhiều ký tự tương tự dễ bị nhầm. Lấy cảm hứng từ Metric Learning, PP-OCRv2 thêm **Center loss** để tăng khoảng cách giữa các lớp:

$$L = L_{ctc} + \lambda L_{center}$$
$$L_{center} = \sum_{t=1}^{T} \|x_t - c_{y_t}\|_2^2$$

Trong đó $x_t$ là feature tại bước $t$, $c_{y_t}$ là center của lớp $y_t$.

**Khởi tạo center quan trọng**: PP-OCRv2 dùng quy trình:
1. Huấn luyện mạng baseline với CTC loss chuẩn
2. Trích ảnh dự đoán đúng → tập G
3. Đưa từng ảnh G qua mạng, tính $y_t = \arg\max(W \cdot x_t)$
4. Tổng hợp $x_t$ theo $y_t$, trung bình → center khởi tạo

**Config Loss** (`ch_PP-OCRv2_rec_enhanced_ctc_loss.yml`):
```yaml
Loss:
  name: CombinedLoss
  loss_config_list:
    - CTCLoss:
        weight: 1.0
    - CenterLoss:
        weight: 0.05
        num_classes: 6625
        feat_dim: 96
        center_file_path: "./train_center.pkl"
```

### 6.4 Tổng kết Chương 6

PP-OCR dùng 19 chiến lược ở backbone, learning rate, augmentation, model tailoring, quantization để xây dựng phiên bản server và mobile.

PP-OCRv2 cải tiến thêm: backbone (PP-LCNet), augmentation (CopyPaste), loss (Enhanced CTC), và knowledge distillation (CML, U-DML) — vượt PP-OCR cả về accuracy và speed.

---

# CHƯƠNG 7 — SUY LUẬN VÀ TRIỂN KHAI PP-OCRv2

## 7.1 Tổng quan

Chương này giới thiệu suy luận hiệu năng cao, triển khai dịch vụ và triển khai trên thiết bị di động của PP-OCRv2. Bạn sẽ học:
- Chọn phương pháp triển khai phù hợp cho từng kịch bản
- Suy luận PP-OCRv2 trong nhiều tình huống
- Triển khai qua **Paddle Inference**, **Paddle Serving**, **Paddle Lite**

### 7.1.1 Giới thiệu

Sau khi huấn luyện, để dự đoán cần định nghĩa mạng, tải mô hình, tiền xử lý dữ liệu, suy luận, hậu xử lý — tiện cho debug nhưng hiệu suất thấp.

Có 2 giải pháp suy luận offline:

| Đặc điểm | Inference dựa training engine | Inference dựa inference engine |
|---|---|---|
| Đặc trưng | Dùng cùng engine với training; cần định nghĩa lại network; phù hợp tích hợp hệ thống | Cần chuyển đổi model, loại phần không cần thiết; **không cần định nghĩa network**; tích hợp hệ thống tốt |
| Ngôn ngữ | Python | Python hoặc C++ |
| Bước suy luận | Định nghĩa cấu trúc Python → chuẩn bị input → tải model → suy luận | Chuẩn bị input → tải model structure + parameters → suy luận |

Trong triển khai offline, nên dùng inference engine. PaddlePaddle có 5 phương án:

| Triển khai | Đặc trưng | Kịch bản | Phần cứng |
|---|---|---|---|
| **Paddle Inference** | General, hiệu năng cao | Thuật toán phức tạp | x86 CPU, NVIDIA GPU, Kunlun/Ascend |
| **Paddle Lite** | Nhẹ | Mô hình nhẹ, phần cứng hạn chế | ARM CPU/GPU, Kirin/Rockchip... |
| **Paddle Serving** | Đồng thời cao | Lưu lượng lớn, latency thấp | x86/ARM CPU, NVIDIA GPU |
| **Paddle.js** | Suy luận trên trình duyệt | Web | Chrome/Safari/Firefox |
| **Paddle2ONNX** | Mở, tương thích | Triển khai trên chip AI khác | Horizon X3, các chip AI khác |

PaddleOCR cung cấp 3 phương án chính:
- **Offline Inference (Paddle Inference)**: ưu tiên khi không cần real-time cao — số hóa tài liệu, trích xuất quảng cáo. Không có độ trễ mạng, hiệu suất tốt, an toàn dữ liệu.
- **Service Deployment (Paddle Serving)**: cần real-time cao — OCR thương mại, dịch ảnh thời gian thực. Có chi phí mạng, dùng GPU kém hiệu quả, rủi ro an ninh.
- **Mobile Deployment (Paddle Lite)**: triển khai trên di động/robot. Nhạy cảm với kích thước mô hình, hiệu suất hạn chế.

### 7.1.2 Chuẩn bị môi trường

```bash
git clone https://gitee.com/paddlepaddle/PaddleOCR.git
cd PaddleOCR
pip install -U pip
pip install -r requirements.txt
pip install paddlenlp==2.2.1  # cho VQA tasks
```

## 7.2 Suy luận Python với Paddle Inference

**Paddle Inference** là thư viện suy luận native của PaddlePaddle, hoạt động trên server/cloud cho hiệu năng cao. Hỗ trợ mọi model do PaddlePaddle huấn luyện. Đã được tối ưu sâu cho nhiều platform.

**Quy trình suy luận 6 bước:**
1. Chuẩn bị dữ liệu và môi trường
2. Export model suy luận
3. Khởi tạo inference engine
4. Tiền xử lý dữ liệu
5. Suy luận
6. Hậu xử lý

PP-OCRv2 có 3 model: **text detection**, **direction classifier**, **text recognition** — mỗi cái có quy trình suy luận riêng.

### 7.2.2 Suy luận model phát hiện văn bản

Tham số quan trọng:
- `image_dir`: đường dẫn ảnh/thư mục ảnh
- `det_model_dir`: đường dẫn model phát hiện

```bash
# Tải model
cd inference && wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_det_infer.tar
tar -xf ch_PP-OCRv2_det_infer.tar
```

Model có 3 file: `inference.pdiparams` (2.2M), `inference.pdiparams.info`, `inference.pdmodel` (845K).

**Export model đã train sang dạng inference**:
```bash
python tools/export_model.py -c configs/det/ch_PP-OCRv2/ch_PP-OCRv2_det_cml.yml \
  -o Global.pretrained_model="ch_PP-OCRv2_det_distill_train/best_accuracy" \
     Global.save_inference_dir="./my_model"
```

Model PP-OCRv2 distillation có 3 sub-networks (Teacher, Student, Student2) — khi export, chỉ Student1 được dùng cho inference.

**Suy luận**:
```bash
python tools/infer/predict_det.py \
  --image_dir="./doc/imgs/00018069.jpg" \
  --det_model_dir="./inference/ch_PP-OCRv2_det_infer" \
  --use_gpu=False
```

**TextDetector class** (`tools/infer/predict_det.py`):
- `__init__`: thiết lập preprocessing (`DetResizeForTest`, `NormalizeImage`, `ToCHWImage`, `KeepKeys`), postprocessing (`DBPostProcess` với `thresh`, `box_thresh`, `unclip_ratio`...)
- `order_points_clockwise`: sắp xếp 4 điểm theo chiều kim đồng hồ
- `clip_det_res`: giới hạn điểm trong biên ảnh
- `filter_tag_det_res`: loại bỏ kết quả nhỏ (<3 pixel)
- `__call__`: tiền xử lý → copy data sang inference engine → predict → copy về CPU → hậu xử lý

Tham số dòng lệnh quan trọng (`tools/infer/utility.py`):
- Detection: `det_algorithm` (DB/EAST/SAST), `det_db_thresh=0.3`, `det_db_box_thresh=0.6`, `det_db_unclip_ratio=1.5`, `use_dilation`, `det_db_score_mode`
- Recognition: `rec_algorithm=CRNN`, `rec_image_shape="3,32,320"`, `rec_char_dict_path`, `use_space_char`, `max_text_length=25`
- Classifier: `use_angle_cls`, `cls_image_shape="3,48,192"`, `cls_thresh=0.9`, `label_list=['0','180']`
- Tăng tốc: `use_gpu`, `use_tensorrt`, `enable_mkldnn`, `cpu_threads`
- Multi-process: `use_mp`, `total_process_num`

### 7.2.3 Suy luận Direction Classifier

```bash
cd inference && wget https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar
tar -xf ch_ppocr_mobile_v2.0_cls_infer.tar

python tools/infer/predict_cls.py \
  --image_dir="./doc/imgs_words/ch/word_1.jpg" \
  --cls_model_dir="./inference/ch_ppocr_mobile_v2.0_cls_infer" \
  --use_gpu=False
```

**TextClassifier class**:
- `resize_norm_img`: scale về `cls_image_shape` (3, 48, 192) và chuẩn hóa
- `__call__`: batch hóa theo aspect ratio để tăng tốc → predict → nếu label='180' với score > cls_thresh thì xoay ảnh 180°

Output: `Predicts of word_1.jpg: ['0', 0.9998784]` — hướng 0° với độ tin cậy 99.98%.

### 7.2.4 Suy luận Text Recognition

```bash
cd inference && wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_rec_infer.tar
tar -xf ch_PP-OCRv2_rec_infer.tar

python tools/infer/predict_rec.py \
  --image_dir="./doc/imgs_words/ch/word_4.jpg" \
  --rec_model_dir="./inference/ch_PP-OCRv2_rec_infer" \
  --use_gpu=False
```

**TextRecognizer class**:
- `resize_norm_img`: scale theo `max_wh_ratio` để batch — width động `int(32 * max_wh_ratio)`
- `__call__`: 
  - Sắp xếp ảnh theo aspect ratio (tăng tốc batch)
  - Batch hóa, tính max_wh_ratio cho mỗi batch
  - Preprocess → inference → CTCLabelDecode hậu xử lý

Output: `Predicts of word_4.jpg: ('实力活力', 0.9409585)`.

### 7.2.5 End-to-end Inference PP-OCRv2

Gọi cả 3 module qua tham số:
- `image_dir`: ảnh đầu vào
- `det_model_dir`, `cls_model_dir`, `rec_model_dir`: 3 model
- `use_angle_cls`: bật direction classifier
- `use_mp`, `total_process_num`: multi-process

Ví dụ với ảnh tài liệu y tế tiếng Trung — output là toàn bộ vùng văn bản đã phát hiện kèm nội dung nhận dạng.

---

*— Hết phần tóm tắt trang 150–200 —*

Phần tiếp theo (trang 200+) sẽ tiếp tục với:
- 7.2.6 Suy luận WHL Package
- 7.3 Suy luận C++ Paddle Inference
- 7.4 Triển khai dịch vụ Paddle Serving
- 7.5 Triển khai end-to-side Paddle Lite
- Chương 8 — Phân tích tài liệu (Layout Analysis, Table Recognition, DocVQA)

**Tài nguyên:**
- Repo: https://github.com/PaddlePaddle/PaddleOCR
- Tutorial inference: PaddleOCR/doc/doc_ch/inference.md
- Tutorial deployment: PaddleOCR/deploy/
