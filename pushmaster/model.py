import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from pushmaster import query
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
    def requests_cache_key(self):
        return 'push-requests-%s' % self.key()

    def bust_requests_cache(self):
        memcache.delete(self.requests_cache_key)

    @property
    def ptime(self):
        return self.ltime or self.ctime

    @property
    def uri(self):
        return urls.push(self)

    @property
    def api_uri(self):
        return urls.api_push(self)

    def put(self):
        try:
            return super(Push, self).put()
        finally:
            query.bust_push_caches()

    @property
    def json(self):
        return {'key': unicode(self.key()),
                'state': self.state,
                'owner': self.owner.email()}

class Request(TrackedModel):
    all_states = ('requested', 'accepted', 'checkedin', 'onstage', 'tested', 'live', 'abandoned', 'rejected')
    default_state = 'requested'

    owner = db.UserProperty(auto_current_user_add=True)
    subject = db.StringProperty()
    branch = db.StringProperty()
    message = db.TextProperty()
    state = db.StringProperty(choices=all_states, default=default_state)
    reject_reason = db.TextProperty()
    target_date = db.DateProperty()

    push_plans = db.BooleanProperty(default=False)
    no_testing = db.BooleanProperty(default=False)
    js_serials = db.BooleanProperty(default=False)
    img_serials = db.BooleanProperty(default=False)
    urgent = db.BooleanProperty(default=False)
    tests_pass = db.BooleanProperty(default=False)

    push = db.ReferenceProperty(Push, collection_name='requests')

    @property
    def uri(self):
        return urls.request(self)

    @property
    def api_uri(self):
        return urls.api_request(self)

    @property
    def json(self):
        return {'key': unicode(self.key()),
                'owner': self.owner.email(),
                'subject': self.subject,
                'branch': self.branch,
                'message': self.message,
                'state': self.state,
                'reject_reason': self.reject_reason,
                'target_date': self.target_date.strftime("%D")}

