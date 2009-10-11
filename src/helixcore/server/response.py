
from helixcore.server.errors import RequestProcessingError

def response_ok(**kwargs):
    '''
    @return: success response dict
    @param **kwargs: optional data to be appended to response
    '''
    return dict({'status': 'ok'}, **kwargs)

def response_error(request_processing_error):
    '''
    @return: error response based on given RequestProcessingError
    @param request_processing_error: instance of RequestProcessingError (holds category, message)
    '''
    return {
        'status': 'error',
        'category': request_processing_error.category,
        'message': request_processing_error.message,
    }

def response_app_error(message):
    '''
    @return: error response with application category
    @param message: error message
    '''
    return {
        'status': 'error',
        'category': RequestProcessingError.Categories.application,
        'message': message,
    }

