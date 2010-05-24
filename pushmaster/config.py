import timezone
import util

is_dev = util.is_dev()
is_prod = not is_dev
debug = is_dev

timezone = timezone.Pacific
jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'
jquery_ui = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.0/jquery-ui.min.js'
reset_css = 'http://developer.yahoo.com/yui/build/reset/reset.css'
favicon = 'http://static.px.yelp.com/favicon.ico'
mail_to = 'push+pushmaster@yelp.com'
hostname = 'yelp-pushmaster.appspot.com' if is_prod else 'localhost:8080'
protocol = 'http'
push_plans_url = 'https://trac.yelpcorp.com/wiki/YelpPushPlans'
static_host_count = 4

def url(path):
    return '%s://%s%s' % (protocol, hostname, path)

def static_host(path):
    return '%d.%s' % (hash(path) % static_host_count, hostname)

report_users = (
    ('Consumer/I18n', (
            'abhinav',
            'alan',
            'edmund',
            'hannah',
            'jlatt',
            'jon',
            'rohan',
            'wing',
            ), (
            'benb',
            'vivek',
            )),
    ('Ads', (
            'juliank',
            'mtai',
            ), (
            'bryan',
            )),
    ('Biz', (
            'adamb',
            'anthony',
            'lenza',
            'minh',
            ), (
            'kyle',
            'mallen',
            )),
    ('Internal Apps', (
            'derwiki',
            'duncan',
            'kmitton',
            ), (
            'bryan',
            )),
    ('Search', (
            'aditya',
            'daniel',
            'jfennell',
            'shivaram',
            'smg',
            'timr',
            ), (
            'eric',
            )),
    ('Spam', (
            'dave',
            'pwais',
            ), (
            'jeremy',
            )),
    ('Mobile', (
            'alexd',
            'gabe',
            'garrick',
            'greg',
            'johnb',
            'mattj',
            'newhouseb',
            'pretz',
            ), (
            'eric',
            )),
    )

def gen_report_user_to_team():
    for team, devs, pms in report_users:
        for dev in devs:
            yield (dev, team)
report_user_to_team = dict(gen_report_user_to_team())
