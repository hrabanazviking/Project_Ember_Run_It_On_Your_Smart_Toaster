# ADR 0007 — First-slice ratification

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr.** ("go for phase 7")
**Author:** Mythic-Engineering session driven by Volmarr — Architect / Forge Worker / Auditor / Scribe (roles rotated through the slice)
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

The first slice of Ember is complete: Phases 1-7 of
`docs/architecture/EMBER_FIRST_SLICE_PLAN.md` shipped in a single day
(2026-05-21) across 11 commits. The acceptance criterion of §0 of that
plan — *"a fresh operator can install Ember, walk Hjarta, ingest a
directory, ask a grounded question, and survive a network-pull mid-
conversation with a graceful banner"* — is met, and verified
end-to-end against real `sqlite-vec` + real Ollama with `phi3:mini`.

This ADR captures the load-bearing decisions made or confirmed during
the slice. They are the standing law for the second slice and beyond.

## 2. Decisions

### 2.1 Stdlib-first dependency policy

**Decision:** Every first-slice subsystem is stdlib-only by default;
external dependencies are added only when there is no stdlib path.

**Concrete consequences:**

| Subsystem | Stdlib? | External dep |
|---|---|---|
| Schemas | `dataclasses` + `enum.StrEnum` | None |
| Brunnr (sqlite_vec) | `sqlite3` | `sqlite-vec` (the vector index — no stdlib alternative) |
| Smiðja embed client | `urllib.request` | None — no `httpx` |
| Smiðja journal | `json` + `tempfile` + `os.replace` | None |
| Funi (Ollama) | `urllib.request` | None — no `httpx` |
| Hjarta state prompts | `tomllib` (stdlib in 3.11+) + `importlib.resources` | None |
| Hjarta identity | `json` | None |
| CLI dispatcher | `argparse` | None — no `typer` |

**Why:** The Vow of Smallness. Two HTTP clients now live in the codebase
(Smiðja + Funi); both use stdlib. Adding `httpx` would replace *both*;
neither needs it individually. A Pi 5 install of Ember + `sqlite-vec`
is under 10 MB of Python deps.

**When to revisit:** If a future subsystem cannot achieve correctness
with stdlib (e.g. WebSocket-based streaming for Funi), add the
narrowest dependency that does the job. Add it under
`[project.optional-dependencies]` so operators opt in.

### 2.2 Typed-value-over-exception for cross-realm failure

**Decision:** Failure that crosses a realm boundary is a *typed return
value*, not an exception. Internal-to-realm errors may still raise.

**Concrete forms:**

- `Brunnr.open()` → `BrunnrHandle | Disconnected(reason, since, detail)`.
- `Strengr.open()` wraps the above; never raises a connection error.
- `Strengr.health()` always returns `StrengrHealth`; on failure
  `last_ok=None` with a populated `detail`.
- `Funi.open()` → `FuniHandle | Unavailable(reason, detail)`.
- `Funi.complete()` always returns `FuniReply`; mid-call failure
  becomes `finish_reason=ERROR` with operator-readable text.
- `Funi.health()` mirrors `Strengr.health()` — never raises.

**Why:** The Vow of Graceful Offline. Spark code is forced by the type
system to handle the failure branch — there is no `except` shortcut
that lets an unhandled `Disconnected` propagate. The Vow becomes a
*compile-time-checkable property*, not a runtime convention.

**Where exceptions still live:** Programming-error cases (`BrunnrError`
for "you asked for a chunk_id that doesn't exist"; `HjartaError` for
"the identity file is corrupt") raise normally. The split is *"is this
the operator's network failing, or is this our code wrong?"*

### 2.3 Backend kind on the Protocol, not in the config

**Decision:** Every `BrunnrHandle` carries a `backend_kind: str` class
attribute; every `FuniHandle` carries `runtime_kind: str`. Health
helpers read the attribute off the handle.

**Why:** The handle already knows what it is. Passing config through
`health()` to recover the name was the alternative; that couples
diagnostic code to configuration. The attribute approach lets
`getattr(handle, "backend_kind", "unknown")` degrade gracefully for
legacy or stub handles.

