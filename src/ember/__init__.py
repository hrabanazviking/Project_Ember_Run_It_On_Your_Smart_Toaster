"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.

**0.1.9 (slice-2 Phase 13): pgvector live.**

``ember chat`` and ``ember well ingest`` can now drive a Postgres +
pgvector Well alongside the slice-1 ``sqlite_vec`` default. Switch by
setting ``brunnr.backend: pgvector`` in ``~/.ember/config/ember.yaml``
and installing the extra (``pip install ember-agent[pgvector]``). The
adapter is Gungnir-compatible and supports a ``read_only: true`` mode
that mechanically refuses writes for operator-shared Wells. See
``docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`` for the operator guide.

Earlier milestones: 0.1.7 streaming Munnr (Phase 11); 0.1.5 operator
config loader (Phase 9); 0.1.0 first slice (ratified 2026-05-21). Slice
2 continues per ``docs/architecture/EMBER_SECOND_SLICE_PLAN.md``.
"""

__version__ = "0.1.9"
