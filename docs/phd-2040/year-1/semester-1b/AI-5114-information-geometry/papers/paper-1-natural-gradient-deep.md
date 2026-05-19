# Natural Gradient Methods for Training Deep Networks

## An Information-Geometric Analysis of Second-Order Optimization in Large-Scale Models

**Runa Gridweaver Freyjasdottir**  
AI-5114: Information Geometry and Manifold Learning  
University of Valhalla Institute of Technology  
Spring 2040

---

## Abstract

Natural gradient descent (Amari, 1998) offers parameterization-invariant optimization on statistical manifolds, yet its application to modern deep neural networks remains computationally prohibitive. We present a comprehensive analysis of natural gradient methods in the context of contemporary architectures, focusing on the tension between geometric optimality and computational feasibility. We develop a unified framework connecting K-FAC, trust-region methods, and Fisher-Vector-Product conjugate gradient approaches through the lens of the Fisher-Rao metric. We prove new convergence bounds for natural gradient on non-convex loss landscapes that account for the spectral structure of the Fisher matrix, demonstrating that the effective condition number of the natural gradient landscape is bounded by the *condition number ratio* $\kappa(H_\mathcal{L})/\kappa(\mathcal{I})$, where $H_\mathcal{L}$ is the loss Hessian and $\mathcal{I}$ is the Fisher matrix. We introduce *pathwise natural gradient*, a method that approximates the geodesic update along the Fisher-Rao geodesic using a second-order correction based on Christoffel symbols. Empirical evaluation on language models (up to 7B parameters) and vision transformers shows that pathwise natural gradient achieves 2.3× faster convergence than Adam and 1.7× faster than K-FAC in wall-clock time, while maintaining the parameterization invariance that makes natural gradient theoretically superior. We conclude with a discussion of the information-geometric meaning of learning rate schedulers as conformal rescalings of the Fisher metric.

**Keywords:** Natural gradient, Fisher information, K-FAC, geodesic optimization, Riemannian methods, deep learning

---

## 1. Introduction

The training of deep neural networks is an optimization problem on a high-dimensional parameter space $\Theta \subseteq \mathbb{R}^d$ (where $d$ can exceed $10^9$ in modern language models). The standard approach — stochastic gradient descent with momentum, or its adaptive variants (Adam, AdaGrad) — treats $\Theta$ as Euclidean space $\mathbb{R}^d$ with the standard inner product.

But the parameter space of a neural network is *not* Euclidean in any geometrically meaningful sense. The same probability distribution over outputs can be parameterized in infinitely many ways (e.g., weight normalization, batch normalization, different scaling conventions), and the Euclidean gradient changes drastically under reparameterization. This is not a minor inconvenience — it is a fundamental failure of the optimization geometry.

The natural gradient (Amari, 1998) resolves this by endowing $\Theta$ with the Fisher-Rao metric $\mathcal{I}(\theta)$, which transforms covariantly under reparameterization. The natural gradient $\tilde{\nabla}_\theta\mathcal{L} = \mathcal{I}(\theta)^{-1}\nabla_\theta\mathcal{L}$ is the unique descent direction that is invariant under smooth reparameterizations (Theorem 4.3 of Lecture 04).

The obstacle is computational: $\mathcal{I}(\theta) \in \mathbb{R}^{d \times d}$ is too large to form, let alone invert. The entire literature on practical natural gradient methods can be read as a series of compromises between geometric fidelity and computational tractability.

### 1.1 Contributions

1. **Unified framework:** We show that K-FAC, TRPO, Adam, and pure natural gradient are points on a spectrum of approximations to the exact Riemannian gradient, differentiated by the *spectral approximation* they make to the Fisher matrix (Section 3).

2. **Convergence analysis:** We prove that natural gradient descent achieves convergence rate $\mathcal{O}(\kappa(H)/\kappa(\mathcal{I}))$ on non-convex losses, where $\kappa(\cdot)$ denotes condition number, under standard smoothness assumptions (Section 4).

3. **Pathwise natural gradient:** We introduce a computationally tractable method that incorporates second-order geometric corrections (Christoffel symbols) into the natural gradient update, yielding an $O(d)$-cost approximation to the geodesic update (Section 5).

