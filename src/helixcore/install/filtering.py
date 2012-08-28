from functools import partial

def in_diapasone(begin, end, value):
    return (begin == None or value > begin) and (end == None or value <= end)

def version2int(v):
    if v is None:
        return None
    else:
        return map(int, v.split('-'))

def filter_patches(begin, end, patches, reverse=False):
    sorted_patches = sorted(patches, key=version2int, reverse=reverse)
    return [p for p in sorted_patches if in_diapasone(version2int(begin), version2int(end), version2int(p))]

filter_forward = filter_patches
filter_backward = partial(filter_patches, reverse=True)

