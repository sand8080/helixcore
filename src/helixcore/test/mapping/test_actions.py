import unittest
from datetime import datetime

from helixcore.db.wrapper import transaction, EmptyResultSetError
from helixcore.db.query_builder import insert
from helixcore.db.cond import Eq
from helixcore.mapping.objects import Mapped
from helixcore.mapping import actions

from helixcore.test.helpers import transaction

class ActionsTestCase(unittest.TestCase):
    class T(Mapped):
        __slots__ = ['id', 'name', 'date']
        table = 'test_actions'

    @transaction()
    def do_setUp(self, curs=None):
        curs.execute('DROP TABLE IF EXISTS %s' % self.T.table)
        curs.execute('CREATE TABLE %s (id serial, PRIMARY KEY (id), name varchar, date timestamp)' % self.T.table)
        for i in range(10):
            curs.execute(*insert(self.T.table, {'name': '%d' % i, 'date': datetime.now()}))

    def setUp(self):
        self.do_setUp()

    @transaction()
    def test_get(self, curs=None):
        obj = actions.get(curs, self.T, cond=Eq('id', 2))
        self.assertEqual(2, obj.id)
        self.assertEqual('1', obj.name)

    @transaction()
    def test_insert_with_id(self, curs=None):
        obj = self.T(id=1, name='n', date=datetime.now())
        self.assertRaises(actions.MappingError, actions.insert, curs, obj)

    @transaction()
    def test_insert(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        actions.insert(curs, obj)

    @transaction()
    def test_double_insert(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        actions.insert(curs, obj)
        self.assertRaises(actions.MappingError, actions.insert, curs, obj)

    @transaction()
    def test_update_without_id(self, curs=None):
        obj = self.T(name='n', date=datetime.now())
        self.assertRaises(actions.MappingError, actions.update, curs, obj)

    @transaction()
    def test_update(self, curs=None):
        obj = actions.get(curs, self.T, cond=Eq('id', 1))
        obj.name = 'mamba'
        actions.update(curs, obj)
        new_obj = actions.get(curs, self.T, cond=Eq('id', 1))
        self.assertEqual(obj.name, new_obj.name)

    @transaction()
    def test_delete(self, curs=None):
        obj = actions.get(curs, self.T, cond=Eq('id', 1))
        actions.delete(curs, obj)
        self.assertFalse(hasattr(obj, 'id'))
        self.assertRaises(EmptyResultSetError, actions.get, curs, self.T, cond=Eq('id', 1))

    @transaction()
    def test_double_delete(self, curs=None):
        obj = actions.get(curs, self.T, cond=Eq('id', 1))
        actions.delete(curs, obj)
        self.assertRaises(actions.MappingError, actions.delete, curs, obj)

if __name__ == '__main__':
    unittest.main()
