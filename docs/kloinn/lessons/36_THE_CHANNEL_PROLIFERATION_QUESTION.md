# 36 — The Channel Proliferation Question

OpenClaw ships 23+ messaging channel bridges. Ember should ship
how many? The cost-benefit of every channel.

---

## The premise

Operators are already in messaging apps. They prefer
interacting *in* those apps over opening a separate AI
assistant.

OpenClaw's bet: bridge to *all* major channels. Reduce friction
to near zero.

This works because OpenClaw has:
- Massive contributor base.
- Time to write + maintain 23 bridges.
- Operators wanting breadth.

---

## What 23 bridges actually costs

### Per-bridge ongoing costs

Each channel has:
- An API that *changes* (sometimes silently).
- Edge cases (rate limits, attachments, reactions).
- Auth flows that vary.
- Documentation requirements.
- Security implications (each is a new attack surface).

Per bridge per year: ~10-50 hours of maintenance.

23 bridges: ~230-1150 hours/year. That's 0.1-0.5 FTE of
*just bridge maintenance*.

### Per-bridge upfront costs

Each new bridge: ~80-200 hours to implement, test, document.
First-time setup of OAuth, webhook handlers, message
translators.

23 bridges to *initially* build: ~1800-4600 hours. Several
FTE-years.

This is *the price OpenClaw paid* to reach mainstream
coverage. It's substantial.

---

## What Ember should ship

Per [`../patterns/16_MULTI_CHANNEL_MESSAGING.md`](../patterns/16_MULTI_CHANNEL_MESSAGING.md):

🟢 **Adapt to Ember Vows**: ship 2-3 bridges in Phase 4.

### Tier 1 (Phase 4 ship)

