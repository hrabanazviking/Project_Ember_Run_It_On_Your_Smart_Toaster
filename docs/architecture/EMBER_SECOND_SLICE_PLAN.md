# EMBER_SECOND_SLICE_PLAN — Household Well + Feels Alive + Gets Useful

**Voice:** Architect (Rúnhild Svartdóttir), with Forge Worker (Eldra Járnsdóttir) notes on phasing
**Status:** **Ratified 2026-05-21 by Volmarr.** ("go for slice 2 — bundle 1, 2, 3")
**Last touched:** 2026-05-21 (slice-1 ratification day; slice 2 begins next commit)
**Reads with:** `EMBER_SECOND_SLICE_OPTIONS.md` (the menu this plan was picked from), `EMBER_FIRST_SLICE_PLAN.md` (the model this plan parallels), `docs/decisions/0007-first-slice-ratification-2026-05-21.md` §5 (the candidate-ADR list this plan instantiates).

---

## 0. What "second slice" means here

The first slice built Ember from "documentation-rich, code-empty" to a working CLI that can hold a grounded conversation against `sqlite_vec` + Ollama on a Pi 5. The second slice takes Ember from "single-operator, single-device, batched-replies, retrieval-only" to **"household-shared, streaming, tool-capable, operator-configurable."**

Volmarr ratified all four ADR candidates from ADR 0007 §5 (minus 0012, which stays in the queue):

| ADR | Topic | Bundle origin |
|---|---|---|
| **0008** | Operator config-file loader (YAML + TOML) | Bundle 1 + Bundle 2 |
| **0009** | Streaming Funi replies | Bundle 2 |
| **0010** | `pgvector` Brunnr (Gungnir-compatible) | Bundle 1 |
| **0011** | Tool use (execution, sandbox, approval) | Bundle 3 |

### Acceptance criterion

> A fresh operator on a Raspberry Pi 5 with Ollama already running locally, or on a household machine with a shared Postgres + pgvector instance (Gungnir-shape), can:
>
> 1. `pip install ember-agent[sqlite_vec,pgvector]`
> 2. `ember chat` — sees the Hjarta first-run wizard (unchanged from slice 1).
> 3. Walks Hjarta, ends with a `~/.ember/config/ember.yaml` file the operator can edit afterwards to change Funi model, Brunnr backend, embedding model, logging, tool-approval policy.
> 4. Switches Brunnr backend from `sqlite_vec` to `pgvector` with a config edit, points at an existing Gungnir-shape Postgres, ingests new content via `ember well ingest` that lands in the shared Well.
> 5. `ember chat` — asks a question, **watches the reply stream token-by-token** instead of waiting for the whole thing. Cites grounding chunks from the shared Well.
> 6. Asks a question that wants a tool: *"What does my pyproject.toml say about Python version?"* — Ember produces a structured `ToolCall(name="read_local_file", arguments={"path": "pyproject.toml"})`, Munnr renders the proposed call, the operator approves with one keystroke, Ember reads the file, summarises the answer, and persists both the tool call and the operator's approval to the audit log.
> 7. Network pull mid-conversation → graceful banner (unchanged from slice 1).

If that whole loop works on real hardware against real Gungnir, slice 2 is done.

---

## 1. Dependencies the slice assumes

### 1.1 New deps (all under `[project.optional-dependencies]`, opt-in extras)

| Extra | Pins | Used by |
|---|---|---|
| `config` | `pyyaml>=6.0` | ADR 0008 — YAML loader. TOML reading uses stdlib `tomllib`; TOML writing uses hand-rolled emitter (small, single-purpose). |
| `pgvector` | `psycopg[binary]>=3.2`, `pgvector>=0.3` | ADR 0010 — Postgres + pgvector adapter. |
| `tools` | *(none beyond stdlib for the first three tools)* | ADR 0011 — `search_well` + `read_local_file` use stdlib; `fetch_url` uses stdlib `urllib`. Later tool packs may add deps. |
| `validation` *(optional)* | `pydantic>=2.7` | ADR 0008 — if Volmarr opts in for friendlier validation errors. Default is stdlib `dataclasses` + hand-rolled validators. |

