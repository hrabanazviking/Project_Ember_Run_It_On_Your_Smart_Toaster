# Lecture 01: Differential Geometry Foundations

## Manifolds, Tangent Spaces, Metric Tensors

> *"At the root of all things lies not chaos, but smooth structure — the manifold upon which gradients carve their paths."*

---

## 1. Topological Preliminaries

Before we can speak of geometry on statistical parameter spaces, we must establish the ground from which every smooth structure grows: the topological manifold.

**Definition 1.1 (Topological Manifold).** A Hausdorff, second-countable topological space $M$ is an *n-dimensional topological manifold* if every point $p \in M$ has an open neighborhood $U$ homeomorphic to an open subset of $\mathbb{R}^n$. That is, there exists a homeomorphism $\varphi: U \to \varphi(U) \subseteq \mathbb{R}^n$.

The pair $(U, \varphi)$ is called a *chart* or *local coordinate system*. The requirement of second-countability (equivalent to $M$ having a countable basis for its topology) ensures paracompactness, which we need for partitions of unity — and without partitions of unity, Riemannian metrics cannot be shown to exist globally.

**Why Hausdorff?** The Hausdorff condition excludes pathological spaces like the line with two origins. In statistical contexts, our parameter spaces (e.g., the interior of the probability simplex $\Delta^{n-1}$, the space of positive-definite matrices $\mathcal{S}_{++}^n$) are manifestly Hausdorff. But we mention it because the distinction between *separated* and *non-separated* gluing of charts will matter when we consider quotient manifolds later in the course.

## 2. Smooth Manifolds

**Definition 1.2 (Smooth Manifold).** A *smooth manifold* (or $C^\infty$-manifold) of dimension $n$ is a topological manifold $M$ equipped with a *smooth atlas* $\mathcal{A} = \{(U_\alpha, \varphi_\alpha)\}$ — a collection of charts such that:
1. $\bigcup_\alpha U_\alpha = M$ (the charts cover $M$),
2. For any overlapping charts $(U_\alpha, \varphi_\alpha)$ and $(U_\beta, \varphi_\beta)$, the *transition map*
$$\varphi_\beta \circ \varphi_\alpha^{-1} : \varphi_\alpha(U_\alpha \cap U_\beta) \to \varphi_\beta(U_\alpha \cap U_\beta)$$
is $C^\infty$.

A *maximal atlas* is an atlas that is not properly contained in any other smooth atlas (i.e., it contains every compatible chart). By Zorn's lemma, every smooth atlas extends uniquely to a maximal one. We work exclusively with maximal atlases.

### 2.1 The Statistical Manifold as a Smooth Manifold

Consider a parametric family of probability distributions $\mathcal{S} = \{p_\xi : \xi \in \Xi\}$ where $\Xi \subseteq \mathbb{R}^n$ is an open parameter space. Under regularity conditions (the identification problem: $\xi_1 \neq \xi_2 \Rightarrow p_{\xi_1} \neq p_{\xi_2}$; and smooth dependence of $p_\xi$ on $\xi$), the parameter space $\Xi$ inherits a smooth manifold structure. A single global chart $(\Xi, \text{id})$ suffices.

This seems trivial, and in a sense it is — but the *geometry* of $\Xi$ is not the flat Euclidean geometry inherited from $\mathbb{R}^n$. The Fisher information metric will warp it into something far richer, like the way the Norns weave fate into an otherwise blank tapestry.

**Example: The Binomial Manifold.** Consider the binomial family $\mathcal{B}(n, p)$ for fixed $n$ with parameter space $\Xi = (0, 1)$. This is a 1-manifold. It admits a single global chart. Yet as we shall see, its Fisher-Rao geometry is that of a hyperbolic metric on $(0,1)$ — a space of constant negative curvature $\kappa = -1/4$.

