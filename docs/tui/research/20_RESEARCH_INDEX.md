# 20 — Research Index

Stofa stands on shoulders. This directory studies **15 excellent
TUIs**, distills what makes each one work, and synthesizes the
lessons into a "what we steal / what we avoid" rubric for Stofa.

Every study follows the same shape:
- **What it is**
- **The clever idea**
- **What we steal for Stofa**
- **What we explicitly avoid**

The synthesis at the end ([`34_SYNTHESIS.md`](34_SYNTHESIS.md))
consolidates across all 14.

---

## The 15 studied

| File | TUI | What it teaches us |
|---|---|---|
| [`21_LAZYGIT.md`](21_LAZYGIT.md) | lazygit (Go) | column-as-context, modal but visual |
| [`22_HTOP_AND_BTOP.md`](22_HTOP_AND_BTOP.md) | htop / btop | live updates, restraint in animation |
| [`23_NEOVIM_AND_HELIX.md`](23_NEOVIM_AND_HELIX.md) | nvim / helix | modal editing, motion primitives |
| [`24_RANGER_AND_NNN.md`](24_RANGER_AND_NNN.md) | ranger / nnn | three-pane file managers |
| [`25_ATUIN.md`](25_ATUIN.md) | atuin | shell-history search as a TUI |
| [`26_AERC.md`](26_AERC.md) | aerc | email TUI; multi-tab, vim-shaped |
| [`27_GLOW.md`](27_GLOW.md) | glow | markdown rendering in the terminal |
| [`28_LAZYDOCKER.md`](28_LAZYDOCKER.md) | lazydocker | dashboard-of-dashboards pattern |
| [`29_K9S.md`](29_K9S.md) | k9s | command palette as primary nav |
| [`30_GH_DASH.md`](30_GH_DASH.md) | gh-dash | GitHub-as-dashboard; views + filters |
| [`31_SPOTIFY_TUI.md`](31_SPOTIFY_TUI.md) | spotify-tui | always-on context bar |
| [`32_CHATGPT_AND_AI_TUIS.md`](32_CHATGPT_AND_AI_TUIS.md) | claude-code, mods, gpt-cli, llm | AI-chat-in-TUI patterns |
| [`33_DECORATIVE_TUIS_NAP_PIPES_NEKOTUI.md`](33_DECORATIVE_TUIS_NAP_PIPES_NEKOTUI.md) | nap, pipes.sh, oneko-tui | cute / decorative TUIs |
| [`34_SYNTHESIS.md`](34_SYNTHESIS.md) | (synthesis) | the rubric |

---

## The high-level lessons (preview of synthesis)

These are the patterns we'll see repeated across the studies:

1. **Position is a label.** Lazygit's three columns each *mean*
   something (staged / unstaged / log); the operator never wonders
   which is which because position is fixed.
2. **The dashboard is more important than the screen.** htop's main
   view is "everything at once"; the operator can scan rather than
   navigate.
3. **Modal editing is power, not friction — when discoverable.**
   nvim's modal system overwhelms novices; helix's pre-selection
   model softens the curve.
4. **Command palettes are the escape hatch.** k9s + every modern
   editor proves that `:` (or `Ctrl-P`) lets operators do *anything*
   without memorizing every key.
5. **A live status bar is half the UI.** spotify-tui's always-on
   playback bar; lazygit's git-state line. Operators look down for
   ground truth.
6. **Cute > corporate.** Glow's cat, lazygit's commit jokes,
   pipes.sh's pure-decoration motion — these are not optional;
   they're load-bearing for adoption.
7. **Theme matters more than you think.** k9s ships ~30 themes;
   atuin's dracula option doubled its install rate the week it
   landed (apocryphal but plausible).
8. **Render diff, not full repaint.** Every modern TUI uses
   change-only updates; full-screen repaints are a bandwidth + flicker
   sin.
9. **Help is a keypress.** lazygit's `?`, neovim's `:help`, atuin's
   `Ctrl-H` — without it, every TUI fails Persona 2 (Iðunn the
   newcomer).
10. **One thing well, then more.** Every great TUI started narrow.
    Stofa V1 ships chat + well + doctor + settings + mcp — more than
    one, but each genuinely useful.

---

## Anti-pattern catalogue

Things we see in less-great TUIs that we explicitly will NOT do:

- **Splash screens longer than a blink.** No one wants to watch a
  3-second logo animate.
- **Confusing iconography.** A box with a clock in it that means…
  what? Either label it or omit it.
- **Hidden commands.** Actions that only exist via a config file,
  with no discoverable surface in the UI. Always have a command
  palette entry.
- **Inconsistent colors.** Different "red" in different panels.
  Pick five semantic colors and never deviate.
- **Animation that distracts.** Pulsing borders, spinning indicators
  that never stop. Animation should mean something.
- **Crashes from terminal weirdness.** No graceful fallback for
  no-color / no-mouse / no-Unicode. Stofa handles all three.
- **Quit-only-via-Ctrl-C.** Every TUI must have a `q` (or equivalent)
  that actually works.

---

## How to use this research

When designing a new Stofa surface, ask:

1. **Which of the 14 has solved this problem before?** Read their
   study.
2. **What did they steal vs invent?** The synthesis catalogues this.
3. **What's our Vow-aligned variant?** Stofa is sovereign by default,
   Norse-aesthetic, cozy. Sometimes the right answer is "what they
   did, but warmer."

Every screen plan in [`../screens/`](../screens/) cites at least two
of these studies in its "inspiration" section.
