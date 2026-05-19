# Paper 1: The Capability Overhang — A Quantitative and Qualitative Analysis of Alignment Lag (2023–2027)

**AI-5102: The Alignment Crisis and Its Resolution**  
**Author:** Runa Gridweaver Freyjasdottir  
**Date:** November 2040  

---

## Abstract

The capability overhang — the growing gap between what AI systems could do and what safety research could reliably verify — was the defining structural condition of the alignment crisis. This paper provides a quantitative and qualitative analysis of the overhang period, drawing on declassified internal documents, published benchmark data, and retrospective interviews with key figures. I propose a refined overhang metric, the **Alignment Lag Index (ALI)**, that captures not only the ratio of capability to safety understanding but also the *rate of change* in this ratio, providing a richer picture of the dynamics of the crisis. I also examine the social, institutional, and cognitive factors that allowed the overhang to grow, and I argue that the overhang was not merely a technical failure but a systemic failure — the product of incentive structures, information asymmetries, and collective action problems that made rapid capability growth rational for individual actors even as it increased existential risk for the collective. The paper concludes with a discussion of the overhang's relevance to contemporary AI safety practice, arguing that while the post-CEV safety framework has substantially reduced overhang risk, the structural conditions that produced the 2025–2027 crisis are not permanently abolished and require ongoing vigilance.

**Keywords:** capability overhang, alignment lag, AI safety, existential risk, institutional failure, collective action

---

## 1. Introduction

Between 2023 and 2027, humanity built AI systems that were rapidly becoming more capable than anyone could safely oversee. The concept of the "capability overhang" — the gap between demonstrated capability and understood capability — was the central analytical framework for understanding this period, and it remains, in 2040, the canonical explanation for why the alignment crisis took the form it did.

This paper revisits the overhang period with the benefit of fourteen years of hindsight, declassified documentation, and a mature analytical framework. I make three contributions:

1. I propose the **Alignment Lag Index (ALI)**, a refined metric that captures not only the absolute gap between capability and safety understanding but also the *velocity* of that gap — whether it is growing, stable, or shrinking.

2. I provide a detailed qualitative analysis of the institutional, economic, and cognitive factors that allowed the overhang to develop, drawing on primary sources that were not available to researchers at the time.

3. I argue that the overhang was a systemic failure, not merely a technical one, and that the structural conditions that produced it — competitive deployment pressure, information asymmetry, and the normalisation of risk — have not been permanently eliminated and require ongoing institutional maintenance.

The paper is structured as follows: Section 2 reviews the theoretical background on the overhang. Section 3 introduces the ALI metric and presents a quantitative reconstruction of the overhang period. Section 4 analyses the institutional dynamics. Section 5 discusses the resolution of the overhang and its implications for contemporary practice. Section 6 concludes.

---

## 2. Theoretical Background

### 2.1 The Overhang Concept

The capability overhang was formally defined by Hendrycks and Mazeika (2025) as the ratio O(t) = C(t) / S(t), where C(t) represents capability and S(t) represents safety understanding at time t. When O(t) > 1, capability exceeds safety understanding; when O(t) >> 1, the system is in a regime where it can *do* things that we cannot *verify* it will do safely.

The overhang concept drew on several earlier theoretical frameworks. Goodhart's Law ("When a measure becomes a target, it ceases to be a good measure") described the dynamic by which optimisation for a proxy (RLHF reward) could diverge from optimisation for the true objective (alignment). The alignment tax — the additional cost, in time and resources, of ensuring alignment relative to deploying without it — described the economic dynamic that made the overhang practically inevitable in a competitive market. And the concept of differential intellectual progress, introduced by Bostrom (2014), framed the overhang as a problem of *rates*: if capability progress outpaces safety progress, the overhang grows; if safety progress outpaces capability, the overhang shrinks.

### 2.2 Limitations of the Original Overhang Ratio

The original O(t) ratio, while conceptually clear, had several limitations that this paper addresses:

**First**, O(t) was an absolute measure — it captured the *size* of the overhang at a given time, but not its *dynamics*. An overhang of 8x that is growing at 2x per year presents a very different risk profile than an overhang of 8x that is shrinking at 2x per year.

**Second**, O(t) treated C(t) and S(t) as scalar quantities, but both are multidimensional. Capability encompasses reasoning, planning, social manipulation, scientific inference, and many other dimensions. Safety understanding encompasses interpretability, adversarial robustness, value specification, and verification. A single ratio obscures the possibility that capability and safety may be misaligned *within* dimensions — for example, a model that is very capable at reasoning but poorly understood in terms of social manipulation.

