---
codex_id: 17_PLUGINS_EXTENSIBILITY
title: Plugins — Where the System Asks to Be Extended
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - hermes_cli/plugins.py:1-120
  - hermes_cli/plugins.py:200-400
  - hermes_cli/plugins.py:230-280
  - plugins/__init__.py
  - plugins/memory/__init__.py:1-40
  - plugins/observability/langfuse/plugin.yaml
  - plugins/disk-cleanup/plugin.yaml
  - plugins/spotify/plugin.yaml
  - plugins/google_meet/plugin.yaml
  - plugins/teams_pipeline/plugin.yaml
  - plugins/hermes-achievements/README.md
  - plugins/browser/browser_use/
  - plugins/browser/browserbase/
  - plugins/browser/firecrawl/
  - plugins/web/exa/
  - plugins/web/searxng/
  - plugins/web/tavily/
  - plugins/image_gen/openai/
  - plugins/image_gen/xai/
  - plugins/video_gen/fal/
  - plugins/context_engine/__init__.py
  - plugins/example-dashboard/dashboard/
  - plugins/platforms/google_chat/
  - plugins/platforms/line/
  - plugins/platforms/teams/
  - plugins/kanban/dashboard/
  - plugins/kanban/systemd/
  - providers/__init__.py:1-100
  - AGENTS.md:487-585
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/13_TOOLS_SUBSYSTEM
  - 10_domain/15_PROVIDERS_MULTI_MODEL
  - 10_domain/19_BOUNDARY_LAW
  - 20_interface/27_PLUGIN_INTERFACE
---

# Plugins — Where the System Asks to Be Extended

*— Rúnhild Svartdóttir, Architect*

> *A system's pluggability is its humility. To declare the seams where extension is welcome is to admit that the system cannot anticipate every need. The architect's job is to make those seams generous enough to encourage and disciplined enough to keep the system whole.*

`plugins/` is sixteen trees and one of the most heavily-trafficked surfaces in Hermes. Plugins add: memory backends, model providers, context engines, image-generation backends, video-generation backends, web-search backends, browser backends, observability sinks, messaging-platform adapters, dashboards, achievement systems, smart-home integrations, music-player integrations, file-cleanup automation, meeting transcription, and arbitrary user-authored tools.

The mental model: **four discovery sources, five plugin *kinds*, three load-order rules, one `PluginContext` API.** That's what holds it together. (Imperfectly. We'll get to the imperfections.)

---

## 1. The Sixteen Plugin Trees

What sits under `plugins/`:

| Tree | Kind | Files | What it is |
|---|---|---|---|
| `browser/` | backend | 3 trees (`browser_use/`, `browserbase/`, `firecrawl/`) | Alternative browser-automation backends |
| `context_engine/` | exclusive | bare `__init__.py` | Discovery path for context-engine plugins |
| `disk-cleanup/` | standalone | `__init__.py` + `disk_cleanup.py` + `plugin.yaml` | Auto-tracks ephemeral files, cleans them up via hooks |
| `example-dashboard/` | standalone | `dashboard/` | Reference dashboard plugin |
| `google_meet/` | standalone | 8 files | Join Google Meet, transcribe captions, speak via TTS |
| `hermes-achievements/` | standalone | LICENSE + README + `dashboard/` + `docs/` + `tests/` | Vendored from `@PCinkusz/hermes-achievements`; gamification badges |
| `image_gen/` | backend | 3 trees (`openai/`, `openai-codex/`, `xai/`) | Image-generation backends |
| `kanban/` | n/a | `dashboard/` + `systemd/` | Kanban dashboard SPA + systemd unit |
| `memory/` | exclusive | 9 trees (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb, +`__init__.py`) | Memory providers — one active at a time |
| `model-providers/` | model-provider | 30+ trees | Inference backend profiles (covered in `[[10_domain/15_PROVIDERS_MULTI_MODEL]]`) |
| `observability/` | standalone | `langfuse/` | Tracing sink (Langfuse) |
| `platforms/` | platform | 5 trees (`google_chat/`, `irc/`, `line/`, `simplex/`, `teams/`) | Additional messaging platforms beyond the bundled set |
| `spotify/` | backend | 4 files | Spotify Web API tools (7 tools, PKCE OAuth) |
| `teams_pipeline/` | standalone | 9 files | Microsoft Teams meeting-summary pipeline |
| `video_gen/` | backend | 2 trees (`fal/`, `xai/`) | Video-generation backends |
| `web/` | backend | 8 trees (brave_free, ddgs, exa, firecrawl, parallel, searxng, tavily, xai) | Web-search backends |

