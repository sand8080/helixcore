from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Text, ArbitraryDict, NullableText)


REQUEST_PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

AUTHORIZED_REQUEST_AUTH_INFO = {
    Optional('session_id'): Text(),
    Optional('custom_actor_info'): NullableText(),
}

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'code': Text(),
    'category': Text(),
    'message': Text(),
    'details': [ArbitraryDict()],
}

ADDING_OBJECT_RESPONSE = AnyOf(
    dict({'id': int}, **RESPONSE_STATUS_OK),
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

AUTHORIZED_RESPONSE_STATUS_ONLY = AnyOf(
    AUTHORIZED_RESPONSE_STATUS_OK,
    AUTHORIZED_RESPONSE_STATUS_ERROR
)

PING_REQUEST = {}

PING_RESPONSE = RESPONSE_STATUS_ONLY

LOGIN_REQUEST = {
    'login': Text(),
    'password': Text(),
    'environment_name': Text(),
    Optional('custom_actor_info'): NullableText(),
}

LOGIN_RESPONSE = AUTHORIZED_RESPONSE_STATUS_ONLY

LOGOUT_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

LOGOUT_RESPONSE = RESPONSE_STATUS_ONLY
