# Lecture 06: Attention Geometry

## Information Geometry of Transformer Attention Patterns

> *"The attention matrix is a map of Midgard: each entry marks a path between tokens, and the Fisher metric measures how those paths bend under the weight of meaning."*

---

## 1. The Attention Mechanism as a Statistical Object

The transformer attention mechanism (Vaswani et al., 2017) computes:

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V = AV,$$

where $Q = XW_Q$, $K = XW_K$, $V = XW_V$ are projections of the input sequence $X \in \mathbb{R}^{n \times d}$, and $A = \text{softmax}(QK^\top/\sqrt{d_k}) \in \mathbb{R}^{n \times n}$ is the *attention matrix*.

Each row $A_i = (a_{i1}, \ldots, a_{in})$ of the attention matrix is a probability distribution over the $n$ tokens, produced by applying the softmax function to the $i$-th row of the score matrix $S = QK^\top/\sqrt{d_k}$:
$$a_{ij} = \frac{\exp(s_{ij})}{\sum_{k=1}^n \exp(s_{ik})} = \text{softmax}(s_i)_j.$$

This means: *each row of the attention matrix lives on the probability simplex $\Delta^{n-1}$*. The entire attention matrix is a collection of $n$ distributions on $\Delta^{n-1}$ — a statistical manifold.

### 1.1 Attention as a Markov Kernel

The attention matrix $A$ defines a *Markov kernel* on the token set $\{1, \ldots, n\}$: $A_{ij}$ is the probability of transitioning from token $i$ to token $j$ in one step. The Markov chain $A$ has:
- **Stationary distribution** $\pi$ (if irreducible and aperiodic): $\pi A = \pi$.
- **Mixing time** $t_{\text{mix}}(\epsilon) = \min\{t : \|A^t_{i\cdot} - \pi\|_1 \leq \epsilon\}$ — the time to reach near-stationarity.
- **Spectral gap** $\gamma = 1 - \lambda_2(A)$ where $\lambda_2$ is the second-largest eigenvalue — controls mixing rate.

The multi-layer application of attention corresponds to iterating this Markov kernel. A 12-layer transformer with residual connections computes $A^{(12)} = A_{12}A_{11}\cdots A_1$ (approximately, since each layer has its own attention matrix). The spectral properties of this product determine how information propagates through the network.

## 2. The Fisher-Rao Geometry of Softmax

### 2.1 Softmax as a Statistical Map

The softmax function $\sigma: \mathbb{R}^n \to \Delta^{n-1}_{\text{int}}$ defined by $\sigma(z)_i = e^{z_i}/\sum_j e^{z_j}$ is a diffeomorphism from $\mathbb{R}^n$ to the interior of the probability simplex. When we view $\Delta^{n-1}$ as a Riemannian manifold with the Fisher-Rao metric, softmax becomes a *statistical embedding*: it maps the Euclidean space of logits to the statistical manifold of distributions.

**Proposition 6.1.** The softmax map $\sigma: (\mathbb{R}^n, g_{\text{logit}}) \to (\Delta^{n-1}, g_{\text{FR}})$ is a smooth map between Riemannian manifolds, where $g_{\text{logit}}$ is the pullback metric $\sigma^* g_{\text{FR}}$. The pullback metric on $\mathbb{R}^n$ at logits $z$ is:
$$g_{\text{logit}}(z) = \text{diag}(\sigma(z)) - \sigma(z)\sigma(z)^\top,$$
which is exactly the *covariance matrix* of the categorical distribution $\sigma(z)$.

*Proof.* The Jacobian of softmax is $J_{ij} = \frac{\partial\sigma_i}{\partial z_j} = \sigma_i(\delta_{ij} - \sigma_j)$. The pullback metric is $g = J^\top g_{\text{FR}} J$, but since $g_{\text{FR}}$ in the $\sigma$-coordinates at point $p$ is $(\text{diag}(1/p_i) + 1/(1-\sum p_i))$ restricted to $\Delta^{n-1}$, and $J$ accounts for the constraint, a direct computation gives $g_{\text{logit}} = \text{diag}(\sigma) - \sigma\sigma^\top$. □

### 2.2 The Softmax Metric as Fisher Information

The matrix $G(z) = \text{diag}(\sigma(z)) - \sigma(z)\sigma(z)^\top$ is the *Fisher information matrix* of the categorical distribution with parameters $\sigma(z)$. It is also the precision matrix of the multinomial distribution — encoding how much information each logit provides about the distribution.

