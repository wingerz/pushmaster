import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

import model
import timezone

CACHE_SECONDS = 60 * 60 * 24

def push_requests(push, state=None):
    requests = memcache.get(push.requests_cache_key)
    if requests is None:
        requests = list(model.Request.all().filter('push =', push))
        requests = sorted(requests, key=lambda r: (not r.urgent, r.mtime))
        memcache.add(push.requests_cache_key, requests, CACHE_SECONDS)

    if state is not None:
        requests = filter(lambda r: r.state == state, requests)

    return requests

CURRENT_PUSH_CACHE_KEY = 'push-current'
OPEN_PUSHES_CACHE_KEY = 'push-open'

def current_push():
    current_push = memcache.get(CURRENT_PUSH_CACHE_KEY)
    if current_push is None:
        states = ('accepting', 'onstage')
        current_push = model.Push.all().filter('state in', states).order('-ctime').get()
        memcache.add(CURRENT_PUSH_CACHE_KEY, current_push, CACHE_SECONDS)
    return current_push

def open_pushes():
    open_pushes = memcache.get(OPEN_PUSHES_CACHE_KEY)
    if open_pushes is None:
        states = ('accepting', 'onstage', 'live')
        open_pushes = model.Push.all().filter('state in', states).order('-ctime').fetch(25)
        open_pushes = sorted(open_pushes, key=lambda p: p.ptime, reverse=True)
        memcache.add(OPEN_PUSHES_CACHE_KEY, open_pushes, 60 * 60)
    return open_pushes

def pushes_for_user(user, limit=25):
    states = ('accepting', 'onstage', 'live')
    pushes = model.Push.all().filter('owner =', user).filter('state in', states).fetch(limit)
    pushes = sorted(pushes, key=lambda p: p.ptime, reverse=True)
    return pushes

def pushes_for_the_week_of(from_date):
        from_date = from_date.astimezone(timezone.UTC())
        pushes = list(model.Push.all().filter('state =', 'live').filter('ltime >=', from_date).filter('ltime <', from_date + datetime.timedelta(days=7)).order('ltime'))
        return pushes

def bust_push_caches():
    memcache.delete_multi([CURRENT_PUSH_CACHE_KEY, OPEN_PUSHES_CACHE_KEY])

CURRENT_REQUESTS_CACHE_KEY = 'request-current'

def current_requests():
    requests = memcache.get(CURRENT_REQUESTS_CACHE_KEY)
    if requests is None:
        states = ('requested', 'rejected')
        requests = list(model.Request.all().filter('state in', states))
        requests = sorted(requests, key=lambda r: (r.target_date, not r.urgent, r.mtime))
        memcache.add('request-current', requests, CACHE_SECONDS)

    return requests

def pending_requests(not_after=None):
    requests = current_requests()
    requests = filter(lambda r: r.state == model.Request.default_state, requests)
    if not_after is not None:
        requests = filter(lambda r: r.target_date <= not_after, requests)
    return requests

def requests_for_user(user, limit=25):
    states = ('requested', 'accepted', 'checkedin', 'onstage', 'tested', 'live', 'rejected')
    requests = model.Request.all().filter('state in', states).filter('owner =', user).fetch(limit)
    requests = sorted(requests, key=lambda r: (r.target_date, r.ctime), reverse=True)
    return requests

def bust_request_caches():
    memcache.delete(CURRENT_REQUESTS_CACHE_KEY)