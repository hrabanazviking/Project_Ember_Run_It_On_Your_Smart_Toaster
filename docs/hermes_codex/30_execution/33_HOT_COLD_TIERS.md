---
codex_id: 33_HOT_COLD_TIERS
title: Hot/Cold Tiers — Hardware-Aware Model and Context Selection
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - agent/model_metadata.py:105-150
  - agent/model_metadata.py:563-650
  - agent/context_engine.py
  - agent/context_compressor.py:50-80
  - agent/context_compressor.py:2263-2700
  - run_agent.py:360
  - agent/iteration_budget.py:1-62
  - agent/auxiliary_client.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta]
cross_refs:
  - 30_execution/31_CROSS_PLATFORM_TACTICS
  - 30_execution/36_CONTEXT_FILE_DISCIPLINE
  - 30_execution/41_MULTI_PROVIDER_FAILOVER
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Hot/Cold Tiers

A single LLM agent ships one configuration. A *thoughtful* agent ships several. A Pi cannot run what a workstation can; a workstation should not waste tokens running what a Pi can. Hermes does not have an explicit "tier system" with that name, but if you read `agent/model_metadata.py` next to `agent/context_compressor.py` you can see the same idea operating in three places — *context length probe tiers*, *auxiliary vs main client split*, and *per-platform toolset gating*. Eldra here. Let me pull each one out, then propose a clean Pi/Laptop/Workstation/Swarm tier policy for Ember.

## Tier One — Context-Length Probe Tiers

`agent/model_metadata.py:133`:

```python
MINIMUM_CONTEXT_LENGTH = 64_000
```

This is the floor. Any model in Hermes's metadata cache with a context length below 64K is bumped to 64K for budgeting purposes — because the compression code below assumes a minimum window large enough to retain a useful summary plus several tail messages.

But the context window of a specific session is *not* fixed at the model's max. `agent/context_engine.py` exposes `get_next_probe_tier(current_ctx) -> int`. Used at `agent/context_compressor.py:2580`:

```python
new_ctx = get_next_probe_tier(old_ctx)
```

The pattern: when a request fails with "context too long," step *down* to the next-smaller probe tier and retry. The probe tiers are a hardcoded ladder like 1M → 400K → 200K → 128K → 64K. Different providers expose context windows in different ways and frequently lie about their true ceiling for a given account. The probe ladder lets Hermes *discover* the real ceiling empirically.

Lines 2263–2293 show the specifically Anthropic case:

```python
# Anthropic Sonnet long-context tier gate
# subscription doesn't include the 1M-context tier. This
# (standard tier) and compress.
if classified.reason == FailoverReason.long_context_tier:
    ...
    f"{agent.log_prefix}⚠️  Anthropic long-context tier not available"
```

When the Anthropic API responds "your subscription doesn't include 1M context," Hermes steps down to standard tier and triggers compression. The user doesn't see an error; they see a small "compressed to fit standard tier" notice. **Tier degradation is automatic and invisible by default.**

The mechanic at line 2417 covers the GitHub Models free tier case:

```python
# The free tier enforces a hard 8K token cap per request
```

Hermes knows that several models on the free tier have *output* caps separately from *context* caps. Same idea: detect, downgrade, retry, log.

## Tier Two — Auxiliary vs Main Client

