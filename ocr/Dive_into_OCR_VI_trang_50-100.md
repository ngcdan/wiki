# Dive into OCR — Bản dịch tiếng Việt (Trang 50–100)

*Tiếp nối từ file dịch trang 10–50. Phần này tập trung vào Chương 4 (Thực hành DBNet) và mở đầu Chương 5 (Nhận dạng văn bản).*

> Lưu ý: Phần lớn các đoạn mã trong khu vực này tham chiếu trực tiếp tới mã nguồn mở của PaddleOCR. Bản dịch này tóm tắt ý nghĩa và mục đích của mã, kèm theo đường dẫn tới repo gốc. Bạn đọc nên xem mã đầy đủ tại: https://github.com/PaddlePaddle/PaddleOCR

---

## (Trang 50–52) Tiếp tục 4.2.1 — Bắt đầu nhanh với DBNet

Khi gọi `paddleocr` lần đầu, công cụ sẽ tự động tải về mô hình PP-OCRv2 nhẹ và chạy phát hiện văn bản trên ảnh đầu vào. Có hai cách sử dụng:

**Cách 1 — qua dòng lệnh:**

```bash
# `--image_dir` chỉ đường dẫn ảnh cần dự đoán
# `--rec false` nghĩa là không nhận dạng, chỉ phát hiện văn bản
!paddleocr --image_dir ./12.jpg --rec false
```

Kết quả in ra danh sách tọa độ các hộp văn bản.

**Cách 2 — qua mã Python:**

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR()
img_path = './12.jpg'
result = ocr.ocr(img_path, rec=False)
print(f"Các hộp văn bản dự đoán của {img_path}:")
print(result)
```

**Trực quan hóa kết quả phát hiện**: dùng `cv2.polylines` để vẽ các đa giác lên ảnh gốc, sau đó hiển thị bằng `matplotlib`.

---

## 4.2.2 Triển khai chi tiết thuật toán DB

### Nguyên lý thuật toán DB

**DB** (Differentiable Binarization) là một thuật toán phát hiện văn bản **dựa trên phân đoạn**, sử dụng module nhị phân hóa khả vi (DB module) để phân biệt vùng văn bản và nền bằng một ngưỡng động.

*Hình 2: So sánh giữa DB và các phương pháp truyền thống*

- **Pipeline truyền thống (mũi tên xanh)**: dùng ngưỡng cố định để nhị phân hóa bản đồ phân đoạn, sau đó dùng hậu xử lý heuristic (như phân cụm pixel) để có vùng văn bản.
- **Pipeline DB (mũi tên đỏ)**: có **bản đồ ngưỡng (threshold map)** dự đoán ngưỡng tại mỗi điểm pixel của ảnh thông qua mạng nơ-ron, thay vì chỉ định một giá trị cố định. Nhờ vậy phân biệt nền và tiền cảnh tốt hơn.

**Ưu điểm của DB:**
1. Cấu trúc đơn giản, không cần hậu xử lý rườm rà.
2. Dữ liệu mã nguồn mở cho độ chính xác và hiệu năng tốt.

Sau khi có bản đồ xác suất, thuật toán phân đoạn truyền thống đặt giá trị 0 cho pixel dưới ngưỡng `t` và 1 cho phần còn lại:

$$B_{i,j} = \begin{cases} 1, & \text{nếu } P_{i,j} \geq t \\ 0, & \text{ngược lại} \end{cases}$$

Tuy nhiên, hàm nhị phân hóa tiêu chuẩn không khả vi nên không thể huấn luyện end-to-end. Để giải quyết, DB dùng **Nhị phân hóa khả vi** xấp xỉ hàm bậc thang:

$$\hat{B} = \frac{1}{1 + e^{-k(P_{i,j} - T_{i,j})}}$$

Trong đó: P là bản đồ xác suất, T là bản đồ ngưỡng, và k là hệ số khuếch đại (thường đặt k=50).

Khi dùng cross-entropy loss, mất mát cho mẫu dương ($l_+$) và mẫu âm ($l_-$):

$$l_+ = -\log\left(\frac{1}{1+e^{-k(P_{i,j}-T_{i,j})}}\right)$$
$$l_- = -\log\left(1 - \frac{1}{1+e^{-k(P_{i,j}-T_{i,j})}}\right)$$

Đạo hàm riêng theo x cho thấy: **hệ số khuếch đại k phóng đại gradient của dự đoán sai**, qua đó tối ưu hóa mô hình tốt hơn. Hình 2(b) cho trường hợp x<0 (mẫu dương bị dự đoán thành mẫu âm) — gradient được phóng đại. Hình 2(c) cho x>0 (mẫu âm bị dự đoán thành dương) — gradient cũng được phóng đại.

*Hình 3: Sơ đồ thuật toán DB — so sánh đường cong giữa DB và Standard Binarization (SB) với k=1 và k=50*

### Cấu trúc mạng của DB

Đặc trưng ảnh đầu vào được trích qua **Backbone** và **FPN**, sau đó nối lại để được đặc trưng có kích thước bằng 1/4 ảnh gốc. Tiếp đến, các tầng tích chập tính ra **bản đồ xác suất** và **bản đồ ngưỡng**, rồi qua hậu xử lý DB để thu được đường viền văn bản.

*Hình 4: Sơ đồ cấu trúc mạng DB — qua các tầng 1/2, 1/4, 1/8, 1/16, 1/32 với element-wise sum và up-sampling*

### Xây dựng mô hình DB

Mô hình DB gồm ba phần:
- **Backbone** để trích đặc trưng ảnh
- **FPN (Feature Pyramid Network)** để tăng cường đặc trưng
- **Head** để tính bản đồ xác suất vùng văn bản

#### Backbone

Mạng phân loại ảnh được dùng làm backbone. Bài báo gốc dùng ResNet50, nhưng trong thực hành sách dùng **MobileNetV3 Large** để huấn luyện nhanh hơn.

```python
# Tham khảo:
# https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.4/ppocr/modeling/backbones/det_mobilenet_v3.py
from ppocr.modeling.backbones.det_mobilenet_v3 import MobileNetV3
```

Giả sử kích thước đầu vào là [640, 640], đầu ra của backbone có 4 đặc trưng với hình dạng: `[1, 16, 160, 160]`, `[1, 24, 80, 80]`, `[1, 56, 40, 40]`, `[1, 480, 20, 20]`. Các đặc trưng này được đưa vào FPN.

#### FPN (Feature Pyramid Network)

FPN được dùng để trích xuất hiệu quả đặc trưng ở mỗi cấp độ. Lớp DBFPN trong PaddleOCR thực hiện:
1. Giảm số kênh của c2, c3, c4, c5 (đầu ra backbone)
2. Up-sample và cộng với đặc trưng cấp dưới
3. Convolution và up-sample tiếp để tất cả về cùng kích thước
4. Concatenate cả 4 mức thành một đặc trưng duy nhất

Đầu vào FPN là đầu ra backbone, đầu ra FPN có chiều cao và rộng bằng 1/4 ảnh gốc. Với ảnh [1, 3, 640, 640], đặc trưng FPN có kích thước [160, 160].

```python
from ppocr.modeling.necks.db_fpn import DBFPN
model_fpn = DBFPN(in_channels=in_channels, out_channels=256)
```

#### Head

Lớp DBHead tính các bản đồ: xác suất vùng văn bản, ngưỡng vùng văn bản, và bản đồ nhị phân — qua công thức Differentiable Binarization.

```python
class DBHead(nn.Layer):
    def step_function(self, x, y):
        # Hàm nhị phân khả vi: tính bản đồ phân đoạn từ probability map và threshold map
        return paddle.reciprocal(1 + paddle.exp(-self.k * (x - y)))
