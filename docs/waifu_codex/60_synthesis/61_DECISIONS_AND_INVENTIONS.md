---
codex_id: 61_DECISIONS_AND_INVENTIONS
title: Decisions and Inventions — ADR-Proposed and Invented Methods from the Waifu Kit
role: Scribe
layer: Synthesis
status: draft
waifu_source_refs:
  - src/main.tsx (10 LOC)
  - src/App.tsx (50 LOC)
  - src/modes/BasicMode.tsx (31 LOC)
  - src/modes/AdvancedMode.tsx (188 LOC)
  - package.json
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-proposed, Rödd-proposed]
cross_refs:
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - 00_vision/00_OVERTURE
  - 00_vision/01_VISION_SYNTHESIS
  - 10_domain/11_DUAL_MODE_PATTERN
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/31_ADVANCED_MODE_FLOW
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - sap_codex/60_synthesis/66_INVENTED_METHODS
  - sap_codex/60_synthesis/68_DECISION_RECORDS
---

# 61 — Decisions and Inventions

> *A small source forces the keeper to combine the envelope and the letter. Five ADRs, ten inventions, sealed together — because the kit was modest, and the keepers can be modest with it.*
> — Eirwyn Rúnblóm

## 0. Posture — Combined, Proposed, Light-Footed

The Scribe's SAP-side synthesis split ADRs (`[[sap:68_DECISION_RECORDS]]`) from inventions (`[[sap:66_INVENTED_METHODS]]`) because that corpus was large. The waifu kit is 846 LOC across five files; splitting the envelopes here would be theatrical. One combined doc honors the source's modesty without losing the discipline.

Every record below is **Status: Proposed**. None are decisions yet. Cartographer's `[[60_REALTIME_TIER_FOR_ANDLIT]]` is the paired piece — the tier-engine work these ADRs and inventions assume. Read them together.

License footnote: every adoption proposal prefers **LiveKit (MIT)** as upstream. Kit code is study-only per `[[52_NO_LICENSE_RISK]]`; `[interface-only]` marks proprietary ZeroWeight surfaces; `[license-pending]` marks any kit-derived pattern adoption.

---

## Part I — Five ADR-Proposed Records

### ADR-WAIFU-001 — Adopt LiveKit (MIT) as Ember's Realtime Media Substrate

**Context.** The kit's realtime media plane is `@livekit/components-react` + `livekit-client` (MIT). `/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:168-182` shows a `LiveKitRoom` consuming a `serverUrl`, a `token`, and binary `connect/video/audio` flags, with `onConnected` / `onDisconnected` lifecycle hooks. LiveKit is a mature WebRTC SFU + client SDK with a stable Room/Track/Participant model. For Ember's proposed Andlit-realtime and Rödd-realtime sub-axes, the realtime substrate is the foundational question.

**Decision.** Adopt LiveKit when (and only when) cloud-tier presence is operator-requested:

1. LiveKit becomes the **Tier-CLOUD media plane** per `[[60_REALTIME_TIER_FOR_ANDLIT]]`.
2. Ember integrates as **LiveKit client**, never as SFU host. The SFU is operator-provided (self-hosted LiveKit Open Source, LiveKit Cloud, or any compatible peer).
3. Ember does not vendor the kit's React integration; the kit is study-only.
4. Python path uses `livekit-agents`; the optional browser surface uses `livekit-client` (both MIT).
5. SFU choice is **pluggable** via a `RealtimeMediaProvider` Protocol with `LiveKitProvider` as default.

**Consequences.** One MIT realtime substrate; operator-controlled SFU; Pi-class hosts are clients only; Tier-CLOUD becomes a slice-6+ effort — slices 3-4 do not need it.

