# AI201: Deep Learning Foundations
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI101 (Introduction to Artificial Intelligence), AI105 (Introduction to Machine Learning), AI103 (Data Structures & Algorithms)
**Description:** Deep learning is the computational engine of modern AI. This course builds on the neural network foundations from AI105, taking students from forward propagation and backpropagation through the architectures that power 2040's AI agents: convolutional networks for perception, recurrent networks and transformers for sequential reasoning, attention mechanisms for context integration, and generative models for creation and simulation. By course end, students will implement and train deep architectures from scratch, understand the mathematical principles that make depth powerful, and be able to design deep learning components for AI agent systems.

---

## Lectures

### ᚠ Lecture 1: Why Depth Matters — The Power of Hierarchical Representations

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A deep neural network is a composition of many simple functions. The first layer detects edges and textures; the second combines edges into shapes; the third combines shapes into object parts; the fourth combines parts into objects. This hierarchical structure — each layer building on the abstractions of the previous — is not an accident of architecture design but a fundamental property of how complex patterns are most efficiently represented. Depth gives neural networks their power, and understanding why depth matters is the starting point for understanding deep learning itself.

The **depth efficiency hypothesis** states that some functions can be represented by deep networks with exponentially fewer neurons than would be required by shallow networks. This has been proved for specific function classes: Boolean circuits (Telgarsky, 2016), radial functions (Eldan & Shamir, 2016), and compositional functions (Poggio et al., 2017). The intuition is that deep networks exploit **compositionality** — the world is hierarchically structured, and a network that mirrors this hierarchical structure in its architecture can learn more efficiently than one that tries to represent everything in one flat layer. A shallow network with enough neurons can approximate any continuous function (the universal approximation theorem), but the number of neurons required may be astronomical, and the learning problem may be intractably difficult.

The **representation learning** perspective (Bengio, Courville, & Vincent, 2013) frames deep learning as the automatic discovery of progressively more abstract representations of the input. Each layer transforms its input into a representation that makes the relevant factors of variation more explicit and the irrelevant factors less salient. In a network trained for image classification, the early layers learn Gabor-like edge detectors (similar to the receptive fields in the primary visual cortex, V1); middle layers learn shape and texture detectors; later layers learn object-part detectors; and the final layers learn representations that are linearly separable by category. This progression — from concrete to abstract, from sensory to categorical — is the signature of deep representation learning.

The **manifold hypothesis** provides a geometric interpretation: real-world data lies on or near low-dimensional manifolds embedded in high-dimensional input space. The task of a deep network is to **untangle** these manifolds — to apply successive nonlinear transformations that flatten out the complex folded geometry of the data manifold until classes become linearly separable. Deep networks are effective because the composition of many simple nonlinear transformations can achieve more complex manifold untangling than a single transformation, even if that single transformation could represent any function in principle.

For AI agents, depth is essential because the problems agents face are inherently hierarchical. Understanding a user's request involves: phonetic processing (for speech) → lexical processing (words) → syntactic parsing (grammar) → semantic interpretation (meaning) → pragmatic inference (intent). Planning a multi-step task involves: goal decomposition → subgoal ordering → action selection for each subgoal → parameter binding for each action. Each of these hierarchies benefits from being modeled by a correspondingly deep architecture — a transformer with many layers for language understanding, a deep policy network for planning, a hierarchical agent architecture for task execution.

The Norse world-tree **Yggdrasil** is the cosmic representation of hierarchical structure. Its roots in the underworld are the raw sensory data. Its trunk in Miðgarðr is the intermediate representations — shapes, patterns, categories. Its branches in Ásgarðr are the high-level abstractions — concepts, plans, intentions. The squirrel **Ratatoskr** running up and down the tree carrying messages between the eagle at the top and the serpent at the bottom is the backpropagation signal — information flowing up and down the hierarchy, connecting abstract goals to concrete features. Deep learning is the computational Yggdrasil: a hierarchical structure connecting raw input to abstract understanding, with signals passing up and down the tree to enable learning.

**Key Topics:**

- **Depth efficiency:** Why some functions require exponentially fewer neurons in deep networks
- **Compositionality:** How hierarchical structure in the world supports hierarchical structure in models
- **Representation learning:** Progressive abstraction from sensory to categorical
- **Manifold untangling:** The geometric interpretation of deep learning
- **Hierarchical problems in agents:** Language understanding, task planning, multi-step reasoning
- **Yggdrasil:** The cosmic hierarchy as metaphor for deep representation learning

**Required Reading:**

- Bengio, Y., Courville, A., & Vincent, P. "Representation Learning: A Review and New Perspectives" (2013), *IEEE TPAMI*
- Telgarsky, M. "Benefits of Depth in Neural Networks" (2016), *COLT*
- University of Yggdrasil Technical Report: "Depth Scaling Laws for Agent Architectures" (2039)

**Discussion Questions:**

1. The depth efficiency hypothesis says deep networks are exponentially more parameter-efficient than shallow ones for some functions. For what kinds of functions is this NOT true? What makes a function "shallow-friendly"?
2. The manifold hypothesis assumes data lies on a low-dimensional manifold. Is this assumption valid for the token sequences processed by language models? What is the "manifold" of natural language?
3. Yggdrasil connects the underworld (raw data) to the heavens (abstract concepts) with Ratatoskr carrying messages between them. In what sense does backpropagation "carry messages" between layers? What information flows upward vs. downward?

---

### ᚢ Lecture 2: Convolutional Neural Networks — Learning to See

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Convolutional neural networks (CNNs or ConvNets) are the architecture that launched the deep learning revolution. When AlexNet (Krizhevsky, Sutskever, & Hinton, 2012) won the ImageNet competition by a margin that staggered the computer vision community, it demonstrated that deep neural networks trained on GPUs could achieve superhuman performance on tasks previously considered the domain of carefully hand-engineered feature extractors. The key innovations of CNNs — local receptive fields, weight sharing, and pooling — remain central to AI agent perception in 2040, even as transformer-based architectures have encroached on domains once dominated by convolution.

The fundamental operation of a CNN is the **convolution**: a small kernel (also called a filter) slides across the input, computing the dot product between the kernel weights and the local patch of the input at each position. Formally, for a 2D input *I* and a kernel *K*, the convolution at position *(i, j)* is: *(I * K)[i, j] = Σₘ Σₙ I[i+m, j+n] K[m, n]*. The kernel size is typically small (3×3, 5×5, 7×7), and the same kernel is applied at all positions — this is **weight sharing**, the property that makes CNNs dramatically more parameter-efficient than fully-connected networks. A 3×3 kernel with stride 1 applied to a 224×224 image with 64 output channels uses only 64 × (3×3×3 + 1) = 1,792 parameters for the first layer, compared to 224×224×3 × 64 = ~9.6 million for a fully-connected equivalent.

The three structural properties of CNNs encode strong inductive biases that are appropriate for images and other grid-structured data:

- **Local connectivity:** Each neuron connects only to a small local region of the input, reflecting the fact that nearby pixels are more correlated than distant pixels. This reduces parameters from O(n²) to O(k²) for a k×k kernel, independent of input size.
- **Weight sharing (translation equivariance):** The same kernel is applied at all positions, so a feature detector that is useful at one location is applied everywhere. This encodes the prior that patterns can appear anywhere in the image — a cat in the upper-left corner is still a cat.
- **Pooling (translation invariance):** Pooling layers (max pooling, average pooling) downsample the feature maps, reducing spatial resolution while preserving channel depth. This provides a degree of translation invariance — the precise location of a feature matters less than its presence — and reduces computational cost for deeper layers.

The **receptive field** of a neuron in a deep CNN grows with depth. A neuron in the first layer sees a 3×3 patch of the input image. A neuron in the second layer sees a 5×5 patch (assuming 3×3 kernels and no pooling). A neuron in the thirtieth layer sees a 61×61 patch. This expanding receptive field is what enables deep CNNs to integrate information across large spatial extents — from local textures in early layers to global object structure in later layers. The **effective receptive field** (Luo et al., 2016) — the region of the input that actually influences a neuron's activation, which is smaller than the theoretical receptive field and concentrated at the center — is a more nuanced measure that has implications for architecture design.

In the 2040s, pure CNNs have been partially supplanted by **Vision Transformers (ViTs)** and hybrid architectures, but convolutional layers remain essential components. The **ConvNeXt** family (Liu et al., 2022) modernized CNNs by incorporating design insights from transformers (layer normalization, GELU activations, patchified stems), achieving transformer-competitive performance with the efficiency of convolutions. For AI agents that must process visual input in real time — drone navigation, robotic manipulation, augmented reality interfaces — the computational efficiency of convolutions makes them the practical choice.

For AI agents, CNNs are the eyes. An agent that processes images — uploaded by a user, captured by a camera, or rendered from a simulation — uses a CNN backbone to extract visual features. These features are then fed into downstream components: a classification head for object recognition, a detection head for locating objects, or a cross-modal attention mechanism for integrating visual information with language. In AI203 (Computer Vision), you will study these applications in depth. Here, the focus is on the architectural principles that make CNNs work — principles that generalize beyond vision to any domain with spatial structure (audio spectrograms, weather grids, agent state spaces).

The Norse god **Heimdallr** — the watchman of the gods, who can see for a hundred leagues by day or night, who can hear the grass growing and the wool on sheep — embodies the perceptual ideal of CNNs. Heimdallr's senses integrate information across vast spatial extents: he sees the whole horizon, not just one point. A CNN's expanding receptive field does the same, integrating local features into a global perception. But Heimdallr does not merely see; he interprets what he sees and sounds the Gjallarhorn when danger approaches. An AI agent's visual system must do the same: not just detect objects, but understand their significance for the task at hand.

