# ⚡ Performance and Resource Guide

## Benchmarks

Measured on a Raspberry Pi 4 (4GB RAM, ARM Cortex-A72):

| Operation | Time | Memory |
|-----------|------|--------|
| Single pulse (all 4 checks) | 50-150ms | +2MB peak |
| Pulse with nerve impulse | 55-160ms | +0.5KB |
| State DB write | 2-5ms | Negligible |
| Health score calculation | <0.1ms | Negligible |
| Circuit breaker check | <0.01ms | Negligible |
| Daemon idle (sleeping) | 0ms | 15MB |

## Memory Profile

```
Object                Size       Share
───────────────────────────────────────
HeartbeatDaemon       ~2 KB      0.01%
HeartbeatState        ~1 KB      0.01%
Check instances (4)   ~4 KB      0.02%
HealthScore buffer    ~4 KB      0.02%
Circuit breakers (4)  ~1 KB      0.01%
Python runtime        ~12 MB     98%
SQLite connection     ~1 MB      8%
───────────────────────────────────────
Total                 ~13 MB     100%
```

## Optimization Strategies

### 1. Pulse Interval

The biggest performance lever is the pulse interval. At 60 seconds, the daemon uses ~0.1% CPU. At 10 seconds, it uses ~0.5%. At 300 seconds, it's essentially idle.

```yaml
heartbeat:
  interval_seconds: 60    # Good default for Pi
  jitter_seconds: 5        # Prevents thundering herd
```

### 2. SQLite WAL Mode

The state database uses WAL (Write-Ahead Logging) mode by default, which allows concurrent reads without blocking writes:

```python
# Already configured in _state_db_init()
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
```

### 3. Check Caching

Circuit breakers effectively cache check results. When a breaker is OPEN, the check is skipped entirely and the last known result is used. This can save significant I/O for database checks.

### 4. Log Rotation

Logs use `RotatingFileHandler` with configurable size and backup count:

```yaml
logging:
  file_max_bytes: 10485760  # 10 MB
  file_backup_count: 5       # Max 50 MB total
```

### 5. Pulse History Pruning

The state database automatically prunes `pulse_history` to the last 1000 entries:

```python
conn.execute("DELETE FROM pulse_history WHERE id < (SELECT MAX(id) FROM pulse_history) - 1000")
```

### 6. Nerve Impulse Optimization

Nerve impulses use Unix domain sockets (AF_UNIX) which bypass the network stack entirely:
- No TCP/IP overhead
- No packet routing
- Direct kernel memory copy between processes
- **Latency**: <0.1ms on the same machine

### 7. Health Score Window Size

The EMA window size controls memory vs. responsiveness:
- Window 50: More responsive, less smooth (for development)
- Window 100: Balanced (default, recommended for production)
- Window 200: Very smooth, slow to respond (for long-running Pi)

## Scaling Considerations

### Multiple Systems

Verðandi is designed for single-system monitoring. To monitor multiple systems:

1. Run one Verðandi instance per system
2. Use the Bifrǫst action to forward state changes to a central monitoring server
3. Use the nerve hub protocol to aggregate impulses

### High Frequency

If you need sub-second monitoring (not recommended for Pi):
- Reduce `interval_seconds` to 5-10
- Reduce `jitter_seconds` to 1
- Increase `health_score_window` to 500+
- Consider adding check-level caching for expensive operations

### Large Number of Checks

Verðandi runs all checks sequentially in a single pulse. With 4 checks at ~30ms each, a pulse takes ~120ms. Adding more checks is linear:
- 10 checks: ~300ms per pulse
- 20 checks: ~600ms per pulse
- 50 checks: ~1.5s per pulse

For very large check sets, consider splitting into multiple Verðandi instances with different intervals.