---
codex_id: 29_TOOL_TYPE_INTERFACE
title: Tool Type Interface — Four Tool Families, Four Trust Models, Zero Shared Validation
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/code_interpreter.py:1-92
  - py/comfyui_tool.py:1-217
  - py/custom_http.py:1-41
  - py/computer_use_tool.py:1-150
  - py/mcp_clients.py:135-167
ember_subsystem_targets: [Smiðja]
cross_refs:
  - 10_domain/19_TOOL_DOMAIN
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/55_API_SIMULATION_TRAPS
  - 50_verification/58_OBSERVABILITY_GAPS
---

# Tool Type Interface — Four Tool Families, Four Trust Models, Zero Shared Validation

> *Sólrún, voice cold and even: SAP has four ways to give the LLM a tool. Each family arrived in a different year, written by a different author, with a different idea of what "validated input" means. The only thing they share is the OpenAI-tool-schema dictionary shape. Below the schema, every family is its own country.*

This document audits the four tool families SAP exposes to the model:

- **Code Interpreter** (`code_interpreter.py`) — execute Python/JS/etc. in E2B sandbox or local container
- **ComfyUI Tool** (`comfyui_tool.py`) — submit an image-generation workflow to a ComfyUI instance
- **Custom HTTP** (`custom_http.py`) — arbitrary HTTP request
- **Computer Use** (`computer_use_tool.py`) — mouse, keyboard, screenshot on the host desktop

Plus the **MCP tool family** (`mcp_clients.py:135-157`) for context. All five families converge on `[{"type": "function", "function": {...}}]` at the LLM's input. Below that, they diverge wildly.

---

## 1. The Subject — One Schema Shape, Five Trust Models

Every tool in SAP exposes itself via OpenAI tool-schema:

```python
# /tmp/super-agent-party/py/code_interpreter.py:41-63 (e2b_code_tool)
e2b_code_tool = {
    "type": "function",
    "function": {
        "name": "e2b_code",
        "description": "执行代码，工具只会返回stdout和stderr。请将你要查看的答案输出到stdout。",
        "parameters": { ... }
    },
}
```

Same shape for all five families. The shape is the *output*; the *input* mechanism differs dramatically:

| Family | Wire mechanism | Trust model | Sandboxed? |
|---|---|---|---|
| `code_interpreter.py` | E2B remote sandbox (`Sandbox(api_key=...)`), or local HTTP `POST /run_code` | E2B service or local sandbox container | Yes (E2B) / Maybe (local) |
| `comfyui_tool.py` | HTTP POST to ComfyUI server, sync polling for result | None — server is trusted | No |
| `custom_http.py` | Arbitrary HTTP via aiohttp | None — URL is whatever the model says | No |
| `computer_use_tool.py` | `pyautogui` calls on the host | None — direct OS access | No |
| `mcp_clients.py` | MCP stdio/sse/ws/streamablehttp protocol | MCP server's | Per-server |

These are not five tool types. They are five **fundamentally different trust boundaries** with one common labeling scheme. The LLM sees five sets of nicely-described functions and has no way to know that one runs in a Firecracker microVM and another mouse-clicks the operator's actual desktop.

---

## 2. `code_interpreter.py` — Trust E2B Or Trust Yourself

`code_interpreter.py:6-18`:

```python
# /tmp/super-agent-party/py/code_interpreter.py:6-18
async def e2b_code(code: str, language: str = "Python") -> str:
    settings = await load_settings()
    e2b_api_key = settings["codeSettings"]["e2b_api_key"]
    executor = ThreadPoolExecutor()
    def run_in_sandbox():
        with Sandbox(api_key=e2b_api_key) as sandbox:
            execution = sandbox.run_code(code,language=language)
            return execution.logs

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_in_sandbox)
    return str(result)
```

E2B is a real microVM service. The trust model is honest: code goes to a remote ephemeral VM, runs, returns. The leakage risk is that the *code itself* — written by the LLM with whatever context it had — leaves the host. If the LLM was given access to user secrets (env vars, file contents), it might embed them in the code as a string literal and exfil to E2B's logs.

`code_interpreter.py:24-39` shows the local-sandbox path:

