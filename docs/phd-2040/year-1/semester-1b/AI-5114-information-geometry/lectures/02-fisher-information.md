# Lecture 02: Fisher Information

## Information Matrix, Cramér-Rao Bound, Natural Gradient

> *"The Fisher metric is the shadow that probability casts upon the parameter space — the shape of uncertainty itself."*

---

## 1. The Score Function

Let $\{p(x;\theta) : \theta \in \Theta \subseteq \mathbb{R}^n\}$ be a parametric statistical model on a sample space $\mathcal{X}$ with a common dominating measure $\mu$ (typically Lebesgue or counting measure). We assume the following regularity conditions hold:

- **(R1)** $\Theta$ is an open subset of $\mathbb{R}^n$.
- **(R2)** The support $\{x : p(x;\theta) > 0\}$ is independent of $\theta$.
- **(R3)** For all $\theta$ and all $i$, $\partial/\partial\theta^i \log p(x;\theta)$ exists $\mu$-almost everywhere.
- **(R4)** Interchange of differentiation and integration is valid at $\theta$.

**Definition 2.1 (Score Function).** The *score function* (or *score vector*) is the random vector:
$$s(\theta) = \nabla_\theta \log p(x;\theta) = \left(\frac{\partial}{\partial\theta^1}\log p(x;\theta), \ldots, \frac{\partial}{\partial\theta^n}\log p(x;\theta)\right)^\top.$$

**Proposition 2.2.** Under (R1)–(R4), $\mathbb{E}_\theta[s(\theta)] = 0$.

*Proof.* From $\int p(x;\theta)\,d\mu = 1$, differentiate under the integral sign:
$$\frac{\partial}{\partial\theta^i}\int p(x;\theta)\,d\mu = \int \frac{\partial}{\partial\theta^i}p(x;\theta)\,d\mu = \int \frac{\partial \log p}{\partial\theta^i}\, p(x;\theta)\,d\mu = \mathbb{E}_\theta\!\left[\frac{\partial \log p}{\partial\theta^i}\right] = 0.$$
The first equality uses (R4), and the left side is zero since $\int p\,d\mu = 1$ is constant. □

The score function measures the *sensitivity* of the log-likelihood to parameter perturbations. Intuitively: if the score is large in magnitude, a small change in $\theta$ produces a large change in the probability distribution.

## 2. The Fisher Information Matrix

**Definition 2.3 (Fisher Information Matrix).** The *Fisher information matrix* at $\theta$ is the $n \times n$ matrix:
$$\mathcal{I}(\theta)_{ij} = \mathbb{E}_\theta\!\left[\frac{\partial \log p}{\partial\theta^i}\cdot\frac{\partial \log p}{\partial\theta^j}\right] = \int \frac{\partial \log p(x;\theta)}{\partial\theta^i}\cdot\frac{\partial \log p(x;\theta)}{\partial\theta^j}\cdot p(x;\theta)\,d\mu(x).$$

Under (R1)–(R4), an equivalent formulation (obtained by differentiating $\mathbb{E}_\theta[s_i] = 0$ once more) is:
$$\mathcal{I}(\theta)_{ij} = -\mathbb{E}_\theta\!\left[\frac{\partial^2 \log p(x;\theta)}{\partial\theta^i\,\partial\theta^j}\right].$$

**Proposition 2.4 (Properties of $\mathcal{I}$).**
1. $\mathcal{I}(\theta)$ is symmetric and positive semi-definite.
2. $\mathcal{I}(\theta)$ is positive definite if and only if the score components are linearly independent (i.e., the model is *identifiable* at $\theta$).
3. Under a reparameterization $\theta \mapsto \xi = \psi(\theta)$ with $\psi$ a diffeomorphism: $\mathcal{I}_\xi(\xi) = J\,\mathcal{I}_\theta(\theta)\,J^\top$, where $J = \frac{\partial\theta}{\partial\xi}$ is the Jacobian.