The `sqlite_vec` extra from slice 1 stays. The default `pip install ember-agent` still pulls zero external deps; operators install only what they use.

### 1.2 Standing rules from ADR 0007

These bind every slice-2 module:

- **Stdlib-first.** Add deps only when correctness requires it.
- **Typed-value-over-exception** at every realm boundary. New `Disconnected` / `Unavailable` / equivalent values for any new failure mode that crosses a band.
- **`backend_kind` / `runtime_kind`** declared as class attributes on any new adapter implementing a Protocol.
- **FTS5 input sanitisation** at the adapter boundary — applies to any new backend that exposes a textual search.

---

## 2. The slice as a file list

Files marked **NEW** are created in slice 2. Files marked *(touched)* exist from slice 1 and get edits.

```
src/ember/
├── schemas/
│   ├── config.py                            (touched — see Phase 8.1)
│   ├── tool.py                              NEW — ToolCall + ToolReply + ToolDescriptor (ADR 0011)
│   └── stream.py                            NEW — FuniStreamChunk + StreamFinishReason (ADR 0009)
├── config/                                  NEW — loader subpackage (ADR 0008)
│   ├── __init__.py                          NEW
│   ├── INTERFACE.md                         NEW
│   ├── loader.py                            NEW — load_ember_config(config_root) -> EmberConfig
│   ├── yaml_loader.py                       NEW — read YAML; pyyaml-optional
│   ├── toml_loader.py                       NEW — read TOML; stdlib tomllib
│   ├── overlay.py                           NEW — merge file + env + defaults
│   └── validate.py                          NEW — typed validators with operator-readable errors
├── well/
│   └── brunnr/
│       └── pgvector/                        NEW (ADR 0010)
│           ├── __init__.py                  NEW
│           ├── INTERFACE.md                 NEW
│           ├── adapter.py                   NEW — PgVectorBrunnr
│           ├── schema.sql                   NEW — Gungnir-compatible DDL probe
│           └── secrets.py                   NEW — keyring + file + env secret resolver
├── spark/
│   ├── funi/
│   │   ├── handle.py                        (touched — adds complete_streaming protocol slot)
│   │   ├── ollama/
│   │   │   └── adapter.py                   (touched — adds complete_streaming via /api/chat stream=true)
│   │   └── tools/                           NEW (ADR 0011 — tool framework)
│   │       ├── __init__.py                  NEW
│   │       ├── INTERFACE.md                 NEW
│   │       ├── registry.py                  NEW — global ToolRegistry + ToolDescriptor protocol
│   │       ├── approval.py                  NEW — standing-trust policy + per-call prompt
│   │       └── audit.py                     NEW — append-only audit log writer
│   ├── hjarta/
│   │   ├── machine.py                       (touched — writes ember.yaml at WriteIdentity)
│   │   └── prompts/wizard.toml              (touched — extra states for tools + advanced config)
│   └── munnr/
│       ├── chat.py                          (touched — incremental render + tool-call handling)
│       └── render.py                        (touched — render_stream_chunk + render_tool_call_proposal)
└── tools/                                   NEW (ADR 0011 — first-party tools)
    ├── __init__.py                          NEW
    ├── README.md                            NEW
    ├── search_well.py                       NEW — calls Brunnr.hybrid_search
    ├── read_local_file.py                   NEW — sandboxed path traversal
    └── fetch_url.py                         NEW — stdlib urllib, robots.txt-respecting

config/
├── ember.example.yaml                       (touched — adds streaming, pgvector, tools sections)
├── storage.example.yaml                     NEW — Brunnr backend selection examples
├── sources.example.yaml                     NEW — Smiðja source registry examples
└── tools.example.yaml                       NEW — tool enablement + approval policy

docs/decisions/
├── 0008-config-file-loader.md               NEW
├── 0009-streaming-funi-replies.md           NEW
├── 0010-pgvector-brunnr.md                  NEW
└── 0011-tool-use-framework.md               NEW

docs/adapters/
└── PGVECTOR_BRUNNR_REFERENCE.md             NEW (paralleling GUNGNIR_WELL_REFERENCE.md but Ember-adapter-side)

docs/methodology/                            (untouched)
deploy/pi/INSTALL.md                         (touched — adds slice-2 config + pgvector + tools sections)

tests/unit/
├── test_schemas_tool.py                     NEW
├── test_schemas_stream.py                   NEW
├── test_config_loader.py                    NEW
├── test_config_overlay.py                   NEW
├── test_config_validate.py                  NEW
├── test_brunnr_pgvector.py                  NEW — requires_postgres marker
├── test_funi_ollama_streaming.py            NEW
├── test_funi_tools_registry.py              NEW
├── test_funi_tools_approval.py              NEW
├── test_funi_tools_audit.py                 NEW
├── test_tool_search_well.py                 NEW
├── test_tool_read_local_file.py             NEW
└── test_tool_fetch_url.py                   NEW

tests/integration/
├── test_pgvector_real_backend.py            NEW — requires_postgres marker
├── test_streaming_round_trip.py             NEW
└── test_phase17_acceptance.py               NEW — full slice-2 acceptance flow
```

