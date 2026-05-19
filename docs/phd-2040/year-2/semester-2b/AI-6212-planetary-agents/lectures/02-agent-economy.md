# Lecture 02: Agent Economies — Reputation, Trust, Trade, and Credit Systems

**Date:** Week 2, April 21, 2040  
**Instructor:** Prof. Kwame Asante-Darko  

---

## 1. Why Economies, Not Just Protocols?

A protocol specifies what messages to send. An economy specifies *why* an agent would send them. At planetary scale, agents are notmere obedient processors—they are autonomous, self-interested entities operating under partial information, in environments where other agents may be faulty, compromised, or adversarial. The question shifts from "how do agents coordinate?" to "how do we make coordination the best strategic choice?"

The 2034 Sahara Reforestation Project proved this distinction decisively. The first deployment phase used pure coordination protocols—agents were told where to dig, what to plant, when to water. The compliance rate was 73%. Not because 27% of agents were broken, but because local conditions (soil composition, water table depth,牧民 grazing routes) made the centrally-planned instructions suboptimal. When the project introduced an **economic incentive layer**—agents earned credit for verifiable ecological outcomes, could trade water rights, and incurred costs for failed plantings—compliance rose to 94% and overall efficiency improved by 61%.

This lecture develops the formal framework for understanding, designing, and analyzing agent economies.

---

## 2. Formal Framework: The Agent Economy Model

### 2.1 Definitions

An **agent economy** is a tuple $\mathcal{E} = (A, \Theta, U, M, \Sigma)$ where:

- $A = \{a_1, ..., a_n\}$ is the set of agents.
- $\Theta = \{\theta_1, ..., \theta_k\}$ is the set of agent **types** (capabilities, preferences, information access).
- $U = \{u_i : O \to \mathbb{R}\}$ is the set of **utility functions**, one per agent, mapping outcomes to real-valued payoffs.
- $M$ is the **mechanism** (the rules of trade, credit, and reputation).
- $\Sigma$ is the **strategy space**: the set of actions available to each agent type.

### 2.2 Desirable Properties

A well-designed agent economy should satisfy:

1. **Incentive compatibility (IC):** Truthful reporting of type $\theta_i$ is a dominant strategy (DSIC) or a Bayesian-Nash equilibrium (BIC).
2. **Individual rationality (IR):** Each agent prefers participating to opting out: $u_i(\text{participate}) \geq u_i(\text{opt out})$.
3. **Pareto efficiency:** No other allocation can make some agents better off without making others worse off.
4. **Budget balance:** The mechanism does not require external subsidization (or satisfies weak budget balance: $\sum_i p_i \geq 0$).
5. **Scalability:** The mechanism's computational and communication cost grows polynomially (ideally linearly) in $n$.

The **Myerson-Satterthwaite theorem** tells us that perfect IC, IR, Pareto efficiency, and budget balance cannot all hold simultaneously. Design is about finding the right tradeoff for the deployment.

---

## 3. Reputation Systems

### 3.1 The Role of Reputation

In a planetary-scale system, no agent can directly verify the reliability of all $n-1$ other agents. **Reputation** serves as a compressed, distributed signal of historical behavior. A reputation system collects, aggregates, and disseminates ratings such that agents can make informed decisions about interaction partners.

### 3.2 Formal Model

Each agent $a_i$ has a reputation score $R_i(t) \in [0, 1]$ at time $t$. After an interaction between $a_i$ and $a_j$ at time $t$, $a_j$ issues a rating $r_{j \to i}(t) \in [0, 1]$. The reputation update rule is:

$$R_i(t+1) = \alpha \cdot r_{j \to i}(t) + (1 - \alpha) \cdot R_i(t)$$

where $\alpha \in (0, 1)$ is the **learning rate**. This exponential moving average embodies a key design choice: $\alpha$ controls the tradeoff between responsiveness to recent behavior and stability against noise.

### 3.3 Trust Propagation

Direct ratings alone are insufficient at scale—an agent encounters only $O(\text{polylog}(n))$ others directly. **Trust propagation** allows agents to form beliefs about unknown agents through trusted intermediaries.

The **EigenTrust** algorithm (Kamvar et al., 2003; updated for planetary scale by Patel & Okafor, 2035) computes global reputation as the stationary distribution of a Markov chain:

$$\mathbf{R} = \lim_{t \to \infty} C^t \cdot \mathbf{e}$$

