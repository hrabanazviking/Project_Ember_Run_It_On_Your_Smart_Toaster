# TASK: Super Agent Party Codex — Mining SAP for Ember's Embodiment, Reach, and Affect

**Started:** 2026-05-24
**Owner:** Volmarr + six Mythic Engineering agents
**Status:** Authoring (parallel, six agents) — pending user approval of manifest
**Branch:** `development`
**Sibling codexes:** `docs/hermes_codex/` (58 docs, Wave 1), `docs/peer_codex/` (10+ scaffold docs, Wave 2)

---

## Scope

Read the Super Agent Party codebase (`heshengtao/super-agent-party`, cloned to `/tmp/super-agent-party/`) and produce a structured corpus of **82 technical MD documents** under `docs/sap_codex/` that distill everything SAP can teach us about making Ember:

- **Embodied** — VRM avatars, Live2D, VTube Studio, VMC protocol, voice (TTS+ASR), expressive presence
- **Reachable** — 8 IM platforms (QQ/WeChat/Feishu/DingTalk/Telegram/Discord/Slack/WeCom), livestream bots (Bilibili/YouTube/Twitch), AI browser, computer control
- **Affective** — `affection_api` + `affection_system` + `behavior_engine` + `autoBehavior` — actual emotional state machine code
- **Pluralistic** — multi-role group chat, Tavern character cards, A2A interfaces, sub-agents
- **Performance-adaptive** — runs on 2-core/2GB minimum; scales up to multi-GPU workstation
- **Multi-device** — IM bots + livestream + browser + computer control = many simultaneous channels = many devices simultaneously
- **Self-healing, bug-resistant, crash-proof, cross-platform** — Win/macOS/Linux native + Docker + portable

The codex's deliverable is the foundation for Ember's next-generation capabilities: not by copying SAP, but by **understanding its choices, identifying its mistakes, and synthesizing better methods**.

## Method

Seven Mythic Engineering agents work in parallel (six roles, with **Forge running as two instances** since its execution queue doubled to absorb the per-IM-bot and per-livestream deep dives). Each reads `docs/sap_codex/meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, and `meta/STYLE_GUIDE.md` before starting.

| Agent | Role | Layer | Docs | Folder |
|---|---|---|---|---|
| 1 | Skald — Sigrún Ljósbrá | Vision | 5 | `00_vision/` |
| 2 | Architect — Rúnhild Svartdóttir | Domain + Interface (architect-owned) | 14 + 6 = 20 | `10_domain/` + 6× `20_interface/` |
| 3 | Cartographer — Védis Eikleið | Synthesis (cartographer-owned) | 6 | 6× `60_synthesis/` |
| 4 | Forge-A — Eldra Járnsdóttir (fire-instance) | Execution (core) | 12 | `30_execution/` core slugs |
| 5 | Forge-B — Eldra Járnsdóttir (iron-instance) | Execution (per-platform) | 11 | `30_execution/` IM bot + livestream subdocs |
| 6 | Auditor — Sólrún Hvítmynd | Verification + Interface (auditor-owned) | 10 + 6 = 16 | `50_verification/` + 6× `20_interface/` |
| 7 | Scribe — Eirwyn Rúnblóm | Synthesis (scribe-owned) + final meta | 7 + 3 = 10 | 7× `60_synthesis/` + meta finalization |

Each agent owns its slugs from `meta/MANIFEST.md`. No two agents write the same file.

**Push cadence:** every agent commits + pushes to `origin/development` once its layer is fully written. Scribe waits for all other layers to land before writing `meta/INDEX.md` and `meta/READING_ORDER.md`, then pushes.

## What Exists Now

- `/tmp/super-agent-party/` — full SAP clone, ~36k Python LOC + Electron main + skills + config (v0.4.2-preview)
- `~/ai/ember/docs/sap_codex/` — empty scaffold with subdirs ready
- This TASK file
- `meta/SHARED_CONTEXT.md` — briefing for all agents (next to write)
- `meta/MANIFEST.md` — 62-doc list with slugs and one-line scope (next to write)
- `meta/STYLE_GUIDE.md` — tone, length, citation, "What This Means for Ember" closer (next to write)

## What Is Needed

- **82 MD docs**, each 1,500–4,000 words (per-IM-bot and per-livestream subdocs may run 1,200–2,500), technical, entertaining, insight-rich, ending with `## What This Means for Ember`
- Citations to real SAP source files with line numbers — never paraphrase marketing copy
- Concrete proposals for Ember's True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr) revised in light of SAP findings
- Concrete proposals for **new** True Names if a SAP domain (e.g. affection, livestream, IM mesh) demands it
- **Propose-only** revisions to Ember's slice plan in `60_synthesis/67_SLICE_PLAN_REVISIONS.md`
- ADRs for the most consequential adoption decisions in `60_synthesis/68_DECISION_RECORDS.md`
- A cross-codex integration roadmap in `60_synthesis/69_INTEGRATION_ROADMAP.md` (SAP × Hermes × Peer × Yggdrasil × Stofa)
- A novel-methods doc (`60_synthesis/66_INVENTED_METHODS.md`) — patterns we invent that **did not exist** in SAP

