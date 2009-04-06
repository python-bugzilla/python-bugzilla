#!/usr/bin/python

import os.path
import urlparse

def url_to_query(url):
    '''Given a big huge bugzilla query URL, returns a query dict that can
    be passed along to the Bugzilla.query() method.'''
    q = dict()
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    if os.path.basename(path) in ('buglist.cgi','query.cgi'):
        q = dict(urlparse.parse_qsl(query))
    return q
