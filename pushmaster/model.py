import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from pushmaster import timezone

__author__ = 'Jeremy Latt <jlatt@yelp.com>'

class Push(db.Model):
    ctime = db.DateTimeProperty(auto_now_add=True)
    mtime = db.DateTimeProperty(auto_now=True)
    owner = db.UserProperty(auto_current_user_add=True)
    state = db.StringProperty(choices=('accepting', 'onstage', 'live', 'abandoned'), default='accepting')

    @property
    def uri(self):
        return '/push/' + str(self.key())

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
        return self.requests.filter('state =', 'accepted')

    @property
    def checkedin_requests(self):
        return self.requests.filter('state =', 'checkedin')

    @property
    def onstage_requests(self):
        return self.requests.filter('state =', 'onstage')

    @property
    def tested_requests(self):
        return self.requests.filter('state =', 'tested')
    
    @property
    def live_requests(self):
        return self.requests.filter('state =', 'live')

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
            memcache.add('push-open', open_pushes, 60 * 60)
        return open_pushes

    @classmethod
    def for_user(cls, user):
        states = ('accepting', 'onstage', 'live')
        return cls.all().filter('owner =', user).filter('state in', states).order('-ctime')

    @classmethod
    def for_week_of(cls, from_date):
        from_date = from_date.astimezone(timezone.UTC())
        return cls.all().filter('state =', 'live').filter('ctime >=', from_date).filter('ctime <', from_date + datetime.timedelta(days=7)).order('ctime')

class Request(db.Model):
    ctime = db.DateTimeProperty(auto_now_add=True)
    mtime = db.DateTimeProperty(auto_now=True)
    owner = db.UserProperty(auto_current_user_add=True)
    subject = db.StringProperty(required=True)
    message = db.TextProperty()
    push = db.ReferenceProperty(Push, collection_name='requests')
    state = db.StringProperty(choices=('requested', 
                                       'accepted',
                                       'checkedin', 
                                       'onstage', 
                                       'tested', 
                                       'live', 
                                       'abandoned'),
                              default='requested')
    push_plans = db.BooleanProperty(default=False)
    no_testing = db.BooleanProperty(default=False)
    urgent = db.BooleanProperty(default=False)
    target_date = db.DateProperty(required=True)

    @property
    def uri(self):
        return '/request/' + str(self.key())

    @classmethod
    def current(cls):
        current_requests = memcache.get('request-current')
        if current_requests is None:
            current_requests = cls.all().filter('state =', 'requested').order('target_date').fetch(100)
            memcache.add('request-current', current_requests, 60 * 10)
        return current_requests

    @classmethod
    def for_user(cls, user):
        states = ('requested', 'accepted', 'checkedin', 'onstage', 'tested', 'live')
        return cls.all().filter('owner =', user).filter('state in', states).order('-target_date')
