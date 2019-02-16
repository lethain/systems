"Test systems.py"
import unittest

from systems.errors import IllegalSourceStock
import systems.models
import systems.parse
import systems.lexer


class TestModels(unittest.TestCase):
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

    def test_stock_minimums(self):
        "Stocks should never dip below their minimum value."
        m = systems.models.Model("Minimum")
        a = m.stock("a", systems.models.Formula(2))
        b = m.stock("b", systems.models.Formula(0))
        m.flow(a,b, systems.models.Rate(1))
        results = m.run(rounds=5)
        final = results[-1]
        self.assertEqual(0, final['a'])
        self.assertEqual(2, final['b'])

    def test_stock_negative_flows(self):
        "Stocks should never dip below their minimum value."
        m = systems.models.Model("Minimum")
        c = m.stock("c", systems.models.Formula(2))
        a = m.stock("a", systems.models.Formula(5))
        b = m.stock("b", systems.models.Formula(0))
        m.flow(a,b, systems.models.Rate("c"))
        results = m.run(rounds=5)
        final = results[-1]
        self.assertEqual(1, final['a'])
        self.assertEqual(4, final['b'])

    def test_formula_rate(self):
        m = systems.models.Model("Maximum")
        a = m.infinite_stock("a")
        b = m.stock("b")
        c = m.stock("c")
        d = m.stock("d", systems.models.Formula(3))

        systems.parse.parse_flow(m, a, b, "d * 2")
        systems.parse.parse_flow(m, b, c, "d")

        results = m.run(rounds=3)
        final = results[-1]
        self.assertEqual(12, final['b'])
        self.assertEqual(6, final['c'])


class TestFormula(unittest.TestCase):
    def test_simple_formulas(self):
        cases = [
            ("0", 0),
            ("0.5", 0.5),
            ("100", 100),
            ("inf", float("+inf")),
        ]
        for case_in, case_out in cases:
            lexed = systems.lexer.lex_formula(case_in)
            formula = systems.models.Formula(lexed)
            self.assertEqual(case_out, formula.compute())

    def test_reference_formulas(self):
        state = {'a': 10, 'b': 5, 'c': 0}
        cases = [
            ("a", 10),
            ("b", 5),
            ("c", 0),
            ("a * 2", 20),
            ("b * 3", 15),
            ("c * 10", 0),
            ("2 * a", 20),
            ("3 * b", 15),
            ("10 * c", 0),
            ("b * a", 50),
            ("a * b", 50),
            ("b * b", 25),
            ("c * a", 0),
        ]
        for case_in, case_out in cases:
            lexed = systems.lexer.lex_formula(case_in)
            formula = systems.models.Formula(lexed)
            self.assertEqual(case_out, formula.compute(state))
