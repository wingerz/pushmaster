__author__ = 'Jeremy Latt jeremy@jeremylatt.com'

from google.appengine.ext.webapp import RequestHandler
from taglib import Tag as T
import page

class Home(RequestHandler):
    def get(self):
        self.redirect('/requests')
