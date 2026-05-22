# 44 — Multi-Agent for Ember Personas

How and when to add operator-selectable personas to Ember.
Concrete Phase 4+ plan.

---

## Personas, not full multi-agent

Per [`../patterns/11_MULTI_AGENT_WORKSPACES.md`](../patterns/11_MULTI_AGENT_WORKSPACES.md):
full multi-agent shape (separate workspaces per agent, complex
routing) is heavy.

**Personas** are the lighter version: one Ember installation;
multiple operator-defined identity profiles; switchable per
session.

This captures 80% of the multi-agent value with 20% of the
complexity.

---

## What a persona is

A persona is:
- **A name** (e.g., "main", "work", "personal", "research").
- **A workspace prompt file set** (AGENTS.md, SOUL.md,
  TOOLS.md specific to this persona).
- **Optional sandbox/tool overrides** (work persona allows
  certain tools; personal doesn't).
- **Its own session history** (separated for privacy).

Personas share:
- The same Funi (LLM backend).
- The same Brunnr (Well backend, unless operator separates).
- The same Verdandi event bus.
- The same Hjarta + Munnr + Stofa surfaces.

---

## Storage shape

```
~/.ember/workspace/
  personas/
    main/
      AGENTS.md
      SOUL.md
      TOOLS.md
      sessions/
        2026-05-22T14:00_uuid/
          ...
    
    work/
      AGENTS.md          # different personality
      SOUL.md            # different identity
      TOOLS.md           # different tools doc
      sessions/
        ...
    
    personal/
      AGENTS.md
      SOUL.md
      TOOLS.md
      sessions/
        ...
```

Personas = directories. Each has its own *full set* of prompt
files. Operator copy + modify.

---

## Switching between personas

CLI:
```bash
ember chat                        # default persona ("main")
ember chat --persona work
ember chat --persona personal
ember persona list
ember persona create research
ember persona delete old_one      # asks for confirmation
```

Stofa:
- Status bar shows current persona.
- `Ctrl+P` opens persona picker.
- Each persona's sessions visible in Episode Browser.

---

## What stays the same across personas

The *physical* Ember:
- Funi backend (same LLM).
- Tools available (in core).
- Brunnr backend (Well storage; configurable per persona).
- Audit log destination (shared or per-persona; configurable).
- Vows (the system itself).

The *operator-facing* Ember:
- Identity (different AGENTS.md per persona).
- Register / tone (different SOUL.md).
- Tool description framing (different TOOLS.md).
- Memory access (per-persona Well, optionally).

---

## When to add personas

🟡 **Phase 4+** — when:

1. Operators ask for it (and they will, eventually).
2. Workspace prompt files are stable (Phase 2-3 work).
3. Sessions are first-class (Phase 2 work).
4. We have time to support it.

Phase 4 ships federation + bridges; personas can join then or
in late-Phase-4 / Phase-5.

---

## Migration path from single-persona

Existing operators have `~/.ember/identity.json` +
`~/.ember/state/`. Personas need to coexist with this.

Approach:

1. **Backward-compat default**: if no `personas/` directory, use
   legacy single-identity files. Existing operators unchanged.

2. **Opt-in migration**: `ember persona migrate-to-multi` creates
   `personas/main/` from existing identity. Operator now has
   one persona; can add more.

3. **Workspace-driven**: new installs start with `personas/main/`
   directly.

Existing operators don't have to migrate. Personas are *opt-in
power feature*.

---

## What personas look like for operators

### Example: research operator

Operator does Norse cosmology research + occasional general
Q&A. Wants:

- **research** persona: deep Norse register; pinned access to
  research Well; teacherly mood default.
- **main** persona: general use; standard register.

```bash
ember persona create research
ember persona configure research \
  --tool-allow read_local_file \
  --tool-allow search_well \
  --tool-deny fetch_url \
  --well-path ~/.ember/wells/norse-research/

# Edit ~/.ember/workspace/personas/research/AGENTS.md
# to define research-specific personality

ember chat --persona research  # now talking with research-Ember
```

### Example: work vs personal

Operator wants:

- **work** persona: brisk; office-tool access; work
  documents.
- **personal** persona: warm; personal-notes access;
  hobby-related tools.

Each persona configured with different sandbox + tool +
prompt settings.

---

## Cross-persona memory question

Can persona A see persona B's notes?

Default: **no**. Each persona's Well is its own.

Operator can:
- Configure shared Well: `well_path` same in both personas.
- Configure separate Wells: different paths.

Common pattern:
- Shared *Funi* (LLM is the same).
- Shared *Brunnr* (one Well; both personas access).
- Separate *Sessions* (chats stay per-persona).

This is *operator-curated isolation*.

---

## Federation + personas

Per Yggdrasil + Klóinn integration:

Operator on laptop, persona "work":
- Routed via tailnet federation to homelab's LLM.
- Uses shared Well (also on homelab).
- Sessions persist in laptop's persona/work/sessions/.

Operator switches to persona "personal":
- Same federation routing.
- Different Well section.
- Different sessions storage.

The federation layer is *persona-aware*.

---

## Per-persona sandbox

Operators can configure stricter sandbox per persona:

```yaml
ember:
  personas:
    research:
      tools:
        sandbox_default: subprocess
    
    work:
      tools:
        sandbox_default: docker      # work might involve sensitive data
        approval:
          all: per_call               # strict
```

This is *per-persona safety tuning*.

---

## Configuration shape

```yaml
ember:
  personas:
    enabled: false                 # opt-in
    default: main
    
    main:
      workspace_path: ~/.ember/workspace/personas/main
      well_path: ~/.ember/wells/main
      sessions_path: ~/.ember/state/sessions/main
    
    research:
      workspace_path: ~/.ember/workspace/personas/research
      well_path: ~/.ember/wells/norse-research
      sessions_path: ~/.ember/state/sessions/research
      tools:
        approval_overrides:
          fetch_url: forbidden
    
    work:
      workspace_path: ~/.ember/workspace/personas/work
      well_path: ~/.ember/wells/work
      sessions_path: ~/.ember/state/sessions/work
      tools:
        sandbox_default: docker
```

---

## Channel-to-persona routing (Phase 4+)

When bridges land + personas land:

```yaml
ember:
  bridges:
    matrix:
      enabled: true
      rooms:
        "!work-room:matrix.org":
          persona: work
        "!personal-room:matrix.org":
          persona: personal
    
    telegram:
      enabled: true
      persona: personal  # all Telegram routed to personal
```

Each channel routes to a configured persona. The operator
specifies.

---

## What personas don't replace

- Sessions (sessions are *within* a persona).
- Workspaces (workspace files *implement* the persona).
- Identity (identity is a *property* of the persona).

Personas are a *layer of organization*; they compose with
existing concepts.

---

## Per-persona Mímir state

Mímir's decay + reinforcement per persona:
- Persona "research" reinforces Norse-related chunks.
- Persona "work" reinforces office-related chunks.
- Each persona's Mímir state evolves separately (when separate
  Wells configured).

