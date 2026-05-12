---
title: "Mail Automation Pipeline — Design"
tags: [spec, mail, automation, mcp-imap, forgejo]
created: 2026-04-20
status: design-approved
---

# Mail Automation Pipeline

Hybrid 2-tier automation để pull mail từ MCP IMAP, classify, store markdown, và reasoning định kỳ (TL;DR, wikilinks, draft reply, candidate tasks).

## Goals

- Tự động pull mail mới mỗi giờ, chỉ mail chưa xử lý.
- Lưu mỗi thread thành 1 file markdown trong `wiki/raw/mail/` (gitignored, full content).
- Phân loại `noise / fyi / action` + tag project — rule-based, iterate được.
- Mail `action` được Claude reasoning 1 lần/ngày: thêm TL;DR, wikilinks, draft reply nếu "quick-replyable", và append candidate tasks vào file daily checked-in (redacted về codename).
- Không auto-create Forgejo issue — user manually prompt Claude khi duyệt candidate list.

## Non-goals

- Không auto-send mail. Chỉ tạo draft trong IMAP Drafts.
- Không modify flags trên IMAP (không mark as read).
- Không xử lý nhiều account ở Phase 1 (infra hỗ trợ sẵn, bật sau).
- Không call Forgejo API từ automation.

## Architecture

```
Tier 1 — Ingest (launchd mỗi 1h)
  ~/dev/mail-automation/src/ingest.ts (Node + imapflow + tsx)
  ├─ Per account trong accounts.yaml:
  │   ├─ Resolve state (UIDVALIDITY + last_uid)
  │   ├─ Fetch UID > last_uid
  │   ├─ Per mail: dedupe Message-ID, resolve thread, classify, write MD
  │   └─ Nếu action → push queue.jsonl
  └─ Persist state atomically

Tier 2 — Reasoning (launchd 08:00 daily)
  claude -p --model sonnet "$(cat prompts/reasoning.md)"
  cwd = ~/dev/wiki
  ├─ Load queue.jsonl
  ├─ Per entry: TL;DR, wikilinks, quick-reply decision, draft, candidate task
  ├─ MCP imap create_reply_draft nếu đủ điều kiện
  └─ Truncate queue.jsonl
```

## Storage layout

```
~/dev/mail-automation/
├── .env                          # chmod 600, gitignored
├── package.json
├── tsconfig.json
├── config/
│   ├── accounts.yaml             # metadata (checked-in)
│   └── rules.yaml                # classification rules (checked-in)
├── src/
│   ├── ingest.ts                 # Tier 1 entry
│   ├── imap-client.ts            # imapflow wrapper
│   ├── classifier.ts             # rules.yaml engine
│   ├── thread-resolver.ts        # In-Reply-To/References → root_id
│   ├── markdown-writer.ts        # write/append thread files
│   ├── state.ts                  # UIDVALIDITY + last_uid + dedupe
│   ├── slugify.ts                # subject → filename slug
│   └── lang-detect.ts            # Vietnamese diacritics heuristic
├── prompts/
│   └── reasoning.md              # Tier 2 prompt template
├── state/
│   ├── accounts.json
│   ├── thread-index.json         # root_id → thread_file_path
│   └── seen-message-ids.jsonl
├── queue.jsonl
├── logs/
│   ├── ingest.log
│   └── reasoning.log
├── scripts/
│   ├── install-launchd.sh
│   ├── uninstall-launchd.sh
│   ├── prune-seen.sh             # monthly, xóa entry > 90 ngày
│   └── requeue-ingested.sh       # re-add thread files status=ingested vào queue
└── README.md

~/Library/LaunchAgents/
├── com.nqcdan.mail-ingest.plist
└── com.nqcdan.mail-reasoning.plist

wiki/raw/mail/                    # GITIGNORED
├── 260420-<slug>.md              # 1 file per thread
└── ...

wiki/raw/260420-daily-tasks.md    # CHECKED-IN, redacted codename
```

## Data schemas

### `config/accounts.yaml`

```yaml
accounts:
  - id: 1
    codename: work-of1
    host_env: ACCOUNT_1_HOST
    port_env: ACCOUNT_1_PORT
    user_env: ACCOUNT_1_USER
    password_env: ACCOUNT_1_PASSWORD
    tls: true
    folders: [INBOX]
    first_run_lookback_days: 7
```

### `.env` (chmod 600, gitignored)

```
ACCOUNT_1_HOST=mail.datatp.cloud
ACCOUNT_1_PORT=993
ACCOUNT_1_USER=harry.vnhph@openfreightone.com
ACCOUNT_1_PASSWORD=...
```

### `config/rules.yaml`