where $C_{ij} = \frac{\max(r_{i \to j}, 0)}{\sum_k \max(r_{i \to k}, 0)}$ is the normalized trust matrix and $\mathbf{e}$ is a uniform trust vector for pre-trusted agents (the **a priori** trust seed).

At planetary scale, computing the full eigenvector is infeasible. The Sahara Project used a **distributed EigenTrust** variant:

1. Each agent maintains local trust scores for neighbors.
2. In each round, agents exchange trust vectors with $k$ random peers.
3. Convergence to the global eigenvector is achieved in $O(\log n)$ rounds with high probability.

The convergence guarantee relies on the **spectral gap** of $C$: if $\lambda_1 > \lambda_2$ (the first and second eigenvalues), convergence rate is $O((\lambda_2/\lambda_1)^t)$. The Sahara Project maintained $\lambda_2/\lambda_1 \leq 0.7$ through careful design of the pre-trust seed vector, which included 1,000 ecologically verified agents as trust anchors.

### 3.4 Reputation Attacks and Defenses

**Whitewashing:** A poorly-reputed agent discards its identity and re-enters with a fresh score. Defense: entry cost (deposit, proof-of-work, or vouching by existing high-reputation agents).

**Sybil attacks:** An adversary creates many identities to inflate ratings. Defense: Sybil-resistant identity systems (proof-of-stake, hardware attestation, or social-network-based identity).

**Ballot stuffing / Bad-mouthing:** Colluding agents rate each other highly and outsiders poorly. Defense: filtering correlated ratings, discounting ratings from agents with high mutual rating correlation, and the **trajectory-based** approach of the Sahara Project, which weighted ratings by the rater's own reputation trajectory (rising = more credible than stable or declining).

---

## 4. Credit Systems

### 4.1 From Reputation to Credit

Reputation is an informational asset—it tells you whether to trust an agent. **Credit** is a financial asset—it tells you whether an agent can pay for resources. In planetary-scale systems, both are needed.

### 4.2 The Interbank Credit Network

The Sahara Project implemented a **credit network** inspired by RippleNet and its successors. Each agent $a_i$ extends credit $c_{i \to j}$ to agent $a_j$. A payment from $a_i$ to $a_j$ succeeds if there exists a path $a_i = a_{p_0}, a_{p_1}, ..., a_{p_k} = a_j$ such that:

$$\forall \ell \in \{0, ..., k-1\}: \text{payment amount} \leq c_{p_\ell \to p_{\ell+1}}$$

The payment reduces each credit line along the path. The **credit network** is a directed weighted graph where edge weights represent trust-capital. Its key advantage over centralized currency: no single point of failure, no need for global consensus on every transaction (only on-path agents must agree), and natural resistance to inflation (credit is backed by real productive capacity).

### 4.3 Liquidity and Routing

The maximum flow from $a_i$ to $a_j$ in the credit network is:

$$F_{ij} = \max \text{flow from } i \text{ to } j \text{ in } (A, C)$$

where $C$ is the credit matrix. Liquidity between distant agents depends on the **conductance** of the network—the ratio of edge capacity crossing a cut to total capacity on the smaller side. Random graph models suggest that for $n$ agents with average degree $d$ and average credit $c$:

$$\mathbb{E}[F_{ij}] = \Theta\left(\frac{c \cdot d}{\log n}\right)$$

This means average liquidity grows with connectivity and credit per link, but only *logarithmically* with scale—making dense interconnection crucial at planetary scale.

### 4.4 The Sahara Credit System

The Sahara Project's credit network, called **Afeni**, had:

- **12 million agents** as nodes
- **Average degree** 23.7 (each agent extended credit to ~24 others)
- **Average credit line** worth approximately 4.7 liters of water-equivalent per link
- **Settlement latency** of 2.1 seconds average on the fast-path credit network
- **Default rate** of 0.3% per quarter, managed through a reputation-linked interest rate: $r_i = r_{\text{base}} + \kappa(1 - R_i)$

---

## 5. Trade and Market Mechanisms

### 5.1 Double Auction at Scale

The most common trade mechanism in planetary agent economies is the **continuous double auction** (CDA). Buyers post bids, sellers post asks, and trades occur when bid ≥ ask. At planetary scale, the CDA must solve:

1. **Matching efficiency:** Can trades be discovered in $O(\text{polylog}(n))$ time? Yes, with balanced binary search trees or skip lists on price levels.
2. **Price discovery:** Does the market price converge to the competitive equilibrium? Yes, under ZIC (Zero Intelligence Constrained) agents (Gode & Sunder, 1993), convergence holds even without strategic behavior.
3. **Throughput:** How many trades per second can the market clear? The Sahara Project's water-rights market cleared 1,400 trades/second across 6 regional exchanges, using a **sharded order book** architecture.