Or: shared Well + shared Mímir = unified memory across
personas. Operator's choice.

---

## What about identity files

Each persona has its own:
- AGENTS.md
- SOUL.md
- TOOLS.md
- (optional) MODES.md, REGISTER.md, etc.

Operators write these to define the persona's character.

Templates can be shipped (community contributions or core
defaults) that operators clone:
```bash
ember persona create research --from-template norse-scholar
```

Templates: a curated set of prompt-file sets for common
personas.

---

## Risk: persona confusion

Operator forgets which persona they're in. Sends sensitive
message to wrong persona.

Mitigations:
- **Persistent display**: Stofa always shows current persona
  in status bar.
- **Confirmation**: explicit confirmation on persona switch.
- **Per-persona color/prompt**: Munnr CLI uses different
  prompt color per persona.
- **Persona-tagged sessions**: sessions tagged with persona
  name in operator-visible record.

---

## Documentation for operators

When personas land:

> *Personas let you have multiple distinct "Embers" sharing
> one installation. Each persona has its own personality
> (defined in markdown files), its own memory (optionally
> separate Well), and its own session history.*
>
> *Operators commonly use personas for:*
> *- Work vs personal contexts.*
> *- Research areas (Norse, philosophy, code review, etc.).*
> *- Different operators sharing the install (per-person
>   persona).*
>
> *Personas are opt-in. Default: single persona ("main").*
> *Migrate via `ember persona migrate-to-multi`.*

---

## Closing

Multi-Agent for Ember Personas is **Phase 4+ work** that
brings OpenClaw's multi-agent shape to Ember in a *Vow-
aligned, lighter, opt-in* form.

Personas = workspace directories + identity files + optional
isolated Well/sessions + per-persona tool/sandbox config.

Key constraints:
- Opt-in (existing operators unaffected).
- Operator-curated (no centralized persona templates beyond
  community-shared).
- Sovereignty-aligned (no cross-cloud personas).
- Defaults clear (one persona = current behavior).

This is the *Klóinn pattern adapted*. We get the operator-
context-switching benefit without the heavier multi-agent
infrastructure.
