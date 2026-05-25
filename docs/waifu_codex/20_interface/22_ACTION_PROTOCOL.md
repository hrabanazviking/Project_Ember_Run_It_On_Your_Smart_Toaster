---
codex_id: 22_ACTION_PROTOCOL
title: Action Protocol — Three Strings As The Entire Vocabulary, Untyped And Ungated
role: Auditor
layer: Interface
status: draft
waifu_source_refs:
  - src/modes/AdvancedMode.tsx:41-51
  - src/modes/AdvancedMode.tsx:9-29
  - README.md (action vocabulary requirement)
ember_subsystem_targets: [Hjarta, Munnr, Andlit-realtime, Rödd-realtime]
cross_refs:
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - sap:25_AVATAR_PROTOCOL
  - sap:1A_AFFECTION_DOMAIN
  - sap:60_TRUE_NAME_REASSIGNMENT
---

# Action Protocol — Three Strings As The Entire Vocabulary, Untyped And Ungated

> *Sólrún, voice cold and even: the kit's avatar action protocol fits on a Post-it note. Three string literals — "embarrassed", "dance", "wave_hand" — dispatched by a uniform-random branch on a click handler, sent into the SDK without negotiation, without acknowledgment, without typing, without consent gating. This is a sketch, not a protocol. Ember will need an actual protocol, and the sketch is useful precisely because it reveals every place the actual protocol must add discipline.*

This document audits the kit's avatar action surface as a *contract*. The lens: **what is the action protocol, where is it brittle, what does a real protocol require?** Comparison to `[[sap:25_AVATAR_PROTOCOL]]` (SAP's VRM-tag system) is essential — SAP solved the same problem for local VRM avatars and arrived at a different, also-imperfect surface. Ember learns from both.

---

## 1. The Surface, In Full

`AdvancedMode.tsx:41-51`:

```typescript
const handleToogleCharacter = () => {
  const randomVal = Math.random();

  if (randomVal < 0.3) {
    session.runAction("embarrassed")
  } else if (randomVal < 0.6) {
    session.runAction("dance")
  } else {
    session.runAction("wave_hand")
  }
}
```

The function is bound at `AdvancedMode.tsx:84`:

```typescript
onClick={handleToogleCharacter}
```

`session.runAction(actionName: string)` is the kit's *entire* client-side action protocol. The session object is created by `useAvatarSession()` at `AdvancedMode.tsx:10` — a proprietary hook from `@zeroweight/react`, signature opaque to this audit. There is **no other action surface** in the kit's 846 LOC. The README confirms the vocabulary: *"Access to the avatar actions used in advanced mode: `embarrassed`, `dance`, and `wave_hand`."* The three actions are part of the operator's ZeroWeight avatar configuration, not the kit's invention.

---

## 2. What This Surface Is (And Isn't)

### 2.1 String-keyed dispatch table

The protocol's type is effectively `(name: string) => void`. No structured data, no parameters, no return value (the call site at `:45` does not `await`). The action name is the entire payload.

### 2.2 Not negotiated

No `getSupportedActions()`. No `actions.list()`. No protocol-version handshake. The three action names are *developer-hardcoded knowledge*. If the operator's ZeroWeight avatar is configured with a different action set (`wink`, `bow`, `peace_sign`), the kit's hardcoded names produce silent failure. If ZeroWeight rotates supported actions on the cloud side, the kit has no way to know.

### 2.3 Not error-handled

`session.runAction("embarrassed")` returns nothing visible. No `try/catch`. No `.then/.catch`. No toast, log, or UI feedback. In a 188-LOC file with seven UI buttons and four state flags, the action dispatch is the single most state-changing operation — treated as fire-and-forget.

### 2.4 Uniform-random

The dispatch (`AdvancedMode.tsx:42-50`) is `Math.random()` with three branches biased 30/30/40. The avatar dances because the number was between 0.3 and 0.6, not because the conversation called for dancing. Honest in a demo; it telegraphs the absence of *semantic* coupling between conversation state and action choice.

