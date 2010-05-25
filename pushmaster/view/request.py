import datetime
import httplib
import logging

from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api.datastore_errors import BadKeyError

from pushmaster import config, logic, model
from pushmaster.taglib import T
from pushmaster.view import common, HTTPStatusCode, RequestHandler

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('Requests', 'EditRequest')

def edit_request_form(request):
    request_id = str(request.key())
    return T.form(action=request.uri, method='post', class_='edit request')(
        T.fieldset(
            T.legend(T.a(class_='toggle', href='#')('Edit Request')),
            T.div(class_='content')(
                T.div(
                    T.label(for_='edit-request-subject-'+request_id)('Subject'),
                    T.input(name='subject', id='edit-request-subject-'+request_id, value=request.subject),
                    ),
                T.div(
                    T.label(for_='edit-request-message-'+request_id)('Message'),
                    T.textarea(name='message', id='edit-request-message-'+request_id)(request.message or ''),
                    ),
                T.div(
                    T.label(for_='edit-request-target-date-'+request_id)('Push Date'),
                    T.input(name='target_date', id='edit-request-target-date-'+request_id, class_='date', value=request.target_date.strftime('%Y-%m-%d') if request.target_date else ''),
                    ),
                T.div(
                    T.input(id='edit-request-urgent-'+request_id, type='checkbox', name='urgent', class_='checkbox', checked=request.urgent),
                    T.label(for_='edit-request-urgent-'+request_id, class_='checkbox')('Urgent (e.g. P0)'),
                    ),
                T.div(
                    T.input(id='edit-request-no-testing-'+request_id, type='checkbox', name='no_testing', checked=request.no_testing, class_='checkbox'),
                    T.label(for_='edit-request-no-testing-'+request_id, class_='checkbox')('No Testing (batch-only)'),
                    ),
                T.div(
                    T.input(id='edit-request-push-plans-'+request_id, type='checkbox', name='push_plans', checked=request.push_plans, class_='checkbox'),
                    T.label(for_='edit-request-push-plans-'+request_id, class_='checkbox')('Push Plans'),
                    ),
                T.div(
                    T.button(type='submit', name='action', value='edit')('Save'),
                    ),
                ),
            ),
        )

def request_actions_form(request):
    form = T.form(action=request.uri, method='post', class_='request-actions')

    button_count = 0

    if request.state == 'requested':
        form(T.button(type='submit', name='action', value='abandon')('Abandon'))
        button_count += 1

    elif request.state == 'accepted':
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='markcheckedin')('Mark Checked In'))
        button_count += 1

    elif request.state == 'onstage':
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='marktested')('Mark Tested'))
        button_count += 1

    if request.state in ('accepted', 'checkedin', 'onstage', 'tested'):
        if button_count:
            form(T.span(' or '))
        form(T.button(type='submit', name='action', value='withdraw')('Withdraw'))
        button_count += 1
        
    return form

def request_display(request):
    div = T.div(class_='request')(
        T.h2(class_='subject')(
            request.subject, ' ', 
            common.user_home_link(request.owner), ' ',
            common.display_date(request.target_date)),
        T.div(class_='message')(common.linkify(request.message or '')),
        )

    if request.push_plans or request.no_testing or request.urgent:
        attrs = T.div(class_='attributes')

        if request.push_plans:
            attrs(T.div(class_='attribute')('This request has push plans.'))
        if request.no_testing:
            attrs(T.div(class_='attribute')('This request requires no stage testing.'))
        if request.urgent:
            attrs(T.div(class_='attribute')('This request is urgent.'))

        div(attrs)

    if common.can_edit_request(request):
        div(request_actions_form(request))

    return div

