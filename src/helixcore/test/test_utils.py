import unittest

from helixcore import utils


class UtilTestCase(unittest.TestCase):
    def test_filter_dict(self):
        self.assertEqual({'b': 4}, utils.filter_dict(('a', 'b'), {'b': 4, 'c': 5}))
        self.assertEqual({}, utils.filter_dict([], {'b': 4, 'c': 5}))
        self.assertEqual({}, utils.filter_dict(('z'), {'b': 4, 'c': 5}))

    def test_filter_all_field_values(self):
        d = {
            't': 'l0',
            'some': None,
            'nested': {
                't': 'l1',
                'abc': 2,
                'def': {
                    't': 'l2',
                },
            },
            'no_t_dict': {'a': 1, 'b': 2},
        }
        self.assertEqual(sorted(('l0', 'l1', 'l2')), sorted(utils.filter_all_field_values('t', d)))
        d = {
            't': 'l0',
            'details': [
                {'t': 'l1-0'},
                {'t': 'l1-1'},
                {'b': 'c'},
                [
                    {'t': 'l2-0', 'n': 5},
                    'b'
                ],
            ],
            'tuple': ({'t': 'l1-2'}, 4, 5),
        }
        self.assertEqual(sorted(('l0', 'l1-0', 'l1-1', 'l1-2', 'l2-0')),
            sorted(utils.filter_all_field_values('t', d)))

        self.assertEqual((), utils.filter_all_field_values('t', 'siski'))
        self.assertEqual((), utils.filter_all_field_values('t', None))
        self.assertEqual((), utils.filter_all_field_values('t', 4))


if __name__ == '__main__':
    unittest.main()