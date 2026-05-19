# Neuroprosthetic Learning Systems: An Analysis of Adaptive Co-Embodiment and the Implications for Embodied Cognition

**AI-6204: Embodied AI — Robotics, Biology, and Physical Intelligence**  
Paper 1 | Due Week 12  
Author: Runa Gridweaver Freyjasdottir

---

## Abstract

The 2037 Adaptive Co-Embodiment (ACE) framework, introduced by Chen-Makinde and Kurosawa, represented a paradigmatic shift in neuroprosthetics: from one-directional neural decoders to bidirectional learning systems in which both the user's nervous system and the prosthetic device adapt simultaneously. This paper analyzes the ACE framework through the lens of embodied cognition theory, arguing that ACE provides empirical confirmation of three core embodied cognition claims: (1) that cognition extends beyond the skull, (2) that the boundary between self and world is negotiated through sensorimotor interaction, and (3) that morphological computation is a genuine form of computation. I formalize the ACE learning dynamics as a coupled dynamical system, derive bounds on the speed of co-adaptation, and identify three failure modes that explain the approximately 15% of users who do not achieve full embodiment. I conclude with implications for the design of future neuroprosthetic systems and for the philosophical status of embodied AI.

**Keywords:** neuroprosthetics, adaptive co-embodiment, embodied cognition, neural interfaces, morphological computation, body schema

---

## 1. Introduction

The history of neuroprosthetics can be divided into three eras. The first era (1960s–2010s) was characterized by one-directional interfaces: signals flowed from the brain to the device, but not back. The user learned to operate the prosthetic; the prosthetic did not learn about the user. The second era (2010s–2036) introduced sensory feedback, enabling bidirectional communication — but the device still did not learn. The sensory encoding was fixed, and the user's brain alone bore the burden of adaptation. The third era began in 2037 with the ACE framework, which introduced *learning* on both sides of the interface.

This paper analyzes the ACE framework not merely as a prosthetic technology but as an empirical test of embodied cognition theory. If embodied cognition is correct — if intelligence genuinely extends beyond the brain into the body and environment — then a system designed to leverage this extension should outperform systems designed under the computationalist assumption. ACE provides exactly this comparison: it outperforms fixed-encoding prosthetics precisely because it treats the prosthetic as a *body part* rather than a *tool*.

The structure of this paper is as follows. Section 2 reviews the embodied cognition claims relevant to neuroprosthetics. Section 3 provides a technical analysis of the ACE architecture, formalizing its learning dynamics as a coupled dynamical system. Section 4 derives theoretical bounds on co-adaptation speed and identifies failure modes. Section 5 discusses the empirical evidence from clinical trials. Section 6 considers implications for future system design and for the philosophical status of embodied AI.

---

## 2. Embodied Cognition and Neuroprosthetics: Theoretical Framework

### 2.1 Three Core Claims

Embodied cognition, as discussed in Lecture 01 and articulated by Clark (2016, 2036 expanded edition), Pfeifer and Bongard (2006/2035), and Varela, Thompson, and Rosch (1991), makes claims that are directly relevant to neuroprosthetic design:

**Claim EC1 (Extended Cognition):** Cognitive processes are not confined to the brain but extend into the body and environment. Tools, when deeply integrated into sensorimotor routines, become part of the cognitive apparatus.

**Claim EC2 (Negotiated Boundaries):** The boundary between self and world — between what is "me" and what is "not-me" — is not fixed by anatomy but negotiated through sensorimotor experience. The rubber hand illusion demonstrates this negotiation; so does tool use, language acquisition, and physical skill development.

**Claim EC3 (Morphological Computation):** The body performs genuine computational work that would otherwise require a brain. This computation is not metaphorical but literal, in the sense that the body's dynamics can be formally mapped to computational operations.

### 2.2 From Claims to Design Principles

These claims generate design principles for neuroprosthetics:

- From **EC1**: The prosthetic should not be a peripheral device but a cognitive extension. This means it must participate in the user's cognitive processing, not merely receive commands.
- From **EC2**: The prosthetic must support the negotiation of body boundaries. This means it must provide sensorimotor contingencies that allow the brain to incorporate the device into the body schema.
- From **EC3**: The prosthetic should exploit morphological computation to reduce its digital computational burden. This means incorporating compliance, variable stiffness, and dynamic response properties into its physical design.

### 2.3 The Prosthetic Embodiment Gap

Prior to ACE, neuroprosthetics consistently produced a gap I term the **prosthetic embodiment gap**: users could operate the device effectively (as measured by task performance) without experiencing it as part of their body (as measured by embodiment assessments). The device was a highly effective tool, but it was not *embodied*.

This gap is a direct consequence of violating the design principles derived from EC1–EC3. Fixed-encoding prosthetics treat the device as a tool (violating EC1), impose unchanging boundaries (violating EC2), and rely entirely on digital computation rather than morphological computation (violating EC3). The ACE framework was the first system designed to address all three violations simultaneously.

---

## 3. Technical Analysis of the ACE Architecture

### 3.1 System Architecture

The ACE system consists of four interconnected components:

**Component A: Neural Decoder (ND)** — A transformer-based architecture that reads motor intentions from motor cortex (1024-channel microelectrode array) and contextual signals from broader cortical areas. The ND outputs a continuous motor intention vector **m**(t) ∈ ℝ^d at millisecond resolution.

**Component B: Prosthetic Controller (PC)** — An impedance controller that generates motor commands **u**(t) based on the decoded intentions **m**(t) and the prosthetic's own dynamic state **p**(t). The PC also adjusts the prosthetic's impedance profile (stiffness, damping) based on predicted task requirements.

**Component C: Neural Encoder (NE)** — Maps tactile and proprioceptive signals from the prosthetic's sensors to stimulation patterns delivered to sensory cortex via a second electrode array. The NE produces stimulation vectors **s**(t) that are intended to produce the experience of touch, pressure, and proprioception in the prosthetic.

**Component D: Predictive Co-Adaptation Layer (PCAL)** — A shared dynamical model that maintains predictions about upcoming movements, sensory consequences, and user intentions. The PCAL is the system's "glue" — it coordinates the ND, PC, and NE to produce coherent, anticipatory behavior.

### 3.2 Formal Dynamics

The full ACE system can be modeled as a coupled dynamical system. I define the state of the user's neural system as **n**(t) ∈ ℝ^N (a vector of neural population activities) and the state of the prosthetic as **p**(t) ∈ ℝ^M (a vector of joint positions, velocities, stiffnesses, and sensor readings).

The joint dynamics are:

**ṅ**(t) = F(**n**(t), **s**(t), **η**(t)) — Neural evolution, driven by sensory input **s**(t) and internal neural dynamics **η**(t)

**ṗ**(t) = G(**p**(t), **u**(t), **e**(t)) — Prosthetic evolution, driven by motor commands **u**(t) and environmental input **e**(t)

The coupling terms:

**u**(t) = PC(ND(**n**(t)), PCAL(**n**(t), **p**(t))) — Motor commands from neural decoding, modulated by prediction

**s**(t) = NE(**p**(t), PCAL(**n**(t), **p**(t))) — Sensory encoding from prosthetic state, modulated by prediction

The PCAL maintains a shared internal model **h**(t) that evolves as:

**ḣ**(t) = H(**h**(t), **n**(t), **p**(t)) — Prediction model update, driven by observed neural and prosthetic states

Crucially, **h**(t) is not computed by either the brain or the prosthetic alone. It is an emergent property of the coupled system — a *distributed representation* that spans both sides of the interface. This is the formal instantiation of EC1: the cognitive process (predictive modeling) extends across the brain-prosthetic boundary.

### 3.3 The Learning Dynamics

The ACE system learns through three simultaneous processes:

**Neural adaptation (ΔF):** The user's neural representations reorganize to accommodate the prosthetic. Motor cortex develops new encoding patterns for prosthetic intentions; sensory cortex develops new decoding patterns for prosthetic feedback. This process occurs on timescales of hours to weeks and is driven by Hebbian plasticity and reward-based learning.