### 2.5 Consent-blind

Clicking the avatar (`AdvancedMode.tsx:84`) fires an action. No confirmation, no opt-in, no per-action permission. For three benign decorative actions, acceptable. The *pattern* is consent-blind by design — and it does not scale. If `runAction("show_credit_card_form")` ever existed in a future ZeroWeight surface, the kit's pattern would dispatch it with the same casual click.

---

## 3. The TypeScript Surface

The `session` object's destructuring at `AdvancedMode.tsx:16-29` reveals what is exposed:

```typescript
const {
  token,
  isConnected,
  isConnecting,
  isEngineReady,
  isLoadingActions,
  micMuted,
  volume,
  timeRemaining,
  connect,
  disconnect,
  toggleMic,
  startSessionTimer,
} = session;
```

Twelve fields. `runAction` is *not* in the destructure; the file calls `session.runAction(...)` directly at `:45,47,49`. `setVolume`, `containerRef`, `livekitUrl`, `markConnected` are also accessed via object reference. The destructure is convenience for the most-used fields.

Notably present: `isLoadingActions` (`:21, :157`). This flag suggests the SDK *fetches* action metadata at session start — meaning, internally, there is a notion of *which actions are available*. The kit does not surface this list to the developer; it only flags the loading-in-progress state. **This is significant.** Inside the SDK, an action-list-fetch event happens. The client could, in principle, know which actions are supported. The kit chose not to expose this. The protocol surface ZeroWeight could have made type-safe was, instead, a string-keyed dispatch.

---

## 4. The Failure Modes, Enumerated

### 4.1 Unknown action name → silent no-op

If the avatar is not configured for `embarrassed`, `session.runAction("embarrassed")` produces nothing. No avatar movement. No client error. The user clicks; nothing happens. Eventually they conclude the kit is broken. The worst kind of failure — silent.

### 4.2 Action name typo → silent no-op

`AdvancedMode.tsx:41` is named `handleToogleCharacter` (sic — `Toogle`, not `Toggle`). TypeScript catches function-name typos. A typo in `session.runAction("ebarrassed")` (missing `m`) behaves identically to §4.1 — silent no-op. The protocol is less safe than the language calling it.

### 4.3 Timing collision → undefined behavior

Rapid clicks dispatch three actions in succession. The cloud may queue, drop, or interrupt. The kit doesn't specify; the user observes whatever the cloud chooses.

### 4.4 Session disconnected → undefined behavior

If `isConnected === false` and `handleToogleCharacter` fires, `runAction` is called against a disconnected session. The kit does not guard with `if (!isConnected) return`. Behavior depends on SDK internals. In practice the `onClick` is on a canvas container that only exists when the session is at least initializing — but this is *spatial coupling*, not *type coupling*.

### 4.5 The Math.random fairness bug

Probability distribution: `embarrassed: 30%, dance: 30%, wave_hand: 40%`. Was the wave bias intentional? The kit doesn't say. The developer has to read branch conditions to discover it. In a contract, such choices would be specified.

---

## 5. The Comparison To SAP's VRM-Tag System

SAP's avatar protocol (`[[sap:25_AVATAR_PROTOCOL]]`) takes a different approach. SAP runs avatars *locally* (VRM, Live2D, VTube Studio). The animation surface is:

- **VRM blendshapes** for expressions (anger, sadness, joy — typed enum per VRM spec)
- **Bone manipulation** for poses (forward kinematics, declared per-bone)
- **Lip-sync** driven by audio analysis (no LLM input)
- **Affection-tag regex** parsed from LLM text output (`[[sap:1A_AFFECTION_DOMAIN]]`) — the LLM writes `<love>+2</love>`, SAP extracts via regex

**More flexible** than the kit on some axes: open-ended (any blendshape, any bone), schema-typed at the VRM spec level, composable (multiple tags per LLM response). **Less typed** on others: regex extraction is fragile, no negotiation, no consent gating.