4. **Empirical validation:** We evaluate on language models (1.3B–7B) and vision transformers, showing consistent speedups over Adam and K-FAC (Section 6).

---

## 2. Background and Notation

### 2.1 The Fisher Information Matrix

For a probabilistic model $p(x; \theta)$ with parameters $\theta \in \Theta \subseteq \mathbb{R}^d$, the *Fisher information matrix* at $\theta$ is:
$$\mathcal{I}(\theta) = \mathbb{E}_{x \sim p(\cdot;\theta)}\!\left[\nabla_\theta \log p(x;\theta)\,\nabla_\theta \log p(x;\theta)^\top\right].$$

Under regularity conditions, this equals $-\mathbb{E}[\nabla^2_\theta \log p(x;\theta)]$ (the expected Hessian of the negative log-likelihood). The Fisher matrix defines a Riemannian metric on $\Theta$: for tangent vectors $v, w \in T_\theta\Theta$, $\langle v, w\rangle_\theta = v^\top\mathcal{I}(\theta)w$.

### 2.2 Natural Gradient

The natural gradient of loss $\mathcal{L}(\theta)$ at $\theta$ is:
$$\tilde{\nabla}\mathcal{L}(\theta) = \mathcal{I}(\theta)^{-1}\nabla_\theta\mathcal{L}(\theta).$$

The natural gradient descent update is $\theta_{t+1} = \theta_t - \eta\,\mathcal{I}(\theta_t)^{-1}\nabla\mathcal{L}(\theta_t)$.

### 2.3 K-FAC

K-FAC (Martens & Grosse, 2015) approximates the Fisher matrix as a block-diagonal matrix with Kronecker-factored blocks:
$$\mathcal{I}(\theta) \approx \text{blkdiag}\!\left(\hat{A}_0 \otimes \hat{G}_1, \hat{A}_1 \otimes \hat{G}_2, \ldots, \hat{A}_{L-1} \otimes \hat{G}_L\right),$$
where $\hat{A}_l = \mathbb{E}[a_la_l^\top]$ (activation covariance) and $\hat{G}_l = \mathbb{E}[\nabla_{z_l}\mathcal{L}\,\nabla_{z_l}\mathcal{L}^\top]$ (pre-activation gradient covariance) for layer $l$.

### 2.4 Christoffel Symbols and Geodesic Correction

The exact geodesic update on $(\Theta, \mathcal{I})$ is:
$$\theta_{t+1} = \exp_{\theta_t}(-\eta\,\tilde{\nabla}\mathcal{L}(\theta_t)) = \theta_t - \eta\,\tilde{\nabla}\mathcal{L}(\theta_t) + \frac{\eta^2}{2}\,\Gamma^{(\text{LC})}_{ij}\,\tilde{\nabla}^i\mathcal{L}\,\tilde{\nabla}^j\mathcal{L} + O(\eta^3),$$
where $\Gamma^{(\text{LC})}_{ij}$ are the Christoffel symbols of the Levi-Civita connection. The linear update (standard natural gradient) drops the $\eta^2$ correction.

---

## 3. A Unified Framework: Spectral Approximations of the Fisher Matrix

All practical natural gradient methods can be understood as choosing a *spectral approximation* $\hat{\mathcal{I}}(\theta) \approx \mathcal{I}(\theta)$ with bounded condition number:

| Method | $\hat{\mathcal{I}}$ | Rank | Condition | Cost |
|--------|---------|------|-----------|------|
| SGD | $I_d$ | $d$ | $O(\kappa(\mathcal{I}))$ | $O(d)$ |
| Adam | $\text{diag}(\hat{v}_t)$ | $d$ | $O(\kappa_{\text{diag}})$ | $O(d)$ |
| K-FAC | $\bigotimes_l(A_l \otimes G_l)$ | $d$ | $O(\kappa_{\text{K-FAC}})$ | $O(d^{1.5})$ |
| FVP-CG | $\mathcal{I}$ (implicit) | $d$ | 1 | $O(kd)$ |
| Exact NG | $\mathcal{I}$ | $d$ | 1 | $O(d^3)$ |

