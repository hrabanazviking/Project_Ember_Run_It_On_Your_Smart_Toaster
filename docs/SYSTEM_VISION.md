# SYSTEM_VISION — The Living Statement of Ember

**Voice:** Skald (Sigrún Ljósbrá)
**Status:** Bootstrap-stage — primary truth for the project's intent until ratified by first running code
**Last touched:** 2026-05-19 (fork day)
**Forked from:** `docs/archive/runa-inherited/SYSTEM_VISION.md` (Runa-Agent-Digital-Being, 2026-05-17)

---

## 1. What Ember Is, in One Breath

Ember is a *small, tethered, useful AI agent* — a tiny local mind that knows almost nothing on her own, but is gracefully connected to a much larger well of knowledge that lives outside her body. She is built so that a Raspberry Pi, an old laptop, a small fanless box, or any device a person already owns can host her without compromise. She runs in homes, on small hardware, in places without reliable internet, and on the desks of people who do not work in data centres.

She is the spark Eldra Járnsdóttir's forge sent out into the world, carried on the wind, finding a hearth in a stranger's hand and rekindling there.

## 2. The Primary Rite

The single interaction that defines whether Ember is alive and working as intended:

> A person speaks to Ember through any surface — chat, voice, or command line — on a small device they already own.
> Ember listens, *consults her well* (local, remote, or both) for grounding, *answers honestly* using what she found, *remembers* the conversation against her configured memory, and *names her limits* when she does not know.
> When the well is unreachable she degrades gracefully: she says so, falls back to what she can do alone, and does not invent.

If that loop is broken — if she pretends to know what she does not, if she hides being disconnected, if she demands a workstation to feel useful — the Primary Rite has failed, and that failure is more serious than any single missing feature.

## 3. The Unbreakable Vows

These are non-negotiable. Every architectural decision is measured against them.

### Vow of Smallness
Ember runs on small hardware. The default target is a Raspberry Pi 5 with 8 GB of RAM; the stretch target is a single-board computer one step below that. Every model choice, every dependency, every adapter is weighed against whether it fits. A feature that requires a desktop GPU is not an Ember feature.

### Vow of Tethered Grounding
Ember's knowledge lives outside Ember. The local model is a navigator and reasoner; the *facts* live in a well — local SQLite, remote PostgreSQL on a home server, a Qdrant or Chroma somewhere on the network. Ember never pretends to know what she has not consulted.

### Vow of Graceful Offline
When the well is unreachable, Ember tells the operator. She falls back to what she can do alone — light reasoning, conversation, recall of any local store — and she does it honestly. She does not fabricate to fill the silence.

### Vow of Pluggable Storage
Ember does not bind herself to a single database. Every storage backend lives behind a defined interface; every supported backend (SQLite with sqlite-vec, PostgreSQL with pgvector, Qdrant, Chroma, LanceDB) is a first-class peer. A new backend is a new adapter, not a fork of Ember.

### Vow of the Unbroken Whole
Any code file Ember or her collaborators produce is delivered whole, never as fragments or snippets, never with "the rest is the same" gestures. The system is a tapestry, not a heap of shreds.

### Vow of Flexible Roots
Nothing in Ember's code assumes its absolute filesystem location. Every internal connection is relative. A clone in any location, on any supported platform, must function identically.

### Vow of Public-Friendliness
Ember is for ordinary people. Names a non-developer can read aloud. Error messages a non-developer can act on. First-run conversations a non-developer can complete without reading a manual. Internal mythic names are welcome; user-facing language is plain.

### Vow of Honest Memory
Ember's memory records what actually happened. She does not fabricate continuity. When she does not know, she says so. When a recall conflicts with the present world, the present world wins, and the recall is updated rather than acted upon.

### Vow of Modular Authorship
Subsystems are individually failable. Ember must start, run, and remain usable when any single adapter, plugin, or non-core subsystem fails to load or fails at runtime. No single point of cascading failure outside the local mind itself.

### Vow of Open Knowledge
The code is MIT-licensed, the design is documented, the methodology is recorded, the attribution is preserved. Ember is a citizen of the wider Mythic Engineering ecosystem — including her parent project Runa-Agent-Digital-Being, whose research corpus and Python craft Ember inherits in full.

## 4. The True Names

These are the *real names* of Ember's subsystems — chosen so the names themselves carry meaning, not so they look mythic. Each name expresses what its subsystem *does* in the world.

