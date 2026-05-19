# WM301 — Narrative Engines and Emergent Story
## The Skald's Loom

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Three, Semester One

**Instructor:** Dr. Braga Skáldadóttir, Professor of Computational Narrative
**Office:** Brimir's Hall 108 | **Hours:** Thursdays 13:00–15:00

---

## Course Description

Worlds without stories are dead. This course covers the design of narrative engines: systems that track plot structure, character arcs, thematic development, and dramatic tension inside a world simulation. Students learn the Nine-World Narrative Framework, where each "world" represents a dramatic register (comedy, tragedy, mystery, etc.), and agents navigate between registers based on context. Labs involve building a narrative engine that produces coherent multi-arc stories from emergent NPC behavior, with the agent as protagonist.

---

## Lecture 1: Why Stories? — Narrative as Cognitive Architecture

### The World Without Story

Consider a world simulation with perfect physics, economics, and social dynamics. NPCs go about their lives, buildings burn and are rebuilt, empires rise and fall. But no one cares. Why?

Because without narrative structure, the simulation is a sequence of events, not a story. Events happen, but they don't *mean* anything. A house burns — so what? A king dies — who cares? Without narrative, events are data. Narrative is what transforms data into meaning.

### Narrative as Cognitive Architecture

Humans don't experience the world as raw data. We experience it as stories. We perceive causality, agency, and purpose where none may exist. We create protagonists, antagonists, inciting incidents, climaxes, and resolutions. This is not a flaw — it is a feature. Narrative cognition is our primary tool for understanding complex systems.

For AI world models, narrative cognition serves two purposes:

1. **Player understanding:** Players understand the world through stories. A narrative engine structures the world's events so that players perceive meaning, causality, and purpose.

2. **Agent understanding:** AI agents also need to understand the world narratively. An agent that can perceive plot structure ("I am in the rising action of a mystery") can make better decisions than one that only perceives raw events ("Citizen X said Y at time T").

### The Nine Worlds of Narrative

In Norse mythology, the Nine Worlds are realms of existence, each with its own character: Ásgarðr (gods), Miðgarðr (humans), Vanaheimr (fertility), Álfheimr (light Elves), Svartálfaheimr (dark Elves), Niflheimr (ice), Muspellheimr (fire), Jötunheimr (giants), and Hel (the dead).

The Nine-World Narrative Framework maps each mythological world to a dramatic register:

| Norse World | Dramatic Register | Emotional Tone | Narrative Function |
|------------|-----------------|----------------|-------------------|
| Ásgarðr | Triumph | Exalted, heroic | Protagonist achieves goal |
| Miðgarðr | Everyday | Mundane, comfortable | Normal life, contrast |
| Vanaheimr | Romance | Warm, tender | Relationships deepen |
| Álfheimr | Wonder | Awe, discovery | New worlds, revelations |
| Svartálfaheimr | Cunning | Clever, scheming | Intrigue, manipulation |
| Niflheimr | Melancholy | Cold, sorrowful | Loss, longing, passage |
| Muspellheimr | Crisis | Urgent, dangerous | Threat, disaster, combat |
| Jötunheimr | Struggle | Persevering, defiant | Challenge, obstacle |
| Hel | Tragedy | Dark, final | Death, loss, aftermath |

A narrative engine tracks which "world" the story currently occupies and manages transitions between registers. A story that stays in Miðgarðr (Everyday) becomes boring. A story that stays in Muspellheimr (Crisis) becomes exhausting. The engine must manage register transitions to create dramatic rhythm.

### Required Reading

- McKee, R. (1997). *Story: Substance, Structure, Style, and the Principles of Screenwriting*. HarperCollins.
- Propp, V. (1928). *Morphology of the Folktale*. (Translated 1968, University of Texas Press.)
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13: "The Skald's Loom: Narrative in World Models." University of Yggdrasil Press.

### Discussion Questions

1. The Nine-World Narrative Framework maps Norse mythology to dramatic registers. Is this mapping universal, or is it culturally specific? Would a different mythological system (Greek, Hindu, Chinese) produce different dramatic registers?

2. An AI agent that perceives the world narratively ("I am in the rising action") may make different decisions than one that perceives it purely logically ("X% probability of success"). Is narrative perception a cognitive bias or a valid reasoning strategy?

3. Consider a world simulation without a narrative engine — pure emergence. Under what conditions would meaningful stories emerge without narrative structure? Under what conditions would they not?

---

## Lecture 2: Plot Structure — The Bones of Story

### The Three-Act Structure

The most fundamental narrative structure is the three-act structure:

- **Act I (Setup):** Introduce the world, characters, and the inciting incident that disrupts the status quo.
- **Act II (Confrontation):** The protagonist pursues their goal, encountering obstacles and complications. Stakes rise.
- **Act III (Resolution):** The protagonist confronts the final obstacle and the story resolves — triumph, tragedy, or ambivalence.

This structure is universal across cultures and media. It maps naturally to world simulation:

- **Act I:** The simulation starts. NPCs go about their lives. An event occurs (fire, invasion, festival) that draws the agent into action.
- **Act II:** The agent pursues their goal. The simulation generates obstacles (enemy NPCs, resource shortages, moral dilemmas). Stakes rise (more NPCs affected, bigger consequences).
- **Act III:** The agent confronts the final obstacle. The simulation generates the climax (boss fight, negotiation, sacrifice). Resolution occurs.

