from pushmaster.timezone import Pacific

timezone = Pacific
jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js'
favicon = 'http://static.px.yelp.com/favicon.ico'
mail_to = 'push@yelp.com'
hostname = 'yelp-pushmaster.appspot.com'
protocol = 'http'
push_plans_url = 'https://trac.yelpcorp.com/wiki/YelpPushPlans'
static_serial = '20100120a'

def url(path):
    return '%s://%s%s' % (protocol, hostname, path)

