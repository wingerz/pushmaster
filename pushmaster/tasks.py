from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from pushmaster import config
from pushmaster.view import RequestHandler

mail_task_url = '/tasks/mail'
xmpp_task_url = '/tasks/xmpp'

class AsyncMailHandler(RequestHandler):
    def post(self):
        to = self.request.get_all('to')
        subject = self.request.get('subject')
        body = self.request.get('body')
        html = self.request.get('html')
        reply_to = self.request.get('reply_to')

        assert to
        assert subject
        assert body

        kw = dict(sender=config.mail_sender, to=to, subject=subject, body=body)
        if reply_to:
            kw['reply_to'] = reply_to
        if html:
            kw['html'] = html
        mail.send_mail(**kw)

def maybe_send_im(to, msg):
    if xmpp.get_presence(to):
        xmpp.send_message(to, '<html xmlns="http://jabber.org/protocol/xhtml-im"><body xmlns="http://www.w3.org/1999/xhtml">%s</body></html>' % msg, raw_xml=True)

class AsyncXMPPHandler(RequestHandler):
    def post(self):
        to = self.request.get('to')
        message = self.request.get('message')

        assert to
        assert message

        maybe_send_im(to, message)

#
# the app
#

wsgi_app = [
    (mail_task_url, AsyncMailHandler),
    (xmpp_task_url, AsyncXMPPHandler),
    ]

def main():
    run_wsgi_app(webapp.WSGIApplication(wsgi_app))

if __name__ == '__main__':
    main()
