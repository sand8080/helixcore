from eventlet import coros
import datetime
import cjson
import urllib2
import random


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
        print '%s >>>>' % func.func_name
        repeats = kwargs['repeats']
        pool = coros.CoroutinePool(max_size=repeats)
        start = datetime.datetime.now()
        for _ in xrange(repeats):
            pool.execute_async(func, self, *args, **kwargs)
        pool.wait_all()
        delta = datetime.datetime.now() - start
        if delta.seconds == 0:
            print 'repeats: %d, elapsed time %s' % (repeats, delta)
        else:
            print 'repeats: %d, elapsed time %s ~ [%s per second]' % (repeats, delta, repeats / delta.seconds)
        print '%s <<<<' % func.func_name
    return decorated


class ClientApplication(object):
    def __init__(self, host, port, login, password):
        self.host = host
        self.port = port
        self.login = login
        self.password = password

    def request(self, data):
        req = urllib2.Request(url='http://%s:%d' % (self.host, self.port), data=cjson.encode(data))
        f = urllib2.urlopen(req)
        return f.read()
