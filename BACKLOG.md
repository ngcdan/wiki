---
title: "BACKLOG (Personal)"
type: backlog
tags: [work, automation, setup, planning, documentation]
created: 2026-02-07
updated: 2026-02-19
---
# BACKLOG (Personal)

## Daily template

```md
### 🧠 Current Focus (Week / Month)

### 📊 Yesterday
- [Win] 
- [Not Done] 
- [Stuck] 

### 🔥 Top 3 Today (Must Win)
1.
2.
3.

### 🧱 One Hard Thing (Do early)

### 🧩 My Tasks — Work

### 🧩 My Tasks — Personal

### ⚡ Quick Decisions
- None
```

## Daily — 2026-02-19

### 🧠 Current Focus (Week / Month)

### 📊 Yesterday
- [Win] 
- [Not Done] 
- [Stuck] 

### 🔥 Top 3 Today (Must Win)
1. Build & submit lại bản build CRM (ưu tiên)
2. Chuẩn bị kế hoạch bảo mật data (S3, OCR) → gửi anh Henry
3. Chuẩn hoá workflow: batch inbox 2 lần/ngày → issue/backlog → ưu tiên → giao dev → report

### 🧱 One Hard Thing (Do early)
- Build & submit lại bản build CRM (fix errors + bump version)

### 🧩 My Tasks — Work
- [ ] Optimize Wiki/Docs: setup Forgejo Actions CI/CD to auto-sync issues
- [ ] Review Mobile (issue/điểm nghẽn/next actions)
- [ ] Build & submit lại bản build CRM
- [ ] Plan bảo mật data S3/OCR → gửi anh Henry
- [ ] Kế hoạch tuyển dụng: trao đổi anh Tuấn → tổng hợp → gửi anh Henry
- [ ] Siết quản lý DB schema (changelog + upgrade guide + 2-step rollout)
- [ ] Plan onboard anh Hiếu (task + PR convention + update 3 dòng)
- [ ] Investigate declaration data flow: confirm logic for pushing to the correct source DB based on Partner Company.

### 🧩 My Tasks — Personal
- [ ] Tập thể dục (sáng)
- [ ] 07:30 routine: Anki + typing
- [ ] Học từ mới tiếng Anh (Anki) ~30p
- [ ] Luyện gõ phím ~30p
- [ ] Setup camera (OpenClaw / node)
- [ ] Chuẩn hoá workflow batch inbox (11h/16h)

### ⚡ Quick Decisions
- None


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

---

## Planning, Ideas

- (OpenClaw) Cân nhắc setup **multiple agents** (triage/coding/ops) trong **1 Gateway** để tách vai trò + tool policy + chạy song song bằng sub-agent sessions; đồng thời tách session theo channel (Telegram vs Web UI) đã làm xong, còn phần agents sẽ review/triển khai sau nếu cần.

- (Idea) **AI “Inbox OS”**: thu thập *mọi* luồng vào (Gmail, chat/message, Zalo, notifications) → **triage + lọc nhiễu cực mạnh** → tổng hợp cho anh theo dạng digest
  - Inputs/connectors: Gmail API, chat APIs (Telegram/Signal/Zalo bridge), webhooks
  - Pipeline: normalize → classify (work/personal/urgent/spam) → dedupe/thread → extract tasks/people/dates → summarize
  - Noise filter: allowlist người/keyword + threshold “importance”, auto-archive phần rác; chỉ ping khi có trigger (deadline gần, mention anh, khách/leader)
  - Output: daily digest 1 trang + “action list” (Top 3), kèm link nguồn; có chế độ *deep dive* khi anh hỏi lại
  - Memory: map người/đơn vị/dự án; học theo feedback (anh mark “quan trọng/không quan trọng”) để tune dần
  - Safety: local-first nếu được; encrypt at rest; log/audit “vì sao hệ thống đánh dấu quan trọng”

---
## BACKLOG - Issues

#### #467 Báo cáo Sales Performance (Freehand/Key Account)
- **Repo:** of1-crm
- **Link:** https://git.datatp.cloud/of1-crm/of1-crm/issues/467
- **Labels:** Feature
- **Assignee:** @vutuongan2003, @duynien
- **Status:** closed
- **Updated at:** 2026-04-01

#### #466 Chuẩn bị API BF1 đấu nối vào S3
- **Repo:** of1-crm
- **Link:** https://git.datatp.cloud/of1-crm/of1-crm/issues/466
- **Assignee:** @ntduc2810
- **Status:** closed
- **Updated at:** 2026-04-01

#### #484 CRM: tổ chức lại phân quyền App CRM, phân quyền theo screens thay vì nghiệp vụ như hiện tại
- **Repo:** of1-crm
- **Link:** https://git.datatp.cloud/of1-crm/of1-crm/issues/484
- **Labels:** Enhancement
- **Assignee:** @qngnhat, @duynien
- **Status:** closed
- **Updated at:** 2026-03-31

#### #490 CRM: Agent List (No Trans) bổ sung thêm các field mới từ API BF1
- **Repo:** of1-crm
- **Link:** https://git.datatp.cloud/of1-crm/of1-crm/issues/490
- **Labels:** Enhancement
- **Assignee:** @duynien
- **Status:** closed
- **Updated at:** 2026-03-31

