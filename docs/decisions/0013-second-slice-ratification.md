# ADR 0013 — Second-slice ratification

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr** ("go for phase 17")
**Author:** Mythic-Engineering session driven by Volmarr — Architect / Forge Worker / Auditor / Cartographer / Scribe (roles rotated through the slice)
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

The second slice of Ember is complete: Phases 8-17 of
`docs/architecture/EMBER_SECOND_SLICE_PLAN.md` shipped across one
working day (2026-05-21) on top of the slice-1 baseline (ratified by
ADR 0007). The acceptance criterion of §0 of that plan is met, and
verified end-to-end:

- against real `sqlite_vec` + real Ollama (`llama3.2:3b` for tools,
  `phi3:mini` for plain chat) by the automated `tests/integration/test_phase17_acceptance.py`,
- against the live Gungnir Postgres on tailnet by `tests/integration/test_pgvector_real_backend.py::TestGungnirRetrieval`,
- against a podman-launched ephemeral pgvector container by the same
  test file's `TestContainerWritePath`,
- and by a manual real-llama3.2:3b smoke covering the full tool-loop
  (DEVLOG 2026-05-21).

Five operator-facing capabilities were added on top of slice 1:

1. **Operator config loader** — `~/.ember/config/ember.yaml` is the
   single source of truth for behaviour. Hjarta writes it at first
   run; edits take effect on next invocation.
2. **Streaming Funi replies** — tokens land in `ember chat` as they
   generate. Ctrl-C tags partial replies and returns to the prompt.
3. **`pgvector` Brunnr** — Gungnir-compatible Postgres backend.
   `read_only: true` mechanically protects shared Wells from writes.
4. **Tool framework** — process-global registry, typed approval
   resolution (PER_CALL / STANDING / FORBIDDEN), append-only JSONL
   audit log, six-kind stdlib argument validator.
5. **Three first-party tools** — `search_well` (STANDING),
   `read_local_file` (PER_CALL + filesystem sandbox), `fetch_url`
   (PER_CALL + robots.txt + address-class refusals).

Four ADRs ratified during slice 2 — 0008 (config loader), 0009
(streaming), 0010 (pgvector), 0011 (tool use) — set the design
contracts. This ADR ratifies the *slice itself*: what it set as canon,
what it deferred, and the standing rules going into slice 3.

## 2. Decisions

### 2.1 Slice-1 standing rules carry forward, plus three extensions

ADR 0007 §2 — stdlib-first, typed-value-over-exception, `*_kind` class
attributes, FTS5 input sanitisation — **all hold for every slice-2
adapter**. Verified by:

- The `pgvector` adapter uses stdlib `psycopg` (the only viable
  Postgres client; documented as an opt-in extra per the policy).
- Every new failure mode crosses a realm boundary as a typed value:
  `Disconnected(AUTH_FAILED)` from the secret resolver, `ToolReply.error`
  from the tool framework boundary, `FuniStreamChunk(finish_reason=ERROR)`
  for stream-failure folding.
- `backend_kind = "pgvector"` and `runtime_kind` extensions follow the
  pattern.
- `plainto_tsquery('english', $1)` is the Postgres analogue of the
  FTS5 input sanitisation rule.

Three extensions canonicalised by slice 2:

- **(§2.2)** Operator-facing config is YAML at a single canonical path,
  loaded by `ember.config.load_ember_config(config_root)`.
- **(§2.3)** Streaming-versus-non-streaming is a Funi-side capability;
  Spark consumes both via the same Protocol method (`complete_streaming`
  exists alongside `complete`).
- **(§2.4)** Tool use is opt-in, per-call-approvable by default,
  registry-FORBIDDEN at the floor, and audited unconditionally when
  enabled.

### 2.2 Operator config is the single source of truth

**Decision:** `~/.ember/config/ember.yaml` is the operator's editing
surface. The dataclasses in `ember.schemas.config` are the *defaults*;
the YAML overlays them; environment variables overlay the YAML; CLI
flags overlay the env. Per ADR 0008 §2.3.

**Concrete consequences for slice 3+:**

- Any new operator-tunable knob lands as a field on the relevant
  config dataclass (with a sensible default) and a documented YAML
  block in `config/ember.example.yaml`.
- CLI flags exist for *per-invocation* overrides only — never as the
  primary configuration surface.
