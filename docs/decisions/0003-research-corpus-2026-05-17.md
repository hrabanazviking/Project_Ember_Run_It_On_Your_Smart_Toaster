# ADR 0003 — Research Corpus (50 Technical Documents)

**Date:** 2026-05-17 (same day as ADR-0001 and ADR-0002)
**Status:** Accepted
**Authors:** Volmarr Wyrd (commissioning), Runa Gridweaver Freyjasdottir (writing)
**Supersedes:** *(none)*
**Superseded by:** *(none)*
**Related:** [ADR 0001](./0001-mythic-engineering-bootstrap-2026-05-17.md), [ADR 0002](./0002-initial-subsystem-decisions-2026-05-17.md)

---

## Context

Following the bootstrap (ADR-0001) and the subsystem implementation decisions (ADR-0002), Volmarr requested a substantial research corpus distilling the most cutting-edge AI / computer-science / cognitive-science / memory / data-science work relevant to Runa's architecture. The intent: a project-local reference library the Architect and the Forge Worker can draw from when slices begin, and the corpus that an AI collaborator new to the repo can read to come up to speed on the technical context.

The corpus was produced as a single autonomous session, 50 documents in 10 batches of 5, with commit + push between every batch so progress was durable against context limits or interruption. Each document followed a fixed seven-section template (Core idea, Technical depth, Key works, Empirical results, Applicability to Runa, Open questions, References) to ensure depth without templated sameness.

## Decisions

### D-3.1 — Adopt the 50-document research corpus as project-local reference material

The 50 documents under `docs/research/01-…` through `docs/research/50-…` are accepted as project-local reference material. They are *not* binding architectural decisions — those live in ADR-0001 and ADR-0002 and future per-slice ADRs. The research corpus is *informative*: it explains the concepts, names the literature, and maps each concept to the Runa subsystem(s) it informs.

Reading order is flexible:
- A reader who wants to understand a specific subsystem (e.g. Muninn) reads the docs that map to it.
- A reader who wants to understand the field reads by category (the eleven categories in INDEX).
- A reader who wants to verify a specific decision in ADR-0001 or ADR-0002 follows back-references to the research docs that informed it.

### D-3.2 — Use the seven-section template for any future research additions

The template (in `docs/research/README.md`) is the standard shape:

1. **Core idea** — plain-language 1-2 paragraphs.
2. **Technical depth** — mechanism, equations, ASCII diagrams where useful.
3. **Key works** — named papers / projects with author + year.
4. **Empirical results** — what's known and on what evidence.
5. **Applicability to Runa** — which subsystem, what slice, what to avoid.
6. **Open questions** — research frontiers worth watching.
7. **References (curated)** — pointers for further reading.

New research docs added later follow this template. Variations require an addendum-and-reason in the doc; not by default.

### D-3.3 — Honest citation, no fabrication

Where attribution of a paper / author / date is certain, cite by name. Where uncertain, mark explicitly ("circa 2023", "as I recall", "verify"). Never fabricate a citation. Bibliographic precision is not the standard — *getting the reader to a real, findable named thing* is the standard.

The corpus as written cites real works to the best of the author's knowledge as of late-2025 / early-2026. Errors of date / attribution are inevitable in a 50-document survey written in a single session; corrections take the form of dated notes at the top of affected docs, not silent rewrites.

### D-3.4 — Corpus integrates with Volmarr's parallel AI OS Research work

During the corpus production, Volmarr added `docs/AI_OS_Research/AI_OS_RESEARCH_2026.md` — a 442-line research doc on the broader AI-OS market landscape (Google Gemini/Googlebook, Microsoft Copilot+, Apple Foundation Models, MCP/AAIF, the OS-shaped research frontier). This doc complements the agent-architecture focus of the 50-doc corpus with current industry / standards / research signal.

`docs/research/INDEX.md` cross-references it under "Companion material." The two bodies of work are intended to be read together: the 50-doc corpus for the *enduring concepts*, Volmarr's piece for the *current state of the field*.

## Consequences

### Positive

- The Architect and Forge Worker have a single curated reading list per subsystem.
- New AI collaborators can be onboarded by pointing at relevant `docs/research/*.md` rather than re-explaining concepts.
- The corpus surfaces *open questions* per topic — places where Runa's design will need empirical investigation, not just literature.
- The corpus connects nearly every architectural decision in ADR-0001 and ADR-0002 to its supporting research, making the decisions auditable.
- Cross-references between docs (`[[NN-slug]]` wikilinks) make navigation natural; an interesting trail leads to related ideas.

### Negative

- 50 documents is a *lot* of reading. Operators with limited time will need to navigate selectively (INDEX is the entry point; the per-doc Applicability sections are the practical orientation).
- The literature evolves quickly. Specific tool versions, benchmark scores, library names will drift; the conceptual content holds longer. Re-survey every 6-12 months for areas under active development.
- Some docs (especially in cognitive-science territory — GWT, free-energy, strange loops) are interpretive rather than prescriptive. They give framing; they don't give specific algorithms.
- The "Applicability to Runa" sections sometimes overpromise — they describe how the concept *could* shape Runa's design, not how it *will*. Final implementation decisions belong in per-slice ADRs.

### Cost

50 documents × ~7 KB average = ~370 KB of new content. Roughly an evening of focused writing. 11 commits to development. No new dependencies; pure documentation.

## What this ADR does *not* decide

- Per-subsystem implementation slice plans. Those become individual ADRs when the slices begin.
- Future research corpus expansion (additional topics, deeper dives on existing topics). When and what is operator's choice.
- Reconciliation of the 50-doc corpus with Volmarr's `AI_OS_RESEARCH_2026.md` if the two ever conflict. They don't conflict at present; cross-references are sufficient.
- The maintenance cadence for re-surveying fast-evolving areas. Suggested every 6-12 months for areas like quantisation, model routing, MCP ecosystem; case-by-case for everything else.

## References

- `docs/research/INDEX.md` — full corpus map.
- `docs/research/README.md` — template + reading guide.
- `docs/AI_OS_Research/AI_OS_RESEARCH_2026.md` — Volmarr's companion piece.
- `TASK_runa_research_corpus.md` — the resumption anchor for the autonomous run.
- All 50 documents under `docs/research/01-…` through `docs/research/50-…`.
- `docs/DEVLOG.md` — entries for the research-corpus session.
