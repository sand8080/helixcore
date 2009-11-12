import unittest

from helixcore.test.test_environment import transaction
import datetime
from eventlet import util, coros

util.wrap_socket_with_coroutine_socket()

class DbBlockingTestCase(unittest.TestCase):
    @transaction()
    def db_sleep(self, num, curs=None):
        curs.execute('SELECT pg_sleep(%s)', [num])

    def test_blocking(self):
        pool = coros.CoroutinePool(max_size=10)

        waiters = []
        task_num, sleep_sec = 2, 1
        for _ in xrange(task_num):
            waiters.append(pool.execute_async(self.db_sleep, sleep_sec))

        begin = datetime.datetime.now()
        for waiter in waiters:
            waiter.wait()
        end = datetime.datetime.now()
        td = end - begin
        print 'Consistent execution time: %s sec' % task_num * sleep_sec
        print 'Real execution time: %d.%d sec' % (td.seconds, td.microseconds)


if __name__ == '__main__':
    unittest.main()
