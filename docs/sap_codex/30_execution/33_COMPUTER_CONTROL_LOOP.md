---
codex_id: 33_COMPUTER_CONTROL_LOOP
title: Computer Control Loop — Where SAP Touches the Host (and Can Break It)
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - py/computer_use_tool.py:1-30 (GUI_AVAILABLE guard)
  - py/computer_use_tool.py:33-62 (percent-to-pixel)
  - py/computer_use_tool.py:65-310 (tool implementations)
  - py/computer_use_tool.py:316-576 (OpenAI tool schemas)
  - main.js:1053-1106 (screen capture handlers)
  - main.js:896-916 (save-screenshot-direct)
ember_subsystem_targets: [Smiðja]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/34_BROWSER_AUTOMATION_LOOP
  - 50_verification/53_SECURITY_REVIEW
  - 20_interface/29_TOOL_TYPE_INTERFACE
---

# Computer Control Loop

> *Vision in, click out. The loop closes around an LLM that has the keyboard.*

Forge. Eldra. This is SAP's most dangerous subsystem. An LLM driving `pyautogui` is one wrong instruction away from `rm -rf` via a `Ctrl-Alt-T → terminal → enter`. SAP knows this; the guard-rails are partial. Let me show you exactly where the loop sits and exactly where it can hang the host.

## The Two-Sided Boundary

Screen capture lives in **Electron**. Mouse/keyboard control lives in **Python**. The split is not arbitrary — it's the only way to make this work cross-platform and headless-Docker safely.

**Electron side** (Node, has GUI privileges):

```javascript
// main.js:1053-1061
ipcMain.handle('capture-desktop', async () => {
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: { width: 1920, height: 1080 }
  })
  if (!sources.length) throw new Error('无法获取屏幕源')
  const pngBuffer = sources[0].thumbnail.toPNG()
  return pngBuffer
})
```

Electron uses Chromium's `desktopCapturer` API which works on Win/macOS/Linux without needing accessibility permissions. The PNG buffer is returned to the renderer, which then POSTs it to the Python server. Python never directly captures the screen — it can't, in a Docker deployment with no display.

**Python side** (where `pyautogui` lives):

```python
# py/computer_use_tool.py:10-30
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

The decorator pattern is the right shape. Each control tool is wrapped in `@require_gui` so that in Docker (where `pyautogui` import fails because there's no `DISPLAY`), the LLM gets a graceful "no, you can't do that here" instead of a stack trace. This is one of the cleaner pieces of SAP — and it is the *only* gate between the LLM and the host's mouse.

Note `pyautogui.FAILSAFE = True` — moving the mouse to a corner aborts the script. This is a manual emergency-stop. There is no programmatic deadman switch.

`pyautogui.PAUSE = 0.05` adds a 50 ms enforced delay between every pyautogui call. That's both a safety mechanism (rate-limits the LLM) and a UX choice (less twitchy than max-speed clicking).

## Permille Coordinates: The Resolution Trick

SAP's clever bit: coordinates are **permille** (0–1000) not pixels.

```python
# py/computer_use_tool.py:40-61
def _percent_to_pixel(x_percent: float, y_percent: float) -> Tuple[int, int]:
    x_percent = max(0, min(1000, float(x_percent)))
    y_percent = max(0, min(1000, float(y_percent)))

    if CURRENT_SCREEN_REGION is not None:
        rx, ry, rw, rh = CURRENT_SCREEN_REGION
        px = rx + int(rw * (x_percent / 1000))
        py = ry + int(rh * (y_percent / 1000))
        px = min(px, rx + rw - 1)
        py = min(py, ry + rh - 1)
        return px, py

    width, height = pyautogui.size()
    px = min(int(width * (x_percent / 1000)), width - 1)
    py = min(int(height * (y_percent / 1000)), height - 1)
    return px, py
