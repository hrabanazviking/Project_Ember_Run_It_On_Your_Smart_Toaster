# 10 — Architecture Overview

This document is the **load-bearing summary** of Stofa's technical
architecture. Everything in the rest of the `architecture/` directory
is detail on points raised here.

---

## Three-layer model

```
┌───────────────────────────────────────────────────────────────┐
│  SCREENS (one per operator-visible surface)                   │
│  Home · Chat · Well · Doctor · Settings · MCP · Hjarta · Help │
│  Each screen is a Textual Screen subclass.                    │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  WIDGETS (reusable composable units)                          │
│  Chrome · Hearth · Status-Bar · Pet-Layer · Panel · Modal     │
│  Each widget is a Textual Widget subclass; styled via CSS.    │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  HANDLES (the existing Ember Protocols)                       │
│  FuniHandle · BrunnrHandle · MCPClientPool · AuditLog · Hjarta│
│  Stofa does NOT reimplement any of these. It composes them.   │
└───────────────────────────────────────────────────────────────┘
```

The bottom layer is **pre-existing Ember code**. Stofa is a fourth
realm (one might call it the *Hall realm*) that consumes the existing
Spark / Thread / Well handles to drive a visual surface.

## What goes where

- **`src/ember/stofa/app.py`** — the `StofaApp(textual.App)` entry
  point. Owns the screen stack and the global event bus.
- **`src/ember/stofa/screens/`** — one file per screen. Each screen is
  a self-contained `textual.Screen` subclass.
- **`src/ember/stofa/widgets/`** — reusable widgets (panels, status bar,
  pet layer, hearth icon).
- **`src/ember/stofa/themes/`** — CSS files for each palette.
- **`src/ember/stofa/pets/`** — the pets system (sprites, behavior).
- **`src/ember/stofa/bindings.py`** — keymap declaration; loadable
  from operator config.
- **`src/ember/stofa/services/`** — long-lived service wrappers that
  bridge handles to the event bus (e.g. `FuniService`, `WellService`).
