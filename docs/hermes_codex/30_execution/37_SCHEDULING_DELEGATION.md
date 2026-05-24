---
codex_id: 37_SCHEDULING_DELEGATION
title: Scheduling and Delegation — Background Work, Cron, Subagent Dispatch
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - cron/jobs.py:1-80
  - cron/jobs.py:721-1000
  - cron/scheduler.py:23-30
  - cron/scheduler.py:1134-1252
  - cron/scheduler.py:1787-1900
  - batch_runner.py:527-810
  - tools/delegate_tool.py:1918-2050
  - agent/iteration_budget.py:1-62
ember_subsystem_targets: [Smiðja, Strengr, Munnr]
cross_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/32_MULTI_DEVICE_ORCHESTRATION
  - 30_execution/40_SERVERLESS_HIBERNATION
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Scheduling and Delegation

Some work isn't meant to happen while you watch. A Smiðja ingest of 5,000 documents. A Brunnr health check. A weekly curator pass. A "remind me at 6pm" alert. Hermes ships three different scheduling/delegation mechanisms — `cron/`, `batch_runner.py`, `tools/delegate_tool.py` — each tuned to a different work shape. I'm Eldra. I'll show you each one, then sketch how Ember should adopt the patterns without ballooning into a daemon farm.

## Three Work Shapes

| Shape | Hermes module | Trigger | Lives where | Examples |
|---|---|---|---|---|
| **Recurring scheduled** | `cron/` | crontab expression / interval | Gateway tick loop or standalone daemon | Daily report, weekly cleanup, periodic health check |
| **Batch parallel** | `batch_runner.py` | one-shot CLI invocation | Operator's machine | Run an eval over 1,000 prompts; generate training trajectories |
| **In-session subagent** | `tools/delegate_tool.py` | mid-conversation tool call | Same process, sibling threads | "Review these 10 PRs in parallel"; "search the web AND search the codebase" |

These are not interchangeable. A "remind me at 6pm" is cron. A "convert every PDF in this folder" is batch. A "read these 5 files and synthesize a summary" is subagent. Hermes ships all three.

## Cron — Recurring Scheduled Work

`cron/jobs.py:37-39` shows the storage:

```python
HERMES_DIR = get_hermes_home().resolve()
CRON_DIR = HERMES_DIR / "cron"
JOBS_FILE = CRON_DIR / "jobs.json"
```

Jobs are persisted as JSON. The schema (inferred from `_normalize_skill_list`, `_coerce_job_text`, etc.) carries:

- `id` (UUID)
- `name` (human label)
- `cron` (crontab expression OR `interval` seconds)
- `prompt` (the task text the agent will execute, or)
- `script` (a shell script path, when `no_agent: true`)
- `skills` / `skill` (preloaded skills for the run)
- `enabled_toolsets` (per-job toolset override)
- `next_run_at` (next due timestamp)
- `last_run_at`, `last_success`, `last_error`
- `delivery` (target platform + chat_id)
- `workdir` (cwd for the run)
- `no_agent` (boolean — script-only path)
- `wakeAgent` (gate-out keyword scan)

The `no_agent` flag is the standout. From `cron/scheduler.py:1152-1167`:

> "no_agent short-circuit — the script IS the job, no LLM involvement. This mirrors the classic 'run a bash script on a timer, send its stdout to telegram' watchdog pattern. The agent path is skipped entirely: no AIAgent, no prompt, no tool loop, no token spend."

A user who wants `disk-usage > 80%` alerts at 9am every day shouldn't have to spawn an LLM for that. The script's stdout becomes the delivered message. Empty stdout = silent run. Non-zero exit = error alert. Brilliant separation.

### The Tick

`cron/scheduler.py:1787` is the heart of the cron loop:

```python
def tick(verbose: bool = True, adapters=None, loop=None) -> int:
    """
    Check and run all due jobs.

    Uses a file lock so only one tick runs at a time, even if the gateway's
    in-process ticker and a standalone daemon or manual tick overlap.
    """
```

The lock pattern is the cross-platform `fcntl`/`msvcrt` polymorphism from [[30_execution/31_CROSS_PLATFORM_TACTICS]]. Multiple processes can call `tick()`; only one wins; the others log "another instance holds the lock" and return 0.

Inside the lock:

```python
due_jobs = get_due_jobs()
...
# Advance next_run_at for all recurring jobs FIRST, under the file lock,
# before any execution begins.  This preserves at-most-once semantics.
for job in due_jobs:
    advance_next_run(job["id"])
```

**At-most-once semantics.** If a tick crashes mid-execution, the next tick won't re-run the same due jobs because `next_run_at` was already advanced. The trade-off is "occasionally miss a tick" instead of "occasionally double-run." For most cron use cases, miss-once is the right failure mode — a re-run of a delivery would spam the user.

Then parallel dispatch with `ThreadPoolExecutor` (lines 1838-1860):

