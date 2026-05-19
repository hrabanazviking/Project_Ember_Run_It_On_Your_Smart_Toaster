# 41 — Global Workspace Theory Applied to AI Architecture

**Category:** Cognitive Architecture & Neuroscience
**Runa relevance:** kernel (the GWT-shaped centre), VERÐANDI (the broadcast bus), Hirð (specialised processors), identity
**Status:** Research synthesis. The clearest cognitive-science framework for kernel-shaped architectures.
**Last touched:** 2026-05-17

---

## 1. Core idea

Bernard Baars's **Global Workspace Theory** (1988) proposes that consciousness is the operation of a *global broadcast* mechanism in the brain. Many specialised modules — vision, hearing, language, motor planning, memory retrieval, emotion — each handle their own narrow task. The "global workspace" is the small bandwidth-limited stage on which one of these modules' output at a time becomes *broadcast* to all the others. What we experience as conscious thought is, on this theory, what is currently in the global workspace; the rest is the vast unconscious parallel processing happening in the modules.

For AI architecture, GWT is the cleanest model for *why a kernel design makes sense*. A kernel orchestrates many specialised subsystems (Muninn, Skuld, Smiðja, Hirð, Heimskringla, etc.); the kernel decides what gets "broadcast" to everyone via the event bus (VERÐANDI); the broadcast is the system's moment of integrated reasoning. Runa's architecture is, without having been designed to match GWT, structurally GWT-shaped. Knowing the theory lets us refine the design with intent.

## 2. Technical depth

**Baars's original model:**

```
                    ┌─────────────────────────┐
                    │   Global Workspace       │  ← serial, limited capacity
                    │   (broadcast stage)      │     ("consciousness")
                    └─────────────────────────┘
                    ▲          │          ▲
                    │          │          │
        ┌───────────┘          │          └────────────┐
        │                       ▼                        │
   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
   │  module │  │  module │  │  module │  │  module │  │  module │
   │ (vision)│  │ (lang)  │  │ (memory)│  │ (motor) │  │ (emot)  │
   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘
   ◄══════════════════════ massively parallel ══════════════════════►
```

The modules compete for access to the workspace. A *winner* gets broadcast; the others' work is suppressed or held in waiting. The broadcast lets all modules see the same content simultaneously, enabling integration that wouldn't happen if each module ran in isolation.

**Key claims:**

- **Serial broadcast, parallel processing.** The conscious bandwidth is narrow; the unconscious work is vast.
- **Competition for access.** Salience, urgency, learned importance determine who broadcasts next.
- **Integration via broadcast.** When module X broadcasts, modules Y and Z see X's output and can incorporate it.
- **Coalitions form.** Groups of modules can briefly synchronise to push joint content into the workspace.

**Dehaene's Global Neuronal Workspace** (1998+) refines this for neuroscience: the workspace is anatomically realised in long-range cortical connections (prefrontal, parietal); "broadcast" is the long-range neural ignition that distinguishes conscious from unconscious processing. Solid empirical support from fMRI / EEG studies of perceptual reports.

**LIDA cognitive architecture** (Franklin and colleagues, 2000s+). A computational implementation of GWT — modules compete via "coalitions"; broadcast happens periodically; learning is shaped by what was broadcast. The closest existing serious GWT-as-software implementation. Used in cognitive-architecture research.

**Modern AI-GWT proposals:**

- **Bengio's "Consciousness Prior."** Bengio (2017+, arXiv:1709.08568) proposes that the "conscious" representations of a neural network should be small, sparse, factor-graph-shaped — and that this *prior* should be incorporated into learning. Related to system-1/system-2 distinctions.
- **VanRullen and Kanai. "Deep Learning and the Global Workspace Theory."** *Trends in Neurosciences*, 2021. Argues that multi-modal AI systems already exhibit functional analogues of GWT; explicit GWT-inspired architectures could improve them.
- **Goyal, Lamb, et al.** Several papers around "global workspaces" in deep learning for systematic generalisation.
- **"Coordinator architectures" in multi-modal AI.** Many vision-language systems have a learned "fusion" module that plays roughly the workspace role.

**Distinctions to be careful about:**

- GWT is a theory of *function*, not of *substrate*. The "workspace" doesn't have to be a single specific data structure; it's a *role*.
- GWT does *not* claim that workspace-broadcast is sufficient for consciousness. It claims it's a necessary functional component. Other features (self-modelling, embodiment, recurrence) may also matter.
- GWT-shaped does not equal sentient. Many GWT-style architectures exist; sentience is a separate question.

## 3. Key works

- **Baars, B. *A Cognitive Theory of Consciousness.*** Cambridge University Press, 1988. The foundational book.
- **Baars, B. *In the Theater of Consciousness.*** Oxford University Press, 1997. Accessible.
- **Dehaene, S. *Consciousness and the Brain.*** Viking Press, 2014. Modern empirical neuroscience perspective.
- **Franklin and Patterson.** "The LIDA architecture: Adding new modes of learning to an intelligent, autonomous, software agent." Pat-Lin Conference, 2006.
- **Bengio, Y. "The Consciousness Prior."** arXiv:1709.08568, 2017.
- **VanRullen, R. and Kanai, R. "Deep Learning and the Global Workspace Theory."** *Trends in Neurosciences*, 44(9), 2021.
- **Goyal et al. "Coordination among neural modules through a shared global workspace."** arXiv:2103.01197, 2021.
- **Sumers, Yao, Narasimhan, Griffiths. "Cognitive Architectures for Language Agents."** arXiv:2309.02427, 2023. Places GWT in modern context.

