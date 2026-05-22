# 47 — Curiosity-Driven Ingest

When Ember (with operator consent) reaches out to fetch
content related to the operator's emerging interests. The
agentic side of memory growth.

---

## The principle

Today, Ember's Well grows only through *explicit operator
ingest*. The operator runs `ember well ingest <path>`;
documents land.

Yggdrasil-V2 (opt-in) adds **curiosity-driven ingest**:
when Ember notices the operator's questions consistently
push *beyond* what's in the Well, she can *suggest*
fetching more — and, with explicit approval, do it.

The operator stays in control. Ember just *offers*.

---

## When curiosity fires

The trigger: Ember has tried to retrieve, gotten thin
results, but the operator keeps asking related questions.

```python
def should_offer_ingest(recent_episodes):
    """Detect a sustained-thin-retrieval pattern."""
    
    # In recent 10 turns, how many had < N hits?
    thin_turns = sum(1 for e in recent_episodes[-10:]
                     if e.hits_count < THIN_THRESHOLD)
    if thin_turns < 5:
        return None  # operator's Well is fine
    
    # All thin turns about similar topics?
    topics = [extract_topic(e) for e in recent_episodes[-10:] if e.hits_count < THIN_THRESHOLD]
    if not all_similar(topics):
        return None  # not a coherent gap
    
    # Suggest filling the gap
    return CuriositySuggestion(
        topic=consensus(topics),
        confidence=thin_turns / 10,
    )
```

When confidence > threshold: surface a suggestion in chat.

---

## What the suggestion looks like

```
> volmarr: what does the Havamal say about hospitality?

ember: I have one mention of hospitality in your notes
(from yggdrasil_research.md), but no specific Havamal
quotes. The Havamal has some classic verses on this — want
me to fetch the standard English-translation text and
ingest it into your Well? (~5 minutes to download + chunk)

> volmarr: yes please

[Ember proposes fetch_url for a public-domain Havamal
translation; operator approves]
[Translation fetched, ingested into Well, chunked]

ember: Done. Now I have the Havamal. To your question:
verses 1-3 are the classic on hospitality...
```

The suggestion is **specific** (names the source, gives
estimate), **optional** (operator says no), **transparent**
(operator sees the tool calls + approves them).

---

## What sources are candidates

Curiosity-driven ingest can pull from:

- **Public domain corpora** (Project Gutenberg, sacred-
  texts.com, etc.) — clear copyright; safe to ingest.
- **Operator-configured trusted sources** (their own
  wiki, their notes folder, etc.).
- **Wikipedia** (CC-BY-SA; cite-on-use).
- **Academic open-access sources**.

NOT candidates:
- Paywalled content (would require auth + ethics).
- Real-time data (weather, news; not the right shape for
  Well-style storage).
- Operator's email / private documents (sovereignty
  violation; only operator manually ingests these).

---

## The trust pyramid

```
        always_ask (default)
       ─────────────────────
              │
              ▼
        Operator-curated public sources
        - public-domain texts
        - Wikipedia
        - operator-configured wiki
              │
              ▼
        Per-call approval (operator says y/n each time)
              │
              ▼
        Fetch + ingest
```

Operators can configure trust:

```yaml
yggdrasil:
  curiosity:
    enabled: false                # opt-in
    auto_suggest: true            # surface suggestions in chat
    sources:
      - kind: public_domain
        domains: [gutenberg.org, sacred-texts.com]
        require_approval: per_call
      - kind: wikipedia
        require_approval: per_call
      - kind: operator_wiki
        urls: [https://my-wiki.example/]
        require_approval: standing  # operator trusts wholly
```

Default: all per-call approval. Operators with reasons elevate.

---

## What curiosity does NOT do

- **No autonomous web crawling.** Ember asks; operator
  approves; one fetch happens.
- **No bulk ingest.** Per-source small chunks; not a
  scraping framework.
