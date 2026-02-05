#!/usr/bin/env bash
set -euo pipefail

# Morning routine (manual trigger)
# - Open Anki
# - Open YouTube “study with me” in Chrome
# - Set ONLY the YouTube player volume to 10% (does NOT change system volume)
#
# Usage:
#   ./automation/morning_routine.sh

YOUTUBE_URL="https://www.youtube.com/watch?v=SQ93oOmVxHs&t=61s"

# 1) Open Anki
open -a "Anki" || true

# 2) Open YouTube in Chrome and set in-player volume to 10%
/usr/bin/osascript <<OSA
set theURL to "${YOUTUBE_URL}"

tell application "Google Chrome"
	activate
	if (count of windows) = 0 then
		make new window
	end if
	set theTab to make new tab at end of tabs of front window
	set URL of theTab to theURL
end tell

# Wait a bit for page/video to load
repeat 25 times
	delay 0.4
	try
		tell application "Google Chrome"
			tell active tab of front window
				set readyState to execute javascript "document.readyState"
			end tell
		end tell
		if readyState is "interactive" or readyState is "complete" then exit repeat
	end try
end repeat

try
	tell application "Google Chrome"
		tell active tab of front window
			-- Set only HTML5 video volume; keep system volume unchanged.
			execute javascript "(function(){ const v=document.querySelector('video'); if(v){ v.volume=0.10; v.play().catch(()=>{});} })();"
		end tell
	end tell
end try
OSA

echo "OK: opened Anki + YouTube study-with-me (player volume=10%)"
