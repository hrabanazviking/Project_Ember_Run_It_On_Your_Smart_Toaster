# 15 — Theming System

Stofa ships with **five built-in themes** and operators can write
their own. This document specifies the token contract every theme
honors, the runtime switching mechanism, and the rules for adding new
themes.

The actual palette files live in [`../design/64_PALETTE_AURORA.md`](../design/64_PALETTE_AURORA.md)
through [`../design/68_PALETTE_BARROW.md`](../design/68_PALETTE_BARROW.md).

---

## Token contract

Every theme defines values for **exactly this set of tokens**, and
**no other tokens**. Widgets reference tokens by name, never raw
colors. This is the load-bearing contract that makes themes
hot-swappable.

```scss
/* ─── Base surfaces ─── */
$background:    /* page background */
$surface:       /* panel / card background */
$surface-alt:   /* secondary background (input bars, headers) */

/* ─── Foreground text ─── */
$text:          /* primary readable text */
$text-muted:    /* secondary text (timestamps, hints) */
$text-disabled: /* disabled / unfocused */

/* ─── Semantic colors (the five) ─── */
$primary:       /* main accent (chrome, focused borders, hearth) */
$accent:        /* secondary accent (interactive: links, prompts) */
$success:       /* good states (Funi up, ingest done, citation found) */
$warning:       /* attention states (Well empty, approval pending) */
$error:         /* bad states (Funi down, tool error, refusal) */

/* ─── Pet-layer colors ─── */
$pet-raven:     /* Hugin's color */
$pet-fox:       /* Refur's color */
$pet-goat:      /* Heiðr's color */
$pet-bee:       /* Sumarbýfa's color */
$pet-cub:       /* Geri-cub's color */
$pet-sapling:   /* Ask-sapling's green */
$pet-drift:     /* Drift's color */
$pet-spark:     /* Funi-spark's fire color */

/* ─── Hearth ─── */
$hearth-base:   /* the hearth icon's body color */
$hearth-glow:   /* the pulse / glow color */
```

Total: **20 tokens**. Themes that try to add a 21st are rejected by
the theme loader.

Why a fixed token set:
- **Predictability for widgets.** Widget CSS references `$primary`;
  it works in any theme.
- **Predictability for theme authors.** Writing a theme is filling
  in 20 blanks, not inventing.
- **Predictability for the operator.** Theme A and theme B differ
  only in palette; the *semantics* are the same.

---

## Built-in themes (V1)

| Theme | Default? | Vibe | When |
|---|---|---|---|
| **Aurora** | ✅ yes | cool twilight, blue-purple | the cozy default |
| **Midgard** | no | warm earth, amber-green | bright daylight feel |
| **Ginnungagap** | no | deep void, near-black | minimal, distraction-free |
| **Solstice** | no | high-contrast bright | accessibility / projector |
| **Barrow** | no | colorblind-safe (deuteranopia + protanopia friendly) | accessibility |

Each has its own file in `../design/64_*.md` through `../design/68_*.md`
with hex values + rationale + a visual mock.

---

## Theme files in the codebase

Each theme is a `.tcss` (Textual CSS) file:

```
src/ember/stofa/themes/
├── aurora.tcss
├── midgard.tcss
├── ginnungagap.tcss
├── solstice.tcss
└── barrow.tcss
```

Each file is roughly 30 lines, defining the 20 tokens. Example
(aurora.tcss, abbreviated):

```css
:root {
    /* base */
    --background: rgb(20 24 32);
    --surface: rgb(28 32 42);
    --surface-alt: rgb(32 36 46);

    /* text */
    --text: rgb(220 220 220);
    --text-muted: rgb(150 160 175);
    --text-disabled: rgb(90 96 110);

    /* semantic */
    --primary: rgb(168 200 220);
    --accent: rgb(220 180 100);
    --success: rgb(140 180 120);
    --warning: rgb(220 180 100);
    --error: rgb(200 110 110);

    /* pets */
    --pet-raven: rgb(180 180 190);   /* slate grey, slightly cool */
    --pet-fox: rgb(200 140 100);     /* warm tan */
    --pet-goat: rgb(180 170 150);    /* cream */
    --pet-bee: rgb(220 180 80);      /* honey gold */
    --pet-cub: rgb(160 130 100);     /* warm brown */
    --pet-sapling: rgb(140 180 120); /* sage */
    --pet-drift: rgb(220 230 240);   /* near-white pale blue */
    --pet-spark: rgb(220 140 80);    /* ember orange */

    /* hearth */
    --hearth-base: rgb(120 80 60);
    --hearth-glow: rgb(220 140 80);
}
```

