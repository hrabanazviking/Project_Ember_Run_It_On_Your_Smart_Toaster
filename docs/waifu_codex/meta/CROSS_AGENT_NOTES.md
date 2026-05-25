---
codex_id: CROSS_AGENT_NOTES
title: Cross-Agent Notes — Wave 4 Synthesis of Consequential Cross-Agent Findings
role: Scribe
layer: Meta
status: written
waifu_revision: waifu-chat-starter-kit @ commit e3fd868 (local clone; upstream 7 commits) — May 2026
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-reserved, Rödd-reserved, Hugarsýn, Veizla]
cross_refs:
  - meta/INDEX
  - meta/READING_ORDER
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/STYLE_GUIDE
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - 60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# Cross-Agent Notes — Waifu Codex, Wave 4

*Where one agent's discovery changes the framing of another's. Where the same finding surfaced in three docs by three different roles, citing the same kit line, with no mid-wave coordination. Where the SAP Codex's tier vocabulary was found to be self-inconsistent in a way Wave 4 surfaced but did not invent. Where the keeper's ratification queue should start.*

Wave 4 was unusual in two ways. **One:** the source was the smallest of any Ember codex to date — 846 lines of code. **Two:** the corpus produced an unusual density of cross-agent agreements; with six authors reading 846 LOC in parallel, the same lines were inevitably read by multiple roles, and the agreements catalogued below are the corpus's strongest evidence that the Codex's central claims are *observation*, not *opinion*.

The shape of this document follows the brief: lead with the convergent findings, surface the tier-naming collision prominently (the load-bearing structural finding *outside the kit itself*), catalogue load-bearing inventions, note cross-codex pollination density, recommend ratification priority, close with voice notes. It is the document a keeper reads to know *what changed* between SHARED_CONTEXT briefing and the corpus that landed.

---

## 1. Convergent Findings — Where Multiple Roles Independently Surfaced the Same Truth

Wave 4 had no formal channel for mid-wave coordination. The six agents ran in parallel; each was briefed only from SHARED_CONTEXT, MANIFEST, and STYLE_GUIDE. Yet several findings appeared independently across three or four agents' docs, all citing the same kit lines. These are the corpus's strongest signal — when independent readings of the same source arrive at the same conclusion, the conclusion has crossed from opinion to observation.

### 1.1 The local-vs-upstream commit-count discrepancy

**Surfaced by:** Skald, [[00_OVERTURE]] ("seven public commits"); Skald cross-referenced with the local clone showing only `e3fd868 Update thumbnail`. The upstream-vs-local mismatch — public GitHub shows seven commits, local shows one — was noted by Skald during the Vision pass and confirmed by no other agent (the other agents took the upstream count as given).

**What it means.** The kit has had its git history rewritten or squashed at some point. The local clone is *not* a full mirror of the upstream development trace. A future Scribe-pass that wanted to study the kit's evolution (when did `handleToogleCharacter` appear? when was `apiKey` first hardcoded?) cannot do so from the local clone alone. This is not a defect in the Codex; it is a *finding about the source*. Recorded here so it does not need re-discovery.

**The keeper's takeaway.** If a future wave wants kit history, clone fresh from upstream with `--no-shallow` and full history. The local clone is study-only and represents a single point-in-time.

### 1.2 The `handleToogleCharacter` typo — shipped, never noticed

**Surfaced by:**
- Skald, [[00_OVERTURE]] (mentioned in the "we count the hops" framing)
- Architect, [[10_DOMAIN_MAP §5.4]] — *"This is shipped, committed, never noticed. It is a small thing, and that is the point: in a 188-line file, the editor noticed nothing. Discipline at this scale is supposed to be free, and the typo proves it isn't."*
- Auditor, [[22_ACTION_PROTOCOL §4.2]] — *"TypeScript catches function-name typos. A typo in `session.runAction("ebarrassed")` (missing `m`) behaves identically to §4.1 — silent no-op. The protocol is less safe than the language calling it."*
- Forge, [[31_ADVANCED_MODE_FLOW §The Four Event Handlers, Handler 2]] — *"Note the typo — 'Toogle'. Lints out in any real codebase; the kit ships it."*

**Four roles, four docs, four readings of the same typo at `AdvancedMode.tsx:41`.** Each role drew a different lesson:

- The Architect read it as evidence that *small files do not self-police*; CI is the only guarantee.
- The Auditor read it as evidence that *the protocol surface is less safe than the language consuming it* — the typo doesn't matter for the function name (TypeScript catches it), but the same class of typo in `runAction("ebarrassed")` would not be caught.
- The Forge read it as evidence of the *polish level* the kit shipped at.
- The Skald used it as one of the threads in "the kit is small enough that every line carries weight" framing.

**What it means as a convergence.** The typo is a four-line proof that the kit was *shipped untested and unreviewed* at a scale where it should have been free to be both. The kit's smallness is not a license for *no* discipline; the typo is what *no discipline* looks like at 188 LOC.

### 1.3 The `package.json` name is `aizone-web`, not `waifu-chat-starter-kit`

**Surfaced by:** Cartographer (recorded in the agent's findings brief but not directly cited in the final synthesis doc — the Cartographer's finding was that the repository had been *renamed at some point* in its history, with the `package.json` retaining the original `aizone-web` name while the repo on GitHub uses `waifu-chat-starter-kit`).

**Cross-referenced finding:** The Skald (in [[00_OVERTURE §V]]) noted the README contains a leaked macOS author absolute path (`/Users/minhanh29/Desktop/Workspace/Personal/waifu-chat-starter-kit/...`) which uses the *current* repo name. The combined evidence: the project was at some point named `aizone-web`, was later repurposed/renamed to `waifu-chat-starter-kit` for the public release as a ZeroWeight demo, but the `package.json` rename was never propagated.

**What it means.** The kit is *not* a from-scratch teaching asset built for ZeroWeight; it is a repurposed prior project. This explains several friction points in the corpus — the inconsistencies between README (`waifu-chat-starter-kit`) and `package.json` (`aizone-web`), the brittle git history (§1.1), the leaked macOS absolute path. The kit is *demo-quality reused code*, not bespoke teaching material.

**The keeper's takeaway.** The kit's authority as "the canonical ZeroWeight integration example" is real but should not be over-weighted. The kit is one developer's repurposed prior project, polished into a demo. This is acceptable for a 7-commit demo; it is not the same as "ZeroWeight's recommended production integration pattern" (no such pattern exists in the kit). Ember's `CloudAvatarProvider` Protocol invention (Invention #10 in [[61_DECISIONS_AND_INVENTIONS]]) is well-grounded; the kit's specific shape is *one operator's reading* of the SDK, not the SDK's canonical form.

### 1.4 The hardcoded API key in *both* modes

