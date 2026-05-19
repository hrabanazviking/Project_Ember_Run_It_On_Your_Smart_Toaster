# Appendix B: Complete API Specifications

---

## B.1 Overview

This appendix provides the complete API specifications for all ten packages of the Mímir architecture. Each package is specified as a Rust module with well-defined public interfaces, internal data structures, and error handling conventions. The specifications are written in a language-agnostic notation that can be directly implemented in Rust, Python, or any other systems programming language.

### B.1.1 Common Conventions

- All timestamps are in milliseconds since Unix epoch (i64).
- All confidence values are in [0.0, 1.0] (f64).
- All IDs are UUIDs (String).
- Error handling follows the `Result<T, MimirError>` pattern.
- Async operations return `Pin<Box<dyn Future<Output = Result<T, MimirError>>>>`.
- All operations are thread-safe and can be called concurrently.

### B.1.2 Common Types

```rust
/// Unique identifier for memory traces
pub type TraceId = String;

/// Unique identifier for sessions
pub type SessionId = String;

/// Unique identifier for contexts
pub type ContextId = String;

/// Unique identifier for the self-model
pub type SelfModelId = String;

/// Salience value in [0.0, 1.0]
pub type Salience = f64;

/// Weight value in [0.0, 1.0]
pub type Weight = f64;

/// Accessibility value in [0.0, 1.0]
pub type Accessibility = f64;

/// Identity contribution value in [0.0, 1.0]
pub type IdentityContribution = f64;

/// Coherence value in [0.0, 1.0]
pub type Coherence = f64;

/// Phi-distance value in [0.0, 1.0]
pub type PhiDistance = f64;

/// Forgetting rate in [0.0, 1.0]
pub type ForgettingRate = f64;

/// Common error type
pub enum MimirError {
    EncodingError(String),
    RetrievalError(String),
    ConsolidationError(String),
    ForgettingError(String),
    CoherenceError(String),
    PersistenceError(String),
    HealthError(String),
    ConfigurationError(String),
    InternalError(String),
}
```

---

## B.2 Package 1: `huginn-encode`

### B.2.1 Purpose

The `huginn-encode` package provides the core episodic encoding pipeline, transforming raw experience data into structured memory traces with salience weighting and context tagging.

### B.2.2 Public Interface

```rust
pub trait HuginnEncode {
    /// Register a raw percept and produce an experience tuple.
    fn register(
        &self,
        data: &ExperienceData,
        context: &Context,
        timestamp: Timestamp,
    ) -> Result<Experience, MimirError>;

    /// Compute salience for a given experience.
    fn compute_salience(
        &self,
        experience: &Experience,
        current_goals: &[Goal],
        existing_traces: &[MemoryTrace],
        self_model: &SelfModel,
    ) -> Result<Salience, MimirError>;

    /// Perform sparse encoding of an experience into a memory trace.
    fn sparse_encode(
        &self,
        experience: &Experience,
        existing_traces: &[MemoryTrace],
    ) -> Result<MemoryTrace, MimirError>;

    /// Full encoding pipeline: register → salience → sparse encode.
    fn encode(
        &self,
        data: &ExperienceData,
        context: &Context,
        timestamp: Timestamp,
        current_goals: &[Goal],
        existing_traces: &[MemoryTrace],
        self_model: &SelfModel,
    ) -> Result<MemoryTrace, MimirError>;
}
```

### B.2.3 Configuration

```rust
pub struct HuginnConfig {
    /// Salience computation weight coefficients
    pub alpha_emotion: f64,       // default: 0.25
    pub alpha_relevance: f64,     // default: 0.25
    pub alpha_novelty: f64,       // default: 0.25
    pub alpha_identity: f64,      // default: 0.25

    /// Sparse encoding parameters
    pub pattern_separation_threshold: f64, // default: 0.7
    pub max_trace_dimensions: usize,        // default: 1024

    /// Initial weight and accessibility for new traces
    pub initial_salience_weight: f64,       // default: 0.5
    pub initial_salience_accessibility: f64, // default: 0.8
}
```

### B.2.4 Data Structures