- Environment-variable overlays remain narrow: `OLLAMA_HOST` (the
  slice-1 escape hatch) and `EMBER_WELL_PASSWORD` (the slice-2
  secret-resolution first stop). New env vars require an ADR.

### 2.3 The graceful-offline contract extends to Funi and tools

ADR 0007 §2.2 (typed-value-over-exception) defined the Vow of
Graceful Offline for the Strengr→Brunnr boundary. Slice 2 propagates
it:

- **Funi opens** return `FuniHandle | Unavailable` (`Unavailable`
  carries a typed `UnavailableReason`).
- **Funi completes** never raise across the boundary; runtime failures
  fold into `FuniReply(finish_reason=ERROR)` (and the streaming
  equivalent: a final ERROR chunk).
- **Tool executes** never raise across the boundary; the framework
  catches any exception and produces `ToolReply(error=...)`.
- **pgvector opens** classify `psycopg.OperationalError` into one of
  eight `DisconnectReason` values (per ADR 0010 §2.8) so Strengr's
  retry policy can distinguish recoverable from non-recoverable.

The slice-3 expectation: any new adapter that crosses a realm
boundary returns typed values, never raises.

### 2.4 Tool use stays read-mostly first

**Decision:** The slice-2 tool framework supports approval, sandbox,
audit. **It does not yet support writes** — no file-write tool, no
shell-command tool, no git operations, no MCP write-side bridge. Per
the EMBER_SECOND_SLICE_PLAN.md §4 exclusion list.

**Why:** Operators need lived experience with the approval flow, the
audit log, and the sandbox refusals before write-side tools introduce
a much larger risk surface. The Phase-16 acceptance smoke already
caught one Ollama-side bug (tool_calls on a non-`done` frame) — the
slice-3 conversation about write tools benefits from another month of
read-side operator feedback before it starts.

**Slice 3+ direction:** A dedicated ADR for write tools is queued. It
will at minimum: extend `ApprovalOutcome` with write-specific
classifications; add a `dry_run` parameter to descriptors that
declare write semantics; introduce a per-tool "blast radius"
declaration (single file? subtree? global?) that operators see in the
proposal.

### 2.5 Audit-log shape is stable across slices

The JSONL record shape defined in ADR 0011 §2.7 is **stable** going
forward. Slice 3+ may add fields (`auditor_id` for multi-operator,
`tool_version` for installed-from-pip tools) but will not rename or
remove existing ones. Operators may write log-rotation policies,
analytics dashboards, or alerting against the current shape.

Single exception: when ADR 0011 §4 ("Open questions") delivers
streaming tool replies, the `reply.output` may grow a
`reply.chunks: list[str]` sibling. That's additive.

### 2.6 The Six True Names are immutable

Slice 2 introduced new subsystems (`config/`, `tools/`) and one new
Hjarta state (`ADVANCED_TOOLS`). The **Six True Names** (Funi /
Strengr / Brunnr / Smiðja / Hjarta / Munnr) remain the load-bearing
identity — every new subsystem is either internal to one of the Six,
or a sibling that does not compete for their role. This holds going
into slice 3.

The next plausible name candidate is **Auga** (eye / view — ADR 0012
GUI). When it ships it joins the Six rather than replacing any of
them.

### 2.7 The plugin scaffold stays empty

`src/ember/plugins/` was reserved in slice 1 and remained untouched
in slice 2. Tools, Brunnr backends, and Funi runtimes all live as
first-party modules under their respective subpackages. Operator
opinion on third-party-plugin loading remains untested; slice 3 may
draft an ADR, but the scaffold stays empty until then.

## 3. What slice 2 deliberately deferred (still queued)

Per EMBER_SECOND_SLICE_PLAN.md §4, all of these are deferred:

- **Other Brunnr backends** — `qdrant`, `chroma`, `lancedb`. None
  blocked; each is a Phase-12-shaped commit when an operator wants
  them.
- **Other Funi runtimes** — `llamacpp`, `lmstudio`, `phi_silica`,
  `apple_foundation`. The Protocol holds; each adapter is a
  Phase-5-shaped commit.
- **Other Smiðja sources** — `url_fetch`, `shared_well`, `nomad`.
- **Other surfaces** — Auga (GUI), Rödd (voice), Bifröst (HTTP
  gateway). ADR 0012 was queued in slice 2 ratification; slice 3
  authors the design.
