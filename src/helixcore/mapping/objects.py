class Mapped(object):
    __slots__ = []

    def __init__(self, **kwargs):
        for k in kwargs:
            if k in self.__slots__:
                setattr(self, k, kwargs[k])
            else:
                raise TypeError('Property "%s" undefinded' % k)

    def update(self, data):
        for (attr, v) in data.iteritems(): setattr(self, attr, v)

    def __repr__(self, except_attrs=()):
        attrs = [(a, getattr(self, a, None)) for a in self.__slots__]
        obj_info = ', '.join(['%s=%s' % (a, v) for (a, v) in attrs if a not in except_attrs])
        return '%s(%s)' % (self.__class__.__name__, obj_info)