Total **new** files: ~50. Total **touched** files: ~10. Target Python LOC at acceptance: **5 000 – 7 000** (excluding tests and docs).

---

## 3. Slice phases (ordered, each is a separable commit)

Each phase ends with green test suite + ruff clean + DEVLOG entry. Phases 8-11 must land in order (config loader unblocks everything else); Phases 12-13 and 14-16 can swap if scheduling demands, but the listed order keeps risk linear.

### Phase 8 — Config schemas + loader scaffold (ADR 0008 part 1)

- **Author ADR 0008** capturing the file-format and overlay-order decisions.
- `src/ember/config/{__init__,INTERFACE,loader,toml_loader,yaml_loader,overlay,validate}.py`.
- Touch `src/ember/schemas/config.py` to add a `from_dict()` classmethod for each config dataclass — the loader uses these.
- **Overlay order:** defaults → file → env-vars → `--config-root` CLI flag. (`OLLAMA_HOST` becomes one env-var override among several.)
- Tests: loader parses example YAML and TOML; overlay merges correctly; validation produces operator-readable error messages.
- **Tools file format decision lands here:** YAML for human-edited operator config; TOML stays for Hjarta state prompts (already shipped).

### Phase 9 — Loader integration + Hjarta config write (ADR 0008 part 2)

