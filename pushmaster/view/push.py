import datetime
import httplib

from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api.datastore_errors import BadKeyError
from google.appengine.ext import db

from pushmaster.taglib import T
from pushmaster import config
from pushmaster import logic
from pushmaster.model import *
from pushmaster.view import common
from pushmaster.view import HTTPStatusCode
from pushmaster.view import RequestHandler

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Pushes', 'EditPush')

def push_item(push):
    return T.li(class_='push')(
        T.a(href=push.uri)(common.display_datetime(push.ltime or push.ctime)),
        T.span('(', common.user_email(push.owner), ')', class_='email'),
        T.span(class_='state')(common.display_push_state(push)),
    )

class Pushes(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: pushes')
        
        pushes = Push.open()

        push_list = T.ol(map(push_item, pushes))
        
        doc.body(push_list)
        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)
        doc.serialize(self.response.out)

    def post(self):
        action = self.request.get('action')
        
        if action == 'new_push':
            push = logic.create_push()
            self.redirect(push.uri)
        else:
            raise HTTPStatusCode(httplib.BAD_REQUEST)

def accepted_list(accepted, request_item=common.request_item):
    return T.ol(class_='accepted requests')(map(request_item, accepted))

def push_pending_list(push, requests):
    is_push_owner = users.get_current_user() == push.owner
    def request_item(request):
        li = common.request_item(request)
        if is_push_owner:
            li(T.div(class_='actions')(
                    T.form(class_='small', action=request.uri, method='post')(
                        T.div(class_='fields')(
                            T.button(type='submit')('Accept'),
                            common.hidden(push=str(push.key()), action='accept')))))
        return li
    ol = T.ol(class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def push_actions_form(push):
    form = T.form(action=push.uri, method='post', class_='small')
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
        li(T.div(class_='actions')(mark_tested_form(request), T.span('or', class_='sep'), withdraw_form(request)))
    return li

def withdrawable_request_item(request):
    li = common.request_item(request)
    if common.can_edit_request(request):
        li(T.div(class_='actions')(withdraw_form(request)))
    return li

def accepted_request_item(request):
    li = common.request_item(request)
    if common.can_edit_request(request):
        li(T.div(class_='actions')(mark_checked_in_form(request), T.span('or', class_='sep'),  withdraw_form(request)))
    return li

class EditPush(RequestHandler):
    def get(self, push_id):
        push = None

        if push_id == 'current':
            push = Push.current()
            self.redirect(push.uri if push else '/pushes')
            return

        try:
            push = Push.get(push_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

        doc = common.Document(title='pushmaster: push: ' + logic.format_datetime(push.ltime or push.ctime))

        today = datetime.date.today()
        requests = filter(lambda request: request.target_date <= today, Request.current())

        header = T.h1(
            common.display_datetime(push.ltime or push.ctime),
            common.display_user_email(push.owner))

        requests_div = T.div(class_='requests')

        push_div = T.div(class_='push')
        
        if users.get_current_user() == push.owner:
            push_div(push_actions_form(push))
        elif push.state != 'live':
            push_div(common.take_ownership_form(push))
            
        push_div(header)

        doc.body(push_div, requests_div)

        if push.state == 'live':
            requests_div(accepted_list(push.live_requests))
        else:
            request_states = [
                ('Tested on Stage', push.tested_requests, withdrawable_request_item),
                ('On Stage', push.onstage_requests, onstage_request_item),
                ('Checked In', push.checkedin_requests, withdrawable_request_item),
                ('Accepted', push.accepted_requests, accepted_request_item),
                ]
            for label, query, request_item in request_states:
                subrequests = list(query)
                if subrequests:
                    requests_div(T.h3(label), accepted_list(subrequests, request_item=request_item))

        if push.state in ('accepting', 'onstage'):
            if requests:
                doc.body(T.h2(class_='pending')('Pending Requests'), push_pending_list(push, requests))

        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js, common.script('/js/push.js'))
        doc.head(T.script(type='text/javascript')('this.push = ', json.dumps(dict(key=str(push.key()), state=push.state)), ';'))
        doc.serialize(self.response.out)

    def post(self, push_id):
        try:
            push = Push.get(push_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

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
            raise HTTPStatusCode(httplib.BAD_REQUEST)
