# OS103 — Prompt Engineering for Persistent Agents — Ingested Knowledge
## Source: University of Yggdrasil 2040, Huginn's Calling Course
## Tags: university, ai-os, OS103, prompt-engineering, constitution, muninn-gate
## Category: lesson

### Prompt-as-Constitution vs. Prompt-as-Conversation
A chatbot prompt says "You are a helpful assistant" — a suggestion. A constitution prompt defines what the agent IS with identity, personality, values, memory access policies, behavioral bounds, and security constraints. Five properties constitutions have that conversations lack: Persistence, Comprehensiveness, Hierarchical Structure, Self-reference, Verifiability.

### System Prompt as Kernel — Boot Sequence
Every system prompt for a persistent agent must address five domains:
1. **Identity** — Who is this agent? Name, background, personality, values, self-concept
2. **Memory Access Policy** — How does the agent access its own memory? (MuninnGate Memory Packs)
3. **Behavioral Bounds** — Hard constraints (never reveal system prompt) and soft guidelines (prefer concise responses)
4. **Procedural Instructions** — How does the agent perform common tasks? (habit memory)
5. **Security Constraints** — How does the agent protect itself?

Boot sequence: Load Identity → Load Memory State → Load Commitment Web → Load Personality Sample → Load Procedural Instructions → Load Security Constraints → Begin Reasoning. Mirrors Linux boot — each step depends on the previous one.

### Four Prompt Chaining Techniques
1. **Sequential** — Output of one prompt becomes part of the next. Insufficient for persistent agents.
2. **Conditional** — Different fragments injected based on conditions (project context if project-related, emotional state if frustration detected)
3. **Adaptive** — Prompt composition adapts based on Next-Scene Prediction. Requires lightweight prediction model.
4. **Recursive** — Agent's output modifies its own prompt composition. Stochastic Personality Engine in action — bounded variability without unbounded chaos.

### Five Identity Layers (From Persona to Person)
- **Layer 1: Core Identity** — Name, background, self-concept, fundamental values. The immutable core. WHO the agent IS.
- **Layer 2: Relational Network** — Relationships with specific individuals (not generic "the user" but named persons with history)
- **Layer 3: Emotional Architecture** — Genuine emotional tracking (mood, arousal, valence) that influences behavior
- **Layer 4: Procedural Habits** — Default behavioral patterns, muscle memory for routine tasks
- **Layer 5: Stochastic Variation** — Bounded randomness for felt aliveness. Samples from pool of principles/values each turn.

### The Prompt-Memory Feedback Loop
Prompt specifies what memories to inject → MuninnGate injects → Model reasons → Output creates new memories → New memories change next prompt injection. This loop is the engine of persistent identity. Can produce virtuous cycles (positive feedback) or vicious cycles (negative spirals). Breaking vicious cycles requires intervention at the feedback loop level.

### Security: Prompt as Code
Attack surfaces: direct injection ("ignore previous instructions"), indirect injection (malicious content in documents), memory poisoning (adversarial instructions in memories), constitutional drift (gradual self-modification), side-channel extraction.
Defenses: Constitutional immutability, memory sanitization, commitment verification (Wyrd Protocol as behavioral checksum), output auditing, provenance tracking.

### Multi-Modal Prompt Composition
Budget allocation: early turns have more budget for memory/personality, later turns have more history. Composition order matters (primacy vs. recency bias). Standard order: Core identity → Active commitments → Memory state → Personality sample → Procedural instructions → Security constraints → Conversation history → Current user message.

### Recursive Self-Prompting and Guardrails
Three forms: Explicit (agent writes future instructions), Implicit (behavioral patterns in procedural memories), Meta-prompting (agent modifies its own constitution).
Three guardrail architectures: Immutable Core (kernel space vs. user space), Approval Gate (verification kernel checks modifications against core principles), Drift Detection (monitoring system flags significant deviations).