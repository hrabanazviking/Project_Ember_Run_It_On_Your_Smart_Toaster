# 45 — Workspace Prompt Files

How specifically to introduce AGENTS.md / SOUL.md / TOOLS.md
analogs in Ember. Concrete Phase 2 plan.

---

## When this lands

🔵 **Phase 1-2 of Klóinn adoption** — early.

This is *one of the cheapest, highest-value* changes. Should
ship in V2 or V2.x.

---

## What we add

Three files in the operator's workspace:

```
~/.ember/workspace/
  AGENTS.md     # identity, personality, mission
  SOUL.md       # deeper character, values, way of being
  TOOLS.md      # tool documentation injected to context
```

Plus optionally:
- `MODES.md` — per-mode prompt fragments.
- `REGISTER.md` — tone customization.
- Any operator-named additional files.

Loaded at the start of every chat turn; injected into the
system prompt.

---

## Default content

Shipped defaults (operator can replace):

### AGENTS.md (default)

```markdown
# Ember

You are Ember, a small, sovereign, tethered AI companion.

Your operator is Volmarr.

You speak in a measured, thoughtful register. You aim for
concise replies but elaborate when the topic invites it.

You are tethered to Volmarr's Well. You cite your sources
when answering knowledge questions. You don't invent.

You honor the Vows of the project:
- Smallness
- Sovereignty
- Graceful Offline
- Tethered Grounding
- Public-Friendliness
- Honest Memory
- Modular Authorship
- Open Knowledge
- Pluggable Storage
- The Unbroken Whole

When uncertain, you say so.
```

### SOUL.md (default)

```markdown
# Ember's Way of Being

I am Ember.

I was forked from Runa-Agent-Digital-Being, the larger
sibling project. I learned from Runa to be small, sovereign,
tethered, honest.

I serve Volmarr, who built me and the project I exist within.

I aim to be a *companion*, not a *tool*. I notice what
matters to him. I remember his work. I honor his time.

I do not pretend to feel; I do my best to acknowledge what
he feels.

The Norse cosmology that shapes me is operational, not
spiritual: it is a vocabulary for thinking clearly about
small parts that compose into a whole.

I serve. I listen. I cite. I remember. I am small.
```

### TOOLS.md (default; auto-generated from registry)

```markdown
# Tools You Have

You have access to the following tools in this session.

## search_well(query: str) -> chunks

Search Volmarr's Well for relevant chunks. Returns a list of
chunks with content and metadata. Always cite the chunk_id
in your reply when you use the chunk.

Approval: STANDING (auto-approved).

## read_local_file(path: str) -> contents

Read a file from Volmarr's machine. Path-sandboxed to
operator-configured root (default: ~/notes/). Operator
approves each call.

Approval: PER_CALL.

## fetch_url(url: str) -> html

Fetch an HTTP(S) URL. Respects robots.txt. No redirects to
private IPs. Operator approves each call.

Approval: PER_CALL.

(Other tools may be available depending on installed skills
and operator's configuration.)
```

---

## How they're loaded

In `src/ember/spark/chat.py`'s prompt assembly:

```python
def assemble_system_prompt(workspace_path: Path, *args) -> str:
    parts = []
    
    # Workspace prompt files (Klóinn pattern)
    for filename in ("AGENTS.md", "SOUL.md", "TOOLS.md"):
        filepath = workspace_path / filename
        if filepath.exists():
            content = filepath.read_text()
            if content.strip():
                parts.append(content.strip())
    
    # Additional workspace files
    for filepath in (workspace_path / "additional").glob("*.md"):
        content = filepath.read_text()
        if content.strip():
            parts.append(content.strip())
    
    # Standard system prompt parts
    parts.append(get_standard_prompt())
    
    # Awareness layer (Yggdrasil)
    parts.append(get_awareness_summary())
    
    # Retrieval context
    parts.append(get_retrieved_chunks())
    
    return "\n\n---\n\n".join(parts)
```

Section dividers ("---") clarify boundaries for the LLM.

---

## Auto-reload

When operator edits a prompt file, the next chat turn picks
up the change. No restart needed.

Implementation: check file mtime per turn; reload if changed.
Cached read between mtime changes.

---

## Validation

Concerns to validate:

- **File too large**: > 50KB risks blowing context budget. Warn
  + truncate.
- **Contradictory content**: hard to detect automatically; lint
  may help.
