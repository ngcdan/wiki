#!/bin/bash
# Quick Start Script - Wiki Automation

echo "🚀 Wiki Automation - Quick Start"
echo "=================================="
echo ""

# Check if in correct directory
if [ ! -f "ai_classifier.py" ]; then
    echo "❌ Error: Run this from /Users/nqcdan/dev/wiki/automation"
    exit 1
fi

# Activate venv
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
    touch .venv/installed
fi

# Load env
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

set -a && source .env && set +a

echo ""
echo "✅ Environment ready!"
echo ""
echo "Choose action:"
echo "  1) Generate daily briefing"
echo "  2) Sync Issues (last 7 days)"
echo "  3) Start Daemon"
echo "  4) Stop Daemon"
echo "  5) Check Daemon Status"
echo "  6) Monitor Logs"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo "📊 Generating daily briefing..."
        python daily_briefing_generator.py
        ;;
    2)
        echo "🔄 Syncing Issues (7 days)..."
        python forgejo_issue_collector.py --days-back 7
        ;;
    3)
        echo "🚀 Starting Daemon..."
        python daemon.py start
        ;;
    4)
        echo "bw Stopping Daemon..."
        python daemon.py stop
        ;;
    5)
        echo "🔍 Checking Status..."
        python daemon.py status
        ;;
    6)
        echo "📋 Monitoring logs (Ctrl+C to exit)..."
        tail -f daemon.log collectors.log daily_briefing.log
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
