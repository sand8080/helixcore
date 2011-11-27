from helixcore.mapping.objects import Mapped


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_info', 'actor_user_id',
        'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class Currency(Mapped):
    __slots__ = ['id', 'code', 'cent_factor', 'name', 'location']
    table = 'currency'
