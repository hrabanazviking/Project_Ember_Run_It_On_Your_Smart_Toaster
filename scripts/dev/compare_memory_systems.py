#!/usr/bin/env python3
"""E-078 — the memory comparison harness.

Runs ONE identical synthetic workload through the three memory
systems Part V must judge (E-077's map):

* **mempalace** (``mempalace/``) — the verbatim archive,
* **mimir-well** (``mimir-well/``) — the living memory,
* **Brunnr** (``src/ember/well/``) — the core's incumbent.

Each system runs in its OWN subprocess (``--system``) so its
peak RSS is its own, writes a JSON fragment, and the parent
(``--all``) aggregates the fragments plus per-profile budget
fits (``ember.budgets``, E-041's book) into one report.

The workload is identical in shape for every system:

* the same 20-item synthetic corpus (canon-flavoured, invented;
  no real companion history — E-089's law applied early),
* the same query strings, fed to each system's *native* search
  (verbatim phrase, full-text terms, paraphrase),
* plus each system's unique rows, which are the point of the
  comparison (E-077 §5): importance / mood / current-truth
  recall for mimir-well, episode recall for Brunnr, and the
  current-truth *contrast* (a superseded fact) for the two
  systems with no supersession at this layer.

Honesty rules baked in:

* **The embedder is held constant.** Brunnr's production
  embedder is an external Ollama service; where no Ollama is
  reachable the harness embeds Brunnr's chunks with the same
  ONNX all-MiniLM-L6-v2 (384-dim) model mempalace uses
  natively, and the report says so. What is compared is the
  stores and their retrieval, not two embedding services.
* **Absence is a measured result.** mimir-well has no vector
  search (E-077 §4.2); its paraphrase row runs its native
  FTS5 search and records what comes back — expected near
  zero, reported, never hidden as a harness gap.
* **Counts come from the runner.** Nothing here estimates;
  sizes are byte sums of the store on disk, latencies are
  ``perf_counter`` medians over repeated queries, RSS is the
  child process's own ``ru_maxrss``.
* Proxy variables are stripped in children: every store here
  is local, and a bracketed ``no_proxy`` is E-005's proven
  ChromaDB failure signature.

Usage (from the repo root, deps supplied on PYTHONPATH —
sqlite-vec for Brunnr, chromadb for mempalace)::

    python3 scripts/dev/compare_memory_systems.py --all \
        --workdir /tmp/ember-e078 --out report.json
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------- #
# The identical workload — 20 synthetic items.                          #
#                                                                       #
# token: a word occurring in exactly this one item (hit detection).     #
# verbatim: an exact phrase from the text.                              #
# fts: three distinctive content words (not the token, not adjacent).   #
# paraphrase: a reworded question sharing no content word with the      #
# text except a place/person anchor — or None (10 of 20 carry one).     #
# --------------------------------------------------------------------- #

CORPUS: list[dict] = [
    dict(slug="ferry", category="knowledge", importance=6, valence=0.1,
         token="quillfeather",
         text="The harbour ferry at Skardvik leaves at the dawn bell and "
              "returns at the dusk bell, carrying salt, dried fish, and "
              "letters between the islands in a quillfeather-marked boat.",
         verbatim="at the dawn bell",
         fts="ferry Skardvik salt",
         paraphrase="When does the boat that carries post between the "
                    "isles set out in the morning?"),
    dict(slug="bees", category="preference", importance=7, valence=0.6,
         token="ambercomb",
         text="The beekeeper at Holt keeps nine hives behind the orchard "
              "and trades ambercomb honey for walrus ivory at the autumn "
              "market.",
         verbatim="behind the orchard",
         fts="beekeeper hives ivory",
         paraphrase="Who looks after the insects that make the sweet "
                    "spread traded when the leaves turn?"),
    dict(slug="forge", category="knowledge", importance=8, valence=0.0,
         token="slaghammer",
         text="A good smith quenches the blade in whale oil, never water, "
              "and tests the edge with a slaghammer tap before the "
              "seax is sold.",
         verbatim="quenches the blade",
         fts="smith edge seax",
         paraphrase=None),
    dict(slug="herbs", category="preference", importance=9, valence=0.8,
         token="moonwort",
         text="For a fever, the healer brews moonwort with yarrow in a "
              "clay pot and gives it at nightfall, sweetened with birch "
              "sap.",
         verbatim="brews moonwort with yarrow",
         fts="healer fever birch",
         paraphrase="What does the herb-woman prepare when someone is "
                    "burning up, and when is it given?"),
    dict(slug="tidemill", category="knowledge", importance=5, valence=-0.1,
         token="millrace",
         text="The tide mill at Ravnvik grinds barley only while the "
              "millrace runs seaward; at slack water the stones rest "
              "and the miller mends sacks.",
         verbatim="while the millrace runs seaward",
         fts="mill barley stones",
         paraphrase=None),
    dict(slug="lighthouse", category="saga_moment", importance=10, valence=-0.8,
         token="stormlantern",
         text="The stormlantern on Hrafnsey was lit by the keeper's "
              "daughter the night the longship broke on the skerries, "
              "and no ship has passed unlit since.",
         verbatim="the night the longship broke",
         fts="keeper skerries ship",
         paraphrase="Who tended the beacon on the island the evening "
                    "the warship wrecked on the rocks?"),
    dict(slug="loom", category="preference", importance=4, valence=0.3,
         token="wadmal",
         text="The weavers of Borgund dye their wadmal cloth with "
              "madder for red and woad for blue, and sell it by the "
              "ell at the spring thing.",
         verbatim="dye their wadmal cloth",
         fts="weavers red blue",
         paraphrase=None),
    dict(slug="nets", category="knowledge", importance=6, valence=-0.3,
         token="corkfloat",
         text="Herring nets are mended with a corkfloat needle and "
              "tarred twine, then hung in the boathouse loft to dry "
              "before the autumn run.",
         verbatim="mended with a corkfloat needle",
         fts="herring twine boathouse",
         paraphrase=None),
    dict(slug="stores", category="knowledge", importance=9, valence=-0.5,
         token="saltbarrel",
         text="For winter the household lays down forty saltbarrel "
              "measures of meal, twelve sides of pork, and dried "
              "apples in the turf storehouse.",
         verbatim="dried apples in the turf storehouse",
         fts="winter household pork",
         paraphrase="What food does the family put away before the "
                    "cold months arrive?"),
    dict(slug="stars", category="knowledge", importance=7, valence=0.2,
         token="waystone",
         text="Sailors steer by the waystone star when the moon is "
              "down, keeping it over the left shoulder until the "
              "fjord mouth opens.",
         verbatim="when the moon is down",
         fts="sailors fjord mouth",
         paraphrase=None),
    dict(slug="shipwright", category="knowledge", importance=8, valence=0.4,
         token="keelpine",
         text="The shipwright chooses keelpine that grew on a north "
              "slope, because slow-grown timber bends without "
              "splitting when the strakes are steamed.",
         verbatim="grew on a north slope",
         fts="timber bends steamed",
         paraphrase="Why does the boat-builder prefer wood from the "
                    "shaded side of the hill?"),
    dict(slug="horse", category="saga_moment", importance=5, valence=0.9,
         token="greyfax",
         text="The greyfax mare won the midsummer race at the meadow "
              "ford and was given a garland of meadowsweet by the "
              "jarl's youngest child.",
         verbatim="won the midsummer race",
         fts="mare meadow garland",
         paraphrase=None),
    dict(slug="wellwater", category="knowledge", importance=10, valence=0.0,
         token="ironbucket",
         text="The ironbucket well behind the hall never freezes, "
              "because its shaft reaches below the frost line to a "
              "warm spring.",
         verbatim="reaches below the frost line",
         fts="shaft spring hall",
         paraphrase="Why does the water source behind the great house "
                    "stay liquid all winter?"),
    dict(slug="oven", category="preference", importance=3, valence=0.7,
         token="ashcake",
         text="Flatbread is baked on the hearthstone and the last "
              "ashcake of the batch is always left for the house "
              "spirits at the door.",
         verbatim="left for the house spirits",
         fts="flatbread hearthstone batch",
         paraphrase=None),
    dict(slug="raven", category="saga_moment", importance=6, valence=-0.6,
         token="oneeyed",
         text="A oneeyed raven follows the fishing fleet from "
              "Hrafnsey and is fed the first sprat of every catch "
              "by the oldest fisherman.",
         verbatim="the first sprat of every catch",
         fts="raven fishing fleet",
         paraphrase=None),
    dict(slug="snowbridge", category="knowledge", importance=7, valence=-0.2,
         token="driftpole",
         text="The snow bridge over Kalldal is marked with driftpole "
              "wands on both sides, because the ice hides the "
              "crevasse until midsummer.",
         verbatim="marked with driftpole wands",
         fts="bridge ice crevasse",
         paraphrase="How do travellers know where the safe crossing "
                    "over the frozen valley lies?"),
    dict(slug="market", category="knowledge", importance=4, valence=0.5,
         token="thingbell",
         text="Market day at Borgund begins when the thingbell rings "
              "from the law rock, and no trading is lawful before "
              "the third ring.",
         verbatim="no trading is lawful",
         fts="trading law rock",
         paraphrase=None),
    dict(slug="salve", category="preference", importance=9, valence=0.85,
         token="pine salve",
         text="The pine salve for rope burns is made from resin, "
              "tallow, and beeswax, and kept in a horn box by the "
              "hearth.",
         verbatim="kept in a horn box",
         fts="resin tallow beeswax",
         paraphrase="What is rubbed on hands hurt by rigging, and "
                    "where is it stored?"),
    dict(slug="ale", category="saga_moment", importance=2, valence=0.95,
         token="yuleale",
         text="The yuleale is brewed with juniper and blessed by the "
              "householder before the first cup is poured for the "
              "ancestors.",
         verbatim="blessed by the householder",
         fts="juniper cup ancestors",
         paraphrase=None),
    dict(slug="grief", category="saga_moment", importance=8, valence=-0.9,
         token="ashship",
         text="When the old lawspeaker died, his ashship was burned "
              "at the shore with his law book and his greyhound "
              "beside him.",
         verbatim="burned at the shore",
         fts="lawspeaker book greyhound",
         paraphrase=None),
]

#: The current-truth contrast pair (E-077 §5): one fact, changed.
TRUTH_OLD = ("The winter market at Skardvik opens on the first day "
             "of the frost month.")
TRUTH_NEW = ("The winter market at Skardvik opens on the fifteenth "
             "day of the frost month.")
TRUTH_QUERY = "winter market Skardvik frost month opens"

#: Brunnr's unique row: conversation turns (operator, reply).
EPISODES: list[tuple[str, str]] = [
    (f"Turn {i}: the traveller asks about road {i}.",
     f"Reply {i}: take the coast path past marker {i}.")
    for i in range(12)
]

K = 5            # recall depth, every system
REPEATS = 2      # per query; the median is kept


def _median_ms(fn, repeats: int = REPEATS) -> tuple[object, float]:
    """Run fn REPEATS times; return (last result, median wall ms)."""
    times: list[float] = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        times.append((time.perf_counter() - start) * 1000.0)
    return result, statistics.median(times)


def _latency_block(samples_ms: list[float]) -> dict:
    ordered = sorted(samples_ms)
    p95 = ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))]
    return {"queries": len(samples_ms),
            "median_ms": round(statistics.median(samples_ms), 3),
            "p95_ms": round(p95, 3),
            "max_ms": round(max(samples_ms), 3)}


def _store_bytes(path: Path) -> int:
    """A SQLite store's true size: the file plus its WAL/SHM
    sidecars, which is where freshly written rows actually live
    until a checkpoint. E-078's first mimir run priced only the
    4 KiB main file and taught the harness this rule."""
    total = 0
    for candidate in (path, Path(str(path) + "-wal"),
                      Path(str(path) + "-shm")):
        try:
            total += candidate.stat().st_size
        except OSError:
            pass
    return total


def _dir_bytes(path: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                pass
    return total


def _rss_kib() -> int:
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _recall_row(system_search, items: list[dict], query_key: str) -> dict:
    """Run one query family; hit = target token in any top-K text."""
    hits = 0
    samples: list[float] = []
    for item in items:
        query = item[query_key]
        texts, ms = _median_ms(lambda q=query: system_search(q))
        samples.append(ms)
        if any(item["token"] in t for t in texts[:K]):
            hits += 1
    row = {"hits": hits, "of": len(items), **_latency_block(samples)}
    return row


# --------------------------------------------------------------------- #
# System children                                                       #
# --------------------------------------------------------------------- #

def run_mimir(workdir: Path) -> dict:
    sys.path.insert(0, str(REPO / "mimir-well" / "src"))
    from mimir_well.core import RunaMemory

    db_path = workdir / "mimir_well.db"
    out: dict = {"system": "mimir-well"}
    # Sizes are priced as the store lies on disk AFTER close
    # (WAL checkpointed): an in-process reading prices the WAL,
    # not the store — the first run's 120 KB/item taught this.
    mem = RunaMemory(db_path=str(db_path))
    out["rss_after_open_kib"] = _rss_kib()
    mem.close()
    out["empty_bytes"] = _store_bytes(db_path)
    mem = RunaMemory(db_path=str(db_path))  # reopened for the run

    ids: dict[str, int] = {}
    add_samples: list[float] = []
    for item in CORPUS:
        start = time.perf_counter()
        mid = mem.add_memory(item["text"], category=item["category"],
                             importance=item["importance"],
                             emotional_valence=item["valence"],
                             tags=["e078"])
        add_samples.append((time.perf_counter() - start) * 1000.0)
        assert mid and mid > 0, item["slug"]
        ids[item["slug"]] = mid
    out["add"] = _latency_block(add_samples)

    def fts(query: str) -> list[str]:
        return [r["content"] for r in mem.fts_search("memories", query, limit=K)]

    def like(query: str) -> list[str]:
        return [r["content"] for r in mem.search_memories(query, limit=K)]

    out["verbatim_fts"] = _recall_row(fts, CORPUS, "verbatim")
    out["verbatim_like"] = _recall_row(like, CORPUS, "verbatim")
    out["fts"] = _recall_row(fts, CORPUS, "fts")
    para = [i for i in CORPUS if i["paraphrase"]]
    out["paraphrase_fts"] = _recall_row(fts, para, "paraphrase")

    # Unique rows: importance / mood / current-truth.
    truth_imp = {i["slug"] for i in CORPUS if i["importance"] >= 9}
    got_imp = {next(s for s, mid in ids.items() if mid == r["id"])
               for r in mem.recall_by_importance(min_importance=9, limit=50)}
    out["importance_recall"] = {"expected": sorted(truth_imp),
                                "returned": sorted(got_imp),
                                "exact": truth_imp == got_imp}
    truth_mood = {i["slug"] for i in CORPUS
                  if abs(i["valence"] - 0.8) <= 0.3}
    got_mood = {next(s for s, mid in ids.items() if mid == r["id"])
                for r in mem.recall_by_mood(target_valence=0.8,
                                            tolerance=0.3, limit=50)}
    out["mood_recall"] = {"expected": sorted(truth_mood),
                          "returned": sorted(got_mood),
                          "exact": truth_mood == got_mood}

    old_id = mem.add_memory(TRUTH_OLD, category="knowledge", importance=6)
    new_id = mem.supersede(old_id, TRUTH_NEW)
    current = [r["content"] for r in
               mem.recall_current(limit=50, min_importance=1)]
    raw = [r["content"] for r in mem.fts_search("memories", "frost",
                                                limit=10)]
    out["current_truth"] = {
        "method": "add_memory + supersede + recall_current",
        "new_id": new_id,
        "recall_current_has_new": TRUTH_NEW in current,
        "recall_current_has_old": TRUTH_OLD in current,
        "raw_fts_still_has_old": TRUTH_OLD in raw,
    }
    mem.close()
    out["final_bytes"] = _store_bytes(db_path)
    out["rss_peak_kib"] = _rss_kib()
    return out


def run_brunnr(workdir: Path) -> dict:
    sys.path.insert(0, str(REPO / "src"))
    from ember.schemas.chunks import Chunk, Document
    from ember.schemas.config import BrunnrConfig, SqliteVecConfig
    from ember.schemas.episode import Episode
    from ember.well.brunnr.sqlite_vec import open as sv_open

    out: dict = {"system": "brunnr"}
    cfg = BrunnrConfig(embedding_dim=384,
                       sqlite_vec=SqliteVecConfig(
                           path=workdir / "store.db"))
    store = workdir / "store.db"
    handle = sv_open(cfg)
    assert hasattr(handle, "add_chunks")
    out["rss_after_open_kib"] = _rss_kib()
    handle.close()
    out["empty_bytes"] = _store_bytes(store)
    handle = sv_open(cfg)  # reopened for the run
    assert hasattr(handle, "add_chunks")

    # The shared embedder (see module docstring): mempalace's own
    # ONNX MiniLM, held constant across the semantic systems.
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    ef = DefaultEmbeddingFunction()

    def embed(texts: list[str]) -> list[tuple[float, ...]]:
        return [tuple(float(x) for x in vec) for vec in ef(texts)]

    out["rss_after_embedder_kib"] = _rss_kib()

    doc_id = handle.add_document(Document(
        source="e078-corpus", title="E-078 corpus",
        content_type="text", hash="e078-corpus-v1"))
    texts = [i["text"] for i in CORPUS] + [TRUTH_OLD, TRUTH_NEW]
    vectors = embed(texts)
    chunks = [Chunk(document_id=doc_id, chunk_index=n, text=t,
                    embedding=v)
              for n, (t, v) in enumerate(zip(texts, vectors))]
    start = time.perf_counter()
    handle.add_chunks(chunks)
    out["add"] = {"queries": len(chunks),
                  "median_ms": round((time.perf_counter() - start)
                                     * 1000.0 / len(chunks), 3),
                  "p95_ms": None, "max_ms": None,
                  "note": "one add_chunks call for the corpus; "
                          "per-chunk mean"}

    def texts_of(hits) -> list[str]:
        return [h.text for h in hits]

    def text_search(q: str) -> list[str]:
        return texts_of(handle.text_search(q, k=K))

    def vector_search(q: str) -> list[str]:
        return texts_of(handle.vector_search(embed([q])[0], k=K))

    def hybrid_search(q: str) -> list[str]:
        return texts_of(handle.hybrid_search(embed([q])[0], q, k=K))

    out["verbatim_text"] = _recall_row(text_search, CORPUS, "verbatim")
    out["verbatim_vector"] = _recall_row(vector_search, CORPUS, "verbatim")
    out["fts_text"] = _recall_row(text_search, CORPUS, "fts")
    out["fts_hybrid"] = _recall_row(hybrid_search, CORPUS, "fts")
    para = [i for i in CORPUS if i["paraphrase"]]
    out["paraphrase_vector"] = _recall_row(vector_search, para, "paraphrase")
    out["paraphrase_hybrid"] = _recall_row(hybrid_search, para, "paraphrase")

    hits = hybrid_search(TRUTH_QUERY)
    out["current_truth"] = {
        "method": "both versions stored as ordinary chunks; "
                  "hybrid_search judged",
        "top_hit_is_new": bool(hits) and hits[0] == TRUTH_NEW,
        "old_in_topk": TRUTH_OLD in hits,
        "new_in_topk": TRUTH_NEW in hits,
    }

    for op, reply in EPISODES:
        handle.add_episode(Episode(operator_input=op, ember_reply=reply))
    recent = handle.recent_episodes(5)
    out["episode_recall"] = {
        "stored": len(EPISODES), "asked": 5,
        "returned": len(recent),
        "newest_first_is_last_stored":
            bool(recent) and recent[0].operator_input == EPISODES[-1][0],
        "all_returned_are_the_last_five":
            {e.operator_input for e in recent}
            == {op for op, _ in EPISODES[-5:]},
    }
    handle.close()
    out["final_bytes"] = _store_bytes(store)
    out["rss_peak_kib"] = _rss_kib()
    return out


def run_mempalace(workdir: Path) -> dict:
    sys.path.insert(0, str(REPO / "mempalace"))
    # HOME stays the real one: the ONNX embedding model's cache
    # lives there and is read, never written, by this harness.
    # The palace itself is addressed by explicit path throughout.
    from mempalace.palace import get_collection
    from mempalace.searcher import search_memories

    palace = workdir / "palace"
    palace.mkdir(parents=True, exist_ok=True)
    out: dict = {"system": "mempalace"}
    col = get_collection(str(palace))
    out["rss_after_open_kib"] = _rss_kib()
    out["empty_bytes"] = _dir_bytes(palace)

    ids = [f"drawer_e078_{i['slug']}" for i in CORPUS]
    docs = [i["text"] for i in CORPUS] + [TRUTH_OLD, TRUTH_NEW]
    all_ids = ids + ["drawer_e078_truth_old", "drawer_e078_truth_new"]
    metas = [dict(wing="e078", room=i["category"],
                  source_file=f"{i['slug']}.txt", chunk_index=0,
                  added_by="e078-harness",
                  filed_at="2026-11-01T00:00:00") for i in CORPUS]
    metas += [dict(wing="e078", room="knowledge",
                   source_file="truth_old.txt", chunk_index=0,
                   added_by="e078-harness",
                   filed_at="2026-11-01T00:00:00"),
              dict(wing="e078", room="knowledge",
                   source_file="truth_new.txt", chunk_index=0,
                   added_by="e078-harness",
                   filed_at="2026-11-01T00:00:00")]
    start = time.perf_counter()
    col.add(ids=all_ids, documents=docs, metadatas=metas)
    elapsed = (time.perf_counter() - start) * 1000.0
    out["add"] = {"queries": len(docs),
                  "median_ms": round(elapsed / len(docs), 3),
                  "p95_ms": None, "max_ms": None,
                  "note": "one collection.add for the corpus; "
                          "per-drawer mean (embedding included)"}

    def search(q: str) -> list[str]:
        result = search_memories(q, str(palace), n_results=K)
        return [r["text"] for r in result.get("results", [])]

    out["verbatim_search"] = _recall_row(search, CORPUS, "verbatim")
    out["fts_search"] = _recall_row(search, CORPUS, "fts")
    para = [i for i in CORPUS if i["paraphrase"]]
    out["paraphrase_search"] = _recall_row(search, para, "paraphrase")

    hits = search(TRUTH_QUERY)
    out["current_truth"] = {
        "method": "both versions filed as ordinary drawers; "
                  "search_memories judged (no supersession at "
                  "the drawer layer)",
        "top_hit_is_new": bool(hits) and hits[0] == TRUTH_NEW,
        "old_in_topk": TRUTH_OLD in hits,
        "new_in_topk": TRUTH_NEW in hits,
    }
    out["final_bytes"] = _dir_bytes(palace)
    out["rss_peak_kib"] = _rss_kib()
    return out


CHILDREN = {"mimir-well": run_mimir, "brunnr": run_brunnr,
            "mempalace": run_mempalace}


# --------------------------------------------------------------------- #
# Parent                                                                #
# --------------------------------------------------------------------- #

def _tracked_bytes(rel: str) -> int:
    out = subprocess.run(["git", "ls-files", rel], cwd=REPO,
                         capture_output=True, text=True,
                         check=True).stdout.splitlines()
    return sum((REPO / name).stat().st_size for name in out)


def _budget_fits(fragments: list[dict]) -> dict:
    sys.path.insert(0, str(REPO / "src"))
    from ember.budgets import all_budgets

    code_bytes = {"mempalace": _tracked_bytes("mempalace"),
                  "mimir-well": _tracked_bytes("mimir-well"),
                  "brunnr": _tracked_bytes("src/ember")}
    fits: dict[str, dict] = {}
    items = len(CORPUS) + 2
    for frag in fragments:
        name = frag["system"]
        growth_per_item = (frag["final_bytes"] - frag["empty_bytes"]) / items
        month = growth_per_item * 600  # E-041 reference month of items
        # RAM basis, per system, honestly: mimir-well and
        # mempalace are judged on their own process peak (their
        # retrieval machinery is in-process). Brunnr is judged
        # on its store-open RSS — in production its embedder is
        # an external service whose RAM is the model's house,
        # never Ember's (E-041 §3); the harness embedder's peak
        # is reported beside it, not charged to Brunnr.
        if name == "brunnr":
            ram_kib, ram_basis = frag["rss_after_open_kib"], \
                "store-open RSS (embedder external in production)"
        else:
            ram_kib, ram_basis = frag["rss_peak_kib"], \
                "own process peak RSS"
        per_profile = {}
        for budget in all_budgets():
            per_profile[budget.profile.value] = {
                "install_fits": code_bytes[name]
                <= budget.install_mib * 1024 * 1024,
                "turn_ram_fits": ram_kib / 1024.0
                <= budget.turn_ram_mib,
                "month_growth_fits": month
                <= budget.storage_growth_mib_per_month * 1024 * 1024,
            }
        fits[name] = {"code_bytes": code_bytes[name],
                      "ram_basis": ram_basis,
                      "ram_mib_judged": round(ram_kib / 1024.0, 1),
                      "growth_bytes_per_item": round(growth_per_item, 1),
                      "projected_month_bytes_at_600_items":
                      round(month),
                      "profiles": per_profile}
    return fits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", choices=sorted(CHILDREN))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.system:
        workdir = args.workdir / args.system
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            frag = CHILDREN[args.system](workdir)
            frag["ok"] = True
        except Exception as exc:  # a failed system is a result too
            frag = {"system": args.system, "ok": False,
                    "error": f"{type(exc).__name__}: {exc}"}
        target = args.workdir / f"{args.system}.json"
        target.write_text(json.dumps(frag, indent=2), encoding="utf-8")
        print(json.dumps(frag, indent=2))
        return 0 if frag["ok"] else 1

    if not args.all:
        parser.error("pass --system NAME or --all")

    args.workdir.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items()
           if k.lower() not in ("http_proxy", "https_proxy",
                                "all_proxy", "no_proxy")}
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO / "src"), str(REPO / "mempalace"),
         str(REPO / "mimir-well" / "src")]
        + ([os.environ["PYTHONPATH"]]
           if os.environ.get("PYTHONPATH") else []))
    env["TMPDIR"] = str(args.workdir)
    fragments = []
    for name in ("mimir-well", "brunnr", "mempalace"):
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()),
             "--system", name, "--workdir", str(args.workdir)],
            capture_output=True, text=True, env=env)
        frag_file = args.workdir / f"{name}.json"
        if frag_file.exists():
            fragments.append(json.loads(frag_file.read_text()))
        else:
            fragments.append({"system": name, "ok": False,
                              "error": "child produced no fragment",
                              "stderr_tail": proc.stderr[-2000:]})
    report = {"corpus_items": len(CORPUS),
              "paraphrase_items": sum(1 for i in CORPUS
                                      if i["paraphrase"]),
              "k": K, "repeats": REPEATS,
              "systems": fragments}
    if all(f.get("ok") for f in fragments):
        report["budget_fits"] = _budget_fits(fragments)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2),
                            encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all(f.get("ok") for f in fragments) else 1


if __name__ == "__main__":
    raise SystemExit(main())
