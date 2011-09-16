from helixcore.json_validator import AnyOf, EqualityValidator


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
            rows.append('<tr><td class="api_dict_key">%s</td>'
                '<td class="api_dict_value">%s</td></tr>' % (name, self._process(o)))
        return result % ''.join(rows)

    def _process_any_of(self, obj):
        result = '<table class="api_any_of">%s</table>'
        rows = []
        for o in obj.validators:
            if isinstance(o, EqualityValidator):
                rows.append('<tr class="api_any_of_case"><td>%s</td></tr>' % o.target_value)
        s_rows = '<tr class="api_any_of_separator"><td>OR</td></tr>'.join(rows)
        return result % s_rows

    def _process(self, obj):
        obj_type = self._obj_type(obj)
        if obj_type is list:
            return self._process_list(obj)
        elif obj_type is AnyOf:
            return self._process_any_of(obj)
        elif obj_type is dict:
            return self._process_dict(obj)
        else:
            return obj_type.__name__