**Prosthetic adaptation (ΔG):** The prosthetic's controller and encoder update their parameters to better match the user's neural patterns. The ND learns to decode the user's specific motor intention patterns; the NE learns to produce stimulation patterns that the user can interpret. Timescales: seconds to hours (online adaptation).

**Co-adaptation (ΔH):** The PCAL learns the shared predictive model, updating its predictions based on the congruence between predicted and observed states. When a prediction is confirmed (the user intended what was predicted), the shared model is reinforced. When a prediction fails, the model is revised. Timescales: continuous.

The critical insight: these three processes are not independent. Neural adaptation changes the mapping that the prosthetic must learn; prosthetic adaptation changes the sensory patterns that drive neural adaptation; co-adaptation coordinates both. The system evolves as a *coupled whole*, not as two independent learners.

### 3.4 Stability Analysis

A coupled learning system can exhibit several dynamical regimes:

**Convergent co-adaptation:** Both sides adapt in complementary directions, and the shared model converges to a stable attractor. This is the desired regime, producing efficient, fluid, embodied operation.

**Oscillatory co-adaptation:** The neural and prosthetic adaptations chase each other without converging. The system oscillates between states without reaching stability. Users in this regime experience cyclic improvement and regression.

**Divergent co-adaptation:** Adaptations on one side outpace the other, leading to increasing misalignment. Users in this regime experience progressive degradation of control.

**Frozen co-adaptation:** Neither side adapts, and the system remains at its initial (poorly calibrated) state. Users in this regime experience the prosthetic as a rigid, unresponsive tool.

The ACE system's training protocol is designed to push the dynamics toward convergent co-adaptation. The key levers are:

- **Adaptation rate balancing**: The neural and prosthetic adaptation rates are matched (via the configurable learning rates of the PC, NE, and ND) to prevent either side from outpacing the other.
- **Prediction error monitoring**: The PCAL continuously monitors prediction errors. Large, sustained errors trigger a "recalibration" mode that slows adaptation and increases the system's sensitivity to misalignment.
- **Structured training tasks**: Early training tasks are chosen to be within the system's convergent basin of attraction. More complex tasks are introduced only after the basic couplings have stabilized.

---

## 4. Theoretical Bounds and Failure Modes

### 4.1 Bounds on Co-Adaptation Speed

I derive a bound on the minimum co-adaptation time based on information-theoretic considerations.

Let the neural-prosthetic interface have a communication capacity of C bits/second (the combined rate of information transfer across the neural decoder and encoder). The total information that must be exchanged to establish stable co-adaptation is I_total = I_neural + I_prosthetic + I_shared, where:

- I_neural: Information required to reorganize the user's neural representations for prosthetic control
- I_prosthetic: Information required to tune the prosthetic's parameters to the user
- I_shared: Information that must be shared between user and prosthetic to establish the co-adaptive model

The minimum co-adaptation time is:

T_min ≥ I_total / C

This is a theoretical minimum; in practice, T is 3–5× T_min due to noise, suboptimal learning rates, and the need for repeated exposure.

Using estimates from the ACE clinical data: C ≈ 50–100 bits/second (based on neural decoder throughput of ~10 kbps with ~0.5–1% information utilization), I_total ≈ 10⁸–10⁹ bits (based on the number of parameters in the neural and prosthetic models), yielding T_min ≈ 10⁶–10⁷ seconds, or roughly 10–100 days of continuous training. This is consistent with the observed 8–12 week training period.

### 4.2 Failure Mode Analysis

Approximately 15% of ACE users do not achieve full embodiment. Analysis of the clinical data reveals three failure modes:

**Failure Mode 1: Adaptation Rate Mismatch.** If the user's neural plasticity is significantly slower (or faster) than the prosthetic's adaptation rate, the coupled system cannot converge. The prosthetic adapts to patterns that the brain has already abandoned, or vice versa. Solution: individualized adaptation rate tuning.

