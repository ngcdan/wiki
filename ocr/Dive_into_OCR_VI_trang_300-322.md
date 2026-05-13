# Dive into OCR — Bản dịch tiếng Việt (Trang 300–322)

*Tiếp nối từ file dịch trang 250–300. Đây là bản dịch đầy đủ, phần cuối cùng của sách. Technical terms giữ nguyên tiếng Anh.*

> Tài liệu gốc: https://github.com/PaddlePaddle/PaddleOCR (release/2.4)

---

## Chương 10 — Thuật toán Tiền xử lý (tiếp)

### 10.2 Data Augmentation (tiếp)

#### 10.2.1 Standard Data Augmentation (tiếp — trang 294–295)

**TIA distort** — biến dạng ảnh bằng cách chia ảnh thành segments và dịch chuyển ngẫu nhiên các control points:

```python
def tia_distort(src, segment=4):
    img_h, img_w = src.shape[:2]

    cut = img_w // segment
    thresh = cut // 3

    src_pts = list()
    dst_pts = list()

    src_pts.append([0, 0])
    src_pts.append([img_w, 0])
    src_pts.append([img_w, img_h])
    src_pts.append([0, img_h])

    dst_pts.append([np.random.randint(thresh), np.random.randint(thresh)])
    dst_pts.append(
        [img_w - np.random.randint(thresh), np.random.randint(thresh)])
    dst_pts.append(
        [img_w - np.random.randint(thresh), img_h - np.random.randint(thresh)])
    dst_pts.append(
        [np.random.randint(thresh), img_h - np.random.randint(thresh)])

    half_thresh = thresh * 0.5

    for cut_idx in np.arange(1, segment, 1):
        src_pts.append([cut * cut_idx, 0])
        src_pts.append([cut * cut_idx, img_h])
        dst_pts.append([
            cut * cut_idx + np.random.randint(thresh) - half_thresh,
            np.random.randint(thresh) - half_thresh
        ])
        dst_pts.append([
            cut * cut_idx + np.random.randint(thresh) - half_thresh,
            img_h + np.random.randint(thresh) - half_thresh
        ])

    trans = WarpMLS(src, src_pts, dst_pts, img_w, img_h)
    dst = trans.generate()

    return dst

distort_img = tia_distort(img)
show_img(img, distort_img)
```

Kết quả: ảnh "DO NOT" gốc bị biến dạng — các phần text bị uốn cong, nghiêng theo các segment.

**TIA stretch** — kéo giãn ảnh bằng cách dịch chuyển các control points theo chiều ngang:

```python
def tia_stretch(src, segment=4):
    img_h, img_w = src.shape[:2]

    cut = img_w // segment
    thresh = cut * 4 // 5

    src_pts = list()
    dst_pts = list()

    src_pts.append([0, 0])
    src_pts.append([img_w, 0])
    src_pts.append([img_w, img_h])
    src_pts.append([0, img_h])

    dst_pts.append([0, 0])
    dst_pts.append([img_w, 0])
    dst_pts.append([img_w, img_h])
    dst_pts.append([0, img_h])

    half_thresh = thresh * 0.5

    for cut_idx in np.arange(1, segment, 1):
        move = np.random.randint(thresh) - half_thresh
        src_pts.append([cut * cut_idx, 0])
        src_pts.append([cut * cut_idx, img_h])
        dst_pts.append([cut * cut_idx + move, 0])
        dst_pts.append([cut * cut_idx + move, img_h])

    trans = WarpMLS(src, src_pts, dst_pts, img_w, img_h)
    dst = trans.generate()

    return dst

stretch_img = tia_stretch(img)
show_img(img, stretch_img)
```

Kết quả: ảnh "DO NOT" bị kéo giãn — một số ký tự bị co lại hoặc giãn ra theo chiều ngang.

---

#### 10.2.2 Image Transformation Techniques (Kỹ thuật biến đổi ảnh — trang 296–297)

