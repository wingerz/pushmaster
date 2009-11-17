from pushmaster.timezone import Pacific

timezone = Pacific

mail_to = 'push@yelp.com'

hostname = 'yelp-pushmaster.appspot.com'

protocol = 'http'

def url(path):
    return '%s://%s%s' % (protocol, hostname, path)
