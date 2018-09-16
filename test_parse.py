"Test parse.py"
import unittest

import systems
import parse

from exceptions import ParseError, MissingDelimiter, UnknownFlowType, ConflictingValues, InitialExceedsMaximum, InitialIsNegative


EXAMPLE_FULL = """
[a] > b @ 25
b > c @ 0.5
c > d @ 0.5, leak
d > [e] @ 1.0
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
                self.assertEqual(value, stock.initial)

    def test_parse_missing_delim(self):
        txt = "[a] < b @ 25"
        with self.assertRaises(MissingDelimiter) as md:
            parse.parse(txt)
        self.assertEqual('>', md.exception.delimiter)

        txt = "[a] > b"
        with self.assertRaises(MissingDelimiter) as md:
            parse.parse(txt)
        self.assertEqual('@', md.exception.delimiter)

    def test_parse_invalid_int_or_float(self):
        txt = """
        c > d @ 1
        d > e @ 3
        [a] > b @ hi

        """
        with self.assertRaises(ParseError) as pe:
            m = parse.parse(txt)
        self.assertEqual(4, pe.exception.line_number)

    def test_conflicting_stock_values(self):
        txt = """
        a(10) > b @ 1
        b > a(5) @ 2
        """
        with self.assertRaises(ConflictingValues) as cv:
            m = parse.parse(txt)
        self.assertEqual('a', cv.exception.name)
        self.assertEqual(10, cv.exception.first)
        self.assertEqual(5, cv.exception.second)


class TestParseStock(unittest.TestCase):
    "Test parsing stocks."

    def test_parse_stock(self):
        opts = [
            ("[a]", "a", float("+inf"), float("+inf")),
            ("b", "b", 0, float("+inf")),
            ("[b", "[b", 0, float("+inf")),
            ("test this", "test this", 0, float("+inf")),
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
            m = systems.Model("TestParseStock")
            stock = parse.parse_stock(m, txt)
            self.assertEqual(name, stock.name)
            self.assertEqual(val, stock.initial)
            self.assertEqual(maximum, stock.maximum)

    def test_illegal_maximums(self):
        with self.assertRaises(InitialExceedsMaximum):
            txt = "test(20, 10)"
            m = systems.Model("TestParseStock")
            stock = parse.parse_stock(m, txt)

        with self.assertRaises(InitialIsNegative):
            txt = "test(-5, 5)"
            m = systems.Model("TestParseStock")
            stock = parse.parse_stock(m, txt)


class TestParseFlow(unittest.TestCase):
    "Test parsing flows."

    def test_parse_flow(self):
        m = systems.Model("TestParseStock")
        source = m.stock("source")
        destination = m.stock("destination")

        opts = [
            ("1", "Rate", 1),
            ("0.1", "Conversion", 0.1),
            (".1", "Conversion", 0.1),
            (".1, leak", "Leak", 0.1),
        ]

    def test_invalid_flows(self):
        m = systems.Model("TestParseStock")
        source = m.stock("source")
        destination = m.stock("destination")

        opts = [
            ("0..1", ParseError),
            ("hello", ParseError),
            ("0.1, fake", UnknownFlowType),
        ]

        for txt, exception_class in opts:
            with self.assertRaises(exception_class):
                parse.parse_flow(m, source, destination, txt)


if __name__ == "__main__":
    unittest.main()
