# Lecture 5: The Transformer Architecture — Attention Is All You Need

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Week 6 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: The Paper That Broke the World

On June 12, 2017, Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan Gomez, Łukasz Kaiser, and Illia Polosukhin submitted a paper to NeurIPS titled "Attention Is All You Need." The paper introduced the Transformer, a neural network architecture based entirely on self-attention mechanisms, dispensing entirely with the recurrence and convolution that had been the backbone of sequential models.

In the seven years between 2017 and 2024, the Transformer would become the most influential architecture in the history of artificial intelligence. It would be the substrate on which GPT, BERT, DALL-E, AlphaFold, and every major language model was built. It would redefine what "AI" meant to the public, to researchers, and to the venture capital industry. It is, in the view of this historian, the single most important architectural innovation since the perceptron.

And it almost didn't happen. The paper was initially rejected from ICLR 2018. It was accepted at NeurIPS 2017 only after significant revision. The title—bold, almost confrontational—was considered grandiose by reviewers. How charming, in retrospect, that anyone thought "attention is all you need" was an overstatement.

---

## 1. The Problem: Sequential Bottlenecks

### 1.1 The Limitations of RNNs

Before the Transformer, the dominant architectures for sequence modeling were recurrent neural networks (RNNs) and their variants—long short-term memory (LSTM) networks (Hochreiter & Schmidhuber, 1997) and gated recurrent units (GRUs) (Cho et al., 2014).

RNNs process sequences one element at a time, maintaining a hidden state that is updated at each step. This sequential processing creates two fundamental problems:

1. **Computational bottleneck**: Each step must wait for the previous step to complete. For a sequence of length *n*, the computation cannot be parallelized across time steps. This makes RNNs extremely slow to train on long sequences.

2. **Information decay**: Even with gating mechanisms (LSTM, GRU), information from early time steps tends to be lost or confounded as it passes through many processing steps. The hidden state must carry all relevant information from the entire sequence, and the capacity to do so is limited.

These problems were well-understood by 2016. The attention mechanism, introduced by Bahdanau, Cho, and Bengio (2014) for neural machine translation, had partially addressed the information decay problem by allowing the decoder to "attend" to relevant parts of the encoder's hidden states, rather than relying solely on the final hidden state. But Bahdanau's attention was an *addition* to an RNN; it did not replace the sequential bottleneck.

### 1.2 The Question

The question that Vaswani et al. posed was deceptively simple: *Do we need recurrence at all?* If attention mechanisms can learn to focus on relevant parts of a sequence, and if attention can be computed in parallel across all positions, then why not build an architecture entirely out of attention?

The answer, it turned out, was: you don't need recurrence. Attention really is all you need.

---

## 2. The Transformer Architecture

### 2.1 Self-Attention

The core mechanism of the Transformer is **scaled dot-product self-attention**. Given a sequence of input embeddings, the self-attention mechanism computes three vectors for each position:

- **Query** (Q): What am I looking for?
- **Key** (K): What do I contain?
- **Value** (V): What information do I provide?

These are computed as linear projections of the input:

$$Q = XW_Q, \quad K = XW_K, \quad V = XW_V$$

where $X$ is the input matrix and $W_Q, W_K, W_V$ are learned projection matrices. The attention output is:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

The scaling factor $\sqrt{d_k}$ (where $d_k$ is the dimension of the key vectors) prevents the dot products from growing too large, which would push the softmax into regions with vanishingly small gradients.

The crucial property of self-attention is that every position can attend to every other position in a *single operation*. There is no sequential bottleneck; the computation is $O(n^2)$ in sequence length but $O(1)$ in the "depth" of information propagation. A position at the beginning of the sequence can attend to a position at the end with no loss of signal.

### 2.2 Multi-Head Attention

A single attention head learns one pattern of relationships. The Transformer uses **multi-head attention**, running *h* attention heads in parallel, each with its own projection matrices:

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W_O$$

where $\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$

This allows the model to attend to different aspects of the input simultaneously—syntactic relationships, semantic relationships, positional relationships—each captured by a different head.

### 2.3 Positional Encoding

