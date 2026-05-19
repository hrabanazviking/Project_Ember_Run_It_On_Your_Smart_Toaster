# Runa Project File Organization And Startup Guide

This document explains a strong file organization strategy for Runa Agent and a user-friendly way to run, start, stop, inspect, repair, and update the system.

The purpose is to prevent the project from becoming another fragile pile of scripts. Runa should be easy to understand from the file tree, easy to start from obvious commands, easy to debug from logs and status commands, and easy to repair when something fails.

The filesystem should tell the truth.

If a file starts Runa, it should be obvious. If a service runs in the background, it should be declared. If state is persistent, it should have a known location. If a command changes the system, it should log what it did. If an adapter can fail, it should fail without taking the whole agent down.

## Core Principles

### 1. Obvious Entry Points

A new operator should be able to open the repository and quickly answer:

- How do I install this?
- How do I configure it?
- How do I start it?
- How do I stop it?
- How do I check if it is healthy?
- How do I run tests?
- How do I start only the CLI?
- How do I start only the API?
- How do I start only the worker?
- How do I repair state or memory?
- Where are logs?
- Where is data stored?

The answer should not require reading a thousand-line script.

### 2. Thin Entry Files, Strong Internal Modules

Files that run things should be thin.

Bad pattern:

```text
run_runa.py
  contains config loading
  contains model routing
  contains memory code
  contains CLI parser
  contains service loop
  contains logging setup
  contains repair code
  contains migration code
```

Good pattern:

```text
runa/cli/main.py
  parses command
  calls runa.runtime.commands

runa/runtime/commands.py
  starts/stops/status/checks services

runa/core/*
  contains actual behavior
```

The command file should route. The core modules should do the work.

### 3. One Official CLI

Runa should have one official command:

```bash
runa
```

Everything else should be reachable through subcommands:

```bash
runa start
runa stop
runa restart
runa status
runa doctor
runa logs
runa shell
runa chat
runa worker
runa api
runa gui
runa voice
runa memory check
runa memory backup
runa state snapshot
runa state restore
runa config validate
```

There can be helper scripts, but they should call the official CLI rather than becoming separate control paths.

### 4. No Hidden Startup Behavior

Runa should never install hidden cron jobs, random background scripts, or unclear autostart behavior.

Allowed:

- `runa service install`
- `runa service uninstall`
- `runa service status`
- `systemctl --user status runa-core`
- documented service unit files

Not allowed:

- silent crontab edits
- background `nohup` scripts without status
- startup edits hidden in install scripts
- hard-coded `@reboot` cron commands
- multiple competing startup mechanisms

### 5. Everything Has A Home

Code, config, logs, state, caches, backups, models, adapters, plugins, and docs should not be mixed together.

A clean project separates:

- source code
- tests
- documentation
- runtime data
- user config
- secrets
- generated artifacts
- logs
- deployment files
- external adapters
- development scripts

### 6. Runtime Data Does Not Belong In Git

The repository should contain source and templates, not live memories, live secrets, active logs, databases, or machine-specific generated state.

In Git:

```text
config/runa.example.yaml
deploy/systemd/runa-core.service
docs/
src/runa/
tests/
```

Not in Git:

```text
~/.runa/state/
~/.runa/memory/
~/.runa/logs/
~/.runa/secrets/
~/.runa/cache/
```

### 7. Services Are Separate From Features

The core Runa process should not have to load every possible feature.

The agent should be able to run with:

- no GUI
- no voice
- no Second Life adapter
- no avatar forge
- no browser adapter
- no symbolic plugins
- no remote model provider

The file organization should make this separation obvious.

## Recommended Repository Layout

The future Runa implementation should use a layout like this:

```text
runa-agent/
  README.md
  pyproject.toml
  uv.lock
  .python-version
  .env.example
  .gitignore
  LICENSE
  NOTICE
  THIRD_PARTY_NOTICES.md

  docs/
    index.md
    architecture/
    operations/
    development/
    design/
    security/
    adapters/
    plugins/
    decisions/

  config/
    runa.example.yaml
    logging.example.yaml
    models.example.yaml
    permissions.example.yaml
    profiles/

  src/
    runa/
      __init__.py
      __main__.py
      cli/
      runtime/
      core/
      services/
      apps/
      adapters/
      plugins/
      skills/
      schemas/
      migrations/

  tests/
    unit/
    integration/
    e2e/
    fixtures/
    snapshots/

  scripts/
    dev/
    maintenance/
    one_shot/

  deploy/
    systemd/
    docker/
    pi/
    examples/

  tools/
    repo/
    diagnostics/
    importers/

  examples/
    configs/
    sessions/
    skills/
    plugins/

  vendor/
    README.md
```

This shape gives Runa a clean split between source, docs, config templates, tests, deployment, and helper tools.

## Top-Level Files

### `README.md`

The README should be the front door.

It should contain:

