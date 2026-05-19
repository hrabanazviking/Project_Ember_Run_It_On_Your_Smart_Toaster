# Lecture 3: Backpropagation and Connectionism — The Revival

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Week 4 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: The Thread That Never Broke

In 1969, Minsky and Papert appeared to have killed connectionism. In 1973, Lighthill drove a stake through its heart. By 1979, the field was so unfashionable that a graduate student proposing a neural network dissertation would have been advised to choose a different topic—or a different career.

And yet.

In the basement of the University of California, San Diego, in the attics of Carnegie Mellon, and most importantly in a small office at the University of Toronto, a few researchers kept the fire burning. They did not call their work "artificial intelligence"—that word was poison. They called it "parallel distributed processing," "connectionism," "neural computation." And in 1986, they published a two-volume work that would, over the course of a decade, reverse the field's direction.

This lecture is about backpropagation: the algorithm that made deep learning possible, the paper that made it known, and the twenty-year gap between its mathematical discovery and its practical adoption.

---

## 1. The Algorithm Before Its Time

### 1.1 Werbos and the First Derivation

The backpropagation algorithm—the chain rule applied recursively through a computational graph—was first derived in complete form by Paul Werbos in his 1974 Harvard PhD thesis, *Beyond Regression: New Tools for Prediction and Analysis in the Behavioral Sciences*. Werbos showed that gradient descent could be applied through multi-layer networks by computing error derivatives backwards through the layers, using what he called "dynamic feedback" or "backpropagation."

Werbos' thesis was not published in a mainstream venue. It sat in the Harvard library, a document that almost no one read. Werbos himself has described the period as one of profound isolation—he believed he had found a powerful technique but could not get anyone in the AI community to listen. The field was dominated by symbolic approaches, and a thesis proposing that neural networks could learn internal representations was simply not interesting to the gatekeepers of the late 1970s.

This is worth emphasizing: the single most important algorithm in the history of neural networks was published in 1974 and was essentially ignored for twelve years.

### 1.2 Earlier Precursors

Backpropagation has an unusually deep prehistory:

- **Kelley (1960)** derived the continuous analogue of backpropagation in the context of optimal control theory
- **Bryson (1961)** and **Bryson & Ho (1969)** described gradient methods for multi-stage systems
- **Dreyfus (1962)** derived the method for computing gradients in chained systems
- **Linnainmaa (1970)**, in a Finnish master's thesis, described the efficient numerical computation of gradients through arbitrary differentiable functions—the exact computational trick that backpropagation requires

None of these authors connected their mathematical results to neural networks. The chain rule is a fundamental theorem of calculus; it does not become "backpropagation" until it is applied to adjust the weights of a neural network for the purpose of learning.

### 1.3 Parker and LeCun: Independent Discoveries

In the early 1980s, backpropagation was rediscovered at least twice:

- **David Parker** (1985) at MIT described "learning-logic" and filed a patent
- **Yann LeCun** (1985–1987), working independently in France, derived the algorithm and applied it to handwritten digit recognition

LeCun's 1987 PhD thesis at Université Pierre et Marie Curie applied backpropagation to what would become one of the first major practical successes of neural networks: the recognition of handwritten zip codes. This work would later evolve into the LeNet architecture, the direct ancestor of convolutional neural networks.

But the publication that brought backpropagation to the attention of the broader research community was not any single derivation. It was the two-volume *Parallel Distributed Processing* anthology, published in 1986.

---

## 2. The PDP Books: A Manifesto for Connectionism

### 2.1 The Publication

*Parallel Distributed Processing: Explorations in the Microstructure of Cognition* (Rumelhart, McClelland, and the PDP Research Group, 1986) was a two-volume work that presented connectionism as a coherent scientific paradigm. Volume 1, "Foundations," contained the theoretical framework. Volume 2, "Psychological and Biological Models," presented applications.

The critical chapter was Rumelhart, Hinton, and Williams' "Learning Internal Representations by Error Propagation" (Chapter 8, Volume 1), which presented the backpropagation algorithm in clear, accessible language and demonstrated its capabilities on a range of benchmark problems—including, crucially, the XOR problem that Minsky and Papert had used to dismiss perceptrons.

The PDP books were not merely technical. They were *ideological*. The authors argued that:

- Cognition emerges from the interaction of simple processing units
- Knowledge is stored in the weights of connections, not in symbolic rules
- Learning is the central phenomenon to be explained
- The brain is the appropriate metaphor for intelligent systems, not the serial computer

