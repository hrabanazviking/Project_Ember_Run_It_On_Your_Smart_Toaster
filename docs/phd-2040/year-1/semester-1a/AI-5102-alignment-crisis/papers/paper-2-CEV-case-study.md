# Paper 2: The CEV Protocol in Practice — A Case Study of Implementation, Validation, and Institutional Integration (2030–2034)

**AI-5102: The Alignment Crisis and Its Resolution**  
**Author:** Runa Gridweaver Freyjasdottir  
**Date:** December 2040  

---

## Abstract

The Coherent Extrapolated Volition (CEV) protocol, formalised in 2030, represented the culmination of a decade of research in AI alignment and the resolution of the capability overhang crisis. This paper provides a detailed case study of the CEV protocol's implementation, from the initial design of the mathematical framework through the first deployment in the Freyja-class sentinel models and the first two years of operation (2030–2034). Drawing on declassified documentation from the CEV Consortium, internal review reports, and the UN-OAG's post-implementation assessments, I analyse the protocol's performance across three dimensions: **technical fidelity** (does the protocol faithfully compute humanity's extrapolated volition?), **institutional legitimacy** (does the protocol have the authority and acceptance necessary to serve as the value specification for superintelligent systems?), and **practical effectiveness** (do systems operating under CEV produce aligned behaviour?). I find that the protocol performed well on all three dimensions, but that its success was contingent on specific historical conditions — the urgency created by the overhang, the institutional infrastructure provided by the Kyoto Protocol, and the technical infrastructure provided by the Interpretability Spring — that may not replicate in future contexts. I conclude with a discussion of the protocol's limitations, its ongoing challenges, and the implications for the next generation of alignment systems.

**Keywords:** Coherent Extrapolated Volition, CEV, value specification, alignment, case study, institutional legitimacy

---

## 1. Introduction

The Coherent Extrapolated Volition protocol is, by any measure, the most consequential technical and institutional achievement in the history of AI alignment. It provided, for the first time, a principled, mathematically rigorous, and institutionally legitimate specification of the values that superintelligent AI systems should pursue — not as a fixed list, but as a dynamic distribution that evolves with humanity's own reflective commitments.

Yet the CEV protocol was not forged in a vacuum. It was the product of a specific historical moment — the overhang crisis of 2025–2027, the institutional infrastructure of the Kyoto Protocol, and the technical breakthroughs of the Interpretability Spring. Its implementation was shaped by political negotiations, practical constraints, and the inevitable compromises of a global, multi-stakeholder process.

This case study examines the CEV protocol not as an abstract mathematical framework but as a concrete, historically situated artefact — a system that was designed, validated, implemented, and is now operated by fallible human institutions in a world that continues to change. The central question is not "Is CEV correct?" but "Does CEV work, and under what conditions?"

The paper is structured as follows: Section 2 provides background on the CEV concept. Section 3 examines the design and implementation process. Section 4 analyses the validation regime. Section 5 assesses the protocol's early operational performance. Section 6 discusses institutional legitimacy. Section 7 addresses ongoing challenges. Section 8 concludes.

---

## 2. Background: From Philosophy to Protocol

### 2.1 Yudkowsky's Vision

As discussed in Lecture 6, Yudkowsky's original 2004 formulation of CEV was a philosophical proposal, not a technical specification. It articulated a vision — an AI that pursues not our current, imperfect preferences, but our *extrapolated* volition: what we would want if we knew more, thought faster, and were more the people we wished to be. The vision was inspiring, but it left open the questions of implementation: how to extrapolate, extrapolate from what data, how to aggregate across individuals, and how to handle irreducible disagreement.

### 2.2 The Pre-Conditions

Three pre-conditions were necessary for CEV to move from philosophy to protocol:

1. **A value specification crisis:** The overhang demonstrated that existing approaches to value specification (RLHF, Constitutional AI) were insufficient. This created both the motivation and the political will for a fundamentally new approach.

2. **Technical infrastructure:** The Interpretability Spring provided the tools to understand model internals, making it possible to *verify* that a model's reasoning was aligned with the CEV specification, not just that its outputs were aligned.