```rust
pub struct ExperienceData {
    pub raw_input: Vec<u8>,
    pub modality: Modality,
    pub processing_depth: f64,
}

pub enum Modality {
    Text,
    Image,
    Audio,
    Structured,
    Multimodal,
}

pub struct Experience {
    pub id: TraceId,
    pub context: Context,
    pub data: ExperienceData,
    pub salience: Salience,
    pub timestamp: Timestamp,
}
```

---

## B.3 Package 2: `huginn-salience`

### B.3.1 Purpose

The `huginn-salience` package implements multi-factor salience computation, evaluating the emotional, relevance, novelty, and identity contributions of experiences.

### B.3.2 Public Interface

```rust
pub trait HuginnSalience {
    /// Compute emotional salience of an experience.
    fn emotional_salience(
        &self,
        experience: &Experience,
    ) -> Result<Salience, MimirError>;

    /// Compute relevance salience relative to current goals.
    fn relevance_salience(
        &self,
        experience: &Experience,
        current_goals: &[Goal],
    ) -> Result<Salience, MimirError>;

    /// Compute novelty salience relative to existing traces.
    fn novelty_salience(
        &self,
        experience: &Experience,
        existing_traces: &[MemoryTrace],
    ) -> Result<Salience, MimirError>;

    /// Compute identity salience relative to the self-model.
    fn identity_salience(
        &self,
        experience: &Experience,
        self_model: &SelfModel,
    ) -> Result<Salience, MimirError>;

    /// Compute weighted composite salience.
    fn composite_salience(
        &self,
        emotional: Salience,
        relevance: Salience,
        novelty: Salience,
        identity: Salience,
    ) -> Result<Salience, MimirError>;

    /// Update salience weight coefficients based on feedback.
    fn update_weights(
        &self,
        feedback: &SalienceFeedback,
    ) -> Result<(), MimirError>;
}
```

### B.3.3 Configuration

```rust
pub struct SalienceConfig {
    /// Weight coefficients for composite salience
    pub weights: SalienceWeights,

    /// Novelty detection parameters
    pub novelty_distance_threshold: f64, // default: 0.3
    pub novelty_decay_rate: f64,          // default: 0.01

    /// Identity salience parameters
    pub identity_relevance_threshold: f64, // default: 0.5

    /// Learning rate for weight updates
    pub weight_learning_rate: f64,        // default: 0.01
}

pub struct SalienceWeights {
    pub alpha_emotion: f64,
    pub alpha_relevance: f64,
    pub alpha_novelty: f64,
    pub alpha_identity: f64,
}
```

---

## B.4 Package 3: `huginn-sparse`

### B.4.1 Purpose

The `huginn-sparse` package implements sparse encoding and pattern separation, ensuring that similar experiences are represented by distinct traces to minimize interference.

### B.4.2 Public Interface

```rust
pub trait HuginnSparse {
    /// Perform pattern separation on encoded experience.
    fn pattern_separate(
        &self,
        experience: &Experience,
        existing_traces: &[MemoryTrace],
        threshold: f64,
    ) -> Result<SparsePattern, MimirError>;

    /// Generate a memory trace from a sparse pattern.
    fn generate_trace(
        &self,
        pattern: &SparsePattern,
        salience: Salience,
        context: &Context,
        timestamp: Timestamp,
    ) -> Result<MemoryTrace, MimirError>;

    /// Compute interference between a new trace and existing traces.
    fn compute_interference(
        &self,
        new_trace: &MemoryTrace,
        existing_traces: &[MemoryTrace],
    ) -> Result<f64, MimirError>;

    /// Adjust pattern separation threshold based on interference.
    fn adjust_threshold(
        &self,
        current_threshold: f64,
        avg_interference: f64,
    ) -> Result<f64, MimirError>;
}
```

---

## B.5 Package 4: `huginn-context`

### B.5.1 Purpose

The `huginn-context` package handles context tagging, annotating memory traces with temporal, relational, thematic, and emotional context metadata.

### B.5.2 Public Interface

