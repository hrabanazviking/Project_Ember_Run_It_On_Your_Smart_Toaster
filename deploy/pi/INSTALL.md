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

## 7. Update / reset

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

Until the config loader lands, edit Ember's behaviour by passing a
different `EmberConfig` to the CLI dispatcher. For most operators this
means waiting for Phase 9+; for now, `phi3:mini` is the recommended
floor.

See [`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`](../../docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md)
for the full host-RAM-keyed model ladder.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ember chat` says `Funi is unavailable (endpoint_unreachable)` | Ollama not running, or bound to a non-default host | `systemctl status ollama`; or set `OLLAMA_HOST`. |
| Hjarta says `well disconnected: backend_reported_unavailable` | `sqlite-vec` extension not installed | `pip install sqlite-vec` in your venv. |
| `ember well ingest` is very slow | Embedding model not loaded; first batch warms it up | Wait — subsequent batches are faster. |
| Reply text ends with `[reply truncated — context limit reached]` | Default `num_predict` is 1024; model wanted more | Operator-tunable in Phase 9+; for now, ask more focused questions. |
| `ember doctor` says `Well: ok` but `documents: 1` after a clean install | Hjarta probe left its harmless test chunk | Expected; safe to ignore or delete via SQL. |

---

## What's next

- **Phase 9+** brings a real config file loader, `pgvector` Brunnr for
  shared household Wells (Gungnir-compatible), and more Funi runtimes
  (`llamacpp`, `lmstudio`, Windows AI Foundry, Apple Foundation Models).
- The first slice that ships with this install guide is `0.1.0`. See
  `pyproject.toml` for the current version.

Welcome to the hearth.
