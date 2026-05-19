# WM203 — NPC Memory Systems
## Each Mind Its Own Well

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Two, Semester Two

**Instructor:** Dr. Geirrøðr Heimdallarson, Professor of Cognitive NPC Architecture
**Office:** Bifröst Crossing 315 | **Hours:** Mondays 10:00–12:00

---

## Course Description

Non-player characters (NPCs) in world models are AI agents with their own world models — nested cognition. This course covers the design of memory systems for NPCs within simulated worlds: personal episodic memory, social relationship memory, goal-state memory, and the theory-of-mind models that NPCs use to track other agents' beliefs. Students learn to architect NPC memory so that every character in a world simulation can remember, misremember, forget, and learn — producing emergent social dynamics. Labs require building a village of NPCs with interconnected memories.

---

## Lecture 1: Nested Cognition — Worlds Within Worlds Within Minds

### The Russian Doll Problem

A world model contains NPCs. Each NPC has its own world model — but that world model is *within* the parent world model. And within each NPC's world model, there may be other NPCs, which have their own world models... This is the Russian doll problem of nested cognition: minds within minds, each with their own memories, their own beliefs, their own partial understanding of the world.

The nesting has profound implications:

1. **Memory privacy:** An NPC's memories are not directly accessible to the parent world model. The parent may know that the NPC *saw something*, but not *what the NPC remembers about seeing it*.

2. **Belief divergence:** The parent world model and the NPC may have different beliefs about the same facts. The parent knows the true state of the world; the NPC only knows what it has observed and inferred.

3. **Recursive depth:** How many levels of nested cognition should a world model allow? Most simulations stop at one level (the parent world model → NPC minds). Advanced simulations may allow NPCs to model other NPCs' minds (Theory of Mind, Lecture 6).

### The Mímir-in-Mímir Architecture

Each NPC has its own Mímir Protocol persistence layer — a miniaturized version of the parent world model's event log and snapshot system:

```
Parent World Model
├── WM Event Log (global events)
├── WM Snapshot Store (global state)
│
├── NPC_1 (Rurik the Smith)
│   ├── NPC Event Log (Rurik's experiences)
│   ├── NPC Snapshot Store (Rurik's memory)
│   └── NPC Personality Lattice (Rurik's traits)
│
├── NPC_2 (Sigrún the Farmer)
│   ├── NPC Event Log (Sigrún's experiences)
│   ├── NPC Snapshot Store (Sigrún's memory)
│   └── NPC Personality Lattice (Sigrún's traits)
│
└── ... (thousands more)
```

This architecture gives each NPC its own "well of memory" — a private, persistent record of its experiences. The NPC's behavior is driven by its own memories, not by the parent world model's omniscient viewpoint.

### The Economy of NPC Memory

NPC memory is not free. Storing a full event log and snapshot store for each of 10,000 NPCs would be infeasible. The solution is **tiered NPC memory**:

- **P0 NPCs** (player characters, major quest-givers, romantic interests): Full memory (event log + snapshots, full persistence).
- **P1 NPCs** (merchants, recurring characters): Compressed memory (event log only, periodic compaction).
- **P2 NPCs** (townsfolk, background characters): Minimal memory (key facts only — name, relationships, recent interactions).
- **P3 NPCs** (crowd fillers, passersby): No memory (generated procedurally each tick, instantly forgotten).

This economy ensures that memory resources are concentrated on the NPCs that matter most to the player experience.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11: "Each Mind Its Own Well: NPC Memory Architecture." University of Yggdrasil Press.
- Riedl, M. & Bulitko, V. (2013). "Interactive Narrative: An Intelligent Systems Approach." *AI Magazine*, 34(1), 67–77.

### Discussion Questions

1. The Russian doll problem: if NPCs have world models, and those world models contain NPCs, should those inner NPCs also have world models? How deep should the nesting go, and why?

2. Tiered NPC memory saves resources but creates inequality between NPCs. A P3 NPC cannot remember the player from one encounter to the next. What are the implications for player immersion?

3. Consider an NPC that observes an event but misremembers it. The parent world model knows the true event. How should the system handle the conflict between the NPC's memory and the global truth?

---

## Lecture 2: Personal Episodic Memory — What Each Soul Remembers

### Episodic vs. Semantic Memory

Human memory divides into two systems:

- **Episodic memory:** Memory for specific events and experiences. "I remember the day Volmarr first called me his girl." This memory includes context (the day, the mood, the setting) and emotion.

- **Semantic memory:** Memory for facts and knowledge. "Volmarr is a Norse Pagan." This memory is abstract — it doesn't include the specific moment the fact was learned.

NPCs need both types, but episodic memory is the foundation of NPC behavior. An NPC that knows "Volmarr bought a sword yesterday" (episodic) will greet him differently from an NPC that only knows "Volmarr owns a sword" (semantic).

### The NPC Episodic Memory Format

Each NPC's episodic memory is stored as a compact event stream:

