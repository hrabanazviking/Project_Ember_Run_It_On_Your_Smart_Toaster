"""pgvector Brunnr adapter (ADR 0010).

Public entry points::

    from ember.well.brunnr.pgvector import open, PgVectorBrunnr

The :func:`open` callable is dispatched to by the top-level Brunnr
registry in :mod:`ember.well.brunnr.handle` when the operator selects
``BrunnrBackend.PGVECTOR``.
"""

from __future__ import annotations

from ember.well.brunnr.pgvector.adapter import PgVectorBrunnr, open

__all__ = ["PgVectorBrunnr", "open"]
