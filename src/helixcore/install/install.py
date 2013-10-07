import glob
import sys
import imp
import cx_Oracle
from datetime import datetime

from helixcore.db import wrapper
from helixcore.db.sql import Insert, Eq, And, Delete, Select
from helixcore.db.wrapper import transaction_with_dynamic_connection_getter as transaction

from helixcore.install import filtering


def __fetch_info(curs, table, field_name, field_value):
    q = Select(table, cond=Eq(field_name, field_value.upper()))
    curs.execute(*q.glue())
    res = curs.fetchall()
    return res


def is_table_exists(curs, table):
    return len(__fetch_info(curs, 'user_tables', 'table_name', table)) > 0


def is_sequence_exists(curs, sequence):
    return len(__fetch_info(curs, 'user_sequences', 'sequence_name', sequence)) > 0


def is_index_exists(curs, index):
    return len(__fetch_info(curs, 'user_indexes', 'index_name', index)) > 0


class PatchProcessor(object):
    def __init__(self, get_connection, put_connection, table, path, logger, patch_like='[1-9\-]*.py'):
        self.logger = logger
        self.get_connection = get_connection
        self.put_connection = put_connection
        self.table = table.upper()
        self.path = path
        self.patch_like = patch_like
        sys.path.append(self.path)

    def get_patches(self):
        names = glob.glob1(self.path, self.patch_like)
        return map(lambda x: x.replace('.py', ''), names)

    def apply(self, last_applied):
        self.logger.debug("Filtering patches greater than last applied: %s" % last_applied)
        patches = filtering.filter_forward(last_applied, None, self.get_patches())
        self.logger.debug("Patches for apply: %s" % patches)
        self.dynamic_patch_call(patches, 'apply', self.register_patch)

    def apply_all(self):
        self.logger.debug("Applying all patches")
        self.apply(None)

    def revert(self, last_applied):
        self.logger.debug("Reverting patches from %s" % last_applied)
        if not self.is_revert_will_processed() or last_applied is None:
            self.logger.debug("Nothing to be reverted")
            return
        patches = filtering.filter_backward(None, last_applied, self.get_patches())
        self.dynamic_patch_call(patches, 'revert', self.unregister_patch)

    def revert_all(self):
        self.logger.debug("Reverting all patches")
        self.revert(self.get_last_applied())

    def dynamic_patch_call(self, patches, executor_name, registrator):
        self.logger.debug("Dynamic patch call for executor %s" % executor_name)
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
        if is_table_exists(curs, self.table):
            registrator(curs, name)

    def register_patch(self, curs, name):
        self.logger.debug("Registering patch %s", name)
        q = Insert(self.table, {'name': name, 'path': self.path, 'application_date': datetime.now()})
        self.logger.debug("Insert sql: %s, %s" % q.glue())
        id_var = curs.var(cx_Oracle.NUMBER)
        sql, params = q.glue()
        curs.execute(sql, params + [id_var])
        ins_id = int(id_var.getvalue())
        self.logger.debug("Patch %s registered with id: %s" % (name, ins_id))

    def unregister_patch(self, curs, name):
        cond = And(Eq('name', name), Eq('path', self.path))
        q = Delete(self.table, cond=cond)
        curs.execute(*q.glue())

    @transaction()
    def is_revert_will_processed(self, curs=None):
        self.logger.debug("Checking revert is required")
        result = is_table_exists(curs, self.table)
        self.logger.debug("Revert is required: %s" % result)
        return result

    # def is_table_exist(self, curs):
    #     self.logger.debug("Checking is table %s exist" % self.table)
    #
    #     q = Select('user_tables', cond=Eq('table_name', self.table))
    #     curs.execute(*q.glue())
    #     res = is_table_exists(curs, self.table)
    #     is_exist = len(res) > 0
    #     self.logger.debug("Is table %s exist: %s" % (self.table, is_exist))
    #     return is_exist

    @transaction()
    def get_last_applied(self, curs=None):
        self.logger.debug("Getting last applied patch")
        if not is_table_exists(curs, self.table):
            return None
        else:
            q = Select(self.table, order_by=['-id'], limit=1)
            curs.execute(*q.glue())
            result = wrapper.fetchall_dicts(curs)
            return result[0]['NAME'] if len(result) else None


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


def execute(cmd_name, get_connection_func, put_connection_func, patch_table_name, patches_path, logger):
    patch_processor = PatchProcessor(get_connection_func, put_connection_func, patch_table_name, patches_path, logger)
    COMMANDS[cmd_name](patch_processor)
