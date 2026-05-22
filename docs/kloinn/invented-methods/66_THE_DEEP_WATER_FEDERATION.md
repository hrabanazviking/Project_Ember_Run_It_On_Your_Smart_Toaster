# 66 — The Deep Water Federation

A new method for *federation across operator's devices over
slow/limited links* — informed by OpenClaw's multi-device
shape but extended for high-latency / intermittent connectivity.

---

## What problem this solves

Yggdrasil's Phase 4 federation assumes good tailnet
connectivity — < 5ms RTT, persistent connection.

But operators sometimes face:
- **Slow links** (cellular, satellite, rural broadband).
- **Intermittent** (mobile while traveling).
- **Bandwidth-limited** (metered data; tethering).

Standard federation breaks down. Calls timeout. Synchronization
fails. Operator's mobile Ember is effectively offline.

The **Deep Water Federation** is *resilient* federation: works
even when links are slow, intermittent, or bandwidth-limited.

Named for lobsters at depth — communicating across vast water
columns, slowly but reliably.

---

## How it differs from standard federation

Standard federation:
- Real-time RPC.
- Persistent connections.
- Sub-second responsiveness assumed.
- Fails fast when slow.

Deep Water Federation:
- Asynchronous message queues.
- Store-and-forward.
- Resilient to disconnects.
- Eventual consistency.
- Operator-visible queue state.

---

## The pattern

```
                    ┌──────────────────────┐
                    │   Home Ember Gateway  │
                    │                       │
                    │   ┌────────────────┐ │
                    │   │ Outbound Queue  │ │
                    │   │ (durable)       │ │
                    │   └────────┬───────┘ │
                    └──────────┬─┴─────────┘
                                │
                                │  (slow/intermittent link)
                                │
                    ┌──────────▼───────────┐
                    │  Mobile Ember Surface │
                    │                        │
                    │   ┌──────────────┐    │
                    │   │ Inbound Queue │    │
                    │   │ (durable)     │    │
                    │   └──────────────┘    │
                    └──────────────────────┘
```

Messages queue at sender. Pushed when link permits. Acked when
received. Retried with exponential backoff.

---

## Use case: traveling operator

Operator on long train ride; mobile data sporadic.

```
[operator on phone]
> Ember, what was that Norse word for "well-loved"?

[Phone's Ember surface queues message]
[Push attempt 1: timeout (no signal)]
[Push attempt 2: timeout]
[Push attempt 3 (5 min later): signal returns; pushed]

[Home Ember processes]
[Reply queued for delivery]
[Delivery attempt 1: timeout]
[Delivery attempt 2 (10 min later): success]

[Phone displays reply]
ember: "Ástúðlegur" — Old Norse for "loving, dear".
```

Operator typed at minute 0. Got response at minute 18. Both
queues handled the intermittency.

This is *asynchronous-by-design* — not failing on slow links.

---

## What this enables

### 1. Mobile Ember in poor coverage

Travel laptop → home Ember works across spotty wifi.

### 2. Background message processing

Operator types question at 10am while underground; reply
arrives at 10:15 when above ground. No lost messages.

### 3. Operator-visible queue

```
ember sync status

Deep Water queues:
  Outbound:
    1 message queued (typed 3 min ago)
    Last delivery attempt: 30s ago (timeout)
    Next retry: 60s
  Inbound:
    0 messages waiting
  
Total messages pending: 1
Cleared on: signal returns
```

Operator knows what's pending.

---

## How acknowledgments work

Each message has:
- Message ID (UUID).
- Sequence number per direction.
- Sent timestamp.
- Acked status.

```python
{
  "msg_id": "...",
  "seq": 142,
  "direction": "mobile_to_home",
  "sent_at": "2026-05-22T10:00:00Z",
  "acked_at": null,                  # not yet acked
  "retry_count": 3,
  "next_retry_at": "2026-05-22T10:01:00Z",
}
```

Both sides keep this log. When ack received: status updated.
On reconnect: missing acks trigger re-pushes.

---

## What gets queued vs not

