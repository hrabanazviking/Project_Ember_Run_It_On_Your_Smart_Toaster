# 50 — Docker Default Sandbox for LARGE Profiles

When and how to default to Docker-based sandboxing for high-
power Ember installations.

---

## The proposal

For operators on **LARGE** or **WORKSTATION** profiles (per
Yggdrasil cross-platform), the *default* for high-power tools
is Docker sandbox.

For TINY / SMALL / MEDIUM: default is subprocess (lighter) or
no-sandbox + per-call approval.

This *tiers* the default by hardware profile, respecting both
Pi-class operators (no Docker overhead) and workstation
operators (full security).

---

## What "high-power tools" means

Tools triggering this default:
- `run_shell_command` (when added; Phase 3+).
- `python_eval` (when added).
- `browser_render` (when added; full headless browser).
- Operator-installed skill tools declaring `sandbox_required: True`.

Low-power tools (search_well, read_local_file with sandbox,
fetch_url with robots.txt) don't need Docker.

---

## Per-profile defaults

```python
PROFILE_SANDBOX_DEFAULTS = {
    "TINY": "none",         # no Docker; per-call approval only
    "SMALL": "subprocess",  # if available
    "MEDIUM": "subprocess",
    "LARGE": "docker",      # Docker recommended
    "WORKSTATION": "docker",
}
```

These are *defaults*. Operators always override.

---

## Why Docker for LARGE+

Workstation-class operators:
- Usually have Docker installed (often for other reasons).
- Have RAM to spare for containers.
- May handle more sensitive data than Pi-class hobbyists.
- Are more likely to install community skills (which need
  isolation).

So Docker fits their context.

---

## Why NOT Docker for TINY/SMALL/MEDIUM

- Docker on Pi 5 works but consumes resources.
- Pi Zero 2W doesn't run Docker well.
- Most Pi-class operators don't install Docker.
- Per-call approval + per-tool sandbox is sufficient for
  *current* tool set.

If a TINY operator wants Docker: opt-in via config.

---

## How the default applies

When Ember boots:

```python
def determine_sandbox_default(profile_class):
    if profile_class in ("LARGE", "WORKSTATION"):
        if docker_available():
            return "docker"
        else:
            print("Warning: LARGE profile detected but Docker "
                  "unavailable. Falling back to subprocess sandbox.")
            return "subprocess"
    else:
        return "subprocess" if subprocess_sandbox_available() else "none"
```

Sensible fallback if Docker isn't installed.

---

## What about operator-installed skills

Skills can override:

```python
@register_tool(
    name="my_skill_tool",
    sandbox_required=True,
    # Optional: declare exact sandbox preference
    sandbox_preference=["docker"],  # only Docker
)
def my_skill_tool(...):
    ...
```

Or accept profile defaults:

```python
@register_tool(
    name="my_skill_tool",
    sandbox_required=True,
    # uses profile-class default
)
```

---

## Operator override

```yaml
ember:
  sandbox:
    default_backend: docker        # explicit override
    # OR
    default_backend_per_profile:
      LARGE: docker
      MEDIUM: docker               # operator wants stricter
      SMALL: docker                # operator with Docker installed
      TINY: none
```

---

## Setup wizard prompt

When operator is detected as LARGE+:

```
[X/8] Sandbox backend for high-power tools

  Detected: LARGE profile (32GB RAM, NVIDIA GPU).
  
  For high-power tools (run_shell_command, etc.), we recommend
  Docker sandboxing.
  
  Docker is installed and running.
  
  ▶ Use Docker (recommended for LARGE)
    Use subprocess (lighter; less isolation)
    No sandbox (trust per-call approval only)
  
  > Docker
```

For SMALL/MEDIUM, the wizard suggests subprocess.

---

## Docker image for Ember sandbox

`ember-sandbox` image:

```dockerfile
FROM python:3.14-slim

RUN useradd -m ember-sandbox

USER ember-sandbox
WORKDIR /workspace

# Standard tools needed by sandboxed code
RUN pip install --user requests beautifulsoup4 ...
```