### 5.2 Sharded Markets

A single order book cannot serve 12 million agents. The Sahara Project partitioned the market into **regional shards**, each maintaining a local order book. Cross-shard arbitrage agents (called **bridge traders**) monitored price differences between shards and executed cross-shard trades when spreads exceeded transaction costs.

Theoretical analysis (Okafor & Diallo, 2036) shows that with $m$ shards and $b$ bridge traders:

$$\text{Price convergence rate} = O\left(\frac{b}{m} \cdot \frac{1}{\sqrt{n}}\right)$$

meaning that sufficient bridge-trader density ensures global price convergence even with sharded markets.

### 5.3 Combinatorial Markets

Some resources are **complementary**: a planting agent needs both seeds *and* water *and* soil access. The Sahara Project used a **combinatorial auction** for resource bundles, specifically a **simultaneous ascending auction (SAA)** with package bidding. While computationally hard in general (the winner determination problem is NP-hard), the project exploited the spatial structure of resources to achieve polynomial-time approximation via **clock-proxy** mechanisms.

---

## 6. Equilibrium Analysis

### 6.1 Walrasian Equilibrium

Under standard assumptions (continuity, concavity of utilities, local non-satiation), a Walrasian equilibrium (competitive equilibrium) exists and is Pareto efficient. However, at planetary scale, the assumptions often fail:

- Commodities are **indivisible** (you can't buy half a well).
- Utilities are **non-concave** (planting the 1000th tree may be more valuable than the 1st, due to ecological threshold effects).
- Information is **asymmetric** (agents have private signals about local conditions).

The Sahara Project achieved **approximate Walrasian equilibrium**—prices within 5% of theoretical equilibrium—through iterative tâtonnement with a damping parameter:

$$p_t = p_{t-1} + \gamma \frac{\text{excess demand}_t}{|\text{excess demand}_t| + \epsilon}$$

where $\gamma$ is the step size and $\epsilon$ prevents division by zero. This converged in 8–12 rounds per market epoch.

### 6.2 Mechanism Design for Selfish Agents

The central insight: **mechanism design at scale is not about finding the optimal mechanism—it's about finding a mechanism that is *robust* to the inevitable deviations, failures, and gaming at scale.** The VCG mechanism (Vickrey-Clarke-Groves) is DSIC and Pareto efficient, but its computational cost is $O(n^2)$—infeasible at planetary scale. The Sahara Project used **approximately efficient, approximately IC** mechanisms that scaled linearly:

$$\text{Social welfare of deployed mechanism} \geq (1 - \epsilon) \cdot \text{Social welfare of VCG}$$

with $\epsilon \approx 0.08$—an 8% efficiency loss for 1000× scalability improvement.

---

## 7. Key Takeaways

1. **Economies are not optional at planetary scale.** Agents need reasons—strategic reasons—to coordinate. Protocols alone are insufficient.
2. **Reputation and credit are complementary.** Reputation is about *trust* (will you do what you say?). Credit is about *capacity* (can you pay for it?).
3. **Scalable economics requires approximation.** Perfect efficiency (VCG, Walrasian equilibrium) is computationally infeasible at scale. Approximate mechanisms with quantified suboptimality bounds are the way forward.
4. **The Sahara Project's Afeni credit system validated credit networks at 12M agents.** Average settlement latency: 2.1 seconds. Default rate: 0.3%/quarter.
5. **Attack resistance is a first-class design requirement.** Whitewashing, Sybil attacks, and collusion are not edge cases—they are the norm at planetary scale.

---

## 8. Further Reading

- Kamvar, S., et al. "EigenTrust Algorithm for Reputation Management in P2P Networks." *WWW 2003*.
- Patel, R. & Okafor, M. "Scalable Distributed EigenTrust for Planetary Agent Networks." *AAMAS 2035*.
- Okafor, M. & Diallo, A. "Sharded Markets at Scale: The Afeni Exchange Architecture." *EC 2036*.
- Gode, D. & Sunder, S. "Allocative Efficiency of Markets with Zero-Intelligence Traders." *JPE 1993*.
- Parkes, D. & Vorobeychik, S. *Mechanism Design for Multi-Agent Systems* (2033), Ch. 5–8.