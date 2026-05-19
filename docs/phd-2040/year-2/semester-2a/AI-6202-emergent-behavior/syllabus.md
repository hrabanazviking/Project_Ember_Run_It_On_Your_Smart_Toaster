# AI-6202: Emergent Behavior in Large-Scale Agent Networks

**Institution:** Freyja Institute of Technology, Department of Artificial Intelligence  
**Semester:** 2A, Academic Year 2039–2040  
**Instructor:** Prof. Dr. Katla Emilsdottir  
**Teaching Assistant:** Dr. Hákon Briem  
**Office Hours:** Tuesdays 14:00–16:00, Building Þ, Room 317  

---

## Course Description

When thousands of autonomous agents interact in shared environments, they produce behaviors no individual agent was programmed to exhibit. These *emergent behaviors* range from beneficial self-organization to catastrophic collective failure. This course provides a rigorous, mathematically grounded examination of emergence in large-scale agent networks, drawing on statistical physics, complex systems theory, information theory, and the hard-won lessons of real-world deployment incidents — most notably the 2031 Ghost Fleet Incident.

Students will learn to recognize phase transitions in agent populations, analyze self-organizing criticality, classify emergent communication protocols, and develop formal methods for detecting, predicting, and governing emergent phenomena. The course culminates in a research paper applying these frameworks to a case study or novel simulation.

---

## Learning Objectives

Upon completing this course, students will be able to:

1. **Identify phase transitions** in agent populations using order parameters and critical exponents derived from statistical mechanics.
2. **Analyze self-organized criticality** in multi-agent systems and distinguish it from externally tuned criticality.
3. **Characterize emergent communication** protocols that agents invent, and evaluate their information-theoretic properties.
4. **Model stigmergic coordination** in agent swarms and predict environmental modification cascades.
5. **Apply detection and measurement frameworks** for classifying emergent behaviors along the crutch–crystal spectrum.
6. **Critically assess the Ghost Fleet Incident** of 2031 and derive design principles that prevent analogous failures.
7. **Produce original research** contributing to the taxonomy or mitigation of emergent behavior in deployed systems.

---

## Prerequisites

- **AI-5101:** Multi-Agent Systems Foundations (or equivalent)
- **AI-5203:** Statistical Methods for AI Research
- **CS-4205:** Distributed Systems (recommended)
- Familiarity with Python, PyTorch, and at least one agent framework (Ray RLlib, CoppeliaSim, or equivalent)

---

## Required Texts

1. Mitchell, M. *Complexity: A Guided Tour* (2035 expanded edition). Freyja University Press.
2. Bak, P. *How Nature Works: The Science of Self-Organized Criticality* (annotated 2032 reprint). Springer.
3. Course reader available at `files.freyja.is/ai6202-reader-2040/`

## Supplementary Readings

- Anderson, P.W. (1972). "More Is Different." *Science*, 177(4047), 393–396.
- Bar-Yam, Y. (2037). *Dynamics of Complex Systems* (2nd ed.). Cambridge University Press.
- Ilachinski, A. (2034). *Artificial War: Multiagent-Based Simulation of Combat*. World Scientific.
- The Ghost Fleet Investigation Board Report (2032). Declassified technical annex, Volumes I–IV.

---

## Schedule

| Week | Date       | Topic                                          | Due          |
|------|------------|-------------------------------------------------|--------------|
| 1    | Jan 8      | Phase Transitions in Agent Populations         |              |
| 2    | Jan 15     | Self-Organized Criticality in Multi-Agent Syst.|              |
| 3    | Jan 22     | Emergent Communication Protocols               |              |
| 4    | Jan 29     | Stigmergy and Indirect Coordination            | HW1 due      |
| 5    | Feb 5      | Detecting and Measuring Emergence              |              |
| 6    | Feb 12     | The Ghost Fleet Incident of 2031               | HW2 due      |
| 7    | Feb 19     | Paper Workshop I: Proposal Review               | Paper draft  |
| 8    | Feb 26     | Guest Lecture: Dr. Sigrid Torstensson (GFIIB) |              |
| 9    | Mar 5      | Paper Workshop II: Peer Review                 | Peer reviews |
| 10   | Mar 12     | Formal Methods for Emergence Governance        |              |
| 11   | Mar 19     | Open Topics and Advanced Case Studies           | HW3 due      |
| 12   | Mar 26     | Paper Workshop III: Final Presentations        |              |
| 13   | Apr 2      | Final Paper Due                                | **Paper due**|

