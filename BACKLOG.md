# BACKLOG (Personal)

## Current focus
- [ ] (Daily) 07:30 routine: Anki + typing (giảm ma sát tối đa, có confirm + delay)
- [ ] (30p) Học từ mới tiếng Anh (Anki) — mỗi ngày
- [ ] (30p) Luyện gõ phím — mỗi ngày
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)
- [ ] Chuẩn hoá luồng làm việc: batch inbox user **2 lần/ngày** (gần 11h, gần 16h) → gom về 1 chỗ → tạo issue/backlog → gán ưu tiên → giao dev → report (anh sẽ duy trì hằng ngày)
- [ ] Pending: plan onboard anh Hiếu (freelancer ~15h/tuần) theo hướng task rõ ràng + PR convention + update tiến độ 3 dòng

## Context (để đọc lại nhanh)
- Quy trình làm việc: `work/workflow.md`

## Reporting / Review
- [ ] (Ý tưởng hay) Daily report chuẩn hoá: mỗi ngày tạo 1 file `work/daily/YYYY-MM-DD.md` + 1 đoạn message ngắn (copy/paste báo cáo anh Tuấn)

## Weekly learning (theo dõi change)
- [ ] Hàng tuần tổng hợp change của anh Tuấn / Đạt / anh Đàn:
  - top files changed
  - coding patterns (naming/structure)
  - điểm đáng học + điểm rủi ro
  - xuất ra markdown trong `work/weekly/`

## Zalo intake → clean-up → issue/backlog
- [ ] Nếu cần: anh Đàn copy text / cap màn hình request từ Zalo → Tommy OCR + clean-up → tạo issue/backlog item + gợi ý label/owner (để anh duyệt)

## Automation (trigger thủ công)

### Google APIs (OAuth) — Calendar + Drive/Docs/Sheets
- [ ] Mở rộng OAuth scopes từ Gmail-only sang Calendar + Drive/Docs/Sheets
  - Enable APIs: Calendar, Drive, Docs, Sheets
  - Add scopes + regenerate `token.json` (refresh token)
  - Viết CLI chung (send mail / create event / upload drive / create doc / edit sheet)
  - Rule: default “send luôn” theo lệnh rõ ràng; log + summary mỗi lần chạy

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
