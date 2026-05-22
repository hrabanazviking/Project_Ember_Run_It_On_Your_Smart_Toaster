# 13 — Sandbox Backend Abstraction

OpenClaw's tool-isolation pattern: pluggable sandbox backends
(Docker, SSH, OpenShell). What it provides; what Ember has;
where adoption makes sense.

---

## The pattern

Tools execute potentially-dangerous operations (shell commands,
file edits, web fetches). OpenClaw isolates these via:

1. **Sandbox mode**: a setting that says "all non-main sessions
   run in sandbox."
2. **Sandbox backend**: the *mechanism* of isolation —
   - `docker` (default): containerized process.
   - `ssh`: remote execution to a sandboxed host.
   - `openshell`: their custom sandbox.

Each backend implements the same interface; tools don't know
which is active.

---

## What each backend does

### Docker

- Spin up a container with limited capabilities.
- Mount the operator's workspace read-only or limited-write.
- Execute the tool inside the container.
- Capture stdout/stderr/exit-code.
- Tear down the container.

Pros: strong isolation. Standard.
Cons: heavy (containers take RAM); requires Docker installed.

### SSH

- Connect to a pre-configured sandbox host.
- Execute the tool remotely.
- Capture output.

Pros: can use *any* remote sandbox (cloud VM, dedicated box, Pi).
Cons: requires SSH setup; network-dependent.

### OpenShell

- OpenClaw's custom sandbox.
- Lighter than Docker; uses chroot / namespaces / cgroups?
- Lower overhead.

(Implementation details unclear without deeper repo dive.)

---

## Why pluggable backends matter

Different operators want different trade-offs:

- **Developer laptop with Docker installed**: Docker is fine.
- **Pi cluster with no Docker**: SSH to a sandbox node.
- **Air-gapped machine with no remote**: OpenShell or
  process-level sandbox.
- **High-security**: Docker with very tight restrictions.
- **High-trust personal use**: maybe no sandbox at all (still
  per-call approval as Ember does).

One-size-fits-all sandbox doesn't fit all operators. Pluggable
backends do.

---

## Ember's current sandboxing

Ember currently uses **per-tool, in-process sandboxing**:

- `read_local_file`: path-prefix sandbox (only inside operator-
  configured root).
- `fetch_url`: domain allowlist + robots.txt + IDNA + no
  redirects to private IPs.
- `search_well`: implicitly safe (read-only).

No *process-level* isolation. The tool runs in Ember's process.

