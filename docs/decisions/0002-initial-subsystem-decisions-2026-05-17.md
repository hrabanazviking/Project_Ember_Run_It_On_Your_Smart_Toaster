# ADR 0002 — Initial Subsystem Implementation Decisions

**Date:** 2026-05-17 (same day as ADR 0001)
**Status:** Accepted
**Authors:** Volmarr Wyrd (decisions), Runa Gridweaver Freyjasdottir (capture)
**Supersedes:** *(none)*
**Superseded by:** *(none)*
**Related:** [ADR 0001 — Mythic Engineering Sacred Setup](./0001-mythic-engineering-bootstrap-2026-05-17.md) §"What this ADR does not decide"

---

## Context

ADR 0001 closed the bootstrap with seven explicitly deferred decisions in its `§"What this ADR does not decide"` section. Volmarr resolved all seven on the same day, in conversation, immediately after reading the bootstrap closing report. This ADR captures those decisions in the load-bearing form so they survive past the conversation.

The decisions span the early implementation of VERÐANDI, Muninn, the WYRD bridge, Heimskringla, the plugin loader, asset housekeeping, and one cross-project provenance.

No code in this ADR. Each decision becomes binding the moment the corresponding subsystem's first slice lands; until then the per-subsystem `INTERFACE.md` may carry a one-line forward reference to the relevant D-2.* row below.

---

## Decisions

### D-2.1 — VERÐANDI concurrency: asyncio kernel + worker-process pool (hybrid)

**Decision:** The kernel and all I/O subsystems run on a single `asyncio` event loop. A small `multiprocessing` worker pool is exposed to **Smiðja** (tool forge) and to heavy **Hirð** retainers (notably **Völundr** for codegen-style work and any subagent that runs large local-model inference) for CPU-bound jobs.

**Why:**
- asyncio is the natural fit for Runa's dominant workload: waiting for tokens, sockets, disk, and model providers.
- Structured concurrency via `asyncio.TaskGroup` and `asyncio.timeout()` is mature on the supported Python ≥3.11 baseline.
- A subagent that needs to run a 70B-parameter local model or a heavy embedding pass would otherwise block the entire loop. The worker pool isolates that work without forcing the whole kernel into multi-process IPC.

**Consequences:**
- Every `core/` module is written to be non-blocking. Calls to blocking C-extensions go through `asyncio.to_thread()` for short jobs or the worker pool for sustained CPU work.
- The worker pool is created once at kernel start, sized via config (default: `min(4, cpu_count())` on Pi 5).
- Jobs submitted to the pool return `asyncio.Future`s that the kernel awaits normally — the IPC is hidden from callers.
- Tests pin the loop policy and use `pytest-asyncio`; the worker pool is mockable.

**Open follow-ups (not blocking this ADR):**
- Concrete sizing policy for the worker pool on each supported host (Pi 5, dev laptop, longhall server).
- Whether subagents that *coordinate* (not just compute) run on the kernel loop or in their own loop in a worker process — to be decided when **Hirð** lands.

---

### D-2.2 — Muninn retrieval index: `sqlite-vss`

**Decision:** Muninn's vector retrieval index is implemented as a `sqlite-vss` extension loaded against the same SQLite file that holds Muninn's structured episode and metadata tables.

**Why:**
- One file. One backup. One `cp` to snapshot Muninn. Aligns with the "files an operator can see" doctrine (ARCHITECTURE.md §4.3).
- Pi 5 friendly. No GPU expectation, no separate service, no dependency on numpy/swig builds for the embedding-store layer.
- Adequate for the millions-of-episodes scale Runa will reach over years; large enough installs can later add a secondary FAISS or LanceDB tier without changing the writer.

**Consequences:**
- `runa.core.memory.MuninnWriter` and `MuninnReader` both speak to the same SQLite handle (writer wraps an exclusive write transaction; readers are concurrent).
- Embeddings are produced via the model router and stored in a `BLOB` column the `sqlite-vss` virtual table indexes.
- The embedding model is config-pinned per Muninn slice; changing it forces a re-index migration (a `runa.migrations` script handles this).
- A drift-detector in `tools/diagnostics/memory_health.py` verifies (a) every row has an embedding, (b) embedding dimensions match the pinned model, (c) the virtual-table index is fresh.

