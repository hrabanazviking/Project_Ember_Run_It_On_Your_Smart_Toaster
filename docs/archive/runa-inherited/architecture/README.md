# `docs/archive/runa-inherited/architecture/`

Runa-shaped architecture documents preserved here for lineage reference
when Ember's own architecture was ratified on 2026-05-21.

| File | What it is | Canonical Ember replacement |
|---|---|---|
| `ARCHITECTURE.md` | The parent Runa-Agent-Digital-Being system shape (kernel + event bus + Hirð + Heimskringla + multiple memory stores). | `docs/architecture/ARCHITECTURE.md` |
| `DOMAIN_MAP.md` | Runa's per-subpackage ownership for `src/runa/{core,runtime,services,apps,adapters,plugins,skills,schemas,migrations,cli}/`. | `docs/architecture/DOMAIN_MAP.md` |
| `DATA_FLOW.md` | Runa's motion grammar — events on VERÐANDI, kernel dispatch, subagent loops. | `docs/architecture/DATA_FLOW.md` |

These files are **read-only reference**. They describe the *parent* project's
shape, not Ember's. They are preserved (not deleted) per the additive rule
of `MYTHIC_ENGINEERING.md` and the Vow of Open Knowledge.

The parent project lives independently at
`hrabanazviking/Runa-Agent-Digital-Being`. If you are working on Runa,
that repository is the canonical home; this archive is for Ember
contributors who want to understand the design heritage they are working
within.

The promotion event is recorded in `docs/DEVLOG.md` (the 2026-05-21
fork-delta entry) and in `docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`
(the ratifying ADR).