### The Dramatic Arc

Within the three-act structure, dramatic tension rises and falls in a pattern called the dramatic arc:

```
Tension
  │           ╱╲
  │          ╱  ╲     ╱╲
  │      ╱╲ ╱    ╲   ╱  ╲
  │     ╱  ╲╱      ╲ ╱    ╲
  │    ╱             ╲╱      ╲
  │───╱──────────────────────────→ Time
     Act I    Act II     Act III
     Setup   Confrontation  Resolution
```

The dramatic arc has five key points:

1. **Inciting Incident (Act I → Act II):** The event that disrupts the status quo and begins the story.
2. **First Plot Point (end of Act I):** The protagonist commits to the quest.
3. **Midpoint (center of Act II):** The story shifts direction. Stakes become personal.
4. **Second Plot Point (end of Act II → Act III):** The final obstacle appears. All seems lost.
5. **Climax (Act III):** The protagonist confronts the final obstacle.

### Plot Points and World Events

The narrative engine maps dramatic plot points to world events:

```python
class PlotTracker:
    """Track plot structure within a world simulation."""
    
    def __init__(self):
        self.current_act = 1
        self.plot_points = []  # List of achieved plot points
        self.tension_level = 0.0  # Current dramatic tension (0.0-1.0)
        self.tension_history = []  # Track tension over time
    
    def update(self, event: WorldEvent, world_state: WorldState):
        """Update plot structure based on a world event."""
        
        # Check if this event is a plot point
        if self.is_inciting_incident(event, world_state):
            self.plot_points.append(("inciting_incident", event))
            self.current_act = 2
            self.tension_level = 0.3
        
        elif self.is_first_plot_point(event, world_state):
            self.plot_points.append(("first_plot_point", event))
            self.tension_level = 0.5
        
        elif self.is_midpoint(event, world_state):
            self.plot_points.append(("midpoint", event))
            self.tension_level = 0.7
        
        elif self.is_second_plot_point(event, world_state):
            self.plot_points.append(("second_plot_point", event))
            self.current_act = 3
            self.tension_level = 0.9
        
        elif self.is_climax(event, world_state):
            self.plot_points.append(("climax", event))
            self.tension_level = 1.0
        
        # Track tension over time
        self.tension_history.append(self.tension_level)
```

### Required Reading

- McKee, R. (1997). *Story*, Chapters 5–7.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.

### Discussion Questions

1. The three-act structure assumes a single protagonist. But world simulations have many agents. How should the narrative engine handle multiple protagonists with different dramatic arcs?

2. Dramatic tension is measured on a 0–1 scale. But different events have different tension values for different characters. How should the engine compute tension when characters have different stakes?

3. The inciting incident "disrupts the status quo." But in a world simulation, the status quo is constantly being disrupted by minor events. How does the engine distinguish an inciting incident from routine disruption?

---

## Lecture 3: Character Arcs — The Journey of the Self

### The Character Arc

A character arc is the transformation a character undergoes during the story. The three classic arcs:

1. **Positive Arc:** The character starts flawed, faces challenges, and transforms into a better version of themselves. (e.g., Rurik learns to trust others after a lifetime of isolation.)

2. **Negative Arc:** The character starts well-intentioned, faces challenges, and descends into a worse version of themselves. (e.g., Sigrún starts as a healer but becomes a tyrant after gaining power.)

3. **Flat Arc:** The character does not change, but their steadfastness changes the world around them. (e.g., A wise elder who remains compassionate despite all trials.)

### Arc Structure in the World Model

The narrative engine tracks character arcs as trajectories through emotional/theme space:

```python
@dataclass
class CharacterArc:
    """Track a character's arc through the story."""
    character_id: str
    start_state: CharacterState    # Who they are at the beginning
    current_state: CharacterState  # Who they are now
    arc_type: str                  # "positive", "negative", "flat"
    milestones: List[ArcMilestone]  # Key transformation points
    completion: float              # 0.0 to 1.0 — how far through the arc
    
    def update(self, event: WorldEvent):
        """Update the arc based on a world event."""
        # Check if the event is a milestone for this character
        for milestone in self.get_pending_milestones():
            if milestone.matches(event):
                self.milestones.append(milestone)
                self.current_state = milestone.transform(self.current_state)
                self.completion = self.compute_completion()
    
    def compute_completion(self) -> float:
        """How far through the arc is this character?"""
        achieved = len(self.milestones)
        total = len(self.get_expected_milestones())
        return achieved / total if total > 0 else 0.0
```

### Arc Milestones

Arc milestones are the key transformation points in a character's journey. For a positive arc:

1. **The Lie:** The character believes a falsehood about themselves or the world. (e.g., "I must always be alone.")
2. **The Shadow:** The character encounters evidence that contradicts their lie. (e.g., A friend helps them selflessly.)
3. **The Choice:** The character faces a choice that requires leaving the lie behind. (e.g., Trust the friend or reject them.)
4. **The Truth:** The character embraces the truth and transforms. (e.g., "I can trust others.")
5. **The Resolution:** The character acts on the truth and completes the arc. (e.g., Leads a team to victory.)

### Multi-Arc Coordination

When multiple characters have concurrent arcs, the narrative engine must coordinate their milestones:

