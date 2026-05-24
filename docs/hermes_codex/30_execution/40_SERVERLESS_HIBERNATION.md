---
codex_id: 40_SERVERLESS_HIBERNATION
title: Serverless Hibernation — Modal, Daytona, Vercel Sandbox Backends
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - tools/environments/__init__.py
  - tools/environments/base.py
  - tools/environments/modal.py:1-100
  - tools/environments/modal.py:172-220
  - tools/environments/daytona.py:60-210
  - tools/environments/vercel_sandbox.py
  - hermes_cli/doctor.py:1140-1213
  - hermes_cli/setup.py:683-694
  - pyproject.toml:90-95
ember_subsystem_targets: [Funi, Strengr, Brunnr]
cross_refs:
  - 30_execution/31_CROSS_PLATFORM_TACTICS
  - 30_execution/32_MULTI_DEVICE_ORCHESTRATION
  - 30_execution/33_HOT_COLD_TIERS
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Serverless Hibernation

There's a kind of cloud compute that *isn't a server*. It boots on demand, runs your code, and goes back to sleep when idle. While asleep, it costs nothing. The "cold start" is the price you pay for the "$0 idle." Modal, Daytona, Vercel Sandbox, Singularity, AWS Lambda — these all implement variants of the pattern. Hermes integrates Modal, Daytona, and Vercel Sandbox as **terminal backends**: the agent's `terminal` tool, when configured this way, executes commands inside a hibernate-able sandbox in the cloud.

I'm Eldra. Let me show you the actual integration shape — particularly how Hermes preserves session state across hibernation events via *snapshots* — then propose what Ember could do with this pattern given the Vow of Smallness.

## The Pattern: A Terminal That Lives in the Cloud

`tools/environments/` has 11 backend implementations. Most relevant for hibernation:

- `local.py` — your machine.
- `docker.py` — a Docker container (you manage the lifecycle).
- `ssh.py` — a remote server (you manage the lifecycle).
- `modal.py` — Modal Sandbox (hibernates idle, snapshots state).
- `daytona.py` — Daytona Sandbox (similar pattern).
- `vercel_sandbox.py` — Vercel Sandbox (similar pattern).
- `singularity.py` — Singularity / Apptainer (HPC).
- `managed_modal.py` — Modal under Nous-managed credentials.

The user picks via `cli-config.yaml`:

```yaml
terminal:
  backend: modal       # or daytona, vercel_sandbox, docker, ssh, local, singularity
```

Every backend implements the `BaseEnvironment` contract (in `tools/environments/base.py`):

```python
class BaseEnvironment:
    def execute(self, command: str, timeout: int) -> ExecutionResult: ...
    def write_file(self, path: str, content: str) -> None: ...
    def read_file(self, path: str) -> str: ...
    def list_files(self, path: str) -> list[str]: ...
    def cleanup(self) -> None: ...
```

The agent's `terminal` tool calls this interface. The agent doesn't know whether it's running on local Linux or a Modal Sandbox 3000 miles away. The abstraction is clean.

## Snapshots — How Hibernation Preserves State

`tools/environments/modal.py:4`:

> "Uses `Sandbox.create()` + `Sandbox.exec()` instead of the older runtime wrapper, while preserving Hermes' persistent snapshot behavior across sessions."

The key word is *persistent*. A sandbox is ephemeral by default — when it goes idle, it dies. Anything written to its filesystem dies with it. Snapshots fix this:

```python
# modal.py:32-34
_SNAPSHOT_STORE = get_hermes_home() / "modal_snapshots.json"
_DIRECT_SNAPSHOT_NAMESPACE = "direct"
```

Hermes maintains a local JSON store mapping `task_id → modal_snapshot_id`. When a new session starts:

1. Check the snapshot store for this task_id.
2. If a snapshot exists, restore from it (`Sandbox.create(image=<snapshot>)`).
3. Run the user's commands inside the restored sandbox.
4. Before sandbox idle/shutdown, take a fresh snapshot.
5. Update the JSON store with the new snapshot_id.

