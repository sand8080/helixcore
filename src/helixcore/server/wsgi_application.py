import cjson
import logging
import sys
import traceback

from helixcore.server.api import Api as HelixApi
from helixcore.server.response import response_error, response_app_error
from helixcore.server.errors import RequestProcessingError


class Application(object):
    def __init__(self, action_handler, protocol, logger, tracking_api_calls=()):
        self.action_handler = action_handler
        self.logger = logger
        self.helix_api = HelixApi(protocol)
        self.tracking_api_calls = tracking_api_calls

    def track_api_call(self, s_req, s_resp, authorized_data):
        pass

    def __call__(self, environ, start_response):
        raw_data = environ['eventlet.input'].read()
        remote_addr = environ.get('REMOTE_ADDR', 'undefined')
        self.logger.debug('Request from %s' % remote_addr)

        action_name = None
        data = {}
        authorized_data = {}
        try:
            action_name, data = self.helix_api.handle_request(raw_data)
            self.logger.debug('Request from %s: %s' % (remote_addr, self.secured_request(action_name, data)))
            authorized_data = dict(data)
            raw_response = self.action_handler(action_name, authorized_data)
            self.logger.log(logging.DEBUG, 'Response to %s: %s' % (remote_addr, raw_response))
            response = self.helix_api.handle_response(action_name, raw_response)
        except RequestProcessingError, e:
            response = self.helix_api.handle_response(action_name, response_error(e), validation=False)
            self.logger.log(logging.ERROR, 'Request from %s: %s' % (remote_addr, self.secured_request(action_name, data)))
            self.logger.log(logging.ERROR, 'Response to %s: %s. Error: %s' % (remote_addr, response, e.message))
        except Exception, e:
            exc_type, value, tb = sys.exc_info()
            exc_descr = 'Exception type: %s. message: %s. trace: %s' % (
                exc_type, value.message, traceback.extract_tb(tb))
            del tb
            response = self.helix_api.handle_response(action_name,
                response_app_error(exc_descr), validation=False)
            self.logger.log(logging.ERROR, 'Response to %s: %s. General error: %s' %
                (remote_addr, response, exc_descr))

        start_response('200 OK', [('Content-type', 'text/plain')])
        if action_name in self.tracking_api_calls:
            request = cjson.encode(self.secured_request(action_name, data))
            secured_authorized_data = self.secured_request(action_name, authorized_data)
            self.track_api_call(request, response, secured_authorized_data)
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
