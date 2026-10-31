# E-049 — The Toaster Test

*Part III, slice E-049. Roadmap line: "The Toaster Test:
the smallest honest target the house can muster (oldest/
smallest machine available) runs the companion through
the day-one flow — the project's name, cashed or
honestly graded."*

## In plain words

**The name is cashed for Ember itself — and honestly
not cashed for a whole companion living alone on a
512 MiB machine.** Ember ran its smallest ("toaster")
settings end to end on the smallest real computer in
the house, talking to the smallest real language model
that computer can serve, and remembering across runs.
Ember's own share is tiny: ready in about a fifth of a
second, never more than 27.2 MiB of memory, installed
under 2 MB — inside every toaster ceiling with room to
spare. But a toaster-sized *whole* companion is a
different claim, and this test measured it instead of
rounding it: the two model programs the normal day-one
shape loads (the chat model and the embedding model)
together need about a gigabyte by the model server's
own accounting — twice the whole 512 MiB toaster host,
before Ember or the operating system take a byte. So:
**the companion core runs on a toaster; a self-contained
companion-plus-models on a literal 512 MiB host does
not, on today's model rungs. That half of the name is
NOT cashed, and the comfortable member of the toaster
class remains the 1 GB-and-up machine** (E-041 §2's
arithmetic, now confirmed by measurement).

## 1. The smallest honest target the house can muster

