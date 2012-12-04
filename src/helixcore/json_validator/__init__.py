'''
Created on Apr 22, 2010

It is a drop-in replacement for validol by Konstantin Merenkov.
The main advantage of this module is its clean design and readable implementation,
extensive error reporting on validation failures with path to failed element.
May be, it's a little slower though...

@author: andrew
'''
import re
import iso8601 #@UnresolvedImport
from decimal import Decimal
import decimal


### errors ###

class ValidationError(Exception):
    '''
    Contains info about validation failure
    '''
    def __init__(self, comment, path):
        '''
        @ivar comment: error message from failed validator
        @ivar path: path to failed element. List of element names and indices.
        '''
        super(ValidationError, self).__init__('Validation failed: %s. Path to failed element: %s' % (comment, path))
        self.path = list(path)
        self.comment = comment

    def get_path(self):
        return self.path

    def get_comment(self):
        return self.comment


### key modifiers for dict schemas ###

@property
def undefined_property(_):
    raise NotImplementedError


class _Key(object):
    '''
    Abstract class for dict key modifier.
    '''

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    # bool. if this modifier allows absent element in data dict
    allows_absent = undefined_property


class Optional(_Key):
    '''
    Key modifier for optional element in dict
    '''

    allows_absent = True


class Mandatory(_Key):
    '''
    Key modifier for mandatory element in dict. Default.
    '''

    allows_absent = False


### validators ###

class ValueValidator(object):
    '''
    Abstract class for all validators
    '''
    def validate(self, data, path):
        '''
        @return: void
        @raise ValidationError: on validation failure
        @param data: actual data to be validated against this validator
        @param path: list of key names and indices representing path to validated element in the entire data structure passed to root validator
        '''
        raise NotImplementedError


class Any(ValueValidator):
    '''
    Validates all.
    '''
    def validate(self, data, path):
        pass


class NoData(ValueValidator):
    '''
    Fails validation. Data just must not be present, this validator must not be called
    '''
    def validate(self, data, path):
        raise ValidationError('No data must be present at this location', path)


class ArbitraryDict(ValueValidator):
    '''
    Validates dict containing arbitrary structure. Elements of dict are not validated.
    '''
    def validate(self, value, path):
        if type(value) is not dict:
            raise ValidationError('Data must be a dict of arbitrary structure', path)


class DictWrapperValidator(ValueValidator):
    def __init__(self, scheme_dict):
        '''
        @param scheme_dict: initial dict of key_name -> validator. Data will be validated against scheme dict
        @ivar scheme_list: list of tuples [(KeyModifier, ValueValidator), ...]
        '''
        super(DictWrapperValidator, self).__init__()
        self.scheme_list = [
            (self._create_key_modifier(raw_key), create_validator(raw_validator))
            for raw_key, raw_validator in scheme_dict.iteritems()
        ]

    def _create_key_modifier(self, key):
        '''
        @return: _Key object built from possibly bare (string) key
        '''
        klass = getattr(key, '__class__', None)
        if klass and issubclass(klass, _Key):
            return key
        return Mandatory(key)

    def validate(self, data, path):
        '''
        @param data: dict of key -> value to validate against this validator
        '''
        if type(data) is not dict:
            raise ValidationError('Data must be a dictionary', path)

        handled_keys = set()
        for (key_mod, validator) in self.scheme_list:
            key_str = str(key_mod)
            path.append(key_str)

            if key_str in data:
                validator.validate(data[key_str], path)
                handled_keys.add(key_str)
            else:
                if not key_mod.allows_absent:
                    raise ValidationError('Element %s must be present in dict' % key_str, path)

            path.pop()

        not_handled_keys = set(data).difference(handled_keys)
        if len(not_handled_keys) > 0:
            raise ValidationError('%d dict elements does not match schema. These element names are: %s' % (len(not_handled_keys), not_handled_keys), path)


class ListWrapperValidator(ValueValidator):
    def __init__(self, scheme_list):
        '''
        @param scheme_list: initial list, containing at most one validator. (If none given, NoData() validator will be used - list must be empty).
        @ivar member_validator: Data members will be validated against this validator.
        '''
        super(ListWrapperValidator, self).__init__()
        if len(scheme_list) == 0:
            scheme_list = [NoData()]
        if len(scheme_list) != 1:
            raise NotImplementedError('Can configure list validator against only one member validator')
        self.member_validator = create_validator(scheme_list[0])

    def validate(self, data, path):
        '''
        @param data: list of values to validate against this member validator
        '''
        if type(data) is not list:
            raise ValidationError('Data must be a list', path)

        for i, item in enumerate(data):
            path.append(str(i))
            self.member_validator.validate(item, path)
            path.pop()


