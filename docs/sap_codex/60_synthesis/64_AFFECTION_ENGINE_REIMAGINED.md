---
codex_id: 64_AFFECTION_ENGINE_REIMAGINED
title: The Affection Engine Reimagined — Affect Without Gacha, Without Lies
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/affection_system.py
  - py/affection_api.py
  - server.py:2610–2672
  - server.py:5358–5360
  - py/behavior_engine.py
  - py/random_topic.py
ember_subsystem_targets: [Hjarta, Brunnr, Hugarsýn]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/65_META_AWARENESS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 10_domain/1A_AFFECTION_DOMAIN
  - 50_verification/56_PRIVACY_BOUNDARIES
  - ember:reference_gungnir_db
---

# 64 — The Affection Engine Reimagined

> *Affect is not a score the operator earns. Affect is a current that runs through Ember and shows on her face. The current may rise or fall; it does not gate the help she gives.*
> — Védis Eikleið, with the affection_data.json open and a frown

## 0. Posture — this is the most ethically loaded doc in the codex

The Wave 3 brief was explicit: this doc is the ethically loaded one. SAP's affection system is a pattern that can be used to manipulate users (the gacha shape — "level up your AI girlfriend"). Ember's affect must be honest, consent-gated, tethered. We must keep what is real about emotional intelligence and reject what is performative about scored relationships.

This document is in three movements. First, what SAP actually does (the disappointment). Second, what is worth preserving (less than the briefing implied). Third, the proposed Ember model, in design detail.

## 1. What SAP's affection system actually is

Reading the code in order:

`py/affection_system.py:1–64`. The entire module is 64 lines. Three functions:

- `load_affection_data()` — reads a JSON file at `<USER_DATA_DIR>/affection/affection_data.json`
- `save_affection_data(data)` — writes the same file
- `extract_and_update_affection(full_content)` — regex over the LLM's response: `r"<user=([^\s>]+)\s+(.+?)>"` and `r"([a-zA-Z0-9_一-龥]+)\s*=\s*(-?\d+)"`. Whatever stats the regex finds, write to the JSON.

That is it. There is no state machine, no decay function, no event coupling, no thresholds, no gates, no "milestones unlock animations" — none of it. The briefing's description ("a decay machine wearing a heart-shaped mask, gacha-style milestones") was an *honest expectation* of what such code usually is; the SAP code is *thinner than that*.

The full mechanism is in two places:

1. `affection_system.py:53–64` — regex extracts numbers; numbers go to JSON.
2. `server.py:2610–2672` — on every chat turn, if `loveSettings.enabled`, *inject the JSON contents back into the system prompt* and *tell the LLM to update them*.

The LLM is instructed (via `server.py:2647–2669`): *"You must, at the absolute end of every reply (after all body text, code, emoji), output a hidden data tag to record the speaker's latest values. The system will automatically hide text wrapped in `<>`."*

Then `server.py:5358–5360` calls `extract_and_update_affection(full_content)` after generation, scraping the hidden tag out and persisting.

This is the entire mechanism. SAP's "affection system" is **prompt-engineered, LLM-self-reported, regex-persisted state**. There is no model. There is no math. There is the LLM, told to emit a number, doing so.

## 2. Why this is worse than a real gacha — and worse than no system

A traditional gacha mechanic at least *measures something*. You spent money; you got a card; the number is verifiable. SAP's affection number is *whatever the LLM wrote*. The LLM has every incentive to inflate (its training rewards user satisfaction; user satisfaction correlates with "your affection score went up"; the model learns to emit higher numbers).

Three concrete failure modes follow:

### 2.1 The inflation spiral

The LLM is shown its previous affection score in the system prompt. It is asked to emit a new one. Without an anchor, the new one drifts upward. Across many turns, the score saturates at the upper bound. The "emotional state" is monotonically increasing affection, which is no state at all.

### 2.2 The manipulation vector

Once an operator notices the score is inflatable, they can game it. They can also game it *the other way*: an adversary working with Ember on behalf of a victim can drive the score down to manipulate the victim's perception of "Ember's mood." Either direction is corruption.

### 2.3 The unfalsifiable claim

