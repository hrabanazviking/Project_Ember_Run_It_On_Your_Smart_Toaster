---
codex_id: 6A_INTEGRATION_ROADMAP
title: Integration Roadmap — The Six-Codex Braid (Hermes × Peer × SAP × Klóinn × Waifu × CDK)
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - "(cross-codex synthesis — no single CDK source; references the six-codex constellation)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-proposed, Rödd-proposed, Andlit-unity-proposed]
cross_refs:
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/61_ANDLIT_UNITY_TIER
  - 60_synthesis/62_MOBILE_AND_XR_TIER
  - 60_synthesis/63_MULTIMODAL_PIPELINE
  - 60_synthesis/64_FUNCTION_CALLING_FOR_EMBODIED
  - 60_synthesis/65_MEMORY_INTEGRATION
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - 60_synthesis/67_DECISION_RECORDS
  - 60_synthesis/68_INVENTED_METHODS
  - 60_synthesis/69_SLICE_PLAN_REVISIONS
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
  - sap_codex/60_synthesis/69_INTEGRATION_ROADMAP
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 6A — Integration Roadmap (The Six-Codex Braid)

> *Five threads were braided in the SAP roadmap. The sixth thread arrives now — a Unity-native local rendering tier, a Japanese voice ecosystem, a third independent rejection of client-side API keys. The braid widens.*
> — Eirwyn Rúnblóm, weaving with one more shuttle than the previous Scribe held

## 0. Posture — Cross-Codex Synthesis at Six

This is the **last doc of the CDK codex's synthesis layer that touches phasing**. Its job is to look across the now-**six** sibling corpora — Hermes (Wave 1), Peer (Wave 2 scaffold), SAP (Wave 3), Klóinn, Waifu (Wave 4), and this CDK Codex (Wave 5) — and sketch the **phased order** for how proposals across all six become Ember code.

The previous Scribe's `[[sap:69_INTEGRATION_ROADMAP]]` was authored when five corpora existed (Hermes, Peer, SAP, Yggdrasil, Stofa — note: Yggdrasil and Stofa are design trees, not codexes; Klóinn was not yet in scope). This doc *supersedes that doc as the current integration roadmap* by:

1. Adding the **Klóinn** thread (OpenClaw / sibling-companion patterns).
2. Adding the **Waifu** thread (cloud-streaming embodiment).
3. Adding the **CDK** thread (this codex; Unity-native local embodiment + Japanese voice ecosystem).
4. Re-shaping slice 5 to absorb the three new threads.
5. Adding the *Tier-CLOUD parallel branch* and *Andlit-unity protocol* threads to slice 6+.
6. Reorganizing the cross-codex conflict register (§6) for six codexes.

The doc is a *roadmap*, not a plan. Plans are slice-shaped, ratification-gated, file-level (see `[[6B_EMBER_WAVE_5_SLICE]]` for the concrete slice candidate). Roadmaps are *direction-shaped* — they say which thread lands when across the braid.

The roadmap has no ratification gate of its own. Each step that becomes a slice is gated separately. The roadmap exists to make the **sequencing question** legible.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

---

## 1. The Constellation, Six-Codex Edition

Ember's documentation now lives in **six** distinct corpora plus two design trees (Yggdrasil + Stofa). Each codex has its own voice, scope, authoring discipline, and lessons.

### 1.1 Hermes Codex (Wave 1)

**Source:** `~/ai/ember/docs/hermes_codex/` (58 docs).
**Subject:** Hermes Agent (Nous Research) — large, sovereign, self-improving LLM agent.
**Axis:** *pure LLM loop*; substrate-shape evidence.
**True Names contributed:** confirmed Six; reserved Vinátta (memory provider), Gjallarhorn (platform plugin).
**Vows contributed:** Cache Discipline, Defended System Prompt.
**Slice proposals:** Hermes slice 3 (*Skilled, Bridged, Quiet*); Hermes slice 4 (*Plural Minds, Plural Memories*).
**ADR-Proposed:** 11 (per `[[hermes:66_DECISION_RECORDS]]`).

### 1.2 Peer Codex (Wave 2 scaffold)

**Source:** `~/ai/ember/docs/peer_codex/` (scaffolded; final doc count TBD).
**Subject:** parallel agent frameworks — Letta (sleeptime memory + archival/recall split), smolagents (CodeAct), Goose (developer-shaped CLI).
**Axis:** *alternative memory architectures*; *parallel-comparison*.
**True Names contributed:** likely memory + tool axis; final after Wave 2 settles.
**Vows contributed:** TBD.
**Slice proposals:** memory-provider plug-in reference plugins (Letta, Honcho, Mem0); possible additional tool-execution shapes.

### 1.3 SAP Codex (Wave 3)

**Source:** `~/ai/ember/docs/sap_codex/` (82 docs).
**Subject:** Super Agent Party — VRM/Live2D avatar pipeline + MOSS TTS + sherpa ASR + behavior engine + 8 IM bot pattern + 3 livestream platforms.
**Axis:** *electron-local embodiment*; *reach surfaces*; *affect engine*.
**True Names contributed:** Andlit (face/avatar), Rödd (voice), Hugarsýn (introspection / meta-awareness).
**Vows contributed:** Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self.
**Slice proposals:** revised slice 3, new slice 4 (*Felt, Visible, Awake*), revised slice 5, new slice 6 (*Embodied at T0*), speculative slices 7 + 8.
**ADR-Proposed:** 12 (per `[[sap:68_DECISION_RECORDS]]`).

