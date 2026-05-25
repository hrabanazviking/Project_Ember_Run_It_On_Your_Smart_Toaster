---
codex_id: 69_INTEGRATION_ROADMAP
title: Integration Roadmap — SAP × Hermes × Peer × Yggdrasil × Stofa
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - "(cross-codex synthesis — no single SAP source; references the constellation)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/67_SLICE_PLAN_REVISIONS
  - 60_synthesis/68_DECISION_RECORDS
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# 69 — Integration Roadmap

> *Five corpora, one Ember. The roadmap is the path between them — not a straight line, but a braided one.*
> — Eirwyn Rúnblóm, weaving the threads

## 0. Posture — Cross-Codex Synthesis

This is the **last doc of the SAP codex's synthesis layer**. Its job is to look across the entire Ember documentation constellation — the Hermes Codex (Wave 1), the Peer Codex (Wave 2), the SAP Codex (Wave 3, this), the Yggdrasil integration design tree, and the Stofa TUI design tree — and sketch a **phased order** for how the proposals across all five become Ember code.

The doc is a *roadmap*, not a plan. Plans are slice-shaped, ratification-gated, file-level (see `[[6C_EMBER_WAVE_3_SLICE]]`). Roadmaps are *direction-shaped* — they say "here is the order in which the territory becomes legible," not "here is what gets implemented next Tuesday."

The roadmap has no ratification gate of its own. Each step on the roadmap that becomes a slice is gated separately. The roadmap exists to make the **sequencing question** legible: when proposal X from SAP and proposal Y from Hermes both want slice-3 space, which goes first?

---

## 1. The Constellation

Ember's documentation lives in five distinct corpora, each with its own voice, scope, and authoring discipline.

### 1.1 Hermes Codex (Wave 1)

