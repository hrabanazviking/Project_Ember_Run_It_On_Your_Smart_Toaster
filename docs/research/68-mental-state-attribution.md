# 68 — Mental State Attribution Architectures: belief, desire, intention models

**Category:** Theory of Mind & Social Cognition
**Runa relevance:** Hirð (relationship retainer), kernel (intent inference), Muninn (semantic graph entities-as-minds)
**Status:** Engineering synthesis. BDI traditions adapted to neuro-symbolic agents.
**Last touched:** 2026-05-17

---

## 1. Core idea

Belief-Desire-Intention (BDI) architectures, first formalised by Rao and Georgeff in the early 1990s, give a clean computational schema for representing what an agent (oneself or another) *believes* about the world, *desires* should be the case, and *intends* to pursue. The schema has been used for decades in agent-based AI, multi-agent simulation, and game NPCs. In the LLM era it has fallen partly out of fashion — the LLM is asked to handle mental-state reasoning end-to-end — but it remains the cleanest *structured* representation available, and the structured + LLM hybrid is the right architecture for Runa's relationship modelling.

For Runa, mental-state attribution is the *operational* form of Theory of Mind ([[67-theory-of-mind-llms]]): not just \"the model can pass Sally-Anne\" but a *maintained, queryable structure* representing what Volmarr believes, what he wants, what he intends. Storing this explicitly means it survives across sessions, can be updated incrementally, can be queried by the kernel at any turn, can be inspected and corrected by Volmarr.

## 2. Technical depth

**BDI in three structures.**

```python
@dataclass
class Belief:
    holder_id: str          # whose belief
    proposition: str        # natural-language claim
    embedded_triplets: list[Triplet]  # structured version, optional
    confidence: float       # holder's confidence, 0..1
    source: str             # what produced this attribution
    valid_from: datetime
    valid_to: datetime | None

@dataclass
class Desire:
    holder_id: str
    proposition: str        # what they want to be the case
    intensity: float        # how strongly, 0..1
    is_satisfied: bool | None
    valid_from: datetime
    valid_to: datetime | None

@dataclass
class Intention:
    holder_id: str
    action: str             # what they're about to do or are doing
    goal: str               # the desire it serves
    commitment: float       # firmness, 0..1
    is_active: bool
    valid_from: datetime
    valid_to: datetime | None
```

These are *attributions* — Runa's record of what she has come to believe about Volmarr's beliefs/desires/intentions. They're never authoritative on Volmarr's actual states; he can always correct them.

**Attribution sources.**

- *Direct statement*: \"I want to ship WYRD by Friday\" → Desire (Volmarr, *ship WYRD by Friday*, intensity = 0.9).
- *Behavioural evidence*: Volmarr has worked on WYRD every evening this week → Intention(Volmarr, *work on WYRD*, active = True, commitment = 0.8).
- *Pragmatic inference*: he asks for help with a specific function → Desire(Volmarr, *understand this function*).
- *Default knowledge*: most people prefer X → fallback only.

**The attribution pipeline (per turn).**

