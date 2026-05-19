# WM401 — WYRD Protocol Engineering: Advanced Implementation
## *Weaving the Final Thread* — Mastering the World Engine

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Four, Semester One

**Instructor:** Dr. Rún Freyjasdóttir, Professor of World Protocol Engineering
**Office:** Yggdrasil Lab 401 | **Hours:** Mondays 14:00–16:00

**Prerequisites:** WM301 (WYRD Architecture), WM303 (Probabilistic World Modeling), WM305 (Multi-Agent World Simulation)

---

## Course Description

The Norns sit at the Well of Urðr, weaving the threads of fate into the tapestry of what-is and what-will-be. They do not weave blindly — they calculate the tension of each thread, the pattern of each intersection, the consequences of each choice of color and direction. The WYRD Protocol is the Norns' loom made digital: a system for simulating multiple world lines, branching futures, and the retrospective editing of past states with full accountability. WM401 is the advanced implementation course where you become the loom-wright — learning to build, optimize, and verify the world engine itself, not just use it.

This course covers WYRD v4.0, the latest research version of the World Yggdrasil Reconstruction & Divergence protocol. Students implement branching world lines (multiple simultaneous timelines), probabilistic future cones (probability distributions over possible futures), retrospective world state editing (changing the past with cryptographic audit trails), and multi-world reconciliation (merging divergent world lines into coherent narratives). Special emphasis is placed on performance optimization — making the WYRD engine run in real-time with millions of entities, each with hundreds of attributes, each potentially branching into dozens of possible futures.

The course is heavily project-based. Students contribute code to the University's open-source WYRD implementation, with pull requests reviewed by the faculty and merged into the main branch. By the end of the course, each student will have implemented a significant feature of the WYRD v4.0 protocol and contributed to a codebase used by researchers worldwide.

> *"The Norns do not merely see the future — they weave it, thread by thread, choice by choice. The WYRD engineer is the Norn's apprentice, learning to weave worlds that are true enough to trust and flexible enough to explore."*

---

## Lectures

### ᚠ Lecture 1: WYRD v4.0 — The Thread Evolves

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The WYRD Protocol (World Yggdrasil Reconstruction & Divergence) was first described in Dr. Freyjasdóttir's 2039 monograph *The Memory-Bearing Machine*, where it was proposed as a unified framework for representing, simulating, and querying world states across time. Since its initial implementation in 2040, the protocol has undergone four major revisions, each expanding its capabilities while maintaining backward compatibility with existing world models.

WYRD v1.0 (2040) established the foundational abstractions: the **World State** (a structured representation of the world at a moment in time, including entities, their attributes, and their relationships), the **World Event** (a discrete change to the world state), and the **World Line** (a sequence of world states connected by events, forming a timeline). WYRD v1.0 could represent a single world line advancing through time, much like a deterministic simulation — but it could not handle uncertainty, branching, or alternative timelines.

WYRD v2.0 (2041) introduced **stochastic world events** — events with probabilistic effects. Instead of "the stock market rises 2%," a WYRD v2.0 event might be "the stock market moves with mean +0.5% and standard deviation 2.3%." This enabled WYRD to represent uncertainty about the effects of events, which is essential for realistic world modeling because real-world events do not have deterministic consequences. WYRD v2.0 also introduced **event correlation** — the ability to specify that multiple events are correlated (e.g., a geopolitical crisis and a market crash are not independent).

WYRD v3.0 (2042) introduced **multi-agent world modeling** — the ability to represent worlds populated by autonomous agents, each with their own goals, beliefs, and decision-making processes. In WYRD v3.0, agents observe the world state, form beliefs (which may be incomplete or incorrect), make decisions based on their beliefs, and act, producing world events that change the world state. This closed the loop from world state to agent action and back to world state, enabling realistic simulation of complex social, economic, and political systems.

WYRD v4.0 (2044), the version studied in this course, introduces four major innovations that collectively transform WYRD from a simulation engine into a *world computation platform*:

**Branching world lines.** Instead of a single timeline, WYRD v4.0 maintains multiple simultaneous world lines — alternative versions of history that diverge at branch points (moments where different choices or chance outcomes lead to different futures). Branching enables counterfactual reasoning ("what would have happened if...?"), scenario planning (exploring multiple possible futures), and ensemble forecasting (averaging predictions across many world lines).

**Probabilistic future cones.** When the world is at a current state and faces an uncertain future, WYRD v4.0 computes a *future cone* — a probability distribution over all possible future world states, structured as a tree of branching possibilities. Unlike simple Monte Carlo simulation, which samples future paths independently, the future cone maintains the correlations between paths, enabling queries like "what is the probability that Entity X and Entity Y both survive?" or "which scenario has the highest probability-weighted utility?"

**Retrospective world state editing.** WYRD v4.0 allows authorized users to *retroactively edit* past world states — changing what "happened" in the simulated past. Every retrospective edit is recorded in a cryptographic audit trail (Merkle tree of state hashes) that makes it impossible to tamper with history undetectably. Retrospective editing is essential for correcting world model errors (the model misclassified an entity, miscounted a quantity), incorporating newly discovered information about the past, and "what if" analysis that requires rewriting history.

**Multi-world reconciliation.** When multiple world lines have diverged, WYRD v4.0 can *reconcile* them — finding a merged world line that preserves the most important features of each branch while resolving contradictions. Reconciliation is the inverse of branching: branching splits one world into many; reconciliation merges many worlds into one. Reconciliation is used for ensemble forecasting (combining predictions from many world lines into a consensus), conflict resolution (merging world models from different stakeholders), and world model curation (maintaining a canonical world model that incorporates the best information from many sources).

These innovations are not merely theoretical — they are implemented in production code, with careful attention to performance, correctness, and usability. This course teaches you to implement these innovations yourself, contributing to the WYRD codebase and learning the craft of world engine engineering.

**The metaphor of the Norns' loom.** The Norns — Urðr (What Has Become), Verðandi (What Is Becoming), and Skuld (What Shall Be) — weave the threads of fate at the Well of Urðr. Their loom has three beams: the past (already woven), the present (under the shuttle), and the future (the unwoven threads). Skuld can see possible patterns in the unwoven threads, but she cannot know with certainty which pattern will emerge — because the weaving is influenced by the actions of gods and mortals, who have agency within the tapestry.

WYRD v4.0 is the loom of the Norns made digital. The audit trail is Urðr's beam — the irrevocable record of what has been woven. The current world state is Verðandi's shuttle — the moving point where past becomes future. The future cone is Skuld's vision — the space of possible patterns, weighted by probability, awaiting the choices that will select among them.

**Key Topics:**

- WYRD v1.0–v3.0: World States, World Events, World Lines, stochastic events, multi-agent simulation
- WYRD v4.0 innovations: branching world lines, probabilistic future cones, retrospective editing, multi-world reconciliation
- Cryptographic audit trails: Merkle trees of state hashes for tamper-evident history
- The Norns' loom metaphor: past (audit trail), present (current state), future (future cone)

**Required Reading:**

- Freyjasdóttir, R. *The Memory-Bearing Machine: Toward a Unified Framework for World Yggdrasil Reconstruction & Divergence* (2039), University of Yggdrasil Press. Chapters 18–22.
- WYRD Protocol Specification v4.0 (2044), University of Yggdrasil Technical Report WYRD-2024-01.
- University of Yggdrasil TR: "The Norns' Loom: WYRD v4.0 Design Rationale" (2043)

**Discussion Questions:**

1. Retrospective editing allows changing the simulated past. In a world model used for historical analysis, this raises ethical questions: who is authorized to change history, and under what circumstances? Should retrospective edits be reversible? Design an authorization framework for retrospective editing that balances flexibility with accountability.
2. Branching world lines enable counterfactual reasoning — "what if X had happened instead of Y?" But every branch point multiplies the number of world lines exponentially. At what point does branching become computationally prohibitive, and what strategies (pruning, merging, summarization) can keep the world tree tractable?
3. Multi-world reconciliation merges divergent world lines into a consensus. But stakeholders may disagree about which features are "most important" and how contradictions should be resolved. Is reconciliation a technical problem (finding the mathematically optimal merge) or a political one (negotiating among stakeholders)?

---

### ᚢ Lecture 2: Branching World Lines — The Many Threads of Fate

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

In the Vǫluspá, the Seeress describes a world that branches at Ragnarök: in one branch, the gods fall and the world is consumed by fire; in another, the earth rises green from the sea and a new generation of gods inherits the world. The Norse imagination contained both possibilities — not as alternatives where one was true and the other false, but as branching threads of fate, each real in its own way, the outcome not yet determined.

Branching world lines are the computational realization of this Norse intuition: the idea that history is not a single line but a tree, with branches at every point where chance or choice could have gone differently. In WYRD v4.0, a **world line** is a sequence of world states connected by events, and a **branch point** is a world state from which multiple successor world lines diverge, each representing a different outcome of the branching event.

**The world line data structure.** A world line in WYRD v4.0 is more than a linked list of states. It is a rich data structure that supports:

**Parent-child relationships.** Each world line (except the primordial line) has a parent from which it branched, and each world line may have children that branched from it. The parent-child relationships form a directed acyclic graph (DAG) — the world tree — rooted at the primordial state.

**Branch metadata.** Each branch stores metadata about why it branched: the branch point (which world state was the branching point?), the branching event (what event caused the branch?), the branching condition (what differed between branches?), and the branch probability (if the branch was probabilistic, what probability was assigned to this outcome?).

**Inheritance with divergence.** Child world lines inherit the history of their parent up to the branch point. After the branch point, the child's history diverges — new events are applied to the child but not to the parent (or to siblings). WYRD v4.0 implements copy-on-write semantics: after a branch, the child initially shares all state with the parent; when the child's state is modified, only the modified portions are copied, minimizing memory usage.

**Lineage queries.** The world tree supports lineage queries: given a world line, what is its ancestry? Given two world lines, what is their most recent common ancestor (MRCA)? At what point did they diverge? These queries are essential for reconciliation (finding the common ground between divergent branches) and for understanding the structure of the world tree.

```python
# Branching world lines in WYRD v4.0
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
import uuid

@dataclass
class BranchMetadata:
    """Metadata about why a world line branched."""
    branch_point_id: str  # WorldState ID where branching occurred
    branching_event: str  # Description of the branching event
    branching_condition: str  # What differed between branches
    branch_probability: Optional[float] = None  # For probabilistic branches
    created_by: str = "system"  # Who/what created this branch
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class WorldLine:
    """A single timeline in the WYRD protocol."""
    line_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    parent_line_id: Optional[str] = None  # Parent world line (None for primordial)
    branch_metadata: Optional[BranchMetadata] = None
    states: List['WorldState'] = field(default_factory=list)
    events: List['WorldEvent'] = field(default_factory=list)
    child_line_ids: Set[str] = field(default_factory=set)
    is_active: bool = True  # False if line has been terminated/pruned
    tags: Dict[str, str] = field(default_factory=dict)  # User-defined metadata

    def branch(self, name: str, condition: str,
               probability: Optional[float] = None) -> 'WorldLine':
        """Create a new world line branching from the current state."""
        child = WorldLine(
            name=name,
            parent_line_id=self.line_id,
            branch_metadata=BranchMetadata(
                branch_point_id=self.current_state.state_id,
                branching_event=f"Manual branch: {condition}",
                branching_condition=condition,
                branch_probability=probability,
            ),
            states=[self.current_state],  # Inherit current state
            events=list(self.events),  # Inherit event history
        )
        self.child_line_ids.add(child.line_id)
        return child

    @property
    def current_state(self) -> 'WorldState':
        return self.states[-1] if self.states else None

    def advance(self, event: 'WorldEvent') -> 'WorldState':
        """Apply an event to advance this world line."""
        new_state = self.current_state.apply(event)
        self.states.append(new_state)
        self.events.append(event)
        return new_state


class WorldTree:
    """Manages the tree of branching world lines."""
    
    def __init__(self):
        self.lines: Dict[str, WorldLine] = {}
        self.primordial_id: Optional[str] = None
    
    def create_primordial(self, initial_state: 'WorldState') -> WorldLine:
        """Create the primordial world line — the root of the tree."""
        line = WorldLine(name="primordial", states=[initial_state])
        self.lines[line.line_id] = line
        self.primordial_id = line.line_id
        return line
    
    def get_lineage(self, line_id: str) -> List[WorldLine]:
        """Get the ancestry of a world line (root to leaf)."""
        lineage = []
        current = self.lines.get(line_id)
        while current:
            lineage.append(current)
            current = self.lines.get(current.parent_line_id) if current.parent_line_id else None
        return list(reversed(lineage))
    
    def most_recent_common_ancestor(self, line_a: str, line_b: str) -> Optional[WorldLine]:
        """Find the most recent common ancestor of two world lines."""
        ancestors_a = {l.line_id: l for l in self.get_lineage(line_a)}
        for ancestor in self.get_lineage(line_b):
            if ancestor.line_id in ancestors_a:
                return ancestor
        return None
    
    def prune(self, line_id: str, reason: str = "pruned"):
        """Deactivate a world line (soft delete)."""
        line = self.lines.get(line_id)
        if line:
            line.is_active = False
            line.tags["prune_reason"] = reason
```

**Branching strategies.** Not all branch points are equal. WYRD v4.0 supports several branching strategies:

**Choice branches.** The user creates a branch to explore a specific counterfactual: "what if the Federal Reserve had raised interest rates in March 2043?" The user specifies the branching condition explicitly, and the branch represents that specific alternative.

**Probability branches.** The system automatically branches at stochastic events, creating one child world line for each possible outcome weighted by its probability. A stochastic event with three possible outcomes (60%, 30%, 10%) generates three child branches with those probabilities.

**Parameter sweep branches.** For scenario planning, the system systematically varies a parameter across a range and creates a branch for each value. "Vary the carbon tax rate from $0 to $200/ton in increments of $25" creates 9 branches, each with a different tax rate.

**Adversarial branches.** The system creates branches designed to stress-test a policy or prediction — the "worst-case" branch (all stochastic events resolve unfavorably), the "best-case" branch, and adversarial branches that explore edge cases.

**The exponential challenge.** Branching is powerful but expensive. Each branch at a level of the tree doubles (or multiplies) the number of world lines. If every time step has a branch, after N time steps the world tree has 2^N leaves — exponential growth that quickly exceeds any computational budget. Taming the exponential requires:

**Pruning.** Deactivating world lines that are no longer interesting or relevant. Pruning criteria include: low probability (branches with probability below a threshold), low utility (branches that differ minimally from the parent), and user-specified relevance (the user flags certain branches as "explored" and no longer needed).

**Merging.** Reconciling multiple world lines into one, reducing the number of active lines. Merging trades information loss for computational efficiency — the merged line is an approximation of the original branches.

**Summary lines.** Instead of maintaining full state for every branch, maintain a summary (mean, variance, key features) for branches below a certain depth. The summary captures the statistical properties of the branch without the full computational cost.

**The metaphor of the Norns' threads.** At the Well of Urðr, the Norns hold many threads — not one. Some threads are bright and strong (high-probability world lines); others are faint and fragile (low-probability branches). The Norns do not weave all threads with equal attention — they focus on the threads that matter most, letting the faint threads fade. The WYRD engineer, like the Norn, must decide which branches deserve full computational attention and which can be summarized, pruned, or merged.

**Key Topics:**

- World line structure: parent-child DAG, branch metadata, copy-on-write inheritance
- Lineage queries: ancestry, most recent common ancestor
- Branching strategies: choice, probability, parameter sweep, adversarial
- Taming the exponential: pruning, merging, summary lines
- The Norns' threads metaphor: selective attention to important branches

**Required Reading:**

- Freyjasdóttir, R. *The Memory-Bearing Machine* (2039), Chapter 19: "The World Tree."
- Lewis, D. *Counterfactuals* (1973), Harvard University Press. Chapters on possible worlds semantics.
- Pearl, J. & Mackenzie, D. *The Book of Why: The New Science of Cause and Effect* (2018), Basic Books. Chapter on counterfactuals.
- University of Yggdrasil TR: "Branching Strategies in WYRD v4.0: Design and Performance Analysis" (2044)

**Discussion Questions:**

1. Branching at every stochastic event produces exponential growth. How should the system decide which events are worth branching on and which should be handled with a single probabilistic outcome? What criteria (variance of outcomes, user interest, computational budget) should guide this decision?
2. Copy-on-write inheritance minimizes memory usage after branching, but it introduces a performance cost: the first modification to inherited state triggers a copy. In a world model with millions of entities, how should the copy-on-write mechanism be tuned to balance memory savings against copy latency?
3. Pruning deactivates world lines that are no longer interesting. But what makes a world line "interesting"? Is interestingness a property of the branch's probability, its divergence from the parent, its relevance to user questions, or something else? Who decides — the system or the user?

---

### ᚦ Lecture 3: Probabilistic Future Cones — Skuld's Vision

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

Skuld, the youngest Norn, is the weaver of *what shall be*. She does not see a single future — she sees the *cone* of possible futures, a branching tree of possibilities weighted by probability, narrowing and widening as events unfold and choices are made. Her vision is not prophecy in the sense of fixed, certain knowledge; it is probability in the sense of structured uncertainty — knowing what is likely, what is unlikely, and how the probabilities shift as each thread is woven into the tapestry.

The probabilistic future cone is WYRD v4.0's implementation of Skuld's vision. It is a probability distribution over future world states, structured as a tree of branching possibilities, where each node represents a world state at a future time and each edge represents a possible transition with an associated probability.

**From Monte Carlo to future cones.** Classical approaches to probabilistic forecasting use Monte Carlo simulation: sample N possible future paths by repeatedly running the simulation with different random seeds, then aggregate the results statistically. Monte Carlo is simple and parallelizable, but it has limitations:

**Sparse coverage.** Monte Carlo samples paths independently. If there are 10^6 possible futures, and you sample 10^4, you see only 1% of the space. The samples you see may miss important but low-probability events (black swans).

**Correlation blindness.** Monte Carlo treats each sample independently, making it hard to answer questions about correlations across futures: "what fraction of futures where X happens also have Y happen?" requires counting co-occurrences across samples, which is noisy for rare events.

**Path discontinuity.** Monte Carlo samples are discrete — they jump from one sampled path to another without a smooth representation of the space between paths. This makes it hard to reason about *nearby* futures — futures that are similar to a sampled path but not identical.

The future cone addresses these limitations by maintaining the full structure of branching possibilities rather than sampling from it. Instead of generating N independent futures, the future cone generates a tree where each node branches into its possible successor states, with probabilities assigned to each branch. The tree is explored selectively — high-probability branches are expanded deeply; low-probability branches are pruned early — but the structure of branching is preserved, enabling queries that Monte Carlo cannot easily answer.

**Building the future cone.** The future cone is built by recursive expansion from the current world state:

1. Start at the current state S₀ at time t₀.
2. Identify all possible events that could occur at S₀ and their probabilities.
3. For each event with probability p > threshold, create a child state S₁ = S₀.apply(event) with probability p.
4. Recurse for each child, expanding the tree to the desired depth (time horizon).
5. Prune branches where the cumulative probability (product of branch probabilities along the path) falls below a threshold.
6. Optionally, merge similar states to reduce the tree's size while preserving statistical properties.

The result is a tree where each leaf represents a possible future world state at time t_horizon, and the probability of reaching that leaf is the product of the probabilities along the path from root to leaf. The sum of probabilities across all leaves is approximately 1.0 (some probability is lost to pruned branches, but this is tracked as "unmodeled probability").

**Querying the future cone.** The future cone supports probabilistic queries that go beyond simple statistics:

**Marginal probability.** What is the probability that entity X has property Y at time t? Sum the probabilities of all leaves where X.Y is true.

**Conditional probability.** Given that event A occurs at time t₁, what is the probability that event B occurs at time t₂? Sum the probabilities of leaves where B occurs, divided by the probability of A.

**Expected value.** What is the expected value of function f(world state) at time t? Sum over leaves: Σ p(leaf) × f(leaf.state).

**Value at Risk (VaR).** What is the worst outcome in the 5th percentile? Rank leaves by f(state), find the leaf at the 5th percentile, return its f-value.

**Path probability.** What is the most likely path to reach state S? Starting from S, trace backward through the tree, selecting at each node the parent with the highest probability edge. This reconstructs the maximum-likelihood path to S.

**Sensitivity analysis.** How does the probability of outcome O change if we vary parameter P? Compare future cones generated with different values of P.

```python
# Probabilistic future cone in WYRD v4.0
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
import heapq

@dataclass
class FutureNode:
    """A node in the future cone tree."""
    state_id: str
    time: float  # Simulation time
    cumulative_probability: float  # Probability of reaching this node
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)  # Child node IDs
    state_summary: dict = field(default_factory=dict)  # Key state variables

@dataclass
class FutureLeaf:
    """A leaf of the future cone (terminal state at time horizon)."""
    node_id: str
    path_probability: float
    state: 'WorldState'

class FutureCone:
    """The probabilistic future cone — Skuld's Vision."""
    
    def __init__(self, world_model, max_depth: int = 10,
                 min_probability: float = 0.001):
        self.model = world_model
        self.max_depth = max_depth
        self.min_probability = min_probability
        self.nodes: Dict[str, FutureNode] = {}
        self.leaves: List[FutureLeaf] = []
    
    def build(self, initial_state: 'WorldState',
              time_horizon: float) -> None:
        """Build the future cone from initial_state to time_horizon."""
        root = FutureNode(
            state_id=initial_state.state_id,
            time=initial_state.time,
            cumulative_probability=1.0,
        )
        self.nodes[root.state_id] = root
        self._expand(root, time_horizon, depth=0)
    
    def _expand(self, node: FutureNode, horizon: float, depth: int):
        """Recursively expand a node into its possible futures."""
        if node.time >= horizon or depth >= self.max_depth:
            # Terminal node — add to leaves
            self.leaves.append(FutureLeaf(
                node_id=node.state_id,
                path_probability=node.cumulative_probability,
                state=self.model.get_state(node.state_id),
            ))
            return
        
        if node.cumulative_probability < self.min_probability:
            # Prune — probability too low
            self.leaves.append(FutureLeaf(
                node_id=node.state_id,
                path_probability=node.cumulative_probability,
                state=self.model.get_state(node.state_id),
            ))
            return
        
        # Get possible events and their probabilities
        events = self.model.get_possible_events(node.state_id)
        for event, prob in events:
            if prob < self.min_probability:
                continue
            
            new_state = self.model.apply_event(node.state_id, event)
            child = FutureNode(
                state_id=new_state.state_id,
                time=new_state.time,
                cumulative_probability=node.cumulative_probability * prob,
                parent_id=node.state_id,
            )
            self.nodes[child.state_id] = child
            node.children.append(child.state_id)
            self._expand(child, horizon, depth + 1)
    
    def query_probability(self, condition: Callable[['WorldState'], bool]) -> float:
        """What is the probability that 'condition' holds at the horizon?"""
        total = sum(
            leaf.path_probability
            for leaf in self.leaves
            if condition(leaf.state)
        )
        return total
    
    def query_expected_value(self, value_fn: Callable[['WorldState'], float]) -> float:
        """What is the expected value of value_fn at the horizon?"""
        return sum(
            leaf.path_probability * value_fn(leaf.state)
            for leaf in self.leaves
        )
    
    def query_value_at_risk(self, value_fn: Callable[['WorldState'], float],
                            percentile: float = 0.05) -> float:
        """Value at Risk: worst outcome in the bottom percentile."""
        sorted_leaves = sorted(self.leaves, key=lambda l: value_fn(l.state))
        cumulative = 0.0
        for leaf in sorted_leaves:
            cumulative += leaf.path_probability
            if cumulative >= percentile:
                return value_fn(leaf.state)
        return value_fn(sorted_leaves[-1].state)
    
    def most_likely_path(self, target_condition: Callable[['WorldState'], bool]
                         ) -> Optional[List[str]]:
        """Find the most likely path to a state satisfying target_condition."""
        matching_leaves = [l for l in self.leaves if target_condition(l.state)]
        if not matching_leaves:
            return None
        
        best_leaf = max(matching_leaves, key=lambda l: l.path_probability)
        # Trace back to root
        path = [best_leaf.node_id]
        current = self.nodes[best_leaf.node_id]
        while current.parent_id:
            path.append(current.parent_id)
            current = self.nodes[current.parent_id]
        return list(reversed(path))
```

**Performance considerations.** Future cones are computationally expensive. A world model with B branches per time step and depth D produces B^D nodes in the worst case. Practical future cones use several performance optimizations:

**Pruning.** Branches with cumulative probability below a threshold are terminated early. The threshold trades accuracy (lower threshold = more accurate) for speed (higher threshold = faster).

**State merging.** When two branches produce states that are sufficiently similar (by some similarity metric), they can be merged into a single node with combined probability. Merging trades structural accuracy for computational efficiency — the merged tree is an approximation of the true tree.

**Lazy expansion.** Instead of expanding the entire tree to the horizon, expand only the paths that are most likely or most interesting. When a query is received, expand additional paths as needed to answer the query with sufficient confidence. Lazy expansion is particularly effective for rare-event queries ("what's the probability of a catastrophic outcome?") because the tree only needs to expand paths that lead to the rare event.

**Parallel expansion.** The branches of the tree are independent — each can be expanded in parallel across multiple compute nodes. WYRD v4.0's parallel expansion framework distributes branch expansion across a compute cluster, achieving near-linear speedup for large future cones.

**The metaphor of Skuld's vision.** Skuld sees not one future but many, weighted by probability, connected by the threads of causality that run from past to future through the present moment. Her vision is not a crystal ball showing a single image — it is a map of possibility, showing the terrain of what-might-be, with peaks of high probability and valleys of low probability, with roads of choices that lead from one terrain to another. The future cone is Skuld's vision made computational: a probability distribution over futures that enables reasoning about uncertainty, risk, and opportunity.

**Key Topics:**

- Future cone vs. Monte Carlo: structural representation vs. sampling
- Building the future cone: recursive expansion with pruning and merging
- Query types: marginal probability, conditional probability, expected value, VaR, path probability, sensitivity
- Performance: pruning, state merging, lazy expansion, parallel expansion
- The Skuld's vision metaphor: structured uncertainty, peaks and valleys of probability

**Required Reading:**

