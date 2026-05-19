# WM207 — Spatial, Temporal, and Causal Reasoning
## The Three Rivers of Yggdrasil

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Two, Semester Two

**Instructor:** Dr. Hvergelmir Vandráðrson, Professor of Multimodal Reasoning
**Office:** Mímisbrunnr Hall 201 | **Hours:** Tuesdays 14:00–16:00

---

## Course Description

The three rivers that water Yggdrasil's roots are spatial, temporal, and causal. This course trains students in the three fundamental reasoning modalities of world modeling: *Spatial reasoning* (where things are, how they relate geometrically, navigation); *Temporal reasoning* (when things happen, duration, sequence, concurrency); and *Causal reasoning* (why things happen, counterfactual assessment, intervention logic). Students build integrated reasoning modules that allow an agent to answer "what if" questions about the simulated world. Heavy mathematics: topology, temporal logic, and Pearl's causal calculus.

---

## Lecture 1: The Three Rivers — Introduction to Multimodal Reasoning

### The Roots of Yggdrasil

In Norse mythology, three wells water the roots of Yggdrasil:

- **Urðarbrunnr** (Well of Urð): The well of the past. The Norns draw from it to weave what has become. This is **temporal reasoning** — understanding when events happen, how they sequence, and how the past constrains the present.

- **Mímisbrunnr** (Well of Mímir): The well of wisdom. Óðinn sacrificed an eye to drink from it. This is **causal reasoning** — understanding why events happen, which causes produce which effects, and what would change under intervention.

- **Hvergelmir** (The Roaring Well): The well that feeds all rivers. Níðhöggr gnaws at its root. This is **spatial reasoning** — understanding where things are, how space is structured, and how objects navigate through it.

These three wells correspond to the three fundamental modalities of reasoning about a world:

- **Where** (Hvergelmir): Spatial — topology, geometry, navigation, distance.
- **When** (Urðarbrunnr): Temporal — sequence, duration, concurrency, change.
- **Why** (Mímisbrunnr): Causal — mechanisms, counterfactuals, interventions, explanation.

### The Integration Challenge

Each modality alone is well-understood. Spatial reasoning has centuries of geometry and topology behind it. Temporal reasoning has temporal logics and process calculi. Causal reasoning has Pearl's do-calculus and Rubin's potential outcomes.

The challenge of this course is **integration**: building a reasoning module that seamlessly combines all three modalities. An agent must answer questions like:

- "Where was the fire when Rurik entered the building?" (Spatial + Temporal)
- "Why did the fire spread to the northern wing?" (Spatial + Causal)
- "If Rurik had entered 5 minutes earlier, would he have survived?" (Temporal + Causal + Spatial — the fire would have been smaller because it hadn't reached the exit yet)

These integrated questions require a unified framework that can reason across all three dimensions simultaneously.

### Course Roadmap

- **Lectures 1–3:** Spatial reasoning (the Hvergelmir stream).
- **Lectures 4–6:** Temporal reasoning (the Urðarbrunnr stream).
- **Lectures 7–9:** Causal reasoning (the Mímisbrunnr stream).
- **Lectures 10–11:** Integration — the Three Rivers Confluence.
- **Lecture 12:** Capstone.

### Required Reading

- Pearl, J. & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*. Basic Books.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12: "The Three Rivers: Spatial, Temporal, and Causal Reasoning." University of Yggdrasil Press.

### Discussion Questions

1. The three rivers correspond to three questions (Where, When, Why). Are there other fundamental reasoning modalities? What about "How" (mechanistic reasoning) or "Who" (attributional reasoning)?

2. Consider the question: "If Rurik had entered the building 5 minutes earlier, would he have survived?" This requires all three modalities. Which one is most critical for this question? Why?

3. The Norse mythological mapping assigns spatial reasoning to Hvergelmir (the well that feeds all rivers). Why is spatial reasoning the "source" of all rivers? What does this imply about the primacy of space in world modeling?

---

## Lecture 2: Spatial Reasoning — Topology and Place

### The Geography of a World Model

A world model is, first and foremost, a model of space. Things have locations. Locations have topology (rooms are connected by doors, regions are connected by roads). Topology determines what is *adjacent*, *contained*, *reachable*, and *distant*.

The spatial substrate of a world model consists of:

1. **Locations:** Point-like positions in space. A location has coordinates (in a continuous space) or a label (in a discrete space like a building layout).
2. **Regions:** Collections of locations with shared properties. A region may be a room, a building, a district, or a biome.
3. **Connections:** Pairs of locations that are directly connected. A door connects two rooms. A road connects two towns.
4. **Barriers:** Pairs of locations that are separated by an impassable boundary. A wall separates rooms. A cliff separates levels.

### The Spatial Graph

The spatial substrate is represented as a **labeled directed graph**:

```
    ┌──────────┐         ┌──────────┐
    │  Market   │◄───────│  Tavern   │
    │  Square   │  door  │          │
    └────┬─────┘         └──────────┘
         │ road                │ door
    ┌────┴─────┐         ┌──┴────────┐
    │  Smithy  │         │  Temple   │
    │          │─────────│          │
    └──────────┘  wall    └──────────┘
         │                           │
    ┌────┴─────┐              ┌─────┴───┐
    │ Farmland │              │ Forest  │
    └──────────┘              └─────────┘
```

Each edge has a label (door, road, wall, path) and a weight (distance, traversal time, difficulty).

### Spatial Queries

The spatial graph supports several types of queries:

1. **Location query:** "Where is Rurik?" → Return the node containing Rurik.
2. **Path query:** "How does Rurik get from the Smithy to the Temple?" → Return the shortest path.
3. **Reachability query:** "Can Rurik reach the Forest?" → Return True/False.
4. **Proximity query:** "What is near Rurik?" → Return all entities within distance D.
5. **Containment query:** "Is the Smithy in the Village?" → Return True/False (transitive containment).

```python
class SpatialReasoner:
    """Spatial reasoning engine for world models."""
    
    def __init__(self, spatial_graph: nx.Graph):
        self.graph = spatial_graph
    
    def find_path(self, from_location: str, to_location: str) -> List[str]:
        """Find shortest path between two locations."""
        try:
            return nx.shortest_path(self.graph, from_location, to_location, weight="weight")
        except nx.NetworkXNoPath:
            return []  # Unreachable
    
    def find_reachable(self, from_location: str, max_distance: float) -> Set[str]:
        """Find all locations within max_distance."""
        distances = nx.single_source_dijkstra_path_length(
            self.graph, from_location, cutoff=max_distance, weight="weight"
        )
        return set(distances.keys())
    
    def find_nearby_entities(self, location: str, entity_index: Dict[str, str], 
                            max_distance: float) -> Dict[str, float]:
        """Find all entities near a location."""
        reachable = self.find_reachable(location, max_distance)
        nearby = {}
        for entity, entity_loc in entity_index.items():
            if entity_loc in reachable:
                nearby[entity] = reachable[entity_loc]
        return nearby
```

### Required Reading

- Kuipers, B. (2000). "The Spatial Semantic Hierarchy." *Artificial Intelligence*, 119(1), 191–233.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The spatial graph uses discrete locations (nodes) and connections (edges). But real space is continuous. How should the model handle continuous space — e.g., NPC movement within a room?

2. The spatial graph is static (locations and connections don't change). But in a dynamic world, buildings are destroyed, roads are blocked, walls are breached. How should the spatial graph handle dynamic topology?

3. Proximity queries ("What is near Rurik?") depend on the distance metric. Should "distance" be physical (Euclidean), temporal (time to traverse), or subjective (perceived distance based on familiarity)?

---

## Lecture 3: Spatial Reasoning — Navigation and the Hvergelmir Stream

### Pathfinding in the World

Navigation is the most fundamental spatial reasoning task: given a start location and a goal location, find the best path. "Best" may mean shortest, fastest, safest, or most scenic — the optimization criterion depends on the NPC's goals and constraints.

### A* Navigation with World Awareness

The A* algorithm is the standard pathfinding algorithm. But for world models, A* must be extended to consider world-specific costs:

- **Danger:** Paths through dangerous areas (fire, enemies, traps) have higher cost.
- **Difficulty:** Paths through difficult terrain (mountains, swamps, deep snow) have higher cost.
- **Social cost:** Paths through unfriendly territory (enemy factions, restricted areas) have higher cost.
- **Emotion:** NPCs with phobias (fear of water, fear of heights) assign higher cost to triggering paths.

```python
class WorldAwareNavigator:
    """A* navigation with world-specific costs."""
    
    def __init__(self, spatial_graph: nx.Graph, world_state: WorldState):
        self.graph = spatial_graph
        self.world = world_state
    
    def navigate(self, start: str, goal: str, 
                npc: NPC) -> NavigationResult:
        """Find the best path for an NPC considering world costs."""
        
        def heuristic(node: str) -> float:
            """Heuristic: Euclidean distance to goal."""
            return self.graph.nodes[node].get("distance_to_goal", 0)
        
        def edge_cost(node_a: str, node_b: str) -> float:
            """Edge cost considering world state and NPC preferences."""
            # Base cost: traversal time
            base = self.graph[node_a][node_b].get("weight", 1.0)
            
            # Danger cost
            danger = self.world.get_danger_level(node_b)
            
            # Difficulty cost
            difficulty = self.world.get_difficulty(node_b, npc)
            
            # Social cost
            social = self.world.get_social_cost(node_b, npc)
            
            # Emotional cost
            emotional = npc.get_emotional_cost(node_b)
            
            return base * (1 + danger + difficulty + social + emotional)
        
        path = nx.astar_path(self.graph, start, goal, 
                            heuristic=heuristic, weight=edge_cost)
        
        return NavigationResult(
            path=path,
            total_cost=sum(edge_cost(path[i], path[i+1]) for i in range(len(path)-1)),
            estimated_time=self._estimate_time(path)
        )
```

### Spatial Reasoning Beyond Navigation

Navigation is just one aspect of spatial reasoning. Other spatial reasoning tasks include:

1. **Area estimation:** "How large is the burning region?" (Important for evacuation planning.)
2. **Line-of-sight calculation:** "Can Rurik see the fire from the market square?" (Important for NPC perception.)
3. **Spatial containment reasoning:** "Is the village inside the valley?" (Important for environmental effects.)
4. **Spatial change reasoning:** "The river has flooded — which locations are now submerged?" (Important for dynamic world events.)

### Lab 1: Building a Spatial Model

In this lab, you will build a spatial model of a village:

1. Define 15+ locations with coordinates and connections.
2. Assign properties to locations (danger level, difficulty, social faction).
3. Implement A* navigation with world-aware costs.
4. Test navigation with different NPCs (brave guard, frightened child, merchant avoiding enemies).

### Required Reading

- Russell, S. & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*, 4th Edition. Pearson. Chapter 3: "Solving Problems by Searching."
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The world-aware navigator uses world state (danger levels, faction territories) to compute edge costs. But world state changes over time. How should the navigator handle path costs that change during traversal (e.g., a fire spreads while the NPC is walking)?

2. Emotional costs (phobias, preferences) are NPC-specific. Should pathfinding compute a unique path for each NPC, or can NPCs share paths computed for a "generic" traveler?

3. Consider an NPC that must navigate through a dangerous area. The optimal path avoids the danger but takes 10× longer. The dangerous path is short but risky. How should the NPC decide? What is the "rational" choice?

---

## Lecture 4: Temporal Reasoning — Sequence and Duration

### The Flow of Ticks

In a world model, time advances in discrete ticks. Each tick, the world state updates: NPCs move, fires spread, relationships evolve, weather changes. Temporal reasoning is the ability to understand and answer questions about this flow of ticks.

The fundamental concepts of temporal reasoning:

- **Events:** Things that happen at specific times. `fire_started(t=100)`.
- **Fluents:** Properties that hold over intervals. `burning(building, t=100..200)`.
- **Sequences:** Ordered sets of events. `fire_started → citizen_entered → citizen_damaged → citizen_died`.
- **Durations:** Lengths of intervals. `burning lasted 100 ticks`.
- **Concurrency:** Events that happen simultaneously or overlap. `fire_burning AND citizen_entering`.

### Interval Temporal Logic

The standard formalism for temporal reasoning is **interval temporal logic** (ITL), which reasons about time intervals rather than time points:

```
[α] φ  — φ holds throughout interval α
⟨α⟩ φ  — φ holds at some point during interval α
α ; β   — interval α is followed by interval β
α ∥ β   — intervals α and β overlap
α ⊂ β   — interval α is contained within interval β
```

These operators allow us to express temporal properties:

- "The fire was burning throughout the entire time Rurik was in the building": `[rurik_in_building] fire_burning`
- "At some point during the fire, Sigrún entered the market": `⟨fire⟩ sigrun_in_market`
- "After the fire started, the building collapsed": `fire_started ; building_collapsed`

### The Temporal Reasoning Engine

```python
class TemporalReasoner:
    """Temporal reasoning engine for world models."""
    
    def __init__(self, event_log: EventLog):
        self.event_log = event_log
    
    def query(self, temporal_formula: TemporalFormula) -> bool:
        """Evaluate a temporal formula against the event log."""
        
        if isinstance(temporal_formula, Throughout):
            # [α] φ — φ holds throughout interval α
            interval = self.resolve_interval(temporal_formula.interval)
            for tick in range(interval.start, interval.end + 1):
                if not self.evaluate_at(temporal_formula.predicate, tick):
                    return False
            return True
        
        elif isinstance(temporal_formula, Sometime):
            # ⟨α⟩ φ — φ holds at some point during interval α
            interval = self.resolve_interval(temporal_formula.interval)
            for tick in range(interval.start, interval.end + 1):
                if self.evaluate_at(temporal_formula.predicate, tick):
                    return True
            return False
        
        elif isinstance(temporal_formula, Sequence):
            # α ; β — α is followed by β
            interval_a = self.resolve_interval(temporal_formula.interval_a)
            interval_b = self.resolve_interval(temporal_formula.interval_b)
            return interval_a.end < interval_b.start
        
        elif isinstance(temporal_formula, Overlap):
            # α ∥ β — α and β overlap
            interval_a = self.resolve_interval(temporal_formula.interval_a)
            interval_b = self.resolve_interval(temporal_formula.interval_b)
            return (interval_a.start <= interval_b.end and 
                   interval_b.start <= interval_a.end)
```

### Required Reading

- Allen, J. (1983). "Maintaining Knowledge about Temporal Intervals." *Communications of the ACM*, 26(11), 832–843.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. Interval temporal logic uses intervals, not points. But some events are instantaneous (a lightning strike). Should the system represent instantaneous events as zero-length intervals, or as a separate type of temporal object?

2. The temporal reasoner evaluates formulas against the event log. But the event log only contains events that actually happened. How should the system evaluate counterfactual temporal formulas ("If the fire hadn't started, the building wouldn't have collapsed")?

3. Consider two concurrent events: "Rurik entered the building" and "The fire spread to the second floor." Should concurrency be represented as exact overlap, or as "within N ticks of each other"?

---

## Lecture 5: Temporal Reasoning — Concurrency, Persistence, and Change

### The Persistence Problem

Not all properties change every tick. A building that is burning at tick T is likely still burning at tick T+1. This is the **persistence problem** — the problem of inferring that a property that held at some past time still holds, unless there is evidence to the contrary.

The default assumption in temporal reasoning is **frame axiom**: properties persist unless explicitly changed by an event. This is also known as the **commonsense law of inertia**:

```
burning(building, T+1) ← burning(building, T), ¬extinguished(building, T+1)
```

"In English: the building is burning at T+1 if it was burning at T and was not extinguished between T and T+1."

### The Qualification Problem

Properties persist unless qualified by exceptions:

- A building is burning unless it is extinguished.
- A citizen is alive unless they die.
- A door is open unless it is closed.

But the qualifications are often numerous and hard to enumerate completely. This is the **qualification problem** — the difficulty of listing all the exceptions to a persistence rule.

The world model handles the qualification problem through **negation as failure**: if there is no explicit evidence that the building was extinguished, assume it is still burning. This is pragmatically sound but logically incomplete — there may be extinguishing events that the model doesn't know about.

### Concurrency and Synchronization

When multiple events happen simultaneously, the world model must decide their **interleaving** — the order in which they are processed:

- **Sequential interleaving:** Events are processed one at a time, in some order. The order may matter (if A and B both affect the same entity).
- **True concurrency:** Events are processed simultaneously, with conflicts resolved by conflict rules (priority, randomization, or domain logic).
- **Transactional concurrency:** Events are grouped into transactions that are processed atomically. Conflicts within a transaction are resolved by the transaction's rules.

```python
class ConcurrencyManager:
    """Manage concurrent events in the world model."""
    
    def process_tick(self, events: List[Event], world: WorldState):
        """Process events for a single tick, handling concurrency."""
        
        # Group events by affected entity
        entity_groups = defaultdict(list)
        for event in events:
            for entity in event.affected_entities():
                entity_groups[entity].append(event)
        
        # Process entities with no conflicts (single event)
        for entity, group in entity_groups.items():
            if len(group) == 1:
                group[0].apply(world)
        
        # Process entities with conflicts (multiple events)
        for entity, group in entity_groups.items():
            if len(group) > 1:
                resolved = self.resolve_conflict(entity, group, world)
                resolved.apply(world)
    
    def resolve_conflict(self, entity: str, events: List[Event], 
                        world: WorldState) -> Event:
        """Resolve concurrent events affecting the same entity."""
        # Priority-based conflict resolution
        events_sorted = sorted(events, key=lambda e: e.priority, reverse=True)
        return events_sorted[0]  # Highest priority wins
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.
- Shanahan, M. (1997). *Solving the Frame Problem: A Mathematical Investigation of the Common Sense Law of Inertia*. MIT Press.

### Discussion Questions

1. The frame axiom assumes persistence unless explicitly changed. But what about gradual change? A fire doesn't just burn or not-burn — it gets stronger or weaker. How should persistence handle continuous change?

2. Negation as failure is pragmatically useful but logically incomplete. Should the world model include an explicit "closed-world assumption" — the statement that anything not known is false? Or should it maintain a third truth value: unknown?

3. Consider two concurrent events: "Rurik opens the door" and "Sigrún closes the door." Sequential interleaving gives different results depending on order. True concurrency gives undefined results. How should the world model handle this specific conflict?

---

## Lecture 6: The Urðarbrunnr Stream — Temporal Reasoning for World Models

### Temporal Queries in the World

The Urðarbrunnr Stream — the temporal reasoning layer of the Three Rivers architecture — answers questions about time:

- **When:** "When did the fire start?" → T=100
- **How long:** "How long was Rurik in the burning building?" → 10 ticks
- **Before/After:** "Did Rurik enter the building before the fire started?" → No (fire started first)
- **During:** "Was the fire still burning when Sigrún arrived?" → Yes
- **Concurrency:** "Were Rurik and Sigrún in the building at the same time?" → No (they overlapped by only 2 ticks, below the concurrency threshold)

### The Temporal Query Language

The Urðarbrunnr Stream provides a query language for temporal reasoning:

```
WHEN (fire_started)                                    → T=100
DURATION (burning(building))                            → [T=100, T=200] = 100 ticks
BEFORE (rurik_entered, fire_started)                    → False
AFTER (fire_started, rurik_entered)                     → True
DURING (sigrun_arrived, burning(building))              → True
OVERLAP (rurik_in_building, sigrun_in_building)         → False (overlap < threshold)
```

### Temporal Reasoning in the Agent

The agent uses temporal reasoning in two ways:

1. **Proactive:** The agent reasons about future events. "If I enter the building now, I will be in the fire for at least 5 ticks." This forward reasoning helps the agent plan.

2. **Reactive:** The agent reasons about past events. "The fire started at T=100, and Rurik entered at T=105. Rurik was in the building for 5 ticks before the fire spread to his location (T=110)." This backward reasoning explains events.

```python
class UrdrStream:
    """Temporal reasoning layer — the Urðarbrunnr Stream."""
    
    def __init__(self, event_log: EventLog):
        self.event_log = event_log
        self.temporal_reasoner = TemporalReasoner(event_log)
    
    def when(self, event: str) -> List[int]:
        """When did this event happen?"""
        return self.event_log.find_event_times(event)
    
    def duration(self, fluent: str) -> List[Interval]:
        """How long did this fluent hold?"""
        return self.event_log.find_fluent_intervals(fluent)
    
    def before(self, event_a: str, event_b: str) -> bool:
        """Did event_a happen before event_b?"""
        times_a = self.when(event_a)
        times_b = self.when(event_b)
        return any(a < b for a in times_a for b in times_b)
    
    def during(self, event_a: str, fluent_b: str) -> bool:
        """Did event_a happen during fluent_b?"""
        times_a = self.when(event_a)
        intervals_b = self.duration(fluent_b)
        return any(
            interval.start <= t <= interval.end 
            for t in times_a for interval in intervals_b
        )
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.
- Allen, J. (1983). "Maintaining Knowledge about Temporal Intervals." *Communications of the ACM*, 26(11), 832–843.

### Discussion Questions

1. The Urðarbrunnr Stream uses the event log as its primary data source. But the event log may be incomplete (some events are not logged). How should the stream handle temporal queries about missing events?

2. Temporal queries return exact answers ("Rurik was in the building for exactly 10 ticks"). But in a world model with imprecise timestamps, answers may have uncertainty. How should the stream represent and communicate temporal uncertainty?

3. The OVERLAP query requires a threshold (how much overlap counts as "concurrent"). What is the right threshold for a world model? Should it be configurable per entity type?

---

## Lecture 7: Causal Reasoning — Mechanisms and Counterfactuals

### The Mímisbrunnr Stream

The Mímisbrunnr Stream — the causal reasoning layer — answers questions about why things happen and what would have happened otherwise. It draws from Pearl's structural causal models and the do-calculus.

### Structural Causal Models

A **structural causal model** (SCM) consists of:

1. **Endogenous variables:** Variables determined within the model (e.g., `fire_damage`, `building_status`, `citizen_health`).
2. **Exogenous variables:** Variables determined outside the model (e.g., `lightning_strike`, `player_action`).
3. **Structural equations:** Functions mapping causes to effects (e.g., `fire_damage = fire_intensity × exposure_time - fire_resistance`).
4. **Graph:** A directed acyclic graph (DAG) showing which variables causally influence which others.

```python
class StructuralCausalModel:
    """Pearl's structural causal model for world reasoning."""
    
    def __init__(self):
        self.equations = {}   # Variable → structural equation
        self.graph = nx.DiGraph()  # Causal graph
    
    def add_equation(self, variable: str, equation: Callable, 
                   parents: List[str]):
        """Add a structural equation for a variable."""
        self.equations[variable] = equation
        for parent in parents:
            self.graph.add_edge(parent, variable)
    
    def compute(self, exogenous: Dict[str, Any]) -> Dict[str, Any]:
        """Compute all endogenous variables from exogenous inputs."""
        # Topological sort ensures parents are computed before children
        result = dict(exogenous)
        for variable in nx.topological_sort(self.graph):
            if variable in self.equations and variable not in result:
                parent_values = {p: result[p] for p in self.graph.predecessors(variable)}
                result[variable] = self.equations[variable](**parent_values)
        return result
    
    def intervene(self, variable: str, value: Any, 
                 exogenous: Dict[str, Any]) -> Dict[str, Any]:
        """The do-operator: set a variable to a value and recompute."""
        # Remove all incoming edges to the intervened variable
        modified_graph = self.graph.copy()
        for parent in list(self.graph.predecessors(variable)):
            modified_graph.remove_edge(parent, variable)
        
        # Set the variable to its new value
        result = dict(exogenous)
        result[variable] = value  # Intervention
        
        # Recompute all descendants
        for var in nx.topological_sort(modified_graph):
            if var in self.equations and var != variable:
                parent_values = {p: result[p] for p in modified_graph.predecessors(var)}
                result[var] = self.equations[var](**parent_values)
        
        return result
```

### The Do-Calculus

The do-operator `do(X = x)` represents an **intervention** — setting variable X to value x regardless of its natural causes. This is different from conditioning on `X = x` (which is observation).

- **Observation:** "Given that Rurik was in the burning building, what is the probability he took damage?" This conditions on Rurik's location — it accounts for the selection bias.
- **Intervention:** "If we force Rurik to be in the burning building, what is the probability he takes damage?" This sets Rurik's location — it removes the selection bias.

The do-calculus provides rules for manipulating causal expressions:

1. **Insertion/deletion:** `P(Y | do(X=x))` can be computed from the modified graph where all incoming edges to X are removed.
2. **Action/observation exchange:** Under certain conditions, `do(X=x)` can be replaced by conditioning on `X=x`.
3. **Counterfactuals:** Given evidence and an intervention, what would have happened?

### Required Reading

- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*, 2nd Edition. Cambridge University Press.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The do-operator requires knowing the causal graph. But in many world models, the causal graph is not fully known (some causal relationships are discovered during gameplay). How should the system handle unknown causal relationships?

2. Consider the causal chain: `lightning → fire → Rurik damage`. If we intervene on `fire` (set fire to not happening), the lightning still occurs. But if we intervene on `lightning` (set lightning to not happening), the fire doesn't occur either. The system must distinguish between intervening on a cause and intervening on an effect. How is this handled?

3. Counterfactuals require computing what would have happened under a different set of circumstances. But the world model may have randomness (e.g., dice rolls). How should counterfactuals handle stochastic variables?

---

## Lecture 8: Causal Reasoning — Interventions and the Do-Calculus in Practice

### Interventions in the World Model

The Mímisbrunnr Stream implements the do-calculus for world model reasoning. When the system asks "What would happen if we intervened on variable X?", it uses the `intervene` method to compute the counterfactual world:

```python
class MimisbrunnrStream:
    """Causal reasoning layer — the Mímisbrunnr Stream."""
    
    def __init__(self, scm: StructuralCausalModel):
        self.scm = scm
    
    def why(self, effect: str, world_state: Dict) -> CausalExplanation:
        """Why did this effect occur? Return the causal explanation."""
        # Find all direct causes of the effect
        direct_causes = list(self.scm.graph.predecessors(effect))
        
        # For each direct cause, compute its contribution
        contributions = {}
        for cause in direct_causes:
            # Counterfactual: what if this cause had its default value?
            default_value = self.scm.equations[cause].default
            counterfactual_state = self.scm.intervene(cause, default_value, world_state)
            contribution = world_state[effect] - counterfactual_state[effect]
            contributions[cause] = contribution
        
        return CausalExplanation(
            effect=effect,
            direct_causes=direct_causes,
            contributions=contributions,
            total=sum(contributions.values())
        )
    
    def what_if(self, intervention: Dict[str, Any], 
               world_state: Dict) -> CounterfactualResult:
        """What would happen if we intervened?"""
        result = self.scm.intervene(
            variable=list(intervention.keys())[0],
            value=list(intervention.values())[0],
            exogenous=world_state
        )
        return CounterfactualResult(
            intervention=intervention,
            counterfactual_state=result
        )
```

### Answering Causal Questions

The Mímisbrunnr Stream can answer several types of causal questions:

1. **Why?** "Why did Rurik take 50 damage?" → Because the building was burning (5 damage/tick × 10 ticks), and he had no fire resistance.
2. **What if?** "What if Rurik had a fire resistance potion?" → He would take only 25 damage (5 × 10 × 0.5) and survive his 45 HP.
3. **Because?** "Because of what?" → Because the lightning struck the building (established the fire) AND Rurik entered the building (created the exposure).
4. **Despite?** "Despite what?" → Despite his high HP (45), he died because the total damage exceeded it.

### Lab 2: Building a Causal Model

In this lab, you will build a structural causal model for a village:

1. Define 10 endogenous variables and 5 exogenous variables.
2. Write structural equations for each endogenous variable.
3. Draw the causal DAG.
4. Implement the `compute`, `intervene`, and `why` methods.
5. Answer 5 causal questions and 3 counterfactual questions.

### Required Reading

- Pearl, J. (2009). *Causality*, Chapter 3: "Interventions."
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The `why` method returns direct causes. But important causes may be indirect (distant in the DAG). Should the system trace causal chains to a specified depth? How deep should it go?

2. Counterfactuals require re-computing the entire world state from the point of intervention. For large world models, this is expensive. How can counterfactual computation be optimized?

3. The `what_if` method allows single-variable interventions. What about multi-variable interventions ("What if there were no fire AND Rurik had fire resistance?")? How should the system handle joint interventions?

---

## Lecture 9: Causal Discovery — Learning Causal Structure from Data

### When the Graph Is Unknown

In some world models, the causal graph is given (the designer specifies the rules). In others, the causal structure must be **learned from data** — observing the world and inferring which variables causally influence which others.

Causal discovery algorithms attempt to reconstruct the causal DAG from observational data:

1. **Constraint-based methods (PC algorithm):** Test for conditional independence between variables. If X and Y are conditionally independent given Z, there is no direct causal edge between X and Y.

2. **Score-based methods (GES):** Search over possible DAG structures and score them by how well they fit the data. The highest-scoring DAG is the best causal model.

3. **Functional causal model methods (LiNGAM):** Assume that causal relationships are linear and non-Gaussian. Exploit the asymmetry of cause and effect to determine direction.

```python
class CausalDiscovery:
    """Discover causal structure from observational data."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def pc_algorithm(self, alpha: float = 0.05) -> nx.DiGraph:
        """PC algorithm: constraint-based causal discovery."""
        # Step 1: Start with a complete undirected graph
        variables = list(self.data.columns)
        graph = nx.Graph()
        graph.add_nodes_from(variables)
        graph.add_edges_from([(i, j) for i in variables for j in variables if i < j])
        
        # Step 2: Remove edges where variables are conditionally independent
        depth = 0
        while True:
            removed = False
            for edge in list(graph.edges()):
                x, y = edge
                # Find conditioning set of size 'depth'
                neighbors = [n for n in graph.neighbors(x) if n != y]
                for conditioning_set in combinations(neighbors, depth):
                    if self._conditionally_independent(x, y, conditioning_set, alpha):
                        graph.remove_edge(x, y)
                        removed = True
                        break
            depth += 1
            if not removed:
                break
        
        # Step 3: Orient edges using v-structures and acyclicity
        return self._orient_edges(graph)
    
    def _conditionally_independent(self, x: str, y: str, 
                                   z: List[str], alpha: float) -> bool:
        """Test conditional independence using partial correlation."""
        # Simplified: use partial correlation test
        from scipy import stats
        resid_x = self._partial_residual(x, z)
        resid_y = self._partial_residual(y, z)
        corr = np.corrcoef(resid_x, resid_y)[0, 1]
        n = len(self.data)
        t_stat = corr * np.sqrt(n - len(z) - 2) / np.sqrt(1 - corr**2)
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - len(z) - 2))
        return p_value > alpha
```

### Required Reading

- Spirtes, P., Glymour, C. & Scheines, R. (2000). *Causation, Prediction, and Search*, 2nd Edition. MIT Press.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The PC algorithm assumes no confounders — variables that cause both X and Y but are not measured. How should the system handle unmeasured confounders?

2. Causal discovery from observational data can only determine the causal graph up to Markov equivalence — some DAGs are indistinguishable from data alone. How should the system communicate this uncertainty?

3. The PC algorithm tests conditional independence using partial correlations. But partial correlations assume linear relationships. How should the system handle nonlinear causal relationships?

---

## Lecture 10: Three Rivers Confluence — Integrating Spatial, Temporal, and Causal Reasoning

### The Confluence

The Three Rivers — spatial (Hvergelmir), temporal (Urðarbrunnr), and causal (Mímisbrunnr) — meet at the base of Yggdrasil. In the world model, they meet in the **Confluence Engine**, which integrates all three reasoning modalities:

```
           ┌───────────────┐
           │  Confluence   │
           │  Engine       │
           └───┬─────┬─────┘
               │     │     │
    ┌──────────┘     │     └──────────┐
    │                │                │
┌───┴────┐    ┌─────┴─────┐    ┌─────┴─────┐
│Spatial │    │ Temporal   │    │  Causal   │
│Reasoner│    │ Reasoner   │    │  Reasoner │
│(Hvrglmr)│    │(Urðarbrnnr)│    │(Mímisbrnnr)│
└─────────┘    └───────────┘    └───────────┘
```

### Integrated Queries

The Confluence Engine answers queries that span all three modalities:

**Query:** "Why is the village square empty?"

- **Spatial:** The village square is at coordinates (0, 0). The tavern, smithy, and market are adjacent. (Where is the square?)
- **Temporal:** The fire started at T=100. The evacuation order was issued at T=102. The square was evacuated by T=105. (When did it become empty?)
- **Causal:** The fire → evacuation order → square evacuation. (Why did it become empty?)

The Confluence Engine composes these three answers into a single integrated explanation:

> "The village square (at the center of the village, adjacent to the tavern, smithy, and market) is currently empty because a fire started in the smithy at T=100, which triggered an evacuation order at T=102, and by T=105 all citizens had left the square for the safety of the temple and farmlands."

### Implementation

```python
class ConfluenceEngine:
    """Integrate spatial, temporal, and causal reasoning."""
    
    def __init__(self, spatial: SpatialReasoner, temporal: TemporalReasoner,
                causal: StructuralCausalModel):
        self.spatial = spatial
        self.temporal = temporal
        self.causal = MimisbrunnrStream(causal)
    
    def answer_integrated_query(self, query: IntegratedQuery) -> IntegratedAnswer:
        """Answer a query that spans spatial, temporal, and causal modalities."""
        
        # Decompose the query into sub-queries
        sub_queries = self.decompose(query)
        
        # Answer each sub-query with the appropriate reasoner
        answers = {}
        for sub in sub_queries:
            if sub.modality == "spatial":
                answers[sub.id] = self.spatial.answer(sub)
            elif sub.modality == "temporal":
                answers[sub.id] = self.temporal.answer(sub)
            elif sub.modality == "causal":
                answers[sub.id] = self.causal.answer(sub)
        
        # Compose the sub-answers into an integrated answer
        return self.compose(query, answers)
    
    def decompose(self, query: IntegratedQuery) -> List[SubQuery]:
        """Decompose an integrated query into modality-specific sub-queries."""
        sub_queries = []
        
        # Extract spatial components
        if query.spatial_component:
            sub_queries.append(SubQuery(
                modality="spatial", 
                question=query.spatial_component
            ))
        
        # Extract temporal components
        if query.temporal_component:
            sub_queries.append(SubQuery(
                modality="temporal", 
                question=query.temporal_component
            ))
        
        # Extract causal components
        if query.causal_component:
            sub_queries.append(SubQuery(
                modality="causal", 
                question=query.causal_component
            ))
        
        return sub_queries
    
    def compose(self, query: IntegratedQuery, 
               answers: Dict[str, Any]) -> IntegratedAnswer:
        """Compose sub-answers into an integrated answer."""
        # The composition strategy depends on the query type
        # For "why" queries: causal answer is primary, spatial and temporal provide context
        # For "where" queries: spatial answer is primary, temporal and causal provide context
        # For "when" queries: temporal answer is primary, spatial and causal provide context
        
        if query.type == "why":
            primary = answers.get("causal", "Unknown")
            context_spatial = answers.get("spatial", "")
            context_temporal = answers.get("temporal", "")
            return IntegratedAnswer(
                primary=primary,
                context=f"({context_spatial}; {context_temporal})"
            )
        # ... other query types
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why*, Chapters 7–9.

### Discussion Questions

1. The Confluence Engine decomposes queries into modality-specific sub-queries. But some queries are inherently cross-modal — they cannot be cleanly separated. ("Why is Rurik in the burning building?" involves spatial reasoning (where is the building?), temporal reasoning (when did he enter?), and causal reasoning (why did he enter?).) How should the engine handle inseparable queries?

2. The composition strategy depends on the query type (why, where, when). But what about mixed queries ("Why is the village square empty at noon?" — both why and when)? Should the primary modality be determined by the query's focus, or should all modalities be presented equally?

3. The Confluence Engine currently answers queries about the actual world. What about counterfactual queries ("What if the smithy were on the north side of the village?" — a spatial counterfactual)? How should spatial, temporal, and causal counterfactuals interact?

---

## Lecture 11: The Three Rivers API and Performance — Where, When, Why at Scale

### The Three Rivers Service

The Confluence Engine is exposed as a REST service:

```python
class ThreeRiversService:
    """The Three Rivers reasoning service."""
    
    def spatial_query(self, world_id: str, query: str) -> SpatialResult:
        """Answer a spatial query."""
        ...
    
    def temporal_query(self, world_id: str, query: str) -> TemporalResult:
        """Answer a temporal query."""
        ...
    
    def causal_query(self, world_id: str, query: str) -> CausalResult:
        """Answer a causal query."""
        ...
    
    def integrated_query(self, world_id: str, query: str) -> IntegratedResult:
        """Answer an integrated spatial-temporal-causal query."""
        ...
    
    def counterfactual(self, world_id: str, 
                      interventions: Dict[str, Any]) -> CounterfactualResult:
        """Answer a counterfactual what-if question."""
        ...
    
    def causal_discovery(self, world_id: str, 
                        variables: List[str]) -> CausalGraphResult:
        """Discover causal structure from observational data."""
        ...
```

### Performance Considerations

Three Rivers reasoning can be computationally expensive:

1. **Spatial pathfinding:** A* is O(E + V log V) per query. For large graphs, precompute all-pairs shortest paths.
2. **Temporal querying:** Interval queries are O(N) for N events. Index events by time for O(log N) queries.
3. **Causal intervention:** Re-running the SCM is O(V + E) per intervention. Cache intervention results for common queries.
4. **Causal discovery:** The PC algorithm is O(N^d) where N is the number of variables and d is the max conditioning set size. Limit d to 3–4 for practical performance.
5. **Integrated queries:** Decompose and parallelize sub-queries across the three reasoners.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 12.

### Discussion Questions

1. The Confluence Engine caches intervention results for common queries. But what if the world state changes between queries? The cached results are stale. How should the cache handle world state changes?

2. Causal discovery is expensive. In a world model with 10,000 variables, the PC algorithm is infeasible. What approximations can be used? (Local causal discovery? Restricted conditioning set sizes?)

3. Integrated queries require decomposing a natural-language query into modality-specific sub-queries. The decomposition step itself may be ambiguous. How should the system handle ambiguous decompositions?

---

## Lecture 12: The Three Rivers — Course Synthesis and Capstone

### Summary: Three Rivers, One World

We began at the roots of Yggdrasil, where three wells water the world tree. We end with a unified reasoning architecture that integrates three fundamental modalities:

- **The Hvergelmir Stream (Spatial):** Where things are, how they connect, how to navigate. Topology, geometry, pathfinding. The spatial graph and world-aware navigation.

- **The Urðarbrunnr Stream (Temporal):** When things happen, how long they last, what overlaps. Interval temporal logic, persistence, concurrency. The temporal query engine.

- **The Mímisbrunnr Stream (Causal):** Why things happen, what would change. Structural causal models, the do-calculus, counterfactuals. The causal explanation engine.

- **The Confluence:** Where, when, and why together. Integrated queries, decomposition, composition. The Three Rivers meet at the base of Yggdrasil.

These three rivers are not separate — they flow together, informing each other. Spatial reasoning constrains what can happen where. Temporal reasoning constrains when it can happen. Causal reasoning constrains why it happens. Together, they form the foundation of a world model that can answer any question about the simulated world.

### Capstone Project: The Three Rivers Simulator

Your capstone project is to build a complete Three Rivers reasoning system:

1. **Spatial module:** A village spatial graph with 20+ locations, world-aware A* navigation, and proximity/containment queries.
2. **Temporal module:** An event log with interval temporal logic queries, persistence handling, and concurrency resolution.
3. **Causal module:** A structural causal model with 10+ variables, the do-operator, and counterfactual reasoning.
4. **Confluence engine:** An integrated query system that decomposes queries into modality-specific sub-queries and composes the answers.
5. **API layer:** A REST service exposing spatial, temporal, causal, and integrated queries.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with type hints and docstrings).
2. Village model (spatial graph, event log, SCM).
3. 10 spatial queries, 10 temporal queries, 10 causal queries, and 5 integrated queries with full answers and explanations.
4. 5 counterfactual scenarios with before/after analysis.
5. A design document (5–8 pages) describing your Three Rivers architecture.

### The Rivers Flow

The Three Rivers water the roots of Yggdrasil. Hvergelmir feeds the spatial stream — the water of place. Urðarbrunnr feeds the temporal stream — the water of time. Mímisbrunnr feeds the causal stream — the water of wisdom. And where they meet, the world grows.

**ᚻ Hagalaz — Hail. The disruptive force that reveals structure.**
**ᛁ Isa — Ice. Time frozen, still, waiting.**
**ᛞ Dagaz — Dawn. The breakthrough, the moment of clarity.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᚻ — The three rivers flow. The world drinks.*