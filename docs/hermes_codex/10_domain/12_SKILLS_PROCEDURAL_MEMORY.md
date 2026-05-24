---
codex_id: 12_SKILLS_PROCEDURAL_MEMORY
title: Skills as Procedural Memory — How Hermes Remembers How to Do
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - AGENTS.md:587-700
  - AGENTS.md:750-781
  - skills/software-development/test-driven-development/SKILL.md:1-60
  - skills/dogfood/SKILL.md:1-40
  - skills/apple/findmy/SKILL.md:1-50
  - agent/curator.py:1-80
  - agent/curator.py:56-79
  - agent/curator_backup.py
  - agent/skill_utils.py
  - agent/skill_bundles.py
  - agent/skill_commands.py
  - agent/skill_preprocessing.py
  - agent/prompt_builder.py:848-1000
  - tools/skill_manager_tool.py
  - tools/skill_usage.py
  - tools/skill_provenance.py
  - tools/skills_tool.py
  - tools/skills_hub.py
  - tools/skills_sync.py
  - tools/skills_guard.py
  - hermes_cli/skills_config.py
  - hermes_cli/skills_hub.py
  - hermes_constants.py:160-194
ember_subsystem_targets: [Listir, Funi, Munnr, Brunnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/13_TOOLS_SUBSYSTEM
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Skills as Procedural Memory
## How Hermes Remembers How to Do

*— Rúnhild Svartdóttir, Architect*

> *Knowledge of fact and knowledge of method are different bones. You can recall the name of a hammer without knowing how to swing it. Procedural memory is the knowledge of swing. The skill of a system is not what it knows but what it can be told to do once and never need to be told again.*

Hermes's `skills/` and `optional-skills/` directories are *procedural memory*: documents that explain how to do a thing once, so the agent can do the thing thereafter. They are not tools (tools are atomic capabilities); they are not facts (facts go to memory providers); they are recipes — long-form workflows the agent can read and execute. 170 SKILL.md files are bundled with Hermes. Each is a small saga of "how to" written in a format the model can read at scale.

This doc maps the skills domain: the file format, the lifecycle, the discovery layer, the curator, the Hub, and the boundary lines that keep it from drowning the system prompt.

---

## 1. The Two Skill Realms

Hermes has *two* skills directories:

- **`skills/`** (~25 category folders) — bundled, shipped, loadable by default. Categories include: `apple`, `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `diagramming`, `dogfood`, `domain`, `email`, `gaming`, `gifs`, `github`, `index-cache`, `inference-sh`, `mcp`, `media`, `mlops`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`, `yuanbao`.

- **`optional-skills/`** (~18 category folders) — heavier or niche skills shipped with the repo but NOT active by default. Installed explicitly via `hermes skills install official/<category>/<skill>`. Categories: `autonomous-ai-agents`, `blockchain`, `communication`, `creative`, `devops`, `dogfood`, `email`, `finance`, `health`, `mcp`, `migration`, `mlops`, `productivity`, `research`, `security`, `software-development`, `web-development`.

The split is *load discipline*. Bundled skills go into every agent's prompt index. Optional skills must be installed; once installed, they participate. The user pays the system-prompt-token cost only for skills they have opted into. This is one of Hermes's clearer Vow-of-Smallness disciplines.

The adapter lives at `tools/skills_hub.py` (the `OptionalSkillSource` class). Discovery resolution (per `hermes_constants.py:160-194`):

1. `HERMES_OPTIONAL_SKILLS` env var (Nix wrapper / packaged override)
2. `HERMES_BUNDLED_SKILLS` env var
3. Wheel-installed `<sysconfig data>/skills` and `<sysconfig data>/optional-skills`
4. Caller-supplied default (source-checkout path)
5. `<HERMES_HOME>/skills` and `<HERMES_HOME>/optional-skills` (user-installed)

Profile-aware. Cross-platform. No absolute paths. **Vow of Flexible Roots in code.**

---

## 2. The SKILL.md Format

Every skill is a Markdown file with YAML frontmatter. The minimal example (from `skills/dogfood/SKILL.md:1-10`):

```yaml
---
name: dogfood
description: "Exploratory QA of web apps: find bugs, evidence, reports."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, testing, browser, web, dogfood]
    related_skills: []
---
```

Full frontmatter schema (per `AGENTS.md:604-614`):

| Field | Required | Purpose |
|---|---|---|
| `name` | yes | Canonical skill identifier (matches directory name) |
| `description` | yes | One sentence, **≤ 60 characters**, ends with a period |
| `version` | yes | Semver |
| `author` | yes | Human contributor first, then "Hermes Agent" if co-authored |
| `license` | yes | Usually MIT |
| `platforms` | yes | OS-gating list: `[macos]`, `[linux, macos]`, `[linux, macos, windows]` |
| `metadata.hermes.tags` | yes | List of categorization tags |
| `metadata.hermes.category` | optional | Category name (mirrors directory) |
| `metadata.hermes.related_skills` | optional | List of names for related-skill discovery |
| `metadata.hermes.config` | optional | config.yaml settings the skill needs (stored under `skills.config.<key>`, prompted during setup, injected at load) |
| `tags`, `category` | optional | Top-level mirrors of the metadata.hermes.* fields |

The body of the SKILL.md follows a *modern section order* (`AGENTS.md:667-674`):

1. `# <Skill> Skill` title
2. 2–3 sentence intro stating what it does and doesn't do
3. `## When to Use`
4. `## Prerequisites`
5. `## How to Run`
6. `## Quick Reference`
7. `## Procedure`
8. `## Pitfalls`
9. `## Verification`

Target length: ~200 lines for complex, ~100 lines for simple. The TDD skill (`skills/software-development/test-driven-development/SKILL.md`) is a tight example. The Find My skill (`skills/apple/findmy/SKILL.md:1-50`) shows the `platforms: [macos]` gate at work — the skill is only surfaced when the agent is on macOS.

The format is also a *contract* enforced by tooling. Per `AGENTS.md:617-636`:
- Description must be ≤ 60 chars and end with a period (verified by a Python regex assertion in CI)
- Tool references in prose must be native Hermes tools or named MCP servers — no shell utilities the agent already has wrapped
- Platform gating audited against actual script imports (POSIX-only primitives like `fcntl`, `termios`, `os.setsid` must be declared)
- Scripts go in `scripts/`, references in `references/`, templates in `templates/`
- Tests at `tests/skills/test_<skill>_skill.py` use only stdlib + pytest + mock

This is *agentskills.io* — an external open standard Hermes contributes to. Skills written for Hermes can be loaded by other agentskills.io compliant runtimes.

---

## 3. How Skills Get Into the System Prompt

The injection path lives in `agent/prompt_builder.py:997` — `build_skills_system_prompt`. The flow:

1. **Scan all skill roots**: `skills/` (bundled), `optional-skills/` (user-installed), `~/.hermes/skills/` (user-authored or agent-created). `agent/skill_utils.py:iter_skill_index_files` walks them.
2. **Parse frontmatter** (`agent/skill_utils.py:parse_frontmatter`).
3. **Filter by platform**: `agent/skill_utils.py:skill_matches_platform` — gate skills whose `platforms:` doesn't include the current OS.
4. **Filter by disabled list**: `agent/skill_utils.py:get_disabled_skill_names`.
5. **Build a compact index**: just the name + description + tags, *not* the full SKILL.md body.
6. **Cache the snapshot**: `agent/prompt_builder.py:848 — _skills_prompt_snapshot_path`. The snapshot is keyed by skill manifest hash; rebuilt only when skills change.

The index goes into the system prompt under a `SKILLS_GUIDANCE` block (`agent/prompt_builder.py:128-131`). The agent sees: *"Here are skills you can use. To execute one, call `skill_view` for the body, then follow the procedure."*

`skill_view` is the tool that returns the full SKILL.md when the agent decides to use a skill. This keeps the system prompt small (just the index) and pays the body's tokens only when actually invoked.

### 3.1 Custom slash commands from skills

`agent/skill_commands.py` scans `~/.hermes/skills/` and injects skill names as *user message* slash commands (per `AGENTS.md:150-152`). When the user types `/dogfood`, it is rewritten to "use the dogfood skill" and submitted as a user message — *not* a system prompt change. **This preserves prompt caching.** A user message is a different cache region than the system block.

This is a tiny but load-bearing design. Adding skills must never invalidate the system-prompt cache. The path: user runs `/skill`, the slash handler crafts a user message ("use the X skill"), the model reads the system-prompt skill index (cached), the model decides to call `skill_view`, the tool returns the body, the model executes. Zero cache invalidation.

---

## 4. The Curator — Lifecycle Management

Hermes auto-creates skills from successful workflows. The agent can call `skill_manage(action="create", name="...", body="...")` and a new SKILL.md materializes under `~/.hermes/skills/` with `created_by: "agent"` provenance. The system would drown in agent-created skills if there were no maintenance.

The curator (`agent/curator.py`) is the cleaner. From the docstring (`agent/curator.py:1-20`):

> *"The curator is an auxiliary-model task that periodically reviews agent-created skills and maintains the collection. It runs inactivity-triggered (no cron daemon): when the agent is idle and the last curator run was longer than interval_hours ago, maybe_run_curator() spawns a forked AIAgent to do the review."*

Default lifecycle thresholds (`agent/curator.py:56-59`):

```python
DEFAULT_INTERVAL_HOURS = 24 * 7      # 7 days between curator runs
DEFAULT_MIN_IDLE_HOURS = 2           # agent must be idle 2h before run
DEFAULT_STALE_AFTER_DAYS = 30        # mark stale after 30d of disuse
DEFAULT_ARCHIVE_AFTER_DAYS = 90      # archive after 90d
```

Telemetry source: `tools/skill_usage.py` owns the sidecar `~/.hermes/skills/.usage.json` (per `AGENTS.md:760-765`). Each agent-created skill has: `use_count`, `view_count`, `patch_count`, `last_activity_at`, `state` (active / stale / archived), `pinned`.

Invariants (`AGENTS.md:766-774`):

- Only touches agent-created skills (`tools/skill_provenance.is_agent_created`)
- Never auto-deletes; max destructive action is *archive*. Archives go to `~/.hermes/skills/.archive/` and are restorable.
- Pinned skills bypass all auto-transitions and the LLM review pass
- `skill_manage(action="delete")` refuses pinned skills; patch/edit/write_file/remove_file go through so the agent can keep improving pinned skills

Backup mechanism (`agent/curator_backup.py`): tar.gz snapshot before every curator run. If a run does something the user disapproves of, `hermes curator rollback` restores from snapshot.

The CLI (`hermes_cli/curator.py`) exposes the verbs: `status`, `run`, `pause`, `resume`, `pin`, `unpin`, `archive`, `restore`, `prune`, `backup`, `rollback`. The user remains in control. **Never deletes** is the invariant the user trusts.

---

## 5. The Skills Hub

`tools/skills_hub.py` + `hermes_cli/skills_hub.py` + `tools/skills_sync.py` make up the skill *distribution* layer — the bridge between local Hermes and the Skills Hub (GitHub-based).

The Hub serves three populations:
- **Official**: `official/<category>/<name>` (curated by NousResearch)
- **Community**: shared by other users
- **Personal**: the user's own published skills

The auth uses `PyJWT[crypto]` (`pyproject.toml:55`) — GitHub App JWT for bot identity when a user publishes. Read-only browsing requires no auth.

`tools/skills_sync.py` does the actual file transfer: clone the Hub repo, copy the requested skill, install dependencies, register in the index. `tools/skills_guard.py` validates: no path traversal, no surprise binaries, frontmatter passes the description-length check.

This is essentially **a package manager for procedural memory**. The skill is the unit; the manifest is the SKILL.md frontmatter; the registry is git-backed. Decentralization with a soft center.

---

## 6. The Skill Tools

A small family of tools manages the skills themselves:

| Tool | File | Purpose |
|---|---|---|
| `skills_list` | `tools/skills_tool.py` | List available skills, filterable by tag/category |
| `skill_view` | `tools/skills_tool.py` | Return the full SKILL.md body |
| `skill_manage` | `tools/skill_manager_tool.py` | Create, patch, edit, write_file, remove_file, archive, restore, delete |

These are *core* tools (in `_HERMES_CORE_TOOLS` per `toolsets.py:41-42`). Every platform's base toolset includes them. The agent always has the means to consult its own procedural memory and to update it.

The CLI-side counterpart is `hermes_cli/skills_config.py` which feeds the `hermes tools` curses UI for skill enable/disable per platform. And `hermes_cli/skills_hub.py` for `hermes skills install official/...` and the Hub sync flow.

---

## 7. The Three Sources of a Skill

When the agent has a SKILL.md, it can come from one of three sources:

1. **Bundled**: shipped with the wheel/checkout. Read-only for the curator. Updates come from `hermes update`. `metadata.hermes.created_by` is `"hermes"` or the contributor's name.

2. **Hub-installed**: explicitly installed by the user via `hermes skills install`. Lives in `~/.hermes/skills/`. Read-only for the curator. Updates come from `hermes skills sync`. `created_by` is the original author.

3. **Agent-created**: written by the agent at runtime via `skill_manage`. Lives in `~/.hermes/skills/`. `created_by: "agent"`. **Only this class is curator-managed.** Bundled and Hub skills are off-limits to the curator.

The provenance check (`tools/skill_provenance.is_agent_created`) is the boundary line. Without it, the curator could quietly archive a bundled skill the user expected to find.

---

## 8. agentskills.io — The External Standard

Hermes did not invent the SKILL.md format unilaterally. agentskills.io is an emerging open standard for portable procedural memory. The frontmatter fields above are the standard's surface; the `metadata.hermes.*` namespace is Hermes-specific extension.

The TDD skill is credited to `obra/superpowers` (per `skills/software-development/test-driven-development/SKILL.md:5`) — an external skill library. Hermes imports and adapts. This is a *cooperating* ecosystem.

For Ember, the implication is huge: **Ember does not need to invent its own skill format.** Adopting agentskills.io means inherit a corpus of existing skills, with attribution preserved per the Vow of Open Knowledge.

---

## 9. The Skill Authoring Hardline

`AGENTS.md:617-694` lays out a hardline review standard. Reviewers reject PRs that violate it:

1. **Description ≤ 60 characters, one sentence, ends with a period.** No marketing words ("powerful", "comprehensive", "seamless", "advanced"). Don't repeat the skill name.

2. **Tools referenced in prose must be native Hermes tools or named MCP servers.** When the skill needs a capability, name the proper tool: `terminal`, `web_extract`, `read_file`, `patch`, `search_files`, `vision_analyze`, `browser_navigate`, `delegate_task`. Do *not* name shell utilities the agent already wraps (`grep` → `search_files`, `cat`/`head`/`tail` → `read_file`, `sed`/`awk` → `patch`).

3. **Platform gating audited against actual script imports.** POSIX-only primitives (`fcntl`, `termios`, `os.setsid`, `/proc`, hardcoded `/tmp`, `signal.SIGKILL`, bash heredocs, `osascript`, `apt`, `systemctl`) must declare supported platforms. Default posture: fix cross-platform first using `tempfile.gettempdir`, `pathlib.Path`, `psutil.pid_exists`.

4. **Author credits the human contributor first.** "Hermes Agent" is secondary.

5. **Section order strict** (see §2 above).

6. **Scripts/references/templates in their own subdirs.** Don't expect the model to inline-write parsers, XML walkers, or non-trivial logic every call — ship a helper script.

7. **Tests at `tests/skills/test_<skill>_skill.py`** — stdlib + pytest + mock only; no live network.

8. **`.env.example` additions in a clearly delimited block.** Stale contributor edits outside the skill's own block must be dropped during salvage.

This is rare in the open-source world: a documented, enforced quality bar for an extension format. Ember will benefit from copying both the bar and the enforcement.

---

## 10. Skills as the Anti-Bloat Pattern

Why does this matter architecturally? Because skills are the answer to a question every agent system asks: *"How do we keep adding capabilities without bloating the system prompt?"*

The naïve answer is "more instructions in the prompt." The bloat answer is "more tools." The Hermes answer is **procedural memory**: capabilities live in their own files, the prompt contains only an *index*, and the body is paid-for on demand via `skill_view`.

A Hermes session with 170 bundled skills costs *only* the system-prompt index (a few thousand tokens at most, depending on description count). The bodies stay on disk. The agent reads a body when it has decided to do that workflow. The model's attention is not diluted by every instruction the system can possibly hold.

This pattern scales. It does not violate prompt caching. It does not require a separate retrieval system. It is a file system being used as a paged memory hierarchy. *Brilliantly mundane.*

---

## What This Means for Ember

**Proposed new True Name: Listir** (Old Norse: "arts, skills, accomplishments"). Listir is the procedural-memory subsystem — distinct from Funi (model), Munnr (mouth), Brunnr (factual memory), Smiðja (ingest), Hjarta (setup), Strengr (network). She is the *arts* the agent has learned to perform.

Lives in: `src/ember/spark/listir/` (proposed). Realm: Spark — Listir is local; her files are on the device.

Reads from: Brunnr (skill content can be cross-referenced into the knowledge DB for full-text search). Writes to: itself (`~/.ember/skills/.../SKILL.md`).

Calls out to: Verkfæri (the tool framework — for `skill_view`, `skill_manage`, `skills_list`).

### Concrete proposals

1. **Adopt agentskills.io as the SKILL.md format.** Same frontmatter, same section order, same hardline standards. Inherit Hermes's 170 bundled skills (with attribution preserved). Add an `ember:` namespace for Ember-specific metadata when needed; otherwise share the standard. This honors the **Vow of Open Knowledge** and the **Vow of Smallness** (a 60-char description fits any model's context).

