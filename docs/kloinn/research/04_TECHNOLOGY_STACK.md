# 04 — Technology Stack

OpenClaw's technology choices, contrasted with Ember's. What each
implies about the project's audience and constraints.

---

## OpenClaw's stack

| Layer | Choice |
|---|---|
| **Language** | TypeScript |
| **Runtime** | Node.js 24 (recommended), 22.19+ minimum |
| **Package manager** | pnpm (workspace) |
| **Build/bundle** | tsdown, tsx |
| **Testing** | Vitest |
| **Linter** | Oxlint |
| **Security** | Semgrep |
| **Containerization** | Docker (`Dockerfile`, `docker-compose.yml`) |
| **Cloud deploy targets** | Fly.io, Render |
| **Pre-commit** | `.pre-commit-config.yaml` |
| **IDE config** | `.vscode/` checked in |

This is a **modern JavaScript-ecosystem stack** — what a TypeScript-
native team would build in 2024-2026.

---

## Ember's stack

| Layer | Choice |
|---|---|
| **Language** | Python 3.14 |
| **Runtime** | CPython (system or .venv) |
| **Package manager** | pip + pyproject.toml |
| **Build** | none (pure Python, no compile step) |
| **Testing** | pytest |
| **Linter** | ruff (also formatter) |
| **Security** | bandit (when run) |
| **Containerization** | none (operator can dockerize if they want) |
| **Cloud deploy targets** | none (sovereign-first) |
| **Pre-commit** | none |
| **IDE config** | none checked in |

This is a **deliberately minimal Python-ecosystem stack** — what
the Pi-class hardware can run without complaint.

---

## The fundamental divergence

OpenClaw bets on **Node.js**:
- Vast ecosystem (npm has the most packages of any registry).
- TypeScript = strong typing in a flexible language.
- Mature async (event loop natively).
- Front-end + back-end same language (Live Canvas + UI in TS).
- Mobile-friendly (React Native if needed).

Ember bets on **Python**:
- Best AI/ML ecosystem (sentence-transformers, ollama-python,
  PyTorch, llama.cpp Python bindings).
- Pi-class friendly (CPython runs on every device we target).
- Operator-friendly (Python is more widely-taught than TypeScript).
- Simple deployment (no compile, no bundle, no node_modules).
- Existing scientific tooling for the data work (pandas, numpy).

Both are *reasonable choices*. They lead to different ergonomics.

---

## What this implies about operators

### OpenClaw's operator

- Comfortable with Node.js + npm/pnpm ecosystem.
- Likely has installed Node before.
- Used to JavaScript-ecosystem patterns (package.json, workspaces,
  bundlers).
- Often a web developer or polyglot engineer.
- Likely on Mac/Linux.

### Ember's operator

- Comfortable with Python + pip.
- Possibly never touched Node.
- Used to Unix tooling (CLI, shell scripting, simple installs).
- Often a data scientist, hobbyist, sysadmin, or AI-researcher.
- Likely on Linux (Pi, Ubuntu, etc.) or Mac.

Different audiences. Both legitimate.

---

## Performance considerations

### Node.js advantages

- **Faster startup**: Node starts in ~50ms. CPython is ~150-300ms.
- **JIT optimization**: V8's JIT optimizes hot paths.
- **Concurrent I/O**: Node's event loop is purpose-built for
  concurrent network I/O (great for 23+ channel bridges).

### Python advantages

- **Slower native startup but better for our actual workloads**:
  Once we're past startup, both languages are I/O-bound for LLM
  inference (the LLM is the bottleneck, not the agent code).
- **Better LLM ecosystem**: Ollama, llama.cpp, sentence-transformers,
  langchain, transformers — all primarily Python.
- **Type hints + runtime checks**: Python's gradual typing is less
  strict than TS but enough for most production work.

For Ember's specific workload (LLM-bound, low-concurrency, single-
operator), Python is *fine*. We don't need Node's I/O concurrency.

For OpenClaw's workload (multi-channel, multi-agent, possibly
many concurrent sessions), Node's I/O concurrency is *valuable*.

The right tool depends on the workload.

---

## Footprint comparison

### Disk

A fresh OpenClaw install with all dependencies:
- node_modules: hundreds of MB
- TypeScript compiled output: tens of MB
- Total: ~500MB-1GB

A fresh Ember install:
- .venv with all deps: ~150MB
- src/ember: ~5MB
- Total: ~150-200MB

Ember is ~3-5× lighter. Matters for Pi-class.

### RAM

