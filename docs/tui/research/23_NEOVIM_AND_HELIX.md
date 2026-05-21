# 23 — Neovim and Helix

> https://neovim.io/ · https://helix-editor.com/

Two modal editors. Neovim is the classic-with-decades; Helix is the
clean-slate-2020s. Together they teach Stofa about **modal interaction**,
**keymap discoverability**, and **the cost-curve of learning a tool**.

---

## Neovim

### What it is

The fork-of-Vim that became the de facto standard for modal-editor
operators. Async, Lua-extensible, embedded in many newer TUIs as a
component. Maintained by a community of >800.

### The modal-editing pattern

In Neovim, the same key means different things in different modes:

- `i` in normal mode → enter insert mode.
- `i` in insert mode → type the letter "i".
- `i` in visual mode → "inside" (textobject operator).

This is *brutally powerful* — most actions are 2-3 keystrokes — but
the learning curve is famously steep. New operators report 6+
months to fluency.

### What we steal

1. **The motion vocabulary.** `j` = down, `k` = up, `h` = left,
   `l` = right. `gg` = top, `G` = bottom. These are *universal* in
   the TUI world among power-users; we bind them as defaults
   alongside arrow keys.
2. **The `:` command line.** Neovim's `:` opens a command mode where
   any named action can be typed. Stofa's `:` opens the same — fuzzy
   command palette for any named action.
3. **`?` for help search.** In Neovim, `:help` opens help; the
   `K` key opens help for the word under cursor. Stofa's `?` is
   the same idea, scoped per-screen.
4. **`Esc` to exit.** Esc cancels modes, modals, focus changes.
   Universal. We follow.

### What we avoid

1. **Per-context redefinition of keys.** In Neovim, `i` means
   different things in different modes. Stofa keeps `c` meaning
   "go to chat" *everywhere* — global keys are global.
2. **The "must memorize 50 keys to be productive" curve.** New
   operators in Stofa are productive with ~5 keys (`c`/`w`/`d`/`?`/`q`).
3. **Hidden global state.** Neovim has registers, marks, jump list,
   change list — all invisible to the novice. Stofa exposes its
   state in the status bar and Doctor screen.

---

## Helix

### What it is

A modal editor that fixed Neovim's primary UX wart: the
**verb-then-object** order. In Neovim, you type `d` (delete) and then
`w` (word) and you've deleted a word — but you don't *see* what's
selected. Helix flips it: select first, then act. The selection is
visible at all times.

Author: Blaž Hrastnik. Started 2021. ~30k stars by 2026.

### The clever idea

**Pre-selection over post-selection.** The operator's cursor is
always a selection; commands operate on the current selection;
operators *see what they're about to do* before they do it.

This makes modal editing **discoverable**. You can experiment
without losing data — the worst case is you select wrong and try
again.

### What we steal

1. **Visible selection.** Stofa's focused widget is always
   visually distinct ($accent border instead of $primary). The
   operator sees what they're about to act on.
2. **The "select then act" mental model in lists.** In WellScreen
   the operator navigates with j/k, selecting a document, then
   presses an action key (`i` to ingest, `r` to re-ingest, `Delete`
   to delete). They see what they've selected first.
3. **The forgiving error model.** Helix shows undo prominently
   and tutorials emphasize "you can always undo." Stofa's
   ToolApprovalScreen always has a "deny" that *isn't punished*.

### What we avoid

1. **Helix's full modal model.** Stofa is mostly *modeless*. We
   bring back some modal ideas (input vs navigation), but the
   chat input doesn't require "enter insert mode."
2. **The reliance on a tutorial.** Helix ships with a built-in
   tutor; Stofa's discoverability is via `?` per screen, no
   separate tutor needed.

---

## What both teach us about discoverability

Both editors have famous "you must memorize" reputations. Both
ship tutorials. Both ship cheat sheets.

Stofa's response:

- **Don't make the operator memorize.** `?` always shows current
  bindings.
- **Have so few bindings that memorization isn't required.** Five
  screen-jumps, ten navigation keys, screen-specific actions
  visible in the StatusBar. Roughly 25 keys to know.
- **Make discovery fun.** The command palette (`:`) is fuzzy-search;
  every action is named in human English.

---

## The cost-curve graph

Editor-tools tend to follow a learning curve:

```
       productivity
        ▲
        │                            ●●●●●●●●●●  ← vim (eventually)
        │                       ●●●●
        │                ●●●●●●
        │           ●●●●●
        │       ●●●●
        │   ●●●●
        │ ●●
        │●           ●●●●●●●●●●●●●●●●●●●●●●●  ← VS Code (consistent)
        │           ●
        └───────────────────────────────────────▶  time
```

Vim/Neovim ramps slowly but has higher ceiling. VS Code is
immediately productive but plateaus. **Stofa wants the VS-Code curve
shape with the vim ceiling.** Achieved by:

- Defaults that work for newcomers (arrow keys + clear chrome).
- Power-user features available but not required (vim keys via
  config; command palette for advanced actions; rebinding).
- A flat "this is what you do" surface for first-hour operators.

---

## Specific Stofa choices informed by these editors

- **`hjkl` AND arrow keys, both bound by default.** Neither
  audience pays a cost.
- **`:` and `Ctrl-P` both open the command palette.** Vim
  tradition + VS Code tradition both served.
- **`?` shows current screen bindings.** Cheaper than `:help`;
  no separate help system.
- **Focus has clear visual distinction.** Helix-style "see your
  selection."
- **Esc always cancels.** Universal.
- **No modal redefinition of letter keys.** A pressed `c` always
  means "go to chat" — never "change" or "comment" or anything
  context-specific.

---

## Closing

Neovim teaches what *power* looks like when keystrokes are dense.
Helix teaches what *discoverability* looks like when selection is
visible. Stofa takes the motion vocabulary and the help model from
Neovim, the visible-selection model and the forgiving error model
from Helix, and rejects both editors' "tutorial required" stance —
Stofa's TUI must be usable in 60 seconds, every time.
