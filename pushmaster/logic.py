from cgi import escape as html_escape
import datetime
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import xmpp
from google.appengine.runtime.apiproxy_errors import OverQuotaError
from pushmaster import config
from pushmaster.model import *
from pushmaster import timezone

__author__ = 'Jeremy Latt <jlatt@yelp.com>'

def maybe_send_im(to, msg):
    if xmpp.get_presence(to):
        xmpp.send_message(to, '<html xmlns="http://jabber.org/protocol/xhtml-im"><body xmlns="http://www.w3.org/1999/xhtml">%s</body></html>' % msg, raw_xml=True)

def tznow(tz=config.timezone):
    return datetime.datetime.now(tz)

def choose_strftime_format(dt):
    now = tznow()
    
    strftime_format = '%e %b %Y' # 15 Sep 2009
    if dt.date().year == now.date().year:
        if dt.date().month == now.date().month:
            if dt.date().day == now.date().day:
                strftime_format = '%l:%M %p' # 3:07 PM
            elif (now.date() - dt.date()) < datetime.timedelta(days=7):
                strftime_format = '%a %l:%M %p' # Wed 3:07 PM
            else:
                strftime_format = '%a, %e %b' # Wed, 20 Jan
    return strftime_format

def format_datetime(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.UTC())
    dt = dt.astimezone(config.timezone) 
    return dt.strftime(choose_strftime_format(dt))

def choose_date_strftime_format(d):
    today = tznow().date()
    strftime_format = '%e %b %Y' # 15 Sep 2009
    if d.year == today.year:
        if d.month == today.month:
            if d.day == today.day:
                strftime_format = 'today'
            elif d.day == (today.day + 1):
                strftime_format = 'tomorrow'
            elif d.day == (today.day - 1):
                strftime_format = 'yesterday'
            else:
                strftime_format = '%a, %e %b' # Wed, 20 Jan
        else:
            strftime_format = '%e %b' # 15 Sep
    return strftime_format
            
def format_date(d):
    return d.strftime(choose_date_strftime_format(d))

def create_request(subject, **kw):
    return set_request_properties(Request(), subject, **kw)

def edit_request(request, subject, **kw):
    assert request.state in ('requested', 'rejected')
    return set_request_properties(request, subject, **kw)

def set_request_properties(request, subject, message=None, push_plans=False, no_testing=False, urgent=False, js_serials=False, target_date=None, branch=None, img_serials=False, tests_pass=False):
    assert len(subject) > 0
    target_date = target_date or datetime.date.today()

    request.state = 'requested'
    request.reject_reason = None
    request.push = None
    request.subject = subject
    request.branch = branch
    request.push_plans = push_plans
    request.no_testing = no_testing
    request.js_serials = js_serials
    request.img_serials = img_serials
    request.tests_pass = tests_pass
    request.urgent = urgent
    request.target_date = target_date
    if message:
        assert len(message) > 0
        request.message = message

    request.put()
    Request.bust_caches()
    send_request_mail(request)

    return request

def send_request_mail(request):
    body = [request.message or request.subject]
    if request.push_plans:
        body.append('This request has push plans.')
        body.append(config.push_plans_url)
    if request.no_testing:
        body.append('This request requires no stage testing.')
    body.append(config.url(request.uri))

    mail.send_mail(
        sender=users.get_current_user().email(),
        to=config.mail_to,
        subject=request.subject,
        body='\n'.join(body))

def abandon_request(request):
    assert request.state in ('requested', 'accepted', 'rejected')
    request.state = 'abandoned'
    request.push = None
    
    request.put()
    
    Request.bust_caches()

    return request

def create_push(name=None, parent=None):
    push = Push(name=name)

    if parent:
        assert parent.state in ('accepting', 'onstage')
        for request in parent.requests:
            request.push = push
            request.put()
        parent.state = 'abandoned'
        parent.put()

    push.put()

    Push.bust_caches()

    return push

def abandon_push(push):
    assert push.state in ('accepting', 'onstage')

    push.state = 'abandoned'
    for request in push.requests:
        request.state = 'requested'
        request.push = None
        request.put()

    push.put()

    Request.bust_caches()
    Push.bust_caches()

    return push

def accept_request(push, request):
    assert push.state in ('accepting', 'onstage')
    assert request.state == 'requested'
    assert not request.push

    request.push = push
    request.state = 'accepted'

    request.put()
    Request.bust_caches()

    return request

