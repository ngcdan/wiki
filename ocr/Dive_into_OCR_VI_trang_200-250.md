# Dive into OCR — Bản dịch tiếng Việt (Trang 200–250)

*Tiếp nối từ file dịch trang 150–200. Đây là bản dịch đầy đủ bằng tiếng Việt. Technical terms giữ nguyên tiếng Anh.*

> Tài liệu gốc: https://github.com/PaddlePaddle/PaddleOCR (release/2.4)

---

## 7.2.5 Suy luận End-to-end PP-OCRv2 (tiếp — trang 194–198)

Nếu sử dụng direction classifier cho suy luận end-to-end, bạn có thể dùng lệnh sau:

```python
# Sử dụng direction classifier để chạy hệ thống PP-OCRv2
!python tools/infer/predict_system.py \
    --image_dir="./doc/imgs/00018069.jpg" \
    --det_model_dir="./inference/ch_PP-OCRv2_det_infer/" \
    --cls_model_dir="./inference/ch_ppocr_mobile_v2.0_cls_infer/" \
    --rec_model_dir="./inference/ch_PP-OCRv2_rec_infer/" \
    --use_angle_cls=True

# Hiển thị kết quả
img = cv2.imread("./inference_results/00018069.jpg")
plt.figure(figsize=(20, 8))
plt.imshow(img[..., ::-1])
plt.show()
```

Kết quả visualization được lưu mặc định vào thư mục `./inference_results`. Khung phát hiện và kết quả nhận dạng được hiển thị trực quan trên ảnh, đồng thời thông tin file đã nhận dạng cũng được in ra.

Nếu bạn muốn lưu kết quả nhận dạng đã crop, hãy set tham số `save_crop_res=True`, kết quả cuối cùng được lưu vào thư mục `output`. Các ảnh đã crop có thể được dùng để gán nhãn và huấn luyện model recognition.

```python
# Cắt ảnh kết quả text detection và lưu lại
!python tools/infer/predict_system.py \
    --image_dir="./doc/imgs/00018069.jpg" \
    --det_model_dir="./inference/ch_PP-OCRv2_det_infer/" \
    --cls_model_dir="./inference/ch_ppocr_mobile_v2.0_cls_infer/" \
    --rec_model_dir="./inference/ch_PP-OCRv2_rec_infer/" \
    --use_angle_cls=True \
    --save_crop_res=True
```

Suy luận end-to-end được thực hiện bởi class `TextSystem`. Quy trình và định nghĩa hàm như sau:

```python
# Reference Code: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.4/tools/infer/predict_system.py
from tools.infer.utility import draw_ocr_box_txt, get_rotate_crop_image
from ppocr.utils.utility import get_image_file_list

class TextSystem(object):
    # Khởi tạo hàm
    def __init__(self, args):
        self.args = args
        # Nếu không muốn hiển thị log, set show_log = False
        if not args.show_log:
            logger.setLevel(logging.INFO)
        # Định nghĩa engine suy luận text detection
        self.text_detector = TextDetector(args)
        # Định nghĩa engine suy luận text recognition
        self.text_recognizer = TextRecognizer(args)
        # Có sử dụng direction classifier hay không
        self.use_angle_cls = args.use_angle_cls
        # Ngưỡng confidence score, xác định kết quả detection và recognition
        # có cần được hiển thị hoặc trả về hay không
        self.drop_score = args.drop_score
        # Định nghĩa engine suy luận direction classifier
        if self.use_angle_cls:
            self.text_classifier = TextClassifier(args)

    # Lưu ảnh kết quả text detection
    def draw_crop_rec_res(self, output_dir, img_crop_list, rec_res):
        os.makedirs(output_dir, exist_ok=True)
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite(
                os.path.join(output_dir,
                             f"mg_crop_{bno+self.crop_image_res_index}.jpg"),
                img_crop_list[bno])
            logger.debug(f"{bno}, {rec_res[bno]}")
        self.crop_image_res_index += bbox_num

    # Hàm suy luận chính (core inference function)
    def __call__(self, img, cls=True):
        ori_im = img.copy()
        # Lấy kết quả detection các vùng text
        dt_boxes, elapse = self.text_detector(img)
        logger.debug("dt_boxes num : {}, elapse : {}".format(
            len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []
        # Sắp xếp các detection boxes: từ trên xuống dưới, từ trái sang phải
        dt_boxes = sorted_boxes(dt_boxes)
        # Thực hiện perspective transformation và chỉnh sửa trên kết quả detection
        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        # Sử dụng direction classifier để chỉnh sửa kết quả detection
        if self.use_angle_cls and cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            logger.debug("cls num  : {}, elapse : {}".format(
                len(img_crop_list), elapse))
        # Lấy kết quả text recognition
        rec_res, elapse = self.text_recognizer(img_crop_list)
        logger.debug("rec_res num  : {}, elapse : {}".format(
            len(rec_res), elapse))
        # Lưu các ảnh đã chỉnh sửa trong text detection
        if self.args.save_crop_res:
            self.draw_crop_rec_res(self.args.crop_res_save_dir, img_crop_list,
                                    rec_res)
        # Lọc kết quả theo ngưỡng recognition score,
        # nếu score thấp hơn ngưỡng thì loại bỏ
        filter_boxes, filter_rec_res = [], []
        for box, rec_reuslt in zip(dt_boxes, rec_res):
            text, score = rec_reuslt
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_reuslt)
        return filter_boxes, filter_rec_res
```

**Hàm `sorted_boxes`** — sắp xếp các detection boxes theo thứ tự đọc:

```python
def sorted_boxes(dt_boxes):
    # Sắp xếp detection boxes: đầu tiên từ trên xuống dưới, sau đó từ trái sang phải
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and \
                (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes
```

Logic: sắp xếp theo tọa độ y (trên → dưới) trước, nếu hai box có y gần nhau (chênh lệch < 10 pixel) thì sắp xếp theo tọa độ x (trái → phải). Điều này đảm bảo thứ tự đọc tự nhiên.

**Script suy luận chính:**

```python
args = parse_args()
args.cls_model_dir = "./inference/ch_ppocr_mobile_v2.0_cls_infer"
args.det_model_dir = "./inference/ch_PP-OCRv2_det_infer/"
args.rec_model_dir = "./inference/ch_PP-OCRv2_rec_infer/"
args.image_dir = "./doc/imgs/00018069.jpg"
args.use_angle_cls = True
args.use_gpu = True

image_file_list = get_image_file_list(args.image_dir)
image_file_list = image_file_list[args.process_id::args.total_process_num]
text_sys = TextSystem(args)
is_visualize = True
font_path = args.vis_font_path
drop_score = args.drop_score

total_time = 0
cpu_mem, gpu_mem, gpu_util = 0, 0, 0
_st = time.time()
count = 0
for idx, image_file in enumerate(image_file_list):
    img = cv2.imread(image_file)
    if img is None:
        logger.debug("error in loading image:{}".format(image_file))
        continue
    starttime = time.time()
    dt_boxes, rec_res = text_sys(img)
    elapse = time.time() - starttime
    total_time += elapse

    logger.debug(
        str(idx) + "  Predict time of %s: %.3fs" % (image_file, elapse))
    for text, score in rec_res:
        logger.debug("{}, {:.3f}".format(text, score))

    if is_visualize:
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        boxes = dt_boxes
        txts = [rec_res[i][0] for i in range(len(rec_res))]
        scores = [rec_res[i][1] for i in range(len(rec_res))]

        draw_img = draw_ocr_box_txt(
            image,
            boxes,
            txts,
            scores,
            drop_score=drop_score,
            font_path=font_path)
    draw_img_save_dir = args.draw_img_save_dir
    os.makedirs(draw_img_save_dir, exist_ok=True)
    cv2.imwrite(
        os.path.join(draw_img_save_dir, os.path.basename(image_file)),
        draw_img[:, :, ::-1])
    logger.debug("The visualized image saved in {}".format(
        os.path.join(draw_img_save_dir, os.path.basename(image_file))))

logger.info("The predict total time is {}".format(time.time() - _st))
```

Kết quả suy luận hiển thị khung detection + nội dung đã nhận dạng cho ảnh xét nghiệm y tế.

---

## 7.2.6 Suy luận bằng WHL Package trong PP-OCRv2 (trang 199–201)

Để bắt đầu sử dụng OCR text detection và recognition model một cách thuận tiện hơn, PaddleOCR cung cấp whl package dựa trên engine suy luận Paddle Inference. Bạn có thể trải nghiệm PaddleOCR chỉ sau một lần cài đặt.