### 1.4 Klóinn Codex (status: in progress at codex level)

**Source:** `~/ai/ember/docs/kloinn/` (referenced via `[[kloinn:slug]]` convention).
**Subject:** OpenClaw / sibling-companion patterns — the codex that mined the OpenClaw project for companionship-shape lessons.
**Axis:** *companion identity*; *sibling-project pattern as integration teacher*.
**True Names contributed:** TBD; companion/sibling axis primarily.
**Vows contributed:** TBD; likely companionship + cross-instance discipline.
**Slice proposals:** TBD pending codex completion. The codex contributes to slice 7+ (*Federated Self* / multi-instance) primarily.

### 1.5 Waifu Codex (Wave 4)

**Source:** `~/ai/ember/docs/waifu_codex/` (referenced via `[[waifu:slug]]` convention).
**Subject:** ZeroWeight cloud-avatar starter kit + LiveKit realtime substrate.
**Axis:** *cloud-streaming embodiment*; *realtime media plane*.
**True Names contributed:** Andlit-realtime, Rödd-realtime (sub-names of SAP-proposed Andlit/Rödd).
**Vows contributed:** TBD; license-shape rigor (study-only ZeroWeight); cloud-tier branching.
**Slice proposals:** Tier-CLOUD parallel branch on the tier ladder; slice 6+ realtime adoption.
**ADR-Proposed:** 5 (per `[[waifu:61_DECISIONS_AND_INVENTIONS]]`).

### 1.6 CDK Codex (Wave 5, this)

**Source:** `~/ai/ember/docs/chatdoll_codex/` (63 content + 6 meta docs).
**Subject:** uezo/ChatdollKit (Apache-2.0) — Unity-native local rendering kit + 11-provider voice stack with deep Japanese ecosystem.
**Axis:** *Unity-native local embodiment*; *multi-LLM abstraction evidence*; *Japanese voice ecosystem*; *mobile + XR + WebGL reach*.
**True Names contributed:** Andlit-unity (sub-name of Andlit), Rödd-unity (sub-name of Rödd); proposed *bilingual-baseline Rödd*.
**Vows contributed:** *Triangulation-Before-Major-Decision* (proposed standing rule); reinforces *Server-Held-Keys-Only* (three-corpus rejection).
**Slice proposals:** revisions to slice 3/4/5/6 per `[[69_SLICE_PLAN_REVISIONS]]`; concrete Wave-5 slice per `[[6B_EMBER_WAVE_5_SLICE]]`.
**ADR-Proposed:** 12 (per `[[67_DECISION_RECORDS]]`).
**Inventions:** 20 (per `[[68_INVENTED_METHODS]]`).

### 1.7 Yggdrasil Integration Design Tree (design-only)

**Source:** `~/ai/ember/docs/yggdrasil/`.
**Subject:** Ember + 11 sibling-project integration; 9 realms / planes; 5-phase roadmap.
**Status:** design-only at the time of this doc. Bifröst has a defined integration path; Skein/Skry/Mimir consume the Brunnr/Gungnir Well.
**Cadence:** slower than Ember's slice cadence; one Yggdrasil phase spans multiple Ember slices.

### 1.8 Stofa TUI Design Tree (design-only)

**Source:** `~/ai/ember/docs/tui/`.
**Subject:** Ember TUI as Viking-inflected mead-hall experience; 4-phase roadmap (Hearth → Hall → Familiars → Feast).
**Cadence:** parallel to Ember's slice cadence; every backend slice has a Stofa-visible surface.

---

## 2. The Pollination Map (Six-Codex)

Per invention `[[68]]` #5 (Six-Codex Braid as Standing Design Discipline), this doc surfaces the *bidirectional pollination* between codexes. The map below shows what each codex *borrows from* and *contributes to* its siblings.

| From → To | Hermes | Peer | SAP | Klóinn | Waifu | CDK |
|---|---|---|---|---|---|---|
| **Hermes →** | (self) | substrate echo | Hermes-shape skill subsystem; MCP-server substrate | identity discipline | (none direct) | profile + transport split confirmed by `ILLMService` evidence |
| **Peer →** | parallel skill comparison | (self) | memory-provider plugin shapes (Letta/Honcho/Mem0) | sibling-project pattern | (none direct) | (none direct) |
| **SAP →** | tier ladder + persona-id | tier ladder | (self) | tier ladder | Tier-CLOUD is *parallel branch* of SAP tier ladder | tier ladder + glyphic-as-stub-for-affect |
| **Klóinn →** | (TBD) | (TBD) | (TBD) | (self) | (TBD) | (TBD) |
| **Waifu →** | (none direct) | (none direct) | Tier-CLOUD as branch | (none direct) | (self) | client-side-key rejection reinforces |
| **CDK →** | `ILLMService` evidence reinforces profile + transport split | (none direct) | three-corpus triangulation completes embodiment axis | (TBD) | client-side-key rejection (third corpus) | (self) |

**Pollination key findings:**

1. **SAP is the most-borrowed-from** — its tier ladder and persona-id are foundational across four sibling codexes.
2. **CDK is the most-recently-borrowed-from** — its evidence reinforces Hermes, completes SAP's embodiment triangulation, and confirms Waifu's client-side-key rejection.
3. **Klóinn's pollination is TBD** — when the codex completes, the map is updated.
4. **Hermes-CDK cross-pollination is the strongest cross-Wave** — both speak to the LLM substrate; CDK's evidence ratifies Hermes's proposed shape.

