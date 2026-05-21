# 14 — Layout System

Stofa uses Textual's CSS-based layout. This document is the **layout
contract** — what containers exist, how widgets are positioned, and
the rules that keep every screen visually consistent.

---

## The layout primitives

Textual gives us three layout strategies. We use all three, each in
its right place:

| Layout | When to use | Example |
|---|---|---|
| `vertical` | Stacking widgets top-to-bottom | Chat panel (header / messages / input) |
| `horizontal` | Side-by-side widgets | Home dashboard (2 columns of panels) |
| `grid` | Fixed-cell layouts | The 2×2 home dashboard |

We do **not** use `layers` for the main UI — only for the pet layer
(which floats on top of everything).

---

## The Stofa layout grammar

Every screen follows the same outer structure:

```
┌─ ChromeHeader (1 row) ─────────────────────────────┐
│  Stofa · {current-screen-name}  🔥  ⏎ {model-id}    │
├────────────────────────────────────────────────────┤
│                                                    │
│           ScreenContent (variable rows)             │
│           (this is where each screen renders)       │
│                                                    │
├────────────────────────────────────────────────────┤
│ Status: {realm-states} · {tools} · {last-action}    │
└─ StatusBar (1 row) ────────────────────────────────┘
```

`ChromeHeader` and `StatusBar` are **chrome** — they belong to
StofaApp, not to individual screens. Every screen renders inside
ScreenContent, which is the App's body.

This is enforced by composition: `StofaApp.compose` yields
`ChromeHeader`, then `ScreenContainer` (which Textual fills with the
active screen), then `StatusBar`.

---

## The HomeScreen 2×2 grid

The Home dashboard is a 2×2 grid of panels, each with its own
internal vertical layout:

```css
HomeScreen {
    layout: grid;
    grid-size: 2 2;            /* 2 cols, 2 rows */
    grid-columns: 1fr 1fr;
    grid-rows: 1fr 1fr;
    grid-gutter: 1;            /* 1 cell of breathing room */
    padding: 1 2;
}
```

Each panel inside is its own `Panel` widget (a `Vertical` container
with a titled border).

When the terminal is too narrow (`width < 80`), the grid degrades to
`grid-size: 1 4` (single column, 4 rows). This is handled via Textual's
responsive CSS:

```css
HomeScreen {
    grid-size: 2 2;
}

HomeScreen.narrow {
    grid-size: 1 4;
}
```

The App listens for `Resize` events and toggles the `.narrow` class
on HomeScreen when `width < 80`. One-line responsive design.

---

## ChatScreen layout

ChatScreen is `vertical`:

```
┌──── Conversation: {ember-name} ──── 🔥 ─────────────┐
│                                                      │
│  ┌──── messages (scrollable) ────────────────────┐  │
│  │  > operator: hello                            │  │
│  │  ember: hi there! …                           │  │
│  │  > operator: what do my notes say about X     │  │
│  │  ember: …                                     │  │
│  │  ┌─ citations ─────────────────────────────┐  │  │
│  │  │ • notes/odin.md · "…"                    │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  > _                                          [Enter]│
└──────────────────────────────────────────────────────┘
```

In CSS:

```css
ChatScreen {
    layout: vertical;
    padding: 0 1;
}

ChatScreen > MessagesView {
    height: 1fr;          /* takes all remaining vertical space */
    border: round $primary;
    padding: 1 2;
}

ChatScreen > InputBar {
    height: 3;            /* fixed 3 rows */
    border: round $accent;
    padding: 0 1;
}
```

`1fr` is Textual's "take remaining space" unit. The input bar has
fixed height (3 rows: top border + content + bottom border).

---

## WellScreen layout (two-pane)

Two columns: a document tree on the left, document details on the
right. Standard file-manager pattern (see [`research/24_RANGER_AND_NNN.md`](../research/24_RANGER_AND_NNN.md)).

```
┌──── Well ──── 95 docs · 35,000 chunks · 240MB ─────────────────────┐
│ ┌─ Sources ──────┐ ┌─ Details ──────────────────────────────────┐  │
│ │ notes/         │ │ {selected document}                         │  │
│ │   odin.md      │ │                                             │  │
│ │   yggdrasil.md │ │ Title:    notes/odin.md                    │  │
│ │ research/      │ │ Content:  md                                │  │
│ │   ai_safety.pdf│ │ Hash:     abc12345                          │  │
│ │   ...          │ │ Chunks:   23                                │  │
│ └────────────────┘ │ Ingested: 2026-05-20T17:45:33Z              │  │
│                    │                                             │  │
│                    │ Recent excerpt:                              │  │
│                    │   "Odin's ravens, Huginn and Muninn…"       │  │
│                    │                                             │  │
│                    │ i = ingest a path · r = re-ingest selected  │  │
│                    └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

```css
WellScreen {
    layout: horizontal;
    padding: 0 1;
}

WellScreen > SourcesPanel {
    width: 30;             /* fixed 30 cells */
    border: round $primary;
}

