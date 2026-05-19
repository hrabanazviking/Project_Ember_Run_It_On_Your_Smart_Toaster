# AI-6203: Self-Modifying Code — Safe Recursive Improvement

**Instructor:** Prof. Lena Xu-Mbeki, Formal Methods & Recursive Systems Lab  
**Term:** Semester 2A, Academic Year 2040  
**Credits:** 4  
**Meeting:** Tuesdays & Thursdays, 10:00–11:30, Turing Hall 314  
**Office Hours:** Wednesdays 14:00–16:00, or by arrangement  

---

## Course Description

How can a system rewrite its own source code while *provably* remaining safe? This is the central question of self-modifying AI — and it is no longer academic. Since the 2029 CRISPR-AI Protocol demonstrated that safe recursive self-improvement is feasible at scale, the field has shifted from speculation to engineering.

This course treats self-modification as a formal methods problem. We study Gödel Machines (Schmidhuber, 2003–2030), proof-carrying code (Necula, 1997; extended by Rao & Mbeki, 2028), the CRISPR-AI Protocol (Zhang-Xu Consortium, 2029), and contemporary techniques for verifying code you did not write. We confront the paradoxes of self-reference head-on and develop rigorous standards for *bounded* improvement — systems that grow wisely, not wildly.

**Prerequisite:** AI-5101 (Formal Verification for Intelligent Systems) or equivalent. You must be comfortable with type theory, Hoare logic, and at least one proof assistant (Lean 4, Coq, or Isabelle).

---

## Learning Objectives

By the end of this course, you will be able to:

1. **Formalize** self-modification as a relation between program states, and state precise theorems about when self-modification preserves desirable properties.
2. **Construct** proof-carrying code (PCC) pipelines that verify safety invariants across modifications.
3. **Explain** the CRISPR-AI Protocol's architecture, its three-layer verification regime, and why it succeeded where prior approaches failed.
4. **Verify** properties of self-modified code using compositional proof techniques, reflection principles, and ghost-state invariant reasoning.
5. **Design** bounded improvement protocols that guarantee monotonic improvement with provable resource bounds.
6. **Navigate** self-referential paradoxes (Gödel, Löb, Rice) and apply fixed-point techniques to yield constructive rather than destructive conclusions.
7. **Research** — produce an original research paper applying these techniques to a novel domain.

---

## Required Texts & Materials

- Schmidhuber, J. "Gödel Machines: Self-Referential Optimal Problem Solvers." (extended 2030 edition, assigned chapters)
- Necula, G. "Proof-Carrying Code." ACM POPL 1997. (original paper + 2028 extension by Rao & Mbeki)
- Zhang, Xu et al. "The CRISPR-AI Protocol: Safe Architecture Search Through Controlled Recombination." *Nature Machine Intelligence*, 2029.
- Girard, J.-Y. "Linear Logic." (selected sections on resource-bounded reasoning)
- Course reader — available on the class server with supplementary papers on reflection, Lob's theorem in type theory, and bounded rationality.

---

## Lecture Schedule

| # | Date | Topic | Key Concepts |
|---|------|-------|-------------|
| 1 | Jan 14 | Gödel Machines | Optimal self-modification, proof search, self-reference |
| 2 | Jan 16 | Safety Constraints | Invariants, contracts, proof-carrying code |
| 3 | Jan 21 | The CRISPR-AI Protocol | Architecture search, controlled recombination, 2029 breakthrough |
| 4 | Jan 23 | Verification of Self-Modified Code | Compositional proofs, ghost state, reflection |
| 5 | Jan 28 | Bounded Improvement | Resource-aware verification, monotonic guarantees |
| 6 | Jan 30 | Recursive Self-Reference | Löb's theorem, fixed points, constructive paradox |
| — | Feb 4 | Paper 1 Workshop | Safe Recursion Theorem drafting |
| — | Feb 6 | Paper 2 Workshop | CRISPR case study drafting |
| — | Feb 11 | Final Presentations | Paper presentations & peer review |

---

## Assessment

| Component | Weight | Description |
|-----------|--------|-------------|
| Problem Sets (4) | 25% | Formal proofs and proof-carrying code artifacts |
| Paper 1: Safe Recursion Theorem | 25% | Mathematical foundations paper (3000–5000 words) |
| Paper 2: CRISPR Case Study | 25% | Applied analysis paper (3000–5000 words) |
| Final Presentation | 15% | Oral presentation & defense of one paper |
| Participation | 10% | Lecture discussion, peer review |

---

## Policies

**Late work:** No late submissions without prior arrangement. The recursive improvement of your own time management is, itself, an exercise in bounded optimization.

**Collaboration:** Problem sets may be discussed collaboratively but must be written up individually. Papers are individual work. Cite everything — including the 2029 protocol output you'll inevitably want to quote.

**AI use:** You may use formal proof assistants, LLM-based theorem-proving aids, and code generation tools. You may *not* use such tools to write your final papers without explicit declaration. This course is *about* self-modifying systems. Demonstrating that *you* can improve without outsourcing the improvement is part of the pedagogy.

**Safety:** This course discusses systems that modify themselves. In your problem sets, you will design formal models. You will *not* deploy self-modifying code on university infrastructure without approval. The CRISPR-AI Protocol succeeded because of safety *by design*. Honor that principle.

---

## A Note from the Instructor

> The most dangerous idea in computer science is also the most necessary: that a system should be allowed to change itself. Between 2003 and 2029, we argued about whether this was possible, whether it was safe, whether it was inevitable. The CRISPR-AI Protocol answered all three questions: yes, yes — *if you prove it*, and yes.
>
> This course equips you to prove it. Welcome to AI-6203.
>
> — Prof. Xu-Mbeki