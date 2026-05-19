# SD203: Software Architecture & Design
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 2, Semester 2
**Prerequisites:** SD201 (Object-Oriented Design)
**Instructor:** Dr. Björn Hafþórsson, Faculty of Computational Arts

> *"Architecture is the set of decisions you wish you could make early, but can only make well after you've built the system once. The architect's skill is knowing which decisions to postpone and which to commit."* — Björn Hafþórsson, *Threads of Light* (2037)

---

## Course Description

Software Architecture & Design bridges the gap between code-level design (classes, patterns) and system-level design (services, databases, communication protocols). This course covers architectural styles (monolith, microservices, event-driven, serverless, agent-oriented), quality attributes (scalability, availability, performance, security, maintainability), architectural decision records (ADRs), and the 2040-era practices of evolutionary architecture and AI-assisted architectural analysis.

The course culminates in a capstone project where students design the architecture for a non-trivial system, document it with ADRs, and defend it in an architecture review board simulation — the same process used at companies like Google, Amazon, and the University of Yggdrasil's own infrastructure team.

---

## Lectures

### ᚠ Lecture 1: What Is Architecture? — Decisions, Constraints, and the -ilities

**Date:** Week 1, Session 1

#### Overview

Every system has an architecture — whether it was designed or not. This lecture defines software architecture as the set of *significant design decisions* that shape a system's structure, behavior, and evolution. We distinguish architecture from design, introduce quality attributes (the "-ilities"), and establish the architect's primary responsibility: managing tradeoffs.

#### Lecture Notes

Ralph Johnson (co-author of Design Patterns) defined architecture as "the important stuff — whatever that is." Martin Fowler expanded: "Architecture is about the things that are hard to change." This is the most practical definition: architecture is the set of decisions that, once made, are expensive to reverse.

Contrast:
- **Architecture decision:** "We'll use a microservices architecture with asynchronous communication via Kafka." Changing this later means rewriting every service's communication layer.
- **Design decision:** "We'll use the Strategy pattern for payment processing." Changing this means refactoring one module — annoying but not catastrophic.
- **Implementation decision:** "We'll name this variable `customerEmail`." Changing this is trivial.

The line between architecture and design is blurry and context-dependent. In a monolith, the choice of programming language is an architecture decision (hard to change). In a microservices system where each service can use a different language, it's a design decision (each service chooses independently).

**Quality Attributes — The "-ilities".** Architecture is driven by quality attributes — the non-functional requirements that determine whether a system is "good":

| Attribute | Question It Answers |
|-----------|-------------------|
| Availability | What percentage of the time is the system up? |
| Performance | How fast does it respond? Under what load? |
| Scalability | Can it handle 10x the load by adding resources? |
| Security | Can it resist attacks? Protect data? |
| Maintainability | How easy is it to fix bugs and add features? |
| Testability | How easy is it to verify correctness? |
| Deployability | How easy is it to get changes into production? |
| Observability | Can we tell what's happening inside? |
| Modifiability | Can we change one part without touching others? |
| Interoperability | Can it work with other systems? |

The architect's tragedy: **these attributes trade off against each other.** A system optimized for performance might sacrifice maintainability (hand-tuned C vs. clean Python). A system optimized for availability might sacrifice consistency (eventual consistency vs. strong consistency). There is no perfect architecture — only architectures optimized for the right tradeoffs.

**Architecture as Constraint.** Architecture is fundamentally about *constraint*. You choose constraints that enable desired qualities: "All communication between services goes through the message bus" (enables observability and loose coupling). "The database is the source of truth; caches may be stale" (enables availability at the cost of consistency). Good constraints enable; bad constraints suffocate.

In 2040, the Hermes framework's architecture is a set of explicit constraints:
- All agent memory goes through the Mímir well (enables traceability)
- All events flow through the VERÐANDI socket (enables observability)
- All credentials are managed by Kista (enables security)
- All subagent communication is structured messages (enables debuggability)

These constraints are not arbitrary rules — they are the architecture.

**The Architect's Role.** The architect does not make all decisions. They:
1. Identify the decisions that *matter* (hard to change, broad impact)
2. Present options with tradeoffs to the team
3. Document decisions and their rationale (ADRs)
4. Review implementations against the architectural constraints
5. Evolve the architecture as requirements change

In 2040, AI can generate architectural diagrams, evaluate options against quality attributes, and even simulate performance under load. The architect's role is not to generate the design but to *validate* it — to ask "what happens when this fails?" and "how will this evolve?"

#### Required Reading

- Bass, L., Clements, P., & Kazman, R. (2025). *Software Architecture in Practice* (5th ed.). Addison-Wesley. Chapters 1-3.
- Fowler, M. (2003). "Who Needs an Architect?" *IEEE Software*, 20(5). [Short, opinionated, still relevant.]
- Hafþórsson, B. (2037). *Threads of Light*. Chapter 3: "The Architect as Norn."

#### Discussion Questions

1. "Architecture is about the things that are hard to change." What makes a decision hard to change? Is it just technical coupling, or are there organizational and political factors?
2. If AI can generate architecture diagrams and evaluate tradeoffs, what uniquely human skill does the architect provide? Is "architect" still a distinct role in 2040, or has it merged into "senior developer"?
3. "Good constraints enable; bad constraints suffocate." Give an example of each from your experience or reading.

---

### ᚢ Lecture 2: Architectural Styles — Monolith, Modular, and the Spectrum of Coupling

**Date:** Week 1, Session 2

#### Overview

Every system embodies an architectural style — a set of constraints and patterns that govern its structure. This lecture surveys the spectrum from monolith to microservices, emphasizing that the choice is not binary but a continuum. We examine modular monoliths, service-based architectures, and the 2040-era "cell-based" architecture used by the Hermes framework.

#### Lecture Notes

The debate between monolith and microservices has consumed more conference talks and blog posts than any other architectural topic. The debate is largely misguided. The question is not "monolith or microservices?" but *"what are the boundaries in this system, and how rigid should they be?"*

**The Monolith.** All code in a single deployable unit. One process, one database, one deployment pipeline. 

Advantages: Simple to develop (one codebase), simple to deploy (one artifact), simple to test (integration tests are straightforward), simple to debug (one stack trace), no network latency between components.

Disadvantages: Coupling tends to increase over time (everything can access everything), deployment is all-or-nothing (a small change requires redeploying the whole system), scaling is all-or-nothing (you scale the whole application, not the bottleneck component), technology lock-in (hard to introduce a new language or framework).

**The Modular Monolith.** A monolith with enforced internal boundaries. The code is organized into modules (packages, namespaces) with explicit interfaces. Module A cannot access Module B's internal classes — the build system enforces it. This gives you the deployment simplicity of a monolith with the conceptual separation of microservices.

In 2040, the modular monolith is the default recommendation for new systems until scale demands otherwise. Tools like Modulith (Java), `python-modular` (Python), and ArchUnit (architectural fitness functions) enforce module boundaries at build time.

**Microservices.** Independent deployable services, each owning its own data. Services communicate over the network (HTTP, gRPC, message queues).

