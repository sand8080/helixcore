import buildhelpers
from utils import lists_from_dict

def select(table, columns=None, cond=None, group_by=None, order_by=None, limit=None, offset=0, for_update=False):
    where_str, where_params = buildhelpers.where(cond)
    sql = 'SELECT %(target)s FROM %(table)s %(where)s %(group_by)s %(order_by)s %(limit)s %(offset)s %(locking)s' % {
        'target': '*' if columns is None else buildhelpers.quote_list(columns),
        'table': buildhelpers.quote(table),
        'where': where_str,
        'group_by': ''  if group_by is None else 'GROUP BY %s' % buildhelpers.quote_list(group_by),
        'limit': ''  if limit is None else 'LIMIT %d' % limit,
        'offset': ''  if offset == 0 else 'OFFSET %d' % offset,
        'order_by': buildhelpers.order(order_by),
        'locking': ''  if not for_update else 'FOR UPDATE',
    }
    return sql.strip(), where_params

def update(table, updates, cond=None):
    update_columns, update_params = lists_from_dict(updates)
    where_str, where_params = buildhelpers.where(cond)
    sql = 'UPDATE %(table)s SET %(updates)s %(where)s' % {
        'table': buildhelpers.quote(table),
        'updates': ','.join('%s = %%s' % buildhelpers.quote(c) for c in update_columns),
        'where': where_str,
    }
    return sql.strip(), update_params + where_params

def delete(table, cond=None):
    where_str, where_params = buildhelpers.where(cond)
    sql = 'DELETE FROM %(table)s %(where)s' % {
        'table': buildhelpers.quote(table),
        'where': where_str,
    }
    return sql.strip(), where_params

def insert(table, inserts):
    insert_columns, insert_params = lists_from_dict(inserts)
    sql = 'INSERT INTO %(table)s (%(columns)s) VALUES (%(values)s)' % {
        'table': buildhelpers.quote(table),
        'columns': ','.join(map(buildhelpers.quote, insert_columns)),
        'values': ','.join('%s' for c in insert_columns),
    }
    return sql.strip(), insert_params
