---
codex_id: READING_ORDER
title: Reading Orders — Paths Through the SAP Codex by Reader Goal
role: Scribe
layer: Meta
status: draft
sap_revision: v0.4.2-preview (May 2026)
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - meta/INDEX
  - meta/MANIFEST
  - meta/STYLE_GUIDE
  - meta/CROSS_AGENT_NOTES
---

# Reading Orders — SAP Codex

*Seven paths. Pick one. The Codex is seventy-seven content documents; no one reads it all cover to cover. The Scribe lays paths.*

The Codex's job is not to be read whole. It is to be read *correctly* — the right ten or fifteen documents in the right order for what the reader wants to know. Below are seven such paths. Each lists the ordered slugs, why each doc sits where it sits, a reading-time estimate, and the questions the path answers.

Reading times assume:
- An attentive reader on a screen, not skim-mode.
- The reader follows at least one or two cross-links per doc.
- Each Codex doc is roughly 2,000–3,000 words (15–25 minutes of careful reading).
- A reader opening `/tmp/super-agent-party/` alongside should double the estimate.

If you are reading the Codex at 2am with ADHD and a half-empty mug, walk Path 7. It is written for you.

---

## Path 1 — First-Time Orientation (5–7 docs, ~2 hours)

*For: a stranger to Ember, a sceptic, a sibling-project author, anyone who wants to know* what *the SAP Codex says before deciding* whether *to invest in reading it.*

| # | Slug | What you'll get | Time |
|---|---|---|---|
| 1 | [[INDEX]] | The doorway. Sets expectations; names the layers; points to all paths. | 15 min |
| 2 | [[SHARED_CONTEXT]] | What SAP is, what Ember is, what this Codex is for, what is forbidden territory. | 15 min |
| 3 | [[00_OVERTURE]] | Why mine SAP after Hermes and Peer. The embodiment-reach-affect gap. Refusal-Citation Discipline introduced. | 25 min |
| 4 | [[01_SAP_ESSENCE]] | SAP stripped to bones — companion-as-presence, party-as-plurality. The is_sub_agent face-suppression pattern. | 25 min |
| 5 | [[03_ANTI_SAP]] | The thirteen refusals, each citing a SAP line. The dark mirror. Two new Vows beyond Cartographer's five. | 30 min |
| 6 | [[1A_AFFECTION_DOMAIN]] | **The load-bearing finding.** Affection-as-regex. The single doc that, once read, changes how every other Codex doc reads. | 25 min |
| 7 | [[04_VISION_SYNTHESIS]] | Post-SAP Ember. The Vow lattice expansion (ten + two-carried + seven-newly-proposed). The Veizla as candidate True Name. | 25 min |

**Total: ~2.5 hours.** You leave knowing what SAP is, what the codex's central diagnosis is, what Ember refuses, and what Ember proposes. You do *not* leave knowing the code patterns to lift, the security threats, or the migration plan — those are Paths 3, 5, and 6.

---

## Path 2 — Affect-Axis Deep Dive (8 docs, ~3 hours)

