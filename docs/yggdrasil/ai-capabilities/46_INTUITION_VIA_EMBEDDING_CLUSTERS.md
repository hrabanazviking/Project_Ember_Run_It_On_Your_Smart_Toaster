# 46 — Intuition via Embedding Clusters

How Ember surfaces "hunches" — things that feel relevant
but aren't directly asked about. The cluster-detection layer.

---

## The principle

Human intuition feels like guessing but is actually
*pattern recognition over implicit structure*. We "have a
hunch" when our brain notices a structural fit we can't yet
articulate.

Ember can do the same — operationally — by detecting
*embedding clusters* in her Well and surfacing cluster
neighbors when a query hits one corner of a cluster.

---

## What clusters are

In a vector store, documents that are semantically near
form *clusters* — regions of dense similarity.

```
                                ┌─ Cluster A ─┐
                                │  ●●●        │
                                │ ●● ●●       │
                                │  ● ●        │
                                └─────────────┘

                  ┌─ Cluster B ─┐
                  │  ●● ●●      │
                  │ ●● ●●●●     │
                  │  ●● ●       │
                  └─────────────┘

       ┌─ Cluster C ─┐
       │  ●●●        │
       │ ●● ● ●●     │
       └─────────────┘
```

A query lands at some point in vector space. Standard
retrieval returns the *nearest* documents (a few from one
cluster).

Ember's intuition layer: when a query lands near a cluster
*edge*, also surface a few documents from the cluster's
*core* — "things you didn't ask for but probably want."

---

## When intuition fires

Conditions for surfacing intuitive matches:

1. The query's top-3 results all live in the same cluster
   (high confidence the query is *about* that cluster).
2. The cluster has been *recently active* (operator queried
   it within the last N days) OR has *strong Muninn
   associations* with the query's topic.
3. There are documents in the cluster that haven't been
   surfaced in recent queries (avoiding repetition).

When all three: surface 1-2 *intuitive* documents in
addition to the direct matches. Label them as such in the
citation panel.

---

## What the operator sees

A chat-turn citation panel:

```
ember: Here's what I found about Odin's ravens:

   • notes/ravens.md — Hugin and Munin, the two ravens...
   • mythology/odin_cycle.md — Each morning Odin sends...
   • ─────────────────────────
   • [intuition] notes/yggdrasil.md — the tree where the
     ravens perch each evening. (related to your query
     but not directly about it)
```

The intuition citations are *visually distinct* (separator
+ label) so the operator knows these aren't direct answers
to their question — they're "you might also like."

---

## How the cluster is computed

In V1, clustering uses a lightweight density-based
approach:

```python
def find_cluster(query_embedding, all_chunks, k_for_cluster=20):
    """Return chunk IDs in the cluster around the query."""
    # Get k nearest by cosine
    near = vector_search(query_embedding, k=k_for_cluster)
    
    # Of those, find a subset that are also near each other
    # (true cluster, not just nearest to query)
    cohesive = filter_cohesive(near, cohesion_threshold=0.7)
    
    return cohesive
```

`filter_cohesive` keeps chunks that are within `0.7` cosine
similarity of at least 50% of other chunks in the set.
Loose, but useful.

V2 could use k-means or HDBSCAN; V1 keeps it simple.

---

## How intuition is *different* from retrieval

| Aspect | Retrieval | Intuition |
|---|---|---|
| Trigger | Operator asked X | Operator asked X, and X seems to be *about* a cluster |
| Returns | Top-k by relevance | Top-k by relevance PLUS 1-2 "cluster mates" |
| Labeling | None special | Labeled "[intuition]" |
| Confidence | High (matches query) | Medium (cluster-similarity) |

The labeling matters: operator sees `[intuition]` and
knows "this isn't what I asked for, but Ember thinks I
might want it."

---

## Why this works operationally

In practice, operators researching a topic:

1. Ask question A about cluster X.
2. Ember returns answers + (intuitively) one cluster X
   document they didn't know existed.
3. Operator notices that document, asks about it.
4. Cluster X gets reinforced (Mímir promotion); Muninn
   strengthens associations.
5. Future queries about cluster X surface this document
   directly.

The intuition layer *seeds the operator's exploration*.

---

## Operator-facing example

```
> volmarr: tell me about Odin's sacrifice on Yggdrasil

ember: Odin hung himself on the world-tree for nine nights,
pierced by his own spear, dedicated to himself. He learned
nine mighty songs and won the runes...

Direct sources from your Well:
   • notes/odin/sacrifice.md
   • havamal/sacrifice_verse_138.md
   
Related (cluster intuition):
   • notes/initiation_rituals.md — Other Norse initiatory
     death-and-rebirth motifs. (You haven't returned to
     this in ~3 months.)
```

The operator might say "oh right, I haven't looked at that
in a while" and ask about it. Or they might say "not what
I'm looking for; skip it." Either way: the *opportunity* to
discover a related document was given without forcing the
operator to know it was there.

---

## What intuition is NOT

- **Not prediction.** We don't predict what the operator
  will ask next; we surface what they might appreciate now.
- **Not mind-reading.** Cluster detection is mechanical;
  no claim about operator's inner state.
- **Not always firing.** Most chat turns get standard
  retrieval only. Intuition fires when clusters are
  detected AND not over-firing.

---

## Configuration shape

```yaml
yggdrasil:
  intuition:
    enabled: true
    max_intuitive_per_turn: 2
    cluster:
      k_neighbors_for_cluster: 20
      cohesion_threshold: 0.7
    surface:
      require_recent_activity: false   # surface even cold clusters
      cooldown_per_doc_days: 7         # don't repeat same intuition
      label: "intuition"               # operator can rename
    confidence_threshold: 0.6          # only surface if confident
```

---

## How Verdandi sees intuition

Events:
- `intuition.cluster_detected` (cluster_id, size)
- `intuition.surfaced` (chunk_id, query, cluster_id)
- `intuition.operator_engaged` (chunk_id, follow_up_query)

The "engaged" event lets the meta-learning layer notice
which intuitions paid off — strengthens those cluster
profiles for future suggestions.

---

## Risk / known issues

- **Noise.** Bad clusters surface irrelevant intuitions.
  Mitigation: confidence threshold + cooldown.
- **Spam.** Too many intuitions per turn fatigues operator.
  Cap at 2.
- **Cluster-bias.** Operator who consistently dismisses
  intuitions gets fewer over time. (Pattern-detection
  loop notices.)

---

## Why this is "intuition"

The word matters. We could call this "cluster-based
expansion" — accurate but cold.

"Intuition" captures the *feel* — the operator experiences
it as Ember *sensing* something relevant they didn't ask
for. The implementation is mechanical; the experience is
something close to: a research assistant who's been
working with you long enough to anticipate connections.

This isn't anthropomorphism (we're not claiming Ember
*has* intuition in a human sense). It's *labeling that
matches the operator's experience*.

---

## Closing

Intuition via Embedding Clusters is **the surfacing layer
for hunches**. Mechanical underneath; experientially
*intuitive* on top. Surfaces opportunities the operator
might value without overwhelming them.

This is what makes Ember feel *attentive* rather than
*reactive*.
