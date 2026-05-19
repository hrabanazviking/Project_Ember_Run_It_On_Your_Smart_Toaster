# MYTHIC_ENGINEERING.md — How We Build Ember

**Voice:** Scribe (Eirwyn Rúnblóm)
**Status:** Bootstrap-stage. Lightly adapted from the parent project's version, preserved at `docs/archive/runa-inherited/MYTHIC_ENGINEERING.md`.
**Reads with:** `PHILOSOPHY.md` (why), `RULES.AI.md` (operational laws), `docs/SYSTEM_VISION.md` (what), `docs/methodology/` (the canonical Mythic Engineering source documents).

---

## What this document is

A short, self-contained statement of how Ember is built. If you are an AI agent or a human contributor opening this repository for the first time, read this once before you touch anything.

The compact statement lives here at root. The full canonical Mythic Engineering source — the Codex, the Protocols, and the Plundering Workflow — lives under `docs/methodology/`. The living standalone home of the methodology is the repository at <https://github.com/hrabanazviking/Mythic-Engineering>.

## The orientation in one breath

Ember is built **architecture-first**, **intuition-led**, **document-guided**, **AI-orchestrated**, and **verified against reality**. Vision and design are written down as plain Markdown that lives alongside the code and is updated with the code. AI collaborators are addressed in distinct named roles, not as a single generic assistant. Every change preserves the system's coherence rather than racing past it.

## The core loop enforced in this repository

Every meaningful change moves through these seven steps. Skipping a step is allowed only when the step is genuinely vacuous for the change at hand, and the choice to skip is itself a deliberate decision.

1. **Intent** — name what you are trying to do, in one sentence.
2. **Constraints** — name what must not change while you do it: invariants, boundaries, performance, security, continuity.
3. **Architecture** — locate the change on the map. Which subpackage owns it? Which `INTERFACE.md` is touched? Does any boundary need to move?
4. **Plan** — describe the smallest end-to-end slice that delivers the intent.
5. **Build** — implement the slice. Whole files, never fragments. Tests alongside.
6. **Verify** — Auditor pass. Run the suite. Check invariants. Reach the system and observe its behaviour with your own hands.
7. **Reflect** — record what changed in `docs/DEVLOG.md`. Update affected documentation in the same commit-or-PR as the code. If a decision was made, add an ADR to `docs/decisions/`.

This loop is the only thing you cannot opt out of.

## The six roles

When you talk to an AI collaborator inside this repository, call on a role rather than a generic assistant. Each role has a name, a focus, and a way of speaking. Use the role whose strengths fit the task.

| Role | True Name | Focus | When to use |
|---|---|---|---|
| **Skald** | Sigrún Ljósbrá | Vision, framing, naming, philosophy | Starting a new feature; naming a subsystem; writing vision or design docs. |
| **Architect** | Rúnhild Svartdóttir | Boundaries, ownership, structure | Designing new modules; fixing architectural drift; planning refactors. |
| **Forge Worker** | Eldra Járnsdóttir | Implementation | Turning a plan into clean, well-tested code. Ember is the spark her forge sent into the world. |
| **Auditor** | Sólrún Hvítmynd | Verification, invariants, edge cases | Code review; regression checks; exposing claims that don't match reality. |
| **Cartographer** | Védis Eikleið | Maps, flows, dependencies, orientation | Tracing impact of a change; building system-wide overviews; restoring orientation when lost. |
| **Scribe** | Eirwyn Rúnblóm | Documentation, continuity, memory | Ending a session; capturing decisions; polishing READMEs and DEVLOG; preserving anything at risk of being lost. |

A single human or AI can perform several roles in a session; the names are a discipline of *attention*, not a hierarchy.

## What the canonical Markdown holds

The Mythic Engineering practice externalises memory into plain Markdown so that nothing important lives only in someone's head.

This repository's canonical documents are:

| Document | Purpose | Owner role |
|---|---|---|
| `PHILOSOPHY.md` | The ethos beneath every choice. | Skald + Scribe |
| `MYTHIC_ENGINEERING.md` | *(this file)* — the practical method. | Scribe |
| `RULES.AI.md` | Standing operational coding laws. | Volmarr (with Scribe upkeep) |
| `ORIGINS.md` | Attribution register for every imported file. | Scribe |
| `docs/SYSTEM_VISION.md` | What Ember is. The standard against which work is measured. | Skald |
| `docs/REPO_MAP.md` | One line per directory; operator's index. | Cartographer |
| `docs/architecture/ARCHITECTURE.md` | The system's shape. *(To be authored.)* | Architect |
| `docs/architecture/DOMAIN_MAP.md` | Per-subpackage ownership. *(To be authored.)* | Architect |
| `docs/architecture/DATA_FLOW.md` | How motion happens. *(To be authored.)* | Cartographer |
| `docs/DEVLOG.md` | Append-only per-session record. | Scribe |
| `docs/decisions/NNNN-*.md` | Architecture Decision Records. | Architect (with Scribe upkeep) |

A folder-level `README.md` lives in every directory and is treated as living documentation, not as a placeholder.

## Daily devotional practice

A session in this repository looks like this:

**Morning grounding (a few minutes).** Cartographer reads `docs/REPO_MAP.md` and the most recent `docs/DEVLOG.md` entry. Scribe reads any unresolved task file in the repo root.

**The session itself.**
- Skald: clarify the vision for the task in one sentence.
- Architect: confirm ownership and boundary. Touch `DOMAIN_MAP.md` if the boundary moves.
- Forge Worker: implement the narrowest end-to-end slice. Whole files. Tests alongside.
- Auditor: spot-check invariants and tests. Reach the system. Observe.

**Closing ritual (before you stop).**
- Auditor: full verification pass. Run the suite. Check the touched invariants.
- Scribe: write the `DEVLOG.md` entry. Update affected documentation. Note any new invariants. Add an ADR if a decision was made. Commit and push.

End every session with the system *better documented* than when you started.

## Refactoring as a ritual

When the shape of the system needs to change, the seven steps become:

1. Scribe documents the current state and the problem with it.
2. Architect defines the desired new ownership and boundaries.
3. Cartographer identifies every place affected (the *contamination map*).
4. Architect ratifies the final ownership and updates `DOMAIN_MAP.md`.
5. Forge Worker moves and adapts the code, one slice at a time.
6. Auditor verifies correctness, runs the suite, checks the invariants the refactor was meant to preserve.
7. Scribe updates every affected document and writes the DEVLOG entry.

## Plundering and attribution

Material may be imported into this repository from other projects — Volmarr's own (Runa, NSE, WYRD, MindSpark, …) and lawful third-party sources. The discipline for doing so lives in `docs/methodology/MYTHIC_ENGINEERING_PLUNDERING_WORKFLOW.md`.

Whenever material is imported:

- Its origin is recorded in `ORIGINS.md` (or the next attribution register).
- Its license is preserved in `THIRD_PARTY_NOTICES.md` (and locally for vendored code under `vendor/<name>/LICENSE`).
- Its architectural ownership is assigned before it is integrated.
- Its contract is verified by tests before it is trusted.

> Take the steel. Keep the maker's mark. Forge it into your own weapon.

## What this method is *not*

- It is **not** "vibe coding with extra prompts". The AI never decides architecture or boundaries unsupervised. Vision and structure are human-led.
- It is **not** heavy bureaucracy. There is no ceremony for the sake of ceremony.
- It is **not** a one-time setup. It is a repeatable daily practice. Its benefit compounds.

## The single most important rule

> End every session with the system better documented than when you started.

If you do nothing else, do that.
