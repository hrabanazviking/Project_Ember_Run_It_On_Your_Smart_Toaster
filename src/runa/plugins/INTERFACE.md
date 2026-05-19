# INTERFACE — `runa.plugins`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §9, `docs/plugins/PLUGIN_CONTRACT.md` (to be written before first third-party plugin lands).

## Purpose

Plugin loader, plugin sandbox, plugin discovery, plugin lifecycle. Third-party plugins themselves do not live in this repository — this subpackage is the machinery that finds them, validates them, loads them safely, and reports plugin failures without taking the agent down.

## Public surface

| Symbol | Purpose |
|---|---|
| `runa.plugins.loader.Loader` | The loader. Used by `runa.runtime` at start, and on operator `runa plugin install/remove/list`. |
| `runa.plugins.loader.Loader.discover(search_paths) -> list[PluginManifest]` | Find plugins on disk. |
| `runa.plugins.loader.Loader.load(manifest) -> LoadedPlugin` | Validate against the contract, instantiate inside the sandbox, register. |
| `runa.plugins.loader.Loader.unload(plugin_id)` | Quiesce and remove. |
| `runa.plugins.contract.PluginContract` | The plugin contract — base class third-party plugins inherit from. |
| `runa.plugins.sandbox.SandboxBoundary` | The boundary checks used at load time and per-call. |

## Invariants

- **A misbehaving plugin must never take the agent down.** This is checked by tests; if the sandbox leaks, that is a release-blocking bug.
- **Plugins are isolated from each other.** A plugin cannot import another plugin's modules.
- **Plugins have no access to `~/.runa/secrets/` or `~/.runa/identity/`** unless explicitly granted in operator config.
- **Plugin failures during a call return a typed error**, never an unhandled exception escaping into the kernel.
- **The plugin contract is versioned.** Old plugins receive a compatibility shim until major-version bump.

## Allowed callers

`runa.runtime` (for install/remove/list), `runa.services` (for runtime invocation through the registry).

## Allowed callees

`runa.schemas`, the narrow `runa.core` interfaces declared as the plugin surface.

## Failure semantics

Plugin load failure: log, do not load, surface via `runa doctor`. Plugin call failure: typed error, log, kernel decides whether to continue without the plugin. Plugin sandbox violation: refuse to load, quarantine the manifest, surface to operator.
