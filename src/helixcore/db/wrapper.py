from helixcore.utils import dict_from_lists
from helixcore.db import deadlock_detector


class DbError(Exception):
    pass


class EmptyResultSetError(DbError):
    pass


class SelectedMoreThanOneRow(DbError):
    def __init__(self):
        super(SelectedMoreThanOneRow, self).__init__('Selected more than one row.')


class ObjectCreationError(DbError):
    pass


def fetchall_dicts(curs):
    """
    Fetches all results and makes list of dicts with column names as keys
    """
    records = curs.fetchall()
    columns = [info[0] for info in curs.description]
    return [dict_from_lists(columns, rec) for rec in records]


def fetchone_dict(curs):
    if curs.rowcount > 1:
        raise SelectedMoreThanOneRow()
    if curs.rowcount == 0:
        raise EmptyResultSetError('Nothing to be fetched')
    columns = [info[0] for info in curs.description]
    values = curs.fetchone()
    return dict_from_lists(columns, values)


def transaction(get_conn):
    def decorator(fun):
        def decorated(*args, **kwargs):
            conn = get_conn()
            curs = conn.cursor()
            kwargs['curs'] = curs
            try:
                result = fun(*args, **kwargs)
                _end_trans(curs)
                conn.commit()
                return result
            except:
                _end_trans(curs)
                conn.rollback()
                raise
        return decorated
    return decorator


def transaction_with_dynamic_connection_getter():
    def decorator(fun):
        def decorated(self, *args, **kwargs):
            assert hasattr(self, 'get_connection')
            conn = self.get_connection()
            curs = conn.cursor()
            kwargs['curs'] = curs
            try:
                result = fun(self, *args, **kwargs)
                _end_trans(curs)
                conn.commit()
                return result
            except :
                _end_trans(curs)
                conn.rollback()
                raise
        return decorated
    return decorator


def _end_trans(curs):
    curs.close()
    deadlock_detector.clear_context()
