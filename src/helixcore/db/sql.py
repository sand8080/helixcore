from helixcore.utils import lists_from_dict


def quote(val, quotechar='"', splitter='.'):
    return  splitter.join(
        x.startswith(quotechar) and
        x.endswith(quotechar) and
        x or '%s%s%s' % (quotechar, x, quotechar)
        for x in val.split(splitter)
    )


class SqlNode(object):
    def glue(self):
        '''
        @return: tuple (sql, params) where
        sql - SQL statement (string),
        params - list of query parameters
        '''
        raise NotImplementedError


class Column(SqlNode):
    def __init__(self, name):
        self.name = name

    def glue(self):
        return quote(self.name), []


class Parameter(SqlNode):
    def __init__(self, param):
        self.param = param

    def glue(self):
        return '%s', [self.param]


class Terminal(SqlNode):
    def __init__(self, term):
        self.term = term

    def glue(self):
        return self.term, []


def glue_col(obj):
    '''
    Glue function, by default treats argument as SQL column name.
    Provides specialization for calling on terminal nodes (not derived from SqlNode class).
    @param obj: object (either SqlNode or column name) to glue
    @return tuple (sql, params) - sql representation of object
    '''
    if isinstance(obj, SqlNode):
        return obj.glue()

    if obj is None:
        return 'NULL', [];

    return Column(obj).glue()


def glue_param(obj):
    '''
    Glue function, by default treats argument as a string terminal.
    Provides specialization for calling on terminal nodes (not derived from SqlNode class).
    @param obj: object (either SqlNode or string terminal) to glue
    @return tuple (sql, params) - sql representation of object
    '''
    if isinstance(obj, SqlNode):
        return obj.glue()

    if obj is None:
        return 'NULL', [];

    return Parameter(obj).glue()


class NullLeaf(SqlNode):
    """
    Empty leaf condition
    """
    def glue(self):
        return '', []

class BinaryExpr(SqlNode):
    def __init__(self, lh, rh):
        super(BinaryExpr, self).__init__()
        self.lh = lh
        self.rh = rh

    def _merge_parts(self):
        '''
        @return: tuple(left_glued_cond, right_glued_cond, all_params)
        '''
        nested_cond_l, nested_params_l = glue_col(self.lh)
        nested_cond_r, nested_params_r = glue_param(self.rh)
        return nested_cond_l, nested_cond_r, nested_params_l + nested_params_r

class Any(SqlNode):
    """
    val = ANY (col)
    """
    def __init__(self, val, col):
        self.val = val
        self.col = col
    def glue(self):
        nested_cond_val, nested_params_val = glue_param(self.val)
        nested_cond_col, nested_params_col = glue_col(self.col)
        cond = '%s = ANY (%s)' % (nested_cond_val, nested_cond_col)
        return cond, nested_params_val + nested_params_col


class BinaryOperator(BinaryExpr):
    """
    Binary operator: lh operator rh
    """
    def __init__(self, lh, oper, rh):
        super(BinaryOperator, self).__init__(lh, rh)
        self.oper = oper

    def glue(self):
        left_glued_cond, right_glued_cond, all_params = self._merge_parts()
        cond = '%s %s %s' % (left_glued_cond, self.oper, right_glued_cond)
        return cond, all_params


class Like(BinaryOperator):
    """
    Alias for LIKE SQL condition.
    @param rh: pattern with wildcards, ex. '*dffdf*'
    """
    def __init__(self, lh, rh, case_sensitive=False):
        if rh is None:
            super(Like, self).__init__(lh, 'IS', rh)
        else:
            rh = rh.replace('%', '\%').replace('*', '%');
            super(Like, self).__init__(lh, case_sensitive and 'LIKE' or 'ILIKE', rh)

class Eq(BinaryOperator):
    """
    Alias for leaf equality condition
    """
    def __init__(self, lh, rh):
        if rh is None:
            super(Eq, self).__init__(lh, 'IS', rh)
        else:
            super(Eq, self).__init__(lh, '=', rh)


class MoreEq(BinaryOperator):
    """
    lh >= rh
    """
    def __init__(self, lh, rh):
        super(MoreEq, self).__init__(lh, '>=', rh)


class LessEq(BinaryOperator):
    """
    lh <= rh
    """
    def __init__(self, lh, rh):
        super(LessEq, self).__init__(lh, '<=', rh)


class Less(BinaryOperator):
    """
    lh < rh
    """
    def __init__(self, lh, rh):
        super(Less, self).__init__(lh, '<', rh)


class More(BinaryOperator):
    """
    lh > rh
    """
    def __init__(self, lh, rh):
        super(More, self).__init__(lh, '>', rh)


class Scoped(SqlNode):
    """
    (cond)
    """
    def __init__(self, cond):
        super(Scoped, self).__init__()
        self.cond = cond

    def glue(self):
        cond, params = self.cond.glue()
        return ('(%s)' % cond, params)


