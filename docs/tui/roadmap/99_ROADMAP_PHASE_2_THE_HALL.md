# 99 — Phase 2: The Hall (V1.5)

After the Hearth (V1.0) proves the architecture, the Hall fills in
the rest of the rooms.

---

## Phase name

**The Hall** — Stofa as a full home, not just a fireside.

---

## Scope additions

V1.5 adds:

1. **WellScreen** — browse + ingest UI.
2. **DoctorScreen** — full realm health view.
3. **ToolApprovalScreen** as proper modal (replacing V1's inline
   approval).
4. **Two more themes:** Midgard + Ginnungagap.
5. **Three more pets:** Heiðr, Sumarbýfa, Geri-cub.
6. **All 5 Tier-1 screens** (chat, well, doctor, mcp coming in
   Phase 3) reachable.
7. **Full ASCII fallback** for every visual element.
8. **Theme live-switching** via command palette.

---

## Estimated timeline

For a focused push:

- **Day 1:** WellScreen + WellService (full ingest). (~600 LOC.)
- **Day 2:** DoctorScreen + DoctorService + Heiðr pet. (~400 LOC.)
- **Day 3:** ToolApprovalScreen as modal + Refur improvements +
  Sumarbýfa. (~300 LOC.)
- **Day 4:** Midgard + Ginnungagap themes + theme-swap command +
  Geri-cub. (~300 LOC.)
- **Day 5:** Integration tests + snapshot tests for new screens.
  (~700 LOC tests.)
- **Day 6:** DEVLOG + ship.

**Total: ~5-6 focused days.**

---

## Success criteria

- ✅ All 7 V1 screens functional (chat, well, doctor, tool approval,
  hjarta, help, home).
- ✅ 3 themes selectable + live-swappable.
- ✅ 6 pets in V1.5 (was 3 in V1).
- ✅ Ingest flows visibly through Sumarbýfa.
- ✅ All snapshot tests across all themes.
- ✅ Operator can do their primary workflow (chat + occasional
  ingest + occasional Doctor check) without ever using CLI.

---

## What V1.5 does NOT add

- MCPScreen (Phase 3).
- SettingsScreen (Phase 3).
- Plugin system (Phase 3).
- Auga / Rödd / Bifröst (slice-3 separate).

---

## Closing

The Hall is **Stofa as it was meant to be** for operators who don't
need MCP or settings UI yet. Most operators in Phase 2 have
everything they need — chat, well browsing, health, the basic
themes, the cute pets. Phase 3 adds the power-user surfaces.