Self-attention is inherently permutation-invariant: it has no notion of order. Since order matters in sequences, the Transformer adds **positional encodings** to the input embeddings. The original paper used sinusoidal positional encodings:

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$

This choice allows the model to learn relative positions, since for any fixed offset $k$, $PE_{pos+k}$ can be represented as a linear function of $PE_{pos}$.

### 2.4 The Full Architecture

The Transformer consists of:

- **Encoder**: A stack of $N$ identical layers, each containing:
  - Multi-head self-attention sublayer
  - Position-wise feed-forward network (two linear transformations with ReLU)
  - Residual connections and layer normalization around each sublayer

- **Decoder**: A stack of $N$ identical layers, each containing:
  - Masked multi-head self-attention (preventing positions from attending to subsequent positions)
  - Multi-head cross-attention over the encoder output
  - Position-wise feed-forward network
  - Residual connections and layer normalization

The original Transformer (for English-to-German translation) used $N=6$, $d_{\text{model}}=512$, $h=8$ attention heads, and $d_{ff}=2048$ in the feed-forward layers. Total parameters: approximately 65 million.

---

## 3. Why the Transformer Worked

### 3.1 Parallelization

The Transformer's most immediate advantage was computational. Because self-attention computes all pairwise interactions in parallel, the architecture can be fully parallelized across positions during training. On modern GPU hardware, this meant orders-of-magnitude faster training compared to RNNs.

This was not merely an engineering convenience. It was a *qualitative* change in what was possible. With RNNs, training on sequences longer than a few hundred tokens was prohibitively slow. With Transformers, the constraint shifted from computation time to GPU memory—still a limiting factor, but one that could be addressed with distributed training, gradient accumulation, and efficient attention variants.

### 3.2 Long-Range Dependencies

The self-attention mechanism provides a *direct* connection between any two positions in the sequence, regardless of distance. In an RNN, information must pass through *O(n)* steps to travel from position *i* to position *j*; in a Transformer, it passes through *O(1)* steps (a single attention operation). This dramatically improved the ability of models to capture long-range dependencies—patterns that span hundreds or thousands of tokens.

### 3.3 The Scaling Hypothesis

Perhaps the most consequential property of the Transformer was not any single architectural feature but its ability to *scale*. The architecture is:

- **Depth-scalable**: Adding more layers improves performance (unlike RNNs, which suffer from diminishing returns)
- **Width-scalable**: Increasing model dimension improves performance
- **Data-scalable**: More training data consistently improves performance
- **Task-agnostic**: The same architecture can be applied to translation, summarization, question answering, and more

This scalability—the subject of Kaplan et al.'s (2020) scaling laws—meant that the Transformer was not merely a better architecture for a specific task; it was a *general-purpose substrate* for learning representations from sequences.

---

## 4. The Immediate Aftermath (2017–2019)

### 4.1 BERT: Bidirectional Understanding

In October 2018, Jacob Devlin et al. at Google published "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." BERT was a Transformer encoder (no decoder) pre-trained on two tasks:

1. **Masked language modeling (MLM)**: Randomly mask 15% of tokens and predict them
2. **Next sentence prediction (NSP)**: Predict whether two sentences are consecutive

After pre-training on a large corpus of English text (BooksCorpus + English Wikipedia, ~3.3 billion words), BERT was fine-tuned on downstream tasks. It set new state-of-the-art results on eleven NLP benchmarks simultaneously.

BERT's significance was twofold. First, it demonstrated the power of *pre-training + fine-tuning*: a model trained on a general language modeling objective could be adapted to specific tasks with minimal additional training. Second, it demonstrated the power of *bidirectional* context—attention over the full sequence in both directions, rather than the left-to-right processing of autoregressive models.

### 4.2 GPT: Autoregressive Generation

In June 2018, OpenAI published "Improving Language Understanding by Generative Pre-Training" (Radford et al.), introducing GPT-1. GPT used only the Transformer *decoder* (with masked self-attention), trained autoregressively to predict the next token.

GPT-1 was, in isolation, less impressive than BERT on downstream benchmarks. But it established the autoregressive paradigm that would prove to be more scalable and more capable: GPT-2 (2019) demonstrated zero-shot learning, GPT-3 (2020) demonstrated few-shot learning, and GPT-4 (2023) demonstrated capabilities that began to approach human-level performance across a wide range of tasks.

