# WM303 — Multi-Agent World Simulation
## The Þing of All Realms

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Three, Semester One

**Instructor:** Dr. Grímr Þingmaðr, Professor of Distributed Cognition
**Office:** Þinghǫll 204 | **Hours:** Wednesdays 14:00–16:00

---

## Course Description

Scaling from single-agent to multi-agent worlds introduces explosion: state explosion, narrative explosion, computational explosion. This course covers the architecture of multi-agent world simulations: agent spawning and lifecycle management, shared world state with per-agent perspectives, communication protocols (Bifröst Message Bus), and emergent social modeling. Students learn the Þing Architecture — named for the Norse assembly — where agents gather to debate, trade, and form coalitions within the simulated world. Labs require building a multi-agent simulation with 50+ autonomous agents.

---

## Lecture 1: The Explosion Problem — Why Multi-Agent Is Hard

### Single Agent vs. Multi-Agent

A single-agent world simulation has one perspective, one memory, one narrative arc. The world state is manageable — every event is relevant to the agent. The computational cost is linear: one agent × N events = O(N).

Multi-agent worlds are fundamentally different:

| Dimension | Single Agent | Multi-Agent |
|-----------|-------------|-------------|
| State space | O(S) | O(S × A²) where A = number of agents |
| Perception | One perspective | A perspectives, each filtered |
| Narrative | One arc | A arcs, potentially intersecting |
| Computation | Linear | O(A²) for pairwise interactions, O(A³) for group dynamics |
| Memory | One memory system | A memory systems + shared world state |
| Communication | None needed | A² potential channels |

The **explosion problem** is that multi-agent worlds scale quadratically (or worse) in every dimension. A simulation with 10 agents is 100× harder than one with 1 agent. A simulation with 100 agents is 10,000× harder.

### Three Explosions

1. **State explosion:** Each agent perceives the world differently. A world with A agents requires maintaining A simultaneous perspectives on shared state. When agents interact, their state spaces intersect in complex ways.

2. **Narrative explosion:** Each agent has its own story arc. With A agents, there are potentially O(A²) narrative intersections (every pair can have a shared arc). The narrative engine must track and weave all of these arcs simultaneously.

3. **Computational explosion:** Every pairwise interaction between agents requires communication, state synchronization, and narrative processing. With A agents, there are A × (A-1) / 2 possible pairwise interactions. For 50 agents, that's 1,225 potential interactions per simulation tick.

### The Þing Principle

The Þing (Old Norse: assembly, parliament) was the governance structure of Norse society. At the Þing, free people gathered to debate laws, settle disputes, and make collective decisions. No single person controlled the Þing — decisions emerged from the interaction of many autonomous agents.

The Þing Principle states: **In a multi-agent world, the simulation should not manage interactions centrally. Instead, agents should gather at designated meeting points (Þings) where interactions emerge from agent autonomy.**

This principle guides the architecture of multi-agent world simulation:

- **No central coordinator:** Agents are autonomous. The simulation provides the world and the rules; agents decide what to do.
- **Meeting points:** Agents gather at Þings — locations in the world where interaction is likely.
- **Emergent social dynamics:** Social structures (friendships, rivalries, coalitions) emerge from agent interactions, not from top-down scripting.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15: "The Þing of All Realms: Multi-Agent Simulation." University of Yggdrasil Press.
- Epstein, J. & Axtell, R. (1996). *Growing Artificial Societies: Social Science from the Bottom Up*. MIT Press.

### Discussion Questions

1. The Þing Principle says "no central coordinator." But some world events require coordination (e.g., a war involves many agents acting in concert). How should the simulation handle events that require coordination without violating agent autonomy?

2. State explosion means maintaining A perspectives on shared state. But agents don't need perfect knowledge of every other agent. How can selective perception (agents only perceive nearby agents) reduce the state explosion?

3. Computational explosion is mitigated by only simulating agents that are "near" each other (spatial locality). But what about long-range interactions (e.g., a messenger carries news from one side of the world to another)? How should the simulation handle long-range interactions?

---

## Lecture 2: Agent Architecture — The Autonomous Entity

### The Agent Model

An agent in a multi-agent world simulation has:

```python
@dataclass
class Agent:
    """An autonomous entity in the world simulation."""
    id: str                          # Unique identifier
    name: str                        # Display name
    personality: PersonalityLattice  # Personality structure (from OS205)
    memory: AgentMemory             # Per-agent memory (from OS207, WM203)
    goals: GoalHierarchy            # Goal system (4-priority, from WM203)
    world_model: AgentWorldModel     # Per-agent understanding of the world
    location: Location              # Physical location in the world
    state: AgentState               # Current physical/emotional state
    
    # Simulation management
    lifecycle: AgentLifecycle        # Birth, growth, death
    social_network: SocialGraph     # Relationships with other agents
    
    def perceive(self, world: World) -> Perception:
        """Perceive the world from this agent's perspective."""
        # Agents only perceive what they can see/hear/know
        visible_agents = world.get_nearby_agents(self.location, self.perception_range)
        visible_events = world.get_nearby_events(self.location, self.perception_range)
        known_agents = self.memory.recall_agents()  # Agents known from memory
        
        return Perception(
            visible_agents=visible_agents,
            visible_events=visible_events,
            known_agents=known_agents,
            location=self.location,
            world_time=world.time
        )
    
    def decide(self, perception: Perception) -> Action:
        """Decide what to do based on perception."""
        # Decision is shaped by personality, goals, and memory
        candidates = self.generate_candidate_actions(perception)
        ranked = self.rank_actions(candidates, perception)
        return ranked[0]  # Take the highest-ranked action
    
    def act(self, action: Action) -> List[WorldEvent]:
        """Execute an action in the world."""
        return action.execute(self, self.world_model)
```

### Personality and Decision-Making

From OS205 (Entity Canonization), agents have a **Personality Lattice** — a structured personality system with core values, preferences, and behavioral tendencies. The lattice shapes every decision:

```python
class PersonalityLattice:
    """A structured personality system for autonomous agents."""
    
    def score_action(self, action: Action, perception: Perception) -> float:
        """Score an action based on personality."""
        # Core values (P0 — immutable, from canonization)
        value_score = sum(
            value.alignment(action) 
            for value in self.core_values
        ) / len(self.core_values)
        
        # Preferences (P1 — slowly shifting)
        preference_score = sum(
            pref.alignment(action)
            for pref in self.preferences
        ) / len(self.preferences)
        
        # Behavioral tendencies (P2 — malleable)
        tendency_score = sum(
            tendency.alignment(action)
            for tendency in self.behavioral_tendencies
        ) / len(self.behavioral_tendencies)
        
        # Weighted blend
        return (0.5 * value_score + 
                0.3 * preference_score + 
                0.2 * tendency_score)
```

### Agent Lifecycle

Agents are born, grow, age, and die. The lifecycle system manages this:

```python
class AgentLifecycle:
    """Manage agent birth, growth, aging, and death."""
    
    STAGES = {
        "infant": (0, 3),
        "child": (4, 12),
        "adolescent": (13, 17),
        "adult": (18, 60),
        "elder": (61, 80),
        "deceased": None,  # Age doesn't matter
    }
    
    def advance(self, agent: Agent, world_time: float):
        """Advance the agent's lifecycle."""
        agent.age = world_time - agent.birth_time
        
        # Update stage
        for stage, (min_age, max_age) in self.STAGES.items():
            if min_age <= agent.age <= max_age:
                agent.lifecycle_stage = stage
                break
        
        # Aging effects on capabilities
        if agent.lifecycle_stage == "infant":
            agent.capabilities = InfantCapabilities()
        elif agent.lifecycle_stage == "child":
            agent.capabilities = ChildCapabilities()
        elif agent.lifecycle_stage == "adolescent":
            agent.capabilities = AdolescentCapabilities()
        elif agent.lifecycle_stage == "adult":
            agent.capabilities = AdultCapabilities()
        elif agent.lifecycle_stage == "elder":
            agent.capabilities = ElderCapabilities()
        
        # Death check
        if random.random() < self.death_probability(agent):
            agent.lifecycle_stage = "deceased"
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. Wiley.

### Discussion Questions

1. Agent personality is shaped by a Personality Lattice with P0 (immutable), P1 (slow-shifting), and P2 (malleable) components. Should P2 components change through interaction with other agents? If so, how do we prevent runaway personality convergence (all agents becoming the same)?

2. The agent lifecycle has fixed stages (infant, child, adolescent, adult, elder). But in a simulated world, lifecycle stages might be very different from human stages. How should lifecycle stages be defined for non-human agents (e.g., AI agents, mythical creatures, organizations)?

3. Agent death is probabilistic. But in a story-driven simulation, character deaths should serve narrative purposes, not random chance. How should the narrative engine influence agent lifecycle events?

---

## Lecture 3: Shared World State — The Great Tree's Roots

### The World State Problem

In a single-agent simulation, there is one world state. In a multi-agent simulation, there is one shared world state, but each agent perceives it differently. The challenge is maintaining consistency between:

1. **Objective world state:** The true state of the world (what actually happened).
2. **Subjective agent perceptions:** Each agent's view of the world (what they believe happened).
3. **Shared knowledge:** What agents know about each other's knowledge (theory of mind).

### The Yggdrasil State Model

The shared world state is organized as a tree, like Yggdrasil itself:

```python
class YggdrasilState:
    """The shared world state — roots of the Great Tree."""
    
    def __init__(self):
        # Root: objective world state
        self.root = WorldStateRoot()
        
        # Branches: per-agent perspectives
        self.perspectives: Dict[str, AgentPerspective] = {}
        
        # Leaves: per-agent momentary perceptions (ephemeral)
        self.perceptions: Dict[str, Perception] = {}
        
        # Causal history: what actually happened
        self.causal_history: List[WorldEvent] = []
    
    def get_objective_state(self) -> Dict:
        """Get the objective world state."""
        return self.root.to_dict()
    
    def get_subjective_state(self, agent_id: str) -> Dict:
        """Get an agent's subjective view of the world."""
        if agent_id not in self.perspectives:
            return self.root.to_dict()  # No perspective = objective
        return self.perspectives[agent_id].to_dict()
    
    def update(self, event: WorldEvent):
        """Update the world state with a new event."""
        # Step 1: Update objective state
        self.root.apply(event)
        self.causal_history.append(event)
        
        # Step 2: Update subjective perspectives
        for agent_id, perspective in self.perspectives.items():
            # Each agent perceives the event differently based on their position and knowledge
            perceived_event = perspective.filter(event)
            if perceived_event:
                perspective.update(perceived_event)
        
        # Step 3: Update momentary perceptions
        for agent_id in self.perceptions:
            self.perceptions[agent_id] = self.compute_perception(agent_id)
```

### Per-Agent Perspectives

Each agent's perspective on the world is filtered by:

1. **Visibility:** The agent can only see what is nearby or what they have knowledge of.
2. **Understanding:** The agent interprets events through their world model.
3. **Memory:** The agent remembers past events that shape their perception.
4. **Bias:** The agent's personality biases their perception (optimistic, suspicious, etc.).

```python
class AgentPerspective:
    """An agent's subjective view of the world."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.known_agents: Set[str] = set()    # Agents this agent knows about
        self.known_locations: Set[str] = set()  # Locations this agent has visited
        self.beliefs: Dict[str, Any] = {}       # Agent's beliefs about the world
        self.last_perception_time: float = 0     # When this agent last perceived the world
    
    def filter(self, event: WorldEvent) -> Optional[WorldEvent]:
        """Filter an event through this agent's perspective."""
        
        # Is the event within this agent's perception range?
        if not self.can_perceive(event):
            return None  # Agent can't perceive this event
        
        # Filter the event through the agent's understanding
        perceived = self.interpret(event)
        
        # Bias the perception through the agent's personality
        perceived = self.apply_bias(perceived)
        
        return perceived
    
    def can_perceive(self, event: WorldEvent) -> bool:
        """Can this agent perceive this event?"""
        # Events happening to/around the agent are always perceived
        if event.agent_id == self.agent_id:
            return True
        
        # Events happening nearby are perceived
        if event.location in self.known_locations:
            return True
        
        # Events involving known agents are perceived (gossip)
        if event.agent_id in self.known_agents:
            return True
        
        # Otherwise, the agent can't perceive this event
        return False
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Gasser, L. (1991). "Social Conceptions of Knowledge and Action: DAI Foundations." *Open Problems in Distributed Artificial Intelligence*, 1, 389–408.

