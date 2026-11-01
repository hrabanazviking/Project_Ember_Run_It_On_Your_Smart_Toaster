"""The one memory face for the companion (E-080).

E-079's verdict was **bound**: one memory contract over two
bounded house engines — Brunnr keeps documents, chunks, and
conversation turns; mimir-well keeps living facts (importance,
mood, validity, supersession, lifecycle, guard, audit). This
module is that contract. From here on, companion code speaks
to memory through :class:`MemoryFace` and never has to know
there are two stores behind it.

Binding conditions from the verdict, and where each lands:

1. **One canonical mimir-well path (docket 51 settled for
   the companion).** The face's one default is the mimir-well
   library's own default, ``~/.mimir_well/mimir_well.db``
   (:data:`CANONICAL_MIMIR_DB_PATH`). Any other path arrives
   only as explicit configuration to this face. The face
   does **not** re-point anyone else: bifrost's two raw-SQL
   consumers, the Eye, and Verdandi's check keep their own
   stated paths (docket 109's reckoning, §3 of the E-080
   doc; Part VIII owns bifrost's side) — but the companion
   itself now has exactly one default, named here.
2. **Stores are not merged.** Facts live in mimir-well's
   store, documents/episodes in Brunnr's. Nothing in this
   module copies a store into the other shape.
3. **Persona separation is a face property (docket 110).**
   Brunnr's adapters do not persist persona tags, so the
   face tags *above* the adapter: facts are written under
   the persona's own mimir-well ``user_id`` namespace (the
   member's own isolation), and episode tags are kept in
   the face's tag sidecar (§ below). An untagged episode
   belongs to the default persona only — every other
   persona is refused it, fail-closed. E-083 enforces this
   layer's fixtures in full; the guarantee is built here.
4. **Budgets bind the face.** Meaning search over living
   facts is *index, don't merge* (§ below) and it is priced:
   one indexed fact costs one embedded Brunnr chunk
   (72,239 B measured growth per embedded chunk, E-078).
   On the toaster profile that price breaks the storage
   story, so the toaster ships word search over living
   facts and this face *says so* — indexing defaults off
   there and a meaning query is answered by word search
   with its mode stated, never silently upgraded.
5. mimir-well's flask hygiene (docket 108) is owed at or
   before the E-092 gate, not here.

Index, don't merge — how meaning search over facts works:
when a fact is remembered and indexing is on for the
profile, the face adds the fact's text to Brunnr as one
chunk of a single synthetic index document (source
:data:`FACT_INDEX_SOURCE`), with an embedder the caller
supplies (the core grows no embedder of its own here; no
embedder, no index, stated in the result). The chunk is an
*index entry, not a copy of record*: the face's sidecar
maps chunk → fact id, and every meaning hit is resolved
back through mimir-well — the fact is served only if it
still exists, belongs to the asking persona, and is
current (``is_current`` and its validity window). A
superseded fact's chunk may still sit in the index; it is
never served as current, because resolution — not the
index — decides truth. That is the E-079 charge, proven by
the E-080 tests.

The tag/index sidecar is one small JSON file (stdlib only,
atomic replace) kept beside the mimir store by default:
episode persona tags + the fact-index map. It is face
bookkeeping, not a third store: every fact and turn it
points at lives in its bounded engine.

Lifecycle (E-082): growth, decay, and pruning live on the
face as :meth:`MemoryFace.lifecycle_report`,
:meth:`MemoryFace.run_decay` (mimir-well's own Ebbinghaus
decay, delegated), :meth:`MemoryFace.prune_stale_index`
(sidecar pointers for facts no longer current are dropped;
physical Brunnr reclamation is docket 112 — the handle has
no delete), and :meth:`MemoryFace.run_lifecycle` composing
them under Part III's storage budget (E-050 consumed:
a reference month is 0.39 MiB, inside every ceiling).

Loading mimir-well: the core does not import member code at
module scope anywhere (the E-067 discipline). The face
loads ``mimir_well`` lazily, only when a face is opened
without an injected handle: an already-importable
``mimir_well`` wins, then the in-tree member's ``src``
(found relative to this file, or named explicitly). The
face talks to mimir-well **only through RunaMemory** —
never raw SQL against its tables (docket 109: the face is
the companion's one sanctioned library-path consumer).

Graceful offline, as everywhere in this core: opening a
face whose Brunnr is :class:`Disconnected` or whose
mimir-well cannot load does not raise; the affected half
reports its state and its operations return typed
unavailable results instead of pretending.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from ember.budgets import budget_for
from ember.schemas.chunks import Chunk, Document, RetrievalHit
from ember.schemas.config import ConversationProfile
from ember.schemas.episode import Episode
from ember.schemas.persona import DEFAULT_PERSONA_ID
from ember.well.brunnr.handle import BrunnrHandle

#: The face's one canonical mimir-well store (docket 51):
#: the mimir-well library's own default, named here so the
#: companion has exactly one default and it is this one.
CANONICAL_MIMIR_DB_PATH = Path.home() / ".mimir_well" / "mimir_well.db"

#: Source marker of the face's single synthetic Brunnr
#: document whose chunks index living facts (index, don't
#: merge). Chunks under it are index entries, never records.
FACT_INDEX_SOURCE = "ember-memory-face/fact-index"

#: Title of the fact-index document.
FACT_INDEX_TITLE = "Ember memory face — living-fact index"

#: Measured price of one indexed fact: E-078's embedded-
#: chunk growth (72,239 B per embedded chunk in Brunnr's
#: sqlite_vec store). Priced per profile in the E-080 doc.
INDEX_BYTES_PER_FACT = 72_239

#: Measured price of one living fact in mimir-well's store:
#: 745 B per item, E-078's comparison harness.
FACT_BYTES_PER_FACT = 745

#: Measured price of one conversation turn in Brunnr:
#: 585 B per episode (E-050's steady-state marginal
#: 585.4 B/episode; E-078 measured 585 B/episode).
EPISODE_BYTES_PER_TURN = 585

#: Profiles whose storage story pays the index price by
#: default. The toaster is absent on purpose (verdict
#: §5.4): it ships word search over living facts.
INDEX_DEFAULT_PROFILES = frozenset({
    ConversationProfile.PHONE,
    ConversationProfile.PI,
    ConversationProfile.LAPTOP,
})

Embedder = Callable[[str], Sequence[float]]


@dataclass(frozen=True, slots=True)
class FactResult:
    """The outcome of remembering one living fact."""

    fact_id: Optional[int]
    indexed: bool
    note: str


@dataclass(frozen=True, slots=True)
class LifecycleReport:
    """One lifecycle accounting (E-082), all figures priced
    from measured anchors, never invented."""

    profile: str
    ceiling_bytes_per_month: int
    facts_stored: int  # mimir-well memories rows (all personae)
    facts_bytes: int  # facts_stored x FACT_BYTES_PER_FACT
    indexed_facts: int
    index_bytes: int  # indexed_facts x INDEX_BYTES_PER_FACT
    brunnr_size_bytes: int  # the store's own on-disk size
    index_fits_ceiling: bool
    index_months_of_headroom: float  # ceiling / index price per fact, in facts
    note: str = ""


@dataclass(frozen=True, slots=True)
class MeaningHits:
    """A meaning search's answer, with its mode stated."""

    mode: str  # "meaning" (index-resolved) or "word" (fallback)
    facts: tuple[dict, ...] = ()
    note: str = ""


