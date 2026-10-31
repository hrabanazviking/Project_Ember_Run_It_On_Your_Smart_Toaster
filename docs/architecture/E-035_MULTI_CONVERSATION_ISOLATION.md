# E-035 — Multi-conversation isolation

*Part II, slice E-035. Roadmap line: "Multi-conversation
isolation (fixtures prove no bleed)."*

## What was wrong

E-025 gave the companion personae, each with its own memory.
Inside one persona there was still exactly **one undifferentiated
memory stream**: every episode the persona ever remembered
loaded into every session. An operator who talked to Ember
about household planning in the morning and a work project in
the afternoon got each talk in the other's prompts — the
morning's turns rode into the afternoon's context, windowed and
summarised together, with no way to keep them apart.

## The shape (E-025's discipline, one level in)

A **conversation** is one talk inside a persona — one topic,
one thread. Episodes now carry a second tag beside
`persona_id`:

- `Episode.conversation_id` defaults to `"default"`
  (`ember.schemas.conversation.DEFAULT_CONVERSATION_ID`) — the
  namespace every pre-E-035 episode already belongs to, so an
  existing install's history is continuous, not orphaned.
- Ids are slugs under the persona rules (lowercase letters,
  digits, `-`/`_`, ≤64 chars, never a path), judged in one place:
  `ember.schemas.conversation.is_valid_conversation_id`.

Separation is enforced at the same three doors as persona
separation, in `ember.spark.conversation`:

1. **Resolution** — `resolve_conversation_id(explicit,
   configured)`: the per-invocation choice wins, then the
   config file's `conversation.active`, then `default`. An
   invalid chosen id raises `ConversationError`; chat names it
   and stops (exit 1) — never a silent fall-back to a different
   talk, which would mix exactly what the operator separated.
2. **Filtering** — `episodes_for_conversation` is exact-match
   only. Chat loads history as persona filter → conversation
   filter → windowing, in that order, so a foreign talk's turns
   can neither ride verbatim **nor leak back through the
   window's summary of dropped episodes** (fixture-proven).
3. **The prompt wall** — `prompt.assemble(...,
   conversation_id=...)` drops foreign-conversation episodes
   whatever the caller passed, composing with the persona wall:
   a turn carries only episodes that are its persona's *and*
   its conversation's. Episode context items now also carry
   `conversation_id` in their metadata. Callers that pass no
   conversation id keep the pre-E-035 shape unchanged.

## Wiring

- `chat.run(..., conversation_id=None)` resolves the session's
  conversation after persona resolution, loads only its turns,
  assembles under it, and tags every Episode it persists
  (streaming and non-streaming roads alike). `ember ask` rides
  the same run, so it inherits the configured conversation.
- CLI: `ember chat --conversation <id>`; config:
  `conversation.active` (documented in
  `config/ember.example.yaml`; the E-033 tree-walk stays green
  and a TOML coercion test pins the new key).
- Diary (E-034): a non-default conversation is noted in plain
  words ("This session is in the '…' conversation, kept apart
  from Ember's other talks."). The default conversation adds no
  note — the pinned E-034 sentences are unchanged.
- Pending journal (E-031): the payload now persists
  `conversation_id` beside `persona_id`. Files written before
  E-035 have no such field and load as `default` — the
  namespace those turns always belonged to; a non-string field
  is corruption, judged like the persona field.

## Honest limits

- **The Brunnr adapters still do not persist the tag** — the
  same stated limit as `persona_id` (E-025): their schemas
  predate the tags, so a Well-loaded episode reads back as
  `default`/`default` and cross-restart history for a *named*
  conversation is not yet real. In-session separation, the
  prompt wall, and the journal are exact today; carrying both
  tags to storage belongs to Part V (E-080's persona migration
  road), and this slice does not pretend otherwise.
- **Retrieval grounding is shared, deliberately.** The Well's
  document chunks are the companion's library — the same
  bookshelf for every talk, as a person's is. Only remembered
  *turns* are conversation-private.
- There is no conversation listing/renaming UI yet; a
  conversation comes into being by being named, which matches
  how personae began at E-025.

## Fixtures

`tests/unit/test_conversation_isolation_e035.py` — two named
conversations (`kitchen`, `workshop`) plus the untagged past,
interleaved: slug rules, resolution order and refusal, exact
filtering, the adversarial prompt wall (a foreign episode whose
text is an instruction never reaches the prompt), persona ×
conversation composition, summary non-bleed, journal round-trip
and pre-E-035 payload shape, config coercion, chat wiring on
the Well road and the disconnected journal road, two sessions
on one Well staying apart, and the CLI flag.
