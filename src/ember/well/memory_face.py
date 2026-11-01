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
3. **Persona separation is a face property (docket 110),
   enforced in full at E-083.** Brunnr's adapters do not
   persist persona tags, so the face tags *above* the
   adapter: facts are written under the persona's own
   mimir-well ``user_id`` namespace (the member's own
   isolation), and episode tags are kept in the face's tag
   sidecar (§ below). An untagged episode belongs to the
   face's default persona only — every other persona is
   refused it, fail-closed. E-083's fixture battery (the
   E-025 fixtures at this layer) holds the face to it on
   every path, and closed four gaps the battery exposed:
   the fact-index document is never a document-search
   result (its chunks are fact text; serving them there
   bypassed persona resolution entirely — docket 114);
   persona-filtered reads scan past foreign entries
   instead of starving behind a fixed window (dockets
   115/116); an untagged episode's owner is the face's
   *configured* default persona, not a hard-coded one
   (docket 117); and a persona id is validated against
   the E-025 slug rules on every operation — an invalid
   id (including the empty string, which used to fall
   back to the default persona and read its memory)
   fails closed everywhere (docket 118). Documents added
   as documents remain shared grounding by design (the
   E-025/E-035 rule); only the fact index is persona
   territory, and it is never served as a document.
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

The user's rights (E-084): what the companion remembers
about you is yours to see and to change. The face offers
:meth:`MemoryFace.inspect_memory` and
:meth:`MemoryFace.inspect_fact` (see everything, in plain
words), :meth:`MemoryFace.correct_fact` (fix a fact that
is wrong — same fact, corrected, not a new one hiding the
old), :meth:`MemoryFace.export_memory` (take your memory
out as one plain JSON-shaped bundle, optionally written
to a file you carry), :meth:`MemoryFace.delete_fact`
(forget one thing), and
:meth:`MemoryFace.delete_all_memory` (forget *everything*
for one persona — total, and guarded by an exact
confirmation phrase so no slip or stray call can trigger
it). Honest limits, stated in every result they touch:
deleting a living fact removes its row in mimir-well for
real (the member's audit keeps only a hash of the id,
never the words); deleting a conversation turn is
*logical* — Brunnr's handle has no episode delete
(docket 119), so the turn is tombstoned in the face's
sidecar, never served, inspected, or exported again, but
its physical bytes await a handle-level delete; and
documents added as documents are shared grounding
(E-025/E-035), not one persona's memory, so they are
never part of a persona export or a persona deletion.

Lifecycle (E-082): growth, decay, and pruning live on the
face as :meth:`MemoryFace.lifecycle_report`,
:meth:`MemoryFace.run_decay` (mimir-well's own Ebbinghaus
decay, delegated), :meth:`MemoryFace.prune_stale_index`
(sidecar pointers for facts no longer current are dropped;
physical Brunnr reclamation is docket 112 — the handle has
no delete), and :meth:`MemoryFace.run_lifecycle` composing
them under Part III's storage budget (E-050 consumed:
a reference month is 0.39 MiB, inside every ceiling).

Logger reconciliation (E-085): Verdandi's conversation
logger and this face are two views, not one store. The
logger is the truth for *what was logged* in a session
(verbatim entries, its own delete right, E-063); this face
is the truth for *what the companion currently remembers*
(living facts here, conversation turns in Brunnr). Neither
copies the other wholesale. The only crossing is the
E-072 feed: candidates the logger law offers under the
user's rule arrive here through
:meth:`MemoryFace.ingest_log_candidates`, which remembers
each one as a living fact and records its provenance
(session, category, rule) in the sidecar — so any fed fact
can be traced to the session that fed it, a repeat feed is
a counted duplicate rather than a second fact, and a
logger deletion can be carried into memory:
:meth:`MemoryFace.audit_logger_reconciliation` finds fed
facts whose session is no longer in the log (it deletes
nothing), and :meth:`MemoryFace.retract_deleted_session`
forgets exactly the facts one deleted session fed
(docket 104, settled here). Propagation is *not*
automatic — the logger is a standalone member with no
hook into this core — so the caller who deletes a session
in the logger runs the retraction, or audits for orphans;
that stated boundary is the reconciliation, not a silent
gap. Facts remembered directly (never fed) carry no log
provenance and are never retracted by either operation.

WYRD-shaped export (E-086): the companion's memory is
also exportable in the shapes the constellation's
world-model work consumes, through
:meth:`MemoryFace.export_wyrd`. The boundary is
ThoughtForge TF-145's, honoured: ThoughtForge (and this
face) own cognition and memory; the WYRD Protocol owns
the world-model. So the export is *data in WYRD's own
published shapes* — its ``MemoryRecord`` envelope, its
``CanonicalFactRecord`` (store ``mimir_canonical_store``),
its ``ObservationRecord`` for turns, and the Passive
Oracle's ``FactSummary`` grouping — built from what the
face lawfully holds for one persona, and nothing else.
Ember builds no world model here, writes nothing into
WYRD, and claims no WYRD-side ingestion: shaping the
offering is Ember's side of the interface; modelling it
is WYRD's. Fields Ember does not hold are never invented:
a fact's ``fact_key`` is its mimir-well category (the
only key the member keeps), confidence is the member's
importance rescaled, and support is named only where
E-085's logger provenance actually recorded it.

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
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from ember.budgets import budget_for
from ember.schemas.chunks import Chunk, Document, RetrievalHit
from ember.schemas.config import ConversationProfile
from ember.schemas.episode import Episode
from ember.schemas.persona import DEFAULT_PERSONA_ID, is_valid_persona_id
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

#: The exact words a caller must say to delete *all* of a
#: persona's memory (E-084). Anything else — a typo, an
#: empty string, a near-miss — refuses and deletes nothing.
DELETE_ALL_CONFIRMATION = "delete everything"

#: The one lawful source of logger-fed candidates (E-072):
#: candidates claiming any other source are not logger
#: records and are refused by the E-085 ingest.
LOG_FEED_SOURCE = "conversation_logger"