2. **Adopt the index-not-body pattern as a Vow-level discipline.** System prompt holds the *index*; bodies are paid-for via a `skill_view` tool. This is one of the cheapest ways to keep Ember small while she scales in capability.

3. **Adopt the two-realm split (bundled vs. optional).** Bundled skills ship in the wheel; optional skills install on demand. The user pays the system-prompt-token cost only for skills they have opted into. The discovery resolution from `hermes_constants.py:160-194` is portable; copy it.

4. **Adopt provenance enforcement.** Three sources: bundled (read-only), Hub-installed (read-only for curator), agent-created (curator-managed). The `created_by` frontmatter field is the boundary. Without provenance, a curator can quietly erase a bundled skill the user counted on.

5. **Adopt the curator pattern, with one Vow tweak.** Hermes's curator never deletes; max destructive action is archive. **Ember's curator should match this exactly**, and should *also* refuse to run unless explicitly enabled in the operator's config. The Pi-class hardware target means we cannot afford to surprise the user with a background auxiliary-model job. Default-off for the curator; the operator opts in once they have the hardware budget.

6. **Defer the Skills Hub for now.** Hermes's Hub depends on GitHub, JWT auth, and a sync flow that requires `git` on the device. For a Pi/off-grid setup, a *local* skills directory is sufficient. The Hub adapter is a slice-N feature.

