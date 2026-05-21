# 🫀 Verðandi Heartbeat — Quick Start Guide

## What Is It?

Verðandi Heartbeat (Hjartsláttur) is a self-awareness daemon for AI systems. It takes its own pulse — monitoring health, projects, memory, and schedule — and reacts to what it finds. Think of it as a digital nervous system that feels pain and heals itself.

## Installation (5 Minutes)

### Step 1: Install the Package

```bash
# Clone the repository
git clone https://github.com/hrabanazviking/Verdandi.git
cd Verdandi

# Install with pip (creates both CLI commands)
pip install -e .
```

This creates two CLI commands:
- `verdandi-heartbeat` — the official command name
- `hjartsláttur` — the Norse mythic name (alias)

### Step 2: Verify Installation

```bash
# Check the version
verdandi-heartbeat --version

# Run a single pulse (test mode)
verdandi-heartbeat pulse --once

# See what paths the daemon uses
verdandi-heartbeat paths
```

### Step 3: Install as a systemd Service (Linux/Pi)

```bash
# Use the provided install script
sudo bash scripts/install_heartbeat.sh
```

This will:
- Create the `~/.hermes/state/` directory structure
- Install the systemd service file
- Enable and start the daemon

### Step 4: Check It's Running

```bash
# Check systemd status
systemctl --user status verdandi-heartbeat

# Watch the log
tail -f ~/.hermes/state/logs/verdandi-heartbeat.log

# View the state database
sqlite3 ~/.hermes/state/heartbeat.db "SELECT * FROM heartbeat_state"

# Read the nerve feed
tail ~/.hermes/state/nerve_feed.jsonl
```

## Using with Hermes Agent

Verðandi Heartbeat integrates directly with the Hermes Agent nerve hub:

1. **Install Hermes Agent** (if not already installed):
   ```bash
   pip install hermes-agent
   ```

2. **The nerve hub socket** is at `~/.hermes/state/runa.sock` by default.

3. **Hermes subscribes** to nerve impulses automatically when running. You'll see health events in your sessions:
   ```python
   # In your Hermes session, heartbeat events appear as nerve impulses
   # Type: heartbeat_pulse, heartbeat_state_change
   ```

4. **Custom configuration** at `~/.hermes/state/heartbeat.yaml`:
   ```yaml
   heartbeat:
     interval_seconds: 60
     startup_delay_seconds: 10
     health_score_window: 100
   
   checks:
     eir: true       # Health: CPU, RAM, disk, Pi throttle
     huginn: true     # Projects: git status, remote tracking
     mimir: true     # Memory: DB integrity, size, row counts
     urdr: true      # Schedule: upcoming events, deadlines
   
   reactor:
     enabled: true
     dry_run: true    # Set to false to actually execute actions
   
   nerve:
     publish_pulses: true
     socket_path: ~/.hermes/state/runa.sock
     fallback_to_file: true
   ```

## Using with Other AI Agents

Verðandi Heartbeat is agent-agnostic. Any system that can read from a Unix domain socket or a JSONL file can consume nerve impulses:

### Reading from Socket (Python)

```python
import socket, json

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/home/youruser/.hermes/state/runa.sock")

while True:
    data = sock.recv(4096)
    if data:
        for line in data.decode().strip().split('\n'):
            event = json.loads(line)
            print(f"Event: {event['event_type']}")
            # Process: event['checks'], event['health_score'], etc.
```

### Reading from JSONL File

```python
import json
from pathlib import Path

feed = Path.home() / ".hermes/state/nerve_feed.jsonl"
with open(feed) as f:
    for line in f:
        event = json.loads(line)
        print(f"{event['timestamp']}: {event['event_type']}")
```

## The Four Senses

| Sense | Name | What It Checks |
|-------|------|----------------|
| 🏥 Health | Eir | CPU usage, RAM, disk space, Pi thermal throttle |
| 📂 Projects | Huginn | Git status, branch tracking, dirty repos |
| 🧠 Memory | Mímir | DB integrity, size, row counts, Kista vault |
| 📅 Schedule | Urðr | Upcoming events, deadlines, calendar |

## The Four Acts

| Act | Name | What It Does |
|-----|------|-------------|
| 🔨 Repair | Mjölnir | Restart services, rebuild indexes, clean caches |
| 🎯 Escalate | Gungnir | Send notifications when issues aren't self-healing |
| 🌈 Bridge | Bifrǫst | Forward status to external services (webhooks) |
| 💚 Heal | Eir | Repair corrupted DBs, truncate malformed logs, restore configs |

## Common Operations

```bash
# Run a single pulse and exit
verdandi-heartbeat pulse --once

# Run in daemon mode (foreground)
verdandi-heartbeat pulse --loop

# Run the reactor (dry-run) to see what actions WOULD fire
verdandi-heartbeat react --dry-run

# Show all configured paths
verdandi-heartbeat paths

# Show current configuration
verdandi-heartbeat config

# Stop the service
systemctl --user stop verdandi-heartbeat

# Restart after config changes
systemctl --user restart verdandi-heartbeat
```

## Troubleshooting

### "Another instance is already running"
```bash
# Check if the PID file is stale
cat ~/.hermes/state/run/verdandi-heartbeat.pid
# If the process doesn't exist, remove the stale PID
rm ~/.hermes/state/run/verdandi-heartbeat.pid
```

### "Nerve hub socket not found"
The heartbeat falls back to writing to `nerve_feed.jsonl` if the nerve hub isn't running. This is normal for testing. For full integration, start the Hermes nerve hub first.

### Checks returning UNKNOWN
This usually means the check couldn't find the resource (e.g., Mímir DB doesn't exist yet). The circuit breaker will handle repeated UNKNOWNs by skipping the check after the threshold is reached.

## Next Steps

- Read [ARCHITECTURE.md](architecture.md) for the full system design
- Read [circuit-breaker-pattern.md](circuit-breaker-pattern.md) to understand failure protection
- Read [health-score.md](health-score.md) to understand health trending
- Read [heimdall-watchman.md](heimdall-watchman.md) to understand the awareness layer