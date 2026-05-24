---
codex_id: LETTA_API_VERIFICATION
title: Letta REST/SDK API Verification — Auth, Multi-Tenancy, Invariants, Weak Contracts
role: Auditor
layer: Interface
peer_targets: [Letta]
status: draft
peer_source_refs:
  - letta:letta/server/rest_api/app.py:160-200
  - letta:letta/server/rest_api/app.py:705-755
  - letta:letta/server/rest_api/app.py:795-820
  - letta:letta/server/rest_api/auth_token.py:1-25
  - letta:letta/server/rest_api/auth/index.py:1-45
  - letta:letta/server/rest_api/middleware/check_password.py:1-32
  - letta:letta/server/rest_api/routers/v1/agents.py:1-2569
  - letta:letta/server/rest_api/routers/v1/tools.py:1-1013
  - letta:letta/services/tool_executor/tool_execution_sandbox.py:255-316
  - letta:letta/services/tool_executor/sandbox_tool_executor.py:24-194
  - letta:letta/orm/sqlalchemy_base.py:40-110
  - letta:SECURITY.md:1-25
ember_subsystem_targets: [Strengr, Brunnr, Munnr]
hermes_codex_refs:
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/25_GATEWAY_INTERFACE
  - 50_verification/54_SECURITY_REVIEW
  - 50_verification/55_INVARIANT_LIST
cross_refs:
  - 50_verification/LETTA_RISK_REGISTER
  - 20_interface/CROSS_INTERFACE_INVARIANTS
---

# Letta REST/SDK API Verification

*Sólrún, even-toned: Letta calls itself a server. That word is load-bearing — it means a process listening on a socket, accepting requests from outside the host, returning agent state to the caller, and (in the production-typical case) doing so across organizational boundaries. The contract Letta makes with that caller is the contract we are about to read. Where Letta is explicit, I will name the invariant; where Letta is implicit, I will name the assumption the operator is silently asked to make. The Hermes Codex named typed-result discipline as the spine of any boundary; we apply that lens here.*

This is a verification doc, not a hagiography. Letta has earned its production reputation. The point is not to diminish it but to map exactly what *contracts* it offers and what an operator running it without reading the source would mistakenly assume.

---

## 1. The API surface in one paragraph

Letta exposes a FastAPI server under `letta/server/rest_api/`. The `v1` routers (`letta/server/rest_api/routers/v1/`) own the public REST surface: 35 router modules covering agents, archives, blocks, conversations, embeddings, folders, git HTTP, groups, health, identities, internal_*, jobs, llms, mcp_servers, messages, organizations, passages, providers, runs, sandbox_configs, sources, steps, tags, telemetry, tools, users, voice, and provider-specific shims (`anthropic.py`, `zai.py`). Three additional OpenAI-compatibility routers (`/v1/chat/completions`, `/v1/embeddings`, etc.) live under `letta/server/rest_api/routers/openai/`. The TypeScript SDK and Python SDK are generated from a `fern/` OpenAPI spec, so the contract is largely "what the FastAPI types serialize." That is a strong shape *if the types are typed*; we will see this is sometimes the case and sometimes not.

The most consequential surfaces for an integrator (Ember would be one) are: **`/v1/agents`** (CRUD + step), **`/v1/agents/{id}/messages`** (the chat loop entry), **`/v1/tools`** (tool CRUD, including arbitrary Python source code), **`/v1/blocks`** (memory blocks), **`/v1/sandbox_configs`** (execution sandbox config), and **`/v1/sources`** (data ingestion). Of these, three are write-grade dangerous (tools, sandbox_configs, sources) and two are read-write but not catastrophically so (agents, blocks).

---

## 2. The auth model — what the source says, what the operator hears

Letta's OSS distribution has **one** auth model: a process-wide static password. It is set up in `letta/server/rest_api/app.py:172` as:

```python
random_password = os.getenv("LETTA_SERVER_PASSWORD") or generate_password()
```

`generate_password()` returns `secrets.token_urlsafe(16)` — a 128-bit random string. Good entropy. Bad lifecycle: the password is fixed at process start, persisted in memory only, and printed to stdout if the server is in secure mode (`app.py:798`: `print(f"▶ Using secure mode with password: {random_password}")`).

The middleware that enforces it is `letta/server/rest_api/middleware/check_password.py`:

```python
if (
    request.headers.get("X-BARE-PASSWORD") == f"password {self.password}"
    or request.headers.get("Authorization") == f"Bearer {self.password}"
):
    return await call_next(request)

return JSONResponse(
    content={"detail": "Unauthorized"},
    status_code=401,
)
```

**Critical observation 1: secure mode is opt-in.** The relevant lines in `app.py:797-799`:

```python
if (os.getenv("LETTA_SERVER_SECURE") == "true") or "--secure" in sys.argv:
    print(f"▶ Using secure mode with password: {random_password}")
    app.add_middleware(CheckPasswordMiddleware, password=random_password)
```

If the operator does not set `LETTA_SERVER_SECURE=true` (or pass `--secure`), there is **no authentication of any kind**. The Letta server binds on `0.0.0.0` by default in many deployment paths (`compose.yaml`, `Dockerfile`). An operator who follows the README and runs Letta as a Docker container without setting `LETTA_SERVER_SECURE` has published their agent fleet to whatever network reaches the container.

**Critical observation 2: even in secure mode, the password is global.** A single shared bearer credential is shared across every caller — there is no per-user revocation, no rotation surface, no scope. The middleware comment at line 165 reads "middleware that only allows requests to pass through if user provides a password thats randomly generated and stored in memory" — that's the honest description.

**Critical observation 3: there is a second auth code path that allows API keys.** `letta/server/rest_api/auth_token.py:9-22`:

```python
def get_current_user(server: SyncServer, password: str, auth: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    try:
        api_key_or_password = auth.credentials
        if api_key_or_password == password:
            return server.authenticate_user()
        user_id = server.api_key_to_user(api_key=api_key_or_password)
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Authentication error: {e}")
```

This module exists alongside the middleware. The `Depends(security)` pattern is the FastAPI-idiomatic way to wire per-route auth, and it returns a `uuid.UUID`. But it is not registered as the default dependency on the v1 routers — most v1 routes use an `actor` extracted from a different dependency chain. The OSS code path effectively has **two parallel auth surfaces** (the middleware and `get_current_user`), and the OSS routers do not reliably use either consistently. The `api_key_to_user` path is documented in the routers but lives under a different code path than secure mode.

