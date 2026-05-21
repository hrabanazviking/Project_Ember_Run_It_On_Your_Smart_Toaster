# 📊 Monitoring and Observability

## Health Score Dashboard

```bash
# Get current health
verdandi-heartbeat pulse --once

# Watch health score over time
watch -n 60 'tail -1 ~/.hermes/state/nerve_feed.jsonl | jq "{state, health_score, health_trend}"'

# Get circuit breaker stats
sqlite3 ~/.hermes/state/heartbeat.db "SELECT key, value FROM heartbeat_state WHERE key LIKE '%circuit%'"
```

## Logging

All logs go to `~/.hermes/state/logs/verdandi-heartbeat.log` with rotation:

```bash
# Follow logs in real-time
tail -f ~/.hermes/state/logs/verdandi-heartbeat.log

# Search for errors
grep "ERROR\|CRITICAL" ~/.hermes/state/logs/verdandi-heartbeat.log

# Search for state changes
grep "state_change" ~/.hermes/state/logs/verdandi-heartbeat.log

# Search for actions
grep "action_executed" ~/.hermes/state/logs/verdandi-heartbeat.log
```

## State Database Queries

```bash
# Current state
sqlite3 ~/.hermes/state/heartbeat.db "SELECT * FROM heartbeat_state"

# Recent pulse history
sqlite3 ~/.hermes/state/heartbeat.db "SELECT * FROM pulse_history ORDER BY id DESC LIMIT 10"

# Health score progression
sqlite3 ~/.hermes/state/heartbeat.db "SELECT id, json_extract(data, '$.health_score') FROM pulse_history ORDER BY id DESC LIMIT 20"

# Circuit breaker states
sqlite3 ~/.hermes/state/heartbeat.db "SELECT key, value FROM heartbeat_state WHERE key LIKE '%circuit%'"
```

## Grafana Integration (Planned)

Future versions will expose Prometheus-compatible metrics for Grafana dashboards:

```yaml
# Planned: heartbeat.yaml
metrics:
  enabled: true
  port: 9101
  prefix: "verdandi_"
```

Expected metrics:
- `verdandi_health_score` (gauge, 0-100)
- `verdandi_pulse_count` (counter)
- `verdandi_check_severity{check="eir"}` (gauge, 0-3)
- `verdandi_circuit_breaker_state{check="eir"}` (gauge, 0=closed, 1=open, 2=half_open)
- `verdandi_state` (gauge, 0-5 mapping to state enum)