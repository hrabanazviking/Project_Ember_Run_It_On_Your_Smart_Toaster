# 91 — Terminal Compat Matrix

What terminals Stofa is tested on, and what works where.

---

## Tier 1: officially supported, tested in CI

These get full Stofa with all features. Regression tests run
against simulated versions.

| Terminal | OS | Version |
|---|---|---|
| **GNOME Terminal** | Linux | 3.40+ |
| **Konsole** | Linux | 21+ |
| **xterm** | Linux | (current) |
| **kitty** | Linux / macOS | 0.21+ |
| **alacritty** | Linux / macOS / Windows | 0.10+ |
| **iTerm2** | macOS | 3.4+ |
| **Terminal.app** | macOS | (current) |
| **Windows Terminal** | Windows | 1.13+ |

All Tier-1 terminals support: truecolor, mouse, Unicode (incl.
box-drawing + block elements), keyboard repeat. Stofa renders
fully.

---

## Tier 2: works, but limited

| Terminal | What works | What doesn't |
|---|---|---|
| **tmux** (over Tier-1 terminal) | nearly everything | nested-Esc-tab handling can be quirky |
| **screen** | basic | mouse may not work; some colors lost |
| **Apple Terminal pre-Catalina** | basic | truecolor missing; 256-color fallback |
| **PuTTY** | basic | font choice matters; some Unicode may not render |
| **xtermjs (browser)** | basic | mouse partial; F-keys may not pass through |
| **Linux console (no X)** | ASCII fallback | no Unicode; ASCII-only mode auto-engages |

Stofa works; some features (full color, mouse, smooth animations)
may degrade. ASCII fallback always works.

---

## Tier 3: best-effort

| Terminal | Notes |
|---|---|
| **Mac Terminal in legacy mode** | Try iTerm2 instead |
| **Windows ConHost (pre-Windows-10)** | Try Windows Terminal |
| **Mosh** | known issues with rapid stream rendering; Stofa works but feels laggy |
| **Various web terminals (Cloud Shell, etc.)** | varies wildly; YMMV |

Stofa launches; some features may not work or may glitch. We
respond to bug reports for Tier-3 but don't gate releases on them.

---

## Tier 4: not supported

| Terminal | Why |
|---|---|
| **DOS / Win98 console** | wrong era |
| **Serial-port-only terminals** | < 80 col commonly; Stofa needs 80+ |
| **Terminals < 40 cells wide** | Stofa refuses with "Terminal too narrow" message |

---

## Per-feature compat

### Truecolor (24-bit)

- Tier 1: ✓ all
- Tier 2: depends per terminal; we degrade to 256 then 16
- Tier 3: typically 256 or 16; we render accordingly

### Mouse

- Tier 1: ✓ all
- Tier 2: some yes (tmux), some no (screen on certain configs)
- Tier 3: varies; mouse never required

### Unicode box-drawing

- Tier 1: ✓ all
- Tier 2: depends on operator font; we have ASCII fallback
- Tier 3: ASCII fallback auto-engages on LANG=C

### Unicode block elements (▁-█)

- Tier 1: ✓
- Tier 2: depends; ASCII fallback (`.:|#`) ready
- Tier 3: ASCII

### Emoji (specifically 🔥 for the hearth)

- Tier 1: most yes; some monochrome rendering
- Tier 2: varies; ASCII fallback `^` available
- Tier 3: ASCII

### Keyboard repeat (for hjkl scrolling)

- Tier 1: ✓ all
- Tier 2: ✓ most
- Tier 3: depends on terminal-emulator settings

### Bracketed paste

- Tier 1: ✓
- Tier 2: most
- Tier 3: may pass paste as individual keystrokes (works, just slower)

### Function keys (F1-F12)

- Tier 1: ✓
- Tier 2: usually
- Tier 3: PuTTY may not pass F-keys; Stofa uses `?` as primary
  help binding, F1 as alternate

---

## SSH considerations

When `SSH_CONNECTION` is set:
- Auto-suggest `minimal_redraw: true` mode on first launch.
- Animation budget reduced to 0 by default in `minimal_redraw` mode.
- Mouse support may be limited by SSH client.

Operators on SSH with default settings:
- Pets work but no animation.
- Stream rendering smooth.
- Mouse depends on SSH terminal forwarding.

---

## Resize handling

Tested at:
- 80×24 (xterm default)
- 100×30 (common)
- 120×40 (modern terminal default)
- 200×60 (large monitor)
- 400×80 (ultrawide)
- 80×80 (tall narrow split)
- 40×24 (very narrow; Stofa degrades layout)
- < 40 cells wide: Stofa refuses with "Terminal too narrow"

---

## Per-terminal known quirks

| Terminal | Quirk | Workaround |
|---|---|---|
| Konsole | sometimes rendering glitches on rapid pet motion | reduce pet animation rate (already capped) |
| Windows Terminal | initial render flash on launch | not fixable; bounded to first frame |
| iTerm2 | shell integration features (not used by Stofa) sometimes interfere | turn off iTerm2 shell-integration if conflict |
| tmux | function keys F1-F4 may be eaten | Stofa uses `?` not `F1` as primary |
| mosh | slow stream rendering | minimal_redraw mode helps |

---

## CI matrix

GitHub Actions runs Stofa's snapshot tests on:
- ubuntu-latest with xterm (default ANSI)
- macos-latest with default Terminal-equivalent
- windows-latest with Windows Terminal

Each rendered at 80×24 and 120×40. SVG snapshot diff catches
unintended visual changes.

---

## What we promise

- **Tier 1**: Stofa looks correct, animates smoothly, all features
  work.
- **Tier 2**: Stofa launches, all features work but some look
  degraded.
- **Tier 3**: Stofa launches; some features may not work; we'll
  try to help in bug reports.
- **Tier 4**: out of scope.

---

## Closing

Stofa supports the modern terminal ecosystem fully (Tier 1) and
degrades gracefully on older or constrained terminals (Tier 2-3).
The compat matrix is *honest*: we don't claim universal support;
we say what works where and provide fallbacks where it doesn't.