Property 3 is exactly the transformation rule for a $(0,2)$-tensor! This is the first hint that $\mathcal{I}$ is not just a matrix but a *Riemannian metric*.

### 2.1 Examples

**Example: Univariate Normal $\mathcal{N}(\mu, \sigma^2)$.** The log-likelihood for a single observation is $\log p = -\frac{1}{2}\log(2\pi\sigma^2) - \frac{(x-\mu)^2}{2\sigma^2}$. Computing:
$$\mathcal{I}(\mu, \sigma^2) = \begin{pmatrix} 1/\sigma^2 & 0 \\ 0 & 1/(2\sigma^4) \end{pmatrix}.$$

Note: the metric components depend on $\theta$ — this is a *curved* Riemannian manifold. The off-diagonal zeros indicate that $\mu$ and $\sigma^2$ are *orthogonal parameters* under the Fisher metric.

**Example: Categorical/Multinomial on $\Delta^{n-1}$.** With parameters $\pi = (\pi_1, \ldots, \pi_n)$ on the simplex $\Delta^{n-1}$ (using the constraint $\sum \pi_i = 1$ to reduce to $n-1$ free parameters), the Fisher metric is:
$$\mathcal{I}(\pi)_{ij} = \frac{\delta_{ij}}{\pi_i} + \frac{1}{\pi_n}, \quad 1 \leq i,j \leq n-1.$$

This is the *Fisher-Rao metric* on the statistical simplex, and its geometry is that of the positive orthant of the $(n-1)$-sphere, as we shall see.

**Example: Exponential Families.** For a regular exponential family $p(x;\theta) = \exp(\theta^i T_i(x) - \psi(\theta))$, the Fisher information satisfies $\mathcal{I}(\theta) = \nabla^2\psi(\theta) = [\partial^2\psi/\partial\theta^i\partial\theta^j]$, the Hessian of the cumulant generating function. Since $\psi$ is strictly convex on the natural parameter space, this Hessian is positive definite — confirming that $\mathcal{I}$ defines a genuine Riemannian metric.

## 3. The Cramér-Rao Bound

**Theorem 2.5 (Cramér-Rao Inequality).** Let $\hat{\theta}: \mathcal{X} \to \mathbb{R}^n$ be an unbiased estimator of $\theta$ (i.e., $\mathbb{E}_\theta[\hat{\theta}] = \theta$ for all $\theta \in \Theta$). Then:
$$\text{Cov}_\theta(\hat{\theta}) \succeq \mathcal{I}(\theta)^{-1},$$
i.e., $\text{Cov}_\theta(\hat{\theta}) - \mathcal{I}(\theta)^{-1}$ is positive semi-definite.

*Proof.* Define $h(x) = \hat{\theta}(x) - \theta$. Then $\mathbb{E}_\theta[h] = 0$ (unbiasedness) and $\mathbb{E}_\theta[hs^\top] = I$ (since $\mathbb{E}_\theta[\hat{\theta}\cdot s^\top] = I + \mathbb{E}_\theta[\theta s^\top] = I$, using $\mathbb{E}_\theta[s] = 0$). For any vector $a \in \mathbb{R}^n$:
$$0 \leq \mathbb{E}_\theta\!\left[(a^\top h)^2\right] = a^\top\,\text{Cov}_\theta(\hat{\theta})\,a + 2\,a^\top\,\text{Cov}_\theta(\hat{\theta}, s)\,a + a^\top\,\text{Cov}_\theta(s)\,a.$$
But $\text{Cov}_\theta(\hat{\theta}, s) = \mathbb{E}_\theta[hs^\top] = I$ and $\text{Cov}_\theta(s) = \mathcal{I}(\theta)$. A standard completion-of-squares argument yields the result. □

### 3.1 Cramér-Rao as a Geometric Statement