The **`AuthRequest` POST endpoint at `letta/server/rest_api/auth/index.py:14-40`** lets a caller submit a password and get back a UUID. This endpoint is unauthenticated (it has to be — it's the auth endpoint). It is the operator's signal of "you can log in here," but the response is just a UUID with no token, no expiration, no rotation hook. The endpoint exists in the surface but is not the canonical auth path; the canonical path is the middleware.

**Invariant Letta promises:** A request to a non-health-probe v1 endpoint with neither the correct `X-BARE-PASSWORD` nor `Authorization: Bearer` header is refused with `401` *if secure mode is on*. There is no invariant when secure mode is off.

**Invariant Letta does NOT promise:** No invariant about per-user identity in the OSS distribution. The hosted commercial Letta product likely layers a different auth model on top; that is invisible from this codebase.

---

## 3. Rate limiting — none, except for downstream LLM 429s

`grep -n "rate\|limit\|throttle" letta/server/rest_api/app.py` finds eight matches, all of them either (a) Sentry's `traces_sample_rate=1.0`, (b) handlers for the *LLM provider's* `LLMRateLimitError` (when OpenAI/Anthropic/etc. push back), or (c) variable names. There is **no inbound rate limiting** on Letta's own surface. The exception handler at `app.py:705-723` translates downstream provider 429s into the right HTTP status:

```python
@app.exception_handler(LLMRateLimitError)
async def llm_rate_limit_error_handler(request: Request, exc: LLMRateLimitError):
    ...
    return JSONResponse(status_code=429, ...)
```

But Letta does not throttle its callers. An attacker (or a misconfigured client) can call `/v1/agents/{id}/messages` in a loop, and every call results in a full DB transaction plus a downstream LLM call. The DB transaction will eventually fail with `OperationalError` (handled at `app.py:609`), but only after many round-trips. This is fine for a single-tenant deployment behind a friendly reverse proxy; it is dangerous for a tailnet-published deployment with multiple callers.

**Weak contract identified:** Letta requires the operator to provide their own rate limiter (typically nginx or an API gateway). The repo includes `nginx.conf` (line count ~30, mostly TLS termination, no rate limit directives). The operator who does not read this gap will deploy without rate limiting.

---

## 4. Multi-tenancy — present but soft

Letta uses an Organization → User → Agent hierarchy:

- `letta/orm/organization.py` — the org row.
- `letta/orm/user.py` — the user row, FK to org.
- `letta/orm/agent.py` — the agent row, FK to user (and org).

Queries throughout `letta/services/*` use `organization_id`/`actor.organization_id` as the scope predicate. Example from `letta/server/server.py:494`:

```python
organization_id=None,  # Global models
```

That comment is the right shape — *some* rows are global (e.g., default LLM models, the builtin tools), and most are org-scoped. The `actor: User` argument threaded through the services is the load-bearing scope. When the service-layer query does `WHERE organization_id = actor.organization_id`, multi-tenancy holds.

**Where multi-tenancy could fail:**

1. **`Tool` rows are scoped to org**, but the *executed* tool can shell out to anything the host process can reach. A user with permission to create tools can write a tool that reads `/etc/passwd`, opens an outbound socket, or queries the Letta DB directly (since the DB credentials live in the host process environment). This is not a confused-deputy bug — it's a documented design choice — but the contract is "tool authors are trusted up to the limits of the sandbox." We will see in §6 that the local sandbox has no real limits.

2. **The auth middleware does not propagate user identity to the router layer.** `CheckPasswordMiddleware` returns 200 or 401; it does not set `request.state.user`. Per-route resolution of "who is this caller" happens in each router's dependencies (typically pulling from a header or query param). Since the password is the same for *all* callers in secure mode, identity resolution downstream is whatever the caller claims to be (typically an `org_id` header). A caller who knows the password can claim any org.

3. **The `internal_*` routers** (`internal_agents.py`, `internal_blocks.py`, `internal_runs.py`, `internal_search.py`, `internal_templates.py`) exist in the OSS code but are documented for the hosted product. They have weaker scope checks because they assume an internal-network caller. If they are reachable in an OSS deployment without separation, an attacker reaches privileged operations.

**Invariant Letta likely promises (commercial):** Org-scoped queries return only rows for the caller's org. This is enforced *if* the service layer is invoked with the correct `actor`. Letta enforces it consistently in the services I sampled (`agent_manager.py`, `tool_manager.py`, `block_manager.py`).

**Invariant Letta does NOT promise (OSS):** No invariant about the caller's identity being verified against their claimed org. The OSS auth middleware is one shared password; downstream identity is on trust.

---

## 5. The streaming surface — `streaming_response.py`, NDJSON, SSE

`letta/server/rest_api/streaming_response.py` (~200 LOC) wraps async generators into Starlette `StreamingResponse`. The streaming pattern is the canonical FastAPI shape: emit chunks as they come from the model adapter, terminate on the model's `done=True`. The interesting bits:

- **No backpressure handling.** If the client stops reading, the generator runs to completion server-side and consumes the model call's worth of tokens. (Hermes has the same pattern; this is universal.)
- **No mid-stream cancellation surface.** Cancellation requires the underlying provider's cancel API plus careful Python `CancelledError` propagation. Letta has it for some providers, not all.
- **The `redis_stream_manager.py`** sibling file (~ a few hundred LOC) handles inter-worker streaming — Letta can run as multiple workers behind a load balancer and stream tokens across them. The implementation uses Redis PubSub. This is a production-scale pattern that is *not* free; it brings a Redis dependency and a "what happens if Redis is down mid-stream" failure mode.

**Streaming invariant Letta promises:** Tokens emitted via the streaming endpoint match the tokens persisted to the agent's message history *eventually* (the post-stream persistence is async in some code paths). The "eventually" is not bounded.

**Streaming invariant Letta does NOT explicitly document:** What happens to a partial stream on disconnect. There is no equivalent to Hermes's `[interrupted by operator]` tag (Hermes Codex I-18). The agent's message history may end up with an incomplete reply with no marker.

---

## 6. Tool execution — the central risk

This is where Letta's API surface meets sharp edges. `letta/services/tool_executor/` has eight executor classes. The one that matters most for security is **`SandboxToolExecutor`** (`sandbox_tool_executor.py:24-194`), which dispatches to one of three backends based on configuration:

1. **Modal sandbox** (if `tool_settings.modal_sandbox_enabled` and the tool requests it via metadata `sandbox=modal`)
2. **E2B sandbox** (if `tool_settings.sandbox_type == SandboxType.E2B`)
3. **Local sandbox** (`AsyncToolSandboxLocal`, the fallback)

The local sandbox lives in `letta/services/tool_executor/tool_execution_sandbox.py` (and its async sibling in `letta/services/tool_sandbox/local_sandbox.py`). The relevant block is `run_local_dir_sandbox_directly`, `tool_execution_sandbox.py:255-316`:

```python
def run_local_dir_sandbox_directly(self, ...):
    ...
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_stdout, captured_stderr = io.StringIO(), io.StringIO()
    sys.stdout = captured_stdout
    sys.stderr = captured_stderr
    try:
        with self.temporary_env_vars(env):
            with open(temp_file_path, "r", encoding="utf-8") as f:
                source = f.read()
            code_obj = compile(source, temp_file_path, "exec")
            globals_dict = dict(env)
            globals_dict["__name__"] = "__main__"
            globals_dict["__file__"] = temp_file_path
            exec(code_obj, globals_dict)
            ...
```

**This is `exec()` in-process** with `sys.stdout`/`sys.stderr` redirected. There is no process isolation, no filesystem confinement, no capability restriction. The tool code can:

- Read `os.environ` (and it gets a populated env dict).
- Spawn subprocesses via `subprocess.Popen` or `os.system`.
- Open arbitrary sockets.
- Read or write any file the Letta process can reach (which is everything the host user can).
- Mutate Letta's own globals if it imports them.

There is a venv path (`run_local_dir_sandbox_venv`) that *does* use `subprocess.run` with a fresh interpreter, plus `timeout=60`. That is real process isolation but no filesystem confinement; the subprocess inherits the parent's filesystem view.

The doc comments on the class (line 39-50) make clear that `LOCAL_SANDBOX_RESULT_*` markers are used to separate the function's return value from arbitrary stdout. They are random uuids generated at module load, which prevents trivial spoofing by tool code that happens to print a guess. That is the only marker discipline.

**The E2B path** (lines 92-128, full path: try E2B, fall back to local) — when an E2B API key is configured, the tool runs in an E2B isolate. E2B's sandbox guarantees are real (it's a Firecracker-based microVM). But: the fallback to local happens silently if E2B fails. An operator who configured E2B and assumes their tools always run isolated is wrong — a transient E2B outage means tools run in-process.

