import psycopg2
from functools import partial
from helixcore.db import wrapper

DSN = {
    'user': 'helixtest',
    'database': 'test_helixcore',
    'host': 'localhost',
    'password': 'qazwsx'
}

get_connection = partial(psycopg2.connect, **DSN)
put_connection = lambda x: None
transaction = partial(wrapper.transaction, get_connection, put_connection)
