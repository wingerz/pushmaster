__author__ = 'jlatt@yelp.com'

def report(d):
    return '/report/%d%02d%02d' % (d.year, d.month, d.day)

def push(p):
    return '/push/' + str(p.key())

def request(r):
    return '/request/' + str(r.key())

def user_home(u):
    return '/user/' + u.email()

pushes = '/pushes'

requests = '/requests'

reports = '/reports'
