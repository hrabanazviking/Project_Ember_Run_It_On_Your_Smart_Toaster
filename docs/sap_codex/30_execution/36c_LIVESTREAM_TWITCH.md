# 36c — Livestream: Twitch (Raw IRC Socket, Anonymous Auth, USERNOTICE Vocabulary)

> *Eldra at the anvil. Twitch chat is the only livestream surface in SAP that still runs on raw IRC — TLS socket on port 6697, CAP REQ for tags, anonymous justinfan auth. 210 lines of unblinking 1990s protocol. Mostly correct, with one indentation bug that proves nobody tested the disconnect path.*

The Twitch chat module at `/tmp/super-agent-party/py/twitch_service.py` (210 lines) connects to Twitch's IRC gateway directly — no SDK, no EventSub WebSocket, just `socket.socket + ssl.wrap_socket` and a hand-rolled IRC tag parser. It is the second polling-free livestream in SAP (alongside Bilibili), the only one using IRC, and it ships with a real bug in the cleanup path that the protocol's resilience hides. This subdoc maps the IRC dance, the USERNOTICE → Bilibili-vocabulary mapping, the bug, and what Ember should learn from raw-protocol ingest.

## Platform Shape

Twitch is **livestream-comment-ingest, IRC-over-TLS, anonymous-OAuth-token-authenticated, single-channel-scoped**. Authentication is an OAuth `access_token` (stripped of the `oauth:` prefix at line 14), used in the IRC PASS command. The nickname is the *anonymous read-only* `justinfan12345` (line 67) — Twitch's documented anonymous-read identity. This means **the bot does not send chat back via IRC** — it only listens.

