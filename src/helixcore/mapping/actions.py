from helixcore.db import query_builder
from helixcore.db.wrapper import fetchone_dict
from helixcore.db.cond import Eq

class MappingError(Exception):
    pass

def get(curs, cls, cond, for_update=False):
    curs.execute(*query_builder.select(cls.table, cond=cond, for_update=for_update))
    return cls(**fetchone_dict(curs))

def get_fields(obj):
    return dict((n, getattr(obj, n)) for n in obj.__slots__ if hasattr(obj, n))

def insert(curs, obj):
    if hasattr(obj, 'id'):
        raise MappingError('Inserting %s with id %s' % (obj.__class__.__name__, obj.id))
    curs.execute(*query_builder.insert(obj.table, get_fields(obj)))
    curs.execute("select currval('%s_id_seq')" % obj.table)
    obj.id = fetchone_dict(curs)['currval']

def update(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Updating %s without id' % obj.__class__.__name__)
    curs.execute(*query_builder.update(obj.table, get_fields(obj), cond=Eq('id', obj.id)))

def delete(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Deleting %s without id' % obj.__class__.__name__)
    curs.execute(*query_builder.delete(obj.table, cond=Eq('id', obj.id)))
    del obj.id

