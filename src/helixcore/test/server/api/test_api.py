import unittest
import cjson

from helixcore.test.root_test import RootTestCase

from helixcore.server.api.api import Api, FormatError
from helixcore.server.error.errors import RequestProcessingError


class RequestHandlingTestCase(RootTestCase):
    class PositiveValidatorMoc(object):
        def validate(self, *args, **kwargs):
            pass

    class NegativeValidatorMoc(object):
        def validate(self, *args, **kwargs):
            raise RequestProcessingError('validation', 'Permanent validation error')

    positive_api = Api(PositiveValidatorMoc())
    negative_api = Api(NegativeValidatorMoc())

    def test_request_format_error(self):
        raw_data = '''
        {"hren" : 8986,
        "aaa": "str", 789, -99
        }
        '''
        self.assertRaises(FormatError, self.negative_api.handle_request, raw_data)

    def test_request_validation_error(self):
        bad_data = {
            'action': 'unknown',
            'aaa': 'str',
            'param2': 'foo bar',
        }
        raw_data = cjson.encode(bad_data)
        self.assertRaises(RequestProcessingError, self.negative_api.handle_request, raw_data)

    def test_request_ok(self):
        good_data = {
            'action': 'add_currency',
            'name': 'USD',
            'designation': '$',
            'cent_factor': 100,
        }

        raw_data = cjson.encode(good_data)
        api = Api(self.PositiveValidatorMoc())
        action_name, data = api.handle_request(raw_data)
        self.assertEquals(action_name, good_data.pop('action'))
        self.assertEquals(data, good_data)

        good_response = {'status': 'ok'}
        actual_response = cjson.decode(self.positive_api.handle_response(good_response))
        self.assertEquals(good_response, actual_response)

if __name__ == '__main__':
    unittest.main()
