"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.
The plan of the first slice lives at ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md``.

Phases 1-4 of the first slice are complete: typed schemas under
:mod:`ember.schemas`; the Well realm is wired via
:mod:`ember.well.brunnr.sqlite_vec` and :mod:`ember.well.smidja`; and
the Thread realm's tether :mod:`ember.thread.strengr` wraps Brunnr-open
with retry-on-recoverable-failures and a never-raising ``health()``
probe. :mod:`ember.spark` and :mod:`ember.cli` remain scaffolds;
``python -m ember`` still raises ``NotImplementedError``.
"""

__version__ = "0.0.0"
