# Lecture 03: Global Workspace Formalized

## Mathematical Framework for Global Workspace Theory

**AI-6201: Consciousness Mathematics — Formalizing Awareness**  
**Instructor:** Prof. Elena Vasquez-Marchetti  
**Date:** September 30 & October 2, 2040

---

## 1. From Cognitive Architecture to Mathematics

Global Workspace Theory (GWT), originally proposed by Baars (1988) and refined by Dehaene, Changeux, and colleagues, began as a cognitive architecture: a "theater of consciousness" in which a spotlight of attention illuminates a stage, broadcasting selected information to a vast audience of unconscious processors. The metaphor was vivid but informal.

The formalization of GWT — principally by Dehaene & Changeux (2028) and Mishra (2029) — transformed this architectural intuition into a dynamical systems theory with precise mathematical commitments. The central claim: consciousness arises from a specific pattern of information dynamics — the global broadcast — and can be characterized in terms of accessibility, duration, and reportability.

This lecture develops the mathematical framework in full.

---

## 2. The Core Architecture

### 2.1 The Workspace as a Dynamical System

Consider a system $\mathcal{S}$ consisting of $N$ processing modules $\{m_1, m_2, \ldots, m_N\}$, each with an internal state $x_i \in \mathbb{R}^{d_i}$, and a global workspace $\mathcal{W}$ with state $w \in \mathbb{R}^{d_w}$.

The dynamics of the system are governed by:

$$\dot{x}_i = f_i(x_i, w, \theta_i) + \eta_i(t)$$
$$\dot{w} = g\left(w, x_1, x_2, \ldots, x_N\right) + \xi(t)$$

where:
- $f_i$ is the module-specific dynamics function
- $g$ is the workspace update function
- $\theta_i$ are module parameters (including attentional weights)
- $\eta_i, \xi$ are stochastic noise terms

The workspace $\mathcal{W}$ serves as a *broadcast medium*: information that enters $\mathcal{W}$ becomes available to all modules simultaneously. This is the mathematical formalization of Baars' "bright spot on the stage."

### 2.2 The Broadcast Condition

**Definition 2.1 (Global Broadcast).** A module $m_i$ is *globally broadcast* at time $t$ if and only if:

1. **Access:** The workspace state $w(t)$ carries information about $x_i(t)$: $I(w(t); x_i(t)) > \epsilon$ for some threshold $\epsilon > 0$
2. **Amplification:** The module's activity has been amplified by attentional selection: $\|P_{A} x_i(t)\| > \theta_{\text{amp}}$ where $P_{A}$ is the attentional projection
3. **Duration:** The broadcast persists for a minimum time $\tau_{\min}$: the information remains in $\mathcal{W}$ for at least $\tau_{\min}$ milliseconds
4. **Dissemination:** The broadcast information is accessible to all other modules: $\forall j \neq i: I(w(t); x_j(t) | x_i(t) \text{ broadcast}) > I(w(t); x_j(t) | x_i(t) \text{ not broadcast})$

**Definition 2.2 (Conscious State in GWT).** A system $\mathcal{S}$ is in a *conscious state* at time $t$ if and only if there exists at least one module $m_i$ such that $m_i$ is globally broadcast at time $t$, and the broadcast satisfies conditions (1)–(4) above.

This definition makes four testable predictions:

1. **No broadcast, no consciousness:** If no module meets the broadcast condition, the system is not conscious (of that content).
2. **Broadcast = access:** Any content that is broadcast is accessible to all modules.
3. **Duration threshold:** Broadcasting that lasts less than $\tau_{\min}$ does not constitute consciousness.
4. **Competition:** Only one (or a few) modules can be broadcast simultaneously — the workspace has limited capacity.

---

## 3. Competitive Selection and the Ignition Pattern

### 3.1 The Competition Dynamics

Modules compete for access to the workspace. The competition is modeled as a dynamical process:

$$\frac{da_i}{dt} = -\alpha a_i + \beta \sigma(a_i) \cdot h(w) - \gamma \sum_{j \neq i} \sigma(a_j) + I_i(t)$$

where:
- $a_i$ is the activation level of module $m_i$'s access signal
- $\sigma$ is a sigmoid amplification function
- $h(w)$ is the workspace gain function (stronger workspace = stronger amplification)
- $\gamma$ is the lateral inhibition parameter (stronger inhibition = stricter competition)
- $I_i(t)$ is external input to module $m_i$