- What Runa is.
- What platforms are supported.
- Fast install.
- Fast start.
- Most important commands.
- Link to operations docs.
- Link to architecture docs.
- Link to development docs.

It should not contain every deep design detail. The README should get the operator moving.

Recommended README command block:

```bash
git clone https://github.com/example/runa-agent
cd runa-agent
uv sync
cp config/runa.example.yaml ~/.runa/config/runa.yaml
runa doctor
runa start
runa status
```

### `pyproject.toml`

This should define:

- package metadata
- Python version
- dependencies
- optional dependency groups
- CLI entrypoint
- test configuration
- lint configuration
- formatting configuration

Most important section:

```toml
[project.scripts]
runa = "runa.cli.main:main"
```

That line creates the official `runa` command.

### `uv.lock` Or Equivalent Lock File

Use a lock file so installs are reproducible.

If using `uv`, keep:

```text
uv.lock
```

If using Poetry:

```text
poetry.lock
```

If using plain pip:

```text
requirements.txt
requirements-dev.txt
```

Pick one main dependency workflow and document it.

### `.python-version`

Pin the expected Python version.

Example:

```text
3.12
```

This prevents accidental runtime differences.

### `.env.example`

This should list optional environment variables, but not actual secrets.

Example:

```bash
RUNA_CONFIG=~/.runa/config/runa.yaml
RUNA_PROFILE=default
RUNA_LOG_LEVEL=INFO
OPENAI_API_KEY=
OPENROUTER_API_KEY=
```

Secrets should normally live in the Runa vault, not in `.env`, but `.env.example` is still useful for development.

### `.gitignore`

Must block runtime data and local generated files.

Recommended entries:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
dist/
build/
*.egg-info/

.runa/
data/
logs/
state/
memory/
cache/
secrets/
backups/
*.db
*.sqlite
*.sqlite3
*.log
```

### `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`

Because Runa may harvest code from multiple repos, third-party notices matter.

Use:

```text
LICENSE
NOTICE
THIRD_PARTY_NOTICES.md
```

Every imported subsystem should mention its origin and license.

## `docs/` Organization

The docs directory should be organized by use case, not as a dumping ground.

Recommended layout:

```text
docs/
  index.md

  architecture/
    overview.md
    lifecycle.md
    event-bus.md
    state.md
    memory.md
    world-model.md
    model-router.md
    tool-system.md
    permissions.md
    plugin-system.md
    adapter-system.md

  operations/
    install.md
    quick-start.md
    configuration.md
    startup.md
    service-management.md
    logs.md
    backup-and-restore.md
    migration.md
    troubleshooting.md
    disaster-recovery.md

  development/
    contributing.md
    local-dev.md
    testing.md
    coding-standards.md
    adding-a-command.md
    adding-a-service.md
    adding-a-tool.md
    adding-an-adapter.md
    adding-a-plugin.md

  design/
    product-principles.md
    user-experience.md
    command-design.md
    config-design.md
    error-message-style.md

  security/
    secrets.md
    permissions.md
    browser-automation.md
    network-access.md
    threat-model.md

  adapters/
    second-life.md
    voice.md
    browser.md
    gui.md
    chat-bridges.md

  plugins/
    runavel.md
    seidr-engine.md
    astrology.md

  decisions/
    ADR-0001-use-src-layout.md
    ADR-0002-one-official-cli.md
    ADR-0003-no-hidden-cron.md
```

### `docs/index.md`

The docs index should act like a table of contents.

It should answer:

- I am installing Runa. Where do I go?
- I am operating Runa. Where do I go?
- I am developing Runa. Where do I go?
- I am adding a new adapter. Where do I go?
- I am recovering from a crash. Where do I go?

### `docs/operations/startup.md`

This should be the authoritative startup guide.

It should define:

- foreground startup
- background service startup
- startup on boot
- manual mode
- safe mode
- recovery mode
- how to disable autostart

### `docs/operations/troubleshooting.md`

This should be organized by symptom:

```text
Runa will not start
Runa starts then exits
Runa cannot load config
Runa cannot reach model provider
Runa memory database is locked
Runa service is unhealthy
Runa CLI cannot connect to daemon
Runa GUI cannot connect to API
Runa voice adapter fails
```

Each symptom should have:

- command to check
- likely cause
- repair command
- where logs are

## `config/` Organization

The repo should include example config, not live operator config.

Recommended layout:

```text
config/
  runa.example.yaml
  logging.example.yaml
  models.example.yaml
  permissions.example.yaml
  profiles/
    pi5.example.yaml
    dev.example.yaml
    safe.example.yaml
    server.example.yaml
```

Live config should be copied to:

```text
~/.runa/config/runa.yaml
```

### Main Config File

Recommended live config:

```text
~/.runa/config/runa.yaml
```

Recommended example:

```yaml
profile: default

paths:
  home: ~/.runa
  state: ~/.runa/state
  memory: ~/.runa/memory
  logs: ~/.runa/logs
  cache: ~/.runa/cache
  backups: ~/.runa/backups
  secrets: ~/.runa/secrets

