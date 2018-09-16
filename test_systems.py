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

    def test_infinite_destination_stock(self):
        "Should allow infinite stocks as destinations stock for all rates."
        rates = [systems.Rate(5), systems.Conversion(0.25), systems.Leak(0.25)]
        for rate in rates:
            m = systems.Model("Maximum")            
            a = m.stock("a", 100)
            b = m.infinite_stock("b")
            m.flow(a, b, rate)
            m.run(rounds=3)
                
    def test_stock_maximum_conversion(self):
        m = systems.Model("Maximum")
        a_initial = 10
        a = m.stock("a", a_initial)
        b_max = 3
        b = m.stock("b", 0, b_max)
        f_rate = 0.5

        m.flow(a, b, systems.Conversion(f_rate))
        results = m.run(rounds=3)
        final = results[-1]
        self.assertEqual(b_max, final['b'])

        # 10 - ((1 / 0.5) * 3) = 4
        a_expected = a_initial - ((1 / f_rate) * b_max)
        self.assertEqual(a_expected, final['a'])

    def test_stock_maximum_leak(self):
        m = systems.Model("Maximum")
        a_initial = 10
        a = m.stock("a", a_initial)
        b_max = 3
        b = m.stock("b", 0, b_max)
        m.flow(a, b, systems.Leak(0.5))
        results = m.run(rounds=2)
        final = results[-1]
        self.assertEqual(b_max, final['b'])
        self.assertEqual(a_initial - b_max, final['a'])
