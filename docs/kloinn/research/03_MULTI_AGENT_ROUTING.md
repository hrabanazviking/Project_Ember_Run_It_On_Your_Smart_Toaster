# 03 — Multi-Agent Routing

OpenClaw's pattern of running multiple distinct agents in one
install, with channel/account/peer routing to specific agents.

---

## The pattern

In OpenClaw, **one install can host many agents**. Each agent has:

- Its own **workspace** (directory of files: prompts, skills, history).
- Its own **session** (independent conversation state).
- Its own **identity** (defined in workspace's `AGENTS.md` /
  `SOUL.md`).
- Optional its own **sandbox policy**.

Operators define routing rules:
- Channel X routes to agent A.
- Account Y on channel Z routes to agent B.
- Specific peer (group, contact, room) routes to agent C.
- Everything else routes to the `main` agent.

So one OpenClaw daemon serves N agents, accessible from M channels,
according to the operator's routing rules.

---

## The use cases

This shape exists because operators actually want it:

### Use case 1: personal vs work agent

- "Personal" agent: relaxed register; access to personal notes; no
  work tools.
- "Work" agent: professional register; access to work
  documentation; cron jobs in work tools.
- WhatsApp routes to personal. Slack routes to work. Terminal can
  switch.

### Use case 2: specialty agents

- A research-focused agent with browse + extract tools.
- A code-review agent with read/edit/git tools.
- A general-purpose agent.

Operator picks which to talk to depending on the task.

### Use case 3: persona agents

- An emotional-support persona with warm register.
- A blunt-debugging persona with terse register.
- Operator routes to whichever fits their current need.

Some operators use ChatGPT custom-instructions or Claude Projects
for this. OpenClaw makes it *first-class*.

---

## How routing works (operator-visible)

Configuration in `openclaw.json`:

```json
{
  "agents": {
    "main": { ... },
    "personal": { "workspace": "personal" },
    "work": { "workspace": "work" }
  },
  "routing": {
    "channels.whatsapp": "personal",
    "channels.slack": "work",
    "channels.terminal.peers.@boss": "work",
    "default": "main"
  }
}
```

Routes are *deterministic* — given an input event, the Gateway
picks the agent without ambiguity.

---

## Why this is hard to do well

Multi-agent shape introduces complexity:

### Problem 1: shared state vs isolated state

Should the agents share the Well? Different Wells?

OpenClaw's answer: **separate workspaces** — each agent has its
own files, skills, prompts. Shared knowledge is achieved by
operator explicitly linking files.

### Problem 2: cross-agent awareness

Should agent A know what agent B has been discussing?

OpenClaw's answer: **isolation by default**. Cross-agent context
requires explicit operator configuration.

This is a *privacy* feature: the work agent doesn't see personal
chats; the personal agent doesn't see work chats.

### Problem 3: tool permissions per agent

Different agents may want different tool access.

OpenClaw's answer: per-agent sandbox config. Work agent gets
office-suite tools; personal agent doesn't.

### Problem 4: routing ambiguity

What if an event matches multiple rules?

OpenClaw's answer: first-match-wins ordered rules. Operator
controls precedence.

---

## Ember's current model

Ember today: **one agent**. Single identity. Single Well. Single
chat session at a time.

This is *simpler*. It's also a real limitation. Operators wanting
"work mode" vs "personal mode" must keep two separate Ember
installs, two separate Wells, two separate identities.

---

## What Ember could do

🟢 **Adapt to Ember Vows.**

The multi-agent shape **fits Ember's philosophy** if done right:

- **Sovereign**: operator controls everything; nothing leaves
  device.
- **Operator-curated**: each agent is operator-defined; no
  centralized agent marketplace.
- **Small footprint**: agents share infrastructure (LLM, Brunnr,
  Verdandi); only workspaces diverge.
- **Privacy by isolation**: personal and work stay separate by
  default.

Specific proposal for Ember: introduce **"personas"** as
operator-defined alternate identities sharing the same Ember
infrastructure.

