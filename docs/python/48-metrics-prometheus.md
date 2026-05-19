# 48 — Metrics: Prometheus Exposition, OpenTelemetry Metrics

**Category:** Observability & Operations
**Runa relevance:** `runa doctor`, performance dashboards, Eir alerting
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Metrics are *aggregated numeric measurements over time*: requests-per-second, p99 latency, queue depth, memory used. Distinct from logs (specific events) and traces (causal chains), metrics give dashboards and alerts. **Prometheus** is the dominant open metrics format; **OpenTelemetry metrics** is the emerging standard for emission. Most modern systems expose Prometheus-format metrics over HTTP and the operator points Prometheus / Grafana at them.

For Runa, metrics underpin `runa doctor` (snapshot) and Eir's continuous monitoring (trend). They're how "how is the agent doing" gets a quantitative answer.

## 2. Technique / mechanism

**The four metric types:**

- **Counter:** monotonically increasing. Total requests, total errors. Rate computed by Prometheus.
- **Gauge:** value that goes up and down. Memory usage, queue depth, active connections.
- **Histogram:** bucketed distribution. Request latency, payload size. Computes percentiles.
- **Summary:** like histogram but computes percentiles client-side. Less flexible.

**`prometheus-client` library:**

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Define metrics
kernel_turns = Counter(
    "runa_kernel_turns_total",
    "Total number of kernel turns",
    labelnames=["surface", "outcome"],
)

queue_depth = Gauge(
    "runa_skuld_queue_depth",
    "Number of tasks in the queue",
)

turn_duration = Histogram(
    "runa_kernel_turn_duration_seconds",
    "Kernel turn duration",
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0),
)

# Use
async def handle_turn(heard):
    with turn_duration.time():  # auto-times the block
        try:
            result = await kernel.handle(heard)
            kernel_turns.labels(surface=heard.surface, outcome="success").inc()
            return result
        except Exception:
            kernel_turns.labels(surface=heard.surface, outcome="failure").inc()
            raise

queue_depth.set(skuld.queue_size())

# Expose
start_http_server(port=9090)  # Prometheus scrapes from here
```

Prometheus scrapes `http://host:9090/metrics` periodically and stores the time series.

**OpenTelemetry metrics (alternative / complementary):**

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

kernel_turns = meter.create_counter("runa.kernel.turns")

async def handle_turn(heard):
    ...
    kernel_turns.add(1, attributes={"surface": heard.surface, "outcome": "success"})
```

OTel metrics use the same SDK as traces. Export to OTLP backends.

Prometheus client and OTel coexist; for many systems, both are fine. OTel is "the future" but Prometheus client is mature, fast, well-understood.

**Naming conventions:**

- Snake case: `runa_kernel_turns_total`.
- Suffix `_total` for counters.
- Suffix `_seconds` for time durations (always seconds, not ms — Prometheus convention).
- Suffix `_bytes` for sizes.
- Prefix with project name (`runa_`).

**Labels (be careful with cardinality):**

```python
# OK — bounded set of values
Counter("requests", labelnames=["method"])  # GET, POST, ...

# DANGER — unbounded
Counter("requests", labelnames=["user_id"])  # high cardinality
```

High-cardinality labels blow up Prometheus storage. Don't put unique identifiers in labels.

**Histograms and percentile queries:**

```python
turn_duration = Histogram(
    "runa_kernel_turn_duration_seconds",
    "Kernel turn duration",
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0),
)
```

Prometheus query: `histogram_quantile(0.95, rate(runa_kernel_turn_duration_seconds_bucket[5m]))` — p95 latency over the last 5 minutes.

Choose buckets wisely — too many = expensive; too few = imprecise percentiles. 5-10 buckets covering the expected range.

**Decorators:**

```python
@turn_duration.time()
async def handle_turn(heard):
    ...
```

Auto-times the function.

**`@functools.wraps` + custom metrics:**

```python
import functools

def measure(metric):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            with metric.time():
                return await fn(*args, **kwargs)
        return wrapper
    return decorator

@measure(turn_duration)
async def handle_turn(heard): ...
```

## 3. Key works / libraries

- **prometheus-client** — github.com/prometheus/client_python.
- **Prometheus** — prometheus.io.
- **Grafana** — grafana.com.
- **OpenTelemetry Metrics** — opentelemetry.io.
- **Beyer et al.** *Site Reliability Engineering*, O'Reilly 2016. Foundation chapters on metrics.
- **`prometheus_async`** — prometheus async-friendly metrics.

## 4. Pitfalls and gotchas

- **High-cardinality labels.** User IDs, timestamps, error messages → explosive storage cost.
- **Counter wraparound.** Counters can reset on process restart; Prometheus handles this via `rate()`.
- **Wrong metric type.** A monotonic count as gauge → wrong rate queries.
- **No `_total` suffix on counters.** Prometheus conventions matter for tooling.
- **Exposing `/metrics` publicly.** Should be internal / firewalled.
- **Histograms with too few buckets.** Percentile estimates are wrong.
- **Mutating labels mid-call.** Per-call mutation defeats time-series caching.
- **Multi-process Python.** Each worker has its own metrics; aggregation needed. Use multiprocess mode in `prometheus_client`.

## 5. Applicability to Runa

For **`runa.core.metrics`**:

- Define metrics once at startup. Module-level objects (or a `Metrics` class).
- Use throughout code via `kernel_turns.labels(...).inc()`.

For **`/metrics` endpoint**:

- Bifröst gateway exposes `/metrics` (auth-protected). Operator-internal only.
- `runa doctor` reads from same metrics for the CLI summary.

For **key metrics**:

- `runa_kernel_turns_total{surface,outcome}` — counter.
- `runa_kernel_turn_duration_seconds` — histogram.
- `runa_heimskringla_calls_total{provider,model,outcome}` — counter.
- `runa_heimskringla_tokens_total{provider,direction}` — counter (input/output tokens).
- `runa_heimskringla_breaker_state{provider}` — gauge (0=closed, 1=open, 2=half-open).
- `runa_muninn_episodes_total` — gauge.
- `runa_skuld_queue_depth` — gauge.
- `runa_adapter_connected{adapter}` — gauge.
- `runa_eldhugi_mood` — gauge.
- `runa_process_memory_rss_bytes` — gauge (sampled from psutil).

For **labels**:

- Surface, provider, adapter — bounded sets. OK.
- conversation_id, user_id — high cardinality. **Not** in metrics; only in traces.

For **dashboards**:

- Grafana dashboard with the key metrics, percentile latencies, breaker states.
- Operator-installable via `deploy/grafana/`.

What to avoid:

- Don't put high-cardinality data in labels.
- Don't expose /metrics to the internet.
- Don't conflate metrics with logs. Different use cases.
- Don't track every detail as a metric. Focus on actionable indicators.

## 6. Open questions

- **OTel metrics adoption.** Replacing prometheus-client gradually. Both work; both fine for Runa.
- **Sampling.** Most metrics are full-rate; some (very high cardinality) need sampling.
- **Cross-process aggregation.** `prometheus_client` multiprocess mode for ProcessPoolExecutor workers.

## 7. References (curated)

- prometheus.io.
- github.com/prometheus/client_python.
- opentelemetry.io/docs/specs/semconv/system/.
- *Site Reliability Engineering*, Beyer et al., 2016.
- grafana.com/docs.
- Companion docs: [[46-structured-logging]], [[47-distributed-tracing-opentelemetry]], [[14-health-checks]], [[49-observability-llm-systems]] (research corpus).
