# E-032 — The Day-One Flow: Install → First Model → First Chat

*Part II, slice E-032. The flow a stranger actually walks, run end
to end, timed, and friction-audited. Part XII's Stranger Test
consumes this doc: its timings, its friction table, and its honest
limits are the baseline the Stranger Test is judged against.*

## What was run, and where

The full flow was run for real in a **clean Python venv** on the VM
profile (Python 3.12.3) — no system site-packages, which matters:
the VM's system Python carries PyYAML and sqlite-vec already, and
either one would have hidden the day's headline friction. The
model side was a loopback Ollama **wire-shape** server (the E-029
pattern: `/api/version`, `/api/embed`, `/api/chat` NDJSON), because
no Ollama daemon exists on the VM (E-006). Everything Ember-side —
install, wizard, config write and reload, Well open, probe, chat
turn, persistence — is the real code, installed from this tree.

| Step | Measured (VM profile) | Notes |
|---|---|---|
| `python3 -m venv` (fresh) + `pip install --upgrade pip` | 26.79 s + 19.92 s | CORRECTION (same day): the figure first banked here, 1.85 s, was a venv re-run over the already-created venv, not a fresh create — the fresh-create runner log (26.79 s) arrived after banking and supersedes it |
| `pip install <tree>[sqlite_vec]` | 19.24 s | builds the wheel (290,650 B) + sqlite-vec 0.1.9 from PyPI |
| `ember --help` | 0.46 s | exit 0 |
| Day one: `ember ask "Hello, who are you?"` (wizard + first chat) | 1.28 s | exit 0; wizard's 5 prompts answered with defaults; reply `day-one answer` with the probe citation |
| Second run: `ember ask` (no wizard, config reloaded) | 0.93 s | exit 0 |

Not in the table, deliberately: **Ollama's own install and the
model pull** (`phi3:mini` ≈ 2.3 GB per `deploy/pi/INSTALL.md`) were
not measured — no Ollama on this machine. A real-model day one is
**NOT PROVEN** here; Part III owns hardware proof, device named
there. The PyPI name `ember-agent` was likewise not installed from
PyPI in this slice (the local tree is the campaign's source of
truth; INSTALL.md's git-install fallback stands).

## The friction audit — six findings, three of them breaks

### F1 — Closed stdin crashed the wizard (docket 15, CLOSED)

Hjarta caught Ctrl-C but not EOF. `ember ask … < /dev/null`, a
script that ran out of answers, or a dropped terminal produced a
raw `EOFError` traceback and no state. Reproduced in-process
pre-fix. **Fix:** Hjarta treats EOF exactly like Ctrl-C — a clean
abort at the current state, nothing written — and `ember setup`
reports it as "Setup did not complete", exit 1.

### F2 — Hjarta wrote a config the documented install cannot read (docket 88, CLOSED)

The sharpest day-one break in the tree. The documented install is
`pip install ember-agent[sqlite_vec]` — which does **not** include
PyYAML. But Hjarta always wrote `~/.ember/config/ember.yaml`, and
the loader requires PyYAML for YAML. Proven in the clean venv
(which has no `yaml` module): with an `ember.yaml` in place — the
exact file the old Hjarta wrote — **every** `ember` command exits 1
with "PyYAML is not installed". So a stranger following the guide
finished the wizard and immediately lost their Ember: the first
launch's own post-setup config reload died, and so did every later
launch, until they happened to install a second extra the guide
never named at that step.

**Fix:** the config writer chooses by what the machine can read —
PyYAML importable → `ember.yaml`, byte-for-byte the old behaviour;
otherwise → `ember.toml`, which the loader reads with the standard
library alone. In the clean venv the wizard now writes
`ember.toml`, the same-launch reload succeeds, and the second run
chats. The format is the only difference; no choice is lost.

### F3 — A Well path typed in the wizard was silently forgotten (docket 87, CLOSED)

The wizard's Well prompt invites a different path, probes *that*
Well — and then wrote a config with no trace of the choice, so the
next `ember chat` reopened the **default** Well. The operator's
chosen store (probe chunk and all) sat orphaned while Ember
answered from a different, empty one. The writer's own docstring
always promised this extras shape ("an alternative Brunnr path");
Hjarta simply never passed it. **Fix:** a typed path is persisted
as `brunnr.sqlite_vec.path` in the written config (both formats)
and reloaded on the next launch; accepting the default writes no
override, pinned by test.

### F4 — The install guide's wizard walkthrough omitted a question (fixed)

`deploy/pi/INSTALL.md` listed the wizard's steps but skipped the
tools question that stands between naming and writing identity —
a stranger following the numbered list met an unlisted prompt.
The list now matches the wizard (10 steps), and names the
`ember.toml` case from F2.

### F5 — The wizard pointed TOML users at a YAML file (fixed)

The tools prompt said "change this later by editing
~/.ember/config/ember.yaml" — wrong file for exactly the installs
F2 is about. The prompt now names the config folder and both
filenames.

### F6 — The probe chunk answers first (known, not a defect)

The first chat's reply cites Hjarta's probe chunk
(`ember-hjarta-probe`). INSTALL.md already discloses the probe and
that it "can be deleted later". Recorded so the Stranger Test
does not re-file it.

## What a stranger's day one now is

1. Install Python package + one extra (`[sqlite_vec]`); Ollama and
   its two models are the only other installs, both Ollama's own
   steps in the guide.
2. Run `ember chat` (or `ask`). Five prompts, every one answerable
   by pressing Enter: begin → Ollama → default Well → default name
   → tools off. Nothing is written until the last step; Ctrl-C or
   a closed stdin at any point leaves no half-state.
3. The same invocation reloads the config the wizard just wrote —
   in whichever format this machine can read — and the first chat
   proceeds. Later launches skip the wizard entirely.

## Tests

`tests/unit/test_day_one_flow_e032.py` — **9 passed**: EOF at the
greet and mid-wizard (clean abort, no identity), setup's EOF
report; TOML fallback round-trip of identity + tools + Well path
with PyYAML "absent", YAML still preferred when present; the
wizard persisting a typed Well path (and writing no override for
the default); the pyproject install contract (entry point, zero
core dependencies, the documented extras exist); and the full
flow — wizard (exactly 5 prompts) → config reload with the chosen
name → first chat over the loopback server, reply rendered,
Episode persisted.
