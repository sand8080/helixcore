import unittest
#from datetime import datetime
#from eventlet import api, util, coros

#from helixtariff.test.root_test import RootTestCase
#from helixtariff.conf import settings
#from helixtariff.test.wsgi.client import Client
#from helixtariff.wsgi.server import Server
#
#util.wrap_socket_with_coroutine_socket()
#
#api.spawn(Server.run)

class DbBlockingTestCase(unittest.TestCase):
    pass
#    def setUp(self):
#        super(PsycopgBlockingTestCase, self).setUp()
#        self.cli = Client(settings.server_host, settings.server_port, '%s' % datetime.now(), 'qazwsx')
#
#    def db_sleep(self, num):
#        print self.cli.db_sleep(num)
#
#    def test_blocking(self):
#        self.cli.add_client()
#        pool = coros.CoroutinePool(max_size=10)
#
#        waiters = []
#        waiters.append(pool.execute_async(self.db_sleep, 3))
#
#        for waiter in waiters:
#            waiter.wait()


if __name__ == '__main__':
    unittest.main()
