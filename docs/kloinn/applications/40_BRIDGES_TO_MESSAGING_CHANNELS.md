# 40 — Bridges to Messaging Channels

How specifically Ember should add 2-3 messaging channel bridges
in Phase 4. Concrete implementation guidance.

---

## What we're building

Two bridge sibling projects in Phase 4:

1. **`bifrost-bridge-matrix`** — Matrix protocol bridge.
2. **`bifrost-bridge-telegram`** — Telegram Bot API bridge.

Each is its own pip package, opt-in, sibling-shaped.

(The `bifrost-` prefix puts these under the Bifrǫst sibling
namespace since Bifrǫst is already the cross-realm gateway.)

---

## Architectural shape

```
                ┌──────────────────────┐
                │   Ember Gateway       │
                │ (per Klóinn pattern)  │
                └──────────┬────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         ┌─────────┐ ┌─────────┐ ┌─────────┐
         │ Munnr    │ │ Stofa    │ │ Bridges  │
         │ (CLI)    │ │ (TUI)    │ │ Plugin   │
         └─────────┘ └─────────┘ └────┬─────┘
                                       │
                          ┌────────────┴────────────┐
                          │                          │
                          ▼                          ▼
                 ┌────────────────┐         ┌────────────────┐
                 │ matrix-bridge   │         │ telegram-bridge│
                 │ adapter         │         │ adapter        │
                 └────────┬───────┘         └────────┬───────┘
                          │                          │
                          ▼                          ▼
                 ┌────────────────┐         ┌────────────────┐
                 │ Matrix Olm/    │         │ Telegram Bot   │
                 │ Megolm session │         │ API client     │
                 └────────────────┘         └────────────────┘
```

Bridges are surfaces; they plug into the Gateway like any
other surface. The Gateway abstracts which surface a turn
came from.

---

## Common bridge contract

All bridges implement a `BridgeSurface` Protocol:

```python
class BridgeSurface(Protocol):
    NAME: ClassVar[str]
    
    async def start(self, gateway: Gateway) -> None:
        """Connect to channel; start receiving events."""
        ...
    
    async def stop(self) -> None:
        """Disconnect; clean up."""
        ...
    
    async def health(self) -> SurfaceHealth:
        """Is the bridge connected and ready?"""
        ...
```

Implementations connect to their channel, normalize incoming
events into Ember chat-turn shape, push to Gateway. Gateway
processes; sends reply; bridge formats for channel; delivers.

---

## Matrix bridge specifics

### Library choice

Use **matrix-nio** (Python Matrix SDK).

```python
from nio import AsyncClient, MatrixRoom, RoomMessageText
```

Mature; sovereignty-compatible; supports Olm/Megolm E2EE.

### Setup flow

```bash
ember bridge install matrix
> Homeserver URL: https://matrix.org
> Username: @ember:matrix.org
> Password: ████████ (stored encrypted in Kista)
> Initial sync ...
> 
> Rooms to monitor:
>   [ ] #general:matrix.org
>   [x] !private-room-id:matrix.org
> 
> E2EE enabled? [y/n]: y
> 
> Configured. Run: ember bridge enable matrix
```

### Message flow

1. Matrix message arrives in monitored room.
2. matrix-bridge receives via long-poll / sync.
3. Decrypts (E2EE).
4. Normalizes to Ember chat-turn shape.
5. Pushes to Gateway.
6. Gateway processes; generates reply.
7. matrix-bridge encrypts reply.
8. Sends to room.

Latency budget: ~2-10 seconds end-to-end.

### Per-room routing

Operator can configure per-room persona/sandbox:

```yaml
bridges:
  matrix:
    rooms:
      "!general:matrix.org":
        persona: main
        sandbox: standard
      "!private:matrix.org":
        persona: personal
        sandbox: relaxed
```

---

## Telegram bridge specifics

### Library choice

Use **python-telegram-bot**.

```python
from telegram import Update
from telegram.ext import Application, MessageHandler
```

Maintained; well-documented; covers Bot API thoroughly.

### Setup flow

```bash
ember bridge install telegram
> Create a bot via @BotFather; paste token:
> Bot token: ████████ (stored in Kista)
> 
> Your Telegram user ID (use /start to bot first; check
> the user_id):
> Authorized user ID: 123456789
> 
> Polling mode? (long_polling / webhook)
> Mode: long_polling
> 
> Configured. Run: ember bridge enable telegram
```

### Message flow

1. Telegram user sends message to bot.
2. Bot library long-polls Telegram servers.
3. Bot receives `Update` object.
4. Bridge validates user_id is authorized.
5. Bridge normalizes to chat-turn shape.
6. Pushes to Gateway.
7. Gateway processes; generates reply.
8. Bridge sends reply via Bot API.

### Authorization

Bot tokens are sensitive. *Only* authorized user_ids can
trigger the bridge. This prevents random people from finding
the bot and using it.

```python
async def handle_message(update: Update, context):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text(
            "Sorry, this bot is private."
        )
        return
    # ... process ...
```

---

## Audit trail per channel