| | |
|---|---|
| Device | **Mimir** (`purpleviking1`) — Raspberry Pi 5 Model B Rev 1.1, aarch64, 16 GiB RAM — the house's smallest computer |
| Why this device | No Pi Zero-class or older/smaller machine exists in the house; the paired phone (Galaxy S26 Ultra) and tablet (Tab S10 Lite) were offline (E-048). The Pi 5 is pi-class hardware — this test runs the **toaster profile** on it, and claims exactly that, never a Pi Zero run |
| Source | Clean `git clone --depth 1` of `yrsa/ember-road-build` at **c4c7cdc** — the campaign head, hash-verified on the device |
| Install | Fresh venv, `pip install ./repo` + `sqlite-vec` 0.1.9; `ember --help` exit 0 on-device |
| Profile | `toaster` conversation profile (history 512 tokens / 3 episodes, read from E-021's config), pre-written identity (the wizard is a person's pace — E-046's convention), streaming on, tools off, `num_predict` capped at 128 |
| Chat model | **qwen2.5:0.5b** (397 MB on disk) — the smallest rung of the model ladder, pulled to the device for this test; Ember's FUNI table's own smallest class |
| Embedding model | **nomic-embed-text** (274 MB) — Ember's default, real embeddings into a real sqlite_vec Well on device storage |
| Device weather | Load average ~3.8 during the runs (a sibling campaign's heavy process was resident on the device); temperature after the runs 45.2 °C — no thermal pressure |

Everything ran in `/home/pi/ember-e049/` on the device.
No Docker anywhere; the device's own Ollama served
both models.

## 2. The runs

The E-047 probe, re-pointed at the toaster install:
each run a fresh `python -m ember --config-root <root>
ask …` process, timestamping the "is ready." line and
the first word of the streamed reply, polling the
child's RSS. Raw record: `probe_results.jsonl` in
`/home/pi/ember-e049/` on Mimir.

| Run | Ready (s) | First word (s) | Whole ask (s) | Peak RSS |
|---|---|---|---|---|
| First ever (Well created, both models cold) — "Hello. Please reply with one short sentence saying you are awake." | 0.31 | 11.26 | 14.82 | 27.2 MiB |
| 1 — "What is two plus two? Answer in one short sentence." | 0.21 | 2.55 | 4.06 | 27.1 MiB |
| 2 — "Name one colour of the sky at sunset. One short sentence." | 0.20 | 1.15 | 2.53 | 27.1 MiB |
| 3 — "What was the first question I asked you in this conversation? Quote it back briefly." | 0.28 | 2.18 | 3.76 | 27.1 MiB |
| **Median (judged runs)** | **0.21** | **2.18** | — | **27.2 MiB max** |

Replies were real and correct: "I am awake and ready
to assist you…", "Two plus two equals four.", "One
color of the sky at sunset is orange."

**Memory, proven in the machinery, graded at the
model.** The diary records each new process loading
the earlier exchanges from the Well on disk — 1, then
2, then 3 earlier exchange(s) — and run 3's reply did
reach back to the first exchange ("The first question
I asked you was "Hello.""). It did not quote the first
question in full: a 0.5B model's summarising is weak
(phi3:mini on the same machinery in E-047 recalled the
substance accurately). The honest split: cross-process
memory on the toaster profile is **proven**; recall
*quality* at the smallest model rung is **partial**,
and it is the model's limit, recorded under its name.

**First word vs the 5.0 s cap.** The first word here
(2.18 s, real model included) happens to sit *inside*
the cap, because the 0.5B rung thinks fast. It is
still not the cap's subject: the cap prices Ember's
own startup, whose number is ready — **0.21 s**, ~24×
inside the cap, which stands unrelaxed. The first-ever
run's 11.26 s first word is the two models loading
from SD, stated as measured.

**Storage.** The whole config root after four turns
weighed 83,546 B (Well 81,920 B pre-sized, diary
1,199 B) — the book's 0.40 MiB/month projection
against the toaster's 2 MiB/month ceiling stands.

## 3. The grading: core cashed, whole host not cashed

| Cost | Toaster measured (Pi) | Toaster ceiling |
|---|---|---|
| Installed core | 1,956,428 B (1.87 MiB, bytecode caches incl.) | 2 MiB — fits |
| Ember peak RSS (any run) | 27.2 MiB | 64 MiB idle / 64 MiB turn — fits |
| Ember-side cold start (ready) | 0.21 s | 5.0 s flat cap — fits, cap unrelaxed |
| First word, real smallest model included | 2.18 s | *not an Ember ceiling* |
| Storage growth | 0.40 MiB/month projected (E-041) | 2 MiB — fits |

The whole-host sum, **measured this slice** by
`ollama ps` on the device with both day-one models
loaded: the qwen2.5:0.5b runner reports **442 MB** and
the nomic-embed-text runner **565 MB** — **~1,007 MB
of model house on a 512 MiB host**, before Ember
(27.2 MiB measured) or any operating system. Even the
chat model alone, plus the Tiny doc's OS figure
(~150 MB, E-041 §2) and Ember's 64 MiB turn ceiling,
sums to ~656 MB. (The runners' RSS in `ps` at the same
moment summed to ~864 MiB; either accounting exceeds
the host.) Docket 66's open grading is therefore
closed by measurement, not arithmetic: **on a literal
512 MiB host, today's smallest Ollama-served companion
does not fit; on the 1 GB members of the toaster class
the model house fits and the core's fit is proven
above.** A smaller serving shape (an embedding-free
Well configuration, a sub-0.5B rung, a different
server) is a future road, named here and not claimed.

## 4. What this settles, and what it does not

- **Docket 90 (VM anchors) — toaster half settled, and
  with it the docket.** E-049 re-anchors the toaster
  profile on real ARM hardware: ready 0.21 s, peak
  27.2 MiB, installed 1,956,428 B, all pinned in
  `ember.budgets` and judged clean against the toaster
  ceilings by the book's own `check_against`. Pi
  (E-047), phone-sim (E-048) and toaster halves are
  all settled at their stated grades.
- **Docket 66 (the Tiny profile's numbers) — grading
  closed.** The 512 MiB whole-companion sum is
  disproven for the default two-model shape by direct
  measurement (§3); the book's replacement figures
  (E-041) stand as the citable truth.
- **E-032/E-040's real-model day one — now proven on
  the smallest profile too**, with the smallest model
  rung: install → config → real chat model → real
  embeddings → real Well → memory across processes,
  end to end on a real small machine.
- **Not claimed:** a Pi Zero 2 W or any literal
  512 MiB host running anything (no such device in
  the house); the interactive wizard on-device
  (identity pre-written, as in E-046/E-047); recall
  quality at the 0.5B rung beyond §2's partial grade;
  any member program (the proof is the Ember core).

## 5. The gate

`tests/unit/test_toaster_proof_e049.py` — **6 tests**:
the four toaster anchors pinned exactly; the Ember-side
shape judged clean against the toaster ceilings by the
book's own `check_against`; the flat cap proven
unrelaxed with the ready anchor far inside it; the
real-model first word pinned as record-not-breach
beside it; the whole-host verdict pinned as a test
(docket 66: the measured model runners sum past the
512 MiB host); and the wiring test that keeps the file
in the gate's collection. The device runs themselves
are this doc's evidence — they cannot re-run on the
VM, and the tests do not pretend otherwise.
