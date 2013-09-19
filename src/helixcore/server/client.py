import json
import urllib2

from helixcore import error_code
from helixcore.error import UnauthorizedActivity


class Client(object):
    def __init__(self, url):
        self.url = url

    def _request(self, data, django_req):
        try:
            ip = self._client_ip(django_req)
            h = {'X-Forwarded-For': ip}
            req = urllib2.Request(self.url, headers=h)
            f = urllib2.urlopen(req, json.dumps(data))
            resp = f.read()
            return json.loads(resp)
        except urllib2.URLError:
            return {'status': 'error', 'message': 'Service unavailable',
                'code': error_code.HELIX_SERVICE_UNAVAILABLE}

    def request(self, data, django_req, check_response=True):
        resp = self._request(data, django_req)
        if check_response:
            self._check_response(resp)
        return resp

    def _check_response(self, resp):
        unauth = ('HELIXAUTH_SESSION_NOT_FOUND', 'HELIXAUTH_SESSION_EXPIRED',
            'HELIXAUTH_USER_AUTH_ERROR')
        if resp['status'] != 'ok' and resp['code'] in unauth:
            raise UnauthorizedActivity

    def _client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
