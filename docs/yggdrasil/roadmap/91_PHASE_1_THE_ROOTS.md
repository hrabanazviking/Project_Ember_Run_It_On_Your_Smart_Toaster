# 91 — Phase 1: The Roots

The first integration phase. Memory composition + secret
mediation + observability ground.

---

## What Phase 1 delivers

By the end of Phase 1:

- **Bifrǫst** wired as Ember's Brunnr backend (operator
  opt-in via `ember.yaml`).
- **Mímir** + **Huginn** + **Muninn** composed under
  Bifrǫst with RRF fusion.
- **Kista** mediating all secrets via the SecretResolver
  chain.
- **Verdandi** event bus operational, with Ember's chat
  loop publishing events.
- **Doctor screen** updated with new realm rows for
  Bifrǫst, Mímir, Huginn, Muninn, Kista, Verdandi.
- **DEVLOG entry + ADR-0014** updated to record the
  integration.

What operators experience after upgrading to V1:
- Memory feels *better* (better recall, decay-aware).
- Doctor screen shows the new realms.
- Old configs still work (no breaking changes).

---

## What Phase 1 does NOT include

Deferred to later phases:
- Emotional intelligence + Seiðr (Phase 2).
- Self-awareness "I notice…" (Phase 3).
- Federation (Phase 4).
- Mirror reports (Phase 5).

Phase 1 is *memory + observability + secret plane*.
Everything else later.

---

## The work breakdown

### Track A: Bifrǫst integration (~6 weeks)

**Goal:** Bifrǫst as a Brunnr backend.

Tasks:
1. Add `BifrostBrunnr` adapter implementing `BrunnrHandle`.
2. Add config schema (`brunnr.backend: bifrost`).
3. Wire pip extra: `pip install ember-agent[bifrost]`.
4. Integration tests with real Bifrǫst Bridge.
5. Documentation in `docs/adr/0014-mcp-tool-integration.md`
   updated to also cover Bifrǫst.

**Risk:** Bifrǫst's API may change during integration.
**Mitigation:** Pin to specific Bifrǫst version; bump in
controlled releases.

### Track B: Mímir / Huginn / Muninn through Bifrǫst (~4 weeks)

**Goal:** the three memory backends composed.

Tasks:
1. Each sibling adapter implements the `MemorySource`
   protocol.
2. Bifrǫst's fusion logic delivers RRF output.
3. Health probes for each backend.
4. Tests covering fan-out and graceful degradation.
5. Doctor rows for each.

**Risk:** RRF parameter tuning may need iteration.
**Mitigation:** Operator can override defaults via
`ember.yaml`; ship sensible starting point.

### Track C: Kista secret mediation (~3 weeks)

**Goal:** all secret access through Kista.

Tasks:
1. `SecretResolver` chain replacing direct env-var
   reads.
2. `KistaResolver` implementation calling Kista vault.
3. Migration tool for operators with existing env-var
   secrets to import into Kista.
4. CLI commands: `ember secret resolve`, `ember secret
   set`, `ember kista unlock`.
5. Audit log entries for every secret use.

**Risk:** Operators may not want to migrate; we make
migration *optional* (env-var resolver stays in the
chain).

### Track D: Verdandi event bus (~4 weeks)

**Goal:** observability ground floor.

Tasks:
1. `VerdandiClient` implementing the `EventBus` protocol.
2. Verdandi daemon connection + reconnection logic.
3. Chat loop publishes core events
   (`chat.turn_started`, `chat.turn_finished`, etc.).
4. Stofa StatusBar subscribes to gossip events.
5. Tests for in-process fallback (when daemon
   unavailable).
6. Doctor row showing event-publish health.

**Risk:** UDS socket setup varies by OS. We document
per-platform; provide setup scripts.

### Track E: Cross-cutting (~3 weeks)

- ADR-0014 update + new ADR-0015 (Yggdrasil Phase 1).
- Migration guide: existing Ember installs → V1.
- Updated install docs: new pip extras.
- DEVLOG entries.
- Stofa Settings screen surface for new config sections.
- CI updates for new sibling-dependent test markers.

---

## Total estimate

Roughly 20 weeks of focused work for a single full-time
developer; less for a team.

In practice: many of these tracks proceed in parallel.
Real-world calendar time: 3-6 months from now.

---

## What ship-readiness looks like

Before declaring Phase 1 done:

- [ ] All planned tests pass on Linux + macOS.
- [ ] Tests pass on at least one Pi 5 and one
      workstation device.
- [ ] Operator can `pip install ember-agent[yggdrasil-v1]`
      and get all Phase 1 sibling deps.
- [ ] Migration: existing operators with `~/.ember/state/`
      can upgrade without data loss.
- [ ] Doctor screen shows healthy for all enabled realms.
- [ ] DEVLOG has the V1 entry.
- [ ] Memory files updated.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Sibling project API churn | High | Pin versions; bump in releases |
| Operator migration friction | Medium | Make migrations opt-in; document |
| Performance regression on Pi | Medium | Tier defaults; SMALL profile gets only Mímir |
| Verdandi UDS setup complexity | Medium | Provide setup scripts; in-process fallback |
| RRF parameter tuning takes time | Low | Operator-tunable; ship sensible defaults |

---

## Phase 1 success criteria

Operator-visible:
- Memory feels noticeably better (better recall on
  multi-topic questions).
- "I deleted a doc; will Ember remember it?" → no
  (correctly).
- New Doctor rows visible and green.
- No regressions in baseline chat experience.

Operationally:
- Verdandi event log + audit log are populated.
- Doctor screen functional.
- Secret resolution working end-to-end.

Test-coverage:
- > 90% unit test coverage on new adapters.
- Integration tests for all enabled-realm combinations.
- Pi-class smoke test runs successfully.

---

## After Phase 1

The Roots are in place. Memory is composed. Observability
is grounded. Secrets are mediated.

This is the *plateau* before Phase 2. Real operators can
*use* V1 Ember in production for months while we work on
Phase 2.

---

## Closing

Phase 1: The Roots is **the foundation**. The composed
memory layer; the secret plane; the observability ground;
the audit trail. Without this, nothing in Phase 2-5 works.

We build it carefully. We ship it stable. We let operators
*use* it before we build the next layer.

This is how trees grow — from the roots up.