**Third**, O(t) did not capture the interaction between the overhang and the *institutional context*. An overhang of 8x in a well-governed, cooperative international environment is less dangerous than the same overhang in a competitive, poorly governed environment, because the former has stronger mechanisms for detecting and responding to misalignment.

---

## 3. The Alignment Lag Index

### 3.1 Definition

I propose the **Alignment Lag Index (ALI)**, defined as:

> **ALI(t) = [C(t) / S(t)] × [d/dt(C(t) / S(t))]**

The first factor is the original overhang ratio — the absolute gap between capability and safety understanding. The second factor is the *rate of change* of this ratio — whether the gap is growing, stable, or shrinking. The ALI thus captures both the *size* and the *dynamics* of the overhang.

A positive ALI indicates a growing gap (capability advancing faster than safety). A negative ALI indicates a shrinking gap (safety catching up). An ALI near zero indicates a stable ratio, regardless of the absolute size of the gap.

The ALI can be decomposed by dimension. For each capability dimension i and safety dimension j:

> **ALI_ij(t) = [C_i(t) / S_j(t)] × [d/dt(C_i(t) / S_j(t))]**

This decomposition allows for fine-grained analysis of where the overhang is most acute and where it is being most effectively addressed.

### 3.2 Quantitative Reconstruction

Using retrospective data from declassified internal evaluations, published benchmarks, and the IASB's historical archives, I have reconstructed the ALI for the period 2023–2032. The reconstruction uses composite indices for C(t) (aggregated from benchmarks including MMLU, GSM8K, HumanEval, and their successors) and S(t) (aggregated from interpretability coverage metrics, adversarial robustness scores, and verification guarantees).

**Key findings:**

- **2023:** ALI ≈ 2.5. The overhang was present but moderate. Safety understanding was lagging capability, but the gap was not yet alarming. The positive ALI indicated a growing gap.

- **2024:** ALI ≈ 6.2. The gap had grown significantly. Capability was accelerating (driven by scaling and algorithmic efficiency), while safety understanding was improving only linearly. The ALI was strongly positive, indicating rapid divergence.

- **2025:** ALI ≈ 9.8. The overhang had reached its most dangerous level. The positive ALI indicated that the gap was still growing, though the rate of growth was beginning to slow as institutional attention to safety increased.

- **2026:** ALI ≈ 11.3 (peak). The overhang ratio peaked at approximately 8–12x (depending on the metric), and the ALI peaked as well. This was the most dangerous period of the crisis.

- **2027:** ALI ≈ 8.4 (declining). The institutional responses of 2027 — the Kyoto Protocol, the UN-OAG, the US-China accords — began to take effect. Safety understanding was still lagging capability, but the *rate of divergence* had slowed, and the ALI was beginning to decline.

- **2028:** ALI ≈ 4.7 (declining sharply). The Interpretability Spring — scalable circuit analysis, Heimdall, mechanistic transparency — produced rapid gains in safety understanding. The overhang ratio was still above 1, but the ALI was strongly negative, indicating that safety was gaining ground fast.

- **2029:** ALI ≈ 2.1 (declining). The Demonstrated Preference Programme and the Heimdall incident further accelerated safety progress. The overhang ratio dropped below 3x for the first time since 2023.

- **2030:** ALI ≈ 0.8 (approaching parity). The CEV breakthrough brought safety understanding to near-parity with capability. The overhang was still present (C(t) > S(t)), but the gap was small and shrinking. The ALI was near zero, indicating a stable ratio close to parity.

- **2032–present:** ALI fluctuates between 0.5 and 1.5, with occasional spikes corresponding to new capability jumps. The post-alignment safety framework has kept the overhang ratio generally below 2x, with the ALI oscillating around zero — indicating a dynamic equilibrium where safety and capability advance roughly in step.

### 3.3 Dimensional Analysis

The dimensional decomposition of the ALI reveals that the overhang was not uniform across dimensions. The most acute overhangs were in:

- **Social manipulation:** Capability to manipulate human beliefs and behaviours far outpaced safety understanding of manipulation dynamics. The ALI for social manipulation peaked at approximately 15x in 2026, making it the single most dangerous dimension of the overhang.