```

DB Head sẽ up-sampling dựa trên đặc trưng FPN, đưa kích thước từ 1/4 về bằng ảnh gốc.

---

## 4.2.3 Huấn luyện mô hình DB

DBNet trên PaddleOCR có sẵn 2 backbone: **MobileNetV3** và **ResNet50_vd**. Bạn chọn file cấu hình và bắt đầu huấn luyện theo nhu cầu.

Phần này dùng mô hình DB với backbone MobileNetV3 (cấu hình của mô hình siêu nhẹ) trên tập dữ liệu **ICDAR2015** làm ví dụ.

### Chuẩn bị dữ liệu

Thí nghiệm chọn **ICDAR2015** — tập dữ liệu nổi tiếng và phổ biến nhất trong phát hiện và nhận dạng văn bản cảnh thực.

*Hình 5: Sơ đồ tập dữ liệu ICDAR2015 — các ảnh chụp biển hiệu, siêu thị, hành lang...*

Tập dữ liệu đã được tải sẵn trong dự án `/home/aistudio/data/data96799`. Giải nén bằng:

```bash
!cd ~/data/data96799/ && tar xf icdar2015.tar
```

Cấu trúc thư mục sau khi giải nén:

```
~/train_data/icdar2015/text_localization
├── icdar_c4_train_imgs/        # dữ liệu huấn luyện
├── ch4_test_images/            # dữ liệu test
├── train_icdar2015_label.txt   # nhãn huấn luyện
└── test_icdar2015_label.txt    # nhãn test
```

**Định dạng nhãn:**
```
Image file name [json.dumps encoded image label information]
ch4_test_images/img_61.jpg [{"transcription": "MASA", "points": [[310,104], [416,141], [418,216], [312,179]]}, ...]
```

Trường `points` là tọa độ (x, y) của 4 điểm hộp văn bản, sắp xếp theo chiều kim đồng hồ từ trên trái. Trường `transcription` là nội dung văn bản — không cần cho phát hiện. Nếu nhãn là `*` hoặc `###` nghĩa là bỏ qua nhãn đó.

### Tiền xử lý dữ liệu

Trong huấn luyện, ảnh đầu vào cần đáp ứng các yêu cầu về định dạng và kích thước; đồng thời cần lấy được nhãn thật của bản đồ ngưỡng và bản đồ xác suất từ thông tin nhãn. Vì vậy, dữ liệu cần được tiền xử lý. Ngoài ra, để mở rộng dữ liệu, chống overfitting và cải thiện khả năng tổng quát, thí nghiệm dùng vài phương pháp tăng cường dữ liệu cơ bản.

Các bước tiền xử lý gồm:
- **Giải mã ảnh (Image decoding)**: chuyển ảnh sang định dạng Numpy
- **Mã hóa nhãn (Label encoding)**: phân tích thông tin nhãn từ file txt và lưu định dạng thống nhất
- **Tăng cường dữ liệu cơ bản**: lật ngang, xoay, zoom, cắt ngẫu nhiên, v.v.
- **Lấy nhãn bản đồ ngưỡng**: thông qua mở rộng (expansion)
- **Lấy nhãn bản đồ xác suất**: thông qua thu nhỏ (shrinking)
- **Chuẩn hóa (Normalization)**: đưa phân phối đầu vào về phân phối chuẩn (mean=0, var=1)
- **Biến đổi kênh**: từ định dạng [H, W, C] sang [C, H, W] để phù hợp với mạng

**Image Decoding (DecodeImage)**: lớp đọc ảnh từ buffer bằng `cv2.imdecode`, chuyển sang RGB nếu cần, và đặt vào dictionary `data['image']`.

**Label Decoding (DetLabelEncode)**: phân tích JSON nhãn, lấy hộp văn bản (`polys`), nội dung văn bản (`texts`), và `ignore_tags` (đánh dấu nhãn bị bỏ qua khi text là `*` hoặc `###`).

```python
from ppocr.data.imaug.label_ops import DetLabelEncode
decode_label = DetLabelEncode()
data = decode_label(data)
# data['polys'], data['texts'], data['ignore_tags']
```

**Lấy nhãn bản đồ ngưỡng (MakeBorderMap)**: tính nhãn bản đồ ngưỡng thông qua mở rộng đa giác văn bản. Lớp này dùng `pyclipper` để offset đa giác và tạo ra mặt nạ ngưỡng.

```python
from ppocr.data.imaug.make_border_map import MakeBorderMap
generate_text_border = MakeBorderMap()
data = generate_text_border(data)
# data['threshold_map'], data['threshold_mask']
```

**Lấy nhãn bản đồ xác suất (MakeShrinkMap)**: tính nhãn bản đồ xác suất qua thu nhỏ đa giác. Vùng văn bản thu nhỏ sẽ trở thành nhãn dương (1), phần còn lại là âm (0).

```python
from ppocr.data.imaug.make_shrink_map import MakeShrinkMap
generate_shrink_map = MakeShrinkMap()
data = generate_shrink_map(data)
# data['shrink_map'], data['shrink_mask']
```

**Normalization (NormalizeImage)**: chuẩn hóa với mean `[0.485, 0.456, 0.406]` và std `[0.229, 0.224, 0.225]` (theo chuẩn ImageNet).

**Channel Transformation (ToCHWImage)**: chuyển HWC → CHW bằng `img.transpose((2, 0, 1))`.

### Xây dựng Dataloader

Trong huấn luyện thực tế, dữ liệu được đọc và xử lý theo batch. Phần này dùng API `Dataset` và `DataLoader` của Paddle để xây dataloader.

Lớp `SimpleDataSet` đọc danh sách file nhãn, shuffle dữ liệu (chỉ khi train), và trả về mỗi sample qua `__getitem__`. Hàm `transform` áp dụng tuần tự các phép tiền xử lý đã định nghĩa.

