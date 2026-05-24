---
codex_id: 16_TUI_GATEWAY_BACKENDS
title: The Seven Backends — Where Hermes Actually Runs the Command
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - tools/environments/__init__.py
  - tools/environments/base.py:1-100
  - tools/environments/base.py:81-94
  - tools/environments/local.py:1-60
  - tools/environments/docker.py:1-50
  - tools/environments/ssh.py:1-40
  - tools/environments/modal.py:1-60
  - tools/environments/managed_modal.py
  - tools/environments/modal_utils.py
  - tools/environments/daytona.py
  - tools/environments/singularity.py:1-40
  - tools/environments/vercel_sandbox.py
  - tools/environments/file_sync.py
  - tools/terminal_tool.py
  - hermes_state.py:1-200
  - tui_gateway/server.py:1-100
  - AGENTS.md:200-260
ember_subsystem_targets: [Verkfæri]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/13_TOOLS_SUBSYSTEM
  - 30_execution/31_CROSS_PLATFORM_TACTICS
  - 30_execution/40_SERVERLESS_HIBERNATION
  - 50_verification/53_CRASH_PROOFING_PATTERNS
---

# The Seven Backends
## Where Hermes Actually Runs the Command

*— Rúnhild Svartdóttir, Architect*

> *A tool is a verb; an environment is a body. The same verb has different consequences depending on the body it animates. The architect's job is to keep the verb constant so the agent's reasoning travels unchanged, and to keep the bodies separable so the user can choose which fire to walk into.*

The `terminal` tool is *one* tool in the agent's schema. Behind it stand seven execution environments: **local**, **docker**, **ssh**, **modal** (with two sub-modes), **daytona**, **singularity** (Apptainer), and **vercel_sandbox**. The agent does not know which body is animating its commands — it just calls `terminal(command="...")` and gets back stdout, stderr, and exit code. The user chooses the body via configuration. This doc maps the bodies.

> **Note on the doc slug.** The MANIFEST slug `16_TUI_GATEWAY_BACKENDS` is misleading — these are *terminal-execution* backends in `tools/environments/`, not the `tui_gateway/` Ink-TUI backend. The brief is unambiguous about content. We document the seven execution environments here; the `tui_gateway/` architecture is also briefly covered at the end because it shares the "headless backend with a separate front-end" shape.

---

## 1. The Common Contract

`tools/environments/base.py:1-100` defines the abstract base. The header docstring is precise (`tools/environments/base.py:1-7`):

> *"Unified spawn-per-call model: every command spawns a fresh `bash -c` process. A session snapshot (env vars, functions, aliases) is captured once at init and re-sourced before each command. CWD persists via in-band stdout markers (remote) or a temp file (local)."*

Every environment is a `BaseEnvironment` subclass that implements:

- `execute(command, timeout, ...) -> result` — the heart
- `init()` — capture the session snapshot
- `cleanup()` — release resources
- `get_cwd()`, `set_cwd(path)` — CWD tracking
- `sync_file(local, remote)` — for remote environments

The shape is **spawn-per-call** rather than long-lived shell. Every command opens its own bash; the session snapshot (env vars, functions, aliases) is re-sourced at the top of each invocation. This avoids the *single-shell-state-corrupted* failure mode that plagues long-lived PTY-based agents.

Three shared helpers:
- `tools/environments/base.py:_pipe_stdin` — pipe stdin into the spawned process
- `tools/environments/base.py:_popen_bash` — uniform Popen with `bash -c`
- `tools/environments/file_sync.py` — `FileSyncManager`, `iter_sync_files`, `quoted_mkdir_command`, `quoted_rm_command`, `unique_parent_dirs` — for getting files in and out of remote environments

The sandbox root (`tools/environments/base.py:81-93`) is `get_sandbox_dir()` — `TERMINAL_SANDBOX_DIR` env override or `{HERMES_HOME}/sandboxes/`. Every environment that needs host-side storage lives under here.

Activity reporting (`tools/environments/base.py:46-78`) is thread-local: the agent sets a callback before a tool call so long-running `_wait_for_process` loops can report liveness ("still running, 30s elapsed") back to the gateway without polling.

---

## 2. The Seven Bodies

### 2.1 Local (`tools/environments/local.py`, 677 lines)

**Isolation:** None — the command runs as the Hermes process's user, in the Hermes process's filesystem view.

**Persistence:** Everything persists by definition (this is the host).

**Cost model:** Free. CPU/RAM is whatever the host has.

