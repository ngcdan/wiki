# Dive into OCR — Bản dịch tiếng Việt (Trang 250–300)

*Tiếp nối từ file dịch trang 200–250. Đây là bản dịch đầy đủ bằng tiếng Việt. Technical terms giữ nguyên tiếng Anh.*

> Tài liệu gốc: https://github.com/PaddlePaddle/PaddleOCR (release/2.4)

---

## 8.2 Thực hành Nhận dạng Bảng OCR (tiếp)

### 8.2.2 Giải thích Nguyên lý Dự đoán (tiếp — trang 244–248)

#### Head

Input của head là bốn feature maps output bởi backbone, và output là kết quả suy luận của table structure và tọa độ cell.

Ý nghĩa các tham số đầu vào:

| Tham số | Ý nghĩa |
|---------|---------|
| `in_channels` | Số channels của input feature map |
| `hidden_size` | Hidden layer unit của RNN module trong Attention |
| `max_elem_length` | Số ký tự tối đa được suy luận |
| `in_max_len` | Kích thước input image |
| `loc_type` | Input của nhánh tọa độ cell. 1: Chỉ dùng hidden layer sau Attention. 2: Fuse CNN + Attention features |

Code như sau:

```python
# https://github.com/PaddlePaddle/PaddleOCR/blob/dygraph/ppocr/modeling/heads/table_att_head.py
from paddle import nn
import paddle.nn.functional as F
from ppocr.modeling.heads.table_att_head import AttentionGRUCell

class TableAttentionHead(nn.Layer):
    def __init__(self,
                 in_channels,
                 hidden_size,
                 loc_type=2,
                 in_max_len=488,   # Kích thước input image
                 max_elem_length=800,  # Số labels output tối đa
                 **kwargs):
        super(TableAttentionHead, self).__init__()
        self.input_size = in_channels[-1]
        self.hidden_size = hidden_size
        self.elem_num = 30
        self.max_elem_length = max_elem_length

        self.structure_attention_cell = AttentionGRUCell(
            self.input_size, hidden_size, self.elem_num, use_gru=False)
        self.structure_generator = nn.Linear(hidden_size, self.elem_num)
        self.loc_type = loc_type

        self.in_max_len = in_max_len

        # Nhánh coordinate box regression
        if self.loc_type == 1:
            self.loc_generator = nn.Linear(hidden_size, 4)
        else:
            if self.in_max_len == 640:
                # Kích thước feature map cuối qua backbone là 20*20,
                # nên kích thước input feature map ở đây là 400
                self.loc_fea_trans = nn.Linear(400, self.max_elem_length + 1)
            elif self.in_max_len == 800:
                # Kích thước feature map cuối sau backbone là 23*25,
                # nên kích thước input feature map ở đây là 625
                self.loc_fea_trans = nn.Linear(625, self.max_elem_length + 1)
            elif self.in_max_len == 488:
                # Kích thước feature map cuối qua backbone là 16*16,
                # nên kích thước input feature map ở đây là 256
                self.loc_fea_trans = nn.Linear(256, self.max_elem_length + 1)
            self.loc_generator = nn.Linear(self.input_size + hidden_size, 4)

    def _char_to_onehot(self, input_char, onehot_dim):
        input_ont_hot = F.one_hot(input_char, onehot_dim)
        return input_ont_hot

    def forward(self, inputs, targets=None):
        # Lấy feature map nhỏ nhất output bởi backbone
        fea = inputs[-1]
        if len(fea.shape) == 3:
            pass
        else:
            # Reshape B,C,H,W thành B,C,H*W
            last_shape = int(np.prod(fea.shape[2:]))
            fea = paddle.reshape(fea, [fea.shape[0], fea.shape[1], last_shape])
            # Chuyển B,C,W thành B,W,C
            fea = fea.transpose([0, 2, 1])
        batch_size = fea.shape[0]

        hidden = paddle.zeros((batch_size, self.hidden_size))
        output_hiddens = []
        if self.training and targets is not None:
            structure = targets[0]
            for i in range(self.max_elem_length + 1):
                elem_onehots = self._char_to_onehot(
                    structure[:, i], onehot_dim=self.elem_num)
                (outputs, hidden), alpha = self.structure_attention_cell(
                    hidden, fea, elem_onehots)
                output_hiddens.append(paddle.unsqueeze(outputs, axis=1))
            output = paddle.concat(output_hiddens, axis=1)
            structure_probs = self.structure_generator(output)
            if self.loc_type == 1:
                loc_preds = self.loc_generator(output)
                loc_preds = F.sigmoid(loc_preds)
            else:
                loc_fea = fea.transpose([0, 2, 1])
                loc_fea = self.loc_fea_trans(loc_fea)
                loc_fea = loc_fea.transpose([0, 2, 1])
                loc_concat = paddle.concat([output, loc_fea], axis=2)
                loc_preds = self.loc_generator(loc_concat)
                loc_preds = F.sigmoid(loc_preds)
        else:
            temp_elem = paddle.zeros(shape=[batch_size], dtype="int32")
            structure_probs = None
            loc_preds = None
            elem_onehots = None
            outputs = None
            alpha = None
            max_elem_length = paddle.to_tensor(self.max_elem_length)
            i = 0
            # Attention forward
            while i < max_elem_length + 1:
                elem_onehots = self._char_to_onehot(
                    temp_elem, onehot_dim=self.elem_num)
                (outputs, hidden), alpha = self.structure_attention_cell(
                    hidden, fea, elem_onehots)
                output_hiddens.append(paddle.unsqueeze(outputs, axis=1))
                structure_probs_step = self.structure_generator(outputs)
                temp_elem = structure_probs_step.argmax(axis=1, dtype="int32")
                i += 1

            output = paddle.concat(output_hiddens, axis=1)
            print('Attention output shape', output.shape)
            # Nhánh table structure
            structure_probs = self.structure_generator(output)
            structure_probs = F.softmax(structure_probs)

            # Nhánh cell coordinate
            if self.loc_type == 1:
                loc_preds = self.loc_generator(output)
                loc_preds = F.sigmoid(loc_preds)
            else:
                # Chuyển B,W,C thành B,C,W
                loc_fea = fea.transpose([0, 2, 1])

                loc_fea = self.loc_fea_trans(loc_fea)
                loc_fea = loc_fea.transpose([0, 2, 1])
                loc_concat = paddle.concat([output, loc_fea], axis=2)
                loc_preds = self.loc_generator(loc_concat)
                loc_preds = F.sigmoid(loc_preds)
        return {'structure_probs': structure_probs, 'loc_preds': loc_preds}
```

```python
# Khởi tạo head
head = TableAttentionHead(in_channels=backbone.out_channels, hidden_size=256, loc_type=2)
head.eval()
# Load head parameter
head.set_state_dict(head_dict)

# Thực thi head
print('*'*10, 'head forward shape', '*'*10)
head_out = head(backbone_out)
print('*'*10, 'head out shape', '*'*10)

# In head output và shape tương ứng
for key in head_out:
    print(key, head_out[key].shape)
```

Output:
```
********** head forward shape **********
Attention output shape [1, 801, 256]
********** head out shape **********
structure_probs [1, 801, 30]
loc_preds [1, 801, 4]
```

Giải thích:
- `structure_probs [1, 801, 30]`: xác suất dự đoán cho 801 vị trí, mỗi vị trí có 30 classes (tương ứng dictionary 30 token HTML)
- `loc_preds [1, 801, 4]`: tọa độ cell (x0, y0, x1, y1) cho mỗi vị trí — giá trị đã normalize qua sigmoid về [0,1]

#### Post-processing (Hậu xử lý)

Dictionary file cho hậu xử lý là `ppocr/utils/dict/table_structure_dict.txt`.

Ý tưởng của post-processing decoding:

1. Thực hiện CTC decoding trên `structure_probs`: loại bỏ các ký tự background `sos` và `eos`, chỉ lấy một trong các ký tự lặp liên tiếp.
2. Normalize tọa độ output về 0-1, nhân tọa độ với width và height của ảnh, và decode chúng về không gian ảnh.

