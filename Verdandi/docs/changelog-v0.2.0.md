# 📋 Verðandi v0.2.0 Changelog

## [0.2.0] — 2026-05-11 — "The Spirit" (Andi)

### Added

#### Core
- **Heartbeat Daemon** (`HeartbeatDaemon`): Main loop with state machine
  - States: INITIALIZING, RUNNING, DEGRADED, CRITICAL, RECOVERING, SHUTTING_DOWN
  - Configurable pulse interval with jitter (prevents thundering herd)
  - POSIX signal handling (SIGTERM, SIGHUP, SIGUSR1, SIGUSR2)
  - PID file management for single-instance enforcement
  - Config reload on SIGHUP
  - State dump on SIGUSR2

- **Circuit Breaker** (`CircuitBreaker`): Fail-fast protection for checks/actions
  - Three states: CLOSED, OPEN, HALF_OPEN
  - Configurable failure threshold (default: 5)
  - Configurable cooldown period (default: 300s)
  - Per-check circuit breakers with individual settings
  - Statistics tracking (failures, successes, total calls)

- **Health Score** (`HealthScore`): Exponential Moving Average health trending
  - 0-100 score based on check severities (OK=100, WARNING=50, CRITICAL=0, UNKNOWN=75)
  - Trend detection: improving, stable, degrading
  - Stability metric (standard deviation)
  - Configurable window size (default: 100)

- **State Machine**: Automatic state transitions based on check results
  - INITIALIZING → RUNNING after first pulse
  - RUNNING → DEGRADED on any WARNING check
  - RUNNING → CRITICAL on any CRITICAL check
  - DEGRADED/CRITICAL → RECOVERING when checks improve
  - RECOVERING → RUNNING on sustained improvement

#### Checks (Four Senses)

- **Eir** (Health): CPU usage, RAM, disk space, Pi thermal throttling
- **Huginn** (Projects): Git status, dirty repos, unpushed branches
- **Mímir** (Memory): DB integrity, size, row counts (mimir.db, heartbeat.db, kista.db)
- **Urðr** (Schedule): Upcoming events, deadlines

#### Actions (Four Acts)

- **Mjölnir** (Restart): Restart crashed services, rebuild indexes, clean caches
- **Gungnir** (Escalate): Send notifications via nerve hub for critical issues
- **Bifrǫst** (Bridge): Forward status to external services
- **Eir** (Heal): Auto-repair corrupted databases, truncate malformed JSONL, ensure directories

#### Infrastructure

- **Reactor**: Check → action bridge with rule-based triggering, cooldowns, and dry-run mode
- **Nerve Hub Integration**: Unix domain socket impulses (with file fallback)
- **Configuration**: YAML config with dot-notation access and environment variable overrides
- **Paths**: XDG-compliant, file-location-agnostic path resolution
- **CLI**: `verdandi-heartbeat` and `hjartsláttur` entry points
  - `pulse --once` / `pulse --loop`
  - `react --dry-run`
  - `paths` / `config`
- **Systemd**: Service file and install/uninstall scripts
- **MANIFEST.in**: Include config and service files in distribution

### Bug Fixes

- **SQLite context managers**: All `sqlite3.connect()` calls now use `with` statements to prevent connection leaks on exceptions (core.py, mimir.py, eir_action.py)
- **Circuit breaker prevents cascading failures**: Checks that fail repeatedly are temporarily skipped
- **Health score tracking**: EMA-based trending prevents false positives from single bad pulses

### Testing

- **489 tests passing**: 264 core + 149 checks + 75 actions + 49 integration
- Full coverage of circuit breaker states (closed, open, half_open → closed)
- Health score trending tests (improving, stable, degrading)
- SQLite context manager tests

### Documentation

- 15+ new guide documents in `docs/`
- Massively expanded README with architecture, senses, acts, configuration
- Heimdall watchman documentation
- Circuit breaker pattern guide
- Health score explanation
- Quick start guide
- Integration patterns for AI agents
- Nerve hub protocol specification
- Raspberry Pi optimization guide
- Performance and resource guide
- Troubleshooting guide
- Contributing guide
- Norse mythology mapping

### Breaking Changes

- None. v0.2.0 is fully backward compatible with v0.1.0 (nervous system only).

### Migration from v0.1.0

No migration needed. The heartbeat module coexists with the nervous system. Existing nerve hub subscribers will automatically receive `heartbeat_pulse` and `heartbeat_state_change` event types.