**Quirks:**
- `_msys_to_windows_path` (`tools/environments/local.py:22-39`) translates Git Bash POSIX paths (`/c/Users/x`) to native Windows form (`C:\Users\x`). This is the *Windows path crisis* of `pwd` returning POSIX paths that `os.path.isdir` rejects.
- `_resolve_safe_cwd` (`tools/environments/local.py:42-60`) walks up the path tree if cwd has been deleted by a previous tool call (issue #17558). Without this, every subsequent terminal call would wedge.
- `windows_hide_flags` from `hermes_cli/_subprocess_compat.py` prevents the brief CMD window flash on Windows.

**When to use:** Default. Pi, dev laptop, server, anywhere Hermes is allowed to run shell commands directly.

### 2.2 Docker (`tools/environments/docker.py`, 656 lines)

**Isolation:** Strong. Container with `cap-drop ALL`, `no-new-privileges`, PID limit, configurable CPU/memory/disk limits, no network unless explicit.

**Persistence:** Optional via bind mounts. Default is ephemeral.

**Cost model:** Free (uses host's Docker daemon). CPU/RAM consumed by container.

**Quirks:**
- `_DOCKER_SEARCH_PATHS` (`tools/environments/docker.py:26-30`) probes Docker Desktop's common install paths when `docker` isn't in PATH — `/usr/local/bin`, `/opt/homebrew/bin`, `/Applications/Docker.app/Contents/Resources/bin`.
- `_normalize_forward_env_names` (`tools/environments/docker.py:36-50`) validates the explicit env-var allow list passed to the container — refuses non-string entries, refuses invalid POSIX identifiers.
- The container image is configurable (`terminal.docker_image`); default is a Hermes-prepared image with curl, git, common build tools.

**When to use:** Operator wants isolation but the cost of network round-trips for remote sandboxes is unacceptable. Typical for "I'm running Hermes on my laptop but I want it to compile some sketchy code without polluting my Python env."

### 2.3 SSH (`tools/environments/ssh.py`, 308 lines)

**Isolation:** Whatever the remote host enforces.

**Persistence:** Full (this *is* the remote host).

**Cost model:** Free (your own host). Latency: depends on network.

**Quirks:**
- `_ensure_ssh_available` (`tools/environments/ssh.py:24-33`) fails fast if `ssh` or `scp` is missing, with an actionable install message.
- **ControlMaster connection persistence** is the key performance optimization. Each session opens *one* SSH master connection (`-o ControlMaster=auto -o ControlPath=...`) that is reused for every subsequent command. Without this, every terminal call would pay the SSH handshake cost (~500 ms).
- File sync via `scp` + `FileSyncManager` from `tools/environments/file_sync.py`.

**When to use:** Operator has a remote dev box and wants Hermes to drive it. Pi-Hermes driving a workstation across the household tailnet is a *natural fit* for Ember's Strengr.

### 2.4 Modal (`tools/environments/modal.py`, 478 lines + `managed_modal.py`, 282 lines)

**Isolation:** Container-level (Modal's `Sandbox` primitive).

**Persistence:** *Across sessions* via Modal Sandbox snapshots — the snapshot ID is stored in `~/.hermes/modal_snapshots.json` (`tools/environments/modal.py:34`) and reused on next session. The sandbox can be cold-started from snapshot in seconds.

**Cost model:** Pay-per-second for sandbox runtime, plus image storage. **Hibernates when idle** — the sandbox is automatically suspended when the agent isn't issuing commands.

**Two sub-modes:**
- **`direct`** — Hermes uses Modal SDK with the user's Modal token; sandboxes are billed to the user's account.
- **`managed`** (Nous-managed) — Hermes uses a Nous Research-managed Modal account; the user pays Nous via a subscription rather than holding Modal credentials.

**Quirks:**
- Uses `Sandbox.create()` + `Sandbox.exec()` directly (not the older runtime wrapper) for predictable behavior.
- Snapshot key is `direct:<task_id>` (`tools/environments/modal.py:46-47`) — namespaced to prevent legacy snapshot collisions.
- `tools/environments/modal_utils.py` has shared helpers.

**When to use:** Operator wants serverless execution. Pi-Hermes can drive a Modal sandbox with full GPU/CPU access without the Pi needing the resources. This is one of the most powerful Hermes patterns — a small device commanding a powerful remote body.

### 2.5 Daytona (`tools/environments/daytona.py`, 270 lines)

**Isolation:** Container-level (Daytona's workspace primitive).

**Persistence:** Workspace persists across sessions; can hibernate.

**Cost model:** Daytona's pricing.

**Quirks:**
- Daytona's API is reasonable but young; the adapter handles transient API errors with retry.

**When to use:** Operator already uses Daytona for their cloud dev environments. Similar use case to Modal but with a different vendor.

### 2.6 Singularity / Apptainer (`tools/environments/singularity.py`, 262 lines)

**Isolation:** Container-level with `--containall`, `--no-home`, capability dropping.

**Persistence:** Optional via *writable overlay directories* — overlay files survive across sessions.

**Cost model:** Free (HPC institutions typically have this installed).

**Quirks:**
- `_find_singularity_executable` (`tools/environments/singularity.py:30-40`) probes for `apptainer` first (the renamed Singularity), then `singularity`. Useful actionable error.
- Snapshot store at `~/.hermes/singularity_snapshots.json`.

**When to use:** HPC environments where Docker is forbidden but Singularity/Apptainer is the institutionally sanctioned container runtime. Hermes runs on a login node and drives Singularity for actual computation.

### 2.7 Vercel Sandbox (`tools/environments/vercel_sandbox.py`, 654 lines)

**Isolation:** Vercel's sandbox primitive (V8 isolate-based, browser-style sandboxing).

**Persistence:** Session-level; sandbox is destroyed at session end.

**Cost model:** Vercel pricing.

**When to use:** Web-focused workflows. Vercel's sandbox is JS/edge-friendly and integrates with Vercel deployment.

---

## 3. The CWD Persistence Trick

The `BaseEnvironment` spawn-per-call model has one annoying problem: when you spawn a fresh bash each time, `cd /foo` does not persist. Hermes solves this with two patterns:

**Local:** A temp file (`{HERMES_HOME}/sandboxes/<task>/cwd.txt`) holds the current cwd. The bash script for the next command starts with `cd "$(cat ~/.hermes/sandboxes/<task>/cwd.txt)"`.

**Remote (SSH, Modal, Daytona, Singularity, Vercel):** An *in-band stdout marker*. The script ends with `echo "__HERMES_CWD_MARKER__:$(pwd)"`. The wait-loop parses the marker out of stdout and records the new cwd. The marker is stripped from the user-visible output.

This is **clever** because it makes the cwd a *side effect* of the command rather than a separate round-trip. One command, two pieces of state recovered: exit code and cwd.

For Ember (which today has no terminal tool), this pattern is preserved for the future. When a terminal tool ships, the spawn-per-call + cwd-marker pattern is the right shape.

---

## 4. File Sync (`tools/environments/file_sync.py`, 402 lines)

For remote environments, files need to be pushed in and pulled out. `FileSyncManager` is the orchestrator. Helpers:

- `iter_sync_files(root)` — walk a tree, yielding paths to sync
- `quoted_mkdir_command(paths)` — generate a `mkdir -p` command that handles paths with spaces / special chars
- `quoted_rm_command(paths)` — same shape for `rm`
- `unique_parent_dirs(paths)` — deduplicate parent dirs for batch mkdir

The sync is *incremental* via mtime + size checks. Reduces SSH/SCP round-trips dramatically for projects with thousands of small files.

---

## 5. The Factory

`tools/terminal_tool.py` (which is too large to dwell on here) has a factory function `_create_environment(env_type)` that returns the right `BaseEnvironment` instance based on `TERMINAL_ENV` (config or env var):

- `local` → `LocalEnvironment`
- `docker` → `DockerEnvironment`
- `ssh` → `SSHEnvironment`
- `modal` → `ModalEnvironment` or `ManagedModalEnvironment` (based on `terminal.modal_mode`)
- `daytona` → `DaytonaEnvironment`
- `singularity` → `SingularityEnvironment`
- `vercel_sandbox` → `VercelSandboxEnvironment`

Switching environments is *zero code change*: the operator sets `terminal.env: docker` in `config.yaml` and the next session uses Docker. The agent does not know.

This is the **Vow of Pluggable Storage**'s execution-side cousin. Vow of Pluggable Execution Bodies, if you will.

---

## 6. Why the Architecture Holds

What keeps this architecture coherent across seven body types is the **commitment to spawn-per-call** + the **commitment to one `BaseEnvironment` ABC**. No environment is special. No environment short-circuits the contract. No environment "needs" a different tool surface.

The cost of this commitment is that you cannot easily share state between bash invocations. The benefit is that one bash invocation crashing does not poison the next one.

Hermes's *long-running* commands (background processes, daemons started via `terminal(background=True)`) are tracked separately in `tools/process_registry.py` — they live outside the spawn-per-call discipline because they need to. But interactive terminal use *always* spawns fresh.

---

## 7. The TUI Gateway (Brief Note)

`tui_gateway/` is *not* an execution environment. It is a *front-end* architecture: the Ink/React TUI talks to a Python `tui_gateway` daemon over newline-delimited JSON-RPC on stdio (`tui_gateway/server.py:21-27`). The daemon constructs `AIAgent` instances and drives them. The Ink side renders.

The relevant architectural pattern: **headless backend, swappable front-end.** The same `AIAgent` powers the classic `cli.py` interactive loop *and* the JSON-RPC `tui_gateway`. The choice of front-end is the operator's. The agent doesn't know.

For Ember, the TUI gateway is *future work* (Munnr's CLI is enough for slice 1-2). When it arrives, the architectural pattern is: **a JSON-RPC daemon that drives Funi/Brunnr/Strengr, with an Ink-style TUI talking to it.** Cite `tui_gateway/server.py:21-27` and `AGENTS.md:200-260` as the canonical model.

---

## What This Means for Ember

The seven backends are architecturally beautiful but functionally **out of scope** for Ember's slice plan. The Vow of Smallness rules out Modal/Daytona/Vercel (not Pi-friendly); the Vow of Public-Friendliness rules out Singularity (HPC-only). Docker and SSH are *plausible* future backends. Local is the only one Ember strictly needs.

But the *pattern* is what Ember inherits:

1. **Adopt the `BaseEnvironment` ABC shape** for when Ember acquires a terminal tool. Spawn-per-call. Session snapshot. CWD via in-band marker. One ABC, many implementations, factory dispatch by config. Cite `tools/environments/base.py:1-100`.

2. **Adopt `_resolve_safe_cwd` (`tools/environments/local.py:42-60`).** When cwd disappears mid-session (because the agent's previous command rmrf'd it), walking up the tree rather than crashing is the right recovery. Apply this to any Ember code that uses cwd as state.

3. **Adopt `_msys_to_windows_path` (`tools/environments/local.py:22-39`).** Windows + Git Bash is a real cross-platform target the Vow of Smallness reaches. The path translation is six lines; copy it.

4. **Adopt the *idea* of remote bodies for Pi-Hermes driving a workstation.** SSH is the cheapest realization: a Pi running Ember can drive a workstation across the household tailnet. The workstation does the heavy lifting; the Pi does the conversation. This is a *natural* Strengr extension and aligns with the operator's existing setup (per `MEMORY.md` — the operator's tailnet has a Gungnir node serving as the canonical Well).

5. **Adopt the `tui_gateway/` shape for any future TUI.** Headless Python daemon + Ink-style TUI client + JSON-RPC over stdio. The pattern is portable; the implementation is delayed until Ember's slice plan calls for it.

6. **Refuse the rest.** Docker, Singularity, Vercel, Daytona, Modal — all of them — are out of slice 1-2 scope. They are *patterns to remember*, not patterns to ship.

### Concrete proposals

1. **When Ember acquires a terminal tool, ship it with `local` only.** Use `BaseEnvironment` as the ABC. Documents at `src/ember/spark/verkfaeri/environments/base.py`, `local.py`. Plan `ssh.py` for the slice when Strengr-side remote-execution becomes a Vow.

2. **Adopt `tools/environments/file_sync.py`'s incremental-sync helpers** when remote execution arrives. mtime + size delta; quoted commands; batch mkdir. The 400 lines port without ceremony.

3. **Document the spawn-per-call discipline as a Vow-aligned pattern.** It is the cleanest execution-state-management discipline I have seen in any agent system. The Vow of Modular Authorship says "subsystems must be individually failable"; spawn-per-call ensures one tool call crashing cannot poison the next.

**Affected True Names:** **Verkfæri** (the tool framework hosts the execution-environment dispatch). **Strengr** (when SSH-based remote execution arrives, the connection lives on the Thread).

**Vows reinforced:**
- **Vow of Modular Authorship** — each environment a separate file, each failure isolated.
- **Vow of Flexible Roots** — sandbox dir is `{HERMES_HOME}/sandboxes/`, not hardcoded.
- **Vow of Smallness** — local-only fits the Pi target.

**Vows at risk if mis-ported:**
- **Vow of Smallness** — adopting Modal/Daytona/Vercel would require remote-account dependencies on a device that may have no internet.
- **Vow of Pluggable Storage** — the seven-environment pattern is *also* a precedent for "many backends behind one contract"; reinforces Brunnr's pluggability.

The body of a tool matters less than the contract that animates it. Ember inherits the contract — and starts with the one body she truly needs.