- **No paywall bypass.** Operator-provided credentials
  only via Kista (per [`33_THE_KISTA_SECRET_PLANE.md`](../architecture/33_THE_KISTA_SECRET_PLANE.md)).
- **No "I'm curious about this" without operator prompt.**
  Ember offers only when the operator's *recent questions*
  show a gap.

---

## The agency boundary

This is the closest Yggdrasil gets to "agentic AI." The
boundary:

| Action | Who decides |
|---|---|
| Notice operator gap | Ember (pattern detection) |
| Offer suggestion | Ember (surfaces in chat) |
| Accept or decline | Operator |
| Choose source | Operator (or pre-configured trust) |
| Fetch content | Tool framework (per-call approval) |
| Ingest content | Smiðja (operator-visible progress) |
| Use in future chats | Brunnr (now part of Well) |

Every consequential step has operator involvement. Ember
is *attentive*, not *autonomous*.

---

## Operator-facing example

```
[Past 10 turns: operator keeps asking about a topic with
thin retrieval]

> volmarr: what's the difference between Skuld and Verðandi?

ember: I can tell you Verðandi is the present-Norn and
Skuld is the future-Norn, but I notice you've been asking
about the Norns for several turns now and your Well doesn't
have much depth here.

Want me to fetch a couple of public-domain references?

   • Project Gutenberg's translation of the Völuspá
   • The Prose Edda (Brodeur translation, 1916)

I'll show you each fetch + ingest as it happens; takes ~5
minutes total. Or we can just keep working with what's in
your Well.

> volmarr: yes, fetch both

[fetch_url called twice with operator approval]
[Smiðja ingests both]
[Bee pet animates in Stofa during ingest]

ember: Done — 23 new chunks from Völuspá + 47 from Prose
Edda. Now for your Skuld vs Verðandi question:

The Völuspá names them as: Urðr (Wyrd, past), Verðandi
(Becoming, present), Skuld (Should, future). Brodeur's
translation of the Prose Edda adds...
```

A research assistant moment. Operator gets sourced answers
*plus* their Well grew during the process.

---

## How meta-learning interacts

The meta-learning layer (per
[`44_META_LEARNING_FROM_EPISODES.md`](44_META_LEARNING_FROM_EPISODES.md))
can detect:

- "Curiosity suggestions are accepted 80% of the time."
  → bias toward suggesting.
- "Curiosity suggestions are declined 70% of the time."
  → bias against, or surface less.
- "Suggestions for X-type sources always declined."
  → drop those from candidate set.

Operators with strong preferences get curiosity tuned to
their pattern.

---

## Risk / known issues

- **Disk space.** Auto-ingesting fills the Well. Mitigation:
  per-source size caps; operator-visible Well growth.
- **Quality of public sources.** Wikipedia has errors;
  Project Gutenberg has OCR issues. Each ingested
  document is *cited* — operator can verify when Ember
  surfaces it.
- **Ethics of fetching.** All fetches go through tool
  framework approval; same as any tool call.
- **Curiosity-fatigue.** If suggestions fire too often,
  operator gets annoyed. Cap rate; cool down.

---

## Configuration shape

```yaml
yggdrasil:
  curiosity:
    enabled: false                  # opt-in (off by default)
    triggers:
      thin_retrieval_count: 5        # of last 10 turns
      min_topic_consistency: 0.6     # how alike thin turns must be
      cooldown_minutes: 60           # don't suggest again within
    sources:
      - kind: public_domain
        domains: [gutenberg.org]
        require_approval: per_call
      - kind: wikipedia
        require_approval: per_call
    max_suggestions_per_session: 3
```

---

## Closing

Curiosity-Driven Ingest gives Ember **agency in service of
the operator's curiosity** — not autonomy, but
attentiveness. When the operator's questions push beyond
what's in the Well, Ember *notices* and *offers* to fetch
more.

The operator stays in control. The Well stays the
operator's. Ember grows when invited.

This is *agentic, within bounds* — the only kind of agency
Yggdrasil endorses.
