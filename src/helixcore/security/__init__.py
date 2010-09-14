def sanitize_credentials(d):
    result = dict(d)
    for f in ('password', 'new_password', 'su_password'):
        if result.has_key(f):
            result[f] = '******'
    return result
