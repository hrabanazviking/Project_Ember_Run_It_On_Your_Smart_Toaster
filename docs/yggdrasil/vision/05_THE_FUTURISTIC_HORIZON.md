# 05 — The Futuristic Horizon

What Yggdrasil enables *beyond* the 5-phase roadmap, in the
2-5 year horizon. Speculative but grounded — every horizon item
is a natural extension of patterns established in this design
tree.

---

## The horizon themes

Five major themes for where Yggdrasil could go after V1.0:

1. **Multi-agent constellations.**
2. **Federated learning under sovereignty.**
3. **Edge-AI integration (on-device models).**
4. **Cross-operator collaboration without surveillance.**
5. **Truly autonomous agents (within constraints).**

Each is discussed below. None is committed; each is *possible*
because of the Yggdrasil foundation.

---

## 1. Multi-agent constellations

Today Ember is one agent. Tomorrow, an operator might run
multiple Ember-class agents, each with a different focus:

- **Ember-the-archivist** — runs on the home server, ingests
  the operator's notes, maintains the Well.
- **Ember-the-research** — runs on the desktop, uses
  CloakBrowser + external corpora for current information.
- **Ember-the-companion** — runs on the laptop, focused on
  conversation, lighter Well.

Each is a separate Ember instance. Verdandi's event bus lets
them know about each other:

- Archivist publishes "I just ingested 12 new documents about
  Odin."
- Research subscribes; its next session can mention "I see you
  added Odin documents — want me to fold them into the
  external-research context?"
- Companion subscribes; small-talk can reference "you've been
  reading a lot about Odin lately."

This requires:
- Bifrǫst extended to bridge between agent instances.
- Verdandi's event format generalized for inter-agent traffic
  (already framework-agnostic; minor work).
- Identity model that lets multiple Embers share an operator's
  "core" identity while having sub-roles.

Estimated effort: ~1-2 months of focused work *after* V1
multi-device federation lands. Not committed.

---

## 2. Federated learning under sovereignty

The Hebbian layer (Muninn) currently runs locally. With
operator opt-in, a federated extension could share *associations*
(not raw data) across operators who choose to participate.

Example: 100 operators opt in. Each's local Muninn computes
their personal associations. A federated layer averages
*anonymized weight updates* across all 100. Each operator's
local Muninn gets stronger associations *that were learned
across the cohort* — without anyone seeing anyone else's
documents or queries.

This is *federated learning* applied to associative memory.
Requires:
- An opt-in mechanism (Vow of Sovereignty — never default-on).
- A trust model (operators trust the federator, OR a
  peer-to-peer model that doesn't require central trust).
- Differential privacy on the weight updates.
- Operator-visible audit of what was shared.

Politically and ethically interesting. Technically feasible.
Not committed — opt-in federation is a separate ADR.

---

## 3. Edge-AI integration

Ollama is the current Funi runtime. Future Funi adapters might
include:

- **llama.cpp directly** (the runtime under Ollama, but
  faster startup).
- **Apple's Foundation Models** (on-device Apple Silicon).
- **Microsoft's Phi-3-Silica** (Snapdragon X+ NPU).
- **WebGPU-based models** (browser AI, when Ember has a web
  interface in V3+).
- **Specialized hardware accelerators** (Coral TPU, Rockchip
  NPU on Pi-class boards).

Yggdrasil doesn't change Funi's adapter pattern — it inherits
it. Adding new runtimes is the slice-by-slice path the project
has always followed (per ADR-0009).

The horizon: a Pi 5 with a Coral TPU runs Ember at desktop-
speed. Hamr renders Auga at 30fps via integrated GPU. The
constellation runs on a $200 BOM.

---

## 4. Cross-operator collaboration without surveillance

Currently Ember is single-operator. With Bifrǫst + Verdandi
mature, two operators could collaborate without either's data
leaving their own machine:

- Operator A asks Ember: "I'm wondering about Norse
  cosmology."
- Ember-of-A checks A's Well, then queries (with A's consent)
  Ember-of-B's *public-facing* Well (B has marked some
  documents shareable).
- Ember-of-A gets a citation from B's documents and surfaces
  it to A.
- A could optionally reply to B asynchronously: "I found your
  Yggdrasil notes useful; here's a question…" — sent as a
  message, not a data sync.