**Corollary 6.2.** The softmax map $\sigma$ pulls back the Fisher-Rao metric from the simplex to a metric on logit space that is *not* Euclidean. The natural gradient on logit space (with respect to the softmax pullback metric) is:
$$\tilde{\nabla}_z \mathcal{L} = G(z)^{-1}\nabla_z\mathcal{L} = (\text{diag}(\sigma) - \sigma\sigma^\top)^{-1}\nabla_z\mathcal{L},$$
which differs from the Euclidean gradient $\nabla_z\mathcal{L}$ by a correction that accounts for the curvature of the simplex.

### 2.3 Curvature of the Softmax Manifold

The softmax image of $\mathbb{R}^n$ is $\Delta^{n-1}_{\text{int}}$ with the Fisher-Rao metric. By Chentsov's uniqueness theorem (Lecture 02), this is a constant-negative-curvature manifold (isometric to a portion of the $(n-1)$-sphere via the Bhattacharyya embedding).

**Theorem 6.3 (Curvature of Softmax Space).** The sectional curvature of $(\Delta^{n-1}_{\text{int}}, g_{\text{FR}})$ is constant and equal to $\frac{1}{4}$ (positive, not negative — the simplex with Fisher-Rao is a *spherical* geometry).

In the Bhattacharyya coordinates $\phi(p)_i = \sqrt{p_i}$, the simplex maps to the positive orthant of $S^{n-1}(1/2)$ (the sphere of radius $1/2$). The geodesic distance is $d_{FR}(p, q) = 2\arccos(\sum_i \sqrt{p_iq_i})$, which is an *angular* distance on the sphere.

This has a striking consequence: softmax distributions are naturally parameterized on a positively curved space. Two distributions that are "close" in Euclidean logit space can be far in Fisher-Rao distance if they lie near the boundary of the simplex (where one probability is near zero and the Fisher metric is large).

## 3. Natural Gradient Attention

### 3.1 Standard Attention vs. Natural Gradient Attention

Standard attention computation:
$$A = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right), \quad \text{output} = AV.$$

The gradient of the loss $\mathcal{L}$ with respect to the logits $S = QK^\top/\sqrt{d_k}$ is (by the softmax Jacobian):
$$\frac{\partial\mathcal{L}}{\partial S_{ij}} = \sum_k \frac{\partial\mathcal{L}}{\partial A_{ik}} J_{kj} = \sum_k \frac{\partial\mathcal{L}}{\partial A_{ik}} A_{ik}(\delta_{kj} - A_{ij}) = \frac{\partial\mathcal{L}}{\partial A_{ij}}A_{ij} - A_{ij}\sum_k\frac{\partial\mathcal{L}}{\partial A_{ik}}A_{ik}.$$

The *natural gradient* of $\mathcal{L}$ with respect to the output of the attention layer, measured in the Fisher-Rao metric of the attention distribution, is:
$$\tilde\nabla_{A_i}\mathcal{L} = G(A_i)^{-1}\nabla_{A_i}\mathcal{L} = (\text{diag}(A_i) - A_iA_i^\top)^{-1}\nabla_{A_i}\mathcal{L}.$$

### 3.2 Fisher-Weighted Attention

An alternative approach to natural gradient is to use the Fisher information directly as a *weighting* of the attention pattern. Define the **Fisher-weighted attention**:
$$A^{\text{Fisher}}_{ij} = \frac{A_{ij}/\mathcal{I}_{ij}}{\sum_k A_{ik}/\mathcal{I}_{ik}},$$
where $\mathcal{I}_{ij}$ is the Fisher information associated with the $(i,j)$-th attention score. This upweights directions with low Fisher information (high uncertainty) and downweights directions with high Fisher information (low uncertainty), analogous to how natural gradient descent takes larger steps in directions of low curvature.

### 3.3 The Natural Gradient Transformer

**Definition 6.4 (NG-Transformer Layer).** An *NG-Transformer layer* replaces the attention update $X \leftarrow X + AV$ with the natural gradient update:
$$X \leftarrow X + \alpha\,G(X)^{-1}\nabla_X\mathcal{L}_{\text{attn}},$$
where $G(X) = \mathbb{E}_{A}[\nabla_X \log p(A|X)\nabla_X \log p(A|X)^\top]$ is the empirical Fisher information of the attention distribution, and $\mathcal{L}_{\text{attn}}$ is the attention loss.

