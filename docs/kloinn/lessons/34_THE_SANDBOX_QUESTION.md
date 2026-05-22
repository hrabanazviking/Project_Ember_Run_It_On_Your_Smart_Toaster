# 34 — The Sandbox Question

Different projects answer "how do we keep tool execution safe?"
differently. OpenClaw uses process isolation; Ember uses per-call
approval. Why; what we should consider; the deeper question.

---

## The two main approaches

### Approach 1: process isolation (OpenClaw's default)

Tools run in a sandbox (Docker container, subprocess with
cgroups, SSH-to-sandbox-host). Whatever the tool does inside
the sandbox *cannot* escape to the host.

If the tool tries `rm -rf /`, only the sandbox's filesystem dies.
Host is safe.

### Approach 2: per-call approval (Ember's default)

Tools run in the same process. But every potentially-dangerous
operation requires *operator approval at runtime*:

"Tool `read_local_file` wants to read `/home/operator/diary.md`.
Approve? (y/n)"

The operator decides every potentially-dangerous call.

### Both have merits

Process isolation:
- ✅ Catches misuse the operator doesn't anticipate.
- ✅ Defends against malicious tools.
- ❌ Adds overhead (Docker takes RAM).
- ❌ Operator may not understand what's happening inside.

Per-call approval:
- ✅ Operator sees + chooses every action.
- ✅ Lightweight (no container).
- ❌ Approval fatigue (too many prompts).
- ❌ Operator may approve without reading.

Different operators, different trust models.

---

## What Ember currently does

Ember's tool framework (per `src/ember/tools/`):

- **PER_CALL approval** default for risky tools.
- **Path sandboxing** for `read_local_file` (path-prefix limit).
- **Domain allowlisting + robots.txt** for `fetch_url`.
- **STANDING approval** for low-risk tools (`search_well`).
- **FORBIDDEN** for tools the operator opts to disable entirely.

No process-level isolation. Tools run in-process.

This is *fine* for our three current tools:
- `search_well`: pure read; no side effects.
- `read_local_file`: read-only with sandbox.
- `fetch_url`: read-only network with restrictions.

For *those* tools, process isolation would be overkill.

---

## When process isolation becomes necessary

When tools include:
- Arbitrary shell execution.
- Writing arbitrary files.
- Running operator-installed code.
- Executing untrusted scripts.

…the in-process approach reaches its limits. A malicious tool
in the same process as Ember can do *anything Ember can do*:

- Read other tool's data.
- Modify Ember's state.
- Send data over the network.
- Tamper with the audit log.

For high-power tools: **process isolation is necessary**, not
optional.

---

## The trust model question

The core question:

**"Whom do we trust?"**

### Option A: trust the operator + trust the tools

If both are trusted, per-call approval is sufficient. The
operator reviews each call; trustworthy tools do what they say.

This is Ember's current model. Works for: small, audited, in-
core tool sets.

### Option B: trust the operator, distrust the tools

If tools might be malicious (e.g., from a centralized registry
or community), process isolation is necessary. The operator
can't review every tool's internals; sandboxing is the safety
net.

This is OpenClaw's model. Works for: large tool ecosystems
with community contributions.

### Option C: distrust both

Sandbox AND per-call approval. Most secure; most friction.

Use case: high-security environments (legal compliance,
sensitive data).

### Option D: trust everything

No sandbox, no approval. Highest velocity, highest risk.

Most consumer AI assistants implicitly do this (you trust the
vendor; they trust their tools).

Sovereign AI projects should avoid Option D except for specific
trusted contexts.

---

## What Ember should do

🟢 **Adapt to Ember Vows**: keep current approach for *core
tools*; add process isolation for *high-power tools*.

### Phase 1-2: stay with per-call approval for current tools

Our three tools are safe in-process. Don't add Docker for them.

### Phase 3: introduce sandbox for high-power tools

When we add `run_shell_command`, `python_eval`,
`browser_render`, etc., they require process isolation.

Implement sandbox backends per
[`../patterns/13_SANDBOX_BACKEND_ABSTRACTION.md`](../patterns/13_SANDBOX_BACKEND_ABSTRACTION.md).

### Phase 4: per-bridge sandboxing

When bridges land, channel-bridged sessions sandbox by default.
(Operator can't see every prompt that arrives over a channel;
sandbox protects.)

### Phase 5: per-session sandbox config

`/new --sandbox=strict` for high-security sessions.

---

## Why per-call approval first

The Vow of Smallness applies: don't add complexity until needed.