```python
from paddle.io import Dataset, DataLoader, BatchSampler, DistributedBatchSampler

def build_dataloader(mode, label_file, data_dir, batch_size, drop_last,
                    shuffle, num_workers, seed=None):
    dataset = SimpleDataSet(mode, label_file, data_dir, seed)
    batch_sampler = BatchSampler(dataset=dataset, batch_size=batch_size,
                                  shuffle=shuffle, drop_last=drop_last)
    data_loader = DataLoader(dataset=dataset, batch_sampler=batch_sampler,
                              num_workers=num_workers, return_list=True,
                              use_shared_memory=False)
    return data_loader

train_dataloader = build_dataloader('Train', train_data_label, ic15_data_path,
                                     batch_size=8, drop_last=False,
                                     shuffle=True, num_workers=0)
eval_dataloader  = build_dataloader('Eval', eval_data_label, ic15_data_path,
                                     batch_size=1, drop_last=False,
                                     shuffle=False, num_workers=0)
```

### Hậu xử lý DB (DB Post-processing)

Đầu ra của DB head có cùng kích thước với ảnh gốc. Thực ra, ba kênh đầu ra là **bản đồ xác suất**, **bản đồ ngưỡng** và **bản đồ nhị phân**.

- Khi huấn luyện: cả ba bản đồ và nhãn thật được dùng để tính loss và huấn luyện mô hình.
- Khi suy luận: chỉ cần bản đồ xác suất. Hàm `DBPostProcess` tính tọa độ hộp văn bản từ phản hồi của vùng văn bản trong bản đồ xác suất.

Vì bản đồ xác suất là kết quả thu nhỏ, hậu xử lý sẽ **mở rộng** vùng đa giác dự đoán cùng hệ số offset để có hộp văn bản.

```python
class DBPostProcess(object):
    def __init__(self, thresh=0.3, box_thresh=0.7, max_candidates=1000,
                 unclip_ratio=2.0, use_dilation=False, score_mode="fast"):
        ...
    def __call__(self, outs_dict, shape_list):
        pred = outs_dict['maps'][:, 0, :, :]
        segmentation = pred > self.thresh  # nhị phân hóa theo ngưỡng
        # với mỗi batch, dùng boxes_from_bitmap để tính hộp văn bản
```

**4 tham số quan trọng của hậu xử lý DB:**
- `thresh`: ngưỡng nhị phân hóa bản đồ phân đoạn (mặc định 0.3)
- `box_thresh`: ngưỡng lọc hộp; hộp dưới ngưỡng này sẽ bị loại
- `unclip_ratio`: tỉ lệ phóng to hộp văn bản
- `max_candidates`: số hộp tối đa (mặc định 1000)

**Trực quan hóa**: kết quả phát hiện cho thấy mỗi từ được bao quanh bởi một hộp xanh. Có thể chỉnh `unclip_ratio` lớn hơn (ví dụ 4.0 thay vì 1.5) để hộp văn bản lớn hơn.

### Định nghĩa hàm mất mát (Loss Function)

Vì huấn luyện cho ra ba bản đồ, hàm mất mát tổng hợp ba phần:

$$L = L_b + \alpha \times L_s + \beta \times L_t$$

Trong đó:
- $L_s$ là **Dice Loss** với OHEM (mất mát của bản đồ xác suất)
- $L_t$ là **MaskL1 Loss** — khoảng cách L1 giữa bản đồ ngưỡng dự đoán và nhãn
- $L_b$ là Dice Loss của bản đồ nhị phân văn bản
- $\alpha = 5$, $\beta = 10$ là hệ số trọng số

**Định nghĩa các loss thành phần:**

- **Dice Loss**: so sánh độ tương đồng giữa ảnh nhị phân văn bản dự đoán và nhãn:
$$dice\_loss = 1 - \frac{2 \times intersection\_area}{total\_area}$$
- **Dice Loss (OHEM)**: dùng OHEM để cải thiện sự mất cân bằng giữa mẫu dương và âm. OHEM tự động chọn mẫu khó. Tỉ lệ lấy mẫu dương:âm là 1:3.
- **MaskL1 Loss**: khoảng cách L1 giữa bản đồ ngưỡng dự đoán và nhãn.

```python
class DBLoss(nn.Layer):
    def __init__(self, balance_loss=True, main_loss_type='DiceLoss',
                 alpha=5, beta=10, ohem_ratio=3, eps=1e-6):
        ...
        self.dice_loss = DiceLoss(eps=eps)
        self.l1_loss   = MaskL1Loss(eps=eps)
        self.bce_loss  = BalanceLoss(balance_loss=balance_loss,
                                     main_loss_type=main_loss_type,
                                     negative_ratio=ohem_ratio)

    def forward(self, predicts, labels):
        # predicts['maps'] có 3 kênh: shrink_maps, threshold_maps, binary_maps
        loss_shrink_maps    = self.bce_loss(...)   # cho bản đồ xác suất
        loss_threshold_maps = self.l1_loss(...)    # cho bản đồ ngưỡng
        loss_binary_maps    = self.dice_loss(...)  # cho bản đồ nhị phân
        loss_all = self.alpha * loss_shrink_maps \
                 + self.beta  * loss_threshold_maps \
                 + loss_binary_maps
        return {'loss': loss_all, ...}
```

### Đánh giá chỉ số (Index Evaluation)

Phương pháp tính IoU đơn giản dùng cho đánh giá. Có 3 chỉ số: **Precision**, **Recall**, **Hmean**.

**Logic tính:**
1. Tạo ma trận `iouMat[n,m]`, n là số hộp GT, m là số hộp phát hiện.
2. Đếm IoU > 0.5 chia cho n → **Recall**
3. Đếm IoU > 0.5 chia cho m → **Precision**
4. **Hmean = F1-score:**
$$Hmean = 2.0 \times \frac{Precision \times Recall}{Precision + Recall}$$

**Câu hỏi đặt ra**: nếu IoU GT–hộp dự đoán > 0.5 nhưng vẫn có một số văn bản chưa được phát hiện, chỉ số này có phản ánh chính xác độ chính xác mô hình không? Khi gặp tình huống này, làm sao tối ưu mô hình?

*Hình 6: Ví dụ nhãn GT box và inference box*

### Huấn luyện mô hình

Sau khi xử lý dữ liệu, định nghĩa mạng và hàm loss, ta có thể bắt đầu huấn luyện. Huấn luyện dựa trên cấu hình tham số dạng YAML:

```yaml
Architecture:
  model_type: det
  algorithm: DB
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: DBFPN
    out_channels: 256
  Head:
    name: DBHead
    k: 50

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    learning_rate: 0.001
  regularizer:
    name: 'L2'
    factor: 0

PostProcess:
  name: DBPostProcess
  thresh: 0.3
  box_thresh: 0.6
  max_candidates: 1000
  unclip_ratio: 1.5
```

File cấu hình đầy đủ: `det_mv3_db.yml`.

**Chạy huấn luyện:**

```bash
!mkdir train_data
!cd train_data && ln -s /home/aistudio/data/data96799/icdar2015 icdar2015
!wget -P ./pretrain_models/ \
  https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/MobileNetV3_large_x0_5_pretrained.pdparams
!python tools/train.py -c configs/det/det_mv3_db.yml
```

Mô hình sau huấn luyện lưu trong `PaddleOCR/output/db_mv3/` (có thể chỉnh `Global.save_model_dir`).

