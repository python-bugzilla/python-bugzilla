#!/usr/bin/python

import os
import urlparse

def url_to_query(url):
    '''Given a big huge bugzilla query URL, returns a query dict that can
    be passed along to the Bugzilla.query() method.'''
    q = dict()
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    if os.path.basename(path) in ('buglist.cgi','query.cgi'):
        for (k,v) in urlparse.parse_qsl(query):
            if k not in q:
                q[k] = v
            elif isinstance(q[k], list):
                q[k].append(v)
            else:
                oldv = q[k]
                q[k] = [oldv, v]
    return q

def open_without_clobber(name, *args):
    '''Try to open the given file with the given mode; if that filename exists,
    try "name.1", "name.2", etc. until we find an unused filename.'''
    fd = None
    count = 1
    orig_name = name
    while fd is None:
        try:
            fd = os.open(name, os.O_CREAT|os.O_EXCL, 0666)
        except OSError as e:
            if e.errno == os.errno.EEXIST:
                name = "%s.%i" % (orig_name, count)
                count += 1
            else: # raise IOError like regular open()
                raise IOError, (e.errno, e.strerror, e.filename)
    fobj = open(name, *args)
    if fd != fobj.fileno():
        os.close(fd)
    return fobj