Transformation nghĩa là thực hiện một số biến đổi trên ảnh sau RandCrop. Chủ yếu bao gồm:

- **AutoAugment**
- **RandAugment**
- **TimmAutoAugment**

Khác với các phương pháp augmentation ảnh được thiết kế thủ công truyền thống, **AutoAugment** [2] là giải pháp image augmentation phù hợp cho một dataset cụ thể, được tìm thấy bởi một thuật toán search nhất định trong không gian tìm kiếm của một loạt image augmentation sub-strategies. Đối với ImageNet dataset, giải pháp data augmentation cuối cùng chứa 25 sub-strategy combinations. Mỗi sub-strategy chứa hai transformations. Với mỗi ảnh, một sub-strategy combination được chọn ngẫu nhiên và rồi với một xác suất nhất định thực hiện mỗi transformation trong sub-strategy.

Phương pháp search của AutoAugment [3] khá tốn kém. Tìm kiếm optimal strategy cho dataset này trực tiếp trên dataset đó đòi hỏi rất nhiều computation. Trong **RandAugment**, tác giả phát hiện rằng:
- Với các models lớn hơn và datasets lớn hơn, gains từ augmentation method được search bằng AutoAugment nhỏ hơn
- Mặt khác, searched strategy bị giới hạn cho dataset cụ thể, có poor generalization performance và không phù hợp cho datasets khác

Trong RandAugment, tác giả đề xuất phương pháp random augmentation. Thay vì dùng xác suất cụ thể để xác định có dùng sub-strategy nào không, tất cả sub-strategies được chọn với cùng xác suất. Thí nghiệm trong bài báo cũng cho thấy phương pháp này hoạt động tốt kể cả cho large models.

**TimmAutoAugment** là cải tiến của AutoAugment và RandAugment bởi các tác giả open source. Thực tế đã chứng minh rằng nó có performance tốt hơn trên nhiều visual tasks. Hiện tại, hầu hết VisionTransformer models được triển khai dựa trên TimmAutoAugment.

---

#### 10.2.3 Image Cropping Techniques (Kỹ thuật cắt ảnh — trang 297–299)

Cropping nghĩa là thực hiện một số biến đổi trên ảnh sau Transpose, set pixel values của vùng đã crop thành hằng số nhất định. Chủ yếu bao gồm:

- **CutOut**
- **RandErasing**
- **HideAndSeek**
- **GridMask**

Image cropping methods có thể thực hiện trước hoặc sau normalization. Sự khác biệt là nếu crop ảnh trước normalization và fill vùng bằng 0, pixel values của vùng đã crop sẽ không bằng 0 sau normalization, gây grayscale distribution change của dữ liệu. Các ý tưởng cropping transformation nêu trên đều tương tự nhau — tất cả nhằm giải quyết vấn đề poor generalization ability của trained model trên occlusion images, khác biệt nằm ở chi tiết cropping.

**Cutout** [4] là một loại dropout, nhưng occludes input image thay vì feature map. Nó robust hơn với noise. Cutout có hai ưu điểm:
1. Dùng Cutout, chúng ta có thể simulate tình huống khi subject bị partially occluded
2. Nó promote model tận dụng nhiều nội dung hơn trong ảnh cho classification, và ngăn network chỉ focus vào saliency area, từ đó tránh overfitting

**RandomErasing** [5] tương tự Cutout. Cũng nhằm giải quyết vấn đề poor generalization ability trên occlusion images. Tác giả chỉ ra rằng random cropping bổ sung cho random horizontal flipping. Tác giả cũng xác minh effectiveness trên pedestrian re-identification (REID). Khác với Cutout, RandomErasing hoạt động trên ảnh với xác suất nhất định, kích thước và aspect ratio của mask cũng được randomly generated theo pre-defined hyperparameters.

**HideAndSeek** [6]: Ảnh được chia thành các patches và masks được generate với xác suất nhất định cho mỗi patch.