def index_default_for(profile: ConversationProfile) -> bool:
    """Whether the fact index is on by default on a profile."""
    return profile in INDEX_DEFAULT_PROFILES


def _load_runa_memory_class(explicit_src: Optional[Path] = None):
    """Lazily load mimir-well's RunaMemory (never at import).

    Loaded dynamically (``importlib``), never by a static
    import: mimir-well is an in-tree member, not one of the
    core's declared PyPI extras (E-044's diet), and the core
    imports no member statically anywhere (E-067's rule).

    Resolution: an importable ``mimir_well`` first, then the
    in-tree member's ``src`` relative to this file, then an
    explicitly named member src. Raises ImportError with the
    places tried when none works — the caller turns that
    into the face's honest unavailable state.
    """
    import importlib

    try:
        return importlib.import_module("mimir_well.core").RunaMemory
    except ImportError:
        pass
    candidates: list[Path] = []
    if explicit_src is not None:
        candidates.append(Path(explicit_src))
    # src/ember/well/memory_face.py -> repo root is parents[3].
    candidates.append(
        Path(__file__).resolve().parents[3] / "mimir-well" / "src"
    )
    for cand in candidates:
        if (cand / "mimir_well" / "core.py").exists():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return importlib.import_module("mimir_well.core").RunaMemory
    raise ImportError(
        "mimir_well not importable and no member src found "
        f"(tried: {[str(c) for c in candidates]})"
    )


