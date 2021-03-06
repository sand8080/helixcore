from helixcore import error_code


def response_ok(**kwargs):
    '''
    @return: success response dict
    @param **kwargs: optional data to be appended to response
    '''
    return dict({'status': 'ok'}, **kwargs)


def response_error(e):
    '''
    @return: error response based on given RequestProcessingError
    @param request_processing_error: instance of RequestProcessingError
    '''
    resp = {'status': 'error', 'code': e.code, 'message': ';'.join(e.args),
        'fields': e.fields}
    if e.execution_time is not None:
        resp['execution_time'] = e.execution_time
    return resp


def response_app_error(message):
    '''
    @return: error response with application category
    @param message: error message
    '''
    return {'status': 'error', 'code': error_code.HELIX_APPLICATION_ERROR,
        'message': message, 'fields': []}

