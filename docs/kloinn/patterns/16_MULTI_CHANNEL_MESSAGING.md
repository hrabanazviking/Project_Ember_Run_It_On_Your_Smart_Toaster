# 16 — Multi-Channel Messaging

OpenClaw's 23+ messaging channel bridges. The pattern; the
benefit; what fits Ember.

---

## What OpenClaw bridges

The full list:

WhatsApp, Telegram, Slack, Discord, Google Chat, Signal,
iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost,
Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, Zalo
Personal, WeChat, QQ, WebChat.

Plus native voice/text on macOS, iOS, Android.

That's **23 channels** plus native platforms — the most
comprehensive messaging integration of any sovereign AI assistant.

---

## Why this matters

Operators are already in messaging apps. Asking them to come to
*your* app raises friction. Bringing AI assistance to where
they already are *removes* friction.

If an operator uses Telegram daily and Ember is invisible to
Telegram, they have to remember to open Ember separately. If
Ember can *be* in Telegram (as a chat with their AI), it
integrates seamlessly into their existing flow.

OpenClaw's bet: meet the operator where they are.

---

## How channel bridges work

Each channel has its own:

- **API** (Telegram Bot API, Slack API, Discord Gateway, etc.)
- **Authentication** (bot tokens, OAuth, etc.)
- **Message format** (text, attachments, reactions, etc.)
- **Webhook / polling setup**

OpenClaw provides a **bridge adapter** per channel:

```
gateway ←→ telegram_bridge ←→ Telegram API
gateway ←→ slack_bridge ←→ Slack API
...
```

Bridges normalize messages: in/out of each channel API, into the
Gateway's standard event shape.

---

## What 23+ channels implies

### Maintenance burden

Each bridge:
- Requires understanding the channel's API.
- Breaks when the channel's API changes.
- Has its own auth flow to maintain.
- Has its own edge cases (rate limits, attachments, etc.).

23 bridges = 23 ongoing maintenance commitments. OpenClaw can
do this because they have ~hundreds of contributors. Ember
cannot match this.

### Operator value

Different operators use different channels. Telegram users
care nothing for WhatsApp. Slack users don't use Discord. The
breadth ensures *most* operators find their channel covered.

For Ember: which channels matter to *our* cohort? Probably:
- Telegram (widely loved by sovereignty-leaning users).
- Matrix (sovereignty-aligned).
- Signal (privacy-aligned).
- IRC (old-school operators).
- maybe Discord (gamers / Norse communities).

Five-ish channels would cover most of Ember's cohort.

---

## The federation alternative

There's a different model than per-channel bridges:

**Federation via standards** — instead of bridging to each
proprietary channel, support an open protocol (Matrix, XMPP,
ActivityPub) that *itself* bridges to many.

Matrix has bridges to most major proprietary platforms.
Ember-supporting-Matrix would *transitively* reach many channels.

This is *much less work* than building 23 bridges. But it
introduces a dependency (Matrix-as-required-middleware) that
may not fit all operators.

---

## What Ember should NOT do

🔴 **Reject**:

### 1. Building 23 bridges

We don't have the resources. Even if we did, the maintenance
burden would *dominate* development time.

### 2. Cloud-hosted bridges

Some channels (WhatsApp, iMessage) require their bridges to run
on cloud infrastructure (WhatsApp's API requires Meta-approved
deployments). Sovereignty-incompatible.

### 3. Auto-installed bridges

OpenClaw lets operators add bridges via skills/extensions.
Ember's pip-extras approach is more conservative: each bridge
is its own optional package; operator chooses what to install.

---

## What Ember should do

🟢 **Adapt to Ember Vows**:

### Phase 4: 2-3 high-value bridges

For Phase 4 (federation), ship:

- **Matrix bridge** — covers many transitive channels; aligned
  with Ember's sovereign values.
- **Telegram bridge** — broadly popular; bot API is mature.
- Optionally **Signal bridge** — privacy-aligned; runs locally.