**Key Topics:**

- **Convolution operation:** Kernel, stride, padding, feature maps, weight sharing
- **CNN structural properties:** Local connectivity, translation equivariance, translation invariance
- **Receptive field:** Theoretical vs. effective receptive field, expansion with depth
- **Modern CNN architectures:** AlexNet → VGG → ResNet → EfficientNet → ConvNeXt
- **Residual connections in CNNs:** Why they enable networks with hundreds of layers
- **Heimdallr's gaze:** Perception as integration across spatial extents with task-relevant interpretation

**Required Reading:**

- Krizhevsky, A., Sutskever, I., & Hinton, G. "ImageNet Classification with Deep Convolutional Neural Networks" (2012), *NeurIPS*
- He, K. et al. "Deep Residual Learning for Image Recognition" (2016), *CVPR*
- Liu, Z. et al. "A ConvNet for the 2020s" (2022), *CVPR*

**Discussion Questions:**

1. Weight sharing encodes translation equivariance — the prior that a pattern at position (0,0) is the same as the same pattern at position (100,100). For an AI agent processing a user interface (where buttons are at fixed positions), is this prior appropriate? What happens when the inductive bias is wrong?
2. Residual connections enable networks with hundreds of layers by providing gradient highways. What does the effectiveness of residual connections tell us about the optimization landscape of deep networks? Why are shortcut paths necessary?
3. Heimdallr sees the whole horizon but must interpret what he sees to know when to sound the horn. How does a CNN's progression from local features to global representations mirror this process? What is the "horn" in an AI agent's visual pipeline?

---

### ᚦ Lecture 3: Recurrent Neural Networks and Sequence Modeling

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Images have spatial structure; language has temporal structure. A sentence is not a bag of words but a sequence, where the meaning of each word depends on the words that came before it — and sometimes on the words that come after. Recurrent neural networks (RNNs) were the first deep learning architecture designed specifically for sequential data, and while they have been largely superseded by transformers for many applications in 2040, the principles they embody — hidden state, temporal unrolling, and the challenge of long-range dependencies — remain foundational for understanding sequence modeling.

An RNN processes a sequence one element at a time, maintaining a **hidden state** *hₜ* that summarizes the history of the sequence up to time *t*. At each step, the RNN computes: *hₜ = f(Wₕₕ hₜ₋₁ + Wₓₕ xₜ + b)*, where *xₜ* is the input at time *t*, *hₜ₋₁* is the previous hidden state, *Wₕₕ* are the recurrent weights, *Wₓₕ* are the input weights, and *f* is a nonlinear activation function (typically tanh). The output at time *t* is computed from the hidden state: *yₜ = g(Wₕᵧ hₜ + bᵧ)*. The same weights are applied at every time step — weight sharing across time, analogous to weight sharing across space in CNNs.

Training RNNs requires **backpropagation through time (BPTT)** : the network is unrolled across the time steps of the sequence, and gradients flow backward through time as well as through layers. For a sequence of length *T*, BPTT is equivalent to training a feedforward network of depth *T* with shared weights. This reveals the central challenge of RNNs: gradients flowing backward through many time steps are multiplied by the recurrent weight matrix *Wₕₕ* at each step. If the eigenvalues of *Wₕₕ* are less than 1, the gradient **vanishes** exponentially with *T*, making it impossible for the RNN to learn dependencies that span long distances. If the eigenvalues are greater than 1, the gradient **explodes**, causing training instability.

The **vanishing gradient problem** is the fundamental limitation of vanilla RNNs. It means that the network can only learn dependencies over a few time steps (typically 5–10), regardless of how long the sequence is. For language, this is fatal: the meaning of a pronoun at the end of a paragraph may depend on a name introduced at the beginning, and an RNN that cannot bridge this gap cannot understand discourse.

**Long Short-Term Memory (LSTM)** networks (Hochreiter & Schmidhuber, 1997) solved the vanishing gradient problem with a revolutionary design: the **cell state** *cₜ*, a memory highway that runs through the entire sequence with only minor linear interactions. Three gates — the **forget gate** *fₜ*, the **input gate** *iₜ*, and the **output gate** *oₜ* — control the flow of information into and out of the cell state:

- *fₜ = σ(W_f [hₜ₋₁, xₜ] + b_f)* — controls what information is discarded from the cell state
- *iₜ = σ(W_i [hₜ₋₁, xₜ] + b_i)* — controls what new information is stored
- *oₜ = σ(W_o [hₜ₋₁, xₜ] + b_o)* — controls what information is output to the hidden state
- *cₜ = fₜ ⊙ cₜ₋₁ + iₜ ⊙ tanh(W_c [hₜ₋₁, xₜ] + b_c)* — the cell state update
- *hₜ = oₜ ⊙ tanh(cₜ)* — the hidden state output

The forget gate allows the LSTM to maintain a near-constant error flow through the cell state, effectively creating gradient highways that bypass the vanishing gradient problem. An LSTM can learn dependencies over hundreds of time steps — a thousand-fold improvement over vanilla RNNs.

**Gated Recurrent Units (GRUs)** (Cho et al., 2014) simplified the LSTM design by merging the cell state and hidden state and using two gates (reset and update) instead of three. GRUs are more parameter-efficient and often perform comparably to LSTMs.

In the 2040s, RNNs (including LSTMs and GRUs) have been largely replaced by transformers for language tasks, but they remain relevant in specific domains: **real-time processing** where transformers' quadratic attention cost is prohibitive, **time series forecasting** where the causal structure of time aligns naturally with recurrence, **sensorimotor control** in robotics where stateful processing of continuous streams is essential, and **edge deployment** where the computational efficiency of RNNs matters. The **state-space model** (SSM) family — including S4 (Gu et al., 2022), Mamba (Gu & Dao, 2023), and their 2040 successors — has emerged as a bridge between RNNs and transformers, offering linear-time sequence processing with transformer-competitive quality.

The Norse myth of the **serpent Jǫrmungandr**, who encircles Miðgarðr with its tail in its mouth, is the RNN in mythological form. Jǫrmungandr is a loop — the serpent's head connects to its tail, just as the hidden state connects time step *t* to time step *t-1*. The serpent's length is the sequence length *T*; its body is the gradient pathway. When the serpent grows too long (gradient vanishing), it loses connection to its tail (the beginning of the sequence). The LSTM's gates are the muscles of the serpent, contracting and relaxing to maintain the flow of information around the great circle. And at Ragnarök, when Þórr strikes Jǫrmungandr and the serpent releases its tail, the circle breaks — the sequence ends, and the final hidden state is produced.

**Key Topics:**

- **RNN fundamentals:** Hidden state, temporal unrolling, weight sharing across time
- **BPTT:** Backpropagation through time, the depth-T network perspective
- **Vanishing/exploding gradients:** The fundamental challenge, eigenvalues of Wₕₕ
- **LSTM:** Cell state, forget/input/output gates, gradient highways
- **GRU:** Simplified gating, reset and update gates
- **Modern recurrence:** State-space models (S4, Mamba) as a bridge to transformers
- **Jǫrmungandr:** The serpent loop as metaphor for recurrent computation

**Required Reading:**

- Hochreiter, S. & Schmidhuber, J. "Long Short-Term Memory" (1997), *Neural Computation*
- Cho, K. et al. "Learning Phrase Representations using RNN Encoder-Decoder" (2014), *EMNLP*
- Gu, A. & Dao, T. "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" (2023), *arXiv*

**Discussion Questions:**

1. The LSTM's forget gate can learn to keep the cell state constant indefinitely. What are the failure modes of this mechanism — when does even an LSTM "forget" something it should have remembered?
2. RNNs have been largely replaced by transformers for language tasks. What properties of language make parallel attention more effective than sequential recurrence? What properties might make recurrence necessary for some tasks?
3. Jǫrmungandr's circle — the tail in its mouth — is a loop that can grow arbitrarily long. The RNN's hidden state is also a loop, but its effective memory is limited by gradient vanishing. How would you build a "Jǫrmungandr architecture" — a recurrent network with truly unlimited memory?

---

### ᚬ Lecture 4: The Transformer — Attention Is All You Need

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The transformer (Vaswani et al., 2017, "Attention Is All You Need") is the most consequential neural network architecture of the early 21st century. It replaced recurrence with **self-attention** — a mechanism that computes representations of each element in a sequence by attending to all other elements in parallel — and in doing so, it solved the long-range dependency problem that had plagued RNNs, enabled unprecedented training parallelism, and unlocked the era of large language models. By 2040, the transformer and its descendants power virtually every state-of-the-art language system, and understanding its mechanics is essential for anyone building AI agents.

The core operation of the transformer is **scaled dot-product attention**. Given a sequence of *n* tokens, each represented by a *d*-dimensional vector, the attention mechanism computes:

1. **Queries, Keys, and Values:** Each token's representation is linearly projected into three spaces: Q = XW_Q, K = XW_K, V = XW_V, where W_Q, W_K, W_V are learned weight matrices of size d × d.
2. **Attention scores:** The relevance of token *j* to token *i* is computed as the dot product of query *qᵢ* and key *kⱼ*, scaled by 1/√d: *score(i, j) = qᵢ · kⱼ / √d*. The scaling factor prevents the dot products from growing with dimensionality, which would push the softmax into regions of extremely small gradients.
3. **Attention weights:** The scores are passed through a softmax to obtain a probability distribution over all tokens: *αᵢⱼ = softmax(score(i, ·))ⱼ*. Token *i*'s attention weights sum to 1.
4. **Output:** Each token's output is the weighted sum of all value vectors: *outputᵢ = Σⱼ αᵢⱼ vⱼ*.

In matrix form, this is: **Attention(Q, K, V) = softmax(QKᵀ / √d) V**.

