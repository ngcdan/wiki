# BACKLOG (Personal)

## Current focus

- [ ] (Daily) Sáng dậy tập thể dục nhiều để giảm cân, cân đối
- [ ] (Daily) 07:30 routine: Anki + typing (giảm ma sát tối đa, có confirm + delay)
- [ ] (30p) Học từ mới tiếng Anh (Anki) — mỗi ngày
- [ ] (30p) Luyện gõ phím — mỗi ngày
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)
- [ ] Chuẩn hoá luồng làm việc: batch inbox user **2 lần/ngày** (gần 11h, gần 16h) → gom về 1 chỗ → tạo issue/backlog → gán ưu tiên → giao dev → report (anh sẽ duy trì hằng ngày)
- [ ] (Team) Quản lý thay đổi **DB schema** chặt hơn: bắt buộc changelog schema/entity (create/rename/delete + why), có upgrade guide khi chạy migration/run:update, nâng cấp theo **2 bước** (backward-compatible trước, drop sau). Release cuối tuần: anh Tuấn làm.
- [ ] Pending: plan onboard anh Hiếu (freelancer ~15h/tuần) theo hướng task rõ ràng + PR convention + update tiến độ 3 dòng

### Tasks (Hiếu)

#### 1. UT/IT Templates: eCustoms + ecus-thaison

**Goal:** tạo template UT/IT (main points + skeleton), implement chi tiết sau.

**Main points (IT):**
- [ ] Test the schema file with postgres in testcontainer
- [ ] Test the flow of kafka for each main flow (by creating template, implement detail later) with kafka in testcontainer
  - [ ] Make sure the kafka with all current configurations work correctly: Can publish, Can consume
- [ ] Test the mapping but end to end, read from ecus db, mapping (test method, save to egov db), get and assert

**Checklist (Integration Test):**
- [ ] integration test with spring boot test: in ecustoms and ecus-thaison
- [ ] IT in ecustoms with testcontainer, be able to test the liquibase (load from main schema)
- [ ] IT in ecus-thaison: create TEMPLATE for each entity (domain) to map from expected ecus entity to expected egov entities. Need to save to DB and assert after getting.
- [ ] IT in ecus-thaison: kafka with testcontainer, create template for publishing message → kafka → consume message → expected value: how? by which design?

#### 2. Đọc concept về **Liquibase**, tự tìm hiểu cách dùng Liquibase trong code

#### 3. Discuss với a Hiếu: flow run eGov + branching/libs + DB info
- [ ] Flow run server eGov:
  - Start server platform / UI phoenix
  - Start server eGov / UI
  - Bật lại nginx vào cổng `localhost:8080`
- [ ] Branching + libs sync:
  - Code eGov của các dự án công ty (trừ eGov) luôn update theo nhánh `dev`?
    - Nếu đúng: nhánh `egov` em có được merge/update từ `dev` về không?
  - Flow làm việc: checkout `egov-local-server` -> làm -> tạo PR -> submit merge vào `egov`
  - Lib Java + UI của platform publish lên Nexus có update đồng bộ với release của `dev` không?
- [ ] DB endpoints/info:
  - `of1@egov-dev`: `postgres.of1-dev-egov.svc.cluster.local:5432/egov`
  - `of1@egov-prod`: `egov-server.of1-prod-platform.svc.cluster.local:5432/egov`
  - `of1@platform-egov`: DB beta
  - `of1@ecus-prod`: `win-server-16-ecus-hp.beehp-prod-logs.svc.cluster.local:1433;database=ECUS5VNACCS`
  - `of1@ecus-snapshot`: `win-server-16-ecus-hp.of1-dev-egov.svc.cluster.local:1433;database=ECUS5VNACCS`
  - `of1@ecus-dev`: ???
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

