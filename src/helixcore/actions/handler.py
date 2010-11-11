from helixcore import mapping
from helixcore.error import RequestProcessingError
from functools import wraps


def detalize_error(err_cls, fields):
    '''
    Tries to execute function fields, catches exception of class err_cls
    and converts it to RequestProcessingError of given category
    '''
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except err_cls, e:
                code = getattr(e, 'code', 'HELIXAUTH_ERROR')
                f = fields if isinstance(fields, list) else [fields]
                raise RequestProcessingError('; '.join(e.args),
                    code=code, fields=f)
        return decorated
    return decorator


class AbstractHandler(object):
    def get_fields_for_update(self, data, prefix_of_new='new_'):
        '''
        If data contains fields with prefix == prefix_of_new,
        such fields will be added into result dict:
            {'field': 'new_field'}
        '''
        result = {}
        for f in data.keys():
            if f.startswith(prefix_of_new):
                result[f[len(prefix_of_new):]] = f
        return result

    def update_obj(self, curs, data, load_obj_func):
        to_update = self.get_fields_for_update(data)
        if len(to_update):
            obj = load_obj_func()
            for f, new_f in to_update.items():
                setattr(obj, f, data[new_f])
            mapping.update(curs, obj)

    def objects_info(self, objects, viewer):
        result = []
        for o in objects:
            result.append(viewer(o))
        return result