Roughly **16 trees containing ~75 individual plugins**, plus the user's own `~/.hermes/plugins/<name>/` tree.

---

## 2. The Four Discovery Sources

`hermes_cli/plugins.py:1-30` enumerates them:

1. **Bundled plugins** at `<repo>/plugins/<name>/`
2. **User plugins** at `~/.hermes/plugins/<name>/`
3. **Project plugins** at `./.hermes/plugins/<name>/` (opt-in via `HERMES_ENABLE_PROJECT_PLUGINS`)
4. **Pip plugins** — packages exposing the `hermes_agent.plugins` entry-point group

**Override rule:** later sources override earlier ones on name collision. A user plugin with the same name as a bundled plugin *replaces* it. A pip plugin overrides everything. This is **last-writer-wins**, same as the model-provider discovery (`[[10_domain/15_PROVIDERS_MULTI_MODEL]]`).

Each directory plugin must contain:
- `plugin.yaml` — manifest
- `__init__.py` — exposes a `register(ctx: PluginContext)` function

Pip plugins skip the directory; the entry point goes straight to a module.

---

## 3. The Five Plugin Kinds

`hermes_cli/plugins.py:230` declares the kinds:

```python
_VALID_PLUGIN_KINDS: Set[str] = {"standalone", "backend", "exclusive", "platform", "model-provider"}
```

| Kind | Semantics | Examples |
|---|---|---|
| `standalone` (default) | Hooks/tools of its own; opt-in via `plugins.enabled` | disk-cleanup, hermes-achievements, observability/langfuse, google_meet, teams_pipeline |
| `backend` | Pluggable backend for an existing core tool. Built-in (bundled) backends auto-load; user-installed gated by `plugins.enabled` | spotify (Spotify tool backend), image_gen/openai (image_generate backend), web/searxng (web_search backend), video_gen/fal |
| `exclusive` | Category with exactly one active provider. Selection via `<category>.provider` config; the category's own discovery system loads, general scanner skips | memory (one provider chosen via `memory.provider`), context_engine |
| `platform` | Gateway messaging platform adapter. Bundled platform plugins auto-load; user-installed gated by `plugins.enabled` | platforms/google_chat, platforms/line, platforms/teams |
| `model-provider` | Inference provider profile. Has its own discovery system in `providers/__init__.py`; general scanner skips | All 30+ entries under `plugins/model-providers/` |

The kinds matter because they decide *load timing* and *opt-in policy*. Bundled `standalone` plugins do NOT auto-load — the user must enable them. Bundled `backend` plugins DO auto-load (the user already chose their image-gen provider via config; the backend is just the wiring). Bundled `platform` plugins DO auto-load (the user expects every shipped platform to be available).

---

## 4. The `PluginManifest` Dataclass

`hermes_cli/plugins.py:233-267` shows the manifest shape:

```python
@dataclass
class PluginManifest:
    name: str
    version: str = ""
    description: str = ""
    author: str = ""
    requires_env: List[Union[str, Dict[str, Any]]] = field(default_factory=list)
    provides_tools: List[str] = field(default_factory=list)
    provides_hooks: List[str] = field(default_factory=list)
    source: str = ""        # "user", "project", or "entrypoint"
    path: Optional[str] = None
    kind: str = "standalone"
    key: str = ""           # Registry key (path-derived)
```

The `key` (`hermes_cli/plugins.py:262-267`) is path-derived: a flat plugin at `plugins/disk-cleanup/` gets key `disk-cleanup`; a nested category plugin at `plugins/image_gen/openai/` gets key `image_gen/openai`. The two-level keying is essential for the backend kind.

The `requires_env` field is rich (`hermes_cli/plugins.py:241`) — can be a bare string or a dict with metadata. From `plugins/observability/langfuse/plugin.yaml`:

```yaml
requires_env:
  - HERMES_LANGFUSE_PUBLIC_KEY
  - HERMES_LANGFUSE_SECRET_KEY
```

When a plugin's requires_env is a dict (rather than a string), it gets auto-populated into `OPTIONAL_ENV_VARS` in `hermes_cli/config.py` so the setup wizard surfaces proper descriptions, prompts, password flags, and URLs (per `gateway/platforms/ADDING_A_PLATFORM.md:40-44`).

