# 11 — Multi-Agent Workspaces

The pattern of N agents in one install, each with isolated state
in a workspace directory.

---

## The pattern

**One install hosts N agents**. Each agent lives in a workspace
directory containing its prompts, skills, history, sessions. The
runtime knows how to route between them.

OpenClaw shape:

```
~/.openclaw/
  workspace/                   ← default ("main") agent
    AGENTS.md
    SOUL.md
    TOOLS.md
    skills/
    sessions/
  workspaces/
    personal/
      AGENTS.md
      SOUL.md
      ...
    work/
      ...
```

Each subdirectory is one agent's *world*.

---

## What workspaces hold

For a single agent:

1. **Identity prompts** — `AGENTS.md`, `SOUL.md` define
   personality, mission, register.
2. **Tool documentation** — `TOOLS.md` injected so agent knows what
   it can do.
3. **Skills** — operator-curated capability bundles.
4. **Sessions** — past + active conversation state.
5. **Optional**: workspace-specific config overrides.

Edit any of these as a *file*. No CLI command required for most
edits. Operator-friendly.

---

## How routing happens

Per [`03_MULTI_AGENT_ROUTING.md`](../research/03_MULTI_AGENT_ROUTING.md):

```json
{
  "routing": {
    "channels.whatsapp": "personal",
    "channels.slack": "work",
    "default": "main"
  }
}
```

Gateway maps incoming events to agents. Each event lands in *one*
agent's session.

---

## Why this is good

### 1. Isolation

The work agent doesn't see personal chats. The personal agent
doesn't see work data. Hard isolation by file-system boundaries.

This is *security by default*. Operators don't worry about
accidental cross-context leakage.

### 2. Operator-editable

Identity lives in markdown files. Operators edit with their
preferred editor. No proprietary UI required to change agent
personality.

### 3. Backup-friendly

Whole workspace = one directory. Operator backs it up; restores
elsewhere; agent moves with them.

### 4. Mod-friendly

Operators share workspace templates ("here's a great research
agent workspace"). New operators clone and customize.

### 5. Tool isolation

Each agent can have different tool access. Work agent has
calendar tools; personal agent doesn't. Sandboxed by config.

---

## What's hard about the pattern

### Shared resources

Multiple agents need to share *some* things:
- The LLM (only one Ollama backend).
- Optionally the Well (operator-choice).
- The audit log (could be per-agent; could be shared).

Coordination: which agent currently "owns" the LLM? OpenClaw
likely queues requests; agents await turn.

For Ember at single-operator scale: one agent at a time talks to
the LLM. Queue-based mediation is fine.

### Cross-agent awareness

What if agent A discovers something agent B should know? Hard.

OpenClaw answer: explicit cross-agent links (operator-curated).
No auto-sharing.

Ember answer (when we get here): same. The operator decides what
to share.

### Discovery

How does an operator know which agents exist?

OpenClaw: `/sessions list`, workspace directory inspection.

Ember equivalent: `ember persona list`, `ember persona show <name>`.

---

## Why Ember should DELAY this

🟡 **Defer to V4+.**

The pattern is good. The need is not yet urgent.

Reasons to delay:

1. **Ember has < 100 operators**; the use cases that warrant
   multi-agent shape (work vs personal contexts) come from
   power-users, who Ember has few of.

2. **Implementation complexity**: routing, sandboxing,
   cross-workspace coordination. All real engineering.

3. **The Vow of Smallness applies**: doing one thing well > doing
   multi-thing OK.

4. **Phase 4 federation is more valuable first**: it solves a
   different problem (multi-device) that more operators want.

5. **We learn from OpenClaw's experience**: their multi-agent
   shape is *complex*. They have 7k+ open issues. Some fraction
   relate to multi-agent edge cases. We can study their
   experience before adopting.

---

## Smaller borrowable patterns now

🔵 **Borrow as-is**:

### The "workspace directory" idea (for one agent)

Even with one agent, the *workspace directory* is a useful
abstraction. Ember has bits of this in `~/.ember/`:

```
~/.ember/
  state/                  ← runtime state
  config/                 ← operator config (ember.yaml)
  identity.json
```

We could *consolidate this into a single workspace*:

```
~/.ember/
  workspace/
    identity.json
    AGENTS.md             ← optional; operator-authored prompt
    SOUL.md               ← optional; deeper personality
    TOOLS.md              ← optional; tool documentation
    skills/               ← Phase 3+: operator-curated bundles
    sessions/             ← Episodes
    state/                ← runtime state
    config/
      ember.yaml
```

One folder = one Ember instance. Backup that folder = back up
Ember.

🟢 **Adapt to Ember Vows**:

### Workspace prompt files

Even with one agent, having operator-editable prompt fragments
in markdown is *useful*. Operators can shape personality without
editing code.

Per [`12_PROMPT_INJECTION_FILES.md`](12_PROMPT_INJECTION_FILES.md).

### Multiple "modes" within one identity

Instead of multi-agent, Ember can offer **modes**:

- `ember chat --mode=work`  
  Uses a different `MODES.md/work.md` prompt fragment.

- `ember chat --mode=personal`  
  Uses `MODES.md/personal.md`.

Same identity; different mood + tool access for the moment.

This is *much simpler* than full multi-agent and captures 80% of
operator value.

---

## What multi-agent doesn't do (worth noting)

The pattern doesn't:

- Give operators *more* LLM time (same single LLM is shared).
- Solve privacy concerns *better than file-system isolation*
  already does.
- Enable cross-agent collaboration (that's a separate problem).

It just lets operators *cleanly separate contexts*. Useful, but
modes get most of the way there with less complexity.

---

## Closing

Multi-Agent Workspaces is **OpenClaw's response to operators
having multiple contexts**. It works. It's heavy.

Ember should:
- 🔵 Borrow the workspace-directory abstraction (for one agent).
- 🟢 Adapt the prompt-injection pattern (for personality flexibility).
- 🟢 Adopt "modes" for context-switching within one agent.
- 🟡 Defer full multi-agent shape to V4+ when demand justifies.

We learn from OpenClaw's design, but we don't have to *implement*
their full sophistication on day one. Smallness > completeness.
