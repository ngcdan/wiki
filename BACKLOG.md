# BACKLOG (Personal)

## Current focus
- [ ] (30p) Học từ mới tiếng Anh (Anki)
- [ ] (30p) Luyện gõ phím
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)

## Automation (trigger thủ công)
### A) Daily pull + build (mỗi sáng)
**Mục tiêu:** mỗi sáng tự pull code từ remote về và build sẵn bằng lệnh (log rõ ràng).
- [ ] Anh Đàn note theo checklist: repo path + branch + build command + giờ chạy + cách báo OK/FAIL
- [ ] Tommy viết script CLI + log + summary (copy/paste) và setup job chạy theo giờ

### B) Ops: update prod + sync beta/dev
**Mục tiêu:** tự động hoá các tác vụ vận hành bằng lệnh, anh Đàn là người trigger thủ công.
- [ ] Anh Đàn mô tả flow update prod (SSH host, steps, restart/migrate, rollback)
- [ ] Anh Đàn mô tả flow sync beta/dev (source→target, tool: rsync/scp/docker/k8s, dữ liệu gì)
- [ ] Tommy đóng gói thành scripts có guardrails + log + summary

### C) Thông báo group dev (Zalo)
**Mục tiêu:** sau khi update/sync xong có message ngắn gọn gửi group dev.
- [ ] Tommy tạo template message (version/commit, việc đã làm, downtime, rủi ro, next)
- [ ] (Tuỳ chọn) nếu có bridge/API thì tích hợp gửi tự động; nếu không thì generate text để anh copy/paste

## Workflow: AI “clean up” text/note
Mục tiêu: dán note thô → ra bản rõ ràng + action items.

**Input template (copy/paste):**
```md
# Raw note
Context:
- 
Goal:
- 
Constraints:
- 
Raw bullets:
- 
```

**AI output yêu cầu:**
1) Tóm tắt 5-10 dòng (plain)
2) Chuẩn hóa note theo format:
   - Context / Problem / Decision / Next actions / Open questions
3) Extract TODOs (checkbox)
4) Đề xuất 3 câu hỏi cần làm rõ (nếu thiếu dữ liệu)

**Convention:**
- File ổn định: chuyển từ `notes/00_inbox/` → thư mục chủ đề (project/process/work)
- Title ngắn, có từ khóa; nếu theo ngày dùng prefix `YYYY-MM-DD_`
