import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from pushmaster import timezone
from pushmaster import urls

__author__ = 'Jeremy Latt <jlatt@yelp.com>'

class TrackedModel(db.Model):
    cuser = db.UserProperty(auto_current_user_add=True)
    ctime = db.DateTimeProperty(auto_now_add=True)
    muser = db.UserProperty(auto_current_user=True)
    mtime = db.DateTimeProperty(auto_now=True)

class Push(TrackedModel):
    owner = db.UserProperty(auto_current_user_add=True)
    state = db.StringProperty(choices=('accepting', 'onstage', 'live', 'abandoned'), default='accepting')
    ltime = db.DateTimeProperty()
    name = db.StringProperty()

    @property
    def ptime(self):
        return self.ltime or self.ctime

    @property
    def uri(self):
        return urls.push(self)

    @property
    def tested(self):
        has_requests = False
        for request in self.requests:
            has_requests = True
            if request.state in ('accepted', 'checkedin', 'onstage'):
                return False
        return has_requests

    @property
    def accepted_requests(self):
        return self.requests.filter('state =', 'accepted').order('subject')

    @property
    def checkedin_requests(self):
        return self.requests.filter('state =', 'checkedin').order('subject')

    @property
    def onstage_requests(self):
        return self.requests.filter('state =', 'onstage').order('subject')

    @property
    def tested_requests(self):
        return self.requests.filter('state =', 'tested').order('subject')
    
    @property
    def live_requests(self):
        return self.requests.filter('state =', 'live').order('subject')

    @classmethod
    def current(cls):
        current_push = memcache.get('push-current')
        if current_push is None:
            current_push = cls.all().filter('state in', ('accepting', 'onstage')).order('-ctime').get()
            memcache.add('push-current', current_push, 60 * 60)
        return current_push

    @classmethod
    def open(cls):
        open_pushes = memcache.get('push-open')
        if open_pushes is None:
            open_pushes = cls.all().filter('state in', ('accepting', 'onstage', 'live')).order('-ctime').fetch(20)
            open_pushes = sorted(open_pushes, key=lambda p: p.ptime, reverse=True)
            memcache.add('push-open', open_pushes, 60 * 60)
        return open_pushes

    @classmethod
    def for_user(cls, user):
        states = ('accepting', 'onstage', 'live')
        return cls.all().filter('owner =', user).filter('state in', states).order('-ctime')

    @classmethod
    def for_week_of(cls, from_date):
        from_date = from_date.astimezone(timezone.UTC())
        return cls.all().filter('state =', 'live').filter('ltime >=', from_date).filter('ltime <', from_date + datetime.timedelta(days=7)).order('ltime')

    @classmethod
    def bust_caches(cls):
        memcache.delete_multi(['push-current', 'push-open'])

class Request(TrackedModel):
    owner = db.UserProperty(auto_current_user_add=True)
    subject = db.StringProperty(required=True)
    branch = db.StringProperty()
    message = db.TextProperty()
    state = db.StringProperty(choices=('requested', 'accepted', 'checkedin', 'onstage', 'tested', 'live', 'abandoned'), default='requested')

    push_plans = db.BooleanProperty(default=False)
    no_testing = db.BooleanProperty(default=False)
    js_serials = db.BooleanProperty(default=False)
    img_serials = db.BooleanProperty(default=False)
    urgent = db.BooleanProperty(default=False)
    target_date = db.DateProperty(required=True)

    push = db.ReferenceProperty(Push, collection_name='requests')

    @property
    def uri(self):
        return urls.request(self)

    @classmethod
    def current(cls, not_after=None):
        current_requests = memcache.get('request-current')
        if current_requests is None:
            current_requests = list(cls.all().filter('state =', 'requested').order('target_date').order('ctime'))
            memcache.add('request-current', current_requests, 60 * 10)

        if not_after:
            return [request for request in current_requests if request.target_date <= not_after]
        else:
            return current_requests

    @classmethod
    def for_user(cls, user):
        states = ('requested', 'accepted', 'checkedin', 'onstage', 'tested', 'live')
        return cls.all().filter('owner =', user).filter('state in', states).order('-target_date').order('-ctime')

    @classmethod
    def bust_caches(cls):
        memcache.delete('request-current')
