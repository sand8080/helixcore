def quote(val):
    q, s = '"', '.'
    return  s.join(x.startswith(q) and x.endswith(q) and x or '"%s"' % x for x in val.split(s))

def quote_list(lst, separator=','):
    return separator.join(map(quote, lst))

def where(cond):
    if cond is not None:
        cond_str, params = cond.glue()
        return ('WHERE %s' % cond_str, params)
    else:
        return ('', [])

def order(order_by):
    if order_by is not None:
        orders = []
        for o in order_by:
            if o.startswith('-'):
                orders.append('%s DESC' % quote(o[1:]))
            else:
                orders.append('%s ASC' % quote(o))
        return 'ORDER BY %s' % ','.join(orders)
    else:
        return ''