- **`src/ember/cli/main.py`** — gets a new `ember tui` subcommand that
  imports `ember.stofa.app` lazily (so operators without `[tui]` extra
  don't pay for the import).

The full repo map is [`19_REPO_MAP.md`](19_REPO_MAP.md).

---

## Event-driven, async, single-process

Stofa is built on **Textual** (see [`11_FRAMEWORK_COMPARISON.md`](11_FRAMEWORK_COMPARISON.md)
for why). That means:

- One `asyncio` event loop.
- Every long-running operation (Funi streaming, Well retrieval, MCP
  calls) runs as an awaited coroutine.
- Widgets communicate via `Message`s on a bus, not by direct method
  calls. This is what makes screens loosely coupled.
- The pet layer subscribes to messages and animates accordingly.
- Synchronous Ember handles (sqlite3, urllib) are wrapped in
  `asyncio.to_thread()` so they don't block the event loop.

This is a deliberate departure from the synchronous chat REPL, which
uses blocking I/O. The two coexist: `ember chat` keeps its sync model
(simpler for piped use); Stofa uses async (necessary for live panels).
Both call the *same handles*.

---

## The handle layer is the contract

Stofa does not invent Brunnr access, MCP access, or Funi calls. It
holds the exact same protocols:

```python
brunnr: BrunnrHandle         # existing
funi: FuniHandle             # existing
mcp_pool: MCPClientPool      # existing (Batch I)
audit: AuditLog              # existing
identity: IdentityConfig     # existing
```

This means:

- Switching from `ember chat` to Stofa is *zero data migration*. Same
  Well, same identity, same audit log.
- A bug fix in `BrunnrHandle` benefits both surfaces.
- A new backend (Qdrant, LanceDB) automatically becomes available in
  Stofa the day it lands in Brunnr.
- Stofa can be unit-tested without touching real handles by injecting
  fakes (matching the existing `FakeFuni` / `FakeBrunnr` patterns).

This is the **Vow of Pluggable Storage** applied to surfaces, not
backends.

---

## Service wrappers — the live-update layer

Where Stofa adds substantial new code is the **service layer**. Each
service wraps a synchronous handle in an async-friendly facade and
emits messages when state changes.

Example: `WellService`.

```python
class WellService:
    """Async facade over BrunnrHandle. Emits WellStateChanged messages."""

    def __init__(self, app: StofaApp, brunnr: BrunnrHandle) -> None:
        self._app = app
        self._brunnr = brunnr

    async def refresh_counts(self) -> None:
        stats = await asyncio.to_thread(self._brunnr.count)
        self._app.post_message(WellStateChanged(stats=stats))

    async def ingest(self, path: Path) -> None:
        async for entry in self._stream_ingest(path):
            self._app.post_message(IngestProgress(entry=entry))
```

Services:
- Hold the long-lived handle.
- Translate synchronous calls into async via `to_thread`.
- Emit messages for UI updates instead of returning values directly.
- Are owned by `StofaApp`; not constructed per-screen.

There are five services in V1: `FuniService`, `WellService`,
`MCPService`, `DoctorService`, `AuditService`. Each is < 200 LOC.

---

## The pet layer is a passive subscriber

The pets system **subscribes to existing service messages**. It does
not invent state, does not poll handles, does not own any data.

```python
class PetLayer(Widget):
    def on_funi_streaming(self, event: FuniStreaming) -> None:
        self._funi_spark.set_state("thinking")

    def on_funi_done(self, event: FuniDone) -> None:
        self._funi_spark.set_state("still")

    def on_ingest_progress(self, event: IngestProgress) -> None:
        self._bee.set_state(active=True, payload=event.entry.name)

    def on_retrieval_hit(self, event: RetrievalHit) -> None:
        self._raven.fly_to(panel="citations")
```

This means **pets are pure UI**. Disabling them removes the
subscription and the widget; no other code changes. Adding a pet is
adding one widget that subscribes to one event.

See [`pets/72_PETS_BEHAVIOR_ENGINE.md`](../pets/72_PETS_BEHAVIOR_ENGINE.md)
for the per-pet behavior contracts.

---

## Theming is CSS, scoped to palette tokens

Textual supports CSS-like styling. Stofa defines **5+ themes** (Aurora,
Midgard, Ginnungagap, Solstice, Barrow) as separate `.tcss` files in
`src/ember/stofa/themes/`.

Each theme defines the same set of **semantic tokens**:

```css
/* aurora.tcss */
$background: rgb(20 24 32);
$surface: rgb(28 32 42);
$primary: rgb(168 200 220);
$accent: rgb(220 180 100);
$success: rgb(140 180 120);
$warning: rgb(220 180 100);
$error: rgb(200 110 110);
$muted: rgb(110 116 130);
$text: rgb(220 220 220);
```

Widgets reference *only* the tokens, never raw colors:

```css
Panel {
    background: $surface;
    border: round $primary;
}
```

This lets the operator switch palettes at runtime — `:theme midgard`
in the command palette — with zero widget code changes.

See [`15_THEMING_SYSTEM.md`](15_THEMING_SYSTEM.md) for the full token
list + theme contract.

---

## Keybindings: declarative, rebindable

Stofa loads keybindings from `ember.yaml`:

```yaml
stofa:
  keymap:
    # Global
    quit: ["q", "ctrl+c"]
    help: ["?", "f1"]
    command_palette: [":", "ctrl+p"]
    # Navigation
    focus_chat: ["c"]
    focus_well: ["w"]
    focus_doctor: ["d"]
    # Pets
    toggle_pets: ["p"]
```

The keymap is applied via Textual's `BINDINGS` mechanism, generated
from the loaded YAML. The defaults match the [`16_KEYBINDING_PHILOSOPHY.md`](16_KEYBINDING_PHILOSOPHY.md)
table.

---

## Plugin architecture (V2 scope)

V1 does not ship a plugin system. V2 adds **screen plugins** + **pet
plugins** by exposing two entry-point groups:

- `ember.stofa.screens` — third-party screens that show up in the
  `:screens` command palette
- `ember.stofa.pets` — third-party pets that show up in the pets
  toggle list

See [`18_PLUGIN_ARCHITECTURE.md`](18_PLUGIN_ARCHITECTURE.md).

---

## What lives where (one-line summary)

| Concern | Lives in |
|---|---|
| The app entry point | `stofa/app.py` |
| Each operator-visible surface | `stofa/screens/<screen>.py` |
| Reusable visual unit | `stofa/widgets/<widget>.py` |
| Async wrapper over a sync handle | `stofa/services/<service>.py` |
| One pet | `stofa/pets/<pet>.py` |
| CSS palette | `stofa/themes/<palette>.tcss` |
| Keymap defaults | `stofa/bindings.py` |
| Config schema additions | `schemas/config.py::StofaConfig` |
| CLI integration | `cli/main.py` (one new subcommand) |

## Closing

Three layers (screens / widgets / handles), one event loop, services
as the async-facade layer, pets as passive subscribers, themes as
swappable token sets, keybindings as declarative config. **No new
data model.** Stofa stands on the existing Ember handles like a
roof on a stone foundation.