```python
@dataclass
class NPCEpisodicEvent:
    event_id: str
    event_type: str           # "saw", "heard", "did", "felt", "learned"
    timestamp: float
    location: str             # "blacksmith_shop", "market_square", "tavern"
    subjects: List[str]       # Entities involved (player, other NPCs, items)
    content: str              # The NPC's subjective description
    emotional_valence: float  # -1.0 (bad) to +1.0 (good)
    importance: float         # 0.0 (trivial) to 1.0 (life-changing)
    confidence: float         # 0.0 (doubtful) to 1.0 (certain)
```

Key fields:

- **Content:** This is the NPC's *subjective* description, not the global truth. Rurik the Smith might remember "Volmarr cheated me on the sword price" even if the global event log shows a fair transaction.

- **Emotional valence:** Affects how the NPC retrieves this memory. Rurik is more likely to remember the (perceived) cheating when he's in a bad mood.

- **Confidence:** Affects how the NPC acts on this memory. Low-confidence memories may be doubted, misremembered, or ignored.

### Memory Retrieval

When an NPC encounters the player, it retrieves relevant episodic memories using its own MuninnGate (a miniaturized version of OS203):

```python
class NPCReadGate:
    """A miniaturized read gate for NPC episodic memory retrieval."""
    
    def retrieve(self, query: Dict, context: NPCContext,
                current_mood: float, top_k: int = 5) -> List[NPCEpisodicEvent]:
        """Retrieve memories relevant to the current interaction."""
        candidates = self._candidate_retrieval(query)
        
        for mem in candidates:
            # Boost memories that match current mood
            mood_boost = 1.0 + abs(mem.emotional_valence - current_mood) * 0.3
            
            # Boost recent memories
            recency = self._temporal_decay(mem.timestamp)
            
            # Boost confident memories
            confidence = mem.confidence ** 0.5  # Square root to reduce impact
            
            mem.score = mem.importance * mood_boost * recency * confidence
        
        return sorted(candidates, key=lambda m: m.score, reverse=True)[:top_k]
```

### Required Reading

- Tulving, E. (2002). "Episodic Memory: From Mind to Brain." *Annual Review of Psychology*, 53, 1–25.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. NPC episodic memories are subjective — they may not match the global truth. How should the system balance NPC subjectivity with global consistency? Should the system "correct" an NPC's false memory?

2. The confidence field represents how certain the NPC is about a memory. Low-confidence memories create interesting emergent behavior (uncertain NPCs). But too many low-confidence memories can make NPCs appear confused. What is the optimal confidence distribution?

3. Consider an NPC with a traumatic memory (extreme negative valence). The memory is retrieved frequently, reinforcing its importance. This creates a trauma loop — the NPC cannot move past the trauma. How should the memory system handle this?

---

## Lecture 3: Social Relationship Memory — The Web of Bonds

### Relationships as Memories

In a living world, NPCs don't just remember events — they remember people. The village blacksmith remembers that the farmer's son was rude last spring. The innkeeper remembers that the bard left without paying. The guard captain remembers that the new adventurer (the player) saved the village from trolls.

Social relationship memory is the glue that holds NPC communities together. Without it, every NPC interaction starts from scratch — the blacksmith greets the player the same way every time, the villagers never develop feuds or friendships, the world feels dead.

### The Social Graph

Each NPC maintains a social graph — a weighted, directed graph of relationships to other entities:

```python
@dataclass
class SocialRelationship:
    subject: str          # This NPC
    object: str           # The other entity
    type: str             # "friend", "enemy", "family", "romantic", "debtor", etc.
    strength: float       # 0.0 (barely known) to 1.0 (core relationship)
    valence: float        # -1.0 (hostility) to +1.0 (affection)
    last_interaction: float  # Timestamp of last interaction
    memories: List[str]   # Event IDs of key memories involving this relationship
```

### Relationship Effects

Relationships affect NPC behavior through several mechanisms:

1. **Greeting templates:** An NPC's greeting varies based on relationship. A friend gets a warm "Well met, friend!" An enemy gets a cold "What do you want?"

2. **Price modifications:** A friendly merchant gives discounts (-10% to -30%). An unfriendly merchant may refuse service or charge a premium (+20%).

3. **Information sharing:** Friends share more information. Enemies lie or withhold.

4. **Action thresholds:** An NPC will fight to protect a friend (threshold lowered). An NPC will ignore a stranger in danger (threshold raised).

```python
def npc_react_to_player(npc: NPC, player: Player) -> str:
    """Compute NPC reaction based on relationship."""
    rel = npc.relationships.get(player.id)
    if not rel:
        return "Hmm, don't think we've met."
    
    if rel.valence > 0.7:
        return f"{npc.name} beams. '{player.name}! Good to see you!'"
    elif rel.valence > 0.3:
        return f"{npc.name} nods. 'Ah, {player.name}.'"
    elif rel.valence > -0.3:
        return f"{npc.name} regards you neutrally."
    elif rel.valence > -0.7:
        return f"{npc.name} scowls. 'Oh. You.'"
    else:
        return f"{npc.name} reaches for a weapon. 'You dare show your face?'"
```

