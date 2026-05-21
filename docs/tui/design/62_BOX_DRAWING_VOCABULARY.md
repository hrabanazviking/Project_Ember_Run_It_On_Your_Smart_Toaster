# 62 — Box-Drawing Vocabulary

The exact set of Unicode box-drawing characters Stofa uses, where,
and what they mean.

---

## The principle: one vocabulary, consistently

Every Stofa border uses the same characters. The operator never sees
mixed styles within one screen — that visual jitter exhausts the
eye over hours of use.

Our vocabulary: **light rounded box-drawing**, U+2500 block.

---

## The base characters

| Character | Code | Purpose |
|---|---|---|
| ─ | U+2500 | horizontal line |
| │ | U+2502 | vertical line |
| ╭ | U+256D | top-left rounded corner |
| ╮ | U+256E | top-right rounded corner |
| ╰ | U+2570 | bottom-left rounded corner |
| ╯ | U+256F | bottom-right rounded corner |
| ├ | U+251C | tee right |
| ┤ | U+2524 | tee left |
| ┬ | U+252C | tee down |
| ┴ | U+2534 | tee up |
| ┼ | U+253C | cross |

11 characters. That's the entire vocabulary for borders.

---

## What box characters we DON'T use

- **Sharp corners** (`┌ ┐ └ ┘`). Rounded reads more modern; we pick
  one style and stick.
- **Double-line characters** (`═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬`). Heavier;
  visually competes with content. V1 doesn't use them.
- **Heavy box** (`━ ┃ ┏ ┓ ┗ ┛`). Thick lines fight against the
  considered restrained look.
- **Block characters in chrome** (`▓ ▒ ░ █`). These are for progress
  bars and pet sprites, not borders.

We could revisit these decisions in V2 if a specific need emerges
(e.g., double-line for selected panel borders). V1 keeps it simple.

---

## How borders compose

A standard Stofa panel border:

```
╭───── Title ─────╮
│                  │
│   content here   │
│                  │
╰──────────────────╯
```

- Top: rounded corners + horizontal + centered title.
- Sides: vertical line.
- Bottom: rounded corners + horizontal.

The title goes in the top border, with one space of padding on
each side. If the panel has no title, the top is solid `─`.

---

## Title placement

```
╭───── Conversation ─────╮       ← centered, single-line
╭─ tools ────────────────╮       ← left-aligned with indent
```

Stofa uses **left-aligned-with-1-cell-indent** for screen-name
titles in panel borders, and **centered** for status-bar-aggregate
titles.

Examples:

- `╭───── Conversation ─────╮` — centered (HomeScreen panel)
- `╭─ ChatScreen ───────────╮` — left-aligned (chrome header)

We don't have a hard rule; the choice is per-screen per visual
balance. The Architect's call.

---

## Border state visual differences

Borders communicate state via *color*, not *line style*:

| State | Color | Line style |
|---|---|---|
| Focused | $accent | round |
| Unfocused | $primary | round |
| Disabled | $text-disabled | round |
| Error indication | $error | round (NOT thicker) |

The operator's eye picks up "this is the focused panel" by the warm
amber border color, not by a heavier line.

This means: a panel never *visually* changes its character shape;
only its color. Consistent silhouette, varying tint.

---

## Internal dividers

Within a panel, we use lighter divisions:

```
╭───── Settings ─────────╮
│  Identity              │
│  ─────────────────────  │
│  Funi                  │
│  ─────────────────────  │
│  Brunnr                │
╰─────────────────────────╯
```

A single horizontal `───────` between sections. Same color as the
border ($primary). One blank line above and below to separate it
from the section content.

For inline separators within a content line: a single ` │ ` (pipe
with spaces) between items.

For headers within a section: `── Heading ──` (centered, single
line).

---

## ASCII fallback

When the operator's terminal can't render rounded box-drawing, we
degrade to:

| Character | ASCII fallback |
|---|---|
| ─ | `-` |
| │ | `\|` |
| ╭ | `+` |
| ╮ | `+` |
| ╰ | `+` |
| ╯ | `+` |
| ├ | `+` |
| ┤ | `+` |
| ┬ | `+` |
| ┴ | `+` |
| ┼ | `+` |

The result:

```
+----- Title -----+
|                  |
|   content here   |
|                  |
+------------------+
```

Less elegant but fully functional. Per the Vow of the Unbroken Whole.

---

## Block characters for progress bars

Progress bars use **block elements**, not box-drawing:

| Character | Code | Purpose |
|---|---|---|
| ▁ | U+2581 | 1/8 block |
| ▂ | U+2582 | 2/8 |
| ▃ | U+2583 | 3/8 |
| ▄ | U+2584 | 4/8 |
| ▅ | U+2585 | 5/8 |
| ▆ | U+2586 | 6/8 |
| ▇ | U+2587 | 7/8 |
| █ | U+2588 | full |

Used for ingest progress:

```
ingest: ████████████▆_____________  43%
```

12 full blocks + 1 partial (▆ for the 0.43 fractional). Empty cells
are spaces (not `─`) so the bar reads as a single visual element.

ASCII fallback:
```
ingest: ############|--------------  43%
```

`#` for full, `|` for half-mark, `-` for empty.

---

## Block characters in pet sprites

Pet sprites use block elements for body shapes. See
[`../pets/73_PETS_SPRITE_GUIDE.md`](../pets/73_PETS_SPRITE_GUIDE.md)
for the per-pet character vocabulary.

---

## Status dots

The semantic status indicators use **geometric shapes**, not box-
drawing:

| Character | Code | Status |
|---|---|---|
| ● | U+25CF | full / on |
| ◉ | U+25C9 | filled-ring (V2 maybe) |
| ○ | U+25CB | empty / off |
| ◐ | U+25D0 | half-on (transitional) |

ASCII fallback:
| ● | `*` |
| ○ | `o` |
| ◐ | `c` |

These are colored ($success / $warning / $error) AND positioned
consistently. The shape + color + position together encode the
state.

---

## Special characters used elsewhere

| Character | Use |
|---|---|
| ` ` | regular space (always) |
| ` ` | non-breaking space (only inside command-palette items where line-break would be wrong) |
| `…` | truncation marker |
| `—` | em-dash (used in chrome and prose) |
| `▸` | collapsed section indicator |
| `▾` | expanded section indicator |
| `▶` | focus / current-item pointer |
| `←` `→` `↑` `↓` | arrows (in help overlay key listings) |
| `•` | bullet for list items |

These are used sparingly, each with a fixed meaning.

---

## What we never use

- **Multiple bullet styles** in the same context. One bullet
  character; one meaning.
- **Stars `★`** in V1 (V2 reserved for "starred" / favorites).
- **Diamond `◆`** anywhere.
- **Triangle as bullet `▷`** anywhere.
- **Custom-font glyphs** (Nerd Font icons). Operator may not have
  the font.

---

## Closing

11 box-drawing characters. 8 block elements. 3 status dots. 7
special characters. About 30 total Unicode glyphs that make up the
entire visual surface of Stofa, plus the operator's text plus
the pet sprites. That's a *small* vocabulary applied with
discipline — which is what produces a coherent visual identity.
