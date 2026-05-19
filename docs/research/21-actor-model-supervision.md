# 21 — Actor Model and Erlang-Style Supervision Trees

**Category:** Event-Driven & Concurrency
**Runa relevance:** VERÐANDI (event-bus design), Hirð (retainer isolation), Eir (supervisor logic)
**Status:** Research synthesis. Bridges classic CS to AI agent architecture.
**Last touched:** 2026-05-17

---

## 1. Core idea

The actor model (Hewitt, 1973) is a concurrency paradigm where the *only* unit of computation is an **actor** — a lightweight, isolated entity that holds private state, processes messages from its mailbox one at a time, and can: send messages to other actors, create new actors, and decide how it will respond to the next message. There is no shared memory. There are no locks. Everything is asynchronous message passing.

Erlang took this and built a *let-it-crash* philosophy on top: actors are cheap, so when one fails in a way it doesn't know how to handle, kill it and let a **supervisor actor** restart it from a known-good state. Sufficient supervisors compose into a tree, and the whole system gracefully degrades, isolates, and recovers without anybody writing per-failure recovery code.

For Runa, the actor model is the cleanest articulation of the design principles ARCHITECTURE.md §4.4 commits to: *every adapter is independently failable, no adapter takes another down, the kernel survives the death of any subsystem*. Hirð is, conceptually, a small supervisor tree where the kernel supervises retainers. VERÐANDI is a pub/sub variant of actor messaging. Understanding the classical patterns sharpens how Runa's analogues should work.

## 2. Technical depth

**Actor invariants:**

1. **Encapsulation.** Actor state is *private*. No other actor can read or modify it directly.
2. **Message-passing only.** Inter-actor communication is asynchronous messages dropped into mailboxes.
3. **Sequential per actor.** An actor processes one message at a time, in order. Within an actor, you reason single-threaded.
4. **Location transparency.** An actor's address doesn't tell you which machine it lives on. The same code works distributed.

**Erlang/OTP supervisor semantics** add:

- **Supervisor strategies:**
  - `one_for_one` — when a child dies, restart only that child.
  - `one_for_all` — when any child dies, restart all children.
  - `rest_for_one` — when a child dies, restart it and all children started after it.
- **Restart intensity limits.** "Restart at most 5 times in 10 seconds, otherwise escalate." Prevents infinite restart loops.
- **GenServer** — a behaviour for stateful server-like actors with standard callbacks (`init`, `handle_call`, `handle_cast`, `handle_info`).
- **Application** — top-level supervised entity, the "process" boundary.
- **Hot code reload** — actors can be replaced with new code at runtime, preserving state.

**The let-it-crash philosophy:**

- Don't write defensive code for failures you can't anticipate. Let the actor crash.
- A crashed actor's state is corrupt or unrecoverable; restarting from a known-good initial state is more reliable than trying to repair in-place.
- The supervisor is the only code that decides *how* to recover.
- This works *because* actor state is isolated — one actor's crash doesn't corrupt the whole system.

**The actor model in modern systems:**

- **Erlang/OTP** — the canonical implementation. WhatsApp, RabbitMQ, parts of Cloudflare, parts of telcos.
- **Elixir** — modern syntax over Erlang VM (BEAM). Phoenix, LiveView, Nerves.
- **Akka** (JVM, Lightbend) — actor framework for Scala/Java. Heavy industry use.
- **Orleans** (Microsoft, .NET) — virtual actors with automatic placement.
- **Pony language** — actor-first language with reference capabilities for safety.
- **Ray** (Python, originally Berkeley) — distributed actors for ML workloads.
- **Pykka, Thespian, Pulsar** — Python actor libraries (less ubiquitous than asyncio).

**Adjacent patterns:**

- **Communicating Sequential Processes (CSP)** (Hoare, 1978) — alternative model where processes synchronise on channels. Go's goroutines + channels are a CSP-flavoured system.
- **Reactive Streams** — back-pressure-aware streaming between actors.
- **Process calculi** (π-calculus, ambient calculus) — formal foundations.

## 3. Key works

- **Hewitt, Bishop, Steiger. "A Universal Modular Actor Formalism for Artificial Intelligence."** IJCAI 1973. The foundational paper.
- **Hewitt, C. "Actor Model of Computation: Scalable Robust Information Systems."** arXiv:1008.1459, 2010. Modern restatement.
- **Armstrong, J. "Making reliable distributed systems in the presence of software errors."** PhD thesis, 2003. The Erlang foundation.
- **Armstrong, J. *Programming Erlang*.** Pragmatic Bookshelf. The accessible introduction.
- **Hoare, C.A.R. "Communicating Sequential Processes."** Communications of the ACM, 1978. The CSP foundation.
- **Akka documentation** — akka.io. Reference for JVM actor systems.
- **The Pony Tutorial** — tutorial.ponylang.io. Reference capability annotations for actor safety.
- **Joe Armstrong's "Erlang the Movie"** (1990 promo film, on YouTube) and the "Programming Erlang" book are good cultural references.

