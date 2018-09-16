"Test systems.py"
import unittest

import systems


class TestParse(unittest.TestCase):
    def test_stock_maximum(self):
        m = systems.Model("Maximum")
        a = m.infinite_stock("a")
        b_max = 3
        b = m.stock("b", 0, b_max)
        m.flow(a, b, systems.Rate(1))
        results = m.run()
        for i, result in enumerate(results):
            if i > b_max:
                self.assertEqual(b_max, result['b'])
