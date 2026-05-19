# 42 — Hexagonal Architecture (Ports & Adapters)

**Category:** Architecture Patterns
**Runa relevance:** core/ vs adapters/ boundary (DOMAIN_MAP), testability, future-proofing
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Hexagonal architecture** (Alistair Cockburn, 2005, also called "ports and adapters") proposes that an application has a *core* containing the business logic, surrounded by *adapters* that connect the core to external systems (databases, APIs, message queues, UIs). The core defines *ports* — interfaces — that adapters implement. The core doesn't know about specific adapters; it only knows about ports.

For Runa, the architecture is *already* hexagonal in spirit: `runa.core` is the business logic; `runa.adapters.<system>` are adapters for each external surface; the kernel knows about typed interfaces (Protocols), not specific provider classes. This document makes the pattern explicit and shows how to keep the discipline as the code grows.

## 2. Technique / mechanism

**The hexagonal picture:**

```
                ┌─────────────────────────────┐
                │      Driving adapters        │
                │  (UI, CLI, HTTP gateway)     │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │     Driving ports            │
                │  (what the core exposes)     │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │           CORE                │
                │   (business logic; pure;     │
                │    no external knowledge)    │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │     Driven ports             │
                │  (what the core requires)    │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │      Driven adapters         │
                │  (database, model providers, │
                │   chat platforms)            │
                └─────────────────────────────┘
```

- **Driving adapters** call the core (initiate work).
- **Driven adapters** are called by the core (do work for it).
- **Ports** are typed interfaces (Protocols) — the contract.

**Concrete Python pattern:**

```python
# Core defines port (Protocol)
class EpisodeStore(Protocol):
    def write(self, ep: Episode) -> None: ...
    def search(self, query: str, k: int) -> list[Episode]: ...

# Core uses port via parameter
class Kernel:
    def __init__(self, store: EpisodeStore, ...):
        self.store = store
    
    def handle(self, input: Heard) -> Replied:
        relevant = self.store.search(input.text, k=5)
        # ... pure business logic
        return reply

# Adapter implements port
class SqliteEpisodeStore:
    """Adapter for SQLite-backed Muninn."""
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
    
    def write(self, ep: Episode) -> None:
        self.conn.execute("INSERT INTO episodes ...", ep.to_row())
    
    def search(self, query: str, k: int) -> list[Episode]:
        ...

# Composition: wire adapter into core
store: EpisodeStore = SqliteEpisodeStore("muninn.sqlite")
kernel = Kernel(store=store, ...)
```

Core knows about `EpisodeStore`; not about SQLite, not about sqlite-vss, not about whether storage is local or remote. Switching to a different storage backend (PostgreSQL, in-memory for tests, distributed for longhall) is an adapter change — core unchanged.

**Driving vs driven distinction:**

```python
# Driven port — core calls out
class ProviderPort(Protocol):
    async def complete(self, req: Request) -> Response: ...

# Driving port — core exposes for external callers
class KernelDriver(Protocol):
    async def handle(self, input: Heard) -> Replied: ...

# Driving adapter (HTTP gateway)
@app.post("/v1/chat")
async def chat_endpoint(req: ChatRequest):
    heard = Heard.from_chat(req)
    replied = await kernel.handle(heard)  # core via driving port
    return {"reply": replied.text}
```

**Testability:**

The hexagonal structure makes tests trivial. Core tests run against in-memory stub adapters:

```python
class InMemoryEpisodeStore:
    """Fake for testing — implements the port."""
    def __init__(self):
        self.episodes = []
    
    def write(self, ep): self.episodes.append(ep)
    def search(self, query, k): return [e for e in self.episodes if query in e.text][:k]

def test_kernel():
    kernel = Kernel(store=InMemoryEpisodeStore(), ...)
    result = kernel.handle(Heard(text="hi", ...))
    assert ...
```

No SQLite. No file I/O. No real model calls. Just pure-logic tests of the core.

**Dependency direction (the strict rule):**

- Core depends on *ports* (Protocols).
- Adapters depend on *core* (import core types).
- Core does NOT depend on adapters.

If you find `from runa.adapters.discord import ...` in core code, the architecture has broken.

## 3. Key works / libraries

- **Cockburn, A.** "Hexagonal Architecture." 2005. alistair.cockburn.us/hexagonal-architecture/.
- **Martin, R. (Uncle Bob).** "The Clean Architecture." 2012. blog.cleancoder.com. Related framing — onion architecture.
- **Vernon, V.** *Implementing Domain-Driven Design.* Addison-Wesley, 2013. Heavy DDD context.
- **Evans, E.** *Domain-Driven Design.* 2003. The DDD foundation.
- **`hexagonal-template-python`** — example repos on GitHub.

## 4. Pitfalls and gotchas

- **Premature abstraction.** Hexagonal for a 100-line script is overkill.
- **Port explosion.** Too many fine-grained ports — interface fatigue. Coarsen.
- **Anaemic core.** Core that only delegates to adapters is hollow. Real logic must live in core.
- **Adapter leaking into core.** "Just import this one thing from adapters" begins the rot. Resist.
- **Hexagonal + frameworks (Django, FastAPI).** Frameworks expect to dictate structure. Tension; hexagonal usually wins for the core, framework wins for the edges.

## 5. Applicability to Runa

For **`runa.core`** (per ARCHITECTURE.md):

- The core *is* the inside of the hexagon. Pure business logic. No knowledge of SQLite, no knowledge of HTTPX, no knowledge of any specific adapter.

For **driven ports**:

- `EpisodeStore` (Muninn), `TaskLedger` (Skuld), `Embedder`, `ModelProvider`, `EmotionalJournal` (Eldhugi), `WorldStateBridge` (WYRD), etc.

For **driven adapters**:

- SQLite-backed Muninn, sqlite-vss-backed embedder, httpx-based providers, etc.

For **driving ports**:

- `Kernel.handle(heard) -> replied` is the main one.

For **driving adapters**:

- `runa.cli` (Munnr), `runa.apps.gateway` (Bifröst), `runa.apps.voice` (Rödd), each adapter that brings input from a chat platform.

For **dependency rules in `pyproject.toml`**:

- Future: an import-linter config that enforces `runa.core` doesn't import `runa.adapters`. Caught at CI time.

What to avoid:

- Don't let core import from adapters.
- Don't make ports too fine-grained.
- Don't put business logic in adapters — adapters translate, that's all.
- Don't make tests depend on real adapters.

## 6. Open questions

- **Hexagonal vs DDD aggregates.** Both useful; some teams use together.
- **Coupling tests to ports.** When a port's interface changes, tests change. Worth it.
- **Discovery / loading of adapters.** Plugin-style discovery, hard-coded registration — trade-offs.

## 7. References (curated)

- alistair.cockburn.us/hexagonal-architecture/.
- blog.cleancoder.com — Clean Architecture.
- Vernon, *Implementing DDD*, 2013.
- Companion docs: [[28-protocol-classes]], [[41-dependency-injection]], [[44-plugin-architecture-patterns]].
