def lists_from_dict(d):
    """
    {'a': 1, 'b': 2} ==> (['a', 'b'], [1, 2])
    """
    return map(list, zip(*d.items()))


def dict_from_lists(names, values):
    return dict(zip(names, values))


def filter_dict(e, d):
    return dict(filter(lambda x: x[0] in e, d.items()))