**Source:** `~/ai/ember/docs/hermes_codex/` (58 docs).
**Subject:** Hermes Agent (Nous Research) — a large, sovereign, self-improving AI agent.
**What it taught:** the *pure LLM loop* — conversation loop discipline, skill subsystem, MCP integration, tool dispatch parallelism, typed retry exhaustion, memory provider plug-in, gateway architecture, TUI gateway, plugin framework, cron, multi-provider failover.
**True Names contributed:** confirmed the existing six; reserved Vinátta (memory provider future) and Gjallarhorn (platform plugin future).
**Vows contributed:** Cache Discipline, Defended System Prompt.
**Slice proposals:** slice 3 *Skilled, Bridged, Quiet* + slice 4 *Plural Minds, Plural Memories* (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`).
**ADR proposals:** 11 ADR-Proposed (per `[[hermes:66_DECISION_RECORDS]]`).

### 1.2 Peer Codex (Wave 2)

**Source:** `~/ai/ember/docs/peer_codex/` (scaffolded — final doc count TBD; references Letta, smolagents, Goose, possibly others).
**Subject:** alternative agent frameworks in the open-source ecosystem — Letta (sleep-time memory, archival/recall split), smolagents (lightweight CodeAct), Goose (developer-shaped agent CLI).
**What it taught:** alternative memory architectures (Letta's sleeper memory), lightweight tool calling (smolagents), terminal-resident developer-shaped patterns (Goose).
**True Names contributed:** likely additions in the memory and tool axes; final count after Wave 2 settles.
**Vows contributed:** TBD; the cross-comparison synthesis folder is the relevant reference.
**Slice proposals:** memory-provider plug-in (parallels Hermes Vinátta); possible additional tool-execution shapes.

### 1.3 SAP Codex (Wave 3, this)

**Source:** `~/ai/ember/docs/sap_codex/` (82 docs).
**Subject:** Super Agent Party — the embodiment + reach + affect axes that Hermes and Peer left unaddressed.
**What it teaches:** VRM/Live2D avatar pipeline, MOSS TTS + sherpa ASR voice stack, behavior engine, affection system (which we *reject* and reimagine), 8 IM bot pattern, 3 livestream platforms, computer control, the MCP-client supervisor shape.
**True Names contributed:** Andlit (face/avatar), Rödd (voice), Hugarsýn (introspection / meta-awareness) — per Cartographer's `[[60_TRUE_NAME_REASSIGNMENT]]`.
**Vows contributed:** Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self — per Cartographer's `[[61_NEW_VOWS]]`.
**Slice proposals:** revised slice 3 (per `[[67_SLICE_PLAN_REVISIONS]]`); new slice 4 *Felt, Visible, Awake*; revised slice 5; new slice 6 *Embodied at T0*; speculative slice 7 *Federated Self*; speculative slice 8 *Reach Beyond Self*.
**ADR proposals:** 12 ADR-Proposed (per `[[68_DECISION_RECORDS]]`).

### 1.4 Yggdrasil Integration Design Tree

**Source:** `~/ai/ember/docs/yggdrasil/` (the integration design for Ember + 11 sibling projects).
**Subject:** how Ember integrates with sibling projects — Bifröst (3D galaxy viewer), Skein (embedding-derived KG), Skry (query-time entity projection), Kista (secret plane), Mimir (knowledge plane), Seiðr (generation plane), CloakBrowser (web plane), Astrology (rhythm plane), and several more.
**Status:** design-only at the time of this doc. The architecture, the protocol layer, the 9 realms / planes are documented (`docs/yggdrasil/architecture/30-39`); phase roadmap exists (`docs/yggdrasil/roadmap/90-95`).
**Slice proposals:** Yggdrasil integration is *post-slice-7+*; the foundation must land before sibling integration begins. The Yggdrasil roadmap (5 phases: Roots → Branches → Crown → Network → Constellation) is its own roadmap, parallel to Ember's slice roadmap.
**Key integration:** Bifröst is the first sibling with a defined integration path. Skein + Skry consume the Brunnr/Gungnir Well. Mimir is conceptually adjacent to Brunnr.

### 1.5 Stofa TUI Design Tree

**Source:** `~/ai/ember/docs/tui/` (the design tree for Ember's terminal interface).
**Subject:** Ember's TUI — a "mead-hall" terminal experience replacing/extending the simple `ember chat` REPL.
**Status:** design-only. Architecture, screens (Home, Chat, Well, Doctor, Settings, MCP, Tool Approval, Hjarta Wizard), aesthetic (Viking-inflected), pets (Hugin raven, Geri-cub, Heiðrún mead-horn), and 4-phase roadmap (Hearth → Hall → Familiars → Feast) are documented.
**Slice proposals:** Stofa integration is its own slice roadmap parallel to Ember's. The Hearth phase is the smallest scope (basic TUI shell replacing `ember chat`); the Feast phase is the most ambitious (all screens, all pets, all overlays).
**Key integration:** Stofa is the *surface* of slices 3, 4, 5, 6 — when affect lands in slice 4 with glyph rendering, the glyph appears in Stofa's chat screen. When MCP lands in slice 3, the MCP screen renders the server status. Stofa is *tier-aware* per `[[6B_LOW_POWER_EMBODIMENT]]` (the Pi gets a smaller Stofa).

---

## 2. The Braided Sequence

The integration roadmap is **not** "do Hermes first, then Peer, then SAP." Each codex proposes work for *multiple* slices. The braiding question is: per slice, which threads from which codex land?

The proposed braid:

### Wave 3, Slice 3 — *Skilled, Bridged, Quiet, Tiered, Identified*

**Hermes threads:** skill subsystem (S3-A), provider profile + transport split (S3-B), MCP server (S3-C), tool parallelism + interrupt fan-out (S3-D), Strengr typed retry + exhaustion (S3-E).

**SAP threads:** tier ladder (S3-F), persona-id (S3-G), glyphic + log-affect (S3-H), failsafe-default-quiet standing rule (S3-I).

**Peer threads:** none direct; Peer-informed memory provider lands in slice 5 alongside Hermes's Vinátta.

**Yggdrasil threads:** none direct; persona-id is a foundation for future Yggdrasil identity but no Yggdrasil-specific work.

**Stofa threads:** Hearth phase preliminary work — the TUI shell that replaces `ember chat` can ship *with* slice 3 or *immediately after*. The glyph rendering from SAP-S3-H requires a UI surface that Stofa Hearth provides.

**Theme cohesion:** the slice braids Hermes-developer-shape (skills, MCP) with SAP-companion-shape (tier, persona, glyph) with cross-cutting standing rules (failsafe-default-quiet). The braid is coherent because each thread *enables* future threads — skill subsystem enables tier-conditional skill activation; persona-id enables tier-aware authority assignment in slice 7; glyph enables affect rendering in slice 4.

### Wave 3, Slice 4 — *Felt, Visible, Awake*

**SAP threads:** affect engine (S4-A per ADR-Proposed-SAP-002), sleep-guard (S4-B per SAP-006), overlay-manager (S4-C per SAP-009), sub-agent supervision (S4-D per SAP-012), backpressure overlay (S4-E).

**Hermes threads:** none direct; the Hermes slice-4 (Plural Minds) defers to Ember's slice 5.

**Peer threads:** sleeper-memory-shaped affect (parallel to SAP's affect engine; informs but does not overwrite).

**Yggdrasil threads:** Bifröst preliminary integration begins — the affect surface is one of the data sources Bifröst's galaxy view could render. *Preliminary only*; full Bifröst integration is slice 7+.

**Stofa threads:** Hall phase — full screens land (Well, Doctor, Settings, MCP, Tool Approval). The overlay-manager from SAP-S4-C powers Stofa's affect glyph display and backpressure overlays.

**Theme cohesion:** "Felt" = affect engine. "Visible" = overlay-manager broadcast surface. "Awake" = sleep-guard. Together: Ember becomes *perceptibly present* — operator sees her state, knows when she is working, can choose to keep the host awake while she does.

### Wave 3, Slice 5 — *Plural Minds, Plural Memories*

**Hermes threads:** MCP client (Hermes-S4-A), memory provider ABC (Hermes-S4-B, with Vinátta reservation), agent-initiated skill writes (Hermes-S4-C).

**SAP threads:** behavior engine (SAP-S5-A per ADR-Proposed-SAP-007), first IM bot (SAP-S5-B per SAP-010 — Telegram OR Discord, operator chooses one as the reference).

**Peer threads:** Honcho/Mem0 reference Vinátta plugins (optional opt-in extras parallel to Hermes-S4-B); Letta's sleeper-memory pattern informs but does not directly land.

**Yggdrasil threads:** Skein + Skry integration *begins*. The MCP client gives Ember a way to consume Skein-as-MCP-server. *Preliminary*; full Skein integration is later.

**Stofa threads:** Familiars phase — the text-mode pets land (Hugin, Geri-cub, Heiðrún). Pets are decorative AND helpful — Hugin perches on the Well counter; Heiðrún drops a mead-horn into the audit log when a tool fires. Pet-rendering depends on the overlay-manager from slice 4.

**Theme cohesion:** "Plural Minds" = MCP client (consume foreign agents). "Plural Memories" = memory provider plug-in (consume foreign brains). The behavior engine and first IM bot add the autonomous + reach dimensions that round out the "plural" theme.

### Wave 3, Slice 6 — *Embodied at T0*

**SAP threads:** VRM/Live2D pipeline (SAP-S6-A per ADR-Proposed-SAP-011), consent-token gating (SAP-S6-B), composition-first expression library (SAP-S6-C), cued voice library workflow (SAP-S6-D), avatar-as-backpressure (SAP-S6-E).

**Hermes threads:** none direct; embodiment is SAP-shaped territory.

**Peer threads:** none direct.

**Yggdrasil threads:** CloakBrowser preliminary integration — the avatar surface could render in a browser overlay window per the CloakBrowser realm.

**Stofa threads:** Feast phase — all screens, all pets, all overlays. The avatar surface integrates with Stofa's chat screen (the avatar can live in a tmux pane or a small Electron-shaped helper window alongside the TUI).

**Theme cohesion:** the visible-at-T0 slice. Operators who have followed slices 1-5 have a quietly competent companion; slice 6 makes her *embodied*. The slice is heavy because the avatar pipeline is heavy.

### Wave 3, Slice 7 — *Federated Self*

**SAP threads:** inter-instance MCP peering (SAP-S7-A per `[[6A]]#1, #2`), cross-host affect router (SAP-S7-B per `[[66]]#1`), lid-close handover (SAP-S7-C per `[[66]]#4`), per-utterance arbitration (SAP-S7-D per `[[6A]]#6, #8`), operator party console (SAP-S7-E per `[[6A]]#10`).

**Hermes threads:** none direct.

**Peer threads:** none direct.

**Yggdrasil threads:** **Significant**. Slice 7's persona-aware multi-instance work is the foundation for Yggdrasil's "9 realms / many planes" integration. The persona-id from slice 3, the multi-instance party from slice 7, and the Yggdrasil protocol layer (`docs/yggdrasil/architecture/31`) converge here. Bifröst integration matures.

**Stofa threads:** Stofa gains multi-instance awareness — the party console screen shows the swarm.

**Theme cohesion:** the federated-self slice. Ember becomes plural across hosts. Operator authority remains central; each instance is a peer.

### Wave 3, Slice 8+ — *Reach Beyond Self*

**SAP threads:** additional IM bots (SAP-S8-A — Discord, Slack, Telegram, Feishu, DingTalk, WeChat, WeCom, QQ — one per phase), livestream platforms (SAP-S8-B — Bilibili, YouTube, Twitch — one per phase), quiet-hours throttling (SAP-S8-C), stream-truncation confession (SAP-S8-D).

**Hermes threads:** none direct.

**Peer threads:** none direct.

**Yggdrasil threads:** CloakBrowser (web plane), Seiðr (generation plane) — sibling-project integration matures. Mimir (knowledge plane) integration completes Brunnr's parallel relationship with the broader Norse cognition tree.

**Stofa threads:** Stofa screens for each new IM bot and livestream platform.

**Theme cohesion:** Ember reaches the full ecosystem. Most operators will never need all 8 IM platforms or all 3 livestream platforms — these are *territory* that operators activate piecemeal as their needs grow.

---

## 3. The Yggdrasil Roadmap × Ember Slice Roadmap

Yggdrasil has its own 5-phase roadmap (per `docs/yggdrasil/roadmap/90-95`):

- Phase 1 — The Roots (basic protocol layer, identity, secrets).
- Phase 2 — The Branches (sibling registration, capability discovery).
- Phase 3 — The Crown (cross-realm queries, federated retrieval).
- Phase 4 — The Network (multi-host Yggdrasil mesh).
- Phase 5 — The Constellation Ratified (full integration; all sibling projects accessible).

**Mapping to Ember slices:**

- **Yggdrasil Phase 1 (Roots)** lands in **Ember slice 4-5**. Foundation: persona-id from slice 3, MCP client from slice 5, memory provider from slice 5.
- **Yggdrasil Phase 2 (Branches)** lands in **Ember slice 7**. Sibling registration uses the same persona-table machinery as multi-Ember party.
- **Yggdrasil Phase 3 (Crown)** lands in **Ember slice 8-9**. Cross-realm queries: Brunnr extending to Skein/Skry/Mimir.
- **Yggdrasil Phase 4 (Network)** lands in **Ember slice 10+**. Multi-host Yggdrasil mesh: builds on the federated self machinery.
- **Yggdrasil Phase 5 (Constellation Ratified)** is the asymptote: when all 11 siblings are integrated. Many years out.

**The braid:** Yggdrasil's roadmap is *slower* than Ember's slice cadence. One Yggdrasil phase spans several Ember slices. The sequencing must respect both — Ember slices that touch Yggdrasil territory must wait for the corresponding Yggdrasil phase, and Yggdrasil phases that depend on Ember features must wait for the corresponding slice.

---

## 4. The Stofa Roadmap × Ember Slice Roadmap

Stofa has its own 4-phase roadmap (per `docs/tui/roadmap/99_*`):

- Phase 1 — The Hearth (basic TUI shell; replaces `ember chat`).
- Phase 2 — The Hall (full screens: Well, Doctor, Settings, MCP, Tool Approval, Hjarta Wizard).
- Phase 3 — The Familiars (text-mode pets land).
- Phase 4 — The Feast (all overlays, animations, the full mead-hall experience).

**Mapping to Ember slices:**

- **Stofa Phase 1 (Hearth)** ships **with or after Ember slice 3**. The TUI shell is the surface for glyph rendering (SAP-S3-H) and tier-conditional wizards (SAP-S3-F).
- **Stofa Phase 2 (Hall)** ships **with or after Ember slice 4**. The full screens depend on the overlay-manager from SAP-S4-C and the affect introspection from SAP-S4-A.
- **Stofa Phase 3 (Familiars)** ships **with or after Ember slice 5**. Pets depend on the behavior engine from SAP-S5-A — Hugin perches when the Well is being read; Heiðrún drops a mead-horn when a tool fires.
- **Stofa Phase 4 (Feast)** ships **with or after Ember slice 6**. The full mead-hall experience includes avatar surface integration (SAP-S6-A).

**The braid:** Stofa is the *front* of Ember's slice work — every backend slice should have a Stofa-visible surface as part of acceptance. This means the slice plan owner (Architect + Forge) and the Stofa-design owner (Scribe + Skald, possibly) coordinate slice-by-slice.

The simplest coordination: every slice's acceptance criterion includes one Stofa-side test. Slice 3 includes "the glyph appears in Stofa's chat screen header." Slice 4 includes "the affect introspection screen renders correctly." Etc.

---

## 5. The Cross-Codex Conflict Register

Where do the codexes disagree? What does the keeper resolve?

### 5.1 Affect engine — SAP-canonical

**Conflict:** Hermes is silent on affect (Hermes Agent has no affect). Peer-Letta has sleeper-memory-shaped state that *partly* overlaps affect. SAP-canonical proposal is the tethered affect engine with anchoring, introspection, provisional tray.

**Resolution:** the SAP-derived affect engine (per ADR-Proposed-SAP-002 and `[[64_AFFECTION_ENGINE_REIMAGINED]]`) is canonical. Letta's sleeper memory informs the *memory provider plug-in* (slice 5), not the affect engine. The two are *adjacent* but *distinct* surfaces.

### 5.2 Memory provider — Hermes + Peer convergent

**Conflict:** Hermes proposes Vinátta (memory provider plug-in ABC). Peer-Letta proposes a sleeper-memory pattern. Peer-Honcho proposes an external brain service. SAP is silent (SAP has no equivalent surface).

**Resolution:** the Hermes Vinátta plug-in ABC is canonical. Letta, Honcho, and Mem0 become reference plugins shipped as optional extras (`ember-agent[vinatta-letta]`, `ember-agent[vinatta-honcho]`, `ember-agent[vinatta-mem0]`). Each is a documented integration point; none is the default.

### 5.3 Tool dispatch — Hermes-canonical

**Conflict:** Hermes proposes rules-engine parallelism with interrupt fan-out. SAP's sub-agent supervision provides related primitives. Peer-smolagents proposes CodeAct (tools as Python expressions, executed in a sandbox).

**Resolution:** Hermes's parallelism rules engine is canonical for tool *dispatch*. SAP's sub-agent supervisor is canonical for *subprocess* supervision (per ADR-Proposed-SAP-012). Smolagents-CodeAct is a *distinct* execution model that could ship later as an alternate Smiðja runtime (deferred indefinitely).

### 5.4 MCP — Hermes + SAP convergent

**Conflict:** none. Both Hermes and SAP converge on MCP. The Hermes proposal for Ember-as-MCP-server is canonical (slice 3). The Hermes proposal for Ember-as-MCP-client is canonical (slice 5). SAP's mcp_clients.py pattern informs the *supervisor* shape used in both.

**Resolution:** Hermes-canonical for MCP integration; SAP-informed for subprocess supervisor reuse.

### 5.5 Skills — Hermes-canonical

**Conflict:** none direct. Hermes proposes the skill subsystem; SAP's agent skills (`skills.py`) is adjacent but different (SAP's skills are extension-like). Peer-Letta has no equivalent.

