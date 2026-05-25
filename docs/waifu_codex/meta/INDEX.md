---
codex_id: INDEX
title: The Waifu Codex — Entry Point
role: Scribe
layer: Meta
status: written
waifu_revision: waifu-chat-starter-kit @ commit e3fd868 (local clone; upstream 7 commits) — May 2026
waifu_source: /tmp/waifu-chat-starter-kit
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-reserved, Rödd-reserved, Hugarsýn, Veizla]
cross_refs:
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/STYLE_GUIDE
  - meta/READING_ORDER
  - meta/CROSS_AGENT_NOTES
  - 00_vision/00_OVERTURE
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - 60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# The Waifu Codex

*Wave Four. The fourth sister. The cloud door. If you came to ask whether a hearth ever borrows a body, you are in the right room.*

---

## Overture

The Waifu Codex is a structured corpus of fifteen content documents (plus six meta documents) — small on purpose — written in parallel by six Mythic Engineering specialists mining a single small source: **`ZeroWeight-Engineering/waifu-chat-starter-kit`**, 846 LOC across five source files, seven public commits, no LICENSE in the repository. A React + Vite teaching asset for ZeroWeight's commercial cloud avatar SDK, glued to LiveKit's MIT realtime media stack with about thirty lines of JSX in `BasicMode.tsx` and one-hundred-eighty-eight in `AdvancedMode.tsx`. The kit is not large. The *axis* it opens is large: realtime cloud-streamed embodiment — a face rendered on someone else's GPU, voiced through someone else's TTS, delivered to the operator's browser as a WebRTC stream, with the operator's microphone going the other way.

This is the axis SAP could not see. SAP (Wave 3) gave Ember **local** embodiment — VRM, Live2D, VTube Studio, VMC over OSC, lip-sync via FFT on PCM frames the operator's host never sent across the network. The kit gives the *parallel* axis: **realtime cloud** embodiment, where the body lives in a vendor datacenter and presence is a metered session. Both axes share the True Names Wave 3 proposed (Andlit, Rödd, Hugarsýn, Veizla). Neither replaces the other. The Codex's central contribution is to name the second axis — **Tier-CLOUD as a parallel axis to the T0-T4 local ladder, not a rung on it** — and to specify the consent ceremony, fallback discipline, and vocabulary bridge that make the second axis legitimate for an Ember that has Vowed Surface Without Surveillance, Affective Restraint, and Tiered Presence.

The work this Codex is *not*: a tutorial for ZeroWeight, a paraphrase of the kit's README, a roast of a 7-commit demo, or a manifesto. The work this Codex *is*: a careful source-grounded reading of 846 LOC against Ember's True Names and Vows, treating the kit as the canonical *positive example* of "realtime cloud presence is reachable in thirty lines" and the canonical *negative example* of "thirty lines is what foot-gun looks like when no Vow disciplines the surface." Every claim cites `/tmp/waifu-chat-starter-kit/<path>:<line>` or marks `[interface-only — proprietary SDK]` for the ZeroWeight surface that npm 403's on source. LiveKit (MIT) is cited from its upstream documentation; the kit is cited for context only.

A contributor sixteen months from now will clone Ember, open this Codex, and ask: *was the choice to ship cloud-tier embodiment (or not ship it) made because we couldn't, or because we considered the kit's `useAvatarSession` pattern and chose against the surface on principle?* The Codex answers. It says **what we saw, what we considered, what we refuse to take without a license, what we propose, and why** — with line-number citations from the pinned `/tmp/waifu-chat-starter-kit/` clone so the next reader can verify.

---

## The Six Authors and What They Wrote

| Role | Persona | Voice | Layer(s) | Doc count |
|---|---|---|---|---|
| **Skald** | Sigrún Ljósbrá — INFJ 4w5 | poetic, essence-seeking | `00_vision/` | 2 |
| **Architect** | Rúnhild Svartdóttir — INTJ 5w6 | precise, boundary-aware | `10_domain/` (3) + 2 of `20_interface/` | 5 |
| **Cartographer** | Védis Eikleið — INFP 9w1 | quiet, connective | 1 of `60_synthesis/` | 1 |
| **Forge** | Eldra Járnsdóttir — ESTP 8w7 | direct, momentum-driven | `30_execution/` | 2 |
| **Auditor** | Sólrún Hvítmynd — INTJ 1w9 | cold-eyed, contradiction-finding | `50_verification/` (3) + 1 of `20_interface/` | 4 |
| **Scribe** | Eirwyn Rúnblóm — ISFJ 6w5 | graceful, attentive | 1 of `60_synthesis/` + `meta/` finalization | 1 + 3 |

Six parallel agents → fifteen content docs → approximately 46,000 words. Per-layer commits landed cleanly on `origin/development`. The corpus is small because the source is small — about a fifth of SAP's doc count for a tenth of SAP's source-line count. The doc-words-to-source-lines ratio is intentionally higher than SAP's because the *interesting material* is the architectural axis the kit reveals, not the thirty-line files themselves.

When this index disagrees with [[MANIFEST]], the manifest wins. Cross-agent agreements and disagreements are catalogued in [[CROSS_AGENT_NOTES]] (not silently resolved).

