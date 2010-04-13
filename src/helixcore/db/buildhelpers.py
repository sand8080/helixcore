class Unquoted(object):
    def __init__(self, column):
        self.column = column
    def __str__(self):
        return self.column


def quote(val, quotechar='"', splitter='.'):
    if isinstance(val, Unquoted):
        return val.column
    return  splitter.join(
        x.startswith(quotechar) and
        x.endswith(quotechar) and
        x or '%s%s%s' % (quotechar, x, quotechar)
        for x in val.split(splitter)
    )


def quote_list(lst, separator=','):
    return separator.join(map(quote, lst))


def is_empty_cond(cond):
    cond_str, _ = cond.glue()
    return cond_str == ''


def where(cond):
    if cond is None or is_empty_cond(cond):
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
