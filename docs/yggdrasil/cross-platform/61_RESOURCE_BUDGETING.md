# 61 — Resource Budgeting

How Yggdrasil decides how much CPU / RAM / GPU / disk to
use, and stays within budget under load.

---

## The principle

A device's *capabilities* (per [`60_DEVICE_CAPABILITY_DETECTION.md`](60_DEVICE_CAPABILITY_DETECTION.md))
tell us *what's possible*. A *budget* tells us *how much
Ember should use*.

Operators on a workstation might want Ember to use 80% of
the GPU. On a daily-driver laptop, 30%. On a Pi running
other services, 20%.

The budget is **operator-controlled**; Yggdrasil enforces
it.

---

## What gets budgeted

| Resource | Default budget | Reason |
|---|---|---|
| **RAM (max)** | 50% of total | leave room for OS + other apps |
| **CPU (max steady)** | 75% of cores | leave responsiveness |
| **CPU (burst)** | 100% briefly | OK for short ops |
| **GPU VRAM** | 80% of available | reserve for desktop compositor |
| **Disk write IOPS** | 1000/s sustained | don't thrash slow SSDs |
| **Disk space (state)** | configurable | snapshots + indexes grow |
| **Network egress** | unlimited | (sovereign default; no remote calls) |
| **Network ingress** | unlimited | operator's responsibility |

Defaults are *conservative*. Power users raise them.

---

## How budgets get enforced

Different resources need different enforcement:

### RAM

We can't *force* Python to release memory, but we can:
1. **Pre-allocate within budget** (the LLM, the vector
   index, the SQLite cache).
2. **Watch RSS via psutil**; if it grows past budget,
   trigger emergency action: shed caches, skip non-
   essential ops.
3. **Refuse to load** realms that would exceed budget.

Example: starting with `budget.ram_max_mb: 4000` on an
8GB Pi 5, if Mímir + Huginn would together need 5GB,
Yggdrasil refuses to enable both. Operator sees clear
message.

### CPU

Background workers (dreamstate, reconciliation, gossip)
get *nice levels* on Unix:

```python
os.nice(10)  # background workers run at lower priority
```

If `cpu_steady_percent` would be exceeded, background work
yields to chat.

### GPU VRAM

The LLM and the embedding model (if GPU-accelerated)
must fit within `gpu_vram_max_mb`. We pick model sizes
that fit; if operator over-rides to a larger model, we
warn loudly before loading.

### Disk

Disk space monitoring:
- Snapshots check `disk_free_gb` before writing.
- If free space < `disk_min_free_gb`, snapshots skip
  (operator gets banner).
- Old snapshots prune automatically when over budget.

Disk IOPS:
- mimir-well's SQLite operations get rate-limited if
  needed.
- Background indexing throttles when foreground chat is
  active.

---

## Operator configuration

```yaml
yggdrasil:
  budget:
    ram:
      max_mb: 4000          # or "auto" = 50% of total
      emergency_threshold_mb: 3500
    cpu:
      max_steady_percent: 75
      max_burst_percent: 100
      background_nice_level: 10
    gpu:
      max_vram_mb: 4500     # or "auto" = 80% of detected
      reserve_for_other_apps: true
    disk:
      max_state_gb: 50       # for ~/.ember + snapshots
      min_free_gb: 5         # always leave this free
      max_sustained_iops: 1000
      throttle_during_chat: true
```

---

## Adaptive budgeting

Static budgets work for stable single-purpose devices. For
laptops where operator might be browsing/editing alongside
Ember, adaptive budgeting helps:

```python
class AdaptiveBudgeter:
    """Watches system load; tunes Yggdrasil budget dynamically."""
    
    async def adjust_loop(self):
        while True:
            system_load = await self._observe_system()
            if system_load.is_under_pressure():
                self._reduce_yggdrasil_budget()
            else:
                self._restore_default_budget()
            await asyncio.sleep(60)
```

