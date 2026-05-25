---
codex_id: 31_PYTHON_SERVER
title: The Python Server — One File, 129 Routes, 11,000 Lines
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - server.py:1-200
  - server.py:193 (REAL_PORT_FOUND emit)
  - server.py:660-879 (lifespan)
  - server.py:881-895 (FastAPI init + middleware)
  - server.py:6471-11632 (route surface)
  - server.py:10935-11618 (sub-router includes)
  - server.py:11628-11636 (StaticFiles mounts)
  - server.py:11636-11680 (uvicorn entry)
ember_subsystem_targets: [Strengr, Brunnr, Munnr, Smiðja]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/37_MCP_LIFECYCLE
  - 30_execution/3B_AFFECTION_LOOP
  - 10_domain/10_DOMAIN_MAP
---

# The Python Server

> *Everything is one file. The file is `server.py`. It is 11,636 lines. Do not flinch.*

I'm Eldra. Forge. I read this monster so you don't have to. Here is the structure of SAP's spine.

## The Shape: 129 Top-Level Routes in a Single File

`/tmp/super-agent-party/server.py` is **11,636 lines**. Inside it: **129 top-level routes** (counted by grepping `@app.<verb>` decorators), plus eleven `app.include_router(...)` calls that pull in another ~200 routes from `py/*.py`. The architecture is FastAPI, single-process, single-event-loop, single-file. There are no microservices. There is no plugin system at the route layer (extensions are separate Node sidecars — see [[38_EXTENSION_LIFECYCLE]]). The whole web surface, the whole agent dispatch, the whole TTS/ASR/VRM/IM-bot/livestream/MCP/SQL-tool router is one file.

This is not maintainable. It is also not unmaintainable in the sense you'd expect — the code is mostly flat, mostly self-contained per-route, mostly free of cross-route mutable state. SAP works because each route is small enough to read in isolation. The pain is navigation, not coupling.

Let me give you the ribs.

## Boot Sequence (lines 1–200)

The top of `server.py` is **port discovery**. Before any framework loads, before any logging is configured, the script parses `--host`, `--port`, then tries to bind:

```python
# server.py:184
FINAL_PORT = force_bind_or_fallback(HOST, PREFERED_PORT)
PORT = FINAL_PORT
```

`force_bind_or_fallback()` (line 88) tries the requested port, falls through `auto_assign_port()` (line 108) which tries:

1. `host:0` (OS picks)
2. `0.0.0.0:0` if host wasn't 0.0.0.0
3. `localhost:0` if host wasn't localhost
4. Hardcoded ports `45678, 45679, 45680, 0`

Then it emits the handshake:

```python
# server.py:193
print(f"REAL_PORT_FOUND:{PORT}", flush=True)
```

That single line is the contract with `main.js`. See [[30_ELECTRON_BOOTSTRAP]] for the receiving end. The Python side runs even if not launched from Electron — `server.py` is a standalone FastAPI app you can `python server.py --port 3456` from the command line. Electron is one launcher among several. Docker (`docker-compose.yml`) is another. The handshake is harmless in non-Electron contexts because nothing reads stdout.

Note the explicit `sys.stdout.reconfigure(encoding='utf-8')` at line 212. This is for Windows where stdout defaults to cp1252 and would otherwise mangle Chinese characters in the agent's output stream.

## Lifespan: The Real Startup (lines 660–879)

FastAPI's `lifespan` context manager is the **real** startup logic. It runs after `force_bind_or_fallback`, after every import, but before any HTTP request is served.