**Example: The Multivariate Normal Manifold.** The family $\mathcal{N}(\mu, \Sigma)$ of $n$-dimensional normal distributions with full-rank covariance forms a smooth manifold of dimension $n + n(n+1)/2 = n(n+3)/2$. The parameter space is $\mathbb{R}^n \times \mathcal{S}_{++}^n$, which is an open subset of $\mathbb{R}^{n(n+3)/2}$.

## 3. Tangent Spaces

**Definition 1.3 (Tangent Vector via Derivations).** Let $M$ be a smooth manifold and $p \in M$. A *derivation at $p$* is a linear map $v : C^\infty(M) \to \mathbb{R}$ satisfying the Leibniz rule:
$$v(fg) = v(f) \cdot g(p) + f(p) \cdot v(g).$$

The set of all derivations at $p$ forms a vector space $T_pM$, called the *tangent space at $p$*. Its elements are *tangent vectors*.

**Theorem 1.4.** If $M$ is an $n$-dimensional smooth manifold, then $T_pM \cong \mathbb{R}^n$ for every $p \in M$.

*Proof sketch.* In a local chart $(U, \varphi)$ with $\varphi = (x^1, \ldots, x^n)$, every derivation at $p$ can be expressed uniquely as $v = \sum_{i=1}^n v^i \left.\frac{\partial}{\partial x^i}\right|_p$, where $\left.\frac{\partial}{\partial x^i}\right|_p f = \frac{\partial (f \circ \varphi^{-1})}{\partial x^i}\big|_{\varphi(p)}$. The coordinate vectors $\{\partial/\partial x^i\}|_p$ form a basis. □

### 3.1 Tangent Vectors on Statistical Manifolds

On a statistical manifold $\mathcal{S}$ parameterized by $\xi = (\xi^1, \ldots, \xi^n)$, the tangent space $T_\xi\mathcal{S}$ at parameter value $\xi$ has a natural basis $\{\partial/\partial \xi^i\}|_\xi$. But there is a deeper interpretation.

A tangent vector $v \in T_\xi \mathcal{S}$ represents an *infinitesimal displacement* of the parameter. This displacement induces a corresponding infinitesimal change in the probability distribution. The mathematical object encoding this change is the *score vector*:
$$\ell_i(\xi) = \frac{\partial}{\partial \xi^i} \log p(x; \xi),$$
which we will study extensively in Lecture 02. For now, note that the basis vector $\partial/\partial \xi^i$ corresponds to the direction in which only $\xi^i$ increases.

### 3.2 The Tangent Bundle

**Definition 1.5 (Tangent Bundle).** The *tangent bundle* of $M$ is the disjoint union
$$TM = \bigsqcup_{p \in M} T_pM = \bigcup_{p \in M} \{p\} \times T_pM,$$
equipped with its canonical smooth structure making the projection $\pi: TM \to M$ a smooth map. $TM$ is a $2n$-dimensional smooth manifold.

A *vector field* on $M$ is a smooth section $X: M \to TM$, i.e., $X(p) \in T_pM$ for all $p$. In coordinates, $X = X^i \frac{\partial}{\partial x^i}$ where the coefficient functions $X^i$ are smooth.

The space of vector fields $\mathfrak{X}(M)$ forms a $\mathbb{R}$-algebra under the *Lie bracket*:
$$[X, Y]^i = X(Y^i) - Y(X^i) = X^j \partial_j Y^i - Y^j \partial_j X^i.$$
The Lie bracket satisfies antisymmetry ($[X,Y] = -[Y,X]$) and the Jacobi identity, making $(\mathfrak{X}(M), [\cdot,\cdot])$ a Lie algebra.

## 4. Riemannian Metrics