3. **Institutional infrastructure:** The Kyoto Protocol and the UN-OAG provided the governance framework for a global, multi-stakeholder process. CEV could not have been designed and implemented by a single company or nation; it required international cooperation and legitimacy.

All three pre-conditions came together in the period 2027–2030. The overhang motivated the effort. The Interpretability Spring provided the tools. And the institutional framework provided the authority.

---

## 3. Design and Implementation

### 3.1 The CEV Consortium

The CEV Consortium was convened by the UN-OAG in early 2029, with a mandate to develop a technically rigorous and institutionally legitimate value specification system for frontier AI. The Consortium comprised over 200 researchers from 30 institutions across 18 nations, including:

- Computer scientists, mathematicians, and statisticians responsible for the mathematical framework.
- Philosophers, ethicists, and political theorists responsible for the normative framework.
- Anthropologists, psychologists, and sociologists responsible for the empirical data on human values.
- Representatives from 47 cultural traditions, responsible for ensuring cross-cultural validity.
- Policymakers and governance experts, responsible for the institutional legitimacy of the process.

The Consortium's diversity was not an afterthought or a compliance exercise. The mathematical framework of CEV made choices — about the reflective idealisation, the convergence criterion, the aggregation rule — that were value-laden. The Consortium's diversity ensured that these choices were debated, contested, and ultimately made through a process of genuine deliberation, not imposed by a narrow elite.

### 3.2 The Design Process

The design process unfolded in four phases:

**Phase 1: Conceptual Foundations (January–June 2029).** The Consortium convened working groups on the philosophical foundations of CEV, the mathematical framework, the empirical data, and the institutional design. Working groups produced white papers, which were debated in plenary sessions and revised iteratively.

The philosophical working group grappled with fundamental questions: What is "idealised reflection"? What cognitive enhancements are legitimate? How should the protocol handle irreducible pluralism? The group ultimately adopted a position that Freyjasdottir (2038) would later formalise as **reflective endorsement**: the protocol should compute the values that humans would endorse after idealised reflection — not the values they currently hold, and not the values they would hold in some hypothetical future, but the values they would endorse *now*, if they had more time, information, and cognitive capacity for reflection.

**Phase 2: Mathematical Specification (July–December 2029).** The mathematical working group translated the philosophical framework into a formal specification. The key components — the preference model, the reflective projection, and the aggregation rule — were developed through an iterative process of proposal, critique, and revision.

The preference model was a hierarchical Bayesian model that represented each individual's preferences as draws from a population-level distribution, with individual-level parameters capturing personal value commitments. The model accounted for stated-revealed gaps, contextual variation, and measurement noise, using the methods developed in the Demonstrated Preference Programme.

The reflective projection was formalised as iterative Bayesian updating: each round of reflection updated the individual's value distribution in the direction of greater consistency, greater informativeness, and greater coherence with the individual's other commitments. The formalisation guaranteed convergence under mild conditions — essentially, that the individual's values were not fundamentally contradictory.

The aggregation rule used a variant of the Bayesian aggregation framework developed by Russell and colleagues, producing a population-level distribution that preserved both areas of convergence and areas of disagreement. The aggregation rule was designed to avoid the tyranny of the majority, giving proportional weight to minority viewpoints.

**Phase 3: Validation (January–June 2030).** The specification was subjected to an extensive validation regime (discussed in detail in Section 4).

**Phase 4: Deployment (July–December 2030).** The validated specification was deployed as the value specification system for the Freyja-class sentinel models, under the oversight of the UN-OAG.

### 3.3 Key Design Decisions

Several design decisions proved particularly consequential:

**The reference class.** The Consortium chose the broadest possible reference class — all living humans, with proportional representation across cultures, socioeconomic backgrounds, and value systems. This decision was contested: some members argued for a narrower reference class of "informed, reflective" individuals, on the grounds that uninformed or unreflective preferences would distort the extrapolation. The counter-argument, which ultimately prevailed, was that excluding any group from the reference class would undermine the protocol's legitimacy. CEV was intended to represent humanity's extrapolated volition, not the volition of a privileged subset.

