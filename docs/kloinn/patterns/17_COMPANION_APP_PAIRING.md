# 17 — Companion App Pairing

OpenClaw's iOS/Android companion apps + WebSocket device pairing.
What it provides; how it works; whether Ember needs it.

---

## The pattern

OpenClaw runs a Gateway on a "host" device (typically laptop).
iOS/Android companion apps **pair** with the host via WebSocket.

Once paired:
- Mobile app shows the chat UI.
- Mobile app exposes phone capabilities (camera, screen capture,
  Android commands) as **tools** the agent can invoke (with
  approval).
- Mobile app surfaces Canvas elements (Live Canvas works on
  mobile).

So the operator's phone becomes both a surface (chat UI) and a
device-with-capabilities (camera, location, screen capture).

---

## How pairing works

1. Operator opens companion app on phone.
2. App shows a QR code or pairing token.
3. Operator scans QR with host device OR enters token.
4. Host validates; pairing key exchanged.
5. WebSocket connection established.
6. App + Gateway can communicate.

Subsequent app launches reconnect automatically.

---

## What this enables

### 1. Phone as input surface

Operator's away from desk; chats with Ember via phone. Same
chat, same session, same memory.

### 2. Phone as sensor

Agent asks: "Take a photo of what you're seeing." Operator
captures via app. Agent processes (with VLM if available).

### 3. Phone as canvas

Agent emits Live Canvas; phone renders interactively. Operator
fills forms, taps buttons.

### 4. Pi-as-surface, phone-as-display

Pi-class Ember + phone-as-companion = always-on AI without ever
opening a laptop.

---

## Cross-device coordination

Pairing connects *one phone to one host*. For multi-device:

- Multiple phones can pair with one host (operator's iPad +
  iPhone + spouse's phone, etc.).
- Each phone might route to different agents (multi-agent
  shape, per
  [`11_MULTI_AGENT_WORKSPACES.md`](11_MULTI_AGENT_WORKSPACES.md)).
- Phones DON'T pair with each other; they pair with the host.

Yggdrasil's federation (per
[`../../yggdrasil/cross-platform/65_DISTRIBUTED_COORDINATION.md`](../../yggdrasil/cross-platform/65_DISTRIBUTED_COORDINATION.md))
is a *peer-to-peer* model; pairing is *star topology* (all
spokes connect to one hub).

Both are valid; different needs.

---

## What Ember can adopt

🟡 **Defer to V5+**.

Ember has zero mobile presence today. Building companion apps
is *significant* engineering:

- Native iOS app (Swift / SwiftUI).
- Native Android app (Kotlin / Jetpack Compose).
- WebSocket protocol design.
- Cross-platform encryption + auth.
- App-store submission (Apple, Google).

This is a *multi-quarter* investment. Far beyond what current
Ember can support.

But the *pattern* is valuable to plan for V5+.

---

## Lighter alternative: web companion

Instead of native apps, **a Progressive Web App** (PWA) accessed
via mobile browser:

- Browser tab on phone → shows chat UI.
- Authenticated via QR / token from host.
- WebSocket to host.
- No app store; no native build.

Pros: much lighter to build; cross-platform; sovereign (no
app-store mediation).
Cons: less polished; no native push notifications; weaker
device API access.

For Ember V4 or V5, this is the *much more realistic* path.

---

## What's needed for a web companion

Components:

1. **Host-side**: Gateway exposes a WebSocket endpoint
   (operator-authenticated).
2. **Web UI**: minimal HTML/CSS/JS chat interface (could share
   code with Stofa via web-renderable components).
3. **Pairing**: QR + token exchange in browser.
4. **Auth**: token-based session.

Reachable from the operator's phone browser (on the tailnet).

---

## Configuration shape

```yaml
ember:
  companion:
    enabled: false              # opt-in
    
    web:
      bind_address: 0.0.0.0     # tailnet interface
      port: 8888
      tls: false                # tailnet is encrypted
      tls_cert: ""              # if exposed outside tailnet
      auth_required: true
      pairing_token_ttl_minutes: 5
    
    native_apps:
      ios: false                # not implemented
      android: false            # not implemented
```

---

## Why pair instead of mobile-only

A purist might ask: "Why not run Ember *on the phone* directly?"

Reasons:
- **Battery**: Phone running an LLM drains battery fast.
- **Performance**: 3B+ models tax mobile GPUs.
- **Cost**: Better to have one good Ember host + thin clients.
- **Sovereignty**: Operator's data stays in one place
  (the host); phones are temporary surfaces.

Pairing = phone is a *view* into the operator's home Ember.

---

## Privacy considerations

- WebSocket traffic encrypted (TLS if not on tailnet).
- Pairing tokens short-lived.
- Operator can unpair anytime.
- No data persists on phone beyond chat history (operator
  configurable).

This is *more privacy-friendly* than cloud-hosted phone AI (where
data lives on third-party servers).

---

## What about offline phone?

Phone-without-network can't reach host. Limitations:

- Can show cached recent chat history.
- Cannot make new requests.
- Reconnects automatically when network returns.

Yggdrasil's Vow of Graceful Offline applies to the *host*;
mobile companion is intrinsically network-dependent.

---

## What about pairing across the internet (not just tailnet)?

OpenClaw mentions "remote SSH gateway control" — implying that
operators can reach their host gateway from anywhere via SSH
tunnel.

For Ember: same approach. Operator wanting global reach:
- Set up Tailscale (free tier; sovereign).
- Phone has Tailscale; auto-connects.
- Pairing works as on home network.

No public exposure; no port-forwarding; Tailscale handles
encryption and access control.

This is *the right path* for Ember. We don't expose ports
publicly. Tailnet only.

---

## Lessons from OpenClaw's mobile

### 1. WebSocket pairing is the right shape

Operator-driven setup; persistent connection; clean state.

### 2. Phone as both surface and sensor

The phone offers UI *and* tools (camera, location). Both are
valuable.

### 3. Tools require approval

Phone camera tool requires PER_CALL approval (matches Ember's
existing model). Operator confirms before agent gets image.

### 4. Cross-device session continuity

Operator starts chat on laptop; continues on phone; sessions
flow. The Gateway holds session state; surfaces are stateless.

---

## What Ember should NOT do

🔴 **Reject for now**:

### 1. Native mobile apps in V1-V4

Too much engineering. Web companion is the right path.

### 2. App-store distribution

App stores impose constraints (review, fees, removal risk).
Tailnet-accessed web companion bypasses entirely.

### 3. Cloud-mediated pairing

OpenClaw apps might phone home for pairing setup. Ember's
should not. Direct WebSocket over tailnet.

---

## What we should build (eventually)

🟢 **Adapt to Ember Vows in V4-V5**:

### Phase 4-late or Phase 5: web companion

- Stofa (TUI) is desktop primary.
- Web companion is mobile primary.
- They share session state via host's Gateway.

### Pairing UX

- `ember companion start` on host: shows QR + URL.
- Operator's phone browser visits URL + scans QR.
- Pairing complete; chat works.

---

## Closing

Companion App Pairing is **OpenClaw's mobile story**. Native
apps + WebSocket pairing + Live Canvas + device capabilities
as tools.

Ember should:
- 🔴 Skip native apps for V1-V4.
- 🟢 Build web companion (Progressive Web App) in V5.
- 🟢 Use Tailscale for global reach (no public exposure).
- 🟢 Pair via QR + token; tailnet-only WebSocket.
- 🔵 Borrow the "phone as both surface and sensor" pattern when
  V5 lands.

This is *valuable but distant*. Plan now; build when V5
horizon arrives.
