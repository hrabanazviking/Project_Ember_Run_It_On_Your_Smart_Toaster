# 21 — Lazygit

> https://github.com/jesseduffield/lazygit

The best TUI in software development history. Its lessons drive more
of Stofa's design than any other studied tool.

---

## What it is

A terminal UI for `git`. Operator runs `lazygit` in a repo; gets a
3- or 4-column layout: files, branches, log, status. Every git
operation is one or two keystrokes. Built in Go (gocui).

Author: Jesse Duffield. Started ~2018. ~50k GitHub stars by 2026.

---

## The screenshot

```
┌── Status ──┐┌── Files ─────────────────┐┌── Branches ───────┐┌── Log ────┐
│ ●          ││ M src/foo.py             ││ * main             ││ a1b2c3 fix│
│ origin/    ││ ?? notes/                ││   feat/baz         ││ d4e5f6 doc│
│ main       ││                          ││   feat/qux         ││ g7h8i9 mv │
│            ││                          ││                    ││           │
└────────────┘└──────────────────────────┘└────────────────────┘└───────────┘
[Status                              files: 1m 0??                     1/3 ↑]
```

Four columns, fixed positions, always present. The operator's eye
goes to the same place for the same information, every time.

---

## The clever idea: position is a label

Lazygit's three (or four) columns each have a *fixed meaning*:

- Leftmost = status / staging
- Middle = files (or, focused-column-dependent: stash, etc.)
- Right = branches OR log (cycles)

The operator never has to read a label to know "where is the file
list?" — it's always the second column. This makes scanning fast and
makes muscle memory possible.

The keystrokes match the columns: `1` focuses the first, `2` the
second, `3` the third, `4` the fourth. Mnemonic + spatial.

---

## What we steal

1. **Numeric column-focus shortcuts.** Press `1`/`2`/`3` to jump to
   panels (in HomeScreen + WellScreen).
2. **Title-cased column headers.** Every panel has a centered title
   in its border, matching lazygit's "──── Status ────" pattern.
3. **The keypress + arrow legend at the bottom.** Lazygit's footer
   shows the active set of keys ("c = commit, p = push, ..."). Our
   StatusBar will do the same: contextual key hints.
4. **Modal-but-visual.** Lazygit has modals (the commit message
   modal) but they're *centered overlays* with clear borders. Our
   ToolApprovalScreen mirrors this.
5. **The diff-view-on-demand pattern.** Pressing Enter on a file
   opens a diff in a panel. Our WellScreen + ChatScreen Citations
   panel follow: Enter to expand, Esc to collapse.
6. **Commit-message-style humor.** Lazygit's loading messages
   ("Hashing the porkies…") are part of its charm. We get the same
   register via the pets and the cozy hall framing — different
   delivery, same effect.

---

## What we avoid

1. **Lazygit's per-screen muscle-memory cliff.** Lazygit has
   ~80 keybindings; the operator needs hours to learn them. We cap
   at ~30 visible bindings; rest in the command palette.
2. **The "you must learn modal" hurdle.** Lazygit is modal-aware
   (some keys mean different things in different columns). We try to
   keep keys *globally* consistent: `c` means chat from anywhere.
3. **The default green-blue-yellow color scheme.** Lazygit's defaults
   are bright and noisy. Our Aurora is muted twilight.
4. **The 4-column dense layout as default.** Lazygit's 4-column view
   is exhausting for the first 10 minutes. Our HomeScreen is a
   sparser 2×2.

---

## Specific patterns to mirror in Stofa

### The status-bar key legend

Lazygit:
```
[Status        c=commit p=push   q=quit ?=help                    1/3 ↑]
```

Stofa (HomeScreen):
```
[ ✓ Funi · ✓ Well 95 docs · ✓ MCP 2/2     c=chat w=well d=doctor ?=help ]
```

Same pattern: state on the left, key hints on the right.

### The modal commit message

Lazygit pops a centered text input for commit messages. Modal but
*visible* (other panels still rendered behind). Stofa's
ToolApprovalScreen, HjartaWizardScreen, and CommandPalette follow
this — modal but transparent enough to not feel like a context
break.

### Numeric column-focus

`1`-`4` jump to columns. Our `c`/`w`/`d`/`s`/`m` jump to screens.
Different abstraction (we don't have multi-column screens; we have
multiple screens), same idea: short single-key navigation to the
named thing.

---

## The lazygit author's philosophy (as observed)

Jesse Duffield writes occasional blog posts and gives talks. Themes:

- **Reduce friction at every turn.** If the operator has to think,
  re-design.
- **The terminal is the platform.** Don't fight it; lean into it.
- **Open source is a relationship, not a transaction.** The lazygit
  community is friendly because the maintainer is.

Stofa's design philosophy ([`../vision/02_DESIGN_PHILOSOPHY.md`](../vision/02_DESIGN_PHILOSOPHY.md))
echoes these. Specifically the "coziness over capability" principle
is what lazygit's "reduce friction" looks like when applied to a
single-operator AI hall instead of a multi-developer git tool.

---

## Citations + references

- The lazygit repo (read the README and the docs).
- Jesse's talk: "How I built lazygit" — search YouTube.
- The lazygit screenshot above is composed; the real one has more
  detail but the pattern is faithful.

---

## What we explicitly did NOT take from lazygit

For the record (so future PRs know):

- We don't replicate lazygit's git-state-aware keybindings (where the
  same key means different things in different states). That trades
  consistency for compactness, and we're choosing consistency.
- We don't ship as a single static binary (we're Python + pip).
  Lazygit's distribution model isn't our model.
- We don't use lazygit's color scheme.
- We don't have its 4-column dense layout (too much for a chat-first
  surface).

But the underlying insights — position as label, modal but visual,
key-hints visible — are foundational.

---

## Closing

If we ship a Stofa V1 that an operator who knows lazygit looks at and
thinks "oh, this is from the same family of software," we've done it
right. Not a clone — a cousin.