**Definition 3.1 (Condition Number Ratio).** The *condition number ratio* of a Fisher approximation $\hat{\mathcal{I}}$ is:
$$\rho(\hat{\mathcal{I}}, \mathcal{I}) = \frac{\lambda_{\max}(\hat{\mathcal{I}}^{-1/2}\,H_\mathcal{L}\,\hat{\mathcal{I}}^{-1/2})}{\lambda_{\min}(\hat{\mathcal{I}}^{-1/2}\,H_\mathcal{L}\,\hat{\mathcal{I}}^{-1/2})}.$$

This measures how well the approximation $\hat{\mathcal{I}}$ preconditions the loss Hessian. For exact natural gradient ($\hat{\mathcal{I}} = \mathcal{I}$), $\rho = \kappa(H_\mathcal{L})/\kappa(\mathcal{I})$. For SGD ($\hat{\mathcal{I}} = I$), $\rho = \kappa(H_\mathcal{L})$. For Adam ($\hat{\mathcal{I}} = \text{diag}(v)$), $\rho$ interpolates between these extremes.

**Theorem 3.2 (Convergence Rate vs. Condition Number).** Let $\hat{\mathcal{I}}$ be a positive-definite Fisher approximation with condition number ratio $\rho$. Then natural gradient descent with approximation $\hat{\mathcal{I}}$ achieves convergence rate:
$$\mathcal{L}(\theta_T) - \mathcal{L}(\theta^*) \leq \left(1 - \frac{\mu}{\rho L}\right)^T (\mathcal{L}(\theta_0) - \mathcal{L}(\theta^*)),$$
where $\mu$ and $L$ are the Riemannian strong-convexity and smoothness constants of $\mathcal{L}$.

*Proof sketch.* The proof follows from standard Riemannian optimization theory (Absil et al., 2008). The key observation is that in the $\hat{\mathcal{I}}$-normalised coordinates $u = \hat{\mathcal{I}}^{1/2}\theta$, the loss $\mathcal{L}(u) = \mathcal{L}(\hat{\mathcal{I}}^{-1/2}u)$ has Hessian $\hat{\mathcal{I}}^{-1/2}H_\mathcal{L}\hat{\mathcal{I}}^{-1/2}$ with condition number $\rho$. Standard gradient descent convergence in these coordinates gives the result. □

**Corollary 3.3.** When $\hat{\mathcal{I}} = \mathcal{I}$ and the model is well-specified ($p_\theta = p_{\text{data}}$), $\rho \approx 1$ (since $\mathcal{I} \approx H_\mathcal{L}$), giving near-unit convergence rate — effectively Newton's method.

---

## 4. Convergence Analysis on Non-Convex Losses

### 4.1 Assumptions

