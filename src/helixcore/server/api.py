import cjson, datetime, copy, pytz
from helixcore.server.errors import RequestProcessingError

class FormatError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.request_format, msg)

class Api(object):
    def __init__(self, validate_req_func, validate_resp_func):
        self.validate_req_func = validate_req_func
        self.validate_resp_func = validate_resp_func

    def handle_request(self, raw_data):
        '''
        Parses raw JSON request to structure, validates it and calls appropriate method on handler_object
        @param raw_data: raw JSON data.
        @return: tuple(action_name, data_dict)
        @raise ValidationError: if request validation fails
        '''
        try:
            parsed_data = cjson.decode(raw_data)
        except cjson.DecodeError, e:
            raise FormatError("Cannot parse request: %s" % e)

        action_name = parsed_data.pop('action')
        if action_name is None:
            raise FormatError("'action' parameter is not found in request")

        self.validate_req_func(action_name, parsed_data)

        return (action_name, parsed_data)

    def _postprocess_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.astimezone(pytz.utc).isoformat()
        return value

    def _postprocess_response(self, response, fun):
        if isinstance(response, dict):
            for k in response:
                response[k] = self._postprocess_response(response[k], fun)
            return response
        if hasattr(response, '__iter__'):
            for i in xrange(0, len(response)):
                response[i] = self._postprocess_response(response[i], fun)
            return response
        return fun(response)

    def handle_response(self, action_name, response_dict, validate=True):
        '''
        Validates response scheme and encodes response dict.
        If action_name is none, validation is not perform.
        @param action_name: action name
        @param response_dict: response data.
        @raise ValidationError: if request validation fails
        @return: raw encoded response
        '''
        response = self._postprocess_response(
            copy.deepcopy(response_dict),
            self._postprocess_value
        )

        if validate:
            self.validate_resp_func(action_name, response)

        return cjson.encode(response)
