# 37 — Plugin Sandboxing: In-Process, Subprocess, WASM via wasmtime

**Category:** Safety, Trust, Sandboxing
**Runa relevance:** `src/runa/plugins/` (ADR-0002 §D-2.5 — Runa supports all 4 modes), policy enforcement
**Status:** Research synthesis. Anchors the four-mode plugin design.
**Last touched:** 2026-05-17

---

## 1. Core idea

Per ADR-0002 §D-2.5, Runa's plugin system supports **four isolation models, operator-config-selected per plugin**: in-process trusted, in-process lightweight, out-of-process subprocess, and WebAssembly sandbox via wasmtime. Each represents a different point in the trust-vs-performance-vs-engineering-cost trade-off space. A trusted first-party plugin runs in-process for speed; an untrusted third-party plugin runs in WASM with capability constraints; an experimental plugin runs out-of-process so a crash is recoverable; a prototype runs in-process-lightweight with minimal contract checks.

This document covers the four modes, the actual mechanisms (capabilities, namespaces, WASM sandboxes), and the production engineering of each. The space is well-trodden in operating-system and browser-security research; agent-system plugin loading is the latest place these ideas converge.

## 2. Technical depth

**The four isolation modes:**

### Mode A — In-process trusted

The plugin is a Python class loaded into Runa's process. It can do anything Runa can do — full filesystem, full network, full memory.

- **When appropriate:** plugins authored by Volmarr or trusted contributors.
- **Mechanism:** standard Python imports.
- **Cost:** zero overhead.
- **Risk:** a buggy plugin can crash Runa, corrupt state, exfiltrate secrets.

### Mode B — In-process lightweight

Same as Mode A but with *contract enforcement* — the plugin's declared capability requirements are checked by the policy engine before each call, output is shape-validated.

- **When appropriate:** plugins by less-trusted contributors but where speed matters.
- **Mechanism:** Python import + plugin contract base class + decorator-based capability enforcement.
- **Cost:** small (microseconds per call).
- **Risk:** Python's introspection escapes anything Pure-Python tries to prevent. Genuine isolation requires Mode C or D.

### Mode C — Out-of-process subprocess

The plugin runs in its own Python subprocess; Runa communicates with it via JSON-RPC over stdin/stdout or a Unix socket. The subprocess can be launched with reduced privileges (`os.setuid`, namespaces on Linux, `chroot`, `seccomp`-bpf filters).

- **When appropriate:** third-party plugins where a crash should not affect Runa; cases needing privilege reduction.
- **Mechanism:** `subprocess.Popen` + structured RPC + process-level isolation features.
- **Cost:** ~1ms per call for IPC; subprocess startup overhead (~100ms+).
- **Risk:** isolation depends on the subprocess setup. Lazy implementation defaults to "subprocess with full user permissions" — better than in-process for crash isolation, no better for malicious code.

### Mode D — WebAssembly sandbox via wasmtime

The plugin is compiled to WebAssembly and run inside a WASM runtime (wasmtime, wasmer). The runtime mediates all access to the outside world via *host functions* — the plugin can only call functions the host exposes. By default, the plugin has zero filesystem, network, or system access.

- **When appropriate:** untrusted third-party plugins; high-security deployments; sharing plugins across machines.
- **Mechanism:** plugin compiled to WASI Preview 1 or 2; wasmtime executes; host exposes a narrow Runa-specific API.
- **Cost:** ~10-100× call overhead vs in-process; substantial complexity to author plugins (must compile to WASM, restricted language choices).
- **Risk:** strongest available sandbox in 2025-2026. Known escapes are rare and quickly patched.

**The mechanisms in detail:**

**OS-level isolation (for subprocess mode):**

