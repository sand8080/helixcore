from functools import partial

from helixcore.server.client import Client


class CoreAuthenticator(object):
    def __init__(self, url):
        self.cli = Client(url)
        self.login = partial(self._proxy_request, 'email')
        self.logout = partial(self._proxy_request, 'logout')

    def check_access(self, session_id, service_type, property): #@ReservedAssignment
        req = {'action': 'check_access', 'session_id': session_id,
            'service_type': service_type, 'property': property}
        return self.cli.request(req)

    def check_user_exist(self, session_id, user_id):
        req = {'action': 'check_user_exist', 'session_id': session_id,
            'id': user_id}
        return self.cli.request(req)

    def _proxy_request(self, action, data):
        req = dict(data)
        req['action'] = action
        return self.cli.request(req, check_response=False)

