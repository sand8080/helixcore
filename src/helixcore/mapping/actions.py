from helixcore.db import query_builder
from helixcore.db.wrapper import fetchone_dict, fetchall_dicts
from helixcore.db.sql import Eq
import helixcore.db.deadlock_detector as deadlock_detector

class MappingError(Exception):
    pass

def get(curs, cls, cond, for_update=False):
    if for_update:
        deadlock_detector.handle_lock(cls.table)
    curs.execute(*query_builder.select(cls.table, cond=cond, for_update=for_update))
    return cls(**fetchone_dict(curs))

def get_list(curs, cls, cond, order_by='id', limit=None, offset=0, for_update=False):
    '''
    Selects list of objects, without lock
    @return: list of objects selected.
    '''
    curs.execute(*query_builder.select(cls.table, cond=cond, for_update=for_update, order_by=order_by, limit=limit, offset=offset))
    dicts_list = fetchall_dicts(curs)
    return [cls(**d) for d in dicts_list]

def get_fields(obj):
    return dict((n, getattr(obj, n)) for n in obj.__slots__ if hasattr(obj, n))

def insert(curs, obj):
    if hasattr(obj, 'id'):
        raise MappingError('Inserting %s with id %s' % (obj.__class__.__name__, obj.id))
    curs.execute(*query_builder.insert(obj.table, get_fields(obj)))
    obj.id = fetchone_dict(curs)['id']
#    curs.execute("select currval('%s_id_seq')" % obj.table)
#    obj.id = fetchone_dict(curs)['currval']

def update(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Updating %s without id' % obj.__class__.__name__)
    curs.execute(*query_builder.update(obj.table, get_fields(obj), cond=Eq('id', obj.id)))

def delete(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Deleting %s without id' % obj.__class__.__name__)
    curs.execute(*query_builder.delete(obj.table, cond=Eq('id', obj.id)))
    del obj.id

def reload(curs, obj, for_update=False):
    if not hasattr(obj, 'id'):
        raise MappingError('Reloading %s without id' % obj.__class__.__name__)
    return get(curs, obj.__class__, Eq('id', obj.id), for_update)