- **Writable tools** — see §2.4 above.
- **Multi-operator shared Wells** — backend-level locking is out of
  scope until an operator actually has two Embers fighting over one
  Well.
- **Skein / KG retrieval layers** — depend on Skein/Skry being
  importable as Ember adapters; separate ADR.
- **Plugin framework** — see §2.7 above.
- **Backup / restore / export-import** for the Well — operational
  tooling slice.
- **Voice + image modalities for Funi** — Funi stays text-only.

## 4. Where the version goes

Slice 2 closes at **0.2.0**. Development Status classifier stays at
`3 - Alpha`. The Phase-by-Phase release ladder, for archaeology:

| Phase | Release | Capability |
|---|---|---|
| 9  | `0.1.5` | config loader live |
| 11 | `0.1.7` | streaming Funi live |
| 13 | `0.1.9` | pgvector live |
| 16 | `0.2.0rc1` | tools live (release candidate) |
| 17 | `0.2.0` | slice-2 ratified |

The next bump (`0.3.0`) lands when slice 3 ratifies.

## 5. Consequences

**Gain:**

- The operator can configure Ember by editing one YAML file.
- The operator can tether Ember to a Gungnir-shape Postgres + pgvector
  Well with one config switch + one pip extra; `read_only: true`
  mechanically protects shared Wells.
- The operator can enable tool use, approve each call, and audit
  everything afterward.
- Every realm boundary is now typed-value across the board (slice-1
  Strengr/Brunnr; slice-2 Funi/Tools).
- The test suite covers 488 cases including 1 streaming + 14 pgvector
  (10 container + 4 Gungnir) + 11 tool-framework + 7 tool-loop
  integration + 3 slice-2 acceptance.

**Cost:**

- Five new optional pip extras: `sqlite_vec`, `config`, `pgvector`.
  (`tools` and `validation` are documented but unused — the first
  three tools are stdlib-only.)
- ~3 KLOC of framework code on top of the slice-1 baseline.
- One model-capability constraint operators must know: `phi3:mini`
  cannot do tool calls; `llama3.2:3b` is the Pi-class default for
  tool-enabled chat.

**Risks deliberately accepted:**

- **No write tools yet (§2.4).** Operators who want file edits,
  shell commands, or git ops will wait for slice 3.
- **No plugin loader yet (§2.7).** Third-party tool authors fork the
  repo or vendor their tools under `src/ember/tools/`.
- **No daemon mode.** `ember chat` is a single-process CLI surface;
  multi-process / concurrent-operator deployments wait for the
  Bifröst HTTP-gateway slice.
- **Tool-loop iterations bounded at 8.** A model that loops on
  tool_calls forever still terminates with an operator-facing
  `[tool-loop max iterations reached]` message. Raising this requires
  an ADR.

## 6. Open questions deferred to slice 3

- **`ember tool audit` subcommand.** Operators read JSONL files
  directly until a CLI reader lands. Likely candidate for slice-3
  bookkeeping.
- **Hjarta wizard for tool sub-config.** Right now only `enabled`
  is asked at first-run; `standing_trust` and `approval_overrides`
  require yaml editing. A slice-3 advanced wizard could ask both.
- **Auto-detect tool capability.** `Funi.health()` could report
  whether the loaded model supports tool calls, so Hjarta's
  ADVANCED_TOOLS branch can refuse to enable tools on an incapable
  model. Worth an ADR.
- **Audit-log retention.** Currently unbounded; `prune --older 30d`
  is on the slice-3 wishlist.
- **Per-tool `version` field.** Useful for "this tool's behaviour
  changed; reload approvals." Trivial extension to ADR 0011.

## 7. Related docs

- `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` — the plan this ADR ratifies.
- `docs/decisions/0007-first-slice-ratification-2026-05-21.md` — the parallel ADR for slice 1.
- `docs/decisions/0008-config-file-loader.md` — operator config design.
- `docs/decisions/0009-streaming-funi-replies.md` — streaming protocol.
- `docs/decisions/0010-pgvector-brunnr.md` — pgvector adapter design.
- `docs/decisions/0011-tool-use-framework.md` — tool framework design.
- `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` — operator guide for pgvector.
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — the canonical Well shape pgvector targets.
- `deploy/pi/INSTALL.md` — operator install + slice-2 feature sections.
- `tests/integration/test_phase17_acceptance.py` — the acceptance test.
- `DEVLOG.md` — the slice-2 commit ledger.
