
class RequestProcessingError(Exception):
    class Categories(object):
        application = 'application'
        request_format = 'request_format'
        validation = 'validation'
        unknown_action = 'unknown_action'
        data_integrity = 'data_integrity'
        not_allowed = 'not_allowed'


    def __init__(self, category, message):
        Exception.__init__(self, message)
        self._category = category

    @property
    def category(self):
        return self._category
