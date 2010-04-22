import cgi

__author__ = 'Jeremy Latt <jlatt@yelp.com>'
__all__ = ('T', 'Literal', 'Text', 'XHTML')

def iterflat(args):
    for arg in args:
        if hasattr(arg, '__iter__'):
            for a in iterflat(arg):
                yield a
        else:
            yield arg

def translate(attrs):
    for key, value in attrs.iteritems():
        if key.endswith('_'):
            key = key[:-1]

        yield (key, value)

def iterattrs(attrs):
    for key, value in attrs.iteritems():
        if isinstance(value, bool):
            if value:
                value = key
            else: # skip False
                continue
        else:
            value = unicode(value)

        yield (key, value)

def write_attribute(f, aname, avalue):
    f.write(' ')
    f.write(cgi.escape(aname))
    f.write('=')
    f.write('"')
    f.write(cgi.escape(avalue, quote=True))
    f.write('"')

class StrSerializable(object):
    def __str__(self):
        from StringIO import StringIO
        return self.serialize(StringIO()).getvalue()
    
    __repr__ = __str__

    def serialize(self, f):
        raise NotImplemented

class _Tag(StrSerializable):
    empty = set(('link', 'input', 'hr', 'meta'))

    def __init__(self, tagname, *children, **attrs):
        assert tagname == cgi.escape(tagname), 'illegal tag name %s' % tagname

        self.tagname = tagname
        self.children = list(iterflat(children))
        self.attrs = dict(translate(attrs))

    def __call__(self, *children, **attrs):
        self.children.extend(iterflat(children))
        self.attrs.update(translate(attrs))
        return self

    def serialize(self, f):
        # open tag
        f.write('<')
        f.write(self.tagname)

        # attributes
        for key, value in iterattrs(self.attrs):
            write_attribute(f, key, value)

        if self.tagname in self.empty:
            assert not self.children, 'empty tag %s has children' % self.tagname
            f.write('/>')
        else:
            f.write('>')
        
            for child in self.children:
                if hasattr(child, 'serialize'):
                    child.serialize(f)
                else:
                    f.write(cgi.escape(unicode(child)))

            f.write('</')
            f.write(self.tagname)
            f.write('>')

        return f

class Literal(StrSerializable):
    def __init__(self, html):
        self.html = html

    def serialize(self, f):
        f.write(self.html)
        return f

class Text(StrSerializable):
    def __init__(self, text):
        self.text = text

    def serialize(self, f):
        f.write(cgi.escape(self.text))
        return f


XML_PREAMBLE = '<?xml version="1.0" encoding="UTF-8"?>'
XML_NS = 'http://www.w3.org/1999/xhtml'
XHTML_STRICT_DOCTYPE = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'

class XHTML(StrSerializable):
    def __init__(self):
        self.html = T.html(xmlns=XML_NS)

    def serialize(self, f):
        f.write(XML_PREAMBLE)
        self.html.serialize(f)
        return f

    def __call__(self, *args, **kw):
        self.html(*args, **kw)
        return self

class TagFactory(object):
    """Tag wrapper that lets you use normal Tag syntax (i.e. T('head')(...)) as
    well as "manifested" syntax like T.head(...).
    """

    tag_cls = _Tag

    def __getattr__(self, name):
        return self.tag_cls(name)

    def __call__(self, *args, **kwargs):
        return self.tag_cls(*args, **kwargs)

T = TagFactory()
