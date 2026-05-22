# 18 — Skill Registry and Bundles

OpenClaw's "skills" — operator-curated capability bundles —
and the ClawHub registry that distributes them.

---

## What skills are

In OpenClaw, **skills** are reusable capability bundles. Each
skill packages:

- One or more tools.
- Prompt fragments that teach the agent how to use them.
- Optional Lua/scripting glue.
- Documentation.

Operators install skills to gain new abilities. Example skills
(hypothetical):

- `code-review` — tools for git diff, lint, suggest changes.
- `travel-planner` — search flights, hotels, suggest itineraries.
- `news-briefing` — fetch RSS feeds, summarize headlines.
- `health-tracker` — read fitness data, suggest patterns.

Skills are *first-class artifacts* — operators browse, install,
configure them.

---

## How skills are distributed

OpenClaw has three channels:

1. **Bundled** — ships with OpenClaw core. Always available.
2. **Managed** — comes from ClawHub registry. Community-curated.
   Auto-update channels (stable / beta / dev).
3. **Workspace** — operator-authored in workspace/skills/. No
   registry.

ClawHub appears to be a centralized registry — operators browse,
install, update from one place.

---

## Why skills work

### Operator-friendly

Adding capability without writing code. Operator can `openclaw
install skill <name>` and have new tools.

### Community amplification

One operator builds a skill; thousands can use it. Network
effect.

### Curated quality

ClawHub gatekeeps quality (review, deprecation, security).

### Composable

Multiple skills combine; the agent inherits their tools.

---

## What this teaches Ember

### Pattern: capability as bundle

A *bundle* (one package, one purpose, one set of files) is a
useful operator-facing abstraction. Better than "install these
six things separately."

Ember could adopt this. Pip packages can play this role:
`ember-skill-code-review` installs tools + prompts + docs.

### Pattern: three-tier distribution

bundled / managed / workspace is good thinking:

- **Bundled** = trustworthy core.
- **Managed** = community contributions, curated.
- **Workspace** = operator's own work.

Ember already has bundled (the three core tools). The other tiers
are absent.

### Pattern: prompt fragments per skill

A skill includes prompt fragments telling the agent how to use
its tools. This integrates with
[`12_PROMPT_INJECTION_FILES.md`](12_PROMPT_INJECTION_FILES.md):
each skill ships a `SKILL.md` injected into context.

---

## What Ember should NOT borrow

🔴 **Reject ClawHub registry**.

The Vow of Modular Authorship favors operator-curated, not
centralized-marketplace. Ember will not run a registry.

Reasons:

1. **Maintenance**: registries require moderation, infrastructure,
   trust governance.
2. **Centralization**: a registry becomes a *single point of
   failure / trust* for all skills.
3. **Quality variance**: registries inevitably have bad skills;
   operators get hurt.
4. **License complexity**: registry-distributed code introduces
   licensing edge cases.

OpenClaw can absorb these costs because they have community
size + maintainer capacity. Ember cannot.

---

## What Ember should borrow

🟢 **Adapt to Ember Vows**:

### 1. Skills as PyPI packages

Skills can be *standard pip packages*:

```bash
pip install ember-skill-travel-planner
```

The package implements the skill protocol; Ember discovers it
via entry points.

Operators *opt into* skills they want. Each is a separate
package; operator chooses what to install.

No centralized registry. Operators discover skills via:
- Project documentation (`docs/community-skills.md`).
- PyPI search.
- Operator-to-operator word-of-mouth.
- Operator-authored.

### 2. Skill bundles

A skill package contains:

```
ember_skill_X/
  __init__.py
  SKILL.md           # prompt fragment
  TOOLS.md           # tool documentation
  tools/
    tool_a.py
    tool_b.py
  config.yaml        # default config
```

Discovered via entry point:

```python
# pyproject.toml of ember-skill-X:
[project.entry-points."ember.skills"]
travel_planner = "ember_skill_X:register"
```

When `ember chat` starts, it imports all entry-points and
registers their tools.

### 3. Operator-controlled enable/disable

```yaml
ember:
  skills:
    enabled:
      - ember-skill-code-review
      - ember-skill-news-briefing
    disabled:
      - ember-skill-experimental
```

Operator decides which installed skills are active.

---

## What workspace-skills look like

A simpler tier than pip packages: operator-authored skills in
their workspace directory:

```
~/.ember/workspace/
  skills/
    my-custom-skill/
      SKILL.md
      tool.py
```

Loaded at chat-start. No pip install needed. Operator-only.

This is the *most sovereign* tier — no third-party code; full
operator authorship.

---

## Bundled skills (in core)