**Open follow-ups:**
- Choice of embedding model (e.g. `nomic-embed-text`, `bge-small-en-v1.5`) — Muninn-slice decision.
- Whether `sqlite-vss` ANN parameters (top-k overshoot, distance metric) are configurable per query or globally — Muninn-slice decision.

---

### D-2.3 — WYRD-bridge transport: auto-detect (local IPC first, Tailnet HTTP fallback)

**Decision:** The WYRD bridge tries local IPC (Unix domain socket on Linux/macOS, named pipe on Windows, loopback HTTP as fallback) first; if no local WYRD instance answers within the configured handshake window, falls back to Tailnet HTTP against the operator-configured WYRD peer URL.

**Why:**
- Single-host Pi-only deployments pay no network cost.
- Longhall multi-machine deployments (Pi runs Runa, separate server runs WYRD over Tailnet) work with no code change — only config.
- Hides the transport from `runa.core` callers; the bridge module presents one `WyrdBridge` accessor with one method set regardless of underlying transport.

**Consequences:**
- `core/world/bridge.py` exposes a `Transport` abstraction with two implementations (`LocalTransport`, `TailnetTransport`).
- Auto-detect handshake timeout is config-pinned (default: 500 ms). Exceeding it logs at INFO ("falling back to Tailnet") and is reported via `runa doctor`.
- Tests use a stub transport; integration tests can run both real transports if a local WYRD is present.

