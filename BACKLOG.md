# BACKLOG (Personal)

## Current focus

- [ ] (Daily) 07:30 routine: Anki + typing (giảm ma sát tối đa, có confirm + delay)
- [ ] (30p) Học từ mới tiếng Anh (Anki) — mỗi ngày
- [ ] (30p) Luyện gõ phím — mỗi ngày
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)
- [ ] Chuẩn hoá luồng làm việc: batch inbox user **2 lần/ngày** (gần 11h, gần 16h) → gom về 1 chỗ → tạo issue/backlog → gán ưu tiên → giao dev → report (anh sẽ duy trì hằng ngày)
- [ ] Pending: plan onboard anh Hiếu (freelancer ~15h/tuần) theo hướng task rõ ràng + PR convention + update tiến độ 3 dòng

---
## BACKLOG - Team

<!-- AUTO:FORGEJO_PRS_START -->
#### #288 [CRM-0001] Refactor code
> Refactor code, clean code

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/288
- **Author:** @vutuongan2003
<!-- AUTO:FORGEJO_PRS_END -->


## Automation (trigger thủ công)

### Google APIs (OAuth) — Calendar + Drive/Docs/Sheets
- [ ] Mở rộng OAuth scopes từ Gmail-only sang Calendar + Drive/Docs/Sheets
  - Enable APIs: Calendar, Drive, Docs, Sheets
  - Add scopes + regenerate `token.json` (refresh token)
  - Viết CLI chung (send mail / create event / upload drive / create doc / edit sheet)
  - Rule: default “send luôn” theo lệnh rõ ràng; log + summary mỗi lần chạy

### B) Ops: update prod + sync beta/dev
**Mục tiêu:** tự động hoá các tác vụ vận hành bằng lệnh, anh Đàn là người trigger thủ công.
- [ ] Anh Đàn mô tả flow update prod (SSH host, steps, restart/migrate, rollback)
- [ ] Anh Đàn mô tả flow sync beta/dev (source→target, tool: rsync/scp/docker/k8s, dữ liệu gì)
- [ ] Tommy đóng gói thành scripts có guardrails + log + summary

### C) Thông báo group dev (Zalo)
**Mục tiêu:** sau khi update/sync xong có message ngắn gọn gửi group dev.

## Workflow: AI “clean up” text/note
Mục tiêu: dán note thô → ra bản rõ ràng + action items.

