# 70 — The Borg Protocol (Distributed Capability Aggregation)

How Yggdrasil aggregates capabilities from many siblings
+ devices into a coherent whole that's *more than the
sum of parts*. Named for the metaphor only — we don't
assimilate anything; we *compose*.

---

## The principle

A naive integration would treat each sibling as an
independent black box. The agent calls Bifrǫst when it
wants memory; calls Seiðr when it wants verse; calls
CloakBrowser when it wants web. The agent juggles eleven
APIs.

**The Borg Protocol** flips this: capabilities are
**advertised, indexed, and orchestrated**. The agent
queries: "I need to do X — which combination of realms
can do that?" The protocol *composes* the answer.

The result: capabilities the operator didn't ask for —
because they didn't know they existed — surface
automatically when needed.

---

## How capabilities get advertised

Each realm at boot publishes its capabilities:

```python
{
    "realm": "cloak",
    "capabilities": [
        {
            "name": "fetch_url",
            "description": "Fetch a URL with stealth headers",
            "inputs": [{"name": "url", "type": "URL"}],
            "outputs": [{"name": "html", "type": "HTML"}],
            "cost_class": "network",
            "latency_class": "seconds",
        },
        {
            "name": "fetch_url_with_screenshot",
            "description": "Fetch + screenshot",
            "inputs": [{"name": "url", "type": "URL"}],
            "outputs": [{"name": "html", "type": "HTML"},
                        {"name": "image", "type": "PNG"}],
            "cost_class": "network+gpu",
            "latency_class": "seconds",
        },
    ],
}
```

Capabilities are *typed by input and output*. The Capability
Catalog indexes them.

---

## How queries find composite paths

When the agent receives a request, it can query the
catalog:

```python
catalog.find_paths(
    goal="answer 'what's on this webpage?'",
    available_inputs=["URL"],
    desired_outputs=["text_summary"],
)
# Returns:
# Path 1: fetch_url → summarize_with_funi (latency: seconds)
# Path 2: fetch_url_with_screenshot → describe_image_with_vlm (if avail)
# Path 3: federation.remote_fetch → ... (if federation enabled)
```

The catalog returns *ranked paths*. The agent picks one
(or asks the operator).

---

## The composition shapes

Three common composition patterns:

### Sequential

A → B → C. Output of A feeds B; output of B feeds C.
Example: `fetch_url` → `extract_main_text` → `summarize`.

### Parallel

A + B → fuse. Run A and B simultaneously; fuse their
outputs. Example: `mimir_search` + `huginn_search` →
`rrf_fuse` (the existing Bifrǫst pattern).

### Conditional

If P then A else B. Example: "If the URL is github.com,
use `fetch_url` (cheap); else use `fetch_url_cloaked`
(stealth)."

The catalog supports all three composition shapes.

---

## Why "Borg Protocol"

The naming is *partly* tongue-in-cheek. The Borg from Star
Trek assimilate — they take what's useful from others and
incorporate it. The metaphor evokes *combining many
capabilities into one effective entity*.

But we don't *assimilate* — sibling projects remain
sovereign. The Borg Protocol is the *coordination*
mechanism, not the *acquisition* of others' code.

A better Norse-coded name might be:
- **Ginnungagap Bridge** (the void where worlds combine).
- **Sammen-vald** ("together-chosen"; coined).

For now: "Borg Protocol" because operators get the
intuition immediately.

---

## What this enables

Operators experience emergent capabilities:

### Compose-don't-call

Operator asks "what changed on this webpage today?" Agent:
- Realizes: needs to fetch URL + diff against cached version.
- Catalog finds: `fetch_url` + `mimir_lookup_cache` +
  `diff_text` + `summarize_diff`.
- Composes the pipeline.
- Runs it.
- Returns: "Three new paragraphs were added under section
  X..."

The operator didn't need to know any of those four
capabilities individually. The catalog discovered the
path.

### Capability surfacing

When a new realm is enabled, its capabilities show up in
the catalog. Existing chat flows automatically gain access
to them. Operator: "Oh, I can now do X" — without manual
reconfiguration.

### Cross-device capability mixing

