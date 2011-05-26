import unittest
from datetime import datetime

from helixcore.test.test_environment import transaction

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.sql import Eq, Insert
from helixcore.mapping.objects import Mapped
from helixcore import mapping
import cjson


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

    def test_serialize_field(self):
        d = {'one': 'value', 'info': ['one', 'two']}
        d_res = mapping.objects.serialize_field(d, 'info', 'sz_info')
        self.assertEquals(d['one'], d_res['one'])
        self.assertFalse('info' in d_res)
        self.assertEquals(cjson.encode(d['info']), d_res['sz_info'])

        info = {'d_one': 'd_val', 'd_two': ['d_vval']}
        d = {'one': 'value', 'info': info}
        d_res = mapping.objects.serialize_field(d, 'info', 'sz_info')
        self.assertEquals(d['one'], d_res['one'])
        self.assertFalse('info' in d_res)
        self.assertEquals(cjson.encode(info), d_res['sz_info'])

    def test_deserialize_field(self):
        info = {'a': [1, 2, 3], 'b': 'value'}
        d = {'one': 'value', 'sz_info': cjson.encode(info)}
        d_res = mapping.objects.deserialize_field(d, 'sz_info', 'info')
        self.assertEquals(d['one'], d_res['one'])
        self.assertFalse('sz_info' in d_res)
        self.assertEquals(info, d_res['info'])


if __name__ == '__main__':
    unittest.main()
