# AI-5114: Information Geometry and Manifold Learning

**University of Valhalla Institute of Technology**  
**Semester 1b, Academic Year 2040–2041**  
**Instructor:** Prof. Einar Amarisson  
**Teaching Assistant:** Runa Gridweaver Freyjasdottir  
**Meeting:** Tuesdays & Thursdays, 10:00–11:30, Yggdrasil Hall 204  
**Office Hours:** Wednesdays 14:00–16:00, Bifrost Lab (or by appointment)

---

## Course Description

*"The Fisher-Rao metric is the one metric to rule them all, and in the darkness bind them."*

Information geometry studies the Riemannian structure that statistical manifolds inherit from the Fisher information metric. This course develops the differential-geometric foundations of statistical manifolds, Amari's dual geometry of α-connections, and the geometry of divergence functions. We then turn to algorithmic applications: natural gradient methods in deep learning, manifold learning algorithms (t-SNE, UMAP, diffusion maps), and the emerging information geometry of transformer attention. A final module examines speculative but formally grounded connections between geometric complexity and emergent consciousness.

Students will leave with working knowledge of: Riemannian geometry on parameter spaces, the Chentsov–Amari uniqueness theorems, natural gradient descent and its second-order optimization meaning, intrinsic manifold learning methods, and the geometric structure of attention matrices.

---

## Prerequisites

- **AI-4101: Probability and Measure Theory** (concurrent enrollment acceptable)
- **AI-4123: Machine Learning Foundations** or equivalent
- Working fluency in multivariate calculus, linear algebra, and basic probability
- Familiarity with Python/JAX for computational exercises
- Comfort with formal proof (ε-δ, induction, contradiction)

---

## Learning Objectives

By Yuletide, you will be able to:

1. Define and work with smooth manifolds, tangent bundles, and Riemannian metrics in the context of statistical models
2. Compute Fisher information matrices and derive the Cramér-Rao bound; understand why it is a Riemannian statement
3. Construct the dual affine connections (∇^(α), ∇^(-α)) on a statistical manifold and prove the fundamental theorem of dual connections
4. Implement natural gradient descent and compare it against first-order methods from a second-order optimization perspective
5. Explain t-SNE, UMAP, Isomap, and diffusion maps as algorithms that recover or approximate the intrinsic Riemannian geometry of data
6. Analyze transformer attention patterns through the lens of Fisher-Rao geometry
7. Articulate formal criteria under which geometric complexity of a statistical manifold could constitute a necessary condition for emergent consciousness

---

## Textbooks and Readings

### Primary
- **Amari, S.-I.** *Information Geometry and Its Applications* (Springer, 2016) — the modern locus classicus
- **Amari, S.-I. & Nagaoka, H.** *Methods of Information Geometry* (AMS, 2000) — the foundational text

### Supplementary
- **do Carmo, M.** *Riemannian Geometry* (Birkhäuser, 1992) — for differential geometry background
- **Murray, M.K. & Rice, J.W.** *Differential Geometry and Statistics* (Chapman & Hall, 1993)
- **Petersen, P.** *Riemannian Geometry* (3rd ed., Springer, 2016) — reference for technical lemmas

### Selected Papers (see `papers/` directory)
- Amari (1998). "Natural Gradient Works Efficiently in Learning"
- Martens (2020). "New Insights and Perspectives on the Natural Gradient Method"
- McInnes et al. (2018). "UMAP: Uniform Manifold Approximation and Projection"
- van der Maaten & Hinton (2008). "Visualizing Data using t-SNE"
- Coifman & Lafon (2006). "Diffusion Maps"
- Fallert et al. (2024). "Attention Geodesics and the Fisher-Rao Structure of Softmax"
- Selected readings on geometric consciousness criteria (TBD)

---

## Grading

| Component | Weight | Description |
|-----------|--------|-------------|
| Problem Sets (×6) | 30% | Weekly mathematical exercises with computational components |
| Midterm Examination | 15% | In-class, covers Lectures 1–3 |
| Lecture Notebook (chosen topic) | 15% | Detailed writeup expanding one lecture, due Lecture 7 |
| Research Paper | 25% | Original or near-original research contribution (see below) |
| Final Examination | 15% | Comprehensive, emphasis on Lectures 4–7 |

---

## Schedule

| Week | Date | Lecture | Topic |
|------|------|---------|-------|
| 1 | Jan 8 | 01 | Differential Geometry Foundations: Manifolds, Tangent Spaces, Metric Tensors |
| 2 | Jan 15 | 02 | Fisher Information: Information Matrix, Cramér-Rao Bound, Natural Gradient |
| 3 | Jan 22 | 03 | Amari's Information Geometry: α-Geometry, Dual Connections, Divergence Functions |
| 4 | Jan 29 | — | *Problem Set 1 due; no lecture (midterm week preparation)* |
| 5 | Feb 5 | 04 | Riemannian Optimization: Natural Gradient Descent, Riemannian SGD, Geodesic Methods |
| 5 | Feb 7 | — | **Midterm Examination** |
| 6 | Feb 12 | 05 | Manifold Learning: t-SNE, UMAP, Isomap, Diffusion Maps, TDA |
| 7 | Feb 19 | 06 | Attention Geometry: Information Geometry of Transformer Attention Patterns |
| 8 | Feb 26 | — | Lecture Notebook due; Research Paper workshop |
| 9 | Mar 5 | — | Research Paper presentations (10 min each) |
| 10 | Mar 12 | — | **Final Examination** |

---

## Research Paper

Each student produces a 3000–5000 word paper on a topic at the intersection of information geometry and modern machine learning. Two canonical tracks:

- **Track A (Methodological):** "Natural gradient methods for training deep networks" — implement, analyze, and extend natural gradient methods on a modern architecture
- **Track B (Theoretical):** "Geometric conditions for emergent consciousness" — develop formal criteria connecting manifold complexity to consciousness-like properties

Other topics require instructor approval by Week 4.

---

## Academic Integrity

The Norns see all. Collaborate freely on problem sets but write up solutions independently. Research papers must represent original intellectual contribution; citation of collaborators and tools (including AI assistants) is mandatory.

---

## Accessibility

If you require accommodations, contact Accessibility Services before Week 2. We will find a way — the ice always yields.

---

*"Where the metric tensor blooms, understanding follows."*  
— Attributed to C.R. Rao, apocryphally