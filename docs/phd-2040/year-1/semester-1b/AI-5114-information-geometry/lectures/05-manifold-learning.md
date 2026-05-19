# Lecture 05: Manifold Learning

## t-SNE, UMAP, Isomap, Diffusion Maps, Topological Data Analysis

> *"The data do not lie in Euclidean space — they are cast upon it like shadows on a wall. Manifold learning is the art of reading the true shape from the shadow."*

---

## 1. The Manifold Hypothesis

**Hypothesis 5.1 (Manifold Hypothesis).** High-dimensional data $X = \{x_1, \ldots, x_N\} \subset \mathbb{R}^D$ is assumed to lie on or near a low-dimensional manifold $\mathcal{M}$ of intrinsic dimensionality $d \ll D$.

More precisely, there exists a smooth embedding $\phi: \mathcal{M} \hookrightarrow \mathbb{R}^D$ and a probability measure $\mu$ on $\mathcal{M}$ such that $x_i \approx \phi(z_i)$ for some $z_i \in \mathcal{M}$, and the observed distribution on $\mathbb{R}^D$ is the pushforward $\phi_*\mu$.

If the manifold hypothesis holds, then the intrinsic geometry of the data is the Riemannian geometry of $(\mathcal{M}, g)$, where $g$ is typically (but not always) the pullback of the Euclidean metric via $\phi$. The goal of manifold learning is to *recover* $\mathcal{M}$ — or at least a faithful low-dimensional representation of it — from the data.

### 1.1 When the Manifold Hypothesis Fails

The manifold hypothesis is not always appropriate:
- **Data sets with different intrinsic dimensions in different regions** (the manifold is piecewise-smooth or has singularities).
- **Data concentrated near a submanifold** with significant noise or curvature (the "thick" manifold).
- **Data on trees or stratified spaces** (the underlying structure is not a manifold but a more general topological space).

In these cases, the geometric methods of this lecture still apply, but the interpretation changes: we are learning the *shape* of the data, not merely reducing its dimension.

## 2. Classical Methods: PCA and Multidimensional Scaling

### 2.1 Principal Component Analysis (PCA)

PCA finds the $d$-dimensional affine subspace $\mathcal{V} \subset \mathbb{R}^D$ that minimizes the reconstruction error $\sum_i \|x_i - \text{proj}_\mathcal{V}(x_i)\|^2$. The solution is given by the eigenvectors of the covariance matrix $C = \frac{1}{N}\sum_i (x_i - \bar{x})(x_i - \bar{x})^\top$ corresponding to the $d$ largest eigenvalues.

**Limitation:** PCA is a *linear* method — it finds the best *flat* approximation. If $\mathcal{M}$ is curved, PCA fails to capture the intrinsic geometry. The principal components are tangent directions at the data centroid, and the PCA reconstruction is the orthogonal projection onto the tangent space $T_{\bar{x}}\mathcal{M}$ — not onto $\mathcal{M}$ itself.

### 2.2 Classical Multidimensional Scaling (cMDS)

Given a distance matrix $D = [d_{ij}]$ (where $d_{ij} = \|x_i - x_j\|$, or any dissimilarity metric), cMDS finds the configuration $\{y_i\} \subset \mathbb{R}^d$ that best preserves the distances. It works by:
1. Computing the *centered Gram matrix* $B = -\frac{1}{2}HD^{(2)}H$, where $H = I - \frac{1}{N}\mathbf{1}\mathbf{1}^\top$ is the centering matrix and $D^{(2)}$ is the matrix of squared distances.
2. Taking the top $d$ eigenvectors of $B$ with eigenvalues $\lambda_1 \geq \cdots \geq \lambda_d$.
3. The embedding is $y_i = (\sqrt{\lambda_1}\,v_1^{(i)}, \ldots, \sqrt{\lambda_d}\,v_d^{(i)})$.

