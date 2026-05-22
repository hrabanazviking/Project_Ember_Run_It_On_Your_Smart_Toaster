# 83 — Phase 3: Canvas and Channels

The third and final Klóinn adoption phase. High-effort
features that complete the constellation.

---

## What Phase 3 ships

By the end of Phase 3:

- **OdinUI / Live Canvas** (rich UI in agent responses).
- **Web companion** (PWA paired via tailnet).
- **Deep Water Federation** (resilient multi-device).
- **Personas** (opt-in multi-identity).
- **Tide Routing** (adaptive cross-node routing).
- **Menu Bar Presence** (cross-platform desktop integration).
- **Moult Cycle** (monthly maintenance).
- **Claw Negotiation** (operator-AI disagreement).
- **Auga** sibling (graphical surface for OdinUI).

Phase 3 *completes the Klóinn vision*.

---

## Prerequisites

Phase 3 needs:
- Phase 2 complete (voice, bridges, sandbox).
- Yggdrasil Phase 5 (Constellation; Skein/Skry/Mirror).
- Stofa shipped (V2; needed for Canvas TUI rendering).

---

## Work breakdown

### Track A: OdinUI / Live Canvas (~10 weeks)

Tasks:
1. OdinUI spec definition + JSON Schema.
2. Pydantic validators for each component.
3. TUI renderer (Stofa).
4. Web renderer (companion PWA).
5. Munnr text-fallback renderer.
6. Funi prompt augmentation to emit OdinUI.
7. Form submission → chat-turn integration.
8. Per-session widget state caching.
9. Documentation.
10. Tests.

**Risk:** spec ambiguity → renderer inconsistencies.  
**Mitigation:** strict validation; per-component test suite.

### Track B: Web companion (PWA) (~8 weeks)

Tasks:
1. HTTP/WebSocket server in Ember.
2. PWA frontend (HTML/CSS/JS).
3. Service worker for offline-installability.
4. Pairing flow (QR + token).
5. Session token management.
6. Tailscale integration (Magic DNS, encryption).
7. PWA manifest + icons.
8. OdinUI rendering in browser.
9. Documentation.

**Risk:** mobile browser compatibility variance.  
**Mitigation:** test iOS + Android browsers; document
limitations.

### Track C: Deep Water Federation (~6 weeks)

Tasks:
1. Outbound + inbound queue implementations.
2. Persistence (jsonl).
3. Retry with backoff.
4. Sequence numbers + ack handling.
5. Bandwidth optimization (compress, strip).
6. Operator-visible status.
7. Integration with web companion.
8. Tests (simulated slow link).

**Risk:** edge cases in queue persistence.  
**Mitigation:** comprehensive integration tests.

### Track D: Personas (~5 weeks)

Tasks:
1. Persona directory structure.
2. Per-persona prompt files.
3. Per-persona session storage.
4. Per-persona sandbox/tool config.
5. Persona-switching CLI + Stofa.
6. Migration single-persona → multi.
7. Documentation.

**Risk:** confusion across personas.  
**Mitigation:** persistent visual indicators.

### Track E: Tide Routing (~4 weeks)

Tasks:
1. Routing rule engine.
2. Static rule evaluation.
3. Heuristics (latency, GPU, presence).
4. Federation integration.
5. Doctor screen visibility.
6. Operator override commands.
7. Documentation.

**Risk:** complex routing edge cases.  
**Mitigation:** observable; operator overrides.

### Track F: Menu Bar Presence (~3 weeks)

Tasks:
1. pystray-based menu bar.
2. Cross-platform icon + menu.
3. Status indicators.
4. Quick chat window.
5. Notifications integration.
6. Daemon mode integration.
7. Per-platform setup docs.

**Risk:** Linux desktop fragmentation.  
**Mitigation:** support major DEs; document known issues.

### Track G: Moult Cycle (~3 weeks)

Tasks:
1. Monthly scheduling.
2. Proposal generation per area.
3. Auto-apply low-risk.
4. Operator review interface.
5. Snapshot before each moult.
6. History command.
7. Documentation.

**Risk:** wrong things archived; operator can't recover.  
**Mitigation:** snapshots + restore command.

### Track H: Claw Negotiation (~3 weeks)

Tasks:
1. Disagreement detection.
2. Negotiation message generation.
3. Operator response parsing.
4. Well-update suggestions.
5. Meta-learning integration.
6. Operator-suppression option.

