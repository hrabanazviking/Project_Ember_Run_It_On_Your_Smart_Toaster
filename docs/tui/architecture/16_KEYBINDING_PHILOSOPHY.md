# 16 — Keybinding Philosophy

Stofa's keybinding system is the operator's primary interface. This
document defines the **default keymap**, the **rebinding mechanism**,
and the **principles** that govern both.

---

## The five principles

### 1. Every action has a keybinding

There is no action in Stofa that requires a mouse. Period. The mouse
is a *convenience*, not a *requirement*. Persona 3 (Sigrún the
power-user) and Persona 5 (Eirwyn on SSH) both depend on this.

### 2. Bindings are consistent across screens

Global bindings (`?`, `q`, `Esc`, `:`, `Ctrl-P`) work everywhere and
mean the same thing. Screen-specific bindings are scoped to that
screen.

### 3. Defaults match three keyboard traditions

The default keymap supports operators coming from:

- **Vim** (`hjkl`, `:`, `Esc`, `gg`/`G`).
- **VS Code / GUI tradition** (`Ctrl-P`, arrow keys, `Esc`).
- **Bare terminal tradition** (function keys: `F1` for help).

We bind the same actions to multiple keys when those keys are
idiomatic in different traditions. This is NOT redundant; it's how
we serve multiple personas without forcing them to relearn.

### 4. Every binding is operator-rebindable

`ember.yaml` exposes the full keymap. Operators can override any or
all bindings; partial overrides keep the defaults for unset bindings.

### 5. Discoverability is one keypress away

`?` shows the current screen's bindings, grouped by section, always.
Operators never have to remember; they can always re-discover.

---

## Default keymap

### Global (work everywhere)

| Action | Bindings | Notes |
|---|---|---|
| Show help overlay | `?`, `F1` | Pop-up; dismiss with `?` or `Esc` |
| Command palette | `:`, `Ctrl-P` | Fuzzy command search |
| Quit Stofa | `q`, `Ctrl-C` | Two attempts of `Ctrl-C` to force-exit during a hang |
| Cancel current action | `Esc` | Modal dismiss; field defocus; pop screen |
| Toggle pets | `p` | Animations + presence |
| Toggle theme menu | `Ctrl-T` | Quick theme switch (in addition to `:theme`) |
| Refresh current screen | `r`, `F5` | Re-poll services |
| Go to Home | `h` (from any non-home screen), `Esc` (from screen) | |

### Navigation between screens

| Action | Binding |
|---|---|
| Go to Chat | `c` |
| Go to Well | `w` |
| Go to Doctor | `d` |
| Go to Settings | `s` |
| Go to MCP | `m` |

Single-letter mnemonic, lowercase. The operator presses `c` for
chat, `w` for well, `d` for doctor — first letter wins.

### Within a screen — generic navigation

| Action | Bindings | Notes |
|---|---|---|
| Move focus down | `j`, `↓` | within scrollable lists |
| Move focus up | `k`, `↑` | |
| Move focus left | `h`, `←` | between panels |
| Move focus right | `l`, `→` | |
| Page down | `Ctrl-D`, `Page Down` | |
| Page up | `Ctrl-U`, `Page Up` | |
| Jump to top | `gg`, `Home` | |
| Jump to bottom | `G`, `End` | |
| Activate / open / submit | `Enter` | |
| Cycle focus | `Tab` / `Shift-Tab` | |

### Chat screen

| Action | Binding |
|---|---|
| Send message | `Enter` (when input focused) |
| New line in input | `Shift-Enter` |
| Edit last message | `↑` (when input is empty) |
| Interrupt current stream | `Ctrl-C` (one press during stream; subsequent presses quit) |
| Clear current input | `Ctrl-U` |
| Open citation in detail view | `Enter` (on citation focus) |
| Approve tool call | `y` (in tool approval modal) |
| Approve once + remember session | `a` |
| Deny tool call | `n` |
| Open audit log | `Ctrl-A` |

### Well screen

| Action | Binding |
|---|---|
| Ingest a path | `i` |
| Re-ingest selected | `r` |
| Open document detail | `Enter` |
| Search documents | `/` |
| Sort by name | `1` |
| Sort by ingest date | `2` |
| Sort by chunk count | `3` |
| Delete document (with confirm) | `Delete` |

### Doctor screen

| Action | Binding |
|---|---|
| Re-run all probes | `r` |
| Show realm details | `Enter` |
| View raw response | `v` |

### Settings screen

| Action | Binding |
|---|---|
| Save changes | `s`, `Ctrl-S` |
| Cancel | `Esc` |
| Field help | `?` (on focused field) |
| Toggle section | `Space`, `Enter` (on `▾`/`▸`) |

### MCP screen

| Action | Binding |
|---|---|
| Add server | `a` |
| Ping selected | `p` |
| Restart selected | `r` |
| Toggle auto-approve for a tool | `Space` (on tool row) |
| View server logs | `l` |