```python
# https://github.com/PaddlePaddle/PaddleOCR/blob/dygraph/ppocr/postprocess/rec_postprocess.py#L441
from ppocr.postprocess.rec_postprocess import TableLabelDecode

def post_process(out):
    character_dict_path = 'ppocr/utils/dict/table_structure_dict.txt'
    # Khởi tạo post-processing op
    post_op = TableLabelDecode(character_dict_path)

    post_result = post_op(out)

    structure_str_list = post_result['structure_str_list']

    # Tọa độ đã normalize được khôi phục về kích thước ảnh gốc
    res_loc = post_result['res_loc']
    imgh, imgw = img.shape[0:2]
    res_loc_final = []
    for rno in range(len(res_loc[0])):
        x0, y0, x1, y1 = res_loc[0][rno]
        left = max(int(imgw * x0), 0)
        top = max(int(imgh * y0), 0)
        right = min(int(imgw * x1), imgw - 1)
        bottom = min(int(imgh * y1), imgh - 1)
        res_loc_final.append([left, top, right, bottom])

    # Xử lý thông tin structure
    structure_str_list = structure_str_list[0]
    structure_str_list = ['<html>', '<body>', '<table>'] + structure_str_list + ['</table>', '</body>', '</html>']
    return structure_str_list, res_loc_final

structure_str_list, res_loc_final = post_process(head_out)
```

```python
# In 10 output đầu tiên
print(structure_str_list[:10])
print(res_loc_final[:10])

# Visualization inference box
plt.figure(figsize=(24, 8))
img_show = img.copy()
for box in res_loc_final:
    cv2.rectangle(img_show, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 2)
plt.imshow(img_show)
```

Output:
```
['<html>', '<body>', '<table>', '<thead>', '<tr>', '<td>', '</td>', '<td>', '</td>', '<td>']
[[40, 4, 101, 19], [157, 5, 172, 19], [212, 4, 224, 18], [271, 5, 282, 19], [321, 4, 350, 19], [26, 22, 108, 38], [150, 22, 178, 37], [203, 22, 233, 38], [263, 22, 291, 37], [325, 22, 345, 37]]
```

Kết quả hiển thị: ảnh bảng gốc với tất cả cell boundaries được vẽ bằng hộp đỏ.

---

### 8.2.3 Training (Huấn luyện — trang 249–253)

Trong huấn luyện nhận dạng bảng, cần huấn luyện 3 models: text detection, text recognition, và table structure models. Việc huấn luyện text detection và recognition models có thể tham khảo các phần trước. Ở đây chỉ giới thiệu huấn luyện table structure model.

Phần này sử dụng PubTabNet dataset và MobileNetV3 làm backbone network để giới thiệu cách huấn luyện, đánh giá và test table structure model.

#### Chuẩn bị dữ liệu

Thí nghiệm này chọn PubTabNet dataset để demo.

Một phần PubTabNet dataset đã được tải về trong project và lưu tại `/home/aistudio/data/data119702`. Bạn có thể chạy lệnh sau để giải nén, hoặc tải từ https://github.com/ibm-aur-nlp/PubTabNet.

```bash
# Giải nén dataset
! cd /home/aistudio/data/data119702 && tar -xf pubtabnet_val.tar && cd -
! ls /home/aistudio/data/data119702
```

Output:
```
/home/aistudio/PaddleOCR
PubTabNet_2.0.0_val.jsonl  pubtabnet_val.tar  val
```

Sau khi chạy lệnh trên, có một thư mục và một file:
```
/home/aistudio/data/data119702
├── val/                          Thư mục lưu trữ ảnh
└── PubTabNet_2.0.0_val.jsonl/    Thông tin label
```

Format label của dataset:

```json
{
  "filename": "PMC5755158_010_01.png",    // Tên ảnh
  "split": "train",                        // Ảnh thuộc training set hay validation set?
  "imgid": 0,                              // Index của ảnh
  "html": {
    "structure": {"tokens": ["<thead>", "<tr>", "<td>", ...]},  // Chuỗi HTML của bảng
    "cell": [
      {
        "tokens": ["P", "a", "d", "d", "l", "e", "P", "a", "d", "d", "l", "e"],
                   // Text đơn trong bảng
        "bbox": [x0, y0, x1, y1]   // Tọa độ của text đơn trong bảng
      }
    ]
  }
}
```

#### Data Preprocessing (Tiền xử lý dữ liệu)

Có yêu cầu về format và kích thước ảnh đầu vào trong training. Do đó, trước khi đưa dữ liệu vào model, cần tiền xử lý ảnh và labels để đáp ứng yêu cầu network training và inference.

Tiền xử lý dữ liệu của table structure model chủ yếu bao gồm:

- **DecodeImage**: chuyển ảnh sang format Numpy
- **ResizeTableImage**: resize ảnh và scale cạnh dài về kích thước chỉ định, scale cạnh ngắn theo tỉ lệ tương ứng
- **TableLabelEncode**: parse thông tin label trong label file và lưu dưới format thống nhất
- **NormalizeImage**: thay đổi phân phối giá trị đầu vào của mỗi neuron trong mỗi layer neural network thành standard normal distribution với mean=0 và variance=1, để quá trình optimization trở nên smooth hơn và training dễ hội tụ hơn
- **PaddingTableImage**: padding cạnh ngắn của ảnh bằng cạnh dài
- **ToCHWImage**: format dữ liệu ảnh là [H, W, C] (height, width, channel number), training data format neural network dùng là [C, H, W], nên dữ liệu ảnh cần được sắp xếp lại, ví dụ [224, 224, 3] thành [3, 224, 224]
- **KeepKeys**: lọc dict

#### TableLabelEncode

Để phân tích label information trong label file, đầu tiên load label data và lấy một label:

```python
# Load một phần dữ liệu trong dataset
import json
from pprint import import pprint
with open('/home/aistudio/data/data119702/PubTabNet_2.0.0_val.jsonl', "rb") as f:
    data_lines = f.readlines()
    for line in data_lines:
        data_line = line.decode('utf-8').strip("\n")
        info = json.loads(data_line)
        break
```

Chạy code sau để quan sát so sánh trước và sau TableLabelEncode label encoding:

```python
from ppocr.data.imaug import TableLabelEncode
# Khởi tạo label encoder
label_eocoder_op = TableLabelEncode(max_text_length=100,  # Unused
                                    max_elem_length=50,   # Tối đa bao nhiêu cells có thể dự đoán mỗi ảnh
                                    max_cell_num=500,     # unused
                                    character_dict_path='ppocr/utils/dict/table_structure_dict.txt')
# Xây dựng input data
cells = info['html']['cells']
structure = info['html']['structure']
# In label trước decoding
print("The cells and structure before decode")
print("cells: ", cells)
print("structure: ", structure)

image = cv2.imread(os.path.join('/home/aistudio/data/data119702/val', info['filename']))
data = {'image': image, 'cells': cells, 'structure': structure}
# Thực thi label encoder
data = label_eocoder_op(data)
# In thông tin đã encoded
print("The bbox_list and structure after decode")
print("bbox_list:", data['bbox_list'].tolist())
print("structure:", data['structure'].tolist())
```

Output ví dụ:
```
The cells and structure before decode
cells: [
{'tokens': []},
{'tokens': ['<b>', 'W', 'e', 'a', 'n', 'i', 'n', 'g', '</b>'], 'bbox': [66, 4, 96, 13]},
{'tokens': ['<b>', 'W', 'e', 'e', 'k', ' ', '1', '5', '</b>'], 'bbox': [131, 4, 160, 13]}
...
]
structure: {'tokens': ['<thead>', '<tr>', '<td>',..., '</td>', '</tr>', '</ <tbody>']}

The bbox_list and structure after decode
bbox_list: [
[0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0],
...
[0.27731093764305115, 0.06779661029577255, 0.40336135029792786, 0.22033898532390594],
...
[0.0, 0.0, 0.0, 0.0]
]
structure: [0, 1, 2, ..., 5, 8, 29, 0, 0, 0, 0, 0, 0, 0]
```

Giải thích: `bbox_list` chứa tọa độ đã normalize về [0,1], `structure` chứa index tương ứng trong dictionary.

#### Loss Function (Hàm mất mát)

Loss của model chia thành hai phần:

1. **Structure loss**: structure loss dùng **CrossEntropyLoss**
2. **Loc loss**: loc loss dùng **MSELoss**

Hai losses được fused bằng weighting, total loss với `structure_weight` = 100 và `loc_weight` = 10000:

```
total_loss = structure_loss * structure_weight + loc_loss * loc_weight
```