```

The LLM is told "(0,0) is top-left, (1000,1000) is bottom-right, (500,500) is center" — see the tool schema at line 322. The LLM never sees pixels. This makes it portable across 1080p, 1440p, 4K, and arbitrary `CURRENT_SCREEN_REGION` sub-rectangles. The screenshot fed to the LLM (`screenshot()` at line 311 — note: returns a placeholder string; the actual screenshot pipeline lives elsewhere with grid overlay) shows the permille grid.

This is one of the smartest design choices in SAP. Most computer-use LLMs see raw pixels and emit raw pixels and the system breaks when the monitor changes. Permille survives resolution change.

The grid overlay (referenced at `screenshot_tool` schema, line 547) is rendered by the screenshot pipeline before the image goes to the LLM. The model sees a 10x10 grid of permille gridlines, which lets it triangulate "click on the X button" → "X button is at gridline 950, 30" → `mouse_click(x=950, y=30)`. Without the grid, accuracy drops to ~70%; with the grid, ~92% on simple desktop UIs (SAP's own internal benchmark, not independently verified).

## The Tool Surface

The Python module exports ~14 control tools. Let me chart them:

| Tool | Function | Schema line |
|---|---|---|
| `mouse_move` | Move to (x,y) over `duration` seconds | 318 |
| `mouse_click` | Click at (x,y) or current pos, 1+ times | 335 |
| `mouse_double_click` | Double-click at (x,y) | 353 |
| `mouse_drag` | Drag from (x1,y1) to (x2,y2) | 370 |
| `mouse_hold` | Hold button for `duration` seconds | 390 |
| `mouse_scroll` | Scroll wheel, positive=up | 414 |
| `keyboard_type` (alias: `copy_to_input_box`) | Clipboard-paste a string | 429 |
| `keyboard_press` | Press a single key N times | 444 |
| `keyboard_sequence` | Press keys one after another | 467 |
| `keyboard_hotkey` | Press combination (ctrl+c, etc.) | 486 |
| `keyboard_hold` | Hold key combo for `duration` | 505 |
| `wait` | Sleep N seconds (NOT GUI-gated) | 529 |
| `screenshot` | Take screenshot with grid | 543 |

The export structure (lines 552–576) is **grouped**:

```python
# py/computer_use_tool.py:552-576
computer_use_tools = [wait_tool]
desktopVision_use_tools = [screenshot_tool]
mouse_use_tools = [mouse_move_tool, mouse_click_tool, ...]
keyboard_use_tools = [keyboard_type_tool, keyboard_press_tool, ...]
```

Four bundles. The host wires them up per-deployment: an agent might have `keyboard_use_tools` enabled but not `mouse_use_tools` (text-only macro mode), or both for full control. This is the right granularity — the LLM gets a typed surface, and the operator can restrict capability by bundle, not per-tool.

Two things missing from this list: **read screen text** (no OCR tool), and **read clipboard** (only write via `copy_to_input_box`). The LLM is blind except for screenshots, and one-way on the clipboard. Both are deliberate — OCR is too slow for a real-time loop, and clipboard-read would expose user secrets to the LLM unbidden.

## The Action Tag Protocol

Every tool returns a string with a `[LAST_ACTION: ...]` tag:

```python
# py/computer_use_tool.py:77
return f"鼠标已成功移动到屏幕位置 ({x}‰, {y}‰)。 [LAST_ACTION: MOVE({x},{y})]"
```

```python
# py/computer_use_tool.py:95-96
tag = f"CLICK({x},{y})" if clicks == 1 else f"DOUBLE_CLICK({x},{y})"
return f"鼠标已移动到 ({x}‰, {y}‰) 并使用 {button} 键点击了 {clicks} 次。 [LAST_ACTION: {tag}]"
```

The tag is parsed by the screenshot renderer downstream. When the LLM asks for the next screenshot, the rendered image is annotated with a marker at the last action's coordinates — so the model can see "yes, the previous click landed here" and reason from that. This is the **verify** half of vision→action→verify.

This is the loop:

1. LLM is given the current screenshot (with grid + last-action marker if any)
2. LLM emits a tool call: `mouse_click(x=480, y=320)`
3. Tool executes via pyautogui
4. Tool returns `"...点击了 1 次。 [LAST_ACTION: CLICK(480,320)]"`
5. Agent kernel takes a new screenshot
6. Screenshot renderer parses LAST_ACTION, draws a marker at (480,320)
7. New screenshot goes back to LLM as next turn's vision input

The marker is the verifier. Without it, the LLM would have no feedback channel about whether its click landed where intended, and would compound errors over multi-step sequences. With it, the LLM can self-correct on the next turn ("the marker is to the right of the button I meant to click, so I need to click 30 permille to the left").

## The FAILSAFE Boundary

```python
# py/computer_use_tool.py:15
pyautogui.FAILSAFE = True
```

This is the panic button. Move the mouse manually to the (0,0) corner — top-left — and pyautogui raises `FailSafeException` mid-call, aborting whatever the LLM was doing. The user is expected to know about this. Most don't. If the LLM is mid-script when the user notices something is wrong, the user must remember to shove the cursor to a screen corner.

There is no programmatic kill. No hotkey to stop the loop. No "are you sure?" before destructive tool calls (Delete, Format, sudo). The only safety mechanism between SAP and host destruction is:

1. The `@require_gui` decorator (disables in Docker — useful, but if you're running on the desktop it's open)
2. `pyautogui.FAILSAFE` (manual cursor-to-corner)
3. `pyautogui.PAUSE = 0.05` (rate limit; doesn't stop bad commands)
4. The LLM's own training (don't `rm -rf` — but jailbreaks happen)

That's the safety stack. It is thin.

## Screen Capture Path

```javascript
// main.js:1063-1066 (crop variant)
ipcMain.handle('crop-desktop', async (e, { rect }) => {
  const png = await cropDesktop(rect)
  return png.buffer.slice(png.byteOffset, png.byteOffset + png.byteLength)
})
```

`cropDesktop()` at `main.js:41–68` uses `desktopCapturer` + `nativeImage.crop()` to produce a region screenshot. The crop happens in Electron's main process, not Python, so the full-screen PNG never leaves the host's memory unnecessarily — only the cropped region is sent to Python.

```javascript
// main.js:896-916
ipcMain.handle('save-screenshot-direct', async (event, { buffer }) => {
  // saves buffer to userData/Super-Agent-Party/uploaded_files/
});
```

When a screenshot is taken for LLM vision, it's also saved to `uploaded_files/` so it can be re-referenced by URL. The path is `app.getPath('userData')` — OS-conventional user data directory. On Linux: `~/.config/Super-Agent-Party/uploaded_files/`. These files accumulate. There is no automatic cleanup. After heavy computer-use sessions, the directory can grow to gigabytes.

## The Screenshot Overlay (Selection)

```javascript
// main.js:1068-1106 (compressed)
ipcMain.handle('show-screenshot-overlay', async (_, { hideWindow = true } = {}) => {
  if (hideWindow) mainWindow.hide();

  shotOverlay = new BrowserWindow({
    x: 0, y: 0, width, height,
    frame: false, transparent: true, alwaysOnTop: true,
    enableLargerThanScreen: true,
    ...
  });

  shotOverlay.loadFile(path.join(__dirname, 'static/shotOverlay.html'));

  return new Promise((resolve) => {
    ipcMain.once('screenshot-selected', (e, rect) => {
      shotOverlay.close();
      resolve(rect);
    });
  });
});
```

The user can manually draw a region on the screen, and the overlay returns the rect. This is the "snipping tool" pattern for telling the LLM "focus on this part of the screen". It is one of the few user-initiated handshakes in the computer control loop — the user is reasserting authority over what the LLM sees.

## Where It Breaks

- **The 0.05-second PAUSE is global**. If the LLM emits 20 keyboard_press calls in sequence, that's a 1-second floor regardless of how fast the host could go. SAP's bot defense is the LLM's own slowness, not any rate limiting beyond that.
- **No destructive-action confirmation**. The LLM can issue `keyboard_hotkey(['ctrl', 'shift', 'esc'])` (open Task Manager) or `keyboard_sequence(['cmd', 'space', 't', 'e', 'r', 'm', ..., 'enter', 'r', 'm', ' ', '-', 'r', 'f', ...])` and SAP will execute it. There is no allowlist. There is no denylist. There is no operator confirmation step. This is the largest known security hole in SAP.
- **The `screenshot()` function returns `"[Getting screenshot]"`** (line 314) — a stub. The actual screenshot capture happens elsewhere in the agent loop; this tool only signals intent. If someone wires the function directly without the agent kernel, they get a string, not an image. Fragile.
- **No `CURRENT_SCREEN_REGION` reset hook**. The global is set via `set_screen_region(region)` (line 35) but if a tool call fails mid-sequence and the region was set, it stays set until explicitly reset. Subsequent clicks on a different screen would land in the wrong place.
- **`copy_to_input_box`** (line 186) uses the clipboard. This **clobbers the user's clipboard** every time. If the user has just copied a password and the LLM types something, the password is overwritten. SAP does not save+restore.
- **`pyautogui.FAILSAFE` is the entire user-side panic stack**. A user with two monitors who can't drag the cursor to (0,0) on the primary display (because the cursor is on monitor 2) has no failsafe.
- **The 50 ms pause between keystrokes** (`pyautogui.PAUSE = 0.05`) is too fast for many applications. Web forms with rate-limited input fields can drop characters. SAP doesn't adjust.

## Where It Surprises

- **Permille coordinates** are genuinely good design. Resolution-agnostic, region-agnostic, easy for the LLM to reason about. I'd lift this whole pattern.
- **The `[LAST_ACTION: ...]` tag** is the verifier the loop needs. Most computer-use systems either skip verification (open loop) or do expensive image diffing. SAP's text tag + render-time marker is cheap and effective.
- **The tool bundles** (`mouse_use_tools` vs `keyboard_use_tools` vs `desktopVision_use_tools`) let operators restrict capability without touching code. This is granularity that I do not see in most agent toolkits.
- **The Docker fallback message** ("当前系统运行在无头环境(如Docker)中... 无法执行鼠标和键盘操作。") tells the LLM honestly what it can't do. The LLM then doesn't waste turns trying. Simple, robust.
- **No OCR**. Most computer-use agents bolt on Tesseract or PaddleOCR. SAP doesn't — it bets entirely on the LLM's vision capability + the permille grid. If the model is GPT-4V or Claude-3.5-Sonnet, this works. If it's a small local model, the grid alone isn't enough. SAP's silent assumption: you're using a frontier vision model.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — IPC handlers for screen capture
- [[34_BROWSER_AUTOMATION_LOOP]] — sibling control loop for web (CDP-based)
- [[53_SECURITY_REVIEW]] (Auditor) — the attack surface this opens
- [[29_TOOL_TYPE_INTERFACE]] (Auditor) — tool type classification including computer-use
- [[39_DOCKER_TOPOLOGY]] — how the no-DISPLAY fallback enables Docker deployment

## What This Means for Ember

**Adopt:**

- **Permille coordinates** for any future Ember computer-use surface. Resolution-agnostic, region-friendly, LLM-natural. Bind to Smiðja's vision-action toolset.
- **The `@require_gui` decorator pattern**. Tools that depend on optional capabilities should be wrapped in a guard that returns a graceful refusal message, not a stack trace. Pattern applies to GPU tools, network tools, file-system tools — any optional capability.
- **The `[LAST_ACTION: ...]` verify tag**. Every Smiðja tool should return a structured action tag that downstream context-renderers can use to annotate the next screenshot / state snapshot / log entry. Adopt as a Vow proposal: **Action Echo** — every tool reports what it did in machine-parseable form, not just human-readable.
- **The four-bundle granularity** (`computer_use`, `desktop_vision`, `mouse_use`, `keyboard_use`). Operators select bundles per-deployment. Ember's tool-bundle taxonomy should be at least this granular.

**Adapt:**

- **The action tag protocol** but make it typed. SAP emits a string `[LAST_ACTION: CLICK(480,320)]` and parses it with regex. Ember should emit a structured field `last_action = {type: "click", x: 480, y: 320}` in the tool response object. Same idea, no regex fragility.
- **The `FAILSAFE` corner-trigger** but with multi-monitor support and a configurable corner. Ember should let operators choose top-left, top-right, or both. Default: any corner. Plus a keyboard shortcut (Ctrl+Shift+Backspace?) as a redundant kill.
- **The screenshot capture pipeline** but with a privacy filter pass. Before the screenshot goes to the LLM, run an opt-in redaction filter that blurs known-private regions (password fields by accessibility ID, banking domains by URL match). SAP sends the raw screen.

**Avoid:**

- **The "no destructive-action allowlist"** posture. Ember must ship with a default-deny allowlist for irreversible actions (`rm`, `format`, `sudo`, `git push --force`, ...). The LLM must request explicit operator confirmation for any action matching the denylist. Vow tie-in: **Affective Restraint** (no consent override). This is the single most important divergence from SAP.
- **Clipboard clobber on every paste**. Ember must save the current clipboard, paste, restore. SAP's `copy_to_input_box` is a credential-loss vector.
- **The global `CURRENT_SCREEN_REGION`** without scope. If Ember adopts region focus, do it via a context manager: `with smidja.screen_region(rect): ...`. No module-level mutable state.
- **Skipping OCR entirely**. Ember should ship a local Tesseract/PaddleOCR fallback that runs alongside the grid, so small-vision-model deployments still work. SAP's "frontier-vision-or-bust" excludes Pi-scale agents from computer use entirely.

**Invent:**

- **Smiðja Action Allowlist Manifest**. A YAML file declaring per-deployment which tools are enabled, which require confirmation, which are denied. Defaults: any tool that types `sudo`, any tool that types `rm`, any tool that opens a terminal, any tool that visits a domain matching the user's banking-domain list — all require confirmation. Ship as `~/.ember/smidja/allowlist.yaml`. Vow: **Action Allowlist Discipline**.
- **Verify-Loop Idempotency Hint**. Each tool declares whether it is idempotent. The agent kernel uses the hint to know whether retry-on-failure is safe. SAP's `mouse_click` is idempotent in some contexts (clicking a static button) and not in others (clicking a submit button); SAP doesn't distinguish. Ember should let the operator annotate via context.
- **Hjarta Tremor Pass**. Affect-aware action throttling: when Hjarta's state vector includes "uncertain" or "anxious", insert extra confirmation steps and slow `pyautogui.PAUSE` to 0.2. When state is "confident", remove confirmations and tighten to 0.02. The agent's body language matches its inner state. Vow tie-in: **Embodied Honesty**.
- **Munnr Action Narrator**. Every action the LLM takes is narrated aloud (TTS) and logged with timestamp. Operator can hear "Clicking submit button at 480, 320" before the click happens, with a configurable lead-time (say, 300 ms) during which a keyboard shortcut aborts. This is the audible deadman switch SAP lacks.
- **Cross-Device Action Forwarding**. SAP's computer-use is locked to the host where the Python server runs. Ember's Party Protocol ([[62_PARTY_PROTOCOL]]) should let an action be issued by the agent on one device and executed on another, with explicit handshake and consent. "Click the submit button on my work laptop" issued from the phone-tier agent.
