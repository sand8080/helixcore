import json


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
        h = self.to_dict(except_attrs)
        obj_info = ', '.join(['%s=%s' % (a, h[a]) for a in h])
        return '%s(%s)' % (self.__class__.__name__, obj_info)

    def to_dict(self, except_attrs=()):
        attrs = [(a, getattr(self, a, None)) for a in self.__slots__ if a not in except_attrs]
        return dict(attrs)

    def __getstate__(self):
        """
        used for storing in memcache
        """
        return self.to_dict()

    def __setstate__(self, d):
        """
        used for restoring from memcache
        """
        for k, v in d.items():
            self.__setattr__(k, v)


def serialize_field(d, f_src_name, f_dst_name):
    res = dict(d)
    if isinstance(res.get(f_src_name), (list, dict)):
        v = res.pop(f_src_name)
        res[f_dst_name] = json.dumps(v)
    return res


def deserialize_field(d, f_src_name, f_dst_name):
    res = dict(d)
    if isinstance(res.get(f_src_name), (str, unicode)):
        v = res.pop(f_src_name)
        res[f_dst_name] = json.loads(v)
    return res
