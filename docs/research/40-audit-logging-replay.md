# 40 — Audit Logging and Replay for AI Agents

**Category:** Safety, Trust, Sandboxing
**Runa relevance:** `core/logging/audit/`, `runa logs` command, every kernel turn
**Status:** Research synthesis. The "did Runa do what she said" substrate.
**Last touched:** 2026-05-17

---

## 1. Core idea

An agent operating under standing trust (ADR-0001 §D-1.5) takes actions without per-action approval. The price of that trust is *visibility*: every meaningful decision must be recorded, and the record must be sufficient to answer "what did Runa do, when, why, and to what effect" without ambiguity. Audit logging is the substrate. **Replay** is the powerful corollary: if the audit log is structured enough, an investigator (Volmarr, Eir, future-Runa) can *reconstruct* the agent's reasoning trajectory step by step — examining the same inputs, the same intermediate state, the same model calls — without re-running the action.

This is well-established practice in finance, security, and distributed systems. For AI agents specifically, the practice is less mature: many production systems log haphazardly. The shape of *good* audit logging for agents is converging on: **structured events**, **distributed tracing**, **content-addressed model calls**, **policy-decision evidence**, **tamper-evident chains**. This document covers the patterns and how they map to Runa's design.

## 2. Technical depth

**Audit log requirements:**

1. **Append-only.** No edits, no deletions. (Compensating entries for corrections.)
2. **Tamper-evident.** Detect after-the-fact modification.
3. **Structured.** Machine-queryable, not free-text.
4. **Causally linked.** Each event references its parents (the events that caused it).
5. **Provenanced.** Every claim traces to its source.
6. **Operator-readable.** Volmarr can `runa logs --filter` and understand what he sees.
7. **Privacy-aware.** Secrets are redacted at write-time.

**Structure of a Runa audit-log entry** (proposed):

```json
{
  "event_id": "uuid",
  "timestamp": "2026-05-17T14:32:01.123Z",
  "type": "kernel.turn.thought" | "skill.invoke" | "policy.check" | ...
  "correlation_id": "uuid_of_originating_Heard",
  "causation_id": "uuid_of_parent_event",
  "actor": "kernel" | "huginn" | "smidja" | ...
  "content": { "thought": "..." | "args": {...} | ... },
  "evidence": [ {"source": "muninn.episode/abc", "snippet": "..."} ],
  "policy_decisions": [
    {"principle": "require_confirmation:delete_file", "result": "allow",
     "reason": "in operator-approved list"}
  ],
  "model_call": {
    "provider": "ollama", "model": "llama3.1:8b-instruct-q4_K_M",
    "prompt_hash": "sha256:...", "response_hash": "sha256:...",
    "input_tokens": 1234, "output_tokens": 567, "ms": 890
  } | null,
  "redactions": [ {"field": "content.args.api_key", "method": "sha256_prefix"} ]
}
```

**Tamper-evidence via hash-chained logs:**

```
event[n].hash = sha256(event[n].content || event[n-1].hash)
```

A modification to event N changes its hash; all subsequent hashes change too. Tampering is detectable. Optional: anchor the chain to an external timestamp service (RFC 3161, OpenTimestamps) for tamper-evidence against the system operator themselves.

**Replay:**

If model calls include `prompt_hash` and `response_hash`, and the prompt + response are content-addressed in a content store, full replay is possible:

```
1. Locate event of interest in audit log.
2. Reconstruct kernel state at that moment from earlier events.
3. Replay the model call: feed the stored prompt to a model (the same
   model if available; an analogous one if not) and compare to the
   stored response.
4. Continue replay forward through subsequent events.
```

Replay enables: post-hoc debugging, regression testing, "what would Runa have done with a better model?" exploration.

**Distributed tracing:**

OpenTelemetry standard. Each event carries:
- `trace_id` — groups all events for a single user-facing operation.
- `span_id` — identifies one operation within the trace.
- `parent_span_id` — the operation that initiated this one.

Visualisation tools (Jaeger, Tempo, Honeycomb, Grafana Tempo) read OpenTelemetry data and show timeline waterfalls.

For Runa, OpenTelemetry-compatible logging is overkill in v0 but worth respecting in schema design: use compatible field names.

**Storage substrate:**

Options for the audit log itself:

- **JSONL files** under `~/.runa/logs/audit/YYYY-MM-DD.jsonl`. Simple, grep-friendly, plays well with tools. Rotated daily.
- **SQLite append-only table** in `~/.runa/logs/audit.sqlite`. Queryable, structured, slower to inspect manually but easier to filter.
- **Both** — JSONL is the primary format; nightly Eir job indexes into SQLite for queries.

**Compliance / regulatory note:**

- Some jurisdictions impose specific audit requirements on AI systems. Currently most agent-scale projects ignore these; longer-term they will matter. Audit logs designed for compliance from day one are cheap insurance.

**Cost / size budget:**

- A serious agent generates ~10-1000 audit entries per turn (every thought, every tool call, every policy check). A turn-heavy day: 10K entries. At ~1KB each: 10 MB/day. Over a year: ~4 GB. Manageable on Pi 5 (NVMe).
- Compress rotated logs (zstd). Keep recent uncompressed for fast access.

**Secrets in audit logs:**