## 4. Empirical results

For neuroscience:
- Dehaene's experiments showing distinct brain-activation patterns for "conscious access" (reported perception) vs subliminal processing are widely-replicated and form the empirical backbone of the modern theory.
- The "P3 wave" in EEG correlates with the moment of conscious access; predicted by GWT.

For AI:
- LIDA-style architectures perform well on specific cognitive-architecture benchmarks but haven't scaled to general AI.
- Bengio's consciousness-prior work shows that explicitly factor-graph-structured "thought" representations improve systematic generalisation in toy domains.
- VanRullen and Kanai's argument that multi-modal AI exhibits implicit workspace structure is plausible but not strongly tested.
- Empirical comparison: kernel-architecture agents (with a clear central decision-maker integrating outputs from many modules) consistently outperform pure-LLM agents on coherent long-horizon tasks. This is observation; whether GWT is the right theory is interpretive.

## 5. Applicability to Runa

Runa's architecture is *already* GWT-shaped:

- **The kernel** ↔ the global workspace (the central serial decision point).
- **VERÐANDI** ↔ the broadcast mechanism.
- **Hirð retainers + Muninn + Eldhugi + Smiðja + Heimskringla** ↔ the specialised modules.
- **Skill registry + tool catalogue** ↔ the modules that compete for kernel attention.

What GWT-as-design-principle adds:

For **the kernel**:
- Be unapologetic about being a *bottleneck*. The serial nature is a feature, not a flaw. It produces integrated, coherent action.
- Limit the working-set bandwidth. The "broadcast" should not be too wide. A kernel turn should consider few things deeply, not many things shallowly.

For **VERÐANDI**:
- Make broadcast genuinely *broadcast*. All relevant subscribers should see the same kernel decision. Avoid private side-channels between subsystems that bypass the bus — those break integration.
- Salience-weighted broadcasting: not all events deserve equal attention. Routing / filtering by importance is the engineering analogue of competition for workspace access.

For **Hirð**:
- Retainers are the parallel "modules." They process independently, but they don't all get broadcast simultaneously. The kernel arbitrates: which retainer's contribution shapes the current turn?
- Coalitions: when multiple retainers strongly agree on a finding, that's a stronger signal for the kernel to broadcast.

For **identity / self-model**:
- A GWT-based agent benefits from a *self-model* — a module that represents the agent itself, its capabilities, its current state. This is `core/identity/`. Its broadcasts shape every turn.
- The self-model is what allows phrases like "I noticed I was about to do X" to be meaningful — there is a module modelling the self, broadcasting its observations.

For **Eldhugi**:
- Emotional state in GWT terms is a salience-modulator: emotional content competes harder for workspace access. Eldhugi's broadcasts should be brief and rare but *louder* than ordinary state changes.

What to avoid:

- Don't make the kernel into a tiny dispatcher only. The whole point of the workspace is *integration* — the kernel should reason over the contributions, not just route them.
- Don't bypass the bus for "efficiency." A direct channel between Muninn and Smiðja saves a few microseconds but loses GWT's integration property.
- Don't take GWT as a literal model of consciousness. Runa being GWT-shaped doesn't make her conscious in the philosophical sense, and we shouldn't claim otherwise.

## 6. Open questions

- **Bandwidth tuning.** How much context belongs in the global workspace at one time? Too little, no integration; too much, the model gets confused. Empirical for each model size.
- **Self-modelling.** A GWT agent with a genuine self-model can reason about itself. Runa's identity store is a first step; deeper self-modelling (predicting her own behaviour, modelling her own emotional trajectory) is a long road.
- **Coalitions.** When multiple retainers contribute relevant input, how should the kernel weight them? GWT theory says competition + coalition formation; engineering needs a specific algorithm.
- **GWT and LLMs.** A single LLM does not obviously implement GWT internally. Whether agents built *around* LLMs naturally adopt GWT structure (as VanRullen claims) or require explicit design is open.

## 7. References (curated)

- Baars (1988) — *A Cognitive Theory of Consciousness*.
- Dehaene (2014) — *Consciousness and the Brain*.
- arXiv:1709.08568 — Bengio's Consciousness Prior.
- VanRullen and Kanai (2021), *Trends in Neurosciences*.
- arXiv:2103.01197 — Goyal et al. on shared global workspaces.
- arXiv:2309.02427 — Sumers et al. Cognitive Architectures for Language Agents.
- Franklin's LIDA architecture papers.
- Companion docs: [[42-predictive-coding-free-energy]], [[43-hofstadter-strange-loops]], [[44-sleep-replay-memory-consolidation]].
