# Lecture 04: Riemannian Optimization

## Natural Gradient Descent, Riemannian SGD, Geodesic Methods

> *"Odin gave an eye for wisdom; we give a Hessian for geometry. The natural gradient walks the curved earth — the Euclidean gradient merely flattens it."*

---

## 1. Optimization on Riemannian Manifolds

Consider the optimization problem:
$$\min_{\theta \in \mathcal{M}} \mathcal{L}(\theta),$$
where $(\mathcal{M}, g)$ is a Riemannian manifold — in our case, the statistical manifold $(\Theta, \mathcal{I})$ equipped with the Fisher-Rao metric.

On Euclidean space $\mathbb{R}^n$, gradient descent updates $\theta \leftarrow \theta - \eta\nabla\mathcal{L}$, following the steepest descent direction in the $\ell^2$-norm. On a Riemannian manifold, the steepest descent direction depends on the metric:

**Definition 4.1 (Riemannian Gradient).** The *Riemannian gradient* $\text{grad}\,\mathcal{L} \in T_\theta\mathcal{M}$ of $\mathcal{L}: \mathcal{M} \to \mathbb{R}$ at $\theta$ is the unique tangent vector satisfying:
$$g_\theta(\text{grad}\,\mathcal{L}, v) = d\mathcal{L}_\theta(v) \quad \forall\, v \in T_\theta\mathcal{M}.$$

In coordinates: $\text{grad}\,\mathcal{L} = g^{ij}\,\partial_j\mathcal{L}\,\partial_i$.

The Riemannian gradient generalizes the Euclidean gradient by "rescaling" descent directions according to the local geometry. On the statistical manifold, this rescaling is performed by the Fisher information matrix:
$$\text{grad}\,\mathcal{L}(\theta) = \mathcal{I}(\theta)^{-1}\,\nabla_\theta\mathcal{L}(\theta),$$
which is precisely the natural gradient (Lecture 02, Definition 2.9).

## 2. Natural Gradient Descent

### 2.1 The Algorithm

**Algorithm 4.2 (Natural Gradient Descent).**
```
Input: Initial parameters θ₀, learning rate η
For t = 0, 1, 2, ...:
    Compute gradient: gₜ = ∇_θ L(θₜ)
    Compute/estimate Fisher: Fₜ = I(θₜ)
    Natural gradient: ãₜ = Fₜ⁻¹ gₜ
    Update: θₜ₊₁ = θₜ - η ãₜ
```

**Theorem 4.3 (Invariance of Natural Gradient).** Let $\phi = \psi(\theta)$ be a diffeomorphic reparameterization. Then the natural gradient update in $\phi$-coordinates:
$$\phi_{t+1} = \phi_t - \eta\,\mathcal{I}_\phi(\phi_t)^{-1}\,\nabla_\phi\mathcal{L}(\phi_t)$$
is equivalent to the $\theta$-coordinate update under the pushforward $d\psi$. That is: natural gradient descent is *parameterization-invariant*.

*Proof.* Under reparameterization, the gradient transforms as $\nabla_\phi\mathcal{L} = J^{-\top}\nabla_\theta\mathcal{L}$ (where $J = \partial\theta/\partial\phi$), and the Fisher matrix transforms as $\mathcal{I}_\phi = J^{-1}\mathcal{I}_\theta J^{-\top}$. Therefore:
$$\mathcal{I}_\phi^{-1}\nabla_\phi\mathcal{L} = (J^{-1}\mathcal{I}_\theta J^{-\top})^{-1}J^{-\top}\nabla_\theta\mathcal{L} = J\,\mathcal{I}_\theta^{-1}\,J^{-1}\,J^{-\top}\,\nabla_\theta\mathcal{L}\cdot J^\top = J\,\mathcal{I}_\theta^{-1}\nabla_\theta\mathcal{L}.$$
The update $\phi_{t+1} = \phi_t - \eta\,\mathcal{I}_\phi^{-1}\nabla_\phi\mathcal{L}$ maps to $\theta_{t+1} = \theta_t - \eta\,\mathcal{I}_\theta^{-1}\nabla_\theta\mathcal{L}$, exactly as claimed. □

