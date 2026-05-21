# 19 — Repo Map

Where Stofa lives in `src/ember/` and how each file is named.

---

## The `src/ember/stofa/` package

```
src/ember/stofa/
├── __init__.py              # exports StofaApp + version
├── README_AI.md             # what this module owns (per Mythic-Engineering)
├── INTERFACE.md             # public API
│
├── app.py                   # StofaApp(textual.App) — the entry point
├── bindings.py              # default keymap + load_keymap(config)
├── messages.py              # ~20 Message subclasses (event bus)
│
├── screens/                 # one file per operator-visible surface
│   ├── __init__.py
│   ├── home.py              # HomeScreen (4-panel dashboard)
│   ├── chat.py              # ChatScreen
│   ├── well.py              # WellScreen (browse + ingest)
│   ├── doctor.py            # DoctorScreen
│   ├── settings.py          # SettingsScreen
│   ├── mcp.py               # MCPScreen
│   ├── tool_approval.py     # ToolApprovalScreen (modal)
│   ├── hjarta_wizard.py     # HjartaWizardScreen (first-run)
│   └── help_overlay.py      # HelpOverlay (transparent overlay)
│
├── widgets/                 # reusable visual units
│   ├── __init__.py
│   ├── chrome_header.py     # the top "Stofa · {screen}  🔥  {model}" bar
│   ├── status_bar.py        # the bottom realm-state bar
│   ├── hearth.py            # the 🔥 icon (pulses when Funi thinks)
│   ├── panel.py             # bordered titled container
│   ├── modal.py             # base for modal screens
│   ├── input_bar.py         # chat input box
│   ├── messages_view.py     # chat message scrollback
│   ├── citation_card.py     # one retrieval hit
│   ├── command_palette.py   # the : / Ctrl-P palette
│   ├── data_table.py        # extended Textual DataTable
│   └── collapsible_section.py # for Settings sections
│
├── services/                # async wrappers over handles
│   ├── __init__.py
│   ├── funi_service.py      # FuniService — wraps FuniHandle
│   ├── well_service.py      # WellService — wraps BrunnrHandle + ingest
│   ├── mcp_service.py       # MCPService — wraps MCPClientPool
│   ├── doctor_service.py    # DoctorService — periodic realm probes
│   └── audit_service.py     # AuditService — async wrapper for AuditLog
│
├── pets/                    # the menagerie
│   ├── __init__.py
│   ├── README_AI.md         # pets-module owns
│   ├── pet_layer.py         # PetLayer — the floating widget container
│   ├── base.py              # PetWidget base class
│   ├── sprites.py           # sprite-loading utilities
│   ├── sprites/             # ASCII art for each pet
│   │   ├── hugin.txt
│   │   ├── refur.txt
│   │   ├── heidr.txt
│   │   ├── sumarbyfa.txt
│   │   ├── geri_cub.txt
│   │   ├── ask_sapling.txt
│   │   ├── drift.txt
│   │   ├── funi_spark.txt
│   │   └── ember_ember.txt
│   │
│   ├── hugin.py             # the raven
│   ├── refur.py             # the fox
│   ├── heidr.py             # the goat
│   ├── sumarbyfa.py         # the bee
│   ├── geri_cub.py          # the wolf cub
│   ├── ask_sapling.py       # the ash sapling
│   ├── drift.py             # the snowflake spirit
│   ├── funi_spark.py        # the hearth flame
│   └── ember_ember.py       # the static logo ember
│
├── themes/                  # CSS-based palettes
│   ├── __init__.py
│   ├── loader.py            # load_theme(name) + validation
│   ├── aurora.tcss          # default (cool twilight)
│   ├── midgard.tcss         # warm earth
│   ├── ginnungagap.tcss     # deep void
│   ├── solstice.tcss        # high contrast
│   └── barrow.tcss          # colorblind-safe
│
├── utils/                   # small helpers
│   ├── __init__.py
│   ├── responsive.py        # width-based class toggling
│   ├── ascii_fallback.py    # unicode→ASCII degrade mappings
│   └── tty_detect.py        # SSH / no-color / no-mouse detection
│
└── _version.py              # __version__ = "0.3.0-rc1"  (or whatever)
```

Roughly **45 files** of new code. The biggest individual files are
expected to be:
- `chat.py` (~400 LOC — the most complex screen)
- `pet_layer.py` (~250 LOC — animation orchestration)
- `home.py` (~200 LOC — the 4-panel composition)
- `well.py` (~250 LOC — ingest progress)

Most other files are 50-150 LOC.

---

## Where Stofa code is forbidden

Stofa is a **surface**. It does not own data. It does not reimplement
backends. Specifically, the following are **architectural violations**
(checked by code review):

