# The Ember Budget Book

*Published in-repo at slice E-055 (Part III). The book in
code is `ember.budgets` (`src/ember/budgets.py`); the
ceilings below are read from it, and
`tests/unit/test_budget_book_e055.py` fails if this
document and the code ever drift apart. Every measurement
named here was taken by the slice cited beside it; the
full method and raw numbers for each live in that slice's
record under `docs/architecture/`.*

## In plain words

**Ember's core is small, and that is now measured, not
believed.** Installed, the whole companion core weighs
under a megabyte. Sitting idle with its memory open it
uses about 41 MB of RAM; answering a turn, about the
same — on the campaign's test machine, on a real
Raspberry Pi it used even less (27 MB). Left alone for a
full hour it spent no processor time at all. A month of
daily companionship grows its storage by under half a
megabyte. And on the smallest machine this house owns, a
Raspberry Pi 5, the core ran the whole first-day flow —
install, first chat, remembering across restarts —
inside the smallest profile's limits, talking to a real
(and deliberately tiny) language model.

What eats a small machine was never Ember. It is the
language model, which is a separate program with its own
sizes, and this book never hides the model inside
Ember's numbers. Where a whole-companion claim cannot be
made honestly, this book says so in plain words — see
§6 before quoting any number from it.

## 1. The ceilings (the promises)

Ceilings for the **Ember core only** — the Python
package, its default local memory store (the Well), its
diary and its journal. The model is not included (§6).

| Profile | Reference host | Install | Idle RAM | Turn RAM | Storage growth / month | Cold start to first word |
|---|---|---|---|---|---|---|
| toaster | 512 MiB | 2 MiB | 64 MiB | 64 MiB | 2 MiB | 5.0 s |
| phone | 2,048 MiB | 4 MiB | 96 MiB | 128 MiB | 10 MiB | 5.0 s |
| pi | 4,096 MiB | 8 MiB | 128 MiB | 192 MiB | 25 MiB | 5.0 s |
| laptop | 8,192 MiB | 16 MiB | 256 MiB | 384 MiB | 100 MiB | 5.0 s |

"Reference host" is the smallest host the profile is
named for in this book, stated so a reader can add the
model's size to the right host honestly. The cold-start
cap is flat across profiles on purpose (E-046): starting
is the same process everywhere, and no machine size is
granted a slower start.

Each profile also carries the history a turn may hold —
read from the conversation config itself, so the book
cannot drift from the code: toaster 512 tokens /
3 episodes, phone 1,024 tokens / 5 episodes,
pi 2,048 tokens / 8 episodes, laptop 4,096 tokens /
12 episodes.

These ceilings are enforced, not aspirational: E-042
turned them into tests that re-derive every shape in a
fresh process and judge it against this table, and those
tests run in every slice gate of this campaign. E-056
gathers all of Part III's gates into the permanent
regression armour.

## 2. The founding measurements (VM, E-041)

Measured on the campaign VM (x86, Python 3.12.3, fresh
processes, memory read from `/proc`):

- **Install: 978,843 bytes in all** — the package
  (729,802 B, byte-identical installed and in source),
  its dist-info (83,102 B) and the one default extra a
  working install carries, `sqlite-vec` (165,939 B with
  its dist-info). Bytecode caches excluded; after first
  run they add ~0.6 MB more. The old front-door claim of
  "~50 MB installed" is struck: it overstates Ember by
  ~50×. The ~3.5 GB "typical install" story is Ollama
  (~700 MB) plus models (~2.6 GB) plus Ember (~1 MB).
- **Idle RAM: 40.7 MiB** — the full chat surface
  imported with the default Well open, the shape a
  running companion actually idles in. The interpreter
  alone is 10.5 MiB of that; the bare chat surface
  without the Well is 25.3 MiB.
- **Turn RAM: 40.1 MiB peak**, flat across all four
  profiles at fixture scale (five real chat turns
  against the real Well, history at each profile's cap,
  a labelled stand-in model). At this size the core's
  turn cost *is* its idle cost; profiles differ in what
  they allow, not in what a turn weighs.
- **Storage: 694 bytes per turn** — 614 B per episode
  in the Well (measured over 100 typical turns) plus
  ~80 B of diary — projecting to 0.40 MiB per month at
  the reference workload of 20 turns a day. The
  toaster's 2 MiB/month ceiling is reached at ~86 turns
  a day; the book says so rather than rounding up.

The "~50 MB of RAM" claim is true and generous (idle
40.7, turn 40.1 — both under it, now as measured facts).

