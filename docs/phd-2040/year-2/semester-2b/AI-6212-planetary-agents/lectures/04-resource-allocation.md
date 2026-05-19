# Lecture 04: Resource Allocation Under Uncertainty at Scale

**Date:** Week 4, May 5, 2040  
**Instructor:** Prof. Kwame Asante-Darko  

---

## 1. The Scale of the Problem

A single AI agent digging a well in the Sahara needs water, energy, soil sensors, and seeds—a modest resource bundle with modest uncertainty. Twelve million agents operating across 9.2 million square kilometers of desert, each facing local uncertainty about rainfall, soil quality, equipment degradation, and adversarial interference, need to allocate resources *globally* while acting *locally*. The question is not merely "how much water does each agent need?" but "how do we continuously redistribute water, energy, seeds, and human attention across a system that is simultaneously too large to centralize and too interdependent to decentralize?"

The Sahara Reforestation Project allocated resources worth approximately $2.1$ billion annually across 12 million agents. The annual waste from misallocation—resources unused where needed, over-allocated where not—was estimated at $340$ million in the first year before the deployment of the systems described in this lecture. After deploying market-based and optimization-based allocation in tandem, waste fell to $47$ million (a 86% reduction).

---

## 2. Formal Framework

### 2.1 The Stochastic Resource Allocation Problem

We model resource allocation as a **stochastic optimization** problem. At time $t$, the system state is $s_t \in \mathcal{S}$, capturing all relevant information: resource inventories, agent capabilities, environmental conditions, ongoing tasks. The decision variable is $\mathbf{x}_t \in \mathcal{X}$, the allocation vector mapping resources to agents.

The objective is to minimize expected total cost over a finite or infinite horizon:

$$\min_{\pi} \mathbb{E}\left[\sum_{t=0}^{T} \gamma^t c(s_t, \mathbf{x}_t)\right]$$

where $\pi$ is a policy mapping states to allocations, $\gamma \in (0,1]$ is a discount factor, and $c(s_t, \mathbf{x}_t)$ is the immediate cost (resource waste + ecological penalty + operational cost).

The state evolves as $s_{t+1} \sim P(\cdot | s_t, \mathbf{x}_t)$, where $P$ is the transition kernel capturing environmental dynamics, agent behavior, and exogenous shocks.

### 2.2 The Curse of Dimensionality

For $n$ agents and $m$ resource types, the state space has dimension $O(n \cdot m + n)$ (inventories + agent states). Even with binary resource levels, $|\mathcal{S}| = 2^{n \cdot m + n}$. For $n = 12 \times 10^6$ and $m = 7$ (water, energy, seeds, sensors, maintenance, labor, carbon credits), $|\mathcal{S}| = 2^{96 \times 10^6}$—a number so large that exhaustively enumerating it would exceed the Bekenstein bound for the observable universe.

Classical dynamic programming is infeasible. We need **structural decomposition** and **approximation**.

---

## 3. Decomposition Strategies

### 3.1 Spatial Decomposition

The Sahara Project decomposed the allocation problem geographically. The desert was partitioned into **6,000 cells**, each containing approximately 2,000 agents. Within each cell, a local allocator solved a smaller stochastic optimization:

$$\min_{\pi_i} \mathbb{E}\left[\sum_{t=0}^{T} \gamma^t c_i(s_t^i, \mathbf{x}_t^i)\right]$$

where $s_t^i$ and $\mathbf{x}_t^i$ are the local state and allocation for cell $i$. The critical question: are the cells independent?

**Theorem (Approximate Decomposability):** If cell $i$'s transition dynamics depend on the global state only through a sufficient statistic $\phi(s_t)$ (a compressed representation of global conditions), and $\phi$ has dimension $d \ll n$, then:

$$V_{\text{global}}^* \leq \sum_i V_i^* + O\left(\frac{\text{coupling strength}}{d}\right)$$

