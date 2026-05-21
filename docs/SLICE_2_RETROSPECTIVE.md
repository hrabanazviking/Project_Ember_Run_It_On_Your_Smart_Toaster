# SLICE 2 — Retrospective (2026-05-21)

**Voice:** Scribe (Eirwyn Rúnblóm), with Auditor (Sólrún Hvítmynd)
**Status:** Post-slice retrospective; written 2026-05-21 (slice-2 ratification day)
**Reads with:** `docs/decisions/0013-second-slice-ratification.md` (the ratification ADR), `docs/DEVLOG.md` (the per-phase entries), `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` (the plan that was executed).

---

## What slice 2 was

Slice 2 took the slice-1 Ember (version 0.1.0, ratified ADR 0007 —
the smallest end-to-end vertical that walks Hjarta + Funi + Strengr +
Brunnr-sqlite_vec + Smiðja-local_files + Munnr) and added the five
operator-facing capabilities that move Ember from "minimum viable" to
"deployable to a real operator who wants to live with it":

| Capability | Phase | Release |
|---|---|---|
| Operator config loader (`~/.ember/config/ember.yaml`) | 8-9 | `0.1.5` "config loader live" |
| Streaming Funi replies + Ctrl-C-tags-partial | 10-11 | `0.1.7` "streaming live" |
| pgvector Brunnr (Gungnir-compatible shared Well) | 12-13 | `0.1.9` "pgvector live" |
| Tool framework + first three tools + Munnr tool loop | 14-16 | `0.2.0rc1` "tools live (rc)" |
| Acceptance test + INSTALL.md slice-2 sections + ADR 0013 | 17 | `0.2.0` "slice 2 ratified" |

Ten phases shipped in one working day (2026-05-21).

---

## The numbers

| Metric | Slice-1 baseline | Slice-2 close | Delta |
|---|---|---|---|
| Version | `0.1.0` | `0.2.0` | +0.1 |
| Tests passing | 222 (+2 skipped) | 488 (+2 skipped) | **+266** |
| Test runtime | 0.28s | 18.32s | (slower — mostly the live-pgvector + slice-2 acceptance tests) |
| ADRs ratified | 0001-0007 (7) | 0008-0011 + 0013 (5 more) | +5 |
| `src/ember/` subpackages | 11 | 15 (+`config/`, +`spark/funi/tools/`, +`well/brunnr/pgvector/`, +`tools/`) | +4 |
| Operator pip extras | `sqlite_vec` | `sqlite_vec` + `config` + `pgvector` | +2 |
| Operator-facing YAML knobs | ~12 (slice-1 default-only) | ~40 (full config surface) | +28 |
| Approval-gated tools shipped | 0 | 3 (`search_well`, `read_local_file`, `fetch_url`) | +3 |

---

## What was deliberately deferred (per ADR 0013 §3)

Per `EMBER_SECOND_SLICE_PLAN.md` §4 — the exclusion list — and
re-affirmed by ADR 0013 §3 at ratification:

- **Other Brunnr backends:** `qdrant`, `chroma`, `lancedb`. The
  Protocol holds; each is a future Phase-12-shaped commit.
- **Other Funi runtimes:** `llamacpp`, `lmstudio`, `phi_silica`,
  `apple_foundation`. Same story — each is a future Phase-5-shaped
  commit.
- **Other Smiðja sources:** `url_fetch`, `shared_well`, `nomad`.
- **Other surfaces:** Auga (GUI), Rödd (voice), Bifröst (HTTP
  gateway) — collectively ADR 0012, queued for slice 3.
- **Writable tools:** file write, shell exec, git ops. Read-side
  tools needed lived operator experience first.
- **Multi-operator shared Wells:** concurrent-writer locking is a
  backend-level concern out of slice-2 scope.
- **Skein / KG retrieval layers:** depend on Skein/Skry being
  importable as Ember adapters; separate ADR.
- **Plugin framework:** the `src/ember/plugins/` scaffold stayed
  empty; operator opinion on third-party plugin loading remains
  untested.
- **Backup / restore / export-import** for the Well.
- **Voice + image modalities for Funi.**

None of these block any current slice-2 deployment.

---

## What we learned (the live-fire lessons)

### Two real adapter bugs caught by live-fire

1. **Phase 13 — `register_vector` ran before `CREATE EXTENSION`.**
   The pgvector codec registration needs the `vector` type to exist
   in the target database. On a fresh container Postgres without
   the extension created, `register_vector(conn)` raised
   `vector type not found in the database`.
   - **Fix:** new `_ensure_pgvector_extension(conn, read_only)`
     helper probes `pg_extension` first; creates when writable;
     refuses cleanly on read-only Wells where the extension is
     missing (operator must `CREATE EXTENSION vector` once as DB
     owner).
   - **Regression test:**
     `test_pgvector_open_with_extension_missing_*` cases.

