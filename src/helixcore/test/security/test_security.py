import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.security import (sanitize_credentials, encrypt_passwords,
FIELDS_FOR_ENCRYPTION)


class SecurityTestCase(RootTestCase):
    def test_sanitize_credentials(self):
        d = {'login': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp', 'session_id': 'sid'}
        actual = sanitize_credentials(d)
        expected = {'login': 'l', 'password': '******',
            'new_password': '******', 'su_password': '******',
            'session_id': '******'}
        self.assertEqual(expected, actual)

    def test_encrypt_passwords(self):
        d = {'login': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp', 'session_id': 'sid'}
        enc_d = encrypt_passwords(d, lambda x: '_%s_' % x)
        for f in FIELDS_FOR_ENCRYPTION:
            self.assertNotEqual(d[f], enc_d[f])


if __name__ == '__main__':
    unittest.main()
