# docs/architecture/

The big-picture shape of Ember as a system. If a doc here changes, the
corresponding code is expected to change with it (or vice versa) — these
documents are load-bearing, not aspirational.

## Canonical documents (ratified 2026-05-21)

- `ARCHITECTURE.md` — Three Realms (Spark/Thread/Well), Six True Names,
  dependency law, why-no-kernel-no-bus, first-slice anchor.
- `DOMAIN_MAP.md` — per-subpackage ownership for `src/ember/{schemas,well,thread,spark,cli}/`.
- `DATA_FLOW.md` — three canonical flows (turn / ingest / first-run rite)
  with explicit happy and sad paths.

## Living working documents

- `EMBER_FORK_DELTA.md` — Cartographer's per-file disposition record for
  the migration from the inherited Runa parent. Long-term lineage
  reference.
- `EMBER_FIRST_SLICE_PLAN.md` — file-by-file plan for the minimum viable
  Ember (~38 new files across seven phases). **First slice complete and
  ratified at 0.1.0 (2026-05-21);** kept as historical record alongside
  the slice-2 plan once that lands.
- `EMBER_SECOND_SLICE_OPTIONS.md` — Cartographer's menu of slice-2
  starting points (the five candidate ADRs from ADR 0007 §5, three
  suggested bundles, and the template for `EMBER_SECOND_SLICE_PLAN.md`
  once Volmarr picks scope). **Not a plan — a map of choices.**

## Imported plundered material (Runa-era source material, preserved)

These are the long-form architectural source documents migrated from
repo root during the 2026-05-17 bootstrap. They describe the parent
project's shape and feed the design heritage Ember stands on.

- `ROBUST_AGENT_ENGINEERING_PLAN.md` — original Mythic Engineering build
  plan with the Bifröst / VERÐANDI / Skuld / Muninn architecture.
- `Runa-Agent-Digital-Being.md`, `Runa_Agent_Digital_Being.md` — two
  parallel large vision drafts (intentionally not merged — see ADR 0002).
- `Technical_Architecture_of_Volmarrs_AI_Ecosystem.md` — cross-project
  ecosystem context (NSE, MindSpark, WYRD, Seidr-Smidja, HERETIC, etc.).

## Lineage — the Runa-shaped predecessors

The Runa-shaped predecessors of the three canonical documents above were
moved into `docs/archive/runa-inherited/architecture/` on 2026-05-21
when the Ember versions were ratified and promoted. They are preserved
there, not deleted. See `docs/archive/runa-inherited/architecture/README.md`
for the mapping table.