The divergence between BERT and GPT—bidirectional understanding vs. autoregressive generation—represents a philosophical choice about what language models should *do*. BERT is an analyzer; GPT is a generator. In the long run, generation proved to be the more powerful paradigm, arguably because generation subsumes understanding: to generate coherent text, a model must understand it.

### 4.3 The Cambrian Explosion

Between 2017 and 2020, the Transformer architecture was applied to virtually every domain in AI:

- **Vision**: ViT (Dosovitskiy et al., 2020) applied the Transformer directly to image patches
- **Audio**: Whisper (Radford et al., 2022) used Transformers for speech recognition
- **Protein structure**: AlphaFold 2 (Jumper et al., 2021) used Transformer-based attention to predict protein structure
- **Music**: Music Transformer (Huang et al., 2018)
- **Reinforcement learning**: Decision Transformer (Chen et al., 2021)
- **Code**: Codex (OpenAI, 2021)

The Transformer became the *lingua franca* of deep learning architecture. Not because it was optimal for every task—convolutional networks remained more parameter-efficient for images, for example—but because it was *good enough* across the board and could be scaled consistently.

---

## 5. The Deeper Significance

### 5.1 Universality Through Attention

The Transformer's success suggests something profound about the nature of representation learning: that a sufficiently flexible attention mechanism, applied at sufficient scale, can learn virtually any pattern that can be expressed in sequential or spatial data. The attention mechanism is, in a sense, a universal approximator of relationships—given enough heads, enough layers, and enough data.

This is analogous to the universal approximation theorem for feedforward networks, but it operates at a higher level of abstraction. The universal approximation theorem says that a sufficiently wide feedforward network can approximate any continuous function. The empirical success of Transformers suggests that a sufficiently deep and wide attention-based network can learn any *structural relationship* in sequential data.

### 5.2 The End of Architecture Engineering

Before the Transformer, a significant fraction of AI research was devoted to designing specialized architectures for specific tasks. LSTMs for sequences, CNNs for images, attention-augmented RNNs for translation. Each domain required its own architecture.

The Transformer challenged this approach. By providing a single, general-purpose architecture that could be adapted to any domain with minimal modification, it shifted the focus from architecture design to *scale*: more data, more compute, more parameters. This was the beginning of the "scaling laws" era, which we will discuss in depth in Lecture 6.

### 5.3 A Note on Hindsight

It is tempting, from the perspective of 2040, to view the Transformer's success as inevitable. It was not. In 2017, many researchers were skeptical that an architecture without recurrence or convolution could handle sequential data effectively. The paper's own reviewers questioned whether the approach would generalize beyond machine translation. The title—"Attention Is All You Need"—was seen as needlessly provocative.

The lesson: major paradigm shifts are almost never recognized as such at the time. They begin as interesting results in specific domains and only gradually reveal their generality. The Transformer was not a single "eureka" moment; it was the seed that required the soil of GPU computing, the rain of internet-scale data, and the sunlight of institutional investment before it could grow into the forest we now inhabit.

---

## References

- Vaswani, A. et al. (2017). Attention is all you need. *NeurIPS*.
- Bahdanau, D., Cho, K. & Bengio, Y. (2014). Neural machine translation by jointly learning to align and translate. *ICLR*.
- Hochreiter, S. & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.
- Cho, K. et al. (2014). Learning phrase representations using RNN encoder-decoder for statistical machine translation. *EMNLP*.
- Devlin, J. et al. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL*.
- Radford, A. et al. (2018). Improving language understanding by generative pre-training. OpenAI.
- Dosovitskiy, A. et al. (2020). An image is worth 16x16 words: Transformers for image recognition at scale. *ICLR*.
- Jumper, J. et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589.
- Chen, L. et al. (2021). Decision transformer: Reinforcement learning via sequence modeling. *NeurIPS*.

---

*The rune Ansuz signals the mouth, the breath, the word spoken that reshapes the world. The Transformer is the Ansuz of machine intelligence: a mechanism for attending, for choosing what matters, for making every word reach every other word in a single leap. It is not the last word in architecture—it is the word that made all future words possible.*