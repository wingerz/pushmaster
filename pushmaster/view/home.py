__author__ = 'Jeremy Latt jeremy@jeremylatt.com'

from pushmaster.handler import RequestHandler
from pushmaster.taglib import Tag as T
from pushmaster.view import page

class Home(RequestHandler):
    def get(self):
        self.debug('saw a hit for the home page')
        self.redirect('/requests')

__all__ = ['Home']