In practice, this is approximated by K-FAC or diagonal Fisher methods (cf. Lecture 04). The key insight: the standard Transformer uses *Euclidean* gradient descent on the attention parameters; the NG-Transformer uses *Riemannian* gradient descent, respecting the geometry of the probability simplex on which the attention weights live.

## 4. Information Geometry of Multi-Head Attention

### 4.1 Multi-Head Attention as a Product Manifold

In multi-head attention with $h$ heads, we compute:
$$\text{MultiHead}(X) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W_O,$$
where $\text{head}_k = \text{softmax}(Q_k K_k^\top/\sqrt{d_k})V_k$.

The attention pattern of each head $k$ is a matrix $A^{(k)} \in \mathbb{R}^{n \times n}$ with rows on $\Delta^{n-1}$. The full multi-head attention is a *product* of statistical manifolds:
$$\mathcal{M}_{\text{MHA}} = \underbrace{\Delta^{n-1} \times \cdots \times \Delta^{n-1}}_{h \text{ heads}} \times \underbrace{\Delta^{n-1} \times \cdots \times \Delta^{n-1}}_{n \text{ query positions per head}},$$
with the Fisher-Rao metric on each factor. The dimension of this product manifold is $h \cdot n \cdot (n-1)$.

**Proposition 6.5 (Product Manifold Property).** The Fisher-Rao metric on $\mathcal{M}_{\text{MHA}}$ is the direct sum of the Fisher-Rao metrics on each factor:
$$g_{\text{MHA}} = \bigoplus_{k=1}^{h}\bigoplus_{i=1}^{n} g_{\text{FR}}^{(k,i)},$$
where $g_{\text{FR}}^{(k,i)}$ is the Fisher metric on the simplex for the $i$-th query position of head $k$. Geodesics in the product manifold are componentwise geodesics.

### 4.2 Diversity of Attention Heads

The *diversity* of attention heads can be measured information-geometrically:

**Definition 6.6 (Attention Head Diversity).** The *geometric diversity* of a multi-head attention layer with attention matrices $A^{(1)}, \ldots, A^{(h)}$ is:
$$\mathcal{D}_{\text{geo}} = \frac{1}{\binom{h}{2}}\sum_{k < l}\sum_{i=1}^{n} d_{\text{FR}}(A_i^{(k)}, A_i^{(l)}),$$
the average Fisher-Rao distance between corresponding rows of different attention heads.

High diversity indicates that different heads attend to different aspects of the input — a desirable property for robust representation learning. Low diversity (all heads similar) indicates *attention head redundancy*, which has been empirically observed in large transformers and can be addressed via pruning.

### 4.3 Collapse and Uniformity

**Definition 6.7 (Attention Collapse).** An attention pattern $A_i = (a_{i1}, \ldots, a_{in})$ has *collapsed* if $a_{ij} \approx 1$ for some $j$ and $a_{ik} \approx 0$ for $k \neq j$. In the Fisher-Rao geometry, this corresponds to the distribution being near a *vertex* of $\Delta^{n-1}$, where the metric degenerates (diagonal elements go to infinity).

Conversely, *uniform attention* $A_i = (1/n, \ldots, 1/n)$ corresponds to the *barycenter* of $\Delta^{n-1}$, where the Fisher metric has its minimum eigenvalue. This is the point of *maximum entropy* and minimum Fisher information — the most "uncertain" attention pattern.

**Theorem 6.8 (Fisher Information at Boundary).** For the simplex $\Delta^{n-1}$ with the Fisher-Rao metric, the determinant of the Fisher information matrix at point $p = (p_1, \ldots, p_n)$ is:
$$\det(\mathcal{I}(p)) = \prod_{i=1}^{n}\frac{1}{p_i}.$$
This diverges as any $p_i \to 0$ (the boundary of the simplex) and is maximized at the uniform distribution $p_i = 1/n$ is where $\text{tr}(\mathcal{I}(p))$ is minimized.

## 5. The Geometric Dynamics of Attention

### 5.1 Attention as Geodesic Flow

Consider a single-layer attention mechanism. The transformation $X \mapsto AX$ can be decomposed as:
1. Project $X$ to value space: $V = XW_V$.
2. Apply the attention kernel: $AV$.
3. Re-project to the model dimension: $(AV)W_O$.

The attention matrix $A = \text{softmax}(QK^\top/\sqrt{d_k})$ can be viewed as a *transition kernel* on the token set. If we track the position of token $i$ in the attention distribution $A_i \in \Delta^{n-1}$ as $A_i$ evolves during training, we see a flow on the simplex.