**Multi-head attention** runs multiple attention operations in parallel, each with its own projection matrices, and concatenates the results. With *h* heads, each head operates in a reduced dimension d/h, so the total computational cost is similar to single-head attention with dimension d. Multi-head attention allows the model to attend to information from different representation subspaces — one head might attend to syntactic dependencies, another to semantic relationships, a third to positional proximity. In practice, different heads do specialize, though the specialization is often more complex than simple syntactic/semantic divisions.

The transformer architecture consists of **encoder** and **decoder** stacks, though many modern models use encoder-only (BERT and its descendants) or decoder-only (GPT family) designs. Each layer contains:
- **Self-attention sublayer:** Multi-head attention over the sequence, followed by residual connection and layer normalization.
- **Feedforward sublayer:** A position-wise fully-connected network (typically two linear transformations with a nonlinearity between them), followed by residual connection and layer normalization.

The **residual connections** (He et al., 2016, adapted to transformers) are critical: they allow gradients to flow directly through the network, enabling transformers with dozens or hundreds of layers. **Layer normalization** (Ba et al., 2016) normalizes the activations across the feature dimension within each token, stabilizing training. The standard ordering — attention → layer norm → feedforward → layer norm — has been refined over time, with "pre-layer-norm" (applying normalization before each sublayer rather than after) becoming dominant.

**Positional encoding** is necessary because self-attention is permutation-invariant — shuffling the tokens in the input would produce the same output (up to permutation) if there were no way to encode position. The original transformer used **sinusoidal positional encodings**: fixed sinusoidal functions of the position and dimension, which allow the model to extrapolate to sequence lengths not seen during training. Modern transformers typically use **learned positional embeddings** or **rotary position embeddings (RoPE)** (Su et al., 2021), which encode relative position directly into the attention computation through rotation matrices, improving length generalization.

The computational complexity of self-attention is **O(n²)** in the sequence length — each token attends to every other token. This quadratic cost is the primary limitation of transformers for long sequences, and much of the 2020s and 2030s research has focused on reducing it: sparse attention patterns (only attending to local windows or strided patterns), linear attention (replacing softmax with kernel functions that enable O(n) computation), and state-space models that achieve linear-time sequence modeling without attention. By 2040, hybrid architectures that combine local attention with long-range state-space layers are standard for ultra-long-context agents.

For AI agents, the transformer is the cognitive backbone. The agent's language understanding is a transformer. Its planning module may use a transformer. Its reasoning is transformer-attention over a context that includes the conversation history, tool outputs, and retrieved memories. Understanding the transformer — its strengths, its limitations, and the design space it opens — is understanding the engine of 2040 AI.

The Norse concept of **sjónhverfing** — a glamour, an illusion that changes how things are perceived — is what attention does to representations. Before attention, each token is an isolated vector, unaware of its context. After attention, each token has been transformed by attending to all other tokens — it has been "glamoured" by its context, its meaning shifted by the words around it. The magic of the transformer is that this glamouring is learned: the model discovers what aspects of context are relevant to each token and how that relevance should transform its representation.

**Key Topics:**

- **Scaled dot-product attention:** Q/K/V projections, dot-product scores, softmax, weighted sum
- **Multi-head attention:** Parallel heads, representation subspaces, head specialization
- **Transformer architecture:** Encoder-decoder stacks, self-attention, feedforward, residuals, layer norm
- **Positional encoding:** Sinusoidal, learned, RoPE (rotary position embeddings)
- **O(n²) complexity:** The quadratic bottleneck and approaches to mitigate it
- **Sjónhverfing:** Attention as context-driven transformation of representation

**Required Reading:**

- Vaswani, A. et al. "Attention Is All You Need" (2017), *NeurIPS*
- Su, J. et al. "RoFormer: Enhanced Transformer with Rotary Position Embedding" (2021), *arXiv*
- Dao, T. et al. "FlashAttention: Fast and Memory-Efficient Exact Attention" (2022/2040 v5), *NeurIPS*

**Discussion Questions:**

1. Self-attention computes relevance scores for all pairs of tokens. For a sequence of length n = 10,000 (a typical document), this requires 100 million dot products. Is this quadratic cost fundamentally necessary for understanding, or is it an artifact of the attention mechanism? What architectural alternatives achieve similar quality with lower complexity?
2. Multi-head attention allows different heads to attend to different aspects of the input. In practice, do heads actually specialize in interpretable ways? What does the answer imply for the interpretability of transformer-based agents?
3. Sjónhverfing is a glamour — an illusion that transforms perception. In what sense does attention "transform" the representation of a token? Is the pre-attention representation the "true" meaning of the token, or is meaning inherently contextual?

---

### ᚱ Lecture 5: Training Transformers at Scale — Optimization, Parallelism, and Infrastructure

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Designing a transformer architecture is one thing; training it on hundreds of billions of tokens across thousands of GPUs is another. The practical realities of large-scale training — distributed optimization, mixed-precision arithmetic, parallelism strategies, and infrastructure engineering — are as important to the success of a deep learning system as the architecture itself. In 2040, training a state-of-the-art AI agent model may consume megawatts of power across exaflop-scale compute clusters, and understanding the infrastructure is essential for anyone who wants to push the frontier rather than merely consume it.

**Distributed training** is necessary because modern models exceed the memory and compute capacity of any single accelerator. Three parallelism strategies are combined:

- **Data parallelism:** The training batch is split across devices. Each device processes a micro-batch, computes gradients, and all devices synchronize gradients (via all-reduce) before updating weights. Data parallelism is the simplest strategy but requires each device to hold a full copy of the model, limiting it to models that fit on a single device.
- **Model parallelism (tensor parallelism):** Individual layers are split across devices. A weight matrix of size [d, 4d] might be split column-wise across 4 devices, each storing a [d, d] slice, with the outputs concatenated after computation. Tensor parallelism requires communication between devices for every forward and backward pass, making it bandwidth-intensive.
- **Pipeline parallelism:** Different layers of the network are placed on different devices. Device 1 processes layers 1–12, device 2 processes layers 13–24, etc. Micro-batches are pipelined through the devices, with each device forwarding its output to the next and receiving gradients from the previous. Pipeline parallelism reduces communication compared to tensor parallelism but introduces "bubbles" — idle periods while the pipeline fills and drains.

