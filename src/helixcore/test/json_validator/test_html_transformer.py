import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.json_validator import Text, AnyOf, Optional, Scheme,\
    SimpleWrappingValidator
from helixcore.json_validator.html_transformer import HtmlTransformer
from helixcore.server.api import ApiCall


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
        self.assertEquals('<table class="api_any_of">'
            '<tr class="api_any_of_case"><td>id</td></tr>'
            '<tr class="api_any_of_separator"><td>OR</td></tr>'
            '<tr class="api_any_of_case"><td>-id</td></tr></table>',
            self.trans._process(AnyOf('id', '-id')))
        res = self.trans._process(AnyOf({'id': int}, {'cd': Text}))
        self.assertEquals('<table class="api_any_of">'
            '<tr class="api_any_of_case"><td>'
                '<table class="api_dict"><tr><td class="api_dict_key">id</td>'
                '<td class="api_dict_value">int</td></tr></table>'
            '</td></tr>'
            '<tr class="api_any_of_separator"><td>OR</td></tr>'
            '<tr class="api_any_of_case"><td>'
                '<table class="api_dict"><tr><td class="api_dict_key">cd</td>'
                '<td class="api_dict_value">UserPredicateValidator</td></tr></table>'
            '</td></tr>'
        '</table>', res)

    def test_process_dict(self):
        self.assertEquals('<table class="api_dict"></table>',
            self.trans._process({}))
        self.assertEquals('<table class="api_dict"><tr><td class="api_dict_key">id</td>'
            '<td class="api_dict_value">int</td></tr></table>',
            self.trans._process({'id': int}))
        self.assertEquals('<table class="api_dict"><tr><td class="api_dict_key">values</td>'
            '<td class="api_dict_value"><span class="api_list">[int]</span></td></tr></table>',
            self.trans._process({'values': [int]}))
        self.assertEquals('<table class="api_dict"><tr class="api_dict_optional">'
            '<td class="api_dict_key">id<br><span>optional</span></td>'
            '<td class="api_dict_value">int</td></tr></table>',
            self.trans._process({Optional('id'): int}))

    def test_process_simple_wrapping_validator(self):
        val = SimpleWrappingValidator({})
        res = self.trans._process_simple_wrapping_validator(val)
        self.assertEquals('<table class="api_dict"></table>', res)

        val = SimpleWrappingValidator({'id': str})
        res = self.trans._process_simple_wrapping_validator(val)
        self.assertEquals('<table class="api_dict"><tr><td class="api_dict_key">id</td>'
            '<td class="api_dict_value">str</td></tr></table>', res)

    def test_process_scheme(self):
        sch = Scheme({})
        res = self.trans._process(sch)
        self.assertEquals('<table class="api_dict"></table>', res)

        sch = Scheme({'id': int, Optional('cd'): str})
        res = self.trans._process(sch)
        self.assertEquals('<table class="api_dict"><tr class="api_dict_optional">'
            '<td class="api_dict_key">cd<br><span>optional</span></td><td class="api_dict_value">str</td></tr>'
            '<tr><td class="api_dict_key">id</td><td class="api_dict_value">int</td></tr></table>', res)

    def test_process_protocol(self):
        protocol = [
            ApiCall('request', Scheme({'id': int})),
            ApiCall('response', Scheme({'status': AnyOf('ok', 'error')})),
        ]
        result = self.trans.process_protocol(protocol)
        self.assertEquals('<table class="api_protocol">'
            '<tr><td class="api_call_name">request</td>'
            '<td class="api_call_scheme">'
                '<table class="api_dict">'
                    '<tr><td class="api_dict_key">id</td>'
                    '<td class="api_dict_value">int</td></tr>'
                '</table>'
            '</td>'
            '<td class="api_call_description">None</td></tr>'
            '<tr><td class="api_call_name">response</td>'
            '<td class="api_call_scheme">'
                '<table class="api_dict">'
                    '<tr><td class="api_dict_key">status</td>'
                    '<td class="api_dict_value">'
                        '<table class="api_any_of">'
                            '<tr class="api_any_of_case"><td>ok</td></tr>'
                            '<tr class="api_any_of_separator"><td>OR</td></tr>'
                            '<tr class="api_any_of_case"><td>error</td></tr>'
                        '</table>'
                    '</td></tr>'
                '</table>'
            '</td><td class="api_call_description">None</td></tr></table>',
            result)


if __name__ == '__main__':
    unittest.main()
