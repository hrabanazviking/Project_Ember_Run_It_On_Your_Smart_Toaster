---
codex_id: 1B_DEPLOYMENT_DOMAIN
title: Deployment Domain — Builds, Sandboxes, and the Multi-Runtime Tightrope
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/node_runner.py:1-123
  - py/node_api.py:1-8
  - py/uv_api.py:1-9
  - py/docker_api.py:1-16
  - Dockerfile
  - docker-compose.yml
  - docker-compose-acr.yml
  - package.json
  - pyproject.toml
  - main.js:1-50
ember_subsystem_targets: [Funi, Smiðja]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/18_EXTENSION_DOMAIN
  - 30_execution/3A_CROSS_PLATFORM_BUILDS
  - 30_execution/39_DOCKER_TOPOLOGY
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
---

# Deployment Domain
## Builds, Sandboxes, and the Multi-Runtime Tightrope

*— Rúnhild Svartdóttir, Architect*

> *To ship is to make a promise about a foreign machine. The promise is hard because the machine is foreign. SAP makes the promise five times — Win10, Win11, macOS, Linux, Docker — and mostly keeps it. The keeping costs more code than the promising.*

The deployment domain is the part of SAP that bridges to the host machine's reality — the Python runtime, the Node runtime, the Docker daemon, the uv package manager, the Electron packaging chain. It is small (~150 LOC of Python plus the build configs) but every line is load-bearing. This doc names the surface.

---

## 1. The Subject Itself

**What the domain owns:** detection of runtime tools (`node`, `npm`, `uv`, `docker`), per-extension Node subprocess management, Docker compose topologies, Electron+PyInstaller cross-platform builds.

