# Ember on a Raspberry Pi 5 — install

**Audience:** an operator who wants a small local AI companion running on
a Pi 5 they already own.
**Hardware:** Raspberry Pi 5 with **8 GB RAM** (recommended) or 4 GB
(possible; pick a smaller Funi). 64-bit Raspberry Pi OS (Bookworm) or
Ubuntu Server 24.04+.
**Time:** 20–40 minutes, mostly waiting on the model download.

This is the first-slice install guide. It walks the *standard* happy
path; the **Advanced** section at the end covers Ollama on a non-default
endpoint (e.g. Tailnet-bound).

---

## 1. Prerequisites — Ollama

Ember talks to a local LLM through Ollama. Install Ollama first; verify
it runs.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The installer creates an `ollama` system user, installs the binary to
`/usr/local/bin/ollama`, and starts a systemd service bound to
`localhost:11434`.

Pull the two models Ember expects by default:

```bash
ollama pull phi3:mini          # ~2.3 GB — the reasoning model (Funi)
ollama pull nomic-embed-text   # ~274 MB — the embedding model (Smiðja)
```

Verify both are present:

```bash
ollama list
# Expect: phi3:mini and nomic-embed-text:latest
```

On a Pi 5 (8 GB) with `phi3:mini`, an `ollama run phi3:mini` warm-up
takes ~30 seconds the first time and ~5 seconds afterward.

---

## 2. Install Ember

Ember is a single Python package. Python 3.11 or newer is required.

```bash
python3 -m venv ~/.ember-venv
source ~/.ember-venv/bin/activate
pip install --upgrade pip
pip install "ember-agent[sqlite_vec]"
```

The `[sqlite_vec]` extra pulls in `sqlite-vec`, the vector-storage
extension. Without it, Ember's default Brunnr cannot open.

> If `ember-agent` is not yet on PyPI for the version you want, install
> from this repository:
>
> ```bash
> pip install "git+https://github.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster.git@development#egg=ember-agent[sqlite_vec]"
> ```

Verify:

```bash
ember --help
```

---

## 3. First run — Hjarta

```bash
ember chat
```

On a fresh host, Ember notices `~/.ember/identity/` is missing and runs
the **Hjarta** first-run wizard. It will:

1. **Greet** — press Enter.
2. **Choose Funi** — press Enter to use Ollama.
3. **Discover Funi** — Ember probes `localhost:11434` and confirms
   the model is reachable.
4. **Choose Well** — press Enter to use the default SQLite file at
   `~/.ember/well/store.db`, or type a different path.
5. **Configure Well** — Ember opens the SQLite file (creates the
   directory if needed).
6. **Test retrieval** — Ember writes a tiny probe chunk and confirms
   it can read it back. *This leaves one harmless probe chunk in your
   Well; you can delete it later if you want.*
7. **Name Ember** — press Enter to keep `Ember`, or type your own name
   (e.g. `Spark`, `Sigrún`, `Hugin`).
8. **Write identity** — Ember writes
   `~/.ember/identity/identity.json` *atomically*; nothing on disk
   until this last step.
9. **Done** — Ember is ready.

If the wizard fails at any earlier step, **no files are written.** Fix
the cause (usually `Funi unavailable` = Ollama not running) and re-run.

---

## 4. Give Ember something to read

```bash
ember well ingest ~/notes/
```

Ember walks the directory, finds `.md` / `.txt` / `.json` / `.jsonl` /
`.yaml` files, chunks them, embeds the chunks via Ollama, and writes
them into the Well. Progress is journalled at
`~/.ember/state/smidja_progress/` — if the Pi reboots mid-ingest, the
same command resumes from where it died.

Expect roughly 10–20 chunks per second on a Pi 5 (most of the time is
spent in `nomic-embed-text`, not Ember).

Check the result:

```bash
ember well status
# Well (sqlite_vec):
#   documents:        12
#   chunks:           163
#   embedded chunks:  163
#   size on disk:     5.4 MB
#   last successful probe: 2026-05-21T11:48:03+00:00
```

---

## 5. Talk to Ember

```bash
ember chat
> What do my notes say about Odin?
[Ember answers, with `citations:` listing the documents she pulled from.]
> /exit
```

To ask one question and exit:

```bash
ember ask "What do my notes say about Odin?"
```

If the Well is unreachable mid-conversation (DB file moved, disk full,
network share unmounted on a future remote-Well config), Ember does not
crash. Every ungrounded reply is **prefixed with a `[well: disconnected]`
banner** so you can see when grounding is unavailable. This is the Vow
of Graceful Offline made visible at the terminal.

---

## 6. Health check

```bash
ember doctor
# Ember health:
#   Funi:    ok — model phi3:mini, last_ok 2026-05-21T11:48:03+00:00
#   Well:    ok — backend sqlite_vec, 12 docs / 163 chunks, last_ok 2026-05-21T11:48:03+00:00
```

`ember doctor` exits 0 when both realms are healthy; non-zero if either
fails. Useful as a systemd `ExecStartPre=` if you supervise Ember as a
service.

---

## 7. Editing `ember.yaml` (slice 2)

Hjarta wrote `~/.ember/config/ember.yaml` at first run. Every key is
optional; absent keys fall through to the slice-shipped defaults in
`src/ember/schemas/config.py`. Re-running `ember chat` after an edit
picks up the new values immediately (no daemon to restart).

A copy of the full template lives at
[`config/ember.example.yaml`](../../config/ember.example.yaml) in the
source tree — copy any section out of it.

**Tip:** edit one thing at a time and verify with `ember doctor` after.
A broken yaml fails loud with a clear error and Ember refuses to start
rather than running on partial config.

---

## 8. Streaming on / off (slice 2 — 0.1.7)

Default is **on**: tokens appear in `ember chat` as Funi generates
them. Ctrl-C mid-stream tags the partial reply with
`[interrupted by operator]` and returns to the next prompt — the REPL
keeps going.

To turn streaming off (e.g. when piping `ember ask "…"` into another
tool that wants a single blob):

```yaml
funi:
  streaming: false
```

The non-streaming path uses the same Funi backend; only the surface
behaviour differs.

---

## 9. Switching to a shared Well (`pgvector`, slice 2 — 0.1.9)

Default Well is single-file `sqlite_vec`. If you have a Postgres +
pgvector instance on your tailnet (e.g. Gungnir), point Ember at it
instead:

1. Install the pgvector extra:

   ```bash
   pip install 'ember-agent[pgvector]'
   ```

2. Put your Well password in a mode-`0o600` file:

   ```bash
   mkdir -p ~/.ember/secrets
   chmod 700 ~/.ember/secrets
   editor ~/.ember/secrets/well.password
   chmod 600 ~/.ember/secrets/well.password
   ```

3. Edit `~/.ember/config/ember.yaml`:

   ```yaml
   brunnr:
     backend: pgvector
     embedding_dim: 768          # must match chunks.embedding dim
     pgvector:
       url: "postgresql://volmarr@gungnir/knowledge"
       secret_ref: "~/.ember/secrets/well.password"
       schema: public
       read_only: true   # IMPORTANT for shared Wells you don't own
   ```

4. Verify with `ember doctor` — the Well line will now say
   `backend pgvector`.

The pgvector adapter is schema-probe-first: if the configured schema
already holds `documents` + `chunks` tables (the Gungnir shape), Ember
reuses them. If they don't exist, Ember runs the DDL on first open.
**Set `read_only: true`** when pointing at a database you didn't
bootstrap — it mechanically refuses `add_document` / `add_chunks` /
`add_episode`.

Operator guide with every knob: `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`.
Design rationale: `docs/decisions/0010-pgvector-brunnr.md`.

---