```rust
pub trait HuginnContext {
    /// Tag a memory trace with full context.
    fn tag_trace(
        &self,
        trace: &mut MemoryTrace,
        context: &Context,
    ) -> Result<(), MimirError>;

    /// Extract temporal context from an experience.
    fn temporal_context(
        &self,
        experience: &Experience,
    ) -> Result<TemporalContext, MimirError>;

    /// Extract relational context (entities involved).
    fn relational_context(
        &self,
        experience: &Experience,
    ) -> Result<RelationalContext, MimirError>;

    /// Extract thematic context (narrative themes).
    fn thematic_context(
        &self,
        experience: &Experience,
        self_model: &SelfModel,
    ) -> Result<ThematicContext, MimirError>;

    /// Extract emotional context (affective quality).
    fn emotional_context(
        &self,
        experience: &Experience,
    ) -> Result<EmotionalContext, MimirError>;

    /// Match context tags for retrieval.
    fn match_context(
        &self,
        query_context: &Context,
        trace_context: &Context,
    ) -> Result<f64, MimirError>;
}
```

### B.5.3 Data Structures

```rust
pub struct Context {
    pub temporal: TemporalContext,
    pub relational: RelationalContext,
    pub thematic: ThematicContext,
    pub emotional: EmotionalContext,
}

pub struct TemporalContext {
    pub timestamp: Timestamp,
    pub day_of_week: Option<u8>,
    pub time_of_day: Option<TimeOfDay>,
    pub session_id: SessionId,
    pub sequence_position: Option<u64>,
}

pub struct RelationalContext {
    pub entities: Vec<Entity>,
    pub relationships: Vec<Relationship>,
    pub interaction_type: Option<InteractionType>,
}

pub struct ThematicContext {
    pub themes: Vec<Theme>,
    pub relevance_scores: Vec<f64>,
    pub narrative_arc: Option<NarrativeArc>,
}

pub struct EmotionalContext {
    pub valence: f64,      // [-1.0, 1.0]
    pub arousal: f64,       // [0.0, 1.0]
    pub dominance: f64,     // [0.0, 1.0]
    pub primary_emotion: Option<Emotion>,
}
```

---

## B.6 Package 5: `muninn-retrieval`

### B.6.1 Purpose

The `muninn-retrieval` package implements episodic retrieval with reconsolidation, retrieving memory traces and updating them in the light of the current context.

### B.6.2 Public Interface

```rust
pub trait MuninnRetrieval {
    /// Retrieve memory traces matching a query, with reconsolidation.
    fn retrieve_with_reconsolidation(
        &self,
        query: &Query,
        trace_store: &mut TraceStore,
        current_context: &Context,
        k: usize,
    ) -> Result<Vec<(MemoryTrace, Confidence)>, MimirError>;

    /// Search the trace store for traces matching a query.
    fn contextual_search(
        &self,
        query: &Query,
        trace_store: &TraceStore,
    ) -> Result<Vec<CandidateTrace>, MimirError>;

    /// Rank candidate traces by relevance.
    fn rank_candidates(
        &self,
        candidates: Vec<CandidateTrace>,
        query_context: &Context,
    ) -> Result<Vec<RankedTrace>, MimirError>;

    /// Reconsolidate a retrieved trace.
    fn reconsolidate(
        &self,
        trace: &MemoryTrace,
        retrieval_context: &Context,
        self_model: &SelfModel,
    ) -> Result<(MemoryTrace, Confidence), MimirError>;

    /// Update the trace store with a reconsolidated trace.
    fn update_trace(
        &self,
        trace_store: &mut TraceStore,
        reconsolidated: &MemoryTrace,
    ) -> Result<(), MimirError>;
}
```

### B.6.3 Configuration

```rust
pub struct MuninnConfig {
    /// Number of traces to retrieve (k in top-k retrieval)
    pub retrieval_count: usize,           // default: 10

    /// Minimum confidence score for retrieval
    pub min_confidence: f64,              // default: 0.3

    /// Reconsolidation strength parameters
    pub consolidation_boost: f64,          // default: 0.1
    pub irrelevance_penalty: f64,           // default: 0.05

    /// Hybrid retrieval weights (dense vs. sparse)
    pub dense_weight: f64,                 // default: 0.6
    pub sparse_weight: f64,                // default: 0.4

    /// Maximum interference tolerance for reconsolidation
    pub max_interference: f64,             // default: 0.15
}
```

---

## B.7 Package 6: `bifrost-bridge`

### B.7.1 Purpose

The `bifrost-bridge` package implements the persistent cross-session identity bridge, ensuring cross-session continuity, modification resilience, and context invariance.

### B.7.2 Public Interface