2. **Phase 13 — `{{}}` in `schema.sql` was a stale `.format()`
   escape.** I'd originally written the schema template with
   `.format()` substitution; when I switched to `.replace()` for the
   two named placeholders (`{embedding_dim}`, `{schema}`), I left
   the doubled braces for the JSON-literal default. The result:
   `metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb` was sent verbatim
   to Postgres, which rejected `{{}}` as invalid JSON.
   - **Fix:** `metadata jsonb NOT NULL DEFAULT '{}'::jsonb`.
   - **Lesson:** when you change the substitution mechanism, audit
     all the escapes that were tuned for the old one.

### One real Ollama-streaming surprise

3. **Phase 16 — Ollama emits `message.tool_calls` on a non-`done`
   NDJSON frame.** The adapter originally parsed `tool_calls` only on
   the final `done:true` chunk. Result: the model emitted a tool
   proposal in frame 1 (done=False), then a stop-summary in frame 2
   (done=True, no tool_calls), and the consumer never saw the tool
   call — the chat loop silently terminated without proposing
   anything.
   - **Fix:** accumulate tool_calls across stream frames; attach the
     full list to the final chunk.
   - **Regression test:** `test_streaming_accumulates_tool_calls_from_non_done_chunk`.
   - **Lesson:** test against the real Ollama, not just a clean
     fixture. The Ollama API's NDJSON ordering surprises only show up
     against a real model.

### One operator-facing constraint we learned to document

4. **`phi3:mini` does not support native tool calls.** Ollama returns
   HTTP 400 when the request includes a `tools` field and the model
   doesn't support function calling. The Pi-class default for plain
   chat (`phi3:mini`) is *not* the Pi-class default for tool-enabled
   chat — `llama3.2:3b` is.
   - **Operator-facing fix:** documented in `deploy/pi/INSTALL.md`
     §10 ("Enabling tools") + `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`
     Status header + the §10 Troubleshooting table.
   - **Lesson:** model capability ≠ model family. Each tool-using
     deployment needs a deliberate model choice.

---

## What worked

### Mythic Engineering as a build discipline

- **Document before code.** Every phase opened with an ADR draft (or
  amendments to an existing ADR), got review, then implementation. No
  phase shipped with a design surprise.
- **Whole files only.** Every phase commit delivered complete files.
  No fragments, no "the rest is the same". Verifiable by reading any
  of the 17 phase commits.
- **One ratification ADR per slice.** ADR 0007 + ADR 0013 are the
  load-bearing markers of "what was canonical at this point";
  everything between them rides on those rules.
- **DEVLOG entries per phase.** The Scribe's per-phase entries are the
  prose record next to the commit log — what shipped, what was caught
  by live-fire, what's next. Read at session start.

### Typed-value-over-exception at every realm boundary

ADR 0007 §2.2 established the rule; slice 2 verified it across **every
new boundary**:

- Funi `open()` returns `Unavailable`; `complete()` folds errors into
  `FuniReply(finish_reason=ERROR)`; `complete_streaming()` yields a
  final ERROR chunk.
- Brunnr (both backends) `open()` returns `Disconnected`; eight typed
  reasons; Strengr's retry policy reads them.
- Tool framework: `ApprovalOutcome` distinguishes seven failure /
  success classes; `ToolReply.error` carries executor-side failures
  (typed strings, not exceptions).