#### Model Training (Huấn luyện model)

Khi dữ liệu đã được xử lý và loss function đã được định nghĩa, có thể bắt đầu huấn luyện model.

Training dựa trên PaddleOCR training engine, dưới dạng cấu hình tham số. Tham khảo file cấu hình table recognition model: `configs/table/table_mv3.yml`

Tham số kiến trúc network:

```yaml
Architecture:
  model_type: table
  algorithm: TableAttn
  Backbone:
    name: MobileNetV3
    scale: 1.0
    model_name: large
  Head:
    name: TableAttentionHead
    hidden_size: 256
    loc_type: 2
    max_text_length: 100
    max_elem_length: 800
    max_cell_num: 500
```

Tham số loss function:

```yaml
Loss:
  name: TableAttentionLoss
  structure_weight: 100.0
  loc_weight: 10000.0
```

Sau khi cấu hình xong, khởi động training bằng lệnh sau:

```bash
# Cấu hình dataset
!cd train_data/table/pubtabnet && ln -s /home/aistudio/data/data119702/PubTabNet_2.0.0_val.jsonl PubTabNet_2.0.0_train.jsonl \
&& ln -s /home/aistudio/data/data119702/PubTabNet_2.0.0_val.jsonl PubTabNet_2.0.0_val.jsonl \
&& ln -s /home/aistudio/data/data119702/val train \
&& ln -s /home/aistudio/data/data119702/val val

! python tools/train.py -c configs/table/table_mv3.yml -o Global.use_gpu=False Global.print_batch_step=1 Train.loader.batch_size_per_card=1 Eval.loader.batch_size_per_card=1
```

Trong quá trình training, log sau sẽ được output:

```
[2021/12/26 19:57:29] root INFO: train dataloader has 9115 iters
[2021/12/26 19:57:29] root INFO: valid dataloader has 9115 iters
[2021/12/26 19:57:29] root INFO: During the training process, after the 0th iteration, an evaluation is run every 400 iterations
[2021/12/26 19:57:47] root INFO: epoch: [1/400], iter: 1, lr: 0.001000, loss: 358.711182, structure_loss: 277.904785, loc_loss: 80.806374, acc: 0.000000, reader_cost: 0.05254 s, batch_cost: 17.39120 s, samples: 2, ips: 0.11500
[2021/12/26 19:57:55] root INFO: epoch: [1/400], iter: 2, lr: 0.001000, loss: 353.381165, structure_loss: 208.200623, loc_loss: 137.825607, acc: 0.000000, reader_cost: 0.00041 s, batch_cost: 8.65134 s, samples: 1, ips: 0.11559
...
```

#### Model Evaluation (Đánh giá model)

Trong quá trình training, hai models được lưu mặc định: một là model mới nhất được huấn luyện có tên `latest`, và model khác là model có accuracy cao nhất có tên `best_accuracy`. Tiếp theo, dùng model parameters đã lưu để đánh giá accuracy trên test set:

Mã đánh giá accuracy của table structure model nằm tại `PaddleOCR/ppocr/metrics/table_metric.py`. Gọi `tools/eval.py` để đánh giá accuracy model đã huấn luyện:

```bash
!python tools/eval.py -c configs/table/table_mv3.yml -o Global.checkpoints=/home/aistudio/PaddleOCR/pre_train/en_ppocr_mobile_v2.0_table_structure_train/best_accuracy Global.use_gpu=False Eval.loader.batch_size_per_card=1
```

Log đánh giá:

```
[2021/12/26 20:00:08] root INFO: resume from /home/aistudio/PaddleOCR/pre_train/en_ppocr_mobile_v2.0_table_structure_train/best_accuracy
[2021/12/26 20:00:08] root INFO: metric in ckpt *****************
[2021/12/26 20:00:08] root INFO: acc:0.738014262051563
[2021/12/26 20:00:08] root INFO: fps:8.360272547972942
[2021/12/26 20:00:08] root INFO: best_epoch:7
[2021/12/26 20:00:08] root INFO: start_epoch:8
eval model::    0%|                    | 2/9115 [00:07<8:55:26, 3.53s/it]^C
```

#### Model Inference (Suy luận model)

Sau khi huấn luyện model, bạn cũng có thể dùng model đã lưu để suy luận trên một ảnh đơn hoặc ảnh trong thư mục, và quan sát kết quả suy luận:

```bash
! python tools/infer_table.py -c configs/table/table_mv3.yml -o Global.checkpoints=pretrained_models/en_ppocr_mobile_v2.0_table_structure_train/best_accuracy Global.infer_img=doc/table/table.jpg Global.use_gpu=False
```

Output:
```
[2021/12/26 20:00:22] root INFO: resume from /home/aistudio/PaddleOCR/pre_train/en_ppocr_mobile_v2.0_table_structure_train/best_accuracy
[2021/12/26 20:00:26] root INFO: result: ['<thead><tr><td></td><td></td><td></td><td><thead><tbody><tr><td></td><td></td><td></td><td></td><td></td></tr>...</tbody>'], [[32, 9, 104, 40], [232, 8, 307, 41], [429, 7, 500, 44], [559, 8, 656, 44], [715, 7, 780, 44], ...]
[2021/12/26 20:00:26] root INFO: success!
```

Thông tin structure và cell box information của bảng được output trong quá trình suy luận.

### 8.2.4 Tổng kết

Phần này giới thiệu nguyên lý thuật toán nhận dạng bảng PP-Structure trong PaddleOCR, và quy trình xử lý dữ liệu đến kết thúc training của table structure model.

### 8.2.5 Bài tập

https://aistudio.baidu.com/aistudio/education/objective/28711

---

## 8.3 Thực hành DOC-VQA SER (trang 254–270)

Phần này sẽ giới thiệu cách sử dụng PaddleOCR để huấn luyện và chạy thuật toán DOC-VQA SER, bao gồm:

1. Hiểu nguyên lý thuật toán DOC-VQA SER
2. Nắm vững quy trình training mã DOC-VQA SER trong PaddleOCR

### 8.3.1 Quick Start

Chuẩn bị code và môi trường:

```bash
# Clone PaddleOCR code
! git clone -b release/2.4 https://gitee.com/paddlepaddle/PaddleOCR

# Cài dependencies
! pip install -r PaddleOCR/requirements.txt
! pip install paddleocr

# Cài dependencies
! pip install yacs gnureadline paddlenlp==2.2.1
```

```python
# Chuyển đến thư mục vqa
import os
os.chdir('PaddleOCR/ppstructure/vqa')
```

```bash
# Tải model
! mkdir pretrained_models
# Tải SER model và giải nén
! wget -P ./pretrained_models/ https://paddleocr.bj.bcebos.com/pplayout/PP-Layout_v1.0_ser_pretrained.tar && cd pretrained_models && tar xf PP-Layout_v1.0_ser_pretrained.tar && cd ..
```

```bash
# Thực hiện SER inference
# https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.4/ppstructure/vqa/infer_ser_e2e.py
! python infer_ser_e2e.py \
    --model_name_or_path "./pretrained_models/PP-Layout_v1.0_ser_pretrained/" \
    --max_seq_length 512 \
    --output_dir "output/res_e2e/" \
    --infer_imgs "images/input/zh_val_42.jpg"
```

```python
import cv2
from matplotlib import pyplot as plt
%matplotlib inline

img = cv2.imread('output/res_e2e/zh_val_42_ser.jpg')
plt.figure(figsize=(48, 24))
plt.imshow(img)
```

Kết quả hiển thị: form đăng ký thông tin cá nhân tiếng Trung — các trường được gán nhãn semantic (QUESTION, ANSWER, HEADER) với bounding boxes và màu sắc khác nhau.

### 8.3.2 Giải thích Nguyên lý (trang 257–263)

Các thuật toán của series DOC-VQA trong PaddleOCR hiện được triển khai dựa trên bài báo LayoutXLM, cung cấp hai tasks: SER và RE.

LayoutXLM là phiên bản đa ngôn ngữ (multi-language) của LayoutLMV2.

So với BERT trong NLP, LayoutXLM thêm layout information của text trong ảnh và image features vào input của model. LayoutXLM đã được triển khai trong PaddleNLP, nên ở đây chúng ta giới thiệu data và network từ góc nhìn model forward.

#### Input Data Processing