runtime:
  mode: service
  event_bus: sqlite
  health_interval_seconds: 30
  shutdown_timeout_seconds: 20

model_router:
  default_provider: openrouter
  fallback_provider: ollama
  local_provider: ollama

memory:
  enabled: true
  consolidation_enabled: true
  backup_enabled: true
  backup_interval_hours: 24

adapters:
  voice:
    enabled: false
  gui:
    enabled: false
  second_life:
    enabled: false
  browser:
    enabled: false

permissions:
  mode: owner_trust
  log_all_actions: true
  require_confirmation_for:
    - deleting_home_directory
    - formatting_disk
    - spending_money
    - sending_external_messages
```

### Config Profiles

Profiles make startup user-friendly.

Examples:

```bash
runa start --profile dev
runa start --profile pi5
runa start --profile safe
```

Profile examples:

```text
dev
  local files
  verbose logs
  no autostart
  fake adapters

pi5
  Raspberry Pi defaults
  real memory paths
  systemd user services
  lower model concurrency

safe
  no shell writes
  no network writes
  no external messages
  no browser automation

server
  API enabled
  GUI disabled
  worker enabled
  remote access configured
```

### Config Validation

There should be a command:

```bash
runa config validate
```

It should check:

- paths exist or can be created
- required keys exist
- unknown keys are warned about
- selected model providers are configured
- enabled adapters have required settings
- permissions are valid
- secrets are referenced but not exposed

Bad config should fail before startup.

## `src/runa/` Organization

Use a `src/` layout. It prevents import confusion and keeps source separate from repo tools.

Recommended:

```text
src/
  runa/
    __init__.py
    __main__.py
    cli/
    runtime/
    core/
    services/
    apps/
    adapters/
    plugins/
    skills/
    schemas/
    migrations/
```

### `src/runa/__main__.py`

This allows:

```bash
python -m runa
```

It should simply call the CLI:

```python
from runa.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
```

### `src/runa/cli/`

The CLI owns user commands. It should not contain deep business logic.

Recommended:

```text
src/runa/cli/
  __init__.py
  main.py
  output.py
  parser.py
  commands/
    __init__.py
    start.py
    stop.py
    restart.py
    status.py
    doctor.py
    logs.py
    chat.py
    shell.py
    config.py
    memory.py
    state.py
    service.py
    plugin.py
    adapter.py
```

Responsibilities:

- parse args
- call runtime command functions
- format output
- return clean exit codes

Not responsibilities:

- memory algorithms
- model routing
- agent planning
- adapter implementation
- daemon internals

### `src/runa/runtime/`

Runtime owns process lifecycle.

Recommended:

```text
src/runa/runtime/
  __init__.py
  bootstrap.py
  commands.py
  process.py
  daemon.py
  supervisor.py
  health.py
  shutdown.py
  paths.py
  locks.py
  pidfile.py
  modes.py
```

Responsibilities:

- load config
- initialize paths
- initialize logging
- start services
- stop services
- manage pid files
- prevent duplicate daemons
- expose health status
- coordinate graceful shutdown
- run safe mode and recovery mode

### `src/runa/core/`

Core owns cognition, state, memory, tools, planning, and internal contracts.

Recommended:

```text
src/runa/core/
  __init__.py
  kernel/
  lifecycle/
  events/
  state/
  memory/
  context/
  models/
  planning/
  tasks/
  tools/
  permissions/
  guardrails/
  secrets/
  world/
  logging/
  errors/
```

### `src/runa/core/kernel/`

The kernel coordinates the agent.

```text
kernel/
  kernel.py
  cycle.py
  coordinator.py
  contracts.py
```

It should not directly know about every adapter. It should talk to interfaces:

```text
MemoryGateway
EventBus
TaskLedger
ModelRouter
ToolRegistry
StateStore
WorldModel
```

### `src/runa/core/events/`

The event system is Runa's nervous system.

```text
events/
  bus.py
  envelope.py
  types.py
  subscribers.py
  journal.py
```

All important actions should emit events:

- startup
- shutdown
- user message
- tool call requested
- tool call completed
- memory written
- task created
- task completed
- adapter connected
- adapter failed
- recovery started
- recovery completed

### `src/runa/core/state/`

State owns durable runtime continuity.

```text
state/
  snapshot.py
  store.py
  serializer.py
  diff.py
  recovery.py
  migrations.py
```

This is where `wyrdstate` ideas belong.

### `src/runa/core/memory/`

Memory should be a system, not a single file.

```text
memory/
  gateway.py
  schema.py
  store.py
  semantic.py
  associative.py
  consolidation.py
  decay.py
  audit.py
  backup.py
  repair.py
  retrieval.py
  provenance.py