### Cài đặt whl Package

```bash
pip install "paddleocr==2.3.0.2"

# Nếu bạn muốn có tính năng mới nhất, có thể cài từ source code
# python3 setup.py bdist_wheel
# pip3 install dist/paddleocr-x.x.x-py3-none-any.whl  # x.x.x là số phiên bản
```

### Sử dụng whl Package cho Suy luận

PaddleOCR whl package sẽ tự động tải model PP-OCRv2 ultra-lightweight làm model mặc định. Nó cũng hỗ trợ custom model paths, cấu hình suy luận và các tham số khác. Tên tham số giống hệt suy luận Python trong Paddle Inference.

#### Chạy Detection riêng

```python
from paddleocr import PaddleOCR, draw_ocr

ocr = PaddleOCR(use_gpu=False)  # chỉ cần chạy một lần để tải và load model vào bộ nhớ
img_path = '/home/aistudio/PaddleOCR/doc/imgs/11.jpg'
result = ocr.ocr(img_path, rec=False)
for line in result:
    print(line)

# Hiển thị kết quả
from PIL import Image
image = Image.open(img_path).convert('RGB')
im_show = draw_ocr(image, result, txts=None, scores=None, font_path='/home/aistudio/PaddleOCR/doc/fonts/simfang.ttf')
plt.figure(figsize=(15, 8))
plt.imshow(im_show)
plt.show()
```

Output là danh sách tọa độ bounding box:
```
[[27.0, 459.0], [135.0, 459.0], [135.0, 479.0], [27.0, 479.0]]
[[29.0, 431.0], [369.0, 431.0], [369.0, 444.0], [29.0, 444.0]]
[[26.0, 397.0], [361.0, 397.0], [361.0, 414.0], [26.0, 414.0]]
...
```

Ảnh ví dụ hiển thị detection trên ảnh sản phẩm chăm sóc tóc tiếng Trung — các vùng text được khoanh bằng hộp đỏ.

#### Chạy Recognition riêng

Bạn có thể chỉ định `det=False` để chỉ chạy module recognition:

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_gpu=False)  # chỉ cần chạy một lần để tải model
img_path = '/home/aistudio/PaddleOCR/doc/imgs_words/ch/word_1.jpg'
result = ocr.ocr(img_path, det=False)
for line in result:
    print(line)

# Expected output: ('韩国小馆', 0.9967349)
```

#### Chạy Direction Classifier riêng

Bạn có thể chỉ định `det=False, rec=False, cls=True` để chỉ chạy direction classifier:

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)  # chỉ cần chạy một lần
img_path = '/home/aistudio/PaddleOCR/doc/imgs_words/ch/word_1.jpg'
result = ocr.ocr(img_path, det=False, rec=False, cls=True)
for line in result:
    print(line)

img = cv2.imread(img_path)
plt.imshow(img[..., ::-1])
plt.show()

# Expected output: ['0', 0.9998784]
```

#### Trải nghiệm toàn bộ quy trình: Detection + Direction Classifier + Recognition

```python
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt
%matplotlib inline

# PaddleOCR hiện hỗ trợ nhiều ngôn ngữ: Tiếng Trung, Anh, Pháp, Đức, Hàn, Nhật
# Chuyển đổi bằng tham số lang
# Giá trị: 'ch', 'en', 'french', 'german', 'korean', 'japan'
ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False)  # chỉ cần chạy một lần
img_path = '/home/aistudio/PaddleOCR/doc/imgs/11.jpg'
result = ocr.ocr(img_path, cls=True)
for line in result:
    print(line)

# Hiển thị kết quả
from PIL import Image
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path='/home/aistudio/PaddleOCR/doc/fonts/simfang.ttf')
plt.figure(figsize=(15, 8))
plt.imshow(im_show)
plt.show()
```

Expected output:
```
[[[28.0, 113.0], [330.0, 113.0], [330.0, 133.0], [28.0, 133.0]], ('45元/每公斤100公斤起订', 0.90023524)]
[[[26.0, 143.0], [281.0, 144.0], [281.0, 164.0], [26.0, 163.0]], ('每瓶22元，1000瓶起订', 0.9793598)]
...
```

Kết quả là một list, mỗi phần tử chứa một text box, một chuỗi text và confidence score nhận dạng.

---

## 7.3 Suy luận C++ dựa trên Paddle Inference (trang 202–205)

Trong triển khai suy luận, hiệu năng của C++ tốt hơn Python. Do đó, trong nhiều tình huống, C++ được chọn làm ngôn ngữ phát triển cho suy luận.

Paddle Inference đã giới thiệu ở phần trước cũng hỗ trợ suy luận C++. Phần này chủ yếu nói về suy luận C++ PP-OCRv2.

Trong suy luận C++ trên hệ thống PP-OCRv2 dựa trên Paddle Inference, có các bước sau:

1. Chuẩn bị model
2. Biên dịch thư viện OpenCV
3. Tải thư viện dự đoán Paddle Inference
4. Biên dịch mã suy luận C++ PaddleOCR
5. Chạy hệ thống PP-OCRv2

Do hạn chế phiên bản trên AiStudio, quy trình sẽ chỉ được giải thích chứ không demo. Khuyến khích bạn thực hành suy luận C++ PP-OCRv2 trên máy local.

Chi tiết xem thêm: PP-OCRv2 C++ Inference Tutorial.

### 7.3.1 Chuẩn bị Model

Dùng lệnh sau để chuẩn bị model suy luận PP-OCRv2:

```bash
cd deploy/cpp_infer
wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_det_infer.tar -O ch_PP-OCRv2_det_infer.tar && tar -xf ch_PP-OCRv2_det_infer.tar
wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_rec_infer.tar -O ch_PP-OCRv2_rec_infer.tar && tar -xf ch_PP-OCRv2_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar -O ch_ppocr_mobile_v2.0_cls_infer.tar && tar -xf ch_ppocr_mobile_v2.0_cls_infer.tar
```

### 7.3.2 Biên dịch thư viện OpenCV

- Đầu tiên, tải package đã biên dịch trong môi trường Linux từ trang web chính thức OpenCV. Lấy opencv 3.4.7 làm ví dụ:

```bash
wget https://paddleocr.bj.bcebos.com/libs/opencv/opencv-3.4.7.tar.gz
tar -xf opencv-3.4.7.tar.gz
```

Bạn sẽ thấy thư mục `opencv-3.4.7/` trong thư mục hiện tại.

- Biên dịch OpenCV, set `root_path` và `install_path`:

```bash
root_path="your_opencv_root_path"
install_path=${root_path}/opencv3
build_dir=${root_path}/build

rm -rf ${build_dir}
mkdir ${build_dir}
cd ${build_dir}

cmake .. \
    -DCMAKE_INSTALL_PREFIX=${install_path} \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_IPP=OFF \
    -DBUILD_IPP_IW=OFF \
    -DWITH_LAPACK=OFF \
    -DWITH_EIGEN=OFF \
    -DCMAKE_INSTALL_LIBDIR=lib64 \
    -DWITH_ZLIB=ON \
    -DBUILD_ZLIB=ON \
    -DWITH_JPEG=ON \
    -DBUILD_JPEG=ON \
    -DWITH_PNG=ON \
    -DBUILD_PNG=ON \
    -DWITH_TIFF=ON \
    -DBUILD_TIFF=ON

make -j
make install
```

Hoặc chỉnh sửa nội dung file `tools/build_opencv.sh` rồi chạy:

```bash
sh tools/build_opencv.sh
```

`root_path` là đường dẫn source code OpenCV đã tải, `install_path` là đường dẫn cài đặt OpenCV. Sau `make install`, header files và library files sẽ được tạo trong thư mục này để biên dịch mã OCR.

Cấu trúc file trong đường dẫn cài đặt:

```
opencv3/
|-- bin
|-- include
|-- lib
|-- lib64
|-- share
```

### 7.3.3 Tải thư viện suy luận Paddle Inference

- Các thư viện dự đoán Linux với phiên bản CUDA khác nhau có sẵn trên trang web chính thức Paddle Inference. Bạn có thể chọn phiên bản phù hợp với môi trường của mình.

- Sau khi tải, giải nén:

```bash
wget https://paddle-inference-lib.bj.bcebos.com/2.2.1/cxx_c/Linux/GPU/x86-64_gcc8.2_avx_mkl_cuda10.2_cudnn8.1.1_trt7.2.3.4/paddle_inference.tgz -O paddle_inference.tgz
tar -xf paddle_inference.tgz
```

