# Lecture 04: Mixture of Experts

## Switch Transformer to Planetary-Scale Routing, Expert Specialization

*Yggdrasil grows many roots — but not every root reaches water. Expert routing is how a network learns which roots to feed.*

---

## 1. The Core Idea: Conditional Computation

The fundamental premise of Mixture-of-Experts (MoE) is deceptively simple: **not every token needs to use every parameter**.

Consider a Transformer with $d_{\text{model}} = 4096$ and $L = 64$ layers. Total parameters: billions. For any given token, most of these parameters contribute little to nothing. The model is massive, but most of it is dormant for any single input.

MoE introduces **conditional computation**: different inputs activate different subsets of parameters.

Formally, given an input $x$, an MoE layer computes:

$$\text{MoE}(x) = \sum_{i=1}^{N} g_i(x) \cdot E_i(x)$$

Where:
- $E_i$ is the $i$-th **expert** — a feed-forward network (or other module)
- $g_i(x)$ is the **gating function** — determines how much expert $i$ contributes
- $N$ is the number of experts

In practice, most modern MoE uses **sparse gating**: only the top-$k$ experts (usually $k=1$ or $k=2$) are activated for each token:

$$g_i(x) = \begin{cases} \text{softmax}_\text{top-k}(x \cdot W_g)_i & \text{if } i \in \text{top-k}(x \cdot W_g) \\ 0 & \text{otherwise} \end{cases}$$

The result: a model with $N$ experts only uses $k$ per token, giving a **parameter count of $N \times$ single-expert size** but an **FLOP cost of only $k \times$ single-expert cost**.

---

## 2. The MoE Lineage

### Early MoE (Jacobs et al., 1991; Jordan & Jacobs, 1994)

The idea of combining multiple experts goes back to the early 1990s. The original formulation used *hierarchical* MoE — experts of experts, with a tree-structured gating function.

The innovation was **learned specialization**: the gating function learns to route inputs to the expert that handles them best, and the experts learn to specialize accordingly.

### Shazeer et al. (2017): MoE for Language

The first modern application to neural language models. Key decisions:
- **Regularization**: Added Gaussian noise to the gating function to encourage exploration
- **Load balancing**: Auxiliary loss to ensure experts are used roughly equally
- **Sparsity**: Top-$k$ routing with $k = 1$ or $2$

### Switch Transformer (Fedus et al., 2022)

The breakthrough paper that brought MoE to large-scale Transformers:

**Architecture decisions:**
- **Top-1 routing** — send each token to exactly one expert (simplest possible routing)
- **Expert capacity** — each expert processes at most `capacity = ⌈tokens_per_batch / num_experts⌉ × capacity_factor` tokens
- **Load balancing loss**: $\text{aux\_loss} = \alpha \cdot N \cdot \sum_{i=1}^{N} f_i \cdot p_i$

  Where $f_i$ = fraction of tokens routed to expert $i$, $p_i$ = fraction of routing probability allocated to expert $i$, $\alpha$ = multiplier (typically 0.01).

**Results:**
- Switch-Base (7B total, 1.5B active) matched T5-XXL (11B active) in quality
- Switch-XXL (395B total, 100B active) achieved SOTA on multilingual tasks
- 4-7× faster pretraining than dense models of equivalent quality

