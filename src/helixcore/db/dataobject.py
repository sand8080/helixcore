from helixcore.mapping.objects import Mapped, serialize_field


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_info', 'actor_user_id',
        'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class ActionLogSubjectUserId(Mapped):
    __slots__ = ['id', 'action_log_id', 'subject_id']
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