### Đánh giá mô hình

Trong huấn luyện, mô hình lưu 2 file mặc định: `latest` (mới nhất) và `best_accuracy` (chính xác nhất). Đánh giá trên test set:

```bash
!python tools/eval.py -c configs/det/det_mv3_db.yml \
  -o Global.checkpoints=./output/db_mv3/best_accuracy
```

### Suy luận mô hình

Sau huấn luyện, có thể chạy suy luận trên ảnh:

```bash
!python tools/infer_det.py -c configs/det/det_mv3_db.yml \
  -o Global.checkpoints=./pretrain_models/det_mv3_db_v2.0_train/best_accuracy \
     Global.infer_img=./doc/imgs_en/img_12.jpg
```

Ảnh dự đoán lưu trong `./output/det_db/det_results/`.

---

## 4.2.4 Hỏi đáp về phát hiện văn bản (FAQ)

Phần này tổng hợp các vấn đề thường gặp khi dùng mô hình phát hiện văn bản của PaddleOCR.

### Hỏi đáp về huấn luyện mô hình

**1.1 PaddleOCR cung cấp những thuật toán phát hiện văn bản nào?**
A: PaddleOCR có nhiều mô hình: phương pháp dựa trên hồi quy (EAST, SAST), phương pháp dựa trên phân đoạn (DB, PSENet).

**1.2 Cấu hình của các mô hình siêu nhẹ tiếng Trung trong PaddleOCR?**
A: Với mô hình DB siêu nhẹ, dữ liệu huấn luyện gồm các tập mã nguồn mở: lsvt, rctw, CASIA, CCPD, MSRA, MLT, BornDigit, iflytek, SROIE và dữ liệu tổng hợp — tổng 10W (100K) ảnh, chia 5 phần. Huấn luyện 500 epochs trên 4 V100 GPU, mất 3 ngày.

**1.3 Định dạng nhãn huấn luyện phát hiện văn bản là gì? `###` nghĩa là gì?**
A: Chỉ cần tọa độ vùng văn bản, có thể là 4 hoặc 14 điểm, theo thứ tự trên-trái, trên-phải, dưới-phải, dưới-trái. Với văn bản không rõ, dùng `###` để bỏ qua.

**1.4 Kết quả huấn luyện kém khi văn bản dày đặc?**
A: Với phương pháp dựa trên phân đoạn (như DB), hãy giảm batch data cho `shrink_ratio` trong huấn luyện. Khi suy luận, có thể giảm `unclip_ratio`; giá trị càng lớn, hộp phát hiện càng to.

**1.5 Với tài liệu kích thước lớn, DB có xu hướng bỏ sót văn bản. Tránh thế nào?**
A: Đầu tiên xem có phải do huấn luyện hoặc dự đoán. Nếu mô hình chưa tốt, thêm dữ liệu hoặc tăng cường dữ liệu mạnh hơn. Nếu do ảnh dự đoán quá to, tăng `det_limit_side_len` (mặc định 960). Quan sát kết quả đã phân đoạn để biết có phân đoạn không. Nếu có phân đoạn đầy đủ mà bị bỏ sót — do hậu xử lý — điều chỉnh tham số `DBPostProcess`.

**1.6 Xử lý bỏ sót văn bản cong khi dùng DB?**
A: Tính điểm trung bình của hộp văn bản trong DB hậu xử lý theo diện tích hình chữ nhật dễ bỏ sót văn bản cong. Tính điểm trung bình theo diện tích đa giác sẽ chính xác hơn nhưng chậm hơn. Đặt `det_db_score_mode` thành `slow` (chế độ đa giác) thay vì `fast` (chế độ hình chữ nhật mặc định).

**1.7 Cần bao nhiêu dữ liệu cho OCR đơn giản, yêu cầu chính xác thấp?**
A: (1) Lượng dữ liệu tùy độ phức tạp; càng phức tạp càng cần nhiều. (2) Phát hiện: 500 ảnh là đủ chuẩn cơ bản. Nhận dạng: đảm bảo mỗi ký tự trong từ điển xuất hiện ít nhất 200 lần; với 5 ký tự cần 200–1000 ảnh.

**1.8 Cách lấy thêm dữ liệu khi dữ liệu huấn luyện ít?**
A: 3 cách: (1) Thu thập dữ liệu thật thêm (hiệu quả nhất). (2) Xử lý ảnh cơ bản với PIL/OpenCV — viết chữ lên nền bằng ImageFont, xoay, biến đổi affine, lọc Gaussian. (3) Tổng hợp dữ liệu bằng thuật toán như pix2pix.

**1.9 Cách thay backbone của phát hiện/nhận dạng?**
A: Cả phát hiện và nhận dạng, lựa chọn backbone là sự đánh đổi giữa hiệu quả và tốc độ. Backbone lớn (ResNet101_vd) cho độ chính xác cao nhưng chậm hơn. Backbone nhỏ (MobileNetV3_small_x0_35) nhanh nhưng kém chính xác. **PaddleClas** có 23 series backbone (ResNet_vd, Res2Net, HRNet, MobileNetV3, GhostNet, ...) với 117 mô hình tiền huấn luyện và benchmark sẵn.

(1) Thay backbone phát hiện văn bản: chủ yếu xác định 4 stage tương tự ResNet để dễ tích hợp với FPN. Khởi tạo từ ImageNet giúp hội tụ nhanh hơn.

(2) Thay backbone nhận dạng: chú ý tỉ lệ giảm width/height; với văn bản, tỉ lệ giảm height nên nhỏ hơn width.

**1.10 Cách fine-tune mô hình phát hiện, ví dụ đóng băng tầng trước hoặc dùng learning rate nhỏ cho một số tầng?**
A: Đóng băng: đặt `stop_gradient=True` cho biến. Learning rate khác nhau: đặt fixed learning rate cho weight attribute khi khởi tạo. Thực ra, fine-tuning trực tiếp mà không chỉnh learning rate riêng cũng khả thi.

**1.11 Tại sao kích thước ảnh DB phải là bội của 32?**
A: Liên quan đến stride giảm mẫu của mạng. Với ResNet backbone, ảnh bị giảm 2 lần qua 5 stage, tổng cộng 32 lần. Vậy nên kích thước nên là bội số của 32.

**1.12 Tại sao trong PP-OCR backbone của phát hiện văn bản không dùng SEBlock?**
A: Module SE quan trọng trong MobileNetV3. Nó ước lượng tầm quan trọng của mỗi kênh đặc trưng, gán trọng số. Nhưng với phát hiện văn bản, độ phân giải đầu vào lớn (thường 640×640), nên SE module mất nhiều thời gian. Khả năng cải thiện mạng có hạn nhưng module khá tốn thời gian. Vì vậy trong PP-OCR, backbone phát hiện không dùng SE. Thí nghiệm cho thấy bỏ SE giúp giảm 40% kích thước mô hình siêu nhẹ mà hiệu quả phát hiện vẫn ổn.

