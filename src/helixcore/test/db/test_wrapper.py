import unittest
import psycopg2
from time import sleep
from datetime import datetime

from helixcore.db.wrapper import fetchall_dicts, fetchone_dict, dict_from_lists, EmptyResultSetError
from helixcore.db.query_builder import select, update, insert
from helixcore.db.cond import Eq
from helixcore.test.helpers import transaction, get_connection

class WrapperTestCase(unittest.TestCase):

    table = 'test_wrapper'

    def setUp(self):
        try:
            self.create_table()
        except psycopg2.Error, e:
            print e

    def tearDown(self):
        self.drop_table()

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
        self.fill_table(num_records=num_records)
        curs.execute(*select(self.table))
        result = fetchall_dicts(curs)
        self.assertEqual(num_records, len(result))
        data = result[0]
        self.assertEqual(3, len(data))
        self.assertTrue('id' in data)
        self.assertTrue('name' in data)
        self.assertTrue('date' in data)

    @transaction()
    def test_fetchall_dicts_not_found(self, curs=None):
        curs.execute(*select(self.table))
        self.assertEqual(0, len(fetchall_dicts(curs)))

    @transaction()
    def test_fetchone_dict(self, curs=None):
        self.fill_table(num_records=4)
        curs.execute(*select(self.table, cond=Eq('id', 1)))
        fetchone_dict(curs)

    def test_fetchone_dict_raise(self):
        conn = get_connection()
        curs = conn.cursor()
        try:
            curs.execute(*select(self.table, cond=Eq('id', 1)))
            self.assertRaises(EmptyResultSetError, fetchone_dict, curs)
            curs.close()
            conn.commit()
        except Exception:
            curs.close()
            conn.rollback()
            raise

    @transaction()
    def create_table(self, curs=None):
        curs.execute(
            'CREATE TABLE %s (id serial, name varchar, date timestamp)' %
            self.table
        )

    @transaction()
    def drop_table(self, curs=None):
        curs.execute('DROP TABLE IF EXISTS %s' % self.table)

    @transaction()
    def fill_table(self, num_records=5, curs=None):
        for i in xrange(num_records):
            curs.execute(*insert(self.table, {'name': i, 'date': datetime.now()}))

    @transaction()
    def test_dict_from_list(self, curs=None):
        num_records = 7
        self.fill_table(num_records)
        curs.execute(*select(self.table))
        self.assertEqual(num_records, len(fetchall_dicts(curs)))

    @transaction()
    def slow_task(self, report, id, pause, curs=None):
        q_sel, params = select(self.table, cond=Eq('id', id), for_update=True)
        curs.execute(q_sel, params)
        curs.execute(*update(self.table, updates={'name': 'substituted'}, cond=Eq('id', id)))
        curs.execute(q_sel, params)
        report['slow_task'] = fetchone_dict(curs)
        sleep(pause)

    def fast_task(self, report, id, pause, conn=None):
        curs = conn.cursor()
        try:
            sleep(pause)
            curs.execute(*select(self.table, cond=Eq('id', id)))
            report['fast_task'] = fetchone_dict(curs)
            curs.close()
            conn.commit()
        except Exception:
            curs.close()
            conn.rollback()
            raise

    @transaction()
    def task_wait_before(self, report, id, pause, curs=None):
        sleep(pause)
        curs.execute(*select(self.table, cond=Eq('id', id), for_update=True))
        report['task_wait_before'] = fetchone_dict(curs)

    def test_data_isolation(self):
        self.fill_table()
        from threading import Thread
        report = {}
        id = 1
        t_slow = Thread(target=self.slow_task, args=(report, id, 0.2))
        t_fast = Thread(target=self.fast_task, args=(report, id, 0.1, get_connection()))
        t_slow.start()
        t_fast.start()
        t_slow.join()
        self.assertNotEqual(report['slow_task']['name'], report['fast_task']['name'])

    def test_data_consistency(self):
        self.fill_table()
        from threading import Thread
        report = {}
        id = 1
        t_one = Thread(target=self.slow_task, args=(report, id, 0.2))
        t_two = Thread(target=self.task_wait_before, args=(report, id, 0.1))
        t_one.start()
        t_two.start()
        t_one.join()
        t_two.join()
        self.assertEqual(report['slow_task']['name'], report['task_wait_before']['name'])

if __name__ == '__main__':
    unittest.main()