### 2.4 Recoverable vs non-recoverable disconnect reasons

**Decision:** `DisconnectReason` is partitioned into two sets:

- **Non-recoverable** (`CONFIG_INVALID`, `AUTH_FAILED`, `DNS_FAILURE`):
  Strengr fast-fails after a single attempt. Operator typo feedback is
  instant.
- **Recoverable** (`CONN_REFUSED`, `TIMEOUT`,
  `BACKEND_REPORTED_UNAVAILABLE`, `UNKNOWN`): Strengr retries up to
  `retry_attempts` with exponential backoff capped at
  `retry_backoff_max_s`.

**Why:** Retrying a typo'd config 3× with backoff before reporting it
is bad UX. Splitting the reasons keeps "your server is slow" patient
and "your config is wrong" snappy.

### 2.5 Stdlib `dataclasses` over `pydantic` for schemas

**Decision:** All Phase-2 schemas are `dataclasses.dataclass(frozen=True, slots=True)`. No `pydantic` dependency in the first slice.

**Why:** Phase 2's responsibility is *types only* (the gravitational
floor). No validation is needed at the type-definition layer; the
loader (Phase 9+) handles operator-supplied YAML/TOML validation.
`dataclasses` is stdlib, hashable when frozen, and import-fast on
Pi-class hosts.

