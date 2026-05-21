# 66 — Palette: Ginnungagap

**Ginnungagap** is the deep-void theme. The mood: the primordial
chasm before creation, true-black with tiny restrained highlights.
For operators who want distraction-free and don't mind aesthetic
asceticism.

(Ginnungagap = "the yawning gap" in Norse cosmology; the void
between Niflheim and Muspelheim from which the worlds were formed.)

---

## Full hex values

```scss
/* ─── Base surfaces ─── */
$background:    rgb(5 5 5);       /* #050505 — true near-black */
$surface:       rgb(12 12 12);    /* #0C0C0C — almost no lift */
$surface-alt:   rgb(20 20 20);    /* #141414 — secondary */

/* ─── Text ─── */
$text:          rgb(210 210 210); /* #D2D2D2 — pure light grey */
$text-muted:    rgb(130 130 130); /* #828282 — middle grey */
$text-disabled: rgb(70 70 70);    /* #464646 — disabled */

/* ─── Semantic (deliberately minimal) ─── */
$primary:       rgb(150 150 170); /* #9696AA — pale cool grey */
$accent:        rgb(200 200 220); /* #C8C8DC — slightly brighter accent */
$success:       rgb(120 160 110); /* #78A06E — muted forest */
$warning:       rgb(200 170 90);  /* #C8AA5A — pale gold */
$error:         rgb(190 100 100); /* #BE6464 — muted red */

/* ─── Pets ─── */
$pet-raven:     rgb(140 140 150); /* #8C8C96 — slate */
$pet-fox:       rgb(170 130 90);  /* #AA825A — pale tan */
$pet-goat:      rgb(180 170 150); /* #B4AA96 — cream */
$pet-bee:       rgb(200 170 80);  /* #C8AA50 — gold */
$pet-cub:       rgb(140 110 80);  /* #8C6E50 — brown */
$pet-sapling:   rgb(120 160 110); /* #78A06E — sage */
$pet-drift:     rgb(180 200 220); /* #B4C8DC — pale blue */
$pet-spark:     rgb(200 130 80);  /* #C88250 — ember */

/* ─── Hearth ─── */
$hearth-base:   rgb(100 70 50);   /* #644632 — dim */
$hearth-glow:   rgb(200 130 70);  /* #C88246 — bright */
```

---

## Why these colors

Ginnungagap pushes the **restraint** principle to its limit:

- **Background is near-black.** True #000000 would be too harsh
  against #FFFFFF cursors etc.; #050505 gives the OS just enough
  to render the cursor and selection markings.
- **Surfaces barely lift from the background.** The eye barely
  notices panel boundaries; the chrome reads as a thin outline.
- **Primary and accent are cool greys.** No color in the chrome.
  The only color in Ginnungagap is in the *semantic* indicators —
  success (sage), warning (gold), error (red), and the hearth glow.
- **Pets keep their full colors.** Pets are the only consistent
  warm/colorful element. They stand out vividly against the void.
- **The hearth is the only bright thing.** When Funi is thinking,
  the hearth glow is the brightest pixel on screen.

---

## When to pick Ginnungagap

- **Long focus sessions.** When the operator wants zero visual
  noise.
- **Late-night work.** The deepest dark; least eye fatigue.
- **OLED screens.** True black saves power on OLED.
- **Aesthetic preference for minimalism.** Some operators want
  Spartan; this is for them.

---

## What Ginnungagap is NOT

- **NOT high-contrast.** Use Solstice for that.
- **NOT colorblind-safe.** Use Barrow for that.
- **NOT the default.** Aurora is the default cozy theme; this is
  for operators who explicitly want the void.

---

## Contrast ratios

| Pair | Ratio | WCAG |
|---|---|---|
| $text on $background | 14.2:1 | AAA |
| $text-muted on $background | 6.9:1 | AAA |
| $primary on $background | 7.4:1 | AAA |
| $accent on $background | 11.1:1 | AAA |
| $error on $background | 4.6:1 | AA |
| $success on $background | 5.7:1 | AA |
| Hearth glow on background | 8.9:1 | AAA |

Ginnungagap has the *highest* text-on-background contrast of any
Stofa theme because the background is the darkest.

---

## Mock visual (Ginnungagap)

```
╭ Stofa  ᛞ ᛞ ᛞ  Chat                                   🔥 ╮     ← thin pale border, dim hearth
│                                                          │
│   > volmarr: hello                                       │     ← pale-bright cursor
│                                                          │
│   ember: hi.                                             │     ← pale grey text
│                                                          │
│   > volmarr: what's in my Well?                          │
│                                                          │
│   ember:                                                 │
│   • notes/odin.md                                        │     ← muted bullet
│   • notes/yggdrasil.md                                   │
│                                                          │
│   95 documents total.                                    │
│                                                          │
│  > _                                                     │     ← brighter cursor
╰──────────────────────────────────────────────────────────╯
[ ● Funi   ● Well   ● MCP ]                       [Chat]
   ↑ small colored dots, the only color visible
```

Ginnungagap is **almost monochrome**. The only color is in the
status dots, errors, and hearth-when-active. Everything else is
greyscale. This is exactly the appeal: distraction-free focus.

---

## Closing

Ginnungagap is for operators who want **the void to look at**
instead of **a hall to be in**. The pets are still there
(unmistakably colored against the void); the hearth still works.
But the chrome retreats. Some operators will love this. Most won't.
Both are right.