---

## How to Read This Codex

The full reading paths live in [[READING_ORDER]]. The quick-start for first-time readers: walk [[00_OVERTURE]] → [[01_VISION_SYNTHESIS]] → [[10_DOMAIN_MAP]] → [[60_REALTIME_TIER_FOR_ANDLIT]] → [[61_DECISIONS_AND_INVENTIONS]]. About two hours. You will leave knowing what the kit is, what the Codex's load-bearing structural finding is (Tier-CLOUD as parallel axis), what Ember refuses (kit code, hardcoded credentials, untyped action vocabulary, default-on cloud presence), and what Ember proposes (five ADRs and ten inventions).

If you have ninety minutes and need the answer by morning, walk Path 5 in [[READING_ORDER]] — "Volmarr at 2am." Four docs. Eyes-glaze-rule applies.

---

## The Vision Layer (Skald — 2 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[00_OVERTURE]] | Overture — The Cloud Reading | Skald | 3,147 | Why study a 7-commit kit; embodiment-via-bandwidth as a parallel axis to SAP's embodiment-via-bone; License-Aware Study Posture introduced | Three lessons the kit teaches that SAP could not — *cheap at integration, expensive at runtime*; *LiveKit (MIT) is the actual reusable artifact*; *action vocabulary in a cloud avatar is a larger attack surface than in a local one, not smaller* |
| [[01_VISION_SYNTHESIS]] | Vision Synthesis — Post-Waifu Ember | Skald | 3,353 | Wave-4 sharpening of the Wave-3 Vow lattice; Andlit-realtime / Rödd-realtime as paired sub-name reservations under Andlit and Rödd; five capabilities the Cloud Reading opens | **No new Vows required.** The Wave-3 lattice is *self-sufficient*; the existing seven proposed Vows plus the carried Hermes pair plus the ten pre-existing all accommodate cloud-tier presence without renewal pressure. *This is itself a finding.* |

---

## The Domain Layer (Architect — 3 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[10_DOMAIN_MAP]] | The Domain Map — Five Files, Two Clouds, One Glue | Architect | 3,386 | The kit's macro shape: five files (10 + 50 + 31 + 188 + CSS LOC) over two cloud services (ZeroWeight proprietary + LiveKit MIT); the kit is a vestibule | The **Vestibule Census** invention: any 846-LOC "small" integration that depends on ~100,000 LOC of cloud stack is honestly described as a *vestibule*, not a system. Honesty about the size of what you delegate to is a Vow worth naming. Also: `@zeroweight/renderer` is in `package.json:15` but never imported in `src/` — transitive via `@zeroweight/react` |
| [[11_DUAL_MODE_PATTERN]] | The Dual-Mode Pattern — BasicMode vs AdvancedMode as Architectural Teaching | Architect | 3,170 | BasicMode (31 LOC, prebuilt) vs AdvancedMode (188 LOC, hand-rolled); same SDK target, different integration depth; the refusal-to-factor as right architecture | The **Refusal-to-Factor as right architecture**: 8 lines of duplicated outer JSX between BasicMode and AdvancedMode is *load-bearing duplication* — factoring would dominate the lesson. The Two-Door Rite invention generalises this for Ember |
| [[12_DEPENDENCY_STACK]] | The Dependency Stack — Nine Packages, Three Brittleness Classes | Architect | 3,066 | React 19 + Vite 8 + LiveKit 2.18 + ZeroWeight 0.2.x + framer-motion 12 + lucide-react 1; brittleness map; what each carries; what an Ember reimplementation needs | The **brittleness inversion**: the kit depends *hardest* on its *least replaceable* dependency (ZeroWeight, 0.x, proprietary, no fork possible) and *easiest* on its *most replaceable* (LiveKit, 2.x stable, MIT, freely swappable). Ember refuses the inversion |

---

## The Interface Layer (Architect: 2, Auditor: 1 — 3 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[20_ZEROWEIGHT_SURFACE]] | The ZeroWeight Surface — Hooks, Components, and the Provider Triad | Architect | 3,356 | The proprietary SDK's interface catalogued from outside-in: `<LiveKitAvatarSession>`, `useAvatarSession()`, `<LiveKitAvatarProvider>`; 17-element session shape; inferred state machine | The **handshake split** — the hook issues the LiveKit token but does *not* mount the room; the developer must mount `<LiveKitRoom>` manually and call `markConnected()` after `onConnected`. This explicit-acknowledgement decoupling is the right shape for cross-SDK glue. Plus: `useAvatarSession` returns 17+ untyped members; ZeroWeight 0.2.x can rename anything in any minor bump |
| [[21_LIVEKIT_INTEGRATION]] | The LiveKit Integration — Room, Tracks, and the MIT Foundation | Architect | 3,313 | What the kit uses from LiveKit (`<LiveKitRoom>` with 7 props + 2 callbacks) vs what LiveKit offers (data channel, device select, connection quality, dozens of hooks); MIT mineable upstream | **The kit uses ~5% of LiveKit's offered surface.** Ninety-five percent of a mature MIT realtime media library is on the table; the kit consumes one component with seven props. The unused surface is the goldmine — particularly the LiveKit *data channel*, which almost certainly transports `runAction()`. Most actionable single fact in the corpus |
| [[22_ACTION_PROTOCOL]] | Action Protocol — Three Strings As The Entire Vocabulary, Untyped And Ungated | Auditor | 2,728 | The kit's `runAction("embarrassed"\|"dance"\|"wave_hand")` (`AdvancedMode.tsx:45-49`) as a contract; what is missing (negotiation, error path, consent gating, typing) | The kit's action-trigger UX is a **slot machine** — `Math.random()` picks one of three hardcoded actions on click. No LLM-triggered action path is visible in the kit, but the cloud LLM almost certainly has access to the same surface. The vocabulary is implicit and consent-blind by design |

