#!/usr/bin/python
# Simple self-test of the bugzilla module

# Copyright (C) 2007 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from bugzilla import Bugzilla
import os, glob, sys

def find_firefox_cookiefile():
    cookieglob = os.path.expanduser('~/.mozilla/firefox/default.*/cookies.txt')
    cookiefiles = glob.glob(cookieglob)
    if cookiefiles:
        # TODO return whichever is newest
        return cookiefiles[0]

def selftest(user='',password=''):
    url = 'https://bugzilla.redhat.com/xmlrpc.cgi'
    public_bug = 1
    private_bug = 250666
    query = {'product':'Fedora',
             'component':'kernel',
             'version':'devel',
             'long_desc':'wireless'}
    
    print "Woo, welcome to the bugzilla.py self-test."
    print "Using bugzilla at " + url
    if user and password:
        print 'Using username "%s", password "%s"' % (user,password)
        b = Bugzilla(url=url,user=user,password=password)
    else:
        cookies = find_firefox_cookiefile()
        if not cookies:
            print "Could not find any cookies for that URL!"
            print "Log in with firefox or give me a username/password."
            sys.exit(1)
        print "Reading cookies from " + cookies
        b = Bugzilla(url=url,cookies=cookies)
    print "Reading product list"
    print b.getproducts()
    print

    print "Reading public bug (#%i)" % public_bug
    print b.getbug(public_bug)
    print

    print "Reading private bug (#%i)" % private_bug
    try:
        print b.getbug(private_bug)
    except xmlrpclib.Fault, e:
        if 'NotPermitted' in e.faultString:
            print "Failed: Not authorized."
        else:
            print "Failed: Unknown XMLRPC error: %s"  % e
    q_msg = "%s %s %s %s" % (query['product'],query['component'],
                             query['version'],query['long_desc'])
    print

    print "Querying %s bugs" % q_msg
    bugs = b.query(query)
    print "%s bugs found." % len(bugs)
    for bug in bugs:
        print "Bug %s" % bug
    print

    print "Awesome. We're done."

if __name__ == '__main__':
    user = ''
    password = ''
    if len(sys.argv) > 2:
        (user,password) = sys.argv[1:3]
    selftest(user,password)