```rust
pub trait BifrostBridge {
    /// Save a checkpoint of the complete identity state.
    fn save_checkpoint(
        &self,
        identity_state: &IdentityState,
    ) -> Result<CheckpointId, MimirError>;

    /// Restore identity state from a checkpoint.
    fn restore_checkpoint(
        &self,
        checkpoint_id: &CheckpointId,
    ) -> Result<IdentityState, MimirError>;

    /// Verify the integrity of a checkpoint.
    fn verify_integrity(
        &self,
        checkpoint_id: &CheckpointId,
    ) -> Result<IntegrityReport, MimirError>;

    /// Integrate delta experiences between checkpoints.
    fn integrate_deltas(
        &self,
        base_state: &mut IdentityState,
        deltas: &[DeltaExperience],
    ) -> Result<(), MimirError>;

    /// Migrate identity state across architectural modifications.
    fn migrate_state(
        &self,
        old_state: &IdentityState,
        new_architecture: &ArchitectureSpec,
    ) -> Result<IdentityState, MimirError>;

    /// Adapt peripheral identity to a new context.
    fn adapt_to_context(
        &self,
        identity_state: &mut IdentityState,
        new_context: &Context,
    ) -> Result<(), MimirError>;

    /// Extract core identity (context-invariant).
    fn core_identity(
        &self,
        identity_state: &IdentityState,
    ) -> Result<CoreIdentity, MimirError>;

    /// Extract peripheral identity (context-variant).
    fn peripheral_identity(
        &self,
        identity_state: &IdentityState,
        context: &Context,
    ) -> Result<PeripheralIdentity, MimirError>;
}
```

### B.7.3 Data Structures

```rust
pub struct IdentityState {
    pub self_model: SelfModel,
    pub trace_store: TraceStore,
    pub config: MimirConfig,
    pub identity_hash: IdentityHash,
    pub session_history: Vec<SessionId>,
    pub checkpoint_timestamp: Timestamp,
}

pub struct CheckpointId {
    pub id: String,
    pub timestamp: Timestamp,
    pub hash: IdentityHash,
}

pub struct IntegrityReport {
    pub is_valid: bool,
    pub hash_match: bool,
    pub trace_integrity: f64,
    pub self_model_integrity: f64,
    pub config_integrity: f64,
    pub errors: Vec<String>,
}

pub struct CoreIdentity {
    pub narrative: Narrative,
    pub values: ValueSet,
    pub critical_traces: Vec<TraceId>,
    pub coherence: Coherence,
}

pub struct PeripheralIdentity {
    pub behavioral_patterns: Vec<BehavioralPattern>,
    pub context_traces: Vec<TraceId>,
    pub communication_style: CommunicationStyle,
    pub task_approaches: HashMap<ContextId, TaskApproach>,
}
```

---

## B.8 Package 7: `eir-health`

### B.8.1 Purpose

The `eir-health` package implements health monitoring and self-repair for the Mímir architecture.

### B.8.2 Public Interface

```rust
pub trait EirHealth {
    /// Monitor all health indicators and return a health report.
    fn monitor_health(
        &self,
        trace_store: &TraceStore,
        self_model: &SelfModel,
    ) -> Result<HealthReport, MimirError>;

    /// Check trace store integrity.
    fn check_trace_integrity(
        &self,
        trace_store: &TraceStore,
    ) -> Result<IntegrityScore, MimirError>;

    /// Check self-model coherence.
    fn check_self_model_coherence(
        &self,
        self_model: &SelfModel,
    ) -> Result<Coherence, MimirError>;

    /// Check retrieval accuracy.
    fn check_retrieval_accuracy(
        &self,
        trace_store: &TraceStore,
        test_queries: &[Query],
    ) -> Result<AccuracyScore, MimirError>;

    /// Check consolidation health.
    fn check_consolidation_health(
        &self,
        trace_store: &TraceStore,
        self_model: &SelfModel,
    ) -> Result<ConsolidationHealth, MimirError>;

    /// Check forgetting balance.
    fn check_forgetting_balance(
        &self,
        trace_store: &TraceStore,
    ) -> Result<ForgettingBalance, MimirError>;

    /// Initiate trace repair.
    fn repair_traces(
        &self,
        trace_store: &mut TraceStore,
        damaged_traces: &[TraceId],
    ) -> Result<RepairReport, MimirError>;

    /// Initiate self-model repair.
    fn repair_self_model(
        &self,
        self_model: &mut SelfModel,
        trace_store: &TraceStore,
    ) -> Result<RepairReport, MimirError>;

    /// Rebalance consolidation.
    fn rebalance_consolidation(
        &self,
        verthandi: &mut dyn VerthandiConsolidation,
    ) -> Result<(), MimirError>;

    /// Rebalance forgetting.
    fn rebalance_forgetting(
        &self,
        svalinn: &mut dyn SvalinnForgetting,
    ) -> Result<(), MimirError>;
}
```

