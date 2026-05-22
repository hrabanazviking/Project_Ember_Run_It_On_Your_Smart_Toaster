# 71 — Adding Telegram Bridge

Concrete implementation guidance for the Telegram bridge.
Phase 4 work.

---

## Prerequisites

- Humarr Gateway (Phase 1-2).
- Daemon mode (Phase 4 early).
- Sandbox layer (Phase 3+).
- Kista for secrets.

---

## Step 1: dependency add

```bash
pip install ember-agent[bridge-telegram]
```

```toml
[project.optional-dependencies]
bridge-telegram = [
    "python-telegram-bot>=21.0",
]
```

---

## Step 2: setup wizard

```bash
ember bridge install telegram

[1/5] Create a bot:
   1. Open Telegram, message @BotFather
   2. Send /newbot
   3. Follow prompts; copy the bot token
   
   Paste bot token:
   > 1234567890:ABCdefGhIJklMnoPQrsTUVwxyz
   
[2/5] Identify yourself:
   Message your bot first (/start in Telegram).
   Then find your user ID via:
     @userinfobot on Telegram
   
   Your Telegram user ID:
   > 987654321
   
[3/5] Persona for this bridge:
   ▶ main
     personal
     (other personas)
   > personal
   
[4/5] Sandbox policy:
   ▶ standard (read_local_file forbidden; fetch_url allowed)
     strict (no tools)
     permissive (all tools available)
   > standard
   
[5/5] Privacy acknowledgment:
   Telegram messages traverse Telegram servers. Telegram
   sees: your messages, the bot's replies, metadata.
   
   For end-to-end privacy, consider Matrix bridge instead.
   
   Acknowledge? [y/n]: y

Bridge configured.

To enable: ember bridge enable telegram
```

---

## Step 3: implement bridge

`src/ember/bridges/telegram/__init__.py`:

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

class TelegramBridge:
    NAME = "bridge.telegram"
    
    def __init__(self, config: TelegramBridgeConfig, gateway: HumarrGateway):
        self.config = config
        self.gateway = gateway
        self.app = None
    
    async def start(self):
        token = await self.gateway.kista.resolve(self.config.bot_token_ref)
        
        self.app = Application.builder().token(token).build()
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text)
        )
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def _handle_text(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.config.authorized_user_ids:
            await update.message.reply_text(
                "Sorry, this bot is private."
            )
            return
        
        # Route to gateway with bridge metadata
        event = GatewayEvent(
            source=self.NAME,
            session_id=f"telegram:{update.effective_user.id}",
            persona=self.config.persona,
            sandbox=self.config.sandbox,
            text=update.message.text,
            metadata={
                "telegram_user_id": update.effective_user.id,
                "telegram_username": update.effective_user.username,
                "chat_id": update.effective_chat.id,
            },
        )
        
        response = await self.gateway.handle_event(event)
        
        # Send reply back to Telegram
        await update.message.reply_text(response.text)
    
    async def stop(self):
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
    
    async def health(self) -> SurfaceHealth:
        # Check bot info; verify token still valid
        ...
```

---

## Step 4: per-bridge sandbox policy

In Humarr Gateway:

```python
async def handle_event(self, event: GatewayEvent):
    # Sandbox enforcement per bridge
    sandbox_config = self._compute_sandbox(event)
    
    # Tools subject to bridge-specific overrides
    available_tools = self._filter_tools_for_sandbox(sandbox_config)
    
    # Process turn with restricted tool set
    ...
```

So when Telegram operator's chat triggers tool call,
`read_local_file` is forbidden (per default Telegram sandbox).

---

## Step 5: rate limiting

```python
class TelegramBridge:
    RATE_LIMIT_MESSAGES_PER_MINUTE = 30
    
    def __init__(self, ...):
        self._rate_limiter = RateLimiter(
            self.RATE_LIMIT_MESSAGES_PER_MINUTE,
            per_window_seconds=60,
        )
    
    async def _handle_text(self, update, ctx):
        if not self._rate_limiter.allow(update.effective_user.id):
            await update.message.reply_text(
                "Rate-limited. Please wait a moment."
            )
            return
        # ... process ...
```

Prevents flood from spamming the bot.

---

## Step 6: audit log

Every Telegram chat-turn logged:

```python
{
    "source": "bridge.telegram",
    "telegram_user_id": 987654321,
    "telegram_chat_id": 987654321,
    "persona": "personal",
    "sandbox_active": "standard",
    "operation": "chat_turn",
    "tokens_in": 23,
    "tokens_out": 156,
}
```

---

## Step 7: tests

```python
# tests/integration/test_telegram_bridge.py

@pytest.mark.requires_telegram_test_bot
async def test_telegram_bridge_authorized_user_message():
    bridge = await start_test_bridge()
    
    # Simulate incoming message from authorized user
    update = make_test_update(user_id=987654321, text="hello")
    await bridge._handle_text(update, None)
    
    # Verify gateway received event
    assert gateway.received_events
    event = gateway.received_events[0]
    assert event.source == "bridge.telegram"
    assert event.text == "hello"

@pytest.mark.requires_telegram_test_bot
async def test_telegram_bridge_rejects_unauthorized():
    bridge = await start_test_bridge()
    
    update = make_test_update(user_id=111111, text="hi")
    await bridge._handle_text(update, None)
    
    # Should NOT route to gateway
    assert not gateway.received_events
```

---

## Step 8: configuration

```yaml
ember:
  bridges:
    telegram:
      enabled: false
      bot_token_ref: kista://telegram/bot_token
      authorized_user_ids: [987654321]
      
      polling:
        mode: long_polling          # or "webhook"
        timeout_s: 30
      
      persona: personal
      
      sandbox:
        default: standard
        tool_overrides:
          read_local_file: forbidden
          fetch_url: allowed
      
      rate_limit:
        messages_per_minute: 30
      
      audit:
        log_every_message: true
        privacy_notice_shown: true
```

---

## Step 9: documentation

`docs/bridges/telegram.md`:
- Setup walkthrough.
- Authorization model (who can message).
- Privacy implications.
- Tool sandbox defaults.
- Troubleshooting.
- Removal (uninstall).

---

## Step 10: rollout

V4 release notes:

```
V4 ships Telegram bridge (opt-in).

To enable:
  pip install ember-agent[bridge-telegram]
  ember bridge install telegram
  ember bridge enable telegram

Privacy: Telegram messages traverse Telegram servers.
For end-to-end private, consider Matrix bridge.
```

---

## What we don't do

🔴 **Reject**:

### 1. Telegram channels (broadcast lists)

Operators don't broadcast via Ember.

### 2. Group chats with bot as participant

Initial implementation: only DM (direct message) supported.
Groups complicate sandboxing + privacy.

### 3. Telegram-specific tools

The bridge is for *chatting through Telegram*. Not for
Telegram-specific actions (post photo to channel, etc.).
Operators wanting those: native Telegram clients.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Bot token leak | Stored in Kista (encrypted) |
| Unauthorized users find bot | authorized_user_ids check |
| Bot used to leak operator data | Sandbox + audit |
| Telegram API change | Pin library version |

---

## Closing

Adding Telegram Bridge is **Phase 4 work**. Maps to the
existing Klóinn pattern of bridges-as-surfaces. Implementation
~600 lines including tests.

Critical: ship with Matrix bridge as a *peer* in the same
release. Both demonstrate the bridge pattern; operators can
choose based on privacy comfort.

Operators get phone-Ember via Telegram (less private,
mainstream) or Matrix (more private, federated). Both fit the
Klóinn pattern.