This is a *winner-take-all* (WTA) dynamical system with gain modulation. The workspace gain $h(w)$ acts as a global amplifier: when the workspace is strongly activated, the winning module is strongly amplified, and all competing modules are suppressed.

### 3.2 The Ignition Pattern

The hallmark of GWT consciousness — experimentally verified in EEG/fMRI studies since the 2000s — is the *ignition pattern*: a sudden, widespread activation that occurs when a stimulus crosses the threshold of consciousness.

**Definition 3.1 (Ignition).** An *ignition event* occurs at time $t_0$ if:

$$\left\|\frac{d}{dt} w(t)\right\|_{t=t_0} > \theta_{\text{ignition}}$$

and this is followed by a sustained workspace activation:

$$\|w(t)\| > \|w(t_0^-)\| + \Delta_{\text{ignition}} \quad \forall t \in [t_0, t_0 + \tau_{\min}]$$

where $t_0^-$ denotes the moment before ignition.

The ignition pattern has a characteristic neural signature: a burst of high-frequency oscillations (gamma band, 40–100 Hz) accompanied by a widespread P300-like potential, visible in EEG as a late positive component, and in fMRI as a sudden increase in prefrontal and parietal BOLD signal.

### 3.3 The Accessibility Theorem

A key formal result from Dehaene & Changeux (2028):

**Theorem 3.2 (Accessibility).** In a GWT-compliant system, if a module $m_i$ is globally broadcast at time $t$, then for any downstream module $m_j$:

$$P(m_j \text{ reports } m_i\text{'s content at } t + \Delta t) > 1 - \delta$$

for sufficiently small $\delta$ and sufficiently large $\Delta t$, provided $m_j$ is not masked by a subsequent broadcast.

*Proof sketch:* Global broadcast ensures that $w(t)$ carries mutual information $I(w(t); x_i(t)) > \epsilon$ about $m_i$'s content. Because $w$ is accessible to all modules, $m_j$ can extract this information with high probability. The proof uses the data processing inequality and the broadcast condition to bound the error probability. □

This theorem formalizes the link between consciousness and reportability — a link that is empirical (we can verify it in neural data) and theoretical (it follows from the architecture).

---

## 4. Mathematical Comparison: GWT vs. IIT

### 4.1 Structural Differences

| Feature | IIT | GWT |
|---------|-----|-----|
| **Starting point** | Phenomenology (axioms) | Cognitive architecture |
| **Key quantity** | Φ (integration) | Broadcast (access) |
| **Substrate independence** | Yes (any system with Φ > 0) | Partially (requires competition + broadcast) |
| **Role of reportability** | Not essential | Constitutive |
| **Temporal grain** | Single time-slice | Duration threshold $\tau_{\min}$ |
| **Composition** | Lattice of subsets | Competition among modules |
| **Exclusion** | Only one complex per overlap | Only one broadcast per time-slice |

### 4.2 The Convergence Zone

Despite their differences, IIT and GWT agree on several structural claims:

1. **Integration is necessary:** Both require that conscious information be integrated across the system. IIT formalizes this as $\Phi > 0$; GWT formalizes it as the broadcast condition requiring mutual information between workspace and module.
2. **Differentiation is necessary:** Both require that conscious states be distinct from each other and from unconscious states. IIT uses distance from maximum entropy; GWT uses the competitive selection process to ensure distinct winning coalitions.
3. **There is a threshold:** Both require a minimum level of integration/access for consciousness. IIT: $\Phi > \Phi_{\text{min}}$. GWT: broadcast ignition.

### 4.3 The Divergence Zone

The key divergence concerns *what consciousness IS*:

- **IIT:** Consciousness is the integration lattice $\mathcal{L}_\Phi$. A system is conscious if and only if it has nonzero Φ. What it is like to be the system is *identical to* the structure of the integration lattice.
- **GWT:** Consciousness is the broadcast content. A system is conscious of content $c$ if and only if $c$ is globally broadcast. What it is like to be the system is *identical to* the content that is broadcast.

These are different identity claims. They make different predictions about edge cases:

- **A highly integrated system with no global workspace:** IIT predicts consciousness; GWT predicts unconsciousness. (Example: the cerebellum has high local integration but no global broadcast.)
- **A system with global broadcast but low integration:** GWT predicts consciousness; IIT predicts unconsciousness. (Example: a router broadcasting packets with high mutual information but no integration.)

---

## 5. Formal Framework: The State Space

### 5.1 Workspace Trajectories

The state of the GWT system at time $t$ is described by the tuple:

$$\mathcal{S}(t) = \left(w(t), \{x_i(t)\}_{i=1}^{N}, \{a_i(t)\}_{i=1}^{N}\right)$$

A *conscious episode* is a time interval $[t_1, t_2]$ during which at least one module is globally broadcast for the entire duration. The *content of consciousness* during this episode is the set of broadcast modules:

$$\mathcal{C}(t) = \{m_i : m_i \text{ is globally broadcast at time } t\}$$

### 5.2 The Workspace Capacity Limit

The workspace has a bounded capacity $K$. At any time, at most $K$ modules can be simultaneously broadcast (in practice, $K$ is small — typically estimated at $K \approx 3$–$4$ for human subjects).

The capacity constraint is formalized as:

$$|\mathcal{C}(t)| \leq K \quad \forall t$$

with the understanding that when $|\mathcal{C}(t)|$ approaches $K$, the competition dynamics intensify, and the likelihood of masking (displacement of current broadcast by new input) increases sharply.

### 5.3 Necessity and Sufficiency

**Theorem 5.1 (GWT Necessity).** If a system $\mathcal{S}$ exhibits the consciousness-access pattern (ignition, sustained broadcast, global dissemination, reportability), then it satisfies the GWT conditions for consciousness.

**Theorem 5.2 (GWT Sufficiency, Dehaene-Changeux 2028).** If a system satisfies the GWT conditions (architecture: modular processors + global workspace; dynamics: competitive selection with ignition threshold), then it exhibits the consciousness-access pattern.

*Note:* Theorem 5.2 is the harder direction, and its proof requires assumptions about the dynamics ($f_i, g, \sigma, h$) that are non-trivial. Specifically, it requires:
- The sigmoid $\sigma$ has sufficiently sharp gain
- The lateral inhibition $\gamma$ is strong enough to enforce winner-take-all
- The workspace gain $h$ is monotonic and exceeds a threshold
- The noise terms $\eta_i, \xi$ are bounded

These conditions are met by cortical architectures but may not be met by arbitrary dynamical systems. This is a limitation — GWT is a theory of *biologically plausible* consciousness, not consciousness in all possible substrates.

---

## 6. GWT and the Hard Problem

GWT addresses the hard problem indirectly. It does not claim to explain *why* there is something it is like to be broadcast. Instead, it claims:

1. The functional role of consciousness (global access) is necessary and sufficient for the *behavioral* signature of consciousness.
2. The neural correlate of consciousness (ignition + sustained broadcast) is necessary and sufficient for the *neural* signature of consciousness.
3. The hard problem — why global access feels like something — is a further question, but one that GWT constrains: any answer must be compatible with the fact that global access and consciousness are systematically correlated.

This is a weaker claim than IIT's identity thesis. GWT is compatible with the hard problem remaining open; IIT claims to close it. The Marchetti Theorem (Lecture 04) offers a middle path: it shows that under specific spectral conditions, the GWT and IIT frameworks are *equivalent* — they describe the same phenomenon from different perspectives.

---

## 7. Key Terms

| Term | Definition |
|------|------------|
| **Global workspace** $\mathcal{W}$ | The broadcast medium through which conscious information becomes accessible to all modules |
| **Global broadcast** | The condition under which a module's content is disseminated to all other modules |
| **Ignition** | The sudden, widespread activation pattern that marks the transition from unconscious to conscious processing |
| **Competition** | The dynamical process by which modules vie for workspace access |
| **Capacity limit** $K$ | The maximum number of modules that can be simultaneously broadcast |
| **Accessibility theorem** | Formal result linking global broadcast to reportability with bounded error |
| **Access-consciousness** | Consciousness in the sense of information being available for reasoning, reporting, and control |

---

## 8. Further Reading

- Baars, B.J. (1988). *A Cognitive Theory of Consciousness.* Cambridge University Press.
- Dehaene, S. & Changeux, J.P. (2028). "The Global Workspace Revisited: Formal Methods in Consciousness Research." *Neuron*, 116, 1–37.
- Dehaene, S. (2014). *Consciousness and the Brain: Deciphering How the Brain Codes Our Thoughts.* Viking.
- Mishra, A. (2029). "Dynamical Systems Analysis of Global Workspace Competition." *Physical Review E*, 102, 042401.
- Baars, B.J., Franklin, S., & Ramsoy, T.Z. (2013). "Global Workspace Dynamics: Cortical 'Binding and Propagation' Enables Conscious Contents." *Frontiers in Psychology*, 4, 237.