Textual's CSS engine reads `$primary` in widget CSS and substitutes
`var(--primary)` (or whatever syntax 2.x uses; we conform).

---

## Runtime switching

The operator switches themes via:

- **Command palette:** `:theme midgard`
- **Settings screen:** dropdown with live preview
- **Config file:** `stofa.theme: midgard` in `ember.yaml`

When the theme changes, `StofaApp.theme` (a reactive) is updated;
Textual's CSS hot-reload re-renders every widget. Operator sees a
soft color shift; no flicker beyond one frame; conversation buffer
preserved.

This is *real* live switching, not a relaunch. Validated in
`tests/integration/test_stofa_theme_swap.py`.

---

## Theme contract enforcement

A theme that fails to define any of the 20 tokens **fails to load**
with a clear operator error:

```
Theme "custom.tcss" missing tokens: $pet-drift, $hearth-glow
Falling back to Aurora theme.
```

A theme that defines extra tokens **also fails** (helps catch typos):

```
Theme "custom.tcss" defines unknown tokens: $primry, $foreground
(Did you mean $primary, $text?)
```

This is enforced by `stofa/themes/__init__.py::load_theme(path)`
which validates against the canonical token set before applying.

---

## Operator-supplied themes

Operators can write their own themes:

1. Create `~/.ember/themes/my-theme.tcss` with the 20 tokens.
2. Set `stofa.theme: ~/.ember/themes/my-theme.tcss` in `ember.yaml`.

The Stofa theme loader resolves the path with `Path.expanduser`.
Validation runs the same way as built-in themes.

We do NOT provide a theme editor in V1. (Theme Studio is a V2 screen.)

---

## How widgets use tokens

Widget CSS:

```css
Panel {
    background: $surface;
    color: $text;
    border: round $primary;
}

Panel:focus {
    border: round $accent;     /* focus indication */
}

Button.danger {
    background: $error 20%;     /* error tinted 20% */
    color: $text;
    border: round $error;
}

#hearth-icon {
    color: $hearth-base;
}

#hearth-icon.thinking {
    color: $hearth-glow;
}
```

Widget Python NEVER hardcodes colors:

```python
# wrong
self.styles.background = "rgb(20 24 32)"

# right
# (set via CSS class; the CSS references $surface)
self.add_class("themed-panel")
```

---

## Accessibility-first themes

Two of the five built-ins exist specifically for accessibility:

- **Solstice** — WCAG-AAA contrast across all token pairs.
- **Barrow** — deuteranopia + protanopia safe; reds replaced with
  brown-oranges; greens shifted away from collision with red.

See [`../ux-science/46_ACCESSIBILITY.md`](../ux-science/46_ACCESSIBILITY.md)
for the testing methodology and the specific deltas.

---

## Pet color coordination per theme

Each pet has a *role* color and a *theme-specific tint*. The
contract: every pet's color must be **distinguishable from the
panel background** in every theme.

Validation: a `tests/unit/test_stofa_theme_contrast.py` checks every
pet's color vs the background and warns if the WCAG-2.1 contrast
ratio is below 3.0:1 (the minimum for graphical elements).

---

## Animation tokens

Themes can also tune animation timings (V2 — placeholder for now):

```css
:root {
    --hearth-pulse-period-ms: 1000;
    --pet-tick-period-ms: 1000;
    --message-fade-ms: 200;
}
```

V1 hardcodes these; V2 surfaces them as theme-tunable.

---

## What themes are NOT

- **Not skinning.** Themes change color tokens. Layout, typography,
  spacing, box-drawing — same across all themes.
- **Not personalities.** The pets behave identically regardless of
  theme; only their colors shift.
- **Not switchable per-screen.** One theme at a time; applies to all
  screens.
- **Not animated.** A theme is a static set of colors; we don't
  ship transitions or gradients.

---

## Closing

Twenty tokens. Five themes. Hot-swappable. Validation-enforced. Pets
distinguishable in every palette. Custom themes via file path. This
is the contract that lets Védis switch from Aurora to Midgard during
golden hour without restarting Stofa.