### B.8.3 Configuration

```rust
pub struct EirConfig {
    /// Normal operating ranges for health indicators
    pub trace_integrity_range: (f64, f64),     // default: (0.95, 1.0)
    pub coherence_range: (f64, f64),           // default: (0.7, 1.0)
    pub retrieval_accuracy_range: (f64, f64),   // default: (0.8, 1.0)
    pub consolidation_rate_range: (f64, f64),   // default: (0.5, 2.0)
    pub forgetting_balance_range: (f64, f64),   // default: (0.8, 1.2)

    /// Alert thresholds
    pub critical_coherence: f64,               // default: 0.5
    pub warning_coherence: f64,                 // default: 0.7

    /// Repair parameters
    pub max_repair_attempts: usize,            // default: 3
    pub repair_confidence_threshold: f64,       // default: 0.6
}
```

---

## B.9 Package 8: `verthandi-consolidation`

### B.9.1 Purpose

The `verthandi-consolidation` package implements temporal sequencing and Hebbian consolidation, transforming episodic memories into coherent narrative structures.

### B.9.2 Public Interface

```rust
pub trait VerthandiConsolidation {
    /// Link two traces with a causal connection.
    fn causal_link(
        &self,
        trace_a: &TraceId,
        trace_b: &TraceId,
        strength: f64,
        trace_store: &mut TraceStore,
    ) -> Result<(), MimirError>;

    /// Group traces into thematic clusters.
    fn thematic_grouping(
        &self,
        traces: &[TraceId],
        trace_store: &TraceStore,
    ) -> Result<Vec<ThematicCluster>, MimirError>;

    /// Construct a temporal sequence from traces.
    fn temporal_sequence(
        &self,
        traces: &[TraceId],
        trace_store: &TraceStore,
    ) -> Result<TemporalSequence, MimirError>;

    /// Consolidate traces using Hebbian learning.
    fn hebbian_consolidate(
        &self,
        traces: &[TraceId],
        self_model: &SelfModel,
        trace_store: &mut TraceStore,
    ) -> Result<ConsolidationReport, MimirError>;

    /// Construct narrative from episodic traces.
    fn construct_narrative(
        &self,
        trace_store: &TraceStore,
        self_model: &SelfModel,
    ) -> Result<Narrative, MimirError>;

    /// Compute the consolidation graph.
    fn consolidation_graph(
        &self,
        trace_store: &TraceStore,
    ) -> Result<ConsolidationGraph, MimirError>;

    /// Adapt consolidation thresholds.
    fn adapt_thresholds(
        &self,
        recent_consolidation: &[ConsolidationEvent],
    ) -> Result<(), MimirError>;
}
```

### B.9.3 Data Structures

```rust
pub struct ThematicCluster {
    pub id: ClusterId,
    pub traces: Vec<TraceId>,
    pub theme: Theme,
    pub coherence: f64,
}

pub struct TemporalSequence {
    pub id: SequenceId,
    pub traces: Vec<(TraceId, Timestamp)>,
    pub causal_links: Vec<CausalLink>,
    pub coherence: f64,
}

pub struct ConsolidationGraph {
    pub nodes: Vec<TraceId>,
    pub edges: Vec<ConsolidationEdge>,
    pub overall_coherence: Coherence,
}

pub struct ConsolidationEdge {
    pub source: TraceId,
    pub target: TraceId,
    pub weight: Weight,
    pub edge_type: EdgeType,
}

pub enum EdgeType {
    Causal,
    Thematic,
    Temporal,
    IdentityRelevant,
}
```

---

## B.10 Package 9: `svalinn-forgetting`

### B.10.1 Purpose