#: The categories a logger candidate may become (E-072's
#: feedable vocabulary, mapped): a learned event becomes a
#: ``lesson``, a decision a ``decision``, a milestone a
#: ``milestone``, and an opted-in session summary a
#: ``session_summary``. Anything else is working state,
#: not a memory, and never crosses.
LOG_FEED_CATEGORIES = frozenset({
    "lesson", "decision", "milestone", "session_summary",
})

#: Kind marker of the WYRD-shaped export (E-086).
WYRD_EXPORT_KIND = "ember memory export (wyrd shapes)"

#: WYRD's own MemoryRecord schema version (its published
#: default in ``wyrdforge.models.memory``), stamped on
#: every record envelope the E-086 export emits.
WYRD_RECORD_SCHEMA_VERSION = "1.0.0"

#: The system id WYRD-shaped records carry: this program.
WYRD_SYSTEM_ID = "ember-agent"

#: WYRD's store names, as published in its StoreName enum:
#: canonical facts live in its Mímir store shape, observed
#: turns in its Hugin store shape.
WYRD_STORE_MIMIR = "mimir_canonical_store"
WYRD_STORE_HUGIN = "hugin_observation_store"

#: Entity id of the companion itself in a WYRD export.
WYRD_COMPANION_ENTITY_ID = "ember-companion"

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
        self.deleted_episodes: set[int] = set()
        self.log_facts: dict[str, dict] = {}
        self.index_document_id: Optional[int] = None
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.episode_persona = dict(data.get("episode_persona", {}))
                self.fact_chunk = {
                    str(k): int(v) for k, v in data.get("fact_chunk", {}).items()
                }
                self.fact_persona = dict(data.get("fact_persona", {}))
                self.deleted_episodes = {
                    int(x) for x in data.get("deleted_episodes", [])
                }
                self.log_facts = {
                    str(k): dict(v)
                    for k, v in data.get("log_facts", {}).items()
                    if isinstance(v, dict)
                }
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
            "deleted_episodes": sorted(self.deleted_episodes),
            "log_facts": self.log_facts,
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
        if not is_valid_persona_id(default_persona_id):
            raise ValueError(
                "default_persona_id must be a valid persona slug "
                f"(E-025 rules), got {default_persona_id!r}"
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

    def _persona(self, persona_id: Optional[str]) -> Optional[str]:
        """Resolve and validate a persona id (E-083).

        ``None`` means the face's own default persona. Any
        explicit id must satisfy the E-025 slug rules — the
        same rules that keep a persona id from ever being a
        path. An invalid id (the empty string included: it
        used to fall back to the default persona and so
        read and wrote *its* memory) resolves to ``None``
        here, and every operation fails closed on ``None``:
        reads return nothing, writes are refused with the
        reason stated. There is no silent substitution of
        one persona for another at this layer, ever.
        """
        pid = self.default_persona_id if persona_id is None else persona_id
        return pid if is_valid_persona_id(pid) else None

    @staticmethod
    def _invalid_persona_note(persona_id: Optional[str]) -> str:
        return (
            f"refused: invalid persona id {persona_id!r} "
            "(must be an E-025 slug; nothing was read or written)"
        )

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
        if persona is None:
            return FactResult(None, False,
                              self._invalid_persona_note(persona_id))
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
        if persona is None:
            return []
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
        persona = self._persona(persona_id)
        if persona is None:
            return []
        return self._mimir.recall_current(
            limit=limit, min_importance=min_importance,
            user_id=persona,
        )

    def recall_by_importance(
        self, *, min_importance: int = 7, limit: int = 20,
        persona_id: Optional[str] = None,
    ) -> list[dict]:
        if self._mimir is None:
            return []
        persona = self._persona(persona_id)
        if persona is None:
            return []
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
        if persona is None:
            return []
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
        if persona is None:
            return FactResult(None, False,
                              self._invalid_persona_note(persona_id))
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
        if persona is None:
            return MeaningHits(
                mode="word", facts=(),
                note=self._invalid_persona_note(persona_id))
        if not self.index_facts or self._embedder is None or self._brunnr is None:
            note = (
                "word search: the fact index is off on this profile"
                if not self.index_facts
                else "word search: no embedder or no Brunnr for the index"
            )
            rows = self.recall_facts_word(query, limit=k, persona_id=persona)
            return MeaningHits(mode="word", facts=tuple(rows), note=note)
        qvec = tuple(float(x) for x in self._embedder(query))
        # The candidate scan widens until the asking persona's
        # facts are found or the index is exhausted (docket
        # 116): a fixed window let nearer *foreign* chunks
        # starve the asker's own facts out of the results —
        # filter-then-take over the whole scan is what makes
        # this a per-persona ranking, not a global one.
        facts: list[dict] = []
        seen: set[int] = set()
        width = max(k * 4, k)
        while True:
            hits = self._brunnr.vector_search(qvec, k=width)
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
            if len(facts) >= k or len(hits) < width:
                break
            width *= 2
        return MeaningHits(
            mode="meaning",
            facts=tuple(facts[:k]),
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
    # The user's rights — inspect, correct, export, delete (E-084)        #
    # ------------------------------------------------------------------ #

    def _all_facts(self, persona: str) -> list[dict]:
        """Every living-fact row a persona owns, current and
        superseded alike, through the member's own search
        (an empty word matches every row it owns)."""
        if self._mimir is None:
            return []
        return list(self._mimir.search_memories(
            "", limit=100_000, user_id=persona))

    def _all_turns(self, persona: str) -> list[Episode]:
        """Every turn a persona owns, oldest first, with
        deleted turns (docket 119 tombstones) never served."""
        if self._brunnr is None:
            return []
        width = 16
        while True:
            window = self._brunnr.recent_episodes(width)
            if len(window) < width:
                break
            width *= 2
        return [
            ep for ep in window
            if ep.id not in self._sidecar.deleted_episodes
            and (self._sidecar.episode_persona.get(str(ep.id))
                 or self.default_persona_id) == persona
        ]

    def inspect_fact(
        self, fact_id: int, *, persona_id: Optional[str] = None
    ) -> Optional[dict]:
        """See one remembered fact, exactly as stored.

        Only its owner's persona can see it; anyone else —
        and any invalid persona id — is shown nothing.
        """
        if self._mimir is None:
            return None
        persona = self._persona(persona_id)
        if persona is None:
            return None
        return self._mimir.get_memory(int(fact_id), user_id=persona)

    def inspect_memory(
        self, *, persona_id: Optional[str] = None
    ) -> dict:
        """See everything the companion remembers for you.

        Plain words first: how many facts are still believed
        true, how many are old versions kept as history, and
        how many conversation turns are remembered — then
        the facts and turns themselves. Another persona's
        memory is never part of the answer.
        """
        persona = self._persona(persona_id)
        if persona is None:
            return {"persona": None, "facts": [], "old_facts": [],
                    "turns": [], "note": self._invalid_persona_note(persona_id)}
        if self._mimir is None:
            return {"persona": persona, "facts": [], "old_facts": [],
                    "turns": [], "note": f"mimir-well {self.mimir_state}"}
        facts = self._all_facts(persona)
        current = [f for f in facts if f.get("is_current", 1)]
        old = [f for f in facts if not f.get("is_current", 1)]
        turns = self._all_turns(persona)
        return {
            "persona": persona,
            "facts": current,
            "old_facts": old,
            "turns": turns,
            "note": (
                f"{persona} has {len(current)} fact(s) still believed "
                f"true, {len(old)} old version(s) kept as history, and "
                f"{len(turns)} remembered conversation turn(s). Old "
                "versions are shown so you can see what changed; only "
                "the facts still believed true shape what the companion "
                "says."),
        }

    def correct_fact(
        self, fact_id: int, new_content: str, *,
        persona_id: Optional[str] = None,
    ) -> FactResult:
        """Fix a fact that is wrong — in place, honestly.

        The same fact keeps its id and its history in the
        member's audit; its words are replaced with yours.
        A fact you do not own cannot be corrected from here,
        and the refusal changes nothing. If the fact was
        indexed for meaning search, its old index entry is
        dropped and the corrected words are indexed afresh
        under the profile's usual rule, so meaning search
        never serves the wrong words under a corrected fact.
        """
        if self._mimir is None:
            return FactResult(None, False, f"mimir-well {self.mimir_state}")
        persona = self._persona(persona_id)
        if persona is None:
            return FactResult(None, False,
                              self._invalid_persona_note(persona_id))
        if not new_content or not new_content.strip():
            return FactResult(None, False,
                              "refused: the corrected words are empty; "
                              "nothing was changed")
        if self._mimir.get_memory(int(fact_id), user_id=persona) is None:
            return FactResult(None, False,
                              "refused: that fact is not this persona's "
                              "to correct; nothing was changed")
        ok = self._mimir.update_memory(
            int(fact_id), content=new_content,
            source="ember-memory-face/correct", user_id=persona)
        if not ok:
            return FactResult(None, False,
                              "refused by mimir-well; nothing was changed")
        was_indexed = str(fact_id) in self._sidecar.fact_chunk
        if was_indexed:
            del self._sidecar.fact_chunk[str(fact_id)]
            self._sidecar.fact_persona.pop(str(fact_id), None)
            self._sidecar.save()
            indexed, note = self._maybe_index(int(fact_id), new_content, persona)
            return FactResult(int(fact_id), indexed,
                              "corrected; " + note)
        return FactResult(int(fact_id), False,
                          "corrected; the fact was not indexed, and "
                          "still is not")

    def export_memory(
        self, *, persona_id: Optional[str] = None,
        path: Optional[Path] = None,
    ) -> dict:
        """Take your memory out — one plain bundle, yours only.

        The bundle holds the persona's facts (still-true and
        old versions, marked which is which) and remembered
        turns, and nothing of anyone else's. With ``path``
        it is also written there as JSON, replaced
        atomically, for you to carry away. Documents added
        as documents are shared grounding, not one
        persona's memory, and are never in the bundle.
        """
        seen = self.inspect_memory(persona_id=persona_id)
        persona = seen["persona"]
        if persona is None:
            return {"kind": "ember memory export", "version": 1,
                    "persona": None, "facts": [], "old_facts": [],
                    "turns": [], "note": seen["note"]}
        turns = [{
            "id": ep.id,
            "you_said": ep.operator_input,
            "ember_replied": ep.ember_reply,
            "when": (ep.started_at.isoformat()
                     if ep.started_at is not None else None),
        } for ep in seen["turns"]]
        bundle = {
            "kind": "ember memory export",
            "version": 1,
            "persona": persona,
            "facts": seen["facts"],
            "old_facts": seen["old_facts"],
            "turns": turns,
            "counts": {
                "facts": len(seen["facts"]),
                "old_facts": len(seen["old_facts"]),
                "turns": len(turns),
            },
            "note": (
                "This is everything the companion remembers for "
                f"{persona}: the facts it still believes true, the "
                "old versions it replaced, and the conversation "
                "turns it kept. Nothing here belongs to anyone else."),
        }
        if path is not None:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + ".tmp")
            tmp.write_text(json.dumps(bundle, indent=1, sort_keys=True,
                                      default=str), encoding="utf-8")
            os.replace(tmp, target)
            bundle = {**bundle, "written_to": str(target)}
        return bundle

    # ------------------------------------------------------------------ #
    # WYRD-shaped export — memory in the world-model's shapes (E-086)    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _wyrd_tags(raw) -> list:
        """A fact's tags as a list, whatever shape the
        member stored them in (JSON text or a list)."""
        if isinstance(raw, list):
            return [str(t) for t in raw]
        if isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
            except ValueError:
                return [raw]
            if isinstance(parsed, list):
                return [str(t) for t in parsed]
            return [raw]
        return []

    def export_wyrd(
        self, *, persona_id: Optional[str] = None,
        path: Optional[Path] = None,
    ) -> dict:
        """Your memory, shaped for the world-model work.

        The same memory :meth:`export_memory` hands you in
        Ember's plain bundle, re-shaped into the record
        shapes the WYRD Protocol publishes — the shapes its
        world-model work consumes:

        * the persona and the companion as WYRD entities
          (its Passive Oracle's ``EntitySummary`` shape);
        * every fact still believed true as a canonical
          fact (its ``CanonicalFactRecord``: the
          ``MemoryRecord`` envelope over a
          ``CanonicalFactPayload``), also grouped in its
          ``FactSummary`` shape under the persona's
          subject id, as its context packets group them;
        * every old version as the same record shape,
          marked superseded, with the current fact's
          payload naming the record it supersedes;
        * every remembered turn as an observation (its
          ``ObservationRecord``, an utterance in the Hugin
          store shape).

        The boundary is ThoughtForge TF-145's, honoured:
        cognition and memory are this side's; the
        world-model is WYRD's. This export shapes an
        offering — it builds no world model, writes
        nothing into WYRD, and claims no WYRD-side
        ingestion. Nothing is invented to fill the shapes:
        a fact's key is its mimir-well category (the only
        key the member keeps), its confidence is the
        member's importance (kept 1–10) rescaled to
        WYRD's 0–1, its support names a logger session
        only where E-085's provenance recorded one, and a
        turn whose time was not recorded is stamped with
        the export time and counted under
        ``counts.turns_time_stamped_at_export``. Another
        persona's memory is never part of the export, and
        documents (shared grounding) are never in it.
        With ``path`` the bundle is also written there as
        JSON, replaced atomically, like the plain export.
        """
        seen = self.inspect_memory(persona_id=persona_id)
        persona = seen["persona"]
        if persona is None:
            return {"kind": WYRD_EXPORT_KIND, "version": 1,
                    "wyrd_schema_version": WYRD_RECORD_SCHEMA_VERSION,
                    "persona": None, "subject_id": None,
                    "entities": [], "canonical_facts": {},
                    "records": [], "counts": {},
                    "note": seen["note"]}
        subject = f"ember-persona:{persona}"
        exported_at = datetime.now(timezone.utc).isoformat()
        fed_by_fact = {row["fact_id"]: row
                       for row in self.logger_provenance(
                           persona_id=persona)}
        superseded_by = {}
        for old in seen["old_facts"]:
            if old.get("superseded_by") is not None:
                superseded_by[int(old["superseded_by"])] = int(old["id"])

        def fact_record(fact: dict, *, current: bool) -> dict:
            fid = int(fact["id"])
            content = str(fact.get("content", ""))
            category = str(fact.get("category") or "general")
            fed = fed_by_fact.get(fid)
            support = ([f"ember-log-session:{fed['session_id']}"]
                       if fed and fed.get("session_id") else [])
            return {
                "record_id": f"ember-fact:{fid}",
                "store": WYRD_STORE_MIMIR,
                "record_type": "canonical_fact",
                "schema_version": WYRD_RECORD_SCHEMA_VERSION,
                "tenant_id": persona,
                "system_id": WYRD_SYSTEM_ID,
                "entity_scope": {
                    "primary_subjects": [subject],
                    "secondary_subjects": [WYRD_COMPANION_ENTITY_ID],
                    "scene_id": None,
                    "session_id": (fed.get("session_id")
                                   if fed else None),
                    "world_id": None,
                    "project_id": None,
                },
                "content": {
                    "title": f"{category} — ember fact {fid}",
                    "summary": content,
                    "body_ref": None,
                    "structured_payload": {
                        "fact_subject_id": subject,
                        "fact_key": category,
                        "fact_value": content,
                        "value_type": "string",
                        "domain": str(fact.get("memory_type")
                                      or "general"),
                        "support_record_ids": support,
                        "supersedes_record_id": (
                            f"ember-fact:{superseded_by[fid]}"
                            if fid in superseded_by else None),
                    },
                },
                "truth": {
                    "support_class": "supported",
                    "confidence": min(1.0, max(0.0, float(
                        fact.get("importance") or 5) / 10.0)),
                    "confidence_history": [],
                    "contradiction_status": "none",
                    "approval_state": "approved",
                },
                "provenance": {
                    "source_type": "ember-memory-face",
                    "source_ref": f"mimir-well memory {fid}",
                    "source_hash": hashlib.sha256(
                        content.encode("utf-8")).hexdigest()[:16],
                    "extracted_at": exported_at,
                    "extracted_by": "ember-memory-face/e-086",
                },
                "lifecycle": {
                    "write_policy": ("promotable" if current
                                     else "ephemeral"),
                    "retention_class": "long",
                    "decay_curve": "exp",
                    "expires_at": fact.get("valid_until"),
                    "last_accessed_at": None,
                    "access_count": 0,
                    "stale_after_days": None,
                },
                "retrieval": {
                    "embedding_id": None,
                    "lexical_terms": [],
                    "facets": {
                        "category": [category],
                        "tags": self._wyrd_tags(fact.get("tags")),
                        "current": ["true" if current else "false"],
                    },
                    "default_priority": 0.0,
                },
                "governance": {
                    "sensitivity": "medium",
                    "memory_poison_risk": "low",
                    "allowed_for_runtime": True,
                    "allowed_for_training": False,
                    "requires_review_before_promotion": True,
                },
                "audit": {
                    "created_at": fact.get("timestamp"),
                    "updated_at": fact.get("timestamp"),
                    "created_by_agent": WYRD_SYSTEM_ID,
                    "updated_by_agent": WYRD_SYSTEM_ID,
                },
            }

        records = [fact_record(f, current=True)
                   for f in seen["facts"]]
        records += [fact_record(f, current=False)
                    for f in seen["old_facts"]]
        canonical = [{
            "record_id": f"ember-fact:{int(f['id'])}",
            "subject_id": subject,
            "fact_key": str(f.get("category") or "general"),
            "fact_value": str(f.get("content", "")),
            "confidence": min(1.0, max(0.0, float(
                f.get("importance") or 5) / 10.0)),
            "domain": str(f.get("memory_type") or "general"),
            "uncertain": False,
            "confidence_history": [],
        } for f in seen["facts"]]
        stamped = 0
        for ep in seen["turns"]:
            if ep.started_at is not None:
                observed = ep.started_at.isoformat()
            else:
                observed = exported_at
                stamped += 1
            records.append({
                "record_id": f"ember-turn:{ep.id}",
                "store": WYRD_STORE_HUGIN,
                "record_type": "observation",
                "schema_version": WYRD_RECORD_SCHEMA_VERSION,
                "tenant_id": persona,
                "system_id": WYRD_SYSTEM_ID,
                "entity_scope": {
                    "primary_subjects": [subject],
                    "secondary_subjects": [WYRD_COMPANION_ENTITY_ID],
                    "scene_id": None,
                    "session_id": None,
                    "world_id": None,
                    "project_id": None,
                },
                "content": {
                    "title": f"conversation turn {ep.id}",
                    "summary": ep.operator_input,
                    "body_ref": None,
                    "structured_payload": {
                        "observation_kind": "utterance",
                        "raw_excerpt": ep.operator_input,
                        "normalized_claims": [],
                        "participants": [subject,
                                         WYRD_COMPANION_ENTITY_ID],
                        "observed_at": observed,
                        "place_id": None,
                        "salience": 0.5,
                        "candidate_memory_write": False,
                    },
                },
                "truth": {
                    "support_class": "supported",
                    "confidence": 0.5,
                    "confidence_history": [],
                    "contradiction_status": "none",
                    "approval_state": "approved",
                },
                "provenance": {
                    "source_type": "ember-memory-face",
                    "source_ref": f"brunnr episode {ep.id}",
                    "source_hash": None,
                    "extracted_at": exported_at,
                    "extracted_by": "ember-memory-face/e-086",
                },
                "lifecycle": {
                    "write_policy": "promotable",
                    "retention_class": "long",
                    "decay_curve": "none",
                    "expires_at": None,
                    "last_accessed_at": None,
                    "access_count": 0,
                    "stale_after_days": None,
                },
                "retrieval": {
                    "embedding_id": None,
                    "lexical_terms": [],
                    "facets": {},
                    "default_priority": 0.0,
                },
                "governance": {
                    "sensitivity": "medium",
                    "memory_poison_risk": "low",
                    "allowed_for_runtime": True,
                    "allowed_for_training": False,
                    "requires_review_before_promotion": True,
                },
                "audit": {
                    "created_at": observed,
                    "updated_at": observed,
                    "created_by_agent": WYRD_SYSTEM_ID,
                    "updated_by_agent": WYRD_SYSTEM_ID,
                },
            })
        bundle = {
            "kind": WYRD_EXPORT_KIND,
            "version": 1,
            "wyrd_schema_version": WYRD_RECORD_SCHEMA_VERSION,
            "persona": persona,
            "subject_id": subject,
            "exported_at": exported_at,
            "boundary": {
                "this_side_owns": "cognition and memory "
                                  "(ThoughtForge TF-145)",
                "wyrd_owns": "the world-model",
                "this_export": "memory data in WYRD's published "
                               "record shapes, offered one-way; "
                               "Ember builds no world model and "
                               "writes nothing into WYRD",
            },
            "entities": [
                {"entity_id": subject, "name": persona,
                 "description": "the person this companion "
                                "remembers for",
                 "status": "current", "tags": ["ember-persona"],
                 "location_id": None},
                {"entity_id": WYRD_COMPANION_ENTITY_ID,
                 "name": "Ember",
                 "description": "the companion itself",
                 "status": "current", "tags": ["ember-companion"],
                 "location_id": None},
            ],
            "canonical_facts": {subject: canonical},
            "records": records,
            "counts": {
                "entities": 2,
                "canonical_facts": len(canonical),
                "superseded_facts": len(seen["old_facts"]),
                "observations": len(seen["turns"]),
                "records": len(records),
                "turns_time_stamped_at_export": stamped,
            },
            "note": (
                f"{persona}'s memory in the shapes the WYRD "
                "Protocol's world-model work consumes: "
                f"{len(canonical)} fact(s) still believed true, "
                f"{len(seen['old_facts'])} old version(s) marked "
                f"superseded, and {len(seen['turns'])} remembered "
                "turn(s) as observations. Shaping the offering is "
                "Ember's side of the TF-145 boundary; the "
                "world-model itself is WYRD's, and nothing here "
                "belongs to anyone else."),
        }
        if path is not None:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + ".tmp")
            tmp.write_text(json.dumps(bundle, indent=1, sort_keys=True,
                                      default=str), encoding="utf-8")
            os.replace(tmp, target)
            bundle = {**bundle, "written_to": str(target)}
        return bundle

    def delete_fact(
        self, fact_id: int, *, persona_id: Optional[str] = None
    ) -> dict:
        """Forget one fact, for real.

        Its row is removed from the memory store (the
        member's audit keeps only a hash of its number,
        never its words) and its meaning-search entry is
        dropped. A fact you do not own cannot be forgotten
        from here, and the refusal changes nothing.
        """
        persona = self._persona(persona_id)
        if persona is None:
            return {"deleted": False, "note": self._invalid_persona_note(persona_id)}
        if self._mimir is None:
            return {"deleted": False, "note": f"mimir-well {self.mimir_state}"}
        if self._mimir.get_memory(int(fact_id), user_id=persona) is None:
            return {"deleted": False,
                    "note": "nothing deleted: that fact is not this "
                            "persona's to forget"}
        # The fact's own old versions point at it
        # (superseded_by is a foreign key in the member's
        # store): deleting it first would be refused by
        # that key and strand the chain. Forgetting a fact
        # forgets its lineage — the old versions of this
        # very fact go first, oldest first. (Found by
        # E-086's gate duty: a delete that met the chain
        # in the wrong order died on the key, mid-delete.)
        lineage = sorted(
            (f for f in self._all_facts(persona)
             if f.get("superseded_by") is not None
             and int(f["superseded_by"]) == int(fact_id)),
            key=lambda f: int(f["id"]))
        old_deleted = 0
        for old in lineage:
            if self._mimir.delete_memory(
                    int(old["id"]),
                    source="ember-memory-face/delete-lineage",
                    user_id=persona):
                old_deleted += 1
                if str(old["id"]) in self._sidecar.fact_chunk:
                    del self._sidecar.fact_chunk[str(old["id"])]
                    self._sidecar.fact_persona.pop(str(old["id"]), None)
        if old_deleted:
            self._sidecar.save()
        ok = self._mimir.delete_memory(
            int(fact_id), source="ember-memory-face/delete",
            user_id=persona)
        if not ok:
            return {"deleted": False,
                    "old_versions_deleted": old_deleted,
                    "note": "refused by mimir-well; the fact itself "
                            "was not deleted"
                            + (f", but {old_deleted} old version(s) "
                               "of it were forgotten first"
                               if old_deleted else "")}
        changed = False
        if str(fact_id) in self._sidecar.fact_chunk:
            del self._sidecar.fact_chunk[str(fact_id)]
            self._sidecar.fact_persona.pop(str(fact_id), None)
            changed = True
        # A forgotten fact's logger provenance (E-085) goes
        # with it: a later feed of the same logged words is
        # a fresh crossing, not a duplicate of a fact that
        # no longer exists.
        lineage_ids = {int(old["id"]) for old in lineage}
        for key in [k for k, v in self._sidecar.log_facts.items()
                    if v.get("fact_id") == int(fact_id)
                    or v.get("fact_id") in lineage_ids]:
            del self._sidecar.log_facts[key]
            changed = True
        if changed:
            self._sidecar.save()
        return {"deleted": True, "fact_id": int(fact_id),
                "old_versions_deleted": old_deleted,
                "note": "forgotten: the fact is gone from the memory "
                        "store and from meaning search"
                        + (f", with {old_deleted} old version(s) of "
                           "it that pointed at it" if old_deleted
                           else "")}

    def delete_all_memory(
        self, *, persona_id: Optional[str] = None, confirmation: str = "",
    ) -> dict:
        """Forget *everything* for one persona. Total.

        Guarded by the exact confirmation words
        (:data:`DELETE_ALL_CONFIRMATION`): anything else
        refuses and deletes nothing. When it runs: every
        living fact the persona owns — still-true and old
        versions alike — is removed from the store, every
        index entry is dropped, and every remembered turn
        is tombstoned so it is never served, inspected, or
        exported again. One honest limit: a turn's physical
        bytes stay in the document store because its handle
        has no delete (docket 119) — forgotten here means
        unreachable and uncounted, and the report says so.
        No other persona's memory is touched.
        """
        persona = self._persona(persona_id)
        if persona is None:
            return {"deleted": False, "note": self._invalid_persona_note(persona_id)}
        if confirmation != DELETE_ALL_CONFIRMATION:
            return {"deleted": False,
                    "note": "nothing deleted: to forget everything, "
                            f"say exactly {DELETE_ALL_CONFIRMATION!r}"}
        if self._mimir is None:
            return {"deleted": False, "note": f"mimir-well {self.mimir_state}"}
        # Oldest first: an old version's superseded_by
        # points at a later-created fact (a foreign key in
        # the member's store), so deleting in the search
        # order (importance/timestamp) can meet a fact
        # while an old version still points at it — the
        # member refuses on the key and the total delete
        # dies half-done. Ascending id order always
        # removes referrers before referents. (Found by
        # E-086's gate duty, in E-084's own battery under
        # load; fixed here, regression-pinned in E-086's.)
        facts = sorted(self._all_facts(persona),
                       key=lambda f: int(f["id"]))
        facts_deleted = 0
        for fact in facts:
            if self._mimir.delete_memory(
                    int(fact["id"]), source="ember-memory-face/delete-all",
                    user_id=persona):
                facts_deleted += 1
        turns = self._all_turns(persona)
        for ep in turns:
            if ep.id is not None:
                self._sidecar.deleted_episodes.add(int(ep.id))
                self._sidecar.episode_persona.pop(str(ep.id), None)
        dropped = 0
        for fact_id_s, owner in list(self._sidecar.fact_persona.items()):
            if owner == persona:
                self._sidecar.fact_chunk.pop(fact_id_s, None)
                del self._sidecar.fact_persona[fact_id_s]
                dropped += 1
        # The persona's logger provenance (E-085) is its
        # memory too: total deletion drops it whole.
        for key in [k for k, v in self._sidecar.log_facts.items()
                    if v.get("persona") == persona]:
            del self._sidecar.log_facts[key]
        self._sidecar.save()
        return {
            "deleted": True,
            "persona": persona,
            "facts_deleted": facts_deleted,
            "turns_forgotten": len(turns),
            "index_entries_dropped": dropped,
            "turn_physical_bytes_reclaimed": 0,
            "note": (
                f"everything forgotten for {persona}: "
                f"{facts_deleted} fact(s) removed from the memory "
                f"store and {len(turns)} turn(s) forgotten. The "
                "turns' stored bytes are not physically reclaimed "
                "yet — the document store's handle has no delete "
                "(docket 119) — but no turn can be seen, searched, "
                "or exported from here ever again."),
        }

    # ------------------------------------------------------------------ #
    # Logger reconciliation — two views, one crossing (E-085)             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _log_key(session_id: str, category: str, content: str) -> str:
        """The provenance key of one fed candidate: a hash
        of (session, category, words) — the same identity
        E-072's feed dedupes on, kept as a hash so the
        sidecar holds no second copy of the words."""
        return hashlib.sha256(
            f"{session_id}\0{category}\0{content}".encode("utf-8")
        ).hexdigest()

    def ingest_log_candidates(
        self, candidates, *, persona_id: Optional[str] = None
    ) -> dict:
        """Receive the logger's feed (E-072) into memory.

        Each candidate that is in the lawful shape — source
        ``conversation_logger``, a feedable category,
        non-empty words, a named session, a provenance dict,
        and a *named* persona (a persona is never guessed,
        E-072 §5) — is remembered as a living fact for that
        persona through the face's own guarded path, and
        its provenance is recorded in the sidecar. A repeat
        of an already-fed (session, category, words) is a
        counted duplicate, never a second fact. When
        ``persona_id`` is named by the caller, a candidate
        tagged for anyone else is withheld, not re-homed.
        The report is counts and new fact ids only — no
        candidate words, no session ids — in E-072's
        counts-only discipline.
        """
        report = {
            "total": 0, "ingested": 0, "fact_ids": [],
            "withheld_duplicate": 0, "withheld_unattributable": 0,
            "withheld_invalid": 0, "withheld_persona_mismatch": 0,
            "withheld_blocked": 0,
            "note": "",
        }
        explicit = None
        if persona_id is not None:
            explicit = self._persona(persona_id)
            if explicit is None:
                report["note"] = self._invalid_persona_note(persona_id)
                report["total"] = len(list(candidates))
                report["withheld_invalid"] = report["total"]
                return report
        changed = False
        for cand in candidates:
            report["total"] += 1
            if not isinstance(cand, dict):
                report["withheld_invalid"] += 1
                continue
            content = cand.get("content")
            category = cand.get("category")
            session_id = cand.get("session_id")
            if (cand.get("source") != LOG_FEED_SOURCE
                    or category not in LOG_FEED_CATEGORIES
                    or not isinstance(content, str) or not content.strip()
                    or not isinstance(cand.get("provenance"), dict)):
                report["withheld_invalid"] += 1
                continue
            if not isinstance(session_id, str) or not session_id:
                report["withheld_unattributable"] += 1
                continue
            cand_persona = cand.get("persona_id")
            if (not isinstance(cand_persona, str)
                    or not is_valid_persona_id(cand_persona)):
                report["withheld_unattributable"] += 1
                continue
            if explicit is not None and cand_persona != explicit:
                report["withheld_persona_mismatch"] += 1
                continue
            key = self._log_key(session_id, category, content)
            prior = self._sidecar.log_facts.get(key)
            if prior is not None:
                still = (
                    self.inspect_fact(int(prior.get("fact_id", -1)),
                                      persona_id=cand_persona)
                    if prior.get("fact_id") is not None else None)
                if still is not None:
                    report["withheld_duplicate"] += 1
                    continue
                # The fed fact is gone (forgotten outside the
                # face's delete paths): its provenance is
                # stale, so the crossing may happen afresh.
                del self._sidecar.log_facts[key]
                changed = True
            result = self.remember_fact(
                content, category=category, persona_id=cand_persona)
            if result.fact_id is None:
                report["withheld_blocked"] += 1
                continue
            provenance = cand["provenance"]
            self._sidecar.log_facts[key] = {
                "fact_id": int(result.fact_id),
                "session_id": session_id,
                "persona": cand_persona,
                "category": category,
                "rule_id": provenance.get("rule_id"),
            }
            changed = True
            report["ingested"] += 1
            report["fact_ids"].append(int(result.fact_id))
        if changed:
            self._sidecar.save()
        report["note"] = (
            f"{report['ingested']} logged entr"
            f"{'y' if report['ingested'] == 1 else 'ies'} became "
            "living fact(s); every other candidate is counted "
            "under the reason it was withheld")
        return report

    def logger_provenance(
        self, *, persona_id: Optional[str] = None
    ) -> list[dict]:
        """Which living facts came from the logger, and from
        which session — provenance only, never the words.

        One row per fed fact the persona owns: its fact id,
        the session that fed it, its category, and the rule
        that let it cross. Another persona's fed facts are
        never listed; an invalid persona id lists nothing.
        """
        if persona_id is not None:
            persona = self._persona(persona_id)
            if persona is None:
                return []
            rows = [v for v in self._sidecar.log_facts.values()
                    if v.get("persona") == persona]
        else:
            rows = list(self._sidecar.log_facts.values())
        return sorted(
            ({
                "fact_id": int(v["fact_id"]),
                "session_id": v.get("session_id"),
                "persona": v.get("persona"),
                "category": v.get("category"),
                "rule_id": v.get("rule_id"),
            } for v in rows if v.get("fact_id") is not None),
            key=lambda r: r["fact_id"])

    def audit_logger_reconciliation(
        self, live_session_ids, *, persona_id: Optional[str] = None
    ) -> dict:
        """Find fed facts whose session has left the log.

        ``live_session_ids`` is the caller's authoritative
        list of the sessions still in the logger. A fed
        fact whose session is not among them is *orphaned*:
        its words came from a session the diary no longer
        holds. The audit deletes nothing — it reports
        counts and the orphaned fact ids so the caller can
        decide, and :meth:`retract_deleted_session` can
        act. One warning, stated in every report: the live
        list must come from a deletion the user made
        (E-063's right), never from a size-pruned log —
        Bifröst's line pruning (docket 100) is machine
        hygiene, not a deletion, and auditing against a
        pruned log would mistake hygiene for intent.
        """
        rows = self.logger_provenance(persona_id=persona_id)
        if persona_id is not None and self._persona(persona_id) is None:
            return {"tracked": 0, "still_logged": 0, "orphaned": 0,
                    "orphaned_fact_ids": [],
                    "note": self._invalid_persona_note(persona_id)}
        live = {str(s) for s in live_session_ids}
        orphaned = [r for r in rows if r["session_id"] not in live]
        return {
            "tracked": len(rows),
            "still_logged": len(rows) - len(orphaned),
            "orphaned": len(orphaned),
            "orphaned_fact_ids": [r["fact_id"] for r in orphaned],
            "note": (
                "audit only — nothing was deleted. An orphan is "
                "a fact fed from a session no longer in the "
                "caller's live list; retract it with "
                "retract_deleted_session. Never audit against a "
                "size-pruned log: pruning is hygiene, not a "
                "user deletion (docket 100)."),
        }

    def retract_deleted_session(
        self, session_id: str, *, persona_id: Optional[str] = None
    ) -> dict:
        """Carry one logger deletion into memory (docket 104).

        Forgets exactly the living facts that the named
        session fed — each through the face's own
        :meth:`delete_fact`, so its index entry and its
        provenance go with it — and nothing else: facts the
        session's persona remembered directly, and every
        other session's fed facts, are untouched. A fed
        fact already forgotten by the user is counted as
        already gone, and its stale provenance is dropped
        either way. This operation *is* docket 104's
        propagation: the logger has no hook into this core
        (it is a standalone member), so deletion reaches
        already-fed memory when the caller who deleted the
        session runs this — never silently, never
        automatically, and provably once run.
        """
        if persona_id is not None and self._persona(persona_id) is None:
            return {"retracted": 0, "already_gone": 0, "fact_ids": [],
                    "note": self._invalid_persona_note(persona_id)}
        targets = [
            v for v in list(self._sidecar.log_facts.values())
            if v.get("session_id") == session_id
            and (persona_id is None or v.get("persona") == persona_id)
        ]
        retracted: list[int] = []
        already_gone = 0
        for entry in targets:
            fact_id = int(entry["fact_id"])
            out = self.delete_fact(
                fact_id, persona_id=str(entry.get("persona")))
            if out.get("deleted"):
                retracted.append(fact_id)
            else:
                already_gone += 1
                for key in [k for k, v in self._sidecar.log_facts.items()
                            if v.get("fact_id") == fact_id]:
                    del self._sidecar.log_facts[key]
                self._sidecar.save()
        return {
            "retracted": len(retracted),
            "already_gone": already_gone,
            "fact_ids": retracted,
            "session_id": session_id,
            "note": (
                f"session {session_id}'s fed facts are forgotten "
                "from memory; facts remembered directly and other "
                "sessions' fed facts were not touched. This "
                "retraction is how a logger deletion reaches "
                "already-fed memory (docket 104): it runs when "
                "called, not automatically — the logger is a "
                "standalone member with no hook into the core."),
        }

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
        persona = self._persona(persona_id)
        if persona is None:
            return {"decayed": 0, "pruned": 0, "reinforced": 0,
                    "note": self._invalid_persona_note(persona_id)}
        result = self._mimir.decay(
            half_life_days=half_life_days,
            user_id=persona)
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

    def _document_hits(self, hits: list[RetrievalHit]) -> list[RetrievalHit]:
        """Document-search results with the fact index removed.

        The fact index is a synthetic Brunnr document whose
        chunks are living-fact *text*. Serving one through a
        document search would hand a persona's facts to any
        caller with no persona check at all — the E-083
        battery caught exactly that leak (docket 114). The
        index is served only through the persona-resolved
        fact paths; as a *document* it does not exist.
        """
        index_id = self._sidecar.index_document_id
        if index_id is None:
            return hits
        return [h for h in hits if h.document_id != index_id]

    def search_documents_word(self, query: str, *, k: int = 5) -> list[RetrievalHit]:
        if self._brunnr is None:
            return []
        # Widen past the index chunks the filter drops, so
        # filtering never starves real documents (docket 114).
        width = max(k, 1)
        while True:
            raw = self._brunnr.text_search(query, width)
            hits = self._document_hits(raw)
            if len(hits) >= k or len(raw) < width:
                return hits[:k]
            width *= 2

    def search_documents_meaning(
        self, qvec: Sequence[float], *, k: int = 5
    ) -> list[RetrievalHit]:
        if self._brunnr is None:
            return []
        width = max(k, 1)
        while True:
            raw = self._brunnr.vector_search(qvec, k=width)
            hits = self._document_hits(raw)
            if len(hits) >= k or len(raw) < width:
                return hits[:k]
            width *= 2

    def add_turn(self, episode: Episode) -> Optional[int]:
        """Remember one conversation turn (Brunnr episode).

        The face records the episode's persona tag in its
        sidecar, above the adapter (docket 110) — the tag
        the adapter cannot persist is the face's to keep.
        An episode whose tag is not a valid persona slug is
        refused (returns ``None``, nothing stored): a tag
        the read side would fail closed on must never be
        written in the first place (docket 118).
        """
        if self._brunnr is None:
            return None
        if not is_valid_persona_id(episode.persona_id):
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
        face's default persona only (docket 117 — the
        *configured* default, not a hard-coded id). The
        scan widens until the persona's turns are found or
        the store is exhausted, and the answer is the
        persona's *newest* ``limit`` turns in the store's
        oldest-first order (docket 115): the fixed window
        this replaces both starved a persona behind a run
        of another persona's newer turns and, within its
        window, handed back the *oldest* matches instead
        of the newest — stale history wearing a recent
        name.
        """
        if self._brunnr is None or limit <= 0:
            return []
        persona = self._persona(persona_id)
        if persona is None:
            return []
        width = max(limit * 4, limit)
        while True:
            window = self._brunnr.recent_episodes(width)
            mine = [
                ep for ep in window
                if ep.id not in self._sidecar.deleted_episodes
                and (self._sidecar.episode_persona.get(str(ep.id))
                     or self.default_persona_id) == persona
            ]
            # A wider window only ever adds *older* episodes
            # at the front, so once `limit` of the persona's
            # turns are in hand their newest tail cannot
            # change; an exhausted window is complete either way.
            if len(mine) >= limit or len(window) < width:
                return mine[-limit:]
            width *= 2


__all__ = [
    "CANONICAL_MIMIR_DB_PATH",
    "DELETE_ALL_CONFIRMATION",
    "EPISODE_BYTES_PER_TURN",
    "FACT_BYTES_PER_FACT",
    "FACT_INDEX_SOURCE",
    "INDEX_BYTES_PER_FACT",
    "INDEX_DEFAULT_PROFILES",
    "LOG_FEED_CATEGORIES",
    "LOG_FEED_SOURCE",
    "FactResult",
    "LifecycleReport",
    "MeaningHits",
    "MemoryFace",
    "index_default_for",
]
