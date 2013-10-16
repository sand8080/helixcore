from helixcore.mapping.objects import Mapped, serialize_field

# No boolean in Oracle. So using integer constants instead.
INTEGER_TRUE = 1
INTEGER_FALSE = 0


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_info', 'actor_user_id',
        'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class ActionLogSubjectUser(Mapped):
    __slots__ = ['id', 'environment_id', 'action_log_id', 'subject_id']
    table = 'al_subjs_ids'


class Currency(Mapped):
    __slots__ = ['id', 'code', 'cent_factor', 'name', 'location']
    table = 'currency'


class Notification(Mapped):
    TYPE_EMAIL = 'email'
    __slots__ = ['id', 'environment_id', 'event', 'is_active',
        'type', 'serialized_messages']
    table = 'notification'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'messages', 'serialized_messages')
        super(Notification, self).__init__(**d)


def bool_to_int(b):
    return INTEGER_TRUE if b else INTEGER_FALSE
