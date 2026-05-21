# 45 — Typography for Monospace

The operator's terminal font is *their* font, not ours. But the
choices we make in *how we use it* matter.

---

## What we can and can't control

| Aspect | Who controls it |
|---|---|
| Font family | operator (their terminal) |
| Font size | operator |
| Font weight (regular/bold) | operator's font; we request via styling |
| Italic support | operator's font (often missing) |
| Cell width | terminal (monospace, ~half of cell height) |
| Cell height | terminal |
| Line spacing | terminal |
| Glyph coverage | operator's font (Unicode subsets vary) |

What we *can* control:

- Which characters we emit (Unicode-aware).
- Whether we ask for bold (we do, sparingly).
- Whether we ask for italic (we don't).
- The whitespace structure of our output.
- The visual rhythm via line breaks and padding.

---

## The Unicode subset we use

Stofa uses Unicode characters from these blocks. Anything outside
this list gets ASCII-fallback treatment.

### Required (we assume any modern font has these)

- **Basic Latin (U+0000-U+007F)** — ASCII, the foundation.
- **Box Drawing (U+2500-U+257F)** — for borders. Specifically:
  - `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼` (light box)
  - `╭ ╮ ╯ ╰` (rounded corners) — preferred
  - `═ ║ ╔ ╗ ╚ ╝` (double — used sparingly)
- **Block Elements (U+2580-U+259F)** — for progress bars:
  - `▁ ▂ ▃ ▄ ▅ ▆ ▇ █` (smooth vertical fill)

### Recommended (most fonts have these)

- **Geometric Shapes (U+25A0-U+25FF)** — bullets, dots:
  - `● ○ ◉ ◎` (status dots)
  - `▶ ◀ ▲ ▼` (focus arrows, used sparingly)
- **General Punctuation (U+2000-U+206F)**:
  - `… † ‡ • ※` (decorative)

### Optional (some fonts may not have)

- **Miscellaneous Symbols (U+2600-U+26FF)**:
  - `🔥` — the hearth icon (with ASCII fallback `^`)
  - `★ ☆` (stars; used sparingly in command palette)
- **Dingbats (U+2700-U+27BF)** — used very sparingly.

### Pet sprites use Block Elements + Geometric Shapes

Each pet sprite is a small composition of box-drawing, geometric
shapes, and ASCII. See [`../pets/73_PETS_SPRITE_GUIDE.md`](../pets/73_PETS_SPRITE_GUIDE.md)
for the full character vocabulary per pet.

---

## ASCII fallback

The operator can set `stofa.ascii_only: true` (or auto-detect from
`LANG=C` / no-Unicode terminal). In ASCII mode:

- Box drawing degrades:
  - `╭─╮` → `+-+`
  - `│ │` → `| |`
  - `╰─╯` → `+-+`
- Progress bars:
  - `▁▂▃▄▅▆▇█` → `....::|##` (8-step ASCII gradient)
- Status dots:
  - `●` → `*`
  - `○` → `o`
- Pets:
  - All sprites have ASCII variants (per the sprite guide).

The semantic content of Stofa is preserved in ASCII; only the
prettiness degrades.

---

## Weight: bold sparingly

We use **bold for emphasis only**. Bold appears in:

- Panel titles (`Conversation`, `Well`, etc.).
- The current screen name in the chrome header.
- Operator/Ember prefixes in chat messages.
- Modal titles.
- Key names in `?` overlay (`<b>c</b>` then "= chat").

We do NOT use bold for:

- Body text. Bold body is tiring.
- Status indicators. Color does that work.
- Generic emphasis ("important note!"). We use structural
  emphasis instead (a callout block).

---

## No italic

Italic in monospace fonts:

- Some terminals don't render it (renders as regular).
- Some fonts don't ship italics (renders as fallback, possibly
  jarring).
- Cursive characters interrupt the regular cell rhythm.

We don't depend on italic anywhere. If we ever want to imply
italic intent (e.g., a quote inside a Funi reply), we use other
markers (indent, quote character, color shift).

---

## Visual rhythm

Monospace prose is read more slowly than proportional prose. Our
counterweight:

- **Generous line spacing.** One blank line between conversation
  turns. One blank line above and below headings.
- **Right-margin discipline.** Long lines are hard to scan; we wrap
  at ~80 cells in body text. Code blocks can be wider (operator
  expects that).
- **Indent for hierarchy.** Citations indented from the reply.
  Bullet list items indented from the lead-in line.
- **No mid-line wrap surprises.** When we wrap, we wrap at word
  boundaries and align the continuation with the start of the
  original.

---

## Specific character choices

| Use | Character | Fallback |
|---|---|---|
| Bullet | `•` | `*` |
| Section separator | `───` | `---` |
| Path arrow | `→` | `->` |
| Truncation marker | `…` | `...` |
| Hearth icon | `🔥` or `❖` | `^` |
| Status dot (good) | `●` | `*` |
| Status dot (warn) | `●` (color carries semantics) | `*` |
| Status dot (error) | `●` (color carries semantics) | `*` |
| Focus arrow | `▶` | `>` |
| Empty checkbox | `☐` | `[ ]` |
| Checked checkbox | `☑` | `[x]` |
| Expanded section | `▾` | `v` |
| Collapsed section | `▸` | `>` |

These are catalogued in `src/ember/stofa/utils/ascii_fallback.py` for
automated degradation.

---

## Specifics about emoji

Some Stofa designs lean on emoji (the hearth `🔥`). We're cautious:

- Emoji rendering is **most variable** across terminals — some show
  monochrome glyphs, some color, some none, some show "tofu"
  rectangles.
- We use exactly **one** emoji glyph: the hearth.
- Even that has an ASCII fallback (`^`).
- Pet sprites are built from box-drawing characters, NOT emoji
  animals.

This is the boring, conservative choice. We accept it for
robustness.

---

## What we don't do

- **Font requirements like a Nerd Font.** Nerd Fonts are great but
  not universal. We don't require glyphs like `` (Powerline arrow)
  or `` (folder icon). We use generic Unicode.
- **Ligatures.** Some fonts ligate `->` to `→`. We don't depend on
  this. (If the operator's font does, great; if not, the original
  characters are still readable.)
- **Variable-width characters.** Everything is monospace. Tables
  align via padding, not via column widths.

---

## Closing

Typography in a TUI is the *care* taken with characters, whitespace,
and Unicode subsets. Bold sparingly. Italic not at all. Box-drawing
for chrome. Block elements for bars. Generous spacing. ASCII fallback
ready. The operator's terminal font does the actual rendering; our
job is to use *which* characters they have, in *what* arrangement,
with *what* breathing room.
