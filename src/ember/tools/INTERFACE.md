# INTERFACE — `ember.tools`

## Module purpose

The **first-party tools** subpackage. Each file under this directory
is one tool; importing the package `ember.tools` triggers the
side-effect imports of all three first-party tool modules, which
self-register with the process-global tool registry at
`ember.spark.funi.tools.registry`.

This module is the *tool authors' home*. The framework these tools
ride on (registry, approval, audit, schemas) lives one level deeper at
`ember.spark.funi.tools` and `ember.schemas.tool`. The split is
deliberate per ADR 0011 §2.9: a tool author shouldn't need to navigate
Funi internals to add a tool.

**Shipped Phase 15 (slice 2, 0.1.9 → 0.2.0rc1 → 0.2.0).** Three
first-party tools live here; the framework supports more.

## Public entry points

### The package surface

```python
import ember.tools  # side-effect: registers all first-party tools
```

That single import:

1. Loads `ember.tools.search_well` (registers `search_well`).
2. Loads `ember.tools.read_local_file` (registers `read_local_file`).
3. Loads `ember.tools.fetch_url` (registers `fetch_url`).

The package's `__init__` does the import; Python's module cache means
later imports are no-ops. Tests use
`ember.spark.funi.tools.registry.clear()` between cases to reset, then
either re-import or call `register()` directly on the cached
descriptors.

### Per-tool bindings

Tools that need live host state expose `bind_*` module-level setters.
The host (Munnr's `chat.run` in production) calls them once at
chat-loop startup.

| Tool | Binder | Purpose |
|---|---|---|
| `search_well` | `search_well.bind_brunnr(handle, embedder=None)` | Wire the live `BrunnrHandle` + optional embedder so the tool's executor can call `hybrid_search` / `text_search`. |
| `search_well` | `search_well.unbind()` | Test teardown; production never calls this. |
| `read_local_file` | (none) | Stdlib-only; no host state needed. |
| `fetch_url` | `fetch_url._set_url_opener(fn)`, `_set_address_resolver(fn)`, `_set_robots_fetcher(fn)`, `_reset_seams()` | **Test-only** seams that override stdlib calls so unit tests don't make real network traffic. Production never calls these. |

### Per-tool descriptors

Every tool module exposes a private-by-convention `_DESCRIPTOR` and
`_execute` pair that the package import binds into the registry. Tests
that reset the registry can re-register manually:

```python
from ember.spark.funi.tools import register, clear
from ember.tools import search_well

clear()
register(search_well._DESCRIPTOR, search_well._execute)
```

(This is the pattern `tests/integration/test_phase17_acceptance.py`
uses to verify the full slice-2 acceptance flow without import
ordering surprises.)

## Behavioural contracts

### The conventions every first-party tool follows

See `README.md` in this directory for the full list. Briefly:

1. **One file = one tool.**
2. **Top-level `register(_DESCRIPTOR, _execute)`** at module load.
3. **One `_execute(call: ToolCall) -> ToolReply`.** Allowed to raise;
   the framework boundary turns exceptions into typed
   `ToolReply.error` per ADR 0011 §2.8.
4. **Sandbox refusals are typed `ToolReply.error`, not exceptions.**
   Refusal messages name the path + the reason, but never the file
   body / URL content.
5. **No third-party deps** for the first three. Later tools that need
   external libraries declare a pip extra.
6. **Approval policy on the descriptor.** `STANDING` for read-only
   tools; `PER_CALL` for anything that touches the filesystem or
   network; `FORBIDDEN` for tools the registry refuses to register.
7. **Redaction.** Sensitive argument keys go in
   `ToolDescriptor.redacted_arg_names`; the audit log writes
   `"<redacted>"` for them.

### The three first-party tools

| Tool | Approval | Owns | Refuses |
|---|---|---|---|
| `search_well` | `STANDING` | `hybrid_search` → `text_search` fallback against the bound `BrunnrHandle`. Renders chunks with title / id / score / 240-char preview. | Empty query; unbound handle; out-of-range `k` (clamped to [1, 25]). |
| `read_local_file` | `PER_CALL` | Read a UTF-8 file (≤ 256 KiB) whose resolved path is under `$HOME`. | Symlinks that escape `$HOME`; the sandbox denylist (`~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, `~/.aws/`, `~/.kube/`, `~/.gnupg/`, `~/.password-store/`); directories; missing files; >256 KiB files. |
| `fetch_url` | `PER_CALL` | GET an http(s) URL via stdlib `urllib`. Returns body capped at 1 MiB with a `content-type:` header line. | Non-http(s) schemes; RFC1918 / loopback / link-local / multicast (unless `allow_private_addresses=true`); robots.txt disallow. |

### How tools are reached at runtime

In production the chain is:

1. **`ember chat`** with `config.tools.enabled: true`.
2. **`chat.py`** calls `import ember.tools` (side-effect register) and
   `search_well.bind_brunnr(brunnr, embedder)`.
3. **Munnr** passes the registered descriptors to Funi via
   `funi.complete_streaming(prompt, context, tools=...)`.
4. **Ollama** (or another tool-capable Funi) emits `tool_calls` in
   the final stream chunk.
5. **`chat.py`** validates arguments → resolves approval (per ADR
   0011 §2.4) → optionally prompts → calls the executor → audits →
   feeds the `ToolReply` into the next turn's context.

## Failure semantics

- The framework catches **every** exception from `_execute` and folds
  it into `ToolReply(error=...)`. A tool is allowed to raise.
- A tool can return `ToolReply(output="partial...", error="something
  went wrong")` — partial output + error is legal per ADR 0011 §2.1.
- The `read_local_file` and `fetch_url` sandboxes refuse cleanly with
  typed-error `ToolReply` (not exceptions) so the audit log records a
  proper "approved + refused-by-sandbox" entry rather than an
  uncaught exception trace.
- **No write semantics.** Slice 2 ships read-only tools. Write tools
  wait for a dedicated ADR per ADR 0013 §2.4.

## Limitations

- **No streaming tool replies.** Single-shot `ToolReply` only. A
  future ADR enables streaming for tools that need it (e.g. a large
  file reader, a log tailer).
- **No tool composition.** A tool cannot call another tool. Multi-step
  reasoning happens at the model layer: Funi proposes one tool call,
  sees the reply, proposes the next.
- **No per-tool retry.** If `read_local_file` fails because of a
  transient OSError, the model sees the error and decides whether to
  retry by issuing the call again.
- **No syscall sandbox.** Tools run in-process with Ember's full
  process privileges. Sandboxing is descriptor-level (each tool
  enforces its own constraints in its own code).
- **First three tools only.** Slice-2 first-party catalogue is
  intentionally small. The plugin framework that would let
  third-party tools register from operator-installed packages is
  deferred per ADR 0013 §2.7.
