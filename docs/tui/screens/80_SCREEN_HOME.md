# 80 — Screen: Home

The base screen. Always at the bottom of the screen stack. Landing
page for the operator after Stofa opens.

---

## Purpose

Two purposes:

1. **Dashboard** — at-a-glance view of Ember's current state across
   all four realms.
2. **Hub** — single-keypress entry to every other screen.

---

## Layout

```
┌── Stofa ───── ᛞ ᛞ ᛞ ───── Home ──────────────────────── 🔥 ─┐
│                                                              │
│  ┌──── Conversation ──────┐  ┌──── Well ──────────────┐    │
│  │                          │  │                         │    │
│  │  llama3.2:3b              │  │  95 documents           │    │
│  │  3 sessions today          │  │  35,418 chunks          │    │
│  │  c = open chat             │  │  ~240 MB                │    │
│  │                          │  │  w = browse + ingest    │    │
│  │                          │  │                         │    │
│  └──────────────────────────┘  └─────────────────────────┘    │
│                                                              │
│  ┌──── Realms ─────────────┐  ┌──── Tools ─────────────┐    │
│  │                          │  │                         │    │
│  │  ● Funi    llama3.2:3b   │  │  3 first-party tools    │    │
│  │  ● Strengr ok            │  │  2 MCP servers (2/2 ok) │    │
│  │  ● Brunnr  sqlite-vec    │  │  12 MCP tools           │    │
│  │  d = doctor               │  │  m = mcp · t = approve  │    │
│  │                          │  │                         │    │
│  └──────────────────────────┘  └─────────────────────────┘    │
│                                                              │
│  [Hugin perches here]    [Geri-cub asleep here]              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
[ ● Funi · ● Well 95 docs · ● MCP 2/2 ]   [Home]   [c/w/d/s/m · ? help · q quit]
```

---

## Implementation

`src/ember/stofa/screens/home.py` — `HomeScreen(textual.screen.Screen)`.

```python
class HomeScreen(Screen):
    BINDINGS = [
        Binding("c", "push_chat", "Chat"),
        Binding("w", "push_well", "Well"),
        Binding("d", "push_doctor", "Doctor"),
        Binding("s", "push_settings", "Settings"),
        Binding("m", "push_mcp", "MCP"),
        Binding("1", "focus_panel(0)", "panel 1", show=False),
        Binding("2", "focus_panel(1)", "panel 2", show=False),
        Binding("3", "focus_panel(2)", "panel 3", show=False),
        Binding("4", "focus_panel(3)", "panel 4", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            ConversationPanel(),
            WellPanel(),
            RealmsPanel(),
            ToolsPanel(),
            id="home-grid",
        )

    def on_resize(self, event: Resize) -> None:
        # Toggle .narrow class when width < 80
        narrow = event.size.width < 80
        self.set_class(narrow, "narrow")
```

CSS:

```css
HomeScreen {
    layout: grid;
    grid-size: 2 2;
    grid-columns: 1fr 1fr;
    grid-rows: 1fr 1fr;
    grid-gutter: 1;
    padding: 1 2;
}

HomeScreen.narrow {
    grid-size: 1 4;
}

HomeScreen > Panel {
    background: $surface;
    border: round $primary;
    padding: 1 2;
}

HomeScreen > Panel:focus {
    border: round $accent;
}
```

---

## Per-panel content

### ConversationPanel

Subscribes to:
- `FuniService.health` (current model id).
- `ChatScreen.episodes_count` (sessions today, computed from
  Brunnr's recent_episodes).

Shows:
- `{model-id}` (line 1, bold)
- `{episodes-today} sessions today` (line 2, muted)
- `c = open chat` (line 3, hint)

If Funi is Unavailable: shows "Funi disconnected — press d for
doctor".

### WellPanel

Subscribes to `WellService.stats`.

Shows:
- `{N} documents`
- `{M} chunks`
- `~{size} MB`
- `w = browse + ingest`

If Brunnr is Disconnected: "Brunnr disconnected — press d for
doctor".

### RealmsPanel

Subscribes to `DoctorService.realm_states`.

Shows one line per realm with status dot + brief detail:
- `● Funi    llama3.2:3b`
- `● Strengr ok`
- `● Brunnr  sqlite-vec`
- (and MCP if configured)

`d = doctor` hint at bottom.

Dots are colored: $success (ok), $warning (transitional), $error
(down).

### ToolsPanel

Subscribes to `MCPService.servers` and the tool registry.

Shows:
- `{N} first-party tools`
- `{M} MCP servers ({A}/{B} ok)`
- `{P} MCP tools`
- `m = mcp · t = approve`

If tools are disabled in config: "Tools disabled — set
tools.enabled: true".

---

## Pet positions on HomeScreen

- **Hugin**: default perch (bottom-left of the chrome).
- **Geri-cub**: usually asleep near the bottom-center.
- **Funi-spark**: top-right of chrome.
- **Ember-ember**: top-left of chrome.
- **Drift** (Aurora/Barrow): occasional traversal across the
  chrome.

---

## Navigation

The Home screen pushes other screens onto the stack:

| Key | Action |
|---|---|
| `c` | Push ChatScreen |
| `w` | Push WellScreen |
| `d` | Push DoctorScreen |
| `s` | Push SettingsScreen |
| `m` | Push MCPScreen |
| `?` | Open HelpOverlay |
| `:` | Open CommandPalette |
| `q` | Quit |

---

## Empty / first-time state

If the operator has no Episodes yet, the ConversationPanel shows:

```
No conversations yet.
Press c to chat with Ember.
```

If the Well has no documents:

```
Your Well is empty.
Press w to ingest a directory.
```

---

## What HomeScreen does NOT do

- **Not a settings screen.** Toggles + config live in Settings.
- **Not an activity log.** Recent activity is in StatusBar; long
  history is in EpisodeBrowserScreen (V2).
- **Not customizable in V1.** The 4-panel grid is fixed. V2's
  plugin architecture may add custom panels.

---

## Closing

HomeScreen is the *first thing* the operator sees and the place
they *return to*. Four panels, each scan-readable in ~2 seconds.
Five navigation keys, each a single letter matching the screen's
first letter. The dashboard surface that makes Stofa feel like a
real application rather than a chat window.