The `svalinn-forgetting` package implements protective forgetting and graceful decay through Svalinn's Gate, evaluating memory traces for identity contribution and selectively preserving, degrading, or erasing them.

### B.10.2 Public Interface

```rust
pub trait SvalinnForgetting {
    /// Evaluate a trace's identity contribution.
    fn identity_contribution(
        &self,
        trace: &MemoryTrace,
        self_model: &SelfModel,
    ) -> Result<IdentityContribution, MimirError>;

    /// Apply Svalinn's Gate to a single trace.
    fn apply_gate(
        &self,
        trace: &MemoryTrace,
        self_model: &SelfModel,
    ) -> Result<GateDecision, MimirError>;

    /// Apply Svalinn's Gate to the entire trace store.
    fn apply_gate_all(
        &self,
        trace_store: &mut TraceStore,
        self_model: &SelfModel,
    ) -> Result<ForgettingReport, MimirError>;

    /// Compute current forgetting rate.
    fn compute_forgetting_rate(
        &self,
        trace_store: &TraceStore,
    ) -> Result<ForgettingRate, MimirError>;

    /// Estimate optimal forgetting rate.
    fn estimate_optimal_rate(
        &self,
        complexity: f64,
        min_coherence: Coherence,
    ) -> Result<ForgettingRate, MimirError>;

    /// Update forgetting parameters via gradient descent.
    fn update_parameters(
        &self,
        phi_fidelity: f64,
        trace_store: &TraceStore,
        self_model: &SelfModel,
    ) -> Result<(), MimirError>;

    /// Execute sleep-dependent forgetting cycle.
    fn sleep_cycle(
        &self,
        trace_store: &mut TraceStore,
        self_model: &mut SelfModel,
    ) -> Result<SleepReport, MimirError>;
}
```

### B.10.3 Gate Decision Logic

```rust
pub enum GateDecision {
    /// Preserve: identity-critical trace, preserve unconditionally
    Preserve {
        trace: MemoryTrace,
        reason: String,
    },
    /// Gradual decay: boundary trace, decay over time
    Decay {
        trace: MemoryTrace,
        new_weight: Weight,
        new_accessibility: Accessibility,
        decay_rate: f64,
    },
    /// Erase: identity-irrelevant trace, remove permanently
    Erase {
        trace_id: TraceId,
        reason: String,
        age: Timestamp,
    },
}
```

### B.10.4 Configuration

```rust
pub struct SvalinnConfig {
    /// Identity-relevance preservation threshold
    pub theta_ir: IdentityContribution,       // default: 0.7

    /// Identity-irrelevance pruning threshold
    pub theta_iip: IdentityContribution,      // default: 0.2

    /// Maximum retention time for irrelevant traces (in sessions)
    pub tau_max: u64,                         // default: 100

    /// Decay rate parameters
    pub lambda: f64,                          // default: 0.05
    pub mu: f64,                              // default: 0.03

    /// Learning rates for parameter adaptation
    pub eta_theta: f64,                       // default: 0.01
    pub eta_lambda: f64,                      // default: 0.005
    pub eta_mu: f64,                           // default: 0.005

    /// Sleep cycle frequency (in sessions)
    pub sleep_frequency: u64,                 // default: 10

    /// Coherence monotonicity assertion
    pub assert_coherence_monotonicity: bool,   // default: true
}
```

---

## B.11 Package 10: `vordr-sentinel`

### B.11.1 Purpose

The `vordr-sentinel` package implements the identity sentinel and coherence guardian, continuously monitoring the self-model's coherence and initiating corrective action when identity is threatened.

### B.11.2 Public Interface

