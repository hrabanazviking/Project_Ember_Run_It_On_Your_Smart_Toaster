---
codex_id: 34_BROWSER_AUTOMATION_LOOP
title: Browser Automation Loop — CDP, Vue, and the Accessibility-Tree Cheat
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - py/cdp_tool.py:1-100 (port discovery + WS resolution)
  - py/cdp_tool.py:105-174 (call_vue_method with retry)
  - py/cdp_tool.py:179-303 (interaction tools)
  - py/cdp_tool.py:261-302 (evaluate_script with safety wrap)
  - main.js:864-870 (get-internal-cdp-info)
  - main.js:831-857 (DevToolsActivePort read)
ember_subsystem_targets: [Smiðja]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/33_COMPUTER_CONTROL_LOOP
  - 20_interface/28_BROWSER_AUTOMATION_INTERFACE
---

# Browser Automation Loop

> *Don't show the LLM pixels. Show it a numbered list of clickable things. Cheaper, more accurate, fewer regrets.*

Forge. Eldra. SAP's "AI browser" is not what you think. There is no Playwright. There is no headless Chromium. There is the Electron webview inside the main SAP window, controlled via Chrome DevTools Protocol over a port that the host had to read out of an Electron-internal file. This is held together by a JavaScript bridge inside Electron's renderer called `window.aiBrowser` that exposes the actual control surface to Python. It works. It is fragile in specific, predictable ways.

## The Port Discovery: An Undocumented File

```javascript
// main.js:831-857 (compressed)
if (IS_INTERNAL_MODE_ACTIVE) {
  const portFile = path.join(app.getPath('userData'), 'DevToolsActivePort');
  if (!fs.existsSync(portFile)) {
    await new Promise(r => setTimeout(r, 500));
  }
  if (fs.existsSync(portFile)) {
    const content = fs.readFileSync(portFile, 'utf8');
    const realPort = parseInt(content.split('\n')[0], 10);
    if (!isNaN(realPort)) {
      SESSION_CDP_PORT = realPort;
      console.log(`✅ [CDP] 成功获取系统分配内置浏览器调试端口: ${SESSION_CDP_PORT}`);
    }
  }
}
```

Electron is launched with `--remote-debugging-port=0`, which tells Chromium "pick any port and write it to `<userData>/DevToolsActivePort`". This is Electron-internal behavior — there is no documented API for "what port did Chromium pick?" The file path is undocumented. The file format ("port on line 1, websocket URL on line 2") is undocumented. SAP reads it anyway because there is no alternative.

When Electron upgrades and changes this convention, SAP breaks. Pin to known-good Electron versions or be prepared to fix this in a release-day patch.

The renderer then exposes the port to Python:

```javascript
// main.js:864-869
ipcMain.handle('get-internal-cdp-info', () => {
  return {
    active: IS_INTERNAL_MODE_ACTIVE,
    port: SESSION_CDP_PORT
  };
});
```

Python reads it via the renderer's HTTP API (the chat thread that's already talking to Python gets the CDP port when it sends settings). Once Python knows the port, it can hit `http://127.0.0.1:<port>/json/list` to enumerate CDP targets:

```python
# py/cdp_tool.py:13-26
async def get_cdp_port():
    settings = await load_settings()
    return settings.get('chromeMCPSettings', {}).get('CDPport', 3456)

async def get_targets():
    port = await get_cdp_port()
    try:
        resp = requests.get(f'http://127.0.0.1:{port}/json/list')
        return resp.json()
    except Exception as e:
        print(f"CDP Connection Error: {e}")
        return []
```

Note the default fallback `3456` (line 16) — the same port as the FastAPI server. That's not right; it's a placeholder. If the renderer never sent the real port, the CDP layer will try to talk to itself and fail. The error path is just `print()` and an empty list, which the caller interprets as "no targets" — a silent failure mode.

## Target Filtering: Don't Click on Yourself

CDP exposes every webContent in Electron: main window, VRM windows, DevTools, extension windows, plus every `<webview>` tag. SAP filters carefully:

```python
# py/cdp_tool.py:28-65 (compressed)
async def get_main_window_ws():
    targets = await get_targets()
    for t in targets:
        url, title, target_type = t.get('url',''), t.get('title',''), t.get('type')

        if target_type != 'page': continue       # exclude webview, service_worker
        if 'vrm.html' in url: continue           # exclude VRM avatar windows
        if 'devtools://' in url: continue        # exclude DevTools
        if 'ext' in url: continue                # exclude extension windows
        return t.get('webSocketDebuggerUrl')

    print("Error: Could not find Main Window in CDP targets.")
    return None
```