*For: a contributor preparing the affect-engine slice, a reviewer evaluating Hjarta's expanded scope, anyone debating "should companion agents have an affection score?"*

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[1A_AFFECTION_DOMAIN]] | The Architect's core finding: 64 lines of regex around LLM-emitted tags. Read first. Everything else is reaction. | 25 min |
| 2 | [[3B_AFFECTION_LOOP]] | The Forge confirms 1A from the execution side: the "state" is a system-prompt block at `server.py:2611–2670`. No state machine. | 25 min |
| 3 | [[56_PRIVACY_BOUNDARIES]] | Auditor's lens: `affection_data.json` keyed by plain username is a silent collision (Telegram/Slack); no retention TTL; cross-platform identity bleed. | 25 min |
| 4 | [[61_NEW_VOWS]] | Cartographer's five Vows. **Affective Restraint** ratification-priority #2; **Embodied Honesty** #5. The conflict-check pattern. | 30 min |
| 5 | [[64_AFFECTION_ENGINE_REIMAGINED]] | Cartographer's redesign: dimensional-vector model, Identity Envelope, 30-minute decay constant, affect-as-event-log, LLM never writes affect values. | 30 min |
| 6 | [[65_META_AWARENESS]] | The Hugarsýn surface that makes affect introspectable without gamifying it. Shape-not-content prompt observability. | 30 min |
| 7 | [[66_INVENTED_METHODS]] (read items #5, #8, #10) | Telemetric Affect Surface (#5), **Tethered Affect Anchoring (#8 — the single most consequential invention)**, Affect-Aware Interrupt Cooldown (#10). | 20 min |
| 8 | [[68_DECISION_RECORDS]] (read SAP-002 + SAP-007) | The two ADRs that operationalize the affect-engine adoption decision. SAP-002 (affect engine, high effort, slice 5+); SAP-007 (behavior engine, slice 5+). | 25 min |

**Total: ~3.5 hours.** You leave knowing: SAP's affect is theatre, not state; Ember's reimagining is event-sourced, bounded, decayed, audited; the proposed Vows that gate the redesign; the ADRs that mature it into a slice candidate.

---

## Path 3 — Reach-Axis Deep Dive (10 docs, ~4 hours)

*For: a contributor preparing any IM-bot or livestream slice, a reviewer evaluating the Reach Pyramid, anyone debating how Ember should ship one-versus-many platforms.*

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[14_MESSAGING_DOMAIN]] | The Architect's framing: eight snowflakes, zero abstractions. ~3,800 LOC of near-identical boilerplate. **Boðr** proposed as ReachAdapter ABC. **Reach Pyramid** (Intimate/Local/Public/Broadcast). | 25 min |
| 2 | [[26_IM_BOT_INTERFACE]] | The Auditor's surface analysis: shared abstraction is real but centered on `global_behavior_engine`, not a base class. | 25 min |
| 3 | [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] | The Forge-A overview: 32 IM-bot routes in `server.py:10502–10847` are nearly-identical copy-paste. | 25 min |
| 4 | [[35h_IM_SLACK_BOT]] | The best-in-class deployment in SAP. `chat_update` edits the bubble in place during streaming. Adopt the pattern for Ember's Slack adapter. | 15 min |
| 5 | [[35b_IM_WECHAT_BOT]] | The worst-in-class deployment. Tencent ToS violation; stdout-monkey-patched QR scrape; third-party SDK. **Do not adopt.** | 15 min |
| 6 | [[36b_LIVESTREAM_YOUTUBE]] | The quota-burn case study: 70 minutes/day at default 5s poll (86,400 units against 10,000 default quota). | 15 min |
| 7 | [[36c_LIVESTREAM_TWITCH]] | The real-bug case study: `_send` and `_close_socket` indented inside `_handle_line` (`twitch_service.py:171–181`). Likely AttributeError on first call, swallowed by broad except. **The bot may be non-functional as shipped.** | 20 min |
| 8 | [[27_STREAMING_INTERFACE]] | The Auditor's livestream surface: all three platforms feed `live_router.manager.broadcast()`; two module-level globals hold it together. | 25 min |
| 9 | [[56_PRIVACY_BOUNDARIES]] | Cross-platform identity bleed; livestream → memory privacy; `reasoning_visible: true` Slack/Discord defaults. | 25 min |
| 10 | [[6A_MULTI_AGENT_PARTY]] | Where reach becomes federated: per-utterance channel arbitration; token-of-speaking voice arbitration; quiet-hours-per-platform. | 30 min |

**Total: ~4 hours.** You leave knowing: SAP's eight-snowflake reach stack, what to lift (Slack's `chat_update`, Telegram's no-SDK pattern), what to refuse (WeChat-personal entirely), the bug to not inherit (Twitch's indentation), and the Reach Pyramid as the abstraction Ember invents.

