# 42 — Live Canvas for Auga

How specifically to build a Live-Canvas-equivalent in Auga,
Ember's planned GUI sibling. Concrete Phase 5+ plan.

---

## Auga is the planned GUI

Per Yggdrasil + Norse naming: **Auga** = Old Norse "eye."
The visual surface through which the operator sees Ember.

Auga is *deferred to V5+*. We have time to design it
thoughtfully.

---

## What Canvas-equivalent enables

Per [`../patterns/15_LIVE_CANVAS_A2UI.md`](../patterns/15_LIVE_CANVAS_A2UI.md):
the agent can render interactive UI elements within chat
responses. Forms, buttons, sliders, lists, charts.

For Auga V5+:

### Forms
Agent: "To plan your trip, I need a few details."  
Auga: renders form with dest/dates/budget fields.

### Lists
Agent: "Here are 5 options."  
Auga: renders selectable list; operator clicks one.

### Charts
Agent: "Your reading patterns over time."  
Auga: renders chart inline in chat.

### Confirmations
Agent: "Delete these 3 files?"  
Auga: renders confirm/cancel buttons.

### Iterative refinement
Agent: "Current plan: X, Y, Z. Adjust?"  
Auga: shows current state with editable fields.

---

## The OdinUI spec

Rather than OpenClaw's proprietary A2UI, Ember should define an
*open spec*: **OdinUI** (Old Norse "Odin's eye" — the all-
seeing eye).

### OdinUI as JSON

```json
{
  "type": "form",
  "title": "Trip planner",
  "fields": [
    {
      "name": "destination",
      "label": "Where to?",
      "type": "text",
      "required": true
    },
    {
      "name": "departure",
      "label": "Leave date",
      "type": "date",
      "required": true
    },
    {
      "name": "budget",
      "label": "Budget",
      "type": "number",
      "min": 100,
      "required": false
    }
  ],
  "submit": "Plan trip"
}
```

Simple. Documented. Open. Anyone can implement.

### OdinUI components

V1 spec:
- `text_input`, `number_input`, `date_input`, `select`,
  `checkbox`, `radio` — form primitives.
- `form` — container with submit.
- `list` — selectable items.
- `card` — content presentation.
- `chart` — bar/line/pie.
- `button` — action trigger.
- `progress` — long-running operation indicator.

V2 spec adds:
- `editor` — embedded text/code editor.
- `image` — display image.
- `audio` — play audio.
- `map` — geographic display.

Each component has stable JSON schema. Versioned.

---

## How the agent emits OdinUI

In agent's response, JSON inside markdown code fence:

````markdown
Here's the trip planner:

```odinui
{
  "type": "form",
  ...
}
```

Once you submit, I'll plan based on what you specify.
````

Auga parses the fence; renders inline; operator interacts.
Form submission becomes follow-up chat input.

This is *backward-compatible*: agents that don't emit OdinUI
just produce normal text. Auga renders both.

---

## How the LLM learns to emit it

System prompt augmentation:

```
You have access to OdinUI for interactive UI elements when
appropriate. To emit a form/list/etc., wrap JSON in an
`odinui` code fence. The spec is at <link>.

Use OdinUI sparingly:
- For multi-field input (forms).
- For confirmations of consequential operations.
- For selection from finite lists.

Don't use for: casual conversation, single-text-input prompts.
```

Few-shot examples in TOOLS.md or workspace files.

---

## Stofa fallback

Auga is V5+. Stofa is V2-onwards. Stofa is TUI.

Stofa can render *some* OdinUI:
- `form` → in-terminal text fields with tab navigation.
- `list` → numbered list with hotkey selection.
- `confirm` → yes/no prompt.
- `chart` → ASCII chart.

What Stofa *can't*:
- Rich charts (line graphs with axes).
- Images.
- Maps.
- Complex layouts.

Operator using Stofa: gets simplified rendering. Same agent;
different surface fidelity.

---

## Munnr fallback

Munnr (CLI) is text-only. Cannot render OdinUI.

If agent emits OdinUI to Munnr: agent should fall back to text
prompt instead. The Gateway can pass surface capabilities to
the agent's prompt assembly.

