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
    return T('span', class_='datetime')(logic.format_datetime(dt))

def navbar(current=None):
    nav = T('div', class_='nav')(
        T('a', href='/requests')('Requests'),
        ' | ',
        T('a', href='/pushes')('Pushes'),
        )

    current_push = model.Push.current()
    if current_push:
        nav(
            ' | ',
            T('a', href=current_push.uri)(
                'Current Push: ',
                datetime(current_push.ctime),
                ),
            )
    
    return nav

def session():
    user = users.get_current_user()
    div = T('div', class_='session')(
        T('span', class_='email')(str(user)),
        ' ',
        T('a', href=users.create_logout_url('/'))('Logout')
        )
    return div

def user_email(user):
    return T('a', href='mailto:' + user.email())(user.nickname())

def request_item(request):
    li = T('li')(
        datetime(request.ctime),
        ' ',
        T('a', href=request.uri)(request.subject),
        ' (',
        user_email(request.owner),
        ')',
        )
    if request.push_plans:
        li(T('span', class_='push-plans', title='This request has push plans.')('P'))
    return li

def request_list(requests):
    ol = T('ol', class_='requests')
    if requests:
        ol(map(request_item, requests))
    return ol