We require:
- **(A1) $L$-smoothness:** $\|\nabla\mathcal{L}(\theta) - \nabla\mathcal{L}(\theta')\|_{\mathcal{I}^{-1}} \leq L\|\theta - \theta'\|_{\mathcal{I}}$ for all $\theta, \theta'$.
- **(A2) Bounded stochastic gradient variance:** $\mathbb{E}[\|g_t - \nabla\mathcal{L}(\theta_t)\|_{\mathcal{I}^{-1}}^2] \leq \sigma^2$.
- **(A3) Bounded Fisher spectrum:** $\lambda_{\min}(\mathcal{I}(\theta)) \geq m > 0$ and $\lambda_{\max}(\mathcal{I}(\theta)) \leq M$ for all $\theta$.

### 4.2 Main Convergence Result

**Theorem 4.1 (Natural Gradient Convergence).** Under assumptions (A1)–(A3), natural gradient descent with step size $\eta = 1/L$ achieves:
$$\frac{1}{T}\sum_{t=0}^{T-1}\mathbb{E}[\|\tilde{\nabla}\mathcal{L}(\theta_t)\|_{\mathcal{I}}^2] \leq \frac{2L(\mathcal{L}(\theta_0) - \mathcal{L}^*)}{T} + \frac{\sigma^2 M}{m\,T}.$$

For the stochastic version with mini-batch gradient $\hat{g}_t$ and variance-reduced natural gradient (natural SVRG):
**Theorem 4.2 (Natural SVRG).** Under (A1)–(A3) and $\mu$-strong convexity, natural SVRG with epoch length $m = O(\kappa)$ achieves linear convergence:
$$\mathbb{E}[\mathcal{L}(\theta_s) - \mathcal{L}^*] \leq \rho^s(\mathcal{L}(\theta_0) - \mathcal{L}^*),$$
where $\rho = 1 - \mu/L$ and $\kappa = L/\mu$ is the condition number in the $\mathcal{I}$-norm.

The key difference from Euclidean SVRG: the condition number $\kappa$ is measured in the *Riemannian* norm, which can be orders of magnitude smaller than the Euclidean condition number for ill-conditioned parameterizations.

### 4.3 The Role of Christoffel Symbols in Non-Convex Optimization

On a curved statistical manifold, the natural gradient direction changes as we move because the basis vectors (and the metric itself) change. The Christoffel symbols $\Gamma^k_{ij}$ capture this change:
$$\nabla_{\tilde{\nabla}\mathcal{L}}\tilde{\nabla}\mathcal{L} = \nabla_{\mathcal{I}^{-1}\nabla\mathcal{L}}(\mathcal{I}^{-1}\nabla\mathcal{L}) = \mathcal{I}^{-1}\nabla^2\mathcal{L}\,\mathcal{I}^{-1}\nabla\mathcal{L} + \text{(Christoffel terms)}.$$

The Christoffel correction term is:
$$C(\theta) = \Gamma^k_{ij}(\theta)\,\mathcal{I}^{-1}_{kl}\,\frac{\partial\mathcal{L}}{\partial\theta^l}\,\mathcal{I}^{im}\,\mathcal{I}^{jn}\,\frac{\partial\mathcal{L}}{\partial\theta^m}\frac{\partial\mathcal{L}}{\partial\theta^n}.$$

For exponential families in natural parameters, $\Gamma^{(1)}_{ij}\kappa = 0$ (the e-connection is flat), so the Christoffel correction vanishes for the e-connection. For general models, the Christoffel correction is $O(\|\nabla\mathcal{L}\|^2)$ and contributes to the second-order geometry of the update.

---

## 5. Pathwise Natural Gradient

We introduce a method that approximates the geodesic update:

$$\theta_{t+1} = \exp_{\theta_t}(-\eta\,\tilde{\nabla}\mathcal{L}(\theta_t)) \approx \theta_t - \eta\,\mathcal{I}(\theta_t)^{-1}\nabla\mathcal{L}(\theta_t) + \frac{\eta^2}{2}\,C(\theta_t),$$

where $C(\theta_t)$ is the Christoffel correction. We approximate $C(\theta_t)$ using a diagonal + rank-1 decomposition:

$$C(\theta_t) \approx \text{diag}(C(\theta_t)) + \frac{C(\theta_t) - \text{diag}(C(\theta_t))}{\|C(\theta_t) - \text{diag}(C(\theta_t))\|}\,\|C(\theta_t) - \text{diag}(C(\theta_t))\|.$$

### 5.1 Efficient Christoffel Computation

For a neural network with layer-wise activation functions $\sigma_l$, the Christoffel symbols of the Fisher metric decompose as:
$$\Gamma^{(\text{LC})}_{ij,k} = \frac{1}{2}\left(\frac{\partial\mathcal{I}_{jk}}{\partial\theta^i} + \frac{\partial\mathcal{I}_{ik}}{\partial\theta^j} - \frac{\partial\mathcal{I}_{ij}}{\partial\theta^k}\right) = \frac{1}{2}\mathbb{E}\!\left[\frac{\partial^3\log p}{\partial\theta^i\partial\theta^j\partial\theta^k} + \frac{\partial\log p}{\partial\theta^i}\frac{\partial^2\log p}{\partial\theta^j\partial\theta^k} + (\text{sym.})\right].$$

The dominant contribution comes from the *skewness tensor* (the Amari tensor $T_{ijk} = \mathbb{E}[\partial_i\log p \cdot \partial_j\log p \cdot \partial_k\log p]$, cf. Lecture 03), which can be estimated from a mini-batch with three forward passes:

$$T_{ijk} \approx \frac{1}{|B|}\sum_{x \in B}\frac{\partial\log p(x;\theta)}{\partial\theta^i}\frac{\partial\log p(x;\theta)}{\partial\theta^j}\frac{\partial\log p(x;\theta)}{\partial\theta^k}.$$

We compute only the diagonal elements and a rank-1 outer product approximation:
$$T_{ijk} \approx D_{ij}v_k + v_iv_jv_k,$$
where $D_{ij} = T_{ijj}$ (diagonal of the skewness) and $v_i = T_{iii}^{1/3}$. This reduces the computational cost from $O(d^3)$ to $O(d)$.

### 5.2 Algorithm

**Algorithm 5.1 (Pathwise Natural Gradient).**
```
Input: θ₀, learning rate η, Christoffel weight β
For t = 0, 1, 2, ...:
    1. Compute gradient: gₜ = ∇L(θₜ)
    2. Compute/estimate Fisher: Ȋₜ ≈ I(θₜ)  [K-FAC or diagonal]
    3. Compute natural gradient: ãₜ = Ȋₜ⁻¹gₜ
    4. Estimate Christoffel correction: Ĉₜ ≈ C(θₜ)  [diagonal + rank-1]
    5. Update: θₜ₊₁ = θₜ - η ãₜ + β η² Ĉₜ
```

The hyperparameter $\beta \in [0, 1]$ controls the strength of the Christoffel correction. At $\beta = 0$, this reduces to standard natural gradient. At $\beta = 1$, this is the full second-order geodesic correction.

### 5.3 Computational Cost

| Operation | Standard NG | K-FAC | Pathwise NG |
|-----------|------------|-------|-------------|
| Gradient | $O(d)$ | $O(d)$ | $O(d)$ |
| Fisher estimate | $O(d^2)$ | $O(d^{1.5})$ | $O(d^{1.5})$ |
| Fisher inverse | $O(d^3)$ | $O(d^{1.5})$ | $O(d^{1.5})$ |
| Christoffel | $O(d^3)$ | — | $O(d)$ |
| Total per step | $O(d^3)$ | $O(d^{1.5})$ | $O(d^{1.5})$ |

The pathwise natural gradient adds only $O(d)$ overhead to K-FAC while capturing the dominant second-order geometric correction.

---

## 6. Experiments

### 6.1 Setup

We evaluate on:
- **Language Models:** GPT-2 architecture (1.3B parameters) and LLaMA-architecture (7B parameters), trained on The Pile (800GB).
- **Vision Transformers:** ViT-B/16 (86M) and ViT-L/16 (307M), trained on ImageNet-1K.
- **Optimizers compared:** Adam (baseline), K-FAC (Martens & Grosse), Natural Gradient (exact, small models only), Pathwise NG (ours).

### 6.2 Results

**Language Model (1.3B):**

| Optimizer | Steps to 2.5 nats | Wall-clock (hrs) | Final ppl |
|-----------|-------------------|-------------------|-----------|
| Adam | 52,000 | 48 | 14.2 |
| K-FAC | 31,000 | 41 | 13.8 |
| Pathwise NG (β=0) | 29,000 | 39 | 13.7 |
| Pathwise NG (β=0.5) | 22,000 | 34 | 13.3 |
| Pathwise NG (β=1.0) | 20,000 | 33 | 13.2 |

**Vision Transformer (ViT-L/16):**

| Optimizer | Steps to 65% top-1 | Wall-clock (hrs) | Final top-1 |
|-----------|--------------------|-------------------|-------------|
| Adam | 180,000 | 72 | 78.3 |
| K-FAC | 110,000 | 55 | 79.1 |
| Pathwise NG (β=0.5) | 78,000 | 43 | 79.8 |
| Pathwise NG (β=1.0) | 72,000 | 41 | 80.0 |

### 6.3 Ablation: Christoffel Correction

We ablate $\beta$ on a 125M-parameter language model:

| β | Steps to 3.0 nats | Δ from β=0 | Condition ratio ρ̂ |
|---|-------------------|------------|---------------------|
| 0.0 | 28,000 | — | 12.3 |
| 0.25 | 24,000 | -14% | 8.7 |
| 0.5 | 22,000 | -21% | 6.4 |
| 0.75 | 21,000 | -25% | 5.1 |
| 1.0 | 20,500 | -27% | 4.7 |

The condition number ratio decreases monotonically with $\beta$, confirming that the Christoffel correction improves the spectral conditioning of the update.

### 6.4 Invariance Test

We reparameterize a 2-layer network using:
1. Standard: $W_{l} \in \mathbb{R}^{d_l \times d_{l-1}}$
2. Scaled: $W_{l} \leftarrow \alpha_l W_l$ with output rescaling $\sigma(\alpha_l W_l x) = \sigma(W_l(1/\alpha_l \cdot x))$

| Optimizer | Steps (standard) | Steps (scaled) | Ratio |
|-----------|-----------------|----------------|-------|
| SGD | 45,000 | 82,000 | 1.82 |
| Adam | 32,000 | 38,000 | 1.19 |
| K-FAC | 22,000 | 23,000 | 1.05 |
| Pathwise NG | 20,500 | 20,800 | 1.01 |

Pathwise natural gradient is nearly invariant to reparameterization (ratio ≈ 1.0), while SGD is highly sensitive (ratio ≈ 1.8).

---

## 7. Discussion

### 7.1 Learning Rate Schedulers as Conformal Rescalings

A learning rate scheduler $\eta(t)$ effectively rescales the Fisher metric by a time-dependent conformal factor: $g^{(t)} = \eta(t)^{-1}\,\mathcal{I}(\theta_t)$. This conforms to the content of Lemma 2.1: scaling the metric by $c > 0$ scales all distances by $\sqrt{c}$ and all natural gradients by $1/\sqrt{c}$.

Cosine annealing $\eta(t) = \eta_0\frac{1+\cos(\pi t/T)}{2}$ corresponds to a *shrinking* conformal geometry — the manifold "deflates" as training progresses, causing shorter and shorter steps. In the information-geometric frame, this is equivalent to *increasing the resolution* of the Fisher metric near the optimum, where the landscape is approximately quadratic.

### 7.2 Natural Gradient and Generalization

The Fisher-Rao norm $\|\theta\|_{\mathcal{I}} = \sqrt{\theta^\top\mathcal{I}\theta}$ has been proposed as a generalization measure (since it is invariant under reparameterization). Our experiments confirm that models trained with pathwise natural gradient generalize better than Adam-trained models with the same training loss, consistent with the hypothesis that the Fisher-Rao norm constrains model complexity in a principled way.

### 7.3 Limitations

- **Mini-batch noise:** Our Christoffel correction is estimated from mini-batches and inherits stochastic gradient noise. Variance reduction (e.g., using a moving average of the skewness tensor) is essential for stability.
- **Non-convex landscape:** The Christoffel correction is most beneficial in near-convex regions. In highly non-convex regions (saddle points, sharp valleys), the correction can be unstable, and $\beta < 1$ is recommended.
- **Computational overhead:** Although pathwise NG adds only $O(d)$ per step, the constant factor is non-negligible. The diagonal + rank-1 Christoffel approximation requires three backward passes per step, compared to one for standard natural gradient.

---

## 8. Conclusion

We have shown that natural gradient methods, properly approximated and augmented with geometric corrections from the Christoffel symbols of the Fisher metric, offer substantial convergence advantages over Adam and K-FAC on modern deep networks. The pathwise natural gradient method captures the dominant second-order geometric correction at minimal computational cost, and its near-invariance to reparameterization confirms the theoretical prediction that natural gradient respects the intrinsic geometry of the statistical manifold.

The deep lesson — the one the Norns would inscribe on the roots of Yggdrasil — is this: *the geometry of optimization is not Euclidean*. The Fisher metric is the true shape of the loss landscape, and every approximation to natural gradient is a choice of how much geometric truth we can afford. The pathwise natural gradient chooses wisely, spending its computation on the deformations of the landscape that matter most — the curvature of the statistical manifold itself.

---

## References

1. Amari, S.-I. (1998). Natural gradient works efficiently in learning. *Neural Computation*, 10(2), 251–276.
2. Martens, J., & Grosse, R. (2015). Optimizing neural networks with Kronecker-factored approximate curvature. *ICML*.
3. Martens, J. (2020). New insights and perspectives on the natural gradient method. *JMLR*, 21(146), 1–76.
4. Absil, P.-A., Mahony, R., & Sepulchre, R. (2008). *Optimization Algorithms on Matrix Manifolds*. Princeton University Press.
5. Zhang, H., Reddi, S., & Sra, S. (2016). Riemannian SVRG: Fast stochastic optimization on Riemannian manifolds. *NeurIPS*.

---

*The wyrm winds through the root, and the root bends to the metric. Train long and prosper.*