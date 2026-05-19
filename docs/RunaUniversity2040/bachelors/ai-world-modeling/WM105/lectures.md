# WM105: Introduction to the WYRD Protocol — The Loom of Fate

## Bachelor of Science in AI World Modeling — Year 1, Semester 2
## Runa University, 2040

---

*"In the well of Urd, the Norns carve runes into the roots of Yggdrasil. What was, what is becoming, what must be — these are not tenses of a single verb, but three distinct voices in the grammar of fate."*

— From the WYRD Protocol v3.2 Specification, Foreword

---

# Lecture 1: The Loom of Fate — Historical and Conceptual Foundations

## 1.1 Opening: Why "WYRD"?

The Old English word *wyrd* — cognate with Old Norse *urðr* — originally meant "that which has come to pass," a nominalization of the verb *weorþan*, "to become." In the Poetic Edda, the Norns who sit by the well of Urd carve runes into the threads of Yggdrasil's roots, determining the fates of gods and mortals alike. The WYRD Protocol, now at version 3.2, takes this mythological architecture as its foundational metaphor: world state is not a snapshot but a woven fabric, and the three Norns — Urd, Verðandi, Skuld — give names to three irreducible temporal strata that any competent world model must represent.

This lecture introduces the intellectual lineage from which WYRD draws, the philosophical problems it addresses, and the high-level architecture of the Protocol itself.

## 1.2 The Problem of Temporal Representation in World Modeling

Classical approaches to world modeling in artificial intelligence have treated time as an annotation on state — a timestamp attached to a belief, a temporal index on a proposition. STRIPS (Fikes & Nilsson, 1971) represented the world as a set of predicates, and actions as add/delete lists that transition the world from one state to the next. Situation Calculus (McCarthy, 1963) introduced a more rigorous formalism but retained the fundamentally atemporal ontology: states exist "at" times, but time itself is not a constitutive part of the world model.

The WYRD Protocol argues that this approach is insufficient for agents that must reason about obligation (what must happen), possibility (what could happen), and historical context (what shaped the present). In WYRD, time is not an index — it is the architecture itself. The world state does not merely have a history; it *is* its history, its present transition, and its committed futures, all at once.

Consider a diplomatic agent navigating a treaty negotiation. Its world model must represent not only the current distribution of power (the present), but also the sequence of prior commitments that constrain what moves are now possible (the past), and the set of future obligations that the agent has bound itself to (the future). These three strata are not interchangeable — they have different epistemic statuses, different mutabilities, and different roles in reasoning. WYRD formalizes this distinction.

## 1.3 The Well of Urd: Mythological Architecture

In the Grímnismál and the Vóluspá, the well of Urd (*Urðarbrunnr*) sits beneath the third root of Yggdrasil. The Norns come there each day to draw water and pour it on the root, mixing it with clay to keep the World Tree alive. The imagery is precise: the well contains what has already been established (Urd); the act of pouring is what is currently happening (Verðandi); and the survival of the tree — its continued existence into tomorrow — is what is thereby ensured (Skuld).

The Protocol's designers at Runa University deliberately mapped this tripartite structure onto a technical architecture:

- **Urd (Past Layer):** An immutable, append-only log of all events that have been committed to the world state. Once written, Urd cannot be rewritten — only reconciled.
- **Verðandi (Becoming Layer):** The current deterministic transition function: given Urd and a set of active rules, Verðandi computes what the world is *in the process of* becoming.
- **Skuld (Future Commitment Layer):** A set of obligations, constraints, and scheduled state transitions that *must* occur unless explicitly revoked. Skuld is the future that the world has already promised to itself.

## 1.4 From Myth to Mechanism: The Protocol's Design Philosophy

The WYRD Protocol was first proposed in 2033 by Dr. Hildr Sørensen's group at the Runa University Cognitive Architecture Lab. The initial design (v1.0) was a simple event-sourcing system with a past log and a future queue — two layers, not three. The critical insight that led to v2.0 was that the *process of transition itself* — the "becoming" — could not be reduced to either the past that feeds it or the future it produces. Verðandi, the middle Norn, had to be elevated from a verb to a noun, from a function to a layer.

Version 3.0 introduced contradictory history reconciliation (the "Norn's Judgment" mechanism), and version 3.2 (current) refined the rule definition language, added support for multi-agent loom composition, and formalized the event-sourcing layer's relation to the Urd log.

The Protocol's design philosophy rests on four pillars:

1. **Determinism under Spec:** Given identical Urd and identical rules, Verðandi always produces the same intermediate state and the same Skuld. There are no random oracles inside the Protocol; stochasticity is encapsulated in the Urd log as explicit events, not in the transition function.
2. **Append-Only History:** The Urd log is cryptographically chained (Merkle-linked) and append-only. Rewriting history is modeled not as mutation but as reconciliation — a process described in Lectures 7 and 8.
3. **Commitment Before Occurrence:** An agent can commit to a future action before that action occurs. Skuld makes this commitment a first-class part of world state, not a mere annotation.
4. **Separation of Concerns:** The three layers have fundamentally different data structures, access patterns, and invariants. Any implementation that conflates them is, by definition, not WYRD-compliant.

## 1.5 Overview of the Course

This course progresses through twelve lectures. Lectures 2–4 treat each layer in depth. Lectures 5–6 address rule definition and branching futures. Lectures 7–8 cover the hardest problem in WYRD — contradictory history reconciliation. Lectures 9–10 shift to implementation: event sourcing and the world state engine. Lecture 11 situates the loom metaphor within a broader cognitive architecture, and Lecture 12 addresses multi-agent composition and open research challenges.

By the end of this course, you will have implemented a WYRD-compliant world state engine. That engine will maintain an Urd log, compute Verðandi transitions, manage Skuld commitments, and reconcile contradictory histories. It will be the loom on which your agent weaves.

## 1.6 The WYRD Protocol Specification, v3.2 — A Structural Preview

Formally, a WYRD world state *W* at logical time *t* is a triple:

> *W(t) = ⟨ Ur(t), Ve(t), Sk(t) ⟩*

where:
- *Ur(t)* is the Urd log — an ordered sequence of committed events *e₀, e₁, …, eₙ*, each a structured record with type, payload, causal predecessor, and cryptographic hash.
- *Ve(t)* is the Verðandi layer — a function *Ve: Ur(t) × Rules → IntermediateState*.
- *Sk(t)* is the Skuld layer — a set of future commitments (obligations or constraints).

The transition cycle:

1. An event *eₙ₊₁* arrives at Urd.
2. *eₙ₊₁* is appended to *Ur(t)* → *Ur(t+1)*.
3. *Ve(t+1)* is recomputed from *Ur(t+1)* and the current rules.
4. Commitments in *Sk* triggered by *Ve(t+1)* are evaluated.
5. Triggered obligations produce events appended to Ur; triggered constraints are checked.
6. Cycle repeats until no further commitments trigger (*quiescence*).

### Required Reading

- Sørensen, H., et al. (2033). "The WYRD Protocol: Deterministic State Transition for Temporal World Models." *Proceedings of the International Conference on Cognitive Architectures*, 12(4), 221–248.
- Sturluson, S. (trans. 2016). *The Prose Edda*. Chapters on Gylfaginning and Grímnismál.
- Fikes, R., & Nilsson, N. (1971). "STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving." *Artificial Intelligence*, 2(3–4), 189–208.

### Discussion Questions

1. The WYRD Protocol claims that time is not an index but an architecture. Construct an argument *against* this claim — what can a purely atemporal state representation do that WYRD cannot?
2. Why must Verðandi be a separate layer rather than a function mapping Urd directly to Skuld? What is lost when the "becoming" is compressed?
3. The append-only invariant of Urd is analogous to blockchain immutability. What are the epistemic advantages of an immutable past? The practical disadvantages?
4. Consider an agent that commits to a future action and then receives new information making the commitment suboptimal. How should WYRD handle this tension?

---

# Lecture 2: The Three Layers — Architectural Deep Dive

## 2.1 The Tripartite World

The central claim of WYRD is that world state must be represented as a triple of structurally distinct components. Consider the difference between knowing that an event has occurred, knowing that an event is occurring, and knowing that an event must occur. These have different epistemic profiles: past knowledge has maximal certainty and zero mutability; present knowledge has partial certainty and high mutability; future knowledge has conditional certainty and moderate mutability. A monolithic state representation must encode all three as the same kind of proposition. WYRD instead gives each its own layer, data structure, and invariants.

## 2.2 Urd: The Past Layer

The Urd layer is an ordered, append-only log of events. Each event has a UUID, type, payload, causal predecessor, timestamp, cryptographic hash, and agent ID. The hash chain links each event to its predecessor (*hash(eᵢ) = H(id ‖ type ‖ payload ‖ cause ‖ timestamp ‖ hash(eᵢ₋₁))*), making the log tamper-evident. The core invariants are:

> **Invariant U1 (Append-Only):** No event, once appended to Ur, may be modified, deleted, or reordered.

> **Invariant U2 (Causal Acyclicity):** The cause relation forms a DAG. No event may be transitively caused by itself.

The Urd layer supports three access patterns: Append (add a new event), Read (retrieve events by index, type, agent, or time range), and Verify (Merkle proof). It does not support random-access mutation, deletion, or reordering.

Core event types include PERCEPTION, ACTION, COMMITMENT_CREATED, COMMITMENT_FULFILLED, COMMITMENT_REVOKED, COMMITMENT_VIOLATED, RECONCILIATION, and RULE_CHANGE. The uniformity of perception and action as events (both are things that happen) simplifies Ve recomputation while preserving the important semantic distinction (the agent field records whether the agent was passive or active).

## 2.3 Verðandi: The Becoming Layer

The Verðandi layer is a *computed state*, not a stored one: *Ve(t) = apply_rules(Ur(t), Rᵥ)*. It can always be recomputed from Ur and the rule set. It is not a mere cache — it represents the epistemically distinct state of "what is currently becoming." Events may have been appended to Ur but not yet integrated into Ve (because the transition cycle has not reached quiescence). This lag is not a bug but a feature: it captures the temporal distance between "has happened" and "is now reflected in the world model."

The Verðandi snapshot is authoritative only at quiescence. Between events, Ve is available for queries but should be treated as tentative.

## 2.4 Skuld: The Future Commitment Layer

The Skuld layer contains commitments of two types:

- **Obligations:** "When condition C becomes true in Ve, action A must be performed." Triggered obligations produce events appended to Ur.
- **Constraints:** "Predicate P must never hold in Ve" or "Predicate P must always hold." A constraint violation is a protocol error.

