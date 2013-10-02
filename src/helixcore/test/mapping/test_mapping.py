import unittest
from datetime import datetime
import json
from helixcore.test.db import create_table, fill_table, drop_table

from helixcore.test.test_environment import transaction

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.sql import Eq, Insert
from helixcore.mapping.objects import Mapped
from helixcore import mapping


class MappingTestCase(unittest.TestCase):
    class T(Mapped):
        __slots__ = ['id', 'name', 'date_field']
        table = 'test_actions'

    def setUp(self):
        create_table(self.T.table)
        fill_table(self.T.table)

    def tearDown(self):
        drop_table(self.T.table)

    @transaction()
    def test_get(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 2))
        self.assertEqual(2, obj.id)
        self.assertEqual('1', obj.name)

    @transaction()
    def test_insert_with_id(self, curs=None):
        obj = self.T(id=1, name='n', date_field=datetime.now())
        self.assertRaises(mapping.ObjectCreationError, mapping.insert, curs, obj)

    @transaction()
    def test_insert(self, curs=None):
        obj = self.T(name='n', date_field=datetime.now())
        mapping.insert(curs, obj)
        ins_obj = mapping.get(curs, self.T, cond=Eq('id', obj.id))
        self.assertEquals(obj.id, ins_obj.id)
        self.assertEquals(obj.name, ins_obj.name)

    @transaction()
    def test_double_insert(self, curs=None):
        obj = self.T(name='n', date_field=datetime.now())
        mapping.insert(curs, obj)
        self.assertRaises(mapping.ObjectCreationError, mapping.insert, curs, obj)

    @transaction()
    def test_update_without_id(self, curs=None):
        obj = self.T(name='n', date_field=datetime.now())
        self.assertRaises(mapping.MappingError, mapping.update, curs, obj)

    @transaction()
    def test_update(self, curs=None):
        obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        obj.name = 'updated_%s' % obj.name
        mapping.update(curs, obj)
        upd_obj = mapping.get(curs, self.T, cond=Eq('id', 1))
        self.assertEqual(obj.id, upd_obj.id)
        self.assertEqual(obj.name, upd_obj.name)

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
        self.assertEquals(json.dumps(d['info']), d_res['sz_info'])

        info = {'d_one': 'd_val', 'd_two': ['d_vval']}
        d = {'one': 'value', 'info': info}
        d_res = mapping.objects.serialize_field(d, 'info', 'sz_info')
        self.assertEquals(d['one'], d_res['one'])
        self.assertFalse('info' in d_res)
        self.assertEquals(json.dumps(info), d_res['sz_info'])

    def test_deserialize_field(self):
        info = {'a': [1, 2, 3], 'b': 'value'}
        d = {'one': 'value', 'sz_info': json.dumps(info)}
        d_res = mapping.objects.deserialize_field(d, 'sz_info', 'info')
        self.assertEquals(d['one'], d_res['one'])
        self.assertFalse('sz_info' in d_res)
        self.assertEquals(info, d_res['info'])


if __name__ == '__main__':
    unittest.main()
