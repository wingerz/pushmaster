__author__ = 'Jeremy Latt <jlatt@yelp.com>'

# fix up the environment before anything else
from pushmaster import tweaks

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from pushmaster.view import *
from pushmaster.log import ClassLogger

class LoggingWSGIApplication(webapp.WSGIApplication):

    log = ClassLogger()

    def __call__(self, environ, start_response):
        request = self.REQUEST_CLASS(environ)
        self.log.debug('incoming %s for %s' % (environ['REQUEST_METHOD'], request.uri))
        return super(LoggingWSGIApplication, self).__call__(environ, start_response)

application = LoggingWSGIApplication(
    [('/', Home),
     ('/favicon.ico', Favicon),
     ('/requests', Requests),
     ('/pushes', Pushes),
     ('/request/([^/]+)', EditRequest),
     ('/push/([^/]+)/request/([^/]+)', EditPushRequest),
     ('/push/(.+)', EditPush)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
