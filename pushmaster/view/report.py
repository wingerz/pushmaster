import datetime, httplib, logging

from google.appengine.api import users

from pushmaster import config, model, timezone, urls
from pushmaster.view import common, RequestHandler
from pushmaster.taglib import T

def report_date_range(datestr):
    from_date = datetime.datetime.strptime(datestr, '%Y%m%d').replace(tzinfo=config.timezone)
    to_date = from_date + datetime.timedelta(days=6)
    return (from_date, to_date)

def last_monday_datetime(from_date=None):
    from_date = from_date or datetime.date.today()
    return from_date - datetime.timedelta(days=from_date.weekday())

class Reports(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: reports')

        doc.body(T.h1('Reports'))

        last_monday = last_monday_datetime()
        report_dates = [last_monday - datetime.timedelta(days=(7 * n)) for n in xrange(0, 10)]

        ol = T.ol(class_='reports')
        for date in report_dates:
            ol(T.li(T.a(href=urls.report(date))(
                        date.strftime('%e %b %Y'),
                        T.span(' - '),
                        (date + datetime.timedelta(days=6)).strftime('%e %b %Y'),
                        )))
        doc.body(ol, common.jquery_js, common.jquery_ui_js, common.pushmaster_js)

        doc.serialize(self.response.out)

class ViewReport(RequestHandler):
    def get(self, datestr):
        from_date, to_date = report_date_range(datestr)

        doc = common.Document(title='pushmaster: reports')
        doc.body(T.h1('Report for ', from_date.strftime('%e %b %Y'), ' - ', to_date.strftime('%e %b %Y')))

        pushes = model.Push.for_week_of(from_date)
        for push in pushes:
            pushdiv = T.div(class_='push')
            pushdiv(T.h2(
                    T.a(href=push.uri)(
                        push.ltime.replace(tzinfo=timezone.UTC()).astimezone(config.timezone).strftime('%a, %l:%M %p, %e %b %Y'),
                        T.span(' '),
                        push.name or '',
                        ), 
                    T.span(' by '),
                    common.display_user_email(push.owner),
                    ))
            reqlist = T.ol(class_='requests')
            for request in push.requests:
                reqlist(common.request_item(request))
            pushdiv(reqlist)
            doc.body(pushdiv)

        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)

        doc.serialize(self.response.out)

class LastWeek(RequestHandler):
    def get(self, datestr=None):
        if datestr:
            from_date, to_date = report_date_range(datestr)
        else:
            for_date = last_monday_datetime() - datetime.timedelta(days=7)
            return self.redirect('/lastweek/' + for_date.strftime('%Y%m%d'))
        
        pushes = model.Push.for_week_of(from_date)        
        requests = []
        for push in pushes:
            requests.extend(push.requests)
        requests = sorted(requests, key=lambda r: r.mtime)

        doc = common.Document(title='pushmaster: weekly report: ' + datestr)

        teams_list = T.ul(class_='teams')
        doc(teams_list)

        for team in config.report_users:
            team_item = T.li(class_='team')(T.h3(team['name']))
            teams_list(team_item)

            devs_list = T.ul(class_='devs')
            team_item(devs_list)
            for dev in team['dev']:
                dev_item = T.li(class_='dev')(T.h4(dev))
                devs_list(dev_item)
                dev_requests = filter(lambda r: r.owner.nickname() == dev, requests)
                if dev_requests:
                    requests_list = T.ol(class_='requests')(map(common.request_item, dev_requests))
                    dev_item(requests_list)

            if 'prod' in team:
                
                team_item(T.h4('PM: ' if len(team['prod']) == 1 else 'PMs: ', ', '.join(team['prod']), class_='pm'))
        
        doc.serialize(self.response.out)
