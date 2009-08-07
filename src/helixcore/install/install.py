import glob
import sys
import imp
from datetime import datetime

from helixcore.db.cond import Eq, And
from helixcore.db import query_builder, wrapper
from helixcore.db.wrapper import transaction_with_dynamic_connection_getter as transaction

import filtering

class PatchProcessor(object):
    def __init__(self, get_connection, table, path, patch_like='[1-9\-]*.py'):
        self.get_connection = get_connection
        self.table = table
        self.path = path
        self.patch_like = patch_like
        sys.path.append(self.path)

    def get_patches(self):
        names = glob.glob1(self.path, self.patch_like)
        return map(lambda x: x.replace('.py', ''), names)

    def apply(self, last_applied):
        patches = filtering.filter_forward(last_applied, None, self.get_patches())
        self.dynamic_patch_call(patches, 'apply', self.register_patch)

    def apply_all(self):
        self.apply(None)

    def revert(self, last_applied):
        patches = filtering.filter_backward(None, last_applied, self.get_patches())
        print 'patches', patches
        self.dynamic_patch_call(patches, 'revert', self.unregister_patch)

    def revert_all(self):
        self.revert(self.get_last_applied())

    def dynamic_patch_call(self, patches, executor_name, registrator):
        for p in patches:
            (file, pathname, description) = imp.find_module(p)
            try:
                m = imp.load_module(p, file, pathname, description)
                self.process_patch(p, getattr(m, executor_name), registrator)
            finally:
                file.close()

    @transaction()
    def process_patch(self, name, executor, registrator, curs=None):
        executor(curs)
        if self.is_table_exist(curs):
            registrator(curs, name)

    def register_patch(self, curs, name):
        curs.execute(*query_builder.insert(self.table, {'name': name, 'path': self.path, 'date': datetime.now()}))

    def unregister_patch(self, curs, name):
        cond = And(Eq('name', name), Eq('path', self.path))
        curs.execute(*query_builder.delete(self.table, cond=cond))

    def is_table_exist(self, curs):
        curs.execute(*query_builder.select('pg_tables', cond=Eq('tablename', self.table)))
        return len(curs.fetchall()) > 0

    @transaction()
    def get_last_applied(self, curs=None):
        if not self.is_table_exist(curs):
            return None
        else:
            curs.execute(*query_builder.select(self.table, order_by=['-id'], limit=1))
            result = wrapper.fetchall_dicts(curs)
            return result[0]['name'] if len(result) else None
