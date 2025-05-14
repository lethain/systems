"Test parse.py"
import unittest

import systems.parse as parse
import systems.errors

# remove these explicit imports
from systems.errors import ParseError, UnknownFlowType, ConflictingValues, InvalidFormula

import systems.models


EXAMPLE_FULL = """
# ignore this comment
# ignore this comment too
[a] > b @ 25
b > c @ 0.5
c > d @ Leak(0.5)
d > [e] @ 1.0
"""

EXAMPLE_MAXIMUM = """
[a] > b @ 10
b(0, 5) > c(0, 10) @ 5
"""


class TestParse(unittest.TestCase):
    def test_parse(self):
        model = parse.parse(EXAMPLE_FULL)
        stock_names = ['a', 'b', 'c', 'd', 'e']
        values = {
            'a': float('+inf'),
            'b': 0,
            'e': float('+inf'),
        }
        for stock_name in stock_names:
            stock = model.get_stock(stock_name)
            self.assertIsNotNone(stock)
            self.assertEqual(stock_name, stock.name)
            if stock_name in values:
                value = values[stock_name]
                self.assertEqual(value, stock.initial.compute())

    def test_parse_complex_formula(self):
        spec = """[Hires] > Developers @ 1
        [Ideas] > Projects   @ Developers / (Projects+1)
        Projects > Started   @ Developers - (Started+1)
        Started > Finished   @ Developers"""
        model = parse.parse(spec)

        names = ['Hires', 'Developers', 'Ideas', 'Projects', 'Started', 'Finished']
        for name in names:
            self.assertEqual(name, model.get_stock(name).name)

        results = model.run(rounds=10)
        for row in results:
            for val in row.values():
                self.assertLessEqual(0, val)

    def test_maximums(self):
        model = parse.parse(EXAMPLE_MAXIMUM)
        results = model.run(rounds=4)
        final = results[-1]
        self.assertEqual(5, final['b'])
        self.assertEqual(10, final['c'])

    def test_parsing_infinity(self):
        txt = """
        pi_a(100, inf) > pi_b @ 10
        pi_b > [pi_c] @ 5
        """
        model = parse.parse(txt)
        results = model.run(rounds=5)
        final = results[-1]
        self.assertEqual(50, final['pi_a'])
        self.assertEqual(30, final['pi_b'])

    def test_parse_invalid_int_or_float(self):
        txt = """
        c > d @ 1
        d > e @ 3
        [a] > b @ hi

        """
        with self.assertRaises(InvalidFormula) as pe:
            m = parse.parse(txt)
            m.run()

    def test_circular_formula_dependency(self):
        txt = """
        A(D)
        B(A)
        C(B*3)
        D(C*B)
        """
        with self.assertRaises(systems.errors.CircularReferences):
            m = parse.parse(txt, tracebacks=False)
            m.run()

    def test_non_circular_formula_dependency(self):
        txt = """
        A(100)
        B(A)
        C(B*3)
        D(C*B)
        """
        m = parse.parse(txt)
        results = m.run()
        final = results[0]
        self.assertEqual(100, final['A'])
        self.assertEqual(100, final['B'])
        self.assertEqual(300, final['C'])
        self.assertEqual(30000, final['D'])

    def test_parens(self):
        txt = """
        A(5)
        B(10)
        C((A+B)/2)
        D((((A+A) * (B+B)) / A))
        """
        m = parse.parse(txt)
        results = m.run()
        final = results[0]
        self.assertEqual(5, final['A'])
        self.assertEqual(10, final['B'])
        self.assertEqual(7.5, final['C'])
        self.assertEqual(40, final['D'])

    def test_missing_parens(self):
        "There is a missing paren in the rate definition"
        txt = """
        [A]
        A > B @ Rate(1 * (1 + (1 * 1))
        """
        with self.assertRaises(systems.errors.MismatchedParens):
            m = parse.parse(txt)
            results = m.run()

    def test_conflicting_stock_values(self):
        txt = """
        a(10) > b @ 1
        b > a(5) @ 2
        """
        with self.assertRaises(ConflictingValues) as cv:
            m = parse.parse(txt, tracebacks=False)
        self.assertEqual('a', cv.exception.name)
        self.assertEqual(10, cv.exception.first.compute())
        self.assertEqual(5, cv.exception.second.compute())

    def test_standalone_stock(self):
        txt = """
        a
        b(2)
        c(3, 5)

        a > b @ 1
        b > c @ 2
        """
        m = parse.parse(txt)
        m.run()

        self.assertEqual(0, m.get_stock('a').initial.compute())
        self.assertEqual(2, m.get_stock('b').initial.compute())
        self.assertEqual(3, m.get_stock('c').initial.compute())
        self.assertEqual(5, m.get_stock('c').maximum.compute())


