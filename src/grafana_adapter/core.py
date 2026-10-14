from __future__ import annotations

import time


def monotonic_clock() -> float:
    """Return a monotonically non-decreasing float seconds count.

    We prefer ``time.perf_counter`` over ``time.monotonic`` because both are
    monotonic on CPython, but ``perf_counter`` carries the stronger guarantee
    of the highest-resolution clock available on the platform. The epoch is
    unspecified and stable only within a single process — exactly the property
    a Grafana panel cares about when showing relative durations.
    """
    return float(time.perf_counter())


class Adapter:
    """Wrap a clock callable so callers can inject a fake in tests.

    Grafana data-source code frequently needs a monotonic timestamp for each
    row it emits. Hard-coding ``time.perf_counter`` into every call site makes
    the surrounding logic untestable without sleeping. This class lets the
    production path use the real clock and the test path pass a deterministic
    generator.
    """

    def __init__(self, clock: "Callable[[], float] | None" = None) -> None:
        # Default lazily so monkey-patching ``time.perf_counter`` in a test
        # still takes effect — but we also accept an explicit callable for
        # total determinism.
        self._clock = clock

    def now(self) -> float:
        """Return the current monotonic seconds from the configured clock."""
        if self._clock is not None:
            return float(self._clock())
        return monotonic_clock()