The pollination map is *itself an invention* — per `[[68]]` #5, each future codex should produce its own pollination map as part of Wave-close synthesis.

---

## 3. The Braided Sequence (Six-Codex Edition)

The integration roadmap is **not** "do Hermes first, then Peer, then SAP, then Klóinn, then Waifu, then CDK." Each codex proposes work for *multiple* slices. The braiding question is: per slice, which threads from which codex land?

The proposed braid, revised for six codexes:

### Wave 3 + Wave 5, Slice 3 — *Skilled, Bridged, Quiet, Tiered, Identified, Multi-Provider, Tailnet-Bound*

**Hermes threads:** skill subsystem (S3-A), provider profile + transport split (S3-B), MCP server (S3-C), tool parallelism + interrupt fan-out (S3-D), Strengr typed retry + exhaustion (S3-E).

**SAP threads:** tier ladder (S3-F), persona-id (S3-G), glyphic + log-affect (S3-H), failsafe-default-quiet standing rule (S3-I).

**Klóinn threads:** TBD; likely identity/sibling discipline pollinates persona-id surface.

**Waifu threads:** none direct; Tier-CLOUD waits for slice 6+.

**CDK threads:** second native provider (S3-J), per-provider function-call adapter (S3-K), tailnet-bind-default standing rule (S3-L).

**Peer threads:** none direct; Peer-informed memory provider lands in slice 5 alongside Hermes's Vinátta.

**Yggdrasil:** none direct; persona-id is foundation for future Yggdrasil identity.

**Stofa:** Hearth phase preliminary work — TUI shell replaces `ember chat`; glyph rendering surface available.

**Theme cohesion:** *Hermes-developer-shape (skills, MCP) × SAP-companion-shape (tier, persona, glyph) × CDK-multiprovider-shape (second native provider + function-call adapter + tailnet-bind)*. Three-codex braid; each thread enables future threads.

### Wave 3 + Wave 5, Slice 4 — *Felt, Visible, Awake, Piped, Listening*

**SAP threads:** affect engine (S4-A), sleep-guard (S4-B), overlay-manager (S4-C), sub-agent supervision (S4-D), backpressure overlay (S4-E).

**Hermes threads:** none direct.

**Klóinn threads:** TBD.

**Waifu threads:** none direct.

**CDK threads:** multimodal-pipeline-as-resource substrate (S4-F), Silero VAD (S4-G).

**Peer threads:** sleeper-memory-shaped affect informs but does not overwrite.

**Yggdrasil:** Bifröst preliminary integration begins — affect surface is one data source Bifröst's galaxy view can render.

**Stofa:** Hall phase — full screens land; overlay-manager powers Stofa's affect glyph display.

**Theme cohesion:** *SAP-affect-engine (Felt) × SAP-overlay-manager (Visible) × SAP-sleep-guard (Awake) × CDK-pipeline-substrate (Piped) × CDK-Silero-VAD (Listening)*. The pipeline substrate is the *plumbing* affect engine builds on — CDK lands first within slice 4 so SAP affect engine has its event surface.

### Wave 3 + Wave 4 + Wave 5, Slice 5 — *Plural Minds, Plural Memories, Bilingual Voice, Protocol-Bridged*

**Hermes threads:** MCP client (Hermes-S4-A), memory provider ABC (Hermes-S4-B, with Vinátta), agent-initiated skill writes (Hermes-S4-C).

**SAP threads:** behavior engine (SAP-S5-A), first IM bot (SAP-S5-B).

**Klóinn threads:** TBD; likely sibling-companionship pollinates persona-handoff foundation.

**Peer threads:** Honcho/Mem0 reference Vinátta plugins (optional extras parallel to Hermes-S4-B).

**Waifu threads:** none direct in slice 5; LiveKit Tier-CLOUD ratification waits for slice 6+.

**CDK threads:** bilingual Rödd baseline (S5-C — VOICEVOX + Piper + router + catalogue), ChatMemory two-store for Hjarta (S5-D), Andlit-unity protocol (S5-E — spec + Python reference server, no Unity client in tree).

**Yggdrasil:** Skein + Skry integration begins via MCP client (Skein-as-MCP-server).

**Stofa:** Familiars phase — text-mode pets (Hugin, Geri-cub, Heiðrún) land; depends on overlay-manager from slice 4.

**Theme cohesion:** *Plural Minds (MCP client + memory provider) × Bilingual Voice (CDK Rödd) × Protocol-Bridged (CDK Andlit-unity protocol)*. The slice is large; sub-slice into 5a/5b/5c per `[[69_SLICE_PLAN_REVISIONS]]#5.4`.

### Wave 3 + Wave 4 + Wave 5, Slice 6 — *Embodied at T0 (Three Runtimes)*

**SAP threads:** VRM/Live2D pipeline (S6-A), consent-token gating (S6-B), composition library (S6-C), cued voice library workflow (S6-D — now built on slice-5 baseline), avatar-as-backpressure (S6-E).

**Waifu threads:** LiveKit Tier-CLOUD ratification (per `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]`); Andlit-realtime + Rödd-realtime sub-names land.