**GridMask** [7]: tạo mask có cùng resolution với ảnh gốc và multiply với ảnh gốc. Mask grid và size được điều chỉnh bởi hyperparameters. Trong training, có hai cách sử dụng:
- Set xác suất p và dùng GridMask augment ảnh với xác suất p từ đầu training
- Ban đầu set augmentation probability = 0, và tăng probability dần theo số iterations từ 0 đến p

Phương pháp thứ hai cho kết quả tốt hơn.

---

#### 10.2.4 Image Mixing Techniques (Kỹ thuật trộn ảnh — trang 300)

Mix nghĩa là thực hiện một số biến đổi trên ảnh sau Batch, bao gồm:

- **Mixup**
- **Cutmix**

Các phương pháp data augmentation giới thiệu trước đều dựa trên single image, trong khi mixing được thực hiện trên một batch nhất định để generate batch mới.

**Mixup** [8] là giải pháp đầu tiên cho image aliasing, dễ triển khai và hoạt động tốt không chỉ trên image classification mà còn object detection. Mixup thường được thực hiện trong một batch cho đơn giản. Ảnh sau Mixup cho thấy sự chồng lấp (overlay) giữa hai ảnh khác nhau trong batch.

Khác với Mixup cộng trực tiếp hai ảnh, với **Cutmix** [9], một ROI được cut out từ một ảnh và Cutmix randomly cắt một ROI từ một ảnh, rồi cover lên vùng tương ứng trong ảnh khác. Ảnh sau Cutmix cho thấy một phần ảnh A được thay thế bằng patch từ ảnh B.

---

### 10.3 Image Binarization (Nhị phân hóa ảnh — trang 301–303)

Image binarization là đặt grayscale values của pixels thành 0 hoặc 255, để toàn bộ ảnh thể hiện hiệu ứng black-white rõ ràng. Mỗi pixel trong binary image chỉ có hai giá trị: 0 (đen) và 255 (trắng). Image binarization có thể giảm nhiễu, loại bỏ background interference và highlight contours của object. OCR text recognition performance cải thiện nếu binarization phân biệt được foreground và background.

Các phương pháp binarization phổ biến được chia thành: global binarization, local binarization, và deep learning methods.

#### 10.3.1 Global Thresholding

Global thresholding xử lý toàn bộ pixel trong ảnh bằng cùng một threshold value. Các phương pháp bao gồm fixed thresholding, Otsu, v.v.

**Fixed threshold method** dùng giá trị cố định cho tất cả pixels làm global threshold T. Nếu pixel value của current pixel >= T → gán 255, ngược lại → gán 0. Thường cần thử nhiều thresholds khác nhau để quan sát binarization effect, và khó xác định optimal threshold cho từng ảnh.

Để khắc phục vấn đề này, học giả Nhật Bản Nobuyuki **Otsu** [10] năm 1979 đề xuất adaptive thresholding approach. Otsu chia ảnh thành foreground và background. Variance giữa pixels càng lớn → correlation càng thấp → foreground và background càng phân biệt. Do đó, tính variance giữa gray value của mỗi pixel trong ảnh để tìm gray value có maximum variance — đó chính là binarization threshold.

Ví dụ minh họa: ảnh biển báo "EPPING" — (a) ảnh gốc, (b) binary với T=40, (c) binary với T=120. Threshold khác nhau cho kết quả binarization khác nhau.

#### 10.3.2 Local Thresholding

Nếu ảnh có vấn đề như uneven illumination, binarization methods dựa trên global threshold sẽ không đạt hiệu quả mong muốn. Trong trường hợp này, binarization method dựa trên local threshold phù hợp hơn. Các phương pháp local thresholding phổ biến: **adaptive thresholding algorithm** [11], **NiBlack** [12], **Sauvola** [13], v.v.

