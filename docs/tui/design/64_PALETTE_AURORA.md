# 64 — Palette: Aurora

**Aurora** is Stofa's default theme. The mood: northern twilight,
cool blue-grey landscape under amber-touched aurora. The hour just
after sunset in a Norse winter.

---

## Full hex values

```scss
/* ─── Base surfaces ─── */
$background:    rgb(20 24 32);    /* #14181F — deep twilight blue-grey */
$surface:       rgb(28 32 42);    /* #1C202A — slightly lifted panel */
$surface-alt:   rgb(32 36 46);    /* #20242E — secondary surface */

/* ─── Text ─── */
$text:          rgb(220 220 220); /* #DCDCDC — primary readable */
$text-muted:    rgb(150 160 175); /* #96A0AF — secondary */
$text-disabled: rgb(90 96 110);   /* #5A606E — disabled */

/* ─── Semantic ─── */
$primary:       rgb(168 200 220); /* #A8C8DC — cool sky blue */
$accent:        rgb(220 180 100); /* #DCB464 — warm amber */
$success:       rgb(140 180 120); /* #8CB478 — sage green */
$warning:       rgb(220 180 100); /* #DCB464 — matches accent */
$error:         rgb(200 110 110); /* #C86E6E — muted red */

/* ─── Pets ─── */
$pet-raven:     rgb(180 180 190); /* #B4B4BE — slate grey, slightly cool */
$pet-fox:       rgb(200 140 100); /* #C88C64 — warm tan */
$pet-goat:      rgb(180 170 150); /* #B4AA96 — cream */
$pet-bee:       rgb(220 180 80);  /* #DCB450 — honey gold */
$pet-cub:       rgb(160 130 100); /* #A08264 — warm brown */
$pet-sapling:   rgb(140 180 120); /* #8CB478 — sage (matches success) */
$pet-drift:     rgb(220 230 240); /* #DCE6F0 — near-white pale blue */
$pet-spark:     rgb(220 140 80);  /* #DC8C50 — ember orange */

/* ─── Hearth ─── */
$hearth-base:   rgb(120 80 60);   /* #785038 — banked embers, dim */
$hearth-glow:   rgb(220 140 80);  /* #DC8C50 — active glow */
```

---

## Why these colors

### Background: deep twilight blue-grey (#14181F)

Almost-black but not quite. The faint blue undertone evokes
northern night sky. Pure black (#000000) would be harsh in long
sessions; this is restful but dark enough that all foreground colors
have headroom.

### Primary: cool sky blue (#A8C8DC)

Desaturated blue. Used for chrome (panel borders, headers,
unfocused state). Reads as "structural" — present but not loud.
Complements the warm amber accent (color theory: cool + warm pair
catches the eye).

### Accent: warm amber (#DCB464)

Desaturated honey. Used for interactive elements (focused panel
border, command palette current selection, the hearth glow at peak
pulse). The "you can do something here" color. Warm against the
cool primary creates the visual interest the operator's eye wants.

### Success: sage green (#8CB478)

Calming green, low saturation. Used for "good" states (realms up,
ingest complete, citations found). Not a "hooray!" green; a
"quietly all-well" green.

### Warning: same as accent (#DCB464)

Deliberate overlap. Warnings and interactive elements both get the
amber. Reduces the operator's palette to remember: when amber
appears, it's *attention-worthy* (either as a thing to interact
with or as a thing requiring notice).

### Error: muted red (#C86E6E)

Not bright red. Not orange. A red that says "this is wrong" without
"the world is ending." Operators reading it for hours don't want
to be alarmed every time it appears.

---

## Pet colors

Each pet has a color that fits the Aurora palette family:

- **Hugin (raven)**: slate grey, slightly cool. Reads as a real raven
  against the dark background.
- **Refur (fox)**: warm tan, warmer than the goat. Distinguishes
  fox from goat.
- **Heiðr (goat)**: cream / off-white. Realistic for a Norse goat.
- **Sumarbýfa (bee)**: honey gold, brighter than the others. Bees
  are bright; this one is too.
- **Geri-cub (wolf cub)**: warm brown. Realistic, distinct from fox.
- **Ask-sapling (ash)**: sage green. Matches $success — implying
  "growing."
- **Drift (snowflake)**: pale near-white. Almost a tint of
  $background; ghostly.
- **Funi-spark (hearth flame)**: ember orange. Matches $hearth-glow.

All eight are *distinguishable from each other* and *distinguishable
from the background*. Verified in
`tests/unit/test_stofa_palette_contrast.py`.

---

## Contrast ratios (WCAG)

| Pair | Ratio | WCAG level |
|---|---|---|
| $text on $background | 11.4:1 | AAA |
| $text-muted on $background | 5.7:1 | AA Large |
| $text-disabled on $background | 2.5:1 | (decorative only) |
| $primary on $background | 7.8:1 | AAA |
| $accent on $background | 8.2:1 | AAA |
| $error on $background | 4.9:1 | AA |
| $success on $background | 6.5:1 | AA |

All text-bearing pairs meet at least AA. Decorative-element pairs
(border colors on background) all exceed the 3:1 graphical minimum.

---

## When Aurora doesn't work

- **Operator's room is dark and the monitor is at low brightness.**
  Aurora's dark background can disappear; Solstice (high contrast)
  is better.
- **Operator has color-vision deficiency that confuses the muted
  red/green.** Barrow is better.
- **Operator wants light-mode.** Midgard.
- **Operator wants deep-deep void.** Ginnungagap.

Aurora is the *cozy default*. The alternatives exist for operators
where cozy isn't right.

---

## Mock visual

(Imagine these characters rendered in their Aurora colors.)

```
╭──── Stofa ──── ᛞ ᛞ ᛞ ──── Chat ──────────────── 🔥 ───╮     ← primary border, accent rune
│                                                          │
│   > volmarr: hello there                                 │     ← accent prefix on operator
│                                                          │
│   ember: hi! how can I help today?                       │     ← primary prefix on Ember
│                                                          │
│   > volmarr: tell me about my notes on Odin              │
│                                                          │
│   ember: I found these in your Well:                     │
│                                                          │
│      • notes/odin.md — "the all-father has..."           │     ← text-muted citation
│                                                          │
│      Odin (also Óðinn) is the principal Norse god...    │     ← regular text
│                                                          │
│  > _                                                     │     ← accent cursor
╰──────────────────────────────────────────────────────────╯
[ ● Funi llama3.2:3b  ·  ● Well 95 docs  ·  ● MCP 2/2 ]  [Chat]
   ↑ success dots
```

The operator's eye lands on the input cursor (highest-saturation
accent) first, then the panel border (primary), then the StatusBar
(primary + success dots).

---

## Pet placement in Aurora mock

```
╭──── Stofa ────────────────────────────── 🔥 ─╮
│  ...                                          │
│                              [Hugin perches]  │   ← $pet-raven on $surface
│  ...                                          │
│                                               │
│       [Geri-cub sleeping]                     │   ← $pet-cub on $background
╰───────────────────────────────────────────────╯
```

Hugin slate grey reads against the cool blue-grey surface. Geri-cub
warm brown reads against the deeper twilight background. Both
distinguishable; neither dominant.

---

## Closing

Aurora is what the inside of a Stofa looks like at twilight — deep
cool blues outside, warm amber within, a fire dimly banked in the
corner, animals about. Default theme. Cozy by intent. Operators who
want different have four alternatives, each with its own register.
But this is the one we hope operators stay with.
