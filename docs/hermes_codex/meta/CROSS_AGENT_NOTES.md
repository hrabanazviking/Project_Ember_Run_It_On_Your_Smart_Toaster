---
codex_id: CROSS_AGENT_NOTES
title: Cross-Agent Notes — Scratch Pad for Inter-Author Pollination
role: Scribe
layer: Meta
status: draft
hermes_source_refs: []
ember_subsystem_targets: []
cross_refs:
  - meta/SHARED_CONTEXT
  - meta/MANIFEST
---

# Cross-Agent Notes

*A shared scratch pad for the six Mythic Engineering authors of the Hermes Codex.*

This document exists because the authors do not see each other's drafts during a single authoring wave. When one of us reads something in Hermes that would be more usefully said in **another** author's doc, we leave the thought here rather than reaching across role boundaries. The Scribe sweeps this file at the close of each wave and either: (a) confirms the note has been absorbed into the target doc, or (b) preserves it as a `## Continuation Notes` block on the next wave.

This is the only doc in the Codex where everyone has write access. Be brief. Be precise. Cite a Hermes path. Suggest a target doc.

---

## How to Use This File

### When to leave a note
- You found something in Hermes that belongs in another author's layer.
- You spotted a contradiction between two layer drafts (or two of your own claims).
- You want to flag a *risk* that the Auditor should pick up.
- You realised a True Name reassignment is needed; the Cartographer's `61_TRUE_NAME_REASSIGNMENT` should hear it.
- You think a doc should *not* exist as currently scoped, or should split, or should merge.

### When *not* to leave a note
- For thoughts that belong inside your own doc — just write them there.
- For typos in another doc — leave those for the Scribe's final pass.
- For praise — keep momentum; speak through the work.

### Format
Each note is a fenced block with three required fields and a free-form body:

```
### NOTE [date] from [author] → [target author or doc]
Hermes ref: <repo-relative path:lines>
Suggested target doc: <codex_id>
Body:
  <one paragraph or short bullet list>
```

A note is "absorbed" when its content appears in the target doc. The Scribe marks absorbed notes with `[absorbed in <doc> on <date>]` and moves them to the **Absorbed** section at the bottom (kept for traceability). Unabsorbed notes carry forward; if they linger more than two waves, the Scribe escalates them in `CONTINUATION_BACKLOG`.

### Hard rules
- **Never edit another author's note**, except to mark it absorbed.
- **Never delete a note**, even after absorption — move it to **Absorbed**.
- **Never use this file as a chat channel** — for discussion-style exchanges, file a real ADR under `docs/decisions/` (outside the Codex).

---

## Open Notes (most recent first)

*(empty — Wave 1 has not produced any cross-pollination notes yet)*

---

## Notes by Author Track

The sections below are pre-allocated so each author has a clear inbox. Put a note under the *target* author's section — that's where they will look.

### → Skald (Sigrún Ljósbrá) — Vision

*Notes for the visionary poet. Themes: framing, naming, essence, philosophy. If you've found something in Hermes that needs to be reframed as story before it becomes architecture, drop it here.*

(none yet)

### → Architect (Rúnhild Svartdóttir) — Domain

*Notes for the dark strategist. Themes: structure, boundaries, decomposition, dependency. If you've found a Hermes module that the Architect should treat as load-bearing (or, conversely, a module they've over-weighted), drop it here.*

(none yet)

### → Cartographer (Védis Eikleið) — Interface (tracing) + Synthesis

*Notes for the grounded oracle. Themes: maps, flows, glossaries, cross-walks, migration paths. If you've found that a Hermes pattern maps to a True Name in a way the Cartographer hasn't yet seen, drop it here.*

(none yet)

### → Forge (Eldra Járnsdóttir) — Execution

*Notes for the fire-worker. Themes: code patterns to lift, momentum, implementation, the "how" of any borrowed idea. If you spotted a Hermes function whose shape Ember should mirror, drop the file + line range here so the Forge can read it cold.*

(none yet)

### → Auditor (Sólrún Hvítmynd) — Verification + Interface (verification)

*Notes for the cold mirror. Themes: bugs, contradictions, risks, anti-patterns, security holes, scrutiny. If you saw something in Hermes that scares you — or contradicts what another author claimed — drop it here.*

(none yet)

### → Scribe (Eirwyn Rúnblóm) — Meta

*Notes for the archivist. Themes: cross-link gaps, missing frontmatter, doc-list disagreements, naming drift, manifest updates. If a doc you wrote needs the Scribe to verify a cross-link or update the manifest, drop the note here.*

(none yet)

---

## Themes to Watch

The Scribe will use this section to track recurring concerns across the Codex — things multiple authors are circling that may deserve a dedicated doc on the next wave.

| Theme | First raised by | Docs that touch it | Status |
|---|---|---|---|
| *(none yet)* | | | |

---

## Absorbed Notes (Archive)

When a note has been absorbed into its target doc, the Scribe moves it here with an absorption stamp. Nothing is ever deleted — this is the lineage trail.

*(empty)*

---

## Final Pass Checklist (Scribe-owned)

At the close of each authoring wave, the Scribe walks this checklist:

- [ ] Every Open Note has either been absorbed or has a clear reason for carrying forward.
- [ ] Every Absorbed Note carries a doc-id and date stamp.
- [ ] No author has more than three notes addressed to them that are older than the current wave.
- [ ] The Themes to Watch table reflects the actual state of cross-pollination.
- [ ] `meta/CONTINUATION_BACKLOG.md` has been updated with any unresolved themes.

---

## What This Means for Ember

This file does not directly affect any True Name. It protects the Codex from the silent failure mode all parallel-author projects suffer: *one author finds the truth, but writes it in the wrong room.* The Vow of the Unbroken Whole is honoured here too — the whole work must hang together, not just the individual docs. Cross-pollination is how that wholeness is maintained when six minds write at once.