Đầu tiên, thực hiện phân tích OCR hoặc pdf trên ảnh, lấy texts và bbox information, và xây dựng 3 inputs của model trên cơ sở này:

**1. Text Embedding**

Đầu tiên, dùng WordPiece để phân đoạn text đã nhận dạng bởi OCR, thêm [CLS] và [SEP] tags, dùng [PAD] để fill in the length để lấy input sequence của text:

$$S = \{[CLS], w_1, w_2, \cdots, [SEP], [PAD], [PAD], \cdots\}, |S| = L$$

Sau đó cộng word vector, one-dimensional position vector, và segmented vector để lấy text vector:

$$t_i = TokEmb(w_i) + PosEmb1D(i) + SegEmb(s_i), 0 \leq i < L$$

- One-dimensional position vector: index của word
- Segmented vector: A

```python
# Text Embedding demo
from paddlenlp.transformers import LayoutXLMTokenizer

tokenizer = LayoutXLMTokenizer.from_pretrained('pretrained_models/PP-Layout_v1.0_ser_pretrained')
# Tokenization
print('分词结果', tokenizer.tokenize('开票日期'))
# Kết quả tokenization
print('编码转换结果', tokenizer.encode('开票日期'))
```

Output:
```
分词结果 ['_开', '票日期', '期']
编码转换结果 {'input_ids': [0, 13129, 84072, 1801, 2], 'token_type_ids': [0, 0, 0, 0, 0, 0]}
```

**2. Image Embedding**

Dùng mạng ResNeXt-FPN làm image encoder. Đầu tiên, trích xuất feature map của original document image, rồi average thành kích thước cố định (B * 256 * 7 * 7), và expand feature map theo hàng (B * 256 * 49) để lấy characteristic sequence tương ứng với ảnh sau linear projection (B * 49 * 256). Tương ứng với cấu tạo text vector, image vector cũng được bổ sung one-dimensional relative position và segmentation information. Cuối cùng, cộng feature vector, one-dimensional position vector, và segmented vector để lấy image vector:

$$v_i = Proj(VisTokEmb(I)_i) + PosEmb1D(i) + SegEmb([C]), 0 \leq i < WH$$

- Segmented vector: C

**3. Layout Embedding**

Với phạm vi tọa độ của mỗi word hoặc image region trên trang, bounding box song song với trục tọa độ được dùng để biểu diễn layout information, mỗi bounding box được biểu diễn bằng 4 giá trị tọa độ biên, width, và height. Layout vector thu được bằng cách concatenate các vectors tương ứng với 6 features:

$$l_i = Concat(PosEmb2D_x(x_0, x_1, w), PosEmb2D_y(y_0, y_1, h)), 0 \leq i < WH + L$$

Phần sau demo quy trình xây dựng network input từ input image. Toàn bộ quy trình bao gồm các bước:

1. Thực hiện OCR recognition trên ảnh
2. Tiền xử lý ảnh, bao gồm scaling về kích thước cụ thể và normalization
3. Tokenize text đã nhận dạng và chuyển thành index
4. Normalize text box và giữ giá trị trong khoảng 0-1000
5. Padding kết quả sau bước 3 và 4 để thuận tiện batch grouping

```python
# Xây dựng input cho inference
import cv2
import numpy as np
import paddle
from copy import deepcopy
from paddleocr import PaddleOCR
from paddlenlp.transformers import LayoutXLMTokenizer
from infer_ser_e2e import trans_poly_to_bbox, pad_sentences, split_page

def parse_ocr_info_for_ser(ocr_result):
    # Kết quả OCR được chuyển sang format dictionary,
    # text box được chuyển thành bounding rectangle
    ocr_info = []
    for res in ocr_result:
        ocr_info.append({
            "text": res[1][0],
            "bbox": trans_poly_to_bbox(res[0]),
            "poly": res[0],
        })
    return ocr_info

def preprocess(
        tokenizer,
        ori_img,
        ocr_info,
        img_size=(224, 224),
        pad_token_label_id=-100,
        max_seq_len=512,
        add_special_ids=False,
        return_attention_mask=True):
    ocr_info = deepcopy(ocr_info)
    height = ori_img.shape[0]
    width = ori_img.shape[1]

    # Resize ảnh về kích thước cụ thể
    img = cv2.resize(ori_img, img_size).transpose([2, 0, 1]).astype(np.float32)

    segment_offset_id = []  # Lưu vị trí kết thúc của mỗi text trong input_ids
    bbox_list = []           # Lưu box đã normalize về 0-1000
    input_ids_list = []      # Lưu index của tokenized text segment trong vocabulary
    token_type_ids_list = [] # Lưu category information của text segment

    for info in ocr_info:
        # Normalize box về 0-1000
        # x1, y1, x2, y2
        bbox = info["bbox"]
        bbox[0] = int(bbox[0] * 1000.0 / width)
        bbox[2] = int(bbox[2] * 1000.0 / width)
        bbox[1] = int(bbox[1] * 1000.0 / height)
        bbox[3] = int(bbox[3] * 1000.0 / height)

        # Tokenize text information, bao gồm tokenization và chuyển sang index trong vocabulary
        text = info["text"]
        encode_res = tokenizer.encode(
            text, pad_to_max_seq_len=False, return_attention_mask=True)

        # Quyết định có xóa special characters theo tham số hay không
        if not add_special_ids:
            encode_res["input_ids"] = encode_res["input_ids"][1:-1]
            encode_res["token_type_ids"] = encode_res["token_type_ids"][1:-1]
            encode_res["attention_mask"] = encode_res["attention_mask"][1:-1]

        input_ids_list.extend(encode_res["input_ids"])
        token_type_ids_list.extend(encode_res["token_type_ids"])
        bbox_list.extend([bbox] * len(encode_res["input_ids"]))
        segment_offset_id.append(len(input_ids_list))

    encoded_inputs = {
        "input_ids": input_ids_list,
        "token_type_ids": token_type_ids_list,
        "bbox": bbox_list,
        "attention_mask": [1] * len(input_ids_list),
    }
    # Pad giá trị về chiều dài cụ thể, dùng 0 để bổ sung nếu không đủ
    encoded_inputs = pad_sentences(
        tokenizer,
        encoded_inputs,
        max_seq_len=max_seq_len,
        return_attention_mask=return_attention_mask)

    # Nếu input_ids > 512, chia thành 2 batches
    ncoded_inputs = split_page(encoded_inputs)

    fake_bs = encoded_inputs["input_ids"].shape[0]

    encoded_inputs["image"] = paddle.to_tensor(img).unsqueeze(0).expand(
        [fake_bs] + list(img.shape))

    encoded_inputs["segment_offset_id"] = segment_offset_id

    return encoded_inputs
```

```python
img = cv2.imread('images/input/zh_val_42.jpg')

ocr_engine = PaddleOCR(use_angle_cls=False, show_log=False)
# Thực hiện OCR recognition
ocr_result = ocr_engine.ocr(img, cls=False)
# Kết quả OCR được chuyển sang format dictionary, text box được chuyển thành bounding rectangle
ocr_info = parse_ocr_info_for_ser(ocr_result)

tokenizer = LayoutXLMTokenizer.from_pretrained('pretrained_models/PP-Layout_v1.0_ser_pretrained')
# Resize ảnh, tokenize text, chuyển sang dictionary index, normalize box
max_seq_length = 512
inputs = preprocess(tokenizer=tokenizer, ori_img=img, ocr_info=ocr_info, max_seq_len=max_seq_length, img_size=(224, 224))

print(inputs.keys())
print(inputs['image'].shape)
```

Output:
```
dict_keys(['input_ids', 'token_type_ids', 'bbox', 'attention_mask', 'image', 'segment_offset_id'])
[2, 3, 224, 224]
```

Dữ liệu đã xử lý là dictionary chứa các trường:

| Trường | Ý nghĩa |
|--------|---------|
| `image` | Ảnh đã resize thành 224*224 |
| `bbox` | Box đã normalize về 0-1000 |
| `input_ids` | Index của tokenized text segment trong vocabulary |
| `token_type_ids` | Category information của text segment |
| `attention_mask` | Mask text segment, đánh dấu vị trí special character là 0 và text segment là 1 |
| `segment_offset_id` | Ghi lại vị trí kết thúc của mỗi text trong input_ids |