class TupleWrapperValidator(ValueValidator):
    def __init__(self, scheme_tuple):
        '''
        @param scheme_tuple: initial tuple, containing validators. Each data members will be validated against the corresponding member validator.
        '''
        super(TupleWrapperValidator, self).__init__()
        self.member_validators = map(create_validator, scheme_tuple)

    def validate(self, data, path):
        '''
        @param data: list of values to validate against this member validator
        '''
        if type(data) is not tuple:
            raise ValidationError('Data must be a tuple', path)
        if len(self.member_validators) != len(data):
            raise ValidationError('Data must contain exactly %d elements' % len(self.member_validators), path)

        for i, (item, validator) in enumerate(zip(data, self.member_validators)):
            path.append(str(i))
            validator.validate(item, path)
            path.pop()


class AtomicTypeWrapperValidator(ValueValidator):
    def __init__(self, scheme_type):
        '''
        @param scheme_type: atomic type name. Data must be of this type.
        '''
        super(AtomicTypeWrapperValidator, self).__init__()
        self.scheme_type = scheme_type

    def validate(self, data, path):
        '''
        @param data: value of atomic type self.scheme_type
        '''
        if type(data) != self.scheme_type:
            raise ValidationError('Type of value must be %s' % self.scheme_type, path)


class EqualityValidator(ValueValidator):
    def __init__(self, target_value):
        '''
        @param target_value: some target value. Data must be equal to this value (data == value).
        '''
        super(EqualityValidator, self).__init__()
        self.target_value = target_value

    def validate(self, data, path):
        '''
        @param data: value to validate
        '''
        if data != self.target_value:
            raise ValidationError('Value must be equal to %s' % self.target_value, path)


class UserPredicateValidator(ValueValidator):
    def __init__(self, pred):
        '''
        @param pred: Unary callable returning bool. Will be called on data.
        '''
        super(UserPredicateValidator, self).__init__()
        self.pred = pred

    def validate(self, data, path):
        '''
        @param data: value satisfying self.pred
        '''
        res = False
        try:
            res = self.pred(data)
        except Exception, e:
            raise ValidationError('Value must satisfy given predicate %s, but check failed: %s' % (self.pred, e), path)

        if not res:
            raise ValidationError('Value must satisfy given predicate %s' % self.pred, path)


class AnyOf(ValueValidator):
    def __init__(self, *validators):
        '''
        @param validators: validators data will be validated against.
        '''
        super(AnyOf, self).__init__()
        self.validators = map(create_validator, validators)

    def validate(self, data, path):
        '''
        @param data: must be valid against at least one of self.validators
        '''
        thrown_excs = []
        for v in self.validators:
            try:
                v.validate(data, list(path))
            except ValidationError, e:
                #print 'AnyOf: not validated by %s: %s' % (v, data)
                thrown_excs.append(e)

        if len(thrown_excs) == len(self.validators):
            failures = '; '.join([ '%s (path: %s)' % (e.get_comment(), e.get_path()) for e in thrown_excs ])
            comment = 'Data must satisfy to any of validators, all of them failed: %s' % failures
            raise ValidationError(comment, path)


class RegexpValidator(ValueValidator):
    def __init__(self, pattern, flags=0):
        '''
        @param pattern: pattern like in re.compile() function
        @param flags: flags like in re.compile() function
        '''
        super(RegexpValidator, self).__init__()
        self.match_obj = re.compile(pattern, flags)

    def validate(self, data, path):
        '''
        @param data: value matching self.pattern
        '''
        if not self.match_obj.match(data):
            raise ValidationError('Value must match given regular expression %s' % self.match_obj.pattern, path)


class RegexpCompiledValidator(ValueValidator):
    def __init__(self, match_obj):
        '''
        @param regexp: instance of re.match object
        '''
        super(RegexpCompiledValidator, self).__init__()
        self.match_obj = match_obj

    def validate(self, data, path):
        '''
        @param data: value matching self.match_obj
        '''
        if not self.match_obj.match(data):
            raise ValidationError('Value must match given regular expression %s' % self.match_obj.pattern, path)


class IsoDatetime(ValueValidator):
    '''
    Validates if data is correct iso8601 datetime string.
    '''
    def validate(self, data, path):
        try:
            iso8601.parse_date(data)
        except (iso8601.iso8601.ParseError, TypeError):
            raise ValidationError('value must be a correct ISO 8601 datetime string', path)


class IsoDate(ValueValidator):
    '''
    Special case of IsoDatetime. Accepts date only in ISO 8601 format
    Validates if data is correct date string in format 'yyyy-mm-dd'.
    '''
    date_pattern = re.compile(
        '^'
        '(?P<year>\d\d\d\d)'
        '-'
        '(?P<month>\d\d)'
        '-'
        '(?P<day>\d\d)'
        '(?P<timezone>Z|([+-]\d\d(.\d\d)?))?'
        '$'
    )

    def validate(self, data, path):
        m = self.date_pattern.match(data)
        if not m:
            raise ValidationError('Value %s must be a correct ISO 8601 date string' % data, path)


class Text(ValueValidator):
    '''
    Validates textual data (str or unicode type).
    '''
    def validate(self, data, path):
        AnyOf(str, unicode).validate(data, path)


