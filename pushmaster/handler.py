from google.appengine.ext.webapp import RequestHandler as VanillaRequestHandler
from pushmaster.log import ClassLogger

class RequestHandler(VanillaRequestHandler):

    log = ClassLogger()
