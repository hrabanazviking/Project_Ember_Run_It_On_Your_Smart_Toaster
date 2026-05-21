# 🛠️ Troubleshooting Guide

## Common Issues

### "Another instance is already running"

**Symptom:** `verdandi-heartbeat pulse --loop` exits immediately with this message.

**Cause:** A stale PID file from a previous run that didn't clean up (e.g., killed with `kill -9`).

**Fix:**
```bash
# Check if the process is actually running
cat ~/.hermes/state/run/verdandi-heartbeat.pid
ps -p $(cat ~/.hermes/state/run/verdandi-heartbeat.pid)

# If the process doesn't exist, remove the stale PID file
rm ~/.hermes/state/run/verdandi-heartbeat.pid

# Restart
systemctl --user restart verdandi-heartbeat
```

### "Nerve hub socket not found"

**Symptom:** Warning in logs: "Nerve hub socket not found, falling back to file"

**Cause:** The Hermes nerve hub isn't running, or the socket path is wrong.

**Fix:**
```bash
# Check if the nerve hub is running
ls -la ~/.hermes/state/runa.sock

# Start the nerve hub (if using Hermes)
hermes nerve &

# Or check your config
verdandi-heartbeat config | grep socket
```

**Note:** This is normal during development/testing. The daemon falls back to writing impulses to `nerve_feed.jsonl`.

### All checks returning UNKNOWN

**Symptom:** State stuck in DEGRADED, all checks show UNKNOWN severity.

**Cause:** The circuit breaker has opened for all checks due to repeated failures, or the underlying resources don't exist.

**Fix:**
```bash
# Check the state database
sqlite3 ~/.hermes/state/heartbeat.db "SELECT key, value FROM heartbeat_state"

# Run a single pulse with verbose logging
VERDANDI_LOG_LEVEL=DEBUG verdandi-heartbeat pulse --once

# Check the log file
tail -50 ~/.hermes/state/logs/verdandi-heartbeat.log
```

### State stuck in DEGRADED

**Symptom:** State never transitions back to RUNNING even though checks are OK.

**Cause:** The state machine requires multiple consecutive OK pulses before transitioning from DEGRADED to RECOVERING, then from RECOVERING to RUNNING.

**Fix:** This is by design. Wait for 2-3 pulse intervals. If it stays stuck:
```bash
# Force a state dump
kill -USR2 $(cat ~/.herpes/state/run/verdandi-heartbeat.pid)
cat ~/.hermes/state/verdandi_state_dump.json
```

### SQLite database locked

**Symptom:** "database is locked" errors in logs.

**Cause:** Another process is reading the database while Verðandi is writing to it.

**Fix:**
```bash
# Close any SQLite clients connected to the database
# Or wait briefly (SQLite has a built-in timeout)

# Check if the database is accessible
sqlite3 ~/.hermes/state/heartbeat.db "PRAGMA integrity_check"
```

### Configuration not loading

**Symptom:** Changes to `heartbeat.yaml` aren't taking effect.

**Fix:**
```bash
# Send SIGHUP to reload config
kill -HUP $(cat ~/.hermes/state/run/verdandi-heartbeat.pid)

# Or restart the service
systemctl --user restart verdandi-heartbeat

# Verify config is being read
verdandi-heartbeat config
```

### High CPU usage

**Symptom:** Verðandi is using more CPU than expected.

**Cause:** Pulse interval too short, or a check is doing expensive operations.

**Fix:**
```yaml
# In heartbeat.yaml
heartbeat:
  interval_seconds: 60    # Increase if needed
  jitter_seconds: 5        # Add jitter to spread load
```

```bash
# Check which check is slow
VERDANDI_LOG_LEVEL=DEBUG verdandi-heartbeat pulse --once 2>&1 | grep "ms)"
```

### Disk filling up with logs

**Symptom:** `/var/log/` or `~/.hermes/state/logs/` filling up.

**Fix:** The log handler uses rotating files with size limits. Adjust in config:
```yaml
logging:
  file_max_bytes: 10485760     # 10 MB per file
  file_backup_count: 5        # Keep 5 files max
```

The daemon also auto-prunes `pulse_history` to the last 1000 entries.

### Circuit breaker keeps opening

**Symptom:** Checks showing "circuit breaker OPEN" even though the underlying resource is fine.

**Cause:** The check was failing repeatedly but the underlying issue has been resolved.

**Fix:** Circuit breakers reset on success. If the check now returns OK, the breaker will close after one successful probe. If stuck:
```bash
# Restart the daemon (resets all circuit breakers)
systemctl --user restart verdandi-heartbeat

# Or adjust thresholds
# In heartbeat.yaml
checks:
  eir:
    circuit_breaker_threshold: 10  # More tolerant
    circuit_breaker_cooldown: 60    # Shorter cooldown
```

### Pi thermal throttling

**Symptom:** Eir check consistently reports Pi thermal throttle.

**Fix:**
```bash
# Check current temperature
cat /sys/class/thermal/thermal_zone0/temp

# If consistently above 70°C:
# 1. Improve ventilation
# 2. Add a heatsink
# 3. Adjust thresholds
# In heartbeat.yaml
checks:
  eir:
    thresholds:
      temp_warning_celsius: 75     # Higher threshold for Pi
      temp_critical_celsius: 85
```