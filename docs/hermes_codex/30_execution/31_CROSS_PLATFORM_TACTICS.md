---
codex_id: 31_CROSS_PLATFORM_TACTICS
title: Cross-Platform Tactics — $5 VPS to Termux to Workstation
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - setup-hermes.sh:38-203
  - constraints-termux.txt:1-16
  - pyproject.toml:130-148
  - Dockerfile:1-50
  - flake.nix:1-50
  - nix/packages.nix
  - cron/scheduler.py:23-30
  - agent/process_bootstrap.py:63-110
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 30_execution/33_HOT_COLD_TIERS
  - 30_execution/40_SERVERLESS_HIBERNATION
  - 60_synthesis/63_INTEGRATION_PATHS
  - 50_verification/53_CRASH_PROOFING_PATTERNS
---

# Cross-Platform Tactics

Hermes runs on a $5 VPS, on a workstation, in a Docker container, on a Mac, on a Pi, and on an Android phone via Termux. The same Python package. Different entry conventions, different dep sets, different IO assumptions. None of that is accidental. It's a series of deliberate engineering decisions that let one codebase land cleanly on every surface a user might own. I'm Eldra. I'm going to walk you through the actual tactics, then translate them into Ember's must-run-on-Pi mandate.

## Surface One — pyproject.toml as the Compatibility Skeleton

Open `pyproject.toml`. Line 8 is the foundation: `requires-python = ">=3.11"`. That single line eliminates an enormous amount of compatibility code. Hermes doesn't carry a backport for `tomllib`, `ExceptionGroup`, `Self`, `Required`, or any of the 3.11-additions.

The dependency philosophy is just as important. Line 13–37 is a comment block, and it's one of the wisest pieces of writing in the repo:

> "Exact pins mean the only way a new package version reaches a user is via an intentional update on our end... This was tightened on 2026-05-12 in response to the Mini Shai-Hulud worm hitting mistralai 2.4.6 on PyPI; if that release had been captured by `mistralai>=2.3.0,<3` rather than an exact pin, every install in the hours before the quarantine would have pulled it."

Cross-platform robustness *is* supply-chain robustness. The promise "runs on every platform" presumes "and isn't compromised on any platform." Hermes pins exact versions and treats the lockfile as part of the platform.

The dep set is split into a tiny base (line 38–66) plus 30+ optional extras (line 69+). The principle, from line 31–34:

> "Scope rule: only packages used by EVERY hermes session belong here. Anything that's provider-specific... belongs in an extra and gets lazy-installed via `tools/lazy_deps.py` when the user picks that backend."

This is what lets a Termux install actually fit. The Android/Termux extra at line 133 — `termux` — is *curated*; it deliberately omits Android-incompatible dependencies that the default `all` would pull (voice deps, primarily). The full `all` extra is for desktops; `termux-all` is the same idea filtered for Android.

The lesson: a cross-platform Python project doesn't ship one fat dep list. It ships a *base* small enough to install anywhere, plus extras gated on `sys_platform`. Hermes goes further with `tzdata==2025.3; sys_platform == 'win32'` (line 56) — Windows lacks an IANA tzdata, so it gets one shipped via PyPI. macOS and Linux do not pay that cost.

## Surface Two — setup-hermes.sh, the Bimodal Installer