Federation (per
[`../cross-platform/65_DISTRIBUTED_COORDINATION.md`](../cross-platform/65_DISTRIBUTED_COORDINATION.md))
advertises remote capabilities too. The operator's laptop
gains access to the workstation's "describe_image" capability
without code changes.

---

## How the catalog works internally

Backing store: a small SQLite (or in-memory) table:

```sql
CREATE TABLE capabilities (
    realm TEXT,
    name TEXT,
    description TEXT,
    input_types JSON,
    output_types JSON,
    cost_class TEXT,
    latency_class TEXT,
    cost_estimate_ms INTEGER,
    available BOOLEAN,
    PRIMARY KEY (realm, name)
);
```

Indexed by input/output types for fast lookup.

Updated when:
- A realm starts: capabilities added.
- A realm stops: marked unavailable.
- A federated peer joins: peer's capabilities added.

---

## Path scoring

When multiple paths satisfy a goal, the catalog ranks
them:

```python
def score_path(path: list[Capability]) -> float:
    """Lower is better."""
    return (
        sum(c.cost_estimate_ms for c in path) +
        sum(_cost_class_weight(c.cost_class) for c in path) +
        len(path) * 100   # prefer shorter paths
    )
```

Weights:
- Network calls: + 1000 ms latency penalty.
- GPU calls: + 500 ms.
- Disk I/O: + 100 ms.
- In-memory: 0.

Operator can override weights:

```yaml
yggdrasil:
  borg_protocol:
    path_weights:
      prefer_offline: true       # bias against network
      prefer_local: true         # bias against federation
      prefer_fast: true          # bias for low latency
```

---

## Operator-facing surface

Operator can browse capabilities:

```bash
$ ember capabilities list

Realm: mimir
  • search(query) → chunks (latency: ~50ms; cost: cheap)
  • store(chunk) → chunk_id (latency: ~20ms)

Realm: huginn
  • semantic_search(query) → chunks (latency: ~80ms; cost: cheap)
  • index(text) → embedding_id (latency: ~50ms)

Realm: cloak
  • fetch_url(url) → html (latency: ~3s; cost: network)
  • fetch_with_screenshot(url) → (html, png) (latency: ~4s)

Realm: bifrost
  • hybrid_search(query) → chunks (composes mimir+huginn+muninn)

...

Composition paths:
  Goal "web summary": fetch_url → extract → summarize
                       (path 1: 4 capabilities, ~5 seconds)
  ...
```

Operator can pin paths, disable capabilities, or rename
for ergonomics.

---

## What this protocol is NOT

- **Not an autonomous-agent framework.** The protocol
  *composes capability paths*; the agent (or operator)
  *decides* to invoke them.
- **Not a service mesh.** No service discovery beyond
  Yggdrasil + federation.
- **Not a workflow engine.** Paths are *transient*
  compositions, not durable workflows.
- **Not "AI deciding what to do."** The agent always uses
  paths grounded in operator-visible capabilities.

---

## Risk / known issues

- **Catalog complexity.** As capability count grows,
  ranking becomes important. We start simple; iterate.
- **Stale entries.** When a realm misadvertises, paths
  can be invalid. Mitigation: catalog re-syncs on every
  realm health beat.
- **Path explosion.** With N capabilities, combinatorial
  paths can be many. Mitigation: limit max depth (default
  4 hops); prefer ranked-by-score.

---

## Configuration shape

```yaml
yggdrasil:
  borg_protocol:
    enabled: true
    catalog:
      persist: true              # SQLite-backed
      auto_resync_on_health_beat: true
    path_finding:
      max_hops: 4
      max_alternative_paths: 5
    path_weights:
      prefer_offline: true
      prefer_local: true
      prefer_fast: true
      avoid_capability_classes: []  # operator can blacklist
    surface:
      include_in_chat_context: false  # don't add catalog to prompt
      show_in_doctor: true
```

---

## Closing

The Borg Protocol is **the capability fabric**. Each
realm advertises what it can do. The catalog indexes.
Paths compose. The agent finds answers it didn't have
to be told about.

Capabilities are *composable*; *not blocked behind
hand-written code paths*. New realms add capabilities;
existing flows immediately benefit.

This is what makes Yggdrasil *grow in power* as siblings
join — not by hand-wiring each new combination, but by
*discovery*.
