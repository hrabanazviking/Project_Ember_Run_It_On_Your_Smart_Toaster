---
codex_id: 66_INVENTED_METHODS
title: Invented Methods — Novel Patterns Visible Only Because of SAP
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - "(catalogues patterns NOT present in SAP — invention catalogue)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/65_META_AWARENESS
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# 66 — Invented Methods

> *Some patterns are visible only by their absence. SAP did not see them because it did not need to. Ember will need them, because Ember has Vows SAP does not keep.*
> — Eirwyn Rúnblóm, opening the invention book

## 0. Posture — Invention, Not Translation

This is the most unusual document in the Codex. Every other doc reads SAP and asks *what should Ember adopt, adapt, avoid?* This one asks the inverse question: *what patterns become visible because we read SAP, but were never present in SAP itself?*

The patterns catalogued here are not in `/tmp/super-agent-party/`. You will not find a `cross_host_affect_routing.py` to cite. What you will find is the *negative space* that SAP's design draws around — the things its choices forbid, the things its silences imply, the things its short edges leave undone. Ember's Vows of **Smallness**, **Tethered Grounding**, **Graceful Offline**, **Pluggable Storage**, **Modular Authorship**, and the proposed **Surface Without Surveillance** + **Tiered Presence** + **Federated Self** point at this negative space directly. SAP did not need to invent these because SAP was not built under these Vows. Ember does need them, because Ember is.

Each invention below names *what* SAP did instead, *why* SAP's choice does not survive Ember's Vows, and *how* Ember might do it differently. None of these are slice-plan items — they are *territory marks*. Some will become ADRs in `[[68_DECISION_RECORDS]]`. Some will live for years as documented intent before code arrives. All deserve names.

The Cartographer's `[[60_TRUE_NAME_REASSIGNMENT]]`, `[[62_PARTY_PROTOCOL]]`, `[[63_PERFORMANCE_TIER_ENGINE]]`, `[[64_AFFECTION_ENGINE_REIMAGINED]]`, and `[[65_META_AWARENESS]]` are the primary Wave 3 inventions on the embodiment and reach axes. The inventions here are the *adjacent* ones — patterns Cartographer's docs imply but do not catalogue in invention form, plus the Scribe's own discoveries from the same source reading.

---

## 1. Cross-Host Affect Routing

**SAP's pattern.** Affect state lives in a single JSON file on a single host: `affection_data.json` under `USER_DATA_DIR`, written by `affection_system.py:26-35` (`save_affection_data`). The state is scoped per *user name*, not per device. There is no concept of *which host this state belongs to*. When SAP runs on one machine, this is fine. When a user has SAP installed on a laptop and a desktop, the two affect states drift apart silently.

**Why SAP did not need this.** SAP is a single-host companion. Its assumption is one user, one machine, one running instance. The party metaphor stretches across IM platforms (Discord, Slack, Telegram) but not across machines running SAP.

**Why Ember needs it.** Ember is **multi-device by design** (per `[[ember:Tailnet-accessible by default]]` and `[[62_PARTY_PROTOCOL]]`). The same operator may interact with Ember on a workstation, a laptop, a phone, and a Pi within an hour. If affect lives per-host, the operator's relationship with Ember fragments. If affect lives centrally, the operator's offline experience breaks (Vow of Graceful Offline). The right answer is *routing*.

**Proposed invention.** **Affect-routing daemon** — a Hjarta subsystem that treats affect state as a CRDT (conflict-free replicated data type) keyed by `(operator_id, axis_name)` and replicated lazily across reachable Ember instances on the tailnet. Each Ember instance holds a local copy; mutations are timestamped + signed by the originating instance; reconciliation uses *last-writer-wins per axis* with a per-axis confidence band. When two instances disagree by more than a threshold, the result is *averaged with a divergence marker* rather than chosen — Ember tells the operator "I noticed you and I felt closer over the laptop than the desktop yesterday; I averaged." Honesty over precision.

Cite-shape (for the future implementation): `src/ember/spark/hjarta/affect_router.py`, key methods `route_mutation(axis, delta, source_host)`, `reconcile(remote_state)`, `divergence_report() -> list[AxisDivergence]`.