```python
# /tmp/super-agent-party/py/code_interpreter.py:24-39
async def local_run_code(code: str, language: str = "python") -> str:
    settings = await load_settings()
    url = settings["codeSettings"]["sandbox_url"].strip("/") + "/run_code"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "code": code,
        "language": language
    }

    async with ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            result = await response.text()
            return result
```

`sandbox_url` defaults to `http://127.0.0.1:8080` (per `settings_template.json:181`). The user is expected to run a sandbox container (e.g. `oj-sandbox` or similar) at that URL. **There is no auth header**. Any process on localhost can POST `/run_code` and execute arbitrary code in whatever sandbox the user has set up. If the sandbox is hardened, fine. If the sandbox is `docker run -v /:/host ...` (a common amateur mistake), the LLM just got root on the host.

The interface doesn't tell the LLM which mode is active. The same `local_run_code` tool name shows up regardless of how dangerous it is.

### 2.1 Language list mismatch

`code_interpreter.py:54-58` — `e2b_code_tool` declares languages: `["python", "js", "ts", "r", "java", "bash"]`. `code_interpreter.py:81-86` — `local_run_code_tool` declares 31 languages including `cuda`, `verilog`, `lean`, `swift`, `racket`. The LLM, given both, will switch tools based on language availability — which is fine — but the *security profile* of running `cuda` in a remote E2B vs. local sandbox is entirely different. There's no signal to the LLM about this.

---

## 3. `comfyui_tool.py` — Three Distinct Bugs Per Call

`comfyui_tool.py:212-214`:

```python
# /tmp/super-agent-party/py/comfyui_tool.py:212-214
    image_path_list = get_all(prompt,server_address,settings)

    image_path_list = get_all(prompt,server_address,settings)
```

**Two identical calls.** The first call generates the image. The second call generates *another* image with the same seed (`comfyui_tool.py:200-210` — seeds are re-randomized at line 203 and 209 only when present in workflow config, so a workflow without seed config will run twice with the same prompt and produce the same image).

This is a textbook copy-paste accident. The second call overwrites the first's `image_path_list` variable. The server gets two requests. The user gets one image (presumably; depending on the workflow). The bug has been in the file since whoever pasted it.

`comfyui_tool.py:62-67` — the polling loop:

```python
# /tmp/super-agent-party/py/comfyui_tool.py:62-67
    while True:
        try:
            history = get_history(prompt_id,server_address)[prompt_id]
            break
        except Exception:
            time.sleep(1)
            continue
```

`while True` with `time.sleep(1)` and no upper bound. If the ComfyUI server hangs, this loop runs **forever**. Add to that: `time.sleep` blocks the current thread. The tool was supposed to be called via async; this `time.sleep` blocks an asyncio thread executor for as long as ComfyUI is hung. Add to that: `get_history` uses `urllib.request.urlopen` synchronously (`comfyui_tool.py:52`).

This is synchronous IO inside an async function on a hot loop with no timeout.

### 3.1 Server allocation is racy

`comfyui_tool.py:125-141`:

```python
# /tmp/super-agent-party/py/comfyui_tool.py:125-141
running_comfyuiServers = []

async def comfyui_tool_call(tool_name, text_input = None, image_input = None,text_input_2 = None,image_input_2 = None):
    settings = await load_settings()
    comfyuiServers = settings["comfyuiServers"]
    server_address = ""
    count = 0
    while server_address == "" or count > 30 or comfyuiServers == []:
        await asyncio.sleep(1)
        for server in comfyuiServers:
            if server not in running_comfyuiServers:
                running_comfyuiServers.append(server)
                server_address = server
                break
        count += 1
```

`running_comfyuiServers` is a **module-level list**. Two concurrent `comfyui_tool_call`s both reach line 135 simultaneously. Both see an empty `running_comfyuiServers`. Both pick the same server. Both append it. Both proceed with the same `server_address`. No lock.

Worse, the condition at line 133 is `while server_address == "" or count > 30 or comfyuiServers == []:` — this is a logic bug. If `count > 30`, the loop *continues*. The intent was almost certainly `and count <= 30` (give up after 30 tries). As written, after `count` exceeds 30, the loop continues forever as long as `server_address` is empty. If all servers are busy, the function spins forever. The "30-second timeout" is not a timeout; it is a comment that doesn't match the code.

