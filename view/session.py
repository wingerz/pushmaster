from google.appengine.api import users
from google.appengine.ext.webapp import RequestHandler
from taglib import Tag as T
import page
from model import *
import logic
from common import *

__author__ = 'Jeremy Latt jeremy@jeremylatt.com'
__all__ = ('Logout',)

class Logout(RequestHandler):
    def post(self):
        user = users.get_current_user()
        
        self.redirect('/')
