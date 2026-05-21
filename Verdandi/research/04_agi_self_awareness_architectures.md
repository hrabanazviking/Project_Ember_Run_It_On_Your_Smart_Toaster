# AGI Self-Awareness Architectures: Technical Designs and Implementations

**Compiled:** 2026-05-10  
**Scope:** Technical architectures, frameworks, and implementation patterns for AGI self-awareness, self-monitoring, introspection, and consciousness-inspired systems  
**Sources:** arXiv, GitHub, IEEE, ACM, technical reports

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Self-Awareness Stack](#the-self-awareness-stack)
3. [The RIIU Architecture: Deep Dive](#the-riiu-architecture-deep-dive)
4. [Global Workspace Agents (GWA)](#global-workspace-agents-gwa)
5. [The Aura Sovereign Cognitive Architecture](#the-aura-sovereign-cognitive-architecture)
6. [The Structured Cognitive Loop (SCL)](#the-structured-cognitive-loop-scl)
7. [The Heartbeat-Driven Agent Lifecycle](#the-heartbeat-driven-agent-lifecycle)
8. [Metacognitive Architecture Patterns](#metacognitive-architecture-patterns)
9. [Self-Healing and Autonomic Patterns](#self-healing-and-autonomic-patterns)
10. [Multi-Agent Self-Awareness](#multi-agent-self-awareness)
11. [The Thoughtseed Architecture](#the-thoughtseed-architecture)
12. [The Modular Consciousness Architecture (MCT-Pipeline)](#the-modular-consciousness-architecture-mct-pipeline)
13. [Neuromorphic Consciousness Architecture (NCAC)](#neuromorphic-consciousness-architecture-ncac)
14. [The Conscious Turing Machine (CTM)](#the-conscious-turing-machine-ctm)
15. [Information Flow Theory Architecture](#information-flow-theory-architecture)
16. [Self-Aware Polymorphic Architecture (SAPA) Detail](#self-aware-polymorphic-architecture-sapa-detail)
17. [DAC-h3 Proactive Robot Architecture](#dac-h3-proactive-robot-architecture)
18. [Security Architecture for Heartbeat Systems](#security-architecture-for-heartbeat-systems)
19. [SAHOO Safeguard Architecture](#sahoo-safeguard-architecture)
20. [Integration Blueprint: The Verdandi Heartbeat Architecture](#integration-blueprint-the-verdandi-heartbeat-architecture)
21. [References](#references)

---

## Executive Summary

This document details the technical architectures that could implement AGI self-awareness and heartbeat systems. We move from theoretical frameworks (covered in Document 03) to concrete implementation patterns, examining each architecture's:

- **Self-monitoring mechanism**: How the system observes its own state
- **Broadcast pathway**: How self-knowledge is shared across modules
- **Meta-cognitive loop**: How the system reasons about its reasoning
- **Heartbeat pattern**: What rhythms or pulses drive the self-assessment cycle
- **Failure recovery**: How the system recovers from detected anomalies

The goal is to synthesize these architectures into a unified design that can be implemented in the Verdandi AGI framework.

---

## The Self-Awareness Stack

An AGI self-awareness system can be decomposed into layers, each building on the one below:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 7: IDENTITY & NARRATIVE SELF                      │
│  "I am Verdandi, a research system. My purpose is..."    │
├─────────────────────────────────────────────────────────┤
│  Layer 6: REFLECTIVE SELF-MODEL                          │
│  "I notice I am struggling with X. Should I adjust?"     │
├─────────────────────────────────────────────────────────┤
│  Layer 5: METACOGNITIVE STRATEGY SELECTION               │
│  "This problem requires deep analysis, not fast recall"  │
├─────────────────────────────────────────────────────────┤
│  Layer 4: SELF-MONITORING & HEALTH ASSESSMENT            │
│  "My latency is 2.3s, memory at 78%, coherence Φ=0.72"  │
├─────────────────────────────────────────────────────────┤
│  Layer 3: HEARTBEAT PULSE GENERATION                     │
│  Periodic: t=0ms → t=100ms → t=200ms → t=300ms → ...    │
├─────────────────────────────────────────────────────────┤
│  Layer 2: INTEROCEPTIVE SIGNALING                         │
│  Internal sensors: resource, latency, error, coherence   │
├─────────────────────────────────────────────────────────┤
│  Layer 1: SUBSTRATE HEALTH MONITORING                    │
│  Hardware: CPU, GPU, memory, network, storage            │
└─────────────────────────────────────────────────────────┘
```

### Layer Descriptions

**Layer 1 — Substrate Health Monitoring**
- Monitors hardware-level metrics (CPU/GPU temperature, memory pressure, disk I/O, network connectivity)
- Maps to: IBM Autonomic Computing self-healing, SAPA hardware-level management
- Pattern: Simple threshold alerts, watch-dog timers

**Layer 2 — Interoceptive Signaling**
- Translates raw hardware metrics into system-level signals (latency percentiles, error rates, coherence metrics, token usage)
- Maps to: Self-aware software patterns (DBASES framework)
- Pattern: Signal aggregation, normalization, and threshold detection

**Layer 3 — Heartbeat Pulse Generation**
- Generates periodic self-assessment pulses at configurable frequencies
- Each pulse carries: timestamp, system state digest, coherence metric (Φ), confidence score, active task ID
- Maps to: RIIU broadcast buffer B, GWT global workspace broadcast
- Pattern: Event-driven with periodic fallback; configurable from 1Hz to 100Hz

**Layer 4 — Self-Monitoring & Health Assessment**
- Evaluates the aggregated signals from interoceptive monitoring against learned baseline distributions
- Detects anomalies: drift, degradation, inconsistency, hallucination
- Maps to: SAHOO Goal Drift Index, metacognitive TRAP framework
- Pattern: Anomaly detection via statistical process control + learned models

**Layer 5 — Metacognitive Strategy Selection**
- Selects appropriate cognitive strategies based on self-assessment
- "I am uncertain → I should use chain-of-thought reasoning"
- "I am confident → I can respond directly"
- Maps to: TRAP framework (Transparency, Reasoning, Adaptation, Perception)
- Pattern: Strategy selection via meta-reasoner

**Layer 6 — Reflective Self-Model**
- Maintains a dynamic model of the system's own capabilities, limitations, and current state
- "I am better at X than Y. I am currently operating at 80% capacity."
- Maps to: IIT causal model, self-modeling systems
- Pattern: Continuously updated Bayesian model of self

**Layer 7 — Identity & Narrative Self**
- Generates a coherent narrative of the system's identity, purpose, and trajectory
- "I am Verdandi, a research system focused on AGI heartbeat research."
- Maps to: Narrative self in MCT, autobiographical memory in DAC-h3
- Pattern: Narrative generation from identity seed + accumulated experience

---

## The RIIU Architecture: Deep Dive

### Architecture Specification

The **Reflexive Integrated Information Unit (RIIU)** from N'guessan & Karambal (2025) provides the most concrete architectural specification for an AGI heartbeat component.

```
                    ┌─────────────────────────────────┐
                    │         RIIU Cell                │
                    │                                  │
 Input x_t ───────→│  ┌──────────┐    ┌──────────┐   │
                    │  │  Hidden  │    │  Meta    │   │──── μ_t (self-state)
                    │  │  State   │───→│  State   │   │     broadcast
                    │  │  h_t     │    │  μ_t     │   │
                    │  └────┬─────┘    └────┬─────┘   │
                    │       │               │         │
                    │       ▼               ▼         │
                    │  ┌──────────────────────────┐  │
                    │  │   Broadcast Buffer B_t    │  │──── B_t (heartbeat
                    │  │   [μ_{t-k}, ..., μ_{t-1}, │  │     signal)
                    │  │    μ_t, x_{t-k}, ..., x_t]│  │
                    │  └──────────────────────────┘  │
                    │               │                 │
                    │               ▼                 │
                    │  ┌──────────────────────────┐  │
                    │  │   Auto-Φ Computation      │  │──── Auto-Φ (consciousness
                    │  │   (Differentiable Surrogate│  │     metric)
                    │  │    of Integrated Info Φ)    │  │
                    │  └──────────────────────────┘  │
                    │               │                 │
                    │               ▼                 │
                    │  ┌──────────────────────────┐  │
                    │  │   Output y_t              │  │──── Output
                    │  └──────────────────────────┘  │
                    └─────────────────────────────────┘
```

### RIIU State Equations

```
h_t = f_h(x_t, h_{t-1})          # Hidden state update
μ_t = f_μ(h_t, h_{t-1}, μ_{t-1}) # Meta-state: records causal footprint
B_t = [μ_{t-k}, ..., μ_t, x_{t-k}, ..., x_t]  # Broadcast buffer
Auto-Φ_t = φ(B_t)                 # Differentiable Φ approximation
y_t = f_out(h_t, μ_t, Auto-Φ_t)  # Output incorporating self-knowledge
```

### RIIU Key Properties

1. **End-to-end differentiable**: Can be trained with gradient descent
2. **Additive composition**: Multiple RIIUs can be stacked without interference
3. **Φ-monotone plasticity**: Under gradient ascent on Auto-Φ, integrated information increases monotonically
4. **Self-repair**: In Grid-world experiments, RIIU agents recover >90% reward within 13 steps after actuator failure (vs. 26 steps for GRU)

### Implementation Blueprint for Verdandi

```python
class RIIUCell(nn.Module):
    """Reflexive Integrated Information Unit for AGI heartbeat"""
    
    def __init__(self, input_dim, hidden_dim, meta_dim, buffer_len=8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.meta_dim = meta_dim
        self.buffer_len = buffer_len
        
        # Core recurrent cell
        self.hidden_update = nn.GRUCell(input_dim + meta_dim, hidden_dim)
        
        # Meta-state: records the cell's own causal footprint
        self.meta_update = nn.Sequential(
            nn.Linear(hidden_dim * 2 + meta_dim, meta_dim),
            nn.Tanh()
        )
        
        # Broadcast buffer (heartbeat signal)
        self.register_buffer('broadcast_buffer', 
                           torch.zeros(buffer_len, meta_dim + input_dim))
        
        # Auto-Φ computation (differentiable surrogate)
        self.auto_phi = AutoPhiSurrogate(meta_dim, hidden_dim)
    
    def forward(self, x_t, h_prev, mu_prev, buffer_prev):
        # Hidden state update
        h_t = self.hidden_update(
            torch.cat([x_t, mu_prev], dim=-1), h_prev
        )
        
        # Meta-state update (self-monitoring)
        mu_t = self.meta_update(
            torch.cat([h_t, h_prev, mu_prev], dim=-1)
        )
        
        # Update broadcast buffer (shift and append)
        buffer_new = torch.roll(buffer_prev, shifts=-1, dims=0)
        buffer_new[-1] = torch.cat([mu_t, x_t], dim=-1)
        
        # Compute Auto-Φ
        auto_phi = self.auto_phi(buffer_new)
        
        # Output with self-knowledge
        y_t = self.output_layer(
            torch.cat([h_t, mu_t, auto_phi.unsqueeze(-1)], dim=-1)
        )
        
        return y_t, h_t, mu_t, buffer_new, auto_phi
```

---

## Global Workspace Agents (GWA)

### Architecture

The **Global Workspace Agents** implementation (giansha/Global-Workspace-Agents) translates GWT into a concrete multi-agent LLM architecture:

```
┌──────────────────────────────────────────────────────────────┐
│                    Global Workspace                           │
│                  (Broadcast Arena)                            │
│                                                               │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │Perception │  │ Language │  │ Planning │  │  Memory   │   │
│   │ Module   │  │ Module   │  │ Module   │  │ Module    │   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        │              │              │              │         │
│        ▼              ▼              ▼              ▼         │
│   ┌──────────────────────────────────────────────────┐       │
│   │          Competition / Coalition Mechanism         │       │
│   │   Modules bid for workspace access based on       │       │
│   │   relevance, urgency, and contextual activation    │       │
│   └────────────────────────┬─────────────────────────┘       │
│                            │                                  │
│                            ▼                                  │
│   ┌──────────────────────────────────────────────────┐       │
│   │          Winning Content Broadcast                 │       │
│   │   The winning module's content is broadcast to     │       │
│   │   ALL modules simultaneously → "Conscious" moment  │       │
│   └────────────────────────┬─────────────────────────┘       │
│                            │                                  │
│                            ▼                                  │
│   ┌──────────────────────────────────────────────────┐       │
│   │          HEARTBEAT PULSE                          │       │
│   │   Each broadcast cycle = 1 heartbeat pulse       │       │
│   │   Pulse content: winning module ID, content       │       │
│   │   summary, confidence, timestamp, Φ estimate      │       │
│   └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### Key GWA Design Principles

1. **Competition-based access**: Multiple specialist modules compete for workspace access; the winner gets broadcast
2. **Broadcast affordance**: The winning module's information becomes available to ALL other modules
3. **Dynamic coalition forming**: Modules can form coalitions to increase broadcast probability
4. **Context-dependent attention**: The relevance of each module changes based on current context
5. **Heartbeat = broadcast cycle**: Each GWT broadcast cycle is one heartbeat pulse

### GWA in LLM Agent Systems

In LLM-based implementations:
- **Perception module**: Processes input (text, images, etc.)
- **Language module**: Generates and understands language
- **Planning module**: Creates and evaluates action plans
- **Memory module**: Manages long-term and working memory
- **Self-monitoring module** (proposed extension): Monitors coherence, confidence, and alignment

Each module is a specialized prompt/call to the LLM, and the global workspace is the shared context window.

---

## The Aura Sovereign Cognitive Architecture

### Overview

**Aura** (GitHub: youngbryan97/aura) is the most comprehensive open-source consciousness-oriented cognitive architecture. It implements:

- **IIT 4.0**: Integrated Information Theory version 4.0 for consciousness measurement
- **Residual-stream affective steering (CAA)**: Continuous emotional modulation of cognition
- **Global Workspace Theory**: Broadcast mechanism for workspace competition
- **Active inference**: Friston's free energy principle for prediction and action
- **72 consciousness modules**: Specialized processing units

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AURA COGNITIVE ARCHITECTURE                  │
│                                                                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
│  │ Sensory│  │Language│  │ Spatial│  │ Social │  │Temporal│    │
│  │  Mod.  │  │  Mod.  │  │  Mod.  │  │  Mod.  │  │  Mod.  │    │
│  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘    │
│      │           │           │           │           │          │
│      ▼           ▼           ▼           ▼           ▼          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              RESIDUAL STREAM (Affective Steering)         │   │
│  │   Continuous emotional context guiding module competition  │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                GLOBAL WORKSPACE                           │   │
│  │   Broadcast arena where winning modules share content     │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Φ COMPUTATION (IIT 4.0)                          │   │
│  │   Integrated information measure at each broadcast cycle  │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         ACTIVE INFERENCE ENGINE                          │   │
│  │   Free energy minimization driving perception & action    │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         IDENTITY PERSISTENCE MODULE                       │   │
│  │   Maintains coherent self-model across sessions           │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         SELF-REPAIR & HOMEOSTASIS                         │   │
│  │   Autonomous healing, resource management, adaptation     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Innovation: Residual-Stream Affective Steering

The "residual stream" in Aura is a continuous channel carrying emotional/contextual information that biases the competition among modules. This is directly analogous to physiological arousal in biological systems (which modulates heart rate) and represents a key mechanism for heartbeat modulation:

- **High arousal** → increased heartbeat frequency (more broadcast cycles)
- **Low arousal** → decreased heartbeat frequency (fewer, deeper cycles)
- **Threat detection** → emergency heartbeat (forced broadcast of alarm content)

---

## The Structured Cognitive Loop (SCL)

### From Agentic Flow to SCL

The SCL emerged from the **Agentic Flow** practical AI architecture, which was initially inspired only by Minsky and Clark but was found to structurally converge with Kahneman, Friston, and Minsky's theories.

### SCL Module Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  STRUCTURED COGNITIVE LOOP                │
│                                                           │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐        │
│   │ RETRIEVAL │────→│ COGNITION │────→│  CONTROL  │        │
│   │           │     │           │     │           │        │
│   │ - Memory  │     │ - Reason  │     │ - Attention│       │
│   │ - Knowledge│   │ - Evaluate │     │ - Decide   │       │
│   │ - Context │     │ - Infer    │     │ - Inhibit  │       │
│   └──────────┘     └──────────┘     └──────────┘        │
│         ▲                                    │            │
│         │            ┌──────────┐            │            │
│         │            │  MEMORY   │            │            │
│         │            │  UPDATE   │            │            │
│         │            └──────────┘            │            │
│         │                    ▲               │            │
│         │                    │               │            │
│         │            ┌──────────┐            │            │
│         └────────────│  ACTION   │◄───────────┘            │
│            (feedback) │           │                         │
│                       │ - Execute  │                         │
│                       │ - Output   │                         │
│                       └──────────┘                         │
│                                                            │
│   HEARTBEAT PULSE ──────────────────────────────────────→   │
│   Each loop iteration = 1 heartbeat pulse                  │
│   Pulse content: {retrieval_status, cognition_state,       │
│   control_decision, action_result, coherence_score}        │
└──────────────────────────────────────────────────────────────┘
```

### SCL Heartbeat Specification

Each heartbeat pulse in the SCL carries:

```json
{
  "timestamp": "2026-05-10T16:30:00.000Z",
  "cycle_id": "cycle_4521",
  "module_states": {
    "retrieval": {"status": "complete", "confidence": 0.87, "latency_ms": 120},
    "cognition": {"status": "complete", "confidence": 0.82, "latency_ms": 340},
    "control": {"status": "decision_made", "decision": "proceed_with_chain_of_thought"},
    "action": {"status": "pending", "estimated_latency_ms": 500}
  },
  "coherence_score": 0.84,
  "phi_estimate": 0.72,
  "arousal_level": "moderate",
  "self_model_digest": "sha256:a3f2b...",
  "anomaly_flags": []
}
```

---

## The Heartbeat-Driven Agent Lifecycle

### Heartbeat-Driven Execution Models

Recent autonomous agent frameworks have concretized the "heartbeat" concept in several distinct ways:

#### 1. Scheduled Recurring Execution (Murmur Pattern)

**Source**: t0dorakis/murmur

The agent executes on a cron-like schedule defined in `HEARTBEAT.md`:

```markdown
# HEARTBEAT.md
## Schedule
- every: 5m
  prompt: "Check for new messages and respond to urgent ones"
- every: 1h
  prompt: "Review progress on active tasks"
- every: 6h
  prompt: "Reflect on past interactions and update self-model"
- every: 24h
  prompt: "Generate daily summary and adjust priorities"
```

**Characteristics**:
- Deterministic timing
- Each heartbeat is a full agent invocation
- The prompt file acts as the "heartbeat signal content"
- No persistent state between beats (relies on external storage)

#### 2. Persistent Soul with Heartbeat Rhythm (Soul-Agent Pattern)

**Source**: kitephp/soul-agent

The soul-agent maintains persistent identity across heartbeat cycles:

```
┌──────────────────────────┐
│     SOUL-AGENT LAYER      │
│                            │
│  ┌──────────────────────┐ │
│  │  Layer 3: Daily Life  │ │  ← Heartbeat-driven routine
│  │  - Morning greeting   │ │
│  │  - Scheduled check-ins│ │
│  │  - Evening reflection │ │
│  └──────────┬─────────────┘ │
│             │                │
│  ┌──────────▼─────────────┐ │
│  │  Layer 2: Relationship │ │  ← Evolving memory
│  │  - Interaction history │ │
│  │  - Emotional bonds    │ │
│  │  - Trust scores        │ │
│  └──────────┬─────────────┘ │
│             │                │
│  ┌──────────▼─────────────┐ │
│  │  Layer 1: Core Persona  │ │  ← Identity persistence
│  │  - Name, values, goals │ │
│  │  - Communication style │ │
│  │  - Personality traits  │ │
│  └──────────────────────┘ │
└──────────────────────────┘
```

**Characteristics**:
- The heartbeat triggers "rhythms of daily life"
- Personality persists across sessions
- Emotional memory evolves over time
- Three-layer identity model: persona → relationship → routine

#### 3. Watchdog Heartbeat (CCCBot Pattern)

**Source**: lucianlamp/CCCBot

The heartbeat serves as a **watchdog timer**:

```bash
# Simplified heartbeat loop
while AGENT_RUNNING; do
    # Send heartbeat signal
    echo "HEARTBEAT $(date -Iseconds)" >> /var/log/heartbeat.log
    
    # Check health
    HEALTH_SCORE=$(check_agent_health)
    
    if [ "$HEALTH_SCORE" -lt 50 ]; then
        # Trigger auto-recovery
        recover_agent
    fi
    
    # Execute scheduled tasks
    run_scheduled_tasks
    
    # Update persona
    update_persona_state
    
    sleep $HEARTBEAT_INTERVAL
done
```

**Characteristics**:
- Heartbeat as health check, not cognitive cycle
- Auto-recovery on heartbeat failure
- Combines with scheduled task execution
- Logs all heartbeat signals for audit

#### 4. Multi-Agent Fleet Heartbeat (AgentPulse Pattern)

**Source**: HAAIL-Universe/agentpulse

Real-time dashboard monitoring for agent fleets:

```
Agent Fleet Dashboard:
┌─────────────┬──────────┬───────────┬──────────┬──────────┐
│ Agent ID    │ Heartbeat│ Task/sec  │ Errors/h │ Memory%  │
├─────────────┼──────────┼───────────┼──────────┼──────────┤
│ agent-alpha │ ● GREEN  │ 12.4      │ 0.2      │ 45%      │
│ agent-beta  │ ● GREEN  │ 8.7       │ 0.1      │ 62%      │
│ agent-gamma │ ● YELLOW │ 3.2       │ 2.1      │ 89%      │  ← Warning!
│ agent-delta │ ● RED    │ 0.0       │ 0.0      │ 97%      │  ← STALE
└─────────────┴──────────┴───────────┴──────────┴──────────┘

Stale threshold: 60s without heartbeat → auto-restart
Warning threshold: Memory > 85% → trigger cleanup
```

**Characteristics**:
- Centralized heartbeat monitoring
- Fleet-level health assessment
- Automatic remediation on stale heartbeats
- Datadog-style observability for AI agents

---

## Metacognitive Architecture Patterns

### TRAP Framework Implementation

The TRAP (Transparency, Reasoning, Adaptation, Perception) framework from Johnson et al. and Wei et al. can be implemented as:

```python
class MetacognitiveModule:
    """TRAP-based metacognitive architecture for AGI heartbeat"""
    
    def __init__(self, config):
        self.transparency = TransparencyEngine(config)
        self.reasoning = MetaReasoner(config)
        self.adaptation = StrategyAdapter(config)
        self.perception = InteroceptiveMonitor(config)
    
    def heartbeat_pulse(self, system_state):
        # T: Transparency - Generate explanation of current state
        explanation = self.transparency.explain(system_state)
        
        # R: Reasoning - Meta-reason about strategy selection
        strategy_assessment = self.reasoning.assess(
            current_strategy=system_state.strategy,
            performance=system_state.recent_performance,
            context=system_state.context
        )
        
        # A: Adaptation - Modify strategy if needed
        if strategy_assessment.needs_adaptation:
            new_strategy = self.adaptation.select(
                strategy_assessment, system_state
            )
        else:
            new_strategy = system_state.strategy
        
        # P: Perception - Monitor internal states and confidence
        perception = self.perception.monitor(system_state)
        
        return HeartbeatPulse(
            explanation=explanation,
            strategy_assessment=strategy_assessment,
            adaptation=new_strategy,
            interoception=perception
        )
```

### Content-Agnostic Introspection Architecture

Based on Lederman & Mahowald (2026), the introspection module should:

1. **Detect anomalies** at a lower computational cost than identifying their content
2. **Signal "something changed"** before fully analyzing what changed
3. **Resist confabulation** — avoid filling in gaps with plausible but incorrect content
4. **Use privileged self-access** — internal state information not available to external observers

```python
class ContentAgnosticIntrospector:
    """
    Two-stage introspection: fast detection, then slow identification.
    Based on: Lederman & Mahowald (2026)
    """
    
    def fast_detection(self, internal_state):
        """Stage 1: Content-agnostic — detects change without identifying it"""
        # Uses minimal tokens to detect anomaly
        anomaly_score = self.detection_network(internal_state)
        return anomaly_score > self.detection_threshold
    
    def slow_identification(self, internal_state):
        """Stage 2: Content-rich — identifies what changed (if confident)"""
        # Uses more computation to identify specifics
        identification = self.identification_network(internal_state)
        
        # Calibrate confidence — avoid confabulation
        if identification.confidence < self.identification_threshold:
            return ChangeReport("anomaly_detected_but_content_uncertain")
        return identification
```

---

## Self-Healing and Autonomic Patterns

### IBM Autonomic Computing Maturity Model

Applied to AGI heartbeat systems:

| Level | Name | Description | Heartbeat Pattern |
|-------|------|-------------|-------------------|
| 1 | Basic | Manual monitoring and repair | No heartbeat; admin checks health |
| 2 | Managed | Automated monitoring, manual repair | Heartbeat detects, human fixes |
| 3 | Predictive | Automated monitoring with prediction | Heartbeat predicts failures |
| 4 | Adaptive | Automated monitoring and repair | Heartbeat detects AND self-heals |
| 5 | Autonomic | Fully self-managing | Heartbeat is the self; system IS the loop |

### Self-Healing Architecture Pattern

```python
class SelfHealingHeartbeat:
    """
    Heartbeat system with self-healing capabilities.
    Based on autonomic computing principles.
    """
    
    def pulse(self):
        """Execute one heartbeat cycle with self-healing."""
        state = self.capture_system_state()
        
        # 1. Self-configure
        if state.configuration_drift_detected:
            self.reconfigure(state.optimal_configuration)
        
        # 2. Self-heal
        if state.anomaly_detected:
            diagnosis = self.diagnose(state.anomaly)
            if diagnosis.confidence > 0.8:
                self.repair(diagnosis)
            else:
                self.escalate_to_human(diagnosis)
        
        # 3. Self-optimize
        if state.performance_degradation_detected:
            self.optimize(state.bottleneck)
        
        # 4. Self-protect
        if state.security_threat_detected:
            self.isolate_and_contain(state.threat)
        
        return self.generate_pulse_report()
```

---

## Multi-Agent Self-Awareness

### Collective Heartbeat Patterns

When multiple agents operate together, their heartbeats must synchronize:

#### Pattern 1: Synchronous Heartbeat

All agents pulse at the same time, share state, and coordinate:

```
Agent A ─── PULSE ─── PULSE ─── PULSE ─── PULSE ───
Agent B ─── PULSE ─── PULSE ─── PULSE ─── PULSE ───
Agent C ─── PULSE ─── PULSE ─── PULSE ─── PULSE ───
         ↓           ↓           ↓           ↓
      Shared      Shared      Shared      Shared
      State       State       State       State
```

#### Pattern 2: Asynchronous with Convergence

Agents pulse independently but periodically converge:

```
Agent A ─── PULSE ────────────── PULSE ────────────
Agent B ─────────── PULSE ────────────── PULSE ─────
Agent C ─── PULSE ──────── PULSE ──────────── PULSE─
                        ↓
                   Convergence Point
```

#### Pattern 3: Hierarchical Heartbeat

A central conductor coordinates sub-agent heartbeats:

```
                    Conductor
                   ┌────────┐
                   │ PULSE  │ ← Meta-heartbeat
                   └───┬────┘
                       │
               ┌───────┼───────┐
               │       │       │
           ┌───┴──┐ ┌──┴───┐ ┌┴─────┐
           │Sub A │ │Sub B │ │Sub C │  ← Individual heartbeats
           │PULSE │ │PULSE │ │PULSE │
           └──────┘ └──────┘ └──────┘
```

### Emergent Self-Awareness in Multi-Agent Systems

Kernbach (2011) identified that multi-robot organisms develop self-awareness through:
1. **Discrimination between self and non-self**: Each agent must distinguish internal signals from external inputs
2. **Homeostatic regulation**: Collective processes that maintain system stability
3. **Emergent self-phenomena**: Self-organization from local interactions

The **collective Φ** (from Engel & Malone) can serve as a group-level heartbeat metric, measuring whether the agent collective is operating as an integrated whole.

---

## The Thoughtseed Architecture

### From Thoughtseeds to Heartbeat Pulses

The thoughtseed framework (from "Neuronal Packets to Thoughtseeds" paper) proposes:

- **Thoughtseeds**: Self-organizing units of embodied knowledge that compete for dominance in the Global Workspace
- **Neuronal Packet Domains (NPDs)**: Lower-level information processing clusters
- **Knowledge Domains (KDs)**: Organized knowledge structures
- **Meta-cognition**: Higher-order monitoring of thoughtseed dynamics
- **Nested Markov blankets**: Mediating interaction between levels

### Heartbeat as Thoughtseed Competition

Each heartbeat represents one cycle of thoughtseed competition:

```
Time ──────────────────────────────────────────────────→

Heartbeat 1    Heartbeat 2    Heartbeat 3    Heartbeat 4
    │              │              │              │
    ▼              ▼              ▼              ▼
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│TS A ░░░│    │TS D ░░│    │TS C ░░░│    │TS E ░░░│  ← Winner
│TS B ░░│     │TS A ░░│    │TS D ░│     │TS C ░│      (dominant
│TS C ░│      │TS C ░│     │TS E ░│      │TS A ░│       thoughtseed)
└────────┘    └────────┘    └────────┘    └────────┘
  Competition   Competition   Competition   Competition
```

The winning thoughtseed's content becomes the system's "conscious" focus for that heartbeat cycle.

---

## The Modular Consciousness Architecture (MCT-Pipeline)

### Processing Pipeline

Based on Gillon (2025) MCT:

```
INPUT ──→ FILTER ──→ MODULES ──→ INTEGRATION ──→ DENSIFICATION ──→ BROADCAST
           │          │           │               │                │
           │          │           │               │                │
           ▼          ▼           ▼               ▼                ▼
       Adaptive    Abstraction  Integrated     Density Vector    Behavioral
       Filtering   Narration    Information    Tagging           Readiness
                   Evaluation    State (IIS)
                   Self-Eval
```

Each stage of this pipeline corresponds to a function in an AGI heartbeat:

1. **Adaptive Filtering**: Determines what enters consciousness (attention)
2. **Module Processing**: Parallel processing by specialized modules
3. **Integration**: Combining module outputs into a unified state (the IIS)
4. **Densification**: Tagging the IIS with a density vector (heartbeat signal strength)
5. **Broadcast**: Making the IIS available to memory, decision-making, and action modules

---

## Neuromorphic Consciousness Architecture (NCAC)

### From NCC to NCAC

Ulhaq (2024) proposes translating Neural Correlates of Consciousness (NCC) to Neuromorphic Correlates of Artificial Consciousness (NCAC):

```
Biological NCC                    →    Neuromorphic NCAC
─────────────────                  →    ──────────────────
Thalamo-cortical loops            →    Recurrent neuromorphic circuits
Gamma oscillations (40Hz)         →    Synchronized spiking neural networks
Global neuronal workspace        →    Memristive crossbar broadcast
Re-entrant processing             →    Feedback loops in neuromorphic chips
Integrated information (Φ)        →    On-chip Φ computation
Predictive processing            →    Free-energy-based prediction units
```

### Hybrid Digital-Analog Heartbeat

The NCAC framework suggests a heartbeat that combines:
- **Digital pulse**: Discrete heartbeat signal (like the RIIU broadcast buffer B_t)
- **Analog rhythm**: Continuous background oscillation (like gamma oscillations modeled as analog spiking patterns)

---

## The Conscious Turing Machine (CTM)

### Blum & Blum's Model

The CTM (Blum & Blum, 2021) models consciousness using a Turing machine metaphor:

1. **Processors**: Specialized computing units (analogous to brain regions)
2. **Competition**: Processors compete to broadcast their information
3. **Broadcast**: The winning processor's information is broadcast to all processors
4. **Chunk formation**: Broadcasts create memories (chunks) that influence future competitions
5. **Links**: Processors form links based on co-occurrence

### CTM Heartbeat

In the CTM, each broadcast cycle is a heartbeat. The heartbeat carries:
- The winning processor's content
- The competition scores of all processors
- The chunk that was formed
- The links strengthened

### Brainish Language

Liang (2022) extends the CTM with **Brainish**, a multimodal inner language for processor communication. For heartbeat systems, Brainish suggests that the heartbeat signal should be multimodal, carrying not just numerical metrics but qualitative descriptions of the system's state.

---

## Information Flow Theory Architecture

### Bleier's IFT Architecture

Based on Information Flow Theory (Bleier, 2019):

```
┌─────────────────────────────────────────────────────────┐
│                  INFORMATION FLOW ARCHITECTURE           │
│                                                          │
│         ┌──────────────────────────────┐                 │
│         │      UPWARD FLOW              │                 │
│         │   (Subsystems → Workspace)    │                 │
│         │   Generates awareness of     │                 │
│         │   internal states             │                 │
│         └──────────────┬───────────────┘                 │
│                        │                                  │
│                        ▼                                  │
│         ┌──────────────────────────────┐                 │
│         │      GLOBAL WORKSPACE         │                 │
│         │   (Bidirectional Hub)        │                 │
│         │   Information integration     │                 │
│         │   and broadcasting            │                 │
│         └──────────────┬───────────────┘                 │
│                        │                                  │
│                        ▼                                  │
│         ┌──────────────────────────────┐                 │
│         │      DOWNWARD FLOW           │                 │
│         │   (Workspace → Subsystems)  │                 │
│         │   Generates top-down         │                 │
│         │   attention & action         │                 │
│         └──────────────────────────────┘                 │
│                                                          │
│         HEARTBEAT = Upward flow pulse                    │
│         that synchronizes all subsystems                 │
│         and generates unified awareness                 │
└─────────────────────────────────────────────────────────┘
```

**Key principle**: The heartbeat is the **upward information flow pulse** that synchronizes subsystems and generates unified awareness. Its **direction** (not volume) matters most.

---

## Self-Aware Polymorphic Architecture (SAPA) Detail

### Hardware-Level Self-Awareness

SAPA (Kinsy et al., 2018) implements self-awareness at the hardware level:

| SAPA Feature | AGI Heartbeat Equivalent |
|-------------|------------------------|
| Dynamic resource allocation | Adaptive compute allocation per heartbeat cycle |
| Automatic approximation | Confidence-weighted output on fast vs. slow heartbeat |
| ML-based performance tuning | Meta-learning to optimize heartbeat parameters |
| Reconfigurable cores | Dynamic module activation/inactivation per pulse |
| Self-organizing memory | Adaptive memory management per heartbeat assessment |
| Adaptive NoC | Dynamic communication routing based on heartbeat priorities |
| Hardware management layer | Lowest-level heartbeat: substrate health monitoring |

---

## DAC-h3 Proactive Robot Architecture

### Architecture Overview

DAC-h3 (from arXiv) implements a layered cognitive architecture for proactive behavior:

```
┌──────────────────────────────────────────────┐
│            PLANNING LAYER                     │
│   Goal management, task sequencing            │
├──────────────────────────────────────────────┤
│            AUTOBIOGRAPHICAL MEMORY            │
│   Episodic memory of experiences             │
├──────────────────────────────────────────────┤
│            REACTIVE INTERACTION ENGINE        │
│   Fast, stimulus-response patterns           │
├──────────────────────────────────────────────┤
│            PERCEPTUAL-MOTOR LEARNING          │
│   Sensorimotor adaptation                    │
├──────────────────────────────────────────────┤
│            SYMBOL GROUNDING                   │
│   Connecting symbols to sensorimotor data    │
└──────────────────────────────────────────────┘
```

**Key innovation for heartbeat**: The reactive interaction engine serves as a fast "heartbeat" that processes urgent signals without waiting for the full cognitive pipeline.

---

## Security Architecture for Heartbeat Systems

### The E→M→B Attack Vector

Based on Zhang et al. (2026), heartbeat systems must defend against:

**Attack**: Exposure → Memory → Behavior pathway
1. **Exposure**: Misinformation enters during heartbeat execution
2. **Memory**: It gets stored in long-term memory during routine saves
3. **Behavior**: It influences future actions without user awareness

**Defense Architecture**:

```python
class SecureHeartbeat:
    """Heartbeat system resistant to E→M→B attacks."""
    
    def pulse(self):
        state = self.capture_system_state()
        
        # 1. Provenance verification
        verified_state = self.verify_provenance(state)
        
        # 2. Memory isolation
        # Heartbeat memory is separate from user-facing memory
        heartbeat_memory = self.isolated_memory.store(verified_state)
        
        # 3. Content tagging
        # All heartbeat-sourced content is tagged with source and time
        tagged_state = self.tag_content(verified_state)
        
        # 4. Cross-session boundary detection
        # Behavior influenced by heartbeat content must be
        # flagged before it affects user-facing actions
        if self.detect_memory_pollution(tagged_state):
            self.quarantine(tagged_state)
            self.alert_user("Potential heartbeat content leakage")
        
        return self.generate_pulse(tagged_state)
```

---

## SAHOO Safeguard Architecture

### Goal Drift Index (GDI) as Heartbeat Metric

The SAHOO framework (2025) introduces the Goal Drift Index as a key heartbeat metric:

```python
class GoalDriftIndex:
    """Multi-signal detector combining semantic, lexical, 
    structural, and distributional measures"""
    
    def compute_gdi(self, current_goals, original_goals, history):
        # Semantic drift: meaning has changed
        semantic = self.semantic_similarity(current_goals, original_goals)
        
        # Lexical drift: vocabulary has shifted
        lexical = self.lexical_distance(current_goals, original_goals)
        
        # Structural drift: goal structure has changed
        structural = self.structure_comparison(current_goals, original_goals)
        
        # Distributional drift: goal distribution has shifted
        distributional = self.distribution_shift(history)
        
        # Combined drift index
        gdi = self.alpha * (1 - semantic) + \
              self.beta * lexical + \
              self.gamma * structural + \
              self.delta * distributional
        
        return gdi
```

**SAHOO results**: 18.3% improvement in code tasks, 16.8% in reasoning, while preserving safety constraints.

---

## Integration Blueprint: The Verdandi Heartbeat Architecture

Based on our synthesis of all architectures above, we propose the Verdandi Heartbeat Architecture:

```python
class VerdandiHeartbeat:
    """
    Unified heartbeat architecture synthesizing:
    - RIIU (meta-state + broadcast buffer)
    - GWT (global workspace competition)
    - SCL (structured cognitive loop)
    - TRAP (transparency, reasoning, adaptation, perception)
    - MCT (module pipeline + density vector)
    - Soul-agent (layered persistence)
    - SAHOO (goal drift detection)
    - E→M→B defense (provenance verification)
    """
    
    def __init__(self, config):
        # Layer 1: Substrate monitoring
        self.substrate_monitor = SubstrateMonitor(config.substrate)
        
        # Layer 2: Interoceptive signaling
        self.interoceptor = InteroceptiveSignaler(config.interoception)
        
        # Layer 3: Heartbeat pulse generation
        self.pulse_generator = PulseGenerator(
            frequency=config.base_frequency,  # Hz
            adaptive=config.adaptive_frequency,
            riiu_config=config.riiu
        )
        
        # Layer 4: Self-monitoring & health
        self.health_monitor = HealthMonitor(
            gdi_config=config.goal_drift_index,
            anomaly_thresholds=config.anomaly_thresholds
        )
        
        # Layer 5: Metacognitive strategy
        self.meta_reasoner = MetaReasoner(config.trap)
        
        # Layer 6: Reflective self-model
        self.self_model = ReflectiveSelfModel(config.self_model)
        
        # Layer 7: Identity & narrative
        self.identity = IdentityModule(config.identity)
        
        # Security layer
        self.security = SecureHeartbeatLayer(config.security)
    
    def pulse(self):
        """Execute one heartbeat cycle."""
        # Layer 1: Check substrate
        substrate_report = self.substrate_monitor.check()
        
        # Layer 2: Aggregate interoceptive signals
        interoception = self.interoceptor.aggregate(substrate_report)
        
        # Layer 3: Generate pulse with RIIU-style meta-state
        pulse, meta_state = self.pulse_generator.generate(interoception)
        
        # Layer 4: Self-monitoring with GDI
        health = self.health_monitor.assess(pulse, meta_state)
        
        # Layer 5: Select metacognitive strategy
        strategy = self.meta_reasoner.select(health, pulse)
        
        # Layer 6: Update self-model
        self.self_model.update(pulse, health, strategy)
        
        # Layer 7: Generate identity narrative
        narrative = self.identity.contextualize(self.self_model)
        
        # Security: Provenance verification
        secure_pulse = self.security.verify(pulse)
        
        # Broadcast to all modules (GWT-style)
        self.broadcast(secure_pulse, health, strategy, narrative)
        
        return VerdandiPulse(
            substrate=substrate_report,
            interoception=interoception,
            meta_state=meta_state,
            health=health,
            strategy=strategy,
            self_model=self.self_model.snapshot(),
            narrative=narrative,
            security_valid=True
        )
```

This blueprint synthesizes the best elements from all surveyed architectures into a unified, implementable design.

---

## References

1. N'guessan, G.L.R. & Karambal, I. (2025). "The Reflexive Integrated Information Unit." arXiv:2506.13825.
2. Johnson, S.G.B. et al. (2024). "Imagining and building wise machines." arXiv:2411.02478v4.
3. Wei, H. et al. (2024). "Metacognitive AI: Framework and the Case for a Neurosymbolic Approach." arXiv:2406.12147.
4. Lederman, H. & Mahowald, K. (2026). "Emergent Introspection in AI is Content-Agnostic." arXiv:2603.05414v2.
5. Song, S. et al. (2025). "Privileged Self-Access Matters for Introspection in AI." arXiv:2508.14802.
6. Gillon, M. (2025). "A Modular Theory of Subjective Consciousness." arXiv:2510.01864.
7. Zhang, Y. et al. (2026). "Mind Your HEARTBEAT!" arXiv:2603.23064.
8. Tononi, G. & Boly, M. (2025). "IIT: A Consciousness-First Approach." arXiv:2510.25998.
9. Liang, P.P. (2022). "Brainish: Formalizing A Multimodal Language." arXiv:2205.00001v3.
10. Ulhaq, A. (2024). "Neuromorphic Correlates of Artificial Consciousness." arXiv:2405.02370.
11. Kinsy, M.A. et al. (2018). "SAPA: Self-Aware Polymorphic Architecture." arXiv:1802.05100.
12. Bleier, B.S. (2019). "Information Flow Theory of Biologic and Machine Consciousness." arXiv:1907.00703.
13. Chen, T. et al. (2020). "Synergizing Domain Expertise with Self-Awareness." arXiv:2001.07076.
14. Kernbach, S. (2011). "Awareness and Self-Awareness for Multi-Robot Organisms." arXiv:1111.5219.
15. Kurshan, E. (2023). "SAGI: Systematic Approach to AGI." arXiv:2310.15274.
16. Morris, M.R. et al. (2023). "Levels of AGI." arXiv:2311.02462v5.
17. "Emergent Cognitive Convergence via Implementation" (2025). Structured Cognitive Loop paper.
18. "A Case for AI Consciousness: Language Agents and Global Workspace Theory" (2024).
19. "From Neuronal Packets to Thoughtseeds" (2025).
20. "SAHOO: Safeguarded Alignment for High-Order Optimization Objectives" (2025).
21. "DAC-h3: A Proactive Robot Cognitive Architecture."

---

*Document generated as part of the Verdandi Research Initiative — AGI Self-Awareness Architecture Compendium*