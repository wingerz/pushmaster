__author__ = 'Jeremy Latt <jlatt@yelp.com>'

from pushmaster import config
from pushmaster.handler import RequestHandler
from pushmaster.taglib import T
from pushmaster.view import page

class RedirectHandler(RequestHandler):
    def get(self):
        self.redirect(self.url)

class Home(RedirectHandler):
    url = '/requests'

class Favicon(RedirectHandler):
    url = config.favicon

__all__ = ['Home', 'Favicon']
