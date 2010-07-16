import datetime
import httplib
import logging

from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api.datastore_errors import BadKeyError
from google.appengine.ext import db
import yaml

from pushmaster.taglib import T, ScriptCData
from pushmaster import config
from pushmaster import logic
from pushmaster import model
from pushmaster import query
from pushmaster import urls
from pushmaster.view import common
from pushmaster.view import HTTPStatusCode
from pushmaster.view import RequestHandler

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Pushes', 'EditPush')

log = logging.getLogger('pushmaster.view.push')

def push_item(push):
    return T.li(class_='push')(
        T.a(href=push.uri)(
            common.display_datetime(push.ptime),
            T.span(' '),
            T.span(push.name or ''),
            ),
        common.user_home_link(push.owner),
        T.span(class_='state')(common.display_push_state(push)),
    )

class Pushes(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: pushes')
        
        pushes = query.open_pushes()

        push_list = T.ol(map(push_item, pushes))
        
        doc.body(T.h1('Recent Pushes'))
        doc.body(push_list)
        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)
        doc.serialize(self.response.out)

    def post(self):
        action = self.request.get('act')
        
        if action == 'new_push':
            name = self.request.get('name')
            push = logic.create_push(name=name)
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
                            common.hidden(push=str(push.key()), act='accept')),
                        ),
                    T.span('or', class_='sep'),
                    reject_request_link(request),
                    ),
               )
        return li
    ol = T.ol(class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def push_actions_form(push, requests):
    form = T.form(action=push.uri, method='post', class_='small')
    fields = T.div(class_='fields')
    form(fields)

    button_count = 0

    if push.state in ('accepting', 'onstage') and filter(lambda r: r.state == 'checkedin', requests):
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='act', value='sendtostage')('Mark Deployed to Stage'))
        button_count +=1

    if push.state == 'onstage' and requests and all(r.state == 'tested' for r in requests):
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='act', value='sendtolive')('Mark Live'))
        button_count +=1

    if push.state in ('accepting', 'onstage'):
        if button_count:
            fields(T.span(' or '))
        fields(T.button(type='submit', name='act', value='abandon')('Abandon'))
        button_count +=1
        
    return form

def mark_checked_in_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Mark Checked In'), 
            common.hidden(push='true', act='markcheckedin')))

def withdraw_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Withdraw'),
            common.hidden(push='true', act='withdraw')))

def mark_tested_form(request):
    return T.form(class_='small', method='post', action=request.uri)(
        T.div(class_='fields')(
            T.button(type='submit')('Mark Tested'), 
            common.hidden(push='true', act='marktested')))

def reject_request_link(request):
    return T.a('Reject', class_='reject-request', href=request.uri, title=request.subject)

class EditPush(RequestHandler):
    def get_request_header_list(self, header, default=''):
        hval = self.request.headers.get(header, default)
        return [part.strip() for part in hval.split(',')]

    def get(self, push_id):
        push = None

        if push_id == 'current':
            push = query.current_push()
            self.redirect(push.uri if push else '/pushes')
            return

        try:
            push = model.Push.get(push_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

        current_user = users.get_current_user()        
        pending_requests = query.pending_requests(not_after=datetime.date.today()) if current_user == push.owner else []

        if 'application/json' in self.get_request_header_list('Accept', default='*/*'):
            requests = query.push_requests(push)
            push_div = self.render_push_div(current_user, push, requests, pending_requests)
            response = {'push': dict(key=unicode(push.key()), state=push.state), 'html': unicode(push_div)}
            self.response.headers['Vary'] = 'Accept'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.headers['Cache-Control'] = 'no-store'
            self.response.out.write(json.dumps(response))

        else:
            doc = self.render_doc(current_user, push, pending_requests)
            self.response.out.write(unicode(doc))

    def render_doc(self, current_user, push, pending_requests):
        doc = common.Document(title='pushmaster: push: ' + logic.format_datetime(push.ptime))
        requests = query.push_requests(push)
        push_div = self.render_push_div(current_user, push, requests, pending_requests)
        doc.body(push_div)

        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js, common.script('/js/push.js'))
        push_json = ScriptCData('this.push = %s;' % json.dumps(dict(key=str(push.key()), state=push.state)))
        doc.head(T.script(type='text/javascript')(push_json))

        return doc

    def render_push_div(self, current_user, push, requests, pending_requests):
        push_div = T.div(class_='push')

        if current_user == push.owner:
            push_div(push_actions_form(push, requests)(class_='small push-action'))
        elif push.state != 'live':
            push_div(common.take_ownership_form(push)(class_='small push-action'))
            
        header = T.h1(common.display_datetime(push.ptime), T.span(class_='name')(push.name or ''), common.user_home_link(push.owner))

        if any(request.push_plans for request in requests):
            header(common.push_plans_badge())

        if any(request.js_serials for request in requests):
            header(common.js_serials_badge())

        if any(request.img_serials for request in requests):
            header(common.img_serials_badge())

        push_div(header)

        requests_div = T.div(class_='requests')
        push_div(requests_div)

        def requests_with_state(state):
            return filter(lambda r: r.state == state, requests)

        if push.state == 'live':
            requests_div(accepted_list(requests_with_state('live')))
        else:
            def onstage_request_item(request):
                li = common.request_item(request)
                if common.can_edit_request(request, push):
                    li(T.div(class_='actions')(mark_tested_form(request), T.span('or', class_='sep'), withdraw_form(request)))
                return li

            def withdrawable_request_item(request):
                li = common.request_item(request)
                if common.can_edit_request(request, push):
                    li(T.div(class_='actions')(withdraw_form(request)))
                return li

            def accepted_request_item(request):
                li = common.request_item(request)
                if common.can_edit_request(request, push):
                    li(T.div(class_='actions')(
                            mark_checked_in_form(request), 
                            T.span('or', class_='sep'),  
                            withdraw_form(request),
                            T.span('or', class_='sep'),
                            reject_request_link(request),
                            ))
                return li

            request_states = [
                ('Tested on Stage', requests_with_state('tested'), withdrawable_request_item),
                ('On Stage', requests_with_state('onstage'), onstage_request_item),
                ('Checked In', requests_with_state('checkedin'), withdrawable_request_item),
                ('Accepted', requests_with_state('accepted'), accepted_request_item),
                ]
            for label, subrequests, request_item in request_states:
                if subrequests:
                    requests_div(T.h3(label), accepted_list(subrequests, request_item=request_item))

        if current_user == push.owner:
            accepted_requests = requests_with_state('accepted')
            if accepted_requests:
                requests_div(T.pre('rebase-pull-branches %s' % (' '.join(['"%s"' % request.branch for request in accepted_requests if request.branch]),), class_='code'))
                    
        if push.state in ('accepting', 'onstage'):
            if pending_requests:
                push_div(T.h2(class_='pending')('Pending Requests'), push_pending_list(push, pending_requests))

        return push_div

    def post(self, push_id):
        try:
            push = model.Push.get(push_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

        action = self.request.get('act')

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
