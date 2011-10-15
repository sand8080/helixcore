from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Text, ArbitraryDict, NullableText, IsoDatetime)


REQUEST_PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

AUTHORIZED_REQUEST_AUTH_INFO = {
    'session_id': Text(),
    Optional('custom_actor_info'): NullableText(),
}

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'code': Text(),
    'message': Text(),
    Optional('fields'): [ArbitraryDict()],
}

ADDING_OBJECT_RESPONSE = AnyOf(
    dict({'id': int}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

ADDING_OBJECTS_RESPONSE = AnyOf(
    dict({'ids': [int]}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

AUTHORIZED_RESPONSE_STATUS_OK = dict(
    RESPONSE_STATUS_OK,
    **{'session_id': Text()}
)

AUTHORIZED_RESPONSE_STATUS_ERROR = dict(
    RESPONSE_STATUS_ERROR,
    **{'session_id': Text()}
)

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

PING_REQUEST = {}

PING_RESPONSE = RESPONSE_STATUS_ONLY

LOGIN_REQUEST = {
    'login': Text(),
    'password': Text(),
    'environment_name': Text(),
    Optional('custom_actor_info'): NullableText(),
}

LOGIN_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'session_id': Text(),
            'user_id': int,
            'environment_id': int,
        }
    ),
    RESPONSE_STATUS_ERROR
)

LOGOUT_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

LOGOUT_RESPONSE = RESPONSE_STATUS_ONLY

CHECK_ACCESS_REQUEST = dict(
    {
        'service_type': Text(),
        'property': Text(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CHECK_ACCESS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'user_id': int,
            'environment_id': int,
            'access': AnyOf('granted', 'denied'),
        }
    ),
    RESPONSE_STATUS_ERROR
)

ACTION_LOG_INFO = {
    'id': int,
    'session_id': NullableText(),
    'custom_actor_info': NullableText(),
    'actor_user_id': AnyOf(int, None),
    'subject_users_ids': [int],
    'action': Text(),
    'request_date': IsoDatetime(),
    'remote_addr': Text(),
    'request': Text(),
    'response': Text(),
}

GET_ACTION_LOGS_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
            Optional('user_id'): int,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'action_logs': [ACTION_LOG_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_ACTION_LOGS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_SELF_RESPONSE = GET_ACTION_LOGS_RESPONSE