Trong **adaptive thresholding algorithm**, có sliding window kích thước s×s centered trên một pixel, quét toàn bộ ảnh. Trong mỗi slide, pixels trong current window được averaged và average value được dùng làm local threshold T. Nếu value pixel < T/100 → gán 0, nếu > T/100 → gán 255.

**NiBlack** tính mean m và variance s của pixels trong local region, rồi tính local threshold: T = m + k × s, trong đó k là correction factor (giá trị 0-1). Binarization thực hiện theo threshold T.

**Sauvola** là cải tiến từ NiBlack. Tính local threshold: T = m − [1 + k − (frac{s}{R} − 1)], trong đó R là dynamic range của variance. Nếu input image hiện tại là 8-bit grey-scale image, R = 128. Sauvola hoạt động tốt hơn NiBlack trong tình huống uneven illumination.

#### 10.3.3 Techniques Based on Deep Learning

Các phương pháp binarization global và local truyền thống khó set appropriate thresholds, dẫn đến poor image binarization effect. Với sự phát triển liên tục của deep learning, một số nhà nghiên cứu đã bắt đầu thử dùng neural networks để binarize images:

- **Pratikakis I et al** [14]: dùng **U-Net** convolutional neural network architecture cho document image binarization trong cuộc thi ICDAR2017 DIBCO và giành championship
- **Chris Tensmeyer et al** [15]: dùng multi-scale **full convolutional neural network** để binarize document images
- **Vo QN et al** [16]: đề xuất hierarchical **deep supervised network (DSN)** cho document binarization
- **Westphal F et al** [17]: dùng **Grid Long Short Term Memory (Grid LSTM)** network cho binarization. Tuy nhiên, performance thấp hơn phương pháp [16]
- **Calvo-Zaragoza J et al** [18]: dùng deep **encoder và decoder** architecture để đạt binarization

---

### 10.4 Denoising (Khử nhiễu — trang 303–306)

Image noise là unnecessary hoặc redundant interference information tồn tại trong image data. Nó có thể ảnh hưởng nghiêm trọng đến data quality, nên thường cần xử lý noise. Đồng thời, cần maintain details của ảnh khi removing noise. Các phương pháp denoising được phân thành 4 nhóm: spatial domain filtering, transform domain filtering, non-local filtering, và methods based on neural network.

#### 10.4.1 Spatial Domain Filtering

Spatial domain filtering xử lý pixel values bằng cách thực hiện data operations trực tiếp trên original image. Các thuật toán spatial domain filtering denoising phổ biến: **mean filter**, **Gaussian filter**, **median filter**, **bilateral filter** [19], **Non-Local Means (NLM) algorithm** [20], v.v.

**Mean filter** dùng average pixel value trong vùng lân cận pixel A để thay thế original pixel value của pixel A. Là typical smoothing linear filter. Mean filter đơn giản và tính toán nhanh, đóng vai trò smoothing toàn bộ ảnh. Tuy nhiên, không preserve image details, làm ảnh bị blurred.

**Gaussian filter** cũng là linear filter và là thuật toán filtering phổ biến. Sau Gaussian filter, value mỗi image pixel được thay bằng weighted average value của chính nó và các pixel khác trong field. So với mean filter, Gaussian filter performs better on smoothing và better preserve edge information, đồng thời suppress Gaussian noise.

**Median filter** thay thế image pixel value bằng median của neighbourhood grey values của target pixel. Là non-linear filter, phù hợp xử lý **salt-and-pepper noise** và preserve image edge details.

**Bilateral filter** xem xét không chỉ spatial distance của pixels, mà cả similarity giữa pixels và colour intensity.

Bốn filters được triển khai với thư viện OpenCV:

```python
noise_img = cv2.imread('preprocess/noise.png')
# Mean filter
img_mean = cv2.blur(noise_img, (5,5))
show_img(noise_img, img_mean)
# Gaussian filter
img_gussian = cv2.GaussianBlur(noise_img, (5,5), 1)
show_img(noise_img, img_gussian)
# Median filter
img_median = cv2.medianBlur(noise_img, 5)
show_img(noise_img, img_median)
# Bilateral filter
img_bilater = cv2.bilateralFilter(noise_img, 3, 15, 15)
show_img(noise_img, img_bilater)
```