class Requests(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: requests')

        requests = model.Request.current()

        subject = self.request.get('subject')
        message = self.request.get('message')        

        if requests:
            doc.body(T.h2('Pending Requests'), common.request_list(requests))

        doc.body(T.div(common.bookmarklet(self.hostname)))
        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)

        doc.serialize(self.response.out)
        
    def post(self):
        subject = self.request.get('subject')
        message = self.request.get('message')
        push_plans = self.request.get('push_plans', 'off')
        no_testing = self.request.get('no_testing', 'off')
        urgent = self.request.get('urgent', 'off')
        target_date = self.request.get('target_date')
        target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None

        try:
            assert push_plans in ('on', 'off'), 'push_plans must be either on or off'
            assert no_testing in ('on', 'off'), 'no_testing must be either on or off'
            assert urgent in ('on', 'off'), 'urgent must be either on or off'
            assert len(subject) > 0, 'subject is required'
        except AssertionError, e:
            self.log.info('bad request: %s', e.message)
            raise HTTPStatusCode(httplib.BAD_REQUEST)

        request = logic.create_request(
            subject=subject, 
            message=message,
            push_plans=(push_plans == 'on'),
            no_testing=(no_testing == 'on'),
            urgent=(urgent == 'on'),
            target_date=target_date,
            )

        push = None
        push_key = self.request.get('push')
        if push_key:
            try:
                push = model.Push.get(push_key)
            except BadKeyError:
                pass
        self.redirect(push.uri if push else request.uri)

class EditRequest(RequestHandler):
    def get(self, request_id):
        try:
            request = model.Request.get(request_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

        if self.negotiate_content_type(provided=('text/html', 'application/json')) == 'application/json':
            self.get_json(request)
        else:
            self.get_html(request)

    def get_html(self, request):
        doc = common.Document(title='pushmaster: request: ' + request.subject)
        
        rdisplay = request_display(request)

        doc.body(rdisplay)
        
        if common.can_edit_request(request):
            if request.state == 'requested':
                doc.body(edit_request_form(request))
        else:
            rdisplay(common.take_ownership_form(request))

        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)
        doc.serialize(self.response.out)

    def get_json(self, request):
        req_json = {'key': str(req.key()), 'subject': req.subject, 'message': req.message, 'state': req.state}
        self.response.write(json.dumps(req_json))

    def post(self, request_id):
        try:
            request = model.Request.get(request_id)
        except BadKeyError:
            raise HTTPStatusCode(httplib.NOT_FOUND)

        action = self.request.get('action')
        redirect_to_push = self.request.get('push') == 'true'

        if action == 'edit':
            subject = self.request.get('subject')
            assert len(subject) > 0, 'subject must have a value'
            message = self.request.get('message')
            target_date = self.request.get('target_date')
            target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None
            push_plans = self.request.get('push_plans', 'off')
            assert push_plans in ('on', 'off'), 'push plans must be on or off'
            no_testing = self.request.get('no_testing', 'off')
            assert no_testing in ('on', 'off'), 'no testing must be on or off'
            urgent = self.request.get('urgent', 'off')
            assert urgent in ('on', 'off'), 'urgent must be on or off'
            logic.edit_request(request, subject=subject, message=message, push_plans=push_plans == 'on', no_testing=no_testing == 'on', urgent=urgent == 'on', target_date=target_date)
            self.redirect(request.uri)

        elif action == 'accept':
            push_id = self.request.get('push')
            push = model.Push.get(push_id)
            logic.accept_request(push, request)
            self.redirect(push.uri)

        elif action == 'abandon':
            logic.abandon_request(request)
            self.redirect('/requests')

        elif action == 'withdraw':
            push_uri = request.push.uri if request.push else None
            logic.withdraw_request(request)
            self.redirect(push_uri if (redirect_to_push and push_uri) else request.uri)

        elif action == 'markcheckedin':
            push_uri = request.push.uri if request.push else None
            logic.set_request_checkedin(request)
            self.redirect(push_uri if (redirect_to_push and push_uri) else request.uri)

        elif action == 'marktested':
            push_uri = request.push.uri if request.push else None
            logic.set_request_tested(request)
            self.redirect(push_uri if (redirect_to_push and push_uri) else request.uri)

        elif action == 'take_ownership':
            push_uri = request.push.uri if request.push else None
            logic.take_ownership(request)
            self.redirect(push_uri if (redirect_to_push and push_uri) else request.uri)
        
        else:
            raise HTTPStatusCode(httplib.BAD_REQUEST)