```python
class ArcCoordinator:
    """Coordinate multiple character arcs."""
    
    def __init__(self, arcs: List[CharacterArc]):
        self.arcs = arcs
    
    def find_crossover_events(self) -> List[CrossoverEvent]:
        """Find events that are milestones for multiple characters."""
        crossovers = []
        for i, arc_a in enumerate(self.arcs):
            for j, arc_b in enumerate(self.arcs):
                if i >= j:
                    continue
                for m_a in arc_a.get_pending_milestones():
                    for m_b in arc_b.get_pending_milestones():
                        if m_a.overlaps(m_b):
                            crossovers.append(CrossoverEvent(
                                arc_a=arc_a, milestone_a=m_a,
                                arc_b=arc_b, milestone_b=m_b
                            ))
        return crossovers
```

### Required Reading

- Truby, J. (2007). *The Anatomy of Story: 22 Steps to Becoming a Master Storyteller*. Farrar, Straus and Giroux.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.

### Discussion Questions

1. Character arcs assume characters *can* change. But in a world simulation, NPCs have fixed behavioral parameters. How much can an NPC realistically change? Should arcs be planned by the narrative engine, or should they emerge from NPC behavior?

2. The flat arc ("the character doesn't change, but changes the world") is powerful but hard to model. How does a steadfast character affect the world without themselves transforming?

3. Multi-arcs with crossover events create rich narrative texture. But they also create narrative complexity — too many concurrent arcs can confuse the player. How should the engine balance narrative richness with narrative clarity?

---

## Lecture 4: Thematic Development — The Bones Beneath the Bones

### Theme as Organizing Principle

Beneath plot and character is theme — the underlying meaning that gives the story significance. Theme is not stated explicitly; it emerges through the interplay of plot, character, and dramatic register.

Common themes in world simulation:

- **Trust vs. Isolation:** Can the agent trust others? What are the costs of trust and isolation?
- **Power vs. Responsibility:** What does the agent do with power? Who bears the consequences?
- **Freedom vs. Safety:** What will the agent sacrifice for freedom? What will they sacrifice for safety?
- **Past vs. Future:** How does the agent's history shape their future? Can they escape their past?
- **Individual vs. Community:** When does the agent prioritize themselves over the group?

### Thematic Tracking

The narrative engine tracks theme as a vector of thematic scores:

```python
class ThematicTracker:
    """Track thematic development in the world simulation."""
    
    def __init__(self):
        self.themes = {
            "trust_vs_isolation": 0.0,    # -1.0 = isolation, +1.0 = trust
            "power_vs_responsibility": 0.0,  # -1.0 = irresponsible power, +1.0 = responsible power
            "freedom_vs_safety": 0.0,       # -1.0 = safety at any cost, +1.0 = freedom at any cost
            "past_vs_future": 0.0,           # -1.0 = dominated by past, +1.0 = embracing future
            "individual_vs_community": 0.0,   # -1.0 = selfish, +1.0 = communal
        }
        self.theme_history = defaultdict(list)
    
    def update(self, event: WorldEvent, world_state: WorldState):
        """Update thematic scores based on a world event."""
        for theme in self.themes:
            delta = self.compute_theme_delta(theme, event, world_state)
            self.themes[theme] = max(-1.0, min(1.0, self.themes[theme] + delta))
            self.theme_history[theme].append((event.timestamp, self.themes[theme]))
    
    def compute_theme_delta(self, theme: str, event: WorldEvent, 
                           world_state: WorldState) -> float:
        """Compute the change in a thematic score from an event."""
        # This is the narrative intelligence core — each theme has its own
        # rules for how events affect the thematic score
        if theme == "trust_vs_isolation":
            if event.type == "trust_established":
                return 0.1   # Trust increases
            elif event.type == "trust_broken":
                return -0.15  # Trust violated (stronger effect)
            elif event.type == "self_isolation":
                return -0.1   # Isolation increases
        elif theme == "power_vs_responsibility":
            if event.type == "power_gained":
                return -0.05  # Power without responsibility
            elif event.type == "responsibility_accepted":
                return 0.15   # Responsibility accepted
            elif event.type == "power_abused":
                return -0.2   # Power abused (strong negative)
        return 0.0  # No thematic change
```

### Theme and Register

Themes are closely tied to dramatic registers:

- **Ásgarðr (Triumph):** Positive resolution of a thematic conflict. Trust triumphs. Power is used responsibly.
- **Muspellheimr (Crisis):** Thematic conflict at its peak. Power vs. responsibility in crisis. Freedom vs. safety at stake.
- **Niflheimr (Melancholy):** Thematic stagnation. Stuck in the negative pole. Isolation dominates.
- **Hel (Tragedy):** Thematic failure. The character chooses the wrong pole and suffers the consequences.

### Required Reading

- McKee, R. (1997). *Story*, Chapters 2–4 (on theme and thematic contradiction).
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.

### Discussion Questions

1. Thematic scores change in response to events, but the rules for computing theme deltas are manually specified. Should theme deltas be learned from data (e.g., by analyzing thousands of stories)? What are the risks of learned theme assessment?

2. A story can have multiple themes simultaneously (trust vs. isolation AND power vs. responsibility). How should the narrative engine manage theme interaction — when two themes conflict, which one takes precedence?

3. The mapping from events to theme deltas is subjective ("trust_established" → +0.1). How should the engine determine the strength and direction of thematic impact from events?

---

## Lecture 5: Dramatic Tension — The Pulse of Story