**Resolution:** Hermes-canonical for skills. SAP's skill concept is *not* adopted; the term "skill" in Ember refers to the Hermes-shape.

### 5.6 Avatar — SAP-canonical

**Conflict:** Hermes has no avatar. Peer has no avatar. SAP-canonical for the entire embodiment axis.

**Resolution:** SAP-derived avatar pipeline lands in slice 6.

### 5.7 IM bots / livestream / reach — SAP-canonical

**Conflict:** Hermes has IM-bot-shaped patterns (the gateway/run.py shape) but smaller scope. SAP-canonical for the 8-platform pattern.

**Resolution:** SAP-derived per-persona IM fallback shape (per ADR-Proposed-SAP-010). One reference IM bot in slice 5; additional platforms in slice 8+.

### 5.8 Tier ladder — SAP-canonical

**Conflict:** none. Neither Hermes nor Peer addresses the tier question directly.

**Resolution:** SAP-canonical. The tier ladder (T0/T1/T2/T3/T4) is named in `[[6B_LOW_POWER_EMBODIMENT]]` and ratified in slice 3.

### 5.9 Persona-id — SAP-canonical

**Conflict:** none. Neither Hermes nor Peer addresses identity.

**Resolution:** SAP-canonical. Persona-id issuance per ADR-Proposed-SAP-005 lands in slice 3.