The current three tools (`search_well`, `read_local_file`,
`fetch_url`) are *core* — not skills, just always-on capabilities.

For V2+, we might decide some additions belong as *bundled
skills* — shipping in core but conceptually separate:

- `ember-skill-note-taking` — read/write workspace notes.
- `ember-skill-cron` (when daemon mode lands) — scheduled tasks.
- `ember-skill-bridges-matrix` — Matrix integration.

These could be sub-modules of `src/ember/skills/` shipped in
core but enabled via config.

---

## Skill discovery

Without a registry, how do operators find skills?

Options:
1. **Documentation page**: `docs/skills/community.md` — curated
   list of known community skills. Maintainer-curated, not
   automated.
2. **PyPI search**: `pip search ember-skill` (if PyPI search
   worked; it's currently broken).
3. **GitHub topic**: `topic:ember-skill` — searchable on GitHub.
4. **Documentation tags**: Skill authors tag their READMEs.

The first is the most pragmatic. Curated list. Maintainer-
reviewed before adding. Like the Awesome- list pattern for
Python frameworks.

---

## What skills should NOT do

🔴 **Reject patterns**:

### 1. Automatic updates

Skills should not auto-update. Each update is a security event;
operator must consent.

### 2. Telemetry / phone-home

Skills must not leak data. Audit at install time. Refuse skills
that contact non-operator endpoints without explicit declaration.

### 3. Privileged operations without approval

Skills run inside Ember's tool framework — subject to
per-call approval and sandboxing. No "trust me; let me have
full access" patterns.

### 4. Crypto-related operations

Skills handling crypto wallets / signing should be *especially*
gated. Default: refuse.

---

## Quality assurance for community skills

Without a registry's review process, how do we ensure quality?

**We don't, for community skills.** Operators install at their
own risk.

What we provide:
- A **skill audit tool** (`ember skill audit <package>`): reads
  the skill's code, reports tools registered, network calls
  made, dependencies, license. Operator decides if acceptable.
- A **skill template** showing best practices.
- Documentation: "before installing community skills, audit
  them with this tool."

This is *trust but verify*. The operator is responsible; we
provide the tools to verify.

---

## Compared to OpenClaw's ClawHub

| | OpenClaw ClawHub | Ember community skills |
|---|---|---|
| **Discovery** | central registry | docs page / pip search |
| **Distribution** | OpenClaw-mediated | PyPI / GitHub |
| **Quality control** | OpenClaw curators | operator audit |
| **Update model** | auto-update channels | manual pip upgrade |
| **Trust model** | centralized | decentralized |

OpenClaw's model is *easier for operators* but *requires
infrastructure*. Ember's model is *more work for operators* but
*requires no infrastructure*.

Aligned with our Vows. Less convenient. More sovereign.

---

## Configuration shape

```yaml
ember:
  skills:
    discovery:
      auto_load_entry_points: true       # discover installed skills
      workspace_skills_path: ~/.ember/workspace/skills/
    enabled:                              # operator-controlled
      - ember-skill-code-review
      - my-custom-skill
    disabled: []
    audit_log:
      record_skill_load: true
      record_skill_tool_use: true
```

---

## What this looks like for an operator

```bash
# Discover an interesting skill
$ ember skill discover travel
Available skills (community-listed):
  ember-skill-travel-planner (PyPI; v1.2)
    https://github.com/ophiel/ember-skill-travel-planner

$ ember skill audit ember-skill-travel-planner
Auditing ember-skill-travel-planner v1.2:
  Tools registered: search_flights, search_hotels, plan_itinerary
  Network calls: api.flights-data.com, api.hotels-data.com
  Required env: TRAVEL_API_KEY
  Dependencies: requests, pydantic
  License: MIT
  Last commit: 3 weeks ago
  Issues: ~5 open
[Proceed? y/n] y

$ pip install ember-skill-travel-planner
$ ember skill enable ember-skill-travel-planner
Travel planner skill enabled.
```

The operator stays in charge. Audit *before* install. Enable
*after* install. Disable anytime.

---

## Closing

Skill Registry and Bundles is **OpenClaw's leverage of community
contribution**. ClawHub amplifies one author's work to many
operators.

Ember should:
- 🔴 Reject the centralized-registry pattern.
- 🟢 Adapt: skills as pip packages + entry points.
- 🟢 Adopt: workspace-authored skills tier.
- 🔵 Borrow the bundled / community / workspace three-tier
  conceptually.
- 🟢 Build a skill-audit tool for operator self-verification.

The Klóinn lesson: **community skills are valuable**; the
*centralization* is not. Distribute via PyPI + docs; trust
operators to verify; preserve sovereignty.