- **User separation.** Run as a different OS user. Filesystem ACLs do the rest.
- **chroot.** Restrict the visible filesystem to a directory.
- **Linux namespaces** (PID, mount, network, IPC, user, UTS). The Docker/podman foundation.
- **seccomp-bpf.** Filter the system calls a process is allowed to make. Strong, low-overhead.
- **AppArmor / SELinux.** Mandatory-access-control layers on top.
- **cgroups.** Resource limits (CPU, memory, file descriptors).

**WebAssembly + WASI:**

- **WebAssembly (Wasm)** — a portable binary instruction format. Originally for browsers; now widely used server-side.
- **WASI (WebAssembly System Interface)** — POSIX-like interface for Wasm programs. Files, sockets, env vars. **Capability-based**: a Wasm program can only access the file descriptors / capabilities the host explicitly gives it.
- **Component Model** (WASI Preview 2). Higher-level abstraction with typed interfaces between Wasm components. Stable as of 2024.
- **wasmtime** (Bytecode Alliance, primarily Mozilla / Fastly contributors). Production-grade WASI runtime in Rust.
- **wasmer** — alternative runtime, more features for cloud-native use.

**Capability-based security (foundational pattern):**

- A capability is an *unforgeable reference* to a resource. If you have it, you can use the resource. If you don't, you can't even refer to it.
- Examples: a file descriptor on Unix is a capability. A WASI file handle is a capability.
- Contrast with permission-based security: "can user X open file Y?" requires a global policy decision. Capability-based: "do you have a handle? then yes."
- WASM with WASI is the modern mainstream implementation of capability-based security. Strong theoretical foundations (1960s+, Levy, Hardy).

**Plugin contract design:**

The plugin contract should be *the same* across all four modes. Plugin authors write to one interface; operators choose isolation at deploy time. Mode A and B import the class directly; Mode C runs the class in a subprocess via a thin wrapper; Mode D runs a WASM-compiled version of the same logic via WASI Component Model bindings.

This contract-first design is the key engineering investment. Cost: harder upfront. Benefit: plugin authors are not forced to know about isolation; operators get the choice.

## 3. Key works

- **Adams, S. "Plugin Sandboxing Patterns."** No single canonical reference; this material is scattered across OS security, language runtimes, and modern Wasm literature.
- **Levy, H. *Capability-Based Computer Systems.*** Digital Press, 1984. The classical reference for capability-based security.
- **Hardy, N. "KeyKOS Architecture."** ACM SIGOPS, 1985. Capability-based OS.
- **Haas et al. "Bringing the Web up to Speed with WebAssembly."** PLDI 2017. The Wasm paper.
- **Bytecode Alliance** — bytecodealliance.org. Stewards of wasmtime and the Wasm ecosystem.
- **wasmtime documentation** — docs.wasmtime.dev.
- **The WASI Subgroup specifications** — github.com/WebAssembly/WASI.
- **Justine Tunney's APE / Cosmopolitan Libc / llamafile** — adjacent territory; portable native rather than WASM.
- **OpenAI Plugins / ChatGPT Plugins** (2023-2024, since deprecated) — early industry plugin-architecture experiment with mixed results.
- **MCP (Model Context Protocol)** — Anthropic, 2024 — a newer entry in the agent-plugin-protocol space. Not strictly a sandboxing standard but relevant to plugin architecture.

## 4. Empirical results

- **WASM startup time:** wasmtime can instantiate a Wasm module in ~1-10ms; subprocess Python startup is ~100-500ms. WASM wins decisively on warm-up.
- **WASM call overhead:** ~10-100x over native function call within the same process. For computationally-heavy plugins, the overhead is negligible; for high-frequency tiny calls, it dominates.
- **Sandbox escape history:** seccomp-bpf escapes occasionally found (kernel bugs); WASM escapes very rare (the runtime is the smaller, more-audited surface). Capability-based design is structurally harder to escape than permission-based.
- **Production plugin systems:** VS Code's extension model (in-process trusted, with effort), browser extensions (subprocess + namespace), Roblox (per-game Lua sandboxes), Figma (WASM for compute plugins). All have war stories.
- **Authoring difficulty:** Mode A is "write a Python class." Mode D requires Rust / C / AssemblyScript / TinyGo / etc., and disciplined awareness of WASI's restrictions. Steep author learning curve.