| File pattern | Reason it's banned |
|---|---|
| `src/ember/stofa/*.py` importing from `src/ember/well/brunnr/sqlite_vec/*` directly | Use `BrunnrHandle` Protocol |
| `src/ember/stofa/*.py` importing from `src/ember/spark/funi/ollama/*` directly | Use `FuniHandle` Protocol |
| Any non-Stofa file importing from `src/ember/stofa/*` | Stofa depends on others; others don't depend on Stofa |
| Direct sqlite3 / psycopg / urllib calls inside Stofa | Use the existing handles |
| Any business logic in widgets (`widgets/*.py`) | Widgets are visual; logic lives in screens or services |

A pre-commit linter checks these patterns. Violations fail CI.

---

## Tests directory layout

```
tests/
├── unit/
│   ├── test_stofa_app.py
│   ├── test_stofa_messages.py
│   ├── test_stofa_bindings.py
│   ├── test_stofa_themes_loader.py
│   ├── test_stofa_responsive.py
│   ├── test_stofa_ascii_fallback.py
│   ├── test_stofa_services_funi.py
│   ├── test_stofa_services_well.py
│   ├── test_stofa_services_mcp.py
│   ├── test_stofa_pets_layer.py
│   ├── test_stofa_pets_hugin.py        # one per pet
│   └── test_stofa_pets_<rest>.py
│
├── integration/
│   ├── test_stofa_e2e_chat_turn.py     # spin up app, drive a turn
│   ├── test_stofa_e2e_first_run.py     # Hjarta wizard
│   ├── test_stofa_e2e_ingest.py        # Well screen ingest
│   ├── test_stofa_e2e_resize.py        # SIGWINCH at multiple sizes
│   ├── test_stofa_e2e_theme_swap.py    # live theme change
│   ├── test_stofa_e2e_mcp_integration.py # MCP tool flow visualised
│   └── test_stofa_e2e_quit_clean.py    # q / Ctrl-C exit hygiene
│
└── snapshot/
    ├── home_aurora_120x40.svg          # rendered SVG snapshots
    ├── home_midgard_120x40.svg
    ├── chat_streaming_120x40.svg
    ├── well_browsing_120x40.svg
    └── ... ~25 snapshots in V1
```

Textual ships `pytest-textual-snapshot` for the snapshot tests —
the rendered output is captured as SVG and diffed in CI. This is how
we catch "did the layout shift unintentionally."

---

## Documentation layout

```
docs/
├── tui/                     # this entire design tree
├── decisions/
│   └── 0015-stofa-tui.md    # the ADR (to be written before code)
└── DEVLOG.md                # Batch K (Stofa V1 ship) goes here
```

The `docs/tui/` tree (this directory) is the *design*; the ADR is
the *commitment*; the DEVLOG is the *record*.

---

## Config additions

`src/ember/schemas/config.py` gets one new dataclass:

```python
@dataclass(frozen=True, slots=True)
class StofaConfig:
    """Operator-facing Stofa preferences."""
    theme: str = "aurora"
    pets_enabled: bool = True
    pets_animate: bool = True
    start_screen: str = "home"   # "home" | "chat"
    keymap: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    minimal_redraw: bool = False  # SSH-friendly mode
```

Added to `EmberConfig`:

```python
@dataclass(frozen=True, slots=True)
class EmberConfig:
    # ... existing fields ...
    stofa: StofaConfig = field(default_factory=StofaConfig)
```

---

## CLI integration

`src/ember/cli/main.py` gets one new subcommand:

```python
sub.add_parser("tui", help="Open Stofa (Ember's interactive TUI).")
```

Plus the no-argument behavior: when `ember` is run with no args AND
stdin is a TTY (interactive launch), Stofa opens. When stdin is
piped (script mode), the existing help-message behavior wins. This
keeps `ember chat`-in-pipelines unchanged.

Lazy import:

```python
if args.command == "tui":
    from ember.stofa.app import StofaApp  # noqa: PLC0415
    StofaApp(config=config, config_root=config_root).run()
    return 0
```

Operators without `[tui]` extra get a friendly "install with
`pip install ember-agent[tui]`" message rather than ImportError.

---

## Pip extra

`pyproject.toml`:

```toml
tui = ["textual>=2.0,<3.0"]
```

One direct dep. Transitive: Rich, markdown-it-py, mdit_py_plugins,
pygments, linkify-it-py, uc-micro-py, platformdirs (~12 total).
All MIT/BSD.

---

## Closing

Forty-five new files in `src/ember/stofa/`. One CLI subcommand. One
new schema dataclass. One new pip extra. All under the existing
realm boundaries; no other Ember module imports from Stofa.

The full V1 ship lands as a single ADR-0015 commit when the design
tree is reviewed and ratified.
