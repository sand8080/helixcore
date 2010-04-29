import unittest
import cjson

from helixcore.test.root_test import RootTestCase
from helixcore.valik.valik import Text
from helixcore.server.api import Api, ApiCall, FormatError
from helixcore.server.errors import RequestProcessingError


class RequestHandlingTestCase(RootTestCase):
    def test_request_format_error(self):
        raw_data = '{"hren" : 8986, "aaa": "str", 789, -99}'
        self.assertRaises(FormatError, Api([]).handle_request, raw_data)

    def test_request_validation_error(self):
        bad_data = {
            'action': 'unknown',
            'aaa': 'str',
            'param2': 'foo bar',
        }
        raw_data = cjson.encode(bad_data)
        self.assertRaises(RequestProcessingError, Api([]).handle_request, raw_data)

    def test_request_ok(self):
        good_data = {
            'action': 'add_currency',
            'name': 'USD',
            'designation': '$',
            'cent_factor': 100,
        }

        raw_data = cjson.encode(good_data)
        protocol = [
            ApiCall('add_currency_request', {'name': Text(), 'designation': Text(), 'cent_factor': int}),
            ApiCall('add_currency_response', {'status': Text()}),
        ]
        test_api = Api(protocol)
        action_name, data = test_api.handle_request(raw_data)
        self.assertEquals(action_name, good_data.pop('action'))
        self.assertEquals(data, good_data)

        good_response = {'status': 'ok'}
        actual_response = cjson.decode(test_api.handle_response(action_name, good_response))
        self.assertEquals(good_response, actual_response)


if __name__ == '__main__':
    unittest.main()
