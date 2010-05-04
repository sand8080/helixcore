import warnings
warnings.warn('Use objects from helixcore.db.sql inststead.', category=DeprecationWarning)

from sql import Select, Update, Delete, Insert


def select(table, columns=None, cond=None, group_by=None, order_by=None, limit=None, offset=0, for_update=False):
    obj = Select(table, columns, cond, group_by, order_by, limit, offset, for_update)
    return obj.glue()

def update(table, updates, cond=None):
    obj = Update(table, updates, cond)
    return obj.glue()

def delete(table, cond=None):
    obj = Delete(table, cond)
    return obj.glue()

def insert(table, inserts):
    obj = Insert(table, inserts)
    return obj.glue()
