"""Brunnr — the Well's storage contract (API v1, E-037).

Public surface::

    from ember.well.brunnr import BrunnrHandle, open

The :class:`BrunnrHandle` protocol is the minimum surface every
Well backend satisfies; the module-level :func:`open` dispatches
on the configured backend. Concrete adapters (``sqlite_vec``,
``pgvector``) live in their subpackages and are reached through
``open`` — they are not part of the frozen API (E-037).
"""

from ember.well.brunnr.handle import BrunnrHandle, open

__all__ = ["BrunnrHandle", "open"]