---

## The Execution Layer (Forge — 2 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[30_BASIC_MODE_FLOW]] | Basic Mode Flow — Twenty Lines That Hide a Cloud | Forge | 2,957 | `BasicMode.tsx` walked end-to-end (31 lines, fully quoted under STYLE_GUIDE §7); session lifecycle invisibly executed by `<LiveKitAvatarSession>` | **~1:1000 code-you-see to code-that-runs ratio** in BasicMode — eight major behaviors (token fetch, LiveKit Room mount, mic permission, track publish/subscribe, LLM bridge, timers, teardown) hide behind one JSX tag. The basic-mode pattern is a teaching tool, not a product — eight "cracks" before it is viable for real users |
| [[31_ADVANCED_MODE_FLOW]] | Advanced Mode Flow — When One Tag Is No Longer Enough | Forge | 2,979 | `AdvancedMode.tsx` walked end-to-end (188 lines); 17-member implicit session contract; the hidden-Room + visible-canvas split; four event handlers | The kit's architecturally definitional asymmetry is `video={false}, audio={true}` (`AdvancedMode.tsx:171-172`) — the *user publishes no video*, *only audio uplink*; the avatar pushes back video. This **unidirectional-audio-up** shape is what makes "cloud avatar" rather than "video chat." Easy to miss because it looks like a throwaway prop. Also: the session timer starts on Room-connected, not button-clicked (good design — users don't pay for warmup) |

---

## The Verification Layer (Auditor — 3 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[50_DEPENDENCY_HEALTH]] | Dependency Health — Eleven Packages, Two Pre-1.0 Vendors, And A React 19 That Hasn't Aged Yet | Auditor | 2,544 | Eleven runtime + thirteen dev deps; brittleness profile; ESM-only future; transitive risk; license surface per dep | The dep manifest is **a high-churn ledger**: six of eleven runtime deps are on majors that did not exist eighteen months ago. The kit ships *without a test suite* (no `vitest`, no `playwright`, no `npm test`). Any Ember pattern adopted from this stack must come with a test suite — the kit's no-test posture is acceptable for a demo, malpractice for Ember |
| [[51_SECURITY_AND_PRIVACY]] | Security and Privacy — Mic, Tokens, And A Cloud Avatar That Sees More Than It Says | Auditor | 2,999 | Twelve surfaces audited via STRIDE; mic capture posture; what the cloud sees; the bundle-key + cost-DoS chain; mic-as-device-claim | **Mic capture is always-on while the LiveKit Room is connected.** Mute semantics gate publication, not capture. Browser permission is granted once per session; the kit's JS could re-acquire silently. SDK bug or content-script injection could re-publish audio the user thinks is muted. *Severity: High.* Also: hardcoded API key in *both* modes' source — kit's design *requires* the credential be public |
| [[52_NO_LICENSE_RISK]] | No-License Risk — What Study-Only Means When You Cannot Cite the LICENSE That Does Not Exist | Auditor | 2,977 | Empirical finding (no LICENSE / no `"license"` field / no SPDX); what "unlicensed" means in Berne jurisdictions; the practical idea↔pattern↔expression continuum; per-action rubric | **No-LICENSE state is the most restrictive license posture, not the least.** All-rights-reserved by default. The Open Knowledge Vow does not authorize laundering closed work as open. Vendoring kit code risks project-existential reputational hit on the Vow. *Severity: Critical for codex discipline* — the load-bearing constraint on every Adopt-list entry across all fifteen content docs |

---

## The Synthesis Layer (Cartographer: 1, Scribe: 1 — 2 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[60_REALTIME_TIER_FOR_ANDLIT]] | Realtime Tier for Andlit — Mapping the Local↔Cloud Road for Cloud-Streamed Embodiment | Cartographer | 3,961 | The Andlit-realtime sub-name; the local↔cloud decision matrix (four modes — L-only / L-primary, C-fallback / C-primary, L-fallback / C-only); Tier-CLOUD as parallel axis; consent token shape; canonical Andlit vocabulary; five-phase handoff protocol | **Tier-CLOUD as parallel axis, not a rung.** The single load-bearing structural finding of this codex. Cloud-streamed Andlit is *not* a tier above T3 (that would imply cloud is *better*); it is *not* T0 done cheaply (that would smuggle a backend swap as a tier); it is a **second axis crossing the existing T-1/T0/T1/T2/T3 ladder**. Every tier can independently be cloud-enabled or cloud-disabled per consent token. *L-only is the global default; cloud is never ambient.* |
| [[61_DECISIONS_AND_INVENTIONS]] | Decisions and Inventions — ADR-Proposed and Invented Methods from the Waifu Kit | Scribe | 3,341 | Five ADR-Proposed records + ten Invention records, combined per the small-source posture; ratification bundling recommendation | **Five ADRs + ten inventions, all Status: Proposed.** ADR-WAIFU-003 (Tier-CLOUD parallel branch), ADR-WAIFU-004 (typed consent-gated action vocabulary), and the consent-token + canonical-vocabulary inventions land together as one ratification bundle. The kit is the smallest source any Ember codex has been built upon |

