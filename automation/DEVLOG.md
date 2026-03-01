# Wiki Automation - DEVLOG

> System documentation & development log for wiki automation

**Status:** Production Ready ✅  
**Features:** Issue Collection (AI-powered) + Daily Briefing + Telegram Daemon  
**Last Updated:** 2026-02-16

---

## Architecture Overview

Hệ thống được thiết kế tối giản, tập trung vào **Issue Management** và **Information Retrieval**.

### Components

1.  **Daemon Service (`daemon.py`)**
    *   Chạy background (LaunchAgent)
    *   Tự động trigger jobs theo lịch
    *   Gửi notification & reports qua Telegram

2.  **AI Classifier (`ai_classifier.py`)**
    *   Core intelligence
    *   Phân loại Issue: Feature/Bug/Enhancement
    *   Đánh giá Priority: P0/P1/P2
    *   Detect duplicates

3.  **Issue Collector (`forgejo_issue_collector.py`)**
    *   Fetch issues từ Forgejo
    *   Chạy qua AI Classifier
    *   Update `BACKLOG.md`

4.  **Daily Briefing (`daily_briefing_generator.py`)**
    *   Tổng hợp thông tin 24h qua
    *   Top priorities từ Backlog
    *   Report gửi vào 7:00 AM

---

## Quick Start Management

### 1. Control Daemon

```bash
cd /Users/nqcdan/dev/wiki/automation
source .venv/bin/activate

python daemon.py start    # Khởi động
python daemon.py stop     # Tạm dừng
python daemon.py restart  # Apply code mới
python daemon.py status   # Check trạng thái
```

### 2. Manual Trigger (CLI)

```bash
# Force run issue sync (last 7 days)
python forgejo_issue_collector.py --days-back 7

# Force generate briefing
python daily_briefing_generator.py
```

### 3. Logs Monitoring

```bash
tail -f daemon.log           # Main service log
tail -f collectors.log       # Issue syncing details
tail -f daily_briefing.log   # Briefing generation details
```

---

## Schedule & Alerts

**Telegram Bot:** `Zoe Bot (Finance)` (Group or DM)

| Time | Task | Description |
|------|------|-------------|
| **07:00** | Daily Briefing | Tổng hợp Backlog, Priorities & Focus today |
| **08:00** | Issue Sync | Quét issues 8 giờ qua (Deep scan) |
| **11:00** | Issue Sync | Quét mới để update backlog trưa |
| **16:00** | Issue Sync | Quét mới để chốt công việc cuối ngày |
| **Realtime** | Error Alerts | Báo lỗi hệ thống ngay lập tức |
| **Every 5m** | Heartbeat | Ping `💓 Heartbeat: HH:MM:SS` để check alive |

---

## Installation & Setup

### Prerequisites
*   Python 3.9+
*   Forgejo Account (Token)
*   OpenAI API Key
*   Telegram Bot Token

### Config (`.env`)

```env
FORGEJO_URL=https://git.datatp.cloud
FORGEJO_TOKEN=***
FORGEJO_OWNER=of1-crm
AI_PROVIDER=openai
OPENAI_API_KEY=sk-***
TELEGRAM_BOT_TOKEN=***
TELEGRAM_CHAT_ID=***
```

### Auto-start (Mac LaunchAgent)

Run install script:
```bash
./install_daemon.sh
```

---

## Technical Maintenance

### File Structure
```
automation/
├── logs/                      # Log files (.log, .err)
├── data/                      # Data files (summaries, pid)
├── daemon.py                  # Process supervisor & scheduler
├── ai_classifier.py           # AI logic (OpenAI/Ollama)
├── forgejo_issue_collector.py # Issue fetching & processing
├── daily_briefing_generator.py# Report generator
├── markdown_optimizer.py      # Meta-data enhancer
├── requirements.txt           # Python deps
└── .env                       # Secrets
```

### Adding New Features
1.  Viết script python độc lập (e.g. `new_feature.py`)
2.  Test chạy manual OK
3.  Import và thêm vào `daemon.py` schedule
4.  Restart daemon

---

## Status History

*   **2026-02-16:** Phase 1 Complete.
    *   Setup AI automation (Issue Classifier + Daily Briefing).
    *   Setup Telegram Daemon.
    *   Cleaned up PR collector & Setup scripts.
    *   Consolidated documentation.
