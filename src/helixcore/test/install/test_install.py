import unittest
import os

from helixcore.install.install import PatchProcessor, is_table_exists, is_sequence_exists, is_index_exists
from helixcore.test.test_environment import get_connection, put_connection, transaction
from helixcore.db import wrapper
from helixcore.db.sql import Select
from helixcore.test.utils_for_testing import console_logger


class PatchProcessorTestCase(unittest.TestCase):
    path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'patches_db')
    table = 'test_patch'

    def setUp(self):
        self.processor = PatchProcessor(get_connection, put_connection, self.table, self.path, console_logger)

    @transaction()
    def get_patches_list(self, curs=None):
        curs.execute(*Select(self.processor.table, order_by=['-id']).glue())
        return wrapper.fetchall_dicts(curs)

    @transaction()
    def test_is_table_exists(self, curs=None):
        table = 'test_is_table_exists'
        try:
            sql = 'CREATE TABLE %s (id NUMBER)' % table
            curs.execute(sql)
            self.assertTrue(is_table_exists(curs, table))
        finally:
            sql = 'DROP TABLE %s' % table
            curs.execute(sql)
        self.assertFalse(is_table_exists(curs, table))

    @transaction()
    def test_is_index_exists(self, curs=None):
        table = 'test_is_index_exists'
        index = '%s_idx' % table
        try:
            sql = 'CREATE TABLE %s (id NUMBER NOT NULL)' % table
            curs.execute(sql)
            self.assertTrue(is_table_exists(curs, table))
            sql = 'CREATE UNIQUE INDEX %(index)s ON %(table)s(id)' % {'table': table, 'index': index}
            curs.execute(sql)
            self.assertTrue(is_index_exists(curs, index))
        finally:
            sql = 'DROP INDEX %s' % index
            curs.execute(sql)
            sql = 'DROP TABLE %s' % table
            curs.execute(sql)
        self.assertFalse(is_index_exists(curs, table))
        self.assertFalse(is_table_exists(curs, table))

    @transaction()
    def test_is_sequence_exists(self, curs=None):
        sequence = 'test_is_sequence_exists'
        try:
            sql = 'CREATE SEQUENCE %s' % sequence
            curs.execute(sql)
            self.assertTrue(is_sequence_exists(curs, sequence))
        finally:
            sql = 'DROP SEQUENCE %s' % sequence
            curs.execute(sql)
        self.assertFalse(is_sequence_exists(curs, sequence))

    def test_get_patches(self):
        try:
            self.processor.revert_all()
            self.processor.apply_all()
            self.assertEqual(len(self.processor.get_patches()), len(self.get_patches_list()))
        finally:
            self.processor.revert_all()

    def test_get_last_applied(self):
        try:
            self.processor.revert_all()
            self.processor.apply_all()
            last_applied = self.processor.get_last_applied()
            self.assertEqual('2', last_applied)
        finally:
            self.processor.revert_all()

    def test_patches_without_db(self):
        patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'patches_no_action')
        processor = PatchProcessor(get_connection, put_connection, '___', patches_path, console_logger)
        try:
            processor.revert_all()
            processor.apply_all()
        finally:
            processor.revert_all()
            self._drop_patches()

    @transaction()
    def _drop_patches(self, curs=None):
        sequence = '%s_seq' % self.table
        if is_sequence_exists(curs, sequence):
            curs.execute('DROP SEQUENCE %s' % sequence)
        if is_table_exists(curs, self.table):
            curs.execute('DROP TABLE %s' % self.table)


if __name__ == '__main__':
    unittest.main()
