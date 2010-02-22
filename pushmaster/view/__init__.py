import httplib

from google.appengine.ext import webapp

from pushmaster.log import ClassLogger

class HTTPStatusCode(Exception):
    def __init__(self, code, message=None):
        message = message or httplib.responses.get(code, 'Unknown Error')
        self.code = code
        super(HTTPStatusCode, self).__init__(message)

class RequestHandler(webapp.RequestHandler):
    log = ClassLogger()

    def set_error(self, code=httplib.INTERNAL_SERVER_ERROR, message=None):
        message = message or httplib.responses.get(code, 'Unknown Error')
        self.error(code)
        self.response.headers['Content-type'] = 'text/plain'
        self.response.out.write(message)

    def handle_exception(self, exception, debug_mode):
        if not debug_mode:
            if isinstance(exception, HTTPStatusCode):
                self.set_error(code=exception.code, message=exception.message)
            else:
                self.set_error()
        else:
            super(RequestHandler, self).handle_exception(exception, debug_mode)
