# -*- coding: utf-8 -*-
import unittest

from helixcore.db.sql import Leaf, Eq, And, Or, Scoped, Any, NullLeaf, In, Select


class SqlTestCase(unittest.TestCase):
    def test_cond(self):
        c, p = Leaf('billing.id', '<', 0).glue()
        self.assertEqual('"billing"."id" < %s', c)
        self.assertEqual(1, len(p))
        self.assertEqual([0], p)

        test_str = 'хитрый cat'
        c, p = Leaf('balance.name', '!=', test_str).glue()
        self.assertEqual('"balance"."name" != %s', c)
        self.assertEqual([test_str], p)

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

    def test_null_leaf(self):
        cond_and = And(NullLeaf(), Eq('a', 'b'))
        c, p = cond_and.glue()
        self.assertEqual('"a" = %s', c)
        self.assertEqual(['b'], p)

        cond_and = And(Eq('c', 'd'), NullLeaf())
        c, p = cond_and.glue()
        self.assertEqual('"c" = %s', c)
        self.assertEqual(['d'], p)

        cond_and = And(NullLeaf(), NullLeaf())
        c, p = cond_and.glue()
        self.assertEqual('', c)
        self.assertEqual([], p)

        cond_and = And(Eq('c', 'd'), NullLeaf())
        cond_or = Or(Eq('e', 'f'), cond_and)
        c, p = cond_or.glue()
        self.assertEqual('"e" = %s OR "c" = %s', c)
        self.assertEqual(['f', 'd'], p)

    def test_any_cond(self):
        cond_any = Any(15, 'ids')
        c, p = cond_any.glue()
        self.assertEqual(c, '%s = ANY (ids)')
        self.assertEqual(p, [15])

    def test_in_cond(self):
        cond_in = In('name', ['one', 2, 'three'])
        c, p = cond_in.glue()
        self.assertEqual(c, '"name" IN (%s,%s,%s)')
        self.assertEqual(p, ['one', 2, 'three'])

    def test_select_query(self):
        nested = Select('service_set_descr', columns=['name'], cond=Eq('name', 'registration ru'))
        c, p = nested.glue()
        self.assertEqual(c, 'SELECT "name" FROM "service_set_descr" WHERE "name" = %s')
        self.assertEqual(p, ['registration ru'])

        scoped_cond = Scoped(nested)
        c, p = scoped_cond.glue()
        self.assertEqual(c, '(SELECT "name" FROM "service_set_descr" WHERE "name" = %s)')
        self.assertEqual(p, ['registration ru'])

        cond_eq = Eq('service_set_descr_id', Scoped(nested))
        c, p = cond_eq.glue()
        self.assertEqual(c, '"service_set_descr_id" = (SELECT "name" FROM "service_set_descr" WHERE "name" = %s)')
        self.assertEqual(p, ['registration ru'])

        nested = Select('service_set', columns=['service_type_id'], cond=cond_eq)
        c, p = nested.glue()
        self.assertEqual(c, 'SELECT "service_type_id" FROM "service_set" WHERE "service_set_descr_id" = (SELECT "name" FROM "service_set_descr" WHERE "name" = %s)')
        self.assertEqual(p, ['registration ru'])


if __name__ == '__main__':
    unittest.main()
