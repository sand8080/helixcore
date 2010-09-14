import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.security import sanitize_credentials


class SecurityTestCase(RootTestCase):
    def test_sanitize_credentials(self):
        d = {'login': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp'}
        actual = sanitize_credentials(d)
        expected = {'login': 'l', 'password': '******',
            'new_password': '******', 'su_password': '******'}
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
