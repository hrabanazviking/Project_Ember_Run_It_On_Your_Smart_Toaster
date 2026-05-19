# 40 — C Extensions, Cython, Rust via PyO3 / maturin

**Category:** Performance
**Runa relevance:** rare-but-load-bearing hot paths, embedding compute, future Heimskringla optimisations
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Pure Python has fundamental performance limits — the interpreter overhead, the GIL, the dynamic dispatch on every operation. For CPU-bound hot paths, dropping to compiled code can be 10-1000× faster. Python's ecosystem supports this through several paths: **C extension modules** (oldest, fastest, hardest), **Cython** (Python-like syntax, compiled), **PyO3 + maturin** (Rust, increasingly popular), and **cffi / ctypes** (call existing C from Python).

For Runa, the rule is: stay in Python until a profile demands otherwise. When it does, Rust via PyO3 is the modern default — memory-safe, fast, growing ecosystem, well-tooled. Heimskringla's embedding-heavy paths, Muninn's vector-similarity inner loops, anything CPU-bound that profiling identifies — those are PyO3 candidates.

## 2. Technique / mechanism

**Paths to compiled code:**

| Path | Strength | Cost |
|---|---|---|
| **CPython C API** | Maximum performance; full control | Steep learning curve; manual refcounts |
| **Cython** | Python-like syntax; significant speedup | Cython-specific syntax to learn |
| **PyO3 + maturin (Rust)** | Memory-safe; modern; great tooling | Need to know Rust |
| **cffi / ctypes** | Call existing C libraries | Just bindings, no own logic |
| **numba** | JIT-compiled NumPy-style Python | Specific to numeric workloads |

**Cython sketch:**

```python
# fast_module.pyx
cdef int compute(int x, int y):
    return x * y + 7

def fast_compute(int x, int y) -> int:
    return compute(x, y)
```

Build via `setup.py` with `cythonize`. Imports as a normal Python module; calls are ~30-100× faster than pure Python for math.

**PyO3 + maturin (Rust):**

```toml
# Cargo.toml
[package]
name = "runa_core"
version = "0.1.0"

[lib]
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
```

```rust
// src/lib.rs
use pyo3::prelude::*;

#[pyfunction]
fn fast_compute(x: i64, y: i64) -> i64 {
    x * y + 7
}

#[pymodule]
fn runa_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fast_compute, m)?)?;
    Ok(())
}
```

Build via `maturin develop` (creates a wheel and installs to current env). Import as `runa_core` from Python.

**ctypes for existing C:**

```python
import ctypes

lib = ctypes.CDLL("./mylib.so")
lib.compute.argtypes = [ctypes.c_int, ctypes.c_int]
lib.compute.restype = ctypes.c_int

result = lib.compute(3, 4)
```

Suitable for calling existing C libraries without writing wrappers in C.

**cffi for cleaner C bindings:**

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("int compute(int x, int y);")
lib = ffi.dlopen("./mylib.so")

result = lib.compute(3, 4)
```

`cffi` parses C headers; cleaner than ctypes for non-trivial bindings.

**numba for numeric hot paths:**

```python
from numba import jit

@jit(nopython=True)
def fast_loop(arr):
    total = 0.0
    for x in arr:
        total += x ** 2
    return total
```

`@jit(nopython=True)` compiles the function on first call. Subsequent calls are near-C speed. Restricted to a subset of Python.

**Release the GIL in extensions:**

C/Rust extensions can release the GIL during work. Multiple Python threads then run in true parallel.

```rust
#[pyfunction]
fn heavy_work(py: Python, data: Vec<f64>) -> f64 {
    py.allow_threads(|| {
        // GIL released here — other Python threads can run
        compute_heavy(data)
    })
}
```

This is how libraries like numpy and Pillow get parallel performance from Python threads.

**Numpy / scipy as a "compiled-Python" path:**

Most heavy numerical work in Python uses numpy, which is C+SIMD under the hood. A numpy operation is *not* pure Python — it's a vectorised C op. If your hot path can be expressed as numpy operations, you're already mostly there.

```python
import numpy as np

def cosine_similarity(a, b):
    # Pure Python: slow
    # NumPy: ~100× faster, no compilation needed
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

## 3. Key works / libraries

- **Python C API** — docs.python.org/3/c-api/.
- **Cython** — cython.org.
- **PyO3** — pyo3.rs.
- **maturin** — github.com/PyO3/maturin.
- **cffi** — cffi.readthedocs.io.
- **ctypes** — stdlib.
- **numba** — numba.pydata.org.
- **numpy** — numpy.org.
- **cytypes (mypyc)** — mypyc.readthedocs.io. Compile typed Python to C.
- **PEP 489** — multi-phase initialization for extensions.

## 4. Pitfalls and gotchas

- **Premature optimisation.** Don't drop to compiled code without profiling. Pure Python is faster to debug.
- **Build complexity.** Compiled extensions need wheels per (Python version × OS × architecture). maturin / cibuildwheel help.
- **Pi (aarch64) builds.** Make sure your build setup produces ARM wheels. Pi 5 specifically.
- **C-extension refcount bugs.** Manual reference counting in C API is a source of subtle bugs. Rust + PyO3 mostly avoids this.
- **GIL release without thread safety.** Releasing the GIL in C is allowed; if Python state is touched without re-acquiring, crash.
- **Cython syntax drift.** Cython evolves; old Cython files may need updates.
- **Type stub files (`.pyi`)** for extensions. mypy needs them; write them.
- **Cross-compilation.** Compiling for Pi from x86 takes setup.

## 5. Applicability to Runa

For **default**: pure Python everywhere. Compiled code is the exception.

For **Heimskringla embedding compute** (if profile justifies):

- Embeddings are already in numpy via sentence-transformers / model libraries. No further work needed for typical hot paths.

For **Muninn vector-similarity**:

- sqlite-vss / sqlite-vec do the heavy work in C. Pure-Python loops over results are fine.

For **custom hot paths** (only when profiled):

- Rust + PyO3. Compile to wheel; ship in the deploy pipeline.

For **C-library bindings**:

- If we ever need to wrap a C library (e.g., a custom audio codec), `cffi` over `ctypes` for cleaner bindings.

For **deploy/pi/**:

- Pi 5 (aarch64) wheels need to be built either natively on Pi or cross-compiled. Document in deploy/pi/.

What to avoid:

- Don't compile without profiling.
- Don't write C extensions if Rust + PyO3 will do.
- Don't use Cython for new code without good reason — Rust is more memory-safe.
- Don't ship a wheel per platform if you can ship one universal wheel.

## 6. Open questions

- **PyO3 maturity on aarch64.** Generally good; verify per project.
- **mypyc adoption.** Compiling typed Python is appealing; mypyc usage thin.
- **Free-threaded Python.** Once stable, compiled extensions need extra discipline. Watch.

## 7. References (curated)

- pyo3.rs — PyO3 book.
- cython.org.
- numba.pydata.org.
- cffi.readthedocs.io.
- mypyc.readthedocs.io.
- realpython.com/python-bindings-overview/.
- Companion docs: [[20-thread-safety-python]], [[36-profiling-python]], [[37-memory-profiling]].
