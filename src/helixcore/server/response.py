from helixcore.server.errors import RequestProcessingError


HELIX_APPLICATION_ERROR = 'HELIX_APPLICATION_ERROR'


def response_ok(**kwargs):
    '''
    @return: success response dict
    @param **kwargs: optional data to be appended to response
    '''
    return dict({'status': 'ok'}, **kwargs)


def response_error(e):
    '''
    @return: error response based on given RequestProcessingError
    @param request_processing_error: instance of RequestProcessingError (holds category, message)
    '''
    return {'status': 'error', 'code': e.code, 'category': e.category,
        'message': e.message, 'details': e.details,}


def response_app_error(message):
    '''
    @return: error response with application category
    @param message: error message
    '''
    return {
        'status': 'error',
        'code': HELIX_APPLICATION_ERROR,
        'category': RequestProcessingError.Category.application,
        'message': message,
        'details': [],
    }

