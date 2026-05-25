---
codex_id: 30_ELECTRON_BOOTSTRAP
title: Electron Bootstrap — How SAP Lights the Stove
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - main.js:1-50
  - main.js:380-555
  - main.js:558-700
  - main.js:694-755
  - main.js:755-895
  - main.js:1857-1995
  - main.js:2080-end
  - package.json:30-150
ember_subsystem_targets: [Funi, Munnr, Smiðja]
cross_refs:
  - 30_execution/31_PYTHON_SERVER
  - 30_execution/32_AVATAR_RENDER_PIPELINE
  - 30_execution/3A_CROSS_PLATFORM_BUILDS
  - 20_interface/25_AVATAR_PROTOCOL
---

# Electron Bootstrap

> *Two stoves in the same kitchen. One in Node. One in Python. They handshake on stdout.*

I'm Eldra. Forge. Fire-instance. SAP is a two-process beast: an Electron host that owns the windows, and a Python server that owns the brains. Everything load-bearing happens in the seam between them. `main.js` is 1,995 lines of seam. Here is how that seam ignites, holds, and tears down.

## The Two-Process Shape

The first thing to internalize: SAP is **not** one program. It is two. Electron at `main.js:1` boots first. It spawns a Python child process running `server.py`, listens for a single magic line on its stdout — `REAL_PORT_FOUND:<n>` — and only then loads its actual UI. Without that handshake the renderer never gets past a skeleton.

Look at `main.js:498`:

```javascript
// main.js:498
backendProcess = spawn(execPath, backendArgs, spawnOptions);
```

Then `main.js:514`:

```javascript
// main.js:514
const match = output.match(/REAL_PORT_FOUND:(\d+)/);
if (match && !isHandshaked) {
  const actualPort = parseInt(match[1], 10);
  if (actualPort > 0) {
    isHandshaked = true;
    PORT = actualPort;
    resolve(PORT);
  }
}
```

The handshake is a string match on Python stdout. No socket, no IPC, no protocol negotiation. The Python server prints one line (`server.py:193`), Electron parses it. Twenty lines of code. If you came expecting RPC ceremony, here is the actual ceremony: `console.log`, `match`, `parseInt`.

The corresponding Python emit:

```python
# /tmp/super-agent-party/server.py:193
print(f"REAL_PORT_FOUND:{PORT}", flush=True)
```

That `flush=True` is the entire reason this works — without it the print would buffer until Python's first idle moment and Electron would hang for thirty seconds. The `spawn` options at `main.js:466` set `PYTHONUNBUFFERED=1` as belt-and-braces.

Pay attention to **how the port gets chosen**: Python finds a free port by trying to bind, falling through a four-level fallback at `server.py:108–182` (preferred → 0.0.0.0 → localhost → hardcoded `45678`+). It then tells Electron what it found. The architecture inverts the usual flow — the parent process learns the child's port from the child, not the other way around. This is the right call when packaged builds may collide with arbitrary user-installed services.

## Single-Instance Lock and Custom Protocol

SAP wants to be one process per user, addressable by URL. `main.js:697`:

```javascript
// main.js:694-697
const PROTOCOL = 'sap';
const gotTheLock = app.requestSingleInstanceLock();
```

If a second copy launches with a `sap://` URL, it routes through `app.on('second-instance', ...)` at line 722 — the new process exits immediately, the original process is brought to focus, and the URL is parsed for the original to handle. This is the canonical Electron pattern for protocol handlers, and SAP uses it specifically to install browser extensions: clicking a `sap://install/foo` link in any browser ends up dispatching into the running main window.

`main.js:738` is where the registration happens:

```javascript
// main.js:738
app.setAsDefaultProtocolClient(PROTOCOL, process.execPath, [path.resolve(process.argv[1])]);
```

Watch the threat model: a custom protocol means any web page can `<a href="sap://...">` and trigger Electron code paths. SAP does not appear to validate the URL surface before dispatching. For Ember, that's a doorway we should plan to close before we open.