Commitments have a lifecycle: Creation → Triggering → Fulfillment (for obligations) or Maintenance (for constraints) → Revocation or Expiration. Priority ordering resolves conflicts between competing commitments.

## 2.5 The Transition Cycle

The three layers form a cycle: Urd feeds Ve (through rule application), Ve triggers Skuld (by satisfying conditions), and Skuld feeds back into Urd (by producing obligation events). The cycle continues until quiescence — no further commitments are triggered.

This cycle is the heartbeat of a WYRD-compliant engine. Each "tick" advances the weave by one thread.

### Required Reading

- Sørensen, H., & Lindqvist, E. (2035). "The Urd Log: Append-Only History for Cognitive Agents." *Journal of Artificial General Intelligence*, 7(2), 88–114.
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System." *Communications of the ACM*, 21(7), 558–565.
- Betz, G. (2013). *Debate Dynamics: How Controversy Shapes Our World*. Chapter 3.

### Discussion Questions

1. An agent's Urd log records a perception that is later discovered to be a sensor glitch. How can this be handled without violating the append-only invariant?
2. What happens to quiescence if an obligation's condition is always true? How should the Protocol handle perpetual commitments?
3. Compare the WYRD Skuld layer to "intentions" in the BDI architecture. Key similarities and differences?
4. Under what conditions would an agent be justified in relaxing the cryptographic chain invariant of Urd?

---

# Lecture 3: Urd in Depth — The Well of What Was

## 3.1 The Irreversibility of the Past

The Urd layer is the simplest in concept — a log of events that have happened — and the most philosophically loaded. The decision to make it append-only is a commitment to the position that *what has happened cannot unhappen*. The agent cannot pretend it did not see what it saw. It can only *reconcile* — to add new events that change the meaning of old ones without erasing them.

## 3.2 Event Types and Semantics

The core event types of WYRD v3.2 are:

- **PERCEPTION:** The agent observed something.
- **ACTION:** The agent performed something.
- **COMMITMENT_CREATED/ FULFILLED / REVOKED / VIOLATED:** Lifecycle events for Skuld commitments.
- **RECONCILIATION:** A past event is being superseded by a new interpretation.
- **RULE_CHANGE:** The Verðandi rule set was modified.

The Protocol treats perception and action uniformly as events. The asymmetry (observation vs. agency) is captured in the `agent` field, not in the event structure. This simplifies the rule engine: all events flow through a single pipeline.

## 3.3 The Causal DAG

The `cause` field turns the log from a linear sequence into a directed acyclic graph. If *eᵢ* has `cause = eⱼ`, then *eⱼ* is a causal precondition of *eᵢ*. This DAG supports counterfactual reasoning (trace backward through cause links), responsibility attribution (identify originating events), and reconciliation scope (identify descendants of superseded events).

## 3.4 Logical Time and Timestamps

The `timestamp` field uses logical time (Lamport, 1978), not wall-clock time. Logical time is a monotonically increasing counter that respects causality: if *e₁* causes *e₂*, then *timestamp(e₁) < timestamp(e₂)*. Logical time is agent-local; when agents communicate, they exchange timestamps and update their clocks. Physical time is recorded as payload data, allowing duration reasoning without disrupting causal ordering.

## 3.5 Event Granularity

Event granularity is a key design decision. Fine-grained events (many small events) allow precise causal reasoning but increase storage. Coarse-grained events (few large events) are compact but lose detail. The reference implementation defaults to medium-grained: one event per detected object per perception frame. The Protocol requires only that events be *self-describing* — the type and payload must contain enough information for the rule engine.

## 3.6 Urd as Episodic Memory

Urd also serves as the agent's episodic memory. Queries support explanation generation ("Why did I bring an umbrella? Because event e₄₂ was a perception of rain."), learning (correlate past events to update rules), and self-reflection (summarize the log to extract behavioral patterns). The Urd log is the agent's autobiography — a complete, tamper-evident record of everything that has happened and everything it has done.

## 3.7 Storage and Compaction

The append-only invariant means Urd grows monotonically. WYRD v3.2 introduces two compaction mechanisms:

1. **Snapshotting:** Periodically snapshot Ve and store it alongside Ur. For recomputation, start from the most recent snapshot and replay only subsequent events.
2. **Archival:** Events older than a configurable threshold are moved to a different storage tier. Archived events are still verifiable (their hashes remain in the Merkle chain) but are not loaded during normal recomputation.

### Required Reading

- Sørensen, H., & Lindqvist, E. (2035). "The Urd Log: Append-Only History for Cognitive Agents." *JAGI*, 7(2), 88–114.
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System." *CACM*, 21(7), 558–565.
- Nakamoto, S. (2008). "Bitcoin: A Peer-to-Peer Electronic Cash System."

### Discussion Questions

1. Propose two strategies for managing Urd log size without violating the append-only invariant beyond snapshotting and archival.
2. If logical time is agent-local, how should an agent handle events received from agents with behind clocks?
3. Give concrete examples where fine-grained events would be preferable and where coarse-grained would be preferable.
4. Is the Reconciliation event type sufficient for all types of error, or are there errors it cannot address?

---

# Lecture 4: Verðandi in Depth — What is Becoming

## 4.1 The Present as Process

The Verðandi layer is the most technically complex and philosophically interesting of WYRD's three layers. It sits between the immutable past (Urd) and the committed future (Skuld), representing the current state as it is *becoming* — neither fully settled nor fully determined.

## 4.2 Formal Definition

Ve(t) = apply_rules(Ur(t), Rᵥ) produces a key-value snapshot: {k₁:v₁, k₂:v₂, ..., kₘ:vₘ}. The key property is *determinism*: given the same Ur and Rᵥ, Ve is always the same. No randomness, no hidden state.

## 4.3 The Rule Definition Language

A Verðandi rule has an id, trigger (event type or "always"), condition (predicate on Ve), effect (state update), and priority (for conflict resolution):

```
Rule "r1_move_north" {
  trigger:   ACTION
  condition: payload.action == "move" AND payload.direction == "north"
  effect:    Ve.agent.location.y += 1
  priority:  10
}
```

When multiple rules fire simultaneously, they are applied in priority order (higher first). Ties are broken by lexicographic ID ordering. WYRD allows conflicts rather than forbidding them, because forbidding conflicts entirely makes rule authoring impractical.

## 4.4 Incremental vs. Full Recomputation

Full replay processes every event in Ur through the rules: O(|Ur|) per recomputation. Incremental update applies only rules triggered by the new event: O(|R|) per event. The reference implementation supports both modes: full replay for crash recovery and auditing, incremental for normal operation. Incremental update requires that the deterministic priority/ID ordering produces consistent results regardless of application order — a subtle correctness condition.

## 4.5 State Keys and Namespaces

Verðandi state keys use dot-separated namespaces: `agent.*` (agent state), `world.*` (external world), `other_agents.*` (beliefs about others), `meta.*` (engine state). Namespaces prevent collisions and support namespace-level rule application.

## 4.6 The Semantics of "Becoming"

Why "becoming" rather than "present"? Because the present is not a fixed state — it is a process. During the transition cycle, Ve is in flux. Events have arrived at Ur but are not yet integrated. Skuld obligations have triggered but their action events are not yet processed. The "becoming" captures this in-betweenness. Ve is authoritative only at quiescence; between events, it is tentative.

### Required Reading

- Sørensen, H. (2036). "Verðandi: Deterministic State Derivation from Append-Only Event Logs." *Proceedings of the Symposium on Cognitive Architectures*, 4, 112–130.
- Hellström, T., & Lindqvist, E. (2037). "Rule Priority and Conflict Resolution in the WYRD Protocol." *AI Letters*, 9(1), 34–41.
- Forbus, K. (2019). "Qualitative Process Theory: Revisited." *Artificial Intelligence*, 271, 1–22.

### Discussion Questions

1. WYRD allows rules to conflict and resolves conflicts deterministically. Is this better or worse than forbidding conflicts? What are the trade-offs?
2. Construct a rule set where incremental update produces a different result from full replay. How could the Protocol prevent this?
3. Is the lag between event arrival and Ve integration a feature or a bug? Can it be used productively?
4. What are the storage implications of maintaining both Ur and Ve? When would on-demand derivation be preferable to materialization?

---

# Lecture 5: Skuld in Depth — What Must Be

## 5.1 The Future as Commitment

The Skuld layer is WYRD's most distinctive contribution. While most frameworks treat the future as predictions or probabilities, WYRD treats it as *commitments* — obligations the agent has promised to fulfill and constraints it has promised to maintain. The name, from Old Norse *skuld*, means "debt" or "obligation," and it is also the third Norn, representing what must necessarily come to pass.

This distinction — between what *will* happen (prediction) and what *must* happen (commitment) — is fundamental. An agent's Skuld layer is not a probability distribution over futures. It is a set of *contracts* that the agent has entered into, either with itself (self-imposed goals) or with other agents (social commitments). This makes Skuld a natural substrate for planning, negotiation, and multi-agent coordination.

## 5.2 Obligations: Conditional Actions

An *obligation* is a commitment of the form: "When condition C holds in Ve, perform action A." Formally:

```
Obligation {
  condition:  Predicate     // evaluated against Ve
  action:     Action        // the action to perform
  deadline:   Option<Time>  // optional time constraint
}
```

When the condition becomes true in Ve, the obligation *triggers*: the action is converted into an ACTION event and appended to the Urd log. This is the primary mechanism by which Skuld feeds back into Urd.

Obligations can be *self-imposed* (created by the agent as a personal goal) or *externally imposed* (created by another agent or by the environment as a social commitment). The Skuld layer does not distinguish between these sources — once a commitment is in Skuld, it is binding regardless of origin.

### 5.2.1 Obligation Triggers and Quiescence

A critical subtlety: an obligation triggers when its condition *becomes* true, not when it *is* true. The difference matters in the transition cycle. If condition C was true in Ve(t-1) and remains true in Ve(t), the obligation does *not* trigger again — it has already been discharged. But if condition C was false in Ve(t-1) and becomes true in Ve(t), the obligation triggers.

This "edge-triggered" semantics (borrowed from digital logic design) prevents infinite loops. Without it, a perpetually-true condition would trigger the obligation on every tick, creating an unbounded stream of events and preventing quiescence.

### 5.2.2 Deadline Enforcement

Obligations may optionally have a `deadline`: a logical time by which the action must be performed. If the deadline passes without the action being appended to Ur, the obligation *expires* and a COMMITMENT_VIOLATED event is generated.

Deadline enforcement is checked during the transition cycle. After Ve is recomputed, the engine checks all obligations in Sk against their deadlines (which are expressed in logical time relative to the current Ve). Any obligation whose deadline has passed without fulfillment is flagged as violated.

