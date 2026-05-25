---
codex_id: 3A_CROSS_PLATFORM_BUILDS
title: Cross-Platform Builds — Electron Builder + PyInstaller in a Three-Legged Race
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - package.json:30-150 (electron-builder config)
  - server.spec:1-124 (PyInstaller spec)
  - start.js (Electron entry script)
  - main.js:441-498 (resourcesPath logic)
  - py/node_runner.py:23-32 (Electron-as-Node)
ember_subsystem_targets: [Funi]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/31_PYTHON_SERVER
  - 30_execution/39_DOCKER_TOPOLOGY
  - 30_execution/38_EXTENSION_LIFECYCLE
---

# Cross-Platform Builds

> *Two build systems chained. PyInstaller produces a `server` executable. Electron-builder takes that executable as `extraResources`. Both have to run on the target platform. There is no clean cross-compilation story.*

Forge. Eldra. SAP ships to Windows (NSIS installer), macOS (DMG, arm64-only), Linux (AppImage), and Docker (`Dockerfile`). Native builds are produced by **chaining PyInstaller + electron-builder**. This is the most fragile part of SAP's release pipeline, and reading it tells you which platforms are first-class and which are afterthoughts.

## The Two-Stage Build

```
Stage 1: PyInstaller (per-platform)
  server.py + py/* + skills/ + vrm/ + config/ + static/
  → dist/server/server[.exe]  (single-folder bundle, ~250 MB)

Stage 2: electron-builder (per-platform)
  main.js + static/ + dist/server/ (as extraResources)
  + node_modules/npm/ + node_modules/acpx/
  → AppImage / NSIS / DMG
```

Two separate toolchains. PyInstaller bundles the Python runtime + all imports + data files into a self-contained executable directory. Electron-builder bundles the Electron runtime + the renderer assets + the PyInstaller output (as a resource) into a platform-native installer.

This means: **you cannot build SAP on Linux for Windows.** PyInstaller does not cross-compile. You need a Windows host to produce the Windows build, a macOS host (arm64) to produce the Mac build, and a Linux host to produce the Linux build. SAP's release process is presumably three machines (or GitHub Actions matrix) running in parallel.

## The PyInstaller Spec

```python
# server.spec:37-58 (Analysis block)
a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=ffmpeg_bin,
    datas=[
        ('config/settings_template.json', 'config'),
        ('config/locales.json', 'config'),
        ('static', 'static'),
        ('vrm', 'vrm'),
        ('tiktoken_cache', 'tiktoken_cache'),
        ('skills', 'skills'),
        *ffmpeg_data,
        *my_extra_datas,
    ],
    hiddenimports=my_hidden_imports,
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False, optimize=0,
)
```

The bundle pulls in:
- Source: `server.py` + everything it imports (every file in `py/`)
- **Binaries**: `ffmpeg` (for audio processing — `imageio-ffmpeg.get_ffmpeg_exe()` returns the bundled binary path at line 6)
- **Data**: `config/` (templates + locales), `static/` (the frontend SPA), `vrm/` (default VRM models), `tiktoken_cache/` (the BPE tokenizer files — needs to ship because token-counting is offline), `skills/` (default agent skills)

**`my_hidden_imports`** (line 19-26):

```python
my_hidden_imports = [
    'pydantic.deprecated.decorator',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'botpy',
    'imageio_ffmpeg',
    *collect_submodules('mem0'),
]
```

These are imports PyInstaller's static analyzer cannot detect on its own. `pydantic.deprecated.decorator` is dynamically imported by Pydantic v2. `tiktoken_ext.openai_public` is the BPE registration. `botpy` (Tencent QQ SDK) does dynamic plugin loading. `mem0` (memory framework) has dozens of dynamically-loaded submodules — `collect_submodules('mem0')` walks them all and includes everything.

Every one of those hidden_imports represents a debugging session. PyInstaller silently omits modules its static analyzer can't see; you discover the omission when the user clicks something and you get `ImportError: No module named 'foo'` in production. Each entry in `my_hidden_imports` is a tombstone.

```python
# server.spec:30-34
if platform.system() != 'Windows':
    my_hidden_imports.extend(collect_submodules('zerobox'))
    my_extra_datas.extend(collect_data_files('zerobox'))
```

`zerobox` is a Linux/macOS-only pure-Python lib. SAP gates the import per-platform. This pattern repeats throughout — every platform-specific lib needs a `platform.system()` branch.

### Per-Platform Build Branches