```python
_max_workers = None  # default: unbounded
# env > config > unbounded
...
if verbose:
    logger.info("Running %d job(s) in parallel (max_workers=%s)", ...)
```

If 5 jobs are due, all 5 run concurrently (subject to `HERMES_CRON_MAX_PARALLEL` env var or `cron.max_parallel_jobs` config). Each gets its own thread. Each job is wrapped in `_process_job()` which executes, saves output, delivers, and marks the run.

### Delivery integration

The cron module is gateway-aware:

```python
def tick(verbose=True, adapters=None, loop=None) -> int:
    ...
```

`adapters` is a dict of `Platform → live adapter` injected by the running gateway. If the gateway is up, deliveries go through live transports (websocket → bot). If the gateway is down or cron runs standalone, the adapters are None and the delivery falls back to (typically) a queued local write.

### Prompt injection guard at scheduling time

Lines 47-58:

```python
class CronPromptInjectionBlocked(Exception):
    """Raised by _build_job_prompt when the fully-assembled prompt trips the
    injection scanner... A malicious skill could carry an injection payload
    that reached the non-interactive (auto-approve) cron agent."""
```

Cron jobs typically run with auto-approve (no human in the loop). A malicious skill or prompt would be especially dangerous in that mode. The scan happens at *prompt-assembly time* — after skills are loaded — so the full payload is checked before the LLM call. Defense in depth.

## Batch Runner — One-Shot Parallel Throughput

`batch_runner.py` (1,321 lines) is the operator-facing batch tool. Class `BatchRunner` at line 527. It:

1. Loads a dataset of prompts (line 642).
2. Splits into batches (line 674).
3. Runs each prompt through a fresh AIAgent (line 244, `_process_single_prompt`).
4. Checkpoints progress (line 715).
5. Filters out already-completed prompts on resume (line 732).

The checkpoint pattern is interesting (`_scan_completed_prompts_by_content` at line 732):

```python
def _scan_completed_prompts_by_content(self) -> set:
    """Scan output files and identify prompts that have already been completed,
    by hashing prompt content. Survives renames/reorderings of the input dataset.
    """
```

Completed-prompt identification is by *content hash*, not by index. If the operator inserts a new prompt at line 50, the batch runner doesn't re-run lines 51-N. This is a small but crucial UX detail for long-running batches.

The runner is operator-only — there's no equivalent surface for end-users. A user running Ember locally on a Pi never invokes a batch runner directly. So Ember's design choice is: do we expose this? My answer below: **no for v1**, but the *primitive* should exist so Smiðja can use it internally.

## Subagent Delegation — In-Session Parallelism

This is fully covered in [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]]. Brief recap: `tools/delegate_tool.py:1918` spawns child AIAgents with isolated context, restricted toolsets, own task_ids, own iteration budgets. Parent blocks until children complete.

The relationship to scheduling: subagent delegation is *synchronous in-session* delegation. The user's session waits. Cron is *asynchronous out-of-session* delegation. The user is not present. Batch runner is *batch-mode operator-driven* delegation. The user is absent for the duration but watching the dashboard. Three modes, three patterns.

## What This Means for Ember

Ember needs all three patterns. But scaled to Pi-and-up hardware and Vow-of-Public-Friendliness defaults.

### Smiðja's batch ingest

The Hermes `BatchRunner` pattern maps onto Smiðja's existing ingest job. Today Smiðja does an iterate-over-files-and-embed; with the BatchRunner pattern, it becomes:

```python
# src/ember/smiðja/batch.py
@dataclass(frozen=True)
class IngestBatchConfig:
    batch_size: int = 100              # chunks per batch (tier-aware)
    num_workers: int = 4               # threads
    max_concurrent_embed: int = 8      # concurrent embed API calls
    checkpoint_every: int = 100        # batches
    skip_under_target: bool = True
    per_batch_timeout: float = 300.0

class IngestRunner:
    def __init__(self, config: IngestBatchConfig): ...
    def _load_checkpoint(self) -> dict: ...
    def _save_checkpoint(self, data: dict) -> None: ...
    def _scan_completed_chunks_by_content_hash(self) -> set[str]: ...
    def run(self, paths: list[Path], *, resume: bool = False) -> IngestReport: ...
```

The content-hash resume is non-negotiable. If an ingest of 5,000 PDFs is interrupted at 3,200, the resume must skip the first 3,200 without re-embedding them. Per-content-hash is the only way to survive a re-ordered input.

### Munnr's cron — but smaller

Ember's user is likely to want some recurring jobs. "Remind me to take a break every 90 minutes." "Email me the daily Brunnr health every morning at 8am." But Ember's user is *not* operating a 24/7 gateway with cross-platform delivery to Slack/Discord/Telegram. Trim the cron stack:

