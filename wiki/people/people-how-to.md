---
title: People — Quy trình sử dụng
tags:
  - people
  - meta
created: 2026-04-18
updated: 2026-04-18
---

# People — Quy trình sử dụng

Thư mục này ghi hồ sơ đồng nghiệp + bản đồ quan hệ + playbook hành xử cho office politics. Thiết kế theo triết lý "bộ não thứ hai": mọi observation phải externalize thành note.

## Nguyên tắc nền

- **Codename only.** Tên thật chỉ tồn tại trong `people-mapping.md` (gitignored). Mọi file/note/reference khác chỉ dùng codename. Điều này cho phép vault sync cloud hoặc bị xem lướt mà không lộ danh tính.
- **Một người = một file.** Đặt tên `people-<codename>.md`.
- **Không đoán.** AI chỉ tổng hợp từ observation đã có. Thiếu data → hỏi, không tự suy diễn tính cách hay quan hệ.
- **Liên kết dày đặc.** Dùng `[[people-P02]]` thay vì viết codename trơn trong nội dung — để Obsidian graph + backlinks hoạt động.
- **Playbook là output, không phải input.** Chỉ viết guideline khi đã có đủ observation tích lũy. Đừng viết playbook dựa trên 1-2 lần tiếp xúc.

## Thêm người mới

1. Chọn codename — khuyên dùng `P01`, `P02`, ... tăng dần. Cấp cao có thể dùng `EXEC-01`, `EXEC-02`.
2. Update `people-mapping.md`: thêm dòng mapping codename ↔ tên thật + ghi chú bối cảnh (phòng ban, dự án).
3. Copy `people-template.md` → `people-<codename>.md`.
4. Điền frontmatter + các section đã biết. **Phần chưa biết để trống.** Không đoán.

## Flow cập nhật hồ sơ

Khi có data mới về một người, flow chuẩn:

1. **Capture raw** — paste Zalo chat / email / meeting note vào `raw/YYMMDD-<topic>.md`, hoặc nhắn trực tiếp cho Claude.
2. **Extract** — Claude rút gọn observation, hỏi codename người được nhắc đến.
3. **Update** — thêm entry mới vào section `## Lịch sử tương tác` của file `people-<codename>.md` tương ứng. Newest on top.
4. **Hỏi trước khi update playbook.** Nếu observation mới gợi ý thay đổi guideline hành xử, Claude phải hỏi: "Observation này có đủ cơ sở để update Playbook section không?"

## Quy ước relationship labels

Dùng nhãn chuẩn khi liệt kê quan hệ trong `## Bản đồ quan hệ`. Labels viết bằng tiếng Việt có dấu, nối bằng hyphen (không dấu cách):

- `đồng-minh` — cùng phe, lợi ích chung
- `đối-thủ` — xung đột lợi ích trực tiếp
- `trung-lập` — chưa rõ phe, chưa có xung đột
- `cố-vấn` — người mình học hỏi
- `cấp-dưới` — cấp dưới trực tiếp của mình
- `cấp-trên` — cấp trên mình báo cáo
- `đồng-cấp` — cùng level
- `phức-tạp` — quan hệ hỗn hợp (vừa hợp tác vừa cạnh tranh, frenemy)

Khi quan hệ giữa **hai người khác** (không phải mình) — cũng dùng nhãn tương tự, viết từ góc nhìn quan sát.

## Quy ước risk level

Trường `risk_level` trong frontmatter:

- `low` — tương tác an toàn, ít rủi ro chính trị
- `medium` — cần cẩn thận khi chia sẻ thông tin, có pattern bất lợi
- `high` — tránh chia sẻ thông tin nhạy cảm, cẩn trọng mọi tương tác

## Schema hồ sơ

Xem `people-template.md`. Các section bắt buộc:

- `## Hồ sơ` — vai trò, dept, báo cáo cho ai
- `## Bản đồ quan hệ` — wikilinks + nhãn
- `## Lịch sử tương tác` — timeline, newest on top
- `## Playbook` — nên / không nên / risk cần tránh

Các section tùy chọn: `## Tính cách & Motivation`, `## Điểm mạnh`, `## Điểm yếu / Blind spots`, `## Ghi chú khác`.

## Random revisit

Mỗi tuần / cuối tháng:

1. Mở 1-2 hồ sơ ngẫu nhiên trong `people/`.
2. Đọc lại `## Lịch sử tương tác` — có pattern nào mới không?
3. Update Playbook nếu cần.
4. Xem local graph — có ai mình chưa thêm vào bản đồ quan hệ?

## Liên quan

- [[people-mapping]] — bảng tra cứu codename ↔ tên thật (gitignored)
- [[people-template]] — template note
- [[personal/work]] — context chung về công ty và vai trò của mình