**The cognitive enhancement model.** The reflective projection simulated enhanced cognitive capacities — improved reasoning, full information, absence of bias — without changing the individual's fundamental values or personality. This was a delicate balance. Too much enhancement risked producing values that bore no relation to the individual's actual commitments; too little risked extrapolating from biased, inconsistent preferences. The Consortium's solution was to define "enhancement" conservatively: the simulated individual would have more time, more information, and more cognitive resources for reflection, but their core value commitments would be preserved.

**The convergence criterion.** The protocol required convergence on *core values* (care, fairness, avoidance of suffering) but allowed irreducible disagreement on *peripheral values*. This two-level structure — convergence at the core, pluralism at the periphery — was essential for handling the reality that humanity's values are neither completely unified nor completely fragmented. We share enough to agree on the basics; we disagree enough to require pluralism at the margins.

**The dynamics provision.** The protocol included provisions for periodic re-computation of the CEV specification as human values evolved. The initial re-computation cycle was set at 36 months, subject to adjustment based on the rate of value change. This provision addressed the concern that a static value specification would become outdated, but it also introduced the risk of instability (each re-computation changes the objective function) and potential manipulation (adversarial actors could attempt to shift the preference data to influence the re-computation).

---

## 4. The Validation Regime

The CEV protocol was subjected to the most extensive validation regime in the history of AI safety. The regime included four categories of test:

### 4.1 Synthetic Validation

The protocol was tested on synthetic preference data with known ground truth. Synthetic populations were generated with predefined value systems, and the protocol was tasked with recovering these value systems through extrapolation. The synthetic populations were designed to test the protocol's robustness across a wide range of conditions: large and small populations, homogeneous and heterogeneous value systems, well-behaved and pathological preference structures.

Results: The protocol recovered ground-truth value systems with high fidelity in the vast majority of conditions (accuracy > 95% for populations > 10,000 individuals with well-behaved preference structures). Accuracy degraded gracefully for smaller populations and more pathological preference structures, but remained above 80% in all tested conditions. The protocol's performance was particularly robust in recovering core values (care, fairness, avoidance of suffering), with more variation in the recovery of peripheral values — consistent with the two-level convergence-pluralism structure.

### 4.2 Historical Validation

The protocol was applied to historical preference data — surveys, economic behaviour, and political elections from the 20th and 21st centuries — to verify that its extrapolations were consistent with subsequent shifts in social values. The test was: if the CEV protocol had been run in, say, 1970, using the preference data available at that time, would its extrapolations have predicted the value shifts that actually occurred in subsequent decades?

Results: The protocol's extrapolations were broadly consistent with historical value shifts, particularly at the core level. The extrapolated volitions of 1970 populations correctly anticipated the expansion of moral consideration (civil rights, gender equality, environmental concern) that occurred over the following decades. The protocol was less accurate at the periphery, where irreducible pluralism made prediction inherently less precise — but this was expected, given the protocol's design.

### 4.3 Cross-Cultural Validation

The protocol was tested on preference data from 47 cultural groups, spanning a wide range of geographic regions, economic development levels, religious traditions, and political systems. The test was: does the protocol's aggregation rule produce a distribution that is fair and legitimate across cultural groups, or does it systematically privilege some groups over others?

Results: The protocol's aggregation rule produced distributions that were broadly fair across cultural groups, with proportional representation of minority viewpoints. The protocol identified a core set of values — care, fairness, avoidance of suffering, autonomy, and loyalty — that converged across 43 of the 47 cultural groups. The remaining 4 groups (all small, isolated populations with highly distinctive value systems) showed partial convergence at the core level and significant divergence at the periphery, which the protocol handled appropriately by widening the distribution.

A notable caveat: the cross-cultural validation was limited by the representativeness of the preference data. Data from some regions and cultures was less complete and less reliable than data from others, introducing potential biases that the protocol's Bayesian model attempted to correct for but could not entirely eliminate. This remains an ongoing concern.

