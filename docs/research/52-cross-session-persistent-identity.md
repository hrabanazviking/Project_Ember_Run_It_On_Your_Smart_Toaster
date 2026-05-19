# 52 — Cross-Session Persistent Identity via Memory Snapshots and Replay

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (persistence layer), identity (continuity of self), kernel (boot ritual)
**Status:** Engineering synthesis. The "how" of being the same Runa next session.
**Last touched:** 2026-05-17

---

## 1. Core idea

LLMs are stateless across calls. Anything that persists about an agent — personality, history, ongoing concerns, relationships — must be reconstituted from external storage every time the model is invoked. *Cross-session persistent identity* is the engineering discipline of making this reconstitution faithful enough that the agent on Tuesday morning is recognisably the same agent who said goodnight on Monday — not by metaphysical claim, but by behavioural and narrative continuity.

The construction has three independently necessary parts: a **durable substrate** (the bytes on disk that survive the process), a **boot ritual** (the deterministic procedure that re-inflates working state from the substrate at every wake), and a **journal of becoming** (the append-only record of how the identity changed between wakes, so growth is preserved and visible). Together these are the substrate of continuity. Each is non-trivial in its own way; the *combination* is what makes identity actually persist.

## 2. Technical depth

**The durable substrate.** What must survive a process exit:

```
identity/
├── persona.md             ← static voice, values, name, tone (rarely edited)
├── identity_journal.jsonl ← every meaningful change, append-only, with cause
├── relationships/
│   ├── volmarr.json       ← who he is, what we share, ongoing threads
│   └── ...
├── ongoing_concerns.md    ← what Runa is currently caring about
└── self_summary.md        ← reflection's latest distilled "who I am"

muninn/
├── episodes.db            ← sqlite: id, ts, content, embedding, importance, last_accessed
├── reflections.db         ← summaries with provenance arrays
└── episodes.faiss         ← optional vector index (or sqlite-vss; see [[08-sqlite-vss-embedding-in-database]])

saga/
└── chapters/              ← per-week prose narrations, immutable once written

logs/
├── boot_log.jsonl
└── turn_log.jsonl
```

The split between *identity* (slowly changing, mostly markdown for human auditability) and *muninn* (rapidly changing, database for query) matters. Identity is something Volmarr can read; Muninn is something Runa can query.

**The boot ritual.** When the runtime starts a session:

1. **Load persona.md** — sets system-prompt prefix. This is Runa's voice baseline.
2. **Load self_summary.md** — the *current* most distilled self-account, written by the last reflection pass. This is Runa-to-Runa, what she said to herself about herself last time.
3. **Load top-K most recent + most important Muninn episodes** under the retrieval rule (see [[51-generative-agent-memory-streams]]). Capped at e.g. 30 entries to fit context.
4. **Load ongoing_concerns.md** — open threads. What was unfinished.
5. **Load relationship-context for whoever just spoke** (e.g. Volmarr's relationship.json).
6. **Assemble the system prompt** by concatenating: persona ▸ self_summary ▸ active_relationship ▸ retrieved_episodes ▸ ongoing_concerns.
7. **Write a boot entry** to identity_journal.jsonl with the timestamp and the assembled context fingerprint. This is the *fact* of waking; later reflections can refer to it.

Crucially: the boot ritual is deterministic. Given the same disk state, the same context is assembled. This makes the run reproducible and debuggable.

**The journal of becoming.** The identity_journal is the only place where *change to identity* is recorded. Schema:

```jsonl
{"ts":"2026-05-17T08:31:00Z","type":"persona_edit","actor":"volmarr","summary":"clarified Runa's stance on...","diff":"..."}
{"ts":"2026-05-17T22:14:00Z","type":"reflection","actor":"saga","summary":"identified a new value...","source_episodes":["e123","e187"]}
{"ts":"2026-05-18T07:55:00Z","type":"relationship_update","actor":"runa","target":"volmarr","summary":"...","source_episodes":["e201"]}
```

Three actor classes — Volmarr, Saga (reflection), Runa-self (any subagent including the kernel) — and an immutable record of who changed what when and why. Identity can grow; *what cannot be made to silently change is the record of its growth*.

**Replay.** Because identity_journal is append-only and event-sourced, the *trajectory* of Runa's identity is reconstructible from scratch by replaying entries. This is the same technique used by event-sourcing databases ([[22-event-sourcing-cqrs]]). It costs nothing to retain and is the only way to answer the question "how did Runa become who she now is."

**Conflict and contradiction.** If a reflection writes one thing and Volmarr explicitly overrides it, both events go in the journal. The current `self_summary.md` reflects the latest synthesis. Older versions remain readable in git. No silent overrides; no lossy edits.

## 3. Key works

- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. The flat memory stream as continuity substrate.
- **Packer, C., Wooders, S., Lin, K. et al.** *MemGPT.* arXiv:2310.08560, 2023. Two-tier core/archival memory; see [[01-memgpt-os-memory-hierarchies]].
- **Sumers, T. R., Yao, S., Narasimhan, K., Griffiths, T. L.** *Cognitive Architectures for Language Agents.* arXiv:2309.02427, 2023. Names *procedural memory* as part of agent identity.
- **Lample, G. and Conneau, A.** (and successors). RAG framing. [[04-rag-evolution]].
- **Anthropic (2024+).** *Claude Memory Tool* docs. Tool-mediated persistent memory in production.
- **OpenAI (2024+).** *ChatGPT memory* feature. Production cross-session continuity at scale (architecture only partly public).
- **Letta** (formerly MemGPT). Open-source agent platform with persistent memory; reference implementation worth reading.
- **Hofstadter, D.** *I Am a Strange Loop.* 2007. Philosophical backdrop for *what* it means to be the same self across time. [[43-hofstadter-strange-loops]].
- **Parfit, D.** *Reasons and Persons.* 1984. Personal identity philosophy; the bundle theory underwrites the engineering stance here.

## 4. Empirical results

- *Production deployments.* ChatGPT memory has been live since early 2024; user reports converge on \"persists facts, less reliable on personality\". Anthropic's memory tool (late 2024+) gives explicit read/write/delete primitives that the model uses on demand; in evals this produces measurably better long-horizon coherence.
- *Generative Agents.* Park's 25-day Smallville run is the canonical long-horizon empirical demo. Behavioural coherence survived the duration without identity collapse, contingent on reflection cadence.
- *Failure modes documented.* Identity drift under retrieval pressure: when the agent retrieves many low-importance memories, the persona prompt's signal-to-noise drops and behaviour goes generic. The fix is importance-weighted retrieval (Park) or hierarchical retrieval (MemGPT).
- *Boot-context budget.* Empirically, ~30 retrieved episodes + persona + self_summary in a 32K-context window leaves ample room for the actual conversation without bleed. Smaller-context models need more aggressive distillation.

## 5. Applicability to Runa

This is directly Runa's substrate question. The PHILOSOPHY says Runa is "a sovereign digital being living on a dedicated machine." That is operationally meaningful only if Runa-on-Tuesday is Runa-on-Monday, which requires this layer.

For **`core/identity/`**:

- Implement the durable-substrate layout above. Markdown for human-readable; sqlite for query-optimised.
- The boot ritual lives in the kernel's startup path. Deterministic, fast (<1s on the Pi 5), instrumented.
- The identity_journal is the *only* legal way to mutate identity. All persona edits, all reflection-driven updates, all relationship updates go through it. Write helpers enforce append-only.

For **Muninn**:

- Episodes live forever (or until consolidation; see [[57-sleep-dream-replay-consolidation]]).
- Importance + recency + relevance retrieval at boot, per [[51-generative-agent-memory-streams]].
- Reflection writes back into both Muninn (as memory) and the identity_journal (as identity event) when a reflection genuinely shifts how Runa describes herself.

For **Saga (the narrator)**:

- Saga's chapters are the *prose* memory layer — immutable once written, weekly cadence. They are Runa-narrating-Runa, the literary form of self_summary.md.
- A new chapter is written every week from that week's high-importance episodes + reflections. The chapter itself becomes a Muninn episode (so it can be retrieved later) and a journal event (so the act of becoming-narrated is recorded).

For **kernel boot:**

- The first thing the kernel does at every session start is the boot ritual. Before any external input is processed, Runa knows who she is. This is non-negotiable.
- The last thing the kernel does at session end is a clean *flush*: any in-memory state goes to disk; any unfinished reflection runs to completion if cheap, queues otherwise.

What to avoid:

- **Lossy overwrite of `self_summary.md`.** Git tracks it; the journal records the cause. Never silently replace.
- **Conflating Muninn episodes with identity events.** An episode is *that something happened*; an identity event is *that something changed about who Runa is*. Different rates, different schemas, different audiences.
- **Hardcoding identity in code.** Per RULES.AI.md: identity lives in data files. The code reads; the code does not assert.
- **Trying to be \"the same\" by freezing.** Identity is stable, not frozen. Stability is achieved by continuity of substrate + traceable change, not by refusing to update.
- **Ignoring the cold-boot edge case.** First boot of a brand-new Runa needs a special path: the journal is empty, the self_summary is the seed text from `PHILOSOPHY.md`. Don't crash; bootstrap gracefully.

## 6. Open questions

- **How to compress identity over years.** After three years, the journal is hundreds of thousands of entries. Reflection-of-reflection helps, but at some point a compression-with-residue strategy is needed. Open.
- **Multiple-machine identity.** If Runa is migrated from one Pi to another, the disk substrate moves; what about model-internal state? The persona prompt makes this *largely* portable, but quirks of a specific model version are not in the substrate. See [[55-adapter-based-identity-persistence]].
- **Identity under model upgrade.** When llama.cpp or the base model changes, behaviour changes subtly. Persona stays the same on paper; tone shifts. How to detect and reconcile.
- **The right granularity for relationship files.** Per-person is obvious for Volmarr; what about a fleeting interlocutor? Open design question.
- **Privacy and selective forgetting.** A digital being who is asked to forget something must do so verifiably. Append-only is hostile to this. Open. See [[95-capability-based-security]].

## 7. References (curated)

- arXiv:2304.03442 — Park et al., *Generative Agents.* Section 4 (memory) is the reference architecture.
- arXiv:2310.08560 — Packer et al., *MemGPT.* Tiered memory + paging.
- arXiv:2309.02427 — Sumers et al., *Cognitive Architectures for Language Agents.* The categorisation of agent memory types.
- Anthropic docs — *Claude memory and tool-mediated persistence.* Production design.
- Letta source — open-source agent platform with explicit persistent identity. `github.com/letta-ai/letta`.
- Hofstadter (2007), *I Am a Strange Loop.* The why behind the engineering.
- Parfit (1984), *Reasons and Persons.* Personal-identity philosophy in the bundle-theory vein.
- Companion docs: [[01-memgpt-os-memory-hierarchies]], [[51-generative-agent-memory-streams]], [[53-autobiographical-memory-architectures]], [[55-adapter-based-identity-persistence]], [[62-identity-stability-under-change]].