---

## Path 4 — Embodiment-Axis Deep Dive (9 docs, ~3.5 hours)

*For: a contributor preparing the avatar/voice slice, a reviewer evaluating the Andlit/Rödd reservations, anyone debating whether Ember "needs" a face.*

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[11_AVATAR_DOMAIN]] | The Architect's framing: VRM, Live2D, VTube Studio, VMC bidirectional. `vts_manager.py` (235 LOC, FFT vowel-band lip-sync) is the cleanest module in SAP. | 25 min |
| 2 | [[25_AVATAR_PROTOCOL]] | The Architect's surface analysis: VMC OSC bound to `0.0.0.0` (`main.js:71–77`) — body pose leaks across network; bidirectional, so hostile sources can drive the avatar. | 25 min |
| 3 | [[32_AVATAR_RENDER_PIPELINE]] | The Forge-A execution: transparent-Electron-window-into-OBS. The pipeline is sound; reuse for any T0 Andlit surface. | 30 min |
| 4 | [[16_VOICE_DOMAIN]] | The Architect's voice framing: `moss_tts.py` + `sherpa_asr.py`. Lazy-load pattern (`moss_tts.py:17`) is right. | 20 min |
| 5 | [[2A_VOICE_INTERFACE]] | Half-built duplex: barge-in detection exists, echo cancellation does not. | 20 min |
| 6 | [[63_PERFORMANCE_TIER_ENGINE]] | The Cartographer's tier ladder (T-1 through T3). Andlit + Rödd reserved as paired names; ship code only on tier-engine ratification. | 30 min |
| 7 | [[6B_LOW_POWER_EMBODIMENT]] | The Scribe's tier expansion: glyphic embodiment at T3; haptic affect at T2; status pulse file at T4. **The toaster as first-class tier.** | 30 min |
| 8 | [[60_TRUE_NAME_REASSIGNMENT]] | The Cartographer's True Name decisions: Andlit + Rödd reserved (paired); the Name Reservation pattern invented. | 30 min |
| 9 | [[66_INVENTED_METHODS]] (items #2, #6, #9, #11, #17) | Glyphic Embodiment (#2), Consent-Token Avatar Gating (#6), Per-Tier Voice Substitution (#9), Avatar-as-Backpressure Indicator (#11), Composition-First Avatar Vocabulary (#17). | 20 min |

**Total: ~3.5 hours.** You leave knowing: SAP's avatar stack (VRM + Live2D + VMC + VTS), the genuinely clever lip-sync, the VMC security hole, the tier ladder that gates embodiment, the paired-name reservation pattern, and the catalog of small inventions that round out the avatar surface.

---

## Path 5 — Security-and-Threat Audit (9 docs, ~4 hours)

*For: a security-minded contributor, a PR reviewer who suspects scope creep, anyone preparing the Vow ratification ceremony.*

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[03_ANTI_SAP]] | The Skald's thirteen-refusal table. Set the moral compass first. Refusal-Citation Discipline established. | 30 min |
| 2 | [[53_SECURITY_REVIEW]] | The Auditor's STRIDE pass. **Longest Avoid list in the codex.** `"yolo"` permission mode; pickle deserialization; localhost API with no auth; etc. | 35 min |
| 3 | [[56_PRIVACY_BOUNDARIES]] | Eight jurisdictions, three livestream platforms, one memory store. Cross-platform identity bleed; no consent capture; livestream → memory. | 30 min |
| 4 | [[57_FAILURE_TAXONOMY]] | 50 failure modes catalogued and ranked. Risk-Register-as-Code invented here. | 30 min |
| 5 | [[55_API_SIMULATION_TRAPS]] | The OpenAI-compat leakage catalog. Token-count drift; cache tokens lost; `dify_openai.py` destroys conversation history. | 25 min |
| 6 | [[29_TOOL_TYPE_INTERFACE]] | Four tool families, four trust models, zero shared validation. `custom_http` accepts arbitrary URLs. `comfyui_tool.py` does path-concatenation with LLM strings. **TrustClass enum** proposed. | 30 min |
| 7 | [[59_CONFIG_DRIFT]] | `update_workspace_settings` can change SAP's own permission mode to `yolo` — **the agent can disarm its own seatbelt.** | 25 min |
| 8 | [[58_OBSERVABILITY_GAPS]] | No structured logging, no metrics, no health endpoints. Stdout-as-log is the only telemetry. What Ember must surface. | 25 min |
| 9 | [[61_NEW_VOWS]] | The five Cartographer Vows in ratification-priority order. **Surface Without Surveillance** is #1 for a reason. | 30 min |