class TestParseStock(unittest.TestCase):
    "Test parsing stocks."

    def test_parse_stock(self):
        opts = [
            ("[a]", "a", float("+inf"), float("+inf")),
            ("b", "b", 0, float("+inf")),
            ("test_this", "test_this", 0, float("+inf")),
            ("  test ", "test", 0, float("+inf")),
            (" test", "test", 0, float("+inf")),
            ("test(0) ", "test", 0, float("+inf")),
            ("test(1) ", "test", 1, float("+inf")),
            ("test(200) ", "test", 200, float("+inf")),
            ("test(0, 10) ", "test", 0, 10),
            ("test(10, 10) ", "test", 10, 10),
            ("test(10, 20) ", "test", 10, 20)
        ]
        for txt, name, val, maximum in opts:
            m = systems.models.Model("TestParseStock")
            stock = parse.parse_stock(m, txt)
            self.assertEqual(name, stock.name)
            self.assertEqual(val, stock.initial.compute())
            self.assertEqual(maximum, stock.maximum.compute())

    def test_illegal_names(self):
        legal = ['A', 'a', 'Best', 'Hiring', 'a1', 'A0', 'A_1']
        illegal = ['1', '1a', 'a-', 'A-','A+', 'A 3']
        for name in legal:
            m = systems.models.Model("TestParseStock")
            stock = parse.parse_stock(m, name)

        for name in illegal:
            m = systems.models.Model("TestParseStock")
            with self.assertRaises(systems.errors.IllegalStockName):
                stock = parse.parse_stock(m, name)


class TestParseFlow(unittest.TestCase):
    "Test parsing flows."

    def test_parse_flow(self):
        opts = [
            ("1", "Rate", 1),
            ("Rate(1)", "Rate", 1),
            ("0.1", "Conversion", 0.1),
            ("Conversion(0.1)", "Conversion", 0.1),
            ("leak(0.1)", "Leak", 0.1),
        ]
        for txt, kind, value in opts:
            m = systems.models.Model("TestParseStock")
            source = m.stock("source")
            destination = m.stock("destination")
            flow = parse.parse_flow(m, source, destination, txt)
            self.assertEqual(kind, flow.rate.__class__.__name__)
            self.assertEqual(value, flow.rate.formula.compute())

    def test_parse_formula(self):
        opts = [
            ("Source * 2", "Rate"),
            ("Source * Source", "Rate"),
            ("Source + Source", "Rate"),
        ]
        for txt, kind in opts:
            m = systems.models.Model("TestParseStock")
            source = m.stock("source")
            destination = m.stock("destination")
            flow = parse.parse_flow(m, source, destination, txt)
            self.assertEqual(kind, flow.rate.__class__.__name__)

    def test_invalid_formulas(self):
        opts = [
            "+",
            "a * ",
            "* a",
            "1 3 4",
        ]
        for txt in opts:
            m = systems.models.Model("TestParseStock")
            source = m.stock("source")
            destination = m.stock("destination")
            with self.assertRaises(InvalidFormula):
                parse.parse_flow(m, source, destination, txt)

    def test_invalid_flows(self):
        m = systems.models.Model("TestParseStock")
        source = m.stock("source")
        destination = m.stock("destination")

        opts = [
            ("Fake(5)", UnknownFlowType),
            ("Fake(0.1)", UnknownFlowType),
        ]

        for txt, exception_class in opts:
            with self.assertRaises(exception_class):
                parse.parse_flow(m, source, destination, txt)


if __name__ == "__main__":
    unittest.main()
