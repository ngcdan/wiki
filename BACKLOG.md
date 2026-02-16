---
title: "BACKLOG (Personal)"
type: backlog
tags: [work, automation, setup, planning, documentation]
created: 2026-02-07
updated: 2026-02-16
---
# BACKLOG (Personal)

## Current focus

- [ ] (Daily) Sáng dậy tập thể dục nhiều để giảm cân, cân đối
- [ ] (Daily) 07:30 routine: Anki + typing (giảm ma sát tối đa, có confirm + delay)
- [ ] (30p) Học từ mới tiếng Anh (Anki) — mỗi ngày
- [ ] (30p) Luyện gõ phím — mỗi ngày
- [ ] Review phần Mobile (note lại: issue / điểm nghẽn / next actions)
- [ ] Build & submit lại **bản build CRM** (ưu tiên) — fix errors, bump versionCode/CFBundleVersion nếu cần
- [ ] Chuẩn bị kế hoạch **bảo mật data** cho dự án **S3, OCR** → gửi anh Henry
- [ ] Trình bày nhu cầu tuyển dụng nhân sự với anh Tuấn; tổng hợp và gửi kế hoạch cho anh Henry
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
  - `of1@ecus-dev`: `win-server-16-ecus-hp.of1-dev-egov.svc.cluster.local:1433;database=ECUS5VNACCS`
---

## Planning, Ideas

- [ ] (OpenClaw) Cân nhắc setup **multiple agents** (triage/coding/ops) trong **1 Gateway** để tách vai trò + tool policy + chạy song song bằng sub-agent sessions; đồng thời tách session theo channel (Telegram vs Web UI) đã làm xong, còn phần agents sẽ review/triển khai sau nếu cần.

- [ ] (Idea) **AI “Inbox OS”**: thu thập *mọi* luồng vào (Gmail, chat/message, Zalo, notifications) → **triage + lọc nhiễu cực mạnh** → tổng hợp cho anh theo dạng digest
  - Inputs/connectors: Gmail API, chat APIs (Telegram/Signal/Zalo bridge), webhooks
  - Pipeline: normalize → classify (work/personal/urgent/spam) → dedupe/thread → extract tasks/people/dates → summarize
  - Noise filter: allowlist người/keyword + threshold “importance”, auto-archive phần rác; chỉ ping khi có trigger (deadline gần, mention anh, khách/leader)
  - Output: daily digest 1 trang + “action list” (Top 3), kèm link nguồn; có chế độ *deep dive* khi anh hỏi lại
  - Memory: map người/đơn vị/dự án; học theo feedback (anh mark “quan trọng/không quan trọng”) để tune dần
  - Safety: local-first nếu được; encrypt at rest; log/audit “vì sao hệ thống đánh dấu quan trọng”

---
