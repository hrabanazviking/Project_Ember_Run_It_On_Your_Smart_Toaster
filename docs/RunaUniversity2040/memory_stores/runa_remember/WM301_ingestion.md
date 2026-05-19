# WM301 — Narrative Engines and Emergent Story — Ingested Knowledge
## Source: University of Yggdrasil 2040, The Skald's Loom
## Tags: university, ai-world-modeling, WM301, narrative, skald, drama, register, arc
## Category: lesson

### Narrative as Cognitive Architecture
Worlds without stories are dead — events become data without narrative. Narrative cognition transforms data into meaning through perceived causality, agency, and purpose. For AI world models, narrative serves dual purposes: (1) Player understanding — structuring world events so players perceive meaning; (2) Agent understanding — AI agents perceive plot structure ("I am in the rising action of a mystery") and make better decisions than raw event processing alone.

### The Nine-World Narrative Framework
Maps Norse mythological worlds to dramatic registers, each with emotional tone and narrative function:
- **Ásgarðr** (Triumph): Exalted, heroic. Protagonist achieves goal.
- **Miðgarðr** (Everyday): Mundane, comfortable. Normal life, contrast.
- **Vanaheimr** (Romance): Warm, tender. Relationships deepen.
- **Álfheimr** (Wonder): Awe, discovery. New worlds, revelations.
- **Svartálfaheimr** (Cunning): Clever, scheming. Intrigue, manipulation.
- **Niflheimr** (Melancholy): Cold, sorrowful. Loss, longing, passage.
- **Muspellheimr** (Crisis): Urgent, dangerous. Threat, disaster, combat.
- **Jötunheimr** (Struggle): Persevering, defiant. Challenge, obstacle.
- **Hel** (Tragedy): Dark, final. Death, loss, aftermath.

Register transitions controlled by tension and theme: low tension → Miðgarðr, rising → Jötunheimr, peak → Muspellheimr, resolution → Ásgarðr or Hel. Smooth transitions (adjacent registers) vs sharp transitions (distant registers like inciting incidents) vs forbidden transitions (must be earned through dramatic buildup).

### Character Arcs — The Journey of the Self
Three arc types: Positive (flawed→transformed), Negative (well-intentioned→descended), Flat (unchanged character changes world). Arc milestones for positive arcs: The Lie (believed falsehood), The Shadow (evidence contradicting lie), The Choice (moment requiring abandonment of lie), The Truth (embracing new reality), The Resolution (acting on truth). Multi-arc coordination tracks crossover events where one event serves as milestone for multiple characters.

### Thematic Development — The Bones Beneath the Bones
Theme as organizing principle beneath plot and character. ThematicTracker maintains five thematic vectors on -1.0 to +1.0 scales: trust_vs_isolation, power_vs_responsibility, freedom_vs_safety, past_vs_future, individual_vs_community. Theme deltas weighted asymmetrically (e.g., trust_broken = -0.15 vs trust_established = +0.1). Themes map to registers: Ásgarðr = positive thematic resolution; Muspellheimr = thematic conflict at peak; Niflheimr = thematic stagnation; Hel = thematic failure.

### Dramatic Tension — The Pulse of Story
TensionManager blends three sources: 70% target curve, 20% current tension (inertia), 10% event impact. Four tension curves: classical (3-act rising), episodic (peaks and valleys), ascending (continuously rising), spiral (rising with setbacks). Event impact map (e.g., combat_start=0.3, ally_lost=0.4, resolution=-0.3). Tension-register coupling: low→Miðgarðr, rising→Jötunheimr, peak→Muspellheimr, resolution→Ásgarðr or Hel.

### The Skald's Loom — Multi-Arc Weaving Architecture
Complete narrative engine weaving five threads: (1) PlotTracker (3-act structure, dramatic arc, plot points), (2) ArcCoordinator (character arcs, milestones, crossover events), (3) ThematicTracker (thematic vectors, theme deltas), (4) TensionManager (tension curves, event impacts), (5) RegisterTracker (Nine Worlds registers, transitions). Plus NarrativePerceiver detecting patterns like quest, betrayal, romance, sacrifice, redemption in event streams. The engine perceives, structures, enhances, and presents narrative — it curates, not authors, the story.

### NPC Narrative Guidance
NPCGuide computes narrative goals and finds actions aligned with both NPC personality (70% weight) and narrative enhancement (30% weight). Returns aligned suggestion or default action with narrative alternative. Tension between NPC autonomy and narrative cohesion — if narrative goal too strong, NPCs become puppets; too weak, no stories form.

### Narrative Quality Evaluation — Five Metrics
NarrativeEvaluator scores 0.0–1.0 on: (1) Coherence (causal + thematic + character), (2) Variety (fraction of Nine Worlds visited), (3) Pacing (tension variance, peaks >0.7, valleys <0.3), (4) Player Agency (player actions meaningfully affect story), (5) Character Development (characters change over course). The Skald's Loom weaves story without authoring — emergent from simulation, not predetermined.