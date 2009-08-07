import unittest

from helixcore.db.buildhelpers import quote, quote_list

class BuildhelpersTestCase(unittest.TestCase):
    def test_quote(self):
        self.assertEqual('"id"', quote('id'))
        self.assertEqual('"id"', quote('"id"'))
        self.assertEqual('""id"', quote('"id'))
        self.assertEqual('"id""', quote('id"'))
        self.assertEqual('"billing"."id"', quote('billing.id'))
        self.assertEqual('"billing"."id"', quote('"billing"."id"'))
        self.assertEqual('""billing"."id""', quote('"billing.id"'))
        self.assertEqual('"billing"."id"."cd"', quote('billing.id.cd'))

    def test_quote_list(self):
        self.assertEqual(('"1"."1","1"."2","1"."2"."1"'), quote_list(('1.1', '1.2', '1.2.1')))

if __name__ == '__main__':
    unittest.main()