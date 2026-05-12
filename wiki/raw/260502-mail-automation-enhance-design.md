# Mail Automation Enhancement — Design Spec

**Date**: 2026-05-02
**Status**: Approved
**Project**: mail-automation
**Related**: [260420-mail-automation.md](260420-mail-automation.md)

## Goal

Enhance mail-automation pipeline for efficiency, usability, and stability:
1. Implement Tier 2 reasoning (TL;DR, draft reply, candidate tasks) via Claude Code headless
2. Add Telegram bot as full control interface (notifications, interactive drafts, config management)
3. Make config management easier via Telegram commands, YAML remains source of truth

## Architecture

```
┌─────────────┐    launchd 1h    ┌──────────────┐
│  IMAP Server │◄───────────────│  Ingest (T1)  │
└─────────────┘                 └──────┬───────┘
                                       │ ghi mail → wiki/raw/mail/
                                       │ ghi event → events.jsonl
                                       ▼
                               ┌───────────────┐
                               │  Telegram Bot  │◄──── long-running (pm2)
                               │  (trung tâm)   │
                               └──┬────┬────┬──┘
                                  │    │    │
                    ┌─────────────┘    │    └─────────────┐
                    ▼                  ▼                  ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │  Notification │  │  Reasoning   │  │  Config Mgmt │
            │  (gửi summary │  │  (claude -p) │  │  (YAML R/W)  │
            │   lên TG)     │  │  TL;DR, draft│  │  /rules, etc │
            └──────────────┘  └──────┬───────┘  └──────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │  MCP imap     │
                              │  (draft reply)│
                              └──────────────┘
```

### Components

1. **Ingest (giữ nguyên)** — launchd 1h, thêm ghi event vào `events.jsonl`
2. **Telegram Bot** — long-running process (pm2), dispatcher trung tâm
3. **Reasoning** — bot spawn `claude -p` on-demand per-mail (không batch)

### Communication: Ingest → Bot

Ingest append **2 loại event** vào `events.jsonl` sau mỗi run:

1. **Per-mail event** (cho mỗi mail `action` mới):
```json
{"type":"new_action_mail","at":"...","account":1,"folder":"INBOX","uid":123,"message_id":"<...>","thread_file":"wiki/raw/mail/260416-slug.md","subject":"...","from":"...","category":"action","project":"bf1"}
```

2. **Run summary event** (cuối mỗi run):
```json
{"type":"ingest_complete","at":"...","account":1,"folder":"INBOX","new_threads":2,"appended":1,"queued":3}
```

`queue.jsonl` **không còn sử dụng** — `events.jsonl` thay thế hoàn toàn. Per-mail events chứa đủ thông tin để bot gửi notification và trigger reasoning.

Bot watch file bằng `fs.watch()` + track byte offset (persist vào `state/event-cursor.json`) → phát hiện event mới → xử lý. Khi bot restart, đọc từ saved offset → không miss events ghi trong lúc bot down.

## Telegram Bot Commands & Interactions

### Commands

| Command | Mô tả |
|---------|--------|
| `/status` | Pipeline status: last ingest, queue size, threads count |
| `/recent` | 5 mail gần nhất (đọc từ `events.jsonl` per-mail events, filter `new_action_mail`) |
| `/rules` | Liệt kê classification rules |
| `/rules categories` | Chỉ category rules |
| `/rules projects` | Chỉ project rules |
| `/add-rule <cat\|proj> <name> <field> <pattern>` | Thêm rule |
| `/del-rule <cat\|proj> <name>` | Xóa rule (with confirm) |
| `/accounts` | Liệt kê accounts |
| `/add-account` | Guided flow thêm account mới |
| `/ingest` | Trigger ingest thủ công |
| `/queue` | Xem queue chờ reasoning |
| `/reason` | Trigger reasoning thủ công |

### Interactive Flow — Mail Action Notification

```
Bot:  📬 New action mail
      From: Nguyen Van A <a@bf1.vn>
      Subject: Yêu cầu cập nhật FMS pricing
      Project: bf1 | Category: action

      [⚡ Reason now]  [⏭ Skip]

User: [⚡ Reason now]

Bot:  🤖 Đang reasoning...

Bot:  📝 TL;DR:
      A yêu cầu cập nhật bảng giá FMS cho Q3,
      deadline thứ 6 tuần này. Cần confirm với team pricing.

      ✏️ Draft reply:
      ───────────────
      Chào anh A,
      Em đã nhận yêu cầu. Em sẽ coordinate với team
      pricing và update trước thứ 6.
      ───────────────

      [✅ Approve]  [✏️ Edit]  [❌ Skip]

User: [✏️ Edit]

Bot:  Gửi nội dung reply mới:

User: "Chào anh A, em nhận rồi. Để em check lại
       với chị B rồi reply anh trước thứ 5 nhé."

Bot:  ✏️ Draft updated:
      ───────────────
      Chào anh A, em nhận rồi. Để em check lại
      với chị B rồi reply anh trước thứ 5 nhé.
      ───────────────

      [✅ Approve]  [✏️ Edit again]  [❌ Skip]

User: [✅ Approve]

Bot:  ✅ Draft created in mailbox. Review in mail app.
```

