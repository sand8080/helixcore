import cjson, datetime, copy, pytz
from helixcore.server.errors import RequestProcessingError

class FormatError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.request_format, msg)

class Api(object):
    def __init__(self, validate_func):
        self.validate_func = validate_func

    def handle_request(self, raw_data):
        '''
        Parses raw JSON request to structure, validates it and calls appropriate method on handler_object
        @param raw_data: raw JSON data.
        @param handler: callable object taking action name and parsed data as parameters. Returns response dict
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

        self.validate_func.validate(action_name, parsed_data)

        return (action_name, parsed_data)

    def handle_response(self, response_dict):
        '''
        Validates (custom operation) and encodes response dict
        @param response_dict: response data.
        @param handler: callable object taking action name and parsed data as parameters. Returns response dict
        @raise ValidationError: if request validation fails
        @return: raw encoded response
        '''
        def postprocess_value(value):
            if isinstance(value, datetime.datetime):
                return value.astimezone(pytz.utc).isoformat()
            return value

        def postprocess_response(response, fun):
            if isinstance(response, dict):
                for k in response:
                    response[k] = postprocess_response(response[k], fun)
                return response
            if hasattr(response, '__iter__'):
                for i in xrange(0, len(response)):
                    response[i] = postprocess_response(response[i], fun)
                return response
            return fun(response)

        return cjson.encode(postprocess_response(copy.deepcopy(response_dict), postprocess_value))