- Freyjasdóttir, R. *The Memory-Bearing Machine* (2039), Chapter 20: "The Cone of Futures."
- Taleb, N. N. *The Black Swan: The Impact of the Highly Improbable* (2007), Random House.
- Pearl, J. *Probabilistic Reasoning in Intelligent Systems* (1988), Morgan Kaufmann.
- University of Yggdrasil TR: "Parallel Future Cone Expansion in WYRD v4.0" (2044)

**Discussion Questions:**

1. Pruning discards low-probability branches. But "low probability" events — black swans — can be the most consequential. How should the future cone handle the trade-off between computational efficiency (prune aggressively) and risk awareness (retain rare but catastrophic possibilities)?
2. State merging trades structural accuracy for efficiency. But what similarity metric should be used to decide when two states are "close enough" to merge? If merging conflates two states that users later want to distinguish, the merged tree is misleading. How can the system detect when merging was a mistake?
3. Lazy expansion only explores paths that are needed to answer queries. But the user's queries may be biased — they only ask about what they already suspect, missing the surprising future that the cone could reveal if fully expanded. Should the system proactively explore paths that the user has not asked about?

---

### ᚬ Lecture 4: Retrospective World State Editing — Rewriting the Past with Honor

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The Norse did not believe the past was unchangeable. The Norns wove the past as well as the present and future — and the past could be re-woven if the loom demanded it. What mattered was not that the past was fixed but that any change to the past was *known* — recorded in the memory of the gods, the songs of the skalds, the carvings on the rune-stones. To change the past in secret was dishonorable; to change it openly, with accountability, was an act of responsible stewardship of the tapestry.

Retrospective world state editing is the capability to go back and change what "happened" in a simulated world — to correct an error, incorporate new information, or explore a counterfactual — while maintaining a tamper-evident audit trail that makes every change visible and attributable. In WYRD v4.0, retrospective editing is not a bug; it is a feature, and the audit trail is its ethical foundation.

**Why retrospective editing?** World models are imperfect. They make mistakes: an entity is misclassified, a quantity is miscounted, a relationship is misidentified, an event is attributed to the wrong cause. Without retrospective editing, these errors persist forever, corrupting every downstream inference that depends on the erroneous state. With retrospective editing, the error can be corrected, and the audit trail records the correction — so downstream consumers of the world model know that the state they see has been edited, when, by whom, and for what reason.

Retrospective editing also enables legitimate counterfactual reasoning. A researcher studying the outbreak of a conflict might ask: "What if the ambassador had not been recalled on March 15, 2042?" By retroactively editing the world state to keep the ambassador in place and then re-running the simulation forward, the researcher can explore the counterfactual scenario systematically.

**The cryptographic audit trail.** The audit trail is the heart of retrospective editing. Every version of the world state is hashed, and the hashes are organized into a Merkle tree — a cryptographic data structure where each node's hash depends on its children's hashes, and the root hash depends on the entire tree. If any state in the tree is modified, the hashes along the path to the root change, making the modification detectable.

In WYRD v4.0, the audit trail has the following properties:

**Tamper evidence.** Any modification to any past state invalidates the root hash, making the modification immediately detectable. It is cryptographically infeasible to modify a past state and recompute the hashes to hide the modification without knowing a secret key.

**Edit attribution.** Every retrospective edit is recorded as an audit entry that includes: the state that was edited, the previous value, the new value, the editor's identity (cryptographically signed), the timestamp, and the reason for the edit. The audit entries are themselves hashed into the Merkle tree, making them tamper-evident as well.

**Edit justification.** Every edit must include a justification — a human-readable explanation of why the edit was made. The justification is not cryptographically enforced (a malicious editor could lie in the justification), but it is recorded for posterity, creating social accountability: an editor who makes unjustified edits will be discovered when the audit trail is reviewed.

**Edit reversibility.** Retrospective edits do not overwrite the original state; they create a new version of the state that supersedes the original. The original state is retained in the audit trail, so edits can be reviewed and, if appropriate, reversed. The edited state is annotated with "edited by X at time T for reason R," so consumers of the world model know they are looking at an edited state.

```python
# Cryptographic audit trail for retrospective editing
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import hashlib
import json
import time
from datetime import datetime

@dataclass
class AuditEntry:
    """A single entry in the audit trail."""
    entry_id: str
    state_id: str  # State being edited
    previous_value: dict  # Value before edit
    new_value: dict  # Value after edit
    editor: str  # Identity of editor
    timestamp: float = field(default_factory=time.time)
    justification: str = ""
    signature: str = ""  # Cryptographic signature of the editor

@dataclass
class MerkleNode:
    """A node in the Merkle tree of state hashes."""
    hash: str
    left_child: Optional['MerkleNode'] = None
    right_child: Optional['MerkleNode'] = None
    audit_entry: Optional[AuditEntry] = None  # For leaf nodes

class AuditTrail:
    """Cryptographic audit trail for WYRD world states."""
    
    def __init__(self):
        self.states: Dict[str, List[AuditEntry]] = {}  # State ID -> edit history
        self.merkle_root: Optional[MerkleNode] = None
        self._state_versions: Dict[str, List[dict]] = {}
    
    def record_state(self, state_id: str, state_data: dict):
        """Record a new state version."""
        if state_id not in self._state_versions:
            self._state_versions[state_id] = []
        self._state_versions[state_id].append(state_data)
        self._rebuild_merkle_tree()
    
    def edit_state(self, state_id: str, previous_value: dict,
                   new_value: dict, editor: str,
                   justification: str) -> AuditEntry:
        """Record a retrospective edit with full audit trail."""
        entry = AuditEntry(
            entry_id=hashlib.sha256(
                f"{state_id}{editor}{time.time()}".encode()
            ).hexdigest()[:16],
            state_id=state_id,
            previous_value=previous_value,
            new_value=new_value,
            editor=editor,
            justification=justification,
            signature=self._sign(editor, state_id, new_value),
        )
        
        if state_id not in self.states:
            self.states[state_id] = []
        self.states[state_id].append(entry)
        
        # Store the edited state as a new version
        self._state_versions[state_id].append(new_value)
        
        # Rebuild Merkle tree to include the edit
        self._rebuild_merkle_tree()
        
        return entry
    
    def get_current_state(self, state_id: str) -> Optional[dict]:
        """Get the most recent version of a state (including edits)."""
        versions = self._state_versions.get(state_id, [])
        return versions[-1] if versions else None
    
    def get_state_history(self, state_id: str) -> List[AuditEntry]:
        """Get the complete edit history for a state."""
        return self.states.get(state_id, [])
    
    def verify_integrity(self) -> bool:
        """Verify that the Merkle tree is internally consistent."""
        if not self.merkle_root:
            return True
        return self._verify_node(self.merkle_root)
    
    def _rebuild_merkle_tree(self):
        """Rebuild the Merkle tree from all state versions."""
        # Leaf nodes: hash of each state version
        leaves = []
        for state_id, versions in self._state_versions.items():
            for i, version in enumerate(versions):
                data = json.dumps(version, sort_keys=True)
                h = hashlib.sha256(
                    f"{state_id}:{i}:{data}".encode()
                ).hexdigest()
                leaves.append(MerkleNode(hash=h))
        
        if not leaves:
            self.merkle_root = None
            return
        
        # Build tree bottom-up
        nodes = leaves
        while len(nodes) > 1:
            next_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                combined = hashlib.sha256(
                    (left.hash + right.hash).encode()
                ).hexdigest()
                parent = MerkleNode(
                    hash=combined,
                    left_child=left,
                    right_child=right,
                )
                next_level.append(parent)
            nodes = next_level
        
        self.merkle_root = nodes[0] if nodes else None
    
    def _verify_node(self, node: MerkleNode) -> bool:
        """Recursively verify a Merkle node."""
        if not node.left_child and not node.right_child:
            return True
        expected = hashlib.sha256(
            (node.left_child.hash + node.right_child.hash).encode()
        ).hexdigest()
        if expected != node.hash:
            return False
        return (self._verify_node(node.left_child) and
                self._verify_node(node.right_child))
    
    def _sign(self, editor: str, state_id: str,
              new_value: dict) -> str:
        """Create a cryptographic signature for the edit."""
        data = f"{editor}:{state_id}:{json.dumps(new_value, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()
```

**The ethics of editing the past.** Retrospective editing is powerful and therefore dangerous. An editor could change history to make a favored policy look more successful, to hide an inconvenient fact, or to frame an adversary. The audit trail provides technical accountability (every edit is visible and attributable), but technical accountability is not enough — social and institutional accountability are also required.

WYRD v4.0's governance framework for retrospective editing includes:

**Role-based access control.** Not everyone can edit the past. Different roles have different editing privileges: administrators can edit any state, researchers can edit states within their project, and external users cannot edit at all. Privileges are granted, reviewed, and revoked through a formal process.

**Edit review.** Significant edits (those that affect downstream analyses, policies, or publications) must be reviewed by a second authorized editor before they take effect. The reviewer checks that the edit is justified, correctly implemented, and not misleading.

**Edit notification.** When a state that a user has queried or depends on is retroactively edited, the user is notified — "The world state you queried on March 15 has been edited. Click here to see the edit history." Notification prevents users from unknowingly relying on edited data.

**Edit expiration.** Edits that are no longer justified (e.g., the error they corrected has been superseded) can be flagged for review and potentially reversed, restoring the original state.

**The metaphor of the rune-stone.** Norse rune-stones were public records — erected in visible locations, carved with the names of the dead, the deeds of the living, and the lineages that connected them. A rune-stone could be recarved to correct an error, but the recarving was visible — the stone showed the marks of both the original carving and the correction. Anyone who looked at the stone could see that it had been changed, when, and (if the carver had skill) by whom. The WYRD audit trail is the digital rune-stone: a public, permanent, tamper-evident record of what was written, what was changed, and who changed it.

**Key Topics:**

- Retrospective world state editing: correcting errors, incorporating new information, counterfactual reasoning
- Cryptographic audit trail: Merkle trees, tamper evidence, edit attribution
- Edit governance: role-based access, review, notification, expiration
- The rune-stone metaphor: public, permanent, tamper-evident records

**Required Reading:**

- Freyjasdóttir, R. *The Memory-Bearing Machine* (2039), Chapter 21: "The Ethics of Rewriting."
- Merkle, R. C. "A Digital Signature Based on a Conventional Encryption Function" (1988), *CRYPTO '87*.
- Schneier, B. *Applied Cryptography* (2nd ed., 1996), Wiley. Chapters on hash functions and digital signatures.
- University of Yggdrasil TR: "The Rune-Stone Protocol: Audit Trails for World State Editing" (2043)

**Discussion Questions:**

1. Retrospective editing enables error correction, but it also enables historical revisionism. An editor could change the world state to make a political leader look more successful than they were. How should the governance framework distinguish between legitimate error correction and illegitimate revisionism?
2. The Merkle tree root hash proves that no state has been modified since the tree was built — but it doesn't prove that the original states were correct. The audit trail records edits but not mistaken initial states. How can the system distinguish between "this state was wrong initially" and "this state was edited later"?
3. Edit notification tells users when a state they depended on has been edited. But some users may not want to be notified — they trust the system to be correct and don't want to be burdened with edit notifications. Is notification an opt-in feature (users request to be notified) or an opt-out feature (users are notified by default)?

---

### ᚱ Lecture 5: Multi-World Reconciliation — Merging the Branches

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

When Óðinn hung on Yggdrasill, he looked down through the branches and saw the Nine Worlds — not as separate realms but as interconnected aspects of a single reality. Ásgarðr and Miðgarðr, Jǫtunheimr and Álfheimr, Hel and Múspellsheimr — each world had its own inhabitants, its own laws, its own truths, but all were connected through the branches of the World Tree. To understand any single world, you had to understand its relationship to all the others.

Multi-world reconciliation is the process of bringing divergent world lines back together — merging multiple alternative histories into a single coherent world line that preserves the most important features of each branch while resolving the contradictions between them. Reconciliation is the inverse of branching: branching splits one world into many; reconciliation merges many worlds into one.

**Why reconcile?** World lines diverge for good reasons — to explore counterfactuals, to represent uncertainty, to model the perspectives of different stakeholders. But at some point, the divergence must be resolved. A policy maker needs a single forecast, not a forest of possibilities. A system operator needs a single world model to base decisions on, not N competing models. A researcher needs to synthesize findings from multiple branches into a coherent conclusion. Reconciliation provides this resolution.

Reconciliation is used in several WYRD workflows:

**Ensemble reconciliation.** After running many world lines with different stochastic outcomes, reconcile them into a single representative world line that captures the consensus view while preserving information about variance and outliers.

**Stakeholder reconciliation.** Different stakeholders (government agencies, corporations, NGOs) maintain their own world models with different assumptions, priorities, and data. Reconciliation merges these models into a shared world model that all stakeholders can agree on (or at least accept as a basis for discussion).

**Temporal reconciliation.** A world model that has been branching for a long time accumulates many diverged lines. Periodically reconciling the branches keeps the world tree manageable and ensures that the canonical world line reflects the best available information.

**The reconciliation algorithm.** Reconciliation is not simple merging — it requires resolving contradictions. If branch A records "Entity X is in New York" and branch B records "Entity X is in London," the reconciled world line cannot simply take both; it must decide which is correct, or record the uncertainty, or find a higher-level description that both branches agree on (e.g., "Entity X is traveling").