The discipline pays in two ways: callers can't accidentally drop a
failure (the type system makes them handle it), and the audit log
classifies failures cleanly (the operator can read "approved /
auto-approved / denied / invalid_arguments / forbidden_by_registry /
no_such_tool" instead of a uniform "failed").

### The Protocol + registry + lazy-import pattern

Slice 2 added two new Protocol implementations (`pgvector` Brunnr,
streaming-and-tool-using Funi) **without touching the Protocols
themselves**. The Phase-3 `BrunnrHandle` Protocol held; the Phase-5
`FuniHandle` Protocol gained one new method (`complete_streaming`) but
didn't require any consumer to change.

Lazy imports (ADR 0007 §2.1) mean a missing pip extra never breaks
`import ember` — the registry's `open()` returns a typed
`Disconnected(BACKEND_REPORTED_UNAVAILABLE)` with a clear "install
the X extra" message.

### Test seams for everything that touches the outside world

- Funi adapters take a test-injectable `urlopen`.
- pgvector tests gate on reachability via `requires_postgres` /
  `requires_gungnir` / `requires_podman` markers; fixtures skip
  cleanly when unmet.
- Tool framework `StdinApprovalPrompter` is a `Protocol` so tests
  inject scripted-answer prompters.
- `fetch_url` tool has three module-level test seams (URL opener,
  address resolver, robots.txt fetcher) so tests cover every
  refusal mode without real network.

488 tests. None of them touch the public internet.

---

## What didn't work as well

### The first-version pgvector adapter was *almost* right

The bug count (two real adapter bugs caught by live-fire) was higher
than the slice-1 sqlite_vec adapter (zero post-acceptance bugs).
Lessons:

- **Test against real Postgres earlier.** Phase 12 shipped 36 unit
  tests, all using mocks. Phase 13 added 14 live-backend tests; both
  bugs would have been caught at Phase 12 with even one real-Postgres
  test.
- **Don't switch substitution mechanisms mid-implementation.** The
  `{{}}` bug was a self-inflicted footgun from changing `.format()`
  to `.replace()` without re-auditing the template.

### The model-capability constraint surfaced late

The `phi3:mini`-can't-do-tool-calls fact surfaced during the Phase-16
acceptance smoke, not earlier in the design. If it had been raised
during ADR 0011 drafting, the slice-2 install guide could have led
with "pull llama3.2:3b for tool use" instead of treating it as a
post-hoc troubleshooting row.

**Fix going forward:** ADRs that depend on a Funi capability (tool
calls, streaming, vision, audio) should name the *specific local
models* that satisfy them, not just the API contract.

### The `tools.example.yaml` file never landed

The slice-2 plan listed `config/tools.example.yaml` as a new file
(see `EMBER_SECOND_SLICE_PLAN.md` §2 file list). Shipping
`tools.example.yaml` separately from `ember.example.yaml` would have
let operators see the tool-use config in isolation. The actual
implementation put everything in `ember.example.yaml` (§10 of the
template) which is fine but slightly cluttered.

**Slice 3+ candidate:** split per-realm example YAMLs from the
single all-in-one `ember.yaml` template once there are operators
contributing their own per-realm tunings.

### `ember tool audit` subcommand wasn't shipped

The slice-2 plan didn't explicitly call for it, but operators reading
the audit log JSONL files via `cat` / `jq` is awkward. A small CLI
reader (`ember tool audit --since 2026-05-19 --tool fetch_url`) would
make the audit log usable as forensics rather than archaeology.

**Slice 3 wishlist item** — ADR 0013 §6 names it explicitly.

---

## How long did it actually take

| Plan estimate | Reality | Variance |
|---|---|---|
| EMBER_SECOND_SLICE_PLAN.md §0 estimated "~5000-7000 LOC across 3-5 sessions" | One working day, 10 phase commits | Significantly faster than estimated |

The variance is mostly because the Mythic Engineering pre-work paid
off: the slice-1 baseline's standing rules + the per-phase ADR
drafts meant each phase opened with the design already settled. No
phase had to back up and re-architect.

The 488-test count is on the high end of what I'd have estimated;
the slice-2 acceptance criterion of "every realm-boundary failure
returns a typed value" naturally generates a lot of one-test-per-
reason cases.

---

## What's queued for slice 3

Per ADR 0013 §3 + §6:

**Deferred capabilities:**

- ADR 0012 alternate surfaces: Auga (GUI), Rödd (voice), Bifröst
  (HTTP gateway).
- Other Brunnr backends as operators want them.
- Other Funi runtimes as operators want them.
- Other Smiðja sources.
- Writable tools (after operators have lived with reads for a while).
- Skein / KG retrieval layers.
- Plugin framework.
- Backup / restore / export-import for the Well.

**Open questions tracked for slice 3:**

- `ember tool audit` subcommand.
- Hjarta wizard for tool sub-config (per-tool approval, standing_trust).
- `Funi.health()` reporting tool-call capability so Hjarta can refuse
  to enable tools on an incapable model.
- Audit-log retention pruning.
- Per-tool `version` field.

---

## The Cartographer's closing word

> *Slice 1 proved Ember could exist on a toaster. Slice 2 proved
> Ember can be tethered to a real Well across a tailnet, can stream
> her thinking aloud, can be granted small operator-approved tools,
> and can do all of this without breaking any of the four Vows the
> Skald named on fork day. The hearth is lit. The next slice's job
> is to give her more ways to be reached — voice, GUI, HTTP — without
> compromising what makes her small.*

— Védis Eikleið

---

## See also

- `docs/DEVLOG.md` — per-phase prose record.
- `docs/decisions/0013-second-slice-ratification.md` — the ratifying
  ADR with the full standing-rules carryforward + deferral list.
- `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` — the plan that was
  executed.
- `deploy/pi/INSTALL.md` — operator install guide covering the
  slice-2 capability surface.
- `docs/OPERATOR_PLAYBOOK.md` — slice-2 operator how-to recipes.