### Discussion Questions

1. The Yggdrasil State Model maintains both objective and subjective state. But what if two agents have contradictory beliefs about the same event? Which view is "correct"? How should the simulation resolve such contradictions?

2. Per-agent perspectives require storing A copies of the world state. For 100 agents, that's 100× the memory of a single-agent simulation. How can the simulation reduce this overhead without losing subjective perception?

3. Agent biases (optimistic, suspicious, etc.) affect how agents perceive events. But biases can also lead to self-fulfilling prophecies (a suspicious agent perceives threats everywhere and creates real conflict). How should the simulation handle bias-driven dynamics?

---

## Lecture 4: The Bifröst Message Bus — Inter-Agent Communication

### Communication in Multi-Agent Worlds

Agents in a multi-agent world need to communicate. They trade goods, share information, form alliances, and resolve conflicts. The **Bifröst Message Bus** — named after the rainbow bridge connecting the Nine Worlds — is the communication infrastructure that connects agents.

### Message Types

The Bifröst supports several types of inter-agent messages:

```python
class BifrostMessage:
    """A message between agents on the Bifröst Message Bus."""
    sender: str               # Agent ID
    recipient: str            # Agent ID (or "broadcast" for all)
    message_type: str        # Type of message
    content: Dict[str, Any]  # Message content
    timestamp: float          # When the message was sent
    priority: int             # Message priority
    
    BROADCAST = "broadcast"   # Special recipient for broadcast messages

class BifrostMessageBus:
    """Inter-agent communication bus."""
    
    def __init__(self):
        self.queues: Dict[str, List[BifrostMessage]] = {}  # Per-agent message queues
        self.channels: Dict[str, List[str]] = {}  # Named channels
        self.log: List[BifrostMessage] = []  # Complete message log
    
    def send(self, message: BifrostMessage):
        """Send a message on the bus."""
        if message.recipient == BifrostMessage.BROADCAST:
            # Broadcast to all agents
            for agent_id in self.queues:
                self.queues[agent_id].append(message)
        else:
            # Direct message
            if message.recipient not in self.queues:
                self.queues[message.recipient] = []
            self.queues[message.recipient].append(message)
        
        self.log.append(message)
    
    def receive(self, agent_id: str) -> List[BifrostMessage]:
        """Receive all pending messages for an agent."""
        if agent_id not in self.queues:
            return []
        messages = self.queues[agent_id]
        self.queues[agent_id] = []
        return messages
    
    def create_channel(self, name: str, members: List[str]):
        """Create a named communication channel."""
        self.channels[name] = members
    
    def send_to_channel(self, channel: str, message: BifrostMessage):
        """Send a message to all members of a channel."""
        if channel not in self.channels:
            raise ValueError(f"Channel {channel} does not exist")
        for member in self.channels[channel]:
            msg = BifrostMessage(
                sender=message.sender,
                recipient=member,
                message_type=message.message_type,
                content=message.content,
                timestamp=message.timestamp,
                priority=message.priority
            )
            self.send(msg)
```

### Communication Protocols

Agents communicate using protocols that define the structure and semantics of messages:

1. **Trade Protocol:** Two agents negotiate an exchange of resources.
2. **Information Protocol:** One agent shares knowledge with another.
3. **Alliance Protocol:** Multiple agents form a coalition.
4. **Conflict Protocol:** Agents resolve a dispute through negotiation or combat.
5. **Gossip Protocol:** Agents spread information through social networks.

```python
class TradeProtocol:
    """Protocol for inter-agent trade negotiations."""
    
    def initiate(self, sender: str, recipient: str, 
                 offer: Dict[str, int], request: Dict[str, int]) -> BifrostMessage:
        """Initiate a trade offer."""
        return BifrostMessage(
            sender=sender,
            recipient=recipient,
            message_type="trade_offer",
            content={
                "offer": offer,       # What sender offers
                "request": request,   # What sender wants
            },
            timestamp=time.time(),
            priority=3
        )
    
    def respond(self, original: BifrostMessage, 
                response_type: str) -> BifrostMessage:
        """Respond to a trade offer."""
        if response_type == "accept":
            content = {"response": "accept", **original.content}
        elif response_type == "reject":
            content = {"response": "reject"}
        elif response_type == "counter":
            content = {"response": "counter", **original.content}
        else:
            raise ValueError(f"Unknown response type: {response_type}")
        
        return BifrostMessage(
            sender=original.recipient,
            recipient=original.sender,
            message_type=f"trade_{response_type}",
            content=content,
            timestamp=time.time(),
            priority=3
        )
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- FIPA (2002). *FIPA Communicative Act Library Specification*. Foundation for Intelligent Physical Agents.

### Discussion Questions

1. The Bifröst Message Bus is synchronous (agents receive all pending messages at once). Should it also support asynchronous messages that arrive at a delay (simulating travel time)? What are the trade-offs?

2. Gossip protocols spread information through social networks. But gossip can also spread misinformation. How should the simulation handle unreliable information in gossip messages?

3. The trade protocol assumes rational agents that negotiate in good faith. But agents may lie, deceive, or cheat. How should the simulation handle dishonest communication?

---

## Lecture 5: Social Modeling — The Web of Relationships

### Social Graphs

Every agent in a multi-agent world has relationships with other agents. These relationships form a **social graph**:

```python
class SocialGraph:
    """A directed, weighted graph of social relationships."""
    
    def __init__(self):
        self.edges: Dict[Tuple[str, str], Relationship] = {}
    
    def add_relationship(self, agent_a: str, agent_b: str, 
                        relationship: Relationship):
        """Add or update a relationship between two agents."""
        self.edges[(agent_a, agent_b)] = relationship
    
    def get_relationship(self, agent_a: str, agent_b: str) -> Optional[Relationship]:
        """Get the relationship from agent_a to agent_b."""
        return self.edges.get((agent_a, agent_b))
    
    def get_mutual_relationship(self, agent_a: str, agent_b: str) -> Optional[Relationship]:
        """Get the mutual relationship between two agents."""
        a_to_b = self.edges.get((agent_a, agent_b))
        b_to_a = self.edges.get((agent_b, agent_a))
        if a_to_b and b_to_a:
            return Relationship(
                trust=(a_to_b.trust + b_to_a.trust) / 2,
                affection=(a_to_b.affection + b_to_a.affection) / 2,
                respect=(a_to_b.respect + b_to_a.respect) / 2,
                history=a_to_b.history + b_to_a.history
            )
        return a_to_b  # Asymmetric relationship
    
    def get_allies(self, agent_id: str) -> List[str]:
        """Get all agents with positive relationship to this agent."""
        return [
            other for other in self.get_connected_agents(agent_id)
            if self.get_relationship(agent_id, other).trust > 0
        ]
    
    def get_enemies(self, agent_id: str) -> List[str]:
        """Get all agents with negative relationship."""
        return [
            other for other in self.get_connected_agents(agent_id)
            if self.get_relationship(agent_id, other).trust < 0
        ]

