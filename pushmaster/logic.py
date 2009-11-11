from google.appengine.api import mail, users

from pushmaster import config
from pushmaster.model import *
from pushmaster import timezone

__author__ = 'Jeremy Latt <jeremy@jeremylatt.com>'

strftime_format = '%a, %d %b %Y %I:%M %p'

def format_datetime(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.UTC())
    return dt.astimezone(config.timezone).strftime(strftime_format)

def create_request(subject, message=None, push_plans=False):
    assert len(subject) > 0

    request = Request(subject=subject, push_plans=push_plans)
    if message:
        assert len(message) > 0
        request.message = message

    request.put()

    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] ' + request.subject,
        body=request.message or '')

    return request

def edit_request(request, subject, message=None, push_plans=False):
    assert request.state in ('requested', 'accepted')

    request.state = 'requested'
    request.subject = subject
    request.push_plans = push_plans
    if message:
        request.message = message

    request.put()

    email = mail.EmailMessage(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] ' + subject)
    if request.message:
        email.body = request.message

    return request

def abandon_request(request):
    assert request.state in ('requested', 'accepted')
    request.state = 'abandoned'
    request.push = None
    
    request.put()
    return request

def create_push(parent=None):
    push = Push()

    if parent:
        assert parent.state in ('accepting', 'onstage')
        for request in parent.requests:
            request.push = push
            request.put()
        parent.state = 'abandoned'

    push.put()
    return push

def abandon_push(push):
    assert push.state in ('accepting', 'onstage')

    push.state = 'abandoned'
    for request in push.requests:
        request.state = 'requested'
        request.push = None
        request.put()

    push.put()

    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] %s abandoned' % format_datetime(push.ctime),
        body='The push was abandoned.')

    return push

def accept_request(push, request):
    assert push.state in ('accepting', 'onstage')
    assert request.state == 'requested'
    assert not request.push

    request.push = push
    request.state = 'accepted'

    request.put()

    mail.send_mail(
        sender=users.get_current_user().email(),
        to=request.owner.email(),
        subject='[push] PCTI ' + request.subject,
        body='Please check this in.')

    return request

def withdraw_request(request):
    assert request.state in ('accepted', 'checkedin', 'onstage')
    assert request.push
    assert request.push.state in ('accepting', 'onstage')

    request.push = None
    request.state = 'requested'

    request.put()
    
    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] request withdrawn: ' + request.subject,
        body=request.message or '')

    return request

def send_to_stage(push):
    assert push.state in ('accepting', 'onstage')
    push.state = 'onstage'

    for request in push.requests:
        if request.state == 'checkedin':
            request.state = 'onstage'
            
            request.put()

            mail.send_mail(
                sender=users.get_current_user().email(),
                to=config.mail_to,
                subject='[push] PCYC: ' + request.subject,
                body='Please check your changes on stage.')

    push.put()
    return push

def set_request_tested(request):
    assert request.state == 'onstage'
    request.state = 'tested'
    request.put()
    
    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] LG2M: ' + request.subject,
        body='Looks good to me.')

    return request

def send_to_live(push):
    assert push.state == 'onstage'
    requests = list(push.requests)
    for request in requests:
        assert request.state == 'tested'

    for request in requests:
        request.state = 'live'
        request.put()
        
        mail.send_mail(
            sender=users.get_current_user().email(),
            to=request.owner.email(),
            subject='[push] live: ' + request.subject,
            body='Please monitor live to verify your changes.')

    push.state = 'live'
    push.put()
    return push

def set_request_checkedin(request):
    assert request.state == 'accepted'
    assert request.push

    request.state = 'checkedin'
    
    request.put()
        
    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject='[push] checked in: ' + request.subject,
        body='My changes are checked in.')

    return request