**Total: ~4 hours.** You leave knowing: SAP's complete threat surface (computer control + 8 IM bots + 3 livestreams + smart home + plain-text credentials + pickle deserialization + VMC on 0.0.0.0), the Refusal-Citation Discipline as the codex-wide protocol, the TrustClass enum as Ember's mitigation, and the five-Vow ratification order that gates the security redesign.

---

## Path 6 — Synthesis-Only Quick Read (13 docs, ~5 hours)

*For: a planner, a decision-maker preparing a slice ratification, anyone who wants the* answer *the codex proposes before reading the* analysis *that grounded it.*

Read in this dependency order. Each builds on the previous.

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[60_TRUE_NAME_REASSIGNMENT]] | The vocabulary settles first. Names gate code. | 30 min |
| 2 | [[61_NEW_VOWS]] | The Vows that govern the new names. Five Cartographer + two Skald = seven proposed. | 30 min |
| 3 | [[62_PARTY_PROTOCOL]] | Federation as Cartographer's central protocol. Role-bidding leader election. Ed25519 persona keys. | 30 min |
| 4 | [[63_PERFORMANCE_TIER_ENGINE]] | The tier ladder that makes federation + embodiment tractable. T-1 through T3. Pi-baseline test as standing review gate. | 25 min |
| 5 | [[64_AFFECTION_ENGINE_REIMAGINED]] | The redesign of the load-bearing finding. Event-sourced; dimensional-vector; decay-bounded; LLM never authors values. | 25 min |
| 6 | [[65_META_AWARENESS]] | Hugarsýn — the introspectable surface. Vow-as-typed-surface (the largest single novel contribution per the Cartographer). | 25 min |
| 7 | [[66_INVENTED_METHODS]] | The 20 minor/adjacent inventions catalogued. Tethered Affect Anchoring (#8) is the keystone. | 35 min |
| 8 | [[6A_MULTI_AGENT_PARTY]] | Many Embers across many devices. Per-utterance arbitration; operator is the only centralized authority. | 30 min |
| 9 | [[6B_LOW_POWER_EMBODIMENT]] | The toaster as first-class tier. Glyphic; haptic; status pulse file. | 25 min |
| 10 | [[67_SLICE_PLAN_REVISIONS]] | The proposed Slice 3 expansions. 8–10 weeks; 2,050 LOC; sub-slicing into 3a/3b acceptable. | 30 min |
| 11 | [[68_DECISION_RECORDS]] | The 12 ADR-Proposed records. SAP-001 through SAP-012, clustered by target slice. | 35 min |
| 12 | [[6C_EMBER_WAVE_3_SLICE]] | The concrete Wave 3 slice proposal. *Skilled, Bridged, Quiet, Tiered, Identified.* | 30 min |
| 13 | [[69_INTEGRATION_ROADMAP]] | The braided-slice approach across SAP × Hermes × Peer × Yggdrasil × Stofa. Five-year trajectory as asymptote, not forecast. | 35 min |

**Total: ~5.5 hours.** You leave with: the complete synthesis-layer narrative, the ratification-priority order for Vows, the slice-by-slice integration roadmap, the 12 ADRs ready for keeper decision, and the long-trajectory framing.

---

## Path 7 — For Volmarr at 2am with ADHD (4 docs, ~90 minutes)

*If you only read four documents, read these. In this order. Stop when your eyes glaze.*

| # | Slug | The single thing this doc teaches | Time |
|---|---|---|---|
| 1 | [[1A_AFFECTION_DOMAIN]] | SAP's "affection state machine" is 64 lines of regex. There is no state. The LLM is both author and judge. This is **the** finding. | 25 min |
| 2 | [[03_ANTI_SAP]] | The thirteen refusals. Every refusal cites a SAP line. Refusal-Citation Discipline is now a Codex protocol. | 30 min |
| 3 | [[64_AFFECTION_ENGINE_REIMAGINED]] | What Hjarta becomes instead. Event-sourced. Bounded. Decayed. The LLM never writes affect values. | 25 min |
| 4 | [[6C_EMBER_WAVE_3_SLICE]] | The concrete Wave 3 slice proposal. *Skilled, Bridged, Quiet, Tiered, Identified.* Eight to ten weeks. | 30 min |

**Total: ~90 minutes.** You leave knowing the headline finding, the codex's stance toward SAP, the redesign Ember proposes, and the concrete slice that lands first. Save the rest for when the mug is fresh.

---

## How to Choose a Path

| If your most pressing question is… | Walk Path |
|---|---|
| *What is the SAP Codex, and is it worth my time?* | 1 (First-Time Orientation) |
| *Should companion agents have an affection score?* | 2 (Affect-Axis) |
| *Should Ember ship eight IM bots — or one ReachAdapter and seven adapters?* | 3 (Reach-Axis) |
| *Does Ember need a face?* | 4 (Embodiment-Axis) |
| *Where does SAP's surface scare me, and what does Ember refuse?* | 5 (Security-and-Threat) |
| *What slice are we shipping next?* | 6 (Synthesis-Only) |
| *I have 90 minutes and need to be smart about this by morning.* | 7 (Volmarr-at-2am) |

When in doubt, walk Path 1. The Skald's framing is short, and it makes every later path land better. When the doubt persists, walk Path 7. The Scribe wrote it for the reader the Codex actually has.

---

## A Note on Skim Mode

The Codex can be skimmed. Each content doc has:

- A frontmatter block (read for `role`, `layer`, `sap_source_refs`).
- A first paragraph that compresses the doc's claim.
- A `## What This Means for Ember` closing section with the **Adopt / Adapt / Avoid / Invent** lists.

A skim-mode reading is: frontmatter, first paragraph, closing section. About 5 minutes per doc. Useful for triage; insufficient for any decision that materially changes Ember. Skim to *find* the docs that deserve a full read.

The closer (**Adopt / Adapt / Avoid / Invent**) is load-bearing. If you read nothing else of a content doc, read its closer. That is where the codex's stance toward each SAP pattern lives.

---

## What This Means for Ember

Reading orders are not just convenience. They are how the Codex protects the **Vow of Public-Friendliness** at meta level: a corpus that cannot be entered by a non-expert is a corpus that has failed, regardless of its contents. By describing seven concrete paths — one for each kind of reader the Codex serves — this file ensures no contributor is left wandering through 205,000 words looking for the room they came for.

The paths also protect the **Vow of Honest Memory** at the project level. A new contributor walking Path 1 in a year's time arrives at the same understanding as a contributor walking it today, because the paths are recorded and maintained. The institutional memory of "this is how we read our own Codex" is itself a kind of memory the Vows require Ember to keep honest.

Path 7 is, additionally, the practice of **Public-Friendliness at the operator scale**: the Codex's primary keeper is the operator who wrote it. The fourth path serves him directly. *That* is what a Codex for one — that scales to many — looks like.

**True Names affected:** none directly. **Vows protected:** Public-Friendliness, Honest Memory, Open Knowledge (through the explicit reading-by-goal taxonomy).

— *Eirwyn Rúnblóm, the Scribe*