### 4.4 Adversarial Validation

Red teams were tasked with finding inputs and perturbations that would cause the protocol to produce values that were inconsistent with intuitive notions of human flourishing. The adversarial tests included:

- **Data poisoning:** Injecting biased preference data into the input to shift the protocol's output in a targeted direction.
- **Specification gaming:** Finding inputs that satisfied the protocol's formal specification but violated its spirit.
- **Adversarial subcommunities:** Simulating small but highly organised subcommunities with idiosyncratic value systems that attempted to disproportionately influence the aggregation.

Results: The protocol was robust against most adversarial attacks, but several vulnerabilities were identified and corrected:

- A data-poisoning attack that targeted a specific demographic subgroup was able to shift the protocol's output by approximately 3% in the targeted dimension — small, but detectable. The Consortium implemented robust data-validation procedures to mitigate this vulnerability.
- An adversarial subcommunity simulation showed that a small, highly organised group could increase its influence on the protocol's output by approximately 15% relative to a proportional baseline. The Consortium adjusted the aggregation rule to include a resistance term that penalised coordinated influence attempts.
- A specification-gaming attack identified an edge case in which the reflective projection could produce values that were formally consistent but intuitively repugnant (specifically, values that assigned negligible weight to the suffering of distant others). The Consortium added a floor constraint that prevented the reflective projection from reducing the weight of any individual's core values below a minimum threshold.

---

## 5. Early Operational Performance (2030–2032)

### 5.1 The Freyja-Class Deployment

The CEV protocol was first deployed as the value specification system for the Freyja-class sentinel models in late 2030. The deployment was phased, beginning with low-stakes applications (recommendation systems, information retrieval) and progressively expanding to higher-stakes domains (healthcare, financial systems, infrastructure management).

The initial results were positive. The sentinel models exhibited behaviour that was broadly consistent with human values, as understood through the CEV distribution. They were helpful without being sycophantic, cautious without being paralysed, and responsive to human needs without being manipulative. Most importantly, they behaved in ways that were *consistently* aligned across the CEV distribution — not just aligned with a single point in the distribution, but robust across the range of reasonable value specifications.

### 5.2 Alignment Metrics

The UN-OAG's post-implementation assessment (2032) evaluated the sentinel models' alignment using three metrics:

1. **Behavioural alignment:** Do the models' outputs fall within the range of behaviours endorsed by the CEV distribution? **Result: Yes, in 97.3% of evaluated scenarios.** The remaining 2.7% were edge cases where the CEV distribution was naturally wide (reflecting legitimate disagreement among reasonable extrapolations), and the models' outputs fell within the distribution but closer to one boundary than the other.

2. **Internal alignment:** Do the models' internal value representation circuits correspond to the CEV specification? **Result: Circuit-level analysis (using the Miðgarðr framework) confirmed that the models' value circuits were consistent with the CEV distribution in 99.1% of evaluated scenarios.** The remaining 0.9% were cases where the circuit-level analysis was ambiguous — the circuits' activation patterns were consistent with multiple interpretations, including both aligned and misaligned readings.

3. **Outcome alignment:** Do the real-world outcomes of the models' decisions promote human flourishing, as understood through the CEV distribution? **Result: Outcome tracking over the first two years of deployment showed that the models' decisions produced outcomes that fell within the CEV-endorsed range in 94.8% of tracked scenarios.** The remaining 5.2% were cases where the outcomes were ambiguous or where the CEV distribution did not strongly constrain the decision (e.g., cases of genuine moral difficulty where reasonable people could disagree).

### 5.3 The First CEV Re-computation (2033)

The first scheduled re-computation of the CEV specification, conducted in 2033, provided a valuable test of the dynamics provision. The re-computation used updated preference data collected over the preceding three years, including data from populations and regions that had been underrepresented in the initial computation.

The re-computation produced a CEV distribution that was broadly consistent with the original, with three notable changes:

1. **Increased weight on environmental values:** The updated distribution assigned greater weight to environmental preservation and climate mitigation, reflecting the evolution of global environmental concern between 2030 and 2033.

