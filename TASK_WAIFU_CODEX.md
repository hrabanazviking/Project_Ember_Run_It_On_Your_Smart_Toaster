# TASK: Waifu Codex — Mining waifu-chat-starter-kit for Ember's Realtime Cloud Embodiment Axis

**Started:** 2026-05-25
**Owner:** Volmarr + six Mythic Engineering agents
**Status:** Authoring (parallel, six agents) — pending agent dispatch
**Branch:** `development`
**Sibling codexes:** `docs/hermes_codex/` (58 docs), `docs/peer_codex/` (scaffold), `docs/kloinn/` (57 docs), `docs/sap_codex/` (83 docs)

---

## Scope

Read the waifu-chat-starter-kit (`ZeroWeight-Engineering/waifu-chat-starter-kit`, cloned to `/tmp/waifu-chat-starter-kit/`) and produce a structured corpus of **15 content MD documents** under `docs/waifu_codex/` that distill what this small but focused kit teaches Ember about:

- **Realtime cloud avatar embodiment** — streaming audio/video to a cloud-rendered avatar via LiveKit + ZeroWeight SDK, contrasted with SAP's local VRM/Live2D approach
- **Dual-mode integration patterns** — the kit ships `BasicMode` (31 LOC, minimal embed) and `AdvancedMode` (188 LOC, custom UI with controls) as parallel examples
- **Avatar action vocabulary as a contract** — `embarrassed`, `dance`, `wave_hand` as a typed surface
- **Realtime presence trade-offs** — WebRTC latency, cloud-auth surface, mic capture posture, action protocol limits
- **What Ember's Andlit/Rödd realtime tier should look like** — when local embodiment isn't enough and cloud streaming is appropriate

The corpus is intentionally **smaller than SAP** (15 docs vs 83) because the source is intentionally **smaller** (846 LOC across 5 source files vs SAP's 36,000+ LOC). Honest 15+ docs beat padded 50+.

## Method

Six Mythic Engineering agents work in parallel, each scoped to a layer + role. Each reads `docs/waifu_codex/meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, and `meta/STYLE_GUIDE.md` before starting.

| Agent | Role | Layer | Docs | Folder |
|---|---|---|---|---|
| 1 | Skald — Sigrún Ljósbrá | Vision | 2 | `00_vision/` |
| 2 | Architect — Rúnhild Svartdóttir | Domain + Interface (architect-owned) | 3 + 2 = 5 | `10_domain/` + 2× `20_interface/` |
| 3 | Cartographer — Védis Eikleið | Synthesis (cartographer-owned) | 1 | 1× `60_synthesis/` |
| 4 | Forge — Eldra Járnsdóttir | Execution | 2 | `30_execution/` |
| 5 | Auditor — Sólrún Hvítmynd | Verification + Interface (auditor-owned) | 3 + 1 = 4 | `50_verification/` + 1× `20_interface/` |
| 6 | Scribe — Eirwyn Rúnblóm | Synthesis (scribe-owned) + final meta | 1 + 3 = 4 | 1× `60_synthesis/` + meta finalization |

Each agent owns its slugs from `meta/MANIFEST.md`. No two agents write the same file.

**Push cadence:** every agent writes files only. Orchestrator commits + pushes per layer (six commits) after all agents return. Scribe writes `meta/INDEX.md`, `meta/READING_ORDER.md`, and `meta/CROSS_AGENT_NOTES.md` in a follow-up pass after all content lands.

## What Exists Now

- `/tmp/waifu-chat-starter-kit/` — full clone, 7-commit repo, 846 LOC total, 5 source files
- `~/ai/ember/docs/waifu_codex/` — empty scaffold with subdirs ready
- This TASK file
- `meta/SHARED_CONTEXT.md` — briefing (next to write)
- `meta/MANIFEST.md` — 15-doc list with slugs and one-line scope (next to write)
- `meta/STYLE_GUIDE.md` — tone, length, citation, closer (next to write)

## What Is Needed

- **15 MD docs**, each **1,500–3,000 words** (tighter than SAP — small source = tight scope), technical, entertaining, insight-rich, ending with `## What This Means for Ember`
- **Citations to real source files with line numbers** — but treat the kit as **study-only** (no LICENSE file in repo)
- For Adopt/Adapt recommendations, prefer LiveKit (MIT) as the upstream — do not propose adopting kit code without license clarification
- Concrete proposals for Ember's **Andlit-realtime** and **Rödd-realtime** tiers
- Cross-references to `[[sap:1A_AFFECTION_DOMAIN]]`, `[[sap:11_AVATAR_DOMAIN]]`, `[[sap:32_AVATAR_RENDER_PIPELINE]]` for the local-VRM↔cloud-stream comparison

## Non-Goals

- Do NOT modify Ember source code
- Do NOT modify existing Ember docs outside `docs/waifu_codex/`
- Do NOT propose adopting kit code without license confirmation (Open Knowledge Vow)
- Do NOT paraphrase the kit's README — cite the actual 5 source files
- Do NOT invent kit features that aren't in the code

## Vows Honored

- **Open Knowledge** — kit has no LICENSE; study-only posture, prefer LiveKit (MIT) as adoptable upstream
- **Smallness** — every Ember proposal must remain Pi-runnable; cloud-tier features are explicitly *optional* on top
- **Tethered Grounding** — avatar state must integrate with Ember's Well, not live exclusively in a cloud session
- **Graceful Offline** — cloud avatar must fail gracefully to a local fallback (text, log, low-tier presence)
- **Pluggable Storage** — no proposal locks Ember to ZeroWeight specifically
- **Modular Authorship** — Andlit-realtime is one of multiple presence modes, not the only one
- **Public-Friendliness** — user surface must remain readable
- **Flexible Roots** — no absolute paths
- **Surface Without Surveillance** *(SAP-proposed)* — mic capture + cloud streaming must carry explicit, revocable scope
- **Affective Restraint** *(SAP-proposed)* — avatar action vocabulary must respect consent

## Next Steps After Authoring

1. Volmarr reviews `60_synthesis/60_REALTIME_TIER_FOR_ANDLIT.md` and `61_DECISIONS_AND_INVENTIONS.md`
2. Per-layer commits + push (6 commits)
3. Final Scribe pass: `meta/INDEX.md` + `meta/READING_ORDER.md` + `meta/CROSS_AGENT_NOTES.md`
4. DEVLOG entry
5. Memory updates

## Continuation Notes

If an agent runs out of budget mid-doc, leave a `## Continuation Notes` block at the bottom and save what you have.