---

## 5. The `PluginContext` API

The `ctx` passed to `plugin.register(ctx)` is `hermes_cli/plugins.py:287-...`. Methods I'd highlight:

### 5.1 `ctx.register_tool(...)` (`hermes_cli/plugins.py:317-355`)

Registers a tool in the global registry **and** tracks it as plugin-provided. Optional `override=True` swaps an existing built-in. The `_manager._plugin_tool_names` set tracks all plugin tools for later cleanup if a plugin is disabled.

### 5.2 `ctx.register_hook(name, callback)`

Registers a lifecycle hook. Valid hooks (per `AGENTS.md:499-503`):
- `pre_tool_call` / `post_tool_call`
- `pre_llm_call` / `post_llm_call`
- `pre_api_request` / `post_api_request`
- `on_session_start` / `on_session_end`

Hooks are invoked from `model_tools.py` (tool calls) and `run_agent.py` (lifecycle).

### 5.3 `ctx.register_cli_command(name, help, setup_fn, handler_fn)`

Plugins can register `hermes <pluginname> <subcmd>` argparse subcommands. The plugin's argparse tree is wired into `hermes_cli/main.py` at startup. **No change to main.py required.** Important.

### 5.4 `ctx.register_platform(...)` (gateway plugins)

Registers a `BasePlatformAdapter` subclass with the gateway. Auto-wires config parsing, user authorization, cron delivery, send_message routing, system prompt hints, status display.

### 5.5 `ctx.inject_message(content, role)` (`hermes_cli/plugins.py:357-383`)

Plugin can inject a message into the active conversation. If the agent is idle, it starts a new turn; if the agent is mid-turn, it interrupts. This is how the `hermes-achievements` plugin announces a badge unlock ("You earned the Night Owl achievement!") without the user typing.

### 5.6 `ctx.llm` (`hermes_cli/plugins.py:296-313`)

Lazy facade for `PluginLlm` (`agent/plugin_llm.py`). Lets trusted plugins run host-owned chat or structured completions against the user's active model and auth *without* bringing their own provider keys. Plugins can also override capability (model, agent id, auth profile) via `plugins.entries.<plugin_id>.llm.*` config keys.

**This is a genuinely good idea.** The plugin doesn't need its own API key; it uses Hermes's. Saves duplicating credentials; gives the user control over which plugins can call the LLM.

---

## 6. The Opt-In Allow-List

`hermes_cli/plugins.py:200-223` defines the `plugins.enabled` config key:

- **Missing or malformed** — opt-in default; first `migrate_config` populates with a grandfathered set
- **Empty list** — nothing loads
- **Concrete list** — only these load

Bundled `standalone` plugins are NOT auto-loaded. The user has to either run `hermes plugins enable disk-cleanup` (writes to config.yaml) or check the box in `hermes plugins` (the curses UI).

This is the **Vow of Public-Friendliness** colliding with the **Vow of Modular Authorship**: the user is in control of which third-party-ish code runs in their agent. Some plugins (the achievements one) get vendored *into* the repo and auto-load anyway — these are first-party.

---

## 7. The Plugin Loading Pipeline

The full lifecycle for one plugin (simplified):

1. **`discover_plugins()`** is called (idempotent; once per process). Triggered as side effect of importing `model_tools.py`.
2. Each discovery source is scanned; manifests are parsed; the registry is populated.
3. For each manifest:
   - Check `kind` — does the general scanner load it? (memory + model-provider have their own systems.)
   - Check `plugins.enabled` — is the user opting in?
   - Check `requires_env` — are required env vars set?
4. For accepted plugins:
   - Import the `__init__.py`
   - Call `register(ctx)` with a fresh `PluginContext`
   - Capture any registered tools, hooks, commands
   - Store in `LoadedPlugin` (`hermes_cli/plugins.py:270-281`)
5. Errors are logged but do not abort. A failed plugin shows in `hermes plugins` as `error: <message>`.

The error-isolation behavior is *crucial*. A bad plugin should NOT crash Hermes; it should fail to load and be visible in the plugin status.

---

## 8. The Three Parallel Discoveries (The Leak)

Hermes has *three* plugin discovery systems running in parallel:

