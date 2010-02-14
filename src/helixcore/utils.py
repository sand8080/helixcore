def lists_from_dict(d):
    """
    {'a': 1, 'b': 2} ==> (['a', 'b'], [1, 2])
    """
    return map(list, zip(*d.items()))


def dict_from_lists(names, values):
    return dict(zip(names, values))


def filter_dict(e, d):
    return dict(filter(lambda x: x[0] in e, d.items()))


def filter_all_field_values(f, d):
    def is_container(o):
        return isinstance(o, (dict, list, tuple))
    val = ()
    if not is_container(d):
        return val
    if isinstance(d, dict):
        if f in d:
            val = (d[f],)
        nested = filter(is_container, d.values())
    else:
        nested = filter(is_container, d)
    for n in nested:
        val = val + filter_all_field_values(f, n)
    return val