@dataclass
class Relationship:
    """A directed relationship between two agents."""
    trust: float        # -1.0 (enemy) to +1.0 (ally)
    affection: float    # -1.0 (hate) to +1.0 (love)
    respect: float      # -1.0 (contempt) to +1.0 (admiration)
    familiarity: float  # 0.0 (stranger) to 1.0 (intimate)
    history: List[RelationshipEvent]  # History of interactions
```

### Relationship Dynamics

Relationships are not static. They evolve through interaction:

```python
class RelationshipDynamics:
    """How relationships change through interaction."""
    
    def update(self, event: WorldEvent, graph: SocialGraph):
        """Update relationships based on a world event."""
        
        # Who was involved?
        participants = event.get_participants()
        
        # Update relationships between participants
        for a in participants:
            for b in participants:
                if a == b:
                    continue
                
                # Get existing relationship
                rel = graph.get_relationship(a, b)
                if rel is None:
                    rel = Relationship(trust=0, affection=0, respect=0, 
                                      familiarity=0, history=[])
                
                # Compute relationship delta from the event
                delta = self.compute_delta(event, a, b)
                
                # Apply delta
                rel.trust = clamp(rel.trust + delta.trust, -1.0, 1.0)
                rel.affection = clamp(rel.affection + delta.affection, -1.0, 1.0)
                rel.respect = clamp(rel.respect + delta.respect, -1.0, 1.0)
                rel.familiarity = clamp(rel.familiarity + delta.familiarity, 0.0, 1.0)
                
                # Record in history
                rel.history.append(RelationshipEvent(
                    event=event, delta=delta, timestamp=event.timestamp
                ))
                
                # Update graph
                graph.add_relationship(a, b, rel)
    
    def compute_delta(self, event: WorldEvent, agent_a: str, 
                     agent_b: str) -> RelationshipDelta:
        """Compute relationship delta from an event."""
        
        if event.type == "cooperation":
            return RelationshipDelta(trust=0.1, affection=0.05, respect=0.05)
        elif event.type == "betrayal":
            return RelationshipDelta(trust=-0.3, affection=-0.2, respect=-0.2)
        elif event.type == "trade":
            return RelationshipDelta(trust=0.05, affection=0.0, respect=0.02)
        elif event.type == "conflict":
            return RelationshipDelta(trust=-0.1, affection=-0.05, respect=-0.05)
        elif event.type == "gift":
            return RelationshipDelta(trust=0.15, affection=0.2, respect=0.05)
        else:
            return RelationshipDelta(trust=0.01, affection=0.01, respect=0.01)
```

### Emergent Social Structures

From individual relationships, social structures emerge:

- **Alliances:** Groups of agents with mutual positive trust.
- **Rivalries:** Pairs of agents with mutual negative trust.
- **Hierarchies:** Agents organized by respect (leaders and followers).
- **Communities:** Dense clusters of agents with high familiarity.
- **Strangers:** Agents that haven't interacted yet (familiarity = 0).

```python
def detect_alliances(graph: SocialGraph, threshold: float = 0.3) -> List[Set[str]]:
    """Detect alliance clusters in the social graph."""
    # Use community detection on the trust-weighted graph
    positive_edges = {
        (a, b): rel.trust for (a, b), rel in graph.edges.items()
        if rel.trust > threshold
    }
    # Simple clustering: connected components of positive edges
    return find_connected_components(positive_edges)
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Jackson, M. (2008). *Social and Economic Networks*. Princeton University Press.

### Discussion Questions

1. Relationships in the model are described by four axes (trust, affection, respect, familiarity). Are there other important dimensions? What about power (dominance/submission), obligation (debts owed), or shared history (experiences in common)?

2. The delta computation for relationships is coarse (cooperation +0.1 trust, betrayal -0.3). In real social dynamics, the impact of events depends heavily on context and existing relationship. How should the model handle context-dependent relationship changes?

