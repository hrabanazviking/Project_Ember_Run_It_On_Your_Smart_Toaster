# 🍓 Raspberry Pi Optimization Guide

## Overview

Verðandi Heartbeat was born on a Raspberry Pi and is optimized for its constraints. A Pi has limited CPU, RAM (4GB on Pi 4/5), and especially storage I/O. Here's how to make it run efficiently on Pi hardware.

## Resource Usage

Typical Pi resource consumption during a 60-second pulse cycle:

| Resource | Usage | Notes |
|----------|-------|-------|
| CPU | ~0.1-0.5% per pulse | Most time is sleeping |
| RAM | ~15-25 MB | Python process + SQLite |
| Disk I/O | ~1-5 KB/pulse | State DB write + nerve impulse |
| Storage | ~5 MB total | DB grows ~1 KB/day |

## Pi-Specific Optimizations

### 1. Thermal Monitoring

The Eir check reads `/sys/class/thermal/thermal_zone0/temp` for CPU temperature:

```yaml
checks:
  eir:
    thresholds:
      temp_warning_celsius: 70    # Pi throttles at ~80°C
      temp_critical_celsius: 80   # Pi hard-throttles at ~85°C
```

### 2. SD Card Protection

Minimize writes to extend SD card life:
```yaml
heartbeat:
  interval_seconds: 120   # Less frequent = fewer DB writes
  jitter_seconds: 10      # Spread writes across time

logging:
  file_max_bytes: 5242880   # 5 MB (smaller than default)
  file_backup_count: 2      # Fewer log files
```

### 3. Memory Conservation

Python on a Pi uses more RAM than you'd expect. Limit the health score window:
```yaml
heartbeat:
  health_score_window: 50    # Default 100, halve for Pi
```

### 4. Check Frequency

Run expensive checks less frequently:
- **Eir** (health): Every pulse (lightweight, just reads /proc and /sys)
- **Huginn** (projects): Every pulse (git operations are fast on local SSD)
- **Mímir** (memory): Every pulse (single DB query)
- **Urðr** (schedule): Every pulse (single file read)

### 5. Circuit Breakers on Pi

More aggressive circuit breakers for Pi:
```yaml
checks:
  mimir:
    circuit_breaker_threshold: 3   # Open after 3 failures (Pi is slower)
    circuit_breaker_cooldown: 120  # 2 minute cooldown (faster recovery than default)
```

## Systemd Service for Pi

The default service file is already optimized for Pi:

```ini
[Unit]
Description=Verðandi Heartbeat — The Norn of Becoming
After=network.target

[Service]
Type=simple
ExecStart=/home/pi/.local/bin/verdandi-heartbeat pulse --loop
Restart=always
RestartSec=10
Environment=VERDANDI_STATE_DIR=/home/pi/.hermes/state
Environment=VERDANDI_LOG_LEVEL=INFO

# Pi-specific limits
MemoryMax=64M
CPUQuota=5%

[Install]
WantedBy=default.target
```

## Monitoring Pi Health

```bash
# Quick health check
verdandi-heartbeat pulse --once

# Watch temperature trend
grep "health:cpu_temp" ~/.hermes/state/logs/verdandi-heartbeat.log | tail -20

# Check disk space (important on Pi with small SD cards)
df -h ~/.hermes/state/

# Monitor memory
free -h
ps aux | grep verdandi
```

## Headless Pi Setup

For Pi running headless (no display):

```bash
# Install as user service (no sudo needed)
bash scripts/install_heartbeat.sh

# Enable lingering (so service runs even without login)
loginctl enable-linger pi

# Check status
systemctl --user status verdandi-heartbeat
journalctl --user -u verdandi-heartbeat -f
```

## Pi Zero W Specific

If running on a Pi Zero W (512MB RAM):
```yaml
heartbeat:
  interval_seconds: 300   # 5 minute intervals
  health_score_window: 20 # Very small window
logging:
  file_max_bytes: 1048576  # 1 MB
  file_backup_count: 1
```

And reduce the Python overhead:
```bash
# Use pip's --no-compile flag
pip install --no-compile -e .
```