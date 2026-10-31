# E-047 — The Pi proof

*Part III, slice E-047. Roadmap line: "The Pi proof: the
full companion on Mimir-class hardware (real Pi or NOT
PROVEN, stated plainly)."*

## In plain words

**PROVEN — on a real Raspberry Pi, with a real model.**
Ember was installed fresh on Mimir — the house's Raspberry
Pi 5 — and held real conversations with phi3:mini, the
very model Ember's own defaults recommend for a Pi,
remembering across separate runs what it had been told.
Ember itself is tiny on the Pi: it is ready to talk in
about a fifth of a second, never used more than 27.1 MiB
of memory (the smallest profile's ceiling is 64 MiB), and
the installed program weighs under 2 MB. The one slow
number is the model's, not Ember's: the first word of a
reply took about 5.7 seconds because a language model
thinking on a Pi's CPU takes that long to begin. That
cost belongs to the model, it is the same cost any Pi
companion pays, and it is recorded here under its own
name rather than hidden inside Ember's numbers.

## 1. The device and the install

| | |
|---|---|
| Device | **Mimir** (`purpleviking1`) — Raspberry Pi 5 Model B Rev 1.1, aarch64, 16 GiB RAM, 469 GB SD (202 GB free) |
| OS Python | 3.11.2 (Ember requires ≥3.11) |
| Model server | Ollama 0.20.5, already resident on the device |
| Chat model | **phi3:mini** (2.2 GB) — Ember's documented default for a Pi 5 |
| Embedding model | **nomic-embed-text** (274 MB, pulled for this proof) — Ember's default |
| Source | Clean `git clone --depth 1` of `yrsa/ember-road-build` at **fae0e0b** — the campaign tree itself, hash-verified on the device |
| Install | Fresh venv, `pip install ./repo` + `sqlite-vec` 0.1.9; `ember --help` exit 0 on-device |

Everything ran in `/home/pi/ember-e047/` on the device.
The config was the ordinary operator shape: a pre-written
identity (the day-one wizard is a person's pace, not a
machine's — E-046's convention), the `pi` conversation
profile, streaming on, tools off, `num_predict` capped at
128 to bound Pi-CPU generation, and a real sqlite_vec
Well on device storage. No Docker anywhere; the Pi's own
Ollama service served the model.

## 2. The runs

A probe on the device spawned each run as a fresh
`python -m ember --config-root <root> ask …` process,
timestamped the "is ready." line and the first word of
the streamed reply (the first content after the banner's
prompt mark), and polled the child's RSS. Raw record:
`probe_results.jsonl` in `/home/pi/ember-e047/` on Mimir;
probe script sha256-pinned in the slice workpapers.

| Run | Ready (s) | First word (s) | Whole ask (s) | Peak RSS |
|---|---|---|---|---|
| First ever (Well created, model cold) | 0.36 | — (see note) | 64.91 | 27.1 MiB |
| 1 — "What is two plus two?" | 0.18 | 5.17 | 5.64 | 27.1 MiB |
| 2 — "Name one colour of the sky at sunset." | 0.19 | 5.69 | 6.08 | 27.1 MiB |
| 3 — "What was the first question I asked you?" | 0.17 | 6.37 | 24.60 | 27.1 MiB |
| **Median (judged runs)** | **0.18** | **5.69** | — | **27.1 MiB** |

Replies were real and correct: "Four", "Orange", and —
the run that proves companionship rather than mere
answering — run 3, in a brand-new process, accurately
summarised the first-ever run's greeting ("You initially
greeted me and requested a response indicating
awakening…"). The Well on device storage (store.db,
81,920 B after four turns) carried the memory across
processes, embedded by the real nomic-embed-text.

Notes on the two honest wrinkles:

- **First-ever first word is not recorded.** The first
  probe version timed the chat banner instead of the
  model's first token; the flaw was caught from its own
  output, the probe was fixed (first content after the
  banner's prompt mark), and only the fixed probe's runs
  are judged. The first-ever run's total (64.91 s —
  phi3:mini loading from SD + first generation) and its
  ready time stand as measured.
- **First word vs the 5.0 s cap.** E-046's flat cap
  prices *Ember's own* cold start against an instantly
  answering wire-shape model, and said in its §5 that a
  real-model cold start was NOT PROVEN and owned by this
  slice. Now it is proven, and the split is exact: Ember
  is ready in **0.18 s** (~28× inside the cap — the cap
  stands, unrelaxed), and the remaining ~5.5 s is
  phi3:mini's prompt processing on the Pi CPU. Judging
  the model-included number against Ember's cap would
  fold a model's cost into Ember's book, which the book
  forbids by design (E-041). Both numbers are pinned in
  `ember.budgets` under distinct names
  (`MEASURED_PI_READY_S`,
  `MEASURED_PI_FIRST_WORD_REAL_MODEL_S`) with a test that
  keeps them from ever being merged.

## 3. The Pi against the book

| Cost | Pi measured | Pi ceiling | Toaster ceiling (for scale) |
|---|---|---|---|
| Installed core | 1,951,508 B (1.86 MiB, bytecode caches incl.) | 8 MiB | 2 MiB — fits |
| Ember peak RSS (any run) | 27.1 MiB | 192 MiB turn / 128 MiB idle | 64 MiB — fits |
| Ember-side cold start (ready) | 0.18 s | 5.0 s flat cap | same cap — fits |
| First word, real model included | 5.69 s | *not an Ember ceiling* | — |

Ollama's own runner held ~3.7 GiB RSS with phi3:mini
loaded — the model's house, stated for completeness and
charged to no Ember ceiling. Device temperature after
the runs: 44.4 °C — no thermal pressure. The venv as a
whole (interpreter env included) weighed 27 MB; the
checkout beside it is the monorepo's, not an install cost.

## 4. What this settles, and what it does not

- **Docket 90 (VM anchors) — Pi half settled.** E-047 was
  to re-derive, not merely relax, on real hardware: the
  ready anchor is re-derived (0.18 s), the cap stands.
  The phone-class (E-048) and toaster-device (E-049)
  re-anchors remain theirs to make.
- **E-032/E-040's standing NOT PROVEN — closed for the
  Pi.** "Real-model day one" was unproven on the VM (no
  Ollama there); on the Pi the full default shape —
  install, config, real model, real embeddings, real
  Well, memory across processes — ran end to end.
- **Not claimed:** the interactive wizard on-device
  (identity was pre-written, as in E-046); an hour-long
  Pi idle (E-045's discipline is VM-proven; the Pi runs
  show a 27.1 MiB working set and no persistent process
  in the `ask` shape); the toaster device verdict
  (E-049's — this Pi is pi-class, not the smallest
  honest target); any member program (the proof is the
  Ember core, the roadmap's subject).

## 5. The gate

`tests/unit/test_pi_proof_e047.py` — **5 tests**: the
four Pi anchors pinned exactly; the Ember-side shape
judged clean against the pi ceilings by the book's own
`check_against`; the flat cap proven unrelaxed with the
ready anchor far inside it; the model-included first
word pinned as record-not-breach beside it; and the
wiring test that keeps the file in the gate's collection.
The device runs themselves are this doc's evidence —
they cannot re-run on the VM, and the tests do not
pretend otherwise.