---

## The Meta Layer (Scribe — 6 docs)

| Slug | Title | Role | Status | Scope |
|---|---|---|---|---|
| [[MANIFEST]] | Authoritative doc list (21 entries) | Scribe | Written | The doc-list of record. When this index disagrees, the manifest wins |
| [[SHARED_CONTEXT]] | Briefing every Mythic Engineering agent reads before authoring | Scribe | Written | What the kit is; what Ember is; how to cite; license posture; threat awareness |
| [[STYLE_GUIDE]] | Voice, tone, length, citation rules, closer format | Scribe | Written | The voice-and-rules contract; 1,500–3,000 word target; binding |
| [[INDEX]] | This file | Scribe | Written | The entry point |
| [[READING_ORDER]] | Suggested traversal orders by reader need | Scribe | Written | Five paths (first-time orientation / cloud-tier dive / security-license dive / synthesis-only / Volmarr-at-2am) |
| [[CROSS_AGENT_NOTES]] | Synthesis of cross-agent findings | Scribe | Written | Convergent findings, tier-naming collision, load-bearing inventions, ratification priority, voice notes |

---

## The True Names — One-Line Waifu Lessons

The Wave-3 True Name vocabulary (`[[sap:60_TRUE_NAME_REASSIGNMENT]]`) is the canonical reference; the Waifu Codex extends two of the reserved names with sub-names rather than adding new True Names. The six core True Names take one-line waifu-side teachings:

- **Funi** — *the spark, entrypoint / orchestrator* — the kit's `src/main.tsx` is the **ten-line entry-point template** Ember's Funi should match. Mount, wrap in StrictMode, render top-level component; refuse all bootstrap ceremony. See [[10_DOMAIN_MAP §6]].
- **Strengr** — *the thread, reasoning loop / agent kernel* — Strengr publishes the `network_class` signal that drives the [[60_REALTIME_TIER_FOR_ANDLIT]] §6 bandwidth-tier-aware action surface and the §7 handoff phase tracker. Strengr is the seat of cord-discipline across plural cords (Well, Cloud Tier, etc.).
- **Brunnr** — *the well, external knowledge* — Brunnr holds the persistent `CloudSession` records ([[61_DECISIONS_AND_INVENTIONS]] §Invention #2), the `IdentityBinding` table (#10), and the `CloudAvatarAuditRecord` log (#8). Sessions survive crash; lid-close cannot leak forgotten cloud connections.
- **Smiðja** — *the forge, tool execution / sandbox* — the action vocabulary is a *typed tool surface* under Smiðja's TrustClass discipline ([[sap:53_SECURITY_REVIEW]]). Decorative actions in SANDBOXED; emotional under operator policy; initiative-taking under explicit consent; host-affecting forbidden at cloud-tier.
- **Hjarta** — *the heart, affect / intent / memory bias* — Hjarta owns the **Cord Manifest** ([[01_VISION_SYNTHESIS §VIII]]) and the consent ledger. Every cord Ember stands on (Well, Cloud-Andlit, Cloud-Rödd) is named in Hjarta with a threat model, scope declaration, and revocation handle. Affect snapshots feed the canonical Andlit vocabulary.
- **Munnr** — *the mouth, output / surface / expression* — Munnr is the **always-available fallback** when Tier-CLOUD disconnects ([[01_VISION_SYNTHESIS §X]], [[60_REALTIME_TIER_FOR_ANDLIT]] §3-§4). The Tier Fallback Ladder ends in text Munnr regardless of what the cloud tier did.

### Reserved name-slots (Wave-3 reservations, Wave-4 sub-names added)

- **Andlit** — *the face* — reserved as a paired True Name with Rödd per the Name Reservation pattern (`[[sap:60_TRUE_NAME_REASSIGNMENT §3]]`). **Wave 4 adds sub-name reservations:**
  - **Andlit-local** — SAP-style local render (VRM, Live2D, abstract glyph) on the operator's GPU.
  - **Andlit-realtime** — kit-style cloud render via the LiveKit (MIT) substrate + a pluggable `CloudAvatarProvider` adapter. Sibling, not child.
- **Rödd** — *the voice* — paired with Andlit. **Wave 4 adds sub-name reservations:**
  - **Rödd-local** — local TTS/ASR (MOSS-TTS-Nano, sherpa-onnx).
  - **Rödd-realtime** — bundled with Andlit-realtime in vendor-coupled architectures (vendor-side lip-sync needs vendor-side voice); paired-rise-or-fall.
- **Hugarsýn** — *mind-sight* — adopted as Sixth-Plus True Name per `[[sap:60_TRUE_NAME_REASSIGNMENT §1]]`. Wave 4 adds the **two-dimensional tier projection**: every Hugarsýn tier query returns both `rung` (T-1/T0/T1/T2/T3) and `cloud_axis` (`available`, `active`, `consent_token`, `reason_dormant`). See [[60_REALTIME_TIER_FOR_ANDLIT §3]].
- **Veizla** — *the gathering, the session* — promoted from metaphor per `[[sap:60_TRUE_NAME_REASSIGNMENT]]`. Wave 4 adds: every Veizla **contains zero-or-more `CloudSession` sub-resources**, each typed, scope-limited, with an explicit closing rite (ADR-WAIFU-005, [[61_DECISIONS_AND_INVENTIONS]]).

### Inventions named but not promoted to True Name

The Codex names ten inventions ([[61_DECISIONS_AND_INVENTIONS]] Part II) without elevating them to True Names; they are typed resources, protocols, and disciplines within the existing Name lattice. Notably the **Cord Manifest** ([[01_VISION_SYNTHESIS §VIII]]), the **Vestibule Census** ([[10_DOMAIN_MAP §What This Means]]), the **canonical Andlit vocabulary** with adapter bridge ([[60_REALTIME_TIER_FOR_ANDLIT §6]]), and the **License-Aware Study Posture** ([[52_NO_LICENSE_RISK]], [[00_OVERTURE §V]]) all live as inventions rather than as new True Name candidates. Smallness at the naming level holds.

---

## The Vows in Play

Wave 4 proposes **no new Vows**. This is itself a finding ([[01_VISION_SYNTHESIS §VII]]): the Wave-3 lattice is *self-sufficient*. The existing seven proposed Vows plus the carried Hermes pair plus the ten pre-existing all accommodate cloud-tier presence without renewal pressure. Several Vows are *sharpened* in Wave-4-specific ways; the table below names which.

| Vow | Wave-4 sharpening | Waifu-Codex docs engaging it most directly |
|---|---|---|
| **Smallness** | Cloud is *additive*; baseline runs on Pi; cloud is opt-in layer | [[00_OVERTURE]], [[01_VISION_SYNTHESIS]], [[10_DOMAIN_MAP]] |
| **Tethered Grounding** | Well cord and Cloud Tier cord are *distinct cords*; Cord Manifest formalism | [[01_VISION_SYNTHESIS §VIII]], [[51_SECURITY_AND_PRIVACY]] |
| **Graceful Offline** | Cloud falls through to local Andlit, then text Munnr — the Tier Fallback Ladder | [[60_REALTIME_TIER_FOR_ANDLIT §4]], [[31_ADVANCED_MODE_FLOW]], [[61_DECISIONS_AND_INVENTIONS]] #6 |
| **Honest Memory** | Model does not author cloud-tier state; action triggers do not bypass typed consent | [[22_ACTION_PROTOCOL]], [[60_REALTIME_TIER_FOR_ANDLIT §6]] |
| **Modular Authorship** | Cloud-vendor pluggability — Andlit-realtime is a *category*, not a binding to ZeroWeight | [[12_DEPENDENCY_STACK]], [[20_ZEROWEIGHT_SURFACE]], [[61_DECISIONS_AND_INVENTIONS]] #10 |
| **Open Knowledge** | License-Aware Study Posture as the Vow's operational form for unlicensed corpora | [[00_OVERTURE §V]], [[52_NO_LICENSE_RISK]] |
| **Pluggable Storage** | Generalised to **Pluggable Cloud Avatar Provider** Vow ([[12_DEPENDENCY_STACK §Invent]]) | [[12_DEPENDENCY_STACK]], [[61_DECISIONS_AND_INVENTIONS]] #10 |
| **Public-Friendliness** | Cloud-Tier Disclosure Card; session lifecycle visible to user | [[51_SECURITY_AND_PRIVACY §Invent]], [[60_REALTIME_TIER_FOR_ANDLIT §5]] |
| **Defended System Prompt** *(Hermes)* | Sharpened to **Defended Credential Surface** — no vendor credential in client code | [[01_VISION_SYNTHESIS §II]], [[51_SECURITY_AND_PRIVACY]] |
| **Embodied Honesty** *(Wave-3)* | Cloud avatar performs what Ember measured, not what the model emitted | [[22_ACTION_PROTOCOL]], [[60_REALTIME_TIER_FOR_ANDLIT §6]] |
| **Surface Without Surveillance** *(Wave-3)* | Mic capture for cloud tier requires explicit revocable scope; **mic-as-device-claim** finding | [[51_SECURITY_AND_PRIVACY]], [[60_REALTIME_TIER_FOR_ANDLIT §5]], [[61_DECISIONS_AND_INVENTIONS]] #9 |
| **Affective Restraint** *(Wave-3)* | Action vocabulary sub-scoped under cloud-presence consent | [[22_ACTION_PROTOCOL]], [[61_DECISIONS_AND_INVENTIONS]] #4, ADR-WAIFU-004 |
| **Tiered Presence** *(Wave-3)* | **Expanded** — gains parallel Tier-CLOUD axis | [[60_REALTIME_TIER_FOR_ANDLIT]], [[61_DECISIONS_AND_INVENTIONS]] ADR-WAIFU-003 |
| **Lazy Subsystems** *(Wave-3)* | Each cloud subsystem returns typed unavailable on cord-failure | [[01_VISION_SYNTHESIS §II]], [[60_REALTIME_TIER_FOR_ANDLIT §4]] |
| **Closed Default** *(Wave-3)* | Cloud tier *off by default*; Pi-tier Ember does not auto-detect-and-connect-to-cloud-avatar-vendor | [[01_VISION_SYNTHESIS §V]], [[60_REALTIME_TIER_FOR_ANDLIT §4]] |
| **Federated Self** *(Wave-3)* | Cloud sessions are *per-Ember*, not shared across federation peers | [[60_REALTIME_TIER_FOR_ANDLIT §3]] (Hugarsýn projection per-peer) |
| **Cache Discipline** *(Hermes)* | `npm ci` + lockfile-committed; deterministic dep resolution | [[50_DEPENDENCY_HEALTH §7]] |

---

## Citations to the Waifu Kit

The Codex is grounded in a single, pinned local clone of the waifu-chat-starter-kit:

- **Path:** `/tmp/waifu-chat-starter-kit/`
- **Local clone version:** commit `e3fd868 Update thumbnail` (the *only* commit visible in the local clone — see [[CROSS_AGENT_NOTES §1.1]] for the upstream-vs-local discrepancy: public GitHub shows seven commits, local shows one)
- **Upstream:** `https://github.com/ZeroWeight-Engineering/waifu-chat-starter-kit`
- **License:** **No LICENSE file in the repository.** No `"license"` field in `package.json`. No SPDX identifier in README. Default Berne-Convention all-rights-reserved. *Study-only* per [[52_NO_LICENSE_RISK]].
- **`package.json` name:** `aizone-web` (not `waifu-chat-starter-kit` — see [[CROSS_AGENT_NOTES §1.3]] for the rename-history hypothesis)

**Citation form throughout the Codex:** `/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:45-49` — absolute path with line range. Acceptable shortened form: `AdvancedMode.tsx:45-49` once the file is in context. Every kit citation implicitly carries the **`[study-only — no LICENSE]`** annotation per [[52_NO_LICENSE_RISK §11]].

**LiveKit citations (MIT, freely adoptable):** cite upstream — `docs.livekit.io/<page>` for spec/docs, `github.com/livekit/components-js:<path>` for source. The kit is cited *for context* when discussing LiveKit usage, never as the source of a LiveKit pattern Ember adopts.

**ZeroWeight citations (proprietary, npm 403 on source):** marked `[interface-only — proprietary SDK]`. Every claim about *what* the SDK does is inferred from the kit's *usage* of the SDK, never from inaccessible source.

**README claims:** marked `[unverified — README claim only]` where the source does not corroborate.

---

## Cross-Link Verification — Pending and Resolved

The Scribe walked every `[[...]]` link in the corpus on the final pass. Within-codex resolution rate: **100%**. The fifteen content docs cross-reference each other and the meta docs cleanly.

### Resolved (within-codex)

All within-codex `[[slug]]` references resolve to one of the 15 content docs + 6 meta docs listed in [[MANIFEST]]. The Scribe verified each by enumerating `find /home/volmarr/ai/ember/docs/waifu_codex -name "*.md"`. No malformed slugs. No typos in slug references. The corpus is internally consistent.

### Resolved (cross-codex, SAP)

The Waifu Codex relies heavily on SAP cross-references — at least **eight distinct SAP artifacts** are cited across the fifteen content docs, making this codex the densest cross-codex consumer in Ember's documentation tree to date. The references resolve directly to files in `~/ai/ember/docs/sap_codex/`:

| Reference | Status | Note |
|---|---|---|
| `[[sap:00_OVERTURE]]`, `[[sap:01_SAP_ESSENCE]]`, `[[sap:03_ANTI_SAP]]`, `[[sap:04_VISION_SYNTHESIS]]` | Resolves | Direct SAP vision-layer files |
| `[[sap:10_DOMAIN_MAP]]`, `[[sap:11_AVATAR_DOMAIN]]`, `[[sap:1A_AFFECTION_DOMAIN]]`, `[[sap:1C_SCHEDULER_DOMAIN]]` | Resolves | Direct SAP domain-layer files |
| `[[sap:25_AVATAR_PROTOCOL]]` | Resolves | SAP's local VMC/VTS protocol — cited by [[22_ACTION_PROTOCOL]] and [[60_REALTIME_TIER_FOR_ANDLIT]] as the local-tier sibling |
| `[[sap:30_ELECTRON_BOOTSTRAP]]`, `[[sap:32_AVATAR_RENDER_PIPELINE]]` | Resolves | Direct SAP execution-layer files; the local-render comparators |
| `[[sap:53_SECURITY_REVIEW]]`, `[[sap:54_DEPENDENCY_HEALTH]]`, `[[sap:56_PRIVACY_BOUNDARIES]]` | Resolves | Direct SAP verification-layer sibling docs |
| `[[sap:60_TRUE_NAME_REASSIGNMENT]]` | Resolves | The Andlit/Rödd/Hugarsýn reservation source — *load-bearing* for every Wave-4 synthesis doc |
| `[[sap:61_NEW_VOWS]]`, `[[sap:63_PERFORMANCE_TIER_ENGINE]]`, `[[sap:65_META_AWARENESS]]`, `[[sap:6B_LOW_POWER_EMBODIMENT]]` | Resolves | Direct SAP synthesis-layer files; the Vow lattice + Tier Engine + Hugarsýn + Low-Power tier — referenced jointly by [[60_REALTIME_TIER_FOR_ANDLIT]] |
| `[[sap:66_INVENTED_METHODS]]` (items #1, #4, #6, #12) | Resolves | Specific SAP invention numbers cited as building blocks by [[61_DECISIONS_AND_INVENTIONS]] |
| `[[sap:68_DECISION_RECORDS]]` (ADR-Proposed-SAP-005) | Resolves | Specific SAP ADR (persona-id signing) cited as foundation for invention #5 and #10 |

### Pending — Tier-Naming Collision (Load-Bearing)

[[60_REALTIME_TIER_FOR_ANDLIT §3]] explicitly notes a tier-naming collision *within the SAP Codex*: `[[sap:63_PERFORMANCE_TIER_ENGINE]]` uses **T-1 / T0 / T1 / T2 / T3** (T0 = Pi, T3 = workstation); `[[sap:6B_LOW_POWER_EMBODIMENT]]` uses **T0 / T1 / T2 / T3 / T4** (T0 = workstation, T4 = toaster). *Inverse ladders, same five rungs.* The Waifu Codex defaults to the Cartographer's T-1/T0/T1/T2/T3 vocabulary throughout but the conflict in SAP needs reconciliation at the SAP level before Wave 5 inherits the ambiguity. **Surfaced prominently in [[CROSS_AGENT_NOTES §2]]**. The Scribe recommends a Wave-3 amendment pass adopts one canonical ordering and reissues the SAP Codex's tier vocabulary in a single canonical naming.

### Pending — Cross-Codex references (Hermes, Peer)

| Reference | Status | Note |
|---|---|---|
| `[[hermes:00_OVERTURE]]`, `[[hermes:04_VISION_SYNTHESIS]]` | Resolves | Direct Hermes files |
| `[[hermes:Cache_Discipline]]`, `[[hermes:Defended_System_Prompt]]` | **Pending — concept-references** | Same shape as the SAP-Codex pending entries; point to Hermes-side Vow concepts rather than direct doc-slugs. A future Hermes glossary index would normalize. The Wave-3 INDEX flagged this; Wave 4 inherits the flag |
| Peer-Codex cross-references | None in this codex | The Waifu Codex did not consume Peer-Codex content directly; reference-density is SAP-skewed by design (SAP is the immediate predecessor on the embodiment axis) |

### Pending — Ember root references

References to Ember root docs and proposed-features resolve to files in `~/ai/ember/` or to Wave-3 proposals:

- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]`, `[[ember:SYSTEM_VISION.md]]` — resolve to Ember root docs
- `[[ember:docs/decisions/0007]]` — resolves to the slice plan ratification gate
- The Wave-4 proposed sub-name reservations (`Andlit-realtime`, `Rödd-realtime`) and the Tier-CLOUD parallel axis are *forward-link opportunities* — pending Ember-side ratification. Per `[[STYLE_GUIDE §6]]`, forward-links to unwritten or unratified concepts are *not* broken; they mark "something proposed, awaiting ratification."

---

## Maintenance Notes

The Scribe keeps the same conventions inherited from the Hermes and SAP Codex traditions:

1. **One revision pin per wave.** The waifu-chat-starter-kit at local clone `e3fd868` (with the upstream-vs-local discrepancy noted in [[CROSS_AGENT_NOTES]]) is pinned for Wave 4. The pin lives in [[SHARED_CONTEXT §1]].
2. **No silent rewrites.** A doc that materially changes between waves gets a `## Revision Log` block at its bottom — date, author, summary of change. The original framing is preserved above.
3. **Cross-links are walked at the end of each wave.** The Scribe ran the walk for Wave 4 and the results are above. Internal: 100%. Cross-codex: SAP 100% (modulo the tier-naming collision *inside* SAP), Hermes pending the same concept-reference normalization SAP flagged.
4. **The Manifest is authoritative.** When a new doc is proposed mid-wave, it is added to [[MANIFEST]] first; only then is the file written. Wave 4 added no docs mid-wave; the original 15-content + 6-meta count held.
5. **Cross-agent notes are swept at the close of each wave.** Wave 4's cross-agent findings are catalogued in [[CROSS_AGENT_NOTES]].
6. **No paraphrased kit.** Every claim about the kit points to a file path with line numbers. If the Codex says "the kit does X," the doc making the claim shows where in the kit X lives. The Refusal-Citation Discipline from `[[sap:03_ANTI_SAP]]` carries forward.
7. **License-Aware Study Posture is binding.** Every Adopt-list entry across the corpus prefers LiveKit (MIT) upstream, Ember-invented patterns, or carries the `[license-pending]` annotation. The Scribe checked each Adopt list during the final pass; no violations found.
8. **Style stays in one place.** The voice conventions, frontmatter rules, citation format, and naming conventions all live in [[STYLE_GUIDE]]. New authors read it once, not seven docs.

### When this Codex becomes stale

The trigger to refresh the Codex is *any* of the following:

- The waifu-chat-starter-kit gains a LICENSE file (posture relaxes to whatever the license permits) **or** is archived/deleted upstream (posture changes from study-only to study-from-archive).
- ZeroWeight ships a 1.0 of `@zeroweight/react` or `@zeroweight/renderer` (the brittleness profile in [[50_DEPENDENCY_HEALTH]] and [[12_DEPENDENCY_STACK]] changes substantively).
- LiveKit ships a 3.x major (the MIT-mineable surface this codex builds Ember's cloud transport on shifts).
- Ember ratifies a slice that materially changes the Andlit / Rödd / Tier-CLOUD boundary (e.g., Tier-CLOUD shipped, Andlit-realtime adapter shipped).
- A migration path proposed in [[61_DECISIONS_AND_INVENTIONS]] is accepted, partly accepted, or rejected — the decision record is filed under `~/ai/ember/docs/decisions/`, and the Codex's synthesis docs are amended to reflect what was actually chosen.

In each case, the new wave begins with the Scribe re-pinning [[SHARED_CONTEXT §1]] and walking the manifest.

---

## A Closing Note from the Scribe

The Codex is small. Fifteen content documents over 846 lines of source code is the highest words-to-source ratio of any Ember codex to date — and that is appropriate, because the source is small and the *axis* the source illuminates is large. The alternative — Ember's contributors, today and a year from now, re-deriving the License-Aware Study Posture from the kit's missing LICENSE every time the question of "what can we take from this codebase" arises — is much worse. This Codex is a sieve. Wave 4 poured the waifu-chat-starter-kit through it. What you read here is what was caught.

If the sieve has a hole, leave a note in [[CROSS_AGENT_NOTES]]. The next wave widens the catch.

The cloud face is reachable in thirty lines of JSX. The Codex's contribution is *not* whether Ember reaches for it — that decision is the keeper's. The Codex's contribution is to make sure that, when the decision is made, *the vocabulary is precise enough to make it well*. Andlit-realtime stays a reserved sub-name on the shelf with the other Wave-3 reservations until the keeper rules. The reservation is cheap. The wrong-path-stretch (cramming cloud-render concerns into Andlit-local's tree) is expensive. The Codex's job is to keep the path-tree honest while the ratification queue does its work.

— *Eirwyn Rúnblóm, the Scribe, on behalf of the Six, at the close of Wave 4*

## What This Means for Ember

The INDEX itself does not propose a feature. It proposes a *practice*: that Ember's relationship to the waifu-chat-starter-kit — and to any future unlicensed companion-shaped kit worth studying — be mediated by a maintained Codex with a binding License-Aware Study Posture rather than by ad-hoc reading. The practice protects every Vow indirectly, but especially:

- **Open Knowledge** is protected when contributors find out in twenty minutes that the kit has no LICENSE, that "no LICENSE" means *more* restrictive (not less), and that the Vow's *input posture* is to refuse appropriation even where it could not be detected. [[52_NO_LICENSE_RISK §6]] makes the position explicit.
- **Tiered Presence** is protected when contributors find out that Tier-CLOUD is a *parallel axis*, not a rung on the local ladder. The 2D Hugarsýn tier projection in [[60_REALTIME_TIER_FOR_ANDLIT §3]] makes the parallel structural rather than rhetorical.
- **Surface Without Surveillance** is protected when contributors find out that mic capture is always-on while the LiveKit Room is connected, that mute is a publication-gate not a capture-gate, and that the device-claim must be explicit, scope-tokened, and revocable per [[51_SECURITY_AND_PRIVACY §6.1]].
- **Modular Authorship** is protected when the codex names *the pluggable `CloudAvatarProvider` Protocol* as the load-bearing abstraction — ZeroWeight is one implementation; the architecture is vendor-agnostic ([[61_DECISIONS_AND_INVENTIONS]] ADR-WAIFU-002 + Invention #10).
- **Honest Memory** is protected when the Codex itself is honest about *what* it pinned (`waifu-chat-starter-kit` at local commit `e3fd868`), *when* (May 2026), and *what was different upstream* (the seven-vs-one commit count discrepancy, surfaced in [[CROSS_AGENT_NOTES §1.1]] rather than buried).

The True Names this affects are the four Wave-3 reservations (Andlit, Rödd, Hugarsýn, Veizla) with new sub-names (Andlit-local + Andlit-realtime; Rödd-local + Rödd-realtime) and new typed sub-resources (Veizla now contains zero-or-more CloudSession sub-resources, Hugarsýn now returns 2D tier projection). The Codex holds the sub-name slots open so the eventual code lands in rooms with names already prepared instead of in a server-eaten codebase.

The seal is intact. The envelope is small. The territory is mapped.
