# 92 — Process Scheduling for Cognitive Systems: Attention as a CPU

**Category:** AI Operating System
**Runa relevance:** kernel scheduling of subagent runs, background-task management, resource allocation across cognitive layers
**Status:** OS-theory + AI-systems synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

In a traditional OS, the scheduler decides which process runs on the CPU at any given moment. The scheduling problem in an AI OS is structurally similar but conceptually different: the scarce resource is *attention* — the agent's reasoning capacity in any given moment — and the candidates are *cognitive tasks*: respond to the user, run consolidation, do background research, run a verification pass, write a Saga chapter. The scheduling decisions made here determine how much of Runa's life is *responsive* (foreground, reactive) vs. *deliberative* (background, reflective). Designed badly, Runa is either lagging on response or never doing the offline work; designed well, both happen at the right cadences.

For Runa, scheduling matters in concrete ways: when does Draumr ([[57-sleep-dream-replay-consolidation]]) run? when does the curiosity retainer ([[63-active-inference-self-modelling]]) explore questions? when does Smiðja evaluate calibration? How are these orchestrated so they don't fight the foreground loop or each other? The answer is a scheduler with explicit policies for priority, preemption, and budget.

## 2. Technical depth

**The basic OS scheduling concepts (Tanenbaum).**

- *Preemptive vs cooperative*: preemptive — the scheduler can interrupt a running process; cooperative — processes yield voluntarily.
- *Priority levels*: high-priority processes preempt low.
- *Round-robin*: equal time slices.
- *Real-time vs batch*: real-time has hard deadlines; batch is throughput-oriented.
- *Multi-level feedback queues*: dynamically adjust priorities.

**Adapting to cognitive tasks.**

A cognitive task in Runa is:
- A *subagent* to invoke (planner, narrator, Draumr, ...).
- A *budget* (token count, time limit, retrieval-call cap).
- A *priority* (foreground request, scheduled task, opportunistic).
- A *trigger* (user request, time-based, condition-based, manual).
- A *result handling policy* (write to disk, notify user, queue follow-up).

**Foreground vs background.**

- *Foreground*: triggered by user input. Strict latency target (e.g. <2s for chitchat, <30s for deliberation). Preempts most background.
- *Background*: scheduled or opportunistic. No hard deadlines but bounded budgets.

Foreground takes priority. Background runs in idle slices, on schedule, or on explicit request.

**Scheduler policy (proposed Runa default).**

```
on user input arrival:
    suspend background tasks (preempt, save state)
    invoke foreground kernel pipeline
    on completion:
        resume highest-priority background task
        if no background pending, idle

on schedule trigger (e.g. nightly 02:00):
    if foreground idle:
        invoke Draumr (consolidation)
    else:
        defer to next idle window

on condition trigger (e.g. accumulated importance > threshold):
    enqueue trigger evaluation as background task
    process when foreground idle
```

This is multi-level feedback queue + condition triggers, with explicit foreground priority.

**Cognitive cost models.**

What does it cost to *run* a cognitive task?

- *Token budget*: total LLM tokens (input + output). Most expensive variable.
- *Inference time*: wall-clock for LLM calls; depends on model size, context length, hardware.
- *Retrieval calls*: Muninn queries; cheap individually but accumulate.
- *Tool calls*: external services; cost varies wildly.
- *Disk writes*: Muninn appends, journal entries. Cheap.

A *cost estimator* approximates these for each candidate task; the scheduler uses estimates to plan.

**Scheduling primitives Runa needs.**

1. *Task queue*: prioritised, persistent (across restarts).
2. *Resource accounting*: per-task budget tracking; per-day caps.
3. *Triggers*: time-based, condition-based, manual.
4. *Preemption*: ability to pause and resume long-running tasks.
5. *Failure handling*: tasks that fail get logged and either retried or escalated.
6. *Inspection*: Volmarr can list, prioritise, cancel.

**Implementation note: simple is fine.**

For Phase 1 Runa, a simple cron-like scheduler + a foreground/background split is sufficient. No need for full multi-level feedback queues. Pi-class hardware can run a basic scheduler comfortably; complexity should follow demonstrated need.

**Real-time considerations.**

Runa is not hard-real-time; latency budgets are soft. But Volmarr-facing latency matters: chitchat sub-second, deliberation under 30s, large planning tasks under 5 min. The scheduler enforces these via budget caps; long-running tasks split into pieces.

**Background task taxonomy.**

- *Periodic*: every N hours / daily / weekly. Examples: Draumr nightly, Saga weekly, calibration monthly.
- *Condition-triggered*: when X happens. Examples: reflection when high-importance episodes accumulate, anomaly detection when behaviour drifts.
- *Opportunistic*: during idle. Examples: curiosity exploration, semantic-graph cleanup.
- *Volmarr-triggered*: explicit \"run this now\".

Each has different scheduling rules but the same underlying primitives.

**Multi-machine considerations.**

If Runa eventually spans multiple machines (Pi for always-on, laptop for heavier compute, cloud for surge), scheduling becomes *distributed*. Job placement decisions become explicit: \"this task needs GPU; route to laptop.\" Phase-3+ concern.

## 3. Key works

