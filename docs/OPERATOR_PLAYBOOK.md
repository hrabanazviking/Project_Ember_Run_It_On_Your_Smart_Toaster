# OPERATOR_PLAYBOOK — Slice-2 recipes for living with Ember

**Voice:** Cartographer (Védis Eikleið), with Forge Worker (Eldra Járnsdóttir)
**Status:** Living document. Recipes added as operators contribute them.
**Last touched:** 2026-05-21 (post-slice-2 ratification)
**Reads with:** `deploy/pi/INSTALL.md` (the install + capability walkthroughs); `docs/adapters/*` (per-adapter operator references); `docs/SYSTEM_VISION.md` §11 (the Vows mapped to shipped code).

---

## Who this document is for

Operators who have Ember installed (per `deploy/pi/INSTALL.md`) and
want recipes for the common things they'll actually want to do.
Each recipe is structured the same way:

- **What you want** — the operator-facing goal.
- **What you'll edit** — the file(s) you'll touch.
- **The recipe** — copy-paste yaml / commands.
- **Verification** — how to confirm it worked.
- **What could go wrong** — the operator-facing failure modes.

If your goal isn't here, file an issue with what you wanted to do and
where you got stuck. The shape of this playbook grows by what
operators actually need.

---

## Recipe 1 — Point Ember at your tailnet Ollama

**What you want:** Ollama runs on another machine (a workstation in
your closet, a small server, etc.) and you want Ember on your Pi to
use *that* model, not a Pi-local copy.

**What you'll edit:** `~/.ember/config/ember.yaml`.

**The recipe:**

```yaml
funi:
  ollama:
    base_url: "http://100.67.240.22:11434"   # your tailnet Ollama host
    model: "llama3.2:3b"                     # whatever you pulled there
```

OR, as a per-invocation override that doesn't touch the yaml:

```bash
OLLAMA_HOST=http://100.67.240.22:11434 ember chat
```

(The env-var path was the Phase-7 escape hatch; it still works and is
fine for ad-hoc use. The config-file path is right for permanent
setups.)

**Verification:** `ember doctor` will show
`Funi: ok — model llama3.2:3b, last_ok 2026-05-21T...`.

**What could go wrong:**

- **`Funi is unavailable (endpoint_unreachable)`** — the URL doesn't
  resolve or refuses connection. Check Tailscale, check `ollama
  serve` is running on the remote host bound to `0.0.0.0:11434` (not
  just `localhost`).
- **`endpoint_unreachable` only when tools are enabled** — the model
  you pointed at can't do tool calls. Switch to `llama3.2:3b` or
  disable tools.

---

## Recipe 2 — Switch to a shared Gungnir-shape Well

**What you want:** You already have a Postgres + pgvector instance
holding ingested content (your own Gungnir, or a household shared
Well). You want Ember to query it instead of its local `sqlite_vec`
copy.

**What you'll edit:** `~/.ember/config/ember.yaml` + create
`~/.ember/secrets/well.password`.

**The recipe:**

```bash
# 1. Install the pgvector extra.
pip install 'ember-agent[pgvector]'

# 2. Put your Well password in a mode-0o600 file.
mkdir -p ~/.ember/secrets
chmod 700 ~/.ember/secrets
$EDITOR ~/.ember/secrets/well.password
chmod 600 ~/.ember/secrets/well.password
```

```yaml
# 3. Edit ~/.ember/config/ember.yaml — replace the brunnr block:
brunnr:
  backend: pgvector
  embedding_dim: 768          # must match chunks.embedding dim
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"
    schema: public
    read_only: true   # IMPORTANT if you don't own this database
```

**Verification:** `ember doctor` will show
`Well: ok — backend pgvector, N docs / M chunks, last_ok 2026-05-21T...`
with the real counts from the target database.

**What could go wrong:**

- **`Well: DISCONNECTED — auth_failed (no Well secret resolved …)`**
  — secret file missing, wrong permissions, or empty. Re-check
  `chmod 600 ~/.ember/secrets/well.password`.
