# Lecture 03: Amari's Information Geometry

## α-Geometry, Dual Connections, Divergence Functions

> *"The Levi-Civita connection is the trunk of Yggdrasil, but the branches reach into α-space — and there, the dual roots drink from different streams."*

---

## 1. Beyond the Levi-Civita Connection

The fundamental theorem of Riemannian geometry (Lecture 01) guarantees a unique torsion-free, metric-compatible connection — the Levi-Civita connection. But in information geometry, we free ourselves from the requirement of torsion-freeness. Why? Because statistical manifolds carry *two* natural families of connections, each geometrically meaningful, and their interplay reveals structure invisible to the Levi-Civita connection alone.

Recall: an *affine connection* $\nabla$ on a smooth manifold $M$ satisfies:
1. $\nabla_{fX+gY}Z = f\nabla_XZ + g\nabla_YZ$
2. $\nabla_X(fY) = X(f)Y + f\nabla_XY$

The *torsion tensor* of $\nabla$ is $T^\nabla(X,Y) = \nabla_XY - \nabla_YX - [X,Y]$. The Levi-Civita connection has $T = 0$.

**Definition 3.1 (Metric-Compatiblity).** A connection $\nabla$ is *metric-compatible* with $(M, g)$ if:
$$X\,g(Y,Z) = g(\nabla_X Y, Z) + g(Y, \nabla_X Z) \quad \forall\, X,Y,Z \in \mathfrak{X}(M).$$

For a *metric-compatible* connection, parallel transport preserves inner products. This is essential for our purposes — we want geometric structure that respects the Fisher metric.

## 2. The Exponential and Mixture Families

Before introducing α-connections, we must understand the two fundamental coordinate systems of information geometry.

**Definition 3.2 (Exponential Family).** A statistical model $\mathcal{S}$ is an *exponential family* if distributions can be written as:
$$p(x;\theta) = \exp\!\left(\theta^i T_i(x) - \psi(\theta)\right)h(x),$$
where $\theta = (\theta^1, \ldots, \theta^n)$ are the *natural parameters*, $T_i$ are sufficient statistics, and $\psi(\theta) = \log \int e^{\theta^i T_i(x)}h(x)\,d\mu(x)$ is the *cumulant function* (log-partition function).

The natural parameter space $\Theta = \{\theta : \psi(\theta) < \infty\}$ is convex.

**Definition 3.3 (Mixture Family).** A statistical model $\mathcal{S}$ is a *mixture family* if distributions can be written as:
$$p(x;\eta) = \eta^i p_i(x) + \left(1 - \sum_i \eta^i\right) p_0(x), \quad \eta \in \Delta^{n-1}_\text{int},$$
where $p_0, p_1, \ldots, p_n$ are fixed linearly independent probability distributions and $\eta$ are the *mixture parameters*.

### 2.1 Duality of Coordinate Systems

These two families are *dual* to each other. The Legendre transform connects them:

**Theorem 3.4 (Legendre Duality).** For a regular exponential family, the map $\theta \mapsto \eta = \nabla_\theta\psi(\theta)$ is a diffeomorphism from the natural parameter space $\Theta$ to the *expectation parameter space* $\mathcal{E} = \{\eta : \eta_i = \mathbb{E}_\theta[T_i(x)]\}$. The inverse is $\eta \mapsto \theta = \nabla_\eta\psi^*(\eta)$, where $\psi^*(\eta) = \sup_\theta\{\theta^\top\eta - \psi(\theta)\}$ is the convex conjugate.

The expectation parameters $\eta$ are the *mixture coordinates* (also called *η-coordinates* or *dual coordinates*). The Fisher information matrices in these two coordinate systems satisfy:
$$\mathcal{I}(\theta) = \nabla^2_\theta\psi(\theta) = \frac{\partial\eta_i}{\partial\theta^j}, \qquad \mathcal{I}(\eta) = \nabla^2_\eta\psi^*(\eta) = \frac{\partial\theta^i}{\partial\eta_j} = \mathcal{I}(\theta)^{-1}.$$

These are *inverse* matrices in dual coordinates — a fact with profound geometric consequences.

## 3. Amari's α-Connections

