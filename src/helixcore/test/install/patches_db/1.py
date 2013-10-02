from helixcore.install.install import is_sequence_exists, is_table_exists
from helixcore.test.install.test_install import PatchProcessorTestCase


table = PatchProcessorTestCase.table
sequence = '%s_seq' % table


def apply(curs):
    print "Creating table %s" % table
    sql = 'CREATE TABLE %(table)s (' \
          'id NUMBER NOT NULL,' \
          'name varchar2(200 CHAR),' \
          'path varchar2(200 CHAR),' \
          'application_date date,' \
          'PRIMARY KEY (id)' \
          ')' % {'table': table}
    curs.execute(sql)
    print "Creating sequence %s" % sequence
    curs.execute('CREATE SEQUENCE %s' % sequence)


def revert(curs):
    if is_sequence_exists(curs, sequence):
        print "Dropping sequence %s" % sequence
        curs.execute('DROP SEQUENCE %s' % sequence)
    if is_table_exists(curs, table):
        print "Dropping table %s" % table
        curs.execute('DROP TABLE %s' % table)

