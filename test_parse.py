"Test parse.py"
import unittest

import systems


class TestParse(unittest.TestCase):
    def test_a(self):
        self.assertEqual(1, 1)

    def test_b(self):
        self.assertEqual(1, 2)        


if __name__ == "__main__":
    unittest.main()
