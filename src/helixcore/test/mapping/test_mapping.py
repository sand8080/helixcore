import unittest
from datetime import datetime

from helixcore.test.test_environment import transaction

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.sql import Eq, Insert
from helixcore.mapping.objects import Mapped
from helixcore import mapping


class MappingTestCase(unittest.TestCase):
    class T(Mapped):
        __slots__ = ['id', 'name', 'date']
        table = 'test_actions'

    @transaction()
    def do_setUp(self, curs=None):
        curs.execute('DROP TABLE IF EXISTS %s' % self.T.table)
        curs.execute('CREATE TABLE %s (id serial, PRIMARY KEY (id), name varchar, date timestamp)' % self.T.table)
        for i in range(10):
            q = Insert(self.T.table, {'name': '%d' % i, 'date': datetime.now()})
            curs.execute(*q.glue())

    def setUp(self):
        self.do_setUp()

    @transaction()
    def test_get(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 2))
        self.assertEqual(2, obj.id)
        self.assertEqual('1', obj.name)

    @transaction()
    def test_insert_with_id(self, curs=None):
        obj = self.T(id=1, name='n', date=datetime.now())
        self.assertRaises(mapping.ObjectCreationError, mapping.insert, curs, obj)

    @transaction()
    def test_insert(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        mapping.insert(curs, obj)

    @transaction()
    def test_double_insert(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        mapping.insert(curs, obj)
        self.assertRaises(mapping.ObjectCreationError, mapping.insert, curs, obj)

    @transaction()
    def test_update_without_id(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        self.assertRaises(mapping.MappingError, mapping.update, curs, obj)

    @transaction()
    def test_update(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        obj.name = 'mamba'
        mapping.update(curs, obj)
        new_obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        self.assertEqual(obj.name, new_obj.name)

    @transaction()
    def test_delete(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        mapping.delete(curs, obj)
        self.assertFalse(hasattr(obj, 'id'))
        self.assertRaises(EmptyResultSetError, mapping.get, curs, self.T, cond=Eq('id', 1))

    @transaction()
    def test_double_delete(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        mapping.delete(curs, obj)
        self.assertRaises(mapping.MappingError, mapping.delete, curs, obj)

if __name__ == '__main__':
    unittest.main()
