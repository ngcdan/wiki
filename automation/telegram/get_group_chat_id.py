#!/usr/bin/env python3
"""Get Telegram group chat_id via Bot API getUpdates.

How it works:
- Telegram only reveals group chat_id to your bot after the bot receives an update.
- So you must add the bot to the group and send a message in the group first.

Security:
- Do NOT hardcode tokens.
- Provide token via env var TELEGRAM_BOT_TOKEN.

Usage:
  export TELEGRAM_BOT_TOKEN='123:abc...'
  python3 get_group_chat_id.py --tail 200

Tips:
- You can filter by title: --title "My Group"
- You can print only groups: default behavior
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, Optional


def api_get(token: str, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    q = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = f"https://api.telegram.org/bot{token}/{method}{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-wiki-automation"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {body}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail", type=int, default=200, help="How many updates to fetch")
    ap.add_argument("--title", type=str, default=None, help="Filter groups by chat title contains this string")
    ap.add_argument("--include-private", action="store_true", help="Also show private chats/users")
    ap.add_argument("--delete-webhook", action="store_true", help="Call deleteWebhook(drop_pending_updates=true) then exit")
    args = ap.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
        sys.exit(2)

    if args.delete_webhook:
        res = api_get(token, "deleteWebhook", {"drop_pending_updates": "true"})
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    try:
        data = api_get(token, "getUpdates", {"limit": args.tail})
    except RuntimeError as e:
        msg = str(e)
        # Bot API returns 409 Conflict when a webhook is set for the bot.
        if "HTTP 409" in msg and "Conflict" in msg:
            print("ERROR: Telegram Bot API returned 409 Conflict for getUpdates.")
            print("This usually means the bot currently has a webhook configured, so long-polling getUpdates is blocked.")
            print("Fix options:")
            print("1) Remove webhook (recommended if you use polling):")
            print("   export TELEGRAM_BOT_TOKEN='...'")
            print("   python3 get_group_chat_id.py --delete-webhook")
            print("2) Or disable webhook in your app and retry.")
            sys.exit(3)
        raise

    if not data.get("ok"):
        print("ERROR: getUpdates failed:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        sys.exit(1)

    updates = data.get("result", [])

    chats: dict[int, dict] = {}

    def consider(chat: dict):
        if not chat:
            return
        chat_id = chat.get("id")
        if not isinstance(chat_id, int):
            return
        chats.setdefault(chat_id, chat)

    for u in updates:
        # common update types
        msg = u.get("message") or u.get("edited_message") or u.get("channel_post") or u.get("my_chat_member")
        if isinstance(msg, dict):
            chat = msg.get("chat")
            consider(chat)
        # membership updates store chat nested
        if isinstance(u.get("my_chat_member"), dict):
            consider(u["my_chat_member"].get("chat"))

    rows = []
    for cid, chat in chats.items():
        ctype = chat.get("type")
        title = chat.get("title") or ""
        username = chat.get("username") or ""

        is_group = ctype in ("group", "supergroup")
        if not args.include_private and not is_group:
            continue

        if args.title and args.title.lower() not in title.lower():
            continue

        rows.append((ctype, title, username, cid))

    rows.sort(key=lambda r: (r[0], r[1], r[3]))

    if not rows:
        print("No matching chats found in recent updates.")
        print("Checklist:")
        print("- Add the bot to the target group")
        print("- Send at least 1 message in that group (e.g. 'hi')")
        print("- Re-run this script")
        return

    print("type\ttitle\tusername\tchat_id")
    for r in rows:
        print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}")


if __name__ == "__main__":
    main()
