# INTERFACE — `ember.spark.hjarta`

## Module purpose

The first-run setup ritual. A finite state machine that wires Funi to
Strengr to Brunnr and writes the identity atomically at the end.

## Public entry points (planned, Phase 6)

- `ember.spark.hjarta.machine.run(config_root=Path("~/.ember/")) -> HjartaOutcome`
- `ember.spark.hjarta.machine.HjartaState` — the state enum.

## States

`Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell
→ TestRetrieval → NameEmber → WriteIdentity → Done`

Each transition is a single typed function. Each state's prompt content
lives in `config/hjarta_prompts/*.yaml` (RULES.AI.md "no hardcoded data").

## Inputs

A clean (or to-be-reset) `~/.ember/` root.

## Outputs

`HjartaOutcome(success: bool, error: str | None, identity_path: Path | None)`.

## Side effects

- Reads operator answers (stdin in CLI mode).
- Probes Funi runtime (calls `funi.open` / `funi.health`).
- Probes Brunnr backend (calls `strengr.open` + `brunnr.add_chunk` +
  `brunnr.vector_search` + `brunnr.delete` on a single probe chunk).
- Writes `~/.ember/identity/identity.yaml` **atomically** at the
  WriteIdentity state.

## Allowed imports

`ember.schemas`, `ember.spark.funi`, `ember.thread.strengr`,
`ember.well.brunnr` (through public interfaces only).

## Invariants

- On any failure before WriteIdentity, the filesystem is unchanged.
- A successful run produces an identity file that subsequent
  `ember chat` invocations consume without further setup.
- No state transition is silent; each one is observable for tests.

## Forbidden responsibilities

- Ongoing conversation (Munnr).
- Reconfiguration after first run (`ember config edit` / `ember setup --reset`).