```

This is where `mimir-well`, `huginn`, `muninn`, `bifrost`, and `eir` ideas belong.

### `src/runa/core/context/`

Context owns what gets sent into models.

```text
context/
  assembler.py
  budget.py
  pruner.py
  summarizer.py
  citations.py
```

This is where `svalinn` and Mimir context-engineering ideas belong.

### `src/runa/core/models/`

Model routing should be separate from the agent loop.

```text
models/
  router.py
  provider.py
  messages.py
  budgets.py
  fallbacks.py
  providers/
    openai.py
    openrouter.py
    ollama.py
    lmstudio.py
```

The rest of Runa should not care which provider is currently used.

### `src/runa/core/tools/`

Tools should be registered, permissioned, logged, and evaluated.

```text
tools/
  registry.py
  tool.py
  executor.py
  result.py
  affinity.py
  builtin/
    filesystem.py
    shell.py
    git.py
    web.py
```

This is where `skofnung` ideas belong.

### `src/runa/core/permissions/`

Permissions should be explicit.

```text
permissions/
  policy.py
  grants.py
  evaluator.py
  audit.py
```

This should answer:

- Is this tool allowed?
- Is this path allowed?
- Is this network target allowed?
- Is this secret allowed?
- Should this action be logged?
- Should this action require confirmation?

### `src/runa/core/guardrails/`

Guardrails should validate behavior without turning the agent into permission-paralysis.

```text
guardrails/
  output.py
  commands.py
  memory.py
  tool_calls.py
```

This is where `vordr` and memory guard ideas belong.

### `src/runa/core/secrets/`

Secrets must be separate from config.

```text
secrets/
  vault.py
  crypto.py
  store.py
  references.py
  audit.py
```

This is where `kista` ideas belong.

### `src/runa/core/world/`

The world model should be separate from memory.

```text
world/
  model.py
  entity.py
  component.py
  relation.py
  observation.py
  belief.py
  oracle.py
  store.py
```

This is where WYRD ideas belong.

### `src/runa/services/`

Services are long-running runtime pieces.

Recommended:

```text
services/
  core_service.py
  api_service.py
  worker_service.py
  scheduler_service.py
  memory_service.py
  health_service.py
```

These are not systemd files. These are Python service classes used by the runtime.

Each service should implement:

```python
class Service:
    name: str

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def health(self) -> HealthStatus: ...
```

### `src/runa/apps/`

Apps are user-facing programs.

Recommended:

```text
apps/
  api/
    app.py
    routes/
    models.py
  tui/
    app.py
  gui/
    app.py
  voice/
    app.py
```

Keep apps thin. They should call Runa services and core interfaces.

### `src/runa/adapters/`

Adapters connect Runa to external worlds.

Recommended:

```text
adapters/
  second_life/
  browser/
  voice/
  discord/
  matrix/
  email/
  filesystem_watch/
```

Adapter rules:

- optional by default
- config-gated
- permission-gated
- health-checkable
- restartable
- isolated from core cognition

### `src/runa/plugins/`

Plugins are optional capabilities.

Recommended:

```text
plugins/
  runavel/
  seidr_engine/
  astrology/
```

Plugin rules:

- no startup side effects
- explicit manifest
- explicit permissions
- explicit commands/tools exposed
- tests for each plugin

### `src/runa/skills/`

Skills are structured instructions and tool recipes.

Recommended:

```text
skills/
  loader.py
  manifest.py
  registry.py
  validator.py
```

Skill files can live in:

```text
~/.runa/skills/
```

Repo-provided examples can live in:

```text
examples/skills/
```

### `src/runa/schemas/`

Shared typed schemas belong here.

```text
schemas/
  config.py
  events.py
  memory.py
  state.py
  tools.py
  permissions.py
  health.py
```

Prefer typed schemas over loose dictionaries.

### `src/runa/migrations/`

Migrations belong in a known place.

```text
migrations/
  state/
  memory/
  config/
```

Runa needs migration commands:

```bash
runa migrate check
runa migrate apply
runa migrate status
```

## Runtime Home Directory

Runa's runtime home should be:

```text
~/.runa/
```

Recommended layout:

```text
~/.runa/
  config/
    runa.yaml
    logging.yaml
    models.yaml
    permissions.yaml

  state/
    snapshots/
    sessions/
    pid/
    locks/

  memory/
    runa-memory.sqlite3
    vector/
    associative/
    backups/

  logs/
    runa.log
    events.jsonl
    tools.jsonl
    errors.log
    audit.jsonl

  cache/
    prompts/
    tools/
    web/

  secrets/
    vault.db
    keys/

  backups/
    state/
    memory/
    config/

  plugins/
  skills/
  adapters/
  tmp/