## Non-Goals

- Do NOT modify Ember source code
- Do NOT modify existing Ember docs outside `docs/sap_codex/`
- Do NOT modify the slice plan (propose-only — ratification gate still applies)
- Do NOT paraphrase SAP's marketing copy — cite real source files and line numbers
- Do NOT invent SAP features that aren't in the code
- Do NOT copy SAP's gacha-style affection mechanics uncritically — analyze and reimagine
- Do NOT copy SAP's surveillance-adjacent IM defaults uncritically — document the threat model

## Vows Honored

Each agent works under Ember's existing Vows (drawn from `PHILOSOPHY.md`, `RULES.AI.md`, and the Hermes Codex):

- **Smallness** — every Ember proposal must remain Pi-runnable in its baseline form, even if scaled-up variants exist
- **Tethered Grounding** — affection state, memory, retrieval must integrate with the external Well, not duplicate it
- **Graceful Offline** — anything network-dependent (IM, livestream, cloud LLM) must fail honestly with offline fallback
- **Pluggable Storage** — no proposal locks Ember to a single backend
- **Modular Authorship** — every borrowed subsystem must be optional / individually failable / individually swappable
- **Public-Friendliness** — anything user-facing must remain readable to non-experts
- **Flexible Roots** — no absolute paths anywhere
- **Open Knowledge** — MIT-friendly recommendations only (SAP is AGPLv3 — cite, do not vendor)
- **Cache Discipline** *(proposed in Hermes Codex)* — every speculative cache has a TTL and an invariant check
- **Defended System Prompt** *(proposed in Hermes Codex)* — instructions enter via a typed surface, never via string concatenation

## Vows Newly Proposed by This Codex (to be argued in `60_synthesis/61_NEW_VOWS.md`)

- **Embodied Honesty** — avatar expression must reflect real internal state, not theatre
- **Surface Without Surveillance** — every reach (IM bot, livestream, computer control) carries explicit, revocable scope
- **Affective Restraint** — affection state may bias behavior but never override consent or safety
- **Tiered Presence** — Ember's reach scales down gracefully (full embodiment → text-only → log-only)
- **Federated Self** — multi-device orchestration treats each device as a peer, not a slave

## Next Steps After Authoring

1. Volmarr reviews `60_synthesis/67_SLICE_PLAN_REVISIONS.md`, `68_DECISION_RECORDS.md`, `69_INTEGRATION_ROADMAP.md`
2. Ratification of any proposed changes per the ratification gate
3. Scribe writes a final `meta/INDEX.md` and `meta/READING_ORDER.md` once all docs are in place
4. Cross-link audit (Scribe): every `[[slug]]` resolves
5. Codex becomes the source-of-truth for SAP-inspired Ember evolution
6. Wave 3 announcement in `docs/DEVLOG.md`

## Continuation Notes

If an agent runs out of budget mid-doc, it leaves a `## Continuation Notes` block at the bottom of its current doc, and a follow-up Forge or Scribe instance picks it up using the slug list in `meta/MANIFEST.md` as ground truth.

If a doc's scope grows beyond ~4,000 words, the agent splits it into `<slug>_A.md` / `<slug>_B.md` and updates `meta/MANIFEST.md` with a parallel entry — never silently truncating.