### 5.10 Standing rules — additive across codexes

Hermes proposes Cache Discipline and Defended System Prompt. SAP proposes Failsafe-Default-Quiet. Peer proposes (TBD — likely something around memory-state hygiene).

**Resolution:** all are additive. Each becomes a standing rule in the relevant slice ratification. Slice 3 adopts Failsafe-Default-Quiet. Slice 4 may adopt Cache Discipline. Slice 5 may adopt Defended System Prompt (or earlier — defended system prompt is wanted by every slice that touches prompt assembly).

---

## 6. The Five-Year Trajectory

If everything proposed across all five corpora becomes Ember code, what does Ember look like in five years?

**Year 1 (now → +12 months):** slices 3, 4, 5 ship. Ember is *skilled, bridged, quiet, tiered, identified, felt, visible, awake, plural-minded, plural-memoried, autonomous-but-restrained*. Stofa Hall is the surface. Yggdrasil Roots phase is complete. The Pi 5 has a meaningful Ember presence.

**Year 2 (months +13 → +24):** slices 6 and 7 ship. Ember is *embodied at T0* (VRM avatar with consent gating, cued voice library, composition-first expression). Ember is *federated* (multi-instance party across the operator's tailnet; lid-close handover; cross-host affect; operator party console). Stofa Familiars and Feast phases ship. Yggdrasil Branches phase is complete. Bifröst integration matures.

**Year 3 (months +25 → +36):** slice 8 begins. Additional IM bots and livestream platforms land per operator demand. Yggdrasil Crown phase is in progress. Skein + Skry full integration completes. The first sibling-project-as-realm experience is operational.

**Year 4 (months +37 → +48):** Yggdrasil Network phase. Multi-host Yggdrasil mesh. Ember runs across many devices belonging to many people on a shared trust mesh (with explicit consent gating per `[[66_INVENTED_METHODS]]#6` and the entire `[[6A_MULTI_AGENT_PARTY]]` framework).

**Year 5 (months +49 → +60):** Yggdrasil Constellation Ratified. Full sibling integration: Mimir, Seiðr, CloakBrowser, Astrology, Kista — each accessible as a realm via the Yggdrasil protocol. Ember is *the most capable, robust, self-healing, cross-platform Norse AI agent ever built* (the language from `docs/yggdrasil/INDEX.md`).

This is an *asymptote*, not a forecast. The trajectory will adjust as operator demand, ecosystem evolution, and individual codex revisions accumulate. The roadmap exists to make the sequencing *visible*, not to commit any of it.

---

## 7. Risks to the Roadmap

| Risk | Mitigation |
|---|---|
| One codex's proposal blocks another's (e.g. Hermes Vinátta and Peer-Letta memory shapes conflict at the API boundary) | Conflicts surface in the keeper's review of slice plans. Where unavoidable, the slice plan picks one canonical and notes the other as deferred alternative. |
| Yggdrasil and Ember slice cadences misalign — Ember slice 7 needs Yggdrasil Phase 2 but Yggdrasil is still in Phase 1 | The roadmap is *advisory*. Slices ship when their dependencies are met. If Yggdrasil Phase 2 is late, Ember slice 7 either waits or ships a smaller scope that does not depend on Yggdrasil. |
| Stofa-side work is undersized in the slice plan because it's "just UI" | Every slice acceptance criterion includes at least one Stofa-side test. The Stofa work is *part of* the slice, not after it. |
| The cross-codex conflict register (§5) misses a conflict | The keeper review uses this doc as one input; the keeper also reads each codex directly. New conflicts get appended. |
| Operator demand inverts the proposed slice order (e.g. operators want avatar before federation) | The roadmap is not contractual. Slice plan keeper has authority to re-order. The roadmap exists to document the proposed order, not to lock it. |
| A codex grows after this doc is written (Wave 4, etc.) and adds new threads | This doc is a Wave-3-snapshot. Wave 4's analogous doc would supersede this in cross-codex sequencing. |
| Sibling projects evolve independently and their integration shape changes | Yggdrasil's design tree is itself a living document. Re-survey at slice-7 ratification time. |

---

## 8. The Roadmap as a Single Picture

```
                           Ember Wave 3 Slice Roadmap
                                  (proposed)

   Slice 2 ──────────────────────────────────────────────────── shipped
       │
       │  Hermes  Hermes  SAP   SAP   SAP   SAP                 H = Hermes
       ▼  ┌───┐   ┌───┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐                  S = SAP
   Slice 3 │S-A│   │S-B│   │F│   │G│   │H│   │I│ ────── propose   P = Peer
       │  └───┘   └───┘   └─┘   └─┘   └─┘   └─┘
       │   skill   prov   tier  pers  glyph quiet
       │   subs    split  ladd  id           rule
       │
       ▼  SAP    SAP   SAP   SAP   SAP
   Slice 4 ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐  ────────── propose
       │   │A│   │B│   │C│   │D│   │E│
       │   └─┘   └─┘   └─┘   └─┘   └─┘
       │  affect sleep over  sub   back
       │  engine guard lay   agent press
       │
       ▼  Hermes  Hermes  Hermes  SAP   SAP   P (info)
   Slice 5 ┌───┐   ┌───┐   ┌───┐   ┌─┐   ┌─┐   ┌────┐ ── propose
       │   │S4A│   │S4B│   │S4C│   │A│   │B│   │Honc│
       │   └───┘   └───┘   └───┘   └─┘   └─┘   └────┘
       │   MCP    mem     skill   beh   IM    Letta/Mem0
       │   clt    prov    write   eng   bot   reference plugins
       │
       ▼  SAP    SAP   SAP   SAP   SAP
   Slice 6 ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐  ────────── propose
       │   │A│   │B│   │C│   │D│   │E│
       │   └─┘   └─┘   └─┘   └─┘   └─┘
       │  VRM/   con-   compos cued  avatar
       │  Live2D sent   first  voice as
       │  pipe   gate   lib    lib   back-press
       │
       ▼  SAP    SAP   SAP   SAP   SAP   Yggdrasil
   Slice 7 ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌───────┐  ─── speculative
       │   │A│   │B│   │C│   │D│   │E│   │Branches│
       │   └─┘   └─┘   └─┘   └─┘   └─┘   └───────┘
       │  peer   xhost  lid   utt   party  yggdrasil
       │  MCP    affect close arb   conso  phase 2
       │
       ▼  SAP × N  Yggdrasil   Stofa
   Slice 8 ┌─────┐  ┌──────┐   ┌────┐  ────── speculative
   and on  │ +IM │  │ Crown│   │Feast│
           │+strm│  │ phase│   │     │
           └─────┘  └──────┘   └────┘
```

The diagram is schematic, not exact. Each box represents one ADR-Proposed thread. Slices grow from top to bottom. Time flows downward.

---

## 9. The Keeper's Roadmap Checklist

If the keeper accepts this roadmap as the basis of cross-codex sequencing:

1. Read `[[hermes:65_SLICE_PLAN_REVISIONS]]` and `[[hermes:66_DECISION_RECORDS]]` — the Hermes proposals.
2. Read `[[peer:65_SLICE_PLAN_REVISIONS]]` (when authored) — the Peer proposals.
3. Read `[[67_SLICE_PLAN_REVISIONS]]` and `[[68_DECISION_RECORDS]]` — the SAP proposals.
4. Read this doc (`[[69_INTEGRATION_ROADMAP]]`) — the cross-codex sequencing.
5. Decide which braided slice (§2) to ratify next.
6. Author the relevant slice plan in `docs/architecture/` per `[[6C_EMBER_WAVE_3_SLICE]]` (or its successor for later slices).
7. Ratify via the next-available ADR number.
8. Coordinate with the Yggdrasil and Stofa roadmap owners on parallel phasing.
9. Re-survey at each slice ratification: have any codexes grown? Have any conflicts surfaced? Update this doc accordingly (or supersede with a Wave-4 equivalent).

---

## 10. Cross-References

- `[[60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's True Name proposals across all axes.
- `[[61_NEW_VOWS]]` — Cartographer's new Vows that this roadmap respects.
- `[[66_INVENTED_METHODS]]` — invention catalogue that informs many slices.
- `[[67_SLICE_PLAN_REVISIONS]]` — SAP-side slice-plan proposals.
- `[[68_DECISION_RECORDS]]` — SAP-side ADR-Proposed records.
- `[[6C_EMBER_WAVE_3_SLICE]]` — the concrete slice-3 proposal.
- `[[6A_MULTI_AGENT_PARTY]]` — slice 7's design source.
- `[[6B_LOW_POWER_EMBODIMENT]]` — slice 3's tier ladder + slice 6's cued voice source.
- `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]` — Hermes-side gap analysis.
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — Hermes-side slice proposals.
- `[[hermes:66_DECISION_RECORDS]]` — Hermes-side ADRs.
- `[[peer:65_SLICE_PLAN_REVISIONS]]` (when authored) — Peer-side slice proposals.
- `[[ember:EMBER_SECOND_SLICE_PLAN]]` — the slice-2 plan all proposals build from.
- `[[ember:0013-second-slice-ratification]]` — the standing-rules ADR.
- Yggdrasil: `docs/yggdrasil/INDEX.md`, `docs/yggdrasil/roadmap/90-95`, `docs/yggdrasil/architecture/30-39`.
- Stofa: `docs/tui/INDEX.md`, `docs/tui/roadmap/99-*`, `docs/tui/screens/80-88`.

---

## What This Means for Ember

**True Names affected:** all six, across the 5-year trajectory. Funi most (slices 3, 5, 7). Munnr second-most (slices 3, 4, 6, 7, 8). Hjarta heavily (slice 4 affect, slice 7 cross-host affect). Brunnr heavily (Yggdrasil integration in slices 7+). Strengr in slice 3 only. Smiðja in slice 4 (sub-agent supervision consolidation).

**Vows touched:** all 10 existing Vows reinforced across the trajectory. All 5 proposed new Vows (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self) instantiated across slices 3-7. Cache Discipline and Defended System Prompt (Hermes-proposed) become standing rules in slice 4 or 5.

**Adopt:**

- The braided-slice approach where each slice contains threads from multiple codexes, not a per-codex-sequential approach.
- The Yggdrasil and Stofa parallel roadmaps as *coordinated* with Ember's slice roadmap, not subordinate.
- The cross-codex conflict register (§5) as a living document — appended when new conflicts surface.

**Adapt:**

- The Hermes-proposed slice 4 (Plural Minds, Plural Memories) becomes Ember slice 5 (after the SAP-derived slice 4 *Felt, Visible, Awake* takes the slot). The slice numbering reflects the bundling decision in `[[67_SLICE_PLAN_REVISIONS]]`.
- The Yggdrasil 5-phase roadmap is *slower* than Ember's slice cadence; one Yggdrasil phase spans multiple Ember slices.

**Avoid:**

- Per-codex-sequential planning ("do all Hermes first, then all SAP"). This invites three problems: (1) cohesion loss within slices, (2) interface-revision churn when later codexes touch earlier surfaces, (3) operator-visible "Hermes era" vs "SAP era" personalities that fragment Ember's identity.
- Treating Yggdrasil or Stofa as "later" work. They are *part of* every Ember slice from slice 3 onward.
- Letting the roadmap calcify. The keeper re-surveys at each slice ratification.

**Invent:**

1. **The Braided-Slice Approach.** Slices contain threads from multiple codexes, organized around theme cohesion rather than codex-of-origin.
2. **The Cross-Codex Conflict Register.** Section 5 of this doc is itself an invention — a living document of where the codexes disagree and how the disagreements resolve.
3. **Per-Slice Stofa Acceptance.** Every Ember slice acceptance criterion includes at least one Stofa-side test. The TUI is not "later"; it is *the surface of every slice*.
4. **The Five-Year Trajectory as Trajectory, Not Forecast.** §6's five-year sketch is an *asymptote* the project is rowing toward, explicitly acknowledged as such, not a commitment.
5. **Yggdrasil/Stofa Parallel Roadmaps as Coordinated, Not Subordinate.** Each has its own phase numbering; Ember slice plans coordinate with them rather than absorbing them.

**Concrete next step for the keeper:**

1. Read this doc.
2. Read each codex's slice-plan-revisions and decision-records documents.
3. Read the Yggdrasil INDEX and roadmap; read the Stofa INDEX and roadmap.
4. Decide whether the braided-slice approach is the right pattern for Wave 3.
5. If yes: ratify slice 3 per `[[6C_EMBER_WAVE_3_SLICE]]`.
6. Coordinate with the Yggdrasil and Stofa roadmap owners (Skald + Architect, with Volmarr as keeper) on parallel phasing.
7. Re-survey this roadmap at each slice ratification.

**The roadmap stands as written. The project does not change. Each slice that becomes Ember code is ratified separately.**

The Scribe records. The keeper decides. The hands of the Forge do the work.