The Cramér-Rao bound is not merely an inequality about estimation — it is a *geometric* statement about the size of the tangent space. Consider the statistical manifold $(\mathcal{S}, g)$ where $g = \mathcal{I}(\theta)$ is the Fisher-Rao metric. The *differential* of an unbiased estimator $\hat{\theta}$ at $\theta$ can be viewed as an attempt to invert the identity map $T_\theta\Theta \to T_\theta\mathcal{S}$. The Cramér-Rao bound says:

$$\text{The "volume" of the uncertainty ellipsoid } \{\delta\theta : \delta\theta^\top\,\mathcal{I}(\theta)\,\delta\theta = 1\} \text{ cannot be shrunk below } \text{vol}(\mathcal{I}(\theta)^{-1/2}).$$

In other words, the Fisher metric defines a *minimum distinguishability* between nearby probability distributions, and no estimator can resolve parameter values more finely than the metric permits. This is the information-geometric content of Cramér-Rao.

### 3.2 The Van Trees (Bayesian) Cramér-Rao Bound

For a prior $\pi(\theta)$, the *Bayesian Cramér-Rao bound* (Van Trees, 1968) states:
$$\mathbb{E}\!\left[(\hat{\theta} - \theta)(\hat{\theta} - \theta)^\top\right] \succeq \left(\mathbb{E}[\mathcal{I}(\theta)] + \mathbb{E}[\nabla_\theta \log \pi][\nabla_\theta \log \pi]^\top\right)^{-1},$$
where expectations are over both $x$ and $\theta$. The additional term $\mathbb{E}[\nabla_\theta \log \pi][\nabla_\theta \log \pi]^\top$ encodes prior information as an additional Riemannian contribution — the prior warps the geometry.

## 4. The Fisher-Rao Metric: Chentsov's Uniqueness Theorem

The Fisher information matrix is not *one possible* Riemannian metric on a statistical manifold — it is, in a deep sense, the *only natural* one.

**Theorem 2.6 (Chentsov, 1982).** On the simplex $\Delta^{n-1}$, the Fisher-Rao metric is (up to a positive scalar constant) the *unique* Riemannian metric that is invariant under Markov morphisms (stochastic maps that are bijections on distributions).

In other words: if you demand that your metric respect the statistical structure of $\Delta^{n-1}$ — specifically, that it is preserved under the natural action of the monoid of stochastic matrices — then the Fisher-Rao metric is your only option. Any other metric would break this symmetry.

**Theorem 2.7 (Chentsov, extended by Campbell, 1986).** On a general statistical manifold, the Fisher-Rao metric is the unique Riemannian metric (up to conformal scaling) that is invariant under sufficient statistics.

This is the differential-geometric equivalent of the Shannon uniqueness theorem in information theory: just as entropy is the unique measure of uncertainty satisfying natural axioms, the Fisher-Rao metric is the unique measure of information distance satisfying natural invariance axioms.

*The Fisher-Rao metric is to statistics what entropy is to information theory — the canonical, irreplaceable object dictated by the structure of the problem itself.*

### 4.1 Conformal Factor and the Wilks Theorem

Chentsov's theorem allows a conformal scaling: $g \mapsto c \cdot g$ for any $c > 0$. The choice $c = 1$ makes the Fisher-Rao metric the *standard* choice. The Wilks theorem provides another connection:

**Theorem 2.8 (Wilks, 1938).** Under regularity conditions, $-2\log\Lambda_n \xrightarrow{d} \chi^2_n$ where $\Lambda_n$ is the likelihood ratio and $n$ is the number of parameters. The $\chi^2_n$ distribution has density $(2\pi)^{-n/2}|g|^{-1/2}\exp(-\frac{1}{2}g_{ij}\delta\theta^i\delta\theta^j)\sqrt{\det g}\,d^n\delta\theta$ with respect to the Lebesgue measure in normal coordinates — exactly the volume form of the Fisher-Rao metric.

## 5. Natural Gradient Descent