**Definition 3.5 (α-Connection).** Let $(\mathcal{S}, g)$ be a statistical manifold with Fisher metric $g_{ij}$. The *α-connection* $\nabla^{(\alpha)}$ for $\alpha \in \mathbb{R}$ is the affine connection with Christoffel symbols:
$$\Gamma_{ij,k}^{(\alpha)} = \Gamma_{ij,k}^{(0)} + \frac{\alpha}{2}\,T_{ijk},$$
where $\Gamma_{ij,k}^{(0)}$ are the Christoffel symbols of the Levi-Civita connection (i.e., the *0-connection*), and:
$$T_{ijk} = \mathbb{E}_\theta\!\left[\frac{\partial \log p}{\partial\theta^i}\cdot\frac{\partial \log p}{\partial\theta^j}\cdot\frac{\partial \log p}{\partial\theta^k}\right]$$
is the *skewness tensor* (also called the *cubic tensor* or *Amari tensor*).

The indices are lowered: $\Gamma_{ij,k}^{(\alpha)} = g_{kl}\,\Gamma_{ij}^{(\alpha)\,l}$, so:
$$\nabla^{(\alpha)}_{\partial_i}\partial_j = \Gamma_{ij}^{(\alpha)\,l}\,\partial_l, \quad \text{where } \Gamma_{ij}^{(\alpha)\,l} = g^{lk}\,\Gamma_{ij,k}^{(\alpha)}.$$

### 3.1 Key Properties of α-Connections

**Proposition 3.6.** For any $\alpha \in \mathbb{R}$:
1. $\nabla^{(\alpha)}$ is *metric-compatible* with the Fisher metric: $X\,g(Y,Z) = g(\nabla^{(\alpha)}_X Y, Z) + g(Y, \nabla^{(-\alpha)}_X Z)$. Note the *opposite* α on the right side!
2. The torsion of $\nabla^{(\alpha)}$ is $T^{(\alpha)}_{ijk} = \alpha\,S_{ijk}$ where $S_{ijk} = \frac{1}{2}(T_{ijk} - T_{ikj})$ is the antisymmetrized cubic tensor.
3. $\nabla^{(0)}$ is the Levi-Civita connection (torsion-free).
4. $\nabla^{(\alpha)}$ and $\nabla^{(-\alpha)}$ are *dual* connections in the sense of Definition 3.7.

**Definition 3.7 (Dual Connections).** Two affine connections $\nabla$ and $\nabla^*$ on $(M, g)$ are *dual* with respect to $g$ if for all vector fields $X, Y, Z$:
$$X\,g(Y,Z) = g(\nabla_X Y, Z) + g(Y, \nabla^*_X Z).$$

This means: parallel transporting $Y$ along curve $\gamma$ with $\nabla$ and parallel transporting $Z$ along the same curve with $\nabla^*$ both preserve the inner product $g(Y, Z)$ at the endpoints.

### 3.2 The Canonical Pair: $\nabla^{(1)}$ and $\nabla^{(-1)}$

The connections $\nabla^{(1)}$ (the *exponential connection*) and $\nabla^{(-1)}$ (the *mixture connection*) are the most important in practice:

- **$\nabla^{(1)}$-flatness (e-flatness):** A submanifold is *e-flat* if it is autoparallel with respect to $\nabla^{(1)}$, meaning that the $\nabla^{(1)}$-geodesics starting in the submanifold stay within it. Equivalently, the $\nabla^{(1)}$-Christoffel symbols vanish in natural coordinates: in $\theta$-coordinates, $\Gamma_{ij}^{(1)\,k} = 0$ for an exponential family.

- **$\nabla^{(-1)}$-flatness (m-flatness):** A submanifold is *m-flat* if it is autoparallel with respect to $\nabla^{(-1)}$. In $\eta$-coordinates (mixture coordinates), $\Gamma_{ij}^{(-1)\,k} = 0$ for a mixture family.

**Theorem 3.8 (Flatness of Exponential and Mixture Families).**
1. An exponential family is e-flat (in $\theta$-coordinates, all $\Gamma_{ij}^{(1)\,k} = 0$).
2. A mixture family is m-flat (in $\eta$-coordinates, all $\Gamma_{ij}^{(-1)\,k} = 0$).

This is why these coordinates are "natural" for each type of family: they linearize the respective connection's geodesics.

### 3.3 General α-Flatness

More generally, a statistical manifold is *α-flat* if $\nabla^{(\alpha)}$-geodesics are straight lines in some coordinate system. The key structural theorem:

**Theorem 3.9 (Amari).** A statistical manifold is α-flat if and only if it is $(-\alpha)$-flat. The manifold is 0-flat (Levi-Civita flat) if and only if the cubic tensor $T_{ijk}$ vanishes everywhere — i.e., the manifold has dual constant curvature $\kappa$ with curvature tensor related to $T_{ijk} = 0$.