Thư mục con `paddle_inference/` sẽ được tạo.

### 7.3.4 Biên dịch mã suy luận PaddleOCR

Lệnh biên dịch như sau, cần thay thế đường dẫn thư viện suy luận C++ Paddle, opencv, và các thư viện phụ thuộc khác bằng đường dẫn thực trên máy bạn:

```bash
sh tools/build.sh
```

Bạn cần sửa đường dẫn môi trường trong `tools/build.sh`:

```bash
OPENCV_DIR=your_opencv_dir
LIB_DIR=your_paddle_inference_dir
CUDA_LIB_DIR=your_cuda_lib_dir
CUDNN_LIB_DIR=/your_cudnn_lib_dir
```

Trong đó:
- `OPENCV_DIR` là đường dẫn opencv đã biên dịch và cài đặt
- `LIB_DIR` là đường dẫn thư viện Paddle Inference đã tải (thư mục `paddle_inference`) hoặc đã biên dịch (thư mục `build/paddle_inference_install_dir`)
- `CUDA_LIB_DIR` là đường dẫn cuda library file, trong docker là `/usr/local/cuda/lib64`
- `CUDNN_LIB_DIR` là đường dẫn cudnn library file, trong docker là `/usr/lib/x86_64-linux-gnu/`

**Lưu ý: Các đường dẫn trên phải là đường dẫn tuyệt đối, không dùng đường dẫn tương đối.**

Sau khi biên dịch, file thực thi có tên `ppocr` sẽ được tạo trong thư mục `build`.

### 7.3.5 Chạy hệ thống PP-OCRv2

Cách chạy:

```bash
./build/ppocr <mode> [--param1] [--param2] [...]
```

`mode` là tham số bắt buộc, chọn chức năng, giá trị là `['det', 'rec', 'system']`, tương ứng gọi detection, recognition, và detection + recognition end-to-end (bao gồm direction classifier).

- Chạy chỉ text detection:

```bash
./build/ppocr det \
    --det_model_dir=./ch_PP-OCRv2_det_infer/ \
    --image_dir=../../doc/imgs/12.jpg
```

- Chạy chỉ text recognition:

```bash
./build/ppocr rec \
    --rec_model_dir=./ch_PP-OCRv2_rec_infer/ \
    --image_dir=../../doc/imgs_words/ch/
```

- Chạy hệ thống PP-OCRv2 (không dùng direction classifier):

```bash
./build/ppocr system \
    --det_model_dir=./ch_PP-OCRv2_det_infer/ \
    --rec_model_dir=./ch_PP-OCRv2_rec_infer/ \
    --image_dir=../../doc/imgs/12.jpg
```

- Chạy hệ thống PP-OCRv2 (có direction classifier):

```bash
./build/ppocr system \
    --det_model_dir=./ch_PP-OCRv2_det_infer/ \
    --rec_model_dir=./ch_PP-OCRv2_rec_infer/ \
    --use_angle_cls=true \
    --cls_model_dir=./ch_ppocr_mobile_v2.0_cls_infer \
    --image_dir=../../doc/imgs/12.jpg
```

---

## 7.4 Triển khai dịch vụ bằng Paddle Serving (trang 205–210)

Ở Mục 2 và 3, chúng ta đã giới thiệu suy luận hệ thống PP-OCRv2 dựa trên Paddle Inference — đây là suy luận offline, code được triển khai trên một máy cụ thể chỉ có thể dùng trên máy đó và không thể truy cập từ máy khác. Do đó, nhu cầu triển khai model dưới dạng dịch vụ được đặt ra.

Trong triển khai dịch vụ (Service deployment), model được triển khai thành một service, các thiết bị khác có thể truy cập service này bằng cách gửi request để nhận kết quả suy luận.

Paddle Serving là công cụ được PaddlePaddle tạo ra để giúp developer thực hiện triển khai dịch vụ. Phần này chủ yếu nói về triển khai dịch vụ hệ thống PP-OCRv2 với Paddle Serving.

### 7.4.1 Giới thiệu Paddle Serving

Paddle Serving là framework triển khai dịch vụ mã nguồn mở của PaddlePaddle. Mục tiêu dài hạn là cung cấp các dịch vụ chuyên nghiệp, đáng tin cậy và dễ sử dụng hơn để giải quyết "dặm cuối" của việc landing AI. Paddle Serving hiện cung cấp hai framework:

- **C++ Serving**: hướng đến hiệu năng cao
- **Python Pipeline**: hướng đến dễ phát triển thứ cấp

Khi model PP-OCRv2 được triển khai thành dịch vụ với Paddle Serving, quy trình gồm 6 bước:

1. Chuẩn bị dữ liệu và môi trường triển khai
2. Chuẩn bị model cho serving
3. Chuẩn bị mã server
4. Chuẩn bị mã client
5. Khởi động dịch vụ
6. Truy cập dịch vụ và nhận output

### 7.4.2 Chuẩn bị dữ liệu suy luận và môi trường triển khai

Dữ liệu phải nhất quán với dữ liệu dùng cho suy luận model.

Trước khi chạy Paddle Serving, cần cài 3 package: `paddle-serving-server`, `paddle-serving-client` và `paddle-serving-app`:

```bash
wget https://paddle-serving.bj.bcebos.com/test-dev/whl/paddle_serving_server_gpu-0.7.0.post102-py3-none-any.whl
pip install paddle_serving_server_gpu-0.7.0.post102-py3-none-any.whl

wget https://paddle-serving.bj.bcebos.com/test-dev/whl/paddle_serving_client-0.7.0-cp37-none-any.whl
pip install paddle_serving_client-0.7.0-cp37-none-any.whl

wget https://paddle-serving.bj.bcebos.com/test-dev/whl/paddle_serving_app-0.7.0-py3-none-any.whl
pip install paddle_serving_app-0.7.0-py3-none-any.whl

rm ./*.whl
```

### 7.4.3 Chuẩn bị model cho triển khai

Trước khi triển khai dịch vụ model, đầu tiên cần chuyển inference model thành model phù hợp cho triển khai dịch vụ.

Đầu tiên tải model suy luận:

```python
os.chdir("/home/aistudio/PaddleOCR/deploy/pdserving/")

# Tải và giải nén model text detection OCR
!wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_det_infer.tar -O ch_PP-OCRv2_det_infer.tar && tar -xf ch_PP-OCRv2_det_infer.tar && rm ch_PP-OCRv2_det_infer.tar

# Tải và giải nén model text recognition OCR
!wget https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_rec_infer.tar -O ch_PP-OCRv2_rec_infer.tar && tar -xf ch_PP-OCRv2_rec_infer.tar && rm ch_PP-OCRv2_rec_infer.tar
```

Chạy lệnh chuyển đổi model:

```bash
# Chuyển đổi detection model
!python -m paddle_serving_client.convert --dirname ./ch_PP-OCRv2_det_infer/ \
                                        --model_filename inference.pdmodel \
                                        --params_filename inference.pdiparams \
                                        --serving_server ./ppocrv2_det_serving/ \
                                        --serving_client ./ppocrv2_det_client/

# Chuyển đổi recognition model
!python -m paddle_serving_client.convert --dirname ./ch_PP-OCRv2_rec_infer/ \
                                        --model_filename inference.pdmodel \
                                        --params_filename inference.pdiparams \
                                        --serving_server ./ppocrv2_rec_serving/ \
                                        --serving_client ./ppocrv2_rec_client/
```

Xem cấu trúc thư mục:

```
ppocrv2_det_client
├── [ 296]  serving_client_conf.prototxt
└── [  98]  serving_client_conf.stream.prototxt

ppocrv2_rec_client
├── [ 284]  serving_client_conf.prototxt
└── [  93]  serving_client_conf.stream.prototxt

ppocrv2_det_serving
├── [2.2M]  inference.pdiparams
├── [842K]  inference.pdmodel
├── [ 296]  serving_server_conf.prototxt
└── [  98]  serving_server_conf.stream.prototxt

ppocrv2_rec_serving
├── [7.9M]  inference.pdiparams
├── [527K]  inference.pdmodel
├── [ 284]  serving_server_conf.prototxt
└── [  93]  serving_server_conf.stream.prototxt
```

Sau khi chuyển đổi detection model, cũng sẽ có thêm thư mục `ppocrv2_det_mobile_serving` và `ppocrv2_det_mobile_client` với cấu trúc tương tự. Model recognition cũng tương tự.

### 7.4.4 Triển khai Paddle Serving Pipeline