**Invariant Letta promises about tool execution:** Tool execution returns a `ToolExecutionResult` (`tool_execution_result.py`) with `status`, `func_return`, `stdout`, `stderr`, `sandbox_config_fingerprint`. The return shape is well-typed.

**Invariant Letta does NOT promise about tool execution:**
- No promise that "sandbox" means process-isolated.
- No promise that a tool cannot read environment variables (the env *is the credential store* — see §7).
- No promise that a failed remote sandbox doesn't fall back to local execution.

**The `assert orig_memory_str == new_memory_str, "Memory should not be modified in a sandbox tool"`** at `sandbox_tool_executor.py:138` is a sanity check, not an invariant. It crashes the request if violated. Memory mutation by a tool would only happen if the tool's own code referenced the agent_state object directly (which the sandbox grammar discourages but does not prevent — `agent_state_copy` is a deepcopy and `tools=[]` is set on the copy, but the copy is still passed in).

---

## 7. Credential handling — env-var-shaped, scoped by sandbox config

LLM provider credentials in Letta are managed in two layers:

1. **Provider-level "BYOK" credentials** stored encrypted in the DB (`letta/services/provider_manager.py` handles enc/dec). Per-org, per-provider.
2. **Sandbox-level env vars** stored in `sandbox_configs` (per-config) and merged into the tool execution env at call time.