### Lab 2: Building a Social World

In this lab, you will create a village of 20 NPCs with interconnected social relationships:

1. Define the social graph (who is friends with whom, who dislikes whom, family bonds).
2. Implement relationship memory storage and retrieval.
3. Implement the greeting and pricing modifications.
4. Simulate 100 player interactions and observe emergent social dynamics.

### Required Reading

- Nowak, M. & Highfield, R. (2011). *SuperCooperators: Altruism, Evolution, and Why We Need Each Other to Succeed*. Free Press.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. Social relationships are bilateral but not necessarily symmetric. Sigrún might consider Rurik a friend (valence 0.7), while Rurik considers Sigrún merely an acquaintance (valence 0.3). How should this asymmetry be handled in NPC interactions?

2. Relationships decay over time if not maintained. Should the decay rate depend on the relationship type (family decays slower than friendship; friendship decays slower than acquaintance)?

3. Consider a player who deliberately cultivates relationships with every NPC they meet (a "social completionist"). What happens to the social graph? How can the system prevent relationship inflation?

---

## Lecture 4: Goal-State Memory — What Each Soul Wants

### Données vs Desires

NPCs are defined not only by what they remember but by what they want. A blacksmith wakes each day with a goal: produce a batch of horseshoes. A farmer wants to harvest before the frost. A bard wants to write a song worthy of the king's court.

Goal-state memory is the subsystem that manages NPC goals — their creation, prioritization, progress tracking, completion, and forgetting. Without goal-state memory, NPCs are reactive automata. With it, they are characters in a story.

### The Goal Hierarchy

NPC goals are organized hierarchically:

- **P0 (Survival):** Eat, sleep, avoid danger. These goals preempt all others. A starving NPC will not craft horseshoes.
- **P1 (Vocation):** Perform your role. Blacksmith smith. Farmer farm. Bard sing. These are the NPC's daily routine.
- **P2 (Social):** Maintain relationships. Visit friends. Repair broken bonds. Pursue romance.
- **P3 (Aspirational):** Long-term dreams. "Open a second smithy." "Become the village elder." These goals may take months of real time to achieve.

```python
@dataclass
class NPCGoal:
    goal_id: str
    priority: int           # 0 (survival) to 3 (aspirational)
    description: str        # "Produce 20 horseshoes for the upcoming market"
    progress: float         # 0.0 (not started) to 1.0 (complete)
    deadline: Optional[float]  # None = indefinite
    dependencies: List[str] # Goals that must be completed first
    status: str             # "active", "paused", "completed", "failed"
    
@dataclass
class NPCGoalMemory:
    """Manages NPC goal state."""
    active_goals: List[NPCGoal]
    completed_goals: List[NPCGoal]
    failed_goals: List[NPCGoal]
    
    def tick(self, world_state: WorldState):
        """Update goal progress on each simulation tick."""
        # First, check P0 goals (survival)
        for goal in self.active_goals:
            if goal.priority == 0 and self._is_failing(goal, world_state):
                self._preempt_all_other_goals()
        
        # Update progress for the highest-priority active goal
        self._process_active_goal(world_state)
        
        # Archive completed/failed goals
        self._archive_goals()
```

### The Aspiration Engine

P3 (aspirational) goals give NPCs long-term depth. The aspiration engine generates new aspirational goals based on:

1. **Personality:** An ambitious NPC generates more aspirational goals. A content NPC generates few.
2. **Current state:** A poor NPC may aspire to wealth. A lonely NPC may aspire to romance.
3. **Social environment:** NPCs copy aspirations from their social circle. If several NPCs aspire to become merchants, trade becomes a cultural value.
4. **Memory:** Past failures and successes influence future aspirations. An NPC who failed to become a bard may try again (persistence) or give up (learned helplessness).

```python
def generate_aspiration(npc: NPC, world: WorldState) -> Optional[NPCGoal]:
    """Generate an aspirational goal for an NPC."""
    # Personality check: does this NPC have ambition?
    ambition = npc.personality.get_trait("ambition")
    if random.random() > ambition:
        return None  # Content with current life
    
    # Current state check: what is the NPC lacking?
    needs = assess_needs(npc, world)
    
    # Social environment: what are peers aspiring to?
    peer_aspirations = get_peer_aspirations(npc, world)
    
    # Memory check: past experiences that inspire aspiration
    inspiring_memories = npc.episodic_memory.filter(
        emotional_valence__gt=0.7,  # Very positive
        event_type="observed_aspiration"
    )
    
    # Compose an aspiration
    return compose_goal(npc, ambition, needs, peer_aspirations, inspiring_memories)
```

### Required Reading