### Interactive Flow — Config Rule

```
User: /add-rule category noise sender_domain spam-corp.com

Bot:  ✅ Added rule to categories/noise:
      sender_domain: [spam-corp.com]
      Rules file updated: config/rules.yaml
```

### Interactive Flow — Add Account

```
User: /add-account
Bot:  📧 Thêm account mới. Trả lời từng câu:
      1/6 — Codename:
User: work-datatp
Bot:  2/6 — IMAP host:
User: mail.datatp.cloud
Bot:  3/6 — Port (mặc định 993):
User: 993
Bot:  4/6 — Username (email):
User: dan@datatp.cloud
Bot:  5/6 — Password:
User: ******
Bot:  6/6 — Folders (phân cách dấu phẩy, mặc định INBOX):
User: INBOX, Sent
Bot:  ✅ Account #2 "work-datatp" added.
      [🔄 Test connection]  [👌 Done]
```

**Cách ghi vào file**: Bot tính next ID = max(existing IDs) + 1. Ví dụ account #2:
- `.env` append:
  ```
  ACCOUNT_2_HOST=mail.datatp.cloud
  ACCOUNT_2_PORT=993
  ACCOUNT_2_USER=dan@datatp.cloud
  ACCOUNT_2_PASSWORD=******
  ACCOUNT_2_TLS=true
  ```
- `config/accounts.yaml` append entry mới với `host_env: ACCOUNT_2_HOST`, `user_env: ACCOUNT_2_USER`, etc. — giữ đúng pattern env var reference hiện tại.

Password ghi vào `.env` (chmod 600). Bot xóa message chứa password khỏi Telegram ngay sau khi nhận.

### Conversation State

In-memory, single user:
- `idle` — chờ command
- `awaiting_edit` — chờ nội dung draft mới
- `awaiting_confirm` — chờ approve/skip
- `awaiting_account_step` — đang trong guided add-account flow
- `reasoning` — đang chờ `claude -p` trả kết quả

**Transitions**:
- Bất kỳ state nào + nhận `/cancel` → reset về `idle`
- Bất kỳ state nào + nhận command khác (trừ `/cancel`) → bot reply "Đang có flow chưa xong. Gửi /cancel để hủy."
- `reasoning` + timeout/error → gửi error notification → reset về `idle`
- Restart bot → state reset về `idle` (không mất data, chỉ mất flow đang dở)

## Reasoning Pipeline (Tier 2)

### Trigger

1. **Auto**: Sau ingest có mail `action` mới (detect từ `events.jsonl`)
2. **Manual**: `/reason` hoặc [⚡ Reason now]

### Execution

```bash
claude -p "$(cat prompts/reasoning-single.md)" \
  --allowedTools mcp__imap__create_reply_draft \
  < thread-context.json
```

Reasoning chạy **per-mail** (không batch). Lý do:
- Interactive trên Telegram — user cần approve/edit từng mail
- Fail 1 mail không block mail khác
- Không cần chờ daily batch

### Prompt Structure

Refactor `prompts/reasoning.md` hiện tại (batch-oriented) thành 3 file:

| File | Mô tả |
|------|--------|
| `prompts/reasoning-system.md` | System context: people mapping path, wiki structure, redaction rules, safety rules. Trích từ phần "Safety rules" + "Input" + "Bước 1" của `reasoning.md` hiện tại |
| `prompts/reasoning-single.md` | Per-thread: TL;DR, wikilinks, draft reply decision, candidate task extraction. Trích từ "Bước 2" (2a-2e) của `reasoning.md`, thêm output format delimiters |
| `prompts/draft-reply.md` | Prompt cho lần spawn thứ 2: nhận approved body text + uid + account, gọi MCP imap tạo draft |

`prompts/reasoning.md` giữ lại làm reference, không xóa.

Bot compose prompt = concatenate(reasoning-system.md, reasoning-single.md, thread context JSON) → pipe vào `claude -p --print` (flag `--print` = non-interactive, output to stdout).

