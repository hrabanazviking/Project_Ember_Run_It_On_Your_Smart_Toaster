---
codex_id: 27_PLUGIN_INTERFACE
title: Plugin Interface — Discovery Safety, Init Failure, Teardown Honesty
role: Auditor
layer: Interface
status: draft
hermes_source_refs:
  - hermes_cli/plugins.py:1-200
  - hermes_cli/plugins.py:125-200
  - gateway/hooks.py:64-145
  - plugins/spotify/plugin.yaml:1-14
  - SECURITY.md:154-168
ember_subsystem_targets: [Brunnr, Smiðja, Munnr]
cross_refs:
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 50_verification/54_SECURITY_REVIEW
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Plugin Interface — From a Verification Perspective

*Sólrún, narrow-eyed: a plugin system is the place where the agent agrees to run code it did not write. The interface that gates that decision is the most consequential interface in the codebase. Most projects design it as if it were a small dependency-injection helper. It is not. It is an attack surface and an evolution contract. I will treat it as both.*

Hermes's plugin system is one of the larger surfaces in the codebase, by Python LOC and by capability. 16+ shipped plugins, four discovery sources, ~15 lifecycle hook names, four kinds of registration, and a manifest format that has accumulated 22 platform-registry fields (per [[20_interface/25_GATEWAY_INTERFACE]] §7) plus a separate yaml-manifest format. This doc audits the *contract* — what a plugin must declare, what it can do, when it can fail, who notices.

## 1. The four discovery sources

`hermes_cli/plugins.py:1-33`:

> Discovers, loads, and manages plugins from four sources:
> 1. **Bundled plugins** – `<repo>/plugins/<name>/`
> 2. **User plugins**   – `~/.hermes/plugins/<name>/`
> 3. **Project plugins** – `./.hermes/plugins/<name>/` (opt-in via `HERMES_ENABLE_PROJECT_PLUGINS`)
> 4. **Pip plugins**     – packages that expose the `hermes_agent.plugins` entry-point group.
>
> Later sources override earlier ones on name collision, so a user or project plugin with the same name as a bundled plugin replaces it.

**Audit finding #1: shadowing is permitted and *intentional***. A user-installed plugin named `langfuse` will silently replace the bundled `observability/langfuse`. The operator who installed both does not see a conflict warning unless `HERMES_PLUGINS_DEBUG=1`.

**Audit finding #2: project-directory plugins are env-var-gated**, not config-gated. This is the right shape — running `cd untrusted-repo && ember chat` does not auto-load `./.hermes/plugins/`. Operator opt-in is explicit.

**Audit finding #3: pip-installed plugins have no manifest validation**. They are discovered via the `hermes_agent.plugins` entry-point group. Pip's entry-point mechanism runs arbitrary import-time code as soon as the package is installed. A malicious wheel installed accidentally (typo-squatting `hermes-agent-langfuse` vs `hermes_agent_langfuse`) is a supply-chain risk Hermes has not addressed at this interface; it lives in the `CONTRIBUTING.md` supply-chain section instead.

## 2. The manifest format

Each directory-based plugin must contain `plugin.yaml`. Sample (`plugins/spotify/plugin.yaml:1-14`):

```yaml
name: spotify
version: 1.0.0
description: "Native Spotify integration — 7 tools (playback, devices, queue, search, playlists, albums, library) using Spotify Web API + PKCE OAuth. Auth via `hermes auth spotify`. Tools gate on `providers.spotify` in ~/.hermes/auth.json."
author: NousResearch
kind: backend
provides_tools:
  - spotify_playback
  - spotify_devices
  - spotify_queue
  - spotify_search
  - spotify_playlists
  - spotify_albums
  - spotify_library
```

What the manifest **declares** (sampled across plugins): `name`, `version`, `description`, `author`, `kind`, `provides_tools`. Optionally also: `provides_platforms`, `provides_hooks`, `dependencies`, `enabled_by_default`, `requires_env`, `provider`.

What the manifest **does NOT declare** at runtime check:

- **What env vars / credentials it will read.** Documented in the docstring (`plugins/observability/langfuse/__init__.py:11-23`), not in the manifest. A reviewer must read code, not yaml.
- **What network hosts it will reach.** Implied by name; not declared.
- **What hooks it will register.** `provides_hooks` is sometimes present, sometimes not. The actual registration happens in `register(ctx)`.
- **What modules it will import.** It will import whatever its `__init__.py` does. Including transitively.
- **Whether it spawns subprocesses or threads.** Not declared.
- **Whether it opens file descriptors that survive `unregister()`.** Not declared.

**Audit finding #4: the manifest is informational, not contractual**. Nothing the runtime checks against the manifest constrains what the plugin can do. The manifest is for the human reviewer.

## 3. The registration contract

