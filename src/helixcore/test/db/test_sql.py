# -*- coding: utf-8 -*-
import unittest

from helixcore.db.sql import Leaf, Eq, And, Or, Scoped, Any, NullLeaf, In, Select, Update, Delete, Insert


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

    def test_nested_select(self):
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

        in_cond = In('id', nested)
        c, p = in_cond.glue()
        self.assertEqual(c, '''"id" IN (SELECT "service_type_id" FROM "service_set" WHERE "service_set_descr_id" = (SELECT "name" FROM "service_set_descr" WHERE "name" = %s))''')
        self.assertEqual(p, ['registration ru'])

        any_cond = Any('id', nested)
        c, p = any_cond.glue()
        self.assertEqual(c, '''%s = ANY (SELECT "service_type_id" FROM "service_set" WHERE "service_set_descr_id" = (SELECT "name" FROM "service_set_descr" WHERE "name" = %s))''')
        self.assertEqual(p, ['registration ru'])


    def test_select(self):
        self.assertEqual('SELECT * FROM "billing"', Select('billing').glue()[0])
        self.assertEqual(
            'SELECT "id" FROM "billing"',
            Select('billing', columns='id').glue()[0]
        )
        self.assertEqual(
            'SELECT "id" FROM "billing"',
            Select('billing', columns=['id']).glue()[0]
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"',
            Select('billing', columns=['id', 'billing.amount']).glue()[0]
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"  GROUP BY "id","billing"."currency"',
            Select('billing', columns=['id', 'billing.amount'], group_by=['id', 'billing.currency']).glue()[0]
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"   ORDER BY "id" ASC,"billing"."amount" DESC',
            Select('billing', columns=['id', 'billing.amount'], order_by=['id', '-billing.amount']).glue()[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"    LIMIT 4',
            Select('billing', limit=4).glue()[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"    LIMIT 0',
            Select('billing', limit=0).glue()[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"   ORDER BY "id" ASC,"ammount" ASC LIMIT 5 OFFSET 6',
            Select('billing', order_by=['id', 'ammount'], limit=5, offset=6).glue()[0]
        )

        cond_and = And(
            Leaf('billing.amount', '>', 10),
            Leaf('billing.amount', '<', 100)
        )
        q_str, params = Select('billing', cond=cond_and).glue()
        self.assertEqual(
            'SELECT * FROM "billing" WHERE "billing"."amount" > %s AND "billing"."amount" < %s',
            q_str
        )
        self.assertEqual([10, 100], params)

        self.assertEqual(
            'SELECT * FROM "billing" WHERE "id" = %s     FOR UPDATE',
            Select('billing', cond=Eq('id', 5), for_update=True).glue()[0]
        )

    def test_update(self):
        q_str, q_params = Update('balance', {'client_id': 4}, Eq('id', 1)).glue()
        self.assertEqual(
            'UPDATE "balance" SET "client_id" = %s WHERE "id" = %s',
            q_str
        )
        self.assertEqual(q_params, [4, 1])

    def test_delete(self):
        q_str, q_params = Delete('balance_lock', Eq('balance_id', 7)).glue()
        self.assertEqual(
            'DELETE FROM "balance_lock" WHERE "balance_id" = %s',
            q_str
        )
        self.assertEqual([7], q_params)

        q_str, q_params = Delete('currency').glue()
        self.assertEqual('DELETE FROM "currency"', q_str)
        self.assertEqual([], q_params)

    def test_insert(self):
        q_str, q_params = Insert('balance', {'client_id': 42, 'amount': 0, 'currency': 'usd'}).glue()
        self.assertEqual(
            'INSERT INTO "balance" ("currency","amount","client_id") VALUES (%s,%s,%s) RETURNING id',
            q_str
        )
        self.assertEqual(['usd', 0, 42], q_params)


if __name__ == '__main__':
    unittest.main()
