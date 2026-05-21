# 63 — Icon Vocabulary

Every glyph in Stofa that carries a *meaning* (beyond a letter or
border). What it means, what it falls back to, where it appears.

---

## The full list

| Glyph | Unicode | Meaning | ASCII fallback | Where used |
|---|---|---|---|---|
| 🔥 | U+1F525 | hearth (Funi-related; alive/thinking state) | `^` | chrome header (top-right) |
| ● | U+25CF | status dot (color-coded) | `*` | StatusBar, MCPScreen, DoctorScreen |
| ○ | U+25CB | empty / not-yet-probed | `o` | DoctorScreen (uninitialized) |
| ◐ | U+25D0 | half / transitional | `c` | (rare, V2-ish) |
| ✓ | U+2713 | ok / success | `+` | DoctorScreen, settings toggles, lists |
| ✗ | U+2717 | failed / no | `x` | DoctorScreen (down state), tool denied |
| ▶ | U+25B6 | focus pointer / current item | `>` | command palette, lists |
| ▾ | U+25BE | expanded section | `v` | Settings collapsibles, dropdowns |
| ▸ | U+25B8 | collapsed section | `>` | Settings collapsibles |
| ▷ | U+25B7 | (NOT USED — reserved) | — | — |
| • | U+2022 | bullet | `*` | lists (chat replies, citations) |
| → | U+2192 | path arrow / next | `->` | breadcrumbs, multi-step flows |
| ← | U+2190 | back arrow | `<-` | rarely (mostly Esc carries this meaning) |
| ↑ | U+2191 | up (in help overlay) | `^` | key hints |
| ↓ | U+2193 | down (in help overlay) | `v` | key hints |
| ↩ | U+21A9 | Enter / return | `<-` | key hints |
| ⏎ | U+23CE | Enter / submit | `<-` | input bars |
| ⠋ | U+2807 | spinner frame 1 | `|` | loading |
| ⠙ | U+2819 | spinner frame 2 | `/` | loading |
| ⠹ | U+2839 | spinner frame 3 | `-` | loading |
| ⠸ | U+2838 | spinner frame 4 | `\` | loading |
| ⠼ | U+283C | spinner frame 5 | `|` | loading |
| ⠴ | U+2834 | spinner frame 6 | `/` | loading |
| ⠦ | U+2826 | spinner frame 7 | `-` | loading |
| ⠧ | U+2827 | spinner frame 8 | `\` | loading |
| ⠇ | U+2807 | spinner frame 9 | `|` | loading |
| ⠏ | U+280F | spinner frame 10 | `/` | loading |
| ─ | U+2500 | horizontal line | `-` | borders, separators |
| │ | U+2502 | vertical line | `\|` | borders |
| ╭ ╮ ╰ ╯ | various | rounded corners | `+` | borders |
| ▁-█ | U+2581-U+2588 | block fractions | various ASCII | progress bars |
| … | U+2026 | truncation | `...` | long text |
| — | U+2014 | em-dash | `--` | prose, chrome |
| ᛞ | U+16DE | runic ornament | `*` | chrome separator |
| ᛟ | U+16DF | runic ornament | `*` | Hjarta wizard title |
| ᛏ | U+16CF | runic ornament (pet bark) | `+` | Ask-sapling sprite |

Roughly 35 glyphs total, including the box-drawing set. Memorized
once; consistent forever.

---

## How operators learn the icons

We don't quiz them. The icons are *contextual* — each appears in a
place where its meaning is unambiguous:

- `🔥` is in the corner; operators figure out "that's the activity
  indicator" by watching it pulse when Funi works.
- `●` next to "Funi" with green color is obviously "Funi is up."
- `✓` next to a checkbox is obvious.
- `▾` / `▸` next to a section header is obvious.

The `?` overlay (per [`../screens/88_HELP_OVERLAY.md`](../screens/88_HELP_OVERLAY.md))
includes a small **legend** section that catalogs the icons + their
meanings, for operators who want explicit reference.

---

## The spinner

The braille-pattern spinner (`⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`) cycles at ~1.5 Hz.
Total cycle: ~6.5 seconds. Frames are positioned in a clockwise
rotation, which gives the visual impression of spinning.

ASCII fallback uses `|/-\` cycling. Less smooth but recognizably a
spinner.

The spinner appears:
- Next to "asking Funi" during an in-progress request.
- Next to "ingesting" during long ingest operations.
- Next to "ping" during MCP server ping.

Never as decoration. Never always-on.

---

## What icons we DON'T use

The list of "could but won't":

- **Folder icons** (`📁`, `📂`) — emoji rendering varies; we use
  text labels instead.
- **File icons** — same reason.
- **Star icons in V1** (`★`, `☆`) — reserved for V2 "favorites."
- **Heart icons** — too saccharine; doesn't fit Norse register.
- **Lightning** — corporate; doesn't fit.
- **Trash can** — varies in rendering; we use the word "Delete".
- **Settings gear** — varies; we use the word "Settings".
- **Nerd-font icons** — require Nerd Font installation; we don't.

---

## Closing

35 glyphs. Each with a single, contextual meaning. ASCII fallback
for every one. Legend in the help overlay. Operators don't have to
memorize; they pick up the meanings from context. The discipline is
what keeps Stofa from feeling like an emoji explosion.