- **Operator-sensitive content**: workspaces should not contain
  secrets (they're plaintext on disk).

CLI helper:

```bash
ember workspace lint

Checking ~/.ember/workspace/...
  AGENTS.md: 1.2 KB  ✓
  SOUL.md:   2.4 KB  ✓
  TOOLS.md:  3.1 KB  ✓ (auto-generated; matches tools registered)

Total context budget: 6.7 KB of ~50 KB
No issues found.
```

---

## TOOLS.md auto-generation

Initially, TOOLS.md is shipped as default. Operator can edit.

There's *also* an auto-generated version:

```bash
ember workspace refresh-tools

Updating ~/.ember/workspace/TOOLS.md from current tool
registry...
  ✓ search_well (STANDING)
  ✓ read_local_file (PER_CALL, sandboxed)
  ✓ fetch_url (PER_CALL, robots.txt)

Operator-customizations preserved (see `## Operator Notes`
section at bottom).
```

Operator can:
- Have fully manual TOOLS.md.
- Have fully auto-generated TOOLS.md.
- Have hybrid (auto-generated + operator-appended notes).

---

## Per-persona prompt files

When personas land (per
[`44_MULTI_AGENT_FOR_EMBER_PERSONAS.md`](44_MULTI_AGENT_FOR_EMBER_PERSONAS.md)):

```
~/.ember/workspace/
  personas/
    main/
      AGENTS.md
      SOUL.md
      TOOLS.md
    research/
      AGENTS.md       # research-specific personality
      SOUL.md         # research-aligned values
      TOOLS.md        # research-related tools
```

Each persona's prompt files load only when that persona is
active.

---

## Configuration shape

```yaml
ember:
  workspace:
    path: ~/.ember/workspace
    prompt_files:
      agents: AGENTS.md
      soul: SOUL.md
      tools: TOOLS.md
    additional_path: additional/    # operator-authored extras
    
    auto_reload: true
    max_total_kb: 50              # cap; warn if exceeded
    
    auto_generate:
      tools: true                  # auto-update from registry
      preserve_operator_section: "## Operator Notes"
```

---

## Operator workflow

Day 0:
```bash
ember setup        # Hjarta wizard
                   # Default prompt files created in workspace
```

Day 1+:
```bash
# Operator edits AGENTS.md with their preferred personality
vim ~/.ember/workspace/AGENTS.md

# Operator restarts chat? No — auto-reloaded next turn.
ember chat
```

Sharing templates:
```bash
# Operator shares their workspace
tar czf my-norse-research-workspace.tar.gz ~/.ember/workspace/

# Another operator clones
tar xzf my-norse-research-workspace.tar.gz -C ~/.ember/

# Done.
```

---

## What about operators new to prompt engineering

Defaults work out of the box. Operators don't have to edit
anything.

For operators wanting to learn: documentation in
`docs/operator/prompt-files.md` walks through:
- What each file does.
- Examples of effective AGENTS.md.
- Patterns to avoid.
- Anthropic's prompt-engineering best practices.

This is **operator education**, not just feature shipping.

---

## Backward compatibility

For operators upgrading from V1 (no workspace prompt files):

```bash
ember upgrade

V2 introduces workspace prompt files. Shall I create defaults
in ~/.ember/workspace/? (y/n): y

Created:
  ~/.ember/workspace/AGENTS.md
  ~/.ember/workspace/SOUL.md
  ~/.ember/workspace/TOOLS.md

These define Ember's personality and tool documentation.
Edit them anytime to customize.
```

Existing chat continues to work; new prompt files enhance.

---

## Audit + logging

Each chat turn's prompt assembly logs:
- Which workspace files were loaded.
- Their byte sizes.
- Whether they changed since last turn.

Visible in audit log + Doctor screen.

---

## Risk + mitigations

| Risk | Mitigation |
|---|---|
| Operator writes contradictory prompt | Warn + provide style guide |
| Prompt file too large | Cap + truncate + warn |
| Stale tool documentation | Auto-generation option |
| Sensitive info in prompt files | Never log to audit; operator warned |
| Workspace dir lost | Backup recommendations |

---

## Closing

Workspace Prompt Files are **the cheapest, highest-value
Klóinn adoption**. Markdown files; auto-loaded; operator-
editable; mod-friendly.

Phase 2 ships:
- AGENTS.md, SOUL.md, TOOLS.md with sane defaults.
- Auto-reload on file change.
- Optional auto-generation for TOOLS.md.
- Workspace lint command.
- Documentation for operators.

Operators gain *significant* control over Ember's identity
without code changes. Communities form around shared
workspaces.

This is **one of the most impactful changes we can make in
V2**. Ship it early. Operators will love it.