## 3. How the core got lighter (E-043, E-044)

- **The install cut (E-043).** The wheel was always
  honest (~305 KB, the core only), but the source
  distribution dragged the whole monorepo: ~45 MB
  compressed, 127,162,419 B unpacked. Excluding the
  eleven optional member directories and the heritage
  corpora from the *distribution* (nothing was deleted
  from the repo; members still run from a checkout)
  brought it to **~1.1 MB compressed / 3,464,529 B
  unpacked — a ~41× cut**. A clean install from the cut
  distribution was proven: the core starts, and no
  member lands in the installed packages.
- **The dependency diet (E-044).** Every root
  requirement is now bounded above and below. The diet
  caught a real break: the unbounded model-context
  extra would have installed a major version whose SDK
  removed the very server class Ember starts — a fresh
  install could not have served. Measured shapes: the
  test-only `dev` extra is 7,600,880 B (the combined
  developer set was 89,112,145 B before the split,
  −91.5%); all extras combined weigh 53,703,943 B. The
  core itself still depends on nothing — every extra is
  opt-in.

## 4. The behaviour measurements (E-045 – E-054)

Each row is the slice that measured it; the record
named in the last column holds the method.

| What | Measured | Where |
|---|---|---|
| Idle for one hour (all 4 profiles) | 0.0 s CPU, exactly 1 thread, disk byte-identical (164,616 B), memory never grew (40.8 → 23.0 MiB settling) | E-045 |
| Cold start, toaster profile (VM) | first word median 2.87 s against the flat 5.0 s cap; ~97% of it is process startup; first-ever start 3.60 s | E-046 |
| Update weight | download 293,387 B; unpacks to 775,675 B; applying peaks at 1,844,737 B — the toaster fits it ~7× over | E-052 |
| A month of companionship | 408,566 B in all (600 turns): Well 352,256 B, diary 56,310 B — 680.9 B/turn, inside the book's 694 | E-050 |
| Long (essay-length) turns | 6,144 B per episode; a month of them at reference pace is 3.51 MiB — past the toaster's storage ceiling, inside the phone's | E-050 |
| Battery-shaped work | one 5 s blocking rest spent 0.000 s of CPU (no busy-wait); duty-cycled background work ran at 0.1885 CPU/wall against 0.4117 unshaped, under the same contention | E-053 |
| Thermal patience | background work eases at 1.0 load-per-CPU or 70 °C, yields at 2.0 or 80 °C, and never waits longer than a stated 30 s bound | E-051 |
| Running out of room | features shed in a stated ladder at 75% / 90% / 100% of the turn ceiling — summaries, then semantic search, then the wide history window — each shed and each restore announced in plain words; answering and saving are never shed | E-054 |

## 5. The device proofs

Proof grades are part of the measurement. A number is
only ever claimed for the device and grade named here.

### The Pi proof — REAL device (E-047)

Mimir (`purpleviking1`), a Raspberry Pi 5 Model B
Rev 1.1 (aarch64, 16 GiB RAM), Ember installed fresh
into a clean virtual environment, the `pi` profile,
real models (phi3:mini for chat, nomic-embed-text for
embedding) served by the house's Ollama:

- ready (Ember's own startup) median **0.18 s**;
- first word median **5.69 s** — a real-model number:
  it prices the model's thinking on the Pi's CPU, not
  Ember, and is deliberately not judged against the
  cold-start cap;
- peak memory **27.1 MiB** — inside even the toaster's
  64 MiB turn ceiling;
- installed **1,951,508 B** — inside the pi profile's
  8 MiB install ceiling and the toaster's 2 MiB alike;
- memory proven across processes: a later run recalled
  what the first run had been asked.

### The phone-class proof — SIMULATED (E-048)

No real phone is claimed. The `phone` profile ran on
the campaign VM in a phone-shaped room: pinned to
2 CPUs, a 512 MiB watchdog on its memory (never
triggered), a stand-in model answering instantly, so
the numbers price Ember alone:

- ready median **1.77 s**; first word median
  **1.79 s** — inside the unrelaxed 5.0 s cap, as was
  the first-ever run (3.92 s);
- peak memory **43.0 MiB** — inside the phone ceilings
  (96 MiB idle, 128 MiB turn);
- memory proven at the wire: each later process's
  request carried the earlier exchanges verbatim.

### The Toaster Test — REAL device, honestly graded (E-049)

The smallest honest target the house can muster is the
same Raspberry Pi 5 (the house holds no smaller
computer; the paired phone and tablet were offline),
running the **toaster** profile through the whole
first-day flow — fresh install, fresh memory, real
embedding — against the smallest real model rung the
house can serve, qwen2.5:0.5b:

- ready median **0.21 s**; first word median
  **2.18 s** (real-model, recorded not cap-judged);
- peak memory **27.2 MiB** against the toaster's 64 MiB
  ceilings;
- installed **1,956,428 B** against the 2 MiB ceiling;
- memory proven in the machinery across processes
  (0, 1, 2, then 3 earlier exchanges loaded); spoken
  recall at the 0.5B rung is graded **partial** — the
  small model's limit, named, not Ember's.

**The verdict, in two halves.** The project's name is
cashed for the Ember core: the toaster profile runs the
whole first-day flow inside every toaster ceiling on
real hardware. It is **not cashed** for a whole
self-contained companion on a literal 512 MiB host:
with both first-day models loaded, the model runners
alone held 442 MB + 565 MB (~1,007 MB) — the model
house alone overflows a 512 MiB machine before the
operating system (~150 MB) and Ember are added. The
1 GB members of the toaster class are the comfortable
floor for a whole companion today. That is arithmetic
measured on the device (E-049), not a rounding-down of
the promise.

## 6. What these numbers do not include, and what is NOT PROVEN

- **The model.** Every ceiling and anchor in this book
  prices the Ember core only. Model runners are separate
  programs (the smallest chat rung measured ~442 MB
  resident on the Pi; the default phi3:mini runner
  ~3.7 GiB there). Add the model to the profile's
  reference host openly, per rung.
- **Python itself.** An interpreter is inside every
  memory figure (10.5 MiB of it) but its *install* is
  the host's, not Ember's.
- **The other members.** This book is the core's book.
  Every member's cost, per profile, is the member
  budget table — §7 below (E-057). (One member was
  already weighed for shape: Verdandi's two programs
  are ~20 MiB-class processes on the VM — nerve hub
  21.9 MiB live, heartbeat 18.4 MiB import-level,
  E-041.)
- **Documents a person feeds Ember.** Ingested files
  are bounded by the ingest caps, not by the storage
  ceiling, which prices conversation.

NOT PROVEN, named plainly:

- **A real phone.** The phone proof is simulated
  (E-048): the house's phone was offline and the tree
  holds no phone runtime. No phone number in this book
  is a phone measurement.
- **A real battery's drain.** E-053 measured the
  drain's cause (CPU duty) on a mains-fed VM. Percent
  per hour on a real battery is not proven anywhere.
- **Heat on the Pi.** The thermal policy (E-051) is
  proven on the VM, which exposes no temperature
  sensors; the Pi's own thermal behaviour under Ember
  is not yet measured.
- **A whole companion on 512 MiB.** See §5: graded
  NOT CASHED by measurement, not by opinion.

## 7. The members' costs (E-057)

The core is not the whole monorepo. Every member that
can run, weighed the same way for each: its **tracked
size** (every tracked file in its directory, summed —
the checkout weight), the **smallest profile whose
install ceiling covers that size**, and an
**import-level RAM floor** (a fresh process importing
the member's top package on the VM; the bare
interpreter's own floor by the same method is
10.1 MiB, so a floor is a floor, never a running cost —
the core's running idle is 40.7 MiB, §2, and Verdandi's
running hub is 21.9 MiB live, E-041).

| Member | Tracked files | Tracked size | Smallest profile covering it | Import-level RAM floor |
|---|---|---|---|---|
| `src/` (ember core) | 130 | 831,437 B | toaster | 12.0 MiB |
| `Verdandi/` | 190 | 16,996,351 B | none | 12.6 MiB |
| `kista/` | 25 | 2,770,218 B | phone | 24.2 MiB |
| `mempalace/` | 257 | 59,049,715 B | none | 11.5 MiB |
| `mimir-well/` | 58 | 607,675 B | toaster | 20.8 MiB |
| `seidr_engine/` | 11 | 103,728 B | toaster | 13.3 MiB |
| `astrology-engine/` | 25 | 7,477,309 B | pi | 12.4 MiB |
| `bifrost/` | 10 | 77,916 B | toaster | 15.2 MiB |
| `Hamr/` | 168 | 6,081,769 B | pi | 40.1 MiB |
| `Open-VTT/` | 209 | 6,768,730 B | pi | NOT MEASURED |
| `CloakBrowser/` | 112 | 6,420,853 B | pi | NOT MEASURED |
| `cleasby-vigfusson-old-norse-dict/` | 170 | 24,221,782 B | none | NOT MEASURED |

In plain words: the twelve running members weigh
131,407,483 bytes together, and three of them —
mempalace, the dictionary, and Verdandi (which misses
even the laptop's ceiling by 219,135 bytes) — fit no
profile's install ceiling at all. Their weight is data,
not code: benchmark corpora, a test snapshot, loose
images. And none of it is charged to a core user: the
members are excluded from the core's distribution
(E-043) and never installed with it. A member's cost is
paid only by carrying the whole monorepo or running
that member from a checkout. The rest of the tracked
tree (documents, root images, assets, tests, scaffolding
— roughly 83 MiB) is checkout-only estate, never
installed or run with the companion.

NOT MEASURED, named plainly: Open-VTT's RAM (its Godot
engine is absent here), the dictionary's RAM (a Node
app; its dependencies are not installed here), and
CloakBrowser's RAM — its import needs dependencies this
bare environment lacks, and its real weight is a
proprietary browser binary that is not in this tree at
all; the tracked size above is its wrapper only.

