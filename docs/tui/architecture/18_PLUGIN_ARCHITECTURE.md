# 18 — Plugin Architecture (V2 scope)

V1 of Stofa ships a fixed set of screens, widgets, and pets. **V2
adds an extension system** that lets operators and the community
ship their own. This document specifies the contract.

---

## What plugins can extend in V2

| Extension type | Entry-point group | Example |
|---|---|---|
| Screens | `ember.stofa.screens` | A community "EpisodeBrowser" screen |
| Pets | `ember.stofa.pets` | A community "Skoll the wolf" pet |
| Themes | `ember.stofa.themes` | A community palette |
| Status-bar widgets | `ember.stofa.status_widgets` | A "current model token budget" indicator |
| Command palette commands | `ember.stofa.commands` | `:explain-error` |

What plugins **cannot** extend (locked surfaces):

- Funi handle. (Adapter slot, not plugin slot.)
- Brunnr handle. Same.
- The audit log format. Per ADR-0011.
- The tool framework. Per ADR-0011.
- The MCP integration. Per ADR-0014.
- The chrome layout (header / status bar position).
- The state machine.

The plugin surface is **decoration + addition**, not replacement.

---

## How plugins ship

Pip-installable packages declare entry points. Example
`pyproject.toml` for a community pets package:

```toml
[project]
name = "stofa-pets-bestiary-northern"

[project.entry-points."ember.stofa.pets"]
skoll = "stofa_pets_northern.skoll:Skoll"
hati = "stofa_pets_northern.hati:Hati"
```

The operator installs:

```sh
pip install stofa-pets-bestiary-northern
```

Stofa discovers the new pets via `importlib.metadata.entry_points()`
at app startup. They appear in the Settings → Pets toggle list.

---

## Plugin discovery

`StofaApp.discover_plugins()` runs once during CONSTRUCTING. It:

1. Calls `importlib.metadata.entry_points()` for each of the five
   plugin groups.
2. For each entry, imports the module + retrieves the class.
3. Validates the class against the appropriate Protocol.
4. Registers the plugin.

Validation failure → one-line stderr warning, plugin skipped, app
continues. (Vow of the Unbroken Whole: one bad plugin doesn't kill
the hall.)

---

## Plugin Protocols (V2)

### Screen plugin

```python
from typing import Protocol
from textual.screen import Screen

class StofaScreenPlugin(Protocol):
    """A community-supplied screen.

    Must subclass textual.screen.Screen. Must declare:
      - NAME: str  — unique screen name (e.g., "episode_browser")
      - HOTKEY: str | None  — optional default keybind
      - DESCRIPTION: str  — one-line shown in the command palette
    """
    NAME: str
    HOTKEY: str | None
    DESCRIPTION: str
```

The plugin's screen is pushed via `:screen <NAME>` in the command
palette, or via `HOTKEY` if the operator opts in.

### Pet plugin

```python
class StofaPetPlugin(Protocol):
    """A community-supplied pet.

    Must subclass `stofa.pets.PetWidget`. Must define:
      - NAME: str  — display name ("skoll")
      - DESCRIPTION: str  — one-line ("a wolf cub that watches for ingest")
      - DEFAULT_ENABLED: bool  — default off for non-builtin pets
      - SPRITE: PetSprite  — see pets/73_PETS_SPRITE_GUIDE
      - SUBSCRIBES_TO: tuple[type[Message], ...]
    """
    NAME: str
    DESCRIPTION: str
    DEFAULT_ENABLED: bool
    SPRITE: object
    SUBSCRIBES_TO: tuple
```

A pet plugin gets the same animation budget cap as built-in pets
(1 Hz per pet, 4 Hz aggregate). The framework enforces this — a
plugin pet that tries to tick faster gets throttled.

### Theme plugin

```python
class StofaThemePlugin(Protocol):
    """A theme — defined by a .tcss file path."""
    NAME: str
    DESCRIPTION: str
    TCSS_PATH: Path
```

Theme plugins are even simpler — they're just `.tcss` files
shipped in a pip package, validated against the 20-token contract
(per [`15_THEMING_SYSTEM.md`](15_THEMING_SYSTEM.md)).

### Status-bar widget plugin