```

### Why Runtime Home Matters

This avoids:

- writing state into the Git repository
- losing memory during code updates
- mixing logs with source files
- leaking secrets into commits
- making backups hard
- making uninstall unclear

### `runa paths`

Add a command:

```bash
runa paths
```

Expected output:

```text
Runa home:     /home/pi/.runa
Config:        /home/pi/.runa/config/runa.yaml
State:         /home/pi/.runa/state
Memory:        /home/pi/.runa/memory
Logs:          /home/pi/.runa/logs
Cache:         /home/pi/.runa/cache
Secrets:       /home/pi/.runa/secrets
Backups:       /home/pi/.runa/backups
```

This is a small command that prevents a lot of confusion.

## User-Friendly Startup Design

Runa should support several startup styles:

1. Foreground development mode.
2. Local chat mode.
3. Background service mode.
4. Boot autostart mode.
5. Safe mode.
6. Recovery mode.

Each mode should use the same config system and same runtime code.

## Official Commands

### `runa init`

Creates the runtime home.

```bash
runa init
```

Should do:

- create `~/.runa`
- create subdirectories
- copy example config if missing
- create empty log files if useful
- initialize state database
- initialize memory database
- print next steps

Should not do:

- install autostart
- edit crontab
- start background services without saying so
- overwrite existing config without backup

### `runa doctor`

Checks whether Runa can run.

```bash
runa doctor
```

Should check:

- Python version
- package installation
- config validity
- runtime paths
- write permissions
- model provider config
- memory database health
- state database health
- secrets vault status
- service status
- systemd status if installed

Example output:

```text
Runa Doctor

OK   Python 3.12.4
OK   Config valid: /home/pi/.runa/config/runa.yaml
OK   State path writable
OK   Memory database reachable
WARN OpenRouter key missing
OK   Ollama reachable at http://localhost:11434
OK   No stale lock files
OK   Service not currently running
```

### `runa start`

Starts Runa.

```bash
runa start
```

Default behavior:

- load config
- validate config
- initialize logging
- acquire lock
- start core service
- start enabled services
- print status

Useful flags:

```bash
runa start --foreground
runa start --daemon
runa start --profile pi5
runa start --safe
runa start --no-adapters
runa start --only core
runa start --only api
runa start --only worker
```

### `runa stop`

Stops Runa cleanly.

```bash
runa stop
```

Should:

- send shutdown event
- stop accepting new tasks
- wait for active task checkpoint
- flush memory writes
- save state snapshot
- stop services
- release lock
- print shutdown result

### `runa restart`

Equivalent to:

```bash
runa stop
runa start
```

But implemented with correct lifecycle handling.

### `runa status`

Shows current status.

```bash
runa status
```

Should show:

- running or stopped
- pid
- uptime
- profile
- config path
- enabled services
- model provider status
- memory status
- queue length
- last error
- last snapshot

Example:

```text
Runa is running

PID:               10422
Uptime:            2h 14m
Profile:           pi5
Config:            /home/pi/.runa/config/runa.yaml
Core:              healthy
API:               healthy on http://127.0.0.1:8765
Worker:            healthy
Memory:            healthy, last backup 3h ago
Event bus:         healthy, 12 pending events
Last snapshot:     2026-05-17 14:04:22
Last error:        none
```

### `runa logs`

Shows logs in a user-friendly way.

```bash
runa logs
runa logs --follow
runa logs --errors
runa logs --events
runa logs --tools
```

It should know where logs are. The user should not have to remember log paths.

### `runa chat`

Starts an interactive terminal chat with Runa.

```bash
runa chat
```

If core is running, it connects to the running core.

If core is not running, it can either:

- start temporary local foreground mode
- or print a clear message:

```text
Runa core is not running.
Start it with: runa start
Or run one-shot local chat with: runa chat --local
```

### `runa shell`

Starts an operator shell for administrative commands.

```bash
runa shell
```

This is not a Unix shell. It is a Runa command shell:

```text
runa> status
runa> memory search "Volmarr preferences"
runa> state snapshot
runa> tasks list
runa> logs errors
runa> exit
```

### `runa api`

Runs only the API service.

```bash
runa api --foreground
```

Useful for development and GUI integration.

### `runa worker`

Runs only background workers.

```bash
runa worker --foreground
```

Workers include:

- memory consolidation
- backups
- health checks
- scheduled tasks

### `runa gui`

Starts the GUI.

```bash
runa gui
```

Should connect to the API or core service. GUI startup should not duplicate the core runtime.

### `runa voice`

Starts the voice interface.

```bash
runa voice
```

Should be an adapter/app, not the main runtime.

### `runa service install`

Installs systemd user services.

```bash
runa service install
```

Should:

- write systemd unit files to the user systemd directory
- reload systemd user daemon
- print exactly what was installed
- not start automatically unless requested

Better:

```bash
runa service install --enable
runa service install --enable --start
```

### `runa service uninstall`

Removes systemd services.

```bash
runa service uninstall
```

Should:

- stop services
- disable services
- remove Runa unit files
- reload systemd user daemon
- leave user data alone

### `runa service status`

Wraps systemd status in a friendlier view.

```bash
runa service status
```

Should show:

- installed or not installed
- enabled or disabled
- running or stopped
- unit file path
- last failure

## Recommended Startup Files

There should be very few files whose job is to start Runa.

### Python Entrypoint

```text
src/runa/__main__.py
```

Purpose:

```bash
python -m runa
```

### CLI Entrypoint

```text
src/runa/cli/main.py
```

Purpose:

```bash
runa
```

### Runtime Bootstrap

```text
src/runa/runtime/bootstrap.py
```

Purpose:

- load config
- initialize paths
- initialize logging
- build service container
- return runtime object

### Runtime Commands

```text
src/runa/runtime/commands.py
```

Purpose:

- `start()`
- `stop()`
- `restart()`
- `status()`
- `doctor()`

### Service Units

```text
deploy/systemd/runa-core.service
deploy/systemd/runa-worker.service
deploy/systemd/runa-api.service
```

Purpose:

- documented background service files
- installed only by explicit command

### Dev Helper

```text
scripts/dev/run-local.sh
```

Purpose:

- convenience wrapper for developers
- calls `uv run runa start --foreground --profile dev`
- not used as production startup

## Systemd User Service Design

For a Raspberry Pi owner machine, systemd user services are cleaner than cron.

Recommended files:

```text
deploy/systemd/
  runa-core.service
  runa-api.service
  runa-worker.service