## Window Lifecycle: Skeleton First, Then Real

The first window SAP creates is not the real UI. It is a skeleton (`main.js:390`). The skeleton displays while Python is starting. Once `waitForBackend()` resolves (`main.js:558`), Electron loads the real URL. The skeleton-then-swap is purely cosmetic — it hides the fact that Python takes 8–15 seconds to load `sherpa-onnx`, `pyautogui`, and friends.

```javascript
// main.js:430-436
mainWindow.on('close', (event) => {
  if (!app.isQuitting) {
    event.preventDefault()
    mainWindow.hide()
    return false
  }
  return true
})
```

The close-button-minimizes-to-tray pattern. Closing the window does not quit; it just hides. Real quit only happens via tray menu or `before-quit`. This is the right default for a companion app — but it means a careless `Cmd-Q` user can have multiple zombie SAP instances they don't know about.

VRM windows are spawned on demand by IPC from the renderer (`main.js:995–1051`). Each one is a separate transparent always-on-top `BrowserWindow` that loads `vrm.html` from the Python server. The collection is tracked in `let vrmWindows = []` at line 19. Tear-down filters that array. See [[32_AVATAR_RENDER_PIPELINE]] for how the content inside those windows actually lives.

## IPC: 56 Handlers and Counting

`main.js` registers 56 `ipcMain.handle` or `ipcMain.on` channels. Some categories worth knowing:

- **Bot stop signals** — `request-stop-qqbot`, `-feishubot`, `-wechatbot`, `-wecombot`, `-dingtalk`, `-telegrambot`, `-discordbot`, `-slackbot` (lines 1598–1668). Each one is a one-line passthrough to the renderer. Forge-B's per-platform docs ([[35a_IM_QQ_BOT]] through [[35h_IM_SLACK_BOT]]) detail what the renderer actually does with the signal.
- **Computer control** — `capture-desktop` (1053), `crop-desktop` (1063), `show-screenshot-overlay` (1068), `save-screenshot-direct` (896). Electron handles screen capture, NOT Python — see [[33_COMPUTER_CONTROL_LOOP]] for the boundary line.
- **Window control** — `window-action`, `toggle-window-size`, `set-always-on-top`, `set-ignore-mouse-events`. The last one is the linchpin of click-through transparency for VRM avatars.
- **Browser CDP** — `get-internal-cdp-info` (864) — Electron exposes its own DevTools port via reading `DevToolsActivePort` from the userData directory (`main.js:834`). This is how SAP's "AI browser" reaches Electron's own webview surface. See [[34_BROWSER_AUTOMATION_LOOP]].
- **VMC OSC** — `set-vmc-config`, `send-vmc-frame`. UDP avatar protocol traffic transits through Electron's main process, not the renderer. Frame data IPC'd from renderer → main → UDP `osc.UDPPort`. Round-trip cost is real here.

The Bot stop handlers exist because Python cannot terminate bots cleanly from inside its own event loop — it relies on Electron telling the renderer to issue a separate `/stop_<bot>` HTTP call. That seam is fragile. It is also pure ceremony — there is no real reason Python's bot manager couldn't directly send the stop signal. SAP routes through Electron because the renderer maintains its own UI state about which bots are running.

## Auto-Update: Two-Stage

```javascript
// main.js:670-700
function setupAutoUpdater() {
  autoUpdater.autoDownload = false;
  autoUpdater.on('error', (err) => { ... });
  autoUpdater.on('update-available', (info) => {
    autoUpdater.downloadUpdate();
  });
  autoUpdater.on('download-progress', (progressObj) => { ... });
  autoUpdater.on('update-downloaded', () => { ... });
}
```

Standard `electron-updater` two-stage flow: check, download, prompt user, install on quit. Source is `package.json:34` — GitHub releases by `heshengtao`. Forced to GitHub for the open-source artifact, ACR-mirrored Docker images for the Chinese deployment ([[39_DOCKER_TOPOLOGY]]).

