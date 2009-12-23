from eventlet import coros
from helixcore.test.test_environment import transaction
import datetime
import unittest


class DbBlockingTestCase(unittest.TestCase):
    @transaction()
    def db_sleep(self, num, curs=None):
        curs.execute('SELECT pg_sleep(%s)::text', [num])

    def test_blocking(self):
        task_num, sleep_sec = 1, 1
        pool = coros.CoroutinePool(max_size=10)
        begin = datetime.datetime.now()
        for _ in xrange(task_num):
            pool.execute_async(self.db_sleep, sleep_sec)
        pool.wait_all()
        end = datetime.datetime.now()
        td = end - begin
        print 'Consistent execution time: %s sec' % task_num * sleep_sec
        print 'Real execution time: %d.%d sec' % (td.seconds, td.microseconds)


if __name__ == '__main__':
    unittest.main()
