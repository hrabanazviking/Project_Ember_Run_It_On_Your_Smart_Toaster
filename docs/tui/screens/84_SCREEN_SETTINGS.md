# 84 — Screen: Settings

Edit `ember.yaml` from inside Stofa. With validation, live preview
where applicable, and "this field needs the operator to think"
warnings.

---

## Purpose

The operator who wants to change a setting shouldn't have to:
- Quit Stofa.
- Find their `ember.yaml` file.
- Edit it in a text editor.
- Worry about YAML syntax.
- Relaunch.

Settings screen does all of this in-app, with field-level help.

---

## Layout

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Settings ─── unsaved changes ── 🔥 ─┐
│                                                              │
│  ▾ Identity                                                  │
│     Ember's name:    [ Mimir                          ]      │
│     Operator:        [ Volmarr                        ]      │
│                                                              │
│  ▾ Funi (LLM)                                                │
│     Runtime:         [ ollama          ▾ ]                   │
│     Model:           [ llama3.2:3b                    ]      │
│     Endpoint:        [ http://100.67.240.22:11434     ]      │
│     Streaming:       [ ✓ ]                                   │
│                                                              │
│  ▸ Brunnr (Well)                                             │
│                                                              │
│  ▸ Tools                                                     │
│                                                              │
│  ▸ MCP                                                       │
│                                                              │
│  ▾ Stofa                                                     │
│     Theme:           [ aurora          ▾ ] (live preview)    │
│     Pets:            [ ✓ ]   Animate pets: [ ✓ ]            │
│     Hearth pulse:    [ ✓ ]                                   │
│     Start screen:    [ home            ▾ ]                   │
│     UI density:      [ medium          ▾ ]                   │
│     Minimal redraw:  [ □ ] (SSH-friendly)                    │
│                                                              │
│  s = save · esc = cancel · ? = field help                   │
└──────────────────────────────────────────────────────────────┘
[ ● Realms ok · unsaved ]   [Settings]   [s save · esc cancel · ?]
```

---

## Implementation

`src/ember/stofa/screens/settings.py` — `SettingsScreen(textual.screen.Screen)`.

Composes a `VerticalScroll` of `CollapsibleSection` widgets.

Each `CollapsibleSection` corresponds to one of EmberConfig's
sub-dataclasses (IdentityConfig, FuniConfig, BrunnrConfig, etc.).
Inside each section: form fields generated from the dataclass's
fields.

---

## Field-to-widget mapping

| Dataclass field type | Widget |
|---|---|
| `str` | `Input` |
| `int` / `float` | `Input` (with numeric validation) |
| `bool` | `Checkbox` (`[✓]` / `[□]`) |
| `Path` | `Input` (with path-existence indicator) |
| `StrEnum` | `Select` dropdown |
| `Mapping[str, X]` | `Mapping_editor` (key-value pairs, V2) |
| nested dataclass | nested `CollapsibleSection` |

---

## Save flow

1. Operator presses `s` (or `Ctrl-S`).
2. SettingsScreen validates every field against its dataclass
   field type.
3. If validation fails: highlight the bad field in red, show the
   error message inline.
4. If validation passes: serialize to YAML.
5. Write to `<config_root>/config/ember.yaml` via the
   `ember.config.writer` (atomic write).
6. Reload config in StofaApp.
7. Trigger re-load of services (FuniService, etc.) if their config
   changed.
8. Show success notification in StatusBar ("Settings saved").

If `Ctrl-C` or `Esc` during edits with unsaved changes: confirm
modal "You have unsaved changes. Discard? (y/n)".

---

## Field help (`?` on focus)

Operator focuses a field, presses `?`. A small overlay appears:

```
╭── Field: Funi.model ──────────────────────╮
│                                            │
│  The Ollama model identifier.              │
│                                            │
│  Default: phi3:mini                        │
│  Recommended: llama3.2:3b (slice-2 default)│
│                                            │
│  Notes:                                    │
│  - Must be a model already pulled by       │
│    Ollama (run: ollama list).              │
│  - Tool-capable models recommended for     │
│    chat with tools enabled.                │
│                                            │
│  Esc to close                              │
╰────────────────────────────────────────────╯
```

The help content comes from the dataclass field's docstring (we
keep field-level descriptions in `schemas/config.py`).

---

## Live preview where it makes sense

Some settings can preview without save:

- **Theme:** changing the dropdown immediately re-renders Stofa in
  the new theme. (If operator cancels, Stofa reverts to the saved
  theme.)
- **Pets toggle:** immediately hides/shows pets. (Same revert.)
- **UI density:** immediately re-renders with new spacing. (Same
  revert.)

Others require save + service-reload:

- **Funi model / endpoint:** requires re-opening the Funi handle.
  Stofa shows "Will apply on save" hint when changed.
- **Brunnr backend:** same.
- **MCP servers added/removed:** same.

---

## Keybindings

| Key | Action |
|---|---|
| `↓` / `j` | Next field |
| `↑` / `k` | Previous field |
| `Tab` / `Shift+Tab` | Move between fields |
| `Space` | Toggle checkbox / open dropdown |
| `Enter` | Activate selected option / move to next field |
| `Esc` | If editing field: revert that field. If at section level: confirm-and-exit. |
| `s` / `Ctrl-S` | Save all changes |
| `?` | Field help (current field) |
| `r` | Reset section to defaults (with confirm) |
| `R` (Shift+r) | Reset ALL settings to defaults (with confirm) |

---

## What SettingsScreen does NOT do

- **Validate against the live Funi / Brunnr instance.** Validation
  is structural (correct type / valid enum); semantic validation
  ("does this Ollama endpoint actually have this model?") happens
  at service-open time.
- **Replace `ember.yaml` editing entirely.** Operators can still
  hand-edit `ember.yaml`; Stofa picks up the changes on next launch.
- **Show the actual YAML being written.** That's a debug-overlay-
  level concern.
- **Edit identity.json directly.** Identity edits go through
  Hjarta-the-wizard or `ember setup --reset`.

---

## Closing

SettingsScreen is the operator's control surface for everything
configurable. Field-level help, live preview where possible, atomic
save, structural validation. Replaces the "go find ember.yaml in a
text editor" friction with a real form-shaped UI.