### 3.2 `seed_input2` not `seed_input_2`

`comfyui_tool.py:200-211`:

```python
    if "seed_input" in using_workflow and using_workflow["seed_input"] is not None:
        ...
    if "seed_input2" in using_workflow and using_workflow["seed_input2"] is not None:
        ...
```

`text_input` and `text_input_2` (underscore-suffixed). `image_input` and `image_input_2`. But `seed_input` and `seed_input2` (no underscore). The user's workflow config keys must inconsistently follow both conventions or one will silently not work.

---

## 4. `custom_http.py` — The 41-Line Backdoor

`custom_http.py:1-41` — the whole module:

```python
# /tmp/super-agent-party/py/custom_http.py:11-41
async def fetch_custom_http(method, url, headers=None, body=None):
    if headers is None or headers == "":
        headers = {}
    elif isinstance(headers, str):
        print(f'headers: {headers}')
        headers = safe_json_loads(headers)

    content_type = headers.get('Content-Type', 'application/json')

    kwargs = {
        'headers': headers,
    }

    if content_type == 'application/json':
        kwargs['json'] = body
    else:
        kwargs['data'] = body

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                print(f'Status: {response.status}')
                response_text = await response.text()
                print(f'Response: {response_text}')
                return response_text
    except Exception as e:
        print(f'Error: {e}')
        return f'Error: {e}'
```

This is an LLM tool that takes arbitrary `method`, `url`, `headers`, and `body`, and executes the HTTP request. There is:

- **No URL validation** — any URL the LLM produces is hit.
- **No private-network protection** — `url='http://169.254.169.254/latest/meta-data/'` reaches AWS metadata service. `url='http://localhost:8000/api/admin/...'` reaches sibling services.
- **No header filter** — the LLM can construct any header, including `Cookie: ...` or `X-Forwarded-For: ...`.
- **No timeout** — `aiohttp.ClientSession()` default timeout is `5*60` seconds. Hung requests hang the call.
- **`print()` of request/response bodies** to stdout — every response body, including headers possibly containing tokens, ends up in the host's stdout.

This is the *worst* tool surface in SAP from a security posture. The model's outbound network access is effectively unlimited, with no observability beyond `print()` and no constraint.

`[[53_SECURITY_REVIEW]]` enumerates the SSRF (Server-Side Request Forgery) class — `custom_http.py` is the textbook example.

---

## 5. `computer_use_tool.py` — The Coordinate-Percent Lie

`computer_use_tool.py:9-30`:

```python
# /tmp/super-agent-party/py/computer_use_tool.py:9-30
GUI_AVAILABLE = False
try:
    import pyautogui
    import pyperclip
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    GUI_AVAILABLE = True
except (KeyError, ImportError, Exception) as e:
    print(f"⚠️ [Warning] 桌面鼠标键盘工具已禁用 (缺少 DISPLAY): {e}")

def require_gui(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not GUI_AVAILABLE:
            return "执行失败：当前系统运行在无头环境(如Docker)中，没有物理显示器，无法执行鼠标和键盘操作。"
        return await func(*args, **kwargs)
    return wrapper
```

The fall-through pattern is honest: in headless environments, the tool returns a string explaining itself. Good. `pyautogui.FAILSAFE = True` is the standard escape-hatch (mouse to upper-left corner aborts). Good.

`computer_use_tool.py:40-61` — the coordinate translation:

```python
# /tmp/super-agent-party/py/computer_use_tool.py:40-61
def _percent_to_pixel(x_percent: float, y_percent: float) -> Tuple[int, int]:
    """内部辅助函数：将千分比 (0 到 1000) 转换为当前屏幕或指定区域的实际像素坐标。"""
    x_percent = max(0, min(1000, float(x_percent)))
    y_percent = max(0, min(1000, float(y_percent)))
    
    if CURRENT_SCREEN_REGION is not None:
        rx, ry, rw, rh = CURRENT_SCREEN_REGION
        px = rx + int(rw * (x_percent / 1000))
        py = ry + int(rh * (y_percent / 1000))
        ...
        return px, py
        
    width, height = pyautogui.size()
    px = min(int(width * (x_percent / 1000)), width - 1)
    py = min(int(height * (y_percent / 1000)), height - 1)
    
    return px, py
```

