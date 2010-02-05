from pushmaster import config
from pushmaster.taglib import T

XHTML_STRICT_DOCTYPE = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
HTML_OPEN = '<html xmlns="http://www.w3.org/1999/xhtml">'
HTML_CLOSE = '</html>'

def write(out, head, body):
    out.write(XHTML_STRICT_DOCTYPE)
    out.write(HTML_OPEN)
    head.serialize(out)
    body.serialize(out)
    out.write(HTML_CLOSE)

def stylesheet(href, external=False):
    if not external:
        href = '/%s%s' % (config.static_serial, href)
    return T('link', rel='stylesheet', href=href)

def script(src, external=False):
    if not external:
        src = '/%s%s' % (config.static_serial, src)
    return T.script(type='text/javascript', src=src)

def head(title='', stylesheets=[], scripts=[]):
    return T.head(
        T.title(title),
        T.link(rel='shortcut icon', type='image/x-icon', href=config.favicon),
        stylesheet('http://developer.yahoo.com/yui/build/reset/reset.css', external=True),
        stylesheet('/css/ui-lightness/jquery-ui-1.7.2.custom.css'),
        stylesheet('/css/pushmaster.css'),
        map(stylesheet, stylesheets),
        map(script, scripts))