**Definition 1.6 (Riemannian Metric).** A *Riemannian metric* on a smooth manifold $M$ is a smooth $(0,2)$-tensor field $g$ that assigns to each point $p \in M$ an inner product $g_p$ on $T_pM$. Concretely:
1. **Smoothness:** For any smooth vector fields $X, Y \in \mathfrak{X}(M)$, the function $p \mapsto g_p(X_p, Y_p)$ is smooth.
2. **Positive-definiteness:** $g_p(v, v) \geq 0$ for all $v \in T_pM$, with equality iff $v = 0$.
3. **Symmetry:** $g_p(v, w) = g_p(w, v)$.

In local coordinates $(x^1, \ldots, x^n)$, we write:
$$g = g_{ij}\, dx^i \otimes dx^j, \quad \text{where } g_{ij}(p) = g_p\!\left(\left.\frac{\partial}{\partial x^i}\right|_p, \left.\frac{\partial}{\partial x^j}\right|_p\right).$$

The matrix $[g_{ij}(p)]$ is symmetric and positive-definite at each point.

**Theorem 1.7 (Existence of Riemannian Metrics).** Every smooth manifold admits a Riemannian metric.

*Proof.* Let $\{(U_\alpha, \varphi_\alpha)\}$ be a locally finite open cover of $M$ (which exists by paracompactness, which follows from second-countability). On each chart domain $U_\alpha$, define the *Euclidean metric* $g^{(\alpha)}$ by pulling back the standard inner product from $\mathbb{R}^n$ via $\varphi_\alpha$. Let $\{\rho_\alpha\}$ be a partition of unity subordinate to the cover. Set:
$$g = \sum_\alpha \rho_\alpha \cdot g^{(\alpha)}.$$
Since each $\rho_\alpha \geq 0$, $\sum_\alpha \rho_\alpha = 1$, and at least one $\rho_\alpha > 0$ at every point, $g$ is a well-defined, smooth, symmetric, positive-definite $(0,2)$-tensor field. □

### 4.1 The Metric as a Measuring Device

A Riemannian metric endows $M$ with geometric structure. Specifically:

- **Length of a curve.** For a smooth curve $\gamma: [a,b] \to M$:
$$L(\gamma) = \int_a^b \sqrt{g_{\gamma(t)}(\dot{\gamma}(t), \dot{\gamma}(t))}\, dt = \int_a^b \sqrt{g_{ij}(\gamma(t))\, \dot{\gamma}^i(t)\, \dot{\gamma}^j(t)}\, dt.$$

- **Geodesic distance.** The *Riemannian distance* between $p, q \in M$:
$$d(p, q) = \inf\{L(\gamma) : \gamma \text{ is a piecewise smooth curve from } p \text{ to } q\}.$$

- **Volume element.** The metric induces a volume form $\omega_g = \sqrt{\det(g_{ij})}\, dx^1 \wedge \cdots \wedge dx^n$, the natural integration measure on $M$.

### 4.2 Pullback Metrics

If $\phi: (N, h) \to (M, g)$ is a smooth map between Riemannian manifolds, the *pullback metric* $\phi^*g$ on $N$ (when $\phi$ is an immersion) is defined by:
$$(\phi^*g)_p(v, w) = g_{\phi(p)}(d\phi_p(v), d\phi_p(w)).$$

This construction is essential for statistical manifolds: the map from parameter space to probability distributions pulls back a metric from the "space of distributions" to the parameter space. When the space of distributions is equipped with the Fisher-Rao metric, this pullback gives the Fisher information matrix — as we will see in Lecture 02.

## 5. Connections, Parallel Transport, and Curvature

### 5.1 Affine Connections

**Definition 1.8 (Affine Connection).** An *affine connection* (or simply *connection*) on $M$ is a map $\nabla: \mathfrak{X}(M) \times \mathfrak{X}(M) \to \mathfrak{X}(M)$, written $(X, Y) \mapsto \nabla_X Y$, satisfying:
1. $\nabla_{fX+gY} Z = f\,\nabla_X Z + g\,\nabla_Y Z$ ($C^\infty$-linear in the first argument),
2. $\nabla_X(fY) = X(f)\,Y + f\,\nabla_X Y$ (Leibniz rule in the second argument).

