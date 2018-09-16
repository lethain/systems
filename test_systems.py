"Test systems.py"
import unittest

import systems


class TestParse(unittest.TestCase):
    def test_stock_maximum(self):
        m = systems.Model("Maximum")
        a = m.infinite_stock("a")
        b = m.stock("b", 0, 3)
        m.flow(a, b, systems.Rate(1))

        results = m.run()
