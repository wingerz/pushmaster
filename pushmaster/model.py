from google.appengine.ext import db

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
        return cls.all().filter('state in', ('accepting', 'onstage')).order('-ctime').get()

    @classmethod
    def open(cls, limit=20):
        return cls.all().filter('state in', ('accepting', 'onstage', 'live')).order('-ctime').fetch(limit)

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

    @property
    def uri(self):
        return '/request/' + str(self.key())

    @classmethod
    def current(cls):
        return cls.gql('WHERE state = :state ORDER BY ctime ASC', state='requested').fetch(100)