This invariance is a profound result: natural gradient descent "sees" the same optimization landscape regardless of how we choose to parameterize our model. Euclidean gradient descent does *not* possess this invariance — in different parameterizations, it can converge to different points or diverge entirely.

### 2.2 Natural Gradient as Second-Order Method

**Theorem 4.4 (Fisher-Newton Connection).** For the negative log-likelihood loss $\mathcal{L}(\theta) = -\mathbb{E}_{x\sim p_{\text{data}}}[\log p(x;\theta)]$, the Fisher matrix and the empirical Hessian satisfy:
$$\mathbb{E}_{x\sim p_\theta}\!\left[\nabla^2_\theta \log p(x;\theta)\right] = \mathcal{I}(\theta) - \mathbb{E}_{x\sim p_\theta}\!\left[\nabla_\theta\log p \cdot \nabla_\theta\log p^\top\right] + \mathbb{E}_{x\sim p_\theta}\!\left[\nabla_\theta\log p \cdot \nabla_\theta\log p^\top\right] = \mathcal{I}(\theta).$$

More precisely: $\mathcal{I}(\theta) = \mathbb{E}_{p_\theta}[s\,s^\top]$ and $H_\mathcal{L}(\theta) = \nabla^2_\theta\mathcal{L}(\theta) = \mathbb{E}_{p_\text{data}}[-\nabla^2\log p]$. The Fisher matrix is the *expected* Hessian of the log-likelihood, while $H_\mathcal{L}$ is the *empirical* Hessian. When $p_\theta = p_{\text{data}}$ (i.e., the model is perfectly trained), $\mathcal{I} \approx H_\mathcal{L}$, and natural gradient closely approximates Newton's method.

### 2.3 Convergence Analysis

**Theorem 4.5 (Convergence Rate of Natural Gradient).** Consider natural gradient descent on $(\mathcal{M}, g)$ with step size $\eta$. Under the assumptions:
- $\mathcal{L}$ is $L$-smooth with respect to the Riemannian metric: $\|\text{grad}\,\mathcal{L}(\theta) - P_{\gamma}\,\text{grad}\,\mathcal{L}(\theta')\|_\theta \leq L\,d(\theta, \theta')$ for all $\theta, \theta'$, where $P_\gamma$ denotes parallel transport along the geodesic $\gamma$ from $\theta'$ to $\theta$.
- The natural gradient is $\mu$-bounded below: $\mathcal{L}(\theta) - \mathcal{L}(\theta^*) \leq \frac{1}{2\mu}\|\text{grad}\,\mathcal{L}(\theta)\|_\theta^2$.

Then natural gradient descent achieves the convergence rate:
$$\mathcal{L}(\theta_T) - \mathcal{L}(\theta^*) \leq \left(1 - \frac{\mu}{L}\right)^T(\mathcal{L}(\theta_0) - \mathcal{L}(\theta^*)).$$

The condition number $\kappa = L/\mu$ is the *Riemannian* condition number — measured in terms of the intrinsic curvature of the loss landscape, not the arbitrary coordinate condition number. This can be dramatically better than the Euclidean condition number in ill-conditioned parameterizations.

## 3. Practical Approximations

### 3.1 The Computational Bottleneck

For a modern neural network with $d$ parameters (e.g., $d \sim 10^9$ for a large language model), computing $\mathcal{I}(\theta)^{-1}\nabla\mathcal{L}$ requires $O(d^2)$ storage and $O(d^3)$ computation. This is infeasible. Practical natural gradient methods must approximate.

### 3.2 Diagonal Fisher (AdaGrad / Adam)

The simplest approximation: $\mathcal{I}(\theta) \approx \text{diag}(\mathcal{I}(\theta))$. The natural gradient becomes:
$$\tilde{\nabla}_\theta\mathcal{L} \approx \text{diag}(\mathcal{I}(\theta))^{-1}\,\nabla_\theta\mathcal{L} = \left(\frac{\partial\mathcal{L}/\partial\theta_1}{\mathcal{I}_{11}}, \ldots, \frac{\partial\mathcal{L}/\partial\theta_d}{\mathcal{I}_{dd}}\right)^\top.$$

