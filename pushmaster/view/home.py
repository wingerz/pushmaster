__author__ = 'Jeremy Latt jeremy@jeremylatt.com'

from pushmaster.handler import RequestHandler
from pushmaster.taglib import T
from pushmaster.view import page

class Home(RequestHandler):
    def get(self):
        self.redirect('/requests')

__all__ = ['Home']