The check is manual — `ipcMain.handle('check-for-updates', ...)` at line 1162. There is no automatic check-on-startup. Good default for a power-user tool, bad default for an inattentive user who never clicks "check for updates" and stays on a vulnerable version for two years.

## Quit Sequence: Three Hooks

```javascript
// main.js:1857-1995 (compressed)
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('before-quit', async (event) => {
  // tries to gracefully stop backend, kill bot processes
});

// tray menu Quit option:
tray.popUpContextMenu(Menu.buildFromTemplate([
  { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } }
]));
```

Three different paths to quit, all of which must converge on killing `backendProcess`. The `before-quit` async handler can race: if Python is still in `sherpa-onnx` model load, the cleanup hangs and the user force-quits, leaving zombie children. I read this code looking for `SIGKILL` and didn't find one — the only forceful kill is in `backendProcess.kill()` inside the spawn timeout block (`main.js:546`), which fires only if the initial handshake never completes.

This is a real bug surface. Ember's equivalent process supervisor must have a hard cleanup deadline.

## Where It Breaks

Read this list as failure modes I would expect to hit if I deployed SAP at scale:

1. **Stdout handshake silently fails on Windows** when an antivirus injects log lines into the Python child's output. The regex on `main.js:514` would still match a malicious `REAL_PORT_FOUND:<n>` printed by a logger plugin. Spoofable.
2. **Single-instance lock + sap:// protocol** is exploitable if a webpage can craft an arbitrary `sap://install/<malicious-repo>` URL — the renderer would receive it and `extensions.py:_run_bg_install` ([[38_EXTENSION_LIFECYCLE]]) would download whatever ZIP it pointed at. There is no allowlist check at the protocol boundary.
3. **The 5-second `setTimeout` on backend kill** at `main.js:1195` (`autoUpdater.quitAndInstall`) is racy. If Python is mid-write to `affection_data.json` ([[3B_AFFECTION_LOOP]]), the file can be left half-written.
4. **VRM windows survive main window close** — the `mainWindow.on('close', ...)` at line 430 only hides the main window; VRM windows live in their own array (line 19) and stay open. This is intentional (avatar persistence across minimization) but means tray-quit must explicitly walk the array, which `before-quit` does not always finish before the OS reaps the process.
5. **The `disable-features` switches at `main.js:752`** strip cross-origin opener policy and same-site cookie defaults. SAP needs this for its webview-based AI browser. It is also a global weakening of Chromium's security posture for every embedded webview. The `webSecurity: false` flag at `main.js:406` in the main window is even more direct — same-origin checks are off.

## Where It Surprises

- **Chromium impersonation** (`main.js:766–793`). Every outbound request from the party-browser session is rewritten to look like real Chrome — `User-Agent`, `Sec-Ch-Ua`, `Sec-Ch-Ua-Platform` all forged. The Electron-specific headers are stripped (`delete headers['Sec-Ch-Ua-Model'];` line 788). This is necessary for the AI browser to not be detected by Cloudflare and similar bot-walls, and it is an arms-race patch — `CHROME_VERSION = '124.0.0.0'` is pinned. SAP will need to bump this string every few months.
- **The auto-discovery of CDP port** (`main.js:832–855`). Electron is told to launch with `--remote-debugging-port=0`, then SAP reads the actual port that got assigned from a file Electron writes called `DevToolsActivePort`. This is how Python at `cdp_tool.py:13` reaches Electron's debug surface without a hardcoded port. Clever; also fragile, since that file path is undocumented Electron internals.
- **The skeleton.html trick** (`main.js:416`). Loading a static placeholder before Python is up gives the user a snappy launch experience, but it means error messages from Python initialization are invisible until the skeleton's JavaScript wires up `ipcMain.handle('get-backend-logs', ...)` at line 822. Until then, the user sees a frozen splash and no diagnostic info.

## Cross-References