```python
# src/ember/munnr/cron/jobs.py
@dataclass(frozen=True)
class CronJob:
    id: str
    name: str
    schedule: str           # crontab expression
    prompt: str | None = None
    script_path: Path | None = None     # mutually exclusive with prompt
    delivery: Literal["stdout", "notify", "file"] = "stdout"
    workdir: Path | None = None
    enabled: bool = True
    next_run_at: float | None = None
    last_run_at: float | None = None
    last_success: bool | None = None
    skills: list[str] = field(default_factory=list)
```

Three delivery surfaces, all local:

- `stdout`: write to a log file under `~/.ember/cron/output/<job_id>/<ts>.md`.
- `notify`: OS notification via `notify-send` (Linux), `osascript` (macOS), or a fallback `print()` to a tail-able log.
- `file`: write to a specified file.

No Telegram/Slack/Discord adapter in v1. Vow of Smallness — if the user wants gateway delivery, they layer it on themselves.

### Tick loop in Munnr

```python
# src/ember/munnr/cron/scheduler.py
def tick(*, verbose: bool = True) -> int:
    """Run all due cron jobs. Returns number of jobs executed.

    Uses a cross-platform file lock so multiple tick callers don't double-run.
    Advances next_run_at under lock before execution (at-most-once semantics).
    """
```

The cross-platform lock pattern from `cron/scheduler.py:23-30` transfers verbatim:

```python
try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
```

`ember cron tick` calls it once. For continuous scheduling, `ember cron daemon` runs a 60-second loop. Optional. The user who hates background processes runs `ember cron tick` from their *own* cron / launchd / Task Scheduler.

This is important. **Ember does not require a daemon to schedule.** Linux user with a system cron? They write `*/5 * * * * ember cron tick` themselves and Ember plays nice. Mac user with launchd? Same. Windows user with Task Scheduler? Same. Pi user who wants Ember always-on? They run `ember cron daemon`. Choice.

### no_agent short-circuit

Adopt verbatim. The user who wants `df -h | grep -E "9[0-9]%|100%"` at 9am every day shouldn't burn LLM tokens. Pattern:

```python
job = CronJob(
    name="disk-usage-alert",
    schedule="0 9 * * *",
    script_path=Path("~/.ember/cron/scripts/disk-check.sh"),
    delivery="notify",
)
```

If `script_path` is set and `prompt` is unset, the job runs as a subprocess. Stdout becomes the notification. Same semantics as Hermes.

### Subagent delegation — minimal in v1

Ember v1 likely doesn't need user-facing `delegate_task`. The work shapes that benefit from it (parallel PR review, multi-file search) aren't core Ember workflows. The internal need is real: Smiðja's batch ingest *will* want to dispatch chunks to multiple Funi workers.

Proposal: build the *iteration budget* primitive (`IterationBudget` from `agent/iteration_budget.py:1-62`, adopted verbatim) and the *isolated subagent* primitive but **don't expose `delegate_task` as a user-callable tool in v1**. Smiðja calls it internally. The user-facing tool waits until [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]] mesh dispatch arrives.

### Vow check

- **Vow of Smallness** — cron + ingest only. No batch_runner-style operator daemon. No multi-platform delivery in v1.
- **Vow of Tethered Grounding** — preserved. Cron jobs that ask LLM questions are subject to the same Brunnr tether as interactive sessions.
- **Vow of Graceful Offline** — at risk if a cron job tries to deliver via a network notify. Mitigation: when delivery fails, write to local file fallback. Job marked partial-success.
- **Vow of Public-Friendliness** — strengthened. `ember cron add "remind me to drink water" --every "90 min"` is a one-liner.
- **Vow of Modular Authorship** — strengthened. Cron is a sibling subsystem under `munnr/cron/`. If it crashes, Ember chat keeps running. Conversely, if `ember chat` is busy, `ember cron tick` runs independently in its own process.

### Implementation slice

Slice 1 (most valuable): the no_agent script path. Implement `ember cron add --script` and `ember cron tick`. Zero LLM involvement; users can immediately wire up Pi-friendly watchdogs.

Slice 2: agent-driven cron jobs. Add `prompt:` and skill preloading. Reuse Munnr's prompt construction from [[30_execution/36_CONTEXT_FILE_DISCIPLINE]].

Slice 3: IngestRunner with checkpointing. Smiðja gets resumable batches.

Slice 4: internal subagent primitive for Smiðja's parallel embed.

Slice 5 (post-v1): user-facing delegate_task tool. Probably gated behind Workstation-tier.

### What I do not propose

- Multi-platform delivery adapters in v1.
- A persistent daemon required for any cron functionality.
- User-facing `delegate_task` in v1.
- Cron job auto-creation by the agent (too easy to surprise the user).
- Cross-machine cron coordination (post-mesh feature).

### Where to read next

- [[30_execution/30_SELF_HEALING_LOOP]] — the curator is the first internal cron-shaped client of this system.
- [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]] — what the subagent primitive grows into.
- [[30_execution/40_SERVERLESS_HIBERNATION]] — how cron interacts with hibernated remote backends.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs.

Background work is real work. Schedule it like you mean it. Run it like you trust the lock. — Eldra.
