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
    return T.ol(class_='requests', id='pending-requests')

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
        if 'application/json' in self.request.headers.get('Accept', ''):
            return self.get_xhr(push, requests)
        else:
            return self.get_full(push, requests)

    def get_xhr(self, push, requests):
        self.response.headers['Content-type'] = 'application/json'
        return self.response.out.write(json.dumps({
            'push': self.push_json(push),
            'pending': map(self.request_json, requests),
        }))
        
    def get_full(self, push, requests):
        header = T.h1(
            common.datetime(push.ctime),
            ' (',
            common.user_email(push.owner),
            ') ',
            T.span(push.state),
        )

        requests_div = T.div(class_='requests', id='requests')(
            T.h2('Requests'),
        )

        if push.state == 'live':
            requests_div(accepted_list(push.live_requests))
        else:
            if users.get_current_user() == push.owner:
                requests_div(push_actions_form(push))
            else:
                requests_div(common.take_ownership_form(push))

        body = T.body(
            common.session(),
            common.navbar(),
            header,
            requests_div,
        )
            
        if push.state in ('accepting', 'onstage'):
            body(
                T.h2('Pending Requests'),
                push_pending_list(push, requests),
                common.new_request_form(push),
            )

        body(
            page.script(config.jquery, external=True),
            page.script('/js/pushmaster.js'),
            T.script(type='text/javascript')(
                'var push = ', json.dumps(self.push_json(push)), ';\n',
                'var pending = ', json.dumps(map(self.request_json, requests)), ';\n',
            ),
            page.script('/js/push.js'),
        )

        head = page.head(title='pushmaster: push: ' + logic.format_datetime(push.ctime))
        page.write(self.response.out, head, body)

    def push_json(self, push):
        return {
            'key': str(push.key()),
            'uri': push.uri,
            'state': push.state,
            'requests': map(self.request_json, push.requests),
            'owner': {
                'email': push.owner.email(),
                'nickname': push.owner.nickname(),
            },
        }

    def request_json(self, request):
        return {
            'key': str(request.key()),
            'uri': request.uri,
            'subject': request.subject,
            'state': request.state,
            'ctime': logic.format_datetime(request.ctime),
            'owner': {
                'email': request.owner.email(),
                'nickname': request.owner.nickname(),
            },
        }

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
