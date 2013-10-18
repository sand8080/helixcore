import cx_Oracle
from cx_Oracle import IntegrityError

from helixcore.db.sql import Eq, And, Select, Insert, Update, Delete
from helixcore.db.wrapper import fetchone_dict, fetchall_dicts, fetch_dict, DbError, ObjectCreationError,\
    ObjectDeletionError
import helixcore.db.deadlock_detector as deadlock_detector
from helixcore.error import DataIntegrityError


class MappingError(DbError):
    pass


def get(curs, cls, cond, for_update=False):
    if for_update:
        deadlock_detector.handle_lock(cls.table)
    curs.execute(*Select(cls.table, cond=cond, for_update=for_update).glue())
    return cls(**fetchone_dict(curs))


def get_list(curs, cls, cond, order_by='id', limit=None, offset=0, for_update=False,
             join_cond=None):
    """
    Selects list of objects
    @return: list of objects selected.
    """
    if for_update:
        deadlock_detector.handle_lock(cls.table)
    curs.execute(*Select(cls.table, cond=cond, for_update=for_update, order_by=order_by, limit=limit,
                         offset=offset, join_cond=join_cond).glue())
    dicts_list = fetchall_dicts(curs)

    if for_update and len(dicts_list) > 1:
        deadlock_detector.handle_lock(cls.table)

    non_strict = join_cond is not None
    return [cls(non_strict=non_strict, **d) for d in dicts_list]


def exec_for_each(curs, func, cls, cond, order_by='id', limit=None, offset=0):
    """
    Executes callback unary function for each selected object.
    practically, not applicable for for-update queries, cause we cannot use cursor between fetches
    (i.e. to save objects)
    """
    curs.execute(*Select(cls.table, cond=cond, for_update=False, order_by=order_by, limit=limit, offset=offset).glue())
    while True:
        d = fetch_dict(curs)
        if d is None:
            break
        func(cls(**d))


def get_fields(obj):
    return dict((n, getattr(obj, n)) for n in obj.__slots__ if hasattr(obj, n))


def insert(curs, obj):
    if hasattr(obj, 'id'):
        raise ObjectCreationError('Object %s id %s already exists' % (obj, obj.id))
    try:
        id_var = curs.var(cx_Oracle.NUMBER)
        sql, params = Insert(obj.table, get_fields(obj)).glue()
        curs.execute(sql, params + [id_var])
        obj.id = int(id_var.getvalue())
    except IntegrityError, e:
        # e.args in cx_Oracle is not strings
        raise ObjectCreationError("Object can't be created: %s" % '; '.join(map(str, e.args)))


def update(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Updating %s without id' % obj.__class__.__name__)
    try:
        curs.execute(*Update(obj.table, get_fields(obj), cond=Eq('id', obj.id)).glue())
    except IntegrityError, e:
        # e.args in cx_Oracle is not strings
        raise DataIntegrityError("Object %s updating error: %s" % (obj, ';'.join(map(str, e.args))))


def save(curs, obj):
    if hasattr(obj, 'id'):
        update(curs, obj)
    else:
        insert(curs, obj)


def delete(curs, obj):
    if not hasattr(obj, 'id'):
        raise MappingError('Deleting %s without id' % obj.__class__.__name__)
    try:
        curs.execute(*Delete(obj.table, cond=Eq('id', obj.id)).glue())
        del obj.id
    except IntegrityError, e:
        raise ObjectDeletionError('Object %s deleting error: %s' %
            (obj, ';'.join(e.args)))


def delete_objects(curs, objs):
    for o in objs:
        delete(curs, o)


def reload(curs, obj, for_update=False): #IGNORE:W0622
    if not hasattr(obj, 'id'):
        raise MappingError('Reloading %s without id' % obj.__class__.__name__)
    return get(curs, obj.__class__, Eq('id', obj.id), for_update)


def get_obj_by_fields(curs, cls, fields, for_update):
    """
    Returns object of class cls by anded conditions from fields.
    fields is dictionary of {field: value}
    """
    and_cond = None
    for k, v in fields.items():
        eq_cond = Eq(k, v)
        if and_cond is None:
            and_cond = eq_cond
        else:
            and_cond = And(and_cond, eq_cond)
    return get(curs, cls, and_cond, for_update)


def get_obj_by_field(curs, cls, field, value, for_update):
    return get_obj_by_fields(curs, cls, {field: value}, for_update)
