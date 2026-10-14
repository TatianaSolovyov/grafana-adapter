import unittest

from grafana_adapter import monotonic_clock, Adapter


class TestModuleLevel(unittest.TestCase):
    def test_monotonic_clock_returns_float(self):
        value = monotonic_clock()
        self.assertIsInstance(value, float)

    def test_monotonic_clock_is_non_decreasing(self):
        first = monotonic_clock()
        second = monotonic_clock()
        self.assertGreaterEqual(second, first)


class TestAdapter(unittest.TestCase):
    def test_default_uses_real_clock(self):
        adapter = Adapter()
        value = adapter.now()
        self.assertIsInstance(value, float)

    def test_explicit_clock_is_used(self):
        state = {"ticks": [1.0, 2.5, 3.0]}

        def fake_clock():
            return state["ticks"].pop(0)

        adapter = Adapter(clock=fake_clock)
        self.assertEqual(adapter.now(), 1.0)
        self.assertEqual(adapter.now(), 2.5)
        self.assertEqual(adapter.now(), 3.0)

    def test_clock_returning_int_is_coerced_to_float(self):
        adapter = Adapter(clock=lambda: 7)
        result = adapter.now()
        self.assertIsInstance(result, float)
        self.assertEqual(result, 7.0)

    def test_clock_returning_string_raises(self):
        adapter = Adapter(clock=lambda: "not a number")
        with self.assertRaises((ValueError, TypeError)):
            adapter.now()

    def test_none_clock_falls_back_to_real(self):
        adapter = Adapter(clock=None)
        first = adapter.now()
        second = adapter.now()
        self.assertGreaterEqual(second, first)

    def test_multiple_adapters_are_independent(self):
        a = Adapter(clock=lambda: 10.0)
        b = Adapter(clock=lambda: 20.0)
        self.assertEqual(a.now(), 10.0)
        self.assertEqual(b.now(), 20.0)
        self.assertEqual(a.now(), 10.0)
        self.assertEqual(b.now(), 20.0)


if __name__ == "__main__":
    unittest.main()
