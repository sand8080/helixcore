from helixcore.json_validator import (AnyOf, EqualityValidator,
    DictWrapperValidator, Optional, AtomicTypeWrapperValidator,
    Scheme, ListWrapperValidator, NoData, ArbitraryDict)


class HtmlTransformer(object):
    def _obj_type(self, obj):
        if isinstance(obj, type):
            return obj
        else:
            return type(obj)

    def _process_list(self, objs):
        elems = []
        for o in objs:
            elems.append(self._process(o))
        return '<table class="api_list"><tr><td>[%s]</td></tr></table>' % ', '.join(elems)

    def _process_dict(self, obj):
        result = '<table class="api_dict">%s</table>'
        rows = []
        if isinstance(obj, dict):
            items = obj.items()
        elif isinstance(obj, DictWrapperValidator):
            items = obj.scheme_list
        elif isinstance(obj, ArbitraryDict):
            items = []
        if len(items):
            rows.append('<tr><td colspan="2">{</td></tr>')
            for name, o in items:
                if isinstance(name, Optional):
                    row = '<tr class="api_dict_optional">' \
                        '<td class="api_dict_key">%s<br><span>optional</span></td>' \
                        '<td class="api_dict_value">%s</td></tr>'
                else:
                    row = '<tr><td class="api_dict_key">%s</td>' \
                        '<td class="api_dict_value">%s</td></tr>'
                rows.append(row % (name, self._process(o)))
            rows.append('<tr><td colspan="2">}</td></tr>')
        else:
            rows.append('<tr><td>{}</td></tr>')
        return result % ''.join(rows)

    def _process_any_of(self, obj):
        result = '<table class="api_any_of">%s</table>'
        rows = []
        for o in obj.validators:
            r = self._process(o)
            rows.append('<tr class="api_any_of_case"><td>%s</td></tr>' % r)
        s_rows = '<tr class="api_any_of_separator"><td>OR</td></tr>'.join(rows)
        return result % s_rows

    def _process_equality_validator(self, validator):
        return '%s' % validator.target_value

    def _process_simple_wrapping_validator(self, validator):
        return self._process(validator.validator)

    def _process_no_data(self, validator):
        return ''

    def _process_list_wrapper_validator(self, validator):
        return '<table class="api_list"><tr><td>[%s]</td></tr></table>' % self._process(validator.member_validator)

    def _process(self, obj):
        obj_type = self._obj_type(obj)
        if obj_type is list:
            return self._process_list(obj)
        elif obj_type is AnyOf:
            return self._process_any_of(obj)
        elif obj_type in (dict, DictWrapperValidator, ArbitraryDict):
            return self._process_dict(obj)
        elif obj_type is EqualityValidator:
            return self._process_equality_validator(obj)
        elif obj_type is AtomicTypeWrapperValidator:
            return obj.scheme_type.__name__
        elif obj_type is Scheme:
            return self._process_simple_wrapping_validator(obj)
        elif obj_type is ListWrapperValidator:
            return self._process_list_wrapper_validator(obj)
        elif obj_type is NoData:
            return self._process_no_data(obj)
        else:
            return obj_type.__name__

    def process_protocol(self, protocol):
        rows = []
        for api_call in protocol:
            sch = self._process(api_call.scheme)
            row = '<tr><td class="api_call_name">%s</td>' \
                '<td class="api_call_scheme">%s</td>' \
                '<td class="api_call_description">%s</td></tr>' % (api_call.name,
                sch, api_call.description)
            rows.append(row)
        result = '<table class="api_protocol">%s</table>' % ''.join(rows)
        return result

