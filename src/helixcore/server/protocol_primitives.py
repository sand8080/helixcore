from helixcore.json_validator import (Optional, AnyOf,
    ARBITRARY_DICT, TEXT, ISO_DATETIME, NULLABLE_TEXT,
    DECIMAL_TEXT, POSITIVE_INT, ID, NON_NEGATIVE_INT)


REQUEST_PAGING_PARAMS = {
    Optional('limit'): NON_NEGATIVE_INT,
    Optional('offset'): NON_NEGATIVE_INT,
}

AUTHORIZED_REQUEST_AUTH_INFO = {
    'session_id': TEXT,
    Optional('custom_actor_info'): NULLABLE_TEXT,
}

RESPONSE_STATUS_OK = {
    'status': 'ok',
    Optional('execution_time'): DECIMAL_TEXT,
}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'code': TEXT,
    'message': TEXT,
    Optional('fields'): [TEXT],
    Optional('execution_time'): DECIMAL_TEXT,
#    Optional('environment_id'): ID,
}

def resp(d_resp):
    return AnyOf(
        dict(
            RESPONSE_STATUS_OK,
            **d_resp
        ),
        RESPONSE_STATUS_ERROR
    )

def authorized_req(d_req):
    return dict(
        d_req,
        **AUTHORIZED_REQUEST_AUTH_INFO
    )

ADDING_OBJECT_RESPONSE = resp({'id': ID})

ADDING_OBJECTS_RESPONSE = resp({'ids': [ID]})

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
        user_id=ID,
        environment_id=ID,
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
        user_id=ID,
        environment_id=ID,
        access=AnyOf('granted', 'denied'),
    ),
    RESPONSE_STATUS_ERROR
)

ACTION_LOG_INFO = {
    'id': ID,
    'session_id': NULLABLE_TEXT,
    'custom_actor_info': NULLABLE_TEXT,
    'actor_user_id': AnyOf(ID, None),
    'subject_users_ids': [ID],
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
            Optional('session_id'): NULLABLE_TEXT,
            Optional('user_id'): ID,
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
        total=NON_NEGATIVE_INT,
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

GET_CURRENCIES_REQUEST = dict(
    {
        'filter_params': {
            Optional('code'): TEXT,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('code', '-code')],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CURRENCY_INFO = {
    'id': ID,
    'code': TEXT,
    'cent_factor': POSITIVE_INT,
    'name': TEXT,
    'location': TEXT,
}

GET_CURRENCIES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'currencies': [CURRENCY_INFO]}
    ),
    RESPONSE_STATUS_ERROR
)
