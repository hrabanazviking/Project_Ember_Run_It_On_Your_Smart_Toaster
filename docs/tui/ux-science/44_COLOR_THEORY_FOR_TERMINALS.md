# 44 — Color Theory for Terminals

How to use color in a TUI where you can't trust the operator's
terminal to render it the same as yours.

---

## What terminals can render

Modern terminals (2026) generally support:

- **16-color ANSI** (everywhere, always)
- **256-color xterm** (almost everywhere)
- **24-bit truecolor** (most modern terminals)

But:

- The operator's *theme* affects how the 16 ANSI colors look. "Bright
  green" in their terminal could be #5FFF5F or #00CC00 or anything.
- The operator's *brightness/contrast* setting affects perception.
- Some terminals advertise truecolor but lie.
- Light-mode vs dark-mode operators see *very* different palettes.

The lesson: **don't trust the rendering**. Design for variability.

---

## How Stofa picks colors

We define every color in **24-bit hex** in our `.tcss` theme files.
Textual then degrades to 256-color or 16-color as the terminal
requires. The token contract (20 named tokens) ensures we never
reach for a raw color in widget code.

### The five semantic colors (per palette)

Each theme defines these five with meaning, not name:

- **$primary** — chrome, accents, panel borders.
- **$accent** — interactive elements, links, focused things.
- **$success** — good state.
- **$warning** — attention state.
- **$error** — bad state.

These five are the *only* colors that carry meaning. Everything else
(neutrals, backgrounds, muted text) is decoration.

**A new palette is defined by choosing these five hex values.**
Everything else flows from them.

### The neutral surfaces

Each palette also defines:

- **$background** — page background (the "floor of the hall").
- **$surface** — panel background (slightly lifted).
- **$surface-alt** — secondary surface (input bars, headers).
- **$text** — primary readable text.
- **$text-muted** — secondary text.
- **$text-disabled** — inactive text.

These should have **at least 7:1 contrast** between `$text` and
`$background` (WCAG AAA). Verified in `tests/unit/test_stofa_palette_contrast.py`.

---

## The Aurora default

Aurora is Stofa's default palette. Cool twilight feel — deep
blue-grey background, muted blue primary, warm amber accent.

```
$background    rgb(20 24 32)     #14181F      
$surface       rgb(28 32 42)     #1C202A      
$surface-alt   rgb(32 36 46)     #20242E      

$text          rgb(220 220 220)  #DCDCDC      
$text-muted    rgb(150 160 175)  #96A0AF      
$text-disabled rgb(90 96 110)    #5A606E      

$primary       rgb(168 200 220)  #A8C8DC      ← cool blue
$accent        rgb(220 180 100)  #DCB464      ← warm amber
$success       rgb(140 180 120)  #8CB478      ← sage green
$warning       rgb(220 180 100)  #DCB464      ← matches accent
$error         rgb(200 110 110)  #C86E6E      ← muted red
```

Why these specific values:

- **Background is near-black but not black.** Pure black is harsh
  in a long session. #14181F has just enough blue to feel like
  twilight.
- **Primary is desaturated cool.** Won't fatigue the eye like
  pure cyan would.
- **Accent is desaturated warm amber.** Complements the cool
  primary. Standard "complementary color" theory.
- **Success is desaturated green.** Pure #00FF00 would be
  exhausting; sage is calming.
- **Warning is the same as accent.** Deliberate: "interactive
  things" and "attention things" both call for the same warm hue.
  Reduces palette complexity.
- **Error is desaturated red-brown.** Pure red is alarming; our
  red says "this is wrong" without "the building is on fire."

---

## Theme variations (preview; full detail in design/)

| Theme | Feel | Background hex |
|---|---|---|
| **Aurora** (default) | cool twilight | #14181F |
| **Midgard** | warm daylight | #F5EFE0 (light!) |
| **Ginnungagap** | deep void | #050505 |
| **Solstice** | high contrast | #FFFFFF or #000000 |
| **Barrow** | colorblind-safe | #1C2030 |

See [`../design/64_PALETTE_AURORA.md`](../design/64_PALETTE_AURORA.md)
through [`../design/68_PALETTE_BARROW.md`](../design/68_PALETTE_BARROW.md)
for the full specifications.