### 5.1 The Problem with Euclidean Gradients

Consider minimizing a loss function $\mathcal{L}(\theta)$ on a statistical manifold. The standard (Euclidean) gradient update is:
$$\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t).$$

This update treats the parameter space $\Theta$ as Euclidean $\mathbb{R}^n$ with the standard inner product. But the *true* geometry of $\Theta$ is given by the Fisher-Rao metric $\mathcal{I}(\theta)$. The Euclidean gradient $\nabla_\theta \mathcal{L}$ does not account for the fact that perturbations in different directions $\delta\theta$ may correspond to vastly different changes in the probability distribution $p(x;\theta)$.

### 5.2 Definition of the Natural Gradient

**Definition 2.9 (Natural Gradient).** The *natural gradient* of $\mathcal{L}$ at $\theta$ is the Riemannian gradient of $\mathcal{L}$ with respect to the Fisher-Rao metric:
$$\tilde{\nabla}_\theta \mathcal{L} := \mathcal{I}(\theta)^{-1}\,\nabla_\theta \mathcal{L}(\theta).$$

In coordinate-free language, the natural gradient $\text{grad}\,\mathcal{L} \in T_\theta\Theta$ is the unique vector satisfying:
$$g_\theta(v, \text{grad}\,\mathcal{L}) = d\mathcal{L}_\theta(v) \quad \forall\, v \in T_\theta\Theta,$$
where $g_\theta = \mathcal{I}(\theta)$ is the Fisher metric and $d\mathcal{L}_\theta$ is the differential of $\mathcal{L}$. In coordinates, $\text{grad}\,\mathcal{L} = \mathcal{I}(\theta)^{-1}\,\nabla_\theta \mathcal{L}$.

**The natural gradient descent update** is:
$$\theta_{t+1} = \theta_t - \eta\,\mathcal{I}(\theta_t)^{-1}\,\nabla_\theta \mathcal{L}(\theta_t).$$

### 5.3 Why Natural Gradient Is Better: A Second-Order Perspective

**Theorem 2.10 (Amari, 1998).** The natural gradient direction is the steepest descent direction with respect to the KL-divergence $\text{KL}(p_\theta\|p_{\theta+\delta\theta})$ in the Riemannian metric.

The Euclidean gradient finds the steepest direction in $\ell^2$-norm, while the natural gradient finds the steepest direction in the *information norm* $\|\delta\theta\|_\mathcal{I}^2 = \delta\theta^\top \mathcal{I}(\theta)\,\delta\theta$. This norm measures the *actual* change in the probability distribution, not the arbitrary coordinate change.

Concretely, consider a second-order Taylor expansion of the loss:
$$\mathcal{L}(\theta + \delta\theta) \approx \mathcal{L}(\theta) + \nabla_\theta \mathcal{L}^\top \delta\theta + \frac{1}{2}\delta\theta^\top H_\mathcal{L}(\theta)\,\delta\theta,$$
where $H_\mathcal{L} = \nabla^2_\theta \mathcal{L}$ is the Hessian. The Newton update $\delta\theta = -H_\mathcal{L}^{-1}\nabla_\theta\mathcal{L}$ requires computing and inverting $H_\mathcal{L}$. The natural gradient replaces $H_\mathcal{L}$ with $\mathcal{I}(\theta)$ — an *expected* Hessian:
$$\mathcal{I}(\theta)_{ij} = \mathbb{E}_\theta\!\left[-\frac{\partial^2 \log p}{\partial\theta^i\,\partial\theta^j}\right] = \mathbb{E}_\theta[\text{Hessian of } -\!\log p].$$

For the negative log-likelihood loss $\mathcal{L}(\theta) = -\mathbb{E}_{x\sim p_\text{data}}[\log p(x;\theta)]$, the Hessian has a *Fisher approximation* that avoids double back-propagation.

### 5.4 Natural Gradient for Neural Networks

