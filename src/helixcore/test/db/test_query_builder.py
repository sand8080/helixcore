import unittest

from helixcore.db.cond import Leaf, Eq, And
from helixcore.db.query_builder import select, update, delete, insert

class QueryBuilderTestCase(unittest.TestCase):
    def test_select(self):
        self.assertEqual('SELECT * FROM "billing"', select('billing')[0])
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"',
            select('billing', columns=['id', 'billing.amount'])[0]
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"  GROUP BY "id","billing"."currency"',
            select('billing', columns=['id', 'billing.amount'], group_by=['id', 'billing.currency'])[0]
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"   ORDER BY "id" ASC,"billing"."amount" DESC',
            select('billing', columns=['id', 'billing.amount'], order_by=['id', '-billing.amount'])[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"    LIMIT 4',
            select('billing', limit=4)[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"    LIMIT 0',
            select('billing', limit=0)[0]
        )
        self.assertEqual(
            'SELECT * FROM "billing"   ORDER BY "id" ASC,"ammount" ASC LIMIT 5 OFFSET 6',
            select('billing', order_by=['id', 'ammount'], limit=5, offset=6)[0]
        )

        cond_and = And(
            Leaf('billing.amount', '>', 10),
            Leaf('billing.amount', '<', 100)
        )
        q_str, params = select('billing', cond=cond_and)
        self.assertEqual(
            'SELECT * FROM "billing" WHERE "billing"."amount" > %s AND "billing"."amount" < %s',
            q_str
        )
        self.assertEqual([10, 100], params)

        self.assertEqual(
            'SELECT * FROM "billing" WHERE "id" = %s     FOR UPDATE',
            select('billing', cond=Eq('id', 5), for_update=True)[0]
        )

    def test_update(self):
        q_str, q_params = update('balance', {'client_id': 4}, Eq('id', 1))
        self.assertEqual(
            'UPDATE "balance" SET "client_id" = %s WHERE "id" = %s',
            q_str
        )
        self.assertEqual(q_params, [4, 1])

    def test_delete(self):
        q_str, q_params = delete('balance_lock', Eq('balance_id', 7))
        self.assertEqual(
            'DELETE FROM "balance_lock" WHERE "balance_id" = %s',
            q_str
        )
        self.assertEqual([7], q_params)

        q_str, q_params = delete('currency')
        self.assertEqual('DELETE FROM "currency"', q_str)
        self.assertEqual([], q_params)

    def test_insert(self):
        q_str, q_params = insert('balance', {'client_id': 42, 'amount': 0, 'currency': 'usd'})
        self.assertEqual(
            'INSERT INTO "balance" ("currency","amount","client_id") VALUES (%s,%s,%s)',
            q_str
        )
        self.assertEqual(['usd', 0, 42], q_params)

if __name__ == '__main__':
    unittest.main()