Each persona:
- Has its own `identity.json`.
- Has its own `ember.yaml` (or override fragments).
- Has its own Well *or* shares the main Well (operator choice).
- Has its own Episodes stream.
- Inherits the same Funi/Brunnr/Mímir/etc. backends.

Operator switches via `ember --persona work chat`.

---

## How this differs from sub-conversations

Sub-conversation: "let me start a new chat thread within the same
agent."

Persona: "let me talk to a *different* agent with their own
identity, prompts, and history."

The distinction matters. Operators sometimes want the first
(continuation of context); sometimes want the second (clean
separation).

Both should be possible. Ember currently only supports the first
(implicitly, via Episode boundaries).

---

## Routing rules — for later

In Phase 4+ (federation, possibly Phase 5 with multi-channel
bridging), Ember could adopt routing rules:

```yaml
ember:
  routing:
    munnr_cli: main_persona
    stofa: main_persona
    telegram_bridge: personal_persona
    slack_bridge: work_persona
    default: main_persona
```

For V1/V2/V3 we don't need this; one persona at a time is fine.
For V4+ when bridges land, routing becomes essential.

---

## What OpenClaw teaches about the routing

A few specific lessons:

### 1. Deterministic routing

Never let an event silently go to "some agent" — always to a
specific one. Predictability > "smart" routing.

### 2. First-match-wins ordering

The operator orders the rules. The Gateway respects the order.
No magic priority computation.

### 3. Explicit default

Always have a `default` rule. If no rule matches, the default
applies. Never silently drop events.

### 4. Routing is operator-readable

The operator can read `routing.yaml` (or whatever the format) and
understand exactly where their messages go. No black-box.

These four are good engineering. Ember should follow them when we
add multi-persona.

---

## What about personas + multi-character roleplay

Some operators want personas for *roleplay* — "let me talk to my
fantasy story character." That's a third use case beyond
personal/work and specialty.

OpenClaw doesn't optimize for this (their persona shape is more
"agent" than "character"). But the underlying mechanism could
support it.

Ember's `identity.json` already supports arbitrary
operator-defined identity; persona shape would extend that.

The user-side risk: roleplay personas can blur lines between AI
and human relationships in ways that are uncomfortable or
unhealthy. Ember should *support* this use case (operator choice)
but *not encourage* it as a primary surface.

---

## Risks of multi-agent shape

🟡 **Defer until needed.**

The risks:

- **Complexity**: multi-agent shape adds many edges
  (cross-agent state, routing, conflicts).
- **Operator confusion**: which agent did I talk to last?
- **Resource usage**: N agents = N times the prompt assembly,
  N times the workspace state.

OpenClaw deals with these because they have the operator base to
warrant it. Ember might *not* warrant it until V4+.

Don't introduce multi-persona until 80% of operators ask for it.
Until then: one agent, well-tuned, is better than three agents
half-tuned.

---

## What's borrowable now

Even without full multi-persona, two specific patterns can land
in V2-V3:

### 1. Workspace files (AGENTS.md, SOUL.md, TOOLS.md analogs)

We can introduce *prompt-injection files* in Ember's directory
structure that the agent reads on every turn. These give operators
finer-grained control over personality without configuration
changes.

Discussed in [`../patterns/12_PROMPT_INJECTION_FILES.md`](../patterns/12_PROMPT_INJECTION_FILES.md).

### 2. Per-channel sandbox policy (Phase 4+)

When bridges land, each bridge has its own sandbox stance. The
Telegram bridge might disallow `read_local_file` even if main
session allows it. Per-channel policy is a natural fit.

---

## Closing

Multi-Agent Routing is **OpenClaw's recognition that operators
have multiple contexts**, and one agent isn't enough. The shape
is sophisticated but the underlying idea is simple: *let the
operator define which agent handles what*.

Ember should adopt the *idea* now (workspace prompts; per-channel
policy as bridges land), and the *full shape* later (personas
with full isolation) when operator demand warrants.

This is one of OpenClaw's biggest lessons. Worth studying carefully.