## 4. Empirical results

Erlang/OTP's deployment record speaks for itself:

- **WhatsApp** scaled to ~900M users on Erlang with a small team — the per-user resource efficiency of BEAM is widely cited.
- **Ericsson AXD301 switch** achieved 99.9999999% uptime ("nine 9s") with Erlang/OTP. That's ~31 ms of downtime per year.
- **RabbitMQ** is the most-deployed message broker (along with Kafka); Erlang foundations.

Specific empirical claims:

- Actor crashes affect only the crashed actor; supervisor restart times measured in microseconds.
- Per-actor memory footprint on BEAM: ~300 bytes. You can spawn millions on commodity hardware.
- Hot-reload is observed working in production telco gear with multi-decade uptimes.

The trade-offs:

- Performance: per-message overhead is real. For tight inner loops, shared-memory concurrency wins.
- Debugging: distributed message-passing is harder to reason about than synchronous calls.
- Learning curve: thinking in actors is genuinely different.

## 5. Applicability to Runa

The actor model is *not* a strict prescription for Runa, but its patterns directly inform several Runa design decisions:

For **VERÐANDI event bus**:

- VERÐANDI is a pub/sub variant of actor messaging. Subscribers are actor-like — each has its own state, processes events one at a time, doesn't share memory with others.
- The "no shared mutable state" rule should hold inside VERÐANDI. Subscribers communicate only via events.

For **Hirð (subagent hall)**:

- Each retainer (Huginn / Völundr / Eir / …) is an actor in the classic sense. Its state is private; the kernel addresses it via `SubagentDispatch` messages; results return via `SubagentReport`.
- Cross-retainer communication always routes through the kernel — the "no direct retainer-to-retainer calls" rule (DOMAIN_MAP §10) is exactly the actor-encapsulation rule.

For **Eir (supervisor)**:

- Eir is Runa's supervisor in the OTP sense. When a service dies (gateway, voice, an adapter), Eir's logic decides whether to restart, escalate, or quarantine.
- The `one_for_one` strategy is the default — a crashed adapter does not bring down the rest. `rest_for_one` may be appropriate for services with explicit dependency chains.
- Restart intensity limits prevent infinite crash loops. Pinned in config.

For **adapter failure isolation** (DOMAIN_MAP §8 invariants):

- Each adapter is an actor. Its crash does not affect any other adapter. The let-it-crash philosophy is exactly the design.

For **the kernel itself**:

- The kernel is *one* actor (one place that synchronously decides what to do next), supervised by the runtime's process supervisor. A kernel crash is a service-down event recovered by full restart per DATA_FLOW §5.

Recommended adoption depth:

- **Adopt the actor *patterns* — encapsulation, message-passing, supervisor trees, restart intensity limits.**
- **Don't adopt a heavy actor framework** for v0. Plain asyncio with a small `Actor` base class is enough for Runa's scale. Ray or similar may be worth it later for compute-heavy distributed retainers.

What to avoid:

- Don't share mutable state between retainers or adapters. Everything goes through events.
- Don't write defensive try/except blocks for failures the actor can't recover from. Let it die and let the supervisor restart.
- Don't make supervisor restart logic complex. If `one_for_one + intensity_limit` is wrong, the deeper problem is somewhere else.
- Don't conflate "concurrent" with "actor". Two coroutines that share `asyncio.Lock` and read each other's state are not actors.

## 6. Open questions

- **Actor frameworks vs hand-rolled.** A real actor framework (Akka, Orleans) gives a lot for free; the cost is a heavy dependency. Hand-rolled actors in asyncio cover most needs.
- **Distributed actors.** When Runa runs across Pi + laptop + server, actor-style messaging across the Tailnet is a clean model. Frameworks like Ray and Pyro fit; asyncio doesn't natively.
- **Persistence.** Actor state by default is in-memory. Eventually-persistent actors (Akka Persistence, the event-sourcing crossover) compose with the actor pattern; see [[22-event-sourcing-cqrs]].
- **Type safety across messages.** Erlang is dynamic; Akka is partially typed; Pony has full type safety with reference capabilities. Runa's `runa.schemas.events` (typed via Pydantic) is the equivalent.

## 7. References (curated)

- Armstrong, J. *Programming Erlang*, 2nd ed., Pragmatic Bookshelf, 2013.
- arXiv:1008.1459 — Hewitt's modern actor formalism.
- erlang.org/doc/design_principles/sup_princ.html — OTP supervisor principles.
- ponylang.io — Pony's reference capability system.
- Joe Armstrong, "The Mess We're In" (2014 talk) — YouTube, philosophical context.
- akka.io/docs — Akka.
- docs.ray.io — Ray.
- Hoare, *Communicating Sequential Processes*, 1985. The CSP book.
- Companion docs: [[22-event-sourcing-cqrs]], [[23-asyncio-structured-concurrency]], [[24-multiprocessing-worker-pools]].