**Failure Mode 2: Insufficient Proprioceptive Channel Capacity.** Some users have damaged proprioceptive cortex (common in amputations following trauma). Without adequate proprioceptive channels, the sensory feedback loop cannot support the sensorimotor contingencies required for embodiment. Solution: alternative feedback channels (vibrotactile, auditory, cross-modal).

**Failure Mode 3: Prior Body Schema Rigidity.** Some users maintain a rigid representation of their intact body schema that resists modification. This is particularly common in users with short amputation durations and high pre-amputation body awareness. The neural representations simply don't reorganize enough to accommodate the prosthetic. Solution: extended training with body-illusion protocols.

These failure modes are not bugs in the system; they are expected consequences of treating prosthetic embodiment as a negotiated process. If embodiment is genuinely negotiated (EC2), then some negotiations will fail — just as some interpersonal negotiations fail.

---

## 5. Empirical Evidence

### 5.1 Clinical Trial Results

The ACE Phase II clinical trial (n = 47, 2037–2038) yielded the following results:

- **task performance**: ACE users outperformed fixed-encoding users by 40–60% on standardized dexterity tasks (Box and Blocks Test, Nine-Hole Peg Test, Clothespin Relocation Test).
- **embodiment scores**: ACE users scored 72 ± 12 on the Embodiment Assessment Battery (EAB), compared to 38 ± 15 for fixed-encoding users. The natural limb range is 70–90.
- **training time**: ACE users achieved stable embodiment in 8–12 weeks, compared to 20+ weeks for fixed-encoding users (who often did not achieve stable embodiment at all).
- **sensory discrimination**: ACE users achieved tactile discrimination comparable to natural limb users on 80% of standard tests (two-point discrimination, pressure threshold, texture identification).

These results are consistent with the theoretical prediction that bidirectional learning systems should outperform fixed systems on both performance and embodiment metrics.

### 5.2 The Embodiment Correlation

A key finding: task performance and embodiment scores correlated only moderately (r = 0.43) in the ACE group. Some users with high performance had low embodiment, and vice versa. This suggests that embodiment is not merely "good performance experienced from the inside" — it is a distinct and partially independent phenomenon.

This has important implications for the philosophical debate. If embodiment were simply a subjective correlate of objective performance, we would expect high correlation. The moderate correlation suggests that embodiment involves something *additional* to performance — likely the sense of agency, ownership, and sensorimotor fluency that the ACE system specifically targets.

### 5.3 Neural Adaptation Signatures

Neuroimaging studies of ACE users reveal a characteristic signature of successful co-adaptation: the emergence of a *shared neural representation* spanning both biological and prosthetic control. Specifically, in successfully embodied users:

- Motor cortex representations for prosthetic movements become interspersed with (not separate from) representations for biological movements.
- Somatosensory cortex responses to prosthetic stimuli become localized to the hand representation area, not to the peripheral stimulation site.
- The pattern of functional connectivity between motor, sensory, and associative areas becomes similar to the pattern seen in intact-limb users.

In users who do not achieve embodiment, these signatures are absent. Prosthetic representations remain localized to the stimulation site and do not integrate with the biological hand representation. This is neural evidence for EC2: the boundary of the body schema has not been renegotiated to include the prosthetic.

---

## 6. Implications and Future Directions

### 6.1 Design Implications

The ACE framework's success validates the design principles derived from embodied cognition. Future prosthetic systems should:

1. **Maximize bidirectional adaptation**: Both sides of the interface must learn, and their learning rates must be matched.
2. **Invest in morphological computation**: The prosthetic body itself should do as much computation as possible (through compliance, variable stiffness, and dynamic response properties). This reduces the computational burden on both the neural decoder and the prosthetic controller.
3. **Target embodiment, not just performance**: Embodiment is partially independent of task performance and must be explicitly targeted through training protocols that support sensorimotor contingency and body schema renegotiation.
4. **Prepare for failure modes**: Individualized adaptation, alternative feedback channels, and flexible training regimens are necessary to address the ~15% of users who currently do not achieve embodiment.