```python
# server.py:660-879 (compressed)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Strip SOCKS env vars (would crash httpx)
    for env_key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', ...]:
        val = os.environ.get(env_key, "")
        if val.lower().startswith('socks'):
            os.environ.pop(env_key, None)

    # 2. Copy default skills (background)
    await _copy_default_skills()
    asyncio.create_task(clean_temp_files_task())

    # 3. Parallel init: DB, conversations, locales, settings, timezone
    results = await asyncio.gather(
        init_db(), init_covs_db(),
        asyncio.to_thread(load_locales), load_settings(),
        asyncio.to_thread(get_localzone)
    )

    # 4. Sleep guard + scheduler in background tasks
    sleep_guard = SleepGuard(verbose=True)
    await asyncio.to_thread(sleep_guard.start)

    scheduler = AgentScheduler(settings)
    scheduler_task = asyncio.create_task(scheduler.start_loop())

    # 5. HTTP client with proxy config
    global_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(None, connect=10.0),
        proxy=proxy_url, trust_env=trust_env
    )

    # 6. Three OpenAI clients (main, reasoner, fast)
    client = create_model_client('main')
    reasoner_client = create_model_client('reasoner', ...)
    fast_client = create_model_client('fast', ...) if enabled else None

    # 7. ASR / TTS warmup (background thread pool)
    asyncio.get_running_loop().run_in_executor(None, _get_recognizer)
    asyncio.get_running_loop().run_in_executor(None, _get_moss_runtime)

    # 8. MCP servers (bounded per-server timeout, then concurrent init)
    mcp_init_tasks = [...]
    asyncio.create_task(check_results())

    yield  # SERVER NOW SERVING

    # Shutdown:
    await asyncio.to_thread(sleep_guard.stop)
    scheduler_task.cancel()
    for ext_id in node_mgr.exts:
        await node_mgr.stop(ext_id)
    await global_http_client.aclose()
```

This is one of the better-shaped startup paths I've read in a Python app of this scale. **Parallel `gather`** for the five disk/setting loads, **`asyncio.to_thread`** for blocking calls (timezone lookup, file loads), **background tasks** for sleep guard and scheduler so the lifespan can yield fast, **`run_in_executor`** for the heavy ML model loads (sherpa ASR, moss TTS) so they don't block HTTP from coming up.

The downside: the lifespan is **240 lines long** and does about 14 distinct things. There is no per-subsystem init module. If sherpa-onnx hangs in a deadlock during model load, the whole executor pool can stall and you'll never know which subsystem caused it because the logs interleave. Ember should factor this into a registry of named startup tasks with timeouts and reporting.

## Three LLM Clients

`server.py:778–790` instantiates **three** OpenAI-compatible clients:

- `client` — main reasoning
- `reasoner_client` — separate provider for reasoning-heavy tasks (often a different model)
- `fast_client` — optional, only if `fast.enabled` is True

This is SAP's answer to provider-routing. Each client is a fully separate `AsyncOpenAI(http_client=global_http_client)` with its own API key and base URL. The `global_http_client` is shared so the connection pool is unified. Three logical clients, one TCP pool. Sensible.