**Risk:** triggers too often; annoying.  
**Mitigation:** threshold tuning; opt-in default off.

### Track I: Auga sibling (~6 weeks)

Tasks:
1. Auga as separate sibling.
2. Textual-web as rendering layer.
3. OdinUI Canvas integration.
4. Persistent state per session.
5. Same content as Stofa, GUI presentation.
6. Documentation.

**Risk:** maintains parity with Stofa.  
**Mitigation:** share code where possible (Textual-web).

### Track J: Cross-cutting (~3 weeks)

- ADRs for each.
- Migration V2 → V3.
- Performance regression.
- Full documentation refresh.

---

## Total estimate

Roughly 51 weeks. Real-world: 12-18 months calendar.

This is **the longest phase**. Multi-quarter. Substantial.

---

## What ship-readiness looks like

- [ ] All previous phases stable.
- [ ] Canvas renders correctly on Stofa + web.
- [ ] Web companion pairs + chats reliably.
- [ ] Deep Water survives simulated bad networks.
- [ ] Personas isolated correctly.
- [ ] Tide routes per rules + heuristics.
- [ ] Menu bar functional on macOS + Windows + KDE.
- [ ] Moult Cycle runs monthly + surfaces proposals.
- [ ] Claw Negotiation respects operator overrides.
- [ ] Auga renders OdinUI as designed.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Phase 3 scope explosion | High | Aggressive cuts; defer non-critical |
| Auga maintenance burden | High | Lean on Textual-web; minimal divergence from Stofa |
| Browser fragmentation | Med | Document support matrix |
| Deep Water edge cases | High | Extensive testing under simulated failures |
| Operator overwhelm | Med | Default off for opt-ins; clear docs |

---

## What operators experience after Phase 3

### Mobile-companion operator

Opens phone browser → tailnet Ember → chat session continues
seamlessly from laptop. Forms render natively. Voice works
on phone too (if Rödd configured).

### Personas operator

Has work + personal + research personas. Each with own
prompts + memory + sessions. Switches per moment.

### Cluster operator

Multiple Ember nodes (laptop, homelab, Pi). Tide routes per
load + latency. Federation handles failovers.

### Long-term operator

After 6+ months: monthly Moult Cycle surfaces tuning
proposals. Operator + Ember evolve together.

---

## Phase 3 success criteria

Operator-visible:
- "Ember on my phone works."
- "Canvas elements appear when relevant."
- "I have multiple personas now."
- "Background maintenance keeps things tidy."

Quantitative:
- Web companion latency: < 100ms on tailnet.
- Canvas rendering: < 500ms.
- Federation Deep Water: 99% reliability over 30 days.
- Moult Cycle: completes monthly with no regressions.

---

## After Phase 3

Phase 3 is **the constellation complete** for Klóinn. Beyond:

- V4+: emergent operator-driven features.
- Multi-modal Ember (with Yggdrasil V5+).
- Foundation model upgrades as community models improve.
- Community ecosystem maturation.

The system is *deep + broad* by Phase 3. Future work is
*refinement + adaptation*, not foundational shift.

---

## What Klóinn doesn't promise after Phase 3

🔴 **Still NOT in scope**:

- Native mobile apps (web companion suffices for most).
- 23+ channel bridges (2-3 high-value only).
- Centralized skill registry.
- Cloud-hosted Ember offerings.
- Telemetry / call-home.

These remain rejected. Vows preserved through V3 and beyond.

---

## Cumulative work across 3 phases

| Phase | Estimated weeks |
|---|---|
| 1 | 16 |
| 2 | 33 |
| 3 | 51 |
| Total | 100 |

100 weeks = ~2 years calendar (assuming part-time).
Substantial. Pays back in operator value + project maturity.

---

## Closing

Phase 3: Canvas and Channels **completes the Klóinn
adoption**. Canvas + web companion + Deep Water + personas
+ Tide + Menu Bar + Moult + Claw + Auga.

Ship target: V3.0 — *the Klóinn-informed mature Ember*.

After V3: Ember is **both deep architecturally (Yggdrasil)
and broad ergonomically (Klóinn)**. The two trees compose.
Operators get the best of both philosophies — *without*
losing sovereignty.

The Klóinn Codex closes here. 57 documents; three phases; one
sister project that taught us what we needed to learn.

We thank Molty + the OpenClaw maintainers. May both projects
thrive. May the operator cohorts each project serves find
their tools.

— *the Skald, in closing*
