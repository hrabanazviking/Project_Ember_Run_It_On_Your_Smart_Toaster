# 🌐 Cross-Platform Guide

## Supported Platforms

Verðandi Heartbeat runs on any Python 3.9+ system. The following platforms are tested:

| Platform | Status | Notes |
|----------|--------|-------|
| Raspberry Pi OS (Linux ARM) | ✅ Primary | Born on Pi, best experience |
| Ubuntu/Debian (Linux x86) | ✅ Supported | Full functionality |
| macOS (Darwin) | ✅ Supported | Full functionality, no thermal data |
| WSL (Windows Subsystem for Linux) | ⚠️ Partial | No PID files, no systemd |
| Windows (native) | ⚠️ Partial | No Unix sockets, no signals |

## Path Resolution

Verðandi uses XDG-compliant path resolution with fallbacks:

```python
# Priority order:
# 1. Environment variable (VERDANDI_STATE_DIR, etc.)
# 2. XDG specification (XDG_STATE_HOME, XDG_CONFIG_HOME, etc.)
# 3. Platform-specific defaults

# Linux:
#   state: ~/.local/state/hermes/
#   config: ~/.config/hermes/
#   data: ~/.local/share/hermes/

# macOS:
#   state: ~/Library/Application Support/hermes/state/
#   config: ~/Library/Application Support/hermes/config/
#   data: ~/Library/Application Support/hermes/

# Fallback (all platforms):
#   state: ~/.hermes/state/
#   config: ~/.hermes/config/
#   data: ~/.hermes/data/
```

## Platform-Specific Behavior

### Raspberry Pi (Linux ARM)

- **Thermal data**: Reads `/sys/class/thermal/thermal_zone0/temp`
- **systemd**: Full service support with `systemctl --user`
- **PID file**: `~/.hermes/state/run/verdandi-heartbeat.pid`
- **Socket**: `~/.hermes/state/runa.sock`

### macOS (Darwin)

- **Thermal data**: Not available from sysfs. Use `sudo powermetrics --samplers thermal` or skip thermal checks
- **LaunchAgent**: Use `launchctl` instead of `systemctl` (see below)
- **PID file**: Supported in `~/.hermes/state/run/`

### WSL (Windows Subsystem for Linux)

- **systemd**: May not be available (depends on WSL version)
- **PID file**: Supported but may not survive WSL restart
- **Socket**: Unix domain sockets work in WSL2

### Windows (Native)

- **Socket**: No Unix domain sockets. Falls back to file-based nerve feed
- **Signals**: No POSIX signals. Use Ctrl+C for shutdown
- **PID file**: Uses `tempfile` instead of `/run`
- **Paths**: Uses `%APPDATA%\hermes\state\` instead of `~/.hermes/state/`

## LaunchAgent for macOS

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.verdandi.heartbeat</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/verdandi-heartbeat</string>
        <string>pulse</string>
        <string>--loop</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/verdandi-heartbeat.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/verdandi-heartbeat.out</string>
</dict>
</plist>
```

Install:
```bash
cp com.verdandi.heartbeat.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.verdandi.heartbeat.plist
```

## Docker (Experimental)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
VOLUME /root/.hermes/state
CMD ["verdandi-heartbeat", "pulse", "--loop"]
```

```bash
docker build -t verdandi-heartbeat .
docker run -d --name verdandi \
  -v ~/.hermes/state:/root/.hermes/state \
  verdandi-heartbeat
```