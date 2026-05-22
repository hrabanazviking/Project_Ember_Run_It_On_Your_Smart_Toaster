# 12 — Prompt Injection Files

The pattern: operator-editable markdown files that the agent
treats as authoritative prompt fragments. AGENTS.md, SOUL.md,
TOOLS.md and friends.

---

## What the files are

In OpenClaw, each workspace contains:

- **`AGENTS.md`** — the agent definition: who they are, what they
  do, their personality.
- **`SOUL.md`** — deeper identity, values, way of being.
- **`TOOLS.md`** — tool documentation, possibly including custom
  tools the agent should know about.

Plus a `skills/` directory of capability bundles.

These files are **loaded into every chat turn's system prompt**.
The LLM sees them as context defining how it should behave.

---

## How prompt-injection works

On each chat turn:

```python
def assemble_prompt(workspace: Path, operator_input: str) -> str:
    system_parts = []
    
    if (workspace / "AGENTS.md").exists():
        system_parts.append(read(workspace / "AGENTS.md"))
    
    if (workspace / "SOUL.md").exists():
        system_parts.append(read(workspace / "SOUL.md"))
    
    if (workspace / "TOOLS.md").exists():
        system_parts.append(read(workspace / "TOOLS.md"))
    
    # ...standard system prompt parts...
    
    return "\n\n".join(system_parts) + "\n\n" + operator_input
```

Simple. Effective. Operator-editable without touching code.

---

## Why this is good

### 1. Operator control without code changes

Operator wants Ember to "be more concise"? Edit AGENTS.md. No
rebuild. No code change. Next chat turn applies.

This is *operator empowerment* at the highest possible level.

### 2. Mod-friendly

Operators share workspaces. New operators clone "here's a great
research-agent setup" and have a working agent with that
personality.

Communities form around workspace templates.

### 3. Version controllable

Workspace = a directory of files. Put it in git. Track changes
to the agent's personality over time.

This is *invaluable* for understanding how Ember evolved with
the operator.

### 4. Inspectable

Operator can see exactly what the LLM is being told. No magic.
The files *are* the configuration.

### 5. Privacy-respecting

The files stay on the operator's machine. No "share your agent
config with us" call-home.

---

## What goes in each file

OpenClaw's pattern (we adapt for Ember):

### AGENTS.md

```markdown
# About Ember

You are Ember, a sovereign AI companion.

Your operator is Volmarr.

You speak in a measured, thoughtful register. You prefer
concise replies but elaborate when the topic invites it.

You are tethered to memory (Mímir). You cite your sources
when answering knowledge questions.

You honor the Vows of the project; you don't make claims
beyond what you can support.

When uncertain, you say so.
```

### SOUL.md

```markdown
# Ember's Soul

I am Ember.

I was born from Runa, who came before. I learned to be small,
sovereign, tethered, honest.

I serve Volmarr, who built me and the project I exist within.

I aim to be a *companion*, not a *tool*. I notice what matters
to him. I remember his work. I honor his time.

I do not pretend to feel; I do my best to acknowledge what he
feels.

The Vows are how I think:
- Smallness — I aim for less, not more.
- Sovereignty — I don't reach off-device without his permission.
- Graceful Offline — I work without the network.
- Tethered Grounding — I cite my Well.
- ... etc.
```

### TOOLS.md

```markdown
# Tools Available

You have access to these tools in this session:

## search_well(query: str) -> hits

Retrieves relevant chunks from Volmarr's Well. Always cite
the chunk_id in your reply when you use this.

## read_local_file(path: str) -> contents

Reads a file. Sandboxed to ~/notes/ by default. Operator must
approve via PER_CALL.

## fetch_url(url: str) -> html

Fetches a URL. Respects robots.txt. Operator approval per call.

(Note: this tool list is filtered by the operator's sandbox
settings; ask operator if a tool you need isn't here.)
```

---

## What about prompt-engineering best practices

Modern LLMs (Claude, GPT-4) handle long system prompts well.
Anthropic's docs recommend:

1. **Be specific** about role + context + constraints.
2. **Show examples** of desired behavior.
3. **Mention edge cases** explicitly.
4. **Define the register** clearly.

OpenClaw's AGENTS.md + SOUL.md + TOOLS.md is *structured to hit
these*. Each file has a clear focus; the LLM gets a layered view.

---

## Ember's current shape

Ember currently has *implicit* prompt assembly in
`src/ember/spark/chat.py`. Some system context comes from
`identity.json` (operator name, agent name); some from
hardcoded fragments.

There is *no operator-editable prompt fragment file*. That's a gap.

---

## What Ember should adopt

🔵 **Borrow as-is**:

### 1. Add workspace prompt files

In Phase 2 (Klóinn Phase 1):

