import cjson, datetime, copy, pytz
from helixcore.server.exceptions import ValidationError, FormatError
from helixcore.validol.validol import validate


# Useful for documentation generation
class ApiCall(object):
    def __init__(self, name, scheme, description='Not described at yet.'):
        self.name = name
        self.scheme = scheme
        self.description = description


class Api(object):
    def __init__(self, protocol):
        '''
        @param protocol: list of ApiCall objects
        '''
        self.scheme_dict = dict((c.name, c.scheme) for c in protocol)

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

        self.validate_request(action_name, parsed_data)

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

    def handle_response(self, action_name, response_dict, validation=True):
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

        if validation:
            self.validate_response(action_name, response)

        return cjson.encode(response)

    def _validate(self, call_name, data):
        scheme = self.scheme_dict.get(call_name)
        if scheme is None:
            raise ValidationError('Scheme for %s not found' % call_name)

        result = validate(scheme, data)
        if not result:
            raise ValidationError(
                'Validation failed for action %s. Expected scheme: %s. Actual data: %s'
                % (call_name, scheme, data)
            )

    def validate_request(self, action_name, data):
        '''
        Validates API request data by action name
        @raise ValidationError: if validation failed for some reason
        '''
        return self._validate('%s_request' % action_name, data)


    def validate_response(self, action_name, data):
        '''
        Validates API response data by action name
        @raise ValidationError: if validation failed for some reason
        '''
        return self._validate('%s_response' % action_name, data)
