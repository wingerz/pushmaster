import os
import timezone
import util

import yaml

is_dev = util.is_dev()
is_prod = not is_dev
debug = is_dev

timezone = timezone.Pacific
jquery = '//ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'
jquery_ui = '//ajax.googleapis.com/ajax/libs/jqueryui/1.8.0/jquery-ui.min.js'
reset_css = '//developer.yahoo.com/yui/build/reset/reset.css'
favicon = '//images.yelp.com/favicon.ico'
mail_sender = 'app@yelp-pushmaster.appspotmail.com'
mail_to = 'push+pushmaster@yelp.com'
hostname = 'yelp-pushmaster.appspot.com' if is_prod else 'localhost:8080'
protocol = 'http'
push_plans_url = 'https://trac.yelpcorp.com/wiki/YelpPushPlans'
static_host_count = 4

def url(path):
    return '%s://%s%s' % (protocol, hostname, path)

def static_host(path):
    return '%d.%s' % (hash(path) % static_host_count, hostname)

report_users = yaml.load(file(os.path.join(os.path.dirname(__file__), '..', 'report_users.yaml')))['report_users']

def gen_report_user_to_team():
    for team in report_users:
        for dev in team['dev']:
            yield (dev, team['name'])
report_user_to_team = dict(gen_report_user_to_team())

nothing_messages = (
    'Zip.',
    'Zero.',
    'Zilch.',
    'Nada.',
    'Bupkiss.',
    'Nothing to see here, move along.',
    'Nope.',
    'Void.',
    'None.',
    'Naught.',
    'This area left intentionally blank.',
    'Diddly.',
    'Nix.',
    'Nothing.',
    'Zippo.',
    'Zot.',
    'Null.',
    'Nil.',
    'Crickets.',
    'Empty.',
    'Tumbleweeds.',
    'A cricket riding a tumbleweed.',
    'The sound of one hand clapping.',
    'Guru Meditation #00000004 0000AAC0',
    )
