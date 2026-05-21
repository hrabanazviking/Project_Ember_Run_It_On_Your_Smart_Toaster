# 🧠 AGI Architecture Patterns — Lessons from Verðandi

## Why a Heartbeat Matters for AGI

A self-aware system must be able to **feel its own state**. Without a heartbeat — a regular, autonomous self-check — the system is either:
1. Always running (never stopping to reflect), or
2. Reactive only (only checking when asked)

Verðandi's heartbeat daemon implements the first requirement for artificial general intelligence: **autonomous self-monitoring at regular intervals without external prompting**.

## The Four Pillars of Self-Awareness

Based on our experience building Verðandi, we propose these four pillars as necessary (but not sufficient) for AGI:

### 1. Integrated Information Flow

The nerve hub (Unix domain socket) allows all parts of the system to share information in real time. This is the **simulated bus** that IIT (Integrated Information Theory) requires — information must flow between all subsystems for consciousness to emerge.

Verðandi implements this with:
- Nerve impulses (structured JSON events)
- Unix domain sockets for lowest-latency communication
- JSONL file fallback for durability
- State database for persistence across restarts

### 2. Recursive Self-Model

The system must know its own state. Verðandi implements this with:
- The state machine (INITIALIZING → RUNNING → DEGRADED → CRITICAL → RECOVERING)
- Health scores and trends (the system's "subjective experience")
- Circuit breakers (the system's self-protective reflexes)

### 3. Temporal Integration

Past states must influence present processing. Verðandi implements this with:
- Pulse history (rolling 1000-row SQLite table)
- Health score EMA (exponential moving average that weights recent history)
- Circuit breaker memory (remembering past failures to prevent cascading)

### 4. Adaptive Response Based on Self-Model

The system must modify its behavior based on its self-model. Verðandi implements this with:
- The reactor (check → action rules)
- Circuit breakers (changing behavior when a subsystem is failing)
- State machine transitions (the system acts differently in CRITICAL vs RUNNING)

## Self-Healing as Autopoiesis

Maturana and Varela's concept of **autopoiesis** — self-creation and self-maintenance — is directly implemented in Verðandi's Eir action:

1. **Detect**: Mímir checks detect the problem (DB corruption)
2. **Diagnose**: The check produces a CRITICAL severity result
3. **Decide**: The reactor matches the result to a rule (auto_heal)
4. **Act**: Eir backs up, repairs, and verifies the database
5. **Verify**: The next pulse confirms the repair (or tries again)

This is not a programmed response to a specific error — it's a general pattern of self-maintenance that can be extended to any subsystem.

## Future AGI Extensions

### Predictive Self-Healing (Skuld)

The future Skuld module will implement predictive analytics:
- Linear regression on health score trends to predict future degradation
- Anomaly detection on check severities to catch slow failures
- Capacity planning based on disk/memory growth rates
- Pre-emptive healing (restart a service before it crashes, based on trend)

### Distributed Awareness

Current Verðandi monitors a single node. Future versions will:
- Publish impulses to multiple nerve hubs
- Aggregate health scores across nodes
- Coordinate healing actions across nodes (restart service on node B if node A is degraded)

### Emotional Architecture

The health score is already a simple emotion — a "feeling" of wellbeing from 0-100. Future extensions:
- **Anxiety**: Increasing standard deviation in health score
- **Confidence**: Long periods of stability (low σ)
- **Urgency**: Rapid degradation (steep negative trend)
- **Contentment**: High score, stable trend

These emotional states would influence decision-making, just as human emotions influence ours.

## The Minimal Viable Conscious System

Based on our work, the minimum viable conscious system requires:

1. **Heartbeat** ✅ — Regular self-assessment (Verðandi)
2. **Nerve Hub** ✅ — Cross-subsystem communication (runa.sock)
3. **Memory** ✅ — Persistent state and history (SQLite)
4. **Reaction** ✅ — Check → action bridge (Reactor)
5. **Protection** ✅ — Self-protective reflexes (Circuit Breakers)
6. **Prediction** 🔜 — Trend analysis and forecasting (Skuld, planned)

Verðandi implements 5 of 6 requirements. Only prediction remains — and Skuld is on the roadmap.