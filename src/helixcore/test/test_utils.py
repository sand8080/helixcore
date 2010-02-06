import unittest

from helixcore import utils

class UtilTestCase(unittest.TestCase):
    def test_filter_dict(self):
        self.assertEqual({'b': 4}, utils.filter_dict(('a', 'b'), {'b': 4, 'c': 5}))
        self.assertEqual({}, utils.filter_dict([], {'b': 4, 'c': 5}))
        self.assertEqual({}, utils.filter_dict(('z'), {'b': 4, 'c': 5}))


if __name__ == '__main__':
    unittest.main()