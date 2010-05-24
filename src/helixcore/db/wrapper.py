from helixcore.utils import dict_from_lists
from helixcore.db import deadlock_detector


class DbError(Exception):
    pass


class EmptyResultSetError(DbError):
    pass


class ObjectNotFound(DbError):
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
    '''
    @return: Single rowset as dict.
    @raise SelectedMoreThanOneRow: if curs contains more than one row
    @raise EmptyResultSetError: if curs contains no rows
    '''
    if curs.rowcount > 1:
        raise SelectedMoreThanOneRow()
    if curs.rowcount == 0:
        raise EmptyResultSetError('Nothing to be fetched')
    return fetch_dict(curs)


def fetch_dict(curs):
    '''@return: next rowset as dict. None if no rowsets in cursor
    '''
    if curs.rowcount > 1:
        raise SelectedMoreThanOneRow()
    if curs.rowcount == 0:
        raise EmptyResultSetError('Nothing to be fetched')
    columns = [info[0] for info in curs.description]
    values = curs.fetchone()
    return dict_from_lists(columns, values)


def transaction(get_conn, put_conn):
    def decorator(fun):
        def decorated(*args, **kwargs):
            conn = get_conn()
            try:
                curs = conn.cursor()
                kwargs['curs'] = curs
                result = fun(*args, **kwargs)
                _end_trans(curs)
                conn.commit()
                return result
            except Exception, e:
                import sys, traceback
                traceback.print_exc(file=sys.stderr)
                _end_trans(curs)
                conn.rollback()
                raise e
            finally:
                put_conn(conn)
        return decorated
    return decorator


def transaction_with_dynamic_connection_getter():
    def decorator(fun):
        def decorated(self, *args, **kwargs):
            assert hasattr(self, 'get_connection')
            conn = self.get_connection()
            try:
                curs = conn.cursor()
                kwargs['curs'] = curs
                result = fun(self, *args, **kwargs)
                _end_trans(curs)
                conn.commit()
                return result
            except Exception, e:
                _end_trans(curs)
                conn.rollback()
                raise e
            finally:
                self.put_connection(conn)
        return decorated
    return decorator


def _end_trans(curs):
    curs.close()
    deadlock_detector.clear_context()