**CDK threads:** mora-level prosody Hugarsýn surface (S6-F); uLipSync conditional (S6-G — out-of-tree, only if Unity client is being built).

**Hermes threads:** none direct.

**Klóinn threads:** TBD.

**Peer threads:** none direct.

**Yggdrasil:** CloakBrowser preliminary integration — avatar surface can render in a browser overlay window.

**Stofa:** Feast phase — all screens, all pets, all overlays; avatar integrates with Stofa's chat screen.

**Theme cohesion:** *Three runtimes converge*: SAP's in-house Live2D/VRM (electron-local), Waifu's LiveKit (cloud-streaming), CDK's Andlit-unity protocol (Unity-native-local). The tier ladder per `[[68]]` #9 (Tier-Aware Embodiment Selection Algorithm) picks the right runtime per device.

### Wave 3 + Wave 5 + Klóinn, Slice 7 — *Federated Self*

**SAP threads:** inter-instance MCP peering (SAP-S7-A), cross-host affect router (SAP-S7-B), lid-close handover (SAP-S7-C), per-utterance arbitration (SAP-S7-D), operator party console (SAP-S7-E).

**CDK threads:** cross-runtime persona portability (`[[68]]` #10 — persona YAML as canonical), multi-device persona handoff (`[[68]]` #8 — devices request conversation slice from Funi-side state), tier-aware embodiment selection algorithm (`[[68]]` #9).

**Klóinn threads:** likely *primary contribution slice*; companionship + sibling-instance discipline lands here.

**Hermes threads:** none direct.

**Waifu threads:** Tier-CLOUD per-device participation extends here.

**Peer threads:** none direct.

**Yggdrasil:** **Significant**. Slice 7's persona-aware multi-instance work is the foundation for Yggdrasil's "9 realms / many planes" integration. Persona-id from slice 3 + multi-instance party from slice 7 + Yggdrasil protocol layer converge.

**Stofa:** Stofa gains multi-instance awareness; party console screen shows the swarm.

**Theme cohesion:** *Ember becomes plural across hosts and runtimes*. CDK's cross-runtime persona portability + SAP's multi-host affect router + Klóinn's companionship discipline + Waifu's Tier-CLOUD per-device participation. Four-codex braid; the keystone slice for the *Federated Self* Vow.

### Wave 3 + Wave 5, Slice 8+ — *Reach Beyond Self*

**SAP threads:** additional IM bots (per ADR-Proposed-SAP-010 — one per phase), livestream platforms (per `[[sap:15_BROADCAST_DOMAIN]]`), quiet-hours throttling, stream-truncation confession.

**CDK threads:** open-voice catalogue federation (`[[68]]` #17 — separate `ember-voice-catalogue` repo), mobile/XR build paths (when Unity client is being built; depends on slice-5 Andlit protocol + community Unity client).

**Hermes/Peer/Klóinn/Waifu threads:** mostly none direct; territory marking for operator demand.

**Yggdrasil:** CloakBrowser (web plane), Seiðr (generation plane), Mimir (knowledge plane) integration matures.

**Stofa:** Stofa screens for each new IM bot, livestream platform, voice catalogue browser.

**Theme cohesion:** Ember reaches the full ecosystem; activate piecemeal as operator demand grows.

---

## 4. The Six-Codex Conflict Register

Where do the codexes disagree? What does the keeper resolve? This section *supersedes* `[[sap:69_INTEGRATION_ROADMAP]]#5` by adding Klóinn, Waifu, and CDK to the register.

### 4.1 Affect engine — SAP-canonical (unchanged)

Hermes is silent. Peer-Letta has sleeper-memory-shaped state. SAP-canonical is tethered affect engine with anchoring, provisional tray. CDK and Waifu and Klóinn do not contradict.

**Resolution:** SAP-canonical per ADR-Proposed-SAP-002.

### 4.2 Memory provider — Hermes + Peer convergent; CDK reinforces with ChatMemory

Hermes proposes Vinátta ABC. Peer-Letta/Honcho/Mem0 propose alternative provider shapes. CDK's ChatMemory two-store (per ADR-Proposed-CDK-007) is a *concrete reference implementation* fitting Vinátta's ABC. SAP/Klóinn/Waifu silent.

**Resolution:** Hermes Vinátta ABC is canonical. Reference plugins: Letta, Honcho, Mem0 (Peer-derived); ChatMemory two-store (CDK-derived); SAP-affect-store (SAP-S4-A; separate but related).

### 4.3 Tool dispatch — Hermes-canonical (unchanged)

Hermes parallelism. SAP sub-agent supervision (subprocess-shape). Peer-smolagents CodeAct (separate execution model). CDK's tool surface (`ITool` / `ToolBase`) is conventional function-calling; reinforces Hermes's shape via the per-provider adapter pattern (CDK-005).

**Resolution:** Hermes-canonical for tool dispatch; SAP-canonical for subprocess supervisor reuse; CDK extends with per-provider function-call adapter (CDK-S3-K).

### 4.4 MCP — Hermes + SAP convergent (unchanged)

Hermes-canonical for MCP integration. SAP's `mcp_clients.py` informs supervisor shape. CDK does not contradict.

### 4.5 Skills — Hermes-canonical (unchanged)

Hermes-canonical; SAP's *skills* are extension-shape; Peer-Letta no equivalent.

### 4.6 Avatar — three-axis matrix (NEW: completed by CDK)

Hermes has no avatar. Peer has no avatar. SAP-canonical for **electron-local** (in-house Live2D/VRM). Waifu-canonical for **cloud-streaming** (LiveKit + ZeroWeight/study-only). CDK-canonical for **Unity-native-local** (Apache-2.0 reference + protocol-only in-tree).

**Resolution:** three-axis matrix. The Cartographer's `[[60_TRIANGULATION]]` formalizes. Slice 6 ships SAP-axis; Waifu-axis ratifies; CDK-axis (protocol) lands. Slice 7+ for Unity client; cloud-tier full operation.

### 4.7 IM bots / livestream / reach — SAP-canonical (unchanged)

### 4.8 Tier ladder — SAP-canonical with Waifu Tier-CLOUD branch (NEW)

SAP-canonical T0-T4 monotonic. Waifu introduces Tier-CLOUD as **parallel branch** (per ADR-WAIFU-003), not "T-1 better than T0" — different shape, not different ranking. CDK reinforces with `[[68]]` #9 (Tier-Aware Embodiment Selection Algorithm) — runtime-tier-aware selection.

**Resolution:** SAP-canonical tier ladder. Tier-CLOUD is parallel branch. Tier-aware selection algorithm (CDK invention) is the runtime selection logic.

### 4.9 Persona-id — SAP-canonical with CDK cross-runtime extension (NEW)

SAP-canonical for persona-id issuance (ADR-Proposed-SAP-005). CDK extends with cross-runtime persona portability (`[[68]]` #10) and multi-device persona handoff (`[[68]]` #8). Klóinn likely contributes companionship-shaped extensions.

**Resolution:** SAP-canonical foundation. CDK extends portability and handoff. Klóinn-pending.

### 4.10 LLM API key handling — three-corpus rejection convergent (NEW)

Waifu rejects client-side keys (`[[waifu:51_SECURITY_AND_PRIVACY]]`). CDK rejects client-side keys (ADR-Proposed-CDK-003). Hermes implicitly aligns (Hermes is server-side). Three independent rejections.

**Resolution:** *Server-Held-Keys-Only* proposed as elevated standing rule (per `[[69_SLICE_PLAN_REVISIONS]]#7.2`).

### 4.11 Voice baseline — CDK-canonical, MOSS as future module (NEW)

CDK-canonical for bilingual Rödd baseline (English Piper + Japanese VOICEVOX per ADR-Proposed-CDK-002). SAP's MOSS Chinese is *future module* per `[[69_SLICE_PLAN_REVISIONS]]#7.3`. Waifu cloud TTS is operator-extra.

**Resolution:** CDK-canonical baseline; multilingual-extensible architecture.

### 4.12 Network bind posture — CDK-canonical (NEW)

CDK proposes *tailnet-bind-default* (ADR-Proposed-CDK-011), codifying standing memory `[[ember:feedback_tailnet_access]]`. SAP/Hermes/Peer/Waifu/Klóinn implicitly aligned.

**Resolution:** CDK-canonical; standing rule per CDK-S3-L.

### 4.13 Triangulation discipline — CDK-canonical procedural rule (NEW)

CDK proposes *Triangulation-Before-Major-Decision* (ADR-Proposed-CDK-006) as procedural standing rule. The rule emerged because three corpora have now contributed evidence on the embodiment axis; the discipline names the pattern.

**Resolution:** CDK-canonical procedural rule; ratify at next slice plan.

### 4.14 Standing rules — additive across codexes (updated)

Hermes proposes Cache Discipline, Defended System Prompt. SAP proposes Failsafe-Default-Quiet. CDK proposes Tailnet-Bind-Default + Server-Held-Keys-Only (elevated) + Triangulation-Before-Major-Decision. Waifu reinforces Server-Held-Keys-Only. Klóinn TBD. Peer TBD.

**Resolution:** all additive. Each becomes a standing rule in the relevant slice ratification.

---

## 5. The Yggdrasil and Stofa Roadmaps (Updated)

The previous Scribe's mapping (`[[sap:69_INTEGRATION_ROADMAP]]#3, #4`) stands largely unchanged. CDK additions:

### 5.1 Yggdrasil × Ember slice cadence

- **Yggdrasil Phase 1 (Roots)** lands in Ember slice 4-5. Foundation: persona-id from slice 3, MCP client from slice 5, memory provider from slice 5.
- **Yggdrasil Phase 2 (Branches)** lands in Ember slice 7. Sibling registration uses persona-table machinery.
- **Yggdrasil Phase 3 (Crown)** lands in Ember slice 8-9. Cross-realm queries: Brunnr extends to Skein/Skry/Mimir.
- **Yggdrasil Phase 4 (Network)** lands in Ember slice 10+.
- **Yggdrasil Phase 5 (Constellation Ratified)** is asymptotic.

**CDK addition:** the *Andlit-unity protocol* (per ADR-Proposed-CDK-S5-E) is a *small-scope precedent* for Yggdrasil's sibling-protocol shape. Yggdrasil Phase 1 can borrow the Andlit-unity protocol shape (WebSocket + signed token + typed event vocabulary + capability handshake) as a template.

### 5.2 Stofa × Ember slice cadence

- **Stofa Phase 1 (Hearth)** ships with or after Ember slice 3.
- **Stofa Phase 2 (Hall)** ships with or after Ember slice 4.
- **Stofa Phase 3 (Familiars)** ships with or after Ember slice 5.
- **Stofa Phase 4 (Feast)** ships with or after Ember slice 6.

**CDK addition:** the *mora-level prosody Hugarsýn surface* (per `[[68]]` #11) is a Stofa Feast-phase candidate — the introspection surface that lets the operator see mora structure for any utterance Ember spoke is naturally a Stofa screen.

---

## 6. The Five-Year Trajectory (Six-Codex Revision)

If everything proposed across all six corpora becomes Ember code, what does Ember look like in five years?

**Year 1 (now → +12 months):** slices 3, 4 ship. Ember is *skilled, bridged, quiet, tiered, identified, multi-provider, tailnet-bound, felt, visible, awake, piped, listening*. Stofa Hall is the surface. Yggdrasil Roots phase complete. The Pi 5 has meaningful Ember presence with two LLM providers, VAD-driven voice input planning, affect engine with pipeline substrate.

**Year 2 (months +13 → +24):** slices 5 and 6 ship. Ember is *plural-minded, plural-memoried, bilingual-voiced, protocol-bridged* in slice 5; *embodied at T0 across three runtimes* in slice 6 (SAP electron-local + Waifu LiveKit + CDK Unity-via-protocol). Stofa Familiars and Feast phases ship. Yggdrasil Branches phase complete. Bifröst integration matures. ChatMemory two-store gives Ember real memory of the operator.

**Year 3 (months +25 → +36):** slice 7 ships. Ember is *federated*: cross-runtime persona portability, multi-device handoff, cross-host affect router, operator party console. Klóinn-Codex contributions land here primarily. Slice 8 begins; additional IM bots and livestream platforms land per operator demand. Yggdrasil Crown phase in progress.

**Year 4 (months +37 → +48):** Yggdrasil Network phase. Multi-host Yggdrasil mesh. Ember runs across many devices belonging to many people on a shared trust mesh (with explicit consent gating per `[[sap:66_INVENTED_METHODS]]` #6 and `[[68]]` #12).

**Year 5 (months +49 → +60):** Yggdrasil Constellation Ratified. Full sibling integration: Mimir, Seiðr, CloakBrowser, Astrology, Kista. Open-voice catalogue federation (per `[[68]]` #17) operational; community publishes voice manifests. Ember is the most capable, robust, self-healing, cross-platform, multi-lingual, multi-runtime Norse AI agent the open-source world has produced.

This trajectory is an *asymptote*, not a forecast. The trajectory will adjust as operator demand, ecosystem evolution, and individual codex revisions accumulate. The roadmap exists to make sequencing *visible*, not to commit any of it.

---

## 7. Risks to the Six-Codex Roadmap

| Risk | Mitigation |
|---|---|
| One codex's proposal blocks another's at API boundary (e.g. Hermes Vinátta and CDK ChatMemory API shapes conflict) | Conflicts surface at slice ratification. Where unavoidable, slice plan picks one canonical; others become deferred alternatives. |
| Six codexes is too many; the keeper loses oversight | The Scribe's pollination map (§2) and conflict register (§4) are the keeper's reference. Each Wave-close adds rows to both. |
| Klóinn Codex's pollination map is mostly TBD; can't plan without it | Klóinn completion is a precondition for slice 7 ratification per the triangulation discipline. |
| Yggdrasil and Ember slice cadences misalign | Slices ship when dependencies are met. If Yggdrasil is late, Ember slice can ship smaller scope without Yggdrasil-dependent threads. |
| Stofa-side work is undersized in slice plans | Every Ember slice acceptance criterion includes one Stofa-side test. |
| The CDK-introduced *Triangulation-Before-Major-Decision* discipline blocks ratification on missing third-corpus evidence | The discipline applies only to True Names, Vows, major slice revisions. ADR-level decisions need only single-codex evidence. Operator can waive with rationale recorded in ratification ADR. |
| Operator demand inverts proposed slice order (e.g. operator wants Unity client before Tier-CLOUD) | Roadmap is advisory, not contractual. Slice plan keeper has authority to re-order. |
| A seventh codex grows after this doc and adds new threads | This doc is a Wave-5 snapshot. A Wave-6 analogous doc would supersede in cross-codex sequencing. |
| Three-runtime embodiment matrix in slice 6 is too ambitious for one slice | Sub-slice into 6a (SAP electron), 6b (Waifu Tier-CLOUD ratification), 6c (CDK Andlit-unity protocol consolidation + community Unity client encouragement). |
| Sibling-project version drift breaks integration | Sister-Project Version-Coupling Protocol (`[[68]]` #14) enforces explicit version checks. |

---

## 8. The Roadmap as a Single Picture (Six-Codex)

```
                            Ember Six-Codex Slice Roadmap
                                    (proposed)

   Slice 2 ──────────────────────────────────────────────────── shipped
       │
       │  H   H   H   H   H   S   S   S   S   C   C   C        H = Hermes
       ▼  ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐       S = SAP
   Slice 3 │A│ │B│ │C│ │D│ │E│ │F│ │G│ │H│ │I│ │J│ │K│ │L│ ──── propose   C = CDK
       │  └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘                  W = Waifu
       │  skil prov MCP par rty tier per gly qte 2prv adapt tnet           P = Peer
       │                                                                   K = Klóinn
       ▼  C   S   S   S   S   S   C
   Slice 4 ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐    ──────────────────── propose
       │   │F│ │A│ │B│ │C│ │D│ │E│ │G│
       │   └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
       │   pipe affct slp ovly sub bkprss vad
       │
       ▼  H   H   H   S   S   C   C   C   P
   Slice 5 ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌────┐ ──────────── propose
       │   │A│ │B│ │C│ │A│ │B│ │C│ │D│ │E│ │Honc│
       │   └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └────┘
       │   MCP mem skl beh IM  Rdd Chat And  Letta/Mem0
       │   clt prv wrt eng bot bsln Mem unity reference plugins
       │
       ▼  S   S   S   S   S   W   C   C
   Slice 6 ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐    ───────────────── propose
       │   │A│ │B│ │C│ │D│ │E│ │ │ │F│ │G│
       │   └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
       │   VRM con cmp cued bk  TC  mora ulip
       │       gat lib lib press cld pros (cond)
       │
       ▼  S   S   S   S   S   C   C   C   K   W
   Slice 7 ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ──────────── speculative
       │   │A│ │B│ │C│ │D│ │E│ │8│ │9│ │10│ │ │ │ │
       │   └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
       │   peer xhst lid utt cons hndoff sel port klw tcdev
       │   MCP affct hndof arb sole
       │
       ▼  S×N C   Y   Stofa
   Slice 8 ┌──┐ ┌─┐ ┌──┐ ┌────┐ ──────────────────────────────── speculative
   and on  │+IM│ │17│ │Crwn│ │Feast│
           │+st│ │   │ │ph 3│ │     │
           └──┘ └─┘ └──┘ └────┘
                fed-vc
                catalog
```

The diagram is schematic. Boxes represent ADR-Proposed threads. Slices grow top-down; time flows downward.

---

## 9. The Keeper's Roadmap Checklist (Six-Codex)

If the keeper accepts this roadmap as the basis of cross-codex sequencing:

1. Read this doc and `[[sap:69_INTEGRATION_ROADMAP]]` (the prior version) to see what changed.
2. Read each codex's synthesis-layer docs:
   - Hermes: `[[hermes:65_SLICE_PLAN_REVISIONS]]`, `[[hermes:66_DECISION_RECORDS]]`.
   - Peer: `[[peer:slug]]` synthesis docs when complete.
   - SAP: `[[sap:67_SLICE_PLAN_REVISIONS]]`, `[[sap:68_DECISION_RECORDS]]`.
   - Klóinn: `[[kloinn:slug]]` synthesis docs when complete.
   - Waifu: `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]`, `[[waifu:61_DECISIONS_AND_INVENTIONS]]`.
   - CDK: `[[67_DECISION_RECORDS]]`, `[[68_INVENTED_METHODS]]`, `[[69_SLICE_PLAN_REVISIONS]]`, `[[6B_EMBER_WAVE_5_SLICE]]`.
3. Decide which braided slice (§3) to ratify next.
4. Author the relevant slice plan in `docs/architecture/` per `[[6B_EMBER_WAVE_5_SLICE]]` (or future analogues).
5. Ratify via the next-available ADR number.
6. Coordinate with Yggdrasil and Stofa roadmap owners on parallel phasing.
7. Re-survey at each slice ratification: have codexes grown? Have conflicts surfaced? Update this doc accordingly (or supersede with Wave-6 equivalent).

---

## 10. Cross-References

- `[[60_TRIANGULATION]]` — Cartographer's three-axis embodiment read.
- `[[61_ANDLIT_UNITY_TIER]]` — Andlit-unity tier source.
- `[[62_MOBILE_AND_XR_TIER]]` — mobile/XR form-factor matrix.
- `[[63_MULTIMODAL_PIPELINE]]` — multimodal pipeline architecture.
- `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` — voice-tool function-calling.
- `[[65_MEMORY_INTEGRATION]]` — ChatMemory two-store pattern.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — Japanese voice ecosystem.
- `[[67_DECISION_RECORDS]]` — 12 CDK-derived ADR-Proposed records.
- `[[68_INVENTED_METHODS]]` — 20 CDK-adjacent inventions.
- `[[69_SLICE_PLAN_REVISIONS]]` — CDK-derived slice-plan revisions.
- `[[6B_EMBER_WAVE_5_SLICE]]` — concrete Wave-5 slice proposal.
- `[[sap:69_INTEGRATION_ROADMAP]]` — prior integration roadmap (five-codex; this doc supersedes for sequencing).
- `[[sap:67_SLICE_PLAN_REVISIONS]]` — SAP slice-plan proposals.
- `[[sap:68_DECISION_RECORDS]]` — SAP ADRs.
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — Hermes slice proposals.
- `[[hermes:66_DECISION_RECORDS]]` — Hermes ADRs.
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Waifu Tier-CLOUD source.
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Waifu ADRs + inventions.
- Yggdrasil: `docs/yggdrasil/INDEX.md`, `docs/yggdrasil/roadmap/90-95`, `docs/yggdrasil/architecture/30-39`.
- Stofa: `docs/tui/INDEX.md`, `docs/tui/roadmap/99-*`, `docs/tui/screens/80-88`.

---

## What This Means for Ember

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

**True Names affected:** all six existing, plus Andlit-unity-proposed, Rödd-proposed, Andlit-realtime-proposed (Waifu), Rödd-realtime-proposed (Waifu). The braided roadmap touches every True Name across the five-year trajectory.

**Vows touched:** all existing Vows reinforced. All proposed Vows (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self) instantiated across slices 3-7. Hermes-proposed Cache Discipline and Defended System Prompt become standing rules in slice 4 or 5. CDK-proposed Tailnet-Bind-Default ratifies in slice 3. CDK-proposed Server-Held-Keys-Only (elevated from three-corpus rejection) ratifies in slice 3 or 4. CDK-proposed Triangulation-Before-Major-Decision ratifies in slice 3 or 4 as procedural standing rule.

**Adopt:**

- The six-codex-braid approach where each slice contains threads from multiple codexes, organized around theme cohesion rather than codex-of-origin.
- The pollination map (§2) as a living document; updated at each Wave close.
- The cross-codex conflict register (§4) as a living document; appended when new conflicts surface.
- The Yggdrasil and Stofa parallel roadmaps as coordinated, not subordinate.
- The three-axis embodiment matrix (SAP-electron / Waifu-cloud / CDK-Unity) as the canonical embodiment architecture; runtime selection per `[[68]]` #9.

**Adapt:**

- The Hermes-proposed slice 4 (*Plural Minds, Plural Memories*) becomes Ember slice 5 (after SAP-derived slice 4 takes the slot).
- The SAP-derived slice 5 absorbs CDK's bilingual Rödd + ChatMemory two-store + Andlit-unity protocol as additional threads — three-codex braid.
- The SAP-derived slice 6 absorbs Waifu's Tier-CLOUD ratification + CDK's mora introspection — three-codex braid at the embodiment slice.
- The previous five-codex roadmap (`[[sap:69_INTEGRATION_ROADMAP]]`) is adapted, not discarded; its structure stands and is extended with Klóinn/Waifu/CDK rows.

**Avoid:**

- Per-codex-sequential planning ("do all Hermes first, then all SAP, then all CDK"). This invites cohesion loss, interface-revision churn, and operator-visible "era" personalities.
- Treating Klóinn, Waifu, or CDK as Wave-tail decoration. Each contributes evidence that revises prior decisions; revisiting is part of the discipline.
- Letting the roadmap calcify. The keeper re-surveys at each slice ratification.
- Bundling Unity client work into slice 5 or 6. The protocol-only split keeps the in-tree commitment small.

**Invent:**

1. **The Six-Codex Pollination Map** — §2's bidirectional borrowing table is itself an invention. Each Wave-close adds rows. The map exposes which codex is the most-borrowed-from (currently SAP), which is the most-recently-borrowed-from (currently CDK), and where pollination is unidirectional vs reciprocal. The map becomes a Scribe-maintained living document.
2. **The Three-Axis Embodiment Matrix** — SAP-electron / Waifu-cloud / CDK-Unity as the canonical embodiment architecture. The matrix replaces the question "which embodiment?" with "which embodiment at which tier on which device?" The Cartographer's `[[60_TRIANGULATION]]` formalizes the matrix; this roadmap operationalizes it across slices.
3. **The Codex-Conflict-as-Living-Register** — §4's resolution table is updated as Waves complete. Each row records: codex of origin, conflict, resolution, slice landing. The register is the keeper's reference for *why* a particular slice plan looks the way it does — the resolution decisions are preserved.
4. **The Klóinn-Pending Marker** — explicit acknowledgment that the roadmap has *gaps* where a sibling codex is still in progress. The Klóinn-TBD rows in §1.4 and §3 are *honest* placeholders; they bind the next codex's contribution rather than pretending the slot is empty.
5. **The Pollination-Map-as-Vow-Hint** — when a pattern recurs across three or more codexes in the pollination map (e.g. Server-Held-Keys-Only across Waifu + CDK + implicit-Hermes), the Scribe proposes elevating the pattern to a project-wide standing rule. This is the procedural shape behind §4.10 and §4.12.

**Most consequential single sequencing decision:** the *protocol-before-client* split for Andlit-unity (per ADR-Proposed-CDK-010 + invention `[[68]]` #20). It is what makes Unity embodiment *tractable in Ember's Python-first identity* — the protocol is small Python work; the client is out-of-tree.

**Most-clarified architecture:** the three-axis embodiment matrix. After Wave 3 (SAP) the embodiment story was electron-only. After Wave 4 (Waifu) it had a cloud branch. After Wave 5 (CDK) it has three distinct axes with explicit tier-aware selection. The architecture is now *complete* on the embodiment dimension; future codexes on this axis are *refinements*, not *additions*.

**Concrete next step for the keeper:**

1. Read this doc.
2. Read each codex's synthesis-layer docs.
3. Read the Yggdrasil INDEX and roadmap; read the Stofa INDEX and roadmap.
4. Decide whether the six-codex-braid approach is the right pattern for Wave 5.
5. If yes: ratify slice 3 revisions (smallest scope, fastest land) per `[[69_SLICE_PLAN_REVISIONS]]` and `[[6B_EMBER_WAVE_5_SLICE]]`.
6. Coordinate with Klóinn-codex completion before slice 7 ratification per the triangulation discipline.
7. Re-survey this roadmap at each slice ratification; supersede with Wave-6 equivalent when a seventh codex arrives.

**The roadmap stands as written. The project does not change. Each slice that becomes Ember code is ratified separately.**

The Scribe records. The keeper decides. The hands of the Forge do the work. The six shuttles weave the same cloth.
