# INTERFACE — `ember.spark.funi.tools`

## Module purpose

The tool-use framework (ADR 0011). Schemas live one level up at
`ember.schemas.tool`; this subpackage owns the *behaviour* — the
registry, the approval-policy resolver + interactive prompter, and the
append-only audit log. Phase 14 ships the framework only; tools land in
Phase 15 (`ember.tools`); Munnr wires through in Phase 16.

## Public entry points

### Registry

- `register(descriptor, executor)` — register a tool at import time.
  Raises `ToolError` if the descriptor is `FORBIDDEN` or the name is
  already taken.
- `lookup(name) -> (descriptor, executor) | None` — read a tool by name.
- `list_tools() -> list[ToolDescriptor]` — every registered tool,
  sorted by name.
- `is_registered(name) -> bool` — cheap presence check.
- `clear()` — test helper; production code never calls this.

### Argument validation

- `validate_arguments(descriptor, arguments) -> str | None` —
  None on success; operator-readable error string otherwise (treated by
  the framework as `ApprovalOutcome.INVALID_ARGUMENTS`).

### Approval resolution

- `resolve_approval(descriptor, *, config_overrides, session_standing,
   standing_trust_all) -> ApprovalDecision` — pure policy resolver. No
  IO. Returns either a final outcome or `needs_prompt=True`.
- `resolve_with_answer(answer) -> ApprovalOutcome` — turn a y/n/always
  prompter answer into the final outcome.
- `ApprovalPrompter` — Protocol every interactive prompter satisfies.
- `StdinApprovalPrompter` — concrete prompter reading y/n/always from
  a `TextIO`. Defaults to `sys.stdin` / `sys.stdout`; tests inject
  `io.StringIO`.

### Audit log

- `AuditLog(config_root, *, ember_version="")` — per-process writer.
- `AuditLog.record(*, call, descriptor, approval, reply, when=None)`
  appends one JSONL record to today's file.
- `AuditLog.path_for(when)` and `AuditLog.root_dir` for tests and the
  forthcoming `ember tool audit` subcommand.

## Behavioural contracts

### Registration

- Re-registering an existing tool name is an error.
- A descriptor with `required_approval=FORBIDDEN` cannot register.
- Tools register at import time. Importing
  `ember.tools.search_well` triggers its top-level `register(...)`
  call; the registration survives for the process lifetime.

### Approval

Resolution order (ADR 0011 §2.4):

1. Descriptor `FORBIDDEN` → `FORBIDDEN_BY_REGISTRY` (cannot be lifted).
2. Operator's `standing_trust_all=True` → `AUTO_APPROVED`.
3. Effective policy = descriptor's, then overlaid by config (config can
   downgrade `STANDING` → `PER_CALL`, but cannot upgrade).
4. `STANDING` → `AUTO_APPROVED`.
5. Session has the tool's name → `AUTO_APPROVED` (operator typed
   `always` earlier).
6. Otherwise → caller must prompt; on `y` → `APPROVED_THIS_CALL`, on
   `always` → `APPROVED_FOR_SESSION`, anything else → `DENIED`.

EOF on stdin during a prompt is treated as `n` (safer to refuse than to
silently approve when the operator can't see the prompt).

### Audit log

- One file per UTC day at `<config_root>/state/tool_audit/<date>.jsonl`.
- Directory created mode `0o700`; files mode `0o600`.
- Each record is a single-line JSON object, written with a single
  `os.write` call to a `O_APPEND` fd. Short writes truncate cleanly;
  no partial-line records survive a crash.
- Arguments listed in `ToolDescriptor.redacted_arg_names` are written
  as `"<redacted>"`.
- `reply.output` is truncated to 4 KiB; the record carries an
  `output_truncated: bool` flag. Episodes remain the canonical source
  for full reply text.

## Limitations (Phase 14)

- **No caller wires through yet.** Phase 16's Munnr integration is
  what makes this framework operator-reachable.
- **No `ember tool audit` subcommand.** Operators read JSONL files
  directly until Phase 17 or a follow-up adds the reader.
- **No streaming tool replies.** Single-shot `ToolReply` only; a
  future ADR ships streaming if/when a tool needs it.
- **No syscall sandbox.** Tools run in-process. Sandboxing is each
  tool's own responsibility (`read_local_file` rejects `~/.ssh/` in
  its own code).
