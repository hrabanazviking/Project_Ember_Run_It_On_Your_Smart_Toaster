---
codex_id: 18_EXTENSION_DOMAIN
title: Extension Domain — Skills, Extensions, and the Two Plugin Surfaces
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/skills.py:1-200
  - py/skills.py:390-680
  - py/extensions.py:1-200
  - py/node_runner.py:1-123
  - skills/skill-creator/
  - skills/sap-extension-creator/
ember_subsystem_targets: [Smiðja, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/23_SKILL_INTERFACE
  - 20_interface/24_EXTENSION_INTERFACE
  - 30_execution/38_EXTENSION_LIFECYCLE
---

# Extension Domain
## Skills, Extensions, and the Two Plugin Surfaces

*— Rúnhild Svartdóttir, Architect*

> *A system that cannot grow is a system that will be replaced. A system that grows in three different ways at once is a system that will be replaced by something simpler.*

The extension domain in SAP is *two separate plugin systems sharing a name and not an interface*: **Skills** (markdown-procedural-memory installed from GitHub or zip) and **Extensions** (Node.js apps that run in their own subprocess and present a window). They are good ideas, separately. They are not unified.

---

## 1. The Subject Itself

**What the domain owns:** two parallel extension surfaces — Skills (procedural-memory documents) and Extensions (Node.js subprocess apps). Both install from GitHub or zip. Both have a creator skill in `skills/`. Both register routes in `server.py`. Neither shares code with the other.

**What it does *not* own:**
- The LLM-side knowledge of which skills/extensions are available at any moment (that's still in `server.py`)
- Per-skill / per-extension sandboxing (no sandbox; trust is implicit)
- Inter-extension communication (there is none — extensions are isolated subprocesses)
- A unified manifest format (Skills use SKILL.md YAML frontmatter; Extensions use package.json)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/skills.py` | 681 | Skill install (GitHub / zip), per-project sync, SKILL.md parsing |
| `py/extensions.py` | 631 | Extension install (GitHub / zip), task-status tracking, install/uninstall API |
| `py/node_runner.py` | 123 | Per-extension Node.js subprocess lifecycle, port allocation |
| `py/node_api.py` | 8 | `/api/node/probe` — node presence check |
| `py/uv_api.py` | 9 | `/api/uv/probe` — uv presence check |
| `py/docker_api.py` | 16 | `/api/docker/probe` — docker presence check |
| `skills/skill-creator/` | (manifest + scripts) | The skill that creates skills |
| `skills/sap-extension-creator/` | (manifest + scripts) | The skill that creates extensions |
| `skills/find-skills/` | (manifest) | The skill that discovers skills |
| `skills/officeCLI/` | (manifest) | An office-document-CLI sample skill |

Two domains living in the same `extensions/` folder of the user's data dir, plus a `skills/` folder. No shared base class. No shared manifest schema. Two parallel installations.

---

## 2. How It Works

### 2.1 Skills — procedural memory in markdown

A **Skill** is a directory containing at least a `SKILL.md` file with a YAML frontmatter. The metadata schema (parsed at `py/skills.py:106-233`) is:

- `id` — required, the directory name
- `name` — displayed name
- `description` — what the skill does (max 500 chars, line 349)
- `version` — semver-ish (sanitized at line 304-316)
- `author` — string or list (line 319-329)
- `files` — auto-discovered, top 8 (line 363)

The body of `SKILL.md` is the procedural memory — natural-language instructions for the LLM on when and how to invoke this skill. The skill might include accompanying scripts, data files, or templates. The LLM is taught about the skill via system-prompt injection (logic in `server.py`, not the skill module itself).

**Skill installation paths** (line 390-512):

- **From GitHub URL** (line 464-512): parse URL → discover default branch via GitHub API → download zip → unpack → recurse-discover SKILL.md files → install each. Subpath URLs (`/tree/main/skills/docx`) are supported.
- **From zip upload** (line 572-600): same, minus the GitHub step.
- **Per-project sync** (line 633-664): copy a global skill into `<project>/.agent/skills/<id>/`, or remove, or sync-back to global.

The discovery is *recursive*: `_install_skills_from_directory` (line 392) finds every nested directory containing a SKILL.md and installs them all. This makes the official Anthropic skills repo (which contains many sub-skills) install cleanly with one URL.

**File encoding fallback** at `_read_file_with_encoding` (line 236-265): tries `utf-8`, `utf-8-sig`, `gbk`, `gb2312`, `latin-1`, `cp1252` in order. This is the kind of polish that suggests SAP has been used by humans with non-UTF8 files; the multi-encoding path is small but well-considered.

### 2.2 Extensions — Node.js subprocess apps

An **Extension** is a directory containing a `package.json` and an `index.js` (the entry point). It is installed from GitHub or zip (`py/extensions.py:464-512`). Once installed, `NodeExtension` (`py/node_runner.py:11-100`) manages its lifecycle:

1. **Resolve exec path** (line 21-31): if running inside Electron, use the Electron-as-Node trick (`ELECTRON_RUN_AS_NODE=1`, `electron.exe` as the Node binary, `npm-cli.js` script). If Docker or no Electron context, use system `node` and `npm`. This handles the *packaged-app* case where there is no separate Node installation.
2. **Run `npm install`** (line 51-72) — but only if `node_modules` is missing or older than `package.json` (line 49-51, mtime check).
3. **Pick a port** (line 76): either `package.json.nodePort` or `_free_port()` (line 100-104, OS-assigned).
4. **Spawn the subprocess** (line 78-83): `node index.js <port>`, pipe stdout+stderr, set `NODE_EXTENSION_ID=<ext_id>` env var.
5. **Wait for the port to open** (line 84, `_wait_port`) — health-gates the start.

The extension is now a separate process listening on its own port. The Electron UI can open a window pointing at `http://localhost:<port>/` to render the extension's UI.

**Multi-instance support** is implied — `vrmWindows = []` in `main.js:19` is plural, and `start-vrm-window` (line 995) pushes new windows — but the underlying `NodeExtension` is per-extension-id, not per-instance. An extension cannot run as two parallel subprocesses on different ports without code changes.

### 2.3 The install-task tracker

`py/extensions.py:147-157` defines an in-process `install_tasks: Dict[str, Dict[str, Any]]` and `update_task_status(ext_id, status, detail, progress)`. The status (`installing` / `success` / `error` / `unknown`) is queryable via `/api/extensions/install-status/{ext_id}`. This is a real progress surface — the user can poll while a slow `npm install` runs.

The comment at line 147 notes "生产环境建议用 Redis" (production should use Redis) — accurate. The in-process dict won't survive a process restart; mid-install crashes leave the tracker uninformed.

### 2.4 The Windows-readonly dance

`py/extensions.py:58-91` (`_remove_readonly`, `robust_rmtree`, `make_tree_writable`) handles Windows file permissions during install/uninstall. Some npm packages install with read-only flags; `shutil.rmtree` then fails. SAP handles it: on Windows, recursively chmod-write before delete; use the `onerror` (or `onexc` for newer Python) callback to override read-only when encountered. Three helper functions, ~30 lines, fixes a real bug.

### 2.5 The probe trio

`py/node_api.py`, `py/uv_api.py`, `py/docker_api.py` are each *one route*: `/api/{node,uv,docker}/probe` returning `{installed: bool, path: ...}` based on `shutil.which`. These are the readiness checks the Electron UI hits to know what to gray out in the install panel.

The three files are tiny, parallel, and reused-via-symmetry. They are also a candidate for unification: one `/api/probe/{tool}` route with a configured allow-list.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Two plugin surfaces, no unified manifest

A Skill has `SKILL.md` with YAML frontmatter. An Extension has `package.json`. The two cannot be cross-referenced; an extension cannot bundle a skill; a skill cannot depend on an extension. This was probably an organic split (Skills came from the Anthropic-skills repo influence; Extensions came from the desire to ship custom UI), but the architectural cost is real.

### 3.2 No sandbox boundary

Both surfaces are trusted. A Skill's procedural memory is injected into the LLM system prompt — a malicious skill can prompt-inject. An Extension is a Node.js subprocess with full filesystem and network access — a malicious extension is a malicious local process. There is no signing. There is no permission manifest. There is no capability declaration.

### 3.3 Extension multi-instance is implicit

`vrmWindows` is plural; `NodeExtension` is singular. Want two parallel extensions? Install a copy under a different id. The architecture does not contemplate "the same extension running twice with different config."

### 3.4 npm install is online-required

`py/node_runner.py:53-70` invokes `npm install` synchronously at extension start (if `node_modules` is stale). No offline mode; no vendored fallback. An extension first-launch with no network silently hangs at the subprocess `communicate()` call until the npm timeout, then surfaces the error.

### 3.5 The encoding-tolerance is asymmetric

Skills' YAML frontmatter parsing tries six encodings (`py/skills.py:247`). Extensions' `package.json` reading uses Python default UTF-8 (`py/node_runner.py:20`). A non-UTF8 package.json crashes silently at the `json.loads` step.

### 3.6 The crisp parts

- The **YAML frontmatter pattern** (lines 178-209) — the SKILL.md convention is the right shape for procedural-memory documents.
- The **Electron-as-Node trick** in `py/node_runner.py:21-31`. Genuinely clever — uses the Electron binary as a Node interpreter via the documented `ELECTRON_RUN_AS_NODE` env flag, eliminating the need to ship a separate Node runtime.
- The **mtime-based npm install skip** (line 49-51) — `node_modules` is older than `package.json` ⇒ reinstall; else skip.
- The **per-project skill sync** (line 633-664) — global pool + per-project copies, with explicit install/remove/sync-back actions.
- The **multi-encoding file reader** in `py/skills.py:236-265`.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 12
- [[19_TOOL_DOMAIN]] for tools (separate concept from skills/extensions)
- [[20_interface/23_SKILL_INTERFACE]] for the skill protocol contract
- [[20_interface/24_EXTENSION_INTERFACE]] for the extension protocol contract
- [[30_execution/38_EXTENSION_LIFECYCLE]] (Forge) for the install→sandbox→load→unload flow
- [[hermes:HEM-12_SKILLS_PROCEDURAL_MEMORY]] for Hermes's Skills (much more developed)
- [[hermes:HEM-17_PLUGINS_EXTENSIBILITY]] for Hermes's plugin system (also more developed)

---

## What This Means for Ember

**Adopt:**
- **The SKILL.md / YAML-frontmatter pattern** for procedural memory. Ember's Skills (likely named **Verkfæri** — tools/instruments — or **Háttr** — habits/method) use the same format. Cross-compatibility with Anthropic-skills and SAP-skills is a Vow of Open Knowledge benefit.
- **The Electron-as-Node trick** (`py/node_runner.py:21-31`) when Ember packages a desktop app. It removes a whole class of "Node not installed" support issues.
- **mtime-based npm-install skip** as a general pattern: cache invalidation by dependency-file mtime > artifact mtime.
- **The multi-encoding file reader** at `_read_file_with_encoding` — apply to every file-ingest path Ember offers.
- **Per-project sync** of skills (global pool + project copies + sync actions). Ember's Realms have skill scope; project-level overrides are first-class.

**Adapt:**
- **Two parallel plugin systems** — adapt to a **unified extension protocol** with multiple *bodies*. A single manifest schema declares: (1) the *procedural memory* (markdown skills), (2) the *capability scripts* (Python/Node/Bash), (3) the *UI surface* (HTML / Node-served). Skills become a *kind* of extension, not a separate domain.
- The **in-process install-tracker** — adapt to write through Ember's Sögumiðla event bus so install progress is durable across restarts and visible across surfaces.
- The **Windows-readonly dance** — adopt the discipline, but generalize: every Ember filesystem mutation goes through a `safe_rmtree` / `safe_copy` helper with platform-specific handling. The three helper functions become one well-tested module.

**Avoid:**
- **Trusted-by-default plugin loading.** Both SAP's Skills and Extensions are trusted. Ember refuses: every extension declares a capability manifest (filesystem-paths, network-hosts, tool-uses), and the host enforces. An extension that exceeds its declared capabilities is killed and reported.
- **`npm install` at first launch with no offline path.** Ember's extensions vendor their `node_modules` or are explicitly online-required (the user is warned at install).
- **No signed manifest.** Even if Ember does not implement code-signing in v1, the manifest schema includes a `signature` field — present and required by tier (Pi: hash-only; workstation: GPG).
- **Two plugin systems sharing nothing.** One protocol; many bodies.

**Invent:**
- **The Capability Manifest.** Every Ember extension declares — in the manifest, signed — its requested capabilities: `filesystem: [<paths>]`, `network: [<hosts>]`, `tools: [<names>]`, `surfaces: [<names>]`. Funi grants only declared capabilities. Smiðja enforces. A drift between declared and used is an audit event.
- **Skill-as-Verkfæri.** Skills in Ember are first-class *tools* with a YAML frontmatter manifest and a structured body. The tool's *system prompt fragment* is one section; the tool's *Python implementation* is another; the tool's *example invocations* are another. SAP separates these via folder convention; Ember unifies them in one manifest.
- **Extension Realms.** An Ember extension is a Realm with reduced scope — its own Funi subentrypoint, its own Smiðja with capability-gated tools, its own Brunnr connection to a sub-Well. Two extensions cannot communicate except through the parent Realm's Sögumiðla bus. SAP's "subprocess on a port" becomes "Realm with a typed manifest."
- **The Extension Cross-Tier Body.** A heavyweight extension (e.g. a local LLM runner) ships a *Pi-body* (delegates to a remote/peer Ember), a *laptop-body* (small model), and a *workstation-body* (full model). The manifest declares which bodies exist; Funi loads the right one per tier. This is the [[60_synthesis/63_PERFORMANCE_TIER_ENGINE]] integration.
- **The Plugin Verification Pass.** At install, Ember runs an automated check: read manifest → diff against declared capabilities → scan for known-bad patterns (process-spawning, raw-socket, eval-of-user-input) → produce a yellow/red advisory. SAP installs and prays; Ember installs and reports.
