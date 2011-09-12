import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.json_validator import Text, AnyOf
from helixcore.json_validator.html_transformer import HtmlTransformer
#from helixcore.json_validator import (validate, AnyOf, Optional, Scheme, ValueValidator,
#    Text, IsoDatetime, DecimalText, ArbitraryDict, ValidationError,
#    PositiveDecimalText)


class HtmlTransformerTestCase(RootTestCase):
    trans = HtmlTransformer()

    def test_obj_type(self):
        self.assertEquals(int, self.trans._obj_type(1))
        self.assertEquals(int, self.trans._obj_type(int))
        self.assertEquals(list, self.trans._obj_type([]))
        self.assertEquals(list, self.trans._obj_type(list))
        self.assertEquals(HtmlTransformer, self.trans._obj_type(self.trans))
        self.assertEquals(HtmlTransformer, self.trans._obj_type(HtmlTransformer))

    def test_int(self):
        self.assertEquals('int', self.trans._process(int))

    def test_process_list(self):
        self.assertEquals('<span class="api_list">[]</span>', self.trans._process([]))
        self.assertEquals('<span class="api_list">[int]</span>', self.trans._process([1]))
        self.assertEquals('<span class="api_list">[int, int]</span>', self.trans._process([1, int]))

    def test_text(self):
        self.assertEquals('Text', self.trans._process(Text()))
        self.assertEquals('Text', self.trans._process(Text))

    def test_process_any_of(self):
        self.assertEquals('<table class="api_any_of">' \
            '<tr class="api_any_of_case"><td>id</td></tr>' \
            '<tr class="api_any_of_separator"><td>OR</td></tr>' \
            '<tr class="api_any_of_case"><td>-id</td></tr></table>',
            self.trans._process(AnyOf('id', '-id')))


if __name__ == '__main__':
    unittest.main()
