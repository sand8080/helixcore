import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.json_validator import Text, AnyOf, Optional, Scheme,\
    SimpleWrappingValidator, ListWrapperValidator, NoData, ArbitraryDict
from helixcore.json_validator.html_transformer import HtmlTransformer
from helixcore.server.api import ApiCall


class HtmlTransformerTestCase(RootTestCase):
    def test_obj_type(self):
        trans = HtmlTransformer()
        self.assertEquals(int, trans._obj_type(1))
        self.assertEquals(int, trans._obj_type(int))
        self.assertEquals(list, trans._obj_type([]))
        self.assertEquals(list, trans._obj_type(list))
        self.assertEquals(HtmlTransformer, trans._obj_type(trans))
        self.assertEquals(HtmlTransformer, trans._obj_type(HtmlTransformer))

    def test_int(self):
        trans = HtmlTransformer()
        self.assertEquals('int', trans._process(int))

    def test_process_list(self):
        trans = HtmlTransformer()
        self.assertEquals('<table class="api_list"><tr><td>[]</td></tr></table>',
            trans._process([]))
        self.assertEquals('<table class="api_list"><tr><td>[int]</td></tr></table>',
            trans._process([1]))
        self.assertEquals('<table class="api_list"><tr><td>[int, int]</td></tr></table>',
            trans._process([1, int]))

    def test_text(self):
        trans = HtmlTransformer()
        self.assertEquals('Text', trans._process(Text()))
        self.assertEquals('Text', trans._process(Text))

    def test_process_any_of(self):
        trans = HtmlTransformer()
        self.assertEquals('<table class="api_any_of">'
            '<tr class="api_any_of_case"><td>id</td></tr>'
            '<tr class="api_any_of_separator"><td>OR</td></tr>'
            '<tr class="api_any_of_case"><td>-id</td></tr></table>',
            trans._process(AnyOf('id', '-id')))
        res = trans._process(AnyOf({'id': int}, {'cd': Text}))
        self.assertEquals('<table class="api_any_of">'
                '<tr class="api_any_of_case">'
                    '<td>'
                        '<table class="api_dict">'
                            '<tr><td colspan="2">{</td></tr>'
                            '<tr>'
                                '<td class="api_dict_key">id</td>'
                                '<td class="api_dict_value">int</td>'
                            '</tr>'
                            '<tr><td colspan="2">}</td></tr>'
                        '</table>'
                    '</td>'
                '</tr>'
                '<tr class="api_any_of_separator"><td>OR</td></tr>'
                '<tr class="api_any_of_case">'
                    '<td>'
                        '<table class="api_dict">'
                            '<tr><td colspan="2">{</td></tr>'
                            '<tr>'
                                '<td class="api_dict_key">cd</td>'
                                '<td class="api_dict_value">UserPredicateValidator</td>'
                            '</tr>'
                            '<tr><td colspan="2">}</td></tr>'
                        '</table>'
                    '</td>'
                '</tr>'
            '</table>', res)

    def test_process_dict(self):
        trans = HtmlTransformer()
        self.assertEquals('<table class="api_dict"><tr><td>{}</td></tr></table>',
            trans._process({}))
        self.assertEquals('<table class="api_dict">'
            '<tr><td colspan="2">{</td></tr>'
            '<tr><td class="api_dict_key">id</td>'
            '<td class="api_dict_value">int</td></tr>'
            '<tr><td colspan="2">}</td></tr></table>',
            trans._process({'id': int}))
        self.assertEquals('<table class="api_dict">'
            '<tr><td colspan="2">{</td></tr>'
            '<tr><td class="api_dict_key">values</td>'
            '<td class="api_dict_value">'
                '<table class="api_list"><tr><td>[int]</td></tr></table>'
            '</td></tr>'
            '<tr><td colspan="2">}</td></tr></table>',
            trans._process({'values': [int]}))
        self.assertEquals('<table class="api_dict">'
            '<tr><td colspan="2">{</td></tr>'
            '<tr class="api_dict_optional">'
            '<td class="api_dict_key">id<br><span>optional</span></td>'
            '<td class="api_dict_value">int</td></tr>'
            '<tr><td colspan="2">}</td></tr></table>',
            trans._process({Optional('id'): int}))

    def test_process_simple_wrapping_validator(self):
        trans = HtmlTransformer()
        val = SimpleWrappingValidator({})
        res = trans._process_simple_wrapping_validator(val)
        self.assertEquals('<table class="api_dict"><tr><td>{}</td></tr></table>', res)

        val = SimpleWrappingValidator({'id': str})
        res = trans._process_simple_wrapping_validator(val)
        self.assertEquals('<table class="api_dict">'
            '<tr><td colspan="2">{</td></tr>'
            '<tr><td class="api_dict_key">id</td>'
            '<td class="api_dict_value">str</td></tr>'
            '<tr><td colspan="2">}</td></tr></table>', res)

    def test_process_scheme(self):
        trans = HtmlTransformer()
        sch = Scheme({})
        res = trans._process(sch)
        self.assertEquals('<table class="api_dict"><tr><td>{}</td></tr></table>', res)

        sch = Scheme({'id': int, Optional('cd'): str})
        res = trans._process(sch)
        self.assertEquals('<table class="api_dict">'
            '<tr><td colspan="2">{</td></tr>'
            '<tr class="api_dict_optional">'
            '<td class="api_dict_key">cd<br><span>optional</span></td><td class="api_dict_value">str</td></tr>'
            '<tr><td class="api_dict_key">id</td><td class="api_dict_value">int</td></tr>'
            '<tr><td colspan="2">}</td></tr></table>', res)

