# 65 — Distributed Coordination

How multiple Ember instances on the operator's network
coordinate as a single federated system. Phase 4 feature;
Yggdrasil's most advanced capability.

---

## The principle

A power-operator may have:
- A laptop they carry around (chat + light memory).
- A homelab desktop with a big GPU (heavy inference).
- A NAS with the canonical Well storage.
- A Pi at home for ambient/voice surface.

Today, each runs *separately*. Yggdrasil Phase 4 lets
them **federate** — coordinate as a single distributed
Ember.

Properties:
- **Sovereign-only**: federation stays within the operator's
  network (tailnet). Never cloud.
- **Opt-in**: defaults stand-alone.
- **Decentralized**: no node is required; nodes negotiate
  capabilities.
- **Graceful**: any node going offline = federation
  degrades, doesn't break.

---

## The roles a node can play

A node advertises one or more roles:

| Role | What it offers |
|---|---|
| **Inference** | LLM access (Funi); GPU resource |
| **Storage** | the canonical Well / Mímir / Huginn DBs |
| **Surface** | a Stofa instance for the operator |
| **Ingest** | spare CPU to run Smiðja batch ingest |
| **Specialty** | a unique capability (e.g., the only node with CloakBrowser) |

Each node configures which roles it offers:

```yaml
yggdrasil:
  federation:
    enabled: true
    roles:
      - inference        # this node has the GPU
      - storage          # also the Well lives here
    advertise_on_tailnet: true
```

Other nodes discover via tailnet (mDNS or operator-
configured peer list).

---

## How federation works at chat time

Operator types into Stofa on their laptop:

1. **Laptop Stofa** (surface role) receives input.
2. Laptop's local Yggdrasil checks: do I have an inference
   role locally?
   - **Yes** → run LLM locally.
   - **No** → discover inference node on tailnet; route.
3. Laptop's Yggdrasil checks: do I have storage locally?
   - **Yes** → use local Brunnr/Bifrǫst.
   - **No** → discover storage node; route retrieval.
4. Inference + retrieval happen wherever-appropriate.
5. Result returned to laptop Stofa.
6. Operator sees streaming reply.

Latency adds a few ms (tailnet RTT is < 5ms typically).
Operator-perceptible only on first-token; subsequent
tokens stream as usual.

---

## How discovery works

Two modes:

### Mode 1: mDNS over tailnet

Each federation-participating Ember advertises:
```
_ember-yggdrasil._tcp.local
  port 9876
  txt-record:
    roles=inference,storage
    node-id=homelab-1
    version=2.0.0
```

Nodes on the same tailnet auto-discover.

### Mode 2: Explicit peer list

Operator configures known peers:
```yaml
yggdrasil:
  federation:
    peers:
      - hostname: laptop.tailnet
        roles: [surface]
      - hostname: homelab.tailnet
        roles: [inference, storage]
      - hostname: pi-ambient.tailnet
        roles: [surface]
```

mDNS for the convenience case; explicit list for the
stable case.

---

## Authentication

Federation requires nodes to trust each other. Yggdrasil's
default: **operator-installed shared secret** (one per
federation):

```yaml
yggdrasil:
  federation:
    auth:
      kind: shared_secret
      secret_ref: kista://ember/federation_secret
```

Kista holds the secret. All operator-controlled nodes
share the same Kista vault content (operator manually
syncs once).

Optional: PKI-style with per-node certs. V3.

---

## How storage federates

The Well lives on one node (the storage node). Other
nodes access it via:

- **Direct connection** (Brunnr's pluggable backend
  pointing at the storage node).
- **Cache-with-fallback** (each node has a small local
  cache; falls back to remote when uncached).

Operator chooses per-node:

```yaml
# On laptop:
yggdrasil:
  federation:
    storage:
      mode: remote
      node: homelab.tailnet
      local_cache_mb: 200       # cache recent chunks
```

Network blip → cache serves; falls back to "Mímir
unavailable" when truly disconnected.

---

## How inference federates

The LLM lives on the inference node. Other nodes route
inference requests:

```python
async def funi_complete(prompt: str) -> str:
    if self.has_local_inference:
        return await self.local_funi.complete(prompt)
    
    inference_node = self.federation.find_node("inference")
    if not inference_node:
        return Disconnected("no inference node reachable")
    
    return await self.federation.rpc(
        inference_node,
        "funi.complete",
        prompt=prompt,
    )
```

The RPC happens over the tailnet; secured by the federation
auth.

---

## Handling node failures

Per [`50_SELF_HEALING_PHILOSOPHY.md`](../robustness/50_SELF_HEALING_PHILOSOPHY.md):
each node fails independently.

- **Inference node down** → other nodes can't chat (until
  it returns). Surface clear banner.
- **Storage node down** → cached content served; new
  retrievals fail with typed-error.
