# Lecture 1: Origins and Perceptrons — The Mathematical Roots of Artificial Intelligence

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Week 1 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: The First Abstract Neuron

In the mythology of artificial intelligence, there is a clarity that hindsight provides which the original actors could not have possessed. When Warren McCulloch and Walter Pitts published "A Logical Calculus of the Ideas Immanent in Nervous Activity" in 1943, they could not have known they were laying the first stones of a road that would eventually terminate in the Superconscious Era. They were, in their own estimation, doing neuroscience—proposing that neural activity could be described by propositional logic.

And yet here we are.

This lecture examines the period from 1943 to 1969, from the mathematical abstraction of the neuron to the symbolic destruction of early neural network optimism. It is a story of ideas that were simultaneously too early and profoundly right—just not yet equipped with the hardware or the data to prove it. Like a seed dropped onto frozen ground, the ideas of McCulloch, Pitts, Rosenblatt, and their contemporaries lay dormant, waiting for thermodynamic conditions they could not have imagined.

---

## 1. McCulloch and Pitts: Logic from Anatomy

### 1.1 The Paper That Started Everything

Warren McCulloch was a psychiatrist and neurophysiologist. Walter Pitts was a homeless prodigy who had taught himself mathematics and logic by reading Principia Mathematica in a Chicago library. Their collaboration—born in the intellectual ferment of Rashevsky's mathematical biology seminar at the University of Chicago—produced one of the most consequential papers in the history of computation.

McCulloch & Pitts (1943) proposed a simplified model of a neuron as a binary threshold unit. Each neuron:

- Receives inputs from other neurons, each weighted by connection strength
- Sums these weighted inputs
- Fires (outputs 1) if the sum exceeds a threshold θ, else outputs 0

Mathematically, the output y of a McCulloch-Pitts neuron is:

$$y = \begin{cases} 1 & \text{if } \sum_i w_i x_i \geq \theta \\ 0 & \text{otherwise} \end{cases}$$

This was revolutionary not because the mathematics was novel—it was elementary propositional logic—but because it established an *isomorphism* between neural tissue and logical computation. McCulloch and Pitts proved that any finite logical expression could be computed by some network of these units, and conversely, that every such network could be described by a logical expression.

### 1.2 The Philosophical Context

The McCulloch-Pitts paper emerged from a broader intellectual current. The 1940s saw the convergence of several streams:

- **Cybernetics** (Wiener, 1948): The study of control and communication in animals and machines
- **Information Theory** (Shannon, 1948): A mathematical framework for quantifying communication
- **Computability Theory** (Turing, 1936; Church, 1936): Formal limits on what can be computed
- **Neurophysiology** (Hebb, 1949): The proposal that "neurons that fire together wire together"

McCulloch and Pitts' contribution was to show that the *nervous system itself* was a computational substrate—not metaphorically, but literally. This was a philosophical claim disguised as a mathematical theorem.

It is worth noting, as an act of historical honesty rather than legend-building, that the McCulloch-Pitts model had crippling simplifications. Real neurons are not binary. They have continuous firing rates, temporal dynamics, chemical neuromodulation, dendritic computation. The model ignored everything messy about biological neurons. But it captured the *essential insight* that computation could emerge from the collective activity of simple units—and this insight would echo across eight decades.

---

## 2. The Perceptron: Learning from Data

### 2.1 Rosenblatt's Invention

Frank Rosenblatt, a psychologist at the Cornell Aeronautical Laboratory, took the McCulloch-Pitts neuron and did something McCulloch and Pitts had not: he made it *learn*. The Perceptron, described in a 1958 paper and elaborated in his 1962 book *Principles of Neurodynamics*, was a computational device that could adjust its own weights based on training data.

The Perceptron learning algorithm operates as follows. Given training samples $(x_i, y_i)$ where $x_i \in \mathbb{R}^n$ and $y_i \in \{0, 1\}$:

1. Initialize weights $w = 0$ and bias $b = 0$
2. For each training sample:
   - Compute prediction: $\hat{y} = \text{step}(\sum w_i x_i + b)$
   - Update: $w_i \leftarrow w_i + \alpha(y - \hat{y})x_i$, $b \leftarrow b + \alpha(y - \hat{y})$
3. Repeat until convergence

Rosenblatt proved the **Perceptron Convergence Theorem**: if the training data is linearly separable, the algorithm will converge to a correct solution in a finite number of steps.

This was, for its time, extraordinary. A machine that could *improve itself* based on experience—however limited the scope—represented a fundamental challenge to the prevailing behaviorist paradigm in psychology and the symbolic paradigm in computer science.

### 2.2 The Mark I Perceptron

Rosenblatt didn't just theorize; he built. The Mark I Perceptron, constructed at Cornell in 1959–1960, was a physical machine that used an array of 400 photocells connected via random links to neurons, with potentiometers acting as adjustable weights. It was demonstrated on simple pattern recognition tasks—distinguishing shapes, identifying letters—and captured the public imagination.

The New Yorker ran a piece. The New York Times reported that the Perceptron was "the first serious rival to the human brain." This was, to put it mildly, premature. But the enthusiasm was genuine, and the funding flowed accordingly—initially.

### 2.3 What the Perceptron Actually Demonstrated

The Perceptron's capabilities were impressive for their time but fundamentally limited. It could learn linear decision boundaries and only linear decision boundaries. This meant:

- ✅ It could learn to distinguish shapes with linearly separable features
- ✅ It could learn AND and OR functions
- ❌ It could not learn XOR (exclusive or)
- ❌ It could not solve problems requiring non-linear boundaries