1. **General** — `hermes_cli/plugins.py`. The full thing described above.
2. **Memory** — `plugins/memory/__init__.py`. Separate scanner; selects one active provider via `memory.provider` config.
3. **Model-provider** — `providers/__init__.py`. Separate scanner; lazy-discovers profiles; last-writer-wins override.

Each has different:
- Discovery code (three implementations)
- Manifest expectations (the model-provider scanner uses a heuristic if `kind:` is missing)
- Override semantics
- Load-timing (memory is discovered at agent init; model-provider at first `get_provider_profile()`)
- Override behavior (memory: bundled wins over user; model-provider: user wins over bundled)

**This is the largest pluggability boundary leak in Hermes.** A new contributor writing a "memory plugin" with the general manifest will silently fail. A contributor writing a "model-provider" plugin with the general directory layout will also silently fail.

The redemption: each system *works*. The pattern is just not unified. For Ember, this is the lesson — **one plugin-discovery contract, multiple `kind`s**.

---

## 9. Plugin Categories Worth Studying

### 9.1 `plugins/observability/langfuse/`

Pure hook-only plugin. No tools. Just sinks for `pre_api_request`, `post_api_request`, `pre_llm_call`, `post_llm_call`, `pre_tool_call`, `post_tool_call`. Sends spans to Langfuse. The plugin file is tiny because the hook API does the heavy lifting.

### 9.2 `plugins/disk-cleanup/`

Hook-only plugin that subscribes to `post_tool_call` and `on_session_end`. Tracks files created during the session in a sidecar log; on session end, classifies them (test outputs? cron logs? temp scripts?) and offers to clean up. **No agent action required.** The plugin is operating *around* the agent, not as a tool.

### 9.3 `plugins/spotify/`

A `backend` plugin that registers 7 Spotify tools (`spotify_playback`, `spotify_devices`, `spotify_queue`, `spotify_search`, `spotify_playlists`, `spotify_albums`, `spotify_library`). Uses PKCE OAuth via `hermes auth spotify`. Tools gate on credentials in `~/.hermes/auth.json`.

### 9.4 `plugins/google_meet/`

A heavy `standalone` plugin: joins Google Meet via a headless browser, transcribes captions, can speak via TTS through a virtual audio cable (BlackHole on macOS, PulseAudio on Linux). Has v1 (transcribe-only), v2 (realtime duplex audio via OpenAI Realtime), v3 (remote node host — bot runs on a different machine than the gateway).

### 9.5 `plugins/hermes-achievements/`

A vendored third-party plugin (from `@PCinkusz`). Reads local Hermes session history and unlocks badges. Renders into a dashboard tab. **First-party because vendored; tracks third-party staging repo for new badges.** This is one model for "we ship community plugins by vendoring them when they're load-bearing for the user experience."

### 9.6 `plugins/teams_pipeline/`

A full pipeline plugin: subscriptions, models, store, runtime, CLI. Polls Microsoft Graph for Teams transcripts, processes them into summaries, surfaces in CLI via `hermes teams ...`. Demonstrates a plugin that owns *its own data model and persistence*.

### 9.7 `plugins/kanban/dashboard/` + `plugins/kanban/systemd/`

The Kanban plugin is *split* — the actual tools live in `tools/kanban_tools.py` (core), the dashboard SPA lives here, the systemd unit lives here. The plugin tree is *deployment assets* rather than runtime code. Worth noting: not every plugin tree is Python.

---

## 10. The Boundary Lines

Three boundaries the plugin system enforces:

1. **Plugins never touch core.** Per `AGENTS.md:531-535`: *"plugins MUST NOT modify core files (run_agent.py, cli.py, gateway/run.py, hermes_cli/main.py, etc.). If a plugin needs a capability the framework doesn't expose, expand the generic plugin surface (new hook, new ctx method) — never hardcode plugin-specific logic into core."* PR #5295 (per AGENTS.md) removed 95 lines of hardcoded honcho argparse from `main.py` for exactly this reason.

2. **Plugins register through the context.** Tools, hooks, CLI commands, platforms — all through `ctx.register_*`. The plugin does not reach into the registry directly.

3. **Plugins fail in isolation.** A failed plugin is `error: <message>` in `hermes plugins`. It does not crash Hermes. It does not block other plugins. The **Vow of Modular Authorship**, exactly.

---

## What This Means for Ember

The plugin system is one of Hermes's *strongest* areas — and one of its messier ones. Ember should learn the pattern, fix the leak.