Kết quả visualization trên ảnh Lena: mean filter cho ảnh smooth nhất (mờ nhất), Gaussian filter smooth nhưng giữ edges tốt hơn, median filter preserve edges tốt nhất, bilateral filter cân bằng giữa smoothing và edge preservation.

Các filters dựa trên neighbourhood pixels cơ bản chỉ xem xét gray value information của pixels trong sliding window, mà không xem xét statistical information (như variance, pixel distribution characteristics, prior knowledge of noise). Với những hạn chế này, **NLM algorithm** đã được đề xuất — sử dụng redundant information trong ảnh để loại bỏ noise và giữ lại maximum detailed features. NLM method dùng toàn bộ ảnh để denoising bằng cách tìm similar regions trong ảnh theo blocks, tính weighted average của các regions này để lấy denoised image. Similarity được tính bằng weighted Euclidean distance, và tỉ lệ thuận với weight.

---

### 10.5 Transform Domain Filtering (Lọc miền biến đổi — trang 306)

Transform domain filtering methods chuyển ảnh từ original spatial domain sang transform domain. Trong transform domain, noise có thể chia thành high, medium và low frequency noises, và các different frequency noises có thể được tách bởi transform domain method. Sau đó ảnh được chuyển ngược từ transform domain về original space domain bằng inverse transformation, loại bỏ image noise. Có nhiều cách chuyển đổi, bao gồm **Fourier transform**, **wavelet transform**, v.v.

**Fourier transform** chuyển input image từ spatial domain sang frequency domain, chứa cả low và high frequency information. Các điểm trên ảnh nơi grey values thay đổi nhanh thường là high frequency noise trong ảnh. Low-pass filter với Fourier transform loại bỏ high-frequency component của ảnh và chỉ cho low-frequency information đi qua filter, từ đó đạt mục đích loại bỏ image noise.

**Wavelet transform** denoising thực hiện qua 3 bước:
1. **Wavelet decomposition**: chọn wavelet và số layers N, áp dụng N layers wavelet decomposition cho signal s
2. **Non-linear threshold quantization của wavelet transform coefficients**: chọn threshold cho mỗi layer từ 1 đến N, high-frequency coefficient của layer đó được quantized, low-frequency coefficient không xử lý
3. **Wavelet coefficient reconstruction**: dựa trên low frequency coefficient của Nth layer và high frequency coefficients của 1–N layers sau xử lý, thực hiện wavelet reconstruction của original signal

Chìa khóa của wavelet transform denoising nằm ở threshold value. Threshold function có thể chia thành **hard threshold function** và **soft threshold function**.

#### 10.5.1 BM3D

**BM3D** (Block-matching and 3D filtering) [21] kết hợp spatial domain filtering và transform domain filtering techniques. Đầu tiên dùng phương pháp computing similar blocks trong NLM, rồi tích hợp wavelet transform denoising method. Thuật toán tìm similar blocks bằng similarity determination và combine chúng thành 3D groups. Các 3D groups sau đó được transformed vào wavelet domain, nơi hard thresholding hoặc Wiener filtering được dùng để giảm noise. Cuối cùng, inverse transformation process được thực hiện để aggregate tất cả image blocks và thu được noise-reduced image.

#### 10.5.2 Methods based on Deep Learning

Với sự phát triển của deep learning, denoising algorithms dựa trên deep learning liên tục xuất hiện, và CNN-based denoising methods đã cải thiện denoising effect. Các phương pháp phổ biến dựa trên deep learning bao gồm **DnCNNs** [22], **FFDNet** [23], **MPRNet** [24], v.v.

- **DnCNNs** (Denoising CNNs): giới thiệu **residual learning** và **batch normalisation** vào image denoising lần đầu tiên. Sự kết hợp của hai phương pháp enhance lẫn nhau, effectively improve training speed và denoising performance.

