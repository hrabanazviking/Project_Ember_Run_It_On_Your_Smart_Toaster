# 20 — Sibling: Cleasby-Vigfusson Old Norse Dictionary

> *"The lore-hoard at the root of the tree."*

A Next.js web frontend serving the Cleasby-Vigfusson Old Norse
dictionary corpus. Data, not service. Not Python.

---

## What it is

A static-corpus + Next.js web application that surfaces the
classic Cleasby-Vigfusson dictionary of Old Norse, originally
published 1874-1900. The dictionary itself is **public domain**
(authored before 1900); the Next.js wrapper is the only
project-specific code.

Three uses:

1. **As a website** — operator browses Old Norse words in
   their browser.
2. **As a data source** — the dictionary corpus can be
   exported as JSON/TSV.
3. **As an ingestion target** — Yggdrasil-Ember can ingest
   the dictionary into the Well.

---

## Why this sibling matters for Yggdrasil

Three integration roles:

### 1. Corpus for Ember's Well

The Old Norse dictionary is a *natural knowledge base* for
Ember:

- Many of Ember's surfaces, pets, realms, etc. have Norse
  names. The operator might ask "what does Heiðr mean?" or
  "what's the etymology of Yggdrasil?" — and Ember should
  *know*, not hallucinate.
- Ingesting the dictionary as a Well corpus means Ember can
  answer these questions with citations to the actual
  Cleasby-Vigfusson entries.

### 2. Lexicon for Seiðr

Seiðr Engine (sibling #4) generates verse using a Nine
Worlds lexicon. Cleasby-Vigfusson can *enhance* that
lexicon with attested forms, kennings, etc.

### 3. Translation surface (V2)

A future tool `translate_old_norse(text)` could use the
dictionary corpus for lookup-based translation of Old Norse
fragments the operator pastes into chat.

---

## How Yggdrasil integrates norse-dict

### Integration role

For V1, the simplest integration:

1. **Export the dictionary corpus to JSON/Markdown.** This is
   a one-shot operation; the corpus doesn't change.
2. **Ingest it into the operator's Well.** Becomes one of
   their normal documents — searchable, retrievable, citable.
3. **Provide a convenience CLI** (`ember yggdrasil ingest-norse-dict`)
   that does the export + ingest in one step.

### Adapter shape

A small `src/ember/yggdrasil/norse_dict/` package:

- `ingest.py` — fetches the dictionary corpus (from the
  Next.js app's data layer or a packaged data archive),
  parses entries, calls `BrunnrHandle.add_document` for
  each entry (or chunks them sensibly).

That's it. No runtime integration; just a one-shot ingest
helper.

### Configuration shape

```yaml
yggdrasil:
  norse_dict:
    auto_ingest: false           # operator runs explicitly
    corpus_path: ~/.ember/data/cleasby_vigfusson.json
    well_namespace: norse_lore
```

The `well_namespace` lets the operator query "in my norse_lore
namespace, what does Heiðr mean?" without polluting other
documents' search results.

### Seiðr integration (Phase 3)

Seiðr's lexicon (built from its own Nine Worlds vocabulary)
can be *augmented* by Cleasby-Vigfusson entries that match the
world themes. A Seiðr-extension reads the dictionary's
attested kennings and adds them to its generation pool.

This is a Seiðr-side change, not an Ember change. We document
it here as cross-sibling collaboration.

---

## Why this sibling is mostly data, not service

Cleasby-Vigfusson is a **public-domain dictionary corpus**.
The actual content doesn't change. The Next.js app is one
*presentation* of the data; Ember's Well becomes another.

Treating this as a *data source* rather than a *service* is
the right shape. We don't need to talk to the Next.js app
over HTTP; we just need the underlying corpus.

If the operator wants to *browse* the dictionary (use the
web UI), they run the Next.js app. If they want Ember to
*reference* the dictionary, they ingest it into the Well.
Two different surfaces; one corpus.

---

## Risk / known issues

- **Corpus extraction.** The dictionary needs to be in
  importable form. Yggdrasil-Phase-1 includes a one-time
  extraction step.
- **OCR errors.** Cleasby-Vigfusson was scanned + OCR'd.
  Entries may have typos. The dictionary itself is the
  source of truth; we don't try to correct.
- **Specialized vocabulary.** Many entries reference Old
  Icelandic / Old English / Latin etymological notes. Ember
  surfacing these might be confusing for non-philologist
  operators. Mitigation: clear citation; operator-facing
  reply doesn't pretend Ember authored the etymology.

---

## Open questions for Phase 1 ratification

1. **Corpus format.** JSON-per-entry? One big JSONL? Markdown
   per letter? Ingestion strategy depends.
2. **Update strategy.** When the Next.js app's data updates
   (corrections), how does Ember's Well get refreshed?
   Probably: operator re-runs the ingest CLI.
3. **Translation tool scope.** V1 = ingest only; V2 =
   translation tool. Defer translation features.

---

## Test strategy

Phase 1 ships:

- **Unit tests** for the corpus parser.
- **Integration test** — ingest a small sample of the
  dictionary into a tmp Brunnr, verify queries return
  expected entries.

Tests in `tests/unit/test_yggdrasil_norse_dict_ingest.py`.

---

## Operator-facing example

```bash
# One-time setup
ember yggdrasil ingest-norse-dict
# Output: "Ingested 35,217 entries from Cleasby-Vigfusson
# dictionary into Well namespace 'norse_lore'."

# Later, in chat:
> volmarr: what does the Old Norse word "Heiðr" mean?

ember: Let me check the dictionary.
[searches Well, filters to norse_lore namespace]

ember: From Cleasby-Vigfusson:
   • Heiðr (noun, feminine) — heath; brightness; honor;
     fame. Also a personal name, used in the Völuspá for
     a seeress.

So when our goat pet is called Heiðr, it's invoking the
domestic register: honor + brightness. The bright-faced
goat by the hearth.
```

The operator gets the *etymological truth* with a citation,
not Ember's guess.

---

## Closing

Cleasby-Vigfusson is **lore-hoard at the root of the tree** —
the Cleasby-Vigfusson dictionary as canonical reference for
all the Old Norse vocabulary Yggdrasil uses. Ingested into the
Well, it makes Ember *literate in her own naming*.

A small integration with a large culturally-grounding effect.