class NullableText(Text):
    '''
    Validates either text or None
    '''
    def validate(self, data, path):
        if data is None:
            return
        super(NullableText, self).validate(data, path)


class DecimalText(Text):
    '''
    Validates if data is correct string representation of decimal.
    '''
    def validate(self, data, path):
        super(DecimalText, self).validate(data, path)
        try:
            Decimal(data)
        except decimal.DecimalException:
            raise ValidationError('Value %s must be a correct string representation of decimal' % data, path)


class PositiveDecimalText(DecimalText):
    '''
    Validates if data is correct string representation of positive decimal.
    '''
    def validate(self, data, path):
        super(PositiveDecimalText, self).validate(data, path)
        if Decimal(data) <= 0:
            raise ValidationError('Value %s must be a correct string representation of positive decimal' %
                data, path)


class NonNegativeDecimalText(DecimalText):
    '''
    Validates if data is correct string representation of non negative decimal.
    '''
    def validate(self, data, path):
        super(NonNegativeDecimalText, self).validate(data, path)
        if Decimal(data) < 0:
            raise ValidationError('Value %s must be a correct string representation of non negative decimal' %
                data, path)


class NullableDecimalText(Text):
    '''
    Validates either decimal or None
    '''
    def validate(self, data, path):
        if data is None:
            return
        super(NullableDecimalText, self).validate(data, path)


class SimpleWrappingValidator(ValueValidator):
    '''
    Abstract class for validators that just wrap another validator class, and possibly perform some additional checks
    '''
    def __init__(self, validator):
        '''
        @ivar validator: wrapped ValueValidator object
        '''
        super(SimpleWrappingValidator, self).__init__()
        self.validator = create_validator(validator)

    def validate(self, data, path):
        '''
        Just delegate validation to self.validator
        '''
        self.validator.validate(data, path)

    def __repr__(self):
        return 'scheme %s' % self.validator


class Scheme(SimpleWrappingValidator):
    '''
    For backward compatibility with validol. Just wraps single validator object.
    '''
    pass


class Positive(SimpleWrappingValidator):
    """
    Validates if data > 0.
    If such comparison operator is not applicable to data you will get compile error
    """
    def validate(self, data, path):
        super(Positive, self).validate(data, path)
        if not data > 0:
            raise ValidationError('Value %s must be positive' % data, path)


class NonNegative(SimpleWrappingValidator):
    """
    Validates if data >= 0.
    If such comparison operator is not applicable to data you will get compile error
    """
    def validate(self, data, path):
        super(NonNegative, self).validate(data, path)
        if not data >= 0:
            raise ValidationError('Value %s must be positive' % data, path)


class EmailText(RegexpCompiledValidator, Text):
    '''
    Validates if data is correct string representation of email.
    '''
    def __init__(self):
        match_obj = re.compile(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,6})$')
        super(EmailText, self).__init__(match_obj)

    def validate(self, data, path):
        Text.validate(self, data, path)
        RegexpCompiledValidator.validate(self, data, path)


### factory ###

atomic_types = set([str, unicode, int, bool, float])
def create_validator(obj):
    '''
    Creates ValueValidator object out of any type.
    @return: ValueValidator
    '''
    if hasattr(obj, '__class__') and issubclass(obj.__class__, ValueValidator):
        return obj

    obj_type = type(obj)

    if obj_type is dict:
        return DictWrapperValidator(obj)
    if obj_type is list:
        return ListWrapperValidator(obj)
    if obj_type is tuple:
        return TupleWrapperValidator(obj)
    if obj in atomic_types:
        return AtomicTypeWrapperValidator(obj)
    if obj is object:
        return Any()
    if callable(obj):
        return UserPredicateValidator(obj)
    # this f##king SRE_Pattern, why can't I f##king kill it
    if hasattr(obj, 'match') and hasattr(obj, 'search'):
        return RegexpCompiledValidator(obj)

    return EqualityValidator(obj)

### main function ###

def validate(scheme, data):
    '''
    Validates data against scheme.
    @return: void
    @raise ValidationError: if validation failed
    '''
    create_validator(scheme).validate(data, [])


ARBITRARY_DICT = ArbitraryDict()
ISO_DATE = IsoDate()
ISO_DATETIME = IsoDatetime()
TEXT = Text()
NULLABLE_TEXT = NullableText()
NULLABLE_INT = AnyOf(None, int)
NULLABLE_DECIMAL_TEXT = NullableDecimalText()
DECIMAL_TEXT = DecimalText()
POSITIVE_DECIMAL_TEXT = PositiveDecimalText()
NON_NEGATIVE_DECIMAL_TEXT = NonNegativeDecimalText()
NON_NEGATIVE_INT = NonNegative(int)
POSITIVE_INT = Positive(int)
ID = POSITIVE_INT
INT = int
BOOLEAN = bool
EMAIL = EmailText()