- **FFDNet** (Fast and Flexible Denoising NetWork): hoạt động trên **downsampled sub-images**, đạt good balance giữa training/inference speed và enlarging receptive field. Đồng thời dùng **orthogonal regularization** để enhance generalization.

- **MPRNet**: đầu tiên learns contextualized features dùng **encoder-decoder architectures** với large receptive field. Rồi combines chúng với **high-resolution branch** giữ lại local information cần thiết. MPRNet có thể áp dụng trong nhiều scenarios như rain removal, deblurring, denoising, v.v.

---

### 10.6 Summary (Tổng kết — trang 307)

Phần này tập trung vào các phương pháp phổ biến của data augmentation, binarization và denoising trong image pre-processing.

Đầu tiên, để improve robustness của model, data augmentation thường được dùng trên training samples. 4 loại kỹ thuật data augmentation được giới thiệu:

1. **Standard data augmentation techniques**: rotation, perspective transformation, blurring, Gaussian noise, random cropping, v.v.
2. **Image transformation techniques**: transform ảnh sau RandCrop — AutoAugment và RandAugment
3. **Image cropping techniques**: crop ảnh sau transposition và set pixel values của cropped region thành hằng số (mặc định là 0) — CutOut, RandErasing, HideAndSeek và GridMask
4. **Image mixing techniques**: mix data sau batch processing — Mixup và Cutmix

Thứ hai, binary images chất lượng cao có thể effectively cải thiện text recognition performance. Global thresholding (Fixed Thresholding, Otsu), local thresholding (Adaptive Thresholding, NiBlack, Sauvola, Bernsen) và methods based on deep learning (U-Net, Grid LSTM, Full Convolutional Neural Network, v.v.) được giới thiệu chính.

Thứ ba, trong thời đại big data khi chất lượng ảnh không đồng đều, image filtering ngày càng được sử dụng nhiều. Phần này cũng giới thiệu ngắn gọn một số image denoising methods, bao gồm spatial domain filtering, transform domain filtering, BM3D và filtering based on deep learning.

---

---

# Chương 11 — Thuật toán Tổng hợp Dữ liệu (Data Synthesis Algorithms) (trang 309–315)

## 11.1 Background (Nền tảng)

Performance của deep learning methods liên quan chặt chẽ đến quality và quantity của training data, nhưng việc thu thập massive annotated data đã trở thành bottleneck cho efficient development của nhiều deep learning tasks. Images của different scenes trong OCR tasks có unique styles về fonts, blurs, lighting, v.v. Collecting đủ data là challenging và costly, và manual annotation cũng time-consuming và error-prone.

Do đó, trong trường hợp thiếu sufficient annotated data, automatic synthesis của annotated images ngày càng được chú ý, vì nó successfully giảm bớt shortage of data và problem of manual data annotation. Trong trường hợp OCR, synthesised data quan trọng trong training OCR text detection và recognition models và đã proved effective trong nhiều algorithms.

Trong phần này, một số representative data synthesis methods gần đây sẽ được trình bày, bao gồm **SynthText**, **Verisimilar**, **SynthText3D**, **SF-GAN**, **SRNet**, **ScrabbleGAN**, **UnrealText**.

## 11.2 Data Synthesis Algorithms (trang 309–315)

### SynthText

Ankush Gupta et al. (2016) [1] đề xuất **SynthText** — phương pháp mới synthesize text images bằng cách overlay synthetic text lên background images trong natural scenes. Quy trình synthesis gồm 5 bước:
1. Thu thập lượng lớn text-free background images, fonts và text corpora
2. Ảnh được segmented thành contiguous regions dựa trên local colour và texture cues, và dùng CNN để obtain dense pixel-wise depth map
3. Lấy candidate region theo semantic và depth information
4. (Tùy chọn) Chọn colour của text và outline theo colour của candidate region
5. Render text bằng randomly selected font

