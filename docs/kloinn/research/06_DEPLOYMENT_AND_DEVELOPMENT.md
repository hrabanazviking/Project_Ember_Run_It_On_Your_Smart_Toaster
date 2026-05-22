# 06 — Deployment and Development

How OpenClaw is deployed and developed. The release-channels model.
The install paths. What translates to Ember.

---

## Three release channels

OpenClaw ships through three channels:

- **stable** — tagged releases (e.g., `openclaw@5.2.0`). Operator-
  ready.
- **beta** — prerelease tags (e.g., `openclaw@5.3.0-beta.4`). For
  early adopters.
- **dev** — moving `main` branch. For contributors.

Operators choose which:

```bash
npm install -g openclaw@latest       # stable
npm install -g openclaw@beta         # beta
npm install -g openclaw@dev          # dev
```

This is a *standard* npm pattern. The OpenClaw discipline: every
commit on `main` is "shippable as dev"; releases gate stable/beta.

---

## Daemon vs ephemeral

Two operational modes:

### Ephemeral
- Run `openclaw` ad hoc.
- Process exits when chat ends.
- No always-on services.

### Daemon
- `openclaw --install-daemon`.
- Installs launchd plist (macOS) or systemd user service (Linux).
- Always-on; handles channel events asynchronously; voice wake
  works.

Operators choose. Both supported.

---

## Cloud deployment options

OpenClaw ships configs for:
- **Fly.io** — `fly.toml`
- **Render** — `render.yaml`
- **Docker** — `Dockerfile` + `docker-compose.yml`

Operators can self-host on a VPS. The Gateway architecture works
the same on cloud as on local (it's still *operator-owned* — just
the operator's VPS, not their laptop).

---

## Development workflow

For contributors:

```bash
git clone https://github.com/openclaw/openclaw
cd openclaw
pnpm install
pnpm gateway:watch   # auto-reloading dev server
```

Dev server reloads on file changes. Standard modern dev experience.

For full setup:

```bash
pnpm build           # produce dist/
pnpm openclaw setup  # interactive onboarding
pnpm openclaw onboard
```

---

## What Ember has today

### Release model

Ember currently has *only* PyPI releases:
- `pip install ember-agent` → latest stable.
- No formal beta channel.
- No "dev" channel beyond installing from main branch via git.

### Operational mode

Ephemeral only. No daemon. No always-on.

### Cloud deploy configs

None. Operators wanting cloud do it manually.

### Dev workflow

```bash
git clone https://github.com/.../Project_Ember_Run_It_On_Your_Smart_Toaster
cd ember
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Standard Python.

---

## What translates

🔵 **Borrow as-is**:

### 1. Three release channels

Ember can adopt:

- `pip install ember-agent` → stable.
- `pip install ember-agent --pre` → beta (PyPI's prerelease flag).
- `pip install ember-agent==X.Y.Z-dev<N>` → explicit dev.

This is *minimal effort* and *operator-friendly*. Just discipline
about which versions land where.

Per [`../applications/48_DEVELOPMENT_CHANNELS_FOR_EMBER.md`](../applications/48_DEVELOPMENT_CHANNELS_FOR_EMBER.md).

### 2. Auto-reloading dev server (sort of)

Ember has `ember chat` which restarts cleanly per session. For
TUI work (Stofa), Textual has dev tools with hot reload. We
should encourage their use in the contributor README.

🟢 **Adapt to Ember Vows**:

### 3. Daemon mode as opt-in

Add `ember --install-daemon` flag (V4 with federation). Default
remains ephemeral. Operators opt in for:
- Always-on chat (no startup time per session).
- Async features (cron tool, bridges).
- Federation host node.

Daemon manages itself via systemd (Linux) / launchd (macOS) /
Windows Service (Windows).

---

## What Ember should NOT borrow

🔴 **Reject**:

### 1. Cloud-deploy configs in core

OpenClaw ships Fly.io + Render configs. Ember should not.

Why: Sovereignty. We don't want to suggest cloud is a primary
deployment path. Operators wanting cloud should write their own
configs.

Documentation in `docs/deploy/` could *show how* to deploy on a
VPS (operator-curated), but core repo doesn't ship the configs.

### 2. Docker as primary install path

OpenClaw provides Dockerfile + docker-compose as easy installation.
Ember sticks with pip.

Why: Pi-class compatibility. Docker on Pi is heavy. pip-install is
universal.

For operators wanting containerization, *they* can build the
container. We can publish reference Dockerfiles in
`docs/contrib/deployment/` if community asks.

---

## Pre-commit hooks

OpenClaw has `.pre-commit-config.yaml`. Common hooks:
- Trailing whitespace
- File ending newlines
- YAML/JSON syntax
- Lint
- Type-check

Ember should adopt this. Cheap; catches issues early.

Proposed `pre-commit-config.yaml` for Ember:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=500']
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        require_serial: true
```

Small commit. Big quality boost.

---

## CI/CD comparison

OpenClaw's CI (visible via `.github/workflows/ci.yml`):
- Multi-OS matrix (Linux, macOS, Windows).
- Multi-Node version matrix.
- Lint + test + build.
- Container builds.

Ember's CI (per existing setup):
- Linux only (currently).
- Single Python version (3.14).
- pytest + ruff.

**Ember should expand CI**:
- Add macOS + Windows runners (per
  [`../../yggdrasil/cross-platform/`](../../yggdrasil/cross-platform/)).
- Add Python 3.12 + 3.13 + 3.14 matrix (we say cross-platform; we
  should verify cross-version).
- Add Pi-class smoke test via QEMU or cross-compilation (later).

---

## Version management

OpenClaw uses semantic versioning:
- `5.0.0` — major release.
- `5.1.0` — minor (additive features).
- `5.1.1` — patch (bug fixes).
- `5.2.0-beta.1` — prerelease tag.

Ember currently is at `0.2.0` after slice 2 ratification. We
should:
- Continue semver.
- Reach `1.0.0` after Yggdrasil Phase 1 + Klóinn Phase 1.
- Use `1.0.0-beta.1` etc. for prerelease testing.

---

## What about a "managed channel"?

OpenClaw mentions "bundled/managed/workspace skills." Operators
have a *choice* of skill source:

- **bundled** — ships with OpenClaw core; auto-updated.
- **managed** — comes from ClawHub registry; operator opt-in.
- **workspace** — operator-authored in their workspace dir.

Ember currently only has "bundled" (the three tools in
`src/ember/tools/`).

🟡 **Defer**: managed-channel skills (centralized registry) is
*against* Ember's Vow of Modular Authorship. We won't run a
registry. Operator-curated only.

But workspace-level operator-authored skills could come earlier.
Once Lua or Python-plugin extension lands, operators can ship
their own.

---

## Closing

Deployment and Development is **where OpenClaw is mature and
Ember is still growing into discipline**. Their three channels,
daemon-or-ephemeral, multi-OS CI, pre-commit hooks — these are
solid engineering practices we should adopt.

What we shouldn't borrow: cloud-deploy configs in core, Docker as
default. Those serve OpenClaw's audience, not ours.

This is *operational maturity* learning. Cheap to implement, big
quality impact.