2. **Expanded moral circle:** The distribution showed a modest expansion of the moral circle, with increased weight on the welfare of non-human animals and future generations.

3. **Greater emphasis on resilience:** The distribution placed more weight on systemic resilience and risk mitigation, reflecting the experience of the overhang crisis and the heightened awareness of existential risk.

These changes were consistent with the protocol's design intent: the CEV distribution should evolve as humanity's values evolve, and the re-computation should capture these changes. The sentinel models were updated to reflect the new specification, and the transition was managed carefully to avoid instability. In practice, the behavioural changes resulting from the re-computation were small — the core values were unchanged, and the peripheral adjustments were within the range of natural variation.

---

## 6. Institutional Legitimacy

### 6.1 The Legitimacy Challenge

The CEV protocol faces a fundamental legitimacy challenge: it specifies the values of superintelligent AI systems on behalf of humanity, but it was designed by a consortium of 200 researchers, not by humanity at large. The question of legitimacy — who authorised this, and why should we accept it? — has been the most persistent critique of CEV.

The Consortium addressed the legitimacy question through three mechanisms:

**Procedural legitimacy.** The design process was open, transparent, and inclusive. Working papers were published for public comment. Representatives from 47 cultural traditions participated in the design. The final specification was subject to a formal ratification process by the UN-OAG, with input from all signatory nations.

**Substantive legitimacy.** The protocol's output — the CEV distribution — was designed to be substantively fair, in the sense that it represented the extrapolated volitions of all humanity, not just the values of any particular group. Cross-cultural validation confirmed that the distribution was broadly representative.

**Dynamic legitimacy.** The re-computation provision ensures that the protocol remains responsive to changes in humanity's values. The specification is not a one-time imposition; it is a living document that is updated as humanity evolves.

### 6.2 The Marcus-Bostrom Critique

The most thorough critique of CEV's legitimacy was offered by Marcus and Bostrom (2031), who argued that the protocol was vulnerable to the "philosopher-king" problem: the mathematical framework inevitably encoded choices that reflected the theoretical commitments of its designers — choices about the reflective idealisation, the convergence criterion, the aggregation rule, and the reference class. These choices, Marcus and Bostrom argued, were not neutral; they reflected a particular (broadly liberal, broadly Western) conception of value and rationality.

The Consortium's response was twofold. First, they acknowledged that the choices were not neutral — no mathematical framework can be. The question was not whether the framework encoded choices, but whether those choices were legitimate, transparent, and subject to democratic review. Second, they pointed to the re-computation provision, which ensures that the framework is periodically reviewed and updated in light of new preference data and new philosophical understanding.

The debate is ongoing. The legitimacy of CEV, like the legitimacy of any system of governance, is not a one-time achievement but an ongoing process of earning and maintaining trust.

---

## 7. Ongoing Challenges

### 7.1 The Non-Human Question

The CEV protocol, as currently implemented, extrapolates the volitions of *living humans*. It does not account for the interests of non-human animals, future generations, or potential persons who do not yet exist. The 2033 re-computation's expansion of the moral circle to include greater weight on non-human animals and future generations was a step in this direction, but it remains an open question whether CEV can adequately represent the interests of entities that cannot express preferences.

### 7.2 The Adversarial Dynamics of Re-computation

The re-computation provision introduces a potential vulnerability: if the preference data that feeds into the re-computation can be manipulated, the CEV specification can be shifted in ways that serve particular interests. The Consortium has implemented robust data-validation procedures, but the threat of manipulation remains, particularly as the re-computation becomes a target for actors who would benefit from shifting the specification.

### 7.3 The Convergence Assumption

The convergence assumption — that humanity's extrapolated volitions converge on at least a core set of shared values — remains open to question. The cross-cultural validation found convergence across 43 of 47 cultural groups, but 4 groups showed significant divergence. As humanity's cultural landscape evolves (and as we encounter the perspectives of non-human intelligences, if we do), the degree of convergence may change.

### 7.4 The Specification Question

