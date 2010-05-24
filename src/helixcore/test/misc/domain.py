'''
Created on May 7, 2010

@author: andrew
'''
import unittest
from helixcore.misc.domain import DomainName


class DomainNameTestCase(unittest.TestCase):
    def test_parse(self):
        d = DomainName.parse('qweq-tt.com.ru')
        self.assertEquals('qweq-tt', d.name)
        self.assertEquals('com.ru', d.zone)


if __name__ == '__main__':
    unittest.main()