**Affected True Names:** the plugin system is *cross-Realm*. Funi plugins (model providers — but Ember currently runs Ollama-only), Brunnr plugins (storage backends — slice 2 already has this for sqlite_vec / pgvector), Strengr plugins (alternate network backends), Munnr plugins (alternate UI surfaces), Smiðja plugins (ingest sources), Verkfæri plugins (tools), Listir plugins (skill sources).

The system needs *one* True Name to govern it — and that True Name is probably **best left implicit**. Plugins are not a subsystem; plugins are a *facet* every subsystem exposes. The contract is shared; the implementations are per-Realm.

### Concrete proposals

1. **Adopt ONE plugin-discovery contract, with multiple `kind`s.** Hermes's leak — three parallel discoveries — should not be Ember's inheritance. Define:
   - **One** scanner: `~/.ember/plugins/<name>/` + `<repo>/plugins/<name>/` + entry-points
   - **One** manifest format: `plugin.yaml` with `name`, `version`, `description`, `author`, `kind`, `requires_env`, `provides_*`, `platforms` (OS gate)
   - **One** discovery time: idempotent `discover_plugins()` at agent init
   - **Multiple** `kind` values that dispatch to per-kind loaders: `tool`, `storage` (Brunnr backend), `ingest` (Smiðja source), `provider` (future), `context_engine`, `surface` (future Munnr alternatives), `hook_only`
   - **One** `PluginContext` shape with per-kind subsets of methods exposed

2. **Adopt `ctx.register_tool` + `ctx.register_hook` + `ctx.register_cli_command` exactly.** Same shape. Same opt-in policy. Cite `hermes_cli/plugins.py:317-400`.

3. **Adopt the rich `requires_env` (dict shape) for auto-populating the setup wizard.** `requires_env: [{name: HERMES_FOO, description: ..., url: ..., password: true}]` is much friendlier than a bare string list. Cite the model-provider plugin manifests.

4. **Adopt the opt-in default for user/standalone plugins.** Bundled plugins of `kind: backend` or `kind: platform` auto-load (they wire existing tools); bundled `standalone` and *all* user plugins require explicit opt-in. This protects the user from running arbitrary code without consent. Cite `hermes_cli/plugins.py:200-223`.

5. **Adopt the `ctx.llm` facade.** Plugins shouldn't bring their own API keys; they should call the host's LLM via a controlled facade with config-gated overrides. Cite `hermes_cli/plugins.py:296-313`.

6. **Adopt the *plugin-injects-message* pattern (`ctx.inject_message`).** A plugin can send the agent a message ("memory provider updated 3 records"). Useful for observability, achievements-style notifications, background-job completions. Cite `hermes_cli/plugins.py:357-383`.

7. **Refuse to vendor third-party plugins by default.** Hermes's vendoring of `hermes-achievements` is pragmatic but architecturally weakens the boundary. Ember should keep third-party plugins out of the repo. Pip-installable, yes. Vendored, no.

8. **Refuse to ship sixteen plugin trees in the initial slices.** Ember's slice 1-2 has zero plugins (Brunnr backends are first-party, not plugin-shipped). Adding plugin support is a slice-N decision, and when added, ship with **fewer than five** initial plugins (memory? observability? maybe one ingest source?).

9. **Document the *plugins-must-not-touch-core* invariant in `[[10_domain/19_BOUNDARY_LAW]]` as a Vow.** Cite `AGENTS.md:531-535` and the PR #5295 example. Ember's pluggability discipline should be stricter than Hermes's: NO plugin code touches realm-band code (Spark, Thread, Well). Plugins live in their own band that imports DOWN into the realms but is never imported BY them.

**Vows reinforced:**
- **Vow of Modular Authorship** — plugins are individually failable; bad plugin doesn't crash Ember.
- **Vow of Open Knowledge** — plugin manifests are declarative, discoverable, attributed.
- **Vow of Public-Friendliness** — opt-in defaults; rich env-var prompts in setup wizard.

**Vows at risk:**
- **Vow of Smallness** — sixteen plugin trees on a Pi is a system-bloat hazard. Ember should ship few plugins early.
- **Vow of Modular Authorship** — three parallel discovery systems is exactly the failure mode the Vow defends against. Don't inherit it.

The system asks to be extended in the places it draws the seam. The Hermes seam is generous; the implementation of the seam is fractured. Ember inherits the generosity and refuses the fracture.