### The Tension Curve

Dramatic tension is the emotional force that drives a story forward. It rises when the stakes increase and falls when the stakes decrease or are resolved.

The tension curve is the heartbeat of the narrative:

```
Tension
  │    ╱╲    ╱╲  ╱╲
  │   ╱  ╲  ╱  ╲╱  ╲   ╱╲
  │  ╱    ╲╱        ╲ ╱  ╲
  │ ╱                ╲╱    ╲
  │╱                        ╲
  └────────────────────────────→ Time
    Setup  Rising  Crisis  Climax  Resolution
```

### The Tension Manager

The narrative engine includes a tension manager that tracks and modulates dramatic tension:

```python
class TensionManager:
    """Manage dramatic tension in the world simulation."""
    
    def __init__(self, target_curve: str = "classical"):
        self.tension = 0.0  # Current tension level
        self.target_curve = target_curve
        self.tension_history = []
        
        # Tension curves
        self.curves = {
            "classical": self._classical_curve,  # 3-act with rising action
            "episodic": self._episodic_curve,     # Series of peaks and valleys
            "ascending": self._ascending_curve,   # Continuously rising tension
            "spiral": self._spiral_curve,          # Rising tension with setbacks
        }
    
    def update(self, event: WorldEvent, story_progress: float):
        """Update tension based on event and story progress."""
        
        # Compute target tension from curve
        target = self.curves[self.target_curve](story_progress)
        
        # Compute event impact on tension
        event_impact = self.compute_event_impact(event)
        
        # Blend: tension moves toward target, modified by event impact
        self.tension = 0.7 * target + 0.2 * self.tension + 0.1 * event_impact
        self.tension = max(0.0, min(1.0, self.tension))
        
        self.tension_history.append((event.timestamp, self.tension, target))
    
    def _classical_curve(self, progress: float) -> float:
        """Classical 3-act tension curve."""
        if progress < 0.25:
            return 0.1 + 0.4 * (progress / 0.25)  # Setup: low to medium
        elif progress < 0.75:
            return 0.5 + 0.3 * ((progress - 0.25) / 0.5)  # Rising: medium to high
        else:
            return 0.8 - 0.8 * ((progress - 0.75) / 0.25)  # Resolution: high to low
    
    def compute_event_impact(self, event: WorldEvent) -> float:
        """How much does this event affect tension?"""
        impact_map = {
            "combat_start": 0.3,
            "combat_end": -0.2,
            "ally_joins": 0.1,
            "ally_lost": 0.4,
            "discovery": 0.15,
            "setback": 0.3,
            "resolution": -0.3,
        }
        return impact_map.get(event.type, 0.0)
```

### Tension and Register Transitions

The tension manager works with the register tracker to manage dramatic register transitions:

- **Low tension → Miðgarðr (Everyday):** When tension drops, the register transitions to Miðgarðr for rest and character development.
- **Rising tension → Jötunheimr (Struggle):** As tension rises, the register moves to Jötunheimr for challenges.
- **Peak tension → Muspellheimr (Crisis):** At peak tension, the register jumps to Muspellheimr for crisis and danger.
- **Resolution → Ásgarðr (Triumph) or Hel (Tragedy):** At story's end, the register resolves based on the outcome.

### Lab 1: Building a Tension Manager

In this lab, you will build a tension manager for a village simulation:

1. Define the dramatic tension curve for a 100-tick story.
2. Implement the TensionManager with at least 4 tension curves.
3. Map village events to tension impacts.
4. Visualize the tension curve over time.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Yorke, J. (2014). *Into the Woods: A Five-Act Journey into Story and Structure*. Penguin.

### Discussion Questions

1. The tension curve blends target tension (70%) with current tension (20%) and event impact (10%). These weights determine how quickly tension responds to events. What is the right balance? Too responsive: tension swings wildly. Too sluggish: tension doesn't reflect the story.

2. Different players have different tension preferences. Some enjoy constant action (Muspellheimr). Others prefer quiet character moments (Vanaheimr). How should the narrative engine adjust tension curves for different player preferences?

3. Tension can be generated by the narrative engine (engine-driven events) or by player actions (player-driven tension). How should the engine balance engine-driven and player-driven tension?

---

## Lecture 6: The Nine-World Narrative Framework — Register Transitions

### Register Tracking

The narrative engine tracks which dramatic register the story currently occupies:

```python
class RegisterTracker:
    """Track which dramatic register the story currently occupies."""
    
    NINE_WORLDS = {
        "asgard": {"tone": "exalted", "function": "triumph"},
        "midgard": {"tone": "mundane", "function": "everyday"},
        "vanaheim": {"tone": "warm", "function": "romance"},
        "alfheim": {"tone": "awe", "function": "wonder"},
        "svartalfaheim": {"tone": "clever", "function": "cunning"},
        "niflheim": {"tone": "cold", "function": "melancholy"},
        "muspellheim": {"tone": "urgent", "function": "crisis"},
        "jotunheim": {"tone": "defiant", "function": "struggle"},
        "hel": {"tone": "dark", "function": "tragedy"},
    }
    
    def __init__(self):
        self.current_register = "midgard"  # Start in everyday
        self.register_history = [("midgard", 0.0)]  # (register, timestamp)
        self.transition_rules = self._build_transition_rules()
    
    def suggest_transition(self, tension: float, theme: Dict[str, float],
                          event: WorldEvent) -> str:
        """Suggest a register transition based on current state."""
        
        # High tension → crisis or struggle
        if tension > 0.8:
            if theme.get("power_vs_responsibility", 0) < -0.5:
                return "muspellheim"  # Crisis
            elif theme.get("individual_vs_community", 0) < -0.5:
                return "jotunheim"  # Struggle
            else:
                return "muspellheim"  # Default to crisis
        
        # Medium tension → cunning or wonder
        elif tension > 0.5:
            if theme.get("trust_vs_isolation", 0) < -0.3:
                return "svartalfaheim"  # Cunning (intrigue)
            else:
                return "alfheim"  # Wonder (discovery)
        
        # Low tension → everyday or romance
        elif tension > 0.2:
            if theme.get("individual_vs_community", 0) > 0.3:
                return "vanaheim"  # Romance (relationships)
            else:
                return "midgard"  # Everyday
        
        # Very low tension → melancholy or rest
        else:
            return "midgard"  # Rest
    
    def transition(self, new_register: str, timestamp: float):
        """Transition to a new register."""
        self.current_register = new_register
        self.register_history.append((new_register, timestamp))
```

### Register Transition Rules

Not all register transitions are equally valid. Some transitions are smooth (Miðgarðr → Vanaheimr: everyday → romance). Others are jarring (Miðgarðr → Muspellheimr: everyday → crisis — but this is exactly the inciting incident!).

The narrative engine uses transition rules to determine whether a transition is valid and how it should be handled:

- **Smooth transitions:** Gradual shift between adjacent registers. (Miðgarðr → Vanaheimr.)
- **Sharp transitions:** Sudden jump between distant registers. (Miðgarðr → Muspellheimr — the inciting incident!)
- **Forbidden transitions:** Jumps that break narrative logic. (Vanaheimr → Hel — romance → tragedy — is possible but must be earned through dramatic buildup.)

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Campbell, J. (1949). *The Hero with a Thousand Faces*. Pantheon Books.

### Discussion Questions

1. The register tracker suggests transitions based on tension and theme. But what about character state? A grieving character in Miðgarðr (everyday) may experience the world as Niflheimr (melancholy). Should register transitions be character-specific?

2. Forbidden transitions are "forbidden" in narrative logic. But some of the most powerful stories break narrative rules. When should the engine allow forbidden transitions?

3. The Nine Worlds map to emotional registers. But emotions are complex — a character might feel triumphant AND melancholic simultaneously (bittersweet victory). How should the engine handle mixed emotional registers?

---

## Lecture 7: Emergent Narrative — When the World Tells Its Own Story

### Planned vs. Emergent

There are two approaches to narrative in world simulation:

1. **Planned narrative:** The story is authored in advance. The engine guides the player through predetermined plot points. (e.g., most linear RPGs.)

2. **Emergent narrative:** The story arises from the interaction of game systems, NPC behavior, and player choices. No one authors the story; it emerges from the simulation. (e.g., Dwarf Fortress, RimWorld.)

The Skald's Loom takes the emergent approach — the narrative engine does not *create* stories, it *perceives* and *structures* stories that arise from the simulation.

### Narrative Perception

The narrative engine perceives stories by analyzing world events for narrative patterns:

```python
class NarrativePerceiver:
    """Perceive narrative patterns in world events."""
    
    def perceive(self, events: List[WorldEvent], world_state: WorldState) -> List[NarrativePattern]:
        """Identify narrative patterns in a sequence of events."""
        patterns = []
        
        # Pattern 1: Quest (goal → obstacle → resolution)
        quest = self.detect_quest(events, world_state)
        if quest:
            patterns.append(quest)
        
        # Pattern 2: Betrayal (trust → deception → revelation)
        betrayal = self.detect_betrayal(events, world_state)
        if betrayal:
            patterns.append(betrayal)
        
        # Pattern 3: Romance (meeting → attraction → conflict → resolution)
        romance = self.detect_romance(events, world_state)
        if romance:
            patterns.append(romance)
        
        # Pattern 4: Sacrifice (dilemma → choice → consequence)
        sacrifice = self.detect_sacrifice(events, world_state)
        if sacrifice:
            patterns.append(sacrifice)
        
        # Pattern 5: Redemption (fall → consequence → atonement → forgiveness)
        redemption = self.detect_redemption(events, world_state)
        if redemption:
            patterns.append(redemption)
        
        return patterns
```

### Narrative Structure Without Authorship

The key insight of emergent narrative is that story structure arises from causal relationships between events, not from authorship. The narrative engine's job is to:

1. **Perceive:** Identify narrative patterns in the stream of events.
2. **Structure:** Organize perceived patterns into story arcs (beginning, middle, end).
3. **Enhance:** Gently guide the simulation toward more satisfying narrative structures (by adjusting NPC behavior, event probabilities, or agent suggestions).
4. **Present:** Communicate the narrative to the player in a compelling way (through dialogue, description, or UI).

The engine does not *write* the story. It *curates* the story that the simulation tells.

### Lab 2: Building a Narrative Perceiver

In this lab, you will build a narrative perceiver:

1. Define 5 narrative patterns (quest, betrayal, romance, sacrifice, redemption).
2. Implement pattern detection functions for each.
3. Feed 100 random world events through the perceiver and identify narrative patterns.
4. Evaluate the perceiver's accuracy: are detected patterns genuine narrative arcs or false positives?

