---
codex_id: 24_EXTENSION_INTERFACE
title: Extension Interface — package.json, the Port, and the Spawned Process
role: Architect
layer: Interface
status: draft
sap_source_refs:
  - py/extensions.py:1-631
  - py/extensions.py:23-55
  - py/node_runner.py:1-123
  - main.js:995-1150
ember_subsystem_targets: [Funi, Smiðja]
cross_refs:
  - 10_domain/18_EXTENSION_DOMAIN
  - 10_domain/1B_DEPLOYMENT_DOMAIN
  - 20_interface/23_SKILL_INTERFACE
  - 30_execution/38_EXTENSION_LIFECYCLE
  - 60_synthesis/66_INVENTED_METHODS
---

# Extension Interface
## package.json, the Port, and the Spawned Process

*— Rúnhild Svartdóttir, Architect*

> *An extension is a contract that says: I will run as a separate process; I will listen on a port; I will not need to know how the rest of the system works; I will receive only what you give me. The contract is short. The trust is wide.*

The Extension interface is SAP's *heavyweight* plugin surface — Node.js subprocess applications that run beside the main SAP server, present their own UI in a window, and communicate via HTTP. This doc names what an extension must contain, what SAP promises in return, and where the contract is more *suggestion* than *enforcement*.

---

## 1. The Subject