**Observation 6.9.** The gradient flow of the training loss $\mathcal{L}$ on the attention weights $A$ induces a flow on $\Delta^{n-1}$. In Euclidean gradient descent (with logits $s$), this flow is:
$$\dot{A}_i = \frac{\partial A_i}{\partial s_i}\cdot\dot{s}_i = (\text{diag}(A_i) - A_iA_i^\top)\cdot\dot{s}_i,$$
where $\dot{s}_i = -\eta\,\nabla_{s_i}\mathcal{L}$. In natural gradient descent (with the Fisher-Rao metric), the flow becomes:
$$\dot{A}_i = (\text{diag}(A_i) - A_iA_i^\top)\cdot(\text{diag}(A_i) - A_iA_i^\top)^{-1}\cdot\dot{s}_i = \dot{s}_i,$$
which is *parameterization-free* — the natural gradient flow on the simplex does not depend on the specific parameterization (logits, probabilities, or any other).

### 5.2 Residual Connections and Parallel Transport

A transformer block computes:
$$X^{(\ell+1)} = X^{(\ell)} + \text{Attn}(X^{(\ell)}) + \text{FFN}(X^{(\ell)} + \text{Attn}(X^{(\ell)})).$$

The residual connection adds $X^{(\ell)}$ to the output, which in geometric terms is a *shortcut* that bypasses the nonlinear transformation. From the perspective of information geometry:
- The attention mechanism $\text{Attn}(X^{(\ell)})$ produces a flow on the attention simplex.
- The residual connection ensures that the flow doesn't stray too far from the identity, preventing *attention collapse*.
- The layer normalization $\text{LN}(X) = (X - \mu)/\sigma$ projects the representation back to a "spherical" submanifold (analogous to retraction in Riemannian optimization).

### 5.3 Positional Encodings as Gauge Choices

Positional encodings $\text{PE}(i) \in \mathbb{R}^d$ break the permutation invariance of attention. They can be viewed as a *choice of gauge* — a coordinate system on the position manifold. Sinusoidal positional encodings $\text{PE}(i, 2k) = \sin(i/10000^{2k/d})$ and $\text{PE}(i, 2k+1) = \cos(i/10000^{2k/d})$ embed the linear position $i$ into a curved manifold using a frequency decomposition. Learned positional encodings optimize the gauge for the specific data distribution.

Under a diffeomorphic reparameterization of positions, the natural gradient of the attention pattern is invariant (by Theorem 4.3), but the Euclidean gradient is not. This suggests that *transformers with natural gradient attention are invariant to monotonic reparameterizations of position*, while standard transformers are not.

## 6. Attention Entropy and Information Capacity

### 6.1 Entropy of Attention Patterns

The *entropy* of the $i$-th row of the attention matrix:
$$H(A_i) = -\sum_{j=1}^{n} a_{ij}\log a_{ij},$$
measures the "spread" of attention. Low entropy (concentrated attention) indicates that the query at position $i$ strongly attends to one or a few positions; high entropy (diffuse attention) indicates broad, uncertain attention.

**Proposition 6.10 (Entropy-Fisher Relation).** For a distribution $p$ on $\Delta^{n-1}$:
$$\mathcal{I}(p) \succeq \frac{1}{\max_i p_i}\,H(p)\cdot I_{n-1},$$
where $\mathcal{I}(p)$ is the Fisher information matrix. High-Fisher-information distributions have *low entropy* (they are concentrated near vertices of the simplex), while low-Fisher-information distributions have *high entropy* (near the barycenter).

### 6.2 Mutual Information Between Queries and Keys

The attention matrix $A$ can be interpreted as a *joint distribution* (after normalization): $P(i, j) = A_{ij}/n$ or as a *conditional distribution* $P(j|i) = A_{ij}$. The mutual information $I(Q; K)$ through the attention mechanism is:
$$I(Q; K) = H(Q) - H(Q|K) = -\sum_i p(i)\log p(i) + \sum_{i,j} p(i,j)\log p(j|i),$$
where $p(i) = 1/n$ (uniform over queries) and $p(j|i) = A_{ij}$.

This mutual information measures the *information capacity* of the attention layer — how much information about the key positions is captured by the query-attention mechanism. Maximum $I(Q;K)$ is achieved when each row of $A$ is concentrated on a single column (one-to-one attention); minimum $I(Q;K)$ is achieved when $A_{ij} = 1/n$ (uniform attention).

### 6.3 Temperature Scaling and the Fisher Metric

