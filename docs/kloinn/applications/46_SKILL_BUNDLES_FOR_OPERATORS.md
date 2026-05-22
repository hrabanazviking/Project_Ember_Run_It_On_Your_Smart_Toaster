# 46 — Skill Bundles for Operators

How specifically to add operator-installable skill bundles to
Ember without a centralized registry.

---

## What a skill bundle is

A *skill bundle* is a pip package that adds capabilities to
Ember:

```
ember-skill-X/
  pyproject.toml
  ember_skill_X/
    __init__.py
    SKILL.md            # prompt fragment for the agent
    TOOLS.md            # tool docs (auto-generated or curated)
    tools/
      tool_a.py
      tool_b.py
    config.yaml         # default config
    tests/
      test_tools.py
```

Operator runs `pip install ember-skill-X`; Ember discovers it
via entry points; the agent gains the skill's tools + prompt
fragments.

---

## Discovery via entry points

In `pyproject.toml` of `ember-skill-X`:

```toml
[project.entry-points."ember.skills"]
travel_planner = "ember_skill_X:register"
```

Ember at startup:

```python
import importlib.metadata

for entry_point in importlib.metadata.entry_points(group="ember.skills"):
    register_fn = entry_point.load()
    register_fn(skill_registry)
```

Each skill's `register` function adds its tools, prompt
fragments, etc.

---

## The Skill Protocol

```python
class Skill(Protocol):
    NAME: ClassVar[str]
    VERSION: ClassVar[str]
    
    def tools(self) -> list[ToolDescriptor]:
        """Tools provided by this skill."""
        ...
    
    def prompt_fragment(self) -> str | None:
        """SKILL.md content; injected into system prompt."""
        ...
    
    def tools_documentation(self) -> str | None:
        """TOOLS.md content; describes tools to the agent."""
        ...
    
    def health(self) -> SkillHealth:
        """Is the skill ready to use?"""
        ...
```

Implementations register tools + prompts when loaded.

---

## Configuration shape

```yaml
ember:
  skills:
    discovery:
      auto_load_entry_points: true
    
    enabled:
      - ember-skill-code-review
      - my-custom-skill        # operator-authored
    
    disabled: []
    
    audit:
      record_load: true
      record_tool_use: true
```

Operator controls which installed skills are active.

---

## What ships in core vs as skills

🔵 **Borrow as-is**: tier classification:

### Core (always available)

- `search_well` — fundamental retrieval.
- `read_local_file` — fundamental I/O.
- `fetch_url` — fundamental network.

These are in `src/ember/tools/` always.

### Bundled skills (ship in core; operator can disable)

Future:
- `ember-skill-cron` (when daemon mode lands).
- `ember-skill-write-files` (when write tools ship).
- `ember-skill-bridges-matrix` (bridges as skill bundle).
- `ember-skill-bridges-telegram`.

Operator can disable via `ember.yaml`.

### Community skills (pip-installable; opt-in)

Anything else. Operator audits + installs + enables.

---

## Audit tool for community skills

```bash
ember skill audit ember-skill-X

Auditing ember-skill-X v1.2:

Tools registered (3):
  ✓ search_my_data: search a specific data source
  ✓ download_my_data: download to local file
  ✓ format_my_data: format JSON to markdown

Network endpoints contacted:
  ⚠ api.example.com/v2/* (when search/download called)
  No other network calls detected (per static analysis).

Required environment:
  MY_API_KEY (referenced in tools/_auth.py:14)

Dependencies:
  requests >= 2.30
  pydantic >= 2.0

Sensitive operations:
  - download_my_data writes to disk (default: ~/my-data/)
  - Operator can change destination via config

License: MIT
Last release: 2 weeks ago
Issues: 3 open, 12 closed

Proceed? [y/n]:
```

Static analysis: look for `requests.get`, `urllib.request`,
`os.system`, etc. Report what's there. Operator decides.

This is **trust but verify**. We provide the verification
tool.

---

## Skill template

Provide a template for operators wanting to build skills:

```bash
ember skill scaffold my-new-skill

Created ./my-new-skill/ with:
  pyproject.toml
  ember_skill_my_new_skill/
    __init__.py
    SKILL.md
    TOOLS.md
    tools/__init__.py
    tools/example_tool.py
  tests/test_example_tool.py
  README.md

Next steps:
  1. Edit ember_skill_my_new_skill/tools/example_tool.py
  2. Update SKILL.md with the agent's role for your skill
  3. Update TOOLS.md to document the tool
  4. pytest tests/
  5. pip install -e .

Ember will discover your skill the next time it starts.
```

This is *operator empowerment*: build your own skill in
minutes.

---

## Discovery docs (curated, not registry)

`docs/community-skills.md` curated list:

```markdown
# Community Skills

Operator-contributed skills. We curate this list; we don't
run a registry.

## Code review

**ember-skill-code-review** (by @user)
  https://github.com/user/ember-skill-code-review
  Tools: git_diff_review, lint_check, suggest_changes
  License: MIT
  Maintenance: Active (last commit 1 week)
  Audit: Ember team reviewed v1.2; clean.
  
  Install: `pip install ember-skill-code-review`

## News briefing

**ember-skill-news-briefing** (by @other-user)
  ...
```

Curators (maintainers) review skills before adding to the list.
Skills can be flagged / removed if quality degrades.

This is *lighter than a registry*: we don't host code, only
the list.

---

## What about skill versioning

Skills are pip packages; pip handles versioning.

Operator can pin versions:
```yaml
ember:
  skills:
    pinned_versions:
      ember-skill-code-review: "1.2.3"  # don't auto-update
```

---

## Skill loading order

If multiple skills register conflicting tools (same name),
loading order matters.

```yaml
ember:
  skills:
    enabled:
      - ember-skill-a
      - ember-skill-b      # if conflict, b's tool wins
```

Last-loaded wins. Operator can swap order.

Better: skills should namespace their tools to avoid
conflicts: `ember-skill-A.read_file` vs `ember-skill-B.read_file`.

The Skill Protocol can enforce: tools must be prefixed by
skill name.

---

## Disabling skills temporarily

```bash
ember skill disable ember-skill-X    # disable until re-enabled
ember skill enable ember-skill-X
ember skill list                      # show all installed; enabled status
```

Useful when debugging: disable possibly-conflicting skills.

---

## Skill + sandbox interaction

If a skill's tool requires sandbox (per
[`43_SANDBOXING_LAYER_FOR_TOOLS.md`](43_SANDBOXING_LAYER_FOR_TOOLS.md)):

```python
@register_tool(
    name="run_my_thing",
    sandbox_required=True,
    sandbox_preference=["docker", "subprocess"],
)
def run_my_thing(...):
    ...
```

The skill declares; the runtime enforces.

If a skill *doesn't* declare sandbox but the operator wants
extra safety: configure globally:

```yaml
ember:
  skills:
    override_sandbox:
      ember-skill-X:
        all_tools: docker
```

---

## Phase 2-3 ship plan

🔵 **Phase 1-2**: Skill Protocol + entry-point discovery +
audit tool.

🟢 **Phase 2-3**: First few bundled skills (cron, write files,
etc.).

🟡 **Phase 4+**: Community skills become viable as ecosystem
develops.

---

## What we don't do

🔴 **Reject**:

### 1. Auto-install community skills

Operators always opt in. No "Ember discovered skill X; install?"
prompts.

### 2. Hosted skill registry

We don't run a registry. Period.

### 3. Skill-marketplace UX

No "browse skills" Stofa screen. Skills are found via
docs/community-skills.md + PyPI.

---

## Privacy in skills

Skills must declare:
- Network endpoints they contact.
- Files they read/write.
- Environment variables required.
- Sensitive operations (disk write, network, etc.).

Skill audit tool reports these. Operators decide if comfortable.

If a skill's behavior changes (e.g., adds new network
endpoint), operator must re-audit before re-enabling.

---

## Closing

Skill Bundles for Operators is **OpenClaw's mass-distribution
pattern adapted to sovereignty**. Pip packages + entry points +
audit tool + curated docs list.

No registry. No centralized control. Operators choose; operators
verify; operators install.

Phase 1-2 ships the Protocol + discovery; Phase 3+ ships
bundled skills + community ecosystem.

This is the **right shape for Ember's cohort**. Power-users
build skills; everyone else picks from curated list. The
operator stays in charge.
