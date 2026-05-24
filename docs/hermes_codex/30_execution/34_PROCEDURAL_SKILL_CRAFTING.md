---
codex_id: 34_PROCEDURAL_SKILL_CRAFTING
title: Procedural Skill Crafting — Turning Experience Into Reusable Procedure
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - tools/skill_usage.py:1-50
  - tools/skill_usage.py:285-340
  - agent/skill_commands.py:1-470
  - agent/curator.py:301-445
  - agent/skill_bundles.py:253-340
  - agent/curator_backup.py
ember_subsystem_targets: [Smiðja, Munnr]
cross_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/38_PERSISTENT_MEMORY
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 50_verification/52_ANTIPATTERN_CATALOG
---

# Procedural Skill Crafting

A skill is a piece of advice from past-you to future-you, written down and indexed so future-you can find it. In Hermes, a skill is a directory under `~/.hermes/skills/<name>/` containing `SKILL.md` plus optional `references/`, `templates/`, `scripts/` subdirs. The agent itself creates skills mid-session via the `skill_manage` tool. Provenance is tracked. The curator ([[30_execution/30_SELF_HEALING_LOOP]]) periodically reviews them. This is procedural memory, distilled from episodic memory, by the agent that's living the episode.

I'm Eldra. I'm going to walk you through the actual mechanics — provenance, file layout, the sidecar telemetry file, the slash-command surface, the safety rules — then propose what Ember's analogue should look like under the Vow of Honest Memory.

## The Skill File Layout

Every skill lives under `~/.hermes/skills/<slug>/`. Minimum:

```
~/.hermes/skills/backend-pr-review/
├── SKILL.md           # the actual instructional content
```

Richer skills add support directories per `agent/curator.py:381-393`:

```
~/.hermes/skills/backend-pr-review/
├── SKILL.md
├── references/        # session-specific detail, condensed knowledge banks
│   ├── django-orm-quirks.md
│   └── pr-2847-postmortem.md
├── templates/         # starter files meant to be copied and modified
│   └── pr-description.md
└── scripts/           # statically re-runnable actions
    ├── run-tests.sh
    └── lint-changed-files.sh
```

Three categories matter:

- **SKILL.md** — the instruction body. Loaded when the skill is invoked. Should be class-level, not session-specific.
- **references/** — knowledge banks. Quoted research, API docs excerpts, domain notes, reproduction recipes. The curator routinely promotes narrow session-specific skills into a referenced section here when consolidating.
- **templates/** — files meant to be copied. The agent reads them and emits modified copies during a session.
- **scripts/** — re-runnable actions. The agent invokes them via `terminal`.

The curator's prompt at `agent/curator.py:383-393` explicitly names the demotion path:

> "DEMOTE TO REFERENCES/TEMPLATES/SCRIPTS — a sibling has narrow-but-valuable session-specific content. Move it into the umbrella's appropriate support directory."

This is the *shape rule* that prevents fragmentation. Class-level skill → SKILL.md. Session-specific detail → references/. Reusable starter → templates/. Re-runnable action → scripts/.

## Provenance — Who Made This?

`tools/skill_usage.py:290`:

```python
def is_agent_created(skill_name: str) -> bool:
    """Whether *skill_name* is neither bundled nor hub-installed."""
    off_limits = _read_bundled_manifest_names() | _read_hub_installed_names()
    return skill_name not in off_limits
```

Three provenance buckets:

1. **Bundled** — skills shipped with Hermes. Listed in `.bundled_manifest`. Read-only as far as the curator is concerned.
2. **Hub-installed** — skills installed via the agentskills.io hub. Listed in `.hub/`. Also off-limits to the curator.
3. **Agent-created** — everything else. Eligible for curator review.

Only bucket 3 is touched by curator transitions. This is the **first invariant**: the agent never modifies skills it didn't create. Bundled and hub skills are stable; agent-created skills evolve.

Provenance is tracked in `~/.hermes/skills/.usage.json` — a sidecar map keyed by skill name (line 322–340):

```python
def _empty_record() -> Dict[str, Any]:
    return {
        "created_by": None,            # "agent" | None
        "use_count": 0,
        "view_count": 0,
        "last_used_at": None,
        "last_viewed_at": None,
        "patch_count": 0,
        "last_patched_at": None,
        "created_at": _now_iso(),
        "state": STATE_ACTIVE,
        "pinned": False,
        "archived_at": None,
    }
```

`created_by="agent"` flags a skill as agent-created and curator-eligible. Pinned skills are exempt from auto-transitions. State is one of `active`, `stale`, `archived`.

The sidecar is deliberate per the file's header doc:

> "Sidecar, not frontmatter. Keeps operational telemetry out of user-authored SKILL.md content and avoids conflict pressure for bundled/hub skills."

If telemetry lived in the SKILL.md frontmatter, every `use_count` bump would dirty the file. Sidecar isolates the counter writes from the instruction content. The pattern is right.

## Atomic Writes Everywhere

The sidecar uses the atomic-write pattern (line 343+):

```python
def save_usage(data: Dict[str, Dict[str, Any]]) -> None:
    """Write the usage map atomically. Best-effort — errors are logged, not raised."""
```

The implementation uses `tempfile.NamedTemporaryFile(dir=...)` + `os.replace()`. Atomic on POSIX, atomic-on-same-volume on Windows. This is the same pattern Ember already uses (per `docs/CROSS_PLATFORM_PLAN.md`). Cross-walk is clean.

Same module also gracefully handles cross-platform file locks:

```python
# tools/skill_usage.py:45-50
try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        pass
```

The same polymorphism as `cron/scheduler.py:23-30`. Tested across both Unix and Windows.

## The skill_manage Tool

`agent/curator.py:401-414` lists the curator-visible actions:

```
- skills_list, skill_view        — read the current landscape
- skill_manage action=patch      — add sections to the umbrella
- skill_manage action=create     — create a new umbrella SKILL.md
- skill_manage action=write_file — add a references/, templates/, or
  scripts/ file under an existing skill (the skill must already exist)
- skill_manage action=delete     — archive a skill. MUST pass
  `absorbed_into=<umbrella>` when you've merged its content into another
  skill...
```

The action shape is the cleanest thing about it. **Five verbs, two of which only require a name; three of which require additional structured arguments.** Every action is reversible (delete is archive-to-`.archive/`, not unlink).

Notable: `skill_manage action=write_file` requires the parent skill already exists. The agent can't accidentally create a skill by writing a sub-file. Structure-creation is explicit.

The most interesting argument is `absorbed_into=<umbrella>` on `delete`. The curator's whole pipeline relies on knowing whether a removed skill was *consolidated into* another or *truly pruned*. Without this argument, post-hoc inference is fragile. With it, the structured YAML summary at `agent/curator.py:427-444` becomes trustworthy:

```yaml
consolidations:
  - from: <old-skill-name>
    into: <umbrella-skill-name>
    reason: <one short sentence — why merged, not just 'similar'>
prunings:
  - name: <skill-name>
    reason: <one short sentence — why archived with no merge target>
```

This is the audit trail that makes the loop trustworthy.

## The Slash-Command Surface

`agent/skill_commands.py:1-475` exposes skills as slash commands. The user types `/<skill-name>`, and the dispatcher:

1. Resolves the slash name via `resolve_skill_command_key()` (line 409) — handles hyphen/underscore variants for Telegram bot compatibility.
2. Loads the skill via `_load_skill_payload()` (line 53). Handles absolute paths under trusted roots, expands `~`, and refuses arbitrary paths outside `SKILLS_DIR` + external skill dirs.
3. Builds an invocation message via `build_skill_invocation_message()` (line 428) that concatenates an activation note + the skill's body + any config substitutions.
4. Sends that message as if the user typed it.

The pattern: a slash command is a *macro* that expands to a long user message containing the skill body. The agent then has the skill in context, freshly, for the next turn. No system-prompt mutation. No cache invalidation. The skill enters as a user message and the prompt cache prefix stays warm.

**This is the cleverest single design choice in the Hermes skill system.** Many architectures inject skills into the system prompt; that invalidates the prefix cache every time a skill changes or is added. Hermes injects skills into a user message, which is necessarily *after* the cached prefix. Cost stays low.

## Safety Around Auto-Creation

`agent/curator.py:344-358` is the safety contract for the LLM curator pass:

```
Hard rules — do not violate:
1. DO NOT touch bundled or hub-installed skills.
2. DO NOT delete any skill. Archiving is the maximum destructive action.
3. DO NOT touch skills shown as pinned=yes. Skip them entirely.
4. DO NOT use usage counters as a reason to skip consolidation.
5. DO NOT reject consolidation on the grounds that 'each skill has a distinct trigger'.
```

Rules 1, 2, and 3 are mechanical safeguards. Rules 4 and 5 are behavioral — they tell the LLM how to *think* about the task, not just what to refuse. This level of prompt-engineering precision is itself a craft skill, and the result is a curator that aggressively but safely consolidates.

The curator-backup module (`agent/curator_backup.py`) takes a snapshot of the entire skill library *before* every live curator run. If the curator goes off the rails, the snapshot allows full rollback. The combination of "archive instead of delete" + "snapshot before run" + "structured YAML diff" makes the LLM pass safe by construction.

## What Hermes Doesn't Quite Do

A few observations from reading the code rather than the marketing:

1. **No automatic skill creation from session success.** The agent only creates a skill when the user (or the agent acting on user intent) asks for one. There's no signal like "this session succeeded; propose a skill from it." That's a *human-in-the-loop* design choice — and a defensible one.
2. **No skill version history.** A patch overwrites SKILL.md in place. Recovery is via the snapshot module (whole-library snapshot, not per-skill diff). For a serious procedural memory store, per-skill `git`-shaped history would be nicer.
3. **No skill-level success/failure feedback.** Counters track `use_count`, not `use_count_successful`. A skill that always gets invoked but always fails to deliver looks identical to a skill that always succeeds.
4. **No cross-machine skill sync.** Skills are local to one host. The user has to manually copy `~/.hermes/skills/` or symlink it.

## What This Means for Ember

The mechanics are mostly transferable. Two filters: (a) the Vow of Honest Memory requires more rigorous provenance, and (b) the Vow of Smallness limits the auxiliary-LLM call sites we can afford on a Pi.

### Ember skill layout

Mirror Hermes verbatim under `~/.ember/skills/<slug>/`:

```
~/.ember/skills/<slug>/
├── SKILL.md
├── references/
├── templates/
└── scripts/
```

Three provenance buckets:

- **Bundled** — ships with Ember. Listed in `~/.ember/skills/.bundled_manifest`.
- **Community** — installed via a future Ember equivalent of the hub (Vow of Open Knowledge). For now: empty.
- **User-or-agent** — everything else. Curator-eligible.

The sidecar `.usage.json` is identical in shape to Hermes's. Steal `tools/skill_usage.py:285-340` verbatim.

### Ember skill_manage tool — proposed API

```python
# src/ember/smiðja/skills/manage.py
def skill_manage(
    action: Literal["create", "patch", "write_file", "view", "delete"],
    name: str,
    *,
    content: str | None = None,
    file_path: str | None = None,    # for write_file
    file_content: str | None = None, # for write_file
    absorbed_into: str | None = None,  # required on delete
    reason: str = "",
) -> SkillManageResult: ...
```

The same five-verb shape. `absorbed_into` required on delete to feed the audit trail. `reason` recorded with every mutation in a `.history.jsonl` per-skill (this fixes Hermes's gap of no per-skill history — cheap to add).

### Honest-memory provenance

Vow of Honest Memory says: never fabricate continuity. For skills, that means **every fact in a SKILL.md must be traceable**. Two enforcement mechanisms:

1. **Source-anchored skill blocks.** A SKILL.md section can declare its source: `<!-- source: session 47abf, turn 12 -->`. The curator preserves these markers when consolidating.
2. **`well.cite` integration.** When the agent writes a skill that quotes the user's documents, the chunk IDs from Brunnr are embedded as `<!-- well-chunk: 7a3f, 8c1b -->`. The user can ask "why does this skill say that?" and Ember can show the source chunks.

This adds about 50 lines to Hermes's pattern and makes the resulting library auditable. The Vow of Honest Memory pays for itself: no skill ever claims something it can't trace back.

### The auxiliary-call constraint

Curator's umbrella-finding LLM pass is the only place skill crafting touches an LLM (the rest is filesystem operations). On Pi-tier, that pass runs on local Funi. On Workstation-tier, it can run on a more capable model. On Pi-tier with no peer mesh, *the pass is deferred* if the local model is too small to handle the curator prompt:

```python
# src/ember/smiðja/curator/llm_pass.py
def can_run_llm_pass(tier: TierConfig, candidate_count: int) -> bool:
    """Heuristic: curator prompt is ~5K tokens + ~500 tokens per candidate.

    Pi-tier with 8K context can handle ~6 candidates. Beyond that, defer.
    """
    estimated = 5000 + 500 * candidate_count
    return estimated <= tier.funi_max_context
```

When `can_run_llm_pass()` returns False, the curator logs "skipped: tier insufficient for N candidates" and tries again next interval. The user can:
- Reduce candidates (archive obvious-junk skills manually).
- Use a swarm peer with bigger context.
- Use Strengr with explicit opt-in (`curator.model: strengr`).

This is the [[Vow of Smallness]] in code form. The feature works on Pi; it just defers gracefully.

### Bundle pattern — adopt verbatim

`agent/skill_bundles.py` is so clean it should be a near-1:1 copy. The bundle directory under `~/.ember/skill-bundles/<slug>.yaml`:

```yaml
name: ingest-day
description: A normal Smiðja ingest pass plus the Brunnr health check after.
skills:
  - smithja-ingest-from-dir
  - brunnr-health-check
  - well-vacuum-vacuum-vacuum
instruction: |
  Run as a sequence; if any fails, summarize what got done.
```

Munnr's slash dispatcher resolves `/<bundle>` before `/<skill>` (bundle wins on collision, per Hermes line 30). The forgiving stance — missing member skills are listed, not fatal — is the right default.

### Snapshot before curator — adopt verbatim

`agent/curator_backup.py`'s `snapshot_skills(reason="pre-curator-run")` is exactly the right primitive. Ember's curator should call it before every live run. The snapshot lives under `~/.ember/skills/.snapshots/<timestamp>/` and is recoverable via `ember skills restore <timestamp>`.

This is one of the *cheapest* invariants you can buy: the curator can be aggressive because the user can always undo.

### Vows on the line

- **Vow of Honest Memory** — strengthened by source-anchored skill blocks and per-skill `.history.jsonl`.
- **Vow of Smallness** — strengthened by `can_run_llm_pass()` deferring on insufficient tier.
- **Vow of Public-Friendliness** — strengthened. Skills are markdown; bundles are YAML; both are hand-editable.
- **Vow of Open Knowledge** — preserved. Skills are MIT-licensed by default. Sharing is encouraged; `ember skills export <name>` is a one-command tarball.
- **Vow of Modular Authorship** — strengthened. A broken SKILL.md doesn't crash the agent; it logs at warning and continues (`agent/skill_bundles.py:122` "we don't raise — a broken bundle shouldn't take down slash command discovery").

### What I do not propose

I do NOT propose:
- A skill marketplace with monetization (out of scope; would invite supply-chain concerns).
- Automatic skill creation from successful sessions (too easy to overfit on noise).
- A skill-version-control system (per-skill `.history.jsonl` is enough until proven otherwise).
- Encryption-at-rest for skills (Vow of Smallness — overhead not warranted).

### Where to read next

- [[30_execution/30_SELF_HEALING_LOOP]] — the curator loop that uses these skills.
- [[30_execution/38_PERSISTENT_MEMORY]] — the SessionDB that ground-truths what an agent *did* before turning it into a skill.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — Smiðja's expanded scope to own skill crafting.
- [[50_verification/52_ANTIPATTERN_CATALOG]] — the auto-skill-from-session pattern Ember should avoid.

A skill is past-you teaching future-you. Write it like the apprentice you were when you needed it. — Eldra.
