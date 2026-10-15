# grafana-adapter

A single clock function returning a monotonic float with a stable epoch, plus a small wrapper class so tests can inject a fake clock.

```python
from grafana_adapter import monotonic_clock, Adapter

# Direct use
seconds = monotonic_clock()

# Or wrapped, so a test can pass its own clock
adapter = Adapter()
adapter.now()
```

## Why this exists

Grafana data-source code often needs a monotonic timestamp per emitted row, and hard-coding `time.perf_counter` at every call site makes the surrounding logic untestable without sleeping. This library provides one named function — `monotonic_clock` — and an `Adapter` class whose constructor accepts a `clock` callable. Production code uses the default; tests pass a generator returning predetermined values.

We chose `time.perf_counter` over `time.monotonic`. Both are monotonic on CPython, but `perf_counter` offers the higher-resolution clock and is the standard library's recommended choice for measuring short durations. The trade-off is that the epoch is unspecified and stable only within a single process — which is the only property that matters for relative-duration panels.

## Edge cases

`Adapter(clock=None)` (the default) calls `monotonic_clock()` lazily at each `now()` call. This means monkey-patching `time.perf_counter` in a test still takes effect, but if you want full determinism pass an explicit callable. The wrapper coerces integer return values to `float`; non-numeric returns propagate as a `TypeError` or `ValueError` from `float()`.
