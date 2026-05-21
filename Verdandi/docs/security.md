# 🛡️ Security Considerations

## Threat Model

Verðandi Heartbeat runs as the local user on a single system. Its threat model is:

| Threat Level | Description | Mitigation |
|-------------|-------------|------------|
| **Low** | Someone reads the nerve feed | No sensitive data in impulses |
| **Medium** | Someone modifies the config | Config file permissions (0600) |
| **High** | Someone replaces the binary | Binary verification (future) |
| **Critical** | Someone exploits a check/action | Circuit breakers, dry-run mode |

## Security Properties

### 1. No Network Listening

The daemon does NOT listen on any network port. All communication is via:
- Unix domain sockets (filesystem permission model)
- Local SQLite database (filesystem permission model)
- Local JSONL files (filesystem permission model)

This means Verðandi is **not attackable from the network** by default.

### 2. Filesystem-Based Security

Since all communication is filesystem-based, filesystem permissions are the primary security boundary:

```bash
# Set restrictive permissions on sensitive files
chmod 600 ~/.hermes/state/heartbeat.yaml   # Config may contain paths
chmod 600 ~/.hermes/state/heartbeat.db      # State database
chmod 700 ~/.hermes/state/                   # Directory
```

### 3. No Authentication in Nerve Hub

The nerve hub socket does not authenticate clients. Any local process can connect and read/write impulses. This is **by design** — the nerve hub is a trusted local bus.

If you need authentication, add a proxy layer that validates connections before forwarding to the socket.

### 4. Action Safety

Actions are the most security-sensitive part of the system:

- **Dry-run mode** (`reactor.dry_run: true`): Actions are not executed, only logged
- **Circuit breakers**: Prevent action loops
- **Cooldowns**: Prevent rapid repeated actions
- **No `sudo`**: Actions run as the daemon's user, no privilege escalation

### 5. Eir Auto-Heal Safety

The Eir auto-heal action makes copies before modifying databases:

```python
# Safety: Copy → Modify → Verify (never modify in-place)
db_path.copy(recover_path)  # Backup first
# ... repair ...
integrity = conn.execute("PRAGMA integrity_check").fetchone()
if integrity[0] != "ok":
    # Restore from backup
    recover_path.copy(db_path)
    return False
```

## Best Practices

1. **Run as a non-root user** — the daemon never needs root
2. **Set file permissions** — 600 for config/DB, 700 for state directory
3. **Use dry-run mode** when first enabling the reactor
4. **Review cooldown settings** — prevent action spam
5. **Audit the nerve feed** periodically for unexpected state changes
6. **Don't expose the socket** to network shares or containers without a proxy