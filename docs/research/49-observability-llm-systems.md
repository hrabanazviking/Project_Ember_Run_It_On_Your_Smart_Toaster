# 49 — Observability for LLM Systems: Traces, Evals, Token Accounting

**Category:** SWE for AI Systems
**Runa relevance:** `core/logging/`, Heimskringla cost tracking, Eir health checks, `runa doctor`
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Traditional software observability — logs, metrics, traces — applies to LLM systems but also misses important things. The shape of an LLM request is different: a single user input fans out through retrieval, model calls, tool calls, sub-agent invocations, memory writes. A single "turn" can cost real money (cloud tokens), real time (seconds-to-minutes), and produce real downstream consequences (state mutations, external messages). Standard tracing handles the structural part; LLM-specific observability adds: **token accounting** (what was spent), **prompt provenance** (what was in context), **eval scoring** (was it any good), **drift detection** (did behaviour change over time).

A cluster of tools has emerged in 2023-2026 specifically for LLM observability: **LangSmith, Langfuse, Helicone, Phoenix (Arize), Honeycomb's LLM-traces support, Logfire**. They share a common shape: capture every model call with its prompt, response, cost, latency, and feedback hooks; visualise traces; run evals; alert on regression.

For Runa, observability is the dual of audit logging ([[40-audit-logging-replay]]): audit asks "what did Runa do, can I prove it?", observability asks "how well is Runa doing, where are the problems?". Different audiences, overlapping data, distinct tools.

## 2. Technical depth

**The four pillars of LLM observability:**

### 1. Distributed tracing

Each user interaction becomes a *trace* — a tree of *spans* representing operations:

```
Trace: "Volmarr asks about Muninn backups"
├─ Span: kernel.turn
│  ├─ Span: muninn.retrieve (15ms, 3 results)
│  ├─ Span: heimskringla.call.ollama (820ms, 4321 tokens in, 156 out)
│  │  └─ Span: model.inference.llama-3.1-8b
│  ├─ Span: smidja.run_tool.search_audit_log (24ms)
│  ├─ Span: heimskringla.call.ollama (610ms, 3987 tokens in, 89 out)
│  └─ Span: reply.send (5ms)
```

OpenTelemetry standard. Span attributes include LLM-specific fields: model, provider, prompt_tokens, completion_tokens, cost_usd, prompt_template_id, conversation_id.

### 2. Token / cost accounting

Every model call is logged with:
- Provider (anthropic / openai / ollama / etc.)
- Model identifier
- Input token count
- Output token count
- Cost (provider-published prices applied)
- Latency

Aggregated views: cost per turn, cost per day, cost per user, cost per retainer. Operator-visible budgets and alerts.

### 3. Prompt / output capture

Every model call captures (privacy-respecting):
- Prompt template used
- Prompt-template input variables (often hashed if sensitive)
- Full prompt (or hash thereof)
- Output (or hash + snippet)
- For replay ([[40-audit-logging-replay]]): content-addressed prompt and response storage.

### 4. Eval scoring + drift detection

Periodic eval runs over the deployed system; results plotted over time. Regressions visible. Patterns: nightly small eval suites, weekly comprehensive runs, on-demand bisection.

**Production tools (as of late 2025):**

- **LangSmith** (LangChain). Tightly coupled to LangChain pipelines. Strong UI. Closed-source platform.
- **Langfuse**. Open-source platform; self-hostable. OpenTelemetry-compatible. Strong for self-hosted deployments.
- **Helicone**. Proxy-based — sits between your app and the LLM API. Easy integration; minimal code changes. Closed-source platform with open-source proxy.
- **Phoenix (Arize)**. Open-source LLM observability. Good for evals.
- **OpenLLMetry** — open-source OpenTelemetry extension for LLMs.
- **Logfire** (Pydantic). Newer; focuses on Python ecosystem.
- **Honeycomb / Datadog / NewRelic** — general APM tools with growing LLM-specific support.

**Self-hosted vs SaaS:**

- SaaS (LangSmith, Helicone): easier, faster setup, hosted dashboards, vendor lock-in, data leaves the host.
- Self-hosted (Langfuse, Phoenix): more setup, full data sovereignty, integrate with your own dashboards.

For Runa, the local-first / sovereign design strongly favours self-hosted.

## 3. Key works