"Under pressure" indicators:
- System swap activity > 1MB/s sustained.
- System load average > num_cores.
- GPU VRAM > 90% used by other processes.
- Power-save mode active.

When detected: pause dreamstate, throttle background
ingest, reduce GPU memory usage.

Adaptive budgeting is **opt-in**; defaults are static.

---

## What happens when budget is exceeded

Three escalation levels:

### Level 1: gentle nudge

Internal warning, logged via Verdandi. Background workers
pause briefly. Operator sees nothing.

### Level 2: clear surface

Chat banner: "Memory pressure detected; pausing background
indexing until load drops."

### Level 3: refuse-to-cause-harm

A request that would push the system past safe limits
gets typed-rejected:

```
operator: ingest /path/to/huge/corpus
ember: That corpus is 12 GB. With your current Yggdrasil
budget (4 GB RAM), ingesting it would risk swapping.

Options:
  1. Increase the budget: ember.yaml → yggdrasil.budget.ram.max_mb
  2. Ingest in batches: ember well ingest <path> --batch-size 100MB
  3. Cancel
```

Never crash. Always inform.

---

## How budget interacts with device profile

The device profile *suggests* a default budget:

| Class | Default budget shape |
|---|---|
| TINY (Pi Zero) | 30% RAM, 50% CPU, no GPU; no Huginn |
| SMALL (Pi 5) | 50% RAM, 70% CPU, no GPU; basic stack |
| MEDIUM (laptop) | 50% RAM, 60% CPU, optional GPU; full stack |
| LARGE (workstation) | 50% RAM, 75% CPU, GPU-on; full stack |
| WORKSTATION | 70% RAM, 90% CPU, GPU-on; advanced features |

Operator can override per-axis. Defaults are designed for
the *common case* per class.

---

## Cross-platform considerations

### Linux

Most accurate signals:
- `/proc/meminfo` for RAM
- `/sys/class/power_supply/` for battery
- cgroups for container limits
- `nvidia-smi` / `rocm-smi` for GPU

### macOS

- `sysctl` for hardware info
- `vm_stat` for memory
- `pmset` for power
- `system_profiler` for GPU (Apple Silicon: built-in)

### Windows

- WMI for hardware
- `nvidia-smi.exe` for GPU
- Power state via Win32 APIs
- (Tested less; defaults conservative)

The detection layer abstracts these. Budget enforcement
uses portable primitives where possible.

---

## What this gives operators

### Predictable behavior

"How much resource will Ember use?" → answerable. Operator
configures the budget; Ember stays within it.

### Multi-tenant friendly

Running Ember on a homelab server alongside other services:
budget keeps Ember polite.

### Battery-friendly

On laptop: when on battery + low power, budget shrinks
automatically (adaptive). When plugged in: full budget.

### Crash-resistant under load

When other apps eat memory, Ember degrades gracefully
instead of OOM-killing.

---

## Risk / known issues

- **Python's GC isn't precise.** RSS may exceed budget
  briefly. We monitor + trigger emergency actions when it
  does.
- **Budget enforcement adds latency.** Negligible (<5ms
  per operation) but real.
- **Operator-chosen budgets may be wrong.** If they
  pick a budget too small for their workload, things will
  fail. We warn but don't override.

---

## Observability

Verdandi events:
- `budget.warning` (resource, current, limit)
- `budget.exceeded` (resource, action_taken)
- `budget.adjustment` (resource, old_limit, new_limit)

Stofa Doctor screen shows live budget usage:

```
Budget:
  RAM:    1.8 GB / 4.0 GB (45%)  [OK]
  CPU:    23% (steady)  [OK]
  GPU:    3.2 GB / 4.5 GB VRAM (71%) [OK]
  Disk:   12 GB / 50 GB state (24%); 230 GB free  [OK]
```

---

## Closing

Resource Budgeting makes Yggdrasil **a polite tenant on
the operator's hardware**. Configure once; the system
respects the budget; degrades gracefully when pushed.

This is what separates *production-grade software* from
*tools that work on the developer's machine but nowhere
else*.