# # '<table class="api_dict"><tr><td colspan="2">{</td></tr><tr class="api_dict_optional"><td class="api_dict_key">cd<br><span>optional</span></td><td class="api_dict_value">str</td></tr><tr><td class="api_dict_key">id</td><td class="api_dict_value">int</td></tr><tr><td colspan="2">}</td></tr></table>'
# # '<table class="api_dict"><tr><td colspan="2">{</td></tr><tr><td class="api_dict_key">id</td><td class="api_dict_value">int</td></tr><tr class="api_dict_optional"><td class="api_dict_key">cd<br><span>optional</span></td><td class="api_dict_value">str</td></tr><tr><td colspan="2">}</td></tr></table>'

    def test_process_no_data(self):
        trans = HtmlTransformer()
        res = trans._process_no_data(NoData)
        self.assertEquals('', res)

    def test_process_list_wrapper_validator(self):
        trans = HtmlTransformer()
        val = ListWrapperValidator([])
        res = trans._process_list_wrapper_validator(val)
        self.assertEquals('<table class="api_list"><tr><td>[]</td></tr></table>', res)

        val = ListWrapperValidator([ArbitraryDict()])
        res = trans._process_list_wrapper_validator(val)
        self.assertEquals('<table class="api_list">'
            '<tr><td>[<table class="api_dict"><tr><td>{}</td></tr></table>]</td></tr>'
            '</table>', res)

    def test_process_protocol(self):
        trans = HtmlTransformer()
        protocol = [
            ApiCall('request', Scheme({'id': int})),
            ApiCall('response', Scheme({'status': AnyOf('ok', 'error')})),
        ]
        res = trans.process_protocol(protocol)
        self.assertEquals('<table class="api_protocol">'
            '<tr>'
                '<td class="api_call_name api_call_request">request</td>'
                '<td class="api_call_scheme">'
                    '<table class="api_dict">'
                        '<tr><td colspan="2">{</td></tr>'
                        '<tr>'
                            '<td class="api_dict_key">id</td>'
                            '<td class="api_dict_value">int</td>'
                        '</tr>'
                        '<tr><td colspan="2">}</td></tr>'
                    '</table>'
                '</td>'
                '<td class="api_call_description"></td>'
            '</tr>'
            '<tr>'
                '<td class="api_call_name api_call_response">response</td>'
                '<td class="api_call_scheme">'
                    '<table class="api_dict">'
                        '<tr><td colspan="2">{</td></tr>'
                        '<tr>'
                            '<td class="api_dict_key">status</td>'
                            '<td class="api_dict_value">'
                                '<table class="api_any_of">'
                                    '<tr class="api_any_of_case"><td>ok</td></tr>'
                                    '<tr class="api_any_of_separator"><td>OR</td></tr>'
                                    '<tr class="api_any_of_case"><td>error</td></tr>'
                                '</table>'
                            '</td>'
                        '</tr>'
                        '<tr><td colspan="2">}</td></tr>'
                    '</table>'
                '</td>'
                '<td class="api_call_description"></td>'
            '</tr>'
        '</table>', res)


if __name__ == '__main__':
    unittest.main()
