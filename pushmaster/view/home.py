__author__ = 'Jeremy Latt jeremy@jeremylatt.com'

from pushmaster.handler import RequestHandler
from pushmaster.taglib import Tag as T
from pushmaster.view import page

class Home(RequestHandler):
    def get(self):
        self.redirect('/requests')

__all__ = ['Home']
