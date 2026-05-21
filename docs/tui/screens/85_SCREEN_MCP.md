# 85 — Screen: MCP

Manage external MCP servers. View tools each server provides. Ping
servers. Adjust auto-approve.

---

## Purpose

MCP servers are external processes Stofa spawns + talks to. The
operator needs a place to:
- See what's running.
- See what tools each provides.
- Restart / ping failing servers.
- Tune auto-approve per tool.

---

## Layout

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── MCP ──── 2/2 servers · 12 tools ── 🔥 ─┐
│                                                                 │
│  Server          Status        Tools   Last ping                │
│  ──────          ──────        ─────   ─────────                │
│                                                                 │
│  ▶ filesystem    ● ok          12      2s ago                   │
│    github        ● ok          8       5s ago                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  filesystem tools (12):                                         │
│                                                                 │
│    [ ] read_file              standing-approve: ☐               │
│    [ ] write_file             standing-approve: ☐               │
│    [✓] list_directory         standing-approve: ✓ (your config) │
│    [ ] search                 standing-approve: ☐               │
│    [ ] grep                   standing-approve: ☐               │
│    ... (7 more)                                                 │
│                                                                 │
│  a = add server · p = ping selected · r = restart · l = logs   │
│  Space = toggle auto-approve (on selected tool row)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
[ ● MCP 2/2 ]   [MCP]   [a · p · r · l · Esc · ? · q]
```

---

## Implementation

`src/ember/stofa/screens/mcp.py` — `MCPScreen(textual.screen.Screen)`.

Composes:
- `ServerList` (top-left) — selectable list of configured servers.
- `ToolsList` (below) — tools of the focused server, with
  auto-approve checkboxes.

Reads from `MCPService` (which wraps the existing `MCPClientPool`).

---

## Per-server display

Each server row shows:
- Status dot (color-coded).
- Name.
- Tool count.
- Last successful ping timestamp.

Status meanings:
- ● $success — running, last ping succeeded.
- ● $warning — running but last ping is stale (>60s).
- ● $error — down (spawn failed or recent ping failed).

---

## Keybindings

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate servers |
| `Tab` | Move focus to tools list |
| `a` | Add new server (opens modal) |
| `p` | Ping selected server (forces a fresh probe) |
| `r` | Restart selected server (kill + respawn) |
| `l` | View server's stdout/stderr logs (modal) |
| `Space` (on tool row) | Toggle auto-approve for that tool |
| `Delete` | Remove server from config (with confirm) |
| `Esc` | Back to Home |

---

## Adding a server (`a`)

A modal:

```
╭── Add MCP server ──────────────────────────╮
│                                              │
│  Name:    [ filesystem                    ]  │
│  Command: [ npx                           ]  │
│  Args:    [ -y                              │
│             @modelcontextprotocol/server-fs │
│             /home/me/notes                ]  │
│                                              │
│  Env:                                        │
│    (key) [ ___________ ] = [ ____________ ] │
│    + add another                             │
│                                              │
│  s = save and spawn · esc = cancel          │
╰──────────────────────────────────────────────╯
```

On save:
1. Write the server to `ember.yaml` under `mcp.servers`.
2. Spawn via `MCPClientPool.add_server()` (V2 feature; for V1 may
   require restart).
3. Refresh the server list.

---

## Restart flow (`r`)

Operator presses `r` on a failing server:

1. Show confirm: "Restart server 'filesystem'? (y/n)"
2. On y: `MCPClientPool.restart(name)` — closes the existing
   session, spawns a fresh subprocess, re-initializes.
3. Status updates as the operation completes.

---

## Logs (`l`)

Modal showing the server's recent stdout/stderr:

```
╭── filesystem logs ──────────────────────────╮
│                                              │
│  2026-05-21 14:30:15 INFO server starting   │
│  2026-05-21 14:30:15 INFO registered tools: │
│    read_file, write_file, list_directory,   │
│    ... (9 more)                              │
│  2026-05-21 14:30:16 INFO ready             │
│                                              │
│  Esc to close                                │
╰──────────────────────────────────────────────╯
```

V1 may show only last-N-lines from the spawned process's output;
V2 with full log capture.

---

## Auto-approve toggle (`Space`)

Operator focuses a tool row, presses Space. The checkbox flips.
The change writes to `ember.yaml` immediately:

```yaml
mcp:
  servers:
    - name: filesystem
      command: npx
      args: [-y, "@modelcontextprotocol/server-fs", /home/me/notes]
      auto_approve:
        - list_directory       # ← just added
```

A `[✓]` next to a tool means: in chat, that tool's approval policy
is STANDING (auto-approve every call).

A `[ ]` means PER_CALL (the operator gets prompted each time).

---

## Pet behavior on MCP

- **Funi-spark** still indicates Funi's current state.
- **Other pets** are minimal here (no retrieval, no chat, no
  ingest).
- **Geri-cub** sleeps.

---

## Empty state

```
┌── No MCP servers configured ────────────────────────┐
│                                                      │
│  Press a to add your first MCP server.               │
│                                                      │
│  Or edit ember.yaml under `mcp.servers:`.            │
│                                                      │
│  Suggested first server: filesystem                  │
│    npx -y @modelcontextprotocol/server-filesystem    │
│                                                      │
│  See https://modelcontextprotocol.io/servers for     │
│  more.                                                │
└──────────────────────────────────────────────────────┘
```

---

## What MCPScreen does NOT do

- **Browse a marketplace of MCP servers.** V2 reserved.
- **Install MCP servers via npm/pip.** Operator handles install;
  Stofa only spawns.
- **Edit per-tool descriptors.** Descriptors come from the MCP
  server itself; Stofa is read-only on them.
- **Replace Settings for MCP config.** Settings has the full
  config dataclass; MCPScreen is the runtime-view counterpart.

---

## Closing

MCPScreen is where operators **see what tools Ember has** and
**manage the bridges to the wider MCP ecosystem**. Server list,
per-tool auto-approve, ping/restart, logs. A small dashboard for
the part of Ember that grows by plugin.
