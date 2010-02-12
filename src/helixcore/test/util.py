# coding=utf-8
from eventlet import GreenPool
import datetime
import cjson
import random
import time
from StringIO import StringIO

from eventlet import patcher
urllib2 = patcher.import_patched('urllib2')


def random_syllable(
    consonant='r|t|p|l|k|ch|kr|ts|bz|dr|zh|g|f|d|s|z|x|b|n|m'.split('|'),
    vowels='eyuioja'
):
    return ''.join(map(random.choice, (consonant, vowels)))


def random_word(min_syllable=2, max_syllable=6):
    return ''.join(random_syllable() for x in range(random.randint(min_syllable, max_syllable))) #@UnusedVariable


def select_random(collection):
    min_idx, max_idx = 0, len(collection) - 1
    return collection[random.randint(min_idx, max_idx)]


def profile(func):
    def decorated(self, *args, **kwargs):
        times = []
        def time_calculator(*a, **kw):
            start = time.time()
            func(*a, **kw)
            times.append(time.time() - start)

        print '%s >>>>' % func.func_name
        repeats = kwargs['repeats']
        pool = GreenPool(size=repeats)
        start = datetime.datetime.now()
        for _ in xrange(repeats):
            pool.spawn(time_calculator, self, *args, **kwargs)
        pool.waitall()
        delta = datetime.datetime.now() - start
        if delta.seconds == 0:
            print 'repeats: %d, elapsed time %s' % (repeats, delta)
        else:
            print 'repeats: %d, elapsed time %s ~ [%s per second]' % (repeats, delta, repeats / delta.seconds)

        mid = sum(times) / repeats
        sigma = (sum((x - mid) ** 2 for x in times) / repeats) ** 0.5
        percent = sigma / mid
        print ' * ',
        print '%.0f ±%.0f msec,' % (mid * 1000, sigma * 1000),
        print '%.0f ±%.0f requests per second' % (1.0 / mid, 1.0 / mid * percent),
        print '(%.0f%%) ' % (percent * 100),
        print '%s <<<<' % func.func_name
        print
    return decorated


def show_time(func):
    def decorated(self, *args, **kwargs):
        print '%s >>>>' % func.func_name
        start = datetime.datetime.now()
        result = func(self, *args, **kwargs)
        delta = datetime.datetime.now() - start
        print 'elapsed time %s' % delta
        print '%s <<<<' % func.func_name
        return result
    return decorated


class ClientApplication(object):
    def __init__(self, app, login, password):
        self.app = app
        self.login = login
        self.password = password

    def request(self, data):
        data_copy = dict(data)
        if 'login' not in data_copy:
            data_copy['login'] = self.login
        if 'password' not in data_copy:
            data_copy['password'] = self.password
        environ = {'eventlet.input': StringIO(cjson.encode(data_copy))}
        def start_response(_, __):
            pass
        response = self.app(environ, start_response)[0]
        return cjson.decode(response)