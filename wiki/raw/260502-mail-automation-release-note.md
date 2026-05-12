---
title: "Mail Automation Enhancement — Release Note"
tags: [mail-automation, telegram-bot, release]
created: 2026-05-02
status: deployed
related:
  - "[[260420-mail-automation]]"
  - "[[260502-mail-automation-enhance-design]]"
  - "[[260502-mail-automation-enhance-plan]]"
---

## Summary

Nâng cấp mail-automation pipeline: thêm Telegram bot làm trung tâm điều khiển + Tier 2 reasoning qua Claude Code headless.

Branch: `feat/telegram-bot-tier2` (14 commits)
Repo: `~/dev/mail-automation`

## What Changed

### Tier 1 — Ingest (modified)
- `queue.jsonl` thay bằng `events.jsonl` (per-mail events + run summary events)
- Logic ingest giữ nguyên, chỉ thay output format

### Tier 2 — Reasoning (new)
- Spawn `claude -p` per-mail (không batch), tận dụng Max subscription
- TL;DR + draft reply + candidate tasks extraction
- Output parse qua delimiters: `---TLDR---`, `---DRAFT---`, `---TASKS---`, `---END---`
- Retry 1 lần khi timeout (180s configurable)

### Telegram Bot (new)
- Framework: grammy (TypeScript-native)
- Process: pm2 (`mail-bot`), auto-restart khi reboot
- Single user auth via `TELEGRAM_OWNER_ID`

## Commands

| Command | Mô tả |
|---------|--------|
| `/status` | Pipeline status: last ingest, queue size |
| `/recent` | 5 mail action gần nhất |
| `/rules` | Liệt kê classification rules |
| `/add_rule` | Thêm rule (category/project) |
| `/del_rule` | Xóa rule (có confirm) |
| `/accounts` | Liệt kê IMAP accounts |
| `/add_account` | Guided flow thêm account mới (6 bước) |
| `/ingest` | Trigger ingest thủ công |
| `/queue` | Xem mail chờ reasoning |
| `/reason` | Trigger reasoning thủ công |
| `/cancel` | Hủy flow đang dở |

## Interactive Draft Flow

```
Mail action mới → Bot gửi notification
→ [Reason now] → Claude reasoning → TL;DR + draft
→ [Edit] → User sửa trên Telegram
→ [Approve] → claude -p tạo draft trong mailbox
→ Review trong mail app → Send thủ công
```

## File Structure

```
src/
├── ingest.ts              # Modified: events.jsonl thay queue.jsonl
├── bot/
│   ├── index.ts           # Entry point, wire everything
│   ├── auth.ts            # Owner-only middleware
│   ├── state.ts           # Conversation state machine
│   ├── event-watcher.ts   # Watch events.jsonl, byte cursor
│   ├── commands.ts        # Command handlers
│   ├── interactions.ts    # Inline keyboard callbacks
│   ├── reasoning.ts       # Spawn claude -p, parse output
│   ├── config-manager.ts  # YAML read/write, validate
│   ├── account-flow.ts    # Guided add-account flow
│   ├── thread-updater.ts  # Update markdown frontmatter
│   └── formatting.ts      # Telegram message formatting
prompts/
├── reasoning.md           # Original (kept as reference)
├── reasoning-system.md    # System context
├── reasoning-single.md    # Per-thread reasoning
└── draft-reply.md         # Draft reply via MCP
```

## Env Vars

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_OWNER_ID=...
REASONING_TIMEOUT_MS=180000   # default 180s
```

## Operations

```bash
# Bot
pm2 status                    # Xem trạng thái
pm2 logs mail-bot             # Xem logs
pm2 restart mail-bot          # Restart
pm2 stop mail-bot             # Dừng

# Ingest (vẫn chạy qua launchd mỗi giờ)
npm run ingest                # Manual run
npm run ingest:dry            # Dry run
```

## Design Docs

- Spec: `[[260502-mail-automation-enhance-design]]`
- Plan: `[[260502-mail-automation-enhance-plan]]`
- Original spec: `[[260420-mail-automation]]`