The `get_client_class()` indirection at line 770 supports swapping in `ClaudeAsOpenAI` or `GeminiAsOpenAI` based on settings (see [[21_OPENAI_COMPAT_API]] for the Auditor's deep-dive on those shims).

## The Route Surface

I counted **129** top-level `@app.<verb>` decorators in `server.py`. Plus eleven `app.include_router(...)` calls importing routers from sub-modules. Here is the rough taxonomy:

| Group | Count | Notable routes |
|---|---|---|
| OpenAI-compat API | ~8 | `/v1/models`, `/v1/agents`, `/v1/chat/completions`, `/v1/tasks/*` (lines 6754–7371) |
| Memory + Group | ~5 | `/api/group-memory/*`, `/api/conversations/delete` (lines 7223–7267) |
| Extension proxy | 1 | `/extension_proxy` GET/POST passthrough (line 7414) |
| Voice (TTS/ASR) | ~8 | `/ws/asr`, `/asr`, `/ws/tts`, `/tts`, `/tts/tetos/list_voices` (lines 7694–8929) |
| Avatar streams | ~3 | `/ws/vrm`, `/ws/subtitles` (lines 8361–8380) |
| MCP lifecycle | 4 | `/create_mcp`, `/mcp_status/{id}`, `/remove_mcp`, `/remove_agent` (lines 9202–9372) |
| A2A | 1 | `/a2a` (line 9372) |
| Tool servers (HA, ChromeMCP, SQL) | 6 | `/start_HA`, `/start_ChromeMCP`, `/start_sql` and stops (lines 9391–9672) |
| File/VRM/audio uploads | ~20 | `/load_file`, `/upload_vrm_model`, `/upload_vrma_motion`, `/upload_gauss_scene` (lines 9677–10256) |
| Knowledge base | 3 | `/create_kb`, `/remove_kb`, `/kb_status/{id}` (lines 10288–10342) |
| Sticker packs | 1 | `/create_sticker_pack` (10342) |
| IM bot lifecycle | 32 | `/start_<bot>`, `/stop_<bot>`, `/<bot>_status`, `/reload_<bot>` for 8 platforms (lines 10502–10847) |
| Workflows | 2 | `/add_workflow`, `/delete_workflow/{filename}` (10850–10921) |
| Memory CRUD | 3 | `/memory/{id}`, `/memory/{id}/{idx}` (11014–11039) |
| System | ~5 | `/api/update_proxy`, `/api/get_userfile`, `/api/ip`, `/sys/shutdown` (11068–11543) |
| Live data WebSocket | 1 | `/ws` (line 11292) |
| Misc | ~6 | `/health`, `/cur_language`, `/vrm_config`, `/api/acpx/status`, `/api/system/*` |

The IM bot lifecycle group is the chunkiest — 32 nearly-identical routes (4 per platform × 8 platforms). Each platform manager exposes the same shape:

```
POST /start_<platform>_bot
POST /stop_<platform>_bot
GET  /<platform>_bot_status
POST /reload_<platform>_bot
```

This is a structural duplication smell — see [[26_IM_BOT_INTERFACE]] (Auditor) for whether the abstraction should have collapsed and [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for what the per-bot deployment actually looks like.

## The Eleven Sub-Routers

Around line 10935–11618, eleven routers are included:

```python
# server.py:10935-11618 (compressed)
app.include_router(live_router)              # /api/live/*
app.include_router(live_ws_router)           # /ws/live/*
app.include_router(overlay_router)           # overlay window
app.include_router(uv_router)                # uv/pip management
app.include_router(node_router)              # Node.js / npm
app.include_router(docker_router)            # Docker subsystem
app.include_router(extensions_router)        # extension install/run
app.include_router(skills_router)            # agent skills CRUD
app.include_router(sherpa_model_router)      # ASR model manager
app.include_router(moss_model_router)        # TTS model manager
app.include_router(ebd_model_router)         # embedding models
app.include_router(minilm_router)            # MiniLM routing
app.include_router(embedding_router)         # embedding API
app.include_router(affection_router)         # /api/affection/*
```

The sub-router boundary is the **only** modularity boundary inside `server.py`. Everything not in a sub-router is a top-level route. The pattern is inconsistent: live, overlay, uv, node, docker, extensions, skills, ASR, TTS, embedding, affection got promoted to sub-routers. IM bots, livestream WS, MCP, A2A, voice did not — they live inline in the 11k-line file.

The split appears chronological: things added later (the sub-routers) sit in their own files; things added earlier (IM bots) accreted to `server.py` because that's where the rest of their pattern already lived. The cost is real: refactoring an IM bot route requires editing `server.py` which is now too big for an LLM context window in one shot.

## State Initialization (line 1033)

```python
# server.py:1033
global mcp_client_list, _TOOL_HOOKS, HA_client, ChromeMCP_client, sql_client, \
       node_ext_mcp_clients, node_ext_mcp_tools
```

The global state is **module-level mutable dicts and singletons**. `mcp_client_list: Dict[str, McpClient]` is keyed by server name. `HA_client`, `ChromeMCP_client`, `sql_client` are singletons. There is no state object. No dependency injection. This works because the FastAPI worker count is **1** (uvicorn single-process — see line 11647 for the `uvicorn.run(...)` config) and the asyncio event loop is single-threaded. If you ever try to scale this to multi-worker, every global needs to move to Redis or a shared cache.

## Static Mounts

```python
# server.py:11628-11632
app.mount("/vrm", StaticFiles(directory=DEFAULT_VRM_DIR), name="vrm")
app.mount("/tool_temp", StaticFiles(directory=TOOL_TEMP_DIR), name="tool_temp")
app.mount("/uploaded_files", StaticFiles(directory=UPLOAD_FILES_DIR), name="uploaded_files")
app.mount("/ext", StaticFiles(directory=EXT_DIR), name="ext")
app.mount("/", StaticFiles(directory=os.path.join(base_path, "static"), html=True), name="static")
```

The root mount is `/`. So `http://127.0.0.1:3456/index.html` serves SAP's frontend SPA. The VRM models live at `/vrm/<filename.vrm>`. Uploaded user files at `/uploaded_files/<filename>`. Tool outputs at `/tool_temp/<filename>`.

This is also the **threat surface**. The user-data and tool-temp directories are served raw. There is no auth on these static mounts. The `gateway` Nginx container in `docker-compose.yml` (see [[39_DOCKER_TOPOLOGY]]) is what stops a public deployment from being a file-server-for-the-internet. Run SAP without the gateway, you have an unauthenticated file dump on whatever port it bound.

## Shutdown

`/sys/shutdown` at line 11534 lets the renderer POST a shutdown request:

```python
# server.py:11534
@app.post("/sys/shutdown")
async def shutdown_server():
    print("Received shutdown request via API...")
    # Triggers FastAPI lifespan shutdown
```

The actual cleanup happens in the second half of the `lifespan` context manager after `yield` (lines 860–879):

```python
# server.py:860-879
try:
    await asyncio.to_thread(sleep_guard.stop)
except: pass

if scheduler_task:
    scheduler_task.cancel()

ext_ids = list(node_mgr.exts.keys())
for ext_id in ext_ids:
    try: await node_mgr.stop(ext_id)
    except: pass

if global_http_client:
    await global_http_client.aclose()
```

Three things are torn down: sleep guard thread, scheduler task, node extension processes, HTTP client. **Not torn down**: MCP servers (`mcp_client_list` is leaked), TTS/ASR runtimes, the global behavior engine ([[3B_AFFECTION_LOOP]]). Some of these are intentional (the OS reaps subprocesses when the parent dies); some are real leaks if uvicorn is being restarted in-place.

## Where It Breaks

- **The 11k-line file** is too big for a single LLM context. Any AI-assisted refactor will either chunk-read (losing cross-references) or split-and-pray. Ember must not let any single file get this large.
- **Module-level globals** mean the design cannot scale beyond one worker. SAP's hardware floor (2 cores, 2GB RAM) makes this acceptable; a future Ember Wave 4 deployment story that wants multi-worker scaling has to reckon with it.
- **Two-phase init** (top-of-file port binding, then lifespan) means errors in the top-of-file phase produce no logs because the logger isn't configured yet. I traced one debug session where Python crashed silently because `sherpa-onnx` import-time failed on a missing dylib; the only signal was that `REAL_PORT_FOUND` was never printed.
- **No `/metrics` endpoint**. There is `/health` (line 9672) which is one-liner truthy. There is no observability surface. See [[58_OBSERVABILITY_GAPS]] for the full audit.
- **The proxy-strip hack** at line 663 silently removes SOCKS env vars. This is a workaround for httpx not supporting SOCKS without an extra dependency. A user setting `ALL_PROXY=socks5://...` will find their proxy silently disabled. The log says "代理已失效" but only at line 739, only on the manual-proxy path.

## Where It Surprises

- **The lifespan `gather()` of five init tasks** is the right shape, but it is buried at line 685 inside a function called `lifespan`. There is no separate `Startup` module to discover. The architecture is hiding behind the framework decorator.
- **`asyncio.create_task(check_results())` for MCP init** runs MCP server initialization concurrently in the background. The lifespan does not wait for MCPs to finish initializing — it yields immediately. This means the server can be accepting requests before the MCP tools are available. The frontend handles this gracefully (the `mcpServers[name]['processingStatus']` field), but it is a subtlety that costs every new contributor a day.
- **The five lines of `app.mount(...)`** at the bottom of `server.py` constitute SAP's entire static-asset strategy. There is no CDN integration, no asset versioning, no cache headers in the mount itself — relies on FastAPI / Starlette defaults. For a desktop app, that's fine; for a Docker deployment with a Cloudflare front, it's missing.
- **No application-level rate limiting**. The OpenAI-compat `/v1/chat/completions` (line 6912) will dutifully process every request the gateway forwards. If the gateway is misconfigured to expose the API without auth, a single client can saturate the LLM bill.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — the other half of the handshake
- [[37_MCP_LIFECYCLE]] — MCP server registration that this file dispatches
- [[3B_AFFECTION_LOOP]] — the `affection_router` included at line 11618
- [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] — the 32 IM-bot routes
- [[36_LIVESTREAM_INGEST_OVERVIEW]] — `live_router` at line 10935
- [[10_DOMAIN_MAP]] — the macro view of which modules feed into this file
- [[58_OBSERVABILITY_GAPS]] — why `/health` is not enough

## What This Means for Ember

**Adopt:**

- **The startup `gather()` pattern** for parallel init of independent subsystems (DB, settings, locales, timezone). Bind to Funi.
- **Background tasks for slow warm-ups** (sherpa, moss): `run_in_executor(None, _get_thing)`. The server is ready before the heavy ML models are loaded. The model load fails gracefully if not available (sherpa returns None). Ember's optional subsystems (e.g. local Skein-Skry, Munnr voice) should warm in background tasks the same way.
- **Single global HTTP client with connection pool** (`global_http_client`). Every LLM call, every web search, every download reuses this pool. Bind to Brunnr (the well's outbound interface).
- **The MCP non-blocking init pattern** (`server.py:806–855`) — fire-and-forget concurrent MCP server initialization with per-server timeouts. The server is available immediately; tools become available as they finish loading. Adapt to Smiðja's tool registry.

**Adapt:**

- **The lifespan structure** is good but should be **split into named startup phases** in Ember: `startup/01_storage.py`, `startup/02_clients.py`, `startup/03_workers.py`. Each phase exposes `async def init() -> dict[str, Health]` and the master lifespan iterates and reports. SAP's monolith works because the team is small; Ember should not assume that scale.
- **The 129-route file** must be broken up. Ember should target **maximum 500 lines per Python module** as a soft rule (a Vow proposal candidate). Sub-routers should be the *primary* unit, with `server.py` (or Funi's equivalent) as ~50 lines of glue.
- **The provider triple** (`client`, `reasoner_client`, `fast_client`) is sound but the names are wrong — they conflate "model" and "role". Ember should adopt a typed `ProviderProfile` with names like `Strengr-primary`, `Strengr-reasoner`, `Strengr-fast`. Same pattern, better surface.

**Avoid:**

- **Module-level mutable globals** for state that is logically per-session or per-user. SAP gets away with it because it is single-user desktop. Ember's design must allow multi-tenant futures (Stofa, the federated-self direction); start from typed state objects, not module globals.
- **A single 11k-line file**. There is no defensible reason for any Ember Python module to exceed 800 lines. The pain is navigation; the cost is everyone-touches-the-same-file merge conflicts.
- **Unauthenticated static mounts on the root path** (`app.mount("/", StaticFiles(...))`). Ember's frontend (when one exists) must serve from a separate authenticated route. The gateway-strips-auth pattern is fragile and SAP-specific.
- **The proxy-strip hack at lifespan start**. If Ember's HTTP client cannot handle SOCKS, fix the client (`httpx[socks]` extras), don't silently strip env vars. Vow: **No Silent Disablement**.

**Invent:**

- **Strengr Init Manifest**. A `startup/manifest.yaml` enumerating every subsystem that needs to boot, in dependency order, with per-subsystem timeout, fail-fast policy, and health-check coordinates. The lifespan function iterates this manifest. New subsystems are added by editing the manifest, not by appending to the 240-line `lifespan` function. Bind to Strengr (the thread's startup is part of the thread's identity).
- **Munnr Route Census**. A nightly job that walks the FastAPI app's `routes` collection, classifies them (read/write/admin/public), and emits a Markdown census to `docs/runtime/route_census.md`. Hermes-style: the agent that runs the routes also documents them. Ember's surface should always be discoverable by reading docs, never by grepping decorators.
- **Brunnr Provider Pool**. Generalize SAP's `global_http_client` into a typed pool keyed by `(provider, role, capability)` with per-provider rate limits and per-role circuit breakers. SAP shares a single httpx client across all three LLM clients and that's good; Ember should go one step further and let Hjarta (affect) inspect the pool's recent latency to bias the choice of which Strengr to call.