**Lưu ý:** Sửa hai trường `model_config` trong file `PaddleOCR/deploy/pdserving/config.yml` thành `ppocrv2_det_mobile_serving` và `ppocrv2_rec_mobile_serving` tương ứng, để trỏ đến thư mục model đã chuyển đổi.

Thư mục `pdserving` chứa mã khởi động pipeline service và gửi prediction requests:

```
__init__.py
config.yml            # File cấu hình khởi động dịch vụ
ocr_reader.py         # Mã tiền xử lý và hậu xử lý model OCR
pipeline_http_client.py  # Script gửi inference request
web_service.py        # Script khởi động server
```

#### Khởi động dịch vụ

Mở terminal mới và chạy lệnh sau:

```bash
# Khởi động dịch vụ và lưu log vào web_serving_log.txt
cd PaddleOCR/deploy/pdserving/
nohup python web_service.py &>web_serving_log.txt &
```

Sau khi dịch vụ khởi động, log tương tự như sau sẽ được in trong `web_serving_log.txt` — hiển thị các bước `inference_op_replace_pass`, `memory_optimize_pass`, `ir_graph_to_program_pass` với thông tin cluster name và size.

#### Gửi service request

```bash
!python pipeline_http_client.py
```

Output:
```
{'err_no': 0, 'err_msg': '', 'key': ['res'], 'value': ["['{detected_text}', '{text}|{score}']"], 'tensors': []}
```

Bạn có thể điều chỉnh số lượng concurrency trong `config.yml`. Ở đây chỉ demo hiệu ứng chạy, mặc định set concurrency = 1:

```yaml
det:
    # Concurrency: khi is_thread_op=True → thread concurrency, ngược lại → process concurrency
    concurrency: 1
    ...
rec:
    # Concurrency: khi is_thread_op=True → thread concurrency, ngược lại → process concurrency
    concurrency: 1
    ...
```

Dữ liệu performance suy luận sẽ tự động được ghi vào file `PipelineServingLogs/pipeline.tracer`.

### 7.4.5 FAQ

**Q1:** Sau khi gửi request, không có kết quả trả về hoặc hiện lỗi output decoding.

**A1:** Không set proxy khi khởi động dịch vụ và gửi request. Tắt proxy trước bằng lệnh:

```bash
unset https_proxy
unset http_proxy
```

---

## 7.5 Suy luận End-to-Side dựa trên Paddle Lite (trang 210–212)

Khi Internet di động ngày càng phổ biến, có ngày càng nhiều điện thoại di động và thiết bị nhúng. Đồng thời, vì lý do bảo mật dữ liệu và tiết kiệm chi phí vận hành model, ngày càng nhiều model được chạy trực tiếp trên thiết bị đầu cuối (end-side devices).

Paddle Lite là engine suy luận nhẹ của PaddlePaddle. Nó cung cấp khả năng suy luận hiệu quả cho điện thoại di động và thiết bị IoT, tích hợp rộng rãi phần cứng đa nền tảng để cung cấp giải pháp triển khai nhẹ cho end-side deployment và landing ứng dụng.

Phần này sẽ giới thiệu các bước triển khai model phát hiện và nhận dạng tiếng Trung ultra-lightweight của PaddleOCR trên thiết bị di động dựa trên Paddle Lite.

### 7.5.1 Chuẩn bị môi trường

Bạn cần chuẩn bị cross-compilation environment và thư viện suy luận Paddle Lite. Cross-compilation environment được dùng để tạo file thực thi có thể chạy trên thiết bị đầu cuối. Khuyến khích dùng Docker làm cross-compilation environment.

### 7.5.2 Chuẩn bị Model

Trong suy luận model với Paddle Lite, trước tiên cần chuyển inference model thành model tối ưu cho suy luận Paddle Lite (đuôi file thường là `.nb`). Nhiều chiến lược được áp dụng để tự động tối ưu model gốc, bao gồm quantization, subgraph fusion, hybrid scheduling, và kernel optimization. Model đã tối ưu nhẹ hơn và nhanh hơn.

### 7.5.3 Biên dịch

Chạy `make -j` để biên dịch và lấy file thực thi. Lần chạy đầu tiên, lệnh này sẽ tải các thư viện phụ thuộc như opencv. Sau khi tải xong, chạy `make -j` lần nữa.

### 7.5.4 Upload lên thiết bị di động

Dùng các công cụ như `adb` để transfer file thực thi, model files, và configuration files lên thiết bị di động như điện thoại.

### 7.5.5 Chạy

Chạy file thực thi trên terminal thiết bị di động để nhận kết quả. Ví dụ output trên demo Android nhận dạng nhãn sản phẩm chăm sóc tóc tiếng Trung:

```
The detection visualized image saved in ./vis.jpg
0    纯臻营养护发素    0.993604
1    产品信息/参数     0.992728
2    (45元/每公斤，100公斤起订)    0.97417
3    每瓶22元，1000瓶起订）  0.993976
4    【品牌】：代加工方式/OEMODM    0.985133
5    【品名】：纯臻营养护发素    0.995007
6    【产品编号】：YM-X-3011    0.96899
7    【净含量】：220ml    0.996577
8    【适用人群】：适合所有肤质    0.995842
9    【主要成分】：鲸蜡硬脂醇、燕麦B-葡聚    0.961928
10   糖、椰油酰胺丙基甜菜碱、泛醇    0.925898
11   （成品包材）     0.972573
12   【主要功能】：可紧致头发磷层，从而达到    0.994448
13   即时持久改善头发光泽的效果，给干燥的头    0.990198
14   发足够的滋养     0.997668
花费了0.457335秒
```

### 7.5.6 FAQ

**Q1:** Nếu tôi muốn thay đổi model, có cần lặp lại toàn bộ quy trình không?

**A1:** Nếu bạn đã thực hiện các bước trên, bạn chỉ cần thay file `.nb` model. Đồng thời cập nhật dictionary.

**Q2:** Làm sao test với ảnh khác?

**A2:** Thay ảnh `.jpg` test trong thư mục debug bằng ảnh bạn muốn test, rồi `adb push` lên điện thoại.

**Q3:** Làm sao đóng gói demo và gửi lên mobile APP?

**A3:** Demo này nhằm cung cấp phần thuật toán cốt lõi cho chạy OCR trên điện thoại di động. Bạn có thể tham khảo `PaddleOCR/deploy/android_demo` — đây là ví dụ đóng gói demo thành ứng dụng trên điện thoại.

---

## 7.6 Bài tập

Vui lòng tham khảo phần Câu hỏi Trắc nghiệm Triển khai Suy luận (Inference Deployment Objective Questions) và phần Bài tập Thực hành Triển khai Suy luận (Inference Deployment Practice Questions).

---

---

# Chương 8 — Công nghệ Phân tích Tài liệu (Document Analysis Technology)

## 8.1 Giới thiệu Công nghệ Phân tích Tài liệu (trang 215)

Chương này chủ yếu giới thiệu kiến thức lý thuyết về công nghệ phân tích tài liệu, bao gồm bối cảnh, phân loại thuật toán và ý tưởng đằng sau các thuật toán.

Trong chương này, bạn sẽ học:
1. Phân loại và ý tưởng của layout analysis
2. Phân loại và ý tưởng của table recognition
3. Phân loại và ý tưởng của information extraction

Tài liệu là phương tiện chứa thông tin. Bố cục khác nhau phù hợp với các loại thông tin khác nhau, chẳng hạn như danh sách và thẻ căn cước. Phân tích tài liệu là quá trình đọc, diễn giải và trích xuất thông tin tự động. Nó thường bao gồm các hướng nghiên cứu sau:

1. **Module phân tích bố cục (Layout Analysis):** Chia mỗi trang tài liệu thành các vùng nội dung khác nhau. Module này có thể được dùng không chỉ để phân chia vùng liên quan và không liên quan, mà còn để phân loại nội dung nó nhận dạng.

2. **Module OCR (Optical Character Recognition):** Định vị và nhận dạng tất cả text trong tài liệu.

3. **Module nhận dạng bảng (Table Recognition):** Nhận dạng bảng trong tài liệu và chuyển thành file Excel.

4. **Module trích xuất thông tin (Information Extraction):** Sử dụng kết quả OCR và thông tin ảnh để hiểu và nhận dạng thông tin cụ thể trong tài liệu hoặc mối quan hệ giữa các thông tin.

Vì module OCR đã được trình bày chi tiết ở các chương trước, ba module còn lại sẽ được giới thiệu lần lượt. Trong mỗi phần, các phương pháp kinh điển hoặc phổ biến và datasets của module sẽ được giới thiệu.