---

## What Auga uses for rendering

V5 candidate stacks:

### Option A: Tauri (Rust + web frontend)
- Pros: native window; web-based UI; small binary.
- Cons: requires Rust knowledge for Tauri customization.

### Option B: Python Tkinter
- Pros: pure Python; in stdlib; works everywhere.
- Cons: looks dated; limited.

### Option C: Python + Qt (PyQt6 / PySide6)
- Pros: modern look; powerful.
- Cons: Qt licensing; larger install.

### Option D: Python + Textual-web
- Pros: same code as Stofa; Textual supports web rendering.
- Cons: limited richness for true GUI.

### Recommendation

For V5: **Option D (Textual-web)**. Same code as Stofa; less
work; covers 80% of needs.

For V6+: revisit if richer UI is justified.

This is *pragmatic* — extending Stofa to web rather than
building a separate GUI stack. Less code; more consistency.

---

## OdinUI as web companion

The web companion (per
[`../patterns/17_COMPANION_APP_PAIRING.md`](../patterns/17_COMPANION_APP_PAIRING.md))
in V5+ would render OdinUI naturally — it's a browser; renders
JSON-described UI is easy.

So OdinUI works in three surfaces:
- Auga (desktop GUI / Textual-web): full fidelity.
- Stofa (TUI): simplified.
- Web companion: full fidelity (browser-native).

Agent emits once; surfaces render appropriately.

---

## Interactive vs static

Some OdinUI elements need *responses* (form submit, list
select). These create follow-up chat turns:

```
operator: "plan a trip"
agent: [emits OdinUI form]
operator: [fills + submits form]
agent: [receives form data as chat input]
agent: "Based on your inputs..."
```

The agent's response after submit references the form data. The
chat is *coherent across* the UI interaction.

---

## Caching widget state

If operator's session pauses (close laptop) and resumes, the
form should persist. OdinUI elements get session-attached state.

Stored in `~/.ember/state/sessions/<session_id>/widgets/`.

---

## Privacy considerations

OdinUI elements may capture data:
- Forms collect operator input.
- Editor changes content.
- Selections create preferences.

This data flows back to the agent. Same as any chat input.
*Logged* in audit; *visible* to operator; *not* sent off-device.

---

## Configuration shape

```yaml
ember:
  ui:
    odinui:
      enabled: true                # by default if Auga running
      version: 1
      max_widgets_per_response: 5  # cap to prevent flood
    
    auga:
      enabled: false               # V5+
      surface: textual-web
      bind: 0.0.0.0
      port: 8889
    
    stofa:
      odinui_simplified_rendering: true
```

---

## V5 ship plan for OdinUI

Order of implementation:

1. **Spec**: write OdinUI spec doc + JSON schema.
2. **Renderer (Auga)**: render basic components.
3. **Stofa simplified renderer**: render form/list/confirm.
4. **Agent prompts**: teach Funi to emit OdinUI.
5. **Test**: synthesis testing of forms / lists / charts.
6. **Document**: how operators see + use Canvas.

Modular. Each step is shippable independently.

---

## What Auga doesn't do

🔴 **Reject for V5**:

### 1. Replace Stofa

Stofa is TUI primary; Auga is GUI for operators preferring it.
Both ship; both work.

### 2. Native mobile app

Auga is desktop / Textual-web. Mobile is web companion.

### 3. Vendor-locked UI framework

Stay Python + Textual-web for V5. No commitment to Qt/Tk/etc.

---

## Closing

Live Canvas for Auga is **V5+ work; OdinUI is the open spec; Auga is the rendering surface**.

Ember gets:
- An open Canvas-equivalent (OdinUI).
- Three surfaces rendering it (Auga, Stofa-simplified, web).
- Agents emitting forms/lists/charts when appropriate.
- Operator-friendly interaction extending chat shape.

This is **a major Phase 5+ surface upgrade**. Plan now; build
in V5.

The Klóinn lesson: rich UI within chat is *valuable*. We define
it openly (OdinUI), implement it modularly (Auga + Stofa
fallback), and ship sovereignly.