def withdraw_request(request):
    assert request.state in ('accepted', 'checkedin', 'onstage', 'tested')
    assert request.push
    assert request.push.state in ('accepting', 'onstage')

    push_owner_email = request.push.owner.email()
    request.push = None
    request.state = 'requested'

    mail.send_mail(
        sender=users.get_current_user().email(),
        to=push_owner_email,
        cc=config.mail_to,
        subject='Re: ' + request.subject,
        body='I withdrew my request.\n' + config.url(request.uri))

    request.put()
    
    Request.bust_caches()

    return request

def send_to_stage(push):
    assert push.state in ('accepting', 'onstage')

    push.state = 'onstage'
    push.put()
    
    Push.bust_caches()

    for request in push.requests:
        if request.state == 'checkedin':
            request.state = 'onstage'
            if request.no_testing:
                set_request_tested(request)
            else:
                owner_email = request.owner.email()

                mail.send_mail(
                    sender=users.get_current_user().email(),
                    to=owner_email,
                    cc=config.mail_to,
                    subject='Re: ' + request.subject,
                    body='Please check your changes on stage.\n' + config.url(push.uri))

                im_fields = dict(
                    pushmaster_email=html_escape(push.owner.email()),
                    pushmaster_name=html_escape(push.owner.nickname()),
                    request_subject=html_escape(request.subject),
                    uri=html_escape(config.url(push.uri)),
                    )
                maybe_send_im(owner_email, '<a href="mailto:%(pushmaster_email)s">%(pushmaster_name)s</a> requests that you check your changes on stage for <a href="%(uri)s">%(request_subject)s</a>.' % im_fields)
                request.put()

    return push

def set_request_tested(request):
    assert request.state == 'onstage'
    assert request.push

    push = request.push

    request.state = 'tested'
    request.put()
    
    push_owner_email = push.owner.email()
    
    mail.send_mail(
        sender=users.get_current_user().email(),
        to=push_owner_email,
        cc=config.mail_to,
        subject='Re: ' + request.subject,
        body='Looks good to me.\n' + config.url(push.uri))

    if all(request.state == 'tested' for request in push.requests):
        maybe_send_im(push_owner_email, 'All changes for <a href="%s">the push</a> are tested on stage.' % config.url(push.uri))

    return request

def send_to_live(push):
    assert push.state == 'onstage'
    requests = list(push.requests)
    for request in requests:
        assert request.state in ('tested', 'live')

    for request in requests:
        request.state = 'live'
        request.put()

    push.state = 'live'
    push.ltime = datetime.datetime.utcnow()
    push.put()
    
    Push.bust_caches()

    return push

def set_request_checkedin(request):
    assert request.state == 'accepted'
    assert request.push

    request.state = 'checkedin'
        
    mail.send_mail(
        sender=users.get_current_user().email(),
        to=request.push.owner.email(),
        cc=config.mail_to,
        subject='Re: ' + request.subject,
        body='My changes are checked in.\n' + config.url(request.push.uri))

    request.put()

    return request

def take_ownership(object):
    object.owner = users.get_current_user()
    object.put()

    if isinstance(object, Push):
        Push.bust_caches()
    elif isinstance(object, Request):
        Request.bust_caches()
    
    return object

def force_live(push):
    for request in push.requests:
        request.state = 'live'
        request.put()

    push.state = 'live'
    push.ltime = push.mtime
    push.put()

    Push.bust_caches()
    
    return push

def reject_request(request, rejector, reason=None):
    request.push = None
    request.state = 'rejected'
    if reason:
        request.reject_reason = reason

    request.put()
    Request.bust_caches()

    im_fields = dict(
        rejector_email=html_escape(rejector.email()),
        rejector_name=html_escape(rejector.nickname()),
        request_subject=html_escape(request.subject),
        uri=html_escape(config.url(request.uri)),
        reason=html_escape(reason),
        )
    maybe_send_im(request.owner.email(), '<a href="mailto:%(rejector_email)s">%(rejector_name)s</a> rejected your request <a href="%(uri)s">%(request_subject)s</a>: %(reason)s' % im_fields)

    mail.send_mail(
        sender=rejector,
        to=request.owner.email(),
        cc=config.mail_to,
        subject='Re: ' + request.subject,
        body="""This request was rejected.\n\n%s\n\n%s""" % (reason, config.url(request.uri)),
        )

    return request
