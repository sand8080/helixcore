from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    ARBITRARY_DICT, TEXT, ISO_DATETIME, NULLABLE_TEXT)


REQUEST_PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

AUTHORIZED_REQUEST_AUTH_INFO = {
    'session_id': TEXT,
    Optional('custom_actor_info'): NULLABLE_TEXT,
}

RESPONSE_STATUS_OK = {
    'status': 'ok',
}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'code': TEXT,
    'message': TEXT,
    Optional('fields'): [ARBITRARY_DICT],
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
    **{'session_id': TEXT}
)

AUTHORIZED_RESPONSE_STATUS_ERROR = dict(
    RESPONSE_STATUS_ERROR,
    **{'session_id': TEXT}
)

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

PING_REQUEST = {}

PING_RESPONSE = RESPONSE_STATUS_ONLY

LOGIN_REQUEST = {
    'login': TEXT,
    'password': TEXT,
    'environment_name': TEXT,
    Optional('custom_actor_info'): NULLABLE_TEXT,
}

LOGIN_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        session_id=TEXT,
        user_id=int,
        environment_id=int,
    ),
    RESPONSE_STATUS_ERROR
)

LOGOUT_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

LOGOUT_RESPONSE = RESPONSE_STATUS_ONLY

CHECK_ACCESS_REQUEST = dict(
    AUTHORIZED_REQUEST_AUTH_INFO,
    service_type=TEXT,
    property=TEXT,
)

CHECK_ACCESS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        user_id=int,
        environment_id=int,
        access=AnyOf('granted', 'denied'),
    ),
    RESPONSE_STATUS_ERROR
)

ACTION_LOG_INFO = {
    'id': int,
    'session_id': NULLABLE_TEXT,
    'custom_actor_info': NULLABLE_TEXT,
    'actor_user_id': AnyOf(int, None),
    'subject_users_ids': [int],
    'action': TEXT,
    'request_date': ISO_DATETIME,
    'remote_addr': TEXT,
    'request': TEXT,
    'response': TEXT,
}

GET_ACTION_LOGS_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): ISO_DATETIME,
            Optional('to_request_date'): ISO_DATETIME,
            Optional('action'): TEXT,
            Optional('session_id'): TEXT,
            Optional('user_id'): int,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf(
            'request_date',
            '-request_date',
            'id',
            '-id',
        )]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        action_logs=[ACTION_LOG_INFO],
        total=NonNegative(int),
    ),
    RESPONSE_STATUS_ERROR
)

GET_ACTION_LOGS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): ISO_DATETIME,
            Optional('to_request_date'): ISO_DATETIME,
            Optional('action'): TEXT,
            Optional('session_id'): TEXT,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf(
            'request_date',
            '-request_date',
            'id',
            '-id',
        )]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_SELF_RESPONSE = GET_ACTION_LOGS_RESPONSE
