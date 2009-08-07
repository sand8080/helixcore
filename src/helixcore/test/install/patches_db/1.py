from helixcore.test.install.test_install import PatchProcessorTestCase
table = PatchProcessorTestCase.table

def apply(curs):
    print 'Creating table %s' % table
    curs.execute(
        'CREATE TABLE %s ('
        'id serial,'
        'name varchar,'
        'path varchar,'
        'date timestamp'
        ')' % table
    )

def revert(curs):
    print 'Dropping table %s' % table
    curs.execute('DROP TABLE IF EXISTS %s' % table)

