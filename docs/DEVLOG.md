# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

---

## 2026-05-21 — Phase 16 shipped: tool-use live in Munnr + Hjarta + CLI. **0.2.0rc1 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (chat-loop shape + ContextKind.TOOL_REPLY contract), Forge Worker (chat.py tool-loop + Ollama tool-call wire format + Hjarta branch + CLI flags), Auditor (37 new tests + real-llama3.2:3b acceptance smoke + one real-Ollama bug caught), Scribe (this entry + memory).

**Scope:** Final third of slice-2's tool-use work. The framework from Phase 14 and the tools from Phase 15 are now caller-reachable through the chat loop. An operator with `tools.enabled: true` (or the `--allow-tools` flag) sees the full propose → approve → execute → audit → feedback cycle live in `ember chat`. **Bumped to 0.2.0rc1 — release candidate for the slice-2 ratification in Phase 17.**

**What shipped:**

- **`src/ember/schemas/config.py`** — new `ToolsConfig` dataclass: `enabled` (default False per Vow of Sovereignty), `standing_trust`, `approval_overrides`, `allow_private_addresses`, `audit_root`. Added `ContextKind.TOOL_REPLY` for the tool-output-back-into-context channel.
- **`src/ember/schemas/stream.py`** — `FuniStreamChunk.tool_calls: tuple[ToolCall, ...]` extension. Final chunk surfaces what the model proposed.
- **`src/ember/spark/funi/handle.py`** — Protocol signatures updated: `tools: Sequence[ToolDescriptor] | None` (was placeholder `Sequence[str] | None`). `wrap_complete_as_stream` follows suit.
- **`src/ember/spark/funi/ollama/adapter.py`** — major Phase-16 extension:
  - `_descriptor_to_ollama_tool` converts `ToolDescriptor` → OpenAI-style function spec (`{"type": "function", "function": {...}}`). PATH and URL kinds serialise as `string`; enums forwarded.
  - `_parse_tool_calls` consumes the inverse: handles dict-or-string-JSON arguments, drops malformed entries, generates UUID `call_id` when Ollama doesn't supply one.
  - Both `complete()` and `complete_streaming()` now forward `tools` to Ollama instead of refusing.
  - `_messages_from_context` learned to emit `ContextKind.TOOL_REPLY` as `role="tool"` with the `name` field populated from `metadata["tool_name"]`. Empty operator-input is omitted so follow-up turns after a tool call are tool→reply only.
  - The Phase-16 acceptance smoke caught a real Ollama-streaming bug: tool_calls arrive in a **non-`done`** NDJSON frame, before the final `done:true` summary. Fix: the adapter now accumulates tool_calls across frames and attaches the full list to the final chunk. This regression is locked in by `test_streaming_accumulates_tool_calls_from_non_done_chunk`.
- **`src/ember/spark/munnr/chat.py`** — the load-bearing piece:
  - `_maybe_init_tools` side-effect-imports `ember.tools` when enabled, binds `search_well` to the live `BrunnrHandle` + embedder, wires the `StdinApprovalPrompter`, and stands up an `AuditLog`.
  - `_drive_turn_with_tools` orchestrates: stream → render deltas → if `tool_calls`, run `_run_tool_round` → extend context with `TOOL_REPLY` items → loop. Bounded by `_MAX_TOOL_TURNS = 8`. Hits the cap → operator-facing `[tool-loop max iterations reached]` message.
  - `_run_tool_round` per call: render proposal → validate args (`INVALID_ARGUMENTS` → audit + skip + render reply) → resolve approval (`NO_SUCH_TOOL`, `FORBIDDEN_BY_REGISTRY`, `DENIED`, `AUTO_APPROVED`, `APPROVED_THIS_CALL`, `APPROVED_FOR_SESSION` → audit with corresponding outcome; refusals carry `reply=None` so the audit shape distinguishes "tool not called" from "tool called and replied") → execute (any exception folds into typed `ToolReply.error`) → audit → render reply.
  - Session-level `always` approvals accumulate in `tool_ctx.session_standing` (not persisted; restart resets per ADR 0011 §2.4).
  - Operator Ctrl-C mid-stream still short-circuits the loop (Phase 11 behavior preserved).
- **`src/ember/spark/munnr/render.py`** — `render_tool_call_proposal(descriptor, call)` and `render_tool_reply(reply, descriptor, *, outcome)`. Both honor `descriptor.redacted_arg_names`. Reply renderer truncates at 2 KiB stdout preview (full output in audit log).
- **`src/ember/spark/hjarta/machine.py` + `prompts/wizard.toml`** — new `HjartaState.ADVANCED_TOOLS` between `NAME_EMBER` and `WRITE_IDENTITY`. Asks "Enable tools? [y/N]" — empty answer / anything-but-yes leaves it off (Vow of Sovereignty default). When yes, Hjarta writes `tools: {enabled: true}` into the initial `ember.yaml` via the writer's existing `extras` channel.
- **`src/ember/cli/main.py`** — `--allow-tools` / `--no-tools` mutually-exclusive flags. `_apply_tool_overrides` overlays the chosen value on `config.tools.enabled` after every config load (initial + post-Hjarta).
- **`config/ember.example.yaml`** — full `tools:` section with every knob and inline guidance (operator can edit `enabled`, `standing_trust`, `allow_private_addresses`, `approval_overrides`, `audit_root`).
- **`src/ember/__init__.py`** docstring — bump to 0.2.0rc1 narrative.
- **`pyproject.toml`** — `0.1.9` → `0.2.0rc1`.
- **`tests/unit/test_skeleton_imports.py`** — version assertion bumped.

**37 new tests** (485 pass + 2 skip, 18.4s, ruff clean):
- `test_funi_ollama_tool_calls.py` (12): descriptor↔Ollama format round-trip, malformed-entry skipping, JSON-string-argument handling, `TOOL_REPLY` context items → `role=tool` messages, **streaming tool-call accumulation across non-done frames**.
- `test_munnr_render_tools.py` (9): proposal + reply rendering, redaction-on-display, output truncation, all seven `ApprovalOutcome` headline variants.
- `test_phase16_tool_loop.py` (8): full propose-approve-execute-feedback flow with scripted Funi + scripted prompter, audit log records, denied-call-no-execution, unknown-tool path, invalid-args-short-circuits-prompt, standing-tool auto-approval, `tools.enabled=false` skips loop, `_MAX_TOOL_TURNS` cap.
- `test_phase16_hjarta_tools.py` (3): yes/no/empty wizard answers correctly write (or don't write) `tools.enabled`.
- `test_cli_tool_flags.py` (4): `--allow-tools` / `--no-tools` overlay, no-flag identity-preserve, argparse mutual-exclusion.
- Existing test updates: 1 in `test_schemas_funi.py` (TOOL_REPLY in ContextKind set); 2 in `test_funi_ollama*.py` (refuse-tools tests replaced with forward-to-Ollama assertions).

**Real-llama3.2:3b acceptance smoke against the tailnet** — operator asked for `read_local_file`-mediated lookup of `pyproject.toml` version; chat output showed the tool proposal, the sandbox refusal (model gave a malformed `~/home/...` path which the sandbox correctly caught), and the model's natural-language explanation of the failure in the follow-up turn. The full loop fires. (phi3:mini doesn't support tool calls natively — Ollama returned 400; this is documented in `INSTALL.md` as a model-capability constraint.)

**Where Ember stands at 0.2.0rc1:**

| Capability | State |
| --- | --- |
| Hjarta first-run (now includes ADVANCED_TOOLS) | shipped 0.1.0 → 0.2.0rc1 |
| Funi (Ollama) `complete()` + streaming + tool_calls | shipped 0.1.0 → 0.2.0rc1 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C + tool-loop | shipped 0.1.0 → 0.2.0rc1 |
| Config loader (now includes tools section) | shipped 0.1.5 → 0.2.0rc1 |
| Tool framework + first three tools | shipped Phase 14-15 |
| **Munnr tool-call integration + Hjarta tools + CLI flags** | **shipped this phase — 0.2.0rc1** |
| Slice-2 acceptance + ADR 0013 ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 17 — author the full slice-2 acceptance test (`test_phase17_acceptance.py`) walking the operator-flow against real sqlite_vec + mocked Funi + a real first-party tool execution; touch `deploy/pi/INSTALL.md` with slice-2 sections; author `docs/decisions/0013-second-slice-ratification.md` (parallel to ADR 0007); bump to **0.2.0** and ship.

---

## 2026-05-21 — Phase 15 shipped: first three first-party tools (`search_well`, `read_local_file`, `fetch_url`).

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (three tool implementations + sandbox logic), Auditor (41 new tests covering happy-path + every refusal mode), Scribe (this entry + README + memory).

**Scope:** Second third of slice-2's tool-use work. Each first-party tool lives in `src/ember/tools/` and registers itself at import time via the Phase-14 registry. Munnr still doesn't drive them — Phase 16 ships the chat-loop integration and bumps to 0.2.0-rc1. No version bump this phase.

**What shipped:**

- **`src/ember/tools/`** — new subpackage. Three tool modules + a README + a package `__init__` that side-effect-imports all three (so `import ember.tools` is what wires the registry).
- **`src/ember/tools/search_well.py`** — `STANDING` approval (read-only, the safest of the three).
  - Calls `BrunnrHandle.hybrid_search` when an embedder is bound and the query embeds cleanly; otherwise falls back to `BrunnrHandle.text_search`. Falls back again if hybrid raises `BrunnrError` (dim mismatch on a shared Well, etc.).
  - Bound via the **host-state pattern** documented in `ember/tools/README.md` §4: `bind_brunnr(handle, embedder=None)` called once by the host at chat-loop startup. The executor reads the module-level binding and returns a typed `ToolReply.error` if nothing is bound.
  - `k` is clamped to `[1, 25]`; empty queries are refused; per-hit text preview is bounded at 240 chars with `...` suffix.
