# 72 — Adding Sandbox Backend

Concrete implementation guidance for adding the first sandbox
backend (subprocess) to Ember. Phase 3 work.

---

## Why subprocess first

- Linux native; no Docker dependency.
- Lightweight.
- Pi-class compatible.
- Sufficient for most high-power tools.

Docker backend can come later for operators wanting stronger
isolation.

---

## Step 1: define the Protocol

`src/ember/sandbox/protocol.py`:

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
    crashed: bool = False

@dataclass(frozen=True)
class SandboxHealth:
    available: bool
    detail: str

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
        ...
    
    async def health(self) -> SandboxHealth:
        ...
```

---

## Step 2: implement subprocess backend

`src/ember/sandbox/backends/subprocess_sandbox.py`:

```python
import asyncio
import os
import resource
import sys

class SubprocessSandbox:
    BACKEND_KIND = "subprocess"
    
    async def execute(
        self,
        command,
        cwd,
        env,
        timeout_s=30.0,
        max_memory_mb=200,
        max_output_bytes=5_000_000,
    ):
        if sys.platform != "linux":
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr="SubprocessSandbox: only Linux supported",
                timed_out=False,
                cpu_seconds=0,
                peak_memory_mb=0,
                crashed=True,
            )
        
        def preexec():
            # Set resource limits before exec
            resource.setrlimit(resource.RLIMIT_CPU, (int(timeout_s), int(timeout_s)))
            resource.setrlimit(
                resource.RLIMIT_AS,
                (max_memory_mb * 1024 * 1024, max_memory_mb * 1024 * 1024),
            )
            resource.setrlimit(
                resource.RLIMIT_FSIZE,
                (max_output_bytes, max_output_bytes),
            )
            os.nice(10)
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=preexec,
            )
            
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_s + 5,
                )
                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")
                
                # Truncate if exceeds max_output
                stdout = stdout[:max_output_bytes]
                stderr = stderr[:max_output_bytes]
                
                # Get resource usage
                rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
                
                return SandboxResult(
                    exit_code=proc.returncode or 0,
                    stdout=stdout,
                    stderr=stderr,
                    timed_out=False,
                    cpu_seconds=rusage.ru_utime + rusage.ru_stime,
                    peak_memory_mb=rusage.ru_maxrss // 1024,  # KB → MB
                )
            
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return SandboxResult(
                    exit_code=-9,
                    stdout="",
                    stderr=f"Timed out after {timeout_s}s",
                    timed_out=True,
                    cpu_seconds=timeout_s,
                    peak_memory_mb=0,
                )
        
        except Exception as exc:
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=f"Sandbox error: {exc}",
                timed_out=False,
                cpu_seconds=0,
                peak_memory_mb=0,
                crashed=True,
            )
    
    async def health(self):
        if sys.platform != "linux":
            return SandboxHealth(
                available=False,
                detail="SubprocessSandbox requires Linux"
            )
        return SandboxHealth(
            available=True,
            detail="Linux cgroups available"
        )
```

---

## Step 3: sandbox registry

`src/ember/sandbox/registry.py`:

```python
class SandboxRegistry:
    def __init__(self):
        self._backends: dict[str, Sandbox] = {}
    
    def register(self, backend: Sandbox):
        self._backends[backend.BACKEND_KIND] = backend
    
    def get(self, kind: str) -> Sandbox | None:
        return self._backends.get(kind)
    
    def pick_available(self, preference: list[str]) -> Sandbox | None:
        for kind in preference:
            backend = self._backends.get(kind)
            if backend and backend.health_cache.available:
                return backend
        return None
```

Backends register at boot:

```python
# In src/ember/sandbox/__init__.py
def initialize_sandbox_registry():
    registry = SandboxRegistry()
    registry.register(NoSandbox())
    registry.register(SubprocessSandbox())
    # docker, ssh: registered if pip extras installed
    return registry