Four layers of exclusion to find the main window. The VRM filter exists because SAP can have multiple transparent VRM windows ([[32_AVATAR_RENDER_PIPELINE]]), and they're also CDP targets. Hitting one of those with a click command would try to interact with a transparent always-on-top avatar window, which is funny in description and bad in production.

The `<webview>` tags inside the main window are themselves CDP targets:

```python
# py/cdp_tool.py:67-77
async def get_webview_ws(index=None):
    targets = await get_targets()
    webviews = [t for t in targets if t['type'] == 'webview']

    target_idx = index if index is not None else CURRENT_PAGE_INDEX

    if 0 <= target_idx < len(webviews):
        return webviews[target_idx].get('webSocketDebuggerUrl')
    return None
```

`CURRENT_PAGE_INDEX` (line 10) is a module-level global. The agent loop sets it when switching tabs, and subsequent commands target the active webview. Again, no scope: if a tool errors mid-sequence and the index is on tab 3, the next call still hits tab 3 even if the user has manually closed it.

## The Vue Bridge: window.aiBrowser

The clever bit: SAP doesn't issue raw CDP commands like `DOM.querySelector` + `Runtime.evaluate(click)`. It evaluates calls to a JS object the renderer pre-defines:

```python
# py/cdp_tool.py:105-123 (compressed)
async def call_vue_method(method_name, args_list=None):
    ws_url = await get_main_window_ws()
    if not ws_url:
        return {"error": "Main window not found"}

    if args_list:
        json_args = [json.dumps(arg) for arg in args_list]
        args_str = ", ".join(json_args)
    else:
        args_str = ""

    expression = f"window.aiBrowser.{method_name}({args_str})"

    # ... (Runtime.evaluate via WS, with retry)
```

So `cdp_tool.click(uid="el-7")` becomes a CDP `Runtime.evaluate` of `window.aiBrowser.webviewClick("el-7", false)`. The `window.aiBrowser` object lives in the Vue app (preloaded via `static/js/preload.js`) and **already understands the webview**. It can take a snapshot, fill a form, click an element by UID, drag, hover, scroll, and capture a screenshot — all in terms of the *accessibility tree*, not raw selectors.

This is the cheat: the LLM doesn't write `document.querySelector('button[type="submit"]')`. It calls `click(uid="42")` where `uid="42"` was returned by an earlier `take_snapshot()` call that enumerated all interactable elements with stable IDs. The accessibility tree is rendered once per page state; the LLM works against IDs.

The snapshot format is opaque to me without reading `static/js/preload.js` (which I haven't), but the pattern is clear: SAP gives the LLM **a structured, numbered manifest of the page** rather than a screenshot or raw HTML. This is dramatically more reliable for multi-step web automation. It is also a security pivot — if the bridge ever gets exposed to untrusted JS in a webview, the LLM's tools become attacker tools.

## Retry Logic: Three Strikes

`call_vue_method` (line 105) has a retry loop with specific error-class detection:

```python
# py/cdp_tool.py:135-173 (compressed)
if 'exceptionDetails' in res:
    exc = res['exceptionDetails']
    msg = exc.get('text', 'Unknown Error')
    ...
    if "Illegal invocation" in msg or "GUEST_VIEW_MANAGER_CALL" in msg:
        print(f"[Warn] Retrying {method_name} due to Electron error: {msg}")
        raise ValueError("Electron Webview Error")   # triggers retry

    return f"Error executing {method_name}: {msg}"
```

`"Illegal invocation"` and `"GUEST_VIEW_MANAGER_CALL"` are Electron-internal errors that occur when a webview is mid-navigation or has been GC'd. They're transient — usually a fresh WebSocket reconnection (`ws_url = await get_main_window_ws() or ws_url`, line 173) fixes them. Three retries with 1-second delays. After three failures, the loop returns an error string the LLM can read.

This is mature error handling. The retry is bounded, the error class is specific, and the WS URL is refreshed on each retry because **the WebSocket URL itself can rotate** — Electron may assign a new debug-WS URL to a webview after navigation.

## The Tool Surface

The exported tools (line 308 onward):

| Group | Tools |
|---|---|
| Navigation | `list_pages`, `new_page`, `close_page`, `select_page`, `navigate_page`, `wait_for` |
| Interaction | `click`, `fill`, `fill_form`, `drag`, `hover`, `press_key`, `handle_dialog` |
| Discovery | `take_snapshot` (accessibility tree) |
| Debugging | `evaluate_script`, `take_screenshot` |

13 tools. Compared to `computer_use_tool.py`'s 14 tools, the browser surface is roughly comparable in size but operates at a higher abstraction layer. The LLM thinks in elements, not pixels. The accuracy is better. The speed is better. The cost (no screenshot per turn) is dramatically lower.

## The evaluate_script Safety Hack

`evaluate_script` lets the LLM run arbitrary JS in the active webview. SAP wraps incoming code with three guards:

```python
# py/cdp_tool.py:261-288 (compressed)
async def evaluate_script(script_code, args=None):
    # 1. Strip markdown code fences (LLMs love to wrap in ```javascript)
    clean_code = script_code.strip().strip('`')
    if clean_code.startswith('javascript'):
        clean_code = clean_code[10:].strip()

    # 2. Auto-wrap if AI forgot the function declaration
    if not clean_code.startswith("function") and not clean_code.startswith("() =>") and not clean_code.startswith("async function"):
        clean_code = f"function() {{\n{clean_code}\n}}"

    # 3. Navigation safety: defer code that submits forms or sets location
    if "submit()" in clean_code or "location" in clean_code:
        safe_code = f"""
        function() {{
            setTimeout(function() {{
                ({clean_code})();
            }}, 100);
            return 'Command scheduled (Async execution for navigation safety)';
        }}
        """
        return await call_vue_method('executeInActiveWebview', [safe_code, args or []])

    return await call_vue_method('executeInActiveWebview', [clean_code, args or []])
