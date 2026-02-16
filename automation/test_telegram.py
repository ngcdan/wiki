#!/usr/bin/env python3
"""Test Telegram Bot Connection"""

import os
import sys
import requests

# Load env
env_file = "/Users/nqcdan/dev/wiki/automation/.env"
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            if v:
                os.environ[k] = v

token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print('🔧 Testing Telegram Bot...')
print(f'Bot Token: {token[:20]}...')
print(f'Chat ID: {chat_id}')
print()

# Send test message
url = f'https://api.telegram.org/bot{token}/sendMessage'
payload = {
    'chat_id': chat_id,
    'text': '🧪 *Test Message*\n\nWiki Automation Bot configured!\n\n✅ Bot token: OK\n✅ Chat ID: OK\n\nReady to start daemon.',
    'parse_mode': 'Markdown'
}

try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
        print('✅ Test message sent successfully!')
        print('📱 Check Telegram for the message')
        sys.exit(0)
    else:
        print(f'❌ Failed: {response.status_code}')
        print(response.text)
        sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