---

### 8.1.1 Layout Analysis — Phân tích bố cục (trang 215–220)

#### Giới thiệu nền tảng

Layout analysis chủ yếu được dùng cho document retrieval, key information extraction, content classification, v.v. Mục đích là phân loại ảnh tài liệu. Các danh mục bao gồm plain text, tiêu đề, bảng, hình ảnh và danh sách. Tuy nhiên, nhiều yếu tố khiến layout analysis vẫn là bài toán thách thức, bao gồm sự đa dạng và phức tạp của bố cục và định dạng tài liệu, chất lượng ảnh tài liệu kém, và thiếu dataset annotated quy mô lớn.

Các giải pháp hiện có thường dựa trên **object detection** hoặc **semantic segmentation**, phát hiện hoặc phân đoạn các mẫu khác nhau trong tài liệu thành các đối tượng khác nhau.

Một số bài báo đại diện được chia thành hai loại:

| Phương pháp | Bài báo chính |
|---|---|
| Dựa trên object detection | Visual Detection with Context, Object Detection, VSR |
| Dựa trên semantic segmentation | Semantic Segmentation |

#### Phương pháp dựa trên Object Detection

Soto Carlos [1] học từ thuật toán object detection Faster R-CNN, sử dụng thông tin ngữ cảnh và thông tin vị trí cố hữu trong nội dung tài liệu để cải thiện hiệu năng phát hiện vùng. Li Kai [2] và các đồng tác giả cũng đề xuất phương pháp phân tích tài liệu dựa trên object detection, giải quyết vấn đề cross-domain bằng cách giới thiệu ba module: feature pyramid alignment module, region alignment module, và rendering layer alignment module. Ba module này bổ sung cho nhau, điều chỉnh từ góc nhìn general image và góc nhìn document image cụ thể, từ đó giải quyết sự không nhất quán giữa large-label training datasets và target domain.

#### Phương pháp dựa trên Semantic Segmentation

Sarkar Mausoom [3] và các đồng tác giả đề xuất cơ chế segmentation dựa trên a priori để huấn luyện model segmentation tài liệu trên ảnh độ phân giải cao, giải quyết vấn đề các cấu trúc vùng dày đặc không thể phân biệt được và bị merge do thu nhỏ ảnh gốc quá mức. Zhang Peng [4] và các đồng tác giả đề xuất unified framework VSR (Vision, Semantics and Relations) cho document layout analysis. Framework sử dụng two-stream network để trích xuất visual và semantic features, và kết hợp thích ứng các features này thông qua adaptive aggregation module, vượt qua hiệu quả thấp của việc fuse các module khác nhau và thiếu relationship modeling giữa các layout components trong các phương pháp dựa trên CV hiện có.

#### Datasets

Mặc dù các phương pháp hiện có có thể giải quyết bài toán layout analysis ở mức độ nhất định, chúng phụ thuộc vào lượng lớn labeled training data. Gần đây, nhiều datasets đã được đề xuất cho document analysis:

1. **PubLayNet [5]:** Dataset chứa 500,000 document images, trong đó 400,000 dùng cho training, 50,000 cho verification, và 50,000 cho testing. Tables, texts, pictures, titles, và lists được gán nhãn trong dataset.

2. **HJDataset [6]:** Dataset chứa 2,271 document images. Ngoài bounding boxes và masks của nội dung, nó còn bao gồm hierarchical structure và reading order của các layout elements.

Kết quả benchmark (Detection mAP @ IOU [0.50:0.95]) trên test set:

| Category | Faster R-CNN | Mask R-CNN | RetinaNet |
|---|---|---|---|
| Page Frame | 99.046 | 99.097 | 99.038 |
| Row | 98.831 | 98.482 | 95.067 |
| Title Region | 87.571 | 89.483 | 69.593 |
| Text Region | 94.463 | 86.798 | 89.531 |
| Title | 65.908 | 71.517 | 72.566 |
| Subtitle | 84.093 | 84.174 | 85.865 |
| Other | 44.023 | 39.849 | 14.371 |
| **mAP** | **81.991** | **81.343** | **75.223** |

Nhìn chung, giá trị mAP cao cho thấy phát hiện chính xác các layout elements. Faster R-CNN và Mask R-CNN đạt kết quả tương đương, tốt hơn RetinaNet. Đáng chú ý, phát hiện các block nhỏ như title có độ chính xác thấp hơn, và accuracy giảm mạnh cho category title ở Faster R-CNN model.

---

### 8.1.2 Table Recognition — Nhận dạng bảng (trang 220–228)

#### Giới thiệu nền tảng

Bảng là thành phần phổ biến trong các loại tài liệu. Với sự bùng nổ của các loại tài liệu, việc tìm bảng hiệu quả từ tài liệu và lấy nội dung và cấu trúc của chúng trở nên cấp thiết — đây gọi là Table Recognition. Các khó khăn được tóm tắt như sau:

1. Kiểu và phong cách bảng phức tạp và đa dạng, chẳng hạn *hàng/cột gộp khác nhau, nội dung đa dạng*.
2. Phong cách tài liệu bản thân cũng đa dạng.
3. Môi trường ánh sáng khi chụp phức tạp.

Bài toán table recognition là chuyển thông tin bảng từ ảnh tài liệu thành file Excel. Hình minh họa cho thấy ảnh gốc (bên trái) và kết quả sau nhận dạng (bên phải) — bao gồm cả bảng xét nghiệm y tế và bảng thống kê dịch tễ.

Các thuật toán table recognition hiện có được chia thành 4 loại theo nguyên lý tái tạo cấu trúc bảng:

| Phương pháp | Ý tưởng | Bài báo chính |
|---|---|---|
| Dựa trên heuristic rules | Quy tắc thiết kế thủ công, connected domain analysis và xử lý | T-Rect, pdf2table |
| Dựa trên CNN | Target detection, semantic segmentation | CascadeTabNet, Multi-Type-TD-TSR, LGPMA, tabstruct-net, CDeC-Net, TableNet, TableSense, Deepdesrt, Deeptabstr, GTE, Cycle-CenterNet, FCN |
| Dựa trên GCN | Coi table recognition là bài toán graph reconstruction trên nền tảng graph neural network | GNN, TGRNet, GraphTSR |
| Dựa trên End to End | Sử dụng attention mechanism | Table-Master |

#### Thuật toán truyền thống dựa trên Heuristic Rules

Nghiên cứu sớm về table recognition chủ yếu dựa trên heuristic rules. Ví dụ, hệ thống T-Rect đề xuất bởi Kieninger [1] phân tích connected domain của ảnh tài liệu theo kiểu bottom-up, merge chúng theo quy tắc đã định để lấy logical texts. Sau đó, pdf2table đề xuất bởi Yildiz [2] là phương pháp đầu tiên nhận dạng bảng trên tài liệu PDF — khai thác thông tin riêng trong file PDF (như texts, drawing paths và các thông tin khó lấy từ ảnh tài liệu) để hỗ trợ nhận dạng bảng. Gần đây, Koci [3] biểu diễn layout region trong trang thành graph, rồi dùng thuật toán Remove and Conquer (RAC) để nhận dạng bảng như một subgraph.

#### Phương pháp dựa trên Deep Learning CNN

Với sự phát triển nhanh của deep learning trong computer vision, NLP, speech processing, v.v., các nhà nghiên cứu đã áp dụng deep learning vào lĩnh vực table recognition và đạt kết quả tốt.

Trong thuật toán DeepTabStR, Siddiqui Shoaib Ahmed [12] mô tả bài toán table structure recognition thành bài toán object detection, và dùng deformable convolution để phát hiện table cells tốt hơn. Raja Sachin [6] đề xuất TabStruct-Net kết hợp cell detection và structure recognition trực quan để nhận dạng cấu trúc bảng, giải quyết vấn đề lỗi nhận dạng do thay đổi lớn trong bố cục bảng. Tuy nhiên, phương pháp này không xử lý được bảng có nhiều ô trống.

Các phương pháp table structure recognition trước đó bắt đầu từ các phần tử ở granularity khác nhau (row/column và text region), và dễ bỏ qua vấn đề merge empty cells. Qiao Liang [10] đề xuất framework mới LGPMA, tận dụng thông tin từ local và global features thông qua mask re-scoring strategy, thu được aligned cell region đáng tin cậy hơn, và cuối cùng giới thiệu table structure restoration pipelines bao gồm cell matching, empty cell searching và merging.