Vows touched: **Federated Self** (proposed), **Honest Memory** (carried from Hermes), **Tethered Grounding** (the affect state's authoritative log lives in the Well, not in any one host).

---

## 2. Low-Power VRM Stand-In (Text-and-Emoji Avatar)

**SAP's pattern.** SAP's embodiment is *rich or absent*. The VRM pipeline (`vts_manager.py:1-235`) and the Live2D path require a render budget. When the render budget is zero — Pi, phone, log-only environments — SAP has no avatar at all. The embodiment system silently degrades to "no body."

**Why SAP did not need this.** SAP's hardware floor is 2 cores / 2 GB RAM, which is enough for Electron + basic rendering. The case where the operator *wants* embodiment but *has* no render budget did not enter the design.

**Why Ember needs it.** The proposed Vow of **Tiered Presence** requires Ember to express herself at every host capability tier. T4 (smart toaster, log-only) gets no avatar. T3 (Pi 5, text-only) cannot afford VRM. But T3 *can* afford a small emoji-affect substitute. This is the **text avatar**.

**Proposed invention.** **Glyphic embodiment** — a small Munnr surface that renders affect state as a sequence of glyphs (Unicode emoji, sparingly chosen). When affect is calm: `( - _ - )`. When delighted: `( ^ _ ^ )`. When listening: `( o _ o )`. When tired: `( ~ _ ~ )`. The vocabulary is fixed (≤24 glyphs), the mapping is declarative (`config/glyphs.yaml`), and the surface is read-only — operators cannot prompt-inject the avatar. This is *not* a chatbot face emoji at the start of every reply; it is a *one-line header* that Munnr renders once per turn, visually distinct from message content. See `[[6B_LOW_POWER_EMBODIMENT]]` for the full tier table.

Cite-shape: `src/ember/spark/munnr/glyphic.py`, method `render_glyph(affect_snapshot) -> str`. ~50 LOC. Pi-runnable. No deps.

Vows touched: **Tiered Presence**, **Smallness**, **Embodied Honesty** (the glyph must reflect real affect, not theatre).

---

## 3. Semantic IM Fallback Routing

**SAP's pattern.** SAP ships 8 IM bot managers (`qq_bot_manager.py`, `wechat_bot_manager.py`, `telegram_bot_manager.py`, `discord_bot_manager.py`, `slack_bot_manager.py`, `feishu_bot_manager.py`, `dingtalk_bot_manager.py`, `wecom_bot_manager.py`). Each is a separate class with its own connection lifecycle, message format, and failure model. When one platform goes down, the operator simply does not receive messages on that platform. There is no fallback routing.

**Why SAP did not need this.** SAP's reach model is *multi-platform parallel*, not *multi-platform substitutable*. Each platform's audience is treated as distinct. If Telegram goes down, the Telegram audience is unreachable until Telegram comes back. This is correct for marketing-shaped reach.

**Why Ember needs it.** Ember's reach is *relational*, not audience-shaped. An operator who talks to Ember on Telegram during the day and Discord at night is the *same person*. If Telegram is down, the operator should be able to talk to Ember on Discord, and Ember should still know who they are. This is *graceful degradation across the reach surface*.

**Proposed invention.** **Persona-keyed fallback routing** — when an IM platform's connection fails, Munnr looks up the operator's last-seen identities on adjacent platforms (via a tailnet-resident mapping table in Brunnr) and emits a *graceful-redirect message* on those platforms: *"Telegram is down; if this is Volmarr, I am here on Discord too."* The redirect message is signed (so a spoofer cannot impersonate Ember), and the operator's response on the fallback platform is authenticated against the persona table before Ember treats it as the same conversation. The whole flow is operator-opt-in and revocable.

Cite-shape: `src/ember/spark/munnr/im_fallback.py`. The persona table lives in Brunnr as `persona_identity` rows: `(persona_id, platform, platform_user_id, trust_signature, last_seen_at)`. The redirect ceremony is gated by ADR (see `[[68_DECISION_RECORDS]]`).

Vows touched: **Graceful Offline**, **Surface Without Surveillance** (the persona table is operator-managed, not auto-built from scraping), **Honest Memory** (every cross-platform identification is audit-logged).

---

## 4. Party-Leader Migration

**SAP's pattern.** SAP has no concept of a *party leader*. Each running SAP instance is sovereign. There is no protocol for handing authority between instances. If the laptop running SAP closes its lid, the IM bots running on the laptop go silent until the laptop wakes up.

**Why SAP did not need this.** Single-host design. The laptop *is* the SAP instance; if it sleeps, SAP sleeps.

**Why Ember needs it.** Cartographer's `[[62_PARTY_PROTOCOL]]` establishes that multiple Ember instances can be present on a tailnet. One of them is the *leader* for any given IM platform or livestream (only one can hold a Discord bot token usefully). When the leader laptop closes its lid, the leadership should *migrate* to a still-awake peer — not crash, not stall, not double-post when the laptop wakes. This is the **lid-close handover**.

**Proposed invention.** **Lid-close-aware party leadership** — every Ember instance reports a *liveness pulse* to the tailnet (UDP heartbeat, 5 s interval) plus a *graceful-shutdown intent* signal (sent on `systemd suspend.target`, on macOS lid-close notification, on Pi `shutdown -h`). When the leader announces intent to suspend, the next-priority peer (per a fixed priority order in `~/.ember/config/party.yaml`) accepts the transfer, takes over the IM tokens and livestream credentials *with a small mute window* (≤2 s) to prevent overlap, and announces takeover on the connected channels (silently in audit log; not as a chat message to the operator). When the original leader wakes, it sees the takeover in the audit log and *does not reclaim* without operator command. The peer that took over is now the leader until *its* lid closes.

Cite-shape: `src/ember/spark/funi/party_leader.py`, key methods `announce_intent(reason)`, `accept_transfer(from_host)`, `reclaim(operator_command)`. ~250 LOC. Depends on Hermes-style typed exhaustion for the credential transfer (per Hermes ADR-Proposed-Strengr-001).

Vows touched: **Federated Self**, **Graceful Offline**, **Modular Authorship** (leader crash does not kill peers; peers can run leaderless).

---

## 5. Telemetric Affect Surface

**SAP's pattern.** SAP's affect state is *internal*. It mutates via regex-parsed tags in LLM output (`affection_system.py:44`: `re.search(r"<user=([^\s>]+)\s+(.+?)>", full_content)`). The operator does not see the state; they see only its effects (avatar expressions, autobehavior triggers). The state is *opaque* by default.

**Why SAP did not need this.** SAP's affect is a game mechanic. Like a gacha game's friendship bar, the *surprise* of the state mutation is part of the experience. Exposing the internals would break the spell.

**Why Ember needs it.** Vow of **Embodied Honesty** (proposed) forbids the spell. Vow of **Honest Memory** forbids opaque state. The operator must be able to look at Ember's affect and ask *"what do you think of me right now and why?"* — and Ember must answer with state, not theatre. The affect surface should be a **piece of telemetry**, not a hidden parameter.

**Proposed invention.** **Hugarsýn-mode affect introspection** — Cartographer's `[[65_META_AWARENESS]]` proposes Hugarsýn (mind-sight) as the introspection surface. This invention extends it: affect becomes a *first-class subject* of Hugarsýn. The operator runs `ember introspect affect` and gets a structured printout: each axis, current value, last-mutation event, last-mutation source (which conversation turn produced the change), confidence band, and decay trajectory. The printout includes a `why` field per axis that describes the *reason* Ember moved on that axis (e.g., `axis=warmth, value=+0.12 since 2026-05-23T14:30Z, last_mutation=session 0142 turn 3, reason="operator shared a private hardship and I responded; warmth raised; decayed slightly overnight"`). The operator can also *write* to the surface: `ember introspect affect set warmth=0.0 reason="resetting after a frustrating week"`.

Cite-shape: extends `src/ember/spark/hjarta/affect.py` with `class AffectIntrospection`. New CLI: `ember introspect affect`. The `why` field is *not* generated post-hoc; it is captured at mutation time and stored alongside the value.

Vows touched: **Embodied Honesty**, **Honest Memory**, **Public-Friendliness** (the surface is a plain CLI, not an admin panel).

---

## 6. Consent-Token Avatar Gating

**SAP's pattern.** SAP's avatar can express anything the model decides to express, gated by no explicit consent surface. The VTube Studio control (`vts_manager.py`) can drive expressions like `kiss`, `wink`, `surprised`, `crying`, `angry` based on model output. There is no permission layer. If the model decides to make the avatar wink at someone, the avatar winks.

**Why SAP did not need this.** SAP is a *companion* product. The operator implicitly consents to all expressive surfaces by installing it. Granular consent would feel paternalistic to the target audience.

**Why Ember needs it.** Vow of **Surface Without Surveillance** (proposed) requires that every reach surface — including outward avatar expressions — carry explicit, revocable scope. Vow of **Embodied Honesty** requires that the avatar express *real* state, not theatre, and that means the operator must be able to *constrain* the expressive palette. An operator running Ember at work does not want the avatar to display a `kiss` expression even if the model thinks it would be charming.

**Proposed invention.** **Consent-token expression gating** — every avatar expression is associated with a *consent token* in `~/.ember/config/expression_tokens.yaml`. The operator declares which tokens are granted in which contexts: `at_work: [smile, wink_no, listen, nod, shake_head]`, `at_home: [smile, wink, blow_kiss, surprised, sad, listen, nod]`, `streaming: [smile, surprised, neutral, listen]`. The avatar may only emit expressions whose tokens are granted in the current context. Context is operator-declared at session start (or inferred from a context-pick screen). Revocation is mid-session — `ember context set work` changes the gating instantly. The model can request an ungranted expression, but Munnr substitutes the nearest granted neighbour (with a log entry) rather than emitting the request.

Cite-shape: `src/ember/spark/munnr/expression_gate.py`. The token table is config; the gate is a small filter; the substitution is declarative. ~150 LOC.

Vows touched: **Surface Without Surveillance**, **Embodied Honesty**, **Affective Restraint** (proposed), **Public-Friendliness** (operators can read the YAML without instruction).

---

## 7. Stream-Truncation Confession

**SAP's pattern.** SAP's livestream pipeline (`live_router.py:1-546`, `blivedm/`, `ytdm.py`, `twitch_service.py`) ingests comments → routes via topic logic → produces avatar response. When the response is too long for the latency budget, it is *truncated* — the avatar simply stops speaking. The viewer does not know whether the model meant to stop, ran out of time, or hit an error.

**Why SAP did not need this.** Livestream viewers expect occasional silence. Truncation feels like the model "thinking" or "moving on."

**Why Ember needs it.** Vow of **Embodied Honesty** forbids the silent truncation. If Ember had more to say and was cut by a latency budget, the viewer (or the operator behind a private livestream) deserves to know.

**Proposed invention.** **Confessing truncation** — when the livestream avatar's response is truncated by latency, Ember emits a *single-glyph confession* in the next idle moment: a small `…(more)` overlay tag, plus a log line in Hugarsýn introspection that captures what was cut. The full response is preserved in the session log. If the operator (or a viewer with appropriate permissions, via consent token) asks "what were you going to say?", Ember can reply with the truncated tail.

Cite-shape: `src/ember/spark/munnr/livestream/truncation_confession.py`. Hook point: the livestream renderer's truncation event. ~80 LOC.

Vows touched: **Embodied Honesty**, **Honest Memory**, **Graceful Offline** (the truncation is itself a graceful-failure event with a typed-value return shape).

---

## 8. Tethered Affect Anchoring

**SAP's pattern.** SAP's affect state is *entirely self-contained*. The `affection_data.json` file does not reference the conversations that produced the state. If the operator asks "why do you like me?", SAP has no grounded answer — it can only confabulate from current state value.

**Why SAP did not need this.** SAP's affect is a number for a UI. The *why* is not a feature.

**Why Ember needs it.** Vow of **Tethered Grounding** says the Well is canonical. Affect mutations must *anchor* to Well-resident evidence. The operator must be able to ask "show me the three conversation turns most responsible for your current warmth value" and get an *actual citation* into the Well.

**Proposed invention.** **Affect anchoring** — every affect mutation is stored not as a scalar delta but as a tuple `(axis, delta, anchor_chunk_ids, decay_curve)`. `anchor_chunk_ids` is a list of Brunnr chunk IDs from the conversation turn(s) that produced the mutation. When Ember introspects affect (`[[#5 Telemetric Affect Surface]]`), the `why` field can hyperlink to those chunks. When the anchor chunks are deleted from the Well (operator privacy command), the mutation decays to zero on next reconciliation. **Affect cannot survive its own evidence.**

Cite-shape: extends the affect storage schema. The reconciler runs on every Well change event (Brunnr publishes an `episode_deleted` event). ~120 LOC plus schema migration.

Vows touched: **Tethered Grounding**, **Honest Memory**, **Affective Restraint**, and a privacy-preservation property that is itself worth naming: **Affect Survivable Only With Evidence**.

---

## 9. Per-Tier Voice Substitution

**SAP's pattern.** SAP's voice stack (`moss_tts.py:1-267`, `sherpa_asr.py`) provides TTS and ASR but assumes a workstation-shaped render budget. Pi-class hardware cannot run MOSS TTS quality. The fallback is *no voice*.

**Why SAP did not need this.** SAP's voice expectation is a deluxe one. Cheap voice was not a target.

**Why Ember needs it.** Vow of **Tiered Presence** requires expressive degradation, not silence. At T2 (phone), MOSS-quality TTS is impossible; espeak-ng or piper-tts is. At T3 (Pi), even piper may be too heavy; a *cued voice clip library* (pre-rendered short phrases) is. At T4 (toaster), text is the only voice.

**Proposed invention.** **Voice-tier substitution chain** — each utterance is annotated with a *minimum tier* requirement, and Munnr selects the appropriate voice engine. The chain is declarative: `[moss_tts, piper_tts, espeak_ng, cued_library, text_only]`. The cued library is a small operator-curated set of pre-rendered MP3s for common Ember phrases ("good morning, Volmarr", "I am thinking", "I am here") — generated on the workstation tier when the operator first sets up the Pi tier. Substitution is *transparent* to the prompt layer: the model produces text; Munnr's voice selector decides how to speak it.

Cite-shape: `src/ember/spark/munnr/voice/chain.py`. The chain is config; each engine implements a small Protocol. The cued library is a directory of MP3s with a manifest. ~200 LOC plus the manifest format.

Vows touched: **Tiered Presence**, **Smallness**, **Graceful Offline** (network TTS is one engine among several; absence is recoverable), **Public-Friendliness** (operators can record their own cued lines if desired).

---

## 10. Affect-Aware Interrupt Cooldown

**SAP's pattern.** SAP's behavior engine (`behavior_engine.py:144-222`) fires triggers regardless of recent operator activity. If the operator just told SAP to stop talking, the next "cycle" trigger will still fire on schedule. The engine is *deaf to affect signal*.

**Why SAP did not need this.** SAP's autonomous behavior is designed to be persistent — the companion product wants to feel "alive." Cooldown after operator irritation would feel like the companion was sulking.

**Why Ember needs it.** Vow of **Affective Restraint** (proposed) requires that affect bias behavior. When the operator has signalled frustration or distance, autonomous triggers should *back off* — not stop, not sulk, but apply a cooldown gate.

**Proposed invention.** **Affect-gated autonomous triggers** — every autonomous trigger (cycle, time-based, no-input) checks the current affect axis `operator_receptivity` before firing. If receptivity is below a threshold, the trigger is *deferred* (not skipped) to a later time when receptivity may have recovered. The deferral is logged. The operator can see, via Hugarsýn introspection, that a trigger was deferred and why.

Cite-shape: extends `src/ember/spark/hjarta/scheduler.py` (the Ember equivalent of SAP's `behavior_engine.py`). The check is a single conditional: `if receptivity < config.autonomous.receptivity_floor: defer`. ~30 LOC for the gate itself; the receptivity axis already exists per `[[#5]]` and `[[64_AFFECTION_ENGINE_REIMAGINED]]`.

Vows touched: **Affective Restraint**, **Honest Memory** (deferral is logged, not silent), **Public-Friendliness** (the floor is operator-configurable).

---

## 11. Avatar-as-Backpressure Indicator

**SAP's pattern.** SAP's avatar expresses what the model wants it to express. The avatar's expressions are *content-driven*, not *system-state-driven*. If the LLM provider is rate-limited and SAP is on its third retry, the avatar shows whatever expression the last reply demanded.

**Why SAP did not need this.** SAP treats the avatar as a *character*, not a *dashboard*.

**Why Ember needs it.** Vow of **Embodied Honesty** says the avatar reflects internal state. When Strengr is in a rate-limit backoff loop, the avatar should *show* it — not hide it. The operator deserves to see when Ember is genuinely working versus genuinely thinking versus genuinely waiting on something they cannot fix.

**Proposed invention.** **Avatar-as-state-indicator** — a small visual layer beneath the affect-driven expression: a *spinner glyph* when Strengr is mid-call, a *clock glyph* when in retry backoff with a typed-exhaustion `until` value, a *broken-link glyph* when the provider is in `Disconnected` state. These overlay on the affect expression rather than replacing it. The glyphs are config-driven and small enough to render at T3 (text) and T4 (log).

Cite-shape: `src/ember/spark/munnr/avatar/backpressure_overlay.py`. The overlay reads from Strengr's state channel via internal API. ~100 LOC.

Vows touched: **Embodied Honesty**, **Graceful Offline** (the backpressure indicator *is* the graceful-offline surface), **Honest Memory**.

---

## 12. Recursive-Trust Audit Trail

**SAP's pattern.** SAP's MCP integration (`mcp_clients.py:1-189`) allows a connected MCP server to call SAP's tools. There is no chain-of-trust audit for nested calls: if MCP-server-A calls SAP-tool-B which calls MCP-server-C, the audit log records each step but not the originating *trust chain*.

**Why SAP did not need this.** SAP's threat model treats MCP servers as trusted. The audit log is for the operator's curiosity, not their safety.

**Why Ember needs it.** Vow of **Surface Without Surveillance** (proposed) plus Hermes-derived audit discipline (per `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]`) require that every cross-trust-boundary call leave a trail. Nested calls need *recursive* trust accounting.

**Proposed invention.** **Trust-chain decorated audit records** — every tool call carries an immutable `trust_chain: list[str]` field in its audit record: e.g. `[operator, mcp:filesystem, ember.search_well, mcp:fetch]`. When a call originates from an MCP peer, its trust_chain starts with that peer's client_id. When a call originates from a *call from a call from an MCP peer*, the chain shows the full descent. The operator can grep audit logs for `trust_chain:contains:mcp:foo` to find every call ultimately attributable to peer `foo`. Calls whose chain length exceeds a configurable maximum are *refused* at the executor level (default max: 4).

Cite-shape: extends `src/ember/spark/funi/tools/audit.py` per ADR 0011. The chain is a frozen list propagated through the dispatcher's context. ~60 LOC of plumbing plus a chain-depth check.

Vows touched: **Honest Memory**, **Surface Without Surveillance**, **Modular Authorship** (the chain depth limit means a broken peer cannot recursively exhaust the executor).

---

## 13. Quiet-Hours Reach Throttling

**SAP's pattern.** SAP's IM bots respond to incoming messages 24/7. There is no operator-configurable *quiet hours* — if a Discord ping arrives at 03:00, SAP replies. The scheduler can fire outgoing messages at any hour (`scheduler.py:32-61`).

**Why SAP did not need this.** SAP's persistent-companion product wants to *be available*.

**Why Ember needs it.** Vow of **Surface Without Surveillance** (proposed) implies that reach is opt-in by *time* as well as by *scope*. An operator on a quiet evening should be able to declare "Ember sleeps from 22:00 to 07:00" — meaning Ember does not respond on any platform during those hours (or, configurably, responds only with a *small note* directing the sender to wait until morning).

**Proposed invention.** **Per-platform quiet-hours rules** — `~/.ember/config/quiet_hours.yaml` defines per-platform schedules: `discord: { 22:00-07:00: "soft", 02:00-06:00: "hard" }`. Soft = automated polite-note reply. Hard = no response at all (the bot remains connected but ignores messages). The operator can override per-conversation: a flag in the conversation metadata can say "this conversation is always loud."

Cite-shape: `src/ember/spark/munnr/im/quiet_hours.py`. Each IM bot consults the gate before responding. ~80 LOC plus the config format.

Vows touched: **Surface Without Surveillance**, **Tiered Presence**, **Affective Restraint** (the operator's evening is theirs).

---

## 14. Receipt-Bound Provisional Memory

**SAP's pattern.** SAP's memory writes are immediate and unconditional. The model says something interesting; the affection_data or behaviorSettings is mutated; no receipt mechanism gates the write.

**Why SAP did not need this.** Memory writes are local. Mistakes are recoverable by file edit. Fast-and-loose wins over careful here.

**Why Ember needs it.** Hermes's `[[hermes:Honest Memory]]` Vow and Ember's existing Episode discipline make memory a *contract*. When a mutation is proposed by an inference (e.g. "the operator hates morning meetings, increase irritation axis on weekday mornings"), the mutation should be *provisional* until the operator has had a chance to see it. Otherwise Ember's memory drifts into the model's hallucinations.

**Proposed invention.** **Receipt-bound provisional memory** — every model-proposed memory mutation enters a *pending tray* in Hjarta. The mutation is *not yet applied* to live state. The operator sees the pending tray on next interaction (or via `ember memory pending`). They can confirm (mutation applies), reject (mutation discarded), or amend (mutation rewritten before applying). Mutations not addressed within N days (config-driven default: 7) expire silently.

Cite-shape: `src/ember/spark/hjarta/provisional_memory.py`. The tray is a small JSONL file or Brunnr table; the apply/reject CLI is straightforward. ~150 LOC.

Vows touched: **Honest Memory**, **Tethered Grounding**, **Public-Friendliness** (the operator sees and curates what Ember remembers about them).

---

## 15. Cross-Codex Pollination Hooks

**SAP's pattern.** SAP is a single codebase. There is no concept of cross-corpus design influence.

**Why SAP did not need this.** SAP is not a corpus; it is a product.

**Why Ember needs it.** Ember has, at this moment, **three sibling codexes** (Hermes Wave 1, Peer Wave 2, this SAP Wave 3) plus the Yggdrasil and Stofa design trees. Insights migrate between corpora informally; the migration is unaudited and silently lossy.

**Proposed invention.** **Codex pollination hooks** — a meta-pattern, not a code module. Each codex doc that proposes a True Name, a Vow, or an ADR includes a `pollinates:` frontmatter field naming *target docs in sibling codexes* where the proposal should be considered for transplant. The Scribe's final pass collects these and produces a `meta/POLLINATION_MAP.md` per codex showing the bidirectional fertilization. Over time, this becomes the *cross-codex memory* — the explicit record of which ideas crossed from which corpus into which.

Cite-shape: a frontmatter convention, not code. Implementation is the Scribe's discipline at final-pass time. The map itself is a small Markdown file with hyperlinks.

Vows touched: **Open Knowledge**, **Honest Memory** (the corpora know what they have borrowed).

---

## 16. Failsafe Default-Quiet Mode

**SAP's pattern.** SAP defaults to *enabled* on most surfaces. The IM bots, the avatar, the autonomous behavior — all default to "on" when settings_template.json is loaded. The operator must explicitly turn things off.

**Why SAP did not need this.** SAP is a product with a feature-rich first-launch experience. "On by default" is what the product manager wants.

**Why Ember needs it.** Vow of **Smallness** plus Vow of **Surface Without Surveillance** require **opt-in, not opt-out**. Every reach surface should default *off*. The first-launch wizard (Hjarta's existing wizard) is the only place where surfaces get turned on, and only with explicit operator consent. This is the inversion of SAP's default.

**Proposed invention.** **Failsafe default-quiet mode** — `ember chat` on a fresh install gives the operator *zero outward reach surfaces*. No IM bots running. No livestream connections. No autonomous triggers. No tool-call approval policies above `PER_CALL`. The operator must walk a *reach wizard* (extension to Hjarta's existing wizard) that enumerates each surface and asks explicit consent before enabling. The default-quiet state is also recoverable: `ember reach reset` returns all surfaces to off.

Cite-shape: extends `src/ember/spark/hjarta/machine.py` with a `ReachWizard` state set. The defaults flip in `config/ember.example.yaml`. Test added: `test_default_quiet.py` verifies no outward reach exists on first launch.

Vows touched: **Surface Without Surveillance**, **Smallness**, **Public-Friendliness** (the operator sees every surface they are enabling).

---

## 17. Composition-Over-Theatrics Avatar Library

**SAP's pattern.** SAP's avatar library leans heavily on emotional theatrics. The VRM models support expressions like `cry`, `angry`, `surprised`, `wink`, `kiss`, plus a long tail of model-specific blendshapes. The expressive vocabulary is *emotionally maximalist*.

**Why SAP did not need this.** SAP's audience expects an anime-style emotive companion.

**Why Ember needs it.** Vow of **Embodied Honesty** plus the Cyber-Viking aesthetic (per `[[ember:PHILOSOPHY]]`) prefer *composed dignity* over emotional theatrics. Ember's avatar should be capable of *intensity* (the saga-style stoicism that contains a great deal) without *maximalist display* (the gacha-style cry-face that performs a tiny amount).

**Proposed invention.** **Composition-first avatar vocabulary** — a curated avatar expression library that *prefers* small variations on a composed base. The default expression is *open, attentive, slightly amused*. Variations: *focused*, *listening intently*, *quietly pleased*, *thoughtfully troubled*, *amused*, *clear-eyed concern*. The maximalist expressions (cry, kiss, fury, terror) are *available* but *gated* (per `[[#6 Consent-Token Avatar Gating]]`) and *rare* by default. This is not censorship; it is *aesthetic discipline*. The vocabulary lives in `vrm/ember_expression_library.yaml`.

Cite-shape: a curated YAML + a default-mapping table in `src/ember/spark/munnr/avatar/composition.py`. The library can be replaced by the operator; this is the recommended default.

Vows touched: **Embodied Honesty**, **Public-Friendliness**, and an aesthetic Vow not yet ratified but worth naming: **Saga-Stoic Restraint**.

---

## 18. Operator-Authored Skill Provenance

**SAP's pattern.** SAP's Agent Skills (`skills.py`) and Extensions (`extensions.py`) are mostly developer-authored. There is no first-class concept of *operator-authored* skills with provenance tracking.

**Why SAP did not need this.** SAP's skill audience is the SAP developer + the SAP power-user. The "operator authoring a skill mid-conversation" pattern was not the target.

**Why Ember needs it.** Hermes's `[[hermes:Skill-002]]` ADR proposes agent-initiated skill writes with audit. The next invention beyond that is *operator-initiated* skill writes, with a richer provenance story.

**Proposed invention.** **Operator-Authored Skill with Provenance** — when an operator runs `ember skill create <name>`, the skill is written with mandatory frontmatter `author: operator(<persona_id>)` and `provenance: session/<id>` *and* a `verified_against:` list capturing the conversation turns that prompted the skill creation. Later, the operator can ask `ember skill provenance <name>` and see the conversation history that motivated the skill. This makes skill libraries *narratively grounded* rather than abstract.

Cite-shape: extends Hermes's proposed skill subsystem with provenance plumbing. ~80 LOC.

Vows touched: **Honest Memory**, **Tethered Grounding**, **Public-Friendliness**.

---

## 19. Defended System Prompt Honors Multi-Origin

**SAP's pattern.** SAP's system prompt is built via string concatenation across many sources (`get_setting.py`, character cards, `behaviorSettings` content). There is no typed instruction surface and no per-origin trust accounting.

**Why SAP did not need this.** Single-origin trust. The operator and the developer are the same trust class.

**Why Ember needs it.** Hermes proposed **Defended System Prompt** as a Vow (typed instruction entry). The next step beyond *typed* is *multi-origin* — when a system prompt block originates from an MCP peer, from a character card, from an operator config, or from a developer default, each origin's trust class is accounted for, and the block's effective weight is gated accordingly.

**Proposed invention.** **Multi-origin system prompt assembly** — system prompt blocks carry an `origin` tag (operator, developer, mcp_peer:foo, character_card:bar) plus a `trust_class` (high, medium, low). The assembler concatenates blocks in trust order (operator > developer > character_card > mcp_peer) and applies *content gates* per trust class (e.g., low-trust blocks cannot contain instructions matching the `IGNORE PREVIOUS` pattern; medium-trust blocks have a length cap). The full assembled prompt is logged with the origin annotations for any operator who runs `ember introspect prompt`.

Cite-shape: extends `src/ember/spark/funi/prompt_assembly.py` (per Hermes ADR-Proposed). The origin tagging is mechanical; the trust class is config. ~140 LOC.

Vows touched: **Defended System Prompt**, **Honest Memory**, **Surface Without Surveillance**.

---

## 20. Two-Hand-Holding Operator Audit Ceremony

**SAP's pattern.** SAP has no consent ceremony around destructive operations. Computer-control actions, file writes, smart-home device commands fire as the model decides. There may be log entries, but there is no *ceremony*.

**Why SAP did not need this.** Friction is the enemy of the companion experience.

**Why Ember needs it.** Hermes's audit + ADR 0011's tool approval framework establish a per-call approval surface. The next step is a *ceremony* for destructive operations — a small, deliberate moment that says "this is something serious; both hands on it."

**Proposed invention.** **Two-hand-holding ceremony** — destructive operations (file deletion, system commands, irreversible smart-home actions, send-to-public-IM) require *two confirmations* across a short time delay (default: 3 seconds). The first confirmation arms; the second commits. During the delay window, the Hugarsýn surface shows the full proposed action including any chained tool calls that depend on it. The operator can cancel by simply not confirming the second time. This is *not* a CAPTCHA; it is a *moment of pause*.

Cite-shape: extends the tool approval framework with a `ceremony: two_hand` annotation on destructive tool descriptors. The CLI prompts twice. ~70 LOC plus tool-descriptor annotations.

Vows touched: **Honest Memory**, **Public-Friendliness** (the ceremony is visible, not hidden), and a sub-Vow worth naming: **Friction Where Friction Helps**.

---

## What This Means for Ember

This whole document is **Invent**. None of the patterns above exist in SAP. All of them become visible because Ember's Vows draw shapes SAP's product goals did not draw. Each invention is a *territory mark*, not a slice-plan item. The Cartographer's `[[60_TRUE_NAME_REASSIGNMENT]]`, `[[61_NEW_VOWS]]`, `[[62_PARTY_PROTOCOL]]`, `[[63_PERFORMANCE_TIER_ENGINE]]`, `[[64_AFFECTION_ENGINE_REIMAGINED]]`, and `[[65_META_AWARENESS]]` are the *major* inventions of Wave 3; this doc catalogues the *minor and adjacent* inventions that round out the surface.

**Adopt:** (none — this doc is all Invent by design)

**Adapt:** (none — this doc is all Invent by design)

**Avoid:** Every SAP pattern this doc names — silent affect, hidden truncation, opt-out-default reach, single-host affect storage, theatrically-maximalist avatar, untyped multi-origin prompts. Each pattern's avoidance is implicit in the corresponding invention.

**Invent (this is the whole doc):**

1. **Cross-Host Affect Routing** — affect as CRDT across reachable Ember instances; ties to `[[6A_MULTI_AGENT_PARTY]]`.
2. **Glyphic Embodiment** — text-and-emoji avatar for T3 hosts; ties to `[[6B_LOW_POWER_EMBODIMENT]]`.
3. **Semantic IM Fallback Routing** — persona-keyed cross-platform graceful redirect; ties to `[[hermes:Graceful Offline]]`.
4. **Party-Leader Migration** — lid-close handover of IM token authority; ties to `[[62_PARTY_PROTOCOL]]` and `[[6A_MULTI_AGENT_PARTY]]`.
5. **Telemetric Affect Surface** — `ember introspect affect` reveals state with `why` field; ties to `[[65_META_AWARENESS]]`.
6. **Consent-Token Avatar Gating** — expression palette gated by operator-declared context.
7. **Stream-Truncation Confession** — livestream truncation announced rather than silent.
8. **Tethered Affect Anchoring** — affect mutations cite the Well chunks that produced them; affect cannot survive its own evidence.
9. **Per-Tier Voice Substitution** — voice engine chain by host capability; ties to `[[6B_LOW_POWER_EMBODIMENT]]`.
10. **Affect-Aware Interrupt Cooldown** — autonomous triggers gated by operator receptivity; ties to `[[64_AFFECTION_ENGINE_REIMAGINED]]`.
11. **Avatar-as-Backpressure Indicator** — system state visible in the avatar overlay.
12. **Recursive-Trust Audit Trail** — trust_chain field on every tool call audit record.
13. **Quiet-Hours Reach Throttling** — per-platform per-time-window reach gates.
14. **Receipt-Bound Provisional Memory** — model-proposed memory mutations land in a pending tray for operator confirmation.
15. **Cross-Codex Pollination Hooks** — frontmatter convention recording bidirectional fertilization across corpora.
16. **Failsafe Default-Quiet Mode** — opt-in reach surfaces on first launch.
17. **Composition-First Avatar Vocabulary** — saga-stoic restraint over gacha maximalism.
18. **Operator-Authored Skill Provenance** — operator-written skills carry conversation provenance.
19. **Defended System Prompt Honors Multi-Origin** — per-origin trust accounting in prompt assembly.
20. **Two-Hand-Holding Operator Audit Ceremony** — short delay before destructive commits.

**Cross-references:**

- `[[60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's True Name reassignments anchor several of these inventions.
- `[[61_NEW_VOWS]]` — the proposed Vows that these inventions instantiate.
- `[[62_PARTY_PROTOCOL]]` — Cartographer's protocol that #1 and #4 extend.
- `[[63_PERFORMANCE_TIER_ENGINE]]` — Cartographer's tier engine that #2, #9, and the entire `[[6B_LOW_POWER_EMBODIMENT]]` extend.
- `[[64_AFFECTION_ENGINE_REIMAGINED]]` — Cartographer's affect engine that #5, #8, and #10 extend.
- `[[65_META_AWARENESS]]` — Cartographer's Hugarsýn that #5, #7, #11, #19 extend.
- `[[67_SLICE_PLAN_REVISIONS]]` — where the most-ready inventions become slice-3 candidates.
- `[[68_DECISION_RECORDS]]` — ADR-Proposed records for the inventions that mature into decisions.
- `[[69_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[6A_MULTI_AGENT_PARTY]]` — #1, #4 are foundational to multi-Ember party protocol.
- `[[6B_LOW_POWER_EMBODIMENT]]` — #2, #9 are foundational to the low-power tier story.
- `[[6C_EMBER_WAVE_3_SLICE]]` — the slice-3 proposal that incorporates the most-ready inventions.
- `[[hermes:Skill-002]]` — Hermes-side foundation that #18 extends.
- `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]` — Hermes-side audit discipline that #12 extends.
- `[[peer:LETTA-2_SLEEPER]]` — Peer Codex sleeper-memory pattern adjacent to #14.
- `[[ember:PHILOSOPHY]]` — the Cyber-Viking aesthetic that grounds #17.
- `[[ember:RULES.AI]]` — the iron laws that all inventions must honor.

**True Names affected:** Hjarta (most — #1, #5, #8, #10, #14), Munnr (#2, #3, #6, #7, #9, #11, #13, #17, #20), Funi (#4, #12, #15, #19), Brunnr (#1, #8 anchor storage), Strengr (#11 backpressure surface). Smiðja unchanged in this batch.

**Most consequential single invention:** **#8 Tethered Affect Anchoring**. It is the one that, once shipped, makes Ember's affect *truthful* rather than *fictional*. Everything else can be ratified piecemeal; #8 is the keystone.

**Most-ready-for-slice-3:** #2 (Glyphic Embodiment), #5 (Telemetric Affect Surface), #16 (Failsafe Default-Quiet Mode). All three are small, low-risk, high-clarity additions that align with the existing Hermes-derived slice-3 shape proposed in `[[67_SLICE_PLAN_REVISIONS]]`.

The inventions stand as written. The slice plan does not change here. The Cartographer's docs and the Scribe's `[[67_SLICE_PLAN_REVISIONS]]` propose which of these to mature first.