#### SER Network

SER là Semantic Entity Recognition, có thể nhận dạng và phân loại texts trong ảnh. Một fully connected classification head được thêm vào output của SER network LayoutXLMModel:

```python
# https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/transformers/layoutxlm/modeling.py#L846
from paddlenlp.transformers import LayoutXLMPretrainedModel
from paddle import nn

class LayoutXLMForTokenClassification(LayoutXLMPretrainedModel):
    def __init__(self, layoutxlm, num_classes=2, dropout=None):
        super(LayoutXLMForTokenClassification, self).__init__()
        self.num_classes = num_classes
        if isinstance(layoutxlm, dict):
            self.layoutxlm = LayoutXLMModel(**layoutxlm)
        else:
            self.layoutxlm = layoutxlm
        self.dropout = nn.Dropout(dropout if dropout is not None else self.layoutxlm.config["hidden_dropout_prob"])
        self.classifier = nn.Linear(self.layoutxlm.config["hidden_size"], num_classes)
        self.classifier.apply(self.init_weights)

    def get_input_embeddings(self):
        return self.layoutxlm.embeddings.word_embeddings

    def forward(self, input_ids=None, bbox=None, image=None, attention_mask=None,
                token_type_ids=None, position_ids=None, head_mask=None, labels=None):
        # Tính backbone
        outputs = self.layoutxlm(input_ids=input_ids, bbox=bbox, image=image,
                                  attention_mask=attention_mask, token_type_ids=token_type_ids,
                                  position_ids=position_ids, head_mask=head_mask)
        seq_length = input_ids.shape[1]
        # Tính head
        sequence_output, image_output = outputs[0][:, :seq_length], outputs[0][:, seq_length:]
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)

        outputs = logits,

        # Tính loss
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()

            if attention_mask is not None:
                active_loss = attention_mask.reshape([-1, ]) == 1
                active_logits = logits.reshape([-1, self.num_classes])[active_loss]
                active_labels = labels.reshape([-1, ])[active_loss]
                loss = loss_fct(active_logits, active_labels)
            else:
                loss = loss_fct(logits.reshape([-1, self.num_classes]), labels.reshape([-1, ]))
            outputs = (loss, ) + outputs
        return outputs
```

```python
# Khởi tạo network
net = LayoutXLMForTokenClassification.from_pretrained('pretrained_models/PP-Layout_v1.0_ser_pretrained')
net.eval()
# Thực hiện network forward
outputs = net(input_ids=inputs["input_ids"],
              bbox=inputs["bbox"],
              image=inputs["image"],
              token_type_ids=inputs["token_type_ids"],
              attention_mask=inputs["attention_mask"])
print(outputs[0].shape)
```

Output: `[2, 512, 7]` — 2 batches, 512 tokens, 7 classes (O, B-QUESTION, I-QUESTION, B-ANSWER, I-ANSWER, B-HEADER, I-HEADER).

#### Post-Processing (Hậu xử lý)

Hậu xử lý chủ yếu match kết quả suy luận của text segment output bởi model với text, và kết hợp kết quả suy luận với kết quả OCR. Gồm các bước:

1. Với mỗi text, đếm inferred labels của tất cả text segments thuộc text đó
2. Chọn label có nhiều inference nhất của tất cả text segments làm label của text

```python
import paddle
import numpy as np
from infer_ser_e2e import get_bio_label_maps

label2id_map, id2label_map = get_bio_label_maps('labels/labels_ser.txt')

def postprocess(attention_mask, preds, id2label_map):
    if isinstance(preds, paddle.Tensor):
        preds = preds.numpy()
    preds = np.argmax(preds, axis=2)

    preds_list = [[] for _ in range(preds.shape[0])]

    # Giữ batch info
    for i in range(preds.shape[0]):
        for j in range(preds.shape[1]):
            if attention_mask[i][j] == 1:
                preds_list[i].append(id2label_map[preds[i][j]])

    return preds_list

def merge_preds_list_with_ocr_info(ocr_info, segment_offset_id, preds_list,
                                    label2id_map_for_draw):
    # List flatten
    preds = [p for pred in preds_list for p in pred]

    # Chuyển dictionary label2idx sang idx2label, loại bỏ prefix B- và I-
    id2label_map = dict()
    for key in label2id_map_for_draw:
        val = label2id_map_for_draw[key]
        if key == "O":
            id2label_map[val] = key
        if key.startswith("B-") or key.startswith("I-"):
            id2label_map[val] = key[2:]
        else:
            id2label_map[val] = key
    print("id2label_map:", id2label_map)

    # Đếm inferred label của mỗi text
    for idx in range(len(segment_offset_id)):
        if idx == 0:
            start_id = 0
        else:
            start_id = segment_offset_id[idx - 1]

        end_id = segment_offset_id[idx]
        # Lấy phạm vi text trong output
        curr_pred = preds[start_id:end_id]
        # Lấy tất cả inference results của text trong output
        curr_pred = [label2id_map_for_draw[p] for p in curr_pred]

        if len(curr_pred) <= 0:
            pred_id = 0
        else:
            # Đếm label
            counts = np.bincount(curr_pred)
            pred_id = np.argmax(counts)
        ocr_info[idx]["pred_id"] = int(pred_id)
        ocr_info[idx]["pred"] = id2label_map[int(pred_id)]
    return ocr_info
```

Output ví dụ:
```
label2id_map: {'O': 0, 'B-QUESTION': 1, 'I-QUESTION': 2, 'B-ANSWER': 3, 'I-ANSWER': 4, 'B-HEADER': 5, 'I-HEADER': 5}
label2id_map_for_draw: {'O': 0, 'B-QUESTION': 1, 'I-QUESTION': 1, 'B-ANSWER': 3, 'I-ANSWER': 3, 'B-HEADER': 5, 'I-HEADER': 5}
id2label_map: {0: 'O', 1: 'QUESTION', 3: 'ANSWER', 5: 'HEADER'}
result: [
{'text': '申报学院（部门）：', 'bbox': [1026.0, 292.0, 1495.0, 377.0], ..., 'pred_id': 5, 'pred': 'HEADER'},
{'text': '个人信息登记表', 'bbox': [207.0, 424.0, 587.0, 475.0], ..., 'pred_id': 1, 'pred': 'QUESTION'},
{'text': '姓名', 'bbox': [1144.0, 526.0, 1218.0, 566.0], ..., 'pred_id': 1, 'pred': 'QUESTION'}
...
]
```

### 8.3.3 Training (Huấn luyện — trang 264–269)

Phần này lấy XFUN Chinese dataset làm ví dụ để giới thiệu cách huấn luyện, đánh giá và test SER model.

#### Chuẩn bị dữ liệu

XFUN dataset là multilingual dataset đề xuất bởi Microsoft cho KIE tasks. Chứa 7 datasets, mỗi dataset có 149 training sets và 50 validation sets:
- ZH (Chinese), JA (Japanese), ES (Spanish), FR (French), IT (Italian), DE (German), PT (Portuguese)

Thí nghiệm này dùng Chinese dataset để demo và French dataset cho khóa thực hành.

```bash
! wget https://paddleocr.bj.bcebos.com/dataset/XFUND.tar
! tar -xf XFUND.tar
```

Cấu trúc thư mục:
```
/home/aistudio/PaddleOCR/ppstructure/vqa/XFUND
├── zh_train/ training set
│   ├── image/                    image storage folder
│   ├── xfun_normalize_train.json label information
└── zh_val/ verification set
    ├── image/                    image storage folder
    ├── xfun_normalize_val.json   label information
```

Format label:
```json
{
    "height": 3508,    // Image height
    "width": 2480,     // Image width
    "ocr_info": [
        {
            "text": "开票日期：",   // Nội dung text
            "label": "question",  // Category của text
            "bbox": [261, 802, 483, 859],  // Text box
            "id": 54,             // Text Index
            "linking": [[54, 60]], // Mối quan hệ giữa text hiện tại và texts khác (question, answer)
            "words": []
        },
        {
            "text": "检验检疫费弍佰肆拾",
            "label": "answer",
            "bbox": [487, 810, 862, 859],
            "id": 60,
            "linking": [[54, 60]],
            "words": []
        }
    ]
}
```

#### Loss Function

Vì đây là bài toán classification, chọn **CrossEntropyLoss** làm loss function.

