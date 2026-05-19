# tests/e2e/

End-to-end tests through the real `runa` CLI or the real gateway HTTP surface. Slowest tier.

Carry the `e2e` pytest marker. Excluded from the default test run; opt in with `pytest -m e2e`.

May touch a real local model (Ollama / LM Studio) when one is available and configured; skip cleanly when not.
