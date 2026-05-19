# 05 — Idempotency Design and Safe Retries

**Category:** Robustness Fundamentals
**Runa relevance:** Heimskringla (retrying provider calls), Smiðja (tool reinvocation), Skuld (resumable tasks), Eir (recovery)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

An operation is **idempotent** if performing it once and performing it many times have the same effect. `GET /users/42` is idempotent — calling it ten times reads the same user record. `DELETE /users/42` is also idempotent — calling it ten times leaves the user gone. `POST /users` is *not* idempotent — calling it ten times creates ten users.

In distributed and concurrent systems, the difference between idempotent and non-idempotent operations is the difference between *safe to retry* and *dangerous to retry*. Network requests fail; processes crash; messages get delivered twice; jobs get picked up by two workers simultaneously. If your code is idempotent, all of these are recoverable — just retry. If it isn't, you need bespoke deduplication, transactional locking, or some other heavier machinery.

For Runa, idempotency is the substrate under which everything else (retry policies, crash recovery, supervisor restarts) works safely. An agent that crashes mid-conversation and is restarted must not double-record the conversation, double-send the message, double-charge the cloud bill, or double-fire any tool. Idempotency is what makes that safe.

## 2. Technique / mechanism

**The two flavours:**

**Naturally idempotent operations:**
- Reads (`GET`, `SELECT`, file reads).
- Setting absolute state (`UPDATE x SET name='Runa'`, `f.write_text(...)`).
- Idempotent-by-design tools (`mkdir -p`, `rsync`, `apt install` if already installed).

**Operations that need to be *made* idempotent:**
- Inserts.
- Sends (emails, messages, API calls with side effects).
- Counters and increments.
- Tool calls with external consequence.

**Three techniques for making non-idempotent operations idempotent:**

### Technique 1 — Idempotency keys

Assign every operation a unique key; the server / store records which keys it has seen and refuses to re-execute:

```python
import uuid
from typing import Protocol

class IdempotencyKey(str): pass

class WithIdempotency(Protocol):
    def send(self, message: str, *, idempotency_key: IdempotencyKey) -> Result: ...

# Caller:
key = IdempotencyKey(uuid.uuid4().hex)
result = service.send("Hello", idempotency_key=key)
# If we retry with the same key, we get the same result, not a re-send.
```

The server stores `(key, result)`. Replaying with same key returns the stored result. Stripe, PayPal, AWS APIs all do this.

### Technique 2 — Natural-key dedup

Use a domain-natural unique identifier instead of generating one:

```python
def upsert_episode(episode: Episode) -> None:
    """Idempotent by episode.episode_id."""
    db.execute(
        "INSERT OR IGNORE INTO episodes (episode_id, text, ts) VALUES (?, ?, ?)",
        episode.episode_id, episode.text, episode.timestamp,
    )
```

The UUID is the natural key. INSERT OR IGNORE (SQLite) or ON CONFLICT DO NOTHING (PostgreSQL) makes the insert idempotent.

### Technique 3 — Compare-and-set / optimistic concurrency

```python
def update_task_state(task_id: UUID, expected_state: TaskState, new_state: TaskState) -> bool:
    """Idempotent transition: succeeds once, no-op on re-run."""
    cursor = db.execute(
        "UPDATE tasks SET state = ? WHERE task_id = ? AND state = ?",
        new_state, task_id, expected_state,
    )
    return cursor.rowcount > 0
```

Retrying after a partial success yields rowcount=0; the caller knows the transition already happened.

**Idempotency for outgoing API calls:**

```python
async def call_provider_idempotent(
    provider: ModelProvider,
    request: ModelRequest,
    *,
    idempotency_key: str | None = None,
) -> ModelResponse:
    if idempotency_key is None:
        idempotency_key = hashlib.sha256(
            f"{request.prompt}|{request.model}|{request.temperature}".encode()
        ).hexdigest()
    
    # Check local cache first
    if cached := await cache.get(idempotency_key):
        return cached
    
    response = await provider.complete(request, idempotency_key=idempotency_key)
    await cache.put(idempotency_key, response, ttl=300)
    return response
```

The cache + provider-side idempotency_key together make the call safely retryable.

**Idempotency for file operations:**

```python
def atomic_write(path: Path, content: str) -> None:
    """Idempotent: writes content; if exact content already exists, no-op."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    # os.replace is atomic on POSIX; equivalent on Windows for most cases
    os.replace(tmp, path)
```

Or with content-hash check:

```python
def write_if_changed(path: Path, content: str) -> bool:
    """Returns True if written, False if content was already current."""
    if path.exists() and path.read_text() == content:
        return False
    atomic_write(path, content)
    return True
```

**Idempotency for incrementing counters:**

Not idempotent by default! `counter += 1` is *the* canonical example of a non-idempotent operation. Approaches:

- **Use absolute state instead:** record events; the count is `len(events)`.
- **Idempotency key per increment:** `(key, +1)`; the server dedup'es by key. Counter is `count(distinct keys)`.
- **Compare-and-set:** read current; write new = current + 1, conditional on no change. Spinwait on conflict.

## 3. Key works / libraries

- **REST architectural style** (Fielding, 2000) — defines idempotency at HTTP-method level.
- **Pat Helland.** "Memories, Guesses, and Apologies." ACM Queue, 2007. Foundational thinking on idempotency in distributed systems.
- **AWS SDK idempotency mechanisms** — `aws-sdk-python`'s built-in `idempotency_token` parameters.
- **Stripe API docs on idempotency** — stripe.com/docs/api/idempotent_requests. Probably the most-cited industry example.
- **`aiosafe` / similar small libraries** that wrap retry+dedup.
- **`tenacity`** (github.com/jd/tenacity) — retry library with hooks for tracking attempts.
- **SQLAlchemy `ON CONFLICT` patterns.**

## 4. Pitfalls and gotchas

- **Idempotency keys must be propagated through retries.** A retry that generates a new key fails the purpose. Generate the key *before the first attempt* and reuse.
- **Idempotency keys have TTLs.** A key remembered forever is a storage cost; a key remembered too briefly allows old duplicates to slip through. Common compromise: 24-72 hours.
- **The action might be idempotent; the side effect might not be.** Sending an email twice may be "the same" in the API but the recipient sees two emails. Be careful about external effects.
- **Race between "check if done" and "do":** classic. Use compare-and-set or transactional patterns, not "if not exists: create."
- **At-least-once vs exactly-once:** at-least-once + idempotency = effectively exactly-once. Pure exactly-once is much harder and rarely needed.
- **Non-deterministic operations.** LLM calls with `temperature > 0` are not deterministic — even with the same input, output differs. Idempotency key gets you "the same response if I retry within TTL"; it doesn't get you "deterministic if I retry tomorrow."
- **Concurrent retries** of the same operation can both reach an "is this done?" check before either has written. Lock or use the idempotency-key store as the lock.

## 5. Applicability to Runa

For **Heimskringla (model-call retries)**:

- Every cloud provider call carries an idempotency key (provider-supported where available; semantic-cache key elsewhere).
- The per-provider cache ([[33-model-routing-ensembles]] research doc) plus idempotency keys make retries safe.

For **Muninn (memory writes)**:

- Every episode has a UUID `episode_id`. Writes use INSERT OR IGNORE — replayed writes are no-ops.
- Reflection-pass consolidation writes are keyed by (cluster_id, model_version) so reruns produce the same summary unless inputs changed.

For **Skuld (task ledger)**:

- Task transitions use compare-and-set. A duplicate "mark complete" attempt no-ops.
- Crash recovery: in-progress tasks are re-loaded; the resume logic runs through idempotent steps.

For **Smiðja (tool calls)**:

- Tools that affect external state (send email, write file, create thing) accept an idempotency_key in their invocation. The kernel generates the key from the originating event's correlation_id, ensuring retries within a turn are deduplicated.
- File writes go through `atomic_write` or `write_if_changed`.

For **adapters (chat platforms)**:

- Outgoing message sends use platform-specific idempotency (Discord supports it via message dedup; others vary). When not natively supported, dedup at the adapter layer using a recent-sent table.

For **Eir (repair)**:

- Repair actions are *especially* important to make idempotent. A repair that runs twice should not double-repair (e.g., compact-and-vacuum a SQLite that was already compacted).

What to avoid:

- Don't retry non-idempotent operations without dedup. The cost of two-of-everything compounds quickly.
- Don't generate a fresh idempotency key per retry. Defeats the purpose.
- Don't skip TTL management on idempotency-key stores. Memory grows without bound.
- Don't conflate "the call is idempotent" with "the call has no side effects." A `GET` that triggers a webhook is no longer side-effect-free.

## 6. Open questions

- **Distributed idempotency at scale.** Cross-node coordination of idempotency-key stores requires consensus (Redis, Paxos-based) and adds latency. Trade-offs.
- **Idempotency for LLM calls.** With non-zero temperature, "idempotent" means "returns cached response if within TTL" — not the more-rigorous mathematical sense. Worth distinguishing.
- **Idempotency annotations.** Marking functions as `@idempotent` is conceptually appealing but not widely standardised in Python.

## 7. References (curated)

- stripe.com/docs/api/idempotent_requests — Stripe's industry-leading docs.
- Pat Helland, "Memories, Guesses, and Apologies," ACM Queue 2007.
- restfulapi.net/idempotent-rest-apis/ — RESTful semantics.
- github.com/jd/tenacity — retry library.
- aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/ — Amazon's "Builders' Library" article.
- Companion docs: [[01-exception-design]], [[06-retry-strategies]], [[11-crash-only-software]], [[22-event-sourcing-cqrs]] (research corpus).