## 5.3 Constraints: Invariants Over Verðandi

A *constraint* is a commitment of the form: "Predicate P must never hold in Ve" (a safety constraint) or "Predicate P must always hold in Ve" (a liveness constraint). Formally:

```
Constraint {
  predicate:   Predicate      // evaluated against Ve
  kind:        SAFE | LIVE     // safety or liveness
  severity:    Level           // what happens on violation
}
```

Constraint violations are protocol errors. When a constraint is violated, the engine generates a COMMITMENT_VIOLATED event appended to Ur, and the severity level determines what happens next:

- **ADVISORY:** The violation is logged but no action is taken.
- **REMEDIATION:** The violation triggers an obligation to restore the invariant.
- **HALT:** The transition cycle is paused until the violation is resolved.

The severity level is set when the constraint is created and cannot be changed (though the constraint itself can be revoked).

### 5.3.1 Safety vs. Liveness Constraints

Safety constraints ("never P") and liveness constraints ("always P") are duals. In temporal logic, safety properties state that "bad things never happen" and liveness properties state that "good things eventually happen." WYRD's constraint system mirrors this distinction:

- A safety constraint checks that a predicate is *false* after each transition. If it becomes true, the constraint is violated.
- A liveness constraint checks that a predicate is *true* after each transition. If it becomes false, the constraint is violated.

Note: WYRD's liveness constraints are stronger than temporal logic liveness. In temporal logic, "eventually P" allows P to be false for any finite duration and then become true. WYRD's liveness constraints require P to be true *at every quiescent state*. This is closer to "always P" than "eventually P," which is why WYRD calls them "liveness constraints" with some terminological looseness.

## 5.4 Priority and Conflict Resolution

When multiple commitments conflict (e.g., two obligations with contradictory actions, or an obligation whose action would violate a constraint), priority determines the outcome. Each commitment has a `priority` field (an integer), and higher-priority commitments take precedence.

Priority resolution follows these rules:

1. **Constraints always override obligations.** If an obligation's action would violate a constraint, the obligation is *suspended* (not executed) and a COMMITMENT_VIOLATED event is generated.
2. **Among obligations with the same condition and different actions, the one with higher priority fires; the other is discarded.**
3. **If two obligations have the same priority and the same condition, the one with the earlier `created_at` timestamp fires.**
4. **If two constraints conflict (one says "never P" and the other says "always not-P", which is equivalent), they are compatible.** If they genuinely conflict (one says "always P" and the other says "never P"), the higher-priority constraint wins.

## 5.5 Commitment Lifecycle: Complete Specification

1. **Creation:** A commitment is added to Skuld by an ACTION event (the agent commits), a PERCEPTION event (the agent perceives a commitment from another agent), or a RULE_CHANGE event (a rule adds a commitment).
2. **Waiting:** The commitment's condition is checked against Ve after each transition cycle tick. If false, it remains waiting.
3. **Triggered:** When the condition becomes true, the commitment triggers. For obligations, the action is converted to an event and appended to Ur. For constraints (on violation), a COMMITMENT_VIOLATED event is generated.
4. **Fulfilled:** An obligation is fulfilled when its action event appears in Ur. A constraint is maintained as long as it is not violated.
5. **Revoked:** The commitment's creator (or a higher-priority commitment) can revoke it. Revocation generates a COMMITMENT_REVOKED event appended to Ur.
6. **Expired:** If the commitment has an `expires_at` time, it is automatically revoked when that time is reached.

## 5.6 Commitments vs. Intentions: WYRD and BDI

The Skuld layer bears a superficial resemblance to the "Intentions" component of the BDI (Belief-Desire-Intention) architecture (Rao & Georgeff, 1995). Both represent commitments to future action. But there are crucial differences:

- **BDI intentions are desires filtered by commitment.** An intention is a desire that the agent has decided to pursue. Intentions can be dropped if they become impossible or undesirable.
- **WYRD commitments are promises, not desires.** A commitment in Skuld is not something the agent *wants* to do; it is something the agent has *promised* to do. Commitments can be revoked, but revocation is an explicit act with consequences (generating a COMMITMENT_REVOKED event).

This distinction makes Skuld more suitable for multi-agent coordination. When two agents exchange commitments, they are not sharing desires — they are entering into contracts. The COMMITMENT_CREATED and COMMITMENT_FULFILLED events in Ur provide an audit trail of who promised what and whether they delivered.

## 5.7 The Temporal Structure of Commitments

Commitments have a rich temporal structure that mirrors the three layers of WYRD itself:

- A commitment is *created* at a specific point in Urd (when the COMMITMENT_CREATED event is appended).
- A commitment *waits* in Skuld until its condition is satisfied in Ve.
- A commitment is *fulfilled* at a future point in Urd (when the corresponding action event is appended).

This means that a commitment spans all three layers: it is born in Urd, lives in Skuld, and is triggered by Ve. The temporal structure of WYRD is recursive: each commitment is a miniature instance of the past-present-future tripartition.

### Required Reading

- Sørensen, H., & Eriksson, A. (2034). "Skuld: Obligation and Constraint in Temporal World Models." *Proceedings of the Nordic Conference on Artificial Intelligence*, 22, 145–163.
- Rao, A., & Georgeff, M. (1995). "BDI Agents: From Theory to Practice." *Proceedings of ICMAS*, 312–319.
- Castelfranchi, C. (1995). "Commitments: From Individual Intentions to Groups and Organizations." *Proceedings of ICMAS*, 41–48.

### Discussion Questions

1. Edge-triggered obligation semantics prevent infinite loops but also prevent periodic actions (e.g., "check heartbeat every 60 seconds"). How should WYRD support periodic obligations without breaking quiescence guarantees?
2. What is the difference between a liveness constraint ("always P") and a safety constraint ("never not-P")? Are they equivalent? Under what conditions?
3. Constraints always override obligations. Is this the right priority ordering? Give a scenario where an obligation should override a constraint.
4. Compare the WYRD commitment lifecycle to the lifecycle of a legal contract. What parallels and divergences can you identify?

---

# Lecture 6: Branching Futures — The Weave of Possibility

## 6.1 Committed Futures vs. Possible Futures

The Skuld layer represents *committed* futures — things the agent has promised to do or maintain. But WYRD also needs to reason about *possible* futures — things that *could* happen, given the current state and rules, even if no commitment has been made. This lecture addresses how WYRD handles branching futures: the tree of possibilities that unfolds from the current Verðandi state.

The distinction is crucial. Committed futures (Skuld) are *what must happen*. Possible futures are *what could happen*. WYRD does not store possible futures in a separate layer — it computes them on demand from the current state and the rule set. This design choice reflects the Protocol's commitment to determinism: given the same Ur, Ve, and rules, the set of possible futures is always the same.

## 6.2 The Possibility Tree

Given the current world state W(t) = ⟨Ur(t), Ve(t), Sk(t)⟩ and the current rule set Rᵥ, a *possibility tree* is a directed graph where:

- The root is W(t) (the current world state).
- Each node is a world state W(tₖ) reachable from its parent by appending one event to Ur, recomputing Ve, and evaluating Sk.
- Edges are labeled with the event that causes the transition.

The possibility tree is *not* stored anywhere — it is computed on demand by the rule engine. When an agent needs to reason about possible futures (e.g., for planning), it projects the possibility tree to a certain depth, evaluates the outcomes, and prunes branches that are inconsistent with its commitments or goals.

### 6.2.1 Branching Factor and Enumerability

The branching factor of the possibility tree depends on the number of events that could be appended to Ur at the current time. This includes:

- **External events:** Perceptions from the environment (unknown until they occur).
- **Obligation events:** Actions triggered by Skuld commitments (deterministic, once triggered).
- **Agent actions:** Actions the agent could choose to take (the set of available actions).

External events are unknown, so the possibility tree branches over all possible perceptions. This makes the tree very large in practice. WYRD handles this by using a *stochastic pruning* strategy: the agent assigns probabilities to possible perceptions based on its world model and only explores the most likely branches.

## 6.3 From Possibility to Commitment: Planning as Weaving

The process of planning in WYRD can be described as navigating the possibility tree to find a branch that leads to a desired state, and then *committing* to that branch by adding the corresponding actions to Skuld. This is the "weaving" metaphor: the agent explores the loom of possibility, selects a thread, and weaves it into the fabric of commitment.

Formally, planning in WYRD follows this algorithm:

1. **Project:** Compute the possibility tree from the current state to depth d.
2. **Evaluate:** Score each leaf state using a value function (the agent's goals or utility function).
3. **Select:** Choose the branch with the highest expected value.
4. **Commit:** For each action on the selected branch, add an obligation to Skuld with the appropriate condition.
5. **Execute:** As the transition cycle proceeds, the obligations will trigger and the actions will be performed.

This algorithm is similar to forward-chaining planning, but with a crucial difference: the agent commits to actions *before* they are needed, by placing them in Skuld. This means that the agent's future behavior is determined not only by its current state but by its commitments. If a better opportunity arises before a commitment triggers, the agent must decide whether to revoke the commitment (generating a COMMITMENT_REVOKED event) or honor it.

### 6.3.1 Revocation Costs

Every commitment has an implicit *revocation cost*: the cost of going back on a promise. This cost may be:

- **Internal:** The computational cost of generating a COMMITMENT_REVOKED event and re-computing Ve.
- **Social:** If the commitment was made to another agent, revocation may damage trust or incur penalties.
- **Cascading:** If other commitments depend on this one, revocation may trigger a chain of further revocations.

WYRD does not prescribe how to compute revocation costs — it leaves this to the agent's utility function. But it does ensure that every revocation is recorded in the Urd log, providing a complete audit trail.

## 6.4 The Norns' Loom: Branching and the Three Layers

The possibility tree interacts with all three WYRD layers:

- **Urd:** The past determines which branches are accessible. Events that have already occurred close off branches that are no longer possible. For example, if the agent has already perceived rain (Urd contains a PERCEPTION event with `detected: rain`), the branch where it does not rain is closed.
- **Verðandi:** The current state determines the branching factor. The number of possible next events depends on what is true in Ve.
- **Skuld:** Committed futures constrain the possibility tree. An obligation in Skuld means that certain actions *will* be taken when conditions are met, closing off branches where those actions are not taken.

This three-way interaction is the "loom" in its fullest sense: the past (Urd) provides the warp, the present (Verðandi) provides the current shed, and the commitments (Skuld) provide the pattern that the weaver intends to produce. The possibility tree is the space between the threads — the weft that the weaver has not yet chosen.

## 6.5 Multi-Agent Branching

When multiple agents share a world, their possibility trees intertwine. Each agent has its own Urd log, its own Ve, and its own Skuld, but they share a world state. Agent A's actions affect Agent B's perceptions and vice versa.

WYRD v3.2 introduces *loom composition* for multi-agent settings. Each agent maintains its own WYRD triple, but the Verðandi layers are synchronized through shared state updates. When Agent A takes an action, the ACTION event is appended to A's Urd log, and a corresponding PERCEPTION event is appended to B's Urd log. This ensures that both agents' Ve layers remain consistent with the shared world state.

We cover multi-agent loom composition in detail in Lecture 12.

## 6.6 Branching and Quiescence Revisited

In Lecture 2, we defined quiescence as the state where no further Skuld commitments are triggered. But branching futures introduce a subtlety: even at quiescence, the possibility tree has branches that have not been explored. Quiescence means that the current state is stable — not that there are no possible futures to consider.

Analogically, quiescence is like the weaver pausing at the loom: the threads are in a stable configuration, but the weave could continue in many directions. The next thread to be woven is the agent's choice, informed by its goals and its evaluation of the possibility tree.

### Required Reading

- Sørensen, H., & Lindqvist, E. (2036). "Branching Futures in the WYRD Protocol: From Possibility to Commitment." *AI Letters*, 8(2), 77–92.
- Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*, 4th ed. Chapter 11 on planning and Chapter 14 on probabilistic reasoning.
- Castelfranchi, C., & Falcone, R. (1998). "Principles of Trust for MAS: Cognitive Anatomy of Trust." *Proceedings of ICMAS*, 72–79.

### Discussion Questions

1. The possibility tree branches over all possible perceptions, making it very large. Propose at least two strategies for pruning the tree without losing important branches.
2. If an agent commits to a branch and then discovers a better branch, should it revoke the commitment? What factors should influence this decision?
3. How does multi-agent branching interact with commitment? If Agent A commits to an action that affects Agent B's possibility tree, should Agent B be notified?
4. Compare WYRD's possibility tree to the search tree in classical planning (e.g., A* search). What are the key similarities and differences?

---

# Lecture 7: Contradictory History Reconciliation — The Norn's Judgment (Part I)

## 7.1 The Problem: When the Past is Wrong

A fundamental invariant of WYRD is that the Urd log is append-only: no event, once appended, may be modified or deleted. This invariant ensures auditability and tamper-evidence. But it creates a problem: what happens when an event in the Urd log is *wrong*?

Consider the following scenario: An agent's camera perceives a red ball (PERCEPTION event appended to Ur). The agent takes action based on this perception — it reaches for the ball. Then, a second perception reveals that the "red ball" was actually a shadow (PERCEPTION event with corrected information). The first perception is still in the Ur log, but the agent now knows it was wrong.

In a traditional world model, the agent would simply update its belief: "the object is a shadow, not a red ball." But in WYRD, beliefs are derived from Ur via Ve. The first perception event is in Ur, and the rule set will derive "there is a red ball" from it. How can the agent correct this without deleting the event?

This is the problem of *contradictory history reconciliation*, and it is the hardest problem in WYRD. The Protocol's solution — the "Norn's Judgment" — is the subject of this lecture and the next.

## 7.2 Reconciliation Events

WYRD v3.0 introduced a new event type: RECONCILIATION. A reconciliation event has the following schema:

```
ReconciliationEvent {
  id:                UUID
  type:              RECONCILIATION
  superseded:        UUID            // the event being corrected
  interpretation:    String          // why the original event was wrong
  corrected:         Event           // the corrected version of the event
  timestamp:         LogicalTime
  hash:              CryptoHash
  agent:             AgentID
}
```

A reconciliation event says: "Event X was wrong because of Y, and the correct interpretation is Z." It does not delete event X — it *superscedes* it, adding new information that changes how X is interpreted by the rule engine.

## 7.3 How Reconciliation Works in the Verðandi Layer

When a reconciliation event is appended to Ur, the rule engine treats it as follows:

1. The reconciliation event is processed like any other event: it triggers rules that match its type (RECONCILIATION).
2. The standard rule for RECONCILIATION events is: "When a RECONCILIATION event supersedes event X, re-process event X's effects with the corrected data."

This is implemented in the rule set as:

```
Rule "r_reconcile" {
  trigger:   RECONCILIATION
  condition: true
  effect:    Ve = reprocess(Ve, event.superseded, event.corrected)
  priority:  MAX_PRIORITY  // reconciliation always takes precedence
}
```

The `reprocess` function identifies all state changes in Ve that were derived from the superseded event, undoes them, and applies the corrected event's data instead. This is a form of *selective replay*: the engine re-derives the affected portions of Ve without re-deriving the entire state.

## 7.4 The Cascade Problem

Reconciliation of a single event is straightforward. But reconciliations can cascade: if the superseded event caused other events (via Skuld obligations), those events may also need to be reconciled. Consider:

1. Event e₁: PERCEPTION → "red ball detected"
2. Event e₂: COMMITMENT_CREATED → "obligation to reach for the ball" (triggered by e₁ via a Skuld rule)
3. Event e₃: ACTION → "reach for the ball" (triggered by the obligation from e₂)
4. Event e₄: PERCEPTION → "shadow detected, not a ball" (contradicts e₁)
5. Event e₅: RECONCILIATION → supersedes e₁ with "shadow detected"

The reconciliation of e₁ (event e₅) should also affect e₂ and e₃, because they were caused by e₁. This is the *cascade problem*: a reconciliation event may need to propagate through the causal DAG to affect all downstream events.

WYRD's approach to cascade reconciliation uses the causal DAG (the `cause` field in each event). When a reconciliation event supersedes event X, the engine:

1. Identifies all events in Ur that are causal descendants of X (using the DAG).
2. For each causal descendant, checks whether it was directly caused by the superseded event or only indirectly.
3. Directly caused events are *marked for re-evaluation*: their effects are re-derived using the corrected data.
4. Indirectly caused events are examined further to determine if they need re-evaluation.

This cascade is bounded by the depth of the causal DAG. In practice, most reconciliations affect only a small number of downstream events, because the causal chains in a typical Urd log are short.

## 7.5 Reconciliation and Quiescence

Reconciliation events are processed during the transition cycle, just like any other event. This means that a reconciliation can trigger Skuld commitments: if the corrected state satisfies a commitment condition that the original state did not, the commitment will fire.

However, reconciliations can also *un-trigger* commitments: if the original state triggered an obligation that the corrected state does not, the obligation should not have fired. But the obligation's action has already been appended to Ur as an event — and that event cannot be deleted.

WYRD handles this by generating a *counter-event*: an event that undoes the effect of the erroneously triggered obligation. For example, if an obligation to "send an evacuation notification" was triggered by a false alarm (a misperception of fire), and the misperception is later reconciled, the counter-event would be "cancel evacuation notification" — appended to Ur as a new event.

This approach preserves the append-only invariant (the original "send" event remains in Ur) while correcting the world state (the "cancel" event undoes its effect). It is analogous to accounting: you don't erase a transaction; you post a reversing entry.

## 7.6 Formal Properties of Reconciliation

The WYRD Protocol guarantees the following formal properties for reconciliation:

- **Consistency:** After reconciliation, Ve is consistent with the corrected data — it is as if the superseded event had never occurred (or rather, had occurred in its corrected form).
- **Completeness:** All causal descendants of the superseded event are re-evaluated.
- **Auditability:** The original event, the reconciliation event, and any counter-events are all present in Ur, providing a complete audit trail.
- **Termination:** The reconciliation cascade terminates, because the Urd log is finite and no reconciliation event can supersede itself (by the acyclicity invariant).

### Required Reading

- Sørensen, H., & Eriksson, A. (2035). "The Norn's Judgment: Contradictory History Reconciliation in the WYRD Protocol." *Proceedings of the Symposium on Cognitive Architectures*, 3, 201–219.
- Strom, R., et al. (2012). "Eventual Consistency." *Synthesis Lectures on Data Management*, 4(5), 1–141. (For context on reconciliation in distributed systems.)
- Brachman, R., & Levesque, H. (2004). *Knowledge Representation and Reasoning*. Chapter 4 on belief revision.

### Discussion Questions

1. The cascade problem can cause a reconciliation to affect many downstream events. What are the computational costs? How can they be bounded?
2. The counter-event approach preserves the append-only invariant but leaves a "scar" in the Urd log (both the original event and the counter-event are present). Is this a feature or a bug? What are the implications for auditing?
3. What happens if two reconciliation events contradict each other (each superseding the same original event with different corrections)? How should the Protocol handle this?
4. Compare WYRD's reconciliation approach to the AGM belief revision operators (Alchourrón, Gärdenfors, and Makinson, 1985). What are the key similarities and differences?

---

# Lecture 8: Contradictory History Reconciliation — The Norn's Judgment (Part II)

## 8.1 Advanced Reconciliation Scenarios

In Lecture 7, we covered the basics of reconciliation: a single event is superseded by a reconciliation event, and the cascade propagates through the causal DAG. This lecture covers advanced scenarios that make reconciliation more complex: multiple simultaneous reconciliations, self-referential reconciliations, and reconciliation in multi-agent settings.

## 8.2 Multiple Simultaneous Reconciliations

What happens when two or more events in Ur need to be reconciled at the same time? For example, the agent receives two corrected perceptions in rapid succession:

- Event e₄: PERCEPTION → "shadow detected, not a ball"
- Event e₅: PERCEPTION → "actually, it's a red ball after all, just partly occluded"

In this case, e₅ reconciles the reconciliation (e₄ supersedes e₁; e₅ supersedes e₄'s interpretation). WYRD handles this by processing reconciliations in the order they appear in the Urd log. Each reconciliation event triggers a cascade, and the next reconciliation event is processed against the already-reconciled state.

The formal guarantee is:

> **Reconciliation Monotonicity:** If event eᵢ is reconciled before event eⱼ, and both supersede the same original event eₖ, then the final Verðandi state is determined by the later reconciliation (eⱼ), not the earlier one (eᵢ).

This ensures that reconciliations are "last writer wins" with respect to any given original event. If multiple corrections are issued for the same event, only the most recent one is effective.

## 8.3 Self-Referential Reconciliations and the Acyclicity Invariant

Can a reconciliation event supersede itself? The WYRD Protocol forbids this via the Causal Acyclicity Invariant (U2). A reconciliation event cannot supersede itself, nor can it supersede an event that was caused by the reconciliation's own correction. This prevents infinite loops.

But what about *indirect* self-reference? Consider:

- e₁: PERCEPTION → "object is a cat"
- e₂: RECONCILIATION → supersedes e₁, corrected to "object is a dog"
- e₃: PERCEPTION → "on closer inspection, it's actually a cat"
- e₄: RECONCILIATION → supersedes e₂, corrected back to "object is a cat"

This is not a circular reconciliation — each event supersedes a different original event. But the final state is the same as the initial state, which seems wasteful. WYRD does not optimize for this case, because it is rare and because the audit trail is valuable: e₁, e₂, e₃, and e₄ together tell the story of how the agent's understanding of the object evolved.

## 8.4 Reprocessing Strategies

When a reconciliation event triggers a cascade, the engine must re-derive the affected portion of Ve. There are two strategies:

1. **Full Replay:** After a reconciliation, re-derive Ve from scratch by replaying all events in Ur. This is correct but expensive — O(|Ur|).

2. **Selective Replay:** After a reconciliation, identify the events affected by the cascade and re-derive only the affected portions of Ve. This is more efficient but requires maintaining a dependency graph between events and Ve state keys.

The reference implementation uses selective replay by default, with a fallback to full replay if the dependency graph is corrupted or unavailable.

### 8.4.1 The Dependency Graph

The dependency graph is a mapping from Ve state keys to the events that contributed to their current values. When a reconciliation affects event X, the engine:

1. Looks up all state keys that depend on X (via the dependency graph).
2. Re-derives those state keys by replaying the events that contribute to them, using the corrected data.
3. Checks for cascade effects: if any of the re-derived state keys trigger Skuld commitments that were not previously triggered, it generates counter-events for any erroneously triggered obligations.

The dependency graph is maintained incrementally: each time a rule fires and modifies a state key, the engine records which event triggered the rule and which state keys were affected. This makes selective replay efficient at the cost of maintaining additional metadata.

## 8.5 Reconciliation in Multi-Agent Settings

When multiple agents share a world, reconciliation becomes more complex. Agent A's reconciliation may affect Agent B's world state, and vice versa. WYRD v3.2 specifies a *reconciliation propagation protocol* for this case:

1. When Agent A generates a reconciliation event, it appends it to its own Ur log.
2. A *propagation event* (a special type of PERCEPTION) is sent to all agents whose Ve may be affected.
3. Each receiving agent processes the propagation event, checks whether its Ve depends on the superseded event, and if so, re-derives the affected portion of its Ve.
4. If the reconciliation affects any Skuld commitments, the agent generates counter-events and propagates them to other affected agents.

This protocol is not guaranteed to produce a globally consistent state — it is *eventually consistent* (in the sense of distributed systems). Globally consistent reconciliation would require a distributed transaction protocol, which WYRD v3.2 does not specify (it is an open research topic).

## 8.6 The Norn's Judgment: Naming the Process

The reconciliation process is called the "Norn's Judgment" in WYRD terminology, after the Norns who sit at the well of Urd and decide the fates of gods and mortals. The metaphor is precise: when the past is wrong, the Norns must judge how to correct it. They cannot undo the past (the append-only invariant), but they can reinterpret it (the reconciliation event) and adjust the weave accordingly (the cascade and counter-events).

The Norn's Judgment is not a punishment or an erasure. It is a reinterpretation — a new way of reading the old threads. The original event remains in the Urd log, a reminder that the past cannot be changed, only understood differently. The reconciliation event sits beside it, a new thread that changes the meaning of the old one without erasing it.

This is the deepest lesson of the WYRD Protocol: the past is immutable, but our understanding of it is not. The weave can be corrected, but the original threads remain.

### Required Reading

- Sørensen, H., & Eriksson, A. (2035). "The Norn's Judgment: Contradictory History Reconciliation in the WYRD Protocol." *Proceedings of the Symposium on Cognitive Architectures*, 3, 201–219.
- Alchourrón, C., Gärdenfors, P., & Makinson, D. (1985). "On the Logic of Theory Change: Partial Meet Contraction and Revision Functions." *Journal of Symbolic Logic*, 50(2), 510–530.
- Gilbert, H., & Malkhi, D. (2019). "Append-Only Ledgers and Their Applications." *Distributed Computing*, 6, 44–59.

### Discussion Questions

1. Multiple reconciliations of the same event follow "last writer wins" semantics. Is this the best strategy? What alternatives exist, and what are their trade-offs?
2. The acyclicity invariant prevents self-referential reconciliations. But what if an agent's understanding of an event changes gradually over time, with each new perception slightly modifying the previous interpretation? How should WYRD handle this?
3. Selective replay requires maintaining a dependency graph. What are the space and time costs? Are there situations where selective replay is worse than full replay?
4. The reconciliation propagation protocol is eventually consistent but not globally consistent. What are the practical implications of this limitation for multi-agent systems?

---

# Lecture 9: Event Sourcing in WYRD — Threading the Past

## 9.1 Introduction: From Event Logs to World Models

Event sourcing is a well-established pattern in software engineering: instead of storing the current state of a system, store the sequence of events that led to that state. The current state can then be reconstructed by replaying the events from the beginning. WYRD's Urd layer is, at its core, an event-sourced log — but it extends the pattern in several important ways.

This lecture covers event sourcing as it is implemented in WYRD, the relationship between Urd and traditional event-sourcing systems, the challenges of event sourcing for cognitive agents, and the practical considerations involved in building a production-quality Urd log.

## 9.2 Event Sourcing: A Brief Primer

The core idea of event sourcing is simple: state is a function of history. Rather than storing a snapshot of the world, store the events that produced it. The snapshot can be reconstructed at any time by replaying the events.

Traditional event sourcing (as practiced in enterprise systems) focuses on consistency, auditability, and temporal queries. A bank account, for example, might store every transaction (deposit, withdrawal, transfer) rather than just the current balance. The balance can be computed by summing all transactions, and any past balance can be computed by summing transactions up to a given date.

WYRD's event sourcing extends this pattern in three ways:

1. **Cryptographic chaining:** Each event in the Urd log is linked to its predecessor by a hash, forming a Merkle chain. This provides tamper-evidence, which is not typically required in enterprise event sourcing.

2. **Causal structure:** The `cause` field in each event forms a causal DAG, not just a linear sequence. This enables counterfactual reasoning and reconciliation — capabilities that traditional event sourcing does not need.

3. **Tripartite architecture:** The Urd log is not the only data structure; it is one of three layers (Urd, Verðandi, Skuld) that must be kept in sync. This makes the WYRD event-sourcing system more complex than traditional ones, but also more expressive.

## 9.3 The Urd Log as an Event Store

The Urd log is an append-only, cryptographically chained, causally structured event store. Each event has a well-defined schema (see Lecture 3) and is linked to its predecessor by a hash. The log supports three operations:

1. **Append:** Add a new event to the end of the log.
2. **Read:** Retrieve events by index, type, agent, time range, or causal link.
3. **Verify:** Given a root hash and an event, prove that the event is part of the log.

These operations correspond to the three core guarantees of the Urd log:

- **Integrity:** The log has not been tampered with (verified by the Merkle chain).
- **Completeness:** No events have been removed (verified by the append-only invariant and the hash chain).
- **Causality:** The causal relationships between events are explicit (verified by the `cause` field and the DAG structure).

## 9.4 Snapshotting and Compaction

As the Urd log grows, replaying all events to reconstruct Ve becomes increasingly expensive. WYRD v3.2 introduces two compaction mechanisms:

### 9.4.1 Periodic Snapshots

The engine periodically takes a snapshot of Ve and stores it alongside the Urd log. A snapshot contains:

```
Snapshot {
  timestamp:   LogicalTime     // the logical time of the snapshot
  ve_state:    Map<StateKey, Value>  // the Ve snapshot
  ur_hash:     CryptoHash      // the hash of the last event in Ur at snapshot time
  sk_state:    Set<Commitment> // the set of active commitments at snapshot time
}
```

To reconstruct Ve from a snapshot, the engine starts from the snapshot and replays only the events that occurred after the snapshot's logical time. This reduces the cost of Ve recomputation from O(|Ur|) to O(|Ur| - |snapshot_point|).

### 9.4.2 Archival Storage

Events older than a configurable threshold can be moved to an archival store. Archival events are still verifiable (their hashes are included in the Merkle chain), but they are not loaded during normal Ve recomputation. Archival events are only accessed when:

- An audit requires the complete history.
- A reconciliation event supersedes an archived event.
- A query explicitly requests historical data.

Archival is not deletion. The append-only invariant requires that archived events remain accessible and verifiable. They are simply stored in a different tier (e.g., cold storage) with higher access latency.

## 9.5 Eventual Consistency in Distributed Settings

In a multi-agent system, each agent maintains its own Urd log. When agents interact, they exchange events: Agent A's actions become perceptions in Agent B's Urd log, and vice versa. This raises the question of consistency: how can we ensure that two agents' world models are consistent when they have different Urd logs?

WYRD v3.2 adopts an *eventual consistency* model: each agent's Ve is consistent with its own Urd log, but there is no guarantee that two agents' Ve layers are identical at any given moment. Instead, the Protocol guarantees that if two agents' Urd logs converge (i.e., they contain the same set of events), then their Ve layers will also converge.

This eventual consistency model has practical implications:

- **Staleness:** When Agent A sends a message to Agent B, there is a lag between the time the message is sent and the time it is received and processed. During this lag, the two agents' Ve layers may differ.
- **Conflict:** If two agents take conflicting actions simultaneously (e.g., both try to pick up the same object), the conflict is detected when their events are merged into a shared context. WYRD does not specify a conflict resolution protocol for this case — it is left to the application layer.
- **Reconciliation propagation:** As discussed in Lecture 8, when Agent A generates a reconciliation event, it must propagate the event to all affected agents. The propagation protocol is eventually consistent: there is a lag between when Agent A reconciles and when Agent B processes the reconciliation.

## 9.6 The Urd Log as a Substrate for Learning

Beyond its role in Ve recomputation, the Urd log serves as a substrate for machine learning. The agent can mine its own history for patterns:

- **Rule induction:** The agent can examine the Urd log to discover regularities — e.g., "whenever I perceive rain, I later get wet" — and use these to create new Verðandi rules or Skuld commitments.
- **Behavioral analysis:** The agent can summarize its own actions over time, identifying habitual patterns and making deliberate changes.
- **Counterfactual analysis:** The agent can explore "what if" scenarios by temporarily modifying events in the Urd log, recomputing Ve, and observing the difference. This is a form of *causal learning* that leverages the causal DAG structure of Urd.

The Urd log is not just a record of what happened — it is a resource for understanding why it happened and what could have happened differently.

## 9.7 Practical Implementation Considerations

### 9.7.1 Storage Format

The reference implementation stores each event as a JSON object in a flat file. Each event is serialized as a single line, and the file is appended to using atomic write operations to ensure crash safety. The hash chain is verified on startup.

For high-performance applications, the reference implementation also supports a binary format (Protocol Buffers) and a columnar format (Apache Parquet) for efficient time-range queries.

### 9.7.2 Indexing

The Urd log is indexed by event type, agent ID, and time range. These indexes are stored as separate files and updated incrementally as new events are appended. The reference implementation uses skip lists for O(log n) insertion and O(log n) lookup.

### 9.7.3 Concurrency

The Urd log must support concurrent reads and sequential writes. The reference implementation uses a single-writer, multiple-reader lock: only one thread can append at a time, but any number of threads can read. This is sufficient for single-agent settings; multi-agent settings require distributed consensus, which is an active research topic.

### Required Reading

- Betts, D., et al. (2012). "Event Sourcing." *Microsoft Patterns and Practices*, 1–32.
- Hellström, T., & Sørensen, H. (2036). "Event Sourcing for Cognitive Agents: The Urd Log in Practice." *Journal of Agent Systems*, 14(3), 201–228.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. Chapter 11 on event sourcing and change data capture.

### Discussion Questions

1. The reference implementation uses a flat file for event storage. What are the trade-offs of using a database instead? Under what conditions would a database be preferable?
2. Archival storage moves old events to a different tier but keeps them accessible. What are the security implications of this approach? How should access controls be implemented for archived events?
3. WYRD's eventual consistency model means that two agents' Ve layers may differ at any given moment. What are the practical implications of this for multi-agent coordination?
4. How can the Urd log be used for causal learning? Propose a concrete algorithm for rule induction from the Urd log.

---

# Lecture 10: World State Engine Implementation — Building the Loom

## 10.1 Introduction: From Theory to Practice

Lectures 1–9 covered the WYRD Protocol's theoretical foundations. This lecture and the next shift to implementation: how to build a WYRD-compliant world state engine that maintains Urd, computes Verðandi transitions, manages Skuld commitments, and reconciles contradictory histories.

The course project requires you to implement such an engine in your programming language of choice. This lecture provides a reference architecture, implementation strategies, and practical guidance.

## 10.2 Architecture Overview

A WYRD world state engine has five components:

1. **Urd Store:** The append-only cryptographic event log.
2. **Verðandi Engine:** The rule application engine that derives Ve from Ur and Rᵥ.
3. **Skuld Manager:** The commitment lifecycle manager that evaluates conditions and triggers actions.
4. **Transition Controller:** The component that drives the transition cycle (appending events, recomputing Ve, evaluating Skuld commitments, and checking for quiescence).
5. **Reconciliation Engine:** The component that handles RECONCILIATION events, propagates cascades, and generates counter-events.

```
┌──────────────────────────────────────────────────┐
│                 Transition Controller            │
│  (drives the transition cycle, checks quiescence)│
├──────────┬──────────────────┬────────────────────┤
│          │                  │                    │
│  Urd     │  Verðandi        │  Skuld             │
│  Store   │  Engine          │  Manager           │
│          │                  │                    │
│ (append- │ (applies rules   │ (evaluates         │
│  only    │  to derive Ve)   │  commitments,      │
│  event   │                  │  triggers         │
│  log)    │                  │  obligations)      │
│          │                  │                    │
├──────────┴──────────────────┴────────────────────┤
│          Reconciliation Engine                      │
│  (handles RECONCILIATION events, cascade,          │
│   counter-events)                                   │
└────────────────────────────────────────────────────┘
```

## 10.3 The Urd Store: Implementation

### 10.3.1 Data Structure

The Urd store is an append-only log of events, each with a hash linked to its predecessor. The reference implementation uses a flat file with one event per line (JSON serialization). New events are appended atomically.

```python
class UrdStore:
    def __init__(self):
        self.events = []        # list of Event objects
        self.index = {}         # type -> [Event], agent -> [Event], etc.
        self.hash_chain = {}    # id -> hash
        self.last_hash = GENESIS_HASH

    def append(self, event):
        event.hash = compute_hash(event, self.last_hash)
        self.events.append(event)
        self.hash_chain[event.id] = event.hash
        self.last_hash = event.hash
        self._update_index(event)

    def verify(self, event_id):
        """Verify that an event is part of the hash chain."""
        # Walk the chain from the event to the tip
        # If any hash is invalid, return False
        # Otherwise, return True
        pass

    def query(self, type=None, agent=None, time_range=None):
        """Retrieve events matching the given criteria."""
        # Use indexes for efficient queries
        pass
```

### 10.3.2 Hash Chain

Each event's hash is computed as `SHA-256(id || type || payload || cause || timestamp || previous_hash)`. The genesis event (the first event in the log) has `previous_hash = 0` (a sentinel value).

The hash chain provides integrity: any tampering with an event invalidates all subsequent hashes. The hash chain also provides inclusion proofs: to verify that event eᵢ is part of the log, walk the chain from eᵢ to the tip and check that all hashes are valid.

### 10.3.3 Persistence and Crash Recovery

The Urd store must survive crashes. The reference implementation uses write-ahead logging: each event is written to the log file before it is added to the in-memory data structure. On startup, the engine reads the log file to reconstruct the in-memory state. If the engine crashes during startup, the log file is replayed from the beginning.

For large logs, periodic snapshots of the Verðandi state are stored alongside the log. On startup, the engine loads the most recent snapshot and replays only subsequent events.

## 10.4 The Verðandi Engine: Implementation

### 10.4.1 Rule Application

The Verðandi engine derives the current state from the Urd log and the rule set. The `apply_rules` function processes each event in the Urd log, applies matching rules, and produces the current Ve snapshot.

```python
def apply_rules(urd_log, rules, initial_state=None):
    """Derive Ve from Ur and rules."""
    if initial_state is None:
        ve = {}  # start from empty state
    else:
        ve = dict(initial_state)  # start from snapshot

    for event in urd_log:
        for rule in sorted(rules, key=lambda r: (-r.priority, r.id)):
            if rule.trigger == event.type or rule.trigger == "always":
                if rule.condition(event, ve):
                    ve = rule.effect(event, ve)

    return ve
```

Rules are applied in priority order (higher priority first), with ties broken by lexicographic ID ordering. This ensures deterministic performance regardless of insertion order.

### 10.4.2 Incremental Update

For normal operation, the engine uses incremental update: when a new event arrives, only the rules that match the event's type are considered. This reduces the per-event cost from O(|Ur| × |R|) to O(|R(evt_type)|), where R(evt_type) is the set of rules matching the event's type.

```python
def incremental_update(ve, event, rules):
    """Update Ve incrementally based on a new event."""
    for rule in sorted(rules, key=lambda r: (-r.priority, r.id)):
        if rule.trigger == event.type or rule.trigger == "always":
            if rule.condition(event, ve):
                ve = rule.effect(event, ve)
    return ve
```

### 10.4.3 Dependency Tracking

For selective replay during reconciliation, the engine maintains a dependency graph: a mapping from Ve state keys to the events and rules that contributed to their current values.

```python
class DependencyGraph:
    def __init__(self):
        self.key_to_events = {}  # StateKey -> set of event IDs
        self.key_to_rules = {}   # StateKey -> set of rule IDs

    def record(self, state_key, event_id, rule_id):
        self.key_to_events.setdefault(state_key, set()).add(event_id)
        self.key_to_rules.setdefault(state_key, set()).add(rule_id)

    def affected_keys(self, event_id):
        """Return all state keys that depend on the given event."""
        return {k for k, events in self.key_to_events.items() if event_id in events}
```

When a reconciliation affects event X, the engine uses the dependency graph to identify affected state keys and re-derive only those keys, rather than replaying the entire Urd log.

## 10.5 The Skuld Manager: Implementation

### 10.5.1 Commitment Lifecycle

The Skuld manager maintains the set of active commitments and evaluates them after each transition cycle tick.

```python
class SkuldManager:
    def __init__(self):
        self.commitments = {}   # commitment_id -> Commitment

    def add_commitment(self, commitment):
        self.commitments[commitment.id] = commitment
        # Append COMMITMENT_CREATED event to Urd

    def evaluate(self, ve, urd_append):
        """Evaluate all commitments against the current Ve."""
        triggered_obligations = []
        violated_constraints = []

        for commitment in self.commitments.values():
            if commitment.type == OBLIGATION:
                if commitment.condition(ve) and not commitment.was_triggered:
                    triggered_obligations.append(commitment)
                    commitment.was_triggered = True
            elif commitment.type == CONSTRAINT:
                if commitment.kind == SAFE:
                    if commitment.predicate(ve):  # violation: predicate should be False
                        violated_constraints.append(commitment)
                elif commitment.kind == LIVE:
                    if not commitment.predicate(ve):  # violation: predicate should be True
                        violated_constraints.append(commitment)

        # Process triggered obligations
        for obligation in triggered_obligations:
            urd_append(obligation.action.to_event())

        # Process violated constraints
        for constraint in violated_constraints:
            urd_append(Event(type=COMMITMENT_VIOLATED,
                            payload={"commitment_id": constraint.id,
                                      "constraint": str(constraint.predicate)}))

        return len(triggered_obligations) + len(violated_constraints) > 0
```

### 10.5.2 Edge-Triggered Semantics

Note the `was_triggered` flag in the obligation evaluation. This implements edge-triggered semantics: an obligation triggers when its condition *becomes* true, not when it *is* true. The flag is reset when the condition becomes false (allowing the obligation to trigger again if the condition re-enters the true state).

## 10.6 The Transition Controller: Implementation

The transition controller drives the main loop:

```python
def transition_cycle(urd_store, verdandi_engine, skuld_manager, rules):
    """Run the transition cycle until quiescence."""
    while True:
        # Recompute Ve from Ur and rules
        ve = verdandi_engine.apply_rules(urd_store, rules)

        # Evaluate Skuld commitments
        any_triggered = skuld_manager.evaluate(
            ve, urd_store.append)

        # Check for quiescence
        if not any_triggered:
            break

    return ve
```

This loop continues until no further commitments are triggered. The quiescence guarantee requires that the commitment set contains no unbounded obligation chains — i.e., no cycle of obligations that keep triggering each other indefinitely.

### 10.6.1 Quiescence Guarantee

The quiescence guarantee is formalized as follows:

> **Quiescence Guarantee:** If the Skuld set contains no cycles of obligations where each obligation's trigger condition is satisfied by the previous obligation's action, then the transition cycle will terminate.

This is equivalent to requiring that the dependency graph of obligation triggers has no cycles. The engine can detect potential non-termination by checking for cycles in the trigger dependency graph when commitments are added.

## 10.7 The Reconciliation Engine: Implementation

The reconciliation engine handles RECONCILIATION events by propagating corrections through the causal DAG:

```python
class ReconciliationEngine:
    def __init__(self, urd_store, verdandi_engine, skuld_manager, dep_graph):
        self.urd_store = urd_store
        self.verdandi_engine = verdandi_engine
        self.skuld_manager = skuld_manager
        self.dep_graph = dep_graph

    def reconcile(self, reconciliation_event):
        """Process a RECONCILIATION event."""
        superseded_id = reconciliation_event.payload["superseded"]

        # Find all causal descendants of the superseded event
        descendants = self.urd_store.find_causal_descendants(superseded_id)

        # Find all state keys affected by the superseded event and its descendants
        affected_keys = set()
        for event_id in [superseded_id] + descendants:
            affected_keys.update(self.dep_graph.affected_keys(event_id))

        # Re-derive affected state keys using selective replay
        corrected_event = reconciliation_event.payload["corrected"]
        # ... (selective replay logic)

        # Generate counter-events for any erroneously triggered obligations
        # ... (counter-event generation logic)

        # Resume the transition cycle
        self.verdandi_engine.transition_cycle(
            self.urd_store, self, self.skuld_manager)
```

### Required Reading

- Hellström, T., & Sørensen, H. (2037). "Building the Loom: A Reference Architecture for WYRD-Compliant World State Engines." *Software Engineering for Cognitive Systems*, 2(1), 45–72.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. Chapters 5 and 11.
- Fowler, M. (2019). "Event Sourcing." *martinfowler.com*. Available at: https://martinfowler.com/eaaDev/EventSourcing.html

### Discussion Questions

1. The reference implementation uses a flat file for the Urd store. What are the trade-offs of using a database? Under what conditions would a database be preferable?
2. The quiescence guarantee requires no cycles in the obligation trigger dependency graph. How can the engine detect cycles when commitments are added? What should it do if a cycle is detected?
3. The incremental update algorithm assumes that rules are order-independent given the priority tiebreaker. Construct a rule set where this assumption fails. How should the engine handle this case?
4. The reconciliation engine uses selective replay by default. What are the failure modes of selective replay, and how should the engine detect and recover from them?

---

# Lecture 11: The Norns and the Loom Metaphor — Mythology as Architecture

## 11.1 Introduction: Why Mythology?

Throughout this course, we have used the metaphor of the Norns and the loom to explain WYRD's architecture. This lecture examines the metaphor in detail: where it illuminates, where it breaks down, and what it teaches us about the relationship between narrative structure and computational architecture.

Why use mythology at all? Computer science has a rich tradition of metaphor — from "memory" to "garbage collection" to "daemon" — but these metaphors are typically shallow labels. The WYRD Protocol's use of Norse mythology goes deeper: the Norns are not just names for layers; their attributes and relationships in the mythological sources map directly onto the Protocol's design decisions.

## 11.2 Urd: The Well and the Log

In the Eddic sources, Urd (*Urðr*) is the eldest of the three Norns. Her name means "fate" or "that which has come to pass." She sits by the well of Urd at the base of Yggdrasil, drawing water from the well and pouring it on the roots of the World Tree.

The mapping to WYRD is precise:

- The well of Urd is the Urd log: a deep reservoir of everything that has happened.
- The act of drawing water is event retrieval: the engine reads events from the log.
- The act of pouring water on the roots is event processing: the engine applies events to the Verðandi layer.
- The roots of Yggdrasil are the causal DAG: events flow from the well into the tree, just as events in the Urd log propagate through the causal structure of the world model.
- The water itself is the information: just as water nourishes the tree, events nourish the Verðandi layer, transforming it from an empty state into a rich model of the world.

But the metaphor also reveals a limitation. In the mythology, the well of Urd is a passive reservoir — the Norns draw from it, but they do not add to it. In WYRD, the Urd log is actively appended to by the agent's perceptions, actions, and commitments. The agent is both a weaver and a contributor to the well: it draws from Urd to compute Ve, and it adds to Urd when it takes actions.

## 11.3 Verðandi: The Becoming and the Present Thread

Verðandi (*Verðandi*) is the second Norn. Her name means "becoming" or "that which is happening." In the mythology, she is the Norn of the present — the one who spins the thread of the present moment.

The mapping to WYRD is instructive:

- Verðandi's spinning is the rule application process: the Verðandi engine takes events from Urd (the raw thread) and spins them into the fabric of the current state (the woven cloth).
- The spinning wheel is the rule set: just as a spinning wheel transforms raw fiber into thread, the rule set transforms raw events into state.
- The thread tension is Ve's responsiveness to new events: just as a weaver adjusts tension to create different patterns, the rule engine adjusts Ve in response to new events.

The "becoming" in Verðandi's name captures a crucial property of the Verðandi layer: it is not a static state but an ongoing process. The current state is always in the process of becoming — always being computed, re-computed, and updated. This is why Ve is authoritative only at quiescence: between events, it is in flux, like a thread being spun on the wheel.

## 11.4 Skuld: The Debt and the Commitment

Skuld (*Skuld*) is the third and youngest Norn. Her name means "debt" or "obligation" — what must come to pass, what is owed to the future. In some sources, she is also associated with the future more broadly, but the etymology emphasizes obligation rather than prediction.

The mapping to WYRD is precise and powerful:

- Skuld's debt is the commitment in Skuld: just as a debt must be paid, an obligation must be fulfilled.
- The cutting of the thread is the triggering of an obligation: just as the Norn cuts the thread of life when the time comes, the Skuld manager triggers an obligation when its condition is met.
- The constraint that the thread must not be cut too short is the constraint: just as the Norns ensure that life lasts for its appointed span, the constraints in Skuld ensure that certain conditions are maintained.

The etymology of *skuld* as "debt" is particularly apt. A WYRD commitment is not a prediction — it is a promise, a contract with the future. The agent is not predicting what will happen; it is committing to what it will make happen. This is why Skuld is a separate layer, not a probability distribution: it represents a different kind of knowledge — deontic (obligation-based) rather than epistemic (belief-based).

## 11.5 The Loom: Threads, Warp, and Weft

The overarching metaphor is the loom: the Norns weave the threads of fate, and the WYRD engine weaves the events of the world into a coherent model. In this metaphor:

- **The warp** (the vertical threads, held taut on the loom) is Urd: the fixed structure of the past, against which all new events are woven.
- **The weft** (the horizontal thread, woven through the warp) is Ve: the current state, which is determined by the warp (Urd) and the pattern (rules).
- **The pattern** (the design that the weaver intends to produce) is Skuld: the set of commitments that the agent intends to fulfill, which shape the direction of the weaving.

The loom metaphor captures several key insights:

1. **The past constrains the present.** Just as the warp threads are fixed before the weft is woven, the events in Urd are fixed before Ve is computed. The weaver cannot change the warp mid-weave — they must work with the threads they have.

2. **The present is determined by the pattern.** Just as the weft follows the pattern set by the weaver, Ve is determined by the rules applied to Ur. Change the pattern (the rules), and the fabric changes, even if the warp (Ur) remains the same.

3. **The future is committed, not predicted.** Just as the weaver plans a pattern before weaving it, the agent commits to future actions before performing them. Skuld is the pattern that the weaver intends to produce, not a prediction of what the fabric will look like.

4. **Reconciliation is re-weaving.** When a thread is woven incorrectly (a past event is wrong), the weaver cannot pull it out (the append-only invariant). Instead, they weave a corrective thread alongside it (the reconciliation event), changing the fabric without destroying it.

## 11.6 Where the Metaphor Breaks Down

All metaphors have limits. The Norns and the loom metaphor breaks down in several important ways:

1. **The Norns are external to the world they shape.** In the mythology, the Norns stand outside the world, weaving the fates of others. In WYRD, the agent is both the weaver and the woven: it shapes the world model (through its actions and commitments) and is shaped by it (through its perceptions and the constraints of the past).

2. **The loom produces a single fabric.** In the mythology, the Norns weave one fate for each individual. In WYRD, the possibility tree produces many possible fabrics, and the agent chooses which one to commit to. Skuld is only one branch of the possibility tree — the branch the agent has chosen.

3. **The Norns' knowledge is perfect.** In the mythology, the Norns know all fates. In WYRD, the agent's knowledge is imperfect — perceptions can be wrong (requiring reconciliation), and the future is uncertain (the possibility tree branches over unknown perceptions).

4. **The thread of fate is immutable.** In the mythology, once the Norns have woven a fate, it cannot be changed. In WYRD, commitments can be revoked and past events can be reinterpreted. The WYRD agent has more agency than the subjects of the Norns.

These breakdowns are instructive: they point to the ways in which WYRD goes beyond the mythological metaphor, adding flexibility, correction, and choice that the mythological Norns do not possess.

## 11.7 The Loom as Cognitive Architecture

The loom metaphor is not just a pedagogical device — it is a design philosophy. The WYRD Protocol treats world modeling as a form of weaving: the agent takes raw perceptions (threads), applies rules (the pattern), and produces a coherent model of the world (the fabric). The three layers of WYRD — Urd, Verðandi, Skuld — correspond to three aspects of the weaving process: the raw material, the process, and the intended design.

This architectural metaphor has implications for cognitive science. If world modeling is weaving, then:

- **Perception is thread-gathering.** The agent collects raw perceptions from the environment, which become the threads of the fabric.
- **Attention is thread-selection.** The agent does not perceive everything — it selects which perceptions to attend to, which threads to gather.
- **Learning is pattern-refinement.** The agent adjusts its rules (the pattern) based on experience, producing a better fabric over time.
- **Memory is the fabric itself.** The agent's world model is not a static picture but a woven fabric, with threads of past, present, and commitment intertwined.

The WYRD Protocol is not just a world modeling system — it is a cognitive architecture that treats temporal reasoning as fundamentally structured by the tripartite distinction between past, present, and future. The loom metaphor makes this structure vivid and intuitive, while the formal specification ensures that it is riggable and implementable.

### Required Reading

- Larrington, C. (2014). *The Poetic Edda*. Translated with introduction and notes. Oxford World's Classics. (Focus on Völuspá and Grímnismál.)
- Sørensen, H. (2038). "The Loom Metaphor: From Mythology to Architecture." *Nordic Journal of Cognitive Science*, 5(1), 1–28.
- Lakoff, G., & Johnson, M. (1980). *Metaphors We Live By*. Chapters 1–6. (For context on metaphor as cognitive structure.)

### Discussion Questions

1. The loom metaphor suggests that the agent is a weaver, but the mythological Norns are external to the world they shape. What are the implications of the agent being both weaver and woven? Does this create a paradox?
2. The metaphor breaks down when it suggests that the thread of fate is immutable. WYRD allows commitments to be revoked and past events to be reinterpreted. How does this change the nature of the agent's relationship to its past?
3. If world modeling is weaving, what is attention? Propose a mapping between the cognitive concept of attention and the weaving metaphor.
4. The WYRD Protocol uses Norse mythology, but other mythological systems also have tripartite temporal structures (e.g., the Greek Moirai: Clotho, Lachesis, Atropos). Compare the Norse and Greek systems. Would the Protocol have been different if designed around Greek mythology?

---

# Lecture 12: Advanced WYRD — Multi-Agent Looms and Open Research

## 12.1 Introduction: Beyond the Single Agent

All previous lectures have assumed a single agent with its own WYRD triple (Urd, Verðandi, Skuld). This lecture extends WYRD to multi-agent settings, where multiple agents share a world and must coordinate their actions, commitments, and reconciliations.

## 12.2 Multi-Agent Architecture

In a multi-agent setting, each agent maintains its own WYRD triple:

```
Agent i:  Wᵢ(t) = ⟨ Urᵢ(t), Veᵢ(t), Skᵢ(t) ⟩
```

The key challenge is that agents interact: Agent A's actions become Agent B's perceptions, and vice versa. WYRD v3.2 handles this through a *message-passing protocol*:

1. When Agent A takes an action that is visible to Agent B, a PERCEPTION event is generated in Agent B's Urd log, corresponding to Agent A's ACTION event.
2. The PERCEPTION event in B's log contains a reference to A's ACTION event (via the `cause` field), creating a cross-agent causal link.
3. When Agent A generates a RECONCILIATION event, a propagation event is sent to all agents whose Ve may be affected (as described in Lecture 8).

### 12.2.1 Shared State and Consistency

Each agent's Ve layer is a *local* model of the shared world. Two agents' Ve layers may differ at any given moment, because they have different Urd logs (agents perceive the world from different perspectives and at different times). WYRD v3.2 does not guarantee that all agents' Ve layers are identical — it guarantees only that they are *consistent* with each other's Urd logs.

Formally, WYRD defines *consistency* as follows: two agents' world models are consistent if they agree on all shared perceptions and shared commitments. That is:

> Ur_A ∩ Ur_B ≠ ∅  →  Ve_A and Ve_B agree on all state keys derived from shared events.

This is a weaker condition than global consistency, but it is achievable in practice. Agents can have private perceptions and private commitments that are not shared with other agents, and these do not need to be consistent with anyone else's model.

### 12.2.2 Commitment Exchange

One of the most important interactions in a multi-agent WYRD system is *commitment exchange*. When two agents agree on a joint plan, they exchange commitments: each agent adds obligations to its Skuld layer that correspond to the other agent's expectations.

For example, if Agents A and B agree that A will deliver a package and B will pay for it:

- Agent A adds an obligation to Skuld: "When B confirms receipt, deliver package."
- Agent B adds an obligation to Skuld: "When A confirms delivery, pay A."

These exchanged commitments are tracked by COMMITMENT_CREATED events in both agents' Urd logs, creating an auditable history of the agreement.

### 12.2.3 Loom Composition

WYRD v3.2 introduces the concept of *loom composition*: multiple agents' looms can be composed into a shared loom that represents the joint world model. The composed loom is not a single WYRD triple — it is a distributed structure that combines the Urd logs, Verðandi engines, and Skuld managers of all participating agents.

The composed loom operates as follows:

1. Each agent maintains its own Urd log and Ve layer.
2. When an agent takes an action, it appends an ACTION event to its own Urd log and sends a PERCEPTION event to all affected agents.
3. Each affected agent appends the PERCEPTION event to its own Urd log and recomputes its Ve layer.
4. Committed actions (Skuld obligations) are shared via COMMITMENT_CREATED events.
5. Reconciliations are propagated via RECONCILIATION events.

This architecture is *eventually consistent*: each agent's Ve layer converges toward a consistent view of the shared world as events propagate, but there is no global clock and no global Ve.

## 12.3 Open Research Questions

The WYRD Protocol, even at v3.2, leaves many questions open. This section surveys the most pressing research challenges.

### 12.3.1 Formal Verification of WYRD Systems

The transition cycle, quiescence guarantee, and reconciliation protocol all have formal properties that should be verified. Currently, these properties are argued informally in the specification. A formal verification of the WYRD Protocol — using a theorem prover such as Coq or Isabelle — would increase confidence in the correctness of implementations.

Open questions:
- Can we formally verify that the transition cycle always reaches quiescence under the specified conditions?
- Can we formally verify that the reconciliation protocol preserves the invariants of the Urd log (append-only, causally acyclic)?
- Can we formally verify that incremental update produces the same result as full replay?

### 12.3.2 Probabilistic Extensions

WYRD is deterministic: given the same Urd and rules, Ve is always the same. But many real-world problems require probabilistic reasoning. How can WYRD be extended to handle uncertainty without sacrificing determinism?

One approach is to model uncertainty in the Urd log: instead of appending a deterministic event, append a *distribution* over possible events. The Verðandi engine would then compute a distribution over Ve, rather than a single Ve. This raises questions about how to maintain the append-only invariant for distributions, how to reconcile probabilistic events, and how to combine distributions from multiple agents.

### 12.3.3 Hierarchical WYRD

The current Protocol treats all events as atomic. But many world models have hierarchical structure: a "day" event contains "hour" events, which contain "minute" events. How can WYRD represent this hierarchy?

One approach is to nest Urd logs: a "compound event" in the top-level Urd log contains a sub-Urd log that records the events within the compound event. This would allow agents to reason at different granularities — zoomed out (days) or zoomed in (minutes) — without losing the append-only invariant.

### 12.3.4 WYRD and Neural Networks

The WYRD Protocol is a symbolic system: events, rules, commitments, and reconciliations are all represented symbolically. But modern AI systems increasingly use neural networks for perception, language understanding, and decision-making. How can WYRD be integrated with neural network-based components?

One approach is to use neural networks to generate events for the Urd log: a visual perception module outputs PERCEPTION events, a language module outputs COMMITMENT_CREATED events, and so on. The neural network is a sensor that feeds events into the WYRD system, which processes them symbolically.

This raises questions about how to reconcile neural network outputs (which are probabilistic and approximate) with WYRD's deterministic specifications. If a neural network occasionally produces incorrect perceptions, the WYRD reconciliation mechanism must correct them — but the reconciliation mechanism requires a "ground truth" to correct to, which the neural network may not provide.

### 12.3.5 Scalability

The WYRD Protocol has been tested primarily in small-scale settings (single agents, short time horizons). Scaling to long-lived agents with millions of events, large rule sets, and complex commitment structures raises several challenges:

- **Storage:** The Urd log grows monotonically. How should events be archived and indexed for efficient access?
- **Computation:** Recomputing Ve from a large Urd log is expensive. Can incremental update be made more efficient for large rule sets?
- **Communication:** In a multi-agent setting, propagating events and reconciliations to all affected agents requires significant bandwidth. Can propagation be selective or prioritized?

### 12.3.6 Ethical Considerations

An agent's Urd log is a complete record of its perceptions, actions, and commitments. This raises significant privacy concerns: who has the right to audit an agent's Urd log? Can an agent selectively delete events from its log (violating the append-only invariant) to protect privacy? How should WYRD handle the tension between auditability and privacy?

These questions are beyond the scope of the Protocol specification, but they are essential for any real-world deployment.

## 12.4 The Future of WYRD

The WYRD Protocol is a living specification. Version 3.2 represents the current state of the art, but the design team at Runa University is actively working on v4.0, which is expected to include:

- **Probabilistic events:** Support for distributions over event types and payloads, enabling WYRD to handle uncertain perceptions.
- **Hierarchical events:** Support for compound events with nested Urd logs, enabling multi-granularity reasoning.
- **Distributed consensus:** A protocol for achieving globally consistent Ve across multiple agents, based on PBFT (Practical Byzantine Fault Tolerance).
- **Neural-symbolic integration:** APIs for connecting neural network modules to WYRD as event generators and rule learners.

These extensions will push WYRD beyond its current boundaries, but the core design philosophy — the tripartite architecture, the append-only invariant, the deterministic transition cycle, and the commitment structure — will remain.

## 12.5 Conclusion: The Loom and the Agent

We began this course with the metaphor of the loom: the Norns weaving the threads of fate at the well of Urd. We have spent twelve lectures building the loom — understanding its warp (Urd), its weft (Verðandi), and its pattern (Skuld). We have learned to weave (the transition cycle), to correct (the Norn's Judgment), and to coordinate (loom composition).

But the loom is not the agent. The loom is the infrastructure on which the agent's cognition runs. The agent sits at the loom, drawing threads from the well (perceiving events), spinning them into fabric (computing Ve), and planning the pattern (committing to future actions). The WYRD Protocol provides the loom; the agent provides the intelligence.

As you implement your WYRD-compliant world state engine, remember that the loom is only as good as the weaver. A well-built loom with a poor weaver produces tangled cloth. A well-trained weaver with a broken loom cannot produce cloth at all. The WYRD Protocol provides the best loom we know how to build. It is up to you — the next generation of AI world modelers — to become the best weavers you can be.

The Norns are waiting. The well is full. The threads are ready. Start weaving.

### Required Reading

- Sørensen, H. (2039). "WYRD v4.0: A Preview." *Runa University Cognitive Architecture Lab Technical Report*, 2039-01.
- Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. 2nd ed. Chapters 4–6 on multi-agent coordination.
- Lipton, R., & McGinnis, R. (2038). "Formal Verification of WYRD: A Progress Report." *Proceedings of the Symposium on Verified Cognitive Architectures*, 1, 33–47.

### Discussion Questions

1. In a multi-agent WYRD system, each agent has its own Urd log. How can two agents resolve a conflict when their Urd logs contain contradictory events (e.g., Agent A remembers a conversation that Agent B denies having)?
2. Probabilistic extensions would allow WYRD to handle uncertain perceptions. But how should reconciliation work for probabilistic events? If a perception is later found to be wrong, should we reconcile the entire distribution or just the most likely outcome?
3. Hierarchical Urd logs would allow agents to reason at different granularities. What are the implications for the append-only invariant? Can nested logs be archived independently?
4. An agent's Urd log is a complete record of its perceptions, actions, and commitments. This raises significant privacy concerns. Propose a privacy framework for WYRD that balances auditability with the right to forget. Can the append-only invariant be preserved while allowing selective redaction?

---

*End of WM105 Lecture Notes. The Norns are waiting. The well is full. The threads are ready. Start weaving.*