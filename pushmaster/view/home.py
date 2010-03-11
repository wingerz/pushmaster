from google.appengine.api import users

from pushmaster import config
from pushmaster import model
from pushmaster.taglib import T, XHTML
from pushmaster.view import common
from pushmaster.view import RequestHandler

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Home', 'Favicon', 'RedirectHandler')

class RedirectHandler(RequestHandler):
    def get(self):
        self.redirect(self.url)

def push_item(push):
    return T.li(class_='push')(
        T.a(href=push.uri)(common.display_datetime(push.ctime)),
        T.span(common.display_push_state(push)),
        )

def request_item(request):
    item = common.request_item(request)
    item(T.span(class_='state')(request.state))
    return item

class Home(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: home')

        current_user = users.get_current_user()
        requests = model.Request.for_user(current_user).fetch(25)
        if requests:
            doc.body(
                T.h3('Recent Requests'),
                T.ol(class_='my requests')(map(request_item, requests)),
                )

        pushes = model.Push.for_user(current_user).fetch(25)
        if pushes:
            doc.body(
                T.h3('Recent Pushes'),
                T.ol(class_='pushes')(map(push_item, pushes)),
                )

        doc.body(common.new_request_form(), T.div(common.bookmarklet()))
        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)
        doc.serialize(self.response.out)

class Favicon(RedirectHandler):
    url = config.favicon

