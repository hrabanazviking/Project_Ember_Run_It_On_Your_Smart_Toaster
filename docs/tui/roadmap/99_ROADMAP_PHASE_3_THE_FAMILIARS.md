# 99 — Phase 3: The Familiars (V2.0)

Power user surface. MCP management, full Settings, plugin
architecture, more themes, more pets.

---

## Phase name

**The Familiars** — the operator's customized hall, with their
chosen pets, their tuned settings, their plugins.

---

## Scope additions

V2.0 adds:

1. **MCPScreen** — full server management (add, ping, restart, logs,
   per-tool auto-approve).
2. **SettingsScreen** — every config field, form-shaped, with
   field-level help and live-preview.
3. **Plugin system** — entry-points for screens, pets, themes,
   commands, status widgets.
4. **Two more pets:** Ask-sapling, Drift.
5. **Two more themes:** Solstice (high-contrast) + Barrow
   (colorblind-safe).
6. **EpisodeBrowserScreen** (browse + search persisted Episodes).
7. **AuditLogScreen** (paginated audit log viewer).
8. **Theme Studio** (operator-customizable themes via UI).
9. **Reduced-motion respect** (read OS prefers-reduced-motion).
10. **Screen-reader mode** (opt-in alternate rendering).

---

## Estimated timeline

For a focused push:

- **Week 1, Day 1-2:** MCPScreen + MCPService improvements.
- **Week 1, Day 3-4:** SettingsScreen (the big one). Every config
  field gets a widget.
- **Week 1, Day 5:** Plugin entry points + discovery + validation.
- **Week 2, Day 1:** Ask-sapling + Drift pets.
- **Week 2, Day 2:** Solstice + Barrow themes + accessibility
  testing.
- **Week 2, Day 3:** EpisodeBrowserScreen + AuditLogScreen.
- **Week 2, Day 4:** Theme Studio.
- **Week 2, Day 5-6:** Tests + DEVLOG + ship.

**Total: ~10-12 focused days.**

---

## Success criteria

- ✅ Operators can manage MCP entirely in Stofa.
- ✅ Operators never need to hand-edit `ember.yaml`.
- ✅ At least one community plugin proves the architecture
  (e.g., a "weather" pet).
- ✅ All 9 V1+V2 pets work.
- ✅ All 5 themes (V1: Aurora; V1.5: Midgard, Ginnungagap; V2:
  Solstice, Barrow).
- ✅ Accessibility pass: screen-reader mode works, reduced-motion
  honored.

---

## Plugin ecosystem expectations

V2 ships the plugin entry points. By the end of V2:

- The ember-agent maintainers ship a "pets pack" example plugin
  (one or two extra pets).
- Documentation at `docs/STOFA_PLUGINS.md` for plugin authors.
- A few community plugins announce themselves (best-case;
  not gated on this).

---

## What V2 does NOT add

- Auga / Rödd / Bifröst (slice-3 separate).
- Multi-tab chat (V3 maybe).
- Operator-customizable HomeScreen layout (V3 maybe).
- Built-in AI training / fine-tuning (not Stofa's job, ever).

---

## Closing

The Familiars is **Stofa as a real platform**, not just an app.
Operators can extend it. Plugin authors can ship. The full
accessibility + theming + customization story is real. After V2,
Stofa is feature-complete for the "AI hall" use case.

V3 (the Feast) is polish + community + whatever the operators
themselves ask for.
