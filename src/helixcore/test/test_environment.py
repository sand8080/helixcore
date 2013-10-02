import cx_Oracle
from functools import partial
from helixcore.db import wrapper

DSN = {
    'user': 'pg_test',
    'password': 'lsDf#2cv',
    'dsn': 'dm01-scan.malina.local/CommTEST',
}

get_connection = partial(cx_Oracle.connect, **DSN)
put_connection = lambda x: None
transaction = partial(wrapper.transaction, get_connection, put_connection)
