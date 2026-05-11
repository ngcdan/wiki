# Mail Automation Enhancement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Telegram bot as full control interface + Tier 2 reasoning pipeline to the existing mail-automation ingest system.

**Architecture:** Monolith approach — single long-running Telegram bot process (grammy + pm2) acts as central dispatcher. Bot watches `events.jsonl` written by ingest, sends notifications, spawns `claude -p` for reasoning, handles config management via commands. Existing ingest code stays mostly unchanged.

**Tech Stack:** TypeScript, grammy (Telegram), tsx, pm2, claude CLI (headless), existing imapflow/mailparser/yaml stack.

**Spec:** `wiki/raw/260502-mail-automation-enhance-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/ingest.ts` | Modify | Replace `queue.jsonl` writes with `events.jsonl` writes (per-mail + run summary events) |
| `src/bot/index.ts` | Create | Bot entry point: init grammy, register commands, start event watcher, graceful shutdown |
| `src/bot/auth.ts` | Create | Owner-only middleware: check `chat.id === TELEGRAM_OWNER_ID` |
| `src/bot/state.ts` | Create | Conversation state machine (idle/awaiting_edit/awaiting_confirm/awaiting_account_step/reasoning) |
| `src/bot/event-watcher.ts` | Create | Watch `events.jsonl` with `fs.watch()`, track byte offset cursor, emit new events |
| `src/bot/commands.ts` | Create | Command handlers: /status, /recent, /rules, /accounts, /ingest, /queue, /reason, /cancel |
| `src/bot/interactions.ts` | Create | Inline keyboard callback handlers: reason_now, skip, approve, edit, edit_again, cancel |
| `src/bot/config-manager.ts` | Create | Read/write `config/rules.yaml` and `config/accounts.yaml`, validate after write, rollback on corrupt |
| `src/bot/account-flow.ts` | Create | Guided add-account flow (6-step conversation), write to accounts.yaml + .env |
| `src/bot/reasoning.ts` | Create | Spawn `claude -p`, compose prompt, parse structured output (TLDR/DRAFT/TASKS sections) |
| `src/bot/thread-updater.ts` | Create | Update thread markdown files: add draft reply section, update frontmatter status |
| `src/bot/formatting.ts` | Create | Telegram message formatting helpers (mail notification, TL;DR, draft display) |
| `prompts/reasoning-system.md` | Create | System context prompt (from existing reasoning.md safety rules + input section) |
| `prompts/reasoning-single.md` | Create | Per-thread reasoning prompt (from existing reasoning.md step 2, with output delimiters) |
| `prompts/draft-reply.md` | Create | Prompt for second claude -p spawn: create IMAP draft via MCP tool |
| `package.json` | Modify | Add `grammy` dependency, add `bot` script |
| `.gitignore` | Modify | Add `events.jsonl` |

---

## Task 1: Install grammy and add bot script

**Files:**
- Modify: `package.json`
- Modify: `.gitignore`

- [ ] **Step 1: Install grammy**

```bash
npm install grammy
```

- [ ] **Step 2: Add bot script to package.json**

In `package.json`, add to `"scripts"`:
```json
"bot": "tsx src/bot/index.ts"
```

- [ ] **Step 3: Update .gitignore**

Append to `.gitignore`:
```
events.jsonl
state/event-cursor.json
```

- [ ] **Step 4: Add env var placeholders**

Append to `.env`:
```
TELEGRAM_BOT_TOKEN=
TELEGRAM_OWNER_ID=
REASONING_TIMEOUT_MS=180000
```

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json .gitignore
git commit -m "chore: add grammy dependency and bot script"
```

---

## Task 2: Modify ingest to write events.jsonl instead of queue.jsonl

**Files:**
- Modify: `src/ingest.ts:16,189-201`

- [ ] **Step 1: Replace QUEUE_PATH with EVENTS_PATH**

In `src/ingest.ts`, change line 16:
```typescript
// Before
const QUEUE_PATH = `${ROOT}queue.jsonl`;

// After
const EVENTS_PATH = `${ROOT}events.jsonl`;
```

- [ ] **Step 2: Replace queue.jsonl write with per-mail event**

In `src/ingest.ts`, replace the `if (category === "action")` block (lines 189-202):

```typescript
// Before
if (category === "action") {
  appendFileSync(
    QUEUE_PATH,
    JSON.stringify({
      thread_file: `wiki/raw/mail/${threadFilename}`,
      message_id: messageId,
      account: acc.id,
      uid,
      category,
      project,
      pushed_at: new Date().toISOString(),
    }) + "\n"
  );
  summary.queued++;
}

// After
if (category === "action") {
  appendFileSync(
    EVENTS_PATH,
    JSON.stringify({
      type: "new_action_mail",
      at: new Date().toISOString(),
      account: acc.id,
      folder,
      uid,
      message_id: messageId,
      thread_file: `wiki/raw/mail/${threadFilename}`,
      subject: subject.slice(0, 200),
      from: fromStr,
      category,
      project,
    }) + "\n"
  );
  summary.queued++;
}
```

- [ ] **Step 3: Add run summary event after each folder**

After `summaries.push(summary);` (line 219), before the `finally` block, add:

```typescript
if (!DRY_RUN) {
  appendFileSync(
    EVENTS_PATH,
    JSON.stringify({
      type: "ingest_complete",
      at: new Date().toISOString(),
      account: acc.id,
      folder,
      new_threads: summary.new_threads,
      appended: summary.appended,
      queued: summary.queued,
    }) + "\n"
  );
}
```

- [ ] **Step 4: Verify ingest:dry still works**

```bash
npm run ingest:dry
```

Expected: No errors, no file writes, same summary output as before.

- [ ] **Step 5: Commit**

```bash
git add src/ingest.ts
git commit -m "feat: replace queue.jsonl with events.jsonl in ingest"
```

---

## Task 3: Bot auth middleware

**Files:**
- Create: `src/bot/auth.ts`

- [ ] **Step 1: Create auth middleware**

```typescript
import type { Context, NextFunction } from "grammy";