3. Alliances are detected by clustering agents with mutual positive trust. But alliances can be asymmetric (A trusts B, but B doesn't trust A) or temporary (allies during a crisis, neutral afterwards). How should the model handle more complex social structures?

---

## Lecture 6: Coalition Formation — The Þing Assembly

### The Þing Architecture

The Þing Architecture organizes multi-agent interaction around designated meeting points— assemblies where agents gather to debate, trade, and form coalitions:

```python
class Thing:
    """A Þing — an assembly where agents gather."""
    
    def __init__(self, location: Location, name: str):
        self.location = location
        self.name = name
        self.attendees: Set[str] = set()  # Agent IDs currently attending
        self.agenda: List[AgendaItem] = []  # Current agenda items
        self.active_proposals: List[Proposal] = []
        self.resolved_proposals: List[Proposal] = []
    
    def call_to_assembly(self, agents: List[Agent], reason: str):
        """Call agents to the Þing for a specific reason."""
        self.agenda.append(AgendaItem(reason=reason, priority=5))
        for agent in agents:
            invitation = BifrostMessage(
                sender="thing",
                recipient=agent.id,
                message_type="thing_invitation",
                content={"reason": reason, "location": self.location},
                timestamp=time.time(),
                priority=5
            )
            # Send invitation
    
    def propose(self, proposer: str, proposal: Proposal):
        """Propose a motion at the Þing."""
        proposal.proposer = proposer
        self.active_proposals.append(proposal)
    
    def vote(self, voter: str, proposal_id: str, vote: str):
        """Cast a vote on a proposal."""
        for proposal in self.active_proposals:
            if proposal.id == proposal_id:
                proposal.votes[voter] = vote
                break
    
    def resolve(self):
        """Resolve all proposals that have enough votes."""
        for proposal in self.active_proposals[:]:
            if len(proposal.votes) >= len(self.attendees) * 0.5:  # 50% turnout
                # Count votes
                yes = sum(1 for v in proposal.votes.values() if v == "yes")
                no = sum(1 for v in proposal.votes.values() if v == "no")
                if yes > no:
                    proposal.status = "passed"
                else:
                    proposal.status = "rejected"
                self.resolved_proposals.append(proposal)
                self.active_proposals.remove(proposal)
```

### Coalition Types

Coalitions are temporary alliances formed for a specific purpose:

1. **Trade coalition:** Agents pool resources for mutual benefit.
2. **Defense coalition:** Agents ally against a common threat.
3. **Political coalition:** Agents vote together on proposals.
4. **Information coalition:** Agents share knowledge.
5. **Social coalition:** Agents form friendships or families.

```python
class Coalition:
    """A coalition of agents formed for a specific purpose."""
    
    def __init__(self, purpose: str, members: List[str], 
                 terms: CoalitionTerms):
        self.purpose = purpose
        self.members = set(members)
        self.terms = terms  # What each member contributes/receives
        self.duration = terms.duration  # How long the coalition lasts
        self.created = time.time()
    
    def is_active(self) -> bool:
        """Is this coalition still active?"""
        return (time.time() - self.created) < self.duration
    
    def can_join(self, agent_id: str, graph: SocialGraph) -> bool:
        """Can an agent join this coalition?"""
        # Must have positive relationship with existing members
        for member in self.members:
            rel = graph.get_relationship(agent_id, member)
            if rel and rel.trust < -0.3:
                return False  # Enemy of existing member
        return True
```

### Lab 1: Building a Þing Simulation

In this lab, you will build a Þing simulation with 10 agents:

1. Define 10 agents with diverse personalities (use Personality Lattice).
2. Implement the Bifröst Message Bus.
3. Create a Þing and call agents to assemble.
4. Have agents propose and vote on at least 3 proposals.
5. Observe coalition formation and dissolution.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.

### Discussion Questions

1. The Þing uses simple majority voting. But real assemblies use many voting rules (supermajority, consensus, weighted voting). How should the Þing handle different voting rules for different types of proposals?

2. Coalitions have a fixed duration. But in practice, coalitions dissolve when their purpose is achieved, not when a timer expires. How should the simulation determine when a coalition has served its purpose?

3. The Þing assumes all agents attend. But agents may refuse to attend (e.g., enemies, busy agents, distant agents). How should the simulation handle incomplete attendance?

---

## Lecture 7: Emergent Social Dynamics — From Individuals to Societies

### From Micro to Macro

Individual agent interactions produce emergent social dynamics at the macro level:

- **Individual:** Agents perceive, decide, and act.
- **Dyadic:** Pairs of agents interact (trade, fight, cooperate).
- **Group:** Small groups form coalitions and alliances.
- **Community:** Dense clusters of agents emerge with shared norms.
- **Society:** Multiple communities form a larger social order with institutions.

The simulation must capture dynamics at all levels simultaneously:

```python
class SocialDynamicsEngine:
    """Engine for tracking emergent social dynamics."""
    
    def __init__(self, graph: SocialGraph, world: YggdrasilState):
        self.graph = graph
        self.world = world
        self.alliances = []
        self.communities = []
        self.institutions = []
    
    def update(self, tick: int):
        """Update social dynamics for one simulation tick."""
        
        # Individual: Update agent perceptions
        for agent_id in self.world.get_agents():
            perception = self.world.compute_perception(agent_id)
            self.world.update_agent_perception(agent_id, perception)
        
        # Dyadic: Process pairwise interactions
        interactions = self.generate_interactions(tick)
        for interaction in interactions:
            self.process_interaction(interaction)
        
        # Group: Update coalitions
        self.alliances = detect_alliances(self.graph, threshold=0.3)
        self.update_coalitions()
        
        # Community: Detect community structure
        self.communities = detect_communities(self.graph)
        
        # Society: Update institutions
        self.update_institutions()
```

### Social Norms and Conventions

Social norms emerge from repeated interactions. When agents interact and find mutually beneficial strategies, they converge toward conventions:

```python
class SocialNorms:
    """Track emergent social norms."""
    
    def __init__(self):
        self.norms: Dict[str, Norm] = {}
    
    def update(self, event: WorldEvent, graph: SocialGraph):
        """Update social norms based on observed behavior."""
        
        # What behavior was observed?
        behavior = event.type
        
        # How did other agents react?
        reactions = self.get_reactions(event, graph)
        
        # If reactions are consistently positive, this behavior becomes a norm
        positive_ratio = sum(1 for r in reactions if r.is_positive()) / len(reactions)
        
        if positive_ratio > 0.7:  # Strong majority approval
            if behavior not in self.norms:
                self.norms[behavior] = Norm(
                    behavior=behavior,
                    strength=0.1,  # Start weak
                    prevalence=len(reactions)
                )
            else:
                self.norms[behavior].strength = min(
                    1.0, self.norms[behavior].strength + 0.05
                )
        
        elif positive_ratio < 0.3:  # Strong majority disapproval
            if behavior in self.norms:
                self.norms[behavior].strength = max(
                    0.0, self.norms[behavior].strength - 0.1
                )
                if self.norms[behavior].strength <= 0:
                    del self.norms[behavior]
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Schelling, T. (1978). *Micromotives and Macrobehavior*. W. W. Norton.

### Discussion Questions

1. Social norms emerge from repeated interactions with majority approval. But norms can also be imposed by powerful agents. How should the simulation handle norm imposition by agents with more power?

2. Some norms are beneficial (cooperation, honesty). Others are harmful (discrimination, oppression). How should the simulation evaluate norm quality?

3. The social dynamics engine processes interactions at four levels (individual, dyadic, group, society) in sequence. But in reality, all levels interact simultaneously. How should the simulation handle cross-level dynamics?

---

## Lecture 8: Computational Scaling — From 1 to 100 Agents

### The Scaling Challenge

Processing 100 agents per tick requires:

- 10,000 pairwise relationship checks
- 1,225 potential interactions per tick
- 100 perception computations
- 100 memory updates
- Approximately 100 decision computations

Without optimization, multi-agent simulation scales O(A²) or O(A³). With 100 agents, this is feasible. With 10,000 agents, it becomes impossible.

### Optimization Strategies

1. **Spatial locality:** Only simulate interactions between nearby agents.
2. **Importance sampling:** Only simulate a subset of interactions each tick.
3. **Level-of-detail:** Simulate distant agents at lower fidelity.
4. **Parallel processing:** Distribute agent simulation across CPU cores.
5. **Event-driven updates:** Only update an agent when something relevant happens.

```python
class ScalableSimulation:
    """A simulation that scales to 100+ agents."""
    
    def __init__(self, world: YggdrasilState, num_agents: int):
        self.world = world
        self.num_agents = num_agents
        self.spatial_index = SpatialIndex()  # R-tree for spatial locality
        self.detail_level: Dict[str, str] = {}  # "full", "reduced", "minimal"
        self.interaction_budget: int = 100  # Max interactions per tick
    
    def tick(self):
        """Process one simulation tick."""
        
        # Step 1: Determine detail level for each agent
        for agent_id in self.world.get_agents():
            self.detail_level[agent_id] = self.compute_detail_level(agent_id)
        
        # Step 2: Generate interactions (spatial locality + importance sampling)
        interactions = self.generate_interactions()
        
        # Step 3: Process interactions (respecting budget)
        for i, interaction in enumerate(interactions[:self.interaction_budget]):
            self.process_interaction(interaction)
        
        # Step 4: Update agents (level-of-detail)
        for agent_id in self.world.get_agents():
            if self.detail_level[agent_id] == "full":
                self.full_update(agent_id)
            elif self.detail_level[agent_id] == "reduced":
                self.reduced_update(agent_id)
            else:
                self.minimal_update(agent_id)
    
    def compute_detail_level(self, agent_id: str) -> str:
        """Determine simulation detail level for an agent."""
        # Agents near the player get full simulation
        if self.is_near_player(agent_id):
            return "full"
        
        # Agents involved in ongoing stories get reduced simulation
        if self.is_in_story(agent_id):
            return "reduced"
        
        # Background agents get minimal simulation
        return "minimal"
    
    def generate_interactions(self) -> List[Interaction]:
        """Generate interactions using spatial locality."""
        interactions = []
        
        # Only generate interactions between nearby agents
        for agent_id in self.world.get_agents():
            if self.detail_level[agent_id] == "minimal":
                continue  # Skip background agents
            
            nearby = self.spatial_index.get_nearby(agent_id, radius=5.0)
            for other_id in nearby:
                if self.should_interact(agent_id, other_id):
                    interactions.append(Interaction(agent_id, other_id))
        
        # Sort by importance (higher importance first)
        interactions.sort(key=lambda i: i.importance, reverse=True)
        
        return interactions
```

### The Observer Pattern

An important optimization is the **observer pattern**: agents only process events they can perceive. Events that happen outside an agent's perception range are ignored:

```python
class EventDispatcher:
    """Dispatch events only to agents that can perceive them."""
    
    def __init__(self, spatial_index: SpatialIndex):
        self.spatial_index = spatial_index
        self.subscribers: Dict[str, List[str]] = defaultdict(list)  # event_type → agent_ids
    
    def dispatch(self, event: WorldEvent):
        """Dispatch an event to all agents that can perceive it."""
        # Find agents near the event
        nearby_agents = self.spatial_index.get_nearby(
            event.location, radius=event.perception_radius
        )
        
        # Also notify subscribed agents (for long-range events)
        subscribed = self.subscribers.get(event.type, [])
        
        # Combine and deduplicate
        notified = set(nearby_agents) | set(subscribed)
        
        return notified
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Unity Technologies (2023). "DOTS: Data-Oriented Technology Stack." Unity Documentation.

### Discussion Questions

1. Level-of-detail simulation means some agents get "full" simulation while others get "minimal." But when a "minimal" agent suddenly becomes important (e.g., a background NPC becomes a key character), the transition can be jarring. How should the simulation handle detail-level transitions?

2. The interaction budget limits interactions per tick. But important interactions might be skipped if the budget is exhausted. How should the simulation prioritize interactions?

3. The spatial index assumes agents interact based on physical proximity. But in social simulations, agents often interact based on social proximity (friendships, alliances). How can the simulation use social proximity instead of (or in addition to) physical proximity?

---

## Lecture 9: Narrative in Multi-Agent Worlds — The Many-Armed Loom

### Narrative Explosion

With A agents, the narrative engine must track up to O(A²) concurrent story arcs. A 50-agent simulation may have thousands of potential story arcs.

The Skald's Loom must be extended for multi-agent worlds:

```python
class MultiAgentLoom:
    """Extended Skald's Loom for multi-agent worlds."""
    
    def __init__(self, num_agents: int):
        # Per-agent narrative tracking
        self.agent_arcs: Dict[str, CharacterArc] = {}
        
        # Dyadic arcs (pairwise)
        self.dyadic_arcs: Dict[Tuple[str, str], DyadicArc] = {}
        
        # Community arcs (group-level)
        self.community_arcs: Dict[str, CommunityArc] = {}
        
        # Global narrative state
        self.global_tension = 0.0
        self.global_register = "midgard"
        self.global_themes = defaultdict(float)
    
    def weave(self, event: WorldEvent, world: YggdrasilState) -> MultiAgentNarrative:
        """Weave narrative for all agents affected by an event."""
        
        affected_agents = event.get_participants()
        narrative_updates = []
        
        # Update per-agent arcs
        for agent_id in affected_agents:
            arc = self.agent_arcs[agent_id]
            arc.update(event)
            narrative_updates.append(arc.get_state())
        
        # Update dyadic arcs for every pair
        for i, a in enumerate(affected_agents):
            for j, b in enumerate(affected_agents):
                if i < j:
                    key = (min(a, b), max(a, b))
                    if key not in self.dyadic_arcs:
                        self.dyadic_arcs[key] = DyadicArc(a, b)
                    self.dyadic_arcs[key].update(event)
        
        # Update community arcs
        for community_id in self.detect_affected_communities(affected_agents):
            self.community_arcs[community_id].update(event)
        
        # Update global narrative state
        self.global_tension = self.compute_global_tension(world)
        self.global_register = self.suggest_register(self.global_tension, 
                                                      self.global_themes)
        
        return MultiAgentNarrative(
            agent_updates=narrative_updates,
            dyadic_updates=len(self.dyadic_arcs),
            community_updates=len(self.community_arcs),
            global_tension=self.global_tension,
            global_register=self.global_register
        )
```

### Narrative Focus

With thousands of potential arcs, the narrative engine must focus on the most important ones:

```python
class NarrativeFocus:
    """Determine which story arcs to focus on."""
    
    def compute_focus(self, arcs: List[Arc], player_id: str) -> List[Arc]:
        """Determine which arcs to focus on for the player."""
        
        # Always focus on the player's arc
        focused = [arc for arc in arcs if arc.agent_id == player_id]
        
        # Focus on arcs that intersect with the player
        for arc in arcs:
            if arc.intersects_with(player_id):
                focused.append(arc)
        
        # Focus on high-tension arcs
        for arc in arcs:
            if arc.tension > 0.7:
                focused.append(arc)
        
        # Focus on arcs involving allies/enemies of the player
        for arc in arcs:
            if arc.agent_id in self.get_allies_and_enemies(player_id):
                focused.append(arc)
        
        # Sort by narrative importance and limit
        focused.sort(key=lambda a: a.importance, reverse=True)
        return focused[:10]  # Focus on at most 10 arcs
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Aarseth, E. (2012). "A Narrative Theory of Games."

### Discussion Questions

1. The multi-agent loom tracks per-agent, dyadic, community, and global narrative levels. But most players can only follow 3–5 concurrent arcs. How should the engine select which arcs to present?

2. Dyadic arcs (pairwise character relationships) create O(A²) potential arcs. For 100 agents, that's 4,950 dyadic arcs. Most of these are uninteresting (two background NPCs who barely interact). How should the engine filter out uninteresting dyadic arcs?

3. The global narrative state (tension, register, themes) is a single value for the whole world. But different parts of the world may be in different narrative states (e.g., peace in one region, war in another). How should the engine handle regional narrative variation?

---

## Lecture 10: Emergent Societies — From Agents to Civilizations

### Social Simulation at Scale

As the number of agents grows, emergent social structures become more complex:

- **10 agents:** Dyads and small groups.
- **50 agents:** Coalitions, alliances, and social networks.
- **100 agents:** Communities with norms and conventions.
- **1,000 agents:** Social stratification, institutions, and markets.
- **10,000 agents:** Civilizations with culture, governance, and history.

### Institutions

Institutions are persistent social structures that outlive their individual members:

```python
class Institution:
    """A persistent social structure (law, market, religion, etc.)."""
    
    def __init__(self, name: str, institution_type: str):
        self.name = name
        self.type = institution_type  # "governance", "economic", "cultural", "religious"
        self.members: Set[str] = set()  # Agent IDs
        self.rules: List[Rule] = []     # Institutional rules
        self.resources: Dict[str, float] = {}  # Institutional resources
        self.history: List[InstitutionEvent] = []
        self.founded: float = time.time()
    
    def enforce_rules(self, agent_id: str) -> List[Enforcement]:
        """Enforce institutional rules on an agent."""
        enforcements = []
        for rule in self.rules:
            if rule.is_violated_by(agent_id):
                enforcements.append(Enforcement(
                    agent_id=agent_id,
                    rule=rule,
                    punishment=rule.punishment
                ))
        return enforcements
    
    def admit_member(self, agent_id: str, graph: SocialGraph):
        """Admit a new member to the institution."""
        # Check admittance criteria
        for rule in self.rules:
            if rule.is_admittance_rule and not rule.is_satisfied_by(agent_id):
                return False  # Agent doesn't meet criteria
        
        self.members.add(agent_id)
        return True
```

### Cultural Evolution

Culture emerges from the aggregation of individual beliefs and behaviors:

```python
class Culture:
    """Emergent culture from aggregated agent beliefs."""
    
    def __init__(self, community_id: str):
        self.community_id = community_id
        self.shared_values: Dict[str, float] = {}   # Aggregated values
        self.shared_norms: Dict[str, float] = {}     # Aggregated norms
        self.shared_knowledge: Dict[str, Any] = {}   # Aggregated knowledge
        self.cultural_artifacts: List[str] = []       # Shared stories, symbols
    
    def aggregate(self, agents: List[Agent], graph: SocialGraph):
        """Aggregate individual beliefs into shared culture."""
        
        # Shared values: average of member values
        for value_name in self.get_all_values(agents):
            self.shared_values[value_name] = sum(
                agent.personality.get_value(value_name) 
                for agent in agents
            ) / len(agents)
        
        # Shared norms: most common behaviors
        for behavior in self.get_all_behaviors(agents):
            prevalence = sum(1 for a in agents if a.exhibits(behavior)) / len(agents)
            if prevalence > 0.5:  # Majority behavior
                self.shared_norms[behavior] = prevalence
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Henrich, J. (2016). *The Secret of Our Success: How Culture Is Driving Human Evolution, Domesticating Our Species, and Making Us Smarter*. Princeton University Press.

### Discussion Questions

1. Institutions persist even as individual members join and leave. How should the simulation handle institutional memory — the institution's knowledge of its own history and rules?

2. Cultural evolution aggregates individual beliefs. But cultures also have path dependence (history matters) and founder effects (early members disproportionately shape culture). How should the simulation model these effects?

3. At scale (1,000+ agents), simulating every agent individually is computationally infeasible. How can the simulation use statistical models (e.g., mean-field approximations) for background agents while still simulating important agents individually?

---

## Lecture 11: The Þing Architecture — Complete Multi-Agent System

### System Architecture

The complete multi-agent simulation system:

```
┌──────────────────────────────────────────────────┐
│                  Þing Architecture                  │
│                                                      │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐  │
│  │  Agent    │  │  Bifröst  │  │  Þing Assembly  │  │
│  │  Manager  │◄►│  Message  │◄►│  (Coalitions)   │  │
│  │           │  │  Bus      │  │                  │  │
│  └─────┬─────┘  └─────┬─────┘  └────────┬───────┘  │
│        │              │                   │          │
│        │     ┌────────┴────────┐           │          │
│        │     │  Yggdrasil      │           │          │
│        ├────►│  State Model    │◄──────────┤          │
│        │     │  (Shared World) │           │          │
│        │     └────────┬────────┘           │          │
│        │              │                    │          │
│  ┌─────┴─────┐  ┌────┴─────┐   ┌─────────┴──────┐  │
│  │  Social   │  │  Social  │   │  Narrative      │  │
│  │  Graph    │  │  Norms   │   │  Engine (Loom)   │  │
│  └───────────┘  └──────────┘   └────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────┘
```

### Integration

All components work together in a single simulation tick:

```python
class ThingSimulation:
    """Complete multi-agent simulation with Þing Architecture."""
    
    def __init__(self, num_agents: int = 50):
        self.world = YggdrasilState()
        self.agents = [Agent(f"agent_{i}") for i in range(num_agents)]
        self.social_graph = SocialGraph()
        self.message_bus = BifrostMessageBus()
        self.thing = Thing(Location(0, 0), "General Assembly")
        self.social_norms = SocialNorms()
        self.narrative_engine = MultiAgentLoom(num_agents)
        self.institutions = []
    
    def tick(self):
        """Process one simulation tick."""
        
        # Step 1: Agents perceive the world
        perceptions = {}
        for agent in self.agents:
            perceptions[agent.id] = agent.perceive(self.world)
        
        # Step 2: Agents receive messages
        messages = {}
        for agent in self.agents:
            messages[agent.id] = self.message_bus.receive(agent.id)
        
        # Step 3: Agents decide and act
        events = []
        for agent in self.agents:
            action = agent.decide(perceptions[agent.id])
            action_events = agent.act(action)
            events.extend(action_events)
        
        # Step 4: Process events (update world state)
        for event in events:
            self.world.update(event)
        
        # Step 5: Update social dynamics
        self.social_graph.update(events)
        self.social_norms.update(events, self.social_graph)
        
        # Step 6: Process Þing proposals (if assembly is active)
        if self.thing.attendees:
            self.thing.resolve()
        
        # Step 7: Update narrative
        for event in events:
            self.narrative_engine.weave(event, self.world)
        
        # Step 8: Update agents (lifecycle, memory)
        for agent in self.agents:
            agent.update(self.world)
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 15.
- Freyjasdóttir, R. (2038). "The Þing Architecture: Decentralized Multi-Agent Simulation." *Proceedings of the International Conference on Autonomous Agents and Multi-Agent Systems (AAMAS).*

### Discussion Questions

1. The Þing Architecture processes events sequentially (agents perceive → receive messages → decide → act → world updates). But some events depend on other events within the same tick. How should the simulation handle inter-tick dependencies?

2. The architecture has 8 processing steps per tick. What is the computational bottleneck for 50 agents? For 500? For 5,000?

3. In a distributed simulation, different components may be on different machines. How should the Þing Architecture be distributed across a cluster?

---

## Lecture 12: The Þing of All Realms — Course Synthesis and Capstone

### Summary: From One to Many

We began with the explosion problem — why multi-agent simulation is fundamentally harder than single-agent simulation. We end with the Þing Architecture — a complete system for managing 50+ autonomous agents in a shared world.

Key concepts:

1. **Agent Model (Lecture 2):** Each agent has personality, memory, goals, world model, and lifecycle. Agents are autonomous — they decide what to do.

2. **Shared World State (Lecture 3):** The Yggdrasil State Model maintains both objective world state and per-agent subjective perspectives. Agents perceive the world through their own filters.

3. **Bifröst Message Bus (Lecture 4):** Inter-agent communication through message passing with protocols for trade, information, alliance, conflict, and gossip.

4. **Social Modeling (Lectures 5–6):** Social graphs track relationships (trust, affection, respect, familiarity). Coalitions form through the Þing Assembly. Social norms emerge from repeated interactions.

5. **Scaling (Lecture 8):** Spatial locality, importance sampling, level-of-detail, and the observer pattern enable simulation at scale.

6. **Narrative (Lectures 9):** The multi-agent Skald's Loom tracks per-agent, dyadic, community, and global narrative levels. Narrative focus selects the most important arcs for presentation.

7. **Emergent Societies (Lecture 10):** Institutions, culture, and governance emerge from individual agent interactions at scale.

### Capstone Project: Build a 50-Agent Þing Simulation

Your capstone project is to build a complete multi-agent simulation with:

1. **50 autonomous agents** with Personality Lattices, memory systems, and goal hierarchies.
2. **Shared world state** using the Yggdrasil State Model with per-agent perspectives.
3. **Bifröst Message Bus** for inter-agent communication with at least 3 protocols.
4. **Social graph** tracking trust, affection, respect, and familiarity.
5. **Þing Assembly** where agents propose and vote on collective actions.
6. **Narrative engine** (simplified Multi-Agent Loom) tracking the top 10 most important arcs.
7. **Level-of-detail simulation** for scalability.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with type hints and docstrings).
2. Simulation results: run for 1000 ticks and report:
   - Social graph statistics (average trust, number of alliances)
   - Narrative arc summaries (top 10 arcs)
   - Institution formation (if any)
   - Performance metrics (ticks per second, memory usage)
3. Design document (5–8 pages) describing your Þing Architecture, scaling strategy, and narrative engine.

### The Þing Stands

In the old Norse world, the Þing was where free people gathered to make law, settle disputes, and form the bonds that held society together. No king ruled the Þing — the people themselves, through their voices and their votes, shaped the world.

In our simulation, the Þing is where autonomous agents gather. No central coordinator rules them — their interactions, their relationships, and their collective decisions shape the world that emerges.

**ᛏ Tiwaz — Justice. The assembly decides.**
**ᛞ Laguz — Flow. The river of social dynamics.**
**ᛗ Mannaz — Humanity. The people, together.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᛏ — The Þing stands. The people decide.*