import timezone
import util

is_dev = util.is_dev()
is_prod = not is_dev
debug = is_dev

timezone = timezone.Pacific
jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js'
jquery_ui = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js'
favicon = 'http://static.px.yelp.com/favicon.ico'
mail_to = 'push@yelp.com'
hostname = 'yelp-pushmaster.appspot.com'
protocol = 'http'
push_plans_url = 'https://trac.yelpcorp.com/wiki/YelpPushPlans'
static_serial = '2010-02-22'

def url(path):
    return '%s://%s%s' % (protocol, hostname, path)

