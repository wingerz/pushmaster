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

def new_request_form():
    return T.form(action='/requests', method='post', class_='request')(
        T.fieldset(
            T.legend('New Request'),
            T.div(
                T.label(for_='new-request-subject')('Subject'),
                T.input(name='subject', id='new-request-subject'),
                ),
            T.div(
                T.label(for_='new-request-message')('Message'),
                T.textarea(name='message', id='new-request-message'),
                ),
            T.div(
                T.input(id='new-request-push-plans', type='checkbox', name='push_plans', class_='checkbox'),
                T.label(class_='checkbox', for_='new-request-push-plans')('Push Plans'),
                ),
            ),
        T.div(
            T.button(type='submit')('Create')
            ),
        )

def edit_request_form(request):
    request_id = str(request.key())
    return T.form(action=request.uri, method='post', class_='request')(
        T.fieldset(
            T.legend(T.a(class_='edit-request-toggle')('Edit Request')),
            T.div(class_='edit-request-content')(
                T.div(
                    T.label(for_='edit-request-subject-'+request_id)('Subject'),
                    T.input(name='subject', id='edit-request-subject-'+request_id, value=request.subject),
                    ),
                T.div(
                    T.label(for_='edit-request-message-'+request_id)('Message'),
                    T.textarea(name='message', id='edit-request-message-'+request_id)(request.message or ''),
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

    if request.state == 'requested':
        form(T.button(type='submit', name='action', value='abandon')('Abandon'))

    elif request.state == 'accepted':
        form(T.button(type='submit', name='action', value='markcheckedin')('Mark Checked In'))

    elif request.state == 'onstage':
        form(T.button(type='submit', name='action', value='marktested')('Mark Tested'))

    if request.state in ('accepted', 'checkedin', 'onstage', 'tested'):
        form(T.button(type='submit', name='action', value='withdraw')('Withdraw'))
        
    return form

def request_display(request):
    div = T.div(class_='request')(
        T.h2(class_='subject')(
            request.subject,
            ' (',
            common.user_email(request.owner),
            ')'
            ),
        T.div(class_='message')(common.linkify(request.message or '')),
        T.h3(class_='push-plans')('This request has push plans.') if request.push_plans else '',
        )

    push = request.push
    if push:
        div(
            T.h3(class_='push')(
                'Push: ',
                T.a(href=push.uri)(
                    common.datetime(push.ctime),
                    ),
                ' (',
                common.user_email(push.owner),
                ')',
                ),
            )

    if users.get_current_user() == request.owner:
        div(request_actions_form(request))

    return div

class Requests(RequestHandler):
    def get(self):
        requests = Request.current()

        body = T('body')(
            common.session(),
            common.navbar(),
            new_request_form(),
            T('h2')('Pending Requests'),
            common.request_list(requests),
            )

        page.write(self.response.out, page.head(title='pushmaster: requests'), body)
        
    def post(self):
        subject = self.request.get('subject')
        message = self.request.get('message')
        push_plans = self.request.get('push_plans', 'off')

        assert push_plans in ('on', 'off')

        assert len(subject) > 0

        request = logic.create_request(
            subject=subject, 
            message=message,
            push_plans=(push_plans == 'on'))
        self.redirect('/requests')

class EditRequest(RequestHandler):
    def get(self, request_id):
        request = Request.get(request_id)
        
        rdisplay = request_display(request)

        body = T('body')(
            common.session(),
            common.navbar(),
            rdisplay,
            )
        
        if users.get_current_user() == request.owner:
            if request.state == 'requested':
                body(edit_request_form(request))
        else:
            rdisplay(common.take_ownership_form(request))

        body(
            page.script(config.jquery, external=True),
            page.script('/js/request.js'),
            )

        page.write(self.response.out, page.head(title='pushmaster: request: ' + request.subject), body)

    def post(self, request_id):
        request = Request.get(request_id)

        action = self.request.get('action')

        if action == 'edit':
            subject = self.request.get('subject')
            assert len(subject) > 0
            message = self.request.get('message')
            push_plans = self.request.get('push_plans', 'off')
            assert push_plans in ('on', 'off')
            logic.edit_request(request, subject=subject, message=message, push_plans=push_plans == 'on')
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
            self.redirect(request.uri)

        elif action == 'markcheckedin':
            logic.set_request_checkedin(request)
            self.redirect(request.uri)

        elif action == 'marktested':
            logic.set_request_tested(request)
            self.redirect(request.uri)

        elif action == 'take_ownership':
            logic.take_ownership(request)
            self.redirect(request.uri)
        
        else:
            self.redirect(request.uri)