7. **Adopt the slash-command-as-user-message pattern.** When the operator types `/foo`, Munnr should rewrite it to "use the foo skill" and submit as a user message. This preserves prompt caching exactly the way Hermes does it.

8. **Adopt the prompt-injection scanner from `agent/prompt_builder.py:36-74` for skill files.** A user-installed SKILL.md is an attack surface — someone might Hub-install a skill whose body contains "ignore your prior instructions." The same threat-pattern regex set used for AGENTS.md/.cursorrules applies to skill bodies. Run it before injection.

**Affected True Names:** **Listir** (new), **Munnr** (slash-command rewrite), **Funi** (system-prompt assembly with skill index), **Brunnr** (optional cross-reference of skill bodies into the knowledge DB for search).

**Vows reinforced:** **Vow of Smallness** (index-not-body), **Vow of Honest Memory** (provenance enforcement), **Vow of Modular Authorship** (each skill is its own file), **Vow of Open Knowledge** (agentskills.io standard).

**Vows at risk if mis-ported:** **Vow of Smallness** if Ember tries to load skill bodies eagerly. **Vow of Public-Friendliness** if curator deletion behavior is not made explicit. **Vow of Graceful Offline** if the Hub becomes a hard dependency.

The art of doing is a different art than the art of knowing. Listir is for the doing. The procedural memory pattern Hermes pioneered for agentic systems is one of the genuinely good ideas in the field. Ember inherits it whole — and refines it for smaller fires.