export function ownerOnly(ownerId: number) {
  return async (ctx: Context, next: NextFunction): Promise<void> => {
    if (ctx.chat?.id !== ownerId) return;
    await next();
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/auth.ts
git commit -m "feat: add owner-only auth middleware for Telegram bot"
```

---

## Task 4: Conversation state machine

**Files:**
- Create: `src/bot/state.ts`

- [ ] **Step 1: Create state machine**

```typescript
export type BotState =
  | { kind: "idle" }
  | { kind: "awaiting_edit"; threadFile: string; uid: number; account: number; tldr: string; tasks: string }
  | { kind: "awaiting_confirm"; threadFile: string; uid: number; account: number; draftBody: string; tldr: string; tasks: string }
  | { kind: "awaiting_account_step"; step: number; data: Partial<AccountDraft> }
  | { kind: "reasoning"; threadFile: string; uid: number; account: number };

export interface AccountDraft {
  codename: string;
  host: string;
  port: string;
  user: string;
  password: string;
  folders: string;
}

export class ConversationState {
  private current: BotState = { kind: "idle" };

  get(): BotState {
    return this.current;
  }

  set(state: BotState): void {
    this.current = state;
  }

  reset(): void {
    this.current = { kind: "idle" };
  }

  isIdle(): boolean {
    return this.current.kind === "idle";
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/state.ts
git commit -m "feat: add conversation state machine for bot"
```

---

## Task 5: Event watcher

**Files:**
- Create: `src/bot/event-watcher.ts`

- [ ] **Step 1: Create event watcher with cursor persistence**

```typescript
import { watch, writeFileSync, existsSync, statSync, openSync, readSync, closeSync } from "node:fs";
import { readFileSync } from "node:fs";
import { EventEmitter } from "node:events";

export interface IngestEvent {
  type: "new_action_mail" | "ingest_complete";
  at: string;
  account: number;
  folder: string;
  [key: string]: unknown;
}

export class EventWatcher extends EventEmitter {
  private cursorPath: string;
  private eventsPath: string;
  private offset: number; // byte offset

  constructor(eventsPath: string, cursorPath: string) {
    super();
    this.eventsPath = eventsPath;
    this.cursorPath = cursorPath;
    this.offset = this.loadCursor();
  }

  start(): void {
    // Process any events written while bot was down
    this.processNewEvents();

    // Watch for changes
    if (existsSync(this.eventsPath)) {
      watch(this.eventsPath, () => this.processNewEvents());
    } else {
      const interval = setInterval(() => {
        if (existsSync(this.eventsPath)) {
          clearInterval(interval);
          watch(this.eventsPath, () => this.processNewEvents());
          this.processNewEvents();
        }
      }, 5000);
    }
  }

  private processNewEvents(): void {
    if (!existsSync(this.eventsPath)) return;

    const stat = statSync(this.eventsPath);
    if (stat.size <= this.offset) return;

    // Read only new bytes using Buffer to handle byte offset correctly
    const bytesToRead = stat.size - this.offset;
    const buf = Buffer.alloc(bytesToRead);
    const fd = openSync(this.eventsPath, "r");
    try {
      readSync(fd, buf, 0, bytesToRead, this.offset);
    } finally {
      closeSync(fd);
    }

    const newContent = buf.toString("utf8");
    const lines = newContent.split("\n");

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const event = JSON.parse(line) as IngestEvent;
        this.emit("event", event);
      } catch {
        // skip malformed line
      }
    }

    this.offset = stat.size;
    this.saveCursor();
  }

  private loadCursor(): number {
    if (!existsSync(this.cursorPath)) return 0;
    try {
      const data = JSON.parse(readFileSync(this.cursorPath, "utf8"));
      return data.byte_offset ?? 0;
    } catch {
      return 0;
    }
  }

  private saveCursor(): void {
    writeFileSync(
      this.cursorPath,
      JSON.stringify({ byte_offset: this.offset, last_read_at: new Date().toISOString() })
    );
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/event-watcher.ts
git commit -m "feat: add event watcher with cursor persistence"
```

---

## Task 6: Telegram message formatting helpers

**Files:**
- Create: `src/bot/formatting.ts`

- [ ] **Step 1: Create formatting functions**

```typescript
import type { IngestEvent } from "./event-watcher.js";

export function formatNewMailNotification(event: IngestEvent): string {
  const lines = [
    `📬 *New action mail*`,
    `*From:* ${escapeMarkdown(String(event.from ?? "unknown"))}`,
    `*Subject:* ${escapeMarkdown(String(event.subject ?? "(no subject)"))}`,
    `*Project:* ${event.project ?? "other"} | *Category:* ${event.category ?? "action"}`,
  ];
  return lines.join("\n");
}

export function formatTldr(tldr: string): string {
  return `📝 *TL;DR:*\n${escapeMarkdown(tldr)}`;
}

export function formatDraft(body: string): string {
  return `✏️ *Draft reply:*\n───────────────\n${escapeMarkdown(body)}\n───────────────`;
}

export function formatDraftSkipped(reason: string): string {
  return `⏭ *Draft skipped:* ${escapeMarkdown(reason)}`;
}

export function formatIngestSummary(event: IngestEvent): string {
  return (
    `📊 *Ingest complete*\n` +
    `Account: ${event.account} | Folder: ${event.folder}\n` +
    `New: ${event.new_threads ?? 0} | Appended: ${event.appended ?? 0} | Queued: ${event.queued ?? 0}`
  );
}

export function escapeMarkdown(text: string): string {
  return text.replace(/([_*\[\]()~`>#+\-=|{}.!\\])/g, "\\$1");
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/formatting.ts
git commit -m "feat: add Telegram message formatting helpers"
```

---

## Task 7: Config manager (rules + accounts YAML read/write)

**Files:**
- Create: `src/bot/config-manager.ts`

- [ ] **Step 1: Create config manager**

```typescript
import { readFileSync, writeFileSync, existsSync, appendFileSync, chmodSync } from "node:fs";
import YAML from "yaml";

interface MatchBlock {
  sender_regex?: string;
  subject_regex?: string;
  header?: string;
  sender_domain?: string[];
}

interface Rule {
  name: string;
  match?: MatchBlock;
}

interface RulesFile {
  categories: Rule[];
  projects: Rule[];
}

interface AccountYaml {
  id: number;
  codename: string;
  host_env: string;
  port_env: string;
  user_env: string;
  password_env: string;
  tls_env: string;
  folders: string[];
  first_run_lookback_days: number;
}

interface AccountsFile {
  accounts: AccountYaml[];
}

const VALID_FIELDS = ["sender_regex", "subject_regex", "header", "sender_domain"] as const;
type MatchField = typeof VALID_FIELDS[number];

export class ConfigManager {
  constructor(
    private rulesPath: string,
    private accountsPath: string,
    private envPath: string,
  ) {}

  // --- Rules ---

  loadRules(): RulesFile {
    const raw = readFileSync(this.rulesPath, "utf8");
    return YAML.parse(raw) as RulesFile;
  }

  listRules(dimension?: "categories" | "projects"): string {
    const rules = this.loadRules();
    const lines: string[] = [];

    const format = (label: string, list: Rule[]) => {
      lines.push(`📋 ${label}:`);
      for (const r of list) {
        if (!r.match) {
          lines.push(`  • ${r.name} (fallback)`);
          continue;
        }
        const fields = Object.keys(r.match).join(", ");
        lines.push(`  • ${r.name} — ${fields}`);
      }
    };

    if (!dimension || dimension === "categories") format("Categories", rules.categories);
    if (!dimension || dimension === "projects") format("Projects", rules.projects);
    return lines.join("\n");
  }

  addRule(
    dimension: "categories" | "projects",
    name: string,
    field: string,
    pattern: string,
  ): string {
    if (!VALID_FIELDS.includes(field as MatchField)) {
      return `❌ Invalid field "${field}". Valid: ${VALID_FIELDS.join(", ")}`;
    }

    const rules = this.loadRules();
    const list = rules[dimension];
    const existing = list.find((r) => r.name === name);

    if (existing) {
      if (!existing.match) existing.match = {};
      if (field === "sender_domain") {
        existing.match.sender_domain = [...(existing.match.sender_domain ?? []), pattern];
      } else {
        (existing.match as Record<string, string>)[field] = pattern;
      }
    } else {
      const newRule: Rule = { name, match: {} };
      if (field === "sender_domain") {
        newRule.match!.sender_domain = [pattern];
      } else {
        (newRule.match as Record<string, string>)[field] = pattern;
      }
      // Insert before last rule (which may be a fallback with no match)
      const lastRule = list[list.length - 1];
      if (lastRule && !lastRule.match) {
        list.splice(list.length - 1, 0, newRule);
      } else {
        list.push(newRule);
      }
    }

    this.saveRules(rules);
    return `✅ Added to ${dimension}/${name}: ${field} = ${pattern}`;
  }

  deleteRule(dimension: "categories" | "projects", name: string): string | null {
    const rules = this.loadRules();
    const list = rules[dimension];
    const idx = list.findIndex((r) => r.name === name);
    if (idx === -1) return null;
    list.splice(idx, 1);
    this.saveRules(rules);
    return `✅ Deleted rule "${name}" from ${dimension}`;
  }

  private saveRules(rules: RulesFile): void {
    const backup = readFileSync(this.rulesPath, "utf8");
    const yaml = YAML.stringify(rules);
    writeFileSync(this.rulesPath, yaml);
    // Validate by re-parsing
    try {
      YAML.parse(readFileSync(this.rulesPath, "utf8"));
    } catch {
      writeFileSync(this.rulesPath, backup);
      throw new Error("YAML validation failed, rolled back");
    }
  }

  // --- Accounts ---

  loadAccounts(): AccountsFile {
    const raw = readFileSync(this.accountsPath, "utf8");
    return YAML.parse(raw) as AccountsFile;
  }

  listAccounts(): string {
    const accs = this.loadAccounts();
    const lines = ["📧 Accounts:"];
    for (const a of accs.accounts) {
      lines.push(`  • #${a.id} "${a.codename}" — folders: ${a.folders.join(", ")}`);
    }
    return lines.join("\n");
  }

  nextAccountId(): number {
    const accs = this.loadAccounts();
    return Math.max(0, ...accs.accounts.map((a) => a.id)) + 1;
  }

  addAccount(data: {
    codename: string;
    host: string;
    port: string;
    user: string;
    password: string;
    folders: string[];
  }): { id: number; result: string } {
    const id = this.nextAccountId();
    const prefix = `ACCOUNT_${id}`;

    // Write to .env
    const envLines = [
      "",
      `${prefix}_HOST=${data.host}`,
      `${prefix}_PORT=${data.port}`,
      `${prefix}_USER=${data.user}`,
      `${prefix}_PASSWORD=${data.password}`,
      `${prefix}_TLS=true`,
    ].join("\n");
    appendFileSync(this.envPath, envLines + "\n");
    chmodSync(this.envPath, 0o600);

    // Write to accounts.yaml
    const accs = this.loadAccounts();
    accs.accounts.push({
      id,
      codename: data.codename,
      host_env: `${prefix}_HOST`,
      port_env: `${prefix}_PORT`,
      user_env: `${prefix}_USER`,
      password_env: `${prefix}_PASSWORD`,
      tls_env: `${prefix}_TLS`,
      folders: data.folders,
      first_run_lookback_days: 7,
    });
    writeFileSync(this.accountsPath, YAML.stringify(accs));

    return { id, result: `✅ Account #${id} "${data.codename}" added.` };
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/config-manager.ts
git commit -m "feat: add config manager for rules and accounts YAML"
```

---

## Task 8: Account add guided flow

**Files:**
- Create: `src/bot/account-flow.ts`

- [ ] **Step 1: Create guided account flow handler**

```typescript
import type { Context } from "grammy";
import type { ConversationState, AccountDraft } from "./state.js";
import type { ConfigManager } from "./config-manager.js";
import { InlineKeyboard } from "grammy";

const STEPS = [
  { key: "codename" as const, prompt: "1/6 — Codename (ví dụ: personal-gmail):" },
  { key: "host" as const, prompt: "2/6 — IMAP host:" },
  { key: "port" as const, prompt: "3/6 — Port (mặc định 993):" },
  { key: "user" as const, prompt: "4/6 — Username (email):" },
  { key: "password" as const, prompt: "5/6 — Password:" },
  { key: "folders" as const, prompt: "6/6 — Folders (phân cách dấu phẩy, mặc định INBOX):" },
];

export function startAccountFlow(state: ConversationState): string {
  state.set({ kind: "awaiting_account_step", step: 0, data: {} });
  return `📧 Thêm account mới. Trả lời từng câu:\n${STEPS[0].prompt}`;
}

export async function handleAccountStep(
  ctx: Context,
  state: ConversationState,
  configManager: ConfigManager,
): Promise<void> {
  const current = state.get();
  if (current.kind !== "awaiting_account_step") return;

  const text = ctx.message?.text?.trim();
  if (!text) return;

  const stepDef = STEPS[current.step];
  const data = { ...current.data };
  const key = stepDef.key;

  // Handle password — delete message immediately
  if (key === "password") {
    try {
      await ctx.api.deleteMessage(ctx.chat!.id, ctx.message!.message_id);
    } catch {
      // May fail if bot lacks permission, continue anyway
    }
  }

  // Handle defaults
  if (key === "port" && text === "") {
    data[key] = "993";
  } else if (key === "folders" && text === "") {
    data[key] = "INBOX";
  } else {
    data[key] = text;
  }

  const nextStep = current.step + 1;

  if (nextStep < STEPS.length) {
    state.set({ kind: "awaiting_account_step", step: nextStep, data });
    await ctx.reply(STEPS[nextStep].prompt);
    return;
  }

  // All steps complete — save
  const folders = (data.folders ?? "INBOX").split(",").map((f) => f.trim()).filter(Boolean);

  try {
    const { id, result } = configManager.addAccount({
      codename: data.codename!,
      host: data.host!,
      port: data.port ?? "993",
      user: data.user!,
      password: data.password!,
      folders,
    });

    state.reset();
    await ctx.reply(result, {
      reply_markup: new InlineKeyboard().text("👌 Done", "account_done"),
    });
  } catch (e) {
    state.reset();
    await ctx.reply(`❌ Error adding account: ${e instanceof Error ? e.message : String(e)}`);
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/account-flow.ts
git commit -m "feat: add guided account add flow for Telegram"
```

---

## Task 9: Reasoning module (spawn claude -p, parse output)

**Files:**
- Create: `src/bot/reasoning.ts`

- [ ] **Step 1: Create reasoning module**

```typescript
import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";

const TIMEOUT_MS = parseInt(process.env.REASONING_TIMEOUT_MS ?? "180000", 10);

export interface ReasoningInput {
  threadFile: string;     // absolute path to thread markdown
  messageId: string;
  account: number;
  uid: number;
  category: string;
  project: string;
}

export interface ReasoningResult {
  tldr: string;
  draft: string | null;     // null if SKIP
  skipReason: string | null; // reason if SKIP
  tasks: string | null;      // null if NONE
  raw: string;               // raw output for fallback
}

export async function spawnReasoning(
  input: ReasoningInput,
  projectDir: string,
  promptsDir: string,
): Promise<ReasoningResult> {
  const systemPrompt = readFileSync(`${promptsDir}/reasoning-system.md`, "utf8");
  const singlePrompt = readFileSync(`${promptsDir}/reasoning-single.md`, "utf8");
  const threadContent = readFileSync(input.threadFile, "utf8");

  const peopleMappingPath = `${process.env.HOME}/dev/wiki/wiki/people/people-mapping.md`;
  const peopleMapping = existsSync(peopleMappingPath)
    ? readFileSync(peopleMappingPath, "utf8")
    : "(no people mapping file found)";

  const contextJson = JSON.stringify({
    thread_file: input.threadFile,
    thread_content: threadContent,
    message_id: input.messageId,
    account: input.account,
    uid: input.uid,
    category: input.category,
    project: input.project,
    people_mapping: peopleMapping,
  });

  const fullPrompt = `${systemPrompt}\n\n${singlePrompt}\n\n## Thread Context\n\`\`\`json\n${contextJson}\n\`\`\``;

  // Retry once on timeout
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const raw = await spawnClaude(["-p", fullPrompt], projectDir);
      return parseOutput(raw);
    } catch (e) {
      if (attempt === 0 && e instanceof Error && e.message.includes("TIMEOUT")) {
        continue; // retry once
      }
      throw e;
    }
  }
  throw new Error("unreachable");
}

function spawnClaude(args: string[], cwd: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn("claude", args, {
      cwd,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d: Buffer) => { stdout += d.toString(); });
    child.stderr.on("data", (d: Buffer) => { stderr += d.toString(); });

    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      reject(new Error(`TIMEOUT: claude -p exceeded ${TIMEOUT_MS}ms`));
    }, TIMEOUT_MS);

    child.on("close", (code) => {
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`claude -p exited ${code}\nstderr: ${stderr}`));
        return;
      }
      resolve(stdout);
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

export function parseOutput(raw: string): ReasoningResult {
  const tldr = extractSection(raw, "---TLDR---", "---DRAFT---") ?? "(parse error: no TL;DR)";
  const draftRaw = extractSection(raw, "---DRAFT---", "---TASKS---") ?? "";
  const tasksRaw = extractSection(raw, "---TASKS---", "---END---") ?? "";

  let draft: string | null = null;
  let skipReason: string | null = null;

  if (draftRaw.trim().startsWith("SKIP:")) {
    skipReason = draftRaw.trim().slice(5).trim();
  } else if (draftRaw.trim()) {
    draft = draftRaw.trim();
  }

  const tasks = tasksRaw.trim() === "NONE" || !tasksRaw.trim() ? null : tasksRaw.trim();

  return { tldr, draft, skipReason, tasks, raw };
}

function extractSection(text: string, startMarker: string, endMarker: string): string | null {
  const startIdx = text.indexOf(startMarker);
  if (startIdx === -1) return null;
  const contentStart = startIdx + startMarker.length;
  const endIdx = text.indexOf(endMarker, contentStart);
  if (endIdx === -1) return text.slice(contentStart).trim();
  return text.slice(contentStart, endIdx).trim();
}

export async function spawnDraftReply(
  uid: number,
  account: number,
  body: string,
  projectDir: string,
  promptsDir: string,
): Promise<string> {
  const draftPrompt = readFileSync(`${promptsDir}/draft-reply.md`, "utf8");
  const fullPrompt = `${draftPrompt}\n\nAccount: ${account}\nUID: ${uid}\nFolder: INBOX\nBody:\n${body}`;

  const raw = await spawnClaude(
    ["-p", "--allowedTools", "mcp__imap__create_reply_draft", fullPrompt],
    projectDir,
  );
  return raw.trim();
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/reasoning.ts
git commit -m "feat: add reasoning module to spawn claude -p and parse output"
```

---

## Task 10: Thread updater (update markdown + frontmatter)

**Files:**
- Create: `src/bot/thread-updater.ts`

- [ ] **Step 1: Create thread updater**

```typescript
import { readFileSync, writeFileSync } from "node:fs";
import YAML from "yaml";

interface Frontmatter {
  status?: string;
  reasoned_at?: string;
  replied_at?: string;
  [key: string]: unknown;
}

export function updateThreadStatus(
  filePath: string,
  status: "reasoned" | "replied",
  draftBody?: string,
): void {
  const raw = readFileSync(filePath, "utf8");
  const { frontmatter, body } = splitFrontmatter(raw);
  const fm = (YAML.parse(frontmatter) as Frontmatter) ?? {};

  fm.status = status;
  const now = new Date().toISOString();
  if (status === "reasoned") fm.reasoned_at = now;
  if (status === "replied") fm.replied_at = now;

  let newBody = body;
  if (draftBody) {
    newBody = body.replace(/\n*$/, "\n\n") +
      `## Draft reply — ${now}\n\n${draftBody.trim()}\n`;
  }

  const output = "---\n" + YAML.stringify(fm).trimEnd() + "\n---\n" + newBody;
  writeFileSync(filePath, output);
}

export function addSkippedDraft(filePath: string, reason: string): void {
  const raw = readFileSync(filePath, "utf8");
  const { frontmatter, body } = splitFrontmatter(raw);
  const fm = (YAML.parse(frontmatter) as Frontmatter) ?? {};

  fm.status = "reasoned";
  fm.reasoned_at = new Date().toISOString();

  const newBody = body.replace(/\n*$/, "\n\n") +
    `## Draft reply — SKIPPED — ${new Date().toISOString()}\nLý do: ${reason}\n`;

  const output = "---\n" + YAML.stringify(fm).trimEnd() + "\n---\n" + newBody;
  writeFileSync(filePath, output);
}

function splitFrontmatter(raw: string): { frontmatter: string; body: string } {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { frontmatter: "", body: raw };
  return { frontmatter: m[1], body: m[2] };
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/thread-updater.ts
git commit -m "feat: add thread updater for markdown frontmatter and draft sections"
```

---

## Task 11: Refactor prompts for per-mail reasoning

**Files:**
- Create: `prompts/reasoning-system.md`
- Create: `prompts/reasoning-single.md`
- Create: `prompts/draft-reply.md`

- [ ] **Step 1: Create reasoning-system.md**

Extract from existing `prompts/reasoning.md` — safety rules, input format, people mapping instructions:

```markdown
# Mail Reasoning — System Context

Bạn là Tier 2 reasoning của mail automation pipeline.

## People mapping

People mapping (codename ↔ email thật): sẽ được cung cấp trong thread context JSON field `people_mapping`.
Parse thành map `email lowercase → codename`.
Nếu content rỗng: dùng codename `UNKNOWN-<hash6 of email>` cho tất cả.

## Wiki structure

Thread files nằm tại `wiki/raw/mail/*.md` (full content).
Daily tasks output: `wiki/raw/<YYMMDD>-daily-tasks.md`.
Project notes: `wiki/projects/`.

## Safety rules

- KHÔNG auto-send mail — chỉ tạo draft content.
- KHÔNG commit git.
- KHÔNG touch Forgejo.
- KHÔNG modify IMAP flags.
- Nếu gặp lỗi: report error, không crash.

## REDACTION rules (cho candidate tasks output)

- Email + tên thật → `[[people-<codename>]]`.
- UNKNOWN sender → `[[people-UNKNOWN-<hash6>]]` + note "cần gán codename".
- Không được leak tên/email/số điện thoại thật.
```

- [ ] **Step 2: Create reasoning-single.md**

Extract from existing `prompts/reasoning.md` step 2 (2a-2e), add output delimiters:

```markdown
# Per-Thread Reasoning

Bạn nhận 1 thread mail trong JSON context. Thực hiện 3 việc:

## 1. TL;DR
Generate TL;DR 2-3 dòng tiếng Việt:
- Bối cảnh (ai, chủ đề).
- Yêu cầu chính / câu hỏi chính.
- Deadline nếu có.

## 2. Draft reply decision

Đánh giá mail có nên draft reply không.

Criteria YES (TẤT CẢ phải đạt):
- Mail có câu hỏi hoặc request rõ ràng hướng đến user.
- Trả lời được với info đã có trong thread + context.
- Reply < 5 câu.
- Sender có codename trong mapping (KHÔNG phải UNKNOWN).

Criteria NO (bất kỳ cái nào → skip):
- Cần info từ người/system khác.
- Sensitivity cao (escalation, conflict, quyết định chiến lược).
- Sender UNKNOWN.
- Mail là notification/FYI.
- Mail đã được user reply rồi (last message from user).

Nếu YES: detect language (>5% Vietnamese diacritics → Vietnamese, else English). Viết draft reply phù hợp.
Nếu NO: ghi SKIP: <lý do 1 câu>.

## 3. Candidate tasks

Nếu thread chứa task/deadline/request thực sự (không chỉ info), output candidate task.
Format:
- Short title (tiếng Việt)
- Source: thread file basename
- Context: 2-3 dòng, REDACTED
- Deadline: nếu có

Nếu không có task: output NONE.

## Output format

PHẢI output đúng format sau, không thêm text ngoài các section:

---TLDR---
<nội dung TL;DR>
---DRAFT---
<nội dung draft reply HOẶC SKIP: <lý do>>
---TASKS---
<candidate task content HOẶC NONE>
---END---
```

- [ ] **Step 3: Create draft-reply.md**

```markdown
# Draft Reply Creation

Bạn nhận thông tin để tạo draft reply trong mailbox qua MCP tool.

Gọi tool `mcp__imap__create_reply_draft` với các tham số được cung cấp dưới đây.

Chỉ gọi tool, không output text khác.
```

- [ ] **Step 4: Commit**

```bash
git add prompts/reasoning-system.md prompts/reasoning-single.md prompts/draft-reply.md
git commit -m "feat: add per-mail reasoning prompts (system, single, draft-reply)"
```

---

## Task 12: Bot commands handler

**Files:**
- Create: `src/bot/commands.ts`

- [ ] **Step 1: Create commands handler**

```typescript
import type { Context } from "grammy";
import { execFile } from "node:child_process";
import { readFileSync, existsSync, statSync } from "node:fs";
import type { ConfigManager } from "./config-manager.js";
import type { ConversationState } from "./state.js";
import { startAccountFlow } from "./account-flow.js";
import { InlineKeyboard } from "grammy";
import { escapeMarkdown } from "./formatting.js";

export function registerCommands(deps: {
  configManager: ConfigManager;
  state: ConversationState;
  projectDir: string;
  eventsPath: string;
  statePath: string;
}) {
  const { configManager, state, projectDir, eventsPath, statePath } = deps;

  return {
    status: async (ctx: Context) => {
      const accountsState = existsSync(`${statePath}/accounts.json`)
        ? JSON.parse(readFileSync(`${statePath}/accounts.json`, "utf8"))
        : {};
      const lines = ["📊 *Pipeline Status*"];

      for (const [accId, folders] of Object.entries(accountsState)) {
        for (const [folder, st] of Object.entries(folders as Record<string, { last_sync_at?: string; last_uid?: number }>)) {
          lines.push(`Account ${accId}/${folder}: last sync ${st.last_sync_at ?? "never"}, uid ${st.last_uid ?? 0}`);
        }
      }

      // Count pending events
      if (existsSync(eventsPath)) {
        const content = readFileSync(eventsPath, "utf8");
        const actionMails = content.split("\n").filter((l) => l.includes('"new_action_mail"')).length;
        lines.push(`\nAction mails total: ${actionMails}`);
      }

      await ctx.reply(lines.join("\n"), { parse_mode: "Markdown" });
    },

    recent: async (ctx: Context) => {
      if (!existsSync(eventsPath)) {
        await ctx.reply("No events yet.");
        return;
      }
      const content = readFileSync(eventsPath, "utf8");
      const events = content
        .split("\n")
        .filter((l) => l.includes('"new_action_mail"'))
        .map((l) => { try { return JSON.parse(l); } catch { return null; } })
        .filter(Boolean)
        .slice(-5)
        .reverse();

      if (events.length === 0) {
        await ctx.reply("No recent action mails.");
        return;
      }

      const lines = events.map((e: Record<string, unknown>, i: number) =>
        `${i + 1}. ${escapeMarkdown(String(e.subject ?? "(no subject)"))}\n   ${e.project} | ${e.from}`
      );
      await ctx.reply(`📬 *Recent action mails:*\n\n${lines.join("\n\n")}`, { parse_mode: "Markdown" });
    },

    rules: async (ctx: Context) => {
      const args = ctx.message?.text?.split(/\s+/).slice(1) ?? [];
      const dimension = args[0] === "categories" ? "categories" : args[0] === "projects" ? "projects" : undefined;
      const text = configManager.listRules(dimension);
      await ctx.reply(text);
    },

    add_rule: async (ctx: Context) => {
      const args = ctx.message?.text?.split(/\s+/).slice(1) ?? [];
      if (args.length < 4) {
        await ctx.reply("Usage: /add_rule <category|project> <name> <field> <pattern>");
        return;
      }
      const [dimStr, name, field, ...patternParts] = args;
      const dimension = dimStr === "category" ? "categories" : dimStr === "project" ? "projects" : null;
      if (!dimension) {
        await ctx.reply('❌ First arg must be "category" or "project"');
        return;
      }
      const result = configManager.addRule(dimension, name, field, patternParts.join(" "));
      await ctx.reply(result);
    },

    del_rule: async (ctx: Context) => {
      const args = ctx.message?.text?.split(/\s+/).slice(1) ?? [];
      if (args.length < 2) {
        await ctx.reply("Usage: /del_rule <category|project> <name>");
        return;
      }
      const [dimStr, name] = args;
      const dimension = dimStr === "category" ? "categories" : dimStr === "project" ? "projects" : null;
      if (!dimension) {
        await ctx.reply('❌ First arg must be "category" or "project"');
        return;
      }
      await ctx.reply(`⚠️ Delete rule "${name}" from ${dimension}?`, {
        reply_markup: new InlineKeyboard()
          .text("✅ Confirm", `delrule_confirm_${dimension}_${name}`)
          .text("❌ Cancel", "delrule_cancel"),
      });
    },

    accounts: async (ctx: Context) => {
      const text = configManager.listAccounts();
      await ctx.reply(text);
    },

    add_account: async (ctx: Context) => {
      const msg = startAccountFlow(state);
      await ctx.reply(msg);
    },

    ingest: async (ctx: Context) => {
      await ctx.reply("🔄 Triggering ingest...");
      execFile("npm", ["run", "-s", "ingest"], { cwd: projectDir }, (err, stdout, stderr) => {
        const output = stdout || stderr || "done";
        ctx.reply(`Ingest result:\n\`\`\`\n${output.slice(-500)}\n\`\`\``).catch(() => {});
      });
    },

    queue: async (ctx: Context) => {
      if (!existsSync(eventsPath)) {
        await ctx.reply("No events yet.");
        return;
      }
      const content = readFileSync(eventsPath, "utf8");
      const actionMails = content
        .split("\n")
        .filter((l) => l.includes('"new_action_mail"'))
        .map((l) => { try { return JSON.parse(l); } catch { return null; } })
        .filter(Boolean);

      // Check which ones haven't been reasoned yet (status still "ingested" in thread file)
      const pending = actionMails.filter((e: Record<string, unknown>) => {
        const threadPath = `${process.env.WIKI_ROOT ?? `${process.env.HOME}/dev/wiki`}/${e.thread_file}`;
        if (!existsSync(threadPath)) return false;
        const raw = readFileSync(threadPath, "utf8");
        return raw.includes('status: ingested');
      });

      if (pending.length === 0) {
        await ctx.reply("Queue is empty — no pending action mails.");
        return;
      }

      const lines = pending.slice(-10).map((e: Record<string, unknown>, i: number) =>
        `${i + 1}. ${escapeMarkdown(String(e.subject ?? "(no subject)"))}\n   ${e.project} | ${e.from}`
      );
      await ctx.reply(`📋 *Pending queue (${pending.length}):*\n\n${lines.join("\n\n")}`, { parse_mode: "Markdown" });
    },

    reason: async (ctx: Context) => {
      if (!state.isIdle()) {
        await ctx.reply("⚠️ Đang có flow khác. Gửi /cancel trước.");
        return;
      }
      if (!existsSync(eventsPath)) {
        await ctx.reply("No events to reason about.");
        return;
      }
      // Find first pending action mail
      const content = readFileSync(eventsPath, "utf8");
      const actionMails = content
        .split("\n")
        .filter((l) => l.includes('"new_action_mail"'))
        .map((l) => { try { return JSON.parse(l); } catch { return null; } })
        .filter(Boolean);

      const wikiRoot = process.env.WIKI_ROOT ?? `${process.env.HOME}/dev/wiki`;
      const pending = actionMails.find((e: Record<string, unknown>) => {
        const threadPath = `${wikiRoot}/${e.thread_file}`;
        if (!existsSync(threadPath)) return false;
        return readFileSync(threadPath, "utf8").includes('status: ingested');
      });

      if (!pending) {
        await ctx.reply("No pending mails to reason about.");
        return;
      }

      await ctx.reply(`🤖 Reasoning: ${pending.subject?.slice(0, 60)}...`);
      // Delegate to interactions.reason_now — caller (index.ts) must wire this
      return { triggerReason: pending };
    },

    cancel: async (ctx: Context) => {
      if (state.isIdle()) {
        await ctx.reply("Nothing to cancel.");
        return;
      }
      state.reset();
      await ctx.reply("🔄 Cancelled. Back to idle.");
    },
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/commands.ts
git commit -m "feat: add bot command handlers"
```

---

## Task 13: Bot interactions handler (inline keyboard callbacks)

**Files:**
- Create: `src/bot/interactions.ts`

- [ ] **Step 1: Create interactions handler**

```typescript
import type { Context } from "grammy";
import type { ConversationState } from "./state.js";
import type { ConfigManager } from "./config-manager.js";
import { spawnReasoning, spawnDraftReply, type ReasoningInput } from "./reasoning.js";
import { updateThreadStatus, addSkippedDraft } from "./thread-updater.js";
import { formatTldr, formatDraft, formatDraftSkipped } from "./formatting.js";
import { InlineKeyboard } from "grammy";
import { readFileSync, existsSync, writeFileSync, appendFileSync } from "node:fs";

export function registerInteractions(deps: {
  state: ConversationState;
  configManager: ConfigManager;
  projectDir: string;
  promptsDir: string;
  wikiRoot: string;
}) {
  const { state, configManager, projectDir, promptsDir, wikiRoot } = deps;

  return {
    reason_now: async (ctx: Context, eventData: { threadFile: string; uid: number; account: number; messageId: string; category: string; project: string }) => {
      await ctx.answerCallbackQuery("🤖 Starting reasoning...");
      await ctx.editMessageReplyMarkup({ reply_markup: undefined });

      const threadFilePath = `${wikiRoot}/${eventData.threadFile}`;
      if (!existsSync(threadFilePath)) {
        await ctx.reply(`❌ Thread file not found: ${eventData.threadFile}`);
        return;
      }

      state.set({ kind: "reasoning", threadFile: threadFilePath, uid: eventData.uid, account: eventData.account });
      await ctx.reply("🤖 Đang reasoning...");

      try {
        const input: ReasoningInput = {
          threadFile: threadFilePath,
          messageId: eventData.messageId,
          account: eventData.account,
          uid: eventData.uid,
          category: eventData.category,
          project: eventData.project,
        };
        const result = await spawnReasoning(input, projectDir, promptsDir);

        // If parse failed (no delimiters found), send raw output for manual decision
        if (result.tldr === "(parse error: no TL;DR)") {
          state.reset();
          await ctx.reply(`⚠️ Could not parse reasoning output. Raw:\n\n\`\`\`\n${result.raw.slice(0, 3000)}\n\`\`\``);
          return;
        }

        const tldrMsg = formatTldr(result.tldr);

        if (result.draft) {
          const draftMsg = formatDraft(result.draft);
          state.set({
            kind: "awaiting_confirm",
            threadFile: threadFilePath,
            uid: eventData.uid,
            account: eventData.account,
            draftBody: result.draft,
            tldr: result.tldr,
            tasks: result.tasks ?? "",
          });
          await ctx.reply(`${tldrMsg}\n\n${draftMsg}`, {
            parse_mode: "Markdown",
            reply_markup: new InlineKeyboard()
              .text("✅ Approve", "approve_draft")
              .text("✏️ Edit", "edit_draft")
              .text("❌ Skip", "skip_draft"),
          });
        } else {
          const skipMsg = formatDraftSkipped(result.skipReason ?? "unknown");
          addSkippedDraft(threadFilePath, result.skipReason ?? "unknown");

          // Handle tasks if any
          if (result.tasks) {
            appendCandidateTasks(result.tasks, wikiRoot);
          }

          state.reset();
          await ctx.reply(`${tldrMsg}\n\n${skipMsg}`, { parse_mode: "Markdown" });
        }
      } catch (e) {
        state.reset();
        const msg = e instanceof Error ? e.message : String(e);
        await ctx.reply(`❌ Reasoning failed: ${msg.slice(0, 500)}`);
      }
    },

    approve_draft: async (ctx: Context) => {
      const current = state.get();
      if (current.kind !== "awaiting_confirm") return;
      await ctx.answerCallbackQuery("Creating draft...");
      await ctx.editMessageReplyMarkup({ reply_markup: undefined });

      try {
        await spawnDraftReply(current.uid, current.account, current.draftBody, projectDir, promptsDir);
        updateThreadStatus(current.threadFile, "replied", current.draftBody);
        if (current.tasks) appendCandidateTasks(current.tasks, wikiRoot);
        state.reset();
        await ctx.reply("✅ Draft created in mailbox. Review in mail app.");
      } catch (e) {
        updateThreadStatus(current.threadFile, "reasoned");
        state.reset();
        await ctx.reply(`❌ Draft creation failed: ${e instanceof Error ? e.message : String(e)}`);
      }
    },

    edit_draft: async (ctx: Context) => {
      const current = state.get();
      if (current.kind !== "awaiting_confirm") return;
      await ctx.answerCallbackQuery();
      await ctx.editMessageReplyMarkup({ reply_markup: undefined });

      state.set({
        kind: "awaiting_edit",
        threadFile: current.threadFile,
        uid: current.uid,
        account: current.account,
        tldr: current.tldr,
        tasks: current.tasks,
      });
      await ctx.reply("Gửi nội dung reply mới:");
    },

    skip_draft: async (ctx: Context) => {
      const current = state.get();
      if (current.kind !== "awaiting_confirm") return;
      await ctx.answerCallbackQuery("Skipped");
      await ctx.editMessageReplyMarkup({ reply_markup: undefined });

      addSkippedDraft(current.threadFile, "User skipped via Telegram");
      if (current.tasks) appendCandidateTasks(current.tasks, wikiRoot);
      state.reset();
      await ctx.reply("⏭ Draft skipped.");
    },

    handle_edit_text: async (ctx: Context) => {
      const current = state.get();
      if (current.kind !== "awaiting_edit") return;
      const newBody = ctx.message?.text?.trim();
      if (!newBody) return;

      state.set({
        kind: "awaiting_confirm",
        threadFile: current.threadFile,
        uid: current.uid,
        account: current.account,
        draftBody: newBody,
        tldr: current.tldr,
        tasks: current.tasks,
      });

      await ctx.reply(formatDraft(newBody), {
        parse_mode: "Markdown",
        reply_markup: new InlineKeyboard()
          .text("✅ Approve", "approve_draft")
          .text("✏️ Edit again", "edit_draft")
          .text("❌ Skip", "skip_draft"),
      });
    },

    delrule_confirm: async (ctx: Context, dimension: "categories" | "projects", name: string) => {
      const result = configManager.deleteRule(dimension, name);
      await ctx.answerCallbackQuery();
      await ctx.editMessageText(result ?? `❌ Rule "${name}" not found`);
    },

    delrule_cancel: async (ctx: Context) => {
      await ctx.answerCallbackQuery("Cancelled");
      await ctx.editMessageText("❌ Cancelled.");
    },
  };
}

function appendCandidateTasks(tasksContent: string, wikiRoot: string): void {
  const now = new Date();
  const yy = String(now.getFullYear()).slice(-2);
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  const dateStr = `${now.getFullYear()}-${mm}-${dd}`;
  const prefix = `${yy}${mm}${dd}`;
  const filePath = `${wikiRoot}/wiki/raw/${prefix}-daily-tasks.md`;

  if (!existsSync(filePath)) {
    writeFileSync(
      filePath,
      `---\ntitle: "Daily candidate tasks — ${dateStr}"\ntags: [daily-tasks, mail-derived]\ncreated: ${dateStr}\nstatus: pending_review\n---\n\n## Candidate issues from mail\n\n`,
    );
  }

  appendFileSync(filePath, tasksContent + "\n\n");
}
```

- [ ] **Step 2: Commit**

```bash
git add src/bot/interactions.ts
git commit -m "feat: add bot interaction handlers (approve, edit, skip drafts)"
```

---

## Task 14: Bot entry point (wire everything together)

**Files:**
- Create: `src/bot/index.ts`

- [ ] **Step 1: Create bot entry point**

```typescript
import "dotenv/config";
import { Bot } from "grammy";
import { ownerOnly } from "./auth.js";
import { ConversationState } from "./state.js";
import { EventWatcher, type IngestEvent } from "./event-watcher.js";
import { ConfigManager } from "./config-manager.js";
import { registerCommands } from "./commands.js";
import { registerInteractions } from "./interactions.js";
import { handleAccountStep } from "./account-flow.js";
import { formatNewMailNotification, formatIngestSummary } from "./formatting.js";
import { InlineKeyboard } from "grammy";

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const OWNER_ID = parseInt(process.env.TELEGRAM_OWNER_ID ?? "0", 10);

if (!TOKEN) throw new Error("TELEGRAM_BOT_TOKEN not set");
if (!OWNER_ID) throw new Error("TELEGRAM_OWNER_ID not set");

const ROOT = new URL("../..", import.meta.url).pathname;
const EVENTS_PATH = `${ROOT}events.jsonl`;
const CURSOR_PATH = `${ROOT}state/event-cursor.json`;
const STATE_DIR = `${ROOT}state`;
const RULES_PATH = `${ROOT}config/rules.yaml`;
const ACCOUNTS_PATH = `${ROOT}config/accounts.yaml`;
const ENV_PATH = `${ROOT}.env`;
const PROMPTS_DIR = `${ROOT}prompts`;
const WIKI_ROOT = process.env.WIKI_ROOT ?? `${process.env.HOME}/dev/wiki`;

const bot = new Bot(TOKEN);
const state = new ConversationState();
const configManager = new ConfigManager(RULES_PATH, ACCOUNTS_PATH, ENV_PATH);
const watcher = new EventWatcher(EVENTS_PATH, CURSOR_PATH);

// Auth middleware — owner only
bot.use(ownerOnly(OWNER_ID));

// Register commands
const commands = registerCommands({
  configManager,
  state,
  projectDir: ROOT,
  eventsPath: EVENTS_PATH,
  statePath: STATE_DIR,
});

const interactions = registerInteractions({
  state,
  configManager,
  projectDir: ROOT,
  promptsDir: PROMPTS_DIR,
  wikiRoot: WIKI_ROOT,
});

// Pending events that await user interaction (keyed by callback data suffix)
const pendingEvents = new Map<string, Record<string, unknown>>();

// Commands
bot.command("status", commands.status);
bot.command("recent", commands.recent);
bot.command("rules", commands.rules);
bot.command("add_rule", commands.add_rule);
bot.command("del_rule", commands.del_rule);
bot.command("accounts", commands.accounts);
bot.command("add_account", commands.add_account);
bot.command("ingest", commands.ingest);
bot.command("queue", commands.queue);
bot.command("reason", async (ctx) => {
  const result = await commands.reason(ctx);
  if (result?.triggerReason) {
    const event = result.triggerReason;
    await interactions.reason_now(ctx, {
      threadFile: event.thread_file,
      uid: event.uid,
      account: event.account,
      messageId: event.message_id,
      category: event.category,
      project: event.project,
    });
  }
});
bot.command("cancel", commands.cancel);

// Callback queries
bot.callbackQuery("approve_draft", (ctx) => interactions.approve_draft(ctx));
bot.callbackQuery("edit_draft", (ctx) => interactions.edit_draft(ctx));
bot.callbackQuery("skip_draft", (ctx) => interactions.skip_draft(ctx));
bot.callbackQuery("account_done", (ctx) => { ctx.answerCallbackQuery("👌"); ctx.editMessageReplyMarkup({ reply_markup: undefined }); });
bot.callbackQuery(/^delrule_confirm_(.+)_(.+)$/, (ctx) => {
  const match = ctx.callbackQuery.data.match(/^delrule_confirm_(.+?)_(.+)$/);
  if (match) interactions.delrule_confirm(ctx, match[1] as "categories" | "projects", match[2]);
});
bot.callbackQuery("delrule_cancel", (ctx) => interactions.delrule_cancel(ctx));

// Dynamic callback for reason_now (carries event ID)
bot.callbackQuery(/^reason_(.+)$/, async (ctx) => {
  const eventId = ctx.callbackQuery.data.replace("reason_", "");
  const eventData = pendingEvents.get(eventId);
  if (!eventData) {
    await ctx.answerCallbackQuery("Event expired. Use /reason instead.");
    return;
  }
  pendingEvents.delete(eventId);
  await interactions.reason_now(ctx, eventData as any);
});

bot.callbackQuery(/^skip_event_/, async (ctx) => {
  await ctx.answerCallbackQuery("Skipped");
  await ctx.editMessageReplyMarkup({ reply_markup: undefined });
});

// Text messages — route based on state
bot.on("message:text", async (ctx) => {
  const current = state.get();

  // Commands always get handled by grammy command handlers above
  if (ctx.message.text.startsWith("/")) {
    if (ctx.message.text === "/cancel") return; // already handled
    if (!state.isIdle()) {
      await ctx.reply("⚠️ Đang có flow chưa xong. Gửi /cancel để hủy.");
      return;
    }
    return; // let grammy handle the command
  }

  switch (current.kind) {
    case "awaiting_edit":
      await interactions.handle_edit_text(ctx);
      break;
    case "awaiting_account_step":
      await handleAccountStep(ctx, state, configManager);
      break;
    case "idle":
      await ctx.reply("Gửi /status, /rules, /accounts hoặc /help để bắt đầu.");
      break;
    default:
      await ctx.reply("⚠️ Đang xử lý. Vui lòng chờ hoặc gửi /cancel.");
  }
});

// Event watcher — send notifications
watcher.on("event", async (event: IngestEvent) => {
  if (event.type === "new_action_mail") {
    const eventId = `${event.account}_${event.uid}_${Date.now()}`;
    pendingEvents.set(eventId, event);

    // Clean up old pending events (keep last 50)
    if (pendingEvents.size > 50) {
      const keys = [...pendingEvents.keys()];
      for (let i = 0; i < keys.length - 50; i++) {
        pendingEvents.delete(keys[i]);
      }
    }

    const text = formatNewMailNotification(event);
    try {
      await bot.api.sendMessage(OWNER_ID, text, {
        parse_mode: "Markdown",
        reply_markup: new InlineKeyboard()
          .text("⚡ Reason now", `reason_${eventId}`)
          .text("⏭ Skip", `skip_event_${eventId}`),
      });
    } catch (e) {
      console.error("[bot] Failed to send notification:", e);
    }
  } else if (event.type === "ingest_complete") {
    const queued = (event.queued as number) ?? 0;
    if (queued > 0 || (event.new_threads as number) > 0) {
      const text = formatIngestSummary(event);
      try {
        await bot.api.sendMessage(OWNER_ID, text, { parse_mode: "Markdown" });
      } catch (e) {
        console.error("[bot] Failed to send summary:", e);
      }
    }
  }
});

// Graceful shutdown
function shutdown() {
  console.log("[bot] shutting down...");
  bot.stop();
  process.exit(0);
}
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

// Start
console.log("[bot] starting...");
watcher.start();
bot.start({
  onStart: () => console.log("[bot] running"),
});
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add src/bot/index.ts
git commit -m "feat: add bot entry point wiring commands, interactions, and event watcher"
```

---

## Task 15: End-to-end manual test

- [ ] **Step 1: Set up Telegram bot**

1. Talk to @BotFather on Telegram, create bot, get token
2. Get your Telegram user ID (talk to @userinfobot)
3. Update `.env`:
   ```
   TELEGRAM_BOT_TOKEN=<your token>
   TELEGRAM_OWNER_ID=<your id>
   ```

- [ ] **Step 2: Start bot**

```bash
npm run bot
```

Expected: `[bot] starting...` then `[bot] running`

- [ ] **Step 3: Test basic commands**

Send to bot on Telegram:
- `/status` — should show pipeline status
- `/rules` — should list classification rules
- `/accounts` — should list account #1
- `/recent` — should show recent action mails (or "No recent action mails")

- [ ] **Step 4: Test config commands**

```
/add_rule category test_noise sender_domain example.com
/rules categories
/del_rule category test_noise
```

Verify `config/rules.yaml` is updated and rolled back correctly.

- [ ] **Step 5: Test ingest integration**

```
/ingest
```

Verify bot receives ingest result, and if there are new action mails, notification appears with [⚡ Reason now] button.

- [ ] **Step 6: Commit final state**

```bash
git add -A
git commit -m "feat: mail automation enhancement — Telegram bot + Tier 2 reasoning"
```

---

## Task 16: pm2 setup for production

- [ ] **Step 1: Install pm2 globally if not present**

```bash
npm install -g pm2
```

- [ ] **Step 2: Start bot with pm2**

```bash
cd /Users/nqcdan/dev/mail-automation
pm2 start src/bot/index.ts --interpreter tsx --name mail-bot
pm2 save
pm2 startup
```

- [ ] **Step 3: Verify auto-restart**

```bash
pm2 kill
pm2 resurrect
pm2 status
```

Expected: `mail-bot` is running.

- [ ] **Step 4: Verify logs**

```bash
pm2 logs mail-bot --lines 10
```

Expected: `[bot] starting...` and `[bot] running`
