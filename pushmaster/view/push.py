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
        T.a(href=push.uri)(common.display_datetime(push.ctime)),
        T.span('(', common.user_email(push.owner), ')', class_='email'),
        T.span(class_='state')(common.display_push_state(push)),
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

def accepted_list(accepted, request_item=common.request_item):
    return T.ol(class_='accepted requests')(map(request_item, accepted))

def push_pending_list(push, requests):
    is_push_owner = users.get_current_user() == push.owner
    def request_item(request):
        li = common.request_item(request)
        if is_push_owner:
            li.children.insert(0, T.form(class_='small', action=request.uri, method='post')(
                    T.div(class_='fields')(
                        T.button(type='submit')('Accept'),
                        common.hidden(push=str(push.key()), action='accept'))))
        return li
    ol = T.ol(class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def push_actions_form(push):
    form = T.form(action=push.uri, method='post')
    fields = T.div(class_='fields')
    form(fields)

    button_count = 0

    if push.state in ('accepting', 'onstage') and push.checkedin_requests.fetch(1):
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='action', value='sendtostage')('Mark Deployed to Stage'))
        button_count +=1

    if push.state == 'onstage' and push.tested:
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='action', value='sendtolive')('Mark Live'))
        button_count +=1

    if push.state in ('accepting', 'onstage'):
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='action', value='abandon')('Abandon'))
        button_count +=1
        
    return form

def mark_checked_in_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Mark Checked In'), 
            common.hidden(push='true', action='markcheckedin')))

def withdraw_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Withdraw'),
            common.hidden(push='true', action='withdraw')))

def mark_tested_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Mark Tested'), 
            common.hidden(push='true', action='marktested')))

def onstage_request_item(request):
    li = common.request_item(request)
    if common.can_edit_request(request):
        li.children.insert(0, mark_tested_form(request))
    return li

def accepted_request_item(request):
    li = common.request_item(request)
    if common.can_edit_request(request):
        li.children.insert(0, mark_checked_in_form(request))
    return li

class EditPush(RequestHandler):
    def get(self, push_id):
        push = Push.get(push_id)
        requests = Request.current()

        estimated_push_count = push.requests.count(20)
        if estimated_push_count >= 20:
            header = T.h1(class_='gonzo')
        elif estimated_push_count >= 15:
            header = T.h1(class_='epic')
        else:
            header = T.h1()

        header(
            common.display_datetime(push.ctime),
            T.span('(', common.user_email(push.owner), ')', class_='email'),
            T.span(common.display_push_state(push)),
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
            request_states = [
                ('Tested on Stage', push.tested_requests, common.request_item),
                ('On Stage', push.onstage_requests, onstage_request_item),
                ('Checked In', push.checkedin_requests, common.request_item),
                ('Accepted', push.accepted_requests, accepted_request_item),
                ]
            for label, query, request_item in request_states:
                subrequests = list(query)
                if subrequests:
                    requests_div(T.h3(label), accepted_list(subrequests, request_item=request_item))

            if users.get_current_user() == push.owner:
                body(push_actions_form(push))
            else:
                body(common.take_ownership_form(push))

        if push.state in ('accepting', 'onstage'):
            if requests:
                body(T.h2(class_='pending')('Pending Requests'), push_pending_list(push, requests))
            body(common.new_request_form(push))

        body(
            page.script(config.jquery, external=True),
            page.script(config.jquery_ui, external=True),
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
