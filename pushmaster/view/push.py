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

def push_item(push):
    return T.li(class_='push')(
        T.a(href=push.uri)(common.datetime(push.ctime)),
        ' (',
        common.user_email(push.owner),
        ') ',
        T.span(class_='state')(push.state),
    )

class Pushes(RequestHandler):
    def get(self):
        pushes = Push.open()

        push_list = T.ol(map(push_item, pushes))
        
        body = T.body(
            common.session(),
            common.navbar(),
            T.div(class_='new-push')(common.new_push_form()),
            push_list, 
        )
        page.write(self.response.out, page.head(title='pushmaster: pushes'), body)

    def post(self):
        action = self.request.get('action')
        
        assert action == 'new_push'

        push = logic.create_push()

        self.redirect(push.uri)

def accepted_item(request):
    li = T.li(class_='accepted request')(
        common.datetime(request.ctime),
        ' ',
        T.a(href=request.uri)(request.subject),
        ' (',
        common.user_email(request.owner),
        ')',
    )
    if request.push_plans:
        li(T.a(class_='push-plans', href=config.push_plans_url)('P'))
    return li

def accepted_list(accepted):
    return T.ol(class_='accepted requests')(
        map(accepted_item, accepted),
        )

def push_pending_list(push, requests):
    is_push_owner = users.get_current_user() == push.owner
    def request_item(request):
        li = T.li()
        if is_push_owner:
            li(
                T.form(action=request.uri, method='post', class_='accept-request')(
                    T.input(type='hidden', name='push', value=str(push.key())),
                    T.button(type='submit', name='action', value='accept')('Accept'),
                )
            )
        li(
            ' ',
            common.datetime(request.ctime),
            ' ',
            T.a(href=request.uri)(request.subject),
            ' (',
            common.user_email(request.owner),
            ')',
        )
        if request.push_plans:
            li(T.a(class_='push-plans', href=config.push_plans_url)('P'))
        return li
    ol = T.ol(class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def push_actions_form(push):
    form = T.form(action=push.uri, method='post')

    button_count = 0

    if push.state in ('accepting', 'onstage') and push.checkedin_requests.fetch(1):
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='sendtostage')('Mark Deployed to Stage'))
        button_count +=1

    if push.state == 'onstage' and push.tested:
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='sendtolive')('Mark Live'))
        button_count +=1

    if push.state in ('accepting', 'onstage'):
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='abandon')('Abandon'))
        button_count +=1
        
    return form


class EditPush(RequestHandler):
    def get(self, push_id):
        push = Push.get(push_id)
        requests = Request.current()

        header = T.h1(class_='epic', title='EPIC PUSH!!1') if len(push.requests.fetch(16)) == 15 else T.h1()
        header(
            common.datetime(push.ctime),
            ' (',
            common.user_email(push.owner),
            ') ',
            T.span(push.state),
        )

        requests_div = T.div(class_='requests')
        
        body = T.body(
            common.session(),
            common.navbar(),
            header,
            requests_div,
        )

        if push.state == 'live':
            requests_div(accepted_list(push.live_requests))
        else:
            requests_div(
                T.h3('Tested on Stage'),
                accepted_list(push.tested_requests),
                T.h3('On Stage'),
                accepted_list(push.onstage_requests),
                T.h3('Checked In'),
                accepted_list(push.checkedin_requests),
                T.h3('Accepted'),
                accepted_list(push.accepted_requests),
            )
            if users.get_current_user() == push.owner:
                body(push_actions_form(push))
            else:
                body(common.take_ownership_form(push))

        

        if push.state in ('accepting', 'onstage'):
            body(
                T.h2('Pending Requests', class_='pending'),
                push_pending_list(push, requests),
                common.new_request_form(push),
            )

        body(
            page.script(config.jquery, external=True),
            page.script('/js/jquery-ui-1.7.2.custom.min.js'),
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