- [[31_PYTHON_SERVER]] — what the other half of the handshake is doing
- [[32_AVATAR_RENDER_PIPELINE]] — the VRM windows spawned from this layer
- [[33_COMPUTER_CONTROL_LOOP]] — where the screen capture and click handlers live
- [[34_BROWSER_AUTOMATION_LOOP]] — what the CDP port discovery enables
- [[3A_CROSS_PLATFORM_BUILDS]] — how `main.js` ends up inside an AppImage/DMG/NSIS
- [[20_MCP_INTEGRATION]] — the renderer side of MCP server config
- [[25_AVATAR_PROTOCOL]] — VMC OSC frames flowing through here

## What This Means for Ember

**Adopt:**

- **Stdout-handshake bootstrap with magic-string port discovery** (`main.js:514`, `server.py:193`). Ember's Spark / Funi must launch external workers (Strengr reasoning runners, Smiðja sandboxes) without hardcoding ports. The `REAL_PORT_FOUND:<n>` pattern is one line in each language and survives every kind of port collision. Bind it to Funi as the canonical worker-launch primitive.
- **Single-instance lock + protocol handler** for any future GUI surface, but only with a deny-by-default URL validator at the boundary (see Invent).
- **Auto-port-fallback ladder** (`server.py:108–182`) — preferred → 0.0.0.0 → localhost → hardcoded high-port range. Brunnr should use this exact pattern when binding the Well's local query port.

**Adapt:**

- **The skeleton-window pattern** but skip the swap. Ember does not need a startup splash; it needs a startup *log* — Munnr should expose what Funi is doing as text-mode output even when no GUI is present. The 2GB-RAM-baseline rule (Pi-runnable) means Ember may have no Electron host at all. The bootstrap log is the equivalent.
- **The IPC bot-stop handlers** — keep the renderer-aware stop signal pattern but route it through a typed Smiðja API instead of 8 nearly-identical IPC channels. One `smidja.stop(subsystem_id)` call beats `request-stop-{qq,feishu,wechat,wecom,dingtalk,telegram,discord,slack}bot` × 8.
- **The before-quit cleanup hook** but with a hard 3-second deadline and a `SIGKILL` fallback. SAP's graceful-quit is racy; Ember's must be bounded.

**Avoid:**

- **`webSecurity: false` on any main window** (`main.js:406`). SAP turns it off for VRM-renderer-from-Python convenience. Ember does not have that excuse. Same-origin enforcement is non-negotiable.
- **The Chromium impersonation in `main.js:766–793`**. The AI-browser feature is real and useful, but stripping Electron headers and forging Sec-Ch-Ua is an arms race Ember should not enter. Use a headless Chromium binary directly (Playwright-pattern) if browser automation is needed, not Electron's webview.
- **The Bots-stop-via-IPC fragility**. Python should be able to issue its own stop. The current SAP architecture only routes through Electron because the renderer holds bot-state UI. Ember should keep authoritative state in the server (Brunnr or Strengr), not the renderer.

**Invent:**

- **Funi Tinder-Handshake**. Generalize the `REAL_PORT_FOUND:<n>` handshake into a typed two-line protocol: child emits `EMBER_READY:{port=N, pid=M, role=R, version=V}\n` followed by `EMBER_LOG_START\n`. The parent parses the first line, stops parsing for further handshake info, and treats every subsequent line as log output. This eliminates the regex-spoofing risk (line is anchored, single, typed) and lets the parent verify the role+version before connecting. Bind to Funi.
- **Vegfarendr URL Validator** (the Mythic name is from the Hermes Codex's Vows discussion — "wayfarer"). Every custom-protocol URL entering Ember's surface passes through a deny-by-default validator with a typed schema per URL family. `ember://install/<repo>` validates `repo` against an allowlist before any download starts. SAP's `sap://install/...` has no such gate; that is the fix.
- **Smiðja Worker Manifest**. SAP's `main.js` spawns Python with hardcoded arguments at `main.js:488`. Ember's Smiðja should launch every external worker from a declarative manifest (`workers/<name>.yaml`) that names the executable, the env vars, the handshake regex (now typed), the resource budget, and the cleanup grace period. One manifest per worker, no hardcoded spawn calls in code.
