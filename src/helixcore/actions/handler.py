import datetime
from functools import wraps

from helixcore import mapping
from helixcore.error import RequestProcessingError


def execution_time(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        start = datetime.datetime.now()
        resp = func(*args, **kwargs)
        end = datetime.datetime.now()
        td = end - start
        resp['execution_time'] = '%s.%s' % (td.seconds, td.microseconds)
        return resp
    return decorated


def detalize_error(err_cls, fields):
    '''
    Tries to execute function fields, catches exception of class err_cls
    and converts it to RequestProcessingError with given code
    '''
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except err_cls, e:
                code = getattr(e, 'code', 'HELIX_ERROR')
                f = fields if isinstance(fields, list) else [fields]
                raise RequestProcessingError('; '.join(e.args),
                    code=code, fields=f)
        return decorated
    return decorator


def set_subject_users_ids(field_name):
    '''
    Sets subject users ids to data for correct action logging
    '''
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                data = args[1]
                users_ids = data.get(field_name)
                if users_ids is not None:
                    if isinstance(users_ids, list):
                        data['subject_users_ids'] = list(set(users_ids))
                    else:
                        data['subject_users_ids'] = [users_ids]
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

    def update_objs(self, curs, data, load_obj_func):
        to_update = self.get_fields_for_update(data)
        updated_objs = []
        if len(to_update):
            objs = load_obj_func()
            if not isinstance(objs, (list, tuple)):
                objs = [objs]
            for obj in objs:
                for f, new_f in to_update.items():
                    setattr(obj, f, data[new_f])
                mapping.update(curs, obj)
                updated_objs.append(obj)
        return updated_objs

    update_obj = update_objs

    def objects_info(self, objects, viewer):
        result = []
        for o in objects:
            result.append(viewer(o))
        return result