Ngoài ra, còn có các phương pháp detect và recognize bảng trong cùng một model:
- **DeepDeSRT** (Schreiber Sebastian [11]): dùng Faster RCNN và FCN semantic segmentation cho table detection + hàng/cột — hai model độc lập.
- **CascadeTabNet** (Prasad Devashish [4]): Cascade Mask R-CNN HRNet — detect bảng và recognize cấu trúc đồng thời, vượt qua hạn chế dùng hai phương pháp độc lập.
- **TableNet** (Paliwal Shubham [8]): end-to-end deep multi-task architecture cho table detection và structure recognition, thêm spatial semantic features để cải thiện hiệu năng.
- **GTE** (Zheng Xinyi [13]): systematic framework dùng cell detection network hướng dẫn table detection network, hierarchical network + cluster-based cell structure recognition.

Nghiên cứu trước chủ yếu tập trung vào bảng có bố cục đơn giản và alignment tốt trong PDF scan. Tuy nhiên, bảng thực tế có thể phức tạp, biến dạng nghiêm trọng, cong, hoặc bị che. Do đó, Long Rujiao [14] xây dựng dataset nhận dạng bảng WTW cho tình huống phức tạp thực tế, và đưa ra phương pháp **Cycle-CenterNet** — dùng cyclic pairing module optimization và pairing loss mới để nhóm chính xác các discrete units thành structured tables.

Phương pháp CNN không giỏi xử lý bảng có crossing columns và rows, nên có hai hướng nghiên cứu khác.

#### Phương pháp dựa trên Deep Learning GCN

Gần đây, với sự phát triển của Graph Convolutional Network (GCN), một số nhà nghiên cứu đã thử áp dụng GCN cho table structure recognition:

- **Qasim Shah Rukh [20]:** coi table structure recognition là bài toán tương thích với graph neural networks, thiết kế kiến trúc differentiable mới tận dụng CNN cho feature extraction và tương tác hiệu quả giữa các vertices của graph neural network. Tuy nhiên, phương pháp này chỉ dùng location features của cells, không dùng semantic features.

- **GraphTSR** (Chi Zewen [19]): graph neural network khác cho table structure recognition trong PDF files. Lấy table cells làm input, dùng kết nối giữa edges và nodes của graph để dự đoán mối quan hệ giữa cells và nhận dạng table structure — giải quyết nhận dạng cell span qua rows hoặc columns.

- **TGRNet** (Xue Wenyuan [21]): reformulate table structure recognition thành table reconstruction, phương pháp end-to-end gồm 2 nhánh — cell detection branch và cell logic location branch. Hai nhánh dự đoán spatial và logical positions của cells, giải quyết vấn đề phương pháp trước không chú ý đến logical position.

#### Phương pháp dựa trên End-to-End

Khác với các phương pháp dùng post-processing để tái tạo cấu trúc bảng, phương pháp end-to-end dùng network để hoàn thành output HTML representation trực tiếp.

Phương pháp chủ yếu dùng **Seq2Seq** của Image Caption để dự đoán cấu trúc bảng, ví dụ các phương pháp dựa trên attention hoặc transformer.

**TableMaster** — Ye Jiaquan [22] lấy table structure model bằng cách cải tiến thuật toán Master dựa trên Transformer. Thêm nhánh coordinate regression cho box. Tác giả không tách model thành hai nhánh ở layer cuối, mà decoupled sequence prediction và box regression sau Transformer decoding layer đầu tiên. So sánh kiến trúc:

- **Vanilla MASTER:** Input Image → Feature Extractor → Positional Encoding → Transformer Layers → Linear & Softmax → Output Probabilities
- **Table Structure MASTER:** Giống trên nhưng sau Transformer decoding layer đầu tiên, tách thành hai nhánh:
  - Nhánh 1: Transformer Layers → Linear & Softmax → Output Probabilities (structure)
  - Nhánh 2: Transformer Layers → Linear & Sigmoid → Box Regression (cell coordinates)

#### Datasets

Do phương pháp deep learning là data-driven, cần lượng lớn labeled data. Kích thước nhỏ của datasets hiện có cũng là ràng buộc quan trọng, nên một số datasets đã được đề xuất:

1. **PubTabNet [16]:** Chứa 568K table images và structured HTML representations.
2. **PubMed Tables (PubTables-1M) [17]:** Dataset nhận dạng cấu trúc bảng với annotations cấu trúc chi tiết. 460,589 pdf images cho table detection tasks, 947,642 table images cho table recognition tasks.
3. **TableBank [18]:** Dataset phát hiện và nhận dạng bảng sử dụng Word và LaTeX documents trên Internet, chứa 417K annotations chất lượng cao.
4. **SciTSR [19]:** Dataset nhận dạng cấu trúc bảng, hầu hết ảnh được chuyển từ papers. Chứa 15,000 bảng từ PDF files và structure tags tương ứng.
5. **TabStructDB [12]:** Bao gồm 1,081 table regions, được đánh dấu với dense row và column information.
6. **WTW [14]:** Dataset quy mô lớn cho scene table detection và recognition, chứa 14,581 images — bảng bị biến dạng, cong, hoặc bị che.

---

### 8.1.3 Document VQA (trang 228–235)

#### Bài toán thực tế

Sếp giao task: xây dựng hệ thống nhận dạng thẻ căn cước (ID card recognition system).

Ví dụ output mong muốn:
```python
result = {
    "姓名": "x明明",
    "性别": "男",
    "名族": "汉",
    "地址": "黑龙江省海伦市海伦镇",
    "公民身份证号": 90000000
}
```

Cách chọn phương án:
1. Dùng rules để trích xuất thông tin sau text detection
2. Dùng scale types để trích xuất thông tin sau text detection
3. Outsource cho bên ngoài

#### Giới thiệu nền tảng

Trong bài toán VQA (Visual Question Answering), câu hỏi và câu trả lời chủ yếu tập trung vào nội dung của ảnh. Nhưng vì thông tin cốt lõi của text images là text, VQA có thể chia thành hai loại: **Text-VQA** cho natural scenes và **DocVQA** cho scanned texts.

| Task | Mô tả |
|------|-------|
| **VQA** | Hỏi đáp về **nội dung hình ảnh** (picture content) |
| **Text-VQA** | Hỏi đáp về **text trên hình ảnh** (texts on pictures) |
| **DocVQA** | Hỏi đáp về **text trong ảnh tài liệu** (texts of document images) |

Vì DocVQA gần với ứng dụng thực tế hơn, nó được sử dụng rộng rãi hơn trong nghiên cứu và công nghiệp. Thường thì câu hỏi trong DocVQA là cố định. Ví dụ trong scenario thẻ căn cước:
1. Số CMND là gì?
2. Tên là gì?
3. Dân tộc gì?

Dựa trên kiến thức nền tảng này, nghiên cứu về DocVQA đã bắt đầu tập trung vào task **Key Information Extraction (KIE)**. KIE chủ yếu trích xuất key information cần thiết từ ảnh, chẳng hạn tên và số CMND từ thẻ căn cước.

#### KIE — hai sub-tasks

1. **SER (Semantic Entity Recognition):** Phân loại mỗi text đã phát hiện — ví dụ đánh dấu text là "tên" của thẻ căn cước. Ví dụ trong hình bên trái — mỗi trường text được gán nhãn semantic.

2. **RE (Relation Extraction):** Phân loại mỗi text đã phát hiện, ví dụ thành questions và answers. Sau đó tìm answer tương ứng cho mỗi question. Trong hình, hộp đỏ và đen đại diện question và answer tương ứng, đường vàng biểu thị relation giữa question và answer.

#### Phương pháp KIE chung

Phương pháp KIE chung được nghiên cứu dựa trên Named Entity Recognition (NER) [4], nhưng các phương pháp này chỉ dùng text information trong ảnh mà thiếu visual và structural information, nên không đủ chính xác. Gần đây, visual và structural information đã được tích hợp. Theo nguyên lý fusion multimodal information, các phương pháp này chia thành 4 loại:

| Phương pháp | Ý tưởng | Bài báo chính |
|---|---|---|
| Grid-based | Fuse multi-modal information trên images (texts, layouts, images) | Chargrid |
| Token-based | Dùng methods như BERT cho multi-modal information fusion | LayoutLM, LayoutLMv2, StrucTexT |
| GCN-based | Dùng graph network structure cho multi-modal information fusion | GCN, PICK, SDMG-R, SERA |
| End-to-End | Hợp nhất OCR và key information extraction vào một network | Trie |

#### Grid-Based Method

