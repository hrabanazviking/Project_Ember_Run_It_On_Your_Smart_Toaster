# 47 — Distributed Tracing with OpenTelemetry (Python-side)

**Category:** Observability & Operations
**Runa relevance:** observability stack, `runa doctor`, performance investigation
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A trace is the timeline of a single operation — a kernel turn, a tool call, a model request — broken into *spans* representing each step. **OpenTelemetry** (OTel) is the open standard for emitting traces, metrics, and logs that can be collected and visualised by many tools (Jaeger, Tempo, Honeycomb, Datadog). Python's OTel SDK is mature. Instrumenting once means choosing any backend later.

For Runa, tracing connects the operator-facing "what did Runa do for that question?" investigation to the developer-facing "where did the latency go?" debugging. Same data; same instrumentation; multiple consumers.

## 2. Technique / mechanism

**Install:**

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

**Setup:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "runa-kernel"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
```

**Creating spans:**

```python
async def handle_turn(heard: Heard):
    with tracer.start_as_current_span("kernel.turn") as span:
        span.set_attribute("conversation_id", str(heard.conversation_id))
        
        with tracer.start_as_current_span("muninn.retrieve"):
            context = await muninn.retrieve(heard.text)
        
        with tracer.start_as_current_span("heimskringla.call"):
            span.set_attribute("provider", "anthropic")
            response = await heimskringla.complete(...)
        
        return Replied(text=response.text)
```

Each `with` block creates a span. Parent-child relationships are automatic.

**Span attributes:**

```python
span.set_attribute("user_id", 42)
span.set_attribute("provider.model", "claude-3.5-sonnet")
span.set_attribute("tokens.input", 4321)
span.set_attribute("tokens.output", 156)
```

Searchable / filterable in the trace viewer.

**Events on spans (point-in-time):**

```python
span.add_event("cache_miss", attributes={"key": cache_key})
span.add_event("retry_triggered", attributes={"attempt": 2})
```

**Recording exceptions:**

```python
try:
    ...
except Exception as exc:
    span.record_exception(exc)
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
    raise
```

The exception shows in the trace with traceback.

**Automatic instrumentation:**

```python
# Install instrumentation packages
# pip install opentelemetry-instrumentation-httpx opentelemetry-instrumentation-sqlite3

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

HTTPXClientInstrumentor().instrument()  # all httpx calls now traced
SQLite3Instrumentor().instrument()      # all sqlite3 calls now traced
```

Pre-built instrumentation for many libraries. Spans show up automatically wherever instrumented code is called.

**Exporters (where traces go):**

- **ConsoleSpanExporter** — prints to stdout. Dev only.
- **OTLPSpanExporter** — sends to any OTLP-compatible backend (Jaeger, Tempo, Honeycomb, Datadog).
- **JaegerExporter** — Jaeger-specific (deprecated in favour of OTLP).

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
provider.add_span_processor(BatchSpanProcessor(exporter))
```

**Context propagation across async:**

OTel's Python SDK uses `ContextVar` internally; works across async / TaskGroup natively.

**Context propagation across processes:**

```python
from opentelemetry.propagate import inject, extract

# Sender:
carrier = {}
inject(carrier)  # write trace context to carrier
# send carrier as part of message...

# Receiver:
ctx = extract(carrier)  # read trace context
with tracer.start_as_current_span("received", context=ctx):
    ...
```

The trace ID continues across process boundaries. Lets you trace requests through subprocess workers.

**Sampling:**

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

provider = TracerProvider(
    resource=resource,
    sampler=TraceIdRatioBased(0.1),  # sample 10% of traces
)
```

For high-traffic systems, full tracing is expensive. Sampling reduces cost; trace coverage remains representative.

## 3. Key works / libraries

- **OpenTelemetry** — opentelemetry.io.
- **OpenTelemetry Python SDK** — github.com/open-telemetry/opentelemetry-python.
- **Dapper paper** (Sigelman et al., Google, 2010) — distributed tracing's foundation.
- **Zipkin, Jaeger, Tempo** — popular open backends.
- **Langfuse, Phoenix, Honeycomb** — LLM-aware backends.
- **OTel semantic conventions for GenAI** — opentelemetry.io/docs/specs/semconv/gen-ai/.

## 4. Pitfalls and gotchas

- **Span explosion.** A loop creating spans per iteration → millions of spans. Sample or aggregate.
- **Missing parent context.** Span without `start_as_current_span` doesn't become a child. Use the context manager.
- **Cross-process propagation requires explicit work.** Carriers, extract/inject.
- **Span attributes' cardinality.** High-cardinality attributes (user IDs, timestamps) blow up backend cost.
- **Synchronous export blocks** — use `BatchSpanProcessor`, not `SimpleSpanProcessor`.
- **Backend rate limits.** Sending too many spans → drops.
- **Forgetting `set_status` on errors.** Span shows as success even though it failed.

## 5. Applicability to Runa

For **kernel turns**:

- `kernel.turn` span wraps each turn.
- Child spans for retrieval, model calls, tool calls, memory writes.
- Span attributes for correlation_id, conversation_id, provider, model, latency.

For **adapters**:

- Each adapter call gets a span.
- Cross-adapter calls propagate context.

For **`runa doctor`**:

- Aggregates trace metrics. Shows recent slow turns. Surfaces patterns.

For **deployment**:

- Local dev: ConsoleSpanExporter.
- Self-hosted: Langfuse or Phoenix as backend ([[49-observability-llm-systems]] in research corpus).
- Production: optional OTLP to remote backend.

For **subprocess workers (Smiðja)**:

- Propagate trace context via task descriptor.
- Worker spans become children of the kernel-turn span.

What to avoid:

- Don't trace inside hot loops without sampling.
- Don't put high-cardinality data in span attributes.
- Don't forget to set status on errors.
- Don't enable tracing in production without considering backend cost.

## 6. Open questions

- **OTel adoption.** Standard is solid; ecosystem maturing. Most monitoring stacks support OTLP.
- **LLM-specific semantic conventions.** Just stabilising as of late 2025.
- **Self-hosted observability stack.** Langfuse + Tempo + Grafana = full open-source stack.

## 7. References (curated)

- opentelemetry.io.
- github.com/open-telemetry/opentelemetry-python.
- opentelemetry.io/docs/specs/semconv/gen-ai/.
- Sigelman et al., Dapper paper, Google 2010.
- Companion docs: [[46-structured-logging]], [[48-metrics-prometheus]], [[49-observability-llm-systems]] (research corpus).