Each bridge:
- Lives in its own pip extra: `ember-agent[bridge-matrix]`.
- Connects via the Gateway.
- Routes via operator-configured rules.
- Respects per-channel sandbox + audit.

### Phase 5+: more bridges as community contributions

If operators want Discord, IRC, WeChat — let them contribute
bridges as community sibling packages. We curate; we don't
build.

---

## How bridges integrate with multi-agent

If/when multi-agent (per
[`11_MULTI_AGENT_WORKSPACES.md`](11_MULTI_AGENT_WORKSPACES.md))
lands:

```yaml
ember:
  routing:
    bridges.telegram: personal_persona
    bridges.matrix: work_persona
    default: main_persona
```

Each bridge routes to a configured persona. Same Ember; different
contexts per channel.

---

## How bridges interact with privacy

Critical concern: when operator chats via Telegram, the *Telegram
servers* see the messages (in transit). End-to-end encryption is
optional in Telegram (secret chats).

So bridges *necessarily* leak some metadata to the bridge
channel. Operators must be aware.

Ember's approach:
- Document this clearly.
- Default bridges *off*.
- Per-channel privacy guidance in setup wizard.
- Operators can choose privacy-aligned channels (Matrix, Signal)
  over leaky ones.

---

## Latency considerations

Channel bridges introduce:
- Network round-trip to channel API.
- Webhook delivery delay (channel→Ember).
- Response delivery delay (Ember→channel).
- LLM processing time.

Total latency for channel-bridged chat: typically 3-15 seconds
depending on channel + LLM + network.

This is *acceptable* for messaging context (users expect SMS-
like delays). Less acceptable for voice / live chat.

---

## Configuration shape

```yaml
ember:
  bridges:
    enabled: false                 # opt-in
    
    matrix:
      enabled: false
      homeserver: matrix.org
      user_id: "@ember-of-volmarr:matrix.org"
      device_id: ember_device_1
      access_token_ref: kista://matrix/access_token
      rooms:
        - "!work-room:matrix.org"
        - "!personal-room:matrix.org"
    
    telegram:
      enabled: false
      bot_token_ref: kista://telegram/bot_token
      authorized_user_ids: [123456789]
      polling_interval_s: 10
    
    signal:
      enabled: false
      data_dir: ~/.ember/signal/
```

Each bridge is independent. Operators enable what they want.

---

## What about UI-rendering channels

OpenClaw's Canvas works on macOS/iOS/Android — but not on
Telegram or WhatsApp. Bridges are *text-only* (mostly).

For Ember: text-only bridge by default. Canvas/widgets *only*
on richer surfaces (Stofa, Auga).

When agent emits Canvas markup that goes to a text-only bridge,
fall back to descriptive text: "I'd render a form here; can you
tell me X, Y, Z instead?"

---

## Risk: bridge security

Channel APIs are *complex*. Bridges interact with:
- OAuth flows (Slack, Discord).
- Bot tokens (Telegram).
- API keys (most channels).
- Per-message attachments (potential vectors).

Each bridge is *another attack surface*. We must:
- Audit each bridge carefully before promoting it.
- Sandbox bridge processes (per
  [`13_SANDBOX_BACKEND_ABSTRACTION.md`](13_SANDBOX_BACKEND_ABSTRACTION.md)).
- Limit credential exposure to Kista.
- Test failure modes (channel API down; rate-limited;
  malformed inputs).

---

## Closing

Multi-Channel Messaging is **OpenClaw's signature scaling
feature**. 23+ channels = mass-market reach.

Ember should:
- 🔴 Reject building all 23+ bridges (not feasible; not aligned).
- 🟢 Adapt: ship 2-3 high-value sovereign-aligned bridges in
  Phase 4+.
- 🔵 Borrow the bridge-adapter pattern (Gateway-routes-bridges).
- 🟡 Defer per-bridge polish until operator demand exists.

The Klóinn lesson: **bridges are powerful operator-meeting
tools**. We don't need 23; we need the right 3-5 for our cohort.