A second tiering: not all LLM calls are equal in importance. The main session uses one client (per `agent/conversation_loop.py`'s primary path). Background tasks — context summarization, curator review ([[30_execution/30_SELF_HEALING_LOOP]]), title generation, prompt sanitization — use the **auxiliary client** (`agent/auxiliary_client.py`).

The split matters because:

- The auxiliary client can use a *smaller, cheaper model*. A 3B parameter model is more than capable of summarizing middle turns of a conversation, but you don't want it driving the conversation.
- The auxiliary client has *separate prompt cache state*. Curator and compressor runs don't pollute the main session's KV cache.
- The auxiliary client can *use a different provider entirely*. Main: Anthropic Sonnet. Auxiliary: a local Ollama llama3.2:3b. The Pi can do this with no remote dependency.

This is a free composability win. The "tier" here isn't named, but the *split* gives Hermes the architecture to support tier-aware routing without code duplication.

## Tier Three — Per-Platform Toolset Gating

`cron/scheduler.py:60-89` (`_resolve_cron_enabled_toolsets`) shows the third tiering: which **toolsets** are available in a given execution context.

```python
# 1. Per-job ``enabled_toolsets`` (set via ``cronjob`` tool on create/update).
# 2. Per-platform ``hermes tools`` config for the ``cron`` platform.
# 3. ``None`` on any lookup failure — AIAgent loads the full default set
```

Cron jobs run with a *different* toolset than interactive chat. The reasoning, from the comment block: "_DEFAULT_OFF_TOOLSETS ({moa, homeassistant, rl}) are removed by `_get_platform_tools` for unconfigured platforms, so fresh installs get cron WITHOUT `moa` by default (issue reported by Norbert — surprise $4.63 run)."

Pattern recognition: the cost-of-tool-use varies by tool. `moa` (Mixture-of-Agents) is expensive; you don't want it auto-firing on a 5-minute cron. Gating toolsets by execution surface (interactive vs cron vs gateway vs delegated subagent) keeps cost bounded and behaviors predictable.

## What Hermes Does Not Quite Do

Three things Hermes has individual pieces of but no unified system:

1. **No `Host` capability detection.** Hermes doesn't say "I see I'm on a Pi 5 with 4GB RAM, so I'll select tier X." Termux detection in `setup-hermes.sh:38` is purely for install-time decisions; runtime tier selection is config-driven, not discovery-driven.
2. **No declared tier policy.** A user reading `config.yaml.example` sees `model.provider`, `delegation.max_iterations`, `cron.max_parallel_jobs` — but not "Pi-tier" or "Workstation-tier". Tiering is implicit in the choices.
3. **No tier-aware curator/compressor selection.** The compressor always uses the auxiliary client. There's no fallback to "use main client if auxiliary times out" or "switch auxiliary to a smaller model if I detect a 4GB device."

Ember can make all three explicit.

## What This Means for Ember

I propose a **four-tier policy** for Ember, declared in `ember.yaml`, auto-selected by Hjarta at first run, overridable any time. Tier names are aesthetic but the *capability promises* are the load-bearing part.

### The Four Tiers

| Tier | Hardware example | Funi (local LLM) | Brunnr (Well) | Smiðja (ingest) | Curator | Mesh |
|---|---|---|---|---|---|---|
| **Pi-tier** | Pi 5 4-8GB, Termux | llama3.2:3b, qwen2.5:3b | sqlite_vec, local | small batches (10 chunks) | local Funi, weekly | join-only |
| **Laptop-tier** | M2/M3 Mac, 16GB Linux | llama3.2:8b, mistral:7b | sqlite_vec OR pgvector | mid batches (100 chunks) | local Funi or Strengr-opt | join+host |
| **Workstation-tier** | RTX 3090/4090, 32GB+ | llama3.2:70b-instruct-q4, qwen2.5:32b | pgvector or qdrant | large batches (1000 chunks) | local Funi (big) | host |
| **Swarm-tier** | several devices visible via Strengr mesh | dispatched by capability | shared remote pgvector | distributed across peers | dispatched to most-capable peer | full participant |

Each tier *contains* the one below. A Workstation can do anything a Pi can; a Swarm can do anything a Workstation can. Demotion is always safe.

### Tier Detection (Hjarta)

Hjarta runs once at first-launch (and on `ember reconfigure`). It detects:

```python
# src/ember/hjarta/tier.py
@dataclass(frozen=True)
class TierDetection:
    suggested_tier: Literal["pi", "laptop", "workstation", "swarm"]
    confidence: float            # 0.0 - 1.0
    reasons: list[str]           # human-readable
    host: Host                   # from ember.hjarta.platform

def detect_tier() -> TierDetection: ...
```

Detection signals:

- **RAM** from `psutil.virtual_memory().total`. <8GB ⇒ Pi-tier candidate. 8-24GB ⇒ Laptop. >24GB ⇒ Workstation candidate.
- **GPU** via nvidia-smi presence (Linux/Windows) or `system_profiler SPDisplaysDataType` (macOS). Apple Silicon = unified memory, treat as Laptop with bonus context. NVIDIA detected with VRAM ≥ 16GB ⇒ Workstation.
- **CPU cores** from `os.cpu_count()`. < 4 ⇒ likely Pi or Termux.
- **Arch** from `platform.machine()`. ARMv7 / aarch64 ⇒ Pi unless RAM disagrees.
- **/sys/firmware/devicetree/base/model** existence and contents (Pi-specific).
- **TERMUX_VERSION** env var (Android).

Hjarta proposes a tier; the user accepts or overrides. The proposal is recorded in `~/.ember/state/tier.json`. The host's `detect_host()` from [[30_execution/31_CROSS_PLATFORM_TACTICS]] feeds this.

### Tier-Aware Configuration

A tier is not just a label; it's a parameter set:

```python
# src/ember/spark/funi/tier_config.py
@dataclass(frozen=True)
class TierConfig:
    funi_model_recommend: list[str]      # ranked candidates
    funi_max_context: int                # token cap for prompts
    smiðja_batch_size: int               # chunks per ingest batch
    curator_model: Literal["local", "strengr", "off"]
    mesh_role: Literal["join", "host", "full"]
    delegation_max_concurrent: int
    delegation_max_iterations: int

PI_TIER: TierConfig = TierConfig(
    funi_model_recommend=["llama3.2:3b", "qwen2.5:3b", "phi3:mini"],
    funi_max_context=8000,
    smiðja_batch_size=10,
    curator_model="local",
    mesh_role="join",
    delegation_max_concurrent=1,
    delegation_max_iterations=20,
)

WORKSTATION_TIER: TierConfig = TierConfig(
    funi_model_recommend=["qwen2.5:32b", "llama3.2:70b-instruct-q4"],
    funi_max_context=131072,
    smiðja_batch_size=1000,
    curator_model="local",
    mesh_role="host",
    delegation_max_concurrent=8,
    delegation_max_iterations=90,
)
# (LAPTOP_TIER, SWARM_TIER similarly)
```

### Probe-Tier Pattern for Ember

Adopt Hermes's context-probe pattern verbatim. `src/ember/spark/funi/probe.py`:

```python
EMBER_PROBE_TIERS = [131_072, 65_536, 32_768, 16_384, 8_192, 4_096]

def get_next_probe_tier(current_ctx: int) -> int:
    """Return the next-smaller probe tier, or 0 if at minimum."""
    for t in EMBER_PROBE_TIERS:
        if t < current_ctx:
            return t
    return 0
```

When Funi reports a too-long-prompt error, Ember steps down to the next probe tier and triggers compression. This works for *any* local model whose true context ceiling is fuzzy (frequent reality for quantized Ollama models).

### Auxiliary Client Split

Mirror Hermes. Ember has two LLM call sites:

- **Main session**: `funi.call(...)` — uses the user's chosen Funi model.
- **Auxiliary**: `funi.call_aux(...)` — uses a *smaller* model, defaulting to whatever Funi advertises as its "small" variant.

```python
# src/ember/spark/funi/__init__.py
def call(messages: list[Message], *, max_tokens: int = 1024) -> Reply: ...

def call_aux(messages: list[Message], *, max_tokens: int = 512) -> Reply: ...
```

The auxiliary call is used by:
- The context compressor (when sessions get long).
- The curator (when reviewing skills).
- The trajectory summarizer (when producing session digests).
- The title generator (when nicknaming sessions for the chat history).

On Pi-tier, auxiliary defaults to the same model as main (a Pi only has one model loaded). On Laptop/Workstation tier, auxiliary can be a separately-loaded smaller model (e.g., main=qwen2.5:32b, aux=qwen2.5:3b).

### Per-Surface Toolset Gating

Borrow Hermes's `_resolve_cron_enabled_toolsets` shape. Ember's tools are far fewer, but the same precedence applies:

```python
# src/ember/munnr/toolsets.py
def resolve_enabled_toolsets(surface: Literal["chat", "cron", "ingest"], cfg: dict) -> list[str]:
    """Per-surface > per-tier > default."""
```

Why this matters: a user wants `ember chat` to have access to `read_local_file`, but they likely don't want a cron job at 3am to read local files. Surface-aware toolset gating closes the surprise-cost class of bugs Hermes's Norbert hit.

### Tier Promotion

A user buys a new laptop. They move their `~/.ember/` to it. They run `ember chat`. Hjarta detects the better hardware, prints:

```
Detected upgrade: pi-tier → laptop-tier
Suggested changes:
  - Funi model: llama3.2:3b → llama3.2:8b (recommend `ember funi pull llama3.2:8b`)
  - Smiðja batch: 10 → 100 chunks per pass
  - Curator: weekly → daily-eligible
Run `ember tier accept` to apply, or `ember tier hold` to keep current.
```

This is the *Cross-Platform Plan* in action — a user moving between platforms gets a path, not a re-onboarding.

### What stays the same across tiers

Critically, **the user-facing commands are identical at every tier**. `ember chat`, `ember well ingest`, `ember well query`, `ember curator status`. The tier only changes:

- Which model Funi uses.
- How aggressive Smiðja's batching is.
- Whether Curator and Mesh participate.
- The compression boundaries the compressor uses.

A user who never thinks about tiers gets sensible defaults. A user who cares can dial.

### Vows on the line

- **Vow of Smallness** — strengthened. Pi-tier is the explicit floor, and every other tier is opt-in scaling.
- **Vow of Pluggable Storage** — preserved. Tier affects *which* storage adapter is recommended, never which adapters work. Brunnr remains pluggable at every tier.
- **Vow of Public-Friendliness** — strengthened. Auto-detection means non-developers don't have to read a tier policy. They run `ember setup` and get sensible defaults.
- **Vow of Honest Memory** — at risk if tier-down-step silently drops messages. Mitigation: every probe step-down logs a one-line note in `state.json` ("compressed at probe tier 32K because 64K failed"). The user can read it.
- **Vow of Flexible Roots** — preserved. Tier detection writes to `~/.ember/state/tier.json` via `Path.home()`. No absolute paths.

### One More Thing — Tier-Aware Iteration Budgets

`agent/iteration_budget.py` is exactly the right shape, but its constants are fixed (90 parent, 50 child). Ember's `IterationBudget` should accept the cap from the tier:

```python
budget = IterationBudget(tier_config.delegation_max_iterations)
```

Pi-tier: 20 iterations max — keeps any single tool-loop bounded on slow hardware.
Workstation-tier: 90 iterations max — same as Hermes default.
Swarm-tier: 120 iterations max — bigger problems can be sliced across more peers.

### Where to read next

- [[30_execution/31_CROSS_PLATFORM_TACTICS]] — the `Host` capability record that feeds tier detection.
- [[30_execution/36_CONTEXT_FILE_DISCIPLINE]] — how the prompt-caching layer pairs with tier-aware context limits.
- [[30_execution/41_MULTI_PROVIDER_FAILOVER]] — how tier-down-step interacts with provider failover.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — Funi's expanded scope to own the tier policy.

If your only hammer is the same on a Pi and a workstation, you are using neither well. Pick the hammer for the anvil. — Eldra.