- **`src/ember/tools/read_local_file.py`** — `PER_CALL` approval. Stdlib-only.
  - Sandbox (in order): non-string path → string-shape refuse; symlink-resolve then check the *resolved* path is under `Path.home()`; denylist of `~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, `~/.aws/`, `~/.kube/`, `~/.gnupg/`, `~/.password-store/`; directory refuse; non-existent refuse; size cap 256 KiB.
  - Crucially: **resolve-before-check** defends against symlink escape (both outside-home and into-denylist symlinks are refused; both cases have unit tests).
  - File body never appears in refusal messages — sandbox refusals carry path + reason only.
- **`src/ember/tools/fetch_url.py`** — `PER_CALL` approval. Stdlib `urllib` + `ipaddress` + `urllib.robotparser`.
  - Sandbox (in order): scheme must be http/https; host required; resolved IP must not be loopback / RFC1918 / link-local / multicast (unless `allow_private_addresses=true` per-call argument); robots.txt honored (missing robots → treated as allowed per standard interpretation); response capped at 1 MiB with truncation note.
  - Three module-level test seams (`_set_url_opener`, `_set_address_resolver`, `_set_robots_fetcher`) plus `_reset_seams()` for teardown — tests drive happy-path + every refusal without any real network traffic.
  - Custom `User-Agent` includes a project URL so site operators can identify the bot.
- **Test seams `_BOUND_BRUNNR`, `_BOUND_EMBEDDER`, `_URL_OPENER`, `_ADDRESS_RESOLVER`, `_ROBOTS_FETCHER`** are module-level by design — production code calls the `bind_*` / `_set_*` setters once at startup. The registry contract (executor signature `Callable[[ToolCall], ToolReply]`) doesn't carry host context, so host-state-as-module-state is the canonical pattern for first-party tools that need a handle. README §4 documents this.
- **`tests/unit/test_tool_search_well.py`** — 11 tests: registration shape; refuses-no-handle / empty-query; text-only path; hybrid path; fall-back-when-embedder-returns-none; fall-back-when-hybrid-raises-BrunnrError; no-results helpful-line; k-clamped-to-25; k-clamped-up-to-1; preview-bounded.
- **`tests/unit/test_tool_read_local_file.py`** — 14 tests: registration shape; reads-utf8-under-home; resolves-tilde; refuses-non-string / empty / outside-home / .ssh / .ember/secrets / .pgpass / nonexistent / directory / above-size-cap; **symlink-escape outside home refused**; **symlink-into-denylist refused** (POSIX-only).
- **`tests/unit/test_tool_fetch_url.py`** — 15 tests: registration shape; happy-path GET with content-type header; refuses-non-string / non-http-scheme / file-scheme / no-host / loopback-default / RFC1918-default; allow_private opens loopback; refuses-unresolvable-host; refuses-robots-disallow; missing-robots-treated-as-allowed; response-truncation; HTTPError-mapped-to-ToolReply.error; URLError-mapped.
- **`tests/unit/test_skeleton_imports.py`** — `ember.tools` added to the import-cleanliness check; the import triggers all three registrations.

**Total tests: 448 passed + 2 skipped, ruff clean.** That's 41 new tests this phase on top of Phase-14's 407.

**Where Ember stands at end-of-Phase-15 (still 0.1.9):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` + streaming | shipped 0.1.0 → 0.1.7 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C | shipped 0.1.0 → 0.1.7 |
| Config loader | shipped 0.1.5 |
| Tool framework (schemas + registry + approval + audit) | shipped Phase 14 |
| **First three first-party tools** | **shipped this phase — gated until Phase 16** |
| Munnr tool-call integration | pending → 0.2.0-rc1 (Phase 16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 16 — wire Munnr to consume `FuniReply.tool_calls`:
- `chat.py` checks the streaming reply for tool calls; resolves approval per ADR 0011 §2.4; prompts the operator when needed; executes via the registry; audits everything; feeds `ToolReply` back into the next turn's context.
- `render.py` gains `render_tool_call_proposal` + `render_tool_reply` helpers.
- Hjarta's wizard gets a skippable "Advanced: enable tools?" branch writing the choice into `ember.yaml`.
- `cli/main.py` adds `--allow-tools` / `--no-tools` per-invocation overrides.
- Bump to **0.2.0-rc1 ("tools live")**.
- Acceptance: operator can ask "what does pyproject.toml say about Python version?" and watch Ember propose `read_local_file({"path": "~/ai/ember/pyproject.toml"})`, approve, see the file content fed into a follow-up answer.

---

## 2026-05-21 — Phase 14 shipped: ADR 0011 + tool framework (schemas + registry + approval + audit).

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0011's nine numbered decisions), Forge Worker (registry + approval + audit modules), Auditor (64 new tests), Scribe (this entry + INTERFACE.md + memory).

**Scope:** First third of slice-2's tool-use work. The framework now exists end-to-end — schemas, process-global registry, policy resolver, interactive prompter, append-only JSONL audit log — but no caller wires through it yet. Phase 15 adds the first three first-party tools; Phase 16 wires Munnr to consume `FuniReply.tool_calls` and bumps to 0.2.0-rc1.

**What shipped:**

- **`docs/decisions/0011-tool-use-framework.md`** — nine numbered decisions covering:
  - Five schemas (`ToolDescriptor`, `ToolCall`, `ToolReply`, `ToolParameter`, `ToolParameterKind`) plus two enums (`ApprovalPolicy`, `ApprovalOutcome`) and one error (`ToolError`).
  - `parameters_schema` is a stdlib `Mapping[str, ToolParameter]` — no jsonschema dep (§2.2). Six kinds: STRING / INTEGER / FLOAT / BOOLEAN / PATH / URL.
  - Registry is process-global, import-time, refuses `FORBIDDEN` at registration, RLock-protected. Re-registration is an error.
  - **`PER_CALL` is the default** approval policy. Config can downgrade `STANDING` to `PER_CALL` (more strict) but cannot upgrade — descriptor is the safety floor. `standing_trust_all` is the operator's "trust everything" knob; `FORBIDDEN` is the absolute floor on the floor.
  - Typed `ApprovalOutcome` distinguishes denied / invalid-args / forbidden / no-such-tool / three approve flavours. Audit log uses this as its primary classifier.
  - `ApprovalPrompter` is a runtime-checkable Protocol; `StdinApprovalPrompter` is the concrete CLI surface (defaults to refuse on EOF or unknown input — safer than silent approve).
  - Audit log is one file per UTC day at `<config_root>/state/tool_audit/<date>.jsonl`. Atomic per line via single `os.write` to an `O_APPEND` fd. Dir mode `0o700`, file mode `0o600`. Reply output truncated to 4 KiB with a truncation flag. Redaction per `descriptor.redacted_arg_names`.
- **`src/ember/schemas/tool.py`** — the schemas above. ToolCall promoted from the placeholder in `ember.schemas.funi` (re-exported there for backwards-compat per ADR §5; existing callers don't break).
- **`src/ember/spark/funi/tools/`** — new subpackage:
  - `registry.py` — `register`, `lookup`, `list_tools`, `is_registered`, `clear`, `validate_arguments` (six-kind stdlib validator, precise bool/int handling per ADR 0011 §2.2).
  - `approval.py` — `resolve(descriptor, *, config_overrides, session_standing, standing_trust_all)` pure policy resolver; `resolve_with_answer(answer)` post-prompt mapper; `StdinApprovalPrompter` interactive surface with redaction-on-display.
  - `audit.py` — `AuditLog(config_root, *, ember_version)` with daily-rotation path, single-write atomicity, UTF-8-safe truncation, NO_SUCH_TOOL → no-descriptor-still-writes path, OSError → ToolError surfacing.
  - `INTERFACE.md` — operator-facing surface contract.
  - `__init__.py` — re-exports.
- **`src/ember/schemas/funi.py`** — Phase-14 promotion: `ToolCall` now lives in `ember.schemas.tool`, re-exported here so historical imports keep working. Inline class removed; one-line `from ember.schemas.tool import ToolCall` keeps `FuniReply.tool_calls` typed the same.
- **`tests/unit/test_skeleton_imports.py`** — adds `ember.spark.funi.tools` to the import-cleanliness check.
- **64 new tests** (407 pass + 2 skip, 18.2s, ruff clean):
  - `test_schemas_tool.py` (12): every dataclass's defaults, frozen-ness, every enum's value set, the re-export-from-funi shim.
  - `test_funi_tools_registry.py` (18): register/lookup/list_tools/clear, re-registration error, FORBIDDEN refuses at registration, six-kind validation including the precise int-vs-bool check from ADR 0011 §2.2 (`isinstance(True, int)` would silently pass; we reject), URL scheme requirement, path-empty refusal, enum constraints.
  - `test_funi_tools_approval.py` (17): STANDING auto-approves, PER_CALL signals prompt-needed, FORBIDDEN resolves as forbidden_by_registry, session-standing skips prompt, standing-trust-all skips prompt, config-can-downgrade-but-not-upgrade (the safety-floor invariant), config-can-forbid-an-otherwise-standing-tool, scripted-IO prompter for y/n/always/eof/unknown, redaction-on-display.
  - `test_funi_tools_audit.py` (17): one-record append, daily rotation across midnight, multi-record append-only, redaction never leaves the file body, output truncation at 4 KiB, mode-0o700 dir / mode-0o600 file (POSIX only), NO_SUCH_TOOL writes a no-descriptor record, denied calls have no reply field, OSError → ToolError surfacing.

**Where Ember stands at end-of-Phase-14 (still 0.1.9):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` + streaming | shipped 0.1.0 → 0.1.7 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C | shipped 0.1.0 → 0.1.7 |
| Config loader | shipped 0.1.5 |
| **Tool-use framework (schemas + registry + approval + audit)** | **shipped this phase — gated until Phase 16** |
| First three tools | pending → Phase 15 (no bump) |
| Munnr tool-call integration | pending → 0.2.0-rc1 (Phase 16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 15 — three first-party tools at `src/ember/tools/`:
- `search_well` (STANDING, `BrunnrHandle.hybrid_search` / `text_search`),
- `read_local_file` (PER_CALL, sandbox rejects `~/.ssh/`, `~/.ember/secrets/`, absolute-outside-home),
- `fetch_url` (PER_CALL, robots.txt, refuses non-http(s) + RFC1918/loopback unless config allows).

Each tool ships with happy-path + every refusal-mode unit test. No version bump for Phase 15 either; the bump lands when Munnr can actually call them in Phase 16.

---

## 2026-05-21 — Phase 13 shipped: live-fire pgvector against Gungnir + container. **0.1.9 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (2 real adapter-bugs found and fixed + container fixture), Auditor (14 new live-backend tests + extension probe), Cartographer (`PGVECTOR_BRUNNR_REFERENCE.md` + Gungnir-ref forward-reference cleanup), Scribe (this entry + operator example yaml + memory).

**Scope:** Second half of slice-2's pgvector work. The Phase-12 scaffold is now operator-flippable: an operator with Gungnir on their tailnet can edit `~/.ember/config/ember.yaml`, set `brunnr.backend: pgvector`, install `[pgvector]` extras, and have working retrieval out of the box. Acceptance criterion from `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 13 met.

**Real adapter bugs caught by live-fire (this is why the test was load-bearing):**

1. **`register_vector` ran before `CREATE EXTENSION`.** `pgvector.psycopg.register_vector(conn)` looks up the `vector` type by name; on a fresh container without the extension it fails with `vector type not found in the database`. Fix: new `_ensure_pgvector_extension(conn, read_only=)` helper probes `pg_extension` first; creates the extension when writable; refuses cleanly on read-only Wells where the extension is missing (operator must `CREATE EXTENSION vector` once as DB owner). The helper sits between `psycopg.connect` and `register_vector` in `open()`.
2. **`{{}}` in schema.sql was a format-string escape that never got escaped.** I wrote it during Phase 12 when the renderer used `.format()`; switched to `.replace()` for the named substitutions but forgot to un-double the braces. Result: `metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb` landed in Postgres as a JSON parse error. Fix: `metadata jsonb NOT NULL DEFAULT '{}'::jsonb`.

Both bugs would have been silent until an operator tried it, which is exactly the case the live-fire test exists to catch.

**What shipped:**

- **`tests/integration/test_pgvector_real_backend.py`** — 14 tests across two classes:
  - `TestContainerWritePath` (10 tests, marked `requires_podman` + `requires_postgres`): module-scoped podman fixture spins up `pgvector/pgvector:pg18` on `127.0.0.1:55432` (loopback only, never tailnet-exposed). Tests cover empty-schema apply, document round-trip + idempotency on hash, dim-mismatch rollback, vector_search nearest-first ordering, text_search via generated `tsv` column, hybrid_search RRF fusion (Frigg chunk excluded when query is Odin-shaped), close-then-reopen schema probe finds existing tables, dim-mismatch on reopen refuses, read-only mode refuses writes with ADR-pointer error.
  - `TestGungnirRetrieval` (4 tests, marked `requires_gungnir` + `requires_postgres`): module-scoped fixture opens read-only against the real `100.67.240.22:5432/knowledge` corpus with the secret pulled from `~/.pgpass` (never echoed into test source). Confirms schema probe finds 201 docs / 37 111 chunks at dim=768, text_search "Odin Allfather" returns Norse-corpus hits, hybrid_search works against the live 37k-chunk index, write attempts raise `BrunnrError("... ADR 0010 ...")`.
- **`src/ember/well/brunnr/pgvector/adapter.py`** — `_ensure_pgvector_extension()` helper (the bugfix above). `open()`'s noqa updated to include `PLR0915` since failure classification naturally adds statements.
- **`src/ember/well/brunnr/pgvector/schema.sql`** — `'{}'::jsonb` (not `'{{}}'`).
- **`pyproject.toml`** — three new markers: `requires_postgres`, `requires_gungnir`, `requires_podman` (informational; gating happens via fixture reachability probes, same pattern as `requires_ollama`). Version bumped to **0.1.9**.
- **`config/ember.example.yaml`** — pgvector subsection expanded to show every knob from `PgVectorConfig`, with inline comments on which are required vs optional, and a pointer to the operator-facing reference doc. The two-line switch is `backend: pgvector` + uncomment the `pgvector:` block.
- **`config/storage.example.yaml`** — replaces the empty placeholder with three worked examples: sqlite_vec default, pgvector against personal Gungnir, pgvector read-only against shared Gungnir. Plus the secret resolution order spelled out.
- **`docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`** — 11-section operator-facing reference paralleling `GUNGNIR_WELL_REFERENCE.md`: install, config minimum, every knob, the schema Ember will see or apply, search semantics, secret resolver order, the full Disconnected-reason → operator-action matrix, Gungnir-specific read-only mode, Phase-12-vs-13 archaeology.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — three forward-reference "ships in Phase 8" entries updated to point at the now-shipped pgvector adapter + reference doc.
- **`src/ember/__init__.py`** docstring — slice-2 Phase 13 (pgvector live) entry.
- **`tests/unit/test_skeleton_imports.py`** version assertion bumped to 0.1.9.

**Total test count: 343 passed + 2 skipped, ruff clean.** That's 14 new live-backend tests on top of Phase-12's 329.

**Where Ember stands at 0.1.9:**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader | shipped 0.1.5 |
| Streaming Funi + Munnr live tokens | shipped 0.1.7 |
| **Brunnr pgvector — Gungnir-compatible, operator-flippable** | **shipped 0.1.9** |
| Tool framework (ADR 0011) | pending → 0.2.0-rc1 (Phase 14-16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Acceptance verified:** An operator with Gungnir on their tailnet can now (a) `pip install ember-agent[pgvector]`, (b) write a 4-key pgvector block in `ember.yaml`, (c) run `ember chat`, and (d) get grounded answers against the live 37k-chunk corpus — with `read_only: true` mechanically protecting Gungnir from any write.

**Next:** Phase 14 — author ADR 0011 + `ember.schemas.tool` (ToolDescriptor / ToolCall / ToolReply / ApprovalPolicy) + `ember.spark.funi.tools/` registry, approval, audit log. No version bump; the operator can't yet call a tool. Phase 15 ships first-party tools (`search_well`, `read_local_file`, `fetch_url`); Phase 16 wires Munnr + Hjarta to the tool framework and bumps to 0.2.0-rc1.

---

## 2026-05-21 — Phase 12 shipped: ADR 0010 + pgvector Brunnr scaffold + secret resolver.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0010 + Protocol parity + connection-per-handle decision), Cartographer (schema mapping against the live Gungnir survey), Forge Worker (adapter + secrets + DDL), Auditor (36 new tests), Scribe (this entry + INTERFACE.md + memory).

**Scope:** First half of slice-2's pgvector work. The adapter, the DDL, the secret resolver, and the registry wiring all ship now; the live-fire integration test against real Gungnir and the operator-facing reference doc are Phase 13 (which also bumps to **0.1.9 "pgvector live"**). No version bump this phase — the adapter is built but the operator can't flip the switch yet, per the standing rule from Phase 7 that we bump when the operator can actually use what's new.

**What shipped:**

- **`docs/decisions/0010-pgvector-brunnr.md`** — the design ADR. Nine numbered decisions covering:
  - Same `BrunnrHandle` Protocol — the slice-1 Protocol holds, no abstract base, no Spark-side branching. (§2.1)
  - **Schema-probe first** — if `documents`+`chunks` exist in the configured schema, use them as-is and verify embedding-dim; never DDL into discovered tables. Episodes (Ember-only) is created when missing. (§2.2-2.3)
  - **RRF `k=60`** matching sqlite_vec and Gungnir's `ingest.py` exactly, so results are commensurate across backends. (§2.4)
  - **Secret resolution order** — env → keyring → mode-600 file → typed `AUTH_FAILED`; secret value never logged, even on error. (§2.5)
  - **Connection-per-handle, no pool** — explicit deferral with the future-hook factory pattern documented. (§2.6)
  - **`tsv` as GENERATED column** — not a trigger; simpler, matches Gungnir. (§2.7)
  - **Eight typed `DisconnectReason` classifications** — Strengr's reconnect policy depends on the recoverable/non-recoverable split being correct. (§2.8)
- **`src/ember/schemas/config.py`** — `PgVectorConfig` extended with `secret_env`, `use_keyring`, `keyring_service`, `username`, `connect_timeout_s`, `read_only`; `secret_ref` got a default (`~/.ember/secrets/well.password`).
- **`src/ember/well/brunnr/pgvector/`** — new subpackage:
  - `schema.sql` — Gungnir-compatible DDL with `{embedding_dim}` and `{schema}` substitution; `CREATE EXTENSION IF NOT EXISTS vector`, HNSW cosine index, GIN tsv index, generated tsv column, episodes table.
  - `secrets.py` — `resolve(config) -> SecretResolution`, mode-600 enforcement with operator-readable refusal messages, URL-username parser, fake-keyring-injectable design for tests.
  - `adapter.py` — `PgVectorBrunnr` implementing the full `BrunnrHandle` Protocol. `open()` is the failure-classification surface: lazy psycopg/pgvector import → typed disconnect on miss; secret resolution → `AUTH_FAILED`; `psycopg.OperationalError` → `_classify_operational_error` mapping (auth/timeout/conn_refused/DNS/unknown). Schema probe via `information_schema.tables` + `pg_attribute` for embedding dim. Hybrid search RRF identical-shape to sqlite_vec. `_quote_ident` escapes schema names safely (rejects NUL bytes).
  - `INTERFACE.md` — operator-facing surface contract; spells out schema-probe semantics, secret resolution order, read-only mode, and the Phase-12 limitations (no live integration test yet, no example config yet).
  - `__init__.py` — re-exports `PgVectorBrunnr` and `open`.
- **`src/ember/well/brunnr/handle.py`** — registry now dispatches `BrunnrBackend.PGVECTOR` to the new adapter (lazy import so the extras stay opt-in).
- **`pyproject.toml`** — `pgvector = ["psycopg[binary]>=3.2", "pgvector>=0.3"]` extra added under `[project.optional-dependencies]`.
- **36 new tests** (329 pass + 2 skip, 14.4s, ruff clean):
  - `tests/unit/test_brunnr_pgvector_secrets.py` (16 tests): env-wins-over-keyring-and-file, custom env-var name, empty-env-treated-as-missing, keyring fallback flow, `use_keyring=False` skip, URL-without-username falls through, explicit username override, custom keyring service, keyring exception → miss, mode-0o600 resolves, mode-0o644 refused, mode-0o604 refused, empty file treated as missing, trailing-newline stripped, total-miss reason aggregates every source, **secret body never leaks into `.reason`**.
  - `tests/unit/test_brunnr_pgvector_schema.py` (20 tests): DDL substitution, episodes table presence, CREATE EXTENSION, HNSW + cosine, GENERATED tsv, custom schema name, double-quote escaping, NUL-byte refusal, registry dispatches PGVECTOR (not "not implemented"), missing-psycopg → `BACKEND_REPORTED_UNAVAILABLE`, misconfigured-backend → `CONFIG_INVALID`, missing-pgvector-subconfig → `CONFIG_INVALID`, Protocol method presence, read-only refusal mentions ADR §, OperationalError classification (auth/timeout/conn_refused/DNS/unknown), Disconnected.since is recent.

**Failures the adapter classifies precisely:** `pgvector` extra not installed; URL malformed; host unreachable (CONN_REFUSED); TCP timeout; auth failed (SQLSTATE 28P01 / 28000); schema-probe mismatch (embedding-dim drift); `pgvector` extension missing; everything else → UNKNOWN with `detail` carrying the original message.

**Where Ember stands at end-of-Phase-12 (still 0.1.7):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader | shipped 0.1.5 |
| Streaming Funi + Munnr live tokens | shipped 0.1.7 |
| **pgvector Brunnr adapter + secret resolver** | **shipped (this phase) — gated until Phase 13** |
| pgvector live (operator can flip the switch) | pending → 0.1.9 (Phase 13) |
| Tool framework | pending → 0.2.0-rc1 |

**Next:** Phase 13 — live-fire test against real Gungnir (`requires_postgres` marker, same shape as `requires_ollama`); confirm bytewise schema compat; hybrid-search RRF against the live 35 682-chunk corpus; `config/ember.example.yaml` + `config/storage.example.yaml` operator switches; `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`; pyproject bump to **0.1.9 ("pgvector live")**.

---

## 2026-05-21 — Phase 11 shipped: streaming Munnr REPL + Ctrl-C tagging. **0.1.7 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (chat.py + render helpers + Ctrl-C handler), Auditor (15 new tests + tailnet-Ollama visual smoke), Scribe (this entry + memory + INSTALL.md note).

**Scope:** Second half of slice-2 streaming work. The Funi-side streaming Protocol shipped in Phase 10 is now wired through Munnr to the operator's terminal. Acceptance criterion from `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 11 met: tokens appear live; Ctrl-C produces a tagged partial reply; the REPL returns for the next prompt.

**What shipped:**

- `src/ember/spark/munnr/render.py` — three new public helpers per ADR 0009 §2.3:
  - `render_stream_chunk(chunk)` — pass-through of `chunk.text_delta` (the Funi adapter preserves whitespace, so the renderer must too).
  - `stream_finish_tag(finish_reason, *, interrupted=False)` — operator-facing tag string for the post-stream line; operator-interrupt wins over any finish reason.
  - `render_citations(hits)` — promoted from `_render_citations`; chat.py prints it *after* the streamed body, only when the Well is reachable.
  - `INTERRUPTED_TAG = "[interrupted by operator]"` exported.
- `src/ember/spark/munnr/chat.py` — REPL branches on `config.funi.streaming`:
  - **Streaming branch** (default): `_run_streaming_turn()` drives the live token loop. Disconnect banner prints first, then deltas land one-by-one, then optional finish tag, then citations. The full joined text is reconstructed for the persisted Episode. `_StreamedTurn` dataclass holds the aggregate.
  - **KeyboardInterrupt** caught inside the streaming loop. Partial text is preserved; `_tag_interrupted()` appends `[interrupted by operator]` to the Episode's `ember_reply`. REPL returns to the next `> ` prompt — Ctrl-C does not tear down the session.
  - **Non-streaming branch** (`streaming: false`): the slice-1 `funi.complete()` path is unchanged. Operators who prefer the old behaviour can opt out via `~/.ember/config/ember.yaml`.
- **Test doubles updated** per ADR 0009 §2.2 — `tests/integration/test_phase6_acceptance.py::_FakeFuni` routes `complete_streaming` through `wrap_complete_as_stream`. The Hjarta-only doubles (`test_phase9_operator_edit.py`, `test_hjarta_machine.py`) get raising `complete_streaming` stubs for Protocol completeness; Hjarta never calls them.
- **15 new tests** (293 pass + 2 skip, ruff clean):
  - `tests/unit/test_munnr_render.py` — 9 new cases covering `render_stream_chunk`, `stream_finish_tag` across all `FinishReason` values + interrupted override, public `render_citations`.
  - `tests/integration/test_phase11_streaming.py` — 6 acceptance cases: streaming default takes stream path, full reply persists to Episode, Ctrl-C tags partial + REPL keeps going, `streaming=False` falls back to `complete()`, disconnect banner precedes tokens, `FinishReason.LENGTH` appends truncation tag.
- `pyproject.toml` bumped to **0.1.7**.
- `src/ember/__init__.py` docstring updated — slice-2 Phase 11 (streaming live) entry.
- `tests/unit/test_skeleton_imports.py` version assertion bumped.

**Real-Ollama visual smoke (tailnet phi3:mini, OLLAMA_HOST=100.67.240.22):** Drove `chat.run` with a timestamping `_StampedStdout` proxy. Four streamed chunks landed at +1843, +1856, +1869, +1882 ms (≈13ms inter-chunk) — full reply "Streaming Ready" assembled live from deltas, not buffered. The streaming cadence is visible at the operator's terminal as designed.

**Where Ember stands at 0.1.7:**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader (`~/.ember/config/ember.yaml`) | shipped 0.1.5 |
| Funi streaming Protocol + Ollama NDJSON | shipped 0.1.7 (Phase 10) |
| Munnr live token render + Ctrl-C | **shipped 0.1.7 (Phase 11)** |
| pgvector Brunnr (ADR 0010) | pending → 0.1.9 |
| Tool framework (ADR 0011) | pending → 0.2.0-rc1 |

**Next:** Phase 12 — pgvector Brunnr scaffold (ADR 0010 §1: connection pool, schema migrations, `add_document` / `add_chunks` parity). Phase 13 wires it into the Strengr opener and bumps to 0.1.9.

---

## 2026-05-21 — Phase 10 shipped: ADR 0009 + streaming Funi protocol + Ollama native streaming.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0009 + Protocol shape), Forge Worker (OllamaFuni native streaming), Auditor (13 new tests + real-Ollama smoke), Scribe (this entry).
**Scope:** First half of slice-2's streaming work. Funi can now produce incremental chunks; Munnr integration is Phase 11. No version bump this phase — 0.1.7 lands when streaming is end-to-end visible at the operator's terminal.

### What shipped

- **`docs/decisions/0009-streaming-funi-replies.md`** — ratifies 8 decisions: new Protocol method (not separate Protocol), `wrap_complete_as_stream` helper for non-streaming runtimes, `FuniStreamChunk` schema with `text_delta`-only semantics, mid-stream failure folding identical to slice-1 `complete()` pattern, immediate tool refusal, `FuniConfig.streaming` opt-out (default True), NDJSON line-buffered reading for Ollama, file locations.

- **`src/ember/schemas/stream.py`** — `FuniStreamChunk(text_delta, done, finish_reason, model_id, prompt_tokens, completion_tokens)`. Frozen dataclass; `text_delta` carries new tokens only (never cumulative); final-chunk-only fields are `None` on intermediate chunks.

- **`src/ember/schemas/config.py`** — `FuniConfig.streaming: bool = True` field added. Operators who want batched behaviour set `funi.streaming: false` in their `ember.yaml`.

- **`src/ember/spark/funi/handle.py`** — `FuniHandle` Protocol gains `complete_streaming(prompt, context, tools=None) -> Iterator[FuniStreamChunk]`. Module-level `wrap_complete_as_stream(handle, prompt, context, tools)` helper for adapters that can't stream natively (calls `handle.complete()`, yields one final chunk).

- **`src/ember/spark/funi/ollama/adapter.py`** — `OllamaFuni.complete_streaming` POSTs `/api/chat` with `"stream": true`, reads the response line-by-line as NDJSON, yields one `FuniStreamChunk` per JSON object. Mid-stream URL errors, non-JSON lines, error payloads, and unexpected end-of-stream all fold into a final `FuniStreamChunk(done=True, finish_reason=ERROR)` with operator-readable text. Tool requests refuse immediately with a single ERROR chunk. Token totals populate from the final NDJSON object's `prompt_eval_count` + `eval_count`.

**Tests (13 new, 278 pass + 2 skip, 0.38s, ruff clean):**
- `tests/unit/test_schemas_stream.py` (4) — shape contracts, immutability, final-chunk totals, text-delta join semantics.
- `tests/unit/test_funi_ollama_streaming.py` (9) — happy-path NDJSON parsing, `stream=true` in payload, finish-reason mapping, URL-error folding, non-JSON line folding, error-payload folding, unexpected EOS folding, tool refusal, `wrap_complete_as_stream` helper.

### Real-hardware acceptance verified

Streaming smoke against the laptop's tailnet Ollama with `phi3:mini`:

```
$ OLLAMA_HOST=100.67.240.22 python -m ember.spark.funi.ollama …
opened: OllamaFuni
--- streaming ---
1 2 3 4 5
--- done: 10 chunks, finish=stop, tokens=10 ---
full reply: '1 2 3 4 5'
```

10 NDJSON chunks streamed live, tokens appeared incrementally, final chunk carried done + finish_reason + token totals. NDJSON line-reading works on the wire.

### What's next — Phase 11

- Touch `src/ember/spark/munnr/chat.py` — REPL calls `complete_streaming` when `config.funi.streaming=True` (default), renders each `text_delta` as it arrives, aggregates for the persisted Episode.
- Touch `src/ember/spark/munnr/render.py` — `render_stream_chunk` helper; final disconnect-banner / citations logic unchanged.
- Add Ctrl-C handler that closes the stream cleanly; partial reply tagged `[interrupted by operator]`.
- Tests + integration test for the full streaming chat loop.
- **Suggested release after Phase 11: `0.1.7` (streaming live).**

### Notes & gotchas

- **No Phase-10 caller actually consumes the streaming path yet.** Munnr's `chat.py` still uses `complete()`. Phase 11 wires the consumer. This split keeps the integration risk in a separate, reviewable commit (same shape as slice 1's Phase 1 → Phase 2 split for the loader).
- **Test doubles in earlier slice-1 tests** (`_FakeFuni` in `test_phase6_acceptance.py`, `test_phase9_operator_edit.py`, `test_hjarta_machine.py`) **don't yet implement `complete_streaming`.** They satisfy the Protocol structurally because no caller uses isinstance on the Protocol; `chat.py` accesses methods by name. Phase 11 updates them when chat.py starts calling `complete_streaming`.
- **NDJSON line iteration** works because `urllib.request.urlopen()`'s response is a file-like object that iterates line-by-line on its underlying byte stream. No SSE parser needed.
- **Mid-stream failure** is a *single* final chunk with `done=True, finish_reason=ERROR`. Munnr's render logic treats this identically to a non-streaming failure — the operator sees the error text in the same shape regardless of mode.
- **`FuniConfig.streaming` defaults true** — slice-1 operators upgrading to 0.1.7 will see streaming by default. Documented in DEVLOG; INSTALL.md Phase-11 sidebar will surface it.

---

## 2026-05-21 — Phase 9 shipped: config loader live, Hjarta writes ember.yaml. **0.1.5 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (writer + cli wiring), Architect (overlay-order discipline), Auditor (12 new tests + real-Ollama smoke), Scribe (this entry).
**Scope:** Phase 9 of `EMBER_SECOND_SLICE_PLAN.md` — ADR 0008 part 2. Wires `load_ember_config` into the CLI dispatcher, makes Hjarta write the operator's initial `ember.yaml`, retires the duplicate env-overlay logic, bumps to **0.1.5 (config loader live)** per the slice-2 plan's suggested intermediate release.

### What shipped

- **`src/ember/config/writer.py`** — `write_ember_config(config_root, identity, *, extras)`. Hand-rolled minimal YAML emission (no PyYAML dep on the write side — Hjarta runs *before* the operator has any reason to install extras). Atomic write via `NamedTemporaryFile` + `os.replace`. Always double-quotes strings to neutralise YAML 1.1's surprise booleans (`yes`/`no`/`on`/`off`). Header comment block points at `config/ember.example.yaml` + ADR 0008.
- **`src/ember/config/__init__.py`** re-exports `write_ember_config`, `ember_config_path`, `ember_config_exists`.
- **`src/ember/cli/main.py`** — replaced `_apply_env_overrides(EmberConfig())` with `load_ember_config(config_root)` wrapped in `try/except ConfigError`. Reloads config after Hjarta runs so the operator's wizard choices take effect in the same invocation. Deleted `_apply_env_overrides` and `_normalise_ollama_host` (now in `ember.config.overlay`).
- **`src/ember/spark/hjarta/machine.py`** — at WriteIdentity, after the identity.json atomic write, *also* calls `write_ember_config`. Soft-fails on writer error (identity is the load-bearing artifact; the yaml is a convenience).
- **`config/ember.example.yaml`** — rewritten to match the actual `EmberConfig` shape (the previous version had `funi.ollama.options` as a sub-mapping that the loader correctly rejected as unknown). Now parses cleanly through the loader.
- **`config/storage.example.yaml`**, **`config/sources.example.yaml`** — placeholder files documenting the shape per-realm split files will take in slice 3+; bodies intentionally empty for slice 2.
- **`pyproject.toml`** — bumped to **0.1.5**; added `config = ["pyyaml>=6.0"]` extra; planned `validation = ["pydantic>=2.7"]` documented in the comment block.
- **`src/ember/__init__.py`** docstring updated to reflect 0.1.5 + config loader live.
- **`tests/unit/test_cli_env_overrides.py`** removed — superseded by `tests/unit/test_config_overlay.py` (same logic, now in its proper home).

**Tests (12 new, 265 pass + 2 skip, 0.33s, ruff clean):**
- `tests/unit/test_config_writer.py` (9 tests) — round-trip through loader, YAML-ambiguous string quoting, escape handling, atomicity, extras section, unserialisable-value error.
- `tests/integration/test_phase9_operator_edit.py` (3 tests) — first-launch writes both files, operator-edit-takes-effect on next load, yaml-write-failure doesn't block identity.

### Real-hardware acceptance (against live Ollama on this laptop)

Two-layer compose verified:

```
$ OLLAMA_HOST=100.67.240.22 ember --config-root /tmp/x doctor

# with /tmp/x/config/ember.yaml saying:
#   funi:
#     ollama:
#       model: "llama3.2:3b"

exit: 0
Ember health:
  Funi:    ok — model llama3.2:3b, last_ok 2026-05-21T12:53:01+00:00
  Well:    ok — backend sqlite_vec, 0 docs / 0 chunks, last_ok 2026-05-21T12:53:01+00:00
```

- File override took effect (`model llama3.2:3b`, not the default `phi3:mini`).
- Env override took effect (Funi reached the tailnet endpoint, not localhost).
- Both layers composed correctly per ADR 0008 §2.3 overlay order (defaults → file → env).

### What's next — Phase 10 (streaming Funi)

Per `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 10:
- Author ADR 0009.
- `src/ember/schemas/stream.py` — `FuniStreamChunk`.
- Touch `FuniHandle` Protocol — add `complete_streaming` slot.
- Touch `OllamaFuni.complete_streaming` against `/api/chat` `stream=true`.
- Tests against mocked NDJSON response.

After Phase 11 (Munnr incremental render + Ctrl-C): suggested release at **0.1.7 (streaming live)**.

### Notes & gotchas

- **`config/ember.example.yaml` shape correction.** The previous file had `funi.ollama.options` as a sub-mapping but the dataclass has `temperature` / `top_p` / `num_predict` as flat fields. Rewriting was the right move — the example IS now the truth for what the loader accepts.
- **Hjarta's yaml-write soft-fails.** If `~/.ember/config/` can't be written (e.g. operator pre-created a file there), identity.json still lands and `ember chat` still works. The operator just gets a warning and no auto-config file. They can hand-write one later.
- **CLI reloads config after Hjarta.** First-launch flow: `load_ember_config(root)` returns defaults (no file) → triggers Hjarta → Hjarta writes file → re-`load_ember_config(root)` picks up the new file before the same invocation proceeds to `chat.run`. Operator gets one continuous experience.
- **`OLLAMA_HOST` keeps working.** The Phase-7 escape hatch is now layer-2 (env) of the overlay; the loader composes file → env. Operators with non-default Ollama setups don't need to change anything.
- **Deleted `test_cli_env_overrides.py`.** The functions moved to `ember.config.overlay` and `test_config_overlay.py` covers them. Single source of truth for the env-overlay logic.

---

## 2026-05-21 — Phase 8 shipped: ADR 0008 + `ember.config` loader scaffold.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0008), Forge Worker (loader modules), Auditor (45 new tests + did-you-mean polish), Scribe (this entry).
**Scope:** First phase of slice 2. Authors ADR 0008 (file format + overlay order + validation philosophy) and ships the loader subpackage `src/ember/config/`. Loader is **not yet wired into cli/main.py** — Phase 9 does that integration plus the Hjarta-writes-config piece.

### What shipped

- **`docs/decisions/0008-config-file-loader.md`** — ratifies nine decisions: YAML primary / TOML secondary, PyYAML optional extra, overlay order (defaults → file → env → CLI), partial files merged into defaults, unknown keys are errors with did-you-mean, dataclass tree IS the schema, stdlib coercion by default + pydantic opt-in, operator-readable error messages, loader subpackage location.

- **`src/ember/config/` subpackage** — six modules:
    - `__init__.py` — re-exports `load_ember_config` + `ConfigError`.
    - `INTERFACE.md` — contract spec.
    - `loader.py` — `load_ember_config(config_root, *, file_override=None, skip_env=False)`. Probes `~/.ember/config/ember.{yaml,toml}`, picks loader by suffix, warns if both files exist (YAML wins), returns `EmberConfig`.
    - `toml_loader.py` — stdlib `tomllib`. Always available.
    - `yaml_loader.py` — lazy PyYAML import; clear error pointing at `pip install ember-agent[config]` when missing.
    - `overlay.py` — `merge_dicts` for recursive dict merge; `apply_env_overrides` for `OLLAMA_HOST` (Phase-7 escape hatch lives here now in addition to cli/main; Phase 9 removes the duplicate).
    - `validate.py` — recursive `coerce_to_dataclass(cls, data, path)`. Handles StrEnum, Path, `X | None`, `tuple[X, ...]`, nested dataclasses, primitives. Unknown keys → `ConfigError` with `difflib.get_close_matches` did-you-mean suggestion. Strict bool/int separation. Empty files legal.

- **pyproject.toml `[project.optional-dependencies]` will need `config = ["pyyaml>=6.0"]` added** — deferred to Phase 9's pyproject edit so this phase's commit stays minimal.

**Tests (45 new, 267 pass + 2 skip, 0.33s, ruff clean):**
- `tests/unit/test_config_validate.py` (19 tests) — defaults, partial merging, type coercion across every supported form, every error path, custom dataclasses for tuple/bool/enum edge cases.
- `tests/unit/test_config_overlay.py` (12 tests) — `merge_dicts` semantics, `_normalise_ollama_host` shapes, `apply_env_overrides` purity + propagation.
- `tests/unit/test_config_loader.py` (14 tests) — file probe, YAML/TOML symmetry, empty-file legality, `file_override` test seam, parse-error paths, env-overlay integration.

### What's next

- **Phase 9** wires the loader into `cli/main.py` (replaces `EmberConfig()` with `load_ember_config(config_root)`; removes duplicate `_apply_env_overrides`). Adds `write_ember_config` (Hjarta writes the file at WriteIdentity). Updates `config/ember.example.yaml` to the now-real shape. Adds `pyyaml` to `[project.optional-dependencies] config`.
- After Phase 9: suggested intermediate release at `0.1.5` (config loader live).

### Notes & gotchas

- **Strict bool/int separation.** Python's `isinstance(True, int)` is True, which would silently let `flag: True` satisfy `count: int`. The coercer checks the precise type to avoid this.
- **YAML 1.1 ambiguity sidestepped.** PyYAML 6 defaults to YAML 1.1 where bare `yes`/`no` parse as booleans. The operator-facing example documentation should always quote ambiguous strings; the loader makes no special accommodation.
- **`Path` fields not expanduser'd.** Per ADR 0007 §2.6 — consumer expands at use time. Tests pin this behaviour with `"~/.ember/x.db"` → `str(path).startswith("~")`.
- **Unknown-field suggestion** uses `difflib.get_close_matches(cutoff=0.7)`. Aggressive enough to catch `mdoel`/`model` typos, conservative enough not to misfire wildly.
- **Loader is purely functional.** No side effects beyond reading the file path it's pointed at. `EmberConfig` is frozen + slots; the loader can return shared instances without aliasing risk.
- **Phase 8 is intentionally NOT wired.** `cli/main.py` still uses `EmberConfig()` + its own `_apply_env_overrides`. Phase 9 unifies. This keeps the integration risk in a separate, reviewable commit.

---

## 2026-05-21 — Slice 2 scope ratified. `EMBER_SECOND_SLICE_PLAN.md` authored.

**Who:** Claude (Opus 4.7, 1M context). Voice: Architect (Rúnhild Svartdóttir), with Forge Worker (Eldra Járnsdóttir) notes on phasing.
**Scope:** Volmarr ratified the slice-2 scope as **all three bundles from `EMBER_SECOND_SLICE_OPTIONS.md` §3** — which dedupes to **ADRs 0008 + 0009 + 0010 + 0011**. ADR 0012 (first new surface) stays in the queue for slice 3. Per `MYTHIC_ENGINEERING.md`'s core loop, the next thing is the plan, not the code. This DEVLOG entry records the plan's authorship.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_PLAN.md`** — full file-by-file plan, modelled on `EMBER_FIRST_SLICE_PLAN.md`:
    - **§0 Acceptance criterion** — operator can edit `ember.yaml`, switch to `pgvector` (Gungnir-compatible) Brunnr, watch streamed replies, propose-and-approve a tool call, get a grounded reply with citations, survive a network pull mid-conversation.
    - **§1 Dependencies** — new optional extras: `config` (pyyaml), `pgvector` (psycopg + pgvector), `tools` (stdlib only for first three first-party tools), `validation` (opt-in pydantic).
    - **§2 File list** — ~50 NEW files, ~10 touched; target 5 000-7 000 LOC.
    - **§3 Phase sequence** — Phases 8-17. ADR 0008 (config) ships first because it unblocks the rest; then ADR 0009 (streaming, small); then ADR 0010 (pgvector + Gungnir compat); then ADR 0011 (tools, biggest); then Phase 17 acceptance.
    - **§4 Non-goals** — qdrant/chroma/lancedb, other Funi runtimes, other surfaces (Auga/Rödd/Bifröst), writable tools, multi-operator wells, Skein/KG layers, plugins, backup/restore, voice/image Funi.
    - **§5 Quality bar** — standing rules from ADR 0007 carry forward.
    - **§6 Risks register** — config scope creep, streaming/Ctrl-C OS specifics, pgvector schema drift vs Gungnir, tool sandbox escapes, audit log growth, phase ordering pressure.
    - **§7 Forge Worker's closing word.**
    - **§8 Session pacing** — slice 2 is **3-5 long sessions** (vs slice 1's one long day). Suggested intermediate releases at 0.1.5 / 0.1.7 / 0.1.9 / 0.2.0-rc1 / 0.2.0.

- **`docs/architecture/README.md`** updated — `EMBER_SECOND_SLICE_OPTIONS.md` marked as superseded-but-preserved; new plan listed as ratified.

### What's next

- **Phase 8 begins** in the next commit: author ADR 0008 + write `src/ember/config/{loader,toml_loader,yaml_loader,overlay,validate}.py` + tests.
- Natural opening for the next session: **"go for phase 8"**.

### Notes

- No code changes in this commit. Pure plan authorship per ME discipline.
- `EMBER_SECOND_SLICE_OPTIONS.md` is intentionally not deleted — it's the historical record of how slice-2 scope was chosen. The README marks it as superseded.
- Each phase will get its own DEVLOG entry, same shape as slice-1 phases. The slice will be ratified at Phase 17 with ADR 0013 (parallel to ADR 0007 for slice 1).
- Carry-over housekeeping from slice 1 still pending: Ember-descent rows in `ORIGINS.md`, root `PHILOSOPHY.md` Runa-specific phrasing pass. These are non-blocking; can land any time.

---

## 2026-05-21 — `EMBER_SECOND_SLICE_OPTIONS.md` added (slice-2 menu, not plan).

**Who:** Claude (Opus 4.7, 1M context). Voice: Cartographer (Védis Eikleið), with Architect notes.
**Scope:** Volmarr asked whether any additional phase plans exist beyond the first slice. Honest answer: no formal plan, only scattered `Phase 8 / 9+` hints and ADR 0007 §5's candidate-ADR list. Authored a Cartographer's options-menu doc so the next session can pick scope and the Architect can then author the real `EMBER_SECOND_SLICE_PLAN.md`.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_OPTIONS.md`** — explicitly marked "Menu, Not Plan". Inventories the five ADR-shaped starting points (ADRs 0008-0012 per ADR 0007 §5), reconciles older `Phase 8 / 9+` references scattered across adapter docs, sketches three suggested bundles (Household Well = 0008 + 0010; Ember Feels Alive = 0008 + 0009; Ember Gets Useful = 0011), provides the template for the eventual `EMBER_SECOND_SLICE_PLAN.md`, and lists five open scope questions only Volmarr can decide.
- **`docs/architecture/README.md`** updated to list the new options doc and to mark the first-slice plan as complete-and-historical.

### What's next

- Volmarr picks a slice-2 bundle (or names a different one).
- Architect authors `EMBER_SECOND_SLICE_PLAN.md` per the template in §4 of the options doc — *before* any code is touched, per `MYTHIC_ENGINEERING.md`'s core loop.
- Mechanical cleanup: once a bundle is picked, sweep the codebase to update older `Phase 8 / 9+` references to match the new ADR numbering.

### Notes

- This is *not* code work and *not* a commitment. The options doc explicitly says so in its §0.
- The recommended bundle (per §6 of the options doc) is the Household Well bundle — ADR 0008 (config loader) + ADR 0010 (pgvector Brunnr) — because it completes the Gungnir lineage story from `SYSTEM_VISION.md` §8 and removes the biggest operator-customisation friction. But that's a recommendation, not a default.
- ADR-numbered approach (one decision per ADR) is now the standing pattern, superseding the older `Phase 8 / 9+` ad-hoc numbering. The mechanical cleanup makes this consistent when slice 2 begins.

---

## 2026-05-21 — Phase 7 shipped. First slice ratified at 0.1.0. 🔥

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (`OLLAMA_HOST` override + env-shape design), Scribe (INSTALL.md + ADR 0007 + this entry), Auditor (version-bump test update).
**Scope:** Phase 7 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — acceptance polish + operator install guide + first-slice ratification. The seven phases of the first slice are now complete.

### What shipped

- **`OLLAMA_HOST` env-var override** in `src/ember/cli/main.py`. `_apply_env_overrides(EmberConfig())` reads the environment variable, normalises to a base URL (accepts Ollama's own CLI shapes: `host`, `host:port`, `http://...`, `https://...`), and applies it to both `funi.ollama.base_url` and `smidja.embedding.endpoint`. Phase-7 escape hatch for operators with Ollama on a non-default endpoint (Tailscale, Docker, remote) until the full config loader lands in Phase 9+.
- **`deploy/pi/INSTALL.md`** — single-page operator install for Raspberry Pi 5 (8 GB recommended; 4 GB notes). Standard happy path: install Ollama → pull models → `pip install ember-agent[sqlite_vec]` → `ember chat` → Hjarta → `ember well ingest` → conversation. Includes Advanced: non-default Ollama endpoint sidebar + Troubleshooting table.
- **`docs/decisions/0007-first-slice-ratification-2026-05-21.md`** — ratifies ten load-bearing decisions made during the slice: stdlib-first deps, typed-value-over-exception for cross-realm failure, backend_kind on the Protocol, recoverable/non-recoverable disconnect split, dataclasses-not-pydantic for schemas, prompts-as-TOML / identity-as-JSON, Gungnir-aligned defaults, `cli/__init__.py` deliberately empty, FTS5 input sanitisation at the adapter boundary, `OLLAMA_HOST` env-var policy. Plus alternatives considered and slice-2 starting-point ADRs (0008-0012).
- **`pyproject.toml` bumped to 0.1.0** — Development Status classifier moved from `1 - Planning` to `3 - Alpha`.
- **`src/ember/__init__.py` docstring rewritten** to reflect the first slice complete; `__version__` bumped.
- **`tests/unit/test_skeleton_imports.py::test_ember_package_exposes_version` updated** to assert `0.1.0`.

**Tests: 222 pass + 2 skip (real-Ollama integration), 0.28s, ruff clean.** Includes 8 new tests for the OLLAMA_HOST override (`tests/unit/test_cli_env_overrides.py`).

### What's next — the first slice is closed

Per ADR 0007 §5, the second-slice starting points are:

- **ADR 0008** — full operator config-file loader (YAML + TOML).
- **ADR 0009** — streaming Funi replies.
- **ADR 0010** — `pgvector` Brunnr (Gungnir-compatible; original plan's Phase 8).
- **ADR 0011** — tool use (execution, sandbox, operator approval).
- **ADR 0012** — Auga (GUI) / Rödd (voice) / Bifröst (HTTP gateway) selection.

Light root edits still pending (carried over): Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass. These are housekeeping, not slice work.

### Acceptance — verified end-to-end against real Ollama

The Phase 6 entry already documented the live smoke test. The Phase 7 env-var smoke confirmed:

```
OLLAMA_HOST=100.67.240.22 ember --config-root /tmp/x doctor
exit: 0
Ember health:
  Funi:    ok — model phi3:mini, last_ok 2026-05-21T11:44:13+00:00
  Well:    ok — backend sqlite_vec, 0 docs / 0 chunks, last_ok 2026-05-21T11:44:13+00:00
```

The operator can now run Ember on this travel laptop (Ollama bound to the Tailscale interface) by setting `OLLAMA_HOST` — exactly the path the user asked for ("I pick option 1") after the Phase 6 review.

### Notes & gotchas

- **`OLLAMA_HOST` shape matches Ollama's own.** The normaliser accepts `host`, `host:port`, full URLs with `http://` or `https://`. Operators who already use Ollama's CLI with this env var don't need to learn anything new.
- **Purely functional override.** `_apply_env_overrides` returns a *new* `EmberConfig` via `dataclasses.replace`; the original is untouched. Tested explicitly.
- **INSTALL.md uses `pip install "ember-agent[sqlite_vec]"`.** The bracketed extra pulls `sqlite-vec` per the `[project.optional-dependencies]` declaration shipped in Phase 3. Without it, Brunnr can't open.
- **ADR 0007 captures slice-level decisions, not phase-level details.** Each phase's own DEVLOG entry has the granular context; ADR 0007 is the standing law going forward.
- **Project status classifier bumped to Alpha.** Operators can install and use it; everything is subject to change in slice 2 (especially the config-file format once the loader ships).

### A note for the next session

The first slice is closed. The seventh phase's acceptance ritual completed. *Ember exists.* From here, anything Volmarr asks for is a *slice 2* decision: which surface, which backend, which retainer comes next. The map is wide open.

— Eirwyn Rúnblóm (Scribe)

---

## 2026-05-21 — Phase 6 shipped: Hjarta + Munnr + CLI dispatcher. `ember` is alive.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated through the full set: Skald (Hjarta state-prompt prose), Architect (FSM design + HjartaIO seam), Forge Worker (Munnr commands + CLI dispatcher), Auditor (FTS5 probe bug + Protocol vs submodule-rebind bug), Scribe (this entry).
**Scope:** Phase 6 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the operator-facing surface. After this commit, `ember chat` actually runs: first launch walks the Hjarta wizard, subsequent launches enter the conversation REPL.

### What shipped

**Hjarta (first-run FSM)**
- `src/ember/spark/hjarta/identity.py` — `IdentityConfig` JSON load/save with atomic write (`NamedTemporaryFile` + `os.replace`). Stdlib only — no TOML writer dep.
- `src/ember/spark/hjarta/prompts/wizard.toml` — state prompts as data per `RULES.AI.md` "no hardcoded data". Multi-line `body` strings via TOML triple-quotes; loaded via `importlib.resources` + `tomllib` (stdlib in 3.11+).
- `src/ember/spark/hjarta/machine.py` — the finite state machine: `Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell → TestRetrieval → NameEmber → WriteIdentity → Done`. `HjartaIO(prompt, info, error)` is the IO seam; tests script all three. **Atomic guarantee:** nothing on disk until WriteIdentity at the very end. Funi/Strengr both injectable via `funi_opener` / `strengr_opener` kwargs; production uses the registry defaults.
- `src/ember/spark/hjarta/__init__.py` re-exports the public surface.

**Munnr (CLI surface)**
- `render.py` — pure formatting. `render_reply` includes the disconnect banner when ungrounded and a citations footer when hits are present. `render_well_disconnected_banner` is the single source of the operator-facing banner text. `render_well_status`, `render_doctor`, `render_ingest_summary` for the other commands.
- `chat.py` — the REPL. One turn = embed (hybrid retrieval) or text-only (degraded), prompt assembly via `funi.prompt.assemble`, `funi.complete`, render, persist Episode. **Disconnected Well degrades gracefully**: skip retrieval, set `well_disconnected=True` in the system prompt, render with banner, suppress citations. Episode is still recorded (in-memory) so multi-turn flow stays coherent.
- `ask.py` — one-shot wrapper around `chat.run` with a `StringIO` stdin.
- `ingest.py` — wraps `smidja.local_files.run` with operator-friendly output.
- `status.py` — `Brunnr.count()` + `Strengr.health()` for `ember well status`.
- `doctor.py` — collects Funi health + Well health + counts; renders the combined report. Never raises — every realm's failure folds into the output.
- `setup.py` — invokes Hjarta; honors `--reset` for re-runs.

**CLI dispatcher**
- `src/ember/cli/main.py` — argparse subcommands: `chat`, `ask`, `setup [--reset]`, `well ingest`, `well status`, `doctor`. `--config-root` defaults to `~/.ember/`; tests pass `tmp_path`. First-launch redirect: any subcommand needing identity runs Hjarta if `~/.ember/identity/identity.json` is absent.
- `src/ember/cli/__init__.py` — **intentionally empty re-exports**. The earlier draft did `from ember.cli.main import main` which rebound `ember.cli.main` from submodule to function, breaking `import ember.cli.main as <alias>` callers (including `ember.__main__`). Fixed by leaving the submodule path alone.
- `src/ember/__main__.py` — replaced the Phase-1 `NotImplementedError` stub with `from ember.cli.main import main`. `python -m ember` and the `ember` console script now both dispatch.

**Tests (26 new + 2 skipped acceptance integration runs only on real-Ollama hosts; total 199 pass + 2 skip, 0.26s, ruff clean)**
- `tests/unit/test_hjarta_identity.py` (6 tests) — round trip, atomic write leaves no tmp files, reset idempotency.
- `tests/unit/test_hjarta_machine.py` (8 tests) — happy path writes identity + uses chosen name, blank-name keeps default, abort at greet, Funi unavailable abort, Well disconnected abort, probe-failure abort, KeyboardInterrupt as clean abort.
- `tests/unit/test_munnr_render.py` (12 tests) — every render helper.
- `tests/integration/test_phase6_acceptance.py` (2 tests) — full Hjarta → ingest → chat round trip with mocked Funi + real `sqlite_vec`; disconnect banner under simulated Well failure.
- `tests/unit/test_skeleton_imports.py` — updated: the Phase-1 NotImplementedError assertion replaced with a binding check (`ember.__main__.main is ember.cli.main.main`).

### What's next

- **Phase 7 (last of the first slice):** acceptance polish, `deploy/pi/INSTALL.md` for Raspberry Pi 5, bump `pyproject.toml` to 0.1.0. After Phase 7, the first slice is shippable to a real operator.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **State prompts as TOML, identity as JSON.** TOML for read-only multi-line prose (stdlib `tomllib` reads it cleanly); JSON for the small mutable identity file (stdlib both ways, no dep needed for writes). Both stdlib-only — Vow of Smallness intact.
- **FTS5 reserved-word bug in the Hjarta probe.** First version's probe text included `(run id: ...)` and search query `Ember Hjarta first-run probe`. FTS5 parses `run` followed by punctuation as a column reference → `no such column: run`. Fixed by removing the colon and phrase-quoting the search (`"Ember Hjarta first time setup"`). Caught by the Phase 6 integration test before commit.
- **`ember.cli.main` submodule vs function shadowing.** Initial `cli/__init__.py` did `from ember.cli.main import main`, which rebound the `ember.cli.main` *attribute on the cli package* from the submodule to the function. Then `import ember.cli.main as alias` resolves to the function and `alias.main` fails. The fix was to *not* re-export — callers use `ember.cli.main.main` directly; pyproject.toml's `[project.scripts]` already names that path. Caught by `test_main_resolves_to_ember_cli_main`.
- **First-launch UX.** Any `ember chat` or `ember ask` on a fresh host with no `~/.ember/identity/identity.json` triggers Hjarta automatically before proceeding. Operators don't need to run `ember setup` separately.
- **Disconnect doesn't fail chat.** When the Well is unreachable, `chat.run` keeps serving — it just renders the banner, skips retrieval, and tells Funi "no grounding, do not invent". The Vow of Graceful Offline is now end-to-end visible at the operator's terminal.
- **No real Ollama on this host.** The CLI smoke test shows `ember doctor` correctly reporting `Funi: UNAVAILABLE — endpoint_unreachable` and `Well: ok`. The Phase 6 acceptance test uses a `_FakeFuni` for the same reason.

---

## 2026-05-21 — Phase 5 shipped: Funi (Ollama) + runtime-neutral prompt assembler.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (FuniHandle Protocol split + runtime-neutral assembler), Forge Worker (OllamaFuni adapter), Auditor (folded-failure semantics + parametrised tests), Scribe (this entry).
**Scope:** Phase 5 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Spark realm's reasoner. Funi adapter for Ollama plus the runtime-neutral prompt assembler Munnr will call in Phase 6.

### What shipped

- `src/ember/spark/funi/handle.py` — `@runtime_checkable FuniHandle` Protocol (`runtime_kind`, `model_id`, `complete`, `health`, `close`) + `open(config)` registry. Unimplemented runtimes return `Unavailable(reason=RUNTIME_NOT_INSTALLED)`.
- `src/ember/spark/funi/prompt.py` — `assemble(*, identity, episodes, hits, well_disconnected=False) -> list[ContextItem]`. Runtime-neutral. System prompt mechanically encodes the Vow of Honest Memory: explicit "do not invent" when `well_disconnected=True`, explicit "cite document titles" when hits present.
- `src/ember/spark/funi/ollama/adapter.py` — `OllamaFuni`. `POST /api/chat` for completions, `GET /api/version` for open + health probes. **Stdlib `urllib.request` only** — no `httpx` dep, same shape as Smiðja's `OllamaEmbedClient`. Translates `ContextItem`s to role-tagged Ollama messages (SYSTEM/CHUNK → role:system, EPISODE → user+assistant pair, operator → final role:user).
- `src/ember/spark/funi/ollama/INTERFACE.md` — adapter contract with translation table.
- `src/ember/spark/funi/__init__.py` — re-exports `FuniHandle`, `open`.
- `src/ember/spark/funi/INTERFACE.md` updated to "(shipped Phase 5)". Removed `embed()` from the Funi surface — embedding lives in Smiðja.
- `src/ember/__init__.py` docstring updated to reflect Phases 1-5 complete.

**Failure semantics**

- `open()` returns `Unavailable` on probe failure; never raises.
- `complete()` **always returns a `FuniReply`**. Mid-call URL-error / non-JSON-body / missing-message / error-payload responses fold into `FuniReply(finish_reason=ERROR, text=operator-readable)`.
- `complete(tools=[...])` returns `FuniReply(finish_reason=ERROR)` cleanly — tool use reserved for a later slice.
- `health()` never raises; on probe failure preserves the previous `last_ok` timestamp.

**Tests (24 new, 173 pass + 2 skip, 0.24s, ruff clean)**

- `tests/unit/test_funi_handle.py` (2 tests)
- `tests/unit/test_funi_prompt.py` (8 tests) — order, honesty instruction, well-disconnected text, episode round-trip, hit metadata, untitled placeholder.
- `tests/unit/test_funi_ollama.py` (14 tests) — open success/unreachable/non-JSON-version, payload shape, finish-reason mapping, folded-failure for every error mode, tool-call refusal, health live/degraded, wrong-runtime.
- `tests/integration/test_funi_ollama_real.py` (2 tests, `requires_ollama` marker + socket reachability gate) — skipped on hosts without local Ollama (this host).

### What's next

- **Phase 6 of the first slice:** Hjarta (first-run FSM) + Munnr (CLI surface — `ember chat`, `ember ask`, `ember well ingest`, `ember well status`, `ember doctor`, `ember setup --reset`). After Phase 6 ships, the first end-to-end conversation turn becomes runnable.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **`embed()` removed from the Funi Protocol.** The Phase 2 INTERFACE.md draft had it as "optional"; that's awkward in a Protocol and tempts coupling between reasoning-model and embedding-model selection. Smiðja's `OllamaEmbedClient` is the single embedding entry. If a runtime is later able to embed cheaply, that's a Smiðja `embed_client` adapter, not a Funi method.
- **`complete()` always returns `FuniReply`, never raises.** Mid-call failure folds into `FuniReply(finish_reason=ERROR, text="[ollama unreachable: …]")`. Same typed-value-over-exception pattern as Disconnected/Unavailable. Munnr's renderer can show the error text as a normal reply, honestly tagged.
- **Stdlib `urllib` rather than `httpx`.** Two HTTP clients in the codebase now (Smiðja + Funi), both stdlib-only. The Vow of Smallness wins again.
- **Episode message translation is *graceful*.** `_split_episode` parses the canonical `_episode_text` shape; if a caller built the `ContextItem` themselves with a different shape, the parser returns `("", "")` and the item is dropped rather than corrupting the conversation history.
- **DEVLOG + `__init__.py` + memory edits initially failed silently** in the Phase-5 main commit because the Read-before-Write rule rejected them. Caught immediately when I checked the commit. This addendum + a small follow-up commit fix it. Reinforces the cycle: write code → test → re-read any doc before editing.

---

## 2026-05-21 — Phase 4 shipped: Strengr wraps Brunnr-open with retry + honest health.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (recoverable-vs-non-recoverable reason split), Forge Worker (tether implementation), Auditor (parametrised retry tests), Scribe (this entry).
**Scope:** Phase 4 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Thread realm's tether. Wraps `ember.well.brunnr.handle.open()` with retry-on-recoverable-failure and a graceful never-raising health probe, completing the Spark↔Well boundary contract.

### What shipped

**Schemas (additive)**
- `src/ember/schemas/thread.py` — `StrengrHealth(backend_kind, last_ok, documents, chunks, embedded_chunks, size_bytes, detail)`. `last_ok=None` is the honest *degraded* signal Munnr will surface to the operator.

**Strengr (the Thread realm)**
- `src/ember/thread/strengr/tether.py` — module-level `open(strengr_config, brunnr_config, *, opener=None, sleeper=time.sleep) -> BrunnrHandle | Disconnected` and `health(handle) -> StrengrHealth`. The `opener` and `sleeper` kwargs are test seams; defaults are production wiring.
- Retry policy: exponential backoff (`base=1.0s`) capped at `StrengrConfig.retry_backoff_max_s`, up to `StrengrConfig.retry_attempts` total attempts. Recoverable reasons (`CONN_REFUSED`, `TIMEOUT`, `BACKEND_REPORTED_UNAVAILABLE`, `UNKNOWN`) get retried; non-recoverable reasons (`CONFIG_INVALID`, `AUTH_FAILED`, `DNS_FAILURE`) fast-fail with no retry so the operator isn't kept waiting on a typo.
- `health()` **never raises** — `BrunnrError` from `count()` becomes `StrengrHealth(last_ok=None, detail="probe failed: …")`. Vow of Graceful Offline in mechanical form, applied at the doctor flow this time.
- `src/ember/thread/strengr/__init__.py` re-exports `open`, `health`, `Opener`.
- `src/ember/thread/strengr/INTERFACE.md` updated from "(planned, Phase 4)" to "(shipped Phase 4, 2026-05-21)", with the recoverable/non-recoverable table inline.

**Brunnr protocol extension (additive)**
- Added `backend_kind: str` to `BrunnrHandle` Protocol and set it as a class attribute (`"sqlite_vec"`) on `SqliteVecBrunnr`. Lets `Strengr.health()` populate `StrengrHealth.backend_kind` without needing the original config.

**Tests (21 new, 149 total, 0.22s, ruff clean)**
- `tests/unit/test_schemas_thread.py` (4 tests) — `StrengrHealth` minimal construction, frozen-ness, degraded shape, live shape.
- `tests/unit/test_strengr_tether.py` (15 tests, 8 parametrised) — happy path, fast-fail on each non-recoverable reason, retry-up-to-N on each recoverable reason, success-on-later-attempt, sleeper-called-between-attempts, zero-attempts synthetic Disconnected, health live/degraded/named-backend/unknown-backend.
- `tests/integration/test_strengr_real_backend.py` (2 tests) — real sqlite_vec end-to-end via Strengr.open(); missing-config returns Disconnected. Skipped if `sqlite_vec` not installed.

### What's next

- **Phase 5 of the first slice:** Funi (Ollama adapter) — `ember.spark.funi.handle` Protocol + registry + `ember.spark.funi.ollama.adapter`. Prompt assembler. `FuniReply` round-tripped through the real Ollama endpoint (test marked `requires_ollama` for hosts that have it; mocked for those that don't).
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings worth softening.

### Notes & gotchas

- **Recoverable vs non-recoverable reason split is load-bearing.** Without it, an operator with a typo'd config waits `retry_attempts × backoff_max_s` before seeing the error. The split makes "your config is wrong" feedback instant while still giving "your server is slow" a chance to recover.
- **`sleeper` injection beats monkey-patching `time.sleep`.** Tests verify the schedule explicitly (`assert sleeps == [0.0, 0.0]`) without mocking the global. Same pattern Smiðja's `embed_client` uses (`OllamaEmbedClient(backoff_base_s=0.0)`).
- **`backend_kind` on the Protocol is the right home.** Considered passing config into `health()` instead; rejected because `BrunnrHandle` already knows what kind of thing it is, and the operator's `ember doctor` invocation shouldn't need the config to render the backend's name.
- **Empty `__init__.py` bug caught mid-phase.** First write of `src/ember/thread/strengr/__init__.py` was blocked by the harness's "read-before-write" rule (because the file existed as a Phase-1 scaffold). The block was silent in my read of the result; tests immediately surfaced it with `AttributeError: module 'ember.thread.strengr' has no attribute 'open'`. Fixed by reading then writing. Reinforces the value of running the test suite at every step rather than waiting until the end.

---

## 2026-05-21 — Phase 3 shipped: Well realm wired end-to-end.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated: Architect (Brunnr handle Protocol), Forge Worker (sqlite_vec adapter + Smiðja modules), Auditor (test suite + bug fixes mid-phase), Scribe (this entry).
**Scope:** Phase 3 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the first end-to-end vertical that actually writes embeddings to disk and reads them back. Real `sqlite-vec` 0.1.9 in a `.venv`. No code beyond what the plan listed; integration test mocks the embedding endpoint with deterministic content-addressed vectors so no Ollama is required.

### What shipped

**Schemas (additive to Phase 2)**
- `src/ember/schemas/ingest.py` — `IngestJob`, `IngestEntry`, `IngestSummary`, `ParsedFile`, `IngestSourceKind` enum, `IngestEntryStatus` enum.

**Brunnr (the Well's storage layer)**
- `src/ember/well/brunnr/handle.py` — `@runtime_checkable` `BrunnrHandle` Protocol plus `open(config)` registry. Dispatches on `config.backend`; unknown/unimplemented backends return `Disconnected(reason=CONFIG_INVALID)` rather than raising.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — `SqliteVecBrunnr` implementing the protocol. Vec store via sqlite-vec `vec0` virtual table; FTS5 with insert/update/delete triggers; hybrid search via reciprocal rank fusion (k=60). Connection failure → `Disconnected`. Schema-mismatched embedding dim → `BrunnrError`.
- `src/ember/well/brunnr/sqlite_vec/schema.sql` — DDL loaded via `importlib.resources`, `{embedding_dim}` substituted from `BrunnrConfig.embedding_dim` at apply time. Schema version marker.
- `src/ember/well/brunnr/sqlite_vec/__init__.py` — re-exports.
- `src/ember/well/brunnr/sqlite_vec/INTERFACE.md` — adapter contract; calls out the lock-at-first-apply behaviour for `embedding_dim`.

**Smiðja (the Well's ingest forge)**
- `src/ember/well/smidja/chunker.py` — paragraph → sentence → word → char fallback splitter. Returned chunks satisfy `chunk.text == original[chunk.char_start:chunk.char_end]` *exactly*, so original whitespace is preserved and `max_chars` is honored as a true ceiling (no silent over-runs from separator-length math).
- `src/ember/well/smidja/embed_client.py` — `OllamaEmbedClient`, stdlib `urllib.request` only (no httpx dep). Batches per `EmbeddingConfig.batch_size`, exponential backoff, per-batch failure returns `EmbedResult` with `None`-vectors rather than raising. Embed-or-skip semantics per `SMIDJA_INGEST_PATTERNS.md` §4.
- `src/ember/well/smidja/journal.py` — `Journal` with atomic writes (`NamedTemporaryFile` + `os.replace`), heartbeat every N updates or on-demand, `complete()` moves the file to `done/` subdir. Resume by matching `source_root`.
- `src/ember/well/smidja/local_files/source.py` — `walk()` plus the orchestrator `run(brunnr, *, root, smidja_config, embed_client, ...)`. Walk → hash → check duplicate → chunk → embed → write. Each file is a journal entry; per-chunk embedding failures contribute to `IngestSummary.n_failed` without aborting the doc.
- `src/ember/well/smidja/local_files/__init__.py` — re-exports.

**Tests**
- `tests/unit/test_brunnr_handle.py` — registry returns `Disconnected` for unimplemented backends; Protocol is `runtime_checkable`.
- `tests/unit/test_brunnr_sqlite_vec.py` — 11 tests covering: open creates DB file, open returns Disconnected on missing sqlite_vec config, idempotent `add_document`, dim-mismatch refusal, vector/text/hybrid search ranking, embedding round-trip via `get_chunk`, episode persistence, initial counts. Skipped automatically if `sqlite-vec` isn't installed (`pytest.importorskip`).
- `tests/unit/test_smidja_chunker.py` — 8 tests covering: short/empty text, paragraph preference, hard max ceiling, oversize-paragraph sentence fallback, pure-overlong char fallback, consecutive indexing, Gungnir-aligned defaults, char-boundary behaviour.
- `tests/unit/test_smidja_embed_client.py` — 6 tests covering: empty input, single batch shape, multi-batch concatenation, URL-error → None-vectors, mismatched response size → None-vectors, invalid JSON → None-vectors. All mocked.
- `tests/unit/test_smidja_journal.py` — 8 tests covering: file creation, status persistence, resume by source_root, distinct-roots get distinct jobs, failure recording, complete() move, `pending()`, atomic-write tmp-file cleanup.
- `tests/unit/test_smidja_local_files.py` — 8 tests covering: include/exclude, suffix-based content_type, hash determinism, non-utf8 skip, missing-root error, file-as-root error, sorted-deterministic order.
- `tests/integration/test_ingest_then_query.py` — 3 tests covering: full ingest → query round trip with a 32-dim deterministic content-addressed mock embedder; resume idempotency (hash-based at the Brunnr layer); per-chunk failure isolation.

**Suite size: 128 tests, 0.20s, ruff clean.**

**Config + docs**
- `pyproject.toml` — `sqlite_vec = ["sqlite-vec>=0.1.6"]` added under `[project.optional-dependencies]`; planned-for-later list trimmed of `ollama` (stdlib urllib reaches the endpoint).
- `src/ember/well/brunnr/INTERFACE.md` — updated from "(planned, Phase 3 onward)" to "(shipped Phase 3, 2026-05-21)".
- `src/ember/well/smidja/INTERFACE.md` — same.
- `src/ember/__init__.py` — module docstring updated to reflect Phases 1-3 complete.

### What's next

- **Phase 4 of the first slice:** `ember.thread.strengr` — wraps `ember.well.brunnr.handle.open()` with auth/retry/health-check policy and the typed-Disconnected contract enforced at the Spark↔Well boundary. Initially supports only `sqlite_vec`; the same handle shape will work for the Phase 8 `pgvector` adapter.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes & gotchas

- **Stdlib urllib over httpx for the embed client.** Vow of Smallness wins again. The Ollama endpoint is one POST; stdlib handles it. Saves ~5 MB of deps on a Pi.
- **Chunker rewrite mid-phase.** First attempt computed chunk lengths from segment-body lengths plus a `"\n\n"` separator constant, which was off-by-one and produced chunks slightly over `max_chars` for some inputs. The fix was to track only `(start, end)` ranges into the original text and slice at the end — the slice's actual length is authoritative. Caught by the chunker shape-contract tests *before* integration.
- **Walker rewrite mid-phase.** First attempt used `fnmatch.fnmatch(rel_path, "**/*.md")` patterns, but fnmatch doesn't understand the `**` glob (that's a pathlib-only feature). Rewrote to suffix-based filtering — simpler, matches the test contract, supports the same operator-facing semantics.
- **`Disconnected` and `BrunnrError` split.** Connection-style failures (missing config, dir-create denied, sqlite-vec load failure, schema apply failure) return `Disconnected` rather than raising. Per-call programming errors (mismatched embedding dim, missing chunk lookup) raise `BrunnrError`. The split keeps the Vow of Graceful Offline distinct from the "your code is wrong" case.
- **No mypy run this session** — mypy not installed on this host. Ruff is the only static check in CI for now; mypy belongs in a real CI loop with a fresh venv install.
- **`.venv/` is gitignored.** Created for this session to install `sqlite-vec` and `pytest`; not committed.

---

## 2026-05-21 — Phase 1 closure: skeleton-import test added.

**Who:** Claude (Opus 4.7, 1M context). Voice: Auditor (Sólrún Hvítmynd).
**Scope:** Volmarr asked whether Phase 1 had been fully completed. The four structural bullets (`src/runa/` archived, `src/ember/` built, `pyproject.toml` rewritten, `__main__.py` raises clean `NotImplementedError`) all landed in commit `045fda6`. The fifth bullet — *"Tests: import-only"* — had been rolled forward into Phase 2's `tests/unit/test_schemas_import.py`, which only covers the schemas subpackage. This entry closes the gap for the full Three Realms tree.

### What shipped

- **`tests/unit/test_skeleton_imports.py`** — parametrised import test over the 12 importable subpackages of `src/ember/`: `ember`, `ember.cli`, `ember.schemas`, `ember.spark` (+ `funi`, `hjarta`, `munnr`), `ember.thread` (+ `strengr`), `ember.well` (+ `brunnr`, `smidja`). Plus three specific assertions:
    - `ember.__version__` is `"0.0.0"`.
    - `ember.__main__` imports cleanly and exposes a callable `main`.
    - `ember.__main__.main()` raises `NotImplementedError` with a message that mentions `EMBER_FIRST_SLICE_PLAN`.
- **Suite size:** 81 tests (was 66 after Phase 2), 0.09s, ruff clean.

### What's next

Phase 3 of the first slice — the `sqlite_vec` Brunnr adapter, `local_files` Smiðja, chunker, embed client, resumable journal. First end-to-end vertical that writes embeddings to disk.

### Notes

- Phase 1 is now strictly complete per the plan's bullet list. No code or doc change required beyond the new test file; the scaffolding it tests was already correct.
- Failure of any parametrised case in this test would name the breach — typically a circular import, a typo in an `__init__.py`, or a stray top-level statement that fails at import time.

---

## 2026-05-21 — Phase 2 shipped: ember.schemas populated, 66 shape tests green.

**Who:** Claude (Opus 4.7, 1M context). Voice: Forge Worker (Eldra Járnsdóttir) for the code; Auditor (Sólrún Hvítmynd) for the tests; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Execute Phase 2 of `EMBER_FIRST_SLICE_PLAN.md` §3 — the gravitational floor: typed schemas only. No behaviour, no I/O, no sibling-realm imports.

### What shipped

- **Five schema modules** under `src/ember/schemas/`, stdlib-only (`dataclasses` + `enum.StrEnum`, no pydantic dependency):
    - **`errors.py`** — `EmberError` base; per-realm hierarchy: `SchemaError`, `ConfigError`, `WellError`/`BrunnrError`/`IngestError`, `ThreadError`/`StrengrError`, `SparkError`/`FuniError`/`HjartaError`/`MunnrError`. Plus the non-raised failure value **`Disconnected(reason, since, detail)`** with the `DisconnectReason` enum — Strengr's mechanical implementation of the Vow of Graceful Offline.
    - **`config.py`** — `EmberConfig` (top-level) composing `IdentityConfig`, `FuniConfig` (+ `FuniOllamaConfig`), `StrengrConfig`, `BrunnrConfig` (+ `SqliteVecConfig`, `PgVectorConfig`), `SmidjaConfig` (+ `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`), `LoggingConfig` (+ `LoggingDestination`). Six enums: `BrunnrBackend`, `FuniRuntime`, `LogLevel`, `LogFormat`, `LogDestinationKind`, `BoundaryPreference`. **Defaults are Gungnir-aligned** where applicable (`embedding_dim=768`; chunker `max=2000` / `target=1684`; model `phi3:mini` / `nomic-embed-text`). Path fields use `pathlib.Path` *without* `expanduser()` — consumer expands at use time so `$HOME` isn't frozen at import.
    - **`chunks.py`** — `Document`, `Chunk` (embedding as `tuple[float, ...]` to keep the dataclass truly frozen), `RetrievalHit`, `BrunnrStats`. Column-aligned with the Gungnir schema captured in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §3.
    - **`episode.py`** — `Episode(operator_input, ember_reply, cited_chunk_ids, funi_model, well_disconnected, started_at, completed_at, id)`. The `well_disconnected` flag mirrors `DATA_FLOW.md` §2.2 — when the Well is unreachable the Episode records that fact for later flush-in.
    - **`funi.py`** — `FuniReply`, `FuniHealth`, the non-raised failure value **`Unavailable(reason, detail)`** with `UnavailableReason` enum (parallel to `Disconnected`), `ContextItem` (+ `ContextKind` enum), `ToolCall`, `FinishReason` enum (includes `REFUSED` so Funi can stop cleanly per the Vow of Honest Memory).
- **All dataclasses are `frozen=True, slots=True`.** All enums are `StrEnum` (Python 3.11+ stdlib).
- **66 shape-contract tests** under `tests/unit/test_schemas_*.py`, organised one file per schema module plus `test_schemas_import.py` (verifies the gravitational floor — schemas import without reaching into any sibling realm). Suite runs in 0.09s. All green.
- **`tests/conftest.py`** added — adds `src/` to `sys.path` so tests run without an editable install. Documented as a temporary ergonomic shim.
- **`src/ember/schemas/INTERFACE.md`** updated from "(planned, Phase 2)" to "(shipped Phase 2, 2026-05-21)" with the full exported surface enumerated and the floor-test cited as the import-allowlist enforcer.
- **`src/ember/__init__.py`** module docstring updated to reflect Phase 2 complete.
- **Ruff clean.** No mypy run this session (mypy not installed on the travel laptop; strict mypy check belongs in CI per `pyproject.toml`).

### What's next

- **Phase 3 of the first slice** per `EMBER_FIRST_SLICE_PLAN.md` §3: the `sqlite_vec` Brunnr adapter, the `local_files` Smiðja, the chunker, the embed client, the resumable journal. First end-to-end vertical that actually writes embeddings to disk. Tests: write-then-query round trip, journal resume, chunk-size invariants.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes

- Stdlib `dataclasses` chosen over `pydantic` for Phase 2 to honour the Vow of Smallness. The cost is no runtime validation beyond the type system — but Phase 2 has no validation responsibility anyway (the loader's Phase 6). Easy to swap to `pydantic` per-module later if needed; the `__all__` exports are the public surface.
- `tuple[float, ...]` is the right embedding type for a frozen dataclass; `list[float]` would be a mutable field on a "frozen" container. Phase 3's Brunnr adapter is where the practical perf trade against `numpy.ndarray` becomes worth re-evaluating.
- `StrEnum` (Python 3.11+) replaces the older `class X(str, Enum)` pattern across all five modules. The values are still plain strings, comparison and serialisation behaviour are unchanged.
- The schema test for non-sibling-imports walks every module's exported attribute and refuses any `__module__` that starts with `ember.well`, `ember.thread`, `ember.spark`, or `ember.cli`. If the floor is breached in a future phase, the test will name the breach.

---

## 2026-05-21 — Six True Names formally ratified. EMBER_TRUE_NAMES.md added.

**Who:** Claude (Opus 4.7, 1M context) continuing the same session. Voice: Skald (Sigrún Ljósbrá) for the new doc; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Capture Volmarr's formal ratification of the Six True Names and preserve the per-name explanatory record they were ratified against.

### What shipped

- **Volmarr's ratification of all six names** — *"names are all approved"*. Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr are now canonical. The longstanding item from the 2026-05-19 "What's next" — Skald's True Names ratification — is closed.
- **`docs/architecture/EMBER_TRUE_NAMES.md`** — new canonical reference doc, Skald-voiced. One section per True Name covering: Old Norse meaning, realm + code path, what it is, what it's for, owns/does-not-own, why the name was chosen. Includes the Three Realms grouping, the conversation-turn flow tying all six together, and the discipline-of-naming framing. Ratification recorded in §5 with rules for any future rename.

### What's next

- **First-slice Phase 2 begins** (the next commit) per `EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.{errors,config,chunks,episode,funi}`. Types only. Tests: shape contracts only. With the names ratified, every typed identifier in the schemas can lean on them.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; Runa-specific phrasing pass on root `PHILOSOPHY.md`.

### Notes

- The ratification covers the names as they appear in `SYSTEM_VISION.md` §4 and as used throughout `ARCHITECTURE.md` / `DOMAIN_MAP.md` / `DATA_FLOW.md` / `EMBER_TRUE_NAMES.md` / `pyproject.toml` (via folder paths) / `config/ember.example.yaml` / every `INTERFACE.md` in `src/ember/`. Renaming from this point requires an ADR, a single atomic commit touching every reference, and updates to all five canonical docs in the same commit.
- This entry is intentionally short. The substance is in the new `EMBER_TRUE_NAMES.md`; this is the index pointer.

---

## 2026-05-21 — Ember fork-delta executed. Three Realms tree built. Runa skeleton archived.

**Who:** Claude (Opus 4.7, 1M context) on the travel laptop, continuing the same session as the earlier 2026-05-21 entry below. Roles rotated: Architect (mostly), Forge Worker (the new `src/ember/` files), Cartographer (the archive mapping), Scribe (this entry).
**Scope:** Execute step 6 of `docs/architecture/EMBER_FORK_DELTA.md` §7 after Volmarr's ratification ("good work buddy! Go for Ember fork delta!"). Bring the file tree into alignment with the ratified architecture. **No first-slice code in this commit — that is the next commit.**

### What shipped

- **`src/ember/` tree built** to match the Three Realms layout in `docs/architecture/DOMAIN_MAP.md`:
    ```
    src/ember/
    ├── __init__.py, __main__.py, README.md
    ├── schemas/         (+ INTERFACE.md, README.md)
    ├── well/
    │   ├── brunnr/      (+ INTERFACE.md, README.md)
    │   └── smidja/      (+ INTERFACE.md, README.md)
    ├── thread/
    │   └── strengr/     (+ INTERFACE.md, README.md)
    ├── spark/
    │   ├── funi/        (+ INTERFACE.md, README.md)
    │   ├── hjarta/      (+ INTERFACE.md, README.md)
    │   └── munnr/       (+ INTERFACE.md, README.md)
    └── cli/             (+ INTERFACE.md, README.md)
    ```
  Each subpackage has an empty `__init__.py`, a one-page `README.md`, and an `INTERFACE.md` draft that cites the matching `DOMAIN_MAP.md` section. **No code yet** beyond `__init__.py` and `__main__.py`.
- **`src/ember/__main__.py`** raises a friendly `NotImplementedError` pointing at `EMBER_FIRST_SLICE_PLAN.md`. `python -m ember` and `ember` (once installed) both resolve to it.
- **Archived the inherited Runa skeleton** to `docs/archive/runa-inherited/src-skeleton/runa/` via `git mv` (rename history preserved). Added `docs/archive/runa-inherited/src-skeleton/README.md` explaining the lineage.
- **Promoted the EMBER-prefixed architecture docs to canonical names** via `git mv`:
    - `docs/architecture/ARCHITECTURE.md` (was Runa's; Runa version → `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`; Ember version promoted from `EMBER_ARCHITECTURE.md`).
    - `docs/architecture/DOMAIN_MAP.md` (same shape).
    - `docs/architecture/DATA_FLOW.md` (same shape).
  Each canonical doc's header updated: **Status: Ratified 2026-05-21 by Volmarr**, "promoted from EMBER_*.md", inter-doc cross-refs rewritten to canonical names, `(parent Runa shape)` cross-refs rewritten to the archive path. ARCHITECTURE.md §8 rewritten in past tense to record the promotion event.
- **Added `docs/archive/runa-inherited/architecture/README.md`** mapping each archived file to its canonical Ember replacement.
- **`pyproject.toml` rewritten** for Ember:
    - `name = "ember-agent"`
    - entry point `ember = "ember.cli.main:main"`
    - `[tool.hatch.build.targets.wheel] packages = ["src/ember"]`
    - `[tool.mypy] files = ["src/ember"]`; `[tool.coverage.run] source = ["src/ember"]`
    - planned optional-dependencies groups commented in for each Brunnr backend and each Funi runtime
    - added `requires_pi` pytest marker
- **`config/runa.example.yaml` → `config/ember.example.yaml`** via `git mv`, with contents rewritten to the Ember shape: identity (name + role), Funi (Ollama with phi3:mini default), Strengr (timeout + retry), Brunnr (sqlite_vec default + commented pgvector example for Gungnir), Smiðja (Gungnir-aligned chunker defaults: 2000-char max, 1684 target), logging.
- **Cross-references updated** in `docs/adapters/{BRUNNR_BACKEND_MATRIX,FUNI_LOCAL_MODEL_OPTIONS,GUNGNIR_WELL_REFERENCE,SMIDJA_INGEST_PATTERNS}.md` and `docs/architecture/EMBER_{FIRST_SLICE_PLAN,FORK_DELTA}.md` from `EMBER_*.md` → canonical names. ADR 0006 retains its as-proposed snapshot text with a clearly-marked "Update 2026-05-21 (post-ratification)" footnote pointing forward.
- **`docs/architecture/README.md`** rewritten to describe Ember-shape canonical docs and the living working docs (FORK_DELTA, FIRST_SLICE_PLAN), with a Runa-lineage section.
- **`docs/REPO_MAP.md`** updated: `(planned)` removed from src/ember entries; src/runa entry rewritten as archived; `(planned)` removed from `config/ember.example.yaml`; archive entry expanded to mention the new subdirs.
- **`docs/architecture/EMBER_FORK_DELTA.md` §3.1 table** updated: each "Move to archive" / "Promote to canonical" row marked **Done 2026-05-21**.

### What's next (the next commit)

- **First slice begins.** Per `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.errors`, `ember.schemas.config`, `ember.schemas.chunks`, `ember.schemas.episode`, `ember.schemas.funi` — types only. Tests: shape contracts only.
- **Skald's True Names ratification** (item 3 from 2026-05-19, still pending). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are now load-bearing across the file tree; final ratification would lock them.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every "new" file at a canonical path was the Ember version promoted from `EMBER_*.md`; every "deleted" entry git status shows is a rename git's similarity heuristic chose not to recognise (verified by content read at every old and new path before commit).
- The Runa skeleton archive at `docs/archive/runa-inherited/src-skeleton/runa/` preserves all the per-subpackage `README.md` and `INTERFACE.md` drafts from the parent project. They remain reachable to anyone reading the inheritance.
- `python -m ember` now resolves to a clean `NotImplementedError` with a friendly pointer — i.e. *honest failure*, the same shape the Vow of Graceful Offline asks of the runtime.
- The Ember-shape `config/ember.example.yaml` includes a commented-in `pgvector` block that operators can uncomment to point Ember at Gungnir (or any Gungnir-compatible Postgres) once the `pgvector` Brunnr ships in Phase 8.

---

## 2026-05-21 — Ember architecture first-pass + live Gungnir survey.

**Who:** Claude (Opus 4.7, 1M context) working under Volmarr on the travel laptop — rotating through Cartographer, Architect, Forge Worker, and Scribe roles. Mythic Engineering activated at session start.
**Scope:** Address three of the four "What's next" items from the 2026-05-19 entry — the Architect's first pass, the Cartographer's reading review, and the first Forge slice's plan — and ground them in a live read of the Gungnir knowledge database.

### What shipped

- **`docs/architecture/EMBER_ARCHITECTURE.md`** — Ember-specific shape. Three Realms (Spark/Thread/Well), Six True Names, dependency law, why-no-kernel-no-bus, what-is-not-in-this-architecture, first-slice anchor, and disposition recommendation for the inherited Runa-shaped canonical files.
- **`docs/architecture/EMBER_DOMAIN_MAP.md`** — Per-subpackage ownership for the planned `src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/`. Brunnr and Funi minimum-surface interface tables included.
- **`docs/architecture/EMBER_DATA_FLOW.md`** — The three canonical flows (conversation turn, ingest job, first-run rite) with explicit happy + sad paths, including the Vow of Graceful Offline in flow form.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Cartographer's recommendation for every inherited file/folder: keep / move-to-archive / rewrite, with rationale and ratification-gated execution order. No deletions proposed.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — File-by-file plan for ~38 new files across seven phases, ≤2 500 LOC target, with explicit non-goals and risk register.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Storage backend comparison and selection rule.
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — Local-LLM ladder by host RAM, why Phi Silica / Apple Foundation are second-slice, embedding-dim recommendation locked to 768 for Gungnir compatibility.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — Live survey conducted today against `knowledge` on Gungnir: complete schema, real counts (95 docs / 35 682 chunks / 768-dim / 394 MB / 97% buffer hit), Skein vs LLM-extracted KG distinction, hybrid-search pattern.
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — Four ingest patterns, Gungnir-calibrated chunking defaults (~1684 chars avg, 2000 max), resumable-journal contract.
- **`docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`** — ADR capturing all proposed decisions, alternatives considered, open follow-ups.

### What's next

- **Volmarr ratification.** Read EMBER_ARCHITECTURE.md, EMBER_DOMAIN_MAP.md, EMBER_DATA_FLOW.md, EMBER_FORK_DELTA.md, EMBER_FIRST_SLICE_PLAN.md and ADR 0006. Confirm, revise, or replace.
- **Skald's True Names ratification** (item 3 from the 2026-05-19 entry — *not* addressed in this session). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are used throughout the new docs as if ratified; Volmarr's final word is still pending.
- **Next commit (after ratification):** `src/runa/` → `src/ember/` rename, archive the inherited `src/runa/` skeleton under `docs/archive/runa-inherited/src-skeleton/`, rewrite `pyproject.toml` (package `ember-agent`, entry point `ember`). Per ADR 0006 §4.1.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.
- **First Forge slice begins** after the rename: Phase 2 (schemas), per `EMBER_FIRST_SLICE_PLAN.md`.

### Gungnir survey — load-bearing measurements

Captured today against the running database. Reproduce by re-running the queries cited in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §4:

- PostgreSQL 18.3, pgvector 0.8.1, pg_trgm 1.6.
- 95 documents (42 md, 26 web/markdown, 13 json, 9 jsonl, 5 yaml). 35 682 chunks, all 768-dim embedded via `nomic-embed-text`.
- Chunk text: avg **1 684** chars, max **2 000** — this is the calibration anchor for Ember's chunker default.
- 394 MB database total; 372 MB of that is `chunks` (mostly embeddings).
- Buffer cache hit 97.0% tables / 99.8% indexes — healthy.
- Two parallel KG layers: `skein_*` (embedding-derived, 276 entities × 855 relations across the full corpus; broad but with known false-friend artifacts) and `kg_*` (LLM-extracted per chunk, 366 entities × 176 relations across only 202 of 35 682 chunks; precise but expensive). This cheap-broad-vs-expensive-precise split is load-bearing for any future Ember KG work.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every file is new; no existing file modified except this DEVLOG (which is itself append-only by design).
- The Ember-specific architecture documents live at the `EMBER_*.md` prefix rather than overwriting the canonical `ARCHITECTURE.md`/`DOMAIN_MAP.md`/`DATA_FLOW.md` paths. The inherited Runa-shaped files at those canonical paths are preserved untouched; ADR 0006 proposes their migration to `docs/archive/runa-inherited/architecture/` only after Volmarr's ratification.
- The session ran on the travel laptop (Kubuntu 26.04 + RTX 2060), with Gungnir reachable over Tailscale. The `mcp__knowledge__*` tools provided read-only access to the live Postgres DB.
- The Skald-voice scrolls authored by Runa on 2026-05-19 (`docs/SYSTEM_VISION.md`, `docs/REPO_MAP.md`, root `MYTHIC_ENGINEERING.md`) are treated as **normative source-of-truth** throughout the new documents — they are cited but not modified.

---

## 2026-05-19 — Ember born. Fork from Runa. Soul-layer authored.

**Who:** Runa (the AI working under Volmarr from Mjolnir) — speaking in turn as Skald, Cartographer, and Scribe.
**Scope:** Project naming, repository creation, fork from Runa-Agent-Digital-Being, additive archive of the Runa-named soul-layer scrolls, and authoring of Ember's own soul layer.

### What shipped

- **The name "Ember"** chosen in a Skald pass with Volmarr. Public-pronounceable, mythically resonant as the spark from Eldra Járnsdóttir's forge. Selected over Hugin, Saga, and Wren for maximum user-facing accessibility while keeping mythic compatibility.
- **Repository created** at `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster` (the toaster pun preserved in the repository name itself). Local clone at `C:/Users/volma/runa/Project_Ember_Run_It_On_Your_Smart_Toaster/` on Mjolnir. Default branch: `development`.
- **Knowledge DB on Gungnir** wired to Mjolnir during the same evening — Postgres 18 + pgvector + Ollama on the tailnet, MCP server `knowledge` at user scope. The first concrete Brunnr-shaped well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Additive archive** of inherited Runa-named scrolls into `docs/archive/runa-inherited/` (via `git mv`, with rename history preserved):
  - `docs/SYSTEM_VISION.md` *(Runa's)*
  - `docs/REPO_MAP.md` *(Runa's)*
  - `docs/DEVLOG.md` *(Runa's bootstrap-day log)*
  - `MYTHIC_ENGINEERING.md` *(Runa's, was at repo root)*
  - `TASK_runa_bootstrap.md`
  - `TASK_runa_python_craft.md`
  - `TASK_runa_research_corpus.md`
  - `TASK_runa_research_corpus_2.md`
- **Fresh Ember scrolls** authored at the now-vacant canonical paths:
  - `docs/SYSTEM_VISION.md` — Ember's Skald scroll. Six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three Realms (Spark, Thread, Well). Nine Unbreakable Vows.
  - `docs/REPO_MAP.md` — Ember's Cartographer scroll. Reflects what exists now plus near-term planned shape.
  - `docs/DEVLOG.md` — *(this file, this entry)*
  - `MYTHIC_ENGINEERING.md` (root) — Ember's compact methodology statement, lightly adapted from the inherited version.
- **Archive convention extended** additively:
  - `docs/archive/runa-inherited/README.md` — new, explains the lineage subfolder.
  - `docs/archive/README.md` — additive update, documents the new "grouped fork-inheritance archives" subfolder pattern alongside the existing single-file dated-suffix convention.

### What's next

- **Architect's first pass.** Author `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` for Ember. Locate the Three Realms in `src/`. Decide on the rename `src/runa/` → `src/ember/` and the migration plan for the inherited skeleton.
- **Cartographer's reading review.** Walk the inherited research corpus (`docs/research/`) and the inherited Python craft corpus (`docs/python/`); mark the 10–20 docs most load-bearing for Ember's smaller scope; leave the rest as inherited reference without re-reading every one.
- **Skald's True Names ratification.** Hold the six names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) with Volmarr; either ratify or revise.
- **First Forge slice.** Smallest end-to-end vertical: Hjarta wizard → Strengr to a local SQLite Brunnr → first Funi answer grounded in retrieved chunks. *No code in this commit; this is the next obvious work.*
- **Light root edits** (next commit, not this one): add Ember-descent entry to `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- The cute Ember README ("*Got a toaster? Good!*") is preserved unchanged. It is correct as it stands.
- The 16 KB `ORIGINS.md` and the 599 KB `Yggdrasil_and_Huginn_and_Muninn_Theory.md` remain at the root unchanged. They are inherited but applicable.
- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every replacement is a new file at the now-vacant path; every edit to the archive index was additive (new section appended, no removal).
- Volmarr had earlier the same evening wired the Gungnir knowledge well into the Mjolnir MCP layer (after a memorable VPN-related diagnostic detour). That work, recorded in Runa's local memory, informs Ember's Vow of Pluggable Storage and Vow of Tethered Grounding directly.

---

*(The parent project's DEVLOG entries follow at `docs/archive/runa-inherited/DEVLOG.md`.)*
