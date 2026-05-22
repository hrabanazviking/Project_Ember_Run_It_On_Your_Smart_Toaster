# 43 — Sandboxing Layer for Tools

How specifically to add process-level sandboxing to Ember's
tool framework. Concrete Phase 3 plan.

---

## When this lands

🟢 **Phase 3 of Klóinn adoption** — when first high-power
tool is added.

Trigger: a tool that needs process isolation (e.g.,
`run_shell_command`, `python_eval`, `browser_render`).

Before that: current per-call approval suffices.

---

## The Sandbox Protocol

Define in `src/ember/sandbox/protocol.py`:

```python
from typing import Protocol, ClassVar
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    cpu_seconds: float
    peak_memory_mb: int

class Sandbox(Protocol):
    BACKEND_KIND: ClassVar[str]
    
    async def execute(
        self,
        command: list[str],
        cwd: Path,
        env: dict[str, str],
        timeout_s: float = 30.0,
        max_memory_mb: int = 200,
        max_output_bytes: int = 5_000_000,
    ) -> SandboxResult:
        """Execute a command in the sandbox."""
        ...
    
    async def health(self) -> SandboxHealth:
        """Is the backend ready?"""
        ...
```

Implementations live in `src/ember/sandbox/backends/`:
- `none.py` — passthrough (current behavior; for trusted
  tools).
- `subprocess.py` — Python subprocess with `resource` limits.
- `docker.py` — Docker container per call.
- `ssh.py` — Remote execution.

---

## Backend: NoSandbox (default for low-power)

```python
class NoSandbox:
    BACKEND_KIND = "none"
    
    async def execute(self, command, cwd, env, timeout_s, ...):
        # ... straight asyncio subprocess ...
```

This is *the current behavior* for tools like `search_well`,
`read_local_file`, `fetch_url`. They're safe in-process; we
preserve that.

---

## Backend: SubprocessSandbox (Linux primary)

Lightweight, Linux-only. Uses Python's `resource` module + `subprocess`:

```python
class SubprocessSandbox:
    BACKEND_KIND = "subprocess"
    
    async def execute(self, command, cwd, env, timeout_s, ...):
        def preexec():
            # Linux only
            import resource
            resource.setrlimit(resource.RLIMIT_CPU, (timeout_s, timeout_s))
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_output_bytes,) * 2)
            os.nice(10)
        
        proc = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=preexec,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout_s + 5,  # buffer
            )
            return SandboxResult(...)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return SandboxResult(..., timed_out=True)
```

Provides:
- CPU time limit.
- Memory limit.
- Output size limit.
- Lower priority (nice +10).

Limitations:
- Linux only (resource module).
- Limited filesystem isolation (process can read most files).
- Network not restricted.

Good for *modest* sandboxing. Better than nothing.

---

## Backend: DockerSandbox (full isolation)

```python
class DockerSandbox:
    BACKEND_KIND = "docker"
    
    IMAGE = "ember-sandbox:latest"
    
    async def execute(self, command, cwd, env, timeout_s, ...):
        # Use docker CLI via subprocess
        docker_cmd = [
            "docker", "run",
            "--rm",
            "--memory", f"{max_memory_mb}m",
            "--cpus", "1",
            "--network", "none",  # no network by default
            "-v", f"{cwd}:/workspace:ro",
            "-w", "/workspace",
            self.IMAGE,
            "timeout", str(timeout_s),
        ] + command
        
        # ... run via asyncio subprocess ...
```

Provides:
- Strong filesystem isolation.
- Network isolation (--network none).
- Memory limits enforced by kernel.
- Independent of host OS state.

Requires: Docker installed on host. Not Pi-class friendly.

---

## Backend: SSHSandbox (remote execution)

```python
class SSHSandbox:
    BACKEND_KIND = "ssh"
    
    HOST = "sandbox.tailnet"
    USER = "ember-sandbox"
    KEY_FILE = "~/.ssh/ember_sandbox"
    
    async def execute(self, command, cwd, env, timeout_s, ...):
        ssh_cmd = [
            "ssh",
            "-i", self.KEY_FILE,
            "-o", "StrictHostKeyChecking=yes",
            f"{self.USER}@{self.HOST}",
            "timeout", str(timeout_s),
        ] + command
        # ... run via asyncio subprocess ...
```

Useful when:
- Operator has a sandbox VM/Pi on tailnet.
- They want full OS isolation.
- The sandbox host can be restored to known state.

---

## Tool integration

Each tool declares its sandbox requirement:

```python
@register_tool(
    name="run_shell_command",
    approval=Approval.PER_CALL,
    sandbox_required=True,
    sandbox_preference=["docker", "subprocess", "ssh"],
)
def run_shell_command(cmd: str) -> str:
    """Run a shell command; output captured."""
    # Implementation routes through sandbox
    ...
```

