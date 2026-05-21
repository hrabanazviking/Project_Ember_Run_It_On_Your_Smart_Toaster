# 🎨 Contributing to Verðandi

## Getting Started

1. **Fork** the repository: https://github.com/hrabanazviking/Verdandi
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/Verdandi.git`
3. **Install** in development mode: `pip install -e ".[dev]"`
4. **Run tests**: `python3 -m pytest tests/ -v`
5. **Create a branch**: `git checkout -b feature/my-feature`

## Code Style — The Sacred Craft

We follow Norse Pagan coding philosophy (Mythic Engineering):

### Naming Conventions

- **Modules and classes**: Use Norse mythological names when they map directly to the function
- **Functions and variables**: Use descriptive English names
- **Config keys**: Use dot-notation (`checks.eir.thresholds.cpu_warning_percent`)
- **Nerve event types**: Use snake_case (`heartbeat_pulse`, `state_change`)

### Structure

```
heartbeat/
├── core.py          # Daemon, CircuitBreaker, HealthScore, state machine
├── config.py        # HeartbeatConfig with dot-notation access
├── paths.py         # File-location-agnostic path resolution
├── signals.py        # POSIX signal handling
├── checks/
│   ├── base.py       # BaseCheck, CheckResult, CheckSeverity
│   ├── eir.py        # Health checks
│   ├── huginn.py     # Project checks
│   ├── mimir.py      # Memory checks
│   └── urdr.py       # Schedule checks
└── actions/
    ├── base.py       # BaseAction, ActionContext, ActionResult
    ├── eir_action.py      # Auto-heal
    ├── mjolnir_action.py  # Restart services
    ├── gungnir_action.py  # Escalate
    └── bifrost_action.py  # Bridge/forward
```

### Adding a New Check

1. Create a new file in `heartbeat/checks/`
2. Subclass `BaseCheck`:
```python
from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity

@register_check("my_check")
class MyCheck(BaseCheck):
    name = "my_check"
    description = "What this check monitors"
    
    def check(self) -> CheckResult:
        # Your check logic here
        return CheckResult(
            name="domain:detail",
            severity=CheckSeverity.OK,
            message="All good",
            details={"key": "value"}
        )
```

3. Add to `CHECK_REGISTRY` in `heartbeat/checks/__init__.py`
4. Add config defaults in `HeartbeatConfig.DEFAULTS`
5. Add tests in `tests/test_heartbeat_checks.py`

### Adding a New Action

1. Create a new file in `heartbeat/actions/`
2. Subclass `BaseAction`:
```python
from heartbeat.actions.base import BaseAction, ActionContext, ActionResult, ActionSeverity

@register_action("my_action")
class MyAction(BaseAction):
    name = "my_action"
    description = "What this action does"
    trigger_checks = ["my_check"]
    trigger_severity = CheckSeverity.CRITICAL
    cooldown_seconds = 300
    
    def _execute(self, ctx: ActionContext) -> ActionResult:
        # Your action logic here
        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.SUCCESS,
            message="Action completed"
        )
    
    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message="[DRY-RUN] Would do X, Y, Z"
        )
```

3. Add to `ACTION_REGISTRY` in `heartbeat/actions/__init__.py`
4. Add tests in `tests/test_heartbeat_actions.py`

## Testing Requirements

- All new features must have tests
- All tests must pass: 489+ and growing
- Use `pytest` fixtures for config and temp paths
- Mock external resources (filesystem, network, etc.)
- Integration tests go in `tests/test_heartbeat_integration.py`

## Git Discipline

- **Commit messages**: Use Norse-themed but descriptive messages
  - Good: `🫀 Add circuit breaker pattern to prevent cascading failures`
  - Good: `🔨 Fix sqlite3 context manager leak in mimir check`
  - Bad: `fix stuff`
  - Bad: `update`
- **Push early, push often**: Never let uncommitted changes sit
- **PRs**: One feature per PR, with linked issue

## The Forge Process

We use Mythic Engineering's 6-agent forge process:

1. **Skáld** (Naming/Philosophy) — Names concepts, writes metaphors
2. **Architect** (Structure) — Maps domains, defines boundaries
3. **Smith** (Implementation) — Writes code, fixes bugs
4. **Oracle** (Prediction) — Forecasts bugs, stress tests
5. **Guardian** (Security) — Audits security, hardens surfaces
6. **Lore Master** (Documentation) — Expands docs, writes guides

Each agent contributes in their domain. When adding a new feature, consider all six perspectives.