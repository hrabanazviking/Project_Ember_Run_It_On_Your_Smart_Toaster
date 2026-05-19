# 44 — Plugin Architecture Patterns

**Category:** Architecture Patterns
**Runa relevance:** `runa.plugins/` (ADR-0002 §D-2.5), MCP server integration, third-party extension
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A *plugin architecture* lets external code extend an application without modifying the application itself. Plugins discover, load, register their capabilities; the application calls them through known interfaces. Done well, plugins decouple core functionality from extensions, enable a third-party ecosystem, and reduce churn in the main codebase.

ADR-0002 §D-2.5 commits Runa to a four-mode plugin system (in-process trusted, in-process light, subprocess, WASM). [[37-plugin-sandboxing]] in the research corpus covers the *isolation* side. This doc covers the *Python implementation* — how plugins are discovered, loaded, registered, and called.

## 2. Technique / mechanism

**Three discovery mechanisms:**

### 1. Entry points (the standard Python way)

```toml
# pyproject.toml of a plugin package
[project.entry-points."runa.plugins"]
my_plugin = "my_package.plugin:MyPlugin"
```

```python
# Application code: discover plugins
from importlib.metadata import entry_points

for ep in entry_points(group="runa.plugins"):
    plugin_class = ep.load()
    plugin_instance = plugin_class()
    register(plugin_instance)
```

Plugins are *pip-installable*. Discovery via the standard Python packaging machinery. No custom config.

### 2. Filesystem discovery

```python
def discover_plugins(plugin_dir: Path) -> list[PluginManifest]:
    """Scan a directory for plugin manifests."""
    plugins = []
    for manifest_path in plugin_dir.glob("*/plugin.json"):
        with open(manifest_path) as f:
            manifest = PluginManifest(**json.load(f))
        plugins.append(manifest)
    return plugins
```

User drops a folder containing a manifest and code into `~/.runa/plugins/`. Application picks it up at start.

### 3. Configuration listing

```yaml
# config/runa.yaml
plugins:
  enabled:
    - name: "my_plugin"
      source: "package:my_package.plugin:MyPlugin"
    - name: "another"
      source: "file:/home/user/plugins/another/"
```

Explicit list in config. Simple; user has full control.

**The contract:**

```python
from typing import Protocol

class PluginContract(Protocol):
    plugin_id: str
    version: str
    capabilities_required: list[str]
    
    def initialize(self, host: "PluginHost") -> None: ...
    def call(self, method: str, args: dict) -> dict: ...
    def shutdown(self) -> None: ...

class PluginHost(Protocol):
    """The narrow API plugins can call back into."""
    def log(self, msg: str) -> None: ...
    def request_tool(self, tool_id: str, args: dict) -> dict: ...
    def emit_event(self, event_type: str, data: dict) -> None: ...
```

**Loader skeleton:**

```python
class PluginLoader:
    def __init__(self):
        self._plugins: dict[str, LoadedPlugin] = {}
    
    def load(self, manifest: PluginManifest) -> LoadedPlugin:
        # Validate manifest
        # Pick isolation strategy (per ADR-0002 §D-2.5)
        strategy = self._strategy_for(manifest.isolation_mode)
        
        # Instantiate via strategy
        instance = strategy.load(manifest)
        
        # Verify it satisfies the contract
        assert isinstance(instance, PluginContract)
        
        # Initialize
        instance.initialize(self._host_for_plugin(manifest))
        
        # Register
        loaded = LoadedPlugin(
            manifest=manifest,
            instance=instance,
            strategy=strategy,
        )
        self._plugins[manifest.plugin_id] = loaded
        return loaded
    
    def unload(self, plugin_id: str) -> None:
        plugin = self._plugins.pop(plugin_id)
        plugin.instance.shutdown()
        plugin.strategy.unload(plugin)
```

**Plugin manifest:**

```python
class PluginManifest(BaseModel):
    plugin_id: str
    version: str
    name: str
    description: str
    author: str
    capabilities_required: list[str]   # what host APIs it needs
    isolation_mode: Literal["in_proc_trusted", "in_proc_light", "subprocess", "wasm"]
    entry_point: str  # "package.module:ClassName" or path
```

**Host API (the narrow surface plugins can use):**

