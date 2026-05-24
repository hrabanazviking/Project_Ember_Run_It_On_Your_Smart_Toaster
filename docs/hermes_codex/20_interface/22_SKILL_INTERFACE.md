---
codex_id: 22_SKILL_INTERFACE
title: Skill Interface — The agentskills.io Contract
role: Cartographer
layer: Interface
status: draft
hermes_source_refs:
  - tools/skill_manager_tool.py:107-275
  - tools/skill_manager_tool.py:217-253
  - tools/skill_manager_tool.py:713-790
  - agent/skill_utils.py
  - agent/skill_bundles.py
  - agent/skill_commands.py
  - agent/skill_preprocessing.py
  - skills/software-development/writing-plans/SKILL.md
  - skills/software-development/test-driven-development/SKILL.md
  - skills/software-development/hermes-agent-skill-authoring/SKILL.md
  - optional-skills/mcp/fastmcp/SKILL.md
ember_subsystem_targets: [Funi, Munnr, Brunnr, Smiðja]
cross_refs:
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/21_RPC_INTERFACE
  - 10_domain/12_SKILLS_PROCEDURAL_MEMORY
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/63_INTEGRATION_PATHS
---

# 22 — Skill Interface: The agentskills.io Contract

> *Procedural memory does not need to be a database. It needs to be a directory full of letters the agent wrote to its future self.*
> — Védis Eikleið, on the shape of remembered method

## 1. What a "skill" is to Hermes

A Hermes skill is **a directory containing a `SKILL.md` file with YAML frontmatter and a Markdown body**. That is the entire mechanical definition. There is no database, no compiled artifact, no entry point, no plugin manifest. The system reads SKILL.md at session start, presents the agent with a list of available skills by name and description, and lets the agent ask for the body of any one of them via the `skill_view` tool.

This is a deliberately spare contract. It cannot run code on its own. It is not a tool. It is *procedural memory* in the cognitive-science sense: a recallable procedure the agent applies when its retrieval/recall pattern says "the user asked for X — the writing-plans skill applies." The agent then reads the body of that skill and follows its instructions, using whichever real tools (read_file, write_file, terminal, etc.) the procedure recommends.

This is the cleanest example I have seen of **knowledge-as-Markdown**, and it is the model Ember should adopt directly. Skills do not need to be plugins; plugins do not need to be skills. They are different shapes.

## 2. The validator is the contract

`tools/skill_manager_tool.py:217-253` defines `_validate_frontmatter`, the only enforcing gate. Here is the validation surface in full:

```python
def _validate_frontmatter(content: str) -> Optional[str]:
    if not content.strip():
        return "Content cannot be empty."

    if not content.startswith("---"):
        return "SKILL.md must start with YAML frontmatter (---). ..."

    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return "SKILL.md frontmatter is not closed. ..."

    yaml_content = content[3:end_match.start() + 3]

    try:
        parsed = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        return f"YAML frontmatter parse error: {e}"

    if not isinstance(parsed, dict):
        return "Frontmatter must be a YAML mapping (key: value pairs)."

    if "name" not in parsed:
        return "Frontmatter must include 'name' field."
    if "description" not in parsed:
        return "Frontmatter must include 'description' field."
    if len(str(parsed["description"])) > MAX_DESCRIPTION_LENGTH:
        return f"Description exceeds {MAX_DESCRIPTION_LENGTH} characters."

    body = content[end_match.end() + 3:].strip()
    if not body:
        return "SKILL.md must have content after the frontmatter ..."

    return None
```

Twelve enforced rules, no more. The contract is:

1. File starts with `---` at byte 0 (no leading blank line, no BOM).
2. A closing `---` line exists somewhere after.
3. The block between parses as a YAML mapping.
4. The mapping has a `name` key.
5. The mapping has a `description` key.
6. The description is ≤ `MAX_DESCRIPTION_LENGTH = 1024` chars (line 112).
7. The body after the closing `---` is non-empty.

Constants from `tools/skill_manager_tool.py:107-172`:

```python
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000   # ~36k tokens at 2.75 chars/token
MAX_SKILL_FILE_BYTES = 1_048_576    # 1 MiB per supporting file
VALID_NAME_RE = re.compile(r'^[a-z0-9][a-z0-9._-]*$')
ALLOWED_SUBDIRS = {"references", "templates", "scripts", "assets"}
```

That is the entire contract surface. Everything else — `version`, `author`, `license`, `metadata.hermes.tags`, `metadata.hermes.related_skills`, `platforms` — is **convention, not validation**. Peer skills include them; the validator never checks them. This is an unusually permissive contract for something that ships with so much surrounding ceremony.

## 3. The peer-matched shape

Look at the frontmatter of `skills/software-development/writing-plans/SKILL.md:1-12`:

```yaml
---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---
```

And `skills/software-development/test-driven-development/SKILL.md:1-12`:

```yaml
---
name: test-driven-development
description: "TDD: enforce RED-GREEN-REFACTOR, tests before code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, tdd, development, quality, red-green-refactor]
    related_skills: [systematic-debugging, writing-plans, subagent-driven-development]
---
```

Two skills, identical frontmatter shape. This is the **peer-matched convention** described in `skills/software-development/hermes-agent-skill-authoring/SKILL.md:42-53`. The fields beyond `name` + `description`:

- `version` — semver, advisory.
- `author` — provenance string.
- `license` — usually MIT.
- `platforms` — list of OSes this skill applies to. Advisory; not enforced.
- `metadata.hermes.tags` — tags for filtering / surfacing during retrieval.
- `metadata.hermes.related_skills` — graph edges to other skills. Used by retrieval to expand the recall set.

The `metadata.hermes.related_skills` field is the closest thing the skill system has to a **dependency graph**. It is not enforced at load time; it is consumed by `agent/skill_utils.py` when the agent is computing which skills to surface for a given query. Hermes treats it as a hint, not a contract — a skill can reference a related skill that does not exist (e.g., from a previous version of the repo), and nothing breaks; the reference simply fails to resolve and is ignored.

## 4. The lifecycle — discovery, load, invoke, retire

### Discovery

`agent/skill_utils.py::get_all_skills_dirs()` (referenced from `tools/skill_manager_tool.py:286-295`) returns the list of roots Hermes scans. There are three:

1. `~/.hermes/skills/` — user-local skills.
2. `<package>/skills/` — in-repo bundled skills.
3. `<package>/optional-skills/` — opt-in extra skills (you have to explicitly enable a category).

Discovery is **filesystem walk plus filter**:

```python
for skills_dir in get_all_skills_dirs():
    if not skills_dir.exists():
        continue
    for skill_md in skills_dir.rglob("SKILL.md"):
        if is_excluded_skill_path(skill_md):
            continue
        if skill_md.parent.name == name:
            return {"path": skill_md.parent}
```

`tools/skill_manager_tool.py:286-295`. `rglob("SKILL.md")` is the discovery primitive. Exclusion is via a deny list (`agent/skill_utils.py::is_excluded_skill_path`). **No registry, no manifest, no plugin index.** The filesystem is the registry.

### Load

When the agent starts a session, it builds a list of `(name, description, path)` tuples by walking every `SKILL.md` and reading its frontmatter only. The bodies are not loaded at session start — they remain on disk until invoked. This is the **lazy-body** optimisation that lets Hermes ship ~100+ skills without putting them all in the system prompt.