The `get_byok_overrides` pattern across `llm_api/*_client.py` returns `(api_key, ..., ...)` triples for the configured provider. Examples:

- `letta/llm_api/openai_client.py:177`: `api_key, _, _ = self.get_byok_overrides(llm_config)`
- `letta/llm_api/anthropic_client.py:431`: `api_key, _, _ = self.get_byok_overrides(llm_config)`

Fallback chain (openai): `byok_key → model_settings.openai_api_key → os.environ['OPENAI_API_KEY'] → "DUMMY_API_KEY"`. The dummy-key fallback is for embedding endpoints behind a permissive gateway. It is mildly surprising — a misconfigured caller can end up sending `"DUMMY_API_KEY"` to an attacker-controlled endpoint and not notice.

**Sandbox env injection** is the key risk vector. `sandbox_tool_executor.py:44-62`:

```python
credentials_service = SandboxCredentialsService()
fetched_credentials = await credentials_service.fetch_credentials(
    actor=actor,
    tool_name=tool.name,
    agent_id=agent_state.id if agent_state else None,
)
if sandbox_env_vars is None:
    sandbox_env_vars = {}
if agent_state and agent_state.project_id:
    fetched_credentials["PROJECT_ID"] = agent_state.project_id
sandbox_env_vars = {**fetched_credentials, **sandbox_env_vars}
```

Credentials are fetched per-tool from `SandboxCredentialsService`. The service may also call webhooks (the codebase has `WEBHOOK_SETUP.md`) to dynamically resolve credentials. That webhook is a network dependency; if it is down, the tool runs without the credential and may produce surprising behavior.

The credentials are merged into the env that is then handed to the sandbox subprocess (venv path) or the local `temporary_env_vars` (in-process path). **In the in-process path, the credentials are in `os.environ` for the duration of the tool run** — which means any concurrent thread of the Letta server can read them. The `temporary_env_vars` context manager (`tool_execution_sandbox.py:115-122`) restores the original env on exit, but during the run, the global env is mutated. Async tool execution + multi-worker = a real race window.

