---
title: "Personal Folder Reorganization — Design Spec"
date: 2026-04-05
tags: [spec, personal, reorganization]
status: draft
---

# Personal Folder Reorganization

## Goal

Gom 42 files rời rạc trong `wiki/personal/` thành 6 file lớn theo chủ đề, mỗi file tổ chức bằng H2 sections. Giữ nguyên `books/` và `english/` subfolders.

## Current State

- 21 loose `.md` files ở root `personal/`
- `books/` (10 files) — notes từ sách
- `english/` (7 files) — IELTS, grammar, vocab
- `rulebooks/` (3 files) — AI integration, goal-setting, living-framework
- 2 file raw notes lớn: `ideas.md` (760 dòng), `reflect-plan-minimize.md` (540 dòng)

## Target Structure

```
wiki/
├── quick-notes.md          # ideas.md + reflect-plan-minimize.md (raw notes)
└── personal/
    ├── work.md             # Công việc, career, quy trình
    ├── mindset.md          # Tư duy, quy tắc sống, thói quen
    ├── skills.md           # Kỹ năng, giao tiếp, học tập
    ├── finance.md          # Tài chính cá nhân
    ├── life.md             # Sức khoẻ, du lịch
    ├── rulebooks.md        # AI integration, goal-setting, living-framework
    ├── books/              # (giữ nguyên)
    └── english/            # (giữ nguyên)
```

## Merge Mapping

### work.md

| Section (H2) | Source | Lines |
|---------------|--------|-------|
| Chiến lược phát triển | `plan.md` | 44 |
| Career Narrative | `self-review.md` | 146 |
| Workflow hằng ngày | `workflow.md` | 188 |
| Skill Practice | `skill-practice.md` | 45 |
| Backlog | `BACKLOG.md` | 112 |
| Nhiệm vụ hàng ngày | `todays-3.md` | 17 |

### mindset.md

| Section (H2) | Source | Lines |
|---------------|--------|-------|
| Quy tắc sống | `rules.md` | 109 |
| Thói quen | `habits.md` | 41 |
| Kỷ luật | `su-ky-luat.md` | 45 |
| Tự tin | `su-tu-tin.md` | 17 |
| Tư duy & Ra quyết định | `thinking-decision.md` | 61 |

### skills.md

| Section (H2) | Source | Lines |
|---------------|--------|-------|
| Giao tiếp | `communicate.md` | 83 |
| Kỹ năng tổng hợp | `skills.md` | ~20 |
| Học nhanh hơn | `learn-skill-faster.md` | 18 |
| Tech Skills tương lai | `valuable-tech-skills-future.md` | 27 |
| Luyện gõ | `typing-practice.md` | ~10 |

### finance.md

Rename từ `personal-finance.md`, giữ nguyên content (234 dòng).

### life.md

| Section (H2) | Source | Lines |
|---------------|--------|-------|
| Sức khoẻ & Thể thao | `suc-khoe-the-thao.md` | 55 |
| Du lịch Thái Lan | `thailands.md` | 12 |
| Checklist Travel | `checklist-travel.md` | ~10 |

### rulebooks.md

| Section (H2) | Source | Lines |
|---------------|--------|-------|
| AI Integration | `rulebooks/ai-integration.md` | ~27 |
| Goal Setting | `rulebooks/goal-setting.md` | ~47 |
| Living Framework | `rulebooks/living-framework.md` | ~50 |

### wiki/quick-notes.md

Move `ideas.md` (760 dòng) + `reflect-plan-minimize.md` (540 dòng) ra `wiki/quick-notes.md`. Gom nguyên content, đánh dấu raw.

## Rules

- Mỗi file có frontmatter: `title`, `tags`, `updated`
- Mỗi section cũ thành H2 (`##`) trong file mới
- Giữ wikilinks hiện có, cập nhật broken links
- Xóa tất cả source files sau khi merge
- Xóa folder `rulebooks/` sau khi gom
- Không động `books/` và `english/`

## Out of Scope

- Không chỉnh sửa nội dung bên trong notes
- Không thay đổi `books/` hoặc `english/`