## 10. Enabling tools (slice 2 — 0.2.0)

Default is **off** per the Vow of Sovereignty. To enable:

```yaml
tools:
  enabled: true
```

Or as a per-invocation override:

```bash
ember --allow-tools chat
ember --no-tools chat   # force off even when config says on
```

Three first-party tools ship in 0.2.0:

| Tool | Approval | What it does | Refuses |
|---|---|---|---|
| `search_well` | `STANDING` (auto) | hybrid_search against the bound Well | empty query, dim mismatch |
| `read_local_file` | `PER_CALL` | read a UTF-8 file under `$HOME` | paths outside `$HOME`, `~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, files > 256 KiB |
| `fetch_url` | `PER_CALL` | GET an http(s) URL via stdlib `urllib` | non-http(s) schemes, RFC1918/loopback (unless `allow_private_addresses=true`), robots.txt disallow, response > 1 MiB |

Every tool call is recorded in an append-only JSONL audit log at
`~/.ember/state/tool_audit/<YYYY-MM-DD>.jsonl` — including refusals
and invalid-arguments rejections. Operator guide:
`docs/decisions/0011-tool-use-framework.md`.

### Approval policy (slice 2 — 0.2.0)

When `tools.enabled: true`, Ember asks before every `PER_CALL` tool
invocation:

```
[tool proposal] read_local_file  (call abc12345)
  description: Read a UTF-8 text file from the operator's home directory...
  arguments:
    path: '/home/volmarr/notes/runes.md'
approve this call? [y/n/always]
```

Three answers:

- `y` — approve this call only.
- `always` — approve this tool for the rest of this session (does NOT
  persist; restart resets).
- `n` (or anything else) — refuse. Funi sees a typed error reply and
  usually summarises gracefully.

`STANDING` tools (`search_well`) skip the prompt. To downgrade them to
`PER_CALL`:

```yaml
tools:
  enabled: true
  approval_overrides:
    search_well: per_call    # be strict about search too
```

You can also **forbid** a tool entirely — the registry refuses to even
register it:

```yaml
tools:
  enabled: true
  approval_overrides:
    fetch_url: forbidden
```

To flip the floor and auto-approve **every** `PER_CALL` tool (still
audited):

```yaml
tools:
  enabled: true
  standing_trust: true     # "trust everything" mode
```

The descriptor is the **safety floor** — config can downgrade
`STANDING` → `PER_CALL` (more strict) but cannot upgrade
`PER_CALL` → `STANDING`. Pin the safer direction.

### Tool-capable models

Tools require a Funi runtime that supports OpenAI-style function
calling. On the Ollama side, **not every small model does** — `phi3:mini`
returns HTTP 400 when tools are supplied. **`llama3.2:3b`** is the
recommended tool-capable model for slice 2 on Pi-class hardware:

```bash
ollama pull llama3.2:3b
```

```yaml
funi:
  ollama:
    model: "llama3.2:3b"
```

If you keep `phi3:mini` as your default Funi, set `tools.enabled:
false` (the default) — Ember stays useful without tools.

---

## 11. Update / reset

To re-run the wizard from scratch:

```bash
ember setup --reset
```

To remove Ember entirely:

```bash
pip uninstall ember-agent
rm -rf ~/.ember-venv ~/.ember/
```

The Well file at `~/.ember/well/store.db` contains everything Ember
remembers. **Back it up by copying that file** before deleting the
directory.

---

## Advanced: Ollama on a non-default endpoint

If Ollama is bound to something other than `localhost:11434` — e.g.
because you've put it on a Tailscale interface for cross-device access
— set the `OLLAMA_HOST` environment variable before running Ember:

```bash
export OLLAMA_HOST=100.67.240.22:11434
ember chat
```

`OLLAMA_HOST` accepts the same shapes Ollama's own CLI accepts:

- `localhost`  → `http://localhost:11434`
- `localhost:11434`  → `http://localhost:11434`
- `100.67.240.22`  → `http://100.67.240.22:11434`
- `100.67.240.22:11434`  → `http://100.67.240.22:11434`
- `http://ollama.local:11434`  → preserved
- `https://ollama.example.com:8443`  → preserved