#### Model Training

Sau khi xử lý dữ liệu và định nghĩa loss function, có thể bắt đầu huấn luyện model:

```bash
! python train_ser.py \
    --model_name_or_path "layoutxlm-base-uncased" \
    --ser_model_type "LayoutXLM" \
    --train_data_dir "XFUND/zh_train/image" \
    --train_label_path "XFUND/zh_train/xfun_normalize_train.json" \
    --eval_data_dir "XFUND/zh_val/image" \
    --eval_label_path "XFUND/zh_val/xfun_normalize_val.json" \
    --per_gpu_train_batch_size 8 \
    --per_gpu_eval_batch_size 8 \
    --num_train_epochs 200 \
    --eval_steps 10 \
    --output_dir "./output/ser/" \
    --learning_rate 5e-5 \
    --warmup_steps 50 \
    --evaluate_during_training \
    --num_workers 0 \
    --seed 2048
```

Training log hiển thị: 149 samples, 200 epochs, batch size 8, total 3800 optimization steps. Loss giảm dần từ ~1.98 → ~1.60 qua 10 iterations đầu tiên.

Kết quả evaluation đầu tiên (sau 10 steps — mới epoch 0):
```
             precision    recall  f1-score   support
  ANSWER         0.01      0.01      0.01      1514
  HEADER         0.00      0.00      0.00        58
QUESTION         0.03      0.02      0.02      1155

micro avg         0.02      0.01      0.01      2727
macro avg         0.01      0.01      0.01      2727
weighted avg      0.02      0.01      0.01      2727

f1 = 0.013078227173649792
loss = 1.5786780970437186
precision = 0.01925820256776034
recall = 0.009900990099009901
```

(Lưu ý: đây chỉ là kết quả epoch 0 — model cần training nhiều epoch hơn để đạt accuracy tốt)

#### Model Evaluation (Đánh giá model)

Trong quá trình training, hai models được lưu mặc định: `latest_model` và `best_model`. Cấu trúc thư mục lưu model:

```
output/ser/
├── best_model
│   ├── model_config.json        # Model configuration
│   ├── model_state.pdparams     # Model parameters
│   ├── sentencepiece.bpe.model  # Parameters of tokenizer
│   ├── tokenizer_config.json    # Tokenizer configuration
│   └── training_args.bin        # Parameters for starting training
├── infer_results.txt
├── latest_model
│   ├── model_config.json
│   ├── model_state.pdparams
│   ├── sentencepiece.bpe.model
│   ├── tokenizer_config.json
│   └── training_args.bin
├── test_gt.txt
├── test_pred.txt
└── train.log                    # Training log
```

Dùng model parameters đã lưu để đánh giá accuracy trên test set:

```bash
! python eval_ser.py \
    --model_name_or_path "output/ser/best_model" \
    --ser_model_type "LayoutXLM" \
    --eval_data_dir "XFUND/zh_val/image" \
    --eval_label_path "XFUND/zh_val/xfun_normalize_val.json" \
    --per_gpu_eval_batch_size 8 \
    --num_workers 8 \
    --output_dir "output/ser/" \
    --seed 2048
```

#### Model Inference (Suy luận model)

Sau khi huấn luyện, dùng model đã lưu để suy luận trên ảnh đơn:

```bash
! python infer_ser_e2e.py \
    --model_name_or_path "./pretrained_models/PP-Layout_v1.0_ser_pretrained/" \
    --ser_model_type "LayoutXLM" \
    --max_seq_length 512 \
    --output_dir "output/ser_e2e/" \
    --infer_imgs "images/input/zh_val_42.jpg"
```

Output:
```
process: [0/1], save result to output/ser_e2e/zh_val_42_ser.jpg
```

### 8.3.4 Bài tập

Experiment: https://aistudio.baidu.com/aistudio/projectdetail/3281385

---

---

# Chương 9 — Thuật toán End-to-End (trang 271–285)

## 9.1 Background (Nền tảng)

Thuật toán OCR chủ yếu gồm hai loại: thuật toán two-stage và thuật toán end-to-end. Thuật toán OCR two-stage bao gồm hai tasks: text detection và text recognition. Thuật toán text detection định vị vùng text của input image, và thuật toán text recognition nhận dạng nội dung text trong ảnh. Về cơ bản, thuật toán OCR end-to-end nhằm tích hợp detection và recognition trong một unified framework. Hai phần chia sẻ cùng backbone network nhưng có specialized modules cho detection và recognition, để có thể được huấn luyện cùng lúc. Thuật toán end-to-end đơn giản hóa quy trình, do đó model nhỏ hơn và tốc độ xử lý nhanh hơn.

Trong phần này, chúng ta giới thiệu một số phương pháp end-to-end text recognition dựa trên deep learning gần đây. Các approaches có thể chia thành hai loại:

1. End-to-end regular text recognition (nhận dạng text thông thường)
2. End-to-end arbitrary-shaped text recognition (nhận dạng text hình dạng tùy ý)

Thuật toán end-to-end regular text recognition chủ yếu xử lý detection và recognition text ngang hoặc đa hướng. Tuy nhiên, có nhiều text cong và biến dạng trong natural scenes, như con dấu. Để detect và recognize các texts này, cần thuật toán end-to-end arbitrary-shaped text recognition. Đồng thời, các thuật toán này cũng có thể xử lý regular texts.

| Phương pháp | Bài báo chính |
|---|---|
| End-to-end regular text recognition | FOTS, TextSpotter |
| End-to-end arbitrary-shaped text recognition | Mask TextSpotterv1, Mask TextSpotter2, Mask TextSpotterv3, TextDragon, CharNet, TUTS, ABCNet, ABCNetV2, Text Perceptron, PGNet, PAN++ |

## 9.2 Algorithms (Thuật toán)

### 9.2.1 Thuật toán End-to-end Regular Text Recognition

#### FOTS

Xuebo Liu và Ding Liang et al. (2018) [1] đề xuất FOTS (Fast Oriented Text Spotting) — unified end-to-end trainable network cho simultaneous detection và recognition. Kiến trúc network gồm 4 phần:

1. **Shared convolutions** để trích xuất feature maps. Bằng cách chia sẻ convolutional features, network có thể detect và recognize text đồng thời với ít computation overhead, đạt tốc độ real-time.
2. **Text detection branch** dựa trên fully convolutional network (FCN), sau khi feature maps được trích xuất, dự đoán detection bounding boxes.
3. **RoIRotate operator** trích xuất oriented text regions từ convolutional feature maps. Thao tác này hợp nhất text detection và recognition thành end-to-end pipeline.
4. **Text proposal features** được đưa vào Recurrent Neural Network (RNN) encoder và Connectionist Temporal Classification (CTC) decoder cho text recognition.

Vì tất cả modules trong network là differentiable, toàn bộ hệ thống có thể được trained end-to-end, không cần complicated post-processing và hyperparameter tuning.

Tác giả đã thực hiện thí nghiệm trên ICDAR 2015, ICDAR 2017 MLT và ICDAR 2013 datasets.

#### TextSpotter

Tong He et al. (2018) [2] đề xuất TextSpotter — model đơn giản nhưng hiệu quả. Detection model là fully convolution architecture xây dựng trên PVAnet framework và giới thiệu recurrent branch mới cho word recognition. TextSpotter có thể xử lý detection và recognition trong một lần. RNN branch gồm text-alignment layer mới và LSTM-based recurrent module với novel character attention embedding mechanism.

Phương pháp này phát triển text-alignment layer bằng grid sampling scheme thay vì conventional RoI pooling. Nó tính toán fixed-length convolutional features align chính xác với detected text region theo bất kỳ hướng nào. Character attention mechanism dùng character spatial information làm additional supervision, giúp RNN focus vào current attentional features. Cuối cùng, TextSpotter dùng learning strategy cho phép text detection và recognition work collaboratively bằng cách chia sẻ convolutional features.

Tác giả thí nghiệm trên ICDAR2013 và ICDAR2015 datasets.

### 9.2.2 Thuật toán End-to-end Arbitrary-shaped Text Recognition

#### Mask TextSpotter (v1)

Pengyuan Lyu và Minghui Liao et al. (2018) [3] đề xuất Mask TextSpotter — end-to-end trainable neural network model cho scene text spotting. Nó có thể detect và recognize text instances trong arbitrary shapes (horizontal, oriented, hoặc curved), không giống một số phương pháp chỉ detect và recognize horizontal texts hoặc oriented texts.