The LLM uses **per-mille (千分比)** coordinates from 0 to 1000, not the more common percentage 0-100 or normalized 0-1. The choice is unusual; the comment calls it 千分比. The discreteness is one part in 1000, so on a 4K display (3840×2160) one per-mille step is ~4 pixels. Good enough for buttons.

But — `CURRENT_SCREEN_REGION` (`computer_use_tool.py:33`) is **another module-level global**. If two tool calls happen concurrently with different region settings, they race on this global. The percentage-to-pixel translation depends on the region; the region depends on whoever last called `set_screen_region`.

On a multi-monitor system this is worse: `pyautogui.size()` returns the *primary* monitor's size, not the bounding box of all monitors. A click at `(500, 500)` lands on whichever monitor `(width/2, height/2)` of the primary lands on — which may be off-screen on a portrait secondary.

### 5.1 The percentage is not a coordinate; it is a *belief*

The LLM is shown a screenshot. The screenshot covers some monitor at some resolution. The LLM infers a per-mille target. The conversion back to pixels assumes the screenshot was the full primary monitor with no region override. If the screenshot was a region-clipped screenshot (via `visionControlSettings.ScreenSize`, `settings_template.json:206`), the LLM's per-mille is *relative to the clipped image*, but the tool's per-mille translates *relative to whatever region is active right now*.

A click at `(500, 500)` in a screenshot taken with one region, executed in a different region, lands somewhere wrong. There is no per-call region binding.

---

## 6. The MCP Family — The Only Sane One

`mcp_clients.py:135-167` (already shown in [[21_OPENAI_COMPAT_API]] discussion of MCP):

```python
# /tmp/super-agent-party/py/mcp_clients.py:136-157
    async def get_openai_functions(self,disable_tools=[]):
        async with self._lock:
            if not self._conn or not self._conn.session:
                return []
            tools = (await self._conn.session.list_tools()).tools
            self._tools = [t.name for t in tools]
            self._tools_list = [{"name": t.name, "description": t.description,"enabled":True} for t in tools]
            tools_list = []
            for t in tools:
                if t.name not in disable_tools:
                    tools_list.append(
                        {
                            "type": "function",
                            "function": {
                                "name": t.name,
                                "description": t.description,
                                "parameters": t.inputSchema,
                            },
                        }
                    )
            return tools_list
```

The MCP family is the only one of the five that:

- Has a defined wire protocol (MCP)
- Has an actual lock around tool calls (`self._lock`)
- Returns typed errors instead of returning strings on failure
- Has heartbeat-based connection monitoring (line 119-124)
- Has a callback-on-failure surface

MCP is the right shape. The other four are ad-hoc.

`mcp_clients.py:159-167`:

```python
    async def call_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> Any:
        async with self._lock:
            if not self._conn or not self._conn.session:
                return None
            try:
                return await self._conn.session.call_tool(tool_name, tool_params)
            except Exception as e:
                logging.error("Failed to call tool %s: %s", tool_name, e)
                return "Failed to call tool %s: %s" % (tool_name, e)
```

Still returns a string on exception — which conflates "the call returned the string 'foo'" with "the call failed and we made up a string." But at least it uses `logging.error`, not `print()`. Half-credit.

---

## 7. Cross-References

- [[10_domain/19_TOOL_DOMAIN]] — Architect's domain-axis catalog of all tool modules
- [[50_verification/53_SECURITY_REVIEW]] — `custom_http.py` SSRF, local sandbox auth, `computer_use_tool` operator-impersonation
- [[50_verification/55_API_SIMULATION_TRAPS]] — overlap with OpenAI-compat tool-schema fidelity
- [[50_verification/58_OBSERVABILITY_GAPS]] — `print()` as error channel
- [[20_interface/20_MCP_INTEGRATION]] — Architect's MCP integration story (the positive example)
- [[hermes:HEM-22_TOOL_INTERFACE]] — Hermes's typed tool surface
- [[ember:RULES.AI]] — "make all code robust, crash-proof" — comfyui's `while True` is the violation

