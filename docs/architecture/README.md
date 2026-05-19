# docs/architecture/

The big-picture shape of Runa as a system. If a doc here changes, the corresponding code is expected to change with it (or vice versa) — these documents are load-bearing, not aspirational.

## Canonical documents

- `DOMAIN_MAP.md` — every subsystem in `src/runa/` named in one sentence, ownership rules, boundary rules.
- `ARCHITECTURE.md` — layer diagram, dependency direction, the kernel/event-bus/memory/world-model story.
- `DATA_FLOW.md` — how events travel, where memory writes happen, request lifecycle.

## Imported plundered material

Long-form architectural source documents migrated from repo root during the 2026-05-17 bootstrap:

- `ROBUST_AGENT_ENGINEERING_PLAN.md` — the original Mythic Engineering build plan with the Bifröst / VERÐANDI / Skuld / Muninn architecture.
- `Runa-Agent-Digital-Being.md`, `Runa_Agent_Digital_Being.md` — two large vision-stage agent designs (possible duplicates, review pending).
- `Technical_Architecture_of_Volmarrs_AI_Ecosystem.md` — ecosystem context for how Runa fits with NSE, MindSpark, WYRD, Seidr-Smidja, HERETIC, etc.

These are the source material the canonical documents above will distill from.