- Redact at write-time. The audit log should never contain API keys, passwords, or secrets in clear.
- Redaction approach: replace with `sha256_prefix("KEY", 8)` — gives enough identity to debug ("this is API key abc12345...") without revealing the actual key.

## 3. Key works

- **Schneier, B. and Kelsey, J. "Secure Audit Logs to Support Computer Forensics."** ACM Transactions on Information and System Security, 1999. The classical reference.
- **Crosby, S. and Wallach, D. "Efficient Data Structures for Tamper-Evident Logging."** USENIX Security, 2009. History tree data structure.
- **OpenTelemetry specification** — opentelemetry.io.
- **OpenTimestamps** — opentimestamps.org. Bitcoin-blockchain-anchored timestamping.
- **Certificate Transparency** (RFC 6962). Production-scale tamper-evident logging. Worth studying for the engineering choices.
- **Trillian** (Google) — production tamper-evident log. github.com/google/trillian.
- **Dapper paper** (Sigelman et al., Google, 2010). The foundation of distributed tracing.

## 4. Empirical results

- **Tamper-evidence via hash chains** is well-deployed at internet scale (Certificate Transparency holds billions of entries). The pattern is rock-solid.
- **Replay** of LLM agent calls: feasible when prompts and responses are content-addressed and the same model is available. Modern caching infrastructure (Anthropic prompt caching, etc.) makes deterministic replay easier than it was.
- **Storage cost:** scales linearly with activity. JSONL + zstd compression at typical agent rates is comfortably affordable.
- **Practical retrieval:** SQLite full-text search + structured filters on a 4 GB audit log answers queries in <100ms on Pi 5.

## 5. Applicability to Runa

For **`core/logging/audit/`**:

- Primary store: JSONL files under `~/.runa/logs/audit/YYYY-MM-DD.jsonl`. One file per UTC day. Rotated automatically.
- Schema: the proposed JSON structure above. Validated by Pydantic at write-time.
- Hash chain: each event's `prev_hash` field. A small `chain_anchor.json` at the start of each day captures the inherited hash from the previous day.

For **`runa logs` command**:

- Filter, follow, summarise. Backed by either JSONL grep or SQLite index depending on operation.
- Default filters: by correlation_id, by actor, by time range, by event type, by policy decision.

For **replay**:

- A `runa state replay <correlation_id>` command reconstructs the turn's trace and (optionally) re-runs the model calls against current models.
- Useful for: "why did Runa do that?" investigations; regression testing after policy changes; debugging.

For **Eir review**:

- Eir's daily maintenance includes scanning the audit log for anomalies: unusually-many policy violations, repeated failures, sudden behaviour shifts. Surfaces via `runa doctor` or proactive `Notified` to Volmarr.

For **tamper-evidence**:

- Hash chain implemented. Optional anchoring to OpenTimestamps if Volmarr wants third-party tamper-evidence (probably not needed for personal use; useful for any future external accountability).

For **secrets redaction**:

- Centralised redaction step at audit-write time. Pattern library covers API keys, passwords, JWTs, OAuth tokens, common secret formats.
- Redaction is *additive* — original (unredacted) goes to a separate operator-only encrypted log; the regular audit log has redacted versions. This is the "trust-but-evidence" pattern.

For **storage discipline**:

- `~/.runa/logs/audit/` is operator-readable, not world-readable. File permissions 0600.
- Backup `runa state snapshot` includes the audit log; restore preserves it.

What to avoid:

- Don't log full unredacted prompt + response contents. Hashes plus prompt-template-name plus snippets are usually enough for debugging.
- Don't log to a single file. Daily rotation is mandatory; otherwise the file grows without bound and disk fills.
- Don't silently fail audit writes. A failed audit-write is a significant fault; surface it. Eir should escalate.
- Don't dispose of audit logs eagerly. Operator-asked retention only. Even compressed archives should be retained for at least a year.

## 6. Open questions

- **Privacy-preserving audit.** Volmarr's privacy and Runa's accountability sometimes conflict. Encrypted-at-rest with operator-only-key audit logs are an answer; complete answers are hard.
- **Audit-log search via LLM.** "Show me times Runa hesitated to delete files" — natural-language queries over the audit log. Practically achievable; underdeveloped tooling.
- **Cross-agent audit.** When Hirð retainers act, do their logs join the kernel's chain or branch? Single-chain is simplest; branching is more accurate. Open design choice.
- **Compliance evolution.** AI agent regulation is evolving (EU AI Act, US executive orders, sectoral guidance). The right audit schema will likely need to evolve too.

## 7. References (curated)

- ACM TISSEC 1999 — Schneier and Kelsey on secure audit logs.
- USENIX Security 2009 — Crosby and Wallach.
- opentelemetry.io — OpenTelemetry.
- opentimestamps.org — OpenTimestamps.
- github.com/google/trillian — Trillian.
- RFC 6962 — Certificate Transparency.
- Sigelman et al. (Google, 2010) — Dapper paper.
- Companion docs: [[14-constitutional-ai]] (policy decisions to log), [[22-event-sourcing-cqrs]] (the event-sourcing connection), [[37-plugin-sandboxing]], [[38-prompt-injection-defenses]], [[39-output-filtering]].
