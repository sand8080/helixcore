def lists_from_dict(d):
    """
    {'a': 1, 'b': 2} ==> (['a', 'b'], [1, 2])
    """
    return map(list, zip(*d.items()))

def dict_from_lists(names, values):
    return dict(zip(names, values))
