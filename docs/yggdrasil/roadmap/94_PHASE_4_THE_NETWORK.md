# 94 — Phase 4: The Network

Federation across the operator's tailnet. Multiple Ember
nodes coordinating as one.

---

## What Phase 4 delivers

By the end of Phase 4:

- **Federation layer** lets multiple Ember instances
  coordinate (per
  [`../cross-platform/65_DISTRIBUTED_COORDINATION.md`](../cross-platform/65_DISTRIBUTED_COORDINATION.md)).
- **Role-based node configuration** (inference / storage
  / surface / ingest).
- **mDNS-based discovery** over tailnet.
- **Shared-secret authentication** between nodes.
- **Cross-device shared memory** (the Well lives on one
  node; surfaces consume from any).
- **Inference offload** (laptop chats; workstation runs
  the model).
- **Federation health observability** (Doctor screen shows
  remote nodes).
- **Graceful degradation** when nodes go offline.

Operators experience:
- "Same Ember everywhere" across their devices.
- Light laptop + heavy workstation = best of both.
- Pi-stofa-only mode for ambient surfaces.

---

## The work breakdown

### Track A: Federation core protocol (~6 weeks)

**Goal:** the wire protocol for node coordination.

Tasks:
1. `FederationNode` class managing peer connections.
2. Protocol: gRPC OR custom JSON-over-mTLS (decide
   during planning).
3. Capability advertisement per node.
4. Role-based routing.
5. Shared-secret auth.
6. Tests: 2-node + 3-node integration.

**Risk:** Protocol bikeshedding.
**Mitigation:** time-box decision; pick "good enough."

### Track B: Discovery (~3 weeks)

**Goal:** nodes find each other.

Tasks:
1. mDNS advertisement + listening.
2. Explicit peer-list fallback (for non-mDNS networks).
3. Tailnet detection helper.
4. CLI: `ember federation discover`.

**Risk:** mDNS unreliable across network topologies.
**Mitigation:** explicit peer list always works.

### Track C: Cross-node inference routing (~5 weeks)

**Goal:** route Funi requests to remote inference node.

Tasks:
1. `RemoteFuni` adapter routing through federation.
2. Streaming-response handling over the wire.
3. Tail-latency considerations (cache plumbing).
4. Fallback to local Funi when remote unreachable.

**Risk:** Streaming latency on tailnet.
**Mitigation:** tailnet RTT is typically <5ms; should
be fine. Operator can warn if RTT exceeds threshold.

### Track D: Cross-node memory access (~5 weeks)

**Goal:** Brunnr/Bifrǫst routed to remote storage node.

Tasks:
1. `RemoteBifrostBrunnr` adapter.
2. Local cache for recent retrievals (small LRU).
3. Reconciliation when network re-connects.
4. Tests: laptop with empty local Well, queries remote
   storage node successfully.

### Track E: Coordinated state evolution (~4 weeks)

**Goal:** Episodes from any node land in the same Well.

Tasks:
1. Episode writes routed to storage node.
2. Local fallback when storage node unreachable
   (queue + sync later).
3. Conflict resolution for divergent writes.
4. Tests: write-from-laptop, read-from-pi.

### Track F: Doctor + Stofa updates (~2 weeks)

- New Federation panel in Stofa.
- Doctor rows per remote node.
- Per-node health gossip displayed.
- Inference / storage role indicators.

### Track G: Cross-cutting (~3 weeks)

- ADRs.
- DEVLOG.
- V3 → V4 migration (mostly additive; existing single-
  node operators see new federation config but unaffected
  if they don't enable).
- Documentation for operators setting up multi-device.

---

## Total estimate

Roughly 28 weeks. Real-world: 6-8 months after Phase 3.

---

## What ship-readiness looks like

- [ ] Single-node operators see no regression.
- [ ] 2-node setup works end-to-end (laptop + homelab).
- [ ] 3+ node setup works (laptop + homelab + pi).
- [ ] Killing one node doesn't bring down the others.
- [ ] Re-joining a node syncs cleanly.
- [ ] Documentation walks operator through setup
      step-by-step.
- [ ] Stofa Federation panel functional.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Distributed-systems complexity | High | Time-box scope; defer edge cases |
| Auth setup friction | Medium | Document carefully; provide setup wizard |
| Latency on tailnet | Medium | Local caches; degrade gracefully |
| Schema-divergence across versions | High | Require version match across federation |
| Operators self-hosting tailnet | Low | Tailscale is reliable; document alternatives |

---

## Phase 4 success criteria

Operator-visible:
- Laptop running Stofa can use homelab's 70B model
  transparently.
- Pi can run Stofa-only and use the family Well.
- "Same Ember everywhere" feels real.

Operationally:
- Federation health visible in Doctor.
- Reconciliation works after network restorations.
- No data loss in cross-node operations.

---

## What operators set up

A typical Phase-4-using operator:

```bash
# On homelab desktop:
ember federation init --role=inference,storage
# Shows a setup token to share with other nodes

# On laptop:
ember federation join <token>
# Auto-discovers homelab via tailnet
# Configures itself as surface role
```

That's it. Two commands. Federation works.

For air-gapped or non-tailnet setups, explicit peer-list
configuration in `ember.yaml`.

---

## What's NOT in Phase 4

Deferred to Phase 5 or beyond:
- Skein / Skry live integration.
- Multi-modal.
- Mirror of Ginnungagap.
- Cloud-hosted federation (we still won't do cloud).

Federation is *one focused thing*. We ship it well.

---

## Closing

Phase 4: The Network **expands Ember from a single device
to a fabric**. One Ember experience; many devices
participating; full sovereignty maintained.

This is what *power-operators* have been waiting for: the
ability to have Ember on every device they own, all
sharing the same memory + identity + presence.