```yaml
# Evaluated top-down per dimension, first match wins
categories:
  - name: noise
    match:
      - sender_regex: "(noreply|no-reply|notifications?|newsletter)@"
      - subject_regex: "(?i)(unsubscribe|marketing|promotion)"
      - header: "List-Unsubscribe"
  - name: fyi
    match:
      - sender_regex: "@(jira|forgejo|gitlab|github)\\."
      - subject_regex: "(?i)(ci|build) (passed|failed|succeeded)"
  - name: action   # default fallback

projects:
  - name: bf1
    match:
      - sender_domain: [bf1.vn, openfreightone.com]
      - subject_regex: "(?i)\\b(bf1|bfs|fms)\\b"
  - name: of1
    match:
      - subject_regex: "(?i)\\bof1\\b"
  - name: other   # default
```

### `state/accounts.json`

```json
{
  "1": {
    "INBOX": {
      "uidvalidity": 1707832451,
      "last_uid": 48291,
      "last_sync_at": "2026-04-20T14:00:00Z"
    }
  }
}
```

### `state/thread-index.json`

```json
{
  "<xyz@datatp.cloud>": "wiki/raw/mail/260420-invoice-march-2026.md"
}
```

### `state/seen-message-ids.jsonl` (append-only)

```
{"message_id":"<abc@datatp.cloud>","account":1,"uid":48291,"ingested_at":"2026-04-20T14:00:05Z"}
```

### Thread file `wiki/raw/mail/260420-<slug>.md`

```markdown
---
title: "Invoice March 2026"
tags: [mail, thread, fyi]
category: fyi
project: of1
account: 1
thread_root_message_id: "<xyz@datatp.cloud>"
message_ids:
  - "<xyz@datatp.cloud>"
  - "<reply1@datatp.cloud>"
participants:
  - "harry.vnhph@openfreightone.com"
  - "billing@vendor.com"
first_seen: 2026-04-20T14:00:05Z
last_updated: 2026-04-20T14:00:05Z
status: ingested   # ingested | reasoned | replied | archived
---

<!-- TL;DR placeholder -->

## Message 1 — 2026-04-20 13:45 — billing@vendor.com
Subject: Invoice March 2026

[body markdown]

## Message 2 — ...
```

### `queue.jsonl`

```json
{"thread_file":"wiki/raw/mail/260420-invoice-march-2026.md","message_id":"<xyz@...>","account":1,"uid":48291,"category":"action","project":"of1","pushed_at":"2026-04-20T14:00:05Z"}
```

### `wiki/raw/<YYMMDD>-daily-tasks.md` (checked-in, redacted)

```markdown
---
title: "Daily candidate tasks — 2026-04-20"
tags: [daily-tasks, mail-derived]
created: 2026-04-20
status: pending_review
---

## Candidate issues from mail

### 1. Chuẩn bị báo cáo Q1 cho [[people-p01]]
- [ ] create issue
- Source: [[260420-invoice-march-2026]]
- Proposed title: "Chuẩn bị báo cáo Q1"
- Context: P01 yêu cầu bản draft trước 2026-04-25
- Repo: _(user chỉ định)_
```

## Tier 1 — Ingest flow

```
1. Load config/accounts.yaml + .env (dotenv)
2. Load state/accounts.json + thread-index.json
3. Load seen-message-ids.jsonl → Set<string>

4. Per account → per folder:
   a. getMailboxLock(folder)
   b. Read mailbox.uidValidity
   c. Resolve state:
      - First run: fetch mail trong first_run_lookback_days (SINCE search)
      - UIDVALIDITY changed: re-sync window, log warning
      - Else: fetch UID > last_uid
   d. Per mail (fetch envelope + source):
      - Dedupe: skip nếu messageId ∈ seenSet
      - Parse body: prefer text/plain; fallback HTML via turndown
      - Thread resolution:
        root_id = references[0] || inReplyTo || messageId
        Lookup thread-index.json:
          - Exists → append to file
          - Not exists → create new file YYMMDD-<slug(subject)>.md
            (collision → suffix -2, -3)
      - Classify: category + project (rules.yaml)
      - Write/append markdown với frontmatter đúng schema
      - Nếu category == action → append queue.jsonl
      - seenSet.add(messageId); append seen-message-ids.jsonl
      - last_uid = max(last_uid, uid)
   e. releaseLock

5. Persist state atomically (tmp + rename)
6. Log summary
```

### Error handling

- IMAP timeout: log, skip account, exit 0.
- Parse error per mail: log, skip, không advance last_uid. 3 failures liên tiếp → `state/poison.jsonl`, advance.
- Disk full: crash, next run re-ingest (dedup qua Message-ID).
- State corrupt: rename `.corrupt-<ts>`, first_run từ đầu.

### Atomicity

