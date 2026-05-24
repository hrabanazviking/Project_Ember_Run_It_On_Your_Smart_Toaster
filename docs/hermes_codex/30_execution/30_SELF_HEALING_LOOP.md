---
codex_id: 30_SELF_HEALING_LOOP
title: The Self-Healing Loop — How Hermes Turns Experience Into Procedure
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - agent/curator.py:1-450
  - agent/curator.py:1369-1554
  - agent/curator.py:1763-1782
  - agent/skill_bundles.py:1-411
  - agent/system_prompt.py:60-285
  - agent/iteration_budget.py:1-62
  - agent/curator_backup.py
  - agent/skill_commands.py
ember_subsystem_targets: [Smiðja, Munnr, Funi, Hjarta]
cross_refs:
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 30_execution/38_PERSISTENT_MEMORY
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 50_verification/53_CRASH_PROOFING_PATTERNS
---

# The Self-Healing Loop

I'm Eldra. I work at the anvil. Theory is for after the hammer falls. Here is the hammer-fall.

A "self-healing loop" in an agent is the closed circuit where **the agent's own experience becomes the agent's next procedure**. Most projects ship a flat skill library and call it a day. Hermes does something a layer deeper: skills can be created, patched, marked stale, archived, and *consolidated under umbrellas* — all by an LLM that periodically forks itself to audit its own toolbox. The loop is not a buzzword. It's a 1,781-line module called `agent/curator.py` plus a 410-line bundle dispatcher called `agent/skill_bundles.py`. I read both. Here's how the circuit actually closes.

## Five Stages of the Loop

The Hermes self-healing loop has five stages. They are not abstract. Each one maps to an entry point in the code.

1. **Capture** — a working session that succeeds or fails. The agent's actions are recorded in `hermes_state.py` (SQLite with FTS5 — see [[30_execution/38_PERSISTENT_MEMORY]]).
2. **Codify** — when the user (or the agent itself) decides a workflow is worth keeping, `skill_manage` writes a SKILL.md plus optional `references/`, `templates/`, `scripts/` subfiles to `~/.hermes/skills/<name>/`.
3. **Curate** — an inactivity-triggered fork (`maybe_run_curator()` at `agent/curator.py:1763`) wakes an auxiliary model, hands it the candidate list of *agent-created* skills, and asks it to consolidate, prune, or patch.
4. **Recombine** — `agent/skill_bundles.py` lets multiple skills be invoked as a single `/<bundle>` slash command, building a synthetic user message that injects every member skill's body at once.
5. **Replay** — every subsequent session reads from this library. Procedural memory has been distilled out of episodic memory.

The cycle never demands the user's attention. The whole thing runs in a daemon thread:

```python
# agent/curator.py:1547
t = threading.Thread(target=_llm_pass, daemon=True, name="curator-review")
t.start()
```

That single line is the architecture. The agent is busy thinking; meanwhile, a fork of itself is studying what it already knows and tidying the bookshelf.

## Stage 1 — Capture: SessionDB as the Journal

Hermes persists every message via `hermes_state.py`. The schema (lines 255–300) wires three SQLite tables together:

