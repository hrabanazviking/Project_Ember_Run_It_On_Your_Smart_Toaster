# 34 — Synthesis: what we steal, what we avoid

Distillation of the 13 prior studies into a usable rubric for Stofa
design decisions.

---

## The "what we steal" catalogue

### From lazygit
- Position-as-label for panels (HomeScreen 2×2 grid; WellScreen
  sources+details).
- Bottom-bar key-hint legend.
- Modal-but-visible overlays (ToolApprovalScreen, CommandPalette).
- Numeric column-focus shortcuts (`1`/`2`/`3` for HomeScreen
  panels).
- Diff/preview-on-Enter expansion pattern.

### From htop and btop
- One-color-one-meaning across the entire app.
- Bottom-bar contextual help.
- Smooth Unicode block characters for progress bars.
- Rounded borders.
- Five built-in themes at V1.

### From neovim and helix
- `hjkl` + arrow keys both bound as defaults.
- `:` opens command palette.
- `?` shows current bindings.
- Visible focus / selection.
- Forgiving error model.

### From ranger and nnn
- Two-pane sources+details in WellScreen.
- Preview-on-focus (no Enter required for primary preview).
- `/` to start fuzzy search within a pane.
- < 500ms launch budget.

### From atuin
- Fuzzy filter as primary input in CommandPalette.
- Structured result rows with timestamps.
- Aggregate stats line at top of pane.
- "Respect the existing keybinding" (Esc, Ctrl-C, Tab, Enter).

### From aerc
- `:` command palette as escape hatch.
- Configurable keymap.
- (V2 reserved) Multi-tab pattern.

### From glow
- Real markdown rendering for Funi replies (via Rich).
- Generous padding inside content panels.
- Syntax highlighting on code blocks.
- Horizontal rules as section separators.

### From lazydocker
- Single layout template applied to multiple domains (3 layouts
  cover all 9 screens).
- Color-coded status dots.
- `]`/`[` to cycle tabs in detail panels.

### From k9s
- `:` opens fuzzy command palette as primary navigation.
- Resource-as-row pattern.
- `/` opens filter in list views.
- (V2 reserved) Quantity of themes.

### From gh-dash
- Dashboard sections (V2: configurable; V1: fixed 4).
- TUI-as-CLI-subcommand integration.

### From spotify-tui
- Persistent always-on status bar with three-zone layout.

### From AI-CLI tools (claude-code, mods, etc.)
- Per-turn separators in chat.
- Token-by-token streaming.
- Inline tool-call callouts.
- Ctrl-C tagging.

### From decorative TUIs (nap, pipes, oneko)
- Generous padding.
- Rounded borders.
- Decorative glyphs as ornament.
- Cultural permission for animation.
- Pets-as-inhabitants (slow, deliberate, ambient).

---

## The "what we avoid" catalogue

### From lazygit (and modal-key tools)
- Per-context redefinition of letter keys.
- > 80 keybindings to learn for fluency.

### From htop and btop
- Constant pulsing / animation everywhere.
- Bright saturated default colors.
- Full-screen 1-Hz repaints.

### From neovim
- "You must learn modal" tutorial cliff.
- Hidden global state (registers / marks).

### From nnn
- Pure-stdlib Spartan look.
- Shell-script-as-plugin extension.

### From aerc
- Per-screen muscle-memory cliff.
- Heavy configuration burden.

### From glow
- Pager-mode navigation.

### From lazydocker
- "Every panel has tabs" extreme.

### From k9s
- Reliance on `:` for everything (no single-letter direct jumps).
- Themes without validation (broken themes).

### From spotify-tui
- Controls in the status bar (info only).

### From AI-CLI tools
- Sign-in / cloud requirement.
- Multi-provider abstraction layer (we pick at config time).
- Template libraries (V2 maybe).

### From decorative TUIs
- Clippy-style pop-up demanding attention.
- Giant ASCII-art splash logos.
- Bouncing alerts.

---

## The rubric: ten questions to ask of every Stofa design choice

1. **Is the position meaningful?** (Lazygit: position is label.)
2. **Is one color one meaning?** (Htop/btop.)
3. **Is there a key for this without a mouse?** (Every studied TUI.)
4. **Is the binding consistent across screens?** (Lazygit + Neovim
   teach the opposite; we choose consistency.)
5. **Does `?` discover it?** (Lazygit + Neovim.)
6. **Does it animate only when it means something?** (Btop teaches
   the anti-pattern.)
7. **Is the layout one of our three?** (Lazydocker: template re-use.)
8. **Does the dashboard scan in 2 seconds?** (Htop.)
9. **Is there a fallback for no-color / no-mouse / no-Unicode?**
   (Vow of the Unbroken Whole.)
10. **Does it bring delight without demanding attention?** (Glow,
    nap, oneko.)

If a design choice can answer "yes" to 8+ of these, it ships. If
not, redesign.

---

## What Stofa is *uniquely*

After the synthesis, here's what makes Stofa not-a-clone-of-anything:

- **Cozy Viking aesthetic** — not corporate, not cyberpunk, not
  Spartan; *household Norse*. No one else is here.
- **Pets as ambient status indicators** — borrowed in spirit from
  decorative TUIs, applied as a working information surface. Not a
  precedent.
- **AI-first multi-screen home** — most AI tools are CLI; most TUIs
  are not AI; we sit in the cross.
- **Sovereign-by-default** — no sign-in, no telemetry, no cloud
  sync. Rare in modern TUI/AI tools.
- **Plugin architecture for screens AND pets AND themes** — most
  TUIs allow theme plugins; few allow screen plugins; none allow
  pet plugins.

The combination is the moat. No one else is building this.

---

## Adoption strategy implications

Based on the research, here's how Stofa probably catches on:

1. **First lure: the cute screenshot.** Operators see Hugin the
   raven perched on a panel in a Stofa screenshot and click. (See:
   how glow, nap, oneko-tui grew.)
2. **First impression: it's beautiful and works immediately.** The
   < 500ms launch + the Aurora theme + the friendly Hjarta wizard
   land them in a usable chat in 60 seconds.
3. **First retention: the dashboard feels alive.** The status bar
   updates; the hearth pulses when Funi thinks; the bee shows up
   for the first ingest. They feel like they're *in* something.
4. **First evangelism: they tell friends.** "Have you tried Stofa
   yet? It's an AI client with a little raven that perches on the
   citation panel. Sounds dumb, but it's actually really good."
5. **Long-term: it lives in their workflow.** Volmarr-class
   operators keep it open in a tmux pane. It becomes part of the
   landscape of their terminal day.

This is the *exact* adoption curve lazygit followed.

---

## Closing

Thirteen TUIs studied. ~50 patterns catalogued. The synthesis: take
the position-as-label discipline of lazygit, the visual investment of
btop, the markdown care of glow, the persistent status bar of
spotify-tui, the command palette of k9s, the speed of nnn, and the
willingness to be cute of nap and oneko. Combine. Add pets, theme,
Norse register. Refuse the things each of these gets wrong. Ship.

That's Stofa.
