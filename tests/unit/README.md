# tests/unit/

Single-module tests. Mirror the layout of `src/runa/` — a test for `src/runa/core/kernel.py` lives at `tests/unit/core/test_kernel.py`.

No network, no disk outside `tmp_path`, no real model calls, no real adapters. Anything outside the module under test is a fake.
