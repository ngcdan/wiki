#!/usr/bin/env python3
"""Get Telegram Chat ID

Hướng dẫn:
1. Gửi message bất kỳ cho bot @nqcdan_finance_bot trên Telegram
2. Chạy script này để lấy chat ID
3. Chat ID sẽ tự động update vào .env
"""

import json
import os
import sys

import requests

BOT_TOKEN = "8217173221:AAHAZmSW-ccDtOdAD4WmHDYY_oGgIhSI-Ok"
ENV_FILE = "/Users/nqcdan/dev/wiki/automation/.env"

def get_chat_id():
    """Get chat ID from Telegram updates."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            print("❌ Error:", data.get("description"))
            return None
        
        updates = data.get("result", [])
        if not updates:
            print("❌ Không có message nào")
            print()
            print("📱 Hướng dẫn:")
            print("   Option 1 (Private): Gửi message trực tiếp cho @nqcdan_finance_bot")
            print("   Option 2 (Group): Add bot vào group và gửi message bất kỳ")
            return None
        
        # Get latest chat
        latest = updates[-1]
        message = latest.get("message", {})
        chat = message.get("chat", {})
        
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        chat_title = chat.get("title", "Private Chat")
        
        if chat_id:
            print(f"✅ Chat ID: {chat_id}")
            print(f"📍 Chat Type: {chat_type}")
            if chat_type in ["group", "supergroup"]:
                print(f"👥 Group Name: {chat_title}")
            print()
            return str(chat_id)
        else:
            print("❌ Không tìm thấy chat ID")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_env(chat_id):
    """Update .env file with chat ID."""
    try:
        with open(ENV_FILE, 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('TELEGRAM_CHAT_ID='):
                lines[i] = f'TELEGRAM_CHAT_ID={chat_id}\n'
                updated = True
                break
        
        if updated:
            with open(ENV_FILE, 'w') as f:
                f.writelines(lines)
            print(f"✅ Updated .env with TELEGRAM_CHAT_ID={chat_id}")
            return True
        else:
            print("❌ TELEGRAM_CHAT_ID not found in .env")
            return False
            
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def send_test_message(chat_id):
    """Send test message to verify setup."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🧪 *Test Message*\n\nWiki Automation Bot setup thành công!\n\nDaemon service sẽ gửi:\n• Daily briefing (7:00 AM)\n• Sync status (11:00 AM & 4:00 PM)\n• Error alerts",
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Test message sent to Telegram")
        return True
    except Exception as e:
        print(f"❌ Failed to send test message: {e}")
        return False

def main():
    print("🔍 Getting Telegram Chat ID...")
    print()
    
    chat_id = get_chat_id()
    if not chat_id:
        sys.exit(1)
    
    print()
    print("📝 Updating .env...")
    if not update_env(chat_id):
        sys.exit(1)
    
    print()
    print("📤 Sending test message...")
    send_test_message(chat_id)
    
    print()
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("  1. Check Telegram for test message")
    print("  2. Start daemon: python daemon.py start")
    print("  3. Or install LaunchAgent: ./install_daemon.sh")

if __name__ == "__main__":
    main()
