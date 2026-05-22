# 60 — Device Capability Detection

How Yggdrasil knows what kind of device it's running on,
and tunes itself accordingly. The first step of any
cross-platform deployment.

---

## The principle

Ember runs on:
- **Tiny devices**: Raspberry Pi Zero 2 W (512MB RAM), old
  laptops, Chromebooks.
- **Small devices**: Pi 4/5, modest laptops.
- **Workstations**: gaming laptops with discrete GPU.
- **Servers**: multi-GPU desktops, homelab nodes.
- **Clusters**: a federation of any of the above.

Each device has different *capabilities* — RAM, CPU cores,
GPU presence + VRAM, disk speed, network. Yggdrasil
**detects** these at boot and **picks defaults** that fit.

A Pi gets a 1B-parameter model + sqlite-only memory. A
desktop gets a 7B model + Qdrant + full memory stack.

---

## What gets detected

A `DeviceProfile` is built at boot from these signals:

```python
@dataclass(frozen=True)
class DeviceProfile:
    # CPU
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_arch: str               # "x86_64", "aarch64", "armv7l"
    cpu_freq_max_mhz: int
    
    # Memory
    ram_total_mb: int
    ram_available_mb: int
    swap_mb: int
    
    # GPU
    gpu_present: bool
    gpu_kind: str | None        # "nvidia", "amd", "intel", "apple_m"
    gpu_vram_mb: int            # 0 if no GPU
    gpu_compute_capability: str | None  # e.g., "8.6" for Ampere
    
    # Disk
    disk_total_gb: int
    disk_free_gb: int
    disk_speed_class: str       # "spinning", "sata_ssd", "nvme"
    
    # Network
    network_interfaces: list[str]
    on_tailnet: bool            # operator's tailscale present?
    
    # OS
    os_name: str                # "linux", "darwin", "windows"
    os_version: str
    distro: str | None          # for linux: "ubuntu", "fedora", etc.
    
    # Power
    is_battery: bool
    is_low_power: bool          # currently in power-save mode
    
    # Derived
    profile_class: ProfileClass # see below
```

The `profile_class` is the *summary classification* — what
"tier" of device this is.

---

## The five profile classes

```python
class ProfileClass(StrEnum):
    TINY = "tiny"               # < 1 GB RAM
    SMALL = "small"             # 1-4 GB RAM, no GPU
    MEDIUM = "medium"           # 4-16 GB RAM, optional small GPU
    LARGE = "large"             # 16-64 GB RAM, GPU >= 8 GB VRAM
    WORKSTATION = "workstation" # > 64 GB RAM OR multi-GPU
```

Classification logic:

```python
def classify(profile: DeviceProfile) -> ProfileClass:
    if profile.ram_total_mb < 1024:
        return ProfileClass.TINY
    if profile.ram_total_mb < 4096:
        return ProfileClass.SMALL
    if profile.ram_total_mb < 16384:
        return ProfileClass.MEDIUM
    if profile.ram_total_mb < 65536:
        return ProfileClass.LARGE
    return ProfileClass.WORKSTATION
```

(Simplified; actual logic considers GPU + disk + cores.)

---

## What each profile class enables/disables

Per [`62_TIERED_DEFAULTS_BY_PROFILE.md`](62_TIERED_DEFAULTS_BY_PROFILE.md), each class has
default settings:

| Setting | TINY | SMALL | MEDIUM | LARGE | WORKSTATION |
|---|---|---|---|---|---|
| Funi model | 0.5B-1B | 1B-3B | 3B-7B | 7B-13B | 13B-70B+ |
| Brunnr backend | sqlite | sqlite | sqlite_vec | pgvector | pgvector + qdrant |
| Bifrǫst enabled | no | optional | yes | yes | yes |
| Huginn | no | no | yes | yes | yes |
| Muninn | no | optional | yes | yes | yes |
| MemPalace | no | no | optional | yes | yes |
| Dreamstate | basic | basic | full | full | full |
| Cloak browser | no | no | optional | yes | yes |
| Seiðr | yes | yes | yes | yes | yes |
| Verdandi | basic | yes | yes | yes | yes |

The operator can override any default. Detection just
gives sensible *starting* points.

---

## How detection happens

Single module: `src/ember/yggdrasil/device/profile.py`.

```python
def detect() -> DeviceProfile:
    """Build a DeviceProfile from system signals."""
    return DeviceProfile(
        cpu_cores_physical=_count_physical_cores(),
        cpu_cores_logical=os.cpu_count(),
        cpu_arch=platform.machine(),
        # ...
        gpu_present=_detect_gpu(),
        gpu_kind=_detect_gpu_kind(),
        gpu_vram_mb=_detect_gpu_vram(),
        # ...
        on_tailnet=_check_tailscale_interface(),
        is_battery=_is_running_on_battery(),
    )
```

