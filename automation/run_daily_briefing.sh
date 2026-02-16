#!/bin/bash
cd /Users/nqcdan/dev/wiki/automation
source .venv/bin/activate
set -a && source .env && set +a
python daily_briefing_generator.py >> /Users/nqcdan/dev/wiki/automation/daily_briefing.log 2>&1