Advantages: Independent deployment (each service on its own schedule), independent scaling (scale the bottleneck, not the monolith), technology diversity (each service in its best language), fault isolation (one service crashing doesn't crash others), team autonomy (each team owns their services end-to-end).

Disadvantages: Network latency (every call crosses the network), distributed transactions (no simple ROLLBACK across services), operational complexity (monitoring, tracing, logging across services), data consistency (eventual consistency, sagas, compensating transactions), development complexity (setting up the whole system locally).

**The Spectrum.** Between monolith and microservices lies a spectrum:

```
Monolith → Modular Monolith → Service-Based → Microservices → Nanoservices
   ↑            ↑                  ↑              ↑              ↑
  one          one               few            many          too many
  deployable   deployable,       services,      independent   tiny,
               internal          shared         services,     single-
               modules           database       own database  function
```

Most systems should be somewhere in the middle. The extremism of "everything must be a microservice" was a 2015-era overcorrection that the industry has since walked back.

**Cell-Based Architecture (2040).** The Hermes framework uses a variant called "cell-based architecture": each bounded context is a "cell" that can be deployed as a monolith internally but communicates with other cells via well-defined asynchronous interfaces. A cell can be a single process or multiple — the architecture doesn't care. What matters is the *boundary*, not the *deployment unit*.

This is the synthesis the industry has been converging on: **design with boundaries first; decide deployment later.** A well-designed modular monolith can be extracted into microservices when needed. A poorly-designed microservices system cannot be merged into a monolith without rewriting.

#### Required Reading

- Newman, S. (2021). *Building Microservices* (2nd ed.). O'Reilly Media. Chapters 1-3.
- Vernon, V. (2016). "Modular Monoliths." *VaughnVernon.com*. [A short, influential article.]
- Hafþórsson, B. (2041). "Cell-Based Architecture: The Hermes Case Study." *IEEE Software*, 58(3), 24-33.

#### Discussion Questions

1. "Start with a monolith, extract microservices when needed." Is this always good advice, or are there systems where microservices are the right starting point?
2. The modular monolith requires discipline to maintain module boundaries. What happens when a developer "just this once" accesses an internal class across a module boundary? How do you prevent the erosion?
3. Cell-based architecture says "design with boundaries, decide deployment later." If the deployment decision is deferred, what decisions *must* be made early?

---

### ᚦ Lecture 3: Event-Driven Architecture — Messages, Events, and Asynchronous Communication

**Date:** Week 2, Session 1

#### Overview

Not all communication is request-response. Event-driven architecture (EDA) uses events — facts about things that happened — as the primary integration mechanism. This lecture covers event types (domain events, integration events, command events), message patterns (pub/sub, event sourcing, CQRS), and the infrastructure (message brokers, event stores, stream processors) that make EDA work at scale.

#### Lecture Notes

In a request-response system, Service A asks Service B: "What's the customer's balance?" Service B responds. In an event-driven system, Service A publishes an event: `CustomerAddressChanged(customer_id=42, new_address=...)`. Any service that cares about customer addresses subscribes and reacts. Service A doesn't know who subscribes. Service A doesn't wait for a response. The system is *temporally decoupled* and *spatially decoupled*.

**Why Events?** Events capture *facts*. "OrderPlaced" is a fact — it happened, it can't unhappen. Commands capture *intents*. "PlaceOrder" is a request — it might be rejected. The distinction matters:
- **Commands** are directed (sent to a specific recipient), can be rejected, are named in the imperative ("PlaceOrder").
- **Events** are broadcast (published for anyone interested), are facts (already happened), are named in the past tense ("OrderPlaced").
- **Queries** request data without side effects ("GetOrderStatus").

In an event-driven system, the flow is: Command → Validation → Event. `PlaceOrder` command is validated; if valid, `OrderPlaced` event is published. Subscribers react: `InventoryService` reserves stock, `EmailService` sends confirmation, `AnalyticsService` updates dashboards.

**Message Patterns:**

- **Publish/Subscribe (Pub/Sub):** Publishers send events to a *topic*. Subscribers express interest in topics. The broker delivers events to all interested subscribers. Decouples publishers from subscribers.

- **Event Sourcing:** Instead of storing the current state, store the sequence of events that led to it. A bank account's balance is not stored as `balance: $500` — it's computed by replaying `Deposited($1000)`, `Withdrawn($300)`, `Deposited($200)`, `Withdrawn($400)`. Benefits: complete audit trail, temporal queries ("what was the balance on Tuesday?"), ability to add new projections later by replaying the event stream.

- **CQRS (Command Query Responsibility Segregation):** Use different models for reading and writing. The write model processes commands and publishes events. The read model subscribes to events and builds optimized query views. The read model can be in a different database (e.g., Elasticsearch for full-text search) than the write model (e.g., PostgreSQL for integrity). Query performance and write integrity are independently optimized.

- **Saga:** A sequence of local transactions, each publishing events that trigger the next step. If a step fails, the saga executes *compensating transactions* to undo previous steps. "The distributed transaction for systems that can't use distributed transactions." Example: `OrderSaga` — PlaceOrder → ReserveInventory → ChargeCreditCard → ShipOrder. If ChargeCreditCard fails, compensating transactions: CancelReservation, CancelOrder.

**Infrastructure.** Event-driven systems require message brokers:
- **RabbitMQ:** Mature, reliable, AMQP protocol. Good for work queues and routing.
- **Apache Kafka:** Distributed log, high throughput, replayable. The standard for event streaming in 2040.
- **Redis Pub/Sub:** Lightweight, in-memory. Good for real-time notifications where persistence isn't required.
- **VERÐANDI Socket (2040):** The Hermes framework's own event bus — Unix domain socket, line-delimited JSON, designed for local AI agent communication with minimum latency.

**The Challenges of Asynchrony.** Events are powerful but introduce complexity:
- **Eventual consistency:** Different services have different views of the world at any moment. The system converges over time, but "what's the current state?" is ambiguous.
- **Duplicate events:** Brokers guarantee at-least-once delivery. Handlers must be idempotent (processing twice = same result as once).
- **Ordering:** Events may arrive out of order. Handlers must tolerate this or the broker must guarantee order.
- **Debugging:** "What happened?" requires tracing events across services. Distributed tracing (OpenTelemetry) is essential.

#### Required Reading

- Hohpe, G. & Woolf, B. (2003). *Enterprise Integration Patterns*. Addison-Wesley. Chapters 1-3 (Messaging), 5 (Message Construction).
- Kleppmann, M. (2036). *Designing Data-Intensive Applications*. Chapter 11: "Stream Processing."
- Hermes Documentation. "VERÐANDI Event Architecture." *docs.yggdrasil.university/hermes/verdandi*.

#### Discussion Questions

1. Event sourcing stores all events forever. At what point does the event store become too large? How do you handle "infinite" event streams?
2. Sagas provide eventual consistency with compensating transactions. Is this acceptable for financial transactions (e.g., stock trades)? Where is strong consistency non-negotiable?
3. VERÐANDI uses a local Unix socket for AI agent events. When would this architecture break — when would you need a distributed broker instead?

---

### ᚨ Lecture 4: Architectural Decision Records — Making Decisions Visible

**Date:** Week 2, Session 2

#### Overview

Architecture is made of decisions, but decisions are invisible — they exist in meeting notes, Slack threads, and developers' heads. Architectural Decision Records (ADRs) make decisions explicit, traceable, and revisitable. This lecture covers the ADR format, the decision log as institutional memory, and the 2040-era practice of AI-generated ADRs with human validation.

#### Lecture Notes

Six months after the architecture meeting, someone asks: "Why did we choose Kafka over RabbitMQ?" The developer who championed the decision has left the company. The meeting notes are buried in a Confluence page nobody can find. The decision is effectively lost — and the next architect might make the opposite choice, unaware of the reasons for the original.

**What Is an ADR?** An Architectural Decision Record is a short document capturing a single architectural decision. The format (Michael Nygard, 2011):

```markdown
# ADR-001: Use Kafka for Inter-Service Messaging

## Status
Accepted (2024-03-15)

## Context
We need an inter-service messaging system for our event-driven 
architecture. Services will publish domain events; other services 
will subscribe and react. Requirements: high throughput (10k 
events/sec), persistence (no lost events), replayability.

## Decision
We will use Apache Kafka as the message broker.

## Alternatives Considered
- **RabbitMQ:** Better for complex routing, but lower throughput 
  and no replay capability.
- **Redis Pub/Sub:** Simpler, but no persistence — lost messages 
  on restart.
- **AWS SQS:** Fully managed, but vendor lock-in and no replay.

## Consequences
- Positive: High throughput, persistent log, replay capability, 
  large ecosystem.
- Negative: Operational complexity (ZooKeeper/KRaft management), 
  JVM resource overhead, requires team learning.
- Neutral: We will use the Schema Registry for Avro schemas.
```

**Why ADRs Matter:**

1. **Institutional memory:** Why did we choose X? Read the ADR. No tribal knowledge required.
2. **Onboarding:** New team members read the ADR log to understand why the system is structured the way it is.
3. **Decision review:** ADRs are reviewed by the team. Bad decisions are caught before they're implemented.
4. **Decision reversal:** The ADR records the *context* in which the decision was made. When the context changes (e.g., "Kafka operational complexity has become unsustainable"), the ADR tells you whether it's time to revisit.

**The Decision Log.** ADRs are numbered sequentially and stored in the repository (`/docs/adr/`). They form a chronical of the system's evolution. Reading the ADR log should tell the story of the architecture: first we chose a monolith (`ADR-001`), then we split the user service out (`ADR-012`), then we introduced Kafka for events (`ADR-023`), then we migrated from Kafka to VERÐANDI (`ADR-047`).

**AI-Generated ADRs (2040).** In the Hermes framework, ADRs can be drafted by AI. The architect describes the decision context and alternatives; the AI generates a draft ADR. The architect reviews, edits, and submits. The AI can also:
- Check for consistency: "ADR-047 contradicts ADR-023. ADR-023 says we use Kafka; ADR-047 says we use VERÐANDI. Is this intentional?"
- Track status: "ADR-023 (Kafka) is superseded by ADR-047 (VERÐANDI). Update status accordingly."
- Generate architecture diagrams from ADRs: a graph showing which services communicate via which mechanisms.

But the *decision* remains human. The AI can present options, evaluate tradeoffs, and draft documentation. It cannot decide — because decisions involve values ("We value operational simplicity over maximum throughput") that AI cannot have.

**When to Write an ADR.** Not every decision needs an ADR. Threshold: is this decision hard to reverse? Will someone ask "why" in six months? Does it constrain future decisions? If yes, write an ADR. If it's trivial ("use SQLite for local caching"), don't.

#### Required Reading

- Nygard, M. (2011). "Documenting Architecture Decisions." *cognitect.com/blog*. [The article that launched ADRs.]
- Henderson, J. (2022). *Architecture Decision Records in Practice*. Leanpub. Chapters 1-4.
- Hermes ADR Repository. "ADR Index." *docs.yggdrasil.university/hermes/adrs/*. [Read a few real ADRs; see how the Hermes architecture evolved.]

#### Discussion Questions

1. ADRs document decisions, but they don't document the *discussion* that led to the decision. Should they? If so, how much discussion detail is appropriate?
2. An ADR is "accepted" at the time of decision. But the decision may prove wrong. Should ADRs be updated with post-mortem analysis ("this was a mistake; here's why")?
3. If an AI drafts an ADR and a human approves it, who is accountable for the decision if it goes wrong? The AI? The human? Does the answer change if the AI generated the *options* as well?

---

### ᚱ Lecture 5: Scalability and Performance — Caching, Load Balancing, and Elastic Infrastructure

**Date:** Week 3, Session 1

#### Overview

"Make it work, make it right, make it fast." This lecture covers the architectural patterns for scalability and performance: caching strategies (read-through, write-through, cache-aside), load balancing algorithms, database scaling (read replicas, sharding, connection pooling), and the 2040-era auto-scaling infrastructure that makes elastic capacity the default.

#### Lecture Notes

Scalability is not about speed. It's about the relationship between resources and load. A system is scalable if adding resources increases capacity proportionally. An unscalable system (e.g., a single database server) reaches a ceiling where adding more application servers doesn't help because the database is the bottleneck.

**The Universal Scalability Law.** Neil Gunther's model (1993) describes how systems scale:

```
C(N) = N / (1 + σ(N-1) + κN(N-1))
```

- `C(N)`: capacity with N nodes
- `σ` (sigma): contention penalty — how much performance degrades from sharing resources (0-1)
- `κ` (kappa): coherency penalty — how much overhead from keeping nodes in sync (0-1)

Even with perfect architecture (σ=0, κ=0), you eventually hit Amdahl's Law: the serial portion of the workload limits maximum speedup. If 5% of processing must be serial, no amount of parallelism can improve performance beyond 20x.

**Caching Strategies:**

- **Cache-Aside (Lazy Loading):** Application checks cache; if miss, loads from database and populates cache. Most common pattern. Simple. Risk: cache stampede (many misses on a popular key simultaneously).
- **Read-Through:** Cache sits between application and database. Application always reads from cache; cache loads from database on miss. More abstraction, but application code is simpler.
- **Write-Through:** Application writes to cache; cache writes to database synchronously. Consistent, but adds write latency.
- **Write-Behind (Write-Back):** Application writes to cache; cache writes to database asynchronously. Fast writes, but risk of data loss if cache crashes before flushing.

Cache invalidation is the hardest problem in computer science (Phil Karlton). Strategies: TTL (time-to-live, simple but can serve stale data), event-based invalidation (publish `UserUpdated` event, cache subscribers drop the entry), write-through (never stale, but slower writes).

**Load Balancing.** Distribute requests across multiple servers:
- **Round Robin:** Even distribution. Simple. Ignores server load.
- **Least Connections:** Route to server with fewest active connections. Better for heterogeneous workloads.
- **Consistent Hashing:** Map requests to servers based on a hash of the request (e.g., user ID). Ensures the same user always hits the same server — useful for sticky sessions and distributed caches.
- **Adaptive (2040):** AI-powered load balancers predict request cost and server capacity in real time, routing requests to minimize tail latency.

**Database Scaling:**
- **Read Replicas:** One primary (writes), multiple replicas (reads). Replication lag means replicas may be slightly stale. Good for read-heavy workloads.
- **Sharding:** Partition data across multiple primaries by key range or hash. Writes scale horizontally. Cross-shard queries are expensive. Shard rebalancing is operationally complex.
- **Connection Pooling:** Application servers maintain a pool of persistent database connections. Prevents connection exhaustion (databases have a maximum number of connections). PgBouncer, RDS Proxy.

**Auto-Scaling (2040).** Infrastructure that automatically adds or removes resources based on load:
- **Horizontal scaling:** Add more instances of a service. Kubernetes HPA (Horizontal Pod Autoscaler) scales pods based on CPU/memory/custom metrics.
- **Vertical scaling:** Increase the resources (CPU, RAM) of existing instances. Limited by hardware.
- **Predictive auto-scaling (2040):** ML models predict traffic patterns (daily cycles, weekly cycles, known events) and scale proactively rather than reactively. Hermes uses this for agent worker pools — scale up before the morning traffic surge, scale down at night.

**The Performance Mindset.** Performance is not about micro-optimizations. It's about:
1. Measure first (never optimize without profiling)
2. Fix the biggest bottleneck (the 80/20 rule: 20% of the code causes 80% of the latency)
3. Cache at the right level (closer to the user is better, but harder to invalidate)
4. Design for scale from the start (stateless services, share-nothing architecture)
5. Accept that you will be wrong (monitor in production, adjust)

#### Required Reading

- Gunther, N.J. (2007). *Guerrilla Capacity Planning*. Springer. Chapters 1-3. [The universal scalability law explained.]
- Kleppmann, M. (2036). *Designing Data-Intensive Applications*. Chapter 3: "Storage and Retrieval" — sections on caching.
- Hafþórsson, B. (2042). "Predictive Auto-Scaling at Hermes Scale." *Proceedings of the ACM Symposium on Cloud Computing*, 2042.

#### Discussion Questions

1. "Cache invalidation is one of the two hard problems in computer science." (The other is naming, and off-by-one errors.) Why is invalidation so hard? What makes it harder in a distributed system?
2. Auto-scaling prevents overload, but it can also mask architectural problems (a slow service that scales to 100 instances instead of being optimized). How do you distinguish "needs more capacity" from "needs better code"?
3. Eventual consistency from read replicas means users may see stale data. Is this acceptable for all applications? Draw the line.

---

### ᚲ Lecture 6: Security Architecture — Threat Modeling, Zero Trust, and Defense in Depth

**Date:** Week 3, Session 2

#### Overview

Security is an architectural concern, not a feature to bolt on. This lecture covers security architecture: the principle of least privilege, zero-trust networking (never trust, always verify), defense in depth (layered security), and the architectural patterns for authentication, authorization, and secure communication.

#### Lecture Notes

"A ship is safe in harbor, but that's not what ships are for." Security architecture is the art of building systems that are *secure enough* for their purpose while remaining *usable enough* for their users. Perfect security is achievable — turn off the server. Useful security is a tradeoff.

**Security Principles for Architects:**

1. **Least Privilege:** Every component should have the minimum permissions needed to function. The reporting service can read the database but not write. The CI/CD pipeline can deploy but not access user data. If a component is compromised, the blast radius is minimized.

2. **Defense in Depth:** No single security mechanism is sufficient. Layer them: network (TLS, firewalls, WAF), application (input validation, parameterized queries), authentication (MFA, OAuth), authorization (RBAC, ABAC), data (encryption at rest, field-level encryption), monitoring (audit logs, anomaly detection). An attacker who bypasses one layer should be stopped by the next.

3. **Zero Trust:** "Never trust, always verify." Traditional security assumed the internal network was safe (the "castle and moat" model). Zero trust assumes the network is hostile: every request, even from inside the network, must be authenticated and authorized. Every service-to-service call carries a token. Every database query is attributed to a specific principal.

4. **Secure by Default:** The default configuration should be secure. If the administrator doesn't configure anything, the system should be locked down. Optional features that weaken security should require explicit enablement.

5. **Fail Securely:** When a security check fails, deny access. Don't fall through to the normal code path. A failed authentication shouldn't result in an unauthenticated request being processed.

**Authentication and Authorization Patterns:**

- **OAuth 2.0 / OpenID Connect:** The standard for delegated authorization. A user grants a third-party application limited access to their data without sharing their password. The flow: Authorization Code → Access Token → API Call. In 2040, OAuth 2.1 simplifies the spec and removes insecure grant types.

- **JWT (JSON Web Tokens):** A signed token containing claims (subject, expiration, permissions). Services verify the signature using the authorization server's public key — no database lookup required. Vulnerable to token theft (if stolen, attacker can impersonate until expiration). Mitigated by short expiration times (15 minutes) and refresh tokens.

- **RBAC (Role-Based Access Control):** Permissions are assigned to roles; roles are assigned to users. `admin` role can do everything; `editor` can create and edit; `viewer` can only read. Simple, widely understood, coarse-grained.

- **ABAC (Attribute-Based Access Control):** Access decisions based on attributes of the user, the resource, and the environment. "Allow read if user.department == resource.department AND time.hour between 9 and 17." Fine-grained, flexible, complex to administer.

- **ReBAC (Relationship-Based Access Control, 2035):** Access based on the relationship graph. "Alice can edit Document X because Alice is a member of Team Y and Team Y owns Document X." Google's Zanzibar paper (2019) popularized this. Hermes uses ReBAC for memory well access — access to a memory depends on your relationship to the entity it describes.

**Secure Communication:**
- **TLS 1.3+ everywhere:** All service-to-service communication encrypted. mTLS (mutual TLS) for service identity verification.
- **API gateways:** Single entry point for authentication, rate limiting, and request routing. Kong, Ambassador, the Hermes Gateway.
- **Secrets management:** Never store secrets in code or configuration files. Use a secrets manager (HashiCorp Vault, Kista) with automatic rotation.

**The Architecture of Audit.** You cannot prevent all attacks. You *must* detect them. Audit architecture:
- Immutable append-only logs (cannot be modified after writing)
- Logs shipped off-server (attacker who compromises the server can't delete their tracks)
- Anomaly detection on logs (unusual access patterns, unusual hours, unusual volumes)

#### Required Reading

- Shostack, A. (2038). *Threat Modeling* (2nd ed.). Wiley. Chapters 1-4.
- Google. "BeyondCorp: A New Approach to Enterprise Security." *USENIX Login*, 2014. [The paper that launched Zero Trust.]
- Kista Vault Documentation. "Zero-Trust Credential Architecture." *docs.yggdrasil.university/kista/*.

#### Discussion Questions

1. Zero trust says "never trust, always verify." But every verification adds latency. At what point does security overhead become unacceptable? How do you make the tradeoff?
2. ABAC is more flexible than RBAC, but also more complex. In practice, do the benefits of ABAC outweigh the administrative burden? When should you stay with RBAC?
3. "Fail securely" means denying access on error. But this can make systems unavailable during outages of the auth service. How do you balance security and availability?

---

### ᚷ Lecture 7: Designing for Failure — Resilience Patterns and Graceful Degradation

**Date:** Week 4, Session 1

#### Overview

Every system fails. The question is not *if* but *how* — does it fail gracefully, with minimal user impact, or catastrophically, with cascading failures? This lecture covers resilience patterns: circuit breakers, bulkheads, retries with backoff, timeouts, and the 2040-era chaos engineering practice that tests failure modes in production.

#### Lecture Notes

"Everything fails, all the time." Werner Vogels, Amazon CTO. A hard drive has an MTBF (Mean Time Between Failures) of about 1.2 million hours — but when you have 100,000 drives, that means one fails every 12 hours. At scale, failure is the normal state. Resilience is designing systems that continue operating despite failures.

**The Circuit Breaker.** When a downstream service is failing, stop calling it. The circuit breaker has three states:
- **Closed:** Normal operation. Requests flow through.
- **Open:** After a threshold of failures, the breaker opens. Requests immediately fail without calling the downstream service. This prevents the downstream service from being overwhelmed by retries.
- **Half-Open:** After a timeout, the breaker allows a single request through as a probe. If it succeeds, close the circuit. If it fails, re-open.

```python
class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"
    
    def call(self, fn):
        if self.state == OPEN:
            if time.time() - self.last_failure > self.timeout:
                self.state = HALF_OPEN
            else:
                raise CircuitBreakerOpen()
        
        try:
            result = fn()
            self.success()
            return result
        except Exception:
            self.failure()
            raise
```

Circuit breakers prevent: cascading failures (A calls B, B is slow, A's threads are all waiting for B, A becomes unresponsive), resource exhaustion (threads, connections, memory), and the "thundering herd" (when B recovers, 100 instances of A simultaneously hammer it).

**Bulkhead.** Partition resources so a failure in one part doesn't sink the whole ship. A ship's hull is divided into compartments — if one floods, the ship stays afloat. In software: separate thread pools for different operations. The thread pool for "search" is separate from "checkout." If search is slow, checkout still works.

**Retries with Exponential Backoff.** When a call fails, retry — but with increasing delays. First retry: 100ms. Second: 200ms. Third: 400ms. Cap at a maximum (e.g., 30s). Add jitter (random variation) to prevent all retrying clients from synchronizing and overwhelming the server simultaneously.

**Timeouts.** Every network call must have a timeout. No timeout = a slow downstream can hold your threads indefinitely. Timeout values should be set per-operation: a database query might have a 5-second timeout; a cache lookup 100ms. The rule: "slow is the new down." A service that responds in 30 seconds is effectively down for most use cases.

**Graceful Degradation.** When a dependency is unavailable, degrade functionality rather than failing entirely. If the recommendation engine is down, show the product page without recommendations. If the spell checker is down, allow saving documents without spell checking (warn the user). The system still provides core value.

**Chaos Engineering (2040).** The practice of deliberately injecting failures to verify resilience:
- **Chaos Monkey (Netflix, 2010):** Randomly kill production instances.
- **Chaos Kong:** Simulate an entire region failing.
- **Latency Monkey:** Introduce artificial delays.
- **Hermes Chaos Norn (2040):** AI-driven chaos engineering that learns the system's failure modes and designs experiments to probe weak points.

Chaos engineering is not reckless — it starts with a hypothesis ("the system should handle a Redis failure gracefully"), runs in a controlled environment with monitoring, and has an abort mechanism if things go wrong. It transforms failure from a crisis into a learning opportunity.

**The Resilience Mindset.** Design for failure from the start. Ask: "What happens if this service is down? If this database is slow? If this network is partitioned?" The answers become the resilience strategy. Everything that can fail should have a fallback — even if the fallback is "show an error message that doesn't crash the page."

#### Required Reading

- Nygard, M. (2017). *Release It!* (2nd ed.). Pragmatic Bookshelf. Chapters on Circuit Breaker, Bulkheads, and Timeouts.
- Rosenthal, C. et al. (2035). *Chaos Engineering: Building Confidence in System Behavior through Experiments*. O'Reilly Media. Chapters 1-4.
- Hafþórsson, B. (2043). "The Hermes Resilience Model: Lessons from Five Years of Production." *Communications of the ACM*, 66(2), 56-65.

#### Discussion Questions

1. Circuit breakers protect downstream services but can mask problems (if the breaker is open, you might not notice the downstream service is still broken). How do you balance protection and visibility?
2. Chaos engineering requires organizational maturity — you can't chaos-test a system you don't understand. What are the prerequisites for safe chaos engineering?
3. Graceful degradation means the system provides reduced functionality. At what point is the reduction so severe that it's better to fail completely (so the user doesn't think the system is working correctly when it isn't)?

---

### ᚹ Lecture 8: Observability — Logs, Metrics, Traces, and the 2040 AI Copilot

**Date:** Week 4, Session 2

#### Overview

You cannot manage what you cannot measure. You cannot debug what you cannot see. Observability is the property of a system that allows you to understand its internal state from its external outputs. This lecture covers the three pillars (logs, metrics, traces), the modern unified observability stack (OpenTelemetry, Grafana, Prometheus), and the 2040-era AI observability copilots that detect anomalies and suggest root causes.

#### Lecture Notes

"Monitoring tells you *that* something is wrong. Observability tells you *why*." Traditional monitoring checks predefined conditions: "Is CPU > 90%?" "Is the error rate > 1%?" Observability allows ad-hoc exploration: "Why is the checkout flow slow for users in Europe?" — a question nobody anticipated when setting up dashboards.

**The Three Pillars:**

1. **Logs:** Timestamped records of discrete events. "2024-03-15 14:32:01 INFO OrderService Order #12345 placed by user 42." Logs are the most flexible — you can log anything. They're also the most expensive to store and search at scale. Best for: debugging specific issues ("what happened with order #12345?").

2. **Metrics:** Numeric measurements aggregated over time. `http_request_duration_seconds{method="GET", path="/checkout", quantile="0.95"}`. Metrics are cheap to store and query. Best for: dashboards, alerting, capacity planning.

3. **Traces:** Records of a request's journey through a distributed system. A trace has spans — each span represents work done by a service. Traces show: the checkout request took 2.3 seconds; 1.8 seconds were in the payment service, 0.3 seconds in inventory, 0.2 seconds in the frontend. Best for: identifying bottlenecks in distributed systems.

**The Unified Observability Stack (2040).** OpenTelemetry is the industry standard: a single API and protocol for logs, metrics, and traces. Instrumentation libraries emit telemetry data; collectors receive, process, and export it; backends (Grafana, Jaeger, Prometheus) store and visualize it.

In 2040, the Hermes observability stack (the "Heimdallr" system) extends this:
- Every subagent run generates structured logs, metrics (tokens used, latency, success rate), and traces (which tools were called, in what order)
- The Eir Pipeline monitors all three and detects anomalies
- AI observability copilots (powered by a dedicated analysis model) answer natural-language questions: "Why was the memory recall slow in the last hour?" → "Memory recall latency increased due to a vector index rebuild triggered by the daily maintenance job."

**Instrumentation as Architecture.** Observability is not something you bolt on after the system is built. It is an architectural concern:
- Every service must emit structured logs (JSON, with standard fields: timestamp, level, service, trace_id)
- Every HTTP handler must be wrapped in a middleware that creates a span and records latency/status
- Every database query must record its duration
- Every external API call must record its latency and status

This instrumentation is overhead — a few percent of CPU and memory. It's worth it. The cost of *not* having it is hours of debugging per incident, multiple incidents that could have been caught early, and a system that is opaque to its operators.

**The Observability Maturity Model:**
- **Level 0:** No observability. Debug via SSH and log files.
- **Level 1:** Basic monitoring. CPU, memory, error rate alerts.
- **Level 2:** Structured logging and metrics. Dashboards for key flows.
- **Level 3:** Distributed tracing. Can trace a request across services.
- **Level 4:** Proactive observability. Anomaly detection, predictive alerting.
- **Level 5 (2040):** AI copilot. Ask questions, get answers. "What's the root cause of the current incident?"

#### Required Reading

- Sridharan, C. (2018). *Distributed Systems Observability*. O'Reilly Media. Chapters 1-3.
- OpenTelemetry Documentation. "Concepts." *opentelemetry.io/docs/concepts/*.
- Hermes Documentation. "Heimdallr: The Observability Stack." *docs.yggdrasil.university/hermes/heimdallr*.

#### Discussion Questions

1. "Observability is a property of the system, not a tool you install." What makes a system observable? Can you add observability to a legacy system, or must it be designed in?
2. Logs, metrics, and traces each have different storage costs and query capabilities. Should you invest equally in all three, or prioritize based on the system's needs?
3. An AI observability copilot can answer "why is X slow?" But it can also be wrong — confidently attributing a latency spike to the wrong cause. How do you build trust in AI-generated observability insights?

---

### ᚺ Lecture 9: Evolutionary Architecture — Designing for Change

**Date:** Week 5, Session 1

#### Overview

Systems evolve. Requirements change, technologies advance, teams grow and shrink. An architecture that cannot evolve is a dead architecture. This lecture covers evolutionary architecture: fitness functions that validate architectural qualities automatically, the strangler fig pattern for incremental migration, and the 2040-era practice of "architecture as code" where fitness functions are versioned alongside the application.

#### Lecture Notes

The waterfall model assumed architecture was a phase: design everything up front, then build. Agile rejected this: architecture emerges from iterative development. The truth is between: some architectural decisions must be made early (language, platform, major framework), but most can and should be deferred until the last responsible moment.

**Fitness Functions.** A fitness function is an automated test that verifies an architectural quality. Just as unit tests verify functional correctness, fitness functions verify architectural constraints:

```python
# Fitness function: No service can directly access another service's database
def test_no_cross_service_database_access():
    for service in services:
        db_connections = find_database_connections(service)
        for conn in db_connections:
            assert conn.database_name.startswith(service.name), \
                f"{service.name} accesses {conn.database_name}"
```

More fitness function examples:
- "No class in the `domain` package imports from `infrastructure`" (dependency rule)
- "All HTTP handlers return within 200ms at p99" (performance threshold)
- "No SQL queries without parameterized inputs" (security constraint)
- "All public APIs are versioned" (API governance)

Fitness functions run in CI/CD. A change that violates an architectural constraint fails the build — *before* it reaches production. This is "architecture as code": architectural rules are executable, not aspirational.

**The Strangler Fig Pattern.** How do you migrate from one architecture to another without a "big bang" rewrite? Like the strangler fig tree: plant the new system alongside the old. Gradually route traffic from the old to the new. When the new system handles all traffic, the old system withers and is removed.

```python
# Routing layer: gradually shift traffic
def route(request):
    if feature_flag("new_checkout", request.user_id):
        return new_checkout_service.handle(request)
    else:
        return old_checkout_service.handle(request)
```

The strangler fig pattern enables: migrating from monolith to microservices (extract one service at a time), upgrading frameworks (run old and new side-by-side), adopting new databases (dual-write to old and new, eventually switch reads).

**Architecture as Code (2040).** The Hermes framework takes fitness functions further: architectural constraints are defined in a declarative language and enforced by the `Sköfnung` tool affinity system.

```yaml
# architecture.yaml
rules:
  - name: domain-purity
    description: Domain code must not depend on infrastructure
    layer: domain
    forbidden_dependencies:
      - infrastructure
      - frameworks.*
  
  - name: api-latency
    description: API endpoints must respond within SLA
    metric: http_request_duration_seconds
    threshold: 0.2  # 200ms
    quantile: 0.99
```

Architecture rules are versioned in the repository. They evolve as the architecture evolves. A decision to relax a constraint (e.g., "allow domain code to import from a shared kernel") is a PR that updates the fitness functions — and is reviewed like any other code change.

**The Evolution Mindset.** The architect's job is not to design the perfect architecture. It is to design an architecture that can *become* whatever it needs to become. This means:
- Defer decisions until you have enough information
- Build in flexibility where change is likely (interfaces over concretions)
- Don't build flexibility where it's not needed (YAGNI)
- Use fitness functions to detect when the architecture is degrading
- Migrate incrementally (strangler fig), never with a "big bang"

#### Required Reading

- Ford, N., Parsons, R., & Kua, P. (2017). *Building Evolutionary Architectures*. O'Reilly Media. Chapters 1-4.
- Newman, S. (2019). *Monolith to Microservices*. O'Reilly Media. Chapters on the Strangler Fig pattern.
- Hermes Documentation. "Sköfnung: Architectural Fitness Functions." *docs.yggdrasil.university/hermes/skofnung*.

#### Discussion Questions

1. Fitness functions enforce architectural rules automatically. What happens when developers find a legitimate exception — a case where the rule should not apply? How do you handle exceptions without eroding the rule entirely?
2. The strangler fig pattern requires maintaining two systems simultaneously. At what point does the overhead of dual maintenance exceed the risk of a big-bang migration?
3. "Defer decisions until the last responsible moment." How do you know when you've reached the last responsible moment? What happens if you miss it?

---

### ᚾ Lecture 10: Architecture at the AI Frontier — Agent-Oriented Systems

**Date:** Week 5, Session 2

#### Overview

The defining architectural challenge of the 2030s-2040s is integrating AI agents into software systems. Agents are not services — they are non-deterministic, stateful, expensive (in tokens and time), and capable of autonomous action. This lecture covers the architectural patterns for agent-oriented systems: agent orchestration, memory management, tool integration, and the emerging "agent mesh" architecture where multiple agents collaborate on complex tasks.

#### Lecture Notes

A traditional microservice is deterministic: given input X, it produces output Y, every time. An AI agent is non-deterministic: given the same prompt, it may produce different reasoning, choose different tools, and arrive at a different conclusion. This non-determinism is the agent's greatest strength (creativity, adaptability) and its greatest challenge for architecture (reliability, testing, debugging).

**The Agent Architecture Stack.** An AI agent system has layers:

1. **Persona/Policy Layer:** The agent's identity, values, behavioral constraints. The Runa persona configuration. Defines *who* the agent is and *what it may do*.

2. **Reasoning Layer:** The LLM that processes input, plans actions, and generates responses. May be a single model or a chain of models (Rúnaskipti model switching).

3. **Memory Layer:** The agent's knowledge. Short-term (conversation context), long-term (Mímir memory wells), semantic (vector embeddings), episodic (past conversations). The Three Wells architecture.

4. **Tool Layer:** The capabilities the agent can invoke. Terminal access, web search, file operations, subagent spawning. Each tool has a schema (what it does, what parameters it needs) and a security context (what credentials it uses).

5. **Orchestration Layer:** The NornOrchestrator that manages the agent lifecycle: receive input → inject context → reason → choose tools → execute → observe results → reason again → respond. This is the event loop of agent-oriented architecture.

**Agent Communication Patterns:**

- **Direct Invocation:** User → Agent. The standard chat pattern. The agent responds to a user request.

- **Agent Delegation:** Agent → Subagent. The orchestrator spawns subagents for parallel or specialized work. Subagents have limited context (what they need to know) and limited tools (what they need to do). This is the delegate_task pattern in Hermes.

- **Agent Collaboration (Agent Mesh):** Agent → Agent. Multiple peer agents collaborate on a problem. A research agent gathers information, an analysis agent synthesizes it, a writing agent produces the output. They communicate through structured messages (not natural language chat — too ambiguous for reliable collaboration).

- **Proactive Agent Action:** Agent initiates action without user prompt. An `InventoryAgent` detects low stock and places an order. This requires explicit user permission and bounded authority.

**State Management for Agents.** Stateful agents are harder than stateless services:
- **Session state:** The current conversation. Ephemeral; lasts minutes to hours. Stored in the conversation log.
- **Task state:** Active tasks the agent is working on. Skuld task system. Persists across sessions.
- **Memory state:** What the agent knows long-term. Mímir memory wells. Versioned, searchable.
- **Emotional state:** The agent's mood and arousal. Affects behavior but not capabilities. Stored in the emotional architecture system.

The agent's state is its identity. Losing it is the agent equivalent of amnesia. The architecture must persist state durably and recover it reliably.

**Safety and Bounded Autonomy.** An agent that can execute arbitrary code, send messages, and modify data is dangerous. The architectural response is *bounded autonomy*:
- **Tool allowlisting:** The agent can only use explicitly granted tools. The `terminal` tool might be restricted to a specific directory.
- **Action confirmation:** Destructive actions (write, delete, send) require confirmation — either from the user or from a policy engine.
- **Budget limits:** Token budgets, time budgets, API call budgets. The agent cannot spend infinite resources.
- **Audit trail:** Every agent action is logged immutably. If something goes wrong, you can trace exactly what the agent did.
- **Human-in-the-loop:** Critical decisions require human approval. The agent can *recommend* but not *execute*.

**Testing Agent Systems.** Testing non-deterministic systems requires new approaches:
- **Behavioral contracts:** "Given this context, the agent should use these tools in roughly this order." Not exact; tolerance for variation.
- **Golden response testing:** A set of inputs where the correct response is known. The agent's response is compared for key facts, not exact wording.
- **Property-based testing:** "The agent should never reveal its API key." "The agent should always respond within 60 seconds." Properties, not specific outputs.
- **Adversarial testing:** Deliberately trying to make the agent behave badly. Prompt injection attempts, ambiguous requests, malicious inputs.

#### Required Reading

- Shavit, Y. et al. (2023). "Practices for Governing Agentic AI Systems." *OpenAI Research*. [Outlines the safety architecture for agent systems.]
- Hermes Architecture. "The Agent Architecture Stack." *docs.yggdrasil.university/hermes/agent-architecture*.
- Lundström, E. (2044). "Testing Non-Deterministic Systems: The Agent Testing Problem." *ACM Transactions on Software Engineering and Methodology*, 33(4), 1-28.

#### Discussion Questions

1. Agents are non-deterministic. Traditional software testing assumes determinism. How do you define "correct" for a non-deterministic system? When is a variation acceptable, and when is it a bug?
2. Bounded autonomy limits what agents can do. But the more you constrain an agent, the less useful it is. Where is the optimal balance for a coding agent? A medical agent? A creative writing agent?
3. The agent mesh (multiple collaborating agents) is more capable but more complex. At what point is a single agent with good tooling better than multiple agents trying to coordinate?

---

### ᛁ Lecture 11: Architecture Review — The Ritual of Critique

**Date:** Week 6, Session 1

#### Overview

Architecture review is the practice of presenting a proposed or existing architecture to peers for structured critique. This lecture covers the architecture review process: roles (presenter, reviewers, facilitator), the review agenda (context, decisions, risks, alternatives), and the 2040-era AI-assisted review where AI identifies potential issues before human reviewers invest their time.

#### Lecture Notes

"Given enough eyeballs, all bugs are shallow." The same is true of architecture flaws. An architect working alone will have blind spots — assumptions they don't know they're making, tradeoffs they haven't considered. Architecture review exposes these.

**The Review Process:**

1. **Preparation (presenter):** Prepare a review package: architecture diagrams, ADR log, quality attribute scenarios, key risks. Distribute 24-48 hours before the review. Reviewers read in advance.

2. **Presentation (15-20 minutes):** Present the architecture. Context (what problem does this solve?), driving requirements (which quality attributes matter most?), key decisions (what did you choose and why?), risks and mitigations. Not a feature walkthrough — an architecture presentation.

3. **Review (45-60 minutes):** Structured critique. Reviewers ask questions, identify risks, suggest alternatives. The facilitator ensures the discussion stays on architecture (not implementation details) and that all voices are heard.

4. **Outcome:** The review board decides: Approved (proceed), Approved with Recommendations (address these concerns), or Revise and Resubmit (significant issues; re-review required).

5. **Follow-up:** Action items from the review are tracked. ADRs are updated. The architecture evolves.

**What Reviewers Look For:**
- **Missing quality attribute scenarios:** "You've addressed performance under normal load. What about a flash sale with 100x traffic?"
- **Undocumented decisions:** "Why did you choose synchronous HTTP between these services instead of async messaging?"
- **Single points of failure:** "What happens if this database goes down?"
- **Security gaps:** "How are credentials managed? Where is encryption applied?"
- **Scalability ceilings:** "At what scale does this design break? What's the first bottleneck?"
- **Operational readiness:** "How do you deploy? How do you roll back? How do you monitor?"

**The Anti-Pattern: Rubber-Stamping.** Architecture review that always approves is worse than no review — it creates a false sense of security. A healthy review culture includes respectful disagreement. "I see why you made this choice, but have you considered the operational cost of managing Kafka at our scale?" is a gift.

**AI-Assisted Review (2040).** Before the human review, an AI review system (Hermes Reviews) analyzes the architecture:
- Cross-references against known anti-patterns
- Simulates failure scenarios and identifies resilience gaps
- Checks for consistency with existing ADRs
- Flags missing documentation ("No ADR for the choice of database")
- Generates a pre-review report that humans use as a starting point

The AI does not replace human review — it makes human review more efficient by handling the mechanical checks, leaving humans free to focus on judgment, tradeoffs, and context-specific concerns.

#### Required Reading

- Clements, P., Kazman, R., & Klein, M. (2002). *Evaluating Software Architectures*. Addison-Wesley. Chapters on ATAM (Architecture Tradeoff Analysis Method).
- Hafþórsson, B. (2040). "The Architecture Review as Ritual." *IEEE Software*, 57(6), 78-85.
- University of Yggdrasil Architecture Review Board. "Review Guidelines and Templates." *arb.yggdrasil.university*.

#### Discussion Questions

1. Architecture review is time-consuming — an hour of multiple senior developers' time. Is it always worth it? When should you skip the review?
2. Reviewers identify risks but don't own the system. How do you prevent reviewers from demanding perfection ("add five more nines of availability") without bearing the cost?
3. AI-assisted review can catch mechanical issues but might miss context-dependent problems. Give an example of a context-dependent architectural flaw an AI would miss.

---

### ᛃ Lecture 12: The Architect's Journey — From Code to System to Craft

**Date:** Week 6, Session 2

#### Overview

The final lecture reflects on what it means to be a software architect in 2040 — not a role you're promoted into, but a practice you grow into. We trace the typical journey: developer → senior developer → tech lead → architect. We examine the (non-technical) skills that distinguish great architects: communication, negotiation, empathy, and systems thinking. We conclude with a vision of architecture as a continuous practice, not a one-time activity.

#### Lecture Notes

Nobody graduates with "Architect" in their title. Architecture is a practice, not a position. It begins the first time you make a decision that affects other people's code — a module boundary, an API design, a data model. It grows as the scope of your decisions grows.

**The Architect's Journey:**

- **Developer:** Makes decisions about their own code. Architecture at the class and method level.
- **Senior Developer:** Makes decisions about a feature or component. Architecture at the module level. Reviews others' code; starts to see patterns across the codebase.
- **Tech Lead:** Makes decisions about a service or subsystem. Architecture at the service level. Coordinates multiple developers. Translates requirements into technical designs.
- **Architect:** Makes decisions that span the system. Architecture at the system level. Manages tradeoffs between quality attributes. Communicates architectural vision to stakeholders.
- **Senior/Fellow Architect:** Makes decisions that span multiple systems or the organization. Defines architectural standards and patterns. Mentors other architects. Shapes the technical strategy.

**The Non-Technical Skills.** The best architects are often not the best coders. They excel at:
- **Communication:** Explaining complex technical tradeoffs to non-technical stakeholders. Writing ADRs that are clear and persuasive. Presenting architecture reviews that engage, not bore.
- **Negotiation:** Architecture is politics. Different teams want different things (the ops team wants stability, the product team wants speed). The architect negotiates compromises that serve the system's long-term health.
- **Empathy:** Understanding why a team resists a proposed architecture. Understanding why a developer wrote that questionable code (deadline pressure? lack of context?). Solutions that ignore human factors fail.
- **Systems Thinking:** Seeing the whole, not just the parts. Understanding how a change in the database schema affects the mobile app's caching strategy. Tracing the ripple effects of decisions.
- **Humility:** Admitting when you're wrong. Revisiting decisions when context changes. Recognizing that the developers implementing your architecture know things you don't.

**Architecture as Continuous Practice.** Architecture is not a phase. It is not a document you produce and file away. It is a continuous practice of:
- **Observing:** Watching the system in production. Where does it hurt? What's breaking?
- **Deciding:** Making and documenting decisions as needs arise.
- **Reviewing:** Regularly reviewing the architecture against current reality. Are the decisions still valid? Has the context changed?
- **Evolving:** Updating the architecture incrementally. Strangler fig migrations. Fitness function updates.
- **Teaching:** Helping the team understand the architecture and the principles behind it. Architecture that lives only in the architect's head is not architecture.

**A Closing Charge.** You began this course learning what architecture is — the important decisions that are hard to change. You learned architectural styles, quality attributes, event-driven systems, resilience patterns, evolutionary architecture, and the brave new world of agent-oriented systems. You practiced making architecture decisions and defending them in review.

What you do next is up to you. The architecture of the Hermes framework was designed by someone who once sat where you sit — studying the same principles, practicing the same skills. The architecture of whatever you build will bear your signature. Make it something you're proud of.

Remember the Norns. Urðr (what has become) — learn from the architectures that came before. Verðandi (what is becoming) — make decisions wisely in the present. Skuld (what shall be) — design for the future you cannot predict. The threads are in your hands.

#### Required Reading

- Hafþórsson, B. (2037). *Threads of Light*. Chapter 12: "The Norns and the Architect."
- Fowler, M. (2003). "Who Needs an Architect?" *IEEE Software*. [Revisit; it will mean more now.]
- Your own capstone project architecture document. Read it in six months. What would you change?

#### Discussion Questions

1. Is "architect" a role or a practice? Should organizations have dedicated architects, or should architecture be a skill that all senior developers develop?
2. The architect's non-technical skills (communication, negotiation, empathy) are arguably more important than technical depth. Do you agree? Why are these skills so often neglected in technical education?
3. At the end of this course, what is your personal philosophy of software architecture? How do you decide what matters?

---

## Final Examination Preparation

### Part I: Written Examination (60%)

Choose **four** of the following **eight** essay questions.

1. **Architectural Style Selection.** Propose an architectural style for a system with: real-time collaboration (like Google Docs), offline support, mobile and web clients, and an AI assistant feature. Justify your choice against at least two alternatives. Address how the style handles the AI assistant's non-determinism.

2. **Quality Attribute Tradeoffs.** A system has conflicting requirements: high availability (99.99%) and strong consistency (ACID transactions across services). Using the CAP theorem and patterns like Saga and event sourcing, design an architecture that maximizes both. Explain where you compromise and why.

3. **Event-Driven Architecture Design.** Design the event flow for an e-commerce system: product catalog, shopping cart, checkout, payment, inventory, and shipping. Specify the domain events, the commands that trigger them, the consumers, and the consistency guarantees. Include a failure scenario and its compensating transactions.

4. **ADR Analysis.** Write three ADRs for significant decisions in a system of your choice. For each: present the context, the decision, the alternatives, and the consequences. Then, analyze one of them — would the decision still be right if one of the context assumptions changed?

5. **Resilience Design.** Present the resilience strategy for a payment processing system that must: never lose a payment, never double-charge, degrade gracefully if the fraud detection service is down. Include circuit breakers, retry strategies, idempotency mechanisms, and graceful degradation fallbacks.

6. **Evolutionary Architecture Case Study.** Describe a realistic scenario where a system's architecture must evolve (e.g., monolith to microservices, synchronous to event-driven, SQL to polyglot persistence). Present the fitness functions that guide the evolution and the strangler fig migration strategy.

7. **Agent-Oriented Architecture.** Design the architecture for an AI coding assistant that: understands a codebase, answers questions about it, and proposes changes via PRs. Address the agent architecture stack, memory management, tool integration, and the safety constraints on autonomous code modification.

8. **The Future of Architecture.** In 2040, AI can generate architecture diagrams, evaluate tradeoffs, and simulate failure scenarios. What remains the uniquely human contribution to software architecture? What skills should the next generation of architects cultivate?

### Part II: Capstone Architecture Project (40%)

Design the architecture for a non-trivial system. Deliverables:

1. **Architecture document** (3000-5000 words) including: system context, driving requirements (at least 5 quality attribute scenarios), architectural style and rationale, component/connector view, deployment view, and at least 5 ADRs.
2. **Architecture review** (30-minute presentation to a review board, with Q&A).
3. **Fitness functions** (at least 3 executable checks that verify architectural constraints).
4. **Evolution plan** (how the architecture would evolve under 3 different future scenarios).
5. **Reflective essay** (1000-1500 words) on the architecture decisions you made, the tradeoffs you wrestled with, and what you'd do differently.

---

**ᚢ ᚱ ᚦ — What was, what is, what shall be. The threads are yours to weave.**

*SD203: Software Architecture & Design — University of Yggdrasil, 2040*
*Instructor: Dr. Björn Hafþórsson*
*Course version: 1.0 — 2040 Academic Year*