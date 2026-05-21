# `ember.tools` — first-party tools

Each file in this directory is **one tool**. Tools register themselves at
import time via `ember.spark.funi.tools.registry.register(descriptor, executor)`.
Importing `ember.tools` imports every first-party tool, which is the
canonical way Munnr wires the registry.

The *framework* (registry, approval, audit, schemas) lives at
`ember.spark.funi.tools` and `ember.schemas.tool`. This directory holds
only the *tools* themselves so a tool author doesn't have to navigate
Funi internals to add one.

## Conventions every first-party tool follows

1. **Top-level `register(_DESCRIPTOR, _execute)`** — the module body
   calls the registry once at import time. No re-import-safe guard is
   needed because Python caches modules; tests use `registry.clear()`
   between cases.

2. **Module-level constants for the descriptor.** `_DESCRIPTOR` is the
   `ToolDescriptor`; `_NAME`, `_TIMEOUT_S` etc. live next to it so the
   descriptor reads top-down.

3. **One `_execute(call: ToolCall) -> ToolReply` function.** The
   framework catches exceptions and converts them to `ToolReply.error`,
   so the executor is allowed to raise. It does not have to be
   defensive at the boundary.

4. **`bind_*` helpers for host state.** A tool that needs a runtime
   handle (e.g. `search_well` needs the `BrunnrHandle`) exposes a
   module-level setter the host calls once at chat-loop setup. The
   executor reads the module-level binding and returns a typed error
   `ToolReply` when nothing is bound.

5. **Sandbox refusals are typed ToolReply errors**, not exceptions. The
   framework's audit log distinguishes denied-by-operator from
   refused-by-sandbox via `ApprovalOutcome.DENIED` vs the tool's own
   error string in `ToolReply.error`. Use clear messages:
   `"refused: path '~/.ssh/id_rsa' is on the sandbox denylist"`.

6. **No third-party deps.** Stdlib only for the first three. Later
   tools that need external libraries declare a pip extra.

7. **Approval policy on the descriptor:**
   - `STANDING` for read-only tools that can't surprise the operator
     (e.g. `search_well`).
   - `PER_CALL` for any tool that touches the filesystem, the network,
     or anything else the operator might want to gate.
   - `FORBIDDEN` is the registry-refuses-to-register lane (ADR 0011
     §2.4). First-party tools never use this; it's reserved for tools
     shipped in a build that the operator wants to mechanically
     disable.

8. **Redaction.** If an argument is sensitive (a token, a password, a
   path the operator would not want in the audit log), list it in
   `ToolDescriptor.redacted_arg_names`. Phase-15 tools don't take
   secrets, but the pattern is preserved for future tools.

## The first three tools (Phase 15)

| Tool | Approval | What it does | Refuses |
|---|---|---|---|
| `search_well` | `STANDING` | hybrid_search against the bound `BrunnrHandle` | unbound handle, dim mismatch, empty query |
| `read_local_file` | `PER_CALL` | read a UTF-8 file under `$HOME` | paths outside `$HOME`, sandbox denylist (`~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`), files larger than 256 KiB |
| `fetch_url` | `PER_CALL` | GET an http(s) URL via stdlib `urllib` | non-http(s) schemes, RFC1918/loopback/link-local unless `allow_private_addresses=true` (config), robots.txt disallow, responses larger than 1 MiB |

See each module's docstring for the per-tool contract; see
`docs/decisions/0011-tool-use-framework.md` §2.9 for the
Phase-14-vs-15-vs-16 split.
