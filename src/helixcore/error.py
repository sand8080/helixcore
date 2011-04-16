from helixcore import error_code


class HelixcoreException(Exception):
    pass


class UnauthorizedActivity(HelixcoreException):
    pass


class RequestProcessingError(Exception):
    def __init__(self, message, code=None, fields=None):
        Exception.__init__(self, message)
        if code is None:
            self.code = error_code.HELIX_REQUEST_PROCESSING_ERROR
        else:
            self.code = code
        self.fields = [] if fields is None else fields


class UnknownActionError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_UNKNOWN_ACTION_ERROR)


class DataIntegrityError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_DATA_INTEGRITY_ERROR)


class ActionNotAllowedError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_ACTION_NOT_ALLOWED_ERROR)


class ApplicationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_APPLICATION_ERROR)


class ValidationError(RequestProcessingError):
    def __init__(self, msg, fields=None):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_VALIDATION_ERROR, fields=fields)


class FormatError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_FORMAT_ERROR)


class AuthError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self,
            msg, code=error_code.HELIX_AUTH_ERROR)