Queued:
- Chat messages (operator → Ember; Ember → operator).
- Tool approval requests.
- Notification events.

Not queued (real-time only):
- Live token streaming (only when connected).
- Voice (latency-sensitive).
- Long-running tool execution (must be local).

Deep Water shines for *async* operations. Real-time still needs
real-time.

---

## Bandwidth optimization

For metered connections:
- **Message compression**: gzip/zstd on JSON payloads.
- **Token vs full response**: stream tokens when connected;
  send compressed text when queued.
- **Image stripping**: phone-camera tools strip EXIF, downsize
  images before queuing.
- **Tools cached**: tool descriptions cached on phone; not
  re-sent every turn.

These reduce data transferred per chat-turn from ~5-50KB to
~0.5-5KB. Significant on metered cellular.

---

## Tailscale as the carrier

Tailscale handles the connectivity. Tailscale Subnet
sharing + tailnet's mesh routing mean:
- Phone connects to home Ember regardless of physical
  network.
- WireGuard encryption is automatic.
- Tailscale's "magic DNS" lets us address by hostname.

So Deep Water's queues sit *above* Tailscale's connectivity.
We don't reinvent VPN.

---

## Local-first on mobile

When operator's phone is offline (no signal at all):
- Last-known reply is cached.
- Operator can browse recent chat history.
- New messages queued for when connection returns.

This is **the local-first promise** — operator interaction
*never* depends on connection.

---

## Configuration shape

```yaml
ember:
  deep_water:
    enabled: false                 # opt-in V5
    
    queues:
      outbound:
        max_size: 1000             # max pending
        persistence: ~/.ember/state/queues/outbound.jsonl
        retry_backoff_start_s: 30
        retry_backoff_max_s: 3600
      inbound:
        max_size: 1000
        persistence: ~/.ember/state/queues/inbound.jsonl
    
    bandwidth:
      compress_payloads: true
      strip_image_exif: true
      max_image_kb_when_metered: 200
    
    auto_detect_metered: true       # via tailscale signals
    
    operator_visibility:
      surface_queue_status: true
      notify_on_persistent_failure: true
```

---

## What this is NOT

🔴 **Reject**:

### 1. Cloud-mediated messaging

Deep Water uses tailnet only. No third-party message queue
(no MQTT cloud, no AWS SQS, no Firebase).

### 2. Eventual consistency for state

Deep Water is for *messages*, not for state synchronization.
Ember's state (Mímir, Muninn, etc.) lives on home device;
phone is a *surface*, not a *replica*.

### 3. Always-available remote LLM

Deep Water doesn't promise the LLM is reachable. It promises
that *when reachable*, traffic flows reliably.

---

## V5+ ship plan

🟡 **Phase 5+ Klóinn adoption** — when web companion +
federation are mature.

Implementation:
- Phase 5a: outbound/inbound queues with retry.
- Phase 5b: bandwidth optimization.
- Phase 5c: operator-visible status.
- Phase 5d: integration with web companion.

Each step is independently shippable.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Queue grows unboundedly | max_size limits |
| Messages lost on phone restart | Persistent queues |
| Order of delivery wrong | Sequence numbers; reorder on receive |
| Operator confusion about delays | Visible queue status |

---

## Composition with other methods

| Method | Deep Water interaction |
|---|---|
| Federation (Yggdrasil) | Standard federation when connected; Deep Water when slow |
| Tide Routing | Tide can choose Deep Water if link is slow |
| Humarr Gateway | Manages Deep Water queues |
| Web companion | Deep Water + PWA = travel-friendly Ember |

---

## Closing

The Deep Water Federation is **Ember's offline-tolerant
multi-device pattern**. Slow/intermittent links no longer
break federation.

Named for the *deep water of lobster habitat* — connectivity
that flows slowly but reliably. Pairs with web companion for
travel-friendly Ember.

V5+ feature. Pairs with federation + web companion. Maintains
tailnet-only sovereignty.

This is *resilient sovereign-AI federation*. Klóinn-original
method for the codex.