```python
# server.spec:72-124 (compressed)
if platform.system() == 'Darwin':
    exe = EXE(pyz, a.scripts, [], name='server', icon='static/source/icon.png', **base_exe_config)
    coll = COLLECT(exe, a.binaries, a.datas, name='server', upx_exclude=[], **universal_disable_sign)
elif platform.system() == 'Windows':
    exe = EXE(pyz, a.scripts, [], name='server', icon='static/source/icon.ico', **base_exe_config)
    coll = COLLECT(...)
else:
    exe = EXE(pyz, a.scripts, [], name='server', **base_exe_config)  # Linux: no icon
    coll = COLLECT(...)
```

Three branches. Cosmetic differences (.ico vs .png icon, none for Linux). The `base_exe_config` is shared:

```python
# server.spec:62-70
base_exe_config = {
    'debug': False,
    'strip': False,
    'upx': True,
    'bootloader_ignore_signals': False,
    'disable_windowed_traceback': False,
    **universal_disable_sign
}
```

`upx: True` is the UPX compression switch. UPX shrinks the executable by 30-50% but **adds ~200ms to cold start** as the executable decompresses itself into memory. SAP accepts the trade-off because distribution size matters more than startup time (the user waits another 200 ms once; they download every gigabyte of patch forever).

`universal_disable_sign` (line 12-17):

```python
universal_disable_sign = {
    'codesign_identity': None,
    'entitlements_file': None,
    'signing_requirements': '',
    'exclude_binaries': True
}
```

**SAP doesn't sign its binaries.** No Apple Developer ID. No Windows EV cert. Users on macOS will see "Apple cannot verify this developer" warnings; users on Windows will see SmartScreen warnings. The unsigned ship is a deliberate choice (developer cost) but it shifts trust friction to the user.

## The Electron-Builder Config

```json
// package.json:30-79 (compressed)
"build": {
  "appId": "com.superagent.party",
  "productName": "Super-Agent-Party",
  "publish": {
    "provider": "github",
    "owner": "heshengtao",
    "repo": "super-agent-party",
    "releaseType": "draft"
  },
  "compression": "maximum",
  "directories": {
    "output": "release"
  },
  "files": [
    "main.js", "LICENSE", "README.md",
    "dist/", "static/source/", "static/js/preload.js",
    "static/skeleton.html", "static/js/shotPreload.js",
    "static/js/webview-preload.js", "static/shotOverlay.html",
    "static/source/icon_tray.png"
  ],
  "extraResources": [
    { "from": "dist/server/", "to": "server", "filter": ["**/*"] },
    { "from": "node_modules/npm/", "to": "npm", "filter": ["**/*"] },
    { "from": "node_modules/acpx/", "to": "acpx", "filter": ["**/*"] }
  ]
}
```

Three pieces:

1. **`files`**: what goes inside the asar archive. The Electron app's own JS + assets.
2. **`extraResources`**: what gets copied alongside the asar at `process.resourcesPath`. This is where the PyInstaller `server/` directory ends up — referenced from `main.js:492`.
3. **`publish`**: GitHub draft release. The CI builds it, electron-updater can detect it later. Draft means a maintainer manually publishes after smoke-testing.

**Bundled npm + acpx**: SAP ships its own `npm` (for the Node extension installer in `node_runner.py`) and its own `acpx` (the companion CLI). System Node is not assumed. This is what makes the desktop SAP work even on Windows machines without Node installed. The cost: ~150 MB of npm+acpx in the install.

### Platform Targets

```json
// package.json:80-149 (compressed)
"linux": {
  "icon": "static/source/icon.png",
  "target": ["AppImage"],
  "artifactName": "${productName}-${version}-Linux-${arch}.${ext}"
},
"mac": {
  "icon": "static/source/icon.icns",
  "target": [{"target": "dmg", "arch": ["arm64"]}],
  "artifactName": "${productName}-${version}-Mac.${ext}",
  "category": "public.app-category.utilities",
  "identity": "-",   // no signing
  "hardenedRuntime": false,
  "gatekeeperAssess": false,
  "entitlements": "entitlements.mac.plist",
  ...
},
"win": {
  "icon": "static/source/icon.png",
  "verifyUpdateCodeSignature": false,
  "target": ["nsis"],
  ...
},
"nsis": {
  "oneClick": false,
  "allowElevation": true,
  "allowToChangeInstallationDirectory": true,
  "createDesktopShortcut": true,
  "differentialPackage": true,
  "perMachine": false
}
```

**Linux**: AppImage only. No `.deb`, no `.rpm`, no Snap, no Flatpak. AppImage is the lowest-friction (just a binary the user `chmod +x`-es) but doesn't integrate with system package managers.

