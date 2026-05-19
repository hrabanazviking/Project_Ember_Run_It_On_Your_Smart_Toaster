# docs/research/

A working library of cutting-edge AI / computer-science / cognitive-science research distilled into project-relevant concept syntheses. Each document is a single technical idea — the idea, the mechanism, the literature, the evidence, the application to Runa, and what to watch next.

## Purpose

The Architect and the Forge Worker reach into this folder when a slice begins. A doc here does not *bind* any subsystem; it gives the slice's author a fast, dense, opinionated read on the state of the art around the subsystem in question.

This folder is **research**, not design. Things in `docs/design/` are Volmarr's own design explorations and the imported design-harvest docs. Things here are externally-anchored — concepts that exist in the wider literature, presented in a form that connects them to Runa's architecture.

## Per-document template

Every research doc follows the same seven-section structure so a reader can scan or read deeply with equal ease:

1. **Core idea** — 1–2 paragraphs in plain language. Read this if you have 30 seconds.
2. **Technical depth** — algorithms, mechanisms, equations where useful, ASCII diagrams where useful. Read this if you want to know how it works.
3. **Key works** — named papers / projects with authors and approximate year. Read this if you want to know who did the foundational work.
4. **Empirical results** — what's known, on what benchmarks, with what limitations. Read this if you want to know whether it works.
5. **Applicability to Runa** — which subsystem this informs, what slice would use it, what to avoid. Read this if you are about to write code.
6. **Open questions** — active research frontiers worth watching.
7. **References (curated)** — specific papers / repos / docs to read next.

## File naming

`NN-short-kebab-slug.md` where `NN` is a zero-padded number 01–50 matching the corpus index in `INDEX.md`. The numbers are *stable* — when a doc is superseded, its replacement gets a new number, and the old doc moves to `../archive/research/`. Numbers are never reassigned.

## How to read this folder

- Start at `INDEX.md` for the full topic map grouped by category.
- Each category section there links to the relevant docs.
- Cross-references between docs use `[[NN-slug]]` Wikilink-style; resolve them by file name.

## Quality standard

These documents are first-pass syntheses. They cite real, named work and try to be accurate about the state of the art as of late-2025 / early-2026. Where a date or attribution is uncertain it is marked honestly. Bibliographic precision is not the standard — *getting the reader to the right named thing* is the standard.

If you find an error, **add a dated correction note at the top of the affected doc** rather than rewriting silently. The corpus is append-only in spirit; corrections are visible.
