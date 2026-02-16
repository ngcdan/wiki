#!/bin/bash
# LaunchAgent installer for Wiki Automation Daemon

PLIST_FILE=~/Library/LaunchAgents/com.wiki.automation.daemon.plist
PYTHON_PATH=/Users/nqcdan/dev/wiki/automation/.venv/bin/python
DAEMON_PATH=/Users/nqcdan/dev/wiki/automation/daemon.py
WORK_DIR=/Users/nqcdan/dev/wiki/automation

echo "📦 Installing Wiki Automation Daemon as LaunchAgent..."

# Create plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wiki.automation.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$DAEMON_PATH</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$WORK_DIR/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>$WORK_DIR/daemon.err</string>
    <key>WorkingDirectory</key>
    <string>$WORK_DIR</string>
</dict>
</plist>
EOF

echo "✅ Created LaunchAgent plist: $PLIST_FILE"

# Load LaunchAgent
launchctl load "$PLIST_FILE"

echo "✅ LaunchAgent loaded"
echo ""
echo "Daemon will:"
echo "  - Start automatically on login"
echo "  - Restart if crashed"
echo "  - Run scheduled tasks (7AM, 11AM, 4PM)"
echo "  - Send notifications via Telegram"
echo ""
echo "Commands:"
echo "  Check status: launchctl list | grep wiki"
echo "  View logs: tail -f $WORK_DIR/daemon.log"
echo "  Unload: launchctl unload $PLIST_FILE"