In local coordinates, $\nabla$ is determined by its *Christoffel symbols*:
$$\nabla_{\partial_i} \partial_j = \Gamma_{ij}^k\, \partial_k.$$

### 5.2 The Levi-Civita Connection

**Theorem 1.9 (Fundamental Theorem of Riemannian Geometry).** On a Riemannian manifold $(M, g)$, there exists a unique affine connection $\nabla$ that is:
1. **Torsion-free:** $\nabla_X Y - \nabla_Y X = [X, Y]$,
2. **Metric-compatible:** $X(g(Y,Z)) = g(\nabla_X Y, Z) + g(Y, \nabla_X Z)$.

This unique connection is called the *Levi-Civita connection* (or *Riemannian connection*). Its Christoffel symbols are:
$$\Gamma_{ij}^k = \frac{1}{2} g^{kl}\!\left(\frac{\partial g_{lj}}{\partial x^i} + \frac{\partial g_{il}}{\partial x^j} - \frac{\partial g_{ij}}{\partial x^l}\right).$$

This formula is the Koszul formula in coordinates, and it is the *only* connection compatible with both the metric and the symmetry of the tangent bundle. In information geometry, we will encounter connections that preserve metric compatibility but *violate* torsion-freeness — these are Amari's α-connections, the subject of Lecture 03.

### 5.3 Curvature

**Definition 1.10 (Riemann Curvature Tensor).** The *Riemann curvature endomorphism* $R: \mathfrak{X}(M)^3 \to \mathfrak{X}(M)$ is defined by:
$$R(X, Y)Z = \nabla_X \nabla_Y Z - \nabla_Y \nabla_X Z - \nabla_{[X,Y]} Z.$$

In coordinates, the components $R_{ijk}^l$ are defined by $R(\partial_i, \partial_j)\partial_k = R_{ijk}^l\, \partial_l$.

The *sectional curvature* of a 2-plane $\sigma = \text{span}(v, w) \subseteq T_pM$ is:
$$K(\sigma) = K(v, w) = \frac{g(R(v,w)w, v)}{g(v,v)\,g(w,w) - g(v,w)^2}.$$

A manifold has *constant curvature* $\kappa$ if $K(\sigma) = \kappa$ for all $\sigma$ and all $p$.

**For the binomial manifold** $\mathcal{B}(n, p)$ with the Fisher-Rao metric $g = \frac{n}{p(1-p)}\, dp^2$, one computes $K = -1/4$ — constant negative curvature, the geometry of a hyperbolic half-plane.

## 6. Geodesics

**Definition 1.11 (Geodesic).** A smooth curve $\gamma: I \to M$ is a *geodesic* if it satisfies:
$$\nabla_{\dot{\gamma}} \dot{\gamma} = 0,$$
i.e., its velocity is parallel-transported along itself. In coordinates, this gives the *geodesic equation*:
$$\ddot{\gamma}^k(t) + \Gamma_{ij}^k(\gamma(t))\, \dot{\gamma}^i(t)\, \dot{\gamma}^j(t) = 0.$$

**Theorem 1.12 (Existence and Uniqueness of Geodesics).** For every $p \in M$ and $v \in T_pM$, there exists a unique maximal geodesic $\gamma_v: I_v \to M$ with $\gamma(0) = p$ and $\dot{\gamma}(0) = v$.

The *exponential map* $\exp_p: T_pM \supseteq U \to M$ is defined by $\exp_p(v) = \gamma_v(1)$, where $U$ is a neighborhood of $0 \in T_pM$ on which $\exp_p$ is defined. The exponential map is a local diffeomorphism near the origin, giving *normal coordinates* $(r^1, \ldots, r^n)$ in which $\Gamma_{ij}^k(0) = 0$ and $g_{ij}(0) = \delta_{ij}$.

## 7. Submanifolds and the Second Fundamental Form