class _Sidecar:
    """The face's bookkeeping: episode tags + fact-index map.

    One JSON file, replaced atomically on every change. Not
    a store: it holds only tags and pointers into the two
    bounded engines.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.episode_persona: dict[str, str] = {}
        self.fact_chunk: dict[str, int] = {}
        self.fact_persona: dict[str, str] = {}
        self.index_document_id: Optional[int] = None
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.episode_persona = dict(data.get("episode_persona", {}))
                self.fact_chunk = {
                    str(k): int(v) for k, v in data.get("fact_chunk", {}).items()
                }
                self.fact_persona = dict(data.get("fact_persona", {}))
                doc_id = data.get("index_document_id")
                self.index_document_id = int(doc_id) if doc_id is not None else None
            except (OSError, ValueError, TypeError):
                # A corrupt sidecar degrades to empty tags:
                # episodes fall back to default-persona-only
                # and facts to unindexed — fail-closed both.
                pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "episode_persona": self.episode_persona,
            "fact_chunk": self.fact_chunk,
            "fact_persona": self.fact_persona,
            "index_document_id": self.index_document_id,
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=1, sort_keys=True),
                       encoding="utf-8")
        os.replace(tmp, self.path)


class MemoryFace:
    """The companion's one memory contract (E-080).

    Construct with live handles (tests, embedders of the
    face in larger wiring) or via :meth:`open`. Every
    operation names the bounded engine that serves it;
    no operation merges the stores.
    """

    def __init__(
        self,
        *,
        brunnr: Optional[BrunnrHandle] = None,
        mimir: Any = None,
        mimir_state: str = "not-configured",
        profile: ConversationProfile = ConversationProfile.TOASTER,
        embedder: Optional[Embedder] = None,
        index_facts: Optional[bool] = None,
        sidecar_path: Optional[Path] = None,
        default_persona_id: str = DEFAULT_PERSONA_ID,
    ):
        self._brunnr = brunnr
        self._mimir = mimir
        #: "live", or why the living-facts half is unavailable.
        self.mimir_state = mimir_state if mimir is not None else mimir_state
        self.profile = profile
        self._embedder = embedder
        self.index_facts = (
            index_default_for(profile) if index_facts is None else index_facts
        )
        self.default_persona_id = default_persona_id
        if sidecar_path is None:
            base = (
                Path(mimir.db_path).parent
                if mimir is not None and getattr(mimir, "db_path", None)
                else Path.home() / ".ember"
            )
            sidecar_path = base / "memory_face_sidecar.json"
        self._sidecar = _Sidecar(Path(sidecar_path))

    # ------------------------------------------------------------------ #
    # Opening                                                             #
    # ------------------------------------------------------------------ #

    @classmethod
    def open(
        cls,
        *,
        brunnr_config: Any = None,
        brunnr: Optional[BrunnrHandle] = None,
        mimir_db_path: Optional[Path] = None,
        mimir_src: Optional[Path] = None,
        profile: ConversationProfile = ConversationProfile.TOASTER,
        embedder: Optional[Embedder] = None,
        index_facts: Optional[bool] = None,
        sidecar_path: Optional[Path] = None,
        default_persona_id: str = DEFAULT_PERSONA_ID,
    ) -> "MemoryFace":
        """Open the face over the bounded engines.

        The mimir-well path defaults to the one canonical
        path (docket 51); Brunnr opens through its own
        registry when a config is given. Either half may
        come up unavailable — the face reports it, never
        raises for an offline engine.
        """
        if brunnr is None and brunnr_config is not None:
            from ember.schemas.errors import Disconnected
            from ember.well.brunnr.handle import open as brunnr_open

            opened = brunnr_open(brunnr_config)
            brunnr = None if isinstance(opened, Disconnected) else opened
        mimir = None
        mimir_state = "live"
        try:
            runa = _load_runa_memory_class(mimir_src)
            mimir = runa(db_path=str(mimir_db_path or CANONICAL_MIMIR_DB_PATH))
        except Exception as exc:  # noqa: BLE001 — reported, not raised
            mimir_state = f"unavailable: {type(exc).__name__}: {exc}"
        return cls(
            brunnr=brunnr,
            mimir=mimir,
            mimir_state=mimir_state,
            profile=profile,
            embedder=embedder,
            index_facts=index_facts,
            sidecar_path=sidecar_path,
            default_persona_id=default_persona_id,
        )

    # ------------------------------------------------------------------ #
    # State                                                               #
    # ------------------------------------------------------------------ #

    def state(self) -> dict:
        """Both halves' state, the profile, and the index mode."""
        budget = budget_for(self.profile)
        return {
            "brunnr": "live" if self._brunnr is not None else "unavailable",
            "mimir_well": self.mimir_state,
            "canonical_mimir_db_path": str(CANONICAL_MIMIR_DB_PATH),
            "profile": self.profile.value,
            "index_facts": self.index_facts,
            "index_default_for_profile": index_default_for(self.profile),
            "index_bytes_per_fact": INDEX_BYTES_PER_FACT,
            "indexed_facts": len(self._sidecar.fact_chunk),
            "storage_growth_mib_per_month": (
                budget.storage_growth_mib_per_month
            ),
        }

    def close(self) -> None:
        if self._brunnr is not None:
            self._brunnr.close()
        if self._mimir is not None:
            self._mimir.close()

    # ------------------------------------------------------------------ #
    # Living facts — mimir-well's territory                               #
    # ------------------------------------------------------------------ #

    def _persona(self, persona_id: Optional[str]) -> str:
        return persona_id or self.default_persona_id

    def remember_fact(
        self,
        content: str,
        *,
        category: str = "general",
        importance: int = 5,
        emotional_valence: float = 0.0,
        persona_id: Optional[str] = None,
    ) -> FactResult:
        """Remember one living fact (mimir-well, guarded).

        Returns the fact's id, whether it was indexed for
        meaning search, and a plain note saying why not when
        it was not. A guard-blocked write is reported as
        blocked (``fact_id`` None), never hidden.
        """
        if self._mimir is None:
            return FactResult(None, False, f"mimir-well {self.mimir_state}")
        persona = self._persona(persona_id)
        fact_id = self._mimir.add_memory(
            content,
            category=category,
            importance=importance,
            emotional_valence=emotional_valence,
            user_id=persona,
        )
        if not fact_id or fact_id < 0:
            return FactResult(None, False, "blocked by mimir-well's guard")
        indexed, note = self._maybe_index(fact_id, content, persona)
        return FactResult(int(fact_id), indexed, note)

    def _maybe_index(self, fact_id: int, content: str, persona: str):
        if not self.index_facts:
            return False, (
                f"not indexed: the fact index is off on the "
                f"{self.profile.value} profile (word search only, "
                f"E-079 §5.4)"
            )
        if self._embedder is None:
            return False, "not indexed: no embedder supplied to the face"
        if self._brunnr is None:
            return False, "not indexed: Brunnr unavailable"
        doc_id = self._sidecar.index_document_id
        if doc_id is None:
            digest = hashlib.sha256(FACT_INDEX_SOURCE.encode()).hexdigest()
            doc_id = self._brunnr.add_document(
                Document(
                    source=FACT_INDEX_SOURCE,
                    title=FACT_INDEX_TITLE,
                    content_type="memory-fact-index",
                    hash=digest,
                )
            )
            self._sidecar.index_document_id = int(doc_id)
        chunk_ids = self._brunnr.add_chunks(
            [
                Chunk(
                    document_id=int(doc_id),
                    chunk_index=int(fact_id),
                    text=content,
                    embedding=tuple(float(x) for x in self._embedder(content)),
                )
            ]
        )
        if chunk_ids:
            self._sidecar.fact_chunk[str(fact_id)] = int(chunk_ids[0])
            self._sidecar.fact_persona[str(fact_id)] = persona
            self._sidecar.save()
            return True, "indexed for meaning search (index, don't merge)"
        return False, "not indexed: Brunnr accepted no chunk"

    def recall_facts_word(
        self, query: str, *, limit: int = 20, persona_id: Optional[str] = None
    ) -> list[dict]:
        """Word search over living facts (mimir-well FTS5).

        Only the asking persona's facts, current ones only —
        a superseded fact is never served as current.
        """
        if self._mimir is None:
            return []
        persona = self._persona(persona_id)
        rows = self._mimir.fts_search("memories", query, limit=limit,
                                      user_id=persona)
        return [r for r in rows if r.get("is_current", 1)]

    def recall_current(
        self, *, limit: int = 10, min_importance: int = 1,
        persona_id: Optional[str] = None,
    ) -> list[dict]:
        """The current-truth view of living facts."""
        if self._mimir is None:
            return []
        return self._mimir.recall_current(
            limit=limit, min_importance=min_importance,
            user_id=self._persona(persona_id),
        )

    def recall_by_importance(
        self, *, min_importance: int = 7, limit: int = 20,
        persona_id: Optional[str] = None,
    ) -> list[dict]:
        if self._mimir is None:
            return []
        persona = self._persona(persona_id)
        rows = self._mimir.recall_by_importance(
            min_importance=min_importance, limit=limit, user_id=persona)
        return [r for r in rows if r.get("is_current", 1)]

    def recall_by_mood(
        self, target_valence: float, *, tolerance: float = 0.3,
        limit: int = 20, persona_id: Optional[str] = None,
    ) -> list[dict]:
        if self._mimir is None:
            return []
        persona = self._persona(persona_id)
        rows = self._mimir.recall_by_mood(
            target_valence=target_valence, tolerance=tolerance,
            limit=limit, user_id=persona)
        return [r for r in rows if r.get("is_current", 1)]

    def supersede_fact(
        self, old_fact_id: int, new_content: str, *,
        persona_id: Optional[str] = None,
    ) -> FactResult:
        """Replace a fact; the old one stops being current.

        The new fact is indexed under the same rule as any
        remembered fact. The old fact's index chunk is left
        in Brunnr — resolution at search time, not the
        index, decides what is current (§ module docstring).
        """
        if self._mimir is None:
            return FactResult(None, False, f"mimir-well {self.mimir_state}")
        persona = self._persona(persona_id)
        new_id = self._mimir.supersede(
            old_fact_id, new_content, user_id=persona)
        if not new_id or new_id < 0:
            return FactResult(None, False,
                              "supersede refused by mimir-well")
        indexed, note = self._maybe_index(int(new_id), new_content, persona)
        return FactResult(int(new_id), indexed, note)

    def search_facts_meaning(
        self, query: str, *, k: int = 5, persona_id: Optional[str] = None
    ) -> MeaningHits:
        """Meaning search over living facts, index-resolved.

        On profiles where the index is off (the toaster),
        or with no embedder, this answers by word search
        and *says so* in ``mode`` — the verdict's stated
        fallback, never a silent downgrade. Meaning hits
        are resolved through mimir-well: superseded,
        other-persona, and vanished facts are dropped.
        """
        persona = self._persona(persona_id)
        if not self.index_facts or self._embedder is None or self._brunnr is None:
            note = (
                "word search: the fact index is off on this profile"
                if not self.index_facts
                else "word search: no embedder or no Brunnr for the index"
            )
            rows = self.recall_facts_word(query, limit=k, persona_id=persona)
            return MeaningHits(mode="word", facts=tuple(rows), note=note)
        qvec = tuple(float(x) for x in self._embedder(query))
        hits = self._brunnr.vector_search(qvec, k=max(k * 4, k))
        facts: list[dict] = []
        seen: set[int] = set()
        for hit in hits:
            fact_id = self._fact_for_chunk(hit.chunk_id)
            if fact_id is None or fact_id in seen:
                continue
            seen.add(fact_id)
            if self._sidecar.fact_persona.get(str(fact_id)) != persona:
                continue
            resolved = self._resolve_current_fact(fact_id, persona)
            if resolved is not None:
                facts.append(resolved)
            if len(facts) >= k:
                break
        return MeaningHits(
            mode="meaning",
            facts=tuple(facts),
            note="index hits resolved through mimir-well's current truth",
        )

    def _fact_for_chunk(self, chunk_id: int) -> Optional[int]:
        for fact_id, cid in self._sidecar.fact_chunk.items():
            if cid == chunk_id:
                return int(fact_id)
        return None

    def _resolve_current_fact(self, fact_id: int, persona: str) -> Optional[dict]:
        if self._mimir is None:
            return None
        row = self._mimir.get_memory(fact_id, user_id=persona)
        if row is None or not row.get("is_current", 1):
            return None
        return row

    # ------------------------------------------------------------------ #
    # Lifecycle — growth, decay, pruning (E-082)                          #
    # ------------------------------------------------------------------ #

    def lifecycle_report(self) -> LifecycleReport:
        """Growth accounting against this profile's budget.

        E-050 proved a reference month of companionship
        costs 0.39 MiB — inside every profile's ceiling
        with years of headroom — so lifecycle here is
        accounting and hygiene, not emergency pruning.
        The one growth that can break a small profile is
        the fact index (72,239 B per indexed fact,
        E-078/E-080): this report prices the index held
        today against the profile's monthly ceiling and
        says plainly whether it fits.
        """
        budget = budget_for(self.profile)
        ceiling = int(budget.storage_growth_mib_per_month * 1024 * 1024)
        facts_stored = 0
        if self._mimir is not None:
            try:
                facts_stored = int(
                    self._mimir.get_stats().get("memories", 0))
            except Exception:  # noqa: BLE001 — accounting degrades to 0
                facts_stored = 0
        indexed = len(self._sidecar.fact_chunk)
        index_bytes = indexed * INDEX_BYTES_PER_FACT
        brunnr_bytes = 0
        if self._brunnr is not None:
            try:
                brunnr_bytes = int(self._brunnr.count().size_bytes)
            except Exception:  # noqa: BLE001
                brunnr_bytes = 0
        return LifecycleReport(
            profile=self.profile.value,
            ceiling_bytes_per_month=ceiling,
            facts_stored=facts_stored,
            facts_bytes=facts_stored * FACT_BYTES_PER_FACT,
            indexed_facts=indexed,
            index_bytes=index_bytes,
            brunnr_size_bytes=brunnr_bytes,
            index_fits_ceiling=index_bytes <= ceiling,
            index_months_of_headroom=(
                ceiling / INDEX_BYTES_PER_FACT if INDEX_BYTES_PER_FACT
                else 0.0),
            note=(
                "index priced at the measured 72,239 B/fact; "
                "facts at 745 B/item (E-078); reference-month "
                "growth 0.39 MiB fits every ceiling (E-050)"),
        )

    def prune_stale_index(self) -> dict:
        """Drop index pointers for facts no longer current.

        A superseded or deleted fact's chunk stays in
        Brunnr (the handle offers no chunk delete — docket
        112), but its sidecar pointer is the face's own
        bookkeeping: dropping it means the stale chunk can
        never be resolved or counted again, and the index
        accounting shrinks by the measured price per entry.
        Physical Brunnr bytes are NOT reclaimed by this —
        the report says so; reclamation needs a handle
        delete the core does not have yet.
        """
        pruned = 0
        kept: dict[str, int] = {}
        kept_persona: dict[str, str] = {}
        for fact_id_s, chunk_id in self._sidecar.fact_chunk.items():
            persona = self._sidecar.fact_persona.get(fact_id_s, "")
            resolved = (
                self._resolve_current_fact(int(fact_id_s), persona)
                if self._mimir is not None else None)
            if resolved is None:
                pruned += 1
            else:
                kept[fact_id_s] = chunk_id
                kept_persona[fact_id_s] = persona
        if pruned:
            self._sidecar.fact_chunk = kept
            self._sidecar.fact_persona = kept_persona
            self._sidecar.save()
        return {
            "pruned_index_entries": pruned,
            "index_bytes_logically_reclaimed": pruned * INDEX_BYTES_PER_FACT,
            "physical_bytes_reclaimed": 0,
            "note": ("Brunnr's handle has no chunk delete (docket 112): "
                     "stale chunks become unreachable and uncounted, "
                     "their bytes await a handle-level delete"),
        }

    def run_decay(self, *, persona_id: Optional[str] = None,
                  half_life_days: float = 30.0) -> dict:
        """Run mimir-well's own Ebbinghaus decay for a persona.

        Delegated, never reimplemented: the member owns the
        forgetting curve. Its returned ``pruned`` count is
        the member's word for facts whose decayed importance
        fell below the floor — read its code and the count
        means importance was floored at 1, not that rows
        were deleted; the E-082 doc states this plainly so
        no report ever claims deletions that did not happen.
        """
        if self._mimir is None:
            return {"decayed": 0, "pruned": 0, "reinforced": 0,
                    "note": f"mimir-well {self.mimir_state}"}
        result = self._mimir.decay(
            half_life_days=half_life_days,
            user_id=self._persona(persona_id))
        return dict(result)

    def run_lifecycle(self, *, persona_id: Optional[str] = None,
                      half_life_days: float = 30.0) -> dict:
        """One lifecycle pass: decay, prune the index, report.

        Order matters: decay first (importance settles),
        then stale-index pruning (superseded/vanished facts
        lose their pointers), then the growth accounting —
        so the report prices the store as the pass left it.
        """
        decay = self.run_decay(persona_id=persona_id,
                               half_life_days=half_life_days)
        prune = self.prune_stale_index()
        report = self.lifecycle_report()
        return {"decay": decay, "prune": prune, "report": report}

    # ------------------------------------------------------------------ #
    # Documents & episodes — Brunnr's territory                           #
    # ------------------------------------------------------------------ #

    def add_document(self, doc: Document) -> Optional[int]:
        if self._brunnr is None:
            return None
        return self._brunnr.add_document(doc)

    def add_chunks(self, chunks: Sequence[Chunk]) -> list[int]:
        if self._brunnr is None:
            return []
        return self._brunnr.add_chunks(chunks)

    def search_documents_word(self, query: str, *, k: int = 5) -> list[RetrievalHit]:
        if self._brunnr is None:
            return []
        return self._brunnr.text_search(query, k)

    def search_documents_meaning(
        self, qvec: Sequence[float], *, k: int = 5
    ) -> list[RetrievalHit]:
        if self._brunnr is None:
            return []
        return self._brunnr.vector_search(qvec, k)

    def add_turn(self, episode: Episode) -> Optional[int]:
        """Remember one conversation turn (Brunnr episode).

        The face records the episode's persona tag in its
        sidecar, above the adapter (docket 110) — the tag
        the adapter cannot persist is the face's to keep.
        """
        if self._brunnr is None:
            return None
        episode_id = self._brunnr.add_episode(episode)
        self._sidecar.episode_persona[str(int(episode_id))] = episode.persona_id
        self._sidecar.save()
        return int(episode_id)

    def recent_turns(
        self, *, limit: int = 5, persona_id: Optional[str] = None
    ) -> list[Episode]:
        """Recent turns for one persona only, fail-closed.

        An episode is served to a persona when the face's
        tag says it is theirs; an untagged episode (written
        before the face, or outside it) belongs to the
        default persona only.
        """
        if self._brunnr is None:
            return []
        persona = self._persona(persona_id)
        window = self._brunnr.recent_episodes(max(limit * 4, limit))
        out: list[Episode] = []
        for ep in window:
            tag = self._sidecar.episode_persona.get(str(ep.id))
            owner = tag if tag is not None else DEFAULT_PERSONA_ID
            if owner == persona:
                out.append(ep)
            if len(out) >= limit:
                break
        return out


__all__ = [
    "CANONICAL_MIMIR_DB_PATH",
    "EPISODE_BYTES_PER_TURN",
    "FACT_BYTES_PER_FACT",
    "FACT_INDEX_SOURCE",
    "INDEX_BYTES_PER_FACT",
    "INDEX_DEFAULT_PROFILES",
    "FactResult",
    "LifecycleReport",
    "MeaningHits",
    "MemoryFace",
    "index_default_for",
]