cMDS is equivalent to PCA when the distances are Euclidean. It *exactly* recovers the original configuration (up to rotation) if the distances are Euclidean and $d$ equals the true dimensionality. For non-Euclidean distances (e.g., geodesic distances on a manifold), cMDS produces the best Euclidean approximation — which is an *isometric* embedding only if the manifold is flat.

## 3. Isomap

**Isomap** (Tenenbaum, de Silva, & Langford, 2000) addresses the curvature limitation of cMDS by replacing Euclidean distances with *geodesic* distances on the data manifold.

### 3.1 Algorithm

1. **Neighborhood graph:** Construct a graph $G$ on the data points where $x_i$ and $x_j$ are connected if $x_j$ is among the $k$ nearest neighbors of $x_i$ (or within an $\epsilon$-ball). Weight each edge by $\|x_i - x_j\|$.

2. **Geodesic distances:** Compute the shortest-path distances $d_G(i,j)$ on $G$ (using Dijkstra's algorithm or Floyd-Warshall). These approximate the true geodesic distances $d_{\mathcal{M}}(x_i, x_j)$ on the manifold.

3. **Embedding:** Apply cMDS to the geodesic distance matrix $D_G = [d_G(i,j)]$.

### 3.2 Theoretical Foundation

**Theorem 5.2 (Isomap Consistency).** Let $\mathcal{M}$ be a compact, connected, smooth Riemannian manifold isometrically embedded in $\mathbb{R}^D$. If $\mathcal{M}$ is *convex* (i.e., geodesics between any two points in $\mathcal{M}$ remain in the convex hull of the embedding), then as $N \to \infty$ and $k \to \infty$ appropriately:
$$d_G(i,j) \to d_{\mathcal{M}}(x_i, x_j) \quad \text{almost surely}.$$

The convexity condition ensures that short Euclidean distances are good approximations of geodesic distances. Without it, "shortcuts" through ambient space can cause Isomap to underestimate geodesic distances.

### 3.3 Limitations

Isomap assumes the manifold is *uniformly sampled* and *convex*. For manifolds with holes, dense and sparse regions, or non-trivial topology, the nearest-neighbor graph may not faithfully approximate geodesic distances. Additionally, Isomap's reliance on geodesic distances makes it sensitive to *short circuits* — spurious edges that cross through ambient space and destroy the manifold structure.

### 3.4 Isomap and the Fisher-Rao Metric

Isomap uses the *ambient Euclidean metric* for nearest-neighbor distances. An information-geometric variant would use the *Fisher-Rao distance* between data distributions as the dissimilarity measure. Given data modeled as local probability distributions $\{p_{x_i}\}$, the Isomap embedding in Fisher-Rao space would recover the intrinsic information-geometric structure of the data manifold. This is the approach taken by *information-geometric CCA* and related methods.

## 4. Diffusion Maps

**Diffusion maps** (Coifman & Lafon, 2006) take a fundamentally different approach: instead of recovering an isometric embedding, they construct a *diffusion operator* on the data and use its eigenfunctions as coordinates.

### 4.1 The Diffusion Operator

1. **Kernel matrix:** Construct a symmetric kernel $K_{ij} = k(x_i, x_j) = \exp(-\|x_i - x_j\|^2 / 2\sigma^2)$ (Gaussian kernel with bandwidth $\sigma$).

2. **Normalization:** Define $D = \text{diag}(D_{ii})$ where $D_{ii} = \sum_j K_{ij}$. The *random walk* normalized kernel is:
$$P_{ij} = \frac{K_{ij}}{D_{ii}} = \frac{K(x_i, x_j)}{\sum_l K(x_i, x_l)}.$$
$P$ is a row-stochastic matrix — a Markov transition matrix on the data. The Markov chain models a *diffusion process* on $\mathcal{M}$.

3. **Diffusion distance:** The *diffusion distance* at time $t$ is:
$$D_t^2(x_i, x_j) = \sum_{k} \frac{(P^t_{ik} - P^t_{jk})^2}{\pi_k},$$
where $\pi$ is the stationary distribution of $P$ (which exists under mild conditions). This measures how different the transition probabilities from $x_i$ and $x_j$ are after $t$ steps — points reachable from both $x_i$ and $x_j$ in $t$ steps contribute to making them "close."

4. **Embedding:** The diffusion map at time $t$ maps data point $x_i$ to:
$$\Psi_t(x_i) = \left(\lambda_1^t\,\psi_1(i), \lambda_2^t\,\psi_2(i), \ldots, \lambda_d^t\,\psi_d(i)\right),$$
where $(\lambda_k, \psi_k)$ are the eigenvalue/eigenfunction pairs of $P$ (with $1 = \lambda_0 > \lambda_1 \geq \lambda_2 \geq \cdots$).

**Theorem 5.3 (Diffusion Map Embedding).** The diffusion map $\Psi_t$ satisfies:
$$D_t^2(x_i, x_j) = \|\Psi_t(x_i) - \Psi_t(x_j)\|^2.$$
That is, the diffusion distance is *exactly* the Euclidean distance in the diffusion map coordinates.

### 4.2 Connection to the Laplace-Beltrami Operator

**Theorem 5.4 (Convergence to Laplace-Beltrami).** As $N \to \infty$ and $\sigma \to 0$ with $N\sigma^{d+2} \to \infty$:
$$\frac{1}{\sigma^2}(I - P) \to -c\,\Delta_{\mathcal{M}},$$
where $\Delta_{\mathcal{M}}$ is the *Laplace-Beltrami operator* on $\mathcal{M}$ (with respect to the Riemannian volume form) and $c$ is an explicit constant depending on the kernel.

The Laplace-Beltrami operator $\Delta_{\mathcal{M}} = -\text{div}\,\text{grad}$ encodes the intrinsic Riemannian geometry. Its eigenfunctions form an orthonormal basis of $L^2(\mathcal{M}, dV_g)$ and the eigenvalues encode the "frequencies" of the manifold. Diffusion maps recover these eigenfunctions from data, providing coordinates that are:
- **Intrinsic:** Independent of the embedding $\phi: \mathcal{M} \hookrightarrow \mathbb{R}^D$.
- **Multi-scale:** The parameter $t$ controls the scale of the diffusion, and the decay of eigenvalues $\lambda_k^t$ determines which coordinates are relevant.
- **Connected to geometry:** The heat kernel $e^{-t\Delta_{\mathcal{M}}}$ is the fundamental solution of the heat equation on $\mathcal{M}$, and its asymptotics encode the curvature (via the Minakshisundaram-Pleijel expansion).

### 4.3 Diffusion Maps and the Fisher-Rao Metric

If we replace the Gaussian kernel $K_{ij} = \exp(-\|x_i-x_j\|^2/2\sigma^2)$ with the *Fisher-Rao kernel* $K_{ij} = \exp(-d_{FR}(p_i, p_j)^2/2\sigma^2)$, where $p_i$ is a local distribution associated with data point $x_i$, the resulting diffusion operator approximates the *Laplace-Beltrami operator on the statistical manifold* rather than the ambient Euclidean manifold. This gives a Fisher-information-weighted diffusion that respects the information geometry of the data.

## 5. t-Distributed Stochastic Neighbor Embedding (t-SNE)

**t-SNE** (van der Maaten & Hinton, 2008) is a *non-linear* dimensionality reduction method that preserves *local structure* by matching pairwise similarities in high and low dimensions.

### 5.1 Algorithm

1. **High-dimensional similarities:** Compute the *conditional probabilities*:
$$p_{j|i} = \frac{\exp(-\|x_i - x_j\|^2 / 2\sigma_i^2)}{\sum_{k\neq i}\exp(-\|x_i - x_k\|^2 / 2\sigma_i^2)},$$
where $\sigma_i$ is set by binary search to achieve a fixed *perplexity* $\text{Perp}(P_i) = 2^{H(P_i)}$ where $H(P_i) = -\sum_j p_{j|i}\log_2 p_{j|i}$. Symmetrize: $p_{ij} = (p_{j|i} + p_{i|j})/2N$.

2. **Low-dimensional similarities:** Use the *Student-t distribution* with one degree of freedom (Cauchy distribution):
$$q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{k\neq l}(1 + \|y_k - y_l\|^2)^{-1}}.$$