For a general exponential family, $\nabla^{(\alpha)}$-flat coordinates are given by the *α-embeddings*:
$$\ell^{(\alpha)}(\theta) = \begin{cases} \frac{2}{1-\alpha}\,p(x;\theta)^{(1-\alpha)/2} & \alpha \neq 1 \\ \log p(x;\theta) & \alpha = 1 \end{cases}$$

and the $\nabla^{(\alpha)}$-geodesics are straight-line interpolations in the $(1+\alpha)/2$-representation of $p$.

## 4. Divergence Functions

### 4.1 f-Divergences

**Definition 3.10 (f-Divergence).** Let $f: (0,\infty) \to \mathbb{R}$ be a convex function with $f(1) = 0$. The *f-divergence* between $p$ and $q$ is:
$$D_f(p\|q) = \int f\!\left(\frac{p(x)}{q(x)}\right) q(x)\,d\mu(x),$$
with the convention $f(0) = \lim_{t\to 0^+} f(t)$.

Important instances:
- **KL divergence:** $f(t) = t\log t$, giving $D_{KL}(p\|q) = \int p\log(p/q)\,d\mu$.
- **Reverse KL:** $f(t) = -\log t$, giving $D_{KL}(q\|p)$.
- **α-divergence:** $f(t) = \frac{4}{1-\alpha^2}\!\left(1 - t^{(1+\alpha)/2}t^{(1-\alpha)/2}\right)$ for $\alpha \neq \pm 1$, giving:
  $$D^{(\alpha)}(p\|q) = \frac{4}{1-\alpha^2}\left(1 - \int p(x)^{\frac{1+\alpha}{2}}q(x)^{\frac{1-\alpha}{2}}\,d\mu(x)\right).$$
- **Hellinger distance:** $\alpha = 0$: $D^{(0)}(p\|q) = 4\!\left(1 - \int \sqrt{pq}\,d\mu\right) = d_H(p,q)^2$.
- **χ²-divergence:** $\alpha = 3$: $f(t) = (t-1)^2/t$, giving $\chi^2(p\|q) = \int(p-q)^2/q\,d\mu$.

### 4.2 Bregman Divergences

**Definition 3.11 (Bregman Divergence).** Let $\psi: \Omega \to \mathbb{R}$ be a $C^2$-strictly-convex function on a convex domain $\Omega \subseteq \mathbb{R}^n$. The *Bregman divergence* generated by $\psi$ is:
$$B_\psi(\theta\|\theta') = \psi(\theta) - \psi(\theta') - \nabla\psi(\theta')^\top(\theta - \theta').$$

This is the "gap" between $\psi(\theta)$ and its first-order Taylor approximation at $\theta'$.

**Theorem 3.12 (Bregman = Canonical Divergence for Dually Flat Spaces).** On a dually flat statistical manifold (one that is flat with respect to both $\nabla^{(1)}$ and $\nabla^{(-1)}$), the Bregman divergence $B_\psi(\theta\|\theta')$ in natural coordinates coincides with the KL divergence $D_{KL}(p_{\theta'}\|p_\theta)$.