In Phase 1-2 with three tools, per-call approval is *sufficient*.
Adding Docker for our current tools would be over-engineering.

When tools warrant isolation, we add it. Not before.

---

## The OpenClaw-default-sandbox question

OpenClaw's default for non-main sessions: sandbox-enabled. The
operator opts *out* if they want.

Should Ember mirror this?

🟡 **Defer.**

Reasons:
- Our tools don't warrant it yet.
- Pi-class operators don't want Docker overhead.
- Per-call approval is *understandable* by operators; sandboxing
  is less so.

When we have high-power tools, we'll revisit.

For LARGE+ profile operators wanting sandbox-by-default: a
config switch (`sandbox.default_for_all_tools: true`) is fine.

For TINY+ profile operators: per-call approval stays default.

---

## The approval-fatigue problem

Operators get tired of approving every call. If we ask for
approval on every `fetch_url`, they'll start auto-approving
without reading.

Mitigations Ember already uses:
- **STANDING approval** for low-risk tools.
- **Operator-configured `approval_overrides`**: per-tool
  preferences.
- **Per-domain rules**: github.com always approved; facebook.com
  always denied.
- **The Mirror of Ginnungagap** (per Yggdrasil): suggests
  elevating frequently-approved patterns to STANDING.

The lesson: approval should be *focused* on *unusual* calls,
not routine ones.

---

## What about cloud-managed sandboxes

OpenClaw's `ssh` sandbox backend can connect to a *remote*
sandbox host (cloud VM, dedicated box, etc.).

For Ember: stay tailnet-only.
- Remote sandbox host is fine if on operator's tailnet.
- Public-internet sandbox host is NOT (sovereignty).

This is just a configuration discipline.

---

## What about Webassembly sandboxes

A modern alternative: WASM-based sandbox. Run tools as WASM
modules; the WASM runtime enforces capability limits.

Pros: very lightweight; cross-platform.
Cons: tools must be WASM-compatible (most aren't).

For Ember V5+, consider WASM for *specific* tool types (math
evaluation, code linting, etc.). Not as default sandbox for
arbitrary tools.

---

## The "soft sandbox" middle ground

Between "fully isolated subprocess" and "in-process", there's:

**Soft sandbox** — tool runs in-process but with:
- Restricted file-system view (chroot-like, hard in Python).
- Restricted environment variables.
- Restricted network access (firewall rules per-call).
- Time/memory limits.

Some of this Ember already does (path sandboxing for
`read_local_file`, robots.txt for `fetch_url`).

For high-power tools, add:
- `resource` module limits (CPU time, memory).
- Network namespace if available (Linux).
- File descriptor limits.

This is *cheaper than full Docker* and *better than nothing*.
Worth considering for Phase 3.

---

## Configuration shape (full)

```yaml
ember:
  tools:
    approval:
      default: per_call           # or "standing" / "forbidden"
      overrides:
        search_well: standing
        fetch_url:
          per_domain:
            github.com: standing
            facebook.com: forbidden
    
    sandbox:
      default_backend: none       # or "subprocess" / "docker" / "ssh"
      per_tool_overrides:
        run_shell_command:
          backend: docker
        python_eval:
          backend: subprocess
      
      resource_limits:
        max_cpu_seconds: 30
        max_memory_mb: 200
        max_output_bytes: 5_000_000
```

---

## The deeper question

The Sandbox Question is part of a bigger question:

**"How does an AI assistant handle the operator's trust
contract?"**

OpenClaw says: "I'll sandbox by default; you opt out."
Ember says: "I'll ask you each time; you opt in to standing
trust."

Both are *trying to protect the operator*. Both prioritize
operator-safety.

The differences are *cohort-shaped*:
- OpenClaw operators expect some friction-reduction; sandbox
  default trades safety for convenience.
- Ember operators expect explicit choice; per-call default
  trades convenience for safety.

Neither is wrong. They serve different operators.

---

## Closing

The Sandbox Question is **a real engineering + philosophy
question**. Process isolation vs per-call approval are both
valid; the right answer depends on cohort + tools.

Ember's path:
- Phase 1-2: per-call approval continues.
- Phase 3: introduce sandbox backends as tools warrant.
- Phase 4: per-bridge sandbox defaults.
- Phase 5: per-session sandbox config.

We borrow OpenClaw's *abstraction* (sandbox backends) without
borrowing their *default* (sandbox-on-by-default for non-main).
Each operator picks.

The deeper lesson: **safety is a contract with the operator,
not a one-size-fits-all setting**. Build the abstractions;
let operators choose.