3. **Optimization:** Minimize the KL divergence:
$$\mathcal{L} = \text{KL}(P\|Q) = \sum_{i\neq j} p_{ij}\log\frac{p_{ij}}{q_{ij}}$$
using gradient descent (with momentum and early exaggeration).

### 5.2 Geometric Interpretation

t-SNE can be understood as a *distortion-minimizing projection* from a high-dimensional similarity structure $P$ to a low-dimensional one $Q$. The heavy-tailed Student-t kernel in $Q$ compensates for the "crowding problem" — in high dimensions, there is much more volume at moderate distances than in low dimensions, and the t-distribution's heavier tails allow distant points in $\mathbb{R}^d$ to better separate.

**From the information-geometric perspective:** t-SNE minimizes the KL divergence between the *empirical information geometry* of the data (encoded by $P$) and the *induced geometry* of the embedding (encoded by $Q$). This is a *pullback* operation: we want the Fisher-Rao geometry of $Q$ to match that of $P$ as closely as possible, as measured by KL divergence.

The main limitations of t-SNE are:
- **Non-convexity:** The cost function $\text{KL}(P\|Q)$ has many local minima; results depend on initialization.
- **No explicit model:** t-SNE does not produce a mapping from $\mathbb{R}^D$ to $\mathbb{R}^d$; it only produces an embedding of the training data.
- **Global structure loss:** t-SNE preserves local structure at the expense of global geometry; cluster sizes and distances between clusters are not preserved.

