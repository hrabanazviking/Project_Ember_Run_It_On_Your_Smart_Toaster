# 50 — Self-Healing Philosophy

The principles that make Yggdrasil resilient to partial
failure. Five philosophical rules; every later robustness
doc applies them.

---

## The five principles

### 1. Every realm fails independently

No single realm's failure cascades to others. Mímir down →
the agent continues with Huginn + Muninn. Verdandi down →
self-awareness disabled; chat continues. Kista down → realms
that need secrets pause; realms that don't, continue.

This is the **Vow of the Unbroken Whole** applied at the
realm scale.

### 2. Failure must be observable

A silent failure is the worst failure. Every realm publishes
its health state via Verdandi. Every cross-realm operation
produces a Receipt (per
[`../architecture/39_THE_RECONCILIATION_LAYER.md`](../architecture/39_THE_RECONCILIATION_LAYER.md)).
Operators (and Ember herself) can always answer "what
broke?"

### 3. Recovery is automatic for transient failures

Network blips, brief restarts, momentary disk hiccups
should heal themselves without operator action. The
reconciliation worker + gossip protocol + per-realm health
probes converge automatically.

### 4. Persistent failures get one clear surface

When something doesn't self-heal in N attempts, surface to
the operator *clearly and once* — not silently, not
repeatedly. The Doctor screen + a one-time chat-banner
notification.

### 5. Operator intervention is always available

For everything the system can auto-heal, the operator can
also manually trigger the heal. For everything the system
*can't* heal, the operator gets clear next-steps. Nothing
is hidden behind "the system decides."

---

## What "self-healing" means here

It does NOT mean:
- AI mystically repairing itself.
- Auto-rewriting code on failure.
- Auto-restarting services that should stay down (e.g.,
  one that's leaking memory).

It DOES mean:
- Re-trying transient failures with backoff.
- Reopening connections that dropped.
- Restoring state from the Norns snapshots when needed.
- Surfacing persistent failures with operator-actionable
  guidance.

Bounded mechanical recovery. Not magic.

---

## The healing hierarchy

Healing happens at several layers, each with progressively
more aggressive recovery:

### Layer 1: in-call retry (immediate, transparent)

For very transient errors — a single failed read from
Huginn might just be a network hiccup. The adapter retries
once internally. Operator never sees it.

### Layer 2: backoff retry (background, observable)

For failures that persist beyond one retry. The
reconciliation worker picks up the Receipt; retries with
exponential backoff. Operator sees it in the Doctor screen
if they look; otherwise invisible.

### Layer 3: realm restart (background, automatic for some realms)

If a realm has been unreachable for > N minutes, the
restart playbook tries to bring it back. Specific to each
realm:
- Qdrant: try docker container restart (if managed).
- Verdandi: try daemon restart.
- mimir-well: re-open the SQLite handle.

These are *operator-controllable* (default off for some;
on for low-risk realms).

### Layer 4: realm degradation (operator-facing)

When a realm can't be restored automatically, mark it as
degraded. The system continues with the realm offline; a
clear banner tells the operator what's missing.

### Layer 5: operator intervention (manual)

When the operator must act, they get:
- Clear next-step in the Doctor screen.
- A chat-banner once (not repeated).
- Optional: an alert via Verdandi-bridge-to-notification-
  system.

---

## What gets healed vs what doesn't

**Auto-healed:**
- Network blips to Huginn / Verdandi / Bifrǫst / external
  APIs.
- Brief Qdrant restarts (if managed by Yggdrasil).
- Transient sqlite locks.
- Brief Kista unlock-required prompts (if cached unlock
  available).

**NOT auto-healed (operator action required):**
- Configuration errors (`ember.yaml` syntax wrong).
- Persistent realm unavailability (Qdrant won't start).
- Disk full.
- Kista master-key forgotten.
- Schema migrations that need operator decision.

The line: **anything that requires a choice → operator
decides**. Anything that's just a retry → the system does
it.

---

## The "graceful degradation" gradient

Yggdrasil's capability fades gracefully as realms fail:

| Realms down | Lost capability |
|---|---|
| 0 (all healthy) | full Yggdrasil |
| Huginn | semantic search; falls back to Mímir-only |
| Verdandi | self-awareness "I notice…"; chat continues |
| Astrology | rhythm-based tone shifts; default tone |
| Seiðr | mood-channel verse seeding; default register |
| CloakBrowser | stealth web; only `fetch_url` available |
| Kista | secret-requiring realms; basic chat works |
| Mímir | structured memory; Huginn-only mode |
| Funi | chat fails; Stofa shows "Funi disconnected" |
| All except Funi + sqlite | bare-bones Ember (like pre-Yggdrasil) |

The operator can lose 9 of 11 realms and *still chat*.
This is the bottom-of-the-stack guarantee.

---

## Why we don't promise more

Some self-healing approaches promise:
- Auto-deploy replacement instances on cloud.
- Auto-failover to backup providers.
- Auto-rewrite of broken configuration.

We don't.

Why:
1. **Sovereignty**: cloud failover means cloud dependency.
2. **Predictability**: auto-rewriting config might do
   the wrong thing; operator should approve.
3. **Resource cost**: Pi-class operators can't afford
   redundant instances.
4. **Honesty**: we shouldn't promise what we can't
   reliably deliver.

The promises we *do* make are deliberately modest. We
*meet* them.

---

## How the operator experiences self-healing

Most days: invisible. Things work. Things that hiccup
recover. Nothing surfaces.

Some days: brief banners. "Huginn was unreachable for 2
minutes; recovered automatically." Acknowledgment, not
alarm.

Rare days: persistent failure surfaces. "Qdrant has been
down for 30 minutes. Doctor screen has details. Bifrǫst
is operating Mímir-only mode in the meantime."

Operator-actionable, not panicky.

---

## Closing

Self-Healing Philosophy is **modest, mechanical,
operator-respectful**. We don't promise magic. We promise
that transient failures *just heal*, that persistent ones
*get surfaced clearly*, and that the operator always has
the next step in hand.

Five principles. Five layers of healing. One operator who
trusts the system because the system *deserves* trust.
