# INTERFACE — `ember.spark.funi.ollama`

## Module purpose

Ollama-backed Funi runtime. The first-slice default; ships with
`phi3:mini` as the recommended model for Pi5-8GB hosts (see
`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` §3).

## Public entry points (shipped Phase 5, 2026-05-21)

- `ember.spark.funi.ollama.OllamaFuni` — concrete adapter implementing
  the `FuniHandle` Protocol. `runtime_kind = "ollama"`.
- `ember.spark.funi.ollama.open(config) -> OllamaFuni | Unavailable` —
  the entry that `ember.spark.funi.handle.open` dispatches to.

## HTTP surface used

- `POST {base_url}/api/chat` — completions, `stream=false`, role-tagged
  messages.
- `GET {base_url}/api/version` — open-time probe and `health()` probe.

Stdlib `urllib.request` only — **no `httpx` dependency**, matching the
shape Smiðja's `OllamaEmbedClient` uses.

## Message translation

Runtime-neutral `ContextItem`s are translated to Ollama messages:

| `ContextKind` | Becomes |
|---|---|
| `SYSTEM` | `{"role": "system", "content": item.text}` |
| `CHUNK` | `{"role": "system", "content": item.text}` (grounding, not history) |
| `EPISODE` | Parsed `_episode_text` shape → alternating `user`/`assistant`. Drops items the parser can't recognise. |

The operator's current input is always appended as the final
`{"role": "user", ...}` message.

## Failure semantics

- `open()` returns `Unavailable(reason=ENDPOINT_UNREACHABLE)` on probe
  failure. Never raises.
- `complete()` **always returns a `FuniReply`**. Mid-call URL errors,
  non-JSON bodies, error-payload responses, or missing message
  content yield `FuniReply(finish_reason=ERROR, text=...)` with an
  operator-readable explanation in the text.
- `complete(tools=[...])` returns `FuniReply(finish_reason=ERROR)`
  cleanly — tool use is reserved for a later slice.
- `health()` never raises; on probe failure it returns
  `FuniHealth(last_ok=<previous>)` (the timestamp of the last
  successful call, or `None` if there hasn't been one).

## Limitations (Phase 5)

- No streaming.
- No tool execution.
- `ram_use_bytes` always `None` (we don't poll Ollama's `/api/ps`).
- Default timeout 60 s per request; tune via the adapter's `timeout_s`
  constructor argument when needed.