**What it does *not* own:**
- The Python sandbox itself (that's `cli_tool.py`'s zerobox integration — see [[13_COMPUTER_CONTROL_DOMAIN]])
- The build outputs (those go to `release/`, not in this domain)
- The auto-updater (that's `main.js` + `electron-updater`)
- The first-run config wizard (that's UI in `static/`)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/node_runner.py` | 123 | Per-extension Node subprocess (start/stop, port alloc, npm install) |
| `py/node_api.py` | 8 | `/api/node/probe` — `shutil.which("node")` |
| `py/uv_api.py` | 9 | `/api/uv/probe` — `shutil.which("uv")` |
| `py/docker_api.py` | 16 | `/api/docker/probe` — `shutil.which("docker")` |
| `Dockerfile` + `docker-compose.yml` + `docker-compose-acr.yml` | — | Docker topologies (default + Alibaba Container Registry variant) |
| `package.json` + `main.js` | — | Electron build config, app lifecycle |
| `pyproject.toml` + `uv.lock` + `server.spec` | — | Python deps (managed by `uv`) + PyInstaller spec |

Small files, big consequences. The deployment surface is the place where SAP's claim of "Win10/11 + Server 2025 + macOS M-chip + Linux AppImage + .deb + Docker" lands.

---

## 2. How It Works

### 2.1 The probe trio

Three identical-shaped one-route routers (`py/node_api.py`, `py/uv_api.py`, `py/docker_api.py`) return `{installed: bool, path?: str}` based on `shutil.which(name)`. The Electron UI hits these to know what install options to gray out in the extension panel. The pattern is dead simple:

```python
# /tmp/super-agent-party/py/docker_api.py:6-14
@router.get("/probe")
def probe_docker():
    docker_path = shutil.which("docker")
    return {
        "installed": docker_path is not None,
        "path": docker_path
    }
```

Three files, twenty-five lines combined. Honestly the kind of code that should be a single `probe(tool: str)` route with a configured allowlist of probable tools. But the parallelism is at least *consistent*.

### 2.2 The Node runtime under Electron

The most architecturally interesting piece is at `py/node_runner.py:14-31` — handling the case where SAP is packaged as an Electron app and Node is not separately installed:

```python
# /tmp/super-agent-party/py/node_runner.py:10-12, 21-31
ELECTRON_NODE = os.environ.get("ELECTRON_NODE_EXEC")
ELECTRON_NPM_CLI = os.environ.get("ELECTRON_NPM_CLI")
...
def _get_exec_cmds(self):
    if IS_DOCKER or not ELECTRON_NODE:
        npm_exe = "npm.cmd" if os.name == "nt" else "npm"
        return ["node"], [npm_exe]
    else:
        # Electron桌面端环境：
        # Node 命令: electron.exe
        # NPM 命令: electron.exe /path/to/npm-cli.js
        return [ELECTRON_NODE], [ELECTRON_NODE, ELECTRON_NPM_CLI]
```

When packaged as Electron, SAP sets `ELECTRON_NODE_EXEC` to the path of the Electron binary itself. Electron supports a runtime mode `ELECTRON_RUN_AS_NODE=1` which makes the same binary behave as a vanilla Node interpreter. `npm` is invoked via the bundled `npm-cli.js`. So **the packaged app never requires a separate Node install** — the Electron binary doubles as the Node runtime for extensions.

This is genuinely clever. It is also fragile: a future Electron version might change the env-var contract, and SAP would silently fall back to looking for `node` on PATH (which a packaged-app user wouldn't have).

### 2.3 The per-extension subprocess

`NodeExtension(ext_id)` (`py/node_runner.py:12`) is the lifecycle wrapper. `start()` (line 39):

1. Read `package.json` (line 19).
2. Decide exec commands per environment.
3. Check `node_modules` mtime vs `package.json` mtime (line 49) — only reinstall when deps changed.
4. Run `npm install --production` (line 56-67) — capture stdout/stderr; raise on nonzero exit.
5. Pick a port (line 76): `package.json.nodePort` or OS-assigned `_free_port()`.
6. Spawn `node index.js <port>` (line 78-83) with `NODE_EXTENSION_ID` env.
7. Wait for the port to open via `_wait_port` (line 84, line 100-104).

`stop()` (line 87-91): `terminate()` + `await proc.wait()`. No SIGKILL fallback if the process ignores SIGTERM.

The port range is `(3100, 13999)` (line 6). With 10,900 possible ports, SAP comfortably accommodates dozens of simultaneous extensions; it does not need a port-pool manager.

### 2.4 The Docker topologies

`docker-compose.yml` is the standard topology; `docker-compose-acr.yml` is the Alibaba Container Registry variant (China-friendly registry). SAP's containerized deployment includes the Python server, optional dependencies, and a gateway for auth/routing.

The compose file is not in this doc's deep-read scope — the Forge owns [[30_execution/39_DOCKER_TOPOLOGY]] — but the *domain* point is that **SAP ships two compose variants** for different registry availabilities, and the choice is at the user's discretion. This is the kind of small-but-real internationalization investment that suggests SAP has a real global userbase.

### 2.5 The Python deps

`pyproject.toml` lists the Python deps; `uv.lock` is the resolved lockfile. SAP uses **uv** as the package manager — the modern Rust-based alternative to pip. The `/api/uv/probe` route exists because some SAP install paths invoke `uv` at runtime (to install extensions' Python deps). uv is fast enough that on-demand install is acceptable; pip would not be.

### 2.6 The PyInstaller build

`server.spec` (PyInstaller spec file) configures the bundling. Combined with `package.json`'s electron-builder config, SAP produces:
- `.exe` for Windows (Win10/11)
- `.dmg` for macOS (M-chip + Intel)
- `.AppImage` and `.deb` for Linux
- A portable `.zip` for power users

This is the cross-platform claim. The exact spec mechanics are Forge territory ([[30_execution/3A_CROSS_PLATFORM_BUILDS]]); the domain point is that **a desktop user can install SAP via the platform-native installer of their choice**.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The npm install is online-required

`py/node_runner.py:53-67` invokes `npm install --production` synchronously. There is no offline mode; no vendored `node_modules` fallback. A first-run on an offline host hangs at the subprocess `communicate()`, then surfaces the network error. Compare to `py/sleep_guard.py:108-120` where systemd-inhibit failure is logged and fall-through to xdotool is attempted — the Node deps install has no equivalent fallback.

### 3.2 The `stop` is not forceful

`NodeExtension.stop()` (`py/node_runner.py:87-91`) `terminate()`s the process and `await proc.wait()`. If the extension is hung in an infinite loop ignoring SIGTERM, `wait()` blocks forever. No timeout; no `proc.kill()` escalation.

### 3.3 The port-wait timeout is generous

`_wait_port(port, timeout=10)` (`py/node_runner.py:100-104`) polls 10 times per second for 10 seconds. An extension that takes >10s to bind its port fails to start. For most Node apps this is fine; for an extension that downloads a model at startup, it is not.

### 3.4 The `ELECTRON_NODE_EXEC` contract is implicit

If the env vars are set wrong (or set to a stale Electron binary path), the extension launches with the wrong Node. There is no validation that the binary is callable; the first `npm install` will fail and surface whatever error Electron produces, which is usually inscrutable to a non-Electron-savvy user.

### 3.5 The probe routes don't check version

`shutil.which("node")` returns the path *if any* `node` is on PATH. It does not check that the version is one SAP supports (presumably ≥16 for modern extensions). An old Node will pass the probe and fail at extension launch.

### 3.6 The crisp parts

- The **Electron-as-Node** pattern. A small, real innovation.
- The **mtime-based npm-install skip** (`py/node_runner.py:49-51`).
- The **two-compose-variant** internationalization.
- The **uv adoption** — modern Python tooling rather than pip.
- The **simple probe routes** — three lines per route, three files; consistent shape.
- The **port-range allocation** — no global port manager needed; ample range.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 12 (Extension surface uses this)
- [[18_EXTENSION_DOMAIN]] for the extension lifecycle that this domain supports
- [[30_execution/3A_CROSS_PLATFORM_BUILDS]] (Forge) for the build-spec deep dive
- [[30_execution/39_DOCKER_TOPOLOGY]] (Forge) for the compose-file deep dive
- [[60_synthesis/63_PERFORMANCE_TIER_ENGINE]] for the tier-collapse Ember invents
- [[hermes:HEM-18_HERMES_CLI]] for the contrasting CLI-first deployment shape
- [[peer:LETTA-7_SURFACE]] for the contrasting "single Python service" shape

---

## What This Means for Ember

**Adopt:**
- The **Electron-as-Node** trick (`py/node_runner.py:21-31`) when packaging Ember as a desktop app.
- The **mtime-based dependency-install skip** (`py/node_runner.py:49-51`) generalized to any "expensive setup vs cheap source" decision.
- The **per-extension port allocation** in a wide range — Ember Realms can claim local ports the same way.
- The **uv** as Python package manager. Modern; fast; lockfile-honest.
- The **two-compose-variant** discipline — Ember ships a default compose and a *whatever-Volmarr-needs* compose (probably tailnet-bound and gungnir-aware).

**Adapt:**
- The **probe trio** — adapt to a single `/api/probe/{name}` route with a configured allowlist (`node`, `uv`, `docker`, `ollama`, `cuda-runtime`, `vts`, ...) and per-tool version-check policy. Three files become one.
- The **terminate-without-kill-escalation** — adapt to **terminate, wait-with-timeout, then kill**. Funi's subprocess management is non-hanging by construction.
- The **online-required npm install** — adapt to **offline-first**: extensions may declare a vendored `node_modules.tar.gz` in their manifest; if present, untar instead of npm-install. Online install is the fallback, not the default.

**Avoid:**
- **Probes that don't check version.** Version is part of the probe contract.
- **Inscrutable Electron-NODE errors** when env vars are stale. Validate the binary is callable and the version is supported at probe time, not at first use.
- **A `wait()` that can hang forever.** Every subprocess wait in Ember has a timeout + escalation policy.
- **Two compose files when there should be one parameterized one.** A Jinja-templated compose with a `tier_manifest`-driven render is the right shape.

**Invent:**
- **Tier-Aware Deployment Manifests.** Ember's deployment is configured by `tier_manifest.yaml` — declares the host tier (pi / laptop / workstation / server), the included True Names, the enabled reach platforms. The manifest *parameterizes* the build pipeline (which PyInstaller spec, which compose, which model downloads). One source of truth; multiple deploy outputs. SAP achieves cross-platform by ifs; Ember by manifest.
- **The Bring-Your-Own-Runtime Vow.** Where SAP bundles Electron-as-Node, Ember declares: *any* runtime Ember depends on must be probeable, version-pinnable, and offlineable. If Ember requires `ollama`, the manifest names the version; the build can vendor or require it; the user is warned at install-time, not at first-use.
- **Cross-Realm Dependency Sharing.** Two Ember Realms on the same host (e.g. main Ember + an extension Realm) share their Python venv and Node `node_modules` via symlink, not duplication. SAP gives each extension its own `node_modules`; Ember dedupes at the host filesystem level via content-addressed storage (the same `package-lock.json` resolves to the same store).
- **The Hermes-Style Doctor.** Ember exposes `ember doctor` — runs every probe, checks every dep version, validates every env-var contract, surfaces every degradation. Output is human-readable + machine-parseable. SAP has no equivalent; the user discovers degradation by features failing silently.
- **The Tailnet-Default Build.** Per Volmarr's standing preference, Ember's default `docker-compose.yml` binds to the Tailscale interface (`tailscale0` or its IP), not `0.0.0.0`. The `127.0.0.1` mode is opt-in for users who explicitly want localhost-only. SAP defaults to `0.0.0.0` in many places (a Docker-friendly choice that exposes to LAN unless firewalled); Ember inverts the default.