where $V_{\text{global}}^*$ is the optimal global value and $V_i^*$ is the optimal local value. The **price of decomposition**—the gap between centralized and decentralized solutions—is bounded by coupling strength divided by informativeness.

In the Sahara, the sufficient statistic $\phi(s_t)$ was a 47-dimensional vector capturing regional weather forecasts, aggregate water levels, carbon credit prices, and equipment health distributions. This compressed the 96-million-dimensional state into a manageable summary.

### 3.2 Temporal Decomposition

Over a 50-year project horizon, time scales naturally separate:

- **Seconds–minutes:** Sensor readings, local adjustments (solve via reactive control)
- **Minutes–hours:** Resource redistribution within cells (solve via local markets)
- **Hours–days:** Inter-cell resource transfer (solve via regional optimization)
- **Days–weeks:** Seasonal planning, fleet repositioning (solve via model predictive control)
- **Weeks–months:** Strategic decisions, policy changes (solve via simulation-based optimization)

Each time scale is addressed by a different solver, with the outputs of longer-horizon solvers providing constraints and targets for shorter-horizon ones. This **temporal multi-resolution** approach ensured that urgent decisions (e.g., wildfire response) were not blocked waiting for strategic optimization.

### 3.3 Resource Decomposition

Different resources have different allocation characteristics:

| Resource | Divisible? | Perishable? | Transport Cost | Allocation Method |
|----------|-----------|-------------|----------------|-------------------|
| Water | Yes | Yes (evaporation) | High | Local market + pipeline |
| Energy | Yes | No (battery) | Medium | Distributed auction |
| Seeds | No (discrete) | Yes (viability) | Low | Batch optimization |
| Sensors | No (discrete) | No | Medium | Combinatorial auction |
| Carbon credits | Yes | No | Negligible | Global exchange |
| Labor | No | No | High | Assignment problem |
| Maintenance | No | No | Medium | Priority queue |

The Sahara Project used **mixed allocation**: continuous resources via **dual decomposition** (the Lagrangian relaxation of coupling constraints creates subproblems that can be solved in parallel), discrete resources via **combinatorial auction**, and hybrid resources via **iterative auction** with Walrasian price adjustment.

---

## 4. Market-Based Allocation

### 4.1 The Role of Markets

Decentralized markets solve the computational intractability of centralized allocation by distributing computation across agents. Each agent computes its own demand given prices, and the market aggregates demands to find equilibrium prices. The computational burden scales as $O(n)$ (each agent computes locally) rather than $O(n^2)$ or worse.

### 4.2 Fisher Market and the Eisenberg-Gale Program

A **Fisher market** consists of $n$ buyers with budgets $b_i$ and $m$ divisible goods with supplies $s_j$. Each buyer has a utility function $u_i(x_i)$ over allocations $x_i$. The competitive equilibrium is the solution to:

$$\max_{x} \sum_i b_i \log u_i(x_i) \quad \text{subject to} \quad \sum_i x_{ij} \leq s_j \quad \forall j$$

This **Eisenberg-Gale program** is a convex optimization, solvable in polynomial time. The Sahara Project's water allocation used a Fisher market where:

- Budgets $b_i$ were proportional to each agent's verified ecological output (trees planted, survival rate)
- Utility was Cobb-Douglas: $u_i(x_i) = \prod_j x_{ij}^{\alpha_{ij}}$ (agents need complementary resources)
- Supplies $s_j$ were updated every 5 minutes based on pipeline capacity and reservoir levels

### 4.3 Tâtonnement Dynamics

The Fisher market equilibrium can be reached via **tâtonnement**: prices $p_j$ are adjusted in proportion to excess demand:

$$p_j(t+1) = \max\left(\epsilon, p_j(t) + \gamma \cdot \text{excess\_demand}_j(t)\right)$$

Convergence of tâtonnement for Cobb-Douglas utilities is guaranteed, with rate $O(1/t)$. In practice, the Sahara's water market converged in 8–12 iterations per epoch (5-minute intervals).