## 6. UMAP: Uniform Manifold Approximation and Projection

**UMAP** (McInnes, Healy, & Melville, 2018) constructs a fuzzy topological representation of the data in high dimensions and optimizes a low-dimensional representation to match it.

### 6.1 Algorithm

1. **Fuzzy simplicial set in high dimensions:** For each point $x_i$, find its $k$ nearest neighbors $\{x_{i_1}, \ldots, x_{i_k}\}$. Compute:
$$p_{j|i} = \exp\!\left(-\frac{\|x_i - x_{i_j}\| - \rho_i}{\sigma_i}\right),$$
where $\rho_i = \min_{j}\|x_i - x_j\|$ (ensuring every point has at least one close neighbor) and $\sigma_i$ is chosen to achieve target perplexity. Symmetrize via fuzzy union: $p_{ij} = p_{j|i} + p_{i|j} - p_{j|i}\cdot p_{i|j}$.

2. **Fuzzy simplicial set in low dimensions:** Define $q_{ij} = (1 + a\|y_i - y_j\|^{2b})^{-1}$ where $a, b$ are parameters (default: $a=1.93, b=0.8$, approximating a Student-t kernel).

3. **Optimization:** Minimize the *cross-entropy*:
$$\mathcal{L} = \sum_{i\neq j}\left[-p_{ij}\log q_{ij} - (1-p_{ij})\log(1-q_{ij})\right].$$

### 6.2 Theoretical Foundation: Fuzzy Simplicial Sets and Čech Complexes

UMAP's construction is grounded in *applied topology*. The neighborhood graph generates a *Vietoris-Rips complex* on the data, and the fuzzy membership values $p_{j|i}$ create a *fuzzy simplicial set* — a graded family of simplices with "confidence" weights. The key theoretical result:

**Theorem 5.5 (UMAP Nerve Theorem).** Under the UMAP assumptions (data uniformly sampled from a Riemannian manifold $\mathcal{M}$ with a Riemannian metric adapted to local density), the 1-skeleton of the fuzzy simplicial set converges to the 1-skeleton of the Čech complex of $\mathcal{M}$ as $N \to \infty$ and $\epsilon \to 0$ appropriately.

