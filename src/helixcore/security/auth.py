from functools import partial

from helixcore.server.client import Client


class CoreAuthenticator(object):
    def __init__(self, url):
        self.cli = Client(url)

    def check_access(self, session_id, service_type, property):
        req = {'action': 'check_access', 'session_id': session_id,
            'service_type': service_type, 'property': property}
        return self.cli.request(req)

    def _proxy_request(self, action, data):
        req = dict(data)
        req['action'] = action
        return self.cli.request(req, check_response=False)

    login = partial(_proxy_request, 'login')
    logout = partial(_proxy_request, 'logout')
    logout = partial(_proxy_request, 'check_user_exist')
