# BACKLOG (Personal)

## Current focus

- [ ] (Daily) 07:30 routine: Anki + typing (giảm ma sát tối đa, có confirm + delay)
- [ ] (Daily) Sáng dậy tập thể dục nhiều để giảm cân, cân đối
- [ ] (Daily) Pha cà phê bằng **phin to** (xem công thức nếu cần)
- [ ] (30p) Học từ mới tiếng Anh (Anki) — mỗi ngày
- [ ] (30p) Luyện gõ phím — mỗi ngày
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)
- [ ] Chuẩn hoá luồng làm việc: batch inbox user **2 lần/ngày** (gần 11h, gần 16h) → gom về 1 chỗ → tạo issue/backlog → gán ưu tiên → giao dev → report (anh sẽ duy trì hằng ngày)
- [ ] (Team) Quản lý thay đổi **DB schema** chặt hơn: bắt buộc changelog schema/entity (create/rename/delete + why), có upgrade guide khi chạy migration/run:update, nâng cấp theo **2 bước** (backward-compatible trước, drop sau). Release cuối tuần: anh Tuấn làm.
- [ ] Pending: plan onboard anh Hiếu (freelancer ~15h/tuần) theo hướng task rõ ràng + PR convention + update tiến độ 3 dòng

---

## Planning, Ideas

- [ ] (OpenClaw) Cân nhắc setup **multiple agents** (triage/coding/ops) trong **1 Gateway** để tách vai trò + tool policy + chạy song song bằng sub-agent sessions; đồng thời tách session theo channel (Telegram vs Web UI) đã làm xong, còn phần agents sẽ review/triển khai sau nếu cần.

---
## BACKLOG - Team
#### #301 Refs #286 #290 Clean code
> Clean code Partner + Inquiry Request

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/301
- **Labels:** Enhancement
- **Assignee:** @qngnhat
- **Status:** merged
- **Merged at:** 2026-02-06

#### #288 [CRM-0001] Refactor code
> Refactor code, clean code

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/288
- **Labels:** Enhancement
- **Assignee:** @jesse.vnhph (Lê Ngọc Đàn)
- **Status:** open

#### #285 Resolves #290 + #286 Update Partner continent, Inquiry Request Air Volume
> Cập nhật logic syncLegacySystem để sử dụng continent.

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/285
- **Labels:** Enhancement
- **Assignee:** @ntduc2810, @qngnhat
- **Status:** merged
- **Merged at:** 2026-02-06

#### #284 [Enhancement] Add Pricing Company Branch into Subject Inquiry Request mail
> Thêm target pricing company branch vào subject khi gửi mail để Pricing có thể reject khi sale request nhầm company

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/284
- **Assignee:** (unassigned)
- **Status:** merged
- **Merged at:** 2026-02-05

#### #283 [Enhancement] Clean code CRM
> Add 'pricing branch' field to inquiry request list. Fix popup showing twice issue.

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/283
- **Labels:** Enhancement
- **Assignee:** (unassigned)
- **Status:** merged
- **Merged at:** 2026-02-04

#### #281 [BUG] Could not send approve/reject mail for partner request when request has multi approver
> ![image](/attachments/b5ca9409-021e-4cc9-93a1-26f193e6f9a0)

- **Link:** http://forgejo.of1-apps.svc.cluster.local/of1-crm/of1-crm/pulls/281
- **Labels:** Bug
- **Assignee:** (unassigned)
- **Status:** merged
- **Merged at:** 2026-02-03
## Automation (trigger thủ công)

