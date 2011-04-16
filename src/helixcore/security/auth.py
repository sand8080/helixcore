from helixcore.server.client import Client


class Authentifier(object):
    def __init__(self, url):
        self.cli = Client(url)

    def check_access(self, session_id, service_type, property):
        req = {'action': 'check_access', 'session_id': session_id,
            'service_type': service_type, 'property': property}
        return self.cli.request(req)

    def login(self, data):
        req = dict(data)
        req['action'] = 'login'
        return self.cli.request(req, check_response=False)
