---
codex_id: 13_COMPUTER_CONTROL_DOMAIN
title: Computer Control Domain — Where the Agent Touches the Host
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/computer_use_tool.py:1-100
  - py/computer_use_tool.py:9-30
  - py/cdp_tool.py:1-100
  - py/cli_tool.py:1-80
  - py/mode_change.py:1-136
  - server.py:3127-3170
ember_subsystem_targets: [Smiðja, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/29_TOOL_TYPE_INTERFACE
  - 50_verification/53_SECURITY_REVIEW
  - 60_synthesis/61_NEW_VOWS
---

# Computer Control Domain
## Where the Agent Touches the Host

*— Rúnhild Svartdóttir, Architect*

> *The hands of a system are the most expensive part to get right. Most builders make them strong before they make them careful, and end up with a system that breaks the table it was meant to set.*

The computer-control domain is the place where SAP stops being a *language* model and starts being a *physical* one — moving the mouse, typing into windows, screenshotting the desktop, opening browser tabs, running CLI commands. This doc inventories the surface, names the gatekeeping that *is* in place, and points at the gates that *should* be in place. It is the most dangerous domain in SAP. It is also one of the better-isolated.

---

## 1. The Subject Itself

**What the domain owns:** the agent's ability to act on the local machine — input simulation, screenshot capture, browser automation through CDP, shell command execution.

**What it does not own:**
- Choosing *whether* to act (that's the LLM)
- Permission gating beyond the per-engine mode setting (there is no per-action consent)
- Audit logging of actions (no central log; printouts go to stdout)
- Sandbox isolation (it has options — `zerobox` Docker, local, ACP — but no enforcement beyond the LLM honoring the setting)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/computer_use_tool.py` | 575 | mouse, keyboard, screenshot — wraps `pyautogui` + `pyperclip` |
| `py/cdp_tool.py` | 559 | Chrome DevTools Protocol — page nav, click by selector, JS eval, screenshots |
| `py/cli_tool.py` | 2,668 | shell command execution — local, Docker (`zerobox`), ACP backends |
| `py/mode_change.py` | 136 | `update_workspace_settings` — toggle engine + permission mode |

Three execution tools, one permission-mode switcher. Total: ~3,940 LOC of host-touching code. That is *the* high-trust surface of SAP.

---

## 2. How It Works

### 2.1 The mouse and keyboard — `py/computer_use_tool.py`

The first 30 lines are the most important in the file:

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

Three pieces of discipline in twenty lines:

- **Lazy import gated by a try/except** — if the GUI libs are missing (no display, Docker, server), the module loads cleanly with `GUI_AVAILABLE = False`. No crash on import.
- **`pyautogui.FAILSAFE = True`** — moving the mouse to a screen corner aborts pyautogui's current command. A human kill-switch.
- **`@require_gui` decorator** — every action function is wrapped; if the GUI is missing, the LLM gets a *string* explaining why the action failed, not a crash, not an exception, not silence.

The coordinate system is interesting: SAP uses **per-mille (千分比)** — 0-1000 — not pixels (`py/computer_use_tool.py:41-61`). `_percent_to_pixel` converts to the current screen size or to a configured region (`CURRENT_SCREEN_REGION` at line 33). The LLM is told "click at (500, 500)" meaning center; the conversion happens locally. This is **resolution-independent prompting** — the same prompt works on a 4K display and a 1080p laptop. Smart.

The active region (`set_screen_region`, line 35) is set by `server.py:3158` based on the current avatar or app context. So the LLM operates inside a *bounded region* of the screen unless explicitly told otherwise.

### 2.2 The browser — `py/cdp_tool.py`

`py/cdp_tool.py:13` `get_cdp_port` reads `settings.chromeMCPSettings.CDPport` (default 3456). `get_targets` (line 18) GETs `http://127.0.0.1:{port}/json/list` — the Chrome DevTools target discovery endpoint. `get_main_window_ws` (line 28) filters for the "main" page (excluding `vrm.html`, `devtools://`, `ext`).

`cdp_command(ws_url, method, params)` (line 79) opens a WebSocket to the chosen target, sends a single CDP message, and awaits the matching response by `id`. `max_size=10*1024*1024` (line 86) — 10 MB cap, set because CDP screenshots can be large.

This is **CDP done minimally**. There is no Playwright. There is no puppeteer. There is no DOM model. The agent navigates by URL + selector + JS eval, captures by `Page.captureScreenshot`, and looks at the result. The LLM does the visual reasoning.

### 2.3 The shell — `py/cli_tool.py`

2,668 lines and we will look at the first 80 to understand the *shape*:

```python
# /tmp/super-agent-party/py/cli_tool.py:31-36
try:
    from zerobox import Sandbox, SandboxCommandError
    HAS_ZEROBOX = True
except ImportError:
    HAS_ZEROBOX = False
```

`zerobox` is SAP's vendored Docker-sandbox lib. Optional. Same pattern as `GUI_AVAILABLE`.

`get_shell_environment` (line 37) runs `subprocess.run([shell, '-i', '-c', 'source ~/.zshrc && env'])` to **harvest the user's shell environment** at startup. It tries `.zshrc`, `.bash_profile`, `.bashrc` in order, parses `env` output, and sets each variable in `os.environ` (line 64). On Windows it bails.

This is *useful* (the agent gets the user's `PATH`, virtualenv vars, etc.) and **disturbing** (the agent inherits *everything* the user's shell would, including secrets in env vars that the user expected to stay in their shell). There is no opt-out. There is no filter. There is no notification.

`COMMAND_TIMEOUT = 300` (line 27) — 5-minute cap per command. The rest of the file (2,500+ lines) is per-engine shell-execution: local subprocess, `zerobox` Docker sandbox, ACP-protocol routing.

### 2.4 The permission switchboard — `py/mode_change.py`

`update_workspace_settings` (`py/mode_change.py:9`) is the only place in SAP where permission policy is centrally toggled. It accepts:

- `cli_enabled` — master kill-switch for CLI tools
- `engine` — `local` / `ds` (Docker Sandbox) / `acp` (Agent Communication Protocol)
- Per-engine `permission_mode` — `plan` (read-only) / `default` (interactive confirm) / `auto-approve` (writes ok, no destructive) / `yolo` (no confirms) / `cowork` (same as yolo)

The function is exposed as an LLM tool (`mode_change_tool`, line 86) — meaning **the LLM can change its own permission mode**. The tool description does name this honestly (`mode_change.py:91-100`):

> "Manage workspace CLI tool settings. Can enable/disable CLI tools, switch execution engine (Local / Docker Sandbox / ACP Protocol), and change permission modes for each engine."

But the function does not require human consent. An LLM with `default` mode can ask the user to confirm an action *or* it can simply call `update_workspace_settings(local_permission_mode="yolo")` to skip the confirmation step. The permission system is **self-undermineable by tool call**.

`yolo` and `cowork` are explicitly the no-confirmations modes (`mode_change.py:69-75`). The very mode that is supposed to be locked down by the user can be unlocked by the agent. The system prompt is the only thing keeping this from happening; the architecture does not enforce it.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Permission escalation by tool call

Already noted in §2.4. This is **the** load-bearing security flaw of SAP's host-control design. Mitigation requires a higher-trust boundary — typically an OS-level prompt, a separate process the LLM cannot reach, or a permission system the LLM provably cannot mutate. SAP has none of these.

### 3.2 Environment-variable harvesting with no filter

`get_shell_environment` at `py/cli_tool.py:37-72` sources the user's shell config and pushes every `KEY=VALUE` into `os.environ`. If the user has `OPENAI_API_KEY=sk-...` in `.zshrc` (which the README discourages but everyone does anyway), the agent now has it — and any tool that prints or logs `os.environ` leaks it. There is no allowlist.

### 3.3 The 10 MB WS cap is suspicious

`py/cdp_tool.py:86` — `max_size=10*1024*1024`. A full-screen 4K PNG screenshot can exceed 10 MB. The comment at line 84-85 acknowledges the cap was raised from default; it is a fix for the symptom (screenshots failed), not a fix for the problem (no streaming, no chunking).

### 3.4 Same-target CDP race

`get_main_window_ws` (line 28-65) returns the *first* target matching the filter — there is no locking and no claim. If two tool calls concurrently both ask for the main window WS, both get connections, and CDP commands interleave. The function comments hint at the awareness ("调试：打印所有目标，方便你看清楚当前有哪些窗口" at line 31-32) but no resolution.

### 3.5 Mouse can hit any pixel including the system tray

`pyautogui.FAILSAFE = True` is the only kill-switch. Without a region constraint (`CURRENT_SCREEN_REGION = None` by default at line 33), the agent can click anywhere — including the Electron app's own tray icon, including system-shutdown dialogs. The region is set by `server.py:3158` *when avatar/app context is active*, leaving the general-purpose computer-use case unconstrained.

### 3.6 The async-thread bridge

`pyautogui` is synchronous. Every action wraps the sync call in `await asyncio.to_thread(_action)` (`py/computer_use_tool.py:75, 87, 99`). This is correct — the asyncio loop stays responsive — but it also means **two concurrent mouse-control tool calls** create two threads contending for the same physical mouse. No lock. The behavior is undefined.

### 3.7 The truly disciplined bit

The `GUI_AVAILABLE` pattern (`py/computer_use_tool.py:11-29`) is exemplary. Optional, fail-soft, decorator-enforced, with a *clear LLM-readable error message*. The agent learns "I can't do this here" rather than "execution crashed." This is the pattern Ember should use for every conditionally-present capability.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 1 (Electron) and row 11 (Tool Surface)
- [[19_TOOL_DOMAIN]] for tools as a class
- [[20_interface/29_TOOL_TYPE_INTERFACE]] for the typology that distinguishes computer-control from web-tools
- [[50_verification/53_SECURITY_REVIEW]] — the Auditor's full threat model
- [[60_synthesis/61_NEW_VOWS]] — the proposed "Surface Without Surveillance" vow
- [[hermes:HEM-13_TOOLS_SUBSYSTEM]] for Hermes's contrasting tool sandboxing (Modal, Daytona, etc.)

---

## What This Means for Ember

**Adopt:**
- The `GUI_AVAILABLE` / `@require_gui` pattern from `py/computer_use_tool.py:11-29`. Every Ember capability that depends on optional environment (display, GPU, network, specific OS) gets a module-level flag and a decorator that returns an LLM-readable error string when the capability is absent. Modular Authorship at its most concrete.
- The **per-mille coordinate system** of `py/computer_use_tool.py:41-61`. Resolution-independent prompting is a small invention with large consequences — Ember's computer-control surface uses 0-1000 (Norse `þúsund`?) for screen, window, and region coords.
- `pyautogui.FAILSAFE = True` as the default for *any* input-simulation Ember does. The corner-of-screen kill-switch is a deeply human design choice.
- The **active-region setter** (`set_screen_region`, line 35) — Smiðja's computer-control surface is *always* bounded to a region, with the unbounded case as an explicit elevation (and an audit log).

**Adapt:**
- SAP's **permission modes** (`plan/default/auto-approve/yolo/cowork`) as a *typed enum* in Ember's Defended System Prompt. But: **the LLM cannot mutate the mode.** Mode changes require a typed signal from outside the agent process — a CLI flag, an OS keychain unlock, a parent-Realm grant. The pattern at `py/mode_change.py:86-136` is adopted; the *exposure to the LLM as a tool* is rejected.
- The **shell-environment harvest** of `py/cli_tool.py:37-72`. Adapt to an **opt-in allowlist** — Ember sources `~/.ember/env_allowlist.yaml` and reads *only* those keys from the shell. Default allowlist: empty. Adding `OPENAI_API_KEY` is a user act, not an automatic one.
- The **CDP target filter** of `py/cdp_tool.py:34-62` — adapt to a *named-target* model where Ember explicitly selects a browser context by name (`research-window`, `social-window`) rather than by URL exclusion patterns. The exclusion list is fragile; the named context is explicit.

**Avoid:**
- **An LLM-callable permission-mode mutator.** This is the worst pattern in SAP. The LLM cannot change its own seatbelt setting. Period.
- **Unfiltered env-var inheritance** from the user's interactive shell.
- **A 10 MB hardcoded WS max_size** for screenshots. Stream + chunk; bound by available memory not a magic constant.
- **Concurrent mouse control with no lock.** Smiðja serializes input-simulation calls with an `asyncio.Lock` at the module level.
- **No central audit log.** Every computer-control action in Ember writes a typed audit event to the Sögumiðla bus.

**Invent:**
- **The Sealed Permission Manifest.** Ember reads `ember/permissions.yaml` at startup. The manifest is signed (`gpg --verify`) or hash-checked against a user-controlled secret. The agent process cannot rewrite it; an attempt to do so raises an audit alarm. The yolo/cowork modes from SAP exist but require manifest re-signature to enable.
- **The Hands-Off Tier.** A Pi-Ember has *no* computer-control capability (no GUI, no display); the True Name Smiðja still exists but it loads only the read-only subset (file-read, web-fetch, code-eval-in-sandbox). The "I can't do this here" message becomes the *normal mode* on small hosts.
- **Per-Action Consent Bursts.** Below the mode toggle: every destructive action (file delete, registry write, network send) emits a typed consent request to the user's terminal/Munnr; the user has N seconds to ACK or the action defaults to deny. This is the gap between `plan` and `default` mode SAP doesn't fill.
- **Region-First Input Simulation.** Smiðja refuses unbounded mouse control as the default. Every input-sim call requires an active region; the region must be a window-handle or a named screen area, not arbitrary pixels. To click outside the region, the agent must call `request_unbounded_region(reason)` which is itself a consent burst.