## Appendix — the measured anchors, by their code names

Every anchor in `ember.budgets`, at the value the code
carries. The E-055 tests require each name and value
below to match the code exactly, so this appendix
cannot quietly age away from the measurements.

| Anchor | Value | From |
|---|---|---|
| MEASURED_INSTALL_BYTES | 978,843 | E-041 (VM) |
| MEASURED_IDLE_RAM_MIB | 40.7 | E-041 (VM) |
| MEASURED_TURN_RAM_MIB | 40.1 | E-041 (VM) |
| MEASURED_COLD_START_FIRST_WORD_S | 2.87 | E-046 (VM) |
| MEASURED_PI_READY_S | 0.18 | E-047 (Raspberry Pi 5) |
| MEASURED_PI_FIRST_WORD_REAL_MODEL_S | 5.69 | E-047 (Raspberry Pi 5) |
| MEASURED_PI_PEAK_RSS_MIB | 27.1 | E-047 (Raspberry Pi 5) |
| MEASURED_PI_INSTALLED_BYTES | 1,951,508 | E-047 (Raspberry Pi 5) |
| MEASURED_PHONE_SIM_READY_S | 1.77 | E-048 (SIMULATED) |
| MEASURED_PHONE_SIM_FIRST_WORD_S | 1.79 | E-048 (SIMULATED) |
| MEASURED_PHONE_SIM_PEAK_RSS_MIB | 43.0 | E-048 (SIMULATED) |
| MEASURED_TOASTER_PI_READY_S | 0.21 | E-049 (Raspberry Pi 5) |
| MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S | 2.18 | E-049 (Raspberry Pi 5) |
| MEASURED_TOASTER_PI_PEAK_RSS_MIB | 27.2 | E-049 (Raspberry Pi 5) |
| MEASURED_TOASTER_PI_INSTALLED_BYTES | 1,956,428 | E-049 (Raspberry Pi 5) |
| MEASURED_MONTH_WELL_GROWTH_BYTES | 352,256 | E-050 (VM) |
| MEASURED_MONTH_DIARY_BYTES | 56,310 | E-050 (VM) |
| MEASURED_MONTH_TOTAL_BYTES | 408,566 | E-050 (VM) |
| MEASURED_MONTH_TURNS | 600 | E-050 (VM) |
| MEASURED_WELL_STEADY_BYTES_PER_EPISODE | 585.4 | E-050 (VM) |
| MEASURED_ESSAY_BYTES_PER_EPISODE | 6,144 | E-050 (VM) |
| MEASURED_UPDATE_DOWNLOAD_BYTES | 293,387 | E-052 (VM) |
| MEASURED_UPDATE_INSTALLED_BYTES | 775,675 | E-052 (VM) |
| MEASURED_UPDATE_APPLY_PEAK_BYTES | 1,844,737 | E-052 (VM) |
| MEASURED_BATTERY_REST_CPU_S | 0.0 | E-053 (VM) |
| MEASURED_DUTY_FULL_CPU_FRACTION | 0.4117 | E-053 (VM) |
| MEASURED_DUTY_CONSERVE_CPU_FRACTION | 0.1885 | E-053 (VM) |

The book's storage arithmetic, also from the code:
614 bytes per Well episode + 80 bytes of diary per turn
= **694 bytes per turn**, at a reference workload of
20 turns per day.

*Published by slice E-055, 2026-10-31. The ceilings are
the code's (`ember.budgets`); where this prose and the
code could ever disagree, the code and its gate tests
are the truth and this document is the defect.*