**Definition 1.13 (Embedded Submanifold).** A subset $S \subseteq M$ is an *embedded submanifold* of dimension $k$ if, for every $p \in S$, there exists a chart $(U, \varphi)$ of $M$ with $p \in U$ such that $\varphi(U \cap S) = \varphi(U) \cap (\mathbb{R}^k \times \{0\}^{n-k})$.

For a submanifold $S \hookrightarrow M$, the tangent space at $p$ decomposes as $T_pM = T_pS \oplus N_pS$, where $N_pS$ is the *normal space*. The *second fundamental form* $\text{II}: T_pS \times T_pS \to N_pS$ measures how $S$ curves in $M$:
$$\text{II}(v, w) = (\nabla_v w)^\perp,$$
where $\nabla$ is the Levi-Civita connection of $M$ and $\perp$ denotes the normal component. This object will reappear when we study the curvature of statistical submanifolds, such as the exponential family within the simplex.

## 8. Summary and Forward Look

We have established the differential-geometric scaffolding:

| Concept | Definition | Statistical Interpretation |
|---------|-----------|---------------------------|
| Smooth manifold | Charts and transition maps | Smooth parameter space |
| Tangent space $T_pM$ | Derivations at $p$ | Directions of parameter perturbation |
| Riemannian metric $g$ | Smooth inner product on $T_pM$ | Fisher information matrix (Lecture 02) |
| Levi-Civita connection $\nabla$ | Unique torsion-free, metric-compatible connection | Expected geometry (Lecture 03) |
| Geodesic | $\nabla_{\dot{\gamma}}\dot{\gamma} = 0$ | Shortest paths in Fisher-Rao distance |
| Curvature | Non-commutativity of parallel transport | Sensitivity of statistical inference (Lecture 02) |

In Lecture 02, we will endow the statistical manifold with the Fisher-Rao metric — the *unique* Riemannian metric (up to conformal scaling) invariant under sufficient statistics, as proved by Chentsov (1982). This is where information geometry truly begins.

---

## Exercises

1. **(Coordinate transitions)** Consider $\mathbb{R}^2$ with polar coordinates $(r, \theta)$ and Cartesian coordinates $(x, y)$. Compute the Jacobian of the transition map and verify that the Euclidean metric $g = dx^2 + dy^2$ transforms to $g = dr^2 + r^2\,d\theta^2$.

2. **(Fisher metric on the simplex)** The probability simplex $\Delta^{n-1} = \{(p_1, \ldots, p_n) : p_i > 0, \sum p_i = 1\}$ has the Fisher-Rao metric $g_{ij} = \delta_{ij}/p_i - 1$. Compute the Christoffel symbols and verify that setting all $p_i = 1/n$ gives $\Gamma_{ij}^k = 0$ at the barycenter.

3. **(Hyperbolic metric)** On the upper half-plane $\mathbb{H} = \{(x, y) \in \mathbb{R}^2 : y > 0\}$ with metric $g = (dx^2 + dy^2)/y^2$, show that the Christoffel symbols are $\Gamma_{12}^1 = \Gamma_{21}^1 = \Gamma_{22}^2 = -1/y$, $\Gamma_{11}^2 = 1/y$, $\Gamma_{11}^1 = \Gamma_{22}^1 = \Gamma_{12}^2 = \Gamma_{21}^2 = 0$, and that the geodesics are semicircles centered on the $x$-axis (and vertical lines).

4. **(Pullback via a statistical embedding)** Let $\phi: \mathbb{R}^n \to \Delta^{n-1}$ be the softmax map $\phi(\theta)_i = e^{\theta_i}/\sum_j e^{\theta_j}$. Compute the pullback $\phi^* g$ of the Fisher metric from the simplex. What familiar object do you obtain?

5. **(Non-metric connections)** Give an example of an affine connection on $\mathbb{R}^2$ that is not metric-compatible with the Euclidean metric. Compute its torsion tensor.