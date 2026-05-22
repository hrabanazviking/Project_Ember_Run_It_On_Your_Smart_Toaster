# 49 — Companion App Pairing Design

How specifically to build Ember's web companion in V5+.
Concrete plan.

---

## The shape

A **Progressive Web App** (PWA) accessed from the operator's
phone or tablet browser, paired to the home Ember Gateway via
WebSocket.

No native mobile apps. No app-store submission. Sovereign-only
deployment via Tailscale.

---

## Architecture

```
Phone/tablet                       Home device
─────────────                      ────────────
Browser opens                      ┌──────────┐
mobile-ember.tailnet:8888 ──HTTPS─►│ Ember    │
                                   │ Gateway  │
WebSocket connection              │          │
  ←──────────────────────────────►│          │
                                   │          │
                                   └──────────┘
```

Phone browser hits Ember Gateway over tailnet (Tailscale).
HTTPS via Tailscale's WireGuard encryption. WebSocket for
real-time chat.

No port-forwarding. No public exposure. Tailnet is the
boundary.

---

## Components

### Backend (Ember Gateway extension)

- HTTP server (FastAPI or aiohttp).
- WebSocket endpoint.
- Pairing flow (QR + token).
- Auth via tokens.
- Serves static PWA assets (HTML/CSS/JS).

### Frontend (PWA)

- HTML/CSS/JS (minimal vanilla or simple framework).
- Chat UI.
- Service worker for offline-installability.
- Local IndexedDB for chat draft caching.
- WebSocket client.

---

## Pairing flow

```bash
# On home device:
ember companion start

Companion server listening on 0.0.0.0:8888
URL: http://laptop.tailnet:8888/
Pairing URL: http://laptop.tailnet:8888/pair

QR code:
█▀▀▀▀▀█ █  █ █▀▀▀▀▀█
... (large QR rendered in terminal) ...

Press Ctrl-C to stop server.
```

Operator opens phone browser:
1. Scans QR (or types URL).
2. Pairing page loads.
3. Pairing token entered (or QR contains it).
4. Server validates; issues session token.
5. Browser redirects to chat UI.
6. WebSocket connects; operator chats.

Subsequent visits: session token persisted in browser; auto-
reconnects.

---

## WebSocket message protocol

JSON messages over WebSocket:

### Client → Server

```json
{"type": "chat_input", "text": "Hello"}
{"type": "chat_cancel"}
{"type": "ping"}
```

### Server → Client

```json
{"type": "chat_token", "text": "Hi", "session_id": "..."}
{"type": "chat_done", "session_id": "..."}
{"type": "tool_proposed", "tool": "fetch_url", "args": {...}}
{"type": "pong"}
```

Streaming-friendly. Token-by-token chat.

---

## Auth model

Operators get a long-lived session token after pairing:

```json
{
  "session_token": "sk_eyJhbGciOi...",
  "expires_at": null,                 // never; revocable
  "device_name": "Volmarr's iPhone",
  "paired_at": "2026-05-22T14:30:00Z"
}
```

Tokens are:
- Stored in browser's localStorage.
- Sent in WebSocket handshake.
- Revocable from Ember CLI (`ember companion revoke <device>`).
- Auditable (every connection logged).

---

## Pairing security

The pairing flow has a 5-minute window:

1. `ember companion start` generates a pairing token.
2. Token displayed as QR.
3. Operator's phone scans within 5 min.
4. Pairing completes; phone gets long-lived session token.
5. Pairing token expires; can't be reused.

This prevents long-lived QR codes from being intercepted.

---

## What the operator sees on phone

```
┌──────────────────────────────────┐
│ Ember                             │
│  Connected to laptop.tailnet      │
│                                   │
│  ┌─ Session: 2026-05-22 ─────────┐│
│  │                                ││
│  │  > Volmarr: hi                 ││
│  │                                ││
│  │  Ember: Hello.                 ││
│  │                                ││
│  │                                ││
│  └────────────────────────────────┘│
│                                   │
│  [Type a message...]              │
│  [🎤] [📷] [Send]                  │
│                                   │
└──────────────────────────────────┘
```

Minimalist. Familiar chat UI. Optional mic/camera buttons if
those tools are configured + approved.

---

## Phone capabilities as tools

When operator gives browser permission, Ember can use:

### Camera
```
operator: "Take a photo of what's in front of me"
ember: [requests camera tool]
[browser shows permission prompt]
operator: allows
[photo captured; sent to Ember]
ember: [VLM processes; describes]
```

### Microphone
Voice input via Web Speech API or upload to Ember's STT.

### Location
If permitted by browser; available as tool.

### Files
Upload via standard file picker.