This is *fine* for current tools (they're carefully constrained).
It would *not* be fine if we added:
- `run_shell_command` (arbitrary process execution).
- A full browser tool.
- Code execution tools.

For those: process-level isolation becomes necessary.

---

## What Ember should adopt

🟢 **Adapt to Ember Vows.**

When we add high-power tools (V3+):

### Approach: Protocol-based sandbox backends

Define a `Sandbox` protocol:

```python
class Sandbox(Protocol):
    async def execute(
        self,
        command: list[str],
        cwd: Path,
        env: dict[str, str],
        timeout_s: float,
    ) -> SandboxResult:
        """Execute a command inside the sandbox."""
        ...
    
    async def health(self) -> SandboxHealth:
        """Is the sandbox healthy and ready?"""
        ...
```

Implementations:

1. **`NoSandbox`** — passthrough. Current default for trusted tools.
2. **`DockerSandbox`** — containerized.
3. **`SubprocessSandbox`** — subprocess with cgroups (Linux only).
4. **`SSHSandbox`** — execute on a remote host.

Each tool can declare its preferred sandbox:

```python
@register_tool(
    name="run_shell_command",
    sandbox_required=True,
    sandbox_preference=["docker", "subprocess", "ssh"],
    approval=Approval.PER_CALL,
)
def run_shell_command(cmd: str) -> str:
    ...
```

The runtime picks the first available backend.

### Approach: pip-extras for backend dependencies

- `pip install ember-agent[sandbox-docker]` → enables Docker backend.
- `pip install ember-agent[sandbox-subprocess]` → enables Linux cgroups.
- `pip install ember-agent[sandbox-ssh]` → enables SSH.

Default install ships only `NoSandbox`. Operators opt in.

---

## What about Pi-class

Docker is heavy. Pi-class operators may not want it.

For Pi-class:
- Use `SubprocessSandbox` (light) or `NoSandbox` (trust the tools
  + per-call approval).
- High-power tools (shell, browser) simply *not available* on
  TINY profile.
- Operators wanting more capability: federate to a LARGE node
  via Yggdrasil Phase 4.

---

## Configuration shape

```yaml
ember:
  sandbox:
    default_backend: subprocess     # for trusted tools
    backends:
      docker:
        enabled: false              # opt-in
        image: ember-sandbox:latest
        memory_limit: 512m
        cpu_limit: 1.0
      subprocess:
        enabled: true                # Linux default
        cgroup_v2: true
        memory_limit_mb: 512
      ssh:
        enabled: false
        host: sandbox.tailnet
        user: ember-sandbox
        key_file: ~/.ssh/ember_sandbox
    tools_requiring_sandbox:
      - run_shell_command
      - python_eval
      - browser_render
```

---

## What this enables

When sandbox backends exist:

- Operators can confidently enable powerful tools.
- The Heimdall Pattern (cross-realm gate) can enforce sandbox
  for every dangerous call.
- Audit log shows which backend executed which tool.
- Phase 4 federation: operators can route tool execution to a
  *trusted* node in their tailnet, while session lives on a
  lighter device.

This is significant capability expansion *with* safety.

---

## What we don't promise

🔴 **Reject** — these are NOT the goal:

### 1. Perfect sandbox isolation

Sandboxes are *defense in depth*. They reduce attack surface;
they don't eliminate it. A determined attacker with code
execution inside a Docker container can sometimes escape.

We're honest: sandbox = better isolation; not perfect isolation.

### 2. Cloud-managed sandboxes

OpenClaw mentions Fly.io / Render configs (which could host
sandboxes). Ember doesn't ship those. Sandbox stays operator-
managed.

### 3. Multi-tenant sandboxes

If multiple operators share the system (rare in our cohort),
they each get their own sandbox. No multi-tenant sandbox sharing.

---

## Integration with existing tool framework

Ember's tool framework (per `src/ember/tools/`) already has:
- Per-tool approval (PER_CALL / STANDING / FORBIDDEN).
- Per-tool sandbox config (path restrictions, etc.).
- Audit log.

Adding *sandbox backends* slots in cleanly:

```python
async def execute_tool(call: ToolCall, sandbox: Sandbox) -> ToolReply:
    # ... approval flow ...
    if approved:
        result = await sandbox.execute(...)
        log_audit(...)
        return result
```

The sandbox is *another layer* between approval and execution.

---

## Lessons from OpenClaw's choices

### Docker as default

OpenClaw defaults to Docker because their operator cohort
(web devs + power users) typically has Docker.

Ember's cohort (more diverse, more Pi-class) defaults to
no-sandbox + per-call-approval. Docker is opt-in.

### Backend swapping

OpenClaw lets operators swap backends. Ember should too.
Per-tool-type or system-wide.

### Sandbox is not just for tools

OpenClaw's `non-main` mode sandboxes *whole sessions*. If a
session is from an external channel (Telegram), maybe its
*entire* tool set runs in sandbox.

Ember could mirror this for bridges (V4+): channel-bridged
sessions sandbox all tools.

---

## Risk of over-engineering

🟡 **Defer most of this** until we add high-power tools.

The current Ember tools (read/fetch/search) don't *need* sandbox
backends. Per-call approval + per-tool sandboxes is sufficient.

We design the abstraction now; we implement when needed (V3+).

---

## Closing

Sandbox Backend Abstraction is **OpenClaw's pattern for safely
expanding tool capability**. Multiple isolation mechanisms;
operator chooses; runtime swaps.

Ember should:
1. Define the Sandbox Protocol (cheap; design-only for now).
2. Implement when first high-power tool lands (V3).
3. Default to no-sandbox + per-call-approval for low-power tools.
4. Offer Docker / Subprocess / SSH backends as pip extras.

The pattern unlocks future capability without requiring it
*now*. That's good architecture: ready for what's next; not
over-built for what isn't.
