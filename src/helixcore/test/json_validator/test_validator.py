import unittest
import datetime

from helixcore.json_validator import (validate, AnyOf, Optional, Scheme, ValueValidator,
    Text, IsoDatetime, DecimalText, ArbitraryDict, ValidationError,
    PositiveDecimalText, NonNegativeDecimalText, EmailText)


class ValueValidatorTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must throw exception on attempt to use its validate method """
        v = ValueValidator()
        self.assertRaises(NotImplementedError, v.validate, int, [])

    def test_good_002(self):
        """ all validators must be inherited from ValueValidator """
        # I don't really think it belongs to this test case
        for v in [AnyOf, Scheme, Text, IsoDatetime, DecimalText, ArbitraryDict]:
            result = issubclass(v, ValueValidator)
            self.assertTrue(result)


class SchemeTestCase(unittest.TestCase):
    def test_good_001(self):
        s = Scheme({'id': int})
        s.validate({'id': 10}, [])

    def test_bad_001(self):
        s = Scheme({'id': int})
        self.assertRaises(ValidationError, s.validate, {'id': '10'}, [])

    def test_good_002(self):
        scheme1 = {'id': int}
        scheme2 = {'name': str}
        scheme3 = {'email': str}
        s = Scheme(AnyOf(scheme1, scheme2, scheme3))
        s.validate({'id': 10}, [])

    def test_bad_002(self):
        scheme1 = {'id': int}
        scheme2 = {'name': str}
        scheme3 = {'email': str}
        s = Scheme(AnyOf(scheme1, scheme2, scheme3))
        self.assertRaises(ValidationError, s.validate, {'foo': 'bar'}, [])


class AnyOfTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate one type """
        x = AnyOf(int)
        x.validate(10, [])

    def test_good_002(self):
        """ must validate few types """
        x = AnyOf(10, "bar")
        x.validate("bar", [])

    def test_good_003(self):
        x = {
            'foo': AnyOf(int, str)
            }
        validate(x, {'foo': 10})
        validate(x, {'foo': 'bar'})

    def test_bad_001(self):
        """ must invalidate wrong types """
        x = AnyOf(int)
        self.assertRaises(ValidationError, x.validate, "foo", [])


class ListTestCase(unittest.TestCase):
    def test_good_001(self):
        x = [object]
        validate(x, [1,2,3,4])

    def test_good_002(self):
        x = [int]
        validate(x, [1,2,3,4])

    def test_good_003(self):
        x = []
        validate(x, [])

    def test_good_004(self):
        x = ()
        validate(x, ())

    def test_good_005(self):
        x = (int, str, bool)
        validate(x, (10, "foo", True))

    def test_bad_001(self):
        x = []
        self.assertRaises(ValidationError, validate, x, "foo")

    def test_bad_002(self):
        x = [int]
        self.assertRaises(ValidationError, validate, x, ["foo", "bar"])

    def test_bad_003(self):
        x = []
        self.assertRaises(ValidationError, validate, x, [1,2,3])

    def test_bad_004(self):
        x = ()
        self.assertRaises(ValidationError, validate, x, (10,))

    def test_bad_005(self):
        x = (int, str, bool)
        self.assertRaises(ValidationError, validate, x, ("foo", 10, False))

    def test_bad_006(self):
        x = ()
        self.assertRaises(ValidationError, validate, x, [])


class DictTestCase(unittest.TestCase):
    def test_good_002(self):
        x = {'foo': int}
        validate(x, {'foo': 10})

    def test_good_005(self):
        x = {}
        validate(x, {})

    def test_bad_001(self):
        x = {}
        self.assertRaises(ValidationError, validate, x, [])

    def test_bad_004(self):
        x = {}
        self.assertRaises(ValidationError, validate, x, {'a':'b'})

    def test_bad_006(self):
        x = {"foo": int, "bar": int}
        self.assertRaises(ValidationError, validate, x, {"bar": 10})

    def test_optional_good_001(self):
        x = {Optional('foo'): 10}
        validate(x, {'foo': 10})
        validate(x, {})

    def test_optional_good_002(self):
        x = {Optional('foo'): int}
        validate(x, {'foo': 10})

    def test_optional_bad_002(self):
        x = {Optional('foo'): int}
        validate(x, {})

    def test_optional_good_003(self):
        x = {Optional('foo'): int, 'a': 'b'}
        validate(x, {'foo': 10, 'a': 'b'})

    def test_optional_bad_003(self):
        x = {Optional('a'): int}
        self.assertRaises(ValidationError, validate, x, {'a': 'b'})

    def test_optional_good_004(self):
        x = {'a': 'b', 'c': 'd', Optional('foo'): 'bar', Optional('zoo'): 'xar'}
        validate(x, {'a': 'b', 'c': 'd', 'zoo': 'xar'})

    def test_optional_bad_004(self):
        x = {'a': 'b', 'c': 'd', Optional('foo'): 'bar', Optional('zoo'): 'xar'}
        self.assertRaises(ValidationError, validate, x, {'a': 'b', 'c': 'd', 'zoo': 'bar'})

    def test_nested_dict_001(self):
        x = {'a': 'b', 'c': {'d': 'e'}}
        validate(x, {'a': 'b', 'c': {'d': 'e'}})