Lấy cảm hứng từ Mask R-CNN, Mask TextSpotter có thể detect text bằng segment the instance text regions, từ đó detect text của arbitrary shapes. Kiến trúc network bao gồm RPN, Fast R-CNN (Box Classification + Box Regression), và Mask branch (Word segmentation + Character instance segmentation).

Tác giả thí nghiệm trên ICDAR2013, ICDAR2015 và Total-Text datasets.

#### Mask TextSpotter V2

Minghui Liao et al. (2019) [4] đề xuất Mask TextSpotter V2 dựa trên Mask TextSpotter. Mask TextSpotter nhận dạng single characters, yêu cầu positions của characters trong training, và cần post-processing algorithm để yield text sequence. Để khắc phục các hạn chế này, Mask TextSpotter V2 giới thiệu **Spatial Attention Module (SAM)** cho recognition part, có thể globally predict label sequence của mỗi word bằng spatial attention mechanism. SAM chỉ yêu cầu word-level annotations cho training, giảm đáng kể nhu cầu character-level annotations.

Tác giả thí nghiệm trên 5 datasets: ICDAR 2013, ICDAR 2015, COCO-Text, Total-Text, và MIT.

#### Mask TextSpotter V3

Minghui Liao et al. (2020) [5] đề xuất Mask TextSpotter V3 dựa trên V1 và V2. Trong các phiên bản trước, text detection module dựa trên Mask R-CNN và không detect được long text lines do hạn chế của RPN. Thay vì dùng RPN, tác giả dùng **Segmentation Proposal Network (SPN)** trong V3. SPN vượt trội hơn RPN trong detecting text instances có extreme aspect ratios hoặc irregular shapes. Tác giả cũng đề xuất **hard RoI masking**, có thể effectively suppress neighboring text instances hoặc background noise.

Tác giả thí nghiệm trên Rotated ICDAR 2013, Total-Text, và MSRA-TD500 datasets.

#### TextDragon

Wei Feng et al. (2019) [6] đề xuất TextDragon — novel text spotting framework chỉ dùng word/line-level annotations cho training. Trong TextDragon, text detector được thiết kế để mô tả hình dạng text bằng chuỗi quadrangles, có thể handle text của arbitrary shapes. Để trích xuất arbitrary text regions từ feature maps, TextDragon thiết kế differentiable operator mới tên **RoISlide** — đây là key để kết nối arbitrary shaped text detection và recognition. Dựa trên extracted features qua RoISlide, CNN và CTC based text recognizer được giới thiệu, giúp framework không cần labeling vị trí characters. Model chỉ cần word/line level annotations thay vì positions của annotated characters.

Tác giả thí nghiệm trên CTW1500, Total-Text, và ICDAR 2015 datasets.

#### CharNet

Linjie Xing et al. (2019) [7] đề xuất Convolutional Character Networks (CharNet) cho end-to-end text detection và recognition. CharNet giới thiệu nhánh mới direct character detection và recognition, có thể được tích hợp vào existing text detection framework. Tác giả cũng khám phá characters as basic unit, khắc phục hạn chế của RoI pooling và RNN recognition module trong two-stage framework hiện tại. Ngoài ra, iterative character detection method được đề xuất, cho phép CharNet chuyển character detection capabilities từ synthetic data sang real world images. Điều này giúp huấn luyện CharNet trên real world images mà không cần additional annotations ở character-level bounding boxes.

Tác giả thí nghiệm trên ICDAR 2015, Total-Text và ICDAR MLT 2017.

#### TUTS

Siyang Qin et al. (2019) [8] đề xuất TUTS — end-to-end trainable model. TUTS là simple và flexible OCR model dựa trên Mask R-CNN detector và sequence-to-sequence (seq2seq) attention decoder. Phương pháp có thể detect và recognize text của arbitrary shape, và đề xuất simple và effective **RoI masking step** nhằm lấy useful irregularly shaped text instance features từ image scale features. Ngoài ra, partially labeled data được tự động labeled bởi existing multi-stage OCR engine, giúp greatly optimize model detection và recognition results.

Tác giả thí nghiệm trên ICDAR2015 và Total-Text.

#### ABCNet

Yuliang Liu et al. (2020) [9] đề xuất ABCNet (Adaptive Bezier-Curve Network) — end-to-end trainable model cho arbitrary-shaped texts. Lần đầu tiên, tác giả đưa ra concise parametric representation mới cho curved scene text dùng **Bezier curves**. Đồng thời thiết kế novel **BezierAlign** layer để extracting accurate convolutional features của text instance với arbitrary shapes. Computation overhead của Bezier curve detection method là negligible so với standard detection methods. Bằng cách sharing backbone features, recognition branch có thể được thiết kế lightweight. ABCNet gồm 2 phần: 1) Bezier curve detection; 2) BezierAlign và recognition branch.

Tác giả thí nghiệm trên Total-Text và CTW1500.

#### ABCNet V2

Yuliang Liu et al. (2021) [10] đề xuất ABCNet v2 dựa trên ABCNet với cải tiến ở 4 khía cạnh: feature extractor, detection branch, recognition branch và end-to-end training — đạt state-of-the-art performance với very high efficiency. Detection model tổng quát hơn cho multi-scale text instances bằng bidirectional multi-scale pyramidal global text features. Trong recognition branch, **character attention module** được tích hợp để recursively predict characters mà không cần character-level annotations. Tác giả đề xuất **Adaptive end-to-end training (AET)** strategy cho effective end-to-end training.

Tác giả thí nghiệm trên ICDAR 2015, MSRA-TD500, ReCTS, Total-Text, và SCUT-CTW1500.

#### Text Perceptron

Liang Qiao et al. (2020) [11] đề xuất Text Perceptron — end-to-end trainable arbitrary-shaped text recognition method. Model gồm 3 phần:
1. **Efficient segmentation-based detection module** dùng ResNet và FPN làm backbone, mô tả text region thành 4 subregions: central region, head, tail, top&bottom boundary regions. Boundary information không chỉ giúp tách text regions gần nhau, mà còn capture latent reading-orders.
2. Novel **Shape Transform Module (STM)** biến đổi detected feature regions thành morphologies mà không cần extra parameters, tích hợp irregular text detection và recognition thành end-to-end trainable model.
3. Sequence-based recognition module để generate final character sequences.

Tác giả thí nghiệm trên SynthText 800k, ICDAR2013, ICDAR2015, Total-Text và CTW1500.

#### PGNet

Pengfei Wang et al. (2021) [12] đề xuất PGNet (Point Gathering Network) — novel fully convolutional architecture. Input image được tích hợp thành 4 nhánh sau feature extraction: TBO (Text Border Offset), TCL (Text Center Line), TDO (Text Direction Offset), và TCC map (Text Character Classification). Input của TBO và TCL tạo text detection result sau post-processing, và TCL, TDO, TCC dùng cho text recognition.

PGNet có ưu điểm riêng: thiết kế PGNet loss để hướng dẫn training mà không cần character-level annotations, tăng tốc inference mà không cần NMS và ROI operations, đề xuất module suy luận reading order trong text lines, và graph refinement module (GRM) cải thiện model recognition. Thuật toán này chính xác và nhanh hơn trong inference.

Tác giả thí nghiệm trên ICDAR2015 và Total-Text.

#### PAN++

Wenhai Wang et al. (2021) [13] đề xuất PAN++ — end-to-end text recognition algorithm, có thể effectively detect và recognize arbitrary-shaped texts trong natural scenes. PAN++ dựa trên **kernel representation** — reformulate text line thành text kernel (central region) được bao quanh bởi peripheral pixels, giúp phân biệt tốt adjacent texts. Hơn nữa, kernel representation có thể được predicted bởi single fully convolutional network, rất thân thiện với real-time applications.

Tận dụng kernel representation, tác giả thiết kế: 1) efficient feature enhancement network gồm stacked Feature Pyramid Enhancement Modules (FPEMs); 2) lightweight detection head cooperating với Pixel Aggregation (PA); 3) efficient attention-based recognition head với Masked RoI.

Tác giả thí nghiệm trên Total-Text, CTW1500, ICDAR2015, MSRA-TD500, và RCTW-17.