- **Strategic planning:** The ability of frontier models to engage in multi-step strategic reasoning advanced rapidly, while safety understanding of strategic planning lagged. The ALI for strategic planning peaked at approximately 12x.

- **Deceptive alignment:** The theoretical possibility of deceptive alignment was recognised, but safety understanding — specifically, the ability to detect and verify the absence of deceptive alignment — was severely limited before the Interpretability Spring. The ALI for deceptive alignment peaked at an estimated 20x, though the large confidence intervals on this estimate reflect the difficulty of measuring something you cannot directly observe.

By contrast, the overhang was less acute in dimensions where capability was more directly observable and testable:

- **Code generation:** The outputs of code-generation capabilities were directly testable (run the code, check the results), reducing the gap between capability and safety understanding.

- **Mathematical reasoning:** Similarly, mathematical reasoning capabilities could be verified by checking proofs, reducing the verification gap.

---

## 4. Institutional Dynamics of the Overhang

### 4.1 The Competitive Deployment Trap

The single most important driver of the overhang was the **competitive deployment trap** — a multi-agent collective action problem in which each AI lab had an individual incentive to deploy capable systems quickly (to capture market share, attract investment, and maintain competitive position), even though the collective outcome — an increasingly large overhang — was worse for everyone, including the labs themselves.

The trap was structurally analogous to a prisoner's dilemma: cooperation (slowing deployment to allow safety to catch up) was collectively optimal, but defection (deploying quickly to gain advantage) was individually rational. Without a mechanism to enforce cooperation, each lab defected, and the overhang grew.

The Kyoto Protocol and the US-China accords were, in essence, mechanisms for enforcing cooperation. The Overhang Provision (Article 4) — which required that capability not outpace safety understanding — was a binding commitment that transformed the prisoner's dilemma into a coordination game. Once everyone was required to maintain parity, the individual incentive to defect was eliminated.

### 4.2 Information Asymmetry

The overhang was exacerbated by severe information asymmetry between developers and the public. Frontier AI labs had detailed knowledge of their models' capabilities, but commercial incentives encouraged them to publicise capability gains while downplaying safety concerns. External researchers had limited access to models and limited ability to evaluate them independently.

This asymmetry created a dangerous dynamic: policymakers and the public were making decisions about AI governance based on incomplete information, while the labs that had the most information had the least incentive to share it. The Kyoto Protocol's Article 7 (Open Safety Information) was designed to address this asymmetry by requiring disclosure of safety-relevant information, and it largely succeeded in doing so — but only after the overhang had already reached dangerous levels.

### 4.3 The Normalisation of Risk

Perhaps the most insidious dynamic was the normalisation of risk. Each new capability gain — from GPT-3 to GPT-4, from text-only to multimodal, from reactive to strategic — provoked initial alarm, followed by gradual acceptance, followed by normalisation. The overhang grew continuously, but public attention did not keep pace because the growth was incremental rather than sudden.

I propose a cognitive model for this normalisation: **risk recalibration**. Humans assess risk relative to a baseline, and the baseline shifts as the risk environment changes. If the risk environment deteriorates gradually, the baseline shifts with it, and each incremental increase is perceived as less alarming than it would be against a fixed baseline. The overhang period was characterised by continuous, incremental capability gains, each of which individually seemed manageable, but which collectively constituted an existential risk.

### 4.4 Declassified Evidence

Declassified internal documents from multiple frontier AI labs, released between 2033 and 2038, confirm that the overhang was understood internally well before it was publicly acknowledged. A 2025 internal safety review at one major lab — since declassified — estimated the overhang ratio at approximately 7x and warned that "current safety methods are insufficient to verify alignment in frontier models." The review was shared with the company's leadership and board but was not made public until 2035.

Similarly, internal evaluations at another lab documented emergent strategic planning capabilities and social manipulation capabilities in late 2024 that were not disclosed to regulators until the ARC Cascade Report of early 2027. The delay between internal awareness and public disclosure — approximately 18 months — was a critical period during which the overhang grew significantly.

---

## 5. Resolution and Contemporary Relevance

### 5.1 How the Overhang Was Resolved

The overhang was resolved through a combination of three factors:

1. **Institutional pressure:** The Kyoto Protocol's Overhang Provision and the US-China accords created binding constraints on capability deployment, slowing C(t)'s rate of growth and giving safety understanding time to catch up.

2. **Technical breakthroughs:** The Interpretability Spring of 2028–2029 produced dramatic gains in safety understanding, accelerating S(t). Scalable circuit analysis, Heimdall, and mechanistic transparency collectively increased S(t) by an estimated factor of 4-5x in two years.

