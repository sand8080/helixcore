import unittest

from helixcore.db import filters


class FiltersTestCase(unittest.TestCase):
    class A(object):
        __slots__ = ['id', 'one']

        def __init__(self, id, one):
            self.id = id
            self.one = one

    def test_build_index(self):
        objs = [self.A(1, '1'), self.A(2, '2')]
        objs_idx = filters.build_index(objs)
        self.assertEquals([1, 2], sorted(objs_idx.keys()))

    def test_build_complex_index(self):
        objs = [self.A(1, '1'), self.A(2, '2')]
        objs_idx = filters.build_complex_index(objs, ('id', 'one'))
        self.assertTrue(2, len(objs_idx))
        self.assertTrue('1_1' in objs_idx)
        self.assertTrue('2_2' in objs_idx)

    def test_build_dicts_index(self):
        dicts = [{'id': 1, 'cd': 2}, {'id': 2, 'cd': 3}]
        dicts_idx = filters.build_dicts_index(dicts)
        self.assertEquals([1, 2], sorted(dicts_idx.keys()))


if __name__ == '__main__':
    unittest.main()