class ArbitraryDictTestCase(unittest.TestCase):
    def test_001(self):
        x = {'a': ArbitraryDict()}
        validate(x, {'a': {}})
        validate(x, {'a': {'xx': 'yy'}})
        self.assertRaises(ValidationError, validate, x, {'a': []})


class TextTestCase(unittest.TestCase):
    def test_str_001(self):
        x = Text()
        validate(x, str('abc'))

    def test_unicode_001(self):
        x = Text()
        validate(x, unicode('abc'))

    def test_int_001(self):
        x = Text()
        self.assertRaises(ValidationError, validate, x, 10)


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """

    def test_good_002(self):
        scheme = {Optional('select'): [str],
                  Optional('limit'): int,
                  Optional('offset'): int,}
        data = {}
        validate(scheme, data)

    def test_bad_002(self):
        scheme = {Optional('select'): [str],
                  Optional('limit'): int,
                  Optional('offset'): int,}
        data = {'foo': 'bar'}
        self.assertRaises(ValidationError, validate, scheme, data)


class SamplesTestCase(unittest.TestCase):
    def test_integer_list_001(self):
        """ test case for integer list sample #1 """
        l = [1,2,3,4,5,6]
        scheme = [int]
        validate(scheme, l)
        l.append('bad_end')
        self.assertRaises(ValidationError, validate, scheme, l)

    def test_integer_list_003(self):
        """ test case for integer list sample #3 """
        l = [10, "foo", 15," bar"]
        scheme = [AnyOf(int, str)]
        validate(scheme, l)
        l.append(True)
        self.assertRaises(ValidationError, validate, scheme, l)

    def test_dictionary_001(self):
        """ test case for dictionary #1 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        scheme = {
            'firstName': str,
            'lastName':  str
            }
        validate(scheme, d)
        d['foo'] = 10
        self.assertRaises(ValidationError, validate, scheme, d)

    def test_callables_001(self):
        d = {'x': 10}
        scheme = {'x': lambda x: x > 0}
        validate(scheme,  d)

    def test_callables_002(self):
        d = {'x': -10}
        scheme = {'x': lambda x: x > 0}
        self.assertRaises(ValidationError, validate, scheme,  d)

    def test_callables_003(self):
        d = {'x': 'boom'}
        scheme = {'x': lambda x: x > 0}
        validate(scheme, d) # NOTE what the hell, seriously!

    def test_callables_004(self):
        d = {'x': "foo"}
        scheme = {'x': lambda x: len(x) > 0}
        validate(scheme, d)

    def test_callables_005(self):
        d = {'x': 10}
        scheme = {'x': lambda x: len(x) > 0}
        self.assertRaises(ValidationError, validate, scheme, d)


class IsoDatetimeTestCase(unittest.TestCase):
    def test_validator(self):
        x = IsoDatetime()
        validate(x, datetime.datetime.now().isoformat())
        self.assertRaises(ValidationError, validate, x, datetime.date.today().isoformat())
        self.assertRaises(ValidationError, validate, x, 7)
        self.assertRaises(ValidationError, validate, x, 'some trash')
        self.assertRaises(ValidationError, validate, x, '2010')


class DecimalTextTestCase(unittest.TestCase):
    def test_validator(self):
        x = DecimalText()
        validate(x, '08.0009')
        validate(x, '198.0105')
        validate(x, '-198.0105')
        validate(x, '-0')
        validate(x, '0')
        validate(x, '0.0')
        self.assertRaises(ValidationError, validate, x, 'e2e4')
        self.assertRaises(ValidationError, validate, x, 7)
        self.assertRaises(ValidationError, validate, x, 'some trash')


class PositiveDecimalTextTestCase(unittest.TestCase):
    def test_validator(self):
        x = PositiveDecimalText()
        validate(x, '08.0009')
        validate(x, '198.0105')
        self.assertRaises(ValidationError, validate, x, 'e2e4')
        self.assertRaises(ValidationError, validate, x, 7)
        self.assertRaises(ValidationError, validate, x, 'some trash')
        self.assertRaises(ValidationError, validate, x, '-0.0')
        self.assertRaises(ValidationError, validate, x, '0.0')
        self.assertRaises(ValidationError, validate, x, '-10.06')


class NonNegativeDecimalTextTestCase(unittest.TestCase):
    def test_validator(self):
        x = NonNegativeDecimalText()
        validate(x, '08.0009')
        validate(x, '198.0105')
        validate(x, '0')
        validate(x, '0.0')
        validate(x, '-0.0')
        self.assertRaises(ValidationError, validate, x, 'e2e4')
        self.assertRaises(ValidationError, validate, x, 7)
        self.assertRaises(ValidationError, validate, x, 'some trash')
        self.assertRaises(ValidationError, validate, x, '-10.06')


class EmailTestCase(unittest.TestCase):
    def test_validator(self):
        x = EmailText()
        self.assertRaises(ValidationError, validate, x, 33)
        self.assertRaises(ValidationError, validate, x, 'xzy')
        self.assertRaises(ValidationError, validate, x, 'a-b @m.travel')
        validate(x, 'a@m.ru')
        validate(x, 'a@m.travel')
        validate(x, 'a-b@m.travel')


if __name__ == '__main__':
    unittest.main()