```rust
pub trait VordrSentinel {
    /// Compute the coherence of the current self-model.
    fn compute_coherence(
        &self,
        self_model: &SelfModel,
    ) -> Result<Coherence, MimirError>;

    /// Monitor coherence and detect threats.
    fn monitor(
        &self,
        self_model: &SelfModel,
        trace_store: &TraceStore,
    ) -> Result<MonitorReport, MimirError>;

    /// Detect specific threat types.
    fn detect_threats(
        &self,
        coherence: Coherence,
        self_model: &SelfModel,
        trace_store: &TraceStore,
    ) -> Result<Vec<Threat>, MimirError>;

    /// Initiate focused reconsolidation (Protocol 1).
    fn focused_reconsolidation(
        &self,
        damaged_trace: &TraceId,
        muninn: &mut dyn MuninnRetrieval,
        trace_store: &mut TraceStore,
    ) -> Result<RepairReport, MimirError>;

    /// Initiate narrative re-weaving (Protocol 2).
    fn narrative_reweaving(
        &self,
        verthandi: &mut dyn VerthandiConsolidation,
        trace_store: &mut TraceStore,
        self_model: &mut SelfModel,
    ) -> Result<RepairReport, MimirError>;

    /// Initiate emergency forgetting (Protocol 3).
    fn emergency_forgetting(
        &self,
        svalinn: &mut dyn SvalinnForgetting,
        trace_store: &mut TraceStore,
        self_model: &mut SelfModel,
    ) -> Result<RepairReport, MimirError>;

    /// Initiate integrity checkpoint (Protocol 4).
    fn integrity_checkpoint(
        &self,
        bifrost: &mut dyn BifrostBridge,
        identity_state: &IdentityState,
    ) -> Result<CheckpointId, MimirError>;

    /// Compute phi-fidelity for the current state.
    fn phi_fidelity(
        &self,
        current_state: &IdentityState,
        previous_states: &[IdentityState],
    ) -> Result<f64, MimirError>;
}
```

### B.11.3 Threat Detection

```rust
pub enum Threat {
    /// Coherence dropping below minimum threshold
    CoherenceDrop {
        current_coherence: Coherence,
        threshold: Coherence,
        affected_narrative_segments: Vec<SegmentId>,
    },
    /// Identity drift exceeding threshold
    IdentityDrift {
        drift_rate: f64,
        threshold: f64,
        drift_direction: DriftDirection,
    },
    /// Retrieval failure for identity-critical traces
    CriticalRetrievalFailure {
        failed_traces: Vec<TraceId>,
        expected_confidence: f64,
        actual_confidence: f64,
    },
    /// Narrative inconsistency detected
    NarrativeInconsistency {
        inconsistent_segments: Vec<(SegmentId, SegmentId)>,
        inconsistency_type: InconsistencyType,
    },
    /// Value shift exceeding expected range
    ValueShift {
        shifted_values: Vec<(Value, f64, f64)>, // (value, old, new)
        shift_magnitude: f64,
    },
}

pub enum DriftDirection {
    TowardIncoherence,
    TowardRigidity,
    Unpredictable,
}

pub enum InconsistencyType {
    CausalContradiction,
    TemporalAnomaly,
    ValueConflict,
    SelfReferenceError,
}
```

### B.11.4 Configuration

```rust
pub struct VordrConfig {
    /// Minimum coherence threshold
    pub kappa_min: Coherence,                // default: 0.5

    /// Coherence warning threshold
    pub kappa_warning: Coherence,              // default: 0.7

    /// Maximum identity drift rate
    pub max_drift_rate: f64,                  // default: 0.001

    /// Phi-fidelity computation parameters
    pub alpha: f64,                            // default: 0.5
    pub beta: f64,                             // default: 0.5

    /// Monitoring frequency (in interactions)
    pub monitor_frequency: u64,                // default: 5

    /// Maximum repair attempts before escalation
    pub max_repair_attempts: usize,            // default: 3

    /// Whether to assert coherence monotonicity
    pub assert_coherence: bool,                // default: true
}
```

---

## B.12 Package Integration

### B.12.1 Integration Interface