Each detector is *robust*: returns sensible defaults if
the underlying signal is unavailable.

---

## GPU detection specifics

GPU detection is the *trickiest* part:

```python
def _detect_gpu_kind() -> str | None:
    """Return 'nvidia', 'amd', 'intel', 'apple_m', or None."""
    
    # Try nvidia-smi
    if _command_exists("nvidia-smi"):
        return "nvidia"
    
    # Try ROCm
    if _command_exists("rocm-smi"):
        return "amd"
    
    # macOS: check arm64 (Apple Silicon)
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        return "apple_m"
    
    # Intel iGPU: check for /dev/dri/renderD128 on Linux
    if Path("/dev/dri/renderD128").exists():
        return "intel"
    
    return None
```

Each detection has a fallback to "no GPU." We never crash
on unusual configurations.

---

## When to re-detect

Once at boot is enough for *most* signals (CPU, RAM
hardware, GPU presence).

Some signals change dynamically:
- `is_battery` / `is_low_power` — re-detected every 5
  minutes.
- `disk_free_gb` — re-checked on every snapshot operation.
- `on_tailnet` — re-checked on every cross-device operation.

The `DeviceProfile` is *mostly* immutable; specific fields
update.

---

## What operators see

Stofa's Doctor screen shows the detected profile:

```
Device Profile:
  Class:         LARGE
  CPU:           AMD Ryzen 7 7840HS (16 logical cores)
  RAM:           32 GB total / 18 GB free
  GPU:           NVIDIA RTX 2060 (6 GB VRAM)
  Disk:          1 TB NVMe SSD (450 GB free)
  OS:            Linux 7.0.0 (Kubuntu 26.04)
  Network:       Ethernet, Tailscale active
  Power:         AC (battery present, 87% charged)
  
Yggdrasil tuned to LARGE profile.
Override defaults: ember.yaml → yggdrasil.device.override_class
```

Operators can also force a class:

```yaml
yggdrasil:
  device:
    detection: auto         # or "tiny"/"small"/"medium"/"large"/"workstation"
    overrides:
      cpu_cores_logical: 8  # force a value
```

Useful for testing.

---

## Edge cases handled

### Container with limited resources

Docker / Podman containers can be CPU-limited or
memory-capped. We respect cgroup limits:

```python
def _detect_ram_total_mb() -> int:
    """Respect cgroup limits if present."""
    cgroup_limit = _read_cgroup_memory_limit()
    if cgroup_limit and cgroup_limit < _total_system_ram():
        return cgroup_limit
    return _total_system_ram()
```

A 32GB host running Ember in a 2GB container correctly
detects as SMALL, not LARGE.

### Headless server

No display, no GPU intended for graphics. We don't enable
Stofa's animations / heavy UI by default; CLI-only mode
makes sense.

### Operator on iPad / mobile via SSH

Remote terminal; effective profile is the *server's*, but
Stofa adapts terminal rendering to the operator's terminal
capabilities (256-color, true-color, font metrics).

---

## What happens at boot

```
yggdrasil.boot.started
   ↓
detect device profile (~50ms)
   ↓
yggdrasil.device.profiled (profile_class=LARGE)
   ↓
load defaults for profile_class
   ↓
apply operator overrides from ember.yaml
   ↓
initialize realms enabled by config
   ↓
yggdrasil.boot.completed (active_realms=[...])
```

The whole boot sequence is observable via Verdandi.

---

## Why this matters

Without device detection:
- Operators on Pi spend an hour figuring out "why won't
  Qdrant run."
- Operators on workstations have lobotomized defaults
  and don't realize they're not using full capacity.
- Cross-device support becomes a manual configuration
  exercise for every operator.

With device detection:
- Pi gets *working defaults* the moment they install.
- Workstation gets *appropriate defaults* automatically.
- "Same Ember install, different defaults" makes the
  experience portable.

---

## Test strategy

Per profile class:
- `tests/integration/test_yggdrasil_profile_tiny.py`
  (simulates tiny via overrides).
- ...up through WORKSTATION.
- Each verifies that the *right* realms are enabled / the
  *right* models are recommended.

For real hardware: manual smoke tests on Pi 5, on the
travel laptop, on the homelab server.

---

## Closing

Device Capability Detection is **the foundation of
Yggdrasil's cross-platform promise**. Detection happens
once; defaults flow from it; operators can override.

The Pi works. The laptop works. The workstation works.
All from the *same install*. That's the promise; detection
is how we keep it.
