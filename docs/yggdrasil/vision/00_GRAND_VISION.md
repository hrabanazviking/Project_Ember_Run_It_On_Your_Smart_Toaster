# 00 — Grand Vision

> *I know an ash that stands, called Yggdrasil — a tall tree
> sprinkled with bright dew. From there come the showers that
> fall in the dales; ever green it stands over Urð's well.*
> — Völuspá, st. 19

## The pitch in one sentence

**Ember + ten sibling projects, woven into a single self-healing
sovereign AI organism that reaches from a Raspberry Pi 5 to a
desktop cluster, with composite memory, real-time self-awareness,
emotional intelligence, generative voice, ambient temporal rhythm,
encrypted secrets, and stealth web access — all running on the
operator's own hardware, all the time.**

That's Yggdrasil.

---

## What changes

Today, Ember is a small AI agent: chat REPL, retrieval-grounded
replies, three first-party tools, MCP for plugins, audit log,
Episodes persisted to a Well. Small, tethered, runs on a toaster.

After Yggdrasil ships (across 5 phases, per
[`../roadmap/90_PHASE_OVERVIEW.md`](../roadmap/90_PHASE_OVERVIEW.md)),
Ember will additionally:

- **Compose memory across three backends** simultaneously
  (structured / semantic / associative) via **Bifrǫst Bridge**.
- **Have human-shaped memory decay** — Ebbinghaus curves on every
  Episode via **Mímir's Well**; reinforcement on revisit;
  contradiction detection.
- **Subscribe to a real-time event bus** of her own operations
  via **Verðandi**, gaining what is functionally *self-awareness*:
  she knows what she just did, what's happening now, and what
  pattern that fits.
- **Read tone, mood, and emotional context** in operator input
  AND her own recent replies — modulating her register accordingly
  (see [`../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md`](../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md)).
- **Generate poetry, mottoes, and creative response moods** via
  **Seiðr** — not as gimmick, but as a *mood-modulation channel*
  the chat tone can borrow from.
- **Hold secrets in an encrypted chest** via **Kista** — no
  plaintext passwords in `ember.yaml`; all sensitive values flow
  through a Fernet-protected vault.
- **Reach the web through a cloaked walker** when needed — when
  `fetch_url` hits anti-bot defenses, Ember delegates to
  **CloakBrowser** as an MCP tool.
- **Know what time it is, in every sense** — Astrology Engine
  provides ephemeris-grade temporal awareness: time-of-day, lunar
  phase, season, which subtly shifts Ember's voice (a soft night
  register vs. a bright morning register).
- **Federate across multiple devices** — a Pi 5 in the closet, a
  desktop in the office, a laptop on the road can all run Ember
  simultaneously, sharing identity, Well, and Episode history.
- **Self-heal on failure** — gossip protocol detects when a realm
  goes down; per-failure playbooks restore service; the Norns'
  triple-snapshot system (past/present/future state captured
  continuously) means rollback is always possible.

And critically: **all of this still runs on the lowest-end
hardware the operator owns**. Yggdrasil is *not* a "you need 64GB
RAM" project. It's an *adaptive* project — the operator's device
capability gets detected at startup, and realms load lazily based
on what's worth running.

---

## Why now

Three reasons.

### 1. The siblings exist

Eleven Norse-themed AI infrastructure projects have appeared in
the monorepo over the last few days. Each one is real, each one
works, each one solves a real problem. The cost of *not*
integrating them is to leave that engineering on the floor.

### 2. Ember has the right bones

Ember's architecture (Three Realms / Six True Names / typed-value-
over-exception contract / Vows / handle protocols) was designed
specifically to be *composable*. Brunnr is a Protocol; you can
plug pgvector in tomorrow. Funi is a Protocol; you can plug
llama.cpp in tomorrow. Bifrǫst, Mímir's Well, Verðandi, Kista,
Hamr, etc. are each the same shape — adapter behind a Protocol,
lazy import, opt-in via config.

The integration is *additive*, not invasive. The Six True Names
don't change; we just give them more friends.

### 3. The operator (Volmarr) is already building this constellation

The eleven sibling projects didn't appear from nowhere. They were
built — sometimes elsewhere, sometimes by the same hands that
built Ember — because someone wanted them to exist. The next
honest step is to make them *talk to each other*.

---

## What stays the same

Critically, this plan does **NOT**:

- Break any current Ember code path.
- Force operators to opt in to anything they don't want.
- Add cloud dependencies, sign-ins, or telemetry.
- Replace the existing handles (Funi, Brunnr, MCP) — only adds
  beside them.
- Require a "Yggdrasil mode" — every realm is independently opt-
  in via `ember.yaml`.
- Change the Vows (Smallness, Sovereignty, Graceful Offline,
  Tethered Grounding, Public-Friendliness, Honest Memory,
  Modular Authorship, Open Knowledge, Pluggable Storage, The
  Unbroken Whole, Flexible Roots).

A new operator who runs `pip install ember-agent[sqlite_vec]` on
a fresh Pi gets *the same Ember they would have gotten today*. A
power-user who runs `pip install ember-agent[yggdrasil]` (V3 pip
extra) gets the constellation.

---

## What the operator experiences

After Yggdrasil ships, here's what the operator's first hour with
Ember looks like:

> They run `ember tui` (Stofa, the TUI from the parallel design
> tree). The hall opens. Hugin perches over the citations panel
> as before, but now Verðandi-the-Norn whispers in the status bar:
> *"You haven't asked me about Odin in 3 days. Last time, I
> suggested Yggdrasil-related notes. Want me to re-surface them?"*
>
> They say yes. Bifrǫst Bridge composes a search across Mímir's
> structured store (24 docs match "Odin"), Huginn's vector
> embeddings (47 semantically similar chunks), and Muninn's
> Hebbian associations (12 documents that *co-occur* with Odin
> in the operator's reading pattern).
>
> Ember replies. The tone is slightly warmer than usual; Seiðr
> noticed it's evening, Astrology Engine confirms the moon is
> waxing gibbous, and the response register shifts toward
> introspection. The reply cites three sources, two of which the
> operator hadn't actively asked about — but Muninn (associative
> memory) judged them relevant.
>
> Halfway through, Funi proposes calling `CloakBrowser` to fetch
> a Wikipedia page Ember can't reach with `fetch_url` (Cloudflare
> challenge). The Tool Approval modal asks. Operator says yes.
> The cloaked walker fetches; the content is read into context;
> Ember finishes her reply with the new material.
>
> When operator closes Stofa, Verðandi emits a `session_ended`
> event. Mímir's Well runs Ebbinghaus decay on the day's Episodes;
> the ones the operator engaged with most get reinforced. The
> Norns' backup writes a snapshot. Hugin returns to his perch.

That's not a different application. That's *Ember, more so* —
same identity, same trust model, same operator-at-home register.

---

## What the engineer experiences

For the contributor / maintainer:

- **Adding a new realm = writing one Adapter and one Plugin** —
  the patterns in this design tree are repeatable.
- **Debugging is observable** — every cross-realm call has a
  span in Verðandi's event bus; tracing is built in.
- **Self-healing is structural, not aspirational** — the gossip
  protocol + per-failure playbooks + Norns backups make
  partial-failure scenarios *automated recoveries*.
- **Cross-platform is tested at every release** — the device-
  capability detection layer means CI catches "this only works
  with CUDA" before it reaches operators.

This is the architecture an operator could trust to run their
Ember on a Pi cluster for *years* — through OS upgrades, sibling
project version bumps, hardware failures.

---

## What this design tree commits

This tree commits to **the conversation about ADR-0016**. The 66
docs are the input; ADR-0016 will be the synthesis-into-
commitment.

No code lands until:
1. The operator (Volmarr) reviews the tree.
2. ADR-0016 is drafted from it.
3. ADR-0016 is ratified.
4. Phase-1 implementation begins per
   [`../roadmap/91_PHASE_1_BIFROST_WIRING.md`](../roadmap/91_PHASE_1_BIFROST_WIRING.md).

Estimated effort over the 5 phases: **2-4 months of focused work**,
spread across natural project rhythm. Phase 1 alone (Bifrǫst
wiring) is ~10-15 focused days.

---

## Closing

Ember was built small so it could grow well. Yggdrasil is the
growing-well. Eleven realms, one tree, one operator, one
identity, one purpose: an AI companion who lives in the
operator's hardware, remembers like a person, knows what time it
is, can read the room, can find what she needs on the web,
recovers from her own crashes, runs everywhere, and serves only
the operator who owns her.

That's the grand vision. Everything else in this tree is the
how.
