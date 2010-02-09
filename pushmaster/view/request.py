import datetime
import logging

from google.appengine.api import users

from pushmaster import config
from pushmaster.handler import RequestHandler

from pushmaster.taglib import T
from pushmaster import logic
from pushmaster.model import *
from pushmaster.view import page
from pushmaster.view import common

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
        T.h2(class_='subject')(request.subject, ' (', common.user_email(request.owner), ') ', common.display_date(request.target_date)),
        T.div(class_='message')(common.linkify(request.message or '')),
        T.h3(class_='push-plans')('This request has push plans.') if request.push_plans else '',
        T.h3(class_='push-plans')('This request requires no stage testing.') if request.no_testing else '',
        T.h3(class_='push-plans')('This request is urgent.') if request.urgent else '',
        )

    push = request.push
    if push:
        div(
            T.h3(class_='push')(
                'Push: ',
                T.a(href=push.uri)(
                    common.display_datetime(push.ctime),
                    ),
                ' (',
                common.user_email(push.owner),
                ')',
                ),
            )

    if common.can_edit_request(request):
        div(request_actions_form(request))

    return div

class Requests(RequestHandler):
    def get(self):
        requests = Request.current()

        subject = self.request.get('subject')
        message = self.request.get('message')

        body = T.body(
            common.session(),
            common.navbar(),
            T.h2('Pending Requests'),
            common.request_list(requests),
            common.new_request_form(subject=subject, message=message),
            T.div(common.bookmarklet()),
            page.script(config.jquery, external=True),
            page.script(config.jquery_ui, external=True),
            page.script('/js/pushmaster.js'),
            )
        
        page.write(self.response.out, page.head(title='pushmaster: requests'), body)
        
    def post(self):
        subject = self.request.get('subject')
        message = self.request.get('message')
        target_date = self.request.get('target_date')
        push_plans = self.request.get('push_plans', 'off')
        no_testing = self.request.get('no_testing', 'off')
        urgent = self.request.get('urgent', 'off')

        target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None
        assert push_plans in ('on', 'off'), 'push_plans must be either on or off'
        assert no_testing in ('on', 'off'), 'no_testing must be either on or off'
        assert urgent in ('on', 'off'), 'urgent must be either on or off'

        assert len(subject) > 0, 'subject is required'

        push_key = self.request.get('push')

        request = logic.create_request(
            subject=subject, 
            message=message,
            push_plans=(push_plans == 'on'),
            no_testing=(no_testing == 'on'),
            urgent=(urgent == 'on'),
            target_date=target_date,
            )

        push = Push.get(push_key) if push_key else None
        self.redirect(push.uri if push else '/requests')

class EditRequest(RequestHandler):
    def get(self, request_id):
        request = Request.get(request_id)
        
        rdisplay = request_display(request)

        body = T.body(
            common.session(),
            common.navbar(),
            rdisplay,
        )
        
        if common.can_edit_request(request):
            if request.state == 'requested':
                body(edit_request_form(request))
        else:
            rdisplay(common.take_ownership_form(request))

        body(
            page.script(config.jquery, external=True),
            page.script(config.jquery_ui, external=True),
            page.script('/js/pushmaster.js'),
        )

        page.write(self.response.out, page.head(title='pushmaster: request: ' + request.subject), body)

    def post(self, request_id):
        request = Request.get(request_id)

        action = self.request.get('action')
        redirect_to_push = self.request.get('push') == 'true'

        if action == 'edit':
            subject = self.request.get('subject')
            assert len(subject) > 0
            message = self.request.get('message')
            target_date = self.request.get('target_date')
            target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None
            push_plans = self.request.get('push_plans', 'off')
            assert push_plans in ('on', 'off')
            no_testing = self.request.get('no_testing', 'off')
            assert no_testing in ('on', 'off')
            urgent = self.request.get('urgent', 'off')
            assert urgent in ('on', 'off')
            logic.edit_request(request, subject=subject, message=message, push_plans=push_plans == 'on', no_testing=no_testing == 'on', urgent=urgent == 'on', target_date=target_date)
            self.redirect(request.uri)

        elif action == 'accept':
            push_id = self.request.get('push')
            push = Push.get(push_id)
            logic.accept_request(push, request)
            self.redirect(push.uri)

        elif action == 'abandon':
            logic.abandon_request(request)
            self.redirect('/requests')

        elif action == 'withdraw':
            logic.withdraw_request(request)
            self.redirect(request.push.uri if redirect_to_push else request.uri)

        elif action == 'markcheckedin':
            logic.set_request_checkedin(request)
            self.redirect(request.push.uri if redirect_to_push else request.uri)

        elif action == 'marktested':
            logic.set_request_tested(request)
            self.redirect(request.push.uri if redirect_to_push else request.uri)

        elif action == 'take_ownership':
            logic.take_ownership(request)
            self.redirect(request.push.uri if redirect_to_push else request.uri)
        
        else:
            self.redirect(request.uri)
