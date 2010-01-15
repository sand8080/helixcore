class Unquoted(object):
    def __init__(self, column):
        self.column = column
    def __str__(self):
        return self.column

def quote(val):
    if isinstance(val, Unquoted):
        return val.column
    q, s = '"', '.'
    return  s.join(x.startswith(q) and x.endswith(q) and x or '"%s"' % x for x in val.split(s))

def quote_list(lst, separator=','):
    return separator.join(map(quote, lst))

def where(cond):
    if cond is None:
        return ('', [])
    else:
        cond_str, params = cond.glue()
        return ('WHERE %s' % cond_str, params)

def order(order_by):
    if order_by is None:
        return ''
    if isinstance(order_by, str):
        order_by = [order_by]
    orders = []
    for o in order_by:
        if o.startswith('-'):
            orders.append('%s DESC' % quote(o[1:]))
        else:
            orders.append('%s ASC' % quote(o))
    return 'ORDER BY %s' % ','.join(orders)

def columns(c):
    if c is None:
        return '*'
    if isinstance(c, str):
        c = [c]
    return quote_list(c)
