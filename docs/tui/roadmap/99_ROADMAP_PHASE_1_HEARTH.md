# 99 — Phase 1: The Hearth (MVP)

The smallest Stofa that's worth shipping. Goal: an operator can
launch, chat, and quit cleanly. Everything else is V2+ work; this
phase proves the architecture.

---

## Phase name

**The Hearth** — the first fire. Just enough warmth to sit by.

---

## Scope

V1.0 ships:

1. **HomeScreen** (basic version: 4 panels, status only; no
   ingest-trigger from here).
2. **ChatScreen** (full streaming + tool approval).
3. **HjartaWizardScreen** (first-launch identity).
4. **HelpOverlay** (`?` from any screen).
5. **The four Tier-1 keybindings:** `c`, `q`, `?`, `Esc`.
6. **One theme:** Aurora.
7. **Two always-on pets:** Funi-spark, Ember-ember.
8. **Two event-pets:** Hugin (retrieval), Refur (approval).
9. **Stable resize** + ASCII fallback.
10. **All Vow-of-Unbroken-Whole safety** (error boundaries,
    graceful service failures).

---

## What V1 explicitly does NOT have

These are V2+ scope:

- WellScreen.
- DoctorScreen.
- SettingsScreen.
- MCPScreen.
- ToolApprovalScreen (V1 inlines approval in the chat; V2 makes it
  a modal).

Wait — that contradicts the ChatScreen design. Let me reconsider.

**Revised V1 scope** (more honest about what shippable means):

V1 ships **Phase 1 = the Hearth Minimum**:
- HomeScreen (read-only dashboard, no actions).
- ChatScreen with streaming + inline tool approval (not separate
  modal; just inline y/n in the input area).
- HjartaWizardScreen.
- HelpOverlay.
- Aurora theme only.
- Funi-spark + Ember-ember + Hugin (3 pets).
- Resize-safe + ASCII fallback.
- All error boundaries.

Phase 2 (the Hall) adds WellScreen, DoctorScreen, more pets,
modal ToolApprovalScreen.

Phase 3 (the Familiars) adds MCPScreen, Settings UI, more themes,
plugin support.

Phase 4 (the Feast) is polish + community.

This staging means V1 is genuinely small. The bottom four files
(`99_*`) cover each phase.

---

## Phase 1 deliverables

### Code

- `src/ember/stofa/__init__.py`
- `src/ember/stofa/app.py` (StofaApp; ~150 LOC)
- `src/ember/stofa/bindings.py` (~30 LOC)
- `src/ember/stofa/messages.py` (~80 LOC)
- `src/ember/stofa/screens/home.py` (~120 LOC, read-only dashboard)
- `src/ember/stofa/screens/chat.py` (~400 LOC, the big one)
- `src/ember/stofa/screens/hjarta_wizard.py` (~200 LOC)
- `src/ember/stofa/screens/help_overlay.py` (~80 LOC)
- `src/ember/stofa/widgets/chrome_header.py`
- `src/ember/stofa/widgets/status_bar.py`
- `src/ember/stofa/widgets/hearth.py`
- `src/ember/stofa/widgets/messages_view.py`
- `src/ember/stofa/widgets/input_bar.py`
- `src/ember/stofa/services/funi_service.py` (~150 LOC)
- `src/ember/stofa/services/well_service.py` (~100 LOC; retrieve-only)
- `src/ember/stofa/pets/__init__.py`
- `src/ember/stofa/pets/pet_layer.py`
- `src/ember/stofa/pets/base.py`
- `src/ember/stofa/pets/funi_spark.py`
- `src/ember/stofa/pets/ember_ember.py`
- `src/ember/stofa/pets/hugin.py`
- `src/ember/stofa/themes/aurora.tcss`
- `src/ember/stofa/utils/responsive.py`
- `src/ember/stofa/utils/ascii_fallback.py`

Approximate: **~25 files, ~2,500 LOC**.

### Tests

- `tests/unit/test_stofa_app.py`
- `tests/unit/test_stofa_messages.py`
- `tests/unit/test_stofa_pets_funi_spark.py`
- `tests/unit/test_stofa_pets_hugin.py`
- `tests/unit/test_stofa_themes_loader.py`
- `tests/integration/test_stofa_e2e_chat_turn.py`
- `tests/integration/test_stofa_e2e_first_run.py`
- `tests/integration/test_stofa_e2e_resize.py`
- `tests/integration/test_stofa_e2e_quit_clean.py`
- Snapshot tests (~10 golden SVGs).

Approximate: **~15 test files, ~1,500 LOC**.

### Config + CLI

- `EmberConfig.stofa: StofaConfig` (schema addition).
- `ember tui` subcommand.
- `[tui]` pip extra.
- `ember` with no args opens Stofa when stdin is TTY.

### ADR

- `docs/decisions/0015-stofa-tui.md` — ratifies this phase.

### DEVLOG

Batch K entry summarizing the ship.

---

## Estimated timeline

For a focused single-developer push (one Mythic Engineering session):

- **Day 1:** Scaffold + bindings + messages + chrome + status bar.
  Stofa launches, shows an empty Home, quits cleanly. (~600 LOC.)
- **Day 2:** ChatScreen + FuniService + streaming. First chat turn
  works end-to-end. (~700 LOC.)
- **Day 3:** Hjarta wizard + identity flow + first-launch path.
  (~400 LOC.)
- **Day 4:** Pets (3) + animation engine + Aurora theme + responsive
  layout. (~400 LOC.)
- **Day 5:** Tests (unit + integration + snapshots) + accessibility
  pass + resize testing. (~1,500 LOC test code.)
- **Day 6:** ADR-0015 draft + DEVLOG + commit + push. PyPI release
  candidate.

**Total: ~5-6 focused days.** This is the *time-budget*. Actual
duration depends on availability.

---

## Success criteria

V1 ships when:

- ✅ `pip install ember-agent[tui]` works.
- ✅ `ember tui` launches in < 3 seconds on Pi 5.
- ✅ First-run wizard completes; identity saved.
- ✅ Chat works end-to-end with streaming + tool approval.
- ✅ Hearth pulses correctly during Funi thinking.
- ✅ Hugin perches on retrieval.
- ✅ Resize at every tested size doesn't break the layout.
- ✅ `q` quits cleanly; terminal restored.
- ✅ All snapshot tests pass.
- ✅ All unit + integration tests pass.
- ✅ Ruff clean.
- ✅ ADR-0015 written + ratified.

---

## Risk register

| Risk | Mitigation |
|---|---|
| Textual API surprises | pin to known-good version range |
| Resize edge cases | snapshot test at every documented size |
| First-launch crash on macOS | manual test on macOS pre-release |
| SSH performance | minimal_redraw mode tested |
| Pet animation eats CPU | aggregate-cap enforced in PetLayer |

---

## Closing

Phase 1 is **small on purpose**. The Hearth Minimum proves the
architecture works, ships a usable Stofa, and sets up the foundation
for Phases 2-4 to layer on screens, pets, themes, plugins.

A bonfire starts as a single coal.