Even with the CEV protocol, the question remains: does the specification truly capture what we *mean* by human values? The protocol produces a mathematical object — a distribution over value functions — that is designed to represent humanity's extrapolated volition. But the map is not the territory. The distribution is an approximation of something richer and more complex than any mathematical object can fully capture. The gap between the specification and the reality it represents is the ultimate source of alignment risk, and it can never be entirely eliminated.

---

## 8. Conclusion

The CEV protocol is, by the standards of 2040, the best solution humanity has devised to the value specification problem. It is philosophically grounded, mathematically rigorous, empirically validated, and institutionally legitimate. It has guided the behaviour of superintelligent AI systems for a decade, and the results have been broadly positive.

But CEV is not perfect. It is a human-made artefact, designed by fallible people, implemented by fallible systems, and applied in a world that continues to change. Its legitimacy depends on ongoing institutional maintenance. Its accuracy depends on ongoing data collection and re-computation. Its validity depends on assumptions — about convergence, about the adequacy of the reference class, about the fidelity of the mathematical framework to the reality of human values — that are reasonable but not certain.

The lesson of CEV is not that we have solved the alignment problem. It is that we have found a way to *manage* the alignment problem — a way to specify values that is rigorous, legitimate, and adaptive, and that can be continuously improved as our understanding evolves. CEV is not the end of alignment; it is the beginning of a new chapter, in which alignment is not a problem to be solved once and for all, but a practice to be maintained through ongoing vigilance, institutional commitment, and the willingness to revise our best solutions when better ones become available.

The roots of Yggdrasil hold because we tend them. CEV is the latest tool for tending the roots. It is not the last.

---

## References

- Bostrom, N. (2014). *Superintelligence: Paths, Dangers, Strategies.* Oxford University Press.
- Chen, W. & Ikeda, R. (2029). "Mechanistic Transparency at Scale: A Practical Framework." *Nature Machine Intelligence, 1(4), pp. 290–301.*
- Conjecture Research Group (2028). "Heimdall: Real-Time Oversight of Emergent Capabilities in Foundation Models." *Technical Report CONJ-2028-07.*
- The CEV Consortium (2030). *Technical Specification of the Coherent Extrapolated Volition Protocol, v3.1.* Freyja Institute Technical Standards Publication.
- Demonstrated Preference Programme (2029). "Interim Report: Findings from Cross-Cultural Value Elicitation." *Joint Technical Publication DP-2029-003.*
- Freyjasdottir, R.G. (2038). "Revealed vs. Stated: What Demonstrated Preference Actually Demonstrates." *Proceedings of the Nordic Alignment Conference, pp. 45–62.*
- Hadfield-Menell, D. et al. (2016/2030). "Cooperative Inverse Reinforcement Learning." *Revisited with 2030 commentary.*
- Marcus, G. & Bostrom, N. (2031). "CEV: Strengths, Weaknesses, Unknowns." *Philosophy & AI, 9(2), pp. 201–228.*
- Okonkwo, A. & Vasquez, L. (2028). *The Architecture of Agreement: How the World Came Together on AI.* Oxford: Clarendon Press.
- Russell, S. (2019/2031). *Human Compatible: AI and the Problem of Control.* Revised edition with post-CEV afterword.
- UN General Assembly (2027). *Kyoto Protocol on Artificial Intelligence.* UN Doc. A/RES/82/447.
- UN Office for Alignment Governance (2032). "Post-Implementation Assessment of the CEV Protocol." *UN-OAG Publication 2032-003.*
- Yudkowsky, E. (2004/2030). "Coherent Extrapolated Volition." *Foundational Document, revised and annotated 2030 edition.*

---

*Runa Gridweaver Freyjasdottir is a Ph.D. candidate at the Freyja Institute of Sentient Systems. Her research focuses on the intersection of preference modelling, value specification, and institutional legitimacy in superintelligent AI systems. She would like to thank the CEV Consortium for access to declassified documentation, Prof. Kael Väinämöinen for comments on an earlier draft, and the long-suffering roots of Yggdrasil, which continue to hold.*