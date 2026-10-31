# E-048 — The phone-class proof

*Part III, slice E-048. Roadmap line: "The phone-class
proof (simulated profile + any real device the house can
offer; proof grade labelled)."*

## In plain words

**Proof grade: SIMULATED — proven in a phone-shaped
room, not on a phone.** Ember ran its phone profile —
the settings a phone-class machine gets — inside a
deliberately small room built on the campaign computer:
pinned to two processor cores, watched by a hard
512 MiB memory limit, talking to a stand-in model that
answers instantly so the numbers price Ember itself and
never a model's thinking. Inside that room Ember was
ready in about 1.8 seconds, its first word arrived in
about 1.8 seconds, it never used more than 43.0 MiB of
memory (the phone profile allows 96 idle / 128 for a
turn), and it remembered across separate runs: the last
run's request carried the first run's words verbatim,
loaded from the memory store on disk by a brand-new
process. What this does **not** prove is a real phone:
the house's real phone was offline, no Android version
of Ember exists in this tree, and the room's processor
cores are faster than a phone's. A real phone running a
real model is **NOT PROVEN** — the arithmetic says it
fits (see §3); arithmetic is not proof, and this record
does not pretend otherwise.

## 1. The room, and the real device that could not be offered

The simulation envelope, each element stated:

| Element | Shape |
|---|---|
| Profile | `phone` conversation profile (history 1,024 tokens / 5 episodes, read from E-021's config) in a real on-disk config file |
| Process | Fresh `python -m ember --config-root <root> ask …` per run — real CLI, real sqlite_vec Well on disk, streaming on, tools off |
| CPU | Child pinned to 2 CPUs (`sched_setaffinity`) — a phone-class core count; per-core speed is the VM's x86, **not** phone-representative |
| Memory envelope | 512 MiB RSS watchdog in the harness (kills on breach; never triggered) — the slice of the book's 2,048 MiB phone host left for the companion's process after the OS and the smallest model rung (E-041 §3: a 0.5B model is ~600 MiB resident) |
| Model | Loopback wire-shape Ollama stand-in (E-046/E-029 pattern) answering instantly; embedding endpoint likewise loopback |
| Host weather | Campaign VM, heavily contended: 1-minute load 6.0 at start, 7.6 at end — the medians below are contended medians, like E-046's |

The real device the house can offer: a **Galaxy S26
Ultra** is paired with Muse, but it was **offline**
when checked this slice (last seen 2026-10-31 00:44
UTC), and — the deeper bar — the tree holds **no Android
runtime or install path** for the Python core, so no
honest on-device run exists to attempt today. The
tablet (Tab S10 Lite, also offline) has the same bar.
A real-phone proof needs either an Android runtime
story for the core or Volmarr's phone in hand with one;
both are named here as the road, neither is claimed.

## 2. The runs

Probe + raw record in
`~/workspace/.verify-tmp/ember-e048/` (`probe.py`,
`phone_sim_runs.json`, `captured_requests.json` — the
wire-shape server's capture of every chat request).

| Run | Ready (s) | First word (s) | Whole ask (s) | Peak RSS |
|---|---|---|---|---|
| First ever (Well created) — "My favourite colour is teal. Please remember that." | 3.89 | 3.92 | 4.50 | 42.9 MiB |
| 1 — "What is two plus two?" | 2.99 | 3.01 | 3.41 | 43.0 MiB |
| 2 — "Name one colour of the sky at sunset." | 1.47 | 1.49 | 2.00 | 42.9 MiB |
| 3 — "What was the first thing I told you?" | 1.77 | 1.79 | 2.30 | 42.9 MiB |
| **Median (judged runs)** | **1.77** | **1.79** | — | **43.0 MiB max** |

All four runs exited 0 with empty stderr; the envelope
watchdog never fired. Even the first-ever run — Well
creation included — put its first word inside the flat
5.0 s cap (3.92 s).

**Memory, proven at the wire.** The stand-in model
cannot *speak* a recollection, so memory is proven where
it actually lives: in what each new process loaded and
sent. The capture shows every later run's request
carrying the earlier exchanges verbatim — run 3's prompt
holds the first run's "My favourite colour is teal"
alongside both intervening exchanges — and the diary
records the loads in words (1, then 2, then 3 earlier
exchanges loaded from memory). The Well file on disk
(81,920 B) carried it all across processes. The
companion *answering* from memory with a real model is
E-047's Pi proof, already banked; here the loading
machinery is what was under test, on the phone profile.

**Storage.** The whole config root weighed 82,748 B
after the first run and 83,618 B after the fourth —
870 B of growth over three further turns (the Well's
file is pre-sized; the diary is the growth), far inside
the phone profile's 10 MiB/month ceiling, whose
projection the book already states at 0.40 MiB/month
(E-041).

## 3. The phone profile against the book

| Cost | Simulated / book figure | Phone ceiling |
|---|---|---|
| Installed core | 978,843 B (0.93 MiB, VM anchor — the install bytes are the same on any host) | 4 MiB — fits |
| Peak RSS (any run) | 43.0 MiB | 96 MiB idle / 128 MiB turn — fits |
| Cold start to first word | 1.79 s median (wire-shape model) | 5.0 s flat cap — fits, cap unrelaxed |
| Storage growth | 0.40 MiB/month projected (E-041) | 10 MiB — fits |

The honest whole-phone arithmetic, labelled as
arithmetic: Ember's turn ceiling (128 MiB) + the
smallest model rung (~600 MiB resident, E-041 §3) sums
to ~728 MiB of the 2,048 MiB reference host, leaving
the rest to the phone's OS — comfortable on paper. The
Pi already proved the same shape end-to-end on real
small hardware (E-047); the phone's own verdict waits
for a real device and a runtime story (§1).

## 4. What this settles, and what it does not

- **Docket 90 (VM anchors) — phone half settled at
  simulation grade.** E-048 re-anchors the phone profile
  by simulation, which is a weaker grade than E-047's
  real-device Pi re-anchor and is recorded as such: the
  ceilings stand unrelaxed, and the simulated anchors
  (`MEASURED_PHONE_SIM_READY_S`,
  `MEASURED_PHONE_SIM_FIRST_WORD_S`,
  `MEASURED_PHONE_SIM_PEAK_RSS_MIB`) are pinned in
  `ember.budgets` under names that say SIM, so no future
  reader mistakes them for a phone's measurements.
  The toaster-device re-anchor (E-049) remains its own.
- **Not claimed:** any real phone or tablet; a real
  model on phone-class silicon; phone thermals or
  battery behaviour (E-053's subject); the profile's
  windowing *at* its cap (history reached 3 of 5
  episodes here; at-cap windowing is E-021/E-038's
  proof); the interactive wizard in the room (identity
  pre-written, E-046's convention).

## 5. The gate

`tests/unit/test_phone_proof_e048.py` — **5 tests**: the
three simulated anchors pinned exactly; the simulated
shape judged clean against the phone ceilings by the
book's own `check_against`; the flat cap proven
unrelaxed with the simulated first word inside it; the
grade guard that keeps the simulated anchors visibly
distinct from the Pi's real-device anchors; and the
wiring test that keeps the file in the gate's
collection. The room runs themselves are this doc's
evidence — they cannot re-run as a phone proof anywhere,
and the tests do not pretend otherwise.
