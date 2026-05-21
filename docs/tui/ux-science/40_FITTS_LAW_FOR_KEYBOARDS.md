# 40 — Fitts's Law for Keyboards

## The classical law

**Fitts's Law** (Paul Fitts, 1954): the time to acquire a target with
a pointing device is a logarithmic function of the distance to the
target and its size.

$$T = a + b \cdot \log_2(\tfrac{D}{W} + 1)$$

In GUI design, this is why:

- The Mac menu bar is at the top of the screen (infinite-edge target).
- The Windows Start menu is at the corner (corner targets are
  effectively infinite in two directions).
- Right-click context menus appear at the cursor (zero-distance).

## Fitts's Law for keyboards

There is no cursor on a keyboard, so what does Fitts's Law mean for
Stofa?

**It still applies — to fingers and to memory.**

- **Physical reach.** The keys at the home row (`a` through `;`) are
  reachable without moving the hand. Keys above and below require
  hand movement. Function keys are even further.
- **Modifier cost.** A single keypress is cheap. `Shift+letter` is
  slightly more expensive (one-hand or two-hand depending on letter).
  `Ctrl+letter` is more expensive (thumb stretch). `Ctrl+Shift+
  letter` is the slowest.
- **Sequence cost.** A two-key sequence (`gg`) is faster than a
  modifier sequence (`Ctrl+g+g`) for most operators.
- **Cognitive cost.** A memorable key is faster than an obscure one.
  `c` for "chat" is essentially zero cognitive load; `F7` for "chat"
  is significant.

## Implications for Stofa

### 1. Most-used actions get single home-row keys

The actions an operator does dozens of times per session get the
cheapest bindings:

| Action | Estimated frequency | Binding |
|---|---|---|
| Send chat message | every turn | `Enter` (it's in the input bar anyway) |
| Navigate down a list | many | `j` (home row) |
| Navigate up a list | many | `k` (home row) |
| Activate selected | many | `Enter` |
| Go to chat | a few/session | `c` (home row) |
| Go to home | a few/session | `h` (home row) or `Esc` |
| Cancel current action | many | `Esc` (off-home but universal) |

Compare with rarely-used actions:

| Action | Estimated frequency | Binding |
|---|---|---|
| Re-ingest a document | a few/week | `r` (in WellScreen) |
| Restart MCP server | a few/week | `r` (in MCPScreen) |
| Add MCP server | once/install | `a` (in MCPScreen) |
| Toggle pets | once/install | `p` |

Rare actions can be off-home-row or in the command palette.

### 2. The command palette is the long-tail bin

For actions used < weekly, **no binding is required.** The command
palette (`:` / `Ctrl-P`) provides fuzzy access. The cognitive cost of
remembering `:` + typing is *less than* the cognitive cost of
remembering an obscure binding.

### 3. Two-key sequences over three-modifier shortcuts

Vim's `gg` is fast: two letters, both home-row, no modifier. Compare
`Ctrl+Home`: one modifier reach, one non-home-row key.

Stofa uses two-key sequences for "navigation to extremes":

- `gg` — top of scroll
- `G` — bottom of scroll
- `g h` — go home (in V2; V1 uses `Esc`)

### 4. Modifier keys reserved for "across-screen" actions

Single keys (`c`, `w`, etc.) navigate screens. Modifier-keys
(`Ctrl-P`, `Ctrl-S`, `Ctrl-T`) do meta-things:

- `Ctrl-P` opens command palette (escape hatch).
- `Ctrl-S` saves in Settings.
- `Ctrl-T` toggles theme menu.
- `Ctrl-A` opens audit log.

This is a clean rule: modifiers = meta-actions. Single letters =
screen navigation + screen actions.

### 5. Repeated-key acceleration

For "press-and-hold-to-repeat" actions (scrolling), the OS / terminal
handles keyboard repeat. We test that `j`/`k` and arrows trigger
smooth repeat without missed frames.

## Specific Stofa keybinding decisions justified

### Why `c`/`w`/`d`/`s`/`m` are single letters

These are the five most-common screen jumps. Each is the first
letter of its screen name (chat, well, doctor, settings, mcp).
Mnemonic + home-row-ish. Cognitive cost ~ zero.

### Why `q` quits

`q` is the operator's universal "I want out" key. Home-row. Single
letter. No modifier. Vim, less, more, htop, lazygit, k9s — all use
`q`. We don't fight tradition.

### Why `Esc` is the cancel key

`Esc` is off the home row but every operator knows it cancels things.
For the cognitive-load-low operator, "press Esc" is one of the most
universal recoveries.

### Why `?` shows help

`?` is one keypress (with Shift on most layouts, but the gesture is
familiar). Vim, lazygit, atuin, k9s — universal. The mental model is
"the question key shows the question's answer."

### Why we ALSO bind `F1` for help

Some operators (especially newcomers) think `F1` for help (Windows
convention). Binding `F1` AND `?` to the same action serves both
traditions.

## What we explicitly didn't optimize

- **Pinky-stretches for power-users.** Vim's `:` is a pinky stretch.
  We bind `:` AND `Ctrl-P` so the operator picks.
- **Modifier-heavy bindings.** No `Ctrl+Alt+Shift+letter` anywhere.
  Operators don't have a fourth finger on a chord like that.
- **Mode-switching costs.** Modal editors pay a hidden "what mode am
  I in" cost. Stofa is mostly modeless to avoid this.

## Measurement

Per the [`90_PERFORMANCE_BUDGETS.md`](../operations/90_PERFORMANCE_BUDGETS.md):

- **Time from keypress to visual response: < 16ms.** This is a
  Fitts-adjacent metric — the operator's perceived speed depends on
  the system feeling immediate.
- **Time from `Esc` press to modal dismissed: < 33ms.** The "cancel"
  must feel instant.

## Closing

Fitts's Law is a *physical* law about distance and target size. For
keyboard-driven TUIs, the analog is *home-row distance, modifier cost,
and cognitive load*. Stofa's keymap is designed around these three —
common actions cheap, rare actions in the palette, modifiers reserved
for meta-actions, no chord harder than two-finger.