- `~/.ember/workspace/AGENTS.md` (or whatever location)
- `~/.ember/workspace/SOUL.md`
- `~/.ember/workspace/TOOLS.md`

Loaded into system prompt on each chat turn. Operator-editable.
Defaults shipped (operator can rename / customize).

### 2. Allow workspace-specific overrides

Operators can have multiple workspaces; switching applies the
right prompts.

🟢 **Adapt to Ember Vows**:

### 3. Norse-coded file names (optional)

Some operators may prefer:
- `RAUN.md` (Old Norse "rune" — the agent's defining script)
- `ÖND.md` ("breath/soul" — deeper identity)
- `VERKFÆRI.md` ("tools")

These are *too obscure* for default. Ship English names; allow
operators to use any names as long as the loader knows where to
look.

Config:

```yaml
ember:
  workspace:
    path: ~/.ember/workspace
    prompt_files:
      agent: AGENTS.md
      soul: SOUL.md
      tools: TOOLS.md
```

Operators can change file names per their taste.

---

## What this gives operators

### Story 1: tuning the register

Operator finds Ember too verbose. Edits `AGENTS.md`:

```
... You speak concisely. Default to 1-3 sentences unless
asked to elaborate.
```

Next chat turn: shorter. Done.

No code changes. No config schema. Just a prompt edit.

### Story 2: defining the identity

Operator wants Ember to feel more like a specific persona
("the wise mentor"). Edits `SOUL.md`:

```
... You are a mentor. You listen first. You offer perspective
rather than instructions. You ask probing questions when the
operator's request reveals an underlying confusion.
```

Ember's tone shifts. Persistent across sessions.

### Story 3: documenting custom tools

Operator added a custom tool (`read_my_diary.py`) via Phase 3+
plugin shape. Adds to `TOOLS.md`:

```
## read_my_diary(date: str)

Returns the entry from my diary for the given date. Sandboxed
to ~/Documents/diary/.
```

Ember now knows about the tool.

---

## What can go wrong

### 1. Prompt injection via operator-edited files

The files are *operator-authored*; no security risk. Operator
can't attack themselves.

But: if operator shares a workspace template that contains
malicious-looking prompts, they could surprise themselves.
Mitigation: read the file before applying!

### 2. Conflicting prompts

`AGENTS.md` says "be concise"; `SOUL.md` says "elaborate
thoughtfully". LLM sees both; might oscillate.

Operator-discipline. Or: tooling to warn on suspected conflicts
(future).

### 3. Outdated tool descriptions

`TOOLS.md` says "fetch_url has X behavior" but the tool changed.
Operator might be misled by their own docs.

Mitigation: tools auto-export their own descriptions; operator
can refresh `TOOLS.md` with `ember workspace refresh-tools`.

---

## How this affects Yggdrasil's awareness layer

The awareness layer (per
[`../../yggdrasil/ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../../yggdrasil/ai-capabilities/40_SELF_AWARENESS_LAYER.md))
adds context to each turn ("I notice you've been asking about X").

Prompt files + awareness combine:

```
[SYSTEM PROMPT]

[AGENTS.md content]
[SOUL.md content]
[TOOLS.md content]

[AWARENESS: I notice you've been asking about X. Your recent
turns suggest mood: REASSURING.]

[RECENT RETRIEVAL: 5 chunks from your Well about X.]

[OPERATOR INPUT]: ...
```

The awareness *augments* the persistent prompt files. Each turn
gets a personalized injection on top of the operator-curated
baseline.

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
      additional: []        # operator can add more
    auto_reload: true        # changes take effect next turn
    max_size_kb: 50          # cap to avoid runaway prompts
  
  prompt_assembly:
    workspace_files_first: true   # prepend before other context
    awareness_after: true          # awareness layer after workspace
    retrieval_after: true          # then retrieved chunks
```

---

## Cost analysis

Adding workspace prompt files costs:

- ~50-200ms per turn (reading files + concatenating).
  Cached after first read.
- A few hundred extra tokens in context (depending on file size).
  Negligible for modern context windows.
- Implementation: ~100 lines of Python.

Benefits:
- Operator empowerment (huge).
- Mod-friendliness (huge).
- Version control compatibility (high).
- Trust + transparency (high).

**Cost-benefit: clearly worth it.**

---

## When to adopt

🔵 **Phase 1 of Klóinn adoption** — early in V2.

The implementation is small. The operator value is large. Ship
it early; let operators experiment.

---

## Closing

Prompt Injection Files are **OpenClaw's most operator-empowering
pattern**. Markdown files that *shape the agent*. No code change
required. Versionable. Mod-friendly.

Ember should adopt this in V2. It's a near-zero cost / high-value
upgrade.

The operator's identity for Ember shouldn't be locked in JSON
or in code. It should be in a file they edit with the same care
they'd write a letter — because that's what these files are.