In other words, on an exponential family with natural parameters $\theta$ and expectation parameters $\eta = \nabla\psi(\theta)$:
$$D_{KL}(p_{\theta'}\|p_\theta) = B_\psi(\theta'\|\theta) = \psi(\theta') - \psi(\theta) - (\theta' - \theta)^\top\nabla\psi(\theta).$$

The reversed KL divergence in the same coordinates is:
$$D_{KL}(p_\theta\|p_{\theta'}) = B_{\psi^*}(\eta\|\eta'),$$
where $\psi^*$ is the convex conjugate. This elegant duality captures the fundamental asymmetry of KL divergence as a manifestation of the Legendre duality in exponential families.

### 4.3 The α-Divergence and Fisher Metric

The infinitesimal behavior of the α-divergence recovers the Fisher metric:

**Theorem 3.13.** For any $\alpha \neq \pm 1$:
$$D^{(\alpha)}(p_\theta\|p_{\theta+\delta\theta}) = \frac{1}{2}\,\delta\theta^\top\,\mathcal{I}(\theta)\,\delta\theta + O(\|\delta\theta\|^3).$$

All α-divergences share the same second-order approximation — the Fisher metric. They differ only in their third-order (and higher) behavior, which is controlled by $\alpha$. This is why the Fisher-Rao metric is the *unique* Riemannian metric consistent with all f-divergences.

## 5. The Fundamental Theorem of Dual Connections

**Theorem 3.14 (Amari & Nagaoka, 2000).** Let $(M, g, \nabla, \nabla^*)$ be a manifold with metric $g$ and dual connections $\nabla, \nabla^*$. Then:

1. **Generalized Pythagorean theorem:** If $\gamma$ is a $\nabla$-geodesic, $\sigma$ is a $\nabla^*$-geodesic, and $\nabla^*_{\dot{\gamma}}\dot{\sigma} = 0$ at their intersection point $q$ (i.e., the geodesics are orthogonal in the dual sense), then for any point $p$ on $\gamma$ and $r$ on $\sigma$:
   $$D^{(\alpha)}(p\|r) = D^{(\alpha)}(p\|q) + D^{(\alpha)}(q\|r).$$

2. **Generalized projection theorem:** Given a $\nabla^*$-flat submanifold $S$ and a point $p \notin S$, the point $q \in S$ minimizing $D^{(\alpha)}(p\|\cdot)$ is the dual projection of $p$ onto $S$ — given by the $\nabla^*$-geodesic from $p$ that intersects $S$ $\nabla$-orthogonally.

These generalize the Euclidean Pythagorean theorem and least-squares projection. In the Euclidean case ($\nabla = \nabla^*$ = flat, $g = I$), we recover the standard $|p-r|^2 = |p-q|^2 + |q-r|^2$ and orthogonal projection.

### 5.1 The Dual Pythagorean Theorem on the Simplex

On $\Delta^{n-1}$ with the e-connection $\nabla^{(1)}$ and m-connection $\nabla^{(-1)}$:

- The $\nabla^{(1)}$-geodesic from $p$ to $q$ is the *e-geodesic*: $p^{(t)} \propto p^{1-t}q^t$ (exponential interpolation in $\theta$-space).
- The $\nabla^{(-1)}$-geodesic from $p$ to $q$ is the *m-geodesic*: $p^{(t)} = (1-t)p + tq$ (linear interpolation in $\eta$-space).

The Pythagorean theorem states: if e-geodesic $\overline{pr}$ is $\nabla^{(-1)}$-orthogonal to m-geodesic $\overline{qr}$ at $r$, then:
$$D_{KL}(p\|q) = D_{KL}(p\|r) + D_{KL}(r\|q).$$

This is the *information-geometric Pythagorean theorem* — KL divergence decomposes like squared Euclidean distance!

## 6. Curvature of α-Connections

### 6.1 The α-Curvature Tensor

The Riemann curvature tensor of $\nabla^{(\alpha)}$ is defined in the usual way:
$$R^{(\alpha)}(X,Y)Z = \nabla^{(\alpha)}_X\nabla^{(\alpha)}_YZ - \nabla^{(\alpha)}_Y\nabla^{(\alpha)}_XZ - \nabla^{(\alpha)}_{[X,Y]}Z.$$

**Theorem 3.15 (Amari).** The α-curvature of an exponential family is:
$$R^{(\alpha)}_{ijkl} = \frac{\alpha^2 - 1}{4}\left(T_{ija}\,g^{ab}\,T_{klb} - T_{kla}\,g^{ab}\,T_{ijb}\right).$$

Note the remarkable factor $(\alpha^2 - 1)/4$. This implies:
- $R^{(\alpha)} = 0$ for $\alpha = \pm 1$ — the exponential and mixture connections are *flat*.
- $R^{(\alpha)} = R^{(-\alpha)}$ — the α-curvature depends only on $\alpha^2$.
- The Levi-Civita curvature ($\alpha = 0$) is $R^{(0)} = -\frac{1}{4}\left(T_{ija}\,g^{ab}\,T_{klb} - T_{kla}\,g^{ab}\,T_{ijb}\right) \neq 0$ in general.

### 6.2 Constant Curvature and the Cosh Manifold

For a statistical manifold with *constant α-curvature*, the cubic tensor satisfies a self-reproduction property:
$$T_{ijk}\,T_{lmn} = \kappa\,(g_{il}g_{jm}g_{kn} + \text{sym})$$
for some constant $\kappa$. The normal family $\mathcal{N}(\mu, \sigma^2)$ (with both parameters free) satisfies this and has constant Levi-Civita curvature $\kappa = -1/2$ (like a hyperbolic space).

The cosh-geometry emerges: the geodesic distance for the Fisher-Rao metric on the normal family is:
$$d_{FR}(\theta_1, \theta_2) = 2\,\text{arccosh}\!\left(\cosh\!\left(\frac{\delta\mu}{2\sigma}\right)\right),$$
where $\delta\mu$ and $\sigma$ are measured in the natural affine coordinates.

## 7. The Tangent Bundle as a Statistical Object

The tangent bundle $T\mathcal{S}$ of a statistical manifold $\mathcal{S}$ carries additional structure. The dual pair $(\nabla^{(\alpha)}, \nabla^{(-\alpha)})$ induces a *splitting* of $TT\mathcal{S}$ into horizontal and vertical subspaces:
$$T_{(p,v)}(T\mathcal{S}) = H^{(\alpha)}_{(p,v)} \oplus V_{(p,v)},$$
where the horizontal subspace $H^{(\alpha)}$ depends on the connection $\nabla^{(\alpha)}$.

This splitting is essential for defining *geodesic spray* equations and understanding the second-order geometry of statistical models. It is also the starting point for information-geometric approaches to *second-order asymptotics* (Edgeworth expansions, higher-order Cramér-Rao inequalities), where the cubic tensor $T_{ijk}$ governs third-order terms.

## 8. Summary: The α-Unified Framework

| Object | α = 1 | α = 0 | α = −1 |
|--------|-------|-------|--------|
| Connection | Exponential ($\nabla^{(1)}$) | Levi-Civita ($\nabla^{(0)}$) | Mixture ($\nabla^{(-1)}$) |
| Coordinates | θ (natural) | Fisher-Rao | η (expectation) |
| Flatness | e-flat | Curved | m-flat |
| Geodesics | exp. interpolation | Fisher-Rao | linear interpolation |
| Divergence | Reverse KL / Bregman | Fisher-Rao distance | KL divergence |
| Curvature | $R^{(1)} = 0$ | $R^{(0)} \neq 0$ | $R^{(-1)} = 0$ |
| Torsion | Nonzero | Zero | Nonzero |

The entire menagerie of statistical divergences, coordinate systems, and geometric structures is unified by the single parameter $\alpha$. Each value of $\alpha$ reveals a different face of the same statistical manifold, like the many faces of the Norns who see past, present, and future simultaneously.

---

## Exercises

1. **(α-Christoffel symbols for the normal family)** Compute $\Gamma_{ij}^{(\alpha)\,k}$ for the bivariate normal family $\mathcal{N}(\mu, \sigma^2)$ (with $\sigma$ free, not $\sigma^2$). Show that $\Gamma_{ij}^{(1)\,k} = 0$ in the natural parameters $(\theta^1, \theta^2) = (\mu/\sigma^2, -1/2\sigma^2)$ and $\Gamma_{ij}^{(-1)\,k} = 0$ in the expectation parameters $(\eta^1, \eta^2) = (\mu, \mu^2 + \sigma^2)$.

2. **(Generalized Pythagorean theorem)** Let $p = (0.5, 0.3, 0.2)$, $q = (0.1, 0.8, 0.1)$, $r = (0.3, 0.5, 0.2)$ on $\Delta^2$. Verify numerically that $D_{KL}(p\|r) + D_{KL}(r\|q) = D_{KL}(p\|q)$ if and only if $r$ lies on both the e-geodesic $\overline{pq}$ and the Pythagorean condition is satisfied.

3. **(Bregman divergence and convex conjugates)** For $\psi(\theta) = -\frac{1}{2}\log(-2\theta)$ (the cumulant function of $\mathcal{N}(0, \sigma^2)$ with $\theta = -1/2\sigma^2$), compute the convex conjugate $\psi^*(\eta)$ and verify that $B_\psi(\theta'\|\theta) = D_{KL}(p_{\theta'}\|p_\theta)$.

4. **(α-divergence limit)** Compute $\lim_{\alpha \to 1} D^{(\alpha)}(p\|q)$ and $\lim_{\alpha \to -1} D^{(\alpha)}(p\|q)$. Show that these recover (scaled) KL and reverse-KL respectively. What happens at $\alpha = 0$?

5. **(Cubic tensor for multinomial)** Compute $T_{ijk}$ for the multinomial family on $\Delta^{n-1}$ with parameters $\pi_1, \ldots, \pi_{n-1}$. Show that $T_{ijk} = \frac{\partial^3\psi}{\partial\theta^i\partial\theta^j\partial\theta^k}$ in natural coordinates, where $\psi(\theta) = \log(1 + \sum e^{\theta^i})$.