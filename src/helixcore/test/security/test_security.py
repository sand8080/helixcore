import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.security import sanitize_credentials


class SecurityTestCase(RootTestCase):
    def test_sanitize_credentials(self):
        d = {'email': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp', 'session_id': 'sid'}
        actual = sanitize_credentials(d)
        expected = {'email': 'l', 'password': '******',
            'new_password': '******', 'su_password': '******',
            'session_id': 'sid'}
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
