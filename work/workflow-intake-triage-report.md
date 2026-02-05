# Workflow: Intake → Triage → Issues/Backlog → Report (Anh Đàn)

Updated: 2026-02-06

## Objective
Giảm context switching bằng cách **batch xử lý inbox** và ép mọi request về 1 pipeline thống nhất.

## Rule
- Block user chats (chỉ mở chat dev để support).
- Chỉ mở lại user chat theo 2 khung giờ:
  - **Gần 11:00**
  - **Gần 16:00**

## Steps (2 lần/ngày)
### A) Intake (gom request)
- Lướt Zalo/Outlook 1 lượt.
- Với mỗi request: ghi nhanh 3 ý:
  - What (yêu cầu/lỗi gì)
  - Impact (ai bị ảnh hưởng/mức độ)
  - Evidence (ảnh/log/link)

### B) Triage (xếp ưu tiên)
- Gán priority:
  - **P0**: ảnh hưởng vận hành/tiền/khách hàng ngay
  - **P1**: ảnh hưởng nhiều người dùng nhưng có workaround
  - **P2**: cải tiến/đẹp/tiện
- Quyết định: làm ngay / lên lịch / cần hỏi thêm.

### C) Normalize (đưa về 1 chỗ)
- Tạo Issue (hoặc backlog item) với template:
  - Context
  - Expected / Acceptance criteria
  - Priority + Deadline
  - Owner + Reviewer
  - Links

### D) Delegation
- Giao task nhỏ, độc lập; tránh task “mơ hồ”.
- Với task mơ hồ: tạo sub-task “clarify requirement” trước.

### E) Update tracking
- Update file backlog trong `work/` (1 nguồn sự thật):
  - Top 3 priorities
  - In progress
  - Blocked

### F) Report to Anh Tuấn
- Sau mỗi batch, cập nhật report ngắn (copy/paste).

## Notes
- Ngoài 2 khung giờ trên: hạn chế mở user inbox để không bị kéo nhịp làm việc.
