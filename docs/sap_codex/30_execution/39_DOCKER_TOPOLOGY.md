---
codex_id: 39_DOCKER_TOPOLOGY
title: Docker Topology — Two Containers, One Gateway, Zero Avatars
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - docker-compose.yml:1-29
  - docker-compose-acr.yml:1-27
  - Dockerfile:1-43
  - py/computer_use_tool.py:10-30 (IS_DOCKER fallback)
  - py/node_runner.py:23-26 (IS_DOCKER branch)
ember_subsystem_targets: [Funi, Munnr]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/31_PYTHON_SERVER
  - 30_execution/33_COMPUTER_CONTROL_LOOP
  - 30_execution/3A_CROSS_PLATFORM_BUILDS
---

# Docker Topology

> *No Electron. No avatar. No mouse. Just an API and an Nginx-with-JWT in front of it. The Docker deployment is SAP-without-a-face.*

Forge. Eldra. The Docker story is the **headless** SAP. When you don't have a display, the entire avatar + computer-control + voice stack downgrades or disappears, and what's left is a chat API + IM bots + livestream ingest + MCP. This is the cleanest deployment SAP offers because it's the most constrained — half the features can't run, so the remaining half is forced to be self-sufficient.

## The Two-Container Pattern

```yaml
# docker-compose.yml:1-29
version: '3'

services:
  backend:
    image: ailm32442/super-agent-party:latest
    container_name: sap-backend
    restart: unless-stopped
    volumes:
      - ./super-agent-data:/app/data

  gateway:
    image: ailm32442/nginx-for-sap:latest
    container_name: sap-gateway
    restart: unless-stopped
    ports:
      - "3456:3456"
    environment:
      - JWT_SECRET=ChangeThisToARandomString123!
      - INIT_USER=root
      - INIT_PASS=pass
      - FORCE_RESET=false
    volumes:
      - ./gateway-data:/data
    depends_on:
      - backend
```

Two containers. The backend (Python FastAPI) and a gateway (Nginx + JWT auth). **The backend has no `ports:` mapping** — it is unreachable from outside the Docker network. Only the gateway exposes `3456:3456`. Every request enters via the gateway, is authenticated, and is forwarded to the backend.

This is **the right shape** for a public-facing deployment of SAP. Without the gateway, the backend's static mounts (`/`, `/vrm`, `/uploaded_files`, `/tool_temp`) are exposed unauthenticated — see [[31_PYTHON_SERVER]] for why that's a problem. With the gateway, every route requires a JWT.

### The Gateway Env Block

- `JWT_SECRET=ChangeThisToARandomString123!` — **literally the example string**. SAP relies on the operator changing it. Many operators won't. The README presumably warns; the compose file doesn't enforce.
- `INIT_USER=root`, `INIT_PASS=pass` — initial credentials. Reset on first start. The user is expected to change them via UI.
- `FORCE_RESET=false` — reset credentials back to `root/pass`. Set to `true`, restart, reset, set to `false`, restart. Three-step procedure for password recovery. There is no email reset, no recovery code, no out-of-band channel.

The gateway image is `ailm32442/nginx-for-sap:latest`. Source not in this repo — `nginx-for-sap` lives elsewhere. From the env vars, it's clearly Nginx + a Lua/JS auth layer or a custom binary. The `gateway-data` volume persists the credential state across restarts.

### The ACR Variant

```yaml
# docker-compose-acr.yml (compressed)
services:
  backend:
    image: crpi-9mgnqijkd7wc42x2.cn-shenzhen.personal.cr.aliyuncs.com/ailm32442/super-agent-party:latest
  gateway:
    image: crpi-9mgnqijkd7wc42x2.cn-shenzhen.personal.cr.aliyuncs.com/ailm32442/nginx-for-sap:latest
```

Identical except for image registry. ACR = Aliyun Container Registry (Shenzhen region). The mirror exists because Docker Hub is rate-limited or blocked from Chinese networks. Pulling 5 GB of Python+models from Docker Hub from a Shenzhen VPS can take 30 minutes; pulling from ACR-Shenzhen takes 30 seconds.