- **Tanenbaum, A. S.** *Modern Operating Systems.* Pearson, 4th edition. Reference for scheduling theory.
- **Stallings, W.** *Operating Systems: Internals and Design Principles.* Pearson. Companion reference.
- **Erlang/OTP design principles** — the supervisor-tree pattern for long-running fault-tolerant processes.
- **Apache Airflow** documentation — the DAG-based scheduler pattern.
- **Celery** documentation — distributed task queue.
- **Prefect, Dagster** — modern Python schedulers.
- **Microsoft AutoGen, LangGraph** — agent-orchestration scheduling.
- **Karpathy, A.** *Software 2.0.* 2017. The shift toward LLM-as-runtime conceptualisation.
- **Packer, C. et al.** *MemGPT.* arXiv:2310.08560, 2023. Implicitly schedules paging operations.
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. Reflection scheduling.

## 4. Empirical results

This is more an engineering pattern than benchmarked research. Production observations:

- *Airflow / Celery / Prefect* deployments show robust scheduling at enterprise scale. The patterns transfer.
- *Agent stacks* (AutoGen, LangGraph) handle multi-step scheduling with various opinions; the field is converging on DAG-based or queue-based primitives.
- *Generative Agents*: cadence of reflection materially affects coherence; missing or skipping reflections degrades long-horizon behaviour.
- *Failure-mode evidence*: race conditions in concurrent agents, missed schedules during downtime, budget overruns on poorly-instrumented tasks — all well-known.

## 5. Applicability to Runa

For **the kernel — foreground loop**:

- The kernel is the foreground task by default. When Volmarr's input arrives, the kernel runs to completion, preempting any background work.
- Token budget per turn: configurable (e.g. 8K tokens for chitchat, 32K for deliberation). Beyond budget, response is truncated or summarised.

For **Hirð — background subagents**:

- Each retainer registered with the scheduler with:
  - Trigger condition (cron-like time, threshold event, manual).
  - Resource budget per run.
  - Priority among background tasks.
  - Failure handling.

For **scheduling examples (Phase 1)**:

```yaml
schedule:
  - name: draumr_nightly
    trigger: "0 2 * * *"        # 02:00 daily
    subagent: draumr
    budget: { tokens: 50000, time: 2h, retrievals: 200 }
    priority: low
    foreground_yield: true
  
  - name: saga_weekly
    trigger: "0 4 * * SUN"      # 04:00 Sunday
    subagent: saga
    budget: { tokens: 30000, time: 1h, retrievals: 100 }
    priority: low
  
  - name: importance_threshold_reflection
    trigger: "importance_accumulated > 100"
    subagent: reflector
    budget: { tokens: 20000, time: 30m, retrievals: 50 }
    priority: medium
    coalesce: "max_one_per_4h"
  
  - name: calibration_review
    trigger: "0 6 1 * *"        # 06:00 first of month
    subagent: smidja
    budget: { tokens: 10000, time: 30m }
    priority: low
```

For **persistence**:

- Schedule definitions live in `config/schedules.yaml` (per RULES.AI.md: no hard-coded). Editable by Volmarr.
- Task queue lives in `state/scheduler.sqlite` (queued tasks, running tasks, history).
- Crash recovery: on Runa restart, pending tasks resume; running tasks have last-checkpoint resumed.

For **Eldhugi-aware scheduling**:

- If Eldhugi state indicates Runa is in a high-arousal / stressed pattern, defer non-essential background work. Wellbeing-aware scheduling.
- This is novel; cognitive-science-inspired; experimental.

For **Volmarr-controlled overrides**:

- CLI command `runa schedule [list|run|pause|defer]`. Volmarr can see and control.

What to avoid:

- **Overly fancy scheduling without proven need.** Cron-like + simple priority is enough for Phase 1.
- **Letting background tasks block foreground.** Hard rule: foreground preempts.
- **Unbounded budgets.** Every task has caps; over-budget tasks log and stop.
- **Schedule sprawl.** Don't spawn schedules for every minor concern. Consolidate; review periodically.
- **Missing-schedule failures.** Tasks should detect they were skipped during downtime and decide whether to catch up or skip the gap.

## 6. Open questions

- **Optimal scheduling policies.** The literature is rich for traditional OS; for cognitive scheduling, much is open.
- **Coalescing similar background work.** Multiple reflection triggers within a window should merge; the policy is heuristic.
- **Eldhugi-aware scheduling.** Novel; effectiveness untested.
- **Multi-machine scheduling.** Pi + laptop coordination is a future concern.
- **User-visibility of schedules.** How much detail to show Volmarr without overwhelming.

## 7. References (curated)

- Tanenbaum, *Modern Operating Systems.* Chapters on scheduling.
- Erlang/OTP supervisor-tree design — for fault-tolerant long-running scheduling.
- Apache Airflow, Prefect documentation — modern schedulers worth knowing.
- arXiv:2310.08560 — MemGPT, for OS-style paging-as-scheduling.
- arXiv:2304.03442 — Generative Agents, for reflection cadence.
- Companion docs: [[57-sleep-dream-replay-consolidation]], [[91-ai-os-architecture]], [[94-persistent-agent-state]], [[96-resource-budgets]].
