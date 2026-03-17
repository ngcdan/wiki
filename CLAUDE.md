# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal knowledge base of Markdown notes (no application code). The primary purpose is to collect, organize, and summarize work-related notes, decisions, and ideas. AI assistance is used to clean up raw notes, generate summaries, and propose plans.

**Language:** Use Vietnamese by default unless a note's content is clearly in another language. Technical terms stay in English.

## Structure

- `notes/00_inbox/` — raw, unprocessed notes (date-prefixed filenames)
- `notes/daily/` — daily briefing reports (`YYYY-MM-DD_briefing.md`)
- `notes/weekly/` — weekly logs
- `work/` — project plans, workflows, self-reviews
- `cheatsheets/` — reference/command-sheet style docs
- `rulebooks/` — personal operating frameworks
- `automation/` — Python scripts that automate issue syncing and briefing generation
- `dev-kit/` — AI assistant configuration packs (Gemini skills, Claude guidelines for other projects)

## Note conventions

- One topic per file; avoid mixing unrelated content.
- Date-prefixed filenames for time-based entries: `YYYY-MM-DD_topic.md`.
- Date headers inside files also use `YYYY-MM-DD` format.
- Optional tags: plain bracketed words like `[backend]`, `[infra]`.
- Suggested note skeleton:
  ```
  # Title
  ## Bối cảnh
  ## Vấn đề
  ## Giải pháp/Quyết định
  ## Việc cần làm tiếp theo
  ## Lưu ý/Tham khảo
  ```
- When cleaning up notes: standardize headings/terminology first, then summarize into 3-7 bullets covering context, decision, actions, and risks. Ask only for specifically missing facts rather than guessing.

## Automation scripts (automation/)

All scripts run from `automation/` with the `.venv` activated and `.env` loaded.

**Setup:**
```bash
cd automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Requires automation/.env with API keys
```

**Run scripts directly:**
```bash
# Generate daily briefing
python daily_briefing_generator.py

# Sync Forgejo issues (adjust --days-back as needed)
python forgejo_issue_collector.py --days-back 7

# Daemon lifecycle
python daemon.py start | stop | status

# Interactive quickstart menu
bash quickstart.sh
```

**Architecture:** `daemon.py` orchestrates the other scripts on a schedule (briefing at 7AM, issue sync at 8AM/11AM/4PM). `forgejo_issue_collector.py` writes to `team_issues_summary.md` and `BACKLOG.md`. `daily_briefing_generator.py` aggregates wiki content and optionally uses AI (`ai_classifier.py`) to summarize. Notifications go via Telegram.

**Configuration** (in `automation/.env`, not committed):
- `FORGEJO_URL`, `FORGEJO_TOKEN`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `AI_PROVIDER`, `OPENAI_API_KEY` (optional)

There are no build or test commands — edits are direct Markdown or Python script updates.