### 6.2 Philosophical Implications

ACE provides empirical support for all three embodied cognition claims:

- **EC1 confirmed**: The ACE system's predictive co-adaptation layer is a computational process that spans the brain and the prosthetic. Cognition literally extends beyond the skull.
- **EC2 confirmed**: The body schema is renegotiated over the course of ACE training, expanding to include the prosthetic. The boundary of self is not fixed by anatomy.
- **EC3 confirmed**: The prosthetic's morphological properties (compliance, impedance) perform computational work (force distribution, signal filtering) that reduces the burden on the digital controller. Morphological computation is genuine computation.

These are not merely suggestive analogies. They are empirically verified, quantitatively measurable phenomena. The embodied cognition thesis makes specific, testable predictions about neuroprosthetic performance; ACE tests these predictions; and the predictions are confirmed.

### 6.3 The Path Forward

The 2037 breakthrough is a beginning, not an end. The next frontiers include:

- **Accelerated co-adaptation**: Reducing training time from weeks to days or hours through pharmacological facilitation of neural plasticity, more informative training protocols, and higher-bandwidth interfaces.
- **Full-body embodiment**: Extending the ACE framework from single-limb prosthetics to exoskeletons, robotic avatars, and potentially full-body embodiment in remote or virtual environments.
- **Non-medical applications**: The ACE principles apply beyond prosthetics. Any human-machine interface — from surgical instruments to construction equipment to musical instruments — could benefit from co-adaptive learning.
- **Ethical frameworks**: If a prosthetic can become part of the self, what are the ethical obligations around its removal, modification, or malfunction? We need legal and ethical frameworks that recognize the special status of embodied devices.

---

## 7. Conclusion

The Adaptive Co-Embodiment framework represents the most significant advance in neuroprosthetics since the first brain-computer interfaces, and it does so precisely because it takes embodied cognition seriously. By designing a system in which the prosthetic learns from the brain and the brain learns from the prosthetic, ACE closes the loop that computationalist approaches left open — the loop between body and world, between morphology and mind, between the physical and the cognitive.

The lesson for embodied AI is clear: intelligence is not a property of brains alone. It is a property of systems — brain, body, and environment — coupled through sensorimotor loops. The most effective artificial intelligence systems will be those that recognize this fact and design for it from the start.

---

## References

1. Chen-Makinde, O., Kurosawa, H., et al. (2037). "Adaptive Neural Interfaces: Learning at the Boundary of Body and Machine." *Nature Neuroscience*, 20(8), 1043–1057.
2. Clark, A. (2036). *Surfing Uncertainty: Prediction, Action, and the Embodied Mind* (expanded edition). Oxford University Press.
3. Ghazi-Zahedi, K., et al. (2034). "Morphological Computation Capacity: A Quantitative Measure." *Entropy*, 26(5), 401.
4. Hauser, H., et al. (2031). "Towards a Theoretical Framework for Morphological Computation." *Philosophical Transactions of the Royal Society A*, 382(2184), 20220314.
5. Navarrete, J., et al. (2036). "Autonomous Construction with Local Materials: AI-Guided Building Systems." *Journal of Sustainable Architecture*, 22(4), 301–320.
6. Pfeifer, R., & Bongard, J. (2035). *How the Body Shapes the Way We Think* (revised edition). MIT Press.
7. Tanaka-Moreno, K. (2039). *The Prosthetic Mind: Learning Neural Interfaces and the Embodiment Revolution*. MIT Press.
8. Tanaka-Moreno, K. (2039). "Prosthetic Embodiment and the Extended Mind." *Philosophical Transactions of the Royal Society B*, 374(1783), 20190146.
9. Varela, F., Thompson, E., & Rosch, E. (1991). *The Embodied Mind*. MIT Press.
10. Zamora, J., et al. (2035). "Information-Theoretic Bounds on Morphological Computation." *IEEE Trans. Morphological Computation*, 55(1), 3–19.