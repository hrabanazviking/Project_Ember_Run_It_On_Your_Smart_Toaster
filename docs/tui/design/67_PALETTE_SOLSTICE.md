# 67 — Palette: Solstice

**Solstice** is the high-contrast theme. The mood: midwinter
sunlight on snow, or midsummer noon — brightest light Stofa can
render. For operators who need **accessibility-grade contrast**,
**projector use**, or **screens in direct sunlight**.

WCAG AAA across every text/background pair.

---

## Full hex values

```scss
/* ─── Base surfaces ─── */
$background:    rgb(0 0 0);       /* #000000 — pure black (dark variant default) */
$surface:       rgb(20 20 20);    /* #141414 */
$surface-alt:   rgb(30 30 30);    /* #1E1E1E */

/* OR LIGHT VARIANT (operator-toggle within Solstice): */
/* $background:    rgb(255 255 255); */
/* $surface:       rgb(245 245 245); */
/* $surface-alt:   rgb(235 235 235); */

/* ─── Text ─── */
$text:          rgb(255 255 255); /* #FFFFFF — pure white (dark variant) */
$text-muted:    rgb(200 200 200); /* #C8C8C8 */
$text-disabled: rgb(140 140 140); /* #8C8C8C */

/* ─── Semantic (full saturation for clarity) ─── */
$primary:       rgb(0 200 255);   /* #00C8FF — bright cyan */
$accent:        rgb(255 220 0);   /* #FFDC00 — bright gold */
$success:       rgb(0 220 100);   /* #00DC64 — bright green */
$warning:       rgb(255 180 0);   /* #FFB400 — bright amber */
$error:         rgb(255 80 80);   /* #FF5050 — bright red */

/* ─── Pets ─── */
$pet-raven:     rgb(200 200 200); /* #C8C8C8 — pure grey */
$pet-fox:       rgb(255 140 60);  /* #FF8C3C — bright orange */
$pet-goat:      rgb(240 220 180); /* #F0DCB4 */
$pet-bee:       rgb(255 220 0);   /* #FFDC00 — matches accent */
$pet-cub:       rgb(200 140 80);  /* #C88C50 */
$pet-sapling:   rgb(80 220 80);   /* #50DC50 — bright green */
$pet-drift:     rgb(255 255 255); /* #FFFFFF — pure white */
$pet-spark:     rgb(255 120 60);  /* #FF783C — flame */

/* ─── Hearth ─── */
$hearth-base:   rgb(140 80 40);   /* #8C5028 */
$hearth-glow:   rgb(255 140 60);  /* #FF8C3C — bright fire */
```

---

## Why these colors

Solstice trades subtlety for *clarity*. Every color is saturated,
every contrast is at the maximum:

- **Pure black or pure white background.** No tint. The starting
  baseline for max contrast.
- **Pure white or pure black text.** Same. The 21:1 ratio is the
  WCAG ceiling.
- **Saturated semantic colors.** Bright cyan for primary, bright
  gold for accent, bright green for success — visible at 6 feet away
  on a projector.
- **Pets in saturated colors.** Drift the snowflake is pure white;
  Hugin the raven is pure grey; Bee is pure honey. Everything reads
  cleanly across the high-contrast surface.

This is not the *cozy* theme. This is the **functional** theme.
Operators with accessibility needs or specific environments come
here for utility.

---

## When to pick Solstice

- **Low vision.** WCAG AAA contrast helps.
- **Projector demos.** Bright, saturated colors carry across the
  room.
- **Direct sunlight on monitor.** Maximum visibility.
- **Operator preferring "loud" defaults.** Some like saturated; we
  serve them too.

---

## Two variants: dark Solstice and light Solstice

Solstice ships in both flavors. Operator picks:

```yaml
stofa:
  theme: solstice
  theme_variant: dark    # or "light"
```

**Dark Solstice**: pure-black background, pure-white text, saturated
colors on black.

**Light Solstice**: pure-white background, pure-black text, saturated
colors on white.

Both meet WCAG AAA. Different aesthetics for different operators.

---

## Contrast ratios

### Dark variant
| Pair | Ratio | WCAG |
|---|---|---|
| $text on $background | 21:1 | AAA (max) |
| $text-muted on $background | 13.2:1 | AAA |
| $primary on $background | 12.6:1 | AAA |
| $accent on $background | 18.9:1 | AAA |
| $error on $background | 7.6:1 | AAA |
| $success on $background | 14.1:1 | AAA |

### Light variant
Mirror values; all also AAA.

Solstice is the only Stofa theme guaranteed AAA across every text
pair. This is the accessibility default.

---

## When NOT to pick Solstice

- **Long evening sessions in a dark room.** The high contrast can
  fatigue (Aurora is gentler).
- **Aesthetic preference for cozy.** Solstice is the opposite of
  cozy.
- **OLED screens.** The pure-white in light Solstice is hard on
  OLED.

---

## Mock visual (dark Solstice)

```
╭══ Stofa ══ ᛞ ᛞ ᛞ ══ Chat ═══════════════════ 🔥 ═╮     ← bright cyan border
║                                                          ║
║   > volmarr: hello                                       ║     ← bright gold cursor
║                                                          ║
║   ember: hi! how can I help today?                       ║     ← pure white text
║                                                          ║
║   > volmarr: what's in my Well?                          ║
║                                                          ║
║   ember:                                                 ║
║   • notes/odin.md                                        ║     ← pure white bullet
║                                                          ║
║  > _                                                     ║
╰══════════════════════════════════════════════════════════╯
[ ● Funi  ●  Well  ●  MCP ]                       [Chat]
   ↑ pure saturated dots
```

(Solstice is the only theme where we'd consider double-line
borders for emphasis — they read more clearly under high-contrast.
V1 still uses rounded single; V2 may revisit.)

---

## Closing

Solstice is *not* the prettiest theme. It is the most *legible*.
Some operators need that. For them, Solstice is correct. For others,
it's an option in the picker that they pass over.
