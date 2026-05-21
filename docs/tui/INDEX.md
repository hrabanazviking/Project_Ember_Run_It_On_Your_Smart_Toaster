# Stofa — Ember's TUI Design Tree

**Stofa** (Old Norse: *the hall*) is the Terminal-User-Interface surface for
Project Ember. This directory is the **design tree** — the complete planning,
research, and architecture documentation that precedes any code.

Per the Mythic Engineering iron law: *document before code*. Stofa is a
substantial new surface (more than a re-skin of `ember chat`); it gets the
same ADR + roadmap discipline as the Brunnr adapters or the MCP integration.

---

## What Stofa is

Stofa is the operator's **mead-hall** — a cozy, beautiful, robust, fun
terminal interface where they sit with Ember by the hearth. The chat REPL
(`ember chat`) is a single sliver of what Ember can be; Stofa is the full
hall:

- **A persistent home** for chatting, browsing the Well, running ingest,
  watching health, managing MCP, tuning settings — all without juggling
  command lines or losing context.
- **Beautiful by default.** Modern type, considered color, Norse-inflected
  ornament. Not gaudy; not corporate; not nerd-cave-utilitarian.
- **Cute and alive.** Text-mode pets roam the floor — Hugin the raven
  perches on the Well counter, Geri-cub yawns when nothing's happening,
  Heiðrún drops a mead-horn into the audit log when a tool fires. They
  are decorative AND helpful — see [`pets/`](pets/).
- **Stable to a fault.** Resizes correctly, survives terminal-emulator
  quirks, degrades gracefully when colors / Unicode / mouse aren't
  available. Per the Vow of the Unbroken Whole.
- **Keyboard-first.** Operators who never touch a mouse get the whole UI;
  operators who like mice get sensible mouse support too.
- **Discoverable.** A pressed `?` always tells you what you can do here.

Sibling surfaces (per the slice-3 roadmap):
- **Auga** — GUI (ADR-0012 placeholder)
- **Rödd** — voice surface (ADR-0012 placeholder)
- **Bifröst** — HTTP gateway (ADR-0012 placeholder)

Stofa is the first of the four to be designed end-to-end. The others share
data via the existing handles (`FuniHandle`, `BrunnrHandle`, `MCPClientPool`).

---

## Map of the design tree