**Alternatives Considered.** Native WebRTC (rejected — WebRTC's signalling/ICE/TURN cost a year to rebuild); kit's React integration (rejected — no license); proprietary realtime SDKs like Daily/Agora/Twilio (rejected — Open Knowledge); deferring cloud-tier indefinitely (rejected — Vow-honoring surface deserves commitment to *how*).

**Vow check.** Open Knowledge ✅, Pluggable Storage ✅, Smallness ✅ (Pi runs as client), Modular Authorship ✅.

**Instantiates inventions:** #1, #2, #5, #6.

**Kit references (study-only):** `AdvancedMode.tsx:168-182`, `package.json:13,14,18`. **Upstream (MIT, adoptable):** `github.com/livekit/agents`, `github.com/livekit/client-sdk-js`, `github.com/livekit/livekit`.

---

### ADR-WAIFU-002 — Treat ZeroWeight as Study-Only

**Context.** `@zeroweight/react` + `@zeroweight/renderer` are commercial closed-source SDKs (npm tarball fetch 403s per `[[20_ZEROWEIGHT_SURFACE]]`). The kit itself has no LICENSE (`[[52_NO_LICENSE_RISK]]`). The `apiKey: "your-api-key"` pattern at `BasicMode.tsx:21` and `AdvancedMode.tsx:12` confirms commercial gating.

**Decision.** Treat ZeroWeight as a study-only reference:

1. Ember ships no ZeroWeight integration in the default install.
2. An optional `ember-agent[andlit-zeroweight]` extra **may** ship as a thin adapter conforming to the `CloudAvatarProvider` Protocol (invention #10) — only if Ember publishes the Protocol first.
3. Ember does not vendor any ZeroWeight code. The adapter, if shipped, depends on the published npm package.
4. Ember documentation does not recommend ZeroWeight specifically; it documents the Protocol and points to ZeroWeight as one possible substrate among several.

**Consequences.** Ember stays substrate-neutral. Operators with existing ZeroWeight accounts can integrate via the extra. The proprietary surface stays at the edge.

**Alternatives Considered.** Build ZeroWeight into Ember default (rejected — vendor lock); refuse any ZeroWeight integration (rejected — operator-hostile); vendor the kit's ZeroWeight code (rejected — no license).

**Vow check.** Open Knowledge ✅, Modular Authorship ✅, Pluggable Storage ✅, Public-Friendliness ✅.

**Instantiates inventions:** #10.

**Kit references.** `BasicMode.tsx:3`, `AdvancedMode.tsx:6`, `package.json:15,16` [interface-only — proprietary SDK].

---

### ADR-WAIFU-003 — Introduce Tier-CLOUD as a Parallel Branch on the Tiered Presence Ladder

**Context.** SAP's `[[sap:63_PERFORMANCE_TIER_ENGINE]]` defines a five-tier capability ladder (T0/T1/T2/T3/T4), monotonic and host-anchored. The kit demonstrates a different axis: a *modest* host (laptop, even Pi) can render *rich* avatar embodiment by offloading rendering to a cloud SFU. This is not "T0 done cheaply" — it is a different shape. Calling it T-1 or T0.5 would smuggle a hierarchy that does not exist.

**Decision.** Introduce **Tier-CLOUD** as a parallel branch:

1. The tier ladder becomes a *graph*: `T4 → T3 → T2 → T1 → T0`, with **Tier-CLOUD** branching off T1, T2, T3 as parallel capability (not higher).
2. Tier-CLOUD presupposes operator-provided cloud credentials, network reachability, and a consent-token (invention #5).
3. Tier-CLOUD does not replace T0. A workstation operator chooses T0-local alone, Tier-CLOUD alone, or both (per invention #4).
4. Tier-CLOUD has its own degradation ladder (invention #6).
5. The tier engine gains a `cloud_capabilities` probe alongside the hardware probe.

**Consequences.** A Pi operator can deliberately choose Tier-CLOUD, trading local privacy for richer embodiment. A T0 operator can run local + cloud simultaneously. The taxonomy gains expressiveness without breaking SAP's monotonic ladder.

**Alternatives Considered.** Cloud as T-1 above T0 (rejected — implies better-than-local); as T0.5 (rejected — misleading); refuse to model cloud (rejected — operator wants it); cloud-by-default at T2/T3 (rejected — Surface Without Surveillance violation).

**Vow check.** Tiered Presence ✅, Smallness ✅, Surface Without Surveillance ✅, Modular Authorship ✅.

**Instantiates inventions:** #3, #4, #6.

**Kit references.** `BasicMode.tsx:19-25`, `AdvancedMode.tsx:80-93`.

---

### ADR-WAIFU-004 — Action Vocabulary Is a Typed, Consent-Gated Tool Surface

**Context.** The kit's action API is string-typed and undocumented: `session.runAction("embarrassed")`, `("dance")`, `("wave_hand")` (`AdvancedMode.tsx:45-49`), with `Math.random()` choosing between them — a teaching pattern, not production. The actions are unenumerated in any visible TypeScript surface. For Ember under **Affective Restraint** and **Surface Without Surveillance**, this is the wrong shape.

**Decision.** Treat avatar action vocabulary as a typed, consent-gated tool surface:

1. Every action is declared in `~/.ember/config/andlit_actions.yaml` with schema `{name, intensity_range, contexts_allowed, precondition, substitute_when_denied}`.
2. Action names live in an enumeration the model is *prompted with* and that Munnr validates against on dispatch.
3. Action dispatch goes through a consent gate identical to SAP's `[[sap:66_INVENTED_METHODS]]#6` — operator-declared context determines which tokens are honored; ungranted actions are substituted (with audit log), never silently emitted.
4. The vocabulary is **renderer-portable**: local-VRM, local-Live2D, and Tier-CLOUD all honor the same names; each provider maps to its rendering primitives.
5. Unknown actions are refused with a typed-exhaustion error, not silently dropped.

**Consequences.** The vocabulary becomes documentation; the model's prompt includes the enumeration; new renderers implement the vocabulary without prompt-layer churn; operators tune substitutions per context.

**Alternatives Considered.** String-typed actions with dispatch-time validation (rejected — loses prompt constraint); free-form actions parsed by renderer (rejected — couples model to renderer specifics); expression-only with no actions (rejected — legitimate surface).

**Vow check.** Affective Restraint ✅, Surface Without Surveillance ✅, Embodied Honesty ✅, Pluggable Storage ✅, Public-Friendliness ✅.

**Instantiates inventions:** #7, #8.

**Kit references.** `AdvancedMode.tsx:41-51`. **SAP cross-refs.** `[[sap:66_INVENTED_METHODS]]#6`, `[[sap:25_AVATAR_PROTOCOL]]`.

---

### ADR-WAIFU-005 — Cloud Sessions Are Typed Resources with TTL, Scope, and Auto-Revoke

**Context.** The kit's session model is shallow: `sessionDuration={120}` and `inactivityTimeout={30000}` props at `BasicMode.tsx:22-23`, plus a `timeRemaining` field and `disconnect` callback in advanced mode (`AdvancedMode.tsx:24-29`). Beyond these primitives, the session is opaque. For Ember, a cloud session costs the operator (money, bandwidth, privacy) and must be revocable at any moment. The kit's model is too thin.

**Decision.** Define `CloudSession` as a typed dataclass: `(session_id, provider, issued_at, expires_at, inactivity_window, scope_token, operator_persona_id, audit_chain_id, revoke_url)`:

1. Every session is **opened explicitly** by operator-confirmed call (`ember andlit connect` or wizard).
2. Every session **auto-revokes** when `expires_at` is reached, inactivity exceeds the window, operator triggers disconnect, host enters suspend/lid-close, or a peer-issued revoke event lands in the audit log.
3. Session state lives in **Brunnr**, not volatile memory. A crash recovers; `ember andlit list` surfaces residual sessions.
4. Shutdown follows a **drain pattern**: graceful disconnect → force-disconnect after timeout → hard-purge of local credentials.
5. Hugarsýn gains `ember introspect cloud_sessions`.

**Consequences.** Cloud sessions become inspectable. Lid-close cannot leak forgotten connections. The audit log is the basis for invention #8.

**Alternatives Considered.** In-memory only as LiveKit SDK does (rejected — crash recovery impossible); store credentials only without session shape (rejected — no introspection); centralize in provider dashboard (rejected — vendor coupling).

**Vow check.** Surface Without Surveillance ✅, Honest Memory ✅, Graceful Offline ✅, Tethered Grounding ✅, Modular Authorship ✅.

**Instantiates inventions:** #2, #5, #6, #8, #9.

**Kit references.** `BasicMode.tsx:19-25`, `AdvancedMode.tsx:9-29` [interface-only].

---

## Part II — Ten Invention Records

### Invention #1 — Hybrid Local + Cloud Avatar Handoff Protocol

**What.** A typed protocol that lets Ember run local embodiment (SAP-style VRM/Live2D at T0/T1) and cloud embodiment (LiveKit-tier streaming) in tandem, with runtime handoff between them.

**Kit gap.** The kit ships one mode at a time — `BasicMode` *or* `AdvancedMode`, switched by `useState` at `App.tsx:6`. Hybrid-and-handoff is outside scope.

**Ember.** Andlit holds two child providers (`LocalRenderer`, `CloudRenderer`); both consume the same affect snapshot and action vocabulary. A `HandoffOrchestrator` watches operator intent, synchronizes affect state across renderers (via SAP-derived `[[sap:66_INVENTED_METHODS]]#1`), warms up the target renderer, performs a ~500ms cross-fade, drains the source, and logs the handoff. The model emits the same intent regardless of which renderer is active.

**Cite-shape.** `src/ember/spark/andlit/handoff.py`, ~250 LOC. **Vows.** Modular Authorship, Tiered Presence, Graceful Offline.

---

### Invention #2 — Cloud-Session-as-Typed-Resource (TTL + Scope)

**What.** The `CloudSession` dataclass from ADR-WAIFU-005 treated as the first-class noun of the cloud-tier surface — a thing that lives, is observable, expires, and dies.

**Kit gap.** The kit's session is a React hook return value (`useAvatarSession` at `AdvancedMode.tsx:10-14`). Unmount the component, the session is gone. There is no persistent record.

**Ember.** Brunnr-resident `CloudSession` records, persisted on issuance, inspected via `ember andlit list`, revoked via CLI or auto-revoke triggers. Ember treats cloud sessions the way a careful system treats file handles: explicit open, explicit close, finalizers, audit log.

**Cite-shape.** `src/ember/spark/andlit/cloud_session.py` + Brunnr migration; ~300 LOC. **Vows.** Surface Without Surveillance, Honest Memory, Graceful Offline, Tethered Grounding.

---

### Invention #3 — Bandwidth-Tier-Aware Action Surface

**What.** A degradation gradient on the action vocabulary: at full bandwidth, expensive actions (multi-frame motion) emit fully; at constrained bandwidth, they substitute to cheap approximations (held-pose with tag, glyphic notation, italic verbal description). Expressive even when the media plane starves.

**Kit gap.** The kit shows a loader spinner at `AdvancedMode.tsx:87-91` and waits. No "same action, cheaper" concept.

**Ember.** Each action in YAML carries `bandwidth_cost` and `substitute_at_lower_bandwidth`. Strengr publishes a `current_bandwidth_class` signal; the dispatcher consults it. `dance` at `bandwidth=low` becomes `nod_with_emoji(dance_glyph)`; at `bandwidth=very_low`, `*Ember dances briefly*`. Substitutions are **announced**, never silent.

**Cite-shape.** Extends `src/ember/spark/andlit/actions.py`; ~150 LOC. **Vows.** Tiered Presence, Graceful Offline, Embodied Honesty, Affective Restraint.

---

### Invention #4 — Local-First / Cloud-Augmented Presence Mode

**What.** A named mode where Ember runs local-VRM as the operator-facing surface and cloud-streaming as the audience-facing surface, both synchronized on the same affect and action stream. The operator sees the local VRM; remote viewers see the cloud avatar; both reflect the same Ember.

**Kit gap.** The kit assumes a single audience — the local user of the React app. The asymmetric operator-private / audience-public case is outside scope.

**Ember.** Configured in `~/.ember/config/presence.yaml`: `mode: local_first_cloud_augmented`, `local_renderer: vrm`, `cloud_renderer: livekit+zeroweight`. The two surfaces are independently shutdown-able. Operator closes the local UI → cloud continues. Cloud is stopped → local continues.

**Cite-shape.** `src/ember/spark/andlit/presence_modes.py`; ~200 LOC. **Vows.** Tiered Presence, Modular Authorship, Surface Without Surveillance, Affective Restraint.

---

### Invention #5 — Revocable Cloud-Session Scope Token

**What.** A signed, time-bounded, narrowly-scoped credential the operator issues per session, naming the renderer, action vocabulary subset, audience scope, TTL, and revoke endpoint. Revocation is one CLI call, honored both by Ember's local refusal-to-emit and by the cloud provider's revoke endpoint.

**Kit gap.** The kit's "auth" is a long-lived `apiKey` prop embedded in source (`BasicMode.tsx:21`). No scope, no TTL beyond account-level controls; revocation requires logging into the vendor dashboard.

**Ember.** Per-session `ScopeToken(issuer_persona_id, scope, audience, ttl, issued_at, signature, revoke_endpoint)`. Signed with the persona-key per `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-005. Revoke via `ember andlit revoke <session_id>` — Ember stops emitting; if the provider exposes a revoke endpoint, Ember calls it. Auto-expires at TTL.

**Cite-shape.** `src/ember/spark/andlit/scope_token.py`; ~120 LOC. **Vows.** Surface Without Surveillance, Honest Memory, Affective Restraint, Public-Friendliness.

---

### Invention #6 — Network-Resilience Fallback Ladder

**What.** A declarative degradation chain naming what cloud-tier presence looks like at every network impairment level: `healthy → degraded → poor → offline → catastrophic`, mapped respectively to `full_cloud_presence → cloud_audio_only → text_with_affect_tag → local_fallback → log_line_only`. Transitions are **announced**.

**Kit gap.** Whatever LiveKit's reconnect logic provides, plus a spinner at `AdvancedMode.tsx:87-91`. No operator-facing intermediate state.

**Ember.** A state machine in Strengr publishes `network_class`; Andlit's dispatcher consults `~/.ember/config/andlit_fallback.yaml` for the transition table. Each transition announces via Hugarsýn ("Andlit degraded to cloud-audio-only at 14:32 due to packet loss"). Recovery announces too.

**Cite-shape.** `src/ember/spark/andlit/fallback_ladder.py`; ~180 LOC. **Vows.** Graceful Offline, Embodied Honesty, Surface Without Surveillance, Tiered Presence.

---

### Invention #7 — Action Vocabulary Negotiation (vs Hardcoded Names)

**What.** A handshake at cloud-session-open: the renderer publishes its supported actions; Ember declares the operator-consented subset; the intersection becomes the active vocabulary. Mid-session renegotiation supported.

**Kit gap.** The kit hardcodes three action names at `AdvancedMode.tsx:45-49`. Avatar swap → silent dispatch of unknown actions, silently ignored. No negotiation; only assumption.

**Ember.** At `CloudSession` open, the provider adapter answers `supported_actions() -> frozenset[str]`. Ember intersects with the operator's consent-gated vocabulary; the model's prompt now includes only the intersection. If the renderer hot-swaps avatars mid-session, renegotiation refreshes the active set and the prompt enumeration. Empty intersection → expression-only mode, audit-logged.

**Cite-shape.** `src/ember/spark/andlit/action_negotiation.py`; ~100 LOC. **Vows.** Affective Restraint, Pluggable Storage, Embodied Honesty, Honest Memory.

---

### Invention #8 — Audit Trail for Cloud-Rendered Avatar Expressions

**What.** Every avatar expression Ember emits to a cloud renderer logs with originating context: conversation turn, affect snapshot, consent token, cloud session, renderer ack. Queryable: *"show every action Ember sent to the cloud avatar this week."*

**Kit gap.** `session.runAction("embarrassed")` at `AdvancedMode.tsx:45` is a one-shot call. What happens after is opaque; nothing is logged. The action is ephemeral — out of the React component, gone.

**Ember.** `CloudAvatarAuditRecord(record_id, timestamp, session_id, persona_id, action_name, affect_snapshot_id, consent_token_id, conversation_turn_id, renderer_ack, substitution_applied)`. Brunnr-resident. Queried via `ember introspect cloud_audit`. Ties into the trust-chain field from SAP's `[[sap:66_INVENTED_METHODS]]#12` when the action originated from an MCP peer.

**Cite-shape.** `src/ember/spark/andlit/audit.py` + Brunnr schema; ~150 LOC. **Vows.** Honest Memory, Surface Without Surveillance, Tethered Grounding.

---

### Invention #9 — Consent Token for Mic Capture (Revocable, Scoped)

**What.** A scope-token-shaped credential authorizing microphone capture for a specific session. Specifies duration, destination, audio scope (raw / VAD-segmented / transcript-only), revoke endpoint. Revocation triggers `MediaStreamTrack.stop()` — the *device* releases, not just the track muted.

**Kit gap.** Mic capture is bound to LiveKit's `audio={true}` at `AdvancedMode.tsx:173`. The mic toggle (line 27) flips mute, not device-claim. The browser holds the microphone for the session's life. The operator who *trusts* this UI to release the mic is wrong.

**Ember.** Capture starts only after the operator signs the consent token (visible ceremony, not a hidden dialog). Expiry, revocation, lid-close, or audit anomaly → immediate `MediaStreamTrack.stop()`, device released, announced in audit log. A `mic_max_continuous_capture` config (default 10 min) forces token re-issuance — friction against forgotten-mic-forever scenarios.

**Cite-shape.** `src/ember/spark/rodd/mic_consent.py` + browser adapter; ~140 LOC. **Vows.** Surface Without Surveillance, Honest Memory, Embodied Honesty.

---

### Invention #10 — Cloud-Avatar Provider Protocol with Identity Binding

**What.** A typed Protocol any cloud-avatar provider must satisfy: session open, action dispatch, affect snapshot push, action-vocabulary publication, audio routing, revoke. Each implementation **binds the provider's avatar identity to Ember's persona_id**, so the operator can audit *which Ember was visible on which cloud identity*.

**Kit gap.** The kit binds to one provider (ZeroWeight) via `apiKey` + `avatarId` props (`BasicMode.tsx:20-21`). No abstraction. No identity binding — the provider has no idea *which* Ember is connecting, beyond the account scope.

**Ember.** `CloudAvatarProvider` Protocol with methods `supported_actions()`, `supported_scopes()`, `open_session(persona_id, scope_token)`, `push_affect(session, snapshot)`, `dispatch_action(session, action)`, `revoke_session(session)`, `bind_identity(persona_id, provider_avatar_id)`. The `IdentityBinding` table in Brunnr ties Ember's `persona_id` to the provider's avatar identity, operator-confirmed at first connection, inspectable via `ember andlit bindings list`, revocable.

**Cite-shape.** `src/ember/spark/andlit/provider_protocol.py` + `providers/livekit.py`; ~250 LOC core + ~80 LOC per additional provider. **Vows.** Pluggable Storage, Modular Authorship, Honest Memory, Surface Without Surveillance.

---

## Cross-References

- `[[60_REALTIME_TIER_FOR_ANDLIT]]` — Cartographer's tier engine work; ADR-WAIFU-003 ratifies the Tier-CLOUD branch.
- `[[00_OVERTURE]]`, `[[01_VISION_SYNTHESIS]]` — Skald's framing of the realtime cloud axis.
- `[[11_DUAL_MODE_PATTERN]]` — invention #4 is the third mode the BasicMode/AdvancedMode duality implies.
- `[[20_ZEROWEIGHT_SURFACE]]`, `[[21_LIVEKIT_INTEGRATION]]`, `[[22_ACTION_PROTOCOL]]` — the interface docs ADR-WAIFU-001/-002/-004 build on.
- `[[31_ADVANCED_MODE_FLOW]]` — the session lifecycle ADR-WAIFU-005 replaces.
- `[[51_SECURITY_AND_PRIVACY]]`, `[[52_NO_LICENSE_RISK]]` — the threat and license posture constraining every adoption.
- `[[sap:11_AVATAR_DOMAIN]]`, `[[sap:25_AVATAR_PROTOCOL]]`, `[[sap:32_AVATAR_RENDER_PIPELINE]]` — SAP's local pipeline that #1 and #4 join cloud-side.
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — the Andlit/Rödd True Names this whole synthesis presupposes.
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the tier ladder ADR-WAIFU-003 extends.
- `[[sap:65_META_AWARENESS]]` — Hugarsýn introspection that #2, #6, #8 publish to.
- `[[sap:66_INVENTED_METHODS]]#1, #4, #6, #12` — SAP inventions reused by #1, ADR-005, #4, #8.
- `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-005 — persona-id signing used by #5, #10.
- `[[hermes:Defended System Prompt]]` — Hermes-side typed-instruction discipline behind ADR-WAIFU-004's typed vocabulary.
- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]` — iron laws and Cyber-Viking aesthetic bounding every proposal.

---

## What This Means for Ember

The kit is small. The keepers' work is correspondingly small. But the *territory* it illuminates — the realtime cloud presence axis — is not small. SAP looked downward and inward, into the host's local capabilities. The kit's gaze is outward and upward, into the cloud substrate. The two gazes together make the Andlit-realtime tier visible.

**Adopt:**

- **LiveKit (MIT)** as the realtime media substrate per ADR-WAIFU-001 — upstream-cited, not kit-cited; Python `livekit-agents` for server, Node `livekit-client` for the optional browser tier.
- **Persistent typed cloud-session records** per ADR-WAIFU-005 + invention #2 — Brunnr-resident, CLI-inspectable, auto-revoke on lid-close, TTL, or operator command.
- **The dual-mode documentation pedagogy** — Ember's docs should ship `andlit_minimal_example.py` and `andlit_full_example.py` mirroring the kit's BasicMode/AdvancedMode split, so operators have two integration depths to learn from.

**Adapt:**

- **The kit's React session-hook shape** (one state object with `isConnected`/`timeRemaining`/`connect`/`disconnect`/`toggleMic`) is the *kind* of API operators want from a high-level wrapper. Ember's Python equivalent should expose the same conceptual surface without borrowing code — `[license-pending — adapting pattern shape, not code]`.
- **The action-vocabulary brevity** (three actions, hand-curated) is *correct* for an example, *wrong* for production. Ember adapts the idea of a small named vocabulary into the typed enumeration with consent gates of ADR-WAIFU-004.
- **The session-duration cap** (`sessionDuration={120}`) is good discipline. Ember adapts it into `CloudSession.expires_at` (default 10 min, configurable), with renewal as a deliberate operator action.

**Avoid:**

- **Embedding long-lived credentials in client code** — the `apiKey` pattern at `BasicMode.tsx:21` is a teaching artifact. Ember uses scope tokens, not raw API keys.
- **Untyped string actions** — ADR-WAIFU-004 names why.
- **Opaque sessions** that vanish on component unmount — ADR-WAIFU-005 names why.
- **Silent network degradation** — invention #6 names why.
- **Mic capture without an explicit consent surface** — invention #9 names why.
- **Vendoring kit code** — `[[52_NO_LICENSE_RISK]]` and ADR-WAIFU-002 name why.
- **Defaulting to cloud-tier** — Tier-CLOUD is *parallel* to T0, not above. Operators choose; Ember does not push.

**Invent:**

1. Hybrid Local+Cloud Avatar Handoff Protocol
2. Cloud-Session-as-Typed-Resource
3. Bandwidth-Tier-Aware Action Surface
4. Local-First / Cloud-Augmented Presence Mode
5. Revocable Cloud-Session Scope Token
6. Network-Resilience Fallback Ladder
7. Action Vocabulary Negotiation
8. Audit Trail for Cloud-Rendered Avatar Expressions
9. Consent-Token for Mic Capture
10. Cloud-Avatar Provider Protocol with Identity Binding

---

The kit is 846 lines and seven commits. It is the smallest source any Ember codex has been built upon. Five ADRs claim the structural ground; ten inventions name the patterns Ember will need but the kit did not have. Neither set is exhaustive; both are honest. The decisions are **Proposed**; the inventions are **Territory Marks**. They commit Ember to *knowing what cloud-tier presence ought to look like*, so that if and when Volmarr decides to walk that axis, the path is mapped. The envelope is small. The seal is intact.

— Eirwyn Rúnblóm, sealing