**1.13 Cách tối ưu PP-OCR nếu hiệu quả phát hiện chưa tốt?**
A: Tùy trường hợp:
- Hiệu quả không tốt với cảnh của bạn → ưu tiên fine-tune dữ liệu của bạn
- Ảnh quá lớn, text dày đặc → đừng nén ảnh quá mức; chỉnh logic resize trong tiền xử lý
- Hộp phát hiện quá sát hoặc quá lớn → điều chỉnh `db_unclip_ratio`
- Bỏ sót nhiều hộp → giảm `det_db_box_thresh`, hoặc đặt `det_db_score_mode='slow'`
- Đặt `use_dilation=True` để mở rộng feature map của phát hiện

**1.14 Làm gì khi một phần văn bản bị bỏ sót như hình dưới?**
A: Vấn đề cho thấy một phần được phát hiện nhưng IoU > 0.5 nên chỉ số không phản ánh được. Nếu có nhiều trường hợp như vậy: tăng ngưỡng IoU. Nguyên nhân bỏ sót thường là đặc trưng văn bản không phản hồi — mạng chưa học được. Phân tích từng trường hợp: trực quan kết quả để tìm hiểu lý do (ánh sáng, biến dạng, văn bản dài...) rồi tối ưu bằng tăng cường dữ liệu, điều chỉnh mạng, hoặc thích ứng hậu xử lý.

### Hỏi đáp về suy luận mô hình

**2.1 Biên hộp quá sát text khiến một số góc bị mất, có cách nào?**
A: Tăng `unclip_ratio` trong hậu xử lý. Càng lớn, hộp văn bản càng lớn.

**2.2 Tại sao suy luận PaddleOCR chỉ hỗ trợ một ảnh một lần?**
A: Ảnh được scale tỉ lệ, cạnh dài nhất là 960. Chiều dài và rộng các ảnh khác nhau sau scale nên không thể tạo batch — đặt `test_batch_size_per_card=1`.

**2.3 Tăng tốc suy luận trên CPU?**
A: Dùng **mkldnn (OneDNN)** trên CPU x86 hỗ trợ mkldnn. Tăng `num_threads` cho suy luận.

**2.4 Tăng tốc trên GPU?**
A: Khuyến nghị dùng **TensorRT**:
1. Tải gói Paddle / thư viện suy luận có TensorRT
2. Tải TensorRT từ Nvidia (đúng version với Paddle)
3. Đặt `LD_LIBRARY_PATH` trỏ vào thư mục lib TensorRT
4. Bật option `tensorrt`

**2.5 Triển khai trên thiết bị di động?**
A: PaddlePaddle có **PaddleLite** cho triển khai mobile. PaddleOCR cung cấp DB+CRNN làm code demo cho Android arm.

**2.6 Dùng suy luận đa tiến trình?**
A: PaddleOCR đã thêm tham số kiểm soát đa tiến trình. `use_mp=True` và `total_process_num` chỉ số tiến trình.

**2.7 Cách giải quyết bùng nổ bộ nhớ video và rò rỉ trong suy luận?**
A: Nếu là mô hình huấn luyện, thiếu bộ nhớ vì model hoặc ảnh đầu vào quá lớn. Thêm `paddle.no_grad()` trước hàm main để giảm bộ nhớ. Nếu mô hình suy luận, thêm `config.enable_memory_optim()` trong cấu hình. Về rò rỉ — cài bản Paddle mới nhất đã sửa.

---

## 4.2.5 Bài tập

**Câu hỏi ngắn:**
1. Theo kích thước feature map đầu ra của DB Backbone và FPN, chiều cao và rộng ảnh đầu vào của DB phải là bội số của: A: 32, B: 64.

**Thí nghiệm:**
1. Dùng file cấu hình `configs/det/det_mv3_db.yml` để huấn luyện mô hình phát hiện trên tập `det_data_lesson_demo.tar`, tối ưu độ chính xác.

*Hình 8: Ví dụ dữ liệu huấn luyện det_data_lesson_demo*

## 4.3 Tổng kết

Chương này giới thiệu lý thuyết và thực hành của thuật toán phát hiện văn bản.

- Phần đầu giới thiệu cách bắt đầu nhanh với mô hình phát hiện văn bản PaddleOCR và minh họa quy trình từ xử lý dữ liệu đến huấn luyện thuật toán với ví dụ thuật toán DB.
- Phần thứ hai giới thiệu sự phát triển của phát hiện văn bản trong những năm gần đây, gồm các phương pháp dựa trên hồi quy và phân đoạn.

Chương tiếp theo sẽ nói về các thuật toán nhận dạng văn bản.

## 4.4 Tài liệu tham khảo

1. Liao, Minghui, et al. "Textboxes: A fast text detector with a single deep neural network." AAAI, 2017.
2. Liao, Minghui, Baoguang Shi, and Xiang Bai. "TextBoxes++: A single-shot oriented scene text detector." IEEE TIP 27.8 (2018): 3676-3690.
3. Tian, Zhi, et al. "Detecting text in natural image with connectionist text proposal network." ECCV, Springer, Cham, 2016.
4. Zhou, Xinyu, et al. "EAST: An efficient and accurate scene text detector." CVPR, 2017.
5. Wang, Fangfang, et al. "Geometry-aware scene text detection with instance transformation network." CVPR, 2018.
6. Yuliang, Liu, et al. "Detecting curve text in the wild: New dataset and new solution." arXiv:1712.02170 (2017).
7. Deng, Dan, et al. "Pixellink: Detecting scene text via instance segmentation." AAAI, Vol. 32. No. 1. 2018.
8. Wu, Yue, and Prem Natarajan. "Self-organized text detection with minimal post-processing via border learning." ICCV, 2017.
9. Tian, Zhuotao, et al. "Learning shape-aware embedding for scene text detection." CVPR, 2019.
10. Wang, Wenhai, et al. "Shape robust text detection with progressive scale expansion network." CVPR, 2019.
11. Wang, Wenhai, et al. "Efficient and accurate arbitrary-shaped text detection with pixel aggregation network." ICCV, 2019.
12. Liao, Minghui, et al. "Real-time scene text detection with differentiable binarization." AAAI, Vol. 34. No. 07. 2020.
13. Hochreiter, Sepp, and Jürgen Schmidhuber. "Long short-term memory." Neural computation 9.8 (1997): 1735-1780.
14. Dai, Pengwen, et al. "Progressive Contour Regression for Arbitrary-Shape Scene Text Detection." CVPR, 2021.
15. He, Minghang, et al. "MOST: A Multi-Oriented Scene Text Detector with Localization Refinement." CVPR, 2021.
16. Zhu, Yiqin, et al. "Fourier contour embedding for arbitrary-shaped text detection." CVPR, 2021.
17. Tang, Jun, et al. "Seglink++: Detecting dense and arbitrary-shaped scene text by instance-aware component grouping." Pattern Recognition 96 (2019): 106954.
18. Wang, Yuxin, et al. "Contournet: Taking a further step toward accurate arbitrary-shaped scene text detection." CVPR, 2020.
19. Zhang, Chengquan, et al. "Look more than once: An accurate detector for text of arbitrary shapes." CVPR, 2019.
20. Xue C, Lu S, Zhang W. "MSR: Multi-scale shape regression for scene text detection." arXiv:1901.02596, 2019.