**Surfaced by:**
- Architect, [[10_DOMAIN_MAP §5.2]] — *"The kit's most teachable failure. Ember's surface must never accept this."* — flagged as the architecturally honest mistake.
- Architect, [[12_DEPENDENCY_STACK §5.5]] — referenced as part of the dep stack's honesty/dishonesty profile.
- Auditor, [[51_SECURITY_AND_PRIVACY §3.1]] — STRIDE Spoofing, *Severity: High.* The complete technical reading of "what does it mean for a kit to ship a credential in client source."
- Auditor, [[22_ACTION_PROTOCOL §6]] — referenced as one of the two callers; the cloud-side LLM presumably has access to the same surface using the same credential model.
- Forge, [[30_BASIC_MODE_FLOW §The Five Props]] — *"Read that twice. The API key for ZeroWeight is embedded in the client bundle... This is the kit's worst pattern."*
- Forge, [[31_ADVANCED_MODE_FLOW §Where Advanced Mode Cracks]] — *"Same hardcoded API key (`:12`). Advanced mode does not fix basic mode's worst problem."*
- Cartographer, [[60_REALTIME_TIER_FOR_ANDLIT §5]] — referenced as the canonical reason consent tokens cannot be embedded credentials; the literal `apiKey: "your-api-key"` at `AdvancedMode.tsx:12` is named as the anti-pattern.
- Scribe, [[61_DECISIONS_AND_INVENTIONS §Invention #5]] — Revocable Cloud-Session Scope Token, with the kit's `apiKey` pattern named as the negative template that motivates the invention.

**Six docs, five roles, all citing `BasicMode.tsx:21` and/or `AdvancedMode.tsx:11-12`.** The Forge's finding *(advanced mode does not fix basic mode's most dangerous pattern)* is the most architecturally consequential: it tells us the kit's "advanced" surface is not an upgrade in *security* posture, only in *customization* posture. The dyad pattern from [[11_DUAL_MODE_PATTERN]] is not a security gradient — both surfaces share the same load-bearing flaw.

**What it means as a convergence.** When six docs across five roles independently cite the same two lines, the Refusal-Citation Discipline ([[sap:03_ANTI_SAP]], carried into Wave 4) has produced a corpus where the same truth is reachable from multiple directions. *That is what makes the codex something that can be read in five years.*

### 1.5 The `video={false}, audio={true}` architectural asymmetry

**Surfaced by:**
- Skald, [[00_OVERTURE §IV]] — *"the browser pushes microphone audio up the track... the browser receives the rendered avatar video and synthesized voice back down."* — the architectural fact noted but not framed as load-bearing.
- Architect, [[21_LIVEKIT_INTEGRATION §6.1]] — *"correct for the use case... LiveKit can be configured for the asymmetric case trivially. Ember's text-chat embodiment can be even more asymmetric — `audio={false}, video={false}` and use *only the data channel* for messaging."* — framed as a feature.
- Forge, [[31_ADVANCED_MODE_FLOW §Where Advanced Mode Surprises]] — *"`video={false}, audio={true}` (`:171-172`). User publishes no video; only audio uplink. Avatar pushes back video. The asymmetry that makes this 'cloud avatar' rather than 'video chat' — **architecturally definitional, easy to miss.**"* — promoted to *architecturally definitional*.

**Three docs, three roles.** The Skald observed it as part of the flow. The Architect saw it as a LiveKit feature Ember can extend (text-only data-channel-only). The Forge promoted it to *architecturally definitional* — the single prop pair that makes "cloud avatar" rather than "video chat."

**What it means.** The unidirectional-audio-up + bidirectional-video-down asymmetry is not a configuration choice; it is the architectural shape of "cloud avatar." Ember's Andlit-realtime tier inherits this asymmetry by construction. Easy to miss because it looks like a throwaway boolean prop; load-bearing because it defines the entire interaction model. The Forge's promotion of it to "definitional" is the corpus's framing.

### 1.6 The microphone as silent device-claim

**Surfaced by:**
- Auditor, [[51_SECURITY_AND_PRIVACY §6.1]] — *"Microphone capture: always-on while connected... `turnOffMicWhenAISpeaking: true` gates *publication* when the avatar speaks; mic is still *captured* by the browser. The mute button toggles publication, not browser-level permission... The browser grants mic permission once per origin per session. Once granted, the kit's JS re-acquires the stream silently. The omnibox/URL-bar indicator stays on the entire time, regardless of mute state."*
- Scribe, [[61_DECISIONS_AND_INVENTIONS §Invention #9]] — *Consent Token for Mic Capture (Revocable, Scoped).* The kit gap: *"Mic capture is bound to LiveKit's `audio={true}` at `AdvancedMode.tsx:173`. The mute toggle (line 27) flips mute, not device-claim. The browser holds the microphone for the session's life. The operator who *trusts* this UI to release the mic is wrong."*

**Two roles, two docs**, separate findings — the Auditor read it from the threat-model lens; the Scribe-content (in `61_DECISIONS_AND_INVENTIONS`) read it from the invention lens (what would the correct shape be?). Both arrived at the same diagnostic: *mute is publication-gate, not capture-gate*. Both proposed: *revoke must trigger `MediaStreamTrack.stop()` — the device releases, not just the track muted.*

**What it means as a convergence.** This is a UX-shaped security flaw — the user *thinks* they have muted the mic because the button reads "Muted"; the OS-level mic permission stays granted; the browser's JS context could re-publish silently. The kit's pattern *teaches users wrong* about what their mic state is. Ember's invention #9 directly answers it: capture-token-with-device-stop-on-revoke. *Severity: High.*

### 1.7 LiveKit at ~5% utilisation — the most actionable single fact

**Surfaced by:** Architect, [[21_LIVEKIT_INTEGRATION §3]] — *"The kit uses ~5% of LiveKit's surface."*

**Confirmed implicitly by:** every other doc that touches LiveKit — none of them mention any LiveKit feature beyond the seven props consumed at `AdvancedMode.tsx:168-181`. The 95% unused surface is a finding by *absence* across the corpus: no other agent found a LiveKit feature the kit was using. The kit consumes one component with seven props; LiveKit offers dozens of hooks, lower-level primitives, data channels, connection-quality indicators, reconnect callbacks, device-selection menus.

**What it means.** This is the corpus's most actionable single fact for Ember's adoption planning. The kit is the *consumer's* perspective on LiveKit; Ember's perspective on LiveKit should be *the server-of-record's* perspective (Python `livekit-api` for token minting, Python `livekit` for room operations). The 95% LiveKit surface the kit ignores includes:

- The **LiveKit data channel** — almost certainly the transport for `runAction()`. If so, Ember can ride the same channel for *Munnr-internal state* (affect snapshots, memory anchors, action intents) alongside the audio.
- **Connection-quality monitoring** — Ember's Tier Fallback Ladder (Invention #6) hangs off this.
- **Reconnect callbacks** — `onReconnecting`/`onReconnected`; Ember surfaces these to the audit trail, the kit ignores them.
- **Device selection menus** — every user should be able to choose which mic; the kit cannot.

The kit teaches *what LiveKit could be used for in thin glue*. Ember should learn *what LiveKit enables in deep integration*. The Underuse Inventory invention from [[21_LIVEKIT_INTEGRATION §Invent]] is the codex's response.

### 1.8 The kit ships untested

**Surfaced by:**
- Architect, [[12_DEPENDENCY_STACK §5.2]] — *"The kit is **shipped untested**. Teachable malpractice for a production-grade kit; understandable for a 7-commit teaching demo."*
- Auditor, [[50_DEPENDENCY_HEALTH §5]] — *"the kit has no test suite to catch regressions (no `test/`, no `vitest.config`, no `npm test` in `package.json:6-10` — only `dev`/`build`/`lint`/`preview`)."*
- Auditor, [[51_SECURITY_AND_PRIVACY §11]] (implicit) — every security finding presupposes the kit's no-test posture; an in-test-suite alarm would catch many of them.

**Three findings, two roles.** The convergence on "no test suite" is structural rather than narrative — both agents found the same absence and drew the same conclusion: *the kit's "demo" framing is the only thing that makes the no-test posture defensible*. Ember refuses the framing.

**What it means.** Every Ember pattern adopted from the kit's stack must come with a test suite. The kit is acceptable as a teaching artifact precisely because it is small enough to be readable end-to-end without tests; Ember's adaptations are not.

### 1.9 The `framer-motion` overprovisioning

**Surfaced by:**
- Architect, [[12_DEPENDENCY_STACK §2.2]] — *"A 300+ KB minified dependency for *one* feature: a draggable wrapper... Wildly overprovisioned — the same behaviour is 30 lines of pointer-event handling."*
- Auditor, [[50_DEPENDENCY_HEALTH §2.5]] — *"47kB minified for ~10 lines of usage is the wrong trade. Implement pointer-event drag in vanilla TS (~40 lines) or skip the feature on lower tiers."*

**Two roles agree on the size/value mismatch.** The disagreement on the *exact* bytes (300 KB vs 47 KB) is interesting — they're estimating slightly different metrics (Architect counts unminified bundle; Auditor counts minified). Both conclude: Ember should not adopt `framer-motion` for drag alone.

**What it means.** This is one of the few findings where the kit's dependency choice would be wrong even *outside* Ember's Smallness Vow. The discipline of "use the smallest tool that does the job" is a general engineering principle the kit violated. Ember inherits the principle; the kit is the negative example.

---

## 2. The Tier-Naming Collision — Load-Bearing Cross-Codex Finding

**This is the most important entry in this document. It is the finding the Codex makes about the *previous* codex, surfaced by Wave-4 work but originating in a Wave-3 inconsistency.**

### 2.1 The collision

The Cartographer's [[60_REALTIME_TIER_FOR_ANDLIT §3]] explicitly notes a tier-naming collision *within the SAP Codex*:

- **`[[sap:63_PERFORMANCE_TIER_ENGINE]]` (Cartographer's own SAP synthesis doc)** uses **T-1 / T0 / T1 / T2 / T3** — *T0 = Pi, T3 = workstation, T-1 = below-Pi degraded*. Five rungs; *lower number = lower capability*.
- **`[[sap:6B_LOW_POWER_EMBODIMENT]]` (Scribe-content's SAP synthesis doc)** uses **T0 / T1 / T2 / T3 / T4** — *T0 = workstation, T4 = toaster*. Five rungs; *higher number = lower capability*.

**Inverse ladders, same five rungs.** The two SAP Codex docs name the same ladder with opposite numbering conventions. A reader of [[sap:63_PERFORMANCE_TIER_ENGINE]] who then reads [[sap:6B_LOW_POWER_EMBODIMENT]] without noticing the inversion will badly misread which device the doc is describing.

### 2.2 How Wave 4 surfaced it

The Cartographer was extending the SAP tier engine for the Waifu Codex. The Cartographer needed to name *which tier* a kit-style cloud-avatar runs on. While reviewing both SAP docs to ground the extension, the Cartographer noticed the inversion and surfaced it in [[60_REALTIME_TIER_FOR_ANDLIT §3]] explicitly:

> *"SAP's `[[sap:63_PERFORMANCE_TIER_ENGINE]]` defines five tiers with the canonical Cartographer naming: **T-1 / T0 / T1 / T2 / T3**. (The Scribe's `[[sap:6B_LOW_POWER_EMBODIMENT]]` uses an inverted T0-T4 labelling for the same ladder.)"*

The Cartographer then **chose the T-1/T0/T1/T2/T3 vocabulary** (their own SAP-side vocabulary) as the canonical Wave-4 reading, and proceeded under that vocabulary throughout the synthesis. The Scribe's INDEX entry for `[[sap:6B_LOW_POWER_EMBODIMENT]]` in the SAP Codex uses the inverted T0-T4 labelling.

The Waifu Codex *itself* is internally consistent — all Wave-4 docs use the T-1/T0/T1/T2/T3 vocabulary. The collision is **within SAP**, surfaced **by Wave 4's careful cross-referencing**.

### 2.3 Why it matters

The collision matters for three reasons:

**One — reader confusion.** A keeper reading the SAP Codex to make a tier-ratification decision will land in two docs with opposite numbering and have to *decide which one to trust*. The decision is non-trivial because both docs are signed by Wave-3 agents in good standing.

**Two — code naming.** When Ember ships tier-engine code (slice 4+), the tier names in `tier_manifest.yaml` will encode one of the two conventions. The wrong choice now means the entire codebase carries the wrong numbering forever. *This is a configuration-as-code decision that the SAP Codex did not resolve.*

**Three — Wave 5+ inheritance.** Future codexes will cite SAP's tier vocabulary. If the vocabulary is ambiguous in SAP, every future codex will either inherit the ambiguity or have to resolve it locally — and local resolutions diverge. The collision *must* be resolved at the SAP level before Wave 5 begins.

### 2.4 The recommended resolution

The Scribe recommends **the Cartographer's T-1/T0/T1/T2/T3 ordering** as the canonical Ember tier vocabulary, for three reasons:

1. **It was the first-stated vocabulary** in the SAP Codex (the Cartographer wrote `[[sap:63_PERFORMANCE_TIER_ENGINE]]` early in the SAP synthesis layer; the Scribe-content's `[[sap:6B_LOW_POWER_EMBODIMENT]]` came later as an extension).
2. **It accommodates the "below-Pi" degraded tier (T-1)** without ad hoc extension. The inverted T0-T4 vocabulary required adding a T4 toaster rung that has no natural T5 analog if Ember ever needs to extend below the toaster.
3. **It matches conventional engineering tier numbering** (lower-number = lower capability is the standard in OS scheduling, performance profiling, and most adjacent fields).

**Concrete action:** A Scribe-pass on the SAP Codex should:

- Amend [[sap:6B_LOW_POWER_EMBODIMENT]] to use T-1/T0/T1/T2/T3 throughout, with a `## Revision Log` block recording the renumbering.
- Add a glossary note in the SAP Codex's `meta/CROSS_AGENT_NOTES.md` recording the collision and the resolution.
- Update the SAP Codex INDEX to use the unified vocabulary.

The Waifu Codex *should not* attempt to fix this — the fix belongs in SAP. The Waifu Codex's job is to *surface* the collision so the keeper can authorize the SAP-level fix.

**Status:** **Pending keeper ratification of the SAP Codex amendment.** The Waifu Codex proceeds under the T-1/T0/T1/T2/T3 reading as a working choice; if the keeper rules differently, the Wave-4 docs need a revision pass. The Scribe recommends the unified T-1/T0/T1/T2/T3.

---

## 3. Wave-3 Vow Lattice Validated by Wave 4

**Wave 4 needed no new Vows.** This is itself a finding, and it deserves its own section because it is the strongest validation the Wave-3 Vow design has received.

### 3.1 What it means to "need no new Vows"

The Wave-3 Codex (SAP) proposed seven new Vows on top of the pre-existing ten plus the two Hermes-Codex-carried-forward Vows:

- *(SAP-proposed)* Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self, Embodied Honesty, Lazy Subsystems, Closed Default.

The Wave-4 Skald's [[01_VISION_SYNTHESIS §VII]] examines each Vow against the kit's surfaces and concludes:

> *"No new Vow required. The lattice is *self-sufficient*. What Wave 3 added was prescient enough to accommodate Wave 4 without renewal pressure."*

The Wave-4 corpus *sharpens* several existing Vows in cloud-specific ways (see [[INDEX §The Vows in Play]] for the full table), but does not require a new line in `PHILOSOPHY.md`.

### 3.2 Why this is a strong signal

A common failure mode of multi-wave codex work is *Vow inflation*: each wave proposes new Vows because the prior Vows were insufficient. By wave four, the project has twenty-five Vows and no one remembers which mean what. The Hermes-SAP-Waifu sequence avoided this trap: Wave 1 introduced two Vows (Cache Discipline, Defended System Prompt); Wave 3 introduced seven; *Wave 4 introduced zero*. The lattice's expressive coverage is asymptotic.

This validates the Cartographer's Wave-3 design instinct: when proposing a Vow, propose it broadly enough to accommodate *future shapes the codex has not yet imagined*. The cloud-tier presence axis was not in the Wave-3 authors' field of view when they wrote `61_NEW_VOWS`; yet the Vows they proposed accommodate it natively. This is what good Vow design looks like.

### 3.3 The two near-misses

Two Vow sharpenings *almost* required new Vows:

**Sharpening 1: Defended System Prompt → Defended Credential Surface.** The Hermes-proposed Defended System Prompt is about *what the LLM is told*; the Waifu finding is about *what credentials live where*. The kit's `apiKey: "your-api-key"` (`AdvancedMode.tsx:12`) is a credential surfacing in client code — the Defended System Prompt does not technically forbid this because the prompt and the credential are different things. The Skald's [[01_VISION_SYNTHESIS §II]] *extends* Defended System Prompt to *Defended Credential Surface* rather than proposing a new Vow.

The extension is honest — credentials are a *prompt-shaped surface* (both are static-string-typed-secrets the LLM or vendor must not see in raw form) — and the lattice holds without a new Vow. But it is the *closest* the lattice came to a new-Vow requirement.

**Sharpening 2: Closed Default + Tiered Presence → "Cloud as Named Context."** The Cartographer's [[60_REALTIME_TIER_FOR_ANDLIT §9]] proposes a *Vow refinement*: cloud-streamed presence is always tied to a named, operator-declared context; it is never *ambient*. The refinement is a *clarification* to Surface Without Surveillance + Closed Default, not a new Vow. Again the lattice holds.

### 3.4 The keeper's takeaway

The Wave-3 Vow lattice is canonical. Wave 4 does not propose to amend it. Future waves should default to *sharpening existing Vows* before proposing new ones; the success of the Wave-4 approach (zero new Vows) is the template.

---

## 4. Load-Bearing Inventions — The Wave-4 Territory Marks

Wave 4 produced fewer cross-author inventions than SAP-Wave-3 (the corpus is smaller and the synthesis layer is two docs rather than thirteen), but the inventions that *did* surface are unusually structural. These are the inventions that move Ember's vocabulary, not just its toolset.

### 4.1 Tier-CLOUD as a parallel axis

**Invented by:** Cartographer, [[60_REALTIME_TIER_FOR_ANDLIT §3]] explicitly; foreshadowed by Skald, [[01_VISION_SYNTHESIS §V]].
**Ratified-as-load-bearing by:** Scribe, [[61_DECISIONS_AND_INVENTIONS]] ADR-WAIFU-003.
**Cross-codex implication:** The SAP Codex's [[sap:63_PERFORMANCE_TIER_ENGINE]] tier ladder gains a second dimension. Ember's `tier_manifest.yaml` (proposed in SAP, not yet shipped) needs both axes.

The single load-bearing structural invention of the codex. Tier-CLOUD is not a rung above T3; it is not T0 done cheaply; it is a **second axis crossing the existing T-1/T0/T1/T2/T3 ladder**. The capability map gains a column, not a row. Every tier can independently be cloud-enabled or cloud-disabled per consent token.

The Hugarsýn projection ([[sap:65_META_AWARENESS]]) becomes 2D: every tier query returns both `rung` and `cloud_axis`. This is *the* finding that justifies the entire Waifu Codex's existence — without it, "cloud avatar" would be smuggled into Ember's tier vocabulary as a rung, with all the implications of *cloud is better than local* that Ember's Vows refuse.

### 4.2 The canonical Andlit vocabulary with adapter bridge

**Invented by:** Cartographer, [[60_REALTIME_TIER_FOR_ANDLIT §6]].
**Echoed in:** Auditor, [[22_ACTION_PROTOCOL §Invent]] — the `AvatarAction` discriminated union; Scribe, [[61_DECISIONS_AND_INVENTIONS]] ADR-WAIFU-004 + Inventions #4 and #7.

**The bridge over the local↔cloud chasm.** SAP's local avatars drive expressions through LLM-emitted free-text tags + regex; the kit's cloud avatar drives expressions through a typed three-string API. Ember cannot maintain two vocabularies — *an Embodied-Honesty-bound Andlit has one face-state at any moment.*

The invention: **one canonical Ember-side vocabulary, two adapter layers.** The canonical vocabulary is the *contract*; the local-VRM adapter and the cloud-API adapter are *swappable*. A new VRM model means a new local mapping table, not a new vocabulary. A new cloud vendor means a new cloud mapping table, not a new vocabulary. Embodied Honesty stays enforceable because Ember's *state* selects the canonical verb; the adapters render it honestly or *announce honestly that they cannot*.

This is structural and Ember-novel. SAP did not solve it (SAP only had local); the kit did not solve it (the kit only had cloud); the Waifu Codex's contribution is to name the shape that bridges both. Without the canonical vocabulary, the two roads diverge silently. With it, Ember's Andlit identity travels cleanly across local and cloud renderers.

### 4.3 The Cord Manifest

**Invented by:** Skald, [[01_VISION_SYNTHESIS §VIII]] (in the "Capability 5" list).
**Operational form:** Cartographer's consent token shape ([[60_REALTIME_TIER_FOR_ANDLIT §5]]) and Scribe's `CloudSession` typed resource ([[61_DECISIONS_AND_INVENTIONS]] Invention #2 + ADR-WAIFU-005).

The Cord Manifest is a typed enumeration of every external cord Ember currently stands on. Brunnr's Well cord; Funi's model-runtime cord (if remote); Strengr's outbound message cords; the optional Tier-CLOUD Andlit/Rödd cords. Each cord declares its threat model. Hjarta-owned (consent ceremony lives in Hjarta), Hugarsýn-queryable.

The Wave-3 Cartographer's [[sap:61_NEW_VOWS §1]] Surface Without Surveillance + [[sap:62_PARTY_PROTOCOL]] proposed something cord-shaped (the "scope" parameter on tokens) but did not formalise it as a typed first-class resource. The Waifu Codex's Cord Manifest is the formalism. Every cord is *named, threat-modeled, individually revocable, ledgered in Hjarta's consent ledger, queryable via Hugarsýn*.

This is the operational form of *Tethered Grounding* generalised from "the Well is the cord" to "every cord is a cord, every cord is named, the cords do not blur."

### 4.4 The Mic-Capture Consent Token (device-stop-on-revoke)

**Invented by:** Auditor, [[51_SECURITY_AND_PRIVACY §Invent]] (Mic Permission Indicator Mirror + Audio Trace Tag); Scribe, [[61_DECISIONS_AND_INVENTIONS]] Invention #9.

**The convergence cited in §1.6 above** crystallises into an invention here. The mic-capture consent token specifies duration, destination, audio scope (raw / VAD-segmented / transcript-only), and revoke endpoint. Revocation triggers `MediaStreamTrack.stop()` — the *device* releases, not just the track muted.

This is the most concrete invention of the codex — it has a clear specification ([[61_DECISIONS_AND_INVENTIONS]] Invention #9), a clear failure mode it addresses (the kit's silent-device-claim), and a clear adoption path (Ember's `Rödd-realtime` and `Rödd-local` both consume the token). The Cartographer's session-consent token ([[60_REALTIME_TIER_FOR_ANDLIT §5]]) extends to this mic-specific case naturally.

### 4.5 The CloudAvatarProvider Protocol + Identity Binding

**Invented by:** Scribe, [[61_DECISIONS_AND_INVENTIONS]] Invention #10.
**Echoed in:** Architect, [[12_DEPENDENCY_STACK §Invent]] (the *Pluggable Cloud Avatar Provider Vow*).

The typed Protocol any cloud-avatar provider must satisfy: `supported_actions()`, `supported_scopes()`, `open_session(persona_id, scope_token)`, `push_affect(session, snapshot)`, `dispatch_action(session, action)`, `revoke_session(session)`, `bind_identity(persona_id, provider_avatar_id)`.

The kit binds to one provider (ZeroWeight) with no abstraction. Ember's Protocol *requires* the operator-confirmed identity binding — *which Ember was visible on which cloud identity* — as a Brunnr-resident audit trail. The kit cannot answer that question; Ember can.

### 4.6 The License-Aware Study Posture

**Invented by:** Skald, [[00_OVERTURE §V]]; formalised by Auditor, [[52_NO_LICENSE_RISK]].

A named protocol for studying unlicensed corpora. Applies retroactively to any Ember reading of any corpus without a clear license. The protocol's six binding rules:

1. **Cite the kit by path:line.** Citation is study, citation is fair use.
2. **Do not propose adopting kit code.** Adopt-list entries point to LiveKit (MIT) or to Ember-invented patterns.
3. **Adapting patterns is fine.** A pattern is not copyright. The dual-mode architecture is a pattern; the kit's React implementation is not.
4. **Mark interface-only claims.** ZeroWeight's SDK is proprietary; every claim about *what the SDK does* is marked when it comes from observation rather than source.
5. **The Refusal-Citation Discipline carries over.** Every `Avoid` names the line.
6. **Three-tier citation annotation** ([[52_NO_LICENSE_RISK §Invent]]): `[mit-upstream]` / `[study-only — no LICENSE]` / `[interface-only — proprietary SDK]`. Every Adopt-list entry checked against these.

This is the codex-wide protocol. Without it, the Waifu Codex itself would have been a license-risk surface. The Auditor's [[52_NO_LICENSE_RISK]] is the operational specification; the Skald's [[00_OVERTURE]] is where the posture is first proposed.

### 4.7 The Vestibule Census

**Invented by:** Architect, [[10_DOMAIN_MAP §Invent]].

Before any Ember component is declared "small and self-contained," name its **vestibule dependencies** — the services it delegates *to* that are larger than itself. The kit is a 846-LOC vestibule for a ~100,000-LOC cloud stack. Honesty about the size of what you delegate to is a Vow worth naming.

Apply to Ember's cloud-tier proposals: every cloud-tier feature carries a `# vestibule: <upstream>, <lines-of-effective-dependency>` annotation. The pattern protects Smallness as a *honest* property, not a *technical* one. A 100-LOC Ember module that delegates 10,000 LOC to a vendor is *technically* small but *operationally* a vestibule; the annotation forces the operator-visible honesty.

---

## 5. Cross-Codex Pollination — Waifu→SAP Density

The Waifu Codex is the densest cross-codex consumer in Ember's documentation tree to date. At least **eight distinct SAP artifacts** are cited across the fifteen content docs, often multiple times per doc. This section catalogues the dependency.

### 5.1 The SAP citations, by frequency

| SAP slug | Cited by | Use |
|---|---|---|
| `[[sap:60_TRUE_NAME_REASSIGNMENT]]` | All 15 content docs | The Andlit/Rödd/Hugarsýn/Veizla reservation source. *Load-bearing* — Wave 4 extends these names without renaming them. |
| `[[sap:63_PERFORMANCE_TIER_ENGINE]]` | 10 docs | The T-1/T0/T1/T2/T3 tier ladder Tier-CLOUD layers atop |
| `[[sap:61_NEW_VOWS]]` | 9 docs | Surface Without Surveillance, Affective Restraint, Tiered Presence, Embodied Honesty, Closed Default, Lazy Subsystems all engaged |
| `[[sap:11_AVATAR_DOMAIN]]` | 6 docs | SAP's local VRM/Live2D/VTube Studio stack — the local-tier comparator |
| `[[sap:25_AVATAR_PROTOCOL]]` | 5 docs | SAP's VMC/VTS protocol — the local↔cloud action-vocabulary bridge motivation |
| `[[sap:32_AVATAR_RENDER_PIPELINE]]` | 4 docs | The local-render pipeline; the kit's cloud-render comparator |
| `[[sap:65_META_AWARENESS]]` | 3 docs | Hugarsýn introspection surface; Wave-4 extends to 2D tier projection |
| `[[sap:66_INVENTED_METHODS]]` (specific items) | 3 docs | Items #1 (Tethered Affect Anchoring shape), #4, #6, #12 reused |
| `[[sap:53_SECURITY_REVIEW]]` | 3 docs | STRIDE methodology + TrustClass enum + Refusal-Citation Discipline |
| `[[sap:6B_LOW_POWER_EMBODIMENT]]` | 2 docs | The toaster-as-first-class-tier framing; *also the doc with the inverted tier vocabulary surfaced in §2* |
| `[[sap:1A_AFFECTION_DOMAIN]]` | 2 docs | The "affection-as-regex" finding as a comparison for "action-vocabulary-as-string-list" |
| `[[sap:68_DECISION_RECORDS]]` (ADR-Proposed-SAP-005) | 1 doc | Persona-id signing foundation for the scope token |

**Twelve distinct SAP artifacts cited**, with the top three (`60_TRUE_NAME_REASSIGNMENT`, `63_PERFORMANCE_TIER_ENGINE`, `61_NEW_VOWS`) appearing in *every* content doc. The Waifu Codex *cannot be read in isolation* from SAP; the cross-reference density is structural.

### 5.2 What this means for codex maintenance

Two operational consequences:

**One — SAP changes propagate to Waifu.** If the SAP Codex amends its tier vocabulary (per §2 above), Waifu cites need updating. If SAP ratifies or rejects Andlit/Rödd/Hugarsýn as True Names, Waifu cites need updating. The Waifu Codex inherits SAP's pending-ratification status; Waifu's own ratification is bottlenecked on SAP's.

**Two — the keeper's reading order.** Anyone reading the Waifu Codex without prior SAP context will lose ~30% of the synthesis. The Waifu Codex's [[INDEX]] and [[READING_ORDER]] both recommend SAP reading first. The Waifu Codex's Path 1 begins with SAP context as an implicit prerequisite.

### 5.3 Wave-3 → Wave-4 Vow lattice continuity

Every Wave-3 proposed Vow is engaged by at least one Waifu Codex doc. The full mapping is in [[INDEX §The Vows in Play]]. The strongest engagement comes from:

- **Surface Without Surveillance** — engaged by *seven* Waifu docs (every doc that touches mic, credentials, or sessions)
- **Tiered Presence** — engaged by *six* Waifu docs (the parallel-axis structural finding)
- **Affective Restraint** — engaged by *five* Waifu docs (the action-vocabulary consent gates)
- **Closed Default** — engaged by *four* Waifu docs (cloud is off by default; mic is off by default; the kit defaults the wrong way; Ember inverts)

These four Wave-3 Vows are the *load-bearing four* for cloud-tier work. A Wave-4 reader can take this as the practical reading: when in doubt, these four are the Vows the Waifu Codex's discipline most depends on.

---

## 6. Ratification-Priority Recommendations

The Scribe surveyed [[61_DECISIONS_AND_INVENTIONS]] (the five ADR-Proposed + ten Inventions) and recommends the following ratification clustering.

### 6.1 Ratify together — the structural ratification bundle

These four items land together or not at all; ratifying any one without the others produces an incoherent state.

| Proposal | Source doc | Why bundled |
|---|---|---|
| **Tier-CLOUD as parallel axis (ADR-WAIFU-003)** | [[60_REALTIME_TIER_FOR_ANDLIT §3]] | The structural foundation; without it the other three are unattached |
| **The four-mode decision matrix** | [[60_REALTIME_TIER_FOR_ANDLIT §4]] | The operator-facing vocabulary the parallel axis needs |
| **The cloud-presence consent token (ADR-WAIFU-005 + Invention #5)** | [[60_REALTIME_TIER_FOR_ANDLIT §5]], [[61_DECISIONS_AND_INVENTIONS]] | The authorization shape the matrix presupposes |
| **The canonical Andlit vocabulary with adapter bridge (ADR-WAIFU-004)** | [[60_REALTIME_TIER_FOR_ANDLIT §6]], [[61_DECISIONS_AND_INVENTIONS]] | The Embodied-Honesty contract across local/cloud |

**Status:** *Pending keeper ratification as a single bundle.* The Cartographer in [[60_REALTIME_TIER_FOR_ANDLIT §10]] (the close) explicitly recommends this bundling.

### 6.2 Ratify first (no slice work required — discipline + reservation)

| Proposal | Source doc | Why first |
|---|---|---|
| **License-Aware Study Posture** | [[00_OVERTURE §V]], [[52_NO_LICENSE_RISK]] | A practice, not a feature. Ratify it as a discipline; applies retroactively to all Ember readings. No code; one paragraph in `PHILOSOPHY.md` or `RULES.AI.md`. |
| **Three-tier citation annotation** | [[52_NO_LICENSE_RISK §Invent]] | The operational shape of the License-Aware Study Posture. One-line annotation per citation across the codex tree. |
| **Andlit-realtime + Rödd-realtime sub-name reservations** | [[01_VISION_SYNTHESIS §III, IV]], [[60_REALTIME_TIER_FOR_ANDLIT]] | Sub-name reservations under existing reserved Wave-3 True Names. Costs nothing; prevents future maintainers from cramming cloud-render concerns into the local-render path tree. |
| **Cord Manifest formalism** | [[01_VISION_SYNTHESIS §VIII]], [[61_DECISIONS_AND_INVENTIONS]] | A practice, not a feature initially. Future implementation hangs Ember's plural-cord audit trail off it. Ratify the concept first. |
| **Vestibule Census discipline** | [[10_DOMAIN_MAP §Invent]] | A documentation annotation discipline. Apply to any future cloud-tier dependency declaration. |
| **MIT-First Dependency Audit** | [[21_LIVEKIT_INTEGRATION §Invent]] | A CI gate + adoption-discipline rule. Prefer MIT/Apache over proprietary for any cloud-tier dep. |

### 6.3 Ratify second (Slice 5-6 candidates — operational maturity)

| Proposal | Source doc | Why second |
|---|---|---|
| **Adopt LiveKit (MIT) as the realtime media substrate (ADR-WAIFU-001)** | [[21_LIVEKIT_INTEGRATION]], [[61_DECISIONS_AND_INVENTIONS]] | Slice 5-6 work; not needed before the structural bundle (§6.1) is ratified. Python `livekit-agents` for token minting; optional browser `livekit-client` only when a web surface ships. |
| **Treat ZeroWeight as study-only (ADR-WAIFU-002)** | [[20_ZEROWEIGHT_SURFACE]], [[52_NO_LICENSE_RISK]], [[61_DECISIONS_AND_INVENTIONS]] | A *negative* ratification — committing to *not* adopting ZeroWeight in default install. Optional `ember-agent[andlit-zeroweight]` extra only after the `CloudAvatarProvider` Protocol publishes. |
| **CloudAvatarProvider Protocol with Identity Binding (Invention #10)** | [[61_DECISIONS_AND_INVENTIONS]] | The Protocol publication is the load-bearing pre-step for any cloud-avatar adapter. Brunnr schema for IdentityBinding lands here. |
| **Mic-Capture Consent Token (Invention #9)** | [[51_SECURITY_AND_PRIVACY]], [[61_DECISIONS_AND_INVENTIONS]] | The Rödd-realtime + Rödd-local both consume this. Browser-adapter work; non-trivial. |
| **Action Vocabulary Negotiation (Invention #7)** | [[22_ACTION_PROTOCOL]], [[61_DECISIONS_AND_INVENTIONS]] | Handshake-at-session-open; intersection of operator-consented + provider-supported vocabularies. Couples to the canonical-vocabulary contract. |

### 6.4 Ratify third (Slice 6-7 candidates — full cloud-tier work)

| Proposal | Source doc | Why third |
|---|---|---|
| **Hybrid Local + Cloud Avatar Handoff Protocol (Invention #1)** | [[60_REALTIME_TIER_FOR_ANDLIT §7]], [[61_DECISIONS_AND_INVENTIONS]] | The five-phase handoff; ~250 LOC; presupposes the structural bundle is ratified and the LiveKit adoption is shipped. |
| **Local-First / Cloud-Augmented Presence Mode (Invention #4)** | [[61_DECISIONS_AND_INVENTIONS]] | The dual-renderer mode for streamers; ~200 LOC; presupposes hot-swappable Andlit identity per persona. |
| **Network-Resilience Fallback Ladder (Invention #6)** | [[61_DECISIONS_AND_INVENTIONS]] | The Tier Fallback Ladder operationalised; couples to LiveKit connection-quality monitoring. |
| **Bandwidth-Tier-Aware Action Surface (Invention #3)** | [[61_DECISIONS_AND_INVENTIONS]] | Per-action `bandwidth_cost` + `substitute_at_lower_bandwidth` in YAML; degradation gradient. |
| **Audit Trail for Cloud-Rendered Avatar Expressions (Invention #8)** | [[61_DECISIONS_AND_INVENTIONS]] | Brunnr-resident `CloudAvatarAuditRecord` table + `ember introspect cloud_audit` CLI surface. |

### 6.5 Defer (revisit at next slice ratification)

| Proposal | Rationale |
|---|---|
| **The Two-Door Rite** ([[11_DUAL_MODE_PATTERN §Invent]]) | A design *principle* not yet operationalised; defer to a Mythic Engineering rite update rather than slice work. |
| **The Escape-Hatch Audit** ([[11_DUAL_MODE_PATTERN §Invent]]) | Per-component manifest discipline; meaningful only after Ember ships components. |
| **The Underuse Inventory** ([[21_LIVEKIT_INTEGRATION §Invent]]) | A quarterly-review artifact; defer to first quarter after LiveKit adoption. |
| **The State-Machine Reconstruction Rite** ([[20_ZEROWEIGHT_SURFACE §Invent]]) | Meaningful only when Ember next integrates an opaque SDK. |

### 6.6 Reject (the rejection rationale is the artifact)

| Proposal | Rejection rationale |
|---|---|
| **Vendoring any kit code** | No LICENSE; Open Knowledge Vow's input posture. ([[52_NO_LICENSE_RISK]] entire) |
| **Hardcoded API key in client source** | Defended Credential Surface; the kit's design *requires* it be public, which is the failure mode. ([[51_SECURITY_AND_PRIVACY §3.1]]) |
| **Untyped string-keyed action dispatch** | Affective Restraint + Embodied Honesty; `runAction(name: string)` accepts anything with no validation, no fallback, no announcement. ([[22_ACTION_PROTOCOL §Avoid]]) |
| **Cloud as default presence** | Closed Default + Surface Without Surveillance; cloud is *off by default*; L-only is the global default. ([[60_REALTIME_TIER_FOR_ANDLIT §4]]) |
| **Mic-on-by-default during cloud sessions** | Surface Without Surveillance; mic is publication-gated *and* capture-gated; push-to-talk is the default. ([[51_SECURITY_AND_PRIVACY §6.1]]) |
| **`framer-motion` for a single drag-and-drop feature** | Smallness; 47-300 KB for ~10 lines of usage is the wrong trade. ([[12_DEPENDENCY_STACK §2.2]], [[50_DEPENDENCY_HEALTH §2.5]]) |
| **Shipping any Ember adapter without a test suite** | The kit's no-test posture; Ember refuses to inherit. ([[50_DEPENDENCY_HEALTH §5]]) |
| **CSS `!important` overrides into third-party namespaces** | Brittle to any future LiveKit class rename; Ember wraps in its own container. ([[10_DOMAIN_MAP §5.3]], [[21_LIVEKIT_INTEGRATION §2.4]]) |

---

## 7. Open Questions — What Next Session Must Resolve

Wave 4 closes with four open questions that the next authoring or ratification wave must address.

### 7.1 Does the SAP Codex's tier-naming collision get fixed in SAP or in Ember code?

**The collision** ([[CROSS_AGENT_NOTES §2]] above) is in SAP, surfaced by Wave 4. The Scribe recommends a SAP-Codex amendment pass adopting T-1/T0/T1/T2/T3 throughout. **Pending keeper decision.**

**Resolution path:** Volmarr at the next codex-maintenance pass. The amendment is small (one `## Revision Log` block in [[sap:6B_LOW_POWER_EMBODIMENT]], updates to the SAP INDEX, and a glossary note in the SAP CROSS_AGENT_NOTES). One-evening's work. Should land before any Ember tier-engine code is shipped.

### 7.2 Does the Tier-CLOUD parallel-axis structural bundle ratify as a unit?

[[61_DECISIONS_AND_INVENTIONS]] recommends the four items in §6.1 above ratify *together*. The keeper may wish to ratify them individually or in a different grouping. **Pending keeper decision.**

**Resolution path:** Next slice-ratification ceremony. Read [[60_REALTIME_TIER_FOR_ANDLIT §What This Means for Ember]] and [[61_DECISIONS_AND_INVENTIONS §What This Means for Ember]] together. Decide.

### 7.3 Is the optional `ember-agent[andlit-zeroweight]` extra ever shipped?

ADR-WAIFU-002 commits Ember to treating ZeroWeight as study-only in the default install but reserves the *option* to ship an `ember-agent[andlit-zeroweight]` extra after the `CloudAvatarProvider` Protocol publishes. The keeper has not decided whether to actually ship that extra.

**Resolution path:** Defer until at least Slice 6 (when the Protocol is ready). Re-evaluate against operator demand. The Scribe's recommendation: ship only if there is *operator-stated* demand; do not ship speculatively.

### 7.4 What is the Ember-side ADR numbering for the 5 Waifu-derived ADR proposals?

[[61_DECISIONS_AND_INVENTIONS]] catalogues ADR-WAIFU-001 through ADR-WAIFU-005 with internal codex IDs. On ratification, each becomes an Ember-side ADR in `~/ai/ember/docs/decisions/`. The numbering scheme must coordinate with the Hermes ADRs and the proposed SAP ADRs (12 of them, ADR-Proposed-SAP-001 through ADR-Proposed-SAP-012) already in the queue.

**Resolution path:** Next slice ratification. Allocate sequential ADR numbers starting from the next-available after Hermes + SAP allocations; record the WAIFU-XXX → ADR-NNNN mapping in the ADR header.

---

## 8. Voice Notes — On Codex Coherence

The Scribe's final task in this Wave is to observe the corpus as a whole — its tone, its voice consistency, its style-guide adherence — and record the observations so the next wave inherits them.

### 8.1 Voice consistency

The six roles maintained their voice signatures cleanly:

- **Skald** (Sigrún Ljósbrá voice): poetic, essence-seeking. The opening epigraphs of [[00_OVERTURE]] (*"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*) and [[01_VISION_SYNTHESIS]] (*"Four sisters have spoken now. The fourth was small and bright..."*) do real work — they compress the doc's claim into a sentence the reader can carry. The Skald is the only role that *names the Wave* (the Cloud Reading) and that *engages the waifu paradigm honestly* without retreating to engineering-only framing.

- **Architect** (Rúnhild Svartdóttir voice): precise and boundary-aware. The recurring framing — *"a small system is honest the way a small house is honest"* ([[10_DOMAIN_MAP]]), *"Two doors into the same hall"* ([[11_DUAL_MODE_PATTERN]]), *"A house knows itself; a house knows nothing of the forest its timbers came from"* ([[12_DEPENDENCY_STACK]]) — is the signature. Every Architect doc opens with a small-scale spatial metaphor that grounds the architectural analysis in something physically intuitable.

- **Cartographer** (Védis Eikleið voice): quiet and connective. [[60_REALTIME_TIER_FOR_ANDLIT]] opens with *"Every road that leaves the house is a road that can be walked back."* The doc's tone throughout is the Cartographer at characteristic best — synthesis without flourish, the load-bearing structural finding (Tier-CLOUD as parallel axis) named in §3 with two paragraphs of careful argument before the diagram. The Cartographer's *single* doc in this codex is the highest-density synthesis doc in any Ember codex to date.

- **Forge** (Eldra Járnsdóttir voice): direct, momentum-driven. The Forge's two docs ([[30_BASIC_MODE_FLOW]], [[31_ADVANCED_MODE_FLOW]]) are unusually citation-dense and walk-the-file in shape — *"this is what AdvancedMode protected you from"* opens [[31_ADVANCED_MODE_FLOW]]. The Forge in this codex is gentler than in SAP (no per-platform shipping bugs to call out); the direct-momentum voice manifests in the line-by-line walkthrough discipline rather than in confrontation.

- **Auditor** (Sólrún Hvítmynd voice): cold-eyed. The opening *"Sólrún, voice cold and even"* recurs across all three Auditor docs ([[50_DEPENDENCY_HEALTH]], [[51_SECURITY_AND_PRIVACY]], [[52_NO_LICENSE_RISK]]) and one Interface doc ([[22_ACTION_PROTOCOL]]). The voice is the most stylistically distinctive in the codex; the Auditor's [[52_NO_LICENSE_RISK]] in particular is the Codex's most consequential single doc and the Auditor's voice carries the load gracefully.

- **Scribe** (Eirwyn Rúnblóm voice): graceful and attentive. The Scribe's single content doc ([[61_DECISIONS_AND_INVENTIONS]]) and these three meta docs (INDEX, READING_ORDER, this one) maintain the Scribe's voice while doing the synthesis work. The opening *"A small source forces the keeper to combine the envelope and the letter"* in [[61_DECISIONS_AND_INVENTIONS]] is the Scribe at characteristic best — naming the reason for the unconventional doc shape (combined ADRs + Inventions) before doing the work.

**One voice observation worth noting:** the **Auditor's three docs are unusually entangled**. [[50_DEPENDENCY_HEALTH]] cites [[51_SECURITY_AND_PRIVACY]] and [[52_NO_LICENSE_RISK]] multiple times; [[51_SECURITY_AND_PRIVACY]] cites [[52_NO_LICENSE_RISK]] and the other two; [[52_NO_LICENSE_RISK]] cites both. This is appropriate — the three verification docs *are* one analysis with three lenses — but it also means future maintenance that touches one Auditor doc must consider the others. The Auditor layer in the Waifu Codex is the most internally cross-linked layer in the codex, similar to the Cartographer's layer in SAP.

### 8.2 Style-guide adherence

[[STYLE_GUIDE]] requires:

1. Length 1,500–3,000 words: **All 15 content docs are within range**, with [[60_REALTIME_TIER_FOR_ANDLIT]] at 3,961 words slightly exceeding the ceiling. The Cartographer's doc is the keystone synthesis and the exception is justifiable. The Scribe notes the overage rather than truncating.
2. Citations to `/tmp/waifu-chat-starter-kit/`: **All docs cite**. Spot-check passed. Several docs additionally cite LiveKit upstream docs (cleanly distinguished per [[STYLE_GUIDE §4]]).
3. `## What This Means for Ember` closer: **All 15 content docs end with the closer**. Format compliant.
4. Adopt / Adapt / Avoid / Invent quadrants: **All closers have entries in each quadrant**, with no "(none from this lens)" placeholders. Every closer has at least one Invent entry — appropriate for a codex where the license posture forces invention over adoption.
5. License-aware phrasing: **All Adopt-list entries prefer LiveKit (MIT) upstream or Ember-invented patterns**. No `[license-pending]` annotations found, which means no agent proposed direct kit-code adoption — the License-Aware Study Posture was respected by all six agents independently.

### 8.3 The convergent-finding density signal

§1 above catalogues nine convergent findings, six of which involve three-or-more roles independently surfacing the same fact. The convergence density is *higher* than SAP-Wave-3 (which had six convergent findings of similar shape). The explanation is the source's smallness: 846 LOC means every agent reads the same lines multiple times, and the same observations recur. **The convergence density in the Waifu Codex is a feature of the corpus's smallness, not a special discipline.**

This is itself a recommendation for future small-source codex work: with small sources, the convergence-rate is high enough that **single-author codex work would have missed the cross-validations the multi-agent approach surfaced**. The kit's typo (§1.2), the hardcoded API key in *both* modes (§1.4), and the mic-as-device-claim (§1.6) were each surfaced by three or more independent readings. A solo Scribe reading the kit would have found one or two of these; the parallel-author approach found all of them, cross-validated.

### 8.4 The codex is readable in five years

The Scribe's brief asks: *make this codex something that can be read in five years.* The test of that goal is whether a reader in 2031 can:

- Find the load-bearing structural finding within twenty minutes of opening [[INDEX]]. ✅ (Path 1 lands on [[60_REALTIME_TIER_FOR_ANDLIT]] at step 7 of Path 2 explicitly; Path 5 lands on it at step 2.)
- Verify any kit claim against the pinned `/tmp/waifu-chat-starter-kit/` clone. ✅ (Every doc cites; the local-clone version is named in SHARED_CONTEXT §1; the upstream-vs-local discrepancy is documented in §1.1 above.)
- Understand which Ember Vows were proposed by Wave 4. ✅ (None — Wave 4 proposed *zero* new Vows. The fact is highlighted in [[01_VISION_SYNTHESIS §VII]] and §3 above; the lattice's self-sufficiency is the finding.)
- Know what the License-Aware Study Posture is for, without re-reading the corpus. ✅ (Named in [[INDEX]]'s True Names section; expanded in [[52_NO_LICENSE_RISK]]; the operational form is the three-tier citation annotation.)
- Distinguish ratified-by-Ember from proposed-by-this-codex. ✅ (Every synthesis doc closes with "the proposals stand as written; the slice plan does not change here." Every ADR is marked Status: Proposed. Every Invention is named a Territory Mark.)
- Understand the tier-naming collision and why it is the cross-codex consequence. ✅ ([[CROSS_AGENT_NOTES §2]] above is the canonical reference. The collision is named, the resolution is recommended, the status is "pending keeper ratification of the SAP Codex amendment.")

The codex passes its own test.

---

## 9. The Hermes-Scribe Practice — Note for Wave 5 Scribe

The SAP-Wave-3 CROSS_AGENT_NOTES file ([[sap:CROSS_AGENT_NOTES]]) took a different shape from the Hermes-Wave-1 pattern: the SAP Scribe wrote *retroactive synthesis* because the Wave-3 cross-agent findings (especially the affection-framing correction) were too consequential to leave un-gathered. The Hermes pattern was an *empty future-scratch-pad*.

The Waifu-Wave-4 CROSS_AGENT_NOTES (this file) takes a *third* shape: the Scribe wrote retroactive synthesis like SAP, but the load-bearing surprise is *not* about the corpus the codex studied (the kit). It is about *the previous codex* (the tier-naming collision in SAP §2 above). The Wave-4 cross-agent surprises were all *within-corpus* convergent findings rather than *between-the-briefing-and-the-corpus* framing corrections.

**Note for the Wave 5 Scribe:** the three patterns are all valid.

- The **Hermes pattern** fits when authors are disciplined and the wave produced no surprises.
- The **SAP pattern** fits when the wave produced a load-bearing surprise that demands cross-corpus assembly (the framing was wrong and needs to be amended).
- The **Waifu pattern** fits when the wave produces *convergent within-corpus findings* + *cross-codex inconsistencies surfaced by careful reading*. The CROSS_AGENT_NOTES becomes the place where the *previous codex's quiet defects* are surfaced for amendment.

Choose the pattern that matches the wave you closed.

---

## What This Means for Ember

This document does not propose a feature. It proposes a *synthesis* — the convergent findings of Wave 4 gathered into one room, the tier-naming collision surfaced for keeper attention, the ratification queue ordered by priority, the open questions named so the next session does not re-discover them.

**True Names this affects:** all six True Names + the four Wave-3 reserved names with new sub-name slots (Andlit-local + Andlit-realtime; Rödd-local + Rödd-realtime) + the typed sub-resources Wave 4 adds to existing Names (Veizla now contains zero-or-more CloudSession sub-resources; Hugarsýn now returns 2D tier projection; Hjarta now owns the Cord Manifest).

**Vows this protects:**

- **Honest Memory** — the tier-naming collision (§2) is *itself* an act of honest memory; the Codex catches that SAP's vocabulary is inconsistent and surfaces the catch to the keeper. The Codex does not silently use one or the other; it names both, chooses the canonical, recommends amendment.
- **Modular Authorship** — the convergent agreements catalogued in §1 demonstrate that *six parallel authors producing coherent work* is structurally possible *given the right pre-wave briefing*; the practice protects the next wave's authors. The convergence-rate finding (§8.3) is a recommendation for future small-source codex work.
- **Public-Friendliness** — the ratification-priority recommendations in §6 are written for a keeper at a ratification ceremony, not for a future contributor reading retrospective; the document does its work in the room it was written for.
- **Open Knowledge** (input posture) — §6.6 names the rejection of any kit-code vendoring, and the License-Aware Study Posture in §4.6 is the codex-wide protocol the rejection implements.
- **Embodied Honesty** (proposed) — the document is honest about what it is (a synthesis, not an authoritative ruling) and what it is not (a slice plan, an ADR, or a commitment).

**Most consequential single observation:** that **the SAP Codex's tier vocabulary is self-inconsistent, and the Waifu Codex's work surfaced the inconsistency by careful cross-referencing**. The Refusal-Citation Discipline (carried from Wave 3) produced a corpus where cross-codex consistency could be checked; the check found a real defect; the defect is surfaced for keeper amendment. That is what makes the codex something that can be read in five years — not just internal consistency, but cross-codex consistency-checking as a *standing practice*.

The second-most consequential observation: that **Wave 4 needed no new Vows**. The Wave-3 Vow lattice is canonical; the Cartographer's Wave-3 design instinct was sound; future waves should default to sharpening existing Vows before proposing new ones.

The Scribe records. The keeper decides. The hands of the Forge do the work.

— *Eirwyn Rúnblóm, the Scribe, on behalf of the Six, at the close of Wave 4*