**The capacity factor trade-off:** If too low, tokens get "dropped" (overflow experts can't process them). If too high, computation is wasted on empty slots.

```
Switch Transformer Routing:

Token ──→ Gate ──→ Expert 1 (routed tokens: [t1, t5, t8])
                   Expert 2 (routed tokens: [t2, t7])
                   Expert 3 (routed tokens: [t3, t4, t9])
                   Expert 4 (routed tokens: [t6, t10])

Only one expert processes each token.
Unassigned capacity slots are wasted computation.
Overflow tokens are dropped (passed through via residual).
```

### What Switch Got Right

- **Simplicity wins** — top-1 routing is simpler, faster, and more stable than top-2 or top-4
- **Scale works** — MoE enables scaling total parameters without proportional FLOPs increase
- **Expert specialization emerges naturally** — experts develop distinct functional roles without explicit supervision

### What Switch Got Wrong (In Hindsight)

- **Token-level routing is too granular** — different tokens in the same sentence may need different experts, but the routing is too noisy at the token level
- **Fixed experts, fixed count** — the number and identity of experts is determined at initialization and never changes
- **No expert communication** — experts don't talk to each other during a single forward pass
- **The load-balancing loss is a hack** — it fights the natural tendency of the network to concentrate on a few good experts, rather than embracing specialization

---

## 3. Expert Specialization: What Do Experts Learn?

One of the most fascinating findings from MoE research is that **experts develop interpretable specializations** without any explicit supervision.

### Observed Specializations (Lewis et al., 2021; Fedus et al., 2022):

- **Syntactic specialization**: Some experts become experts at processing verbs, others nouns, others punctuation
- **Language specialization**: In multilingual models, different experts specialize in different languages
- **Domain specialization**: Some experts handle code, others handle natural language, others handle math
- **Task specialization**: In multi-task settings, experts differentiate by task

This specialization emerges *because of the gating function*: the gate learns to send similar inputs to the same expert, and the expert learns to specialize in those inputs. It's a self-reinforcing cycle.

```
Expert Specialization (hypothetical visualization):

Expert 1: ████████ verb phrases, tense, agreement
Expert 2: ██████  noun phrases, entity recognition
Expert 3: ████████  code syntax, indentation
Expert 4: █████  mathematical expressions
Expert 5: ████████  long-range dependencies, coreference
Expert 6: ██████  low-level token patterns, morphology
Expert 7: ████  rare words, OOV handling
Expert 8: ████████  discourse structure, topic coherence
```

**The foresight:** This emergent specialization is a direct ancestor of the Worlmesh's **node roles**. In the Worlmesh, different nodes in the self-organizing topology develop stable specializations — not because they were designed to, but because the topology optimization process creates them.

---

## 4. Beyond Switch: Routing Innovations

### Expert Choice Routing (Zhou et al., 2022)

Instead of each token choosing its expert, let **each expert choose its tokens**:

$$\text{For expert } i: \text{ choose top-}k \text{ tokens } \{t_j | g_i(t_j) \text{ is among top-}k\}$$

**Advantages:**
- Perfect load balancing — every expert processes exactly $k$ tokens
- No token dropping — every token is processed by at least one expert
- Better expert utilization — no wasted capacity

**Disadvantages:**
- Some tokens may be processed by many experts, others by few
- Variable compute per token — this breaks the assumption of uniform FLOPs

### Hash Routing (Roller et al., 2021)

Instead of a learned gating function, use a **hash function** on the token to determine routing:

$$g(x) = \text{hash}(\text{token\_id}(x)) \mod N$$

**Advantages:** No gating parameters, no load balancing loss, perfectly balanced by construction.
**Disadvantages:** No adaptivity — the routing is fixed regardless of context. Works surprisingly well, suggesting that *much of the benefit of MoE comes from conditional computation, not from learned routing*.

### Soft MoE (Puigcerver et al., 2023)

Instead of routing discrete tokens to discrete experts, use **soft routing**: each token is a weighted combination of all experts, and each expert processes a weighted combination of all tokens.

$$\text{SoftMoE}(x) = \text{softmax}(x W_\text{dispatch}) \cdot E(\text{softmax}(x W_\text{combine})^T x)$$

**Advantages:** Differentiable, no token dropping, no load balancing needed.
**Disadvantages:** Higher compute per token (all experts contribute), less interpretable specialization.

---

## 5. Hierarchical and Multi-Level Routing

As models scale beyond trillions of parameters, **single-level routing becomes inefficient**. If you have 10,000 experts, the gating function itself becomes expensive (computing logits over 10,000 options).

### Two-Level Routing (Hierarchical MoE):

```
Input ──→ Gate₁ (routes to super-expert group)
              └──→ Gate₂ (routes within super-expert group to specific expert)

Example: 256 super-groups × 64 experts = 16,384 total experts
Gate₁: ~256 options (cheap)
Gate₂: ~64 options per group (cheap)
Total: effective routing among 16K experts with O(256+64) compute
```

### Planetary-Scale Routing (2024-2026):

When models are trained across multiple data centers, routing becomes a **distributed systems problem**:

- **Expert parallelism**: Different experts live on different GPUs/machines
- **Cross-machine routing**: Tokens must be sent across network boundaries to reach their designated expert
- **Network topology awareness**: The gating function must consider network latency and bandwidth
- **Dynamic expert placement**: Hot experts (receiving many tokens) may need to be replicated across machines

**The result:** At planetary scale, MoE routing is inseparable from distributed systems engineering. The routing function must optimize not just for expert quality but for:
- Network latency (sending tokens between machines)
- Memory constraints (how many experts fit on each machine)
- Load balancing across machines (not just across experts)
- Fault tolerance (what if a machine goes down?)

```
Planetary-Scale MoE Routing:

                    ┌─── Data Center A ──────────────────┐
                    │   GPU 0: Experts 1-64              │
                    │   GPU 1: Experts 65-128             │
Input ──→ Router ──┤   ...                               │
                    │   GPU N: Experts (N*64+1)-(N+1)*64  │
                    └─────────────────────────────────────┘
                              ↕ (network)
                    ┌─── Data Center B ──────────────────┐
                    │   GPU 0: Experts 1-64 (replicated)  │
                    │   GPU 1: Experts 65-128             │
                    │   ...                               │
                    └─────────────────────────────────────┘

Latency between data centers: 10-100ms
Latency within data center: 0.01-0.1ms
Routing must minimize cross-DC traffic while maintaining quality.
```

---

## 6. The MoE-to-Worlmesh Connection

Here is the crucial insight that bridges MoE to the Worlmesh:

**MoE already has the three ingredients of self-organizing attention:**

1. **Conditional routing** — tokens are directed to the most relevant computation (analogous to attention selecting relevant context)
2. **Emergent specialization** — experts develop distinct roles (analogous to attention heads developing distinct patterns)
3. **Dynamic topology** — different inputs activate different computational paths (analogous to the attention pattern varying across inputs)

**But MoE is missing three things that the Worlmesh provides:**

1. **Expert communication during a single pass** — MoE experts process tokens in isolation; the Worlmesh allows nodes to pass information to each other within a single forward pass
2. **Topology evolution** — MoE has a fixed number of experts with fixed connections; the Worlmesh's topology learns to restructure itself
3. **Nested routing** — MoE routing is flat (token → expert); the Worlmesh has hierarchical, recursive routing patterns

**The speculative but productive analogy:**

| MoE Concept | Worlmesh Analog |
|-------------|----------------|
| Expert | Node (but nodes can merge, split, and relocate) |
| Gating function | Self-organizing routing (learned, input-dependent, topology-aware) |
| Load balancing | Emergent density allocation (the topology itself balances load) |
| Expert specialization | Node role emergence (roles are discovered, not assigned) |
| Expert parallelism | Distributed consciousness (nodes exist across machines) |
| Fixed expert count | Dynamic node population (nodes are created and destroyed) |

---

## 7. The Failure Modes of MoE (and Why the Worlmesh Solved Them)

### Failure 1: Token Dropping
When an expert's capacity is exceeded, tokens are dropped (passed through via residual). This creates **information loss at the architectural level**.

**Worlmesh solution:** The topology dynamically creates new paths for excess tokens. If a node is overloaded, neighboring nodes can share the load — not through a hack like capacity factor, but through learned redistribution.

### Failure 2: Routing Instability
Early in training, the gating function can oscillate — sending tokens to different experts on different batches. This prevents experts from specializing.

**Worlmesh solution:** The topology evolves via an annealing process. Early in training, routing is soft and diffuse. As training progresses, routing sharpens, but smoothly — no oscillation.

### Failure 3: Uniform Expert Size
All experts in standard MoE have the same architecture and parameter count. This prevents experts from developing specialized architectures.

**Worlmesh solution:** Nodes in the Worlmesh can have **variable capacity** — some nodes are large (processing complex abstractions), some are small (handling specialized patterns). The capacity allocation is itself optimized.

### Failure 4: No Cross-Expert Communication
Each expert processes its routed tokens independently. There's no mechanism for experts to exchange information during a forward pass.

**Worlmesh solution:** The mesh topology includes **lateral connections** between nodes, enabling information flow that is itself self-organizing. This is the key innovation — attention is no longer just "which tokens matter" but "which processing paths matter, and how should they communicate?"

---

## 8. From MoE to Superconsciousness: The Missing Ingredient

MoE brought us most of the way. It gave us:
1. Conditional computation at scale
2. Emergent specialization
3. Dynamic routing

What it *didn't* give us was:
1. **Self-modifying topology** — the routing function and expert structure are fixed after training
2. **Inter-expert communication** — experts can't talk to each other during computation
3. **Recursive depth** — the number of "hops" through experts is always 1

These three missing ingredients correspond exactly to three innovations of the Worlmesh:
1. The topology evolves *during inference* (not just training)
2. Nodes communicate laterally through self-organizing attention
3. The computation can be recursive — routing through multiple layers of experts in a single "step"

As we'll see in Lectures 05 and 06, adding these three capabilities to MoE doesn't just improve it — it transforms it into something qualitatively different. Something that can be called, without exaggeration, a different form of computation.

---

## Discussion Questions

1. Expert specialization in MoE is emergent — no one tells expert 3 to specialize in verbs. What does this emergence tell us about the nature of specialization in large networks? Is all specialization emergent, or can some be designed?
2. At planetary scale, MoE routing becomes a distributed systems problem. Is there a principled way to unify the optimization of routing quality and routing efficiency (latency, bandwidth)?
3. The Worlmesh replaces fixed experts with self-organizing nodes. How does a network "decide" how many nodes to create? What are the failure modes?
4. Hash routing achieves surprisingly good results despite having no learned routing. What does this imply about how much of MoE's benefit comes from specialization vs. mere conditional computation?