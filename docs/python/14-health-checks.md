# 14 — Health Checks: Liveness, Readiness, Startup

**Category:** Self-Healing & Supervision
**Runa relevance:** `runa doctor`, Eir monitoring, systemd readiness, adapter health
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Health checks are how a system answers three distinct questions: **am I alive?** (would a restart help?), **am I ready?** (should I receive traffic?), and **have I finished starting up?** (should the supervisor think I'm broken yet?). The three are different. A service can be alive but not ready (still loading models). A service can be ready but stuck after some hours (alive answer correct, ready answer wrong). Conflating them produces flapping restarts and silent service degradation.

Kubernetes formalised the three-probe distinction (liveness, readiness, startup); the patterns apply broadly. For Runa, health checks underlie `runa doctor` (the operator-facing diagnostic), Eir's autonomous monitoring, and systemd's restart decisions. The discipline pays off most when something is *not quite right* — the right kind of health check catches it; the wrong kind misses it or causes a thrash.

## 2. Technique / mechanism

**The three probe types:**

### Liveness — "would killing this help?"

A liveness probe answers: should the supervisor restart me? If liveness fails persistently, restart is the right action. If liveness succeeds, the process is making progress; don't restart.

- **What to check:** internal heartbeat counter, main loop iteration time, deadlock detector results.
- **What not to check:** downstream dependencies (those are readiness concerns).
- **Cadence:** every 10-30s typically.

```python
class LivenessCheck:
    def __init__(self):
        self.last_main_loop_iter = time.monotonic()
    
    def main_loop_beat(self):
        self.last_main_loop_iter = time.monotonic()
    
    def is_alive(self) -> bool:
        return (time.monotonic() - self.last_main_loop_iter) < 60.0
```

### Readiness — "should I receive traffic?"

A readiness probe answers: am I in a state to serve requests right now? If not, the load balancer / supervisor should not route to me, but a restart wouldn't necessarily help — I might be loading state, depending on a backend that's still warming up, etc.

- **What to check:** downstream dependencies available, caches warm, configuration loaded, model loaded, database connection healthy.
- **What not to check:** "could the process restart improve things." If restart helps, that's a liveness concern.
- **Cadence:** can be more frequent (every few seconds).

```python
class ReadinessCheck:
    def __init__(self, muninn, heimskringla):
        self.muninn = muninn
        self.heimskringla = heimskringla
    
    async def is_ready(self) -> ReadinessReport:
        checks = await asyncio.gather(
            self._check_muninn(),
            self._check_at_least_one_provider(),
            self._check_disk_space(),
            return_exceptions=True,
        )
        return ReadinessReport(
            ready=all(c is True for c in checks),
            details=dict(zip(["muninn", "providers", "disk"], checks)),
        )
```

### Startup — "have I finished starting?"

A startup probe answers: have I completed initialisation yet? It prevents the supervisor from declaring "this is unhealthy" during a slow startup that's *expected* to be slow.

- **What to check:** specific initialisation steps complete (models loaded, migrations run, indexes built).
- **Cadence:** can be infrequent during startup; replaced by liveness/readiness once startup completes.
- **Purpose:** lets startup take 60s while liveness allows only 10s of silence in steady state.

```python
class StartupCheck:
    def __init__(self):
        self.muninn_loaded = False
        self.skuld_recovered = False
        self.config_validated = False
        self.first_model_ready = False
    
    def is_startup_complete(self) -> bool:
        return all([
            self.muninn_loaded,
            self.skuld_recovered,
            self.config_validated,
            self.first_model_ready,
        ])
```

**HTTP health endpoints** (the common operational shape):

```python
from fastapi import FastAPI, Response, status

app = FastAPI()

@app.get("/health/live")
async def liveness():
    if liveness_check.is_alive():
        return {"status": "ok"}
    return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

@app.get("/health/ready")
async def readiness():
    report = await readiness_check.is_ready()
    if report.ready:
        return {"status": "ok", "details": report.details}
    return Response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=report.json(),
    )

@app.get("/health/startup")
async def startup():
    if startup_check.is_startup_complete():
        return {"status": "ok"}
    return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
```

systemd or Kubernetes (or a small companion process) polls these endpoints and acts.

**Composite health reports:**

```python
@dataclass
class HealthCheck:
    name: str
    status: Literal["pass", "warn", "fail"]
    last_run_at: datetime
    duration_ms: float
    detail: str | None = None

@dataclass
class HealthReport:
    overall: Literal["healthy", "degraded", "unhealthy"]
    checks: list[HealthCheck]
    
    def to_json(self) -> dict:
        return {
            "overall": self.overall,
            "checks": [asdict(c) for c in self.checks],
        }
```

A *composite* readiness check runs many individual checks and reports each separately. `degraded` (some checks fail, others pass) is a real category that requires graceful degradation ([[10-graceful-degradation]]) rather than restart.

**Self-instrumenting code:**

```python
class TrackedOperation:
    """Wrap operations to feed health checks automatically."""
    
    def __init__(self, name: str):
        self.name = name
        self.last_success = 0.0
        self.last_failure = 0.0
        self.recent_failures = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.last_success = time.monotonic()
            self.recent_failures = 0
        else:
            self.last_failure = time.monotonic()
            self.recent_failures += 1
        return False  # don't swallow
    
    def health(self) -> HealthCheck:
        # last_success within last minute = pass; failures = degraded; never = unknown
        ...
```

## 3. Key works / libraries

- **Kubernetes documentation** — kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/. The reference for the three-probe model.
- **systemd `Type=notify`** + `ReadyState`, `WatchdogSec` — the OS-level analogue.
- **Beyer et al.** *Site Reliability Engineering*, O'Reilly 2016 — chapters on monitoring and health checking.
- **`health-check` / `py-healthcheck`** — github.com/Kozea/py-healthcheck. Older Python helper.
- **`HealthCheck.Net`** style libraries — many ecosystems have them.
- **OpenTelemetry's `Status`** — semantic conventions for service health.
- **AWS Builders' Library:** "Implementing health checks."

## 4. Pitfalls and gotchas

- **Liveness checking downstream services.** If your liveness check fails when Anthropic is down, your process restarts pointlessly. Liveness must check *only* internal health.
- **Readiness too strict.** If readiness fails when *any* adapter is degraded, the service is taken out of rotation — but it could still serve most requests. Use composite readiness with graceful-degradation semantics.
- **Startup probe never finishing.** A bug in startup logic means the supervisor thinks startup is forever-in-progress. Eventually escalate.
- **Probe taking too long.** A 30-second probe runs into the 10-second timeout. Probes must be fast.
- **Probe with side effects.** A probe that *does work* (creates a session, writes a row) accumulates effects. Probes must be read-only.
- **Caching probe results too long.** "Was healthy 5 minutes ago" doesn't help when something just broke.
- **Caching probe results too short.** Hammering downstream on every probe.
- **No probe at all.** Service hangs; supervisor doesn't know.
- **Probe that's the only thing that runs.** A service whose health check works but main loop is dead. Probe must require *real work* somewhere.

## 5. Applicability to Runa

For **`runa doctor`** (the operator-facing diagnostic):

- Runs a comprehensive readiness check across all subsystems.
- Returns a HealthReport with per-subsystem detail.
- Includes: Muninn integrity, Skuld stuck-task count, adapter status per provider, breaker states, disk space, model availability.

For **Eir (continuous monitoring)**:

- Runs liveness checks every 10s for each supervised subsystem.
- Runs readiness checks every 30s.
- Records trends; sustained degradation triggers `Notified`.
- Restart decisions driven by liveness; routing decisions driven by readiness.

For **systemd integration**:

- Services use `Type=notify`. `sdnotify.READY=1` on startup-complete.
- `WATCHDOG=1` periodic from main loop (see [[13-watchdog-timers]]).
- `Restart=on-failure` plus `WatchdogSec=` for combined liveness+restart.

For **`runa.runtime.commands.doctor`**:

- Reads each subsystem's health-check results and renders for terminal.
- Shows degraded vs unhealthy distinctly.
- Suggests operator actions ("Anthropic adapter quarantined — check `runa logs --filter=anthropic` for the last error").

For **Bifröst gateway HTTP endpoints**:

- `/health/live`, `/health/ready`, `/health/startup` as documented in §2.
- Lets LobeChat / Open WebUI / external monitoring probe Runa.

For **per-subsystem health**:

- **Muninn:** SQLite `PRAGMA integrity_check`; vector-index dimension matches config; recent successful read.
- **Skuld:** event-log replay succeeded; no tasks stuck in `in_progress` > N hours.
- **Heimskringla:** at least one provider available; per-provider breaker states.
- **WYRD bridge:** last successful refresh within window; transport (local/Tailnet) responsive.
- **Adapters:** connection state per adapter.

What to avoid:

- Don't use a single probe for all three questions. Liveness, readiness, startup are different.
- Don't conflate "Runa works" with "all subsystems perfect." Composite readiness with degraded state.
- Don't make probes slow. They run frequently.
- Don't ignore degraded state. It's not "still ok" — it's "ok enough but worth surfacing."

## 6. Open questions

- **Probe frequency tuning.** Too often = waste; too rare = late detection. Per-subsystem tuning takes observation.
- **Composite probe weighting.** "Degraded if any check fails" vs "degraded if critical checks fail." The critical/non-critical distinction is per-subsystem.
- **Probe-triggered self-repair.** When a probe fails, should Eir attempt auto-repair before alerting? Productive but risky — auto-repair can mask root causes.

## 7. References (curated)

- kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ — Kubernetes probe model.
- freedesktop.org/software/systemd/man/systemd.service.html — systemd Type=notify.
- *Site Reliability Engineering* (Beyer et al., 2016), chapters 6 ("Monitoring Distributed Systems"), 10-12.
- aws.amazon.com/builders-library/implementing-health-checks/ — AWS Builders' Library.
- Companion docs: [[11-crash-only-software]], [[12-supervisor-trees]], [[13-watchdog-timers]], [[15-self-repair-reconciliation]].
