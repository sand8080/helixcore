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


if __name__ == '__main__':
    unittest.main()
