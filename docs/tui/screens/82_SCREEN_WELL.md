# 82 — Screen: Well

Browse the Well's ingested documents; trigger ingest; see ingest
progress.

---

## Purpose

- Show what's in the operator's knowledge base.
- Let the operator add new documents (ingest a directory).
- Surface ingest progress without leaving the screen.
- (V2) delete documents, re-ingest specific paths.

---

## Layout

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Well ─── 95 docs · 35K chunks · 240MB ── 🔥 ─┐
│                                                                       │
│  ┌── Sources ───────────┐  ┌── Selected: odin.md ─────────────────┐  │
│  │                       │  │                                       │  │
│  │  notes/                │  │  Title:    odin.md                    │  │
│  │  ▶ odin.md             │  │  Source:   /home/volmarr/notes/odin.md │  │
│  │    yggdrasil.md       │  │  Type:     md                         │  │
│  │    cooking.md         │  │  Hash:     abc12345                   │  │
│  │  research/             │  │  Chunks:   23                         │  │
│  │    ai_safety.pdf      │  │  Size:     12,489 bytes               │  │
│  │    embeddings.md      │  │  Ingested: 2026-05-20 17:45:33 UTC    │  │
│  │  code/                 │  │                                       │  │
│  │    repos.md            │  │  Recent excerpt:                      │  │
│  │    tools.md            │  │                                       │  │
│  │  ...                   │  │   "Odin (Old Norse: Óðinn) is the    │  │
│  │                       │  │   principal god of the Norse..."     │  │
│  │                       │  │                                       │  │
│  └───────────────────────┘  │  i = ingest · r = re-ingest · / search│  │
│                              └───────────────────────────────────────┘  │
│                                                                       │
│                              [Sumarbýfa during ingest]                │
└───────────────────────────────────────────────────────────────────────┘
[ ● Well 95 docs · ingest idle ]   [Well]   [i/r//=actions · Esc=home]
```

When ingest is running:

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Well ───── INGEST RUNNING ────── 🔥 ─┐
│                                                                │
│  Ingesting: /home/volmarr/notes/2026-research/                 │
│                                                                │
│  Progress: ████████████▆___________________________ 32/97 docs │
│                                                                │
│  Currently: ai-safety-paper-014.pdf                             │
│                                                                │
│  Skipped 3 files (sensitive-name denylist)                     │
│  Skipped 1 file (binary content)                               │
│                                                                │
│  Press Esc to leave screen (ingest continues in background)    │
│  Press Ctrl-C to cancel ingest                                  │
│                                                                │
│              [Sumarbýfa flies left-right ferrying]             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation

`src/ember/stofa/screens/well.py` — `WellScreen(textual.screen.Screen)`.

Composes:
- `SourcesPanel` (left, fixed 30 cells).
- `DetailsPanel` (right, 1fr).
- An overlay `IngestProgressView` when ingest is running (replaces
  details panel temporarily).

---

## Keybindings

| Key | Action |
|---|---|
| `j` / `↓` | Navigate down in sources |
| `k` / `↑` | Navigate up in sources |
| `Enter` | Open document detail (no-op since detail is always shown) |
| `i` | Ingest a path (prompts for path) |
| `r` | Re-ingest selected document |
| `/` | Filter sources by name |
| `1` | Sort by name |
| `2` | Sort by ingest date |
| `3` | Sort by chunk count |
| `Delete` | Delete selected (with confirm) |
| `Esc` | Back to Home |

---

## The ingest flow

Operator presses `i`:

1. A modal appears: "Path to ingest: [____]"
2. Operator types a path; Enter.
3. ChatScreen pushes IngestProgressView in place of details panel.
4. `WellService.ingest(path)` starts in background.
5. Progress messages stream in; bar updates; current file shown.
6. Skipped files counted (sensitive-name + non-text + oversize).
7. When done: success summary, returns to normal layout.
8. SourcesPanel refreshes (new documents appear).

---

## The Sumarbýfa pet during ingest

- Appears at the top of the chrome (or wherever the operator can
  see it; pets are global-overlay).
- Animates left-right ferry motion at ~1 Hz.
- Stays visible across screens (operator can press `c` to chat
  while ingest continues — bee still visible).
- Disappears when ingest finishes.

---

## SourcesPanel internals

- Tree-view of documents organized by their `source` path prefix
  (heuristic: split on `/` to derive folders).
- Each row: filename + content-type indicator + chunk-count.
- Focused row has $accent border.
- Filter (`/`) narrows in real time.
- Sort options change ordering.

```
notes/                           ← folder header (collapsible later)
▶ odin.md           md   23      ← focused
  yggdrasil.md      md    8
  cooking.md        md   12
research/
  ai_safety.pdf     pdf  45      ← future: pdf support
  embeddings.md     md   31
```

---

## DetailsPanel internals

Shows metadata + recent excerpt for the focused document.

Sections:
- **Identity:** title, source, hash, type.
- **Statistics:** chunk count, size, ingest timestamp.
- **Recent excerpt:** the first ~5 lines of the first chunk.
- **Hints:** what keys do here.

Tabs (V2): operator can press `]` to cycle to:
- **Recent excerpt** (default).
- **Chunks** (paginated list of all chunks).
- **Audit** (the audit log entries for this document).

---

## Empty state

```
┌── Sources ───────────┐
│                       │
│  Your Well is empty.  │
│                       │
│  Press i to ingest a  │
│  directory.           │
│                       │
│  Or run:              │
│    ember well ingest  │
│    <path>             │
│                       │
└───────────────────────┘
```

---

## What WellScreen does NOT do

- **View chunk embeddings.** Debug-only; not in V1.
- **Edit documents.** Documents are ingested artifacts; the
  operator edits source files outside Stofa, then re-ingests.
- **Manage Brunnr backend.** That's in Settings.
- **Search the well's content.** That's what chat does. WellScreen's
  `/` filters by filename only.

---

## Closing

WellScreen is the operator's window into their knowledge base. Two
panes: what's there (sources) and what's selected (details). One
key for ingest. Sumarbýfa makes the work visible. Operators with
a long Stofa session check WellScreen periodically as their corpus
grows.