```

### `runa-core.service`

Example:

```ini
[Unit]
Description=Runa Core Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/runa start --foreground --profile pi5 --only core
ExecStop=%h/.local/bin/runa stop --only core
Restart=on-failure
RestartSec=10
WorkingDirectory=%h/Runa-Agent
Environment=RUNA_CONFIG=%h/.runa/config/runa.yaml

[Install]
WantedBy=default.target
```

### `runa-worker.service`

```ini
[Unit]
Description=Runa Worker Service
After=runa-core.service
Requires=runa-core.service

[Service]
Type=simple
ExecStart=%h/.local/bin/runa worker --foreground --profile pi5
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### `runa-api.service`

```ini
[Unit]
Description=Runa Local API Service
After=runa-core.service
Requires=runa-core.service

[Service]
Type=simple
ExecStart=%h/.local/bin/runa api --foreground --profile pi5
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### Why User Services

Use:

```bash
systemctl --user status runa-core
```

Instead of:

```bash
sudo systemctl status runa-core
```

Runa belongs to the user account and writes to `~/.runa`.

### Autostart Command

Autostart should be explicit:

```bash
runa service install --enable --start
```

Disable should be explicit:

```bash
runa service uninstall
```

No crontab needed.

## Development Scripts

Scripts are allowed, but they should be boring and obvious.

Recommended:

```text
scripts/
  dev/
    run-local.sh
    run-api.sh
    run-worker.sh
    reset-dev-data.sh
  maintenance/
    backup-now.sh
    check-repo.sh
  one_shot/
    import-hermes-memory.py
    import-wyrdstate.py
```

Rules:

- scripts must have clear names
- scripts must call official commands when possible
- scripts must not contain hidden daemon logic
- scripts must not edit crontab
- scripts must not silently install services
- destructive scripts must print what they will delete

## Makefile Or Task Runner

A `Makefile` or `justfile` can improve developer experience, but it should not replace the user CLI.

Recommended `justfile` commands:

```text
install
dev
test
lint
format
doctor
start
stop
status
logs
```

Example:

```makefile
.PHONY: install dev test lint format doctor

install:
	uv sync

dev:
	uv run runa start --foreground --profile dev

test:
	uv run pytest

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

doctor:
	uv run runa doctor
```

Important:

The official command is still `runa`. The Makefile is only a developer shortcut.

## Tests Organization

Recommended:

```text
tests/
  unit/
    core/
    runtime/
    cli/
    adapters/
  integration/
    memory/
    state/
    services/
    tools/
  e2e/
    test_start_stop.py
    test_chat_local.py
    test_recovery.py
  fixtures/
    configs/
    memory/
    state/
  snapshots/
```

### Startup Tests

Startup must be tested.

Minimum tests:

```text
test_init_creates_home
test_config_validate_accepts_example
test_config_validate_rejects_bad_path
test_start_foreground
test_stop_saves_snapshot
test_status_when_stopped
test_status_when_running
test_doctor_reports_missing_provider
test_safe_mode_disables_adapters
test_duplicate_start_is_rejected
test_stale_pidfile_is_recovered
```

### Service Tests

Background services should be tested without needing real systemd where possible.

Test:

- generated unit file content
- install path selection
- command generation
- service status parser
- uninstall behavior

### CLI Tests

CLI tests should verify:

- help text
- exit codes
- errors are readable
- commands call correct runtime functions
- JSON output works where supported

## Logging Organization

Runa should use structured logs and human-friendly logs.

Runtime logs:

```text
~/.runa/logs/runa.log
~/.runa/logs/errors.log
~/.runa/logs/events.jsonl
~/.runa/logs/tools.jsonl
~/.runa/logs/audit.jsonl
```

### `runa.log`

Human-readable runtime log.

### `errors.log`

Error-only log.

### `events.jsonl`

Structured event journal.

Each line:

```json
{"time":"2026-05-17T14:04:22Z","event":"memory.write","session":"abc","status":"ok"}
```

### `tools.jsonl`

Tool-call audit log.

Must include:

- tool name
- request id
- permission decision
- started time
- finished time
- status
- summarized result
- redacted secrets

### `audit.jsonl`

Security and operator-relevant actions.

Must include:

- config changes
- service install/uninstall
- secret access
- external message sends
- destructive actions
- permission escalations

## Data And Backup Organization

Backups should be first-class.

Runtime:

```text
~/.runa/backups/
  state/
  memory/
  config/
  full/