The Čech complex $\check{C}_\epsilon(\{x_i\})$ consists of all simplices $\sigma$ such that $\bigcap_{i \in \sigma} B_\epsilon(x_i) \neq \emptyset$. By the Nerve Theorem, $\check{C}_\epsilon$ is homotopy equivalent to $\bigcup_i B_\epsilon(x_i)$, which (for small enough $\epsilon$) is homotopy equivalent to $\mathcal{M}$ itself.

### 6.3 UMAP's Riemannian Metric Adaptation

A crucial innovation in UMAP is the *local metric adaptation*. Instead of using the ambient Euclidean metric, UMAP defines a *local Riemannian metric* at each point:
$$g_i(u, v) = \frac{1}{\rho_i^2}\langle u, v\rangle_{\mathbb{R}^D},$$
where $\rho_i$ is the distance to the nearest neighbor. This rescales distances to account for local density variations, effectively "flattening" the manifold by expanding sparse regions and compressing dense ones. In information-geometric terms, this is analogous to choosing a conformal metric $g = c(x)\,g_{\text{Euclidean}}$ where the conformal factor $c(x) = 1/\rho_i^2$ compensates for non-uniform sampling.

## 7. Topological Data Analysis (TDA)

TDA provides tools that go beyond manifold learning to capture the *topology* of data — connectedness, holes, and voids.

### 7.1 Persistent Homology

**Definition 5.6 (Vietoris-Rips Complex).** For a point cloud $\{x_i\}$ and scale parameter $\epsilon > 0$, the *Vietoris-Rips complex* $\text{VR}_\epsilon$ consists of all simplices $\sigma = [x_{i_0}, \ldots, x_{i_k}]$ such that $\|x_{i_a} - x_{i_b}\| \leq 2\epsilon$ for all $a, b$.

As $\epsilon$ increases from 0 to $\infty$, $\text{VR}_\epsilon$ forms a *filtration*: $\text{VR}_{\epsilon_1} \subseteq \text{VR}_{\epsilon_2}$ for $\epsilon_1 \leq \epsilon_2$. The *persistent homology* tracks how homology groups $H_k(\text{VR}_\epsilon)$ change with $\epsilon$:
- **$H_0$:** Connected components (merge as $\epsilon$ increases).
- **$H_1$:** Loops/cycles (appear and fill in as $\epsilon$ increases).
- **$H_2$:** Voids/cavities (appear and fill in).
- Higher homology groups: higher-dimensional topological features.

Each topological feature has a *birth time* $\epsilon_{\text{birth}}$ and *death time* $\epsilon_{\text{death}}$. The collection of (birth, death) pairs for dimension $k$ is the *persistence diagram* $\text{PD}_k$. Features with long lifetimes $(\epsilon_{\text{death}} - \epsilon_{\text{birth}})$ are *persistent* — they represent genuine topological structure, not noise.

### 7.2 The Stability Theorem

**Theorem 5.7 (Stability of Persistence Diagrams).** Let $f, g: \mathcal{M} \to \mathbb{R}$ be two functions. Then the *bottleneck distance* between their persistence diagrams satisfies:
$$d_B(\text{PD}(f), \text{PD}(g)) \leq \|f - g\|_\infty.$$

This stability result ensures that small perturbations of the data produce small changes in the persistence diagram. It is the topological analogue of the stability of the Fisher-Rao metric under perturbations of the underlying distribution.

### 7.3 Mapper Algorithm

The **Mapper** algorithm (Singh, Mémoli, & Carlsson, 2007) produces a simplicial complex from data:
1. Cover the image $f(X) \subset \mathbb{R}$ (or $\mathbb{R}^d$) with overlapping intervals (patches).
2. For each patch, cluster the preimage $f^{-1}(\text{patch}) \cap X$.
3. Create a node for each cluster, and connect nodes whose clusters share data points.

