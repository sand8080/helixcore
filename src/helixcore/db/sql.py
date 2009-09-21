import buildhelpers
from utils import lists_from_dict

class NullLeaf(object):
    """
    Empty leaf condition
    """
    def glue(self):
        return ('', [])


class Any(object):
    """
    lh = ANY (rh)
    """
    def __init__(self, lh, rh):
        self.lh = lh
        self.rh = rh

    def glue(self):
        return (
            '%%s = ANY (%s)' % self.rh,
            [self.lh]
        )


class Leaf(object):
    """
    Leaf condition
    """
    def __init__(self, lh, oper, rh):
        self.lh = lh
        self.oper = oper
        self.rh = rh

    def glue(self):
        if hasattr(self.rh, 'glue'):
            nested_cond, params = self.rh.glue()
            cond = '%s %s %s' % (buildhelpers.quote(self.lh), self.oper, nested_cond)
        else:
            cond = '%s %s %%s' % (buildhelpers.quote(self.lh), self.oper)
            params = [self.rh]
        return cond, params


class Eq(Leaf):
    """
    Alias for leaf equality condition
    """
    def __init__(self, lh, rh):
        super(Eq, self).__init__(lh, '=', rh)


class MoreEq(Leaf):
    """
    lh >= rh
    """
    def __init__(self, lh, rh):
        super(MoreEq, self).__init__(lh, '>=', rh)


class LessEq(Leaf):
    """
    lh <= rh
    """
    def __init__(self, lh, rh):
        super(LessEq, self).__init__(lh, '<=', rh)


class Less(Leaf):
    """
    lh < rh
    """
    def __init__(self, lh, rh):
        super(Less, self).__init__(lh, '<', rh)


class More(Leaf):
    """
    lh > rh
    """
    def __init__(self, lh, rh):
        super(More, self).__init__(lh, '>', rh)


class Scoped(object):
    """
    (cond)
    """
    def __init__(self, cond):
        self.cond = cond

    def glue(self):
        cond, params = self.cond.glue()
        return ('(%s)' % cond, params)


class In(object):
    """
    IN (values)
    """
    def __init__(self, param, values):
        self.param = param
        self.values = values

    def glue(self):
        in_str = ','.join(['%s' for _ in self.values])
        cond = '%s IN (%s)' % (buildhelpers.quote(self.param), in_str)
        return cond, self.values


class Composite(object):
    def __init__(self, lh, oper, rh):
        self.lh = lh
        self.oper = oper
        self.rh = rh

    def glue(self):
        if isinstance(self.lh, NullLeaf):
            return self.rh.glue()
        elif isinstance(self.rh, NullLeaf):
            return self.lh.glue()
        else:
            cond_lh, params_lh = self.lh.glue()
            cond_rh, params_rh = self.rh.glue()
            return (
                '%s %s %s' % (cond_lh, self.oper, cond_rh),
                params_lh + params_rh
            )


class And(Composite):
    def __init__(self, lh, rh):
        super(And, self).__init__(lh, 'AND', rh)


class Or(Composite):
    def __init__(self, lh, rh):
        super(Or, self).__init__(lh, 'OR', rh)


class Columns(object):
    COUNT_ALL = buildhelpers.Unquoted('COUNT(*)')


class Select(object):
    def __init__(self, table, columns=None, cond=None, group_by=None, order_by=None,
        limit=None, offset=0, for_update=False):
        self.table = table
        self.columns = columns
        self.cond = cond
        self.group_by = group_by
        self.order_by = order_by
        self.limit = limit
        self.offset = offset
        self.for_update = for_update

    def glue(self):
        where_str, where_params = buildhelpers.where(self.cond)
        sql = 'SELECT %(target)s FROM %(table)s %(where)s %(group_by)s %(order_by)s %(limit)s %(offset)s %(locking)s' % {
            'target': '*' if self.columns is None else buildhelpers.quote_list(self.columns),
            'table': buildhelpers.quote(self.table),
            'where': where_str,
            'group_by': ''  if self.group_by is None else 'GROUP BY %s' % buildhelpers.quote_list(self.group_by),
            'limit': ''  if self.limit is None else 'LIMIT %d' % self.limit,
            'offset': ''  if self.offset == 0 else 'OFFSET %d' % self.offset,
            'order_by': buildhelpers.order(self.order_by),
            'locking': ''  if not self.for_update else 'FOR UPDATE',
        }
        return sql.strip(), where_params


class Update(object):
    def __init__(self, table, updates, cond=None):
        self.table = table
        self.updates = updates
        self.cond = cond

    def glue(self):
        update_columns, update_params = lists_from_dict(self.updates)
        where_str, where_params = buildhelpers.where(self.cond)
        sql = 'UPDATE %(table)s SET %(updates)s %(where)s' % {
            'table': buildhelpers.quote(self.table),
            'updates': ','.join('%s = %%s' % buildhelpers.quote(c) for c in update_columns),
            'where': where_str,
        }
        return sql.strip(), update_params + where_params


class Delete(object):
    def __init__(self, table, cond=None):
        self.table = table
        self.cond = cond

    def glue(self):
        where_str, where_params = buildhelpers.where(self.cond)
        sql = 'DELETE FROM %(table)s %(where)s' % {
            'table': buildhelpers.quote(self.table),
            'where': where_str,
        }
        return sql.strip(), where_params


class Insert(object):
    def __init__(self, table, inserts):
        self.table = table
        self.inserts = inserts

    def glue(self):
        insert_columns, insert_params = lists_from_dict(self.inserts)
        sql = 'INSERT INTO %(table)s (%(columns)s) VALUES (%(values)s)' % {
            'table': buildhelpers.quote(self.table),
            'columns': ','.join(map(buildhelpers.quote, insert_columns)),
            'values': ','.join('%s' for _ in insert_columns),
        }
        return sql.strip(), insert_params