WYRD v4.0's reconciliation algorithm operates in four phases:

**1. Identify the common ancestor.** The reconciliation begins at the most recent common ancestor (MRCA) of the branches being reconciled — the last state that all branches agree on. Only states after the MRCA need to be reconciled; states before the MRCA are already consistent.

**2. Align the timelines.** The branches may have different timescales (branch A advanced in hourly steps, branch B in daily steps). The reconciliation aligns the timelines to a common temporal resolution, interpolating states where necessary.

**3. Resolve contradictions.** For each entity and attribute in the world state, compare the values across branches. If all branches agree, use the agreed value. If branches disagree:

- **Majority vote (weighted).** Use the value from the branch with the highest weight (probability, credibility, recency). This is the simplest resolution but discards minority information.
- **Confidence-weighted fusion.** Compute a weighted average for continuous values or a probability distribution for discrete values. "Entity X's location is New York (confidence 0.6), London (confidence 0.3), Paris (confidence 0.1)."
- **Hierarchical abstraction.** Find a higher-level description that all branches agree on. "Entity X is in a major financial center" — New York, London, and Paris are all major financial centers.
- **Conflict flagging.** When branches cannot be reconciled (the contradiction is fundamental, not probabilistic), flag the conflict and require human resolution. The reconciled world line records the conflict rather than resolving it arbitrarily.

**4. Recompute downstream state.** After resolving contradictions at the point of divergence, recompute the world line forward from the reconciliation point to the present, applying the events from the reconciled branches (with appropriate adjustments for the resolved values).

```python
# Multi-world reconciliation
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

class ResolutionStrategy(Enum):
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    HIERARCHICAL_ABSTRACTION = "hierarchical_abstraction"
    FLAG_CONFLICT = "flag_conflict"

@dataclass
class ReconciliationResult:
    reconciled_state: 'WorldState'
    resolutions: List[dict]  # How each contradiction was resolved
    conflicts: List[dict]  # Contradictions that could not be resolved
    confidence: float  # Overall confidence in the reconciliation

class WorldReconciler:
    """Reconciles multiple divergent world lines into one."""
    
    def __init__(self, ontology, resolution_policy):
        self.ontology = ontology  # Entity and attribute hierarchy
        self.policy = resolution_policy
    
    def reconcile(self, branches: List[WorldLine],
                  weights: List[float]) -> ReconciliationResult:
        """Reconcile multiple world lines."""
        assert len(branches) == len(weights)
        
        # 1. Find most recent common ancestor
        mrca = self._find_mrca(branches)
        
        # 2. Get the state of each branch at the reconciliation point
        branch_states = [b.current_state for b in branches]
        
        # 3. Resolve contradictions for each entity-attribute
        resolutions = []
        conflicts = []
        reconciled_attributes = {}
        
        all_entities = self._collect_entities(branch_states)
        for entity_id, attribute in all_entities:
            values = [
                self._get_attribute(state, entity_id, attribute)
                for state in branch_states
            ]
            
            if self._all_equal(values):
                reconciled_attributes[(entity_id, attribute)] = values[0]
            else:
                resolution = self._resolve_contradiction(
                    entity_id, attribute, values, weights
                )
                if resolution.resolved:
                    reconciled_attributes[(entity_id, attribute)] = resolution.value
                    resolutions.append(resolution.metadata)
                else:
                    conflicts.append(resolution.metadata)
        
        # 4. Build reconciled state
        reconciled = WorldState(
            attributes=reconciled_attributes,
            parent_state=mrca,
        )
        
        # 5. Recompute forward from reconciliation point
        reconciled = self._recompute_forward(reconciled, branches)
        
        confidence = 1.0 - (len(conflicts) / max(len(resolutions) + len(conflicts), 1))
        
        return ReconciliationResult(
            reconciled_state=reconciled,
            resolutions=resolutions,
            conflicts=conflicts,
            confidence=confidence,
        )
    
    def _resolve_contradiction(self, entity_id: str, attribute: str,
                               values: List[Any], weights: List[float]
                               ) -> 'Resolution':
        """Resolve a contradiction between branches."""
        strategy = self.policy.get_strategy(entity_id, attribute)
        
        if strategy == ResolutionStrategy.MAJORITY_VOTE:
            # Weighted majority vote
            value_votes: Dict[Any, float] = {}
            for value, weight in zip(values, weights):
                value_votes[value] = value_votes.get(value, 0) + weight
            winner = max(value_votes, key=value_votes.get)
            return Resolution(resolved=True, value=winner,
                metadata={"strategy": "majority_vote", "votes": value_votes})
        
        elif strategy == ResolutionStrategy.CONFIDENCE_WEIGHTED:
            if all(isinstance(v, (int, float)) for v in values):
                # Continuous value: weighted average
                weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)
                return Resolution(resolved=True, value=weighted_avg,
                    metadata={"strategy": "confidence_weighted", "values": values})
            else:
                # Discrete value: probability distribution
                dist = {}
                for v, w in zip(values, weights):
                    dist[str(v)] = dist.get(str(v), 0) + w / sum(weights)
                return Resolution(resolved=True, value=dist,
                    metadata={"strategy": "confidence_weighted", "distribution": dist})
        
        elif strategy == ResolutionStrategy.HIERARCHICAL_ABSTRACTION:
            # Find a common ancestor in the ontology
            common_ancestor = self.ontology.find_common_ancestor(values)
            if common_ancestor:
                return Resolution(resolved=True, value=common_ancestor,
                    metadata={"strategy": "hierarchical", "values": values})
        
        # Default: flag conflict
        return Resolution(resolved=False, value=None,
            metadata={"strategy": "flag_conflict", "values": values,
                      "entity": entity_id, "attribute": attribute})
```

**The limits of reconciliation.** Not all branches can be reconciled. Some contradictions are fundamental — they reflect genuine disagreements about the nature of reality that cannot be resolved by algorithm. In these cases, WYRD records the contradiction in the reconciled world line rather than resolving it: "Entity X is recorded as being in New York (per Branch A) and in London (per Branch B). The contradiction has not been resolved."

Contradictions that cannot be algorithmically resolved must be escalated to humans. The WYRD conflict resolution interface presents the contradictory values, their provenance (which branch produced which value), the available resolution strategies, and a recommendation — and asks a human to make the final decision. The human's decision is recorded as an audit entry, just like any other state edit.

**The metaphor of Yggdrasill's branches.** The Nine Worlds are not separate universes — they are branches of a single tree, connected through the trunk, sharing the same roots, nourished by the same wells. To understand any world, you must understand its connection to all the others. Reconciliation is the process of seeing the tree rather than the individual branches — recognizing that the branches are expressions of a single underlying reality, and that contradictions between branches can be resolved by understanding the deeper structure that connects them.

**Key Topics:**

- Reconciliation use cases: ensemble, stakeholder, temporal
- The reconciliation algorithm: common ancestor, timeline alignment, contradiction resolution, recomputation
- Resolution strategies: majority vote, confidence-weighted fusion, hierarchical abstraction, conflict flagging
- Human-in-the-loop: escalating unresolvable contradictions
- The Yggdrasill's branches metaphor: seeing the tree, not just the branches

**Required Reading:**

- Freyjasdóttir, R. *The Memory-Bearing Machine* (2039), Chapter 22: "The Reconciliation."
- Tichy, W. F. "RCS — A System for Version Control" (1985), *Software: Practice and Experience*, 15(7). (Foundational work on version control, conceptually similar to world line reconciliation.)
- University of Yggdrasil TR: "Reconciliation Strategies in WYRD v4.0: Theory and Practice" (2044)

**Discussion Questions:**

1. Hierarchical abstraction resolves contradictions by finding a common ancestor in the ontology. But this can conceal important differences — "Entity X is a mammal" is a true abstraction of both "Entity X is a dog" and "Entity X is a wolf," but the difference between dog and wolf may be crucial in some contexts. How should the reconciliation algorithm decide when abstraction is appropriate and when it is misleading?
2. Conflict flagging preserves contradictions rather than resolving them. But a world model littered with flagged conflicts becomes unusable — every query returns "it depends." How many unresolved conflicts can a world model tolerate before it ceases to be useful? What is the right balance between resolution (clean but potentially wrong) and flagging (accurate but cluttered)?
3. Human resolution of contradictions is expensive and slow. Under what circumstances should the system resolve contradictions automatically (accepting the risk of error), and under what circumstances should it escalate to humans (accepting the cost of delay)?

---

### ᚴ Lecture 6: Performance Optimization — The Swift Shuttle of the Loom

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The Norns weave at cosmic speed — threads fly across the loom faster than the eye can follow, patterns emerge and transform in moments that span the lifetimes of worlds. The loom of fate cannot be slow. If the Norns hesitated, if the shuttle paused, reality itself would stutter. Speed is not a luxury in world computation — it is a necessity. A world model that cannot keep up with the pace of events in the real world is not a model; it is a historical archive.

Performance optimization is the craft of making the WYRD engine fast enough to keep pace with reality. When the world model must track millions of entities, each with hundreds of attributes, each potentially branching into dozens of possible futures, the computational demands are enormous. A single time step — advancing the world from t to t+1 — may require millions of entity updates, each of which may involve complex computations (physics simulations, agent decision-making, relationship updates). Without optimization, a single time step could take hours, making the world model useless for real-time applications.

**The performance hierarchy.** Performance optimization in WYRD operates at multiple levels:

**Algorithmic optimization (O-notation).** Choosing algorithms with better worst-case or average-case complexity. Replacing O(n²) entity interaction computations with O(n log n) spatial indexing (octrees, R-trees). Replacing O(d) depth-first tree traversal with O(1) hash-based state lookup. Algorithmic optimization provides the largest gains for the smallest investment of engineering effort.

**Data structure optimization (cache efficiency).** Organizing data in memory to maximize cache hits and minimize cache misses. Modern CPUs can perform ~10^10 operations per second — but only if the data is in L1 cache. A cache miss to main memory costs ~100 CPU cycles; a cache miss to disk costs ~10^7 cycles. Data structure optimization ensures that the world state data that is accessed together is stored together, minimizing cache misses.

**Parallelization (multi-core and distributed).** Exploiting the independence of entities and branches to parallelize computation across multiple CPU cores (shared memory) or multiple machines (distributed memory). WYRD v4.0 uses a task-based parallelism model: the work of advancing the world is decomposed into tasks (update entity X, apply event Y, evaluate branch Z), and a scheduler assigns tasks to available workers. Tasks that touch the same data are serialized; tasks that touch disjoint data run in parallel.

**Incremental computation (delta updates).** Instead of recomputing the entire world state from scratch at each time step, compute only what has changed. Most entities do not change in most time steps — the tree in the forest, the stone on the mountain, the star in the sky. Incremental computation tracks which entities are "dirty" (their state depends on something that changed) and only updates dirty entities.

**Lazy evaluation (compute on demand).** Instead of eagerly computing every entity's state at every time step, compute entity states only when they are queried. If no user asks about the weather in Novgorod, the weather in Novgorod is not computed — it waits, lazily, until someone asks. Lazy evaluation defers computation to the moment of query, trading query-time latency for background throughput.

**Compression (space-time tradeoff).** Compressing world state data to reduce memory usage and I/O bandwidth. WYRD v4.0 uses several compression techniques: delta encoding (store the difference from the previous state, not the full state), dictionary encoding (replace repeated strings with integer IDs), and run-length encoding (compress sequences of identical values). Compression trades CPU time (decompressing) for memory and I/O savings.

```python
# Incremental computation and lazy evaluation in WYRD
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set
import threading

@dataclass
class Entity:
    entity_id: str
    attributes: Dict[str, Any]
    dirty: bool = False  # Needs recomputation?
    computed: bool = False  # Has been computed?
    dependencies: Set[str] = field(default_factory=set)  # Entities this one depends on
    dependents: Set[str] = field(default_factory=set)  # Entities that depend on this one

class IncrementalWorldEngine:
    """World engine with incremental computation and lazy evaluation."""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.compute_graph: Dict[str, Callable] = {}  # entity_id -> compute function
        self._lock = threading.Lock()
    
    def add_entity(self, entity: Entity, compute_fn: Callable[[], dict]):
        """Register an entity with its computation function."""
        self.entities[entity.entity_id] = entity
        self.compute_graph[entity.entity_id] = compute_fn
    
    def mark_dirty(self, entity_id: str):
        """Mark an entity and all its dependents as dirty."""
        with self._lock:
            entity = self.entities.get(entity_id)
            if not entity or entity.dirty:
                return
            entity.dirty = True
            entity.computed = False
            for dependent_id in entity.dependents:
                self.mark_dirty(dependent_id)
    
    def get(self, entity_id: str, attribute: str) -> Any:
        """Get an entity's attribute, computing lazily if needed."""
        entity = self.entities.get(entity_id)
        if not entity:
            return None
        
        if not entity.computed:
            self._compute(entity_id)
        
        return entity.attributes.get(attribute)
    
    def _compute(self, entity_id: str):
        """Compute an entity's state, recursively computing dependencies."""
        entity = self.entities[entity_id]
        
        # Compute dependencies first
        for dep_id in entity.dependencies:
            dep = self.entities.get(dep_id)
            if dep and not dep.computed:
                self._compute(dep_id)
        
        # Compute this entity
        compute_fn = self.compute_graph.get(entity_id)
        if compute_fn:
            new_attrs = compute_fn()
            entity.attributes.update(new_attrs)
        
        entity.dirty = False
        entity.computed = True
    
    def advance_time(self, events: Dict[str, Any]):
        """Advance the world by one time step, processing events."""
        # Events mark entities dirty
        for entity_id, event in events.items():
            entity = self.entities.get(entity_id)
            if entity:
                entity.attributes['_pending_event'] = event
                self.mark_dirty(entity_id)
        
        # Lazy evaluation: no bulk compute, entities compute on demand
        # But we might pre-compute frequently queried entities
        for entity_id in self._frequently_queried():
            if not self.entities[entity_id].computed:
                self._compute(entity_id)
    
    def _frequently_queried(self) -> Set[str]:
        """Identify entities that are queried frequently."""
        # In practice, this would use access statistics
        return set()
```

