import buildhelpers

class Leaf(object):
    """
    Leaf condition
    """
    def __init__(self, lh, oper, rh):
        self.lh = lh
        self.oper = oper
        self.rh = rh
    def glue(self):
        return (
            '%s %s %%s' % (buildhelpers.quote(self.lh), self.oper),
            [self.rh]
        )

class Eq(Leaf):
    """
    Alias for leaf equality condition
    """
    def __init__(self, lh, rh):
        super(Eq, self).__init__(lh, '=', rh)

class Scoped(object):
    def __init__(self, cond):
        self.cond = cond
    def glue(self):
        cond, params = self.cond.glue()
        return ('(%s)' % cond, params)

class Composite(object):
    def __init__(self, lh, oper, rh):
        self.lh = lh
        self.oper = oper
        self.rh = rh
    def glue(self):
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
