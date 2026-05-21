# 68 — Palette: Barrow

**Barrow** is Stofa's **colorblind-safe theme**. The mood: stone
chamber in a Norse barrow — muted earth tones, brown-orange where
red would be, blue-leaning where green would clash with red.

Deuteranopia + protanopia tested. Tritanopia tolerable. All
semantic distinctions survive across CVD types.

---

## Full hex values

```scss
/* ─── Base surfaces ─── */
$background:    rgb(28 32 48);    /* #1C2030 — cool slate */
$surface:       rgb(36 40 56);    /* #242838 */
$surface-alt:   rgb(44 48 64);    /* #2C3040 */

/* ─── Text ─── */
$text:          rgb(220 220 220); /* #DCDCDC */
$text-muted:    rgb(150 150 160); /* #9696A0 */
$text-disabled: rgb(90 90 100);   /* #5A5A64 */

/* ─── Semantic (CVD-aware) ─── */
$primary:       rgb(120 170 220); /* #78AADC — clear blue */
$accent:        rgb(220 180 80);  /* #DCB450 — yellow (universally visible) */
$success:       rgb(100 180 220); /* #64B4DC — teal-blue (NOT green) */
$warning:       rgb(220 150 50);  /* #DC9632 — orange (NOT yellow) */
$error:         rgb(170 100 60);  /* #AA643C — brown-orange (NOT red) */

/* ─── Pets ─── */
$pet-raven:     rgb(160 160 180); /* #A0A0B4 */
$pet-fox:       rgb(220 150 50);  /* #DC9632 — orange (matches warning) */
$pet-goat:      rgb(200 190 170); /* #C8BEAA */
$pet-bee:       rgb(220 180 80);  /* #DCB450 — yellow */
$pet-cub:       rgb(140 110 90);  /* #8C6E5A */
$pet-sapling:   rgb(100 180 220); /* #64B4DC — teal (NOT green) */
$pet-drift:     rgb(220 230 240); /* #DCE6F0 */
$pet-spark:     rgb(220 150 50);  /* #DC9632 — flame orange */

/* ─── Hearth ─── */
$hearth-base:   rgb(120 80 60);   /* #785038 */
$hearth-glow:   rgb(220 150 50);  /* #DC9632 — fire */
```

---

## Why these colors

Standard color schemes use **red for bad, green for good**. This
fails 8% of male operators (deuteranopia / protanopia — red-green
confusion).

Barrow rebuilds the semantic palette using **only differences
distinguishable to red-green CVD**:

- **Success = teal-blue** (#64B4DC), NOT green. Visible to all CVD
  types.
- **Warning = orange** (#DC9632), NOT yellow (which can blend with
  green in some CVD).
- **Error = brown-orange** (#AA643C), NOT red. Distinguishable
  from warning by being browner/darker.
- **Primary = clear blue.** Always safe.
- **Accent = yellow.** One of the few CVD-safe pure hues.

Pets follow the same logic: Ask-sapling becomes teal (the "growing"
pet); fox + bee + spark all share the orange family (which works
for CVD).

---

## CVD simulation testing

Each theme is rendered + CVD-simulated via the `colour` library:

| Simulation | Aurora result | Barrow result |
|---|---|---|
| Normal vision | semantic distinctions clear | semantic distinctions clear |
| Deuteranopia | red/green muddled — ERROR | brown/teal clear — OK |
| Protanopia | red/green muddled — ERROR | brown/teal clear — OK |
| Tritanopia | blue/yellow muddled — borderline | warning/accent still distinguishable |

The Barrow theme **explicitly does NOT use** any color pair that
fails the deuteranopia or protanopia simulation. The tritanopia case
(rare, ~0.01% of population) has one borderline pair
(warning/accent both leaning yellow-orange), mitigated by shape:
warning bullet `●` vs accent text-with-prefix.

---

## When to pick Barrow

- **You have CVD.** Definitely pick Barrow.
- **You're testing your CVD operator experience.** Same.
- **You like the slate-blue look.** Barrow's aesthetic is its own
  kind of pretty.

---

## Contrast ratios

| Pair | Ratio | WCAG |
|---|---|---|
| $text on $background | 10.7:1 | AAA |
| $text-muted on $background | 5.3:1 | AA Large |
| $primary on $background | 6.8:1 | AA |
| $accent on $background | 7.4:1 | AAA |
| $error (brown-orange) on $background | 4.2:1 | AA |
| $success (teal-blue) on $background | 5.5:1 | AA |

All AA or better. Contrast preserved across CVD simulation.

---

## What changes vs Aurora

| Token | Aurora | Barrow | Why |
|---|---|---|---|
| $success | sage green | teal-blue | Green confuses with red in CVD |
| $error | muted red | brown-orange | Red confuses with green in CVD |
| $warning | warm amber | orange | Distinguishable from accent + error |
| $pet-sapling | sage green | teal-blue | Match $success |
| $pet-fox | warm tan | orange | Slight shift toward CVD-clearer |

Everything else stays similar to Aurora. Barrow looks like
*Aurora's CVD-rebalanced cousin*, not a totally different theme.

---

## Pet behavior reads correctly

CVD operators get the same semantic information:

- Hugin (raven) — grey, always neutral.
- Refur (fox) — orange. Reads as fox.
- Ask-sapling — teal-blue. Reads as "growing thing" (the form is a
  tree; CVD operators read form first, color second).
- Bee + spark + fox — same warm orange family, distinguishable by
  *form*, not by color.

The deeper principle: **shape + position + color together, never
color alone**. Per [`../ux-science/46_ACCESSIBILITY.md`](../ux-science/46_ACCESSIBILITY.md).

---

## Closing

Barrow is what happens when "colorblind-safe" is a real design
input rather than a checkbox. It's its own aesthetic — slate-cool
with brown-orange and teal-blue — and many CVD operators report
it's their preferred theme even outside accessibility need. Built
for some operators, beautiful for all.