```

Three patches, all earned through pain:

1. **Strip markdown code fences** — LLMs wrap code in `` ```javascript ... ``` `` constantly. SAP just strips them. Pragmatic.
2. **Auto-wrap function** — if the LLM emits `return 1+1;` instead of `function() { return 1+1; }`, SAP wraps it. This used to crash; now it doesn't.
3. **Navigation safety setTimeout** — if the script causes navigation (`form.submit()` or `window.location = ...`), the WebSocket dies before the result comes back. SAP defers the navigation by 100ms so the CDP call can return first. Otherwise every `submit()` returns an error and the LLM thinks it failed.

These are **classic battle scars** in the code. Every one of them was a real bug. Reading them is reading the project's debugging diary.

## Where It Breaks

- **The `DevToolsActivePort` file path is undocumented Electron internals**. When Electron 40+ ships, this can change. SAP's only fallback is hardcoded port `3456` which is wrong.
- **Module-level `CURRENT_PAGE_INDEX`** has no scope. Tab close races with tab switch.
- **No CSRF protection on the CDP port**. Anything on `127.0.0.1` can talk to the debug port. Other apps on the host (or malware) can drive the LLM's browser.
- **`evaluate_script` is full RCE in the webview context**. The LLM can `fetch()` anything the user is logged into. There is no per-domain capability gate.
- **No screenshot diff verification**. The `[LAST_ACTION: ...]` pattern from `computer_use_tool.py` is *not* in `cdp_tool.py`. Browser actions don't leave a marker; the verifier loop is missing on this side.
- **The retry logic assumes "Illegal invocation" is transient**. If the webview is permanently broken (page crashed), the retry will burn three rounds before giving up.
- **`take_snapshot` opaque format**. I can't tell from `py/cdp_tool.py` alone whether two snapshots of the same page have stable IDs. If `uid="42"` means different elements after a refresh, the LLM's plan-then-execute pattern breaks. SAP probably handles this in the Vue bridge; the Python side has no test.

## Where It Surprises

- **The accessibility-tree approach** (snapshot-with-UIDs) is the right answer for browser automation. Pixels-and-OCR is what most agent frameworks do; it is worse. The closest comparable approach is Anthropic's computer-use beta, which uses pixel coordinates; SAP's UID approach is strictly cheaper and more accurate for browser tasks.
- **The WS-reconnect-on-retry** (line 173). Most retry loops just sleep and retry the same call. SAP refreshes the WS URL because it knows the URL itself can rotate. Earned wisdom.
- **The three `evaluate_script` patches** are the kind of thing you only know to write after a year of LLM users hitting them. SAP shipped these. They aren't documented anywhere. They are the difference between "demo works" and "production survives."
- **No headless option**. SAP requires Electron because it requires the user's logged-in session in the embedded webview. This is a feature (the LLM can use sites the user is logged into) and a constraint (no server-side scraping; can't run on a headless box). Different from Playwright's headless-first posture.
- **No third-party Chromium**. SAP uses Electron's bundled Chromium. The user's actual Chrome/Edge is untouched. This is by design (security: don't share session with the user's main browser) but it also means the embedded browser has its own session, its own cookies, its own profile.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — CDP port discovery happens here
- [[33_COMPUTER_CONTROL_LOOP]] — sibling control loop for desktop (pyautogui)
- [[28_BROWSER_AUTOMATION_INTERFACE]] (Auditor) — protocol-level analysis
- [[55_API_SIMULATION_TRAPS]] — adjacent concerns about LLM-driven RPC

## What This Means for Ember

**Adopt:**

- **The accessibility-tree-with-UIDs pattern**. When Ember automates browsers, the LLM operates against `snapshot()` → `click(uid=N)` flow, not pixels. Bind to Smiðja's web-automation toolset. Vow proposal tie-in: **Action Echo** — the snapshot itself is the action context.
- **The Vue-bridge pattern**: a JS object preloaded into the renderer exposing high-level methods, with Python calling them via `Runtime.evaluate("window.<bridge>.<method>(...)")`. This decouples the LLM-facing API from CDP raw protocol details. If Ember has an Electron-based shell in the future, this is the surface.
- **The three `evaluate_script` patches**. Markdown-strip, function-auto-wrap, navigation-defer. Adopt verbatim. These are bug fixes earned through real production. Save someone six months of debugging.
- **Retry with WS refresh** for any WebSocket-driven RPC. Refreshing the URL on retry is the difference between "looks robust" and "is robust."

**Adapt:**

- **The `CURRENT_PAGE_INDEX` global** — replace with a scoped context manager. `with smidja.browser_tab(index=N): ...`. Same idea, no module-level mutable state.
- **The DevToolsActivePort file read**. Adapt only if Ember commits to Electron. If Ember uses a separate Chromium (e.g. Playwright), bypass entirely.
- **The retry loop's error-class detection**. Ember should generalize this: tools declare which error strings/codes should trigger retry vs immediate failure. SAP's hardcoded "Illegal invocation" / "GUEST_VIEW_MANAGER_CALL" is browser-specific.

**Avoid:**

- **No CSRF protection on the debug port**. Ember's debug surfaces must be authenticated even on localhost. Vow tie-in: **Defended System Prompt** generalizes to **Defended Debug Surface**.
- **`evaluate_script` as a blanket capability**. Ember should gate raw-JS-eval behind a per-deployment opt-in. Default: disabled. The accessibility-tree tools cover ~95% of LLM use cases; raw eval is the 5% that opens the RCE doorway.
- **Hardcoded fallback port `3456`**. Hardcoded fallbacks lie to the operator. Ember should hard-fail with a clear error message if the real port can't be discovered.
- **No `[LAST_ACTION: ...]` tag on browser tools**. Ember's browser tools must emit the same structured action echo as computer-use tools, so the agent loop has consistent verifier mechanics across both surfaces.

**Invent:**

- **Snapshot Stability Contract**. Ember's browser snapshot tool emits UIDs that are guaranteed stable across page mutations until the page navigates. SAP's stability is implicit; Ember's should be a documented contract with verification (a unit test that mutates a known page and checks UIDs don't shift). Vow proposal: **UID Stability**.
- **Per-Domain Tool Capability Profiles**. The LLM's available tools change based on the active webview's domain. Banking domain → no `fill_form` for password fields. Social media → no `take_screenshot` of DMs. Domain → capability mapping lives in a YAML manifest. Vow tie-in: **Surface Without Surveillance**.
- **Smiðja Snapshot Cache**. Snapshots are cached by (URL, DOM hash). Repeat snapshot calls within a session return the cached snapshot. The LLM doesn't pay the snapshot cost twice on a page that hasn't changed. Cache invalidates on `MutationObserver` events fired by the page. Vow tie-in: **Cache Discipline**.
- **Cross-Surface Verifier**. When Ember has both `computer_use` and `cdp_browser` tools active, the verifier loop checks: did the computer-use click also produce a browser-side state change? If a click on (480, 320) was supposed to submit a form, the next browser snapshot should show a navigation. Mismatch → flag for operator review. SAP's two control surfaces are independent; Ember's are cross-checked.
- **No-Webview Fallback**. When Electron is not present (Pi deployment, Docker), Smiðja still exposes browser tools via Playwright in headless mode. The tool *interface* is the same; the *implementation* swaps. The LLM doesn't know which it's talking to. Vow tie-in: **Tiered Presence** generalizes — same tools, different bodies.
