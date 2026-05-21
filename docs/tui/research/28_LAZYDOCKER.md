# 28 — Lazydocker

> https://github.com/jesseduffield/lazydocker

Jesse Duffield's other tool — a TUI for Docker. Teaches Stofa about
**dashboard-of-dashboards**, **the panel-cycle pattern**, and
**applying a single design template to a multi-domain app**.

---

## What it is

Like lazygit, but for Docker. Containers / images / volumes / networks
each get their own column; selecting one shows its details on the
right.

```
┌── Project ─┐┌── Containers ──────┐┌── Logs / Stats / Top / Env ────────┐
│ ember-dev   ││ ▶ ember-test       ││ {logs of selected container}        │
│ stofa-dev   ││   ollama-host      ││                                      │
│ skein-kg    ││   pgvector-test    ││                                      │
│             ││                    ││                                      │
└─────────────┘└────────────────────┘└──────────────────────────────────────┘
[1=projects 2=containers 3=images x=stop r=restart ?=help q=quit]
```

---

## The clever idea: same layout template, different domains

Lazydocker reuses lazygit's three-column-plus-detail template for
Docker. The operator who knows lazygit *already knows* lazydocker.

The deeper idea: **a good UI grammar can serve multiple domains.**
You don't have to invent a new layout per app. Pick a strong layout,
apply it everywhere, get muscle memory transfer for free.

### What we steal

Stofa applies the same idea internally: most screens use one of
**three layouts** (per [`../architecture/14_LAYOUT_SYSTEM.md`](../architecture/14_LAYOUT_SYSTEM.md)):

1. Grid (HomeScreen — 2×2 dashboard).
2. Vertical stack (ChatScreen — messages above input).
3. Two-pane (WellScreen — sources + details).

The operator who knows one screen *already knows* how to navigate
the others. Tab cycles focus; Enter activates; Esc backs out;
keyboard navigation is consistent.

---

## The cycle-through-panels pattern

Lazydocker's right panel cycles through tabs (Logs / Stats / Top /
Env) when the operator presses `]` or `[`. Same panel, different
content.

### What we steal — for V1, sparingly

Used in **DoctorScreen**: the right side cycles through realm details
(Funi / Strengr / Brunnr / MCP). Press `]` to cycle next.

Used in **WellScreen** for the document detail: tabs for "Metadata"
/ "Recent excerpt" / "Chunks". Press `]` to cycle.

Not used in **HomeScreen** or **ChatScreen** — those don't need
cycling.

### What we avoid

The "every panel has tabs" extreme. Tabs are good for *secondary*
content; the primary view should be visible without tab-cycling.

---

## The colored container status pattern

Lazydocker shows container state with color:

- Green = running
- Yellow = restarting
- Red = exited
- Grey = stopped

The color is on the bullet/dot before the name. Easy to scan a list
and pick out problems.

### What we steal

Stofa's MCPScreen + DoctorScreen use the same:

- $success (green-ish in Aurora) = up
- $warning (amber) = transitional / unhealthy but reachable
- $error (red-ish) = down
- $text-muted = not yet probed

Bullets / dots before the name, like lazydocker.

---

## What lazydocker teaches us about "dashboard as primary"

In lazydocker the dashboard *is* the application — you don't navigate
through pages; the columns ARE the navigation.

In Stofa, the dashboard (HomeScreen) is the *root*, and individual
deep-dive screens push on top via single-letter keys. Different
shape, same intent: information at a glance, deep-dive on demand.

The split: lazydocker's domain (Docker management) doesn't have a
single primary surface; everything is equally important. Stofa's
domain (AI chat) has chat as primary; everything else supports.

---

## Specific Stofa choices from lazydocker

- **Single template across screens** (the three layouts).
- **Color-coded status dots** for realms / MCP servers.
- **`]` / `[` to cycle tabs** in DoctorScreen detail and WellScreen
  detail.
- **Lazy-style key-hints in the StatusBar** (already covered by the
  lazygit study).

---

## Closing

Lazydocker proves that a TUI grammar generalizes. Stofa is internally
generalized: three layouts, one border style, five semantic colors,
one key-hint footer pattern. Every screen feels like the same
application because it *is* the same template, applied with care.