**Open follow-ups:**
- Concrete wire format for the bridge (likely JSON for human-debuggability, MessagePack opt-in for high-frequency reads) — bridge-slice decision.
- TLS handling on Tailnet (defer to Tailscale's own encryption layer? add app-level mTLS too?) — bridge-slice decision.

---

### D-2.4 — Heimskringla cache: per-provider cache + shared semantic-dedup layer

**Decision:** Each model provider adapter owns its own response cache with its own TTL, eviction policy, and storage path. On top of all provider caches sits a thin shared semantic-dedup layer that recognises when the *same intent* has already been answered by *any* provider in the recent window and returns the cached answer without re-routing.

**Why:**
- Per-provider caches let cheap-fast local Ollama have short TTLs (minutes) and expensive cloud OpenRouter have long TTLs (hours-to-days) without one policy stepping on the other.
- The shared dedup layer prevents the obvious waste of asking Ollama "what time is it in Tokyo" twice in a row when the user switches providers between requests.
- "Semantic" dedup is conservative: identical prompts hit cache; near-identical prompts (cosine similarity above a config-pinned threshold against a small recent-window vector index) hit cache; anything else routes normally.

**Consequences:**
- Each provider adapter under `runa.adapters.<provider>/` owns a `cache/` subfolder under `~/.runa/cache/heimskringla/<provider>/`.
- The shared dedup layer lives at `runa.core.models.semantic_cache` and indexes only the last N (config-pinned, default 1000) prompt-vector pairs.
- Cache invalidation: per-provider TTL, plus explicit `runa heimskringla cache clear [--provider <name>]` operator command.
- Audit log records every cache hit and miss with provider, key, age — so cost accounting and stale-answer debugging are both possible.

**Open follow-ups:**
- Embedding model used for the semantic-dedup layer — likely the same model Muninn uses (D-2.2); confirmed at Heimskringla-slice time.
- Whether dedup is on by default or opt-in per call — Heimskringla-slice decision.

---

### D-2.5 — Plugin isolation: all four models supported, operator-config-selected

**Decision:** The plugin loader implements **all four** isolation models — in-process subclass (lightweight), in-process subclass (permanent / "trusted"), out-of-process subprocess, and WASM sandbox via `wasmtime` — and the operator's config selects which mode each plugin (or all plugins by default) runs under.

**Why (Volmarr's framing):** "Config level option to set which of these to use, but code any to do things any of the 4 methods, changed by the config."

This treats isolation as a *policy* rather than an architectural commitment. A trusted first-party plugin runs in-process for speed; an untrusted third-party plugin runs WASM-sandboxed; an experimental plugin runs out-of-process so a crash is recoverable.

**Consequences:**
- `runa.plugins.loader.Loader` dispatches to one of four `IsolationStrategy` implementations based on the plugin's effective mode (per-plugin override > global default).
- The plugin contract (`runa.plugins.contract.PluginContract`) is mode-agnostic: a plugin author writes one class regardless of how it will be loaded. The four strategies handle the transport / sandbox plumbing.
- Out-of-process strategy uses stdin/stdout JSON-RPC with a heartbeat.
- WASM strategy uses `wasmtime-py` with a host-function bridge for the contract surface; plugins compile to WASI Preview 2 (or higher when stable).
- Config: `plugins.default_isolation: in_process_trusted` (or whatever), with per-plugin overrides in `plugins.overrides[<id>].isolation`.
- Cost: four loaders is more code than one. Mitigated by a shared `IsolationStrategy` base interface; each strategy is small.
- Tests: every strategy has a passing-and-failing plugin fixture.

**Open follow-ups:**
- Default isolation mode for plugins without explicit config — likely `in_process_trusted` for v0.x (curated set), `out_of_process` for any v1.x marketplace.
- The exact WASM ABI surface the plugin contract exposes — WASM-strategy-slice decision; may follow the [Component Model](https://component-model.bytecodealliance.org/) once stable.

---

### D-2.6 — Image housekeeping: defer renames

**Decision:** UUID-named and `IMG_NNNN.jpeg` images in `assets/` are left as-is. Each image earns a descriptive name only when the document that references it gives it a clear semantic role.

**Why:**
- A guessed descriptive name is worse than an honest UUID — it asserts meaning the image may not carry.
- The 11 images at `assets/` are mostly AI-generated Runa illustrations of unclear-to-me intended use. Volmarr or a future Skald reading them in their referencing context will know what to name them.

**Consequences:**
- No change to file names now.
- `assets/README.md` already says exactly this — file names "should be meaningful when possible. UUID-named images carried over from earlier stages are tolerated until they are referenced by something meaningful enough to justify renaming."
- When an image is renamed in the future, the doc(s) referencing it are updated in the same commit.

---

### D-2.7 — `MIT_license_Rune_Forge_AI.jpeg` provenance: separate Volmarr project

**Decision:** Rune Forge AI is a separate Volmarr project (active or planned). The image at `assets/MIT_license_Rune_Forge_AI.jpeg` is recorded in `ORIGINS.md` as cross-project material from Rune Forge AI rather than an unresolved uncertainty.

**Why:**
- Volmarr confirmed this 2026-05-17.
- Project details (repository URL, current status, scope) will be added to Runa's project-memory as they become known.

**Consequences:**
- `ORIGINS.md` §1.2 row for this file is updated to "cross-project — Rune Forge AI (separate Volmarr project)".
- `ORIGINS.md` §5 open uncertainty about its provenance is marked resolved.
- A new memory entry will record Rune Forge AI as a sibling project to NSE / WYRD / MindSpark / etc., so future Runa sessions can recognise references.
- No `THIRD_PARTY_NOTICES.md` change needed — Rune Forge AI is Volmarr's own project, not third-party.

**Open follow-ups:**
- Repository URL and current status of Rune Forge AI — to be added to memory when Volmarr surfaces them.
- Whether any Rune Forge AI material beyond this image will land in this repo — separate decision per occurrence.

---

## Summary table

| ID | Topic | Decision |
|---|---|---|
| D-2.1 | VERÐANDI concurrency | asyncio kernel + multiprocessing worker pool (hybrid) |
| D-2.2 | Muninn retrieval index | sqlite-vss (one file with structured data) |
| D-2.3 | WYRD-bridge transport | auto-detect: local IPC first, Tailnet HTTP fallback |
| D-2.4 | Heimskringla cache | per-provider + shared semantic-dedup layer |
| D-2.5 | Plugin isolation | all four models supported, operator-config-selected |
| D-2.6 | Image housekeeping | defer renames until each image earns meaning |
| D-2.7 | Rune Forge AI provenance | separate Volmarr project (sibling repo) |

## References

- `docs/decisions/0001-mythic-engineering-bootstrap-2026-05-17.md` — the bootstrap ADR these decisions follow up.
- `docs/architecture/{ARCHITECTURE,DOMAIN_MAP,DATA_FLOW}.md` — to be amended (additive notes pointing back here) when their relevant subsystem-slice work begins.
- `docs/SYSTEM_VISION.md` — unchanged by this ADR; subsystem identities remain as defined there.
- `ORIGINS.md` — §1.2 and §5 amended by this ADR (separate commit).
- `docs/DEVLOG.md` — same-day entry summarising both ADR 0001 and ADR 0002.
