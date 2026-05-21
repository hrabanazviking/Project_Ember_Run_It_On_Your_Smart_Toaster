# 🔌 Integration Guide — Connecting Verðandi to Your Systems

## Overview

Verðandi Heartbeat is designed to integrate with any system that can read from a Unix domain socket or a JSONL file. This guide covers integration patterns for AI agents, monitoring systems, and custom applications.

## Nerve Impulse Format

All nerve impulses are JSON objects terminated by newlines:

```json
{
  "event_type": "heartbeat_pulse",
  "pulse_count": 42,
  "state": "running",
  "health_score": 87.5,
  "health_trend": "stable",
  "checks": {
    "eir": {"severity": "ok", "message": "All health checks OK"},
    "huginn": {"severity": "ok", "message": "3 projects, 0 dirty"},
    "mimir": {"severity": "ok", "message": "Mímir DB OK (1234 rows, 2.1MB)"},
    "urdr": {"severity": "ok", "message": "2 events in next 48h"}
  }
}
```

### State Change Events

```json
{
  "event_type": "heartbeat_state_change",
  "old_state": "running",
  "new_state": "degraded",
  "pulse_count": 42
}
```

## Integration Pattern 1: Hermes Agent (Native)

The native integration. Hermes subscribes to the nerve hub and receives impulses automatically:

1. Start the Hermes nerve hub: `hermes nerve`
2. Start Verðandi Heartbeat: `systemctl --user start verdandi-heartbeat`
3. In your Hermes session, nerve events appear as context

The nerve hub socket at `~/.hermes/state/runa.sock` handles the communication.

## Integration Pattern 2: Python Script

```python
#!/usr/bin/env python3
"""Subscribe to Verðandi nerve impulses via socket."""
import socket
import json
import sys

SOCKET_PATH = "~/.hermes/state/runa.sock"

def listen():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    print(f"Connected to {SOCKET_PATH}", file=sys.stderr)
    
    buffer = ""
    while True:
        data = sock.recv(4096)
        if not data:
            break
        buffer += data.decode()
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.strip():
                event = json.loads(line)
                handle_event(event)

def handle_event(event):
    etype = event.get("event_type", "unknown")
    if etype == "heartbeat_pulse":
        score = event.get("health_score", "?")
        trend = event.get("health_trend", "?")
        state = event.get("state", "?")
        print(f"🫀 Pulse #{event['pulse_count']}: state={state}, health={score}, trend={trend}")
        
        # React to critical states
        if state in ("critical", "degraded"):
            for name, check in event.get("checks", {}).items():
                if check["severity"] in ("critical", "warning"):
                    print(f"  ⚠️ {name}: {check['severity']} — {check['message']}")
    
    elif etype == "heartbeat_state_change":
        print(f"🔄 State: {event['old_state']} → {event['new_state']}")

if __name__ == "__main__":
    listen()
```

## Integration Pattern 3: JSONL Log File

When the nerve hub socket is unavailable, Verðandi writes to `~/.hermes/state/nerve_feed.jsonl`:

```bash
# Watch in real-time
tail -f ~/.hermes/state/nerve_feed.jsonl | jq .

# Filter for events
grep "state_change" ~/.hermes/state/nerve_feed.jsonl | jq .

# Get health score history
grep "heartbeat_pulse" ~/.hermes/state/nerve_feed.jsonl | jq '.health_score'
```

## Integration Pattern 4: Prometheus Metrics (Planned)

Future versions will expose Prometheus-compatible metrics:

```python
# Planned: expose health_score, check results, circuit breaker stats
# via HTTP endpoint for Prometheus scraping
```

## Integration Pattern 5: Webhook Notifications

Use the Bifrǫst action to forward state changes to external systems:

```yaml
# heartbeat.yaml
reactor:
  rules:
    - trigger: "*"
      severity: critical
      action: notify_webhook
      cooldown_seconds: 300
      config:
        url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        method: POST
        headers:
          Content-Type: "application/json"
        body_template: |
          {
            "text": "🫀 Verðandi Alert: {{ trigger }} is {{ severity }}",
            "details": "{{ message }}"
          }
```

## Integration Pattern 6: Home Automation (Home Assistant)

```yaml
# In Home Assistant configuration.yaml
sensor:
  - platform: rest
    name: "Verdandi Health Score"
    resource: "http://pi:8123/api/verdandi/health"
    value_template: "{{ value_json.health_score }}"
    scan_interval: 60
    
  - platform: rest
    name: "Verdandi State"
    resource: "http://pi:8123/api/verdandi/state"
    value_template: "{{ value_json.state }}"
```

## Integration Pattern 7: Cronic Regular Checks

For scheduled checks without the daemon:

```bash
# Add to crontab for single pulse every 5 minutes
*/5 * * * * /usr/local/bin/verdandi-heartbeat pulse --once >> /var/log/verdandi/cron.log 2>&1
```

## Event Types Reference

| Event Type | When | Key Fields |
|------------|------|------------|
| `heartbeat_pulse` | Every pulse interval | state, health_score, health_trend, checks |
| `heartbeat_state_change` | State transition | old_state, new_state, pulse_count |
| `check_result` | Individual check result | check_name, severity, message, details |
| `action_executed` | Action fired by reactor | action_name, severity, targets |

## Best Practices

1. **Start the nerve hub first** — Verðandi falls back to file if the socket isn't available, but socket is more efficient
2. **Use circuit breakers** — Don't disable them; they protect against cascading failures
3. **Monitor health score trends** — A degrading trend is more informative than a single bad pulse
4. **Set appropriate thresholds** — Calibrate for your hardware (Pi vs workstation)
5. **Use dry-run mode first** — Set `reactor.dry_run: true` until you've verified the system behaves correctly