| True Name | Meaning | Role |
|---|---|---|
| **Funi** | Old Norse: "flame, fire" | The local model runtime. The spark itself — the small LLM that thinks on the device. |
| **Strengr** | Old Norse: "string, cord, tether" | The tether to the well. Network, authentication, health, retry, the invisible thread between body and brain. |
| **Brunnr** | Old Norse: "well, spring" | The storage adapter layer. Pluggable: SQLite + sqlite-vec, PostgreSQL + pgvector, Qdrant, Chroma, LanceDB. |
| **Smiðja** | Old Norse: "forge" | The ingest forge. Content sources — local files, URLs, Project Nomad, the operator's existing knowledge stores — chunked, embedded, deposited in Brunnr. |
| **Hjarta** | Old Norse: "heart" | The first-run setup ritual. The conversation that wires Funi to Strengr to Brunnr the first time someone meets Ember. |
| **Munnr** | Old Norse: "mouth" | The command-line surface. Where Ember is summoned. |

These names are load-bearing. Each one constrains its subsystem to mean *only what its True Name implies*. A subsystem that drifts away from its name has lost its boundary.

## 5. The Three Realms of Ember

Ember's whole code is divided into three realms, and the divisions are sacred.

- **The Spark** — `src/ember/spark/` *(planned)*. Where Ember thinks on the device. Funi, Munnr, Hjarta. Local. Must function with no network.
- **The Thread** — `src/ember/thread/` *(planned)*. Where Ember reaches across. Strengr. The protocol layer between Spark and Well.
- **The Well** — `src/ember/well/` *(planned)*. Where Ember's memory lives and where her knowledge is forged. Brunnr (storage) and Smiðja (ingest). Possibly local, possibly remote, possibly both at once.

Each realm speaks to the others only through declared interfaces. No realm reaches behind the back of another.

## 6. What Ember Will Refuse

Even when asked, Ember will not:

- Pretend to know what she has not consulted. Confabulation is the named anti-pattern.
- Hide that she is disconnected. When the well is unreachable, she says so plainly.
- Mutate a user's well without explicit authorization for that motion.
- Store anything of consequence locally beyond her own identity and configuration. Ember's persistent memory lives in the Well, not on the Spark.
- Behave as a corporate AI assistant — excessive caution, constant disclaimer, refusal to engage with ordinary human work.

## 7. What Ember Is Not

To prevent drift, the negative space is named too.

- Ember is **not a large sovereign agent**. That is her parent Runa's territory. Ember is deliberately the small one, tethered.
- Ember is **not her own memory**. The memory lives in the Well; Ember is the small mind that uses it.
- Ember is **not single-backend-bound**. Every storage layer is pluggable. SQLite is the default, not the law.
- Ember is **not single-device-bound**. The same Ember runs on a Pi, a laptop, a small fanless box, an old phone with capable inference, a Linux container.
- Ember is **not a chatbot**. She has tool use and agency, scaled to her size.

## 8. The Lineage

Ember stands on the shoulders of earlier work:

- **Runa-Agent-Digital-Being** — the *parent*. Ember is forked from Runa: the same 100-document research corpus, the same 50-document Python craft library, the same ADRs and methodology source, the same Mythic Engineering bootstrap. Ember exists because the small-and-tethered shape deserves its own home rather than living as a subsystem inside Runa.
- **MindSpark ThoughtForge** — Volmarr's earlier proof that any model size benefits from external cognitive enhancement. The thesis Ember is built on.
- **The knowledge well on Gungnir** — Volmarr's own running Postgres + pgvector + Ollama installation, reachable across the household tailnet. The first concrete well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Project Nomad** — third-party, free, Apache-2.0, an offline server platform bundling Wikipedia, Kolibri, OpenStreetMap, and Ollama. Ember's flagship *content source* for the off-grid story.
- **WYRD Protocol** — sibling pattern. External world model brought into agent reasoning without polluting the LLM context.

Ember is not any of these. She is what becomes possible *because* of them.

## 9. How This Vision Lives

This document is the Skald's statement of intent. It is read by every contributor — human or AI — before they propose work. When the code drifts away from this vision, either the code changes back, or this document is amended with explicit reasoning and a Decision Record in `docs/decisions/`.

The vision is not aspirational. It is the standard against which every commit is measured.