WellScreen > DetailsPanel {
    width: 1fr;
    border: round $primary;
    padding: 0 2;
}
```

Narrow-mode (`width < 80`): collapse to a single column with the
sources at top, details below.

---

## DoctorScreen layout

Tabular: one row per realm.

```
┌──── Doctor ───────────────────────────────────────────────────────┐
│                                                                    │
│   Realm     Status              Detail                             │
│   ──────    ──────              ──────                             │
│   Funi      ✓ ok                model: llama3.2:3b                 │
│                                 endpoint: http://100.67.…           │
│                                 last_ok: 2 seconds ago             │
│                                                                    │
│   Strengr   ✓ ok                backend: sqlite-vec                │
│                                 last_ok: 2 seconds ago             │
│                                                                    │
│   Brunnr    ✓ ok                95 docs · 35,000 chunks            │
│                                 ~/.ember/well/store.db (240 MB)    │
│                                                                    │
│   MCP       ✓ 2 of 2 servers    filesystem (12 tools) · github (8) │
│                                                                    │
│   r = re-run probe ·  esc = back                                   │
└────────────────────────────────────────────────────────────────────┘
```

Implemented as a `DataTable` for the rows + a `Static` for the keys
footer.

---

## SettingsScreen layout

Form-shaped. Sections are collapsible panels.

```
┌──── Settings ─────────────────────────────────────────────────────┐
│                                                                    │
│  ▾ Identity                                                        │
│      Ember's name: [ Mimir              ]                          │
│      Operator:     [ Volmarr            ]                          │
│                                                                    │
│  ▾ Funi (LLM)                                                      │
│      Runtime:      [ ollama          ▾ ]                           │
│      Model:        [ llama3.2:3b        ]                          │
│      Endpoint:     [ http://localhost:11434 ]                      │
│      Streaming:    [ ✓ ]                                           │
│                                                                    │
│  ▸ Brunnr (Well)                                                   │
│  ▸ Tools                                                           │
│  ▸ MCP                                                             │
│  ▾ Stofa                                                           │
│      Theme:        [ aurora         ▾ ] (live preview)             │
│      Pets:         [ ✓ ]  Animate: [ ✓ ]                           │
│      Start screen: [ home          ▾ ]                             │
│                                                                    │
│  s = save · esc = cancel · ? = field help                          │
└────────────────────────────────────────────────────────────────────┘
```

Each section is a `Collapsible` widget. The currently-collapsed state
is remembered per-session in App memory; doesn't persist (we don't
want to remember "you last had Brunnr collapsed").

---

## Common layout rules

These hold everywhere:

1. **Outer borders are always `round`.** No `solid` or `tall`.
2. **Padding inside panels is always `0 1` or `1 2`.** Never `0`,
   never `>2`.
3. **Margins between panels are always `1`.** Set via grid-gutter or
   widget-margin.
4. **Fixed-width sidebars use cells, not %.** `width: 30` not
   `width: 30%`. Cells are predictable across terminal widths.
5. **Variable space uses `1fr`.** Multiple `1fr` siblings split
   space proportionally.
6. **No CSS `layers` for normal widgets.** Pet layer is the sole
   exception.
7. **No overflow scroll bars.** Use Textual's automatic scrolling
   for content-overflowing widgets; the scrollbar appears on demand.

---

## Responsive breakpoints

Three tiers:

| Width | Class | Behavior |
|---|---|---|
| ≥ 100 cells | (default) | All panels at intended size; sidebars at fixed widths |
| 80–99 cells | `.medium` | Sidebars narrower (24 instead of 30); home grid 2×2 |
| < 80 cells | `.narrow` | Single-column layouts; sidebars collapse; home grid 1×4 |

`StofaApp` watches `on_resize` and toggles classes on the active
screen. Each screen's CSS handles its narrow/medium variant.

---

## What the layout system is not

- **Not pixel-perfect.** Terminal cells are not pixels; we round to
  cells. A `width: 30` is exactly 30 cells, but how wide that is
  depends on the operator's font.
- **Not absolute-positioned.** Everything is in a layout container.
  No `position: absolute`. The pet layer is the exception (see
  [`pets/72_PETS_BEHAVIOR_ENGINE.md`](../pets/72_PETS_BEHAVIOR_ENGINE.md)).
- **Not framework-dependent for the contract.** This layout grammar
  would translate to any reasonable TUI framework; we picked Textual
  to *implement* it, not to define it.

---

## Layout testing

Per the Vow of the Unbroken Whole: tested at three sizes.

- `80 × 24` — minimum supported (xterm default; also the
  smallest tmux pane operators typically allocate).
- `120 × 40` — common modern terminal.
- `200 × 60` — large monitor.

A pytest fixture in `tests/integration/test_stofa_layout.py` runs
each screen at each size and snapshot-tests the rendered output for
"no widget overflows its container" + "no widget vanishes off-screen."

---

## Closing

The layout system is **constrained on purpose**. Three layouts,
three breakpoints, one border style, two padding values. That
constraint is what makes every screen feel like part of the same
application.
