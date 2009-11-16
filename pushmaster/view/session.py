from google.appengine.api import users
from google.appengine.ext.webapp import RequestHandler
from pushmaster.taglib import T
from pushmaster.view import page
from pushmaster.model import *
from pushamster import logic
from pushmaster.common import *

__author__ = 'Jeremy Latt jeremy@jeremylatt.com'
__all__ = ('Logout',)

class Logout(RequestHandler):
    def post(self):
        user = users.get_current_user()
        
        self.redirect('/')
