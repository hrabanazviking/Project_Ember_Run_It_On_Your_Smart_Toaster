# 83 — Screen: Doctor

Cross-realm health snapshot. Funi, Strengr, Brunnr, MCP — each
realm's current state in one place.

---

## Purpose

When something feels wrong (slow reply, missing citations, tool
fail), the operator presses `d` and sees what's actually up.

---

## Layout

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Doctor ─── last probe 8s ago ── 🔥 ─┐
│                                                              │
│  Realm     Status            Detail                          │
│  ────      ──────            ──────                          │
│                                                              │
│  Funi      ● ok              endpoint:  http://100.67.240.22 │
│                              model:     llama3.2:3b           │
│                              tokens/s:  47 (avg last min)     │
│                              last_ok:   2 seconds ago         │
│                                                              │
│  Strengr   ● ok              backend:   sqlite_vec            │
│                              last_ok:   2 seconds ago         │
│                                                              │
│  Brunnr    ● ok              backend:   sqlite_vec            │
│                              documents: 95                    │
│                              chunks:    35,418                │
│                              size:      240 MB                 │
│                              path:      ~/.ember/well/store.db │
│                              last_ok:   2 seconds ago         │
│                                                              │
│  MCP       ● ok              servers:   2 of 2 reachable      │
│                              tools:     12 total              │
│                                                              │
│              ─ filesystem (12 tools, last ping 5s ago)        │
│              ─ github      (8 tools,  last ping 5s ago)       │
│                                                              │
│  r = re-probe · v = view raw response · Esc = home          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
[ ● Funi · ● Well · ● MCP 2/2 ]   [Doctor]   [r · v · Esc · ? · q]
```

When a realm is down:

```
│  Funi      ● UNAVAILABLE     endpoint:  http://100.67.240.22 │
│                              detail:    Connection refused    │
│                              last_ok:   never (this session)  │
│                              try:       r to re-probe; s to   │
│                                         edit settings          │
```

---

## Implementation

`src/ember/stofa/screens/doctor.py` — `DoctorScreen(textual.screen.Screen)`.

Reads from `DoctorService`, which polls each realm at a configurable
interval (default 30 seconds).

The realm rows are rendered via a `DataTable` widget with
column-spanning rows for the detail fields.

---

## Per-realm probes

| Realm | Probe |
|---|---|
| Funi | `funi.health()` — returns FuniHealth or Unavailable |
| Strengr | indirect via Brunnr (open + close test) |
| Brunnr | `brunnr.count()` — returns BrunnrStats |
| MCP | for each server: `MCPClientPool.ping(name)` |

Each probe has a per-realm timeout (5 seconds default). A timeout
counts as the realm being unhealthy (yellow $warning state).

---

## Keybindings

| Key | Action |
|---|---|
| `r` | Re-probe all realms |
| `v` | View raw response (modal showing the FuniHealth / BrunnrStats / etc. as JSON) |
| `Enter` (on a realm row) | Drill into MCP realm: shows per-server details |
| `↑` / `↓` / `j` / `k` | Navigate realm rows |
| `]` / `[` | (V2) cycle right-pane tabs (Details / Logs / Raw) |
| `Esc` | Back to Home |

---

## When a realm is down

The doctor screen explicitly tells the operator how to recover:

- **Funi unavailable:** "Try: r to re-probe; s to edit settings;
  check Ollama is running at <endpoint>."
- **Brunnr disconnected:** "Try: r to re-probe; s to edit
  settings; check the Well path exists."
- **MCP server down:** "Try: m to manage MCP; restart the
  failing server."

These hints are *operator-actionable*, not "an error occurred."

---

## Pet behavior on Doctor

- **Funi-spark** still indicates Funi's current state (idle vs
  active).
- **Hugin** doesn't perch here (no citations).
- **Refur** doesn't appear (no chat approval).
- **Heiðr** doesn't drop horns (no tool calls).
- **Geri-cub** sleeps in the corner.

Doctor is a *calm* screen. Pets are minimal.

---

## The `v` view-raw modal

Pressing `v` on a realm row opens a modal with the raw response:

```
╭── Raw: Funi health ──────────────────────╮
│                                            │
│  {                                         │
│    "ok": true,                             │
│    "backend_kind": "ollama",               │
│    "model_id": "llama3.2:3b",              │
│    "endpoint": "http://100.67.240.22:11434",│
│    "elapsed_ms": 47,                       │
│    "last_ok": "2026-05-21T14:32:18.000Z"   │
│  }                                         │
│                                            │
│  Esc to close                              │
╰────────────────────────────────────────────╯
```

This is the operator's escape into "show me everything." Useful for
debugging or bug-reporting.

---

## What DoctorScreen does NOT do

- **Fix problems.** Doctor surfaces, it doesn't intervene.
  Operator follows the suggested actions.
- **Replace the StatusBar.** StatusBar gives realm states at all
  times; Doctor gives the deeper view.
- **Test connectivity beyond Ember's handles.** No `ping` to
  arbitrary hosts; only the configured realms.

---

## Closing

DoctorScreen is the *truth window*. When something's wrong, it tells
you what and where, with operator-actionable suggestions. When
everything's fine, it confirms — quietly, four green dots, no fuss.