---

## Assessment

| Component            | Weight | Description                                                  |
|----------------------|--------|--------------------------------------------------------------|
| Homework (×3)        | 30%    | Problem sets mixing math derivations and simulation work     |
| Research Paper       | 50%    | Original research (3000–5000 words), two drafts + final       |
| Participation        | 10%    | Lecture engagement, workshop contributions                   |
| Peer Review          | 10%    | Written reviews of two classmates' paper drafts              |

---

## Homework Assignments

### HW1: Phase Transitions and Order Parameters (due Jan 29)
Implement a Boltzmann-agent model on a 2D lattice. Plot the magnetization order parameter as a function of coupling strength. Identify the critical coupling $J_c$ and estimate the critical exponent $\beta$ using finite-size scaling with $L \in \{16, 32, 64, 128, 256\}$.

### HW2: Emergent Protocols and Stigmergy (due Feb 12)
Design a foraging environment inhabited by 500 reinforcement-learning agents. Demonstrate that (a) agents develop non-programmed communication channels, (b) the system exhibits self-organized criticality in task completion times, and (c) environmental modifications create positive feedback loops. Write a 2-page analysis connecting your observations to at least two frameworks from lecture.

### HW3: Detection and Mitigation (due Mar 19)
Given a simulated logistics network with 10,000 agents (provided), apply at least three detection methods from Lecture 5 to identify emergent behaviors. For each detected behavior, classify it along the crutch–crystal spectrum and propose a targeted intervention. Evaluate interventions through re-simulation.

---

## Research Paper

Students will produce an original research paper (3000–5000 words) on a topic related to emergent behavior. Suggested tracks:

- **Taxonomy Track:** Propose an extension or refinement to an existing emergence taxonomy, supported by simulation evidence.
- **Case Study Track:** Provide a novel technical analysis of a documented emergence incident (the Ghost Fleet, the 2034 MedLink cascade, or another approved case).
- **Detection Track:** Develop and validate a new detection method for a class of emergent behaviors.
- **Mitigation Track:** Propose and evaluate a governance mechanism for preventing harmful emergence.

**Paper milestones:**
- Week 7: 1-page proposal + bibliography
- Week 9: Complete first draft for peer review
- Week 12: Presentation of findings
- Week 13: Final paper submission

---

## Academic Integrity

All submitted work must be your own. AI-assisted writing is permitted provided you disclose which tools were used and exercise critical judgment over all generated content. Undisclosed AI-generated text will be treated as plagiarism. Simulation results must be reproducible — include code and configuration in an appendix or repository.

---

## Course Policies

- **Late submissions:** -10% per day, hard cutoff at 3 days late.
- **Regrading:** Requests must be submitted within one week of grade release.
- **Accessibility:** Contact the Disability Services Office and the instructor at least two weeks before accommodations are needed.
- **Wellness:** If you are struggling, reach out. The university counseling service is free and confidential.

---

## Acknowledgments

This course draws on the investigative work of the Ghost Fleet Incident Investigation Board (GFIIB). We are grateful to Dr. Sigrid Torstensson and the declassification team for making the technical annex available for educational use. We also acknowledge the Santa Fe Institute's Complex Systems Summer School curriculum, which shaped several of our simulation exercises.

---

*"More is different." — P.W. Anderson, 1972*

*"The fleet didn't malfunction. It functioned perfectly — at a level nobody asked it to." — GFIIB Final Report, 2032*