---

## Color theory principles applied

### Complementary contrast for important pairs

The most important visual pairs in Stofa use complementary hues:

- $primary (cool blue) + $accent (warm amber) — operator's eye
  notices the contrast.
- $background (cool dark) + $text (warm-leaning grey) — easy to
  read.

### Analogous harmony for the rest

Pets, hearth, drift — these share a *harmonic* relation to the
primary palette. They don't fight for attention.

Example in Aurora:
- $pet-raven = rgb(180 180 190) — slate grey, slightly cool
- $pet-fox = rgb(200 140 100) — warm tan
- $pet-bee = rgb(220 180 80) — golden, harmonizes with $accent
- $pet-drift = rgb(220 230 240) — pale, near-background-but-lighter

Each pet has a color that *belongs* to Aurora's family.

### Saturation as a hierarchy lever

Across all of Stofa, **higher saturation = higher importance**.

- Chrome: low-medium saturation (lives in the background).
- Pets: medium saturation (notice but don't shout).
- Errors: medium-high saturation (call attention).
- The cursor in the input bar: highest saturation (this is *where
  you are*).

We avoid extreme saturations (>90%) — they fatigue the eye over
long sessions.

### Lightness step for legibility

The lightness step between $background and $text is the most
important pair. We aim for **8:1 contrast** in dark themes,
**12:1** in light themes. WCAG AA wants 4.5:1 for body text; we
exceed.

---

## What we explicitly DON'T do

- **Use white** (#FFFFFF) for body text. Pure white is fatiguing;
  we use ~220-230 grey.
- **Use pure black** (#000000) for backgrounds, except in
  Ginnungagap (which is opt-in for that aesthetic).
- **Use pure primary colors** anywhere. No #FF0000, no #00FF00, no
  #0000FF. Everything is desaturated.
- **Use color as the only signal.** Every color-bearing element is
  *also* labeled / positioned / iconified. Colorblind operators
  always have a non-color path.
- **Animate color changes mid-frame.** A panel that changes color
  while you're reading is distracting. We change color only on
  events (focus, state change).

---

## Colorblind safety

8% of men and 0.5% of women have some color-vision deficiency. Most
common: red-green confusion (deuteranopia, protanopia).

Mitigations:

- **No red/green pairs as the only differentiator.** Always also
  use shape (●○●) or position (left/right).
- **Errors use both color AND a prefix** ("Error: …" rather than
  just red text).
- **Status indicators use shape** (●●● for full, ●●○ for partial,
  ●○○ for low).
- **The Barrow palette** uses brown-orange instead of pure red,
  and shifts greens away from red's spectral neighborhood.

See [`46_ACCESSIBILITY.md`](46_ACCESSIBILITY.md) for the full
accessibility section.

---

## Color math (for curious operators)

We use simple sRGB hex. The token values are picked by hand, not
computed. But we apply a few rules:

- For text-on-background contrast, we use the WCAG-2.1 formula
  and target ≥ 7:1 (AAA).
- For decorative-on-background contrast, we target ≥ 3:1 (graphical
  elements minimum).
- For pet-on-background contrast, we target ≥ 3:1 (so pets are
  visible).

A `tests/unit/test_stofa_palette_contrast.py` test runs these checks
on every theme at every load.

---

## When the operator's terminal doesn't support truecolor

Textual auto-degrades:

- **Truecolor** → exact hex.
- **256-color** → nearest 256-color match (small visual difference).
- **16-color** → nearest ANSI match (significant visual difference,
  but all semantic distinctions preserved).

For the 16-color fallback:

| Token | 16-color approximation |
|---|---|
| $primary | bright blue |
| $accent | bright yellow |
| $success | green |
| $warning | yellow |
| $error | red |
| $text | white |
| $text-muted | bright black (grey) |

The semantic content is preserved; the aesthetic suffers. Acceptable.

---

## Closing

Color in terminal UIs is *less* free than in GUIs. We have less
control over rendering. We have to design for variability. Stofa
responds by being *aggressive about restraint*: five semantic
colors, 20 tokens total, contrast verified in CI, colorblind-safe
variants shipped. Restrained color is the secret to "looks beautiful
on every terminal."