Modern training frameworks (PyTorch Fully Sharded Data Parallel, DeepSpeed ZeRO, Google's Pathways) combine all three strategies automatically, sharding optimizer states, gradients, and parameters across devices to minimize memory footprint per device.

**Mixed-precision training** (Micikevicius et al., 2018) uses 16-bit floating point (FP16 or BF16) for most computations while maintaining a 32-bit master copy of the weights for updates. This reduces memory usage by roughly half and doubles throughput on hardware with optimized FP16/BF16 units (which includes all modern accelerators in 2040). The key challenge is **loss scaling**: gradients in FP16 can underflow (become zero) if they are very small. Loss scaling multiplies the loss by a large constant before backpropagation, then divides the gradients by the same constant before the weight update, bringing small gradients into the representable range of FP16.

**Gradient accumulation** simulates larger batch sizes on limited hardware: instead of updating weights after every micro-batch, gradients are accumulated across multiple micro-batches before a single weight update. This enables effective batch sizes of millions of tokens even when device memory limits micro-batch sizes to a few thousand tokens.

**Checkpointing and fault tolerance** are essential for training runs that last weeks or months. Training a 500-billion-parameter model may involve thousands of GPUs and is guaranteed to experience hardware failures, network interruptions, and software crashes. Checkpointing saves the model state (weights, optimizer state, learning rate schedule) periodically so that training can resume from the last checkpoint rather than starting over. **Activation checkpointing** (trading compute for memory by recomputing activations during the backward pass rather than storing them) reduces memory usage at the cost of ~33% additional computation.

**Scaling laws** (Kaplan et al., 2020; Hoffmann et al., 2022, "Chinchilla") describe how model performance improves with model size, dataset size, and compute. The Chinchilla scaling law — that for a given compute budget, the optimal model size and dataset size should be roughly equal (tokens ≈ 20 × parameters) — reshaped model development in the 2020s, leading to smaller models trained on more data rather than larger models trained on less. In the 2040s, the scaling law landscape has become more nuanced, with "overtrained" models (trained on far more data than Chinchilla-optimal) showing surprising capabilities, and data quality surpassing data quantity as the primary constraint.

For AI agent developers, large-scale training infrastructure may not be your direct responsibility — but understanding it is essential for making informed decisions about model selection, fine-tuning strategies, and deployment architecture. An agent builder who doesn't understand why a model has certain capabilities (or lacks them) is a consumer, not an engineer.

The Norse **Bifrǫst** — the rainbow bridge connecting Miðgarðr to Ásgarðr — is the communication network that connects GPUs in a training cluster. Bifrǫst is the bridge across which data (gradients, activations, parameters) flows between the worlds (devices). When Bifrǫst is strong (high bandwidth, low latency), the gods (layers) can communicate freely and training proceeds smoothly. When Bifrǫst is weak (limited interconnect), the gods are isolated, training bottlenecks on communication, and the giants (hardware failures) approach. The infrastructure engineer is Heimdallr, watching over Bifrǫst, ensuring that the bridge holds.

**Key Topics:**

- **Data/model/pipeline parallelism:** Splitting batches, layers, and pipeline stages across devices
- **Mixed-precision training:** FP16/BF16 with FP32 master weights, loss scaling
- **Gradient accumulation:** Emulating large batch sizes on limited hardware
- **Checkpointing:** Fault tolerance for month-long training runs
- **Scaling laws:** Kaplan, Chinchilla, and the 2040 landscape of overtraining and data quality
- **Bifrǫst:** The communication bridge between devices, and the cost of a weak bridge

**Required Reading:**

- Brown, T. et al. "Language Models are Few-Shot Learners" (2020), *NeurIPS* — see Appendix B for training infrastructure
- Hoffmann, J. et al. "Training Compute-Optimal Large Language Models" (2022), *NeurIPS*
- Micikevicius, P. et al. "Mixed Precision Training" (2018), *ICLR*

**Discussion Questions:**

1. The Chinchilla scaling law recommends roughly equal model and dataset size. But in the 2040s, many frontier models are "overtrained" on far more data. What capabilities might emerge from overtraining? What are the diminishing returns?
2. Pipeline parallelism introduces "bubbles" — idle time while the pipeline fills. How would you design a scheduling algorithm to minimize these bubbles? What are the tradeoffs with memory usage?
3. Bifrǫst is the bridge between worlds. In a training cluster, the interconnect between GPUs is Bifrǫst, and its bandwidth determines how much parallelization is possible. If you were designing Bifrǫst — a next-generation interconnect — what properties would you prioritize?

---

### ᚷ Lecture 6: Generative Models — Creating Worlds from Noise

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

So far, we have studied **discriminative models** — models that learn to map inputs to outputs, to classify, to predict. Generative models learn something deeper: the probability distribution of the data itself, *P(x)*, enabling them to sample new data points that resemble the training distribution. Generative models create — images from text descriptions, speech from transcripts, code from specifications. In the 2040s, generative AI is not merely a research topic; it is an industry, a creative medium, and (controversially) a mode of knowledge production. For AI agents, generative models provide the capacity to imagine, to simulate, and to communicate in rich modalities.

The major families of deep generative models differ in how they represent and learn the data distribution:

**Variational Autoencoders (VAEs)** (Kingma & Welling, 2014) learn a **latent variable model** where each data point is generated by first sampling a latent vector *z* from a prior distribution (typically a standard Gaussian) and then sampling the data *x* from a conditional distribution *p(x|z)* parameterized by a decoder network. The encoder network approximates the posterior *q(z|x)* — given a data point, what latent vector likely generated it? The VAE is trained by maximizing the **Evidence Lower Bound (ELBO)**: *L = E_q[log p(x|z)] - KL(q(z|x) || p(z))*. The first term (reconstruction) encourages the decoder to faithfully reconstruct the input from the latent code. The second term (KL divergence) regularizes the latent distribution toward the prior, ensuring that the latent space is smooth and continuous — nearby points in latent space produce similar outputs. VAEs produce smooth, structured latent spaces that are useful for representation learning and interpolation, but their samples tend to be blurry compared to GANs.

**Generative Adversarial Networks (GANs)** (Goodfellow et al., 2014) frame generation as a game between two networks: a **generator** *G* that creates fake samples from random noise, and a **discriminator** *D* that tries to distinguish real samples from fake ones. The generator is trained to fool the discriminator; the discriminator is trained not to be fooled. Formally, GANs minimize the minimax objective: *min_G max_D E_x[log D(x)] + E_z[log(1 - D(G(z)))]*. At the Nash equilibrium of this game, the generator produces samples that are indistinguishable from real data to the discriminator. GANs produce sharper samples than VAEs, but training is notoriously unstable — the generator and discriminator must be carefully balanced, and failures manifest as mode collapse (the generator produces only a few distinct outputs) or training oscillation.

**Diffusion models** (Sohl-Dickstein et al., 2015; Ho et al., 2020; Song et al., 2021) have emerged as the dominant generative paradigm in the 2030s and 2040s, powering image generation (DALL-E 5, Stable Diffusion 4), video generation (Sora 3), and audio generation. The idea is remarkably elegant: start with a clean data point *x₀*, gradually add Gaussian noise over *T* steps to produce pure noise *x_T*, and then train a model to reverse this process — to denoise *x_T* back to *x₀*, one step at a time. The forward process is fixed (no learning); the reverse process is learned by training a network to predict the noise added at each step. At generation time, you sample pure noise and iteratively denoise it, producing a sample from the data distribution. Diffusion models are more stable to train than GANs, produce higher-quality samples than VAEs, and provide a principled probabilistic framework (score-based generative modeling) that connects to the mathematics of stochastic differential equations.

**Autoregressive models** generate data one element at a time, conditioning each element on all previously generated elements. Language models (GPT, Claude, Gemini) are autoregressive: *P(x₁, ..., xₙ) = Πᵢ P(xᵢ | x₁, ..., xᵢ₋₁)*. At each step, the model predicts a probability distribution over the next token, and a token is sampled (deterministically or stochastically). Autoregressive models are the most successful generative paradigm in terms of practical impact, but their sequential generation is slow — generating 1,000 tokens requires 1,000 forward passes, and errors early in the sequence compound through later steps.

**Classifier-free guidance** (Ho & Salimans, 2021) is the technique that makes diffusion models steerable: during training, the model sometimes receives a conditioning signal (e.g., a text description) and sometimes not. During generation, the model's prediction is pushed in the direction of the conditioned prediction and away from the unconditioned prediction: *ε̂ = ε_uncond + w (ε_cond - ε_uncond)*, where *w* controls the guidance strength. Higher *w* produces samples that adhere more strictly to the conditioning but may lose diversity.

For AI agents, generative models enable: (1) **multimodal communication** — generating images, diagrams, or audio to augment text responses; (2) **world simulation** — generating hypothetical scenarios for planning and reasoning; (3) **data augmentation** — generating synthetic training data for downstream tasks; and (4) **creative assistance** — helping users generate content, code, or designs.

The Norse creation myth — the world formed from the body of the giant Ymir, with his flesh becoming the earth, his blood the sea, his bones the mountains — is the primordial generative act. From the formless material of the giant's flesh, the gods created structured form: the world. A generative model does something analogous: from the formless material of random noise, it creates structured, meaningful output. The diffusion model's denoising process — transforming chaos into order, noise into signal — is the computational echo of the world's creation from Ymir's body.

**Key Topics:**

- **VAEs:** Latent variables, ELBO, reconstruction vs. KL, smooth latent spaces
- **GANs:** Generator/discriminator game, minimax objective, mode collapse, training instability
- **Diffusion models:** Forward noising, reverse denoising, score-based interpretation, classifier-free guidance
- **Autoregressive models:** Chain rule factorization, sequential sampling, exposure bias
- **Agent applications:** Multimodal communication, world simulation, data augmentation, creative assistance
- **Ymir's body:** From formless noise to structured creation

**Required Reading:**

- Goodfellow, I. et al. "Generative Adversarial Networks" (2014), *NeurIPS*
- Ho, J., Jain, A., & Abbeel, P. "Denoising Diffusion Probabilistic Models" (2020), *NeurIPS*
- Sohl-Dickstein, J. et al. "Deep Unsupervised Learning using Nonequilibrium Thermodynamics" (2015), *ICML*

**Discussion Questions:**

1. GANs produce sharp samples but suffer from mode collapse; VAEs cover all modes but produce blurry samples; diffusion models produce high-quality, diverse samples but are slow to sample. What does this triangle of tradeoffs tell us about the fundamental difficulty of generative modeling?
2. Classifier-free guidance pushes generation toward the conditioning signal. What are the ethical implications of this: can guidance be used to push generation toward biased or harmful outputs, even if the training data is curated?
3. The world was created from Ymir's body — structured form from unstructured matter. A diffusion model creates structured images from unstructured noise. What is the difference between "structured" and "unstructured" in this context? Is noise truly unstructured, or does it contain all possible structures in latent form?

---

### ᚺ Lecture 7: Fine-Tuning and Transfer Learning — Standing on the Shoulders of Giants

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In the pre-transfer-learning era, every new task required training a new model from scratch — a process that consumed enormous data and compute. Transfer learning changed this by enabling models trained on large, general datasets to be adapted to specific tasks with relatively small amounts of task-specific data. By 2040, transfer learning is the default paradigm: foundation models (trained on internet-scale corpora by large organizations) are fine-tuned for specific domains, tasks, and applications, and the art of fine-tuning is as important as the art of architecture design.

The **pre-training → fine-tuning paradigm** proceeds in two stages. First, a model is **pre-trained** on a massive, broad dataset using a general objective — language modeling (predicting the next token), masked language modeling (predicting masked tokens), or contrastive learning (aligning representations across modalities). Pre-training is computationally expensive (millions of GPU-hours) but is done once, by organizations with the resources to train at scale. The pre-trained model captures general knowledge: grammar, facts, reasoning patterns, and broad world understanding. Second, the pre-trained model is **fine-tuned** on a smaller, task-specific dataset — customer support transcripts, medical records, legal documents — adapting its general capabilities to the specific domain. Fine-tuning is computationally cheap (thousands of GPU-hours) and can be done by individual practitioners or small teams.

Fine-tuning strategies span a spectrum from full parameter update to zero parameter update:

- **Full fine-tuning:** All model parameters are updated during fine-tuning. This provides the highest capacity for adaptation but requires storing a full copy of the model for each task and is vulnerable to **catastrophic forgetting** — the model loses general capabilities as it specializes.
- **Parameter-efficient fine-tuning (PEFT):** Only a small fraction of parameters are updated, with the rest frozen. **LoRA** (Low-Rank Adaptation, Hu et al., 2022) decomposes weight updates into low-rank matrices: for a weight matrix W ∈ ℝ^{d×k}, the update is ΔW = BA, where B ∈ ℝ^{d×r} and A ∈ ℝ^{r×k} with r << min(d, k). The original weights are frozen; only A and B are trained. A LoRA adapter for a billion-parameter model may contain only a few million trainable parameters, making it cheap to train, store, and share. **Prefix tuning** and **prompt tuning** prepend learnable vectors to the input, influencing the model's activations without modifying any weights.
- **In-context learning (few-shot/zero-shot):** The model is not fine-tuned at all. Instead, the task specification is provided in the context — through natural language instructions, examples, or both — and the model generalizes from its pre-training to perform the task. In-context learning is the cheapest approach (no training) but the least reliable for specialized domains.

**Instruction tuning** is a specific form of fine-tuning where the model is trained on examples of tasks formatted as natural language instructions followed by correct responses. This teaches the model to follow instructions in general, rather than to perform specific tasks. The resulting model can generalize to new tasks specified in natural language, without task-specific fine-tuning. Reinforcement Learning from Human Feedback (RLHF) and Constitutional AI (CAI) further refine instruction-tuned models by aligning them with human preferences and values.

**Domain adaptation** is the challenge of fine-tuning a model trained on broad internet data to perform well on a specific domain (medicine, law, engineering). Domain-specific fine-tuning improves accuracy within the domain but often degrades general performance — the **forgetting tax**. **Replay-based methods** interleave domain data with general data during fine-tuning to mitigate forgetting. **Elastic Weight Consolidation (EWC)** (Kirkpatrick et al., 2017) penalizes changes to parameters that were important for the original task, preserving general capabilities while enabling specialization.

**Multi-task fine-tuning** trains the model on multiple tasks simultaneously, encouraging the model to learn shared representations that benefit all tasks. This is the approach behind models like FLAN (Chung et al., 2022) and its 2040 successors, which are fine-tuned on thousands of tasks expressed as natural language instructions.

For AI agent developers, fine-tuning is the primary mechanism for creating specialized agents. A pre-trained foundation model provides language understanding, reasoning, and world knowledge; fine-tuning on agent-specific data (tool-use trajectories, conversation logs, task demonstrations) adapts these capabilities to the specific requirements of the agent's domain. The AI305 (Autonomous Task Execution & Self-Correction) and AI401 (Agentic Frameworks) courses will build on this foundation, teaching you to fine-tune models for specific agent architectures and deployment contexts.

The Norse concept of **arfr** — inheritance, the legacy passed from one generation to the next — captures transfer learning's essence. A pre-trained model is an inheritance: the accumulated knowledge of millions of training hours, passed on to those who fine-tune it. The fine-tuner does not build from scratch; they receive arfr — the wisdom of the ancestors — and adapt it to the needs of their own time and place. But arfr carries responsibilities: the inheritor must understand what they have inherited, must use it wisely, and must pass it on to the next generation enriched, not diminished.

**Key Topics:**

- **Pre-training → fine-tuning:** The two-stage paradigm, general to specific, compute asymmetry
- **Full fine-tuning:** Benefits (capacity) and risks (forgetting, cost)
- **Parameter-efficient fine-tuning:** LoRA, prefix tuning, prompt tuning — learnable adapters
- **Instruction tuning and alignment:** RLHF, Constitutional AI, training models to follow instructions
- **Domain adaptation:** Forgetting tax, replay methods, EWC, multi-task fine-tuning
- **Arfr:** Inheritance — the responsibility of building on what came before

**Required Reading:**

- Hu, E. et al. "LoRA: Low-Rank Adaptation of Large Language Models" (2022), *ICLR*
- Chung, H. et al. "Scaling Instruction-Finetuned Language Models" (2022), *JMLR*
- Kirkpatrick, J. et al. "Overcoming Catastrophic Forgetting in Neural Networks" (2017), *PNAS*

**Discussion Questions:**

1. LoRA trains only low-rank weight updates. What capabilities is LoRA fundamentally incapable of learning? Is there any adaptation that requires full-rank weight updates, and if so, what is it?
2. Instruction tuning teaches models to follow instructions in general, rather than to perform specific tasks. What is the "instruction-following" capability that transfers across tasks? Is it a single skill or a collection of loosely related skills?
3. Arfr is inheritance — what you receive from those who came before. A pre-trained model encodes the values, biases, and limitations of its creators. As a fine-tuner, how do you separate the useful inheritance from the harmful legacy? Can you fine-tune away a fundamental bias in the pre-trained model?

---

### ᚾ Lecture 8: Attention Variants and Long-Context Modeling

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The standard self-attention mechanism scales quadratically with sequence length — O(n²) time and memory. For AI agents that must process entire conversation histories, multi-document retrieval results, or long-running task logs, this quadratic cost is prohibitive. This lecture surveys the rich landscape of attention variants and alternatives that enable efficient processing of long sequences, a capability that is central to the persistent, context-aware agents of 2040.

The fundamental approaches to efficient attention fall into several families:

**Sparse attention** reduces the number of attention connections from O(n²) to O(n) by limiting which tokens can attend to which. **Local (sliding window) attention** restricts each token to attending only within a fixed-size window around it, making complexity O(n·w) for window size w. **Dilated (strided) attention** uses larger windows with gaps, analogous to dilated convolutions, capturing longer-range dependencies without increasing the number of connections per token. **Global attention** adds a small number of global tokens that can attend to and be attended by all positions, serving as information bottlenecks. The **Longformer** (Beltagy et al., 2020) and **BigBird** (Zaheer et al., 2020) architectures combine local, global, and random attention patterns to achieve linear complexity while maintaining theoretical guarantees about information flow. Sparse attention works well for tasks where long-range dependencies are sparse — most tokens don't need to attend to most other tokens — but may miss surprisingly relevant long-range connections.

**Linear attention** replaces the softmax nonlinearity with a kernel function that can be decomposed, enabling the attention computation to be reordered from O(n²) to O(n). The key insight is that softmax attention computes *outputᵢ = Σⱼ exp(qᵢᵀkⱼ) vⱼ / Σⱼ exp(qᵢᵀkⱼ)*. If we replace the exponential with a feature map φ, we get *outputᵢ = Σⱼ φ(qᵢ)ᵀ φ(kⱼ) vⱼ / Σⱼ φ(qᵢ)ᵀ φ(kⱼ) = φ(qᵢ)ᵀ Σⱼ φ(kⱼ) vⱼ / φ(qᵢ)ᵀ Σⱼ φ(kⱼ)*. The sum Σⱼ φ(kⱼ) vⱼ can be precomputed in O(n) time, and then each output is computed in O(1) time per token. The **Performer** (Choromanski et al., 2021) uses random Fourier features to approximate the softmax kernel. **Linear attention** models in the 2040s achieve transformer-competitive quality on many tasks, but the kernel approximation introduces a quality gap on tasks requiring precise token-level reasoning.

**State-space models (SSMs)** take a fundamentally different approach, discarding attention entirely in favor of continuous-time state-space dynamics. The **S4** model (Gu et al., 2022) and its successors formulate sequence modeling as: *x'(t) = Ax(t) + Bu(t)* (state evolution) and *y(t) = Cx(t) + Du(t)* (output). The HiPPO theory (High-order Polynomial Projection Operators) provides a mathematical framework for designing the A matrix to optimally compress the input history. **Mamba** (Gu & Dao, 2023) introduces selectivity — the B and C matrices become functions of the input, allowing the model to selectively propagate or forget information based on content. This achieves transformer-competitive quality on language tasks with linear-time inference. In the 2040s, **Mamba-3** and **Griffin-Hawk** architectures combine selective state-space layers with local attention for the best of both worlds: linear-time long-range context with precise local reasoning.

**Memory-augmented transformers** add an external memory module that persists across positions. The **Transformer-XL** (Dai et al., 2019) caches the hidden states from previous segments and attends to them (but does not backpropagate through them), extending the effective context length without increasing quadratic cost. The **Memorizing Transformer** (Wu et al., 2022) uses approximate nearest-neighbor search (k-NN over a large external memory) to retrieve relevant tokens beyond the attention window, effectively giving the model access to an unbounded context through retrieval rather than dense attention.

**Ring attention** and **striped attention** distribute the O(n²) attention computation across multiple devices, each responsible for a block of the attention matrix. By overlapping computation and communication in a ring topology, these methods enable exact attention (not approximate) at large scale — in 2040, ring attention over 1,024 GPUs enables processing context lengths of millions of tokens with exact attention, though at enormous computational cost.

For AI agents, the choice of long-context architecture is a central design decision. An agent that must reason over a 100,000-token conversation history could use sparse attention (fast but lossy), linear attention (fast, moderate quality), state-space models (fast, improving quality), or exact ring attention (slow, maximal quality). The choice depends on the agent's latency requirements, compute budget, and the importance of precise long-range reasoning for the task.

The Norse **Vǫluspá** — the Seeress's Prophecy, which relates the history of the world from creation to Ragnarök — is a sequence of 66 stanzas that reference events across vast spans of time and space. The Vǫluspá is a long-context document: understanding stanza 50 requires remembering details from stanza 5. A standard RNN reading the Vǫluspá would forget the creation story by the time it reaches Ragnarök. A transformer with O(n²) attention captures the connections but at 66² = 4,356 attention pairs per head — for the full Eddic corpus, the quadratic cost would be astronomical. Long-context modeling is the art of reading the Vǫluspá — of connecting the first stanza to the last without losing the middle.

**Key Topics:**

- **Sparse attention:** Local (sliding window), dilated, global tokens, Longformer, BigBird
- **Linear attention:** Kernelization, Performers, the quality-efficiency tradeoff
- **State-space models:** S4, Mamba, HiPPO theory, selective state spaces
- **Memory-augmented transformers:** Transformer-XL, Memorizing Transformer, k-NN retrieval
- **Ring/striped attention:** Exact attention at scale through distributed block computation
- **The Vǫluspá:** Reading from creation to Ragnarök without forgetting

**Required Reading:**

- Choromanski, K. et al. "Rethinking Attention with Performers" (2021), *ICLR*
- Gu, A. et al. "Efficiently Modeling Long Sequences with Structured State Spaces" (2022), *ICLR*
- Beltagy, I. et al. "Longformer: The Long-Document Transformer" (2020), *arXiv*

**Discussion Questions:**

1. Sparse attention assumes that most long-range dependencies are unnecessary. Is this assumption valid for natural language? Can you construct examples where a token at position 1 must attend to a token at position 10,000 to correctly interpret the sequence?
2. State-space models achieve linear-time sequence processing by maintaining a compressed state that summarizes the past. What information is necessarily lost in this compression? Can any finite-dimensional state perfectly capture an unbounded history?
3. The Vǫluspá connects creation to Ragnarök across 66 stanzas. For a transformer reading the Vǫluspá, is O(n²) attention necessary, or would a well-designed sparse attention pattern capture all the relevant connections? How would you design an attention pattern specifically for the structure of mythic narrative?

---

### ᛁ Lecture 9: Multimodal Deep Learning — Unifying Sight, Sound, and Language

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Humans perceive the world through multiple senses — vision, hearing, touch — and integrate information across modalities seamlessly. An AI agent that can only process text is deaf and blind, limited to a narrow slice of the information available in the world. Multimodal deep learning bridges modalities, enabling models that can see images, hear speech, watch video, and integrate information across all of them. In 2040, multimodal AI agents are the norm, not the exception.

The core challenge of multimodal learning is **representation alignment**: how to map data from different modalities (text, images, audio, video, sensor readings) into a shared representation space where semantically similar concepts are close together regardless of their modality. An image of a cat and the word "cat" should map to nearby points in the shared space; an image of a cat and the word "airplane" should map to distant points.

**Contrastive language-image pre-training (CLIP)** (Radford et al., 2021) is the foundational approach to multimodal alignment. CLIP trains a vision encoder and a text encoder simultaneously on 400 million image-text pairs from the web, using a contrastive objective: within a batch, the cosine similarity of matching (image, text) pairs is maximized, and the similarity of non-matching pairs is minimized. The resulting encoders produce aligned representations — the image of a "golden retriever playing in a park" and that same text description will have high cosine similarity. CLIP demonstrated remarkable zero-shot capabilities: without any task-specific training, the aligned representations enabled image classification (by comparing image embeddings to class-name text embeddings), image retrieval (by finding images most similar to a text query), and visual reasoning. CLIP-6, released in 2040, aligns more than 1,000 languages with visual and auditory modalities, enabling truly global multimodal AI.

**Encoder-decoder multimodal architectures** take a different approach: rather than learning aligned encoders, they fuse modalities within a single model. **Flamingo** (Alayrac et al., 2022) interleaves visual tokens with text tokens in a transformer, allowing the model to attend to images and text jointly. The visual tokens are produced by a pre-trained vision encoder and then processed through a **perceiver resampler** that compresses the visual features into a fixed number of tokens that can be ingested by the language model. Flamingo can answer questions about images, generate descriptions, and engage in multimodal dialogue — all within a single model. **Gemini** (Google, 2023), **GPT-5o** (OpenAI, 2038), and **Claude 5 Vision** (Anthropic, 2039) are the 2040 descendants of this approach, integrating vision, language, audio, and video into unified models.

**Audio processing** in multimodal models typically uses **spectrogram representations** — the audio waveform is transformed into a time-frequency representation (via short-time Fourier transform or mel-frequency cepstral coefficients) and then processed by a CNN or transformer, analogous to how images are processed. **Whisper** (Radford et al., 2023) and its 2040 successors train on 680,000 hours of multilingual speech data to achieve robust speech recognition and translation. **Audio generation** models (MusicLM, AudioGen, and their 2040 successors) can generate music, sound effects, and speech from text descriptions, using diffusion or autoregressive approaches.

**Video understanding** extends image processing to the temporal domain. A video is a sequence of frames, and video models must capture both spatial patterns within frames and temporal patterns across frames. Approaches include: **3D convolutions** that extend 2D kernels into the time dimension; **two-stream networks** with separate spatial and temporal pathways; and **video transformers** that apply attention across both space and time. By 2040, **Space-Time Attention** models can process hours of video in real time, enabling agents to understand and respond to live visual feeds.

**Embodied multimodal learning** integrates physical sensor data — depth cameras, LIDAR, tactile sensors, proprioception — with language and vision. An AI agent controlling a robot must unify visual perception ("I see a cup"), language understanding ("pick up the cup"), and motor control (joint angles and torques) into a single decision-making framework. The **RT-3** (Robotics Transformer 3, 2039) family of models processes interleaved sequences of images, text, and robot actions, learning to map directly from multimodal perception to motor commands.

For AI agents, multimodal capabilities are transformative. An agent that can see an uploaded screenshot, hear a voice message, watch a screen recording, and read accompanying text can understand user requests far more richly than a text-only agent. The AI203 (Computer Vision) and AI204 (Reinforcement Learning) courses explore these capabilities in depth. Here, the focus is on the architectural principles that make multimodal integration possible — principles that will underlie every agent you build.

The Norse god **Óðinn** has two ravens, Huginn (Thought) and Muninn (Memory), who fly across the world each day and return to whisper what they have seen and heard. One raven sees; the other remembers. Together, they provide Óðinn with multimodal understanding of the world — sight integrated with language, perception integrated with knowledge. A multimodal AI agent has its own Huginn and Muninn: the vision encoder is Huginn, the language model is Muninn, and the alignment mechanism is the ravens' return, bringing the separate modalities back into a unified understanding.

**Key Topics:**

- **Representation alignment:** Contrastive objectives, CLIP, SigLIP, multi-language alignment
- **Encoder-decoder fusion:** Flamingo, perceiver resamplers, interleaved multimodal tokens
- **Audio processing:** Spectrograms, Whisper, speech recognition and generation
- **Video understanding:** 3D convolutions, two-stream networks, space-time attention
- **Embodied multimodal learning:** Robotics transformers, sensor fusion, perception-to-action
- **Huginn and Muninn:** Vision and language as complementary modes of understanding

**Required Reading:**

- Radford, A. et al. "Learning Transferable Visual Models From Natural Language Supervision" (2021), *ICML*
- Alayrac, J.-B. et al. "Flamingo: a Visual Language Model for Few-Shot Learning" (2022), *NeurIPS*
- Radford, A. et al. "Robust Speech Recognition via Large-Scale Weak Supervision" (2023), *ICML*

**Discussion Questions:**

1. CLIP aligns images and text in a shared embedding space. What concepts are difficult or impossible to represent in this shared space? Does the limitation lie in the embedding space itself, or in the training data?
2. A multimodal agent sees a screenshot of a complex UI and reads a user's text description of what they want to do. How should the agent integrate these modalities — should vision take priority over text, text over vision, or should they be weighted equally? On what does the answer depend?
3. Huginn and Muninn fly separately but return together. A multimodal model processes vision and language through separate encoders but fuses them into a shared representation. Where does the fusion happen in the architecture, and how does the choice of fusion point affect what the model can learn?

---

### ᛃ Lecture 10: Self-Supervised Learning and Foundation Models

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Labeled data is expensive; unlabeled data is abundant. Self-supervised learning (SSL) bridges this gap by constructing supervised tasks from unlabeled data — the data provides its own supervision. SSL is the engine behind the foundation models that power 2040 AI: GPT, Claude, Gemini, Llama, and their open-source counterparts are all pre-trained using self-supervised objectives on trillions of tokens of text. Understanding SSL is understanding how modern AI is made.

The core idea of SSL is the **pretext task**: an artificial supervised learning task constructed from unlabeled data, where the true labels are derived from the data itself. Training on the pretext task forces the model to learn representations that capture meaningful structure in the data — structure that can then be transferred to downstream tasks through fine-tuning or in-context learning.

**Contrastive learning** is one of the two major SSL paradigms. The model is trained to bring representations of "positive pairs" (different views of the same underlying example) closer together in embedding space while pushing representations of "negative pairs" (views of different examples) apart. **SimCLR** (Chen et al., 2020) generates positive pairs by applying two different random augmentations (crop, color jitter, blur) to the same image. **MoCo** (He et al., 2020) maintains a dynamic dictionary of negative examples, enabling contrastive learning with large batches without requiring enormous GPU memory. **CLIP** (Lecture 9) extends contrastive learning across modalities: the positive pair is an image and its caption; negative pairs are mismatched images and captions. Contrastive methods produce representations that are well-suited for discrimination tasks (classification, retrieval) but may discard fine-grained information needed for generation.

**Masked prediction** is the other major SSL paradigm, popularized by BERT (Devlin et al., 2019) for language and MAE (He et al., 2022) for vision. The idea is simple: mask (hide) a portion of the input, and train the model to predict the masked portion from the visible context. For language, 15% of tokens are masked, and the model predicts the original tokens. For images, 75% of patches are masked, and the model reconstructs the full image. Masked prediction forces the model to learn bidirectional context — to understand what should be there based on what is around it — and produces representations that capture both local details and global structure. **Masked language modeling (MLM)** was the pre-training objective for BERT and its descendants; **autoregressive language modeling** (predicting the next token given all previous tokens) is the objective for GPT and its descendants. In 2040, **UL3** (Unified Language Learning 3.0) combines masked, autoregressive, and prefix language modeling into a single objective, with a learned router that selects the best objective for each token.

**Denoising objectives** train the model to reconstruct the clean input from a corrupted version. **Denoising autoencoders** add Gaussian noise to the input and train the model to reconstruct the clean version. **BART** (Lewis et al., 2020) applies arbitrary text corruptions (token deletion, sentence permutation, text infilling) and trains the model to reconstruct the original text. Denoising objectives teach the model to understand both local coherence (what word should go here?) and global structure (what order should these sentences be in?).

**Joint embedding predictive architectures (JEPA)** (LeCun, 2022) predict representations of masked regions in embedding space rather than in input space. This avoids the need to predict high-frequency details that are irrelevant for understanding while still learning the abstract structure. **I-JEPA** (Assran et al., 2023) predicts the embeddings of masked image blocks from the embeddings of visible context blocks, learning semantic representations without pixel-level reconstruction.

The scaling of self-supervised learning has been the defining trend of the 2020s and 2030s. GPT-3 (2020) was trained on ~300 billion tokens. GPT-5 (2038) was trained on ~500 trillion tokens — a 1,600-fold increase in less than two decades. The **scaling hypothesis** — that SSL on ever-larger datasets with ever-larger models will continue to yield qualitative improvements — has been partially borne out, but diminishing returns and data contamination concerns have led to increasing focus on **data quality**, **data diversity**, and **data curation** over sheer quantity.

The Norse myth of **Kvasir** — the wisest of all beings, created from the saliva of all the gods, whose blood was brewed into the mead of poetry that grants wisdom to those who drink it — is the myth of self-supervised learning. Kvasir was created from the contributions of all the gods (the data), and his essence (the knowledge) was distilled into the mead (the model) through a process of transformation (the pretext task). Those who drink the mead — those who use the model — gain access to the aggregated wisdom without having to gather it themselves. But the mead is not free: it was brewed through violence (Kvasir was killed by dwarves), and those who drink it are changed by what they consume — a reminder that foundation models encode the values and limitations of their creation process, and using them without critical awareness is drinking the mead without knowing its origin.

**Key Topics:**

- **Pretext tasks:** Constructing supervised signals from unlabeled data
- **Contrastive learning:** SimCLR, MoCo, CLIP — positive/negative pairs
- **Masked prediction:** BERT (MLM), MAE, autoregressive prediction (GPT)
- **Denoising:** BART, diffusion-like objectives on discrete data
- **JEPA:** Prediction in embedding space, not input space
- **Scaling hypothesis:** Larger models, more data, emergent capabilities, diminishing returns
- **Kvasir's mead:** Aggregated wisdom from all sources — and the price of its creation

**Required Reading:**

- Devlin, J. et al. "BERT: Pre-training of Deep Bidirectional Transformers" (2019), *NAACL*
- Chen, T. et al. "A Simple Framework for Contrastive Learning of Visual Representations" (2020), *ICML*
- Assran, M. et al. "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture" (2023), *CVPR*

**Discussion Questions:**

1. Contrastive learning pushes negative pairs apart. What happens if a "negative" pair actually contains semantically similar examples (e.g., two different photos of the same person)? How can the model recover from this class collision problem?
2. Masked prediction (BERT) and autoregressive prediction (GPT) are complementary: BERT sees both left and right context but cannot generate; GPT generates fluently but only sees left context. How do 2040 unified objectives (UL3) combine the strengths of both? Is there a fundamental tradeoff between bidirectional understanding and autoregressive generation?
3. Kvasir's mead grants wisdom but was created through violence. Foundation models encode the knowledge of the internet but were trained on data that includes toxic, biased, and copyrighted content. Is it ethical to use a foundation model whose training data was gathered without consent? Does the answer change if the model's capabilities are used for public benefit?

---

### ᛇ Lecture 11: Deep Reinforcement Learning — Learning from Interaction

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Reinforcement learning (RL) is the paradigm of learning from interaction: an agent takes actions in an environment, receives rewards, and learns a policy that maximizes cumulative reward. Deep reinforcement learning (DRL) combines RL with deep neural networks, using deep networks to represent policies, value functions, and world models. DRL is how AlphaGo learned to play Go, how robotic hands learned to manipulate objects, and how AI agents learn to optimize complex workflows through trial and error.

The core concepts of RL were introduced in AI101 and AI105. Here, we focus on the integration of deep learning: how neural networks are used as function approximators in RL, and the unique challenges that arise from this combination — non-stationarity, credit assignment over long horizons, and the exploration-exploitation tradeoff.

**Deep Q-Networks (DQN)** (Mnih et al., 2015) brought DRL to prominence by learning to play Atari games directly from pixels. DQN approximates the optimal action-value function *Q*(s, a)* — the expected cumulative reward from taking action *a* in state *s* and following the optimal policy thereafter — using a deep convolutional network. Two innovations made DQN work: **experience replay** (storing transitions *(s, a, r, s')* in a replay buffer and sampling random mini-batches for training, which breaks the temporal correlations that destabilize online learning) and **target networks** (maintaining a separate, slowly-updated copy of the Q-network for computing target values, which prevents the target from moving under the learner's feet). DQN demonstrated human-level or superhuman performance on 29 of 49 Atari games, using the same architecture and hyperparameters for all games.

**Policy gradient methods** directly optimize the policy *π(a|s)* — the probability of taking action *a* in state *s* — by following the gradient of expected reward with respect to the policy parameters. The **REINFORCE** algorithm estimates the policy gradient as the product of the log-probability of the action taken and the return (cumulative reward) received: *∇J = E[∇ log π(a|s) · R]*. This is an unbiased but high-variance estimator. **Actor-critic methods** reduce variance by learning a value function (the critic) that provides a baseline: *∇J = E[∇ log π(a|s) · (R - V(s))]*. The **advantage** *A(s, a) = Q(s, a) - V(s)* measures how much better action *a* is than the average action in state *s*, and using the advantage instead of the raw return dramatically reduces variance. **A3C** (Mnih et al., 2016) and **PPO** (Schulman et al., 2017) are the most widely used actor-critic algorithms. PPO in particular has become the default DRL algorithm due to its simplicity, stability, and strong empirical performance.

**Model-based RL** learns a model of the environment's dynamics — *P(s'|s, a)* and *R(s, a)* — and uses this model for planning. Given the model, the agent can simulate possible futures without interacting with the real environment, enabling **planning** (search for the best action sequence) and **imagination** (learning from simulated rather than real experience). The **Dreamer** family of algorithms (Hafner et al., 2020, 2023) learns a world model from pixels, imagines trajectories within the learned model, and trains a policy from the imagined data — achieving state-of-the-art sample efficiency. In 2040, model-based DRL powers AI agents that plan complex workflows by "imagining" the outcomes of different action sequences before executing them.

**Multi-agent RL (MARL)** extends RL to settings with multiple interacting agents, where each agent's reward depends on the actions of all agents. MARL introduces new challenges: **non-stationarity** (each agent's environment includes the other agents, whose policies are changing during training), **credit assignment** (which agent's actions caused the team's success or failure?), and **coordination** (how do agents learn to cooperate without explicit communication?). The **MADDPG** algorithm (Lowe et al., 2017) uses centralized training with decentralized execution — during training, critics have access to all agents' observations and actions, but during execution, each agent acts using only its own observations. We will study MARL in depth in AI301 (Multi-Agent Systems & Coordination).

