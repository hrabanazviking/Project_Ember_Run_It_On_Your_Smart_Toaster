# TASK: Hermes Codex — Mining Hermes Agent for Ember's Evolution

**Started:** 2026-05-22
**Owner:** Volmarr + six Mythic Engineering agents
**Status:** Authoring (parallel, six agents)

---

## Scope

Read the Hermes Agent codebase (NousResearch/hermes-agent, cloned to `/tmp/hermes-agent/`) and produce a structured corpus of **53+ technical MD documents** under `docs/hermes_codex/` that distill everything Hermes can teach us about making Ember:

- Massive, robust, self-healing, bug-resistant, crash-proof, efficient
- Cross-platform (Win/Linux/Mac/iOS/Android/Pi), able to use whatever performance the host offers
- Capable of multi-device orchestration when devices are available
- Possessing wide skills/tools/awareness/self-awareness, emotional & logical intelligence
- Inventive — introducing new methods that are efficient AND powerful

## Method

Six Mythic Engineering agents work in parallel, each scoped to a layer + role:

| Agent | Role | Layer | Docs | Folder |
|---|---|---|---|---|
| 1 | Skald | Vision | 5 | `docs/hermes_codex/00_vision/` |
| 2 | Architect | Domain | 10 | `docs/hermes_codex/10_domain/` |
| 3 | Cartographer | Interface (tracing) + Synthesis | 12 | `docs/hermes_codex/20_interface/`, `60_synthesis/` |
| 4 | Forge | Execution | 12 | `docs/hermes_codex/30_execution/` |
| 5 | Auditor | Verification + Interface (verification) | 11 | `docs/hermes_codex/50_verification/`, `20_interface/` |
| 6 | Scribe | Meta + cross-link maintenance | 3+ | `docs/hermes_codex/meta/` |

Each agent reads `docs/hermes_codex/meta/SHARED_CONTEXT.md` and `meta/MANIFEST.md` before starting.

## What Exists Now

- `/tmp/hermes-agent/` — full Hermes clone, 871k lines Python, 80+ modules
- `~/ai/ember/docs/hermes_codex/` — empty scaffold with subdirs ready
- `meta/SHARED_CONTEXT.md` — brief for all agents
- `meta/MANIFEST.md` — full doc list with slugs and one-line scopes
- This TASK file

## What Is Needed

- 53+ MD docs, each 1500–4000 words, technical, entertaining, insight-rich, ending with `## What This Means for Ember`
- Cross-links resolve (Scribe verifies on final pass)
- Concrete proposals for Ember's True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr) and Three Realms (Spark/Thread/Well)
- A `60_synthesis/65_SLICE_PLAN_REVISIONS.md` that **proposes** revisions to Ember's ratification-gated slice plan but does NOT modify it
- ADRs for the most consequential adoption decisions in `60_synthesis/66_DECISION_RECORDS.md`

## Non-Goals

- Do NOT modify Ember source code
- Do NOT modify existing Ember docs outside `docs/hermes_codex/`
- Do NOT modify the slice plan (propose-only)
- Do NOT paraphrase Hermes's marketing copy — cite real source files and line numbers
- Do NOT invent Hermes features that aren't in the code

## Vows Honored

- **Smallness**: every Ember proposal must remain Pi-runnable in its baseline form
- **Tethered Grounding**: Hermes's memory tricks must integrate with Ember's external Well, not replace it
- **Graceful Offline**: anything network-dependent must fail honestly
- **Pluggable Storage**: no proposal locks Ember to a single backend
- **Modular Authorship**: any borrowed subsystem must be optional / individually failable
- **Public-Friendliness**: anything user-facing must remain readable
- **Flexible Roots**: no absolute paths anywhere
- **Open Knowledge**: MIT-friendly recommendations only

## Next Steps After Authoring

1. Volmarr reviews `60_synthesis/65_SLICE_PLAN_REVISIONS.md` and `66_DECISION_RECORDS.md`
2. Ratification of any proposed changes per the ratification gate
3. Scribe writes a final `meta/INDEX.md` once all docs are in place
4. Codex becomes the source-of-truth for Hermes-inspired Ember evolution

## Continuation Notes

If an agent runs out of budget mid-doc, it leaves a `## Continuation Notes` block at the bottom of its current doc, and the Scribe (or a follow-up Forge instance) picks it up.