Kết quả: text được overlay tự nhiên lên background images — ví dụ chữ "to the" trên bàn, "blarp" trên cốc, text trên các bề mặt phù hợp trong scene.

### Verisimilar

Fangneng Zhan et al. (2018) [2] đề xuất **Verisimilar** — novel image synthesis technique nhằm generate massive annotated scene text images cho training accurate và robust scene text detection và recognition models.

Tác giả kết hợp **semantic segmentation** và **visual saliency** trong text synthesis:
- Giới thiệu semantic segmentation để text chỉ xuất hiện trên perceptible object (ví dụ scene texts thường xuất hiện trên tường hoặc bề mặt bàn, không phải trên thức ăn hay lá cây)
- Dùng visual saliency để xác định embedding locations của text, và phân biệt text với background
- Thiết kế novel scene text appearance model xác định color và brightness của source texts bằng cách learning từ feature của real scene text images adaptively

Phương pháp hoạt động tốt trong training accurate và robust scene text detection và recognition models, và realizes synthesis of verisimilar scene text images.

### SynthText3D

Minghui Liao et al. (2019) [3] đề xuất **SynthText3D** — model synthesizing scene text images trong 3D virtual worlds. Bằng cách này, real-world variations bao gồm complex perspective transformations, various illuminations, và occlusions có thể được realize trong synthesized scene text images.

Cụ thể, text instances trong various fonts được firstly embedded vào suitable positions trong 3D virtual worlds. Synthetic images sản xuất từ 3D virtual worlds yield fantastic visual effects, bao gồm various illuminations, occlusions, và text cùng background scene được rendered together. Cuối cùng, tác giả setup camera với different locations và orientations để produce images của same text từ different viewpoints.

Kết quả hiển thị 3 loại variations:
- (a) Various illuminations và visibility của cùng text instances
- (b) Different viewpoints của cùng text instances
- (c) Different occlusion cases của cùng text instances

### SF-GAN

Fangneng Zhan et al. (2019) [4] đề xuất **Spatial Fusion GAN (SF-GAN)** — kết hợp geometry synthesizer và appearance synthesizer để generate images approximately realistic trong cả geometry và appearance spaces.

- **Geometry synthesizer**: learns contextual geometries của background images và transforms và places foreground objects vào background images unanimously
- **Appearance synthesizer**: adjusts color, brightness và style của foreground objects
- Tác giả cũng thiết kế **fusion network** giới thiệu detail-preserving guide filters để preserve realistic appearance

Kết quả: Foreground text (NECK, GARDEN, BANK, INDIA) được overlay tự nhiên lên Background images, tạo SF-GAN output với lighting, perspective và style phù hợp.

### SRNet

Liang Wu et al. (2019) [5] đề xuất **SRNet** (Style Retention Network) — end-to-end trainable network thay đổi content của source image thành target text trong khi giữ original image style. Framework Style-Text gồm 3 modules:

1. **Style migration module** của text foreground: thay thế text content của source image bằng target text, và preserve original text region đồng thời
2. **Background extraction module**: erases original text và fills text region bằng appropriate texture
3. **Fusion module**: combines information từ hai modules trước và generates edited text images

Sau 3 bước này, image text style có thể được quickly migrated. Ví dụ: "PRELIMINARY" → style migration → background extraction → synthetic text image, áp dụng cho nhiều ngôn ngữ (English, Chinese, Korean).

### ScrabbleGAN

Sharon Fogel et al. (2020) [6] đề xuất **ScrabbleGAN** — semi-supervised approach để synthesize handwritten text images.

Semi-supervised approach có thể dùng cả unlabelled data để train handwritten text synthesis framework bên cạnh labeled data. ScrabbleGAN dựa trên fully convolutional generator model mới có thể generate images với arbitrarily long words hoặc thậm chí complete sentences.