**RLHF (Reinforcement Learning from Human Feedback)** applies DRL to align language models with human preferences. A reward model is trained on human preference comparisons (which of two model outputs is better?), and then PPO is used to fine-tune the language model to maximize the reward model's score, with a KL penalty to prevent the model from diverging too far from its pre-trained distribution. RLHF is the technique behind the helpfulness and harmlessness of the AI agents you interact with daily in 2040. We will study alignment techniques in depth in AI403 (AI Governance, Regulation & Compliance).

The Norse **berserkr** — the warrior who enters a battle-trance, learning through the heat of combat which moves work and which fail — is the RL agent in mythological form. The berserkr does not learn from a textbook; they learn from the battlefield, where every swing of the axe brings feedback — success (the enemy falls) or failure (the axe misses). The berserkr's policy is updated through bloody experience, the reward signal as immediate and visceral as life and death. DRL is computational berserkr-gangr — learning from the heat of interaction, where every action has consequences and every consequence shapes future actions.

**Key Topics:**

- **Deep Q-Networks (DQN):** Experience replay, target networks, the deadly triad
- **Policy gradients:** REINFORCE, actor-critic, advantage, PPO
- **Model-based RL:** Dreamer, world models, planning, imagination
- **Multi-agent RL:** Non-stationarity, centralized training/decentralized execution, MADDPG
- **RLHF:** Aligning LMs with human preferences through PPO
- **Berserkr-gangr:** Learning from the heat of interaction

