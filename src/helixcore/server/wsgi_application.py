import logging
import sys
import traceback

from helixcore.server.api import Api as HelixApi
from helixcore.server.response import response_error, response_app_error
from helixcore.server.errors import RequestProcessingError


class Application(object):
    def __init__(self, action_handler, protocol, logger):
        self.action_handler = action_handler
        self.logger = logger
        self.helix_api = HelixApi(protocol)

    def __call__(self, environ, start_response):
        raw_data = environ['eventlet.input'].read()
        remote_addr = environ.get('REMOTE_ADDR', 'undefined')
        self.logger.debug('Request from %s' % remote_addr)

        data = None
        action_name = None
        try:
            action_name, data = self.helix_api.handle_request(raw_data)
            self.logger.debug('Request from %s: %s' % (remote_addr, self.secured_request(action_name, data)))
            data_copy = dict(data)
            raw_response = self.action_handler(action_name, data_copy)
            self.logger.log(logging.DEBUG, 'Response to %s: %s' % (remote_addr, raw_response))
            response = self.helix_api.handle_response(action_name, raw_response)
        except RequestProcessingError, e:
            response = self.helix_api.handle_response(action_name, response_error(e), validation=False)
            self.logger.log(logging.ERROR, 'Request from %s: %s' % (remote_addr, self.secured_request(action_name, data)))
            self.logger.log(logging.ERROR, 'Response to %s: %s. Error: %s' % (remote_addr, response, e.message))
        except Exception, e:
            _, _, tb = sys.exc_info()
            response = self.helix_api.handle_response(action_name, response_app_error(e.message), validation=False)
            self.logger.log(logging.ERROR, 'Response to %s: %s. General error: %s. Traceback: %s' %
                (remote_addr, response, e.message, traceback.extract_tb(tb)))

        start_response('200 OK', [('Content-type', 'text/plain')])
        return [response]

    def adapt(self, obj, req):
        'Convert obj to bytes'
        req.write(str(obj))

    def secured_request(self, action_name, data):
        d = {'action': action_name}
        if data is not None:
            d.update(data)
        if 'password' in d:
            d['password'] = '******'
        return d