**AdaGrad** accumulates the diagonal: $\hat{\mathcal{I}}_{ii} = \sum_{t} (\partial\mathcal{L}/\partial\theta_i)^2$, giving per-coordinate adaptive learning rates. **Adam** uses exponential moving averages. Both are *degenerate* natural gradient methods — they miss all off-diagonal curvature information.

### 3.3 Kronecker-Factored Approximate Curvature (K-FAC)

For a neural network with layers $l = 1, \ldots, L$, the Fisher matrix has a block structure. K-FAC (Martens & Grosse, 2015) approximates each block as:
$$\mathcal{I}_{ll'} \approx \mathbb{E}[a_{l-1}a_{l-1}^\top] \otimes \mathbb{E}[\nabla_{z_l}\mathcal{L}\,\nabla_{z_l}\mathcal{L}^\top] = A_{l-1} \otimes G_l,$$
where $a_{l-1}$ is the pre-activation of layer $l-1$ and $\nabla_{z_l}\mathcal{L}$ is the gradient with respect to pre-activations. The Kronecker product reduces storage from $O(d_l^2 d_{l-1}^2)$ to $O(d_l^2 + d_{l-1}^2)$ and inversion from $O(d_l^3 d_{l-1}^3)$ to $O(d_l^3 + d_{l-1}^3)$.

**Theorem 4.6 (K-FAC Inverse).** Under the K-FAC approximation, the inverse Fisher block is:
$$(A_{l-1} \otimes G_l)^{-1} = A_{l-1}^{-1} \otimes G_l^{-1},$$
reducing inversion to two small matrix inversions.

K-FAC has been shown to achieve near-Newton convergence rates on deep networks while remaining computationally tractable. Its key insight is that statistical independence between activations and backpropagated gradients makes the Kronecker factorization a good *structural* approximation, not merely a *low-rank* one.

### 3.4 Trust Region Methods (TRPO)

**Definition 4.7 (Trust Region Update).** The *trust region* natural gradient update solves:
$$\max_\theta\, \nabla_\theta\mathcal{L}(\theta_t)^\top\,\delta\theta \quad \text{subject to} \quad \delta\theta^\top\,\mathcal{I}(\theta_t)\,\delta\theta \leq \epsilon,$$
which gives the closed-form solution $\delta\theta = \frac{1}{\lambda}\mathcal{I}(\theta_t)^{-1}\nabla_\theta\mathcal{L}(\theta_t)$ where $\lambda$ is chosen to satisfy the constraint.

This is the foundation of **TRPO** (Trust Region Policy Optimization) in reinforcement learning, where $\mathcal{L}$ is the policy gradient and the trust region constraint ensures that each policy update is "small" in Fisher-Rao distance, preventing catastrophic policy collapse.

## 4. Riemannian Stochastic Gradient Descent

### 4.1 The Algorithm

**Algorithm 4.8 (Riemannian SGD).**
```
Input: Initial θ₀, learning rate schedule ηₜ, manifold (M, g)
For t = 0, 1, 2, ...:
    Sample minibatch Bₜ, compute stochastic gradient ĝₜ = ∇_θ L_B(θₜ)
    Compute Riemannian stochastic gradient: Ẽₜ = g(θₜ)⁻¹ ĝₜ  [or use Fisher approximation]
    Retract: θₜ₊₁ = R_θₜ(-ηₜ Ẽₜ)  [or vector transport + exponential map]
```

The *retraction* $R_\theta: T_\theta\mathcal{M} \to \mathcal{M}$ is a first-order approximation to the exponential map:
$$R_\theta(v) = \theta + v + O(\|v\|^2),$$
which maps a tangent vector back to the manifold. Retractions are computationally cheaper than true exponential maps and are essential for optimization on constrained manifolds (e.g., Stiefel manifolds, the positive-definite cone $\mathcal{S}_{++}^n$, the probability simplex $\Delta^{n-1}$).

### 4.2 Convergence of Riemannian SGD

**Theorem 4.9 (Convergence of R-SGD).** Under standard assumptions (bounded stochastic gradient variance, Lipschitz-smooth retraction, sufficient decrease condition), Riemannian SGD with diminishing step size $\eta_t = O(1/\sqrt{t})$ achieves convergence rate $\mathbb{E}[\|\text{grad}\,\mathcal{L}(\theta_t)\|] = O(1/\sqrt{t})$ for non-convex objectives.

For Riemannian *strongly convex* objectives (where the Hessian of $\mathcal{L}$ is positive definite in the Riemannian sense), Riemannian SGD can achieve linear convergence with constant step size, matching Euclidean SGD rates.

### 4.3 Variance Reduction

**Riemannian SVRG** (Zhang et al., 2016) extends Euclidean SVRG to manifolds. The key difficulty is that gradient computations at different points lie in *different* tangent spaces; they must be *parallel-transported* to a common reference point before averaging:

$$\tilde{\nabla}_\theta\mathcal{L} = \text{PT}_{\theta_t \to \tilde{\theta}}(\nabla_\theta\mathcal{L}_{B_t}(\theta_t)) - \text{PT}_{\theta_t \to \tilde{\theta}}(\nabla_\theta\mathcal{L}_{B_t}(\tilde{\theta})) + \nabla_\theta\mathcal{L}(\tilde{\theta}),$$

where $\text{PT}_{\theta \to \tilde{\theta}}$ denotes parallel transport from $T_\theta\mathcal{M}$ to $T_{\tilde{\theta}}\mathcal{M}$ along the geodesic and $\tilde{\theta}$ is a periodically updated reference point. The parallel transport step ensures gradient estimates lie in the same tangent space.

## 5. Geodesic Methods

### 5.1 Geodesic Descent

The most geometrically natural optimization update follows the geodesic in the direction of the Riemannian gradient:
$$\theta_{t+1} = \exp_{\theta_t}(-\eta_t\,\text{grad}\,\mathcal{L}(\theta_t)),$$
where $\exp_\theta: T_\theta\mathcal{M} \supseteq U \to \mathcal{M}$ is the Riemannian exponential map.

**Proposition 4.10 (Geodesic Update as Natural Gradient).** For sufficiently small step sizes $\eta_t$, the geodesic update $\theta_{t+1} = \exp_{\theta_t}(-\eta_t\,\mathcal{I}(\theta_t)^{-1}\nabla\mathcal{L}(\theta_t))$ coincides with the natural gradient update $\theta_{t+1} = \theta_t - \eta_t\,\mathcal{I}(\theta_t)^{-1}\nabla\mathcal{L}(\theta_t)$ up to first order in $\eta_t$.

The difference between the geodesic update and the linear (natural gradient) update is precisely the Christoffel symbol term:
$$\exp_p(v) = p + v + \frac{1}{2}\Gamma^k_{ij}(p)\,v^iv^j\,\partial_k + O(\|v\|^3),$$
where $\Gamma^k_{ij}$ are the Christoffel symbols of the Levi-Civita connection (in the Fisher-Rao case, these are the e-connection Christoffel symbols). The linear update *ignores* the curvature, which is fine for small steps but becomes significant for large steps on highly curved manifolds.

### 5.2 Computing Geodesics on Statistical Manifolds

For general statistical manifolds, the geodesic equation $\ddot{\theta}^k + \Gamma^k_{ij}\,\dot{\theta}^i\dot{\theta}^j = 0$ must be solved numerically. However, for specific families:

- **Exponential families (in $\theta$-coordinates):** The $\nabla^{(1)}$-geodesics are straight lines, so the exponential map for the e-connection is simply $\exp_\theta^{(1)}(v) = \theta + v$.
- **Mixture families (in $\eta$-coordinates):** The $\nabla^{(-1)}$-geodesics are straight lines, so $\exp_\eta^{(-1)}(v) = \eta + v$.
- **Multinomial ($\Delta^{n-1}$):** The Fisher-Rao geodesics are great-circle arcs on the sphere $S^{n-1}$ under the Bhattacharyya embedding. In explicit terms, the geodesic from $p$ to $q$ is:
$$\gamma(t)_i = \frac{(\sqrt{p_i}\cos(t\alpha) + \sqrt{q_i}/C\sin(t\alpha))^2}{\sum_j(\sqrt{p_j}\cos(t\alpha) + \sqrt{q_j}/C\sin(t\alpha))^2}, \quad \alpha = \arccos\left(\sum_i\sqrt{p_iq_i}\right), \; C = 1.$$

### 5.3 Geodesic Convexity

**Definition 4.11 (Geodesic Convexity).** A function $\mathcal{L}: \mathcal{M} \to \mathbb{R}$ is *geodesically convex* if for any geodesic $\gamma: [0,1] \to \mathcal{M}$:
$$\mathcal{L}(\gamma(t)) \leq (1-t)\,\mathcal{L}(\gamma(0)) + t\,\mathcal{L}(\gamma(1)) \quad \forall\, t \in [0,1].$$

Equivalently, $\mathcal{L}$ is geodesically convex iff $\frac{d^2}{dt^2}\mathcal{L}(\gamma(t)) \geq 0$ for all geodesics $\gamma$.

Geodesic convexity is *not* preserved under diffeomorphism — it depends on the metric. A function that is non-convex in Euclidean space may become geodesically convex on a suitably curved Riemannian manifold, and vice versa. This is the deep insight behind natural gradient methods: the Fisher metric "straightens" the loss landscape by choosing the right curvature.

**Theorem 4.12 (Geodesic Convexity of KL Divergence).** The KL divergence $D_{KL}(p \| \cdot)$ is geodesically convex on $\Delta^{n-1}$ with respect to the m-connection geodesics (linear interpolation). The KL divergence $D_{KL}(\cdot \| p)$ is geodesically convex with respect to the e-connection geodesics (exponential interpolation).

This result has practical consequences: it means that certain optimization problems (e.g., variational inference, EM algorithm) have natural convexity guarantees when viewed in the right geometry.

## 6. Natural Gradient in Practice: Deep Networks

### 6.1 The Fisher-Vector Product

For modern large-scale models, even K-FAC may be too expensive. An alternative is to use the *Fisher-vector product* $\mathcal{I}(\theta)v$, which can be computed without forming $\mathcal{I}$ explicitly using Pearlmutter's trick (1994):

$$\mathcal{I}(\theta)v = \mathbb{E}_{x\sim p_\theta}\!\left[(\nabla_\theta\log p(x;\theta)^\top v)\,\nabla_\theta\log p(x;\theta)\right].$$

This can be computed with two forward-backward passes per sample. Combined with conjugate gradient (CG), this gives a $\mathcal{I}^{-1}\nabla\mathcal{L}$ computation in $O(kd)$ time (where $k$ is the number of CG iterations), avoiding the $O(d^2)$ storage of the full Fisher matrix.

### 6.2 Natural Gradient as Preconditioner: Insights from Hessian Analysis

**Theorem 4.13 (Natural Gradient Rescales the Loss Landscape).** Define $\tilde{\mathcal{L}}(\theta) = \mathcal{L}(\theta)$ but consider the reparameterized loss in the Fisher-normalized coordinates $u = \mathcal{I}(\theta)^{1/2}\theta$. In these coordinates, the gradient is the Euclidean gradient $\nabla_u\tilde{\mathcal{L}} = \mathcal{I}(\theta)^{1/2}\nabla_\theta\mathcal{L}$, and the Hessian is $\mathcal{I}(\theta)^{1/2}\nabla^2_\theta\mathcal{L}(\theta)\,\mathcal{I}(\theta)^{-1/2}$. The condition number becomes:
$$\kappa_u = \frac{\lambda_{\max}(\mathcal{I}^{1/2}\nabla^2\mathcal{L}\,\mathcal{I}^{-1/2})}{\lambda_{\min}(\mathcal{I}^{1/2}\nabla^2\mathcal{L}\,\mathcal{I}^{-1/2})} \leq \frac{\lambda_{\max}(\nabla^2\mathcal{L})\lambda_{\max}(\mathcal{I}^{-1})}{\lambda_{\min}(\nabla^2\mathcal{L})\lambda_{\min}(\mathcal{I}^{-1})}.$$

When $\mathcal{I} \approx \nabla^2\mathcal{L}$ (the "Fisher-Hessian" approximation), the condition number approaches 1, and natural gradient behaves like Newton's method with unit step size — rapid convergence near the optimum.

### 6.3 Relationship to Second-Order Methods

| Method | Update Direction | Preconditioner | Invariance |
|--------|-----------------|---------------|------------|
| SGD | $-\nabla_\theta\mathcal{L}$ | $I$ | None |
| AdaGrad/Adam | $-\text{diag}(\hat{G})^{-1/2}\nabla_\theta\mathcal{L}$ | Diagonal empirical $\hat{G}$ | Diagonal |
| K-FAC | $-(A \otimes G)^{-1}\nabla_\theta\mathcal{L}$ | Kronecker $\mathcal{I}$ | Layerwise affine |
| Natural Gradient | $-\mathcal{I}^{-1}\nabla_\theta\mathcal{L}$ | Full $\mathcal{I}$ | Full diffeomorphism |
| Newton | $-H^{-1}\nabla_\theta\mathcal{L}$ | Full $H$ | Full affine |

## 7. Summary and Forward Look

Natural gradient descent occupies a privileged position in the optimization landscape: it is the *unique* gradient descent method that is invariant under reparameterization, and it achieves the optimal convergence rate (among first-order methods) in the Riemannian geometry of the loss landscape. The challenge is and has always been computational — but approximations (K-FAC, diagonal Fisher, Fisher-vector products) make it practical even for billion-parameter models.

In Lecture 05, we will see how manifold learning algorithms can be understood as *implicitly* using the Fisher-Rao geometry: they recover or approximate the intrinsic Riemannian structure of data manifolds, even when they do not explicitly compute Fisher information.

---

## Exercises

1. **(Natural gradient on a 1D exponential family)** Consider $p(x;\theta) = \theta e^{-\theta x}$ for $x > 0$, $\theta > 0$. Compute the Fisher metric $g(\theta) = \mathcal{I}(\theta)$ and show that the natural gradient update $\theta \leftarrow \theta - \eta\,\mathcal{I}(\theta)^{-1}\frac{\partial\mathcal{L}}{\partial\theta}$ is equivalent to Newton's method for the MLE.

2. **(K-FAC for a 2-layer network)** Consider a 2-layer network $f(x) = W_2\,\sigma(W_1x)$ with loss $\mathcal{L} = \frac{1}{2}\|f(x) - y\|^2$. Write out the K-FAC approximation of the Fisher matrix for both layers explicitly. For each layer, identify $A$ and $G$ and compute the Kronecker inverse.

3. **(Parallel transport on the simplex)** Show that parallel transport of a tangent vector from $p \in \Delta^{n-1}$ to $q \in \Delta^{n-1}$ along the m-geodesic (linear interpolation) in the mixture connection $\nabla^{(-1)}$ is simply the identity map: $v \mapsto v$ in $\eta$-coordinates. Is this also true for the e-connection $\nabla^{(1)}$?

4. **(Geodesic convexity)** Prove that $D_{KL}(p \| \cdot)$ is convex along m-geodesics on $\Delta^{n-1}$. That is, for $q_t = (1-t)q_0 + tq_1$ and any fixed $p$: $D_{KL}(p\|q_t) \leq (1-t)D_{KL}(p\|q_0) + t\,D_{KL}(p\|q_1)$.

5. **(Fisher-vector product)** Implement Pearlmutter's trick for computing $\mathcal{I}(\theta)v$ in a simple neural network. Compare the runtime of CG-based natural gradient ($k$ iterations of Fisher-vector products) to direct inversion for $d = 100$ parameters.