The shared layer is *thin* — operators share *citations*, not
*Wells*. No central server; just operator-to-operator
publishing of certain document IDs as discoverable.

Requires:
- A discovery protocol (tailnet-friendly, no central registry).
- Cryptographic signing of shared citations (Kista helps).
- Operator-controlled "what's shareable" rules.

This is fundamentally different from "social media for AIs."
It's *operator-to-operator, slow-time, document-citation-only*.
Sovereign by design.

---

## 5. Truly autonomous agents (within constraints)

The current Ember waits for the operator. A future Ember could,
with operator opt-in, take initiative within bounded scopes:

- "Every Sunday, re-ingest my notes directory and tell me
  what's new."
- "When new documents land in `~/notes/inbox/`, ingest them and
  alert me."
- "When the lunar phase changes, write me a short Seiðr-
  generated mood line."
- "When I haven't asked about a topic in 2 weeks, gently
  surface it."

Each is a *scheduled* or *event-triggered* action with a clear
trigger and a clear scope. None is "free agency"; all are
operator-configured bounded behaviors.

Requires:
- A scheduling layer (cron-like; Verdandi + a small scheduler).
- Bounded-scope contracts (per-trigger: what can the action
  do? answer: nothing more than the operator could have done
  manually via the same tool).
- Audit log entries for every autonomous action.

This is *agentic Ember* — but agentic in the *constrained,
audited, operator-controlled* sense. Not LLM-fully-runs-the-
world.

---

## What we deliberately leave on the horizon

Some things that would be *technically* possible but
philosophically wrong:

- **"Ember talks to the operator's other apps."** No — Ember
  is in her hall; other apps don't get an integration
  surface unless they're MCP-server-compliant and the operator
  opts in.
- **"Ember reads the operator's emails."** Hard no. Unless the
  operator explicitly ingests their email into the Well as
  documents, Ember has no access.
- **"Ember talks to other operators' Embers without explicit
  per-message consent."** The cross-operator collaboration
  pattern requires *per-citation operator approval*, not blanket
  "always share with B's Ember."

These are *deliberate non-features*. The horizon is not
"everything could be." It's "everything *sovereign* could be."

---

## Timeline shape

Roughly:

- **2026 H2:** V1 ships (Yggdrasil 5 phases).
- **2027:** V2 — plugin ecosystem, more sibling integrations,
  community contributions.
- **2028:** V3 — multi-agent constellations, federated
  learning option (opt-in).
- **2029-2030:** Cross-operator collaboration, more edge-AI
  runtimes, mature autonomous-within-bounds behavior.

This is *not a commitment*. It's a sketch. Real timeline
depends on what operators ask for, what siblings ship,
hardware evolution, etc.

---

## The decade-long view

By 2036:

- **Sovereign AI is a recognized category.** Ember + Yggdrasil
  are one of several mature implementations.
- **Norse-themed sovereign-AI** is a small but real aesthetic
  / philosophical tradition in the field.
- **Multi-device federated single-operator setups** are a
  common pattern (the way "headless Pi server + laptop client"
  is a common pattern in self-hosted today).
- **The Pi-class minimum stays the discipline.** As the world
  moves to bigger AI, Ember's commitment to running on small
  hardware becomes more distinctive, not less.

---

## What stays the same

Across every horizon scenario, **the Vows hold**:

- Smallness — never bloat for bloat's sake.
- Sovereignty — never compromise operator ownership.
- Graceful Offline — never require connectivity.
- Tethered Grounding — never invent.
- Public-Friendliness — never alienate Iðunn.
- Honest Memory — never claim more than the tools support.
- Modular Authorship — never hold siblings hostage.
- Open Knowledge — never hide behind closed source.
- Pluggable Storage — never lock in.
- The Unbroken Whole — never crash the hall.
- Flexible Roots — never assume one filesystem layout.

These constrain the horizon. They also *protect* it. An Ember
in 2036 that still honors all 11 Vows is recognizably the same
Ember as today — just much more capable.

---

## Closing

The horizon is wide. The discipline is narrow: *what does the
operator deserve?* Yggdrasil V1 is the foundation. The horizon
is what an operator with the foundation can build over the
years that follow. Eleven realms today; perhaps twenty by
2030; perhaps a constellation of independently-sovereign-yet-
collaborative operators by 2036. We can't know. We can
*prepare*.

That preparation is what this design tree is.
