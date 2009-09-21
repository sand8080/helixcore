import unittest
import psycopg2
from time import sleep
from datetime import datetime

from helixcore.db.sql import Eq
from helixcore.db.query_builder import insert
import helixcore.db.deadlock_detector as deadlock_detector

from helixcore.test.test_environment import transaction

class DeadlockDetectorTestCase(unittest.TestCase):

    table1 = 'test_deadlock_detector_1'
    table2 = 'test_deadlock_detector_2'
    table3 = 'test_deadlock_detector_3'

    def setUp(self):
        try:
            self.create_tables()
        except psycopg2.Error, e:
            print e

    def tearDown(self):
        self.drop_tables()

    @transaction()
    def test_not_allowed(self, curs=None):
        #table2 -> table3 NOT ALLOWED
        deadlock_detector.ALLOWED_TRANSITIONS = [
            (self.table1, self.table2),
            (self.table1, self.table3),
        ]
        self.fill_table(self.table2, 1, curs)
        self.fill_table(self.table3, 1, curs)

        deadlock_detector.handle_lock(self.table2)
        self.assertRaises(deadlock_detector.TransitionNotAllowedError, deadlock_detector.handle_lock, self.table3, Eq('name', '1'))

    @transaction()
    def test_allowed(self, curs=None):
        deadlock_detector.ALLOWED_TRANSITIONS = [
            (self.table1, self.table2),
            (self.table2, self.table3),
        ]
        self.fill_table(self.table1, 1, curs)
        self.fill_table(self.table2, 1, curs)
        self.fill_table(self.table3, 1, curs)

        deadlock_detector.handle_lock(self.table1)
        deadlock_detector.handle_lock(self.table2)
        deadlock_detector.handle_lock(self.table3)

    def lock_task(self, *tables):
        num_locked = 0
        self.assertFalse(hasattr(deadlock_detector.context, 'locks'))
        for t in tables:
            deadlock_detector.handle_lock(t)
            num_locked += 1
            self.assertEquals(len(deadlock_detector.context.locks), num_locked)

    @transaction()
    def test_thread_contexts(self, curs=None):
        deadlock_detector.ALLOWED_TRANSITIONS = [
            (self.table1, self.table2),
            (self.table2, self.table3),
        ]
        self.fill_table(self.table1, 1, curs)
        self.fill_table(self.table2, 1, curs)
        self.fill_table(self.table3, 1, curs)

        from threading import Thread
        t1 = Thread(target=self.lock_task, args=(self.table1, self.table2))
        t2 = Thread(target=self.lock_task, args=(self.table2, self.table3))
        t1.start()
        t2.start()
        sleep(0.2)

        #current context must be clean
        #locks attribute was initialized in other transaction calls (create_tables, ...) but was cleaned on transactions end
        self.assertEquals(len(deadlock_detector.context.locks), 0)

        t1.join()
        t2.join()

        self.assertEquals(len(deadlock_detector.context.locks), 0)

    @transaction()
    def create_tables(self, curs=None):
        for t in (self.table1, self.table2, self.table3):
            curs.execute(
                'CREATE TABLE %s (id serial, name varchar, date timestamp)' % t
            )

    @transaction()
    def drop_tables(self, curs=None):
        for t in (self.table1, self.table2, self.table3):
            curs.execute('DROP TABLE IF EXISTS %s' % t)

    def fill_table(self, table, num_records=5, curs=None):
        for i in xrange(num_records):
            curs.execute(*insert(table, {'name': i, 'date': datetime.now()}))

if __name__ == '__main__':
    unittest.main()
