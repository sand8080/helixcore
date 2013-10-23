import cx_Oracle
from functools import partial
from helixcore.db import wrapper

DSN = {
    'user': 'TEST_PG_AUTH',
    'password': 'oBOesjAWan19',
    'dsn': 'srv-integration.loyalty-partners.ru/XE',
}

get_connection = partial(cx_Oracle.connect, **DSN)
put_connection = lambda x: None
transaction = partial(wrapper.transaction, get_connection, put_connection)
