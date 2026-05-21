# 🤖 AI Agent Integration Patterns

## Overview

Verðandi Heartbeat is an AI awareness system — it gives AI agents the ability to feel their own system's pulse and react to changes. This document describes patterns for integrating with various AI agent frameworks.

## Pattern 1: Hermes Agent (Primary)

Hermes is the primary consumer of Verðandi nerve impulses. The integration is automatic:

```
Verðandi Heartbeat → nerve hub (runa.sock) → Hermes Agent
```

Hermes reads impulses and adds them to the conversation context when relevant:
- State changes (RUNNING → DEGRADED) are surfaced to the agent
- Health score trends influence the agent's decision-making
- Check results are available for the agent to query

### Using in Conversations

```python
# In a Hermes conversation, the agent can:
# 1. Check system health via the nerve feed
# 2. React to state changes automatically
# 3. Query the state database directly

# Example: Agent asks about system health
# Agent: "How is the system feeling?"
# → Nerve feed shows health_score: 87.5, trend: stable
```

## Pattern 2: LangChain/LangGraph Integration

```python
from langchain.tools import BaseTool
import json
import subprocess

class VerdandiHealthTool(BaseTool):
    name = "verdandi_health"
    description = "Check system health using Verðandi Heartbeat"
    
    def _run(self, query: str) -> str:
        result = subprocess.run(
            ["verdandi-heartbeat", "pulse", "--once"],
            capture_output=True, text=True
        )
        return result.stdout
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
```

## Pattern 3: REST API Wrapper

```python
from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI(title="Verðandi Heartbeat API")

@app.get("/health")
def get_health():
    """Current health score and check results."""
    db = Path.home() / ".hermes/state/heartbeat.db"
    # Read from state database
    import sqlite3
    with sqlite3.connect(str(db)) as conn:
        state = dict(conn.execute(
            "SELECT key, value FROM heartbeat_state"
        ).fetchall())
    return state

@app.get("/health/score")
def get_health_score():
    """Current health score only."""
    # Read from nerve feed
    feed = Path.home() / ".hermes/state/nerve_feed.jsonl"
    last_line = feed.read_text().strip().split("\n")[-1]
    event = json.loads(last_line)
    return {
        "score": event.get("health_score"),
        "trend": event.get("health_trend"),
    }
```

## Pattern 4: WebSocket Streaming

```python
import asyncio
import websockets
import json
import socket

async def stream_verdandi(websocket, path):
    """Stream Verðandi nerve impulses over WebSocket."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(str(Path.home() / ".hermes/state/runa.sock"))
    
    while True:
        data = sock.recv(4096)
        if data:
            for line in data.decode().strip().split("\n"):
                event = json.loads(line)
                await websocket.send(json.dumps(event))

# Start WebSocket server
start_server = websockets.serve(stream_verdandi, "localhost", 8765)
```

## Pattern 5: MQTT Bridge (IoT Integration)

```python
import paho.mqtt.client as mqtt
import json
from pathlib import Path

client = mqtt.Client("verdandi-heartbeat")

def on_connect(c, userdata, flags, rc):
    client.subscribe("verdandi/commands/#")

def on_message(c, userdata, msg):
    if msg.topic == "verdandi/commands/pulse":
        # Trigger a manual pulse
        import subprocess
        subprocess.run(["verdandi-heartbeat", "pulse", "--once"])

client.on_connect = on_connect
client.on_message = on_message

# Publish nerve impulses to MQTT
def publish_impulse(event):
    topic = f"verdandi/events/{event['event_type']}"
    client.publish(topic, json.dumps(event))

client.connect("localhost", 1883)
client.loop_start()
```

## Pattern 6: Home Assistant Integration

```yaml
# configuration.yaml
sensor:
  - platform: command
    name: "Verdandi Health Score"
    command: "cat /home/pi/.hermes/state/nerve_feed.jsonl | tail -1 | jq '.health_score'"
    value_template: "{{ value | float }}"
    scan_interval: 60
    
  - platform: command
    name: "Verdandi State"
    command: "cat /home/pi/.hermes/state/nerve_feed.jsonl | tail -1 | jq '.state'"
    value_template: "{{ value }}"
    scan_interval: 60

automation:
  - alias: "Verdandi Critical Alert"
    trigger:
      platform: state
      entity_id: sensor.verdandi_state
      to: "critical"
    action:
      service: notify.mobile_app_phone
      data:
        message: "🫀 System CRITICAL: Health score {{ states('sensor.verdandi_health_score') }}"
```

## Best Practices for Agent Integration

1. **Read from the nerve feed, not the DB** — the JSONL file is append-only and doesn't require SQLite locking
2. **Handle UNKNOWN severity gracefully** — it means a check couldn't run, not that something is wrong
3. **Respect circuit breaker state** — if a check is OPEN, don't pester the system
4. **Use health score trends** — a single score is a snapshot; a trend tells a story
5. **Subscribe to state changes** — don't poll every pulse; react to state transitions
6. **Keep your integration stateless** — let Verðandi be the source of truth