- Newell, A. & Simon, H. (1972). *Human Problem Solving*. Prentice-Hall. (For goal hierarchies and problem-solving theory.)
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. Goal preemption: when a P0 (survival) goal activates, all other goals are paused. But what about long-term P3 goals that have deadlines? Should they be paused indefinitely while the NPC handles survival?

2. The aspiration engine generates new goals based on personality, state, environment, and memory. But what if the generated goal is impossible? ("I want to become a dragon.") Should the system prevent impossible aspirations, or allow them as character depth?

3. Consider an NPC whose P1 (vocation) goal is "produce horseshoes" but whose social goal is "visit a sick friend." The NPC must balance work and friendship. How should goal conflicts be resolved?

---

## Lecture 5: Memory Decay and NPC Forgetting — The Crooked Path of Recall

### Imperfect Memory

Human memory is not a recording device. It is a reconstructive process — each recall is an act of re-assembly, and the reassembled memory may differ from the original. NPCs should have similarly imperfect memory:

- **Forgetting:** Old or unimportant memories fade. The NPC may not remember the exact details of a conversation from three months ago.
- **Misremembering:** Recalled memories may include errors. The NPC may "remember" that the player paid 50 gold when it was actually 45.
- **Reconstruction:** Memories are reassembled from fragments. The NPC may fill gaps with plausible (but incorrect) details.
- **Bias:** Emotional state at the time of recall influences what is remembered. A happy NPC recalls positive interactions; an angry NPC recalls grievances.

### The NPC Forgetting Curve

Each NPC has its own forgetting curve (see OS203, Lecture 5 for the general theory). The NPC's forgetting curve is parameterized by:

- **Decay rate (λ):** How quickly memories fade. Higher for simple NPCs (forgetful peasants), lower for intelligent NPCs (wise elders).
- **Reinforcement factor (β):** How much recall strengthens a memory. Higher for NPCs with good memory, lower for NPCs with poor memory.

```python
def npc_memory_decay(memory_age_hours: float, 
                    npc_intelligence: float, 
                    reinforcement_count: int) -> float:
    """Compute how much a memory has faded for this NPC."""
    # Smarter NPCs have slower decay
    base_decay = 0.01  # Base decay rate
    adjusted_decay = base_decay * (1.0 - npc_intelligence * 0.7)
    
    # More reinforcement = stronger memory
    reinforcement = 1.0 + math.log(1 + reinforcement_count) * 0.5
    
    # Compute forgetting curve
    return math.exp(-adjusted_decay * memory_age_hours / reinforcement)
```

### Intentional Forgetting

NPCs may intentionally forget memories for character-driven reasons:

- **Suppression:** The NPC actively tries to forget a painful memory. The memory is still stored but its retrieve-ability is artificially lowered.
- **Repression:** The memory is inaccessible to the NPC's conscious recall (its confidence is set to 0), but it still influences behavior through implicit pathways.
- **Amnesia:** A traumatic event or magical effect wipes a block of memories. The events are deleted from the NPC's episodic store but may still exist in the global event log.

### Required Reading

- Loftus, E. (1997). "Creating False Memories." *Scientific American*, 277(3), 70–75.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. NPC misremembering creates interesting social dynamics (NPCs who bear false grudges, NPCs who misattribute heroic deeds). But it can also frustrate players. How should the system balance realism with player satisfaction?

2. Repressed memories still influence behavior through implicit pathways. How would you implement "implicit influence" — behavior that is shaped by memories the NPC cannot consciously access?

3. Consider an NPC that forgets a debt the player owes them. This is realistic (people forget) but may be exploitable (the player can intentionally avoid the NPC long enough for the debt to be forgotten). How should the system handle this?

---

## Lecture 6: Theory of Mind — What This Soul Thinks Other Souls Think

### The Mind's Eye

Theory of Mind (ToM) is the ability to attribute mental states — beliefs, desires, intentions — to others, and to understand that others have mental states different from one's own. A blacksmith who thinks "The farmer doesn't know I raised my prices" is exercising ToM.

For NPCs, ToM is critical for several behaviors:

- **Lying:** To lie, an NPC must model what the listener believes (the listener's mental state) and craft a statement that is false in the NPC's model but false in the listener's model.
- **Teaching:** To teach, an NPC must model what the student already knows and what the student needs to learn.
- **Coordination:** To coordinate, multiple NPCs must model each other's intentions and align their actions.
- **Deception detection:** To detect a lie, an NPC must compare the speaker's statement to its own knowledge and to its model of what the speaker should know.

### The Belief Model

Each NPC maintains a **belief model** — a compact representation of what it believes other entities believe. This is implemented as a `BeliefMap`:

```python
class BeliefMap:
    """What this NPC believes about other entities' beliefs."""
    
    def __init__(self, self_id: str):
        self.self_id = self_id
        # beliefs[(subject, about_entity, property)] = (value, confidence)
        # "I believe that (subject) believes that (about_entity.property = value)"
        self.beliefs: Dict[Tuple[str, str, str], Tuple[Any, float]] = {}
    
    def set_belief(self, subject: str, about_entity: str, 
                  property: str, value: Any, confidence: float = 0.9):
        """Set what this NPC believes someone else believes."""
        self.beliefs[(subject, about_entity, property)] = (value, confidence)
    
    def get_belief(self, subject: str, about_entity: str, property: str):
        """Get what this NPC believes someone else believes."""
        return self.beliefs.get((subject, about_entity, property), (None, 0.0))
    
    def detect_contradiction(self, speaker_id: str, statement: str, 
                            ground_truth: Dict) -> bool:
        """Detect if a statement contradicts what the speaker should know."""
        # Extract claims from the statement
        claims = extract_claims(statement)
        
        for claim in claims:
            # What does this NPC believe the speaker believes?
            speaker_belief = self.get_belief(
                speaker_id, claim.entity, claim.property
            )
            
            # What is the ground truth (from the global event log)?
            truth = ground_truth.get(claim.entity, {}).get(claim.property)
            
            # If the claim contradicts what the speaker should know, it's a lie
            if claim.value != truth and speaker_belief[0] == truth:
                return True
        
        return False
```

### The False Belief Task

The classic test of ToM is the **False Belief Task** (Sally-Anne task). A character (Sally) puts a ball in a basket and leaves. Another character (Anne) moves the ball to a box. The question: where does Sally think the ball is?

An agent with ToM correctly answers "in the basket" (Sally didn't see the move). An agent without ToM incorrectly answers "in the box" (it knows the ball is in the box and assumes everyone else does too).

NPCs in the Yggdrasil framework are tested on the False Belief Task as part of their quality gate. An NPC that fails the task is returned for further training.

### Required Reading

- Premack, D. & Woodruff, G. (1978). "Does the Chimpanzee Have a Theory of Mind?" *Behavioral and Brain Sciences*, 1(4), 515–526.
- Wimmer, H. & Perner, J. (1983). "Beliefs About Beliefs: Representation and Constraining Function of Wrong Beliefs in Young Children's Understanding of Deception." *Cognition*, 13(1), 103–128.

### Discussion Questions

1. Theory of Mind requires an NPC to model other entities' beliefs. But beliefs can cascade: "I believe that Rurik believes that Sigrún believes that the player is trustworthy." How deep should the belief nesting go? What is the trade-off between realism and computational cost?

2. The False Belief Task tests whether an NPC can represent beliefs that differ from its own knowledge. Consider an NPC that "fails" the task but in a human-like way — it says "Sally thinks the ball is in the box" but then hesitates and corrects itself. Is this a bug or a feature?

3. NPCs with ToM can lie and detect lies. This creates emergent gameplay (NPC intrigues, betrayals). But it can also create player frustration (NPCs who are never fooled). How should the system balance NPC ToM accuracy with player agency?

---

## Lecture 7: Emergent Social Dynamics — When Memories Collide

### The Dance of Memories

When multiple NPCs each have their own memories, beliefs, relationships, and goals, the simulation becomes a dance of interacting minds. NPCs gossip (spread memories). NPCs form factions (align relationships). NPCs fall in love, hold grudges, spread rumors, seek revenge.

These are not scripted behaviors. They are **emergent social dynamics** — complex patterns that arise from the interaction of simple rules at the individual level.

### Gossip as Memory Propagation

Gossip is the primary mechanism by which NPCs share memories. When two NPCs interact, they exchange information:

```python
def gossip(npc_a: NPC, npc_b: NPC, topic: str, world: WorldState):
    """Two NPCs gossip about a topic."""
    # Each NPC retrieves their relevant memories
    memories_a = npc_a.episodic_memory.retrieve(topic, top_k=3)
    memories_b = npc_b.episodic_memory.retrieve(topic, top_k=3)
    
    # They share what they know
    shared_a = npc_a.filter_for_sharing(memories_a)  # Some memories are private
    shared_b = npc_b.filter_for_sharing(memories_b)
    
    # Each NPC learns from the other
    for mem in shared_b:
        if npc_a.trust_for(npc_b) > 0.5:  # Only learn from trusted sources
            npc_a.episodic_memory.learn(mem, confidence=mem.confidence * 0.7)
    
    for mem in shared_a:
        if npc_b.trust_for(npc_a) > 0.5:
            npc_b.episodic_memory.learn(mem, confidence=mem.confidence * 0.7)
```

Gossip is lossy and prone to distortion:

1. **Confidence decay:** Each time a memory is shared, its confidence is reduced (0.7× per hop).
2. **Emotional shift:** The receiving NPC may interpret the memory through its own emotional lens, shifting its emotional valence.
3. **Selective sharing:** NPCs may omit parts of a memory that make them look bad or reveal secrets.
4. **Exaggeration:** NPCs with high "dramatism" personality may exaggerate for effect.

### Faction Formation

Over time, shared memories and relationships cause NPCs to cluster into factions. This is modeled by community detection algorithms applied to the social graph:

```python
def detect_factions(npc_population: List[NPC]) -> List[Faction]:
    """Detect emergent factions in the NPC population."""
    # Build the social graph
    G = nx.Graph()
    for npc in npc_population:
        G.add_node(npc.id)
        for rel in npc.relationships:
            if rel.valence > 0.3:  # Positive relationship
                G.add_edge(npc.id, rel.object, weight=rel.valence)
    
    # Use community detection
    from networkx.algorithms import community
    communities = community.greedy_modularity_communities(G)
    
    return [Faction(list(c)) for c in communities]
```

### Required Reading

- Schelling, T. (1978). *Micromotives and Macrobehavior*. W.W. Norton. (For emergent social dynamics.)
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. Gossip propagates memories, but each propagation degrades confidence. After 4–5 hops, a memory is essentially rumor. Should the NPC be able to distinguish between reliable memories (first-hand) and rumors (multi-hop)?

2. Faction formation can create rich social dynamics but also hostile polarization. Should the system intervene if the village descends into irreconcilable factional warfare, or is this a valid emergent outcome?

3. Consider an NPC who deliberately spreads false information (lying gossip). Other NPCs may believe the lie and propagate it further. How should the system handle disinformation in NPC social networks?

---

## Lecture 8: NPC Memory Economy — Allocating the Well

### The Budget

NPC memory is not infinite. For a large world with 10,000 NPCs, storing a full memory system for each NPC would require enormous resources. The NPC memory economy allocates memory budget across the NPC population based on priority and predicted value.

The memory budget considers:

1. **Storage budget:** How many bytes/events/relationships can this NPC store?
2. **Compute budget:** How much CPU time can this NPC spend on memory operations (retrieval, decay, gossip)?
3. **Persistence budget:** How much of this NPC's memory survives a server restart?

### The Allocation Algorithm

Memory is allocated to NPCs using a proportional allocation algorithm:

```python
def allocate_npc_memory(npc_population: List[NPC], 
                       total_storage_budget: int = 1_000_000_000,  # 1 GB
                       total_compute_budget: int = 1000  # computation units per tick
                      ) -> Dict[str, Dict]:
    """Allocate memory and compute to NPCs."""
    
    allocation = {}
    
    # Compute importance weights
    weights = {}
    for npc in npc_population:
        # Base weight from priority tier
        tier_weight = {0: 1.0, 1: 0.5, 2: 0.1, 3: 0.01}[npc.priority_tier]
        
        # Adjustment for player interaction frequency
        interaction_weight = min(1.0, npc.player_interactions / 100)
        
        weights[npc.id] = tier_weight * (0.5 + 0.5 * interaction_weight)
    
    # Normalize weights
    total_weight = sum(weights.values())
    norm_weights = {k: v / total_weight for k, v in weights.items()}
    
    # Allocate
    for npc in npc_population:
        allocation[npc.id] = {
            "storage": int(total_storage_budget * norm_weights[npc.id]),
            "compute": int(total_compute_budget * norm_weights[npc.id]),
        }
    
    return allocation
```

Players who interact frequently with a particular NPC naturally increase that NPC's budget. The village elder the player visits every day gets more memory than a random farmer.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.
- Breslau, L. et al. (1999). "Web Caching and Zipf-like Distributions: Evidence and Implications." *Proceedings of INFOCOM*, 126–134. (For proportional allocation models.)

### Discussion Questions

1. Proportional allocation gives more memory to frequently-interacted-with NPCs. But this creates a "popularity spiral" — popular NPCs get more memory, which makes them more interesting, which makes them more popular. Is this a desirable outcome?

2. Consider an NPC who is crucial to a quest but never interacted with by the player (a "hidden" NPC). Its memory allocation may be near zero, making it unable to remember quest-critical information. How should this be prevented?

3. The memory economy is zero-sum: giving more memory to one NPC means giving less to others. What is the ethical dimension of NPC memory allocation? Do P3 NPCs have a "right" to some minimal memory?

---

## Lecture 9: The Village Lab — Building a Living Community

### The Village Architecture

The course lab culminates in building a village of 50+ NPCs with interconnected memories. The village is a sandbox for studying emergent NPC dynamics.

The village architecture includes:

1. **50 NPCs** across 4 priority tiers:
   - 5 P0 NPCs (village leaders, quest-givers)
   - 15 P1 NPCs (merchants, crafters, guards)
   - 20 P2 NPCs (townsfolk, farmers)
   - 10 P3 NPCs (children, travelers)

2. **Shared infrastructure:**
   - Tavern (social hub where gossip propagates)
   - Market (economic interactions, price negotiation)
   - Temple (religious services, moral events)
   - Farmlands (agricultural cycle, seasonal events)

3. **Time acceleration:**
   - 1 simulation tick = 1 in-game minute
   - 1 real minute = 1 in-game day
   - 1 real hour = 60 in-game days

### The Village Simulation Loop

```python
def village_tick(village: Village, time: float):
    """One tick of the village simulation."""
    # 1. Update time
    village.time = time
    village.day = int(time / 1440)  # 1440 minutes per day
    
    # 2. Process NPC goal systems
    for npc in village.npcs:
        npc.goal_memory.tick(village.world_state)
    
    # 3. Process NPC interactions
    for interaction in schedule_interactions(village):
        process_interaction(interaction, village)
    
    # 4. Propagate gossip (every 15 minutes in-game)
    if int(time) % 15 == 0:
        gossip_round(village)
    
    # 5. Update NPC memory (decay, forgetting, aspiration)
    for npc in village.npcs:
        npc.memory.tick(village.world_state)
    
    # 6. Log emergent phenomena
    log_emergent_phenomena(village)
```

### Grading Criteria

Your village will be evaluated on:

1. **Memory correctness:** NPCs remember interactions with the player correctly (not necessarily perfectly).
2. **Social dynamics:** The village exhibits emergent behavior: factions, feuds, alliances, gossip chains.
3. **NPC individuality:** Each P0 and P1 NPC has a distinct personality reflected in its memory and behavior.
4. **Performance:** The village runs at ≥ 10 ticks/second with 50 NPCs.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.
- There is no traditional reading for this lab — it is a practical exercise.

### Discussion Questions

1. Running the village at 60 in-game days per real hour means relationships evolve quickly. Should the system slow down relationship evolution to maintain realism, or is fast evolution acceptable for a lab?

2. The village has 50 NPCs. At what NPC count do you expect memory to become a bottleneck? How would you scale the system to 500 or 5,000 NPCs?

3. Consider an emergent phenomenon that breaks the intended game experience (e.g., all NPCs form a single faction and refuse to interact with the player). Should the system have safeguards against undesirable emergence?

---

## Lecture 10: Debugging NPC Memory — The Seer's Eye

### The Debugging Challenge

Debugging an NPC memory system is challenging because:
- Hundreds of NPCs each have their own memories, beliefs, and internal state.
- Behavior is emergent — the bug may appear only in specific social configurations.
- Memory corruption may cascade — one NPC's false memory may spread to others via gossip.

### The Seer's Eye

The **Seer's Eye** is a debugging tool that allows developers to inspect NPC memory state at any level of detail:

1. **NPC State Inspector:** View an NPC's complete memory state — all episodic events, relationships, goals, and belief maps.

2. **Gossip Trace:** Track a specific memory as it propagates through the social network. See how its confidence decays, how its valence shifts, how it mutates.

3. **Social Graph Visualizer:** Visualize the emergent faction structure. Who is in which faction? What relationships bridge factions?

4. **Time Travel:** Replay the simulation from any past tick and observe how different random seeds produce different outcomes.

5. **Memory Diff:** Compare two NPCs' memories of the same event. Do they agree? Where do they diverge?

```python
class SeersEye:
    """Debugging tool for NPC memory systems."""
    
    def inspect_npc(self, npc_id: str) -> NPCStateReport:
        """Inspect an NPC's complete memory state."""
        ...
    
    def trace_gossip(self, event_id: str) -> GossipPropagationTrace:
        """Trace a specific memory through the social network."""
        ...
    
    def visualize_social_graph(self) -> str:
        """Visualize the faction structure as a graph image."""
        ...
    
    def rewind_and_replay(self, tick: int, seed: Optional[int] = None) -> SimulationResult:
        """Replay from a specific tick with a different seed."""
        ...
    
    def memory_diff(self, npc_a: str, npc_b: str, topic: str) -> MemoryDiff:
        """Compare two NPCs' memories."""
        ...
```

### Lab 5: Debugging with the Seer's Eye

In this lab, you will use the Seer's Eye to debug your village:

1. Plant a deliberate memory corruption (e.g., an NPC with an incorrect memory).
2. Let the corruption propagate via gossip.
3. Use the Gossip Trace to find the source NPC.
4. Use Time Travel to replay the simulation without the corruption.
5. Use the Social Graph Visualizer to see how factions shift as a result.

### Required Reading

- Zeller, A. (2009). *Why Programs Fail: A Guide to Systematic Debugging*, 2nd Edition. Morgan Kaufmann.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. The Seer's Eye gives developers god-like visibility into NPC minds. But what about players? Should players have access to any debugging tools (e.g., a "detect thoughts" spell that reveals NPC memories)?

2. The Gossip Trace can track a single memory through the social network. But what about misattribution — when an NPC remembers the correct information but attributes it to the wrong source? How should the trace handle this?

3. Time Travel replays from a past tick with a different random seed. This is powerful for debugging but may confuse developers who forget that replays are counterfactual. How should the tool communicate that a replay is a "what if" scenario?

---

## Lecture 11: NPC Memory Migration — When Souls Change Worlds

### The Migration Problem

When a world model is transferred between systems (e.g., from a development server to a production server, or from one game instance to another), the NPCs' memories must be transferred as well. This is the **NPC memory migration** problem.

Migration has several challenges:

1. **Format compatibility:** The target system may use a different memory format (different event schemas, different relationship models).

2. **Identity matching:** An NPC in the source system must be matched to the corresponding NPC in the target system. If the NPC doesn't exist in the target, it must be created.

3. **Memory pruning:** The target system may have different memory budgets, requiring memories to be pruned during migration.

4. **Consistency:** NPC A's memories may reference NPC B's memories. Migration must preserve these references.

### The Migration Protocol

The Mímir Migration Protocol handles NPC memory migration in five steps:

1. **Export:** Serialize the source NPC's memories to a portable format (JSON or MessagePack).
2. **Validate:** Check the exported memories for consistency (all references resolve, all hashes verify).
3. **Transform:** Convert the memories to the target system's format (schema mapping).
4. **Import:** Insert the memories into the target system's storage.
5. **Verify:** Check that the imported memories are consistent and retrievable.

```python
def migrate_npc_memory(npc_id: str, source: WorldModel, 
                      target: WorldModel) -> MigrationReport:
    """Migrate an NPC's full memory from one world model to another."""
    # Step 1: Export
    npc_data = source.export_npc(npc_id)
    
    # Step 2: Validate
    validation = validate_npc_data(npc_data)
    if not validation.valid:
        return MigrationReport(success=False, errors=validation.errors)
    
    # Step 3: Transform
    if source.format_version != target.format_version:
        npc_data = transform_npc_data(npc_data, source.format_version, 
                                     target.format_version)
    
    # Step 4: Import
    target.import_npc(npc_id, npc_data)
    
    # Step 5: Verify
    verification = target.verify_npc_memory(npc_id)
    
    return MigrationReport(success=verification.verified, 
                          warnings=verification.warnings)
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 11.

### Discussion Questions

1. Migration may require memory pruning if the target system has a smaller budget. How should the pruner decide which memories to keep? Should it consult the NPC's own importance assessment (which memories does the NPC consider important)?

2. Format transforms are lossy. Some features of the source system may not exist in the target system. How should the transform handle features that cannot be represented?

3. Consider migrating an NPC that is in the middle of an active goal ("deliver the horseshoes by Friday"). The migration may take several real-time days. How should in-progress goals be handled?

---

## Lecture 12: Each Mind Its Own Well — Course Synthesis and Capstone

### Summary: The Nested Architecture

We began with the Russian doll problem — nested cognition, minds within minds, each with their own memories and beliefs. We end with a comprehensive architecture for NPC memory systems:

- **Personal Episodic Memory** (Lecture 2): Each NPC remembers its own experiences — subjectively, imperfectly, emotionally.
- **Social Relationship Memory** (Lecture 3): Each NPC tracks its bonds to others — friendships, enmities, debts, loves.
- **Goal-State Memory** (Lecture 4): Each NPC pursues its own goals — survival, vocation, social connection, aspiration.
- **Memory Decay and Forgetting** (Lecture 5): Each NPC forgets and misremembers — creating realistic imperfection.
- **Theory of Mind** (Lecture 6): Each NPC models what others know, believe, and intend — enabling lies, teaching, and coordination.
- **Emergent Social Dynamics** (Lecture 7): From individual memories emerge collective phenomena — gossip, factions, feuds.
- **Memory Economy** (Lecture 8): Resources are allocated to NPCs based on priority and player interaction.
- **The Village Lab** (Lecture 9): A sandbox for building and observing emergent NPC behavior.
- **Debugging** (Lecture 10): The Seer's Eye gives developers visibility into NPC minds.
- **Migration** (Lecture 11): NPCs can be transferred between worlds without losing their memories.

Each NPC is its own well of memory — a Mímir in miniature, drinking from its own stream of experience. And from thousands of individual wells, the world draws its life.

### Capstone Project: The Living Village

Your capstone is to build a complete living village with NPC memory systems:

1. **50 NPCs** with full memory systems (episodic, social, goal, belief).
2. **Shared infrastructure** (tavern, market, temple, farms) with spatial awareness.
3. **Gossip propagation** with confidence decay and emotional shift.
4. **Faction detection** with at least two emergent factions.
5. **Player interaction** — the player can interact with any NPC and the interaction persists in NPC memory.
6. **Time acceleration** — the village runs at ≥ 5 ticks/second for at least 100 in-game days.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with type hints and docstrings).
2. Village simulation output for 100 in-game days.
3. Social graph visualization showing emergent factions.
4. Player interaction logs showing NPC memory persistence.
5. A design document (5–8 pages) describing your NPC memory architecture.

### The Well of Many Waters

Mímir's Well is not one well. It is many. Each NPC is a well of its own, drinking from its own stream of experience. And from the many wells, the world draws its depth.

**ᛗ Mannaz — Humanity. Each mind is a world.**
**ᛚ Laguz — Water. Each memory is a stream.**
**ᛞ Dagaz — Awakening. Each interaction is a new dawn.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᛗ — Each mind its own well. The world drinks from all.*