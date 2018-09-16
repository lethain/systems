"Test systems.py"
import unittest

import systems
from exceptions import IllegalSourceStock


class TestParse(unittest.TestCase):
    def test_stock_maximum_rate(self):
        m = systems.Model("Maximum")
        a = m.infinite_stock("a")
        b_max = 3
        b = m.stock("b", 0, b_max)
        m.flow(a, b, systems.Rate(1))
        results = m.run()
        for i, result in enumerate(results):
            if i > b_max:
                self.assertEqual(b_max, result['b'])

    def test_illegal_conversion_leak_source(self):
        "You can't apply a Conversion or Leak to an infinite stock."
        m = systems.Model("Maximum")
        a = m.infinite_stock("a")
        b = m.stock("b")

        rates = [systems.Conversion(0.25), systems.Leak(0.25)]
        for rate in rates:
            with self.assertRaises(IllegalSourceStock):
                m.flow(a, b, rate)

    def test_stock_maximum_conversion(self):
        m = systems.Model("Maximum")
        a = m.stock("a", 10)
        b_max = 3
        b = m.stock("b", 0, b_max)
        m.flow(a, b, systems.Conversion(0.5))
        results = m.run(rounds=1)
        final = results[-1]
        self.assertEqual(b_max, final['b'])

    def test_stock_maximum_leak(self):
        m = systems.Model("Maximum")
        a_initial = 10
        a = m.stock("a", a_initial)
        b_max = 3
        b = m.stock("b", 0, b_max)
        m.flow(a, b, systems.Leak(0.5))
        results = m.run(rounds=1)
        final = results[-1]
        self.assertEqual(b_max, final['b'])
        self.assertEqual(a_initial - b_max, final['a'])        