- **Matrix** — sovereignty-aligned; covers many transitive
  channels (via Matrix's own bridges).
- **Telegram** — broadly used by sovereignty-leaning users; bot
  API is mature + stable.

That's it. Two bridges.

### Tier 2 (Phase 4 late or Phase 5)

- **Signal** — privacy-aligned; signal-cli library makes
  bridging viable.
- **IRC** — old-school operators; libraries are mature.

### Tier 3 (community contributions in Phase 5+)

- **Discord** — community might want; we don't build but accept
  contributions.
- **Slack** — work-context use; community-contributed if
  demand.
- **WhatsApp** — Meta-controlled; would require cloud
  components; we don't.
- **WeChat / QQ / LINE / others** — region-specific;
  community-contributed if interest.

---

## Why Matrix first

Matrix is the *most aligned* bridge for Ember:

- **Open standard**: not vendor-controlled.
- **Self-hostable**: operators can run their own homeserver.
- **End-to-end encryption**: Olm/Megolm crypto.
- **Federated**: connects to other Matrix servers naturally.
- **Bridges to other channels**: Matrix's own
  matrix-appservice-* bridges cover Discord, Slack, IRC, Signal,
  WhatsApp, etc.

So **one Matrix bridge** for Ember = *transitive access to
many channels* via Matrix's bridging ecosystem.

This is *leverage*. We build one bridge; operators reach many
networks.

---

## Why Telegram second

Telegram bot API is:
- Mature + stable.
- Well-documented.
- Easy to integrate (HTTPS webhooks or long-polling).
- Free for our use case.

Telegram is *popular* with sovereignty-leaning operators
(crypto, OSINT, security communities). Good cohort fit.

Risk: Telegram is *not* end-to-end encrypted by default
(secret chats are; group chats aren't). Operators must know.

---

## Why NOT WhatsApp

- Meta-controlled API; can change unilaterally.
- API access requires Meta business approval.
- Bridges often require running on Meta-approved infrastructure.
- Sovereignty conflicts with platform terms.

For Ember: skip. Operators who want WhatsApp can use Matrix's
WhatsApp bridge (with their own setup).

---

## Why NOT iMessage

- Apple-controlled; no public API.
- Bridges (e.g., BlueBubbles) require a Mac running 24/7 as
  bridge.
- Sovereignty + simplicity conflict.

Skip.

---

## What about email

OpenClaw doesn't seem to bridge email (it's listed in some
contexts as "WebChat" but unclear).

For Ember: email is *interesting*:
- SMTP/IMAP are open protocols.
- Email is universal.
- Async by nature (matches AI conversation rhythm).

Could be a Phase 5+ consideration. "Email Ember a question; get
a reply hours later." Different rhythm than chat.

Defer; not in Phase 4 scope.

---

## Routing across channels

Per Yggdrasil + Klóinn integration:

```yaml
ember:
  bridges:
    matrix:
      enabled: true
      route_to: main_persona
    telegram:
      enabled: true
      route_to: personal_persona  # if multi-persona enabled
    
  routing:
    default: main_persona
```

Channels route to personas. Operator decides where each goes.

---

## Bridge as sibling project

🔵 **Borrow as-is**: each bridge is its own sibling project.

Following the existing Ember sibling pattern:

- `ember-bridge-matrix` (or `bifrost-matrix` extending the
  bifrost sibling).
- `ember-bridge-telegram`.

Each is a separate pip package; operator opt-in.

This keeps core Ember small. Operators who don't use bridges
don't pay the cost.

---

## Security implications

Each bridge is an *external surface*. Risks:

- **Authentication compromise**: bot token leaks; bridge
  account taken over.
- **Message injection**: malicious actor sends crafted message
  that exploits Ember's tool layer.
- **DOS via channel**: bridge gets flooded with messages.
- **Privacy leak**: channel logs operator's chats.

Mitigations:
- **Per-bridge auth in Kista**: tokens encrypted; rotated.
- **Per-bridge sandbox** (per
  [`34_THE_SANDBOX_QUESTION.md`](34_THE_SANDBOX_QUESTION.md)):
  bridged sessions sandbox by default.
- **Rate limits**: per-channel inbound rate limits.
- **Audit log**: every channel-bridged turn logged.
- **Operator review**: operators see bridge activity in Doctor
  screen.

---

## The trust-the-bridge question

Channel bridges *necessarily* involve trusting the bridge
process:

- The bridge sees the operator's messages.
- The bridge could log them.
- The bridge could be compromised.

Mitigations:
- Open-source the bridge code; operators can audit.
- Run bridge in same process or sandboxed subprocess; not
  external service.
- No bridge "phones home."

This is *the same trust model* as any local Ember component.
We extend the principle to bridges.

---

## When ought we ship more bridges

Phase 4 ships Matrix + Telegram. Phase 5+ ships more *if*:

1. **Operator demand**: substantial fraction of operators ask
   for a specific channel.
2. **Maintenance volunteer**: someone commits to ongoing
   maintenance of that bridge.
3. **Sovereignty alignment**: the channel supports
   self-hosting / encryption / open protocols.

If all three: ship. If only some: defer.

This is *demand-driven, not feature-driven*. We don't ship
bridges *just because OpenClaw has them*.

---

## What 2 bridges enables

Even with just Matrix + Telegram, operators get:

- Matrix → access to most major chat platforms via
  Matrix-bridge transitively.
- Telegram → direct access to a popular channel.
- Combined: most operators are reachable.

2 bridges + Matrix's bridge ecosystem ≈ many channels covered
without us maintaining them all.

This is *leverage*. Ember provides the *interface*; Matrix
provides the *bridge ecosystem*.

---

## Configuration shape

```yaml
ember:
  bridges:
    enabled: false  # opt-in
    
    matrix:
      enabled: false
      homeserver: matrix.org
      user_id: "@ember:matrix.org"
      access_token_ref: kista://matrix/token
      device_id: ember-1
      rooms:
        listen: ["#ember-chat:matrix.org"]
        e2ee: true
      sandbox_session: true
    
    telegram:
      enabled: false
      bot_token_ref: kista://telegram/bot_token
      authorized_user_ids: [123456789]
      polling_mode: long_polling
      sandbox_session: true
```

---

## What the operator experiences

After Phase 4 ships:

```bash
# Operator wants to chat with Ember via Telegram.
ember bridge enable telegram
> Telegram bot token: ████████
> Authorized user ID: 123456789
> Configure Ember persona for Telegram: (main / personal / work)
> ... 

# Bridge starts; operator can now message Ember bot from
# their phone's Telegram. Conversations land in Ember; replies
# return to Telegram.
```

Setup is **operator-driven**, not auto-magic.

---

## The aspirational "any channel" path

Some operators might want *every* channel. They can:
- Use Matrix + Matrix's bridges to reach 15+ channels.
- Run their own per-channel adapter using a community library.
- Contribute their adapter back to the community.

This *empowers operators* without burdening Ember maintainers.

The Vow of Modular Authorship at work: operator-curated breadth,
not maintainer-shipped breadth.

---

## Closing

The Channel Proliferation Question is **a real strategic
choice**. OpenClaw ships everything; Ember ships strategically.

Ember's bridge strategy:
- 🟢 Phase 4: ship Matrix + Telegram.
- 🟡 Phase 5: Signal + IRC if demand exists.
- 🔴 Skip WhatsApp + iMessage (sovereignty conflicts).
- 🔵 Borrow Matrix's bridge ecosystem for transitive reach.
- 🟢 Each bridge is a sibling project; operators opt in.

We don't compete with OpenClaw on breadth. We compete on
*depth + sovereignty*. Our 2-3 bridges, well-built, serve our
cohort better than 23 half-built would.

The Klóinn lesson: **bridges are leverage, not features-for-
features-sake**. Pick the right 2-3; build them well; lean on
Matrix for the rest.