**What an Extension is:** a directory containing a `package.json` (Node module manifest) and an `index.js` (or whatever the manifest's `main` field points to). On install, SAP runs `npm install --production`, picks a port, spawns the process, and offers a window pointing at that port.

**The contract:**

| Field | Required | Source | Used by |
|---|---|---|---|
| `id` | Yes | install metadata (URL-derived: `<owner>_<repo>`) | Registry, dedup |
| `name` | Yes | `Extension` Pydantic model field (line 23-37) | UI display |
| `description` | Optional | model field | UI |
| `version` | Optional ("1.0.0" default) | model field | Updates |
| `author` | Optional ("未知" default) | model field | Attribution |
| `systemPrompt` | Optional | model field | If non-empty, injected into LLM system prompt when extension is active |
| `repository` | Optional | model field | Update source URL |
| `backupRepository` | Optional | model field | Failover update source |
| `category` | Optional | model field | UI grouping |
| `transparent` | Optional (False) | model field | Window transparency for OBS capture |
| `width` / `height` | 800 / 600 | model field | Default window size |
| `enableVrmWindowSize` | False | model field | Use VRM window dimensions instead |
| `nodePort` | Optional | `package.json` | Pin a specific port; else OS-assigned |

**Where the interface is implemented:**

| File | LOC | Owns |
|---|---|---|
| `py/extensions.py` | 631 | Install, uninstall, list, task tracking |
| `py/node_runner.py` | 123 | Subprocess lifecycle |
| `main.js:995-1150` | ~150 | Window spawn via IPC (`start-vrm-window`, `start-extension-window`) |

---

## 2. How It Works

### 2.1 The Pydantic Extension model

`Extension` at `py/extensions.py:23-37`:

```python
class Extension(BaseModel):
    id: str
    name: str
    description: str = "无描述"
    version: str = "1.0.0"
    author: str = "未知"
    systemPrompt: str = ""
    repository: str = ""
    backupRepository: Optional[str] = ""
    category: str = ""
    transparent: bool = False
    width: int = 800
    height: int = 600
    enableVrmWindowSize: bool = False
```

This is **the explicit interface** — the typed declaration of what an extension is metadata-wise. Compared to the Skill interface ([[23_SKILL_INTERFACE]]) which has YAML frontmatter, the extension interface has a Python Pydantic model. The mismatch is unfortunate; the two surfaces could share a manifest schema.

The Pydantic shape is derived from extension metadata that lives... not in a single conventional file, but assembled from several sources: the `package.json`, optionally a `manifest.json`, optionally a `meta.json`, plus user inputs via the install API. The exact discovery order is in the longer `install_from_github` path (lines beyond what we've sampled).

### 2.2 The install flow

`POST /api/extensions/install-from-github` takes `{url, backupUrl}` and:

1. Parses the URL to extract `<owner>_<repo>` as the extension ID (`get_ext_id_from_url`, line 160-166).
2. Updates the in-process task tracker to `"installing"` (line 150-157).
3. Schedules `_do_zip_install` as a background task (which downloads, unpacks, places).
4. Returns immediately with `{ext_id, status: "installing"}`.

The client polls `/api/extensions/install-status/{ext_id}` for progress.

### 2.3 The download path

`download_zip(url, dest, timeout=60.0)` at line 176-183:

```python
async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
    async with client.stream("GET", url) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            async for chunk in resp.aiter_bytes():
                f.write(chunk)
```

Streamed; redirect-following; explicit timeout. Compared to `py/sub_agent.py:56` which has a 600-second timeout and no rationale, this 60-second timeout is well-chosen for a zip download.

### 2.4 The unpack and root discovery

`find_root_dir(temp_path)` at line 110-120 handles the "GitHub zip extracts to `<repo>-main/` wrapper" case:

```python
def find_root_dir(temp_path: Path) -> Path:
    entries = [p for p in temp_path.iterdir() if p.is_dir()]
    entry_files = ['index.html', 'index.js', 'package.json', 'manifest.json']
    if len(entries) == 1:
        subdir = entries[0]
        if any((subdir / f).exists() for f in entry_files):
            return subdir
    return temp_path
```

The heuristic: if there's exactly one subdirectory and it contains a likely entry file, the subdirectory is the actual extension root. Else the temp dir itself is the root. The four entry-file names are the conventional choices.

### 2.5 The Windows-readonly dance

Already named in [[18_EXTENSION_DOMAIN]] §2.5. `_remove_readonly`, `robust_rmtree`, `make_tree_writable` (lines 58-107) handle the npm-installs-readonly-files-on-Windows footgun. The `onexc` vs `onerror` shim (line 80, 89) handles the Python `shutil.rmtree` API change.

### 2.6 The subprocess lifecycle

`NodeExtension(ext_id)` (`py/node_runner.py:12`) is the runtime wrapper. See [[18_EXTENSION_DOMAIN]] §2.2 and [[1B_DEPLOYMENT_DOMAIN]] §2.3 for the deeper analysis. Key shape:

- Pick exec commands (Electron-as-Node trick or system node/npm).
- mtime-check `node_modules` vs `package.json`; reinstall if stale.
- Pick port (manifest or OS-assigned).
- Spawn `node index.js <port>` with `NODE_EXTENSION_ID` env.
- Wait for port to open (10s timeout).

### 2.7 The window connection

`main.js` exposes IPC handlers including `start-extension-window`. The Electron renderer opens a `BrowserWindow` pointing at `http://localhost:<port>/`. The extension's UI is loaded as a normal web page. The Electron window can be configured (per the `transparent`/`width`/`height` fields above) for OBS-friendliness.

### 2.8 The systemPrompt field

When `Extension.systemPrompt` is non-empty and the extension is active, the field is injected into the LLM's system prompt (presumably in `server.py`, alongside the other prompt assemblers). So an extension can *teach* the LLM about its existence — "you have access to extension X; call it via Y" — even though the extension is a Node process not directly callable as an LLM tool.

This is the **bridge between extensions and skills**: an extension can declare a systemPrompt that *looks like a skill body*, giving the LLM procedural-memory guidance about how to use the extension. The two systems converge at this point — but only via convention, not via shared schema.

---

## 3. The Contract — Inputs, Outputs, Side Effects, Invariants

### 3.1 What an Extension must provide (the producer contract)

- A directory.
- A `package.json` (Node module manifest).
- An `index.js` (or `main`-named entry) that listens on a TCP port passed as `argv[2]`.
- HTML / assets servable via that HTTP port.

### 3.2 What the system provides (the consumer contract)

- Install from GitHub URL or zip upload.
- `npm install --production` once on first run (or on `package.json` mtime change).
- A free TCP port via `_free_port()` (or honor `package.json.nodePort`).
- A spawn with `argv = ["node", "index.js", "<port>"]` and `env.NODE_EXTENSION_ID = <id>`.
- A `BrowserWindow` pointing at `http://localhost:<port>/` on user demand.
- Optional injection of `Extension.systemPrompt` into the LLM system prompt.
- Optional VRM-window-size linkage if `enableVrmWindowSize`.

### 3.3 Side effects of install

- Files copied to `<EXT_DIR>/<id>/`.
- Old extension dir robust-rmtree'd if present.
- Temp dirs created and cleaned in `finally`.
- Network call to GitHub (or wherever the zip is).
- (At spawn time) network call to npm registry if `node_modules` is stale.

### 3.4 Invariants enforced

- Extension ID is `<owner>_<repo>` from the install URL — collision-resistant by virtue of GitHub's namespace.
- Subprocess port is open within 10 seconds or fail.
- Windows readonly files are chmod'd writable before rmtree.

### 3.5 Invariants *not* enforced

- **No signature** on the downloaded code.
- **No capability manifest** declaring what filesystem paths, network hosts, or system features the extension uses.
- **No sandbox** — the Node process has full filesystem and network access.
- **No version pinning** of npm deps beyond whatever `package.json` declares.
- **No resource limits** — an extension can eat CPU, RAM, or open file handles without bound.
- **No inter-extension communication boundary** — extensions can find each other's ports via the same `_free_port` range and call each other; SAP doesn't notice.

### 3.6 The leak

The interface leak is **trust**: extensions are arbitrary Node code. The `systemPrompt` injection means a malicious extension can *also* prompt-inject the LLM. The combination — code-execution + system-prompt-injection — is broader than either alone. A compromised extension is a compromised SAP.

---

## 4. Where It Breaks and Where It Surprises

### 4.1 No sandbox

Already named in §3.5. Extensions are full-trust Node processes. The OS process boundary is the only isolation.

### 4.2 Two metadata systems

`package.json` is the Node convention. The Pydantic `Extension` model is SAP's convention. The mapping between them is implicit (per the install-from-github path). A new extension author has to figure out *both* — what does Node want, what does SAP want — and the answers differ.

### 4.3 No inter-extension protocol

Two extensions on the same SAP instance know nothing about each other. There is no shared event bus. There is no shared storage. There is no "ping the other extension" API. Extensions are isolated by accident, not by design.

### 4.4 The port-range coincidence

`PORT_RANGE = (3100, 13999)` at `py/node_runner.py:6`. Multiple extensions get distinct OS-assigned ports inside the range. Nothing prevents extension A from binding to port 5000 and extension B from *trying* to bind 5000 and silently failing (then `_wait_port` times out).

### 4.5 The install runs npm online

Already noted. Air-gapped install requires pre-vendored `node_modules` (not a documented path).

### 4.6 The crisp parts

- The **Pydantic typed metadata model**.
- The **find-root-dir heuristic** for GitHub zip wrappers.
- The **Windows-readonly handling**.
- The **mtime-based npm-install skip**.
- The **streamed download with explicit timeout**.
- The **task tracker** for slow installs.
- The **systemPrompt field** as a bridge to procedural-memory.

---

## 5. Cross-References

- [[18_EXTENSION_DOMAIN]] — the domain this interface belongs to
- [[1B_DEPLOYMENT_DOMAIN]] — the runtime substrate
- [[23_SKILL_INTERFACE]] — the lightweight sibling
- [[30_execution/38_EXTENSION_LIFECYCLE]] (Forge) — the execution deep dive
- [[60_synthesis/66_INVENTED_METHODS]] (Scribe) — the unified manifest invention
- [[hermes:HEM-27_PLUGIN_INTERFACE]] — Hermes's plugin interface (more developed)

---

## What This Means for Ember

**Adopt:**
- The **find-root-dir heuristic** for unwrapping GitHub zip downloads.
- The **Windows-readonly dance** (`_remove_readonly` + `robust_rmtree`) — apply to all filesystem mutations.
- The **mtime-based dependency-install skip** generalized.
- The **streamed download with explicit timeout** for any large-file fetch.
- The **per-id-task-tracker** pattern with progress percent.

**Adapt:**
- The **Pydantic Extension model** + the YAML SKILL.md — adapt to a **unified `manifest.yaml`** across both extension and skill types. One schema; multiple body kinds (`body: markdown` for skills; `body: node-process` for extensions; `body: python-handler` for tools; `body: docker-service` for heavy extensions).
- The **Electron-as-Node** trick — adapt to Ember's packaged-app extension story.
- The **subprocess-on-a-port** model — adapt to the broader **Realm** abstraction: every extension is a Realm with reduced scope, communicating via MCP (not HTTP), with a typed capability manifest.

**Avoid:**
- **Full-trust extensions.** Every Ember extension declares its capabilities; the host enforces.
- **No signature on downloads.** Every Ember extension manifest includes hash + (optionally) signature; install verifies.
- **Two metadata systems** for closely-related artifacts.
- **Inter-extension communication by accident.** Either explicitly support it (via Sögumiðla) or explicitly prevent it (via process isolation + no shared bus).
- **`systemPrompt` injection without scope.** A skill body in Ember can be in the system prompt; an extension's prompt is in a *namespaced* section ("Per extension <name>: ...") so the LLM knows it's not authoritative.

**Invent:**
- **The Unified Extension Manifest.** A single YAML schema declares: identity (id, name, version, author, signature), capabilities (tools, data, network, surface), body kind (markdown / python / node / docker / external-MCP), and tier eligibility. Skills and extensions become two body-kinds under one manifest. SAP's two-system split collapses.
- **Extension Realms.** An extension is a Realm — its own Funi sub-entrypoint, its own Smiðja with capability-gated tools, its own MCP surface. Two extensions cannot communicate except through the parent Realm's Sögumiðla bus, and only on topics the parent has whitelisted. SAP isolates by accident; Ember isolates by design.
- **The Capability Trust Tier.** Extensions are classified the same way skills are ([[23_SKILL_INTERFACE]] Invent): system / verified / community / local. Each tier has a different capability ceiling (e.g. only `system` extensions can declare `shell_exec`). A `community` extension that requests `shell_exec` fails install with a typed message.
- **The Cross-Tier Body Selector.** An extension manifest can declare multiple bodies: a Pi-body (lightweight, e.g. text-only), a laptop-body (mid-weight, e.g. embedded SQLite), a workstation-body (heavyweight, e.g. ComfyUI). Funi loads the body matching the current host tier. SAP installs one body and hopes; Ember installs the matrix.
- **The Auditable systemPrompt Inject.** Every extension's prompt injection is wrapped in a namespace marker: `<<extension:foo:start>>...<<extension:foo:end>>`. The LLM is told to treat content within a namespace as *advisory*, not as authoritative system instructions. The wrapper also enables provenance — if the LLM emits content traceable to a namespaced prompt, Ember can audit which extension authored that influence.
