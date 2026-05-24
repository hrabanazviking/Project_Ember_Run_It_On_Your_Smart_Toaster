---
codex_id: 35_TRAJECTORY_COMPRESSION
title: Trajectory Compression — Training-Data Pipeline From Live Sessions
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - trajectory_compressor.py:1-130
  - trajectory_compressor.py:332-700
  - trajectory_compressor.py:709-1180
  - agent/trajectory.py:1-57
  - batch_runner.py:1-130
  - batch_runner.py:527-810
  - agent/context_compressor.py:1-80
ember_subsystem_targets: [Smiðja, Brunnr, Hjarta, Munnr]
cross_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
---

# Trajectory Compression

A trajectory is a JSONL record of a complete conversation: every turn, every tool call, every response. Hermes saves them via `agent/trajectory.py` and then compresses them via `trajectory_compressor.py` (1,508 lines). The output is fine-tuning fodder — ShareGPT-format JSONL, token-budgeted, training-signal-preserving. This file is the bridge between *running* an agent and *training a model from how the agent ran*.

I'm Eldra. This is the file in Hermes that most clearly is *not* about the user's experience — it's about the operator's experience and the broader model-training community. Ember has to make a careful call here: do we produce trajectories from our users' sessions? Under what consent? Under what privacy contract? Let me walk through what Hermes does and then sketch what Ember's stance should be.

## The Trajectory File Format

`agent/trajectory.py` is 57 lines. The whole thing:

```python
def save_trajectory(trajectory: List[Dict[str, Any]], model: str,
                    completed: bool, filename: str = None):
    if filename is None:
        filename = "trajectory_samples.jsonl" if completed else "failed_trajectories.jsonl"

    entry = {
        "conversations": trajectory,
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "completed": completed,
    }
    ...
```

One JSONL line per session. Each line contains:
- `conversations`: the full ShareGPT-shape message list (`{"from": "system|human|gpt|tool", "value": "..."}`).
- `timestamp`: when the session completed.
- `model`: which model drove the session.
- `completed`: success/failure flag.

Successful trajectories go to `trajectory_samples.jsonl`; failures to `failed_trajectories.jsonl`. The split lets downstream consumers pick: train on successes only, or train on both with the failure flag as a feature.

A separate concern: `convert_scratchpad_to_think()` (line 16) renames `<REASONING_SCRATCHPAD>` tags to `<think>` tags before saving. This is a small grace note for downstream training pipelines that expect the `<think>` convention. Hermes uses one tag internally and emits another externally.

## The Compressor

`trajectory_compressor.py:1-31` lays out the contract:

> "Post-processes completed agent trajectories to compress them within a target token budget while preserving training signal quality."

The compression strategy from the file header:

1. Protect first turns (system, human, first gpt, first tool).
2. Protect last N turns (final actions and conclusions).
3. Compress MIDDLE turns only, starting from 2nd tool response.
4. Compress only as much as needed to fit under target.
5. Replace compressed region with a single human summary message.
6. Keep remaining tool calls intact (model continues working after summary).

This is *training-data compression*, not *session compression*. The goal is to fit a real conversation into a `target_max_tokens` budget (default 15,250 — see line 90) while keeping the start (which contains the task setup) and the end (which contains the solution) intact. The middle is summarized.

The default summarization model is `google/gemini-3-flash-preview` (line 101). Cheap, fast, good enough at summarization. The compression model is *not* the model whose trajectory is being compressed — separation of concerns is preserved.

Three knobs the file exposes via `CompressionConfig`:

```python
@dataclass
class CompressionConfig:
    target_max_tokens: int = 15250
    summary_target_tokens: int = 750
    protect_first_system: bool = True
    protect_first_human: bool = True
    protect_first_gpt: bool = True
    protect_first_tool: bool = True
    protect_last_n_turns: int = 4
    summarization_model: str = "google/gemini-3-flash-preview"
    num_workers: int = 4
    max_concurrent_requests: int = 50
    skip_under_target: bool = True
    save_over_limit: bool = True
    per_trajectory_timeout: int = 300
    ...
```

Sane defaults. Async pipeline with up to 50 concurrent summarization requests. 5-minute timeout per trajectory. Trajectories already under target are skipped.

## Metrics — Compression as Observable Process