### Hjarta wizard

| Action | Binding |
|---|---|
| Next field | `Tab`, `Enter` |
| Previous field | `Shift-Tab` |
| Field help | `?` |
| Cancel wizard | `Esc` (with confirm) |
| Complete wizard | `Enter` on the last field |

### Help overlay

| Action | Binding |
|---|---|
| Dismiss | `?`, `Esc` |
| Scroll | `j`/`k`, arrows |

---

## Rebinding mechanism

`ember.yaml`:

```yaml
stofa:
  keymap:
    quit: ["q", "ctrl+c"]
    help: ["?", "f1"]
    focus_chat: ["c"]
    # ... etc
```

The `bindings.py` module in `src/ember/stofa/` defines the default
map; operator config overlays. Each binding is a list of strings
because multiple keys can trigger the same action.

Keys are specified in Textual's binding syntax:
- Single chars: `a`, `?`, `1`
- Specials: `enter`, `escape`, `tab`, `space`, `home`, `end`
- Modifiers: `ctrl+x`, `shift+enter`, `alt+1`
- Function keys: `f1`–`f12`

We do NOT support binding to the `Hyper`/`Meta`/`Super` modifiers — too
terminal-emulator-dependent.

---

## Conflicts + resolution

If the operator's overrides create a conflict (same key bound to two
actions), the load fails with a clear error:

```
Keymap conflict: 'c' is bound to both 'focus_chat' and 'create_doc'.
Each key may only trigger one action. Fix in ember.yaml under
stofa.keymap.
```

If the operator's overrides bind to a non-existent action:

```
Unknown action 'open_neovim' in stofa.keymap.
Available actions:
  quit, help, command_palette, focus_chat, focus_well, ...
```

These checks run at config-load time, not at first keypress. The
operator finds out about typos during launch, not three days later
when they finally hit that key.

---

## What we don't bind

Deliberately unbound by default:

- **`Ctrl-Z`** — suspend. Left to the terminal/shell.
- **`Ctrl-L`** — clear screen. Textual handles redraw.
- **`Ctrl-D`** — EOF. In chat input, interpreted as "submit and quit
  this screen"; elsewhere passes through.
- **`Ctrl-Backslash`** — SIGQUIT. Left as-is.

We honor terminal conventions where they're not in conflict with our
needs.

---

## The command palette

`Ctrl-P` (or `:`) opens a fuzzy-searchable command palette:

```
┌─ Command ────────────────────────────┐
│ > the_                                │
│                                       │
│   :theme aurora                       │
│   :theme midgard                      │
│   :theme ginnungagap                  │
│   :theme solstice                     │
│   :theme barrow                       │
│                                       │
└───────────────────────────────────────┘
```

Every named action is in the palette. Typing-as-fuzzy-search. Enter to
execute, Esc to cancel. This is the *escape hatch* for actions that
don't have a direct binding (e.g., rare admin actions like
`:export-audit-log`).

---

## Per-persona binding preferences

These are the default keymap profiles operators can choose in
Settings:

- **default** — the table above
- **vim** — emphasizes hjkl; binds `:q`/`:wq` for quit; binds `:w` to
  save in Settings
- **emacs** — `Ctrl-x Ctrl-c` to quit; `Ctrl-x Ctrl-s` to save;
  `Ctrl-g` for cancel
- **arrows-only** — for operators uncomfortable with hjkl; disables
  hjkl globally, keeps arrows
- **macOS** — `Cmd-Q` if the terminal forwards it (rare); otherwise
  same as default

These are starting points; operators tweak from there.

---

## Two-key sequences

We support a small set of two-key sequences (vim-style):

- `gg` — go to top
- `G` — go to bottom
- `dd` — (in Well only) delete document, with confirm
- `yy` — (in Chat only) copy last message
- `g h` — go home (alternative to `Esc`)
- `g c` — go chat (alternative to `c`)

Two-key sequences time out after 1 second. The operator who presses
`g` and waits sees a hint at the bottom of the screen: "g- ... waiting
for next key (Esc to cancel)".

---

## Mouse support

Even though every action is keyboard-accessible, the mouse is
supported as a convenience:

- **Click on a panel** — focuses it.
- **Click on a button-shaped widget** — activates it.
- **Scroll wheel** — scrolls the focused scrollable.
- **Right-click** — opens context menu (V2; V1 ignores).
- **Drag on a draggable border** — resize (V2).

In V1, mouse is *additive*. It doesn't replace any keyboard action.
Mouse-only operators are accommodated; mouse-required operators have
to wait for Auga (the GUI).

---

## Closing

Single-letter mnemonics for screens, vim+arrow dual-binding for
navigation, full operator rebinding via YAML, command palette as the
escape hatch, `?` for discovery. The discipline is **predictability,
consistency, configurability** — pick one, the others come along.
