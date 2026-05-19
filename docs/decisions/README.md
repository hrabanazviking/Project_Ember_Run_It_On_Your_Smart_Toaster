# docs/decisions/

Architecture Decision Records. One file per commitment. Append-only.

## ADR conventions

- Filename: `NNNN-short-kebab-case.md` where `NNNN` is a zero-padded sequence number (e.g. `0001-src-layout.md`).
- Status: `Proposed` → `Accepted` → `Superseded` (linking to the superseding ADR). Never `Rejected and deleted` — rejected proposals stay as `Rejected` so future contributors don't re-propose the same dead-end.
- Sections: **Context** (what made this decision necessary), **Decision** (the commitment, in plain language), **Consequences** (positive and negative; what is now harder, what is now possible).
- Cross-reference related ADRs by number.

## Imported material

- `HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` — lessons-learned from the Hermes/OpenClaw period. Acts as an informal anti-pattern register that several future ADRs will cite.

## Initial ADRs to write

`0001` — adoption of the `src/runa/` layout (decided 2026-05-17, this bootstrap).
`0002` — standing-owner-trust doctrine (no permission babysitting).
`0003` — true-name domain vocabulary (Bifröst, VERÐANDI, Skuld, Muninn, …).