- **`Well: DISCONNECTED — backend_reported_unavailable (chunks.embedding
  has dim X, config.embedding_dim is Y)`** — the database was
  populated with a different embedding model. Match
  `embedding_dim` to what's actually in the target chunks, OR re-
  ingest with the matching dim.
- **`backend_reported_unavailable (pgvector extension missing and
  read_only=true)`** — your `read_only` mode refuses to install the
  pgvector extension. Either set `read_only: false` (if you own the
  DB) or have the DB owner run `CREATE EXTENSION vector` once.
- **Cannot mutate the discovered schema.** This is *by design* —
  `read_only: true` mechanically refuses `add_document` /
  `add_chunks` / `add_episode`. Switch to `read_only: false` if you
  want to write to this Well.

---

## Recipe 3 — Enable tool use safely

**What you want:** You want Ember to be able to read files,
search the Well via a tool, and fetch URLs — but you want to
approve every call until you trust each tool.

**What you'll edit:** `~/.ember/config/ember.yaml`. Plus possibly
`funi.ollama.model` (slice-2 caveat).

**The recipe:**

```yaml
# 1. Make sure you're on a tool-capable model. phi3:mini cannot do
#    tool calls; llama3.2:3b can.
funi:
  ollama:
    model: "llama3.2:3b"      # pull with: ollama pull llama3.2:3b

# 2. Enable tools — default is off (Vow of Sovereignty).
tools:
  enabled: true               # default false; this opts in
  standing_trust: false       # default — you'll be asked per call
```

That's it for "I want tools, I'll approve each call". When you run
`ember chat` you'll see:

```
[tool proposal] read_local_file  (call abc12345)
  description: Read a UTF-8 text file from the operator's home directory...
  arguments:
    path: '/home/you/notes/runes.md'
approve this call? [y/n/always]
```

Answer `y` to approve once, `n` to refuse, or `always` to grant
session-level standing trust to that tool (resets at restart).

**Verification:** `ember --allow-tools chat` always shows tools
enabled regardless of config (good for one-off testing).
`ember doctor` does not yet report tool state (slice-3 candidate).
The audit log at `~/.ember/state/tool_audit/<YYYY-MM-DD>.jsonl` shows
every call.

**What could go wrong:**

- **`HTTP Error 400: Bad Request`** — your Funi model doesn't support
  tool calls. Pull `llama3.2:3b` and switch (see Recipe 1).
- **`[tool refused: operator denied] read_local_file`** — you said
  `n`. That's working as intended. Funi sees the refusal as a typed
  error and usually explains gracefully on the next turn.
