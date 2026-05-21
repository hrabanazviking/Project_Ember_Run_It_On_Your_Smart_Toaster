"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.

**0.2.0rc1 (slice-2 Phase 16): tools live (release candidate).**

``ember chat`` now drives the full propose → approve → execute →
audit → feedback loop when ``tools.enabled: true`` in
``~/.ember/config/ember.yaml`` (or the per-invocation ``--allow-tools``
CLI flag). Three first-party tools ship: ``search_well`` (STANDING),
``read_local_file`` (PER_CALL, sandbox), ``fetch_url`` (PER_CALL,
robots.txt). Hjarta's wizard now asks "Enable tools?" at first-run.
The append-only audit log lives at ``state/tool_audit/<date>.jsonl``.

Earlier milestones: 0.1.9 pgvector live (Phase 13); 0.1.7 streaming
Munnr (Phase 11); 0.1.5 config loader (Phase 9); 0.1.0 first slice
(ratified 2026-05-21). Phase 17 ships **0.2.0** with the slice-2
acceptance test + ADR 0013 ratification.
"""

__version__ = "0.2.0rc1"
