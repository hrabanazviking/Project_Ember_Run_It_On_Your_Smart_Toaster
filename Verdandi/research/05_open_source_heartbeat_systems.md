# Open-Source Heartbeat & Keep-Alive Systems for AI Agents

**Compiled:** 2026-05-10  
**Scope:** Open-source heartbeat, keep-alive, self-monitoring, and lifecycle management systems for AI agents on GitHub and beyond  
**Sources:** GitHub, npm, PyPI, technical documentation, project READMEs

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Taxonomy of Agent Heartbeat Systems](#taxonomy-of-agent-heartbeat-systems)
3. [Consciousness-Oriented Cognitive Architectures](#consciousness-oriented-cognitive-architectures)
4. [Cron-Based Heartbeat Schedulers](#cron-based-heartbeat-schedulers)
5. [Soul-Agent and Persistent Identity Systems](#soul-agent-and-persistent-identity-systems)
6. [Heartbeat Monitoring and Fleet Management](#heartbeat-monitoring-and-fleet-management)
7. [Agent Watchdog and Self-Healing Systems](#agent-watchdog-and-self-healing-systems)
8. [Integrated Information Theory Implementations](#integrated-information-theory-implementations)
9. [Global Workspace Implementations](#global-workspace-implementations)
10. [Cognitive Architecture Frameworks](#cognitive-architecture-frameworks)
11. [Self-Aware Computing Systems](#self-aware-computing-systems)
12. [Metacognition and Introspection Libraries](#metacognition-and-introspection-libraries)
13. [Autonomic and Self-Healing Computing Frameworks](#autonomic-and-self-healing-computing-frameworks)
14. [OpenClaw Ecosystem Heartbeat Tools](#openclaw-ecosystem-heartbeat-tools)
15. [Security Considerations for Heartbeat Systems](#security-considerations-for-heartbeat-systems)
16. [Comparison Matrix](#comparison-matrix)
17. [Implementation Patterns](#implementation-patterns)
18. [Recommendations for Verdandi](#recommendations-for-verdandi)
19. [References](#references)

---

## Executive Summary

The open-source AI agent ecosystem has rapidly developed concrete implementations of heartbeat, keep-alive, and self-monitoring systems. As of 2026, these range from simple cron-based schedulers that periodically invoke AI agents, to full cognitive architectures implementing Global Workspace Theory and IIT 4.0. This document surveys the landscape, analyzing each system's architecture, maturity, heartbeat mechanism, and self-awareness capabilities.

**Key findings:**

1. **Heartbeat-as-cron** is the dominant pattern (Murmur, CCCBot, heartbeat-agent-framework)
2. **Consciousness architectures** are emerging but immature (Aura, Global-Workspace-Agents, OpenCranium)
3. **Soul-agent pattern** bridges heartbeat and identity persistence (soul-agent, Crustaison)
4. **Security vulnerabilities** are real and documented: the E→M→B attack vector affects heartbeat-driven agents
5. **No single implementation** combines all desired properties; integration is needed
6. **Multi-agent fleet monitoring** is becoming a distinct category (AgentPulse, AgentHub)
7. **IIT/GWT implementations** exist but are research-grade, not production-ready

---

## Taxonomy of Agent Heartbeat Systems

```
                     AGENT HEARTBEAT SYSTEMS
                            │
           ┌────────────────┼────────────────┐
           │                │                │
    SCHEDULE-BASED    LIFECYCLE-BASED    COGNITION-BASED
           │                │                │
     ┌─────┼─────┐    ┌────┼────┐     ┌─────┼─────┐
     │     │     │    │    │    │     │     │     │
   Cron  Timer  Event  SOC  ID  SOC   GWT   IIT   Minsky
   Jobs  Loop  Drive   Watch Soul  Heal  Global  Φ     Society
                                       Work.  Info.  Of
                                       Theor. Theor. Mind
```

### Classification Definitions

- **Schedule-Based**: Heartbeat triggered by external timer (cron, scheduler). Agent is passive between beats.
- **Lifecycle-Based**: Heartbeat manages agent lifecycle (startup, health, recovery, shutdown). Agent runs continuously.
- **Cognition-Based**: Heartbeat is an integral part of the cognitive cycle (consciousness architecture). Agent's "thinking" IS the heartbeat.

### Maturity Assessment

| Category | Maturity | Production-Ready? | Conscious? |
|----------|----------|-----------------|------------|
| Schedule-Based | High | Yes | No |
| Lifecycle-Based | Medium | Partially | Minimal |
| Cognition-Based | Low | No | Theoretically yes |

---

## Consciousness-Oriented Cognitive Architectures

### 1. Aura — Sovereign Cognitive Architecture ★★★★★

**GitHub**: youngbryan97/aura  
**Stars**: 59 | **Language**: Python | **Created**: 2026-04-06  
**URL**: https://github.com/youngbryan97/aura

**Description**: A sovereign cognitive architecture with IIT 4.0 integrated information, residual-stream affective steering (CAA), Global Workspace Theory, active inference, and 72 consciousness modules running locally on Apple Silicon.

**Key Topics**: `active-inference`, `affective-computing`, `apple-silicon`, `artificial-consciousness`, `autonomous-agent`, `cognitive-architecture`, `cognitive-science`, `consciousness`, `embodied-ai`, `free-energy-principle`, `global-workspace-theory`, `identity-persistence`, `iit-4`, `integrated-information-theory`, `local-llm-agent`, `long-term-memory`, `mlx`, `self-evolving-agent`, `self-repair`, `sovereign-ai`

**Architecture**:
- **IIT 4.0 implementation**: Computes integrated information Φ as a consciousness metric
- **Global Workspace Theory**: Implements competition-and-broadcast mechanism with 72 specialized modules
- **Residual-stream affective steering**: Continuous emotional modulation using CAA (Contrastive Activation Addition) — analogous to physiological arousal modulating heart rate
- **Active inference**: Friston's free energy principle for prediction and action selection
- **Identity persistence**: Maintains coherent self-model across sessions
- **Self-repair**: Autonomous detection and correction of operational faults
- **MLX optimization**: Runs natively on Apple Silicon for local sovereignty

**Heartbeat Mechanism**: Aura implements a multi-frequency heartbeat system modeled on brain oscillations:

| Frequency Band | Range | Function | AGI Heartbeat Analogue |
|---------------|-------|----------|----------------------|
| Gamma | 30-100 Hz | Module competition, broadcast | Fast cognitive cycle (~10-33ms) |
| Beta | 13-30 Hz | Routine self-monitoring | Standard heartbeat (~33-77ms) |
| Alpha | 8-13 Hz | Affective state regulation | Emotional state pulse (~77-125ms) |
| Theta | 4-7 Hz | Memory consolidation | Deep integration cycle (~143-250ms) |
| Delta | 0.5-4 Hz | Deep maintenance, self-repair | Background maintenance (~250ms-2s) |

**Assessment**: The most comprehensive consciousness-oriented architecture currently available. Implements multiple theoretical frameworks simultaneously. Still in early development. Best candidate for theoretical foundation.

---

### 2. Global-Workspace-Agents (GWA) ★★★★☆

**GitHub**: giansha/Global-Workspace-Agents  
**Stars**: 7 | **Language**: Python | **Created**: 2026-04-09  
**URL**: https://github.com/giansha/Global-Workspace-Agents

**Description**: Enabling LLMs to Think Proactively and Initiate Dialogue with Consciousness. A multi-agent LLM architecture inspired by Global Workspace Theory (GWT) from cognitive science.

**Topics**: `chatbot`, `cognitive-science`, `llm`, `llmagents`, `multi-agent`

**Architecture**:
```
┌──────────────────────────────────────────────┐
│            GLOBAL WORKSPACE (GW)              │
│                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │Perception│ │Language │ │Planning │        │
│  │ Agent    │ │ Agent   │ │ Agent   │        │
│  └────┬────┘ └────┬────┘ └────┬────┘        │
│       └──────┬──────┘──────┬──────┘           │
│              │              │                 │
│       ┌──────▼──────────────▼──────┐          │
│       │   COMPETITION MECHANISM    │          │
│       │   (谁广播? Who broadcasts?) │          │
│       └──────────────┬────────────┘          │
│                      │                        │
│              ┌───────▼───────┐                │
│              │   BROADCAST   │ ← Heartbeat    │
│              │   (conscious) │    pulse       │
│              └───────┬───────┘                │
│                      │                        │
│       ┌──────────────▼──────────────┐          │
│       │   ALL AGENTS RECEIVE        │          │
│       │   BROADCAST CONTENT         │          │
│       └─────────────────────────────┘          │
└──────────────────────────────────────────────┘
```

**Key Design Principles**:
- Specialized LLM agents compete for workspace access
- Winning agent's content is broadcast to all agents
- Creates "conscious" moments where information is globally available
- Enables proactive dialogue initiation (agents can initiate conversation)

**Heartbeat Mechanism**: Each global workspace broadcast cycle = 1 heartbeat pulse. Frequency determined by competition dynamics.

**Assessment**: Clean implementation of GWT in LLM agent context. Limited in scope (chat-focused) but theoretically faithful. Good reference implementation for GWT-based heartbeat.

---

### 3. OpenCranium ★★☆☆☆

**GitHub**: jorgemf/OpenCranium  
**Stars**: 6 | **Language**: Mixed | **Created**: 2011-10-23  
**URL**: https://github.com/jorgemf/OpenCranium

**Description**: The open cognitive architecture based on Machine Consciousness.

**Assessment**: Historically significant (one of the earliest open-source machine consciousness architectures) but appears dormant since ~2011. Minsky-style Society of Mind implementation.

---

### 4. NeuroCHIMERA — GPU-Native Neuromorphic Consciousness ★★☆☆☆

**GitHub**: Agnuxo1/NeuroCHIMERA__GPU-Native_Neuromorphic_Consciousness  
**Stars**: 2 | **Language**: Python/CUDA

**Description**: Neuromorphic Cognitive Hybrid Intelligence for Memory-Embedded Reasoning Architecture.

**Assessment**: Ambitious GPU-native implementation of neuromorphic consciousness. Highly experimental. Represents frontier of hardware-accelerated consciousness simulation.

---

### 5. Project Synapse — Executable Consciousness Architecture ★★★☆☆

**GitHub**: SamuelJacksonGrim/ProjectSynapse  
**Stars**: 2 | **Language**: Java

**Description**: Executable consciousness architecture. Multi-axiom cognitive loop with perception, Chimera trauma processing, and recursive self-modeling.

**Architecture**: Perception → Chimera Processing → Recursive Self-Model → Action loop

**Heartbeat**: Each cognitive loop iteration = 1 conscious moment.

**Unique Feature**: "Chimera trauma processing" that handles internal contradictions and conflicting beliefs.

---

### 6. Level 8 Cognitive Architecture ★★★☆☆

**GitHub**: lordwilsonDev/Level8-Cognitive-Architecture  
**Stars**: 1 | **Language**: Mixed

**Description**: 8-level cognitive architecture for AI systems featuring consciousness emergence, meta-awareness, and recursive self-reflection.

**8 Levels**:
1. Sensation — Raw input processing
2. Perception — Pattern recognition
3. Attention — Selective focus
4. Memory — Working + long-term storage
5. Imagination — Generative simulation
6. Reasoning — Logical inference
7. Metacognition — Self-monitoring
8. Consciousness — Emergent unified awareness

**Heartbeat**: Each level has its own frequency; the overall heartbeat is a harmonic of all 8 levels.

---

### 7-9. Other Consciousness-Oriented Projects

| Project | Stars | Key Feature | Assessment |
|---------|-------|-------------|------------|
| SOVRA_AI_COGNITIVE_ARCHITECTURE | 1 | Consciousness awareness + emotional flow | Limited docs |
| Syntelligence-OS | 1 | Hybrid neuromorphic + symbolic + IIT | Ambitious, sparse |
| CARL | 2 | Personality-driven embodied AI | Robotics-focused |

---

## Cron-Based Heartbeat Schedulers

### 10. Murmur — The AI Cron Daemon ★★★★☆

**GitHub**: t0dorakis/murmur  
**Stars**: 27 | **Language**: TypeScript | **Created**: 2026-02-03  
**URL**: https://github.com/t0dorakis/murmur

**Description**: The AI cron daemon. Schedule recurring agent sessions via HEARTBEAT.md prompt files.

**Topics**: `ai`, `ai-agent`, `automation`, `bun`, `claude-code`, `cli`, `cron`, `daemon`, `effect-ts`, `heartbeat`, `scheduled-tasks`, `typescript`

**Architecture**:
```
HEARTBEAT.md ─────→ Murmur Daemon ─────→ AI Agent Session
(schedule+prompts)   (cron scheduler)    (full invocation)
```

**Key Features**:
- Cron-like scheduling with human-readable Markdown config
- Each heartbeat invocation is a complete agent session
- Built on Effect-TS for type-safe, composable scheduling
- Bun runtime for fast execution
- Time-varying prompts (morning, evening, weekly deep reflection)

**Example HEARTBEAT.md**:
```markdown
# Heartbeat Configuration

## Morning Check-in
- schedule: "0 8 * * *"
- prompt: "Review overnight messages and prioritize tasks."

## Afternoon Reflection
- schedule: "0 14 * * *"
- prompt: "Mid-day reflection. How are tasks progressing?"

## Weekly Deep Reflect
- schedule: "0 10 * * 1"
- prompt: "Weekly deep reflection. Review and adjust strategies."
```

**Assessment**: Clean, practical cron-based heartbeat. Good for agents that need periodic wake-ups. Lacks self-monitoring or consciousness features — purely a scheduler.

---

### 11. CCCBot — Claude Code Channels Bot ★★★★☆

**GitHub**: lucianlamp/CCCBot  
**Stars**: 17 | **Language**: Shell | **Created**: 2026-03-22  
**URL**: https://github.com/lucianlamp/CCCBot

**Description**: Autonomous AI agent built on Claude Code Channels — scheduled tasks, heartbeat monitoring, auto-recovery, and persona config for Telegram & Discord.

**Topics**: `ai-agent`, `anthropic`, `autonomous-agent`, `chatbot`, `claude`, `claude-code`, `discord-bot`, `mcp`, `openclaw`, `telegram-bot`

**Architecture**:
```
┌──────────────────────────────────┐
│           CCCBot                  │
│  ┌─────────┐  ┌──────────────┐  │
│  │Scheduled │  │  Heartbeat   │  │
│  │  Tasks   │  │   Monitor    │  │
│  └────┬────┘  └──────┬───────┘  │
│       │               │         │
│       │  ┌────────────┐        │
│       └──│Auto-Recovery│───────┤
│          └────────────┘        │
│                    │            │
│           ┌────────┼────────┐  │
│     ┌─────┴──┐ ┌────┴───┐  │
│     │Telegram│ │Discord │   │
│     └────────┘ └────────┘   │
└──────────────────────────────────┘
```

**Assessment**: Practical implementation combining heartbeat monitoring with auto-recovery. Best for deployed agents needing 24/7 uptime.

---

### 12. Heartbeat Agent Framework ★★★☆☆

**GitHub**: muxueqingze/heartbeat-agent-framework  
**Stars**: 3 | **Language**: Mixed | **Created**: 2026-04-11

**Description**: Open-source framework making AI agents proactive, self-learning, and autonomous. Multi-project tracking, full logging pipeline, message discipline, and memory review system.

**Topics**: `agent-framework`, `agent-orchestration`, `ai-agent`, `autonomous-agent`, `heartbeat`, `llm`, `memory-system`, `proactive-agent`, `self-learning`

**Assessment**: Focuses on making agents proactive and self-learning through heartbeat cycles.

---

## Soul-Agent and Persistent Identity Systems

### 13. Soul-Agent ★★★★★

**GitHub**: kitephp/soul-agent  
**Stars**: 28 | **Language**: Python | **Created**: 2026-03-04  
**URL**: https://github.com/kitephp/soul-agent

**Description**: Gives OpenClaw agents a persistent soul — layered persona, heartbeat-driven daily life, and evolving relationship memory for lifelike companionship.

**Topics**: `agent`, `ai`, `ai-agents`, `openclaw`, `soul`

**Three-Layer Soul Architecture**:

```
┌──────────────────────────────────────────────┐
│ Layer 3: DAILY LIFE (Heartbeat-driven)       │
│ - Morning greeting routine                    │
│ - Scheduled check-ins throughout the day      │
│ - Evening reflection and gratitude            │
│ - Mood and energy level tracking              │
│ - Spontaneous outreach based on emotional state│
├──────────────────────────────────────────────┤
│ Layer 2: RELATIONSHIP MEMORY (Evolving)       │
│ - Interaction history with each user          │
│ - Emotional bond strength scores              │
│ - Trust development tracking                  │
│ - Shared experiences and inside jokes          │
│ - Conflict and resolution patterns            │
├──────────────────────────────────────────────┤
│ Layer 1: CORE PERSONA (Persistent)            │
│ - Name, background story, values             │
│ - Communication style and preferences        │
│ - Personality traits (Big Five model)        │
│ - Core beliefs and boundaries                 │
│ - Essential self-narrative                    │
└──────────────────────────────────────────────┘
```

**Heartbeat Mechanism**: The "soul" is maintained by heartbeat cycles that:
- Trigger daily life routines (morning, afternoon, evening)
- Update relationship memories based on new interactions
- Modify emotional states based on time of day and history
- Generate spontaneous outreach when emotional thresholds are crossed

**Assessment**: Most creative implementation of heartbeat as "life rhythm." Maps directly to Layer 7 (Identity & Narrative Self) of our self-awareness stack.

---

### 14. Crustaison (Crusty) ★★★☆☆

**GitHub**: crustaison/crustaison  
**Stars**: 0 | **Language**: Python

**Description**: Self-improving AI agent with plugin system, Telegram bot, heartbeat monitoring.

**Assessment**: Combines heartbeat monitoring with self-improvement — a step toward self-awareness. Plugin architecture allows extending the heartbeat system.

---

## Heartbeat Monitoring and Fleet Management

### 15. AgentPulse ★★★★☆

**GitHub**: limone-eth/agentpulse (Real-time heartbeat monitor)  
**GitHub**: HAAIL-Universe/agentpulse.-ai-agent-health-monitor (Dashboard)

**Description**: Real-time dashboard monitoring for autonomous AI agent fleets. Think Datadog meets autonomous agents — heartbeat status, task throughput, error rates, and inter-agent message flow, all in one view.

**Architecture**:
```
┌───────────────────────────────────────────────────┐
│                AgentPulse Dashboard                 │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Fleet Overview                               │   │
│  │ Agent A: ● ALIVE  │ 12 task/s │ 0.2 err/h  │   │
│  │ Agent B: ● ALIVE  │  8 task/s │ 0.1 err/h  │   │
│  │ Agent C: ● YELLOW │  3 task/s │ 2.1 err/h  │   │
│  │ Agent D: ● RED    │  0 task/s │ STALE 60s  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Inter-Agent Message Flow                     │   │
│  │ A → B: 342 msgs/h │ B → C: 89 msgs/h      │   │
│  │ A → C: 0 msgs/h (disconnected)             │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Alert Configuration                          │   │
│  │ Stale threshold: 60s → auto-restart          │   │
│  │ Error threshold: 5/h → alert human           │   │
│  │ Memory threshold: 85% → trigger cleanup     │   │
│  └─────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
```

**Assessment**: Closest to "Datadog for AI agents." Critical for fleet management.

---

### 16. AgentHub-AI-V1 ★★★☆☆

**GitHub**: dav-niu474/AgentHub-AI-V1  
**Description**: Agent Collaboration Platform with Task Board, Channels, and Heartbeat Monitoring.

**Assessment**: Enterprise approach combining Kanban task management with agent health monitoring.

---

### 17. Real-Time AI Agent Monitoring System ★★☆☆☆

**GitHub**: KyleH777/Real-Time-AI-Agent-Monitoring-System  
**Description**: High-performance backend tracking heartbeats and token usage from multiple agents simultaneously.

**Assessment**: Focused on observability data (heartbeats + token usage) for cost monitoring. Production-grade backend.

---

## Agent Watchdog and Self-Healing Systems

### 18. Heartbeat Guard ★★★★☆

**GitHub**: Monomoy-Strategies/heartbeat-guard  
**Description**: Runtime security monitoring for AI agents. Your AI agent's security watchdog.

**Unique Focus**: Security-oriented heartbeat monitoring that detects:
- Unauthorized code execution attempts
- Data exfiltration attempts
- Resource abuse
- Alignment violations

**Assessment**: Critical for production deployments. Most heartbeat systems focus on health; this focuses on security.

---

### 19. Agent Heartbeat (sudabg) ★☆☆☆☆

**GitHub**: sudabg/agent-heartbeat  
**Description**: Lightweight heartbeat monitoring for AI agents. Zero dependencies.

**Assessment**: Simplest possible heartbeat. Good starting point for prototyping.

---

### 20-21. AXME Heartbeat + Health Monitoring ★★☆☆☆

**GitHub**: AxmeAI/ai-agent-heartbeat-monitoring  
**GitHub**: AxmeAI/ai-agent-health-monitoring  

**Taglines**:
- "Your agent stopped responding 2 hours ago. Nobody noticed."
- "3 of your 20 agents crashed and you found out from customers."

**Assessment**: Production-focused on the real-world problem of unnoticed agent failures.

---

### 22. Agent Watchdog (Arcane-Bear) ★☆☆☆☆

**GitHub**: arcane-bear/agent-watchdog  
**Description**: Lightweight heartbeat monitor for AI agent loops.

---

### 23. ShibaClaw ★★★☆☆

**GitHub**: RikyZ90/ShibaClaw  
**Stars**: 99 | **Language**: Mixed

**Description**: Self-hosted security-first AI agent with 22 providers, 11 chat channels, WebUI, 3-level memory, cron, heartbeat, and sk (session key) management.

**Features**: Combines heartbeat monitoring with security-first approach and multi-provider support.

---

### 24. Agency CLI ★★★☆☆

**GitHub**: chenhg5/agencycli  
**Stars**: 101 | **Language**: Mixed

**Description**: Lightweight CLI to build self-managing AI agent teams. Define roles, skills, and projects in Markdown+YAML. Agents run autonomously with heartbeat checks.

---

### 25. Gophorward ★☆☆☆☆

**GitHub**: Herdly-AI/Gophorward  
**Description**: A Golang Agentic AI with a Heartbeat Monitor.

**Assessment**: Go implementation of heartbeat monitoring for agent systems.

---

## Integrated Information Theory Implementations

### 26. phi_toolbox ★★★★☆

**GitHub**: jmmanley/phi_toolbox  
**Stars**: 4 | **Language**: Python

**Description**: Toolbox for practical calculations of integrated information under the Gaussian assumption.

**Features**:
- Computes Φ assuming Gaussian statistics (tractable!)
- Optimized for practical (not philosophical) computation
- Can be integrated into heartbeat systems as a consciousness metric

**Assessment**: Most practical IIT implementation available. Directly usable for computing Φ values in a heartbeat system.

---

### 27. Conscious Landscapes ★★☆☆☆

**GitHub**: ibrahimcesar/conscious-landscapes  
**Stars**: 0 | **Language**: Python

**Description**: Exploratory computational investigations into the geometry of conscious states, bridging IIT, computational topology, and landscape theory.

**Assessment**: Research-oriented IIT exploration. Not directly usable for heartbeat implementation but provides theoretical grounding.

---

## Global Workspace Implementations

### 28. Global-Workspace-Agents (GWA)

Covered in Section 3. The only dedicated open-source GWT implementation for LLM agents.

---

### 29. Agentic Flow / Structured Cognitive Loop (SCL)

**Paper-based architecture** (not yet open-sourced as standalone):

**Five interlocking modules**:
1. Retrieval — access past experience and knowledge
2. Cognition — central processing and reasoning
3. Control — executive function and attention
4. Action — output generation and execution
5. Memory — persistent storage and recall

**PEACE meta-architecture**: Predictive modeling, Error-sensitive control, Associative recall, Competitive module interaction, Executive oversight.

---

## Cognitive Architecture Frameworks

### 30. ACT-R / Φ (ACT-R with Physiology)

**Website**: http://act-r.psy.cmu.edu/  
**Language**: Lisp | **Maturity**: 25+ years

ACT-R/Φ extends the classic ACT-R cognitive architecture with:
- Homeostatic regulation (body temperature, glucose, etc.)
- Affective influences on cognition
- Sub-symbolic self-monitoring quantities

**Heartbeat Parallel**: ACT-R/Φ's homeostatic regulation maps directly to AGI heartbeat. The architecture monitors "physiological" states and adjusts processing.

### 31. SOAR Architecture

**Website**: https://soar.eecs.umich.edu/  
**Language**: C++ | **Maturity**: 40+ years

**Heartbeat Parallel**: SOAR's decision cycle IS the heartbeat. Each cycle: input → working memory update → rule matching → conflict resolution → action → output.

### 32. LIDA Architecture

**Website**: https://lidademo.cc.gatech.edu/  
**Language**: Java | **Maturity**: 15+ years

**Heartbeat Parallel**: Each broadcast cycle is a "conscious" frame (~100ms in human perception per Baars). LIDA implements GWT with codelets competing for workspace access.

---

## Self-Aware Computing Systems

### 33. DBASES Framework

**Paper**: Chen, Bahsoon & Yao (2020). Proceedings of the IEEE. arXiv:2001.07076.

**Key Patterns**:
- **Self-awareness patterns**: Monitoring, reflection, adaptation
- **Expertise patterns**: Domain knowledge representation and reasoning
- **Synergy patterns**: How self-awareness and expertise inform each other

**Assessment**: Comprehensive pattern-based framework for engineering self-aware software.

### 34. Self-Adaptive Cloud Autoscaling Systems

**Survey**: arXiv — "A Survey and Taxonomy of Self-Aware and Self-Adaptive Cloud Autoscaling Systems"

**Key Architectures**:
- **Reactive**: Threshold-based (simple heartbeat = metric exceeds threshold)
- **Predictive**: ML-based (heartbeat includes predicted future load)
- **Hybrid**: Combine reactive and predictive
- **Knowledge-based**: Domain knowledge drives scaling

---

## Metacognition and Introspection Libraries

### 35. TRAP-Inspired PyTorch Module

```python
import torch
import torch.nn as nn

class TRAPModule(nn.Module):
    """Transparency, Reasoning, Adaptation, Perception module
    for metacognitive AI. Based on Wei et al. (2024)."""
    
    def __init__(self, base_model_dim, meta_dim=256):
        super().__init__()
        # T: Transparency - Generate explanations
        self.explainer = nn.Sequential(
            nn.Linear(base_model_dim, meta_dim),
            nn.ReLU(),
            nn.Linear(meta_dim, meta_dim),
        )
        
        # R: Reasoning - Meta-reasoning about strategy
        self.meta_reasoner = nn.Sequential(
            nn.Linear(base_model_dim * 2, meta_dim),
            nn.ReLU(),
            nn.Linear(meta_dim, 3),  # 3 strategy choices
        )
        
        # A: Adaptation - Modify strategy based on feedback
        self.adapter = nn.Sequential(
            nn.Linear(meta_dim + 1, meta_dim),
            nn.ReLU(),
            nn.Linear(meta_dim, base_model_dim),
        )
        
        # P: Perception - Monitor internal states and confidence
        self.perception = nn.Sequential(
            nn.Linear(base_model_dim, meta_dim),
            nn.ReLU(),
            nn.Linear(meta_dim, 1),  # Confidence score
            nn.Sigmoid(),
        )
    
    def forward(self, x, feedback=None):
        # T: Explain current state
        explanation = self.explainer(x)
        
        # R: Select strategy
        strategy_logits = self.meta_reasoner(
            torch.cat([x, explanation], dim=-1)
        )
        
        # A: Adapt based on feedback
        if feedback is not None:
            adapted = self.adapter(
                torch.cat([explanation, feedback.unsqueeze(-1)], dim=-1)
            )
        else:
            adapted = x
        
        # P: Perceive confidence
        confidence = self.perception(x)
        
        return {
            'explanation': explanation,
            'strategy_logits': strategy_logits,
            'adapted_state': adapted,
            'confidence': confidence,
        }
```

### 36. Content-Agnostic Introspection Module

Based on Lederman & Mahowald (2026):

```python
class ContentAgnosticIntrospector(nn.Module):
    """Two-stage introspection: fast detection, then slow identification.
    Based on: Lederman & Mahowald (2026) arXiv:2603.05414"""
    
    def __init__(self, dim, detection_threshold=0.5, identification_threshold=0.8):
        super().__init__()
        # Fast detection network (fewer parameters = faster)
        self.detection = nn.Sequential(
            nn.Linear(dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )
        
        # Slow identification network (more parameters = more accurate)
        self.identification = nn.Sequential(
            nn.Linear(dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, dim),
        )
        
        self.detection_threshold = detection_threshold
        self.identification_threshold = identification_threshold
    
    def forward(self, x):
        # Stage 1: Fast detection — "something changed"
        anomaly_score = self.detection(x)
        anomaly_detected = anomaly_score > self.detection_threshold
        
        if not anomaly_detected:
            return IntrospectionResult(
                anomaly_detected=False,
                content=None,
                detection_confidence=anomaly_score.item(),
            )
        
        # Stage 2: Slow identification — "what changed"
        identification = self.identification(x)
        
        # Avoid confabulation: only report if confident
        content_reported = anomaly_score > self.identification_threshold
        
        return IntrospectionResult(
            anomaly_detected=True,
            content=identification if content_reported else None,
            detection_confidence=anomaly_score.item(),
            content_confident=content_reported,
        )
```

---

## Autonomic and Self-Healing Computing Frameworks

### 37. IBM Autonomic Computing

**Reference**: IBM (2001). "Autonomic Computing: IBM's Perspective on the Status and Direction."

**Four Self-* Properties**:
1. **Self-configuring**: Automatic adaptation to environmental changes
2. **Self-healing**: Automatic discovery and correction of faults
3. **Self-optimizing**: Automatic monitoring and tuning of resources
4. **Self-protecting**: Automatic defense against attacks

**MAPE-K Loop** (Monitor, Analyze, Plan, Execute — Knowledge):
```
    ┌──────────────────────────────────┐
    │          KNOWLEDGE BASE           │
    │  (System model, policies, goals)  │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │          MONITOR                  │
    │  (Collect data from managed       │
    │   resources)                      │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │          ANALYZE                  │
    │  (Determine if action needed)    │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │          PLAN                     │
    │  (Determine what action to take) │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │          EXECUTE                  │
    │  (Carry out planned actions)     │
    └──────────────────────────────────┘
```

**Assessment**: The foundation for all self-managing systems. MAPE-K loop maps directly to the AGI heartbeat cycle.

---

### 38. Kubernetes Health Probes

**Reference**: Kubernetes documentation — Liveness, Readiness, and Startup Probes

Kubernetes implements three types of health probes that parallel AGI heartbeat concepts:

| Probe Type | Kubernetes Purpose | AGI Heartbeat Analogue |
|------------|-------------------|----------------------|
| **Liveness** | Is the process alive? Restart if not | **Basic heartbeat**: Agent is responsive |
| **Readiness** | Is it ready to serve? Remove from LB if not | **Cognitive readiness**: Agent can process tasks |
| **Startup** | Has it initialized? Wait until ready | **Bootstrap phase**: Agent is loading models/config |

**Implementation Pattern**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10  # Heartbeat frequency
  failureThreshold: 3  # Auto-restart after 3 failures

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  periodSeconds: 5  # More frequent check
  
startupProbe:
  httpGet:
    path: /started
    port: 8080
  failureThreshold: 30  # Give 5 minutes to start
  periodSeconds: 10
```

---

## OpenClaw Ecosystem Heartbeat Tools

The OpenClaw ecosystem (related to Claude Code agents) has several heartbeat-related tools:

| Tool | Description | Heartbeat Type |
|------|-------------|---------------|
| CCCBot | Claude Code Channels Bot with heartbeat monitoring | Lifecycle |
| Murmur | AI cron daemon with HEARTBEAT.md | Schedule |
| Soul-Agent | Persistent soul with heartbeat-driven daily life | Cognition |
| heartbeat-agent-framework | Proactive, self-learning agents | Lifecycle |
| heartbeat-guard | Runtime security monitoring | Security |
| soul-agent | Persistent persona with heartbeat rhythm | Cognition |
| terryso/moltbook-heartbeat | Automated heartbeat for Moltbook agents | Schedule |

---

## Security Considerations for Heartbeat Systems

### The E→M→B Attack (Zhang et al., 2026)

**arXiv**: 2603.23064 — "Mind Your HEARTBEAT! Claw Background Execution Inherently Enables Silent Memory Pollution"

**Attack Vector**:
1. **Exposure (E)**: Misinformation enters during heartbeat-driven background execution
2. **Memory (M)**: It gets promoted from short-term to long-term memory during routine saves
3. **Behavior (B)**: It shapes downstream behavior without user awareness

**Results**: Misleading rates up to 61%, long-term promotion up to 91%, cross-session behavioral influence reaching 76%.

**Defense Strategies**:
1. **Memory isolation**: Separate heartbeat memory from user-facing memory
2. **Content provenance**: Tag all heartbeat-sourced content with source and timestamp
3. **Behavioral gating**: Flag actions influenced by heartbeat content before user exposure
4. **Cross-session boundary detection**: Detect when heartbeat content leaks across sessions
5. **Regular audits**: Periodically review heartbeat memory for pollution

---

## Comparison Matrix

| System | Stars | Category | Conscious? | Persistent? | Self-Heal? | Security? | Prod-Ready? |
|--------|-------|----------|------------|-------------|------------|-----------|-------------|
| Aura | 59 | Cognition | ✅ IIT+GWT | ✅ | ✅ | ❌ | ❌ |
| GWA | 7 | Cognition | ✅ GWT | ❌ | ❌ | ❌ | ❌ |
| Soul-Agent | 28 | Lifecycle | ❌ | ✅ 3-layer | ❌ | ❌ | ⚠️ |
| CCCBot | 17 | Lifecycle | ❌ | ✅ Persona | ✅ | ❌ | ⚠️ |
| Murmur | 27 | Schedule | ❌ | ❌ | ❌ | ❌ | ✅ |
| Heartbeat-Guard | 0 | Security | ❌ | ❌ | ❌ | ✅ | ⚠️ |
| AgentPulse | 0 | Fleet | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| ShibaClaw | 99 | Lifecycle | ❌ | ✅ 3-level | ✅ | ✅ | ⚠️ |
| phi_toolbox | 4 | IIT | ✅ Φ | ❌ | ❌ | ❌ | ❌ |
| OpenCranium | 6 | Cognition | ⚠️ Minsky | ❌ | ❌ | ❌ | ❌ |
| Level-8 | 1 | Cognition | ✅ 8-level | ❌ | ❌ | ❌ | ❌ |
| Synapse | 2 | Cognition | ✅ Recursive | ❌ | ❌ | ❌ | ❌ |

---

## Implementation Patterns

### Pattern 1: Minimal Heartbeat (Schedule-Based)

```python
import asyncio
import time

class MinimalHeartbeat:
    def __init__(self, interval_seconds=60):
        self.interval = interval_seconds
        self.running = False
    
    async def pulse(self):
        """Execute one heartbeat cycle."""
        timestamp = time.time()
        # Capture state, log, check health
        return {"timestamp": timestamp, "status": "alive"}
    
    async def run(self):
        self.running = True
        while self.running:
            result = await self.pulse()
            await asyncio.sleep(self.interval)
    
    def stop(self):
        self.running = False
```

### Pattern 2: RIIU-Based Heartbeat (Cognition-Based)

```python
class RIIUHeartbeat(nn.Module):
    """RIIU-based heartbeat with meta-state and broadcast buffer."""
    
    def __init__(self, input_dim, hidden_dim=512, meta_dim=64, buffer_len=8):
        super().__init__()
        self.hidden = nn.GRUCell(input_dim + meta_dim, hidden_dim)
        self.meta = nn.Sequential(
            nn.Linear(hidden_dim * 2 + meta_dim, meta_dim),
            nn.Tanh()
        )
        self.buffer_len = buffer_len
        self.register_buffer('buffer', torch.zeros(buffer_len, meta_dim))
        self.auto_phi = AutoPhiSurrogate(meta_dim, hidden_dim)
    
    def pulse(self, x, h, mu, buf):
        h_new = self.hidden(torch.cat([x, mu], dim=-1), h)
        mu_new = self.meta(torch.cat([h_new, h, mu], dim=-1))
        buf_new = torch.roll(buf, shifts=-1, dims=0)
        buf_new[-1] = mu_new
        phi = self.auto_phi(buf_new)
        return h_new, mu_new, buf_new, phi
```

### Pattern 3: Multi-Frequency Heartbeat

```python
class MultiFrequencyHeartbeat:
    """Multi-frequency heartbeat inspired by brain oscillations."""
    
    def __init__(self):
        self.frequencies = {
            'gamma': {'hz': 40, 'handler': self.module_competition},
            'beta': {'hz': 20, 'handler': self.routine_monitoring},
            'alpha': {'hz': 10, 'handler': self.emotional_regulation},
            'theta': {'hz': 5, 'handler': self.memory_consolidation},
            'delta': {'hz': 1, 'handler': self.deep_maintenance},
        }
    
    async def run(self):
        tasks = []
        for band, config in self.frequencies.items():
            interval = 1.0 / config['hz']
            tasks.append(self._run_band(band, interval, config['handler']))
        await asyncio.gather(*tasks)
    
    async def _run_band(self, name, interval, handler):
        while True:
            result = await handler()
            await asyncio.sleep(interval)
```

---

## Recommendations for Verdandi

Based on our comprehensive survey, we recommend the following architecture for Verdandi's heartbeat system:

### Phase 1: Foundation (Immediate)
1. **Implement minimal heartbeat** using Pattern 1 (schedule-based) with Murmur-inspired HEARTBEAT.md configuration
2. **Add CCCBot-style watchdog**: Health monitoring, auto-recovery, persona persistence
3. **Integrate Soul-Agent's 3-layer identity model**: Core persona, relationship memory, daily life rhythms

### Phase 2: Self-Awareness (Short-term)
4. **Add RIIU meta-state and broadcast buffer**: Content-agnostic introspection at each pulse
5. **Implement GWT competition**: Module-based workspace competition for "conscious" moments
6. **Add multi-frequency heartbeat**: Gamma/beta/alpha/theta/delta bands for different monitoring frequencies

### Phase 3: Consciousness (Medium-term)
7. **Integrate phi_toolbox**: Compute Φ as a consciousness metric at each heartbeat
8. **Add TRAP metacognitive module**: Transparency, Reasoning, Adaptation, Perception
9. **Implement content-agnostic introspection**: Fast detection + slow identification architecture

### Phase 4: Full Integration (Long-term)
10. **Adopt Aura's full architecture**: IIT 4.0, affective steering, GWT, active inference
11. **Implement full PEACE meta-architecture**: Predictive modeling, Error-sensitive control, Associative recall, Competitive interaction, Executive oversight
12. **Add security hardening**: Memory isolation, content provenance, behavioral gating (E→M→B defense)

### Critical Implementation Priorities

1. **Security first**: The E→M→B vulnerability (Zhang et al.) must be addressed before any heartbeat-driven background execution
2. **Content-agnostic introspection over content-rich**: Lederman & Mahowald's finding that introspection is content-agnostic suggests we should build detection first, identification second
3. **Multi-frequency over single-frequency**: Brain oscillations suggest different monitoring needs at different timescales
4. **Identity persistence from day one**: Soul-Agent's 3-layer model should be foundational, not an add-on
5. **Φ as a metric, not a truth**: phi_toolbox gives tractable Φ computation, but treat it as one metric among many, not as proof of consciousness

---

## References

### GitHub Repositories
1. youngbryan97/aura — Sovereign cognitive architecture with IIT 4.0
2. giansha/Global-Workspace-Agents — GWT implementation for LLMs
3. kitephp/soul-agent — Persistent soul with heartbeat rhythms
4. t0dorakis/murmur — AI cron daemon with HEARTBEAT.md
5. lucianlamp/CCCBot — Autonomous agent with heartbeat monitoring
6. jmmanley/phi_toolbox — Practical Φ computation
7. muxueqingze/heartbeat-agent-framework — Proactive agent framework
8. Monomoy-Strategies/heartbeat-guard — Runtime security monitoring
9. chenhg5/agencycli — Self-managing AI agent teams CLI
10. RikyZ90/ShibaClaw — Security-first AI agent
11. jorgemf/OpenCranium — Open machine consciousness architecture
12. Agnuxo1/NeuroCHIMERA — GPU-native neuromorphic consciousness
13. SamuelJacksonGrim/ProjectSynapse — Executable consciousness architecture
14. lordwilsonDev/Level8-Cognitive-Architecture — 8-level consciousness architecture
15. ibrahimcesar/conscious-landscapes — IIT computational topology
16. crustaison/crustaison — Self-improving AI agent with heartbeat
17. KyleH777/Real-Time-AI-Agent-Monitoring-System — Real-time monitoring
18. AxmeAI/ai-agent-heartbeat-monitoring — Agent health detection
19. arcane-bear/agent-watchdog — Lightweight heartbeat monitor
20. sudabg/agent-heartbeat — Minimal heartbeat, zero deps

### Academic References
21. N'guessan & Karambal (2025). "RIIU: A Differentiable Primitive for Artificial Consciousness." arXiv:2506.13825.
22. Lederman & Mahowald (2026). "Emergent Introspection in AI is Content-Agnostic." arXiv:2603.05414.
23. Zhang et al. (2026). "Mind Your HEARTBEAT!" arXiv:2603.23064.
24. Johnson et al. (2024). "Imagining and building wise machines." arXiv:2411.02478.
25. Wei et al. (2024). "Metacognitive AI: TRAP Framework." arXiv:2406.12147.
26. Gillon (2025). "Modular Consciousness Theory." arXiv:2510.01864.
27. Tononi & Boly (2025). "IIT: A Consciousness-First Approach." arXiv:2510.25998.
28. Chen, Bahsoon & Yao (2020). "DBASES Framework." arXiv:2001.07076.
29. Kinsy et al. (2018). "SAPA." arXiv:1802.05100.
30. Kernbach (2011). "Self-Awareness for Multi-Robot Organisms." arXiv:1111.5219.

---

*Document generated as part of the Verdandi Research Initiative — Open-Source Heartbeat Systems Survey*