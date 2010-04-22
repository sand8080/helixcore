'''
Created on Apr 16, 2010

@author: andrew
'''
from helixcore import mapping
from helixcore.server.errors import RequestProcessingError

def detalize_error(err_cls, category, f_name):
    '''Tries to execute function f_name, catches exception of class err_cls and converts it to RequestProcessingError of given category
    '''
    def decorator(func):
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except err_cls, e:
                raise RequestProcessingError(category, e.message,
                    details=[{'field': f_name, 'message': e.message}])
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
