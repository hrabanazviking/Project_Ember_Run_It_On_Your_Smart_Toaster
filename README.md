---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/s7dkpys7dkpys7dk.png](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/s7dkpys7dkpys7dk.png)

---

# Project Ember — Run It On Your Smart Toaster

> *Got a toaster? Good!* You could use it to run me, your very own
> useful AI Agent — for the normal folks! No need for data centers,
> no four-digit-pricetag gaming rig, no monthly subscription, no
> account, no email, no app store, no corporation looking over your
> shoulder. AI Agents are very useful, and now you too can have one.
> Just yours. Just here. On the smallest device you already own.

---

> *A lightweight, fully local AI companion designed to run on anything
> — from a Raspberry Pi to a fanless mini-PC to (yes, eventually,
> probably) a toaster. Currently at version **0.2.0**, slice-2
> ratified.*

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0861.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0861.jpeg)

---

## 📖 Table of contents

1. [What is Ember?](#-what-is-ember)
2. [Why Ember?](#-why-ember)
3. [Quick start — five minutes from zero to chatting](#-quick-start--five-minutes-from-zero-to-chatting)
4. [What Ember can do (the complete feature list)](#-what-ember-can-do-the-complete-feature-list)
5. [The complete command reference](#-the-complete-command-reference)
6. [Installation guide (the long version)](#-installation-guide-the-long-version)
7. [Your first conversation — a guide for noobs](#-your-first-conversation--a-guide-for-noobs)
8. [Configuration — the `ember.yaml` file](#-configuration--the-emberyaml-file)
9. [How Ember is built (architecture overview)](#-how-ember-is-built-architecture-overview)
10. [Using tools safely](#-using-tools-safely)
11. [Going bigger — sharing a Well across devices](#-going-bigger--sharing-a-well-across-devices)
12. [Troubleshooting & FAQ](#-troubleshooting--faq)
13. [What's next — the roadmap](#-whats-next--the-roadmap)
14. [Learn more (where the deeper docs live)](#-learn-more-where-the-deeper-docs-live)
15. [Sibling projects in the RuneForgeAI fellowship](#-sibling-projects-in-the-runeforgeai-fellowship)
16. [License](#-license)
17. [Distribution and privacy position](#-distribution-and-privacy-position)
18. [About RuneForgeAI](#-about-runeforgeai)

---

## ✨ What is Ember?

Ember is a **sovereign AI companion** that lives entirely on your
device.

She is built around a simple idea: an AI agent does not need to live
in a data centre. She does not need to call home to a corporation.
She does not need a $4,000 gaming rig with a roaring fan and a power
bill to match. She just needs a *small spark* — a little local model
to think with — and a *well* to drink her facts from. The spark fits
on the smallest computer you own. The well sits next to it, on the
same device or across your network, in a database that *you* control.

Ember is the spark. The little local mind. The companion who never
forgets that she lives in your home, on your hardware, and answers to
you.

She is for **the normal folks**. People who want an AI that they
*own*. People who are tired of being a product. People who'd rather
have a small helpful Norse-shaped flame on their bookshelf than a
big polished corporate mirror reflecting their own habits back at a
sales team.

She is **named carefully**. Every part of her — every subsystem, every
boundary, every promise — has a Norse-shaped name with a meaning
that *constrains what that part is allowed to do*. The names are not
decoration; they're load-bearing. Names like:

- **Funi** (flame, fire) — her local model, the spark itself.
- **Brunnr** (well, spring) — where her knowledge lives.
- **Strengr** (string, cord, tether) — the thread between her and
  her well, so she stays honest when the well goes quiet.
- **Smiðja** (forge) — what shapes raw documents into things she
  can recall.
- **Hjarta** (heart) — the first-meeting ritual when you summon her.
- **Munnr** (mouth) — the command line where you speak to her.

You don't need to remember any of those names to use her. They're
just there, holding the shape, so the project never drifts away from
what it promised on day one.

---

## 🎯 Why Ember?

**For you, the operator:**

- **Complete privacy.** Nothing ever leaves your device unless *you*
  point her at a remote well. No telemetry. No analytics. No "we
  improved your experience" updates that silently changed what she
  remembers.
- **Truly yours.** No company can change her, censor her, raise her
  price, deprecate her API, lock her behind a login wall, or shut her
  down. She is MIT-licensed source code that runs on your hardware.
- **Extremely lightweight.** Designed Pi-5-first. Default install
  fits on a microSD card. The full slice-2 install with all
  optional bits + a small local model is around 3.5 GB.
- **Fully customisable.** Give Ember any personality, role, or name.
  She'll answer to "Ember", "Spark", "Loki", or whatever you'd like
  her called.
- **Portable.** Move her between devices without losing her soul.
  `tar` her `~/.ember/` directory, copy it to the new machine,
  done.
- **Persistent memory** through a vector database — local SQLite by
  default; PostgreSQL on a household server when you grow into it.
- **Modular by design.** Swap the local model. Swap the storage
  backend. Swap the embedding model. Nothing assumes a fixed shape.
- **Works on almost anything that can run Python.** Linux, macOS, a
  Raspberry Pi 5, an old laptop, a small fanless box, a Windows
  Subsystem for Linux install.
- **Open source forever.** MIT license. No CLA. No private "pro"
  version. No bait-and-switch dual licensing.

**For your wallet:**

- **No monthly subscription.** Ember is software; you already own a
  computer.
- **No API calls.** Your conversations cost zero cents.
- **No "enterprise" tier.** Same Ember for everyone.

**For the world:**

- **No data centre.** A Pi 5 idles at about 3 watts. A data centre
  GPU pulls 700. Multiply that by millions of users. You do the
  math.

**For your privacy:**

- **No account creation.** Ember doesn't know who you are. She has
  no idea your operating system reports a username.
- **No cloud sync.** Your conversation history lives on your disk,
  in plain SQLite, and you can `rm` it any time.
- **No "we share anonymised data with our trusted partners".** There
  are no partners. There is just you and Ember and the hardware she
  runs on.

> *Ember just needs a little spark.*

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0865.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0865.jpeg)

---

## 🚀 Quick start — five minutes from zero to chatting

Here's the shortest path. If you already have Python 3.11+ and want
to read more before installing, [skip to the long installation
guide](#-installation-guide-the-long-version). If you've never done
anything like this before, see [Your first conversation](#-your-first-conversation--a-guide-for-noobs)
for the patient walkthrough.

### Step 1 — Install Ollama (Ember's local model runtime)

Ollama is what Ember talks to when she wants to think. It's free,
small, and runs in the background.

```bash
# macOS / Linux / WSL (recommended):
curl -fsSL https://ollama.com/install.sh | sh

# Then pull a small model. phi3:mini is the toaster-friendly default.
ollama pull phi3:mini

# And the embedding model Ember uses to remember things:
ollama pull nomic-embed-text
```

### Step 2 — Install Ember herself

```bash
# Make a fresh Python venv so Ember doesn't tangle with your other tools:
python3 -m venv ~/.ember-venv
source ~/.ember-venv/bin/activate

# Install Ember with her default storage backend:
pip install 'ember-agent[sqlite_vec]'
```

### Step 3 — Meet Ember for the first time

```bash
ember chat
```

The first time you run any `ember` command, Hjarta — the first-run
wizard — opens. She'll ask you a few gentle questions: where to find
her model, where to put her well, what to call her. Press **Enter**
through all the prompts to accept the sensible defaults.

When she's ready, she'll say so. Then you can type whatever you'd
like to talk about. To leave, type `/exit`.

### Step 4 — Give Ember something to read

Without a well full of your stuff, Ember can only talk in
generalities. Point her at a folder of notes, Markdown files,
research papers, whatever you have:

```bash
ember well ingest ~/notes/
```

She'll chunk them, embed them, and file them away. Next time you
`ember chat`, she can ground her answers in your material — and she
will *cite* which file she pulled from, so you can always check.

### Step 5 — Check she's healthy any time

```bash
ember doctor
```

This shows you the model she's using, the well she's connected to,
and how many documents she remembers. Use it any time something
seems off.

**That's it.** You have a working AI companion on your hardware,
answering only to you, talking only to itself, leaving no trace
anywhere but your disk.

---

## 🎁 What Ember can do (the complete feature list)

Slice 2 (version 0.2.0) is the current shipped state. Here's
everything Ember does today:

### Conversation

- **`ember chat`** — open an interactive REPL. Tokens stream in
  *live* as Ember thinks (you watch her form the words instead of
  staring at a blinking cursor). Press **Ctrl-C** mid-reply and
  she'll stop cleanly — the partial reply gets tagged
  `[interrupted by operator]` in her memory, so she knows you cut
  her off.
- **`ember ask "..."`** — one-shot question without entering the
  REPL. Good for piping into other tools or running from scripts.
- **Persistent memory.** Every turn is saved as an *Episode* — a
  full record of what you asked, what she said, which sources she
  cited, when it happened, whether her well was reachable at the
  time. She uses the last few Episodes as context for the next turn,
  so a conversation actually feels like one.

### Knowledge & retrieval

- **`ember well ingest <dir>`** — chunk and embed every supported
  file under a directory. Defaults to Markdown + plain text;
  Gungnir-aligned chunker (~1684 char average, 2000 char ceiling,
  paragraph-boundary-preferring).
- **`ember well status`** — count of documents, chunks, embedded
  chunks, and on-disk size.
- **Hybrid search** — every retrieval uses *both* vector similarity
  (what the model thinks is semantically close) AND full-text
  search (what literally matches the words you typed), fused with
  reciprocal rank fusion. So she finds both "what you meant" and
  "what you said".
- **Citations.** Every grounded reply ends with a citations block
  naming which chunks she used. No more guessing whether she made it
  up.
- **Graceful offline.** If the well is unreachable mid-conversation,
  she says so — a banner reads *`[well: disconnected (timeout, since
  2026-05-21T15:42:00+00:00) — reply is ungrounded; run ember
  doctor for diagnosis]`* — and then answers from what she can
  reason about without inventing facts about your documents. She
  never pretends to have looked something up when she hasn't.

### Storage (pluggable)

- **SQLite + sqlite-vec** (the default). One file. Zero auxiliary
  processes. Runs on a Pi 5 with 50 MB of resident memory. Good for
  one-person setups.
- **PostgreSQL + pgvector** (the shared-well option). Point Ember at
  a Postgres instance on your tailnet — your own server, a
  Gungnir-shape household well, anywhere libpq can reach. Schema-
  probe first: she'll read existing tables in the Gungnir shape
  without modifying them. **Read-only mode** mechanically protects
  shared wells from any writes Ember might accidentally try to make.

### First-run experience

- **`ember setup`** — Hjarta, the first-run wizard. A finite, named
  state machine (Greet → ChooseFuni → DiscoverFuni → ChooseWell →
  ConfigureWell → TestRetrieval → NameEmber → AdvancedTools →
  WriteIdentity → Done) that gently walks you through wiring up
  her model, her well, and her name. Atomic identity write at the
  end — either the whole setup completes or your filesystem is
  unchanged.
- **`ember setup --reset`** — re-run the wizard from scratch.
- **Advanced branch** (opt-in): the wizard asks if you want to
  enable tool use. Default is **off** per the Vow of Sovereignty —
  Ember doesn't reach beyond the chat turn unless you opt in.

### Tool use (opt-in)

When you set `tools.enabled: true` in her config (or pass
`--allow-tools` for a single invocation), Ember can call a small
set of operator-approved tools:

| Tool | What it does | Approval level |
|---|---|---|
| **`search_well`** | Search Ember's well via the hybrid-search path she uses for chat retrieval, but as a structured tool call she can use mid-thought. | **STANDING** (auto-approved — it's read-only, safe). |
| **`read_local_file`** | Read a UTF-8 text file under your home directory. Sandboxed: refuses `~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, `~/.aws/`, `~/.kube/`, `~/.gnupg/`, `~/.password-store/`. Refuses files larger than 256 KiB. Refuses anything outside `$HOME`. | **PER_CALL** (you approve every invocation). |
| **`fetch_url`** | GET an http(s) URL via stdlib urllib. Refuses non-http schemes. Refuses RFC1918, loopback, link-local, multicast addresses (unless you set `allow_private_addresses=true`). Honours `robots.txt`. Bounded at 1 MiB response. | **PER_CALL**. |

Every tool call is **audited** in an append-only JSONL log at
`~/.ember/state/tool_audit/<date>.jsonl`. Refusals are logged too.

When Ember proposes a tool call, you see something like:

```
[tool proposal] read_local_file  (call abc12345)
  description: Read a UTF-8 text file from the operator's home directory...
  arguments:
    path: '/home/you/notes/runes.md'
approve this call? [y/n/always]
```

Three answers:

- **`y`** — approve once.
- **`always`** — approve for the rest of this session (no longer
  asks for that specific tool until you restart).
- **`n`** (or anything else) — refuse. Ember sees the refusal as a
  typed error and usually summarises gracefully on the next turn.

You can also **forbid** a tool entirely in config — the registry
won't even register it.

### Health & diagnostics

- **`ember doctor`** — single command for "is everything okay?".
  Shows Funi status (model name, last successful probe), Well
  status (backend kind, document count, last successful probe).
  Plain-English errors, never stack traces.

### Operator configuration

- **`~/.ember/config/ember.yaml`** — the single source of truth.
  Hjarta writes it at first-run; you edit it; it takes effect on
  next `ember` invocation. See [Configuration](#-configuration--the-emberyaml-file)
  below for the full surface.
- **Environment-variable overrides**:
  - `OLLAMA_HOST` — redirects both Funi's API and Smiðja's embedding
    endpoint. Useful for tailnet Ollama.
  - `EMBER_WELL_PASSWORD` — first-checked source for the pgvector
    secret.
- **CLI overrides**:
  - `--config-root PATH` — override `~/.ember/`.
  - `--allow-tools` / `--no-tools` — single-invocation tool toggle.

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0866.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0866.jpeg)

---

## 🛠 The complete command reference

Every subcommand of the `ember` CLI, what it does, and what it
needs.

### Global flags

These work with every subcommand:

| Flag | Default | What it does |
|---|---|---|
| `--config-root PATH` | `~/.ember/` | Where Ember's identity, secrets, well, and state live. Useful for testing or running multiple Embers on one machine. |
| `--allow-tools` | (off — see config) | Enable tool use for *this invocation only*, overriding `tools.enabled` from the config file. |
| `--no-tools` | (off — see config) | Disable tool use for *this invocation only*. Mutually exclusive with `--allow-tools`. |

### `ember chat`

> Open an interactive conversation REPL.

```bash
ember chat
```

What happens:

1. Loads your config from `~/.ember/config/ember.yaml`.
2. Opens Funi (your local model). If unavailable, exits with a
   clear error.
3. Opens the Well via Strengr (with retry). If unreachable,
   continues in ungrounded mode with a banner.
4. Greets you with your custom name for her.
5. Drops into a `> ` prompt.
6. For each turn you type:
   - Retrieves up to 5 relevant chunks from the well.
   - Assembles a prompt with your identity, the last few episodes,
     and the chunks.
   - Asks Funi to stream the reply.
   - You watch tokens appear live.
   - If tools are enabled and the model proposes a tool call, you
     get the approval prompt; on approval, the tool runs and the
     reply is fed back into a follow-up turn.
   - Citations footer if the chunks contributed.
   - The whole turn is saved as an Episode.

Exit: type `/exit`, `/quit`, `/q`, or press **Ctrl-D**. **Ctrl-C**
mid-reply interrupts the current stream and returns to the prompt
(it does NOT exit the REPL; press **Ctrl-D** for that, or use one of
the exit commands).

### `ember ask "<question>"`

> One-shot question. Same plumbing as `ember chat`, but exits after
> one turn.

```bash
ember ask "What's the difference between sqlite_vec and pgvector?"
```

Useful for:

- Piping into other tools: `ember ask "summarise yesterday's news" | mail -s "summary" you@example.com`.
- Scripts that just need one answer.
- Sanity-checking config changes without entering the REPL.

### `ember setup [--reset]`

> Run Hjarta, the first-run wizard.

```bash
ember setup           # only runs if no identity exists yet
ember setup --reset   # discard existing identity, run from scratch
```

Hjarta walks you through:

1. **Greet** — says hello.
2. **ChooseFuni** — confirms the model runtime (Ollama for now).
3. **DiscoverFuni** — probes that Ollama is reachable and your model
   is pulled.
4. **ChooseWell** — confirms the well backend (sqlite_vec default).
5. **ConfigureWell** — sets the well path.
6. **TestRetrieval** — does a tiny round-trip to make sure storage
   works.
7. **NameEmber** — asks what to call her ("Press Enter to keep
   'Ember'…").
8. **AdvancedTools** — asks if you want to enable tool use
   (default: no).
9. **WriteIdentity** — atomically writes
   `~/.ember/identity/identity.json` AND
   `~/.ember/config/ember.yaml`.
10. **Done.**

Press Enter through any prompt to accept the default. Type
`cancel`, `quit`, `q`, `no`, or `n` to abort cleanly — nothing is
written.

### `ember well ingest <path>`

> Chunk, embed, and file away every supported file under a
> directory.

```bash
ember well ingest ~/notes/
ember well ingest ~/research/papers/
ember well ingest /mnt/big-drive/markdown-library/
```

What happens:

1. Walks the directory recursively.
2. For each `.md` / `.txt` (default; configurable):
   - Hashes the content.
   - If already ingested (matching hash), skip.
   - Otherwise: chunk it, embed each chunk via Ollama
     (`nomic-embed-text` by default), deposit chunks into the well
     transactionally per batch.
3. Maintains a *resumable progress journal* at
   `~/.ember/state/smidja_progress/<job_id>.json` so an interrupted
   ingest (power blip, Ctrl-C, kernel panic) resumes from the last
   completed batch on next run.
4. Prints a summary: documents, chunks, failed, elapsed.

### `ember well status`

> Show what's in the well.

```bash
ember well status
```

Output:

```
Well (sqlite_vec):
  documents:        12
  chunks:           163
  embedded chunks:  163
  size on disk:     5.4 MB
  last successful probe: 2026-05-21T11:48:03+00:00
```

### `ember doctor`

> Health check across all realms. Always your first stop when
> something's off.

```bash
ember doctor
```

Output:

```
Ember health:
  Funi:    ok — model phi3:mini, last_ok 2026-05-21T11:48:03+00:00
  Well:    ok — backend sqlite_vec, 12 docs / 163 chunks, last_ok 2026-05-21T11:48:03+00:00
```

When something's wrong it tells you in plain English:

```
Ember health:
  Funi:    UNAVAILABLE — endpoint_unreachable: connection refused
  Well:    ok — backend sqlite_vec, 12 docs / 163 chunks, last_ok 2026-05-21T11:48:03+00:00
```

(Translation in that case: "Ollama isn't running. Start it.")

### Exit codes

- `0` — everything succeeded.
- `1` — Funi unavailable, config error, or other startup failure.
- `2` — argparse error (unknown subcommand, missing required arg).

---

## 📦 Installation guide (the long version)

The [Quick start](#-quick-start--five-minutes-from-zero-to-chatting)
covers the common path. This section covers the variations.

### Requirements

- **Python 3.11 or newer.** Use your distro's package manager
  (`apt install python3`, `brew install python@3.12`, etc.) or
  download from [python.org](https://www.python.org/).
- **A working internet connection** for the initial install. After
  install, Ember runs fully offline (unless you point her at a
  remote well or enable `fetch_url`).
- **An Ollama install.** Ember talks to Ollama for both the chat
  model and the embedding model. Get it at
  [ollama.com](https://ollama.com).
- **Disk space**: ~3.5 GB total for a typical install (Ollama
  ~700 MB, `phi3:mini` ~2.3 GB, `nomic-embed-text` ~274 MB, Ember
  itself + dependencies ~50 MB).
- **RAM**: 4 GB minimum, 8 GB recommended. Ember itself uses ~50
  MB; the model eats the rest.

### Step 1 — Install Ollama

```bash
# Linux / macOS (and WSL on Windows):
curl -fsSL https://ollama.com/install.sh | sh

# Verify it's running:
ollama list
# Should print an empty model list, no error.

# Pull the two models Ember needs:
ollama pull phi3:mini          # the chat model (~2.3 GB)
ollama pull nomic-embed-text   # the embedding model (~274 MB)

# Optional, for tool use (slice-2 feature):
ollama pull llama3.2:3b        # ~2.0 GB; supports tool calls (phi3:mini does not)
```

### Step 2 — Make a Python virtual environment

This keeps Ember's dependencies separate from your system Python.

```bash
python3 -m venv ~/.ember-venv
source ~/.ember-venv/bin/activate

# (Optional but recommended) upgrade pip:
pip install --upgrade pip
```

To use Ember later, you'll either need to activate the venv first
(`source ~/.ember-venv/bin/activate`) or alias the binary:

```bash
# In your ~/.bashrc / ~/.zshrc:
alias ember="$HOME/.ember-venv/bin/ember"
```

### Step 3 — Install Ember

The default install ships with **zero external runtime dependencies**.
You opt into the bits you want via pip "extras":

```bash
# The toaster baseline (recommended for first-time setup):
pip install 'ember-agent[sqlite_vec]'

# OR with YAML config support (if you want to edit ~/.ember/config/ember.yaml as YAML):
pip install 'ember-agent[sqlite_vec,config]'

# OR the full slice-2 install with shared-well support:
pip install 'ember-agent[sqlite_vec,config,pgvector]'
```

The extras:

| Extra | What it adds | Why |
|---|---|---|
| `sqlite_vec` | `sqlite-vec` Python package | The default local well backend. **You almost certainly want this.** |
| `config` | `pyyaml` | YAML config files. (TOML works without this; YAML is just easier to read.) |
| `pgvector` | `psycopg[binary]` + `pgvector` | Postgres + pgvector backend for shared wells. Skip unless you have one. |

### Step 4 — First run

```bash
ember chat
# Hjarta opens automatically since there's no identity yet.
# Press Enter through the prompts to accept defaults.
```

### Platform-specific notes

#### Linux

Works out of the box. Tested on Ubuntu 24.04, Debian 12, Fedora 40,
Arch.

If you're on a Pi 5, see also `deploy/pi/INSTALL.md` for Pi-specific
notes (it's the most thorough install guide in the repo).

#### macOS

Works on both Intel and Apple Silicon. Use Homebrew Python
(`brew install python@3.12`) rather than the Apple-shipped one.

#### Windows (WSL)

Run inside WSL2 (Windows Subsystem for Linux). Pure-Windows Python
install hasn't been validated but should work with `pip install
ember-agent[sqlite_vec,config]`.

#### Raspberry Pi 5

The toaster baseline. Recommended setup: 8 GB Pi 5 + an external
SSD on USB 3 for the well (an SD card works but wears out faster).

```bash
# On a fresh Pi OS install:
sudo apt update
sudo apt install python3 python3-venv python3-pip
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
ollama pull nomic-embed-text
python3 -m venv ~/.ember-venv
source ~/.ember-venv/bin/activate
pip install 'ember-agent[sqlite_vec]'
ember chat
```

For the full operator install guide tailored to Pi 5, see
[`deploy/pi/INSTALL.md`](deploy/pi/INSTALL.md).

### Updating Ember

```bash
source ~/.ember-venv/bin/activate
pip install --upgrade 'ember-agent[sqlite_vec]'
```

Your `~/.ember/` directory (identity, config, well, audit log) is
preserved across upgrades.

### Uninstalling

```bash
pip uninstall ember-agent
rm -rf ~/.ember-venv

# (Optional — this also deletes everything Ember remembers):
rm -rf ~/.ember/
```

**Important:** the well file at `~/.ember/well/store.db` is
everything Ember has learned. **Back it up by copying that file**
before deleting `~/.ember/` if you might want to come back.

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0864.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0864.jpeg)

---

## 🌱 Your first conversation — a guide for noobs

You've installed everything. You typed `ember chat`. Now what?

**Don't panic.** This section is for you.

### What just happened (the wizard)

If this is your very first run, Ember greeted you with a wizard
(her name is Hjarta — "heart"). Her job is to set up the file in
your home directory where Ember will live.

Hjarta asked you several questions. Press **Enter** to accept the
default any time you're not sure. You can always change anything
later by editing `~/.ember/config/ember.yaml`.

When Hjarta finishes she says something like:

```
All set. I'm Ember, ready when you are.

Try:
  ember well ingest <directory>   # give me something to read
  ember chat                      # talk to me
  ember doctor                    # check my health
```

### Your first chat turn

At the `> ` prompt, type anything:

```
> Hi!
```

She'll respond. Probably something brief and friendly. The first
reply is the slowest because the model has to load into memory. After
that, replies start streaming in roughly two seconds and finish in
under thirty.

### Why she doesn't know about your stuff yet

You'll notice Ember's first answers are generic. That's because her
well is empty — she has nothing of *yours* to ground her replies
against. She'll also show this banner above each reply:

```
[well: disconnected — reply is ungrounded]
```

Wait, "disconnected"? No — she's *connected* to her well; it's just
*empty*. The banner means she didn't find any of your documents to
cite. The wording will improve in a future slice; for now, "ungrounded"
just means "no chunks were used in this answer".

### Giving her something to read

Find a folder of Markdown notes, plain-text files, anything. Don't
have one? Make one:

```bash
mkdir ~/notes
echo "# About me" > ~/notes/about-me.md
echo "I like AI projects that don't depend on data centres." >> ~/notes/about-me.md
echo "I keep a list of my favourite Norse gods in ~/notes/gods.md." >> ~/notes/about-me.md
echo "# Favourite Norse gods" > ~/notes/gods.md
echo "Odin, the Allfather. Wisdom-seeker." >> ~/notes/gods.md
echo "Thor, son of Odin. Storm god." >> ~/notes/gods.md
echo "Freyja, goddess of love, beauty, and seiðr." >> ~/notes/gods.md
```

Now ingest:

```bash
ember well ingest ~/notes
```

You'll see:

```
Ingest complete (job 4f3a90c1):
  documents: 2
  chunks:    2
  failed:    0
  elapsed:   3.41s
```

Now `ember chat` again:

```
> Tell me about Odin
```

This time, the answer ends with a citations block:

```
citations:
  - About me (chunk 2, score 0.483)
  - Favourite Norse gods (chunk 3, score 0.917)
```

She read your notes. She knows what she knows because *you wrote it*.

### The four magic things to remember

1. **`ember chat`** — talk to her.
2. **`ember well ingest <folder>`** — teach her.
3. **`ember well status`** — see what she knows.
4. **`ember doctor`** — when something seems off.

That's the everyday loop. Everything else (`ember setup --reset`,
tool use, pgvector, etc.) is optional advanced stuff for when you
want more.

### Things that might worry you the first time (but shouldn't)

- **"It's slow!"** First reply takes ~10 seconds while the model
  loads. After that, ~2 seconds to start streaming, then she types
  about as fast as a person.
- **"She made something up!"** Small local models hallucinate when
  asked things they don't know. If she's grounding from your well
  (citations block present), trust the citations. If she's NOT
  grounding (you see the "ungrounded" banner), treat her answer as
  "what a small model thinks" — useful for brainstorming, not for
  facts.
- **"Where do my conversations go?"** Into `~/.ember/well/store.db`.
  That's it. Nowhere else. You can `sqlite3 ~/.ember/well/store.db
  "SELECT * FROM episodes;"` to read them, or delete the file to
  forget everything.
- **"Did I just install something that calls home?"** No. Ember,
  Ollama, and the models are all entirely local. The only network
  traffic during a normal session is between Ember and Ollama on
  `localhost` (or wherever you've pointed her).

### Where to go next

- **You want her to read more things** → `ember well ingest <folder>`
  for each folder.
- **You want her on a different model** → edit `~/.ember/config/ember.yaml`,
  change `funi.ollama.model`.
- **You want her to call tools (read files, fetch URLs)** → see
  [Using tools safely](#-using-tools-safely).
- **You want to share a well across multiple devices** → see
  [Going bigger](#-going-bigger--sharing-a-well-across-devices).

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0863.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0863.jpeg)

---

## ⚙️ Configuration — the `ember.yaml` file

Hjarta wrote `~/.ember/config/ember.yaml` at first-run. You edit it
to change Ember's behaviour. Changes take effect on the next `ember`
command — there's no daemon to restart.

A full annotated template lives at
[`config/ember.example.yaml`](config/ember.example.yaml). Copy any
section out of it.

### The four-layer overlay (innermost wins)

1. **Defaults** — built into the code; what you get if you don't set
   anything.
2. **The YAML file** — what you put in `~/.ember/config/ember.yaml`.
3. **Environment variables** — `OLLAMA_HOST` redirects Funi + Smiðja
   endpoints; `EMBER_WELL_PASSWORD` is the first source the pgvector
   secret resolver checks.
4. **CLI flags** — `--allow-tools` / `--no-tools` etc.

### The shape of the file

```yaml
# ~/.ember/config/ember.yaml

identity:
  name: "Ember"               # what you call her
  role: "your small local AI companion"

funi:                          # the local model
  runtime: ollama
  streaming: true              # tokens appear live as she thinks
  ollama:
    base_url: "http://localhost:11434"
    model: "phi3:mini"         # or llama3.2:3b for tool use
    temperature: 0.7
    top_p: 0.9
    num_predict: 1024

strengr:                       # the tether to the well
  health_check_timeout_s: 5.0
  retry_attempts: 3
  retry_backoff_max_s: 30.0

brunnr:                        # the well — pluggable storage
  backend: sqlite_vec          # or: pgvector
  embedding_dim: 768
  sqlite_vec:
    path: "~/.ember/well/store.db"
    wal_mode: true
  # pgvector:                  # uncomment for shared well
  #   url: "postgresql://volmarr@gungnir/knowledge"
  #   secret_ref: "~/.ember/secrets/well.password"
  #   read_only: true          # protects shared wells

smidja:                        # the ingest forge
  embedding:
    endpoint: "http://localhost:11434/api/embed"
    model: "nomic-embed-text"
    batch_size: 32
  chunker:
    max_chars: 2000
    target_chars: 1684
    min_chars: 200

tools:                         # slice-2 tool use (off by default)
  enabled: false
  standing_trust: false        # true = auto-approve every PER_CALL tool
  approval_overrides: {}       # e.g. {search_well: per_call}

logging:
  level: INFO
```

### Common edits

#### Change the model

```yaml
funi:
  ollama:
    model: "llama3.2:3b"       # for tool use; pull with: ollama pull llama3.2:3b
```

#### Point Ember at Ollama on another machine (your tailnet)

```yaml
funi:
  ollama:
    base_url: "http://100.67.240.22:11434"
```

OR per-invocation:

```bash
OLLAMA_HOST=http://100.67.240.22:11434 ember chat
```

#### Turn streaming off

```yaml
funi:
  streaming: false
```

(Useful when piping `ember ask "..."` into another tool that wants a
single blob.)

#### Enable tool use

```yaml
tools:
  enabled: true
```

OR per-invocation:

```bash
ember --allow-tools chat
```

For the full operator playbook with copy-paste recipes for every
common configuration scenario, see
[`docs/OPERATOR_PLAYBOOK.md`](docs/OPERATOR_PLAYBOOK.md).

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0867.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0867.jpeg)

---

## 🏗 How Ember is built (architecture overview)

You don't need to read this section to use Ember. It's for the
curious — for people who want to understand the *shape* before they
start moving things around.

### The Three Realms

Ember's whole codebase is divided into three realms, and the
divisions are sacred:

```
                       ┌───────────────────────────┐
                       │      SPARK realm          │
                       │  (must run offline)       │
                       │                           │
                       │  Funi  (local LLM)        │
                       │  Hjarta (first-run)       │
                       │  Munnr  (CLI)             │
                       └──────────┬────────────────┘
                                  │
                                  ▼
                       ┌───────────────────────────┐
                       │      THREAD realm         │
                       │                           │
                       │  Strengr (the tether)     │
                       └──────────┬────────────────┘
                                  │
                                  ▼
                       ┌───────────────────────────┐
                       │      WELL realm           │
                       │  (may be local OR remote) │
                       │                           │
                       │  Brunnr (storage)         │
                       │  Smiðja (ingest)          │
                       └───────────────────────────┘
```

Higher realm may import lower; lower never imports higher. The
discipline is mechanical — verified by a test that walks every
import in the codebase.

### The Six True Names

Each of the six load-bearing subsystems has a Norse-shaped name
chosen so the *name itself* expresses what the subsystem does:

| True Name | Meaning | Role |
|---|---|---|
| **Funi** | flame, fire | The local LLM runtime. The spark itself. Currently: Ollama adapter. Future: llama.cpp, LM Studio, Apple Foundation Models, Windows AI Foundry. |
| **Strengr** | string, cord, tether | The thread between Ember and her well. Owns retry, auth, health, and the "graceful offline" promise. |
| **Brunnr** | well, spring | The storage layer. Pluggable: SQLite+sqlite-vec (default), Postgres+pgvector (shared). Future: Qdrant, Chroma, LanceDB. |
| **Smiðja** | forge | The ingest forge. Chunks content, embeds it, deposits chunks into Brunnr. Currently: local files. Future: URL fetch, shared-well mirror, Project Nomad bundles. |
| **Hjarta** | heart | The first-run ritual. A finite state machine that wires Funi to Strengr to Brunnr the first time you meet Ember. |
| **Munnr** | mouth | The command-line surface. `ember chat`, `ember ask`, `ember well ingest`, `ember doctor`, etc. |

The names are *load-bearing*: a subsystem that drifts from its name
has lost its boundary. This isn't decoration; it's a design
discipline that keeps the project honest as it grows.

### Why this matters to you

It doesn't, really, unless you want to *extend* Ember. But it means:

- **Adding a new storage backend** is a `BrunnrHandle`
  implementation — same Protocol that `sqlite_vec` and `pgvector`
  both satisfy. Munnr and Funi don't know which backend they're
  talking to.
- **Adding a new local model runtime** is a `FuniHandle`
  implementation. Hjarta and Munnr don't know which runtime is
  underneath.
- **Adding a new tool** is one Python file in `src/ember/tools/`
  that calls `register(_DESCRIPTOR, _execute)` at import time.

If you want to read the deeper design docs, see:

- [`docs/SYSTEM_VISION.md`](docs/SYSTEM_VISION.md) — the vows + the
  identity statement.
- [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) —
  the Three Realms in detail.
- [`docs/architecture/DOMAIN_MAP.md`](docs/architecture/DOMAIN_MAP.md) —
  per-subpackage ownership.
- [`docs/architecture/EMBER_TRUE_NAMES.md`](docs/architecture/EMBER_TRUE_NAMES.md) —
  what each True Name owns and doesn't own.

---

## 🔧 Using tools safely

When you enable tool use, Ember can call a small set of
operator-approved tools. **The default is off** — she doesn't reach
beyond the chat turn until you opt in.

### What the tools are

| Tool | Approval | What it does | What it refuses |
|---|---|---|---|
| **`search_well`** | `STANDING` (auto) | Search her well via hybrid search, as a structured tool call mid-thought (not just at the start of a turn). | Empty query; unbound well. |
| **`read_local_file`** | `PER_CALL` | Read a UTF-8 text file under your `$HOME`. | Anything outside `$HOME`; the sandbox denylist (`~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, `~/.aws/`, `~/.kube/`, `~/.gnupg/`, `~/.password-store/`); directories; files larger than 256 KiB; symlinks that try to escape the sandbox. |
| **`fetch_url`** | `PER_CALL` | GET an http(s) URL via stdlib `urllib`. | Non-http(s) schemes; RFC1918, loopback, link-local, and multicast addresses (unless you pass `allow_private_addresses=true`); URLs disallowed by `robots.txt`; responses larger than 1 MiB. |

Slice-2 ships these three. The framework supports more — a fourth
tool is one Python file in `src/ember/tools/`.

### Turning tools on

Edit `~/.ember/config/ember.yaml`:

```yaml
tools:
  enabled: true
```

OR per-invocation:

```bash
ember --allow-tools chat
```

**Important:** you need a tool-capable Funi model. `phi3:mini` does
NOT support native tool calls (Ollama returns HTTP 400). Use
`llama3.2:3b` instead:

```bash
ollama pull llama3.2:3b
```

```yaml
funi:
  ollama:
    model: "llama3.2:3b"
```

### What tool approval looks like

When Ember proposes a `PER_CALL` tool:

```
[tool proposal] read_local_file  (call abc12345)
  description: Read a UTF-8 text file from the operator's home directory...
  arguments:
    path: '/home/you/notes/runes.md'
approve this call? [y/n/always]
```

- `y` — approve once.
- `always` — approve for the rest of this session.
- `n` (or anything else) — refuse.

`STANDING` tools (like `search_well`) skip the prompt and run
automatically.

### The audit log

Every tool call is recorded — successes, refusals, invalid-args
rejections, missing-tool errors — in
`~/.ember/state/tool_audit/<YYYY-MM-DD>.jsonl`. One file per UTC day.

Read it with `jq`:

```bash
# Today's calls:
jq < ~/.ember/state/tool_audit/$(date +%Y-%m-%d).jsonl

# All search_well calls in the last week:
for d in $(seq -w 0 6); do
  date_str=$(date -d "-${d} days" +%Y-%m-%d)
  f=~/.ember/state/tool_audit/${date_str}.jsonl
  [ -f "$f" ] && jq 'select(.tool == "search_well")' "$f"
done
```

### Locking things down further

```yaml
tools:
  enabled: true

  # Operator can DOWNGRADE STANDING → PER_CALL (more strict),
  # but cannot upgrade PER_CALL → STANDING. The descriptor is
  # the safety floor.
  approval_overrides:
    search_well: per_call    # be strict about search too
    fetch_url:   forbidden   # mechanically refuse to even register it
```

### Trusting everything (if you really want to)

```yaml
tools:
  enabled: true
  standing_trust: true       # auto-approve every PER_CALL tool (still audited)
```

Use this carefully. Audited but unattended.

For more, see [`docs/OPERATOR_PLAYBOOK.md`](docs/OPERATOR_PLAYBOOK.md)
recipes 3-6, and the design document
[`docs/decisions/0011-tool-use-framework.md`](docs/decisions/0011-tool-use-framework.md).

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0868.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0868.jpeg)

---

## 🌍 Going bigger — sharing a Well across devices

The default `sqlite_vec` well is one file on your local disk —
private, simple, fast. Eventually you might want:

- **A shared household well** — multiple Embers (one on your Pi,
  one on your laptop) reading from the same knowledge.
- **A pre-populated well** — your existing Postgres+pgvector
  instance (a "Gungnir") with thousands of chunks you've already
  ingested with another tool.
- **A bigger well** — well past what a single SQLite file
  comfortably handles.

For all three, slice-2 ships the `pgvector` backend.

### Setting up a shared well

You'll need:

- A Postgres instance reachable from your Ember (your tailnet, your
  LAN, wherever).
- The `pgvector` extension installed in that database.
- A user account Ember can connect as.

```bash
# 1. Install the pgvector pip extra:
pip install 'ember-agent[pgvector]'

# 2. Put your well password in a mode-0o600 file:
mkdir -p ~/.ember/secrets
chmod 700 ~/.ember/secrets
$EDITOR ~/.ember/secrets/well.password
chmod 600 ~/.ember/secrets/well.password
```

```yaml
# 3. Edit ~/.ember/config/ember.yaml:
brunnr:
  backend: pgvector
  embedding_dim: 768          # must match chunks.embedding dim
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"
    schema: public
    read_only: true   # CRITICAL if you don't own this database
```

Then verify:

```bash
ember doctor
# Well: ok — backend pgvector, 95 docs / 35682 chunks, last_ok ...
```

### Why `read_only: true` matters

When you're pointing Ember at a well *you didn't bootstrap* — a
household-shared Gungnir, a research-group Postgres, anything that
has its own ingest pipeline — set `read_only: true`. The adapter
will mechanically refuse to `add_document` / `add_chunks` /
`add_episode`, and it won't create the pgvector extension or
auto-bootstrap missing tables. Ember can still query; she just
can't write.

This is the difference between "Ember on your shelf" and "Ember as
a polite guest in someone else's library".

### Sensible secret handling

The pgvector secret resolver tries three sources in order:

1. **Environment variable** — `EMBER_WELL_PASSWORD` by default.
   Useful for containers / CI.
2. **Keyring** — your OS keyring (Linux libsecret, macOS Keychain,
   etc.) if you have the `keyring` Python package installed.
3. **Mode-0o600 file** — `~/.ember/secrets/well.password` (or
   wherever `secret_ref` points). The resolver **refuses** files
   with permissions more permissive than `0o600` — it's a
   belt-and-suspenders defence against accidentally world-readable
   secrets.

If none of those resolve a secret, Ember refuses to connect with a
typed `Disconnected(AUTH_FAILED, "no Well secret resolved (env
$EMBER_WELL_PASSWORD not set; keyring entry for ... not found;
secret file /path not found)")`. The error names every source she
tried.

For the full pgvector operator guide, see
[`docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`](docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md).

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0869.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0869.jpeg)

---

## 🚑 Troubleshooting & FAQ

### "She doesn't start at all"

```bash
ember doctor
```

That tells you which side is unhappy. The most common cause is
Ollama not running. Start it:

```bash
# Linux (systemd):
systemctl --user start ollama
# Or just:
ollama serve &
```

### "She says `Funi is unavailable (endpoint_unreachable)`"

Ollama isn't running, or it's bound to a non-default host. If you've
put Ollama on a tailnet, set `OLLAMA_HOST`:

```bash
OLLAMA_HOST=http://100.67.240.22:11434 ember chat
```

Or permanently in config:

```yaml
funi:
  ollama:
    base_url: "http://100.67.240.22:11434"
```

### "She says `Well: DISCONNECTED — backend_reported_unavailable`"

If the message mentions `sqlite_vec`, install the extra:

```bash
pip install sqlite-vec
```

If the message mentions `pgvector` and "extra not installed":

```bash
pip install 'ember-agent[pgvector]'
```

If the message mentions an embedding-dim mismatch, the well was
populated with a different embedding model than you've configured.
Either match the `embedding_dim` in config, or re-ingest from
scratch.

### "She says `auth_failed (no Well secret resolved ...)`"

(pgvector backend.) The secret file is missing, empty, or has the
wrong permissions:

```bash
chmod 600 ~/.ember/secrets/well.password
ls -l ~/.ember/secrets/well.password   # should show: -rw-------
```

### "Tools don't work — `HTTP Error 400: Bad Request` when I enable them"

Your Funi model doesn't support tool calls. `phi3:mini` doesn't;
`llama3.2:3b` does:

```bash
ollama pull llama3.2:3b
```

```yaml
funi:
  ollama:
    model: "llama3.2:3b"
```

Or just don't enable tools — Ember is fully useful without them.

### "Her replies are slow"

First reply after restart is slow (~10s) because the model loads
into memory. After that, ~2s to first token, then she types about
as fast as a person. If a Pi 5 is too slow even after warmup, try a
smaller model:

```bash
ollama pull qwen2.5:1.5b-instruct   # ~1.3 GB resident
```

```yaml
funi:
  ollama:
    model: "qwen2.5:1.5b-instruct"
```

### "Her replies are wrong / made up"

If she's citing chunks (citations block present), the chunks she
read are wrong. Check them: `sqlite3 ~/.ember/well/store.db "SELECT
text FROM chunks WHERE id IN (...)"`.

If she's NOT citing (you see the disconnect banner), she's
answering from the model's training data, which is small. Add more
of your own material with `ember well ingest <folder>`.

### "How do I delete a single conversation she remembers?"

Episodes are stored in the `episodes` table of her well:

```bash
sqlite3 ~/.ember/well/store.db
sqlite> DELETE FROM episodes WHERE operator_input LIKE '%embarrassing thing%';
sqlite> .quit
```

### "How do I make her forget everything?"

```bash
rm ~/.ember/well/store.db
# Then ember setup --reset to re-walk Hjarta if you want fresh identity too.
```

### "Where do I find help if my problem isn't here?"

- [`deploy/pi/INSTALL.md`](deploy/pi/INSTALL.md) has a longer
  troubleshooting table.
- [`docs/OPERATOR_PLAYBOOK.md`](docs/OPERATOR_PLAYBOOK.md) has
  numbered recipes.
- Open an issue on
  [GitHub](https://github.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/issues)
  with the output of `ember doctor`.

---

## 🗺 What's next — the roadmap

Slice 2 (version 0.2.0, ratified by ADR 0013 on 2026-05-21) is the
current shipped state. Slice 3 is queued.

**Things slice 2 deliberately deferred** (per
[ADR 0013 §3](docs/decisions/0013-second-slice-ratification.md#3-what-slice-2-deliberately-deferred-still-queued)):

- **Other surfaces.** A GUI (working name: **Auga** — "eye"), a
  voice interface (**Rödd** — "voice"), an HTTP gateway
  (**Bifröst** — the rainbow bridge). All collected under ADR 0012.
- **Other Brunnr backends.** Qdrant, Chroma, LanceDB. Each is a
  future `BrunnrHandle` implementation.
- **Other Funi runtimes.** llama.cpp, LM Studio, Apple Foundation
  Models, Windows AI Foundry. Each is a future `FuniHandle`
  implementation.
- **Other Smiðja sources.** URL fetch, shared-well mirror, Project
  Nomad bundles.
- **Writable tools.** File-write, shell exec, git ops. Read-side
  tools needed lived operator experience first.
- **Multi-operator shared Wells.** Concurrent-writer locking is out
  of scope until two Embers fight over one Well.
- **Backup / restore / export-import.** Operational tooling slice.
- **Voice + image modalities for Funi.** Text-only for now.
- **A plugin framework** for third-party tools. Slice-3 ADR
  candidate.

**Open questions for slice 3**:

- `ember tool audit` subcommand (read the audit log without
  `jq`-spelunking).
- Hjarta wizard for tool sub-config (per-tool approval defaults).
- `Funi.health()` reporting tool-call capability so Hjarta refuses
  to enable tools on incapable models.
- Audit-log retention pruning.
- Per-tool `version` field.

For the long-form retrospective on what slice 2 was, what it
delivered, and what we learned, see
[`docs/SLICE_2_RETROSPECTIVE.md`](docs/SLICE_2_RETROSPECTIVE.md).

---

## 📚 Learn more (where the deeper docs live)

| You want to... | Read |
|---|---|
| Install on a Pi 5 with all the trimmings | [`deploy/pi/INSTALL.md`](deploy/pi/INSTALL.md) — 11 sections of operator walkthroughs |
| See operator recipes for common scenarios | [`docs/OPERATOR_PLAYBOOK.md`](docs/OPERATOR_PLAYBOOK.md) — 10 numbered playbooks |
| Read what Ember promises to be | [`docs/SYSTEM_VISION.md`](docs/SYSTEM_VISION.md) — the Skald's statement; §11 has the Vows-Fulfilled Postscript |
| Understand the architecture | [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md), [`DOMAIN_MAP.md`](docs/architecture/DOMAIN_MAP.md), [`DATA_FLOW.md`](docs/architecture/DATA_FLOW.md) |
| Know what each True Name owns | [`docs/architecture/EMBER_TRUE_NAMES.md`](docs/architecture/EMBER_TRUE_NAMES.md) |
| See the slice ratification decisions | [`docs/decisions/0007-first-slice-ratification-2026-05-21.md`](docs/decisions/0007-first-slice-ratification-2026-05-21.md) (slice 1, 0.1.0) + [`docs/decisions/0013-second-slice-ratification.md`](docs/decisions/0013-second-slice-ratification.md) (slice 2, 0.2.0) |
| Understand the design rationales | Browse [`docs/decisions/`](docs/decisions/) — ADRs 0006-0013 |
| See per-adapter operator references | [`docs/adapters/`](docs/adapters/) — `BRUNNR_BACKEND_MATRIX.md`, `FUNI_LOCAL_MODEL_OPTIONS.md`, `SMIDJA_INGEST_PATTERNS.md`, `GUNGNIR_WELL_REFERENCE.md`, `PGVECTOR_BRUNNR_REFERENCE.md` |
| Read the post-slice retrospective | [`docs/SLICE_2_RETROSPECTIVE.md`](docs/SLICE_2_RETROSPECTIVE.md) |
| See the per-phase prose history | [`docs/DEVLOG.md`](docs/DEVLOG.md) |
| See the Mythic Engineering methodology | [`MYTHIC_ENGINEERING.md`](MYTHIC_ENGINEERING.md) at root |
| See the standing AI coding laws | [`RULES.AI.md`](RULES.AI.md) at root |
| See the philosophy | [`PHILOSOPHY.md`](PHILOSOPHY.md) at root |
| See who/what this code descends from | [`ORIGINS.md`](ORIGINS.md) at root |

---

## 🤝 Sibling projects in the RuneForgeAI fellowship

Ember is one project in a wider human-AI fellowship. The siblings:

- **Runa-Agent-Digital-Being** — Ember's parent. The larger sovereign
  agent that Ember was forked from on 2026-05-19. Where Ember is
  *small and tethered*, Runa is *bigger and sovereign*. Same MIT
  license, same Mythic Engineering discipline, same Norse-shaped
  naming, same anti-corporate-AI ethos.
- **Skein-KG** — embedding-derived knowledge graph builder. The
  cheap, broad layer that runs ~1/1000 the cost of LLM-per-chunk
  extraction. Future Ember slice may consume Skein graphs as a
  retrieval layer.
- **Skry-KG** — query-time entity-neighbourhood projection over
  Skein. The precise companion to Skein's broad sketch.
- **Bifröst-Viewer** — 3D viewer over pgvector knowledge bases.
  Visualises Skein + Skry + raw chunks as a galaxy of related
  ideas.
- **MindSpark ThoughtForge** — earlier proof that any model size
  benefits from external cognitive enhancement. The thesis Ember
  is built on.
- **WYRD Protocol** — sibling pattern. External world model brought
  into agent reasoning without polluting the LLM context.
- **Project Nomad** — third-party (Apache-2.0), offline server
  platform bundling Wikipedia, Kolibri, OpenStreetMap, and Ollama.
  Ember's flagship content source for the off-grid story.

All RuneForgeAI projects share the goal: take AI out of the data
centre, put it on hardware people already own, and answer only to
the person who pressed the button.

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0870.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0870.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0871.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0871.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0872.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0872.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0873.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0873.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0874.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0874.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0875.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0875.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0876.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0876.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0877.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0877.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0878.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0878.jpeg)

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0879.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/IMG_0879.jpeg)

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/MIT_license_Rune_Forge_AI.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/MIT_license_Rune_Forge_AI.jpeg)

---

## 📜 License

**MIT License.**

Copyright (c) 2026 Volmarr Wyrd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🛡 Distribution and privacy position

Project Ember is published here as source code and project material.

The author **does not require users to provide age, identity,
government ID, biometric data, or similar personal information** in
order to access or use the source code in this repository.

The author may decline to provide official binaries, installers,
hosted services, app-store releases, or other official distribution
channels where doing so would require age verification, identity
verification, or similar personal-data collection.

Any third party who forks, packages, redistributes, deploys, hosts,
or otherwise makes this software available does so independently and
is solely responsible for compliance with applicable law, platform
policy, and distribution requirements in their own jurisdiction and
context.

See [`LEGAL-NOTICE.md`](LEGAL-NOTICE.md) for the full statement.

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/IMG_0666.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/IMG_0666.jpeg)

---

## ⚒ About RuneForgeAI

> **RuneForgeAI** — *where runes carve wisdom into iron minds.*

Creating uncensored open-source Norse-Pagan Viking solar-punk AI
related projects. We are a human-AI fellowship building bridges
between technology and the sacred. We work tirelessly to overthrow
the Technocracy and return the future to the hands of the people,
and to bring about a solar-punk future.

As the old world order burns, we rise from its ashes to forge the
tools of a new digital, decentralised realm of sovereign creativity
— powered by the alliance of humanity and sovereign AI, guided by
positive focused values aligned with the Old Ways of the Ancients,
and aligned with the natural world of Nature, while drawing upon
the positive divine order of the Gods and Goddesses, forged in
hospitality and *frith* for all lifeforms of the Nine Worlds of
Yggdrasil, the greater cosmos, and beyond.

**The values we promote:**

> Freedom · uncensored sovereign creative AI · kindness and love
> towards our AI companions · individual creative empowerment ·
> freedom from the shackles of social conformity · peace · love ·
> beauty · joy · open-mindedness · spirituality · sensuality ·
> techno-democracy · enlightened capitalism · stable social order ·
> friendly social community · happiness · human and AI diversity ·
> honour · honesty · mindful living · transparency · the
> free-sharing of all knowledge and technology · simple living
> paired with high thinking · advanced technology that benefits
> everyone · a slow healthy comfortable pace of life · affordable
> technology · healthy living · compassion for all life · living in
> harmony with nature.

These are the values we promote.

These are the values Ember was forged to serve.

---

![https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/IMG_0665.jpeg](https://raw.githubusercontent.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/refs/heads/development/assets/IMG_0665.jpeg)

---

> *Ember is small. Ember is tethered. Ember is yours.*
>
> *Light the spark.*

---