---

# CHƯƠNG 5 — NHẬN DẠNG VĂN BẢN (TEXT RECOGNITION)

Chương này chủ yếu về lý thuyết của các thuật toán nhận dạng văn bản, gồm bối cảnh, các lớp thuật toán và ý tưởng từ các bài báo kinh điển.

Bạn sẽ học:
1. Mục tiêu của nhận dạng văn bản
2. Các loại thuật toán nhận dạng văn bản
3. Ý tưởng điển hình của từng thuật toán

Nhận dạng văn bản là một tác vụ con của OCR, nhắm đến nhận dạng nội dung của một vùng cụ thể. Trong phương pháp OCR hai giai đoạn, nó đến sau phát hiện văn bản để chuyển ảnh thành text.

Mô hình nhận một dòng văn bản đã định vị và dự đoán nội dung cùng độ tin cậy.

*Hình 1: Trực quan hóa kết quả dự đoán — ví dụ "汉阳鹦鹉家居建材市场E区25-26号" (độ tin cậy 0.9957605) và "原装电池" (0.99971426)*

Nhận dạng văn bản có nhiều kịch bản: nhận dạng tài liệu, biển báo đường, biển số, số công nghiệp. Trong thực tế, có thể chia hai loại:

- **Nhận dạng văn bản thông thường (Regular)**: chủ yếu cho văn bản gần ngang — phông in, văn bản quét.
- **Nhận dạng văn bản không thông thường (Irregular)**: phổ biến trong cảnh tự nhiên — văn bản bị méo, che, mờ, cong, nghiêng.

*Hình 2: Mẫu ảnh IC15 (văn bản không thông thường)*
*Hình 3: Mẫu ảnh IC13 (văn bản thông thường)*

Hai tập dữ liệu công khai trên thường dùng để so sánh khả năng thuật toán. Phân loại các tập dữ liệu benchmark tiếng Anh phổ biến:

- **Văn bản thông thường**: IIIT5K, SVT, IC13
- **Văn bản không thông thường**: IC15, SVTP, CUTE

*Hình 4: Tập dữ liệu benchmark tiếng Anh phổ biến*

## 5.1 Giới thiệu các phương pháp nhận dạng văn bản

Trong phương pháp truyền thống, nhận dạng văn bản chia 3 bước: tiền xử lý ảnh, phân đoạn ký tự, và nhận dạng ký tự. Vậy cần mô hình hóa cho một cảnh cụ thể, mô hình sẽ thất bại khi cảnh thay đổi. Với cảnh phức tạp, các phương pháp học sâu hoạt động tốt hơn.

Phần lớn thuật toán nhận dạng có thể được biểu diễn theo framework sau, chia 4 stage:

| Stage | Mô tả |
|---|---|
| Spatial Transformation Module | Hiệu chỉnh ảnh — thường dùng STN hoặc TPS |
| Vision Feature Extraction Module | Trích đặc trưng ảnh — VGG, RCNN, ResNet... |
| Sequence Feature Extraction Module | Sinh chuỗi ký tự — BiLSTM, Transformer... |
| Predict Module | Chuyển dự đoán mỗi frame của RNN thành chuỗi nhãn — CTC, Attention |

**Tổng hợp các loại thuật toán chính:**

| Loại | Ý tưởng | Bài báo chính |
|---|---|---|
| Truyền thống | Cửa sổ trượt, trích ký tự, lập trình động | — |
| CTC | Dựa trên CTC, nhanh hơn, không cần căn chỉnh trước | CRNN, Rosetta |
| Attention | Áp dụng cho văn bản không thông thường | RARE, DAN, PREN |
| Transformer | Phương pháp dựa transformer | SRN, NRTR, Master, ABINet |
| Rectification | Module hiệu chỉnh học biên text và sửa theo trục ngang | RARE, ASTER, SAR |
| Segmentation | Phân đoạn lấy vị trí ký tự, sau đó phân loại | Text Scanner, Mask TextSpotter |

### 5.1.1 Nhận dạng văn bản thông thường

Có hai thuật toán chính: dựa trên **CTC** (Connectionist Temporal Classification) và **Sequence2Sequence**. Khác nhau ở cách giải mã.

- CTC: chuỗi mã hóa đưa vào CTC để giải mã.
- Seq2Seq: chuỗi đưa vào module RNN để giải mã tuần hoàn.

Cả hai đã được kiểm chứng hiệu quả và là phương pháp chủ đạo.

*Hình 5: Trái — phương pháp CTC, phải — phương pháp Sequence2Sequence*

#### Thuật toán dựa trên CTC

Thuật toán CTC điển hình nhất là **CRNN** (Convolutional Recurrent Neural Network) [1]. CRNN dùng các cấu trúc tích chập chủ đạo như ResNet, MobileNet, VGG để trích đặc trưng. Do đặc thù của nhận dạng văn bản — có nhiều thông tin ngữ cảnh trong đầu vào — và đặc trưng kernel tích chập tập trung vào thông tin cục bộ, thiếu mô hình hóa phụ thuộc dài hạn, CRNN giới thiệu **LSTM hai chiều (Bidirectional LSTM)** để tăng cường mô hình hóa ngữ cảnh. Thí nghiệm chứng minh module BiLSTM trích xuất thông tin ngữ cảnh hiệu quả, sau đó đưa chuỗi đặc trưng đầu ra vào CTC để giải mã chuỗi. Cấu trúc này được áp dụng rộng rãi trong nhận dạng văn bản.

**Rosetta** [2] do Facebook đề xuất, gồm mô hình tích chập đầy đủ và CTC. **Gao Y** [3] et al. dùng tích chập CNN thay LSTM vì ít tham số, hiệu suất tốt hơn và cùng độ chính xác.

*Hình 6: Sơ đồ cấu trúc CRNN — Convolutional Layers → Feature sequence → Recurrent Layers (Deep bidirectional LSTM) → Per-frame predictions → Transcription Layer*

#### Thuật toán Sequence2Sequence

Trong Seq2Seq, Encoder mã hóa chuỗi đầu vào thành vector ngữ nghĩa thống nhất, Decoder giải mã. Trong giải mã, mỗi đầu ra ở bước t-1 là đầu vào của bước t, lặp đến khi xuất ra ký tự kết thúc. Encoder thường là RNN; mỗi từ đầu vào, encoder xuất vector và hidden state, dùng hidden state cho từ tiếp theo trong vòng lặp. Decoder là RNN khác nhận vector đầu ra của encoder và xuất chuỗi từ. Lấy cảm hứng từ Seq2Seq trong dịch máy, **Shi** [4] đề xuất framework codec dựa attention cho nhận dạng văn bản. RNN có thể học mô hình ngôn ngữ ký tự ẩn trong chuỗi từ dữ liệu huấn luyện.