**When to revisit:** When the config loader needs structured-error
validation messages for operators (e.g., "your `embedding_dim` must be
a positive integer"), introduce `pydantic` as an optional dep just
for that subpackage. Don't promote it project-wide.

### 2.6 Prompts as data, identity as JSON, config as TOML

**Decision:** Three different file formats serve three different needs:

- **Hjarta state prompts**: TOML (read-only, multi-line strings,
  stdlib `tomllib`).
- **Identity**: JSON (read+write, small flat structure, stdlib both
  directions).
- **Operator config** (Phase 9+): the example file in `config/` stays
  YAML for human-editing aesthetics; loader will accept both YAML and
  TOML.

**Why:** Per RULES.AI.md "no hardcoded data": prompts live in files,
not source. JSON for writes avoids needing `tomli_w`; TOML for reads
avoids `pyyaml`. Both are stdlib.

### 2.7 Gungnir-aligned defaults

**Decision:** Default values in `EmberConfig` mirror the *measured*
Gungnir corpus:

- `embedding_dim = 768` (matches `nomic-embed-text`).
- Chunker `max_chars = 2000`, `target_chars = 1684` (Gungnir's measured
  average chunk length).
- `EmbeddingConfig.model = "nomic-embed-text"`.

**Why:** Bytewise compatibility with the operator's existing Gungnir
Well, when present. Means a future operator who has both an Ember local
SQLite Well and a Gungnir pgvector Well can move chunks between them
without re-embedding.

### 2.8 `cli/__init__.py` is intentionally empty re-exports

**Decision:** `src/ember/cli/__init__.py` does not import `main` from
the submodule.

**Why:** `from ember.cli.main import main` *rebinds* the
`ember.cli.main` attribute on the package object from the submodule to
the function, breaking `import ember.cli.main as alias` callers
(including `ember.__main__` and the skeleton test). The fix is to
*not* re-export; `pyproject.toml`'s `[project.scripts]` already names
the full dotted path.

### 2.9 FTS5 input sanitisation at the adapter boundary

**Decision:** All operator-supplied text passed to FTS5 is sanitised by
`SqliteVecBrunnr._escape_fts5_query`: tokenise on whitespace, wrap each
token as a literal phrase (doubling internal `"`), OR-join.

**Why:** Operator chat input may contain FTS5-reserved syntax (`:`,
`AND`, `*`, parentheses, quotes, `NEAR`). Without sanitisation, a chat
like `"run: a marathon"` raises `no such column: run`. Caught originally
in the Hjarta probe; the sanitiser is the real fix because
`ember chat` operator input goes through the same path.

### 2.10 OLLAMA_HOST env var as the Phase-9-loader escape hatch

**Decision:** `cli/main.py` reads `OLLAMA_HOST` and applies it as an
override to both `funi.ollama.base_url` and
`smidja.embedding.endpoint`. Accepts the same shapes Ollama's own CLI
accepts.

**Why:** Operators with Ollama bound to a non-default interface
(Tailscale, Docker, remote) need a way to point Ember at the right
endpoint *before the full config loader ships in Phase 9+*. Honoring
Ollama's own env var convention is least-surprise.

**When the config loader lands:** `OLLAMA_HOST` will continue to be
honored as an override over the file-based config, matching how every
other Ollama-ecosystem tool behaves.

## 3. Consequences

### 3.1 What is now true

- Ember is `0.1.0`. The first slice is shippable.
- The seven phases of `EMBER_FIRST_SLICE_PLAN.md` are complete.
- A fresh operator with a Pi 5 + Ollama + `sqlite-vec` can install, walk
  Hjarta, ingest a directory, and have a grounded conversation —
  verified end-to-end.
- 222 tests pass + 2 skipped (real-Ollama integration tests gated on
  reachability). Ruff clean.
- The plan is closed; `EMBER_FIRST_SLICE_PLAN.md` moves to
  `docs/archive/` when Volmarr ratifies the close.

### 3.2 What's NOT done (deliberately out of slice)

- Other Brunnr backends (`pgvector`, `qdrant`, `chroma`, `lancedb`).
- Other Funi runtimes (`llamacpp`, `lmstudio`, `phi_silica`,
  `apple_foundation`).
- Other Smiðja sources (`url_fetch`, `shared_well`, `nomad`).
- Streaming Funi replies.
- Tool use beyond the reserved API slot.
- Voice / GUI / HTTP gateway surfaces.
- Multi-operator shared Wells.
- Plugins.
- A full YAML/TOML config loader (Phase 9+).

These are all explicitly named as non-goals in `EMBER_FIRST_SLICE_PLAN.md` §4.

### 3.3 Decisions that bind the second slice

- Stdlib-first remains the default policy. Any new dep needs justification.
- The typed-failure pattern (Disconnected/Unavailable) extends to every
  new realm boundary.
- New Brunnr backends declare `backend_kind` as a class attribute.
- New Funi runtimes declare `runtime_kind` as a class attribute.
- New operator-input text passed to any backend must be sanitised at
  the adapter boundary (see §2.9).

## 4. Alternatives considered

- **Ship a full YAML config loader as part of Phase 7.** Rejected as
  scope creep. The env-var override (§2.10) covers the urgent
  operator-needs case (Ollama on a non-default endpoint) in 30 lines of
  code, with two parametrised tests.
- **Make the FTS5 fix in Hjarta only (revert the adapter fix).** Rejected
  because operator chat input would re-trigger the same bug. The right
  layer for input sanitisation is the adapter.
- **Defer the first-slice ratification to a separate session.** Rejected
  because the work was done atomically in one day and the
  acceptance criterion verified live; sleeping on it adds no signal.

## 5. Open follow-ups (slice 2 starting points)

- ADR 0008: full operator config-file loader (YAML + TOML).
- ADR 0009: streaming Funi replies (server-sent events, incremental
  render in Munnr).
- ADR 0010: `pgvector` Brunnr — the Gungnir-compatible backend (Phase 8
  of the original plan).
- ADR 0011: tool use — execution model, sandbox policy, operator
  approval flow.
- ADR 0012: Auga (GUI), Rödd (voice), Bifröst (HTTP gateway) — which
  surface ships first.

## 6. Provenance

Reproducible: every commit in the slice (`df67f2a` through `954038d`
plus this commit) is on the `development` branch of
`hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster`. The full
test suite runs in 0.29 s on the travel laptop; the real-Ollama
acceptance smoke was captured in the DEVLOG entry for this commit.

— Eirwyn Rúnblóm (Scribe), with Rúnhild (Architect) and Eldra (Forge Worker)
