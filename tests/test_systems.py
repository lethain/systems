"Test systems.py"
import unittest

from systems.errors import IllegalSourceStock
import systems.models
import systems.parse


class TestParse(unittest.TestCase):
    def test_stock_maximum_rate(self):
        m = systems.models.Model("Maximum")
        a = m.infinite_stock("a")
        b_max = 3
        b = m.stock("b", systems.models.Formula(0), systems.models.Formula(b_max))
        m.flow(a, b, systems.models.Rate(1))
        results = m.run()
        for i, result in enumerate(results):
            if i > b_max:
                self.assertEqual(b_max, result['b'])

    def test_illegal_conversion_leak_source(self):
        "You can't apply a Conversion or Leak to an infinite stock."
        m = systems.models.Model("Maximum")
        a = m.infinite_stock("a")
        b = m.stock("b")

        rates = [systems.models.Conversion(0.25), systems.models.Leak(0.25)]
        for rate in rates:
            with self.assertRaises(IllegalSourceStock):
                m.flow(a, b, rate)

    def test_infinite_destination_stock(self):
        "Should allow infinite stocks as destinations stock for all rates."
        rates = [systems.models.Rate(5), systems.models.Conversion(0.25), systems.models.Leak(0.25)]
        for rate in rates:
            m = systems.models.Model("Maximum")
            a = m.stock("a", systems.models.Formula("100"))
            b = m.infinite_stock("b")
            m.flow(a, b, rate)
            m.run(rounds=3)

    def test_stock_maximum_conversion(self):
        m = systems.models.Model("Maximum")
        a_initial = 10
        
        a = m.stock("a", systems.models.Formula(a_initial))
        b_max = 3
        b = m.stock("b", 0, systems.models.Formula(b_max))
        f_rate = 0.5

        m.flow(a, b, systems.models.Conversion(f_rate))
        results = m.run(rounds=3)
        final = results[-1]
        self.assertEqual(b_max, final['b'])

        # 10 - ((1 / 0.5) * 3) = 4
        a_expected = a_initial - ((1 / f_rate) * b_max)
        self.assertEqual(a_expected, final['a'])

    def test_stock_maximum_leak(self):
        m = systems.models.Model("Maximum")
        a_initial = 10
        a = m.stock("a", systems.models.Formula(a_initial))
        b_max = 3
        b = m.stock("b", systems.models.Formula(0), systems.models.Formula(b_max))
        m.flow(a, b, systems.models.Leak(0.5))
        results = m.run(rounds=2)
        final = results[-1]
        self.assertEqual(b_max, final['b'])
        self.assertEqual(a_initial - b_max, final['a'])

    def test_formula_rate(self):
        m = systems.models.Model("Maximum")
        a = m.infinite_stock("a")
        b = m.stock("b")
        c = m.stock("c")
        d = m.stock("d", systems.models.Formula(3))

        systems.parse.parse_flow(m, a, b, "d * 2")
        systems.parse.parse_flow(m, b, c, "d")

        results = m.run(rounds=3)

        print("\n" + m.render(results))
        
        final = results[-1]
        self.assertEqual(12, final['b'])
        self.assertEqual(6, final['c'])
