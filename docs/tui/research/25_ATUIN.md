# 25 — Atuin

> https://atuin.sh/

A shell-history-as-TUI tool. Replaces your shell's `Ctrl-R` with a
beautiful fuzzy-search interface, with sync, sessions, and stats.

Teaches Stofa about **search-as-primary-interface**, **secondary
chrome**, and **respecting an existing workflow**.

---

## What it is

A Rust binary that hooks into bash/zsh/fish. When you press `Ctrl-R`,
instead of the default minimal history search, atuin opens a TUI:

```
┌─ atuin ─────────────────────────────────────────────────────┐
│ 2026-05-21 14:32  ~/projects/ember  ✓  pytest -q             │
│ 2026-05-21 14:31  ~/projects/ember  ✓  git diff --stat       │
│ 2026-05-21 14:30  ~/projects/ember  ✓  git status            │
│ 2026-05-20 16:08  ~/notes           ✓  ember well ingest .   │
│ 2026-05-20 16:00  ~/projects/ember  ✓  ember chat            │
│                                                              │
│ {fuzzy filter input}                                         │
└──────────────────────────────────────────────────────────────┘
        12,453 commands · 23 sessions · 5 directories
```

The operator types to filter; arrows to navigate; Enter to run.

---

## The clever idea: respect the existing keybinding

`Ctrl-R` is a 40-year-old bash convention. Atuin doesn't try to make
the operator press a new key. It hooks into the existing motion the
operator already has muscle memory for, and replaces what they see
when they do it.

The result: zero adoption friction. Operators install atuin and
suddenly their `Ctrl-R` is good.

This is a powerful lesson: **the best new TUI is the one that
slots into a habit, not the one that demands a new one.**

---

## What we steal

1. **Fuzzy filter as primary input.** Stofa's command palette
   (`:` / `Ctrl-P`) is atuin-shaped: an input field at the bottom,
   results above, narrowing as you type.
2. **Result rows with structured fields.** Atuin shows timestamp,
   directory, status, command. The columns are aligned. Stofa's
   command palette + WellScreen sources panel both follow the
   structured-row pattern.
3. **The bottom-of-pane stats line.** "12,453 commands · 23 sessions"
   — a quiet aggregate. Stofa's WellScreen header has the same:
   "95 documents · 35,000 chunks · 240MB".
4. **Themeable.** Atuin ships themes; Stofa ships themes too.

### What we avoid

1. **The sync server.** Atuin offers cloud sync of your shell
   history. Stofa is sovereign-by-default; no cloud sync.
2. **The "we're better than your shell" pitch.** Atuin can come
   across as "your shell is bad and we're better." Stofa is
   careful never to imply `ember chat` was bad — Stofa is *more*,
   not *better*.

---

## Specific Stofa borrowings

### The fuzzy filter UI

Atuin's input field is a single line at the bottom of the pane.
Operator types; results above narrow. Cursor stays in the input.

Stofa's command palette (`:` / `Ctrl-P`):

```
┌─ Command ─────────────────────────────────────────────────┐
│   :theme aurora                                            │
│   :theme midgard                                           │
│   :theme ginnungagap                                       │
│                                                            │
│ > the_                                                     │
└────────────────────────────────────────────────────────────┘
```

Same shape. Same flow. Operator can Enter to execute, Esc to cancel.

### Result rows with timestamps

Atuin shows when each command was run. Stofa's MCPScreen shows when
each server was last reachable:

```
filesystem    ✓  last ping 2s ago    12 tools
github        ✗  last ping 5m ago    0 tools (disconnected)
```

Same pattern: structured columns + recency.

### Aggregate stats at the bottom

Atuin's footer: "12,453 commands · 23 sessions · 5 directories".
Stofa's WellScreen header: "95 docs · 35,000 chunks · 240MB".

Both give the operator a sense of *scale* without requiring
navigation.

---

## What atuin doesn't have that we need

- Atuin is *single-screen* — it has one job. Stofa is
  multi-screen — chat + well + doctor + etc. We need cross-screen
  navigation, which atuin doesn't have to think about.
- Atuin doesn't have pets. (And shouldn't. Shell history doesn't
  warrant a fox.)

---

## The "respect the habit" lesson

The deepest atuin lesson is: **don't fight the user's existing
muscle memory.**

For Stofa, this means:

- `Esc` always cancels — every operator knows this.
- `Ctrl-C` always exits — universal.
- Arrow keys navigate where they ought to.
- `Tab` cycles focus where it ought to.
- `Enter` activates / submits.

We do not invent new keys for actions that already have a
universally-known key.

---

## Closing

Atuin teaches that great TUIs don't demand attention; they slot in
where attention already is. Stofa's command palette opens at `:`
because vim users know `:`; at `Ctrl-P` because VS Code users know
`Ctrl-P`; not at `Alt-Stofa-K` because no one knows that.

Respect the habit; you respect the operator.
