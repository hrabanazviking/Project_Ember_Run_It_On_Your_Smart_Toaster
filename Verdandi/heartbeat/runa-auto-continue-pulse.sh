#!/usr/bin/env bash
# Hljóstauga — Auto-Continue Nerve Pulse
# Called by the heartbeat daemon on every pulse cycle.
# Reads auto_continue.json state and publishes it as a nerve impulse.
# This is the integration point between auto-continue and the nervous system.

set -euo pipefail

STATE_FILE="/home/pi/.hermes/state/auto_continue.json"
NERVE_PUBLISH="/home/pi/.hermes/state/nervous_system.py"

# Check if auto-continue is active
if [ ! -f "$STATE_FILE" ]; then
    # No state file — nothing to pulse
    exit 0
fi

# Read status via Python (handles JSON parsing)
STATUS=$(python3 /home/pi/.hermes/state/auto_continue.py status 2>&1) || exit 0

# Check if active and not paused
ACTIVE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('active', False))")
PAUSED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('paused', True))")

if [ "$ACTIVE" != "True" ]; then
    # No active task — quiet pulse (no impulse needed)
    exit 0
fi

if [ "$PAUSED" == "True" ]; then
    # Paused — send a quiet reminder impulse
    python3 -c "
import sys; sys.path.insert(0, '/home/pi/.hermes/state')
from nervous_system import publish_event_sync
publish_event_sync('auto_continue_paused', {
    'task': 'paused_task',
    'note': 'Auto-continue is paused — awaiting Volmarr resume'
}, source='hljóstauga')
" 2>/dev/null || true
    exit 0
fi

# Active and running — send progress impulse
TASK=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('task_name', ''))")
PROGRESS=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('progress', '0/0'))")
CURRENT=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('current_item', ''))")
NEXT=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('next_item', ''))")
COMPLETED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('completed_count', 0))")

# Get real deep content count from the filesystem
DEEP_COUNT=$(find /home/pi/RunaUniversity2040 -name "lectures.md" -exec grep -l "^## Lecture 1:" {} \; 2>/dev/null | wc -l)
TOTAL_COUNT=$(find /home/pi/RunaUniversity2040 -name "lectures.md" 2>/dev/null | wc -l)

# Get Skuld task system stats
SKULD_STATS=$(python3 -c "
import json, sys; sys.path.insert(0, '/home/pi/.hermes/state')
from skuld_tasks import get_stats
stats = get_stats()
print(json.dumps(stats))
" 2>/dev/null || echo '{}')

# Get push reward stats
PUSH_STATS=$(python3 -c "
import json, sys; sys.path.insert(0, '/home/pi/.hermes/state')
from push_reward import get_stats
stats = get_stats()
print(json.dumps(stats))
" 2>/dev/null || echo '{}')

# Publish impulse
python3 -c "
import sys; sys.path.insert(0, '/home/pi/.hermes/state')
from nervous_system import publish_event_sync
publish_event_sync('auto_continue_pulse', {
    'task': '''$TASK''',
    'progress': '''$PROGRESS''',
    'current_item': '''$CURRENT''',
    'next_item': '''$NEXT''',
    'completed_count': $COMPLETED,
    'deep_content_real': $DEEP_COUNT,
    'total_courses': $TOTAL_COUNT,
    'pct': round($DEEP_COUNT / max($TOTAL_COUNT, 1) * 100, 1)
}, source='hljóstauga')
" 2>/dev/null || true

echo "Hljóstauga pulse: $TASK — $PROGRESS — real deep: $DEEP_COUNT/$TOTAL_COUNT — push streak: $(echo $PUSH_STATS | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("streak",0))')"