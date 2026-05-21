# 43 — Visual Hierarchy

How to make the operator's eye go to the right place at the right
time.

---

## What hierarchy is for

A screen with no hierarchy is a wall of text. Every element looks
equally important. The operator's eye has nowhere natural to land.

A screen *with* hierarchy is a path. The eye lands on the most
important thing first, the second most important next, and so on.

Hierarchy is achieved through **five orthogonal channels**:

1. **Size** — bigger = more important.
2. **Weight** — bolder = more important.
3. **Color** — contrast vs muted = more important.
4. **Position** — top-left first, top-right second, bottom-left
   third (Western reading order).
5. **Whitespace** — surrounded by space = stands out.

In terminals, channel #1 (size) is limited (one cell per character).
Channels #2-5 do most of the work.

---

## Stofa's hierarchy rules

### Three levels of weight

We use only three weights, and one is implicit:

- **Bold** ($text-bold via font weight) — primary information,
  headlines.
- **Regular** ($text) — body content.
- **Muted** ($text-muted) — secondary information (timestamps,
  hints, disabled).

We do NOT use italic. Italic in terminal fonts is unreliable; many
fonts don't ship an italic; the ones that do are sometimes hard to
read.

### Three levels of color emphasis

- **Saturated accent** ($accent) — interactive elements (links,
  focused borders).
- **Muted accent** ($primary) — chrome (panel borders, headers).
- **Semantic colors** ($success, $warning, $error) — only on
  state-bearing elements (status dots, error messages, success
  confirmations).

Everything else is the theme's neutral $text or $text-muted.

This is restrictive. It's restrictive *on purpose*. When red appears
on screen, the operator should *know* something is wrong without
having to read.

### Position hierarchy

Stofa screens follow this scanning order:

1. **Top of chrome** — current screen name, hearth icon.
2. **Top of screen content** — the main panel title.
3. **Center of screen content** — the operator's task.
4. **Bottom of chrome (StatusBar)** — global state + key hints.
5. **Pet layer** — peripheral; ignore unless something changes.

This order is consistent across every screen. Operators learn
*where to look first* in their first session.

### Border hierarchy

We use three border states:

- **Focused border** — $accent color. Indicates "this is what your
  keys affect."
- **Unfocused border** — $primary color. Indicates "this is a panel."
- **Disabled / inactive border** — $text-disabled. Indicates "this
  exists but isn't currently relevant."

When the operator presses Tab to cycle focus, the border color
shifts and they immediately see where the focus went.

---

## Hierarchy in chat messages

The ChatScreen has the densest hierarchy demand. Multiple turns,
each with multiple parts. Hierarchy:

```
> operator: hello there         ← operator prefix in $accent
ember: hi! how can I help?       ← ember prefix in $primary
                                  ← blank line for separation
> operator: what's in my Well?    ← next operator turn
                                  ← blank line
ember: I found these documents:   ← ember reply
                                  ← horizontal rule (subtle)
   • notes/odin.md (excerpt)      ← citations in $text-muted
   • notes/yggdrasil.md (excerpt)
   ──                             ← subtle separator
   You have 95 documents in       ← Ember's reply continues
   your Well overall. The most
   relevant are above.
```

The eye order:
1. The active message (bottom-most, with cursor nearby).
2. Older messages (scrolling up).
3. Citations within a reply (subtly demarcated).

Citations are *part of* the reply but visually subordinate (lower
weight + indented). This is the right hierarchy: the reply is the
answer; citations support it.

---

## Hierarchy in HomeScreen

The 4-panel grid:

```
┌── Conversation ──────┐ ┌── Well ──────────┐
│                       │ │                   │
│  ↦ <important info>   │ │  <stats>          │
│  <hint>               │ │  <hint>           │
│                       │ │                   │
└───────────────────────┘ └───────────────────┘
┌── Realms ────────────┐ ┌── Tools ─────────┐
│                       │ │                   │
│  <statuses>           │ │  <list>           │
│                       │ │                   │
└───────────────────────┘ └───────────────────┘
```

Hierarchy within each panel:
- Border with title (primary border color).
- 1-2 lines of *current state* in bold.
- 1-2 lines of *hint* in muted.

The four panels are *equally important* on Home. They're laid out in
a grid that doesn't privilege one over the others. (The operator's
first-action choice should be theirs, not the UI's.)

---

## Hierarchy in StatusBar

The status bar has three zones, each with a hierarchy:

```
[ ✓ Funi (llama3.2:3b)  ·  ✓ Well 95 docs  ·  ✓ MCP 2/2 ]    [Chat]    [c=chat w=well ?=help q=quit]
   ↑                                                            ↑                  ↑
   left zone: realm state              center: current screen   right: key hints
```

- **Left zone**: state. Color-coded dots draw the eye to
  any "down" state.
- **Center zone**: current screen name. Bold + primary.
- **Right zone**: contextual key hints. Muted.

The operator who's looking for "is anything wrong?" looks left
first (because that's where the colored dots are). The operator who
forgot what keys to press looks right (because that's where the
hints are).

---

## Cross-screen consistency

Critically: **the hierarchy is the same on every screen**.

- Border colors: same meaning across all screens.
- Bold-vs-regular-vs-muted: same meaning across all screens.
- Semantic colors: same meaning across all screens.
- Layout order: chrome header on top, content middle, status bar
  bottom — every screen.

This is what makes the second screen the operator visits feel
familiar after the first.

---

## What we explicitly don't use for hierarchy

- **Underline.** Many terminals render underline differently
  (some don't render at all). Unreliable.
- **Blink.** Almost universally disabled. And rightly so — it's
  awful.
- **Multiple font sizes.** Terminal cells are monosize.
- **All-caps for emphasis.** All-caps is shouting. We use bold +
  position for emphasis.
- **Emoji.** Cross-platform rendering is inconsistent. We use
  Unicode glyphs in the U+2000-U+25FF range only.

---

## Specific Stofa decisions

| Element | Hierarchy choice |
|---|---|
| Operator message | $accent prefix, regular weight body |
| Ember message | $primary prefix, regular weight body |
| Citation | $text-muted, indented |
| Error message | $error, regular weight, on its own line |
| Modal title | bold, $accent |
| Focused border | $accent, round |
| Unfocused border | $primary, round |
| Panel title | bold, $primary, centered |
| Status indicator (good) | $success bullet (●) |
| Status indicator (warn) | $warning bullet (●) |
| Status indicator (error) | $error bullet (●) |
| Help hint | $text-muted |
| Hearth (idle) | $hearth-base |
| Hearth (thinking) | $hearth-glow, soft pulse |

---

## Closing

Hierarchy is *the* lever for making a complex TUI feel calm. Three
weights, three semantic colors, three border states, consistent
positions across screens. The operator's eye knows where to go
before their mind does — and that's what makes Stofa not
overwhelming, even with the dashboard + pets + multiple panels all
present at once.
