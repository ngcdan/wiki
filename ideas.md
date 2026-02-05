Chụp các bill, chuyển khoản, data lịch sử giao dịch cho bot để tự ocr add vào transactions

Từ đó theo dõi chi tiêu, tạo ra các budget cho các nhóm và đưa ra các chỉ số hằng ngày để chi tiêu cho hợp lý.

Với việc mua sắm, hãy thêm các món đồ muốn mua và check website hàng ngày để tìm giá ưu đãi hoặc các đợt giảm giá để có những deal hời.
Tương tự với vé máy bay và dịch vụ khác.

theo dõi cashflow, đưa ra các kinh nghiệm đầu tư tiền một cách hợp lý và có hệ thống.

---

Anh đang hướng tới một “hệ thống trợ lý tài chính cá nhân” chạy theo quy trình khép kín:

1. **Thu thập dữ liệu tự động**

- Anh gửi **ảnh bill / ảnh chuyển khoản / file sao kê / lịch sử giao dịch** cho bot.
- Bot **OCR + bóc tách dữ liệu** (ngày, số tiền, merchant, nội dung, tài khoản, loại giao dịch) → chuẩn hoá thành **Transactions**.
- Có cơ chế **xác nhận nhanh** khi OCR/categorize không chắc (1–2 tap).

2. **Phân loại & theo dõi chi tiêu – cashflow**

- Tự **gán nhóm chi tiêu** (ăn uống, di chuyển, nhà ở, giải trí, sức khoẻ, học tập, v.v.).
- Theo dõi **cashflow**: thu nhập, chi phí cố định, chi phí biến đổi, dòng tiền ròng; xu hướng theo ngày/tuần/tháng.

3. **Budget & chỉ số điều hành hằng ngày**

- Tạo **budget theo nhóm** + cảnh báo khi vượt ngưỡng.
- Mỗi ngày bot đưa ra “**hạn mức chi

tiêu còn lại hôm nay**” dựa trên ngân sách tháng, tốc độ tiêu hiện tại, và các khoản sắp tới.

- Dashboard ngắn gọn: tổng chi hôm nay, top nhóm, dự báo cuối tháng, “điểm bất thường” (spike).

4. **Danh sách mua sắm + săn deal tự động**

- Anh thêm “**món muốn mua**” (tên, link, giá mục tiêu, deadline).
- Bot **check website hằng ngày**, theo dõi lịch sử giá, phát hiện **giảm giá/flash sale/coupon** → báo khi chạm điều kiện “deal hời”.

5. **Theo dõi giá dịch vụ (vé máy bay, booking, gói dịch vụ khác)**

- Lưu hành trình/nhu cầu (chặng bay, ngày, hãng/giờ bay ưu tiên, ngân sách).
- Bot theo dõi giá định kỳ, báo biến động, gợi ý thời điểm mua tốt hơn.

6. **Kỷ luật tài chính & gợi ý đầu tư có hệ thống**

- Từ cashflow và mục tiêu: đề xuất **quỹ dự phòng**, phân bổ “tiền tiêu/tiền tiết kiệm/tiền đầu

tư”.

- Đưa ra **nguyên tắc & checklist** (DCA, phân bổ rủi ro, tái cân bằng, tránh overtrade), kèm nhắc nhở định kỳ—mang tính “hệ thống”, không phải tips ngẫu hứng.

Nếu anh muốn, em có thể chốt lại thành 1 bản “PRD mini” 1 trang gồm: mục tiêu, luồng dữ liệu, tính năng MVP (1–2 tháng), và giai đoạn mở rộng. Anh muốn ưu tiên làm phần **OCR giao dịch + budget hằng ngày** trước hay **săn deal** trước?