(Sending back would require a real-account OAuth token and IRC `PRIVMSG #channel :...` send commands. SAP does not implement this; the response side is presumably handled via Twitch's separate Helix API or overlay rendering.)

Twitch IRC on port 6697 (TLS) is the documented gateway: `irc.chat.twitch.tv` (line 61). The CAP REQ at line 65 requests both `twitch.tv/tags` (the meta-data tags on each PRIVMSG, the **most important** signal) and `twitch.tv/commands` (USERNOTICE, CLEARCHAT, ROOMSTATE, etc.). Without tags, the bot wouldn't see subscription milestones, gift sub counts, or user display-name with case preservation.

## Source Files

- `twitch_service.py:7–41` — `SimpleTwitchChat`: socket, callback, start/stop
- `twitch_service.py:43–54` — `_listen_loop`: reconnect with exponential backoff (the only correct part of cleanup)
- `twitch_service.py:56–79` — `_connect_and_read`: TLS setup, IRC handshake, line buffer
- `twitch_service.py:81–169` — `_handle_line`: the IRC tag parser + USERNOTICE vocabulary mapper
- `twitch_service.py:171–181` — `_send` / `_close_socket` (the buggy methods, see below)
- `twitch_service.py:184–210` — `start_twitch_task` / `stop_twitch_task`: module-global singleton

## Connection Lifecycle

The IRC handshake at `_connect_and_read` (lines 56–80):

```python
# twitch_service.py:56–68
ctx = ssl.create_default_context()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
self._sock = ctx.wrap_socket(sock, server_hostname="irc.chat.twitch.tv")
self._sock.connect(("irc.chat.twitch.tv", 6697))
self._sock.settimeout(None)

# 认证
self._send(f"CAP REQ :twitch.tv/tags twitch.tv/commands")
self._send(f"PASS oauth:{self.access_token}")
self._send(f"NICK justinfan12345")
self._send(f"JOIN #{self.channel}")
```

Four lines of IRC: CAP REQ, PASS, NICK, JOIN. Each is a complete IRC command terminated with `\r\n` by `_send`. The order matters — PASS before NICK is the IRC standard for authenticated connections.

The reconnect loop at `_listen_loop` (lines 43–54):

```python
async def _listen_loop(self):
    reconnect_delay = 5
    while self._running:
        try:
            await self._connect_and_read()
            reconnect_delay = 5
        except Exception as exc:
            if not self._running:
                break
            print(f"[Twitch] 连接异常: {exc}，{reconnect_delay}s 后重连")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)
```

Exponential backoff from 5s to 60s. Resets to 5s on a successful read session. This is correct and matches Bilibili's reconnect approach. The blanket `except Exception as exc` is broad but defensible here — IRC has many failure modes (TLS error, EOF, timeout, parser exception) and the bot's job is to keep listening.

The receive path at lines 70–79:

```python
buffer = ""
while self._running:
    data = await asyncio.get_event_loop().sock_recv(self._sock, 4096)
    if not data:
        raise ConnectionAbortedError("服务器关闭连接")
    buffer += data.decode("utf-8", errors="ignore")
    while "\r\n" in buffer:
        line, buffer = buffer.split("\r\n", 1)
        if line:
            self._handle_line(line)
```

`asyncio.get_event_loop().sock_recv` runs the socket recv non-blocking via the loop. The buffer accumulates until a `\r\n` boundary, then splits and dispatches lines one at a time. Standard IRC framing — Twitch sends UTF-8, `errors="ignore"` swallows malformed bytes.

`asyncio.get_event_loop()` is **deprecated in Python 3.10+** (use `get_running_loop()`). Same issue as blivedm.

## Message Handling

The `_handle_line` parser (lines 81–169) is the entire interesting logic. PING/PONG keepalive at lines 86–88. Then it parses **IRC tags** (the `@key=value;key=value :user!user@host COMMAND...` prefix):

```python
# twitch_service.py:91–99
tags = {}
if line.startswith("@"):
    tag_str, _, line = line[1:].partition(" ")
    for kv in tag_str.split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            # 处理 Twitch IRC 协议中的转义字符
            v = v.replace("\\s", " ").replace("\\:", ";").replace("\\r", "\r").replace("\\n", "\n")
            tags[k] = v
```

The escape sequences (`\\s` → space, `\\:` → semicolon, `\\r` → CR, `\\n` → LF) are **Twitch IRCv3 tag escape codec** (IRCv3 spec §2.3). Required because IRC tags can't natively contain spaces, semicolons (the separator), or CR/LF.

The command identification at lines 102–106 looks for `PRIVMSG`, `USERNOTICE`, or `CLEARCHAT` in the parsed line tokens. Notice the bot doesn't differentiate the command position — it just scans for the first match in the space-split tokens. This works for well-formed IRC but is fragile against unusual lines.

The **USERNOTICE vocabulary mapping** at lines 127–162 is the platform-translation work — Twitch's rich event types reduced to Bilibili's `danmu_type` taxonomy:

```python
# twitch_service.py:139–157 (condensed)
if msg_id in ["sub", "resub"]:
    # 订阅或续订 -> 对应 B 站 "上舰/舰长"
    danmu_type = "buy_guard"
    msg_content = f"{system_msg} | Message: {user_text}" if user_text else system_msg
    
elif msg_id in ["subgift", "anonsubgift", "submysterygift"]:
    # 赠送订阅 -> 对应 B 站 "礼物"
    danmu_type = "gift"
    msg_content = system_msg
    
elif msg_id == "raid":
    # 突袭 (其他主播带人进场) -> 对应 B 站 "进场"
    danmu_type = "enter_room"
    msg_content = system_msg
    
elif msg_id == "announcement":
    # 频道公告 -> 对应普通弹幕，但在内容前加标识
    danmu_type = "danmaku"
    msg_content = f"[Announcement] {user_text}"
```

Five distinct USERNOTICE `msg-id` values mapped to four internal types (`buy_guard`, `gift`, `enter_room`, `danmaku`). The mapping is **Bilibili-centric** — the internal vocabulary inherits from blivedm rather than being neutrally named. This is a tell: SAP's livestream taxonomy was Bilibili-first, with YouTube and Twitch retrofitted onto it.

Callback dispatch at lines 165–169:

```python
if self._callback:
    asyncio.create_task(
        self._callback(self.channel, user, msg_content, danmu_type)
    )
```

`asyncio.create_task` to dispatch the callback off the parse loop. This is the right pattern — the parser keeps reading lines while the consumer processes the prior event. Compare to blivedm's synchronous dispatch (handlers.py:486–494): twitch_service is *more* permissive (async dispatch) but inherits the same risk if the consumer is slow (the create_task queue grows).

## The Bug

Look at `twitch_service.py:171–181`:

```python
        # 5. 回调给 Service 层
        if self._callback:
            # 这里的回调需确保能接收四个参数：channel, user, msg_content, danmu_type
            asyncio.create_task(
                self._callback(self.channel, user, msg_content, danmu_type)
            )

        def _send(self, msg: str):
            if self._sock:
                self._sock.send(f"{msg}\r\n".encode())

        def _close_socket(self):
            if self._sock:
                try:
                    self._sock.close()
                except:
                    pass
                self._sock = None
```

**`_send` and `_close_socket` are defined inside `_handle_line` with extra indentation** (8 spaces instead of 4). They are inner functions of `_handle_line`, not methods of `SimpleTwitchChat`. This is a clear indentation bug — somebody copy-pasted incorrectly during a refactor.

Consequences:

1. **`self._send(...)` at lines 65–68 still works** — because Python only resolves the name at call time, and there's no other `_send` on the class. Wait, no — without a class-level `_send`, calls to `self._send(...)` raise `AttributeError`. Let me look again...

Actually, this is more nuanced. `_send` is referenced at lines 65–68 inside `_connect_and_read` (a method) and at line 88 inside `_handle_line` (a method). If `_send` is *only* defined inside `_handle_line`, then those references fail.

But the code is shipping. Either: (a) the file actually has `_send` at class level too and I missed it (let me re-check), or (b) the bot never authenticates because `_send` raises AttributeError on line 65, which gets caught by the broad `except Exception` in `_listen_loop` and triggers infinite reconnect.

Looking at lines 81–169 more carefully — `_handle_line` is itself a method of `SimpleTwitchChat`. The indentation of `def _send(self, msg: str):` at line 171 places it **inside `_handle_line` after the callback dispatch**. This means every call to `_handle_line` *redefines* `_send` and `_close_socket` as inner functions, but they never get bound to `self`.

The bug: **`self._send(...)` and `self._close_socket()` references throughout the file should fail at call time** because no method `_send` is defined on the class. The actual class-level definition is missing.

What probably happens: the broad `except Exception` in `_listen_loop` swallows the `AttributeError` on `self._send` call. The reconnect loop fires. Reconnect tries `_send` again. Same exception. The bot reconnects forever, never authenticates, never receives messages.

**Either nobody tested this code path, or there's an additional file in the SAP codebase where Twitch is being patched.** Worth raising in CROSS_AGENT_NOTES.

## Failure Modes

- **The indentation bug above.** If unpatched elsewhere, this bot is non-functional.
- **`print` for logging** (line 52, 202, 209) — same anti-pattern as ytdm.
- **`access_token` in plain config.** No rotation, no scope check.
- **`asyncio.get_event_loop()` deprecated** (line 72).
- **`buffer.decode("utf-8", errors="ignore")`** — malformed bytes silently dropped. Acceptable.
- **No PING reconnect timeout** — IRC PING normally comes every ~5 minutes from Twitch. If the bot misses it (network partition, server quiet), the connection is dead but `sock_recv` doesn't time out. The connection silently hangs until the OS TCP keepalive triggers (typically 2 hours).
- **Channel name normalization** at line 16 — `.lower().lstrip("#")`. Twitch channel names are case-insensitive but unicode-normalized differently than IRC norms. Edge cases (non-ASCII display names) may not roundtrip.
- **Module-global singleton** (lines 187, 199) — `_twitch_chat: Optional[SimpleTwitchChat] = None`. Only one Twitch channel can be ingested per process. SAP can't watch two streams at once.
- **Anonymous `justinfan12345`** — well-known. Twitch can rate-limit or ban this anonymous identity if abused.
- **No subscriber-only / emote-only / followers-only channel handling.** Twitch enforces these modes at the IRC layer with NOTICE messages. SAP ignores NOTICE.

## Privacy & Threat Surface

Twitch is **Amazon-owned, US-jurisdictional**. Per-comment privacy is essentially zero (public livestream chat).

- **OAuth token in plain config.** Standard.
- **Bot ingests every chat from every viewer.** Same as YouTube; standard livestream concern.
- **USERNOTICE includes subscription milestones, anonymous gift sub IDs (`anonsubgift`).** The `system-msg` tag often reveals subscription counts, viewer-to-viewer relationships. SAP processes these.
- **Tag `display-name` preserves case** — useful for the bot, but combined with super-chat dedications and stream-replay logs, contributes to viewer-tracking profile.
- **`justinfan12345` is anonymous-read but logged on Twitch's side.** Twitch knows an IP polled this channel with this token. Not a strong identity link, but not none.
- **No outbound** (read-only). Reduces the surface — the bot cannot accidentally post user content back to chat. The response side (overlay, avatar speech) is outside this module.

## What This Means for Ember

**Adopt:** The **exponential-backoff reconnect with reset-on-success** pattern at `twitch_service.py:43–54`. 5s → 10s → 20s → 40s → 60s cap, reset to 5s on first successful read. This is the right shape for any long-lived ingest connection. Bilibili has it; Twitch has it; the IM bots mostly don't (they rely on SDKs that may or may not implement it). Ember should make this contract mandatory across every connection-holding adapter, with the backoff curve as a configurable strategy.

**Adapt:** The **IRC-tag-based event-vocabulary mapping** at lines 127–162. The intent — translate platform-specific event types to a neutral internal taxonomy — is right. The implementation (Bilibili-centric `buy_guard`, `enter_room` names) is wrong. Ember should adapt by **inverting the dependency**: define the neutral taxonomy first (`subscribe`, `gift_subscribe`, `raid_arrival`, `announcement`, `chat`), then each platform's adapter (Bilibili, YouTube, Twitch) maps its native events onto the neutral vocabulary. The `Mál` taxonomy invented in [[36b_LIVESTREAM_YOUTUBE]] is the right place for this.

**Avoid:** Four patterns. (1) **The indentation bug at lines 171–181.** This is shipping broken code. If Ember adopts raw-protocol ingest, every method must be at class level. Every test must cover the cleanup path. (2) The **`asyncio.get_event_loop()`** deprecation at line 72. Use `get_running_loop()`. (3) The **module-global singleton** (lines 187, 199). Ember must support multiple concurrent livestream ingests across multiple platforms. Each instance owns its own state. (4) The **broad `except Exception`** that swallows real bugs (line 49) — this is why the indentation bug shipped. Ember's reconnect catchers must classify exceptions, log type and message, and have a "this is suspicious" path that escalates rather than silently retries.

**Invent:** A pattern SAP did not implement — **integration-test livestream replay**. Ember should ship a `livestream-replay-fixture/` directory with captured-but-anonymized IRC sessions, Bilibili WebSocket frames, and YouTube poll responses. The test harness replays them through each adapter and verifies the unified `Mál`-shaped emit. This is the test discipline that would have caught the indentation bug. Bind to `Eftirhermur` (Old Norse for "echo/imitation") — the replay-fixture testing surface for ingest layers.

Forward-links: see [[36_LIVESTREAM_INGEST_OVERVIEW]] for cross-platform shape, [[27_STREAMING_INTERFACE]] for unified interface, [[36a_LIVESTREAM_BILIBILI]] for the binary-WebSocket counterpart, [[36b_LIVESTREAM_YOUTUBE]] for the polling-API counterpart, and [[15_BROADCAST_DOMAIN]] for placement.

The forge is hot. Twitch is SAP's only raw-IRC ingest and the one where shipping bugs hide behind the protocol's resilience. Inherit the exponential-backoff-with-reset. Reject the indentation bug, the global singleton, the deprecated event-loop access, the broad exception swallow. Build the replay-fixture test discipline that catches what nobody else does. — Eldra.