All require *operator approval per call* (browser-mediated +
Ember's tool approval).

---

## Live Canvas / OdinUI on web

Per [`42_LIVE_CANVAS_FOR_AUGA.md`](42_LIVE_CANVAS_FOR_AUGA.md):
the web companion renders OdinUI naturally (it's a browser).

Forms, lists, charts, buttons — all standard HTML.

This makes the web companion *richer* than Stofa TUI for some
interactions.

---

## Offline support

PWA installs as "Add to Home Screen" on phone:
- App-like icon.
- Standalone window (no browser chrome).
- Offline-capable (service worker caches assets).

When offline:
- Operator can view recent chat (cached).
- Cannot send new messages (Ember is offline).
- Auto-reconnects when online.

---

## Notification support

Limited:
- iOS: push notifications via PWA were unsupported for years;
  now allowed but limited. Operator must enable.
- Android: PWA notifications work better.

For Ember V5: skip push notifications initially. Operator polls
manually.

V6+ if needed: implement Web Push.

---

## Configuration shape

```yaml
ember:
  companion:
    enabled: false                 # opt-in
    
    server:
      bind: 0.0.0.0
      port: 8888
      static_assets_path: /var/lib/ember/companion-pwa
    
    auth:
      session_token_ttl_seconds: null    # no expiry
      pairing_token_ttl_seconds: 300     # 5 min
      max_paired_devices: 10
    
    features:
      voice: true
      camera: true
      odinui: true
    
    privacy:
      audit_all_messages: true
      record_device_info: true           # browser user-agent
```

---

## CLI commands for companion management

```bash
ember companion start                # starts server
ember companion stop                 # stops server
ember companion status               # shows paired devices + connections
ember companion list                 # lists paired devices
ember companion revoke <device>      # revoke a device's token
ember companion logs                 # show connection log
```

---

## What we ship in PWA

```
companion-pwa/
  index.html
  manifest.json
  service-worker.js
  css/
    style.css
  js/
    app.js              # main chat logic
    websocket.js         # connection management
    odinui.js            # OdinUI rendering
    audio.js             # voice input/output
  assets/
    ember-icon-192.png
    ember-icon-512.png
```

Minimal. No bundler. Plain HTML/CSS/JS. Easy for operators
to inspect.

---

## Tech stack choices

### Backend

- **FastAPI** for HTTP + WebSocket.
- Or aiohttp if we prefer fewer deps.

### Frontend

- Vanilla JS (no React/Vue/etc.).
- Pure HTML + CSS.
- Service worker.

This keeps the surface small + auditable. No build step.
Operators can read the JS.

---

## Performance considerations

PWA loads on first visit; cached after. Subsequent loads:
~100ms cold start.

WebSocket round-trip latency on tailnet: < 50ms.

Chat experience: similar to Stofa. Token-by-token streaming.

---

## Cross-device chat continuity

Operator chats in browser (phone), continues in Stofa (laptop).
Same Ember; sessions sync.

How:
- Sessions live on home device.
- Both surfaces reference session ID.
- Each surface is a *view* into the same conversation.

---

## What we don't do

🔴 **Reject**:

### 1. Native apps in V5

We commit to PWA. If/when native is needed: V6+.

### 2. Public internet exposure

Tailnet only. We never bind to public-internet IPs.

### 3. Cloud-mediated pairing

Pairing direct over tailnet. No "OpenClaw cloud helps you
pair." Sovereign.

### 4. App-store submission

PWAs install via "Add to Home Screen." No App Store. No
Google Play.

---

## Test strategy

- **Unit tests**: WebSocket handlers, auth, token management.
- **Integration tests**: PWA loads, pairs, chats end-to-end.
  Headless browser (Playwright?) drives the PWA.
- **Manual mobile testing**: operator tests on iPhone +
  Android.

---

## V5 ship plan

1. **Phase 5a**: HTTP server + WebSocket + basic auth + chat
   only. PWA renders simple chat.
2. **Phase 5b**: OdinUI rendering.
3. **Phase 5c**: Mic + camera tools.
4. **Phase 5d**: PWA installability + service worker.
5. **Phase 5e** (V6+): push notifications.

Each step is shippable; operators can use earlier steps before
later land.

---

## Closing

Companion App Pairing Design is **V5+ work, web-first**.
Tailnet-only, sovereign, PWA.

Operators get phone-Ember without app-store mediation.
Tailscale handles connectivity. Ember handles auth + chat +
canvas.

The Klóinn lesson translates: mobile is valuable; we get it
via PWA *without* the cost of native apps. Smaller team can
ship; operators get the value.

Plan now; build V5.