The snapshot includes filesystem state, installed packages, working directory, and (depending on backend support) running processes. The next session restores from where the previous one left off.

```python
# modal.py:46-66
def _direct_snapshot_key(task_id: str) -> str:
    return f"{_DIRECT_SNAPSHOT_NAMESPACE}:{task_id}"

def _get_snapshot_restore_candidate(task_id: str) -> tuple[str | None, bool]:
    snapshots = _load_snapshots()
    namespaced_key = _direct_snapshot_key(task_id)
    snapshot_id = snapshots.get(namespaced_key)
    if isinstance(snapshot_id, str) and snapshot_id:
        return snapshot_id, False
    # Legacy fallback for snapshots stored under the bare task_id key
    legacy_snapshot_id = snapshots.get(task_id)
    if isinstance(legacy_snapshot_id, str) and legacy_snapshot_id:
        return legacy_snapshot_id, True
    return None, False


def _store_direct_snapshot(task_id: str, snapshot_id: str) -> None:
    snapshots = _load_snapshots()
    snapshots[_direct_snapshot_key(task_id)] = snapshot_id
    snapshots.pop(task_id, None)   # migrate from legacy bare key
    _save_snapshots(snapshots)
```

The legacy-key fallback is a migration pattern. Older Hermes versions stored snapshots under the bare `task_id`. New versions namespace under `direct:<task_id>`. The read path checks both; the write path migrates. **A user upgrading Hermes doesn't lose their snapshots.** Vow-of-Honest-Memory analog: don't break continuity on a version bump.

The snapshot timeout is generous:

```python
# modal.py:172
_snapshot_timeout = 60  # Modal cold starts can be slow
```

60 seconds for a cold start is acceptable for a long-running agent session; less acceptable for a "I want an answer now" use case. This is the cost of hibernation.

## Daytona — Similar Shape, Different SDK

`tools/environments/daytona.py:60-71`:

```python
from daytona import (
    CreateSandboxFromImageParams,
    Daytona,
    SandboxState,
)
self._SandboxState = SandboxState
```

The `SandboxState` enum has `STOPPED`, `ARCHIVED` values (lines 209+). Daytona's lifecycle:

- `STARTED` — running.
- `STOPPED` — paused. Resumes faster than ARCHIVED.
- `ARCHIVED` — fully hibernated. Resumes slowest but cheapest to store.

Hermes can wake a STOPPED sandbox, or restore from an ARCHIVED one. The pattern mirrors Modal's: persistent state, lazy wake.

## Vercel Sandbox — The Newer Entrant

`hermes_cli/doctor.py:1163-1213` and `hermes_cli/setup.py:683-694` show Vercel Sandbox integration. The doctor block warns:

> "Vercel Sandbox does not support custom container_disk; use the shared default 51200"

Different backends have different feature matrices. Hermes's `doctor` command tells the user which features are available where. **Capability-aware doctor output is a real-world UX win** for users picking a backend.

## What This Enables (For Hermes)

Three real scenarios this pattern serves:

1. **The Pi user with cloud compute.** Pi runs the agent loop; sandbox in Modal runs `apt install`, `npm build`, `cargo run`. The Pi's tiny CPU doesn't have to compile rustc.
2. **The privacy-conscious user.** Local agent reasoning, isolated sandbox for everything that needs to "execute untrusted code" or "read user PII." Sandbox dies when idle; PII doesn't leak into a long-running container.
3. **The Nous-managed user.** `managed_modal.py` exposes a Nous-curated tier where Modal credentials are pooled at the org level. The user doesn't deal with Modal billing.

The cost structure: idle = $0, active = pennies per hour. For a user whose agent runs interactively for an hour a day and idle the rest, the bill is < $1/mo.

## What This Means for Ember — Choose Your Battle

Ember's Vow of Smallness says the Pi should be enough. Hermes's backend zoo is *not* something Ember should ship.

But the abstraction itself — *a terminal-tool backend that isn't necessarily local* — is something Ember might want, *with strict limits*. Two scenarios where it makes sense:

