class RequestProcessingError(Exception):
    class Category(): #IGNORE:W0232
        auth = 'auth'
        validation = 'validation'
        request_format = 'request_format'
        unknown_action = 'unknown_action'
        data_integrity = 'data_integrity'
        data_invalid = 'data_invalid'
        not_allowed = 'not_allowed'
        application = 'application'

    def __init__(self, category, message, details=None):
        Exception.__init__(self, message)
        self.category = category
        self.details = [] if details is None else details

    def _get_message(self):
        return '; '.join(self.args)

    message = property(_get_message, None)


class UnknownActionError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.unknown_action, msg)


class DataIntegrityError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.data_integrity, msg)


class ActionNotAllowedError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.not_allowed, msg)


class ApplicationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.application, msg)


class ValidationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.validation, msg)


class FormatError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.request_format, msg)


class AuthError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Category.auth, msg)
