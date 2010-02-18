__author__ = 'Jeremy Latt <jlatt@yelp.com>'

from pushmaster import config
from pushmaster.model import Push
from pushmaster.taglib import T
from pushmaster.view import page
from pushmaster.view import RequestHandler

class RedirectHandler(RequestHandler):
    def get(self):
        self.redirect(self.url)

class Home(RequestHandler):
    def get(self):
        current = Push.current()
        self.redirect(current.uri if current else '/requests')

class Favicon(RedirectHandler):
    url = config.favicon

__all__ = ['Home', 'Favicon']