**Credential invariant Letta promises:** Credentials live in the DB (encrypted) and are decrypted at request time. They are not logged at INFO level. They are passed via env, not via command line (so they don't show up in `ps`).

**Credential invariant Letta does NOT promise:**
- That credentials are not in `os.environ` of the parent process during tool execution.
- That a buggy tool cannot read another tool's credentials via the env dict.
- That credentials are not in stack traces (the friendly error message at `_handle_execution_error` truncates, but stack traces may include the env via `inspect.getclosurevars` in some libraries).

---

## 8. The ORM — transaction safety and deadlock handling

`letta/orm/sqlalchemy_base.py:40-110` defines the deadlock retry decorator and the timeout-to-typed-result conversion. This is competent work: PostgreSQL `40P01` (deadlock) gets a retry with exponential backoff; statement timeouts get folded into `DatabaseTimeoutError`. The handlers at `app.py:613-650` translate these to 409 / 503 responses with `Retry-After` headers.

**Invariant Letta promises:** A deadlock results in either a successful retry (up to `_DEADLOCK_MAX_RETRIES=3`) or a 409 with `Retry-After: 1`. A statement timeout results in a 503.

**Weakness:** the retry policy is module-level (not per-endpoint). A retry on a non-idempotent write (e.g., `POST /v1/agents/{id}/messages` retrying after a deadlock) could double-post a message if the first attempt actually committed. The decorator does not seem to distinguish committed vs. uncommitted failures. This is a real concern under load.

---

## 9. The OpenAPI surface and the SDK

Letta generates an OpenAPI schema at `app.py:136-162` (`generate_openapi_schema`) and writes it out for SDK generation via Fern (`fern/`). The result is two SDKs:

- Python SDK (under `letta-client` on PyPI)
- TypeScript SDK

Both consume the OpenAPI schema directly. This is the right pattern — types travel from server to client without hand-rolling.

**Weakness identified:** The OpenAPI schema is *generated*, not handwritten, which means any non-OpenAPI-expressible invariant (e.g., "this list must be non-empty if this other field is present") is lost. The Python SDK trusts the types but does not enforce business rules. A caller can construct a `CreateAgentRequest` with internally inconsistent fields; the server rejects it with 422 (handled at `app.py:602`), but the round-trip is wasted.

---

## 10. The named weak points (so they exist)

I name each one so it lands in [[50_verification/LETTA_RISK_REGISTER]]:

- **Weak point W-LET-01**: Secure mode is opt-in. The default OSS deployment has no auth.
- **Weak point W-LET-02**: A single global password for all callers in secure mode. No per-user identity in the OSS auth path.
- **Weak point W-LET-03**: No inbound rate limiting. Caller is responsible for adding one.
- **Weak point W-LET-04**: Local sandbox is in-process `exec()` with no real isolation.
- **Weak point W-LET-05**: Silent fallback from remote sandbox (E2B/Modal) to local sandbox on remote failure.
- **Weak point W-LET-06**: Tool execution env contains org-scoped credentials in `os.environ` of the parent process (race window for concurrent reads in async/worker contexts).
- **Weak point W-LET-07**: No documented partial-stream-on-disconnect handling (no equivalent to Hermes I-18).
- **Weak point W-LET-08**: Two parallel auth code paths (middleware + `get_current_user`) with inconsistent use across routers.
- **Weak point W-LET-09**: `internal_*` routers exist in OSS code and have weaker scope checks.
- **Weak point W-LET-10**: Deadlock retry policy is module-level and does not distinguish committed vs. uncommitted failures (potential double-write).
- **Weak point W-LET-11**: OpenAPI-generated SDKs lose non-OpenAPI-expressible business rules — clients can construct invalid requests that round-trip to the server before failing.
- **Weak point W-LET-12**: `assert` statements (e.g., the memory-not-modified assert at `sandbox_tool_executor.py:138`) used for runtime safety; these are stripped when Python is run with `-O`.

---

## 11. What Hermes already does differently

The Hermes Codex has invariants we can cross-walk:

- **I-25 (Redaction-on-default + CLI-only opt-out)**: Letta has no equivalent. Letta logs LLM provider responses verbosely; redaction is the operator's problem.
- **I-29 (Allowlist required for non-loopback bind)**: Letta has no equivalent. The default Docker deploys bind to `0.0.0.0`.
- **I-18 (Interrupted partial replies persist with marker)**: Letta has no equivalent.
- **I-13 (Tool tools never see Well credentials)**: Letta's local sandbox path is the *opposite* of this — tools get the org credential env.
- **I-30 (Stdout writes are line-atomic under contention)**: Letta does not have a JSON-line protocol on stdout; it has a FastAPI HTTP surface. The analog would be "JSON response writes are not interleaved" which is FastAPI's responsibility.
- **I-11 (Disconnected is a typed value)**: Letta uses HTTP exception handlers (`@app.exception_handler(...)`). This is *similar* in spirit but a different mechanism. The handler approach captures the exception → response path correctly. The weakness is consistency: not every error type has a registered handler, so some uncaught exceptions fall through to FastAPI's 500.

---

## 12. What Ember should treat as load-bearing if she ever exposes a remote surface

If Ember ever lands Bifröst (network-exposed) or a Gjallarhorn-style remote control surface, the following are non-negotiable:

1. **Auth is on by default** (Hermes I-29 generalized). The "off by default" pattern Letta uses is a footgun.
2. **Per-caller identity** (not a shared password). Even a single-user setup should have per-device-paired tokens for revocability.
3. **Inbound rate limiting** at the surface — not delegated to the operator's reverse proxy. The bind-time refusal pattern from Hermes ("allowlist required") generalizes to "rate-limit required."
4. **Tool execution is *always* in a subprocess or stronger** — no `exec()` in-process. The venv path is the floor.
5. **Sandbox fallback is explicit, not silent.** If E2B-style remote sandbox is configured and fails, the call should fail closed, not fall back to local.
6. **Credentials never enter the parent's `os.environ`.** Pass credentials as an explicit env dict to a subprocess, not by mutating the global env.
7. **Disconnected/interrupted stream → typed marker in the persisted reply** (Hermes I-18). Letta lacks this; Ember should keep it.

---

## What This Means for Ember

**Subsystems touched:** Strengr (if Ember ever exposes a network surface), Brunnr (multi-tenancy of memory), Munnr (the interactive surface), and any tool execution layer Smiðja-side.

**Vows touched:**

- **Tethered Grounding**: Letta's tool sandbox in-process `exec()` violates the spirit of "grounded actions." Ember must keep tools subprocess-isolated.
- **Defended System Prompt (candidate)**: Letta does not separate "system prompt" from "memory blocks" cleanly at the API level — a block edit can rewrite the system context. Ember should keep that boundary explicit.
- **Public-Friendliness**: Letta is reachable by network by default. Public-friendliness for Ember means "no surprises when published," which translates to auth-on, rate-limited, allowlist-required.

**Hermes Codex docs reinforced:** [[hermes_codex/50_verification/54_SECURITY_REVIEW]] §2.2 (network bind discipline), [[hermes_codex/50_verification/55_INVARIANT_LIST]] I-25/I-29 (redaction + allowlist), [[hermes_codex/20_interface/25_GATEWAY_INTERFACE]] §3 (opaque identity).

**Hermes Codex docs contradicted:** None directly. Letta provides confirming evidence that the Hermes patterns are the right discipline. Where Hermes is stricter (subprocess-by-default, redaction-by-default), Letta is looser.

**Decision-ready directives:**

1. If Ember reuses any Letta tool code, it must run that code only in a subprocess sandbox with no inherited credentials. Adapter code lives in Strengr; sandbox lives in Smiðja or a new True Name.
2. Ember must not adopt the Letta auth model. If a network surface is added, follow Hermes's allowlist-required pattern, not Letta's opt-in password.
3. The "silent fallback from remote to local sandbox" pattern is an antipattern — to be added to [[50_verification/CROSS_ANTIPATTERN_CATALOG_V2]].
4. The `assert` for runtime safety is an antipattern — to be added to the same catalog.

Letta is a server. Ember is not (yet) a server. The asymmetry teaches: do not become a server until the auth, rate-limit, identity, and sandbox stories are all green. None of Letta's six are green by default.