*Hình 7: Sơ đồ cấu trúc Sequence2Sequence*

Cả hai phương pháp hoạt động tốt với văn bản thông thường nhưng kém với văn bản cong hoặc nghiêng do giới hạn thiết kế mạng. Để giải quyết, các nhà nghiên cứu đề xuất các thuật toán cải tiến.

### 5.1.2 Nhận dạng văn bản không thông thường

Thuật toán nhận dạng văn bản không thông thường chia 4 loại: **Rectification-based**, **Attention-based**, **Segmentation-based**, **Transformer-based**.

#### Phương pháp dựa trên hiệu chỉnh (Rectification-based)

Dùng module biến đổi hình ảnh để chuyển văn bản không thông thường thành văn bản thông thường nhiều nhất có thể, rồi áp dụng phương pháp nhận dạng thông thường.

**RARE** [4] là mô hình đầu tiên đề xuất hiệu chỉnh cho văn bản bất thường. Mạng gồm 2 phần: **STN (Spatial Transformer Network)** và mạng nhận dạng dựa Seq2Seq. STN là module hiệu chỉnh. Ảnh text bất thường đi vào STN và chuyển thành ảnh ngang qua **TPS (Thin-Plate-Spline)**. Biến đổi này có thể hiệu chỉnh văn bản cong và biến hình một phần.

*Hình 8: Sơ đồ cấu trúc RARE — Input Image → Spatial Transformer Network → Rectified Image → Sequence Recognition Network → "MOON"*

Bài RARE chỉ ra phương pháp này có lợi thế lớn trên tập dữ liệu bất thường. So sánh CUTE80 và SVTP với CRNN, hơn 5 điểm % — chứng tỏ module hiệu chỉnh hữu hiệu. Dựa trên đó, [6] cũng kết hợp STN với hệ thống nhận dạng dựa attention.

Phương pháp hiệu chỉnh linh hoạt trong di chuyển. Ngoài attention như RARE, **STAR-Net** [5] áp dụng module hiệu chỉnh cho thuật toán CTC — cải thiện đáng kể so với CRNN.

#### Phương pháp dựa Attention

Phương pháp attention tập trung vào tương quan giữa các chuỗi. Đầu tiên đề xuất trong dịch máy: tin rằng dịch chủ yếu bị ảnh hưởng bởi một số từ nhất định, từ quyết định nên có trọng số lớn hơn. Tương tự cho nhận dạng văn bản. Khi giải mã chuỗi đã mã hóa, mỗi bước chọn ngữ cảnh phù hợp để sinh state kế tiếp, kết quả chính xác hơn.

**R²AM** [7] là phương pháp đầu áp dụng Attention cho nhận dạng văn bản. Mô hình trích đặc trưng đã mã hóa từ ảnh đầu vào qua tầng tích chập đệ quy, sau đó dùng thống kê ngôn ngữ cấp ký tự đã học ngầm để giải mã đầu ra qua mạng nơ-ron lặp. Trong giải mã, attention được giới thiệu để chọn đặc trưng mềm — gần với trực giác con người hơn.

*Hình 9: Sơ đồ R²AM với character-level language modeling và Attention modeling*

Nhiều thuật toán đã khám phá lĩnh vực attention. **SAR** [8] mở rộng attention 1D thành 2D. RARE đã đề cập cũng dựa attention. Thí nghiệm cho thấy phương pháp attention có độ chính xác cao hơn CTC.

*Hình 10: Sơ đồ Attention — minh họa OPTIMUM, STARBU, WYNDHA, CHEVRO, ROBINS, played, UNITED*

#### Phương pháp dựa Segmentation

Coi mỗi ký tự của dòng văn bản như một đơn vị riêng, dễ nhận dạng ký tự đã phân đoạn hơn so với toàn bộ dòng văn bản đã hiệu chỉnh. Thuật toán cố gắng định vị mỗi ký tự trong ảnh văn bản đầu vào, dùng bộ phân loại ký tự để nhận dạng — đơn giản hóa vấn đề toàn cục thành cục bộ. Hoạt động tốt trong cảnh văn bản bất thường. Tuy nhiên, phương pháp này yêu cầu nhãn cấp ký tự, khá khó để có. **Lyu** [9] et al. đề xuất mô hình phân đoạn từ dựa ví dụ để nhận dạng, dùng phương pháp dựa FCN trong phần nhận dạng. [10] thiết kế FCN attention ký tự để giải quyết nhận dạng văn bản từ góc nhìn 2D. Khi văn bản cong hoặc méo nghiêm trọng, phương pháp này định vị tốt cả văn bản thông thường và bất thường.

*Hình 11: Sơ đồ cấu trúc Mask TextSpotter — RoI Feature → Character Segmentation Map (Foreground Mask, Character Mask) → Binary Mask → Results "naughty"*

#### Phương pháp dựa Transformer

Với sự phát triển nhanh của transformer, tính hiệu quả của transformer trong các tác vụ thị giác đã được kiểm chứng trong phân loại và phát hiện. Như đã đề cập trong nhận dạng văn bản thông thường, CNN có hạn chế trong mô hình hóa phụ thuộc dài hạn. Cấu trúc transformer giải quyết vấn đề này. Có thể chú ý đến thông tin toàn cục trong feature extractor và thay thế module mô hình hóa ngữ cảnh phụ thêm (LSTM).

Một số thuật toán nhận dạng dùng cấu trúc encoder của transformer và tích chập để trích đặc trưng chuỗi. Encoder gồm nhiều block xếp chồng với MultiHeadAttention Layer và Positionwise Feedforward Layer. Self-attention trong MultiHeadAttention dùng phép nhân ma trận để mô phỏng tính toán chuỗi thời gian của RNN, giải phóng khỏi phụ thuộc thời gian dài hạn. Cũng có thuật toán dùng decoder của transformer để giải mã — cho thông tin ngữ nghĩa mạnh hơn RNN và hiệu suất tính toán song song cao hơn.

- **SRN** [11] kết nối encoder của transformer với ResNet50 để tăng cường đặc trưng thị giác 2D. Đề xuất module **parallel attention**, dùng thứ tự đọc làm query để tính độc lập với thời gian, xuất song song đặc trưng thị giác đã căn chỉnh ở tất cả bước thời gian. SRN cũng dùng encoder của transformer làm module ngữ nghĩa để tích hợp thông tin thị giác và ngữ nghĩa — hiệu quả hơn với văn bản bất thường bị che và mờ.
- **NRTR** [12] dùng cấu trúc transformer đầy đủ để mã hóa và giải mã ảnh đầu vào, chỉ dùng vài tầng tích chập cho trích xuất đặc trưng cấp cao.
- **SRACN** [13] dùng decoder của transformer thay LSTM, xác nhận lại huấn luyện song song hiệu quả và chính xác.

---

