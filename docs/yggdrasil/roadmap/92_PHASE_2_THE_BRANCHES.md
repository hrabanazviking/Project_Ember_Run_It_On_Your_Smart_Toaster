# 92 — Phase 2: The Branches

Mood, rhythm, audit, and embodiment. The outward-facing
layers that make Ember feel *present*.

---

## What Phase 2 delivers

By the end of Phase 2:

- **Seiðr** seeds Ember's responses via the mood channel
  (per [`../architecture/35_THE_SEIDR_GENERATION_PLANE.md`](../architecture/35_THE_SEIDR_GENERATION_PLANE.md)).
- **Astrology Engine** provides rhythm-aware ambient
  context (per [`../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md`](../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md)).
- **Hamr** delivers a basic avatar (still images +
  identity card; no real-time animation yet).
- **Light-mode audit** runs on every chat turn (per
  [`../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md`](../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md)).
- **Doctor + Stofa updates** for the new realms.
- **Operator-controllable feature toggles** for each new
  realm.

Operators experience:
- Ember's tone *fits the moment* more.
- Subtle ambient context ("full moon tonight" if asked).
- Confident-but-not-overconfident replies (audit caught
  obvious errors).
- A face to associate with the voice (avatar).

---

## The work breakdown

### Track A: Seiðr mood channel (~4 weeks)

**Goal:** Seiðr seeds Ember's responses.

Tasks:
1. `SeidrChannel` adapter implementing the `MoodChannel`
   protocol.
2. Mood-to-form mapping per
   [`../ai-capabilities/48_EMOTIONAL_PALETTE_OF_RESPONSES.md`](../ai-capabilities/48_EMOTIONAL_PALETTE_OF_RESPONSES.md).
3. Integration with prompt assembly — Seiðr verse appears
   in system context.
4. Operator-controllable; off by default for V2.0.0; on
   by V2.1.0 once stable.
5. Tests: mood classifier → Seiðr seed → prompt → Funi
   response shape.

**Risk:** Verse seeds could feel out-of-place. **Mitigation:**
operator can disable; we tune which moods seed.

### Track B: Astrology Engine integration (~3 weeks)

**Goal:** rhythm-aware ambient context.

Tasks:
1. `AstrologyRhythm` adapter implementing
   `RhythmSource`.
2. Pre-computed daily snapshot (per
   [`../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md`](../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md)).
3. Verdandi events on phase change.
4. Prompt-assembly hooks: rhythm context optionally
   added to system prompt.
5. CLI: `ember rhythm now`, `ember rhythm date <YYYY-MM-DD>`.

**Risk:** Astronomical correctness across timezones. **Mitigation:**
Swiss Ephemeris is reliable; we test against known dates.

### Track C: Hamr (basic) (~4 weeks)

**Goal:** an avatar for Ember.

Tasks:
1. `HamrSource` adapter implementing `AvatarSource`.
2. Stofa Identity Card widget shows current portrait.
3. Per-mood portrait variants (loaded from a small
   default set).
4. Operator can install custom portraits via
   `ember hamr install <path>`.
5. NO real-time animation yet (Phase 3+ when GPU profile
   warrants).

**Risk:** Asset licensing. **Mitigation:** ship a small
CC0 default; operator-installs the rest.

### Track D: Light-mode audit (~3 weeks)

**Goal:** catch hallucinations before they ship.

Tasks:
1. `AuditPipeline` running after Funi draft.
2. Citation reality check (Brunnr lookup).
3. Internal consistency check (regex).
4. Capability honesty check (tool-registry lookup).
5. Re-draft logic when checks fail.
6. Verdandi audit events.

**Risk:** False positives causing re-drafts unnecessarily.
**Mitigation:** operator-tunable thresholds; default
conservative.

### Track E: Updated Doctor + Stofa (~2 weeks)

- New rows for Seiðr, Astrology, Hamr, Audit.
- Status indicators for each.
- Settings screens for each.
- Updated wizard (Hjarta) to mention new features in
  first-run flow.

### Track F: Cross-cutting (~2 weeks)

- ADRs updated.
- DEVLOG entries.
- Migration: V1 → V2.
- Test coverage expansion.

---

## Total estimate

Roughly 18 weeks. Real-world: 4-6 months after Phase 1
ships.

---

## What ship-readiness looks like

- [ ] All Phase 1 functionality still works.
- [ ] New realms integrate without breaking baseline.
- [ ] Audit catches at least 3 categories of common
      hallucination on synthetic test set.
- [ ] Astrology computes correctly for 2026-2030 test
      dates.
- [ ] Hamr installable + visible in Stofa.
- [ ] Seiðr-seeded responses tested by operator-
      personas (Iðunn / Volmarr / Sigrún).
- [ ] Doctor screen shows all V2 realms.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Audit false-positives annoy operators | Medium | Conservative thresholds; opt-in tightening |
| Seiðr seeds feel like noise | Medium | Default off; on by 2.1 after iteration |
| Hamr asset licensing | Low | Ship CC0 only; operator installs others |
| Astronomy timezone bugs | Low | Test against known events |

---

## Phase 2 success criteria

Operator-visible:
- Tone-aware register is noticeable.
- Audit prevents at least one citation hallucination per
  week (in operator testing).
- Avatar makes Ember feel *present* (subjective; ask
  operator).
- No regressions in Phase 1 functionality.

Operationally:
- V1 → V2 migration is seamless.
- All test markers pass.

---

## Closing

Phase 2: The Branches **extends Ember outward**. Memory
(Phase 1) gains tone, rhythm, embodiment, integrity-
checking. Ember becomes *present in the moment* — not
just memory + reasoning.

The branches reach beyond the roots; the system spreads.