Phương pháp Grid-based thực hiện multimodal information fusion trên ảnh. **Chargrid [5]** đầu tiên detect và recognize ký tự trong ảnh, xây dựng network input bằng cách điền one-hot code vào vùng ký tự tương ứng (phần non-black trong ảnh bên phải), và cho input đi qua CNN network kiến trúc encoder-decoder để thực hiện coordinate detection và classification của key information.

So với phương pháp truyền thống chỉ dựa trên text, phương pháp này có thể sử dụng cả text information và structural information, nên accuracy cao hơn. Nhưng nó không kết hợp hữu cơ hai loại thông tin.

#### Token-Based Method

**LayoutLM [6]** encode thông tin vị trí 2D và text information cùng nhau vào BERT model, dựa trên pre-training của BERT trong NLP để pre-train large-scale datasets. Trong downstream tasks, LayoutLM cũng giới thiệu image information để cải thiện hiệu năng model. Tuy nhiên, vì LayoutLM kết hợp text, location và image information, image information được fused trong training downstream tasks, khiến multi-modal combination không đủ mạnh.

Dựa trên LayoutLM, **LayoutLMv2 [7]** tích hợp image information với text và layout information trong pre-training stage thông qua transformers, đồng thời thêm spatial perception self-attention mechanism vào Transformer để hỗ trợ model integration visual và text features. Tuy nhiên, mặc dù LayoutLMv2 fuse text, location và image information trong pre-training stage, visual features model học được không đủ fine do hạn chế pre-training task.

Do đó **StrucTexT [8]** đề xuất hai tasks mới: **Sentence Length Prediction (SLP)** và **Paired Boxes Direction (PBD)** trong pre-training để giúp network học fine visual features. SLP task giúp model học length của text segment, PBD task cho phép model học matching relationship giữa box directions. Bằng cách này, deep cross-modal fusion giữa text, visual và layout information có thể được accelerated.

#### GCN-Based Method

Mặc dù các phương pháp GCN-based hiện có [10] sử dụng text và structure information, nhưng không tận dụng tốt image information.

- **PICK [11]:** thêm image information vào GCN network và đề xuất graph learning module để tự động học edge types.

- **SDMG-R [12]:** encode ảnh thành bimodal graph. Nodes của graph chứa visual và textual information của text region. Edges đại diện direct spatial relationship giữa adjacent texts. Bằng cách lặp đi lặp lại spreading information dọc edges và inferring graph node categories, SDMG-R giải quyết vấn đề các phương pháp hiện có không xử lý được novel templates.

- **SERA [10]:** giới thiệu biaffine parser từ dependency syntax analysis vào document relation extraction, và dùng GCN để fuse text và visual information.

#### Phương pháp End-to-End

Các phương pháp hiện có chia KIE thành hai independent tasks: text reading và information extraction. Tuy nhiên, chúng chỉ tập trung cải thiện task information extraction, bỏ qua rằng text reading và information extraction có mối liên hệ qua lại.

Do đó, **Trie [9]** đề xuất unified end-to-end network, trong đó hai tasks có thể được học đồng thời và reinforce lẫn nhau trong quá trình training.

#### Datasets cho KIE

1. **SROIE [2]:** Task3 nhằm trích xuất 4 loại thông tin định trước từ scanned receipt: company, date, address hoặc total number. 626 samples cho training, 347 cho testing.

2. **FUNSD [3]:** Dataset dùng để nắm bắt thông tin bảng từ scanned documents. Chứa 199 marked forms từ real scenarios. 149/199 dùng cho training, 50 cho testing. FUNSD gán semantic tag cho mỗi word: question, answer, title hoặc other.

3. **XFUN:** Dataset đa ngôn ngữ đề xuất bởi Microsoft. Chứa 7 ngôn ngữ, mỗi ngôn ngữ có 149 training sets và 50 test sets.

---

## 8.2 Thực hành Nhận dạng Bảng OCR (OCR Table Recognition Practice) (trang 236–243)

Phần này sẽ giới thiệu cách sử dụng PaddleOCR để huấn luyện và chạy thuật toán nhận dạng bảng, bao gồm:
1. Hiểu nguyên lý thuật toán nhận dạng bảng
2. Nắm vững training và prediction của mã nhận dạng bảng PaddleOCR

### 8.2.1 Quick Start

Để demo nhanh PP-Structure prediction, đầu tiên tải mã PaddleOCR và cài dependency packages:

```bash
# Clone PaddleOCR code
! git clone -b release/2.4 https://gitee.com/paddlepaddle/PaddleOCR

# Cài dependencies
! pip install -U https://paddleocr.bj.bcebos.com/whl/layoutparser-0.0.0-py3-none-any.whl
! pip install -r PaddleOCR/requirements.txt
! pip install pandas
```

Sau khi cài đặt, chạy nhận dạng bảng nhanh:

```python
# Chuyển đến thư mục làm việc
import os
os.chdir('PaddleOCR/ppstructure')
```

```bash
# Tải model
! mkdir inference && cd inference
# Tải model detection ultra-lightweight table English OCR và giải nén
! wget -P ./inference/ https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_det_infer.tar && cd inference && tar xf ch_PP-OCRv2_det_infer.tar && cd ..
# Tải model recognition
! wget -P ./inference/ https://paddleocr.bj.bcebos.com/PP-OCRv2/chinese/ch_PP-OCRv2_rec_infer.tar && cd inference && tar xf ch_PP-OCRv2_rec_infer.tar && cd ..
# Tải model table structure ultra-lightweight và giải nén
! wget -P ./inference/ https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_structure_infer.tar && cd inference && tar xf en_ppocr_mobile_v2.0_table_structure_infer.tar && cd ..
```

```python
# Đọc ảnh và hiển thị
import cv2
from matplotlib import pyplot as plt
%matplotlib inline

img = cv2.imread('../doc/table/table.jpg')
plt.imshow(img)
```

Ảnh ví dụ là bảng so sánh các phương pháp text detection (SegLink, PixelLink, TextSnake, DB, v.v.) với các metrics R, P, F, FPS.

```python
# https://github.com/PaddlePaddle/PaddleOCR/blob/dygraph/ppstructure/table/predict_table.py#L55
from table.predict_table import TableSystem, to_excel
from utility import init_args

# Khởi tạo tham số
args = init_args().parse_args(args=[])
args.det_model_dir = 'inference/ch_PP-OCRv2_det_infer'
args.rec_model_dir = 'inference/ch_PP-OCRv2_rec_infer'
args.table_model_dir = 'inference/en_ppocr_mobile_v2.0_table_structure_infer'
args.rec_char_dict_path = '../ppocr/utils/ppocr_keys_v1.txt'
args.table_char_dict_path = '../ppocr/utils/dict/table_structure_dict.txt'
args.det_limit_side_len = 736
args.det_limit_type = 'min'
args.output = '../output/table'
args.use_gpu = False

# Khởi tạo hệ thống nhận dạng bảng
table_sys = TableSystem(args)
img = cv2.imread('../doc/table/table.jpg')
# Thực hiện nhận dạng bảng
pred_html = table_sys(img)
# Lưu kết quả vào file Excel
to_excel(pred_html, '1.xlsx')
# Hiển thị HTML
from IPython.core.display import display, HTML
display(HTML(pred_html))
```

Output:
```
[2022/03/17 21:27:08] root DEBUG: dt_boxes num : 78, elapse : 0.5478317737579346
[2022/03/17 21:27:10] root DEBUG: rec_res num : 78, elapse : 1.2926230430603027
```

```python
# Đọc file Excel và hiển thị
import pandas as pd
df = pd.read_excel('1.xlsx').fillna('')
print(df)
```

Kết quả hiển thị bảng dữ liệu đã nhận dạng thành công với các cột Methods, R, P, F, FPS.

### 8.2.2 Giải thích Nguyên lý Dự đoán

#### Giới thiệu Pipeline tổng thể

Thuật toán table recognition model của PP-Structure là end-to-end algorithm.

Thuật toán nhận dạng bảng bao gồm 3 models:
1. **Text detection model:** Phát hiện text đơn dòng trong bảng.
2. **Text recognition model:** Nhận dạng text đã phát hiện.
3. **Table structure và cell prediction model:** Dự đoán thông tin HTML của cấu trúc bảng và tọa độ cell.