- Wire the loader into `cli/main.py` — replaces `EmberConfig()` defaults with `load_ember_config(config_root)`.
- `OLLAMA_HOST` keeps working (kept as env-overlay layer above file).
- Touch `spark/hjarta/machine.py` to also write `~/.ember/config/ember.yaml` at the WriteIdentity step (initially with the operator's choices from the wizard, defaults for everything else).
- Write `config/storage.example.yaml`, `config/sources.example.yaml`.
- Touch `config/ember.example.yaml` to reflect the now-real shape.
- Tests: end-to-end first-launch writes both identity + config; second launch loads from file; env-vars override file; CLI args override env.
- **Acceptance:** an operator can edit `~/.ember/config/ember.yaml` to change Funi model, see the change take effect on next `ember chat`.

### Phase 10 — Streaming Funi protocol + Ollama adapter (ADR 0009 part 1)

- **Author ADR 0009.**
- `src/ember/schemas/stream.py` — `FuniStreamChunk(text_delta, done, finish_reason, model_id, prompt_tokens?, completion_tokens?)`.
- Touch `src/ember/spark/funi/handle.py` — `FuniHandle` Protocol gains `complete_streaming(prompt, context, tools) -> Iterator[FuniStreamChunk]`. Default behaviour: yield exactly one chunk with the full reply (so non-streaming adapters auto-satisfy the new slot).
- Touch `src/ember/spark/funi/ollama/adapter.py` — implements `complete_streaming` against Ollama's `POST /api/chat` with `stream=True` (newline-delimited JSON response). Reuses prompt-assembly + message-translation.
- Tests: mocked NDJSON response yields a sequence of chunks; mid-stream URL-error folds into final `FuniStreamChunk(done=True, finish_reason=ERROR)`; non-streaming adapters (future) work via the default implementation.

### Phase 11 — Munnr incremental render + interrupt (ADR 0009 part 2)

- Touch `src/ember/spark/munnr/chat.py` — per-turn loop calls `complete_streaming` when `config.funi.streaming=True` (default true), aggregates chunks for the persisted Episode, renders each `text_delta` as it arrives.
- Touch `src/ember/spark/munnr/render.py` — `render_stream_chunk(chunk)` helper; final disconnect-banner / citations logic unchanged (rendered after the stream ends).
- Add Ctrl-C handler that closes the stream cleanly — partial text becomes the episode's `ember_reply`, with a `[interrupted by operator]` tag.
- Tests: streaming + non-streaming chat both round-trip an Episode; interrupt mid-stream produces partial reply tagged; integration test (`test_streaming_round_trip.py`) drives full flow against mocked Funi.
- **Acceptance:** `ember chat` shows tokens unfolding.

### Phase 12 — `pgvector` Brunnr adapter + secret handling (ADR 0010 part 1)

- **Author ADR 0010.**
- `src/ember/well/brunnr/pgvector/{__init__,INTERFACE,adapter,schema,secrets}.py`.
- Adapter implements `BrunnrHandle` against Postgres + pgvector. Schema probe: if Gungnir-shape tables already exist, use them; if not, run the DDL (mirrors `sqlite_vec/schema.sql` but PG-flavoured, with HNSW cosine index).
- `backend_kind = "pgvector"`.
- `secrets.py` — resolves secrets in order: env-var override → keyring (if `keyring` import available) → mode-600 file at the `PgVectorConfig.secret_ref` path → `Disconnected(AUTH_FAILED)`.
- Connection management: connection-per-handle, no pooling for first ship; ADR 0010 documents the future pool option.
- Tests: round-trip writes + reads against Postgres docker-compose fixture; schema-probe behaviour against existing-tables vs empty DB; mismatched embedding-dim refuses; FTS5 input sanitisation analogue for Postgres `tsvector` queries.

### Phase 13 — Gungnir compatibility + pgvector integration tests (ADR 0010 part 2)

- Live-fire test against real Gungnir (gated on `requires_postgres` + Tailscale reachability check, same shape as `requires_ollama`).
- Confirm bytewise schema compatibility (Ember writes a `Document` + `Chunks`; same row shape as Gungnir's pipeline).
- Hybrid-search RRF (k=60) against the live 35 682-chunk corpus produces sensible results.
- `ember well ingest` with `pgvector` backend writes into a separate test database (not Gungnir's `knowledge`).
- Touch `config/ember.example.yaml` and `config/storage.example.yaml` to make pgvector a one-uncomment switch.
- Touch `docs/adapters/GUNGNIR_WELL_REFERENCE.md` to mark the "pgvector Brunnr is Phase 8" forward-reference as **shipped**.
- Add `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` — adapter-side mirror of the Gungnir reference, covering schema-probe semantics, secret resolution order, connection lifecycle.
- **Acceptance:** an operator with Gungnir on their tailnet can switch via config and have working retrieval.

### Phase 14 — Tool framework: schemas + registry (ADR 0011 part 1)

- **Author ADR 0011.**
- `src/ember/schemas/tool.py` — `ToolDescriptor(name, description, parameters_schema, required_approval)`, `ToolCall(name, arguments)`, `ToolReply(call_id, output, error)`, `ApprovalPolicy(STANDING / PER_CALL / FORBIDDEN)`.
- `src/ember/spark/funi/tools/{__init__,INTERFACE,registry,approval,audit}.py`.
- Registry is global within a process; tools register at import time.
- Approval default: `PER_CALL` (operator approves each invocation interactively); `STANDING` is opt-in via config; `FORBIDDEN` blocks at registry level.
- Audit log: append-only JSONL at `~/.ember/state/tool_audit/<date>.jsonl`. Records call, arguments (redacted per descriptor), approval status, reply, timing.
- Tests: registry holds tools; approval prompt flow with scripted IO; audit log is append-only + atomic-write; forbidden tools refuse at registry level.

### Phase 15 — First three first-party tools (ADR 0011 part 2)

- `src/ember/tools/search_well.py` — descriptor: name `search_well`, parameters `{query: str, k: int}`. Implementation calls `BrunnrHandle.hybrid_search` (or `text_search` if no embedder available). Approval: `STANDING` by default — it's the safest tool, just queries the Well.
- `src/ember/tools/read_local_file.py` — descriptor: name `read_local_file`, parameters `{path: str}`. Sandbox: refuses absolute paths outside the operator's home directory; refuses `~/.ember/secrets/` and `~/.ssh/`. Approval: `PER_CALL` by default.
- `src/ember/tools/fetch_url.py` — descriptor: name `fetch_url`, parameters `{url: str}`. Honors `robots.txt`. Refuses non-`http(s)` schemes, refuses RFC1918 / loopback addresses unless config explicitly allows. Approval: `PER_CALL`.
- Tests: each tool's happy path + each refusal mode. Sandbox tests use `tmp_path` for `read_local_file`; `fetch_url` tests mock `urllib.request.urlopen`.

### Phase 16 — Munnr tool-call integration + Hjarta tools state (ADR 0011 part 3)

- Touch `src/ember/spark/munnr/chat.py` — when `FuniReply.tool_calls` is non-empty, render the proposed call, await approval (per descriptor + config policy), execute, feed `ToolReply` back into the next turn's context.
- Touch `src/ember/spark/munnr/render.py` — `render_tool_call_proposal(call)` + `render_tool_reply(reply)`.
- Touch `src/ember/spark/hjarta/{machine,prompts/wizard}.py` — adds an *Advanced* branch (skippable) that asks: "Enable tools? Which approval policy as default?" Writes choices into the initial `ember.yaml`.
- Touch `cli/main.py` — `--allow-tools` and `--no-tools` flags (override config for a single invocation).
- Integration test: `test_phase17_acceptance.py` walks the full acceptance flow including a tool call.
- **Acceptance:** the operator can ask "what does pyproject.toml say about Python version?" and watch Ember propose + execute + summarise.

### Phase 17 — Slice-2 acceptance and shipping

- `tests/integration/test_phase17_acceptance.py` greens against real `sqlite_vec` + real `pgvector` (docker-compose fixture) + mocked Funi.
- Touch `deploy/pi/INSTALL.md` — adds slice-2 sections: editing `ember.yaml`, enabling streaming, switching to `pgvector`, enabling tools, approval policy.
- Author `docs/decisions/0013-second-slice-ratification.md` ratifying the slice (parallels ADR 0007).
- `pyproject.toml` bump 0.1.0 → 0.2.0; Development Status stays `3 - Alpha`.
- `src/ember/__init__.py` docstring updated.
- DEVLOG entry — slice 2 ratified.

---

## 4. What the slice deliberately does NOT include

Each of these is a *later* slice. None block slice-2 ratification.

- **Other Brunnr backends** (`qdrant`, `chroma`, `lancedb`).
- **Other Funi runtimes** (`llamacpp`, `lmstudio`, `phi_silica`, `apple_foundation`).
- **Other Smiðja sources** (`url_fetch`, `shared_well`, `nomad`).
- **Other surfaces** (Auga GUI, Rödd voice, Bifröst HTTP gateway — these are ADR 0012, deferred).
- **Writable tools** (file write, shell command execution, git operations, MCP tool bridge). The slice-2 tool framework is read-only first; writes get their own ADR after operators have lived with reads for a while.
- **Multi-operator shared Wells** (one Well per operator; concurrent writers are out of scope until backend-level locking is settled).
- **Skein / KG retrieval layers** (the cheap+expensive KG split documented in `GUNGNIR_WELL_REFERENCE.md` §5; depends on Skein/Skry being usable as Ember adapters, separate ADR).
- **Plugin framework** (third-party tools / Brunnr backends / Funi runtimes loaded from the operator's environment). The Phase-1 scaffold `src/ember/plugins/` stays empty.
- **Backup / restore / export-import** for the Well (operational tooling, separate slice).
- **Voice + image modalities for Funi** (Funi stays text-only).

---

## 5. Forge Worker's quality bar

Same standing requirements as the first slice plan §6, plus:

- **Type-checked under mypy strict.** Includes the new Protocols (`complete_streaming`, tool registry).
- **One responsibility per function.** Tool definitions are intentionally tiny; if a tool needs >50 LOC, it's two tools.
- **No hardcoded settings.** Tool sandbox limits, approval defaults, secret resolution order are all config-driven.
- **No hardcoded data.** Tool descriptors live in code (because they're code-defined behaviour) but their `description` strings live in `config/tools.example.yaml` for translation-ability.
- **Every new realm-boundary failure returns a typed value.** Per ADR 0007 §2.2.
- **Every new Brunnr / Funi / Tool adapter declares its `*_kind` class attribute.** Per ADR 0007 §2.3.
- **All operator-supplied text passed to backends is sanitised at the adapter boundary.** Per ADR 0007 §2.9 — pgvector tsvector queries get the same treatment as FTS5.
- **Whole files only.** Never deliver fragments, snippets, or partial updates.

When a phase ships: Auditor pass + DEVLOG entry + push.

---

## 6. Risks the Forge Worker flags now

| Risk | Mitigation |
|---|---|
| Config loader scope creep (every operator wants a different validation message) | Ship minimal validation in Phase 8; add `pydantic` as opt-in extra later if operator feedback demands it. |
| Streaming + Ctrl-C interaction is OS-specific (signal handling differs on Linux / macOS / Windows) | Implement on Linux first; Windows / macOS specifics get an ADR follow-up if the cross-platform story breaks. |
| pgvector + Gungnir schema drift (Volmarr changes the Gungnir schema between slice-1 survey and slice-2 ship) | Adapter probes existing schema at open time; refuses with operator-readable message if shape doesn't match. Re-survey Gungnir live before Phase 12. |
| Tool sandbox escapes (operator runs Ember on a server where path-traversal regex bypass leaks `/etc/shadow`) | First three tools are read-only and minimally scoped. ADR 0011 explicitly defers writable tools to a separate slice. Sandbox tests cover known traversal patterns + symlink escapes. |
| Audit log grows unbounded | Per-day file rotation; operator can `rm` old days. Phase-9 cleanup utility not in scope. |
| Phase ordering breaks if Phase 10 (streaming) ships before Phase 9 (config integration) | Streaming uses `config.funi.streaming` which doesn't exist until Phase 9. Plan keeps the order; if priority pressure inverts it, Streaming defaults to `True` and Phase 9 opts operators *out* via config. |
| The whole slice is too big for one push | Phases 8-9 are ADR 0008 standalone; if scheduling pressure builds, ship as **slice 2a (0008 only)**, then 2b (0009+0010), then 2c (0011). The plan as written assumes all four ship as slice 2.0.0. |

---

## 7. Forge Worker's closing word

> *The first slice built a small fire from cold stones. The second slice teaches that fire to grow without losing the discipline that kept it small. Four ADRs is more than any one session — pace, ratify each phase, and remember that what survived slice 1 was clarity, not speed.*

— Eldra Járnsdóttir

---

## 8. Session pacing — for the reader

This slice is **substantially larger than slice 1**:

| Slice | ADRs | Phases | Target LOC (excl. tests/docs) | Sessions (rough) |
|---|---|---|---|---|
| First (shipped) | 0 implicit + 0006/0007 ratifying | 7 | ~2 500 | 1 long session |
| **Second (this plan)** | **4** (0008, 0009, 0010, 0011) | **10** (Phases 8-17) | **~5 000 – 7 000** | **3-5 long sessions** |

Each phase ends with a green commit. **No phase blocks the previous one from being shipped**, so if scheduling demands a pause after any phase, the in-flight work is already on `development` and the next session resumes from there.

**Suggested natural break points** for multi-session work:
- After Phase 9 (config loader fully landed): operators can already customise without further work. Ship `0.1.5` if desired.
- After Phase 11 (streaming landed): operator UX delta complete. Ship `0.1.7`.
- After Phase 13 (pgvector landed): Gungnir story complete. Ship `0.1.9`.
- After Phase 16 (tools landed): full slice-2 capability. Ship `0.2.0-rc1`.
- After Phase 17 (acceptance): **`0.2.0` released.**

When a phase begins in a future session, the natural opening is **"go for phase N"** — same shape as slice 1's rhythm.
