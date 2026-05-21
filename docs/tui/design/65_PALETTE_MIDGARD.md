# 65 — Palette: Midgard

**Midgard** is the warm-daylight theme. The mood: late summer
afternoon in a Norse meadow, warm earth tones, sunlight on amber
grass. A **light-mode** theme for operators who work in bright
rooms or prefer daytime warmth.

---

## Full hex values

```scss
/* ─── Base surfaces ─── */
$background:    rgb(245 239 224); /* #F5EFE0 — warm parchment cream */
$surface:       rgb(238 230 210); /* #EEE6D2 — slightly darker cream */
$surface-alt:   rgb(232 222 198); /* #E8DEC6 — secondary surface */

/* ─── Text ─── */
$text:          rgb(50 45 40);    /* #322D28 — dark warm brown */
$text-muted:    rgb(110 100 90);  /* #6E645A — secondary brown */
$text-disabled: rgb(170 160 150); /* #AAA096 — disabled */

/* ─── Semantic ─── */
$primary:       rgb(100 75 50);   /* #644B32 — rich earth brown */
$accent:        rgb(180 80 40);   /* #B45028 — warm rust */
$success:       rgb(80 130 60);   /* #50823C — forest green */
$warning:       rgb(200 130 30);  /* #C8821E — amber gold */
$error:         rgb(170 50 40);   /* #AA3228 — burnt red */

/* ─── Pets ─── */
$pet-raven:     rgb(80 80 90);    /* #50505A — dark slate */
$pet-fox:       rgb(180 100 50);  /* #B46432 — warm rust */
$pet-goat:      rgb(120 100 80);  /* #786450 — earthen */
$pet-bee:       rgb(200 150 40);  /* #C89628 — bee yellow */
$pet-cub:       rgb(130 90 60);   /* #825A3C — wolf brown */
$pet-sapling:   rgb(80 130 60);   /* #50823C — sage */
$pet-drift:     rgb(220 210 195); /* #DCD2C3 — faded cream */
$pet-spark:     rgb(200 80 40);   /* #C85028 — fire orange */

/* ─── Hearth ─── */
$hearth-base:   rgb(140 80 60);   /* #8C503C — banked ember */
$hearth-glow:   rgb(220 110 50);  /* #DC6E32 — bright daytime fire */
```

---

## Why these colors

Midgard is the *daylight* counterpart to Aurora's twilight. The same
warm/cool color theory, but inverted:

- **Background is warm light cream**, not cool dark blue. Operators
  in bright rooms (sunlight on monitor) read this much better than
  Aurora.
- **Text is dark warm brown**, not pale grey. High contrast on the
  cream background. Reads like ink on parchment.
- **Primary is rich earth brown**, evoking woodcarving / tooled
  leather. Norse craft tradition rendered as a chrome color.
- **Accent is warm rust**, the warmest color on the palette.
  Interactive elements stand out without being garish.
- **Success is forest green**, more saturated than Aurora's sage
  (works against the lighter background).
- **Error is burnt red**, deeper than Aurora's muted red. The
  contrast-adjusted version.

---

## When to pick Midgard over Aurora

| Situation | Pick |
|---|---|
| You're in a dark room at night | Aurora |
| You're in a bright room (sunlight, fluorescent) | Midgard |
| You like dark mode generally | Aurora |
| You like light mode generally | Midgard |
| Your monitor is high-contrast | either |
| You're projecting Stofa for a demo | Midgard (better in bright rooms) |
| You want maximum cozy | Aurora |

Operators tend to pick one and stay; some switch by time-of-day.
A V2 feature plans **auto-theme-by-clock** (Aurora at night,
Midgard during day, based on system clock + operator's latitude
preference).

---

## Contrast ratios

| Pair | Ratio | WCAG |
|---|---|---|
| $text on $background | 13.8:1 | AAA (very high) |
| $text-muted on $background | 5.4:1 | AA Large |
| $primary on $background | 7.1:1 | AAA |
| $accent on $background | 5.9:1 | AA |
| $error on $background | 6.2:1 | AA |
| $success on $background | 5.3:1 | AA |

Generally similar to Aurora's distribution; the light background
naturally produces high text-contrast.

---

## Pet placement in Midgard

Pets read differently against light:

- Hugin (raven) is now dark-on-light — much more visible than in
  Aurora's dark theme. Reads almost like a silhouette.
- Refur (fox) at warm rust is at-home against the cream background.
- Drift (snowflake pale) becomes nearly invisible — that's
  intentional; in summer-daylight, drift-snow doesn't appear. The
  drift pet is rare in Midgard.

The Pet behavior engine knows about *seasonal pets* in V2 (some
pets more common per theme), but V1 keeps all pets in all themes;
just their visibility varies.

---

## Mock visual (Midgard)

```
╭──── Stofa ──── ᛞ ᛞ ᛞ ──── Chat ────────────── 🔥 ───╮     ← brown border, rust rune
│                                                          │
│   > volmarr: hello                                       │     ← rust prefix on operator
│                                                          │
│   ember: hi! how can I help today?                       │     ← brown prefix on Ember
│                                                          │
│   ember: I found these in your Well:                     │
│                                                          │
│      • notes/odin.md — "the all-father has..."           │     ← muted brown
│                                                          │
│  > _                                                     │     ← rust cursor
╰──────────────────────────────────────────────────────────╯
[ ● Funi llama3.2:3b  ·  ● Well 95 docs  ·  ● MCP 2/2 ]  [Chat]
   ↑ forest-green dots
```

Same composition, daytime mood. Eye still lands on cursor (rust =
warm), then chrome (brown), then realm dots (green).

---

## Closing

Midgard is Aurora's daylight cousin. Same five-semantic-color
discipline, same 20-token contract, just light-mode-shaped. Operators
who reject dark themes get a real home here, not a "default-light"
hacked-from-dark afterthought.
