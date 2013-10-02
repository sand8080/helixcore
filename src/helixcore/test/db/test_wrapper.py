import unittest
from datetime import datetime
import cx_Oracle
from time import sleep

from helixcore.db.wrapper import fetchall_dicts, fetchone_dict, dict_from_lists, EmptyResultSetError, \
    SelectedMoreThanOneRow
from helixcore.db.sql import Eq, In, Select, Insert, Update
from helixcore.install.install import is_table_exists, is_sequence_exists
from helixcore.test.db import create_table, drop_table, fill_table
from helixcore.test.test_environment import transaction, get_connection


class WrapperTestCase(unittest.TestCase):
    table = 'test_wrapper'

    def setUp(self):
        try:
            create_table(self.table)
        except Exception, e:
            print e

    def tearDown(self):
        drop_table(self.table)
        pass

    def test_dict_from_lists(self):
        names = ['id', 'name', 'code']
        values = [1, 'bob', 42, 'ignorable value']
        d = dict_from_lists(names, values)
        for idx, name in enumerate(names):
            self.assertEqual(values[idx], d[name])

    def test_dict_from_lists_duplicates(self):
        dup_name = 'id'
        should_be = 42
        names = [dup_name, 'name', dup_name, 'cd', dup_name]
        values = [1, 'bob', 4, 'xexe', should_be]
        d = dict_from_lists(names, values)
        self.assertEqual(len(names) - (names.count(dup_name) - 1), len(d))
        self.assertEqual(should_be, d[dup_name])

    @transaction()
    def test_fetchall_dicts(self, curs=None):
        num_records = 4
        fill_table(self.table, num_records=num_records)
        curs.execute(*Select(self.table).glue())
        result = fetchall_dicts(curs)
        self.assertEqual(num_records, len(result))
        data = result[0]
        self.assertEqual(3, len(data))
        self.assertTrue('ID' in data)
        self.assertTrue('NAME' in data)
        self.assertTrue('DATE_FIELD' in data)

    @transaction()
    def test_fetchall_dicts_not_found(self, curs=None):
        curs.execute(*Select(self.table).glue())
        self.assertEqual(0, len(fetchall_dicts(curs)))

    @transaction()
    def test_fetchone_dict(self, curs=None):
        fill_table(self.table, num_records=4)
        curs.execute(*Select(self.table, cond=Eq('id', 1)).glue())
        fetchone_dict(curs)

    @transaction()
    def test_fetchone_dict_error(self, curs=None):
        fill_table(self.table, num_records=4)
        curs.execute(*Select(self.table, cond=In('id', [1, 2])).glue())
        self.assertRaises(SelectedMoreThanOneRow, fetchone_dict, curs)

    def test_fetchone_dict_raise(self):
        conn = get_connection()
        curs = conn.cursor()
        try:
            curs.execute(*Select(self.table, cond=Eq('id', 1)).glue())
            self.assertRaises(EmptyResultSetError, fetchone_dict, curs)
            curs.close()
            conn.commit()
        except Exception:
            curs.close()
            conn.rollback()
            raise

    @transaction()
    def test_dict_from_list(self, curs=None):
        num_records = 7
        fill_table(self.table, num_records=num_records)
        curs.execute(*Select(self.table).glue())
        self.assertEqual(num_records, len(fetchall_dicts(curs)))

    @transaction()
    def slow_task(self, report, id, pause, curs=None): #IGNORE:W0622
        q_sel, params = Select(self.table, cond=Eq('id', id), for_update=True).glue()
        curs.execute(q_sel, params)
        curs.execute(*Update(self.table, updates={'name': 'substituted'}, cond=Eq('id', id)).glue())
        curs.execute(q_sel, params)
        report['slow_task'] = fetchone_dict(curs)
        sleep(pause)

    def fast_task(self, report, id, pause, conn=None): #IGNORE:W0622
        curs = conn.cursor()
        try:
            sleep(pause)
            curs.execute(*Select(self.table, cond=Eq('id', id)).glue())
            report['fast_task'] = fetchone_dict(curs)
            curs.close()
            conn.commit()
        except Exception:
            curs.close()
            conn.rollback()
            raise

    @transaction()
    def task_wait_before(self, report, id, pause, curs=None): #IGNORE:W0622
        sleep(pause)
        curs.execute(*Select(self.table, cond=Eq('id', id), for_update=True).glue())
        report['task_wait_before'] = fetchone_dict(curs)

    def test_data_isolation(self):
        fill_table(self.table)
        from threading import Thread
        report = {}
        id = 1 #IGNORE:W0622
        t_slow = Thread(target=self.slow_task, args=(report, id, 0.2))
        t_fast = Thread(target=self.fast_task, args=(report, id, 0.1, get_connection()))
        t_slow.start()
        t_fast.start()
        t_slow.join()
        self.assertNotEqual(report['slow_task']['NAME'], report['fast_task']['NAME'])

    def test_data_consistency(self):
        fill_table(self.table)
        from threading import Thread
        report = {}
        id = 1 #IGNORE:W0622
        t_one = Thread(target=self.slow_task, args=(report, id, 0.2))
        t_two = Thread(target=self.task_wait_before, args=(report, id, 0.1))
        t_one.start()
        t_two.start()
        t_one.join()
        t_two.join()
        self.assertEqual(report['slow_task']['NAME'], report['task_wait_before']['NAME'])


if __name__ == '__main__':
    unittest.main()