Both protocols share a common flaw: **string-encoded action data, no schema, no validation at the protocol boundary, no negotiation**. The kit chose three named actions; SAP chose two-dozen tag families. The shape differs, the *contract discipline* is missing in both. Ember learns from the comparison and invents what neither provided.

---

## 6. The Cloud-Side LLM As Second Caller

A question this audit cannot fully answer (proprietary SDK): does ZeroWeight's cloud-side LLM invoke actions on its own? Inference from the SDK's pattern: almost certainly yes. The "AI avatar chat" framing means the LLM is producing avatar responses with timed animation. The cloud-side action invocation is happening, just not from client-side code.

This means **the action surface has at least two callers**: client `session.runAction(...)` (UI-initiated) and the cloud-side LLM's internal action dispatch (semantically-initiated). They share a vocabulary, presumably without coordination.

Any Ember action protocol must specify: which actor can call which action (operator, cloud LLM, voice command, UI click), what happens on collision, how *origin* is tracked (was that wave from a click or an LLM decision), and whether the operator can veto cloud-LLM-initiated actions. The kit silently assumes the cloud handles all of this. Ember cannot afford that assumption.

---

## 7. Affective Restraint As The Frame

`[[ember:RULES.AI]]` Vow of **Affective Restraint** (proposed in `[[sap:60_TRUE_NAME_REASSIGNMENT]]`, ratification-pending) reads in spirit: *the avatar should not perform affect actions the user has not consented to.* This operationalizes to action categories:

- **Decorative** (wave, bow, idle gestures) → no consent gate; benign by definition
- **Reactive emotional** (embarrassed, surprised, sad) → soft consent (Ember-level "show emotions" toggle)
- **Initiative-taking** (self-started dance, gesture without conversational prompt) → hard consent (operator opt-in; cloud LLM cannot self-initiate without explicit permission)
- **Host-affecting** (open URL, take screenshot, show overlay) → forbidden at cloud-tier per `[[51_SECURITY_AND_PRIVACY]]`

The kit's three actions span the first two categories. The kit does not gate them — fine for a demo, unacceptable for a Vow-binding Ember.

---

## 8. The Argument For A Typed Action Vocabulary

Ember should not adopt the kit's string-keyed protocol. The argument:

**Strings are typo-prone; enums are not.** `runAction("ebarrassed")` (missing `m`) compiles. `runAction(AvatarAction.Embarrassed)` does not. **Enums document the surface** — reading the type tells the developer what's possible. **Enums make negotiation tractable** — `getSupportedActions(): AvatarAction[]` is straightforward when the type is closed. **Enums allow per-action metadata**:

```typescript
const ACTION_METADATA: Record<AvatarAction, {
  category: "decorative" | "emotional" | "initiative",
  consent_level: "implicit" | "soft" | "hard" | "forbidden",
  display_name: string,
  cooldown_ms: number,
}>
```

The kit cannot have this declaration because the protocol is string-keyed.

---

## 9. Cross-References

- `[[20_ZEROWEIGHT_SURFACE]]` — the SDK surface this protocol is a fragment of
- `[[21_LIVEKIT_INTEGRATION]]` — the transport (LiveKit) does not see actions; they go through ZeroWeight's signaling
- `[[51_SECURITY_AND_PRIVACY]]` — action protocol as inbound command channel
- `[[52_NO_LICENSE_RISK]]` — the action names are ZeroWeight's API, not the kit's
- `[[sap:25_AVATAR_PROTOCOL]]` — SAP's VRM-tag protocol; the sibling exercise
- `[[sap:1A_AFFECTION_DOMAIN]]` — SAP's regex-tag extraction; the parallel anti-pattern
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — Andlit / Rödd / Hugarsýn proposal; the action protocol belongs to Andlit-realtime
- `[[ember:RULES.AI]]` — Vow of Affective Restraint applied to the action surface