class In(SqlNode):
    """
    IN (values)
    """
    def __init__(self, param, values):
        super(In, self).__init__()
        self.param = param
        self.values = values

    def glue(self):
        if not self.values:
            return 'False', []
        params = []
        in_str = ''
        if isinstance(self.values, SqlNode):
            in_str, params = self.values.glue()
        else:
            in_str = ','.join(['%s' for _ in self.values])
            params = self.values
        col_sql, col_params = glue_col(self.param)
        cond = '%s IN (%s)' % (col_sql, in_str)
        return cond, col_params + params


class Composite(SqlNode):
    def __init__(self, lh, oper, rh):
        super(Composite, self).__init__()
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

### sql functions (aggregate and simple)

class Function(SqlNode):
    def __init__(self, fn_name, expr):
        self.fn_name = fn_name
        self.expr = expr
    def glue(self):
        sql, params = glue_col(self.expr)
        return ('%s(%s)' % (self.fn_name, sql)), params


class Count(Function):
    def __init__(self, expr):
        super(Count, self).__init__('COUNT', expr)


class Length(Function):
    def __init__(self, expr):
        super(Length, self).__init__('length', expr)


class Columns(object):
    COUNT_ALL = Count(Terminal('*'))


class ColumnsList(SqlNode):
    def __init__(self, c):
        if c is None:
            self.columns_list = [Terminal('*')]
            return
        elif isinstance(c, str):
            self.columns_list = [c]
            return
        self.columns_list = c

    def glue(self):
        cols, _ = zip(*map(glue_col, self.columns_list))
        return ','.join(cols), []


class Where(SqlNode):
    def __init__(self, cond):
        self.cond = cond
    def glue(self):
        if self.cond is None:
            return '', []
        sql, params = glue_param(self.cond)
        if sql == '':
            return sql, params
        return ('WHERE %s' % sql), params


class OrderBy(SqlNode):
    def __init__(self, columns):
        self.columns = columns
        if isinstance(self.columns, str):
            self.columns = [self.columns]
    def glue(self):
        if self.columns is None:
            return '', []
        orders = []
        for o in self.columns:
            col = o
            dir = 'ASC'
            if o.startswith('-'):
                col = o[1:]
                dir = 'DESC'
            sql, _ = glue_col(col)
            orders.append('%s %s' % (sql, dir))
        return 'ORDER BY %s' % ','.join(orders), []


class GroupBy(SqlNode):
    def __init__(self, columns):
        self.columns = columns
        if isinstance(self.columns, str):
            self.columns = [self.columns]
    def glue(self):
        if self.columns is None:
            return '', []
        groups = []
        for o in self.columns:
            groups.append(glue_col(o)[0])
        return 'GROUP BY %s' % ','.join(groups), []


class Select(SqlNode):
    def __init__(self, table, columns=None, cond=None, group_by=None, order_by=None,
        limit=None, offset=0, for_update=False):
        super(Select, self).__init__()
        self.table = table
        self.columns = columns
        self.cond = cond
        self.group_by = group_by
        self.order_by = order_by
        self.limit = limit
        self.offset = offset
        self.for_update = for_update

    def glue(self):
        where_str, where_params = Where(self.cond).glue()
        sql = 'SELECT %(target)s FROM %(table)s %(where)s %(group_by)s %(order_by)s %(limit)s %(offset)s %(locking)s' % {
            'target': ColumnsList(self.columns).glue()[0],
            'table': quote(self.table),
            'where': where_str,
            'group_by': GroupBy(self.group_by).glue()[0],
            'limit': ''  if self.limit is None else 'LIMIT %d' % self.limit,
            'offset': ''  if self.offset == 0 else 'OFFSET %d' % self.offset,
            'order_by': OrderBy(self.order_by).glue()[0],
            'locking': ''  if not self.for_update else 'FOR UPDATE',
        }
        return sql.strip(), where_params


class Update(SqlNode):
    def __init__(self, table, updates, cond=None):
        super(Update, self).__init__()
        self.table = table
        self.updates = updates
        self.cond = cond

    def glue(self):
        update_columns, update_params = lists_from_dict(self.updates)
        where_str, where_params = Where(self.cond).glue()
        sql = 'UPDATE %(table)s SET %(updates)s %(where)s' % {
            'table': quote(self.table),
            'updates': ','.join('%s = %%s' % glue_col(c)[0] for c in update_columns),
            'where': where_str,
        }
        return sql.strip(), update_params + where_params


class Delete(SqlNode):
    def __init__(self, table, cond=None):
        super(Delete, self).__init__()
        self.table = table
        self.cond = cond

    def glue(self):
        where_str, where_params = Where(self.cond).glue()
        sql = 'DELETE FROM %(table)s %(where)s' % {
            'table': quote(self.table),
            'where': where_str,
        }
        return sql.strip(), where_params


class Insert(SqlNode):
    def __init__(self, table, inserts):
        super(Insert, self).__init__()
        self.table = table
        self.inserts = inserts

    def glue(self):
        raw_columns, insert_params = lists_from_dict(self.inserts)
        columns = []
        for o in raw_columns:
            columns.append(glue_col(o)[0])
        sql = 'INSERT INTO %(table)s (%(columns)s) VALUES (%(values)s) RETURNING id' % {
            'table': quote(self.table),
            'columns': ','.join(columns),
            'values': ','.join('%s' for _ in columns),
        }
        return sql.strip(), insert_params
