from helixcore.json_validator import AnyOf, EqualityValidator,\
    DictWrapperValidator, Mandatory, Optional


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
        return '<span class="api_list">[%s]</span>' % ', '.join(elems)

    def _process_dict(self, obj):
        result = '<table class="api_dict">%s</table>'
        rows = []
        for name, o in obj.items():
            if isinstance(name, Optional):
                key_css_class = 'api_dict_key_optional'
            else:
                key_css_class = 'api_dict_key'
            rows.append('<tr><td class="%s">%s</td>'
                '<td class="api_dict_value">%s</td></tr>' % (key_css_class,
                    name, self._process(o)))
        return result % ''.join(rows)

    def _process_any_of(self, obj):
        result = '<table class="api_any_of">%s</table>'
        rows = []
#        print '###', obj.validators, type(obj.validators)
        for o in obj.validators:
            rows.append(self._process(o))
        s_rows = '<tr class="api_any_of_separator"><td>OR</td></tr>'.join(rows)
        return result % s_rows

    def _process_equality_validator(self, validator):
        return '<tr class="api_any_of_case"><td>%s</td></tr>' % validator.target_value

    def _process_dict_validator(self, validator):
        pass
#        result = '<table class="api_dict">%s</table>'
#        rows = []
#        for k, v in validator.scheme_list:
#            if isinstance(k, Optional):
#            row = '<tr class="api_any_of_separator"><td>OR</td></tr>'.join(rows)
#            rows.append()
#        return '<tr class="api_any_of_case"><td>%s</td></tr>' % validator.target_value

    def _process(self, obj):
        obj_type = self._obj_type(obj)
        if obj_type is list:
            return self._process_list(obj)
        elif obj_type is AnyOf:
            return self._process_any_of(obj)
        elif obj_type is dict:
            return self._process_dict(obj)
        elif obj_type is EqualityValidator:
            return self._process_equality_validator(obj)
        elif obj_type is DictWrapperValidator:
            return self._process_dict_validator(obj)
        else:
            return obj_type.__name__