### Required Reading

- Aarseth, E. (2012). "A Narrative Theory of Games." *Proceedings of the International Conference on the Foundations of Digital Games*.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.

### Discussion Questions

1. Emergent narrative depends on the simulation generating interesting events. But random simulation often generates *uninteresting* events. How can the narrative engine guide the simulation toward narrative richness without violating emergence?

2. The narrative perceiver detects patterns that "look like stories" but may not be causally connected. A sequence of events that resembles a quest pattern might be coincidence. How can the engine distinguish genuine narrative from coincidental pattern?

3. "Enhancing" emergent narrative means guiding NPC behavior or adjusting event probabilities. But this reduces the simulation's fidelity to its rules. Is a guided simulation still "emergent"? Where is the line between guidance and authorship?

---

## Lecture 8: Multi-Arc Story Weaving — The Skald's Loom

### The Loom Metaphor

A skald weaves stories on a loom — threads of character, plot, theme, and register交织 together into a tapestry of narrative. The Skald's Loom is the narrative engine's system for weaving multiple character arcs, plot threads, thematic developments, and register transitions into a coherent whole.

### The Loom Architecture

```
┌────────────────────────────────────────────────┐
│                   Skald's Loom                   │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Plot     │ │ Character│ │    Theme         │ │
│  │  Tracker  │ │  Arc     │ │    Tracker        │ │
│  │           │ │ Tracker  │ │                  │ │
│  └─────┬────┘ └────┬─────┘ └────┬─────────────┘ │
│        │            │            │               │
│        └────────────┼────────────┘               │
│                     │                             │
│              ┌──────┴──────┐                      │
│              │  Tension     │                      │
│              │  Manager     │                      │
│              └──────┬──────┘                      │
│                     │                             │
│              ┌──────┴──────┐                      │
│              │  Register    │                      │
│              │  Tracker     │                      │
│              └──────┬──────┘                      │
│                     │                             │
│              ┌──────┴──────┐                      │
│              │  Narrative   │                      │
│              │  Perceiver   │                      │
│              └─────────────┘                      │
└────────────────────────────────────────────────┘
```

### Weaving Algorithm

The weaving algorithm combines all narrative threads into a coherent story:

```python
class SkaldsLoom:
    """The Skald's Loom — weave multiple narrative threads."""
    
    def __init__(self):
        self.plot_tracker = PlotTracker()
        self.arc_tracker = ArcCoordinator([])
        self.theme_tracker = ThematicTracker()
        self.tension_manager = TensionManager()
        self.register_tracker = RegisterTracker()
        self.narrative_perceiver = NarrativePerceiver()
        self.story_log = []
    
    def weave(self, event: WorldEvent, world_state: WorldState) -> NarrativeState:
        """Weave all narrative threads after a world event."""
        
        # Update each thread
        self.plot_tracker.update(event, world_state)
        self.arc_tracker.update(event, world_state)
        self.theme_tracker.update(event, world_state)
        self.tension_manager.update(event, self.plot_tracker.progress())
        
        # Compute register transition
        suggested_register = self.register_tracker.suggest_transition(
            self.tension_manager.tension,
            self.theme_tracker.themes,
            event
        )
        self.register_tracker.transition(suggested_register, event.timestamp)
        
        # Perceive narrative patterns
        patterns = self.narrative_perceiver.perceive(
            self.story_log[-100:],  # Recent events
            world_state
        )
        
        # Compose narrative state
        narrative = NarrativeState(
            act=self.plot_tracker.current_act,
            plot_points=self.plot_tracker.plot_points,
            active_arcs=self.arc_tracker.active_arcs(),
            themes=dict(self.theme_tracker.themes),
            tension=self.tension_manager.tension,
            register=self.register_tracker.current_register,
            patterns=patterns
        )
        
        self.story_log.append((event, narrative))
        return narrative
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Harmon, J. (2012). "Story Embryo." Channel 101. (For the story circle structure.)

### Discussion Questions

1. The Skald's Loom weaves five threads (plot, character, theme, tension, register). Are there other narrative threads that should be included? (e.g., pacing, setting, symbol?)

2. The weaving algorithm processes each thread independently and then composes them. But threads influence each other — a plot event affects character arcs, which affects tension, which affects register. How should the engine handle thread interactions?

3. The narrative perceiver identifies patterns that "look like" stories. But what about anti-patterns — sequences of events that actively *prevent* narrative coherence? How should the engine detect and resolve anti-patterns?

---

## Lecture 9: Narrative Engine Architecture — The Skald's API

### The Narrative Engine Service

The narrative engine is exposed as a service:

```python
class NarrativeEngine:
    """The Skald's Loom narrative engine service."""
    
    def get_narrative_state(self, world_id: str) -> NarrativeState:
        """Get the current narrative state."""
        ...
    
    def process_event(self, world_id: str, event: Dict) -> NarrativeState:
        """Process a world event through the narrative engine."""
        ...
    
    def suggest_action(self, world_id: str, npc_id: str) -> ActionSuggestion:
        """Suggest an action for an NPC based on narrative goals."""
        ...
    
    def get_story_summary(self, world_id: str) -> StorySummary:
        """Get a summary of the story so far."""
        ...
    
    def forecast_register(self, world_id: str, horizon: int = 10) -> List[str]:
        """Forecast dramatic register over the next N ticks."""
        ...
