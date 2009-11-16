from helixcore.db.wrapper import fetchone_dict, fetchall_dicts, EmptyResultSetError
from helixcore.db.sql import Eq, And, Select, Insert, Update, Delete
import helixcore.db.deadlock_detector as deadlock_detector
from helixcore.server.exceptions import DataIntegrityError


class MappingError(Exception):
    pass


def get(curs, cls, cond, for_update=False):
    if for_update:
        deadlock_detector.handle_lock(cls.table)
    curs.execute(*Select(cls.table, cond=cond, for_update=for_update).glue())
    return cls(**fetchone_dict(curs))


def get_list(curs, cls, cond, order_by='id', limit=None, offset=0, for_update=False):
    '''
    Selects list of objects, without lock
    @return: list of objects selected.
    '''
    curs.execute(*Select(cls.table, cond=cond, for_update=for_update, order_by=order_by, limit=limit, offset=offset).glue())
    dicts_list = fetchall_dicts(curs)
    return [cls(**d) for d in dicts_list]


def get_fields(obj):
    return dict((n, getattr(obj, n)) for n in obj.__slots__ if hasattr(obj, n))


def insert(curs, obj):
    if hasattr(obj, 'id'):
        raise MappingError('Inserting %s with id %s' % (obj.__class__.__name__, obj.id))
    curs.execute(*Insert(obj.table, get_fields(obj)).glue())
    obj.id = fetchone_dict(curs)['id']


def update(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Updating %s without id' % obj.__class__.__name__)
    curs.execute(*Update(obj.table, get_fields(obj), cond=Eq('id', obj.id)).glue())


def delete(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Deleting %s without id' % obj.__class__.__name__)
    curs.execute(*Delete(obj.table, cond=Eq('id', obj.id)).glue())
    del obj.id


def reload(curs, obj, for_update=False): #IGNORE:W0622
    if not hasattr(obj, 'id'):
        raise MappingError('Reloading %s without id' % obj.__class__.__name__)
    return get(curs, obj.__class__, Eq('id', obj.id), for_update)


def get_obj_by_fields(curs, cls, fields, for_update):
    '''
    Returns object of class cls by anded conditions from fields.
    fields is dictionary of {field: value}
    '''
    and_cond = None
    for k, v in fields.items():
        eq_cond = Eq(k, v)
        if and_cond is None:
            and_cond = eq_cond
        else:
            and_cond = And(and_cond, eq_cond)
    try:
        return get(curs, cls, and_cond, for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('%s with %s not found in system' % (cls, fields))

def get_obj_by_field(curs, cls, field, value, for_update):
    return get_obj_by_fields(curs, cls, {field: value}, for_update)