SAP ships both compose files. Operator picks one. This is the same GitHub-vs-Gitee pattern as the extension installer ([[38_EXTENSION_LIFECYCLE]]).

## The Dockerfile

```dockerfile
# Dockerfile:1-43
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y gcc curl git ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm install -g acpx@latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv venv && uv sync

COPY . .

RUN mkdir -p uploaded_files && chmod 755 uploaded_files

EXPOSE 3456

ENV HOST=0.0.0.0 \
    PORT=3456 \
    PYTHONUNBUFFERED=1 \
    IS_DOCKER=1

CMD [".venv/bin/python", "server.py", "--host", "0.0.0.0", "--port", "3456"]
```

Python 3.12-slim base. Node 20 from NodeSource (for extensions and `acpx`). `acpx` is the SAP companion CLI tool (Node-based, installed globally). `uv` for Python deps — fast modern Python dep manager.

**`IS_DOCKER=1`** is the flag every other module reads:

- `py/node_runner.py:23`: in Docker, use system `node`/`npm`, not Electron's bundled one.
- `py/computer_use_tool.py:10-20`: pyautogui import will fail (no DISPLAY); GUI_AVAILABLE = False; all mouse/keyboard tools return polite "Docker has no display" messages.

The CMD is the same Python invocation Electron would do with `--host 0.0.0.0 --port 3456`. No port auto-discovery in Docker — the port is fixed at 3456, the gateway expects that, the operator can override if needed.

### What's Missing

The Dockerfile **does not** install:

- Any display server (no `xvfb`, no Wayland)
- Any audio system (no `pulseaudio`, no `alsa`)
- Sherpa ASR / Moss TTS model files (these download on first use)
- VRM model files (these are user-uploaded via API)

These omissions mean:
- **No avatar window** — Docker SAP cannot render an avatar.
- **No mic input or speaker output** — voice features only work via API (file upload + transcript download).
- **No computer control** — `pyautogui` is disabled by the `GUI_AVAILABLE = False` path.
- **First-use download lag** — sherpa-onnx ASR model is ~200 MB and downloads on first ASR call.

This is intentional. Docker SAP is for **bot deployment**, not desktop presence. The IM bots, livestream ingest, MCP, and OpenAI-compat API all work fine without a display.

## The IS_DOCKER Branch in node_runner

```python
# py/node_runner.py:22-32 (recap from [[38_EXTENSION_LIFECYCLE]])
def _get_exec_cmds(self):
    if IS_DOCKER or not ELECTRON_NODE:
        npm_exe = "npm.cmd" if os.name == "nt" else "npm"
        return ["node"], [npm_exe]
    else:
        return [ELECTRON_NODE], [ELECTRON_NODE, ELECTRON_NPM_CLI]
```

In Docker, system Node is used (installed at Dockerfile line 10). On Electron desktop, Electron-as-Node is used. **Same extension code runs in both modes**, because Electron-as-Node is API-compatible with Node 20 (mostly — there are edge cases around `worker_threads` and `child_process` that some extensions hit).

The fact that one binary can be both the Electron runtime and the extension host is a deliberate ship decision that gives SAP simpler packaging (one binary in the AppImage; see [[3A_CROSS_PLATFORM_BUILDS]]).

## What Docker Buys You

- **Multi-instance hosting**: one VPS, ten compose stacks, ten independent SAP instances for ten customers. Not possible with the desktop build.
- **24/7 IM bot operation**: a desktop SAP stops when the laptop sleeps; Docker SAP keeps the WeChat/Discord/Telegram bots alive indefinitely.
- **Reproducible deployments**: pull the image, run docker-compose up, done. No "works on my Mac" pain.
- **Gateway-mediated auth**: real password protection in front of the API. Desktop build has none — it's localhost-only by default.

## What Docker Costs You