Operators pull when needed:

```bash
docker pull ember/sandbox:0.3.0
# or build locally:
cd ~/.ember/sandbox/
docker build -t ember/sandbox:latest .
```

Image is small (~200MB) + read-only filesystem when run.

---

## Per-call container lifecycle

Default: ephemeral containers (one per tool call).

```python
async def execute_in_docker(command, ...):
    docker_args = [
        "docker", "run",
        "--rm",
        "--memory", "256m",
        "--cpus", "1",
        "--network", "none",
        "--read-only",
        "--tmpfs", "/tmp:rw,size=64m",
        "-v", f"{cwd}:/workspace:ro",
        "-w", "/workspace",
        "ember/sandbox:latest",
        "timeout", str(timeout_s),
    ] + command
    # ...
```

Each call creates + destroys a container. Slow (~1-2s
startup), but maximum isolation.

For frequent calls: container pooling (V5+ optimization).

---

## Network access in sandbox

Default: no network (--network none).

For tools that *need* network (e.g., fetch_url even in
sandbox):

```python
sandbox_preference=["docker"],
sandbox_network=True,   # allow network
```

Network-allowed sandboxes use `--network bridge` (Docker
default).

---

## Filesystem access

Default: read-only mount of operator's workspace.

For tools that write:
```python
sandbox_write_allowed=True,
sandbox_write_path="/tmp",   # only writable to /tmp
```

Writes are persisted only to a *temporary* path; copied out
after container exits.

---

## What about non-Docker for LARGE

Some LARGE-profile operators won't have Docker (security-
maximalist; minimal-software philosophy).

For them: subprocess sandbox fallback. Less isolated but
still better than no-sandbox.

Doctor screen shows:
- Detected profile: LARGE
- Recommended sandbox: Docker
- Active sandbox: subprocess (Docker not available)
- Suggestion: install Docker for stronger isolation

Operator decides.

---

## Performance impact

Docker container startup: ~500-2000ms per call.

For tools called *frequently* (10+ times per chat turn): too
slow.

Mitigation: container pooling (keep N containers warm).

For Phase 3 initial: ephemeral containers. Acceptable for
infrequent high-power tool use.

---

## What about WSL on Windows

Windows operators may use WSL2 for Docker. The Linux side
runs containers; Ember talks to Docker daemon via socket.

Cross-platform sandbox works; Windows operators have additional
setup.

---

## Configuration shape

```yaml
ember:
  sandbox:
    profile_defaults:
      TINY: none
      SMALL: subprocess
      MEDIUM: subprocess
      LARGE: docker
      WORKSTATION: docker
    
    docker:
      image: ember/sandbox:latest
      memory_limit_mb: 256
      cpu_limit: 1.0
      network: none
      read_only_fs: true
      tmpfs_size_mb: 64
      pull_on_startup: true
      pool_size: 0                # ephemeral; 0 = no pool
    
    fallback_chain:
      - docker
      - subprocess
      - none
```

---

## What we tell operators

LARGE-profile setup:

```
For your workstation, we default to Docker-sandboxing for
high-power tools (when you add them). This provides strong
isolation between Ember and the tool execution.

If Docker isn't installed or you prefer otherwise, override
in ember.yaml.
```

Pi-class setup:

```
For your Pi 5, we default to lighter subprocess sandboxing
(or per-call approval for tools that don't need isolation).
Docker is overkill for typical Pi workloads.
```

---

## Closing

Docker Default Sandbox for LARGE Profiles is **Phase 3 +
tiered Klóinn adoption**. Workstation operators get strong
isolation by default; Pi-class operators get lighter
defaults appropriate to their hardware.

This is *the right pattern* — fitting the tool to the
context. OpenClaw defaults Docker because their cohort has
Docker; Ember tiers because our cohort spans more hardware.

The Klóinn lesson translates with profile-class awareness.
Best-of-both-worlds: strong isolation for those who can run
it; lighter alternatives for those who can't.