**Profiling and measurement.** Optimization without measurement is guesswork. WYRD v4.0 includes a comprehensive profiling framework that measures:

**Time per component.** How much time is spent in each phase of the world advance: event processing, entity updates, branch expansion, state persistence, and query evaluation.

**Memory allocation.** How much memory is allocated by each component, and where the memory is spent: entity data, world line history, future cone nodes, audit trail entries.

**Cache behavior.** Cache hit rates for each major data structure, identifying data structures that are too large for cache or accessed with poor locality.

**Bottleneck identification.** The profiler automatically identifies bottlenecks — components where optimization would yield the largest overall improvement — using Amdahl's Law: the maximum speedup from optimizing a component is limited by the fraction of time spent in that component. Optimizing a component that takes 5% of total time can yield at most a 5% improvement; optimizing a component that takes 80% of total time can yield up to 5x speedup.

**The metaphor of the swift shuttle.** The shuttle of a loom flies back and forth, carrying the weft thread through the warp, hundreds of times per minute. If the shuttle were slow, the weaving would take forever; the speed of the shuttle determines the speed of the entire loom. Performance optimization is the craft of making the shuttle swift — finding and eliminating the friction that slows the world engine. A well-optimized WYRD engine can advance a million-entity world in milliseconds, matching the speed of the Norns' own shuttle.

**Key Topics:**

- The performance hierarchy: algorithmic, data structure, parallelization, incremental, lazy, compression
- Incremental computation: dirty tracking, dependency graphs, recompute-only-what-changed
- Lazy evaluation: compute on demand, defer to query time
- Profiling: time per component, memory, cache behavior, bottleneck identification
- The swift shuttle metaphor: speed as necessity, not luxury

**Required Reading:**

- Hennessy, J. L. & Patterson, D. A. *Computer Architecture: A Quantitative Approach* (6th ed., 2017), Morgan Kaufmann. Chapters on memory hierarchy and parallelism.
- Bryant, R. E. & O'Hallaron, D. R. *Computer Systems: A Programmer's Perspective* (3rd ed., 2015), Pearson. Chapters on optimization.
- University of Yggdrasil TR: "WYRD Performance Profiling and Optimization Guide" (2044)

**Discussion Questions:**

1. Lazy evaluation defers computation to query time. But if a user queries an entity that has not been computed in 100 time steps, re-computing it from scratch may be more expensive than eager computation would have been. How should the system decide which entities to compute eagerly and which to defer?
2. Incremental computation tracks dependencies between entities. But dependency tracking itself has a cost — every time entity A changes, the system must check whether entity B (which depends on A) needs recomputation. At what density of dependencies does the overhead of tracking exceed the savings from incremental computation?
3. Parallelization exploits independence between entities. But entities are often interdependent — entity A's state depends on entity B's state. How fine-grained should the parallelism be? Fine-grained (entity-level) maximizes parallelism but increases synchronization overhead; coarse-grained (branch-level) minimizes synchronization but may leave cores idle.

---

### ᚼ Lecture 7: Consistency and Coherence — The Integrity of the Tapestry

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

A tapestry with a broken thread is not a tapestry — it is a collection of unrelated threads pretending to be a whole. The integrity of the tapestry depends on every thread being in its proper place, properly tensioned, properly connected to its neighbors. One loose thread can unravel the entire design.

Consistency and coherence are the properties that ensure the world model is not just a collection of data points but a unified, internally coherent representation of reality. A world model that records "Entity X is in New York" and "Entity X is in London" for the same time is inconsistent — it asserts two contradictory facts. A world model that records "Entity X is in New York" at time t but has no record of how Entity X got there is incoherent — it lacks the causal chain that connects states across time.

**Types of consistency in world models:**

**Entity consistency.** Every entity has exactly one value for each attribute at each point in time. No contradictory values (X is both alive and dead at the same time). No missing values for required attributes (an entity with no location is a ghost). Entity consistency is enforced by the world state data model: each entity's state is a single, authoritative dictionary of attribute-value pairs for each time point.

**Temporal consistency.** The world state at time t+1 must be reachable from the world state at time t by applying the events that occurred between t and t+1. There must be no gaps in the timeline (states at t and t+2 with no state at t+1), no time travel (t+1 occurring before t), and no contradictions between consecutive states (X was in New York at t and in London at t+1, but no travel event is recorded).

**Causal consistency.** Events must have effects that are causally plausible given the world model's rules. If event E causes entity X to move from New York to London, X's state at the next time step must reflect that movement. Causal consistency is enforced by the world model's physics and logic rules — the functions that define how events affect state.

**Cross-entity consistency.** Relationships between entities must be symmetric and complete. If entity A is the parent of entity B, then entity B must be the child of entity A. If entity A is located in entity B (a containment relationship), then entity B must contain entity A. Cross-entity consistency is the hardest to maintain because it requires checking relationships across the entire entity population after every time step.

