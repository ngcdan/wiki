# AI Preferences & Integration Rules

## Đối phó với Model Drift (Sự thay đổi ngầm của AI)

**Vấn đề:** Các nhà cung cấp AI liên tục âm thầm cập nhật model (Model Drift). Một prompt hoặc luồng xử lý chạy rất tốt hôm nay có thể hoàn toàn ngưng hoạt động, hoặc trả về kết quả sai lệch, ngớ ngẩn vào ngày mai.

Để không bị phụ thuộc và đứt gãy hệ thống, cần áp dụng các nguyên tắc phòng thủ sau:

### 1. Ghim phiên bản cứng (Pin Version)
- **Tuyệt đối KHÔNG** dùng các tag version động như `latest`, `gpt-4`, `claude-3-5-sonnet` trên môi trường Production.
- **Luôn fix cứng version cụ thể** (vd: `claude-3-5-sonnet-20240620`).
- Khi nhà cung cấp ra mắt version mới, phải có quá trình test kiểm chứng lại chất lượng output trước khi chủ động đổi version.

### 2. Đóng khung bằng Rules & Templates (Scaffolding)
- Không phụ thuộc vào sự "thông minh" hay khả năng suy luận tự do của model.
- Ép model sinh code/data theo đúng khung (templates), định dạng (format), và quy chuẩn (rules) cực kỳ chặt chẽ của dự án. 
- Giảm thiểu tối đa việc model tự quyết định logic cốt lõi.

### 3. Thiết kế AI Agnostic (Kiến trúc linh hoạt)
- Ứng dụng nghiệp vụ không gọi thẳng API của một nhà cung cấp duy nhất.
- Luôn gọi AI thông qua một Gateway / Abstraction Layer trung gian.
- **Mục tiêu:** Khi model của nhà cung cấp A bị lỗi, giảm chất lượng hoặc tăng giá, hệ thống chỉ cần đổi config (switch) sang model của nhà cung cấp B (OpenAI, Anthropic, Gemini...) trong 1 nốt nhạc mà không phải sửa logic code.

### 4. Đường lùi Self-host (Open-source Fallback)
- Luôn quan sát và có phương án dự phòng bằng các model mã nguồn mở (như Llama, Qwen).
- Trong trường hợp xấu nhất (bị cắt dịch vụ, lỗi toàn cầu, API thương mại thay đổi hoàn toàn), có thể tự kéo model về host nội bộ (local host) để đảm bảo hệ thống core vẫn sống và hoạt động độc lập.