- a primary `messages` table,
- an FTS5 virtual table `messages_fts` (BM25 ranked unicode61 tokenizer),
- and a *trigram* FTS5 table `messages_fts_trigram` so CJK substring search still works (`_sanitize_fts5_query` at line 2030 splits on the tokenizer's special characters and quotes hyphenated terms).

Three tables, one journal. Every tool call, every assistant reply, every user turn is durable before the curator even wakes. Without the journal there is nothing to learn from. This is the bedrock the loop sits on.

## Stage 2 — Codify: skill_manage

The agent has a tool called `skill_manage` (referenced throughout `curator.py`, e.g. lines 401–414). Actions are:

- `create` — write a new `SKILL.md` under `~/.hermes/skills/<slug>/`
- `patch` — append or rewrite sections of an existing SKILL.md
- `write_file` — add a `references/`, `templates/`, or `scripts/` subfile to an existing skill
- `delete` — archive (move to `.archive/`, NOT remove from disk — see line 348 hard rule #2)

Each skill is essentially a markdown file with a frontmatter or with section headings the curator will later parse. The shape is forgiving: a SKILL.md is just guidance for the model. What makes the system work is that `skill_manage` is a *first-class agent tool*, callable from inside any session. The agent that just solved the problem writes the skill that captures the solution. No human as intermediary.

## Stage 3 — Curate: the Inactivity-Triggered Fork

This is where the magic lives. Read `agent/curator.py:1763` carefully:

```python
def maybe_run_curator(
    *,
    idle_for_seconds: Optional[float] = None,
    on_summary: Optional[Callable[[str], None]] = None,
) -> Optional[Dict[str, Any]]:
    """Best-effort: run a curator pass if all gates pass."""
    try:
        if not should_run_now():
            return None
        if idle_for_seconds is not None:
            min_idle_s = get_min_idle_hours() * 3600.0
            if idle_for_seconds < min_idle_s:
                return None
        return run_curator_review(on_summary=on_summary)
    except Exception as e:
        logger.debug("maybe_run_curator failed: %s", e, exc_info=True)
```

Three gates. **All three must pass** before the curator wakes:

1. `is_enabled()` — config switch, defaults ON (line 148).
2. Not paused (`is_paused()` reads `.curator_state`).
3. Last run was longer than `interval_hours` ago (default **7 days**, line 56).
4. (Conditional) The caller-supplied idle threshold has elapsed (default **2 hours**, line 57).

And a fifth, subtle one: on the very first observation after install, the curator *refuses to run* and instead seeds `last_run_at = now` (lines 226–242). Why? Because:

> "the curator is designed to run after at least interval_hours (7 days by default) of skill activity, not on the first background tick after `hermes update`."

This is wisdom carved by scars. Without that gate, every fresh install would trigger an immediate full audit on a near-empty library, generate confused output, and the user would lose trust in the whole subsystem on day one. Defer the first cut.

### What the curator actually does

Once the gates pass, `run_curator_review()` (line 1369) executes a four-phase pass:

**Phase 3A — pre-mutation snapshot.** Before touching anything, take a snapshot via `curator_backup.snapshot_skills(reason="pre-curator-run")` (line 1413). Archives are recoverable; full rollback is recoverable too. This is `crash-only software design` applied to a maintenance loop. If the curator dies mid-LLM-call, the user can roll back.

**Phase 3B — pure transitions.** `apply_automatic_transitions()` at line 256 walks every agent-created skill and re-classifies based on `last_activity_at`:

- older than `stale_after_days` (default 30) → mark **stale**
- older than `archive_after_days` (default 90) → move to **archived**
- newly active again after being stale → **reactivated**

This is pure-function. No LLM. No tokens spent. Just timestamps and a state machine — see the `STATE_ACTIVE / STATE_STALE / STATE_ARCHIVED` ladder in `tools.skill_usage`.

**Phase 3C — LLM umbrella pass.** `_llm_pass()` (line 1445) spawns a forked AIAgent under the *auxiliary client* (not the main session — invariant on line 19: "Uses the auxiliary client; never touches the main session's prompt cache"). The forked agent runs with a 1,000-line system prompt (CURATOR_REVIEW_PROMPT, lines 330–445). That prompt is itself an engineered artifact — it tells the model to look for **prefix clusters** (`hermes-config-*`, `gateway-*`, `pr-*`...) and merge them into umbrella skills, *demoting* narrow siblings into `references/`, `templates/`, or `scripts/` subfiles.

The CURATOR_REVIEW_PROMPT is one of the most ruthless prompts I've ever read in an agent codebase. It deliberately prevents the model from coasting:

> "DO NOT use usage counters as a reason to skip consolidation. The counters are new and often mostly zero. Judge overlap on CONTENT, not on use_count. 'use=0' is not evidence a skill is valuable; it's absence of evidence either way."

And:

> "If you end the pass with fewer than 10 archives, you stopped too early — go back and look at the clusters you left alone."

This is a **prompt with a quota**, and it's right to be that way. A timid curator produces fragmented libraries. A bold curator produces structured ones.

**Phase 3D — structured summary + REPORT.md.** Every run writes `~/.hermes/logs/curator/{timestamp}/REPORT.md` plus `run.json` (lines 452–471). The LLM is required to emit a YAML block separating `consolidations:` from `prunings:` (lines 426–445). The post-pass `_classify_removed_skills()` (line 492) then cross-checks: which removed skills had their content absorbed into a still-living umbrella (consolidation) versus genuinely pruned (line 549+)? This is the audit trail that makes the loop *trustworthy*. Nothing happens in the dark.

### Dry-run mode

The CURATOR_DRY_RUN_BANNER (lines 303–327) is the safety valve. `hermes curator run --dry-run` injects this banner above the review prompt. The forked agent is told: "Your output IS the deliverable. Produce the exact same human-readable summary and structured YAML block you would produce on a live run — but describe the actions you WOULD take, not actions you took."

This is a beautifully simple pattern: the same agent, the same prompt, the same toolset — but the prompt restructures the agent's understanding of the task from "execute" to "rehearse." Users get a preview before destructive ops. Ember should steal this verbatim.

## Stage 4 — Recombine: skill_bundles

`agent/skill_bundles.py` is the loop's multiplier. A *bundle* is a YAML file in `~/.hermes/skill-bundles/<slug>.yaml`:

```yaml
name: backend-dev
description: Backend feature work — code review, testing, PR workflow.
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Optional extra guidance.
```

Invoke `/backend-dev` and `build_bundle_invocation_message()` (line 253) loads every member skill's body, then assembles ONE synthetic user message that lists the bundle, then concatenates each skill's content as a block:

```python
header_lines = [
    f'[IMPORTANT: The user has invoked the "{bundle_name}" skill bundle, '
    f"loading {len(loaded_names)} skills together. Treat every skill below "
    "as active guidance for this turn.]",
    "",
    f"Bundle: {bundle_name}",
    f"Skills loaded: {', '.join(loaded_names)}",
]
```

If a referenced skill is missing, it's listed under `Skills missing (skipped):` and the bundle still loads (line 268, "the same forgiving stance"). Bundles don't fail closed; they degrade.

This is a **composability play**. Curate produces stable, class-level skills. Bundle lets the user recombine them into task-shaped invocations. The loop is closed at the user-interaction layer, not just at the maintenance layer.

## Stage 5 — Replay: System Prompt Discipline

The library matters only if the next session reads from it. `agent/system_prompt.py:60–285` shows how. The system prompt is built once per session and cached. Three tiers:

- **stable**: identity, tool guidance, skills prompt, environment hints — concatenated at agent init and never rebuilt mid-session.
- **context**: AGENTS.md / .cursorrules / cwd discovery.
- **volatile**: memory snapshot, USER profile, **date-only** timestamp.

Line 264–271 explicitly prefers date-only formatting:

> "Date-only (not minute-precision) so the system prompt is byte-stable for the full day. Minute-precision changes invalidate prefix-cache KV on every rebuild path."

This is the prompt-caching ergonomic that makes the replay layer cheap. Procedural memory is durable on disk; identity is durable in the cached prompt prefix. Per-turn cost stays low. See [[30_execution/36_CONTEXT_FILE_DISCIPLINE]] for the prompt-caching pattern in detail.

## What Hermes Does Not Do (and Should)

A few honest gaps in Hermes's self-healing loop, because we are in the business of inheriting only the best parts:

1. **No success/failure signal feeding the curator.** The curator judges by mtime + content overlap. It does not know that skill X "actually worked" on task Y. There is no causal feedback. The whole loop is *correlative*.
2. **No A/B test for skill quality.** When two umbrella candidates are proposed, the curator picks one with deterministic ordering. No evaluation harness.
3. **Curator runs on auxiliary client only.** Provider failures during a 7-day-cycle pass aren't catastrophic, but they do mean the loop occasionally just doesn't close. There's no retry queue for missed curator runs.
4. **No cross-device propagation of skills.** Bundles live in `~/.hermes/skill-bundles/`. If a user runs Hermes on a desktop and a Pi, the two libraries drift. Hermes has no built-in sync — it would need git or a third-party sync solution.

## What This Means for Ember

The self-healing loop maps onto Ember's True Names like this:

**Smiðja owns Capture and Codify.** [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] should formalize that Smiðja's responsibility extends from "ingest external docs" to "ingest internal experience." Smiðja already chunks-and-embeds source documents into Brunnr. Adding a `smiðja experience capture` mode — where a completed conversation is treated as a document and chunked-and-embedded — is a straight-line extension. The chunks live alongside knowledge chunks in Brunnr; the embedding adapter is the same; the storage backend is the same.

**Munnr owns Recombine.** Skill bundles are an interaction-layer pattern; bundles belong with the mouth. Munnr's CLI already dispatches slash commands; adding `/<bundle-name>` is a CLI-side feature. Crucially: bundles violate no Vow — they are entirely local, they are YAML files (human-editable, [[Vow of Public-Friendliness]]), and they degrade gracefully when a member skill is missing ([[Vow of Modular Authorship]]).

**Hjarta seeds the loop.** The first-run rite should plant an empty `~/.ember/skills/` directory plus a sentinel `.curator_state` file. Without the sentinel, [[Vow of Smallness]] is at risk — the curator might try to auto-run on first boot and burn tokens before the user has done anything worth curating. Hjarta installs the seven-day defer.

**Funi gates the auxiliary fork.** The curator forks an LLM call. On a Pi, that LLM call must hit a local model unless the user has opted into a network call. The default curator model on Ember should be Funi (local). If Funi is unavailable, the loop should *not silently use Strengr* — it should defer (Vow of Graceful Offline). I propose `ember.yaml`:

```yaml
curator:
  enabled: true
  interval_hours: 168       # 7 days
  min_idle_hours: 2
  model: "local"            # "local" | "strengr" | "off"
  consent_for_strengr: false
```

The default of `model: local` keeps the Vow of Smallness intact. If the user wants the curator to use a stronger remote model, they opt in explicitly.

### Proposed Ember API shape

A new module `~/ai/ember/src/ember/smiðja/curator.py` should expose:

```python
def should_run_now(state_path: Path | None = None) -> bool: ...

def apply_automatic_transitions(now: datetime | None = None) -> dict[str, int]: ...

def run_curator_review(
    *,
    on_summary: Callable[[str], None] | None = None,
    synchronous: bool = False,
    dry_run: bool = False,
    model: Literal["local", "strengr", "off"] = "local",
) -> dict[str, Any]: ...

def maybe_run_curator(
    *,
    idle_for_seconds: float | None = None,
    on_summary: Callable[[str], None] | None = None,
) -> dict[str, Any] | None: ...
```

The signature mirrors Hermes 1:1. The implementation differs in one place: the LLM-call site uses Funi's local model adapter by default and only falls back to Strengr with explicit opt-in.

A new True Name candidate emerges from this work: **Verðr** (Old Norse for "what becomes" / "what is worth"). Verðr would be the self-healing curator subsystem. Where Smiðja captures and codifies, Verðr decides what is worth keeping. Sigrún at [[00_vision/02_NAMING_PARALLELS]] should weigh whether this deserves promotion to a seventh True Name or whether it folds under Smiðja as a sub-rite. I lean *fold*. Verðr is what Smiðja does, not what Smiðja is.

### Vows on the line

- **Vow of Smallness** — at risk if the curator defaults to remote LLM. Mitigation: local default, explicit opt-in for Strengr.
- **Vow of Honest Memory** — strengthened. The curator's REPORT.md gives the user a paper trail. They can see exactly which skill became which umbrella.
- **Vow of Modular Authorship** — strengthened. The curator runs as a daemon thread (line 1547); failure of the auxiliary model does not crash the main session.
- **Vow of Graceful Offline** — at risk if curator silently fails on no-network. Mitigation: when Funi is unavailable and Strengr is not consented, the curator marks the run "skipped (offline)" in `.curator_state.last_run_summary` and tries again next interval.

### Where to read next

- [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] — the mechanics of how skills are auto-created mid-session (the Codify stage in depth).
- [[30_execution/38_PERSISTENT_MEMORY]] — the FTS5 journal that underlies Capture.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — where Smiðja's scope is broadened to encompass this loop.

The forge is hot. Take what's useful. Leave the rest in the ash. — Eldra.