- **No avatar, no embodiment**. The point of SAP, for many users, is the VRM/Live2D companion. Docker can't deliver that.
- **No computer control of the host**. The `pyautogui` tools are no-ops.
- **No browser automation of the host's Chrome**. The CDP layer needs Electron's own webview; Docker has no Electron.
- **No VTube Studio bridge**. VTS runs on the host, not in the container; the bridge would have to connect across the Docker network boundary, which is doable but not configured by default.
- **Voice loop incomplete**. Without audio hardware, mic input and speaker output are file-based, not real-time.

## The Aliyun-CR Detail

`crpi-9mgnqijkd7wc42x2.cn-shenzhen.personal.cr.aliyuncs.com` is **a personal Aliyun account's image registry**. The `crpi-` prefix is Aliyun's standard naming for personal CR instances. This means:
- The image source is one developer's account, not an organization's.
- If the developer's Aliyun account suspends, the China-deployment compose file breaks.
- There is no official mirror in `acr-shanghai`, `acr-beijing`, etc. — just this one.

For Ember, the lesson is **mirror redundancy**: have at least 2 China-accessible image mirrors, ideally one in each major Chinese region, to avoid single-point-of-failure.

## Where It Breaks

- **`JWT_SECRET=ChangeThisToARandomString123!` default**. Operators ship with the example secret. JWT forgery is then trivial.
- **No HTTPS in the compose file**. The gateway exposes port 3456 raw. The README probably says "put a reverse proxy in front"; many operators won't.
- **The backend has no per-user auth**. The gateway authenticates, then forwards to the backend with a trust-the-gateway assumption. If anyone gets inside the Docker network (e.g. another container on the same docker network), they have unauthenticated backend access.
- **`super-agent-data:/app/data` is bind-mounted**. Sensible. Also means everything sensitive lives in `./super-agent-data` on the host: API keys, conversation history, affection data ([[3B_AFFECTION_LOOP]]). Default permissions are 0755. If the host is multi-tenant, every user can read every other user's SAP state.
- **`restart: unless-stopped`** for the backend means a crashing backend will be restarted continuously, potentially looping in some error states. There's no exponential backoff or fail-fast threshold.
- **No healthcheck** in either service. Docker has no idea if the backend is functional vs just running. The gateway has no idea if the backend is responding.
- **The `gateway-data` volume is also bind-mounted**, holding the JWT signing state and user credentials. Compromised host file system = compromised auth.
- **No resource limits**. `mem_limit`, `cpus`, etc. are absent. A misbehaving LLM call can consume all host memory.

## Where It Surprises

- **Two compose files**, dual-sourced, both ship with the repo. China-deployment story is explicit. Most Western open-source projects neglect this.
- **The `IS_DOCKER` env var is read in two specific modules** (node_runner, computer_use_tool) and that's it. The rest of the code is environment-agnostic. Clean.
- **The Electron-as-Node-runtime fallback** elegantly degrades to system Node in Docker. Same extension code, two runtimes.
- **The `acpx` global install** at Dockerfile line 15 is the SAP CLI tool — separate from SAP itself, used by the agent for npm package management. Installing it globally avoids per-session npm install overhead. Small detail, real perf win.
- **The Dockerfile is 43 lines**. For a project this big, that's tight. No multi-stage builds, no buildkit cache mounts, no specialized base images. It works. It's also under-optimized: image size is probably 1.5+ GB; with proper multi-stage builds it could be 600 MB.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — the desktop counterpart that Docker replaces
- [[31_PYTHON_SERVER]] — what runs inside the backend container
- [[33_COMPUTER_CONTROL_LOOP]] — disabled-in-Docker tool layer
- [[3A_CROSS_PLATFORM_BUILDS]] — the desktop build path
- [[53_SECURITY_REVIEW]] (Auditor) — auth model audit
- [[59_CONFIG_DRIFT]] (Auditor) — JWT secret and credential defaults

## What This Means for Ember

**Adopt:**