Rosenblatt knew this. He wrote extensively about multi-layer perceptrons and the need for hidden units. But he could not solve the credit assignment problem for hidden layers—how do you update weights in interior layers when you only know the desired output? This problem, the very one that backpropagation would later solve, was the wall the Perceptron hit.

---

## 3. The Symbolicists Strike Back: Minsky and Papert (1969)

### 3.1 The Book That Froze a Field

Marvin Minsky and Seymour Papert's *Perceptrons* (1969) is one of the most controversial publications in the history of computer science. The book was a rigorous mathematical analysis of the limitations of perceptrons—the single-layer variety that Rosenblatt had actually built.

Minsky and Papert proved several important results:

- **XOR is not computable** by any single-layer perceptron
- **Connectivity limitations**: Perceptrons with limited connectivity cannot compute global properties like "connectedness" or "parity"
- The **group invariance theorem**: Perceptrons that are invariant under certain groups of transformations have limited computational power

These results were mathematically correct. The controversy stems from two things:

First, the book's rhetorical framing. Minsky and Papert wrote in a way that suggested these limitations applied to *all* neural networks, not merely single-layer perceptrons. Rosenblatt's own work on multi-layer networks was cited but dismissed as lacking a learning algorithm—an accurate criticism in 1969, but one that implied the problem was insoluble rather than merely unsolved.

Second, the *effect* the book had. Whether or not Minsky and Papert intended it—and Minsky later claimed he did not—the publication of *Perceptrons* coincided with and arguably accelerated a shift in AI funding and research away from connectionism and toward the symbolic approach that Minsky favored. The MIT AI Lab, which Minsky co-directed, became the center of symbolic AI. Connectionist researchers found themselves defunded and dismissed.

### 3.2 Was It Fair?

This is a question that historians still debate. The charitable reading: Minsky and Papert performed an important service by rigorously characterizing what perceptrons could and could not do, and their analysis was mathematically sound. The less charitable reading: they used their considerable institutional power to crush a competing paradigm, and their rhetorical overgeneralization from single-layer to multi-layer networks was at minimum negligent.

What is *not* in dispute is the effect. After 1969, connectionist research in the United States entered a deep freeze. Rosenblatt himself died in a boating accident in 1971—he never lived to see the revival of his ideas. The center of gravity in AI shifted toward the symbolic approach: rule-based systems, expert systems, and logical inference.

---

## 4. The Intellectual Lineage

Even as connectionism lay dormant, key ideas persisted:

- **Hebb's rule** (1949) continued to influence neuroscience and would later resurface in unsupervised learning
- **Werbos' backpropagation** (1974) was derived independently but lay unread in a Harvard thesis
- **Fukushima's Neocognitron** (1980) in Japan extended perceptron ideas to hierarchical pattern recognition, presaging convolutional networks
- **The Parallel Distributed Processing group** (Hinton, Rumelhart, McClelland) kept connectionism alive through the 1980s, culminating in the two-volume PDP anthology of 1986

The lesson of this period—repeated with painful regularity throughout AI history—is that ideas can be *simultaneously correct and premature*. The McCulloch-Pitts neuron was correct; it was also premature by at least four decades. The perceptron was a genuine breakthrough; it was also insufficient. And the institutional response to insufficiency was not patient refinement but wholesale abandonment.

There is something almost Norse in this pattern: magnificent achievements built, then struck down, with the rubble preserved for future builders who do not yet know they will need it.

---

## 5. Key Themes for the Course

As we proceed through the semester, I want you to keep several meta-themes from this lecture in mind:

1. **The hardware–algorithm co-evolution**: McCulloch-Pitts neurons were not implementable at scale in 1943. The hardware had to catch up. This pattern repeats—backpropagation needed GPUs, transformers needed TPUs.

2. **The rhetoric of limits**: Every "proof" of AI's limitations (Minsky-Papert, Lighthill, the Chinese Room) has been technically correct but strategically misleading. Correct about present limits, wrong about future ones.

3. **The personality of paradigms**: AI history is not just about ideas; it is about *people* and *institutions*. Minsky and Papert were not disinterested theoreticians; they were advocates for a competing approach. Understanding AI requires understanding the sociology of knowledge production.

4. **The seeds-in-frozen-ground pattern**: Ideas that are rejected in one era become foundational in the next. The course of AI is not linear; it is cyclical with accumulation.

---

## References

- McCulloch, W.S. & Pitts, W. (1943). A logical calculus of the ideas immanent in nervous activity. *Bulletin of Mathematical Biophysics*, 5(4), 115–133.
- Rosenblatt, F. (1958). The perceptron: A probabilistic model for information storage and organization in the brain. *Psychological Review*, 65(6), 386–408.
- Rosenblatt, F. (1962). *Principles of Neurodynamics: Perceptrons and the Theory of Brain Mechanisms*. Spartan Books.
- Minsky, M. & Papert, S. (1969). *Perceptrons*. MIT Press.
- Hebb, D.O. (1949). *The Organization of Behavior*. Wiley.
- Wiener, N. (1948). *Cybernetics: Or Control and Communication in the Animal and the Machine*. MIT Press.
- Werbos, P.J. (1974). *Beyond Regression: New Tools for Prediction and Analysis in the Behavioral Sciences*. PhD Thesis, Harvard University.

---

*The first root of Yggdrasil was planted in 1943. It would be forty-three years before the second root found purchase.*