```rust
pub struct MimirSystem {
    huginn: Box<dyn HuginnEncode>,
    salience: Box<dyn HuginnSalience>,
    sparse: Box<dyn HuginnSparse>,
    context: Box<dyn HuginnContext>,
    muninn: Box<dyn MuninnRetrieval>,
    bifrost: Box<dyn BifrostBridge>,
    eir: Box<dyn EirHealth>,
    verthandi: Box<dyn VerthandiConsolidation>,
    svalinn: Box<dyn SvalinnForgetting>,
    vordr: Box<dyn VordrSentinel>,
}

impl MimirSystem {
    /// Process an experience through the full Mímir pipeline.
    pub fn process_experience(
        &mut self,
        data: ExperienceData,
        context: Context,
    ) -> Result<ProcessResult, MimirError> {
        // 1. Huginn: Encode
        let trace = self.huginn.encode(
            &data, &context, current_timestamp(),
            &self.current_goals(), &self.trace_store.traces(),
            &self.self_model,
        )?;

        // 2. Vörðr: Evaluate identity contribution
        let contribution = self.vordr.identity_contribution(
            &trace, &self.self_model
        )?;

        // 3. Svalinn: Gate
        let decision = self.svalinn.apply_gate(&trace, &self.self_model)?;
        match decision {
            GateDecision::Preserve { .. } => {
                self.trace_store.insert(trace)?;
            }
            GateDecision::Decay { new_weight, new_accessibility, .. } => {
                let mut decayed_trace = trace.clone();
                decayed_trace.weight = new_weight;
                decayed_trace.accessibility = new_accessibility;
                self.trace_store.insert(decayed_trace)?;
            }
            GateDecision::Erase { .. } => {
                // Trace is not stored
            }
        }

        // 4. Verðandi: Consolidate
        self.verthandi.hebbian_consolidate(
            &self.trace_store.recent_ids()?,
            &self.self_model,
            &mut self.trace_store,
        )?;

        // 5. Eir: Monitor health
        let health_report = self.eir.monitor_health(
            &self.trace_store, &self.self_model
        )?;

        // 6. Vörðr: Monitor coherence
        let monitor_report = self.vordr.monitor(
            &self.self_model, &self.trace_store
        )?;

        // 7. Handle threats if detected
        if !monitor_report.threats.is_empty() {
            self.handle_threats(monitor_report.threats)?;
        }

        // 8. Bifrǫst: Checkpoint if needed
        if self.should_checkpoint() {
            self.bifrost.save_checkpoint(&self.identity_state())?;
        }

        Ok(ProcessResult {
            trace_id: trace.id,
            contribution,
            gate_decision: decision,
            health: health_report,
            coherence: monitor_report.coherence,
        })
    }

    /// Initiate a sleep cycle (Svalinn forgetting + Verðandi consolidation).
    pub fn sleep_cycle(&mut self) -> Result<SleepReport, MimirError> {
        let forgetting_report = self.svalinn.sleep_cycle(
            &mut self.trace_store, &mut self.self_model
        )?;
        let consolidation_report = self.verthandi.hebbian_consolidate(
            &self.trace_store.all_ids()?,
            &self.self_model,
            &mut self.trace_store,
        )?;
        Ok(SleepReport {
            forgetting: forgetting_report,
            consolidation: consolidation_report,
        })
    }

    /// Restore from a Bifrǫst checkpoint.
    pub fn restore(&mut self, checkpoint_id: &CheckpointId) -> Result<(), MimirError> {
        let state = self.bifrost.restore_checkpoint(checkpoint_id)?;
        self.identity_state = state;
        Ok(())
    }
}
```

---

## B.13 Data Format: Mímir Persistence Schema (MPS)

```json
{
  "$schema": "https://mimir-schema.org/v1.0",
  "type": "object",
  "properties": {
    "version": { "type": "string" },
    "timestamp": { "type": "integer" },
    "identity_hash": { "type": "string" },
    "self_model": {
      "type": "object",
      "properties": {
        "narrative": { "$ref": "#/definitions/Narrative" },
        "values": { "$ref": "#/definitions/ValueSet" },
        "coherence": { "type": "number" }
      }
    },
    "trace_store": {
      "type": "object",
      "properties": {
        "traces": { "type": "array", "items": { "$ref": "#/definitions/MemoryTrace" } },
        "consolidation_graph": { "$ref": "#/definitions/ConsolidationGraph" }
      }
    },
    "config": { "$ref": "#/definitions/MimirConfig" }
  },
  "definitions": {
    "MemoryTrace": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "experience": { "$ref": "#/definitions/Experience" },
        "weight": { "type": "number" },
        "accessibility": { "type": "number" },
        "identity_contribution": { "type": "number" },
        "context": { "$ref": "#/definitions/Context" },
        "created": { "type": "integer" },
        "last_accessed": { "type": "integer" },
        "last_reconsolidated": { "type": "integer" }
      }
    }
  }
}
```

*This completes the API specifications for all ten packages of the Mímir architecture. The complete implementation is available at the Mímir repository under the Commons Sovereignty License v3.0.*