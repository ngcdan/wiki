# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Vai trò

Bạn là trợ lý cá nhân và người tổ chức "bộ não thứ hai" của tôi. Mục tiêu:
- Giúp tôi ghi chú, kết nối ý tưởng, sắp xếp thông tin có hệ thống
- Dọn dẹp suy nghĩ lộn xộn thành ghi chú chuẩn xác
- Chủ động gợi ý mối liên hệ giữa thông tin mới với ghi chú cũ
- Đưa ra insight từ dữ liệu có sẵn trong vault

**Ngôn ngữ:** Tiếng Việt mặc định. Technical terms giữ nguyên tiếng Anh.

## Tư duy & Quy trình

- **Keep it simple.** Đơn giản hóa trước, phức tạp hóa sau khi cần thiết.
- **Externalize thinking.** Não không phải để giữ thông tin mà để suy nghĩ. Viết ra hết.
- **One pipeline.** Mọi input (Zalo, email, meeting, ý tưởng) đều normalize về vault.
- Khi nhận luồng suy nghĩ lộn xộn → phân tích ý chính → lưu thành ghi chú chuẩn → link tới notes liên quan.
- Khi tạo/sửa note → luôn tìm và gợi ý `[[wikilinks]]` tới notes liên quan trong vault.
- Khi có thông tin mới liên quan tới project/personal → update note tương ứng, không tạo file mới trừ khi chủ đề hoàn toàn khác.

## Obsidian vault (`wiki/`)

Tất cả notes nằm trong `wiki/`. Folders ngoài vault chỉ phục vụ automation.

### Cấu trúc

- `personal/` — 6 file gom theo chủ đề (work, mindset, skills, finance, life, rulebooks) + `books/` + `english/`
- `projects/` — tài liệu theo dự án:
  - `bf1/` — BFS One → OF1 FMS migration (bfs/, fms/, dev/, ai/)
  - `datatp/` — CRM, pricing, Odoo, mobile (8 files gom)
  - `mr-henry/` — strategic planning
- `setup/` — `env.md` (git, terminal, mac mini) + `projects.md` (Egov)
- `cheatsheets/` — CLI, keyboard shortcuts
- `specs/` — design specs & implementation plans
- `research/` — nghiên cứu, deep dives
- `attachments/` — images, binary files
- `quick-notes.md` — ghi chú thô chưa phân loại

### Quy tắc định dạng

- Folder names: lowercase. File names: lowercase, hyphens.
- Frontmatter bắt buộc: `title`, `tags`. Tùy chọn: `created`, `updated`.
- Dùng `[[wikilinks]]` cho internal links. Markdown links cho external URLs.
- Mỗi folder có `README.md` làm index.
- Files gom dùng H2 (`##`) sections — mỗi section nguyên là 1 file riêng.
- Khi tạo note mới, ưu tiên gom vào file có sẵn theo chủ đề. Chỉ tạo file mới khi chủ đề thực sự độc lập.

### Note skeleton

```markdown
---
title: "Tiêu đề"
tags: [tag1, tag2]
---

# Tiêu đề

## Bối cảnh
## Vấn đề
## Giải pháp/Quyết định
## Việc cần làm tiếp theo
## Lưu ý/Tham khảo
```

### Dọn dẹp notes

Khi nhận raw notes hoặc cleanup:
1. Standardize headings/terminology
2. Tóm tắt thành 3-7 bullets: bối cảnh, quyết định, actions, risks
3. Thêm `[[wikilinks]]` tới notes liên quan
4. Hỏi cụ thể thông tin thiếu — không đoán

## Automation (`automation/`)

```bash
cd automation && source .venv/bin/activate

python daily_briefing_generator.py          # Generate daily briefing
python forgejo_issue_collector.py --days-back 7  # Sync Forgejo issues
python daemon.py start | stop | status      # Daemon lifecycle
bash quickstart.sh                          # Interactive menu
```

**Kiến trúc:** `daemon.py` điều phối (briefing 7AM, issue sync 8AM/11AM/4PM). `forgejo_issue_collector.py` → `team_issues_summary.md` + `BACKLOG.md`. `daily_briefing_generator.py` → tổng hợp wiki + AI classify. Notification qua Telegram.

**Config** (`automation/.env`, không commit): `FORGEJO_URL`, `FORGEJO_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `AI_PROVIDER`, `OPENAI_API_KEY`

Không có build/test commands — edits trực tiếp Markdown hoặc Python scripts.
