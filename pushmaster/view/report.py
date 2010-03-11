import datetime
import httplib
import logging

from google.appengine.api import users

from pushmaster import config
from pushmaster import model
from pushmaster import timezone
from pushmaster.view import common
from pushmaster.view import RequestHandler
from pushmaster.taglib import T, XHTML

class Reports(RequestHandler):
    def get(self):
        doc = common.Document(title='pushmaster: reports')

        doc.body(
            common.session(),
            common.navbar(),
            T.h1('Reports'),
            )

        today = datetime.date.today()
        last_monday = today - datetime.timedelta(days=today.weekday())
        report_dates = [last_monday - datetime.timedelta(days=(7 * n)) for n in xrange(0, 10)]

        ol = T.ol(class_='reports')
        for date in report_dates:
            ol(T.li(T.a(href=('/report/' + date.strftime('%Y%m%d')))(
                        date.strftime('%e %b %Y'),
                        T.span(' - '),
                        (date + datetime.timedelta(days=6)).strftime('%e %b %Y'),
                        )))

        doc.body(
            ol,
            common.script(config.jquery, external=True),
            common.script(config.jquery_ui, external=True),
            common.script('/js/pushmaster.js'),
            )

        doc.serialize(self.response.out)

class ViewReport(RequestHandler):
    def get(self, datestr):
        from_date = datetime.datetime.strptime(datestr, '%Y%m%d').replace(tzinfo=config.timezone)
        to_date = from_date + datetime.timedelta(days=6)

        doc = common.Document(title='pushmaster: reports')

        doc.body(
            common.session(),
            common.navbar(),
            T.h1('Report for ', from_date.strftime('%e %b %Y'), ' - ', to_date.strftime('%e %b %Y')),
            )

        pushes = model.Push.for_week_of(from_date)
        for push in pushes:
            pushdiv = T.div(class_='push')
            pushdiv(T.h2(
                    T.a(href=push.uri)(push.ltime.replace(tzinfo=timezone.UTC()).astimezone(config.timezone).strftime('%a, %l:%M %p, %e %b %Y')), 
                    T.span(' '),
                    common.display_user_email(push.owner),
                    ))
            reqlist = T.ol(class_='requests')
            for request in push.requests:
                reqlist(common.request_item(request))
            pushdiv(reqlist)
            doc.body(pushdiv)

        doc.body(common.jquery_js, common.jquery_ui_js, common.pushmaster_js)
        doc.serialize(self.response.out)