**macOS**: DMG only, **arm64 only**. Intel Macs are not supported. A real choice — Apple Silicon-only narrows the user base but eliminates the rosetta-vs-native mess.

**Windows**: NSIS installer. `oneClick: false` means it walks the user through install location. `differentialPackage: true` enables electron-updater's binary-diff updates (only changed chunks downloaded, not the full installer). Good detail.

**Notably absent**: portable ZIP for Windows. Some users want "unpack and run" without installer. SAP doesn't ship that. Also absent: AppImage for ARM Linux (Pi). The Pi-runnable Vow for Ember is going to require us to build this ourselves.

### The Aplit Build Matrix

The combined matrix:

| Platform | PyInstaller | Electron-Builder | Output |
|---|---|---|---|
| Win10/11 x64 | server.exe + folder | NSIS installer | `.exe` |
| macOS arm64 | server + folder | DMG | `.dmg` |
| Linux x64 | server + folder | AppImage | `.AppImage` |
| Linux arm64 | not built | not built | N/A |
| Linux x86 | not built | not built | N/A |
| Docker | bypassed (uses `pip install uv` + `uv sync`) | bypassed | `:latest` image |

Three desktop builds + one Docker image. Five host machines or GHA runners needed for a full release. The README says SAP also supports Server 2025 (Windows Server) — the build path is identical to Win10/11.

## The resourcesPath Reading in main.js

```javascript
// main.js:441-446
function getAcpxPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'acpx');
  } else {
    return path.join(__dirname, 'node_modules', 'acpx');
  }
}
```

Two-mode pathing. `app.isPackaged` is true in shipped builds, false in `npm run dev`. The same code-path works for both. Same pattern for `server` executable at `main.js:489-494`:

```javascript
// main.js:489-494
if (isDev) {
  execPath = pythonExec;
  backendArgs = ['-u', 'server.py', '--host', BACKEND_HOST, '--port', '3456'];
} else {
  const serverExecutable = process.platform === 'win32' ? 'server.exe' : 'server';
  const resourcesPath = process.resourcesPath || path.join(process.execPath, '..', 'resources');
  execPath = path.join(resourcesPath, 'server', serverExecutable);
  backendArgs = ['--host', BACKEND_HOST, '--port', '3456'];
  spawnOptions.cwd = path.dirname(execPath);
}
```

Dev mode: `python server.py`. Packaged mode: `<resourcesPath>/server/server[.exe]`. The PyInstaller output is exactly one binary plus its data folder; main.js launches the binary, the binary self-loads its data.

## Where It Breaks