- **The two-container backend + gateway pattern** for public-facing Ember deployments. Backend has no exposed port; gateway handles auth + TLS + rate limiting. Bind to Funi's deployment manifest.
- **The `IS_DOCKER`-style env flag** for environment-dependent behavior. Code that needs to know its surroundings reads one env var, and the behavior branches at module-import time. Document as a Vow proposal: **Honest Environment** — every subsystem declares its environment-dependent behavior in one place.
- **The dual-mirror image pattern**. Ember should ship images on at least two registries (e.g. `ghcr.io` + an alternate China-accessible mirror) with parallel compose files.
- **The bind-mounted data dir** at a predictable path (`./<project>-data:/app/data`). Operator-friendly. Backups are filesystem-level.

**Adapt:**

- **The default `JWT_SECRET=ChangeThis...`** → adapt to generate a random secret on first start and bind-mount it. The compose file should fail to start until a real secret is in place, never accept the default. SAP relies on operator diligence; Ember should refuse to ship insecure defaults.
- **The `INIT_USER=root, INIT_PASS=pass`** → adapt to generate a one-time admin token, log it to container stdout, and require the operator to set a real password via the first UI session. Vow tie-in: **Defended System Prompt** generalizes to **Defended Credentials**.
- **The single gateway** → adapt to support multi-tenant via subdomain routing or path prefixing. SAP's gateway is single-tenant; Ember's should be tenant-aware so one VPS can host multiple Ember identities.
- **`restart: unless-stopped`** → adapt to `restart: on-failure:5` with a crash-loop detector that escalates to operator notification rather than restart-forever.

**Avoid:**

- **No healthcheck**. Ember's compose must include `healthcheck:` directives so Docker knows when a container is sick.
- **No resource limits**. Every Ember container declares `mem_limit`, `cpus`, `pids_limit` defaults. Operators can override but never have unlimited defaults.
- **Backend trust-the-gateway model**. Ember's backend must authenticate every request, even inside the Docker network. Defense in depth.
- **Personal-account image registry** for the official source-of-truth image. Use an org account or a GitHub-Actions-built `ghcr.io` image with reproducible-build provenance.

**Invent:**

- **Funi Deployment Manifest**. A single `ember.yaml` file declares: tier (Pi/laptop/workstation/Docker/cluster), which subsystems are enabled, which ports are exposed, which secrets are required. The deploy CLI reads this manifest and generates the appropriate compose/Dockerfile/systemd unit. SAP has separate compose files; Ember should generate them from a typed source.
- **Tiered Health Checks**. Beyond Docker's binary "healthy/unhealthy", Ember exposes a per-subsystem health surface. The gateway aggregates subsystem health into a single `/health` response with per-subsystem detail. SAP's `/health` is one-line truthy; Ember's is structured.
- **Container Lifecycle Hooks**. Pre-stop hooks let Ember subsystems serialize state to the bind-mount before shutdown. SAP relies on lifespan cleanup, which can be interrupted; Ember's containers should checkpoint state explicitly.
- **Aliyun-Style Bind-Mount Encryption**. The `./super-agent-data` directory holds sensitive material in plaintext. Ember should offer an opt-in encrypted-at-rest mode using `gocryptfs` or similar, with the master key in the operator's keyring. Vow proposal: **Credential Discipline** generalizes to **Data-at-Rest Encryption**.
- **Federated Container Cluster**. Multiple Ember instances on different hosts discover each other via mDNS or a shared discovery service, form a federated party ([[62_PARTY_PROTOCOL]]), and route load. The Docker compose deploys one node of the cluster; the cluster is what users actually consume. SAP is single-node; Ember should architect for many. Vow tie-in: **Federated Self**.
- **Honest Display-Capability Negotiation**. The desktop bridge declares its capabilities (`vrm`, `live2d`, `voice_in`, `voice_out`, `screen_cap`, `mouse`, `keyboard`) at startup. The backend selects the highest-fidelity tool set the bridge can deliver. Docker → text-only. Laptop → full embodiment. The same Ember serves both. Vow tie-in: **Tiered Presence**.
