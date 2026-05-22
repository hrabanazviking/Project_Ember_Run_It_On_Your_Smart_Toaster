# 82 — Phase 2: Bridges and Voice

The second Klóinn adoption phase. Mid-effort features that
expand where Ember can be reached + how operators interact.

---

## What Phase 2 ships

By the end of Phase 2:

- **Matrix bridge** (sovereignty-aligned channel access).
- **Telegram bridge** (mainstream channel access).
- **Talk Mode** (push-to-talk voice; Rödd sibling).
- **Voice Wake** (always-listening, opt-in).
- **Sandbox backends** (subprocess; Docker opt-in).
- **Carapace Defense** layers fully implemented + tested.
- **Pincer Loop** as opt-in plan-then-execute.
- **Skills as pip packages** (entry points + audit tool).
- **Daemon mode** for always-on operations.

Phase 2 *unlocks where operators can reach Ember*.

---

## Prerequisites

Phase 2 needs:
- Phase 1 complete (workspace files, sessions, Gateway).
- Yggdrasil Phase 4 (federation infrastructure).

Daemon mode is shared infrastructure; Phase 2 leans on it.

---

## Work breakdown

### Track A: Matrix bridge (~6 weeks)

Tasks:
1. `bifrost-bridge-matrix` sibling package.
2. matrix-nio integration.
3. E2EE via Olm/Megolm.
4. Per-room routing config.
5. Sandbox integration.
6. Setup wizard.
7. Tests against test homeserver.
8. Documentation.

**Risk:** matrix-nio API churn.  
**Mitigation:** pin version; integration test detects breaks.

### Track B: Telegram bridge (~4 weeks)

Tasks:
1. `bifrost-bridge-telegram` sibling package.
2. python-telegram-bot integration.
3. Authorized-user-ID enforcement.
4. Rate limiting.
5. Setup wizard.
6. Tests against test bot.
7. Documentation.

**Risk:** Telegram API change.  
**Mitigation:** pin library; documented update procedure.

### Track C: Rödd Talk Mode (~5 weeks)

Tasks:
1. Rödd sibling: `ember-agent[voice]`.
2. Microphone integration (sounddevice).
3. STT (faster-whisper).
4. TTS (Piper).
5. Push-to-talk hotkey listener.
6. Stofa integration (visual indicators).
7. Audio device configuration.
8. Tests + setup wizard.
9. Documentation.

**Risk:** audio device variability across platforms.  
**Mitigation:** detection + fallback; clear error messages.

### Track D: Rödd Voice Wake (~4 weeks; extends Track C)

Tasks:
1. openWakeWord integration.
2. Custom wake-word: "hey ember" model.
3. Wake → STT bridge.
4. Mic LED indicator (where supported).
5. Privacy controls (mute hotkey).
6. Tests.
7. Documentation.

**Risk:** wake-word reliability varies.  
**Mitigation:** documented sensitivity tuning.

### Track E: Sandbox backends (~5 weeks)

Tasks:
1. Sandbox Protocol.
2. NoSandbox + SubprocessSandbox implementations.
3. DockerSandbox as opt-in pip extra.
4. Tool framework integration.
5. Sandbox registry + health.
6. Tests (Linux primary).
7. Documentation.

**Risk:** subprocess sandbox edge cases.  
**Mitigation:** extensive integration tests.

### Track F: Pincer Loop (~3 weeks)

Tasks:
1. Plan-then-execute prompt structure.
2. Plan parser + validator.
3. Audit-on-plan integration.
4. Revision loop.
5. Opt-in trigger conditions.
6. Tests + documentation.

**Risk:** doubles LLM latency for some turns.  
**Mitigation:** opt-in default off; cohort-specific use cases.

### Track G: Skills as pip packages (~3 weeks)

Tasks:
1. Skill Protocol definition.
2. Entry-points discovery.
3. Skill audit tool (`ember skill audit`).
4. Skill scaffold template.
5. First bundled skill (e.g., `ember-skill-cron`).
6. Documentation.

**Risk:** community skills don't materialize.  
**Mitigation:** infrastructure ships; ecosystem grows
organically.

### Track H: Cross-cutting (~3 weeks)

- ADRs for each major change.
- DEVLOG entries.
- Migration V1 → V2.
- Performance regression testing.

---

## Total estimate

Roughly 33 weeks. Real-world: 6-9 months calendar.

This is *substantial work*. Worth it.

---

## What ship-readiness looks like

- [ ] All Phase 1 features still work.
- [ ] Matrix + Telegram bridges connect + chat end-to-end.
- [ ] Voice Talk Mode works on Linux/macOS/Windows.
- [ ] Voice Wake works on Linux + macOS.
- [ ] Subprocess sandbox functions on Linux.
- [ ] Pincer Loop usable when opted in.
- [ ] First skill installable via pip.
- [ ] Doctor screen shows all new realms.
- [ ] Documentation comprehensive.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Bridge API breakage | High | Pin versions; test in CI |
| Voice latency on Pi | High | Document realistic expectations |
| Sandbox bypass | High | Carapace layers compensate |
| Pincer doubles latency | Med | Opt-in default off |
| Skill ecosystem fizzles | Low | Infrastructure shipped; doesn't depend on community |
| Cross-platform voice quirks | Med | Per-platform testing |

---

## What operators experience after Phase 2

### Voice-first operator

```bash
$ ember --voice chat
[Listening for "hey ember"]
Operator: "Hey ember, what's on my schedule today?"
Ember: "[STT processes]... [LLM thinks]... [TTS speaks]"
```

Hands-free chat. Daily companion.

### Multi-channel operator

```
Operator messages Ember bot in Telegram. Ember replies in
Telegram.

Operator messages a Matrix room. Ember replies in Matrix.

Both bridges run in one home Ember daemon.
```

Wherever the operator is, Ember reaches.

### High-power-tools operator

```bash
$ pip install ember-skill-code-review
$ ember chat --allow-tools

Ember: Want me to review the diff in your repo?
Operator: yes
Ember: [run_shell_command sandboxed via subprocess]
[reviews and reports]
```

New skills available; sandboxing keeps it safe.

---

## What this enables for Phase 3

Phase 2 builds:
- **Daemon mode** → web companion in Phase 3 needs always-on.
- **Bridges** → multi-channel routing scenarios.
- **Voice** → input/output flexibility.
- **Sandbox** → safe expansion of tool ecosystem.
- **Skills infrastructure** → community contributions.

Phase 3 (Canvas + companion) builds on this.

---

## Phase 2 success criteria

Operator-visible:
- "Ember has voice now."
- "I can chat from Telegram."
- "New tools work safely."

Quantitative:
- Bridges connect reliably.
- Voice latency on Pi < 10s; on laptop < 5s.
- Sandbox catches expected violations.

---

## Closing

Phase 2: Bridges and Voice is **Klóinn's biggest leap**.
Matrix + Telegram + Voice + Sandbox + Pincer + Skills
infrastructure.

This is the phase where Ember **stops being CLI-only** and
becomes *companion-quality*. Operators reach Ember from where
they are; voice makes it ambient; sandbox makes new tools
safe.

Ship target: V2.0. After this, Klóinn-Ember is competitive
with OpenClaw on capability while preserving sovereignty.