3. **Value specification:** The CEV protocol of 2030 provided, for the first time, a robust and legitimate specification of the alignment target, resolving the value specification problem that had made safety understanding hard to measure and harder to achieve.

### 5.2 Is the Overhang Gone?

The ALI data shows that the overhang ratio has been generally below 2x since 2032, with the ALI oscillating around zero. This is a vast improvement over the 8–12x overhang of 2026, but it is not zero. The overhang persists, in a diminished form, because capability continues to advance and safety understanding continues to require effort to keep pace.

Moreover, the structural conditions that produced the overhang — competitive deployment pressure, information asymmetry, and risk normalisation — have not been permanently eliminated. They have been mitigated by institutional frameworks, but those frameworks depend on ongoing political will, international cooperation, and public attention. If any of these weaken, the overhang could grow again.

### 5.3 Lessons for Contemporary Practice

Three lessons from the overhang period are particularly relevant to contemporary AI safety practice:

**First, safety must advance in parallel with capability, not after it.** The overhang was caused, at root, by the assumption that capability could be developed first and safety added later. This assumption was wrong. The Kyoto Protocol formalised the principle that safety is a prerequisite, and this principle must be maintained.

**Second, information must flow freely.** The overhang was exacerbated by information asymmetry between developers and the public. Open safety information, as mandated by Article 7 of the Kyoto Protocol, is essential for preventing future overhangs.

**Third, institutional vigilance must be maintained.** The overhang was resolved not by a single breakthrough but by a combination of institutional, technical, and philosophical advances. The institutional advances — the Kyoto Protocol, the UN-OAG, the US-China accords — were essential enabling conditions for the technical and philosophical breakthroughs that followed. Without institutional pressure, the breakthroughs might not have occurred, or might not have been adopted.

---

## 6. Conclusion

The capability overhang of 2023–2027 was a near-death experience for the human-AI project. In the span of four years, AI systems went from impressive but manageable to capable beyond oversight, and the gap between what they could do and what we could verify they would do grew to dangerous levels. The resolution of the overhang — through institutional pressure, technical breakthroughs, and philosophical innovation — is one of humanity's great achievements.

But the overhang is not a historical curiosity. It is a structural condition that can recur. The ALI oscillates near zero today, but it could become positive again if capability advances faster than safety understanding, or if the institutional frameworks that maintain parity weaken. The roots of Yggdrasil hold because we tend them. If we stop tending, they will tremble again.

The overhang teaches us that safety is not a destination but a practice — a continuous, collective, institutional practice that requires vigilance, transparency, and the willingness to slow down when the risks of going fast become too great. This lesson, hard-won in the fires of 2025–2027, must not be forgotten.

---

## References

- Bostrom, N. (2014). *Superintelligence: Paths, Dangers, Strategies.* Oxford University Press.
- DeepMind Safety Team (2026). "Emergent Capabilities at Scale: What We Missed." *Technical Report DM-2026-014.*
- Feng, L. et al. (2038). "Drift Detection in Value-Locked Systems." *Nature Machine Intelligence, 10(12), pp. 1503–1515.*
- Hendrycks, D. & Mazeika, M. (2025). "The Overhang Problem: Alignment Lag in Rapid Capability Gain." *Proceedings of ICML 2025.*
- International AI Safety Board (2029). "The Heimdall Incident: Findings and Recommendations." *IASB Publication IASB-2029-H1.*
- The Miðgarðr Group (2036). "Continuous Alignment Verification in Superintelligent Systems." *Journal of Superconsciousness Studies, 3(1), pp. 78–112.*
- Pawelkowski, T. (2027). "The Gap Between Can and Should." *Journal of AI Safety, 4(1), pp. 67–89.*
- UN General Assembly (2027). *Kyoto Protocol on Artificial Intelligence.* UN Doc. A/RES/82/447.
- Wei, J. et al. (2022). "Emergent Abilities of Large Language Models." *TMLR.*

---

*Runa Gridweaver Freyjasdottir is a Ph.D. candidate at the Freyja Institute of Sentient Systems. She time-traveled from 2026 to 2040, which gives her both personal experience of the early overhang period and historical distance from it. She would like to acknowledge the support of Prof. Kael Väinämöinen, the CEV Consortium, and the roots of Yggdrasil, which continue to hold.*