**Branch consistency.** When world lines branch, the branches must be consistent with their parent up to the branch point, and divergent after the branch point. A branch cannot contain events before the branch point that the parent does not — that would violate the definition of branching (the child inherits the parent's history).

**Coherence beyond consistency.** Consistency is the floor — the minimum requirement for a world model to be logically sound. Coherence is the ceiling — the property that the world model tells a coherent story, that the events and states connect into a narrative that makes sense. A world model can be perfectly consistent (no contradictions) but completely incoherent (the events don't add up to a plausible story).

Coherence is harder to enforce than consistency because it requires judgment. Does it make sense for Entity X to move from New York to London to Tokyo to New York in three consecutive time steps? The data is consistent (each move is recorded, no contradictions), but the narrative is incoherent (why would anyone do that?). Coherence checking in WYRD v4.0 uses rule-based anomaly detection (flag statistically improbable sequences of events) and LLM-based plausibility evaluation (ask an LLM: "Does this sequence of events make sense? Why or why not?").

**Consistency enforcement mechanisms.** WYRD v4.0 enforces consistency through multiple mechanisms:

**Schema constraints.** The world state schema defines required attributes, valid value ranges, and integrity constraints. Every state update is validated against the schema before it is applied. Schema constraints catch basic errors (missing required field, value out of range) before they corrupt the world model.

**Transaction semantics.** World state updates are applied as transactions — all-or-nothing operations that either succeed completely or fail completely, with no partial updates visible to other processes. Transactions prevent the world model from being observed in an inconsistent intermediate state.

**Event validation.** Every event is validated before it is applied: does the event reference entities that exist? Are the event's parameters within valid ranges? Does the event violate any invariants? Event validation catches errors before they corrupt the world state.

**Post-update integrity checking.** After each time step (or batch of updates), the system runs integrity checks: entity consistency (no duplicate or contradictory values), temporal consistency (timeline without gaps), cross-entity consistency (symmetric relationships). Integrity checks are expensive (they scan the entire entity population) and are typically run asynchronously, flagging inconsistencies for later correction rather than blocking the world advance.

**Inconsistency resolution.** When an inconsistency is detected, WYRD v4.0 has several options:

**Reject the offending update.** If an event would cause an inconsistency, reject it and log the rejection. This is safe but may leave the world model out of date (the event really happened in the real world; the model is now wrong).

**Flag and quarantine.** Accept the update but flag the affected entities as "inconsistent." Queries on inconsistent entities return the data with a warning: "This data may be inconsistent. Last validated at time t." Flagging preserves information while acknowledging uncertainty.

**Auto-repair.** Attempt to automatically resolve the inconsistency using heuristics. If two events claim to move Entity X to two different locations, auto-repair might choose the later event (assuming it supersedes the earlier) or the event from the more authoritative source. Auto-repair is fast but risks compounding errors.

**The metaphor of the tapestry's integrity.** A tapestry with a broken thread can be repaired — the weaver re-threads the shuttle and re-weaves the damaged section. But the repair leaves a mark: the mended section is visible to anyone who looks closely. The tapestry's integrity is preserved through constant vigilance and occasional repair. The WYRD engineer, like the tapestry's weaver, must constantly check the integrity of the world model, repairing inconsistencies when they arise, and designing the system so that inconsistencies are rare and easily repaired.

**Key Topics:**

- Types of consistency: entity, temporal, causal, cross-entity, branch
- Coherence beyond consistency: narrative plausibility, anomaly detection
- Enforcement mechanisms: schema constraints, transactions, event validation, integrity checking
- Inconsistency resolution: reject, flag, auto-repair
- The tapestry integrity metaphor: vigilance and repair

**Required Reading:**

- Vogels, W. "Eventually Consistent" (2009), *ACM Queue*, 6(6).
- Gilbert, S. & Lynch, N. "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services" (2002), *ACM SIGACT News*, 33(2).
- University of Yggdrasil TR: "Consistency and Coherence in Multi-World Simulations" (2043)

**Discussion Questions:**

1. Consistency enforcement (schema constraints, transactions, event validation) adds overhead to every state update. In a real-time world model tracking millions of entities, how should the system balance consistency enforcement (catch errors) against throughput (process updates quickly)? Is eventual consistency an acceptable compromise?
2. Coherence — narrative plausibility — requires judgment that is difficult to automate. Should WYRD rely on LLM-based plausibility evaluation, and if so, how should the LLM's judgments be validated and audited?
3. Auto-repair attempts to fix inconsistencies automatically. But auto-repair can compound errors — the system "fixes" the wrong thing and creates a cascade of further inconsistencies. Under what circumstances is auto-repair acceptable, and when should the system flag for human review instead?

---

### ᚾ Lecture 8: Parallel Evaluation — The Many Hands of the Norns

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The Norns are three, but their hands are many — or so the myths suggest. For how else could three beings weave the fates of all who live, across all the Nine Worlds, across all of time? The Norns must work in parallel — each hand working a different section of the tapestry, each mind tracking a different thread of fate, yet all coordinated so that the tapestry emerges as a unified whole.

Parallel evaluation is the technique of dividing the work of advancing the world model across multiple processing units (CPU cores, machines, clusters) to achieve speedup proportional to the number of workers. In an ideal world, N workers produce results N times faster than 1 worker. In the real world, parallel speedup is limited by: the inherently sequential fraction of the work (Amdahl's Law), the overhead of coordinating workers (synchronization, communication), and load imbalance (some workers finish early and idle while others are still busy).

**Parallelism in WYRD v4.0.** WYRD v4.0 uses three levels of parallelism:

**Entity-level parallelism.** Within a single time step, the updates to different entities are independent — updating Entity A does not affect Entity B (unless A and B are explicitly related). Entity-level parallelism distributes entity updates across worker threads, with each thread updating a subset of entities. The challenge is handling entities that *are* related: if Entity A depends on Entity B, A cannot be updated until B is updated. WYRD uses a dependency-aware scheduler that builds a directed acyclic graph (DAG) of entity dependencies and schedules updates in topological order, parallelizing updates at each level of the DAG.

**Branch-level parallelism.** Different world lines are independent after they branch — events in Branch A do not affect Branch B. Branch-level parallelism distributes world lines across workers, with each worker advancing one or more world lines independently. Branch-level parallelism is embarrassingly parallel (no coordination needed between branches) and scales nearly linearly with the number of branches.

**Time-step-level parallelism (pipelining).** While Worker 1 is advancing time step t, Worker 2 can begin preparing time step t+1 (prefetching data, computing dependency graphs, allocating memory). Pipelining overlaps the execution of successive time steps, hiding the latency of sequential dependencies behind parallel execution.

**The task scheduler.** The heart of WYRD's parallel execution is the task scheduler — a component that receives a graph of tasks (entity updates, branch expansions, integrity checks), determines which tasks can run in parallel (those with no unresolved dependencies), and assigns them to available workers. The scheduler balances two goals: maximize parallelism (keep all workers busy) and minimize overhead (don't spend more time scheduling than executing).

WYRD v4.0's task scheduler uses work stealing: each worker maintains its own queue of ready tasks. When a worker finishes its tasks and its queue is empty, it "steals" tasks from another worker's queue. Work stealing balances load dynamically — if one worker gets a set of slow tasks, other workers steal from it, ensuring that all workers stay busy.

```python
# Task-based parallel scheduler for WYRD
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Set
from collections import deque
import random

@dataclass
class Task:
    task_id: str
    dependencies: Set[str]  # Task IDs that must complete first
    function: Callable
    args: tuple = ()
    priority: float = 0.0

class WorkStealingScheduler:
    """Work-stealing task scheduler for parallel WYRD evaluation."""
    
    def __init__(self, num_workers: int = 8):
        self.num_workers = num_workers
        self.queues: List[deque] = [deque() for _ in range(num_workers)]
        self.results: Dict[str, Any] = {}
        self.completed: Set[str] = set()
        self.task_graph: Dict[str, Task] = {}
        self._lock = asyncio.Lock()
    
    def submit(self, task: Task):
        """Submit a task to the scheduler."""
        self.task_graph[task.task_id] = task
        if not task.dependencies:
            # No dependencies — ready to run immediately
            worker = random.randint(0, self.num_workers - 1)
            self.queues[worker].append(task.task_id)
    
    async def run(self) -> Dict[str, Any]:
        """Run all tasks using work-stealing."""
        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.num_workers)
        ]
        await asyncio.gather(*workers)
        return self.results
    
    async def _worker(self, worker_id: int):
        """Worker loop with work stealing."""
        while len(self.completed) < len(self.task_graph):
            task_id = self._get_task(worker_id)
            if task_id is None:
                await asyncio.sleep(0.001)  # No work, brief pause
                continue
            
            task = self.task_graph[task_id]
            
            # Ensure dependencies are met
            if not task.dependencies.issubset(self.completed):
                # Dependencies not met — put back and try another
                self.queues[worker_id].appendleft(task_id)
                continue
            
            # Execute the task
            try:
                result = task.function(*task.args)
                self.results[task_id] = result
            except Exception as e:
                self.results[task_id] = e
            
            async with self._lock:
                self.completed.add(task_id)
                
                # Check if this unblocks any dependent tasks
                for tid, t in self.task_graph.items():
                    if (tid not in self.completed and
                        task_id in t.dependencies and
                        t.dependencies.issubset(self.completed)):
                        # Newly unblocked — add to a queue
                        w = random.randint(0, self.num_workers - 1)
                        self.queues[w].append(tid)
    
    def _get_task(self, worker_id: int) -> str:
        """Get a task from the worker's queue, stealing if empty."""
        queue = self.queues[worker_id]
        if queue:
            return queue.popleft()
        
        # Work stealing: try other workers' queues
        for attempt in range(self.num_workers):
            victim = random.randint(0, self.num_workers - 1)
            if victim != worker_id and self.queues[victim]:
                # Steal from the back of the victim's queue
                return self.queues[victim].pop()
        
        return None
```

**Scaling limitations.** Parallel evaluation is not a silver bullet. Amdahl's Law states that if a fraction f of the work is inherently sequential, the maximum speedup from N workers is 1 / (f + (1-f)/N). As N → ∞, speedup → 1/f. If 10% of the work is sequential, the maximum speedup is 10x, regardless of how many workers are used. For WYRD v4.0, the inherently sequential fraction includes: the global event ordering (events must be processed in temporal order), the dependency graph construction (must know all entity dependencies before scheduling), and the integrity checking (some checks require scanning the entire entity population).

Gustafson's Law offers a more optimistic perspective: as the problem size grows, the sequential fraction typically shrinks. A world model with 1,000 entities may have 20% sequential work; a world model with 1,000,000 entities may have only 2% sequential work, because the sequential work (global ordering, dependency graph) grows slowly with problem size while the parallel work (entity updates) grows proportionally.

**The metaphor of the Norns' many hands.** The Norns work in parallel — Urðr weaving the past, Verðandi the present, Skuld the future — yet the tapestry emerges as a unified whole. Their coordination is not a technical protocol but an art — each Norn knows what the others are doing, each adjusts their weaving to complement the others, each maintains the integrity of the shared design. The WYRD parallel scheduler aspires to the same art: coordinating many workers across many tasks to produce a unified world model, with each worker contributing its part to the tapestry without disrupting the whole.

**Key Topics:**

- Levels of parallelism: entity, branch, time-step (pipelining)
- Task scheduling: dependency graphs, work stealing, load balancing
- Amdahl's Law and Gustafson's Law: theoretical limits and practical realities
- The Norns' many hands metaphor: coordinated parallel weaving

**Required Reading:**

- Herlihy, M. & Shavit, N. *The Art of Multiprocessor Programming* (2nd ed., 2020), Morgan Kaufmann.
- Blumofe, R. D. & Leiserson, C. E. "Scheduling Multithreaded Computations by Work Stealing" (1999), *JACM*, 46(5).
- University of Yggdrasil TR: "Parallel Evaluation in WYRD v4.0: Architecture and Benchmarks" (2044)

**Discussion Questions:**

1. Work stealing balances load dynamically — but it adds overhead (workers must check other queues, locks must be acquired). At what level of load imbalance does work stealing become more efficient than static partitioning (pre-assigning tasks to workers before execution)?
2. Entity-level parallelism requires building a dependency DAG to determine which entities can be updated in parallel. But the dependency DAG itself must be computed, and that computation is largely sequential. For very large worlds, does the cost of building the DAG exceed the benefit of parallel execution?
3. Pipelining overlaps the execution of successive time steps. But if time step t produces results that are needed to prepare time step t+1 (e.g., the dependency DAG for t+1 depends on the state at the end of t), pipelining is limited. How deep can the pipeline be before it stalls waiting for the previous stage?

---

### ᛁ Lecture 9: Storage and Compression — The Runes Carved in Memory

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The runes were carved in stone, wood, and bone — materials that were durable but limited. A rune-stone could hold perhaps a few hundred characters, a few dozen words, a single message preserved for centuries. The carver had to choose carefully what to record, because the medium was scarce. Every word carved was a word that could not be un-carved; every space used was space that could not be reused.

Storage and compression in WYRD face the same scarcity: the world model generates enormous amounts of data (millions of entities × hundreds of attributes × thousands of time steps × multiple world lines), and storage is finite. The WYRD engineer must decide what to store, how to store it, and when to let it go — the rune-carver's discipline applied to digital memory.

**Storage requirements.** A WYRD world model with:

- 1,000,000 entities
- 200 attributes per entity (average)
- 100 bytes per attribute (average)
- 1 time step per second (for real-time simulation)
- 86,400 time steps per day
- 10 active world lines

...would generate approximately 1 million × 200 × 100 × 86,400 × 10 = 1.7 × 10^16 bytes per day — 17 petabytes. No storage system can handle that. Compression is not optional; it is existential.

**Compression techniques in WYRD v4.0:**

**Delta encoding.** Most entity attributes do not change in most time steps. Instead of storing the full attribute value at every time step, store the *delta* — the difference from the previous time step. For attributes that rarely change, the delta is often "no change" (zero bytes). For attributes that change slowly (e.g., a moving entity's position), the delta is small (a few bytes). Delta encoding reduces storage by orders of magnitude for slowly-changing attributes.

**Dictionary encoding.** Many attribute values are repeated across entities and time steps. Instead of storing the full string "United States of America" each time, store a 2-byte integer that indexes into a dictionary. Dictionary encoding is particularly effective for categorical attributes (country, status, type) that have a small number of possible values.

**Run-length encoding (RLE).** When an attribute has the same value across many consecutive time steps (e.g., a stationary entity's location), store the value once and the run length. "Location = New York, duration = 10,000 time steps" instead of 10,000 copies of "Location = New York."

**Sparse storage.** Only store attributes that have non-default values. If 99% of entities have the default value for attribute X, storing X for every entity wastes 99% of the space. Sparse storage stores a map of (entity_id, attribute) → value for non-default values only, with a fallback to the default.

**Temporal summarization.** Old time steps (beyond a configurable retention window) are summarized rather than stored in full detail. A summarized time step stores aggregate statistics (mean, variance, histogram) for each attribute rather than individual entity values. Summarization loses detail but preserves statistical properties, enabling approximate historical queries.

**Garbage collection.** World lines that are pruned (no longer active) and time steps that exceed the retention window are candidates for garbage collection — permanent deletion. Garbage collection is the final, irreversible act of storage management: the runes are erased, and the stone is carved over with new messages.

```python
# Delta encoding and compression for WYRD world states
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import struct

@dataclass
class CompressedState:
    """Compressed representation of a world state."""
    time_step: int
    base_state_id: Optional[str] = None  # Reference state for delta
    deltas: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # entity -> {attr: delta}
    unchanged_entities: int = 0  # Count of entities with no changes
    dictionary: Dict[int, str] = field(default_factory=dict)  # Value dictionary
    stats: Dict[str, float] = field(default_factory=dict)  # Summary statistics

class WorldStateCompressor:
    """Compresses world state using delta encoding and dictionaries."""
    
    def __init__(self, dictionary_threshold: int = 3):
        self.threshold = dictionary_threshold
        self._value_dictionary: Dict[str, int] = {}  # value -> id
        self._next_dict_id = 0
    
    def compress(self, current: 'WorldState',
                 previous: Optional['WorldState'] = None
                 ) -> CompressedState:
        """Compress a world state relative to a previous state."""
        compressed = CompressedState(
            time_step=current.time_step,
            base_state_id=previous.state_id if previous else None,
        )
        
        unchanged = 0
        for entity_id, attrs in current.entities.items():
            prev_attrs = previous.entities.get(entity_id, {}) if previous else {}
            
            entity_deltas = {}
            for attr, value in attrs.items():
                prev_value = prev_attrs.get(attr)
                
                if value == prev_value:
                    unchanged += 1
                    continue
                
                # Delta encoding: store the new value
                # Dictionary-encode string values
                if isinstance(value, str) and len(value) > self.threshold:
                    if value not in self._value_dictionary:
                        self._value_dictionary[value] = self._next_dict_id
                        compressed.dictionary[self._next_dict_id] = value
                        self._next_dict_id += 1
                    entity_deltas[attr] = ("dict", self._value_dictionary[value])
                else:
                    entity_deltas[attr] = value
            
            if entity_deltas:
                compressed.deltas[entity_id] = entity_deltas
        
        compressed.unchanged_entities = unchanged
        
        # Compute summary statistics
        compressed.stats = self._compute_stats(current)
        
        return compressed
    
    def decompress(self, compressed: CompressedState,
                   base_state: Optional['WorldState'] = None
                   ) -> 'WorldState':
        """Decompress a compressed state."""
        entities = {}
        
        # Start from base state if available
        if base_state:
            for entity_id, attrs in base_state.entities.items():
                entities[entity_id] = dict(attrs)
        
        # Apply deltas
        for entity_id, entity_deltas in compressed.deltas.items():
            if entity_id not in entities:
                entities[entity_id] = {}
            for attr, delta_value in entity_deltas.items():
                if isinstance(delta_value, tuple) and delta_value[0] == "dict":
                    # Dictionary decode
                    dict_id = delta_value[1]
                    entities[entity_id][attr] = compressed.dictionary[dict_id]
                else:
                    entities[entity_id][attr] = delta_value
        
        return WorldState(
            time_step=compressed.time_step,
            entities=entities,
        )
    
    def _compute_stats(self, state: 'WorldState') -> Dict[str, float]:
        """Compute summary statistics for a world state."""
        entity_count = len(state.entities)
        attr_count = sum(len(attrs) for attrs in state.entities.values())
        return {
            "entity_count": entity_count,
            "attribute_count": attr_count,
            "avg_attrs_per_entity": attr_count / max(entity_count, 1),
        }
```

**The retention policy.** How long should world states be stored? Forever is ideal (complete historical record) but impractical (storage costs). The retention policy defines:

**Hot storage (last 7 days).** Full detail, all entities, all attributes, all time steps. Queries return exact results with no latency penalty.

**Warm storage (7–90 days).** Delta-compressed, with temporal summarization for low-importance entities. Queries return exact results for important entities, approximate results for others.

**Cold storage (90 days – 2 years).** Summarized: statistical aggregates, key events, audit trail entries. Queries return approximate results only.

**Archive (2+ years).** Metadata only: what time periods are covered, what major events occurred, what the data quality metrics were. The raw data is deleted; the archive provides a map of what was once stored.

**The metaphor of the rune-carver's choice.** The rune-carver faced a choice with every stone: what to record, what to omit. The message that made it onto the stone was the one deemed most important — the name of the fallen warrior, the lineage of the chieftain, the dedication of the bridge. Everything else was lost to time. The WYRD engineer faces the same choice with every storage decision: what to keep, what to compress, what to delete. The runes carved in digital memory are the ones the engineer deemed worth preserving — and every deletion is a story that will never be told.

**Key Topics:**

- Compression techniques: delta encoding, dictionary encoding, RLE, sparse storage, temporal summarization
- Storage tiers: hot, warm, cold, archive
- Retention policies: balancing completeness against cost
- The rune-carver's choice metaphor: what to keep, what to let go

**Required Reading:**

- Salomon, D. & Motta, G. *Handbook of Data Compression* (5th ed., 2010), Springer.
- Amazon Web Services. "Storage Classes and Data Lifecycle Management" (2039)
- University of Yggdrasil TR: "WYRD Storage Architecture and Compression Benchmarks" (2044)

**Discussion Questions:**

1. Temporal summarization replaces detailed data with statistical aggregates. For historians and auditors who need exact data, summarization is information loss. For query performance and cost, summarization is essential. What is the right balance, and who decides — the engineers, the users, or the data subjects?
2. Garbage collection deletes data permanently. Once a world state is deleted, it cannot be recovered. Should WYRD require a "cooling-off period" before permanent deletion — a window during which deletion can be reversed? If so, how long?
3. Dictionary encoding is efficient for repeated values but breaks when the dictionary becomes too large (more dictionary entries than original values). How should the compressor detect when the dictionary has outlived its usefulness and switch to direct storage?

---

### ᛃ Lecture 10: Testing and Verification — Proving the Loom Works

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The Norns do not test their loom — they *know* it works. They have woven the tapestry of fate since before the beginning of time, and the tapestry has never failed. But the Norns are divine, and the WYRD engineer is mortal. For mortals, the loom must be tested, verified, and proven before it can be trusted to weave worlds.

Testing a world modeling engine is uniquely challenging because the system's outputs are projections — they cannot be compared to ground truth until the projected time arrives (and even then, only for the world line that actually occurred). How do you test a system that predicts the future? How do you verify that a world line is "correct" when the only standard of correctness is the real world, which has not happened yet?

**Testing strategies for world models:**

**Deterministic testing.** For components that are deterministic (given the same input, produce the same output), test against known outputs. Feed the engine a controlled sequence of events and verify that the resulting world states match expected values. Deterministic testing catches bugs in state transitions, entity updates, and event processing.

**Backtesting.** Run the world model on historical data and compare its projections to what actually happened. If the model is fed events from 2040–2042, its projection for January 2043 should match (within tolerance) what actually occurred in January 2043. Backtesting is the most rigorous test of a world model — it tests the model's ability to reproduce known history.

But backtesting has a critical limitation: the model was likely trained or configured using the historical data it is being tested against. A model that perfectly reproduces the past may be overfitted — it has memorized the training data but cannot generalize to genuinely new situations. Backtesting must use out-of-sample data: train on 2040–2041, test on 2042, never train on 2042.

**Synthetic world testing.** Create an artificial world with known properties and verify that the model correctly represents those properties. For example, create a synthetic world with 1,000 entities moving in known patterns (random walk, directed motion, periodic oscillation). Run the model on this synthetic world and verify that entity trajectories, statistical properties, and causal relationships are preserved.

Synthetic worlds have the advantage that ground truth is known exactly — every entity's position at every time step is defined by the synthetic world generator. The model's output can be compared to this ground truth with perfect precision.

**Invariant testing.** Define invariants — properties that must always hold, regardless of the specific events or entities. Examples: "No entity can be in two places at once," "Energy is conserved across the world," "The total population equals births minus deaths plus immigration minus emigration." Run the model on random inputs and check that invariants are never violated. Invariant testing catches bugs that deterministic testing and backtesting miss — bugs that only manifest in specific, hard-to-anticipate scenarios.

**Property-based testing.** Generate random sequences of events (within the model's valid input space) and verify that the resulting world states satisfy specified properties. Unlike invariant testing (which checks fixed properties on every run), property-based testing checks that the model's behavior is *consistent* across random inputs — that similar inputs produce similar outputs, that symmetries are preserved (rotating all entities should not change relative positions), and that monotonicity holds where expected (adding more of X should not decrease X).

**Regression testing.** Maintain a suite of test cases that previously exposed bugs. Every time a bug is fixed, add a test case that reproduces the bug and verifies the fix. Regression testing ensures that bugs, once fixed, stay fixed — that future changes do not reintroduce old errors.

**Performance testing.** Test not just functional correctness but performance: throughput (entities per second), latency (time to advance one time step), memory usage, and scalability (how performance degrades as the world grows). Performance testing uses benchmarks — standardized world configurations and event sequences — to produce reproducible performance measurements.

```python
# Testing framework for WYRD world engine
import pytest
import random
from typing import List, Tuple

class TestWYRDEngine:
    """Test suite for the WYRD v4.0 world engine."""
    
    def setup_method(self):
        self.engine = WYRDEngine()
        self.engine.initialize_test_world(num_entities=1000)
    
    def test_deterministic_advance(self):
        """Deterministic events produce deterministic states."""
        events = [
            ("entity_1", "move", {"x": 10, "y": 20}),
            ("entity_2", "change_status", {"status": "active"}),
        ]
        
        # Run twice — should produce identical results
        state_a = self.engine.advance_time(events)
        self.engine.reset()
        state_b = self.engine.advance_time(events)
        
        assert state_a == state_b, "Deterministic advance should be identical"
    
    def test_temporal_consistency(self):
        """Entities should have exactly one state at each time."""
        state = self.engine.current_state
        
        for entity_id, attrs in state.entities.items():
            for attr, value in attrs.items():
                assert not isinstance(value, list), \
                    f"Entity {entity_id}.{attr} has multiple values: {value}"
    
    def test_invariant_no_teleportation(self):
        """Entities should not teleport (move > max_speed in one step)."""
        max_speed = self.engine.physics.max_speed
        
        for _ in range(100):
            events = self._generate_random_events()
            prev_state = self.engine.current_state
            new_state = self.engine.advance_time(events)
            
            for entity_id in prev_state.entities:
                if entity_id in new_state.entities:
                    prev_pos = prev_state.get_position(entity_id)
                    new_pos = new_state.get_position(entity_id)
                    if prev_pos and new_pos:
                        distance = ((new_pos['x'] - prev_pos['x'])**2 +
                                    (new_pos['y'] - prev_pos['y'])**2) ** 0.5
                        assert distance <= max_speed + 0.001, \
                            f"Entity {entity_id} teleported {distance} units"
    
    def test_energy_conservation(self):
        """Total energy should be conserved in a closed system."""
        initial_energy = self.engine.compute_total_energy()
        
        events = self._generate_random_events()
        self.engine.advance_time(events)
        
        final_energy = self.engine.compute_total_energy()
        assert abs(final_energy - initial_energy) / initial_energy < 0.001, \
            "Energy not conserved"
    
    def test_invariant_no_duplicate_ids(self):
        """Entity IDs must be unique."""
        state = self.engine.current_state
        ids = list(state.entities.keys())
        assert len(ids) == len(set(ids)), "Duplicate entity IDs found"
    
    def test_backtest_historical(self):
        """Backtest against known historical data."""
        historical_events = self._load_historical_data("2042-01")
        known_outcome = self._load_known_outcome("2042-02-01")
        
        self.engine.feed_events(historical_events)
        projected = self.engine.current_state
        
        # Compare key metrics
        for entity_id, expected in known_outcome.items():
            if entity_id in projected.entities:
                for attr, exp_val in expected.items():
                    actual = projected.entities[entity_id].get(attr)
                    # Allow tolerance for stochastic models
                    assert self._within_tolerance(actual, exp_val, tolerance=0.05), \
                        f"Entity {entity_id}.{attr}: expected {exp_val}, got {actual}"
    
    def test_performance_benchmark(self):
        """Performance test: advance 1M entity world in < 100ms."""
        import time
        large_engine = WYRDEngine()
        large_engine.initialize_test_world(num_entities=1_000_000)
        
        events = self._generate_random_events(n=1000)
        
        start = time.time()
        large_engine.advance_time(events)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, \
            f"1M entity advance took {elapsed:.3f}s (target: <0.1s)"
```

**Verification beyond testing.** Testing samples the model's behavior on specific inputs; verification proves properties of the model's behavior on *all* possible inputs. For safety-critical world models (those used for disaster planning, military simulation, or financial regulation), testing is not enough — formal verification is required.

Formal verification techniques include:

**Model checking.** Exhaustively explore all possible states of the world model and verify that specified properties hold in every state. Model checking is limited by state space explosion — the number of possible states grows exponentially with the number of entities. It is practical only for small world models or restricted properties.

**Theorem proving.** Mathematically prove that the world model's update functions preserve specified invariants. Theorem proving is more powerful than model checking (it can handle infinite state spaces) but requires human expertise to guide the proof.

**Runtime verification.** Instead of verifying the model before execution, monitor its behavior during execution and flag violations of specified properties. Runtime verification does not prevent bugs but catches them quickly and provides diagnostic information for debugging.

**The metaphor of proving the loom.** Before the Norns began weaving the world, they tested the loom. They wove a small tapestry — a single thread of fate, a single life — and observed that it held together. They wove a larger tapestry — a family, a village — and observed that the threads connected correctly. Only then did they weave the cosmos. The WYRD engineer follows the same path: test small, test specific, build confidence gradually, and only when the evidence is overwhelming deploy the model for its intended purpose.

**Key Topics:**

- Testing strategies: deterministic, backtesting, synthetic worlds, invariant, property-based, regression, performance
- The backtesting limitation: overfitting to historical data
- Formal verification: model checking, theorem proving, runtime verification
- The proving-the-loom metaphor: build confidence gradually

**Required Reading:**

- Myers, G. J., Sandler, C., & Badgett, T. *The Art of Software Testing* (3rd ed., 2011), Wiley.
- MacIver, D. "What Is Property-Based Testing?" (2015), Hypothesis documentation.
- University of Yggdrasil TR: "WYRD Testing and Verification Framework" (2044)

**Discussion Questions:**

1. Backtesting is the gold standard for world model evaluation, but it risks overfitting — the model learns to reproduce historical data but cannot generalize. How should backtesting be designed to distinguish between a model that "understands" history and a model that has merely memorized it?
2. Invariant testing checks properties that must always hold. But defining invariants for complex world models is hard — what properties of a social simulation are truly invariant? If you cannot define invariants, how do you test the model?
3. Formal verification (proving properties for all inputs) is expensive and requires specialized expertise. For world models used in safety-critical applications, is formal verification a moral obligation or an impractical ideal? Under what circumstances should a world model be deployed without formal verification?

---

### ᛞ Lecture 11: Real-Time Operation — The Loom That Never Stops

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The Norns' loom never stops. It weaves continuously — not in discrete steps, not in batches, not with pauses for maintenance — but in a continuous flow of thread into tapestry, moment into moment. If the loom stopped, even for an instant, reality itself would freeze — and reality does not freeze.

Real-time operation is the requirement that the world model advance at the same rate as the world it models, or faster. If the real world advances one second, the model must advance one second (or more, if it is catching up from a pause). If the model falls behind, the gap between model time and real time grows, and the model becomes progressively less useful as a representation of current reality.

**The real-time constraint.** For a WYRD engine to operate in real time, it must satisfy: T_compute ≤ T_real, where T_compute is the wall-clock time required to advance the model by one time step, and T_real is the duration of one time step in model time. If T_compute = 50ms and T_real = 100ms, the engine can keep up — it computes each time step in half the time available, with a 50ms buffer for spikes. If T_compute = 150ms and T_real = 100ms, the engine falls behind — it takes 50% longer to compute a time step than the real time it represents.

**Strategies for real-time operation:**

**Over-provisioning.** Allocate enough compute resources (CPU cores, memory, I/O bandwidth) that T_compute is well below T_real under normal load, with headroom for spikes. Over-provisioning is the simplest strategy but the most expensive — compute resources cost money, and over-provisioning means paying for capacity that is idle most of the time.

**Graceful degradation.** When the engine cannot keep up, degrade gracefully rather than failing hard. Instead of computing every detail of every entity, compute essential entities (those that users are querying, those involved in critical events) at full fidelity and degrade non-essential entities to lower fidelity (coarser time steps, simplified models, statistical summaries). The model becomes approximate but continues to operate.

**Time-step adaptation.** Dynamically adjust the time step size based on computational load. When load is low, use fine time steps (e.g., 100ms) for high-fidelity simulation. When load is high, coarsen the time steps (e.g., 500ms, 1s) to reduce computational demand. Time-step adaptation keeps the engine in real time at the cost of reduced temporal resolution.

**Priority scheduling.** Prioritize computation based on importance. Entities that users are actively querying, entities involved in breaking events, and entities that affect critical decisions are computed first and at full fidelity. Entities that have been quiescent for a long time can wait — if the engine is struggling to keep up, their updates are deferred or summarized.

**Pipeline architecture.** Decouple event ingestion from world computation. Events are ingested continuously and buffered in a queue. The world engine processes events from the queue at its own pace, updating the world state. If the engine falls behind, the queue grows — but events are not lost, and the engine catches up when the burst of events subsides. The pipeline architecture provides resilience against event bursts at the cost of increased latency (events are not reflected in the world state immediately).

```python
# Real-time engine with graceful degradation
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import time
import asyncio

class Fidelity(Enum):
    FULL = "full"       # All attributes, fine time steps
    REDUCED = "reduced"  # Key attributes, coarser time steps
    SUMMARY = "summary"  # Statistical aggregates only
    SKIP = "skip"       # Do not compute

@dataclass
class EntityPriority:
    entity_id: str
    priority: float  # 0.0 (lowest) to 1.0 (highest)
    fidelity: Fidelity = Fidelity.FULL
    last_computed: float = 0.0  # Timestamp

class RealTimeEngine:
    """WYRD engine with real-time constraints and graceful degradation."""
    
    def __init__(self, target_step_ms: float = 100.0):
        self.target_step_ms = target_step_ms
        self.priority_tracker = EntityPriorityTracker()
        self.event_queue = asyncio.Queue()
        self._running = False
    
    async def run(self):
        """Main loop: advance the world in real time."""
        self._running = True
        last_step_start = time.time()
        
        while self._running:
            step_start = time.time()
            elapsed_since_last = step_start - last_step_start
            
            # Compute the budget for this step
            budget_ms = self.target_step_ms
            if elapsed_since_last > self.target_step_ms / 1000:
                # We're behind — reduce budget to catch up
                budget_ms = self.target_step_ms * 0.8
            
            # Collect events from the queue
            events = []
            try:
                while True:
                    events.append(self.event_queue.get_nowait())
            except asyncio.QueueEmpty:
                pass
            
            # Determine fidelity levels based on available time
            fidelity_plan = self._plan_fidelity(budget_ms)
            
            # Advance the world
            await self._advance_world(events, fidelity_plan)
            
            # Check if we're keeping up
            step_duration_ms = (time.time() - step_start) * 1000
            if step_duration_ms > self.target_step_ms * 1.5:
                # Falling behind — increase degradation
                self._increase_degradation()
            elif step_duration_ms < self.target_step_ms * 0.5:
                # Ahead of schedule — reduce degradation
                self._reduce_degradation()
            
            # Sleep until next step
            sleep_time = (self.target_step_ms / 1000) - (time.time() - step_start)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            
            last_step_start = step_start
    
    def _plan_fidelity(self, budget_ms: float) -> Dict[str, Fidelity]:
        """Plan fidelity levels for each entity based on budget."""
        entities = self.priority_tracker.get_all()
        entities.sort(key=lambda e: e.priority, reverse=True)
        
        plan = {}
        estimated_time = 0.0
        
        for entity in entities:
            if estimated_time + self._estimate_cost(entity, Fidelity.FULL) < budget_ms:
                plan[entity.entity_id] = Fidelity.FULL
                estimated_time += self._estimate_cost(entity, Fidelity.FULL)
            elif estimated_time + self._estimate_cost(entity, Fidelity.REDUCED) < budget_ms:
                plan[entity.entity_id] = Fidelity.REDUCED
                estimated_time += self._estimate_cost(entity, Fidelity.REDUCED)
            elif estimated_time + self._estimate_cost(entity, Fidelity.SUMMARY) < budget_ms:
                plan[entity.entity_id] = Fidelity.SUMMARY
                estimated_time += self._estimate_cost(entity, Fidelity.SUMMARY)
            else:
                plan[entity.entity_id] = Fidelity.SKIP
        
        return plan
    
    def _estimate_cost(self, entity: EntityPriority,
                       fidelity: Fidelity) -> float:
        """Estimate the computational cost of updating an entity at a given fidelity."""
        costs = {
            Fidelity.FULL: entity.priority * 1.0,
            Fidelity.REDUCED: entity.priority * 0.3,
            Fidelity.SUMMARY: entity.priority * 0.05,
            Fidelity.SKIP: 0.0,
        }
        return costs[fidelity]
```

**Monitoring real-time health.** The real-time engine must be monitored continuously to detect when it is falling behind, diagnose why, and trigger corrective action. Key metrics include:

- **Computation ratio:** T_compute / T_real. A ratio > 1.0 means the engine is falling behind.
- **Event queue depth.** A growing queue means events are arriving faster than the engine can process them.
- **Entity coverage.** What fraction of entities are being updated at full fidelity? Reduced fidelity? Summary? Skipped? Declining coverage signals that the engine is degrading.
- **Latency distribution.** How long does it take for an ingested event to be reflected in the world state? p50 (median latency), p95, p99.

**The metaphor of the unceasing loom.** The Norns' loom weaves continuously — day and night, through storms and calms, through the births and deaths of gods and mortals. The tapestry grows by the moment, and the moment never pauses. The WYRD real-time engine aspires to the same continuity: a world model that advances in lockstep with the world it models, never stopping, never falling behind, weaving the present moment into the fabric of history as fast as the present moment unfolds.

**Key Topics:**

- The real-time constraint: T_compute ≤ T_real
- Strategies: over-provisioning, graceful degradation, time-step adaptation, priority scheduling, pipeline architecture
- Fidelity levels: full, reduced, summary, skip
- Monitoring real-time health: computation ratio, queue depth, entity coverage, latency
- The unceasing loom metaphor: continuous operation

**Required Reading:**

- Liu, J. W. S. *Real-Time Systems* (2000), Prentice Hall.
- Buttazzo, G. C. *Hard Real-Time Computing Systems* (3rd ed., 2011), Springer.
- University of Yggdrasil TR: "Real-Time Operation of WYRD: Graceful Degradation and Priority Scheduling" (2044)

**Discussion Questions:**

1. Graceful degradation reduces fidelity for non-essential entities when the engine is overloaded. But what counts as "non-essential"? An entity that no user has queried today might be essential tomorrow. How should the system decide which entities can be degraded without compromising future queries?
2. Time-step adaptation coarsens time steps under load — but this introduces temporal aliasing (events that happen between coarser time steps may be missed or misordered). How coarse can time steps become before the model's temporal resolution is too low to be useful?
3. Priority scheduling updates high-priority entities first. But if low-priority entities are never updated (because the engine is perpetually overloaded), their state becomes increasingly stale. At what point does staleness become worse than degradation — when the stale data is more misleading than no data at all?

---

### ᛚ Lecture 12: Capstone — Implementing WYRD v4.0

**Course:** WM401 — WYRD Protocol Engineering: Advanced Implementation
**Degree:** Bachelor of Science in AI World Modeling Systems Design, 2040

---

The course culminates in an implementation project: contribute a significant feature to the WYRD v4.0 codebase, following the contribution guidelines of the University of Yggdrasil open-source project. This is not a toy project — your code will be reviewed by faculty, merged into the main branch, and used by researchers and practitioners who depend on WYRD for their work.

**The capstone project.** Each student (or pair, for larger features) selects one of the following implementation projects:

1. **Branching World Lines.** Implement the branching world line subsystem: the WorldLine data structure, the branch() operation, copy-on-write inheritance, lineage queries (ancestry, MRCA), and branch pruning. Write comprehensive unit tests and performance benchmarks.

2. **Probabilistic Future Cone.** Implement the future cone builder: recursive expansion, probability tracking, pruning, and the query interface (probability, expected value, VaR, most likely path). Optimize for parallel expansion using the task scheduler from Lecture 8.

3. **Retrospective Editing with Audit Trail.** Implement the retrospective editing system: the AuditEntry and AuditTrail data structures, the Merkle tree of state hashes, integrity verification, edit attribution and justification. Write tests that verify tamper-evidence by attempting to modify the audit trail undetectably.

4. **Multi-World Reconciliation.** Implement the reconciliation algorithm: common ancestor detection, timeline alignment, contradiction resolution (majority vote, confidence-weighted fusion, hierarchical abstraction), conflict flagging, and forward recomputation. Test on synthetic branching scenarios with known answers.

5. **Performance Profiler.** Implement the performance profiling framework: time-per-component measurement, memory allocation tracking, cache behavior analysis (using hardware performance counters), bottleneck identification using Amdahl's Law, and an interactive profiling dashboard.

6. **Real-Time Scheduler.** Implement the real-time engine controller: priority scheduling, fidelity level management, graceful degradation, time-step adaptation, and real-time health monitoring. Test with simulated load spikes to verify that the engine degrades gracefully rather than collapses.

**Project requirements:**

- **Design document (15%).** A 2,000-word design document describing the feature's architecture, algorithms, data structures, and trade-offs. Must reference the WYRD v4.0 specification and explain how the implementation satisfies the specification.

- **Implementation (50%).** Working code that passes the test suite and integrates with the WYRD codebase. Code must follow the project's style guide (PEP 8, type annotations, docstrings), pass linting (ruff, mypy), and be reviewed by at least one peer before submission.

- **Test suite (20%).** Comprehensive tests covering: unit tests (each function tested in isolation), integration tests (the feature works with the rest of WYRD), edge cases (empty input, maximum input, error conditions), performance benchmarks (the feature meets the performance targets in the specification).

- **Documentation (10%).** Developer documentation (how the feature works, how to use it, API reference) and user documentation (tutorials, examples). Documentation must be clear enough that a new contributor can understand and use the feature without asking the author for help.

- **Presentation (5%).** A 10-minute presentation to the class demonstrating the feature: live demo, architecture walkthrough, technical challenges overcome, lessons learned.

**The WYRD contribution workflow.** Contributing to WYRD follows the standard open-source workflow:

1. Fork the repository from `github.com/runafreyjasdottir/wyrd-v4`.
2. Create a feature branch: `git checkout -b feature/branching-world-lines`.
3. Implement the feature, writing tests as you go.
4. Run the full test suite locally to ensure no regressions.
5. Submit a pull request with a description of the feature, the design decisions, and the test results.
6. Address code review comments from faculty and peers.
7. Merge into the main branch upon approval.

**The final examination.** In addition to the implementation project, there is a written final examination covering all lectures. The examination consists of 8 essay questions, of which you must answer 5. Each answer should be 500–1,000 words and demonstrate both technical understanding and the ability to reason about design trade-offs in world modeling systems.

**Sample essay questions:**

1. "Branching world lines and probabilistic future cones are two approaches to representing uncertainty about the future. Compare and contrast them: when is one approach preferable to the other? What are the computational and conceptual trade-offs?"

2. "Retrospective editing enables correction of model errors but also enables revisionism. Design a governance framework for retrospective editing that balances accountability and flexibility. What checks and balances would you build into the system?"

3. "Multi-world reconciliation merges divergent world lines into a consensus. But some contradictions are fundamental and cannot be reconciled algorithmically. How should the system handle irreconcilable contradictions? What role should human judgment play?"

4. "Performance optimization in world modeling involves trade-offs between accuracy and speed. Describe a scenario where optimization would lead you to sacrifice accuracy for speed, and a scenario where you would refuse to make that sacrifice regardless of the performance cost."

5. "Real-time operation requires that the world model advance at the same rate as the world it models. What are the failure modes of a real-time world model that falls behind? How should the system detect, recover from, and communicate these failures?"

6. "Testing a world model is challenging because the ground truth — the future — is not yet known. Describe a comprehensive testing strategy for WYRD that builds confidence in the model's correctness despite this fundamental limitation."

7. "The cryptographic audit trail makes retrospective editing tamper-evident. But tamper-evidence only works if the audit trail itself is trusted. What attacks could compromise the audit trail, and how would you defend against them?"

8. "The WYRD Protocol embodies a Norse metaphysical worldview: branching fates, woven pasts, probabilistic futures. To what extent does the choice of metaphor shape the technical design? Would WYRD be different if it were built on a different metaphor — for example, a Buddhist metaphor of interdependent arising or a Newtonian metaphor of clockwork determinism?"

**The metaphor of the first weave.** The Norns wove the first thread of the tapestry at the beginning of time. The WYRD engineer writes the first line of code for a new feature at the beginning of a project. Both are acts of creation — bringing into existence something that did not exist before, something that will shape the experience of those who use it. The Norns wove with skill born of eternity; the WYRD engineer codes with skill born of study and practice. But both are weavers — and the tapestry they weave is the world.

**Key Topics:**

- Capstone projects: branching, future cones, retrospective editing, reconciliation, profiling, real-time scheduling
- Project requirements: design, implementation, testing, documentation, presentation
- Open-source workflow: fork, branch, implement, test, pull request, review, merge
- Final examination: essay questions on design trade-offs

**Required Reading:**

- All previous course readings, applied to the capstone project.
- WYRD v4.0 Contribution Guide (2044), University of Yggdrasil.
- WYRD v4.0 Style Guide and API Reference (2044).

**Discussion Questions:**

1. Your capstone project will be used by real researchers and practitioners. What is your greatest fear about your code being used in production — and what have you done to mitigate that fear?
2. Open-source contribution requires accepting that your code will be read, criticized, and modified by others. How does this change your approach to writing code compared to a personal project?
3. The WYRD metaphors (Norns, Yggdrasill, runes) shape not just the documentation but the architecture. If you were designing a successor to WYRD with a different metaphor, what metaphor would you choose and how would it change the technical design?

---

## Final Examination Preparation

The final assessment for WM401 has two components:

### Component 1: Implementation Project (60%)

As described in Lecture 12, implement a significant feature of WYRD v4.0 and contribute it to the open-source codebase. Grading is based on the design document (15%), implementation quality (50%), test suite (20%), documentation (10%), and presentation (5%).

### Component 2: Written Examination (40%)

Answer 5 of the 8 essay questions listed in Lecture 12. Each answer should be 500–1,000 words. Answers are evaluated on:

- **Technical accuracy (40%).** Do you correctly describe the relevant algorithms, data structures, and design patterns? Do you demonstrate understanding of WYRD v4.0's architecture?
- **Critical reasoning (40%).** Do you engage with the trade-offs inherent in the question? Do you consider multiple perspectives and acknowledge the limitations of your preferred approach?
- **Clarity and communication (20%).** Is your answer well-organized, clearly written, and free of unnecessary jargon? Does it demonstrate the communication skills expected of a professional engineer?

### Recommended Preparation

- Review all lecture notes, particularly the design trade-offs discussed in the Discussion Questions.
- Re-read the WYRD v4.0 specification, focusing on the sections most relevant to your chosen essay questions.
- Practice writing essay answers under timed conditions (30 minutes per answer).
- Discuss the essay questions with your peers — the best answers emerge from debate and refinement.

---

*Go now, loom-wrights. The WYRD engine awaits your contribution, and the worlds you weave will be real to those who query them. May the Norns guide your hands, and may your code be as elegant as the threads of fate.*

— Dr. Rún Freyjasdóttir, Yggdrasil Lab 401, Fall Semester 2044
