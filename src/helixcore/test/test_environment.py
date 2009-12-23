import psycopg2
from functools import partial
from helixcore.db import wrapper

DSN = {
    'user': 'helixtest',
    'database': 'helixtest',
    'host': 'localhost',
    'password': 'qazwsx'
}

get_connection = partial(psycopg2.connect, **DSN)
transaction = partial(wrapper.transaction, get_connection)