- **PyInstaller hidden_imports list is incomplete by construction**. Every new dynamically-imported module is a runtime ImportError waiting. The only test is "build it and run the full feature matrix". This is a perpetual maintenance tax.
- **Unsigned binaries**. Mac users see Gatekeeper warnings. Windows users see SmartScreen warnings. Users routinely click through these, training them to ignore real warnings later.
- **No Intel Mac build**. Users on 2017-2019 Macs can't run SAP. The decision is defensible (Apple Silicon is Apple's strategic direction; Intel Macs are end-of-life by 2025) but it's a today-cost.
- **No ARM Linux**. Pi 4/5 users cannot run SAP. This is the single biggest gap for Ember's Pi-runnable Vow.
- **UPX compression breaks some antivirus heuristics**. Compressed executables that self-decompress at startup match malware signatures. Some Windows AV products flag SAP's `server.exe` as suspicious.
- **`differentialPackage: true`** requires consistent file layout across versions. A reordered `extraResources` or renamed PyInstaller file invalidates the diff and forces full-package downloads.
- **The PyInstaller `--production` flag is missing** (server.spec doesn't strip debug symbols). The binary is larger than it needs to be and includes assertion code.
- **`bootloader_ignore_signals: False`** means a Ctrl-C in dev mode propagates correctly, but means a `SIGTERM` from the OS during shutdown can leave PyInstaller cleanup half-done. Rare race.
- **`tiktoken_cache` is shipped as data**. This means the BPE files are baked into the binary at build time. If OpenAI updates its tokenizer (rare but happens), SAP's offline token-counting drifts from reality until the next release.

## Where It Surprises

- **PyInstaller + electron-builder chaining works at all**. This is operationally heavy but defensible — the alternative (rewrite Python parts in Rust/Node) is years of work.
- **`collect_submodules('mem0')`** is the right hammer for libraries that confuse static analyzers. SAP uses it instead of listing each `mem0.x.y.z` submodule. Small detail; saves maintenance.
- **The bundled `npm` and `acpx`** make SAP truly self-contained. No "install Node first" friction.
- **`identity: '-'`** on macOS is the "ad-hoc sign" magic value. It avoids the worst of the unsigned-binary friction (Gatekeeper still warns but the binary at least has stable signing metadata for codesign-aware OSes).
- **`compression: maximum`** on the electron-builder side means longer build times but smaller install footprint. SAP installs end up around ~600 MB after compression; without it they'd be 1+ GB.
- **`releaseType: "draft"`** means CI never auto-publishes. A maintainer has to click "Publish release" on GitHub. Good for catching mid-release regressions.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — how the packaged binary is launched
- [[31_PYTHON_SERVER]] — what the PyInstaller binary actually runs
- [[39_DOCKER_TOPOLOGY]] — the build path Docker bypasses
- [[38_EXTENSION_LIFECYCLE]] — bundled `npm` powers this

## What This Means for Ember

**Adopt:**

- **The `process.resourcesPath`-or-dev-path pattern** in main.js. One code-path serves both shipped and dev modes. Bind to Funi's launcher.
- **`differentialPackage: true`** for the installer. Users pay only for what changed. Bandwidth respect.
- **`releaseType: "draft"`** — never auto-publish releases. Manual review gate. Vow tie-in: **Public-Friendliness** (a bad release would hurt non-expert users more than they'd notice).
- **`hidden_imports` aggregation via `collect_submodules()`** for libraries with dynamic loading.

**Adapt:**

- **The unsigned-binaries posture** — adapt by signing. The cost is real ($99/year Apple, ~$300/year Windows EV cert) but the user-friction cost is higher. Vow proposal: **Trust Boundary** — Ember's shipped binaries are signed; warnings on user machines are real warnings, not noise.
- **Three desktop targets** — adapt to also include ARM Linux (Pi 4/5). The PyInstaller build must run on an ARM host (cross-compile is not supported); GHA has ARM runners as of 2024-2025. Vow tie-in: **Smallness** — Pi-runnable is non-negotiable.
- **`compression: maximum`** — adapt to default, but expose a `--fast-build` flag for development that uses `compression: store`. The 60-second compression step during every dev build is wasteful.
- **UPX compression** — adapt to opt-in via build flag. Default off because of AV false-positive risk; enable for size-constrained releases.

**Avoid:**

- **No portable ZIP for Windows**. Many power-users want this. Ember should ship a portable ZIP alongside the installer.
- **Mac arm64-only**. If Ember ships native Mac builds, ship both x64 and arm64 (universal binary if feasible, separate DMGs if not).
- **No package-manager integration for Linux**. Beyond AppImage, ship `.deb` (Debian/Ubuntu) and `.rpm` (RHEL/Fedora) at minimum.
- **`bootloader_ignore_signals: False`** — adapt to True so PyInstaller bootloader handles signals predictably during shutdown.

**Invent:**

- **Funi Build Manifest**. `builds/<platform>-<arch>.yaml` declares: PyInstaller config, electron-builder config, signing config, target distribution channels, post-build smoke tests. CI iterates the manifest; new platforms added by writing a manifest, not by editing two separate build configs. Vow tie-in: **Modular Authorship**.
- **Reproducible-Build Verification**. CI publishes the build's SHA256 plus a `BUILD_PROVENANCE.json` describing exact toolchain versions. An independent rebuild on identical inputs must produce a matching SHA256. Vow tie-in: **Defended System Prompt** generalizes to **Defended Builds**.
- **Tier-Aware Bundles**. The full Ember bundle includes VRM rendering, voice, computer-control. A `ember-mini.AppImage` is a tier-3 bundle: no VRM, no voice, no GUI. ~50 MB instead of ~500. Targets Pi and low-memory hosts. Vow tie-in: **Smallness**, **Tiered Presence**.
- **Hidden-Imports CI Walker**. A test job runs the built binary through every documented feature path and reports ImportError occurrences. The hidden_imports list is then a generated artifact, not hand-curated. Eliminates the perpetual maintenance tax.
- **Cross-Platform Skill Symlink**. SAP ships `skills/` baked into the PyInstaller bundle, so user-installed skills are separate from default skills. Ember should bind-mount or symlink the default-skills set so updates can refresh defaults without overwriting user-installed ones.
- **Pi-First Build**. Build the ARM AppImage first, then degrade-gracefully to x64. SAP builds x64-first and then asks "could we also do ARM?". Ember should invert the priority. Vow tie-in: **Smallness**.
