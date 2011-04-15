import cjson
from random import random
from StringIO import StringIO


def random_syllable(
    consonant='r|t|p|l|k|ch|kr|ts|bz|dr|zh|g|f|d|s|z|x|b|n|m'.split('|'),
    vowels='eyuioja'
):
    return ''.join(map(random.choice, (consonant, vowels)))


def random_word(min_syllable=2, max_syllable=6):
    return ''.join(random_syllable() for x in range(random.randint(min_syllable, max_syllable))) #@UnusedVariable


class ClientSimpleApplication(object):
    def __init__(self, app):
        self.app = app

    def request(self, data):
        environ = {'eventlet.input': StringIO(cjson.encode(data))}
        def start_response(_, __):
            pass
        response = self.app(environ, start_response)[0]
        return cjson.decode(response)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


def get_api_calls(protocol):
    api_calls = [p.name for p in protocol]
    result = set()
    for api_call in api_calls:
        clean = api_call.replace('_request', '').replace('_response', '')
        result.add(clean)
    return result