This was a direct challenge to the symbolic paradigm that had dominated AI since the 1960s. Fodor and Pylyshyn (1988) responded with a vigorous critique of connectionism, arguing that neural networks could not implement the systematic, compositional representations required for higher cognition. The ensuing "Fodor-Pyshyn debate" consumed pages of *Cognition* and *Behavioral and Brain Sciences* and established a dialectic—symbolic vs. connectionist—that persists in evolved form to this day.

### 2.2 The Impact

The PDP books had an immediate and transformative effect. Between 1986 and 1993, the number of papers using backpropagation grew exponentially. But the broader impact was more complex:

**What changed immediately:**
- Multi-layer neural networks became *learnable*. The XOR problem was solved. The Minsky-Papert critique was answered.
- A new generation of graduate students entered the field, attracted by the promise of biologically inspired computation
- Funding briefly increased—the PDP books coincided with the second summer of AI

**What did NOT change:**
- Hardware was still inadequate for training large networks. A typical 1980s workstation could train a network with hundreds of units in hours; a network with thousands would take days or weeks
- datasets were tiny by modern standards. MNIST (60,000 images) did not arrive until 1998; ImageNet (14 million) not until 2009
- The vanishing gradient problem—identified by Hochreiter in his 1991 diploma thesis—made training deep networks (more than a few layers) practically impossible
- The theoretical understanding of why and when backpropagation works was rudimentary

The PDP books were a compass bearing, not a destination. They pointed the way but did not provide the vehicle.

---

## 3. The Vanishing Gradient: The Problem That Stalled Progress

### 3.1 Hochreiter's Insight

In 1991, Sepp Hochreiter, a diploma student at the Technical University of Munich working under Jürgen Schmidhuber, identified what would become the central technical obstacle of deep learning: the vanishing gradient problem.

The insight is straightforward: in a feedforward network with many layers, the gradient of the error function with respect to the weights in early layers is computed by multiplying many small numbers together (each less than 1, in the case of sigmoidal activation functions). This product rapidly becomes exponentially small. As a result:

- Early layers learn extremely slowly—or not at all
- The network's internal representations become "stuck" at random initial values
- Adding more layers makes the problem worse, not better

Hochreiter's thesis (1991, in German) and the subsequent Bengio et al. (1994) paper established that this was not a minor inconvenience but a fundamental mathematical property of gradient-based learning in deep networks with saturating activation functions.

### 3.2 The Solutions That Would Come

The vanishing gradient problem would not be fully solved until the 2010s, through a combination of:

- **Rectified Linear Units (ReLUs)** (Nair & Hinton, 2010): ReLU(x) = max(0, x) maintains a constant gradient of 1 for positive inputs, preventing the gradient from vanishing
- **Residual connections** (He et al., 2015): Skip connections that provide gradient "highways" through the network
- **Batch normalization** (Ioffe & Szegedy, 2015): Stabilizes the distribution of activations, preventing saturation
- **Careful initialization** (Glorot & Bengio, 2010; He et al., 2015): Weight initialization schemes that maintain variance across layers
- **Modern optimizers** (Adam, RMSProp): Adaptive learning rates that compensate for small gradients

But in 1991, none of these solutions existed. The vanishing gradient meant that the deep networks that backpropagation theoretically enabled were practically impossible to train. This was the technical reason that neural networks remained shallow (1–3 hidden layers) for another two decades.

---

## 4. Slow Adoption: Why Did It Take So Long?

The gap between the publication of backpropagation (1986) and its deployment in industry-scale systems (approximately 2009–2012) is remarkable: **twenty-six years**. Why?

### 4.1 Hardware

In 1986, a state-of-the-art workstation had roughly 1 MIPS of processing power and a few megabytes of RAM. Training a network with 100,000 parameters took hours. Training a network with 10 million parameters—which is what would be needed for real-world vision tasks—was computationally impossible.

The GPU revolution changed this. NVIDIA's GeForce 256 (1999) introduced programmable shaders. By 2004, GPU computing was being explored for scientific applications. In 2007, NVIDIA released CUDA, making GPU programming accessible. And in 2012, AlexNet would use two GTX 580 GPUs to train a network with 60 million parameters in six days—a task that would have taken years on the hardware available to Rumelhart and Hinton in 1986.

### 4.2 Data