```

Commands:

```bash
runa backup create
runa backup list
runa backup restore <backup-id>
runa backup verify <backup-id>
```

Backup metadata:

```json
{
  "id": "2026-05-17T14-04-22",
  "created_at": "2026-05-17T14:04:22Z",
  "profile": "pi5",
  "includes": ["state", "memory", "config"],
  "schema_versions": {
    "state": 3,
    "memory": 5,
    "config": 2
  }
}
```

## Operator-Friendly Error Messages

Startup errors should be precise and actionable.

Bad:

```text
Error: failed
```

Good:

```text
Runa could not start because the memory database is locked.

Database:
  /home/pi/.runa/memory/runa-memory.sqlite3

Likely cause:
  Another Runa process is still running, or a previous process crashed.

Try:
  runa status
  runa stop
  runa doctor
  runa memory repair
```

Every startup failure should point to:

- what failed
- where it failed
- likely cause
- next command

## Safe Mode

Safe mode is essential.

Command:

```bash
runa start --safe
```

Safe mode should:

- disable external adapters
- disable shell write tools
- disable external message sending
- disable browser automation
- disable scheduled jobs
- load state read-only if needed
- allow diagnostics and repair

Safe mode lets the operator recover from bad config, broken adapters, or corrupted plugin behavior.

## Recovery Mode

Recovery mode is for damaged state or memory.

Command:

```bash
runa recover
```

Subcommands:

```bash
runa recover state
runa recover memory
runa recover config
runa recover all
```

Recovery should:

- create backup before changing anything
- inspect schema versions
- detect corruption
- attempt repair
- produce report
- never silently delete data

## First-Run Experience

The first run should feel guided but not childish.

Recommended flow:

```bash
runa init
runa doctor
runa start
runa chat
```

### `runa init` Example Output

```text
Runa initialized.

Created:
  /home/pi/.runa/config/runa.yaml
  /home/pi/.runa/state
  /home/pi/.runa/memory
  /home/pi/.runa/logs
  /home/pi/.runa/cache
  /home/pi/.runa/backups

Next:
  runa doctor
  runa start
```

### `runa start` Example Output

```text
Starting Runa with profile: pi5

OK   Config loaded
OK   Runtime paths ready
OK   State store ready
OK   Memory gateway ready
OK   Event bus ready
OK   Core service started
OK   Worker service started

Runa is running.

Use:
  runa status
  runa chat
  runa logs --follow