```

---

## Step 4: integrate with tool framework

In tool registration:

```python
@register_tool(
    name="run_shell_command",
    approval=Approval.PER_CALL,
    sandbox_required=True,
    sandbox_preference=["docker", "subprocess"],
)
async def run_shell_command(cmd: str) -> str:
    sandbox = get_sandbox_for_tool("run_shell_command")
    
    if sandbox is None:
        return error("No sandbox backend available for run_shell_command.")
    
    result = await sandbox.execute(
        command=["sh", "-c", cmd],
        cwd=Path.home() / "sandbox-workdir",
        env={"PATH": "/usr/local/bin:/usr/bin:/bin"},
        timeout_s=30,
    )
    
    return format_result(result)
```

The tool *delegates* to sandbox; doesn't know which backend.

---

## Step 5: configuration

```yaml
ember:
  sandbox:
    default_backend: subprocess
    
    per_tool_backend:
      run_shell_command: subprocess
      python_eval: subprocess
    
    subprocess:
      enabled: true
      max_memory_mb: 256
      max_output_bytes: 5_000_000
      max_timeout_s: 30
      nice_level: 10
    
    docker:
      enabled: false              # opt-in extra
    
    ssh:
      enabled: false              # opt-in extra
```

---

## Step 6: tests

```python
# tests/unit/test_sandbox_subprocess.py

@pytest.mark.skipif(sys.platform != "linux", reason="Linux only")
async def test_subprocess_sandbox_basic_command():
    sandbox = SubprocessSandbox()
    
    result = await sandbox.execute(
        command=["echo", "hello"],
        cwd=Path("/tmp"),
        env={"PATH": "/usr/bin:/bin"},
    )
    
    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert not result.timed_out
    assert not result.crashed

async def test_subprocess_sandbox_timeout():
    sandbox = SubprocessSandbox()
    
    result = await sandbox.execute(
        command=["sleep", "60"],
        cwd=Path("/tmp"),
        env={"PATH": "/usr/bin:/bin"},
        timeout_s=1.0,
    )
    
    assert result.timed_out
    assert result.exit_code != 0

async def test_subprocess_sandbox_memory_limit():
    sandbox = SubprocessSandbox()
    
    # Try to alloc 1GB (should be killed)
    code = "x = bytearray(1024*1024*1024); print(len(x))"
    result = await sandbox.execute(
        command=["python", "-c", code],
        cwd=Path("/tmp"),
        env={"PATH": "/usr/bin:/bin"},
        max_memory_mb=100,
    )
    
    # Should fail with OOM (exit code varies)
    assert result.exit_code != 0
```

---

## Step 7: doctor integration

Doctor screen shows sandbox health:

```
Sandbox Backends:
  none:        ✓ available (passthrough)
  subprocess:  ✓ available (Linux cgroups working)
  docker:      ✗ unavailable (Docker daemon not running)
  ssh:         ✗ disabled (not configured)
```

---

## Step 8: documentation

`docs/sandbox/README.md`:
- Why sandboxing.
- Backend selection.
- Per-tool sandbox configuration.
- Troubleshooting.
- Adding custom backends.

---

## Step 9: rollout in V3

V3 release notes:

```
V3 introduces sandbox backends for high-power tools.

By default, subprocess sandbox is available on Linux.

When a tool requires sandboxing (declared in its registration),
it executes inside the configured backend.

To enable Docker sandbox (stronger isolation):
  pip install ember-agent[sandbox-docker]
  ember sandbox enable docker

See docs/sandbox/ for details.
```

---

## What about Docker backend

`src/ember/sandbox/backends/docker_sandbox.py` follows the
same pattern. Implementation uses `docker run` via subprocess.

Pip extra: `pip install ember-agent[sandbox-docker]`.

Operator opts in. Phase 3+ ships if demand exists.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Sandbox bypass via tool bug | Multiple layers (per Carapace Defense) |
| Resource limit doesn't work on non-Linux | Backend declares unavailable |
| Operator disables sandbox unintentionally | Setup warns; defaults preserve |
| Performance overhead | Modest (~50ms per call); acceptable |

---

## Closing

Adding Sandbox Backend is **Phase 3 work**. Subprocess backend
first; Docker + SSH later if demand. ~400 lines of code +
tests.

Critical: ship before *first* high-power tool (e.g.,
`run_shell_command`). Tools requiring sandbox depend on
backends existing.

This is *the foundation for safely expanding Ember's tool
ecosystem*. Klóinn-informed; sovereignty-aligned.
