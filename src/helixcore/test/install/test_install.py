import unittest
import os

from helixcore.install.install import PatchProcessor
from helixcore.test.helpers import get_connection, transaction
from helixcore.db import query_builder, wrapper

class PatchProcessorTestCase(unittest.TestCase):
    path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        'patches_db'
    )

    table = 'test_patch'

    def setUp(self):
        self.processor = PatchProcessor(get_connection, self.table, self.path)
#        self.processor.revert(self.processor.get_last_applied())

    @transaction()
    def get_patches_list(self, curs=None):
        curs.execute(*query_builder.select(self.processor.table, order_by=['-id']))
        return wrapper.fetchall_dicts(curs)

    def test_get_patches(self):
        try:
            self.processor.apply_all()
            self.assertEqual(len(self.processor.get_patches()), len(self.get_patches_list()))
        finally:
            self.processor.revert_all()

    @transaction()
    def test_table_not_exist(self, curs=None):
        self.processor = PatchProcessor(get_connection, 'fake_table', self.path)
        self.assertFalse(self.processor.is_table_exist(curs))

    @transaction()
    def test_table_exist(self, curs=None):
        self.processor = PatchProcessor(get_connection, 'fake_test_table', self.path)
        try:
            curs.execute('CREATE TABLE %s (id int)' % self.processor.table)
            self.assertTrue(self.processor.is_table_exist(curs))
        finally:
            curs.execute('DROP TABLE %s' % self.processor.table)

    def test_get_last_applied(self):
        try:
            self.processor.apply_all()
            last_applied = self.processor.get_last_applied()
            self.assertEqual('2', last_applied)
        finally:
            self.processor.revert_all()

    def test_patches_without_db(self):
        patches_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'patches_no_action'
        )
        processor = PatchProcessor(get_connection, '___', patches_path)
        processor.apply_all()
        processor.revert_all()

if __name__ == '__main__':
    unittest.main()