Ngoài ra, ScrabbleGAN's generator có thể control style của generated text. Ví dụ, cho phép thay đổi text cursive hay không, hoặc nét bút thin hay thick.

Kết quả: từ "Supercalifragilisticexpialidocious" được generate với nhiều handwriting styles khác nhau — từ neat đến cursive, từ thin đến thick strokes.

### UnrealText

Shangbang Long et al. (2020) [7] đề xuất **UnrealText** — phương pháp effective image synthesis khác, tổng hợp synthetic scene text images từ 3D virtual world. UnrealText dựa trên game engine nổi tiếng **Unreal Engine 4 (UE4)**.

Cụ thể, text instances được coi là **planar polygon meshes** với text foregrounds loaded as texture, và được placed vào suitable positions trong 3D world. Text và scene được rendered together as whole, đạt realistic visual effects như illumination, occlusion, và perspective transformation.

UnrealText engine đạt realistic rendering và high scalability, significantly improves performance của text detectors và model generation. Ngoài ra, large-scale multilingual scene text dataset cũng được constructed, hữu ích cho further research.

Kết quả: ảnh synthetic với effects — Lighting & Shadows, Suitable Text Region, Occlusion — tất cả đều realistic.

---

## 11.3 Summary (Tổng kết)

Public datasets trong text detection và recognition có thể không đáp ứng demand của current application scenarios hoặc số lượng datasets nhỏ. Hơn nữa, manual annotation of data là time-consuming và labour-intensive, nên OCR data synthesis đã trở thành common practice.

Trong phần này, chúng ta đã tóm tắt một số data synthesis methods, bao gồm SynthText, SynthText3D, SF-GAN, SRNet, v.v. OCR data được generate thông qua các methods này, giúp improves performance của text detection và recognition.

---

## 11.4 References

[1] Gupta A, Vedaldi A, Zisserman A. Synthetic data for text localisation in natural images[C]//Proceedings of the IEEE conference on computer vision and pattern recognition. 2016: 2315-2324.

[2] Zhan F, Lu S, Xue C. Verisimilar image synthesis for accurate detection and recognition of texts in scenes[C]//Proceedings of the European Conference on Computer Vision (ECCV). 2018: 249-266.

[3] Liao M, Song B, Long S, et al. SynthText3D: synthesizing scene text images from 3D virtual worlds[J]. Science China Information Sciences, 2020, 63(2): 1-14.

[4] Zhan F, Zhu H, Lu S. Spatial fusion gan for image synthesis[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2019: 3653-3662.

[5] Wu L, Zhang C, Liu J, et al. Editing text in the wild[C]//Proceedings of the 27th ACM international conference on multimedia. 2019: 1500-1508.

[6] Fogel S, Averbuch-Elor H, Cohen S, et al. Scrabblegan: Semi-supervised varying length handwritten text generation[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2020: 4324-4333.

[7] Long S, Yao C. Unrealtext: Synthesizing realistic scene text images from the unreal world[J]. arXiv preprint arXiv:2003.10608, 2020.

---

*— HẾT — Toàn bộ sách Dive into OCR (322 trang) đã được dịch sang tiếng Việt —*

## Tổng quan toàn bộ sách

| Chương | Nội dung | File dịch |
|--------|----------|-----------|
| 1–2 | Giới thiệu OCR, Thuật toán Text Detection | trang_1-10, trang_10-50 |
| 3–4 | Thuật toán Text Recognition, PP-OCR | trang_50-100 |
| 5–6 | Tối ưu PP-OCR, PP-OCRv2 | trang_100-150 |
| 7 | Inference & Deployment | trang_150-200, trang_200-250 |
| 8 | Document Analysis (Layout, Table, VQA/KIE) | trang_200-250, trang_250-300 |
| 9 | End-to-End Algorithm | trang_250-300 |
| 10 | Pre-processing (Augmentation, Binarization, Denoising) | trang_300-322 |
| 11 | Data Synthesis Algorithms | trang_300-322 |
