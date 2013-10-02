import cx_Oracle
import datetime

from helixcore.db.sql import Insert
from helixcore.install.install import is_sequence_exists, is_table_exists
from helixcore.test.test_environment import transaction


@transaction()
def create_table(table, curs=None):
    seq = '%s_seq' % table
    curs.execute('CREATE TABLE %s (id NUMBER, name VARCHAR(200 CHAR), date_field date)' % table)
    curs.execute('CREATE SEQUENCE %s' % seq)


@transaction()
def drop_table(table, curs=None):
    seq = '%s_seq' % table
    if is_sequence_exists(curs, seq):
        curs.execute('DROP SEQUENCE %s' % seq)
    if is_table_exists(curs, table):
        curs.execute('DROP TABLE %s' % table)


@transaction()
def fill_table(table, num_records=5, curs=None):
    result = []
    for i in xrange(num_records):
        id_var = curs.var(cx_Oracle.NUMBER)
        q = Insert(table, {'name': i, 'date_field': datetime.datetime.now()})
        sql, params = q.glue()
        curs.execute(sql, params + [id_var])
        result.append(int(id_var.getvalue()))
    return result

