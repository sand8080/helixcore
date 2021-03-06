import unittest

from helixcore.db.sql import Eq, Any, Insert
from helixcore.mapping.objects import Mapped
from helixcore import mapping

from helixcore.test.test_environment import transaction


class ArraysTestCase(unittest.TestCase):
    class T(Mapped):
        __slots__ = ['id', 'name', 'client_ids']
        table = 'test_arrays'

    @transaction()
    def do_setUp(self, curs=None):
        curs.execute('DROP TABLE IF EXISTS %s' % self.T.table)
        curs.execute('CREATE TABLE %s (id serial, PRIMARY KEY (id), name varchar, client_ids integer[])' % self.T.table)
        for i in xrange(10):
            values = [j for j in xrange(i, i + 3)]
            q = Insert(self.T.table, {'name': '%d' % i, 'client_ids': values})
            curs.execute(*q.glue())

    def setUp(self):
        self.do_setUp()

    @transaction()
    def test_insert(self, curs=None):
        obj = self.T(name='boh0', client_ids=[4,6,4])
        mapping.insert(curs, obj)

    @transaction()
    def test_get(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        self.assertEqual(1, obj.id)
        self.assertEqual('0', obj.name)
        self.assertEqual([0, 1, 2], obj.client_ids)

        obj.client_ids = [1, 1, 1]
        mapping.update(curs, obj)

        objs = mapping.get_list(curs, self.T, cond=Any(1, 'client_ids'), order_by='id')
        self.assertEqual(2, len(objs))
        self.assertEqual(1, objs[0].id)
        self.assertEqual(2, objs[1].id)

    @transaction()
    def test_update(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        obj.name = 'mamba'
        obj.client_ids = [44, 23]
        mapping.update(curs, obj)
        new_obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        self.assertEqual(obj.name, new_obj.name)
        self.assertEqual(obj.client_ids, new_obj.client_ids)


if __name__ == '__main__':
    unittest.main()
