import glob
import sys
import imp
from datetime import datetime

from helixcore.db.sql import Eq, And, Insert, Select, Delete
from helixcore.db import wrapper
from helixcore.db.wrapper import transaction_with_dynamic_connection_getter as transaction

import filtering


class PatchProcessor(object):
    def __init__(self, get_connection, put_connection, table, path, patch_like='[1-9\-]*.py'):
        self.get_connection = get_connection
        self.put_connection = put_connection
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
        if not self.is_revert_will_processed() or last_applied is None:
            return
        patches = filtering.filter_backward(None, last_applied, self.get_patches())
        self.dynamic_patch_call(patches, 'revert', self.unregister_patch)

    def revert_all(self):
        self.revert(self.get_last_applied())

    def dynamic_patch_call(self, patches, executor_name, registrator):
        for p in patches:
            (f, pathname, description) = imp.find_module(p)
            try:
                m = imp.load_module(p, f, pathname, description)
                self.process_patch(p, getattr(m, executor_name), registrator)
            finally:
                f.close()

    @transaction()
    def process_patch(self, name, executor, registrator, curs=None):
        executor(curs)
        if self.is_table_exist(curs):
            registrator(curs, name)

    def register_patch(self, curs, name):
        q = Insert(self.table, {'name': name, 'path': self.path, 'date': datetime.now()})
        curs.execute(*q.glue())

    def unregister_patch(self, curs, name):
        cond = And(Eq('name', name), Eq('path', self.path))
        q = Delete(self.table, cond=cond)
        curs.execute(*q.glue())

    @transaction()
    def is_revert_will_processed(self, curs=None):
        return self.is_table_exist(curs)

    def is_table_exist(self, curs):
        q = Select('pg_tables', cond=Eq('tablename', self.table))
        curs.execute(*q.glue())
        return len(curs.fetchall()) > 0

    @transaction()
    def get_last_applied(self, curs=None):
        if not self.is_table_exist(curs):
            return None
        else:
            q = Select(self.table, order_by=['-id'], limit=1)
            curs.execute(*q.glue())
            result = wrapper.fetchall_dicts(curs)
            return result[0]['name'] if len(result) else None


def update(patch_processor):
    patch_processor.apply(patch_processor.get_last_applied())

def reinit(patch_processor):
    patch_processor.revert_all()
    patch_processor.apply_all()

def revert(patch_processor):
    patch_processor.revert_all()

COMMANDS = {
    'update': update,
    'reinit': reinit,
    'revert': revert,
}

def execute(cmd_name, get_connection_func, put_connection_func, patch_table_name, patches_path):
    patch_processor = PatchProcessor(get_connection_func, put_connection_func, patch_table_name, patches_path)
    COMMANDS[cmd_name](patch_processor)