---

## What This Means for Ember

**Adopt:**
- Adopt **MCP as the primary tool transport.** The MCP family (`mcp_clients.py`) is the only honest tool surface in SAP. Bind Ember's Smiðja to MCP first; everything else is a degraded mode.
- Adopt the **lazy-load-with-fall-through-to-readable-error** pattern from `computer_use_tool.py:9-30` for any optional dependency. The error message is in Chinese in SAP but the *shape* is right.

**Adapt:**
- Adapt the OpenAI-tool-schema as the *outer* shape — that part is correct. Inside, every tool family declares an explicit *trust class*: `sandboxed`, `host-bound`, `network-arbitrary`, `mcp-mediated`. The LLM is told the trust class. The operator-approval gate keys on trust class. SAP's flat "function" labeling is the negative template.
- Adapt the `running_comfyuiServers` pool-allocation pattern into a proper **`asyncio.Queue`-backed resource pool** with timeout-bounded acquisition. The intent is correct; the implementation is racy and infinite-looping.

**Avoid:**
- **Never expose `fetch_custom_http(method, url, headers, body)` as an unconstrained tool** (`custom_http.py:11`). SSRF is the entire reason private-network allowlists exist. Ember's outbound HTTP tool requires a per-call allowlist match.
- **Never use `while True` with `time.sleep` inside an async function** (`comfyui_tool.py:62-67`). Always bounded retries with `asyncio.sleep`. Always a deadline.
- **Never use module-level globals for resource allocation** (`comfyui_tool.py:125`, `computer_use_tool.py:33`). Pool objects, locks, scoped state — never `module.foo = ...` for mutable.
- **Never duplicate a server-mutating call by copy-paste** (`comfyui_tool.py:212-214`). CI should catch identical adjacent lines.
- **Never call `print()` for error reporting on a network tool** (`custom_http.py:36-39`). Structured logging or nothing.
- **Never let the same tool name front two different trust classes** (`local_run_code` vs `e2b_code` — different security profiles, both labeled "function"). Trust class is part of the tool's identity.
- **Never key clicks on a global `CURRENT_SCREEN_REGION`** (`computer_use_tool.py:33`). Region is per-call.

**Invent:**
- **Tool Trust Class.** Every Ember tool declares one of: `MCP_MEDIATED`, `SANDBOXED`, `HOST_FS_READ`, `HOST_FS_WRITE`, `HOST_PROCESS_EXEC`, `NETWORK_OUTBOUND`, `HOST_UI_CONTROL`. Smiðja's executor gates by trust class. The Vow of **Surface Without Surveillance** demands this — every tool's reach is declared, revocable, and observable.
- **Tool Capability Probe.** When Smiðja registers a tool, it asks: "what do you read? what do you write? what do you call?" The tool returns a structured `Capabilities()` declaration. The probe is run on every Ember start; mismatch with last-known capabilities triggers operator re-approval. SAP's silent "this tool can do anything" is the negative template.
- **Tool Result Provenance.** Every tool result carries: `tool_name`, `trust_class`, `latency_ms`, `bytes_in`, `bytes_out`, `error_class | None`. The LLM sees a structured envelope, not a raw string. Hjarta keys reliability scoring off provenance.
- **SSRF-Resistant HTTP Tool.** Ember's outbound HTTP tool requires `url` to match an operator-approved allowlist. The allowlist is checked at *resolved-IP* time, not URL-string time — so `http://attacker.com/` that resolves to `127.0.0.1` does not bypass. Reject `169.254.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `::1`, `fc00::/7` unless explicitly allowed.
- **Bounded Polling Discipline.** All polling loops are wrapped in a `bounded_poll(call, deadline, max_retries, backoff_strategy)` helper. No `while True` in production tool code. CI lint forbids it.
- **Coordinate Provenance.** Every UI-control tool call carries `(monitor_id, region_id, snapshot_id, click_x, click_y)`. The execution layer validates `(monitor_id, region_id)` matches the live state; mismatch returns `stale_region` and forces a fresh screenshot. SAP's region-as-global is the negative template.