## 5. Applicability to Runa

Per ADR-0002 §D-2.5, **Runa supports all four modes** with operator-config selection.

For **`src/runa/plugins/` design**:

```
src/runa/plugins/
├── contract.py           ─ the base class plugins implement
├── manifest.py           ─ plugin manifest schema (id, permissions, isolation_mode)
├── loader.py             ─ dispatcher: picks the right strategy
├── strategies/
│   ├── inproc_trusted.py
│   ├── inproc_lightweight.py
│   ├── subprocess.py
│   └── wasm_wasmtime.py
└── sandbox.py            ─ shared capability-checking utilities
```

**Plugin contract:**

```python
class RunaPlugin(ABC):
    plugin_id: str
    version: str
    capabilities_required: list[Capability]  # declarative
    
    @abstractmethod
    def initialize(self, host: PluginHost) -> None: ...
    
    @abstractmethod
    def call(self, method: str, args: dict) -> dict: ...
    
    @abstractmethod
    def shutdown(self) -> None: ...
```

`PluginHost` is the narrow Runa API the plugin can call: send-event, log, request-tool. No raw filesystem / network — the plugin asks the host for a capability and gets it (or not).

**Default isolation modes per source:**
- First-party plugin authored by Volmarr → in-process trusted.
- Plugin from a verified contributor → in-process lightweight.
- Untrusted / external plugin → out-of-process subprocess by default; WASM if WASM compilation is available.
- Operator can override per-plugin.

**For WASM mode specifically:**

- Use wasmtime-py (Python bindings for wasmtime).
- Define a WASI Component Model interface for `PluginHost`.
- Provide a Rust template plugin and an AssemblyScript template (the two most-practical WASM authoring languages).
- Document the restrictions: no arbitrary Python libs.

For **deploy/pi/**:

- WASM mode on Pi 5: wasmtime-py runs but is heavier than native. Test before committing.

What to avoid:

- Don't write code that depends on a specific isolation mode at the plugin layer. Mode is the *host's* concern.
- Don't grant capabilities globally. Each plugin gets explicitly-listed capabilities at install time.
- Don't trust the plugin's self-declared capabilities. The host enforces; the declaration is metadata for the operator to read.
- Don't ship Mode A as the default for third-party plugins. Mode C should be the default minimum for non-first-party.

## 6. Open questions

- **Cross-mode tooling parity.** Can the same plugin work identically in all four modes without authors writing four versions? Tooling investment.
- **Capability granularity.** Coarse capabilities (`READ_FILES`) are easy to author but permissive. Fine capabilities (`READ_FILES_IN_PATH("/runa/data")`) are safer but burdensome. Right level is a design question.
- **Plugin discovery and signing.** How does Runa know a plugin is what it claims? Signature checks, reputable plugin registries — mature in browser ecosystems, immature in agent ecosystems.
- **WASI Component Model adoption.** As of late 2025, Component Model is stable but tooling is still maturing. Production WASM agents are rare.

## 7. References (curated)

- bytecodealliance.org — wasmtime stewardship.
- docs.wasmtime.dev — wasmtime docs.
- github.com/WebAssembly/component-model — Component Model spec.
- arXiv preprint PLDI 2017 — original Wasm paper.
- github.com/bytecodealliance/wasmtime-py — Python bindings.
- Levy, *Capability-Based Computer Systems*, 1984.
- modelcontextprotocol.io — MCP spec (adjacent territory).
- Anchored decision: ADR-0002 §D-2.5.
- Companion docs: [[14-constitutional-ai]] (policy stack), [[40-audit-logging-replay]] (the audit half).
