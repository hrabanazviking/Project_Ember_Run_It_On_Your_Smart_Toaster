# docs/python/

A working library of Python craftsmanship — patterns and techniques for building the most robust, error-correcting, self-healing, crash-proof, efficient, and stable Python software possible. Each document is a single technique: the idea, the implementation, the gotchas, the application to Runa, and what to watch.

## Purpose

The Forge Worker reaches into this folder when implementation begins. Where `docs/research/` covers *what to build* (architectural concepts from AI / CS / cognitive science), this folder covers *how to build it well in Python* — the engineering craft that turns a research-grade design into code that survives years of operation, restart cycles, network partitions, model timeouts, partial deliveries, and the long tail of operational reality.

This is research, not specification. Final implementation choices belong in per-slice ADRs.

## Per-document template

Every doc follows the same seven-section structure:

1. **Core idea** — 1–2 paragraphs in plain language.
2. **Technique / mechanism** — Python-specific. Code snippets where useful.
3. **Key works / libraries** — named PEPs, libraries, authors.
4. **Pitfalls and gotchas** — failure modes, common mistakes.
5. **Applicability to Runa** — which `src/runa/*` subpackage uses this and how.
6. **Open questions** — trade-offs, things to monitor over time.
7. **References (curated)** — further reading.

## File naming

`NN-short-kebab-slug.md` numbered 01–50, matching `INDEX.md`. Numbers are stable; superseded docs move to `../archive/python/`.

## How to read this folder

- Start at `INDEX.md` for the full topic map grouped by theme.
- Each theme links to its docs.
- Cross-references between docs use `[[NN-slug]]` Wikilink-style; resolve by file name.

## Quality standard

These are first-pass syntheses with code samples. The code should be *correct as written* when the reader copies it; the techniques cited are real, named, current Python practice as of late 2025 / early 2026. Where the ecosystem moves fast, dates and library versions are marked.

Errors get dated correction notes at the top of affected docs, not silent rewrites.

## Relationship to `docs/research/`

| `docs/research/` | `docs/python/` |
|---|---|
| Concepts from AI / CS / cognitive science | Python implementation craft |
| Why this is the right shape | How to build that shape well |
| Cites academic papers, frameworks | Cites PEPs, libraries, idioms |
| Architect's reading | Forge Worker's reading |

Some topics appear in both — asyncio, event sourcing, plugins — at different abstraction levels. The pair is intentional.
