from google.appengine.api import users

from pushmaster import config
from pushmaster import model
from pushmaster.taglib import T
from pushmaster.view import common
from pushmaster.view import page
from pushmaster.view import RequestHandler

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Home', 'Favicon')

class RedirectHandler(RequestHandler):
    def get(self):
        self.redirect(self.url)

def push_item(push):
    request_count = len(list(push.requests))
    return T.li(class_='push')(
        T.a(href=push.uri)(common.display_datetime(push.ctime)),
        T.span(common.display_push_state(push)),
        )

class Home(RequestHandler):
    def get(self):
        body = T.body(
            common.session(),
            common.navbar(),
            )

        current_user = users.get_current_user()
        requests = model.Request.for_user(current_user).fetch(25)
        if requests:
            body(
                T.h3('Requests'),
                T.ol(class_='requests')(map(common.request_item, requests)),
                )

        pushes = model.Push.for_user(current_user).fetch(25)
        if pushes:
            body(
                T.h3('Pushes'),
                T.ol(class_='pushes')(map(push_item, pushes)),
                )

        body(
            common.new_request_form(),
            T.div(common.bookmarklet()),
            page.script(config.jquery, external=True),
            page.script(config.jquery_ui, external=True),
            page.script('/js/pushmaster.js'),
            )

        page.write(self.response.out, page.head(title='pushmaster: home'), body)

class Favicon(RedirectHandler):
    url = config.favicon