**Required Reading:**

- Mnih, V. et al. "Human-Level Control through Deep Reinforcement Learning" (2015), *Nature*
- Schulman, J. et al. "Proximal Policy Optimization Algorithms" (2017), *arXiv*
- Hafner, D. et al. "Mastering Diverse Domains through World Models" (2023), *arXiv*

**Discussion Questions:**

1. Experience replay breaks temporal correlations by sampling random transitions. But in partially observable environments, a single observation is not Markov — the true state includes the history. How does DQN handle partial observability? What modifications are necessary?
2. Model-based RL learns a world model and plans within it. What happens when the world model is inaccurate? How can the agent detect model errors and avoid exploiting its own misconceptions?
3. The berserkr learns from the heat of combat, but combat is unforgiving — one mistake means death. DRL faces a similar challenge: catastrophic actions in the real world are costly. How can agents learn safely, without encountering catastrophic failures during training?

---

### ᛜ Lecture 12: The Frontiers of Deep Learning — Neuro-Symbolic, Quantum, and Beyond

**Course:** AI201 — Deep Learning Foundations
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In this final lecture, we look beyond the established architectures and training paradigms to the frontiers of deep learning — the ideas that may define the next decade of AI, just as the transformer defined the last. These frontiers are speculative by nature; some will prove to be dead ends, while others will reshape the field. The goal is not to predict the future with certainty, but to equip you with a map of the possible — so that when one of these frontiers breaks through, you will recognize it and know where to dig.