The resulting graph captures the "shape" of the data through the lens of the filter function $f$. Different choices of $f$ reveal different topological features. Choosing $f$ to be an information-geometric quantity (e.g., the Fisher-Rao distance to a reference distribution) yields an *information-topological* summary of the data.

## 8. The Information-Geometric Unification

All the methods in this lecture recover or approximate the *intrinsic geometry* of the data manifold. They differ in what aspect of the geometry they preserve:

| Method | Preserves | Approximates | Loss Function |
|--------|-----------|-------------|---------------|
| PCA | Global variance | Flat subspace | $\sum\|x_i - \text{proj}(x_i)\|^2$ |
| Isomap | Geodesic distances | Shortest-path distances | Strain: $\|D_{\mathcal{M}} - D_Y\|^2$ |
| Diffusion maps | Diffusion distances | $(\text{Laplace-Beltrami})^{-1}$ eigenvalues | Spectral: eigenvalue truncation |
| t-SNE | Local similarities | KL divergence | $\text{KL}(P\|Q)$ |
| UMAP | Fuzzy topological structure | Cross-entropy | $-\sum p\log q - (1-p)\log(1-q)$ |
| TDA | Homology | Filtration | Bottleneck distance |

The information-geometric perspective unifies these methods: each method implicitly or explicitly defines a *Riemannian metric* on the data manifold — Euclidean for PCA, geodesic for Isomap, heat kernel for diffusion maps, similarity kernel for t-SNE, locally adapted for UMAP — and then optimizes the embedding to minimize the distortion of this metric in the low-dimensional space. The choice of metric determines what the method preserves.

---

## Exercises

1. **(Isomap on the Swiss roll)** Generate a Swiss roll dataset $x_i = (t_i\cos t_i, t_i\sin t_i, h_i)$ where $t_i \in [3\pi/2, 9\pi/2]$ and $h_i \sim \text{Uniform}(0, 21)$. Implement Isomap and show that it recovers the correct 2D parameterization $(t_i, h_i)$. Compare with PCA, which produces a twisted projection.

2. **(Diffusion maps and the Laplace-Beltrami operator)** For data uniformly sampled from the unit circle $S^1$, compute the diffusion map and show that the first non-trivial eigenvector approximates $\cos(\theta)$ and $\sin(\theta)$, where $\theta$ is the angular coordinate. Verify Theorem 5.4 numerically by comparing $P$ with $I - \sigma^2\Delta_{S^1}/2$.

3. **(t-SNE cost function as KL)** Show that the t-SNE cost function $\text{KL}(P\|Q) = \sum_{i\neq j} p_{ij}\log(p_{ij}/q_{ij})$ is equal to $\sum_{i\neq j} p_{ij}\log p_{ij} - \sum_{i\neq j} p_{ij}\log q_{ij}$. The first term is constant; only the second matters for optimization. Compute the gradient and show it equals $4\sum_j (p_{ij} - q_{ij})(y_i - y_j)(1 + \|y_i - y_j\|^2)^{-1}$.

4. **(UMAP cross-entropy as information geometry)** Show that the UMAP binary cross-entropy loss $\mathcal{L} = -\sum p\log q - (1-p)\log(1-q)$ can be written as $\text{KL}(P\|Q) + \text{KL}((1-P)\|(1-Q)) + H(P) + H(1-P)$, where the entropies are constants. Argue that UMAP minimizes the *symmetric* KL divergence between the high- and low-dimensional similarity structures.

5. **(Persistence diagram computation)** For a set of 100 points sampled uniformly from the unit circle $S^1 \subset \mathbb{R}^2$ plus 50 noise points sampled from $\mathcal{N}(0, 0.5I)$ in $\mathbb{R}^2$, compute the Vietoris-Rips filtration and persistence diagram. Identify the $H_1$ feature corresponding to the circle and the $H_0$ feature corresponding to connectivity. What is the expected lifetime of the $H_1$ feature?