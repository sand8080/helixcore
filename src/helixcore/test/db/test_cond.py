# -*- coding: utf-8 -*-
import unittest

from helixcore.db.cond import Leaf, Eq, And, Or, Scoped

class CondTestCase(unittest.TestCase):
    def test_cond(self):
        (cond, params) = Leaf('billing.id', '<', 0).glue()
        self.assertEqual('"billing"."id" < %s', cond)
        self.assertEqual(1, len(params))
        self.assertEqual(params, [0])

        test_str = 'хитрый cat'
        (cond, params) = Leaf('balance.name', '!=', test_str).glue()
        self.assertEqual('"balance"."name" != %s', cond)
        self.assertEqual(params, [test_str])

    def test_eq_cond(self):
        cond_end = Eq('billing.id', 0)
        (cond, params) = cond_end.glue()
        self.assertEqual('"billing"."id" = %s', cond)
        self.assertEqual(params, [0])

    def test_and_cond(self):
        cond_lh = Leaf('billing.id', '=', 0)
        cond_rh = Leaf('billing.id', '!=', 42)
        cond_end = And(cond_lh, cond_rh)
        (cond, params) = cond_end.glue()
        self.assertEqual(
            '"billing"."id" = %s AND "billing"."id" != %s',
            cond
        )
        self.assertEqual([0, 42], params)

    def test_or_cond(self):
        cond_lh = Leaf('billing.id', '=', 0)
        cond_rh = Leaf('billing.cd', '!=', 101)
        cond_end = Or(cond_lh, cond_rh)
        (cond, params) = cond_end.glue()
        self.assertEqual(
            '"billing"."id" = %s OR "billing"."cd" != %s',
            cond
        )
        self.assertEqual([0, 101], params)

    def test_scoped_cond(self):
        cond_lh = Leaf('billing.id', '=', 'a')
        cond_rh = Leaf('billing.cd', '!=', 'b')
        cond_and = And(cond_lh, cond_rh)
        cond_end = Scoped(cond_and)
        (cond, params) = cond_end.glue()
        self.assertEqual(
            '("billing"."id" = %s AND "billing"."cd" != %s)',
            cond
        )
        self.assertEqual(['a', 'b'], params)

if __name__ == '__main__':
    unittest.main()