### 4.4 Auctions for Indivisible Resources

For indivisible resources (sensors, labor, seed batches), the project used **simultaneous ascending auctions** (SAAs). Each resource type has its own auction. Agents submit bundle bids (e.g., "I'll pay 50 credits for {3 sensors, 2 seed batches, 100L water}"). The winner determination problem is:

$$\max \sum_i b_i \cdot x_i \quad \text{subject to} \quad \text{each item assigned to at most one bidder}$$

This is NP-hard in general, but tractable for the Sahara's instance sizes (thousands of agents bidding on hundreds of distinct resource types per cell) using branch-and-bound with LP relaxation.

### 4.5 The VCG Mechanism and Its Scalable Approximations

The **VCG mechanism** is the unique DSIC, Pareto efficient mechanism. It charges each agent its externality: the welfare loss imposed on others by its presence. The computational challenge: VCG requires solving the allocation problem $n+1$ times (once for the full problem, once for each agent removed).

For $n = 12 \times 10^6$, this is infeasible. The Sahara Project used **MaaVCG** (Market-approximate VCG):

1. Solve the allocation optimally for each cell (tractable, $O(s^2)$ per cell).
2. Charge cells the externality their demand imposes on other cells (via shadow prices from the global price vector).
3. Within each cell, use local VCG for agent-level charges.

This scheme is DSIC at the cell level, approximately DSIC at the agent level, and incurs at most 8% efficiency loss relative to the full VCG (as computed via simulation on historical data).

---

## 5. Robust and Distributionally Robust Optimization

### 5.1 Beyond Expected Value

Expected value minimization assumes full knowledge of the distribution $P$. In practice, $P$ is estimated from data and may be inaccurate. **Robust optimization** minimizes worst-case cost:

$$\min_{\mathbf{x}} \max_{P \in \mathcal{P}} \mathbb{E}_P[c(s, \mathbf{x})]$$

where $\mathcal{P}$ is an **ambiguity set**—a family of plausible distributions. The Sahara Project used a **Wasserstein ambiguity set**:

$$\mathcal{P} = \{P : W_2(P, \hat{P}) \leq \epsilon\}$$

where $\hat{P}$ is the empirical distribution from historical data and $W_2$ is the 2-Wasserstein distance. The radius $\epsilon$ was calibrated via out-of-sample validation to achieve 95% out-of-sample feasibility.

### 5.2 Distributionally Robust Allocation

The **Distributionally Robust** (DR) allocation problem:

$$\min_{\mathbf{x}} \sup_{P \in \mathcal{P}} \mathbb{E}_P[c(s, \mathbf{x})]$$

can be reformulated as a tractable convex program when $c$ is convex in $\mathbf{x}$ and $\mathcal{P}$ is a Wasserstein ball. The Sahara Project solved a DR variant of the Eisenberg-Gale program with Wasserstein ambiguity, yielding allocations that were guaranteed feasible for 95% of plausible future scenarios—compared to 68% for the nominal (expected-value) solution.

The computational cost: a DR Fisher market takes $3$–$5\times$ longer to solve than nominal. Given that the nominal solution converges in seconds, this is acceptable—the DR solution still converges within the 5-minute market epoch.

### 5.3 Chance Constraints

Some constraints cannot be violated without catastrophic consequences. For example, no cell should have less than 24 hours of water reserves with probability less than 0.01%. This is a **chance constraint**:

$$P\left(\text{water reserves in cell } i \geq \text{reserve}_{\min}\right) \geq 1 - 10^{-4}$$

Under Gaussian or elliptical distribution assumptions, chance constraints can be reformulated as deterministic convex constraints using the **Chebyshev-Cantelli inequality** or **quantile** reformulations. The Sahara Project used the **sample average approximation** (SAA) approach: generate $N$ scenarios from $\hat{P}$, and enforce the constraint in all scenarios:

$$\frac{1}{N} \sum_{k=1}^{N} \mathbb{1}[\text{reserves}_i(s^k) \geq \text{reserve}_{\min}] \geq 1 - \alpha$$$

with $N = 10,000$ scenarios and $\alpha = 0.001$.

---

## 6. Reinforcement Learning at Scale

### 6.1 Multi-Agent Reinforcement Learning (MARL)

The allocation problem can be formulated as a **decentralized partially observable Markov decision process** (DEC-POMDP). Solving DEC-POMDP optimally is NEXP-hard. However, the structure of the resource allocation problem—the spatial decomposition, the temporal hierarchy, the market interface—enables tractable approximations.

The Sahara Project used **hierarchical reinforcement learning** (HRL):

- **Top level:** A policy $\pi_{\text{top}}$ sets allocation targets for each cell based on the compressed global state $\phi(s_t)$.
- **Mid level:** Within each cell, a policy $\pi_{\text{cell}}^i$ allocates resources to agents based on local state and top-level targets.
- **Bottom level:** Individual agents execute reactive policies $\pi_{\text{agent}}^j$ based on sensor inputs and allocated resources.

### 6.2 Training at Scale

Training 12 million agent policies is infeasible. Instead, the project trained:

- 1 top-level policy (global allocator)
- 6,000 cell-level policies (parameter-shared, with cell-specific conditioning)
- ~20 agent-level policy archetypes (clustered by agent type and terrain)

Training used **centralized training, decentralized execution** (CTDE): during training, all policies were updated using global information; during execution, each policy used only local observations plus the compressed global state $\phi(s_t)$.

The top-level policy was trained via **proximal policy optimization** (PPO) on a high-fidelity simulator with 50 years of environmental data. The cell-level policies were trained via **mean-field MARL**, where each cell's policy learned to respond to the aggregate (mean-field) behavior of other cells, rather than tracking each individually.

---

## 7. Performance Summary: Sahara Resource Allocation

| Metric | Year 1 (Pre-reform) | Year 3 (Post-reform) | Year 5 (Optimized) |
|--------|---------------------|---------------------|---------------------|
| Annual resource waste | $340M | $89M | $47M |
| Water delivery efficiency | 71% | 89% | 94% |
| Agent utilization rate | 68% | 82% | 91% |
| Emergency response time | 14 min | 4.2 min | 1.8 min |
| Allocation overhead (compute) | 0.3% | 1.1% | 0.8% |
| DR out-of-sample feasibility | — | 92% | 96% |

---

## 8. Key Takeaways

1. **Classical stochastic optimization is infeasible at planetary scale.** Decomposition—spatial, temporal, and resource-wise—is essential.
2. **Markets are computational tools.** They distribute computation across agents, achieving $O(n)$ scaling where centralized optimization is $O(n^2)$ or worse.
3. **Robustness is not optional.** Distributionally robust and chance-constrained formulations provide provable feasibility guarantees that nominal optimization cannot.
4. **Hierarchical RL bridges the scale gap.** Train a few thousand policies (not millions) via parameter sharing and mean-field approximation.
5. **The Sahara's 86% waste reduction** validates the combined market + optimization + RL approach at billion-dollar scale.

---

## 9. Further Reading

- Bertsimas, D. & Kallus, N. "From Predictive to Prescriptive Analytics." *Management Science 2020*.
- Okafor, M. & Diallo, A. "Market-Based Resource Allocation for Planetary-Scale Agent Systems." *AAMAS 2037*.
- Wiesemann, W., Kuhn, D., & Sim, M. "Distributionally Robust Convex Optimization." *Operations Research 2014*.
- Lowe, R. et al. "Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments." *NeurIPS 2017*.
- Parkes, D. & Vorobeychik, S. *Mechanism Design for Multi-Agent Systems*, Ch. 11–13 (2033).