- **`[tool refused: invalid arguments] read_local_file`** — the
  model proposed arguments that don't match the descriptor's
  schema. Often a sign of model hallucination; just say `n` (you
  won't be asked anyway — invalid-args short-circuits the prompt).
- **`[tool refused: path '~/.ssh/id_rsa' is on the sandbox denylist]`** —
  the sandbox caught the proposal before execution. Expected
  behaviour; move the file you want to read outside the denylist or
  refuse the call.

---

## Recipe 4 — Audit what tools have done

**What you want:** See every tool call Ember made, including refusals
and invalid-args rejections.

**What you'll edit:** Nothing — just read.

**The recipe:**

```bash
# Today's calls:
cat ~/.ember/state/tool_audit/$(date +%Y-%m-%d).jsonl | jq

# All search_well calls in the last week:
for day in $(seq -w 0 6); do
  date_str=$(date -d "-${day} days" +%Y-%m-%d)
  f=~/.ember/state/tool_audit/${date_str}.jsonl
  test -f "$f" && jq 'select(.tool == "search_well")' "$f"
done

# Just the refusals:
jq 'select(.approval | startswith("denied") or . == "invalid_arguments" or . == "no_such_tool")' \
  ~/.ember/state/tool_audit/*.jsonl
```

**Verification:** every approved tool call appears as a JSON record
with `tool`, `call_id`, `arguments`, `approval`, `reply` (with
`output`, `error`, `elapsed_s`). Refused calls have no `reply` field
(the tool wasn't actually executed).

**What could go wrong:**

- **No audit files yet** — `tools.enabled: false` (the default), or
  no tool calls have happened yet. Either is fine.
- **Audit file too large to skim** — slice-2 doesn't ship retention
  pruning. `gzip` old files, or wait for the slice-3 `ember tool
  audit prune --older 30d` candidate.

---

## Recipe 5 — Tighten the approval policy

**What you want:** A tool that ships as `STANDING` (e.g.
`search_well`) should still ask before each call.

**What you'll edit:** `~/.ember/config/ember.yaml`.

**The recipe:**

```yaml
tools:
  enabled: true
  approval_overrides:
    search_well: per_call    # downgrade from STANDING to PER_CALL
```

Per ADR 0011 §2.4, the descriptor's policy is the **safety floor**:
config can downgrade `STANDING` → `PER_CALL` (more strict), and can
mark anything as `FORBIDDEN` (which prevents registration entirely),
but config cannot upgrade `PER_CALL` → `STANDING`.

**Verification:** the next `search_well` proposal will prompt you
instead of auto-approving.

**What could go wrong:**

- **Typo in the override** — Ember will silently skip it (the runtime
  coercer drops unknown enum values per a safety belt). Check the
  exact tool name from
  `~/.ember/state/tool_audit/$(date +%Y-%m-%d).jsonl`.

---

## Recipe 6 — Forbid a tool entirely

**What you want:** Some shipped tool should never run on this Ember
deployment.

**What you'll edit:** `~/.ember/config/ember.yaml`.

**The recipe:**

```yaml
tools:
  enabled: true
  approval_overrides:
    fetch_url: forbidden    # the registry refuses to register it
```

A tool marked `forbidden` in config does not appear in the registry
at all. Funi never sees it in the tool list; the model can't propose
it. If the model somehow does, `lookup()` returns None and the
framework records `no_such_tool` in the audit log.

**Verification:** the audit log will not contain `fetch_url` records.
`ember chat` will not display `[tool proposal] fetch_url` even if you
explicitly ask Ember to fetch a URL.

---

## Recipe 7 — Run Ember offline (Pi on your shelf, no internet)

**What you want:** Ember on a Pi with no internet. No tailnet, no
remote Ollama, no remote Well. Just the device.

**What you'll edit:** `~/.ember/config/ember.yaml`.

**The recipe:**

```yaml
funi:
  ollama:
    base_url: "http://localhost:11434"   # Ollama running on the Pi itself
    model: "phi3:mini"

brunnr:
  backend: sqlite_vec
  embedding_dim: 768
  sqlite_vec:
    path: "~/.ember/well/store.db"

tools:
  enabled: false       # no fetch_url, no remote anything
```

Then:

```bash
# Ingest local content into the local Well:
ember well ingest ~/notes/
ember well ingest ~/markdown-library/

# Talk to Ember offline:
ember chat
```

**Verification:** unplug the Pi's network; `ember chat` continues to
work as long as Ollama + sqlite_vec are local. `ember doctor` shows
both realms ok.

**What could go wrong:**

- **`Funi is unavailable (endpoint_unreachable)`** — Ollama isn't
  running. `systemctl --user start ollama` (or however your install
  starts it).
- **Long startup** — first `phi3:mini` load takes a minute on a Pi 5.
  Subsequent calls are fast.

---

## Recipe 8 — Watch tokens unfold (verify streaming is on)

**What you want:** Confirm slice-2 streaming actually streams.

**What you'll edit:** Nothing — streaming is on by default. To verify:

**The recipe:**

```bash
ember ask "Write a short poem about the hearth."
```

You should see tokens appear progressively, not in one block. If the
whole reply lands at once:

```yaml
# Check that you haven't accidentally turned it off:
funi:
  streaming: true   # should be true (default)
```

**Verification:** the visible cadence — words trickle in. The
`tests/integration/test_phase17_acceptance.py::test_slice_two_streaming_default_remains_on`
test verifies the default programmatically.

**What could go wrong:**

- **Reply lands as one block anyway** — your terminal might be
  line-buffering. Ember's streaming writes are flushed; if your
  shell is interposing buffering (rare), pipe `ember chat` directly
  rather than through `tee` or similar.
- **`[ollama unreachable: HTTP Error 400: Bad Request]`** — see
  Recipe 3's tool-capability constraint; this happens when
  `tools.enabled: true` AND your model can't do tool calls.

---

## Recipe 9 — Reset Ember from scratch

**What you want:** Throw away identity, config, and Well — start
clean.

**What you'll edit:** Delete `~/.ember/`.

**The recipe:**

```bash
# 1. Stop any running Ember invocations.
# 2. Back up anything you care about first:
cp ~/.ember/well/store.db ~/ember-backup-$(date +%Y%m%d).db
cp -r ~/.ember/state/tool_audit ~/ember-tool-audit-backup-$(date +%Y%m%d)/

# 3. Remove:
rm -rf ~/.ember/

# 4. Re-run setup:
ember setup
```

OR, less destructive, just re-run Hjarta keeping the Well:

```bash
ember setup --reset
```

This re-runs the wizard but doesn't touch the Well file.

**Verification:** `ember doctor` after — both realms come up clean.
The Well file from before is gone (or preserved depending on which
path you took).

**What could go wrong:**

- **Forgot to back up `~/.ember/well/store.db`** before `rm -rf`.
  All ingested content is gone. There's no recovery; re-ingest from
  the original sources.

---

## Recipe 10 — Move Ember to a new machine

**What you want:** Take your Ember setup from one host to another
(laptop → Pi, or vice versa).

**What you'll edit:** Files on both machines.

**The recipe:**

```bash
# On the source host:
tar czf ember-export.tar.gz \
    -C $HOME \
    .ember/identity \
    .ember/config \
    .ember/well \
    .ember/secrets \
    .ember/state/tool_audit
# Don't include .ember/state/smidja_progress unless you want
# in-progress ingest jobs to resume.

# Copy ember-export.tar.gz to the new machine.

# On the destination host:
# (Assumes Ollama is set up there too.)
pip install ember-agent[sqlite_vec]  # or with [pgvector] if needed
cd $HOME
tar xzf ember-export.tar.gz
chmod 700 .ember/secrets
chmod 600 .ember/secrets/*

ember doctor   # verify
ember chat
```

**Verification:** `ember doctor` on the new host shows both realms ok;
your conversation history is intact (visible by `ember chat` then
asking Ember to recall something from before).

**What could go wrong:**

- **`Well: DISCONNECTED — backend_reported_unavailable`** — embedding
  dim changed because the destination has a different Ollama
  embedding model installed. Re-ingest from the same source content
  on the destination, OR use the same embedding model on both hosts.
- **Permission errors after `tar`** — your tar didn't preserve
  permissions. Re-apply: `chmod 700 ~/.ember/secrets ~/.ember`
  and `chmod 600 ~/.ember/secrets/*`.

---

## Recipes wanted

Want a recipe for something not covered? File an issue with what you
were trying to do and where the existing docs left you stuck.
Operator-contributed recipes land here as they prove useful.

Candidates I'd like to see:

- Running Ember as a systemd unit (slice-3 daemon-mode candidate).
- Setting up a household-shared Gungnir from scratch.
- Migrating from a slice-1 install to slice 2 (the answer is "your
  yaml + secrets carry over; install the new extras"; a recipe with
  copy-paste commands would help).
- Multi-Ember sync (deferred per ADR 0013 §3, but operators may
  want it).
- Tool authoring tutorial (a fourth tool from scratch).