```

## File Naming Rules

Use boring, clear names.

Good:

```text
memory/gateway.py
memory/backup.py
state/snapshot.py
runtime/bootstrap.py
cli/commands/start.py
adapters/second_life/client.py
```

Bad:

```text
big_agent.py
main2.py
new_main.py
helper.py
utils.py
final_runner.py
startup_fixed.py
run_everything.py
```

### Avoid Giant `utils.py`

If a utility is about paths, put it in:

```text
runtime/paths.py
```

If it is about time:

```text
core/time.py
```

If it is about memory:

```text
core/memory/*.py
```

Generic utilities become junk drawers.

## Import Direction Rules

Good architecture has one-way dependencies.

Recommended direction:

```text
cli -> runtime -> services -> core
apps -> services -> core
adapters -> core interfaces
plugins -> core interfaces
core -> schemas
```

Avoid:

```text
core importing cli
core importing gui
core importing second_life
memory importing voice
tools importing api routes
```

The core should know interfaces, not frontends.

## Adapter Startup Rules

Adapters should not start just because they are installed.

Config should control them:

```yaml
adapters:
  second_life:
    enabled: false
  voice:
    enabled: true
  browser:
    enabled: false
```

Commands:

```bash
runa adapter list
runa adapter status
runa adapter start voice
runa adapter stop voice
runa adapter enable voice
runa adapter disable voice
```

Adapter status example:

```text
voice        enabled   running    healthy
second_life  disabled  stopped    not configured
browser      disabled  stopped    policy disabled
```

## Plugin Startup Rules

Plugins should be passive until enabled.

Plugin manifest:

```yaml
name: runavel
version: 0.1.0
entrypoint: runa.plugins.runavel:plugin
permissions:
  filesystem: read-only
  network: none
  secrets: none
commands:
  - rune
  - bindrune
```

Commands:

```bash
runa plugin list
runa plugin inspect runavel
runa plugin enable runavel
runa plugin disable runavel
```

No plugin should silently register background jobs.

## Scheduling Without Cron

Runa can have scheduled jobs, but they should be inside Runa's scheduler service or systemd timers, not hidden cron entries.

Recommended:

```text
runa scheduler list
runa scheduler enable memory-consolidation
runa scheduler disable memory-consolidation
runa scheduler run memory-consolidation
```

Example schedule config:

```yaml
schedules:
  memory_consolidation:
    enabled: true
    interval: 6h
  memory_backup:
    enabled: true
    interval: 24h
  health_report:
    enabled: true
    interval: 1h
```

Scheduler state should be visible:

```bash
runa scheduler status
```

## Repository Docs To Keep At Root

The current planning repo has many root Markdown files. That is fine for a design archive, but the future implementation repo should move most docs under `docs/`.

Root should keep only:

```text
README.md
LICENSE
NOTICE
THIRD_PARTY_NOTICES.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
```

Deep design docs should go under:

```text
docs/architecture/
docs/design/
docs/operations/
docs/research/
```

This keeps the front door clean.

## Suggested Migration From Current Planning Repo

Current root docs can be organized like this:

```text
ROBUST_AGENT_ENGINEERING_PLAN.md
  -> docs/architecture/robust-agent-engineering-plan.md

HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md
  -> docs/research/hermes-openclaw-design-anti-patterns.md

RUNA_ADVANCED_AGI_ENGINEERING_GUIDE.md
  -> docs/architecture/advanced-agi-engineering-guide.md

RUNA_ECOSYSTEM_IDEA_HARVEST.md
  -> docs/research/runa-ecosystem-idea-harvest.md

RUNAFREYJASDOTTIR_GITHUB_CODE_HARVEST.md
  -> docs/research/runafreyjasdottir-github-code-harvest.md

RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md
  -> docs/operations/file-organization-and-startup.md
```

The current repo can stay as-is for now, but the implementation repo should use the cleaner docs tree.

## Minimal First Implementation Tree

The first code version should start smaller than the full architecture.

Recommended first slice:

```text
runa-agent/
  README.md
  pyproject.toml
  .env.example
  config/
    runa.example.yaml
  src/
    runa/
      __init__.py
      __main__.py
      cli/
        main.py
        commands/
          init.py
          doctor.py
          start.py
          stop.py
          status.py
      runtime/
        bootstrap.py
        commands.py
        paths.py
        health.py
        locks.py
      core/
        state/
        events/
        memory/
        models/
  tests/
    unit/
    e2e/
  deploy/
    systemd/
```

Do not build every adapter first.

Build:

```text
init
doctor
start
stop
status
logs
state snapshot
memory check
```

Then expand.

## Golden Path Commands

These commands should always work and should be tested on every release:

```bash
runa init
runa doctor
runa start --foreground
runa status
runa chat --local
runa state snapshot
runa memory check
runa logs
runa stop
```

If these commands are reliable, the project will feel solid.

If these commands are unreliable, no amount of AGI ambition matters.

## What The User Should Never Need To Do

The user should not need to:

- edit crontab manually
- search for random process IDs
- guess where logs are
- guess where config is
- inspect giant scripts to know how startup works
- delete lock files manually except through documented recovery
- run different startup scripts for different subsystems
- copy secrets into source files
- modify code to change model provider
- run background processes with `nohup`
- remember hidden environment variables

There should be a Runa command for normal operations.

## Final Recommended File Roles

The most important file roles are:

```text
README.md
  human front door

pyproject.toml
  package, dependency, and CLI definition

config/runa.example.yaml
  example operator config

src/runa/__main__.py
  python -m runa entry

src/runa/cli/main.py
  runa command entry

src/runa/runtime/bootstrap.py
  config, paths, logging, service construction

src/runa/runtime/commands.py
  start, stop, status, doctor behavior

src/runa/core/*
  actual agent capabilities

src/runa/services/*
  long-running service classes

deploy/systemd/*
  explicit service templates

docs/operations/startup.md
  authoritative startup documentation

tests/e2e/test_start_stop.py
  proof startup works
```

## Final Design Standard

Runa should be organized so that:

- the file tree explains the system
- the CLI controls the system
- systemd starts only documented services
- config is typed and validated
- runtime data lives in `~/.runa`
- state can be snapshotted and restored
- memory can be checked and repaired
- logs are easy to find
- adapters are optional
- plugins are permissioned
- startup is tested
- shutdown is graceful
- recovery is normal, not panic

The implementation should be boring in the places where reliability matters.

The mythic, expressive, companion-like parts of Runa can live above that foundation. But the foundation itself should be plain, explicit, inspectable, and hard to break.
