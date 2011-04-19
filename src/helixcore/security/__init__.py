FIELDS_FOR_ENCRYPTION = ('password', 'new_password', 'su_password')
#FIELDS_FOR_SANITATION = FIELDS_FOR_ENCRYPTION + ('session_id',)
FIELDS_FOR_SANITATION = FIELDS_FOR_ENCRYPTION


def _data_transfromer(d, fields, func):
    result = dict(d)
    for f in fields:
        if result.has_key(f):
            result[f] = func(result[f])
    return result


def sanitize_credentials(d):
    return _data_transfromer(d, FIELDS_FOR_SANITATION, lambda x: '******')

class Session(object):
    def __init__(self, session_id, environment_id, user_id):
        self.session_id = session_id
        self.environment_id = environment_id
        self.user_id = user_id

    def as_dict(self):
        return {'session_id': self.session_id, 'user_id': self.user_id,
            'environment_id': self.environment_id}

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__dict__)