Every bridge call lands in the audit log with channel context:

```json
{
  "timestamp": "2026-05-22T14:32:18Z",
  "source": "bridge.telegram",
  "user_id": "123456789",
  "operation": "chat_turn",
  "tokens_in": 23,
  "tokens_out": 156,
  ...
}
```

Per-channel filters: `ember audit list --source=bridge.telegram`.

---

## Sandboxing per bridge

Per [`../patterns/13_SANDBOX_BACKEND_ABSTRACTION.md`](../patterns/13_SANDBOX_BACKEND_ABSTRACTION.md)
and Yggdrasil:

By default, bridged sessions have stricter sandbox:
- `read_local_file` is denied (operator's files shouldn't be
  exposed via Telegram).
- `fetch_url` allowed with rate-limit.
- `search_well` allowed (this is read-only safe).

Operator can override per-bridge if they want.

---

## Privacy notice in setup

Bridges introduce trust:

```
WARNING: Telegram messages traverse Telegram servers.
Telegram (the company) sees:
  - Operator's identity (user ID, phone number).
  - Message contents (unless Secret Chats, which bots can't use).
  - Bot's responses.

For end-to-end private channels, use Matrix with E2EE.

Telegram is convenient but not privacy-maximal. Proceed? [y/n]
```

Operators must explicitly acknowledge during setup.

---

## Rate limiting

Each bridge has rate limits per channel:
- Matrix: ~5 messages/second (servers enforce).
- Telegram: 30 messages/second (bot API limit).

Bridges enforce *softer* limits to be polite:
- Matrix: 1 message/second/room.
- Telegram: 5 messages/second/user.

Avoids accidental floods.

---

## Disconnect / reconnect

Network blips happen. Bridges handle:

```python
async def maintain_connection(self):
    while not self.shutdown_requested:
        try:
            await self.connect()
            await self.run()
        except ConnectionError:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
```

Exponential backoff up to 60s. Reconnects don't lose
configured state.

---

## Cross-bridge sessions

If operator chats via Matrix, switches to Telegram — should
sessions follow?

Operator-configurable:
- `cross_bridge_session_continuity: shared` — all bridges
  share one ongoing session.
- `cross_bridge_session_continuity: per_bridge` — each bridge
  has its own session.

Default: `per_bridge` (privacy-safer: Telegram chats don't
appear in Matrix bridge log).

---

## Federation interaction

With Yggdrasil Phase 4 federation: bridges live on the
federation's *gateway node*. Other nodes don't need their own
bridges; they route via the gateway.

Reduces duplication; simplifies operator setup.

---

## Configuration shape

```yaml
ember:
  bridges:
    enabled: false  # global opt-in
    
    matrix:
      enabled: false
      homeserver: https://matrix.org
      user_id: "@ember:matrix.org"
      access_token_ref: kista://matrix/access_token
      device_id: ember-1
      e2ee: true
      rooms:
        "!private-id:matrix.org":
          persona: main
          sandbox_overrides:
            read_local_file: forbidden
    
    telegram:
      enabled: false
      bot_token_ref: kista://telegram/bot_token
      authorized_user_ids: [123456789]
      polling_mode: long_polling
      sandbox_overrides:
        read_local_file: forbidden
    
    common:
      cross_bridge_session_continuity: per_bridge
      audit_all_messages: true
      privacy_acknowledgment_required: true
```

---

## CI testing for bridges

Each bridge has:
- **Unit tests**: bridge logic with mocked channel client.
- **Integration tests**: bridge against a test homeserver
  (synapse test instance) or a sandbox bot.
- **End-to-end test**: operator chat round-trip.

Bridge tests are *expensive* (require external services or
test infrastructure). Gated by `@pytest.mark.bridge_integration`.

---

## Operator setup checklist

```
Phase 4 release notes:
  ✓ Bridges supported: Matrix, Telegram.
  
  To enable Matrix:
    1. pip install ember-agent[bridge-matrix]
    2. ember bridge install matrix
    3. ember bridge enable matrix
  
  To enable Telegram:
    1. Create a bot via @BotFather on Telegram.
    2. pip install ember-agent[bridge-telegram]
    3. ember bridge install telegram
    4. ember bridge enable telegram
  
  Operator: review privacy implications during setup.
  Operator: configure persona / sandbox per bridge.
```

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Bridge process crashes | Auto-restart with exponential backoff |
| Channel API change | Pin library versions; bump in releases |
| Operator-credential leak | Store tokens in Kista (encrypted) |
| Floods from malicious channel users | Rate-limit + sandbox + audit |
| Cross-channel data leakage | per_bridge session default |

---

## Closing

Bridges to Messaging Channels are **Phase 4 work — concrete
sibling projects, opt-in pip extras, sandboxed by default**.

Matrix + Telegram cover the high-value sovereignty-aligned
channels. Matrix's own bridge ecosystem transitively covers
more.

Setup is operator-driven; auth via Kista; per-channel sandbox;
audit log captures everything.

This is the *Klóinn-informed minimal version* of OpenClaw's
mass-channel bridging — adapted to Ember's Vows.
