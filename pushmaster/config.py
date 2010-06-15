import timezone
import util

is_dev = util.is_dev()
is_prod = not is_dev
debug = is_dev

timezone = timezone.Pacific
jquery = 'https://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'
jquery_ui = 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.0/jquery-ui.min.js'
reset_css = 'https://developer.yahoo.com/yui/build/reset/reset.css'
favicon = 'https://images.yelp.com/favicon.ico'
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
    ('Consumer', (
            'abhinav',
            'alan',
            'ayust',
            'edmund',
            'hannah',
            'jeffmicklos',
            'jlatt',
            'jon',
            'rohan',
            'wing',
            ), (
            'benb',
            'vivek',
            )),
    ('Ads', (
            'julian',
            'mtai',
            ), (
            'bryan',
            )),
    ('Biz', (
            'adamb',
            'anthony',
            'lenza',
            'minh',
            'ostrowski',
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
            'zeke',
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
            'pretz',
            ), (
            'eric',
            )),
    ('Infra', (
            'bigo',
            'dchen',
            'eskil',
            'evan',
            'jbrown',
            'mtytel',
            'rhett',
            ), tuple()),
    )

def gen_report_user_to_team():
    for team, devs, pms in report_users:
        for dev in devs:
            yield (dev, team)
report_user_to_team = dict(gen_report_user_to_team())
