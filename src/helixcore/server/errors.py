
class RequestProcessingError(Exception):
    class Categories(object):
        application = 'application'
        auth = 'auth'
        request_format = 'request_format'
        validation = 'validation'
        unknown_action = 'unknown_action'
        data_integrity = 'data_integrity'
        not_allowed = 'not_allowed'

    def __init__(self, category, message, details=None):
        Exception.__init__(self, message)
        self.category = category
        self.details = [] if details is None else details