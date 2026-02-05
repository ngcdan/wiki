# Onboarding: Anh Hiếu (Freelancer) — 15h/tuần

Updated: 2026-02-06

## Goal
Giúp anh Hiếu làm việc hiệu quả mà **không ăn thời gian của anh Đàn**, theo kiểu: task rõ ràng → PR rõ ràng → review nhanh → merge.

## Working model
- Time budget: ~**15h/tuần**
- Prefer tasks:
  - độc lập, ít phụ thuộc
  - có scope rõ, có thể hoàn thành trong 2–6 giờ / task
  - ưu tiên bugfix / refactor nhỏ / automation / docs

## Communication
- Kênh chính: chat nhóm dev (không đi qua user)
- Update tiến độ: cuối mỗi session làm việc gửi 3 dòng:
  1) Done
  2) Next
  3) Blockers / needs decision

## Definition of Ready (trước khi bắt đầu)
Mỗi task giao xuống nên có tối thiểu:
- Context (vì sao cần)
- Expected behavior / acceptance criteria
- Priority (P0/P1/P2)
- Deadline (nếu có)
- Links (issue/PR related, screenshots, logs)

## Definition of Done (trước khi gửi PR)
Checklist:
- [ ] Có link issue (Refs/Fixes/Closes #...)
- [ ] Có mô tả ngắn: what/why/how
- [ ] Có test steps (manual) hoặc tests (nếu có)
- [ ] Không phá flow hiện tại; nếu có breaking change thì ghi rõ
- [ ] Update docs/runbook nếu thay đổi cách vận hành

## PR conventions (tối thiểu)
- Title bắt đầu bằng một trong:
  - `Fixes #<id> ...`
  - `Closes #<id> ...`
  - `Refs #<id> ...`
- Description:
  - 1–2 câu tóm tắt
  - Test steps
  - Notes/risk

## How to pick tasks (ưu tiên để giảm phụ thuộc)
1) Bug nhỏ có log rõ
2) Improve tooling (scripts, automation)
3) Cleanup/refactor module nhỏ + add guardrails
4) Docs/runbook cập nhật theo thực tế

## First week plan (gợi ý)
- 1 task nhỏ để làm quen codebase + convention
- 1 task automation/docs để quen flow PR/review
- Chốt checklist “Definition of Done” cố định