```python
class PluginHost:
    """What a plugin can call back into Runa."""
    def __init__(self, plugin_id: str, capabilities: set[str]):
        self.plugin_id = plugin_id
        self.capabilities = capabilities
    
    def log(self, msg: str) -> None:
        logger.info("[plugin %s] %s", self.plugin_id, msg)
    
    def request_tool(self, tool_id: str, args: dict) -> dict:
        if tool_id not in self.capabilities:
            raise PluginPermissionError(f"plugin {self.plugin_id} can't use {tool_id}")
        return tool_dispatcher.dispatch(tool_id, args)
```

Capability-checked. Plugins declare what they need; the host grants only what was approved.

**Isolation strategies (per ADR-0002 §D-2.5):**

```python
class InProcessTrustedStrategy:
    def load(self, manifest):
        module = importlib.import_module(manifest.entry_point)
        return module.PluginClass()

class SubprocessStrategy:
    def load(self, manifest):
        proc = subprocess.Popen([sys.executable, "-m", "runa.plugins.runner", str(manifest)],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return SubprocessProxy(proc)

class WasmStrategy:
    def load(self, manifest):
        import wasmtime
        engine = wasmtime.Engine()
        store = wasmtime.Store(engine)
        module = wasmtime.Module.from_file(engine, manifest.wasm_path)
        return WasmProxy(module, store)
```

The strategy abstraction means plugin code is the same regardless of mode; the loader picks.

**Hot reload (advanced):**

```python
def reload_plugin(plugin_id: str):
    """Replace a running plugin with new code."""
    old = loader.unload(plugin_id)
    new_manifest = discover_again(plugin_id)
    loader.load(new_manifest)
```

Useful for development; risky in production.

## 3. Key works / libraries

- **`stevedore`** — github.com/openstack/stevedore. Plugin loader used by OpenStack.
- **`pluggy`** — github.com/pytest-dev/pluggy. Plugin system behind pytest. Hook-spec based.
- **`importlib.metadata`** — stdlib entry-point discovery.
- **`importlib`** — stdlib dynamic import.
- **Plugin patterns from VS Code, Sublime, Chrome extensions** — industry reference designs.
- **OpenAI / Anthropic MCP** — modelcontextprotocol.io. Standardised tool-plugin protocol.

## 4. Pitfalls and gotchas

- **Plugins importing stdlib differently** can produce surprise behaviour.
- **Plugin authors as adversaries.** Even trusted plugins can have bugs. Sandbox per ADR-0002 §D-2.5.
- **Capability creep.** Plugins request more capabilities; operator approves without thinking.
- **Plugin discovery slowness.** Scanning many directories at startup hurts. Cache.
- **Plugin schema versioning.** Plugin contract evolves; old plugins break. Versioning + compatibility shims.
- **Multiple plugins implementing the same hook.** Order matters; semantics get muddy.
- **Memory leaks from misbehaving plugins.** Periodically restart if subprocess.

## 5. Applicability to Runa

For **`runa.plugins.loader`**:

- Default: entry-point discovery via `importlib.metadata`.
- Alternative: filesystem discovery for `~/.runa/plugins/`.
- Config-based override always wins.

For **isolation strategies per ADR-0002 §D-2.5**:

- All four implemented behind a common `IsolationStrategy` Protocol.
- Operator config selects per plugin.

For **plugin contract**:

- Documented in `docs/plugins/PLUGIN_CONTRACT.md`.
- Versioned. Backward compatibility for at least one prior version.

For **capability system**:

- Plugin manifest declares `capabilities_required`.
- Operator approves at install time.
- Host enforces at call time.

For **MCP server integration**:

- MCP servers ARE plugins in the broad sense. Adapt the loader to launch / subscribe to MCP servers as a strategy.

What to avoid:

- Don't ship without strict capability checking.
- Don't make the plugin API broader than necessary.
- Don't allow plugins to monkey-patch core.
- Don't let plugin failures take down the agent.

## 6. Open questions

- **Plugin registry.** A public registry of vetted plugins (a la Homebrew, npm) is a long-term direction.
- **Cross-plugin coordination.** Plugins that depend on other plugins → load ordering.
- **Plugin signing / verification.** Cryptographic signing of plugins to verify provenance.

## 7. References (curated)

- importlib.metadata stdlib docs.
- github.com/pytest-dev/pluggy.
- github.com/openstack/stevedore.
- modelcontextprotocol.io — MCP spec.
- Companion docs: [[37-plugin-sandboxing]] (research corpus), [[28-protocol-classes]], [[42-hexagonal-architecture]].