- State persist per-run (không per-mail).
- seen-message-ids append sau mỗi mail → crash giữa chừng → re-fetch lần sau nhưng dedup skip.
- queue.jsonl: Tier 2 đọc vào memory rồi truncate.

### What ingest does NOT do

- Không call MCP — imapflow trực tiếp.
- Không LLM.
- Không Forgejo.
- Không mark IMAP flags.

## Tier 2 — Reasoning flow

### Trigger

`claude -p --model sonnet "$(cat prompts/reasoning.md)"` với cwd = `~/dev/wiki`.

### Prompt outline (`prompts/reasoning.md`)

Per entry trong queue.jsonl:

1. Đọc thread file. Skip nếu status != "ingested".
2. TL;DR 2-3 dòng vào placeholder: bối cảnh + yêu cầu + deadline.
3. Wikilinks:
   - Project tag → glob `wiki/projects/<tag>-*`
   - Sender email → codename qua `wiki/people/people-mapping.md` (gitignored)
   - Append section `## Liên quan`
4. Quick-reply decision:
   - Criteria YES: câu hỏi rõ, answer < 5 câu, trả lời được từ context hiện có, sender có codename.
   - Criteria NO: cần info ngoài, sensitivity cao, sender UNKNOWN.
   - Nếu YES:
     - Load `wiki/people/people-<codename>.md` cho tone
     - Detect language: heuristic diacritic ratio
     - Call `mcp__imap__create_reply_draft` với {account, folder, uid}
     - Append draft content vào thread file dưới `## Draft reply — <ts>`
     - status: replied
   - Nếu NO: append `## Draft reply — SKIPPED` + lý do
5. Candidate task extraction:
   - Nếu có task/deadline/request → append vào `wiki/raw/<YYMMDD>-daily-tasks.md`
   - REDACT: sender → `[[people-<codename>]]` hoặc `[[people-UNKNOWN-<hash6>]]`
6. Update frontmatter: status = reasoned/replied + reasoned_at

Sau cùng: truncate queue.jsonl. Log summary.

### Draft reply safety

- Chỉ ghi vào IMAP Drafts — không send.
- MCP fail → append error vào thread file, không advance status.

### Cost estimate

- ~3-5K input + ~1-2K output per mail action với Sonnet → ~$0.02-0.04/mail.
- 10 action mail/ngày → ~$10-15/tháng.

## Launchd config

### `com.nqcdan.mail-ingest.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.nqcdan.mail-ingest</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>cd ~/dev/mail-automation && npx tsx src/ingest.ts >> logs/ingest.log 2>&1</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>/tmp/mail-ingest.out</string>
  <key>StandardErrorPath</key><string>/tmp/mail-ingest.err</string>
</dict>
</plist>
```

### `com.nqcdan.mail-reasoning.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>Label</key><string>com.nqcdan.mail-reasoning</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>cd ~/dev/wiki && claude -p --model sonnet "$(cat ~/dev/mail-automation/prompts/reasoning.md)" >> ~/dev/mail-automation/logs/reasoning.log 2>&1</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
</dict>
</plist>
```

## Privacy & security

- `.env` chmod 600, gitignored.
- `wiki/raw/mail/` gitignored (full content).
- `wiki/raw/<YYMMDD>-daily-tasks.md` checked-in, redacted codename.
- `wiki/people/people-mapping.md` gitignored (đã có sẵn per project CLAUDE.md).
- IMAP password plain text trong .env — chấp nhận tradeoff cho đơn giản.

## Phase rollout

- **Phase 0 — Test Day 1:** Scaffold project. Implement `ingest.ts --dry-run`. Chạy tay 1 lần → xem log phân loại đúng không với inbox thật. Không ghi file, không update state.
- **Phase 1 — Ingest only, 1-3 ngày:** Bỏ dry-run. Enable launchd ingest 1h. Chỉ Tier 1. Quan sát thread files + rules matching. Iterate rules.yaml.
- **Phase 2 — Full pipeline:** Bật Tier 2 daily. Quan sát TL;DR, draft reply quality 1 tuần.
- **Phase 3 — Multi-account:** Thêm account thứ 2+ vào accounts.yaml + .env.

## Testing approach

- Tier 1 unit test: classifier (rules matching), thread-resolver (root_id logic), slugify (collision, strip Re:).
- Tier 1 integration test: Phase 0 dry-run trên inbox thật.
- Tier 2: manual review output 1 tuần Phase 2 trước khi trust automation.

## Open items (không block)

- Log rotation: chưa cần, thêm logrotate sau nếu logs tăng.
- Seen-id pruning: monthly manual via `prune-seen.sh`.
- Thread merging: nếu thread bị split (client không set References đúng) → manual merge sau.
- Reply-all vs reply-to-sender: create_reply_draft default reply-all (theo MCP docs) — user review trước khi send.