OpenClaw daemon idle: ~150-300MB (Node + V8 + loaded modules).
Ember running `ember chat`: ~80-150MB (Python + loaded modules).

Roughly 2× difference. Matters for SMALL profile (< 4GB total).

### Boot time

OpenClaw cold start: ~1-2 seconds.
Ember cold start: ~0.5-1 second.

Marginal. Both feel responsive.

---

## Operator install experience

### OpenClaw

```bash
npm install -g openclaw@latest
openclaw setup
openclaw  # opens chat
```

Three commands. Assumes Node + npm installed.

### Ember (current)

```bash
pip install ember-agent
ember setup
ember chat
```

Three commands. Assumes Python + pip installed.

Both are *roughly equivalent* install experiences. The difference
is *which runtime the operator already has*.

A typical Linux distribution ships with Python (sometimes also
Node). A typical macOS install has Python (older) + sometimes
Node via Homebrew. Windows is the most variable.

For mainstream operators: both stacks are reasonable.
For Pi-class operators: Python is preinstalled; Node usually isn't.

---

## What Ember can borrow from OpenClaw's tooling

🔵 **Borrow as-is**:

### 1. pre-commit hooks

OpenClaw uses `.pre-commit-config.yaml`. Ember should adopt this.
Catches issues before commit; complements CI.

### 2. Linter discipline

OpenClaw uses Oxlint (modern, fast). Ember uses ruff (modern,
fast). Both projects discipline themselves with linters in CI.
Worth continuing.

### 3. Semgrep for security scanning

OpenClaw uses Semgrep for security patterns. Ember could add this
to CI for an extra layer beyond bandit.

### 4. Workspace-level tsconfig discipline

Translates to: workspace-level pyproject.toml + per-package
config. Ember already does this; OpenClaw's monorepo pattern is
*more explicit*.

---

## What Ember should NOT borrow

🔴 **Reject**:

### 1. Cloud-deploy configs (Fly.io, Render)

OpenClaw ships these. Ember does not. Sovereignty is the difference.

Operators wanting to self-host on VPS can do so manually; we
don't help them by shipping cloud-deploy configs.

### 2. Docker as default

OpenClaw provides Dockerfile + docker-compose by default. Ember
does not (and shouldn't).

Reason: Docker is a heavy assumption for Pi-class. Many of our
operators don't have Docker installed.

For LARGE profile operators who want Docker: they can dockerize
Ember themselves. We provide instructions, not a default setup.

### 3. Node-based dependencies in core

If we *added* a Node component (say, for a future Live Canvas
equivalent), it'd be a *separate sibling project* with its own
runtime — not bundled into core Ember.

Core Ember stays Python.

---

## Where the divergence helps Ember

The fact that Ember is Python and OpenClaw is TypeScript is
**not a competitive disadvantage**. It's a positioning choice:

- **Ember serves a different operator cohort.**
- **Ember has access to Python's AI ecosystem.**
- **Ember runs better on Pi-class hardware.**
- **Ember's footprint is smaller.**

Operators who want OpenClaw's stack go to OpenClaw. Operators who
want Ember's stack come to us. Both projects can win.

---

## Lessons for cross-platform reach

### OpenClaw on Pi-class

OpenClaw *can* run on Pi (Node.js runs on Pi). But:
- Node's memory footprint is higher.
- Node startup is slower.
- Node + pnpm install on a 16GB SD card is fine, but on an 8GB
  SD card it's tight.

OpenClaw operators on Pi-class are *possible* but *not the
intended cohort*.

### Ember on workstations

Ember runs fine on workstations. But:
- Python's I/O concurrency story is worse than Node's.
- For *many* concurrent connections (a federation with 10
  nodes), Python's GIL becomes more visible.
- The asyncio ecosystem is fine for our scale but isn't Node-
  effortless.

For high-concurrency federation work (Phase 4+), Python is *enough*
but we may need to be careful.

---

## Closing

The technology stack is a *choice that shapes the operator
cohort*. OpenClaw chose TypeScript + Node and gets web-developer
ergonomics + concurrent I/O. Ember chose Python + pip and gets
Pi-class friendliness + AI ecosystem access.

Both are reasonable. Both serve their cohorts. We don't envy
OpenClaw's stack; we just learn from their *tooling discipline*
(linters, pre-commit, security scans).

The right Python tooling for the next phase: ruff (have), pytest
(have), mypy (have), pre-commit (should add), semgrep (could add),
benchmarks-in-CI (should add as Phase 4 federation lands).