Quy trình:
1. Dùng text detection model phát hiện text đơn dòng trong bảng;
2. Dùng text recognition model nhận dạng text đã phát hiện. Tại bước này, ta có text box và text information;
3. Dùng table structure và cell prediction model để dự đoán HTML information của cấu trúc bảng và tọa độ cell;
4. Aggregate text box ở bước 1 và cell coordinates ở bước 3. Xác định có cần aggregation hay không dựa trên IOU giữa text detection boxes (đỏ) và cell coordinate detection boxes (xanh).
5. Sau khi aggregate text box, sắp xếp text boxes từ trên xuống dưới và từ trái sang phải. Lấy text information tương ứng theo index của sorted text boxes, rồi string splicing để lấy text content của cells.

#### Giới thiệu Table Structure Inference Model

Table recognition cần 3 models: text detection, text recognition và table structure recognition. Model text detection và recognition đã được giới thiệu, ở đây sẽ trình bày chi tiết table structure inference model.

Table structure inference model dự đoán cấu trúc bảng và phát hiện tọa độ cell. Structure model được cải tiến từ thuật toán **RARE**, với các cải tiến chính:

#### Input Data

Với text recognition model, mỗi ký tự được đánh dấu trong dataset là độc lập, nhưng trong table structure inference model, category cần dự đoán không phải là ký tự đơn. So sánh dictionary giữa RARE và table structure model:

| Model | Dictionary |
|---|---|
| RARE | `'<', 's', 'u', 'p', '>', '<', '/', 's', 'u', 'b', '>', '<', 'b', '>', '<', '/', 'b', '>', '<', '/', 'i', '>', '<', '/', 'Y', '>'` |
| Table structure model | `'sos', '<thead>', '<tr>', '<td>', '</td>', '</tr>', '</thead>', '<tbody>', '</tbody>', '<td', ' colspan="5"', '>', ' colspan="2"', ' colspan="4"', ' colspan="6"', ' rowspan="3"', ' colspan="3"', ' colspan="9"', ' colspan="7"', ' rowspan="4"', ' rowspan="5"', ' rowspan="9"', ' colspan="8"', ' rowspan="8"', ' rowspan="6"', ' rowspan="7"', ' rowspan="10"', 'eos'` |

Table structure inference model coi một chuỗi như `<thead>` là một ký tự để nhận dạng.

#### Model

So sánh giữa table structure recognition model và RARE:

- **RARE model** gồm: TPS + CNN + RNN (BLSTM) + AttentionHead
  - TPS: Chỉnh sửa text cong trong ảnh
  - CNN: Trích xuất features từ ảnh
  - RNN: Tăng cường features và trích xuất semantic features
  - AttentionHead: Thực hiện output

- **Table Structure Net** gồm: CNN + AttentionHead (bỏ TPS và RNN)
  - Bỏ TPS vì input image là ảnh bảng hoàn chỉnh (không cần chỉnh cong)
  - Bỏ RNN vì thực nghiệm cho thấy RNN ít ảnh hưởng đến kết quả
  - Thêm nhánh: **Structure out** (output HTML tags) + **Cell location out(N*4)** (regression tọa độ cell)

Để output tọa độ cell, đã thử detect cell coordinates trong detection model. Dựa trên DB model, 2 phương án đã được đề xuất:

| Phương án | Mô tả | Kết quả |
|---|---|---|
| 1. Single-line text detection | Chỉ detect text | Baseline |
| 2. Một model detect texts và cells | Dùng cùng model | Phân biệt khó giữa cell và text trong GT |
| 3. Hai model riêng | Detect texts và cells riêng | Tốt hơn nhưng phức tạp |

Có thể thấy rằng detect texts và cells trong segmentation model sẽ dẫn đến vấn đề: GT của background giữa mỗi dòng trong cell là background hay text? Trong 3 models của pipeline, chỉ text detection và table structure recognition có thể lấy thông tin toàn bộ ảnh. Do đó, thêm regression-based branch vào AttentionHead của table structure recognition model để detect tọa độ cell (x0, y0, x1, y1).

#### Forward Analysis của Table Structure Inference Model

Forward analysis phân tích sự thay đổi output shape trong mỗi module từ preprocessing image input đến network output, để hiểu rõ hơn table cell inference và table structure inference models. Các modules liên quan:

| Type | Module Name |
|---|---|
| Data Processing | ResizeTableImage |
| Data Processing | PaddingTableImage |
| Backbone | MobileNetV3 |
| Head | TableAttentionHead |

#### Input Data Processing

Trong ví dụ này, input image và output của data processing module:

```python
# Chuyển đến thư mục PaddleOCR
os.chdir('../')
from ppocr.data import create_operators, transform
plt.figure(figsize=(24, 8))

# Đọc input image
img = cv2.imread('doc/table/table.jpg')

# Hiển thị input image
plt.subplot(1, 3, 1)
plt.title('src, shape:{}'.format(img.shape))
plt.imshow(img)

# Thực hiện ResizeTableImage
# Scale cạnh dài về specified length, scale cạnh ngắn theo tỉ lệ tương ứng
pre_process_list = [{'ResizeTableImage': {'max_len': args.table_max_len}}]
preprocess_op = create_operators(pre_process_list)
data = {'image': img}
data = transform(data, preprocess_op)

# Hiển thị ảnh sau ResizeTableImage
plt.subplot(1, 3, 2)
plt.title('ResizeTableImage, shape:{}'.format(data['image'].shape))
plt.imshow(data['image'])

# Thực hiện PaddingTableImage
pre_process_list = [{'PaddingTableImage': None}]
preprocess_op = create_operators(pre_process_list)
data = transform(data, preprocess_op)

# Hiển thị ảnh sau PaddingTableImage
plt.subplot(1, 3, 3)
plt.title('PaddingTableImage, shape:{}'.format(data['image'].shape))
plt.imshow(data['image']/255)
plt.show()

# Định nghĩa list processing ops đầy đủ
pre_process_list = [
    {'ResizeTableImage': {'max_len': args.table_max_len}},
    {'NormalizeImage': {'scale': 1./255., 'mean': [0.485, 0.456, 0.406], 'std': [0.229, 0.224, 0.225], 'order': 'hwc'}},
    {'PaddingTableImage': None},
    {'ToCHWImage': None}
]
preprocess_op = create_operators(pre_process_list)
data = {'image': img}
data = transform(data, preprocess_op)
```

Ảnh hiển thị 3 giai đoạn: src (ảnh gốc), ResizeTableImage (đã scale), PaddingTableImage (đã padding thành kích thước cố định).

#### Backbone

Backbone giống với detected backbone, đều output 4 feature maps với kích thước 1/4, 1/8, 1/16 và 1/32 của input image. Các backbones liên quan đã được giới thiệu trong chương text detection, sẽ không lặp lại ở đây.

```python
# https://github.com/PaddlePaddle/PaddleOCR/blob/dygraph/ppocr/modeling/backbones/det_mobilenet_v3.py

from ppocr.modeling.backbones import build_backbone
# Khởi tạo backbone
backbone = build_backbone(dict(name='MobileNetV3', scale=1.0, model_name='large'), model_type='table')
backbone.eval()
# Load backbone parameters
backbone.set_state_dict(backbone_dict)

import numpy as np
x = np.expand_dims(data['image'], axis=0)
```

Tải pre-trained model:

```bash
! wget -P ./pretrained_models/ https://paddleocr.bj.bcebos.com/dygraph_v2.1/table/en_ppocr_mobile_v2.0_table_structure_train.tar && cd pretrained_models && tar xf en_ppocr_mobile_v2.0_table_structure_train.tar && cd ..
```

```python
# Tải pre-trained model đã download
import paddle
pretrain_params = paddle.load('pretrained_models/en_ppocr_mobile_v2.0_table_structure_train/best_accuracy.pdparams')

def filter_params(pretrain_params, prefix):
    new_dict = {}
    for k, v in pretrain_params.items():
        if k.startswith(prefix):
            new_dict[k.replace(prefix+'.', '')] = v
    return new_dict

# Trích xuất parameters
backbone_dict = filter_params(pretrain_params, 'backbone')
head_dict = filter_params(pretrain_params, 'head')
```

---

*— Hết phần dịch trang 200–250 —*

Phần tiếp theo (trang 250+) sẽ tiếp tục với:
- 8.2.2 (tiếp) Forward analysis: Head (TableAttentionHead), Loss, Metric
- 8.2.3 Huấn luyện Table Recognition
- 8.3 Thực hành KIE (Key Information Extraction) với PP-Structure
- Chương 9+ — Các chủ đề nâng cao

**Tài nguyên:**
- Repo: https://github.com/PaddlePaddle/PaddleOCR
- PP-Structure: PaddleOCR/ppstructure/
- Table recognition code: PaddleOCR/ppstructure/table/
- Layout analysis: PaddleOCR/ppstructure/layout/
