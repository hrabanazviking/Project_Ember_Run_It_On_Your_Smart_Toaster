# ADR 0004 — Python Craft Corpus (50 Technical Documents)

**Date:** 2026-05-17 (same day as ADR-0001, ADR-0002, ADR-0003)
**Status:** Accepted
**Authors:** Volmarr Wyrd (commissioning), Runa Gridweaver Freyjasdottir (writing)
**Supersedes:** *(none)*
**Superseded by:** *(none)*
**Related:** [ADR 0001](./0001-mythic-engineering-bootstrap-2026-05-17.md), [ADR 0002](./0002-initial-subsystem-decisions-2026-05-17.md), [ADR 0003](./0003-research-corpus-2026-05-17.md)

---

## Context

Following the bootstrap (ADR-0001), the subsystem implementation decisions (ADR-0002), and the 50-document AI / CS research corpus (ADR-0003), Volmarr requested a parallel 50-document corpus on the *Python craft* required to actually build robust, error-correcting, self-healing, crash-proof, efficient, and stable Python software. Where `docs/research/` covers *concepts*, this corpus covers *implementation techniques in Python specifically*.

The corpus was produced as a single autonomous session, 50 documents in 10 batches of 5, with commit + push between every batch.

## Decisions

### D-4.1 — Adopt the 50-document Python craft corpus as project-local reference

The 50 documents under `docs/python/01-…` through `docs/python/50-…` are accepted as project-local Python-craft reference material. They complement `docs/research/` (concepts) with implementation patterns: real Python code, real PEPs, real libraries, real failure modes.

The corpus is *informative*, not binding. Final implementation choices belong in per-slice ADRs.

### D-4.2 — Seven-section template (same as research corpus)

The same seven-section template applies (Core idea / Technique-mechanism / Key works-libraries / Pitfalls and gotchas / Applicability to Runa / Open questions / References). Consistency with `docs/research/` makes navigation between the two natural.

### D-4.3 — Code samples must be correct as written

Where docs include Python code, the code is correct as written (would compile, would pass type-check, would run if copy-pasted with the obvious imports). This is the standard the corpus is held to. Errors get dated correction notes at the top of affected docs.

### D-4.4 — Two parallel corpora form one library

`docs/research/` (50 docs, ADR-0003) and `docs/python/` (50 docs, ADR-0004) together form a 100-document technical library. The split is deliberate:

- **Architect's reading:** `docs/research/` for conceptual grounding before designing a subsystem.
- **Forge Worker's reading:** `docs/python/` for implementation patterns when writing the slice.

Cross-references go both ways via Wikilink-style `[[NN-slug]]` (resolved by filename within each corpus).

## Consequences

### Positive

- Every architectural commitment from ADR-0001 and ADR-0002 now has a Python implementation reference. asyncio + worker-pool? Doc 19 + 21 + 22 + 23 + 24. Plugin isolation? Doc 44 + research doc 37. Standing-trust audit? Doc 46 + 47 + 48 + research doc 40.
- New contributors (human or AI) have a single curated reading list for Python craftsmanship needed to work on Runa.
- The corpus surfaces real PEPs, real libraries, real maintainers — citations the Forge Worker can act on.
- Cross-references between `docs/python/` and `docs/research/` make the conceptual-to-implementation path navigable.

### Negative

- 100 documents (across both corpora) is a lot of reading. Operators with limited time must navigate via INDEX.
- The Python ecosystem moves quickly. Library names, version specifics, idiomatic recommendations drift over 12-24 months. Re-survey periodically.
- Some docs are quite Python-specific (asyncio internals, GIL details) — they age with the language; check against current Python version when applying.

### Cost

50 documents × ~8.8 KB average = ~440 KB of new content. 11 commits to development.

## What this ADR does *not* decide

- The actual implementation choice for any subsystem. Those become per-slice ADRs.
- Maintenance cadence for the corpus. Suggested 12-24 months for full re-survey; per-doc updates as needed when libraries deprecate or PEPs change.

## References

- `docs/python/INDEX.md` — full corpus map.
- `docs/python/README.md` — template + reading guide.
- `docs/research/` — the conceptual companion corpus (ADR-0003).
- All 50 documents under `docs/python/01-…` through `docs/python/50-…`.
- `TASK_runa_python_craft.md` — resumption anchor for the autonomous run.
- `docs/DEVLOG.md` — entries for the python-craft-corpus session.
