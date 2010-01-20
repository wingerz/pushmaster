import cgi
import re

from google.appengine.api import users

from pushmaster import config
from pushmaster import logic
from pushmaster import model
from pushmaster import timezone
from pushmaster.taglib import Literal, T

linkify_re = re.compile(r'\b(https?://[^\s]+)', re.MULTILINE | re.IGNORECASE)
http_re = re.compile(r'https?://', re.IGNORECASE)

def linkify_repl(m):
    return m.group(1) + link + m.group(3)

def linkify(text):
    parts = []
    for part in linkify_re.split(text):
        m = http_re.match(part)
        if m:
            parts.append('<a href="%s">%s</a>' % (cgi.escape(part, quote=True), cgi.escape(part)))
        else:
            parts.append(cgi.escape(part))
    return Literal(''.join(parts).replace('\n', '<br/>'))

def datetime(dt):
    return T.span(class_='datetime')(logic.format_datetime(dt))

def navbar(current=None):
    nav = T.div(class_='nav')(
        T.a(href='/requests')('Requests'),
        T.span(' | '),
        T.a(href='/pushes')('Pushes'),
        T.span(' | '),
    )

    current_push = model.Push.current()
    if current_push:
        nav(
            T.a(href=current_push.uri)(
                T.span('Current Push: '),
                datetime(current_push.ctime),
            ),
        )
    else:
        nav(new_push_form())
    
    return nav

def session():
    user = users.get_current_user()
    div = T.div(class_='session')(
        T.span(class_='email')(str(user)),
        ' ',
        T.a(href=users.create_logout_url('/'))('Logout')
    )
    return div

def user_email(user):
    return T.a(href='mailto:' + user.email())(user.nickname())

def request_item(request):
    li = T.li(
        datetime(request.ctime),
        ' ',
        T.a(href=request.uri)(request.subject),
        ' (',
        user_email(request.owner),
        ')',
        )
    if request.push_plans:
        li(T.a(class_='push-plans', href=config.push_plans_url)('P'))
    return li

def request_list(requests):
    ol = T.ol(class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol

def take_ownership_form(object):
    form = T.form(class_='take-ownership', action=object.uri, method='post')(
        T.button(type='submit', name='action', value='take_ownership')('Take Ownership'),
        )
    return form

def new_request_form(push=None):
    label = T.a(class_='toggle', href='#')('New Request') if push else 'New Request'
    class_ = 'push request' if push else 'request'
    form = T.form(action='/requests', method='post', class_=class_)(
        T.fieldset(
            T.legend(label),
            T.div(class_='content')(
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
                T.button(type='submit')('Create')
                ),
            ),
        )
    if push:
        form(T.input(type='hidden', name='push', value=str(push.key())))
    return form

def new_push_form():
    return T.form(action='/pushes', method='post', class_='new-push')(
        T.input(type='hidden', name='action', value='new_push'),
        T.button(type='submit')('Start New Push'),
    )
