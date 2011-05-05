import cjson
from random import random
from StringIO import StringIO
from helixcore.error import ValidationError


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


class ProtocolTester(object):
    api = None

    def validate_error_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'error',
            'code': 'c', 'message': 'h'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c', 'category': 'c'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c', 'message': 'm', 'details': []})

    def validate_authorized_error_response(self, action_name):
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'code': 'c',
            'message': 'h', 'fields': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'code': 'c',
            'message': 'h', 'fields': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c',
            'message': 'h', 'fields': [{'f': 'v'}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c', 'message': 'm'})

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

    def validate_authorized_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok', 'session_id': 'i'})
        self.validate_authorized_error_response(action_name)

    def test_ping(self):
        self.api.validate_request('ping', {})
        self.validate_status_response('ping')


class ActionsLogTester(object):
    def _do_count(self, sess_id, action, filtering_method):
        req = {'session_id': sess_id, 'filter_params': {'action': action},
            'paging_params': {}, 'ordering_params': []}
        resp = filtering_method(**req)
        self.check_response_ok(resp)
        return len(resp['action_logs'])

    def _count_records(self, sess_id, action):
        return self._do_count(sess_id, action, self.cli.get_action_logs)

    def _count_self_records(self, sess_id, action):
        return self._do_count(sess_id, action, self.cli.get_action_logs_self)

    def _logged_action(self, action, req, check_resp=True):
        sess_id = req['session_id']
        logs_num = self._count_records(sess_id, action)
        api_call = getattr(self.cli, action)
        resp = api_call(**req)
        if check_resp:
            self.check_response_ok(resp)
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

    def _not_logged_action(self, action, sess_id, req):
        api_call = getattr(self.cli, action)
        req['session_id'] = sess_id
        api_call(**req)
        self.assertEquals(0, self._count_records(sess_id, action))

    def _not_logged_filtering_action(self, action, sess_id):
        req = {'filter_params': {}, 'paging_params': {}}
        self._not_logged_action(action, sess_id, req)

    def check_response_ok(self, resp):
        self.assertEqual('ok', resp['status'])

