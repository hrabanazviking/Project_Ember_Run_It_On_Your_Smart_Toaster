# 24 — Ranger and nnn

> https://ranger.github.io/ · https://github.com/jarun/nnn

Two file managers. ranger is the classic; nnn is the minimal-fast
alternative. Together they teach Stofa about **two-pane and
three-pane navigation**, **directory-as-context**, and **the
preview pane**.

---

## ranger

### What it is

Python-based vim-style file manager. Three-pane miller-columns
layout: parent directory · current directory · preview / child.

### The miller columns layout

The clever idea: **show the context, not just the cursor.**

```
┌── ../home ──────┐┌── volmarr ─────┐┌── notes ──────────────────┐
│   .ssh           ││ docs           ││ # Friday research          │
│   .config        ││ projects       ││                            │
│ ▶ volmarr        ││ ▶ notes        ││ - found a great paper      │
│   shared         ││ src            ││ - emailed Iðunn about ...   │
└──────────────────┘└────────────────┘└────────────────────────────┘
```

Left = where you came from. Middle = where you are. Right = what's
inside the focused thing.

Pressing → moves the columns left (you enter the focused dir).
Pressing ← moves them right (you go up).

### What we steal

1. **The two-pane pattern in WellScreen.** Sources on the left;
   selected-document details on the right. Same Miller-columns idea
   but only two levels (we don't have nested documents).
2. **Preview-on-focus.** Selecting a document in WellScreen
   immediately shows its details (no Enter required). Same as ranger
   focusing a file shows preview.
3. **Letter-shortcuts to common operations.** ranger's `yy` (yank),
   `dd` (cut), `pp` (paste), `gg`/`G`, etc. We follow the vim
   conventions where they map.

### What we avoid

1. **Three-column miller layout for everything.** Most Stofa screens
   are chat-first or dashboard. The Miller columns only fit
   WellScreen.
2. **The "everything is a file" mental model.** Ember's Well is
   documents-and-chunks, not files-and-directories. We use the file
   manager pattern for *navigation* but not for *data model*.

---

## nnn

### What it is

Minimal C-based file manager. <1MB binary. Extremely fast. Single-pane
view by default; can split.

Author: jarun. ~20k stars by 2026.

### The clever idea: less is more

**Single-pane view as the default**. Where ranger gives you three
columns, nnn gives you one. The result is faster, less busy, and
forces the operator to *navigate* rather than scan.

### What we steal

1. **Single-pane default for narrow terminals.** When terminal is
   < 80 cells wide, WellScreen collapses to single-pane (sources
   above, details below in a single column).
2. **Speed as a feature.** nnn's startup is <10ms. Stofa's launch
   should be <500ms to the first usable screen. The path to "ready"
   is a measurable target.

### What we avoid

1. **The "minimal at all costs" trap.** nnn's pure-stdlib look is
   striking but Spartan. Stofa is cozy; we're allowed colors and
   warmth.
2. **The plugin-via-shell-script extension model.** nnn extends
   through shell scripts; Stofa extends through Python plugins.
   Different language, different ecosystem.

---

## Combined lessons for Stofa

| Pattern | Source | Where in Stofa |
|---|---|---|
| Two-pane with preview-on-focus | ranger | WellScreen (sources + details) |
| Narrow-mode collapses to single | nnn | WellScreen responsive layout |
| Letter shortcuts (yy, dd, gg, G) | both | global navigation |
| Speed budget | nnn | < 500ms to ready (test in CI) |
| Status bar with current path | both | StatusBar always shows current screen + state |

---

## What we explicitly invent (not from either)

- **The "preview pane" isn't a file preview.** In Stofa it's a
  document's metadata + recent excerpt. We don't render the full
  document in the preview pane (the chunked text isn't useful
  in raw form).
- **No "open in editor" jump-out.** Ranger and nnn both shell-out
  to `$EDITOR` for editing. Stofa doesn't edit documents — it
  ingests them. Editing happens in the operator's own editor,
  outside Stofa.

---

## Specific Stofa borrowings

### From ranger
- The two-pane sources-then-details layout in WellScreen.
- The `/` to start a fuzzy search (within the current pane).
- The `Enter` to "drill in" / open detail view.

### From nnn
- The under-80-cells collapse to single column.
- The < 500ms startup target.
- The single-letter command set for common operations.

---

## Closing

File managers walked so AI hall managers could run. ranger gave us
the *context-as-position* pattern (where the columns mean different
things by their position). nnn gave us the *speed* and *minimalism*
discipline. Stofa applies both to a chat-first surface — not to
files, but to the operator's relationship with Ember's knowledge.
