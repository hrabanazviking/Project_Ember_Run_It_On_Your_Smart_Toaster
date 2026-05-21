# `ember.spark.hjarta/` — Hjarta

**The first-run setup ritual.** The conversation that wires Funi to
Strengr to Brunnr the first time someone meets Ember. Hjarta is a
*finite, named* state machine — not a generative wizard. Its states
are enumerated, its transitions are unit-testable, and its
end-of-flow `WriteIdentity` step is atomic.

**Shipped:** Phase 6, slice 1 (version 0.1.0); extended Phase 9
(writes `ember.yaml` at WriteIdentity); extended Phase 16 (added
`ADVANCED_TOOLS` branch).
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DATA_FLOW.md` §4 for the first-run rite; `docs/architecture/DOMAIN_MAP.md` §6 for ownership.

---

## What this subpackage owns

- **The FSM** (`machine.py`) — `HjartaState` enum, `HjartaOutcome`
  dataclass, the `run()` function that walks the states.
- **The IO surface** (`HjartaIO` dataclass) — `prompt` / `info` /
  `error` callables. Production wraps stdin/stdout; tests pass scripted
  iterables. Nothing in the FSM touches stdio directly.
- **Identity persistence** (`identity.py`) — atomic write of
  `<config_root>/identity/identity.json` via `tempfile.NamedTemporaryFile`
  + `os.replace`. Plus `load_identity` and `has_identity` for the
  CLI's first-launch redirect.
- **Prompt strings** (`prompts/wizard.toml`) — per-state body + prompt
  text. Data file per RULES.AI.md "no hardcoded data".

## What this subpackage does NOT own

- **The CLI dispatch.** `ember.cli.main` decides when to call
  `hjarta.run()` (typically: when `ember chat` / `ember ask` runs
  without an existing identity, OR explicitly via `ember setup
  --reset`).
- **Ongoing conversation.** Munnr's job.
- **Re-configuration after first run.** Operators edit
  `~/.ember/config/ember.yaml` directly — the config loader picks
  changes up on next launch. Hjarta is for *first-time* setup;
  `--reset` re-runs the same flow but doesn't try to migrate.
- **Backend probing logic itself.** Hjarta calls
  `funi_handle.open(config.funi)` and `strengr.open(config.strengr, config.brunnr)`
  but doesn't reimplement those probes.

## The FSM (per slice-2 — version 0.2.0)

```
Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell
      → TestRetrieval → NameEmber → AdvancedTools → WriteIdentity → Done
```

Each transition is a single typed function. State prompts live in
`prompts/wizard.toml`, loaded as a package resource via
`importlib.resources` + stdlib `tomllib`.

**Atomic boundary:** `WriteIdentity` is the only state that touches
the filesystem. Any failure *before* WriteIdentity leaves the
filesystem unchanged; the operator sees `outcome.success=False` with
a typed `detail` string and can retry. No half-configured state.

### The slice-2 `ADVANCED_TOOLS` branch

Added in Phase 16 (ADR 0011). After `NameEmber`, Hjarta asks one
question:

```
Optional: I can call a small set of operator-approved tools...
Enable tools? [y/N]
```

The default (empty answer / anything-but-yes) keeps tools off — the
Vow of Sovereignty made mechanical in the wizard. When the operator
answers `y`, `WriteIdentity` writes `tools: {enabled: true}` into the
initial `ember.yaml` via the `extras` channel of
`ember.config.write_ember_config`.

The operator can change this later by editing the yaml; no need to
re-run Hjarta.

## How Hjarta is invoked

### From the CLI (production)

`ember.cli.main`'s first-launch redirect calls `setup.run` (which
calls `hjarta.run`) when:

- The operator runs `ember chat` or `ember ask` without an existing
  identity (`hjarta.identity.has_identity(config_root)` is False).
- The operator explicitly runs `ember setup --reset`.

### From a test

```python
from ember.spark.hjarta import HjartaIO, run as hjarta_run

io = HjartaIO(
    prompt=lambda _t: next(answers_iter, ""),
    info=output_list.append,
    error=lambda s: output_list.append("ERROR: " + s),
)
outcome = hjarta_run(
    config=test_config,
    config_root=tmp_path,
    io=io,
    funi_opener=lambda _cfg: _FakeFuni(),
    strengr_opener=lambda _s, _b: _FakeBrunnr(),
)
```

The `funi_opener` / `strengr_opener` parameters are the test seams
— production calls the real registries.

## Layout

```
src/ember/spark/hjarta/
├── README.md
├── INTERFACE.md
├── __init__.py
├── machine.py          # HjartaState + HjartaOutcome + run()
├── identity.py         # save_identity_atomic / load_identity / has_identity
└── prompts/
    └── wizard.toml     # per-state body + prompt text
```

## Failure semantics

- **Pre-WriteIdentity failure → `HjartaOutcome(success=False, final_state=...)`
  with a typed `detail` string.** No filesystem changes.
- **WriteIdentity failure → `HjartaOutcome(success=False)`** with the
  partial state captured; the atomic-write guarantee means the
  filesystem either has both files or neither.
- **Yaml write failure (post-Phase-9) is non-fatal.** The identity
  was written; the operator gets a warning that ember.yaml couldn't
  be written but `ember chat` will still work. They can hand-write
  ember.yaml or re-run setup.
- **Operator Ctrl-C** → `HjartaOutcome(success=False, detail="operator interrupted")`.

## Slice-2 extensions

| Phase | What changed |
|---|---|
| 9 | `WriteIdentity` now also calls `ember.config.write_ember_config(config_root, identity, extras=None)` to lay down the initial `~/.ember/config/ember.yaml`. Soft-fail per the rule above. |
| 16 | New `ADVANCED_TOOLS` state between `NameEmber` and `WriteIdentity`; writes `tools: {enabled: true}` into the yaml extras when the operator opts in. |

## Related

- `INTERFACE.md` — public surface.
- `docs/architecture/DATA_FLOW.md` §4 — first-run rite in full.
- `docs/architecture/DOMAIN_MAP.md` §6 — ownership.
- `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` §3 — auto-recommend
  heuristic data table.
- `tests/unit/test_hjarta_*.py` + `tests/integration/test_phase6_acceptance.py` +
  `tests/integration/test_phase9_operator_edit.py` +
  `tests/integration/test_phase16_hjarta_tools.py` — 15+ tests across
  identity, machine, slice-2 acceptances.