For a neural network with parameters $\theta \in \mathbb{R}^d$, computing $\mathcal{I}(\theta)^{-1}\nabla_\theta\mathcal{L}$ directly requires inverting a $d \times d$ matrix (where $d$ may be $10^6$ to $10^9$), which is infeasible. Practical approaches include:

- **K-FAC (Kronecker-Factored Approximate Curvature):** Approximate $\mathcal{I}(\theta)$ as a block-diagonal Kronecker product $\mathcal{I}(\theta) \approx \bigotimes_l (A_{l-1} \otimes G_l)$, reducing the inverse to inverting small matrices per layer.
- **Diagonal Fisher:** Use $\text{diag}(\mathcal{I}(\theta))$ for a computationally cheap but crude approximation — equivalent to adaptive learning rate methods like AdaGrad/Adam.
- **Damping:** Add $\epsilon I$ to $\mathcal{I}(\theta)$ before inversion (Trust Region / TRPO), connecting to trust-region methods.

## 6. Information Length and Rao's Distance

**Definition 2.11 (Fisher-Rao Distance / Rao's Distance).** The *Fisher-Rao distance* (also called *Rao's distance*) between two probability distributions $p_{\theta_1}, p_{\theta_2}$ is the geodesic distance on the Riemannian manifold $(\Theta, \mathcal{I}(\theta))$:
$$d_{FR}(p_{\theta_1}, p_{\theta_2}) = \inf_\gamma \int_0^1 \sqrt{\dot{\gamma}(t)^\top \mathcal{I}(\gamma(t))\,\dot{\gamma}(t)}\,dt,$$
where the infimum is over all smooth paths $\gamma: [0,1] \to \Theta$ connecting $\gamma(0) = \theta_1$ to $\gamma(1) = \theta_2$.

### 6.1 Hellinger Distance and Fisher-Rao

The Hellinger distance $d_H(p, q) = \left(\frac{1}{2}\int(\sqrt{p} - \sqrt{q})^2\,d\mu\right)^{1/2}$ is related to the Fisher-Rao distance for infinitesimally close distributions:
$$d_{FR}(p_\theta, p_{\theta+\delta\theta}) = \sqrt{\delta\theta^\top \mathcal{I}(\theta)\,\delta\theta} + O(\|\delta\theta\|^2) = 2\,d_H(p_\theta, p_{\theta+\delta\theta}) + O(\|\delta\theta\|^2).$$

Thus the Fisher-Rao metric *is* twice the Hellinger metric in the infinitesimal limit. The square root representation $\sqrt{p(x;\theta)}$ embeds the statistical manifold into $L^2(\mathcal{X}, \mu)$, where the Fisher-Rao geodesic distance corresponds to arc length on the unit sphere. This is the *Bhattacharyya embedding*.

### 6.2 Rao's Distance for the Multinomial

For the multinomial family $\Delta^{n-1}$, Rao (1945) showed that under the Fisher-Rao metric, the manifold is isometric to the positive orthant of the $(n-1)$-sphere $S_+^{n-1}$ with radius $\frac{1}{2}$. The isometry is given by:
$$\phi: \Delta^{n-1} \to S_+^{n-1}, \quad \phi(p)_i = \sqrt{p_i}.$$

Under this embedding, the Fisher-Rao distance between two multinomial distributions $p, q \in \Delta^{n-1}$ is:
$$d_{FR}(p, q) = 2\arccos\left(\sum_{i=1}^n \sqrt{p_i q_i}\right) = 2\arccos\left(\int \sqrt{p(x)q(x)}\,d\mu(x)\right).$$

The quantity $\sum_i \sqrt{p_i q_i}$ is the *Bhattacharyya coefficient*, and this formula reveals the deep geometric fact: the Fisher-Rao geometry of the simplex is spherical geometry.

## 7. Jeffreys Priors and the Fisher Volume