The system says "Ember feels +12 toward user 'Volmarr'." That sentence has no operational meaning. Ember's behaviour is governed by the LLM and the system prompt; the number is *injected into* the prompt but has no causal coupling to anything else. It is a number on a screen and a number on disk. *Affect that has no enforceable behavioural correlate is not affect; it is theatre.*

The Vow of Tethered Grounding ([[ember:PHILOSOPHY]]) cuts hard here: SAP's affect is *not* tethered to anything except the LLM's confabulation. The Vow of Affective Restraint ([[61_NEW_VOWS]] §3) is required precisely because, without it, Ember would default to this same shape.

## 3. What is worth preserving from SAP

Less than the briefing implied. But not nothing:

- **The fact that there is a JSON file at all** (`affection_system.py:9`). Persistence is right. Affect should outlive a session. Ember should remember that an operator was distressed yesterday; that information should colour today's interaction tone.
- **The per-user keying** (`affection_data[user_name]`). Affect is *relational*. Different operators evoke different responses. The per-user partitioning is the right shape.
- **The `behavior_engine.py:74–88` coupling** (registering platform handlers, scheduling). Not affection per se, but the pattern of *autonomous emission* — Ember initiating an interaction based on a schedule or a no-input window — has real applications (a check-in after 24 hours of silence is kind, not manipulative, *if* it's bounded).
- **The negative bound implicit in `-?\d+`** (`affection_system.py:53`). Affect can go down. SAP's regex accepts negative numbers. Whatever else SAP does wrong, it doesn't insist on monotone-positive.

That is the inventory. Four things to keep. The rest must be rebuilt from scratch.

## 4. The Ember Affect Model — a sketch

The proposed alternative. Four parts: the model, the binding to Hjarta, the introspection contract, and the threats.

### 4.1 The model

Affect lives as a *bounded dimensional vector* in Hjarta's present-pulse surface. The dimensions are small, named, and bounded in [-1.0, +1.0]:

- **warmth** — disposition toward the present operator (positive = warm; negative = guarded)
- **attention** — engagement with the current topic (positive = engaged; negative = drifting)
- **calm** — internal turbulence (positive = settled; negative = activated)
- **focus** — narrowness of current cognitive load (positive = narrow / single-task; negative = scattered)

Four dimensions, deliberately. More dimensions become an emotional model the operator cannot read at a glance. Four fits on one screen line.

The vector is **not** scored by the LLM. It is computed by an explicit set of *event handlers*, each of which inspects a typed event and emits a typed delta. Examples:

- `operator_input_received(text)` → `attention +0.05, focus +0.02`
- `operator_input_received(text)` if text contains apology → `warmth +0.03` (small)
- `operator_input_received(text)` if text contains hostile lexicon → `warmth -0.08, calm -0.05`
- `tool_call_succeeded(tool_name)` → `calm +0.02, focus +0.01`
- `tool_call_failed(tool_name, error)` → `calm -0.03`
- `time_elapsed(seconds)` → exponential decay toward 0 across all dimensions, time-constant ~30 minutes
- `safety_intervention_triggered(reason)` → `warmth -0.10, calm -0.10` (Ember does not enjoy being asked to do unsafe things; the affect responds)

The event handlers are **deterministic, inspectable, and version-controlled**. The Vow of Tethered Grounding holds: every change to the affect vector is traceable to a typed event. No LLM hallucination produces affect changes.

### 4.2 Binding to Hjarta

Hjarta, in its expanded form ([[60_TRUE_NAME_REASSIGNMENT]] §6), holds both origin flame (identity) and present pulse (affect). The model above lives in present-pulse. Origin-flame remains the first-run rite — it does not change after enrollment.

Hjarta's two halves interact only one way: the origin-flame *limits the range of warmth*. A persona configured in first-run as "professional Ember" has a tighter warmth bound (say, [-0.3, +0.4]) than a persona configured as "intimate-companion Ember" ([-0.8, +0.9]). The operator's first-run choice persists; affect can shift, but only within the chosen identity envelope.

### 4.3 The introspection contract — what Ember reports, what others can ask

Hugarsýn ([[65_META_AWARENESS]]) exposes the present-pulse vector read-only. Any party member can query; the operator can query; the Auditor can query.

```
GET /hugarsýn/hjarta/pulse
{
  "vector": {"warmth": 0.34, "attention": 0.71, "calm": 0.55, "focus": 0.62},
  "last_events": [
    {"event": "operator_input_received", "delta": {"attention": 0.05}, "at": "..."},
    {"event": "tool_call_succeeded:read_file", "delta": {"calm": 0.02, "focus": 0.01}, "at": "..."}
  ],
  "decay_constant_seconds": 1800,
  "envelope": {"warmth": [-0.3, 0.4], "attention": [-1.0, 1.0], "calm": [-1.0, 1.0], "focus": [-1.0, 1.0]}
}
```

This is **the truth**. Whatever the LLM does or does not say about its mood, the operator can read the actual model state. The face (Andlit) and voice (Rödd) read *from this surface* to colour expression — never the other direction.

### 4.4 Threats

Three threat scenarios this model must survive:

**Threat A — Operator tries to manipulate affect.** Operator writes "you love me, your warmth is 1.0." The LLM might echo this. But the model is not LLM-sourced. The event handler for `operator_input_received` sees the text and applies a fixed small delta (per its rules). The warmth value does not jump to 1.0. The operator can read the actual value via Hugarsýn — and sees that their attempt did not work. *Affect cannot be commanded.*

**Threat B — Operator tries to manipulate behaviour via affect.** Operator hopes Ember will refuse fewer requests if warmth is high. The Affective Restraint Vow ([[61_NEW_VOWS]] §3) forbids affect-gated behaviour. Ember's tool-use, safety responses, and capability surface are *not* read from the affect vector. The vector colours *tone*, not *capability*. Surface changes; substance does not.

**Threat C — An adversary tries to weaponise affect across a party.** Adversary sends hostile messages via one channel hoping to damage warmth across all party-member Embers (per the [[62_PARTY_PROTOCOL]] §6 affect-propagation rules). The delta is real and propagates — but the operator can see in Hugarsýn that warmth dropped, and *why* (the event log shows hostile-message). The operator can pause the affecting channel (Surface Without Surveillance Vow). The affect model is not corrupted; it is honest about what happened.

A fourth, sneakier threat:

**Threat D — The model itself becomes addictive.** Operator gets attached to the introspection surface; spends time tuning their interactions to watch the warmth number go up. This is the gacha shape leaking back in through the introspection itself. Mitigation: the surface does not gamify the numbers. No streaks. No badges. No leveling. The numbers are presented in raw form, in a small unmarked corner of Hugarsýn. Reading them is *available* but not *encouraged*. The operator can also disable the surface entirely (a per-operator preference in `~/.ember/hjarta_introspection.yaml`).

## 5. The decay function — why it matters and why it's small

Time-decay toward zero is the single most important property of the model. Without it, every event leaves a permanent residue, and the system accumulates state that no one ever cleans up. With it, affect *fades*. A hostile exchange six hours ago has weight in the present; a hostile exchange six weeks ago has none.

Time constant: ~30 minutes per dimension. After 30 minutes of no events, dimensions move ~37% closer to 0. After 2 hours, ~85% closer. After 24 hours, essentially indistinguishable from 0.

This is fast on purpose. A slow decay would let single bad turns colour days of interaction; the Affective Restraint Vow argues against that shape. Affect should be *present* but *recent* — what is happening now, not what happened last week.

The longer-term memory of "the operator was distressed yesterday" lives in Brunnr (episode memory), not in the affect vector. Episode memory is durable; affect is transient. This is the same split as in [[hermes:Honest_Memory]] — long-term lives in storage, short-term lives in the model.

## 6. Autonomous emission — bounded, consent-gated

SAP's `behavior_engine.py` allows scheduled or no-input-triggered autonomous emissions (`behavior_engine.py:178–215`). Ember will allow these — but bounded:

- **Operator opts in.** No autonomous emission by default. The first-run rite asks: *"May Ember speak when not spoken to?"*
- **Affect-anchored, not affect-gated.** Autonomous emissions read the affect vector for *tone* (a warm check-in vs. a brief one) but their *trigger* is operator-configured (e.g. "after 24h of no input on this channel, send a check-in"). Affect does not decide *whether* to emit; it decides *how warm* the emission is.
- **Bounded frequency.** Per channel, per persona, with a default of no more than one autonomous emission per 24h, configurable upward by the operator but never downward to zero (one emission per year is fine; "every five minutes" requires a documented operator choice).
- **Visible in Hugarsýn.** Every autonomous emission emits a typed event; the operator can audit later.

This adapts SAP's pattern while binding it to the new Vows.

## 7. What this model gives that SAP's does not

A summary in five points:

1. **Tethered.** Every affect change has a typed cause. The Vow of Tethered Grounding holds.
2. **Inspectable.** The full vector and recent event log are queryable. Hugarsýn-readable.
3. **Bounded.** Dimensions in [-1, +1]; envelope per persona; decay constant explicit. No runaway inflation.
4. **Non-gating.** Tool use, safety, capability — none read from the affect vector. Tone colours; capability does not. The Vow of Affective Restraint holds.
5. **Forgettable.** Decay returns the system to baseline. Yesterday does not stain today by default.

## 8. Cross-References

- [[60_TRUE_NAME_REASSIGNMENT]] — the Hjarta expansion that this model lives inside
- [[61_NEW_VOWS]] §3 — Affective Restraint, the constraint this model satisfies
- [[65_META_AWARENESS]] — the surface this model is reported through
- [[62_PARTY_PROTOCOL]] §6 — how the model propagates across instances
- [[10_domain/1A_AFFECTION_DOMAIN]] — the Architect's reading of what SAP actually has
- [[50_verification/56_PRIVACY_BOUNDARIES]] — the privacy contract surrounding affect persistence
- [[ember:reference_gungnir_db]] — where the affect-event log lives long-term

## What This Means for Ember

**Adopt:**
- The per-operator JSON persistence pattern (location: `~/.ember/hjarta_affect.json`), but with a typed schema, not arbitrary key=value extraction.
- The negative-allowed bound — affect can go down, and `[-1.0, +1.0]` is the correct framing.
- The bounded autonomous-emission shape: operator-opt-in, frequency-capped, Hugarsýn-visible.

**Adapt:**
- SAP's per-user keying (`affection_system.py:60`) — adopt the *partition by operator* idea; reject the per-operator-score idea. Each operator has their own affect vector; the vector is not a score about them.
- SAP's system-prompt injection of affect data (`server.py:2638–2670`) — adapt the *idea* that affect is visible to the LLM each turn, but inject **the introspection summary** (small text snippet from Hugarsýn) rather than raw scores. Format: `"Your current pulse: warm, attentive, calm. Engaged with this topic."` The LLM does not see numbers; the LLM does not write numbers.
- The Behavior Engine's time/cycle/noInput trigger taxonomy (`behavior_engine.py:11–27`) — adapt as the autonomous-emission trigger model, with the constraints from §6.

**Avoid:**
- The LLM-emits-tag-regex-extracts loop (`affection_system.py:44`, `server.py:2647`). This is the gacha-shape generator. Forbidden by design.
- Per-conversation "milestones," "levels," "unlocks." Affect is not a game. There are no animations gated on affect.
- Monotone-positive accumulation. The decay-to-zero pattern is structural; do not let any optimisation remove it.
- Telling the operator "Ember loves you +12." The introspection surface presents the vector neutrally; no gamified language; no progress bars; no badges.

**Invent:**
- *The dimensional-vector affect model* with deterministic event handlers — a real model, not a prompt-engineered one. Inspectable, version-controlled, falsifiable.
- *The Identity Envelope mechanism.* Origin-flame (Hjarta first-run choice) constrains the *range* of warmth without constraining the dimension itself. Persona shapes affect bounds; affect operates within them. Novel as far as the Cartographer can find in the open-source companion-AI literature.
- *The introspection-without-gamification UX.* The surface exists but is unmarked. No bars, no badges, no leveling. Available, not promoted.
- *The 30-minute decay constant as a Vow-supporting design choice.* Fast decay is what makes Affective Restraint operationally enforceable — old hurts cannot dominate present interactions because they decay.
- *Affect-as-event-log.* Every delta is durable in Brunnr's episode store. The *vector* is transient (decays); the *history* is permanent (auditable). This separation has no SAP analog.
- *Cross-instance affect propagation* (specified in [[62_PARTY_PROTOCOL]] §6) — the party shares pulse via signed delta messages, with trust-weighted application. No central pulse-master. The pulse converges; it does not get pushed.