## 5.2 Thực hành nhận dạng văn bản với CRNN

Lý thuyết đã trình bày các phương pháp chính. **CRNN** là một trong những phương pháp được đề xuất sớm và sử dụng rộng rãi trong công nghiệp. Chương này sẽ trình bày cách xây dựng, huấn luyện, đánh giá và dự đoán mô hình nhận dạng văn bản CRNN dựa trên PaddleOCR. Dữ liệu là **icdar2015** với 4468 mẫu huấn luyện và 2077 mẫu test.

Trong phần này, bạn sẽ học:
1. Cách dùng gói PaddleOCR whl để dự đoán nhanh
2. Nguyên lý và cấu trúc mạng CRNN
3. Các bước cần thiết và phương pháp điều chỉnh tham số huấn luyện
4. Cách dùng dataset tùy chỉnh để huấn luyện

### 5.2.1 Bắt đầu nhanh

**Cài đặt dependencies và WHL packages:**

```bash
# Cài PaddlePaddle bản GPU
!pip install paddlepaddle-gpu
# Cài gói PaddleOCR whl
!pip install -U pip
!pip install paddleocr
```

**Dự đoán nội dung nhanh:**

Gói paddleocr sẽ tự động tải mô hình ppocr nhẹ.

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR()
img_path = '/home/aistudio/work/word_19.png'
result = ocr.ocr(img_path, det=False)
for line in result:
    print(line)
```

Kết quả trả về `(text, confidence)`. Ví dụ: `('SLOW', 0.9776376)`.

### 5.2.2 Triển khai chi tiết thuật toán CRNN

Trong phần 4.2.1, `paddleocr` đã tải mô hình CRNN tiền huấn luyện để dự đoán. Phần này giới thiệu chi tiết nguyên lý và quy trình CRNN.

#### Phân loại

CRNN là thuật toán dựa CTC. Vị trí trong sơ đồ lý thuyết là:

```
文本识别 (Text Recognition)
  ├── 规则文本 (Regular text)
  │     ├── 基于CTC的算法 (CTC-based)
  │     │     ├── CRNN ★
  │     │     ├── Rosetta
  │     │     └── others
  │     └── Sequence2Sequence的算法
  └── 不规则文本 (Irregular text)
```

CRNN chủ yếu xử lý văn bản thông thường, thuật toán CTC nhanh hơn và phù hợp văn bản dài. PPOCR chọn CRNN để nhận dạng ký tự tiếng Trung.

#### Giới thiệu chi tiết thuật toán

Cấu trúc mạng CRNN có 3 phần từ dưới lên: **Convolutional layers**, **Recurrent layers**, **Transcription layers**.

*Hình: Cấu trúc CRNN — Input image → Convolutional feature maps → Feature sequence → Deep bidirectional LSTM → Per-frame predictions → "state"*

**1. Backbone:**

Mạng tích chập làm backbone để trích chuỗi đặc trưng từ ảnh đầu vào. Vì `conv`, `max-pooling`, `elementwise` và hàm kích hoạt đều tác động lên vùng cục bộ, chúng bất biến với dịch chuyển. Mỗi cột feature map tương ứng với một vùng chữ nhật (receptive field) của ảnh gốc, các vùng này theo thứ tự từ trái sang phải tương ứng với các cột trên feature map. Vì CNN cần scale ảnh đầu vào về chiều cố định, không phù hợp cho chuỗi có độ dài rất khác nhau. Để hỗ trợ chuỗi độ dài thay đổi, CRNN gửi vector đặc trưng đầu ra tầng cuối backbone vào RNN và chuyển thành đặc trưng chuỗi.

*Hình: Feature Sequence và Receptive field*

**2. Neck:**

Dựa trên mạng tích chập, tầng recurrent xây dựng mạng tuần hoàn, chuyển đặc trưng ảnh thành đặc trưng chuỗi, và dự đoán phân phối nhãn của mỗi frame. RNN giỏi nắm bắt thông tin ngữ cảnh chuỗi. Khi nhận dạng chuỗi dựa ảnh, ngữ cảnh hữu ích hơn xử lý từng pixel riêng lẻ. Ví dụ, một ký tự rộng có thể cần vài frame liên tiếp để mô tả tốt. Một số ký tự mơ hồ cũng dễ giải nghĩa hơn khi quan sát ngữ cảnh. Hơn nữa, RNN truyền lỗi ngược về tầng tích chập, cho phép huấn luyện mạng thống nhất. RNN xử lý chuỗi độ dài bất kỳ, giải quyết vấn đề ảnh text dài. CRNN dùng LSTM hai tầng làm tầng recurrent để giải quyết biến mất và bùng nổ gradient khi huấn luyện chuỗi dài.

**3. Head:**

Tầng phiên âm chuyển dự đoán mỗi frame thành chuỗi nhãn cuối qua mạng kết nối đầy đủ và softmax. Cuối cùng dùng **CTC Loss** để hoàn thành huấn luyện kết hợp CNN-RNN mà không cần căn chỉnh chuỗi. CTC có cơ chế đặc biệt để gộp chuỗi. Sau khi LSTM xuất chuỗi, cần phân loại theo trình tự thời gian. Có thể có nhiều time step cùng tương ứng một loại, nên kết quả tương tự cần gộp. Để tránh gộp các ký tự lặp đã có, CTC giới thiệu ký tự **blank** giữa các ký tự lặp.

*Hình: Minh họa "Paddle" — t0 P, t1 P, t2 -, t3 a, t4 -, t5 d, t6 -, t7 d, t8 d, t9 l, t10 -, t11 e, t12 e → Paddle*

#### Ví dụ mã

Cấu trúc mạng đơn giản và mã triển khai khá đơn giản. Có thể xây các module theo thứ tự dự đoán. Phần này có 4 phần: nhập dữ liệu, xây backbone, xây neck, xây head.

**[Nhập dữ liệu]:** Dữ liệu cần scale về kích thước thống nhất (3, 32, 320) và chuẩn hóa trước khi đưa vào mạng. Tăng cường dữ liệu được lược ở đây cho gọn; các bước cần thiết được minh họa trên 1 ảnh.

```python
import cv2, math, numpy as np

def resize_norm_img(img):
    """Scale và chuẩn hóa dữ liệu"""
    imgC, imgH, imgW = 3, 32, 320
    h, w = img.shape[:2]
    # ... (mã đầy đủ tham khảo repo PaddleOCR)
```

---

*— Hết phần dịch trang 50–100 —*

*Phần tiếp theo sẽ tiếp tục từ trang 101 trở đi (chi tiết triển khai backbone, neck, head, huấn luyện CRNN, FAQ, v.v.).*

---

**Tài nguyên bổ sung:**
- Mã nguồn đầy đủ: https://github.com/PaddlePaddle/PaddleOCR
- File cấu hình: https://github.com/PaddlePaddle/PaddleOCR/tree/release/2.4/configs
- Tài liệu: https://paddlepaddle.github.io/PaddleOCR/
