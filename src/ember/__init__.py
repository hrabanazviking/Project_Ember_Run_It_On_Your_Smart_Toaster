"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.

**0.1.7 (slice-2 Phase 11): streaming live.**

``ember chat`` now writes Funi tokens to stdout as they arrive, instead
of buffering the whole reply. Ctrl-C mid-stream tags the partial reply
with ``[interrupted by operator]`` and the REPL returns to the next
prompt. Operators who prefer the old behaviour can set
``funi.streaming: false`` in ``~/.ember/config/ember.yaml``.

0.1.5 added the operator config loader (slice-2 Phase 9). First slice
(0.1.0) ratified 2026-05-21. Slice 2 in progress per
``docs/architecture/EMBER_SECOND_SLICE_PLAN.md``.
"""

__version__ = "0.1.7"