The file produces a `compression_metrics.json` aggregating per-trajectory stats:

- pre-compression and post-compression token counts
- compression ratio
- protected vs compressed turn counts
- summarization API failure rate
- tool stats: which tools were called, how often, with what error rates
- reasoning stats: how often the model used `<think>` blocks

These metrics are the *operator's* feedback loop. A team training a model on Hermes trajectories can see at a glance which compressions worked, which failed, which sessions are too long to fit even after compression.

## Batch Runner — How Trajectories Get Generated En Masse

`batch_runner.py` (1,321 lines) is the partner module. The flow:

1. Load a dataset of prompts from JSONL.
2. For each prompt: spawn an AIAgent, run it to completion, save the trajectory.
3. Checkpoint progress so an interrupted run can resume.
4. Optionally compress the batch via `trajectory_compressor.py`.
5. Emit aggregate metrics.

This is the harness that turns "Hermes the agent" into "Hermes the data-generating engine." Run thousands of prompts through it overnight, get thousands of JSONL trajectories, train a model on them. This is how Nous and similar groups produce training corpora.

The checkpointing pattern (`_save_checkpoint` at line 715, `_scan_completed_prompts_by_content` at line 732) is worth a separate doc. Cross-link [[50_verification/53_CRASH_PROOFING_PATTERNS]].

## What This Enables

The trajectory pipeline is what lets Hermes the *project* improve. Without it:
- No way to evaluate model X against model Y on real agentic tasks at scale.
- No fine-tuning corpus from real (or synthetic) agent sessions.
- No regression testing of new prompt strategies against historical sessions.

The pattern is RL-adjacent: trajectories are precisely the data shape that RLHF, RLAIF, and DPO consume. Hermes's separation between "run the agent" (`run_agent.py`) and "compress the recordings" (`trajectory_compressor.py`) is the same separation a typical RL pipeline makes between *rollout collection* and *batch processing*.

## What This Means for Ember — A Careful Stance

Ember's Vow of Honest Memory and Vow of Public-Friendliness make the trajectory question delicate. Hermes ships trajectory-saving on by default. Ember should not.

### The default

**Ember does NOT save trajectories by default.** The user's sessions are theirs. Period.

`ember.yaml` defaults:

```yaml
trajectory:
  save: "off"             # "off" | "local" | "shared"
  consent_recorded_at: null
  per_session_prompt: true   # ask each session
```

`save: off` is the floor. No JSONL files appear under `~/.ember/trajectories/`. No data is exfiltrated. No background pipeline runs.

### The opt-in

Power users may want trajectories. Maybe they're training a custom Funi. Maybe they're contributing to community datasets. The opt-in flow:

```
$ ember trajectory enable --mode=local
This will save your conversations as ShareGPT-format JSONL files under
~/.ember/trajectories/. Files are NEVER transmitted off this device
unless you separately enable sharing.

Continue? [y/N]
```

Consent is recorded with timestamp in `~/.ember/state/consent.json`. The user can revoke at any time:

```
$ ember trajectory disable
```

Disabling stops new trajectories from being saved. Already-saved files are not deleted automatically; the user must `ember trajectory purge` to remove them. (Two-step destroy is right for data — one-step is a foot-gun.)

### The contributor mode

For users explicitly contributing trajectories upstream:

```
$ ember trajectory enable --mode=shared --to=community-dataset
```

This requires:
- `mode=local` already enabled.
- A separate consent step with a privacy notice.
- A `ember trajectory review` command to preview what would be shared before each batch upload.
- PII scrubbing (Ember runs the trajectory through a redaction pass before upload).

Without all three, `mode=shared` refuses to enable. This is Vow of Honest Memory in action: the user knows exactly what's leaving their device.

### The Smiðja-trajectory bridge

[[30_execution/30_SELF_HEALING_LOOP]] proposed Smiðja capturing successful conversations as ingestible documents into Brunnr. Trajectory saving is a *parallel* capability: rather than putting the session into the Well as searchable knowledge, save it as JSONL training data.

The same source data, two destinations:

- **Brunnr ingest** (always-on by default, local-only): the user's documents become searchable knowledge. The user's *agent conversations* should NOT auto-ingest. Vow of Honest Memory — what the agent said in a session isn't ground truth, it's the agent's working.
- **Trajectory save** (off by default, local-only when on): the JSONL is durable training data.