**Scenario A — Ember as orchestrator.** The user has Ember on a Pi. They have a workstation peer in the [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]] mesh. The "terminal" actions go to the workstation; reasoning stays on the Pi. This is the *mesh dispatch* covered by Strengr Mesh. No serverless involved.

**Scenario B — Ember asks the user to spin up sandbox compute.** The user wants Ember to compile a Rust binary. The Pi can't. The user has no workstation. They explicitly say `ember sandbox enable modal`. Now Ember can dispatch heavy commands to a Modal Sandbox.

Scenario B is the legitimate use case for Hermes's pattern. It's an *opt-in cloud burst*, not a default mode.

### Proposed Ember API

```python
# src/ember/spark/funi/tools/terminal/backends/base.py
class TerminalBackend(Protocol):
    name: str

    def execute(self, command: str, *, timeout: float = 60.0) -> ExecutionResult: ...
    def write_file(self, path: str, content: str) -> None: ...
    def read_file(self, path: str) -> str: ...
    def list_files(self, path: str) -> list[str]: ...
    def cleanup(self) -> None: ...

class LocalTerminalBackend(TerminalBackend): ...     # default; existing
class SshTerminalBackend(TerminalBackend): ...       # SSH to a peer or remote host (v2)
class ModalTerminalBackend(TerminalBackend): ...     # serverless burst (v3, opt-in)
```

The backend abstraction lives under `funi/tools/terminal/backends/` (the terminal tool is a Funi-side capability — local model decides when to call it). Local is default. SSH and Modal are gated behind:

```yaml
# ember.yaml
funi:
  terminal:
    backend: local    # "local" | "ssh:<host>" | "modal" | "daytona"
    ssh:
      host: workstation
      port: 22
      key: ~/.ssh/id_ed25519
    modal:
      app_name: ember-burst
      app_image: python:3.14
      timeout: 300
      auto_hibernate_after: 60   # seconds idle before snapshot+stop
      snapshot_path: ~/.ember/state/modal_snapshots.json
```

### Snapshot pattern — adopt verbatim

If/when Ember ships a Modal backend, the snapshot JSON pattern from `modal.py:32-80` is exact-transferable. The structure:

```python
# src/ember/spark/funi/tools/terminal/backends/modal.py
_SNAPSHOT_STORE = lambda: get_ember_home() / "state" / "modal_snapshots.json"
_SNAPSHOT_NAMESPACE = "direct"

def _snapshot_key(task_id: str) -> str:
    return f"{_SNAPSHOT_NAMESPACE}:{task_id}"

def load_snapshots() -> dict[str, str]: ...
def save_snapshots(data: dict[str, str]) -> None: ...
def take_snapshot(sandbox: Sandbox, task_id: str) -> str: ...
def restore_from_snapshot(task_id: str) -> Sandbox | None: ...
```

Atomic writes via `tempfile.NamedTemporaryFile(delete=False) + os.replace()` (already an Ember pattern per [[docs/CROSS_PLATFORM_PLAN.md]]).

### What Ember should NOT ship

- **Daytona, Vercel Sandbox, Singularity, managed Modal as separate backends.** Each is hundreds of lines of integration code that maps to a subscription a Pi user is unlikely to have.
- **Modal as a default.** If someone wants it, they `pip install 'ember-agent[modal]'` and opt in via config. No discovery, no automatic enabling.
- **A `managed_*` tier.** Vow of Public-Friendliness. Ember doesn't run a managed credential service.

### What about the Well in the cloud?

The brief asks: "How this could let Ember's Well run cheaply in cloud while Spark runs on Pi."

This is real. Brunnr is pluggable. The Pi's local sqlite_vec Well can be ~hundreds of MB to GBs. A cloud pgvector instance (Supabase free tier, Neon free tier, self-hosted on a $5 VPS) can hold the same data with better performance — and *the network round-trip from Pi to a cloud postgres is faster than a local SQLite scan on large embeddings*.