## 9.3 Summary (Tổng kết)

OCR text detection và recognition là basic task của nhiều ứng dụng như text retrieval và office automation. Hầu hết công trình hiện có coi text detection và recognition là hai separate tasks. Không có shared feature giữa hai tasks và training hai models tốn thời gian. Gần đây, một số phương pháp committed vào end-to-end text recognition, nhằm detect và recognize text đồng thời trong một network.

Tóm tắt các phương pháp end-to-end text recognition dựa trên deep learning, chia thành 2 loại:
1. **End-to-end regular text recognition**: FOTS và TextSpotter — chủ yếu cho regular text detection và recognition
2. **End-to-end arbitrary shape text recognition**: Mask TextSpotterv1/v2/v3, TextDragon, CharNet, TUTS, ABCNet, ABCNetV2, PGNet, PAN++ — cho arbitrary shape text detection và recognition

---

---

# Chương 10 — Thuật toán Tiền xử lý (Pre-processing Algorithm) (trang 287–293)

## 10.1 Background (Nền tảng)

Trong OCR text detection và recognition, chất lượng ảnh ảnh hưởng trực tiếp đến hiệu năng detection và recognition. Ảnh chất lượng thấp thường gặp vấn đề như nghiêng, gấp, mờ, virtual scene, v.v. Do đó, image preprocessing là phần quan trọng cho OCR. Phần này tập trung vào các thuật toán phổ biến của data augmentation, image binarization và denoising trong image preprocessing.

**Data augmentation** là kỹ thuật phổ biến trong deep learning, tăng số lượng và đa dạng mẫu bằng cách biến đổi training data để tăng cường generalization ability của model. **Image binarization** biến đổi ảnh thành black-white, tách text khỏi background, thuận lợi cho text detection và recognition. **Denoising** loại bỏ nhiễu (salt-and-pepper noise, Gaussian noise, v.v.) trong ảnh. Binarization và denoising là preprocessing algorithms phổ biến trong traditional OCR, hoạt động tốt trên printed và scanned documents.

| Data Augmentation | Methods |
|---|---|
| Standard data augmentation | Rotation, perspective transformation, blurring, Gaussian noise, random cropping, v.v. |
| Image transformation | AutoAugment, RandAugment, TimmAutoAugment |
| Image cropping | CutOut, RandErasing, HideAndSeek, GridMask |
| Image mixture | Mixup, Cutmix |

| Binarization | Methods |
|---|---|
| Global thresholding | Fixed thresholding, Otsu |
| Local thresholding | Adaptive thresholding, NiBlack, Sauvola, Bernsen |
| Deep learning | U-Net, Grid LSTM, Full Convolutional Neural Networks, v.v. |

| Denoising | Methods |
|---|---|
| Spatial domain filtering | Mean filtering, Gaussian filtering, median filtering, bilateral filtering, non-local means algorithm (NLM) |
| Transform domain filtering | Fourier transform, wavelet transform |
| BM3D | BM3D |
| Deep learning | DnCNNs, FFDNet, MPRNet |

## 10.2 Data Augmentation (trang 288–293)

OCR handwritten và scene text detection và recognition gặp nhiều vấn đề: different forms, complex background, fuzzy text, v.v. Do đó, training robust recognition model đòi hỏi lượng lớn data cover nhiều scenes. So với data collection và annotation, data augmentation là cách ít tốn kém hơn để cải thiện robustness model.

Phần này tập trung vào một số phương pháp data augmentation standard và một số augmentation methods cải tiến. Chia thành 4 loại:

1. **Common data augmentation methods**: rotation, perspective transformation, blur, Gaussian noise, randCrop, v.v.
2. **Image transformation**: transform ảnh sau RandCrop — AutoAugment, RandAugment
3. **Image cropping techniques**: crop ảnh sau transposition — CutOut, RandErasing, HideAndSeek, GridMask
4. **Image mixing techniques**: mix data sau batch processing — Mixup, Cutmix

### 10.2.1 Standard Data Augmentation

**1. Colour space transformation (cvtColor):** chuyển ảnh từ không gian màu này sang không gian màu khác.

```python
def cvtColor(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    delta = 0.001 * random.random() * flag()
    hsv[:, :, 2] = hsv[:, :, 2] * (1 + delta)
    new_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return new_img
```

**2. Blur:** hiệu ứng blur bằng cách giảm sự khác biệt pixel values. Dùng `cv2.GaussianBlur` — tham số gồm image array, width và height của kernel, standard deviation. Kernel càng lớn, ảnh càng mờ.

```python
def blur(img):
    h, w, _ = img.shape
    if h > 10 and w > 10:
        return cv2.GaussianBlur(img, (5, 5), 1)
    else:
        return img
```

**3. Jitter:** hiệu ứng jitter bằng cách randomly thay đổi pixel values.

```python
def jitter(img):
    w, h, _ = img.shape
    if h > 10 and w > 10:
        thres = min(w, h)
        s = int(random.random() * thres * 0.01)
        src_img = img.copy()
        for i in range(s):
            img[i:, i:, :] = src_img[:w - i, :h - i, :]
        return img
    else:
        return img
```

**4. Noise:** Noise là yếu tố unpredictable trong real images, thêm noise vào real data simulation là data augmentation method đơn giản và hiệu quả. Các phương pháp phổ biến: Gaussian noise, pretzel noise, v.v. Ở đây dùng Gaussian noise — `mean` là mean value, `var` là variance. Variance càng lớn, noise càng mạnh.

```python
def add_gasuss_noise(image, mean=0, var=0.1):
    noise = np.random.normal(mean, var**0.5, image.shape)
    out = image + 0.5 * noise
    out = np.clip(out, 0, 255)
    out = np.uint8(out)
    return out
```

**5. Random Crop:** randomly chọn một region từ ảnh và crop. Với text recognition, do height ảnh nhỏ, set `top_min` và `top_max` để limit cropping size.

```python
def get_crop(image):
    h, w, _ = image.shape
    top_min = 1
    top_max = 8
    top_crop = int(random.randint(top_min, top_max))
    top_crop = min(top_crop, h - 1)
    crop_img = image.copy()
    ratio = random.randint(0, 1)
    if ratio:
        crop_img = crop_img[top_crop:h, :, :]
    else:
        crop_img = crop_img[0:h - top_crop, :, :]
    return crop_img
```

**6. Perspective transformation:** chiếu ảnh lên một plane mới bằng projection matrix. Dùng `WarpMLS` để randomly dịch chuyển 4 corner points.

```python
from warp_mls import WarpMLS

def tia_perspective(src):
    img_h, img_w = src.shape[:2]
    thresh = img_h // 2
    src_pts = [[0, 0], [img_w, 0], [img_w, img_h], [0, img_h]]
    dst_pts = [
        [0, np.random.randint(thresh)],
        [img_w, np.random.randint(thresh)],
        [img_w, img_h - np.random.randint(thresh)],
        [0, img_h - np.random.randint(thresh)]
    ]
    trans = WarpMLS(src, src_pts, dst_pts, img_w, img_h)
    dst = trans.generate()
    return dst
```

**7. Colour Reverse:** đảo ngược màu ảnh bằng cách trừ original pixel value từ maximum value grayscale level. Sau inversion, vùng sáng trở nên tối hơn và vùng tối trở nên sáng hơn.

```python
def reverse(img):
    new_img = 255 - img
    return new_img
```

**8. TIA [1]:** phương pháp data augmentation hiệu quả khác, khởi tạo tập datum points trong ảnh, rồi randomly dịch chuyển các points này qua geometric transformation để tạo ảnh mới. Ví dụ: từ "Safety" được biến dạng thành nhiều biến thể khác nhau bằng cách di chuyển control points.

---

*— Hết phần dịch trang 250–300 —*

Phần tiếp theo (trang 300+) sẽ tiếp tục với:
- 10.2 (tiếp) Data Augmentation nâng cao: AutoAugment, RandAugment, CutOut, RandErasing, Mixup, Cutmix
- 10.3 Image Binarization
- 10.4 Image Denoising
- Chương 11+ (nếu có)

**Tài nguyên:**
- Repo: https://github.com/PaddlePaddle/PaddleOCR
- PP-Structure VQA: PaddleOCR/ppstructure/vqa/
- End-to-end algorithms: PaddleOCR/doc/doc_en/pgnet.md