Each directory plugin must expose `register(ctx)` in its `__init__.py`. `PluginContext` (see `hermes_cli/plugins.py`) is the API surface:

- `ctx.register_tool(name, fn, schema, ...)` — adds a tool (delegates to `tools.registry.register`).
- `ctx.register_hook(name, fn)` — subscribes to one of `VALID_HOOKS` (see §4).
- `ctx.register_platform(entry)` — adds a `PlatformEntry` (see [[20_interface/25_GATEWAY_INTERFACE]] §7).
- `ctx.register_web_search_provider(...)`, `ctx.register_video_gen_provider(...)`, etc. — narrow registration helpers.

The plugin runs `register(ctx)` once at load time. The registration is the entire contract. If `register` raises, the plugin is partially loaded (whatever it registered before the exception remains). If `register` returns without error, the plugin is fully loaded.

**Audit finding #5: there is no `unregister()`.** Once a tool is registered, it stays for the life of the process. A plugin cannot be "disabled" mid-process without restart. The operator's `/disable plugin foo` (if such existed) would be a no-op at runtime.

**Audit finding #6: partial-load state is reachable.** If `register` raises after registering 2 of 3 tools, the agent runs with 2 tools registered and a partial plugin. Operator sees a warning log; the agent does not refuse to start.

**Audit finding #7: there is no init/teardown distinction**. A plugin that wants to start a background thread (e.g. langfuse's batch flusher) must do so inside `register`. There is no separate `init()` after the agent is ready, no separate `teardown()` at process exit. The thread runs forever or until process death.

## 4. The hook surface

`hermes_cli/plugins.py:128-168` declares `VALID_HOOKS`:

```python
VALID_HOOKS: Set[str] = {
    "pre_tool_call",
    "post_tool_call",
    "transform_terminal_output",
    "transform_tool_result",
    "transform_llm_output",
    "pre_llm_call",
    "post_llm_call",
    "pre_api_request",
    "post_api_request",
    "on_session_start",
    "on_session_end",
    "on_session_finalize",
    "on_session_reset",
    "subagent_stop",
    "pre_gateway_dispatch",
    "pre_approval_request",
    "post_approval_response",
}
```

That's 17 hooks. A subset modifies in-flight data:

- `transform_terminal_output` — the *output of the terminal tool* is rewritten by the plugin before the agent sees it.
- `transform_tool_result` — any tool result.
- `transform_llm_output` — the model's response text. "First non-None string wins."
- `pre_gateway_dispatch` — the *inbound message* can be rewritten or dropped.

The trust implication: **a plugin can rewrite the agent's own outputs, the model's responses, and inbound user messages.** A misbehaving plugin can make the agent appear to say things it did not, or make the model appear to say things it did not, or change what the operator typed.

This is documented (`hermes_cli/plugins.py:131-153` comments). It is also exactly what `SECURITY.md:154-168` is talking about when it says:

> "Plugins load into the agent process and run with full agent privileges: they can read the same credentials, call the same tools, register the same hooks, and import the same modules as anything shipped in-tree. The boundary for third-party plugins is operator review before install..."

**Audit verdict: this is the right stance, named explicitly**. It is also exactly the *opposite* of safe-by-default. Ember's Vow of Modular Authorship asks for failure isolation, which the manager provides via try/except. It does not ask for *trust isolation*, which neither Hermes nor Ember can provide without OS-level boundaries.

## 5. Hook dispatch and "first non-None wins"

The `transform_*` hooks have an explicit ordering rule: "first non-None string wins" (`hermes_cli/plugins.py:133-136`). The other hooks are observers. The `pre_gateway_dispatch` hook returns a dict that influences dispatch:

```python
# hermes_cli/plugins.py:146-152
# Gateway pre-dispatch hook. Fired once per incoming MessageEvent
# after the internal-event guard but BEFORE auth/pairing and agent
# dispatch. Plugins may return a dict to influence flow:
#   {"action": "skip",    "reason": "..."}  -> drop message (no reply)
#   {"action": "rewrite", "text": "..."}    -> replace event.text, continue
#   {"action": "allow"}  /  None             -> normal dispatch
```

**Audit finding #8: the "first non-None wins" ordering is not deterministic across plugin loads**. The order depends on (a) discovery order across sources, (b) hash ordering for entry-point names, (c) which source was last to register. Two operators with the same set of plugins can see different transform results.

**Audit finding #9: a `transform_llm_output` plugin that crashes mid-transform leaves the agent in an unspecified state**. The docstring says "First non-None string wins." If the first plugin raises, does the next plugin run? Code reading suggests yes (per the `try/except` pattern Hermes uses elsewhere); the docstring does not say.

## 6. Dependency declaration honesty

Plugins can declare `dependencies` in `plugin.yaml`. Sampled across `plugins/*/plugin.yaml`:

- Some plugins declare their pip extras.
- Many do not.
- The `try: import x except ImportError: x = None` pattern (`plugins/observability/langfuse/__init__.py:38-41`) is the runtime fallback.

**Audit finding #10: dependency declarations are aspirational, not enforced**. A plugin loads even if its `dependencies` are missing. The `try/except ImportError` pattern at the top of `__init__.py` makes the plugin "inert" if its SDK is missing, but it still consumes a slot in the registry, still appears in `hermes plugins list`, and still increases startup time.

**Audit finding #11: the manifest's `dependencies` field is not cross-checked against `requires_env`**. A plugin that needs both `LANGFUSE_PUBLIC_KEY` and the `langfuse` pip package can declare one and forget the other. Operator gets a runtime warning, not a startup refusal.

## 7. The hooks subsystem (separate from plugins, almost)

`gateway/hooks.py:64-145` is the *event hook* loader, distinct from the *plugin hook* registry above. Event hooks live in `~/.hermes/hooks/<name>/` and contain `HOOK.yaml` + `handler.py`. They fire on `agent:start`, `session:end`, etc.

```python
# gateway/hooks.py:115-122
module_name = f"hermes_hook_{hook_name}"
spec = importlib.util.spec_from_file_location(module_name, handler_path)
# ...
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
try:
    spec.loader.exec_module(module)
except Exception:
    sys.modules.pop(module_name, None)
    raise
```

`exec_module` runs the handler's top-level code. **Audit finding #12: the file-on-disk → exec_module path is identical to "run any script in `~/.hermes/hooks/`"**. There is no signature check, no checksum, no sandboxing. If a user account is compromised and the attacker drops a `handler.py` in `~/.hermes/hooks/`, the next `ember chat` runs it.

The mitigation Hermes documents (`SECURITY.md:148-153`):

> "Skills Guard scans installable skill content for injection patterns. It is a review aid; the boundary for third-party skills is operator review before install. Reviewing a skill means reading its Python code and scripts, not just its SKILL.md description — skills execute arbitrary Python at import time."

This applies equally to hooks. The boundary is operator review. **There is no other boundary.**

## 8. Teardown contract

Two questions:

### 8.1 Process-exit teardown

A plugin that started a thread, opened a socket, allocated GPU memory, or holds a file lock — what happens when the agent exits?

Hermes does not call any teardown method on plugins. Process death cleans up file descriptors, network sockets, and threads that are daemon-threads. A plugin that started a non-daemon thread keeps the process alive past the user's exit intent. A plugin that opened a lock file on a network filesystem can wedge a *future* agent start.

**Audit finding #13: there is no plugin teardown lifecycle**. The hooks `on_session_end` and `on_session_finalize` fire per-session, not per-process. The Memory Provider has `shutdown()` (per [[20_interface/24_MEMORY_INTERFACE]] §5), but plugins-as-a-whole do not.

### 8.2 Session-rotation teardown

When the operator runs `/new`, the agent rotates `session_id`. The plugin's `on_session_reset` hook fires. Module-level state (cached credentials, open connections, request counters) is NOT reset. **Audit finding #14: per-session state survives session rotation by default**. A plugin that intended otherwise must explicitly reset on `on_session_reset`. Most do not.

This is the same antipattern named in [[20_interface/26_TUI_BACKEND_INTERFACE]] §1.4 — module-singleton state surviving session boundaries.

## 9. Versioning

The manifest declares `version: 1.0.0`. The plugin-loader does not check this against any required minimum. Hermes has no `min_hermes_version` field in `plugin.yaml`, and no `plugin_protocol_version` for the `register(ctx)` contract.

**Audit finding #15: the plugin contract is unversioned**. A plugin built against Hermes v0.10 that calls `ctx.register_tool` with the v0.10 signature continues to "work" against v0.14 — until the day `register_tool`'s signature changes. There is no compatibility shim, no warning, no refusal.

## 10. What the contract says vs what it should say

Strong contracts on this surface:

- **`VALID_HOOKS` is a closed set** (`hermes_cli/plugins.py:128-168`). A plugin that registers an unknown hook gets refused. Good.
- **`provides_tools` is informational** but `ctx.register_tool` is the binding act. The runtime is honest about what is actually registered.
- **`exec_module` on import failure pops `sys.modules`** (`gateway/hooks.py:120-122`) so a partial load does not leave a half-loaded module. Good.

Weak contracts:

- **No teardown** (per §8).
- **No unregister** (per §3).
- **No version** (per §9).
- **No declarative declared-capabilities** beyond yaml strings (per §2).
- **No isolated sub-interpreter** — a plugin shares `sys.modules` with the agent. A plugin that imports `numpy 1.x` collides with a plugin that imports `numpy 2.x`.
- **No CPU/memory budget** per plugin.

## 11. Comparison to Ember's current shape