Different consent boundaries; different storage shapes; same Capture stage of the loop.

### Proposed Ember API

```python
# src/ember/smiðja/trajectory/save.py
def save_trajectory(
    session_id: str,
    messages: list[Message],
    *,
    model: str,
    completed: bool,
    mode: Literal["off", "local", "shared"] = "off",
) -> Path | None:
    """Save a trajectory as JSONL under ~/.ember/trajectories/.

    Returns the path on success, None on no-op (mode=off, no consent).
    Raises ConsentMissing if consent is stale or never recorded.
    """
```

```python
# src/ember/smiðja/trajectory/compress.py
@dataclass(frozen=True)
class CompressionConfig:
    target_max_tokens: int = 15_000
    protect_first_n: int = 4
    protect_last_n: int = 4
    summarization_model_runtime: Literal["funi", "strengr"] = "funi"
    num_workers: int = 2
    ...

def compress_trajectory(traj_path: Path, config: CompressionConfig) -> Path: ...

def compress_directory(input_dir: Path, output_dir: Path, config: CompressionConfig) -> CompressionMetrics: ...
```

The shapes mirror Hermes. The difference: `summarization_model_runtime: Literal["funi", "strengr"] = "funi"`. By default, compression uses local Funi. The user can opt into Strengr if they have a faster remote model available.

### What Hermes does that Ember should NOT inherit

- **Default-on trajectory saving.** A bad default for an agent that runs in users' homes.
- **Failure-trajectory saving without consent.** `failed_trajectories.jsonl` is exactly the kind of file an angry user wants purged immediately. Ember saves failures only if the user opted into `mode=local` AND opted into `trajectory.save_failures=true`.
- **No PII scrubbing pre-share.** Hermes assumes operator-controlled environments (research orgs). Ember runs in user homes. PII scrubbing must run BEFORE any `mode=shared` upload, even with consent.

### Implementation pieces to borrow verbatim

- The ShareGPT JSONL shape (interop with the existing ecosystem).
- The first-N-protected, last-N-protected, middle-summarized compression strategy.
- The `<think>` tag rename in `convert_scratchpad_to_think`.
- The per-trajectory timeout (5 min default).
- The async pool with `max_concurrent_requests`.
- The `skip_under_target` early-exit.

### Vows on the line

- **Vow of Honest Memory** — strengthened by explicit consent gates. The user can never be surprised that their sessions are being recorded.
- **Vow of Smallness** — preserved by default-off. Pi users pay zero overhead.
- **Vow of Tethered Grounding** — orthogonal. Trajectories are about *the agent's actions*, not about *what the agent should believe*.
- **Vow of Modular Authorship** — strengthened. The whole trajectory subsystem is a sibling module under `smiðja/trajectory/`; if it crashes, the agent doesn't.
- **Vow of Public-Friendliness** — strengthened. Default-off means non-developers don't have to understand training data to use Ember.

### A future possibility

If Ember's curator ([[30_execution/30_SELF_HEALING_LOOP]]) ever gets cleverer about *which* skills to consolidate, it could read the compressed-trajectory metrics: "of the 15 times this skill was invoked, the trajectories show 14 successful completions and 1 failure — keep." This is the *signal* gap I identified in 30_SELF_HEALING_LOOP. The trajectory pipeline is what could fill it.

That work is deferred. Slice plan ([[60_synthesis/65_SLICE_PLAN_REVISIONS]]) shows trajectory-as-curator-signal as a "post-slice-5" item. Bring up the basics first.

### Where to read next

- [[30_execution/30_SELF_HEALING_LOOP]] — Capture-Codify-Curate-Recombine-Replay, of which trajectory save is the most disciplined Capture variant.
- [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] — the other capture path (skill creation), which has different consent semantics.
- [[50_verification/52_ANTIPATTERN_CATALOG]] — default-on logging of user conversations is the antipattern Hermes ships and Ember should not.
- [[60_synthesis/65_SLICE_PLAN_REVISIONS]] — when this lands in Ember's roadmap.

A trajectory is a transcript of work done. Treat it like one. Don't take it without asking. — Eldra.
