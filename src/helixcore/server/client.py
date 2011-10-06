import json
import urllib2

from helixcore import error_code
from helixcore.error import UnauthorizedActivity


class Client(object):
    def __init__(self, url):
        self.url = url

    def _request(self, data):
        try:
            f = urllib2.urlopen(self.url, json.dumps(data))
            resp = f.read()
            return json.loads(resp)
        except urllib2.URLError:
            return {'status': 'error', 'message': 'Service unavailable',
                'code': error_code.HELIX_SERVICE_UNAVAILABLE}

    def request(self, data, check_response=True):
        resp = self._request(data)
        if check_response:
            self._check_response(resp)
        return resp

    def _check_response(self, resp):
        unauth = ('HELIXAUTH_SESSION_NOT_FOUND', 'HELIXAUTH_SESSION_EXPIRED',
            'HELIXAUTH_USER_AUTH_ERROR')
        if resp['status'] != 'ok' and resp['code'] in unauth:
            raise UnauthorizedActivity