Ember's slice-2 surface has no plugins. `src/ember/plugins/` is scaffold (per `UNWIRED_INVENTORY` §5.4 / ADR 0013 §3). The first plugin contract Ember writes will inherit Hermes's lessons or invent its own.

Ember's existing surfaces use **Protocols, not ABCs**, with **typed-value-over-exception** at every boundary (per ADR 0007 §2.2). Two design moves that directly improve over Hermes's plugin shape:

- A `Protocol`-based plugin interface can be statically checked. `mypy --strict` will refuse a plugin that does not match the shape.
- A typed `PluginLoadResult` union (`Loaded(plugin)`, `MissingDependency(name)`, `IncompatibleVersion(plugin_min, hermes_actual)`, `LoadFailed(reason, traceback)`) replaces the silent-warning pattern Hermes uses.

## What This Means for Ember

**Subsystems affected:** Brunnr (storage plugins for new backends), Smiðja (ingest plugins for new content sources), Munnr (renderer plugins for new surfaces). Possibly Funi (runtime plugins for new local-model engines) and Strengr (transport plugins).

**Vows touched:**

- **Vow of Modular Authorship** — plugins are the test of this Vow.
- **Vow of Smallness** — every loaded plugin is RAM and import-time cost on the Pi. The contract must support *not* loading.
- **Vow of Honest Memory** — plugins that rewrite agent output (Hermes's `transform_llm_output`) violate this Vow if Ember adopts them; she must NOT.
- **Vow of Public-Friendliness** — operator must see which plugins are loaded, which failed, and *why*, in plain language.

**Concrete proposals for the Ember plugin contract:**

1. **Define `EmberPlugin` as a `Protocol`**, not an ABC. Methods: `name`, `version`, `protocol_version: int`, `register(ctx) -> RegisterResult`, `teardown() -> None`. Static check via mypy.
2. **Adopt `RegisterResult` as a typed union.** `Registered(items)`, `MissingDependency(name)`, `IncompatibleVersion(min, actual)`, `MissingCredential(env_var)`, `LoadFailed(reason)`. No silent warnings; every outcome is operator-visible via `ember plugins status`.
3. **Refuse partial-load.** If `register` raises after registering some items, the loader rolls back the items it registered and reports `LoadFailed`. The agent runs with the plugin absent, not half-loaded.
4. **Plugin teardown is mandatory.** `teardown()` is called on process exit (atexit), on `/reset`, and on explicit `ember plugins disable foo`. A plugin that wants persistent state writes it to disk inside `teardown`, never relies on next-start module-level singleton.
5. **One discovery source by default.** `~/.ember/plugins/<name>/` only. Pip entry-points are opt-in via `EMBER_ENABLE_PIP_PLUGINS=1`. Project plugins (`./.ember/plugins/`) are opt-in per the same pattern as Hermes — but with an explicit warning banner at startup.
6. **Manifest is contractual.** `requires_env: [...]` is checked at load; missing env → `MissingCredential`. `requires_pip: [...]` is checked at load; missing → `MissingDependency`. The manifest is the truth; the runtime refuses to load a plugin whose runtime behavior contradicts its manifest.
7. **Version the protocol.** `protocol_version: int` mandatory. Loader refuses any plugin where `protocol_version < MIN_SUPPORTED or > MAX_SUPPORTED`.
8. **No `transform_llm_output`-like hook.** Ember's Vow of Honest Memory rules this out. Plugins may *observe* model output (for logging, like langfuse) but never *rewrite* it. The model said what it said.
9. **No `pre_gateway_dispatch` rewrite.** Same vow. Plugins may observe or refuse, never silently rewrite.
10. **Operator-visible plugin state.** `ember plugins status` shows every plugin, its load result, its memory footprint, its open file descriptors. The operator can answer "what is running in this process?" without reading code.
11. **Closed hook set, enforced at load.** Hermes's `VALID_HOOKS` is the right shape; Ember's set should be *smaller* (Ember's surface is smaller).
12. **No `exec_module` of unmanifested files.** Every loaded module must come from a directory that has a valid manifest. A stray `.py` in `~/.ember/plugins/` is ignored, not imported.
13. **Plugin sandboxing posture documented.** Mirror `SECURITY.md`'s scope clarity. Ember plugins run with full agent privilege; the boundary is operator review. State this in the user-facing docs.

Cross-link with [[50_verification/54_SECURITY_REVIEW]] §4 (plugin trust model) and [[50_verification/52_ANTIPATTERN_CATALOG]] entries "no-teardown-lifecycle", "partial-load-survives", "unversioned-extension-point".

A plugin system is the agent's promise that its boundaries are real. Hermes is honest about which boundaries are not real. Ember should be honest too — and where she can do better than Hermes (Protocols, typed results, mandatory teardown), she should.