Frontmatter cache lives in `agent/skill_utils.py` (the broader file we haven't fully read; pattern is inferable from the size and reference points). The cache key is the skill directory's mtime. A user edit invalidates the cached frontmatter but not the body.

### Invoke

The agent has two tools, defined in `tools/skill_manager_tool.py` and exposed via `skill_view` / `skills_list`:

- **`skills_list`** — returns the (name, description) tuples for every visible skill. This is what the agent uses to decide which skill applies to the current user request. The descriptions are designed to be predictive: each starts with "Use when X" so a single scan tells the agent which skill is relevant.
- **`skill_view`** — given a skill name, returns the full body of its SKILL.md. The agent reads this, follows the instructions, and uses *other* tools to do the actual work.

The mental model is: **`skills_list` is a directory of letters; `skill_view` opens one and reads it.** No code is run by viewing a skill. The skill body might say "run `pytest -v` and check the output" — but the running is done by the `terminal` tool, not by the skill loader.

### Retire

Skills are retired by deletion. The `skill_manage` tool action `delete` (`tools/skill_manager_tool.py:747-749`) removes the directory. Pinned skills are exempt — see `_pinned_guard` at `tools/skill_manager_tool.py:137-161`:

```python
def _pinned_guard(name: str) -> Optional[str]:
    """Pin protects a skill from deletion ... only deletion is blocked."""
```

Pinning is a sidecar concept — it lives in `tools/skill_usage.py` (referenced but not the focus of this doc) and gets consulted before destructive ops.

## 5. Skill self-creation — the loop closes

The most consequential thing skills enable: **Hermes can create its own skills.** The `skill_manage(action="create", ...)` action at `tools/skill_manager_tool.py:730-735` is exposed *to the agent itself* as a tool. The agent can decide, mid-conversation, that a procedure it just invented is worth saving for next time, write a `SKILL.md`, and call `skill_manage(action="create", name="...", content="...")`.

The validator runs at write time (line 385: `err = _validate_frontmatter(content)`). The skill is rejected if it fails. The skill is *not* visible to the current session — the loader is cached at session start (`skills/software-development/hermes-agent-skill-authoring/SKILL.md:124-126` documents this explicitly). It becomes visible to the *next* session.

This is **procedural memory as deliberate practice**. The agent encounters a problem, solves it, writes down how it solved it, and the next instance of itself reads the procedure. The same pattern Ember could adopt to grow her own playbook over time without growing her local model.

## 6. The size discipline

`MAX_SKILL_CONTENT_CHARS = 100_000` (line 164). That is the per-skill cap, ~36k tokens. The validator enforces it at write. The recommended sweet spot per `skills/software-development/hermes-agent-skill-authoring/SKILL.md:60-64`: 8-15k chars per skill.

When a skill grows past 20k, the convention is to **split into `references/*.md`** and reference them from SKILL.md. The supporting-files mechanism is mediated by `ALLOWED_SUBDIRS = {"references", "templates", "scripts", "assets"}` (line 171). These are the only subdirectories an in-repo skill is permitted to have. The agent's `skill_manage(action="write_file", ...)` honours this allowlist.

This discipline is what keeps the skill corpus *readable*. A skill that grew to 50k chars would lose its essence and become an unreadable spec. The cap forces refactoring into supporting files, which keeps SKILL.md as the index.

## 7. The retrieval question — how does the agent know which skill applies?

There are three answers depending on which version of Hermes you read:

1. **Token-budgeted full-list injection.** The simplest: every skill's `(name, description)` tuple is injected into the system prompt. The agent reads them all and picks. This works for ~30-50 skills before it eats the context budget.
2. **Tag-filtered surfacing.** When skill count grows, the agent surfaces only skills whose tags match the current user request. `metadata.hermes.tags` is the input; an embedding or keyword filter is the mechanism.
3. **Embedding-recall.** The descriptions get embedded once at index time. At session start, the user's first message gets embedded, and top-K nearest skills get surfaced. This is where Hermes is heading per the optional-skills/ category counts (~30+ categories, hundreds of skills).

Ember can start with option 1. With 5-10 skills (the realistic Ember-scale skill count for v1), the full list fits in 1-2k tokens of system prompt. By option 3 time, Ember's Brunnr (with embedding-based retrieval) is the natural substrate — and that is where the synthesis docs get interesting (see [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]).

## 8. The two writable trees

`skills/software-development/hermes-agent-skill-authoring/SKILL.md:17-21` makes this distinction load-bearing:

> 1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
> 2. **In-repo:** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

This **two-tree separation** is exactly right. The user-local tree is mutable, agent-writable, ephemeral-ish (lives in `$HERMES_HOME`). The in-repo tree is source code, requires a code review, ships in releases. Both are visible to the loader; only one is agent-writable.

For Ember: the in-repo tree maps to `src/ember/skills/`. The user-local tree maps to `~/.ember/skills/`. The same two-tree pattern, transcribed.

## 9. The cross-tree edges

`metadata.hermes.related_skills` is a list of names. Resolution is **across both trees** at load time (`skills/software-development/hermes-agent-skill-authoring/SKILL.md:128-130`):

> `metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh.

This is a soft constraint — the system does not enforce it, but the convention is "prefer referencing only in-repo skills from in-repo skills." It is a portability discipline.

## 10. The agentskills.io angle

The url `agentskills.io` appears in the SHARED_CONTEXT brief; it points to a public registry of agent-skills using this same contract. Hermes ships its in-repo `skills/` tree as a reference implementation. A skill that conforms to Hermes's validator can be published to agentskills.io and consumed by any compatible agent.

The contract is **the validator output of `_validate_frontmatter`**. Nothing else. A SKILL.md that passes Hermes's validator is portable to any agent that adopts the same seven-rule check. There is no protocol negotiation, no version handshake; the file format is the protocol.

This is the cleanest example of **format-as-protocol** in the agent ecosystem today. Markdown + a tiny YAML preamble. Greppable. Versionable. Diffable. Forkable. Ember should adopt this verbatim.

## 11. What the validator does *not* enforce — and why that's right

- No name uniqueness across trees. (Conflict resolution is "first found wins" in the discovery walk.)
- No `version` semver check. (The string is metadata, not behaviour.)
- No `description` quality check. (No "must start with 'Use when'" rule.)
- No `related_skills` resolution check. (Dangling references are silent.)
- No `platforms` enforcement. (Advisory only.)
- No body Markdown lint. (The body is human-and-agent-readable text.)

Each absence is a virtue. The cost of a strict validator is high — every author has to fight the checker. The cost of a loose validator is low — bad skills get rewritten by their authors when they fail in practice. Hermes chose loose, and the corpus is healthier for it.

## What This Means for Ember

**True Names affected:**

- **Funi (flame).** Funi's tool dispatch is the consumer of skills. A new `funi/skills/` module hosts: `loader.py` (the `_validate_frontmatter` validator + `rglob("SKILL.md")` discovery), `surfacer.py` (the strategy that picks which skills to inject into the system prompt), and the two model-facing tools `skills_list` / `skill_view`. The validator can be ported almost verbatim — the only adaptation needed is the absolute-path scrubbing per Vow of Flexible Roots.
- **Munnr (mouth).** The agent's self-creation flow (`skill_manage(action="create", ...)`) is a Munnr-shaped surface because the user observes it. The CLI command `ember skills list` / `ember skills view <name>` / `ember skills create` lives in Munnr. When the agent itself decides to write a skill mid-chat, Munnr's audit log records the write.
- **Brunnr (well).** Embedding-based skill retrieval (option 3 from §7) is a Brunnr concern, not a Funi one. The skill descriptions become a small corpus that Brunnr indexes with the same `hybrid_search` interface the main Well uses. The Vow of Pluggable Storage means this works against any backend.
- **Smiðja (forge).** Skills can be *ingested* like any other content. A new content source `smidja/sources/skills_dir.py` walks `~/.ember/skills/` and `src/ember/skills/`, chunks the bodies, embeds the descriptions, deposits into Brunnr. The result: skill retrieval and Well retrieval use the same machinery.

**Vows touched:**

- *Reinforced:* Vow of Smallness (no database, no plugin framework — just a filesystem walk); Vow of Open Knowledge (skills are Markdown and ship with the repo); Vow of Public-Friendliness (a non-developer can read a skill and understand what it does); Vow of Pluggable Storage (skills are content, not infrastructure); Vow of Modular Authorship (a malformed skill is silently dropped, the corpus stays healthy).
- *Strain test:* Vow of Tethered Grounding — skills are *procedure*, not *fact*. They tell the agent "how" but never "what is true." The boundary needs to stay sharp: skills must never embed claims that should live in the Well. Lint warning candidate: "skill body contains factual assertion patterns ('the Pi 5 has 8 GB of RAM') — extract to Well content."
- *At risk:* The Vow of Honest Memory — agent-created skills could fabricate context if the agent's reasoning during creation was confabulated. Mitigation: every agent-created skill carries an `author: ember-agent` field and a `provenance: session/<session_id>` field; the operator can audit them.

**Specific code-level adoption proposals:**

1. `src/ember/spark/funi/skills/loader.py` — port the validator verbatim, change `HERMES_HOME` → `Path.home() / ".ember"`, keep the constants (`MAX_NAME_LENGTH = 64`, `MAX_DESCRIPTION_LENGTH = 1024`, `MAX_SKILL_CONTENT_CHARS = 100_000`).
2. `src/ember/spark/funi/skills/surfacer.py` — start with strategy 1 (token-budgeted full-list injection). Hook the strategy choice to a config knob `skills.surface_strategy: full_list | tags | embedding` for future expansion.
3. `src/ember/spark/funi/tools/skill_view.py` and `skill_list.py` — the two read-only tools.
4. `src/ember/spark/munnr/skill_commands.py` — operator-facing CLI subcommands `ember skills list/view/create/edit`.
5. `src/ember/skills/` — the in-repo seed corpus. Ship ~5 skills initially: `writing-plans` (adapted from Hermes), `test-driven-development` (adapted), `ember-skill-authoring` (a fresh meta-skill written for Ember), `tethered-grounding-discipline` (Vow-shaped), `graceful-offline-degradation` (Vow-shaped).

**Cross-platform check:** `Path.rglob` and `yaml.safe_load` are both stdlib-friendly (yaml is the one runtime dep — already required for the config loader per ADR 0008). No platform-specific code anywhere.

**Concrete deferral:** the security scan (`tools/skill_manager_tool.py:80-102`, referenced as `_security_scan`) is **not** in scope for Ember v1. Skills in Hermes can ship `scripts/` that get executed; Ember should *not* ship that capability. Skills in Ember are read-only documents. The agent reads them, applies them, but never runs scripts from them. This is a deliberate narrowing — a smaller surface, a smaller threat model, a Vow-of-Smallness-respecting choice.

**Cross-references:**
- The `agentskills.io` ecosystem context lives in [[10_domain/12_SKILLS_PROCEDURAL_MEMORY]] (Architect's territory).
- The self-creation execution detail lives in [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] (Forge's territory).
- The MCP / RPC interfaces that consume skill data (`skills_list`, `skill_view` as MCP-exposed tools) live in [[20_interface/20_MCP_INTEGRATION]] and [[20_interface/21_RPC_INTERFACE]].
- The True Name proposal for whether skills get their own subsystem (working name **Lærdómr**, learned-knowledge) is in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]].
- The migration plan for staging skill adoption is in [[60_synthesis/64_MIGRATION_PLAN]].