```python
class StofaStatusWidgetPlugin(Protocol):
    """A widget that renders into the status bar."""
    NAME: str
    DESCRIPTION: str
    POSITION: Literal["left", "center", "right"]
    MAX_WIDTH: int    # cells
    REFRESH_INTERVAL_MS: int
```

Each plugin gets at most `MAX_WIDTH` cells of the status bar and
refreshes at the configured interval. If aggregate plugin width >
20% of status bar, some are hidden (operator picks which in Settings).

### Command palette command plugin

```python
class StofaCommandPlugin(Protocol):
    """An action invokable from `:`."""
    NAME: str           # the colon command (":explain-error")
    DESCRIPTION: str
    HANDLER: Callable[[StofaApp, str], Awaitable[None]]
```

---

## Plugin sandbox

Plugins run **in-process**, with no sandbox. This means:

- A malicious plugin has full access to the operator's Ember
  config, audit log, and Well data.
- Plugins can call any of Ember's handles.
- Plugins can `os.system()` if they want.

We don't sandbox because:
- Sandboxing in-process Python is impossible in any meaningful way.
- Operators install plugins via pip, which is already a trust
  decision (any pip package can `os.system()`).
- The MCP server pattern is the *right* answer for sandboxed
  third-party code — it runs in a subprocess with its own boundaries.

The operator-facing implication: **install plugins from sources you
trust**, the same way you'd install any pip package. The plugin
discovery surface shows the package name + author + version so the
operator can audit before enabling.

---

## Plugin lifecycle

```
Plugin discovered ──▶ Validated ──▶ Enabled (operator opt-in) ──▶ Loaded ──▶ Active
                                            ▲
                                            │
                                       Settings UI
```

- **Discovered** — appears in the Settings → Plugins list
- **Validated** — passed the Protocol check; can be enabled
- **Enabled** — operator turned it on; persists in `ember.yaml`
- **Loaded** — class imported, instance constructed
- **Active** — registered into the right system (screens / pets / etc.)

Disabling a plugin is reversible:

- Pet: removed from pet layer; can re-enable.
- Screen: command palette entry removed; can re-enable.
- Theme: if currently active, falls back to Aurora; can re-select.
- Status widget: removed from status bar; can re-enable.
- Command: removed from palette; can re-enable.

Uninstalling (pip uninstall) auto-removes from `ember.yaml`'s enabled
list with a "Plugin {name} no longer installed" log entry.

---

## Versioning + compatibility

Plugins declare a Stofa-API version they target:

```python
class Skoll(PetWidget):
    NAME = "skoll"
    STOFA_API = ">=2.0,<3.0"
    # ...
```

Stofa's plugin loader checks the constraint against its own version
and refuses-with-warning if incompatible:

```
Plugin 'skoll' targets STOFA_API >=2.0,<3.0; current Stofa is 1.2.
Skipping. Operator should: pip install --upgrade ember-agent[tui]
```

This is the contract that lets us evolve Stofa internals without
breaking community plugins silently.

---

## Distribution channels

V2 ships:

1. **PyPI** — standard pip install.
2. **A community plugin index** — `docs/STOFA_PLUGINS.md` curated
   list. Not a registry, not a market — a documented list of plugins
   the maintainers have *seen* (not endorsed).
3. **`ember plugin install <name>`** — convenience CLI that wraps
   pip install + enables the plugin. V2-V3 scope.

We do NOT ship:

- A plugin marketplace UI.
- A revenue-sharing system.
- A rating system.
- An auto-update system.

Stofa is sovereign; plugins are pip packages; trust is operator's.

---

## V1 vs V2 split

| Feature | V1 (Stofa launch) | V2 (plugin system) |
|---|---|---|
| Built-in screens | 9 fixed | 9 + plugin-added |
| Built-in pets | 9 fixed | 9 + plugin-added |
| Themes | 5 built-in | 5 + plugin + operator file |
| Status-bar widgets | core only | core + plugins |
| Command palette | core actions | core + plugins |

V1 ships everything documented in this design tree. V2 adds the
plugin system + its documentation + its tests.

V2's design happens *after* V1 ships and we have a clearer sense of
what people actually want to extend.

---

## Closing

Plugins are how Stofa grows beyond what we can ship. The contract
keeps the core stable, lets the community decorate, and respects
operator sovereignty (every plugin is opt-in; uninstall is one
command). V2 ships when V1 is stable and we have at least one
external party asking for the extension surface.