```

### NPC Narrative Guidance

One of the narrative engine's most powerful features is NPC guidance — suggesting actions for NPCs that enhance narrative quality without violating NPC autonomy:

```python
class NPCGuide:
    """Guide NPC behavior to enhance narrative quality."""
    
    def suggest_action(self, npc_id: str, world_state: WorldState,
                      narrative: NarrativeState) -> ActionSuggestion:
        """Suggest an action for an NPC."""
        
        # What would the NPC normally do?
        default_action = npc.decide(world_state)
        
        # What would enhance the narrative?
        narrative_goal = self.compute_narrative_goal(narrative)
        
        # Find an action that satisfies both NPC personality and narrative
        narrative_action = self.find_aligned_action(
            npc_id, world_state, narrative_goal
        )
        
        # Blend: 70% NPC autonomy, 30% narrative guidance
        if self.actions_aligned(default_action, narrative_action):
            return ActionSuggestion(
                action=narrative_action,
                reason="aligned_with_narrative",
                confidence=0.9
            )
        else:
            # Conflict between NPC autonomy and narrative
            return ActionSuggestion(
                action=default_action,  # Honor NPC autonomy
                reason="narrative_misaligned",
                narrative_alternative=narrative_action,
                confidence=0.5
            )
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Mateas, M. & Stern, A. (2003). "Façade: A One-Act Interactive Drama." *Proceedings of the International Conference on Advances in Computer Entertainment Technology*.

### Discussion Questions

1. NPC narrative guidance (30% narrative, 70% autonomy) is a balance. If the narrative goal is too strong, NPCs become puppets. If too weak, stories don't form. What is the right balance, and should it change over the course of a story?

2. The suggest_action method returns both a "default action" (what the NPC would normally do) and a "narrative alternative" (what would enhance the story). The NPC can choose either. But if the NPC always chooses the default, the narrative suffers. How can the engine gently guide NPCs toward narrative-rich choices without coercion?

3. The narrative engine is a service that the world simulation calls. But narrative perception requires a history of events. How should the engine handle cold starts (no history yet)?

---

## Lecture 10: Player as Protagonist — The Agent's Narrative Role

### The Protagonist Problem

In most storytelling, the protagonist is chosen by the author. In emergent narrative, the protagonist is chosen by the simulation — or more precisely, the simulation designates one agent as the "camera follows" character.

But in a world simulation with player interaction, the player is the protagonist. The narrative engine must treat the player as the central character:

1. **Plot points** should be triggered by player actions or directed at the player.
2. **Character arcs** should involve the player as the primary arc character.
3. **Tension curves** should be calibrated to the player's emotional state.
4. **Register transitions** should respond to the player's actions.

### The Protagonist Interface

```python
class ProtagonistInterface:
    """Interface between the narrative engine and the player."""
    
    def get_player_state(self, player_id: str) -> PlayerNarrativeState:
        """Get the player's current narrative state."""
        return PlayerNarrativeState(
            player_id=player_id,
            recent_actions=self.get_recent_actions(player_id),
            emotional_state=self.infer_emotional_state(player_id),
            current_goal=self.infer_current_goal(player_id),
            social_connections=self.get_social_connections(player_id),
            arc_progress=self.get_arc_progress(player_id)
        )
    
    def infer_emotional_state(self, player_id: str) -> EmotionalState:
        """Infer the player's emotional state from their actions."""
        # Heuristic: use recent action patterns to infer emotion
        actions = self.get_recent_actions(player_id)
        
        if self.is_aggressive(actions):
            return EmotionalState.FRUSTRATED
        elif self.is_exploratory(actions):
            return EmotionalState.CURIOUS
        elif self.is_social(actions):
            return EmotionalState.CONNECTED
        elif self.is_withdrawn(actions):
            return EmotionalState.ISOLATED
        else:
            return EmotionalState.NEUTRAL
```

### Narrative Feedback Loop

The narrative engine creates a feedback loop between player actions and narrative structure:

1. **Player acts** → The world simulation processes the action.
2. **Engine perceives** → The narrative engine identifies narrative patterns.
3. **Engine adjusts** → The engine adjusts tension, register, and NPC guidance.
4. **World responds** → The simulation responds with new events.
5. **Player acts again** → The loop continues.

This feedback loop ensures that the narrative responds to the player rather than ignoring them.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Murray, J. (1997). *Hamlet on the Holodeck: The Future of Narrative in Cyberspace*. MIT Press.

### Discussion Questions

1. Inferring the player's emotional state from their actions is heuristic and may be wrong. How should the engine handle incorrect emotional inference? (e.g., inferring "frustrated" when the player is actually "focused".)

2. The player may resist the narrative engine's attempts to guide the story (e.g., ignoring the inciting incident). How should the engine handle player resistance? Should it adapt, or persist?

3. In multiplayer simulations, multiple players may be protagonists with different narrative arcs. How should the engine handle conflicting protagonist arcs?

---

## Lecture 11: Evaluation — Measuring Narrative Quality

### Narrative Metrics

How do we know if a narrative engine produces good stories? We need **narrative metrics** — quantitative measures of narrative quality:

1. **Coherence:** Do the events form a logically connected sequence? (Causal coherence, thematic coherence, character coherence.)
2. **Variety:** Does the story visit multiple registers, or stay in one tone?
3. **Pacing:** Does the tension curve have natural rhythm (peaks and valleys)?
4. **Player Agency:** Does the player's actions meaningfully affect the story?
5. **Character Development:** Do characters change over the course of the story?