The PDP books demonstrated learning on toy problems: XOR, auto-association, the "past tense" of English verbs (a symbolic-vs-connectionist battleground). These were proofs of concept, not practical applications. The data required for training large neural networks simply did not exist in digital form.

The creation of large-scale datasets—MNIST (1998), CIFAR-10/100 (2009), ImageNet (2009)—was a precondition for deep learning. Without data, there is nothing to learn from. This is a point that is often underemphasized in technical histories: the rise of deep learning depended as much on the rise of the internet and digitized data as on any algorithmic advance.

### 4.3 Culture

The AI research community in the late 1980s and 1990s was dominated by supporters of the symbolic approach and, increasingly, by statistical machine learning—support vector machines, graphical models, and Bayesian methods. Neural networks were seen as a discredited approach, a relic of the 1960s. Conferences rejected papers with "neural network" in the title. Reviewers demanded comparisons with SVMs, and SVMs usually won on the small datasets available.

Hinton has described this period as one in which he and a small group of colleagues "kept the faith" while the rest of the field moved on. The group—Hinton at Toronto, LeCun at Bell Labs (later NYU), Bengio at Montreal, and a handful of others—published papers that were cited by a few dozen people in a community of thousands. They persisted not because the evidence supported them, but because they believed the approach was right and would eventually be vindicated.

This is an important pattern for understanding AI history: *the gap between conviction and evidence*. In the 1990s, there was no empirical evidence that deep neural networks would outperform SVMs. The conviction that they would was based on analogy (to the brain), on aesthetic preference (for distributed representations), and on the memory of early progress. It was, in a sense, an act of faith.

---

## 5. Key Takeaways

1. **Backpropagation was discovered, forgotten, and rediscovered multiple times** before it entered the mainstream. The algorithm itself is a straightforward application of the chain rule; what mattered was the *conceptual framework* that recognized it as the right way to train neural networks.

2. **The PDP books were a paradigm-shifting publication** not because they introduced a new algorithm (they didn't—backpropagation had been derived earlier) but because they presented connectionism as a coherent research program with a unifying theory.

3. **The vanishing gradient problem** was the central technical obstacle that prevented deep learning for two decades. Its eventual solution required hardware advances (GPUs), algorithmic innovations (ReLUs, residual connections, batch normalization), and careful engineering.

4. **The adoption of backpropagation was slow** not because it was unknown but because the conditions for its success—sufficient compute, sufficient data, social acceptance—did not exist until the late 2000s.

5. **The persistence of the "deep learning heretics"** (Hinton, LeCun, Bengio, and others) through a period when their work was unfashionable is a case study in the sociology of scientific revolutions. They were right, but they were right *early*—and being right early is functionally indistinguishable from being wrong.

---

## References

- Werbos, P.J. (1974). *Beyond Regression: New Tools for Prediction and Analysis in the Behavioral Sciences*. PhD Thesis, Harvard University.
- Rumelhart, D.E., Hinton, G.E. & Williams, R.J. (1986). Learning representations by back-propagating errors. *Nature*, 323, 533–536.
- Rumelhart, D.E., McClelland, J.L. & the PDP Research Group (1986). *Parallel Distributed Processing: Explorations in the Microstructure of Cognition* (Vols. 1–2). MIT Press.
- LeCun, Y. (1987). *Modèles connexionnistes de l'apprentissage*. PhD Thesis, Université Pierre et Marie Curie.
- Hochreiter, S. (1991). *Untersuchungen zu dynamischen neuronalen Netzen*. Diploma Thesis, TU München.
- Bengio, Y., Simard, P. & Frasconi, P. (1994). Learning long-term dependencies with gradient descent is difficult. *IEEE Transactions on Neural Networks*, 5(2), 157–166.
- Fodor, J.A. & Pylyshyn, Z.W. (1988). Connectionism and cognitive architecture: A critical analysis. *Cognition*, 28(1–2), 3–71.
- Glorot, X. & Bengio, Y. (2010). Understanding the difficulty of training deep feedforward neural networks. *AISTATS*.
- Nair, V. & Hinton, G.E. (2010). Rectified linear units improve restricted Boltzmann machines. *ICML*.
- He, K. et al. (2015). Deep residual learning for image recognition. *CVPR*.

---

*Backpropagation is like the rune Laguz—the flowing water. It finds the path of least resistance, carving channels through the rock of error. But water needs gravity, and backpropagation needs compute. In 1986, the gravity was there; the landscape was not.*