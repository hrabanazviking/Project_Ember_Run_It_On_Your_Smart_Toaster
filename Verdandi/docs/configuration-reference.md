# 🔧 Configuration Reference

## Configuration File Location

Verðandi Heartbeat looks for configuration in this order:

1. `~/.hermes/state/heartbeat.yaml` (recommended)
2. `/etc/verdandi/heartbeat.yaml` (system-wide)
3. `./heartbeat.yaml` (current directory, for development)
4. Built-in defaults (see below)

## Full Configuration Reference

```yaml
# ═══════════════════════════════════════════════════
# VERÐANDI HEARTBEAT CONFIGURATION
# The Norn of Becoming — what is, is becoming
# ═══════════════════════════════════════════════════

# ─── Heartbeat Core ───────────────────────────────
heartbeat:
  interval_seconds: 60          # Seconds between pulses
  startup_delay_seconds: 10      # Delay before first pulse
  jitter_seconds: 5              # Random ± to interval (prevents herd)
  health_score_window: 100       # EMA window for health trending

# ─── Checks (Four Senses) ─────────────────────────
checks:
  eir:                           # Health: CPU, RAM, disk, temperature
    enabled: true
    circuit_breaker_threshold: 5     # Failures before circuit opens
    circuit_breaker_cooldown: 300    # Seconds before half-open probe
    thresholds:
      cpu_warning_percent: 80        # CPU usage % for WARNING
      cpu_critical_percent: 95       # CPU usage % for CRITICAL
      ram_warning_percent: 80        # RAM usage % for WARNING
      ram_critical_percent: 95       # RAM usage % for CRITICAL
      disk_warning_percent: 80       # Disk usage % for WARNING
      disk_critical_percent: 95      # Disk usage % for CRITICAL
      temp_warning_celsius: 70       # Temperature °C for WARNING
      temp_critical_celsius: 80      # Temperature °C for CRITICAL
    paths:                            # Override default paths
      temp_file: "/sys/class/thermal/thermal_zone0/temp"

  huginn:                       # Projects: git status
    enabled: true
    circuit_breaker_threshold: 3
    circuit_breaker_cooldown: 180
    paths:                            # Dirs to check (relative to HOME)
      - "Verdandi"
      - "Mimir"
      - "Huginn"
    threshold_days_stale: 7            # Days before CRITICAL

  mimir:                        # Memory: DB integrity and size
    enabled: true
    circuit_breaker_threshold: 5
    circuit_breaker_cooldown: 600
    thresholds:
      db_size_warning_mb: 100         # DB size MB for WARNING
      db_size_critical_mb: 500         # DB size MB for CRITICAL
    paths:
      mimir_db: "~/.mimir/mimir.db"
      kista_db: "~/.kista/vault.db"

  urdr:                         # Schedule: upcoming events
    enabled: true
    circuit_breaker_threshold: 3
    circuit_breaker_cooldown: 300
    look_ahead_hours: 48             # How far ahead to check
    paths:
      schedule_file: "~/.hermes/state/schedule.json"

# ─── Reactor (Check → Action Bridge) ─────────────
reactor:
  enabled: true
  dry_run: true                  # Set to false to actually execute actions
  default_cooldown_seconds: 300  # Minimum time between same action
  rules:
    - trigger: "health:cpu"
      severity: critical
      action: restart_services
      cooldown_seconds: 600

    - trigger: "memory:mimir_db"
      severity: critical
      action: auto_heal
      cooldown_seconds: 1800

    - trigger: "project:*"
      severity: warning
      action: notify
      cooldown_seconds: 3600

# ─── Nerve Hub Integration ───────────────────────
nerve:
  publish_pulses: true           # Send nerve impulses on each pulse
  socket_path: "~/.hermes/state/runa.sock"
  fallback_to_file: true         # Write to JSONL if socket unavailable

# ─── Logging ──────────────────────────────────────
logging:
  level: "INFO"                  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  file_max_bytes: 10485760       # 10 MB
  file_backup_count: 5
  also_log_to_stderr: true       # Also print to console
```

## Environment Variables

All configuration values can be overridden with environment variables:

```bash
# Path overrides
VERDANDI_STATE_DIR=~/.hermes/state
VERDANDI_LOG_DIR=~/.hermes/state/logs
VERDANDI_PID_DIR=~/.hermes/state/run
VERDANDI_SOCKET_PATH=~/.hermes/state/runa.sock
VERDANDI_DB_PATH=~/.hermes/state/heartbeat.db
VERDANDI_CONFIG_PATH=~/.hermes/state/heartbeat.yaml

# Quick overrides
VERDANDI_INTERVAL=30              # Override heartbeat interval
VERDANDI_LOG_LEVEL=DEBUG          # Override log level
```

## Default Paths (XDG-Compliant)

On first run, Verðandi creates these directories:

```
~/.hermes/
├── state/
│   ├── heartbeat.db          # State database
│   ├── heartbeat.yaml        # Configuration (if created)
│   ├── nerve_feed.jsonl      # Nerve impulse log
│   ├── runa.sock             # Nerve hub socket
│   ├── run/
│   │   └── verdandi-heartbeat.pid
│   └── logs/
│       └── verdandi-heartbeat.log
└── config/
    └── heartbeat.yaml        # Alternative config location
```