```
docs/tui/
├── INDEX.md                       ← you are here
│
├── vision/                        ← Skald (Sigrún) ── the why
│   ├── 00_VISION.md               ── what Stofa is
│   ├── 01_NAMING.md               ── why "Stofa", how to say it
│   ├── 02_DESIGN_PHILOSOPHY.md    ── cozy / Norse / fun / robust
│   ├── 03_USER_PERSONAS.md        ── who sits in the hall
│   └── 04_PETS_VISION.md          ── why the pets matter
│
├── architecture/                  ← Architect (Rúnhild) ── the shape
│   ├── 10_ARCHITECTURE_OVERVIEW.md
│   ├── 11_FRAMEWORK_COMPARISON.md ── Textual vs Rich vs prompt-toolkit
│   ├── 12_STATE_MACHINE.md
│   ├── 13_SCREEN_HIERARCHY.md
│   ├── 14_LAYOUT_SYSTEM.md
│   ├── 15_THEMING_SYSTEM.md
│   ├── 16_KEYBINDING_PHILOSOPHY.md
│   ├── 17_DATA_FLOW.md
│   ├── 18_PLUGIN_ARCHITECTURE.md
│   └── 19_REPO_MAP.md
│
├── research/                      ← Cartographer + Scribe ── lessons from giants
│   ├── 20_RESEARCH_INDEX.md
│   ├── 21_LAZYGIT.md
│   ├── 22_HTOP_AND_BTOP.md
│   ├── 23_NEOVIM_AND_HELIX.md
│   ├── 24_RANGER_AND_NNN.md
│   ├── 25_ATUIN.md
│   ├── 26_AERC.md
│   ├── 27_GLOW.md
│   ├── 28_LAZYDOCKER.md
│   ├── 29_K9S.md
│   ├── 30_GH_DASH.md
│   ├── 31_SPOTIFY_TUI.md
│   ├── 32_CHATGPT_AND_AI_TUIS.md
│   ├── 33_DECORATIVE_TUIS_NAP_PIPES_NEKOTUI.md
│   └── 34_SYNTHESIS.md            ── what we steal, what we avoid
│
├── ux-science/                    ← Auditor + Scribe ── the laws
│   ├── 40_FITTS_LAW_FOR_KEYBOARDS.md
│   ├── 41_HICKS_LAW_AND_MENUS.md
│   ├── 42_INFORMATION_DENSITY.md
│   ├── 43_VISUAL_HIERARCHY.md
│   ├── 44_COLOR_THEORY_FOR_TERMINALS.md
│   ├── 45_TYPOGRAPHY_FOR_MONOSPACE.md
│   ├── 46_ACCESSIBILITY.md
│   ├── 47_INTERACTION_PATTERNS.md
│   ├── 48_ANIMATION_AND_TIMING.md
│   └── 49_PROGRESSIVE_DISCLOSURE.md
│
├── design/                        ← Skald + Auditor ── the look
│   ├── 60_VIKING_AESTHETIC.md
│   ├── 61_RUNIC_TYPOGRAPHY.md
│   ├── 62_BOX_DRAWING_VOCABULARY.md
│   ├── 63_ICON_VOCABULARY.md
│   ├── 64_PALETTE_AURORA.md       ── default (cool, twilight)
│   ├── 65_PALETTE_MIDGARD.md      ── warm earth, daylight
│   ├── 66_PALETTE_GINNUNGAGAP.md  ── deep void, true-black
│   ├── 67_PALETTE_SOLSTICE.md     ── high-contrast
│   └── 68_PALETTE_BARROW.md       ── colorblind-safe
│
├── pets/                          ← Skald + Forge ── the menagerie
│   ├── 70_PETS_OVERVIEW.md
│   ├── 71_PETS_BESTIARY.md        ── all 9 creatures
│   ├── 72_PETS_BEHAVIOR_ENGINE.md
│   ├── 73_PETS_SPRITE_GUIDE.md    ── ASCII art reference
│   ├── 74_PETS_HELPFULNESS.md     ── what they DO besides be cute
│   └── 75_PETS_PERSONALITY_PROFILES.md
│
├── screens/                       ← Architect ── one per surface
│   ├── 80_SCREEN_HOME.md
│   ├── 81_SCREEN_CHAT.md
│   ├── 82_SCREEN_WELL.md
│   ├── 83_SCREEN_DOCTOR.md
│   ├── 84_SCREEN_SETTINGS.md
│   ├── 85_SCREEN_MCP.md
│   ├── 86_SCREEN_TOOL_APPROVAL.md
│   ├── 87_SCREEN_HJARTA_WIZARD.md
│   └── 88_HELP_OVERLAY.md
│
├── operations/                    ← Auditor ── the robustness
│   ├── 90_PERFORMANCE_BUDGETS.md
│   ├── 91_TERMINAL_COMPAT_MATRIX.md
│   ├── 92_RESIZE_HANDLING.md
│   ├── 93_ERROR_BOUNDARIES.md
│   └── 94_OBSERVABILITY.md
│
└── roadmap/                       ← Forge + Scribe ── the doing
    ├── 99_ROADMAP_PHASE_1_HEARTH.md     ── MVP: chat + home + quit
    ├── 99_ROADMAP_PHASE_2_THE_HALL.md   ── Well, Doctor, Settings
    ├── 99_ROADMAP_PHASE_3_THE_FAMILIARS.md  ── Pets + MCP + Themes
    └── 99_ROADMAP_PHASE_4_THE_FEAST.md  ── Polish + community plugins
```

---

## Where to start reading

- **Curious why this exists?** → [`vision/00_VISION.md`](vision/00_VISION.md)
- **Want to see the look?** → [`design/64_PALETTE_AURORA.md`](design/64_PALETTE_AURORA.md), then [`design/62_BOX_DRAWING_VOCABULARY.md`](design/62_BOX_DRAWING_VOCABULARY.md)
- **Want to meet the pets?** → [`pets/71_PETS_BESTIARY.md`](pets/71_PETS_BESTIARY.md)
- **Want to build it?** → [`roadmap/99_ROADMAP_PHASE_1_HEARTH.md`](roadmap/99_ROADMAP_PHASE_1_HEARTH.md)
- **Want the technical bones?** → [`architecture/10_ARCHITECTURE_OVERVIEW.md`](architecture/10_ARCHITECTURE_OVERVIEW.md), then [`architecture/11_FRAMEWORK_COMPARISON.md`](architecture/11_FRAMEWORK_COMPARISON.md)

---

## Stofa is gated on slice 3 ADR

Per ADR-0012 (placeholder, not yet ratified), the slice-3 external-surface
work bundles Stofa + Auga + Rödd + Bifröst. **No Stofa code lands until ADR
0015 (Stofa-specific ratification) is drafted, the slice-2-extended branch
is closed at 0.2.x, and the operator (Volmarr) green-lights the design.**

This design tree is the input to ADR 0015. Nothing here commits the project;
it commits us to the *next* conversation about what to build.

---

## Status

| Document area | Status | Owner role |
|---|---|---|
| Vision | drafted, 2026-05-21 | Skald |
| Architecture | drafted, 2026-05-21 | Architect |
| Research (15 TUIs) | drafted, 2026-05-21 | Cartographer + Scribe |
| UX Science | drafted, 2026-05-21 | Auditor + Scribe |
| Design + Palettes | drafted, 2026-05-21 | Skald + Auditor |
| Pets | drafted, 2026-05-21 | Skald + Forge |
| Screens | drafted, 2026-05-21 | Architect |
| Operations | drafted, 2026-05-21 | Auditor |
| Roadmap | drafted, 2026-05-21 | Forge + Scribe |
| ADR-0015 | not started | — |
| Code | not started | — |
