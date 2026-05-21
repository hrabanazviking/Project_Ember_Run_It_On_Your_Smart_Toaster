# ADR 0011 — Tool-use framework

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr** (under the slice-2 scope ratification — "go for slice 2 — bundle 1, 2, 3"; ADR-level ratification implicit in `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 14-16).
**Author:** Mythic-Engineering session — Architect (Rúnhild Svartdóttir) + Scribe (Eirwyn Rúnblóm) + Auditor (Sólrún Hvítmynd).
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

Slice 1's Funi only *answers* — it has no way to *do anything*. The operator can ask "what does pyproject.toml say about Python version?" and the model can guess, hallucinate, or refuse, but it cannot read the file. Same for searching the Well, fetching a URL, or any other capability the operator might want.

Tool use closes that gap. The pattern is mature in the larger AI ecosystem: the model proposes a structured invocation; the host validates, optionally asks the operator, executes, and feeds the result back into the next turn.

For Ember the framing matters as much as the mechanics. The Vow of Sovereignty (`docs/PHILOSOPHY.md` §2) says the operator stays in control. The Vow of Smallness says the default is "no surprises." Together they require that tool use be:

- **Opt-in by default** — a fresh Ember can't reach outside the chat turn until the operator enables it.
- **Per-call approvable** — the operator sees each proposed call and decides, until they explicitly grant standing trust.
- **Mechanically refused at the registry** — some tools should be impossible to call, period.
- **Audited** — every proposal, every approval, every execution is written to a file the operator can read.
- **Bounded by the framework** — a tool can't bypass the registry or the audit log just by knowing the right import name.

This ADR settles the shape of those bounds. The Phase-14 implementation builds the framework; Phase 15 adds the first three tools; Phase 16 wires Munnr to consume `FuniReply.tool_calls`.

## 2. Decision

### 2.1 The four schemas

```python
class ApprovalPolicy(StrEnum):
    STANDING  = "standing"    # auto-approve every call (operator opt-in)
    PER_CALL  = "per_call"    # operator approves each invocation (default)
    FORBIDDEN = "forbidden"   # tool refuses to register at all

@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    name: str
    description: str
    parameters_schema: Mapping[str, ToolParameter]
    required_approval: ApprovalPolicy = ApprovalPolicy.PER_CALL
    redacted_arg_names: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    name: str
    arguments: Mapping[str, object]

@dataclass(frozen=True, slots=True)
class ToolReply:
    call_id: str
    output: str
    error: str | None = None
    elapsed_s: float = 0.0
```

**Why frozen dataclasses, not pydantic:** ADR 0007's stdlib-first rule binds here. Validation is the registry's job (§2.7), not the schema's; the dataclass is just shape.

**Why `tuple` not `Sequence`:** frozen dataclasses can't hold a mutable default. `tuple` is the canonical immutable choice; the rest of Ember's schemas already use this pattern.

**Why `call_id` on `ToolCall` and `ToolReply`:** a single Funi reply can carry multiple tool calls (per ADR 0009 §2.4); the operator may approve some and deny others. The `call_id` is the join key the audit log uses to pair calls with their replies. The id is a UUID4 string assigned by the Funi adapter when it parses the reply, not by Ember.

### 2.2 The parameters_schema shape — stdlib, not jsonschema

`parameters_schema` is a `Mapping[str, ToolParameter]` where:

```python
@dataclass(frozen=True, slots=True)
class ToolParameter:
    kind: ToolParameterKind  # STRING / INTEGER / FLOAT / BOOLEAN / PATH / URL
    description: str
    required: bool = True
    default: object | None = None
    enum: tuple[str, ...] | None = None
```

**Why not jsonschema:** the dependency is large (~1MB), the validation is too permissive for tool-arg use (no path/URL kinds), and the error messages are hostile to operators. Hand-rolling six kinds covers the first three tools (Phase 15) and every plausible later tool with stdlib only.

**Validation contract:** the registry validates arguments against `parameters_schema` *before* approval is prompted (§2.5). Invalid arguments produce `ToolReply(error="...", output="")` and skip the operator — they never reach the executor and they never count against standing trust.

### 2.3 The registry — process-global, import-time registration

```python
def register(descriptor: ToolDescriptor, fn: Callable) -> None: ...
def lookup(name: str) -> tuple[ToolDescriptor, Callable] | None: ...
def list_tools() -> list[ToolDescriptor]: ...
def clear() -> None: ...  # test helper only
```

**Why process-global:** tools register at import time; the alternative (factory injection on every `Funi.complete`) means every caller stitches the same tool set, which is ceremony without payoff for a single-operator CLI.

**Why import-time registration:** a tool's `import ember.tools.search_well` should make it available. The module's top-level call `register(_DESCRIPTOR, _execute)` is the registration event. This matches what most Python tool-use frameworks do and keeps the operator's mental model simple.

**Re-registration is an error.** Calling `register` twice with the same name raises `ToolError`. Tests use `clear()` between cases.

**`FORBIDDEN` refuses at registration.** A tool descriptor with `required_approval=FORBIDDEN` causes `register()` to raise `ToolError("tool 'name' is FORBIDDEN at the registry level")`. This is the mechanical form of "never executable" — a forbidden tool can't even appear in `list_tools()`.

**Concurrency:** the registry uses a `threading.RLock` so registrations from multiple importers (test setup, lazy imports) don't race. Phase 14 doesn't ship any multi-threaded callers; the lock is preventive, not load-bearing.

### 2.4 Approval policy — `PER_CALL` is the default

Three levers determine whether a call executes:

1. **Descriptor default** — `required_approval` on `ToolDescriptor`. Tool author sets this. `STANDING` for read-only tools (e.g. `search_well`); `PER_CALL` for tools with side-effects (`read_local_file`, `fetch_url`); `FORBIDDEN` for tools that shouldn't exist in this build.
2. **Operator config** — `tools.approval_overrides: {tool_name: policy}` in `ember.yaml`. Operator can downgrade `STANDING` to `PER_CALL` (more strict) but **cannot** upgrade `PER_CALL` to `STANDING` for a tool whose descriptor declares it `PER_CALL` — the descriptor is the floor. (The exception is a global `tools.standing_trust: true` knob that flips every `PER_CALL` to `STANDING` — operator opt-in, documented as the "trust everything" mode.)
3. **Operator prompt** — when the resolved policy is `PER_CALL`, the operator sees the proposed call rendered by Munnr and types `y`/`n`/`always`. `always` upgrades that single tool to `STANDING` for the rest of the session (not persisted; restart resets).

**Resolution order:**

```
descriptor.required_approval
  → overlaid with config.tools.approval_overrides[name]  (descriptor is the floor)
  → final approval prompt to operator if PER_CALL
```

`FORBIDDEN` is the floor on the floor — config cannot lift a `FORBIDDEN` descriptor to executable.

### 2.5 Approval outcomes — typed, not boolean

```python
class ApprovalOutcome(StrEnum):
    AUTO_APPROVED         = "auto_approved"          # STANDING / config override
    APPROVED_THIS_CALL    = "approved_this_call"     # operator typed y
    APPROVED_FOR_SESSION  = "approved_for_session"   # operator typed always
    DENIED                = "denied"                 # operator typed n
    INVALID_ARGUMENTS     = "invalid_arguments"      # registry validation failed
    FORBIDDEN_BY_REGISTRY = "forbidden_by_registry"  # descriptor.required_approval == FORBIDDEN
    NO_SUCH_TOOL          = "no_such_tool"           # registry.lookup returned None
```

The outcome is the audit log's primary classifier. `DENIED` and the three refusal outcomes produce `ToolReply(error="...", output="")` without executing the tool.

**Why typed-not-boolean:** the audit log needs to distinguish "operator denied" from "args were invalid" from "tool isn't registered." A boolean collapses three failure shapes into one log line.

### 2.6 The prompter — a Protocol, not a concrete class

```python
@runtime_checkable
class ApprovalPrompter(Protocol):
    def prompt(self, descriptor: ToolDescriptor, call: ToolCall) -> Literal["y", "n", "always"]: ...
```

**Why Protocol:** Munnr's CLI prompter, Hjarta's wizard prompter, and the scripted test prompter all satisfy the same shape. Phase 14 ships a `StdinApprovalPrompter` that reads y/n/always from a `TextIO`; Phase 16 wires Munnr to use it.

The prompter handles only the *interactive* part — it does NOT decide policy. Policy resolution lives in `approval.resolve()` (§2.4), which then either calls the prompter or short-circuits to auto-approved / forbidden.

### 2.7 The audit log — append-only JSONL, atomic per line

**Location:** `<config_root>/state/tool_audit/<YYYY-MM-DD>.jsonl`. One file per UTC day. Created on first append.

**Atomicity:** each line is written with a single `os.write` (or `open(...).write` with `line_buffering`) of a UTF-8 JSON string followed by `\n`. No partial-line writes survive a crash — short writes truncate cleanly.

**Permissions:** the directory is created with mode `0o700`; new files are `0o600`. The audit log can contain sensitive operator input; permission bits protect it.

**Record shape:**

```json
{
  "ts": "2026-05-21T15:30:00.123456+00:00",
  "call_id": "abc123...",
  "tool": "read_local_file",
  "arguments": {"path": "~/notes/runes.md"},
  "approval": "approved_this_call",
  "reply": {"output": "...truncated...", "error": null, "elapsed_s": 0.012},
  "ember_version": "0.1.9"
}
```

**Redaction:** any argument name in `descriptor.redacted_arg_names` is recorded as `"<redacted>"` in the `arguments` dict. Tools that take secrets / paths the operator wouldn't want logged use this. The reply's `output` is *not* automatically redacted (it's the tool author's job to scrub there); the audit log truncates `output` to 4 KiB with an `"..."` suffix to keep the file size bounded.

**Reading the audit log:** `ember tool audit --since 2026-05-19` (planned for Phase 16) tails / filters the files. Phase 14 only writes; reading is the operator's `cat` / `jq` until the CLI subcommand lands.

### 2.8 The execution shape

```python
def execute(call: ToolCall) -> ToolReply: ...
```

Each tool implements this signature. The registry stores the callable alongside the descriptor; the framework calls it after approval.

**Time-out:** each call is wrapped with a per-tool timeout (`ToolDescriptor.timeout_s`, default 10s). Exceeded → `ToolReply(error="timeout: exceeded N s", output="")`. Phase 14 implements the timer in the framework, not the tool.

**Exceptions:** the framework catches every exception from `execute` and produces `ToolReply(error=f"{type(exc).__name__}: {exc}", output="")`. The tool is allowed to raise; it does not have to be defensive. The framework is the boundary that turns exceptions into typed-value errors.

**Side-effect-free retry:** if the operator denies a call, the tool is *not* invoked at all. There is no "preview" mode for tools — preview is what the description string is for.

### 2.9 What Phase 14 ships vs Phase 15-16

Phase 14 (this ADR's implementation phase):

- `src/ember/schemas/tool.py` — every dataclass + StrEnum named above.
- `src/ember/spark/funi/tools/__init__.py` — re-exports.
- `src/ember/spark/funi/tools/INTERFACE.md` — operator-facing surface contract.
- `src/ember/spark/funi/tools/registry.py` — `register`, `lookup`, `list_tools`, `clear`, `FORBIDDEN`-at-registration guard.
- `src/ember/spark/funi/tools/approval.py` — `resolve()` policy resolution, `StdinApprovalPrompter`, the `ApprovalPrompter` Protocol.
- `src/ember/spark/funi/tools/audit.py` — `AuditLog`, atomic JSONL writer, redaction, daily rotation.
- Unit tests covering each module — registry semantics, approval resolution, audit append-only + redaction, dataclass shape contracts.

Phase 15 (next ADR-bundle commit) adds the first three real tools (`search_well`, `read_local_file`, `fetch_url`) plus their tests. They live at `src/ember/tools/`, not under `spark/funi/tools/` — that subpackage is the *framework*; the *tools* live one level out so a tool author doesn't have to navigate into Funi-internal layout.

Phase 16 wires Munnr to consume `FuniReply.tool_calls`, render proposals, drive approval, execute, and feed `ToolReply` back into the next turn. Hjarta gets an "Enable tools?" advanced branch. `cli/main.py` gets `--allow-tools` / `--no-tools` overrides. **That phase bumps to 0.2.0-rc1.**

Phase 17 ratifies the whole slice and bumps to 0.2.0.

**No version bump in Phase 14.** The framework exists but no caller wires through it yet — same standing rule as Phase 12.

## 3. Consequences

**Gain:**

- A clean, audited, operator-controlled extension point for every future capability that needs to reach beyond the chat turn.
- The Vow of Sovereignty becomes mechanical: `PER_CALL` default + `FORBIDDEN` at the registry level mean an Ember can't quietly grow new abilities.
- The audit log is a forensic trail an operator can read after the fact — when did Ember read what file, fetch which URL, query the Well with which terms.
- Tool authors don't write boilerplate: descriptor + execute function, that's the whole API.

**Cost:**

- Six new types, one new subpackage, ~400 LoC of framework before any real tool ships.
- Per-call approval is friction. Operators who want frictionless tool use will set `standing_trust: true` in their config; the framework still audits, but the prompt goes away.
- The audit log is on disk; operators with extreme privacy concerns will need to redact more aggressively or disable tools entirely.

**Risks deliberately accepted:**

- **No fine-grained sandboxing.** A tool's `execute` runs with Ember's full process privileges. The sandbox is descriptor-level (e.g. `read_local_file` rejects `~/.ssh/` in its own code) — there's no syscall filter. If a tool is malicious or buggy, the operator is exposed. Mitigation: only first-party tools ship by default; third-party tools require explicit operator opt-in (registry registration, audit log entry).
- **No remote tools (yet).** Tools run in-process. A tool that needs to call a network service does so directly via stdlib (`urllib.request` etc.); there's no built-in client-server tool transport. Adding one is a future ADR.
- **No tool composition.** A tool can't call another tool. If Funi wants the result of two tools, it issues two `ToolCall` entries in one `FuniReply`. Munnr (Phase 16) handles them in order.

## 4. Open questions deferred to later

- **Audit-log retention.** Files accumulate forever. An `ember tool audit prune --older 30d` is on the Phase-17 wishlist.
- **Tool versioning.** `ToolDescriptor.version`? Useful for "this tool's behaviour changed; reload approvals." Not needed in Phase 14.
- **Group approvals.** "Always approve any tool tagged 'safe-read'." Conceptually clean; postponed until there are enough tools that per-tool config feels heavy.
- **Streaming tool replies.** Some tools (e.g. a future `read_large_file` or `tail_log`) want to stream output. Phase 14 only supports single-shot replies; streaming is a Phase-16+ ADR.

## 5. Related docs

- `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` §3 Phase 14-16 — the slice phasing.
- `docs/decisions/0007-first-slice-ratification-2026-05-21.md` — stdlib-first / typed-value rules this ADR honours.
- `docs/decisions/0009-streaming-funi-replies.md` — `FuniReply.tool_calls` is the channel the framework consumes.
- `docs/PHILOSOPHY.md` §2 — Sovereignty, the policy this framework mechanises.
- `src/ember/schemas/funi.py` — `ToolCall` placeholder dataclass that Phase 14 replaces / promotes.
