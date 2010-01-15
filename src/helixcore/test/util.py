# coding=utf-8
from eventlet import coros
import datetime
import cjson
import urllib2
import random
import time


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
        pool = coros.CoroutinePool(max_size=repeats)
        start = datetime.datetime.now()
        for _ in xrange(repeats):
            pool.execute_async(time_calculator, self, *args, **kwargs)
        pool.wait_all()
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
    def __init__(self, host, port, login, password, protocol='http'):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.login = login
        self.password = password

    def request(self, data):
        req = urllib2.Request(url='%s://%s:%d' % (self.protocol, self.host, self.port),
            data=cjson.encode(data))
        f = urllib2.urlopen(req)
        return cjson.decode(f.read())