from taglib import Tag as T

XHTML_STRICT_DOCTYPE = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
HTML_OPEN = '<html xmlns="http://www.w3.org/1999/xhtml">'
HTML_CLOSE = '</html>'

def write(out, head, body):
    out.write(XHTML_STRICT_DOCTYPE)
    out.write(HTML_OPEN)
    head.serialize(out)
    body.serialize(out)
    out.write(HTML_CLOSE)

def stylesheet(href):
    return T('link', rel='stylesheet', href=href)

def head(title='', css=[], scripts=[]):
    stylesheets = [stylesheet(href) for href in css]
    scripts = [T('script', type='text/javascript', src=src) for src in scripts]
    return T('head')(
        T('title')(title),
        T('link', rel='shortcut icon', type='image/x-icon', href='http://static.px.yelp.com/favicon.ico'),
        stylesheet('/css/reset.css'),
        stylesheet('/css/pushmaster.css'),
        stylesheets, 
        scripts)