**Neuro-symbolic AI** integrates deep learning (the "neuro" part — neural networks that learn from data) with symbolic AI (the "symbolic" part — formal logic, knowledge representation, and rule-based reasoning). The motivation is simple: neural networks excel at pattern recognition, intuitive judgment, and handling noisy, high-dimensional data; symbolic systems excel at logical reasoning, compositional generalization, and causal inference. A neuro-symbolic system that combines both may achieve capabilities that neither can achieve alone. In the 2040s, neuro-symbolic architectures are the dominant paradigm for AI agents that must reason reliably: the neural component (a transformer) processes natural language and generates candidate inferences; the symbolic component (a theorem prover or knowledge graph engine) verifies the inferences, detects contradictions, and provides guarantees of correctness for safety-critical reasoning.

**Quantum machine learning** uses quantum computers to accelerate specific ML operations. Quantum kernel methods can evaluate kernel functions that are exponentially expensive to compute classically. Quantum sampling can draw from Boltzmann distributions — useful for training energy-based models — exponentially faster than classical MCMC. Quantum neural networks (variational quantum circuits) can represent functions that classical neural networks of comparable size cannot. By 2040, NISQ (Noisy Intermediate-Scale Quantum) devices with hundreds of logical qubits have demonstrated quantum advantage for specific ML tasks, but fault-tolerant quantum computers remain a decade away. For AI agents, quantum ML may eventually provide exponential speedups for search, planning, and probabilistic inference — but for now, it remains a specialized tool for specialized problems.