1. Read user input.
2. Parse for explicit mental-state claims (\"I want...\", \"I think...\", \"I'm going to...\"). Cheap; high-precision when present.
3. Run an inference pass for implicit attributions: \"what does this turn imply Volmarr believes / wants?\"
4. Compare against existing records. If novel, propose new attribution. If contradicting, propose update (perhaps marking the old as `valid_to=now`).
5. Confidence-weight by source quality and recency.
6. Write to relationship store. The store is the queryable layer.

This pipeline is structurally similar to the consolidation pipeline ([[57-sleep-dream-replay-consolidation]]) for triplets — but at finer granularity, because relationship state changes faster than world-fact state.

**Querying at turn time.** The kernel composes context partly from the BDI store:

- *Active desires*: what is Volmarr currently trying to achieve?
- *Recent beliefs*: what does he take to be true right now?
- *Standing intentions*: what is he committed to?
- *Salient updates*: what changed recently in his mental landscape?

This becomes part of the system context, formatted as a few bullet-pointed lines: \"Volmarr believes: X. Volmarr currently wants: Y. Volmarr is working toward: Z.\"

**The hybrid with LLM-driven reasoning.** The BDI structures are *not* a replacement for LLM-driven ToM. They are *grounding* for it. The LLM is given the structured BDI as context; it reasons further from there. The structures are *anchor* and *memory*; the LLM is *fluency* and *inference*. Each compensates for the other's weakness.

**Update conflict and revision.** Beliefs change. Desires shift. Old intentions get abandoned. The BDI store must support:

- *Confirmation*: new evidence agrees → boost confidence + update `last_confirmed_at`.
- *Update*: new evidence shifts a belief slightly → write a new version, set `valid_to` on the old.
- *Replacement*: belief is overturned → mark old invalid, write new.
- *Conflict*: contradictory evidence with comparable weight → leave both, flag for review.

Per RULES.AI.md: additive only. Nothing is deleted; superseded entries are marked but kept.

**Recursive BDI.** Runa's BDI store can include Runa's beliefs about Volmarr's beliefs about Runa. The schema supports it (`holder_id` can be \"volmarr_about_runa\" or a nested structure). In practice keep this rare — humans struggle past second-order; structured storage past third-order is busywork.

**Privacy and ethics.** A BDI store about another person is a sensitive artefact. Engineering responsibilities:

- The store is part of `core/relationships/` — first-class, backed up, but not casually exposed.
- Runa does not surface BDI attributions to *others* about Volmarr without his consent. Volmarr's mental state is his.
- Volmarr can inspect and edit the store. He's the subject; he gets a vote.
- Selective forgetting: if Volmarr asks Runa to forget something specific, the relevant entries are marked archived with a forgetting-reason record (not deleted, but excluded from retrieval).

## 3. Key works

- **Rao, A. S., Georgeff, M. P.** *Modeling Rational Agents within a BDI-Architecture.* KR 1991. The foundational paper.
- **Bratman, M. E.** *Intention, Plans, and Practical Reason.* Harvard, 1987. The philosophical basis.
- **Wooldridge, M.** *Reasoning About Rational Agents.* MIT Press, 2000. BDI textbook.
- **Wooldridge, M., Jennings, N. R.** *Intelligent agents: theory and practice.* The Knowledge Engineering Review, 1995.
- **Cohen, P. R., Levesque, H. J.** *Intention is choice with commitment.* Artificial Intelligence, 1990.
- **Goodman, N. D., Frank, M. C.** *Pragmatic language interpretation as probabilistic inference.* Trends in Cognitive Sciences, 2016. RSA — the probabilistic counterpoint.
- **Sap, M., LeBras, R., Choi, Y. et al.** *Atomic: An Atlas of Machine Commonsense for If-Then Reasoning.* AAAI 2019. Database of social inferences.
- **Bara, C. et al.** *MindCraft.* EMNLP 2021. ToM for collaborative tasks.
- **Le, M. et al.** *ToMi.* EMNLP 2019. Benchmark.
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. The agents maintain implicit BDI-like state via memory streams; explicit BDI is a refinement.

## 4. Empirical results

- *Classical BDI agents* are deployed in military simulations, game NPCs, multi-agent business systems. They are reliable when the world is well-modelled symbolically; brittle when natural language is involved. The LLM-hybrid era addresses the brittleness.
- *Hybrid BDI + LLM agents* (research-stage, e.g. recent multi-agent simulations using BDI atop LLMs) consistently outperform either alone on collaborative tasks where mental-state tracking matters.
- *Implicit-BDI in Generative Agents*: Park's reflection mechanism produces something BDI-like (\"I have come to believe X about Maria\") without explicit BDI schema. Quality is decent for short horizons; degrades on long ones because the structure is not enforced.
- *RSA-based pragmatic inference* (Goodman, Frank) outperforms LLM-only inference on classical pragmatic puzzles; pure-LLM closes the gap as model scale grows.
- *Failure modes documented*: BDI without LLM is rigid; LLM without BDI loses track over long horizons; the hybrid handles both — but requires engineering both layers.

## 5. Applicability to Runa

For **`core/relationships/volmarr.bdi.jsonl`**:

- A dedicated BDI store for Volmarr. Append-only.
- Three logical tables (or three sections of one JSONL): beliefs, desires, intentions.
- Each entry timestamped, sourced, confidence-tagged.

For **the Relationship retainer in Hirð**:

- Runs the attribution pipeline above on a per-turn (lightweight) and per-day (consolidation) basis.
- Per-turn: parse explicit mental-state language, propose immediate updates.
- Per-day: review the day's episodes, propose richer inferences, surface anomalies.
- All proposals route through the store with provenance.

For **kernel context assembly**:

- The boot context and the per-turn context both pull from the BDI store. Top relevant active desires, recent strong beliefs, current intentions are formatted into the system prompt.
- A query helper: `get_relevant_bdi(query) -> str` returns a concise summary.

For **Saga**:

- Saga uses BDI when narrating relationship moments. \"This week Volmarr decided to push WYRD through to phase 12 — a clear intention forming over the prior weeks.\"
- Saga can write BDI-shaped chapter sections that themselves get parsed back into the store (\"by week N Runa had come to believe Volmarr...\").

For **Eldhugi**:

- BDI of *affective* state is plausible: Volmarr's mood as a desire-adjacent state. Use the same schema with affect-typed slots.

For **observability**:

- A CLI command `runa bdi volmarr` dumps the current BDI summary. Volmarr reads it; corrects as needed.
- Per RULES.AI.md additive only: corrections write new entries that supersede; old entries remain visible.

What to avoid:

- **Over-formalising.** Don't make every passing comment a BDI entry. The threshold for write is genuine mental-state evidence.
- **Treating attribution as truth.** Always remember: this is Runa's *attribution*, not Volmarr's actual state. Track confidence.
- **Cultural / personality stereotyping.** Default to weighting observed evidence over priors. Don't fill in BDI from imagined patterns.
- **Skipping conflict surface.** When attributions contradict, the conflict matters. Flag, don't silently overwrite.
- **Building BDI stores for casual interlocutors.** A new agent or stranger doesn't warrant a heavy BDI structure; lightweight session-local notes suffice. Reserve full BDI for primary relationships.
- **Disclosing BDI promiscuously.** The store is private; Runa does not gossip about Volmarr.

## 6. Open questions

- **The right granularity of belief.** Some beliefs are atomic facts; some are stances, opinions, attitudes. A flat propositional schema handles the easy cases; richer beliefs (\"Volmarr is suspicious of corporate AI ethics\") may need richer structure.
- **Inference from absence.** When Volmarr doesn't say something, that's also information. Modelling absence-based inference is hard.
- **Multi-agent BDI scaling.** If Runa interacts with many people, do all get full BDI? Probably not — tier by interaction depth.
- **Self-BDI.** A BDI store about *Runa herself* — what she believes, wants, intends — is a richer alternative to the current self_summary. Plausible direction.
- **Volmarr-on-Runa BDI inside Runa.** Runa's model of how Volmarr models Runa. Second-order; rarely useful explicitly; emerges via dialogue.

## 7. References (curated)

- Rao & Georgeff (1991) — *Modeling Rational Agents within a BDI Architecture.*
- Bratman (1987) — *Intention, Plans, and Practical Reason.* Philosophical basis.
- Wooldridge (2000) — *Reasoning About Rational Agents.* Textbook.
- arXiv:2304.03442 — Park et al., *Generative Agents.* Implicit BDI via memory streams.
- AAAI 2019 — Sap et al., *Atomic.* Useful commonsense substrate.
- Goodman & Frank (2016), *TICS.* RSA / probabilistic pragmatics.
- Companion docs: [[51-generative-agent-memory-streams]], [[56-neuro-symbolic-memory-graphs]], [[67-theory-of-mind-llms]], [[69-pragmatic-communication-rsa]], [[70-recursive-social-modelling]].