**Theorem 2.12 (Jeffreys Prior).** The *Jeffreys prior* $\pi_J(\theta) \propto \sqrt{\det\mathcal{I}(\theta)}$ is the unique (up to proportionality) prior on $\Theta$ that is invariant under reparameterization.

*Proof.* Under $\theta \mapsto \xi = \psi(\theta)$, the Fisher metric transforms as $\mathcal{I}_\xi = J\,\mathcal{I}_\theta\,J^\top$, so:
$$\sqrt{\det\mathcal{I}_\xi} = \sqrt{\det(J\,\mathcal{I}_\theta\,J^\top)} = |\det J|\,\sqrt{\det\mathcal{I}_\theta}.$$
This is exactly the transformation rule for a density under change of variables. Hence $\sqrt{\det\mathcal{I}(\theta)}\,d\theta$ is an invariant volume form. □

The Jeffreys prior is the *uniform distribution on the statistical manifold when measured by the Fisher-Rao volume form*. It is the geometrically natural non-informative prior, as it places equal prior mass on equal-volumes of information-geometric space.

## 8. Connection to Upcoming Lectures

| This Lecture | Key Object | Downstream Role |
|-------------|-----------|-----------------|
| Fisher metric $\mathcal{I}(\theta)$ | Riemannian metric on $\Theta$ | Foundation for α-geometry (L03) |
| Cramér-Rao bound | Minimum variance | Optimality of natural gradient (L04) |
| Natural gradient | $\mathcal{I}^{-1}\nabla\mathcal{L}$ | Riemannian optimization (L04) |
| Rao's distance | Geodesic distance | Manifold learning algorithms (L05) |
| Jeffreys prior | $\sqrt{\det\mathcal{I}}$ | Bayesian geometry |

---

## Exercises

1. **(Fisher for exponential families)** Compute the Fisher information matrix for the 2-parameter gamma distribution $p(x; \alpha, \beta) = \frac{\beta^\alpha}{\Gamma(\alpha)}x^{\alpha-1}e^{-\beta x}$. Show that the off-diagonal term is nonzero — $\alpha$ and $\beta$ are not Fisher-orthogonal. Find a reparameterization in which the Fisher metric is diagonal.

2. **(Rao distance on the binomial manifold)** For the binomial family $\mathcal{B}(n, p)$ with $p \in (0,1)$, the Fisher metric is $g = \frac{n}{p(1-p)}dp^2$. Show that the geodesic distance between $p_1$ and $p_2$ is $2\sqrt{n}\left|\arcsin\sqrt{p_1} - \arcsin\sqrt{p_2}\right|$.

3. **(K-FAC approximation)** Let $\theta = (W_1, W_2)$ be the weights of a 2-layer network. The Fisher matrix is $\mathcal{I}(\theta) = \mathbb{E}[\nabla_\theta \log p \cdot \nabla_\theta \log p^\top]$. Show that the K-FAC approximation $\mathcal{I} \approx A_0 \otimes G_1 \oplus A_1 \otimes G_2$ (Kronecker-factored per layer) reduces the inversion cost from $O(d^3)$ to $O(d^{1.5})$ for each layer.

4. **(Cramér-Rao for biased estimators)** Generalize the Cramér-Rao inequality to biased estimators. If $\text{bias}(\hat{\theta}) = b(\theta)$, show that $\text{Cov}(\hat{\theta}) \succeq (I + \nabla_\theta b)^\top \mathcal{I}^{-1} (I + \nabla_\theta b)$. Interpret the geometric meaning of the bias gradient $\nabla_\theta b$.

5. **(Chentsov's theorem, sketch)** Let $T: \Delta^{n-1} \to \Delta^{m-1}$ be a Markov morphism (i.e., $T$ is a stochastic matrix). Show that the only inner product on $T_p\Delta^{n-1}$ that satisfies $g_{T(p)}(T_*v, T_*w) = g_p(v,w)$ for all Markov morphisms $T$ is (up to scaling) the Fisher-Rao inner product.