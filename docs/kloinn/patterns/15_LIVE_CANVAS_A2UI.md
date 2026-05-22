# 15 — Live Canvas and A2UI

OpenClaw's "agent-driven visual workspace" — where the agent
*renders* interactive UI elements the operator can manipulate.

---

## What Live Canvas is

OpenClaw's **Live Canvas** is described as "an agent-driven
visual workspace." The agent can produce UI elements (forms,
buttons, lists, visualizations) that the operator interacts with
directly.

Their **A2UI** ("agent-to-UI") system is a proprietary
description language: the agent emits A2UI markup; the Canvas
renderer turns it into a real UI.

Example flow (extrapolated):

1. Operator: "Help me plan a trip to Norway."
2. Agent: Returns text + A2UI markup describing a form with
   destination, dates, budget fields + a "submit" button.
3. Operator: Fills the form on the Canvas.
4. Agent receives the form data; refines the plan.

This is **conversation-augmented-with-UI** — text remains the
primary medium, but the agent can summon UI for specific
interactions where forms are clearer than freeform text.

---

## Why this is interesting

Most AI assistants are *text-only*: operator types; agent
replies in text. Even multimodal ones (voice, image) keep
the *interaction shape* linear.

Live Canvas changes the interaction shape: agent can decide
"this answer is better as a form than a paragraph." The UI
becomes part of the response.

This is *new design space*. Few projects have explored it deeply.

---

## When it's useful

### Forms

Operator's request implies a multi-field input. Examples:
- Trip planning.
- Project requirements.
- Configuration wizards.
- Budget allocations.

A form is *clearer* than typing free-text answers to questions.

### Data presentation

Showing tabular data, charts, lists. The agent picks a
visualization that fits.

### Confirmation flows

"Confirm this purchase / this deletion / this approval" — UI
button is clearer than "type yes/no."

### Iterative refinement

Show current state; operator tweaks via UI elements; agent
re-renders.

---

## When it's NOT useful

- Casual conversation (text suffices).
- Quick questions (UI overhead > value).
- Operations the operator wants to do in their preferred editor
  (don't reinvent the UI in the agent).

The agent must judge when UI helps vs hinders. Bad agents over-
UI; good ones under-UI.

---

## What Ember can adopt

🟡 **Defer to V5+ (post-Auga).**

Ember currently has:
- Munnr (CLI text-only).
- Stofa (TUI text-only, planned).
- Auga (GUI, planned for V5).

A Canvas-like surface fits into Auga. Until Auga exists, this
isn't actionable.

For V5, Auga could include:
- **Forms** — agent returns markdown + Auga form-spec; rendered
  inline in chat.
- **Charts** — agent's "show me X over time" → chart embed.
- **Code editors** — agent suggests code; operator edits inline.
- **File pickers** — agent asks for file; UI native picker
  appears.

---

## A2UI as a markup spec

OpenClaw's A2UI is proprietary; format not detailed in their
README. Probably JSON or a custom DSL.

For Ember, we'd want:
- **Open spec**: documented format anyone can implement.
- **Composable**: forms within forms; tables of buttons.
- **Backward-compatible across versions**.
- **Minimal**: just enough to express common UIs; complex needs
  → operator-installed plugins.

Possible existing standards to borrow:
- **Markdown extensions** (we're already markdown-rendering).
- **JSON-Schema** (for forms; well-established).
- **HTMX-like** (for incremental updates).

Or invent our own: **OdinUI**, a Norse-coded UI spec.

---

## TUI-flavored Canvas (sooner)

Even before Auga, Stofa (TUI) could have a Canvas-equivalent:

- Agent returns markdown + Textual widget spec.
- Stofa renders inline widgets — sliders, lists, etc.
- Operator interacts via keyboard.

Stofa-flavored Canvas would be *more limited* than a GUI one
(no rich charts, no images) but *useful* for forms + selectors.

🟢 **Adapt to Ember Vows**: ship a minimal TUI-canvas in V3.

---

## Trade-offs

### Pro: richer interactions

UI elements collapse "ask + reply" loops into "render + edit"
loops. Faster, clearer.

### Pro: discoverability

Operator sees options visually. "Oh, there's a checkbox for
X" — they didn't have to know to ask.

### Con: complexity

Agent must know when UI helps. Renderer must support the spec.
Operator must learn the UI conventions.

### Con: terminal-unfriendly

GUI Canvas is workstation-native. Operators on SSH-only
terminals (Pi Zero, remote shells) can't render rich UI.

Mitigation: TUI fallback — agent emits markdown if Canvas isn't
available.

---

## What about voice + canvas?

If voice is the input, what does Canvas do? Operator can't
*see* it.

OpenClaw's answer (extrapolated): voice mode disables Canvas;
agent reverts to text-only.

Ember's answer (when we get here): same. Voice and Canvas are
two surfaces; only one active at a time.

---

## The Agentic UI question

A bigger philosophical question:

**Should the agent decide when to use UI?** Or should the operator
decide ("show me a form")?

Both have merits:

- **Agent-decides**: more dynamic; less operator effort. But
  agent might over-UI or under-UI.
- **Operator-decides**: more control; less surprise. But misses
  the "huh, a form would be perfect here" insight.

OpenClaw seems agent-decides primarily. Ember should probably
*allow both*: agent suggests UI; operator can say "no, just text"
or "yes, give me the form."

The Mirror of Ginnungagap (per Yggdrasil) could observe operator
patterns and tune the agent's UI-vs-text bias over time.

---

## Configuration shape

```yaml
ember:
  canvas:
    enabled: false              # V5+
    surface:
      stofa: tui_widgets
      auga: gui_widgets
    spec_format: "odinui-1"
    agent_can_emit: true
    operator_can_suggest_text: true
    cache_widget_state_in_episode: true
```

---

## Risk: UI as control gimmick

OpenClaw's Canvas could be misused — agent rendering UI for
*every* response, even when text would suffice. Operator
fatigue follows.

Discipline: UI is for *specific* moments. Default to text. UI
is the exception, not the rule.

---

## What Ember should NOT do

🔴 **Reject for V1-V4**:

### 1. Full-fledged Canvas

Not until Auga exists (V5). Stofa TUI canvas is a *gentler*
introduction.

### 2. Proprietary spec

If we do this, use open spec. JSON-Schema for forms. Open Markdown
for content. No proprietary lock-in.

### 3. Always-on Canvas

Default off. Operator opts in. Some operators *never* want UI —
respect that.

---

## When this matters

Phases:
- V1-V2: text only.
- V3: minimal TUI canvas in Stofa (forms, selectors).
- V4: same; refine based on operator feedback.
- V5: full Canvas in Auga (when Auga exists).

This is *long-horizon*. Don't rush; observe operator demand;
build when justified.

---

## Closing

Live Canvas and A2UI are **OpenClaw's frontier feature** — the
agent rendering UI elements operator manipulates. New design
space. Few projects have explored.

Ember should:
- Study OpenClaw's approach (when their docs are available).
- Ship a minimal TUI canvas in V3 (forms + selectors).
- Full GUI canvas in V5 with Auga.
- Always with open spec, operator-controllable, sovereign.

This is the kind of feature that *might* land or *might not*
depending on operator demand. Plan it; build it when needed.

The lesson: **the conversation isn't always linear text**. UI
can be part of the agent's vocabulary. Use sparingly; use well.