- **Sigelman et al.** "Dapper, a Large-Scale Distributed Systems Tracing Infrastructure." Google, 2010. The original distributed-tracing paper.
- **OpenTelemetry specification.** opentelemetry.io.
- **Honeycomb's "Observability Engineering"** (Majors, Fong-Jones, Miranda, O'Reilly 2022). The modern observability text.
- **Langfuse documentation** — langfuse.com/docs.
- **OpenLLMetry** — github.com/traceloop/openllmetry.
- **Arize Phoenix** — phoenix.arize.com.
- **Pydantic Logfire** — pydantic.dev/logfire.
- **Helicone docs** — helicone.ai/docs.
- **OpenTelemetry semantic conventions for GenAI** — opentelemetry.io/docs/specs/semconv/gen-ai/. The emerging standard for LLM-trace field names.

## 4. Empirical results

- Production LLM systems with proper observability catch regressions ~5-10× faster than systems without. The diagnostic time is the dominant cost; observability collapses it.
- Token-cost surprises (rate-limit, runaway loop, cache miss) are the most common operational pain point — direct cost visibility is the most-cited observability win.
- LLM-judge-driven eval scores correlate moderately with human satisfaction (~0.6-0.8 depending on rubric). Good for detecting regression; less good for absolute quality measurement.
- Self-hosted observability adoption is rising as cost and sovereignty concerns grow. SaaS still dominates by raw numbers.
- Common patterns observed in production: forgotten cache invalidations causing 100× cost spikes; silent provider downgrades (cloud LLM returning lower-quality outputs without errors); prompt-template changes triggering subtle regressions invisible in unit tests.

## 5. Applicability to Runa

For **`core/logging/` shape**:

- Structured logging via Python `logging` + JSON formatter is the floor.
- OpenTelemetry instrumentation on every model call, tool call, memory operation. Compatible with self-hosted Langfuse or Phoenix.
- Per-trace fields: trace_id (turn correlation), span_id, parent_span_id, conversation_id, retainer (if applicable), provider, model, cost, latency.

For **Heimskringla**:

- Every model call logs token counts and cost. Costs aggregated per-day, per-provider, per-purpose (kernel / Hirð / background) for operator visibility.
- Budget tracker: configured daily/monthly caps; warnings at percentages; hard cut-off at 100%.

For **`runa doctor`**:

- Reports: last 24h cost, last 24h error rate per provider, current adapter health, Muninn integrity, Skuld stuck-task count, eval suite drift.

For **eval drift detection**:

- Eir runs a small representative eval suite nightly. Stores results. Trend visible via `runa doctor --evals`.

For **observability stack on Pi 5**:

- A Pi 5 running Runa + Langfuse self-hosted is borderline. Better: Pi 5 emits OpenTelemetry data; a small companion service on a laptop / NAS runs Langfuse / Phoenix.
- Alternatively: JSONL-based local logs with a custom periodic-report script. Simpler; less rich.

For **the audit-vs-observability split**:

- Audit log: legal-grade record, append-only, tamper-evident ([[40-audit-logging-replay]]). For accountability.
- Observability: operational record, mutable indices, search-optimised. For debugging and quality.
- They share *underlying events* but have different storage / retention / access patterns.

For **privacy in observability**:

- Local-first deployment makes this easier — observability data doesn't leave the Pi without consent.
- Even local: redaction for known secret patterns at write-time.
- Conversation content can be hash-only in observability data; full text only in audit log (with stricter access controls).

What to avoid:

- Don't log full prompts and responses to *both* audit and observability. Choose one source of truth; the other references it by hash.
- Don't ignore cost tracking. Cloud LLM cost surprises destroy projects. First-class cost visibility from day one.
- Don't trust eval-score trends without checking the eval suite itself didn't drift. Suite versioning matters.
- Don't add observability that requires per-call internet access. Local-first systems with cloud-only observability defeat the local-first design.

## 6. Open questions

- **Per-token vs per-turn cost models.** Token-level granularity is the standard but interpretation requires aggregation. Turn-level views are often what operators want.
- **The right eval suite for a personal agent.** Generic LLM benchmarks don't measure Runa-as-Runa. A bespoke suite needs investment.
- **Observability vs privacy.** Observability data is valuable; observability data is also dangerous if leaked. Local-first design helps; doesn't fully solve.
- **Behavioural regression bisection.** When an eval score drops, identifying the change responsible is non-trivial. Git-bisect-on-eval-score patterns are emerging.

## 7. References (curated)

- opentelemetry.io — OpenTelemetry standard.
- opentelemetry.io/docs/specs/semconv/gen-ai/ — GenAI semantic conventions.
- langfuse.com — Langfuse (self-hostable).
- phoenix.arize.com — Phoenix.
- helicone.ai — Helicone.
- traceloop.com — Traceloop / OpenLLMetry.
- Sigelman et al. (2010) — Dapper paper.
- Majors, Fong-Jones, Miranda (2022) — *Observability Engineering*.
- Companion docs: [[40-audit-logging-replay]] (the legal-grade side), [[48-testing-ai-agents]] (the offline complement).