The same value applies to both Funi (the reasoner) and Smiðja (the
embedding endpoint).

A full configuration loader (custom model, custom Brunnr backend,
custom embedding model, custom Smiðja chunker defaults) ships in Phase 9+.
Until then, `OLLAMA_HOST` is the escape hatch for the most common
non-default case.

---

## Advanced: smaller Funi models for 4 GB Pis

The default `phi3:mini` needs ~2.5 GB resident. On a 4 GB Pi 5, you may
want a smaller model:

```bash
ollama pull qwen2.5:1.5b-instruct   # ~1.3 GB resident
```

Set the model under `funi.ollama.model` in
`~/.ember/config/ember.yaml` (see §7-10 above for the editing flow).
`phi3:mini` is the recommended floor for general use; **`llama3.2:3b`
is the recommended floor when you want tool calls** (see §10 for
why).

See [`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`](../../docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md)
for the full host-RAM-keyed model ladder.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ember chat` says `Funi is unavailable (endpoint_unreachable)` | Ollama not running, or bound to a non-default host | `systemctl status ollama`; or set `OLLAMA_HOST`. |
| Hjarta says `well disconnected: backend_reported_unavailable` | `sqlite-vec` extension not installed | `pip install sqlite-vec` in your venv. |
| `ember well ingest` is very slow | Embedding model not loaded; first batch warms it up | Wait — subsequent batches are faster. |
| Reply text ends with `[reply truncated — context limit reached]` | Default `num_predict` is 1024; model wanted more | Edit `funi.ollama.num_predict` in `~/.ember/config/ember.yaml`. |
| `ember doctor` says `Well: ok` but `documents: 1` after a clean install | Hjarta probe left its harmless test chunk | Expected; safe to ignore or delete via SQL. |
| `ember chat` with `tools.enabled: true` returns `[ollama unreachable: HTTP Error 400: Bad Request]` | Your Funi model does not support tool calls | Switch `funi.ollama.model` to `llama3.2:3b` (see §10); or set `tools.enabled: false`. |
| Tool proposal renders but `ember chat` says `refused: path '~/...' is on the sandbox denylist` | Model proposed a path inside the read-only denylist (`~/.ssh/`, `~/.ember/secrets/`, etc.) | Expected sandbox behaviour. Move the file outside the denylist or read it via a different tool. |
| `pip install ember-agent[pgvector]` fails | Postgres client headers missing | `apt install libpq-dev`; or use `psycopg[binary]` which bundles them. |
| `ember doctor` says `Well: DISCONNECTED — auth_failed (no Well secret resolved …)` | pgvector secret file missing or wrong mode | Re-check `~/.ember/secrets/well.password` is mode `0o600` (not `0o644`). |

---

## What's next

The slice-2 release (0.2.0, ratified 2026-05-21 by ADR 0013) shipped:

- The config loader (`~/.ember/config/ember.yaml`) — §7.
- Streaming Funi replies with Ctrl-C-tags-partial — §8.
- `pgvector` Brunnr for Gungnir-compatible shared Wells — §9.
- Tool use: `search_well`, `read_local_file`, `fetch_url` with
  per-call approval + audit log — §10.

Slice 3 is queued (ADR 0012 — alternate surfaces: Auga GUI, Rödd
voice, Bifröst HTTP gateway). It does NOT block any current
deployment; this install guide is feature-complete for slice 2.

The current version is in `pyproject.toml`. Slice ratification ADRs:

- `docs/decisions/0007-first-slice-ratification-2026-05-21.md` — 0.1.0.
- `docs/decisions/0013-second-slice-ratification.md` — 0.2.0.

Welcome to the hearth.