The softmax temperature $\tau$ (often set to $1/\sqrt{d_k}$) controls the *sharpness* of the attention distribution:
$$A_{ij}^{(\tau)} = \frac{\exp(s_{ij}/\tau)}{\sum_k \exp(s_{ik}/\tau)}.$$

As $\tau \to 0$: $A^{(\tau)} \to \text{one-hot}(\arg\max_j s_{ij})$ — hard attention, low entropy, high Fisher information.
As $\tau \to \infty$: $A^{(\tau)} \to (1/n, \ldots, 1/n)$ — uniform attention, maximum entropy, minimum Fisher information.

**Proposition 6.11 (Temperature as Conformal Scaling).** The Fisher-Rao metric on the attention manifold scales with temperature: at temperature $\tau$, the Fisher metric is $g^{(\tau)} = g^{(1)}/\tau^2$. Thus, lowering the temperature *stretches* the geometry of the simplex, making nearby distributions appear farther apart in the Fisher distance.

This is a *conformal transformation* of the simplex geometry. The geodesics are preserved (they are still great-circle arcs on the sphere in Bhattacharyya coordinates), but distances are scaled by $1/\tau$.

## 7. Open Questions and Frontiers

1. **Optimal temperature scheduling:** Is there an information-geometrically optimal schedule for $\tau$ during training? Should temperature decrease (focusing attention) or increase (diversifying attention) based on the Fisher information of the attention pattern?

2. **Attention head geometry beyond diversity:** The Fisher-Rao distance between heads measures their separation, but what about the *transversality* of their attention subspaces? Can we define a notion of "geometric independence" for attention heads based on the curvature of the product manifold?

3. **Geodesic attention:** What if we replace the softmax $A = \text{softmax}(QK^\top/\sqrt{d_k})$ with the *geodesic interpolation* $A_i(t) = \text{Geodesic}_{\text{FR}}(e_i, A_i; t)$ on $\Delta^{n-1}$, where $e_i$ is the one-hot distribution at position $i$? This would give a *geometrically natural* attention that respects the curvature of the simplex.

4. **Information geometry of KV-caching:** In autoregressive generation, the key-value cache grows over time. The attention distribution at each step is a path on $\Delta^{n-1}$ as $n$ increases. What is the information-geometric characterization of this path? Does it converge to a limiting distribution?

---

## Exercises

1. **(Softmax pullback metric)** Compute the eigenvalues of the pullback metric $G(z) = \text{diag}(\sigma(z)) - \sigma(z)\sigma(z)^\top$ for a 3-class distribution $z = (z_1, z_2, z_3)$. Show that one eigenvalue is always 0 (corresponding to $\mathbf{1} = (1,1,1)$) and the others are $\sigma_i(1-\sigma_i)$ for the "active" dimensions.

2. **(Natural gradient for cross-entropy)** Let $\mathcal{L}(\theta) = -\sum_i y_i \log \sigma(\theta)_i$ be the cross-entropy loss with softmax activation. Compute the natural gradient $\mathcal{I}(\theta)^{-1}\nabla_\theta\mathcal{L}$ and show it equals $\theta - \theta^*$, where $\theta^*$ is any vector with $\sigma(\theta^*) = y$. Explain why natural gradient descent on cross-entropy converges in one step.

3. **(Attention head diversity)** Generate $h=8$ random attention matrices $A^{(k)} \in \mathbb{R}^{10 \times 10}$ with $\text{softmax}(\mathcal{N}(0,1))$ rows. Compute the geometric diversity $\mathcal{D}_{\text{geo}}$ using the Fisher-Rao distance. Compare with the Euclidean diversity $\frac{1}{\binom{h}{2}}\sum_{k<l}\|A^{(k)}-A^{(l)}\|_F$. Which is larger? Why?

4. **(Temperature scaling)** Prove that the Fisher-Rao metric at temperature $\tau$ is $g^{(\tau)} = g^{(1)}/\tau^2$, i.e., $d_{FR}^{(\tau)}(p, q) = d_{FR}^{(1)}(p, q)/\tau$. Conclude that the geodesic distance between two distributions scales inversely with temperature.

5. **(Mutual information capacity)** Show that the maximum mutual information $I(Q; K)$ through a softmax attention mechanism with $n$ query positions and $n$ key positions is $\log n$ (achieved by hard one-to-one attention) and the minimum is 0 (achieved by uniform attention). Compute $I(Q; K)$ for the 2-token case $A = \begin{pmatrix} \alpha & 1-\alpha \\ 1-\beta & \beta \end{pmatrix}$ as a function of $\alpha$ and $\beta$.