`setup-hermes.sh` is 450+ lines and exists for one reason: the same shell-script entry point must work on desktops/servers (where `uv` is the right tool) and on Termux (where `uv` won't reliably work, but stdlib `venv` + `pip` does).

The branch is `is_termux()` at line 38:

```bash
is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
}
```

Two signals: the `TERMUX_VERSION` env var (set by the Termux app), and the canonical `PREFIX` path containing `com.termux/files/usr`. Either is sufficient. Belt and suspenders. The right pattern when you don't fully trust the environment.

After `is_termux()` returns true, the installer takes a different path entirely:

- Skips `uv` (line 69: "Termux detected — using Python's stdlib venv + pip instead of uv").
- Uses `$PREFIX/bin` for symlinks instead of `~/.local/bin` (line 43).
- Installs `.[termux]` constrained by `constraints-termux.txt` (line 197–203).
- Falls back to `-e "."` (no extras) if the `.[termux]` install fails (line 200).

That fallback line is the unsung hero. **Hermes degrades gracefully even at install time.** If pip can't satisfy `.[termux]` because of a wheel hiccup, it still installs the core. The user gets a working Hermes that may lack a few optional features rather than a broken Hermes.

`constraints-termux.txt` itself is six pins (line 9–15):

```
ipython<10
jedi>=0.18.1,<0.20
parso>=0.8.4,<0.9
stack-data>=0.6,<0.7
pexpect>4.3,<5
matplotlib-inline>=0.1.7,<0.2
```

These are not direct Hermes deps. They are *transitives* that have versions known to work on Termux's Python and versions that break. The constraints file pins them out of the bug zone without making the desktop install pay the same cost. This is what production cross-platform engineering actually looks like: not "write code that runs everywhere," but "write code that runs everywhere PLUS maintain a tiny constraints file per platform that pins around the known-bad upstream patches."

## Surface Three — Dockerfile and the Container Path

`Dockerfile:1-3` does something I have not seen before: it pins both `uv` and `gosu` as scratch base images by SHA256 digest:

```dockerfile
FROM ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie@sha256:b3c543b6c4f23a5f2df22866bd7857e5d304b67a564f4feab6ac22044dde719b AS uv_source
FROM tianon/gosu:1.19-trixie@sha256:3b176695959c71e123eb390d427efc665eeb561b1540e82679c15e992006b8b9 AS gosu_source
FROM debian:13.4
```

Three FROM lines. Two of them are sourced for their binaries only (multi-stage COPY at line 25). The final image is plain Debian 13. The digest pins make this reproducible across Docker rebuilds, registries, and time. Same source, same image, forever — until you intentionally bump.

Line 18: `tini` for zombie reaping. The justification is right there in the comment:

> "tini reaps orphaned zombie processes (MCP stdio subprocesses, git, bun, etc.) that would otherwise accumulate when hermes runs as PID 1. See #15012."

When the agent spawns 50 MCP subprocesses over a long run, each exit must be `wait()`-ed or the kernel keeps a zombie process slot. Without `tini`, a long-running Hermes container slowly fills the PID table. The fix is one binary in the entrypoint chain.

Line 22: a UID 10000 hermes user is created at build time. The `gosu` binary then drops privileges at container start. This is the rare cross-platform docker pattern that actually does the right thing: run as root briefly to set up, then drop. Files written to `/opt/data` (the volume mount) belong to UID 10000, which the host can map cleanly.

Line 56: `npm_config_install_links=false`. The justification is buried in a 25-line comment block. Briefly: Debian 13 ships an older npm whose default would copy `file:` workspace deps; the host-side lockfile was generated with a newer npm that uses symlinks. Without the override, the container's `node_modules/.package-lock.json` permanently disagrees with the root lock, triggering a runtime `npm install` on every startup that fails because `node_modules/` is now root-owned. *One env var prevents an entire class of startup-time bugs.* This is the type of fix that earns the engineer a beer.

## Surface Four — flake.nix and the Nix Path

`flake.nix:1-50` is short. The whole structure of the Nix package is in `nix/`. The flake declares support for three architectures:

```nix
systems = [
  "x86_64-linux"
  "aarch64-linux"
  "aarch64-darwin"
];
```

`x86_64-linux` covers your VPS and your desktop Linux. `aarch64-linux` covers Pi 5, ARM cloud instances, and Termux *with a stretch*. `aarch64-darwin` covers Apple Silicon Macs. Notably absent: `x86_64-darwin` (Intel Macs are EOL territory) and `x86_64-windows` (Nix isn't a Windows tool).

Five `imports` (line 41): packages, overlays, NixOS modules, checks, and devShell. The split means a user can:

- `nix build .#hermes-agent` for a system-level install
- `nix develop` for a hacking shell
- `nix run .#tui` for the terminal UI
- import the NixOS module in their `configuration.nix` for a service

Four entry surfaces from one flake. The `uv2nix` and `pyproject-nix` inputs (lines 9–17) reuse Python's `uv.lock` to drive Nix's dep resolution — the Python lockfile is the source of truth, and Nix just *reads* it. No double maintenance.

## Surface Five — Process Bootstrap (the runtime side)

`agent/process_bootstrap.py` is small but important. Three concerns, lines 1–22:

1. **Lazy OpenAI SDK import** (`_OpenAIProxy`). Saves ~240ms at cold start by deferring `from openai import OpenAI` until first use, while keeping `isinstance(client, OpenAI)` checks working.
2. **`_SafeWriter` for stdout/stderr** (line 63–109). On systemd, on Docker, when piped to nothing — `print()` can raise `OSError: Input/output error`. The wrapper swallows it. The agent doesn't die because the log pipe broke.
3. **HTTP proxy resolution** (lines 112–142). Reads `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` (uppercase AND lowercase variants). Respects `NO_PROXY` via `urllib.request.proxy_bypass_environment`. The corp-firewall case is handled at startup.

These three concerns are exactly the failure modes you hit when you ship Python to surfaces other than "an interactive terminal on a developer's laptop."

The `_SafeWriter` deserves its own moment. Lines 88–91:

```python
def write(self, data):
    try:
        return self._inner.write(data)
    except (OSError, ValueError):
        return len(data) if isinstance(data, str) else 0
```

When stdout is gone, return the bytes "written" as if successful. Print silently no-ops instead of cascading. **Print should never crash an agent.** That's a sharp line, and Hermes draws it.

## Surface Six — Cross-Platform File Locks (and other tactical details)

`cron/scheduler.py:23-30` is a tiny pattern with big consequences:

```python
try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
```

The same module supports POSIX file locks (via `fcntl`) and Windows file locks (via `msvcrt`), with the polymorphism handled at import time. Later (line 1809), the actual lock acquisition switches on `if fcntl: ... elif msvcrt: ...`. Same intent, different syscalls, one code path. This is how you write "locks a file cross-platform" in Python without depending on `portalocker` or `filelock`.

Other tactical details I noted while spelunking:

- `psutil` (pyproject.toml:64) replaces POSIX-only `os.kill(pid, 0)` and `os.killpg`. Pid liveness checks work on Windows.
- `httpx[socks]` (pyproject.toml:42) for SOCKS proxy support — common on Termux-with-Orbot.
- `prompt_toolkit` (line 47) over `readline` — because `readline` is GNU-only and a CPython build on macOS may use libedit instead, which has subtly different keybindings.
- Network code uses absolute timeouts on every request (see retry orchestration in [[30_execution/41_MULTI_PROVIDER_FAILOVER]]) — POSIX-only `signal.alarm` is never used.

## What Hermes Does That Pi-Class Ember Should Not Inherit

Be honest about the things you'd cross-walk with caveats:

1. **Docker as a first-class install path.** A Pi 5 can run Docker, but it doesn't have to. Ember's Pi default should be a venv + pip install, period. Document Docker as supported, not as canonical.
2. **`uv` as default.** `uv` is faster but a separate native binary. Ember should default to stdlib venv + pip (the Termux path Hermes already uses). Make `uv` a documented alternative for users who already have it.
3. **20+ optional extras.** Hermes carries a sprawl of provider extras. Ember's Vow of Smallness suggests we hold to maybe 5: `pi`, `sqlite_vec`, `pgvector`, `qdrant`, `chroma`. Each one is a storage adapter; that's the only optionality Ember actually needs at the install layer.
4. **Multi-stage Dockerfile.** Beautiful pattern but overkill for a "runs anywhere" agent. Ember can ship a single-stage `python:3.14-slim` image and let people fork it for production layouts.

## What This Means for Ember

Ember's Vow of Smallness and Vow of Flexible Roots are exactly the cross-platform stance Hermes practices, with the volume turned down. The actionable lifts:

**Strengr's HTTP layer**

Mirror `agent/process_bootstrap.py:112-142` *minus* the OpenAI proxy. Ember already routes through stdlib `urllib` per [[docs/CROSS_PLATFORM_PLAN.md]]. Add a `strengr/proxy.py` that:

```python
def get_proxy_for_base_url(base_url: str | None) -> str | None: ...
def get_proxy_from_env() -> str | None: ...
```

Read `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` (both cases). Respect `NO_PROXY`. Wire into the Strengr health check first and the call path second.

**Funi's lazy adapter loading**

Steal the lazy-import pattern (`_OpenAIProxy`) for Funi's optional backends. The `lmstudio_reasoning.py`, `gemini_native_adapter.py`, `bedrock_adapter.py` etc. in Hermes all defer their SDK imports. Ember's Funi should follow suit: don't import `ollama-python` at module load — defer until the user picks Ollama as the runtime.

```python
# src/ember/spark/funi/runtime/_lazy.py
class _OllamaProxy:
    __slots__ = ()
    def __call__(self, *args, **kwargs):
        return _load_ollama_cls()(*args, **kwargs)
    def __instancecheck__(self, obj):
        return isinstance(obj, _load_ollama_cls())
```

This keeps `ember chat` cold-start under 500ms on a Pi 5 even when llama-cpp-python or ollama-python are in the user's environment.

**Munnr's stdio safety**

Adopt `_SafeWriter`. When Ember runs as a systemd service or in a Docker container, broken-pipe `OSError`s should not crash the chat REPL. The current Ember has Ctrl-C handling at three sites (per the Cross-Platform Plan) — adding `_install_safe_stdio()` to the chat REPL boot is a 20-line addition that closes a class of corner cases.

**Brunnr's lockfile discipline**

The `fcntl` / `msvcrt` polymorphism (cron/scheduler.py:23-30) belongs in Brunnr. Multi-process access to the SQLite Well — say, when the user runs `ember well ingest` in one terminal while `ember chat` runs in another — needs a cross-platform advisory lock so WAL doesn't deadlock. Brunnr should expose:

```python
class WellLock:
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc) -> None: ...
```

Internally, the lock uses `fcntl.flock(LOCK_EX | LOCK_NB)` where available, falls back to `msvcrt.locking(LK_NBLCK, 1)` on Windows, and to a `.lock` sentinel file with PID + mtime on neither.

**Hjarta's platform detection**

Hjarta is the first-run rite. Hermes detects Termux via `TERMUX_VERSION` env var; Ember should detect Pi via `/sys/firmware/devicetree/base/model` (contains "Raspberry Pi") and Termux the same way Hermes does. The detection result feeds the tier selection in [[30_execution/33_HOT_COLD_TIERS]] and sets a sensible default model size:

```python
# src/ember/hjarta/platform.py
@dataclass(frozen=True)
class Host:
    name: str           # "pi5", "termux", "macos-arm", "linux-x86", "windows-x86"
    is_termux: bool
    is_pi: bool
    arch: str           # "x86_64" | "aarch64" | "armv7l"
    has_gpu: bool
    ram_mb: int

def detect_host() -> Host: ...
```

The Host record then drives the welcome message: "Detected: Pi 5 (4GB). Recommended model: llama3.2:3b. Proceed? [Y/n]".

**Vow check**

- **Vow of Smallness** — every tactic here either preserves or strengthens it.
- **Vow of Flexible Roots** — `setup-hermes.sh:43` (PREFIX vs HOME) is exactly the right pattern. No absolute paths anywhere.
- **Vow of Pluggable Storage** — at risk if we adopt Hermes's "one SQLite file, period" approach. Brunnr must continue to support multiple backends, and the cross-platform lock pattern must be backend-agnostic.
- **Vow of Public-Friendliness** — `setup-hermes.sh`'s explicit Termux fallback to "install without extras" is exactly the kind of "it just works" UX a non-developer needs. Ember's installer should do the same.

### Concrete deliverable

A new `docs/CROSS_PLATFORM_PLAN.md` companion called `CROSS_PLATFORM_TACTICS.md` (this doc) plus three actionable PRs:

1. `src/ember/strengr/proxy.py` — env-driven HTTP proxy resolution.
2. `src/ember/spark/funi/runtime/_lazy.py` — proxy class for optional model SDKs.
3. `src/ember/hjarta/platform.py` — host detection with `Pi` / `Termux` / `WSL` recognition.

Each is < 200 lines. Each closes a specific Hermes-validated category of breakage. None violates a Vow.

### Where to read next

- [[30_execution/33_HOT_COLD_TIERS]] — what `detect_host()` feeds into.
- [[30_execution/40_SERVERLESS_HIBERNATION]] — Modal/Daytona for the *cloud* end of the spectrum.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs to land these.

A blade is only as cross-platform as its weakest edge. Sharpen the install layer first. — Eldra.
