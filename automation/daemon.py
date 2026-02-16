#!/usr/bin/env python3
"""Wiki Automation Daemon Service

Background service chạy automation tasks và gửi kết quả qua Telegram.

Features:
- Chạy như daemon (background service)
- Schedule tasks: daily briefing, PR/Issue sync
- Gửi notifications qua Telegram
- Health monitoring
- Graceful shutdown

Usage:
    python daemon.py start    # Start daemon
    python daemon.py stop     # Stop daemon
    python daemon.py status   # Check status
    python daemon.py restart  # Restart daemon
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Optional

import requests

# Import automation modules
from ai_classifier import AIClassifier
from daily_briefing_generator import DailyBriefingGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/nqcdan/dev/wiki/automation/daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram bot."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send text message to Telegram."""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_document(self, file_path: Path, caption: str = "") -> bool:
        """Send document to Telegram."""
        try:
            url = f"{self.base_url}/sendDocument"
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
            logger.info(f"Telegram document sent: {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram document: {e}")
            return False


class WikiAutomationDaemon:
    """Main daemon service for wiki automation."""

    def __init__(self):
        self.wiki_root = Path("/Users/nqcdan/dev/wiki")
        self.automation_dir = self.wiki_root / "automation"
        self.pid_file = self.automation_dir / "daemon.pid"
        self.running = False

        # Load config
        self._load_env()

        # Initialize components
        self.telegram = TelegramNotifier(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )
        self.briefing_gen = DailyBriefingGenerator(self.wiki_root)

        # Schedule config
        self.schedules = {
            "daily_briefing": time(7, 0),      # 7:00 AM
            "issue_collector_morning": time(8, 0),    # 8:00 AM
            "issue_collector_noon": time(11, 0),      # 11:00 AM
            "issue_collector_afternoon": time(16, 0), # 4:00 PM
        }

    def _load_env(self):
        """Load environment variables from .env."""
        env_file = self.automation_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

    def start(self):
        """Start the daemon."""
        if self.is_running():
            logger.error("Daemon already running")
            return False

        logger.info("Starting Wiki Automation Daemon...")
        self._write_pid()
        self.running = True

        # Send startup notification
        self.telegram.send_message(
            "🚀 *Wiki Automation Daemon Started*\n\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Schedule:\n"
            f"• Daily briefing: 7:00 AM\n"
            f"• Issue Sync: 8:00 AM, 11:00 AM, 4:00 PM"
        )

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Run main loop
        try:
            asyncio.run(self._main_loop())
        except Exception as e:
            logger.error(f"Daemon error: {e}")
            self.telegram.send_message(f"❌ *Daemon Error*\n\n{str(e)}")
        finally:
            self.stop()

        return True

    def stop(self):
        """Stop the daemon."""
        logger.info("Stopping Wiki Automation Daemon...")
        self.running = False
        self._remove_pid()
        self.telegram.send_message("🛑 *Wiki Automation Daemon Stopped*")

    def status(self):
        """Check daemon status."""
        if self.is_running():
            pid = self._read_pid()
            print(f"✅ Daemon is running (PID: {pid})")
            return True
        else:
            print("❌ Daemon is not running")
            return False

    def is_running(self) -> bool:
        """Check if daemon is running."""
        if not self.pid_file.exists():
            return False

        pid = self._read_pid()
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            self._remove_pid()
            return False

    async def _main_loop(self):
        """Main event loop."""
        logger.info("Entering main loop...")
        last_run = {}

        while self.running:
            now = datetime.now()
            current_time = now.time()

            # Check each scheduled task
            for task_name, scheduled_time in self.schedules.items():
                # Check if it's time to run
                if self._should_run(current_time, scheduled_time, last_run.get(task_name)):
                    logger.info(f"Running scheduled task: {task_name}")
                    await self._run_task(task_name)
                    last_run[task_name] = now

            # Sleep for 30 seconds before next check
            await asyncio.sleep(30)

    def _should_run(self, current: time, scheduled: time, last_run: Optional[datetime]) -> bool:
        """Check if task should run now."""
        # Within 1 minute of scheduled time
        current_minutes = current.hour * 60 + current.minute
        scheduled_minutes = scheduled.hour * 60 + scheduled.minute

        if abs(current_minutes - scheduled_minutes) > 1:
            return False

        # Not run in last hour
        if last_run:
            elapsed = (datetime.now() - last_run).total_seconds()
            if elapsed < 3600:  # 1 hour
                return False

        return True

    async def _run_task(self, task_name: str):
        """Run a scheduled task."""
        try:
            if task_name == "daily_briefing":
                await self._run_daily_briefing()
            elif "issue_collector" in task_name:
                # 8AM task looks back 7 days, others 1 day
                days = 7 if "morning" in task_name else 1
                await self._run_issue_collector(days_back=days)
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            self.telegram.send_message(
                f"❌ *Task Failed: {task_name}*\n\n{str(e)}"
            )

        if briefing_file.exists():
            self.telegram.send_document(
                briefing_file,
                caption="📄 Full daily briefing"
            )

        logger.info("Daily briefing sent to Telegram")

    async def _run_issue_collector(self, days_back: int = 7):
        """Run issue collector."""
        logger.info(f"Running issue collector (days_back={days_back})...")

        import subprocess

        result = subprocess.run(
            [
                "bash", "-c",
                "cd /Users/nqcdan/dev/wiki/automation && "
                "source .venv/bin/activate && "
                "set -a && source .env && set +a && "
                f"python forgejo_issue_collector.py --days-back {days_back}"
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Parse output
            output = result.stdout
            
            self.telegram.send_message(
                f"📋 *Issue Collector*\n\n"
                f"Status: ✅ Success\n"
                f"Collected issues from last {days_back} days\n"
                f"BACKLOG updated"
            )
        else:
            self.telegram.send_message(
                f"❌ *Issue Collector Failed*\n\n{result.stderr[:500]}"
            )

        logger.info("Issue collector completed")



    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        self.running = False

    def _write_pid(self):
        """Write PID file."""
        self.pid_file.write_text(str(os.getpid()))

    def _read_pid(self) -> int:
        """Read PID from file."""
        return int(self.pid_file.read_text().strip())

    def _remove_pid(self):
        """Remove PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python daemon.py {start|stop|status|restart}")
        sys.exit(1)

    command = sys.argv[1]
    daemon = WikiAutomationDaemon()

    if command == "start":
        daemon.start()
    elif command == "stop":
        daemon.stop()
    elif command == "status":
        daemon.status()
    elif command == "restart":
        daemon.stop()
        daemon.start()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