The runtime picks the first available backend from
`sandbox_preference`. If none available + `sandbox_required:
True`: tool reports "no sandbox backend available; install
ember-agent[sandbox-docker] or similar."

---

## Configuration shape

```yaml
ember:
  sandbox:
    enabled: true
    
    default_backend: subprocess   # or "none" / "docker" / "ssh"
    
    per_tool_backend:
      run_shell_command: docker
      python_eval: docker
      browser_render: docker
    
    backends:
      subprocess:
        enabled: true              # Linux default
      docker:
        enabled: false             # opt-in (requires Docker)
        image: ember-sandbox:latest
        network: none
        memory_limit_mb: 256
      ssh:
        enabled: false             # opt-in
        host: sandbox.tailnet
        user: ember-sandbox
        key_file: ~/.ssh/ember_sandbox
    
    defaults:
      timeout_s: 30
      max_memory_mb: 256
      max_output_bytes: 5_000_000
```

---

## Pip extras

```bash
pip install ember-agent[sandbox-subprocess]  # Linux (no extra deps actually)
pip install ember-agent[sandbox-docker]      # docker CLI required
pip install ember-agent[sandbox-ssh]         # ssh client + paramiko
```

Most operators get `sandbox-subprocess` for free (Linux). Docker
and SSH are opt-in for those who want them.

---

## Audit + observability

Every sandbox execution is logged:

```python
{
  "operation": "sandbox_execute",
  "backend": "docker",
  "tool": "run_shell_command",
  "command": ["sh", "-c", "ls /etc"],
  "duration_s": 0.45,
  "exit_code": 0,
  "stdout_bytes": 1245,
  "stderr_bytes": 0,
  "timed_out": false,
  "peak_memory_mb": 12
}
```

Operator can review which tools used which backends, how
much resource they consumed.

---

## Sandbox health checks

The Doctor screen + gossip protocol show sandbox state:

```
Sandbox Backends:
  subprocess:  ✓ ok  (Linux cgroups available)
  docker:      ✗ unavailable  (Docker daemon not running)
  ssh:         ✗ unavailable  (sandbox.tailnet unreachable)

Tools requiring sandbox: run_shell_command (would use subprocess)
```

Operator can fix the failed backend or accept the degradation.

---

## Failure modes

### Sandbox backend crashes mid-execution

Result: typed `SandboxResult(exit_code=-1, ..., crashed=True)`.
Tool reports failure; operator sees in audit log.

### Sandbox exceeds timeout

Result: `timed_out=True`. Process killed. Partial output
preserved.

### Sandbox can't acquire resources

E.g., Docker daemon at memory limit. Result: typed error;
operator can adjust limits or use lighter backend.

### Network sandbox loses connection (SSH)

Result: `unavailable`. Tool fails; reconnection on next call.

---

## What about non-deterministic results

A tool run in different sandboxes might produce different
results (e.g., different Python version inside container).

This is *the operator's setup*. If operator has Docker
configured to use Python 3.11 and host has 3.14, that's the
operator's choice. We document this constraint.

---

## Performance considerations

| Backend | Per-call latency |
|---|---|
| none | <1ms |
| subprocess | ~10-50ms (fork + exec) |
| docker | ~500-2000ms (container startup) |
| ssh | ~100-500ms (handshake + exec) |

Docker is *slow* for short tools. Use it for *high-risk* tools
where the safety justifies the latency.

For frequent tools: subprocess is the right balance.

---

## What about future sandbox backends

V5+ candidates:
- **WASM sandbox** — Pyodide / Wasmer for very lightweight
  isolation.
- **gVisor** — sandboxed kernel for stronger isolation than
  containers.
- **Hyperisolated VMs** — Firecracker for max security.

Each could plug in as a new backend implementing the Protocol.

---

## Risk + mitigations

| Risk | Mitigation |
|---|---|
| Sandbox escape | Multi-layer: approval + sandbox + audit |
| Backend misconfigured | Health check + clear error messages |
| Slow tool because of sandbox overhead | Per-tool backend selection |
| Operator confused which backend used | Audit log shows it; Doctor screen too |
| Sandbox + tool dependency mismatch | Document; pin versions in tools |

---

## Closing

Sandboxing Layer for Tools is **Phase 3 work**. Add when first
high-power tool warrants it.

Components:
- Sandbox Protocol.
- 4 backends (none, subprocess, docker, ssh).
- Tool framework integration.
- Configuration + audit.
- Pip extras for optional backends.

This *unlocks* future high-power tools while maintaining
operator safety. Without sandbox: high-power tools too risky.
With sandbox: justifiable + auditable.

The Klóinn lesson translates: **borrow OpenClaw's abstraction;
default to lighter; let operator escalate**. Same safety;
different default; better for our cohort.