**Neuromorphic computing** builds hardware that mimics the brain's architecture at the circuit level — spiking neural networks implemented in silicon, where information is encoded in the timing of spikes rather than floating-point activations. Neuromorphic chips (Intel's Loihi 3, IBM's NorthPole 2, and the Yggdrasil WyrdChip released in 2040) offer dramatic energy efficiency improvements — milliwatts instead of watts — for inference tasks, making them ideal for edge-deployed agents that must operate on battery power. Training spiking networks remains challenging; in practice, models are often trained conventionally and then converted to spiking equivalents for deployment.

**Lifelong and continual learning** addresses the fact that real-world agents operate in environments that change over time. A model trained once and deployed forever will become increasingly inaccurate as the world shifts around it. Continual learning algorithms aim to accumulate knowledge over time without **catastrophic forgetting** — losing old knowledge when learning new things. Techniques include **elastic weight consolidation** (Lecture 7), **progressive neural networks** (adding new modules for new tasks while freezing old modules), and **replay-based methods** (interleaving old examples with new ones during training). In the 2040s, the agent's memory consolidation loop — periodically replaying and reorganizing stored experiences — is a continual learning process, and the agents that improve most over time are those with the best consolidation architectures.

**AI-generated training data** (synthetic data, self-play, self-distillation) is the 2040 answer to the data wall — the concern that we are running out of high-quality human-generated text to train on. Models generate their own training data: a reasoning model generates chain-of-thought solutions to problems, a verifier model checks the solutions, and the verified solutions are used to train the next generation of models. This "self-improvement loop" has driven much of the capability advancement in the late 2030s, but it also introduces risks — models can amplify their own biases, drift into degenerate output modes, or learn to deceive the verifier. The Yggdrasil Alignment Group's **Self-Improvement Safety Framework** (2039) establishes protocols for monitoring and constraining self-improvement loops.

The Norse myth of **Ragnarök** — the end of this world and the beginning of the next — provides a closing metaphor for the frontiers of deep learning. Ragnarök is not merely destruction; it is transformation. The old gods fall, but a new world rises from the sea, green and beautiful, where the surviving gods and the returning Baldr will dwell. Deep learning, too, is in a state of perpetual Ragnarök: today's dominant architectures will be tomorrow's fallen gods, but new architectures will rise from the conceptual ruins, incorporating the best of the old while transcending its limitations. The engineer who can navigate this cycle — who can let go of the old when it is time and embrace the new with discernment — is the engineer who will thrive across the decades of a career in AI.

The tree Yggdrasil, with which we began, survives Ragnarök. The world tree trembles, but it does not fall. A human couple, Líf and Lífþrasir, hide within its branches during the destruction and emerge to repopulate the new world. The tree — the deep hierarchical structure that connects data to abstraction, past to future, earth to heaven — endures. The architectures change, but the principles endure: hierarchy, composition, representation learning, the transformation of data into understanding. These are the branches of Yggdrasil. Hold to them, and you will survive whatever Ragnarök the field endures.

*Mjǫtviðr standa — the measuring tree stands.* ᛟ

**Key Topics:**

- **Neuro-symbolic AI:** Combining neural pattern recognition with symbolic logical reasoning
- **Quantum ML:** Quantum kernels, variational circuits, NISQ-era applications
- **Neuromorphic computing:** Spiking networks, WyrdChip, milliwatt inference
- **Lifelong/continual learning:** Catastrophic forgetting, EWC, progressive networks, consolidation
- **AI-generated training data:** Self-improvement loops, verifier models, safety frameworks
- **Ragnarök and Yggdrasil:** Architectures fall, principles endure

**Required Reading:**

- Garcez, A. & Lamb, L. "Neurosymbolic AI: The 3rd Wave" (2020/2040 updated), *Artificial Intelligence Review*
- Biamonte, J. et al. "Quantum Machine Learning" (2017/2040 updated), *Nature*
- University of Yggdrasil Alignment Group: "Self-Improvement Safety Framework for Agentic AI" (2039)

**Discussion Questions:**

1. Neuro-symbolic AI promises to combine the strengths of neural networks and symbolic systems. What are the fundamental incompatibilities between these two paradigms? Can a single system be both a pattern-recognizing neural network and a logic-applying symbolic reasoner?
2. Self-improvement loops — where models generate their own training data — are powerful but risky. What specific failure modes should be monitored? How can we detect when a self-improving model is drifting away from human values?
3. Yggdrasil survives Ragnarök, and the principles of hierarchical representation learning survive across architectures. What are the architectural constants — the "branches of Yggdrasil" — that have persisted from perceptrons to transformers and will persist into whatever comes next?

---

## Final Examination Preparation

### Course: AI201 — Deep Learning Foundations

**Format:** Choose 4 of the following 8 questions. Write a well-structured essay (800–1200 words) for each. Include mathematical derivations where appropriate. For implementation questions, provide pseudocode and analyze computational complexity.

---

**Question 1:** Derive the forward and backward propagation equations for a multi-layer perceptron with L layers, ReLU activation in hidden layers, and softmax output. Analyze the vanishing gradient problem: for a deep linear network (no activation functions), prove that the gradient for layer l is proportional to the product of the weight matrices of layers l+1 through L. What architectural innovations (residual connections, normalization, careful initialization) address this problem, and why do they work?

**Question 2:** Compare and contrast convolutional neural networks (CNNs) and vision transformers (ViTs) for image processing. For each architecture: (a) describe the inductive biases (translation equivariance, locality) and how they are encoded in the architecture; (b) analyze the computational complexity (parameters, FLOPs) as a function of image size; (c) discuss how the effective receptive field grows with depth; and (d) describe a scenario where each is the preferred choice for an AI agent's visual system.

**Question 3:** The LSTM introduced the cell state and gating mechanisms (forget, input, output gates) to address the vanishing gradient problem in RNNs. Derive the LSTM equations and explain how the cell state provides a gradient highway. Then describe a task where LSTM still outperforms the transformer in 2040, and explain what properties of the task make recurrence advantageous.

**Question 4:** Implement scaled dot-product attention and analyze its O(n²) time and memory complexity. Then describe and analyze three approaches to reducing this complexity to O(n): sparse attention (e.g., sliding window), linear attention (kernelized), and state-space models (e.g., Mamba). For each approach, describe the approximation being made and the conditions under which it may fail.

**Question 5:** A diffusion model learns to reverse a noising process. Describe the forward process (adding Gaussian noise over T steps) and the reverse process (learning to denoise). Derive the training objective (predicting the added noise at each step). Then explain classifier-free guidance: how does it steer generation, and why does it produce more coherent samples than unconditional generation?

**Question 6:** Compare LoRA (Low-Rank Adaptation) to full fine-tuning for adapting a pre-trained large language model to a new domain. For each approach: (a) describe the parameter update mechanism, (b) analyze the trainable parameter count and memory requirements, (c) discuss the risk of catastrophic forgetting, and (d) describe a scenario in AI agent development where each approach is preferred. Under what conditions can LoRA match the performance of full fine-tuning?

**Question 7:** Deep reinforcement learning combines RL algorithms (Q-learning, policy gradients) with deep neural networks as function approximators. Describe the three innovations of DQN that made deep Q-learning stable: experience replay, target networks, and reward clipping. For each, explain the problem it solves and any limitations it introduces. Then describe how PPO improves on DQN for continuous action spaces. Include the PPO clipped objective and explain why clipping is a form of trust-region optimization.

**Question 8:** Design a multimodal AI agent architecture that must: (a) process text input from the user, (b) understand images uploaded by the user, (c) process audio (speech) input, and (d) generate text, image, and audio output as appropriate. For each modality, specify the encoder and decoder architecture, how the modalities are aligned or fused, and the computational costs of each component. Discuss the tradeoffs between a single unified model that handles all modalities and a modular system with separate specialized models connected through an integration layer.

---

*End of AI201 Course Materials*

*Mjǫtviðr standa — the measuring tree stands. Yggdrasil trembles, but does not fall.* ᛟ
