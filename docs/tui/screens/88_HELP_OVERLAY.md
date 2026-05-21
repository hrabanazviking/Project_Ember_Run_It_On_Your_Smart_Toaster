# 88 — Help Overlay

A translucent overlay showing keybindings for the current screen.
Always one keypress away.

---

## Purpose

Discoverability. Operators don't have to remember; `?` always
tells them.

---

## Layout

The overlay renders on top of the current screen, dimming the
underlying content. Centered, ~60-70% of screen width:

```
                ╭─ Help (Chat screen) ─────────────────────────╮
                │                                                │
                │  Global:                                       │
                │    ? F1       this help                        │
                │    : Ctrl-P   command palette                  │
                │    q Ctrl-C   quit                             │
                │    h          Home                             │
                │    Esc        cancel / pop                     │
                │    p          toggle pets                      │
                │                                                │
                │  Navigation:                                   │
                │    c          Chat (you are here)              │
                │    w          Well                             │
                │    d          Doctor                           │
                │    s          Settings                         │
                │    m          MCP                              │
                │                                                │
                │  Chat:                                         │
                │    Enter      send message                     │
                │    Shift+Ent  newline                          │
                │    ↑          recall last message              │
                │    Ctrl-C     interrupt streaming              │
                │    Ctrl-U     clear input                      │
                │    Ctrl-A     open audit log                   │
                │                                                │
                │  Approval modal (when shown):                  │
                │    y          approve once                     │
                │    a          approve + remember session       │
                │    n          deny                             │
                │                                                │
                │  Press ? or Esc to close.                      │
                ╰────────────────────────────────────────────────╯
```

---

## Implementation

`src/ember/stofa/screens/help_overlay.py` —
`HelpOverlay(textual.widget.Widget)`.

It's a **Widget**, not a Screen. Rendered via Textual's `layers`
support, on top of the active screen.

```python
class HelpOverlay(Widget):
    DEFAULT_CSS = """
    HelpOverlay {
        layer: overlay;
        background: $background 60%;
        align: center middle;
    }
    """
```

The 60% alpha (where supported) dims the underlying content but
keeps it visible.

---

## Contents

Three sections, always in this order:

1. **Global** — keys that work everywhere.
2. **Navigation** — screen jumps; current screen marked "(you are here)".
3. **Screen-specific** — the active screen's keys.

Plus a context-conditional section: if the active screen has a
modal up (like ToolApprovalScreen), the modal's keys appear too.

---

## How content is sourced

Each screen declares its bindings via Textual's `BINDINGS` list:

```python
class ChatScreen(Screen):
    BINDINGS = [
        Binding("enter", "send", "send message", show=True),
        Binding("ctrl+c", "interrupt", "interrupt streaming", show=True),
        Binding("up", "recall_last", "recall last message", show=True),
        Binding("ctrl+u", "clear_input", "clear input", show=True),
        # ... etc
    ]
```

The overlay reads `app.bindings` + `app.screen.bindings` and renders
the ones marked `show=True`. Hidden bindings (numeric column-focus
shortcuts, etc.) are not shown — they're for power users who already
know them.

---

## Pet legend (V1 addition)

Below the screen-specific section, the help overlay includes a
small pet legend:

```
                │  Pets:                                         │
                │    🔥  Funi-spark  pulses when Ember thinks   │
                │    ●   Ember-ember  the logo                   │
                │    Hugin (raven)  perches over citations       │
                │    Refur (fox)    watches during approval       │
                │    Heiðr (goat)   drops horns on audit         │
                │    Sumarbýfa (bee) ferries during ingest       │
                │    Geri-cub      sleeps in the corner          │
                │                                                │
                │  Press p to toggle all pets.                   │
```

This is the operator's reference for what each pet means.

---

## Keybindings (for the overlay itself)

| Key | Action |
|---|---|
| `?` | Close the overlay |
| `Esc` | Close the overlay |
| `↓` / `j` | Scroll down (if overlay overflows) |
| `↑` / `k` | Scroll up |

---

## Pet behavior under the overlay

Pets are dimmed along with the rest of the underlying screen.
Animation continues at the same rate; just less visible.

When the overlay opens, no pet jumps to alert — the overlay is the
operator's choice, not an event.

---

## Responsiveness

The overlay scales:

- **Wide terminal:** ~60-cell-wide overlay.
- **Medium (80-99):** ~50-cell overlay.
- **Narrow (<80):** ~40-cell overlay; some long key descriptions
  truncate with `…`.
- **Very narrow (<40):** overlay takes most of the screen; minimal
  decoration.

---

## V2 enhancements (not in V1)

- **Search.** `/` from inside the overlay narrows the visible
  bindings.
- **Click-binding.** Click a row to invoke the action (with mouse
  enabled).
- **Customizable display.** Operator can hide sections they don't
  care about.

---

## Closing

The help overlay is the **escape hatch from confusion**. Operator
sees something they don't know how to do → presses `?` → reads.
One keypress to discoverability. The single most-used overlay
across all five personas.
