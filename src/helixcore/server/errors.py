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