### Input

```json
{
  "thread_file": "wiki/raw/mail/260416-crm-agent-assignment.md",
  "thread_content": "...(full markdown)...",
  "message_id": "<...>",
  "account": 1,
  "uid": 123,
  "category": "action",
  "project": "bf1",
  "people_mapping": "...(nội dung people-mapping.md)..."
}
```

### Output Convention

```
---TLDR---
<nội dung TL;DR>
---DRAFT---
<nội dung draft reply hoặc SKIP: <lý do>>
---TASKS---
<candidate tasks hoặc NONE>
---END---
```

Bot parse sections → gửi lên Telegram → chờ interaction.

### After User Approve

1. Bot spawn `claude -p` với prompt chuyên tạo draft reply qua MCP imap tool. Lý do cần `claude -p` thay vì gọi MCP trực tiếp: MCP imap server chạy dưới Claude Code context, bot TypeScript không access được MCP tools trực tiếp. `claude -p` prompt nhận body text (đã approve/edit) + uid + account → gọi `mcp__imap__create_reply_draft`.
2. Update thread file: thêm `## Draft reply` section, update frontmatter status
3. Append candidate tasks vào `wiki/raw/<YYMMDD>-daily-tasks.md` (nếu có)

### Error Handling

- `claude -p` timeout: 180s (configurable via `REASONING_TIMEOUT_MS` env var), retry 1 lần
- Parse fail: gửi raw output lên Telegram, user quyết định
- MCP imap fail: thông báo lỗi, thread file update status `reasoned`

### Working Directory

Bot PHẢI spawn `claude -p` từ project directory (`/Users/nqcdan/dev/mail-automation`) để Claude Code có thể access MCP servers configured trong `.mcp.json`.

## Config Management

### Source of Truth

- `config/rules.yaml` — classification rules (bot đọc/ghi)
- `config/accounts.yaml` — account metadata (bot đọc/ghi)
- `.env` — credentials (bot ghi khi add-account, không expose qua commands)

### Rules Operations

- **Add**: Parse command → validate field → tìm rule matching name → append condition hoặc tạo rule mới (trước fallback)
- **Delete**: Confirm trước khi xóa
- **Validate**: Parse lại YAML sau ghi → rollback nếu corrupt

### Account Operations

- Guided flow qua Telegram (6 bước)
- Ghi `config/accounts.yaml` + `.env`
- Delete password message ngay sau khi nhận

## File Structure

```
src/
├── ingest.ts              # (giữ nguyên) + thêm ghi events.jsonl
├── bot/
│   ├── index.ts           # Entry point, khởi tạo bot + event watcher
│   ├── commands.ts        # Command handlers
│   ├── interactions.ts    # Inline keyboard callbacks
│   ├── reasoning.ts       # Spawn claude -p, parse output
│   ├── config-manager.ts  # Đọc/ghi YAML, validate
│   └── state.ts           # Conversation state machine
├── imap-client.ts         # (giữ nguyên)
├── classifier.ts          # (giữ nguyên)
├── config.ts              # (giữ nguyên)
├── state.ts               # (giữ nguyên)
├── thread-resolver.ts     # (giữ nguyên)
├── markdown-writer.ts     # (giữ nguyên)
└── slugify.ts             # (giữ nguyên)
```

## Dependencies

| Package | Mục đích |
|---------|----------|
| `grammy` | Telegram Bot API framework (TypeScript-native) |

Existing dependencies giữ nguyên.

## Events File

`events.jsonl` — thay thế `queue.jsonl`. Ingest append 2 loại event (xem section Communication ở trên).

Bot track read offset tại `state/event-cursor.json`:
```json
{"byte_offset": 4096, "last_read_at": "2026-05-02T14:00:00Z"}
```

## Process Management

- Bot chạy qua **pm2**: `pm2 start src/bot.ts --interpreter tsx --name mail-bot`
- `pm2 save` + `pm2 startup` → auto-start khi Mac Mini reboot
- Graceful shutdown: bắt `SIGTERM`/`SIGINT` → stop polling, finish pending, exit

## Auth

Single user. Bot check `chat.id === TELEGRAM_OWNER_ID`. Ignore mọi message từ chat khác.

## Env Vars Mới

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_OWNER_ID=...
```

## Changes to Existing Code

Minimal:
- `src/ingest.ts`: Thay append `queue.jsonl` bằng append `events.jsonl` (per-mail `new_action_mail` events + run summary `ingest_complete` event). Xóa logic ghi `queue.jsonl`.
- Không thay đổi logic ingest/classify/thread hiện tại
