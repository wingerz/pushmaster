import cgi
from functools import partial

__author__ = 'Jeremy Latt <jeremy@jeremylatt.com>'

def iterflat(args):
    for arg in args:
        if hasattr(arg, '__iter__'):
            for a in iterflat(arg):
                yield a
        else:
            yield arg

def translate(attrs):
    newattrs = {}
    for key, value in attrs.items():
        if key.endswith('_'):
            key = key[:-1]
        newattrs[key] = value
    return newattrs

class _Tag(object):
    empty = ('link', 'input', 'hr', 'meta')

    def __init__(self, tagname, **attrs):
        self.tagname = tagname
        self.attrs = translate(attrs)
        self.text = ''
        self.tail = ''
        self.children = []

    def __call__(self, *args, **kwargs):
        if kwargs:
            self.attrs.update(translate(kwargs))
        for arg in iterflat(args):
            if isinstance(arg, basestring):
                if self.children:
                    self.children[-1].tail += arg
                else:
                    self.text += arg
            else:
                self.children.append(arg)
        return self

    def __str__(self):
        from StringIO import StringIO
        return self.serialize(StringIO()).getvalue()

    def write_attribute(self, f, aname, avalue):
        f.write(' ')
        f.write(aname)
        f.write('=')
        f.write('"')
        f.write(cgi.escape(avalue, quote=True))
        f.write('"')

    def serialize(self, f):
        # open tag
        f.write('<')
        f.write(self.tagname)

        # attributes
        for aname, avalue in self.attrs.items():
            if isinstance(avalue, bool):
                if avalue:
                    self.write_attribute(f, aname, aname)
            else:
                self.write_attribute(f, aname, avalue)

        if self.tagname in self.empty:
            f.write('/>')
        else:
            f.write('>')
        
            if self.text:
                f.write(cgi.escape(self.text))
            
            for child in self.children:
                child.serialize(f)

            f.write('</')
            f.write(self.tagname)
            f.write('>')

        f.write(cgi.escape(self.tail))

        return f

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

class Literal(object):
    def __init__(self, html):
        self.html = html

    def serialize(self, f):
        f.write(self.html)