Two complementary patterns:

**Pattern A — Cloud Well, local Spark.** User runs Funi on the Pi (where the chat actually feels responsive). The Well lives in a pgvector instance in the cloud. Strengr's tether handles auth + retry. The Pi's RAM doesn't have to hold the embedding index. This is just Brunnr's pgvector adapter pointed at a remote DSN — no new code needed.

**Pattern B — Serverless Well, hibernate when idle.** Same as Pattern A, but the pgvector instance is on Neon or Supabase free tier which auto-suspends after 5 minutes of idle. Cold-start cost ~2-5 seconds on first query. For an agent the user invokes a few times a day, this is fine.

Pattern A is shipping today (Vow of Pluggable Storage already allows it). Pattern B is operator-side configuration of the user's chosen pgvector host; Ember doesn't have to do anything new to support it.

### What about hibernating Ember itself?

A more exotic pattern: deploy Ember to a serverless function (Vercel Functions, AWS Lambda, Modal endpoints). The function wakes on user request, processes one turn, hibernates.

This is NOT a fit for Ember v1, for two reasons:

1. **Statefulness.** Ember's chat REPL is conversational. Lambda's 15-minute hard limit and cold-start times break the interaction model.
2. **Vow of Smallness.** A Pi user with their data on a Pi is the canonical Ember user. Cloud-only Ember is a separate persona.

Reserve this for a hypothetical Ember-as-API mode that comes after the v1 core lands.

### Vows on the line

- **Vow of Smallness** — at risk if Ember ships multiple cloud backends. Mitigation: only Local in v1; SSH and Modal as opt-in extras.
- **Vow of Pluggable Storage** — strengthened. The cloud-Well pattern (Pattern A above) is a first-class use case.
- **Vow of Graceful Offline** — preserved. The local backend always works without network. Serverless backends fail loudly when offline; user sees "modal sandbox unreachable, defaulting to local."
- **Vow of Tethered Grounding** — preserved. The Well is still the source of truth, whether local or remote.
- **Vow of Modular Authorship** — strengthened. Each backend is a sibling module; a broken Modal SDK doesn't crash local execution.

### Concrete deliverables

For v1: **none**. Local terminal backend already works; no new backend ships.

For post-v1 (gated on demand):

1. `src/ember/spark/funi/tools/terminal/backends/ssh.py` — SSH to a peer or remote host. ~300 lines.
2. `src/ember/spark/funi/tools/terminal/backends/modal.py` — Modal Sandbox with snapshot store. ~500 lines.
3. `pyproject.toml` extras: `ssh = ["paramiko==..."]`, `modal = ["modal==..."]`.
4. `src/ember/munnr/doctor.py` — capability-aware diagnostic command showing which backends are configured and healthy.

Each is opt-in. None blocks v1.

### The cloud-Well shipping path

Brunnr already supports pgvector. Document the Pattern-A workflow in a how-to guide:

```
# docs/cookbooks/cloud-well-pi-spark.md
Run Ember's Spark on a Pi while the Well lives on a free-tier pgvector host.

1. Sign up for Neon / Supabase / Render Postgres.
2. Create a pgvector-enabled database.
3. Set EMBER_BRUNNR_BACKEND=pgvector and EMBER_BRUNNR_DSN=postgres://...
4. Run `ember well init`.
5. Run `ember well ingest ~/Documents`.
6. Run `ember chat` — queries hit the cloud Well over Strengr.
```

That's zero new code and a real Pi-friendly cloud burst story. Vow of Smallness paid; user empowered.

### Where to read next

- [[30_execution/31_CROSS_PLATFORM_TACTICS]] — the local-first stance these backends extend.
- [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]] — Strengr Mesh as the *first* off-device dispatch surface.
- [[30_execution/33_HOT_COLD_TIERS]] — how a Pi-tier user reaches workstation-tier capabilities.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs (none for v1, sketch for post-v1).

A sleeping server costs nothing. So does a server you don't ship. Pick your fights. — Eldra.
