__author__ = 'Jeremy Latt <jeremy@jeremylatt.com>'

# fix up the environment before anything else
from pushmaster import tweaks

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from pushmaster.view import *

application = webapp.WSGIApplication(
    [('/', Home),
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
