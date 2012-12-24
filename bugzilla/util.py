#!/usr/bin/python

import os
import urlparse


def url_to_query(url):
    '''Given a big huge bugzilla query URL, returns a query dict that can
    be passed along to the Bugzilla.query() method.'''
    q = {}
    (ignore, ignore, path,
     ignore, query, ignore) = urlparse.urlparse(url)

    if os.path.basename(path) in ('buglist.cgi', 'query.cgi'):
        for (k, v) in urlparse.parse_qsl(query):
            if k not in q:
                q[k] = v
            elif isinstance(q[k], list):
                q[k].append(v)
            else:
                oldv = q[k]
                q[k] = [oldv, v]
    return q
