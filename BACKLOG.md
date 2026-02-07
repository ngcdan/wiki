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
#### #301 Refs #286 #290 Clean code
> Clean code Partner + Inquiry Request

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/301
- **Author:** @qngnhat

#### #300 Issues #298 - Add requirements for pricing branch
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/300
- **Author:** @ntduc2810

#### #299 Issues #298 - Add required for pricing branch
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/299
- **Author:** @ntduc2810

#### #295 Update sync legacy system, convert partner logic
> Cập nhật logic syncLegacySystem để sử dụng continent.

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/295
- **Author:** @ntduc2810

#### #285 Resolves #290 + #286 Update Partner continent, Inquiry Request Air Volume
> Cập nhật logic syncLegacySystem để sử dụng continent.

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/285
- **Author:** @qngnhat

#### #284 [Enhancement] Add Pricing Company Branch into Subject Inquiry Request mail
> Thêm target pricing company branch vào subject khi gửi mail để Pricing có thể reject khi sale request nhầm company

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/284
- **Author:** @qngnhat

#### #283 [Enhancement] Clean code CRM
> Add 'pricing branch' field to inquiry request list. Fix popup showing twice issue.

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/283
- **Author:** @qngnhat

#### #282 refactor-code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/282
- **Author:** @vutuongan2003

#### #281 [BUG] Could not send approve/reject mail for partner request when request has multi approver
> ![image](/attachments/b5ca9409-021e-4cc9-93a1-26f193e6f9a0)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/281
- **Author:** @qngnhat

#### #280 [ENHANCEMENT, BUG] Add 'pricing branch' field to inquiry request list. Fix popup showing twice issue.
> ** Changes:

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/280
- **Author:** @ntduc2810

#### #279 Fixes #286 - here is title's pull request
> here is description pull requests

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/279
- **Author:** @jesse.vnhph

#### #278 refactor-code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/278
- **Author:** @vutuongan2003

#### #277 refactor code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/277
- **Author:** @ntduc2810

#### #276 refactor crm-user-roles
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/276
- **Author:** @ntduc2810

#### #275 tms
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/275
- **Author:** @jesse.vnhph

#### #274 check diff
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/274
- **Author:** @jesse.vnhph

#### #273 refactor-code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/273
- **Author:** @vutuongan2003

#### #272 clean code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/272
- **Author:** @qngnhat

#### #271 refactor-code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/271
- **Author:** @vutuongan2003

#### #270 clean code
> (no description)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/270
- **Author:** @qngnhat
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
- [ ] Sau khi update/sync xong có message ngắn gọn gửi group dev.

## Workflow: AI “clean up” text/note
Mục tiêu: dán note thô → ra bản rõ ràng + action items.