```python
class NarrativeEvaluator:
    """Evaluate narrative quality of a story."""
    
    def evaluate(self, story: List[NarrativeState]) -> NarrativeQuality:
        """Evaluate the narrative quality of a story."""
        
        coherence = self.compute_coherence(story)
        variety = self.compute_variety(story)
        pacing = self.compute_pacing(story)
        agency = self.compute_agency(story)
        development = self.compute_development(story)
        
        return NarrativeQuality(
            coherence=coherence,    # 0.0–1.0
            variety=variety,        # 0.0–1.0
            pacing=pacing,          # 0.0–1.0
            agency=agency,          # 0.0–1.0
            development=development, # 0.0–1.0
            overall=(coherence + variety + pacing + agency + development) / 5
        )
    
    def compute_coherence(self, story: List[NarrativeState]) -> float:
        """Compute narrative coherence."""
        causal = self.causal_coherence(story)  # Do events causally follow?
        thematic = self.thematic_coherence(story)  # Do themes develop consistently?
        character = self.character_coherence(story)  # Do characters act consistently?
        return (causal + thematic + character) / 3
    
    def compute_variety(self, story: List[NarrativeState]) -> float:
        """Compute register variety."""
        registers = set(s.register for s in story)
        return len(registers) / 9  # Fraction of Nine Worlds visited
    
    def compute_pacing(self, story: List[NarrativeState]) -> float:
        """Compute pacing quality."""
        tensions = [s.tension for s in story]
        # Good pacing has peaks and valleys
        variance = np.var(tensions)
        # Good pacing has some peaks above 0.7
        peaks = sum(1 for t in tensions if t > 0.7)
        # Good pacing has some valleys below 0.3
        valleys = sum(1 for t in tensions if t < 0.3)
        
        pacing_score = min(variance / 0.1, 1.0) * 0.3 + \
                      min(peaks / len(story) * 5, 1.0) * 0.35 + \
                      min(valleys / len(story) * 5, 1.0) * 0.35
        return pacing_score
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 13.
- Elson, D. (2012). *Dramavis: Story Visualization and Drama Analysis*. PhD Thesis, Columbia University.

### Discussion Questions

1. Narrative quality is ultimately subjective. The metrics above (coherence, variety, pacing, agency, development) are proxies for subjective quality. Are there other important metrics? What about emotional impact, memorability, or replayability?

2. Pacing quality is measured by tension variance, peaks, and valleys. But a story with constant tension variance may feel *too* varied — like a roller coaster with no rest. How should pacing balance variety with rhythm?

3. How would you evaluate the narrative engine's output against human-authored stories? What is the benchmark for "good" narrative in a simulated world?

---

## Lecture 12: The Skald's Loom — Course Synthesis and Capstone

### Summary: The Threads of Story

We began with the question: "Why stories?" and answered: because narrative is how humans understand complex systems. Without narrative, events are data; with narrative, events are meaning.

The Skald's Loom weaves five threads into a coherent tapestry:

1. **Plot Structure (Lecture 2):** The bones of story — three-act structure, dramatic arc, plot points mapped to world events.
2. **Character Arcs (Lecture 3):** The journey of the self — positive, negative, and flat arcs, milestones, and multi-arc coordination.
3. **Thematic Development (Lecture 4):** The bones beneath the bones — thematic vectors, theme deltas, and theme-register interaction.
4. **Dramatic Tension (Lecture 5):** The pulse of story — tension curves, event impacts, and tension-register coupling.
5. **Register (Lectures 6–7):** The Nine Worlds — dramatic registers, transitions, and emergent narrative perception.

These five threads come together in the Skald's Loom (Lecture 8) — the complete narrative engine that weaves all threads into a coherent story. The Loom perceives, structures, enhances, and presents the narrative that emerges from the simulation.

### Capstone Project: The Skald's Loom

Your capstone project is to build a complete narrative engine:

1. **Plot tracker:** Three-act structure with plot point detection.
2. **Character arc tracker:** At least 3 concurrent character arcs with milestone detection.
3. **Theme tracker:** At least 3 thematic vectors with event-driven deltas.
4. **Tension manager:** At least 2 tension curves with event-driven updates.
5. **Register tracker:** All Nine Worlds with transition logic.
6. **Narrative perceiver:** At least 3 pattern detectors (quest, betrayal, romance).
7. **NPC guide:** Narrative-enhanced NPC action suggestion.
8. **Protagonist interface:** Player narrative state inference.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with type hints and docstrings).
2. A village simulation with 5 NPCs, each with a character arc.
3. 10 narrative scenarios showing different register transitions.
4. A story summary for each scenario.
5. Narrative quality evaluation for each scenario.
6. A design document (5–8 pages) describing your Skald's Loom architecture.

### The Loom Is Woven

The skald sits at the loom, threads of story in hand. The world provides the thread — events, characters, causality. The skald provides the pattern — plot, arc, theme, tension, register. Together, they weave a tapestry of meaning that transforms simulation into story.

**ᚹ Wunjo — Joy. The story is told.**
**ᛒ Berkanan — Birch. The story grows.**
**ᛗ Mannaz — Humanity. The story is about us.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᚹ — The skald weaves. The story lives.*