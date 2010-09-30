import cjson
import logging
import sys
import traceback

from helixcore import security
from helixcore.server.api import Api as HelixApi
from helixcore.server.response import response_error, response_app_error
from helixcore.server.errors import RequestProcessingError, ValidationError


class Application(object):
    def __init__(self, action_handler, protocol, logger, tracking_api_calls=()):
        self.action_handler = action_handler
        self.logger = logger
        self.helix_api = HelixApi(protocol)
        self.tracking_api_calls = tracking_api_calls

    def track_api_call(self, s_req, s_resp, remote_addr,
        action_name, authorized_data):
        pass

    def __call__(self, environ, start_response):
        raw_data = environ['eventlet.input'].read()
        remote_addr = environ.get('REMOTE_ADDR', 'undefined')

        action_name = None
        processed_action_data = {}
        secured_request = {}
        secured_response = {}

        try:
            action_name, action_data = self.helix_api.handle_request(raw_data)
            secured_request = self._secured_request(action_name, action_data)
            self.logger.debug('Request from %s: %s' % (remote_addr, secured_request))

            processed_action_data = dict(action_data)
            raw_response = self.action_handler(action_name, processed_action_data)

            secured_response = security.sanitize_credentials(raw_response)
            self.logger.log(logging.DEBUG, 'Response to %s: %s' % (remote_addr, secured_response))

            response = self.helix_api.handle_response(action_name, raw_response)
        except ValidationError, e:
            action_name, action_data = self.helix_api.handle_request(raw_data, validation=False)
            secured_request = self._secured_request(action_name, action_data)

            raw_response = response_error(e)
            response = self.helix_api.handle_response(action_name, raw_response, validation=False)
            self.logger.log(logging.ERROR, 'Request from %s: %s' % (remote_addr, secured_request))
            secured_response = security.sanitize_credentials(raw_response)
            self.logger.log(logging.ERROR, 'Response to %s: %s. Error: %s' % (remote_addr, secured_response, e.message))
        except RequestProcessingError, e:
            raw_response = response_error(e)
            response = self.helix_api.handle_response(action_name, raw_response, validation=False)
            self.logger.log(logging.ERROR, 'Request from %s: %s' % (remote_addr, secured_request))
            secured_response = security.sanitize_credentials(raw_response)
            self.logger.log(logging.ERROR, 'Response to %s: %s. Error: %s' % (remote_addr, secured_response, e.message))
        except Exception, e:
            exc_type, value, tb = sys.exc_info()
            exc_descr = 'Exception type: %s. message: %s. trace: %s' % (
                exc_type, '; '.join(value.args), traceback.extract_tb(tb))
            del tb
            raw_response = response_app_error(exc_descr)
            response = self.helix_api.handle_response(action_name,
                raw_response, validation=False)
            secured_response = security.sanitize_credentials(raw_response)
            self.logger.log(logging.ERROR, 'Response to %s: %s. General error: %s' %
                (remote_addr, secured_response, exc_descr))

        start_response('200 OK', [('Content-type', 'text/plain')])

        self._log_action(remote_addr, secured_request, secured_response,
            action_name, processed_action_data)

        return [response]

    def _log_action(self, remote_addr, secured_request, secured_response,
        action_name, processed_action_data):
        try:
            if action_name in self.tracking_api_calls:
                request = cjson.encode(secured_request)
                response = cjson.encode(secured_response)
                self.track_api_call(remote_addr, request,
                    response, action_name, processed_action_data)
        except Exception, e:
            self.logger.log(logging.ERROR, 'Action logging failed: %s' % e)

    def _secured_request(self, action_name, action_data):
        d = security.sanitize_credentials(action_data)
        d['action'] = action_name
        return d