---

## What This Means for Ember

**Adopt:**
- Adopt the **observation** that an action protocol *exists* as a separate surface from the audio + video streams. SAP's local-VRM approach folds animation into the render pipeline; the kit's separation is correct — actions are *commands*, video is *output*. Ember's avatar tier (local or cloud) keeps these separate. The shape of the separation is adoptable wholesale from the kit's pattern (not the kit's code — per `[[52_NO_LICENSE_RISK]]`).
- Adopt the **two-caller insight** (§6) into Ember's protocol design: every action protocol must specify which actors can invoke which actions, and how origin is tracked. The kit does not specify; Ember does. This is adopted as a *design requirement*, with the kit as the example of what skipping the requirement looks like.

**Adapt:**
- Adapt the kit's **action-vocabulary-as-string-list** into Ember's **typed `AvatarAction` enum + per-action metadata**. The vocabulary itself (decorative, emotional, initiative classes) is adapted from the kit's intent; the encoding (enum vs string) is Ember's improvement.
- Adapt the kit's **`isLoadingActions` flag pattern** (`AdvancedMode.tsx:21`) into Ember's `actions.state` machine: `IDLE → NEGOTIATING → READY → DEGRADED`. The kit's boolean conflates "loading" and "loaded"; Ember's state machine surfaces failure modes (`DEGRADED` when negotiation failed but session continues).
- Adapt the **uniform-random demo pattern** (`AdvancedMode.tsx:42-49`) into Ember's **action-trigger discipline**: client-side action firing is always *user-initiated and intentional* (specific gesture, not random click). Random-fire is only a demo affordance; production-Ember does not surface it. The pattern is adapted by removing its random nature.

**Avoid:**
- **Avoid string-keyed action dispatch.** The kit's `session.runAction("embarrassed")` is the exemplar of the unsafe pattern. Ember's equivalent must be `session.runAction(AvatarAction.Embarrassed)` with a discriminated-union ADT, not a string.
- **Avoid silent no-op on unknown action** (§4.1). Ember's wrapper logs unknown actions (operator-visible), increments a `unknown_action_count` metric, and optionally throws in dev mode. The kit's "click and nothing happens" failure mode is forbidden.
- **Avoid fire-and-forget action invocation.** Every Ember action call returns a `Promise<ActionResult>` (or equivalent). The caller can `await` for completion; the result includes `{ status: "fired" | "rejected" | "queued" | "timed_out", reason?: string }`. The kit's no-feedback fire is the negative template.
- **Avoid action invocation without consent gating per category.** Ember's action invocation goes through a per-action consent check: `if (consent.allows(action.category)) { actuallyFire() }`. Decorative actions pass freely; emotional actions pass per the operator's mood-toggle; initiative-taking actions require explicit per-session or per-context permission. The kit's no-gating is acceptable for a demo and unacceptable for Ember.
- **Avoid undocumented probability biases** (§4.5). If Ember ever has random-fire affordances (test mode, screensaver mode), the bias is declared in metadata, not buried in branch conditions.
- **Avoid coupling action invocation to spatial UI shape** (§4.4). The kit's "click the canvas to fire random action" pattern accidentally guards on session state via the canvas-only-exists-when-connecting property. Ember's action invocation guards explicitly on session state, decoupled from UI shape.
- **Avoid action-name typos that the language cannot catch** (§4.2). Typed enums make this impossible. The kit's string-literal pattern makes it inevitable.

**Invent:**
- **The `AvatarAction` Discriminated Union.** Ember's action vocabulary is a discriminated-union ADT:

  ```typescript
  type AvatarAction =
    | { kind: "decorative"; gesture: "wave" | "bow" | "nod" | "idle" }
    | { kind: "emotional"; emotion: "embarrassed" | "surprised" | "sad" | "joyful" }
    | { kind: "initiative"; performance: "dance" | "spin" | "leap" }
    | { kind: "speech-coupled"; lip_sync_track_id: string }
  ```

  Each variant carries its own data. Adding new actions extends the union; the compiler reports missing cases. The kit's string-keyed surface is replaced with a Vow-binding type. The vocabulary is per-avatar configurable (different avatars support different sets), declared in operator-side YAML.

- **The Action Negotiation Phase.** On session connect, Ember's client invokes `getSupportedActions(): AvatarAction[]`. The cloud (or local) avatar responds with its capability list. The client constructs UI from this list — buttons, voice-triggerable phrases, LLM-tool-schema entries — *all driven by the negotiation response*. The kit's hardcoded three names is the negative template; Ember discovers at runtime. (For local avatars, the negotiation is a pure-local query against the renderer's capability declaration.)

- **The Per-Action Consent Metadata.** Each `AvatarAction` variant carries a `consent_level: "implicit" | "soft" | "hard" | "forbidden"`. Implicit fires freely. Soft fires under a per-session-default toggle. Hard fires only with explicit user/operator confirmation per invocation. Forbidden never fires (the action is in the type but the policy is "no" at this tier). The Vow of *Affective Restraint* operationalized at the protocol level.

- **The Action-Origin Tag.** Every fired action carries `origin: "client_ui" | "cloud_llm" | "voice_command" | "scheduled" | "operator_admin"`. The cloud (or local) avatar logs origin per invocation. The operator can audit: which actions fired from which actor over a session. Forensic recordkeeping at the action layer. The kit's invocations have no origin tag; Ember's all do.

- **The Cooldown Per-Action.** Each `AvatarAction` declares a cooldown (e.g. `wave_hand`: 5 seconds; `dance`: 60 seconds). The wrapper enforces — calling `runAction(dance)` within 60 seconds of the last dance is a no-op with `{ status: "rejected", reason: "cooldown" }`. The kit allows rapid-fire dispatch; Ember rate-limits the contract.

- **The Action Coalescing Queue.** When multiple actions are requested in quick succession, the wrapper coalesces: if `embarrassed` is followed by `wave_hand` within 200ms, the queue keeps the latter (more recent = more relevant). Coalescing is per-category: emotional actions coalesce; decorative actions queue; initiative actions reject (only one at a time). The kit's queue behavior is opaque; Ember's is specified.

- **The `unknownActionPolicy` Per-Operator.** When an action is invoked that the negotiation phase did not advertise, Ember's wrapper consults policy: `IGNORE` (silent no-op, log), `WARN` (UI toast), `THROW` (development mode), `RECONCILE` (re-negotiate to refresh action list). The kit's silent no-op is the *default* for `IGNORE`; Ember exposes the choice.

- **The Avatar-Action TypeScript Surface Declaration.** Ember publishes `@ember/avatar-actions` (a TypeScript package) declaring the `AvatarAction` union, `AvatarActionResult`, `AvatarActionMetadata`, `AvatarActionPolicy`. Both local and cloud-tier avatar adapters implement against this surface. The kit's ZeroWeight-specific `useAvatarSession` is replaced by Ember's tier-agnostic interface. The Vow of *Modular Authorship* applied at the action protocol layer.

- **The Affective Restraint Vow As Policy.** The Vow becomes encoded as a per-session policy object: which action categories are permitted, which require explicit consent, which are forbidden. The policy is loaded from operator config (`config/avatar_policy.yaml` — never hardcoded, per `[[ember:RULES.AI]]`). Per session, the policy is consulted at every `runAction` call. The kit's no-policy state is the negative template; the policy is the invention.

The kit's action protocol fits in five lines of TypeScript. The Ember equivalent will fit in fifty — and those forty-five extra lines are the discipline that turns a demo into a system. The avatar's gesture should not be a roll of the dice; the avatar's gesture should be a contract between the LLM's intent, the operator's policy, and the user's consent. The kit's three strings are where this contract *isn't*. Ember's job is to write the version where it is.
