from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.ext.webapp import RequestHandler

from pushmaster.taglib import T
from pushmaster import config
from pushmaster import logic
from pushmaster.view import page
from pushmaster.model import *
from pushmaster.view import common

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Pushes', 'EditPush')

def new_push_form():
    return T('form', action='/pushes', method='post', class_='new-push')(
        T('fieldset')(
            T('input', type='hidden', name='action', value='new_push'),
            T('button', type='submit')('Start New Push'),
            )
        )

def push_item(push):
    return T('li', class_='push')(
        T('a', href=push.uri)(common.datetime(push.ctime)),
        ' (',
        common.user_email(push.owner),
        ') ',
        T('span', class_='state')(push.state),
        )

class Pushes(RequestHandler):
    def get(self):
        pushes = Push.open()

        push_list = T('ol')(
            map(push_item, pushes),
            )
        
        body = T('body')(
            common.session(),
            common.navbar(),
            new_push_form(),
            push_list, 
            )
        page.write(self.response.out, page.head(title='pushmaster: pushes'), body)

    def post(self):
        action = self.request.get('action')
        
        assert action == 'new_push'

        push = logic.create_push()

        self.redirect(push.uri)

def accepted_item(request):
    li = T('li', class_='accepted request')(
        common.datetime(request.ctime),
        ' ',
        T('a', href=request.uri)(request.subject),
        ' (',
        common.user_email(request.owner),
        ')',
        )
    if request.push_plans:
        li(T.a(class_='push-plans', href=config.push_plans_url)('P'))
    return li

def accepted_list(accepted):
    return T('ol', class_='accepted requests')(
        map(accepted_item, accepted),
        )

def push_pending_list(push, requests):
    def request_item(request):
        li = T('li')(
            T('form', action=request.uri, method='post', class_='accept-request')(
                T('input', type='hidden', name='push', value=str(push.key())),
                T('button', type='submit', name='action', value='accept')('Accept'),
                ),
            ' ',
            common.datetime(request.ctime),
            ' ',
            T('a', href=request.uri)(request.subject),
            ' (',
            common.user_email(request.owner),
            ')',
            )
        if request.push_plans:
            li(T.a(class_='push-plans', href=config.push_plans_url)('P'))
        return li
    ol = T('ol', class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def push_actions_form(push):
    form = T('form', action=push.uri, method='post')

    if push.state in ('accepting', 'onstage') and push.checkedin_requests.fetch(1):
        form(T('button', type='submit', name='action', value='sendtostage')('Mark Deployed to Stage'))

    if push.state == 'onstage' and push.tested:
        form(T('button', type='submit', name='action', value='sendtolive')('Mark Live'))

    if push.state in ('accepting', 'onstage'):
        form(T('button', type='submit', name='action', value='abandon')('Abandon'))
    return form


class EditPush(RequestHandler):
    def get(self, push_id):
        push = Push.get(push_id)
        requests = Request.current()

        header = T.h1(
            common.datetime(push.ctime),
            ' (',
            common.user_email(push.owner),
            ') ',
            T.span(push.state),
        )

        requests_div = T.div(class_='requests')(
            T.h2('Requests'),
            T.h3('Live'),
            accepted_list(push.live_requests),
            T.h3('Tested on Stage'),
            accepted_list(push.tested_requests),
            T.h3('On Stage'),
            accepted_list(push.onstage_requests),
            T.h3('Checked In'),
            accepted_list(push.checkedin_requests),
            T.h3('Accepted'),
            accepted_list(push.accepted_requests),
        )

        body = T.body(
            common.session(),
            common.navbar(),
            header,
            requests_div,
        )

        if users.get_current_user() == push.owner:
            requests_div(push_actions_form(push))
        else:
            requests_div(common.take_ownership_form(push))
            
        if push.state in ('accepting', 'onstage'):
            body(
                common.new_request_form(push),
                T.h2('Pending Requests'),
                push_pending_list(push, requests),
            )

        body(
            page.script(config.jquery, external=True),
            page.script('/js/pushmaster.js'),
            page.script('/js/push.js'),
        )

        head = page.head(title='pushmaster: push: ' + logic.format_datetime(push.ctime))(
            T.script(type='text/javascript')(
                'var push = ',
                json.dumps({
                        'key': str(push.key()),
                        'state': push.state,
                    }),
                ';',
            )
        )
        page.write(self.response.out, head, body)

    def post(self, push_id):
        push = Push.get(push_id)

        action = self.request.get('action')

        if action == 'sendtostage':
            logic.send_to_stage(push)
            self.redirect(push.uri)

        elif action == 'sendtolive':
            logic.send_to_live(push)
            self.redirect(push.uri)

        elif action == 'abandon':
            logic.abandon_push(push)
            self.redirect('/pushes')

        elif action == 'take_ownership':
            logic.take_ownership(push)
            self.redirect(push.uri)

        else:
            self.redirect(push.uri)