- **Surface node down** → operator can use Stofa on another
  surface node.

Reconciliation per node:
- Each node tracks its own Verdandi events.
- When federation reconnects, nodes exchange "what I did
  while you were away" digests.
- Conflicting writes resolve by timestamp + operator
  notification.

---

## Anti-patterns we don't do

### Cloud-anything

Federation stays on the operator's network. We don't
offer "Yggdrasil cloud" — operators wanting that can
self-host on their own VPS, but it's the same code with
the operator's own tailnet.

### Centralized coordinator

No "master node." Every node is peer. The role advertising
means *capability discovery*; not authority.

### Persistent global state

The Well is on the storage node; Mímir is there; etc. But
each node holds its own ephemeral state (chat draft,
Stofa UI). No "global state across nodes" requiring
consensus protocols (Paxos, Raft).

### Magic load-balancing

Federation routes by role, not by load. If multiple
inference nodes exist, operator chooses how to assign
(or accepts default = "first one found").

---

## Cross-device shared memory

The Well + Mímir are *single-source* (on the storage node).
This means:
- Operator's notes are consistent across devices.
- Episodes from any node land in the same Well.
- Patterns from any node feed the same meta-learning.

It's *one Ember*, surfaced across devices.

---

## Configuration shape (federated)

Homelab node (storage + inference):
```yaml
yggdrasil:
  federation:
    enabled: true
    roles: [inference, storage]
    advertise_on_tailnet: true
    auth:
      kind: shared_secret
      secret_ref: kista://ember/federation_secret
    bind:
      host: 0.0.0.0           # tailnet interface
      port: 9876
```

Laptop node (surface only):
```yaml
yggdrasil:
  federation:
    enabled: true
    roles: [surface]
    auth:
      kind: shared_secret
      secret_ref: kista://ember/federation_secret
    peers:
      - hostname: homelab.tailnet
        roles: [inference, storage]
    fallback:
      offline_mode: graceful  # when federation unreachable
```

Pi ambient node (surface only):
```yaml
yggdrasil:
  federation:
    enabled: true
    roles: [surface]
    auth:
      kind: shared_secret
      secret_ref: kista://ember/federation_secret
    discovery: mdns           # auto-find peers
```

---

## Operator-facing example

Operator on travel laptop, while at home:

```
[Stofa launches]
[Federation discovers homelab.tailnet]

Ember (federated):
  Surface: this laptop
  Inference: homelab.tailnet (RTX 2060, llama3.1:70b)
  Storage: homelab.tailnet (Well + Mímir + Huginn)

> volmarr: tell me about Yggdrasil

[Routed to homelab for inference + retrieval]
[Response streams to laptop]

ember: Yggdrasil is the world-tree in Norse cosmology...
```

Operator leaves home, goes to coffee shop. Tailnet is
up; federation continues. Laptop's chat uses homelab's
70B model, accessed via tailnet RTT.

Operator goes on plane. Tailnet down. Stofa shows:

```
Federation: degraded (homelab unreachable).
Falling back to local-only mode.
Local Funi: tinyllama:1b (~600 MB; CPU only).
Local Well: 200 MB cache (last sync 6 hours ago).
```

Operator can still chat, with reduced capability. When
they land + reconnect: federation re-syncs.

---

## What this enables

### "Ember everywhere" without re-config

Same operator, multiple devices, *one Ember experience*.
Operator's memory + identity + patterns are shared.

### Heavy GPU for cheap

Operator buys one GPU; uses it from any device.

### Resilient + portable

Take any single device away; the others continue. Add a
new device; it joins automatically (mDNS).

### Cluster operator paradise

Heiðr persona (cluster operator) gets a fleet of Pi-nodes
+ a homelab; orchestrates them as one Ember.

---

## Risk / known issues

- **Tailnet dependency.** Without tailnet, no federation.
  Operators on simpler networks (LAN-only) get LAN-mode
  with explicit peer list.
- **Auth setup complexity.** Sharing the federation
  secret across nodes is operator work; we document
  carefully.
- **Latency-sensitive ops.** Streaming token-by-token over
  tailnet is OK; sub-100ms operations (audit, retrieval)
  may feel slower. Local caching mitigates.
- **Schema evolution across federation versions.** All
  federated nodes should run the same Yggdrasil version.
  Version mismatch handling: degrade to compatible
  protocol or refuse-with-clear-message.

---

## Closing

Distributed Coordination makes Yggdrasil **a federation
of Embers that feels like one Ember**. Operator chooses
which roles each node plays; federation handles routing,
discovery, auth, and reconciliation.

Sovereign. Decentralized. Resilient. Always within the
operator's own network.

This is Phase 4 — the highest expression of Yggdrasil's
cross-platform promise. Not a single device; the *fabric*
of devices.
