# Event Bus Protocol Specification
## VERÐANDI Nerve Hub Wire Protocol

---

## 1. Event Format

```json
{
  "timestamp": 1715347200.123,
  "event_type": "verdandi_pulse",
  "source": "verdandi_heartbeat",
  "event_id": "v0.2-1715347200-abc123",
  "data": {
    "pulse_number": 42,
    "mode": "SPROUT",
    "freyja": { ... },
    "odin": { ... },
    "thor": { ... }
  },
  "metadata": {
    "priority": "normal",
    "persistence": "feed",
    "ttl": 86400
  }
}
```

## 2. Event Types

| Type | Source | Description |
|------|--------|-------------|
| `verdandi_pulse` | heartbeat | Complete awareness pulse |
| `freyja_pulse` | freyja_heartbeat | Creative/emergent check |
| `odin_pulse` | odin_heartbeat | Wisdom/memory check |
| `thor_pulse` | thor_heartbeat | Protection/defense check |
| `orlog_laid` | orlog_layer | Commitment scheduled |
| `orlog_delivered` | orlog_layer | Commitment delivered |
| `threat_detected` | heimdall | Threat alert |
| `rune_discovered` | yggdrasil_hang | New pattern found |
| `self_healing` | thor | Self-correction applied |

## 3. Socket Protocol

The Unix domain socket uses a simple newline-delimited JSON protocol:
- Each event is a single JSON object followed by `\n`
- Subscribers receive events in real-time
- The ring buffer holds the last 256 events for quick retrieval

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
