FIELDS_FOR_ENCRYPTION = ('password', 'new_password', 'su_password')
FIELDS_FOR_SANITATION = FIELDS_FOR_ENCRYPTION + ('session_id',)

def _data_transfromer(d, fields, func):
    result = dict(d)
    for f in fields:
        if result.has_key(f):
            result[f] = func(result[f])
    return result


def sanitize_credentials(d):
    return _data_transfromer(d, FIELDS_FOR_SANITATION, lambda x: '******')


def encrypt_passwords(d, encryptor):
    return _data_transfromer(d, FIELDS_FOR_ENCRYPTION, encryptor)
